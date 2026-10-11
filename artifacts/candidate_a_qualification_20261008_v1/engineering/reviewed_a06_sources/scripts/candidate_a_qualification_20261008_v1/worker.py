"""Reviewed-card-only SUMO technical worker; no launch at import."""
import argparse
from dataclasses import asdict
import csv
import json
import math
import os
from pathlib import Path
import socket
import subprocess
import sys
import time

ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT));sys.path.insert(0,str(ROOT/'scripts/formal_development_20261007_v1'))
from src.candidate_a_qualification_20261008.actor import CycleLedger,PhaseEnvelope,motion_phase,crossing_records
from src.candidate_a_qualification_20261008.safety import Vehicle,red_transition_witness,assert_ingress_and_crossing_coverage
from control import Feedback,FeedbackParameters
from v15_worker import DetectorEventLedger,connect_traci,secure_gap_query,VehicleState,LeaderState
sys.path.insert(0,str(Path(__file__).parent))
from runner import BASE,SUMO,FEEDBACK,NETWORK,RESOURCES,sha,write,validate_card

TLS='ramp_mid';STORAGE='ramp_storage_0';INGRESS=':urban_diverge_1_0';INTERNAL=':ramp_mid_0_0'
DETECTORS=('p1_main_down_20_l0','p1_main_down_20_l1')

def clean(value):
    if isinstance(value,float) and not math.isfinite(value):return None
    if isinstance(value,dict):return {k:clean(v) for k,v in value.items()}
    if isinstance(value,(list,tuple)):return [clean(v) for v in value]
    return value

def encoded(value):return json.dumps(clean(value),separators=(',',':'),allow_nan=False)

def observe(conn):
    vehicles=[];dynamics={};ids={}
    for lane,pop in ((STORAGE,'storage'),(INGRESS,'ingress')):
        ids[lane]=tuple(conn.lane.getLastStepVehicleIDs(lane))
        for vid in ids[lane]:
            typ=conn.vehicle.getTypeID(vid)
            if typ not in dynamics:
                dynamics[typ]=dict(accel=conn.vehicletype.getAccel(typ),decel=conn.vehicletype.getDecel(typ),tau=conn.vehicletype.getTau(typ),action=conn.vehicletype.getActionStepLength(typ),sigma=conn.vehicletype.getImperfection(typ),maxSpeed=conn.vehicletype.getMaxSpeed(typ))
            d=dynamics[typ]
            if (d['sigma']!=.5 or abs(d['accel']-2.6)>1e-8 or abs(d['decel']-4.5)>1e-8 or abs(d['maxSpeed']-55.55555555555556)>1e-8):raise ValueError('protected vehicle dynamics changed')
            v=Vehicle(vid,pop,conn.vehicle.getLanePosition(vid)-(113.08 if pop=='ingress' else 0),conn.vehicle.getSpeed(vid),conn.vehicle.getLength(vid),conn.vehicle.getMinGap(vid),d['accel'],d['decel'],d['tau'],d['action'],typ)
            v.validate()
            if v.speed_m_s>d['maxSpeed']+1e-8:raise ValueError('actual vehicle exceeds coverage maximum')
            if conn.vehicle.getSpeedMode(vid)!=31:raise ValueError('native speed/signal safety mode changed')
            if conn.vehicle.getLaneChangeMode(vid)!=1621:raise ValueError('native lane-change safety mode changed')
            vehicles.append(v)
    internal={vid:dict(position_m=conn.vehicle.getLanePosition(vid),length_m=conn.vehicle.getLength(vid),speed_m_s=conn.vehicle.getSpeed(vid)) for vid in conn.lane.getLastStepVehicleIDs(INTERNAL)}
    for vid,state in internal.items():
        if (not vid.startswith('R_') or conn.vehicle.getTypeID(vid)!='technical_passenger' or
                not all(math.isfinite(x) for x in state.values()) or
                not 0<=state['position_m']<=81.98 or state['length_m']<=0 or state['speed_m_s']<0):
            raise ValueError('unknown internal receiver state')
    front=max((v for v in vehicles if v.population=='storage'),key=lambda v:v.position_m,default=None)
    receiver=dict(available=True,reason='NO_FRONT',front_id='',nearest_internal=None,leader=None)
    if front:
        receiver['front_id']=front.vehicle_id
        route=tuple(conn.vehicle.getRoute(front.vehicle_id));idx=conn.vehicle.getRouteIndex(front.vehicle_id)
        if route[idx:idx+3]!=('ramp_storage','ramp_accel','merge_section'):raise ValueError('checked receiver route changed')
        nearest=min(internal,key=lambda k:internal[k]['position_m']-internal[k]['length_m']) if internal else None
        clearance=internal[nearest]['position_m']-internal[nearest]['length_m'] if nearest else None
        receiver.update(nearest_internal=nearest,nearest_internal_rear_clearance_m=clearance,required_front_clearance_m=front.length_m+front.min_gap_m)
        if nearest and clearance<front.length_m+front.min_gap_m:receiver.update(available=False,reason='INTERNAL_RECEIVER_CLEARANCE')
        raw=conn.vehicle.getLeader(front.vehicle_id,478.67)
        if raw:
            leader_id,gap=raw;typ=conn.vehicle.getTypeID(leader_id);lane=conn.vehicle.getLaneID(leader_id)
            if lane not in (INTERNAL,'ramp_accel_0',':freeway_merge_2_0','merge_section_0','merge_section_1','merge_section_2'):raise ValueError('leader off checked receiving path')
            lead=LeaderState(leader_id,lane,gap,conn.vehicle.getSpeed(leader_id),conn.vehicletype.getEmergencyDecel(typ))
            state=VehicleState(front.position_m,front.speed_m_s,front.length_m,front.min_gap_m,front.accel_m_s2,front.normal_decel_m_s2)
            secure=conn.vehicle.getSecureGap(**secure_gap_query(front.vehicle_id,state,lead))
            if not math.isfinite(secure) or secure<0:raise ValueError('unknown secure receiving gap')
            receiver['leader']=dict(vehicle_id=leader_id,lane_id=lane,gap_excluding_minGap_m=gap,secure_gap_m=secure)
            if gap+1e-9<secure+1.1:receiver.update(available=False,reason='LEADER_SECURE_GAP')
        if receiver['available']:receiver['reason']='AVAILABLE'
    return vehicles,ids,internal,receiver

def sumo_launch_environment():
    """Reuse the protected runner's installed-schema SUMO_HOME override."""
    home=SUMO.parent.parent/'share/sumo'
    for name in ('routes_file.xsd','additional_file.xsd','sumoConfiguration.xsd'):
        if not (home/'data/xsd'/name).is_file():raise FileNotFoundError('missing installed SUMO schema: '+name)
    return dict(os.environ,SUMO_HOME=str(home))

def startup_trace_callback(path):
    """Adapt the inherited connect_traci callable interface to immutable JSONL."""
    path=Path(path)
    with path.open('x'):pass
    def trace(event):
        with path.open('a') as f:f.write(encoded(event)+'\n')
    return trace

def request_phase(tls,requests,time_s,method,value):
    """Record every attempted native phase API call, including API failure."""
    if method not in ('setProgram','setPhase'):
        raise ValueError('unsupported phase request')
    record=dict(time_s=time_s,method=method,value=value,call_completed=False)
    requests.append(record)
    getattr(tls,method)(TLS,value)
    record['call_completed']=True

def accounting_coverage(last_completed_s,last_accounted_s):
    """A closed algebraic prefix cannot qualify an unaccounted advanced step."""
    complete=last_completed_s==last_accounted_s
    return dict(last_accounted_s=last_accounted_s,accounting_complete=complete,
                accounting_status='RECONCILED_COMPLETED_PREFIX' if complete else 'UNRECONCILED_UNSUPPORTED',
                unaccounted_completed_interval_s=None if complete else [last_accounted_s,last_completed_s],
                qualification_accounting_supported=complete)

def run(card_path):
    card=json.loads(Path(card_path).read_text());validate_card(card)
    out=Path(card['output']);reservation=BASE/'engineering/reservations'/f"{card['run_id']}.json"
    if not reservation.is_file() or not out.is_dir() or not (BASE/'engineering/launch.lock').is_file() or json.loads(reservation.read_text())['card_sha256']!=sha(card_path):raise ValueError('missing one-use guardian reservation')
    import traci
    conn=None;proc=None;files=[];started=False;status='ABORTED_TECHNICAL';failure='';snapshot={};last_time=0;last_completed_s=0;last_accounted_s=0
    envelope=PhaseEnvelope();ledger=CycleLedger(card['activation_s'],envelope);events=DetectorEventLedger();feedback=Feedback(FeedbackParameters(**FEEDBACK))
    phase_requests=[];snapshot['phase_api_requests']=phase_requests
    prefixN=0;prefix_by_segment={'PRECONTROL':0,'EXTERNAL_HOLD':0};cycles_written=set();seen_before_control=set();previous_motion='G';latest_nominal_raw=900
    def csvfile(name,fields):
        f=(out/name).open('x',newline='');files.append(f);w=csv.DictWriter(f,fieldnames=fields);w.writeheader();return w
    fields=['time_begin_s','time_end_s','segment','r_ALINEA_veh_h','r_final_veh_h','nominal_raw_veh_h','pending_command_veh_h','pending_requested_s','applied_command_veh_h','command_applied_s','application_delay_s','cycle_id','cycle_begin_s','cycle_end_s','cycle_period_s','nominal_n','cycle_executed','cycle_denial_reason','C_delta','C_applied_delta','E_delta','N_delta','C_total','C_applied_total','E_total','N_total','phase_api_requests_json','program_before','phase_before','state_before','next_switch_before_s','predicted_motion_phase','predicted_motion_state','program_after','phase_after','state_after','next_switch_after_s','storage_supply','receiver_available','receiver_reason','vehicle_states_json','receiver_json','red_transition_json','crossing_ids_json','type_dynamics_json','minimum_actual_deceleration_m_s2']
    steps=csvfile('phase_steps.csv',fields)
    crosses=csvfile('crossings.csv',['vehicle_id','crossing_time_lower_s','crossing_time_upper_s','time_interval','cycle_id','motion_signal_state','state_before','state_after','segment'])
    cycles=csvfile('cycles.csv',['cycle_id','begin_s','end_s','period_s','nominal_n','applied_command_veh_h','command_requested_s','command_applied_s','application_delay_s','executed','denial_reason','completed','N_G','N_y','N_r','crossing_ids_json'])
    fw=csvfile('feedback_updates.csv',['time_s','application_s','occupancy_l0_pct','occupancy_l1_pct','rate_previous_veh_h','rate_raw_veh_h','rate_clipped_veh_h'])
    ew=csvfile('detector_vehicle_events.csv',['time_begin_s','time_end_s','detector_id','vehicle_id','vehicle_length_m','entry_time_s','leave_time_s','type_id'])
    try:
        with socket.socket() as s:s.bind(('127.0.0.1',0));port=s.getsockname()[1]
        with (out/'sumo_stdout.log').open('x') as so,(out/'sumo_stderr.log').open('x') as se:
            env=sumo_launch_environment()
            command=[str(SUMO),'-c',str(Path(card['package'])/'scenario.sumocfg'),'--remote-port',str(port)]
            write(out/'startup_context.json',dict(command=command,worker_cwd=os.getcwd(),sumo_home=env['SUMO_HOME'],environment_override_keys=['SUMO_HOME'],other_environment='inherited unchanged from guardian',schema_sha256={name:sha(Path(env['SUMO_HOME'])/'data/xsd'/name) for name in ('routes_file.xsd','additional_file.xsd','sumoConfiguration.xsd')}))
            proc=subprocess.Popen(command,stdout=so,stderr=se,env=env);started=True
            conn=connect_traci(traci,port,proc,startup_trace_callback(out/'startup_trace.jsonl'),deadline_s=RESOURCES['startup_limit_s'])
            if conn.trafficlight.getControlledLinks(TLS)!=((('ramp_storage_0','ramp_accel_0',INTERNAL),),):raise ValueError('controlled link changed')
            for lane,length in ((STORAGE,204.49),(INGRESS,113.08),(INTERNAL,81.98)):
                if abs(conn.lane.getLength(lane)-length)>1e-8:raise ValueError('compiled runtime safety geometry changed')
            request_phase(conn.trafficlight,phase_requests,0,'setProgram','A_OPEN');request_phase(conn.trafficlight,phase_requests,0,'setPhase',0)
            typ='technical_passenger';coverage=assert_ingress_and_crossing_coverage(conn.vehicletype.getMaxSpeed(typ),conn.vehicletype.getAccel(typ))
            write(out/'coverage.json',coverage)
            for t in range(4200):
                last_time=t
                if t:phase_requests=[]
                snapshot=dict(time_s=t,phase_api_requests=phase_requests)
                if abs(conn.simulation.getTime()-t)>1e-7:raise ValueError('TraCI step alignment changed')
                if t in range(630,4171,30):
                    measurement=events.finish_window(t);occ=[x[0] for x in measurement]
                    if card['mode']=='T1':
                        result=feedback.update(t,t-30,t,*occ);latest_nominal_raw=result['rate_raw_veh_h'];fw.writerow(dict(time_s=t,application_s=t,occupancy_l0_pct=occ[0],occupancy_l1_pct=occ[1],rate_previous_veh_h=result['rate_previous_veh_h'],rate_raw_veh_h=result['rate_raw_veh_h'],rate_clipped_veh_h=result['rate_clipped_veh_h']))
                vehicles,ids,internal,receiver=observe(conn)
                requested=feedback.rate if card['mode']=='T1' else card['fixed_command_veh_h']
                segment='PRECONTROL' if t<600 else 'EXTERNAL_HOLD' if t<card['activation_s'] else 'QUALIFICATION'
                if card['mode']=='FIXED' and t==600:
                    request_phase(conn.trafficlight,phase_requests,t,'setProgram','CA_C8');request_phase(conn.trafficlight,phase_requests,t,'setPhase',1)
                newcycle=False;cycle=None
                if t>=card['activation_s']:
                    newcycle,cycle=ledger.begin_step(t,requested)
                    if newcycle:
                        if conn.trafficlight.getRedYellowGreenState(TLS)!='r' and t!=600:raise ValueError('new cycle started outside safe red boundary')
                        execute=receiver['available']
                        ledger.mark_cycle_start(execute,'' if execute else receiver['reason'])
                        if execute:
                            request_phase(conn.trafficlight,phase_requests,t,'setProgram',f"CA_C{cycle['period_s']}");request_phase(conn.trafficlight,phase_requests,t,'setPhase',2);request_phase(conn.trafficlight,phase_requests,t,'setPhase',0)
                program=conn.trafficlight.getProgram(TLS);phase=conn.trafficlight.getPhase(TLS);state=conn.trafficlight.getRedYellowGreenState(TLS);nxt=conn.trafficlight.getNextSwitch(TLS)
                if t<600:motion_idx,motion=0,'G'
                else:
                    period=int(program.split('CA_C')[1])
                    motion_idx,motion=motion_phase(phase,state,nxt,t,envelope.phases(period))
                if cycle:
                    expected=envelope.state_at(t-cycle['begin_s'],cycle['period_s'],cycle['executed'])
                    if motion!=expected:raise ValueError('native phase is early/late versus planned program')
                redcheck=red_transition_witness(vehicles) if motion=='r' and previous_motion!='r' else {}
                snapshot=dict(time_s=t,phase_api_requests=phase_requests,segment=segment,program=program,phase_before=phase,state_before=state,next_switch=nxt,predicted_motion=motion,cycle=cycle,vehicle_states=[asdict(v) for v in vehicles],receiver=receiver,red_transition=redcheck)
                if redcheck and not redcheck['safe']:
                    status='ABORTED_SAFETY_BEFORE_RED';raise RuntimeError('STOP unsafe prospective native yellow-to-red transition')
                before={v.vehicle_id:v.speed_m_s for v in vehicles}
                conn.simulationStep(t+1)
                last_completed_s=t+1
                snapshot.update(step_advanced=True,last_completed_step_s=last_completed_s,poststep_observation_stage='TLS_STATE_PENDING')
                after_state=conn.trafficlight.getRedYellowGreenState(TLS)
                snapshot.update(state_after=after_state,poststep_observation_stage='INTERNAL_IDS_PENDING')
                afterids=conn.lane.getLastStepVehicleIDs(INTERNAL)
                snapshot.update(internal_ids_after=list(afterids),poststep_observation_stage='CROSSING_RECONCILIATION_PENDING')
                recs=crossing_records(set(ids[STORAGE]),set(internal),set(afterids),t,cycle['cycle_id'] if cycle else -1,motion)
                snapshot.update(actual_crossings=recs,poststep_observation_stage='LEDGER_COMMIT_PENDING')
                if any(r['vehicle_id'] in seen_before_control for r in recs):raise RuntimeError('STOP duplicate global crossing')
                seen_before_control.update(r['vehicle_id'] for r in recs)
                for r in recs:crosses.writerow({**r,'state_before':state,'state_after':after_state,'segment':segment})
                e_delta=ledger.end_step(t+1,[r['vehicle_id'] for r in recs],motion) if cycle else 0
                if not cycle:
                    prefixN+=len(recs);prefix_by_segment[segment]+=len(recs)
                last_accounted_s=t+1
                snapshot.update(poststep_observation_stage='LEDGER_COMMITTED',step_advanced=True,actual_crossings=recs,state_after=after_state,accounting_after=ledger.accounting())
                if after_state!=motion:raise RuntimeError('STOP observed motion-phase prediction mismatch')
                if conn.simulation.getCollidingVehiclesNumber() or conn.simulation.getStartingTeleportNumber() or conn.simulation.getEndingTeleportNumber():status='ABORTED_SAFETY';raise RuntimeError('STOP collision/teleport')
                if motion=='r' and recs:status='ABORTED_SAFETY';raise RuntimeError('STOP red stopline crossing')
                decelerations=[]
                alive=set(conn.vehicle.getIDList())
                for vid,v in before.items():
                    if vid in alive:decelerations.append(conn.vehicle.getSpeed(vid)-v)
                minimum=min(decelerations,default=0.0)
                if minimum<-4.5-1e-6:status='ABORTED_SAFETY';raise RuntimeError('STOP observed acceleration exceeds normal braking bound')
                if (out/'sumo_error.log').exists():
                    errors=(out/'sumo_error.log').read_text()
                    if any(s in errors.lower() for s in ('emergency braking','collision','teleport','emergency stop')):status='ABORTED_SAFETY';raise RuntimeError('STOP native warning')
                if 600<=t<4170:
                    ev=events.add_step(t+1,{d:conn.inductionloop.getVehicleData(d) for d in DETECTORS})
                    for det,records in ev.items():
                        for vid,length,entry,leave,ty in records:ew.writerow(dict(time_begin_s=t,time_end_s=t+1,detector_id=det,vehicle_id=vid,vehicle_length_m=length,entry_time_s=entry,leave_time_s=leave,type_id=ty))
                acc=ledger.accounting();row={k:'' for k in fields}
                row.update(time_begin_s=t,time_end_s=t+1,segment=segment,r_ALINEA_veh_h=feedback.rate if card['mode']=='T1' and t>=600 else '',r_final_veh_h=requested if cycle else '',nominal_raw_veh_h=latest_nominal_raw if card['mode']=='T1' and t>=600 else '',C_delta=requested/3600 if cycle else 0,C_applied_delta=float(ledger.applied_command)/3600 if cycle else 0,E_delta=e_delta,N_delta=len(recs),C_total=acc['C'],C_applied_total=acc['C_applied'],E_total=acc['E'],N_total=acc['N'],phase_api_requests_json=encoded(phase_requests),program_before=program,phase_before=phase,state_before=state,next_switch_before_s=nxt,predicted_motion_phase=motion_idx,predicted_motion_state=motion,program_after=conn.trafficlight.getProgram(TLS),phase_after=conn.trafficlight.getPhase(TLS),state_after=after_state,next_switch_after_s=conn.trafficlight.getNextSwitch(TLS),storage_supply=bool(ids[STORAGE]),receiver_available=receiver['available'],receiver_reason=receiver['reason'],vehicle_states_json=encoded([asdict(v) for v in vehicles]),receiver_json=encoded(receiver),red_transition_json=encoded(redcheck),crossing_ids_json=encoded([r['vehicle_id'] for r in recs]),type_dynamics_json=encoded({v.type_id:dict(tau_s=v.tau_s,action_step_s=v.action_step_s,normal_decel_m_s2=v.normal_decel_m_s2,accel_m_s2=v.accel_m_s2) for v in vehicles}),minimum_actual_deceleration_m_s2=minimum)
                if cycle:
                    row.update(pending_command_veh_h=float(ledger.pending_command),pending_requested_s=ledger.pending_requested_s,applied_command_veh_h=cycle['applied_command_veh_h'],command_applied_s=cycle['command_applied_s'],application_delay_s=cycle['application_delay_s'],cycle_id=cycle['cycle_id'],cycle_begin_s=cycle['begin_s'],cycle_end_s=cycle['end_s'],cycle_period_s=cycle['period_s'],nominal_n=2,cycle_executed=cycle['executed'],cycle_denial_reason=cycle['denial_reason'])
                    if t+1==cycle['end_s']:
                        cr={k:v for k,v in cycle.items() if k!='crossing_ids'};cr['crossing_ids_json']=encoded(cycle['crossing_ids']);cycles.writerow(cr);cycles_written.add(cycle['cycle_id'])
                steps.writerow(row);previous_motion=motion
            status='COMPLETED_NOT_YET_QUALIFIED'
    except Exception as e:
        failure=f'{type(e).__name__}: {e}'
        write(out/'failure_snapshot.json',clean(dict(status=status,error=failure,decision_time_s=last_time,last_completed_step_s=last_completed_s,snapshot=snapshot,accounting=ledger.accounting(),**accounting_coverage(last_completed_s,last_accounted_s))))
        print(failure,file=sys.stderr)
    finally:
        if ledger.cycle and ledger.cycle['cycle_id'] not in cycles_written:
            cr={k:v for k,v in ledger.cycle.items() if k!='crossing_ids'};cr['crossing_ids_json']=encoded(ledger.cycle['crossing_ids']);cycles.writerow(cr)
        for f in files:f.close()
        if conn:
            try:conn.close()
            except Exception:pass
        if proc:
            try:proc.wait(timeout=5)
            except subprocess.TimeoutExpired:proc.terminate();proc.wait(timeout=5)
        write(out/'worker_receipt.json',dict(run_id=card['run_id'],card_sha256=sha(card_path),status=status,error=failure,sumo_started=started,last_completed_step_s=last_completed_s,decision_time_s=last_time,prefix_total_crossings=prefixN,prefix_crossings_by_segment=prefix_by_segment,accounting=ledger.accounting(),cycle_count=len(ledger.rows),runtime_qualification='PENDING_INDEPENDENT_DATA_AND_SCIENCE' if last_completed_s==last_accounted_s else 'PROHIBITED_UNRECONCILED_ACCOUNTING',**accounting_coverage(last_completed_s,last_accounted_s)))
    return 0 if status.startswith('COMPLETED') else 1

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--card',required=True);a=p.parse_args();sys.exit(run(a.card))

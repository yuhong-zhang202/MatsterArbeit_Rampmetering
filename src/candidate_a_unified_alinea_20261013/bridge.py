"""Single-use native diagnostic bridge. No launch or connection at import.

Current task has no native release. execute() always checks canonical future
human authorization/release before output allocation or native import/spawn.
"""
from pathlib import Path
from dataclasses import asdict
import json
import os
import shutil
import socket
import sys
import time

from src.candidate_a_unified_alinea_20261013.adapter import StepAdapter, inventory, TLS, STORAGE, INGRESS, INTERNAL
from src.candidate_a_unified_alinea_20261013.profile import ROOT,TASK,NETWORK,SUMO,sha,write_new,validate_release,require
from src.candidate_a_native_smoke_20261011.bridge_logs import LogCapture
from src.candidate_a_native_smoke_20261011.bridge_resources import ResourceWatchdog
from src.candidate_a_unified_alinea_20261013.frame_cache import FrameCache
from src.candidate_a_unified_alinea_20261013.policy import MAX_GREEN, yellow_scope
from src.candidate_a_unified_alinea_20261013.producer import Producer
from src.candidate_a_unified_alinea_20261013 import budget


def protected_worker():
    sys.path.insert(0,str(ROOT/'scripts/candidate_a_qualification_20261008_v1'))
    import worker
    require(Path(worker.__file__).resolve()==ROOT/'scripts/candidate_a_qualification_20261008_v1/worker.py','wrong protected observer module')
    return worker


def encoded(value):
    if isinstance(value,set):return sorted(value)
    if isinstance(value,Path):return str(value)
    raise TypeError(type(value).__name__)


def append_new(path, value):
    with path.open('a') as f:
        f.write(json.dumps(value,default=encoded,allow_nan=False)+'\n');f.flush();os.fsync(f.fileno())


def admission(conn, time_s, observe, previous_program):
    """Before control requests, rather than after a green is already selected."""
    require(conn.simulation.getTime()==time_s,'admission source time')
    require(conn.trafficlight.getControlledLinks(TLS)==((('ramp_storage_0','ramp_accel_0',INTERNAL),),),'admission link drift')
    inventory(conn)
    vehicles,ids,internal,receiver=observe(conn)
    for lane,length in [(STORAGE,204.49),(INGRESS,113.08),(INTERNAL,81.98)]:
        require(abs(conn.lane.getLength(lane)-length)<=1e-8,'admission geometry drift')
    require(type(receiver.get('available')) is bool and receiver['available'],'receiver denies green')
    require(type(time_s) is int and 1200 <= time_s < 1272, 'admission outside declared horizon')
    program = previous_program
    require(conn.trafficlight.getProgram(TLS)==program and conn.trafficlight.getRedYellowGreenState(TLS)=='r' and conn.trafficlight.getPhase(TLS)==2,'not native cycle-red boundary')
    switch=conn.trafficlight.getNextSwitch(TLS)
    require(switch>=time_s if time_s==1200 else switch==time_s,'native cycle switch mismatch')
    # Reuse full adapter observation validation on a read-only red view before
    # any setters. A new adapter would otherwise expect G at activation1200.
    # Validate all current lane membership here; do not relax its post-selection checks.
    world,_,_=inventory(conn)
    require({v.vehicle_id for v in vehicles}==set(ids[STORAGE])|set(ids[INGRESS]),'admission local coverage')
    for v in vehicles:
        v.validate();require(v.vehicle_id in world and world[v.vehicle_id]['role']=='R' and abs(world[v.vehicle_id]['speed_m_s']-v.speed_m_s)<=1e-8,'admission vehicle binding')
    for lane,covered in [(STORAGE,set(ids[STORAGE])),(INGRESS,set(ids[INGRESS])),(INTERNAL,set(internal))]:
        require(covered==set(conn.lane.getLastStepVehicleIDs(lane))=={v for v,w in world.items() if w['lane_id']==lane},'admission lane binding')
    return {'time_s':time_s,'receiver':receiver,'vehicle_states':[asdict(v) for v in vehicles],'native_red_boundary':True}


def checkpoint(conn, adapter, capture, output, start_time):
    """First actual controlled-red ACK, durably captured; final EOF still required."""
    end = adapter.first_controlled_red_begin+1
    require(adapter.checkpoint_pending and not adapter.checkpoint_verified, 'checkpoint identity')
    require(conn.simulation.getTime()==end and adapter.last_completed==adapter.last_end==end and adapter.pending is None, 'checkpoint time/accounting unknown')
    row=adapter.receipts[-1]
    require(row['motion']=='r' and row['accounting_complete'], 'checkpoint first red unknown')
    require(conn.trafficlight.getProgram(TLS)==adapter.ledger.cycle['program'] and conn.trafficlight.getPhase(TLS)==2 and conn.trafficlight.getRedYellowGreenState(TLS)=='r' and conn.trafficlight.getNextSwitch(TLS)==adapter.ledger.cycle['end_s'], 'checkpoint signal clock unknown')
    require(conn.trafficlight.getControlledLinks(TLS)==((('ramp_storage_0','ramp_accel_0',INTERNAL),),),'checkpoint link mismatch')
    captured=capture.snapshot(end,end,'FIRST_RED_CHECKPOINT_PROVISIONAL_UNTIL_EOF')
    require(not captured['streams']['sumo_stderr.log']['text'],'checkpoint stderr message')
    append_new(output/'log_intervals.jsonl',captured)
    receipt={'time_s':end,'first_controlled_red_begin_s':adapter.first_controlled_red_begin,
        'status':'CHECKPOINT_PASSED_CONTINUE_SAME_AUTHORIZED_RUN',
        'accounting':adapter.ledger.accounting(),'log_capture':captured,
        'log_scope':'PROVISIONAL_NATIVE_CAPTURE_FINAL_EOF_REQUIRED',
        'elapsed_monitored_wall_s':time.monotonic()-start_time,
        'native_safety_proven':False,'rate_qualified':False}
    with (output/'first_red_checkpoint.json').open('x') as f:
        f.write(json.dumps(receipt,default=encoded,allow_nan=False)+'\n');f.flush();os.fsync(f.fileno())
    adapter.checkpoint_verified=True;adapter.checkpoint_pending=False
    return receipt


def request_red_duration(conn, requests, time_s, remaining_s, cycle_end_s, output, program):
    """Audit one official duration API; retain attempt on API/readback failure."""
    require(type(time_s) is int and type(remaining_s) is int and remaining_s>=1 and
        type(cycle_end_s) is int and time_s+remaining_s==cycle_end_s,'red duration clock inputs unknown')
    require(conn.simulation.getTime()==time_s and conn.trafficlight.getProgram(TLS)==program and
        conn.trafficlight.getPhase(TLS)==2 and conn.trafficlight.getRedYellowGreenState(TLS)=='r','duration requires actual bound red ACK')
    record={'time_s':time_s,'method':'setPhaseDuration','value':remaining_s,'call_completed':False}
    requests.append(record)
    append_new(output/'policy_duration_requests.jsonl',{**record,'status':'ATTEMPTED','cycle_end_s':cycle_end_s})
    try:
        # FrameCache treats this official setter as a mutator and invalidates.
        conn.trafficlight.setPhaseDuration(TLS,remaining_s)
        record['call_completed']=True
        record['actual_readback']={'time_s':conn.simulation.getTime(),'program':conn.trafficlight.getProgram(TLS),
            'phase':conn.trafficlight.getPhase(TLS),'state':conn.trafficlight.getRedYellowGreenState(TLS),
            'nextSwitch_s':conn.trafficlight.getNextSwitch(TLS)}
        actual=record['actual_readback']
        require(actual=={'time_s':time_s,'program':program,'phase':2,'state':'r','nextSwitch_s':cycle_end_s},'red duration readback mismatch')
        append_new(output/'policy_duration_requests.jsonl',{**record,'status':'READBACK_VERIFIED','cycle_end_s':cycle_end_s})
    except Exception as exc:
        append_new(output/'policy_duration_requests.jsonl',{**record,'status':'FAILED_STOP','cycle_end_s':cycle_end_s,'error':type(exc).__name__+':'+str(exc)})
        raise


def policy_after_ack(conn, adapter, worker, output):
    """Close observed green, or extend ACTUAL red; never change a pending phase."""
    t=adapter.last_completed
    if t <= 1200 or t >= adapter.end_s:
        return
    cycle=adapter.ledger.cycle
    if cycle is None:
        return
    requests=[]
    state=conn.trafficlight.getRedYellowGreenState(TLS)
    phase=conn.trafficlight.getPhase(TLS)
    require(conn.simulation.getTime()==t and conn.trafficlight.getProgram(TLS)==cycle['program'],'policy ACK signal identity')
    if adapter.previous_motion=='G' and state=='G' and cycle['green_end_s'] is None and cycle['N_G'] >= cycle['requested_quota']:
        require(adapter.receipts and adapter.receipts[-1]['time_end_s']==t,'yellow observation frame unknown')
        world=adapter.receipts[-1]['post_world']
        current_ids=tuple(conn.vehicle.getIDList())
        require(len(set(current_ids))==len(current_ids) and set(current_ids)==set(world),'yellow world IDs unbound')
        vehicles,ids,_,_=adapter.observe(conn)
        local=set(ids[STORAGE])|set(ids[INGRESS])
        require(len(vehicles)==len(local) and {v.vehicle_id for v in vehicles}==local,'yellow local population unknown')
        for lane in (STORAGE,INGRESS):
            require(set(ids[lane])==set(conn.lane.getLastStepVehicleIDs(lane))=={v for v,w in world.items() if w['lane_id']==lane},'yellow lane population unbound')
        for v in vehicles:
            lane=STORAGE if v.population=='storage' else INGRESS
            pos=conn.vehicle.getLanePosition(v.vehicle_id)-(113.08 if v.population=='ingress' else 0)
            require(world[v.vehicle_id]['lane_id']==lane and abs(v.speed_m_s-world[v.vehicle_id]['speed_m_s'])<=1e-8 and
                abs(v.position_m-pos)<=1e-8 and abs(v.length_m-conn.vehicle.getLength(v.vehicle_id))<=1e-8 and
                abs(v.normal_decel_m_s2-conn.vehicle.getDecel(v.vehicle_id))<=1e-8,'yellow position/speed/body unbound')
        require(conn.simulation.getTime()==t,'yellow final source time drift')
        scope=yellow_scope(vehicles,t,cycle['yellow_s']);scope['source_post_frame_time_s']=t;adapter.last_yellow_scope=scope
        append_new(output/'yellow_scope.jsonl',scope)
        require(scope['status']=='PASS','UNKNOWN_LOCAL_YELLOW_SCOPE')
        require(phase==0 and t<=cycle['begin_s']+MAX_GREEN,'green close wrong phase/budget')
        worker.request_phase(conn.trafficlight,requests,t,'setPhase',1)
        require(conn.trafficlight.getPhase(TLS)==1 and conn.trafficlight.getRedYellowGreenState(TLS)=='y' and conn.trafficlight.getNextSwitch(TLS)==t+cycle['yellow_s'],'yellow command readback mismatch')
        adapter.ledger.close_green(t,'ACTUAL_QUOTA_ACK')
    if adapter.previous_motion=='r' and phase==2 and state=='r' and not cycle.get('red_clock_bound'):
        remaining=cycle['end_s']-t
        require(type(remaining) is int and remaining>=1,'remaining red clock unknown')
        require(cycle['green_end_s'] is not None and cycle['end_s']-cycle['green_end_s']-cycle['yellow_s']>=2,'minimum total red violated')
        request_red_duration(conn,requests,t,remaining,cycle['end_s'],output,cycle['program'])
        require(conn.trafficlight.getPhase(TLS)==2 and conn.trafficlight.getRedYellowGreenState(TLS)=='r' and conn.trafficlight.getNextSwitch(TLS)==cycle['end_s'],'red clock readback mismatch')
        cycle['red_clock_bound']=True
        cycle['remaining_red_set_at_s']=t
        cycle['remaining_red_duration_s']=remaining
    if requests:
        append_new(output/'policy_phase_requests.jsonl',{'time_s':t,'requests':requests,'cycle_id':cycle['cycle_id'],'cycle_end_s':cycle['end_s'],'actual_quota_N_G':cycle['N_G'],'requested_quota':cycle['requested_quota'],
            'actual_readback':{'time_s':conn.simulation.getTime(),'phase':conn.trafficlight.getPhase(TLS),
                'state':conn.trafficlight.getRedYellowGreenState(TLS),'nextSwitch_s':conn.trafficlight.getNextSwitch(TLS)}})


def _diagnostic_loop(conn, worker, capture, output, resources, process, start_time, adapter=None, producer=None):
    """Private post-release loop; fake tests inject here, not a public launch API."""
    adapter=adapter or StepAdapter(worker.observe)
    producer=producer or Producer('fixed300',300)
    command_cursor=feedback_cursor=0
    def flush_events():
        nonlocal command_cursor,feedback_cursor
        for row in adapter.ledger.events[command_cursor:]:append_new(output/'command_events.jsonl',row)
        command_cursor=len(adapter.ledger.events)
        for row in producer.events[feedback_cursor:]:append_new(output/'feedback_events.jsonl',row)
        feedback_cursor=len(producer.events)
    conn=FrameCache(conn)
    adapter.query_cache_stats=conn.stats
    phase_requests=[]
    worker.request_phase(conn.trafficlight,phase_requests,0,'setProgram','A_OPEN')
    worker.request_phase(conn.trafficlight,phase_requests,0,'setPhase',0)
    for t in range(adapter.end_s):
        require(time.monotonic()-start_time<=resources['wall_limit_s'],'wall resource STOP')
        require(shutil.disk_usage(output).free>=resources['minimum_free_bytes'],'disk reserve STOP')
        require(sum(p.stat().st_size for p in output.rglob('*') if p.is_file())<=resources['run_limit_bytes'],'output bytes STOP')
        if 'total_budget_baseline' in resources:
            bound=resources['total_budget_baseline']
            require(bound['charged_monitored_s']+time.monotonic()-start_time<=budget.TOTAL_WALL,'total monitored resource STOP')
            require(bound['charged_raw_bytes']+sum(p.stat().st_size for p in output.parent.rglob('*') if p.is_file())<=budget.TOTAL_BYTES,'total raw resource STOP')
        require(process.poll() is None,'native child exited before observed step')
        if t==600:
            worker.request_phase(conn.trafficlight,phase_requests,t,'setProgram','CA_C8')
            worker.request_phase(conn.trafficlight,phase_requests,t,'setPhase',1)
        if t>=1200:
            old_program=conn.trafficlight.getProgram(TLS)
            command=producer.command_at(conn,t)
            new,cycle=adapter.ledger.begin_step(t,command)
            flush_events()
            adapter.command=adapter.ledger.pending_command.rate_veh_h
            if new:
                bound=admission(conn,t,worker.observe,old_program)
                bound.update(applied_request_id=cycle['applied_request_id'],cycle_id=cycle['cycle_id'],
                    period_s=cycle['period_s'],new_program=cycle['program'])
                append_new(output/'admission.jsonl',bound)
                body=adapter.body.observe(conn,t,inventory(conn)[0],[], 'r')
                append_new(output/'body_admission.jsonl',body)
                if t==1200 or old_program!=cycle['program']:
                    worker.request_phase(conn.trafficlight,phase_requests,t,'setProgram',cycle['program'])
                    worker.request_phase(conn.trafficlight,phase_requests,t,'setPhase',0)
                    require(conn.trafficlight.getProgram(TLS)==cycle['program'] and
                        conn.trafficlight.getPhase(TLS)==0 and conn.trafficlight.getRedYellowGreenState(TLS)=='G' and
                        conn.trafficlight.getNextSwitch(TLS)==t+4,'new program green readback unknown')
                    adapter.selected_new_program_at=t
                else:
                    adapter.selected_new_program_at=None
        before=adapter.prepare_step(conn,t)
        append_new(output/'pre_steps.jsonl',{'time_s':t,'bound_snapshot':adapter.pending,'preparation':before,'phase_requests':phase_requests})
        # All log cursors began at byte0 including startup/control queries. Check
        # existing stderr before motion, then consume the afterACK interval.
        pre=capture.snapshot(t,t,'PRE_MOTION_AFTER_CONTROL_AND_OBSERVATION')
        append_new(output/'log_intervals.jsonl',pre)
        require(not pre['streams']['sumo_stderr.log']['text'],'native stderr before motion')
        conn.simulationStep(t+1)
        adapter.bridge_last_ack={'requested_target_s':t+1,'ACK_received':True,'actual_readback_s':None,'actual_time_verified':False}
        append_new(output/'step_ack.jsonl',adapter.bridge_last_ack)
        actual=conn.simulation.getTime()
        adapter.bridge_last_ack['actual_readback_s']=actual
        require(type(actual) in (int,float) and actual==t+1,'ACK actual simulation time mismatch')
        adapter.bridge_last_ack['actual_time_verified']=True
        adapter.last_completed=actual
        append_new(output/'step_ack.jsonl',adapter.bridge_last_ack)
        after=capture.snapshot(t,t+1,'AFTER_SIMULATION_STEP_ACK')
        append_new(output/'log_intervals.jsonl',after)
        try:row=adapter.reconcile_step(conn,capture.adapter_warning(after))
        except Exception:
            append_new(output/'post_steps.jsonl',{'time_s':t,'retained_receipts':[r for r in adapter.receipts if r.get('time_begin_s')==t] ,'pending':adapter.pending,'last_completed_s':adapter.last_completed,'last_accounted_s':adapter.last_end})
            raise
        append_new(output/'post_steps.jsonl',row)
        producer.after_ack(conn,t+1)
        flush_events()
        policy_after_ack(conn,adapter,worker,output)
        if adapter.checkpoint_pending:
            checkpoint(conn, adapter, capture, output, start_time)
        if adapter.paused:
            require(t==adapter.end_s-1,'unexpected diagnostic pause')
            if adapter.ledger.cycle['completed']:
                require(conn.trafficlight.getPhase(TLS)==2 and conn.trafficlight.getRedYellowGreenState(TLS)=='r' and conn.trafficlight.getNextSwitch(TLS)==adapter.end_s,'final native cycle boundary drift')
            else:
                require(producer.mode=='real_alinea','unapproved partial final cycle')
            if producer.mode=='real_alinea':
                require(any(x.startswith('feedback:') and r['first_application_s'] is not None for x,r in adapter.ledger.requests.items()),'REAL_FEEDBACK_COMMAND_NOT_OBSERVED_APPLIED')
            adapter.loop_terminal_elapsed_s=time.monotonic()-start_time
            return adapter
        phase_requests=[]
    raise ValueError('approved horizon stop missing')


def execute(card_path, release_path, root=ROOT):
    root=Path(root).resolve()
    require(root==ROOT,'execute root injection prohibited')
    card=validate_release(card_path,release_path,root)
    total_budget=budget.accounting(root)
    effective=budget.effective_limits(card['resources'],total_budget)
    run=card['spec']['run_id']
    output=root/card['output'];parent=output.parent
    require(not parent.exists(),'run identity/output already consumed')
    require(shutil.disk_usage(root).free>=card['resources']['minimum_free_bytes'],'insufficient fresh disk reserve')
    parent.mkdir(parents=True,exist_ok=False);output.mkdir()
    write_new(parent/'ONE_USE_RESERVATION.json',{'run_id':run,'card_sha256':sha(card_path),'release_sha256':sha(release_path),'status':'CONSUMED_NO_RETRY'})
    write_new(parent/'TOTAL_BUDGET_RESERVATION.json',{'run_id':run,'history_bound':total_budget,'single_ceiling_resources':card['resources'],'effective_total_remaining_limits':effective,'unknown_or_incomplete_reservation_never_released_implicitly':True})
    # Review source/input snapshots before any child can alter output.
    snaps=output/'snapshots';snaps.mkdir()
    for p,h in {**card['sources_sha256'],**card['prepared_input_sha256'],**card['inherited_inputs_sha256'],str(NETWORK):card['network_sha256']}.items():
        target=snaps/p;target.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(root/p,target);require(sha(target)==h,'fresh snapshot drift')
    shutil.copyfile(card_path,output/'card.json');shutil.copyfile(release_path,output/'release.json')
    process=None;conn=None;capture=None;adapter=None;producer=None;watchdog=None;normal_closed=False;status='ABORTED_UNKNOWN';error='';final_logs=None
    started=time.monotonic()
    try:
        capture=LogCapture(output)
        worker=protected_worker()
        import traci  # Authorized entry only; does not itself spawn.
        with socket.socket() as sock:sock.bind(('127.0.0.1',0));port=sock.getsockname()[1]
        env=worker.sumo_launch_environment()
        command=[str(SUMO),'-c',str(root/card['package']/'scenario.sumocfg'),'--remote-port',str(port)]
        write_new(output/'startup_context.json',{'command':command,'SUMO_HOME':env['SUMO_HOME'],'native_warning_suppression':False,'aggregate_warnings':-1,'source_compiler_equivalence':'NOT_VERIFIED'})
        process=worker.launch_sumo_process(command,capture.handles['sumo_stdout.log'],capture.handles['sumo_stderr.log'],env)
        watchdog=ResourceWatchdog(process,parent,effective,started);watchdog.start()
        conn=worker.connect_traci(traci,port,process,worker.startup_trace_callback(output/'startup_trace.jsonl'),deadline_s=card['resources']['startup_limit_s'])
        startup=capture.snapshot(0,0,'STARTUP_CONNECT_ACK');append_new(output/'log_intervals.jsonl',startup)
        require(not startup['streams']['sumo_stderr.log']['text'],'startup stderr nonempty')
        authority={**card['numerical_exception_authority'],'execution_card_sha256':sha(card_path)}
        adapter=StepAdapter(worker.observe,card['spec']['fixed_command_veh_h'],card['spec']['end_s'],authority)
        producer=Producer(card['spec']['mode'],card['spec']['fixed_command_veh_h'])
        _diagnostic_loop(conn,worker,capture,output,{**effective,'total_budget_baseline':total_budget},process,started,adapter,producer)
        status='PACKET_CYCLES_PENDING_LOG_FINALIZATION'
    except Exception as exc:
        error=type(exc).__name__+':'+str(exc)
        write_new(output/'failure_snapshot.json',json.loads(json.dumps({'error':error,'last_completed_s':adapter.last_completed if adapter else None,
            'last_step_ack':getattr(adapter,'bridge_last_ack',None),
            'same_state_query_cache':getattr(adapter,'query_cache_stats',None),
            'last_accounted_s':adapter.last_end if adapter else None,'pending':adapter.pending if adapter else None,
            'accounting':adapter.ledger.accounting() if adapter else None,
            'retained_last_observation':adapter.receipts[-1:] if adapter else [],
            'last_yellow_scope':getattr(adapter,'last_yellow_scope',None),
            'original_logs_preserved':True},default=encoded)))
    finally:
        if conn is not None:
            try:conn.close();normal_closed=True
            except Exception as exc:error+=';close:'+type(exc).__name__+':'+str(exc)
        if process is not None:
            try:process.wait(timeout=5)
            except Exception as exc:
                normal_closed=False;error+=';wait:'+type(exc).__name__+':'+str(exc)
                try:process.terminate();process.wait(timeout=5)
                except Exception as kill_error:
                    error+=';terminate:'+str(kill_error)
                    try:process.kill();process.wait(timeout=5)
                    except Exception as final_kill_error:error+=';kill:'+str(final_kill_error)
            if process.returncode!=0:normal_closed=False
        if watchdog is not None:
            watchdog.close()
            if watchdog.reason or watchdog.error:
                normal_closed=False;error+=';watchdog:'+str(watchdog.reason)+':'+str(watchdog.error)
        if capture is not None:
            try:
                require(process is not None,'native process not started')
                final_logs=capture.finalize(process,adapter.last_completed if adapter else None,normal_closed)
                append_new(output/'log_intervals.jsonl',capture.records[-1])
                if final_logs['status']!='BOUND_NO_OBSERVED_NATIVE_MESSAGE':status='STOP_UNKNOWN_LOG_COVERAGE_OR_NATIVE_MESSAGE'
            except Exception as exc:
                status='STOP_UNKNOWN_LOG_FINALIZATION';error+=';logfinal:'+type(exc).__name__+':'+str(exc)
            capture.close_handles()
        if status=='PACKET_CYCLES_PENDING_LOG_FINALIZATION':
            status=('APPROVED_END_PARTIAL_OR_BODY_CENSORED_NOT_QUALIFIED'
                if not adapter.ledger.cycle['completed'] or adapter.body.active else
                'PACKET_CYCLES_OBSERVED_NO_MONITORED_ANOMALY_NOT_QUALIFIED')
        write_new(output/'bridge_receipt.json',{'run_id':run,'card_sha256':sha(card_path),'status':status,'error':error,
            'native_started':process is not None,'last_completed_s':adapter.last_completed if adapter else None,
            'last_step_ack':getattr(adapter,'bridge_last_ack',None),
            'same_state_query_cache':getattr(adapter,'query_cache_stats',None),
            'last_accounted_s':adapter.last_end if adapter else None,'final_logs':final_logs,
            'resource_watchdog':{'reason':watchdog.reason,'error':watchdog.error,'poll_s':.2} if watchdog else None,
            'actual_native_safety_proven':False,'rate_qualified':False,'automatic_continuation':False,
            'terminal_arrival_audit':'PENDING_INDEPENDENT_FINAL_TRIPINFO_AUDIT_NOT_ONLINE_FULL_COVERAGE',
            'first_red_checkpoint_verified':getattr(adapter,'checkpoint_verified',False),
            'cycles':adapter.ledger.rows if adapter else None,
            'command_records':adapter.ledger.requests if adapter else None,
            'approved_mode':card['spec']['mode'],'approved_end_s':card['spec']['end_s'],
            'partial_final_cycle':bool(adapter and adapter.ledger.cycle and not adapter.ledger.cycle['completed']),
            'body_censored_ids':sorted(adapter.body.active) if adapter and hasattr(adapter.body,'active') else [],
            'real_feedback_decision_count':sum(x.get('event')=='PROJECT_FEEDBACK_DECISION' for x in producer.events) if producer else 0,
            'real_feedback_applied_request_ids':[x for x,r in adapter.ledger.requests.items() if x.startswith('feedback:') and r['first_application_s'] is not None] if adapter else [],
            'control_accounting':adapter.ledger.accounting() if adapter and adapter.last_end is not None and adapter.last_end>1200 else None,
            'total_budget_before_run':total_budget,'effective_resource_limits':effective,
            'budget_timer_scope':'monitored startup plus loop and owned-child cleanup; whole CLI separate',
            'loop_terminal_elapsed_s':getattr(adapter,'loop_terminal_elapsed_s',None),
            'monitored_elapsed_through_cleanup_s':time.monotonic()-started,
            'files_sha256':{str(p.relative_to(output)):sha(p) for p in output.rglob('*') if p.is_file()}})
    return 0 if status in ('PACKET_CYCLES_OBSERVED_NO_MONITORED_ANOMALY_NOT_QUALIFIED',
        'APPROVED_END_PARTIAL_OR_BODY_CENSORED_NOT_QUALIFIED') else 1

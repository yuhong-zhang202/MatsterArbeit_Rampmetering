"""Independent, parameterized development audit and descriptive measurements.

No simulation imports or raw writes. Historical measurement definitions retained.
"""
import argparse, csv, importlib.util, json, math, sys
from pathlib import Path
from collections import Counter
import xml.etree.ElementTree as ET
sys.dont_write_bytecode=True
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[2]

def module(path,name):
    spec=importlib.util.spec_from_file_location(name,path)
    obj=importlib.util.module_from_spec(spec);spec.loader.exec_module(obj);return obj

A=module(ROOT/'scripts/stage6/standard_metering_analysis_20261003/analysis.py','reviewed_measurement')
B=A.boundary

def truth(value):
    if value in (True,'True','true','1',1):return True
    if value in (False,'False','false','0',0):return False
    raise ValueError('invalid boolean '+str(value))

def read_csv(p):
    with Path(p).open() as f:return list(csv.DictReader(f))

def write(path,obj):
    with Path(path).open('x') as f:json.dump(obj,f,indent=2);f.write('\n')

def independent_guard(row,metadata,stopline):
    states=json.loads(row['guard_vehicle_states_json']);decision=json.loads(row['guard_decision_json'])
    if not states:return False,'NO_FRONT'
    assert len({v['vehicle_id'] for v in states})==len(states)==int(row['queue_vehicle_count'])
    front=max(states,key=lambda v:v['position_m']);fid=front['vehicle_id'];gap=stopline-front['position_m']
    assert row['front_queued_vehicle_id']==fid and gap>=0
    unsafe=[]
    for v in states:
        speed=v['speed_m_s'];acc=v['accel_m_s2'];decel=v['decel_m_s2']
        assert speed>=0 and acc>0 and decel>0
        need=0 if speed<.1 else 1.1+(speed+acc)+(speed+acc)**2/(2*decel)
        if v['vehicle_id']!=fid and stopline-v['position_m']+1e-9<need:unsafe.append(v['vehicle_id'])
    assert set(unsafe)==set(json.loads(row['guard_failed_follower_ids_json']))
    if unsafe:return False,'FOLLOWER_STOP_DISTANCE'
    e=decision['input_evidence'];rear=e['nearest_internal_rear_clearance_m'];rear=math.inf if rear is None else rear
    internal=e['nearest_internal_vehicle_id'];leader=e['leader'];secure=e['secure_gap_m']
    length=float(metadata[fid]['vehicle_length_m']);mingap=float(metadata[fid]['min_gap_m'])
    if front['speed_m_s']<.1:
        okay=gap<=1.1 and (internal is None or rear>=length+mingap)
        return okay,'STOPPED_READY' if okay else 'STOPPED_FRONT_OR_RECEIVER_NOT_READY'
    speed=front['speed_m_s']+front['accel_m_s2']
    required=max(e['connected_path_length_m'],length+mingap+1.1+speed+speed**2/(2*front['decel_m_s2']))
    if gap>speed:return False,'FRONT_NOT_ONE_STEP_REACHABLE'
    if not e['route_coverage_ok'] or e['leader_lookahead_m']+1e-9<required:return False,'DOWNSTREAM_COVERAGE_UNKNOWN'
    if internal is not None and (leader is None or leader['vehicle_id']!=internal):return False,'INTERNAL_LEADER_MISMATCH'
    if leader is not None and leader['lane_id'] not in {':ramp_mid_0_0','ramp_accel_0',':freeway_merge_2_0','merge_section_0'}:return False,'LEADER_OFF_CHECKED_PATH'
    if leader is not None and (secure is None or not math.isfinite(secure) or secure<0):return False,'SECURE_GAP_UNAVAILABLE'
    if leader is not None and leader['gap_excluding_ego_min_gap_m']+1e-9<secure+1.1:return False,'LEADER_SECURE_GAP'
    if internal is not None:
        if not math.isfinite(rear):return False,'INTERNAL_CLEARANCE_UNKNOWN'
        if rear+gap-mingap+1e-9<secure+1.1 or rear+1e-9<length+mingap+max(0,speed-gap)+1.1:return False,'INTERNAL_RECEIVER_CLEARANCE'
    return True,'MOVING_READY'

def feedback_and_commands(raw,card):
    rows=read_csv(raw/'controller_steps.csv');updates=read_csv(raw/'feedback_updates.csv')
    assert len(rows)==4200 and len(updates)==119
    previous=900.;bytime={};nominal={};r=900.
    controlled=card['mode']=='ALINEA'
    for t,u in zip(range(630,4171,30),updates):
        assert float(u['decision_time_s'])==t and float(u['interval_begin_s'])==t-30 and float(u['interval_end_s'])==t
        if controlled:
            mean=(float(u['occ_l0_pct'])+float(u['occ_l1_pct']))/2
            rawrate=previous+70*(11-mean);clipped=max(300,min(900,rawrate))
            for key,v in [('occ_mean_pct',mean),('rate_previous_veh_h',previous),('rate_raw_veh_h',rawrate),('rate_clipped_veh_h',clipped)]:assert abs(float(u[key])-v)<1e-7,(t,key)
            previous=clipped;bytime[t]=(rawrate,clipped)
    for t in range(4200):
        if t in bytime:r=bytime[t][1]
        nominal[t]=r
        assert float(rows[t]['time_begin_s'])==t and float(rows[t]['time_end_s'])==t+1
    feedback=A.reconcile_feedback_xml(raw)
    events=A.reconcile_event_feedback(raw)
    return rows,nominal,feedback,events

def control_identity(rows,metadata,card):
    credit=0.;dropped=0.;last_green=None;counts=Counter();minmargin=math.inf;stopline=card['meter_controlled_link']['storage_length_m']
    for t,row in enumerate(rows):
        if t<600:
            assert row['observed_state']=='G' and not row['requested_state'];continue
        rate=float(row['command_rate_veh_h']);before=credit;credit+=rate/3600
        due=credit>=1-1e-10 and (last_green is None or t-last_green>=3)
        allowed,reason=independent_guard(row,metadata,stopline)
        assert truth(row['guard_allowed'])==allowed
        assert row['guard_reason']==(reason if due else 'NOT_DUE_OR_MIN_RED')
        green=due and allowed
        assert truth(row['nominal_slot_scheduled'])==due and truth(row['slot_scheduled'])==green
        if green:credit-=1;last_green=t
        if credit>1:dropped+=credit-1;credit=1
        for key,value in [('credit_before',before),('credit_after',credit),('dropped_credit_total',dropped)]:assert abs(float(row[key])-value)<1e-7,(t,key)
        assert row['observed_state']==row['requested_state']==('G' if green else 'r')
        crossings=json.loads(row['crossing_bracket_ids_json']);counts['actual_crossings']+=len(crossings);counts['greens']+=green
        assert len(crossings)<=1 and (green or not crossings)
        if crossings:assert crossings==[row['front_queued_vehicle_id']]
        if green:
            inter=json.loads(row['post_green_interlock_json']);e=inter['input_evidence']
            for v in e['remaining_storage'].values():
                speed=v['speed_m_s'];need=0 if speed<.1 else 1.1+speed+speed**2/(2*v['normal_decel_m_s2'])
                margin=stopline-v['position_m']-need;assert margin>=-1e-9;minmargin=min(minmargin,margin)
            assert not inter['abort'] and inter['safe_to_red']
        counts[reason]+=1;counts['due_attempts']+=due;counts['denied_due']+=due and not allowed
    command=sum(float(r['command_rate_veh_h'])/3600 for r in rows[600:]);residual=command-counts['greens']-dropped-credit
    assert abs(residual)<1e-7
    return dict(status='PASS',counts=dict(counts),command_credit=command,dropped_credit=dropped,final_credit=credit,credit_residual=residual,min_post_green_stop_margin_m=minmargin,scope='Independent arithmetic conditional on logged TraCI sensor/secureGap values; FCD sensor identity is checked separately.')

def queue_identity(raw,rows,nominal,card,params):
    qrows=read_csv(raw/'queue_override.csv') if (raw/'queue_override.csv').exists() else None
    if qrows is None:
        return dict(status='ABSENT_OLD_T1_LOG',scope='Nominal command remains independently audited. No new override was present in old T1.'),None
    assert len(qrows)==4200
    active=False;trigger=release=0;transitions=[]
    for t,q in enumerate(qrows):
        assert float(q['time_begin_s'])==t and truth(q['observation_valid'])
        if t<600:
            assert not truth(q['override_active']) and not q['nominal_clipped_veh_h'] and not q['final_command_veh_h']
            assert int(q['actual_crossings'])==len(json.loads(rows[t]['crossing_bracket_ids_json']))
            continue
        n=float(q['nominal_clipped_veh_h']);assert abs(n-nominal[t])<1e-7
        if card['treatment']!='T2':
            assert not truth(q['override_active']) and abs(float(q['final_command_veh_h'])-n)<1e-7
        else:
            risk=float(q['risk_extent_m']);assert math.isfinite(risk) and risk>=0
            prior=active;transition='NONE'
            if not active:
                release=0;trigger=trigger+1 if risk>=params['trigger_distance_m'] else 0
                if trigger>=params['trigger_confirm_s']:active=True;trigger=0;transition='ACTIVATE'
            else:
                trigger=0;release=release+1 if risk<=params['release_distance_m'] else 0
                if release>=params['release_confirm_s']:active=False;release=0;transition='RELEASE'
            assert truth(q['override_active_before'])==prior and truth(q['override_active'])==active and q['transition']==transition
            assert int(q['trigger_streak_s'])==trigger and int(q['release_streak_s'])==release
            final=max(n,900) if active else n
            assert abs(float(q['final_command_veh_h'])-final)<1e-7
            if transition!='NONE':transitions.append(dict(time=t,transition=transition,risk_extent_m=risk))
        if t>=600:assert abs(float(rows[t]['command_rate_veh_h'])-float(q['final_command_veh_h']))<1e-7
        assert int(q['actual_crossings'])==len(json.loads(rows[t]['crossing_bracket_ids_json']))
    return dict(status='PASS',active_seconds=sum(truth(q['override_active']) for q in qrows),transitions=transitions,release_coverage=any(t['transition']=='RELEASE' for t in transitions),scope='Prospective rule replay from logged complete risk observations; FCD/body-coordinate mapping separately checked.'),qrows

def service_windows(rows):
    out=[]
    for begin in range(1200,3000,300):
        selected=rows[begin:begin+300]
        command=sum(float(r['command_rate_veh_h'])/3600 for r in selected)
        ids=[v for r in selected for v in json.loads(r['crossing_bracket_ids_json'])];assert len(ids)==len(set(ids))
        supply=sum(int(r['queue_vehicle_count'])>=1 for r in selected);eligible=supply==300
        error=abs(len(ids)-command)/command
        out.append(dict(begin=begin,end=begin+300,final_command_credit=command,actual_crossings=len(ids),storage_supply_seconds=supply,eligible_continuous_supply=eligible,relative_error=error,engineering_status='PASS' if eligible and error<=.1 else 'FAIL' if eligible else 'NOT_TESTED_NO_CONTINUOUS_SUPPLY',denied_due_seconds=sum(truth(r['guard_rejected_slot']) for r in selected)))
    return out

def spatial_queue_and_endpoint(raw,qrows,network,metadata):
    lane_names=['shared_approach_0',':urban_diverge_1_0','ramp_storage_0']
    lane_lengths={e.get('id'):float(e.get('length')) for e in ET.parse(network).iter('lane')}
    offset={};stopline=0.
    for lane in lane_names:offset[lane]=stopline;stopline+=lane_lengths[lane]
    checked=0;ambiguous_speed=0;max_pos_error=max_speed_error=0.;endpoint=[]
    for e in A.records(raw/'fcd.xml.gz','timestep'):
        t=int(float(e.get('time')));prior={v.get('id'):dict(v.attrib) for v in e if v.get('lane') in lane_names}
        if qrows is not None and 599<=t<=4198:
            q=qrows[t+1];obs=json.loads(q['observed_vehicle_records_json']);byid={v['id']:v for v in obs}
            assert len(byid)==len(obs)==int(q['mapped_vehicle_count']) and set(byid)==set(prior)
            low=[];risk=shared=0.
            for vid,v in byid.items():
                f=prior[vid];assert v['lane']==f['lane']
                pe=abs(v['front_m']-float(f['pos']));se=abs(v['speed_m_s']-float(f['speed']))
                max_pos_error=max(max_pos_error,pe);max_speed_error=max(max_speed_error,se)
                assert pe<=.005001 and se<=.005001
                assert abs(v['length_m']-float(metadata[vid]['vehicle_length_m']))<1e-9
                if abs(float(f['speed'])-1.389)<=.005001:ambiguous_speed+=1
                if vid.split('_',1)[0]=='R' and v['speed_m_s']<1.389:
                    distance=stopline-(offset[v['lane']]+v['front_m']-v['length_m'])
                    low.append(dict(v,rear_distance_upstream_meter_m=distance))
                    if v['lane']==lane_names[0]:shared=max(shared,distance)
                    else:risk=max(risk,distance)
            loggedlow=json.loads(q['low_R_records_json'])
            assert {v['id'] for v in low}=={v['id'] for v in loggedlow}
            for v in loggedlow:
                own=next(x for x in low if x['id']==v['id'])
                assert abs(own['rear_distance_upstream_meter_m']-v['rear_distance_upstream_meter_m'])<1e-8
            assert abs(float(q['risk_extent_m'])-risk)<1e-8 and abs(float(q['shared_low_R_extent_m'])-shared)<1e-8
            checked+=1
        if t==4199:
            endpoint=[dict(id=v.get('id'),vehicle_class=v.get('id').split('_',1)[0],lane=v.get('lane'),position_m=float(v.get('pos')),speed_m_s=float(v.get('speed')),x_m=float(v.get('x')),y_m=float(v.get('y'))) for v in e]
    return dict(status='PASS',prestep_snapshots_checked=checked,max_position_precision_residual_m=max_pos_error,max_speed_precision_residual_m_s=max_speed_error,fcd_low_speed_boundary_ambiguous_observations=ambiguous_speed,scope='Complete logged high-precision lane snapshots validated against previous-step rounded FCD and actual length metadata; risk recomputed independently. Rounded speed boundary cases retain ambiguity, not substituted into high-precision state decisions.'),endpoint

def aggregate_integral(raw,package,classes):
    planned=ET.parse(package/'demand.rou.xml').getroot().findall('vehicle')
    exposure=sum(4200-float(v.get('depart')) for v in planned)
    steps=ET.parse(raw/'sumo_summary.xml').getroot().findall('step')
    assert len(steps)==4200
    derived={'scheduled_system_time_observed_total_s':exposure-sum(int(s.get('arrived')) for s in steps),'external_wait_observed_total_s':exposure-sum(int(s.get('inserted')) for s in steps),'in_network_observed_total_s':sum(int(s.get('running')) for s in steps)}
    residual={k:v-sum(c[k] for c in classes) for k,v in derived.items()}
    assert max(map(abs,residual.values()))<1e-6
    return dict(status='PASS',integral_costs_s=derived,residuals_s=residual,scope='Independent whole-cohort cumulative summary integral; no lane-count double counting.')

def main():
    p=argparse.ArgumentParser();p.add_argument('--card',type=Path,required=True);p.add_argument('--baseline-card',type=Path,required=True);p.add_argument('--out-name',required=True);p.add_argument('--queue-parameters',type=Path);args=p.parse_args()
    card=json.loads(args.card.read_text());base=json.loads(args.baseline_card.read_text());raw=Path(card['output']);out=HERE/args.out_name
    assert not out.exists(),'Never overwrite an audit'
    A.validate_current_receipt(raw,args.card)
    package=Path(card['package']);basepackage=Path(base['package'])
    for name,digest in card['input_sha256'].items():assert A.sha(package/name)==digest
    assert A.sha(package/'demand.rou.xml')==A.sha(basepackage/'demand.rou.xml')
    assert card['network_sha256']==base['network_sha256'] and card['sumo_sha256']==base['sumo_sha256'] and card['seed']==base['seed']
    cfg=json.loads((ROOT/'artifacts/stage6_boundary_search_20261002_v1/analysis_config.json').read_text())
    summary=B.analyze(raw,package/'demand.rou.xml',cfg,out,args.card)
    network=Path(ET.parse(package/'scenario.sumocfg').find('.//net-file').get('value'))
    pre=A.pre600(Path(base['output'])/'fcd.xml.gz',raw/'fcd.xml.gz');write(out/'pre600_comparison.json',pre)
    assert pre['equal'],'Pre-treatment trajectory differs'
    rows,nominal,feedback,events=feedback_and_commands(raw,card)
    write(out/'integral_cost_audit.json',aggregate_integral(raw,package,summary['classes']))
    write(out/'feedback_xml_audit.json',feedback);write(out/'event_feedback_audit.json',events)
    city=A.city_evidence(raw/'fcd.xml.gz',raw/'tls_states.xml');write(out/'city_evidence.json',city)
    if card['mode']=='ALINEA':
        meta={r['vehicle_id']:r for r in read_csv(raw/'vehicle_metadata.csv')}
        identity=control_identity(rows,meta,card);write(out/'actuator_identity.json',identity)
        sampled=A.reconcile_service_fcd(raw,card);write(out/'sampled_service.json',sampled)
        # Retain the historical stopped-only helper result; qualify both V15 branches independently.
        import audit_v15_service as V15
        write(out/'v15_service_fcd_audit.json',V15.audit(raw,card))
        write(out/'v15_service_analysis_provenance.json',dict(script_sha256=A.sha(V15.__file__),supersedes_only='Historical sampled_service stopped-only geometry interpretation'))
        chain=A.chain_from_raw(raw,network);write(out/'operational_chain.json',chain)
        windows=service_windows(rows);write(out/'final_command_windows.json',windows)
        if card.get('treatment')=='T2':assert args.queue_parameters,'Need registered queue parameter contract'
        parameter_record=json.loads(args.queue_parameters.read_text()) if args.queue_parameters else {}
        params=parameter_record.get('queue_protection',parameter_record)
        qa,qrows=queue_identity(raw,rows,nominal,card,params);write(out/'queue_identity.json',qa)
        spatial,endpoint=spatial_queue_and_endpoint(raw,qrows,network,meta)
        write(out/'queue_spatial_audit.json',spatial);write(out/'endpoint_vehicles.json',endpoint)
        assert len(endpoint)==sum(c['unfinished'] for c in summary['classes'])
    else:
        write(out/'neutral_comparison.json',A.neutral_compare(base['output'],raw))
    write(out/'adapter_provenance.json',dict(script_sha256=A.sha(__file__),analysis_classification='DEVELOPMENT',source_modules={str(Path(m.__file__)):A.sha(m.__file__) for m in [A,B]},card_sha256=A.sha(args.card),baseline_card_sha256=A.sha(args.baseline_card),queue_parameter_contract_sha256=A.sha(args.queue_parameters) if args.queue_parameters else None,formal_inference=False))
    print(json.dumps({'run_id':card['run_id'],'out':str(out),'classes':summary['classes'],'warnings':summary['warnings']}))

if __name__=='__main__':main()

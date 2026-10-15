"""Natural600 audit adaptation of preserved yellow evidence predicates.

No runtime safety predicate, model or phase configuration is changed.
"""
from scripts.cumulative_full_catalogue_audit_20261014_v1.core import need,near,number,catalogue

POLICY='NATIVE_YELLOW_RESPONSIBILITY_COMPLETE_INPUT_DIAGNOSTIC_V1'

def enabled_contract(contract):
    if contract is None:return False
    need(isinstance(contract,dict) and set(contract)=={'policy','enabled'} and contract['policy']==POLICY and type(contract['enabled']) is bool,'UNKNOWN_YELLOW_CONTRACT')
    return contract['enabled']

def yellow_record(yy,cycles,world,meta,last,diagnostic_contract=None):
    t=yy['time_s'];need(type(t) is int and t==yy['source_post_frame_time_s'] and 600<t<=last,'YELLOW_SOURCE_CLOCK')
    selected=[c for c in cycles if c['begin_s']<t<=c['begin_s']+c['max_green_s']];need(len(selected)==1,'YELLOW_CYCLE_BINDING')
    c=selected[0];P=catalogue(c['period_s']);Y=P['yellow_s']
    need(type(c['yellow_s']) is int and c['yellow_s']==Y and c['max_green_s']==P['max_green_s'],'YELLOW_CATALOGUE_PARAMETERS')
    need(type(yy['yellow_s']) is int and yy['yellow_s']==Y,'YELLOW_PERIOD')
    need(meta is not None,'MISSING_YELLOW_METADATA')
    need(yy.get('classification')=='BOUND_LOCAL_FEASIBILITY_NOT_GLOBAL_SAFETY' and len(yy['covered_ids'])==len(set(yy['covered_ids'])),'YELLOW_SCOPE_OR_DUPLICATE_COVERAGE')
    need(len({q['vehicle_id'] for q in yy['rows']})==len(yy['rows']) and {q['vehicle_id'] for q in yy['rows']}==set(yy['covered_ids'])=={v for v,w in world.items() if w['lane_id'] in ('ramp_storage_0',':urban_diverge_1_0')},'YELLOW_LOCAL_COMPLETE')
    enabled=enabled_contract(diagnostic_contract)
    need(yy['status'] in ('PASS','UNKNOWN'),'UNKNOWN_YELLOW_SCHEMA')
    failed=[]
    for q in yy['rows']:
        vid=q['vehicle_id'];v=meta[vid];population='ingress' if world[vid]['lane_id']==':urban_diverge_1_0' else 'storage'
        need(q['population']==population and number(q['position_m']) and ((population=='storage' and 0<=q['position_m']<204.49) or (population=='ingress' and -113.08<=q['position_m']<=0)),'YELLOW_POSITION_POPULATION_BOUND')
        offset=113.08 if population=='ingress' else 0
        need(q['time_s']==t and near(q['speed_m_s'],world[vid]['speed_m_s']) and q['native_future_safety_proven'] is False,'YELLOW_REAL_SPEED_ID')
        need(near(q['position_m'],v['position_m']-offset) and near(q['length_m'],v['length_m']) and near(q['normal_decel_m_s2'],v['normal_decel_m_s2']),'YELLOW_REAL_FIELDS')
        d=204.49-q['position_m'];speed=q['speed_m_s'];b=q['normal_decel_m_s2'];length=q['length_m'];dt=q['action_step_s']
        need(number(speed) and 0<=speed<=55.55555555555556 and number(d) and near(b,4.5) and near(length,5) and near(dt,1),'YELLOW_EFFECTIVE_MODEL_BOUND')
        one=d>0 and speed<=b*dt;stop=d>0 and (one or d>=speed*dt+speed*speed/(2*b));timing=None if speed==0 else dt+speed/(2*b)+length/speed;clear=speed>0 and timing<=Y and d+length<=speed*(Y-dt)
        need(q['one_step_Euler_stop_possible']==one and near(q['distance_to_meter_m'],d) and q['stop_possible']==stop and q['clear_possible']==clear,'YELLOW_INDEPENDENT_SCREEN')
        need(all(type(q[k]) is bool for k in ('one_step_Euler_stop_possible','stop_possible','clear_possible')),'UNKNOWN_YELLOW_BOOL_SCHEMA')
        need(number(q['stop_distance_screen_m']) and near(q['stop_distance_screen_m'],speed*dt+speed*speed/(2*b)),'YELLOW_STOP_DISTANCE_RECORD')
        recorded=q['body_clear_time_screen_s']
        need(recorded is None if timing is None else number(recorded) and near(recorded,timing),'YELLOW_CLEAR_TIME_RECORD')
        need(q['status']==('WITHIN_LOCAL_yellow_s_SCREEN' if stop or clear else 'UNKNOWN_LOCAL_yellow_s_SCOPE'),'YELLOW_ROW_STATUS_RECORD')
        if not (stop or clear):failed.append(vid)
    expected='PASS' if not failed else 'UNKNOWN'
    need(yy['status']==expected,'YELLOW_OVERALL_STATUS_RECORD')
    if not enabled:need(not failed,'UNKNOWN_LOCAL_YELLOW_SCOPE')
    else:
        d=yy['diagnostic_yellow_contract']
        need(d['policy']==POLICY and type(d['enabled']) is bool and d['enabled'] is True and d['original_witness_status']==expected and type(d['witness_established']) is bool and d['witness_established']==(not failed) and d['failed_witness_ids']==failed and type(d['allow_prepared_step']) is bool and d['allow_prepared_step'] is True and d['future_native_safety_proven'] is False and d['safety_certified'] is None and d['input_scope']=='ORIGINAL_HARD_FRESH_FRAME_AND_POPULATION_JOINS_REQUIRED' and d['interpretation']==('LEGACY_WITNESS_ESTABLISHED' if not failed else 'DIAGNOSTIC_WITNESS_NOT_ESTABLISHED'),'UNKNOWN_YELLOW_DIAGNOSTIC_RECORD')
    return True

def yellow_coverage(records,phase,cycles,post,pre,last,runtime_stop,diagnostic_contract=None):
    need(phase.get('status')=='PASS_CONTINUOUS_PHASES','UNKNOWN_PHASE_FOR_YELLOW_COVERAGE')
    expected={}
    for c in phase['cycles']:
        seq=c['observed_motion_sequence']
        if 'y' in seq:
            t=c['begin_s']+seq.index('y');need(c['green_end_s']==t and t not in expected,'YELLOW_OBSERVED_PHASE_BOUNDARY');expected[t]=c
    times=[q.get('time_s') for q in records]
    need(all(type(t) is int for t in times) and len(times)==len(set(times)),'DUPLICATE_OR_INVALID_YELLOW_RECORD')
    need(set(expected)<=set(times),'MISSING_OBSERVED_YELLOW_SCREEN')
    extras=set(times)-set(expected);need(len(extras)<=1,'EXTRA_UNBOUND_YELLOW_SCREEN')
    for q in records:
        t=q['time_s'];cs=[c for c in cycles if c['begin_s']<t<=c['begin_s']+c['max_green_s']];need(len(cs)==1,'YELLOW_CATALOGUE_CYCLE_BINDING');program=cs[0]['program'];need(q.get('screen_stage')=='PREPARED_BEFORE_FIRST_Y_MOTION' and q.get('source_program')==program and q.get('source_motion')=='y','YELLOW_SCREEN_SOURCE_PHASE')
        need(t<len(pre) and pre[t]['bound_snapshot']['time_s']==t and pre[t]['bound_snapshot']['motion']=='y' and pre[t]['bound_snapshot']['program']==program,'YELLOW_PREPARATION_PHASE_JOIN')
        if t in extras:
            need(runtime_stop is True and t==last and len(pre)==last+1,'EXTRA_YELLOW_NOT_BOUND_TO_ABORTED_PREPARED_PREFIX')
        yellow_record(q,cycles,post[t-1]['post_world'],pre[t]['bound_snapshot']['terminal_before'],last,diagnostic_contract)
    return {'observed_first_Y_count':len(expected),'validated_records':len(records),'prepared_not_observed_times':sorted(extras),'legacy_failed_witness_times':[q['time_s'] for q in records if q['status']=='UNKNOWN'],'binding_integrity':'PASS_IF_ALL_JOINS_PASS','future_native_safety_proven':False}

"""Independent audit compatibility for exact full-catalogue yellow durations.

No runtime safety predicate, model or phase configuration is changed.
"""
from scripts.cumulative_full_catalogue_audit_20261014_v1.core import need,near,number,catalogue

def yellow_record(yy,cycles,world,meta,last):
    t=yy['time_s'];need(type(t) is int and t==yy['source_post_frame_time_s'] and 1200<t<=last,'YELLOW_SOURCE_CLOCK')
    selected=[c for c in cycles if c['begin_s']<t<=c['begin_s']+c['max_green_s']];need(len(selected)==1,'YELLOW_CYCLE_BINDING')
    c=selected[0];P=catalogue(c['period_s']);Y=P['yellow_s']
    need(type(c['yellow_s']) is int and c['yellow_s']==Y and c['max_green_s']==P['max_green_s'],'YELLOW_CATALOGUE_PARAMETERS')
    need(type(yy['yellow_s']) is int and yy['yellow_s']==Y,'YELLOW_PERIOD')
    need(meta is not None,'MISSING_YELLOW_METADATA')
    need(len({q['vehicle_id'] for q in yy['rows']})==len(yy['rows']) and {q['vehicle_id'] for q in yy['rows']}==set(yy['covered_ids'])=={v for v,w in world.items() if w['lane_id'] in ('ramp_storage_0',':urban_diverge_1_0')},'YELLOW_LOCAL_COMPLETE')
    need(yy['status']=='PASS','UNKNOWN_LOCAL_YELLOW_SCOPE')
    for q in yy['rows']:
        vid=q['vehicle_id'];v=meta[vid];offset=113.08 if q['population']=='ingress' else 0
        need(q['time_s']==t and near(q['speed_m_s'],world[vid]['speed_m_s']) and q['native_future_safety_proven'] is False,'YELLOW_REAL_SPEED_ID')
        need(near(q['position_m'],v['position_m']-offset) and near(q['length_m'],v['length_m']) and near(q['normal_decel_m_s2'],v['normal_decel_m_s2']),'YELLOW_REAL_FIELDS')
        d=204.49-q['position_m'];speed=q['speed_m_s'];b=q['normal_decel_m_s2'];length=q['length_m'];dt=q['action_step_s']
        need(number(speed) and 0<=speed<=55.55555555555556 and number(d) and near(b,4.5) and near(length,5) and near(dt,1),'YELLOW_EFFECTIVE_MODEL_BOUND')
        one=d>0 and speed<=b*dt;stop=d>0 and (one or d>=speed*dt+speed*speed/(2*b));timing=None if speed==0 else dt+speed/(2*b)+length/speed;clear=speed>0 and timing<=Y and d+length<=speed*(Y-dt)
        need(q['one_step_Euler_stop_possible']==one and near(q['distance_to_meter_m'],d) and q['stop_possible']==stop and q['clear_possible']==clear,'YELLOW_INDEPENDENT_SCREEN')
        need(stop or clear,'UNKNOWN_LOCAL_YELLOW_SCOPE')
    return True

def yellow_coverage(records,phase,cycles,post,pre,last,runtime_stop):
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
        yellow_record(q,cycles,post[t-1]['post_world'],pre[t]['bound_snapshot']['terminal_before'],last)
    return {'observed_first_Y_count':len(expected),'validated_records':len(records),'prepared_not_observed_times':sorted(extras),'future_native_safety_proven':False}

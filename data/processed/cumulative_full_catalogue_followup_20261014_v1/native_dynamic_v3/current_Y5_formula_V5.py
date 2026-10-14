"""Only current T24/Y5 frozen snapshot compatibility; no future safety proof."""
from scripts.cumulative_full_catalogue_audit_20261014_v1.core import need,near,number
CHECKED=[]
def current_yellow_record(yy,cycles,world,meta,last):
    t=yy['time_s'];need(type(t) is int and t==yy['source_post_frame_time_s'] and 1200<t<=last,'YELLOW_SOURCE_CLOCK')
    selected=[c for c in cycles if c['begin_s']<t<=c['begin_s']+c['max_green_s']];need(len(selected)==1,'YELLOW_CYCLE_BINDING')
    Y=selected[0]['yellow_s'];need(yy['yellow_s']==Y and Y in (2,3,5) and (Y!=5 or selected[0]['period_s']==24),'YELLOW_PERIOD')
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
    CHECKED.append({'time_s':t,'period_s':selected[0]['period_s'],'Y_s':Y,'rows':len(yy['rows']),'status':'PASS_EXISTING_STATE_LOCAL_FORMULAS_NOT_FUTURE_SAFETY','stop_paths':sum(q['stop_possible'] for q in yy['rows']),'clear_paths':sum(q['clear_possible'] for q in yy['rows'])})
    return True

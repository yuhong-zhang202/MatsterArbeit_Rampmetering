"""Independent approved current-state floor and retained legacy-margin accounting.

Only current_following records use this policy. New-G prospective admission is
unchanged and must never be reclassified by this function.
"""
from scripts.cumulative_full_catalogue_audit_20261014_v1.core import need,near,number
POLICY='ACTUAL_CURRENT_NATIVE_GAP_FLOOR_LEGACY_MARGIN_ADVISORY_V1'
PATH=(':ramp_mid_0_0','ramp_accel_0',':freeway_merge_2_0','merge_section_0','merge_section_1','merge_section_2')

def following(q,vid,t,world,metadata,alarms,advisories):
    need(isinstance(q,dict) and q.get('vehicle_id')==vid and q.get('time_s')==t and vid in world,'CURRENT_QUERY_ID_TIME')
    need(q.get('speed_mode')==31 and q.get('lane_change_mode')==1621 and near(q.get('actual_speed_m_s'),world[vid]['speed_m_s']) and q.get('lane_id')==world[vid]['lane_id'],'CURRENT_QUERY_MODES_SPEED_LANE')
    need(q.get('route')==['urban_in','shared_approach','ramp_storage','ramp_accel','merge_section','main_down'] and q.get('lookahead_m')==478.67 and q.get('future_safety_proven') is False and q.get('margin_m')==1.1,'CURRENT_QUERY_SCOPE')
    need(q.get('policy')==POLICY and type(q.get('hard_margin_m')) in (int,float) and q['hard_margin_m']==0 and q.get('margin_role')=='ADVISORY_ONLY','APPROVED_POLICY_BOUNDING')
    geo=q.get('path_geometry_m');need(q.get('receiver_path_lanes')==list(PATH) and isinstance(geo,dict) and set(geo)==set(('ramp_storage_0',)+PATH) and all(number(x) and x>0 for x in geo.values()),'CURRENT_PATH_GEOMETRY')
    pos=q.get('lane_position_m');length=q.get('vehicle_length_m');lane=q['lane_id']
    need(lane in geo and number(pos) and 0<=pos<=geo[lane] and number(length) and length>0,'CURRENT_GEOMETRY_FIELDS')
    if vid in metadata:
        v=metadata[vid];need(near(pos,v['position_m']) and near(length,v['length_m']),'CURRENT_QUERY_POSITION_LENGTH')
    status=q.get('status');fresh=q.get('fresh_getLeader_result')
    if status=='CLEAR_WITHIN_OBSERVED_LOOKAHEAD':
        need(fresh is None or fresh==['',-1],'CLEAR_VALID_EMPTY_RESULT')
        need(all(k in q and q[k] is None for k in ('actual_secure_gap_m','gap_excluding_minGap_m','required_with_margin_m','required_hard_floor_m','hard_screen_pass','legacy_margin_pass')) and q.get('legacy_contract_status')==status and q.get('margin_classification')==status,'CLEAR_NOT_QUERY_PASS')
        return
    need(status in ('CURRENT_GAP_OBSERVED_WITHIN_BOUND','STOP_CURRENT_GAP_BOUND_DENIED'),'UNKNOWN_CURRENT_QUERY_STATUS')
    leader=q.get('leader_id');args=q.get('getSecureGap_args',{});gap=q.get('gap_excluding_minGap_m');secure=q.get('actual_secure_gap_m');mg=q.get('min_gap_m')
    need(leader!=vid and leader in world and isinstance(fresh,list) and fresh==[leader,gap] and all(number(x) and x>=0 for x in (gap,secure,mg)),'LEADER_FRESH_RESULT')
    need(q.get('leader_speed_mode')==31 and q.get('leader_lane_change_mode')==1621,'LEADER_EFFECTIVE_MODES')
    need(args.get('vehID')==vid and args.get('leaderID')==leader and near(args.get('speed'),world[vid]['speed_m_s']) and near(args.get('leaderSpeed'),world[leader]['speed_m_s']) and args.get('leaderMaxDecel')==9 and near(q.get('leader_speed_m_s'),world[leader]['speed_m_s']) and q.get('leader_lane_id')==world[leader]['lane_id'],'CURRENT_SECURE_QUERY_PRIMITIVES')
    need(near(q.get('physical_bumper_gap_m'),gap+mg) and near(q.get('required_with_margin_m'),secure+1.1) and near(q.get('required_hard_floor_m'),secure),'CURRENT_GAP_UNITS')
    hard=gap+mg>0 and gap+1e-9>=secure;legacy=gap+mg>0 and gap+1e-9>=secure+1.1
    classification='WITHIN_LEGACY_MARGIN' if legacy else 'EXTRA_MARGIN_ADVISORY' if hard else 'BELOW_NATIVE_QUERY_FLOOR'
    need(type(q.get('hard_screen_pass')) is bool and q['hard_screen_pass']==hard and type(q.get('legacy_margin_pass')) is bool and q['legacy_margin_pass']==legacy and q.get('margin_classification')==classification,'INDEPENDENT_MARGIN_CLASSIFICATION')
    need((status=='CURRENT_GAP_OBSERVED_WITHIN_BOUND')==hard and q.get('legacy_contract_status')==('CURRENT_GAP_OBSERVED_WITHIN_BOUND' if legacy else 'STOP_CURRENT_GAP_BOUND_DENIED'),'CURRENT_QUERY_CLASSIFICATION')
    record={'time_s':t,'vehicle_id':vid,'leader_id':leader,'gap_m':gap,'queried_secure_m':secure,'legacy_required_m':secure+1.1,'legacy_margin_pass':legacy,'hard_screen_pass':hard,'native_unsafe_proven':False}
    if not hard:alarms.append(dict(record,kind='CURRENT_NATIVE_QUERY_FLOOR_DENIED'))
    elif not legacy:advisories.append(dict(record,kind='EXTRA_MARGIN_ADVISORY_NOT_LEGACY_PASS'))

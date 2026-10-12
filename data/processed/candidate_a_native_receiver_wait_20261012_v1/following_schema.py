"""Independent serialized current-following/WAIT/entry evidence binding, not safety proof."""
import math

POLICY='ACTUAL_SPEED_FOLLOWING_OBSERVATION_WITH_RETAINED_1_1_M_MARGIN_V1'
ROUTE=['urban_in','shared_approach','ramp_storage','ramp_accel','merge_section','main_down']
LANES=[':ramp_mid_0_0','ramp_accel_0',':freeway_merge_2_0','merge_section_0','merge_section_1','merge_section_2']
class Unknown(ValueError):pass

def require(ok,why):
 if not ok:raise Unknown(why)
def finite(value):return type(value) in (int,float) and math.isfinite(value)
def near(a,b):return finite(a) and finite(b) and abs(a-b)<=1e-8

def following(q,vid,t,world):
 require(isinstance(q,dict) and q.get('vehicle_id')==vid and q.get('time_s')==t and vid in world,'FOLLOW_ID_TIME')
 require(q.get('policy')==POLICY and q.get('margin_m')==1.1 and q.get('future_safety_proven') is False,'POLICY_SCOPE')
 require(q.get('route')==ROUTE and q.get('receiver_path_lanes')==LANES and q.get('lookahead_m')==478.67,'ROUTE_LOOKAHEAD')
 require(q.get('lane_id')==world[vid]['lane_id'] and near(q.get('actual_speed_m_s'),world[vid]['speed_m_s']),'FOLLOW_WORLD_BINDING')
 require(q.get('speed_mode')==31 and q.get('lane_change_mode')==1621,'FOLLOW_MODES')
 geometry=q.get('path_geometry_m');require(isinstance(geometry,dict) and set(geometry)==set(['ramp_storage_0']+LANES) and all(finite(v) and v>0 for v in geometry.values()),'PATH_GEOMETRY')
 require(q['lane_id'] in geometry and finite(q.get('lane_position_m')) and 0<=q['lane_position_m']<=geometry[q['lane_id']],'POSITION_BINDING')
 require(finite(q.get('vehicle_length_m')) and q['vehicle_length_m']>0 and finite(q.get('min_gap_m')) and q['min_gap_m']>=0,'SIZE_MIN_GAP')
 raw=q.get('fresh_getLeader_result','MISSING')
 empty=raw is None or (isinstance(raw,(list,tuple)) and len(raw)==2 and raw[0]=='' and type(raw[1]) in (int,float) and raw[1]==-1)
 if empty:
  require(not any(k in q for k in ['leader_id','leader_lane_id','leader_speed_m_s','getSecureGap_args','physical_bumper_gap_m','required_with_margin_m']), 'CLEAR_CONTRADICTORY_LEADER_FIELDS')
  require(q.get('status')=='CLEAR_WITHIN_OBSERVED_LOOKAHEAD' and q.get('actual_secure_gap_m') is None and q.get('gap_excluding_minGap_m') is None,'CLEAR_BINDING')
  require('not globally clear' in q.get('claim_scope',''),'CLEAR_SCOPE')
  return 'CLEAR'
 require(isinstance(raw,(list,tuple)) and len(raw)==2 and raw[0] in world and raw[0]!=vid and finite(raw[1]) and raw[1]>=0,'LEADER_SCHEMA')
 leader=raw[0];require(q.get('leader_id')==leader and q.get('leader_lane_id')==world[leader]['lane_id'] and q['leader_lane_id'] in ['ramp_storage_0']+LANES,'LEADER_WORLD_BINDING')
 require(near(q.get('leader_speed_m_s'),world[leader]['speed_m_s']) and q.get('leader_speed_mode')==31 and q.get('leader_lane_change_mode')==1621,'LEADER_SPEED_MODES')
 require(q.get('getSecureGap_args')=={'vehID':vid,'speed':q['actual_speed_m_s'],'leaderSpeed':q['leader_speed_m_s'],'leaderMaxDecel':9.0,'leaderID':leader},'ACTUAL_QUERY_ARGS')
 require(near(q.get('gap_excluding_minGap_m'),raw[1]) and finite(q.get('actual_secure_gap_m')) and q['actual_secure_gap_m']>=0,'QUERY_RESULT')
 require(near(q.get('physical_bumper_gap_m'),raw[1]+q['min_gap_m']) and near(q.get('required_with_margin_m'),q['actual_secure_gap_m']+1.1),'GAP_ARITHMETIC')
 passed=q['physical_bumper_gap_m']>0 and raw[1]+1e-9>=q['actual_secure_gap_m']+1.1
 require(q.get('status')==('CURRENT_GAP_OBSERVED_WITHIN_BOUND' if passed else 'STOP_CURRENT_GAP_BOUND_DENIED'),'GAP_STATUS')
 return 'CURRENT_GAP_PASS' if passed else 'CURRENT_GAP_STOP'

def receiver(decision,old,t,world):
 require(isinstance(decision,dict) and type(old.get('available')) is bool and decision.get('time_s')==t and decision.get('prospective_available') is old['available'],'RECEIVER_BOOL_TIME')
 require(decision.get('policy')==POLICY and decision.get('future_safety_proven') is False,'RECEIVER_POLICY')
 if old['available']:
  require(decision.get('decision')=='READY','READY_NOT_REWRITTEN');return 'READY'
 require(decision.get('original_prospective_receiver')==old,'PROSPECTIVE_DENIAL_PRESERVED')
 q=decision.get('current_following');result=following(q,old.get('front_id'),t,world)
 require(isinstance(old.get('leader'),dict) and q.get('leader_id')==old['leader'].get('vehicle_id') and near(q.get('gap_excluding_minGap_m'),old['leader'].get('gap_excluding_minGap_m')),'OLD_NEW_LEADER_BINDING')
 require(result!='CLEAR','DENIAL_CANNOT_BECOME_CLEAR')
 require(decision.get('decision')==('WAIT_NATIVE_FOLLOWING' if result=='CURRENT_GAP_PASS' else 'STOP_CURRENT_GAP_BOUND_DENIED'),'WAIT_DISPATCH')
 return decision['decision']

def step(pre,post):
 t=post['time_begin_s'];p=pre['bound_snapshot'];require(pre['time_s']==p['time_s']==t,'STEP_TIME')
 states=[]
 if p['motion']=='G':
  states.append(receiver(p.get('native_receiver_decision'),p['receiver'],t,p['world']))
  states.append(receiver(post.get('post_native_receiver_decision'),post['post_receiver'],t+1,post['post_world']))
 else:require(p.get('native_receiver_decision') is None,'NON_GREEN_DECISION')
 entries=post.get('actual_entry_following');crossed=post['actual_crossings']
 require(isinstance(entries,list) and len(entries)==len(crossed) and len({r.get('vehicle_id') for r in entries})==len(entries),'ENTRY_COVERAGE')
 require({r['vehicle_id'] for r in entries}=={r['vehicle_id'] for r in crossed},'ENTRY_ID_BINDING')
 for r in entries:
  vid=r['vehicle_id'];require(r.get('time_begin_s')==t and r.get('time_end_s')==t+1 and r.get('motion')==p['motion'],'ENTRY_TIME_MOTION')
  require(r.get('before')==p.get('entry_following_before',{}).get(vid),'ENTRY_BEFORE_SNAPSHOT')
  states.append(following(r.get('before'),vid,t,p['world']))
  states.append(following(r.get('after'),vid,t+1,post['post_world']))
 return states

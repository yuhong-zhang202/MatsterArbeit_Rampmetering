"""Bounded offline support for the aborted first-Y attempt, not a new screen."""
from pathlib import Path
import json,math
ROOT=Path(__file__).resolve().parents[4];OUT=Path(__file__).resolve().parent
RAW=ROOT/'data/raw/dynamic_minimum_qualification_20261015_v1/UA_NATIVEGAP_DYNAMIC_S17_01/outputs'
def lastrow(name):
 with (RAW/name).open() as f:
  result=None
  for line in f:
   if line.strip():result=json.loads(line)
 return result
attempt=lastrow('yellow_scope_attempts.jsonl');post=lastrow('post_steps.jsonl');pre=lastrow('pre_steps.jsonl');ids=lastrow('identity_journal.jsonl');world=post['post_world'];meta=ids['vehicle_states'];t=attempt['time_s']
assert t==1236==post['time_end_s']==ids['time_s'] and pre['time_s']==1235
local={v for v,w in world.items() if w['lane_id'] in ('ramp_storage_0',':urban_diverge_1_0')}
assert set(attempt['covered_ids'])==local=={r['vehicle_id'] for r in attempt['rows']} and len(attempt['rows'])==len(local)
failed=[]
for q in attempt['rows']:
 v=q['vehicle_id'];m=meta[v];speed=q['speed_m_s'];b=q['normal_decel_m_s2'];d=204.49-q['position_m'];dt=q['action_step_s'];length=q['length_m'];Y=attempt['yellow_s']
 assert q['time_s']==t and speed==world[v]['speed_m_s'] and b==m['normal_decel_m_s2']==4.5 and dt==m['action_step_s']==1 and length==5
 assert all(math.isfinite(x) for x in (speed,b,d,dt,length))
 one=d>0 and speed<=b*dt;stop=d>0 and (one or d>=speed*dt+speed*speed/(2*b));timing=None if speed==0 else dt+speed/(2*b)+length/speed;clear=speed>0 and timing<=Y and d+length<=speed*(Y-dt)
 assert abs(d-q['distance_to_meter_m'])<1e-9 and q['one_step_Euler_stop_possible']==one and q['stop_possible']==stop and q['clear_possible']==clear
 if not stop and not clear:failed.append(dict(q,recomputed_stop_distance_m=speed*dt+speed*speed/(2*b),recomputed_body_clear_time_s=timing))
assert len(failed)==1 and failed[0]['vehicle_id']=='R_flow.5'
q=failed[0];before=pre['bound_snapshot']['terminal_before']['R_flow.5'];assert before['lane_id']==world['R_flow.5']['lane_id']=='ramp_storage_0' and abs(q['position_m']-(before['position_m']+q['speed_m_s']))<1e-9
result={'status':'PASS_BOUND_ABORTED_ATTEMPT_SUPPORT_NOT_NATIVE_YELLOW_SAFETY','attempt_s':t,'population_count':len(local),'full_ID_speed_model_formula_coverage':True,'failed_rows':failed,'R5_position_independently_bound_to_prior_position_plus_observed_Euler_step':True,'other_attempt_positions_scope':'serialized attempt position; no second full FCD pass performed','phase_in_last_completed_interval':post['motion'],'failed_attempt_observed_first_Y':attempt['observed_first_Y'],'first_Y_native_executed':False,'native_unsafe_proven':False}
assert post['motion']=='G' and attempt['observed_first_Y'] is False
with (OUT/'YELLOW_STOP_SUPPORT_V1.json').open('x') as f:json.dump(result,f,indent=2)
print(json.dumps({k:v for k,v in result.items() if k!='failed_rows'},indent=2))

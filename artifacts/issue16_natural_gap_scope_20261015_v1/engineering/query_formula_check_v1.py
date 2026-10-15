"""Fixed-source arithmetic on two saved frames; no simulator imports or queries."""
import json,math
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3]
SOURCE=ROOT/'data/processed/issue16_natural_gap_scope_20261015_v1/TERMINAL_FRAMES_V1.json'
r=json.loads(SOURCE.read_text())
q0=next(p for p in r['pre'] if p['time_s']==649)['entry_following_before']['R_flow.1']
q1=next(p for p in r['post'] if p['time_end_s']==650)['post_native_receiver_decision']['current_following']
def brake(v,b,tau):
 n=int(v/b)
 return n*v-b*n*(n+1)/2+v*tau
rows=[]
for q in (q0,q1):
 values=[]
 for decel in (9.,4.5):
  lead=brake(q['leader_speed_m_s'],max(4.5,decel),0)
  follower=brake(q['actual_speed_m_s'],4.5,1)
  secure=max(0,follower-lead)
  assert abs(secure-q['actual_secure_gap_m'])<1e-12
  values.append(dict(leaderMaxDecel_diagnostic=decel,leader_brake_gap_m=lead,secure_gap_m=secure,reference_minus_actual_gap_m=secure-q['gap_excluding_minGap_m']))
 rows.append(dict(time_s=q['time_s'],saved_actual_query=q['getSecureGap_args'],saved_native_query_result_m=q['actual_secure_gap_m'],conditional_Euler_formula=values))
print(json.dumps(dict(scope='SOURCE_FORMULA_REPRODUCTION_NOT_NATIVE_MOTION_REPLAY',dt_s=1,normal_decel_m_s2=4.5,tau_s=1,private_native_movement_call_not_recorded=True,rows=rows),indent=2))

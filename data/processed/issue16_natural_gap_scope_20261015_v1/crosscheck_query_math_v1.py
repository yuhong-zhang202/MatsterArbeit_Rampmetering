"""Pinned-source arithmetic only; not a native CF replay or alternative safety test."""
import json
from pathlib import Path
out=Path(__file__).parent;r=json.loads((out/'TERMINAL_FRAMES_V1.json').read_text());qs=[r['pre'][-1]['entry_following_before']['R_flow.1'],r['post'][-1]['post_native_receiver_decision']['current_following']]
def bg(v,b,tau):
 n=int(v/b)
 return n*v-b*n*(n+1)/2+v*tau
rows=[]
for q in qs:
 v=q['actual_speed_m_s'];vl=q['leader_speed_m_s'];gap=q['gap_excluding_minGap_m'];b=4.5
 a=[]
 for leader_b in (9.,4.5):
  leader_brake=bg(vl,max(b,leader_b),0);follower_brake=bg(v,b,1);secure=max(0,follower_brake-leader_brake)
  assert abs(secure-q['actual_secure_gap_m'])<1e-12
  a.append({'diagnostic_leaderMaxDecel':leader_b,'leader_brake_gap_m':leader_brake,'follower_brake_gap_m':follower_brake,'computed_secure_gap_m':secure,'still_below_query':gap<secure})
 rows.append({'time_s':q['time_s'],'actual_query_result_m':q['actual_secure_gap_m'],'source_formula':'MSCFModel.cpp92..98 Euler dt1; base getSecureGap168..184','arithmetic':a})
result={'scope':'PINNED_SOURCE_FORMULA_CONDITIONAL_EULER_NOT_NATIVE_REPLAY','native_motion_private_branch_recorded':False,'finding':'Changing leaderMaxDecel9 to4.5 cannot remove these recorded deficits under this source formula; neither proposal nor parameter modification','rows':rows}
(out/'QUERY_MATH_CROSSCHECK_V1.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result))

"""Two tiny serialized-evidence regression methods; no execution-code reruns."""
from copy import deepcopy
import unittest
from following_schema import following,receiver,Unknown,POLICY,ROUTE,LANES
WORLD={'R_flow.0':{'lane_id':':ramp_mid_0_0','speed_m_s':1.3},'R_flow.1':{'lane_id':'ramp_storage_0','speed_m_s':0.}}
def query():
 return {'vehicle_id':'R_flow.1','time_s':1201,'policy':POLICY,'margin_m':1.1,'future_safety_proven':False,'route':ROUTE,'receiver_path_lanes':LANES,'lookahead_m':478.67,'lane_id':'ramp_storage_0','actual_speed_m_s':0.,'speed_mode':31,'lane_change_mode':1621,'path_geometry_m':{l:100. for l in ['ramp_storage_0']+LANES},'lane_position_m':90.,'vehicle_length_m':5.,'min_gap_m':2.5,'fresh_getLeader_result':['R_flow.0',1.316],'leader_id':'R_flow.0','leader_lane_id':':ramp_mid_0_0','leader_speed_m_s':1.3,'leader_speed_mode':31,'leader_lane_change_mode':1621,'getSecureGap_args':{'vehID':'R_flow.1','speed':0.,'leaderSpeed':1.3,'leaderMaxDecel':9.,'leaderID':'R_flow.0'},'actual_secure_gap_m':0.,'gap_excluding_minGap_m':1.316,'physical_bumper_gap_m':3.816,'required_with_margin_m':1.1,'status':'CURRENT_GAP_OBSERVED_WITHIN_BOUND'}
class BindingTests(unittest.TestCase):
 def test_actual_query_binding_denial_wait_and_unknown(self):
  q=query();old={'available':False,'front_id':'R_flow.1','leader':{'vehicle_id':'R_flow.0','gap_excluding_minGap_m':1.316,'secure_gap_m':2.6}};d={'decision':'WAIT_NATIVE_FOLLOWING','prospective_available':False,'original_prospective_receiver':deepcopy(old),'current_following':q,'time_s':1201,'policy':POLICY,'future_safety_proven':False}
  self.assertEqual(receiver(d,old,1201,WORLD),'WAIT_NATIVE_FOLLOWING')
  for key,value in [('speed',2.6),('leaderID','R_flow.1')]:
   changed=deepcopy(q);changed['getSecureGap_args'][key]=value
   with self.subTest(key=key),self.assertRaises(Unknown):following(changed,'R_flow.1',1201,WORLD)
  denied=deepcopy(q);denied.update(actual_secure_gap_m=2.6,required_with_margin_m=3.7,status='STOP_CURRENT_GAP_BOUND_DENIED');self.assertEqual(following(denied,'R_flow.1',1201,WORLD),'CURRENT_GAP_STOP')
  bad=deepcopy(d);bad['prospective_available']=True
  with self.assertRaises(Unknown):receiver(bad,old,1201,WORLD)
 def test_valid_fresh_clear_cannot_hide_missing_or_contradictory_leader(self):
  q=query();q.update(fresh_getLeader_result=None,status='CLEAR_WITHIN_OBSERVED_LOOKAHEAD',actual_secure_gap_m=None,gap_excluding_minGap_m=None,claim_scope='fresh bounded; not globally clear')
  self.assertEqual(following(q,'R_flow.1',1201,WORLD),'CLEAR')
  for fault in ['missing','bad_empty','wrong_time']:
   changed=deepcopy(q)
   if fault=='missing':changed.pop('fresh_getLeader_result')
   elif fault=='bad_empty':changed['fresh_getLeader_result']=['',0]
   else:changed['time_s']=1200
   with self.subTest(fault=fault),self.assertRaises(Unknown):following(changed,'R_flow.1',1201,WORLD)
if __name__=='__main__':unittest.main()

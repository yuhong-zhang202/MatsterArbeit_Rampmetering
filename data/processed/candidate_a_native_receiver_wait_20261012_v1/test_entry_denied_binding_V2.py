"""Minimal exact before-denied/after-pass terminal-evidence composition regression."""
from copy import deepcopy
import unittest
from following_schema_V2 import step,Unknown,POLICY
from test_following_schema_V3 import query,WORLD

def pair():
 before=query();after=deepcopy(before);after.update(time_s=1202,lane_id=':ramp_mid_0_0',lane_position_m=.3,actual_speed_m_s=1.31);after['getSecureGap_args']['speed']=1.31
 world=deepcopy(WORLD);world['R_flow.1']={'lane_id':':ramp_mid_0_0','speed_m_s':1.31}
 ready=lambda t:{'decision':'READY','prospective_available':True,'time_s':t,'policy':POLICY,'future_safety_proven':False}
 pre={'time_s':1201,'bound_snapshot':{'time_s':1201,'motion':'G','world':WORLD,'receiver':{'available':True},'native_receiver_decision':ready(1201),'entry_following_before':{'R_flow.1':before}}}
 post={'time_begin_s':1201,'post_world':world,'post_receiver':{'available':True},'post_native_receiver_decision':ready(1202),'status':'RECONCILED_DIAGNOSTIC_ONLY','actual_crossings':[{'vehicle_id':'R_flow.1'}],'actual_entry_following':[{'vehicle_id':'R_flow.1','time_begin_s':1201,'time_end_s':1202,'motion':'G','before':before,'after':after}]}
 return pre,post
class EntryStopTests(unittest.TestCase):
 def test_both_sides_denied_need_terminal_binding_and_unknown_is_not_PASS(self):
  pre,post=pair();self.assertEqual(step(pre,post),['READY','READY','CURRENT_GAP_PASS','CURRENT_GAP_PASS'])
  for side in ['BEFORE','AFTER']:
   p,r=pair();q=r['actual_entry_following'][0][side.lower()];q.update(actual_secure_gap_m=4.,required_with_margin_m=5.1,status='STOP_CURRENT_GAP_BOUND_DENIED')
   with self.subTest(side=side),self.assertRaises(Unknown):step(p,r)
   r.update(status='STOP_OBSERVED_AFTER_STEP',reasons=['ACTUAL_ENTRY_'+side+'_CURRENT_GAP_BOUND_DENIED:R_flow.1'])
   self.assertIn('CURRENT_GAP_STOP',step(p,r))
   r['reasons']=['UNRELATED_STOP']
   with self.assertRaises(Unknown):step(p,r)
  for fault in ['unknown','missing_after','wrong_speed']:
   p,r=pair();q=r['actual_entry_following'][0]['before']
   if fault=='unknown':q['status']='UNKNOWN'
   elif fault=='missing_after':r['actual_entry_following'][0]['after']=None
   else:q['getSecureGap_args']['speed']=2.6
   with self.subTest(fault=fault),self.assertRaises(Unknown):step(p,r)
if __name__=='__main__':unittest.main()

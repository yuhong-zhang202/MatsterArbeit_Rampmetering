"""Small independent policy/measurement checks. All generated rows are synthetic."""
import copy,importlib.util,json,pathlib,unittest
from scripts.dynamic_minimum_qualification_audit_20261015_v1.current_gap import following,POLICY,PATH
from scripts.dynamic_minimum_qualification_audit_20261015_v1.scope import resource_alarms,terminal_scope,PARTIAL
from scripts.dynamic_minimum_qualification_audit_20261015_v1.tracking import tracking_review
from scripts.cumulative_full_catalogue_audit_20261014_v1 import core
ROOT=pathlib.Path(__file__).resolve().parents[2]
def sample(gap):
 world={'R_flow.5':{'speed_m_s':1.,'lane_id':'ramp_storage_0'},'R_flow.4':{'speed_m_s':2.,'lane_id':PATH[0]}}
 q=dict(vehicle_id='R_flow.5',time_s=1233,speed_mode=31,lane_change_mode=1621,actual_speed_m_s=1.,lane_id='ramp_storage_0',route=['urban_in','shared_approach','ramp_storage','ramp_accel','merge_section','main_down'],lookahead_m=478.67,future_safety_proven=False,margin_m=1.1,hard_margin_m=0.,margin_role='ADVISORY_ONLY',policy=POLICY,receiver_path_lanes=list(PATH),path_geometry_m={p:300. for p in ('ramp_storage_0',)+PATH},lane_position_m=195.,vehicle_length_m=5.,leader_id='R_flow.4',leader_lane_id=PATH[0],leader_speed_m_s=2.,leader_speed_mode=31,leader_lane_change_mode=1621,getSecureGap_args=dict(vehID='R_flow.5',leaderID='R_flow.4',speed=1.,leaderSpeed=2.,leaderMaxDecel=9),fresh_getLeader_result=['R_flow.4',gap],gap_excluding_minGap_m=gap,actual_secure_gap_m=1.,min_gap_m=2.5,physical_bumper_gap_m=gap+2.5,required_with_margin_m=2.1,required_hard_floor_m=1.)
 hard=gap+1e-9>=1;legacy=gap+1e-9>=2.1
 q.update(hard_screen_pass=hard,legacy_margin_pass=legacy,status='CURRENT_GAP_OBSERVED_WITHIN_BOUND' if hard else 'STOP_CURRENT_GAP_BOUND_DENIED',legacy_contract_status='CURRENT_GAP_OBSERVED_WITHIN_BOUND' if legacy else 'STOP_CURRENT_GAP_BOUND_DENIED',margin_classification='WITHIN_LEGACY_MARGIN' if legacy else 'EXTRA_MARGIN_ADVISORY' if hard else 'BELOW_NATIVE_QUERY_FLOOR')
 return q,world
class Tests(unittest.TestCase):
 def test_native_floor_legacy_warning_joint_binding_and_unknown(self):
  for gap,na,nw in [(2.2,0,0),(2.09,0,1),(.99,1,0)]:
   q,w=sample(gap);a=[];v=[];following(q,'R_flow.5',1233,w,{},a,v);self.assertEqual((len(a),len(v)),(na,nw))
  q,w=sample(2.09)
  for key,value in [('time_s',1232),('speed_mode',0),('hard_screen_pass',False),('leader_id','R_flow.999'),('required_hard_floor_m',0),('policy','LEGACY'),('legacy_margin_pass',True)]:
   bad=copy.deepcopy(q);bad[key]=value
   with self.subTest(key=key),self.assertRaises(ValueError):following(bad,'R_flow.5',1233,w,{},[],[])
  bad=copy.deepcopy(q);del bad['hard_screen_pass']
  with self.assertRaises(ValueError):following(bad,'R_flow.5',1233,w,{},[],[])
  q.update(status='CLEAR_WITHIN_OBSERVED_LOOKAHEAD',fresh_getLeader_result=None,actual_secure_gap_m=None,gap_excluding_minGap_m=None,required_with_margin_m=None,required_hard_floor_m=None,hard_screen_pass=None,legacy_margin_pass=None,legacy_contract_status='CLEAR_WITHIN_OBSERVED_LOOKAHEAD',margin_classification='CLEAR_WITHIN_OBSERVED_LOOKAHEAD')
  a=[];v=[];following(q,'R_flow.5',1233,w,{},a,v);self.assertEqual((a,v),([],[]))
  q['hard_screen_pass']=True
  with self.assertRaises(ValueError):following(q,'R_flow.5',1233,w,{},[],[])
 def test_synthetic_original_requests_decomposition_recovery_and_partial(self):
  spec=importlib.util.spec_from_file_location('independent_fixture_loader',ROOT/'tests/cumulative_full_catalogue_audit_20261014/test_audit.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
  m.BASE=ROOT/'artifacts/cumulative_full_catalogue_followup_20261014_v1/engineering/revision01/synthetic_fixture'
  f=m.load('dynamic_commands');account,phase=m.run(f,1296)
  out=tracking_review(account,f['events'],'dynamic_commands',True,{})
  self.assertEqual(out['status'],'FINITE_DIAGNOSTIC_TRACKING_DEMONSTRATED');self.assertEqual(out['whole_requested_fraction'],'311/24');self.assertEqual(out['whole_actual_N'],14)
  self.assertEqual(out['final_300_recovery']['status'],'RECOVERY_OBSERVED');self.assertFalse(out['qualification'])
  self.assertFalse(out['per_cycle'][-1]['completed']);self.assertEqual(out['per_cycle'][-1]['E_packet'],0)
  self.assertEqual(tracking_review(account,f['events'],'dynamic_commands',False,{})['status'],'NOT_DEMONSTRATED')
  no=core.audit_accounting([],[],[],1296);self.assertIsNone(tracking_review(no,[],'dynamic_commands',True,{})['whole_requested_minus_actual'])
  f=m.load('real_alinea');account,phase=m.run(f,1296);feedback=core.audit_feedback(f['feedback'],f['events'],account,1296)
  self.assertEqual(tracking_review(account,f['events'],'real_alinea',True,feedback)['status'],'FINITE_DIAGNOSTIC_TRACKING_DEMONSTRATED')
  self.assertEqual(tracking_review(account,f['events'],'real_alinea',True,{})['status'],'NOT_DEMONSTRATED')
 def test_budget_layers_partial_zero_and_unobserved(self):
  c={'resources':{'wall_limit_s':300},'spec':{'combined_resource_envelope':{'monitored_s':600}}}
  self.assertEqual(resource_alarms(c,180,180,1),[]);self.assertTrue(resource_alarms(c,301,0,1));self.assertTrue(resource_alarms(c,180,421,1))
  q=terminal_scope({'status':PARTIAL,'error':''},1296,1296,{'observed_end_s':1296,'planned_end_observed':True,'cycles':[dict(begin_s=1290,completed=False,N=0,E=0)]},set())
  self.assertIsNone(q['outside_observed_window_N']);self.assertTrue(q['partial_cycle']);self.assertFalse(q['runtime_stop'])
  with self.assertRaises(ValueError):terminal_scope({'status':PARTIAL,'error':''},1295,1296,{'cycles':[]},set())
if __name__=='__main__':unittest.main()

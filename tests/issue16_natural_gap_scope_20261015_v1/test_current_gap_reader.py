"""Independent saved-query and saved-loop inspection; never starts traffic."""
import json,sys,unittest,tempfile
from pathlib import Path
from copy import deepcopy
from fractions import Fraction
sys.dont_write_bytecode=True
from scripts.natural_actuator_qualification_20261015_v1 import provenance,streaming
from scripts.natural_service_audit_20261015_v1.actual import check_accounting
ROOT=Path(__file__).resolve().parents[2]
BASE=ROOT/'artifacts/issue16_natural_gap_scope_20261015_v1/engineering/implementation_v1/attempt1_fixtures'
CONTRACT=dict(enabled=True,policy=provenance.CURRENT_GAP_CONTRACT)
class CurrentGapReaderTests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.recorded=json.loads((BASE/'recorded_queries.json').read_text())
  cls.native=json.loads((ROOT/'data/processed/issue16_natural_gap_scope_20261015_v1/TERMINAL_FRAMES_V1.json').read_text())
 def query_check(self,q,role='ENTRY_BEFORE',contract=CONTRACT,alarms=None):
  n=self.native; t=q['time_s']; pre=n['pre'][-1];post=n['post'][-1];meta=pre['vehicles'];world={v:dict(speed_m_s=meta[v]['speed_m_s'],lane_id=meta[v]['lane_id']) for v in meta} if t==649 else post['speeds']
  # Preserve prebody lengths, with actual postFCD position for ACK650.
  fc=None if t==649 else n['FCD'][-1]['vehicles'];body=meta;checks=meta if t==649 else {};a=[] if alarms is None else alarms;observations=[]
  streaming.following_observation(q,q['vehicle_id'],t,world,checks,role,contract,a,[],observations,fc,body)
  return a,observations
 def test_approved_version_and_original_query_roles(self):
  originals=[self.native['pre'][-1]['entry_following_before']['R_flow.1'],self.native['post'][-1]['post_native_receiver_decision']['current_following']]
  for new,old in zip(self.recorded['queries'],originals):
   self.assertEqual({k:v for k,v in new.items() if k not in ('passive_leader_geometry','ordinary_current_gap_observation')},old)
  path='artifacts/issue16_natural_gap_scope_20261015_v1/HUMAN_CONTRACT_APPROVAL_RECEIPT_V1.json'
  item=dict(policy=provenance.CURRENT_GAP_CONTRACT,prospective_new_green='UNCHANGED_STRICT',ordinary_current_queries='OBSERVATIONAL_ONLY',approval_receipt=path,approval_sha256=provenance.sha(ROOT/path),native_safety_proven=False)
  self.assertTrue(provenance.current_gap_contract({'current_gap_responsibility_contract':item},ROOT)['enabled']);self.assertFalse(provenance.current_gap_contract({},ROOT)['enabled'])
  for field,value in [('policy','OTHER'),('prospective_new_green','RELAXED'),('approval_sha256','0'*64)]:
   bad=dict(item);bad[field]=value
   with self.assertRaises(ValueError):provenance.current_gap_contract({'current_gap_responsibility_contract':bad},ROOT)
  for original in self.recorded['queries']:
   for role in ('ONGOING_PRE_RECEIVER','POST_RECEIVER','ENTRY_BEFORE','ENTRY_AFTER'):
    q=deepcopy(original);q['ordinary_current_gap_observation']['role']=role;before=deepcopy(q);a,o=self.query_check(q,role)
    self.assertEqual(q,before);self.assertEqual(a,[]);self.assertEqual(o[0]['classification'],'BELOW_NATIVE_REFERENCE_OBSERVED');self.assertFalse(o[0]['native_safety_proven']);self.assertEqual(o[0]['legacy_alarm']['kind'],'CURRENT_NATIVE_QUERY_FLOOR_DENIED')
 def test_missing_negative_corrupt_queries_and_strict_new_green(self):
  original=self.recorded['queries'][0];cases=[]
  for field in ('ordinary_current_gap_observation','getSecureGap_args','passive_leader_geometry'):
   q=deepcopy(original);q.pop(field);cases.append(q)
  q=deepcopy(original);q['gap_excluding_minGap_m']=-1;cases.append(q)
  q=deepcopy(original);q['ordinary_current_gap_observation']['role']='POST_RECEIVER';cases.append(q)
  q=deepcopy(original);q['passive_leader_geometry']['position_m']+=1;cases.append(q)
  q=deepcopy(original);q['actual_secure_gap_m']=float('nan');cases.append(q)
  for q in cases:
   with self.assertRaises((ValueError,KeyError)):self.query_check(q)
  with self.assertRaises(ValueError):self.query_check(original,contract=dict(enabled=False))
  d=self.recorded['receiver'];receiver=d['original_prospective_receiver'];before=deepcopy(d)
  streaming.receiver_observation(d,receiver,650,'POST_RECEIVER',CONTRACT);self.assertEqual(d,before);self.assertFalse(receiver['available'])
  with self.assertRaises(ValueError):streaming.receiver_observation(d,receiver,650,'POST_RECEIVER',CONTRACT,new_green=True)
  for field,value in [('legacy_decision','WAIT_NATIVE_FOLLOWING'),('prospective_available',True)]:
   bad=deepcopy(d);bad[field]=value
   with self.assertRaises(ValueError):streaming.receiver_observation(bad,receiver,650,'POST_RECEIVER',CONTRACT)
  hazard=[dict(kind='colliding_vehicles',value=1)];a,o=self.query_check(deepcopy(original),alarms=hazard);self.assertEqual(a,hazard);self.assertEqual(len(o),1)
 def test_saved_normal_hold_recovery_accounting_and_hazards(self):
  r=json.loads((BASE/'loop_None.json').read_text());self.assertEqual(r['classification'],'SYNTHETIC_MOVEMENT_NO_NATIVE_SAFETY_EVIDENCE');self.assertIsNone(r['error'])
  C=S=A=Fraction(0);N=set();posts=r['logs']['post_steps.jsonl'];cycles=r['cycles'];snapshots=r['logs']['pre_steps.jsonl'];observations=[];alarms=[]
  for row in posts:
   t=row['time_begin_s']
   if t<600:continue
   p=snapshots[t]['bound_snapshot'];c=next(c for c in cycles if c['begin_s']<=t<c['end_s']);C+=Fraction(str(row['rate_chain']['r_final_veh_h']))/3600;S+=Fraction(str(c['selected_command_veh_h']))/3600;A+=Fraction(str(c['applied_command_veh_h'] or 0))/3600
   for x in row['actual_crossings']:self.assertNotIn(x['vehicle_id'],N);N.add(x['vehicle_id'])
   if p['motion']=='G':
    streaming.receiver_observation(p['native_receiver_decision'],p['receiver'],t,'ONGOING_PRE_RECEIVER',CONTRACT,new_green=t==c['begin_s'] and c['executed'])
    streaming.receiver_observation(row['post_native_receiver_decision'],row['post_receiver'],t+1,'POST_RECEIVER',CONTRACT)
   if p['motion'] in ('G','y'):
    self.assertEqual(set(p['entry_following_before']),set(p['storage']))
    for vid,q in p['entry_following_before'].items():streaming.following_observation(q,vid,t,p['world'],p['terminal_before'],'ENTRY_BEFORE',CONTRACT,alarms,[],observations)
   E=sum(2 for c in cycles if c['end_s']<=t+1);X=sum(2 for c in cycles if c['end_s']<=t+1 and c['executed']);partial=not any(c['end_s']==t+1 for c in cycles)
   check_accounting(row['accounting'],C,S,A,E,X,len(N),partial)
  self.assertEqual((C,S,A,E,X,len(N)),(Fraction(41,4),Fraction(41,4),Fraction(33,4),10,8,4));self.assertEqual(alarms,[])
  held=[c for c in cycles if not c['executed']];self.assertEqual([(c['begin_s'],c['end_s']) for c in held],[(608,616)]);self.assertTrue(next(c for c in cycles if c['begin_s']==616)['executed']);self.assertEqual(posts[-1]['accounting']['partial_cycle'],True)
  for row in posts[608:616]:
   self.assertEqual(row['motion'],'r');self.assertIsNone(row['rate_chain']['applied_request_id']);self.assertEqual(row['rate_chain']['r_policy_applied_veh_h'],0)
  self.assertEqual(posts[630]['rate_chain']['pending_request_id'],'feedback:630');self.assertEqual(posts[630]['rate_chain']['selected_request_id'],'real_alinea:600')
  self.assertEqual(posts[632]['rate_chain']['selected_request_id'],'feedback:630');self.assertIsNone(posts[632]['rate_chain']['applied_request_id']);self.assertEqual(posts[633]['rate_chain']['applied_request_id'],'feedback:630')
  for name,cause in [('loop_collision.json','COLLISION_OR_TELEPORT'),('loop_braking.json','UNKNOWN_OR_EXCESSIVE_ACCELERATION:M_flow.0'),('loop_badACK.json','POST_SIGNAL_APPLICATION_BINDING_MISMATCH')]:
   x=json.loads((BASE/name).read_text());row=x['logs']['post_steps.jsonl'][-1]['retained_receipts'][-1];self.assertEqual(x['error'],'DiagnosticStop:'+cause);self.assertEqual(row['terminal_reason'],x['error'])
   if 'badACK' in name:self.assertGreater(x['time_s'],x['last_accounted_s']);self.assertEqual(row['post_signal_application_binding']['status'],'STOP_UNBOUND_BEFORE_LEDGER')
   else:self.assertIn(cause,row['reasons'])
if __name__=='__main__':unittest.main(verbosity=2)

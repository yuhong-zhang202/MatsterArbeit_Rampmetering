"""Focused reader tests only; historical rows and synthetic first-Y routing."""
from pathlib import Path
import unittest,json,copy,ast
from scripts.dynamic_native_yellow_minqual_audit_20261015_v1.yellow import POLICY,yellow_record,yellow_coverage
from scripts.dynamic_native_yellow_minqual_audit_20261015_v1.scope import resource_alarms
ROOT=Path(__file__).resolve().parents[2];CONTRACT={'policy':POLICY,'enabled':True}
def fixture():
 yy=json.loads((ROOT/'data/processed/dynamic_native_yellow_minqual_20261015_v1/offline_v1/HISTORICAL_WITNESS_FIXTURE_V1.json').read_text())['scope']
 yy['source_post_frame_time_s']=1236;world={};meta={}
 for q in yy['rows']:
  vid=q['vehicle_id'];world[vid]={'speed_m_s':q['speed_m_s'],'lane_id':':urban_diverge_1_0' if q['population']=='ingress' else 'ramp_storage_0'};meta[vid]={'position_m':q['position_m']+(113.08 if q['population']=='ingress' else 0),'length_m':q['length_m'],'normal_decel_m_s2':q['normal_decel_m_s2']}
 yy['diagnostic_yellow_contract']={'policy':POLICY,'enabled':True,'original_witness_status':'UNKNOWN','witness_established':False,'failed_witness_ids':['R_flow.5'],'interpretation':'DIAGNOSTIC_WITNESS_NOT_ESTABLISHED','input_scope':'ORIGINAL_HARD_FRESH_FRAME_AND_POPULATION_JOINS_REQUIRED','allow_prepared_step':True,'future_native_safety_proven':False,'safety_certified':None}
 cycle={'begin_s':1232,'period_s':8,'max_green_s':4,'yellow_s':2,'program':'I12_PACKET8'}
 return yy,world,meta,cycle
class Tests(unittest.TestCase):
 def test_historical_false_witness_allowed_only_explicit_typed_contract(self):
  y,w,m,c=fixture();self.assertTrue(yellow_record(y,[c],w,m,1236,CONTRACT));self.assertEqual(y['status'],'UNKNOWN')
  for contract in (None,{'policy':POLICY,'enabled':False},{'policy':POLICY,'enabled':1},{'policy':POLICY,'enabled':1.0},{'policy':POLICY},{'policy':'foreign','enabled':True}):
   with self.subTest(contract=contract),self.assertRaises((ValueError,KeyError)):yellow_record(y,[c],w,m,1236,contract)
  for key,value in [('body_clear_time_screen_s',1.),('status','WITHIN_LOCAL_yellow_s_SCREEN'),('stop_possible',1),('time_s',1235)]:
   bad=copy.deepcopy(y);q=next(q for q in bad['rows'] if q['vehicle_id']=='R_flow.5');q[key]=value
   with self.subTest(key=key),self.assertRaises(ValueError):yellow_record(bad,[c],w,m,1236,CONTRACT)
  bad=copy.deepcopy(y);bad['status']='PASS'
  with self.assertRaises(ValueError):yellow_record(bad,[c],w,m,1236,CONTRACT)
  bad=copy.deepcopy(y);del bad['rows'][0]['body_clear_time_screen_s']
  with self.assertRaises(KeyError):yellow_record(bad,[c],w,m,1236,CONTRACT)
 def test_both_first_y_routes_missing_duplicate_and_unobserved_prepared(self):
  for G in (3,4):
   y,w,m,c=fixture();t=1232+G;y['time_s']=y['source_post_frame_time_s']=t
   for q in y['rows']:q['time_s']=t
   y.update(screen_stage='PREPARED_BEFORE_FIRST_Y_MOTION',source_program='I12_PACKET8',source_motion='y')
   seq='G'*G+'y';phase={'status':'PASS_CONTINUOUS_PHASES','cycles':[dict(c,observed_motion_sequence=seq,green_end_s=t)]}
   pre=[{} for _ in range(t+1)];post=[{} for _ in range(t+1)];pre[t]={'bound_snapshot':{'time_s':t,'motion':'y','program':'I12_PACKET8','terminal_before':m}};post[t-1]={'post_world':w}
   out=yellow_coverage([y],phase,[c],post,pre,t+1,False,CONTRACT);self.assertEqual(out['legacy_failed_witness_times'],[t]);self.assertEqual(out['observed_first_Y_count'],1)
   for bad in ([],[y,y]):
    with self.assertRaises(ValueError):yellow_coverage(bad,phase,[c],post,pre,t+1,False,CONTRACT)
   # Same prepared screen, no observed first-Y motion: only an aborted prefix may retain it.
   unobserved={'status':'PASS_CONTINUOUS_PHASES','cycles':[dict(c,observed_motion_sequence='G'*G,green_end_s=None)]}
   out=yellow_coverage([y],unobserved,[c],post,pre,t,True,CONTRACT);self.assertEqual(out['prepared_not_observed_times'],[t]);self.assertEqual(out['observed_first_Y_count'],0)
   with self.assertRaises(ValueError):yellow_coverage([y],unobserved,[c],post,pre,t,False,CONTRACT)
 def test_unchanged_other_stop_and_shared_nonzero_budget(self):
  old=ast.parse((ROOT/'scripts/dynamic_minimum_qualification_audit_20261015_v1/actual.py').read_text());new=ast.parse((ROOT/'scripts/dynamic_native_yellow_minqual_audit_20261015_v1/actual.py').read_text())
  # Original independent braking/counter/signal checks are not wrapped or removed by yellow continuation.
  select=lambda tree:[ast.dump(q) for q in ast.walk(tree) if isinstance(q,ast.If) and (('NORMAL_BRAKING_BOUND' in ast.unparse(q)) or ('NORMAL_ACCELERATION_BOUND' in ast.unparse(q)))]
  self.assertEqual(select(old),select(new));self.assertTrue(any(isinstance(q,ast.Call) and isinstance(q.func,ast.Name) and q.func.id=='strict_numeric' for q in ast.walk(new)))
  card={'resources':{'wall_limit_s':300},'spec':{'combined_resource_envelope':{'monitored_s':600}}}
  self.assertEqual(resource_alarms(card,180,163.07205774995964,403265825),[]);self.assertTrue(resource_alarms(card,301,163.07205774995964,1));self.assertTrue(resource_alarms(card,200,450,1))
if __name__=='__main__':unittest.main()

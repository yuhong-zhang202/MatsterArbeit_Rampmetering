"""Offline tests only: Python fixtures, no SUMO or live TraCI server."""
import ast,io,json,sys,unittest
from pathlib import Path
from unittest.mock import patch
BASE=Path(__file__).absolute().parents[1];sys.path.insert(0,str(BASE))
import runtime_executor as e,observer as o
FIX=BASE/'tests/fixtures_attempt2';FIX.mkdir()
class S:
 def __init__(self,physical=False):self.t=0;self.physical=physical
 def getTime(self):return self.t
 def getDeltaT(self):return 1
 def getCollidingVehiclesIDList(self):return ('R_flow.70',) if self.physical and self.t==3 else ()
 def getStartingTeleportIDList(self):return ()
 def getEndingTeleportIDList(self):return ()
 def getEmergencyStoppingVehiclesIDList(self):return ()
 def getDepartedIDList(self):return ()
 def getArrivedIDList(self):return ()
class C:
 def __init__(self,physical=False):self.simulation=S(physical)
 def simulationStep(self):self.simulation.t+=1
class Tests(unittest.TestCase):
 def test_exact_450_steps(self):
  c=C();out=io.StringIO()
  with patch.object(o,'snapshot',lambda c,label,b,a:{'kind':'fake_snapshot','label':label}):r=o.advance(c,out,FIX/'no_marker.json')
  rows=[json.loads(s) for s in out.getvalue().splitlines()]
  self.assertEqual(r['steps'],450);self.assertEqual(c.simulation.t,450)
  self.assertEqual([r['fcd_label_candidate'] for r in rows if r['kind']=='step'],list(range(450)))
  self.assertEqual([r['label'] for r in rows if r['kind']=='fake_snapshot'],[0,1,2]+list(range(385,431)))
 def test_collision_stops_without_next_step(self):
  c=C(True)
  with (FIX/'collision_stream.jsonl').open('x') as out,patch.object(o,'snapshot',lambda *a:{}):
   with self.assertRaisesRegex(RuntimeError,'physical_event_stop'):o.advance(c,out,FIX/'physical.json')
  self.assertEqual(c.simulation.t,3);self.assertTrue((FIX/'physical.json').exists())
 def test_only_readonly_api_and_clock(self):
  tree=ast.parse((BASE/'observer.py').read_text())
  names={n.func.attr for n in ast.walk(tree) if isinstance(n,ast.Call) and isinstance(n.func,ast.Attribute)}
  banned=[n for n in names if n.startswith(('set','change','move','add','remove','subscribe')) and n not in {'set','add_argument'}]
  self.assertEqual(banned,[]);self.assertNotIn('start',names)
  self.assertEqual(sum(isinstance(n,ast.Call) and isinstance(n.func,ast.Attribute) and n.func.attr=='Popen' for n in ast.walk(tree)),1)
 def test_both_branches_preserved(self):
  self.assertIn(':urban_diverge_0_0',o.REGION);self.assertIn(':urban_diverge_1_0',o.REGION)
  self.assertIn('shared_approach_0',o.REGION);self.assertIn('U_flow.35',o.TARGETS)
 def test_vehicle_leader_gap_and_tail(self):
  class V:
   def getLeader(self,*a):return ('R_flow.70',0.01)
   def getMinGap(self,*a):return 2.5
   def __getattr__(self,k):
    values={'getTypeID':'technical_passenger','getRoute':('urban_in','shared_approach','urban_out'),'getRouteIndex':1,'getLaneID':':urban_diverge_0_0','getLanePosition':1.52,'getPosition':(1001.82,644.31),'getAngle':2.48,'getSpeed':0.0,'getAcceleration':0.0,'getLength':5.0,'getNextTLS':(),'getNextLinks':(),'getJunctionFoes':()}
    return lambda *a:values[k]
  c=type('C',(),{'vehicle':V()})();r=o.observe_vehicle(c,'U_flow.35')
  self.assertEqual(r['leader_bumper_gap'],2.51);self.assertAlmostEqual(r['pos']-r['length'],-3.48)
 def test_no_leader_is_unknown_not_zero(self):
  class V:
   def getLeader(self,*a):return None
   def getMinGap(self,*a):return 2.5
   def __getattr__(self,k):return lambda *a:0
  r=o.observe_vehicle(type('C',(),{'vehicle':V()})(),'R_flow.70');self.assertIsNone(r['leader_bumper_gap'])
 def run_fake(self,name,code,**kw):
  run=FIX/name
  a={'attempt_id':name,'run_root':str(run),'argv':[sys.executable,'-B','-c',code]}
  return e._run(a,'fake_sha',{'synthetic':True},synthetic=True,timeout=1,cap=1000000,**kw)
 def test_fake_success(self):
  r=self.run_fake('python_success','print("retained")');self.assertEqual(r['status'],'process_completed_pending_gate')
 def test_fake_nonzero(self):
  r=self.run_fake('python_fail','import sys;sys.exit(9)');self.assertEqual(r['status'],'terminal_nonzero')
 def test_fake_timeout_and_claim(self):
  r=self.run_fake('python_timeout','import time;time.sleep(5)');self.assertEqual(r['status'],'terminal_timeout')
  with self.assertRaises(FileExistsError):self.run_fake('python_timeout','print("must not run")')
 def test_output_cap(self):
  r=self.run_fake('python_output','import time;time.sleep(5)',size_fn=lambda p:1000001)
  self.assertEqual(r['status'],'terminal_output_stop_line')
 def review(self,name,review,sha='fake_card'):
  p=FIX/(name+'.json');e.durable(p,review)
  card_path=FIX/(name+'_card.json');e.durable(card_path,{'test':True})
  auth=FIX/(name+'_auth.json');e.durable(auth,{'source':'fixture'})
  a={'status':'conditionally_authorized_released_after_exact_review','card_sha256':e.digest(card_path),'max_SUMO_starts':1,'scope':'single_C_seed17_end450_readonly_diagnostic','user_authorization_binding':e.binding(auth),'review_receipt':e.binding(p)}
  if review.get('card_sha256')=='correct':review['card_sha256']=e.digest(card_path);p.write_text(json.dumps(review));a['review_receipt']=e.binding(p)
  ap=FIX/(name+'_approval.json');e.durable(ap,a)
  return {'user_authorization_binding':e.binding(auth)},card_path,ap
 def test_old_review_rejected(self):
  with self.assertRaises(ValueError):e.validate_approval(*self.review('old',{'status':'PASS_STATIC_FINAL','stage':'design_only','card_sha256':'correct'}))
 def test_wrong_card_rejected(self):
  with self.assertRaises(ValueError):e.validate_approval(*self.review('wrong',{'status':'PASS_STATIC_FINAL','stage':'exact_o2_diagnostic_package','card_sha256':'wrong'}))
 def test_nonpass_rejected(self):
  with self.assertRaises(ValueError):e.validate_approval(*self.review('nonpass',{'status':'FAIL','stage':'exact_o2_diagnostic_package','card_sha256':'correct'}))
 def test_exact_review_accepted(self):
  e.validate_approval(*self.review('pass',{'status':'PASS_STATIC_FINAL','stage':'exact_o2_diagnostic_package','card_sha256':'correct'}))
if __name__=='__main__':
 r=unittest.TextTestRunner(verbosity=2).run(unittest.defaultTestLoader.loadTestsFromTestCase(Tests))
 e.durable(BASE/'offline_test_receipt_revision02.json',{'status':'PASS' if r.wasSuccessful() else 'FAIL','tests':r.testsRun,'failures':len(r.failures),'errors':len(r.errors),'executor_sha256':e.digest(BASE/'runtime_executor.py'),'observer_sha256':e.digest(BASE/'observer.py'),'test_sha256':e.digest(__file__),'real_SUMO_starts':0,'TraCI_connections':0,'netconvert':0,'GUI':0,'python_fake_processes':4,'fixture_history_preserved':str(FIX)})
 sys.exit(not r.wasSuccessful())

"""Focused real-helper/XML fake connection checks; not native vehicle proof."""
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch
import importlib.util,json,tempfile,time,unittest
from src.candidate_a_t10_g5_y3_20261013 import profile,bridge
from src.candidate_a_t10_g5_y3_20261013.policy import Ledger,Command,parameters
from src.candidate_a_t10_g5_y3_20261013.adapter import StepAdapter,inventory
from src.candidate_a_native_smoke_20261011.bridge_logs import LogCapture
from src.candidate_a_native_receiver_wait_20261012.receiver_wait import current_following
sp=importlib.util.spec_from_file_location('base_unified_fixture',profile.ROOT/'tests/candidate_a_unified_alinea_20261013/test_unified.py')
f=importlib.util.module_from_spec(sp);sp.loader.exec_module(f)

class World(f.UnifiedWorld):
 def __init__(self,xml,early=True,unknown=False):
  super().__init__(xml);self.early=early;self.unknown=unknown
 def simulationStep(self,end):
  f.fixture.old.fixture.old.fixture.XMLFakeConnection.simulationStep(self,end);self.arrived=[]
  if end==1201:self.enter['R_flow.0']=end
  if end==(1204 if self.early else 1205) and not(self.unknown and not self.early):self.enter['R_flow.1']=end
  if self.unknown and end==(1204 if self.early else 1205):self.vspeed['R_flow.2']=16.

class CandidateTests(unittest.TestCase):
 def run_loop(self,tmp,early=True,unknown=False):
  pkg=Path(tmp)/'pkg';out=Path(tmp)/'out';profile.stage_package(profile.ROOT,pkg,out,1210);out.mkdir()
  w=World(pkg/'scenario.add.xml',early,unknown);w.program='T10_G5Y3_NATIVE';w.phase=0;w.state='G';w.switch=5
  a=StepAdapter(w.observe,750,1210)
  cap=LogCapture(out);worker=bridge.protected_worker()
  try:bridge._diagnostic_loop(w,SimpleNamespace(observe=w.observe,request_phase=worker.request_phase),cap,out,
   dict(wall_limit_s=300,minimum_free_bytes=0,run_limit_bytes=300000000),f.fixture.old.fixture.old.fixture.fixture.FakeProcess(),time.monotonic(),a)
  finally:cap.close_handles()
  return w,a,out

 def test_real_helper_both_clock_paths_dynamic_red_and_uncapped_accounting(self):
  for early in (True,False):
   with self.subTest(early=early),tempfile.TemporaryDirectory() as tmp:
    w,a,out=self.run_loop(tmp,early)
    self.assertEqual(w.time,1210);self.assertEqual((a.ledger.E,a.ledger.N),(2,2))
    self.assertEqual(w.requests[:2],[(0,'setProgram','A_OPEN'),(0,'setPhase',0)])
    self.assertFalse(any(x[1]=='setProgram' and x[2]=='T10_G5Y3_NATIVE' for x in w.requests if x[0]<1200))
    self.assertEqual(a.ledger.rows[0]['phase_exposure_s'],{'G':4 if early else 5,'y':3,'r':3 if early else 2})
    self.assertTrue(a.checkpoint_verified);self.assertEqual(a.first_controlled_red_begin,1207 if early else 1208)
    chk=json.loads((out/'first_red_checkpoint.json').read_text());self.assertEqual(chk['time_s'],1208 if early else 1209)
    self.assertEqual((w.phase,w.state,w.switch),(2,'r',1210))
    self.assertFalse(a.body.active)
    with self.assertRaisesRegex(ValueError,'unsupported phase request'):
     bridge.protected_worker().request_phase(w.trafficlight,[],1210,'setPhaseDuration',2)
    self.assertTrue((out/'policy_duration_requests.jsonl').is_file())
  l=Ledger();self.assertTrue(all(x is None for x in l.accounting().values()))
  l.begin_step(1200);l.mark_cycle_start(True);l.end_step(1201,[],'G');self.assertEqual((l.E,l.N),(0,0))
  l.begin_step(1201);l.end_step(1202,['a','b','extra'],'G');l.close_green(1202,'ACTUAL_QUOTA_ACK')
  for t in range(1202,1210):
   l.begin_step(t);l.end_step(t+1,['yellow_extra'] if t==1202 else [],l.motion_at(t))
  self.assertEqual((l.E,l.N),(2,4))
  for bad in (8,24,True):
   with self.assertRaises(ValueError):parameters(bad)
  for bad in (300,900,True):
   with self.assertRaises(ValueError):Ledger(bad)

 def test_Y3_unknown_stops_both_paths_before_first_yellow_motion(self):
  for early in (True,False):
   with self.subTest(early=early),tempfile.TemporaryDirectory() as tmp:
    pkg=Path(tmp)/'pkg';out=Path(tmp)/'out';profile.stage_package(profile.ROOT,pkg,out,1210);out.mkdir()
    w=World(pkg/'scenario.add.xml',early,True);a=StepAdapter(w.observe,750,1210);cap=LogCapture(out);worker=bridge.protected_worker()
    try:
     with self.assertRaisesRegex(ValueError,'UNKNOWN_LOCAL_YELLOW_SCOPE'):
      bridge._diagnostic_loop(w,SimpleNamespace(observe=w.observe,request_phase=worker.request_phase),cap,out,
       dict(wall_limit_s=300,minimum_free_bytes=0,run_limit_bytes=300000000),f.fixture.old.fixture.old.fixture.fixture.FakeProcess(),time.monotonic(),a)
    finally:cap.close_handles()
    self.assertEqual(w.time,1204 if early else 1205)
    self.assertEqual((w.phase,w.state),(0,'G'))
    self.assertFalse(any(c[1]=='setPhase' and c[2]==1 for c in w.requests if c[0]>=1200))

 def one_step(self,tmp,fault=None):
  pkg=Path(tmp)/'pkg';profile.stage_package(profile.ROOT,pkg,Path(tmp)/'out',1210)
  w=World(pkg/'scenario.add.xml');w.time=1200;w.program='T10_G5Y3_NATIVE';w.phase=0;w.state='G';w.switch=1205
  a=StepAdapter(w.observe,750,1210);a.selected_new_program_at=1200;a.ledger.begin_step(1200)
  if fault=='identity':w.vehicle.getSpeedMode=lambda v:0
  if fault=='receiver_unknown':
   old=a.observe
   def unknown(c):
    v,ids,internal,rec=old(c);rec['available']='unknown';return v,ids,internal,rec
   a.observe=unknown
  a.prepare_step(w,1200);w.simulationStep(1201)
  if fault=='signal':w.state='r'
  if fault=='phase_bool':w.phase=True
  if fault=='brake':
   w.vspeed['M_flow.0']-=4.501;w.vehicle.getAcceleration=lambda v:-4.501 if v=='M_flow.0' else 0.
  if fault=='collision':w.simulation.getCollidingVehiclesNumber=lambda:1
  warning=dict(time_begin_s=1200,time_end_s=1201,coverage='CALLER_DECLARED_INTERVAL',source='offline-fixture',byte_start=0,byte_end=0,text='emergency braking' if fault=='warning' else '')
  a.reconcile_step(w,warning);return w,a

 def test_original_gates_and_strict_NUM_remain(self):
  for fault,reason in [('identity','UNKNOWN_MODES'),('receiver_unknown','UNKNOWN_RECEIVER'),('signal','POST_SIGNAL_APPLICATION_BINDING_MISMATCH'),('phase_bool','POST_SIGNAL_APPLICATION_BINDING_MISMATCH'),('brake','ORDINARY_BRAKING_EXCEEDED:M_flow.0'),('collision','COLLISION_OR_TELEPORT'),('warning','NATIVE_WARNING')]:
   with self.subTest(fault=fault),tempfile.TemporaryDirectory() as tmp:
    with self.assertRaisesRegex(ValueError,reason):self.one_step(tmp,fault)
  with tempfile.TemporaryDirectory() as tmp:
   pkg=Path(tmp)/'pkg';profile.stage_package(profile.ROOT,pkg,Path(tmp)/'out',1210);w=World(pkg/'scenario.add.xml')
   with self.assertRaisesRegex(ValueError,'NEW_SCOPE_NUMERICAL_EXCEPTION_NOT_ENABLED'):StepAdapter(w.observe,750,1210,{'enabled':True})
   w.time=1208;w.enter={};w.program='T10_G5Y3_NATIVE';w.phase=2;w.state='r';w.switch=1210
   a=StepAdapter(w.observe,750,1210)
   for t in range(1200,1208):
    new,c=a.ledger.begin_step(t)
    if new:a.ledger.mark_cycle_start(True)
    if t==1204:a.ledger.close_green(t,'MAX_GREEN_DEADLINE')
    a.ledger.end_step(t+1,[],a.ledger.motion_at(t))
   a.ledger.cycle['red_clock_bound']=True;a.ledger.begin_step(1208);a.previous_motion='r'
   a.prepare_step(w,1208);w.simulationStep(1209);w.enter['R_flow.0']=1209
   warning=dict(time_begin_s=1208,time_end_s=1209,coverage='CALLER_DECLARED_INTERVAL',source='offline-red-control',byte_start=0,byte_end=0,text='')
   with self.assertRaisesRegex(ValueError,'RED_CROSSING'):a.reconcile_step(w,warning)
   self.assertTrue(a.paused)
   w.time=1206;w.enter['R_flow.1']=1204;w.vspeed['R_flow.2']=7.060596259649246;w.vspeed['R_flow.1']=8.478656087227455;w.actual_gap=9.630877589859532;w.actual_secure=9.621192519298493
   q=current_following(w,'R_flow.2',1206);self.assertEqual(q['status'],'STOP_CURRENT_GAP_BOUND_DENIED');self.assertEqual(q['margin_m'],1.1);self.assertEqual(q['getSecureGap_args']['leaderMaxDecel'],9.)

 def test_offline_card_no_authorization_rejects_before_allocation_import_and_900_preserved(self):
  p=profile.prepare();c=profile.validate(p,require_environment=True)
  self.assertFalse(c['SUMO_execution_authorized']);self.assertFalse(c['numerical_exception_authority']['enabled'])
  with patch.object(bridge,'protected_worker',side_effect=AssertionError('must not import worker')) as worker:
   with self.assertRaisesRegex(ValueError,'FUTURE_EXACT_NATIVE_AUTHORIZATION_MISSING'):bridge.execute(p,profile.ROOT/profile.TASK/'releases'/profile.RUN/'EXECUTION_RELEASE.json')
   worker.assert_not_called()
  self.assertFalse((profile.ROOT/profile.output(profile.RUN)).parent.exists())
  from src.candidate_a_unified_alinea_20261013.policy import parameters as original
  self.assertEqual(original(8)['phases'],(('G',4,1),('y',2,2),('r',2,0)))
  self.assertEqual(c['sources_sha256']['src/candidate_a_unified_alinea_20261013/policy.py'],profile.sha(profile.ROOT/'src/candidate_a_unified_alinea_20261013/policy.py'))

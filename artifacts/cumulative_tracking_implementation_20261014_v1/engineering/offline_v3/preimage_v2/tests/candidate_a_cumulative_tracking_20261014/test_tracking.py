"""Focused synthetic movement and real-helper checks, never native physics proof."""
from pathlib import Path
from fractions import Fraction
from types import SimpleNamespace
from unittest.mock import patch
import importlib.util,json,tempfile,time,unittest
from src.candidate_a_cumulative_tracking_20261014 import profile,bridge
from src.candidate_a_cumulative_tracking_20261014.policy import Ledger,Command,parameters,select_packet
from src.candidate_a_cumulative_tracking_20261014.adapter import StepAdapter
from src.candidate_a_unified_alinea_20261013.producer import Producer,DETECTORS
from src.candidate_a_native_smoke_20261011.bridge_logs import LogCapture
s=importlib.util.spec_from_file_location('old_cumulative_fixture',profile.ROOT/'tests/candidate_a_unified_alinea_20261013/test_unified.py');f=importlib.util.module_from_spec(s);s.loader.exec_module(f)

class World(f.UnifiedWorld):
 def __init__(self,xml,early=True):
  super().__init__(xml);self.early=early;self.tokens=set();self.green=None;self.green_index=0
 def simulationStep(self,end):
  f.fixture.old.fixture.old.fixture.XMLFakeConnection.simulationStep(self,end);self.arrived=[]
  if end<1201 or self.state!='G':return
  token=(self.program,self.switch)
  if token not in self.tokens:
   self.tokens.add(token);maxg=5 if self.program=='T10_G5Y3_NATIVE' else 4
   self.green=(self.switch-maxg,maxg,self.green_index);self.green_index+=2
  begin,maxg,index=self.green
  if end==begin+1:self.enter[f'R_flow.{index}']=end
  if end==begin+(4 if self.early and maxg==5 else 5 if maxg==5 else 1):self.enter[f'R_flow.{index+1}']=end

class Schedule:
 mode='dynamic_commands'
 def __init__(self):self.events=[]
 def command_at(self,c,t):
  return Command('schedule:'+str(t),t,750 if t==1200 else 900,'SCHEDULED') if t in (1200,1201) else None
 def after_ack(self,c,t):pass

class TrackingTests(unittest.TestCase):
 def finish(self,l,n=2):
  begin=l.next_time_s;l.begin_step(begin);l.mark_cycle_start(True);c=l.cycle
  for t in range(begin,c['end_s']):
   if t!=begin:l.begin_step(t)
   if t==begin+c['max_green_s'] and c['green_end_s'] is None:l.close_green(t,'MAX_GREEN_DEADLINE')
   l.end_step(t+1,[str(begin)+':'+str(i) for i in range(n)] if t==begin else [],l.motion_at(t))
  return c

 def test_exact_long_blocks_actual_debt_and_unobserved_partial(self):
  l=Ledger(750,1200+48*100);self.assertTrue(all(v is None for v in l.accounting().values()))
  for i in range(500):
   self.finish(l);self.assertEqual(l.cycle['period_s'],(10,10,8,10,10)[i%5])
   self.assertLessEqual(abs(l.C-l.N),Fraction(1,6));self.assertEqual(l.C-l.N,(l.C-l.E)+(l.E-l.N))
  self.assertEqual((l.C,l.E,l.N,l.next_time_s),(1000,1000,1000,6000))
  for n in (0,1,2,3):
   with self.subTest(N=n):
    q=Ledger(750,1220);self.finish(q,n);self.assertEqual((q.E,q.N),(2,n))
    if n!=2:
     with self.assertRaisesRegex(ValueError,'SERVICE_PACKET_MISMATCH_HOLD'):q.begin_step(q.next_time_s)
    else:q.begin_step(q.next_time_s)
  q=Ledger(750,1203);q.begin_step(1200);q.mark_cycle_start(True);q.end_step(1201,[],'G')
  self.assertEqual((q.E,q.N),(0,0));self.assertTrue(q.accounting()['partial_cycle'])
  with self.assertRaisesRegex(ValueError,'UNKNOWN_ACTUAL_CUMULATIVE_N'):select_packet(0,None,750)
  for rate in (300,719,901,True,float('nan')):
   with self.assertRaises(ValueError):select_packet(0,0,rate)
  self.assertEqual(select_packet(Fraction(1,8),0,750)[0],10)

 def test_dynamic_latest_request_repeated_ids_boundary_and_no_nearest_execution(self):
  l=Ledger(750,1218)
  for t in range(1200,1218):
   command=Command('first',t,750,'SCHEDULED') if t==1200 else Command('new-same',t,750,'SCHEDULED') if t==1201 else Command('fast',t,900,'SCHEDULED') if t==1202 else None
   new,c=l.begin_step(t,command)
   if new:l.mark_cycle_start(True)
   if t==c['begin_s']+c['max_green_s']:l.close_green(t,'MAX_GREEN_DEADLINE')
   l.end_step(t+1,[str(t)+'a',str(t)+'b'] if t==c['begin_s'] else [],l.motion_at(t))
  self.assertEqual(l.C,Fraction(2*750+16*900,3600));self.assertEqual(l.N,4)
  self.assertEqual(l.requests['new-same']['status'],'SUPERSEDED_WITHOUT_APPLICATION')
  self.assertEqual(l.requests['fast']['first_application_s'],1210)
  self.assertEqual([x['period_s'] for x in l.rows],[10,8]);self.assertIsNone(l.rate_chain()['r_policy_pending_veh_h'])
  self.assertNotIn('application_latency',l.accounting())
  q=Ledger(750,1220);self.finish(q)
  q.begin_step(1210,Command('at-boundary',1210,900,'PROJECT_FEEDBACK',900));self.assertEqual(q.cycle['period_s'],8)
  with self.assertRaisesRegex(ValueError,'COMMAND_ID_REBOUND'):q.register(Command('at-boundary',1210,750,'FIXED'),1210)

 def loop(self,tmp,end=1296,early=True,producer=None,command=750):
  pkg=Path(tmp)/'pkg';out=Path(tmp)/'out';profile.stage_package(profile.ROOT,pkg,out,end);out.mkdir()
  w=World(pkg/'scenario.add.xml',early);a=StepAdapter(w.observe,command,end);cap=LogCapture(out);worker=bridge.protected_worker()
  try:bridge._diagnostic_loop(w,SimpleNamespace(observe=w.observe,request_phase=worker.request_phase),cap,out,
   dict(wall_limit_s=300,minimum_free_bytes=0,run_limit_bytes=None),f.fixture.old.fixture.old.fixture.fixture.FakeProcess(),time.monotonic(),a,producer or Producer('fixed750',750))
  finally:cap.close_handles()
  return w,a,out

 def test_real_xml_helper_mixed_clocks_log_routes_and_ack_unknown_stop(self):
  for early in (True,False):
   with self.subTest(early=early),tempfile.TemporaryDirectory() as tmp:
    w,a,out=self.loop(tmp,early=early)
    self.assertEqual((w.time,a.ledger.C,a.ledger.E,a.ledger.N),(1296,20,20,20))
    self.assertEqual([c['period_s'] for c in a.ledger.rows],[10,10,8,10,10]*2)
    self.assertTrue(a.checkpoint_verified);self.assertTrue(all(c['completed'] for c in a.ledger.rows))
    self.assertEqual([c['phase_exposure_s']['G'] for c in a.ledger.rows],[1 if c['period_s']==8 else 4 if early else 5 for c in a.ledger.rows])
    definitive=[json.loads(s) for s in (out/'yellow_scope.jsonl').read_text().splitlines()]
    self.assertEqual(len(definitive),10);self.assertTrue(all(x['screen_stage']=='PREPARED_BEFORE_FIRST_Y_MOTION' for x in definitive))
    self.assertFalse(a.body.active);self.assertTrue((out/'identity_journal.jsonl').is_file());self.assertEqual(parameters(8)['phases'],(('G',4,1),('y',2,2),('r',2,0)))
  with tempfile.TemporaryDirectory() as tmp:
   w,a,out=self.loop(tmp,1218,producer=Schedule());self.assertEqual(a.ledger.requests['schedule:1201']['first_application_s'],1210)
  with tempfile.TemporaryDirectory() as tmp:
   pkg=Path(tmp)/'pkg';profile.stage_package(profile.ROOT,pkg,Path(tmp)/'out',1210);w=World(pkg/'scenario.add.xml');w.time=1200;w.program='T10_G5Y3_NATIVE';w.phase=0;w.state='G';w.switch=1205
   a=StepAdapter(w.observe);a.selected_new_program_at=1200;a.ledger.begin_step(1200,Command('badACK',1200,750,'FIXED'));a.prepare_step(w,1200);w.simulationStep(1201);w.state='r'
   with self.assertRaisesRegex(ValueError,'POST_SIGNAL_APPLICATION_BINDING_MISMATCH'):a.reconcile_step(w,dict(time_begin_s=1200,time_end_s=1201,coverage='CALLER_DECLARED_INTERVAL',source='synthetic',byte_start=0,byte_end=0,text=''))
   self.assertIsNone(a.ledger.requests['badACK']['first_application_s']);self.assertTrue(a.paused)
   with self.assertRaisesRegex(ValueError,'NEW_SCOPE_NUMERICAL_EXCEPTION_NOT_ENABLED'):StepAdapter(w.observe,750,1296,{'enabled':True})

 def test_real_feedback_producer_and_offline_no_authorization_gate(self):
  with tempfile.TemporaryDirectory() as tmp:
   w,a,out=self.loop(tmp,1272,producer=Producer('real_alinea',900),command=900)
   rows=[json.loads(s) for s in (out/'feedback_events.jsonl').read_text().splitlines()]
   decisions=[x for x in rows if x['event']=='PROJECT_FEEDBACK_DECISION'];self.assertEqual([x['global_s'] for x in decisions],[1230,1260]);self.assertEqual([x['rate_previous_veh_h'] for x in decisions],[900,900])
   self.assertEqual(a.ledger.requests['feedback:1230']['first_application_s'],1232);self.assertEqual(a.ledger.requests['feedback:1260']['first_application_s'],1264)
   self.assertEqual((a.ledger.E,a.ledger.N),(18,18));self.assertEqual([c['period_s'] for c in a.ledger.rows],[8]*9)
  from src.candidate_a_unified_alinea_20261013.producer import Feedback,PARAMETERS
  fb=Feedback(PARAMETERS);first=fb.update(630,600,630,11+150/70,11+150/70);self.assertEqual(first['rate_clipped_veh_h'],750)
  self.assertEqual(fb.update(660,630,660,11,11)['rate_previous_veh_h'],750)
  # Actual host-bound card is prepared after test-source freeze. Validate gates
  # using this same real profile without replacing its validators.
  p=profile.prepare();release=profile.ROOT/profile.TASK/'releases'/profile.RUN/'EXECUTION_RELEASE.json'
  with patch.object(bridge,'protected_worker',side_effect=AssertionError('forbidden native import')) as worker:
   with self.assertRaisesRegex(ValueError,'FUTURE_EXACT_NATIVE_AUTHORIZATION_MISSING'):bridge.execute(p,release)
   worker.assert_not_called()
  self.assertFalse((profile.ROOT/profile.output(profile.RUN)).parent.exists())
  self.assertFalse((profile.ROOT/profile.TASK/'authorizations').exists())
  self.assertFalse((profile.ROOT/profile.TASK/'releases').exists())

if __name__=='__main__':unittest.main()

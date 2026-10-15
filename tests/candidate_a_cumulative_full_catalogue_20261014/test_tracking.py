"""Focused synthetic movement and real-helper checks, never native physics proof."""
from pathlib import Path
from fractions import Fraction
from types import SimpleNamespace
from unittest.mock import patch
import importlib.util,json,tempfile,time,unittest,os
from src.candidate_a_cumulative_full_catalogue_20261014 import profile,bridge
from src.candidate_a_cumulative_full_catalogue_20261014.policy import Ledger,Command,parameters,select_packet
from src.candidate_a_cumulative_full_catalogue_20261014.adapter import StepAdapter
from src.candidate_a_cumulative_full_catalogue_20261014.producer import Producer,DETECTORS
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
  if end==begin+(4 if self.early and maxg==5 else 5 if maxg==5 else 1) and not getattr(self,'omit_second',False):self.enter[f'R_flow.{index+1}']=end

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
  l=Ledger(750,1200+48*10);self.assertTrue(all(v is None for v in l.accounting().values()))
  for i in range(50):
   self.finish(l);self.assertEqual(l.cycle['period_s'],(10,9,10,9,10)[i%5])
   self.assertLessEqual(abs(l.C-l.N),Fraction(1,6));self.assertEqual(l.C-l.N,(l.C-l.E)+(l.E-l.N))
  self.assertEqual((l.C,l.E,l.N,l.next_time_s),(100,100,100,1680))
  for n in (0,1,2,3):
   with self.subTest(N=n):
    q=Ledger(750,1220);self.finish(q,n);self.assertEqual((q.E,q.N),(2,n))
    if n!=2:
     with self.assertRaisesRegex(ValueError,'SERVICE_PACKET_MISMATCH_HOLD'):q.begin_step(q.next_time_s)
    else:q.begin_step(q.next_time_s)
  q=Ledger(750,1203);q.begin_step(1200);q.mark_cycle_start(True);q.end_step(1201,[],'G')
  self.assertEqual((q.E,q.N),(0,0));self.assertTrue(q.accounting()['partial_cycle'])
  with self.assertRaisesRegex(ValueError,'UNKNOWN_ACTUAL_CUMULATIVE_N'):select_packet(0,None,750)
  for rate in (299,901,True,float('nan')):
   with self.assertRaises(ValueError):select_packet(0,0,rate)
  self.assertEqual(select_packet(0,0,300)[0],24);self.assertEqual(select_packet(0,0,900)[0],8)
  from src.candidate_a_unified_alinea_20261013.policy import parameters as original
  for period in range(8,25):
   got=parameters(period);expected=original(period)
   self.assertEqual(got['period_s'],period);self.assertEqual(sum(x[1] for x in got['phases']),period)
   self.assertGreaterEqual(got['phases'][2][1],2)
   if period!=10:self.assertEqual(got['phases'],expected['phases']);self.assertEqual(got['program'],expected['program'])
   else:self.assertEqual(got['phases'],(('G',5,1),('y',3,2),('r',2,0)))

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

 def loop(self,tmp,end=1296,early=True,producer=None,command=750,omit_second=False):
  pkg=Path(tmp)/'pkg';out=Path(tmp)/'out';profile.stage_package(profile.ROOT,pkg,out,end);out.mkdir()
  w=World(pkg/'scenario.add.xml',early);w.omit_second=omit_second;a=StepAdapter(w.observe,command,end);cap=LogCapture(out);worker=bridge.protected_worker()
  try:bridge._diagnostic_loop(w,SimpleNamespace(observe=w.observe,request_phase=worker.request_phase),cap,out,
   dict(wall_limit_s=300,minimum_free_bytes=0,run_limit_bytes=None),f.fixture.old.fixture.old.fixture.fixture.FakeProcess(),time.monotonic(),a,producer or Producer('fixed750',750))
  finally:cap.close_handles()
  export=os.environ.get('CA_FULL_CUMULATIVE_FIXTURE_EXPORT')
  if export:
   dest=Path(export)/(f'{(producer or SimpleNamespace(mode="fixed750")).mode}_{end}_{early}_{omit_second}')
   dest.mkdir(parents=True,exist_ok=False)
   for name in ('pre_steps.jsonl','post_steps.jsonl','step_ack.jsonl','command_events.jsonl','feedback_events.jsonl','policy_phase_requests.jsonl','policy_duration_requests.jsonl','yellow_scope.jsonl','yellow_scope_attempts.jsonl','identity_journal.jsonl','body_admission.jsonl','admission.jsonl'):
    path=out/name
    if not path.is_file():continue
    selected=[]
    for line in path.read_text().splitlines():
     row=json.loads(line)
     # retain all decision/control-only rows; preactivation identity/steps
     # are outside this public synthetic scheduler fixture.
     t=row.get('time_s',row.get('time_begin_s',row.get('requested_target_s',1200)))
     if t>=1200:selected.append(line)
    (dest/name).write_text("\n".join(selected)+"\n")
   (dest/'SYNTHETIC_RECEIPT.json').write_text(json.dumps(dict(classification='SYNTHETIC_REAL_HELPER_NO_NATIVE_SAFETY_OR_PHYSICS',end_s=w.time,cycles=a.ledger.rows,command_records=a.ledger.requests,accounting=a.ledger.accounting(),actual_input_is_fake_vehicle_movement=True,first_red_checkpoint_verified=a.checkpoint_verified)))
  return w,a,out

 def test_real_xml_helper_mixed_clocks_log_routes_and_ack_unknown_stop(self):
  for early in (True,):
   with self.subTest(early=early),tempfile.TemporaryDirectory() as tmp:
    w,a,out=self.loop(tmp,early=early)
    self.assertEqual((w.time,a.ledger.C,a.ledger.E,a.ledger.N),(1296,20,20,20))
    self.assertEqual([c['period_s'] for c in a.ledger.rows],[10,9,10,9,10]*2)
    self.assertTrue(a.checkpoint_verified);self.assertTrue(all(c['completed'] for c in a.ledger.rows))
    self.assertEqual([c['phase_exposure_s']['G'] for c in a.ledger.rows],[4 if c['period_s']==10 and early else 5 if c['period_s']==10 else 1 for c in a.ledger.rows])
    definitive=[json.loads(s) for s in (out/'yellow_scope.jsonl').read_text().splitlines()]
    self.assertEqual(len(definitive),10);self.assertTrue(all(x['screen_stage']=='PREPARED_BEFORE_FIRST_Y_MOTION' for x in definitive))
    self.assertEqual(len([x for x in a.ledger.events if x['event']=='PACKET_ACK_OBSERVED']),10)
    self.assertFalse(a.body.active);self.assertTrue((out/'identity_journal.jsonl').is_file());self.assertEqual(parameters(8)['phases'],(('G',4,1),('y',2,2),('r',2,0)))
  # G5 is tested with a single T10 slot; the synthetic queue's later
  # receiver refusal is not repaired by weakening the actual admission gate.
  for omit in (False,True):
   with self.subTest(deadline_missing_second=omit),tempfile.TemporaryDirectory() as tmp:
    w,a,out=self.loop(tmp,1210,early=False,omit_second=omit)
    self.assertEqual(a.ledger.rows[0]['phase_exposure_s'],{'G':5,'y':3,'r':2})
    self.assertEqual((a.ledger.E,a.ledger.N),(2,1 if omit else 2))
    self.assertEqual(a.ledger.rows[0]['green_end_reason'],'MAX_GREEN_DEADLINE' if omit else 'ACTUAL_QUOTA_ACK')
    if omit:
     a.ledger.end_s=1220
     with self.assertRaisesRegex(ValueError,'SERVICE_PACKET_MISMATCH_HOLD'):a.ledger.begin_step(1210)
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
   w,a,out=self.loop(tmp,1296,producer=Producer('real_alinea',900),command=900)
   rows=[json.loads(s) for s in (out/'feedback_events.jsonl').read_text().splitlines()]
   decisions=[x for x in rows if x['event']=='PROJECT_FEEDBACK_DECISION'];self.assertEqual([x['global_s'] for x in decisions],[1230,1260,1290]);self.assertEqual([x['rate_previous_veh_h'] for x in decisions],[900,900,900])
   self.assertEqual(a.ledger.requests['feedback:1230']['first_application_s'],1232);self.assertEqual(a.ledger.requests['feedback:1260']['first_application_s'],1264)
   self.assertEqual((a.ledger.E,a.ledger.N),(24,24));self.assertEqual([c['period_s'] for c in a.ledger.rows],[8]*12);self.assertIsNone(a.ledger.requests['feedback:1290']['first_application_s'])
  q=Ledger(300,1266)
  schedule={1200:300,1201:750,1226:900,1237:300}
  for t in range(1200,1266):
   cmd=Command(f'original:{t}',t,schedule[t],'SCHEDULED') if t in schedule else None
   new,c=q.begin_step(t,cmd)
   if new:q.mark_cycle_start(True)
   if t==c['begin_s']+c['max_green_s']:q.close_green(t,'MAX_GREEN_DEADLINE')
   q.end_step(t+1,[str(t)+'a',str(t)+'b'] if new else [],q.motion_at(t))
  self.assertEqual(q.C,Fraction(300+25*750+11*900+29*300,3600))
  self.assertEqual(q.requests['original:1201']['first_application_s'],1224)
  self.assertTrue(all(8<=x['period_s']<=24 for x in q.rows))
  from src.candidate_a_cumulative_full_catalogue_20261014.producer import Feedback,PARAMETERS
  fb=Feedback(PARAMETERS);first=fb.update(630,600,630,11+150/70,11+150/70);self.assertEqual(first['rate_clipped_veh_h'],750)
  self.assertEqual(fb.update(660,630,660,11,11)['rate_previous_veh_h'],750)
  # Native permission/card gate is checked after independent reader freezes; no card prepared by this suite.

if __name__=='__main__':unittest.main()

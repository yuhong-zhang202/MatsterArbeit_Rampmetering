"""Affected synthetic helper tests: no native physics or executable permission."""
from pathlib import Path
from fractions import Fraction
from types import SimpleNamespace
import importlib.util,json,os,tempfile,time,unittest
from src.candidate_a_cumulative_full_followup_20261014 import profile,bridge,budget
from src.candidate_a_cumulative_full_catalogue_20261014.adapter import StepAdapter
from src.candidate_a_cumulative_full_catalogue_20261014.producer import Producer
from src.candidate_a_native_smoke_20261011.bridge_logs import LogCapture
s=importlib.util.spec_from_file_location('prior_full_helper_fixture',profile.ROOT/'tests/candidate_a_cumulative_full_catalogue_20261014/test_tracking.py');old=importlib.util.module_from_spec(s);s.loader.exec_module(old)

class World(old.World):
 def __init__(self,xml):super().__init__(xml);self.actual_step_targets=[]
 def simulationStep(self,t):self.actual_step_targets.append(t);super().simulationStep(t)

class FollowupTests(unittest.TestCase):
 def loop(self,mode,initial):
  with tempfile.TemporaryDirectory() as tmp:
   pkg=Path(tmp)/'pkg';out=Path(tmp)/'out';profile.stage_package(profile.ROOT,pkg,out,1296);out.mkdir()
   w=World(pkg/'scenario.add.xml');a=StepAdapter(w.observe,initial,1296);producer=Producer(mode,initial);capture=LogCapture(out);worker=bridge.protected_worker()
   try:bridge._diagnostic_loop(w,SimpleNamespace(observe=w.observe,request_phase=worker.request_phase),capture,out,dict(wall_limit_s=300,minimum_free_bytes=0,run_limit_bytes=None),old.f.fixture.old.fixture.old.fixture.fixture.FakeProcess(),time.monotonic(),a,producer)
   finally:capture.close_handles()
   self.assertEqual(w.actual_step_targets,list(range(1,1297)));self.assertEqual(w.time,1296)
   self.assertTrue(a.paused);self.assertTrue(a.checkpoint_verified)
   export=os.environ.get('CA_FULL_FOLLOWUP_FIXTURE_EXPORT')
   if export:
    dest=Path(export)/mode;dest.mkdir(parents=True,exist_ok=False)
    for name in ('pre_steps.jsonl','post_steps.jsonl','step_ack.jsonl','command_events.jsonl','feedback_events.jsonl','policy_phase_requests.jsonl','policy_duration_requests.jsonl','yellow_scope.jsonl','yellow_scope_attempts.jsonl','identity_journal.jsonl','body_admission.jsonl','admission.jsonl'):
     p=out/name
     if not p.exists():continue
     selected=[]
     for line in p.read_text().splitlines():
      row=json.loads(line);t=row.get('time_s',row.get('time_begin_s',row.get('requested_target_s',1200)))
      if t>=1200:selected.append(line)
     (dest/name).write_text('\n'.join(selected)+'\n')
    (dest/'SYNTHETIC_RECEIPT.json').write_text(json.dumps(dict(classification='SYNTHETIC_REAL_XML_HELPER_NOT_NATIVE_DATA',mode=mode,end_s=1296,cycles=a.ledger.rows,command_records=a.ledger.requests,accounting=a.ledger.accounting(),partial_final_cycle=not a.ledger.cycle['completed'],body_censored_ids=sorted(a.body.active),actual_input_is_fake_vehicle_movement=True,first_red_checkpoint_verified=a.checkpoint_verified,terminal_classification='APPROVED_END_PARTIAL_OR_BODY_CENSORED_NOT_QUALIFIED' if not a.ledger.cycle['completed'] or a.body.active else 'PACKET_CYCLES_OBSERVED_NO_MONITORED_ANOMALY_NOT_QUALIFIED'),indent=2)+'\n')
   return a,producer

 def test_actual_dynamic_producer_fixed_end_partial_and_boundary_application(self):
  a,p=self.loop('dynamic_commands',300)
  self.assertEqual(a.ledger.C,Fraction(311,24));self.assertEqual(a.ledger.E,12);self.assertEqual(a.ledger.N,14)
  self.assertFalse(a.ledger.cycle['completed']);self.assertEqual(a.ledger.rows[-1]['phase_exposure_s'],{'G':1,'y':5,'r':5})
  self.assertEqual([x['period_s'] for x in a.ledger.rows],[24,8,8,8,13,24,24])
  for request,time_s in [('dynamic_commands:1200',1200),('scheduled:1201',1224),('scheduled:1226',1232),('scheduled:1237',1240)]:
   self.assertEqual(a.ledger.requests[request]['first_application_s'],time_s)
  self.assertEqual([x['application_delay_s'] for x in a.ledger.events if x['event']=='ACK_OBSERVED'],[0,23,6,3])
  self.assertTrue(all(x['application_status']=='ACK_OBSERVED' for x in a.ledger.rows));self.assertFalse(a.body.active)
  # Final partial is not completed E, not a hold bypass into the following cycle.
  self.assertEqual((a.ledger.E,a.ledger.rows[-1]['completed']),(12,False))

 def test_real_feedback_unchanged_state_windows_and_pending_last_request(self):
  a,p=self.loop('real_alinea',900)
  rows=[x for x in p.events if x['event']=='PROJECT_FEEDBACK_DECISION']
  self.assertEqual([x['global_s'] for x in rows],[1230,1260,1290]);self.assertEqual([x['logical_s'] for x in rows],[630,660,690])
  self.assertEqual([x['rate_previous_veh_h'] for x in rows],[900,900,900])
  self.assertEqual(a.ledger.requests['feedback:1230']['first_application_s'],1232);self.assertEqual(a.ledger.requests['feedback:1260']['first_application_s'],1264)
  self.assertIsNone(a.ledger.requests['feedback:1290']['first_application_s']);self.assertEqual((a.ledger.C,a.ledger.E,a.ledger.N),(24,24,24))

 def test_exact_modes_and_new_budget_unknown_does_not_inherit_old_balance(self):
  self.assertEqual(profile.spec(profile.RUN)['mode'],'dynamic_commands')
  self.assertEqual(profile.spec('UA_CUMULATIVE_FULL_ALINEA_S17_01')['Feedback']['detector_ids'],['p1_main_down_20_l0','p1_main_down_20_l1'])
  with self.assertRaisesRegex(ValueError,'EXACT_FOLLOWUP_IDENTITY_REQUIRED'):profile.spec('UA_CUMULATIVE_FULL750_S17_01')
  with tempfile.TemporaryDirectory() as tmp:
   r=Path(tmp);b=budget.accounting(r);self.assertEqual(b['remaining_s'],600);self.assertIsNone(b['remaining_bytes'])
   (r/budget.RAW/profile.RUN).mkdir(parents=True)
   with self.assertRaisesRegex(ValueError,'PREVIOUS_RUN_REQUIRES_THREE_ROLE_SETTLEMENT'):budget.accounting(r)

if __name__=='__main__':unittest.main()

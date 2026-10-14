"""Synthetic logging-only checks: no vehicle/native safety behavior is certified."""
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch
import json,tempfile,time,unittest
from src.candidate_a_cumulative_full_followup_20261014 import bridge
from src.candidate_a_cumulative_full_catalogue_20261014.policy import Ledger

class StopJournalTests(unittest.TestCase):
 def actual_ledger_events(self):
  ledger=Ledger(900,1208);ledger.begin_step(1200);ledger.mark_cycle_start(True)
  ledger.end_step(1201,[],'G')
  return ledger

 def test_real_loop_stop_persists_created_ACK_without_another_step(self):
  original=ValueError('POST_CURRENT_GAP_BOUND_DENIED')
  conn=SimpleNamespace(simulation=SimpleNamespace(getTime=lambda:conn.clock),clock=0,stats={},trafficlight=SimpleNamespace())
  targets=[]
  def advance(t):targets.append(t);conn.clock=t
  conn.simulationStep=advance
  adapter=SimpleNamespace(end_s=2,ledger=Ledger(900,1208),pending=None,receipts=[],last_completed=None,last_end=None,last_yellow_scope=None)
  def prepare(c,t):
   adapter.pending={'motion':'G'};adapter.ledger.begin_step(1200);adapter.ledger.mark_cycle_start(True)
   return {'classification':'SYNTHETIC_LOGGING_FIXTURE_CLOCK_OFFSET_NOT_NATIVE'}
  def reconcile(c,warning):
   adapter.ledger.end_step(1201,[],'G');adapter.last_end=1
   adapter.receipts.append({'time_begin_s':0,'time_end_s':1,'status':'STOP_OBSERVED_AFTER_STEP'})
   adapter.pending=None;raise original
  adapter.prepare_step=prepare;adapter.reconcile_step=reconcile
  worker=SimpleNamespace(request_phase=lambda *args:None)
  capture=SimpleNamespace(snapshot=lambda *a:{'streams':{'sumo_stderr.log':{'text':''}}},adapter_warning=lambda x:{})
  producer=SimpleNamespace(events=[],mode='dynamic_commands')
  with tempfile.TemporaryDirectory() as tmp:
   out=Path(tmp)
   # Test-only identity/frame facades; actual vehicle predicates are not mocked into a safety PASS.
   with patch.object(bridge,'FrameCache',side_effect=lambda x:x),patch.object(bridge,'identity_snapshot',return_value={'synthetic':True}):
    with self.assertRaises(ValueError) as raised:bridge._diagnostic_loop(conn,worker,capture,out,{'wall_limit_s':300,'minimum_free_bytes':0,'run_limit_bytes':None},SimpleNamespace(poll=lambda:None),time.monotonic(),adapter,producer)
   self.assertIs(raised.exception,original);self.assertEqual(targets,[1])
   rows=[json.loads(x) for x in (out/'command_events.jsonl').read_text().splitlines()]
   self.assertEqual(rows,adapter.ledger.events)
   self.assertEqual([x['event'] for x in rows].count('PACKET_ACK_OBSERVED'),1)
   self.assertEqual([x['event'] for x in rows].count('ACK_OBSERVED'),1)
   self.assertEqual(json.loads((out/'post_steps.jsonl').read_text())['last_accounted_s'],1)

 def test_success_and_repeat_flush_does_not_duplicate_or_fabricate(self):
  ledger=self.actual_ledger_events();adapter=SimpleNamespace(ledger=ledger);producer=SimpleNamespace(events=[{'event':'SYNTHETIC_FEEDBACK_ONLY'}]);cursors={'command':0,'feedback':0}
  with tempfile.TemporaryDirectory() as tmp:
   out=Path(tmp);bridge._flush_observed_events(adapter,producer,out,cursors);bridge._flush_observed_events(adapter,producer,out,cursors)
   self.assertEqual([json.loads(x) for x in (out/'command_events.jsonl').read_text().splitlines()],ledger.events)
   self.assertEqual([json.loads(x) for x in (out/'feedback_events.jsonl').read_text().splitlines()],producer.events)
   self.assertEqual(cursors,{'command':len(ledger.events),'feedback':1})

 def test_IO_unknown_preserves_original_and_successful_prefix_cursor(self):
  ledger=self.actual_ledger_events();adapter=SimpleNamespace(ledger=ledger);producer=SimpleNamespace(events=[]);cursors={'command':0,'feedback':0};original=ValueError('POST_CURRENT_GAP_BOUND_DENIED');real_append=bridge.append_new
  def fail_second(path,row):
   if path.name=='command_events.jsonl' and cursors['command']==1:raise OSError('SYNTHETIC_IO_FAILURE_BEFORE_SECOND_WRITE')
   return real_append(path,row)
  with tempfile.TemporaryDirectory() as tmp:
   out=Path(tmp)
   with patch.object(bridge,'append_new',side_effect=fail_second):
    with self.assertRaisesRegex(RuntimeError,'UNKNOWN_STOP_EVENT_LOGGING.*POST_CURRENT_GAP_BOUND_DENIED') as caught:bridge._retain_reconcile_stop(adapter,producer,out,cursors,{'retained_receipts':[]},original)
   self.assertIs(caught.exception.__cause__,original);self.assertEqual(cursors['command'],1)
   info=json.loads((out/'stop_event_logging_failure.json').read_text());self.assertEqual(info['status'],'UNKNOWN_STOP_EVENT_LOGGING');self.assertTrue(info['uncertain_write_not_retried']);self.assertIn('POST_CURRENT_GAP_BOUND_DENIED',info['original_stop'])
   self.assertFalse((out/'post_steps.jsonl').exists())
   # Explicit unit-level resume after a known pre-write failure, never an automatic native/uncertain-write retry.
   bridge._flush_observed_events(adapter,producer,out,cursors)
   self.assertEqual([json.loads(x) for x in (out/'command_events.jsonl').read_text().splitlines()],ledger.events)

if __name__=='__main__':unittest.main()

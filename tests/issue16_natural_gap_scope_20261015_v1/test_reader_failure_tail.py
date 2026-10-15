"""Bounded saved-terminal and provenance mutations; no traffic loop."""
import sys,json,tempfile,unittest
from pathlib import Path
from copy import deepcopy
sys.dont_write_bytecode=True
from scripts.natural_actuator_qualification_20261015_v1 import actual,provenance,streaming
ROOT=Path(__file__).resolve().parents[2]
RAW=ROOT/'data/raw/natural_actuator_qualification_20261015_v1/QUAL_NATURAL_ALINEA_R900_S17_01/outputs'
class FailureTailTests(unittest.TestCase):
 def test_native_endpoint_existing_id_preserved(self):
  row={'id':'R_flow.0','lane':':ramp_mid_0_0','pos':'1.74023886','speed':'3.93402932'}
  self.assertEqual(actual.endpoint_records({'R_flow.0':row}),[row])
  with self.assertRaises(ValueError):actual.endpoint_records({'R_flow.1':row})
 @classmethod
 def setUpClass(cls):
  cls.receipt=json.loads((RAW/'bridge_receipt.json').read_text())
  for row in streaming.posts(RAW/'post_steps.jsonl'):cls.row=row
  cls.feedback=list(streaming.jsonl(RAW/'feedback_events.jsonl'))
  cls.requests=[e for e in streaming.jsonl(RAW/'command_events.jsonl') if e['event']=='REQUESTED']
 def test_exact_terminal_cause_and_complete_feedback(self):
  self.assertEqual(provenance.gap_stop(self.receipt,self.row)['last_ACK'],650)
  variants=[]
  for key,value in [('terminal_reason','DiagnosticStop:UNRELATED'),('reasons',[]),('time_end_s',649)]:
   row=deepcopy(self.row);row[key]=value;variants.append((self.receipt,row))
  row=deepcopy(self.row);row['post_native_receiver_decision']['current_following']['vehicle_id']='R_flow.9';variants.append((self.receipt,row))
  receipt=deepcopy(self.receipt);receipt['last_step_ack']['actual_time_verified']=False;variants.append((receipt,self.row))
  for receipt,row in variants:
   with self.subTest(row=row.get('terminal_reason')),self.assertRaises(ValueError):provenance.gap_stop(receipt,row)
  r=actual.feedback_prefix(self.feedback,self.requests,self.receipt,self.row)
  self.assertEqual(r['windows'][0]['end_s'],630);self.assertAlmostEqual(r['windows'][0]['rate_veh_h'],866.0731695178215)
  self.assertEqual(r['terminal_ACK_feedback_status'],'NOT_OBSERVED_AFTER_RETAINED_STOP')
  bad=[e for e in self.feedback if not(e['event']=='E1_POST_ACK_EVENTS' and e['global_s']==629)]
  with self.assertRaises(ValueError):actual.feedback_prefix(bad,self.requests,self.receipt,self.row)
 def test_native_EOF_separate_from_worker_failure(self):
  r=self.receipt;g=json.loads((RAW.parent/'guardian_receipt.json').read_text());identity=json.loads((RAW/'owned_process_identity.json').read_text());logs=list(streaming.jsonl(RAW/'log_intervals.jsonl'))
  def call(receipt,guardian,row):return provenance.eof(RAW,receipt,logs,guardian,identity,r['card_sha256'],provenance.sha(RAW/'release.json'),row)
  self.assertEqual(call(r,g,self.row)['status'],'OBSERVED_NATIVE_EOF_AFTER_CONTROLLER_STOP')
  cases=[]
  bad=deepcopy(g);bad['group_cleanup']['no_live_owned_members']=None;cases.append((r,bad,self.row))
  bad=deepcopy(g);bad['stop_reason']='TIMEOUT';cases.append((r,bad,self.row))
  bad=deepcopy(g);bad['worker_returncode']=True;cases.append((r,bad,self.row))
  bad=deepcopy(r);bad['error']='DiagnosticStop:UNRELATED';cases.append((bad,g,self.row))
  bad=deepcopy(r);bad['final_logs']['process_returncode']=1;cases.append((bad,g,self.row))
  cases.append((r,g,None))
  for receipt,guardian,row in cases:
   with self.subTest(guardian=guardian['stop_reason']),self.assertRaises(ValueError):call(receipt,guardian,row)
 def test_explicit_reader_version_and_immutable_snapshot(self):
  with tempfile.TemporaryDirectory() as tmp:
   root=Path(tmp);raw=root/'raw';path='scripts/natural_actuator_qualification_20261015_v1/actual.py';runtime='src/immutable_runtime.py'
   for name in (path,runtime):
    p=root/name;p.parent.mkdir(parents=True,exist_ok=True);p.write_text('old')
    s=raw/'snapshots'/name;s.parent.mkdir(parents=True,exist_ok=True);s.write_text('old')
   sources={name:provenance.sha(root/name) for name in (path,runtime)};(root/path).write_text('new reader')
   with self.assertRaises(ValueError):provenance.execution_sources(root,raw,sources)
   result=provenance.execution_sources(root,raw,sources,True);self.assertEqual(len(result['changed_reader_files']),1)
   snap=raw/'snapshots'/path;snap.write_text('tampered')
   with self.assertRaises(ValueError):provenance.execution_sources(root,raw,sources,True)
   snap.write_text('old');bad=dict(sources);bad[path]='0'*64
   with self.assertRaises(ValueError):provenance.execution_sources(root,raw,bad,True)
   (root/runtime).write_text('runtime drift')
   with self.assertRaises(ValueError):provenance.execution_sources(root,raw,sources,True)
if __name__=='__main__':unittest.main(verbosity=2)

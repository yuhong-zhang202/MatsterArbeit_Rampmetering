import copy,importlib.util,json,sys,tempfile,unittest
from pathlib import Path
BASE=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('executor',BASE/'runtime_executor.py');e=importlib.util.module_from_spec(spec);spec.loader.exec_module(e)
class Tests(unittest.TestCase):
 def setUp(self):self.dir=OUT/self._testMethodName;self.dir.mkdir();self.a={'attempt_id':'SYNTHETIC','run_root':str(self.dir/'run'),'argv':[sys.executable,'-c','import sys; print("fake"); print("warning preserved",file=sys.stderr)']}
 def run_fake(self,**kw):return e._run(self.a,'synthetic',{},synthetic=True,**kw)
 def test_success_preserves_stderr_and_claim(self):
  r=self.run_fake();self.assertEqual(r['status'],'process_completed_pending_gate');self.assertIn('warning preserved',(Path(self.a['run_root'])/'stderr.log').read_text());self.assertEqual(json.loads((Path(self.a['run_root'])/'reservation.json').read_text())['consumed_SUMO_starts'],1)
 def test_timeout(self):
  self.a['argv']=[sys.executable,'-c','import time;time.sleep(5)'];self.assertEqual(self.run_fake(timeout=.1)['status'],'terminal_timeout')
 def test_nonzero(self):
  self.a['argv']=[sys.executable,'-c','raise SystemExit(7)'];self.assertEqual(self.run_fake()['status'],'terminal_nonzero')
 def test_output_cap(self):self.assertEqual(self.run_fake(cap=100)['status'],'terminal_output_stop_line')
 def test_startfailure(self):
  def fail(*a,**k):raise OSError('synthetic start failure')
  self.assertEqual(self.run_fake(factory=fail)['status'],'terminal_start_failure')
 def test_duplicate_success(self):
  self.run_fake()
  with self.assertRaises(FileExistsError):self.run_fake()
 def test_duplicate_failure(self):
  self.a['argv']=[sys.executable,'-c','raise SystemExit(2)'];self.run_fake()
  with self.assertRaises(FileExistsError):self.run_fake()
 def test_orphan_claim(self):
  Path(self.a['run_root']).mkdir()
  with self.assertRaises(FileExistsError):self.run_fake()
 def test_monitor_exception(self):
  self.a['argv']=[sys.executable,'-c','import time;time.sleep(5)']
  def bad(p):raise ValueError('synthetic monitor failure')
  self.assertEqual(self.run_fake(size_fn=bad)['status'],'terminal_inspection_failure')
 def gate(self):
  self.run_fake();run=Path(self.a['run_root']);g={'attempt_id':'SYNTHETIC','card_sha256':'synthetic','technical_status':'PASS','physical_status':'suitable','progression_allowed':True,'checks':[{'check_id':x,'status':'PASS'} for x in e.REQUIRED],'execution_receipt_sha256':e.digest(run/'execution_receipt.json'),'output_manifest_sha256':e.digest(run/'output_manifest.json'),'analysis_version_binding':e.binding(__file__)};return g
 def validate(self,g):
  p=self.dir/'gate.json';p.write_text(json.dumps(g));return e.validate_gate(p,self.a,'synthetic')
 def test_good_gate(self):self.validate(self.gate())
 def test_missing_gate_check(self):
  g=self.gate();g['checks'].pop()
  with self.assertRaises(ValueError):self.validate(g)
 def test_duplicate_gate_check(self):
  g=self.gate();g['checks'][-1]=g['checks'][0]
  with self.assertRaises(ValueError):self.validate(g)
 def test_physical_stop(self):
  g=self.gate();g['physical_status']='complete_evidence_but_comparison_unsuitable_physical_event'
  with self.assertRaises(ValueError):self.validate(g)
 def test_wrong_gate_card(self):
  g=self.gate();g['card_sha256']='wrong'
  with self.assertRaises(ValueError):self.validate(g)
 def test_output_tamper(self):
  g=self.gate();(Path(self.a['run_root'])/'stderr.log').write_text('tampered')
  with self.assertRaises(ValueError):self.validate(g)
 def test_final_output_violation(self):
  g=self.gate();(Path(self.a['run_root'])/'final_output_violation.json').write_text('{}')
  with self.assertRaises(ValueError):self.validate(g)
 def test_approval_missing(self):
  with self.assertRaises(FileNotFoundError):e.preflight(self.dir/'missing',self.dir/'missingapproval',e.ORDER[0],{})
 def review(self,**override):
  data={'status':'PASS_STATIC_FINAL','stage':'exact_runtime_package','card_sha256':'synthetic'};data.update(override);p=self.dir/'review.json';p.write_text(json.dumps(data));return e.binding(p)
 def test_exact_final_review_pass(self):e.validate_review(self.review(),'synthetic')
 def test_design_only_review_rejected(self):
  with self.assertRaises(ValueError):e.validate_review(self.review(stage='design_scope'),'synthetic')
 def test_wrong_card_review_rejected(self):
  with self.assertRaises(ValueError):e.validate_review(self.review(card_sha256='old_card'),'synthetic')
 def test_nonpass_review_rejected(self):
  with self.assertRaises(ValueError):e.validate_review(self.review(status='FAIL'),'synthetic')
 def test_old_pass_word_review_rejected(self):
  with self.assertRaises(ValueError):e.validate_review(self.review(status='PASS'),'synthetic')
 def test_physical_marker_stops_process(self):
  self.a['argv']=[sys.executable,'-c','import time;time.sleep(5)']
  def start(*args,**kwargs):
   p=e.subprocess.Popen(*args,**kwargs)
   (Path(self.a['run_root'])/'physical_stop_request.json').write_text(json.dumps({'event_type':'collision','observed_excerpt':'SYNTHETIC collision example','observer':'primary','source_path':'synthetic.log','observed_unix':0}))
   return p
  r=self.run_fake(factory=start);self.assertEqual(r['status'],'partial_evidence_physical');self.assertIsNotNone(r['returncode'])
 def test_prior_time_budget_not_reset(self):
  self.a['argv']=[sys.executable,'-c','import time;time.sleep(5)']
  self.assertEqual(self.run_fake(prior_time=e.LIMITS['total_monitored_s']-.01)['status'],'terminal_timeout')
 def test_prior_byte_budget_not_reset(self):
  self.assertEqual(self.run_fake(prior_bytes=e.LIMITS['total_observed_bytes']-10)['status'],'terminal_output_stop_line')
 def test_fixed_scope(self):self.assertEqual(len(e.ORDER),5);self.assertEqual(e.LIMITS['retry'],0);self.assertEqual(e.LIMITS['seed23_starts'],0);self.assertEqual(len(set(e.REQUIRED)),14)
if __name__=='__main__':
 OUT=BASE/'fake_tests_revision01';OUT.mkdir(exist_ok=False)
 suite=unittest.defaultTestLoader.loadTestsFromTestCase(Tests)
 with (OUT/'tests.log').open('w') as log:result=unittest.TextTestRunner(stream=log,verbosity=2).run(suite)
 e.durable(BASE/'executor_test_receipt.json',{'status':'PASS' if result.wasSuccessful() else 'FAIL','tests_run':result.testsRun,'failures':len(result.failures),'errors':len(result.errors),'executor_sha256':e.digest(BASE/'runtime_executor.py'),'test_script':e.binding(__file__),'test_log':e.binding(OUT/'tests.log'),'real_SUMO_starts':0,'synthetic_python_processes_only':True})
 print(json.dumps({'passed':result.wasSuccessful(),'count':result.testsRun}));sys.exit(not result.wasSuccessful())

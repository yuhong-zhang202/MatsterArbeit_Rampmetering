#!/usr/bin/env python3
"""Offline tests. Fake process objects plus Python-only process-group watchdog probe."""
import copy
import importlib.util
import json
import os
from pathlib import Path
import sys
import time
import unittest
from unittest.mock import patch

HERE = Path(__file__).absolute().parent
spec = importlib.util.spec_from_file_location('executor', HERE / 'build01_executor.py')
e = importlib.util.module_from_spec(spec)
spec.loader.exec_module(e)
RUN = HERE / 'fake_process_tests_revision01'
RUN.mkdir(exist_ok=False)
RESULTS = []

class FakeClock:
    def __init__(self): self.now=0
    def __call__(self): return self.now
    def sleep(self, seconds): self.now+=seconds

class FakeProcess:
    pid=9000001
    def __init__(self, mode): self.mode=mode; self.killed=False
    def poll(self):
        if self.killed: return -15
        return {'ok':0,'nonzero':7,'missing':0}.get(self.mode)

class Tests(unittest.TestCase):
    def setUp(self):
        self.case=RUN/self._testMethodName
        self.case.mkdir()
        self.output=self.case/'BUILD01'
    def runfake(self, mode='ok', **kwargs):
        clock=FakeClock()
        def factory(argv, **kw):
            self.assertTrue((self.output/'reservation.json').exists())
            self.assertEqual(json.loads((self.output/'reservation.json').read_text())['consumed_starts'],1)
            if mode=='startfailure': raise OSError('synthetic Popen failure')
            kw['stdout'].write(b'synthetic stdout\n')
            kw['stderr'].write(b'synthetic warning retained\n')
            if mode!='missing': (self.output/'network.net.xml').write_text('<net/>')
            return FakeProcess(mode)
        return e._run_reserved(self.output,['FAKE_PROCESS_NO_BINARY'],str(self.case),{}, {'synthetic_only':True},factory=factory,clock=clock,sleep=clock.sleep,terminate=lambda p:setattr(p,'killed',True),synthetic=True,**kwargs)
    def test_success_stderr_and_reservation(self):
        r=self.runfake(); self.assertEqual(r['status'],'completed_pending_compiled_review'); self.assertTrue(r['stderr_nonempty']); self.assertFalse(r['compiled_guard_acceptance']); self.assertEqual(r['consumed_starts'],1)
        self.assertIn('synthetic warning',(self.output/'netconvert.stderr.log').read_text())
    def test_nonzero(self): self.assertEqual(self.runfake('nonzero')['status'],'terminal_nonzero')
    def test_timeout(self):
        r=self.runfake('hang'); self.assertEqual(r['status'],'terminal_timeout'); self.assertTrue(r['termination_requested']); self.assertGreaterEqual(r['wallclock_s'],30)
    def test_cap(self):
        r=self.runfake('hang',size_fn=lambda p:100000001); self.assertEqual(r['status'],'terminal_output_envelope_exceeded'); self.assertTrue(r['termination_requested'])
    def test_startfailure(self): self.assertEqual(self.runfake('startfailure')['status'],'terminal_start_failure')
    def test_missing_network(self): self.assertEqual(self.runfake('missing')['status'],'terminal_missing_or_invalid_network')
    def test_duplicate_after_success(self):
        self.runfake()
        with self.assertRaises(FileExistsError): self.runfake()
    def test_duplicate_after_failure(self):
        self.runfake('nonzero')
        with self.assertRaises(FileExistsError): self.runfake()
    def test_orphan_claim_consumed(self):
        self.output.mkdir()
        with self.assertRaises(FileExistsError): self.runfake()
    def test_monitor_exception_terminates(self):
        def fail(path): raise RuntimeError('synthetic monitor failure')
        r=self.runfake('hang',size_fn=fail); self.assertTrue(r['termination_requested']); self.assertEqual(r['status'],'terminal_output_inspection_failure')
    def test_directory_byte_count(self):
        self.output.mkdir(); (self.output/'a').write_bytes(b'1234'); (self.output/'sub').mkdir(); (self.output/'sub/b').write_bytes(b'12'); self.assertEqual(e.directory_bytes(self.output),6)
    def test_output_symlink_rejected(self):
        self.output.mkdir(); (self.output/'bad').symlink_to(self.case)
        with self.assertRaises(ValueError): e.directory_bytes(self.output)
    def test_input_tamper_rejected(self):
        p=self.case/'source'; p.write_text('before'); b={'path':str(p),'sha256':e.digest(p),'bytes':6}; e.verify_binding(b); p.write_text('after!')
        with self.assertRaises(ValueError): e.verify_binding(b)
    def test_draft_card_rejected(self):
        with self.assertRaisesRegex(ValueError,'Not final'): e.validate_card(HERE/'SG6_BUILD_request_card_draft.json',self.case/'missing',{})
    def test_approval_requires_exact_hash_and_scope(self):
        card=self.case/'synthetic_not_a_build_card.json'; card.write_text('{}')
        side=self.case/'fictitious_sidecar.json'
        a=dict(status='user-approved',synthetic_test_only=False,scope='SG6-BUILD BUILD01 only',card_sha256=e.digest(card),card_path=str(card),max_netconvert_starts=1,monitoring_semantics='polling_50ms_possible_overshoot_preserved',user_approval_quote='SYNTHETIC TEST NOT HUMAN AUTHORIZATION',approved_at='SYNTHETIC')
        side.write_text(json.dumps(a)); e.check_approval(card,side)
        for key,value in [('status','NOT_APPROVED'),('synthetic_test_only',True),('card_sha256','0'*64),('scope','SUMO'),('max_netconvert_starts',2),('monitoring_semantics','hard_quota'),('user_approval_quote','')]:
            bad=dict(a); bad[key]=value; side.write_text(json.dumps(bad))
            with self.assertRaises(ValueError): e.check_approval(card,side)
        side.write_text(json.dumps(dict(a,status='NOT_APPROVED')))
    def test_wrong_command_environment_budget_and_binary_rejected(self):
        base=json.loads((HERE/'SG6_BUILD_request_card_draft.json').read_text()); base['kind']='SG6_BUILD_REQUEST_FINAL_OFFLINE'
        variants=[('argv',['sumo']),('attempt_id','BUILD02'),('output_dir',str(self.output)),('proposed_limits',dict(e.LIMITS,netconvert_starts=2)),('binary',dict(base['binary'],sha256='0'*64)),('environment_overrides',{'SUMO_HOME':'/bad'})]
        for i,(key,value) in enumerate(variants):
            bad=copy.deepcopy(base); bad[key]=value; p=self.case/f'bad{i}.json'; p.write_text(json.dumps(bad))
            with self.assertRaises(ValueError): e.validate_card(p,self.case/'missing',{'SUMO_HOME':e.SUMO_HOME})
        p=self.case/'env.json'; p.write_text(json.dumps(base))
        with self.assertRaisesRegex(ValueError,'Calling SUMO_HOME'): e.validate_card(p,self.case/'missing',{})
        with self.assertRaisesRegex(ValueError,'Dynamic-loader'): e.validate_card(p,self.case/'missing',{'SUMO_HOME':e.SUMO_HOME,'DYLD_INSERT_LIBRARIES':'x'})
    def test_pending_cumulative_audit_rejected(self):
        base=json.loads((HERE/'SG6_BUILD_request_card_draft.json').read_text()); base['kind']='SG6_BUILD_REQUEST_FINAL_OFFLINE'; p=self.case/'bad.json'; p.write_text(json.dumps(base))
        with self.assertRaisesRegex(ValueError,'Cumulative audit pending'): e.validate_card(p,self.case/'missing',{'SUMO_HOME':e.SUMO_HOME})
    def test_real_python_fake_process_timeout_and_stderr(self):
        # This executes only the current Python runtime, never a traffic binary.
        code="import sys,time;print('fake stdout',flush=True);print('fake stderr',file=sys.stderr,flush=True);time.sleep(20)"
        r=e._run_reserved(self.output,[sys.executable,'-c',code],str(self.case),dict(os.environ),{'synthetic_only':True},timeout=0.25,synthetic=True)
        self.assertEqual(r['status'],'terminal_timeout'); self.assertTrue(r['termination_requested']); self.assertTrue(r['stderr_nonempty']); self.assertLess(r['wallclock_s'],4)
    def test_real_python_fake_process_success(self):
        code="from pathlib import Path;Path('BUILD01/network.net.xml').write_text('<net/>');print('synthetic complete')"
        r=e._run_reserved(self.output,[sys.executable,'-c',code],str(self.case),dict(os.environ),{'synthetic_only':True},synthetic=True)
        self.assertEqual(r['status'],'completed_pending_compiled_review')

class Recorder(unittest.TextTestResult):
    def addSuccess(self,test): super().addSuccess(test); RESULTS.append({'test':test.id(),'status':'PASS'})
    def addFailure(self,test,err): super().addFailure(test,err); RESULTS.append({'test':test.id(),'status':'FAIL','error':self._exc_info_to_string(err,test)})
    def addError(self,test,err): super().addError(test,err); RESULTS.append({'test':test.id(),'status':'ERROR','error':self._exc_info_to_string(err,test)})

if __name__=='__main__':
    result=unittest.TextTestRunner(verbosity=2,resultclass=Recorder).run(unittest.defaultTestLoader.loadTestsFromTestCase(Tests))
    receipt={'status':'PASS' if result.wasSuccessful() else 'FAIL','tests_run':result.testsRun,'tests':RESULTS,'executor_sha256':e.digest(HERE/'build01_executor.py'),'test_script_sha256':e.digest(__file__),'real_simulator_starts':0,'python_fake_subprocesses':2,'real_netconvert_starts':0,'synthetic_only':True,'artifact_root':str(RUN),'limitations':['No real netconvert behavior tested','Polling caps can overshoot; not OS quota','SIGKILL/power loss leaves claim consumed; surviving child needs manual inspection']}
    e.durable_json(RUN/'test_receipt.json',receipt)
    sys.exit(0 if result.wasSuccessful() else 1)

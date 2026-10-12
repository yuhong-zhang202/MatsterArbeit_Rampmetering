"""Narrow fake/static budget regressions; never launches native SUMO."""
from copy import deepcopy
from pathlib import Path
from types import SimpleNamespace
import json
import tempfile
import unittest
from unittest.mock import patch
from src.candidate_a_native_smoke_budget_20261012 import profile
from src.candidate_a_native_smoke_budget_20261012.bridge import execute, _diagnostic_loop
from src.candidate_a_native_smoke_20261011.bridge_resources import ResourceWatchdog


class BudgetTests(unittest.TestCase):
    def test_bridge_body_and_target_stop_unchanged(self):
        old=(profile.ROOT/'src/candidate_a_native_smoke_runtime_fix_20261012/bridge.py').read_text()
        new=(profile.ROOT/'src/candidate_a_native_smoke_budget_20261012/bridge.py').read_text()
        self.assertEqual(new,old.replace('from src.candidate_a_native_smoke_runtime_fix_20261012.profile import','from src.candidate_a_native_smoke_budget_20261012.profile import'))
        self.assertIn('for t in range(1207):',new)
        self.assertIn("require(t==1206,'unexpected diagnostic pause')",new)
        self.assertEqual(profile.SPEC['end_s'],1207)
        self.assertFalse(profile.SPEC['automatic_continuation'])
        self.assertTrue(profile.SPEC['first_red_mandatory_pause'])
    def test_prepared_card_and_exact_resource_gate(self):
        card=profile.ROOT/profile.TASK/'engineering/packages'/profile.RUN/'card.json'
        c=profile.validate(card,require_environment=True)
        self.assertEqual(c['resources'],{'wall_limit_s':300,'startup_limit_s':60,'run_limit_bytes':300000000,'minimum_free_bytes':5000000000})
        for field,values in {'wall_limit_s':[180,301,True,300.0,None],'startup_limit_s':[61,60.0],'run_limit_bytes':[300000001],'minimum_free_bytes':[0]}.items():
            for value in values:
                with self.subTest(field=field,value=value):
                    changed=deepcopy(c);changed['resources'][field]=value
                    with patch.object(profile.json,'loads',return_value=changed):
                        with self.assertRaisesRegex(ValueError,'exact resource contract drift'):profile.validate(card)
        changed=deepcopy(c);changed['resources_provenance']['proposed_change']['after']=301
        with patch.object(profile.json,'loads',return_value=changed):
            with self.assertRaisesRegex(ValueError,'resource provenance drift'):profile.validate(card)
    def test_sync_gate_accepts200_under300_but_still_enforces_limit(self):
        with tempfile.TemporaryDirectory() as tmp:
            output=Path(tmp)
            conn=SimpleNamespace(trafficlight=SimpleNamespace())
            worker=SimpleNamespace(request_phase=lambda *args:None)
            proc=SimpleNamespace(poll=lambda:0)
            for limit,elapsed,error in [(180,200,'wall resource STOP'),(300,200,'native child exited'),(300,300,'native child exited'),(300,300.01,'wall resource STOP')]:
                with self.subTest(limit=limit,elapsed=elapsed),patch('src.candidate_a_native_smoke_budget_20261012.bridge.time.monotonic',return_value=elapsed):
                    with self.assertRaisesRegex(ValueError,error):_diagnostic_loop(conn,worker,None,output,{**profile.RESOURCES,'wall_limit_s':limit,'minimum_free_bytes':0},proc,0)
    def test_sampled_watchdog_same_new_limit_and_other_stops(self):
        class FakeProcess:
            def __init__(self):self.terminated=False
            def poll(self):return None
            def terminate(self):self.terminated=True
            def wait(self,timeout=None):return 0
            def kill(self):raise AssertionError('unexpected escalation')
        with tempfile.TemporaryDirectory() as tmp:
            for elapsed,free,limit_bytes,expected in [(299,5000000000,300000000,None),(300,5000000000,300000000,None),(300.01,5000000000,300000000,'WALL_LIMIT'),(299,4999999999,300000000,'DISK_RESERVE'),(299,5000000000,-1,'OUTPUT_BYTES')]:
                with self.subTest(elapsed=elapsed,expected=expected):
                    p=FakeProcess();w=ResourceWatchdog(p,Path(tmp),{**profile.RESOURCES,'run_limit_bytes':limit_bytes},0)
                    with patch('src.candidate_a_native_smoke_20261011.bridge_resources.time.monotonic',return_value=elapsed),patch('src.candidate_a_native_smoke_20261011.bridge_resources.shutil.disk_usage',return_value=SimpleNamespace(free=free)):w.check_once()
                    self.assertEqual(w.reason,expected);self.assertEqual(p.terminated,expected is not None);self.assertIsNone(w.error)
    def test_no_fresh_authorization_denies_before_native_or_raw(self):
        with patch('subprocess.Popen',side_effect=AssertionError('no native spawn')):
            with self.assertRaisesRegex(ValueError,'SMOKE04 native execution authorization missing'):execute(profile.ROOT/'fakecard',profile.ROOT/'fakerelease')
        self.assertFalse((profile.ROOT/profile.OUTPUT).parent.exists())
        self.assertFalse((profile.ROOT/profile.TASK/'AUTHORIZATION_NATIVE_EXECUTION.json').exists())
        self.assertFalse((profile.ROOT/profile.TASK/'engineering/EXECUTION_RELEASE.json').exists())


if __name__=='__main__':unittest.main()

"""Bounded resource-only offline checks; no SUMO, real raw, or arbitrary cap."""
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch
import tempfile,json,shutil,unittest
from src.candidate_a_t10_g5_y3_no_output_cap_20261013 import profile,bridge,budget,resources
from scripts.t10_g5_y3_audit_20261013_v1.core import audit_accounting

class Process:
 def __init__(self):self.stopped=False;self.returncode=None
 def poll(self):return self.returncode
 def terminate(self):self.stopped=True;self.returncode=-15
 def kill(self):self.stopped=True;self.returncode=-9
 def wait(self,timeout):return self.returncode

class ResourceTests(unittest.TestCase):
 def test_removed_bytes_with_wall_disk_and_unknown_STOPS(self):
    with tempfile.TemporaryDirectory()as tmp:
        p=Path(tmp)/'synthetic_large_sparse_file';f=p.open('wb');f.seek(300852929-1);f.write(b'0');f.close()
        self.assertGreater(p.stat().st_size,300000000)
        for label,free,now,error in [('bytes_disabled',6000000000,100,None),('wall',6000000000,301,None),('disk',4999999999,100,None),('unknown',6000000000,100,OSError('synthetic disk query failure'))]:
            process=Process();w=resources.ResourceWatchdog(process,Path(tmp),profile.resources(profile.RUN),0)
            with patch.object(resources.time,'monotonic',return_value=now),patch.object(resources.shutil,'disk_usage',side_effect=error,return_value=SimpleNamespace(free=free)):
                w.check_once()
            if label=='bytes_disabled':self.assertIsNone(w.reason);self.assertFalse(process.stopped)
            else:self.assertTrue(process.stopped);self.assertEqual(w.reason,{'wall':'WALL_LIMIT','disk':'DISK_RESERVE','unknown':'WATCHDOG_UNKNOWN'}[label])
    a=bridge.StepAdapter(lambda conn:None,750,1270)
    def unknown():raise ValueError('UNKNOWN synthetic observation')
    with self.assertRaisesRegex(ValueError,'UNKNOWN'):a._terminal_call(unknown)
    self.assertTrue(a.paused)
    self.assertIsNone(a.last_completed)
    lim=budget.effective_limits(profile.resources(profile.RUN),dict(remaining_s=300,remaining_bytes=None));self.assertIsNone(lim['run_limit_bytes']);self.assertEqual(lim['wall_limit_s'],300)

 def test_entire_bridge_watchdog_and_reader_only_allowed_resource_delta(self):
    root=profile.ROOT
    a=(root/'src/candidate_a_t10_g5_y3_audit_ready_20261013/bridge.py').read_text()
    expected=a.replace('from src.candidate_a_t10_g5_y3_audit_ready_20261013.profile import','from src.candidate_a_t10_g5_y3_no_output_cap_20261013.profile import').replace('from src.candidate_a_t10_g5_y3_audit_ready_20261013 import budget','from src.candidate_a_t10_g5_y3_no_output_cap_20261013 import budget').replace('from src.candidate_a_native_smoke_20261011.bridge_resources import ResourceWatchdog','from src.candidate_a_t10_g5_y3_no_output_cap_20261013.resources import ResourceWatchdog')
    expected=expected.replace("require(sum(p.stat().st_size for p in output.rglob('*') if p.is_file())<=resources['run_limit_bytes'],'output bytes STOP')","require(resources['run_limit_bytes'] is None or sum(p.stat().st_size for p in output.rglob('*') if p.is_file())<=resources['run_limit_bytes'],'output bytes STOP')").replace("require(bound['charged_raw_bytes']+sum(p.stat().st_size for p in output.parent.rglob('*') if p.is_file())<=budget.TOTAL_BYTES,'total raw resource STOP')","require(budget.TOTAL_BYTES is None or bound['charged_raw_bytes']+sum(p.stat().st_size for p in output.parent.rglob('*') if p.is_file())<=budget.TOTAL_BYTES,'total raw resource STOP')")
    self.assertEqual((root/'src/candidate_a_t10_g5_y3_no_output_cap_20261013/bridge.py').read_text(),expected)
    old=(root/'src/candidate_a_native_smoke_20261011/bridge_resources.py').read_text();self.assertEqual((root/'src/candidate_a_t10_g5_y3_no_output_cap_20261013/resources.py').read_text(),old.replace("elif sum(p.stat().st_size for p in self.output.rglob('*') if p.is_file())>self.limits['run_limit_bytes']","elif self.limits['run_limit_bytes'] is not None and sum(p.stat().st_size for p in self.output.rglob('*') if p.is_file())>self.limits['run_limit_bytes']"))
    old=(root/'scripts/t10_g5_y3_audit_20261013_v1/actual.py').read_text();expected=old.replace("'UA_T10_G5Y3_FIXED750_S17_02'","'UA_T10_G5Y3_FIXED750_S17_03'").replace("'run_limit_bytes':300000000","'run_limit_bytes':None").replace("'raw_bytes':300000000","'raw_bytes':None").replace("if elapsed>300 or m['bytes']>300000000 or before['charged_monitored_s']+elapsed>300 or before['charged_raw_bytes']+m['bytes']>300000000:","if elapsed>300 or before['charged_monitored_s']+elapsed>300:").replace('data/processed/t10_g5_y3_audit_ready_20261013_v1','data/processed/t10_g5_y3_no_output_cap_20261013_v1')
    self.assertEqual((root/'scripts/t10_g5_y3_no_output_cap_audit_20261013_v1/actual.py').read_text(),expected)
    self.assertTrue(all(v is None for v in audit_accounting([],[],[],1270)['accounting'].values()))

 def test_fresh03_host_bound_permission_and_old87_protection(self):
    root=profile.ROOT;old=Path('artifacts/t10_g5_y3_audit_ready_20261013_v1/engineering/packages_v4/UA_T10_G5Y3_FIXED750_S17_02/card.json');oc=json.loads((root/old).read_text());self.assertTrue(all(profile.sha(root/k)==v for k,v in oc['sources_sha256'].items()))
    donor=json.loads((root/profile.DONOR/'card.json').read_text());paths=set(profile.sources(root))|set(donor['prepared_input_sha256'])|{str(profile.NETWORK),str(profile.DONOR/'card.json'),str(old)}
    with tempfile.TemporaryDirectory()as tmp:
        fixture=Path(tmp).resolve()
        for rel in paths:
            p=fixture/rel;p.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(root/rel,p)
        card=profile.prepare(root=fixture);c=profile.validate(card,fixture,require_environment=True);self.assertIsNone(c['resources']['run_limit_bytes']);self.assertIsNone(c['spec']['total_resource_envelope']['raw_bytes']);self.assertFalse(c['SUMO_execution_authorized']);self.assertFalse(c['numerical_exception_authority']['enabled'])
        with patch.object(bridge,'ROOT',fixture),patch.object(bridge,'protected_worker',side_effect=AssertionError('must not import native worker'))as worker:
            with self.assertRaisesRegex(ValueError,'FUTURE_EXACT_NATIVE_AUTHORIZATION_MISSING'):bridge.execute(card,fixture/profile.TASK/'releases'/profile.RUN/'EXECUTION_RELEASE.json',root=fixture)
            worker.assert_not_called()
        self.assertFalse((fixture/profile.output(profile.RUN)).parent.exists());self.assertIsNone(budget.accounting(fixture)['remaining_bytes'])
    with self.assertRaises(ValueError):profile.spec('UA_T10_G5Y3_FIXED750_S17_02')
    with self.assertRaisesRegex(ValueError,'FOREIGN_CANDIDATE_CARD'):profile.validate(root/old)

if __name__=='__main__':unittest.main()

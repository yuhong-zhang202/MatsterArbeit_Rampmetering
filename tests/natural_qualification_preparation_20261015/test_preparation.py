"""Bounded preparation/ownership checks. All authority fixtures are temporary fakes."""
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch,Mock
from src.candidate_a_natural_service_20261015 import profile as p,budget as b,guardian as g

EVIDENCE=Path(os.environ.get('QUALIFICATION_TEST_EVIDENCE','/tmp/natural_qualification_test_evidence'))


def put(path,value):
    path.parent.mkdir(parents=True,exist_ok=True);path.write_text(json.dumps(value));return path


class Preparation(unittest.TestCase):
    def test_budget_is_independent_and_unknown_remains_reserved(self):
        with tempfile.TemporaryDirectory() as directory:
            root=Path(directory);old=dict(charged_monitored_s=475.645467625,remaining_s=124.354532375)
            with patch.object(b.previous,'accounting',return_value=old):
                self.assertIsNone(b.preview(root)['available_monitored_s'])
                with self.assertRaisesRegex(ValueError,'NOT_APPROVED'):b.accounting(root)
                authority=root/'FAKE_TEST_ONLY_AUTHORITY.txt';authority.write_text('temporary unittest fixture, not user authority')
                approval=dict(status='DIRECT_USER_APPROVED_INDEPENDENT_NUMERIC_BUDGET',scope_id=b.SCOPE,total_monitored_s=900,direct_user_authority=dict(path=authority.name,sha256=p.sha(authority)))
                put(root/b.APPROVAL,approval)
                result=b.accounting(root)
                self.assertEqual(result['remaining_s'],900);self.assertFalse(result['old_remainder_pooled']);self.assertEqual(result['prior_stage'],old)
                self.assertEqual(b.effective_limits(dict(wall_limit_s=900),result)['wall_limit_s'],870)
                authority.write_text('tampered')
                with self.assertRaisesRegex(ValueError,'AUTHORITY_DRIFT'):b.accounting(root)
                authority.write_text('temporary unittest fixture, not user authority')
                (root/p.TASK/'runs'/p.RUN).mkdir(parents=True)
                with self.assertRaisesRegex(ValueError,'EXHAUSTED_OR_RESERVED'):b.accounting(root)
                (root/p.RAW/p.RUN).mkdir(parents=True)
                with self.assertRaisesRegex(ValueError,'EXHAUSTED_OR_RESERVED'):b.accounting(root)

    def test_exact_preparation_and_missing_release_before_allocation(self):
        with tempfile.TemporaryDirectory() as directory:
            root=Path(directory).resolve()
            for relative in [p.NETWORK,p.USER,p.LEGACY_CARD,*[p.NATURAL/n for n in ('card.json','demand.rou.xml','scenario.sumocfg','scenario.add.xml')]]:
                target=root/relative;target.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(p.ROOT/relative,target)
            with patch.object(p,'sources',return_value={'fixture.py':'f'*64}):
                card=p.prepare(root);c=p.validate_prepared(card,root)
                self.assertFalse((root/p.RAW).exists())
                self.assertEqual(p.sha(card.parent/'demand.rou.xml'),p.sha(root/p.NATURAL/'demand.rou.xml'))
                c['output']='data/raw/WRONG/outputs';put(card,c)
                with self.assertRaisesRegex(ValueError,'OUTPUT_IDENTITY'):p.validate_prepared(card,root)
                c['output']=str(p.RAW/p.RUN/'outputs');put(card,c)
                cfg=card.parent/'scenario.sumocfg';cfg.write_text(cfg.read_text().replace('value="8"','value="7"'))
                c['prepared_input_sha256'][str(cfg.relative_to(root))]=p.sha(cfg);put(card,c)
                with self.assertRaisesRegex(ValueError,'PRECISION'):p.validate_prepared(card,root)
                cfg.write_text(cfg.read_text().replace('value="7"','value="8"'))
                c['prepared_input_sha256'][str(cfg.relative_to(root))]=p.sha(cfg);put(card,c)
                with patch.object(p,'sources',return_value={'fixture.py':'e'*64}):
                    with self.assertRaisesRegex(ValueError,'SOURCE_DRIFT'):p.validate_prepared(card,root)
            # Use actual root only for read-only absent-authority gates. No Popen or raw mkdir may occur.
            from src.candidate_a_natural_service_20261015 import bridge
            with patch.object(p,'validate_prepared',return_value={}),patch.object(g.subprocess,'Popen') as spawn,patch.object(bridge,'protected_worker') as worker:
                with self.assertRaisesRegex(ValueError,'NOT_APPROVED'):g.execute_guarded('unused-card','unused-release')
                with self.assertRaisesRegex(ValueError,'NOT_APPROVED'):bridge.execute('unused-card','unused-release')
                spawn.assert_not_called();worker.assert_not_called()
            with self.assertRaisesRegex(ValueError,'OUTER_GUARDIAN'):g.require_worker_context('unused','unused')

    def test_spawn_hook_persists_unknown_and_wrong_group_before_stop(self):
        with tempfile.TemporaryDirectory() as directory:
            root=Path(directory);card=root/'card';release=root/'release';card.write_text('test');release.write_text('test')
            worker=dict(pid=10,pgid=10,sid=10,status='OBSERVED')
            for name,native in [('same',dict(pid=11,pgid=10,sid=10,status='OBSERVED')),('wrong',dict(pid=11,pgid=11,sid=11,status='OBSERVED')),('unknown',dict(pid=11,pgid=None,sid=None,status='UNKNOWN'))]:
                output=root/name;output.mkdir();proc=Mock(pid=11);proc.poll.return_value=None
                with patch.object(g,'require_worker_context',return_value={'guardian_pid':9}),patch.object(g,'identity',side_effect=[worker,native]):
                    if name=='same':self.assertTrue(g.record_native_identity(proc,output,'test',card,release)['ownership_verified'])
                    else:
                        with self.assertRaisesRegex(ValueError,'UNKNOWN_OR_MISMATCH'):g.record_native_identity(proc,output,'test',card,release)
                        row=json.loads((output/'owned_process_identity.json').read_text());self.assertFalse(row['ownership_verified']);self.assertEqual(row['native'],native)
            # A denied inventory remains UNKNOWN, but cannot leave a live,
            # directly owned worker/session running beyond the deadline.
            proc=Mock(pid=10);proc.poll.return_value=None
            with patch.object(g.subprocess,'Popen',return_value=proc),patch.object(g,'identity',return_value=worker),patch.object(g,'group_members',side_effect=PermissionError('fixture denied inventory')),patch.object(g.os,'killpg') as kill,patch.object(g.time,'monotonic',side_effect=[0,2,3]):
                result=g.supervise(['fake'],{},root,inner_s=1,cleanup_s=1,identity_path=root/'missing',run='test',card_sha='card',release_sha='release',stdout=None,stderr=None)
                kill.assert_called_once_with(10,g.signal.SIGKILL)
                self.assertIsNone(result['group_cleanup']['no_live_owned_members'])

    def test_real_python_group_normal_timeout_and_early_exit(self):
        EVIDENCE.mkdir(parents=True,exist_ok=True)
        worker_code='''import json,os,subprocess,sys,time
from pathlib import Path
child=subprocess.Popen([sys.executable,"-c","import time;time.sleep("+("0.12" if sys.argv[1]=="normal" else "30")+")"])
me=dict(pid=os.getpid(),pgid=os.getpgid(0),sid=os.getsid(0),status="OBSERVED")
native=dict(pid=child.pid,pgid=os.getpgid(child.pid),sid=os.getsid(child.pid),status="OBSERVED")
Path(sys.argv[2]).write_text(json.dumps(dict(run_id="test",card_sha256="card",release_sha256="release",worker=me,native=native,ownership_verified=True)))
if sys.argv[1]=="early":os._exit(7)
child.wait()
'''
        for mode in ('normal','timeout','early'):
            folder=EVIDENCE/mode;folder.mkdir(exist_ok=False);identity=folder/'identity.json'
            with (folder/'stdout.log').open('xb') as out,(folder/'stderr.log').open('xb') as err:
                command=[sys.executable,'-c',worker_code,mode,str(identity)]
                put(folder/'command.json',command)
                receipt=g.supervise(command,dict(os.environ),p.ROOT,inner_s=.6,cleanup_s=.6,identity_path=identity,run='test',card_sha='card',release_sha='release',stdout=out,stderr=err)
            put(folder/'guardian_receipt.json',receipt)
            self.assertTrue(receipt['native_identity_verified'],receipt)
            self.assertIs(receipt['group_cleanup']['no_live_owned_members'],True,receipt)
            self.assertEqual(receipt['overshoot_s'],0,receipt)
            expected={'normal':'WORKER_EXITED','timeout':'INNER_WALL_DEADLINE','early':'WORKER_EXITED_WITH_LIVE_OWNED_MEMBERS'}
            self.assertEqual(receipt['stop_reason'],expected[mode],receipt)


if __name__=='__main__':unittest.main()

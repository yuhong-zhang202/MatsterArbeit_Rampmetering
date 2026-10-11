"""Few XML-driven offline tests; no native binary/connection or ignored raw."""
from pathlib import Path
import importlib.util,json,tempfile,time,unittest
from types import SimpleNamespace
from unittest.mock import patch
import xml.etree.ElementTree as ET
from src.candidate_a_native_smoke_selfloop_fix_20261011.profile import ROOT,TASK,RUN,OUTPUT,stage_package,selfloop_warning_indices,validate_release,base
from src.candidate_a_native_smoke_selfloop_fix_20261011.bridge import _diagnostic_loop,execute
from src.candidate_a_native_smoke_20261011.bridge_logs import LogCapture

spec=importlib.util.spec_from_file_location('original_fake_fixture',ROOT/'tests/candidate_a_native_smoke_bridge_20261011/test_bridge.py');fixture=importlib.util.module_from_spec(spec);spec.loader.exec_module(fixture)


class XMLFakeConnection(fixture.EmptyFakeConnection):
    """Replay one sourced phase successor/event, not native vehicle dynamics."""
    def __init__(self,additional):
        super().__init__();self.programs={node.get('programID'):list(node) for node in ET.parse(additional).getroot().findall('tlLogic')}
    def request(self,tls,records,t,method,value):
        self.requests.append((t,method,value));records.append({'time_s':t,'method':method,'value':value})
        if method=='setProgram':self.program=value
        else:self.phase=value
        if self.program=='A_OPEN':self.state='G';self.switch=999999
        else:
            phase=self.programs[self.program][self.phase];self.state=phase.get('state');self.switch=t+int(phase.get('duration'))
    def simulationStep(self,end):
        if self.program!='A_OPEN' and self.time>=self.switch:
            phases=self.programs[self.program];old=phases[self.phase];self.phase=int(old.get('next',str((self.phase+1)%len(phases))).split()[0]);new=phases[self.phase]
            self.state=new.get('state');self.switch+=int(new.get('duration'))
        self.time=end


class SelfloopTests(unittest.TestCase):
    def test_exact_source_predicate_old17_new0_default_and_single_phase(self):
        old=ET.parse(ROOT/base.OLD/'scenario.add.xml').getroot();self.assertEqual(sum(len(selfloop_warning_indices(p)) for p in old.findall('tlLogic')),17)
        self.assertEqual(selfloop_warning_indices(ET.fromstring('<tlLogic><phase next="0"/></tlLogic>')),[])
        self.assertEqual(selfloop_warning_indices(ET.fromstring('<tlLogic><phase/><phase/><phase/></tlLogic>')),[])
        self.assertEqual(selfloop_warning_indices(ET.fromstring('<tlLogic><phase next="1"/><phase next="1"/></tlLogic>')),[1])
        with tempfile.TemporaryDirectory() as tmp:
            pkg=Path(tmp)/'pkg';stage_package(ROOT,pkg,Path(tmp)/'unallocated')
            new=ET.parse(pkg/'scenario.add.xml').getroot();self.assertEqual([p.get('programID') for p in new.findall('tlLogic')],['CA_C8','CA_C24']);self.assertEqual(sum(len(selfloop_warning_indices(p)) for p in new.findall('tlLogic')),0)
    def test_new_package_demand_controls_paths_hold_semantics(self):
        with tempfile.TemporaryDirectory() as tmp:
            pkg=Path(tmp)/'pkg';out=Path(tmp)/'unallocated';stage_package(ROOT,pkg,out)
            self.assertFalse(out.exists());self.assertEqual((pkg/'demand.rou.xml').read_bytes(),(ROOT/base.OLD/'demand.rou.xml').read_bytes())
            cfg=ET.parse(pkg/'scenario.sumocfg').getroot();self.assertEqual(cfg.find('./time/end').get('value'),'1207');self.assertEqual(cfg.find('./random_number/seed').get('value'),'17')
            self.assertEqual(cfg.find('./report/no-warnings').get('value'),'false');self.assertEqual(cfg.find('./report/aggregate-warnings').get('value'),'-1')
            x=ET.parse(pkg/'scenario.add.xml').getroot();hold=x.find("tlLogic[@programID='CA_C8']");control=x.find("tlLogic[@programID='CA_C24']")
            self.assertEqual([(p.get('duration'),p.get('next')) for p in hold],[('3','1'),('3','2'),('600','0')]);self.assertEqual(sum(int(p.get('duration')) for p in hold),606)
            self.assertEqual([(p.get('duration'),p.get('next')) for p in control],[('3','1'),('3','2'),('18','0')])
    def test_xml_driven_hold_to1200_first_red1207_forces_pause(self):
        with tempfile.TemporaryDirectory() as tmp:
            pkg=Path(tmp)/'pkg';out=Path(tmp)/'fake_output';stage_package(ROOT,pkg,out);out.mkdir()
            conn=XMLFakeConnection(pkg/'scenario.add.xml');worker=SimpleNamespace(observe=conn.observe,request_phase=conn.request);capture=LogCapture(out)
            adapter=_diagnostic_loop(conn,worker,capture,out,{'wall_limit_s':180,'minimum_free_bytes':0,'run_limit_bytes':300000000},fixture.FakeProcess(),time.monotonic())
            rows=[json.loads(line) for line in (out/'post_steps.jsonl').read_text().splitlines()]
            self.assertTrue(all(r['motion']=='y' for r in rows[600:603]));self.assertTrue(all(r['motion']=='r' for r in rows[603:1200]));self.assertEqual(rows[1200]['motion'],'G');self.assertEqual(rows[1206]['motion'],'r')
            self.assertEqual(conn.time,1207);self.assertEqual(conn.switch,1224);self.assertTrue(adapter.paused);self.assertEqual(adapter.ledger.E,0);self.assertEqual(rows[-1]['status'],'MANDATORY_REVIEW_PAUSE_NO_AUTOMATIC_CONTINUATION')
            capture.close_handles()
    def test_new_authorization_missing_before_native_despite_old_identity(self):
        self.assertFalse((ROOT/TASK/'AUTHORIZATION_NATIVE_EXECUTION.json').exists());self.assertFalse((ROOT/TASK/'engineering/EXECUTION_RELEASE.json').exists())
        with patch('subprocess.Popen',side_effect=AssertionError('native must not spawn')):
            with self.assertRaisesRegex(ValueError,'SMOKE02 native execution authorization missing'):execute(ROOT/'fakecard.json',ROOT/'old_release.json')
        self.assertFalse((ROOT/OUTPUT).parent.exists())
    def test_original_warning_remains_stop_with_new_loop(self):
        warning=(ROOT/'artifacts/candidate_a_native_smoke_execution_20261011_v1/engineering/RUNTIME_NATIVE_WARNING_EXTRACT.txt').read_bytes()
        with tempfile.TemporaryDirectory() as tmp:
            pkg=Path(tmp)/'pkg';out=Path(tmp)/'fake_output';stage_package(ROOT,pkg,out);out.mkdir();c=LogCapture(out);c.paths['sumo_stderr.log'].write_bytes(warning)
            conn=XMLFakeConnection(pkg/'scenario.add.xml');worker=SimpleNamespace(observe=conn.observe,request_phase=conn.request)
            with self.assertRaisesRegex(ValueError,'stderr before motion'):_diagnostic_loop(conn,worker,c,out,{'wall_limit_s':180,'minimum_free_bytes':0,'run_limit_bytes':300000000},fixture.FakeProcess(),time.monotonic())
            self.assertEqual(conn.time,0);self.assertFalse((out/'step_ack.jsonl').exists());c.close_handles()

if __name__=='__main__':unittest.main()

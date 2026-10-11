"""Real file binding + fake connection/process only. No native launches."""
from pathlib import Path
from types import SimpleNamespace
import json
import tempfile
import time
import unittest
from unittest.mock import patch
from src.candidate_a_native_smoke_20261011.bridge_card import ROOT,OLD,NETWORK,stage_package,validate_release,RUN
from src.candidate_a_native_smoke_20261011.bridge_logs import LogCapture
from src.candidate_a_native_smoke_20261011.bridge import admission,diagnostic_loop,execute


class FakeProcess:
    def __init__(self, returncode=None):self.returncode=returncode
    def poll(self):return self.returncode


class EmptyFakeConnection:
    def __init__(self):
        self.time=0;self.program='A_OPEN';self.phase=0;self.state='G';self.switch=999999;self.requests=[]
        self.simulation=SimpleNamespace(getTime=lambda:self.time,getPendingVehicles=lambda:(),getArrivedIDList=lambda:(),getDepartedIDList=lambda:(),getCollidingVehiclesNumber=lambda:0,getStartingTeleportNumber=lambda:0,getEndingTeleportNumber=lambda:0)
        self.vehicle=SimpleNamespace(getIDList=lambda:(),getLoadedIDList=lambda:())
        self.lane=SimpleNamespace(getLength=lambda lane:{'ramp_storage_0':204.49,':urban_diverge_1_0':113.08,':ramp_mid_0_0':81.98}[lane],getLastStepVehicleIDs=lambda lane:())
        self.trafficlight=SimpleNamespace(getControlledLinks=lambda tls:((('ramp_storage_0','ramp_accel_0',':ramp_mid_0_0'),),),getProgram=lambda tls:self.program,getPhase=lambda tls:self.phase,getRedYellowGreenState=lambda tls:self.state,getNextSwitch=lambda tls:self.switch)
    def simulationStep(self, end):
        if self.time>=self.switch:
            self.phase=1 if self.phase==0 else 2;self.state='y' if self.phase==1 else 'r';self.switch+=3 if self.phase==1 else (2 if self.program=='CA_C8' else 18)
        self.time=end
    def observe(self, conn):return [],{'ramp_storage_0':(),':urban_diverge_1_0':()}, {}, {'available':True}
    def request(self, tls, records, t, method, value):
        self.requests.append((t,method,value));records.append({'time_s':t,'method':method,'value':value})
        if method=='setProgram':self.program=value
        else:self.phase=value
        self.state=['G','y','r'][self.phase]
        self.switch=t+([3,3,2 if self.program=='CA_C8' else 18][self.phase] if self.program!='A_OPEN' else 999999)


class BridgeTests(unittest.TestCase):
    def capture(self, tmp):return LogCapture(Path(tmp))
    def test_missing_authorization_denies_before_native_or_raw(self):
        with patch('subprocess.Popen',side_effect=AssertionError('native spawn forbidden')):
            with self.assertRaisesRegex(ValueError,'authorization missing'):execute(ROOT/'fakecard.json',ROOT/'fakerelease.json')
        self.assertFalse((ROOT/'data/raw/candidate_a_native_smoke_bridge_20261011_v1'/RUN).exists())
    def test_public_package_copy_paths_and_phase_semantics(self):
        import xml.etree.ElementTree as ET
        with tempfile.TemporaryDirectory() as tmp:
            package=Path(tmp)/'package';out=Path(tmp)/'not_allocated_output';inputs=stage_package(ROOT,package,out)
            self.assertFalse(out.exists());self.assertEqual((package/'demand.rou.xml').read_bytes(),(ROOT/OLD/'demand.rou.xml').read_bytes())
            cfg=ET.parse(package/'scenario.sumocfg').getroot()
            self.assertEqual(cfg.find('./time/end').get('value'),'1207')
            self.assertEqual(cfg.find('./report/no-warnings').get('value'),'false')
            self.assertEqual(cfg.find('./report/aggregate-warnings').get('value'),'-1')
            self.assertNotIn('/CA_FIXED_R300_S17_A07/',(package/'scenario.sumocfg').read_text())
    def test_ordinary_info_late_is_whole_prefix_not_step_warning(self):
        with tempfile.TemporaryDirectory() as tmp:
            c=self.capture(tmp);c.snapshot(0,1,'AFTER_SIMULATION_STEP_ACK')
            with c.paths['sumo_stdout.log'].open('ab') as f:f.write(b'Simulation ended.\n')
            r=c.finalize(FakeProcess(0),1,True)
            self.assertEqual(r['status'],'BOUND_NO_OBSERVED_NATIVE_MESSAGE');self.assertGreater(r['late_bytes']['sumo_stdout.log'],0)
            c.close_handles()
    def test_late_critical_and_unknown_finalization_fail(self):
        for case in ['late_stderr','late_error','unknown_exit','nonzero_exit']:
            with self.subTest(case=case),tempfile.TemporaryDirectory() as tmp:
                c=self.capture(tmp);c.snapshot(0,1,'AFTER_SIMULATION_STEP_ACK')
                if case not in ['unknown_exit','nonzero_exit']:
                    name='sumo_stderr.log' if case=='late_stderr' else 'sumo_error.log'
                    with c.paths[name].open('ab') as f:f.write(b'Warning: emergency braking\n')
                    self.assertEqual(c.finalize(FakeProcess(0),1,True)['status'],'UNKNOWN_OR_NATIVE_MESSAGE')
                else:
                    with self.assertRaisesRegex(ValueError,'EOF'):c.finalize(FakeProcess(1) if case=='nonzero_exit' else FakeProcess(),1,case=='nonzero_exit')
                c.close_handles()
    def test_replacement_shrink_and_partial_stderr_deny(self):
        for case in ['replace','shrink','utf8','line']:
            with self.subTest(case=case),tempfile.TemporaryDirectory() as tmp:
                c=self.capture(tmp);p=c.paths['sumo_stderr.log']
                if case=='shrink':
                    p.write_bytes(b'Warning\n');c.snapshot(0,1,'AFTER_SIMULATION_STEP_ACK');p.write_bytes(b'')
                elif case=='replace':p.unlink();p.write_bytes(b'')
                elif case=='utf8':p.write_bytes(b'\xe4')
                else:p.write_bytes(b'partial')
                with self.assertRaises((ValueError,UnicodeDecodeError)):c.snapshot(1,2,'AFTER_SIMULATION_STEP_ACK')
                c.close_handles()
    def test_source_cursor_contains_startup_and_pre_control_bytes(self):
        with tempfile.TemporaryDirectory() as tmp:
            c=self.capture(tmp);c.paths['sumo_stderr.log'].write_bytes(b'Warning: startup\n')
            r=c.snapshot(0,0,'STARTUP_CONNECT_ACK')
            self.assertEqual(r['streams']['sumo_stderr.log']['byte_start'],0)
            with self.assertRaisesRegex(ValueError,'nonempty'):c.adapter_warning(r)
            c.close_handles()
    def test_green_admission_denied_before_any_request(self):
        conn=EmptyFakeConnection();conn.time=1200;conn.program='CA_C8';conn.phase=2;conn.state='r';conn.switch=1201
        def denied(c):return [],{'ramp_storage_0':(),':urban_diverge_1_0':()}, {}, {'available':False}
        with self.assertRaisesRegex(ValueError,'receiver denies'):admission(conn,1200,denied)
        self.assertEqual(conn.requests,[])
    def test_watchdog_kills_owned_blocked_child_only(self):
        from src.candidate_a_native_smoke_20261011.bridge_resources import ResourceWatchdog
        class HungFakeProcess(FakeProcess):
            def __init__(self):super().__init__();self.terminated=False;self.killed=False
            def terminate(self):self.terminated=True
            def kill(self):self.killed=True;self.returncode=-9
            def wait(self,timeout):
                if not self.killed:raise TimeoutError('fake blocked child')
                return self.returncode
        with tempfile.TemporaryDirectory() as tmp:
            proc=HungFakeProcess();watch=ResourceWatchdog(proc,Path(tmp),{'wall_limit_s':1,'minimum_free_bytes':0,'run_limit_bytes':1},time.monotonic()-2)
            watch.check_once();self.assertEqual(watch.reason,'WALL_LIMIT');self.assertTrue(proc.terminated and proc.killed)
    def test_full_fake_bridge_stops_1207_no_auto_continuation(self):
        with tempfile.TemporaryDirectory() as tmp:
            c=self.capture(tmp);conn=EmptyFakeConnection();worker=SimpleNamespace(observe=conn.observe,request_phase=conn.request)
            adapter=diagnostic_loop(conn,worker,c,Path(tmp),{'wall_limit_s':180,'minimum_free_bytes':0,'run_limit_bytes':300000000},FakeProcess(),time.monotonic())
            self.assertEqual(conn.time,1207);self.assertTrue(adapter.paused);self.assertEqual(adapter.ledger.E,0)
            self.assertAlmostEqual(adapter.ledger.accounting()['C'],7/12)
            self.assertEqual([(t,m,v) for t,m,v in conn.requests if t==1200],[(1200,'setProgram','CA_C24'),(1200,'setPhase',0)])
            lines=[json.loads(line) for line in (Path(tmp)/'post_steps.jsonl').read_text().splitlines()]
            self.assertEqual(lines[603]['motion'],'r');self.assertEqual(lines[-1]['status'],'MANDATORY_REVIEW_PAUSE_NO_AUTOMATIC_CONTINUATION')
            self.assertEqual(c.records[0]['streams']['sumo_stderr.log']['byte_start'],0)
            c.close_handles()

if __name__=='__main__':unittest.main()

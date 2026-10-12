"""New cycle/checkpoint semantics only. XML-driven fake; never native execution."""
import importlib.util,json,tempfile,time,unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch
from src.candidate_a_native_budget_cycles_20261012 import profile
from src.candidate_a_native_budget_cycles_20261012.adapter import StepAdapter,DiagnosticStop,ROUTES,STORAGE,INGRESS,INTERNAL
from src.candidate_a_native_budget_cycles_20261012.bridge import _diagnostic_loop,checkpoint,admission,execute
from src.candidate_a_native_smoke_20261011.bridge_logs import LogCapture
from src.candidate_a_qualification_20261008.safety import Vehicle
sp=importlib.util.spec_from_file_location('old_xml_fixture',profile.ROOT/'tests/candidate_a_native_smoke_selfloop_fix_20261011/test_selfloop.py');fixture=importlib.util.module_from_spec(sp);sp.loader.exec_module(fixture)


class World(fixture.XMLFakeConnection):
    def __init__(self,xml,empty=False,fail=None):
        super().__init__(xml);self.fail=fail;self.empty=empty;self.enter={};self.arrived=[];self.vspeed={'M_flow.0':5.,**({} if empty else {f'R_flow.{i}':0. for i in range(3)})}
        self.vehicle=SimpleNamespace(getIDList=lambda:tuple(self.vspeed),getLoadedIDList=lambda:tuple(self.vspeed),getTypeID=lambda v:'technical_passenger',getRoute=lambda v:ROUTES[v.split('_')[0]],getSpeedMode=lambda v:31,getLaneChangeMode=lambda v:1621,
            getAccel=lambda v:2.6,getDecel=lambda v:4.5,getEmergencyDecel=lambda v:9.,getTau=lambda v:1.,getActionStepLength=lambda v:1.,getImperfection=lambda v:.5,getMaxSpeed=lambda v:55.55555555555556,getSpeed=lambda v:self.vspeed[v],getAcceleration=lambda v:0.,getLaneID=self.lane_id)
        self.lane.getLastStepVehicleIDs=lambda lane:tuple(v for v in self.vspeed if self.lane_id(v)==lane)
        self.simulation.getArrivedIDList=lambda:tuple(self.arrived)
        self.trafficlight.setProgram=lambda tls,v:self.request(self.trafficlight,[],self.time,'setProgram',v)
        self.trafficlight.setPhase=lambda tls,v:self.request(self.trafficlight,[],self.time,'setPhase',v)
    def lane_id(self,v):
        if v.startswith('M'):return 'main_up_0'
        if v not in self.enter:return STORAGE
        return INTERNAL if self.time-self.enter[v]<4 else 'ramp_accel_0'
    def observe(self,conn):
        ids={l:self.lane.getLastStepVehicleIDs(l) for l in (STORAGE,INGRESS)}
        states=[Vehicle(v,'storage',190.,self.vspeed[v],5.,2.5,2.6,4.5,1.,1.,'technical_passenger') for v in ids[STORAGE]]
        denied=self.fail=='receiver' and self.time==1224
        return states,ids,{v:{} for v in self.lane.getLastStepVehicleIDs(INTERNAL)},{'available':None if self.fail=='unknown_receiver' and self.time==1224 else not denied}
    def simulationStep(self,end):
        begin=self.time;super().simulationStep(end);self.arrived=[]
        if not self.empty and begin in (1200,1224,1248):self.enter[f'R_flow.{(begin-1200)//24}']=end
        if self.fail=='red_crossing' and begin==1206 and not self.empty:self.enter['R_flow.1']=end
        if self.fail=='braking' and begin==1200:self.vspeed['M_flow.0']=0.
        if self.fail=='arrived' and begin==1200:del self.vspeed['M_flow.0'];self.arrived=['M_flow.0']
        if self.fail=='phase' and begin==1200:self.phase=1;self.state='y'
    def phase_request(self,tls,records,t,m,v):
        record={'time_s':t,'method':m,'value':v,'call_completed':False};records.append(record);getattr(tls,m)(tls,v);record['call_completed']=True


def warn(t):return {'time_begin_s':t,'time_end_s':t+1,'coverage':'CALLER_DECLARED_INTERVAL','source':'PURE_FAKE','byte_start':0,'byte_end':0,'text':''}


class CycleTests(unittest.TestCase):
    def setup_world(self,tmp,**kwargs):
        pkg=Path(tmp)/'package';out=Path(tmp)/'output';profile.stage_package(profile.ROOT,pkg,out);out.mkdir();world=World(pkg/'scenario.add.xml',**kwargs);cap=LogCapture(out)
        return world,cap,out
    def loop(self,w,c,out,adapter=None):return _diagnostic_loop(w,SimpleNamespace(observe=w.observe,request_phase=w.phase_request),c,out,{'wall_limit_s':300,'minimum_free_bytes':0,'run_limit_bytes':300000000},fixture.fixture.FakeProcess(),time.monotonic(),adapter)
    def test_full_xml_cycles_checkpoint_exact_boundaries_and_actual_N_not_nominal(self):
        with tempfile.TemporaryDirectory() as tmp:
            w,c,out=self.setup_world(tmp)
            try:a=self.loop(w,c,out)
            finally:c.close_handles()
            rows=[json.loads(x) for x in (out/'post_steps.jsonl').read_text().splitlines()]
            self.assertEqual(w.time,1272);self.assertTrue(a.paused and a.checkpoint_verified);self.assertEqual((w.phase,w.state,w.switch),(2,'r',1272));self.assertEqual(len(a.ledger.rows),3)
            self.assertEqual(a.ledger.accounting()['C'],6);self.assertEqual(a.ledger.E,6);self.assertEqual(a.ledger.N,3);self.assertEqual([r['N_G'] for r in a.ledger.rows],[1,1,1]);self.assertTrue(all(r['completed'] for r in a.ledger.rows))
            for t in (1224,1248):
                self.assertEqual(rows[t]['phase_observation']['state_before'],'r');self.assertEqual(rows[t]['phase_observation']['next_switch_before_s'],t);self.assertEqual(rows[t]['motion'],'G');self.assertEqual(rows[t]['phase_observation']['state_after'],'G')
            self.assertEqual([r['time_s'] for r in map(json.loads,(out/'admission.jsonl').read_text().splitlines())],[1200,1224,1248])
            self.assertEqual([r for r in w.requests if r[0]>=1200],[(1200,'setProgram','CA_C24'),(1200,'setPhase',0)])
            cp=json.loads((out/'first_red_checkpoint.json').read_text());self.assertEqual(cp['time_s'],1207);self.assertIn('FINAL_EOF_REQUIRED',cp['log_scope']);self.assertEqual(cp['accounting']['E'],0)
            self.assertFalse((out/'bridge_receipt.json').exists(),'pure loop is not native EOF or execution receipt')
            self.assertEqual([r['motion'] for r in rows[1200:1206]],['G']*3+['y']*3)
    def test_empty_observed_N_zero_is_not_missing_or_partial_completion(self):
        with tempfile.TemporaryDirectory() as tmp:
            w,c,out=self.setup_world(tmp,empty=True)
            try:a=self.loop(w,c,out)
            finally:c.close_handles()
            self.assertEqual(a.ledger.N,0);self.assertEqual(a.ledger.E,6);self.assertEqual(len(a.ledger.rows),3)
        a=StepAdapter(lambda c:None);self.assertIsNone(a.last_end);self.assertEqual(a.ledger.N,0,'unobserved initialized zero must not be exported as observed N')
    def test_receiver_denied_or_unknown_before_second_native_green(self):
        for failure in ('receiver','unknown_receiver'):
            with self.subTest(failure=failure),tempfile.TemporaryDirectory() as tmp:
                w,c,out=self.setup_world(tmp,fail=failure);a=StepAdapter(w.observe)
                try:
                    with self.assertRaisesRegex(ValueError,'UNKNOWN_POST_RECEIVER' if failure=='unknown_receiver' else 'receiver denies'):self.loop(w,c,out,a)
                finally:c.close_handles()
                self.assertEqual(w.time,1224);self.assertEqual(w.state,'r');self.assertEqual(a.ledger.E,2);self.assertTrue(a.ledger.rows[0]['completed']);self.assertEqual(a.ledger.N,1)
    def test_missing_or_failed_checkpoint_blocks_continuation(self):
        with tempfile.TemporaryDirectory() as tmp:
            w,c,out=self.setup_world(tmp);a=StepAdapter(w.observe)
            try:
                with patch('src.candidate_a_native_budget_cycles_20261012.bridge.checkpoint',side_effect=OSError('durable checkpoint failure')):
                    with self.assertRaisesRegex(OSError,'checkpoint failure'):self.loop(w,c,out,a)
                self.assertEqual(w.time,1207);self.assertTrue(a.checkpoint_pending);self.assertFalse(a.checkpoint_verified)
                with self.assertRaisesRegex(DiagnosticStop,'CHECKPOINT_NOT_RELEASED'):a.prepare_step(w,1207)
            finally:c.close_handles()
    def test_anomalies_keep_terminal_accounted_observed_prefix(self):
        for failure,reason in [('red_crossing','RED_CROSSING'),('braking','ORDINARY_BRAKING_EXCEEDED'),('phase','PHASE_MISMATCH')]:
            with self.subTest(failure=failure),tempfile.TemporaryDirectory() as tmp:
                w,c,out=self.setup_world(tmp,fail=failure);a=StepAdapter(w.observe)
                try:
                    with self.assertRaisesRegex(DiagnosticStop,reason):self.loop(w,c,out,a)
                finally:c.close_handles()
                self.assertTrue(a.paused);self.assertEqual(a.last_completed,a.last_end);self.assertEqual(a.ledger.E,0);self.assertFalse(a.ledger.rows[0]['completed'])
                if failure=='red_crossing':self.assertEqual(a.ledger.N,2)
    def test_braking_coverage_serializes_arrived_exclusions_and_actual_values(self):
        with tempfile.TemporaryDirectory() as tmp:
            w,c,out=self.setup_world(tmp,fail='arrived')
            try:a=self.loop(w,c,out)
            finally:c.close_handles()
            r=a.receipts[1200]['braking_observation'];self.assertEqual(r['arrived_ids'],['M_flow.0']);self.assertEqual(r['excluded_before_only_ids'],['M_flow.0']);self.assertNotIn('M_flow.0',r['speed_difference_ids']);self.assertNotIn('M_flow.0',r['after_acceleration_ids']);self.assertEqual(set(r['actual_acceleration_m_s2']),set(r['after_acceleration_ids']));self.assertEqual(set(r['speed_difference_m_s2']),set(r['speed_difference_ids']))
    def test_native_message_is_not_suppressed(self):
        with tempfile.TemporaryDirectory() as tmp:
            w,c,out=self.setup_world(tmp);c.paths['sumo_stderr.log'].write_bytes(b'Warning: collision\n')
            try:
                with self.assertRaisesRegex(ValueError,'stderr before motion'):self.loop(w,c,out)
            finally:c.close_handles()
            self.assertEqual(w.time,0);self.assertFalse((out/'step_ack.jsonl').exists())
    def test_four_exact_budgets_and_preserved_other_caps(self):
        self.assertEqual(tuple(profile.RUNS.values()),(300,360,420,480))
        for run,cap in profile.RUNS.items():
            self.assertEqual(profile.resources(run),{'wall_limit_s':cap,'startup_limit_s':60,'run_limit_bytes':300000000,'minimum_free_bytes':5000000000});self.assertEqual(profile.spec(run)['end_s'],1272)
        with self.assertRaises(ValueError):profile.resources('CA_NATIVE_PHASE_R300_S17_SMOKE04')
    def test_missing_card_denies_before_allocation_or_native(self):
        with patch('subprocess.Popen',side_effect=AssertionError('forbidden native')):
            with self.assertRaises(FileNotFoundError):execute(profile.ROOT/'absent_series_card.json',profile.ROOT/'absent_series_release.json')
        self.assertTrue(all(not (profile.ROOT/profile.output(run)).parent.exists() for run in profile.RUNS))

if __name__=='__main__':unittest.main()

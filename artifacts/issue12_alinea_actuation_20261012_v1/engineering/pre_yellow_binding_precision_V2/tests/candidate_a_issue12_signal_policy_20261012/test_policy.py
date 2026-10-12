"""Few bounded policy/clock/count/arrival fixtures, not native vehicle physics."""
from pathlib import Path
from types import SimpleNamespace
from dataclasses import replace
import importlib.util,json,tempfile,time,unittest
from src.candidate_a_issue12_signal_policy_20261012 import profile
from src.candidate_a_issue12_signal_policy_20261012.policy import Ledger,quantize,yellow_scope,PROGRAM
from src.candidate_a_issue12_signal_policy_20261012.adapter import StepAdapter
from src.candidate_a_issue12_signal_policy_20261012.bridge import _diagnostic_loop,execute,policy_after_ack
from src.candidate_a_native_smoke_20261011.bridge_logs import LogCapture
from src.candidate_a_qualification_20261008.safety import Vehicle
spec=importlib.util.spec_from_file_location('old_wait_fixture',profile.ROOT/'tests/candidate_a_native_receiver_wait_20261012/test_wait.py')
fixture=importlib.util.module_from_spec(spec);spec.loader.exec_module(fixture)


class CountWorld(fixture.World):
    def __init__(self,xml,early=True,arrive=False):
        super().__init__(xml);self.early=early;self.arrive=arrive
        self.vspeed.update({f'R_flow.{n}':0. for n in range(9)})
        self.trafficlight.setPhaseDuration=lambda tls,d:setattr(self,'switch',self.time+d)
    def observe(self,conn):
        v,ids,internal,receiver=super().observe(conn)
        return [replace(s,position_m=self.position(s.vehicle_id)) for s in v],ids,internal,receiver
    def simulationStep(self,end):
        begin=self.time
        fixture.old.fixture.XMLFakeConnection.simulationStep(self,end)
        self.arrived=[]
        if begin>=1200:
            cycle=(begin-1200)//24;offset=(begin-1200)%24
            if offset==0:
                for n in ([3*cycle,3*cycle+1] if self.early else [cycle]):self.enter[f'R_flow.{n}']=end
            if offset==1 and self.early:self.enter[f'R_flow.{3*cycle+2}']=end
            if begin==1200 and self.arrive:
                del self.vspeed['M_flow.0'];self.arrived=['M_flow.0']


class PolicyTests(unittest.TestCase):
    def test_quantization_invalid_boundaries_and_independent_integrals(self):
        self.assertEqual([quantize(x) for x in (300,375,375.01,525,825,900)],[300,300,450,450,750,900])
        for v in (True,None,'300',299,901,float('nan'),float('inf')):
            with self.assertRaises(ValueError):quantize(v)
        ledger=Ledger(375);self.assertTrue(all(v is None for v in ledger.accounting().values()))
        ledger.begin_step(1200,375);ledger.mark_cycle_start(True);ledger.end_step(1201,[],'G')
        a=ledger.accounting();self.assertEqual(a['N'],0);self.assertEqual(a['E'],0)
        self.assertAlmostEqual(a['policy_quantization'],75/3600);self.assertEqual(a['application_latency'],0)
        ledger.begin_step(1201,600);ledger.end_step(1202,[],'G')
        self.assertAlmostEqual(ledger.accounting()['application_latency'],300/3600)
    def test_local_yellow_position_speed_body_and_unknown_scope(self):
        base=Vehicle('R_flow.0','storage',203.49,0.,5.,2.5,2.6,4.5,1.,1.,'technical_passenger')
        self.assertEqual(yellow_scope([base],1205)['status'],'PASS')
        self.assertEqual(yellow_scope([replace(base,speed_m_s=.05)],1205)['status'],'PASS')
        with self.assertRaises(ValueError):yellow_scope([replace(base,position_m=204.49)],1205)
        self.assertEqual(yellow_scope([replace(base,position_m=100.,speed_m_s=55.)],1205)['status'],'UNKNOWN')
        with self.assertRaises(ValueError):yellow_scope([base,base],1205)
    def test_same_ack_and_yellow_excess_are_counted_and_partial_E_not_filled(self):
        l=Ledger(300);l.begin_step(1200,300);l.mark_cycle_start(True)
        l.end_step(1201,['R_flow.0','R_flow.1','R_flow.2'],'G');l.close_green(1201,'ACTUAL_QUOTA_ACK')
        for t in range(1201,1224):
            l.begin_step(t,300);l.end_step(t+1,['R_flow.3'] if t==1201 else [],l.motion_at(t))
        self.assertEqual((l.E,l.N),(2,4));self.assertEqual(l.rows[0]['N_y'],1)
        self.assertEqual(l.accounting()['E_minus_N'],-2)
        self.assertEqual(l.rows[0]['phase_exposure_s'],{'G':1,'y':5,'r':18})
    def loop(self,tmp,early=True,arrive=False):
        pkg=Path(tmp)/'pkg';out=Path(tmp)/'out';profile.stage_package(profile.ROOT,pkg,out);out.mkdir()
        w=CountWorld(pkg/'scenario.add.xml',early=early,arrive=arrive);cap=LogCapture(out);a=StepAdapter(w.observe,300)
        try:
            _diagnostic_loop(w,SimpleNamespace(observe=w.observe,request_phase=w.phase_request),cap,out,
                {'wall_limit_s':300,'minimum_free_bytes':0,'run_limit_bytes':300000000},
                fixture.old.fixture.fixture.FakeProcess(),time.monotonic(),a)
        finally:cap.close_handles()
        return w,out,a
    def test_xml_driven_early_green_actual_red_remaining_clock_and_yellow_excess(self):
        with tempfile.TemporaryDirectory() as tmp:
            w,out,a=self.loop(tmp)
            self.assertEqual(w.time,1272);self.assertEqual((w.phase,w.state,w.switch),(2,'r',1272))
            self.assertEqual((a.ledger.E,a.ledger.N),(6,9));self.assertTrue(a.checkpoint_verified)
            req=[json.loads(x) for x in (out/'policy_phase_requests.jsonl').read_text().splitlines()]
            red=[x for x in req if x['requests'][0]['method']=='setPhaseDuration']
            self.assertEqual([x['actual_readback']['nextSwitch_s'] for x in red],[1224,1248,1272])
            self.assertTrue(all(c['phase_exposure_s']=={'G':1,'y':5,'r':18} for c in a.ledger.rows))
    def test_xml_deadline_dynamic_first_red_and_normal_arrival_pending_schema(self):
        with tempfile.TemporaryDirectory() as tmp:
            w,out,a=self.loop(tmp,early=False,arrive=True)
            self.assertEqual((a.ledger.E,a.ledger.N),(6,3))
            cp=json.loads((out/'first_red_checkpoint.json').read_text());self.assertEqual(cp['time_s'],1223)
            post=[json.loads(x) for x in (out/'post_steps.jsonl').read_text().splitlines()]
            arrived=post[1200]['terminal_arrival_pending'][0]
            self.assertEqual(arrived['vehicle_id'],'M_flow.0');self.assertEqual(arrived['time_begin_s'],1200)
            self.assertEqual(arrived['speed_m_s'],5.);self.assertEqual(arrived['length_m'],5.)
            self.assertEqual(arrived['terminal_edge'],'main_down');self.assertEqual(arrived['normal_decel_m_s2'],4.5)
            self.assertIn('legal final lane changes allowed',arrived['terminal_lane_binding_scope'])
            self.assertIn('NOT_ONLINE_COVERED',arrived['status'])
            self.assertTrue(all(c['phase_exposure_s']=={'G':17,'y':5,'r':2} for c in a.ledger.rows))
    def test_unknown_yellow_scope_stops_before_phase_setter(self):
        with tempfile.TemporaryDirectory() as tmp:
            pkg=Path(tmp)/'pkg';out=Path(tmp)/'out';profile.stage_package(profile.ROOT,pkg,out);out.mkdir()
            w=CountWorld(pkg/'scenario.add.xml');w.time=1201;w.program=PROGRAM;w.phase=0;w.state='G';w.switch=1217
            w.vspeed['R_flow.2']=55.;a=StepAdapter(w.observe,300)
            a.ledger.begin_step(1200,300);a.ledger.mark_cycle_start(True)
            a.ledger.end_step(1201,['R_flow.0','R_flow.1'],'G');a.last_completed=1201;a.previous_motion='G'
            with self.assertRaisesRegex(ValueError,'UNKNOWN_LOCAL_YELLOW_SCOPE'):
                policy_after_ack(w,a,SimpleNamespace(request_phase=w.phase_request),out)
            self.assertEqual(w.state,'G');self.assertEqual(w.requests,[])
            scope=json.loads((out/'yellow_scope.jsonl').read_text());self.assertEqual(scope['status'],'UNKNOWN')

    def test_missing_card_rejects_before_any_native_or_raw_allocation(self):
        with self.assertRaises(FileNotFoundError):execute(profile.ROOT/'nonexistent_issue12_card.json',profile.ROOT/'nonexistent_issue12_release.json')
        self.assertTrue(all(not (profile.ROOT/profile.output(run)).parent.exists() for run in profile.RUNS))

if __name__=='__main__':unittest.main(verbosity=2)

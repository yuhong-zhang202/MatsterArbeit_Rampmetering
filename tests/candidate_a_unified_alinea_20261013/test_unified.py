"""Bounded offline fixtures. Fake movement/E1 is not SUMO physics evidence."""
from pathlib import Path
from types import SimpleNamespace
import importlib.util, json, tempfile, time, unittest
from src.candidate_a_unified_alinea_20261013 import profile, bridge, budget
from src.candidate_a_unified_alinea_20261013.policy import Ledger, Command, parameters, period_for
from src.candidate_a_unified_alinea_20261013.producer import Producer, DETECTORS
from src.candidate_a_unified_alinea_20261013.adapter import StepAdapter, inventory
from src.candidate_a_native_smoke_20261011.bridge_logs import LogCapture
from src.candidate_a_native_receiver_wait_20261012.receiver_wait import current_following
spec=importlib.util.spec_from_file_location('packet_fixture',profile.ROOT/'tests/candidate_a_issue12_packet_policy_20261012/test_packet.py')
fixture=importlib.util.module_from_spec(spec);spec.loader.exec_module(fixture)


class UnifiedWorld(fixture.PacketWorld):
    def __init__(self,xml):
        super().__init__(xml)
        self.vspeed.update({f'R_flow.{n}':0. for n in range(24)})
        self.next_entry=0;self.last_entered_green=None
        self.inductionloop=SimpleNamespace(getIDList=lambda:DETECTORS,
            getLaneID=lambda d:'main_down_'+str(DETECTORS.index(d)), getPosition=lambda d:20.,
            getVehicleData=lambda d:[('M_flow.0',5.,1199.,-1 if self.time<1202 else 1202.,'technical_passenger')]
                if 1200<=self.time<=1202 else [])

    def simulationStep(self,end):
        fixture.old.fixture.old.fixture.XMLFakeConnection.simulationStep(self,end)
        self.arrived=[]
        if end>=1201 and self.state=='G' and self.last_entered_green!=self.switch:
            self.last_entered_green=self.switch
            for n in range(self.next_entry,self.next_entry+2):self.enter[f'R_flow.{n}']=end
            self.next_entry+=2


class UnifiedTests(unittest.TestCase):
    def test_same_clock_wrong_post_signal_program_or_link_never_applies_command(self):
        for mutation in ('state','phase','program','link'):
            with self.subTest(mutation=mutation), tempfile.TemporaryDirectory() as tmp:
                pkg=Path(tmp)/'pkg';out=Path(tmp)/'out'
                profile.stage_package(profile.ROOT,pkg,out,1272)
                w=UnifiedWorld(pkg/'scenario.add.xml');w.time=1200
                w.program='I12_PACKET24';w.phase=0;w.state='G';w.switch=1204
                a=StepAdapter(w.observe,300);a.selected_new_program_at=1200
                a.ledger.begin_step(1200,Command('bound-test',1200,300,'FIXED'))
                a.prepare_step(w,1200);w.simulationStep(1201)
                if mutation=='state':w.state='r'
                if mutation=='phase':w.phase=1
                if mutation=='program':w.program='UNBOUND_PROGRAM'
                if mutation=='link':w.trafficlight.getControlledLinks=lambda tls:()
                self.assertEqual(w.switch,1204)
                warning={'time_begin_s':1200,'time_end_s':1201,'coverage':'CALLER_DECLARED_INTERVAL',
                    'source':'offline-negative-control','byte_start':0,'byte_end':0,'text':''}
                with self.assertRaises(ValueError):a.reconcile_step(w,warning)
                self.assertTrue(a.paused)
                self.assertIsNone(a.ledger.requests['bound-test']['first_application_s'])
                self.assertFalse(any(x['event']=='ACK_OBSERVED' for x in a.ledger.events))
                self.assertFalse(a.receipts[-1]['accounting_complete'])

    def test_all_seventeen_periods_xml_and_real_helper_clock(self):
        with tempfile.TemporaryDirectory() as tmp:
            pkg=Path(tmp)/'pkg';out=Path(tmp)/'out';profile.stage_package(profile.ROOT,pkg,out,1272);out.mkdir()
            worker=bridge.protected_worker()
            for period in range(8,25):
                with self.subTest(period=period):
                    rate=7200/period;l=Ledger(rate);w=UnifiedWorld(pkg/'scenario.add.xml')
                    w.time=1200;par=parameters(period)
                    worker.request_phase(w.trafficlight,[],1200,'setProgram',par['program'])
                    worker.request_phase(w.trafficlight,[],1200,'setPhase',0)
                    for t in range(1200,1200+period):
                        new,c=l.begin_step(t)
                        if new:l.mark_cycle_start(True)
                        motion=l.motion_at(t);w.simulationStep(t+1)
                        self.assertEqual(w.state,motion)
                        l.end_step(t+1,['a','b'] if t==1200 else [],motion)
                        if t==1200:
                            worker.request_phase(w.trafficlight,[],t+1,'setPhase',1)
                            l.close_green(t+1,'ACTUAL_QUOTA_ACK')
                        if motion=='r' and not c.get('bound') and t+1<1200+period:
                            bridge.request_red_duration(w,[],t+1,c['end_s']-(t+1),c['end_s'],out,c['program'])
                            c['bound']=True
                    self.assertEqual((l.E,l.N),(2,2))
                    self.assertEqual((w.state,w.phase,w.switch),('r',2,1200+period))
                    self.assertEqual(c['phase_exposure_s'],{'G':1,'y':par['yellow_s'],'r':period-1-par['yellow_s']})

    def test_dynamic_request_ids_delays_partial_and_real_zero(self):
        l=Ledger(300,1266);p=Producer('dynamic_commands');applications=[]
        for t in range(1200,1266):
            new,c=l.begin_step(t,p.command_at(None,t))
            if new:l.mark_cycle_start(True)
            l.end_step(t+1,[],l.motion_at(t))
            if new:applications.append((c['begin_s'],c['period_s'],c['application_delay_s']))
        self.assertEqual(applications,[(1200,24,0),(1224,10,23),(1234,8,8),(1242,24,5)])
        self.assertEqual((l.E,l.N),(8,0));self.assertAlmostEqual(l.accounting()['C'],10.458333333333334)
        self.assertAlmostEqual(l.accounting()['C_mapped_pending'],10.25)
        l=Ledger();self.assertTrue(all(v is None for v in l.accounting().values()))
        l.begin_step(1200,Command('a',1200,300,'FIXED'));self.assertIsNone(l.requests['a']['first_application_s'])
        l.mark_cycle_start(True);l.end_step(1201,[],'G')
        self.assertEqual((l.E,l.N),(0,0));self.assertEqual(l.requests['a']['status'],'ACK_OBSERVED')
        l.begin_step(1201,Command('same-value',1201,300,'FIXED'));l.end_step(1202,['x','y','z'],'G')
        l.close_green(1202,'ACTUAL_QUOTA_ACK')
        l.begin_step(1202,Command('newer',1202,300,'FIXED'));l.end_step(1203,['extra-yellow'],'y')
        self.assertEqual(l.N,4);self.assertEqual(l.E,0)
        self.assertEqual(l.requests['same-value']['status'],'SUPERSEDED_WITHOUT_APPLICATION')
        self.assertIsNone(l.requests['newer']['first_application_s'])
        for bad in (True,None,'300',299,901,float('nan')):
            with self.assertRaises(ValueError):period_for(bad)
        self.assertEqual(period_for(850),9)

    def run_loop(self, mode, rate, end):
        with tempfile.TemporaryDirectory() as tmp:
            pkg=Path(tmp)/'pkg';out=Path(tmp)/'out';profile.stage_package(profile.ROOT,pkg,out,end);out.mkdir()
            w=UnifiedWorld(pkg/'scenario.add.xml');a=StepAdapter(w.observe,rate,end);producer=Producer(mode,rate)
            cap=LogCapture(out);worker=bridge.protected_worker()
            try:bridge._diagnostic_loop(w,SimpleNamespace(observe=w.observe,request_phase=worker.request_phase),cap,out,
                {'wall_limit_s':300,'minimum_free_bytes':0,'run_limit_bytes':300000000},
                fixture.old.fixture.old.fixture.fixture.FakeProcess(),time.monotonic(),a,producer)
            finally:cap.close_handles()
            return a,w.requests,[json.loads(x) for x in (out/'command_events.jsonl').read_text().splitlines()],producer.events

    def test_real_helper_dynamic_bridge_continuous_phases_and_boundary_switches(self):
        a,calls,events,_=self.run_loop('dynamic_commands',300,1266)
        self.assertEqual((a.last_completed,a.ledger.E,a.ledger.N),(1266,8,8))
        self.assertEqual([(t,v) for t,m,v in calls if t>=1200 and m=='setProgram'],
            [(1200,'I12_PACKET24'),(1224,'I12_PACKET10'),(1234,'I12_PACKET8'),(1242,'I12_PACKET24')])
        self.assertEqual([e['application_delay_s'] for e in events if e['event']=='ACK_OBSERVED'],[0,23,8,5])
        self.assertTrue(a.checkpoint_verified)
        self.assertTrue(all(c['completed'] for c in a.ledger.rows))

    def test_actual_feedback_class_global_seed_ongoing_windows_and_own_clipped_state(self):
        a,calls,events,feedback=self.run_loop('real_alinea',900,1272)
        seed=next(x for x in feedback if x['event']=='E1_ACTIVATION_SEED')
        self.assertEqual(seed['ongoing_events'][DETECTORS[0]][0][2:], [1199.,-1,'technical_passenger'])
        rows=[x for x in feedback if x['event']=='E1_POST_ACK_EVENTS']
        self.assertEqual([x['global_s'] for x in rows],list(range(1201,1273)))
        decisions=[x for x in feedback if x['event']=='PROJECT_FEEDBACK_DECISION']
        self.assertEqual([(x['global_s'],x['update_time_s'],x['global_window_begin_s']) for x in decisions],[(1230,630,1200),(1260,660,1230)])
        self.assertAlmostEqual(decisions[0]['occ_mean_pct'],2/30*100)
        self.assertEqual([x['rate_previous_veh_h'] for x in decisions],[900,900])
        self.assertEqual([x['rate_clipped_veh_h'] for x in decisions],[900,900])
        self.assertEqual([(x['request_id'],x['application_global_s']) for x in events if x['event']=='ACK_OBSERVED'],
            [('real_alinea:1200',1200),('feedback:1230',1232),('feedback:1260',1264)])
        self.assertEqual((a.ledger.E,a.ledger.N),(18,18))
        self.assertEqual([(t,m,v) for t,m,v in calls if t>=1200 and m=='setProgram'],[(1200,'setProgram','I12_PACKET8')])
        p=Producer('real_alinea');p.seeded=True
        with self.assertRaisesRegex(ValueError,'incomplete'):p.command_at(None,1230)
        from src.candidate_a_unified_alinea_20261013.producer import Feedback, PARAMETERS
        f=Feedback(PARAMETERS)
        first=f.update(630,600,630,11+150/70,11+150/70)
        self.assertAlmostEqual(first['rate_clipped_veh_h'],750)
        self.assertEqual(period_for(first['rate_clipped_veh_h']),10)
        second=f.update(660,630,660,11,11)
        self.assertAlmostEqual(second['rate_previous_veh_h'],750)
        self.assertNotEqual(second['rate_previous_veh_h'],720)
        from src.candidate_a_unified_alinea_20261013.event_ledger import DetectorEventLedger
        e=DetectorEventLedger(1200);e.events[DETECTORS[0]][('x',1199)]=('x',5,1199,-1,'technical_passenger')
        with self.assertRaisesRegex(ValueError,'disappeared'):e.add_step(1201,{d:[] for d in DETECTORS})

    def test_preserved_gap_yellow_unknown_and_new_stage_budget_reservations(self):
        with tempfile.TemporaryDirectory() as tmp:
            pkg=Path(tmp)/'pkg';out=Path(tmp)/'out';profile.stage_package(profile.ROOT,pkg,out,1272);out.mkdir()
            w=UnifiedWorld(pkg/'scenario.add.xml');w.time=1206;w.enter['R_flow.1']=1204
            w.vspeed['R_flow.2']=7.060596259649246;w.vspeed['R_flow.1']=8.478656087227455
            w.actual_gap=9.630877589859532;w.actual_secure=9.621192519298493
            q=current_following(w,'R_flow.2',1206)
            self.assertEqual(q['status'],'STOP_CURRENT_GAP_BOUND_DENIED');self.assertEqual(q['margin_m'],1.1)
            self.assertEqual(q['getSecureGap_args']['leaderMaxDecel'],9.)
            w.time=1201;w.enter={};w.vspeed={v:0. for v in w.vspeed};w.vspeed['R_flow.2']=55.
            w.program='I12_PACKET8';w.phase=0;w.state='G';w.switch=1204
            a=StepAdapter(w.observe,900);a.ledger.begin_step(1200);a.ledger.mark_cycle_start(True)
            a.ledger.end_step(1201,['a','b'],'G');a.last_completed=1201;a.previous_motion='G'
            a.receipts=[{'time_end_s':1201,'post_world':inventory(w)[0]}]
            with self.assertRaisesRegex(ValueError,'UNKNOWN_LOCAL_YELLOW_SCOPE'):
                bridge.policy_after_ack(w,a,SimpleNamespace(request_phase=bridge.protected_worker().request_phase),out)
            self.assertEqual(w.requests,[])
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp);(root/'data/raw/issue12_alinea_actuation_20261012_v1/old').mkdir(parents=True)
            self.assertEqual(budget.accounting(root)['charged_monitored_s'],0)
            for n in range(3):(root/budget.RAW/str(n)).mkdir(parents=True)
            b=budget.accounting(root);self.assertEqual((b['charged_monitored_s'],b['charged_raw_bytes']),(900,900000000))
            (root/budget.RAW/'4').mkdir()
            with self.assertRaisesRegex(ValueError,'EXHAUSTED'):budget.accounting(root)

if __name__=='__main__':unittest.main(verbosity=2)

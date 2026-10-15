"""Four affected offline methods; fake movement is not SUMO physics."""
from pathlib import Path
from types import SimpleNamespace
from dataclasses import replace
import importlib.util,json,tempfile,time,unittest,hashlib
from src.candidate_a_issue12_packet_policy_20261012 import profile,bridge,budget
from src.candidate_a_issue12_packet_policy_20261012.policy import Ledger,period_for,quantize,PROGRAM
from src.candidate_a_issue12_packet_policy_20261012.adapter import StepAdapter,inventory,INTERNAL,STORAGE
from src.candidate_a_issue12_packet_policy_20261012.body import BodyTracker
from src.candidate_a_native_receiver_wait_20261012.receiver_wait import current_following
from src.candidate_a_native_smoke_20261011.bridge_logs import LogCapture
sp=importlib.util.spec_from_file_location('old_packet_fixture',profile.ROOT/'tests/candidate_a_issue12_signal_policy_20261012/test_policy.py');old=importlib.util.module_from_spec(sp);sp.loader.exec_module(old)


class PacketWorld(old.CountWorld):
    def __init__(self,xml):
        super().__init__(xml)
        self.vspeed={k:v for k,v in self.vspeed.items() if not k.startswith('R')}
        self.vspeed.update({f'R_flow.{i}':0. for i in range(18)})
    def lane_id(self,v):
        if v.startswith('M'):return 'main_up_0'
        if v not in self.enter:return STORAGE
        return INTERNAL if self.time-self.enter[v]<6 else 'ramp_accel_0'
    def position(self,v):
        if v.startswith('M'):return 50.
        if v not in self.enter:return 203.-int(v.rsplit('.',1)[1])*7.5
        return .5+1.3*(self.time-self.enter[v]) if self.lane_id(v)==INTERNAL else 10.
    def simulationStep(self,end):
        begin=self.time;old.fixture.old.fixture.XMLFakeConnection.simulationStep(self,end);self.arrived=[]
        if begin>=1200 and (begin-1200)%8==0:
            c=(begin-1200)//8
            for n in (2*c,2*c+1):self.enter[f'R_flow.{n}']=end


class PacketTests(unittest.TestCase):
    def world(self,tmp):
        pkg=Path(tmp)/'pkg';out=Path(tmp)/'out';profile.stage_package(profile.ROOT,pkg,out);out.mkdir()
        return PacketWorld(pkg/'scenario.add.xml'),out
    def test_real_xml_helper_nine_cycles_and_tail_under_red(self):
        with tempfile.TemporaryDirectory() as tmp:
            w,out=self.world(tmp);a=StepAdapter(w.observe,900);cap=LogCapture(out);worker=bridge.protected_worker()
            try:bridge._diagnostic_loop(w,SimpleNamespace(observe=w.observe,request_phase=worker.request_phase),cap,out,{'wall_limit_s':300,'minimum_free_bytes':0,'run_limit_bytes':300000000},old.fixture.old.fixture.fixture.FakeProcess(),time.monotonic(),a)
            finally:cap.close_handles()
            self.assertEqual(w.time,1272);self.assertEqual((w.phase,w.state,w.switch),(2,'r',1272))
            self.assertEqual((a.ledger.E,a.ledger.N),(18,18));self.assertEqual(len(a.ledger.rows),9)
            self.assertTrue(a.checkpoint_verified)
            self.assertTrue(all(c['phase_exposure_s']=={'G':1,'y':2,'r':5} for c in a.ledger.rows))
            post=[json.loads(x) for x in (out/'post_steps.jsonl').read_text().splitlines()]
            self.assertTrue(any(x['motion']=='r' and x['body_observation']['spanning_ids'] for x in post))
            self.assertEqual(len((out/'body_admission.jsonl').read_text().splitlines()),9)
            self.assertEqual(len((out/'policy_duration_requests.jsonl').read_text().splitlines()),18)
            with self.assertRaisesRegex(ValueError,'unsupported phase request'):worker.request_phase(w.trafficlight,[],1272,'setPhaseDuration',2)
    def test_all_spanning_body_ids_and_unknown_or_lost_stop(self):
        pos={'R_flow.0':1.,'R_flow.1':3.};t=[11];world={v:{'role':'R','speed_m_s':1.,'lane_id':INTERNAL} for v in pos}
        conn=SimpleNamespace(simulation=SimpleNamespace(getTime=lambda:t[0]),vehicle=SimpleNamespace(getIDList=lambda:tuple(world),getLanePosition=lambda v:pos[v],getLength=lambda v:5.,getSpeed=lambda v:1.,getLaneID=lambda v:INTERNAL),lane=SimpleNamespace(getLastStepVehicleIDs=lambda l:tuple(world)))
        tracker=BodyTracker();entries=[{'vehicle_id':v,'crossing_time_lower_s':10,'crossing_time_upper_s':11} for v in pos]
        row=tracker.observe(conn,11,world,entries,'G');self.assertEqual(row['spanning_ids'],['R_flow.0','R_flow.1'])
        t[0]=12;pos['R_flow.0']=6.;row=tracker.observe(conn,12,world,[],'r')
        self.assertEqual(row['spanning_ids'],['R_flow.1']);self.assertEqual(tracker.cleared['R_flow.0'],12)
        self.assertEqual(next(x for x in row['rows'] if x['vehicle_id']=='R_flow.1')['entry_signal'],'G')
        t[0]=13;del world['R_flow.1']
        with self.assertRaisesRegex(ValueError,'BODY_LOST'):tracker.observe(conn,13,world,[],'r')
        tracker=BodyTracker()
        with self.assertRaisesRegex(ValueError,'BODY_SPANNING_ENTRY_UNBOUND'):tracker.observe(conn,13,{'R_flow.1':{'role':'R','speed_m_s':1.,'lane_id':INTERNAL}},[],'r')
    def test_preserved_emergency_margin_and_actual_yellow_unknown_stop(self):
        with tempfile.TemporaryDirectory() as tmp:
            w,out=self.world(tmp);w.time=1206;w.program=PROGRAM;w.phase=0;w.state='G';w.switch=1217
            w.enter['R_flow.1']=1204;w.vspeed['R_flow.2']=7.060596259649246;w.vspeed['R_flow.1']=8.478656087227455
            w.actual_gap=9.630877589859532;w.actual_secure=9.621192519298493
            q=current_following(w,'R_flow.2',1206);self.assertEqual(q['status'],'STOP_CURRENT_GAP_BOUND_DENIED')
            self.assertEqual(q['getSecureGap_args']['leaderMaxDecel'],9.);self.assertEqual(q['margin_m'],1.1)
            w.time=1201;w.enter={};w.vspeed={v:0. for v in w.vspeed};w.vspeed['R_flow.2']=55.
            w.switch=1204;a=StepAdapter(w.observe,900);a.ledger.begin_step(1200,900);a.ledger.mark_cycle_start(True);a.ledger.end_step(1201,['R_flow.0','R_flow.1'],'G')
            a.last_completed=1201;a.previous_motion='G';a.receipts=[{'time_end_s':1201,'post_world':inventory(w)[0]}]
            with self.assertRaisesRegex(ValueError,'UNKNOWN_LOCAL_YELLOW_SCOPE'):bridge.policy_after_ack(w,a,SimpleNamespace(request_phase=bridge.protected_worker().request_phase),out)
            self.assertEqual(w.phase,0);self.assertEqual(w.requests,[])
    def test_rate_partial_zero_unobserved_and_cumulative_unknown_budget(self):
        self.assertEqual([period_for(x) for x in (300,450,600,750,850,850.01,900)],[24,16,12,10,9,8,8])
        self.assertEqual(quantize(850),800)
        for x in (True,'900',299,901,float('nan')):
            with self.assertRaises(ValueError):period_for(x)
        l=Ledger(900);self.assertTrue(all(x is None for x in l.accounting().values()))
        l.begin_step(1200,900);l.mark_cycle_start(True);l.end_step(1201,[],'G')
        self.assertEqual((l.accounting()['E'],l.accounting()['N']),(0,0));self.assertGreater(l.accounting()['C'],0)
        l.begin_step(1201,900);l.end_step(1202,['R_flow.0','R_flow.1','R_flow.2'],'G');l.close_green(1202,'ACTUAL_QUOTA_ACK')
        for t in range(1202,1208):l.begin_step(t,900);l.end_step(t+1,['R_flow.3'] if t==1202 else [],l.motion_at(t))
        self.assertEqual((l.E,l.N),(2,4))
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp);raw=root/budget.RAW/'old';raw.mkdir(parents=True);receipt=raw/'receipt.json'
            receipt.write_text(json.dumps({'native_started':True,'final_logs':{'coverage':'FINAL_FILES_AT_OWNED_PROCESS_EOF'},'monitored_elapsed_through_cleanup_s':100.}))
            files={str(receipt.relative_to(root)):budget.sha(receipt)};manifest=root/'manifest.json';manifest.write_text(json.dumps({'files':files,'bytes':receipt.stat().st_size}))
            h=root/budget.HISTORY;h.parent.mkdir(parents=True);h.write_text(json.dumps({'runs':{'old':{'receipt_path':str(receipt.relative_to(root)),'receipt_sha256':budget.sha(receipt),'raw_manifest_path':str(manifest.relative_to(root)),'raw_manifest_sha256':budget.sha(manifest)}}}))
            b=budget.accounting(root);self.assertEqual(b['charged_monitored_s'],100.)
            for n in ('unknown1','unknown2'):(root/budget.RAW/n).mkdir()
            b=budget.accounting(root);self.assertEqual(b['charged_monitored_s'],700.);self.assertEqual(len(b['unknown_reserved']),2)
            limits=budget.effective_limits({'wall_limit_s':300,'run_limit_bytes':300000000},b);self.assertEqual(limits['wall_limit_s'],200.)
            (root/budget.RAW/'unknown3').mkdir()
            with self.assertRaisesRegex(ValueError,'TOTAL_BUDGET_EXHAUSTED'):budget.accounting(root)

if __name__=='__main__':unittest.main(verbosity=2)

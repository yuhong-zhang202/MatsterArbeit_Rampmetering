"""Small schema/WAIT/terminal integration fixtures. No native safety certificate."""
import importlib.util,json,tempfile,time,unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch
from src.candidate_a_native_receiver_wait_20261012 import profile
from src.candidate_a_native_receiver_wait_20261012.receiver_wait import classify_receiver,current_following,PATH_LANES
from src.candidate_a_native_receiver_wait_20261012.adapter import StepAdapter,STORAGE,INTERNAL
from src.candidate_a_native_receiver_wait_20261012.bridge import _diagnostic_loop
from src.candidate_a_native_smoke_20261011.bridge_logs import LogCapture
sp=importlib.util.spec_from_file_location('bounded_old_world',profile.ROOT/'tests/candidate_a_native_budget_cycles_20261012/test_cycles.py');old=importlib.util.module_from_spec(sp);sp.loader.exec_module(old)


class World(old.World):
    def __init__(self,xml,fail=None):
        super().__init__(xml,fail=fail);self.actual_gap=3.;self.actual_secure=0.;self.follow_calls=[]
        lengths={STORAGE:204.49,':urban_diverge_1_0':113.08,INTERNAL:81.98,'ramp_accel_0':294.51,':freeway_merge_2_0':12.,'merge_section_0':365.,'merge_section_1':365.,'merge_section_2':365.}
        self.lane.getLength=lambda l:lengths[l]
        self.vehicle.getLanePosition=self.position
        self.vehicle.getLength=lambda v:5.
        self.vehicle.getMinGap=lambda v:2.5
        self.vehicle.getLeader=self.leader
        self.vehicle.getSecureGap=self.secure
    def position(self,v):
        if v.startswith('M'):return 50.
        if self.lane_id(v)==STORAGE:return 203.-int(v.rsplit('.',1)[1])*7.5
        return .314 if self.lane_id(v)==INTERNAL else 10.
    def leader(self,v,lookahead):
        others=sorted((x for x in self.vspeed if x.startswith('R') and x!=v),key=lambda x:int(x.rsplit('.',1)[1]))
        previous=[x for x in others if int(x.rsplit('.',1)[1])<int(v.rsplit('.',1)[1])]
        if not previous:return None
        leader=previous[-1]
        if self.lane_id(leader)=='ramp_accel_0':return None
        return leader,self.actual_gap
    def secure(self,**args):self.follow_calls.append(dict(args));return self.actual_secure
    def observe(self,conn):
        states,ids,internal,receiver=super().observe(conn)
        front=max(ids[STORAGE],key=self.position,default=None)
        receiver.update(front_id=front or '',nearest_internal=next(iter(internal),None),leader=None,reason='AVAILABLE')
        if front and internal and self.time>=1201 and self.fail not in ('receiver','unknown_receiver'):
            leader,gap=self.leader(front,478.67);receiver.update(available=False,reason='LEADER_SECURE_GAP',nearest_internal_rear_clearance_m=-4.68573,required_front_clearance_m=7.5,leader={'vehicle_id':leader,'lane_id':self.lane_id(leader),'gap_excluding_minGap_m':gap,'secure_gap_m':2.6})
        return states,ids,internal,receiver


class WaitTests(unittest.TestCase):
    def world(self,tmp,**kw):
        pkg=Path(tmp)/'package';out=Path(tmp)/'output';profile.stage_package(profile.ROOT,pkg,out);out.mkdir();return World(pkg/'scenario.add.xml',**kw),out
    def postfirst(self,w):w.time=1201;w.program='CA_C24';w.phase=0;w.state='G';w.switch=1203;w.enter['R_flow.0']=1201
    def loop(self,w,out):
        cap=LogCapture(out);adapter=StepAdapter(w.observe)
        try:return _diagnostic_loop(w,SimpleNamespace(observe=w.observe,request_phase=w.phase_request),cap,out,{'wall_limit_s':300,'minimum_free_bytes':0,'run_limit_bytes':300000000},old.fixture.fixture.FakeProcess(),time.monotonic(),adapter)
        finally:cap.close_handles()
    def test_frozen_denial_pattern_current_query_is_separate_and_bound(self):
        with tempfile.TemporaryDirectory() as tmp:
            w,out=self.world(tmp);self.postfirst(w);receiver=w.observe(w)[3];result=classify_receiver(w,receiver,1201)
            self.assertFalse(receiver['available']);self.assertEqual(receiver['leader']['secure_gap_m'],2.6);self.assertEqual(result['decision'],'WAIT_NATIVE_FOLLOWING');self.assertFalse(result['future_safety_proven']);current=result['current_following']
            self.assertEqual(current['getSecureGap_args']['speed'],0.);self.assertEqual(current['actual_secure_gap_m'],0.);self.assertEqual(current['margin_m'],1.1);self.assertEqual(current['time_s'],1201);self.assertEqual(current['leader_id'],'R_flow.0');self.assertEqual(current['vehicle_id'],'R_flow.1')
    def test_moving_native_following_is_not_relabelled_stopped(self):
        with tempfile.TemporaryDirectory() as tmp:
            w,out=self.world(tmp);self.postfirst(w);w.vspeed['R_flow.1']=.5;w.actual_secure=.6;result=classify_receiver(w,w.observe(w)[3],1201)
            self.assertEqual(result['decision'],'WAIT_NATIVE_FOLLOWING');self.assertEqual(result['current_following']['actual_speed_m_s'],.5)
    def test_current_gap_denied_is_not_wait(self):
        with tempfile.TemporaryDirectory() as tmp:
            w,out=self.world(tmp);self.postfirst(w);w.actual_secure=4.
            self.assertEqual(classify_receiver(w,w.observe(w)[3],1201)['decision'],'STOP_CURRENT_GAP_BOUND_DENIED')
    def test_unknown_or_mismatched_inputs_do_not_become_wait(self):
        for fault in ('empty','exception','wrong_id','nan_gap','nan_secure','bad_front','bad_mode'):
            with self.subTest(fault=fault),tempfile.TemporaryDirectory() as tmp:
                w,out=self.world(tmp);self.postfirst(w);receiver=w.observe(w)[3]
                if fault=='empty':w.vehicle.getLeader=lambda v,d:None
                elif fault=='exception':w.vehicle.getLeader=lambda v,d:(_ for _ in ()).throw(OSError('read failed'))
                elif fault=='wrong_id':receiver['leader']['vehicle_id']='R_flow.2'
                elif fault=='nan_gap':w.actual_gap=float('nan')
                elif fault=='nan_secure':w.actual_secure=float('nan')
                elif fault=='bad_front':receiver['front_id']='R_flow.2'
                else:w.vehicle.getSpeedMode=lambda v:0
                with self.assertRaises((ValueError,OSError)):classify_receiver(w,receiver,1201)
    def test_valid_empty_leader_is_bounded_clear_not_unknown(self):
        with tempfile.TemporaryDirectory() as tmp:
            w,out=self.world(tmp);r=current_following(w,'R_flow.0',0,allow_clear=True)
            self.assertEqual(r['status'],'CLEAR_WITHIN_OBSERVED_LOOKAHEAD');self.assertEqual(r['lookahead_m'],478.67);self.assertEqual(r['receiver_path_lanes'],list(PATH_LANES));self.assertIsNone(r['fresh_getLeader_result']);self.assertIn('not globally clear',r['claim_scope'])
            w.vehicle.getLeader=lambda v,d:('',0.)
            with self.assertRaises(ValueError):current_following(w,'R_flow.0',0,allow_clear=True)
    def test_actual_entry_can_change_from_storage_leader_to_internal_leader(self):
        with tempfile.TemporaryDirectory() as tmp:
            w,out=self.world(tmp);before=current_following(w,'R_flow.1',0,allow_clear=True);self.assertEqual(before['leader_lane_id'],STORAGE)
            self.postfirst(w);after=current_following(w,'R_flow.1',1201,allow_clear=True);self.assertEqual(after['leader_lane_id'],INTERNAL);self.assertEqual(before['vehicle_id'],after['vehicle_id'])
    def test_full_xml_wait_checkpoint_three_cycles_and_entry_identity_audit(self):
        with tempfile.TemporaryDirectory() as tmp:
            w,out=self.world(tmp);a=self.loop(w,out);rows=[json.loads(l)for l in(out/'post_steps.jsonl').read_text().splitlines()]
            self.assertEqual(w.time,1272);self.assertTrue(a.checkpoint_verified and a.paused);self.assertEqual(a.ledger.E,6);self.assertEqual(a.ledger.N,3);self.assertTrue(all(r['completed']for r in a.ledger.rows));self.assertEqual(w.switch,1272)
            self.assertEqual(rows[1200]['post_native_receiver_decision']['decision'],'WAIT_NATIVE_FOLLOWING');self.assertFalse(rows[1200]['post_receiver']['available']);self.assertEqual(rows[1200]['actual_entry_following'][0]['vehicle_id'],'R_flow.0');self.assertEqual(rows[1200]['actual_entry_following'][0]['before']['vehicle_id'],'R_flow.0');self.assertEqual(rows[1200]['actual_entry_following'][0]['after']['vehicle_id'],'R_flow.0')
            self.assertEqual(rows[1224]['actual_entry_following'][0]['vehicle_id'],'R_flow.1');self.assertEqual([q for q in w.requests if q[0]>=1200],[(1200,'setProgram','CA_C24'),(1200,'setPhase',0)])
    def test_old_dangerous_and_unknown_terminal_checks_remain(self):
        for fault,reason in [('red_crossing','RED_CROSSING'),('braking','ORDINARY_BRAKING_EXCEEDED'),('phase','PHASE_MISMATCH'),('unknown_receiver','UNKNOWN_POST_RECEIVER'),('receiver','receiver denies')]:
            with self.subTest(fault=fault),tempfile.TemporaryDirectory() as tmp:
                w,out=self.world(tmp,fail=fault)
                with self.assertRaisesRegex(ValueError,reason):self.loop(w,out)
                self.assertLess(w.time,1272)

if __name__=='__main__':unittest.main()

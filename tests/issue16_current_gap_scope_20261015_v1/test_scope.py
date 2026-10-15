"""Approved passive-query contract checks. No simulator or native physics."""
from copy import deepcopy
import importlib.util
import json
import os
from pathlib import Path
import tempfile
import time
from types import SimpleNamespace as NS
import unittest

from src.candidate_a_dynamic_minqual_20261015 import receiver_wait as legacy
from src.candidate_a_natural_service_20261015 import bridge, current_gap_scope as scope, profile
from src.candidate_a_natural_service_20261015.adapter import StepAdapter
from src.candidate_a_natural_service_20261015.producer import Producer
from src.candidate_a_native_smoke_20261011.bridge_logs import LogCapture

sp = importlib.util.spec_from_file_location('issue16_natural_fixture', profile.ROOT/'tests/candidate_a_natural_service_20261015/test_natural.py')
fixture = importlib.util.module_from_spec(sp); sp.loader.exec_module(fixture)
FRAMES = Path('data/processed/issue16_natural_gap_scope_20261015_v1/TERMINAL_FRAMES_V1.json')


class RecordedFrame:
    """Exact saved query primitives; no counterfactual motion or API re-query."""
    def __init__(self, q):
        self.q = deepcopy(q); self.time = q['time_s']; self.calls = []
        front = q['vehicle_id']; leader = q['leader_id']; self.ids = (front, leader)
        geo = q['path_geometry_m']
        # Both recorded frames are R1 on storage, R0 on storage/internal.
        lead_pos = q['lane_position_m']+q['gap_excluding_minGap_m']+q['min_gap_m']+5
        if q['leader_lane_id'] == legacy.INTERNAL: lead_pos -= geo[legacy.STORAGE]
        self.positions = {front:q['lane_position_m'], leader:lead_pos}
        self.simulation = NS(getTime=lambda:self.time)
        self.vehicle = NS(getIDList=lambda:self.ids, getTypeID=lambda v:'technical_passenger',
            getRoute=lambda v:legacy.ROUTES['R'], getSpeedMode=lambda v:31, getLaneChangeMode=lambda v:1621,
            getLaneID=lambda v:q['lane_id'] if v==front else q['leader_lane_id'],
            getLanePosition=lambda v:self.positions[v], getLength=lambda v:5., getMinGap=lambda v:2.5,
            getSpeed=lambda v:q['actual_speed_m_s'] if v==front else q['leader_speed_m_s'],
            getAccel=lambda v:2.6, getDecel=lambda v:4.5, getEmergencyDecel=lambda v:9.,
            getTau=lambda v:1., getActionStepLength=lambda v:1., getImperfection=lambda v:.5,
            getMaxSpeed=lambda v:55.55555555555556,
            getLeader=lambda v,d:(leader,self.q['gap_excluding_minGap_m']), getSecureGap=self.query)
        self.lane = NS(getLength=lambda l:geo[l],
            getLastStepVehicleIDs=lambda l:tuple(v for v in self.ids if self.vehicle.getLaneID(v)==l))
    def query(self, **args):
        self.calls.append(args); return self.q['actual_secure_gap_m']


class PassiveWorld(fixture.NaturalWorld):
    """Same small fake service case, with explicitly synthetic bound deficits."""
    def __init__(self, xml, fault=None):
        super().__init__(xml, case='blocked'); self.scope_fault = fault
        self.vehicle.getLeader = self.leader
        self.vehicle.getSecureGap = self.secure
        if fault == 'collision': self.simulation.getCollidingVehiclesNumber = lambda:1 if self.time==603 else 0
        if fault == 'braking': self.vehicle.getAcceleration = lambda v:-5. if self.time==603 and v=='M_flow.0' else 0.
        if fault == 'badACK': self.fault = 'badACK'
    def station(self, vid):
        offsets = {legacy.STORAGE:0, legacy.INTERNAL:204.49, 'ramp_accel_0':204.49+81.98}
        return offsets[self.lane_id(vid)] + self.position(vid)
    def leader(self, vid, distance):
        n = int(vid.rsplit('.',1)[1])
        if n == 0: return None
        lead = 'R_flow.'+str(n-1)
        if lead not in self.vspeed: return None
        if self.lane_id(lead)=='ramp_accel_0' and not self.deficit(): return None
        return lead, self.station(lead)-self.station(vid)-7.5
    def deficit(self): return self.time in (602,603,617,618,619)
    def secure(self, **args):
        raw = self.leader(args['vehID'],478.67)
        return raw[1]+1 if raw and self.deficit() else 0.
    def observe(self, conn):
        states, ids, internal, receiver = super().observe(conn)
        if self.deficit() and ids[legacy.STORAGE]:
            front = max(ids[legacy.STORAGE],key=self.position); raw = self.leader(front,478.67)
            if raw:
                lead,gap = raw
                receiver.update(available=False, front_id=front, reason='SYNTHETIC_REFERENCE_DEFICIT',
                    leader=dict(vehicle_id=lead,lane_id=self.lane_id(lead),gap_excluding_minGap_m=gap))
        return states, ids, internal, receiver


class ScopeTests(unittest.TestCase):
    def export(self, name, data):
        if directory := os.environ.get('ISSUE16_SCOPE_EXPORT'):
            p=Path(directory); p.mkdir(parents=True,exist_ok=True)
            with (p/(name+'.json')).open('x') as f:json.dump(data,f,indent=2)

    def test_recorded_649_650_queries_preserve_fail_fields_and_new_observation(self):
        raw=json.loads((profile.ROOT/FRAMES).read_text())
        queries=[raw['pre'][1]['entry_following_before']['R_flow.1'],
                 raw['post'][1]['post_native_receiver_decision']['current_following']]
        saved=[]
        for q in queries:
            w=RecordedFrame(q)
            current=scope.current_following(w,q['vehicle_id'],q['time_s'],allow_clear=True,role='ENTRY_BEFORE')
            for key in q:self.assertEqual(json.loads(json.dumps(current[key])),q[key],key)
            self.assertEqual(scope.classification(current),scope.BELOW)
            self.assertFalse(current['hard_screen_pass']);self.assertFalse(current['legacy_margin_pass'])
            self.assertEqual(current['status'],'STOP_CURRENT_GAP_BOUND_DENIED')
            self.assertEqual(w.calls,[q['getSecureGap_args']])
            saved.append(current)
        w=RecordedFrame(queries[1]); receiver=raw['post'][1]['post_receiver']
        result=scope.classify_receiver(w,receiver,650,role='POST_RECEIVER')
        self.assertEqual(result['decision'],scope.BELOW)
        self.assertEqual(result['legacy_decision'],'STOP_CURRENT_GAP_BOUND_DENIED')
        self.assertFalse(receiver['available']);self.assertEqual(result['original_prospective_receiver'],receiver)
        self.export('recorded_queries',dict(classification='SAVED_QUERY_REPLAY_NOT_NATIVE_MOTION',queries=saved,receiver=result))

    def loop(self, fault=None):
        with tempfile.TemporaryDirectory() as tmp:
            package=Path(tmp)/'package';output=Path(tmp)/'output'
            profile.stage_package(profile.ROOT,package,output,641);output.mkdir()
            w=PassiveWorld(package/'scenario.add.xml',fault);a=StepAdapter(w.observe,900,641,yellow_diagnostic_mode=True)
            cap=LogCapture(output);worker=bridge.protected_worker();error=None
            try:
                bridge._diagnostic_loop(w,NS(observe=w.observe,request_phase=worker.request_phase),cap,output,
                    dict(wall_limit_s=300,run_limit_bytes=None,minimum_free_bytes=0),
                    fixture.old.f.fixture.old.fixture.old.fixture.fixture.FakeProcess(),time.monotonic(),a,Producer())
            except Exception as exc:error=exc
            finally:cap.close_handles()
            logs={p.name:[json.loads(line) for line in p.read_text().splitlines()]
                  for p in output.glob('*.jsonl') if p.name in ('admission.jsonl','withheld_packets.jsonl','pre_steps.jsonl','post_steps.jsonl','step_ack.jsonl','control_setters.jsonl')}
            self.export('loop_'+str(fault),dict(classification='SYNTHETIC_MOVEMENT_NO_NATIVE_SAFETY_EVIDENCE',
                error=None if error is None else type(error).__name__+':'+str(error),time_s=w.time,
                last_accounted_s=a.last_end,accounting=a.ledger.accounting(),cycles=a.ledger.rows,logs=logs))
            return w,a,error,logs

    def test_real_adapter_loop_all_passive_roles_and_strict_new_green_red_hold(self):
        w,a,error,logs=self.loop()
        self.assertIsNone(error);self.assertEqual((w.time,a.last_end),(641,641))
        pre=[r['bound_snapshot'] for r in logs['pre_steps.jsonl']]
        post=logs['post_steps.jsonl']
        self.assertEqual(next(p for p in pre if p['time_s']==603)['native_receiver_decision']['decision'],scope.BELOW)
        self.assertEqual(next(p for p in post if p['time_end_s']==602)['post_native_receiver_decision']['decision'],scope.BELOW)
        entry=next(x for row in post for x in row['actual_entry_following'] if x['vehicle_id']=='R_flow.1')
        self.assertEqual([scope.classification(entry[k]) for k in ('before','after')],[scope.BELOW]*2)
        held=next(c for c in a.ledger.rows if c['executed'] is False)
        self.assertEqual(held['begin_s'],608);self.assertEqual(held['phase_exposure_s']['G'],0)
        self.assertFalse(any(608<=t<616 and method in ('setProgram','setPhase') for t,method,_ in w.requests))
        self.assertTrue(any(c['begin_s']>=616 and c['executed'] for c in a.ledger.rows))
        self.assertEqual((a.ledger.E-a.ledger.E_executed),2)
        self.assertTrue(any(c['completed'] and sum(c['N_'+m] for m in ('G','y','r'))==0 for c in a.ledger.rows))
        self.assertTrue(a.ledger.accounting()['partial_cycle'])
        self.assertEqual(profile.spec()['current_gap_responsibility_contract']['policy'],scope.CONTRACT)

    def test_unknown_negative_gap_and_real_faults_remain_terminal(self):
        raw=json.loads((profile.ROOT/FRAMES).read_text())
        q=raw['post'][1]['post_native_receiver_decision']['current_following']
        for fault in ('negative_gap','nan_query','wrong_time','wrong_mode','path_mismatch'):
            with self.subTest(fault=fault):
                w=RecordedFrame(q)
                if fault=='negative_gap':w.q['gap_excluding_minGap_m']=-.1
                elif fault=='nan_query':w.q['actual_secure_gap_m']=float('nan')
                elif fault=='wrong_time':w.time=651
                elif fault=='wrong_mode':w.vehicle.getSpeedMode=lambda _:0
                else:w.positions[q['leader_id']]+=1
                with self.assertRaises(ValueError):scope.current_following(w,q['vehicle_id'],650,role='ENTRY_AFTER')
        for fault,expected in (('collision','COLLISION_OR_TELEPORT'),('braking','EXCESSIVE_ACCELERATION'),('badACK','POST_SIGNAL_APPLICATION_BINDING_MISMATCH')):
            with self.subTest(fault=fault):
                w,a,error,logs=self.loop(fault)
                self.assertIsNotNone(error);self.assertIn(expected,str(error));self.assertTrue(a.paused)
                self.assertEqual(w.time,602 if fault=='badACK' else 603)
                if fault!='badACK':
                    self.assertEqual(a.receipts[-1]['post_native_receiver_decision']['decision'],scope.BELOW)
                    self.assertTrue(a.receipts[-1]['accounting_complete'])
                else:self.assertFalse(a.receipts[-1]['accounting_complete'])


if __name__=='__main__':unittest.main(verbosity=2)

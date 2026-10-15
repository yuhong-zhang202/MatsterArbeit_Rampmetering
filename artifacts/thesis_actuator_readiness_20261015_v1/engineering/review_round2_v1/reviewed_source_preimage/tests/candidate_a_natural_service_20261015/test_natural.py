"""Small composite fake-clock tests; no native traffic or safety evidence."""
import importlib.util
import json
import os
from fractions import Fraction
from pathlib import Path
from types import SimpleNamespace as NS
import tempfile
import time
import unittest
from unittest.mock import patch

from src.candidate_a_natural_service_20261015 import policy, profile, bridge, budget
from src.candidate_a_natural_service_20261015.adapter import StepAdapter
from src.candidate_a_natural_service_20261015.producer import Producer, Feedback, PARAMETERS
from src.candidate_a_native_smoke_20261011.bridge_logs import LogCapture

sp=importlib.util.spec_from_file_location('natural_old_fixture',profile.ROOT/'tests/candidate_a_cumulative_full_catalogue_20261014/test_tracking.py')
old=importlib.util.module_from_spec(sp);sp.loader.exec_module(old)


class NaturalWorld(old.World):
    def __init__(self,xml,case='supply',fault=None):
        super().__init__(xml)
        self.case=case;self.fault=fault;self.vspeed={'M_flow.0':5.};self.departed=[]
        self.simulation.getDepartedIDList=lambda:tuple(self.departed)
        self.inductionloop.getVehicleData=lambda _:[]
        self.green_tokens=set();self.green_begin=None;self.next_vehicle=0
        if fault=='braking':
            self.vehicle.getAcceleration=lambda v:-5. if self.time==608 and v.startswith('M') else 0.
    def simulationStep(self,end):
        old.f.fixture.old.fixture.old.fixture.XMLFakeConnection.simulationStep(self,end)
        self.arrived=[];self.departed=[]
        if end==601 and self.case!='empty':
            self.departed=[f'R_flow.{i}' for i in range(12)]
            self.vspeed.update({v:0. for v in self.departed})
        if end<602 or self.state!='G' or self.case=='empty':return
        token=(self.program,self.switch)
        if token not in self.green_tokens:
            self.green_tokens.add(token)
            self.green_begin=self.switch-(5 if self.program=='T10_G5Y3_NATIVE' else 4)
        if self.case=='late' and end<606:return
        # One actual entry per packet is deliberate: following population can
        # constrain later admission, while N1 must not abort the controller.
        if end==self.green_begin+2 and self.next_vehicle<12:
            self.enter[f'R_flow.{self.next_vehicle}']=end;self.next_vehicle+=1
        if self.fault=='badACK' and end==602:self.state='r'
    def observe(self,conn):
        states,ids,internal,receiver=super().observe(conn)
        if self.fault=='unknown' and self.time==608:receiver['available']=None
        # A deliberately known receiving restriction at the first boundary;
        # bound local/world IDs still pass the original observer validation.
        if self.case=='blocked' and 608<=self.time<616:
            receiver['available']=False;receiver['reason']='SYNTHETIC_KNOWN_RECEIVER_LIMIT'
        return states,ids,internal,receiver


class NaturalTests(unittest.TestCase):
    def packet(self,l,n,held=False,command=None):
        start=l.next_time_s;l.begin_step(start,command)
        l.mark_cycle_start(not held,'SYNTHETIC_LIMIT' if held else '', 'I12_PACKET8' if held else l.cycle['program'])
        for t in range(start,l.cycle['end_s']):
            if t!=start:l.begin_step(t)
            if not held and t==start+l.cycle['max_green_s']:l.close_green(t,'MAX_GREEN_DEADLINE')
            l.end_step(t+1,[f'{start}.{i}' for i in range(n)] if t==start else [],l.motion_at(t))

    def test_nominal_sequence_independent_of_service_no_physical_catchup_and_partial(self):
        allserved=policy.Ledger(750,720);limited=policy.Ledger(750,720)
        for i,n in enumerate((0,1,0,3,2,1)):
            self.packet(allserved,2)
            self.packet(limited,0 if i==2 else n,held=i==2)
            self.assertEqual([x['period_s'] for x in allserved.rows],[x['period_s'] for x in limited.rows])
            self.assertEqual((allserved.C,allserved.E),(limited.C,limited.E))
            self.assertEqual(limited.C-limited.N,(limited.C-limited.E)+(limited.E-limited.N))
        self.assertEqual(limited.E_executed,limited.E-2)
        self.assertEqual(limited.C_selected-limited.C_applied,2)
        l=policy.Ledger(750,620);l.begin_step(600);l.mark_cycle_start(False,'known','I12_PACKET8')
        for t in range(600,610):
            if t!=600:l.begin_step(t,policy.Command('pending',t,900,'SCHEDULED') if t==601 else None)
            l.end_step(t+1,[],'r')
        self.assertIsNone(l.requests['pending']['first_application_s'])
        l.begin_step(610);l.mark_cycle_start(True,signal_program=l.cycle['program']);l.end_step(611,['real.one'],'G')
        self.assertEqual(l.requests['pending']['first_application_s'],610)
        self.assertEqual((l.E,l.E_executed,l.N),(2,0,1))
        self.assertTrue(l.accounting()['partial_cycle'])
        self.assertEqual(l.C,Fraction(750+10*900,3600))
        f=Feedback(PARAMETERS);self.assertEqual(f.update(630,600,630,11+150/70,11+150/70)['rate_clipped_veh_h'],750)
        self.assertEqual(f.update(660,630,660,11,11)['rate_previous_veh_h'],750)

    def run_loop(self,case='supply',fault=None,end=641):
        with tempfile.TemporaryDirectory() as tmp:
            pkg=Path(tmp)/'pkg';out=Path(tmp)/'out';profile.stage_package(profile.ROOT,pkg,out,end);out.mkdir()
            w=NaturalWorld(pkg/'scenario.add.xml',case,fault);a=StepAdapter(w.observe,900,end,yellow_diagnostic_mode=True)
            cap=LogCapture(out);worker=bridge.protected_worker();p=Producer();error=None
            try:
                bridge._diagnostic_loop(w,NS(observe=w.observe,request_phase=worker.request_phase),cap,out,
                    dict(wall_limit_s=300,run_limit_bytes=None,minimum_free_bytes=0),
                    old.f.fixture.old.fixture.old.fixture.fixture.FakeProcess(),time.monotonic(),a,p)
            except Exception as exc:error=exc
            finally:cap.close_handles()
            logs={name:[json.loads(x) for x in path.read_text().splitlines()]
                  for name in ('admission.jsonl','withheld_packets.jsonl','pre_steps.jsonl','post_steps.jsonl','command_events.jsonl','feedback_events.jsonl','policy_duration_requests.jsonl')
                  if (path:=out/name).exists()}
            export=os.environ.get('CA_NATURAL_FIXTURE_EXPORT')
            if export:
                dest=Path(export)/f'{case}_{fault or "none"}_{end}'
                dest.mkdir(parents=True,exist_ok=False)
                for name in ('admission.jsonl','withheld_packets.jsonl','pre_steps.jsonl','post_steps.jsonl',
                             'step_ack.jsonl','command_events.jsonl','feedback_events.jsonl',
                             'policy_duration_requests.jsonl','policy_phase_requests.jsonl','identity_journal.jsonl'):
                    path=out/name
                    if path.exists():(dest/name).write_bytes(path.read_bytes())
                (dest/'SYNTHETIC_RECEIPT.json').write_text(json.dumps(dict(
                    classification='FAKE_WORLD_NO_NATIVE_TRAFFIC_OR_SAFETY_EVIDENCE',
                    last_completed_s=a.last_completed,last_accounted_s=a.last_end,
                    error=None if error is None else type(error).__name__+':'+str(error),
                    accounting=a.ledger.accounting(),cycles=a.ledger.rows,
                    command_records=a.ledger.requests),indent=2))
            return w,a,p,error,logs

    def test_real_loop_empty_one_late_and_receiver_red_wait_then_recovery(self):
        for case in ('empty','supply','late','blocked'):
            with self.subTest(case=case):
                w,a,p,error,logs=self.run_loop(case)
                self.assertIsNone(error)
                self.assertEqual((w.time,a.last_end),(641,641))
                self.assertTrue(all(t>=600 or v=='A_OPEN' or method=='setPhase' for t,method,v in w.requests))
                self.assertFalse(any(method=='setProgram' and value=='CA_C8' for _,method,value in w.requests))
                self.assertEqual(logs['admission.jsonl'][0]['time_s'],600)
                self.assertTrue(logs['admission.jsonl'][0]['initial_same_green'])
                self.assertTrue(any(c['completed'] and sum(c['N_'+m] for m in ('G','y','r'))<2 for c in a.ledger.rows))
                decisions=[e for e in p.events if e['event']=='PROJECT_FEEDBACK_DECISION']
                self.assertEqual([e['global_s'] for e in decisions],[630])
                self.assertEqual(decisions[0]['global_window_begin_s'],600)
                for c in a.ledger.rows:
                    if c['executed'] is False:
                        self.assertEqual(c['phase_exposure_s']['G'],0)
                        self.assertIsNone(c['applied_request_id'])
                        self.assertIsNone(c['applied_command_veh_h'])
                        self.assertFalse(any(c['begin_s']<=t<c['end_s'] and method in ('setProgram','setPhase') for t,method,_ in w.requests))
                if case=='blocked':
                    self.assertTrue(logs['withheld_packets.jsonl'])
                    self.assertLess(a.ledger.E_executed,a.ledger.E)
                    self.assertLess(a.ledger.C_applied,a.ledger.C_selected)
                    first=next(c for c in a.ledger.rows if c['executed'] is False)
                    self.assertTrue(any(c['begin_s']>=first['end_s'] and c['executed'] for c in a.ledger.rows))

    def test_hard_gates_initial_precondition_and_authority_before_native(self):
        for fault in ('braking','badACK','unknown'):
            with self.subTest(fault=fault):
                _,a,_,error,_=self.run_loop(fault=fault)
                self.assertIsNotNone(error);self.assertTrue(a.paused)
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp)
            with self.assertRaisesRegex(ValueError,'NEW_NUMERIC_BUDGET_NOT_APPROVED'):budget.accounting(root)
            # No authority file, launch, connect, reservation or raw allocation.
            self.assertEqual(list(root.iterdir()),[])
        with tempfile.TemporaryDirectory() as tmp:
            pkg=Path(tmp)/'pkg';out=Path(tmp)/'out';profile.stage_package(profile.ROOT,pkg,out,640)
            w=NaturalWorld(pkg/'scenario.add.xml');w.time=600;w.program='A_OPEN';w.phase=0;w.state='G'
            w.vspeed['R_flow.0']=0.
            with self.assertRaisesRegex(ValueError,'UNSUPPORTED_INITIAL_NONEMPTY_OR_BLOCKED_TRANSITION'):
                bridge.admission(w,600,w.observe,'A_OPEN')
            self.assertEqual(w.requests,[])

    def test_exact_complete_endpoint_does_not_prepare_a_future_interval(self):
        w,a,_,error,logs=self.run_loop('blocked',end=640)
        self.assertIsNone(error)
        self.assertEqual((w.time,a.last_end),(640,640))
        self.assertTrue(a.ledger.cycle['completed'])
        self.assertFalse(any(t>=640 for t,_,_ in w.requests))
        self.assertEqual(a.ledger.E,10)
        self.assertLess(a.ledger.E_executed,a.ledger.E)


if __name__=='__main__':unittest.main(verbosity=2)

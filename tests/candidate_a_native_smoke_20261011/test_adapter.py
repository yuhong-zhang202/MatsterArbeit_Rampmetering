"""Fake-connection dispatch/accounting tests; never a native behavior test."""
import json
from pathlib import Path
import subprocess
import sys
import unittest
from types import SimpleNamespace
from src.candidate_a_native_smoke_20261011.adapter import StepAdapter, DiagnosticStop, ROUTES, STORAGE, INGRESS, INTERNAL
from src.candidate_a_qualification_20261008.safety import Vehicle
from src.candidate_a_qualification_20261008.actor import CycleLedger


class FakeConnection:
    def __init__(self, time=1200):
        self.time = time
        self.vehicles = {'R_flow.1':.04573822948686786,'M_flow.1':5.0}
        self.accel = {v:0.0 for v in self.vehicles}
        self.modes = {v:31 for v in self.vehicles}
        self.storage = ['R_flow.1']
        self.internal = []
        self.receiver = True
        self.departed = []
        self.arrived = []
        self.collisions = 0
        self.simulation = SimpleNamespace(getTime=lambda:self.time,getPendingVehicles=lambda:(),
            getArrivedIDList=lambda:tuple(self.arrived),getDepartedIDList=lambda:tuple(self.departed),
            getCollidingVehiclesNumber=lambda:self.collisions,getStartingTeleportNumber=lambda:0,getEndingTeleportNumber=lambda:0)
        self.vehicle = SimpleNamespace(getIDList=lambda:tuple(self.vehicles),getLoadedIDList=lambda:(),
            getTypeID=lambda v:'technical_passenger',getRoute=lambda v:ROUTES[v.split('_')[0]],
            getSpeedMode=lambda v:self.modes[v],getLaneChangeMode=lambda v:1621,
            getSpeed=lambda v:self.vehicles[v],getAcceleration=lambda v:self.accel[v],
            getLaneID=lambda v:INTERNAL if v in self.internal else STORAGE if v in self.storage else 'main_up_0',
            getAccel=lambda v:2.6,getDecel=lambda v:4.5,getEmergencyDecel=lambda v:9.,getTau=lambda v:1.,
            getActionStepLength=lambda v:1.,getImperfection=lambda v:.5,getMaxSpeed=lambda v:55.55555555555556)
        self.lane = SimpleNamespace(getLength=lambda l:{STORAGE:204.49,INGRESS:113.08,INTERNAL:81.98}[l],
            getLastStepVehicleIDs=lambda l:tuple(self.storage if l==STORAGE else self.internal if l==INTERNAL else []))
        self.trafficlight = SimpleNamespace(getControlledLinks=lambda t:((('ramp_storage_0','ramp_accel_0',INTERNAL),),),
            getProgram=lambda t:'CA_C24' if self.time>=1200 else 'CA_C8',getPhase=lambda t:self.phase,
            getRedYellowGreenState=lambda t:self.state,getNextSwitch=lambda t:self.switch)
        self.phase,self.state,self.switch=(0,'G',1203) if time>=1200 else (1,'y',603)
    def observe(self, conn):
        values=[Vehicle(v,'storage',203.48800081023348,self.vehicles[v],5,2.5,2.6,4.5,1,1,'technical_passenger') for v in self.storage]
        return values,{STORAGE:tuple(self.storage),INGRESS:()}, {v:{} for v in self.internal}, {'available':self.receiver}
    def advance_fake(self):
        if self.time == self.switch:
            self.phase = 1 if self.phase==0 else 2
            self.state = 'y' if self.phase==1 else 'r'
            self.switch += 3 if self.phase==1 else 18
        self.time += 1


def warning(conn, text=''):
    return {'time_begin_s':conn.time-1,'time_end_s':conn.time,'coverage':'CALLER_DECLARED_INTERVAL',
            'source':'OFFLINE_FAKE_LOG_NOT_NATIVE','byte_start':0,'byte_end':len(text.encode()),'text':text}


def at_red():
    conn=FakeConnection();adapter=StepAdapter(conn.observe)
    for _ in range(6):
        adapter.prepare_step(conn,conn.time);conn.advance_fake();adapter.reconcile_step(conn,warning(conn))
    return adapter,conn


class AdapterTests(unittest.TestCase):
    def test_unsafe_shadow_is_advisory_then_mandatory_pause(self):
        a,c=at_red();before=a.prepare_step(c,1206)
        self.assertFalse(before['shadow_envelope']['safe'])
        self.assertFalse(before['step_advance_performed'])
        c.advance_fake();r=a.reconcile_step(c,warning(c))
        self.assertEqual(r['status'],'MANDATORY_REVIEW_PAUSE_NO_AUTOMATIC_CONTINUATION')
        self.assertEqual(r['accounting']['E'],0)
        self.assertAlmostEqual(r['accounting']['C'],7/12)
        with self.assertRaises(DiagnosticStop):a.prepare_step(c,1207)
    def test_invalid_modes_and_receiver_block_before_observed_advance(self):
        for failure in ['mode','receiver']:
            with self.subTest(failure=failure):
                c=FakeConnection();a=StepAdapter(c.observe)
                if failure=='mode':c.modes['M_flow.1']=0
                else:c.receiver=False
                with self.assertRaises(DiagnosticStop):a.prepare_step(c,1200)
                self.assertEqual(c.time,1200);self.assertIsNone(a.last_completed)
    def test_red_crossing_keeps_accounted_observed_prefix(self):
        a,c=at_red();a.prepare_step(c,1206);c.advance_fake();c.storage=[];c.internal=['R_flow.1']
        with self.assertRaisesRegex(DiagnosticStop,'RED_CROSSING'):a.reconcile_step(c,warning(c))
        self.assertEqual(a.ledger.N,1);self.assertEqual(a.ledger.E,0)
        self.assertEqual(a.receipts[-1]['actual_crossings'][0]['motion_signal_state'],'r')
    def test_mainline_braking_is_monitored(self):
        c=FakeConnection();a=StepAdapter(c.observe);a.prepare_step(c,1200);c.advance_fake();c.vehicles['M_flow.1']=0.1
        with self.assertRaisesRegex(DiagnosticStop,'ORDINARY_BRAKING_EXCEEDED:M_flow.1'):a.reconcile_step(c,warning(c))
        self.assertEqual(a.last_completed,a.last_end)
    def test_unknown_identity_change_preserves_unaccounted_completed_marker(self):
        c=FakeConnection();a=StepAdapter(c.observe);a.prepare_step(c,1200);c.advance_fake();del c.vehicles['M_flow.1']
        with self.assertRaisesRegex(DiagnosticStop,'UNRECONCILED_WORLD_ID_CHANGE'):a.reconcile_step(c,warning(c))
        self.assertEqual(a.last_completed,1201);self.assertIsNone(a.last_end);self.assertIsNotNone(a.pending)
        self.assertFalse(a.receipts[-1]['accounting_complete'])
    def test_precontrol_red_and_warning_not_exempt(self):
        c=FakeConnection(603);a=StepAdapter(c.observe);before=a.prepare_step(c,603)
        self.assertEqual(before['motion'],'r');c.advance_fake()
        with self.assertRaisesRegex(DiagnosticStop,'NATIVE_WARNING'):a.reconcile_step(c,warning(c,'emergency braking'))
        self.assertEqual(a.receipts[-1]['time_end_s'],604)
    def test_three_complete_cycles_nominal_accounting_not_rate_qualification(self):
        ledger=CycleLedger(1200)
        for t in range(1200,1272):
            new,cycle=ledger.begin_step(t,300)
            if new:ledger.mark_cycle_start(True)
            motion=ledger.envelope.state_at(t-cycle['begin_s'],24)
            ids=[f'R_fake.{t}'] if t-cycle['begin_s'] in [0,1] else []
            ledger.end_step(t+1,ids,motion)
        self.assertEqual(len(ledger.rows),3);self.assertEqual(ledger.accounting()['C'],6)
        self.assertEqual(ledger.E,6);self.assertEqual(ledger.N,6)
    def test_missing_warning_and_post_program_are_not_silent(self):
        for failure in ['missing_warning','program']:
            with self.subTest(failure=failure):
                c=FakeConnection();a=StepAdapter(c.observe);a.prepare_step(c,1200);c.advance_fake()
                if failure=='program':c.trafficlight.getProgram=lambda t:'UNKNOWN'
                with self.assertRaises(DiagnosticStop):a.reconcile_step(c,None if failure=='missing_warning' else warning(c))
                self.assertEqual(a.last_completed,1201);self.assertTrue(a.receipts)
    def test_post_getter_exception_is_terminal_and_accounted(self):
        c=FakeConnection();a=StepAdapter(c.observe);a.prepare_step(c,1200);c.advance_fake()
        def failed_getter(vid):raise OSError('fake getter unavailable')
        c.vehicle.getAcceleration=failed_getter
        with self.assertRaises(OSError):a.reconcile_step(c,warning(c))
        self.assertTrue(a.paused);self.assertEqual(a.last_completed,a.last_end)
        self.assertTrue(a.receipts[-1]['accounting_complete'])
        self.assertIn('OSError',a.receipts[-1]['terminal_reason'])
        with self.assertRaises(DiagnosticStop):a.prepare_step(c,1201)
    def test_cli_plan_only_and_launch_rejected(self):
        path=Path('scripts/candidate_a_native_smoke_20261011_v1/plan.py')
        p=subprocess.run([sys.executable,str(path)],text=True,capture_output=True)
        self.assertEqual(p.returncode,0);j=json.loads(p.stdout)
        self.assertFalse(j['SUMO_launch_authorized']);self.assertFalse(j['native_launch_bridge_implemented'])
        refused=subprocess.run([sys.executable,str(path),'--launch'],text=True,capture_output=True)
        self.assertEqual(refused.returncode,2)

if __name__=='__main__':unittest.main()

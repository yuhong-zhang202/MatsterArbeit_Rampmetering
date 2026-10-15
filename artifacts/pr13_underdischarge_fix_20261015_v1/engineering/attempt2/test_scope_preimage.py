"""Focused offline diagnostic fixtures; no SUMO process or physical evidence."""
import importlib.util
import json
from fractions import Fraction
from pathlib import Path
from types import SimpleNamespace
import tempfile
import time
import unittest
from unittest.mock import patch

from src.candidate_a_cumulative_full_catalogue_20261014.policy import Command, Ledger as HistoricalLedger
from src.candidate_a_cumulative_full_catalogue_20261014 import profile
from src.candidate_a_native_smoke_20261011.bridge_logs import LogCapture
from src.candidate_a_native_yellow_minqual_20261015 import bridge as historical_bridge
from src.candidate_a_service_scope_20261015 import bridge
from src.candidate_a_service_scope_20261015.adapter import StepAdapter
from src.candidate_a_service_scope_20261015.policy import Ledger, PURPOSE, UNDER_TARGET, DiagnosticTargetNotMet

spec = importlib.util.spec_from_file_location('service_scope_fixture', profile.ROOT/'tests/candidate_a_cumulative_full_catalogue_20261014/test_tracking.py')
fixture = importlib.util.module_from_spec(spec)
spec.loader.exec_module(fixture)


class SyntheticProducer:
    # Existing loop accepts terminal partial packets in this mode. This is a
    # synthetic 750 request fixture, not a real Feedback decision or E1 trace.
    mode = 'real_alinea'
    def __init__(self):
        self.events = []
    def command_at(self, conn, t):
        return Command('feedback:synthetic750', t, 750, 'SCHEDULED') if t == 1200 else None
    def after_ack(self, conn, end):
        pass


class ScopeTests(unittest.TestCase):
    def finish_packet(self, ledger, count):
        begin = ledger.next_time_s
        ledger.begin_step(begin)
        ledger.mark_cycle_start(True)
        for t in range(begin, ledger.cycle['end_s']):
            if t != begin:
                ledger.begin_step(t)
            if t == begin+ledger.cycle['max_green_s']:
                ledger.close_green(t, 'MAX_GREEN_DEADLINE')
            ledger.end_step(t+1, [f'synthetic.{begin}.{i}' for i in range(count)] if t == begin else [], ledger.motion_at(t))

    def test_explicit_use_gate_and_raw_ledger_identity(self):
        for purpose in (None, True, 'FORMAL', 'GENERAL', 'OFFLINE', ''):
            with self.subTest(purpose=purpose), self.assertRaisesRegex(ValueError, 'UNSUPPORTED_USE'):
                StepAdapter(lambda _: None, purpose=purpose)
        with self.assertRaises(TypeError):
            Ledger()
        old = HistoricalLedger(750, 1220)
        new = Ledger(750, 1220, purpose=PURPOSE)
        self.assertEqual(new.accounting(), old.accounting())
        self.finish_packet(old, 2)
        self.finish_packet(new, 2)
        new.assess_completed_packet()
        for key, value in old.accounting().items():
            self.assertEqual(new.accounting()[key], value)
        new.begin_step(1210)
        old.begin_step(1210)
        self.assertEqual(new.cycle['packet_selection'], old.cycle['packet_selection'])

    def test_complete_under_target_is_neutral_stop_no_next_packet_or_recovery(self):
        for count in (0, 1):
            with self.subTest(count=count):
                q = Ledger(750, 1220, purpose=PURPOSE)
                self.finish_packet(q, count)
                evidence = q.assess_completed_packet()
                self.assertEqual((q.C, q.E, q.N), (Fraction(25, 12), 2, count))
                self.assertEqual(evidence['status'], UNDER_TARGET)
                self.assertFalse(evidence['actuator_fault_established'])
                self.assertEqual(evidence['cause'], 'UNESTABLISHED')
                self.assertEqual(evidence['requested_minus_actual_exact_fraction'], str(q.C-q.N))
                with self.assertRaises(DiagnosticTargetNotMet):
                    q.begin_step(1210, Command('later', 1210, 900, 'SCHEDULED'))
                self.assertEqual(len(q.rows), 1)
                self.assertNotIn('later', q.requests)
                self.assertEqual((q.C, q.E, q.N), (Fraction(25, 12), 2, count))
        q = Ledger(750, 1210, purpose=PURPOSE)
        self.finish_packet(q, 3)
        self.assertEqual(q.assess_completed_packet()['status'], 'SERVICE_PACKET_QUOTA_EXCEEDED')
        with self.assertRaisesRegex(ValueError, 'SERVICE_PACKET_QUOTA_EXCEEDED'):
            q.require_diagnostic_target()

    def test_partial_pending_and_unknown_are_not_filled_or_passed(self):
        q = Ledger(750, 1203, purpose=PURPOSE)
        for t in range(1200, 1203):
            cmd = Command('pending', t, 900, 'SCHEDULED') if t == 1201 else None
            new, _ = q.begin_step(t, cmd)
            if new:
                q.mark_cycle_start(True)
            q.end_step(t+1, ['synthetic.one'] if t == 1200 else [], 'G')
        self.assertIsNone(q.assess_completed_packet())
        q.require_diagnostic_target()
        self.assertEqual((q.C, q.E, q.N), (Fraction(17, 24), 0, 1))
        self.assertTrue(q.accounting()['partial_cycle'])
        self.assertIsNone(q.requests['pending']['first_application_s'])
        self.assertIsNone(q.accounting()['diagnostic_target_status'])
        r = Ledger(750, 1220, purpose=PURPOSE)
        self.finish_packet(r, 2)
        with self.assertRaisesRegex(ValueError, 'UNKNOWN_COMPLETED_SERVICE_DIAGNOSTIC'):
            r.begin_step(1210)

    def run_fixture(self, kind, end=1218, fault=None):
        with tempfile.TemporaryDirectory() as tmp:
            pkg, out = Path(tmp)/'pkg', Path(tmp)/'out'
            profile.stage_package(profile.ROOT, pkg, out, end)
            out.mkdir()
            w = fixture.World(pkg/'scenario.add.xml', early=False)
            if kind in ('empty', 'one', 'late'):
                w.vspeed = {v: s for v, s in w.vspeed.items() if not v.startswith('R') or (kind != 'empty' and v == 'R_flow.0')}
            w.omit_second = kind != 'two'
            if kind == 'late':
                old_step = w.simulationStep
                def step(target):
                    old_step(target)
                    if 1201 <= target < 1204:
                        w.enter.pop('R_flow.0', None)
                    if target == 1204:
                        w.enter['R_flow.0'] = target
                w.simulationStep = step
            if fault == 'final_braking':
                w.vehicle.getAcceleration = lambda vid: -5. if w.time == 1210 and vid.startswith('M') else 0.
            if fault == 'unknown_receiver':
                old_observe = w.observe
                def observe(conn):
                    vehicles, ids, internal, receiver = old_observe(conn)
                    if w.time >= 1200:
                        receiver['available'] = None
                    return vehicles, ids, internal, receiver
                w.observe = observe
            if fault == 'admission_receiver':
                old_observe = w.observe
                def observe(conn):
                    vehicles, ids, internal, receiver = old_observe(conn)
                    if w.time == 1200:
                        receiver['available'] = False
                    return vehicles, ids, internal, receiver
                w.observe = observe
            a = StepAdapter(w.observe, 750, end, purpose=PURPOSE)
            worker = historical_bridge.protected_worker()
            cap = LogCapture(out)
            error = None
            try:
                bridge._diagnostic_loop(w, SimpleNamespace(observe=w.observe, request_phase=worker.request_phase), cap,
                    out, dict(wall_limit_s=300, minimum_free_bytes=0, run_limit_bytes=None),
                    fixture.f.fixture.old.fixture.old.fixture.fixture.FakeProcess(), time.monotonic(),
                    a, SyntheticProducer(), purpose=PURPOSE)
            except ValueError as exc:
                error = exc
            finally:
                cap.close_handles()
            receipt = json.loads((out/'service_scope_receipt.json').read_text())
            events = [json.loads(line) for line in (out/'service_scope_events.jsonl').read_text().splitlines()]
            return w, a, error, receipt, events

    def test_real_adapter_loop_records_supply_readiness_wait_and_stops_before_new_motion(self):
        for kind in ('empty', 'one', 'late', 'receiver_wait'):
            with self.subTest(kind=kind):
                w, a, error, receipt, events = self.run_fixture(kind)
                self.assertIsInstance(error, DiagnosticTargetNotMet)
                self.assertEqual((w.time, a.last_end, a.ledger.E, a.ledger.N), (1210, 1210, 2, 0 if kind == 'empty' else 1))
                self.assertEqual(receipt['status'], UNDER_TARGET)
                self.assertFalse(receipt['actuator_fault_established'])
                self.assertEqual(len(a.ledger.rows), 1)
                self.assertTrue(a.receipts[-1]['accounting_complete'])
                self.assertFalse(any(t >= 1210 for t, method, value in w.requests))
                assessment = next(event for event in events if event.get('event') == 'FINITE_PACKET_DIAGNOSTIC_ASSESSED')
                self.assertEqual(assessment['status'], UNDER_TARGET)
                context = assessment['service_context']
                self.assertEqual([frame['time_s'] for frame in context], list(range(1200, 1210)))
                if kind == 'empty':
                    self.assertTrue(all(not frame['storage_ids'] for frame in context))
                if kind == 'one':
                    self.assertEqual(context[0]['storage_ids'], ['R_flow.0'])
                if kind == 'late':
                    self.assertEqual(a.ledger.rows[0]['crossing_ids'], ['R_flow.0'])
                    self.assertIn('R_flow.0', context[3]['storage_ids'])
                if kind == 'receiver_wait':
                    self.assertTrue(any((frame['native_receiver_decision'] or {}).get('decision') == 'WAIT_NATIVE_FOLLOWING' for frame in context))

    def test_terminal_complete_partial_safety_priority_and_entry_gate(self):
        _, a, error, receipt, _ = self.run_fixture('one', end=1210)
        self.assertIsInstance(error, DiagnosticTargetNotMet)
        self.assertTrue(a.ledger.cycle['completed'])
        self.assertEqual(receipt['status'], UNDER_TARGET)
        _, a, error, receipt, _ = self.run_fixture('two', end=1212)
        self.assertIsNone(error)
        self.assertTrue(receipt['partial_cycle'])
        self.assertIsNone(receipt['service_diagnostic'])
        for fault in ('final_braking', 'unknown_receiver', 'admission_receiver'):
            with self.subTest(fault=fault):
                _, a, error, receipt, events = self.run_fixture('one', fault=fault)
                self.assertIsNotNone(error)
                self.assertNotIsInstance(error, DiagnosticTargetNotMet)
                self.assertEqual(receipt['status'], 'HARD_OR_UNKNOWN_GATE_STOP')
                self.assertFalse(any(event.get('event') == 'FINITE_PACKET_DIAGNOSTIC_ASSESSED' for event in events))
        _, a, error, receipt, _ = self.run_fixture('two', end=1210)
        self.assertIsNone(error)
        self.assertEqual((a.ledger.E, a.ledger.N), (2, 2))
        self.assertFalse(receipt['general_service_qualified'])
        with patch.object(bridge, 'historical_loop') as inherited:
            for purpose in ('FORMAL', 'GENERAL'):
                with self.subTest(purpose=purpose), self.assertRaisesRegex(ValueError, 'UNSUPPORTED_USE'):
                    bridge._diagnostic_loop(None, None, None, None, None, None, None, a, None, purpose=purpose)
            with self.assertRaisesRegex(ValueError, 'EXPLICIT_DIAGNOSTIC_ADAPTER_REQUIRED'):
                bridge._diagnostic_loop(None, None, None, None, None, None, None, object(), None, purpose=PURPOSE)
            inherited.assert_not_called()


if __name__ == '__main__':
    unittest.main(verbosity=2)

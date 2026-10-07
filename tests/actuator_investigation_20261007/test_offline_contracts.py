"""Bounded technical arithmetic/regression checks; no SUMO starts."""
from fractions import Fraction
from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "scripts/formal_development_20261007_v1"))
from src.actuator_investigation_20261007.offline_contracts import (
    CycleEnvelope, SafeOpportunityLedger)
from control import PulseScheduler


class OfflineContractChecks(unittest.TestCase):
    def test_original_scheduler_ideal_hour_all_integer_rates(self):
        for rate in range(300, 901):
            scheduler = PulseScheduler()
            greens = sum(scheduler.step(t, rate)["slot_scheduled"]
                         for t in range(600, 4200))
            self.assertEqual(greens, rate)
            self.assertAlmostEqual(scheduler.dropped_credit, 0, places=8)
            self.assertAlmostEqual(scheduler.credit, 0, places=8)

    def test_original_scheduler_denial_credit_balance(self):
        scheduler = PulseScheduler()
        greens = sum(scheduler.step(t, 900, guard_allowed=(t % 6 == 0))
                     ["slot_scheduled"] for t in range(600, 4200))
        self.assertEqual(greens, 599)
        self.assertAlmostEqual(900, greens + scheduler.dropped_credit
                               + scheduler.credit, places=8)
        self.assertGreater(scheduler.dropped_credit, 299)

    def test_cycle_mapping_full_domain_conditional_two_vehicle_fixture(self):
        # Algebraic feasibility fixture, NOT proposed green/yellow timings.
        envelope = CycleEnvelope(2, 3, 2, 3)
        for rate in range(300, 901):
            periods = envelope.cycle_sequence(rate, 1000)
            ideal_total = Fraction(7200 * 1000, rate)
            self.assertLess(abs(sum(periods) - ideal_total), 1)
            for period in set(periods):
                program = envelope.program(period)
                self.assertEqual(sum(d for _, d in program), period)
                self.assertEqual([s for s, _ in program], ["G", "y", "r"])
                self.assertGreaterEqual(program[2][1], 3)

    def test_single_vehicle_transition_envelope_cannot_claim_900(self):
        envelope = CycleEnvelope(1, 2, 2, 1)
        self.assertEqual(envelope.nominal_maximum_veh_h, 720)
        with self.assertRaises(ValueError):
            envelope.brackets(900)

    def test_single_period_rounding_differs_from_mean_period_mapping(self):
        envelope = CycleEnvelope(1, 1, 1, 1)
        period, rate, error = envelope.closest_single_period(810)
        self.assertEqual(period, 5)
        self.assertEqual(rate, 720)
        self.assertEqual(error, Fraction(1, 9))
        self.assertEqual(sum(envelope.cycle_sequence(810, 9)), 40)

    def test_b_ideal_all_integer_rates(self):
        for rate in range(300, 901):
            ledger = SafeOpportunityLedger()
            for t in range(3600):
                ledger.step(t, rate)
            self.assertEqual(ledger.opportunities, rate)
            self.assertEqual(ledger.credit, 0)

    def test_b_classifies_denials_and_preserves_exact_balance(self):
        ledger = SafeOpportunityLedger(bank_limit=1)
        reasons = set()
        for t in range(300):
            reasons.add(ledger.step(t, 900, demand=(t >= 20),
                                   receiver=(t >= 40), safe_gap=(t >= 60))
                        ["reason"])
        self.assertTrue({"NO_DEMAND", "RECEIVER_BLOCKED", "SAFE_GAP_DENIED"}
                        <= reasons)
        self.assertEqual(ledger.command_credit,
                         ledger.opportunities + ledger.credit + ledger.dropped_credit)

    def test_b_bank_does_not_bypass_service_headway(self):
        ledger = SafeOpportunityLedger()
        released = []
        for t in range(300):
            if ledger.step(t, 900, safe_gap=(t >= 100))["opportunity"]:
                released.append(t)
        self.assertTrue(all(b - a >= 4 for a, b in zip(released, released[1:])))
        self.assertLess(ledger.opportunities, 75)
        self.assertGreater(ledger.credit, 24)

    def test_b_six_second_safe_headway_is_not_900_capable(self):
        ledger = SafeOpportunityLedger(minimum_headway_s=6)
        for t in range(3600):
            ledger.step(t, 900)
        self.assertEqual(ledger.opportunities, 600)
        self.assertEqual(ledger.credit, 300)

    def test_reject_invalid_timing_rate_and_replay(self):
        with self.assertRaises(ValueError):
            CycleEnvelope(2, 0, 1, 1)
        ledger = SafeOpportunityLedger()
        with self.assertRaises(ValueError):
            ledger.step(1, 900)
        with self.assertRaises(ValueError):
            ledger.step(0, 901)


if __name__ == "__main__":
    unittest.main()

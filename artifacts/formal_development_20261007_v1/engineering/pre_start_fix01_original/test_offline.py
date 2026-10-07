"""Meaningful offline boundary/state tests; no SUMO/TraCI import or start."""
import math
import unittest
from queue_protection import QueueOverride, QueueParameters, risk_snapshot
from control import Feedback, FeedbackParameters, PulseScheduler


class QueueTests(unittest.TestCase):
    def test_confirmation_hysteresis_and_release(self):
        q = QueueOverride()
        for t in range(600, 609):
            self.assertFalse(q.step(t, 261.03, 450)["override_active"])
        self.assertEqual(q.step(609, 261.03, 450)["final_command_veh_h"], 900)
        for t in range(610, 640):
            self.assertTrue(q.step(t, 180, 300)["override_active"])
        for t in range(640, 669):
            self.assertTrue(q.step(t, 102.245, 370)["override_active"])
        r = q.step(669, 102.245, 370)
        self.assertEqual(r["transition"], "RELEASE")
        self.assertEqual(r["final_command_veh_h"], 370)

    def test_interrupted_streak_and_invalid_sample(self):
        q = QueueOverride()
        for t in range(600, 605): q.step(t, 300, 500)
        self.assertEqual(q.step(605, 260, 500)["trigger_streak_s"], 0)
        with self.assertRaises(ValueError): q.step(606, math.nan, 500)
        self.assertEqual(q.next_time_s, 606)

    def test_internal_geometry_and_shared_only(self):
        lengths = {"shared_approach_0":238.80, ":urban_diverge_1_0":113.08, "ramp_storage_0":204.49}
        r = risk_snapshot([("R_flow.0", ":urban_diverge_1_0", 61.54, 1.0, 5.0)], lengths)
        self.assertAlmostEqual(r["risk_extent_m"], 261.03)
        r = risk_snapshot([("R_flow.1", "shared_approach_0", 200, 0, 5)], lengths)
        self.assertEqual(r["risk_extent_m"], 0)
        self.assertGreater(r["shared_low_R_extent_m"], 317.57)
        with self.assertRaises(ValueError): risk_snapshot([], {"ramp_storage_0":204.49})

    def test_speed_and_class_boundary(self):
        lengths = {"shared_approach_0":238.80, ":urban_diverge_1_0":113.08, "ramp_storage_0":204.49}
        r = risk_snapshot([("R_flow.0", "ramp_storage_0", 0, 1.389, 5),
                           ("U_flow.0", ":urban_diverge_1_0", 0, 0, 5)], lengths)
        self.assertEqual(r["risk_extent_m"], 0)

    def test_nominal_state_is_independent(self):
        f = Feedback(FeedbackParameters(11, 70, 300, 900, 900))
        q = QueueOverride()
        for t in range(600, 631):
            if t == 630: f.update(t, t-30, t, 15, 15)
            q.step(t, 300, f.rate)
        self.assertEqual(f.rate, 620)
        self.assertTrue(q.active)
        self.assertEqual(f.update(660, 630, 660, 15, 15)["rate_previous_veh_h"], 620)

    def test_final_command_credit_without_burst(self):
        p = PulseScheduler(); greens = []
        for t in range(600, 660):
            r = p.step(t, 900, t >= 620)
            if r["slot_scheduled"]: greens.append(t)
        self.assertTrue(all(b-a >= 3 for a,b in zip(greens,greens[1:])))
        self.assertGreater(p.dropped_credit, 0)


if __name__ == "__main__": unittest.main()

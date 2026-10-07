"""Meaningful offline boundary/state tests; no SUMO/TraCI import or start."""
import math
import ast
import copy
import inspect
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
from queue_protection import QueueOverride, QueueParameters, risk_snapshot
from control import Feedback, FeedbackParameters, PulseScheduler
import v15_worker


class WorkerCardTests(unittest.TestCase):
    def card(self):
        return dict(guard_revision=v15_worker.REVISION, base_output="unused", package="unused", output="unused",
                    run_id="OFFLINE_ONLY", mode="ALINEA", treatment="T2",
                    feedback=dict(v15_worker.PARAMETERS),
                    meter_controlled_link={"storage_length_m":204.49},
                    startup_deadline_s=60, resources={"startup_limit_s":60})

    def test_complete_card_and_fixed_startup(self):
        self.assertTrue(v15_worker.validate_worker_card(self.card()))
        for value in (0, 30, 61, None):
            c=self.card(); c["startup_deadline_s"]=value
            with self.assertRaises(ValueError): v15_worker.validate_worker_card(c)

    def test_every_required_key_fails_before_spawn(self):
        for path in v15_worker.WORKER_CARD_PATHS:
            c=copy.deepcopy(self.card()); node=c
            for key in path[:-1]: node=node[key]
            del node[path[-1]]
            with self.subTest(path=path), self.assertRaises(ValueError):
                v15_worker.validate_worker_card(c)

    def test_registry_covers_actual_worker_card_reads(self):
        def chain(n):
            if isinstance(n,ast.Name) and n.id=="card": return ()
            if isinstance(n,ast.Subscript) and isinstance(n.slice,ast.Constant) and isinstance(n.slice.value,str):
                parent=chain(n.value)
                if parent is not None:return parent+(n.slice.value,)
            return None
        tree=ast.parse(inspect.getsource(v15_worker.worker))
        actual={chain(n) for n in ast.walk(tree) if isinstance(n,ast.Subscript) and chain(n) is not None}
        self.assertTrue(actual.issubset(set(v15_worker.WORKER_CARD_PATHS)), actual)
        worker_lines=inspect.getsource(v15_worker.worker)
        self.assertLess(worker_lines.index("validate_worker_card(card)"), worker_lines.index("import traci"))
        self.assertLess(worker_lines.index("validate_worker_card(card)"), worker_lines.index("subprocess.Popen"))

    def test_worker_missing_startup_never_spawns(self):
        c=self.card(); del c["startup_deadline_s"]
        with tempfile.TemporaryDirectory() as tmp:
            path=Path(tmp)/"card.json"; path.write_text(json.dumps(c))
            with patch.object(v15_worker.subprocess,"Popen") as spawn:
                with self.assertRaisesRegex(ValueError,"startup_deadline_s"):
                    v15_worker.worker(path)
                spawn.assert_not_called()


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


class CorrectedGuardTests(unittest.TestCase):
    def setUp(self):
        from safe_actuator_fix02 import VehicleState
        self.V = VehicleState
        self.kw = dict(storage_length_m=204.49, route_coverage_ok=True,
            leader_lookahead_m=478.67, connected_path_length_m=181.05,
            allowed_downstream_lanes=frozenset(), leader=None, secure_gap_m=None,
            nearest_internal_vehicle_id=None, nearest_internal_rear_clearance_m=math.inf)
        self.front = self.V(203.49, 0, 5, 2.5, 2.6, 4.5)

    def check(self, states, approaching=None):
        from safe_actuator_fix02 import assess_release
        return assess_release(vehicles=states, approaching_vehicles=approaching or {}, **self.kw)

    def test_recorded_counterexample(self):
        from safe_actuator_fix02 import legacy_assess_release, required_pre_green_distance_m
        states = {"R_flow.0":self.front,
                  "R_flow.3":self.V(114.69805754,20.61937210,5,2.5,2.6,4.5)}
        self.assertTrue(legacy_assess_release(vehicles=states, **self.kw)["allowed"])
        d=self.check(states)
        self.assertFalse(d["allowed"])
        self.assertEqual(d["reason"],"FOLLOWER_POST_RED_PREDICTION")
        self.assertGreater(required_pre_green_distance_m(states["R_flow.3"]), 89.79194246)

    def test_boundary_and_stopped_and_moving_follower(self):
        from dataclasses import replace
        from safe_actuator_fix02 import required_pre_green_distance_m
        for speed in (0, 0.099, 0.1, 5, 20.6193721, 30):
            follower=self.V(0,speed,5,2.5,2.6,4.5)
            req=required_pre_green_distance_m(follower)
            follower=replace(follower,position_m=204.49-req)
            self.assertTrue(self.check({"front":self.front,"follower":follower})["allowed"])
            self.assertFalse(self.check({"front":self.front,"follower":replace(follower,position_m=follower.position_m+1e-6)})["allowed"])

    def test_next_speed_bound_implies_unchanged_post(self):
        from dataclasses import replace
        from safe_actuator_fix02 import required_pre_green_distance_m, immediate_red_stop_requirement_m
        for speed in (0,0.099,0.1,5,20.6193721,30,55.55):
            state=self.V(0,speed,5,2.5,2.6,4.5)
            pre=required_pre_green_distance_m(state)
            for fraction in (0,0.001,0.25,0.75,1):
                nxt=(speed+state.accel_m_s2)*fraction
                self.assertGreaterEqual(pre-nxt+1e-9, immediate_red_stop_requirement_m(replace(state,speed_m_s=nxt)))

    def test_entrant_guard_and_coverage_bound(self):
        from safe_actuator_fix02 import qualify_entrant_coverage
        entrant=self.V(-0.01,40,5,2.5,2.6,4.5)
        d=self.check({"front":self.front},{"entrant":entrant})
        self.assertFalse(d["allowed"])
        self.assertEqual(d["unsafe_followers"],("entrant",))
        x=dict(upstream_length_m=113.08,max_speed_m_s=55.55,accel_m_s2=2.6,tau_s=1,action_step_s=1)
        self.assertLess(qualify_entrant_coverage(**x)["maximum_one_step_advance_m"],113.08)
        for field,value in (("max_speed_m_s",111),("tau_s",0.9),("action_step_s",2)):
            with self.assertRaises(ValueError): qualify_entrant_coverage(**{**x,field:value})
        with self.assertRaises(ValueError): self.check({"same":self.front},{"same":entrant})
        with self.assertRaises(ValueError): self.check({"front":self.front},{"entrant":self.V(.01,0,5,2.5,2.6,4.5)})

    def test_legacy_front_and_interlock_preserved(self):
        from safe_actuator_fix02 import legacy_assess_release
        from stage6_safe_actuator_v10 import post_green_red_interlock
        for front in (self.front,self.V(195,12,5,2.5,2.6,4.5)):
            states={"front":front}
            self.assertEqual(self.check(states)["allowed"],legacy_assess_release(vehicles=states,**self.kw)["allowed"])
        d=post_green_red_interlock(expected_front_id="front",crossing_ids=("front",),
            remaining_storage={"follower":self.V(135.57582461,20.87776707,5,2.5,2.6,4.5)},storage_length_m=204.49)
        self.assertTrue(d["abort"])


if __name__ == "__main__": unittest.main()

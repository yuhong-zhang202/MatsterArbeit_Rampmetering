"""Bounded pure tests for the prospective V10 actuator; no SUMO launch."""

import unittest

from src.stage6_safe_actuator_v10 import (
    LeaderState, VehicleState, assess_release, post_green_red_interlock,
    immediate_red_stop_requirement_m, normal_red_stop_requirement_m,
    secure_gap_query,
)


def vehicle(position=200.0, speed=2.0, accel=2.6, decel=4.5):
    return VehicleState(position, speed, 5.0, 2.5, accel, decel)


def release(**changes):
    args = dict(vehicles={"front": vehicle()}, storage_length_m=204.49,
                route_coverage_ok=True, leader_lookahead_m=200.0,
                connected_path_length_m=177.3,
                allowed_downstream_lanes=frozenset({":ramp_mid_0_0", "ramp_accel_0"}),
                leader=None, secure_gap_m=None,
                nearest_internal_vehicle_id=None,
                nearest_internal_rear_clearance_m=float("inf"))
    args.update(changes)
    return assess_release(**args)


class V10SafetyTests(unittest.TestCase):
    def test_high_speed_front_near_stopped_internal_leader_rejected(self):
        front = vehicle(position=203.0, speed=20.0)
        leader = LeaderState("leader", ":ramp_mid_0_0", 8.0, 0.0, 9.0)
        self.assertEqual(secure_gap_query("front", front, leader),
                         {"vehID": "front", "speed": 22.6, "leaderSpeed": 0.0,
                          "leaderMaxDecel": 9.0, "leaderID": "leader"})
        checked = release(vehicles={"front": front}, leader=leader,
                          secure_gap_m=54.0, nearest_internal_vehicle_id="leader",
                          nearest_internal_rear_clearance_m=9.0)
        self.assertFalse(checked["allowed"])
        self.assertEqual(checked["reason"], "LEADER_SECURE_GAP")

    def test_internal_gap_uses_ego_min_gap_once_and_unknown_coverage_blocks(self):
        leader = LeaderState("leader", ":ramp_mid_0_0", 20.0, 8.0, 9.0)
        checked = release(vehicles={"front": vehicle(position=202.49, speed=2.5)},
                          leader=leader, secure_gap_m=2.0,
                          nearest_internal_vehicle_id="leader",
                          nearest_internal_rear_clearance_m=14.0)
        self.assertTrue(checked["allowed"])
        self.assertEqual(release(route_coverage_ok=False)["reason"],
                         "DOWNSTREAM_COVERAGE_UNKNOWN")
        self.assertEqual(release(nearest_internal_vehicle_id="unmapped",
                                 nearest_internal_rear_clearance_m=20.0)["reason"],
                         "INTERNAL_LEADER_MISMATCH")

    def test_post_green_empty_front_can_stop_or_requires_abort(self):
        stopped = post_green_red_interlock(
            expected_front_id="front", crossing_ids=(),
            remaining_storage={"front": vehicle(position=203.49, speed=0.0)},
            storage_length_m=204.49)
        self.assertEqual((stopped["safe_to_red"], stopped["abort"],
                          stopped["empty_green"]), (True, False, True))
        moving = post_green_red_interlock(
            expected_front_id="front", crossing_ids=(),
            remaining_storage={"front": vehicle(position=203.49, speed=3.0)},
            storage_length_m=204.49)
        self.assertEqual((moving["safe_to_red"], moving["abort"],
                          moving["reason"]), (False, True, "UNSAFE_GREEN_TO_RED"))

    def test_post_green_unique_crossing_and_follower_normal_brake(self):
        result = post_green_red_interlock(
            expected_front_id="front", crossing_ids=("front",),
            remaining_storage={"follower": vehicle(position=185.0, speed=1.0)},
            storage_length_m=204.49)
        self.assertTrue(result["safe_to_red"])
        result = post_green_red_interlock(
            expected_front_id="front", crossing_ids=("front",),
            remaining_storage={"follower": vehicle(position=203.49, speed=2.0)},
            storage_length_m=204.49)
        self.assertEqual(result["reason"], "UNSAFE_GREEN_TO_RED")
        result = post_green_red_interlock(
            expected_front_id="front", crossing_ids=("front", "follower"),
            remaining_storage={}, storage_length_m=204.49)
        self.assertEqual(result["reason"], "WRONG_OR_MULTIPLE_CROSSING")

    def test_v14_post_green_red_uses_observed_speed_and_rejects_near_fast_vehicle(self):
        # Preserved V14 state at t=653 after R_flow.0 crossed [652,653).
        far_fast = vehicle(position=125.44165610028782,
                           speed=21.190230157237327)
        self.assertAlmostEqual(204.49 - far_fast.position_m, 79.0483438997122)
        self.assertAlmostEqual(immediate_red_stop_requirement_m(far_fast),
                               72.18199172575846)
        self.assertGreater(normal_red_stop_requirement_m(far_fast),
                           204.49 - far_fast.position_m)
        result = post_green_red_interlock(
            expected_front_id="R_flow.0", crossing_ids=("R_flow.0",),
            remaining_storage={"R_flow.3": far_fast}, storage_length_m=204.49)
        self.assertTrue(result["safe_to_red"])
        near_fast = vehicle(position=195.0, speed=19.77)
        result = post_green_red_interlock(
            expected_front_id="front", crossing_ids=("front",),
            remaining_storage={"follower": near_fast}, storage_length_m=204.49)
        self.assertEqual(result["reason"], "UNSAFE_GREEN_TO_RED")


if __name__ == "__main__":
    unittest.main()

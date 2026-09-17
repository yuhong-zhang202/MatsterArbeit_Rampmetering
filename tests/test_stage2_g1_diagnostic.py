"""Pure file/math tests: no SUMO, netconvert, TraCI or subprocess."""
import importlib.util
from pathlib import Path
import tempfile
import unittest

SOURCE = Path(__file__).resolve().parents[1] / "src/analysis/build_stage2_g1_diagnostic.py"
spec = importlib.util.spec_from_file_location("g1", SOURCE)
g1 = importlib.util.module_from_spec(spec)
spec.loader.exec_module(g1)


def interval(begin=0, speed=10, count=1):
    return g1.e1_row({"id": "e1", "begin": str(begin), "end": str(begin + 30),
                      "flow": str(count * 120), "speed": str(speed), "occupancy": "2",
                      "nVehContrib": str(count), "nVehEntered": str(count)}, "e1", "lane")


class OfflineDiagnosticTests(unittest.TestCase):
    def test_before_step_boundaries(self):
        for t in (30, 1500, 2700):
            self.assertFalse(g1.event_before(t, t))
            self.assertTrue(g1.event_before(t, t + 1))
            self.assertFalse(g1.event_before(-1, t))
            self.assertFalse(g1.event_before(None, t))

    def test_statuses_never_guess_absent_record(self):
        self.assertEqual(g1.vehicle_status(None), "record_missing_unknown")
        self.assertEqual(g1.vehicle_status(None, explicitly_unentered=True), "not_entered")
        self.assertEqual(g1.vehicle_status({"depart": 1500, "arrival": -1}), "entered_unfinished")
        self.assertEqual(g1.vehicle_status({"depart": 0, "arrival": 2700}), "arrived")

    def test_e1_empty_is_missing_speed(self):
        row = interval(speed=-1, count=0)
        self.assertFalse(row["speed_valid"])
        self.assertEqual(row["speed_raw_mps"], -1)
        self.assertEqual(row["flow_vehph"], 0)
        self.assertIsNone(g1.summarize_e1([row], 0, 30)["speed_mps"])

    def test_e1_negative_speed_with_traffic_is_flagged(self):
        self.assertEqual(interval(speed=-1)["missing_reason"], "negative_speed_with_contributions")

    def test_e1_weighted_speed(self):
        out = g1.summarize_e1([interval(speed=10), interval(30, 20, 3)], 0, 60)
        self.assertEqual(out["speed_mps"], 17.5)
        self.assertEqual(out["speed_contribution_denominator"], 4)
        self.assertEqual(out["flow_vehph"], 240)

    def test_numeric_speed_validity_does_not_claim_traffic_state_validity(self):
        row = interval(speed=4.43)
        self.assertTrue(row["speed_valid"])
        notes = g1.measurement_notes([row])
        self.assertIn("not traffic-state validity", notes["speed_valid_definition"])
        self.assertEqual(notes["specific_reviewed_cases"], [])

    def test_reviewed_flags_require_exact_source_record(self):
        row = g1.e1_row({"id": "merge_upstream_e1_l1", "begin": "1500", "end": "1530", "flow": "120", "speed": "4.43", "occupancy": ".43", "nVehContrib": "1", "nVehEntered": "0"}, "merge_upstream_e1_l1", "main_up_1")
        self.assertEqual(len(g1.measurement_notes([row])["specific_reviewed_cases"]), 1)
        row["speed_raw_mps"] = 4.44
        self.assertEqual(g1.measurement_notes([row])["specific_reviewed_cases"], [])

    def test_interval_boundaries_and_missing_fields(self):
        g1.check_intervals([interval(), interval(30)], end=60)
        for rows in ([interval(), interval()], [interval(30)], [interval(), interval(60)]):
            with self.assertRaises(ValueError):
                g1.check_intervals(rows, end=60)
        with self.assertRaises(ValueError):
            g1.e1_row({"id": "e1"}, "e1", "lane")
        self.assertEqual(g1.summarize_e1([interval(), interval(30)], 30, 60)["nVehContrib"], 1)

    def test_merge_bracket_boundary_not_exact_time(self):
        event = g1.crossing_event("R_flow.0", (29, ":freeway_merge_0_0"), (30, "main_down_0"))
        self.assertEqual(event["status"], "bracketed")
        self.assertTrue(event["boundary_30s_ambiguous"])
        self.assertIn("not_exact", event["time_precision"])
        self.assertFalse(g1.crossing_event("R_flow.0", (30, "ramp_accel_0"), (31, "main_down_0"))["boundary_30s_ambiguous"])

    def test_merge_uncertain_cases(self):
        for previous, reason in ((None, "first_seen_downstream"), ((1, "ramp_accel_0"), "non_unit_sample_gap"), ((2, "main_up_0"), "previous_lane_not_ramp_path")):
            self.assertEqual(g1.crossing_event("R_flow.0", previous, (3, "main_down_0"))["reason"], reason)

    def test_fcd_internal_crossing_lane_change_and_unsampled_end(self):
        with tempfile.TemporaryDirectory() as root:
            path = Path(root) / "fcd.xml"
            path.write_text('<fcd-export><timestep time="0"><vehicle id="R_flow.0" lane=":freeway_merge_0_0" speed="1"/></timestep><timestep time="1"><vehicle id="R_flow.0" lane="main_down_0" speed="1"/></timestep><timestep time="2"><vehicle id="R_flow.0" lane="main_down_1" speed="1"/></timestep></fcd-export>')
            rows, events, check = g1.parse_fcd(path, {"R_flow.0"})
            self.assertEqual(len(events), 1)
            self.assertEqual(events[0]["first_downstream_time_s"], 1)
            self.assertTrue(all(r["vehicle_samples"] is None for r in rows if r["time_s"] == 2700))
            self.assertTrue(all(r["vehicle_samples"] == 0 for r in rows if r["time_s"] == 0 and r["lane_id"] == "main_up_0"))
            self.assertIn(3, check["missing_times_before_end"])

    def test_fcd_duplicate_rejected(self):
        with tempfile.TemporaryDirectory() as root:
            path = Path(root) / "fcd.xml"
            path.write_text('<fcd-export><timestep time="0"><vehicle id="R_flow.0" lane="ramp_accel_0" speed="1"/><vehicle id="R_flow.0" lane="ramp_accel_0" speed="1"/></timestep></fcd-export>')
            with self.assertRaises(ValueError):
                g1.parse_fcd(path, {"R_flow.0"})

    def test_refuse_existing_and_nested_outputs(self):
        with tempfile.TemporaryDirectory() as root:
            existing = Path(root) / "exists"
            existing.mkdir()
            with self.assertRaises(FileExistsError):
                g1.reserve_directories([Path(root) / "new", existing])
            self.assertFalse((Path(root) / "new").exists())
            with self.assertRaises(FileExistsError):
                g1.reserve_directories([Path(root) / "a", Path(root) / "a/b"])

    def test_source_hash_change_detected(self):
        with tempfile.TemporaryDirectory() as root:
            path = Path(root) / "source"
            path.write_text("before")
            hashes = {str(path): g1.digest(path)}
            g1.verify_hashes(hashes)
            path.write_text("after")
            with self.assertRaises(ValueError):
                g1.verify_hashes(hashes)


if __name__ == "__main__":
    unittest.main()

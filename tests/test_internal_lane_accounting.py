"""Small deterministic fixtures for explicit internal-lane FCD accounting."""
from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from src.analysis.internal_lane_accounting import analyze_fcd_accounting, audit_run_observation_outputs, compare_xml_record_semantics


NETWORK = """<net><edge id=":urban_diverge_1" function="internal"><lane id=":urban_diverge_1_0"/></edge><edge id=":ramp_mid_0" function="internal"><lane id=":ramp_mid_0_0"/></edge><edge id="ramp_storage"><lane id="ramp_storage_0"/></edge><edge id="ramp_accel"><lane id="ramp_accel_0"/></edge><edge id="shared_approach"><lane id="shared_approach_0"/></edge><edge id="urban_in"><lane id="urban_in_0"/></edge><edge id="main_down"><lane id="main_down_0"/><lane id="main_down_1"/></edge><edge id=":freeway_merge_0" function="internal"><lane id=":freeway_merge_0_0"/></edge></net>"""
FCD = """<fcd-export><timestep time="0"><vehicle id="R_a" lane=":urban_diverge_1_0" speed="0.0"/><vehicle id="R_b" lane="ramp_storage_0" speed="2"/><vehicle id="mystery" lane="unknown_0" speed="0"/></timestep><timestep time="1"><vehicle id="R_a" lane=":ramp_mid_0_0" speed="0.1"/><vehicle id="U_a" lane="shared_approach_0" speed="0"/><vehicle id="R_dup" lane="ramp_accel_0" speed="0"/><vehicle id="R_dup" lane="ramp_accel_0" speed="0"/></timestep><timestep time="2"><vehicle id="R_a" lane=":freeway_merge_0_0" speed="0"/></timestep></fcd-export>"""


class InternalLaneAccountingTests(unittest.TestCase):
    def test_internal_and_unknown_observations_reconcile(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            base = Path(directory)
            (base / "network.net.xml").write_text(NETWORK)
            (base / "fcd.xml").write_text(FCD)
            result = analyze_fcd_accounting(base / "fcd.xml", base / "network.net.xml")
        rows = {(r["lane_id"], r["vehicle_class"]): r for r in result["per_lane_class"]}
        self.assertEqual(rows[(":urban_diverge_1_0", "R")]["stopped_vehicle_seconds"], 1.0)
        self.assertEqual(rows[(":ramp_mid_0_0", "R")]["stopped_samples"], 1)
        self.assertEqual(rows[("unknown_network_lane", "unknown_id")]["stopped_samples"], 1)
        self.assertEqual(result["accounting"]["unknown_network_lane_samples"], 1)
        self.assertEqual(result["accounting"]["unrecognized_vehicle_id_samples"], 1)
        self.assertEqual(result["accounting"]["duplicate_vehicle_time_samples"], 1)
        self.assertTrue(result["accounting"]["reconciliation"]["known_plus_unknown_equals_selected"])
        self.assertTrue(result["accounting"]["reconciliation"]["atomic_groups_are_mutually_exclusive"])
        first = result["instantaneous_by_timestep"][0]
        self.assertIn(":urban_diverge_1_0/R", first["lane_class_counts"])
        self.assertIn("ramp_path_internal_upstream/R", first["atomic_group_class_counts"])
        self.assertNotIn("ramp_path_internal_upstream/R", first["lane_class_counts"])

    def test_window_and_timestep_validation(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            base = Path(directory)
            (base / "network.net.xml").write_text(NETWORK)
            (base / "fcd.xml").write_text(FCD)
            result = analyze_fcd_accounting(base / "fcd.xml", base / "network.net.xml", time_window=(1.0, 3.0))
            self.assertEqual(result["time"]["timestep_count"], 2)
            self.assertEqual(result["time"]["sampling_step_s"], 1.0)
            self.assertEqual(result["ramp_path_scope"]["lanes"], [":ramp_mid_0_0", ":urban_diverge_1_0", "ramp_accel_0", "ramp_storage_0"])
            (base / "bad.xml").write_text("<fcd-export><timestep time=\"0\"/><timestep time=\"1\"/><timestep time=\"3\"/></fcd-export>")
            bad = analyze_fcd_accounting(base / "bad.xml", base / "network.net.xml")
            self.assertFalse(bad["time"]["uniform_sampling"])
            self.assertFalse(bad["time"]["vehicle_seconds_available"])

    def test_missing_declared_path_lane_is_explicit(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            base = Path(directory)
            (base / "network.net.xml").write_text(NETWORK.replace('<edge id=":ramp_mid_0" function="internal"><lane id=":ramp_mid_0_0"/></edge>', ""))
            (base / "fcd.xml").write_text(FCD)
            result = analyze_fcd_accounting(base / "fcd.xml", base / "network.net.xml")
        self.assertIn(":ramp_mid_0_0", result["accounting"]["declared_lanes_missing_from_network"])
        self.assertEqual(result["ramp_path_scope"]["coverage_status"], "not_verified_missing_declared_lanes")
        self.assertIn(":ramp_mid_0_0", result["ramp_path_scope"]["missing_declared_lanes"])

    def test_output_audit_checks_fcd_trip_e1_and_tls_semantics(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            outputs = root / "outputs"
            outputs.mkdir()
            (root / "network.net.xml").write_text(NETWORK)
            (outputs / "fcd.xml").write_text('<fcd-export><timestep time="0"><vehicle id="R_a"/></timestep><timestep time="1"><vehicle id="R_a"/></timestep></fcd-export>')
            (outputs / "tripinfo.xml").write_text('<tripinfos><tripinfo id="R_a"/></tripinfos>')
            (outputs / "tls_states.xml").write_text('<states><tlsState time="0"/><tlsState time="1"/></states>')
            e1 = '<detector><interval begin="0" end="30" nVehContrib="1" nVehEntered="1" speed="10"/><interval begin="30" end="60" nVehContrib="1" nVehEntered="1" speed="10"/></detector>'
            for name in ("merge_downstream_e1_l0.xml", "merge_downstream_e1_l1.xml", "merge_upstream_e1_l0.xml", "merge_upstream_e1_l1.xml"):
                (outputs / name).write_text(e1)
            result = audit_run_observation_outputs(root)
            same = compare_xml_record_semantics(outputs / "fcd.xml", outputs / "fcd.xml", "timestep")
        self.assertEqual(result["fcd"]["sampling_step_s"], 1.0)
        self.assertTrue(all(result["semantic_checks"].values()))
        self.assertTrue(same["equal"])
        self.assertEqual(same["different_record_count"], 0)

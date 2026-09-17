"""Synthetic offline tests for the Stage 4 qMain adapter."""

from __future__ import annotations

import ast
import copy
import hashlib
import itertools
import json
from pathlib import Path
import tempfile
import unittest
import xml.etree.ElementTree as ET

from src.analysis import analyze_stage4_qmain as stage4

ROOT = Path(__file__).resolve().parents[1]
BATCH = ROOT / "data/processed/stage4_qmain_sequential_20260912_v1"


def contract() -> dict:
    return {
        "batch_id": stage4.BATCH_ID,
        "status": "t42_offline_ready_t43_prohibited",
        "logical_run_ids": list(stage4.ALL_RUN_IDS),
        "controller": "none",
        "only_intervention": "q_main",
        "windows": stage4.REGISTERED_WINDOWS,
        "e1": stage4.REGISTERED_E1,
        "ejmi": stage4.REGISTERED_EJMI,
        "branch_rule": stage4.REGISTERED_BRANCH_RULE,
        "registration_payload_path": stage4.REGISTRATION_PAYLOAD_RELATIVE_PATH,
    }


def e1_bins(speed: float, occupancy: float, q: float = 3300.0) -> list[dict]:
    return [{"begin": float(begin), "end": float(begin + 30), "q_vehph": q,
             "speed_mps": speed, "occupancy_percent": occupancy, "n_contrib": 20}
            for begin in range(0, 2700, 30)]


def manifest(run_id: str, seed: int, q_main: float, speed: float = 28.0,
             occupancy: float = 8.0, r: str = "clear_passage", qualified: bool = True) -> dict:
    bins = e1_bins(speed, occupancy, q_main)
    planned = {"M": round(q_main * 1500.0 / 3600.0), "R": 300, "U": 150, "X": 75}
    value = {"run_id": run_id, "seed": seed, "q_main": q_main,
             "technical_qualified": qualified, "outside_M_1500": 0,
             "single_factor_hash_check": True,
             "planned": planned,
             "endpoints": [{"class": cls, "endpoint_s": endpoint, "coverage": True,
                             "entered": planned[cls]}
                           for endpoint in (1500.0, 2700.0) for cls in ("M", "R", "U", "X")],
             "e1": {"bins_30s": bins, "aggregates": {
                 "A": stage4.aggregate_bins(bins, 0, 1500),
                 "B": stage4.aggregate_bins(bins, 300, 1500),
             }}, "r_passage": {"status": r}}
    value["ejmi"] = {"status": "positive"}
    return value


def complete_observations() -> dict:
    audit = {key: {"passed": True} for key in stage4.REQUIRED_OBSERVATION_AUDIT_KEYS}
    return {
        "qualification": {"passed": True, "required_audit_items": len(audit),
                          "passed_audit_items": len(audit)},
        "planned_demand_vehph": {"M": 3499.2, "R": 720.0, "U": 360.0, "X": 180.0},
        "realized_entry_vehph_A": {"M": 3499.2, "R": 720.0, "U": 360.0, "X": 180.0},
        "q_definition": stage4.REGISTERED_Q_DEFINITION,
        "downstream_e1": {"bins_30s": e1_bins(20.0, 5.0),
                          "aggregates": {key: {} for key in ("A", "B", "Post", "Full")}},
        "m_stopped_episodes": [],
        "m_stopped_position_range": [],
        "m_depart_position_range": [],
        "r_propagation": {"summary": {}, "event_sets": {}},
        "shared_r_u_stopped_exposure": {},
        "tls_context": {"label_count": 2700},
        "warning_coverage_audit": audit,
    }


class Stage4E1Tests(unittest.TestCase):
    def test_two_lane_speed_is_contribution_weighted_and_occupancy_is_mean(self) -> None:
        rows = [
            {"detector_id": "l0", "begin": 0.0, "end": 30.0, "n_contrib": 1,
             "n_entered": 2, "speed_mps": 10.0, "occupancy_percent": 4.0},
            {"detector_id": "l1", "begin": 0.0, "end": 30.0, "n_contrib": 3,
             "n_entered": 4, "speed_mps": 20.0, "occupancy_percent": 8.0},
        ]
        combined = stage4.combine_two_lane_e1(rows, {"l0", "l1"}, 0, 30)
        self.assertEqual(combined[0]["speed_mps"], 17.5)
        self.assertEqual(combined[0]["occupancy_percent"], 6.0)
        self.assertEqual(combined[0]["q_vehph"], 720.0)

    def test_missing_one_lane_fails_coverage(self) -> None:
        row = {"detector_id": "l0", "begin": 0.0, "end": 30.0, "n_contrib": 1,
               "n_entered": 1, "speed_mps": 10.0, "occupancy_percent": 1.0}
        with self.assertRaisesRegex(ValueError, "coverage incomplete"):
            stage4.combine_two_lane_e1([row], {"l0", "l1"}, 0, 30)

    def test_reaggregate_preserves_coverage_and_weighting(self) -> None:
        bins = e1_bins(20.0, 5.0)[:4]
        bins[0]["speed_mps"], bins[0]["n_contrib"] = 10.0, 10
        bins[1]["speed_mps"], bins[1]["n_contrib"] = 30.0, 30
        result = stage4.reaggregate_bins(bins, 0, 120, 60)
        self.assertEqual(len(result), 2)
        self.assertEqual(result[0]["speed_mps"], 25.0)
        self.assertEqual(result[0]["occupancy_percent"], 5.0)

    def test_read_e1_rejects_duplicate_interval(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "e1.xml"
            path.write_text('<detector><interval begin="0" end="30" nVehContrib="1" nVehEntered="1" speed="10" occupancy="2"/><interval begin="0" end="30" nVehContrib="1" nVehEntered="1" speed="10" occupancy="2"/></detector>')
            with self.assertRaisesRegex(ValueError, "duplicate"):
                stage4.read_e1(path, "l0")


class Stage4EJMITests(unittest.TestCase):
    def setUp(self) -> None:
        self.lower = manifest("C17", 17, 3200, 30.0, 5.0)
        self.upper = manifest("MH17", 17, 3800, 31.0, 6.0)

    def test_positive_requires_A_B_and_persistence(self) -> None:
        candidate = manifest("QM3500S17", 17, 3500, 28.0, 8.0)
        result = stage4.evaluate_ejmi(candidate, self.lower, self.upper, contract())
        self.assertEqual(result["status"], "positive")
        self.assertTrue(result["aggregate_checks"]["A"])
        self.assertTrue(result["aggregate_checks"]["B"])
        self.assertTrue(result["persistence"]["passed"])
        self.assertTrue(any(row["pass_60_count"] == 2 and row["pass_30_count"] == 4 for row in result["persistence"]["blocks"]))

    def test_aggregate_margin_failure_is_not_identified(self) -> None:
        candidate = manifest("QM3500S17", 17, 3500, 29.7, 8.0)
        result = stage4.evaluate_ejmi(candidate, self.lower, self.upper, contract())
        self.assertEqual(result["status"], "not_identified")
        self.assertFalse(result["aggregate_checks"]["A"])

    def test_persistence_failure_is_not_identified(self) -> None:
        candidate = manifest("QM3500S17", 17, 3500, 28.0, 8.0)
        for row in candidate["e1"]["bins_30s"]:
            if row["begin"] >= 300:
                row["speed_mps"] = 31.0 if int((row["begin"] - 300) / 30) % 2 == 0 else 27.0
        # Keep registered A/B aggregates positive to isolate the persistence rule.
        result = stage4.evaluate_ejmi(candidate, self.lower, self.upper, contract())
        self.assertFalse(result["persistence"]["passed"])
        self.assertEqual(result["status"], "not_identified")

    def test_unqualified_candidate_is_unresolved(self) -> None:
        candidate = manifest("QM3500S17", 17, 3500, qualified=False)
        result = stage4.evaluate_ejmi(candidate, self.lower, self.upper, contract())
        self.assertEqual(result["status"], "unresolved")

    def test_seed_mismatch_is_rejected(self) -> None:
        candidate = manifest("QM3500S23", 23, 3500)
        with self.assertRaisesRegex(ValueError, "seed"):
            stage4.evaluate_ejmi(candidate, self.lower, self.upper, contract())


class Stage4PassageAndAccountingTests(unittest.TestCase):
    def write_fcd(self, directory: Path, lane_by_time: list[tuple[int, str]]) -> Path:
        root = ET.Element("fcd-export")
        for time, lane in lane_by_time:
            step = ET.SubElement(root, "timestep", {"time": str(time)})
            ET.SubElement(step, "vehicle", {"id": "R_flow.0", "lane": lane})
        path = directory / "fcd.xml"
        ET.ElementTree(root).write(path)
        return path

    def test_r_clear_passage_uses_bracketed_identity_event(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = self.write_fcd(Path(directory), [(0, "ramp_accel_0"), (1, "main_down_0"), (2, "main_down_0")])
            raw = stage4.read_r_passage(path, {"main_down_0", "main_down_1"}, {0.0, 1.0, 2.0})
            result = stage4.classify_r_passage(raw, {"R_flow.0": {"class": "R", "arrival": 2.0}})
            self.assertEqual(result["status"], "clear_passage")
            self.assertEqual(result["a_bracketed_event_count"], 1)

    def test_r_clear_exclusion_requires_complete_coverage(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = self.write_fcd(Path(directory), [(0, "ramp_accel_0"), (1, "ramp_accel_0")])
            raw = stage4.read_r_passage(path, {"main_down_0"}, {0.0, 1.0})
            result = stage4.classify_r_passage(raw, {"R_flow.0": {"class": "R", "arrival": 1700.0}})
            self.assertEqual(result["status"], "clear_exclusion")

    def test_missing_frame_makes_exclusion_unresolved(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = self.write_fcd(Path(directory), [(0, "ramp_accel_0")])
            raw = stage4.read_r_passage(path, {"main_down_0"}, {0.0, 1.0})
            result = stage4.classify_r_passage(raw, {"R_flow.0": {"class": "R", "arrival": 1700.0}})
            self.assertEqual(result["status"], "unresolved")

    def test_arrival_without_passage_is_measurement_contradiction(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = self.write_fcd(Path(directory), [(0, "ramp_accel_0"), (1, "ramp_accel_0")])
            raw = stage4.read_r_passage(path, {"main_down_0"}, {0.0, 1.0})
            result = stage4.classify_r_passage(raw, {"R_flow.0": {"class": "R", "arrival": 1.0}})
            self.assertEqual(result["status"], "unresolved")
            self.assertEqual(result["arrival_without_passage_ids"], ["R_flow.0"])

    def test_unbracketed_first_downstream_observation_is_unresolved(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = self.write_fcd(Path(directory), [(0, "main_down_0"), (1, "main_down_0")])
            raw = stage4.read_r_passage(path, {"main_down_0"}, {0.0, 1.0})
            result = stage4.classify_r_passage(raw, {"R_flow.0": {"class": "R", "arrival": 1700.0}})
            self.assertEqual(result["status"], "unresolved")
            self.assertEqual(result["a_unbracketed_event_count"], 1)

    def test_unknown_lane_breaks_spatial_coverage(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = self.write_fcd(Path(directory), [(0, "unknown_lane"), (1, "ramp_accel_0")])
            raw = stage4.read_r_passage(path, {"main_down_0"}, {0.0, 1.0}, {"main_down_0", "ramp_accel_0"})
            self.assertFalse(raw["coverage_complete"])
            self.assertEqual(raw["unknown_lanes"], 1)

    def test_duplicate_identity_in_one_frame_breaks_coverage(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = ET.Element("fcd-export")
            step = ET.SubElement(root, "timestep", {"time": "0"})
            ET.SubElement(step, "vehicle", {"id": "R_flow.0", "lane": "ramp_accel_0"})
            ET.SubElement(step, "vehicle", {"id": "R_flow.0", "lane": "main_down_0"})
            path = Path(directory) / "fcd.xml"
            ET.ElementTree(root).write(path)
            raw = stage4.read_r_passage(path, {"main_down_0"}, {0.0})
            self.assertEqual(raw["duplicate_vehicle_identities"], 1)
            self.assertFalse(raw["coverage_complete"])
            self.assertEqual(stage4.classify_r_passage(raw, {})["status"], "unresolved")

    def test_endpoint_accounting_retains_denominators(self) -> None:
        plan = {"M": 1, "R": 1, "U": 1, "X": 1}
        trips = {f"{cls}_flow.0": {"class": cls, "depart": 0.0, "arrival": 10.0} for cls in plan}
        boundaries = {1500.0: {"loaded": 4, "inserted": 4, "arrived": 4},
                      2700.0: {"loaded": 4, "inserted": 4, "arrived": 4}}
        rows = stage4.build_endpoints(plan, trips, set(trips), boundaries)
        self.assertEqual(len(rows), 8)
        self.assertTrue(all(row["coverage"] for row in rows))
        self.assertTrue(all(row["planned"] == row["entered"] + row["outside"] for row in rows))


class Stage4CompleteObservationTests(unittest.TestCase):
    class FakeResolver:
        def __init__(self, paths: dict[str, Path]):
            self.paths = paths

        def resolve(self, suffix: str) -> Path:
            return self.paths[suffix]

        def inventory_hashes(self) -> dict[str, str]:
            return {suffix: "fixture" for suffix in stage4.EXPECTED_RUNTIME_SUFFIXES}

    def test_complete_candidate_observation_fixture(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            fcd_root = ET.Element("fcd-export")
            tls_root = ET.Element("tlsStates")
            for time_s in range(2700):
                step = ET.SubElement(fcd_root, "timestep", {"time": str(time_s)})
                if time_s in (0, 1):
                    ET.SubElement(step, "vehicle", {"id": "M_flow.0", "lane": "main_up_0",
                                                     "speed": "0", "pos": str(1390 + time_s)})
                    ET.SubElement(step, "vehicle", {"id": "R_flow.0", "lane": "shared_approach_0",
                                                     "speed": "0", "pos": "20"})
                    ET.SubElement(step, "vehicle", {"id": "U_flow.0", "lane": "shared_approach_0",
                                                     "speed": "0", "pos": "30"})
                ET.SubElement(tls_root, "tlsState", {"time": str(time_s), "id": "urban_tls",
                                                     "programID": "technical_placeholder", "phase": "0", "state": "Gr"})
            fcd_path, tls_path = root / "fcd.xml", root / "tls.xml"
            ET.ElementTree(fcd_root).write(fcd_path)
            ET.ElementTree(tls_root).write(tls_path)
            paths = {"outputs/fcd.xml": fcd_path, "outputs/tls_states.xml": tls_path}
            for detector_id in ("merge_downstream_e1_l0", "merge_downstream_e1_l1"):
                detector_root = ET.Element("detector")
                for begin in range(0, 2700, 30):
                    ET.SubElement(detector_root, "interval", {"begin": str(begin), "end": str(begin + 30),
                                  "nVehContrib": "1", "nVehEntered": "1", "speed": "20", "occupancy": "5"})
                path = root / f"{detector_id}.xml"
                ET.ElementTree(detector_root).write(path)
                paths[f"outputs/{detector_id}.xml"] = path
            contract_value = json.loads((BATCH / "measurement_contract.json").read_text())
            trips = {"M_flow.0": {"class": "M", "depart": 0.0, "arrival": 10.0,
                                   "depart_lane": "main_up_0", "depart_pos_m": 1390.0}}
            endpoints = [
                {"class": cls, "endpoint_s": endpoint, "entered": 1 if endpoint == 1500 else 1,
                 "coverage": True}
                for endpoint in (1500.0, 2700.0) for cls in ("M", "R", "U", "X")
            ]
            observed = stage4.build_required_observations(
                "QM3500S17", self.FakeResolver(paths), contract_value, trips,
                {"M": 1, "R": 1, "U": 1, "X": 1}, endpoints, {"warnings_zero": True})
            self.assertTrue(observed["qualification"]["passed"])
            self.assertEqual(observed["downstream_e1"]["aggregates"]["Full"]["q_vehph"], 240.0)
            self.assertEqual(observed["m_stopped_episodes"][0]["sample_count"], 2)
            self.assertTrue(any(row["observation_domain"] == "A" and row["parent_episode_id"]
                                for row in observed["m_stopped_episodes"]))
            self.assertEqual(observed["m_stopped_position_range"][0]["stopped_sample_count"], 2)
            self.assertAlmostEqual(observed["m_stopped_position_range"][0]["min_distance_to_lane_end_m"], 3.87)
            self.assertAlmostEqual(observed["m_stopped_position_range"][0]["max_distance_to_lane_end_m"], 4.87)
            self.assertEqual(observed["m_depart_position_range"][0]["vehicle_count"], 1)
            self.assertEqual(observed["shared_r_u_stopped_exposure"]["cooccurrence_support_s"], 2)
            self.assertEqual(observed["tls_context"]["label_count"], 2700)
            self.assertIn("summary", observed["r_propagation"])
            self.assertEqual(observed["warning_coverage_audit"]["fcd"]["frame_count"], 2700)
            self.assertIn("nVehEntered", observed["q_definition"]["warning"])
            self.assertEqual(observed["planned_demand_vehph"],
                             {"M": 2.4, "R": 2.4, "U": 2.4, "X": 2.4})
            self.assertEqual(observed["realized_entry_vehph_A"],
                             {"M": 2.4, "R": 2.4, "U": 2.4, "X": 2.4})
            self.assertNotIn("actual_input_vehph", observed)

    def test_candidate_manifest_requires_every_complete_observation_section(self) -> None:
        value = manifest("QM3500S17", 17, 3500)
        value["required_observations_contract_sha256"] = stage4.REGISTERED_OBSERVATIONS_SHA256
        value["required_observations"] = complete_observations()
        registered = {"run_id": "QM3500S17", "seed": 17, "q_main": 3500}
        stage4._validate_manifest(value, registered, False, True)
        for key in stage4.REQUIRED_CANDIDATE_OBSERVATION_KEYS:
            with self.subTest(key=key):
                changed = copy.deepcopy(value)
                del changed["required_observations"][key]
                with self.assertRaisesRegex(ValueError, "complete observations|qualification|audit"):
                    stage4._validate_manifest(changed, registered, False, True)

    def test_candidate_manifest_rejects_failed_observation_audit(self) -> None:
        value = manifest("QM3500S17", 17, 3500)
        value["required_observations_contract_sha256"] = stage4.REGISTERED_OBSERVATIONS_SHA256
        value["required_observations"] = complete_observations()
        value["required_observations"]["warning_coverage_audit"]["fcd"]["passed"] = False
        with self.assertRaisesRegex(ValueError, "audit failed"):
            stage4._validate_manifest(
                value, {"run_id": "QM3500S17", "seed": 17, "q_main": 3500}, False, True)

    def test_registered_reference_entry_rates_use_A_endpoint_counts(self) -> None:
        registry = json.loads((BATCH / "source_registry.json").read_text())
        expected_r = {"C17": 360.0, "C23": 369.6, "MH17": 288.0, "MH23": 285.6}
        expected_m = {"C17": 3199.2, "C23": 3199.2, "MH17": 3799.2, "MH23": 3799.2}
        for registered in registry["runs"][:4]:
            with self.subTest(run_id=registered["run_id"]):
                reference = json.loads((ROOT / registered["reference_manifest_path"]).read_text())
                planned, realized = stage4.build_demand_rate_fields(
                    reference["planned"], reference["endpoints"], 1500.0, [0.0, 1500.0])
                self.assertEqual(planned["R"], 720.0)
                self.assertEqual(realized["R"], expected_r[registered["run_id"]])
                self.assertEqual(realized["M"], expected_m[registered["run_id"]])

    def test_deprecated_ambiguous_input_rate_field_is_rejected(self) -> None:
        value = manifest("QM3500S17", 17, 3500)
        value["required_observations_contract_sha256"] = stage4.REGISTERED_OBSERVATIONS_SHA256
        value["required_observations"] = complete_observations()
        value["required_observations"]["actual_input_vehph"] = value["required_observations"].pop(
            "planned_demand_vehph")
        with self.assertRaisesRegex(ValueError, "deprecated ambiguous"):
            stage4._validate_manifest(
                value, {"run_id": "QM3500S17", "seed": 17, "q_main": 3500}, False, True)

    def test_candidate_entry_rate_must_match_covered_A_endpoint(self) -> None:
        value = manifest("QM3500S17", 17, 3500)
        value["required_observations_contract_sha256"] = stage4.REGISTERED_OBSERVATIONS_SHA256
        value["required_observations"] = complete_observations()
        value["required_observations"]["realized_entry_vehph_A"]["R"] = 360.0
        with self.assertRaisesRegex(ValueError, "differ from plan or A-endpoint"):
            stage4._validate_manifest(
                value, {"run_id": "QM3500S17", "seed": 17, "q_main": 3500}, False, True)


class Stage4SequentialTests(unittest.TestCase):
    @staticmethod
    def ledger() -> dict:
        return {"logical_runs": [
            {"run_id": run_id,
             "seed": 17 if run_id.endswith("17") else 23,
             "q_main": 3200 if run_id.startswith("C") else 3800 if run_id.startswith("MH")
             else 3500 if "3500" in run_id else 3350 if "3350" in run_id else 3650}
            for run_id in stage4.ALL_RUN_IDS]}

    def tier(self, r: str, e: str, qualified: bool = True) -> list[dict]:
        result = []
        for run_id, seed in zip(stage4.TIER1_IDS, (17, 23)):
            row = manifest(run_id, seed, 3500, r=r, qualified=qualified)
            row["ejmi"] = {"status": e}
            result.append(row)
        return result

    def first_tier_with_references(self, tier: list[dict]) -> list[dict]:
        references = [manifest("C17", 17, 3200), manifest("C23", 23, 3200),
                      manifest("MH17", 17, 3800), manifest("MH23", 23, 3800)]
        return references + tier

    def test_passage_without_ejmi_selects_q3650(self) -> None:
        result = stage4.decide_tier1(self.tier("clear_passage", "not_identified"))
        self.assertEqual(result["action"], "run_q3650")
        self.assertEqual(set(result["selected_tier2_runs"]), set(stage4.UPPER_IDS))

    def test_exclusion_without_ejmi_selects_q3350(self) -> None:
        result = stage4.decide_tier1(self.tier("clear_exclusion", "not_identified"))
        self.assertEqual(result["action"], "run_q3350")
        self.assertEqual(set(result["cancelled_by_stop_rule"]), set(stage4.UPPER_IDS))

    def test_passage_with_ejmi_stops_supports_A(self) -> None:
        result = stage4.decide_tier1(self.tier("clear_passage", "positive"))
        self.assertEqual(result["action"], "stop_supports_A")
        self.assertEqual(len(result["cancelled_by_stop_rule"]), 4)

    def test_seed_disagreement_stops_unresolved(self) -> None:
        rows = self.tier("clear_passage", "not_identified")
        rows[1]["r_passage"]["status"] = "clear_exclusion"
        result = stage4.decide_tier1(rows)
        self.assertEqual(result["action"], "stop_unresolved")

    def test_tier1_manifest_qmain_drift_is_rejected_before_decision(self) -> None:
        rows = self.tier("clear_passage", "positive")
        rows[0]["q_main"] = 3499
        with self.assertRaisesRegex(ValueError, "qMain differs"):
            stage4.decide_tier1(rows)

    def test_cancelled_branch_manifest_is_rejected(self) -> None:
        tier = self.tier("clear_passage", "positive")
        decision = stage4.decide_tier1(tier)
        rows = self.first_tier_with_references(tier)
        rows.append(manifest("QM3350S17", 17, 3350))
        with self.assertRaisesRegex(ValueError, "cancelled"):
            stage4.build_logical_statuses(self.ledger(), rows, decision)

    def test_registered_reference_map_is_same_seed_for_all_candidates(self) -> None:
        value = json.loads((BATCH / "measurement_contract.json").read_text())
        registry = {row["run_id"]: row for row in json.loads((BATCH / "source_registry.json").read_text())["runs"]}
        for run_id in stage4.TIER1_IDS + stage4.LOWER_IDS + stage4.UPPER_IDS:
            with self.subTest(run_id=run_id):
                mapping = value["ejmi_reference_map"][run_id]
                seed = registry[run_id]["seed"]
                self.assertEqual(mapping["candidate_seed"], seed)
                self.assertEqual(mapping["lower"]["run_id"], f"C{seed}")
                self.assertEqual(mapping["upper"]["run_id"], f"MH{seed}")
                lower, upper = stage4.load_registered_ejmi_references(
                    registry[run_id], value, ROOT / mapping["lower"]["manifest_path"],
                    ROOT / mapping["upper"]["manifest_path"])
                self.assertEqual({lower["seed"], upper["seed"]}, {seed})

    def test_registered_reference_path_substitution_is_rejected(self) -> None:
        value = json.loads((BATCH / "measurement_contract.json").read_text())
        registry = {row["run_id"]: row for row in json.loads((BATCH / "source_registry.json").read_text())["runs"]}
        mapping = value["ejmi_reference_map"]["QM3500S17"]
        with self.assertRaisesRegex(ValueError, "path differs"):
            stage4.load_registered_ejmi_references(
                registry["QM3500S17"], value, ROOT / mapping["upper"]["manifest_path"],
                ROOT / mapping["upper"]["manifest_path"])

    def test_decide_final_exhaustive_one_point_matrix(self) -> None:
        states = list(itertools.product(("clear_passage", "clear_exclusion", "unresolved"),
                                        ("positive", "not_identified", "unresolved")))
        for first, second in itertools.product(states, repeat=2):
            rows = [manifest("QM3500S17", 17, 3500, r=first[0]),
                    manifest("QM3500S23", 23, 3500, r=second[0])]
            rows[0]["ejmi"]["status"], rows[1]["ejmi"]["status"] = first[1], second[1]
            expected = ("supports_A_within_registered_points"
                        if first == second == ("clear_passage", "positive") else "unresolved")
            self.assertEqual(stage4.decide_final(rows)["action"], expected)

    def test_decide_final_two_point_matrix_and_counterexamples(self) -> None:
        consolidated = list(itertools.product(("clear_passage", "clear_exclusion", "unresolved"),
                                               ("positive", "not_identified", "unresolved")))
        for low, high in itertools.product(consolidated, repeat=2):
            rows = []
            for q_main, state in ((3500, low), (3650, high)):
                for seed in (17, 23):
                    row = manifest(f"QM{q_main}S{seed}", seed, q_main, r=state[0])
                    row["ejmi"]["status"] = state[1]
                    rows.append(row)
            contradiction = any(state == ("clear_exclusion", "positive") for state in (low, high))
            all_registered_states = all(r != "unresolved" and e != "unresolved" for r, e in (low, high))
            if all_registered_states and not contradiction and ("clear_passage", "positive") in (low, high):
                expected = "supports_A_within_registered_points"
            elif low == ("clear_passage", "not_identified") and high == ("clear_exclusion", "not_identified"):
                expected = "supports_B_pattern_within_registered_points"
            else:
                expected = "unresolved"
            self.assertEqual(stage4.decide_final(rows)["action"], expected)
        unqualified = [manifest("QM3500S17", 17, 3500), manifest("QM3500S23", 23, 3500, qualified=False)]
        self.assertEqual(stage4.decide_final(unqualified)["action"], "unresolved")

    def test_status_denominators_include_cancelled_registration_universe(self) -> None:
        ledger = self.ledger()
        tier = self.tier("clear_passage", "positive")
        manifests = self.first_tier_with_references(tier)
        summary = stage4.build_logical_statuses(ledger, manifests, stage4.decide_tier1(tier))
        self.assertTrue(summary["all_registered_terminal"])
        self.assertEqual(summary["denominators"]["registered_logical_runs"], 10)
        self.assertEqual(summary["denominators"]["used_valid_run_manifests"], 6)
        self.assertEqual(summary["denominators"]["class_endpoint_units_expected"], 48)
        self.assertEqual(summary["denominators"]["adjacent_matched_seed_comparisons_expected"], 4)

    def test_selected_branch_remains_nonterminal_until_manifests_exist(self) -> None:
        ledger = self.ledger()
        tier = self.tier("clear_passage", "not_identified")
        manifests = self.first_tier_with_references(tier)
        summary = stage4.build_logical_statuses(ledger, manifests, stage4.decide_tier1(tier))
        self.assertFalse(summary["all_registered_terminal"])
        states = {row["run_id"]: row["state"] for row in summary["logical_statuses"]}
        self.assertEqual(states["QM3650S17"], "selected_pending_execution")
        self.assertEqual(states["QM3350S17"], "cancelled_by_stop_rule")

    def test_mixed_tier2_seed_selection_is_rejected(self) -> None:
        decision = {"action": "run_q3350", "result_status": "tier2_lower_selected",
                    "selected_tier2_runs": ["QM3350S17", "QM3650S23"],
                    "cancelled_by_stop_rule": ["QM3350S23", "QM3650S17"]}
        with self.assertRaisesRegex(ValueError, "same-q seed pair"):
            stage4.build_logical_statuses(self.ledger(), self.first_tier_with_references(self.tier(
                "clear_exclusion", "not_identified")), decision)

    def test_missing_reference_manifest_remains_nonterminal(self) -> None:
        tier = self.tier("clear_passage", "positive")
        summary = stage4.build_logical_statuses(self.ledger(), tier, stage4.decide_tier1(tier))
        row = next(item for item in summary["logical_statuses"] if item["run_id"] == "C17")
        self.assertEqual(row["state"], "reference_manifest_missing")
        self.assertFalse(row["terminal"])

    def test_manifest_identity_and_unique_covered_endpoints_are_required(self) -> None:
        tier = self.tier("clear_passage", "positive")
        rows = self.first_tier_with_references(tier)
        rows[0]["seed"] = 23
        rows[0]["endpoints"] = [{"class": "M", "endpoint_s": 1500.0, "coverage": True}] * 8
        with self.assertRaises(ValueError):
            stage4.build_logical_statuses(self.ledger(), rows, stage4.decide_tier1(tier))

    def test_registered_manifest_payload_hash_is_enforced(self) -> None:
        tier = self.tier("clear_passage", "positive")
        rows = self.first_tier_with_references(tier)
        ledger = self.ledger()
        ledger["manifest_hash_required"] = True
        for registered, observed in zip(ledger["logical_runs"], rows):
            registered["manifest_payload_sha256"] = stage4._manifest_payload_hash(observed)
        rows[0]["seed"] = 23
        with self.assertRaisesRegex(ValueError, "seed differs|payload hash"):
            stage4.build_logical_statuses(ledger, rows, stage4.decide_tier1(tier))


class Stage4SafetyTests(unittest.TestCase):
    def test_contract_rejects_controller_or_window_change(self) -> None:
        value = contract()
        value["controller"] = "ALINEA"
        with self.assertRaisesRegex(ValueError, "uncontrolled"):
            stage4.validate_contract(value)

    def test_contract_rejects_exact_arithmetic_and_margin_drift(self) -> None:
        for field in ("period_s", "occupancy_rule", "speed_rule", "q_rule"):
            with self.subTest(field=field):
                value = contract()
                value["e1"] = dict(value["e1"])
                value["e1"][field] = "changed" if field != "period_s" else 60.0
                with self.assertRaises(ValueError):
                    stage4.validate_contract(value)
        value = contract()
        value["ejmi"] = json.loads(json.dumps(value["ejmi"]))
        value["ejmi"]["margins"]["A"]["delta_v_mps"] += 0.001
        with self.assertRaises(ValueError):
            stage4.validate_contract(value)

    def test_registration_payload_rejects_scientific_drift(self) -> None:
        payload = json.loads((BATCH / "registration_payload.json").read_text())
        stage4.validate_registration_payload(payload)
        payload["q_main_points"][2] = 3499
        with self.assertRaisesRegex(ValueError, "payload changed"):
            stage4.validate_registration_payload(payload)

    def test_final_matrix_and_netconvert_budget_are_frozen(self) -> None:
        payload = json.loads((BATCH / "registration_payload.json").read_text())
        self.assertEqual(payload["budget"]["regular_netconvert_operations_min"], 2)
        self.assertEqual(payload["budget"]["regular_netconvert_operations_max"], 4)
        payload["final_decision_rule"]["additional_points_or_seeds_prohibited"] = False
        with self.assertRaisesRegex(ValueError, "payload changed"):
            stage4.validate_registration_payload(payload)

    def test_current_context_validates_authorized_completed_tier2_execution(self) -> None:
        ledger, _, _ = stage4.validate_context(
            BATCH / "execution_ledger.json", BATCH / "measurement_contract.json", BATCH / "source_registry.json"
        )
        self.assertEqual(ledger["t43_launch_authorization"]["status"], "user_approved")
        self.assertEqual(
            [ledger[field] for field in (
                "actual_sumo_starts", "actual_netconvert_operations",
                "actual_traci_connections", "actual_gui_starts",
            )],
            [4, 4, 0, 0],
        )

    def test_prohibited_t43_rejects_each_nonzero_execution_counter(self) -> None:
        for field in ("actual_sumo_starts", "actual_netconvert_operations",
                      "actual_traci_connections", "actual_gui_starts"):
            with self.subTest(field=field), tempfile.TemporaryDirectory() as directory:
                ledger = json.loads((BATCH / "execution_ledger.json").read_text())
                ledger["t43_launch_authorization"] = {
                    "status": "prohibited", "quote": None
                }
                for counter in (
                    "actual_sumo_starts", "actual_netconvert_operations",
                    "actual_traci_connections", "actual_gui_starts",
                ):
                    ledger[counter] = 0
                ledger[field] = 1
                path = Path(directory) / "ledger.json"
                path.write_text(json.dumps(ledger))
                with self.assertRaisesRegex(ValueError, "cannot contain starts"):
                    stage4.validate_context(
                        path, BATCH / "measurement_contract.json", BATCH / "source_registry.json")

    def test_t43_user_approved_requires_exact_quote_and_hashes(self) -> None:
        ledger = json.loads((BATCH / "execution_ledger.json").read_text())
        ledger["t43_launch_authorization"] = {"status": "user_approved", "quote": ""}
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "ledger.json"
            path.write_text(json.dumps(ledger))
            with self.assertRaisesRegex(ValueError, "exact nonpending"):
                stage4.validate_context(path, BATCH / "measurement_contract.json", BATCH / "source_registry.json")

    def test_scenario_add_source_and_runtime_semantics_reject_drift(self) -> None:
        contract_value = json.loads((BATCH / "measurement_contract.json").read_text())
        observations = contract_value["required_observations"]
        source = ROOT / observations["scenario_add_semantics"]["source_path"]
        stage4.validate_additional_semantics(source, observations, runtime=False)
        with tempfile.TemporaryDirectory() as directory:
            changed = ET.parse(source)
            changed.getroot().find("./inductionLoop[@id='merge_downstream_e1_l0']").set("period", "60")
            path = Path(directory) / "scenario.add.xml"
            changed.write(path)
            with self.assertRaisesRegex(ValueError, "E1 semantics"):
                stage4.validate_additional_semantics(path, observations, runtime=False)

    def test_compiled_topology_and_tls_semantics_reject_drift(self) -> None:
        contract_value = json.loads((BATCH / "measurement_contract.json").read_text())
        observations = contract_value["required_observations"]
        source_map = ROOT / json.loads((BATCH / "source_registry.json").read_text())["runs"][0]["source_map_path"]
        network = stage4._mapped_archive_file(source_map, "network.net.xml")
        stage4.validate_compiled_topology(network, observations)
        with tempfile.TemporaryDirectory() as directory:
            changed = ET.parse(network)
            changed.getroot().find("./edge/lane").set("length", "999")
            path = Path(directory) / "network.net.xml"
            changed.write(path)
            with self.assertRaisesRegex(ValueError, "lane semantics"):
                stage4.validate_compiled_topology(path, observations)

    def test_source_code_and_binary_hash_drift_is_rejected(self) -> None:
        original_contract = json.loads((BATCH / "measurement_contract.json").read_text())
        original_ledger = json.loads((BATCH / "execution_ledger.json").read_text())
        for section, key in (("source_code_hashes", "analyze_stage3_baseline.py"),
                             ("binary_hashes", "sumo")):
            with self.subTest(section=section, key=key), tempfile.TemporaryDirectory() as directory:
                changed = copy.deepcopy(original_contract)
                changed[section][key] = "0" * 64
                contract_path = Path(directory) / "contract.json"
                contract_path.write_text(json.dumps(changed))
                ledger = copy.deepcopy(original_ledger)
                changed_contract_hash = hashlib.sha256(contract_path.read_bytes()).hexdigest()
                ledger["input_hashes"]["contract_sha256"] = changed_contract_hash
                ledger["t43_launch_authorization"][
                    "approved_contract_sha256"
                ] = changed_contract_hash
                ledger_path = Path(directory) / "ledger.json"
                ledger_path.write_text(json.dumps(ledger))
                with self.assertRaisesRegex(ValueError, "hash mismatch"):
                    stage4.validate_context(ledger_path, contract_path, BATCH / "source_registry.json")

    def test_archive_resolver_rejects_missing_required_outputs(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            archive = root / "archive"
            archive.mkdir()
            source_map = root / "map.json"
            source_map.write_text(json.dumps({"archive_status": "complete", "source_runtime_path": "/private/tmp/source",
                                              "archive_runtime_relative_path": "archive", "file_map": []}))
            with self.assertRaisesRegex(ValueError, "lacks required"):
                stage4.ArchiveResolver(source_map, root)

    def test_temporary_and_existing_outputs_are_rejected(self) -> None:
        with self.assertRaisesRegex(ValueError, "temporary"):
            stage4.reserve_directory(Path("/private/tmp/stage4_should_not_exist"))
        with self.assertRaises(FileExistsError):
            stage4.reserve_directory(stage4.ROOT)

    def test_production_module_has_no_simulation_or_network_import(self) -> None:
        path = Path(stage4.__file__)
        tree = ast.parse(path.read_text())
        imported = set()
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                imported.update(alias.name.split(".")[0] for alias in node.names)
            elif isinstance(node, ast.ImportFrom) and node.module:
                imported.add(node.module.split(".")[0])
        self.assertTrue(imported.isdisjoint({"subprocess", "traci", "libsumo", "sumolib", "socket", "requests"}))
        imported_modules = {node.module for node in ast.walk(tree) if isinstance(node, ast.ImportFrom)}
        self.assertNotIn("src.scenarios.run_minimal_uncontrolled", imported_modules)
        calls = [node for node in ast.walk(tree) if isinstance(node, ast.Call)]
        self.assertFalse(any(isinstance(node.func, ast.Attribute) and node.func.attr in {"Popen", "connect"}
                             for node in calls))

    def test_current_runtime_overlay_resolves_both_completed_tier1_runs(self) -> None:
        ledger, _, registry = stage4.validate_context(
            BATCH / "execution_ledger.json",
            BATCH / "measurement_contract.json",
            BATCH / "source_registry.json",
        )
        for run_id in stage4.TIER1_IDS:
            with self.subTest(run_id=run_id):
                row, source_map = stage4.validate_runtime_source_registry(
                    BATCH / "runtime_source_registry.json", ledger, registry, run_id
                )
                self.assertEqual(row["run_id"], run_id)
                self.assertEqual(row["archive_file_count"], 29)
                self.assertTrue(source_map.is_file())

    def test_runtime_overlay_hash_and_path_must_match_final_ledger(self) -> None:
        ledger = json.loads((BATCH / "execution_ledger.json").read_text())
        registry = json.loads((BATCH / "source_registry.json").read_text())
        changed = copy.deepcopy(ledger)
        changed["runtime_source_registry_overlay"]["sha256"] = "0" * 64
        with self.assertRaisesRegex(ValueError, "hash differs"):
            stage4.validate_runtime_source_registry(
                BATCH / "runtime_source_registry.json", changed, registry, "QM3500S17"
            )
        changed = copy.deepcopy(ledger)
        changed["runtime_source_registry_overlay"]["path"] = (
            "data/processed/stage4_qmain_sequential_20260912_v1/source_registry.json"
        )
        with self.assertRaisesRegex(ValueError, "path differs"):
            stage4.validate_runtime_source_registry(
                BATCH / "runtime_source_registry.json", changed, registry, "QM3500S17"
            )

    def test_runtime_overlay_rejects_duplicate_and_unexecuted_entries(self) -> None:
        ledger = json.loads((BATCH / "execution_ledger.json").read_text())
        registry = json.loads((BATCH / "source_registry.json").read_text())
        original = json.loads((BATCH / "runtime_source_registry.json").read_text())
        for mutation, message in (("duplicate", "duplicated"),
                                  ("unexecuted", "completed authorized attempt")):
            with self.subTest(mutation=mutation), tempfile.TemporaryDirectory(
                dir=ROOT / "tests"
            ) as directory:
                value = copy.deepcopy(original)
                if mutation == "duplicate":
                    value["runs"].append(copy.deepcopy(value["runs"][0]))
                else:
                    # Reconstruct the valid pre-Tier-2 overlay before appending a
                    # fabricated upper-run entry.  This isolates the intended
                    # completed-attempt check from the duplicate-identity check.
                    value["runs"] = [
                        row for row in value["runs"] if row["run_id"] in stage4.TIER1_IDS
                    ]
                    value["runs"].append({
                        "run_id": "QM3650S17",
                        "attempt_id": "fabricated_attempt",
                    })
                overlay_path = Path(directory) / "overlay.json"
                overlay_path.write_text(json.dumps(value))
                changed = copy.deepcopy(ledger)
                changed["runtime_source_registry_overlay"] = {
                    "path": overlay_path.relative_to(ROOT).as_posix(),
                    "sha256": hashlib.sha256(overlay_path.read_bytes()).hexdigest(),
                }
                with self.assertRaisesRegex(ValueError, message):
                    stage4.validate_runtime_source_registry(
                        overlay_path, changed, registry, "QM3500S17"
                    )

    def test_runtime_overlay_rejects_attempt_source_map_and_receipt_drift(self) -> None:
        ledger = json.loads((BATCH / "execution_ledger.json").read_text())
        registry = json.loads((BATCH / "source_registry.json").read_text())
        cases = (
            ("attempt", "completed authorized attempt"),
            ("source_map", "facts differ"),
            ("receipt", "facts differ"),
        )
        for mutation, message in cases:
            with self.subTest(mutation=mutation):
                changed_ledger = copy.deepcopy(ledger)
                if mutation == "attempt":
                    changed_ledger["attempts"][0]["status"] = "reserved_prelaunch"
                elif mutation == "source_map":
                    changed_ledger["attempts"][0]["source_map_sha256"] = "0" * 64
                else:
                    changed_ledger["attempts"][0]["engineering_verification_sha256"] = "0" * 64
                with self.assertRaisesRegex(ValueError, message):
                    stage4.validate_runtime_source_registry(
                        BATCH / "runtime_source_registry.json",
                        changed_ledger,
                        registry,
                        "QM3500S17",
                    )

    def test_runtime_overlay_rejects_reference_and_prelaunch_fixture_lacks_tier2(self) -> None:
        ledger = json.loads((BATCH / "execution_ledger.json").read_text())
        registry = json.loads((BATCH / "source_registry.json").read_text())
        with self.assertRaisesRegex(ValueError, "cannot override"):
            stage4.validate_runtime_source_registry(
                BATCH / "runtime_source_registry.json", ledger, registry, "C17"
            )
        with tempfile.TemporaryDirectory(dir=ROOT / "tests") as directory:
            value = json.loads((BATCH / "runtime_source_registry.json").read_text())
            value["runs"] = [row for row in value["runs"] if row["run_id"] in stage4.TIER1_IDS]
            overlay_path = Path(directory) / "prelaunch_overlay.json"
            overlay_path.write_text(json.dumps(value))
            changed = copy.deepcopy(ledger)
            changed["runtime_source_registry_overlay"] = {
                "path": overlay_path.relative_to(ROOT).as_posix(),
                "sha256": hashlib.sha256(overlay_path.read_bytes()).hexdigest(),
            }
            changed["attempts"] = [
                row for row in changed["attempts"] if row["run_id"] in stage4.TIER1_IDS
            ]
            for row in changed["logical_runs"]:
                if row["run_id"] in stage4.UPPER_IDS:
                    row.update({"state": "selected_pending_execution", "terminal": False,
                                "actual_sumo_starts": 0, "attempt_ids": []})
                    row.pop("technical_qualified", None)
                    row.pop("source_map_path", None)
                    row.pop("source_map_sha256", None)
            with self.assertRaisesRegex(ValueError, "absent"):
                stage4.validate_runtime_source_registry(
                    overlay_path, changed, registry, "QM3650S17"
                )

    def test_candidate_without_explicit_runtime_overlay_creates_no_output(self) -> None:
        mapping = json.loads((BATCH / "measurement_contract.json").read_text())[
            "ejmi_reference_map"
        ]["QM3500S17"]
        with tempfile.TemporaryDirectory(dir=ROOT / "tests") as directory:
            output = Path(directory) / "output"
            argv = [
                "analyze-run",
                "--ledger", str(BATCH / "execution_ledger.json"),
                "--contract", str(BATCH / "measurement_contract.json"),
                "--registry", str(BATCH / "source_registry.json"),
                "--run-id", "QM3500S17",
                "--lower-manifest", str(ROOT / mapping["lower"]["manifest_path"]),
                "--upper-manifest", str(ROOT / mapping["upper"]["manifest_path"]),
                "--output-dir", str(output),
            ]
            with self.assertRaisesRegex(ValueError, "explicit ledger-bound"):
                stage4.main(argv)
            self.assertFalse(output.exists())

    def test_reference_rejects_runtime_overlay_before_output_reservation(self) -> None:
        with tempfile.TemporaryDirectory(dir=ROOT / "tests") as directory:
            output = Path(directory) / "output"
            argv = [
                "analyze-run",
                "--ledger", str(BATCH / "execution_ledger.json"),
                "--contract", str(BATCH / "measurement_contract.json"),
                "--registry", str(BATCH / "source_registry.json"),
                "--runtime-registry", str(BATCH / "runtime_source_registry.json"),
                "--run-id", "C17",
                "--output-dir", str(output),
            ]
            with self.assertRaisesRegex(ValueError, "reference analysis cannot"):
                stage4.main(argv)
            self.assertFalse(output.exists())

    def test_analyze_run_help_exposes_explicit_runtime_registry(self) -> None:
        help_text = stage4.build_parser()._subparsers._group_actions[0].choices[
            "analyze-run"
        ].format_help()
        self.assertIn("--runtime-registry", help_text)
        self.assertIn("ledger-bound", help_text)

    def test_current_candidate_manifest_receipts_validate_both_tier1_runs(self) -> None:
        ledger, _, _ = stage4.validate_context(
            BATCH / "execution_ledger.json",
            BATCH / "measurement_contract.json",
            BATCH / "source_registry.json",
        )
        paths = [
            BATCH
            / "verification/engineering_overlay_cli_revision_02"
            / run_id
            / "run_manifest.json"
            for run_id in stage4.TIER1_IDS
        ]
        registered, manifests = stage4.validate_candidate_manifest_receipt_registry(
            BATCH / "candidate_manifest_receipt_registry.json",
            ledger,
            BATCH / "measurement_contract.json",
            BATCH / "source_registry.json",
            paths,
        )
        self.assertEqual([row["run_id"] for row in manifests], list(stage4.TIER1_IDS))
        for run_id in stage4.TIER1_IDS:
            row = next(item for item in registered["logical_runs"] if item["run_id"] == run_id)
            self.assertRegex(row["manifest_payload_sha256"], r"^[0-9a-f]{64}$")

    def test_candidate_manifest_registry_hash_path_and_manifest_drift_are_rejected(self) -> None:
        ledger = json.loads((BATCH / "execution_ledger.json").read_text())
        manifest = (
            BATCH
            / "verification/engineering_overlay_cli_revision_02/QM3500S17/run_manifest.json"
        )
        changed = copy.deepcopy(ledger)
        changed["candidate_manifest_receipt_registry"]["sha256"] = "0" * 64
        with self.assertRaisesRegex(ValueError, "hash differs"):
            stage4.validate_candidate_manifest_receipt_registry(
                BATCH / "candidate_manifest_receipt_registry.json",
                changed,
                BATCH / "measurement_contract.json",
                BATCH / "source_registry.json",
                [manifest],
            )
        changed = copy.deepcopy(ledger)
        changed["candidate_manifest_receipt_registry"]["path"] = (
            "data/processed/stage4_qmain_sequential_20260912_v1/source_registry.json"
        )
        with self.assertRaisesRegex(ValueError, "path differs"):
            stage4.validate_candidate_manifest_receipt_registry(
                BATCH / "candidate_manifest_receipt_registry.json",
                changed,
                BATCH / "measurement_contract.json",
                BATCH / "source_registry.json",
                [manifest],
            )
        with tempfile.TemporaryDirectory(dir=ROOT / "tests") as directory:
            changed_manifest = json.loads(manifest.read_text())
            changed_manifest["seed"] = 23
            changed_path = Path(directory) / "run_manifest.json"
            changed_path.write_text(json.dumps(changed_manifest))
            with self.assertRaises(ValueError):
                stage4.validate_candidate_manifest_receipt_registry(
                    BATCH / "candidate_manifest_receipt_registry.json",
                    ledger,
                    BATCH / "measurement_contract.json",
                    BATCH / "source_registry.json",
                    [changed_path],
                )

    def test_duplicate_candidate_manifest_registration_is_no_overwrite(self) -> None:
        ledger_path = BATCH / "execution_ledger.json"
        manifest_registry = BATCH / "candidate_manifest_receipt_registry.json"
        before = (
            hashlib.sha256(ledger_path.read_bytes()).hexdigest(),
            hashlib.sha256(manifest_registry.read_bytes()).hexdigest(),
        )
        manifest = (
            BATCH
            / "verification/engineering_overlay_cli_revision_02/QM3500S17/run_manifest.json"
        )
        with self.assertRaisesRegex(FileExistsError, "already has a receipt"):
            stage4.register_candidate_manifest(
                ledger_path,
                BATCH / "measurement_contract.json",
                BATCH / "source_registry.json",
                BATCH / "runtime_source_registry.json",
                manifest_registry,
                "QM3500S17",
                manifest,
            )
        after = (
            hashlib.sha256(ledger_path.read_bytes()).hexdigest(),
            hashlib.sha256(manifest_registry.read_bytes()).hexdigest(),
        )
        self.assertEqual(before, after)

    def test_manifest_registration_rejects_unapproved_or_tier2_before_write(self) -> None:
        ledger = json.loads((BATCH / "execution_ledger.json").read_text())
        ledger["t43_launch_authorization"] = {"status": "prohibited", "quote": None}
        for counter in (
            "actual_sumo_starts", "actual_netconvert_operations",
            "actual_traci_connections", "actual_gui_starts",
        ):
            ledger[counter] = 0
        manifest = (
            BATCH
            / "verification/engineering_overlay_cli_revision_02/QM3500S17/run_manifest.json"
        )
        with tempfile.TemporaryDirectory() as directory:
            ledger_path = Path(directory) / "ledger.json"
            ledger_path.write_text(json.dumps(ledger))
            with self.assertRaisesRegex(ValueError, "requires T43 user authorization"):
                stage4.register_candidate_manifest(
                    ledger_path,
                    BATCH / "measurement_contract.json",
                    BATCH / "source_registry.json",
                    BATCH / "runtime_source_registry.json",
                    BATCH / "candidate_manifest_receipt_registry.json",
                    "QM3500S17",
                    manifest,
                )
        with self.assertRaisesRegex(ValueError, "only Tier-1 or reviewed q3650"):
            stage4.register_candidate_manifest(
                BATCH / "execution_ledger.json",
                BATCH / "measurement_contract.json",
                BATCH / "source_registry.json",
                BATCH / "runtime_source_registry.json",
                BATCH / "candidate_manifest_receipt_registry.json",
                "QM3350S17",
                manifest,
            )

    def test_decision_requires_manifest_receipt_registry_before_output(self) -> None:
        manifests = [
            BATCH
            / "verification/engineering_overlay_cli_revision_02"
            / run_id
            / "run_manifest.json"
            for run_id in stage4.TIER1_IDS
        ]
        with tempfile.TemporaryDirectory(dir=ROOT / "tests") as directory:
            output = Path(directory) / "decision"
            argv = [
                "decide-tier1",
                "--ledger", str(BATCH / "execution_ledger.json"),
                "--contract", str(BATCH / "measurement_contract.json"),
                "--registry", str(BATCH / "source_registry.json"),
                "--manifest-registry", str(BATCH / "source_registry.json"),
                "--output-dir", str(output),
            ]
            for manifest in manifests:
                argv.extend(("--run-manifest", str(manifest)))
            with self.assertRaises(ValueError):
                stage4.main(argv)
            self.assertFalse(output.exists())

    def test_register_and_decision_help_expose_manifest_registry(self) -> None:
        parsers = stage4.build_parser()._subparsers._group_actions[0].choices
        self.assertIn("--manifest-registry", parsers["register-manifest"].format_help())
        tier2_help = parsers["register-tier2-plan"].format_help()
        for option in ("--manifest-registry", "--decision", "--scientific-review-receipt",
                       "--gate-registration"):
            self.assertIn(option, tier2_help)
        for command in ("decide-tier1", "decide-final", "summarize-status"):
            self.assertIn("--manifest-registry", parsers[command].format_help())

    def test_exact_scientific_run_q3650_decision_and_tamper_rejection(self) -> None:
        path = ROOT / stage4.TIER1_SCIENTIFIC_DECISION_RELATIVE_PATH
        self.assertEqual(
            hashlib.sha256(path.read_bytes()).hexdigest(),
            "e0fb31613c2af5375aa6d6148da7a9c67ef5efacde1c0e822b806b6bc2d54b91",
        )
        decision = json.loads(path.read_text())
        stage4._validate_tier2_branch_decision_content(decision)
        mutations = []
        one_seed = copy.deepcopy(decision)
        one_seed["selected_tier2_runs"] = ["QM3650S17"]
        mutations.append(one_seed)
        mixed = copy.deepcopy(decision)
        mixed["selected_tier2_runs"] = ["QM3650S17", "QM3350S23"]
        mutations.append(mixed)
        extra = copy.deepcopy(decision)
        extra["selected_tier2_runs"].append("QM3700S17")
        mutations.append(extra)
        lower = copy.deepcopy(decision)
        lower["action"] = "run_q3350"
        mutations.append(lower)
        for changed in mutations:
            with self.subTest(changed=changed["selected_tier2_runs"]), self.assertRaisesRegex(
                ValueError, "exact run_q3650"
            ):
                stage4._validate_tier2_branch_decision_content(changed)

    def test_scientific_review_receipt_is_explicit_and_smoke_substitution_rejected(self) -> None:
        ledger, _, _ = stage4.validate_context(
            BATCH / "execution_ledger.json",
            BATCH / "measurement_contract.json",
            BATCH / "source_registry.json",
        )
        decision = stage4.validate_scientific_tier1_review_receipt(
            ROOT / stage4.TIER1_SCIENTIFIC_REVIEW_RECEIPT_RELATIVE_PATH,
            ROOT / stage4.TIER1_SCIENTIFIC_DECISION_RELATIVE_PATH,
            ledger,
        )
        self.assertEqual(decision["action"], "run_q3650")
        receipt = json.loads(
            (ROOT / stage4.TIER1_SCIENTIFIC_REVIEW_RECEIPT_RELATIVE_PATH).read_text()
        )
        self.assertIsNone(receipt["standalone_scientific_review_artifact_sha256"])
        with self.assertRaisesRegex(ValueError, "cannot substitute"):
            stage4.validate_scientific_tier1_review_receipt(
                ROOT / stage4.TIER1_SCIENTIFIC_REVIEW_RECEIPT_RELATIVE_PATH,
                BATCH / "verification/engineering_decision_cli_revision_01/branch_decision.json",
                ledger,
            )

    def test_final_candidate_set_rejects_single_mixed_and_extra_tier2(self) -> None:
        ledger = json.loads((BATCH / "execution_ledger.json").read_text())
        ledger["tier2_branch_gate"] = {"synthetic": True}
        tier1 = [manifest("QM3500S17", 17, 3500), manifest("QM3500S23", 23, 3500)]
        upper = [manifest("QM3650S17", 17, 3650), manifest("QM3650S23", 23, 3650)]
        stage4.validate_final_candidate_set(ledger, tier1 + upper)
        bad_sets = (
            tier1 + upper[:1],
            tier1 + [upper[0], manifest("QM3350S23", 23, 3350)],
            tier1 + upper + [manifest("QM3350S17", 17, 3350)],
        )
        for rows in bad_sets:
            with self.subTest(ids=[r["run_id"] for r in rows]), self.assertRaisesRegex(
                ValueError, "exact Tier-1 and q3650"
            ):
                stage4.validate_final_candidate_set(ledger, rows)

    def test_completed_tier2_plan_cannot_be_registered_again(self) -> None:
        ledger_path = BATCH / "execution_ledger.json"
        before_hash = hashlib.sha256(ledger_path.read_bytes()).hexdigest()
        before = json.loads(ledger_path.read_text())
        with self.assertRaisesRegex(ValueError, "unchanged Tier-1 counters"):
            stage4.register_tier2_plan(
                ledger_path,
                BATCH / "measurement_contract.json",
                BATCH / "source_registry.json",
                BATCH / "candidate_manifest_receipt_registry.json",
                ROOT / stage4.TIER1_SCIENTIFIC_DECISION_RELATIVE_PATH,
                ROOT / stage4.TIER1_SCIENTIFIC_REVIEW_RECEIPT_RELATIVE_PATH,
                ROOT / stage4.TIER2_BRANCH_GATE_RELATIVE_PATH,
            )
        self.assertEqual(hashlib.sha256(ledger_path.read_bytes()).hexdigest(), before_hash)
        after = json.loads(ledger_path.read_text())
        for field in ("actual_sumo_starts", "actual_netconvert_operations",
                      "actual_traci_connections", "actual_gui_starts"):
            self.assertEqual(after[field], before[field])
        self.assertTrue((ROOT / stage4.TIER2_BRANCH_GATE_RELATIVE_PATH).exists())

    def test_current_tier2_gate_is_exact_and_preserves_completed_execution_counters(self) -> None:
        ledger, _, registry = stage4.validate_context(
            BATCH / "execution_ledger.json",
            BATCH / "measurement_contract.json",
            BATCH / "source_registry.json",
        )
        gate = stage4.validate_tier2_branch_gate(ledger, registry)
        self.assertEqual(gate["action"], "run_q3650")
        self.assertEqual(gate["selected_run_ids"], list(stage4.UPPER_IDS))
        self.assertEqual(gate["cancelled_run_ids"], list(stage4.LOWER_IDS))
        states = {row["run_id"]: row for row in ledger["logical_runs"]}
        self.assertTrue(all(states[run_id]["state"] == "completed_valid"
                            for run_id in stage4.UPPER_IDS))
        self.assertTrue(all(states[run_id]["state"] == "cancelled_by_stop_rule"
                            and states[run_id]["terminal"] is True
                            for run_id in stage4.LOWER_IDS))
        self.assertEqual(
            [ledger[key] for key in ("actual_sumo_starts", "actual_netconvert_operations",
                                     "actual_traci_connections", "actual_gui_starts")],
            [4, 4, 0, 0],
        )

    def test_scientific_decision_smoke_path_is_rejected_even_with_identical_bytes(self) -> None:
        ledger = json.loads((BATCH / "execution_ledger.json").read_text())
        smoke = BATCH / "verification/engineering_decision_cli_revision_01/branch_decision.json"
        scientific = ROOT / stage4.TIER1_SCIENTIFIC_DECISION_RELATIVE_PATH
        self.assertEqual(smoke.read_bytes(), scientific.read_bytes())
        with self.assertRaisesRegex(ValueError, "cannot substitute"):
            stage4.validate_scientific_tier1_review_receipt(
                ROOT / stage4.TIER1_SCIENTIFIC_REVIEW_RECEIPT_RELATIVE_PATH,
                smoke,
                ledger,
            )


class Stage4FinalEvidenceSnapshotTests(unittest.TestCase):
    snapshot_path = BATCH / "final_evidence_ledger_snapshot.json"

    @staticmethod
    def canonical_hash(value: object) -> str:
        payload = json.dumps(
            value, sort_keys=True, separators=(",", ":"), ensure_ascii=False
        ).encode("utf-8")
        return hashlib.sha256(payload).hexdigest()

    def test_final_evidence_snapshot_is_complete_and_registry_bound(self) -> None:
        snapshot_bytes = self.snapshot_path.read_bytes()
        snapshot = json.loads(snapshot_bytes)
        current = json.loads((BATCH / "execution_ledger.json").read_text())
        binding = current["final_evidence_ledger_snapshot"]
        self.assertEqual(
            hashlib.sha256(snapshot_bytes).hexdigest(), binding["sha256"]
        )
        self.assertEqual(
            self.snapshot_path.relative_to(ROOT).as_posix(), binding["path"]
        )
        self.assertEqual(
            snapshot["snapshot_role"],
            "immutable_normative_final_evidence_ledger_input",
        )
        frozen = snapshot["execution_ledger"]
        self.assertEqual(
            self.canonical_hash(frozen),
            snapshot["canonical_execution_ledger_sha256"],
        )
        self.assertEqual(
            snapshot["source_execution_ledger"]["sha256"],
            "a2313d754c982ab4a768dcfcc6810975ffa75bc81dd8ae5b70c0d69c35d26199",
        )
        self.assertEqual(
            [
                frozen[key]
                for key in (
                    "actual_sumo_starts",
                    "actual_netconvert_operations",
                    "actual_traci_connections",
                    "actual_gui_starts",
                )
            ],
            [4, 4, 0, 0],
        )
        self.assertEqual(len(frozen["attempts"]), 4)
        self.assertEqual(
            {row["run_id"] for row in frozen["attempts"]},
            set(stage4.TIER1_IDS + stage4.UPPER_IDS),
        )
        self.assertTrue(
            all(row["status"] == "archived_technical_valid" for row in frozen["attempts"])
        )
        self.assertEqual(
            frozen["tier2_data_analysis_revision_02"]["status"],
            "passed_ready_for_scientific_review",
        )

        approved_registry = json.loads((BATCH / "source_registry.json").read_text())
        archive_files = 0
        for run_id in stage4.TIER1_IDS + stage4.UPPER_IDS:
            row, source_map_path = stage4.validate_runtime_source_registry(
                BATCH / "runtime_source_registry.json",
                frozen,
                approved_registry,
                run_id,
            )
            self.assertEqual(row["run_id"], run_id)
            source_map = json.loads(source_map_path.read_text())
            self.assertEqual(source_map["archive_file_count"], 29)
            archive_files += source_map["archive_file_count"]
        self.assertEqual(archive_files, 116)

        receipt_registry = json.loads(
            (BATCH / "candidate_manifest_receipt_registry.json").read_text()
        )
        manifest_paths = [ROOT / row["manifest_path"] for row in receipt_registry["receipts"]]
        _, manifests = stage4.validate_candidate_manifest_receipt_registry(
            BATCH / "candidate_manifest_receipt_registry.json",
            frozen,
            BATCH / "measurement_contract.json",
            BATCH / "source_registry.json",
            manifest_paths,
        )
        self.assertEqual(
            {row["run_id"] for row in manifests},
            set(stage4.TIER1_IDS + stage4.UPPER_IDS),
        )
        stage4.validate_tier2_branch_gate(frozen, approved_registry)

        historical = snapshot["historical_unpreserved_ledger_binding"]
        self.assertEqual(
            historical["sha256"],
            "b745ccaedf5a9b8c4bcf94119711f9fa4c7e0c12b12d3125c7bd5e337faefff5",
        )
        self.assertFalse(historical["exact_immutable_ledger_snapshot_available"])
        ledger_artifact_hashes = {
            hashlib.sha256(path.read_bytes()).hexdigest()
            for path in BATCH.glob("*ledger*.json")
        }
        self.assertNotIn(historical["sha256"], ledger_artifact_hashes)

    def test_future_current_ledger_metadata_does_not_change_snapshot_validation(self) -> None:
        before = self.snapshot_path.read_bytes()
        snapshot = json.loads(before)
        self.assertFalse(
            snapshot["consumer_contract"]["current_execution_ledger_is_normative"]
        )
        self.assertFalse(
            snapshot["consumer_contract"]
            ["post_snapshot_review_receipt_backlink_required_in_snapshot"]
        )
        frozen = copy.deepcopy(snapshot["execution_ledger"])
        current = json.loads((BATCH / "execution_ledger.json").read_text())
        with tempfile.TemporaryDirectory(dir=ROOT / "tests") as directory:
            future_path = Path(directory) / "future_execution_ledger.json"
            current["future_review_metadata"] = {
                "receipt": "future-only mutable status metadata"
            }
            future_path.write_text(json.dumps(current, indent=2) + "\n")
            self.assertNotEqual(
                hashlib.sha256(future_path.read_bytes()).hexdigest(),
                snapshot["source_execution_ledger"]["sha256"],
            )

        approved_registry = json.loads((BATCH / "source_registry.json").read_text())
        for run_id in stage4.TIER1_IDS + stage4.UPPER_IDS:
            stage4.validate_runtime_source_registry(
                BATCH / "runtime_source_registry.json",
                frozen,
                approved_registry,
                run_id,
            )
        self.assertEqual(
            self.canonical_hash(frozen),
            snapshot["canonical_execution_ledger_sha256"],
        )
        self.assertEqual(before, self.snapshot_path.read_bytes())


if __name__ == "__main__":
    unittest.main()

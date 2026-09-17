"""Independent contract and logic checks for the Stage 4 qMain adapter.

Expected values are calculated locally in this file.  The production aggregation,
EJMI, and branch functions are invoked only as the system under test.
"""
from __future__ import annotations

import copy
from collections import defaultdict
import hashlib
import itertools
import json
from pathlib import Path
import tempfile
import unittest
import xml.etree.ElementTree as ET

from src.analysis import analyze_stage4_qmain as production


ROOT = Path(__file__).resolve().parents[1]
BATCH = ROOT / "data/processed/stage4_qmain_sequential_20260912_v1"


def actual_contract() -> dict:
    return json.loads((BATCH / "measurement_contract.json").read_text(encoding="utf-8"))


def independent_combine(rows: list[dict]) -> dict:
    return {
        "q_vehph": sum(row["n_entered"] for row in rows) * 120.0,
        "speed_mps": sum(row["speed_mps"] * row["n_contrib"] for row in rows)
        / sum(row["n_contrib"] for row in rows),
        "occupancy_percent": sum(row["occupancy_percent"] for row in rows) / 2.0,
    }


def bins(speed: float, occupancy: float) -> list[dict]:
    return [
        {
            "begin": float(begin),
            "end": float(begin + 30),
            "q_vehph": 3300.0,
            "speed_mps": speed,
            "occupancy_percent": occupancy,
            "n_contrib": 20,
        }
        for begin in range(0, 2700, 30)
    ]


def independent_aggregate(rows: list[dict], begin: float, end: float) -> dict:
    selected = [row for row in rows if begin <= row["begin"] and row["end"] <= end]
    duration = sum(row["end"] - row["begin"] for row in selected)
    contributions = sum(row["n_contrib"] for row in selected)
    return {
        "begin": begin,
        "end": end,
        "covered_seconds": duration,
        "q_vehph": sum(row["q_vehph"] * (row["end"] - row["begin"]) for row in selected) / duration,
        "speed_mps": sum(row["speed_mps"] * row["n_contrib"] for row in selected
                         if row["speed_mps"] is not None) / contributions,
        "occupancy_percent": sum(row["occupancy_percent"] * (row["end"] - row["begin"]) for row in selected) / duration,
        "n_contrib": contributions,
    }


def manifest(run_id: str, seed: int, q_main: int, speed: float, occupancy: float) -> dict:
    values = bins(speed, occupancy)
    return {
        "run_id": run_id,
        "seed": seed,
        "q_main": q_main,
        "technical_qualified": True,
        "outside_M_1500": 0,
        "single_factor_hash_check": True,
        "endpoints": [
            {"class": cls, "endpoint_s": endpoint, "coverage": True}
            for endpoint in (1500.0, 2700.0)
            for cls in ("M", "R", "U", "X")
        ],
        "e1": {
            "bins_30s": values,
            "aggregates": {
                "A": independent_aggregate(values, 0.0, 1500.0),
                "B": independent_aggregate(values, 300.0, 1500.0),
            },
        },
        "r_passage": {"status": "clear_passage"},
        "ejmi": {"status": "not_identified"},
    }


def ledger() -> dict:
    points = {
        "C17": 3200, "C23": 3200, "MH17": 3800, "MH23": 3800,
        "QM3500S17": 3500, "QM3500S23": 3500,
        "QM3350S17": 3350, "QM3350S23": 3350,
        "QM3650S17": 3650, "QM3650S23": 3650,
    }
    return {"logical_runs": [{"run_id": run_id, "q_main": points[run_id],
                                "seed": 17 if run_id.endswith("17") else 23}
                               for run_id in production.ALL_RUN_IDS]}


class IndependentArithmeticChecks(unittest.TestCase):
    def test_lane_occupancy_mean_speed_weighting_and_units(self) -> None:
        source = [
            {"detector_id": "l0", "begin": 0.0, "end": 30.0, "n_contrib": 2,
             "n_entered": 3, "speed_mps": 10.0, "occupancy_percent": 4.0},
            {"detector_id": "l1", "begin": 0.0, "end": 30.0, "n_contrib": 8,
             "n_entered": 7, "speed_mps": 25.0, "occupancy_percent": 10.0},
        ]
        expected = independent_combine(source)
        observed = production.combine_two_lane_e1(source, {"l0", "l1"}, 0.0, 30.0)
        self.assertEqual(len(observed), 1)
        for key, value in expected.items():
            self.assertAlmostEqual(observed[0][key], value, places=12)
        self.assertAlmostEqual(observed[0]["occupancy_percent"], 7.0)
        self.assertAlmostEqual(observed[0]["speed_mps"], 22.0)

    def test_contract_enforces_exact_registered_ejmi_margins(self) -> None:
        changed = actual_contract()
        changed["ejmi"]["margins"]["A"]["delta_v_mps"] += 0.001
        with self.assertRaises(ValueError):
            production.validate_contract(changed)

    def test_contract_enforces_period_and_occupancy_rule(self) -> None:
        for field, value in (("period_s", 60.0), ("occupancy_rule", "sum and call density")):
            with self.subTest(field=field):
                changed = actual_contract()
                changed["e1"][field] = value
                with self.assertRaises(ValueError):
                    production.validate_contract(changed)


class IndependentEJMIChecks(unittest.TestCase):
    def setUp(self) -> None:
        self.lower = manifest("C17", 17, 3200, 30.0, 5.0)
        self.upper = manifest("MH17", 17, 3800, 31.0, 6.0)
        self.candidate = manifest("QM3500S17", 17, 3500, 28.0, 8.0)

    def test_exact_A_B_delta_and_strict_envelope(self) -> None:
        contract = actual_contract()
        result = production.evaluate_ejmi(self.candidate, self.lower, self.upper, contract)
        self.assertEqual(result["status"], "positive")
        boundary = copy.deepcopy(self.candidate)
        delta = contract["ejmi"]["margins"]["A"]
        boundary["e1"]["aggregates"]["A"]["speed_mps"] = 30.0 - delta["delta_v_mps"]
        boundary["e1"]["aggregates"]["A"]["occupancy_percent"] = 6.0 + delta["delta_occ_percentage_points"]
        observed = production.evaluate_ejmi(boundary, self.lower, self.upper, contract)
        self.assertFalse(observed["aggregate_checks"]["A"])
        self.assertEqual(observed["status"], "not_identified")

    def test_120_60_30_persistence_requires_three_of_four(self) -> None:
        contract = actual_contract()
        three = copy.deepcopy(self.candidate)
        two = copy.deepcopy(self.candidate)
        for candidate in (three, two):
            for row in candidate["e1"]["bins_30s"]:
                if 300 <= row["begin"] < 1500:
                    row.update(speed_mps=31.0, occupancy_percent=5.0)
        # In [300,420), one failing 30 s bin preserves both 60 s means and gives 3/4.
        for index in (10, 11, 12):
            three["e1"]["bins_30s"][index].update(speed_mps=28.0, occupancy_percent=8.0)
        # Alternating two failures preserves the 60/120 means but yields only 2/4.
        for index in (10, 12):
            two["e1"]["bins_30s"][index].update(speed_mps=28.0, occupancy_percent=8.0)
        self.assertTrue(production.evaluate_ejmi(three, self.lower, self.upper, contract)["persistence"]["passed"])
        self.assertFalse(production.evaluate_ejmi(two, self.lower, self.upper, contract)["persistence"]["passed"])


class IndependentRChecks(unittest.TestCase):
    @staticmethod
    def write_fcd(path: Path, frames: list[tuple[int, list[tuple[str, str]]]]) -> None:
        root = ET.Element("fcd-export")
        for time_s, vehicles in frames:
            node = ET.SubElement(root, "timestep", {"time": str(time_s)})
            for identity, lane in vehicles:
                ET.SubElement(node, "vehicle", {"id": identity, "lane": lane})
        ET.ElementTree(root).write(path)

    def test_duplicate_vehicle_identity_in_one_frame_is_unresolved(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "fcd.xml"
            self.write_fcd(path, [
                (0, [("R_flow.0", "ramp_accel_0")]),
                (1, [("R_flow.0", "main_down_0"), ("R_flow.0", "main_down_0")]),
            ])
            raw = production.read_r_passage(path, {"main_down_0"}, {0.0, 1.0},
                                            {"ramp_accel_0", "main_down_0"})
            result = production.classify_r_passage(raw, {"R_flow.0": {"class": "R", "arrival": 2.0}})
            self.assertEqual(result["status"], "unresolved")

    def test_coverage_and_arrival_contradiction_matrix(self) -> None:
        clear = {"events": [], "coverage_complete": True}
        self.assertEqual(production.classify_r_passage(clear, {})["status"], "clear_exclusion")
        missing = {"events": [], "coverage_complete": False}
        self.assertEqual(production.classify_r_passage(missing, {})["status"], "unresolved")
        contradictory = {"events": [], "coverage_complete": True}
        trips = {"R_flow.0": {"class": "R", "arrival": 100.0}}
        self.assertEqual(production.classify_r_passage(contradictory, trips)["status"], "unresolved")


class IndependentBranchAndDenominatorChecks(unittest.TestCase):
    @staticmethod
    def tier(r17: str, e17: str, r23: str, e23: str, qualified: bool = True) -> list[dict]:
        rows = []
        for run_id, seed, r_state, e_state in (
            ("QM3500S17", 17, r17, e17), ("QM3500S23", 23, r23, e23)
        ):
            row = manifest(run_id, seed, 3500, 28.0, 8.0)
            row["technical_qualified"] = qualified
            row["r_passage"]["status"] = r_state
            row["ejmi"]["status"] = e_state
            rows.append(row)
        return rows

    def test_all_two_seed_branch_combinations(self) -> None:
        states = ("clear_passage", "clear_exclusion", "unresolved")
        ejmi = ("positive", "not_identified", "unresolved")
        for r17, e17, r23, e23 in itertools.product(states, ejmi, states, ejmi):
            with self.subTest(r17=r17, e17=e17, r23=r23, e23=e23):
                if (r17, e17, r23, e23) == ("clear_passage", "positive", "clear_passage", "positive"):
                    expected = "stop_supports_A"
                elif (r17, e17, r23, e23) == ("clear_passage", "not_identified", "clear_passage", "not_identified"):
                    expected = "run_q3650"
                elif (r17, e17, r23, e23) == ("clear_exclusion", "not_identified", "clear_exclusion", "not_identified"):
                    expected = "run_q3350"
                else:
                    expected = "stop_unresolved"
                observed = production.decide_tier1(self.tier(r17, e17, r23, e23))
                self.assertEqual(observed["action"], expected)

    def test_mixed_tier2_branch_is_rejected(self) -> None:
        decision = {
            "action": "invalid_mixed_branch",
            "selected_tier2_runs": ["QM3350S17", "QM3650S23"],
            "cancelled_by_stop_rule": ["QM3350S23", "QM3650S17"],
        }
        refs = [manifest("C17", 17, 3200, 30, 5), manifest("C23", 23, 3200, 30, 5),
                manifest("MH17", 17, 3800, 31, 6), manifest("MH23", 23, 3800, 31, 6)]
        with self.assertRaises(ValueError):
            production.build_logical_statuses(ledger(), refs, decision)

    def test_reference_terminal_status_requires_reference_manifest(self) -> None:
        decision = production.decide_tier1(self.tier("clear_passage", "positive", "clear_passage", "positive"))
        summary = production.build_logical_statuses(ledger(), self.tier("clear_passage", "positive", "clear_passage", "positive"), decision)
        self.assertFalse(summary["all_registered_terminal"])
        by_id = {row["run_id"]: row for row in summary["logical_statuses"]}
        self.assertFalse(by_id["C17"]["terminal"])
        self.assertEqual(summary["denominators"]["used_valid_run_manifests"], 2)

    def test_manifest_identity_and_endpoint_denominator_are_validated(self) -> None:
        decision = production.decide_tier1(self.tier("clear_passage", "positive", "clear_passage", "positive"))
        rows = [manifest("C17", 23, 9999, 30, 5), manifest("C23", 23, 3200, 30, 5),
                manifest("MH17", 17, 3800, 31, 6), manifest("MH23", 23, 3800, 31, 6)]
        rows += self.tier("clear_passage", "positive", "clear_passage", "positive")
        rows[0]["endpoints"] = [{"class": "M", "endpoint_s": 1500.0, "coverage": True}] * 8
        with self.assertRaises(ValueError):
            production.build_logical_statuses(ledger(), rows, decision)

    def test_stop_rule_cancels_all_tier2_and_preserves_registered_denominator(self) -> None:
        tier = self.tier("clear_passage", "positive", "clear_passage", "positive")
        decision = production.decide_tier1(tier)
        self.assertEqual(set(decision["cancelled_by_stop_rule"]), set(production.LOWER_IDS + production.UPPER_IDS))
        refs = [manifest("C17", 17, 3200, 30, 5), manifest("C23", 23, 3200, 30, 5),
                manifest("MH17", 17, 3800, 31, 6), manifest("MH23", 23, 3800, 31, 6)]
        summary = production.build_logical_statuses(ledger(), refs + tier, decision)
        self.assertEqual(summary["denominators"]["registered_logical_runs"], 10)
        self.assertEqual(summary["denominators"]["registered_terminal_runs"], 10)
        self.assertEqual(summary["denominators"]["class_endpoint_units_observed"], 48)

    def test_one_complete_tier2_branch_has_exact_terminal_denominators(self) -> None:
        tier = self.tier("clear_exclusion", "not_identified", "clear_exclusion", "not_identified")
        decision = production.decide_tier1(tier)
        refs = [manifest("C17", 17, 3200, 30, 5), manifest("C23", 23, 3200, 30, 5),
                manifest("MH17", 17, 3800, 31, 6), manifest("MH23", 23, 3800, 31, 6)]
        lower = [manifest("QM3350S17", 17, 3350, 29, 7), manifest("QM3350S23", 23, 3350, 29, 7)]
        summary = production.build_logical_statuses(ledger(), refs + tier + lower, decision)
        self.assertTrue(summary["all_registered_terminal"])
        self.assertEqual(summary["denominators"]["registered_terminal_runs"], 10)
        self.assertEqual(summary["denominators"]["used_valid_run_manifests"], 8)
        self.assertEqual(summary["denominators"]["class_endpoint_units_expected"], 64)
        self.assertEqual(summary["denominators"]["class_endpoint_units_observed"], 64)
        self.assertEqual(summary["denominators"]["adjacent_matched_seed_comparisons_expected"], 6)

    def test_registered_manifest_payload_hash_detects_post_registration_change(self) -> None:
        tier = self.tier("clear_passage", "positive", "clear_passage", "positive")
        rows = [manifest("C17", 17, 3200, 30, 5), manifest("C23", 23, 3200, 30, 5),
                manifest("MH17", 17, 3800, 31, 6), manifest("MH23", 23, 3800, 31, 6)] + tier
        registered = ledger()
        registered["manifest_hash_required"] = True
        by_id = {row["run_id"]: row for row in rows}
        for item in registered["logical_runs"]:
            if item["run_id"] in by_id:
                encoded = json.dumps(by_id[item["run_id"]], sort_keys=True, separators=(",", ":"),
                                     allow_nan=False).encode("utf-8")
                item["manifest_payload_sha256"] = hashlib.sha256(encoded).hexdigest()
        rows[0]["q_main"] = 3201
        with self.assertRaises(ValueError):
            production.build_logical_statuses(registered, rows, production.decide_tier1(tier))


class IndependentAuthorizationAndSafetyChecks(unittest.TestCase):
    def test_current_context_is_authorized_t43_complete_through_tier2(self) -> None:
        ledger_value, contract_value, registry_value = production.validate_context(
            BATCH / "execution_ledger.json", BATCH / "measurement_contract.json", BATCH / "source_registry.json"
        )
        self.assertEqual(ledger_value["actual_sumo_starts"], 4)
        self.assertEqual(ledger_value["actual_netconvert_operations"], 4)
        self.assertEqual(ledger_value["actual_traci_connections"], 0)
        self.assertEqual(ledger_value["actual_gui_starts"], 0)
        self.assertEqual(ledger_value["t43_launch_authorization"]["status"], "user_approved")
        self.assertEqual(
            ledger_value["t43_launch_authorization"]["quote"],
            "批准按 `docs/STAGE4_T43_LAUNCH_CONFIRMATION_PACKAGE.md` 执行 T43。",
        )
        self.assertFalse(contract_value["simulation_launch_capability"])
        self.assertTrue(all(row.get("source_map_path") is None for row in registry_value["runs"][4:]))
        by_id = {row["run_id"]: row for row in ledger_value["logical_runs"]}
        self.assertTrue(all(by_id[run_id]["actual_sumo_starts"] == 1
                            for run_id in production.TIER1_IDS + production.UPPER_IDS))
        self.assertTrue(all(by_id[run_id]["actual_sumo_starts"] == 0
                            for run_id in production.LOWER_IDS))

    def test_payload_is_binding_and_human_proposal_snapshot_is_nonbinding(self) -> None:
        ledger_value = json.loads((BATCH / "execution_ledger.json").read_text(encoding="utf-8"))
        contract_value = actual_contract()
        registry_value = json.loads((BATCH / "source_registry.json").read_text(encoding="utf-8"))
        self.assertNotIn("proposal_path", contract_value)
        self.assertNotIn("proposal_sha256", contract_value)
        self.assertNotIn("proposal_sha256", ledger_value["input_hashes"])
        snapshot = contract_value["non_binding_historical_proposal_snapshot"]
        self.assertEqual(snapshot["role"], "non_binding_historical_snapshot")
        self.assertIn("must not compare", snapshot["validation_rule"])
        self.assertEqual(
            ledger_value["non_binding_historical_traces"]["stage4_human_proposal_snapshot"]["role"],
            "non_binding_historical_snapshot",
        )
        payload_path = ROOT / contract_value["registration_payload_path"]
        payload_hash = hashlib.sha256(payload_path.read_bytes()).hexdigest()
        self.assertEqual(contract_value["registration_payload_sha256"], payload_hash)
        self.assertEqual(ledger_value["input_hashes"]["registration_payload_sha256"], payload_hash)
        self.assertEqual(registry_value["registration_payload_sha256"], payload_hash)

        # validate_context must remain independent of the mutable human Markdown snapshot.
        for proposal_path, proposal_hash in (
            ("docs/changed_human_proposal.md", "0" * 64),
            ("docs/nonexistent_human_proposal.md", None),
        ):
            with self.subTest(proposal_path=proposal_path), tempfile.TemporaryDirectory() as directory:
                changed_contract = copy.deepcopy(contract_value)
                changed_contract["non_binding_historical_proposal_snapshot"]["path"] = proposal_path
                changed_contract["non_binding_historical_proposal_snapshot"]["sha256"] = proposal_hash
                changed_ledger = copy.deepcopy(ledger_value)
                changed_ledger["non_binding_historical_traces"]["stage4_human_proposal_snapshot"] = {
                    "path": proposal_path,
                    "role": "non_binding_historical_snapshot",
                    "sha256": proposal_hash,
                }
                root = Path(directory)
                contract_path, registry_path, ledger_path = (
                    root / "contract.json", root / "registry.json", root / "ledger.json")
                contract_path.write_text(json.dumps(changed_contract), encoding="utf-8")
                registry_path.write_text(json.dumps(registry_value), encoding="utf-8")
                changed_ledger["input_hashes"]["contract_sha256"] = hashlib.sha256(
                    contract_path.read_bytes()).hexdigest()
                changed_ledger["t43_launch_authorization"]["approved_contract_sha256"] = (
                    changed_ledger["input_hashes"]["contract_sha256"]
                )
                changed_ledger["input_hashes"]["source_registry_sha256"] = hashlib.sha256(
                    registry_path.read_bytes()).hexdigest()
                changed_ledger["t43_launch_authorization"]["approved_source_registry_sha256"] = (
                    changed_ledger["input_hashes"]["source_registry_sha256"]
                )
                ledger_path.write_text(json.dumps(changed_ledger), encoding="utf-8")
                production.validate_context(ledger_path, contract_path, registry_path)

    def test_registration_payload_hash_crosslinks_and_scientific_drift_guard(self) -> None:
        ledger_value = json.loads((BATCH / "execution_ledger.json").read_text(encoding="utf-8"))
        contract_value = actual_contract()
        registry_value = json.loads((BATCH / "source_registry.json").read_text(encoding="utf-8"))
        payload_path = ROOT / contract_value["registration_payload_path"]
        observed = hashlib.sha256(payload_path.read_bytes()).hexdigest()
        self.assertEqual(contract_value["registration_payload_sha256"], observed)
        self.assertEqual(ledger_value["input_hashes"]["registration_payload_sha256"], observed)
        self.assertEqual(registry_value["registration_payload_sha256"], observed)
        payload = json.loads(payload_path.read_text(encoding="utf-8"))
        production.validate_registration_payload(payload)
        payload["branch_rule"]["maximum_tier2_branches"] = 2
        with self.assertRaises(ValueError):
            production.validate_registration_payload(payload)

    def test_user_approved_t43_state_requires_nonpending_quote(self) -> None:
        ledger_value = json.loads((BATCH / "execution_ledger.json").read_text(encoding="utf-8"))
        for launch in ({"status": "user_approved", "quote": None},
                       {"status": "user_approved", "quote": "批准运行"}):
            with self.subTest(launch=launch), tempfile.TemporaryDirectory() as directory:
                ledger_value["t43_launch_authorization"] = launch
                path = Path(directory) / "ledger.json"
                path.write_text(json.dumps(ledger_value), encoding="utf-8")
                with self.assertRaises(ValueError):
                    production.validate_context(path, BATCH / "measurement_contract.json", BATCH / "source_registry.json")

    def test_complete_t43_authorization_envelope_is_accepted_by_context_validator(self) -> None:
        ledger_value = json.loads((BATCH / "execution_ledger.json").read_text(encoding="utf-8"))
        contract_path = BATCH / "measurement_contract.json"
        registry_path = BATCH / "source_registry.json"
        payload_path = BATCH / "registration_payload.json"
        ledger_value["t43_launch_authorization"] = {
            "status": "user_approved",
            "quote": "批准按最终T43运行卡执行已注册运行",
            "scope": "T43_exact_registered_runs_only",
            "approved_registration_payload_sha256": hashlib.sha256(payload_path.read_bytes()).hexdigest(),
            "approved_contract_sha256": hashlib.sha256(contract_path.read_bytes()).hexdigest(),
            "approved_source_registry_sha256": hashlib.sha256(registry_path.read_bytes()).hexdigest(),
        }
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "ledger.json"
            path.write_text(json.dumps(ledger_value), encoding="utf-8")
            observed, _, _ = production.validate_context(path, contract_path, registry_path)
            self.assertEqual(observed["t43_launch_authorization"]["status"], "user_approved")

    def test_prohibited_t43_rejects_any_nonzero_execution_counter(self) -> None:
        for field in ("actual_sumo_starts", "actual_netconvert_operations",
                      "actual_traci_connections", "actual_gui_starts"):
            with self.subTest(field=field), tempfile.TemporaryDirectory() as directory:
                value = json.loads((BATCH / "execution_ledger.json").read_text(encoding="utf-8"))
                value["t43_launch_authorization"] = {"status": "prohibited", "quote": None}
                for counter in ("actual_sumo_starts", "actual_netconvert_operations",
                                "actual_traci_connections", "actual_gui_starts"):
                    value[counter] = 0
                value[field] = 1
                path = Path(directory) / "ledger.json"
                path.write_text(json.dumps(value), encoding="utf-8")
                with self.assertRaises(ValueError):
                    production.validate_context(path, BATCH / "measurement_contract.json", BATCH / "source_registry.json")

    def test_exclusive_output_refuses_overwrite(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "value.json"
            production.write_json_exclusive(path, {"first": True})
            before = hashlib.sha256(path.read_bytes()).hexdigest()
            with self.assertRaises(FileExistsError):
                production.write_json_exclusive(path, {"second": True})
            self.assertEqual(hashlib.sha256(path.read_bytes()).hexdigest(), before)

    def test_runtime_overlay_is_ledger_bound_and_resolves_all_completed_candidates(self) -> None:
        ledger_value = json.loads((BATCH / "execution_ledger.json").read_text(encoding="utf-8"))
        registry_value = json.loads((BATCH / "source_registry.json").read_text(encoding="utf-8"))
        overlay_path = BATCH / "runtime_source_registry.json"
        overlay = json.loads(overlay_path.read_text(encoding="utf-8"))
        binding = ledger_value["runtime_source_registry_overlay"]
        self.assertEqual(ROOT / binding["path"], overlay_path)
        self.assertEqual(binding["sha256"], hashlib.sha256(overlay_path.read_bytes()).hexdigest())
        completed_ids = production.TIER1_IDS + production.UPPER_IDS
        self.assertEqual([row["run_id"] for row in overlay["runs"]], list(completed_ids))
        attempts = {row["attempt_id"]: row for row in ledger_value["attempts"]}
        for run_id in completed_ids:
            row, source_map_path = production.validate_runtime_source_registry(
                overlay_path, ledger_value, registry_value, run_id)
            attempt = attempts[row["attempt_id"]]
            self.assertEqual(row["source_map_path"], attempt["source_map_path"])
            self.assertEqual(row["source_map_sha256"], hashlib.sha256(source_map_path.read_bytes()).hexdigest())
            source_map = json.loads(source_map_path.read_text(encoding="utf-8"))
            self.assertEqual(source_map["logical_run_id"], run_id)
            self.assertEqual(source_map["archive_file_count"], 29)
            self.assertEqual(len(source_map["file_map"]), 29)
            receipt_path = ROOT / row["engineering_verification_path"]
            self.assertEqual(row["engineering_verification_sha256"],
                             hashlib.sha256(receipt_path.read_bytes()).hexdigest())
            summary_row = next(item for item in source_map["file_map"]
                               if item["archive_relative_path"].endswith("/summary.json"))
            summary_path = ROOT / summary_row["archive_relative_path"]
            self.assertEqual(row["summary_sha256"], hashlib.sha256(summary_path.read_bytes()).hexdigest())

    def test_runtime_overlay_rejects_identity_and_provenance_drift(self) -> None:
        base_ledger = json.loads((BATCH / "execution_ledger.json").read_text(encoding="utf-8"))
        registry_value = json.loads((BATCH / "source_registry.json").read_text(encoding="utf-8"))
        base_overlay = json.loads((BATCH / "runtime_source_registry.json").read_text(encoding="utf-8"))
        mutations = {
            "duplicate": lambda value: value["runs"].append(copy.deepcopy(value["runs"][0])),
            "tier2": lambda value: value["runs"][0].update(run_id="QM3650S17"),
            "reference": lambda value: value["runs"][0].update(run_id="C17"),
            "unexecuted_attempt": lambda value: value["runs"][0].update(attempt_id="missing_attempt"),
            "source_map": lambda value: value["runs"][0].update(source_map_sha256="0" * 64),
            "archive": lambda value: value["runs"][0].update(archive_runtime_path="artifacts/wrong"),
            "receipt": lambda value: value["runs"][0].update(engineering_verification_sha256="0" * 64),
            "summary": lambda value: value["runs"][0].update(summary_sha256="0" * 64),
        }
        temp_parent = BATCH / "verification"
        for label, mutate in mutations.items():
            with self.subTest(label=label), tempfile.TemporaryDirectory(dir=temp_parent) as directory:
                root = Path(directory)
                changed_overlay = copy.deepcopy(base_overlay)
                mutate(changed_overlay)
                overlay_path = root / "runtime_registry.json"
                overlay_path.write_text(json.dumps(changed_overlay), encoding="utf-8")
                changed_ledger = copy.deepcopy(base_ledger)
                changed_ledger["runtime_source_registry_overlay"] = {
                    "path": overlay_path.relative_to(ROOT).as_posix(),
                    "sha256": hashlib.sha256(overlay_path.read_bytes()).hexdigest(),
                }
                with self.assertRaises(ValueError):
                    production.validate_runtime_source_registry(
                        overlay_path, changed_ledger, registry_value, "QM3500S17")

    def test_candidate_cli_rejects_bad_overlay_before_output_creation(self) -> None:
        with tempfile.TemporaryDirectory(dir=BATCH / "verification") as directory:
            root = Path(directory)
            output = root / "must_not_exist"
            with self.assertRaises(ValueError):
                production.main([
                    "analyze-run",
                    "--ledger", str(BATCH / "execution_ledger.json"),
                    "--contract", str(BATCH / "measurement_contract.json"),
                    "--registry", str(BATCH / "source_registry.json"),
                    "--runtime-registry", str(BATCH / "source_registry.json"),
                    "--output-dir", str(output),
                    "--run-id", "QM3500S17",
                    "--lower-manifest", str(BATCH / "verification/reference_C17_revision_01/run_manifest.json"),
                    "--upper-manifest", str(BATCH / "verification/reference_MH17_revision_01/run_manifest.json"),
                ])
            self.assertFalse(output.exists())


class IndependentReferenceArchiveChecks(unittest.TestCase):
    @staticmethod
    def archive_file(source_map_path: Path, suffix: str) -> Path:
        source = json.loads(source_map_path.read_text(encoding="utf-8"))
        rows = [row for row in source["file_map"] if row["original_absolute_path"].endswith("/" + suffix)]
        if len(rows) != 1:
            raise AssertionError((source_map_path, suffix, len(rows)))
        path = ROOT / rows[0]["archive_relative_path"]
        if hashlib.sha256(path.read_bytes()).hexdigest() != rows[0]["sha256"]:
            raise AssertionError(f"archive hash mismatch: {path}")
        return path

    @staticmethod
    def independent_e1(source_map_path: Path, detector_ids: tuple[str, str] = (
            "mainline_merge_entry_e1_l0", "mainline_merge_entry_e1_l1")) -> dict[str, dict]:
        detector_rows: list[dict] = []
        for detector_id in detector_ids:
            path = IndependentReferenceArchiveChecks.archive_file(source_map_path, f"outputs/{detector_id}.xml")
            for node in ET.parse(path).getroot().iter("interval"):
                detector_rows.append({
                    "detector_id": detector_id,
                    "begin": float(node.get("begin")), "end": float(node.get("end")),
                    "n_entered": int(node.get("nVehEntered")),
                    "n_contrib": int(node.get("nVehContrib")),
                    "speed_mps": float(node.get("speed")),
                    "occupancy_percent": float(node.get("occupancy")),
                })
        combined = []
        for begin in range(0, 2700, 30):
            selected = [row for row in detector_rows if row["begin"] == begin and row["end"] == begin + 30]
            if len(selected) != 2 or len({row["detector_id"] for row in selected}) != 2:
                raise AssertionError(f"reference lane coverage failed at {begin}")
            contribution = sum(row["n_contrib"] for row in selected)
            combined.append({
                "begin": float(begin), "end": float(begin + 30),
                "q_vehph": sum(row["n_entered"] for row in selected) * 120.0,
                "speed_mps": (sum(row["speed_mps"] * row["n_contrib"] for row in selected)
                              / contribution if contribution else None),
                "occupancy_percent": sum(row["occupancy_percent"] for row in selected) / 2.0,
                "n_contrib": contribution,
            })
        return {"A": independent_aggregate(combined, 0.0, 1500.0),
                "B": independent_aggregate(combined, 300.0, 1500.0),
                "Post": independent_aggregate(combined, 1500.0, 2700.0),
                "Full": independent_aggregate(combined, 0.0, 2700.0)}

    @staticmethod
    def independent_r_count(source_map_path: Path) -> tuple[int, int]:
        path = IndependentReferenceArchiveChecks.archive_file(source_map_path, "outputs/fcd.xml")
        frames = 0
        previous: dict[str, tuple[float, str]] = {}
        first: dict[str, tuple[float, bool]] = {}
        for _, step in ET.iterparse(path, events=("end",)):
            if step.tag != "timestep":
                continue
            time_s = float(step.get("time"))
            identities: set[str] = set()
            for vehicle in step.findall(".//vehicle"):
                identity, lane = vehicle.get("id", ""), vehicle.get("lane", "")
                if identity in identities:
                    raise AssertionError(f"duplicate FCD identity at {time_s}: {identity}")
                identities.add(identity)
                if identity.startswith("R_flow.") and identity not in first and lane in {"main_down_0", "main_down_1"}:
                    prior = previous.get(identity)
                    first[identity] = (time_s, bool(prior and abs(time_s - prior[0] - 1.0) <= 1e-12))
                if identity.startswith("R_flow."):
                    previous[identity] = (time_s, lane)
            frames += 1
            step.clear()
        return sum(time_s < 1500 and bracketed for time_s, bracketed in first.values()), frames

    def test_four_reused_references_match_independent_raw_reconstruction(self) -> None:
        expected_r = {"C17": 36, "C23": 40, "MH17": 0, "MH23": 0}
        registry = json.loads((BATCH / "source_registry.json").read_text(encoding="utf-8"))
        records = {row["run_id"]: row for row in registry["runs"]}
        for run_id, expected_count in expected_r.items():
            with self.subTest(run_id=run_id):
                source_map = ROOT / records[run_id]["source_map_path"]
                aggregate = self.independent_e1(source_map)
                r_count, frame_count = self.independent_r_count(source_map)
                observed = json.loads((BATCH / "verification" / f"reference_{run_id}_revision_02" /
                                       "run_manifest.json").read_text(encoding="utf-8"))
                self.assertEqual(r_count, expected_count)
                self.assertEqual(frame_count, 2700)
                self.assertEqual(observed["r_passage"]["a_bracketed_event_count"], expected_count)
                self.assertEqual(len(observed["endpoints"]), 8)
                self.assertEqual(len({(row["class"], row["endpoint_s"]) for row in observed["endpoints"]}), 8)
                for window in ("A", "B"):
                    for key in ("q_vehph", "speed_mps", "occupancy_percent", "n_contrib"):
                        self.assertAlmostEqual(observed["e1"]["aggregates"][window][key],
                                               aggregate[window][key], places=12)


class IndependentSecondScientificRepairChecks(unittest.TestCase):
    @staticmethod
    def _canonical_hash(value: object) -> str:
        encoded = json.dumps(value, sort_keys=True, separators=(",", ":"),
                             allow_nan=False).encode("utf-8")
        return hashlib.sha256(encoded).hexdigest()

    @staticmethod
    def _episodes(times_by_key: dict[tuple, list[float]]) -> dict[tuple, tuple[int, int]]:
        result = {}
        for key, values in times_by_key.items():
            episode_count = 0
            previous = None
            for value in sorted(values):
                if previous is None or value - previous != 1.0:
                    episode_count += 1
                previous = value
            result[key] = (episode_count, len(values))
        return result

    @classmethod
    def independent_complete_observations(cls, source_map: Path, contract: dict) -> dict:
        lanes = contract["required_observations"]["lanes"]
        fcd = IndependentReferenceArchiveChecks.archive_file(source_map, "outputs/fcd.xml")
        stopped: defaultdict[tuple, list[float]] = defaultdict(list)
        positions: defaultdict[str, list[float]] = defaultdict(list)
        shared_times: defaultdict[str, set[float]] = defaultdict(set)
        first_r_region: dict[str, float] = {}
        labels: list[float] = []
        duplicates = unknown_ids = unknown_lanes = 0
        r_regions = {
            "ramp_accel", "ramp_mid_internal", "ramp_storage",
            "ramp_diverge_internal", "shared_approach",
        }
        for _, step in ET.iterparse(fcd, events=("end",)):
            if step.tag != "timestep":
                continue
            time_s = float(step.get("time"))
            labels.append(time_s)
            seen: set[str] = set()
            for vehicle in step.findall(".//vehicle"):
                identity = vehicle.get("id", "")
                lane_id = vehicle.get("lane", "")
                if identity in seen:
                    duplicates += 1
                seen.add(identity)
                prefix = identity.split("_flow.", 1)[0]
                if prefix not in {"M", "R", "U", "X"}:
                    unknown_ids += 1
                if lane_id not in lanes:
                    unknown_lanes += 1
                    continue
                if float(vehicle.get("speed")) > 0.1:
                    continue
                region = lanes[lane_id]["region"]
                stopped[(prefix, identity, region)].append(time_s)
                if prefix == "M":
                    positions[lane_id].append(float(vehicle.get("pos")))
                if prefix in {"R", "U"} and region == "shared_approach":
                    shared_times[prefix].add(time_s)
                if prefix == "R" and region in r_regions:
                    first_r_region.setdefault(region, time_s)
            step.clear()
        episodes = cls._episodes(stopped)
        shared = {
            kind: {
                "episode_count": sum(count for (prefix, _, region), (count, _) in episodes.items()
                                     if prefix == kind and region == "shared_approach"),
                "stopped_vehicle_seconds": float(sum(samples for (prefix, _, region), (_, samples)
                                                     in episodes.items()
                                                     if prefix == kind and region == "shared_approach")),
            }
            for kind in ("R", "U")
        }
        tls_path = IndependentReferenceArchiveChecks.archive_file(source_map, "outputs/tls_states.xml")
        tls_rows = []
        for node in ET.parse(tls_path).getroot().iter("tlsState"):
            if node.get("id") == "urban_tls":
                tls_rows.append((float(node.get("time")), node.get("state")))
        trip_path = IndependentReferenceArchiveChecks.archive_file(source_map, "outputs/tripinfo.xml")
        departs: defaultdict[str, list[float]] = defaultdict(list)
        for node in ET.parse(trip_path).getroot().iter("tripinfo"):
            if node.get("id", "").startswith("M_flow."):
                departs[node.get("departLane")].append(float(node.get("departPos")))
        m_ranges = []
        for lane_id, values in sorted(positions.items()):
            lane_length = lanes[lane_id]["length_m"]
            m_ranges.append({
                "lane_id": lane_id,
                "stopped_sample_count": len(values),
                "min_position_m": min(values),
                "max_position_m": max(values),
                "min_distance_to_lane_end_m": lane_length - max(values),
                "max_distance_to_lane_end_m": lane_length - min(values),
            })
        depart_ranges = [{
            "lane_id": lane_id,
            "vehicle_count": len(values),
            "min_depart_position_m": min(values),
            "max_depart_position_m": max(values),
        } for lane_id, values in sorted(departs.items())]
        demand_path = IndependentReferenceArchiveChecks.archive_file(source_map, "demand.rou.xml")
        planned = {}
        for node in ET.parse(demand_path).getroot().iter("flow"):
            prefix = node.get("id", "").split("_flow", 1)[0]
            if prefix in {"M", "R", "U", "X"}:
                planned[prefix] = planned.get(prefix, 0) + int(node.get("number"))
        ordered_regions = [name for name, _ in sorted(first_r_region.items(), key=lambda item: item[1])]
        return {
            "fcd": {
                "frame_count": len(labels),
                "labels": labels,
                "duplicates": duplicates,
                "unknown_ids": unknown_ids,
                "unknown_lanes": unknown_lanes,
            },
            "downstream_e1": IndependentReferenceArchiveChecks.independent_e1(
                source_map, ("merge_downstream_e1_l0", "merge_downstream_e1_l1")),
            "m_episode_count": sum(count for (prefix, _, _), (count, _) in episodes.items()
                                   if prefix == "M"),
            "m_sample_count": sum(samples for (prefix, _, _), (_, samples) in episodes.items()
                                  if prefix == "M"),
            "m_ranges": m_ranges,
            "depart_ranges": depart_ranges,
            "planned_demand_vehph": {key: value * 3600.0 / 1500.0
                                      for key, value in planned.items()},
            "r_order": ordered_regions,
            "shared": shared,
            "cooccurrence": len(shared_times["R"] & shared_times["U"]),
            "tls": {
                "label_count": len(tls_rows),
                "states": sorted({state for _, state in tls_rows}),
                "transition_count": sum(left[1] != right[1]
                                        for left, right in zip(tls_rows, tls_rows[1:])),
            },
        }

    def test_all_six_candidates_have_exact_same_seed_reference_bindings(self) -> None:
        contract = actual_contract()
        registry = json.loads((BATCH / "source_registry.json").read_text(encoding="utf-8"))
        ledger_value = json.loads((BATCH / "execution_ledger.json").read_text(encoding="utf-8"))
        by_registry = {row["run_id"]: row for row in registry["runs"]}
        by_ledger = {row["run_id"]: row for row in ledger_value["logical_runs"]}
        for candidate_id in production.TIER1_IDS + production.LOWER_IDS + production.UPPER_IDS:
            binding = contract["ejmi_reference_map"][candidate_id]
            seed = by_registry[candidate_id]["seed"]
            self.assertEqual(binding["candidate_seed"], seed)
            for side, prefix, q_main in (("lower", "C", 3200), ("upper", "MH", 3800)):
                expected_id = f"{prefix}{seed}"
                reference = binding[side]
                self.assertEqual((reference["run_id"], reference["seed"], reference["q_main"]),
                                 (expected_id, seed, q_main))
                self.assertEqual(reference["manifest_path"], by_registry[expected_id]["reference_manifest_path"])
                self.assertEqual(reference["source_map_path"], by_registry[expected_id]["source_map_path"])
                self.assertEqual(reference["source_map_sha256"], by_registry[expected_id]["source_map_sha256"])
                self.assertEqual(reference["source_map_sha256"], hashlib.sha256(
                    (ROOT / reference["source_map_path"]).read_bytes()).hexdigest())
                value = json.loads((ROOT / reference["manifest_path"]).read_text(encoding="utf-8"))
                self.assertEqual(reference["manifest_payload_sha256"], self._canonical_hash(value))
                self.assertEqual(reference["manifest_payload_sha256"],
                                 by_ledger[expected_id]["manifest_payload_sha256"])

    def test_final_decision_full_registered_state_space_matches_independent_oracle(self) -> None:
        states = tuple(itertools.product(
            ("clear_passage", "clear_exclusion", "unresolved"),
            ("positive", "not_identified", "unresolved"),
        ))

        def oracle(q_states: list[tuple[tuple[str, str], tuple[str, str]]]) -> str:
            consolidated = []
            for seed17, seed23 in q_states:
                if seed17 != seed23 or "unresolved" in seed17:
                    return "unresolved"
                consolidated.append(seed17)
            if ("clear_exclusion", "positive") in consolidated:
                return "unresolved"
            if ("clear_passage", "positive") in consolidated:
                return "supports_A_within_registered_points"
            if (len(consolidated) >= 2
                    and all(state[1] == "not_identified" for state in consolidated)):
                transition = next((i for i, state in enumerate(consolidated)
                                   if state[0] == "clear_exclusion"), None)
                if (transition is not None and transition > 0
                        and all(state[0] == "clear_passage" for state in consolidated[:transition])
                        and all(state[0] == "clear_exclusion" for state in consolidated[transition:])):
                    return "supports_B_pattern_within_registered_points"
            return "unresolved"

        for q_values in ((3500,), (3350, 3500), (3500, 3650)):
            for seed_states in itertools.product(states, repeat=2 * len(q_values)):
                rows = []
                grouped = []
                for index, q_main in enumerate(q_values):
                    pair = (seed_states[2 * index], seed_states[2 * index + 1])
                    grouped.append(pair)
                    for seed, state in zip((17, 23), pair):
                        row = manifest(f"QM{q_main}S{seed}", seed, q_main, 28.0, 8.0)
                        row["r_passage"]["status"], row["ejmi"]["status"] = state
                        rows.append(row)
                self.assertEqual(production.decide_final(rows)["action"], oracle(grouped))

    def test_four_reference_complete_observations_match_independent_xml_reconstruction(self) -> None:
        contract = actual_contract()
        registry = {row["run_id"]: row for row in json.loads(
            (BATCH / "source_registry.json").read_text(encoding="utf-8"))["runs"]}
        expected_r_order = [
            "ramp_accel", "ramp_mid_internal", "ramp_storage",
            "ramp_diverge_internal", "shared_approach",
        ]
        for run_id in production.REFERENCE_IDS:
            with self.subTest(run_id=run_id):
                source_map = ROOT / registry[run_id]["source_map_path"]
                independent = self.independent_complete_observations(source_map, contract)
                manifest_path = BATCH / "verification" / f"reference_{run_id}_revision_05" / "run_manifest.json"
                observed = json.loads(manifest_path.read_text(encoding="utf-8"))
                complete = observed["required_observations"]
                self.assertTrue(observed["technical_qualified"])
                self.assertEqual(complete["qualification"], {
                    "passed": True, "required_audit_items": 7, "passed_audit_items": 7})
                self.assertEqual(independent["fcd"]["frame_count"], 2700)
                self.assertEqual(independent["fcd"]["labels"], [float(value) for value in range(2700)])
                self.assertEqual((independent["fcd"]["duplicates"], independent["fcd"]["unknown_ids"],
                                  independent["fcd"]["unknown_lanes"]), (0, 0, 0))
                for window in ("A", "B", "Post", "Full"):
                    for key in ("q_vehph", "speed_mps", "occupancy_percent", "n_contrib"):
                        self.assertAlmostEqual(
                            complete["downstream_e1"]["aggregates"][window][key],
                            independent["downstream_e1"][window][key], places=12)
                full_m = [row for row in complete["m_stopped_episodes"]
                          if row["observation_domain"] == "Full"]
                self.assertEqual((len(full_m), sum(row["sample_count"] for row in full_m)),
                                 (independent["m_episode_count"], independent["m_sample_count"]))
                self.assertEqual(complete["m_stopped_position_range"], independent["m_ranges"])
                self.assertEqual(complete["m_depart_position_range"], independent["depart_ranges"])
                self.assertEqual(complete["planned_demand_vehph"], independent["planned_demand_vehph"])
                realized = {
                    row["class"]: row["entered"] * 3600.0 / 1500.0
                    for row in observed["endpoints"] if row["endpoint_s"] == 1500.0
                }
                self.assertEqual(complete["realized_entry_vehph_A"], realized)
                self.assertNotIn("actual_input_vehph", complete)
                self.assertEqual(complete["r_propagation"]["event_sets"]["observed_region_sequence"],
                                 expected_r_order)
                self.assertEqual(independent["r_order"], expected_r_order)
                self.assertEqual(complete["shared_r_u_stopped_exposure"]["by_class"], independent["shared"])
                self.assertEqual(complete["shared_r_u_stopped_exposure"]["cooccurrence_support_s"],
                                 independent["cooccurrence"])
                for key, value in independent["tls"].items():
                    self.assertEqual(complete["tls_context"][key], value)
                self.assertTrue(all(item["passed"] for item in
                                    complete["warning_coverage_audit"].values()))

    def test_detector_topology_source_and_binary_hashes_are_independently_bound(self) -> None:
        contract = actual_contract()
        observations = contract["required_observations"]
        source = ROOT / observations["scenario_add_semantics"]["source_path"]
        self.assertEqual(hashlib.sha256(source.read_bytes()).hexdigest(),
                         observations["scenario_add_semantics"]["source_sha256"])
        source_root = ET.parse(source).getroot()
        self.assertEqual({node.get("id") for node in source_root.findall("inductionLoop")},
                         set(observations["scenario_add_semantics"]["e1_ids"]))
        self.assertEqual({node.get("id") for node in source_root.findall("laneAreaDetector")},
                         set(observations["scenario_add_semantics"]["e2_ids"]))
        events = source_root.findall("timedEvent")
        self.assertEqual(len(events), 1)
        self.assertTrue(all(events[0].get(key) == value for key, value in
                            observations["scenario_add_semantics"]["tls_event"].items()))
        source_e1 = {node.get("id"): node for node in source_root.findall("inductionLoop")}
        for expected in observations["e1_detectors"]:
            node = source_e1[expected["detector_id"]]
            self.assertEqual(node.get("lane"), expected["lane_id"])
            self.assertAlmostEqual(float(node.get("pos")), expected["position_m"])
            self.assertAlmostEqual(float(node.get("period")), expected["period_s"])
        source_e2 = {node.get("id"): node for node in source_root.findall("laneAreaDetector")}
        for expected in observations["e2_detectors"]:
            node = source_e2[expected["detector_id"]]
            self.assertEqual(node.get("lane"), expected["lane_id"])
            self.assertAlmostEqual(float(node.get("pos")), expected["begin_pos_m"])
            self.assertAlmostEqual(float(node.get("endPos")), -0.1)
            self.assertAlmostEqual(float(node.get("period")), expected["period_s"])
        for name, path in production.SOURCE_PATHS.items():
            self.assertEqual(hashlib.sha256(path.read_bytes()).hexdigest(),
                             contract["source_code_hashes"][name])
        for name, path in production.BINARY_PATHS.items():
            self.assertEqual(hashlib.sha256(path.read_bytes()).hexdigest(),
                             contract["binary_hashes"][name])
        registry = {row["run_id"]: row for row in json.loads(
            (BATCH / "source_registry.json").read_text(encoding="utf-8"))["runs"]}
        for run_id in production.REFERENCE_IDS:
            source_map = ROOT / registry[run_id]["source_map_path"]
            network = IndependentReferenceArchiveChecks.archive_file(source_map, "network.net.xml")
            self.assertEqual(hashlib.sha256(network.read_bytes()).hexdigest(),
                             observations["compiled_topology"]["registered_reference_network_sha256"][run_id])
            network_root = ET.parse(network).getroot()
            lane_rows = {lane.get("id"): (edge.get("id"), float(lane.get("length")),
                                          float(lane.get("speed")))
                         for edge in network_root.findall("edge") for lane in edge.findall("lane")}
            lane_ids = set(lane_rows)
            self.assertEqual(lane_ids, set(observations["compiled_topology"]["required_lane_ids"]))
            for lane_id, expected in observations["lanes"].items():
                edge_id, length, speed = lane_rows[lane_id]
                self.assertEqual(edge_id, expected["edge_id"])
                self.assertAlmostEqual(length, expected["length_m"], places=2)
                self.assertAlmostEqual(speed, expected["speed_limit_mps"], places=2)

    def test_registered_budget_q_label_and_current_t43_state(self) -> None:
        payload = json.loads((BATCH / "registration_payload.json").read_text(encoding="utf-8"))
        ledger_value = json.loads((BATCH / "execution_ledger.json").read_text(encoding="utf-8"))
        self.assertEqual(payload["budget"]["regular_netconvert_operations_min"], 2)
        self.assertEqual(payload["budget"]["regular_netconvert_operations_max"], 4)
        self.assertEqual(payload["budget"]["hard_netconvert_operation_cap"], 5)
        self.assertIn("nVehEntered", payload["e1"]["q_rule"])
        self.assertIn("do not mix with Stage 3 nVehContrib", payload["required_observations"]["q_definition"]["warning"])
        self.assertEqual(
            ledger_value["t43_launch_authorization"]["quote"],
            "批准按 `docs/STAGE4_T43_LAUNCH_CONFIRMATION_PACKAGE.md` 执行 T43。",
        )
        self.assertEqual(ledger_value["t43_launch_authorization"]["status"], "user_approved")
        self.assertEqual(
            {field: ledger_value[field] for field in (
                "actual_sumo_starts", "actual_netconvert_operations",
                "actual_traci_connections", "actual_gui_starts")},
            {"actual_sumo_starts": 4, "actual_netconvert_operations": 4,
             "actual_traci_connections": 0, "actual_gui_starts": 0},
        )

    def test_deprecated_input_field_and_rate_mismatches_are_rejected(self) -> None:
        path = BATCH / "verification/reference_C17_revision_05/run_manifest.json"
        valid = json.loads(path.read_text(encoding="utf-8"))
        production._validate_candidate_observations(valid)
        deprecated = copy.deepcopy(valid)
        deprecated["required_observations"]["actual_input_vehph"] = deprecated[
            "required_observations"].pop("planned_demand_vehph")
        with self.assertRaisesRegex(ValueError, "deprecated ambiguous"):
            production._validate_candidate_observations(deprecated)
        for field in ("planned_demand_vehph", "realized_entry_vehph_A"):
            with self.subTest(field=field):
                changed = copy.deepcopy(valid)
                changed["required_observations"][field]["R"] += 2.4
                with self.assertRaisesRegex(ValueError, "plan or A-endpoint"):
                    production._validate_candidate_observations(changed)

    def test_entry_accounting_is_the_seventh_required_qualification_item(self) -> None:
        path = BATCH / "verification/reference_C17_revision_05/run_manifest.json"
        valid = json.loads(path.read_text(encoding="utf-8"))
        audit = valid["required_observations"]["warning_coverage_audit"]
        self.assertEqual(set(audit), {
            "fcd", "downstream_e1", "tls", "entry_accounting",
            "m_depart_position", "technical_warnings", "source_inventory",
        })
        changed = copy.deepcopy(valid)
        changed["required_observations"]["warning_coverage_audit"]["entry_accounting"]["passed"] = False
        with self.assertRaisesRegex(ValueError, "audit failed"):
            production._validate_candidate_observations(changed)


class IndependentTier2GateChecks(unittest.TestCase):
    """Independent checks of the immutable Tier-2 gate and prelaunch state."""

    @staticmethod
    def _load(name: str) -> dict:
        return json.loads((BATCH / name).read_text(encoding="utf-8"))

    @staticmethod
    def _sha(name: str) -> str:
        return hashlib.sha256((BATCH / name).read_bytes()).hexdigest()

    def test_exact_scientific_path_hash_and_relay_are_bound(self) -> None:
        ledger = self._load("execution_ledger.json")
        gate = self._load("tier2_branch_gate_registration.json")
        receipt = self._load("tier1_scientific_branch_review_receipt.json")
        expected_path = (
            "data/processed/stage4_qmain_sequential_20260912_v1/"
            "analysis/tier1/revision_05/decision/branch_decision.json"
        )
        self.assertEqual(gate["scientific_decision_path"], expected_path)
        self.assertEqual(receipt["decision_path"], expected_path)
        self.assertEqual(gate["scientific_decision_sha256"],
                         "e0fb31613c2af5375aa6d6148da7a9c67ef5efacde1c0e822b806b6bc2d54b91")
        self.assertEqual(receipt["decision_sha256"], gate["scientific_decision_sha256"])
        self.assertEqual(gate["scientific_review_receipt_sha256"],
                         self._sha("tier1_scientific_branch_review_receipt.json"))
        self.assertEqual(ledger["tier2_branch_gate"]["sha256"],
                         self._sha("tier2_branch_gate_registration.json"))
        self.assertEqual(gate["adapter_sha256_at_registration"],
                         hashlib.sha256(Path(production.__file__).read_bytes()).hexdigest())

    def test_engineering_smoke_is_identical_but_cannot_replace_scientific_path(self) -> None:
        ledger = self._load("execution_ledger.json")
        scientific = ROOT / production.TIER1_SCIENTIFIC_DECISION_RELATIVE_PATH
        smoke = BATCH / "verification/engineering_decision_cli_revision_01/branch_decision.json"
        self.assertEqual(smoke.read_bytes(), scientific.read_bytes())
        with self.assertRaisesRegex(ValueError, "cannot substitute"):
            production.validate_scientific_tier1_review_receipt(
                BATCH / "tier1_scientific_branch_review_receipt.json", smoke, ledger
            )

    def test_gate_has_exact_pair_commands_and_no_extra_branch(self) -> None:
        gate = self._load("tier2_branch_gate_registration.json")
        registry = self._load("source_registry.json")
        by_id = {row["run_id"]: row for row in registry["runs"]}
        self.assertEqual(gate["selected_run_ids"], ["QM3650S17", "QM3650S23"])
        self.assertEqual(gate["selected_seed_pair"], [17, 23])
        self.assertEqual(gate["selected_q_main"], 3650)
        self.assertEqual(gate["cancelled_run_ids"], ["QM3350S17", "QM3350S23"])
        self.assertTrue(gate["additional_qmain_points_or_seeds_prohibited"])
        expected = [{"run_id": run_id, "seed": by_id[run_id]["seed"],
                     "q_main": by_id[run_id]["q_main"],
                     "exact_runner_command_argv": by_id[run_id]["exact_runner_command_argv"]}
                    for run_id in ("QM3650S17", "QM3650S23")]
        self.assertEqual(gate["selected_run_contracts"], expected)

    def test_completed_tier2_state_has_exact_runtime_receipts_and_cancelled_lower_pair(self) -> None:
        ledger = self._load("execution_ledger.json")
        overlay = self._load("runtime_source_registry.json")
        receipts = self._load("candidate_manifest_receipt_registry.json")
        completed_ids = {"QM3500S17", "QM3500S23", "QM3650S17", "QM3650S23"}
        self.assertEqual({row["run_id"] for row in overlay["runs"]}, completed_ids)
        self.assertEqual({row["run_id"] for row in receipts["receipts"]}, completed_ids)
        by_id = {row["run_id"]: row for row in ledger["logical_runs"]}
        for run_id in ("QM3650S17", "QM3650S23"):
            self.assertEqual(by_id[run_id]["state"], "completed_valid")
            self.assertTrue(by_id[run_id]["terminal"])
            self.assertEqual(by_id[run_id]["attempt_ids"], [f"{run_id}_attempt1"])
            self.assertEqual(by_id[run_id]["actual_sumo_starts"], 1)
            self.assertTrue((BATCH / "source_maps" / f"{run_id}_attempt1.json").exists())
        self.assertEqual(len(ledger["attempts"]), 4)
        self.assertIsNone(ledger["execution_reservations"]["active_attempt_id"])

    def test_cancelled_lower_pair_is_terminal_and_cannot_carry_attempts(self) -> None:
        ledger = self._load("execution_ledger.json")
        registry = self._load("source_registry.json")
        by_id = {row["run_id"]: row for row in ledger["logical_runs"]}
        for run_id in ("QM3350S17", "QM3350S23"):
            self.assertEqual(by_id[run_id]["state"], "cancelled_by_stop_rule")
            self.assertTrue(by_id[run_id]["terminal"])
            self.assertEqual(by_id[run_id]["attempt_ids"], [])
            self.assertEqual(by_id[run_id]["actual_sumo_starts"], 0)
        changed = copy.deepcopy(ledger)
        next(row for row in changed["logical_runs"] if row["run_id"] == "QM3350S17")[
            "attempt_ids"] = ["forged"]
        with self.assertRaisesRegex(ValueError, "cancelled q3350"):
            production.validate_tier2_branch_gate(changed, registry)

    def test_gate_accepts_future_completed_upper_states_but_overlay_still_requires_facts(self) -> None:
        ledger = self._load("execution_ledger.json")
        registry = self._load("source_registry.json")
        for completed in (1, 2):
            changed = copy.deepcopy(ledger)
            by_id = {row["run_id"]: row for row in changed["logical_runs"]}
            upper_ids = ("QM3650S17", "QM3650S23")
            retained = set(upper_ids[:completed])
            changed["attempts"] = [row for row in changed["attempts"]
                                   if row["run_id"] not in set(upper_ids) - retained]
            changed["actual_sumo_starts"] = 2 + completed
            changed["actual_netconvert_operations"] = 2 + completed
            for run_id in set(upper_ids) - retained:
                row = by_id[run_id]
                row["state"] = "selected_pending_execution"
                row["terminal"] = False
                row["attempt_ids"] = []
                row["actual_sumo_starts"] = 0
                row.pop("source_map_path", None)
                row.pop("source_map_sha256", None)
                row.pop("technical_qualified", None)
            production.validate_tier2_branch_gate(changed, registry)
            overlay = self._load("runtime_source_registry.json")
            missing_run_id = upper_ids[completed - 1]
            overlay["runs"] = [row for row in overlay["runs"]
                               if row["run_id"] in set(production.TIER1_IDS) | retained
                               and row["run_id"] != missing_run_id]
            with tempfile.TemporaryDirectory(dir=BATCH / "verification") as directory:
                overlay_path = Path(directory) / "runtime_source_registry.json"
                overlay_path.write_text(json.dumps(overlay), encoding="utf-8")
                changed["runtime_source_registry_overlay"]["path"] = str(
                    overlay_path.relative_to(ROOT))
                changed["runtime_source_registry_overlay"]["sha256"] = hashlib.sha256(
                    overlay_path.read_bytes()).hexdigest()
                with self.assertRaisesRegex(ValueError, "absent"):
                    production.validate_runtime_source_registry(
                        overlay_path, changed, registry, missing_run_id)

    def test_existing_receipt_drift_is_detected_before_future_use(self) -> None:
        ledger = self._load("execution_ledger.json")
        registry = self._load("candidate_manifest_receipt_registry.json")
        manifests = [BATCH / "verification/engineering_overlay_cli_revision_02" / run_id /
                     "run_manifest.json" for run_id in ("QM3500S17", "QM3500S23")]
        with tempfile.TemporaryDirectory(dir=BATCH / "verification") as directory:
            changed_registry = copy.deepcopy(registry)
            changed_registry["receipts"][0]["manifest_file_sha256"] = "0" * 64
            path = Path(directory) / "registry.json"
            path.write_text(json.dumps(changed_registry), encoding="utf-8")
            changed_ledger = copy.deepcopy(ledger)
            changed_ledger["candidate_manifest_receipt_registry"]["path"] = path.relative_to(ROOT).as_posix()
            changed_ledger["candidate_manifest_receipt_registry"]["sha256"] = hashlib.sha256(
                path.read_bytes()).hexdigest()
            with self.assertRaises(ValueError):
                production.validate_candidate_manifest_receipt_registry(
                    path, changed_ledger, BATCH / "measurement_contract.json",
                    BATCH / "source_registry.json", manifests,
                )

    def test_single_mixed_extra_and_tampered_decisions_are_rejected(self) -> None:
        decision = self._load("analysis/tier1/revision_05/decision/branch_decision.json")
        mutations = []
        for field, value in (
            ("selected_tier2_runs", ["QM3650S17"]),
            ("selected_tier2_runs", ["QM3650S17", "QM3350S23"]),
            ("selected_tier2_runs", ["QM3650S17", "QM3650S23", "QM3700S17"]),
            ("action", "run_q3350"),
            ("ejmi_states", ["positive", "not_identified"]),
        ):
            changed = copy.deepcopy(decision); changed[field] = value; mutations.append(changed)
        for changed in mutations:
            with self.assertRaisesRegex(ValueError, "exact run_q3650"):
                production._validate_tier2_branch_decision_content(changed)


class IndependentFinalEvidenceSnapshotChecks(unittest.TestCase):
    snapshot_path = BATCH / "final_evidence_ledger_snapshot.json"
    snapshot_sha256 = "f589c905067887536037fe6fe045438e8a1588cbf3246dcc50b573facecb4516"

    @staticmethod
    def canonical_hash(value: object) -> str:
        encoded = json.dumps(
            value, sort_keys=True, separators=(",", ":"), ensure_ascii=False
        ).encode("utf-8")
        return hashlib.sha256(encoded).hexdigest()

    def test_snapshot_independently_rebuilds_all_execution_evidence_hashes(self) -> None:
        snapshot_bytes = self.snapshot_path.read_bytes()
        self.assertEqual(hashlib.sha256(snapshot_bytes).hexdigest(), self.snapshot_sha256)
        snapshot = json.loads(snapshot_bytes)
        frozen = snapshot["execution_ledger"]
        self.assertEqual(
            self.canonical_hash(frozen), snapshot["canonical_execution_ledger_sha256"]
        )
        self.assertEqual(
            [frozen[key] for key in (
                "actual_sumo_starts", "actual_netconvert_operations",
                "actual_traci_connections", "actual_gui_starts")],
            [4, 4, 0, 0],
        )
        self.assertEqual(len(frozen["attempts"]), 4)
        expected_runs = {"QM3500S17", "QM3500S23", "QM3650S17", "QM3650S23"}
        self.assertEqual({row["run_id"] for row in frozen["attempts"]}, expected_runs)

        external = snapshot["bound_external_evidence"]
        archive_files = 0
        for key in ("runtime_source_registry", "candidate_manifest_receipt_registry"):
            binding = external[key]
            path = ROOT / binding["path"]
            self.assertEqual(hashlib.sha256(path.read_bytes()).hexdigest(), binding["sha256"])
        runtime = json.loads((ROOT / external["runtime_source_registry"]["path"]).read_text())
        self.assertEqual({row["run_id"] for row in runtime["runs"]}, expected_runs)
        for row in runtime["runs"]:
            source_map_path = ROOT / row["source_map_path"]
            self.assertEqual(
                hashlib.sha256(source_map_path.read_bytes()).hexdigest(),
                row["source_map_sha256"],
            )
            source_map = json.loads(source_map_path.read_text())
            self.assertEqual(source_map["archive_file_count"], 29)
            self.assertEqual(len(source_map["file_map"]), 29)
            for item in source_map["file_map"]:
                archive = ROOT / item["archive_relative_path"]
                self.assertEqual(hashlib.sha256(archive.read_bytes()).hexdigest(), item["sha256"])
                self.assertEqual(archive.stat().st_size, item["size_bytes"])
                archive_files += 1
        self.assertEqual(archive_files, 116)

        receipts = json.loads(
            (ROOT / external["candidate_manifest_receipt_registry"]["path"]).read_text()
        )
        self.assertEqual({row["run_id"] for row in receipts["receipts"]}, expected_runs)
        for row in receipts["receipts"]:
            manifest = ROOT / row["manifest_path"]
            receipt = ROOT / row["receipt_path"]
            self.assertEqual(hashlib.sha256(manifest.read_bytes()).hexdigest(),
                             row["manifest_file_sha256"])
            self.assertEqual(hashlib.sha256(receipt.read_bytes()).hexdigest(),
                             row["receipt_file_sha256"])

    def test_snapshot_consumer_is_independent_of_future_mutable_ledger_metadata(self) -> None:
        before = self.snapshot_path.read_bytes()
        snapshot = json.loads(before)
        frozen_hash = self.canonical_hash(snapshot["execution_ledger"])
        current = json.loads((BATCH / "execution_ledger.json").read_text())
        current["future_review_metadata"] = {"receipt": "non-normative"}
        self.assertNotEqual(self.canonical_hash(current), frozen_hash)
        self.assertEqual(frozen_hash, snapshot["canonical_execution_ledger_sha256"])
        self.assertFalse(snapshot["consumer_contract"]["current_execution_ledger_is_normative"])
        self.assertFalse(snapshot["consumer_contract"]
                         ["post_snapshot_review_receipt_backlink_required_in_snapshot"])
        self.assertEqual(self.snapshot_path.read_bytes(), before)
        historical = snapshot["historical_unpreserved_ledger_binding"]
        self.assertFalse(historical["exact_immutable_ledger_snapshot_available"])
        artifact_hashes = {
            hashlib.sha256(path.read_bytes()).hexdigest()
            for path in BATCH.glob("*ledger*.json")
        }
        self.assertNotIn(historical["sha256"], artifact_hashes)


if __name__ == "__main__":
    unittest.main()

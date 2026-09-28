from __future__ import annotations

import importlib.util
import json
from pathlib import Path
import tempfile
import unittest
from unittest import mock

from scripts.stage6.minimal3199.minimal3199_adapter import ROOT, sha256, validate_pair

RUNNER_PATH = ROOT / "artifacts/stage6_ramp_induced_validation_20260922_v1/r02_single_start/runner.py"
PACKAGE = ROOT / "artifacts/stage6_minimal3199_ux0_r720_treatment_attempt1_20260924_rev2"
CARD_PATH = PACKAGE / "MINIMAL3199_R720_DELAYED_S17_UX0_ATTEMPT1_CARD_FINAL_REV2.json"

spec = importlib.util.spec_from_file_location("minimal3199_treatment_attempt_runner", RUNNER_PATH)
RUNNER = importlib.util.module_from_spec(spec)
spec.loader.exec_module(RUNNER)


class Minimal3199TreatmentAttemptTests(unittest.TestCase):
    def setUp(self):
        self.card = json.loads(CARD_PATH.read_text(encoding="utf-8"))
        self.card_hash = sha256(CARD_PATH)

    def test_exact_card_readonly_preflight_passes_but_review_gate_blocks_launch(self):
        plan = RUNNER.make_plan(ROOT, CARD_PATH, self.card_hash)
        self.assertEqual(plan["status"], "PREFLIGHT_PASS_NO_PROCESS_STARTED")
        self.assertFalse(plan["simulator_process_started"])
        self.assertTrue(plan["launch_authorized"])
        self.assertFalse(plan["launchable_now"])
        self.assertEqual(plan["launch_review_gate"]["status"], "WAITING_FOR_REQUIRED_REVIEWS")
        self.assertEqual(plan["guardian_request_validation"]["status"], "BLOCKED_BY_REVIEW_GATE")
        self.assertEqual(plan["persisted_start_request"]["status"], "PASS_UNSENT")
        self.assertFalse(plan["persisted_start_request"]["dispatched"])

    def test_runner_and_guardian_binding_is_exact_for_unique_attempt(self):
        binding = RUNNER.MINIMAL3199_RETRY_BINDINGS[self.card["run_id"]]
        self.assertEqual(self.card["run_id"], "MINIMAL3199_R720_DELAYED_S17_UX0_ATTEMPT1")
        self.assertEqual(self.card["runner_binding"]["kind"], "MINIMAL3199_UX0_TREATMENT_FINAL")
        self.assertEqual(self.card["runner_binding"]["card_path"], binding["card_path"])
        self.assertEqual(self.card["runner_binding"]["output_directory"], binding["output_directory"])
        self.assertEqual(self.card["runtime_binding"]["guardian_runner_sha256"], sha256(RUNNER_PATH))
        self.assertEqual(self.card["resource_limits"]["runtime_s"], 90)
        self.assertEqual(self.card["resource_limits"]["storage_bytes"], 75_000_000)

    def test_pre_materialized_m_list_is_100_percent_matched_and_r_is_only_extra_demand(self):
        source_root = ROOT / "scripts/stage6/minimal3199/prepared_rev3"
        manifest = json.loads((source_root / "INPUT_MANIFEST.json").read_text(encoding="utf-8"))
        control = source_root / "control/demand.rou.xml"
        treatment = source_root / "treatment/demand.rou.xml"
        result = validate_pair(control, treatment, manifest)
        self.assertEqual(result["m_count"], 1333)
        self.assertEqual(result["m_matches"], 1333)
        self.assertEqual(result["control_r_count"], 0)
        self.assertEqual(result["treatment_r_count"], 192)
        self.assertTrue(result["u_x_explicit_zero_both_arms"])

    def test_common_m_speedfactor_mismatch_fixture_fails_closed(self):
        source_root = ROOT / "scripts/stage6/minimal3199/prepared_rev3"
        manifest = json.loads((source_root / "INPUT_MANIFEST.json").read_text(encoding="utf-8"))
        control = source_root / "control/demand.rou.xml"
        treatment_text = (source_root / "treatment/demand.rou.xml").read_text(encoding="utf-8")
        original = 'speedFactor="0.9428"'
        self.assertIn('id="M_flow.0"', treatment_text)
        self.assertEqual(treatment_text.count(original), 1)
        with tempfile.TemporaryDirectory() as temporary:
            treatment_copy = Path(temporary) / "treatment.rou.xml"
            treatment_copy.write_text(treatment_text.replace(original, 'speedFactor="1.1000"', 1), encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "M identity/depart/route/type/speedFactor/depart parameters differ"):
                validate_pair(control, treatment_copy, manifest)

    def test_explicit_zero_ledger_and_matched_control_receipts_are_bound(self):
        manifest = json.loads((PACKAGE / "INPUT_MANIFEST.json").read_text(encoding="utf-8"))
        self.assertEqual(manifest["class_counts"]["control"]["U"], {"planned_count": 0, "status": "PASS_ZERO"})
        self.assertEqual(manifest["class_counts"]["control"]["X"], {"planned_count": 0, "status": "PASS_ZERO"})
        self.assertEqual(manifest["class_counts"]["treatment"]["U"], {"planned_count": 0, "status": "PASS_ZERO"})
        self.assertEqual(manifest["class_counts"]["treatment"]["X"], {"planned_count": 0, "status": "PASS_ZERO"})
        control = manifest["matched_control_binding"]
        self.assertEqual(control["run_id"], "MINIMAL3199_CTRL_S17_TECH_RETRY2")
        self.assertEqual(control["card_sha256"], RUNNER.MINIMAL3199_TREATMENT_ATTEMPT1_BINDING["matched_control_card_sha256"])
        self.assertEqual(control["scientific_review_sha256"], RUNNER.MINIMAL3199_TREATMENT_ATTEMPT1_BINDING["matched_control_scientific_review_sha256"])

    def test_guardian_request_rejects_missing_schema_before_any_dispatch(self):
        with self.assertRaisesRegex(RUNNER.GateError, "INVALID_START_REQUEST"):
            RUNNER.validate_guardian_start_request({}, ROOT)

    def test_exact_treatment_start_request_schema_passes_offline_with_exact_resource_binding(self):
        binding = RUNNER.MINIMAL3199_TREATMENT_ATTEMPT1_BINDING
        reservation = ROOT / binding["consumption_directory"] / f"{self.card['run_id']}.json"
        with mock.patch.object(
            RUNNER, "minimal3199_retry_final_review_gate",
            return_value={"status": "PASS", "reviews": {"test_only_mock": "PASS"}},
        ):
            card, files = RUNNER.verify_card(ROOT, CARD_PATH, self.card_hash, allow_prelaunch=True)
            plan = RUNNER.make_plan(ROOT, CARD_PATH, self.card_hash)
            start = RUNNER.prepare_minimal3199_guardian_start(
                ROOT, CARD_PATH, self.card_hash, card, files, files["output"], reservation
            )
            self.assertEqual(plan["status"], "PREFLIGHT_PASS_NO_PROCESS_STARTED")
            self.assertTrue(plan["launchable_now"])
            self.assertEqual(start["request_schema"], "r02-start-v2")
            self.assertEqual(start["max_runtime_s"], 90)
            self.assertEqual(start["max_output_bytes"], 75_000_000)
            self.assertEqual(
                RUNNER.validate_guardian_start_request(start, ROOT), binding
            )

    def test_guardian_start_request_rejects_treatment_resource_or_path_mutation(self):
        binding = RUNNER.MINIMAL3199_TREATMENT_ATTEMPT1_BINDING
        reservation = ROOT / binding["consumption_directory"] / f"{self.card['run_id']}.json"
        with mock.patch.object(
            RUNNER, "minimal3199_retry_final_review_gate",
            return_value={"status": "PASS", "reviews": {"test_only_mock": "PASS"}},
        ):
            card, files = RUNNER.verify_card(ROOT, CARD_PATH, self.card_hash, allow_prelaunch=True)
            start = RUNNER.prepare_minimal3199_guardian_start(
                ROOT, CARD_PATH, self.card_hash, card, files, files["output"], reservation
            )
        wrong_resource = dict(start, max_output_bytes=60_000_000)
        with self.assertRaisesRegex(RUNNER.GateError, "START_RESOURCE_BINDING_MISMATCH"):
            RUNNER.validate_guardian_start_request(wrong_resource, ROOT)
        wrong_path = dict(start, output_directory=str(ROOT / "data/raw/other"))
        with self.assertRaisesRegex(RUNNER.GateError, "START_PROVENANCE_BINDING_MISMATCH"):
            RUNNER.validate_guardian_start_request(wrong_path, ROOT)

    def test_review_receipts_are_not_yet_hash_bound(self):
        gate = RUNNER.minimal3199_retry_final_review_gate(ROOT, self.card_hash, self.card["run_id"])
        self.assertEqual(gate["status"], "WAITING_FOR_REQUIRED_REVIEWS")
        self.assertEqual(gate["reviews"]["engineering"]["status"], "PASS")
        self.assertEqual(gate["reviews"]["data_provenance"]["status"], "MISSING")
        self.assertEqual(gate["reviews"]["scientific"]["status"], "MISSING")

    def test_rev2_request_is_non_circular_and_rev1_artifacts_are_preserved(self):
        old_package = ROOT / "artifacts/stage6_minimal3199_ux0_r720_treatment_attempt1_20260924_v1"
        self.assertTrue((old_package / "MINIMAL3199_R720_DELAYED_S17_UX0_ATTEMPT1_CARD_FINAL.json").is_file())
        self.assertEqual(self.card["card_revision"], 2)
        self.assertNotIn("request_sha256", self.card["guardian_request_binding"])
        request_path = ROOT / self.card["guardian_request_binding"]["request_path"]
        receipt_path = ROOT / self.card["guardian_request_binding"]["receipt_path"]
        request_bytes = request_path.read_bytes()
        receipt = json.loads(receipt_path.read_text(encoding="utf-8"))
        self.assertEqual(receipt["card_sha256"], self.card_hash)
        self.assertEqual(receipt["request_sha256"], sha256(request_path))
        self.assertEqual(receipt["request_bytes"], len(request_bytes))
        self.assertFalse(receipt["dispatched"])

    def test_preflight_rejects_mutated_persisted_request_and_receipt(self):
        binding = RUNNER.MINIMAL3199_TREATMENT_ATTEMPT1_BINDING
        request_path = ROOT / binding["start_request_path"]
        receipt_path = ROOT / binding["start_request_receipt_path"]
        original_request = request_path.read_bytes()
        original_receipt = receipt_path.read_bytes()
        try:
            request_path.write_bytes(original_request + b" ")
            with self.assertRaisesRegex(RUNNER.GateError, "PERSISTED_START_REQUEST_CONTENT_MISMATCH"):
                RUNNER.make_plan(ROOT, CARD_PATH, self.card_hash)
            request_path.write_bytes(original_request)
            receipt = json.loads(original_receipt.decode("utf-8"))
            receipt["request_sha256"] = "0" * 64
            receipt_path.write_text(json.dumps(receipt, sort_keys=True) + "\n", encoding="utf-8")
            with self.assertRaisesRegex(RUNNER.GateError, "PERSISTED_START_REQUEST_RECEIPT_MISMATCH"):
                RUNNER.make_plan(ROOT, CARD_PATH, self.card_hash)
        finally:
            request_path.write_bytes(original_request)
            receipt_path.write_bytes(original_receipt)


if __name__ == "__main__":
    unittest.main()

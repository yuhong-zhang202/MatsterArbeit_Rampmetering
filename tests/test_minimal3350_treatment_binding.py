from __future__ import annotations

import importlib.util
import json
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
PACKAGE = ROOT / "artifacts/stage6_minimal3350_r720_treatment_preparation_20260924_rev3"
RUNNER_PATH = PACKAGE / "r02_single_start/runner.py"
RUN_ID = "MINIMAL3350_R720_DELAYED_S17"
CARD_PATH = PACKAGE / f"{RUN_ID}_CARD_REV1.json"

spec = importlib.util.spec_from_file_location("minimal3350_treatment_runner_tests", RUNNER_PATH)
runner = importlib.util.module_from_spec(spec)
assert spec and spec.loader
spec.loader.exec_module(runner)


class Minimal3350TreatmentBindingTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.card = json.loads(CARD_PATH.read_text(encoding="utf-8"))
        cls.card_hash = runner.sha256_file(CARD_PATH)

    def test_exact_card_static_preflight_passes_but_stays_review_gated(self):
        result = runner.make_plan(ROOT, CARD_PATH, self.card_hash)
        self.assertEqual(result["status"], "PREFLIGHT_PASS_NO_PROCESS_STARTED")
        self.assertFalse(result["launchable_now"])
        self.assertFalse(result["simulator_process_started"])
        self.assertEqual(result["launch_review_gate"]["status"], "WAITING_FOR_REQUIRED_REVIEWS")

    def test_treatment_binding_is_exact_and_separate_from_control(self):
        binding = runner.MINIMAL3350_TREATMENT_BINDING
        self.assertEqual(binding["run_id"] if "run_id" in binding else RUN_ID, RUN_ID)
        self.assertEqual(binding["authorized_wallclock_s"], 90)
        self.assertEqual(binding["authorized_output_bytes"], 75_000_000)
        self.assertNotEqual(binding["output_directory"], runner.MINIMAL3350_CONTROL_BINDING["output_directory"])
        self.assertEqual(self.card["runner_binding"]["card_path"], binding["card_path"])
        self.assertFalse((ROOT / binding["output_directory"]).exists())
        self.assertFalse((ROOT / binding["consumption_directory"] / f"{RUN_ID}.json").exists())

    def test_persisted_start_request_validates_offline_without_review_release(self):
        request_path = PACKAGE / "START_REQUEST.json"
        request = json.loads(request_path.read_text(encoding="utf-8"))
        result = runner.validate_guardian_start_request(request, ROOT, require_reviews=False)
        self.assertEqual(result["kind"], "PAIR_RUN")
        self.assertEqual(request["run_id"], RUN_ID)
        self.assertEqual(request["max_runtime_s"], 90)
        self.assertEqual(request["max_output_bytes"], 75_000_000)

    def test_guardian_request_fails_closed_on_run_id_or_limit_change(self):
        request = json.loads((PACKAGE / "START_REQUEST.json").read_text(encoding="utf-8"))
        request["run_id"] = "MINIMAL3350_CTRL_S17"
        with self.assertRaises(runner.GateError):
            runner.validate_guardian_start_request(request, ROOT, require_reviews=False)
        request = json.loads((PACKAGE / "START_REQUEST.json").read_text(encoding="utf-8"))
        request["max_output_bytes"] = 60_000_000
        with self.assertRaises(runner.GateError):
            runner.validate_guardian_start_request(request, ROOT, require_reviews=False)

    def test_exact_receipt_schema_and_card_hash_required(self):
        good = {"schema":"stage6_minimal3350_treatment_engineering_prelaunch_review_v1",
                "run_id":RUN_ID,"card_sha256":self.card_hash,"status":"PASS_PRELAUNCH",
                "findings":{"blocker":0,"major":0,"required_minor":0}}
        self.assertTrue(runner.minimal3350_review_receipt_valid("engineering", good, RUN_ID, self.card_hash))
        for mutate in (
            lambda d: d.update(run_id="MINIMAL3350_CTRL_S17"),
            lambda d: d.update(card_sha256="0"*64),
            lambda d: d.update(status="PASS"),
            lambda d: d["findings"].update(required_minor=1),
            lambda d: d.update(schema="stage6_engineering_prelaunch_review_v1"),
        ):
            bad=json.loads(json.dumps(good)); mutate(bad)
            self.assertFalse(runner.minimal3350_review_receipt_valid("engineering", bad, RUN_ID, self.card_hash))

    def test_control_postrun_science_receipt_is_hash_bound_into_treatment_card(self):
        matched = self.card["matched_control_binding"]
        review = ROOT / matched["scientific_review_path"]
        self.assertEqual(runner.sha256_file(review), matched["scientific_review_sha256"])
        value = json.loads(review.read_text(encoding="utf-8"))
        self.assertEqual(value["disposition"], "LOW_R_BACKGROUND_ACCEPTABLE")
        self.assertEqual(value["card_sha256"], matched["card_sha256"])


if __name__ == "__main__":
    unittest.main()

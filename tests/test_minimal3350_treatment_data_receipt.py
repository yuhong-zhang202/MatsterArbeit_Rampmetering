import copy
import hashlib
import importlib.util
import json
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
PACKAGE = ROOT / "artifacts/stage6_minimal3350_r720_treatment_preparation_20260924_rev7"
RUN_ID = "MINIMAL3350_R720_DELAYED_S17"
SPEC = importlib.util.spec_from_file_location("minimal3350_rev7_runner_data_receipt_test",
                                               PACKAGE / "r02_single_start/runner.py")
runner = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(runner)


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def build_rev7_receipt():
    source = ROOT / "artifacts/stage6_minimal3350_r720_treatment_preparation_20260924_rev6/DATA_PROVENANCE_PRELAUNCH_REVIEW.json"
    receipt = json.loads(source.read_text())
    receipt["package_id"] = PACKAGE.name
    card_path = f"artifacts/{PACKAGE.name}/{RUN_ID}_CARD_REV1.json"
    receipt["bindings"].update({
        "card_path": card_path,
        "card_sha256": sha(ROOT / card_path),
        "input_manifest_sha256": sha(PACKAGE / "INPUT_MANIFEST.json"),
        "runtime_binding_sha256": sha(PACKAGE / "runtime_binding.json"),
        "runner_sha256": sha(PACKAGE / "r02_single_start/runner.py"),
        "start_request_sha256": sha(PACKAGE / "START_REQUEST.json"),
        "start_request_receipt_sha256": sha(PACKAGE / "START_REQUEST_RECEIPT.json"),
        "provenance_receipt_sha256": sha(PACKAGE / "PROVENANCE_RECEIPT.json"),
    })
    return receipt


class Minimal3350TreatmentDataReceiptTests(unittest.TestCase):
    def setUp(self):
        self.receipt = build_rev7_receipt()
        self.card_sha = sha(PACKAGE / f"{RUN_ID}_CARD_REV1.json")

    def validate(self):
        return runner.minimal3350_treatment_data_receipt_valid(ROOT, self.receipt,
                                                              RUN_ID, self.card_sha)

    def test_nested_hash_bound_data_receipt_is_accepted(self):
        self.assertTrue(self.validate())

    def test_missing_or_wrong_nested_card_path_or_hash_is_rejected(self):
        self.receipt["bindings"].pop("card_sha256")
        self.assertFalse(self.validate())
        self.receipt = build_rev7_receipt()
        self.receipt["bindings"]["card_path"] = "artifacts/wrong/card.json"
        self.assertFalse(self.validate())
        self.receipt = build_rev7_receipt()
        self.receipt["bindings"]["card_sha256"] = "0" * 64
        self.assertFalse(self.validate())

    def test_wrong_manifest_runtime_runner_request_or_provenance_hash_is_rejected(self):
        for key in ("input_manifest_sha256", "runtime_binding_sha256", "runner_sha256",
                    "start_request_sha256", "start_request_receipt_sha256",
                    "provenance_receipt_sha256"):
            with self.subTest(key=key):
                self.receipt = build_rev7_receipt()
                self.receipt["bindings"][key] = "0" * 64
                self.assertFalse(self.validate())

    def test_wrong_status_run_id_findings_or_control_gate_is_rejected(self):
        self.receipt["status"] = "PASS"
        self.assertFalse(self.validate())
        self.receipt = build_rev7_receipt()
        self.receipt["run_id"] = "OTHER_RUN"
        self.assertFalse(self.validate())
        self.receipt = build_rev7_receipt()
        self.receipt["findings"]["required_minor"] = 1
        self.assertFalse(self.validate())
        self.receipt = build_rev7_receipt()
        self.receipt["matched_control_gate"]["scientific_disposition"] = "LOW_R_SELF_CONGESTED"
        self.assertFalse(self.validate())

    def test_missing_receipt_or_nested_binding_is_rejected(self):
        self.assertFalse(runner.minimal3350_treatment_data_receipt_valid(ROOT, None,
                          RUN_ID, self.card_sha))
        self.receipt.pop("bindings")
        self.assertFalse(self.validate())


if __name__ == "__main__":
    unittest.main()

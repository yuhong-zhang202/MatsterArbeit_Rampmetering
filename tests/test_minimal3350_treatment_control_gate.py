import copy
import hashlib
import importlib.util
import json
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
PACKAGE = ROOT / "artifacts/stage6_minimal3350_r720_treatment_preparation_20260924_rev6"
RUNNER_PATH = PACKAGE / "r02_single_start/runner.py"
CARD = json.loads((PACKAGE / "MINIMAL3350_R720_DELAYED_S17_CARD_REV1.json").read_text())
SPEC = importlib.util.spec_from_file_location("minimal3350_rev5_runner_test", RUNNER_PATH)
runner = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(runner)


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


class Minimal3350TreatmentControlGateTests(unittest.TestCase):
    def setUp(self):
        self.card = copy.deepcopy(CARD)
        self.binding = copy.deepcopy(self.card["matched_control_binding"])
        self.control_card = json.loads((ROOT / self.binding["card_path"]).read_text())
        self.data_review = json.loads((ROOT / self.binding["data_review_path"]).read_text())
        self.science_review = json.loads((ROOT / self.binding["scientific_review_path"]).read_text())
        self.output_manifest = json.loads((ROOT / self.binding["output_manifest_path"]).read_text())
        self.hashes = {
            "card": sha(ROOT / self.binding["card_path"]),
            "data_review": sha(ROOT / self.binding["data_review_path"]),
            "science_review": sha(ROOT / self.binding["scientific_review_path"]),
            "output_manifest": sha(ROOT / self.binding["output_manifest_path"]),
        }

    def validate(self):
        return runner.validate_minimal3350_control_release_receipts(
            self.card, self.binding, self.control_card, self.data_review,
            self.science_review, self.output_manifest, self.hashes)

    def test_exact_low_r_control_receipts_are_accepted(self):
        self.validate()
        self.assertTrue(self.card["stage6_exploratory_control_disposition_required_for_release"])
        self.assertEqual(self.card["stage6_exploratory_control_disposition_required"],
                         "LOW_R_BACKGROUND_ACCEPTABLE")
        self.assertFalse(self.card["legacy_clean_high_mobility_screen_required_for_release"])
        self.assertNotIn("LOW_R_BACKGROUND_ACCEPTABLE_required_for_release", self.card)

    def test_missing_or_false_exploratory_control_prerequisite_is_rejected(self):
        self.card.pop("stage6_exploratory_control_disposition_required_for_release")
        with self.assertRaises(runner.GateError):
            self.validate()
        self.card["stage6_exploratory_control_disposition_required_for_release"] = False
        with self.assertRaises(runner.GateError):
            self.validate()

    def test_missing_or_mismatched_control_binding_is_rejected(self):
        self.binding.pop("scientific_review_sha256")
        with self.assertRaises(runner.GateError):
            self.validate()

    def test_missing_control_review_receipt_is_rejected(self):
        self.science_review = None
        with self.assertRaises(runner.GateError):
            self.validate()
        self.science_review = json.loads((ROOT / self.binding["scientific_review_path"]).read_text())
        self.data_review = None
        with self.assertRaises(runner.GateError):
            self.validate()
        self.binding = copy.deepcopy(CARD["matched_control_binding"])
        self.binding["card_sha256"] = "0" * 64
        with self.assertRaises(runner.GateError):
            self.validate()

    def test_wrong_control_category_or_nonzero_findings_is_rejected(self):
        self.science_review["disposition"] = "LOW_R_SELF_CONGESTED"
        with self.assertRaises(runner.GateError):
            self.validate()
        self.science_review["disposition"] = "LOW_R_BACKGROUND_ACCEPTABLE"
        self.science_review["findings"]["major"] = 1
        with self.assertRaises(runner.GateError):
            self.validate()

    def test_wrong_control_identity_or_receipt_card_hash_is_rejected(self):
        self.science_review["run_id"] = "OTHER_CONTROL"
        with self.assertRaises(runner.GateError):
            self.validate()
        self.science_review["run_id"] = "MINIMAL3350_CTRL_S17"
        self.data_review["card_sha256"] = "0" * 64
        with self.assertRaises(runner.GateError):
            self.validate()


if __name__ == "__main__":
    unittest.main()

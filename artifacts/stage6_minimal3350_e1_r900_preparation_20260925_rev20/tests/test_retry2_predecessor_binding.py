from __future__ import annotations

import importlib.util
import json
import hashlib
from pathlib import Path
import shutil
import sys
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[3]
PKG = ROOT / "artifacts/stage6_minimal3350_e1_r900_preparation_20260925_rev20"
RUNNER_PATH = PKG / "r02_single_start/runner.py"
sys.path.insert(0, str(RUNNER_PATH.parent))
spec = importlib.util.spec_from_file_location("rev20_retry3_runner", RUNNER_PATH)
RUNNER = importlib.util.module_from_spec(spec)
assert spec and spec.loader
sys.modules[spec.name] = RUNNER
spec.loader.exec_module(RUNNER)

SOURCE = ROOT / "artifacts/stage6_minimal3350_e1_r900_preparation_20260925_rev19"
SOURCE_FILES = {
    RUNNER.MINIMAL3350_RETRY2_CARD_PATH: SOURCE / "MINIMAL3350_E1_R900_DELAYED_S17_TECH_RETRY2_CARD_FINAL_REV1.json",
    RUNNER.MINIMAL3350_RETRY2_RESERVATION_PATH: SOURCE / "r02_single_start/consumption/MINIMAL3350_E1_R900_DELAYED_S17_TECH_RETRY2.json",
    RUNNER.MINIMAL3350_RETRY2_FAILURE_PATH: SOURCE / "TECH_RETRY2_FAILURE_DISPOSITION.json",
}


def retry3_card() -> dict:
    return {
        "run_id": RUNNER.MINIMAL3350_TREATMENT_RUN_ID,
        "retry_context": {
            "type": "INDEPENDENT_TECHNICAL_RETRY",
            "retry_of_run_id": "MINIMAL3350_E1_R900_DELAYED_S17_TECH_RETRY2",
            "retry_of_card_sha256": RUNNER.MINIMAL3350_RETRY2_CARD_SHA256,
            "retry_of_reservation_sha256": RUNNER.MINIMAL3350_RETRY2_RESERVATION_SHA256,
            "retry_of_failure_disposition_path": RUNNER.MINIMAL3350_RETRY2_FAILURE_PATH,
            "retry_of_failure_disposition_sha256": RUNNER.MINIMAL3350_RETRY2_FAILURE_SHA256,
            "scientific_condition_unchanged": True,
        },
    }


class Retry2PredecessorBindingTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.repo = Path(self.temp.name)
        for rel, src in SOURCE_FILES.items():
            dst = self.repo / rel
            dst.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(src, dst)

    def tearDown(self):
        self.temp.cleanup()

    def test_accepts_exact_failed_retry2_predecessor_and_disposition(self):
        RUNNER.validate_minimal3350_retry2_predecessor(self.repo, retry3_card())

    def test_rejects_altered_or_missing_reservation(self):
        path = self.repo / RUNNER.MINIMAL3350_RETRY2_RESERVATION_PATH
        original = path.read_bytes()
        path.write_bytes(original + b" ")
        with self.assertRaisesRegex(RUNNER.GateError, "PREDECESSOR_HASH_MISMATCH"):
            RUNNER.validate_minimal3350_retry2_predecessor(self.repo, retry3_card())
        path.unlink()
        with self.assertRaises((RUNNER.GateError, FileNotFoundError)):
            RUNNER.validate_minimal3350_retry2_predecessor(self.repo, retry3_card())

    def test_rejects_missing_or_altered_failure_disposition(self):
        path = self.repo / RUNNER.MINIMAL3350_RETRY2_FAILURE_PATH
        original = path.read_bytes()
        path.unlink()
        with self.assertRaises((RUNNER.GateError, FileNotFoundError)):
            RUNNER.validate_minimal3350_retry2_predecessor(self.repo, retry3_card())
        path.write_bytes(original + b" ")
        with self.assertRaisesRegex(RUNNER.GateError, "PREDECESSOR_HASH_MISMATCH"):
            RUNNER.validate_minimal3350_retry2_predecessor(self.repo, retry3_card())

    def test_rejects_wrong_card_or_reservation_hash_in_retry_context(self):
        for key in ("retry_of_card_sha256", "retry_of_reservation_sha256"):
            card = retry3_card()
            card["retry_context"][key] = "0" * 64
            with self.subTest(key=key), self.assertRaisesRegex(
                    RUNNER.GateError, "PARENT_BINDING_MISMATCH"):
                RUNNER.validate_minimal3350_retry2_predecessor(self.repo, card)

    def test_rejects_failure_receipt_with_wrong_status_or_launch_counts(self):
        path = self.repo / RUNNER.MINIMAL3350_RETRY2_FAILURE_PATH
        receipt = json.loads(path.read_text())
        for key, value in (("status", "PASS"), ("sumo_starts", 1), ("retry_allowed", True)):
            changed = dict(receipt)
            changed[key] = value
            path.write_text(json.dumps(changed, sort_keys=True))
            card = retry3_card()
            forged_digest = hashlib.sha256(path.read_bytes()).hexdigest()
            card["retry_context"]["retry_of_failure_disposition_sha256"] = forged_digest
            with self.subTest(key=key), patch.object(
                    RUNNER, "MINIMAL3350_RETRY2_FAILURE_SHA256", forged_digest), self.assertRaisesRegex(
                    RUNNER.GateError, "FAILURE_DISPOSITION_INVALID"):
                RUNNER.validate_minimal3350_retry2_predecessor(self.repo, card)
        path.write_text(json.dumps(receipt, sort_keys=True))

    def test_rejects_execution_receipt_even_when_predecessor_receipt_is_valid(self):
        execution = self.repo / RUNNER.MINIMAL3350_RETRY2_EXECUTION_PATH
        execution.parent.mkdir(parents=True, exist_ok=True)
        execution.write_text("{}")
        with self.assertRaisesRegex(RUNNER.GateError, "PREDECESSOR_NOT_CLOSED"):
            RUNNER.validate_minimal3350_retry2_predecessor(self.repo, retry3_card())


if __name__ == "__main__":
    unittest.main()

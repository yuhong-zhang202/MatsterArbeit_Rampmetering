from __future__ import annotations

import importlib.util
import json
from pathlib import Path
import unittest

from scripts.stage6.minimal3199.minimal3199_adapter import ROOT, sha256

RUNNER_PATH = ROOT / "artifacts/stage6_ramp_induced_validation_20260922_v1/r02_single_start/runner.py"
CARD_PATH = ROOT / "artifacts/stage6_minimal3199_ctrl_execution_20260924_v1/MINIMAL3199_CTRL_S17_CARD_FINAL.json"
DRAFT_PATH = ROOT / "scripts/stage6/minimal3199/prepared_rev3/MINIMAL3199_CTRL_S17_CARD_DRAFT_NOT_AUTHORIZED_REV3.json"

_spec = importlib.util.spec_from_file_location("minimal3199_final_execution_runner", RUNNER_PATH)
RUNNER = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(RUNNER)


class Minimal3199FinalExecutionTests(unittest.TestCase):
    def test_historical_final_card_is_rejected_after_runner_revision(self):
        card = json.loads(CARD_PATH.read_text(encoding="utf-8"))
        self.assertEqual(card["run_id"], "MINIMAL3199_CTRL_S17")
        self.assertEqual(card["card_status"], "FINAL_AUTHORIZED_FOR_ONE_START")
        with self.assertRaisesRegex(RUNNER.GateError, "RUNNER_MANIFEST_HASH_MISMATCH"):
            RUNNER.make_plan(ROOT, CARD_PATH, sha256(CARD_PATH))

    def test_final_control_card_hash_is_exact(self):
        with self.assertRaisesRegex(RUNNER.GateError, "APPROVED_CARD_HASH_MISMATCH"):
            RUNNER.make_plan(ROOT, CARD_PATH, "0" * 64)

    def test_superseded_draft_cannot_launch(self):
        card = json.loads(DRAFT_PATH.read_text(encoding="utf-8"))
        with self.assertRaisesRegex(RUNNER.GateError, "CARD_NOT_EXACTLY_AUTHORIZED"):
            RUNNER.verify_card(ROOT, DRAFT_PATH, sha256(DRAFT_PATH), allow_prelaunch=False)
        self.assertEqual(card["card_status"], "DRAFT_NOT_AUTHORIZED")
        self.assertIsNone(card["run_command"])

    def test_failed_historical_raw_and_consumption_are_preserved(self):
        card = json.loads(CARD_PATH.read_text(encoding="utf-8"))
        output = ROOT / card["output_directory"]
        self.assertEqual({path.name for path in output.iterdir()},
                         {"scenario_control.add.xml", "scenario_control.sumocfg"})
        self.assertEqual(sha256(output / "scenario_control.add.xml"),
                         card["input_sha256"]["additional"])
        self.assertEqual(sha256(output / "scenario_control.sumocfg"),
                         "0a016bea72ef30815226bd8677dbdd86803796523c481e476a6e47f577457c49")
        consumption = (ROOT / card["runner_binding"]["consumption_directory"]
                       / "MINIMAL3199_CTRL_S17.json")
        record = json.loads(consumption.read_text(encoding="utf-8"))
        self.assertEqual(record["status"], "FAILED")
        self.assertEqual(record["failure"], "KeyError:'additional_schema'")
        self.assertIsNone(record["simulator_pid"])
        self.assertFalse(record["retry_allowed"])


if __name__ == "__main__":
    unittest.main()

from __future__ import annotations

import hashlib
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[3]
PKG = ROOT / "artifacts/stage6_minimal3350_e1_r900_preparation_20260925_rev17"
CARD = json.loads((PKG / "MINIMAL3350_E1_R900_DELAYED_S17_CARD_FINAL_REV1.json").read_text())
CARD_SHA = hashlib.sha256((PKG / "MINIMAL3350_E1_R900_DELAYED_S17_CARD_FINAL_REV1.json").read_bytes()).hexdigest()

def module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec and spec.loader
    result = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(result)
    return result

ADAPTER = module("e1_adapter_under_test", PKG / "minimal3350_e1_r900_adapter.py")
RUNNER = module("e1_runner_under_test", PKG / "r02_single_start/runner.py")

def validation_args(demand: Path):
    return (CARD, demand, ROOT / CARD["common_m_manifest"]["path"],
            ROOT / CARD["r_vehicle_source"]["path"], ROOT,
            ROOT / CARD["matched_control_binding"]["demand_input_path"])

class E1R900PreflightTests(unittest.TestCase):
    def test_exact_m_and_r900_schedule(self):
        got = ADAPTER.validate_treatment_card(*validation_args(PKG / "inputs/treatment/demand.rou.xml"))
        self.assertEqual(got["m_count"], 1396)
        self.assertEqual(got["r_count"], 240)
        self.assertEqual(got["r_schedule_ms"], [540000, 1496000, 4000])

    def _assert_demand_rejected(self, mutate):
        with tempfile.TemporaryDirectory() as td:
            bad = Path(td) / "demand.rou.xml"
            tree = ET.parse(PKG / "inputs/treatment/demand.rou.xml")
            mutate(tree.getroot())
            tree.write(bad, encoding="utf-8", xml_declaration=True)
            with self.assertRaises(ValueError):
                ADAPTER.validate_treatment_card(*validation_args(bad))

    def test_reject_depart_at_exclusive_1500s_endpoint(self):
        self._assert_demand_rejected(lambda root: next(x for x in root if x.get("id") == "R_flow.239").set("depart", "1500.000"))

    def test_reject_missing_last_r_identity(self):
        self._assert_demand_rejected(lambda root: root.remove(next(x for x in root if x.get("id") == "R_flow.239")))

    def test_original_design_and_escalation_plan_hashes_are_separate(self):
        manifest = json.loads((PKG / "INPUT_MANIFEST.json").read_text())
        self.assertEqual(manifest["design_plan_sha256"], CARD["design_sha256"])
        self.assertEqual(hashlib.sha256((ROOT / CARD["design_plan"]).read_bytes()).hexdigest(), CARD["design_sha256"])
        self.assertEqual(manifest["escalation_plan_sha256"], CARD["escalation_plan"]["sha256"])
        self.assertEqual(hashlib.sha256((ROOT / CARD["escalation_plan"]["path"]).read_bytes()).hexdigest(), manifest["escalation_plan_sha256"])

    def test_review_schema_is_exact_and_wrong_schema_fails_closed(self):
        receipt = {"schema": "stage6_minimal3350_treatment_engineering_prelaunch_review_v1",
                   "status": "PASS_PRELAUNCH", "run_id": CARD["run_id"],
                   "card_sha256": CARD_SHA,
                   "findings": {"blocker": 0, "major": 0, "required_minor": 0}}
        self.assertTrue(RUNNER.minimal3350_review_receipt_valid("engineering", receipt, CARD["run_id"], CARD_SHA, ROOT))
        receipt["schema"] = "stage6_minimal3350_e1_r900_engineering_prelaunch_review_v1"
        self.assertFalse(RUNNER.minimal3350_review_receipt_valid("engineering", receipt, CARD["run_id"], CARD_SHA, ROOT))

if __name__ == "__main__":
    unittest.main()

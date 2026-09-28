import hashlib
import importlib.util
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[4]
PACKAGE = ROOT / "artifacts/stage6_full_network_abc_phenomenon_validation_plan_20260926_v1/A_launch_package"
CARD = PACKAGE / "FULLNET3350_A_R900_S17_CARD_DRAFT_NOT_AUTHORIZED_REV1.json"
FINAL_CARD = PACKAGE / "FULLNET3350_A_R900_S17_CARD_FINAL_REV1.json"
RUNNER_PATH = ROOT / "artifacts/stage6_ramp_induced_validation_20260922_v1/r02_single_start/runner.py"
SPEC = importlib.util.spec_from_file_location("r02_runner_a_binding_test", RUNNER_PATH)
runner = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(runner)


class FullNetworkABindingTests(unittest.TestCase):
    def setUp(self):
        self.card = json.loads(CARD.read_text())
        self.repo = ROOT.resolve()

    def test_superseded_draft_cannot_be_used_with_revised_runner(self):
        card_hash = hashlib.sha256(CARD.read_bytes()).hexdigest()
        with self.assertRaisesRegex(runner.GateError, "GUARDIAN_RUNNER_HASH_MISMATCH"):
            runner.make_plan(self.repo, CARD, card_hash)

    def test_exact_final_card_is_launchable_but_preflight_starts_nothing(self):
        card_hash = hashlib.sha256(FINAL_CARD.read_bytes()).hexdigest()
        plan = runner.make_plan(self.repo, FINAL_CARD, card_hash)
        self.assertEqual(plan["status"], "PREFLIGHT_PASS_NO_PROCESS_STARTED")
        self.assertTrue(plan["launch_authorized"])
        self.assertTrue(plan["launchable_now"])
        self.assertFalse(plan["simulator_process_started"])
        self.assertEqual(plan["max_starts"], 1)
        self.assertEqual(plan["technical_retries"], 0)

    def test_final_card_rejects_changed_authorization_scope(self):
        card_hash = hashlib.sha256(FINAL_CARD.read_bytes()).hexdigest()
        altered = json.loads(FINAL_CARD.read_text())
        altered["authorization_record"]["prohibited_runs"] = ["C"]
        original_load = runner.load_json

        def load_with_altered_card(path):
            if Path(path).resolve() == FINAL_CARD.resolve():
                return altered
            return original_load(path)

        with patch.object(runner, "load_json", side_effect=load_with_altered_card):
            with self.assertRaisesRegex(runner.GateError, "ABC_A_AUTHORIZATION_SCOPE_MISMATCH"):
                runner.verify_card(self.repo, FINAL_CARD, card_hash)

    def test_final_card_rejects_alternate_card_path(self):
        other = PACKAGE / "FULLNET3350_A_R900_S17_CARD_FINAL_NOT_ALLOWLISTED.json"
        other.write_text(FINAL_CARD.read_text())
        try:
            with self.assertRaisesRegex(runner.GateError, "RUNNER_BINDING_MISMATCH:card_path"):
                runner._run_binding(self.repo, other.resolve(), json.loads(other.read_text()))
        finally:
            other.unlink()

    def test_wrong_route_reference_fails_closed(self):
        source = PACKAGE / "inputs/scenario.sumocfg"
        xml = source.read_text()
        changed = xml.replace(
            str((PACKAGE / "data_binding/demand_A_materialized.rou.xml").resolve()),
            str((PACKAGE / "data_binding/stale_demand.xml").resolve()),
        )
        self.assertNotEqual(xml, changed)
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".sumocfg", dir=PACKAGE / "inputs", delete=False
        ) as tmp:
            tmp.write(changed)
            tmp_path = Path(tmp.name)
        try:
            with self.assertRaisesRegex(runner.GateError, "ABC_A_NESTED_INPUT_REFERENCE_MISMATCH:route-files"):
                runner.validate_fullnetwork_abc_a_nested_references(
                    self.repo, self.card, tmp_path, PACKAGE / "inputs/scenario.add.xml"
                )
        finally:
            tmp_path.unlink()

    def test_output_role_outside_a_root_fails_closed(self):
        original = json.loads((PACKAGE / "output_roles.json").read_text())
        changed = json.loads(json.dumps(original))
        changed["required_xml_roles"][0]["path"] = "/tmp/old-run/outputs/old.xml"
        with patch.object(runner, "load_json", return_value=changed):
            with self.assertRaisesRegex(runner.GateError, "ABC_A_OUTPUT_ROLE_PATH_MISMATCH"):
                runner.validate_fullnetwork_abc_a_nested_references(
                    self.repo,
                    self.card,
                    PACKAGE / "inputs/scenario.sumocfg",
                    PACKAGE / "inputs/scenario.add.xml",
                )


if __name__ == "__main__":
    unittest.main()

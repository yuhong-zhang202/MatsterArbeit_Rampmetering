from __future__ import annotations

import importlib.util
import json
from pathlib import Path
import shutil
import tempfile
import unittest

from scripts.stage6.minimal3199.minimal3199_adapter import ROOT, sha256

RUNNER_PATH = ROOT / "artifacts/stage6_ramp_induced_validation_20260922_v1/r02_single_start/runner.py"
CARD_PATH = ROOT / "artifacts/stage6_minimal3199_ctrl_technical_retry_20260924_v1/MINIMAL3199_CTRL_S17_TECH_RETRY1_CARD_DRAFT.json"

_spec = importlib.util.spec_from_file_location("minimal3199_technical_retry_runner", RUNNER_PATH)
RUNNER = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(RUNNER)


class Minimal3199TechnicalRetryTests(unittest.TestCase):
    def _valid_guardian_request_fixture(self, temp: Path, run_id=None):
        root = temp.resolve()
        run_id = run_id or RUNNER.MINIMAL3199_RETRY_RUN_ID
        runner_rel = "scripts/r02/runner.py"
        runner_file = root / runner_rel
        runner_file.parent.mkdir(parents=True)
        shutil.copyfile(RUNNER_PATH, runner_file)
        runner_hash = sha256(runner_file)
        role_source_rel = "inputs/output_roles.json"
        role_source = root / role_source_rel
        role_source.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(ROOT / "scripts/stage6/minimal3199/prepared_rev3/control/output_roles.json", role_source)
        role_source_hash = sha256(role_source)
        role_data = json.loads(role_source.read_text(encoding="utf-8"))
        output_rel = "data/raw/retry/outputs"
        consumption_rel = "artifacts/retry/consumption"
        card_rel = "artifacts/retry/card.json"
        runtime_rel = "artifacts/retry/runtime.json"
        schema = json.loads((CARD_PATH.parent / "control/runtime_binding_final.json").read_text(encoding="utf-8"))
        schema.update({
            "binary_path": "/sumo",
            "sumo_home": RUNNER.EXPECTED_SUMO_HOME,
            "additional_schema_path": RUNNER.EXPECTED_ADDITIONAL_SCHEMA,
            "additional_schema_sha256": RUNNER.EXPECTED_ADDITIONAL_SCHEMA_SHA256,
            "max_runtime_s": 90,
            "max_output_bytes": 60_000_000,
            "guardian_runner_sha256": runner_hash,
        })
        runtime_file = root / runtime_rel
        runtime_file.parent.mkdir(parents=True, exist_ok=True)
        runtime_file.write_bytes(RUNNER.canonical_json_bytes(schema))
        binding = {
            "package_id": "retry", "card_path": card_rel,
            "output_directory": output_rel, "consumption_directory": consumption_rel,
            "kind": "MINIMAL3199_TECH_RETRY_FINAL_CONTROL",
            "runtime_binding_path": runtime_rel, "runtime_binding_sha256": sha256(runtime_file),
            "output_role_source": role_source_rel, "request_schema": "r02-start-v2",
            "approved_card_sha256": "pending",
        }
        card = {
            "run_id": run_id, "execution_attempt_id": run_id,
            "card_status": "FINAL_AUTHORIZED_FOR_ONE_START", "execution_authorized": True,
            "output_directory": output_rel, "runtime_binding": schema,
            "runner": {"path": runner_rel, "sha256": runner_hash},
            "output_role_source": {"path": role_source_rel, "sha256": role_source_hash},
            "runner_binding": {"run_id": run_id, "package_id": "retry", "card_path": card_rel,
                               "output_directory": output_rel, "consumption_directory": consumption_rel,
                               "kind": "MINIMAL3199_TECH_RETRY_FINAL_CONTROL"},
        }
        card_file = root / card_rel
        card_file.parent.mkdir(parents=True, exist_ok=True)
        card_file.write_bytes(RUNNER.canonical_json_bytes(card))
        binding["approved_card_sha256"] = sha256(card_file)
        output = (root / output_rel).resolve(strict=False)
        reservation = (root / consumption_rel / f"{run_id}.json").resolve(strict=False)
        request = {
            "action": "START", "run_id": run_id,
            "command": [schema["binary_path"], "-c", str(output / "scenario_control.sumocfg")],
            "cwd": str(root), "output_directory": str(output), "reservation_path": str(reservation),
            "sumo_home": schema["sumo_home"],
            "additional_schema_path": schema["additional_schema_path"],
            "additional_schema_sha256": schema["additional_schema_sha256"],
            "max_runtime_s": 90, "max_output_bytes": 60_000_000,
            "output_roles": role_data["required_xml_roles"],
            "output_role_source": role_source_rel,
            "output_role_source_sha256": role_source_hash,
            "request_schema": "r02-start-v2", "card_path": card_rel,
            "card_sha256": binding["approved_card_sha256"],
            "runtime_binding_path": runtime_rel, "runtime_binding_sha256": binding["runtime_binding_sha256"],
            "runner_path": runner_rel, "runner_sha256": runner_hash,
        }
        return root, request, {run_id: binding}

    def test_superseded_draft_fails_closed_after_runner_revision(self):
        with self.assertRaisesRegex(RUNNER.GateError, "MINIMAL3199_RUNNER_HASH_BINDING_MISMATCH"):
            RUNNER.make_plan(ROOT, CARD_PATH, sha256(CARD_PATH))

    def test_draft_refuses_launch_before_consumption_or_process(self):
        with self.assertRaisesRegex(RUNNER.GateError, "CARD_NOT_EXACTLY_AUTHORIZED"):
            RUNNER.verify_card(ROOT, CARD_PATH, sha256(CARD_PATH), allow_prelaunch=False)
        card = json.loads(CARD_PATH.read_text(encoding="utf-8"))
        reservation = ROOT / card["runner_binding"]["consumption_directory"] / f"{card['run_id']}.json"
        self.assertTrue(reservation.exists())
        self.assertEqual(json.loads(reservation.read_text(encoding="utf-8"))["retry_allowed"], False)

    def test_staging_helper_rebinds_config_and_all_additional_outputs(self):
        card = json.loads(CARD_PATH.read_text(encoding="utf-8"))
        source_cfg = ROOT / "scripts/stage6/minimal3199/prepared_rev3/control/scenario.sumocfg"
        source_add = ROOT / "scripts/stage6/minimal3199/prepared_rev3/control/scenario.add.xml"
        old_output = ROOT / "data/raw/stage6_minimal3199_existence_20260924_v1/MINIMAL3199_CTRL_S17/outputs"
        new_output = ROOT / card["output_directory"]
        cfg_data, add_data, transform = RUNNER.stage_minimal3199_inputs(source_cfg, source_add, old_output, new_output)
        manifest = json.loads((CARD_PATH.parent / card["input_manifest"]).read_text(encoding="utf-8"))
        expected = manifest["staged_config"]["transform"]
        cfg_text, add_text = cfg_data.decode("utf-8"), add_data.decode("utf-8")
        self.assertNotIn(str(old_output), cfg_text)
        self.assertNotIn(str(old_output), add_text)
        self.assertEqual(cfg_text.count(str(new_output)) - cfg_text.count(str(new_output / "scenario_control.add.xml")), 8)
        self.assertEqual(cfg_text.count(str(new_output / "scenario_control.add.xml")), 1)
        self.assertEqual(add_text.count(str(new_output)), 12)
        self.assertEqual(transform, expected)
        self.assertEqual(transform["sumocfg"]["expected_staged_sha256"], card["staged_config_sha256"])
        self.assertEqual(transform["sumocfg"]["expected_staged_bytes"], card["staged_config_bytes"])
        self.assertEqual(transform["additional"]["expected_staged_sha256"], card["staged_additional_sha256"])
        self.assertEqual(transform["additional"]["expected_staged_bytes"], card["staged_additional_bytes"])
        self.assertEqual({p.name for p in new_output.iterdir()},
                         {"scenario_control.sumocfg", "scenario_control.add.xml", "guardian_stderr.log"})
        staged_cfg = new_output / "scenario_control.sumocfg"
        staged_add = new_output / "scenario_control.add.xml"
        self.assertFalse(staged_cfg.is_symlink())
        self.assertFalse(staged_add.is_symlink())
        self.assertEqual(staged_cfg.read_bytes(), cfg_data)
        self.assertEqual(staged_add.read_bytes(), add_data)
        self.assertEqual(staged_cfg.stat().st_size, card["staged_config_bytes"])
        self.assertEqual(staged_add.stat().st_size, card["staged_additional_bytes"])
        self.assertEqual(sha256(staged_cfg), card["staged_config_sha256"])
        self.assertEqual(sha256(staged_add), card["staged_additional_sha256"])

    def test_staging_fails_closed_when_additional_output_count_changes(self):
        source_cfg = ROOT / "scripts/stage6/minimal3199/prepared_rev3/control/scenario.sumocfg"
        source_add = ROOT / "scripts/stage6/minimal3199/prepared_rev3/control/scenario.add.xml"
        old_output = ROOT / "data/raw/stage6_minimal3199_existence_20260924_v1/MINIMAL3199_CTRL_S17/outputs"
        new_output = ROOT / "data/raw/stage6_minimal3199_existence_20260924_v2/MINIMAL3199_CTRL_S17_TECH_RETRY1/outputs"
        with tempfile.TemporaryDirectory() as temp:
            temp_add = Path(temp) / "scenario.add.xml"
            text = source_add.read_text(encoding="utf-8")
            text = text.replace(str(old_output), "/tmp/unbound_output_root", 1)
            temp_add.write_text(text, encoding="utf-8")
            with self.assertRaisesRegex(RUNNER.GateError, "STAGED_INPUT_TRANSFORM_SOURCE_OCCURRENCE_MISMATCH"):
                RUNNER.stage_minimal3199_inputs(source_cfg, temp_add, old_output, new_output)

    def test_guardian_start_fails_closed_when_resolved_schema_is_missing(self):
        files = {"binary": Path("/sumo"), "sumocfg": Path("/cfg"), "sumo_home": Path("/sumo-home"),
                 "output_roles": [], "output_role_source_sha256": "0" * 64}
        card = {"runtime_binding": {"max_runtime_s": 90, "max_output_bytes": 60_000_000}}
        with self.assertRaisesRegex(RUNNER.GateError, "RESOLVED_START_INPUT_MISSING:additional_schema"):
            RUNNER.build_guardian_start_spec(files, card, Path("/out"), Path("/reservation"), ROOT, "x")

    def test_guardian_start_rejects_wrong_schema_hash(self):
        with tempfile.TemporaryDirectory() as temp:
            schema = Path(temp) / "schema.xsd"
            schema.write_text("schema", encoding="utf-8")
            files = {"binary": Path("/sumo"), "sumocfg": Path("/cfg"), "sumo_home": Path("/sumo-home"),
                     "additional_schema": schema, "output_roles": [], "output_role_source_sha256": "0" * 64}
            card = {"runtime_binding": {"additional_schema_sha256": "0" * 64,
                                         "max_runtime_s": 90, "max_output_bytes": 60_000_000},
                    "output_role_source": {"path": "roles.json"}}
            with self.assertRaisesRegex(RUNNER.GateError, "RESOLVED_ADDITIONAL_SCHEMA_HASH_MISMATCH"):
                RUNNER.build_guardian_start_spec(files, card, Path("/out"), Path("/reservation"), ROOT, "x")

    def test_staged_hash_mismatch_is_a_gate_error(self):
        card = json.loads(CARD_PATH.read_text(encoding="utf-8"))
        manifest = json.loads((CARD_PATH.parent / card["input_manifest"]).read_text(encoding="utf-8"))
        spec = manifest["staged_config"]
        bad_transform = json.loads(json.dumps(spec["transform"]))
        bad_transform["additional"]["expected_staged_sha256"] = "0" * 64
        with self.assertRaisesRegex(RUNNER.GateError, "MINIMAL3199_STAGED_INPUT_EXPECTATION_MISMATCH"):
            RUNNER.validate_staged_config_binding(
                {"sumocfg_source": spec["sumocfg_source"],
                 "additional_source": spec["additional_source"], "transform": bad_transform},
                card, {"sumocfg": spec["sumocfg_source"], "additional": spec["additional_source"]},
                spec["transform"])

    def test_contradictory_duplicate_runner_hash_is_rejected(self):
        card = json.loads(CARD_PATH.read_text(encoding="utf-8"))
        manifest = json.loads((CARD_PATH.parent / card["input_manifest"]).read_text(encoding="utf-8"))
        runtime = card["runtime_binding"]
        runner_path = ROOT / manifest["runner_path"]
        actual_hash = sha256(runner_path)
        manifest["runner"] = {"path": str(runner_path), "sha256": "0" * 64}
        with self.assertRaisesRegex(RUNNER.GateError, "MINIMAL3199_DUPLICATE_RUNNER_HASH_MISMATCH"):
            RUNNER.validate_minimal3199_runner_hashes(manifest, card, runtime, runner_path, ROOT, actual_hash)

    def test_missing_schema_hash_or_path_in_resolved_runtime_is_gate_error(self):
        runtime = json.loads(CARD_PATH.read_text(encoding="utf-8"))["runtime_binding"]
        del runtime["additional_schema_path"]
        with self.assertRaisesRegex(RUNNER.GateError, "ADDITIONAL_SCHEMA_PATH_MISMATCH"):
            RUNNER.verified_additional_schema(runtime)

    def test_final_retry_waits_for_exact_card_review_receipts(self):
        gate = RUNNER.minimal3199_retry_final_review_gate(ROOT, "f" * 64)
        self.assertEqual(gate["status"], "WAITING_FOR_REQUIRED_REVIEWS")
        self.assertEqual(gate["review_binding_status"], "PENDING_REVIEWS")
        self.assertEqual(set(gate["reviews"]), {"engineering", "data_provenance", "scientific"})

    def test_reconstructed_historical_guardian_start_is_rejected_pre_spawn(self):
        fixture_path = ROOT / "tests/fixtures/minimal3199_tech_retry1_guardian_start_reconstructed.json"
        fixture = json.loads(fixture_path.read_text(encoding="utf-8"))
        self.assertIn("Deterministic reconstruction", fixture["reconstruction_provenance"]["basis"])
        with self.assertRaisesRegex(RUNNER.GateError, "INVALID_START_REQUEST_SCHEMA"):
            RUNNER.validate_guardian_start_request(
                fixture["guardian_start_request"], ROOT)

    def test_guardian_accepts_valid_exact_v2_request_without_process(self):
        with tempfile.TemporaryDirectory() as temp:
            root, request, bindings = self._valid_guardian_request_fixture(Path(temp))
            result = RUNNER.validate_guardian_start_request(request, root, bindings)
            self.assertEqual(result["kind"], "MINIMAL3199_TECH_RETRY_FINAL_CONTROL")

    def test_guardian_accepts_only_exact_fresh_retry2_binding(self):
        with tempfile.TemporaryDirectory() as temp:
            root, request, bindings = self._valid_guardian_request_fixture(
                Path(temp), RUNNER.MINIMAL3199_RETRY2_RUN_ID)
            result = RUNNER.validate_guardian_start_request(request, root, bindings)
            self.assertEqual(request["run_id"], RUNNER.MINIMAL3199_RETRY2_RUN_ID)
            self.assertEqual(RUNNER.MINIMAL3199_RETRY2_FINAL_BINDING["card_path"],
                             "artifacts/stage6_minimal3199_ctrl_technical_retry2_20260924_v1/MINIMAL3199_CTRL_S17_TECH_RETRY2_CARD_FINAL.json")
            self.assertIs(RUNNER.SUPPORTED_RUN_BINDINGS[request["run_id"]],
                          RUNNER.MINIMAL3199_RETRY2_FINAL_BINDING)

    def test_guardian_rejects_unregistered_retry3_id(self):
        with tempfile.TemporaryDirectory() as temp:
            root, request, _ = self._valid_guardian_request_fixture(Path(temp))
            request["run_id"] = "MINIMAL3199_CTRL_S17_TECH_RETRY3"
            with self.assertRaisesRegex(RUNNER.GateError, "INVALID_START_REQUEST"):
                RUNNER.validate_guardian_start_request(request, root)

    def test_guardian_rejects_missing_extra_wrong_type_and_wrong_path(self):
        mutations = [
            (lambda r: r.pop("card_sha256"), "INVALID_START_REQUEST_SCHEMA"),
            (lambda r: r.__setitem__("unbound", True), "INVALID_START_REQUEST_SCHEMA"),
            (lambda r: r.__setitem__("command", "/sumo -c config"), "INVALID_START_REQUEST_TYPES"),
            (lambda r: r.__setitem__("output_directory", "/wrong/output"), "START_PROVENANCE_BINDING_MISMATCH"),
        ]
        for mutate, expected in mutations:
            with self.subTest(expected=expected):
                with tempfile.TemporaryDirectory() as temp:
                    root, request, bindings = self._valid_guardian_request_fixture(Path(temp))
                    mutate(request)
                    with self.assertRaisesRegex(RUNNER.GateError, expected):
                        RUNNER.validate_guardian_start_request(request, root, bindings)


if __name__ == "__main__":
    unittest.main()

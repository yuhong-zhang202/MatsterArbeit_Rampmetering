"""Offline R02 binding/Guardian tests. All executable/runtime paths are fixtures."""
from __future__ import annotations

import hashlib
import io
import json
import os
from pathlib import Path
import signal
import shutil
import tempfile
import unittest
from unittest import mock

import runner

REAL_ROOT = Path(__file__).resolve().parents[3]
PAIR_REL = "artifacts/stage6_pair_3199_s17_preparation_20260923_v1"
INPUTS = {
    "sumocfg": "scenario.sumocfg", "demand": "demand.rou.xml",
    "additional": "scenario.add.xml", "network": "network.net.xml",
}


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


class PairRunnerTests(unittest.TestCase):
    def test_repaired_v5_final_card_with_stale_runner_hash_fails_closed(self):
        rel = runner.REPAIRED_V5_FINAL_BINDING["card_path"]
        card = REAL_ROOT / rel
        digest = sha(card)
        with self.assertRaisesRegex(runner.GateError, "GUARDIAN_RUNNER_HASH_MISMATCH"):
            runner.make_plan(REAL_ROOT, card, digest)
        with self.assertRaisesRegex(runner.GateError, "APPROVED_CARD_HASH_MISMATCH"):
            runner.make_plan(REAL_ROOT, card, "0" * 64)

    def test_repaired_final_review_gate_requires_exact_card_bound_zero_finding_reviews(self):
        digest = "a" * 64
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            for rel in runner.REPAIRED_V5_FINAL_BINDING["required_review_receipts"].values():
                path = root / rel
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text(json.dumps({"status": "PASS_PRELAUNCH", "card_sha256": digest,
                                            "findings": {"blocker": 0, "major": 0, "required_minor": 0}}),
                                encoding="utf-8")
            hashes = {role: sha(root / rel) for role, rel in
                      runner.REPAIRED_V5_FINAL_BINDING["required_review_receipts"].items()}
            sidecar_path = root / runner.REPAIRED_V5_FINAL_BINDING["review_binding"]
            sidecar_path.parent.mkdir(parents=True, exist_ok=True)
            sidecar_path.write_text(json.dumps({"status": "FINAL_PRELAUNCH_REVIEW_GATE_PASS",
                                                "card_sha256": digest, "review_receipt_sha256": hashes}),
                                    encoding="utf-8")
            self.assertEqual(runner.repaired_final_review_gate(root, digest)["status"], "PASS")
            sidecar_path.write_text(json.dumps({"status": "FINAL_PRELAUNCH_REVIEW_GATE_PASS",
                                                "card_sha256": "b" * 64, "review_receipt_sha256": hashes}),
                                    encoding="utf-8")
            self.assertEqual(runner.repaired_final_review_gate(root, digest)["status"],
                             "WAITING_FOR_REQUIRED_REVIEWS")

    def test_superseded_repaired_treatment_draft_fails_closed_after_runner_revision(self):
        rel = runner.REPAIRED_PRELAUNCH_BINDING["card_path"]
        card = REAL_ROOT / rel
        digest = sha(card)
        with self.assertRaisesRegex(runner.GateError, "GUARDIAN_RUNNER_HASH_MISMATCH"):
            runner.make_plan(REAL_ROOT, card, digest)

    def test_repaired_prelaunch_hash_run_id_output_and_path_mismatches_refused(self):
        rel = runner.REPAIRED_PRELAUNCH_BINDING["card_path"]
        source = REAL_ROOT / rel
        original = json.loads(source.read_text(encoding="utf-8"))
        with self.assertRaisesRegex(runner.GateError, "APPROVED_CARD_HASH_MISMATCH"):
            runner.make_plan(REAL_ROOT, source, "0" * 64)

        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            exact_path = root / rel
            exact_path.parent.mkdir(parents=True)

            wrong_run = dict(original)
            wrong_run["run_id"] = "PAIR_3199_CTRL_S17"
            exact_path.write_text(json.dumps(wrong_run), encoding="utf-8")
            with self.assertRaises(runner.GateError):
                runner._run_binding(root, exact_path, wrong_run)

            wrong_output = dict(original)
            wrong_output["output_directory"] += "_unexpected"
            exact_path.write_text(json.dumps(wrong_output), encoding="utf-8")
            with self.assertRaisesRegex(runner.GateError, "OUTPUT_DIRECTORY_BINDING_MISMATCH"):
                runner._run_binding(root, exact_path, wrong_output)

            wrong_binding = dict(original)
            wrong_binding["runner_binding"] = dict(original["runner_binding"])
            wrong_binding["runner_binding"]["card_path"] += ".other"
            exact_path.write_text(json.dumps(wrong_binding), encoding="utf-8")
            with self.assertRaisesRegex(runner.GateError, "RUNNER_BINDING_MISMATCH:card_path"):
                runner._run_binding(root, exact_path, wrong_binding)

            displaced = root / "alternate" / Path(rel).name
            displaced.parent.mkdir(parents=True)
            displaced.write_text(json.dumps(original), encoding="utf-8")
            with self.assertRaisesRegex(runner.GateError, "RUNNER_BINDING_MISMATCH:package_id"):
                runner._run_binding(root, displaced, original)

    def test_treatment_prelaunch_is_readonly_and_cannot_launch(self):
        td, root, card, digest, _, _ = self.make_fixture(prelaunch=True)
        plan = runner.make_plan(root, card, digest)
        self.assertEqual(plan["run_id"], "PAIR_3199_R720_DELAYED_S17")
        self.assertFalse(plan["simulator_process_started"])
        self.assertFalse(plan["launch_authorized"])
        self.assertEqual(card.read_text().count("first_scheduled_R_departure"), 1)
        self.assertEqual(card.read_text().count("first_actual_R_departure"), 1)
        self.assertEqual(card.read_text().count("first_R_arrival_near_merge"), 1)
        with self.assertRaisesRegex(runner.GateError, "CARD_NOT_EXACTLY_AUTHORIZED"):
            runner.verify_card(root, card, digest, allow_prelaunch=False)
        td.cleanup()

    def test_final_control_binding_accepts_exact_authorized_card(self):
        td, root, card, digest, _, _ = self.make_fixture(final=True)
        plan = runner.make_plan(root, card, digest)
        self.assertEqual(plan["run_id"], "PAIR_3199_CTRL_S17")
        self.assertFalse(plan["simulator_process_started"])
        self.assertEqual(plan["max_starts"], 1)
        self.assertEqual(plan["technical_retries"], 0)
        td.cleanup()

    def test_final_treatment_binding_accepts_exact_single_start_card(self):
        td, root, card, digest, _, _ = self.make_fixture(
            run_id="PAIR_3199_R720_DELAYED_S17", final=True)
        plan = runner.make_plan(root, card, digest)
        self.assertEqual(plan["run_id"], "PAIR_3199_R720_DELAYED_S17")
        self.assertTrue(plan["launch_authorized"])
        self.assertEqual(plan["max_starts"], 1)
        self.assertEqual(plan["technical_retries"], 0)
        self.assertEqual(plan["guardian_runner_sha256"], sha(Path(runner.__file__).resolve()))
        td.cleanup()

    def test_final_control_wrong_run_card_hash_path_resource_or_provenance_refused(self):
        td, root, card, _, _, _ = self.make_fixture(final=True)
        value = json.loads(card.read_text())
        value["run_id"] = "PAIR_3199_R720_DELAYED_S17"
        card.write_text(json.dumps(value, sort_keys=True))
        with self.assertRaises(runner.GateError):
            runner.make_plan(root, card, sha(card))
        td.cleanup()

        td, root, card, _, _, _ = self.make_fixture(final=True)
        with self.assertRaisesRegex(runner.GateError, "APPROVED_CARD_HASH_MISMATCH"):
            runner.make_plan(root, card, "0" * 64)
        td.cleanup()

        td, root, card, _, _, _ = self.make_fixture(final=True)
        value = json.loads(card.read_text())
        value["runner_binding"]["card_path"] = runner.SUPPORTED_RUN_BINDINGS["PAIR_3199_CTRL_S17"]["card_path"]
        card.write_text(json.dumps(value, sort_keys=True))
        with self.assertRaisesRegex(runner.GateError, "RUNNER_BINDING_MISMATCH:card_path"):
            runner.make_plan(root, card, sha(card))
        td.cleanup()

        td, root, card, _, _, _ = self.make_fixture(final=True)
        value = json.loads(card.read_text())
        value["resource_limits"]["storage_bytes"] = 1
        card.write_text(json.dumps(value, sort_keys=True))
        with self.assertRaisesRegex(runner.GateError, "RUNTIME_RESOURCE_BINDING_MISMATCH"):
            runner.make_plan(root, card, sha(card))
        td.cleanup()

        td, root, card, _, _, runtime_file = self.make_fixture(final=True)
        runtime_file.write_text("{}\n")
        with self.assertRaisesRegex(runner.GateError, "RUNTIME_BINDING_FILE_HASH_MISMATCH"):
            runner.make_plan(root, card, sha(card))
        td.cleanup()

        td, root, card, _, package, _ = self.make_fixture(final=True)
        demand = package / "inputs/control/demand.rou.xml"
        demand.write_bytes(demand.read_bytes() + b"\n")
        with self.assertRaisesRegex(runner.GateError, "INPUT_HASH_MISMATCH:demand"):
            runner.make_plan(root, card, sha(card))
        td.cleanup()

        td, root, card, _, _, _ = self.make_fixture(final=True)
        value = json.loads(card.read_text())
        value["authorization_record"]["prohibited_runs"].remove("PAIR_3199_R720_DELAYED_S17")
        card.write_text(json.dumps(value, sort_keys=True))
        with self.assertRaisesRegex(runner.GateError, "FINAL_CARD_AUTHORIZATION_SCOPE_MISMATCH"):
            runner.make_plan(root, card, sha(card))
        td.cleanup()

        td, root, card, digest, _, _ = self.make_fixture(final=True)
        output = root / runner.FINAL_AUTHORIZED_BINDINGS["PAIR_3199_CTRL_S17"]["output_directory"]
        output.parent.mkdir(parents=True)
        output.mkdir()
        with self.assertRaisesRegex(runner.GateError, "OUTPUT_DIRECTORY_ALREADY_EXISTS|OUTPUT_RUN_ROOT_ALREADY_EXISTS"):
            runner.make_plan(root, card, digest)
        td.cleanup()

    def make_fixture(self, run_id="PAIR_3199_CTRL_S17", authorized=True, final=False, prelaunch=False):
        if prelaunch:
            run_id = "PAIR_3199_R720_DELAYED_S17"
        td = tempfile.TemporaryDirectory()
        root = Path(td.name)
        arm = "control" if run_id.endswith("CTRL_S17") else "treatment"
        package = root / "artifacts" / "stage6_pair_3199_s17_preparation_20260923_v1"
        arm_dir = package / "inputs" / arm
        arm_dir.mkdir(parents=True)
        source_dir = REAL_ROOT / PAIR_REL / "inputs" / arm
        for name in ("scenario.sumocfg", "demand.rou.xml", "scenario.add.xml",
                     "output_roles.json", "expected_identity_manifest.json"):
            shutil.copyfile(source_dir / name, arm_dir / name)
        network_rel = "artifacts/stage6_baseline_localization_20260921_v1/LOC_M3350_S17/engineering/build_attempts/TV_BUILD01/network.net.xml"
        network = root / network_rel
        network.parent.mkdir(parents=True)
        shutil.copyfile(REAL_ROOT / network_rel, network)

        fakebin = (root / "fake-runtime" / "sumo").resolve()
        fakebin.parent.mkdir()
        fakebin.write_bytes(b"mock sumo executable; never invoked\n")
        fakebin.chmod(0o755)
        fakepy = (root / "fake-runtime" / "python").resolve()
        fakepy.write_bytes(b"mock python executable; never invoked\n")
        home = (root / "fake-runtime" / "share" / "sumo").resolve()
        schema = home / "data" / "xsd" / "additional_file.xsd"
        schema.parent.mkdir(parents=True)
        schema.write_bytes(b"mock schema\n")
        required_versions = {name: "fixture" for name in runner.REQUIRED_PYTHON_PACKAGES}
        max_runtime = 120 if prelaunch or (final and run_id == "PAIR_3199_R720_DELAYED_S17") else 90
        max_output = 90_000_000 if prelaunch or (final and run_id == "PAIR_3199_R720_DELAYED_S17") else 60_000_000
        runtime = {
            "binary_path": str(fakebin), "binary_sha256": sha(fakebin), "binary_version": "1.26.0",
            "version_evidence": {"binary_path": str(fakebin), "binary_sha256": sha(fakebin),
                                 "reported_version": "1.26.0",
                                 "query": "sumo --version (environment probe; no simulation)"},
            "python_environment": {"executable_path": str(fakepy), "executable_sha256": sha(fakepy),
                                   "version": "3.13.0", "implementation": "CPython",
                                   "package_versions": required_versions},
            "max_runtime_s": max_runtime, "max_output_bytes": max_output,
            "guardian_runner_sha256": sha(Path(runner.__file__).resolve()),
            "sumo_home": str(home), "additional_schema_path": str(schema),
            "additional_schema_sha256": sha(schema),
            "resource_proposal": {"scope": run_id,
                                  "status": "PROPOSED_NOT_AUTHORIZED" if prelaunch else ("AUTHORIZED_FOR_THIS_RUN" if final else "PROPOSED_NOT_AUTHORIZED"),
                                  "wallclock_stop_limit_s": max_runtime,
                                  "output_size_stop_limit_bytes_decimal": max_output,
                                  "enforcement": "100ms_polled_stop_trigger_with_possible_overshoot_not_hard_quota"},
        }
        binding_dir = package / "runtime_bindings"
        binding_dir.mkdir()
        b = (runner.PRELAUNCH_ONLY_BINDINGS[run_id] if prelaunch else
             (runner.FINAL_AUTHORIZED_BINDINGS[run_id] if final else runner.SUPPORTED_RUN_BINDINGS[run_id]))
        runtime_rel = b.get("runtime_binding_path", f"artifacts/{package.name}/runtime_bindings/{run_id}.json")
        runtime_file = root / runtime_rel
        runtime_file.write_text(json.dumps(runtime, sort_keys=True), encoding="utf-8")

        input_manifest_rel = f"inputs/{arm}/expected_identity_manifest.json"
        manifest_file = package / input_manifest_rel
        manifest = json.loads(manifest_file.read_text())
        output_rel = runner.SUPPORTED_RUN_BINDINGS[run_id]["output_directory"]
        output_role_rel = f"{PAIR_REL}/inputs/{arm}/output_roles.json"
        input_rel = {
            "sumocfg": f"inputs/{arm}/scenario.sumocfg",
            "demand": f"inputs/{arm}/demand.rou.xml",
            "additional": f"inputs/{arm}/scenario.add.xml", "network": network_rel,
            "output_roles": f"inputs/{arm}/output_roles.json",
        }
        input_hashes = {role: sha((package / rel) if role != "network" else root / rel)
                        for role, rel in input_rel.items()}
        card_rel = b["card_path"]
        card_file = root / card_rel
        card_file.parent.mkdir(parents=True, exist_ok=True)
        status = ("PRELAUNCH_READY_AWAITING_AUTHORIZATION" if prelaunch else
                  ("FINAL_AUTHORIZED_FOR_ONE_START" if final else
                   ("AUTHORIZED_EXACT_CARD" if authorized else "DRAFT_NOT_AUTHORIZED")))
        card = {
            "schema_version": "1", "card_revision": 4 if prelaunch else (1 if final else 2),
            "card_status": status,
            "execution_authorized": False if prelaunch else authorized, "approval_required": True if prelaunch else (False if final else not authorized),
            "run_id": run_id, "pair_id": "PAIR_3199_S17", "seed": 17, "horizon_s": 2700,
            "max_starts": 1, "technical_retries": 0, "progression_allowed": False,
            "design_sha256": manifest["design_plan_sha256"],
            "input_manifest": input_manifest_rel,
            "input_manifest_sha256": sha(manifest_file),
            "inputs": input_rel, "input_sha256": input_hashes,
            "output_role_source": {"path": output_role_rel,
                                   "sha256": sha(package / f"inputs/{arm}/output_roles.json")},
            "output_directory": output_rel,
            "runner_binding": {"run_id": run_id, "package_id": b["package_id"],
                                "card_path": b["card_path"], "output_directory": b["output_directory"],
                                "consumption_directory": b["consumption_directory"], "kind": b["kind"]},
            "runtime_binding_path": runtime_rel, "runtime_binding_sha256": sha(runtime_file),
            "runtime_binding": runtime,
            "resource_limits": {"runtime_s": max_runtime, "storage_bytes": max_output,
                                "status": "PROPOSED_NOT_AUTHORIZED" if prelaunch else ("AUTHORIZED_FOR_THIS_RUN" if authorized else "PROPOSED_NOT_AUTHORIZED"),
                                "scope": run_id},
        }
        if prelaunch or (final and run_id == "PAIR_3199_R720_DELAYED_S17"):
            contract_rel = runner.STAGE6_WITNESS_CONTRACT_PATH
            contract_path = root / contract_rel
            contract_path.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(REAL_ROOT / contract_rel, contract_path)
            card["witness_contract"] = {"path": contract_rel, "sha256": sha(contract_path)}
            card["treatment_release_gate"] = "STAGE6_EXPLORATORY_RAMP_INDUCED_WITNESS_CONTRACT_ONLY"
            card["LOW_R_BACKGROUND_ACCEPTABLE_required_for_release"] = False
            card["required_event_timeline_markers"] = [
                "R_demand_activation", "first_scheduled_R_departure", "first_actual_R_departure",
                "first_R_arrival_near_merge", "first_meaningful_merge_exposure",
                "first_M_deterioration", "State1_onset",
            ]
        if final and run_id == "PAIR_3199_R720_DELAYED_S17":
            card["authorization_record"] = {
                "authorization": "USER_AUTHORIZED_EXACTLY_ONE_TREATMENT_START",
                "run_id": run_id, "exact_card_path": b["card_path"], "max_starts": 1,
                "technical_retries": 0, "wallclock_stop_trigger_s": 120,
                "output_size_stop_trigger_bytes_decimal": 90_000_000,
                "output_polling_interval_ms": 100, "polling_overshoot_accepted": True,
                "prohibited_runs": ["seed23", "B", "C", "transition", "other_qMain_qRamp"],
            }
        elif final:
            card["authorization_record"] = {
                "authorization": "USER_AUTHORIZED_EXACTLY_ONE_CONTROL_START",
                "run_id": run_id, "max_starts": 1, "technical_retries": 0,
                "prohibited_runs": ["PAIR_3199_R720_DELAYED_S17", "seed23", "B", "C", "other_qMain_qRamp"],
            }
        card_file.write_text(json.dumps(card, sort_keys=True), encoding="utf-8")
        patches = mock.patch.multiple(
            runner, EXPECTED_SUMO_PATH=str(fakebin), EXPECTED_SUMO_SHA256=sha(fakebin),
            EXPECTED_SUMO_HOME=str(home), EXPECTED_ADDITIONAL_SCHEMA=str(schema),
            EXPECTED_ADDITIONAL_SCHEMA_SHA256=sha(schema),
        )
        patches.start()
        self.addCleanup(patches.stop)
        self.addCleanup(td.cleanup)
        py_patch = mock.patch.object(runner.sys, "executable", str(fakepy))
        py_patch.start()
        self.addCleanup(py_patch.stop)
        self.addCleanup(mock.patch.object(runner.platform, "python_version", return_value="3.13.0").stop)
        version_patch = mock.patch.object(runner.platform, "python_version", return_value="3.13.0")
        version_patch.start()
        self.addCleanup(version_patch.stop)
        self.addCleanup(mock.patch.object(runner.platform, "python_implementation", return_value="CPython").stop)
        impl_patch = mock.patch.object(runner.platform, "python_implementation", return_value="CPython")
        impl_patch.start()
        self.addCleanup(impl_patch.stop)
        package_patch = mock.patch.object(runner.importlib.metadata, "version", side_effect=lambda name: required_versions[name])
        package_patch.start()
        self.addCleanup(package_patch.stop)
        return td, root, card_file, sha(card_file), package, runtime_file

    def test_both_pair_run_ids_bind_separately(self):
        for run_id in ("PAIR_3199_CTRL_S17", "PAIR_3199_R720_DELAYED_S17"):
            with self.subTest(run_id=run_id):
                td, root, card, digest, _, _ = self.make_fixture(run_id)
                plan = runner.make_plan(root, card, digest)
                self.assertEqual(plan["run_id"], run_id)
                self.assertNotEqual(plan["output_directory"], "")
                self.assertFalse(plan["simulator_process_started"])
                td.cleanup()

    def test_card_run_id_mismatch_refused(self):
        td, root, card, _, _, runtime_file = self.make_fixture()
        value = json.loads(card.read_text())
        value["run_id"] = "PAIR_3199_R720_DELAYED_S17"
        card.write_text(json.dumps(value, sort_keys=True))
        with self.assertRaisesRegex(runner.GateError, "RUNNER_BINDING_MISMATCH:run_id|CARD_PATH_RUN_ID_BINDING_MISMATCH"):
            runner.make_plan(root, card, sha(card))
        td.cleanup()

    def test_runtime_binding_hash_and_content_mismatch_refused(self):
        td, root, card, _, package, runtime_file = self.make_fixture()
        value = json.loads(card.read_text())
        value["runtime_binding"]["guardian_runner_sha256"] = "0" * 64
        card.write_text(json.dumps(value, sort_keys=True))
        with self.assertRaisesRegex(runner.GateError, "GUARDIAN_RUNNER_HASH_MISMATCH"):
            runner.make_plan(root, card, sha(card))
        value["runtime_binding"]["guardian_runner_sha256"] = sha(Path(runner.__file__).resolve())
        card.write_text(json.dumps(value, sort_keys=True))
        runtime_file.write_text("{}\n")
        with self.assertRaisesRegex(runner.GateError, "RUNTIME_BINDING_FILE_HASH_MISMATCH"):
            runner.make_plan(root, card, sha(card))
        td.cleanup()

    def test_cross_arm_runtime_sidecar_path_relabeling_refused(self):
        td, root, card, _, package, _ = self.make_fixture("PAIR_3199_CTRL_S17")
        treatment_sidecar = package / "runtime_bindings/PAIR_3199_R720_DELAYED_S17.json"
        treatment_sidecar.parent.mkdir(parents=True, exist_ok=True)
        treatment_sidecar.write_text("{}\n", encoding="utf-8")
        value = json.loads(card.read_text())
        value["runtime_binding_path"] = "artifacts/stage6_pair_3199_s17_preparation_20260923_v1/runtime_bindings/PAIR_3199_R720_DELAYED_S17.json"
        value["runtime_binding_sha256"] = sha(treatment_sidecar)
        card.write_text(json.dumps(value, sort_keys=True))
        with self.assertRaisesRegex(runner.GateError, "RUNTIME_BINDING_PATH_MISMATCH"):
            runner.make_plan(root, card, sha(card))
        td.cleanup()

    def test_cross_arm_resource_scope_relabeling_refused(self):
        td, root, card, _, package, runtime_file = self.make_fixture("PAIR_3199_CTRL_S17")
        value = json.loads(card.read_text())
        value["runtime_binding"]["resource_proposal"]["scope"] = "PAIR_3199_R720_DELAYED_S17"
        value["resource_limits"]["scope"] = "PAIR_3199_R720_DELAYED_S17"
        runtime_file.write_text(json.dumps(value["runtime_binding"], sort_keys=True), encoding="utf-8")
        value["runtime_binding_sha256"] = sha(runtime_file)
        card.write_text(json.dumps(value, sort_keys=True))
        with self.assertRaisesRegex(runner.GateError, "PAIR_RESOURCE_SCOPE_MISMATCH"):
            runner.make_plan(root, card, sha(card))
        td.cleanup()

    def test_sumo_home_and_binary_hash_mismatches_refused(self):
        td, root, card, _, _, runtime_file = self.make_fixture()
        value = json.loads(card.read_text())
        value["runtime_binding"]["sumo_home"] = "/wrong/sumo-home"
        runtime_file.write_text(json.dumps(value["runtime_binding"], sort_keys=True))
        value["runtime_binding_sha256"] = sha(runtime_file)
        card.write_text(json.dumps(value, sort_keys=True))
        with self.assertRaisesRegex(runner.GateError, "SUMO_HOME_PATH_(MISMATCH|NOT_FOUND)"):
            runner.make_plan(root, card, sha(card))
        td.cleanup()

        td, root, card, _, _, runtime_file = self.make_fixture()
        value = json.loads(card.read_text())
        value["runtime_binding"]["binary_sha256"] = "0" * 64
        runtime_file.write_text(json.dumps(value["runtime_binding"], sort_keys=True))
        value["runtime_binding_sha256"] = sha(runtime_file)
        card.write_text(json.dumps(value, sort_keys=True))
        with self.assertRaisesRegex(runner.GateError, "BINARY_HASH_MISMATCH"):
            runner.make_plan(root, card, sha(card))
        td.cleanup()

    def test_existing_output_path_refused(self):
        td, root, card, digest, _, _ = self.make_fixture()
        output = root / runner.SUPPORTED_RUN_BINDINGS["PAIR_3199_CTRL_S17"]["output_directory"]
        output.mkdir(parents=True)
        with self.assertRaisesRegex(runner.GateError, "OUTPUT_DIRECTORY_ALREADY_EXISTS"):
            runner.make_plan(root, card, digest)
        td.cleanup()

    def test_input_provenance_and_runner_hash_mismatch_refused(self):
        td, root, card, _, package, runtime_file = self.make_fixture()
        demand = package / "inputs/control/demand.rou.xml"
        demand.write_bytes(demand.read_bytes() + b"\n")
        with self.assertRaisesRegex(runner.GateError, "INPUT_HASH_MISMATCH:demand"):
            runner.make_plan(root, card, sha(card))
        td.cleanup()

        td, root, card, _, _, runtime_file = self.make_fixture()
        value = json.loads(card.read_text())
        value["runtime_binding"]["guardian_runner_sha256"] = "0" * 64
        runtime_file.write_text(json.dumps(value["runtime_binding"], sort_keys=True))
        value["runtime_binding_sha256"] = sha(runtime_file)
        card.write_text(json.dumps(value, sort_keys=True))
        with self.assertRaisesRegex(runner.GateError, "GUARDIAN_RUNNER_HASH_MISMATCH"):
            runner.make_plan(root, card, sha(card))
        td.cleanup()

    def test_draft_denied_for_preflight_and_launch_without_consumption(self):
        td, root, card, digest, _, _ = self.make_fixture(authorized=False)
        for action in (lambda: runner.make_plan(root, card, digest),
                       lambda: runner.launch(root, card, digest)):
            with self.assertRaisesRegex(runner.GateError, "CARD_NOT_EXACTLY_AUTHORIZED"):
                action()
        consumption = root / runner.SUPPORTED_RUN_BINDINGS["PAIR_3199_CTRL_S17"]["consumption_directory"]
        self.assertFalse(consumption.exists())
        self.assertFalse((root / runner.SUPPORTED_RUN_BINDINGS["PAIR_3199_CTRL_S17"]["output_directory"]).exists())
        td.cleanup()

    def test_one_use_no_retry_and_arm_output_isolation(self):
        for run_id in ("PAIR_3199_CTRL_S17", "PAIR_3199_R720_DELAYED_S17"):
            td, root, card, digest, _, _ = self.make_fixture(run_id)
            fake_guardian = type("Guardian", (), {"pid": 4242, "stdin": object(), "stdout": object(),
                                                  "poll": lambda self: None, "wait": lambda self, **kw: 0})()
            events = [
                {"event": "SPAWNED", "pid": 7777, "started_at_utc": "2026-09-23T00:00:00.000000Z"},
                {"event": "EXITED", "process_status": "PROCESS_EXITED", "return_code": 0,
                 "stop_reason": None, "started_at_utc": "2026-09-23T00:00:00.000000Z",
                 "finished_at_utc": "2026-09-23T00:00:01.000000Z", "wallclock_runtime_s": 1.0},
                {"event": "DISARMED"},
            ]
            def fake_start(output, sumo_home):
                order.append("guardian_start")
                for name in ("fcd.xml", "runner_stdout.log", "runner_stderr.log", "guardian_stderr.log"):
                    (output / name).write_text("mock\n", encoding="utf-8")
                return fake_guardian
            order = []
            real_fsync = runner._fsync_directory
            def tracked_fsync(path):
                order.append("directory_fsync")
                return real_fsync(path)
            with mock.patch.object(runner, "start_guardian", side_effect=fake_start), \
                    mock.patch.object(runner, "_read_guardian_event", side_effect=events), \
                    mock.patch.object(runner, "_write_json_line"), \
                    mock.patch.object(runner, "_fsync_directory", side_effect=tracked_fsync):
                self.assertEqual(runner.launch(root, card, digest), 0)
                self.assertLess(order.index("directory_fsync"), order.index("guardian_start"))
                output = root / runner.SUPPORTED_RUN_BINDINGS[run_id]["output_directory"]
                receipt = json.loads((output / "execution_receipt.json").read_text())
                self.assertEqual(receipt["run_id"], run_id)
                self.assertFalse(receipt["retry_allowed"])
                with self.assertRaisesRegex(runner.GateError, "ONE_START_ALREADY_CONSUMED"):
                    runner.launch(root, card, digest)
            td.cleanup()

    def test_reconstructed_atomic_reservation_durability_order(self):
        events = []
        real_write = runner._write_exclusive
        real_replace = runner.os.replace
        real_fsync = runner._fsync_directory
        def write(path, data):
            events.append("exclusive_file_write_fsync")
            return real_write(path, data)
        def replace(source, target):
            events.append("atomic_replace")
            return real_replace(source, target)
        def fsync(path):
            events.append("parent_directory_fsync")
            return real_fsync(path)
        with tempfile.TemporaryDirectory() as directory:
            state = Path(directory) / "reservation.json"
            with mock.patch.object(runner, "_write_exclusive", side_effect=write), \
                    mock.patch.object(runner.os, "replace", side_effect=replace), \
                    mock.patch.object(runner, "_fsync_directory", side_effect=fsync):
                runner._atomic_status(state, b"{}\n")
            self.assertEqual(events, ["exclusive_file_write_fsync", "atomic_replace", "parent_directory_fsync"])

    def test_reconstructed_guardian_invalid_start_creates_no_child(self):
        invalid = json.dumps({"action": "START", "run_id": "UNSUPPORTED"}) + "\n"
        with mock.patch.object(runner.sys, "stdin", io.StringIO(invalid)), \
                mock.patch.object(runner.sys, "stdout", io.StringIO()), \
                mock.patch.object(runner, "_write_json_line"), \
                mock.patch.object(runner.subprocess, "Popen") as popen:
            self.assertEqual(runner.guardian_main(), 2)
            popen.assert_not_called()

    def test_reconstructed_resource_trigger_boundaries(self):
        self.assertIsNone(runner.resource_stop_reason(89.999, 59_999_999, 90, 60_000_000))
        self.assertEqual(runner.resource_stop_reason(90, 0, 90, 60_000_000), "WALLCLOCK_LIMIT")
        self.assertEqual(runner.resource_stop_reason(0, 60_000_000, 90, 60_000_000), "OUTPUT_SIZE_LIMIT")
        self.assertEqual(runner.resource_stop_reason(90, 60_000_000, 90, 60_000_000), "WALLCLOCK_LIMIT")
        self.assertEqual(runner.resource_stop_reason(0, 0, 90, 60_000_000, True), "LAUNCHER_DISAPPEARED")

    def test_reconstructed_process_group_sigterm_then_sigkill(self):
        process = mock.Mock()
        process.wait.side_effect = [runner.subprocess.TimeoutExpired("mock", 5), 0]
        with mock.patch.object(runner.os, "killpg") as killpg:
            runner.terminate_process_group(1234, process, 5)
        self.assertEqual(killpg.call_args_list,
                         [mock.call(1234, signal.SIGTERM), mock.call(1234, signal.SIGKILL)])
        self.assertEqual(process.wait.call_count, 2)

    def test_reconstructed_output_manifest_inventory_is_deterministic(self):
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory)
            (output / "fcd.xml").write_text("<fcd-export/>\n")
            (output / "extra.bin").write_bytes(b"extra")
            roles = [{"role": "fcd.xml", "kind": "fcd"}, {"role": "tripinfo.xml", "kind": "tripinfo"}]
            first = runner.canonical_json_bytes(runner.build_output_manifest(
                output, roles, "roles.json", "a" * 64, "PAIR_3199_CTRL_S17"))
            second = runner.canonical_json_bytes(runner.build_output_manifest(
                output, roles, "roles.json", "a" * 64, "PAIR_3199_CTRL_S17"))
            self.assertEqual(first, second)
            data = json.loads(first)
            by_role = {item["role"]: item for item in data["artifact_roles"]}
            self.assertEqual(by_role["fcd.xml"]["status"], "PRESENT")
            self.assertEqual(by_role["tripinfo.xml"]["status"], "MISSING")
            self.assertTrue(any(item["relative_path"] == "extra.bin" for item in data["support_files"]))

    def test_legacy_retry_binding_remains_explicit_and_consumed(self):
        legacy = REAL_ROOT / "artifacts/stage6_ramp_induced_validation_20260922_v1/control_card_FINAL_RI3350_CTRL_S17_technical_retry1_REV1.json"
        self.assertEqual(runner.SUPPORTED_RUN_BINDINGS["RI3350_CTRL_S17_technical_retry1"]["kind"], "TECHNICAL_RETRY")
        self.assertEqual(runner.SUPPORTED_RUN_BINDINGS["RI3350_CTRL_S17_technical_retry1"]["card_path"],
                         legacy.relative_to(REAL_ROOT).as_posix())


if __name__ == "__main__":
    unittest.main()

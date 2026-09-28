from __future__ import annotations

import copy
import json
import importlib.util
import shutil
import tempfile
import unittest
import xml.etree.ElementTree as ET
from pathlib import Path

from scripts.stage6.minimal3199.minimal3199_adapter import (
    PACKAGE, ROOT, R02, parse_routes, sha256, validate_file_bindings, validate_pair,
)

_spec = importlib.util.spec_from_file_location("r02_minimal3199_test", R02)
R02_RUNNER = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(R02_RUNNER)


class Minimal3199AdapterTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.manifest = json.loads((PACKAGE / "INPUT_MANIFEST.json").read_text())
        cls.control = PACKAGE / "control/demand.rou.xml"
        cls.treatment = PACKAGE / "treatment/demand.rou.xml"

    def _tmp_pair(self):
        td = tempfile.TemporaryDirectory()
        self.addCleanup(td.cleanup)
        base = Path(td.name)
        c, t = base / "control.rou.xml", base / "treatment.rou.xml"
        shutil.copy2(self.control, c)
        shutil.copy2(self.treatment, t)
        return base, c, t

    def test_exact_pair_m_match_zero_classes_and_R_only(self):
        report = validate_pair(self.control, self.treatment, copy.deepcopy(self.manifest))
        self.assertEqual(report["m_matches"], 1333)
        self.assertEqual(report["control_r_count"], 0)
        self.assertEqual(report["treatment_r_count"], 192)
        self.assertTrue(report["u_x_explicit_zero_both_arms"])

    def test_missing_zero_is_not_accepted_as_zero(self):
        _, _, _ = self._tmp_pair()
        manifest = copy.deepcopy(self.manifest)
        del manifest["class_counts"]["control"]["U"]
        with self.assertRaisesRegex(ValueError, "explicitly PASS_ZERO"):
            validate_pair(self.control, self.treatment, manifest)

    def test_missing_treatment_X_zero_is_not_accepted_as_zero(self):
        manifest = copy.deepcopy(self.manifest)
        del manifest["class_counts"]["treatment"]["X"]
        with self.assertRaisesRegex(ValueError, "explicitly PASS_ZERO"):
            validate_pair(self.control, self.treatment, manifest)

    def test_each_U_X_zero_must_be_explicit_in_both_arms(self):
        for arm in ("control", "treatment"):
            for cls in ("U", "X"):
                with self.subTest(arm=arm, cls=cls):
                    manifest = copy.deepcopy(self.manifest)
                    del manifest["class_counts"][arm][cls]
                    with self.assertRaisesRegex(ValueError, "explicitly PASS_ZERO"):
                        validate_pair(self.control, self.treatment, manifest)

    def test_control_R_zero_must_be_explicit(self):
        manifest = copy.deepcopy(self.manifest)
        del manifest["class_counts"]["control"]["R"]
        with self.assertRaisesRegex(ValueError, "control R must be explicitly PASS_ZERO"):
            validate_pair(self.control, self.treatment, manifest)

    def test_M_speedFactor_mismatch_fails(self):
        _, c, t = self._tmp_pair()
        root = ET.parse(t).getroot()
        target = next(x for x in root.findall("vehicle") if x.get("id") == "M_flow.3")
        target.set("speedFactor", "1.0605")
        ET.ElementTree(root).write(t, encoding="utf-8", xml_declaration=True)
        with self.assertRaisesRegex(ValueError, "M identity/depart/route/type/speedFactor"):
            validate_pair(c, t, copy.deepcopy(self.manifest))

    def test_M_identity_mismatch_fails(self):
        _, c, t = self._tmp_pair()
        root = ET.parse(t).getroot()
        target = next(x for x in root.findall("vehicle") if x.get("id") == "M_flow.3")
        target.set("id", "M_flow.3a")  # Preserve departure ordering while changing one identity.
        ET.ElementTree(root).write(t, encoding="utf-8", xml_declaration=True)
        with self.assertRaisesRegex(ValueError, "M counts or ID sets"):
            validate_pair(c, t, copy.deepcopy(self.manifest))

    def test_M_desired_depart_mismatch_fails(self):
        _, c, t = self._tmp_pair()
        root = ET.parse(t).getroot()
        target = next(x for x in root.findall("vehicle") if x.get("id") == "M_flow.3")
        target.set("depart", f"{float(target.get('depart')) + 0.001:.3f}")
        ET.ElementTree(root).write(t, encoding="utf-8", xml_declaration=True)
        with self.assertRaisesRegex(ValueError, "M identity/depart/route/type/speedFactor"):
            validate_pair(c, t, copy.deepcopy(self.manifest))

    def test_M_route_mismatch_fails(self):
        _, c, t = self._tmp_pair()
        root = ET.parse(t).getroot()
        target = next(x for x in root.findall("vehicle") if x.get("id") == "M_flow.3")
        target.set("route", "R_route")
        ET.ElementTree(root).write(t, encoding="utf-8", xml_declaration=True)
        with self.assertRaisesRegex(ValueError, "M identity/depart/route/type/speedFactor"):
            validate_pair(c, t, copy.deepcopy(self.manifest))

    def test_M_vType_mismatch_fails(self):
        _, c, t = self._tmp_pair()
        root = ET.parse(t).getroot()
        target = next(x for x in root.findall("vehicle") if x.get("id") == "M_flow.3")
        target.set("type", "M_type")
        ET.ElementTree(root).write(t, encoding="utf-8", xml_declaration=True)
        with self.assertRaisesRegex(ValueError, "unresolved route/type"):
            validate_pair(c, t, copy.deepcopy(self.manifest))

    def test_R_in_control_fails(self):
        _, c, t = self._tmp_pair()
        root = ET.parse(c).getroot()
        treatment_root = ET.parse(t).getroot()
        r = next(x for x in treatment_root.findall("vehicle") if x.get("id") == "R_flow.0")
        root.append(copy.deepcopy(r))
        vehicles = [x for x in root if x.tag == "vehicle"]
        vehicles.sort(key=lambda x: (int(float(x.get("depart")) * 1000), x.get("id")))
        for node in vehicles:
            root.remove(node)
        root.extend(vehicles)
        ET.ElementTree(root).write(c, encoding="utf-8", xml_declaration=True)
        with self.assertRaisesRegex(ValueError, "control contains non-M demand"):
            validate_pair(c, t, copy.deepcopy(self.manifest))

    def test_R_treatment_identity_mismatch_fails(self):
        _, c, t = self._tmp_pair()
        root = ET.parse(t).getroot()
        target = next(x for x in root.findall("vehicle") if x.get("id") == "R_flow.0")
        target.set("id", "R_flow.000")
        ET.ElementTree(root).write(t, encoding="utf-8", xml_declaration=True)
        with self.assertRaisesRegex(ValueError, "treatment-only identities must be exactly"):
            validate_pair(c, t, copy.deepcopy(self.manifest))

    def test_R_treatment_schedule_mismatch_fails(self):
        _, c, t = self._tmp_pair()
        root = ET.parse(t).getroot()
        target = next(x for x in root.findall("vehicle") if x.get("id") == "R_flow.1")
        target.set("depart", "545.001")
        ET.ElementTree(root).write(t, encoding="utf-8", xml_declaration=True)
        with self.assertRaisesRegex(ValueError, "R schedule is not exactly"):
            validate_pair(c, t, copy.deepcopy(self.manifest))

    def test_non_R_treatment_difference_fails(self):
        _, c, t = self._tmp_pair()
        root = ET.parse(t).getroot()
        m0 = next(x for x in root.findall("vehicle") if x.get("id") == "M_flow.0")
        extra = copy.deepcopy(m0)
        extra.set("id", "U_flow.0")
        extra.set("route", "U_route")
        root.append(extra)
        ET.ElementTree(root).write(t, encoding="utf-8", xml_declaration=True)
        with self.assertRaises(ValueError):
            validate_pair(c, t, copy.deepcopy(self.manifest))

    def test_unsorted_records_fail(self):
        _, c, t = self._tmp_pair()
        root = ET.parse(t).getroot()
        vehicles = root.findall("vehicle")
        # Put the final/high-time record first, after definitions.
        for node in vehicles:
            root.remove(node)
        root.extend([vehicles[-1], *vehicles[:-1]])
        ET.ElementTree(root).write(t, encoding="utf-8", xml_declaration=True)
        with self.assertRaisesRegex(ValueError, "not globally sorted"):
            validate_pair(c, t, copy.deepcopy(self.manifest))

    def _binding_fixture(self, base: Path):
        runner = base / "runner.py"
        runner.write_text("MINIMAL3199_CTRL_S17 MINIMAL3199_R720_DELAYED_S17\n")
        data = base / "input.dat"
        data.write_text("bound input")
        runtime_ref = base / "runtime.json"
        runtime_ref.write_text("{}\n")
        manifest = {"run_ids": {"control": "MINIMAL3199_CTRL_S17", "treatment": "MINIMAL3199_R720_DELAYED_S17"},
                    "outputs": {"control": "out-a", "treatment": "out-b"},
                    "arm_inputs": {arm: {"demand": {"path": "input.dat", "sha256": sha256(data)}} for arm in ("control", "treatment")},
                    "runner": {"path": "runner.py", "sha256": sha256(runner)}}
        cards = {arm: {"card_status": "DRAFT_NOT_AUTHORIZED", "execution_authorized": False, "run_command": None,
                       "run_id": manifest["run_ids"][arm], "output_directory": manifest["outputs"][arm],
                       "input_sha256": {"demand": sha256(data)}} for arm in ("control", "treatment")}
        runtime = {"freshness_status": "CURRENT_EXACT_CARD_READONLY_VERIFIED", "reference_path": "runtime.json",
                   "reference_sha256": sha256(runtime_ref), "guardian_runner_sha256": sha256(runner)}
        return runner, manifest, cards, runtime

    def test_binding_hash_runtime_and_output_checks(self):
        with tempfile.TemporaryDirectory() as td:
            base = Path(td)
            runner, manifest, cards, runtime = self._binding_fixture(base)
            outputs = (base / "out-a", base / "out-b")
            validate_file_bindings(base, manifest, cards, runtime, runner_path=runner, output_paths=outputs)
            with self.subTest("input hash mismatch"):
                bad = copy.deepcopy(manifest)
                bad["arm_inputs"]["control"]["demand"]["sha256"] = "0" * 64
                with self.assertRaisesRegex(ValueError, "input hash mismatch"):
                    validate_file_bindings(base, bad, cards, runtime, runner_path=runner, output_paths=outputs)
            with self.subTest("runtime hash mismatch"):
                bad_runtime = copy.deepcopy(runtime)
                bad_runtime["guardian_runner_sha256"] = "0" * 64
                with self.assertRaisesRegex(ValueError, "Guardian runner hash"):
                    validate_file_bindings(base, manifest, cards, bad_runtime, runner_path=runner, output_paths=outputs)
            with self.subTest("existing output path"):
                outputs[0].mkdir()
                with self.assertRaisesRegex(ValueError, "output path collision"):
                    validate_file_bindings(base, manifest, cards, runtime, runner_path=runner, output_paths=outputs)

    def test_card_run_id_mismatch_fails(self):
        with tempfile.TemporaryDirectory() as td:
            base = Path(td)
            runner, manifest, cards, runtime = self._binding_fixture(base)
            cards["control"]["run_id"] = "MINIMAL3199_R720_DELAYED_S17"
            with self.assertRaisesRegex(ValueError, "card/run ID mismatch"):
                validate_file_bindings(base, manifest, cards, runtime, runner_path=runner,
                                       output_paths=(base / "out-a", base / "out-b"))

    def test_R02_preflight_is_readonly_and_draft_launch_is_refused(self):
        for run_id in ("MINIMAL3199_CTRL_S17", "MINIMAL3199_R720_DELAYED_S17"):
            card_path = PACKAGE / f"{run_id}_CARD_DRAFT_NOT_AUTHORIZED_REV3.json"
            digest = sha256(card_path)
            with self.assertRaisesRegex(R02_RUNNER.GateError, "CARD_NOT_EXACTLY_AUTHORIZED"):
                R02_RUNNER.verify_card(ROOT, card_path, digest, allow_prelaunch=False)
            # The additive final-control runner revision intentionally makes prior rev3
            # drafts stale; they must fail closed until rebuilt and separately reviewed.
            with self.assertRaisesRegex(R02_RUNNER.GateError, "RUNNER_MANIFEST_HASH_MISMATCH"):
                R02_RUNNER.make_plan(ROOT, card_path, digest)

    def test_R02_card_hash_and_path_mismatch_fail_closed(self):
        card_path = PACKAGE / "MINIMAL3199_CTRL_S17_CARD_DRAFT_NOT_AUTHORIZED_REV3.json"
        with self.assertRaisesRegex(R02_RUNNER.GateError, "APPROVED_CARD_HASH_MISMATCH"):
            R02_RUNNER.make_plan(ROOT, card_path, "0" * 64)
        card = json.loads(card_path.read_text())
        wrong = PACKAGE / "wrong_card.json"
        self.addCleanup(lambda: wrong.unlink(missing_ok=True))
        wrong.write_text(json.dumps(card))
        with self.assertRaisesRegex(R02_RUNNER.GateError, "CARD_PATH_RUN_ID_BINDING_MISMATCH"):
            R02_RUNNER.make_plan(ROOT, wrong, sha256(wrong))

    def test_R02_allows_existing_shared_output_root_but_requires_fresh_arm_path(self):
        with tempfile.TemporaryDirectory() as td:
            repo = Path(td)
            output_root = repo / "data/raw/pair"
            (output_root / "MINIMAL3199_CTRL_S17/outputs").mkdir(parents=True)
            binding = {"output_root": "data/raw/pair",
                       "output_directory": "data/raw/pair/MINIMAL3199_R720_DELAYED_S17/outputs",
                       "kind": "PAIR_RUN"}
            output = R02_RUNNER._validate_minimal3199_output_path(
                repo, binding, binding["output_directory"], {})
            self.assertFalse(output.exists())
            output.mkdir(parents=True)
            with self.assertRaisesRegex(R02_RUNNER.GateError, "OUTPUT_DIRECTORY_ALREADY_EXISTS"):
                R02_RUNNER._validate_minimal3199_output_path(
                    repo, binding, binding["output_directory"], {})


if __name__ == "__main__":
    unittest.main()

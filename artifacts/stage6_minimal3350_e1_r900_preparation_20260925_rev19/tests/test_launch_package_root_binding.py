from __future__ import annotations

import importlib.util
import json
from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[3]
PKG = ROOT / "artifacts/stage6_minimal3350_e1_r900_preparation_20260925_rev19"
RUNNER_PATH = PKG / "r02_single_start/runner.py"
sys.path.insert(0, str(PKG / "r02_single_start"))

spec = importlib.util.spec_from_file_location("rev19_package_root_runner", RUNNER_PATH)
RUNNER = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = RUNNER
spec.loader.exec_module(RUNNER)
from e1_nested_reference_binding import build_and_validate_staged_inputs


class LaunchPackageRootBindingTests(unittest.TestCase):
    def test_reproduces_rev18_missing_artifacts_parent_and_accepts_correct_root(self):
        correct_root = RUNNER.minimal3350_treatment_package_root(ROOT)
        self.assertEqual(correct_root, PKG)
        wrong_rev18_root = ROOT / PKG.name
        self.assertNotEqual(wrong_rev18_root, correct_root)

        roles = json.loads((PKG / "inputs/treatment/output_roles.json").read_text())["required_xml_roles"]
        args = dict(
            repo=ROOT,
            source_cfg=PKG / "inputs/treatment/scenario.sumocfg",
            source_demand=PKG / "inputs/treatment/demand.rou.xml",
            source_additional=PKG / "inputs/treatment/scenario.add.xml",
            network=ROOT / "artifacts/stage6_baseline_localization_20260921_v1/LOC_M3350_S17/engineering/build_attempts/TV_BUILD01/network.net.xml",
            output_directory=ROOT / "data/raw/stage6_minimal3350_ux0_20260925_v19/MINIMAL3350_E1_R900_DELAYED_S17_TECH_RETRY2/outputs",
            roles=roles,
        )
        with self.assertRaises(FileNotFoundError):
            build_and_validate_staged_inputs(package_root=wrong_rev18_root, **args)

        card = json.loads((PKG / "MINIMAL3350_E1_R900_DELAYED_S17_TECH_RETRY2_CARD_FINAL_REV1.json").read_text())
        files = {
            "sumocfg": args["source_cfg"], "demand": args["source_demand"],
            "additional": args["source_additional"], "network": args["network"],
            "output_roles": roles,
            "staged_preview_paths": {
                "sumocfg": PKG / "staging_preview/scenario_control.sumocfg",
                "additional": PKG / "staging_preview/scenario_control.add.xml",
            },
        }
        self.assertEqual(RUNNER.minimal3350_treatment_package_root(ROOT), correct_root)
        cfg_bytes, additional_bytes, closure = RUNNER.build_minimal3350_launch_staged_inputs(
            ROOT, card, files, args["output_directory"])
        self.assertTrue(cfg_bytes)
        self.assertTrue(additional_bytes)
        self.assertEqual(closure["configured_unique_paths"], 20)
        self.assertFalse(args["output_directory"].exists())


if __name__ == "__main__":
    unittest.main()

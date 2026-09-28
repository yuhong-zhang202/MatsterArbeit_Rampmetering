"""Read-only preflight tests; no SUMO process is started."""

from __future__ import annotations

import json
import os
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest
from unittest.mock import patch

from src.scenarios import fullnet_abc_rebuild as rebuild
from src.scenarios import fullnet_abc_single_start as runner


class FullnetAbcSingleStartTests(unittest.TestCase):
    def _package_and_card(self, base: Path) -> tuple[Path, Path, Path]:
        package = base / "package"
        raw = base / "raw"
        rebuild.build(package, raw, speed_seed=170026, mean=1.0,
                      deviation=0.1, minimum=0.2, maximum=2.0,
                      source_note="reviewed prospective speed-factor specification")
        card = {
            "schema_version": "2", "run_id": "MATCHED_R0_S17", "arm": "R0",
            "package_dir": str(package), "raw_root": str(raw),
            "package_manifest_sha256": rebuild.digest(package / "INPUT_MANIFEST.json"),
            "input_sha256": {
                "demand": rebuild.digest(package / "R0/demand.rou.xml"),
                "additional": rebuild.digest(package / "R0/scenario.add.xml"),
                "sumocfg": rebuild.digest(package / "R0/scenario.sumocfg"),
            },
            "network_sha256": "887c232483f0c68dc024334ff5997250d7d36299ab2744bdcf49d5a314c700ca",
            "sumo_sha256": runner.SUMO_SHA256,
            "sumo_home": str(runner.SUMO_HOME),
            "additional_schema_sha256": runner.ADDITIONAL_SCHEMA_SHA256,
            "routes_schema_sha256": runner.ROUTES_SCHEMA_SHA256,
            "runner_sha256": rebuild.digest(Path(runner.__file__)),
            "runner_version": runner.RUNNER_VERSION,
            "max_runtime_s": 120, "max_output_bytes": 100_000_000, "poll_ms": 100,
            "design_review_status": "PASS_FOR_EXPLORATORY_PRELAUNCH_DESIGN",
        }
        card_path = base / "card.json"
        card_path.write_text(json.dumps(card))
        return package, raw, card_path

    def test_exact_card_static_preflight_and_replay_gate(self) -> None:
        with TemporaryDirectory() as temporary:
            base = Path(temporary)
            package, raw, card_path = self._package_and_card(base)
            package = package.resolve(strict=True)
            raw = raw.resolve(strict=False)
            actual_descendant = runner._descendant

            def temp_layout(path: Path, root: Path) -> bool:
                if root == rebuild.ROOT / "artifacts":
                    return path == package
                if root == rebuild.ROOT / "data/raw":
                    return path == raw
                return actual_descendant(path, root)

            with patch.object(runner, "_descendant", side_effect=temp_layout):
                result = runner.preflight(card_path, rebuild.digest(card_path))
                self.assertEqual(result["status"], "PREFLIGHT_PASS_NO_PROCESS_STARTED")
                self.assertEqual(result["sumo_home_for_child"], str(runner.SUMO_HOME))
                self.assertFalse(raw.exists())
                (package / "reservations").mkdir()
                (package / "reservations/MATCHED_R0_S17.json").write_text("{}")
                with self.assertRaisesRegex(runner.GateError, "already consumed"):
                    runner.preflight(card_path, rebuild.digest(card_path))

    def test_wrong_card_hash_or_resource_contract_blocked(self) -> None:
        with TemporaryDirectory() as temporary:
            base = Path(temporary)
            _, _, card_path = self._package_and_card(base)
            with self.assertRaisesRegex(runner.GateError, "hash or file mismatch"):
                runner.preflight(card_path, "0" * 64)
            card = json.loads(card_path.read_text())
            card["max_output_bytes"] = 100_000_001
            card_path.write_text(json.dumps(card))
            with self.assertRaisesRegex(runner.GateError, "resource contract mismatch"):
                runner.preflight(card_path, rebuild.digest(card_path))

    def test_wrong_schema_or_runner_binding_rejected_before_start(self) -> None:
        with TemporaryDirectory() as temporary:
            base = Path(temporary)
            _, _, card_path = self._package_and_card(base)
            card = json.loads(card_path.read_text())
            card["additional_schema_sha256"] = "0" * 64
            card_path.write_text(json.dumps(card))
            with self.assertRaisesRegex(runner.GateError, "schema binding mismatch"):
                runner.preflight(card_path, rebuild.digest(card_path))
            card["additional_schema_sha256"] = runner.ADDITIONAL_SCHEMA_SHA256
            card["runner_sha256"] = "0" * 64
            card_path.write_text(json.dumps(card))
            with self.assertRaisesRegex(runner.GateError, "runner version or hash mismatch"):
                runner.preflight(card_path, rebuild.digest(card_path))

    def test_failed_process_consumes_start_and_writes_receipts(self) -> None:
        class FakeProcess:
            pid = 123456
            returncode = 7

            def poll(self) -> int:
                return self.returncode

            def wait(self) -> int:
                return self.returncode

        with TemporaryDirectory() as temporary:
            base = Path(temporary).resolve(strict=True)
            package, raw, card_path = self._package_and_card(base)
            planned = {
                "status": "PREFLIGHT_PASS_NO_PROCESS_STARTED", "run_id": "MATCHED_R0_S17", "arm": "R0",
                "card_sha256": rebuild.digest(card_path), "card_path": str(card_path),
                "package_dir": str(package), "output_dir": str(raw / "R0/outputs"),
                "reservation": str(package / "reservations/MATCHED_R0_S17.json"),
            }
            with patch.dict(os.environ, {"SUMO_HOME": "/incorrect/SUMO_HOME"}), patch.object(
                runner, "preflight", return_value=planned
            ), patch.object(
                runner.subprocess, "Popen", return_value=FakeProcess()
            ) as spawned:
                receipt = runner.launch(card_path, rebuild.digest(card_path))
            self.assertEqual(receipt["status"], "FAILED")
            self.assertEqual(receipt["return_code"], 7)
            self.assertFalse(receipt["retry_allowed"])
            self.assertTrue((package / "run_receipts/MATCHED_R0_S17.json").is_file())
            self.assertTrue((raw / "R0/outputs/execution_receipt.json").is_file())
            reservation = json.loads((package / "reservations/MATCHED_R0_S17.json").read_text())
            self.assertEqual(reservation["final_status"], "FAILED")
            spawned.assert_called_once()
            self.assertEqual(spawned.call_args.kwargs["env"]["SUMO_HOME"], str(runner.SUMO_HOME))
            self.assertEqual(receipt["sumo_home_for_child"], str(runner.SUMO_HOME))


if __name__ == "__main__":
    unittest.main()

"""Read-only and mocked one-use gates; no SUMO process is started."""

from __future__ import annotations

import json
import os
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest
from unittest.mock import patch

from src.scenarios import fullnet_rebalanced28_build as builder
from src.scenarios import fullnet_rebalanced28_single_start as runner


class Rebalanced28SingleStartTests(unittest.TestCase):
    def _fixture(self, base: Path) -> tuple[Path, Path, Path]:
        artifact_root = base / "artifacts"
        artifact_root.mkdir()
        package = artifact_root / "inputs"
        raw = base / "raw"
        with patch.object(builder, "ARTIFACT_ROOT", artifact_root), patch.object(builder, "RAW_ROOT", raw):
            builder.build(package, raw)
        arm_dir = package / builder.ARM
        card = {
            "schema_version": runner.SCHEMA_VERSION, "run_id": builder.RUN_ID, "arm": builder.ARM,
            "package_dir": str(package), "raw_root": str(raw),
            "package_manifest_sha256": builder.digest(package / "INPUT_MANIFEST.json"),
            "input_sha256": {"demand": builder.digest(arm_dir / "demand.rou.xml"),
                             "additional": builder.digest(arm_dir / "scenario.add.xml"),
                             "sumocfg": builder.digest(arm_dir / "scenario.sumocfg")},
            "base_manifest_sha256": builder.BASE_MANIFEST_SHA256,
            "a_receipt_sha256": builder.digest(runner.A_RECEIPT),
            "network_sha256": runner.NETWORK_SHA256, "sumo_sha256": runner.SUMO_SHA256,
            "sumo_home": str(runner.SUMO_HOME),
            "additional_schema_sha256": runner.ADDITIONAL_SCHEMA_SHA256,
            "routes_schema_sha256": runner.ROUTES_SCHEMA_SHA256,
            "runner_sha256": builder.digest(Path(runner.__file__)),
            "runner_version": runner.RUNNER_VERSION,
            "max_runtime_s": 120, "max_output_bytes": 100_000_000, "poll_ms": 100,
            "design_review_status": runner.DESIGN_REVIEW_STATUS,
        }
        card_path = base / "card.json"
        card_path.write_text(json.dumps(card))
        return package, raw, card_path

    def test_read_only_preflight_and_consumed_reservation(self) -> None:
        with TemporaryDirectory() as temporary:
            base = Path(temporary).resolve()
            package, raw, card_path = self._fixture(base)
            with patch.object(builder, "ARTIFACT_ROOT", package.parent), patch.object(builder, "RAW_ROOT", raw):
                result = runner.preflight(card_path, builder.digest(card_path))
                self.assertEqual(result["status"], "PREFLIGHT_PASS_NO_PROCESS_STARTED")
                self.assertEqual(result["output_refs"], 20)
                self.assertFalse(raw.exists())
                (package / "reservations").mkdir()
                (package / "reservations" / f"{builder.RUN_ID}.json").write_text("{}")
                with self.assertRaisesRegex(runner.GateError, "already consumed"):
                    runner.preflight(card_path, builder.digest(card_path))

    def test_card_resource_or_source_tamper_blocks_before_start(self) -> None:
        with TemporaryDirectory() as temporary:
            base = Path(temporary).resolve()
            package, raw, card_path = self._fixture(base)
            with patch.object(builder, "ARTIFACT_ROOT", package.parent), patch.object(builder, "RAW_ROOT", raw):
                with self.assertRaisesRegex(runner.GateError, "hash or file mismatch"):
                    runner.preflight(card_path, "0" * 64)
                card = json.loads(card_path.read_text())
                card["max_runtime_s"] = 121
                card_path.write_text(json.dumps(card))
                with self.assertRaisesRegex(runner.GateError, "resource contract mismatch"):
                    runner.preflight(card_path, builder.digest(card_path))
                card["max_runtime_s"] = 120
                card_path.write_text(json.dumps(card))
                (package / builder.ARM / "scenario.add.xml").write_text("<additional/>")
                with self.assertRaisesRegex(runner.GateError, "hash or file mismatch"):
                    runner.preflight(card_path, builder.digest(card_path))

    def test_mocked_failed_start_consumes_one_use_and_preserves_receipt(self) -> None:
        class FakeProcess:
            pid = 123456
            returncode = 7

            def poll(self) -> int:
                return self.returncode

            def wait(self) -> int:
                return self.returncode

        with TemporaryDirectory() as temporary:
            base = Path(temporary).resolve()
            package, raw, card_path = self._fixture(base)
            with patch.object(builder, "ARTIFACT_ROOT", package.parent), patch.object(builder, "RAW_ROOT", raw), \
                    patch.dict(os.environ, {"SUMO_HOME": "/wrong"}), \
                    patch.object(runner.subprocess, "Popen", return_value=FakeProcess()) as spawned:
                receipt = runner.launch(card_path, builder.digest(card_path))
                self.assertEqual(receipt["status"], "FAILED")
                self.assertEqual(receipt["return_code"], 7)
                self.assertFalse(receipt["retry_allowed"])
                self.assertTrue((package / "run_receipts" / f"{builder.RUN_ID}.json").is_file())
                self.assertTrue((raw / builder.ARM / "outputs/execution_receipt.json").is_file())
                spawned.assert_called_once()
                self.assertEqual(spawned.call_args.kwargs["env"]["SUMO_HOME"], str(runner.SUMO_HOME))


if __name__ == "__main__":
    unittest.main()

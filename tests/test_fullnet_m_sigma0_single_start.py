"""Static card and one-use failure tests; SUMO is never started."""

from __future__ import annotations

import json
import os
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest
from unittest.mock import patch

from src.scenarios import fullnet_m_sigma0_diagnostic as builder
from src.scenarios import fullnet_m_sigma0_single_start as runner


class Sigma0SingleStartTests(unittest.TestCase):
    def _package_card(self, root: Path, arm: str = "R0_SIGMA0") -> tuple[Path, Path, Path]:
        artifact = root / "artifact"
        raw_parent = root / "raw_parent"
        artifact.mkdir()
        raw_parent.mkdir()
        package, raw = artifact / "inputs", raw_parent / "sigma0_raw"
        with patch.object(builder, "ARTIFACT_ROOT", artifact), patch.object(builder, "RAW_PARENT", raw_parent):
            builder.build(package, raw)
        card = {"schema_version": "sigma0-diagnostic-1", "run_id": runner.RUN_IDS[arm],
                "arm": arm, "package_dir": str(package), "raw_root": str(raw),
                "package_manifest_sha256": builder.digest(package / "INPUT_MANIFEST.json"),
                "input_sha256": {role: builder.digest(package / arm / filename)
                                 for role, filename in (("demand", "demand.rou.xml"),
                                                        ("additional", "scenario.add.xml"),
                                                        ("sumocfg", "scenario.sumocfg"))},
                "base_manifest_sha256": builder.BASE_MANIFEST_SHA256,
                "network_sha256": runner.NETWORK_SHA256,
                "sumo_sha256": runner.SUMO_SHA256, "sumo_home": str(runner.SUMO_HOME),
                "additional_schema_sha256": runner.ADDITIONAL_SCHEMA_SHA256,
                "routes_schema_sha256": runner.ROUTES_SCHEMA_SHA256,
                "runner_sha256": builder.digest(Path(runner.__file__)),
                "runner_version": runner.RUNNER_VERSION,
                "max_runtime_s": 120, "max_output_bytes": 100_000_000, "poll_ms": 100,
                "design_review_status": "PASS_PLAN_ONLY"}
        card_path = root / "card.json"
        card_path.write_text(json.dumps(card))
        return package, raw, card_path

    def _preflight(self, package: Path, raw: Path, card: Path) -> dict:
        with patch.object(builder, "ARTIFACT_ROOT", package.parent), patch.object(builder, "RAW_PARENT", raw.parent):
            return runner.preflight(card, builder.digest(card))

    def test_preflight_and_consumed_reservation(self) -> None:
        with TemporaryDirectory() as temp:
            package, raw, card = self._package_card(Path(temp).resolve())
            result = self._preflight(package, raw, card)
            self.assertEqual(result["status"], "PREFLIGHT_PASS_NO_PROCESS_STARTED")
            self.assertFalse(raw.exists())
            reservation = package / "reservations" / f"{runner.RUN_IDS['R0_SIGMA0']}.json"
            reservation.parent.mkdir()
            reservation.write_text("{}")
            with self.assertRaisesRegex(runner.GateError, "already consumed"):
                self._preflight(package, raw, card)

    def test_tampered_card_or_demand_fails_before_start(self) -> None:
        with TemporaryDirectory() as temp:
            package, raw, card = self._package_card(Path(temp).resolve())
            with self.assertRaisesRegex(runner.GateError, "hash or file mismatch"):
                with patch.object(builder, "ARTIFACT_ROOT", package.parent), patch.object(builder, "RAW_PARENT", raw.parent):
                    runner.preflight(card, "0" * 64)
            demand = package / "R0_SIGMA0/demand.rou.xml"
            demand.write_text(demand.read_text().replace("sigma=\"0\"", "sigma=\"0.1\"", 1))
            with self.assertRaisesRegex(runner.GateError, "hash or file mismatch"):
                self._preflight(package, raw, card)

    def test_unreviewed_status_is_rejected(self) -> None:
        with TemporaryDirectory() as temp:
            package, raw, card = self._package_card(Path(temp).resolve())
            data = json.loads(card.read_text())
            data["design_review_status"] = "PASS_FOR_EXPLORATORY_PRELAUNCH_DESIGN"
            card.write_text(json.dumps(data))
            with self.assertRaisesRegex(runner.GateError, "plan review status mismatch"):
                self._preflight(package, raw, card)

    def test_a_requires_completed_hash_bound_r0_receipt(self) -> None:
        with TemporaryDirectory() as temp:
            package, raw, card = self._package_card(Path(temp).resolve(), "A_SIGMA0")
            data = json.loads(card.read_text())
            data["r0_receipt_sha256"] = "0" * 64
            card.write_text(json.dumps(data))
            with self.assertRaisesRegex(runner.GateError, "hash or file mismatch"):
                self._preflight(package, raw, card)

    def test_failed_child_consumes_once_preserves_receipts_and_env(self) -> None:
        class FakeProcess:
            pid = 123456
            returncode = 1

            def poll(self) -> int:
                return self.returncode

            def wait(self) -> int:
                return self.returncode

        with TemporaryDirectory() as temp:
            package, raw, card = self._package_card(Path(temp).resolve())
            with patch.object(builder, "ARTIFACT_ROOT", package.parent), patch.object(builder, "RAW_PARENT", raw.parent), \
                 patch.dict(os.environ, {"SUMO_HOME": "/wrong"}), \
                 patch.object(runner.subprocess, "Popen", return_value=FakeProcess()) as spawned:
                receipt = runner.launch(card, builder.digest(card))
            self.assertEqual(receipt["status"], "FAILED")
            self.assertEqual(receipt["return_code"], 1)
            self.assertFalse(receipt["retry_allowed"])
            self.assertEqual(spawned.call_args.kwargs["env"]["SUMO_HOME"], str(runner.SUMO_HOME))
            self.assertTrue((raw / "R0_SIGMA0/outputs/execution_receipt.json").is_file())
            self.assertTrue((package / "run_receipts" / f"{runner.RUN_IDS['R0_SIGMA0']}.json").is_file())
            reservation = json.loads((package / "reservations" / f"{runner.RUN_IDS['R0_SIGMA0']}.json").read_text())
            self.assertEqual(reservation["final_status"], "FAILED")


if __name__ == "__main__":
    unittest.main()

from __future__ import annotations

import importlib.util
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[3]
PKG = ROOT / "artifacts/stage6_minimal3350_e1_r900_preparation_20260925_rev20"
RUNNER_PATH = PKG / "r02_single_start/runner.py"
spec = importlib.util.spec_from_file_location("rev20_lifecycle_runner", RUNNER_PATH)
RUNNER = importlib.util.module_from_spec(spec)
assert spec and spec.loader
spec.loader.exec_module(RUNNER)


class LaunchStagingLifecycleTests(unittest.TestCase):
    def test_reproduces_rev19_duplicate_exclusive_add_write(self):
        cfg = b"<configuration />"
        add = b"<additional />"
        with tempfile.TemporaryDirectory() as temp:
            output = Path(temp) / "legacy_output"
            output.mkdir()
            add_path = output / "scenario_control.add.xml"
            cfg_path = output / "scenario_control.sumocfg"
            RUNNER._write_exclusive(add_path, add)
            RUNNER._write_exclusive(cfg_path, cfg)
            with self.assertRaises(FileExistsError):
                RUNNER._write_exclusive(add_path, add)

    def test_corrected_lifecycle_writes_each_file_once_and_fails_closed_on_reuse(self):
        cfg = b"<configuration />"
        add = b"<additional />"
        with tempfile.TemporaryDirectory() as temp:
            output = Path(temp) / "fresh_output"
            original = RUNNER._write_exclusive
            calls: list[Path] = []

            def counted(path: Path, data: bytes) -> None:
                calls.append(path)
                original(path, data)

            with patch.object(RUNNER, "_write_exclusive", side_effect=counted):
                cfg_path, add_path = RUNNER.stage_launch_output_files(output, cfg, add)
            self.assertEqual(calls, [add_path, cfg_path])
            self.assertEqual(add_path.read_bytes(), add)
            self.assertEqual(cfg_path.read_bytes(), cfg)
            with self.assertRaises(FileExistsError):
                RUNNER.stage_launch_output_files(output, cfg, add)

    def test_precreated_nonempty_output_fails_closed_before_file_writes(self):
        with tempfile.TemporaryDirectory() as temp:
            output = Path(temp) / "precreated"
            output.mkdir()
            (output / "scenario_control.add.xml").write_bytes(b"stale")
            with self.assertRaises(RUNNER.GateError):
                RUNNER.stage_launch_output_files(
                    output, b"<configuration />", b"<additional />",
                    output_directory_precreated=True)
            self.assertEqual((output / "scenario_control.add.xml").read_bytes(), b"stale")
            self.assertFalse((output / "scenario_control.sumocfg").exists())


if __name__ == "__main__":
    unittest.main()

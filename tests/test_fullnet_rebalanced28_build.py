"""Offline checks for the one-candidate B_REBALANCED28 package."""

from __future__ import annotations

import json
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest
from unittest.mock import patch
import xml.etree.ElementTree as ET

from src.scenarios import fullnet_rebalanced28_build as builder


class Rebalanced28BuildTests(unittest.TestCase):
    def test_demand_is_byte_identical_and_only_new_ramp_program_selected(self) -> None:
        with TemporaryDirectory() as temporary:
            root = Path(temporary).resolve()
            artifact_root = root / "artifacts"
            artifact_root.mkdir()
            package = artifact_root / "inputs"
            raw = root / "raw"
            with patch.object(builder, "ARTIFACT_ROOT", artifact_root), patch.object(builder, "RAW_ROOT", raw):
                result = builder.build(package, raw)
                self.assertEqual(result["status"], "REBALANCED28_STATIC_EQUIVALENCE_PASS_NO_SUMO_STARTED")
                self.assertFalse(raw.exists())
                self.assertEqual((package / builder.ARM / "demand.rou.xml").read_bytes(),
                                 (builder.BASE / "A/demand.rou.xml").read_bytes())
                new_add = ET.parse(package / builder.ARM / "scenario.add.xml").getroot()
                source_add = ET.parse(builder.BASE / "A/scenario.add.xml").getroot()
                self.assertEqual(new_add.find("WAUT").get("startProg"), builder.ARM)
                self.assertEqual(source_add.find("WAUT").get("startProg"), "A_OPEN")
                programs = new_add.findall("tlLogic")
                self.assertEqual(len(programs), 1)
                self.assertEqual(programs[0].get("id"), "ramp_mid")
                self.assertEqual([(p.get("duration"), p.get("state")) for p in programs[0].findall("phase")],
                                 [("28", "G"), ("3", "y"), ("29", "r")])
                self.assertEqual(builder.audit(package, raw)["counts"],
                                 {"M": 1396, "R": 240, "U": 150, "X": 75})
                manifest = json.loads((package / "INPUT_MANIFEST.json").read_text())
                self.assertEqual(manifest["raw_root"], str(raw))
                self.assertEqual(manifest["files"][f"{builder.ARM}/demand.rou.xml"],
                                 builder.digest(builder.BASE / "A/demand.rou.xml"))
                with self.assertRaises(FileExistsError):
                    builder.build(package, raw)

    def test_tampered_signal_fails_static_audit(self) -> None:
        with TemporaryDirectory() as temporary:
            root = Path(temporary).resolve()
            artifact_root = root / "artifacts"
            artifact_root.mkdir()
            package = artifact_root / "inputs"
            raw = root / "raw"
            with patch.object(builder, "ARTIFACT_ROOT", artifact_root), patch.object(builder, "RAW_ROOT", raw):
                builder.build(package, raw)
                path = package / builder.ARM / "scenario.add.xml"
                path.write_text(path.read_text().replace('duration="28"', 'duration="27"'))
                with self.assertRaisesRegex(ValueError, "unexpected new arm content"):
                    builder.audit(package, raw)


if __name__ == "__main__":
    unittest.main()

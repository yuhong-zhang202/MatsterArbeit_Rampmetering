"""Offline checks for the one-candidate B22_SIGMA0 package."""

from __future__ import annotations

import json
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest
from unittest.mock import patch
import xml.etree.ElementTree as ET

from src.scenarios import fullnet_b22_sigma0_build as builder


class B22Sigma0BuildTests(unittest.TestCase):
    def test_demand_is_byte_identical_and_only_new_ramp_program_selected(self) -> None:
        with TemporaryDirectory() as temporary:
            root = Path(temporary).resolve()
            artifact_root = root / "artifacts"
            artifact_root.mkdir()
            package = artifact_root / "inputs"
            raw = root / "raw"
            with patch.object(builder, "ARTIFACT_ROOT", artifact_root), patch.object(builder, "RAW_ROOT", raw):
                result = builder.build(package, raw)
                self.assertEqual(result["status"], "B22_SIGMA0_STATIC_EQUIVALENCE_PASS_NO_SUMO_STARTED")
                self.assertFalse(raw.exists())
                self.assertEqual((package / builder.ARM / "demand.rou.xml").read_bytes(),
                                 (builder.BASE / "A_SIGMA0/demand.rou.xml").read_bytes())
                new_add = ET.parse(package / builder.ARM / "scenario.add.xml").getroot()
                source_add = ET.parse(builder.BASE / "A_SIGMA0/scenario.add.xml").getroot()
                self.assertEqual(new_add.find("WAUT").get("startProg"), "B_MODERATE")
                self.assertEqual(source_add.find("WAUT").get("startProg"), "A_OPEN")
                programs = new_add.findall("tlLogic")
                self.assertEqual(len(programs), 0)  # 22G program is in the unchanged compiled network
                self.assertEqual(builder.audit(package, raw)["counts"],
                                 {"M": 1396, "R": 240, "U": 150, "X": 75})
                manifest = json.loads((package / "INPUT_MANIFEST.json").read_text())
                self.assertEqual(manifest["raw_root"], str(raw))
                self.assertEqual(manifest["files"][f"{builder.ARM}/demand.rou.xml"],
                                 builder.digest(builder.BASE / "A_SIGMA0/demand.rou.xml"))
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
                path.write_text(path.read_text().replace('startProg="B_MODERATE"', 'startProg="A_OPEN"'))
                with self.assertRaisesRegex(ValueError, "unexpected new arm content"):
                    builder.audit(package, raw)


if __name__ == "__main__":
    unittest.main()

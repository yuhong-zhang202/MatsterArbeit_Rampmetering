"""Offline regression checks for the prospective full-network input package."""

from __future__ import annotations

import json
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest
import xml.etree.ElementTree as ET

from src.scenarios import fullnet_abc_rebuild as rebuilder


class FullnetAbcRebuildTests(unittest.TestCase):
    def test_matched_symbolic_requested_inputs_and_provenance(self) -> None:
        with TemporaryDirectory() as temporary:
            base = Path(temporary)
            package = base / "package"
            raw = base / "raw"
            report = rebuilder.build(package, raw, speed_seed=170026, mean=1.0,
                                     deviation=0.1, minimum=0.2, maximum=2.0,
                                     source_note="SUMO 1.26 passenger default normc(1,0.1,0.2,2)")
            self.assertEqual(report["status"], "STATIC_INPUT_EQUIVALENCE_PASS_NO_SUMO_STARTED")
            self.assertEqual(report["counts"]["R0"], {"M": 1396, "R": 0, "U": 150, "X": 75})
            self.assertEqual(report["counts"]["A"], {"M": 1396, "R": 240, "U": 150, "X": 75})
            demand = ET.parse(package / "A/demand.rou.xml").getroot()
            records = {node.get("id"): node for node in demand.findall("vehicle")}
            self.assertEqual(records["U_flow.1"].get("departPos"), "last")
            self.assertEqual(records["U_flow.1"].get("departLane"), "best")
            self.assertEqual(records["U_flow.1"].get("departSpeed"), "max")
            self.assertEqual(records["M_flow.502"].get("depart"), "539.148")
            self.assertEqual(records["R_flow.239"].get("depart"), "1496.000")
            self.assertEqual(len(records["R_flow.239"].get("speedFactor").split(".")[1]), 10)
            manifest = json.loads((package / "INPUT_MANIFEST.json").read_text())
            self.assertEqual(manifest["speed_factor_generation"]["seed"], 170026)
            self.assertEqual(len(manifest["files"]), 13)  # 12 XML + static audit
            self.assertFalse(raw.exists())
            with self.assertRaises(FileExistsError):
                rebuilder.build(package, raw, speed_seed=170026, mean=1.0,
                                deviation=0.1, minimum=0.2, maximum=2.0,
                                source_note="already built")

    def test_numeric_departure_semantics_fail_static_audit(self) -> None:
        with TemporaryDirectory() as temporary:
            base = Path(temporary)
            package = base / "package"
            rebuilder.build(package, base / "raw", speed_seed=170026, mean=1.0,
                            deviation=0.1, minimum=0.2, maximum=2.0,
                            source_note="SUMO 1.26 passenger default")
            target = package / "A/demand.rou.xml"
            tree = ET.parse(target)
            tree.getroot().find("vehicle[@id='U_flow.1']").set("departSpeed", "14.0817")
            tree.write(target, encoding="utf-8", xml_declaration=True)
            with self.assertRaisesRegex(ValueError, "departure rule"):
                rebuilder._audit(package)


if __name__ == "__main__":
    unittest.main()

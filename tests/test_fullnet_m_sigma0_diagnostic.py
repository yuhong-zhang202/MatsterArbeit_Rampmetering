"""Offline regression tests for M-only sigma=0 diagnostic inputs."""

from __future__ import annotations

import json
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest
from unittest.mock import patch
import xml.etree.ElementTree as ET

from src.scenarios import fullnet_m_sigma0_diagnostic as builder


class Sigma0BuilderTests(unittest.TestCase):
    def _build(self, base: Path) -> tuple[Path, Path]:
        artifact = base / "artifact"
        raw_parent = base / "raw_parent"
        artifact.mkdir()
        raw_parent.mkdir()
        package, raw = artifact / "inputs", raw_parent / "sigma0_raw"
        with patch.object(builder, "ARTIFACT_ROOT", artifact), patch.object(builder, "RAW_PARENT", raw_parent):
            builder.build(package, raw)
        return package, raw

    def test_two_arm_only_m_type_changes_and_source_bound(self) -> None:
        with TemporaryDirectory() as temp:
            package, raw = self._build(Path(temp))
            with patch.object(builder, "ARTIFACT_ROOT", package.parent), patch.object(builder, "RAW_PARENT", raw.parent):
                audit = builder.audit(package, raw)
            self.assertEqual(audit["counts"], builder.EXPECTED)
            self.assertFalse(raw.exists())
            for arm, source_arm in builder.ARM_SOURCE.items():
                root = ET.parse(package / arm / "demand.rou.xml").getroot()
                types = root.findall("vType")
                self.assertEqual(len(types), 2)
                self.assertEqual(types[0].attrib, {"id": "technical_passenger", "vClass": "passenger"})
                self.assertEqual(types[1].attrib, {"id": builder.M_TYPE, "vClass": "passenger", "sigma": "0"})
                old = {v.get("id"): v for v in ET.parse(builder.BASE / source_arm / "demand.rou.xml").getroot().findall("vehicle")}
                for new in root.findall("vehicle"):
                    attrs = dict(new.attrib)
                    if new.get("id", "").startswith("M_flow."):
                        self.assertEqual(attrs.pop("type"), builder.M_TYPE)
                        attrs["type"] = "technical_passenger"
                    self.assertEqual(attrs, old[new.get("id")].attrib)
            manifest = json.loads((package / "INPUT_MANIFEST.json").read_text())
            self.assertEqual(manifest["base_manifest_sha256"], builder.BASE_MANIFEST_SHA256)
            self.assertEqual(len(manifest["files"]), 7)

    def test_changed_non_m_type_or_demand_fails_static_audit(self) -> None:
        with TemporaryDirectory() as temp:
            package, raw = self._build(Path(temp))
            demand = package / "A_SIGMA0/demand.rou.xml"
            tree = ET.parse(demand)
            tree.getroot().find("vehicle[@id='R_flow.0']").set("type", builder.M_TYPE)
            tree.write(demand, encoding="utf-8", xml_declaration=True)
            with self.assertRaisesRegex(ValueError, "unexpected demand change"):
                builder.audit(package, raw)

    def test_existing_raw_or_package_rejected(self) -> None:
        with TemporaryDirectory() as temp:
            package, raw = self._build(Path(temp))
            with patch.object(builder, "ARTIFACT_ROOT", package.parent), patch.object(builder, "RAW_PARENT", raw.parent):
                with self.assertRaises(FileExistsError):
                    builder.build(package, raw)


if __name__ == "__main__":
    unittest.main()

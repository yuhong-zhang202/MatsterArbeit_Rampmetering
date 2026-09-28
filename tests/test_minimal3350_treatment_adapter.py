from __future__ import annotations

import importlib.util
import json
from pathlib import Path
import tempfile
import unittest
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
ADAPTER = ROOT / "scripts/stage6/minimal3350/minimal3350_treatment_adapter.py"
CONTROL = ROOT / "artifacts/stage6_minimal3350_control_preparation_20260924_rev8/inputs/control/demand.rou.xml"
COMMON = ROOT / "artifacts/stage6_minimal3350_control_preparation_20260924_rev8/COMMON_M_DEMAND_MANIFEST.json"
RSOURCE = ROOT / "scripts/stage6/minimal3199/prepared_rev3/treatment/demand.rou.xml"
COMMON_SHA = "2fb1383e709e2174e2623aae575649aba40937729325a5e9c43bcc2b76982865"

spec = importlib.util.spec_from_file_location("minimal3350_treatment_adapter_test", ADAPTER)
adapter = importlib.util.module_from_spec(spec)
assert spec and spec.loader
spec.loader.exec_module(adapter)


class Minimal3350TreatmentAdapterTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.dest = Path(self.tmp.name) / "demand.rou.xml"
        adapter.materialize_treatment_demand(CONTROL, RSOURCE, self.dest)
        self.card = {
            "common_m_manifest": {"path": "unused", "sha256": COMMON_SHA},
            "r_vehicle_source": {"path": adapter.R_SOURCE_REL, "sha256": adapter.sha256(RSOURCE)},
        }

    def tearDown(self):
        self.tmp.cleanup()

    def validate(self, path=None, card=None):
        return adapter.validate_treatment_card(card or self.card, path or self.dest,
                                               COMMON, RSOURCE, ROOT, CONTROL)

    def mutate(self, fn):
        root = ET.parse(self.dest).getroot()
        fn(root)
        path = Path(self.tmp.name) / f"mutated-{len(list(Path(self.tmp.name).glob('mutated-*')))}.xml"
        ET.ElementTree(root).write(path, encoding="utf-8", xml_declaration=True)
        return path

    def test_materialized_treatment_matches_all_1396_m_and_adds_only_r192(self):
        result = self.validate()
        self.assertEqual(result["status"], "PASS")
        self.assertEqual(result["m_exact_matches_control"], 1396)
        self.assertEqual(result["m_exact_matches_common_manifest"], 1396)
        self.assertEqual(result["r_count"], 192)
        self.assertEqual((result["u_count"], result["x_count"]), (0, 0))
        self.assertTrue(result["sorted_by_depart_ms_and_id"])

    def test_rejects_changed_m_speedfactor(self):
        path = self.mutate(lambda root: next(n for n in root if n.get("id") == "M_flow.16").set("speedFactor", "1.0000"))
        with self.assertRaisesRegex(ValueError, "differs from common M manifest"):
            self.validate(path)

    def test_rejects_changed_m_depart(self):
        path = self.mutate(lambda root: next(n for n in root if n.get("id") == "M_flow.16").set("depart", "17.185"))
        with self.assertRaisesRegex(ValueError, "differs from common M manifest"):
            self.validate(path)

    def test_rejects_wrong_m_route(self):
        path = self.mutate(lambda root: next(n for n in root if n.get("id") == "M_flow.16").set("route", "R_route"))
        with self.assertRaisesRegex(ValueError, "differs from common M manifest"):
            self.validate(path)

    def test_rejects_missing_r_identity(self):
        def remove(root): root.remove(next(n for n in root if n.get("id") == "R_flow.191"))
        path = self.mutate(remove)
        with self.assertRaisesRegex(ValueError, "R identity mismatch"):
            self.validate(path)

    def test_rejects_extra_u_even_when_zero_ledger_is_claimed(self):
        def add(root):
            root.append(ET.Element("vehicle", {"id":"U_flow.0","type":"technical_passenger","route":"U_route","depart":"2699.000","departPos":"last","departLane":"best","departSpeed":"max","speedFactor":"1.0000"}))
        path = self.mutate(add)
        with self.assertRaisesRegex(ValueError, "U/X must be explicitly zero"):
            self.validate(path)

    def test_rejects_unsorted_vehicle_records(self):
        def disorder(root):
            nodes=[n for n in root if n.tag=="vehicle"]
            for n in nodes: root.remove(n)
            for n in reversed(nodes): root.append(n)
        path = self.mutate(disorder)
        with self.assertRaisesRegex(ValueError, "globally sorted"):
            self.validate(path)

    def test_rejects_wrong_r_window_or_rate(self):
        card = dict(self.card)
        card["r_vehicle_source"] = dict(self.card["r_vehicle_source"], sha256="0"*64)
        with self.assertRaisesRegex(ValueError, "R source hash mismatch"):
            self.validate(card=card)


if __name__ == "__main__":
    unittest.main()

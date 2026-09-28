import importlib.util
import tempfile
import unittest
import xml.etree.ElementTree as ET
from pathlib import Path


MODULE_PATH = Path(__file__).resolve().parents[1] / "scripts/stage6/pair3199_common_demand.py"
spec = importlib.util.spec_from_file_location("pair3199_common_demand", MODULE_PATH)
module = importlib.util.module_from_spec(spec)
assert spec.loader is not None
spec.loader.exec_module(module)


def write_pair(root: Path, treatment_mutation=None):
    def build(path, treatment=False):
        doc = ET.Element("routes")
        ET.SubElement(doc, "vType", id="technical_passenger", vClass="passenger")
        vehicles = []
        specs = {"M": (1333, 0, 1_500_000), "U": (150, 0, 1_500_000), "X": (75, 0, 1_500_000)}
        for cls, (count, begin, end) in specs.items():
            ET.SubElement(doc, "route", id=f"{cls}_route", edges="a b")
            offset = (end - begin) // count
            for i in range(count):
                attrs = {"id": f"{cls}_flow.{i}", "type": "technical_passenger", "route": f"{cls}_route",
                         "depart": module.ms_text(begin + i * offset), "departPos": "last", "departLane": "best", "departSpeed": "max",
                         "speedFactor": "1.00"}
                vehicles.append(attrs)
        ET.SubElement(doc, "route", id="R_route", edges="r a b")
        if treatment:
            offset = (1_500_000 - 540_000) // 192
            for i in range(192):
                attrs = {"id": f"R_flow.{i}", "type": "technical_passenger", "route": "R_route",
                         "depart": module.ms_text(540_000 + i * offset), "departPos": "last", "departLane": "best", "departSpeed": "max",
                         "speedFactor": "1.00"}
                vehicles.append(attrs)
            if treatment_mutation:
                temp = ET.Element("routes")
                for attrs in vehicles:
                    ET.SubElement(temp, "vehicle", attrs)
                treatment_mutation(temp)
                vehicles = [node.attrib.copy() for node in temp.findall("vehicle")]
        for attrs in sorted(vehicles, key=lambda x: (float(x["depart"]), x["id"])):
            ET.SubElement(doc, "vehicle", attrs)
        ET.ElementTree(doc).write(path, encoding="utf-8", xml_declaration=True)

    c = root / "control.xml"
    t = root / "treatment.xml"
    build(c)
    build(t, True)
    return c, t


class Pair3199CommonDemandTests(unittest.TestCase):
    def test_valid_pair_passes_with_exact_r_only_delta(self):
        with tempfile.TemporaryDirectory() as tmp:
            c, t = write_pair(Path(tmp))
            result = module.check_pair(c, t)
            self.assertEqual(result["status"], "PASS")
            self.assertEqual(result["common_id_matches"], 1558)
            self.assertEqual(result["common_depart_schedule_matches"], 1558)
            self.assertEqual(result["common_route_type_matches"], 1558)
            self.assertEqual(result["common_speedFactor_matches"], 1558)
            self.assertTrue(result["route_definitions_match"])
            self.assertTrue(result["vtype_definitions_match"])
            self.assertTrue(result["checker_fail_closed"])
            self.assertFalse(result["mismatch_detected"])
            self.assertTrue(result["treatment_only_is_R_exactly"])

    def test_speedfactor_mismatch_fails_closed(self):
        def mutate(doc):
            doc.find("vehicle[@id='M_flow.9']").set("speedFactor", "1.01")
        with tempfile.TemporaryDirectory() as tmp:
            c, t = write_pair(Path(tmp), mutate)
            result = module.check_pair(c, t)
            self.assertEqual(result["status"], "FAIL")
            self.assertTrue(result["checker_fail_closed"])
            self.assertTrue(result["mismatch_detected"])

    def test_missing_ux_identity_fails_closed(self):
        with tempfile.TemporaryDirectory() as tmp:
            c, t = write_pair(Path(tmp))
            root = ET.parse(t).getroot()
            root.remove(root.find("vehicle[@id='U_flow.0']"))
            ET.ElementTree(root).write(t, encoding="utf-8", xml_declaration=True)
            result = module.check_pair(c, t)
            self.assertEqual(result["status"], "FAIL")
            self.assertIn("treatment is missing common M/U/X IDs", result["failures"])

    def test_route_edge_definition_mismatch_fails_closed(self):
        with tempfile.TemporaryDirectory() as tmp:
            c, t = write_pair(Path(tmp))
            root = ET.parse(t).getroot()
            root.find("route[@id='M_route']").set("edges", "a changed_edge")
            ET.ElementTree(root).write(t, encoding="utf-8", xml_declaration=True)
            result = module.check_pair(c, t)
            self.assertEqual(result["status"], "FAIL")
            self.assertTrue(result["checker_fail_closed"])
            self.assertIn("complete route definitions (including edge lists and all attributes) differ across arms", result["failures"])

    def test_vtype_attribute_mismatch_fails_closed(self):
        with tempfile.TemporaryDirectory() as tmp:
            c, t = write_pair(Path(tmp))
            root = ET.parse(t).getroot()
            root.find("vType[@id='technical_passenger']").set("vClass", "bus")
            ET.ElementTree(root).write(t, encoding="utf-8", xml_declaration=True)
            result = module.check_pair(c, t)
            self.assertEqual(result["status"], "FAIL")
            self.assertTrue(result["checker_fail_closed"])
            self.assertIn("complete vType definitions (including all attributes) differ across arms", result["failures"])

    def test_missing_explicit_speedfactor_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            c, t = write_pair(Path(tmp))
            root = ET.parse(t).getroot()
            root.find("vehicle[@id='M_flow.0']").attrib.pop("speedFactor")
            ET.ElementTree(root).write(t, encoding="utf-8", xml_declaration=True)
            with self.assertRaisesRegex(ValueError, "missing required or unsupported vehicle attributes"):
                module.check_pair(c, t)

    def test_treatment_only_top_level_flow_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            c, t = write_pair(Path(tmp))
            root = ET.parse(t).getroot()
            ET.SubElement(root, "flow", id="sneaky", type="technical_passenger", route="R_route",
                          begin="540", end="1500", number="192")
            ET.ElementTree(root).write(t, encoding="utf-8", xml_declaration=True)
            with self.assertRaisesRegex(ValueError, "unsupported top-level XML node"):
                module.check_pair(c, t)

    def test_nested_vehicle_param_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            c, t = write_pair(Path(tmp))
            root = ET.parse(t).getroot()
            vehicle = root.find("vehicle[@id='M_flow.0']")
            ET.SubElement(vehicle, "param", key="hiddenBehavior", value="1")
            ET.ElementTree(root).write(t, encoding="utf-8", xml_declaration=True)
            with self.assertRaisesRegex(ValueError, "nested XML elements under vehicle are unsupported"):
                module.check_pair(c, t)

    def test_unlisted_vehicle_attribute_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            c, t = write_pair(Path(tmp))
            root = ET.parse(t).getroot()
            root.find("vehicle[@id='M_flow.0']").set("speedDev", "0.2")
            ET.ElementTree(root).write(t, encoding="utf-8", xml_declaration=True)
            with self.assertRaisesRegex(ValueError, "missing required or unsupported vehicle attributes"):
                module.check_pair(c, t)

    def test_utf16_dtd_default_speedfactor_bypass_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            c, t = write_pair(Path(tmp))
            root = ET.parse(t).getroot()
            root.find("vehicle[@id='M_flow.0']").attrib.pop("speedFactor")
            body = ET.tostring(root, encoding="unicode")
            xml = ('<?xml version="1.0" encoding="UTF-16"?>\n'
                   '<!DOCTYPE routes [<!ATTLIST vehicle speedFactor CDATA "1.00">]>\n'
                   + body)
            t.write_bytes(xml.encode("utf-16"))
            with self.assertRaisesRegex(ValueError, "strict UTF-8"):
                module.check_pair(c, t)

    def test_utf8_dtd_default_speedfactor_rejected_by_parser_callback(self):
        with tempfile.TemporaryDirectory() as tmp:
            c, t = write_pair(Path(tmp))
            root = ET.parse(t).getroot()
            root.find("vehicle[@id='M_flow.0']").attrib.pop("speedFactor")
            body = ET.tostring(root, encoding="unicode")
            xml = ('<?xml version="1.0" encoding="UTF-8"?>\n'
                   '<!DOCTYPE routes [<!ATTLIST vehicle speedFactor CDATA "1.00">]>\n'
                   + body)
            t.write_bytes(xml.encode("utf-8"))
            with self.assertRaisesRegex(ValueError, "unsupported XML DOCTYPE"):
                module.check_pair(c, t)

    def test_utf8_bom_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            c, t = write_pair(Path(tmp))
            t.write_bytes(b"\xef\xbb\xbf" + t.read_bytes())
            with self.assertRaisesRegex(ValueError, "UTF-8 BOM is unsupported"):
                module.check_pair(c, t)


if __name__ == "__main__":
    unittest.main()

import copy, hashlib, importlib.util, json, shutil, tempfile, unittest
from pathlib import Path
import xml.etree.ElementTree as ET

ROOT=Path(__file__).resolve().parents[3]
PKG=ROOT/"artifacts/stage6_clean_onset_3199_r900_preparation_20260925_v1"
CARD_PATH=PKG/"CLEAN3199_A_R900_DELAYED_S17_CARD_DRAFT_NOT_AUTHORIZED_REV1.json"
ADAPTER_PATH=PKG/"tools/candidate_a_binding.py"
spec=importlib.util.spec_from_file_location("candidate_a_binding_tests",ADAPTER_PATH)
adapter=importlib.util.module_from_spec(spec); spec.loader.exec_module(adapter)

def digest(p): return hashlib.sha256(p.read_bytes()).hexdigest()

class CandidateABindingTests(unittest.TestCase):
    def setUp(self):
        self.card=json.loads(CARD_PATH.read_text())
    def test_exact_candidate_passes(self):
        result=adapter.validate_card(self.card,PKG,ROOT)
        self.assertEqual(result["status"],"PASS")
        self.assertTrue(result["M_full_attr_exact"])
        self.assertTrue(result["R_source_full_attr_exact"])
    def _mutant(self, change):
        td=tempfile.TemporaryDirectory()
        root=Path(td.name)
        shutil.copytree(PKG/"inputs",root/"inputs")
        shutil.copy2(PKG/"INPUT_MANIFEST.json",root/"INPUT_MANIFEST.json")
        card=copy.deepcopy(self.card)
        demand=root/"inputs/treatment/demand.rou.xml"
        add=root/"inputs/treatment/scenario.add.xml"
        if change=="duplicate_m":
            doc=ET.parse(demand); r=doc.getroot(); r.append(copy.deepcopy(next(v for v in r.findall("vehicle") if v.get("id","").startswith("M_flow.")))); doc.write(demand,encoding="utf-8",xml_declaration=True)
        elif change=="fractional_m_depart":
            doc=ET.parse(demand); r=doc.getroot(); next(v for v in r.findall("vehicle") if v.get("id")=="M_flow.0").set("depart","0.0005"); doc.write(demand,encoding="utf-8",xml_declaration=True)
        elif change=="r_factor_mismatch":
            doc=ET.parse(demand); r=doc.getroot(); next(v for v in r.findall("vehicle") if v.get("id")=="R_flow.0").set("speedFactor","1.5000"); doc.write(demand,encoding="utf-8",xml_declaration=True)
        elif change=="stale_nested_output":
            text=add.read_text(); add.write_text(text.replace("stage6_clean_onset_3199_ux0_20260925_v1","stage6_minimal3199_existence_20260924_v4"))
        manifest=json.loads((root/"INPUT_MANIFEST.json").read_text())
        manifest["input_sha256"]["demand"]=digest(demand)
        manifest["input_sha256"]["additional"]=digest(add)
        (root/"INPUT_MANIFEST.json").write_text(json.dumps(manifest,indent=2,sort_keys=True)+"\n")
        card["input_sha256"]["demand"]=digest(demand)
        card["input_sha256"]["additional"]=digest(add)
        card["input_manifest_sha256"]=digest(root/"INPUT_MANIFEST.json")
        return td,root,card
    def test_duplicate_M_identity_fails_closed(self):
        td,root,card=self._mutant("duplicate_m")
        with td,self.assertRaises(ValueError): adapter.validate_card(card,root,ROOT)
    def test_fractional_millisecond_M_depart_fails_closed(self):
        td,root,card=self._mutant("fractional_m_depart")
        with td,self.assertRaises(ValueError): adapter.validate_card(card,root,ROOT)
    def test_R_record_must_match_bound_source(self):
        td,root,card=self._mutant("r_factor_mismatch")
        with td,self.assertRaises(ValueError): adapter.validate_card(card,root,ROOT)
    def test_stale_nested_reference_fails_closed(self):
        td,root,card=self._mutant("stale_nested_output")
        with td,self.assertRaises(ValueError): adapter.validate_card(card,root,ROOT)

if __name__=="__main__": unittest.main(verbosity=2)

from __future__ import annotations
import copy, hashlib, importlib.util, json, unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3]
PKG=ROOT/'artifacts/stage6_minimal3350_e1_r900_preparation_20260925_rev17'
CARD_PATH=PKG/'MINIMAL3350_E1_R900_DELAYED_S17_CARD_FINAL_REV1.json'
CARD=json.loads(CARD_PATH.read_text()); RUN_ID=CARD['run_id']
CARD_SHA=hashlib.sha256(CARD_PATH.read_bytes()).hexdigest()
def load(path): return json.loads(Path(path).read_text())
spec=importlib.util.spec_from_file_location('rev17_runner_receipt_test',PKG/'r02_single_start/runner.py')
RUNNER=importlib.util.module_from_spec(spec); spec.loader.exec_module(RUNNER)
RECEIPTS={
 'engineering':load(PKG/'ENGINEERING_PRELAUNCH_REVIEW.json'),
 'data_provenance':load(PKG/'DATA_PROVENANCE_PRELAUNCH_REVIEW.json'),
 'scientific':load(PKG/'SCIENTIFIC_PRELAUNCH_REVIEW.json'),
}
class Rev17ReviewReceiptCompatibilityTests(unittest.TestCase):
    def test_all_three_current_exact_receipts_validate(self):
        for role,receipt in RECEIPTS.items():
            with self.subTest(role=role):
                self.assertTrue(RUNNER.minimal3350_review_receipt_valid(role,receipt,RUN_ID,CARD_SHA,ROOT))
    def test_engineering_receipt_rejects_wrong_card_status_or_findings(self):
        for key,value in [('card_sha256','0'*64),('status','FAIL'),('findings',{'blocker':0,'major':1,'required_minor':0})]:
            bad=copy.deepcopy(RECEIPTS['engineering']); bad[key]=value
            self.assertFalse(RUNNER.minimal3350_review_receipt_valid('engineering',bad,RUN_ID,CARD_SHA,ROOT))
    def test_data_receipt_rejects_missing_or_mismatched_nested_provenance(self):
        bad=copy.deepcopy(RECEIPTS['data_provenance']); bad['bindings'].pop('adapter_sha256')
        self.assertFalse(RUNNER.minimal3350_review_receipt_valid('data_provenance',bad,RUN_ID,CARD_SHA,ROOT))
        bad=copy.deepcopy(RECEIPTS['data_provenance']); bad['bindings']['start_request_sha256']='0'*64
        self.assertFalse(RUNNER.minimal3350_review_receipt_valid('data_provenance',bad,RUN_ID,CARD_SHA,ROOT))
        bad=copy.deepcopy(RECEIPTS['data_provenance']); bad['matched_control_gate']['scientific_disposition']='FAIL'
        self.assertFalse(RUNNER.minimal3350_review_receipt_valid('data_provenance',bad,RUN_ID,CARD_SHA,ROOT))
    def test_scientific_receipt_rejects_wrong_schema_disposition_card_or_findings(self):
        for key,value in [('schema','wrong'),('disposition','FAIL_PRELAUNCH'),('card_sha256','0'*64),('findings',{'blocker':1,'major':0,'required_minor':0})]:
            bad=copy.deepcopy(RECEIPTS['scientific']); bad[key]=value
            self.assertFalse(RUNNER.minimal3350_review_receipt_valid('scientific',bad,RUN_ID,CARD_SHA,ROOT))

    def test_final_sidecar_binds_exact_hashes_of_all_three_receipts(self):
        side=load(PKG/'FINAL_PRELAUNCH_REVIEW_BINDING.json')
        expected={role:hashlib.sha256((PKG/fname).read_bytes()).hexdigest() for role,fname in {
            'engineering':'ENGINEERING_PRELAUNCH_REVIEW.json',
            'data_provenance':'DATA_PROVENANCE_PRELAUNCH_REVIEW.json',
            'scientific':'SCIENTIFIC_PRELAUNCH_REVIEW.json'}.items()}
        self.assertTrue(RUNNER.minimal3350_review_sidecar_valid(side,RUN_ID,CARD_SHA,expected))
        bad=copy.deepcopy(side); bad['review_receipt_sha256']['scientific']='0'*64
        self.assertFalse(RUNNER.minimal3350_review_sidecar_valid(bad,RUN_ID,CARD_SHA,expected))

if __name__=='__main__': unittest.main()

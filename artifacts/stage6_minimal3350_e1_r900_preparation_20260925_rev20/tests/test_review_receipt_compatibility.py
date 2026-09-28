from __future__ import annotations
import copy,hashlib,importlib.util,json,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3]
PKG=ROOT/'artifacts/stage6_minimal3350_e1_r900_preparation_20260925_rev20'
CARD_PATH=PKG/'MINIMAL3350_E1_R900_DELAYED_S17_TECH_RETRY3_CARD_FINAL_REV1.json'
CARD=json.loads(CARD_PATH.read_text());RUN_ID=CARD['run_id'];CARD_SHA=hashlib.sha256(CARD_PATH.read_bytes()).hexdigest()
spec=importlib.util.spec_from_file_location('retry1_review_runner',PKG/'r02_single_start/runner.py');RUNNER=importlib.util.module_from_spec(spec);spec.loader.exec_module(RUNNER)
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def data_receipt():
 control=CARD['matched_control_binding']
 return {
  'schema':'stage6_minimal3350_e1_r900_retry3_data_provenance_prelaunch_review_v1',
  'status':'PASS_DATA_PROVENANCE_PRELAUNCH','run_id':RUN_ID,'package_id':PKG.name,
  'card_sha256':CARD_SHA,'findings':{'blocker':0,'major':0,'required_minor':0},
  'bindings':{
   'card_path':str(CARD_PATH.relative_to(ROOT)),'card_sha256':CARD_SHA,
   'input_manifest_sha256':sha(PKG/'INPUT_MANIFEST.json'),
   'runtime_binding_sha256':sha(PKG/'runtime_binding.json'),
   'runner_sha256':sha(PKG/'r02_single_start/runner.py'),
   'start_request_sha256':sha(PKG/'START_REQUEST.json'),
   'start_request_receipt_sha256':sha(PKG/'START_REQUEST_RECEIPT.json'),
   'provenance_receipt_sha256':sha(PKG/'PROVENANCE_RECEIPT.json'),
   'design_plan_sha256':CARD['design_sha256'],
   'witness_contract_sha256':CARD['witness_contract']['sha256'],
   'adapter_sha256':sha(PKG/'minimal3350_e1_r900_adapter.py')},
  'matched_control_gate':{
   'run_id':control['run_id'],'card_sha256':control['card_sha256'],
   'data_review_sha256':control['data_review_sha256'],'data_review_disposition':'PASS_DATA_LIFECYCLE',
   'data_side_control_category':'LOW_R_BACKGROUND_ACCEPTABLE',
   'scientific_review_sha256':control['scientific_review_sha256'],
   'scientific_disposition':'LOW_R_BACKGROUND_ACCEPTABLE',
   'scientific_findings':{'blocker':0,'major':0,'required_minor':0},
   'output_manifest_sha256':control['output_manifest_sha256'],'result':'PASS_EXACT_BOUND_CONTROL_RECEIPTS'},
  'condition_check':{'qMain_veh_per_h':3350.4,'seed':17,'R_veh_per_h':900,'R_window_s':'[540,1500)',
   'U':0,'X':0,'legacy_clean_high_mobility_screen_required_for_release':False,
   'stage6_exploratory_control_disposition_required_for_release':True,
   'required_exploratory_control_disposition':'LOW_R_BACKGROUND_ACCEPTABLE'}}
class ReviewReceiptTests(unittest.TestCase):
 def test_exact_engineering_and_science_receipts_pass_and_malformed_fail(self):
  receipts={
   'engineering':{'schema':'stage6_minimal3350_e1_r900_retry3_engineering_prelaunch_review_v1','status':'PASS_PRELAUNCH'},
   'scientific':{'schema':'stage6_minimal3350_e1_r900_retry3_scientific_prelaunch_review_v1','disposition':'PASS_PRELAUNCH'}}
  for role,fields in receipts.items():
   rec={**fields,'run_id':RUN_ID,'card_sha256':CARD_SHA,'findings':{'blocker':0,'major':0,'required_minor':0}}
   self.assertTrue(RUNNER.minimal3350_review_receipt_valid(role,rec,RUN_ID,CARD_SHA,ROOT))
   role_status=('status','FAIL') if role=='engineering' else ('disposition','FAIL')
   for key,value in [('schema','wrong'),role_status,('run_id','wrong'),('card_sha256','0'*64),('findings',{'blocker':0,'major':1,'required_minor':0})]:
    bad=copy.deepcopy(rec);bad[key]=value
    self.assertFalse(RUNNER.minimal3350_review_receipt_valid(role,bad,RUN_ID,CARD_SHA,ROOT))
 def test_nested_data_receipt_validates_all_hash_and_condition_bindings(self):
  rec=data_receipt()
  self.assertTrue(RUNNER.minimal3350_review_receipt_valid('data_provenance',rec,RUN_ID,CARD_SHA,ROOT))
  for mutate in (
   lambda x:x['bindings'].pop('adapter_sha256'),
   lambda x:x['bindings'].__setitem__('start_request_sha256','0'*64),
   lambda x:x['matched_control_gate'].__setitem__('scientific_disposition','FAIL'),
   lambda x:x['condition_check'].__setitem__('R_veh_per_h',720),
   lambda x:x.__setitem__('card_sha256','0'*64),
   lambda x:x['findings'].__setitem__('required_minor',1),
  ):
   bad=copy.deepcopy(rec);mutate(bad)
   self.assertFalse(RUNNER.minimal3350_review_receipt_valid('data_provenance',bad,RUN_ID,CARD_SHA,ROOT))
 def test_sidecar_must_bind_all_exact_receipt_hashes(self):
  hashes={'engineering':'a'*64,'data_provenance':'b'*64,'scientific':'c'*64}
  side={'status':'FINAL_PRELAUNCH_REVIEW_GATE_PASS','run_id':RUN_ID,'card_sha256':CARD_SHA,'review_receipt_sha256':hashes}
  self.assertTrue(RUNNER.minimal3350_review_sidecar_valid(side,RUN_ID,CARD_SHA,hashes))
  bad=copy.deepcopy(side);bad['review_receipt_sha256']['scientific']='0'*64
  self.assertFalse(RUNNER.minimal3350_review_sidecar_valid(bad,RUN_ID,CARD_SHA,hashes))
  self.assertFalse(RUNNER.minimal3350_review_sidecar_valid(side,RUN_ID,'0'*64,hashes))
if __name__=='__main__':unittest.main()

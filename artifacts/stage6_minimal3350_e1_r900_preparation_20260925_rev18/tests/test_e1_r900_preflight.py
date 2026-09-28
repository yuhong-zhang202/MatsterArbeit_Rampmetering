from __future__ import annotations
import hashlib,importlib.util,json,unittest
from pathlib import Path
import xml.etree.ElementTree as ET
ROOT=Path(__file__).resolve().parents[3]
PKG=ROOT/'artifacts/stage6_minimal3350_e1_r900_preparation_20260925_rev18'
RUN_ID='MINIMAL3350_E1_R900_DELAYED_S17_TECH_RETRY1'
CARD_PATH=PKG/f'{RUN_ID}_CARD_FINAL_REV1.json'
CARD=json.loads(CARD_PATH.read_text())
CARD_SHA=hashlib.sha256(CARD_PATH.read_bytes()).hexdigest()
def load(name,path):
 spec=importlib.util.spec_from_file_location(name,path);mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod);return mod
ADAPTER=load('retry1_e1_adapter',PKG/'minimal3350_e1_r900_adapter.py')
RUNNER=load('retry1_e1_runner',PKG/'r02_single_start/runner.py')
class E1RetryPreflightTests(unittest.TestCase):
 def test_fixed_scientific_and_common_m_r_identity_vectors(self):
  control=ROOT/CARD['matched_control_binding']['demand_input_path']
  common=ROOT/CARD['common_m_manifest']['path'];rsource=ROOT/CARD['r_vehicle_source']['path'];demand=PKG/'inputs/treatment/demand.rou.xml'
  got=ADAPTER.validate_treatment_card(CARD,demand,common,rsource,ROOT,control)
  self.assertEqual((got['m_count'],got['m_exact_matches'],got['r_count']),(1396,1396,240))
  self.assertEqual(got['r_schedule_ms'],[540000,1496000,4000])
  old=json.loads((ROOT/'artifacts/stage6_minimal3350_e1_r900_preparation_20260925_rev17/MINIMAL3350_E1_R900_DELAYED_S17_CARD_FINAL_REV1.json').read_text())
  for k in ('qMain_veh_per_h','R_veh_per_h','R_window_s','seed','U','X','M_planned_count','TLS_program','witness_contract','matched_control_binding','common_m_manifest'):
   self.assertEqual(CARD[k],old[k],k)
  self.assertEqual(CARD['input_sha256']['demand'],old['input_sha256']['demand'])
  self.assertEqual(CARD['r_vehicle_source']['sha256'],old['r_vehicle_source']['sha256'])
 def test_retry_parent_and_run_identity_are_distinct_and_bound(self):
  self.assertNotEqual(CARD['run_id'],'MINIMAL3350_E1_R900_DELAYED_S17')
  self.assertEqual(CARD['retry_context']['retry_of_card_sha256'],'f0387580053ad6b862ec2874a4eb55e5c9a468a3f23db561af40d6c9e6499908')
  self.assertEqual(RUNNER.verify_card(ROOT,CARD_PATH,CARD_SHA,allow_prelaunch=True)[0]['run_id'],RUN_ID)
 def test_fixed_resource_binding_and_unique_absent_output(self):
  self.assertEqual(CARD['resource_limits']['runtime_s'],120)
  self.assertEqual(CARD['resource_limits']['storage_bytes'],100000000)
  self.assertEqual(CARD['resource_limits']['polling_interval_ms'],100)
  self.assertFalse((ROOT/CARD['output_directory']).exists())
  self.assertFalse((PKG/'r02_single_start/consumption'/f'{RUN_ID}.json').exists())
 def test_three_receipt_schemas_require_exact_card_and_zero_findings(self):
  from test_review_receipt_compatibility import data_receipt
  examples={
   'engineering':{'schema':'stage6_minimal3350_e1_r900_retry1_engineering_prelaunch_review_v1','status':'PASS_PRELAUNCH'},
   'scientific':{'schema':'stage6_minimal3350_e1_r900_retry1_scientific_prelaunch_review_v1','disposition':'PASS_PRELAUNCH'}}
  data=data_receipt()
  self.assertTrue(RUNNER.minimal3350_review_receipt_valid('data_provenance',data,RUN_ID,CARD_SHA,ROOT))
  bad_data=dict(data);bad_data['card_sha256']='0'*64
  self.assertFalse(RUNNER.minimal3350_review_receipt_valid('data_provenance',bad_data,RUN_ID,CARD_SHA,ROOT))
  for role,fields in examples.items():
   rec={**fields,'run_id':RUN_ID,'card_sha256':CARD_SHA,'findings':{'blocker':0,'major':0,'required_minor':0}}
   self.assertTrue(RUNNER.minimal3350_review_receipt_valid(role,rec,RUN_ID,CARD_SHA,ROOT))
   for key,value in [('card_sha256','0'*64),('findings',{'blocker':0,'major':1,'required_minor':0}),
                     ('status','FAIL') if role=='engineering' else ('disposition','FAIL')]:
    bad=dict(rec);bad[key]=value
    self.assertFalse(RUNNER.minimal3350_review_receipt_valid(role,bad,RUN_ID,CARD_SHA,ROOT))
   bad=dict(rec);bad['schema']='wrong'
   self.assertFalse(RUNNER.minimal3350_review_receipt_valid(role,bad,RUN_ID,CARD_SHA,ROOT))
if __name__=='__main__':unittest.main()

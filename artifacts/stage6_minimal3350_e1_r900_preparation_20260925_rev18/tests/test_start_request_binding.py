from __future__ import annotations
import hashlib,importlib.util,json,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3]
PKG=ROOT/'artifacts/stage6_minimal3350_e1_r900_preparation_20260925_rev18'
CARD_PATH=PKG/'MINIMAL3350_E1_R900_DELAYED_S17_TECH_RETRY1_CARD_FINAL_REV1.json'
CARD=json.loads(CARD_PATH.read_text());REQUEST=json.loads((PKG/'START_REQUEST.json').read_text()) if (PKG/'START_REQUEST.json').exists() else None
spec=importlib.util.spec_from_file_location('retry1_start_runner',PKG/'r02_single_start/runner.py');RUNNER=importlib.util.module_from_spec(spec);spec.loader.exec_module(RUNNER)
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
class StartRequestBindingTests(unittest.TestCase):
 def test_start_request_binds_retry_card_runtime_output_and_consumption(self):
  self.assertIsNotNone(REQUEST)
  out=(ROOT/CARD['output_directory']).resolve();cons=PKG/'r02_single_start/consumption'/f"{CARD['run_id']}.json"
  self.assertEqual(REQUEST['run_id'],CARD['run_id'])
  self.assertEqual(REQUEST['card_sha256'],sha(CARD_PATH))
  self.assertEqual(REQUEST['command'][-1],str(out/'scenario_control.sumocfg'))
  self.assertEqual(REQUEST['reservation_path'],str(cons.resolve()))
  self.assertEqual(REQUEST['output_directory'],str(out))
  self.assertEqual(REQUEST['runtime_binding_sha256'],sha(ROOT/CARD['runtime_binding_path']))
  self.assertEqual(REQUEST['runner_sha256'],sha(ROOT/CARD['runner']['path']))
  self.assertEqual((REQUEST['max_runtime_s'],REQUEST['max_output_bytes']),(120,100000000))
 def test_static_preflight_stays_nonlaunchable_until_fresh_reviews(self):
  plan=RUNNER.make_plan(ROOT,CARD_PATH,sha(CARD_PATH))
  self.assertFalse(plan['launchable_now'])
  self.assertEqual(plan['guardian_request_validation']['status'],'PASS')
  self.assertEqual(plan['guardian_request_validation']['persisted_request'],'PASS_UNSENT')
  self.assertEqual(plan['nested_reference_validation']['status'],'PASS')
  self.assertTrue(plan['nested_reference_validation']['validated_actual_staged_bytes'])
  self.assertFalse(plan['simulator_process_started'])
 def test_reject_stale_config_and_reservation_paths(self):
  for field,value in [('command',list(REQUEST['command'])),('reservation_path',str(ROOT/'artifacts/stage6_minimal3350_e1_r900_preparation_20260925_rev17/r02_single_start/consumption/MINIMAL3350_E1_R900_DELAYED_S17.json'))]:
   bad=dict(REQUEST);bad[field]=value
   if field=='command':bad[field][-1]=str(ROOT/'data/raw/stage6_minimal3350_ux0_20260925_v17/MINIMAL3350_E1_R900_DELAYED_S17/outputs/scenario_control.sumocfg')
   with self.assertRaises(RUNNER.GateError):RUNNER.validate_guardian_start_request(bad,ROOT,require_reviews=False)
if __name__=='__main__':unittest.main()

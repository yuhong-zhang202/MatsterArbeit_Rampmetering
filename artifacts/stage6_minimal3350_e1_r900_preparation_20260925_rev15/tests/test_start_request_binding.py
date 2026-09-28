from __future__ import annotations
import hashlib, json, unittest
from pathlib import Path
import importlib.util
ROOT=Path(__file__).resolve().parents[3]
PKG=ROOT/'artifacts/stage6_minimal3350_e1_r900_preparation_20260925_rev15'
CARD_PATH=PKG/'MINIMAL3350_E1_R900_DELAYED_S17_CARD_PRELAUNCH_REV2.json'
CARD=json.loads(CARD_PATH.read_text())
REQUEST=json.loads((PKG/'START_REQUEST.json').read_text())
spec=importlib.util.spec_from_file_location('e1_runner_request_test',PKG/'r02_single_start/runner.py')
RUNNER=importlib.util.module_from_spec(spec); spec.loader.exec_module(RUNNER)
def sha(path): return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def validate(req):
    out=(ROOT/CARD['output_directory']).resolve()
    expected_config=str(out/'scenario_control.sumocfg')
    expected_reservation=str((PKG/'r02_single_start/consumption'/f"{CARD['run_id']}.json").resolve())
    if req['run_id']!=CARD['run_id'] or req['card_path']!=f"artifacts/{PKG.name}/{CARD_PATH.name}" or req['card_sha256']!=sha(CARD_PATH):
        raise ValueError('card/run binding mismatch')
    if req['command'][-1]!=expected_config: raise ValueError('scenario config path mismatch')
    if req['reservation_path']!=expected_reservation: raise ValueError('reservation path mismatch')
    if req['output_directory']!=str(out): raise ValueError('output directory mismatch')
    if req['runner_path']!=CARD['runner']['path'] or req['runner_sha256']!=sha(ROOT/req['runner_path']): raise ValueError('runner binding mismatch')
    if req['runtime_binding_path']!=CARD['runtime_binding_path'] or req['runtime_binding_sha256']!=sha(ROOT/req['runtime_binding_path']): raise ValueError('runtime binding mismatch')
    expected_roles={role['role']:str(out/role['role']) for role in req['output_roles']}
    if len(expected_roles)!=18 or len(req['output_roles'])!=18 or any(r['path']!=expected_roles[r['role']] for r in req['output_roles']): raise ValueError('output role binding mismatch')
    if req['max_runtime_s']!=120 or req['max_output_bytes']!=100_000_000: raise ValueError('resource binding mismatch')
    return True
class StartRequestBindingTests(unittest.TestCase):
    def test_exact_e1_request_paths_and_hashes(self):
        self.assertTrue(validate(REQUEST))
        self.assertIn('/stage6_minimal3350_ux0_20260925_v16/MINIMAL3350_E1_R900_DELAYED_S17/outputs/scenario_control.sumocfg',REQUEST['command'][-1])
        self.assertIn('/stage6_minimal3350_e1_r900_preparation_20260925_rev15/r02_single_start/consumption/MINIMAL3350_E1_R900_DELAYED_S17.json',REQUEST['reservation_path'])
        runtime=CARD['runtime_binding']
        files={'binary':Path(runtime['binary_path']),'sumocfg':Path(REQUEST['command'][-1]),'sumo_home':Path(runtime['sumo_home']),'additional_schema':Path(runtime['additional_schema_path']),'output_roles':REQUEST['output_roles'],'output_role_source_sha256':REQUEST['output_role_source_sha256']}
        output=Path(REQUEST['output_directory']); reservation=Path(REQUEST['reservation_path'])
        rebuilt=RUNNER.build_guardian_start_spec(files,CARD,output,reservation,ROOT,CARD['run_id'],CARD_PATH,sha(CARD_PATH))
        self.assertEqual(RUNNER.canonical_json_bytes(rebuilt),RUNNER.canonical_json_bytes(REQUEST))
    def test_reject_stale_r720_config(self):
        bad=dict(REQUEST); bad['command']=list(REQUEST['command'])
        bad['command'][-1]=str(ROOT/'data/raw/stage6_minimal3350_ux0_20260924_v15/MINIMAL3350_R720_DELAYED_S17/outputs/scenario_control.sumocfg')
        with self.assertRaisesRegex(ValueError,'scenario config path'): validate(bad)
    def test_reject_stale_r720_reservation(self):
        bad=dict(REQUEST)
        bad['reservation_path']=str(ROOT/'artifacts/stage6_minimal3350_r720_treatment_preparation_20260924_rev7/r02_single_start/consumption/MINIMAL3350_R720_DELAYED_S17.json')
        with self.assertRaisesRegex(ValueError,'reservation path'): validate(bad)
    def test_reject_other_e1_binding_mismatch(self):
        for field,value in [('card_sha256','0'*64),('runner_sha256','0'*64),('runtime_binding_sha256','0'*64),('output_directory','/tmp/elsewhere')]:
            with self.subTest(field=field):
                bad=dict(REQUEST); bad[field]=value
                with self.assertRaises(ValueError): validate(bad)
if __name__=='__main__': unittest.main()

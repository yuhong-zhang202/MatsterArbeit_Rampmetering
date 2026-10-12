"""Public read-only frozen WAIT prelaunch source/card/input verification."""
from pathlib import Path
import hashlib,json,re,xml.etree.ElementTree as ET
ROOT=Path(__file__).resolve().parents[3]
TASK=Path('artifacts/candidate_a_native_receiver_wait_20261012_v1');ENG=TASK/'engineering'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def load(p):return json.loads((ROOT/p).read_text())
def check(mapping):
 for n,h in mapping.items():assert sha(ROOT/n)==h,n
 return len(mapping)
def audit():
 p=ROOT/ENG/'INPUT_BINDINGS_V2.json';assert sha(p)=='dd917c8b15fffe39d779cb02ae155f99f8855eb4195e0f76c2f9f59a73f44435';bound=json.loads(p.read_text());assert check(bound['files'])==77
 protected=load('artifacts/candidate_a_a1_contract_20261011_v1/engineering/PROTECTED_BASELINE_SHA256.json')['files'];assert check(protected)==536
 old=load('artifacts/candidate_a_native_budget_cycles_20261012_v1/engineering/INPUT_BINDINGS_V1.json');assert check(old['files'])==59
 run='CA_NATIVE_PHASE_R300_S17_WAIT_DIAG01_V2';cardpath=ENG/'packages'/run/'card.json';card=load(cardpath);assert sha(ROOT/cardpath)=='c6f8574a57396939b1b4be4c119041e78ce1f652050d5a621c6d121d8def10ac'
 check(card['sources_sha256']);check(card['prepared_input_sha256']);check(card['inherited_inputs_sha256'])
 assert card['status']=='PREPARED_NOT_RELEASED' and card['runtime_authorization_generated'] is False
 assert card['baseline_commit']==bound['baseline_commit']=='20e5e83ac059768320cdaa4c815d164e1022de45'
 assert card['resources']=={'wall_limit_s':300,'startup_limit_s':60,'run_limit_bytes':300000000,'minimum_free_bytes':5000000000}
 assert all(type(v) is int for v in card['resources'].values())
 assert card['spec']['end_s']==1272 and card['spec']['first_red_mandatory_checkpoint_s']==1207 and card['spec']['complete_cycles_target']==3 and card['spec']['automatic_retry'] is False
 assert sha(ROOT/card['user_authorization']['path'])==card['user_authorization']['sha256']
 assert not (ROOT/card['output']).parent.exists() and not (ROOT/TASK/'authorization'/run/'AUTHORIZATION_NATIVE_EXECUTION.json').exists() and not (ROOT/ENG/'releases'/run/'EXECUTION_RELEASE.json').exists()
 oldcard=load('artifacts/candidate_a_native_budget_cycles_20261012_v1/engineering/packages/CA_NATIVE_PHASE_R300_S17_CYCLES_W300_01/card.json')
 assert card['network_sha256']==oldcard['network_sha256'] and card['resources']==oldcard['resources']
 assert (ROOT/card['package']/'demand.rou.xml').read_bytes()==(ROOT/oldcard['package']/'demand.rou.xml').read_bytes()
 old_cfg=ET.parse(ROOT/oldcard['package']/'scenario.sumocfg').getroot()
 old_root=old_cfg.find('./input/net-file').get('value').split('/artifacts/')[0]
 for n in ['scenario.add.xml','scenario.sumocfg']:
  new=(ROOT/card['package']/n).read_text().replace(str(ROOT),old_root).replace('candidate_a_native_receiver_wait_20261012_v1','candidate_a_native_budget_cycles_20261012_v1').replace(run,oldcard['spec']['run_id'])
  assert new==(ROOT/oldcard['package']/n).read_text(),n
 cfg=ET.parse(ROOT/card['package']/'scenario.sumocfg').getroot();assert cfg.find('./time/end').get('value')=='1272' and cfg.find('./time/step-length').get('value')=='1'
 logic=ET.parse(ROOT/card['package']/'scenario.add.xml').getroot().find("tlLogic[@programID='CA_C24']");assert [(x.get('state'),x.get('duration'),x.get('next'))for x in logic]==[('G','3','1'),('y','3','2'),('r','18','0')]
 log=(ROOT/ENG/'OFFLINE_TESTS_V3.txt').read_text();assert 'Ran 11 tests' in log and re.search('^OK$',log,re.MULTILINE)
 helper=(ROOT/'src/candidate_a_native_receiver_wait_20261012/receiver_wait.py').read_text();adapter=(ROOT/'src/candidate_a_native_receiver_wait_20261012/adapter.py').read_text();bridge=(ROOT/'src/candidate_a_native_receiver_wait_20261012/bridge.py').read_text()
 for text in ["LOOKAHEAD_M = 478.67","MARGIN_M = 1.1","'speed':speed","expected_leader=leader,allow_clear=False","'original_prospective_receiver':dict(receiver)","allow_clear and expected_leader is None"]:assert text in helper,text
 for text in ["receiver['available']","'GREEN_START_NOT_PREPARED_OR_RECEIVER_DENIED'","'actual_entry_following'","'entry_following_before'","current_following(conn, vid, self.last_completed, allow_clear=True)","'ACTUAL_ENTRY_CURRENT_GAP_BOUND_DENIED:'"]:assert text in adapter,text
 for text in ['for t in range(1272):','if t in (1224,1248):','FIRST_RED_CHECKPOINT_PROVISIONAL_UNTIL_EOF',"require(t==1271,'unexpected diagnostic pause')"]:assert text in bridge,text
 assert 'request_phase' not in bridge.split('if t in (1224,1248):',1)[1].split('before=adapter.prepare_step',1)[0]
 trace=load(TASK/'design/SOURCE_TRACE_V1.json');assert trace['official_pin']=='fa7df22d7f1c4ae245192ecc32410a49f1ffb2a3'
 for source in trace['sources']:assert sha(ROOT/source['prior_receipt_path'])==source['prior_receipt_sha256']
 assert 'W300 was consumed' in (ROOT/TASK/'design/MINIMAL_WAIT_DESIGN_V3.md').read_text()
 assert 'before_status not in allowed' in adapter and 'after_status not in allowed' in adapter
 assert 'ACTUAL_ENTRY_BEFORE_CURRENT_GAP_BOUND_DENIED' in adapter
 assert sha(ROOT/ENG/'packages/CA_NATIVE_PHASE_R300_S17_WAIT_DIAG01/card.json')=='973e0a7544bf31adc1cfc6c293b4a2e8112f61ca2b7d7785f7f7dff4857c8f11'
 assert 'FAILED' in (ROOT/ENG/'PRE_FIX_COMPOSITION_REGRESSION_FAIL_V1.txt').read_text()
 return {'status':'PASS_BOUNDED_INDEPENDENT_WAIT_OFFLINE_DATA_PRELAUNCH','engineering_files_verified':77,'protected_files_verified':536,'old_engineering_files_verified':59,'card_sha256':sha(ROOT/cardpath),'new_native_starts':0,'new_source_snapshot':'UNCOMMITTED_EXACT_HASH_BOUND_NOT_TESTED_BASELINE_COMMIT','engineering11tests_log_reviewed_not_rerun':True,'raw_auth_release_absent':True,'clean_checkout':'NOT_RUN','future_native_WAIT_actual_queries_N_and_safety':'NOT_YET_OBSERVED'}
if __name__=='__main__':print(json.dumps(audit(),indent=2))

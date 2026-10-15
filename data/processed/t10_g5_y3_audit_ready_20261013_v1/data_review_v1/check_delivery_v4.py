"""Bounded independent static audit. No simulator/runtime imports."""
import ast,hashlib,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[4]
TASK='artifacts/t10_g5_y3_audit_ready_20261013_v1'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def need(ok,reason):
 if not ok:raise ValueError(reason)
def method(src,name):return ast.dump(next(x for x in ast.walk(ast.parse(src)) if isinstance(x,ast.FunctionDef) and x.name==name),include_attributes=False)
def main():
 e=ROOT/TASK/'engineering/implementation_v4';b=e/'ENGINEERING_DELIVERY_BINDING_V4.json';need(sha(b)=='65fa264562e4a721e91c7eb484191b3f6c00a0904e58624b10a6ee379aa8225a','EXACT_ENGINEERING_BINDER');checked={}
 for n,h in json.loads(b.read_text())['files_sha256'].items():need(sha(ROOT/n)==h,'ENGINEERING_FILE:'+n);checked[n]=h
 cp=ROOT/TASK/'engineering/packages_v4/UA_T10_G5Y3_FIXED750_S17_02/card.json';c=json.loads(cp.read_text());need(sha(cp)=='18774ee7aba5319b9947cf6c817c29db00339e7b5f52bb2abef509cf4313755e' and len(c['sources_sha256'])==87 and c['common_runtime_source_sha256']=='4deb99f4a6c0b053d810d3b61123a5fff8a15df09cd9cd659e2b4f39bff9fd40','CARD_IDENTITY')
 for key in ('sources_sha256','prepared_input_sha256','inherited_inputs_sha256'):
  for n,h in c[key].items():need(sha(ROOT/n)==h,'CARD_FILE:'+n);checked[n]=h
 for n,h in c['environment']['files_sha256'].items():need(sha(Path(n))==h,'STATIC_ENVIRONMENT:'+n)
 need(c['SUMO_execution_authorized'] is False and c['numerical_exception_authority']['enabled'] is False and all(v is None for v in c['observations'].values()),'OFFLINE_NULL_STRICT')
 need(c['spec']['end_s']==1270 and c['spec']['phase_durations_s']==[5,3,2] and c['spec']['total_resource_envelope']=={'monitored_s':300,'raw_bytes':300000000},'NEW_UNAPPROVED_FIXED_SCOPE')
 need(not(ROOT/c['output']).parent.exists() and not(ROOT/TASK/'authorizations').exists() and not(ROOT/TASK/'releases').exists(),'RAW_OR_PERMISSION_CREATED')
 old=ROOT/'artifacts/t10_g5_y3_candidate_20261013_v1/engineering/packages/UA_T10_G5Y3_FIXED750_S17_01/card.json';need(sha(old)=='6dc909466ddf8387db7a132c2609cb09564fb05c5d917ba9d67de7ba633b7476','OLD_CARD_DRIFT')
 for n,h in json.loads(old.read_text())['sources_sha256'].items():need(sha(ROOT/n)==h,'OLD73_SOURCE_DRIFT')
 oldb=ROOT/TASK/'engineering/implementation_v3/ENGINEERING_DELIVERY_BINDING_V3.json';need(sha(oldb)=='1c707af1c52aae072814a60b7ceea181a7e6103a56afe7d1e63941e3be0a02b3','OLD_BINDER_DRIFT');od=json.loads(oldb.read_text())['files_sha256'];changed=[]
 for n,h in od.items():
  if sha(ROOT/n)!=h:need(sha(e/'preimage_v3'/n)==h,'HISTORICAL_PREIMAGE_DRIFT');changed.append(n)
 expected=json.loads((e/'SOURCE_CARD_HISTORY_RECONCILIATION_V4.json').read_text())['changed_v3_live_paths'];need(sorted(changed)==sorted(expected) and len(changed)==4,'EXACT_HISTORY_CHANGE_SCOPE')
 test=ROOT/'tests/t10_g5_y3_audit_20261013/test_audit.py';oldtest=e/'preimage_v3/tests/t10_g5_y3_audit_20261013/test_audit.py';oldnames=[x.name for x in ast.walk(ast.parse(oldtest.read_text())) if isinstance(x,ast.FunctionDef) and (x.name.startswith('test_') or x.name=='phase')]; unchanged=[]
 for name in oldnames:
  if name not in ('test_extra_PRE_identity_prefix_valid_and_unknown_cases','test_public_fixture_real_card_gates_and_unchanged_motion_bridge'):
   need(method(test.read_text(),name)==method(oldtest.read_text(),name),'UNAFFECTED_TEST_DRIFT:'+name);unchanged.append(name)
 reuse={'unchanged_previous_methods':unchanged}
 olde=(e/'preimage_v3/scripts/t10_g5_y3_audit_20261013_v1/evidence.py').read_text();newe=(ROOT/'scripts/t10_g5_y3_audit_20261013_v1/evidence.py').read_text()
 for name in ('yellow_coverage','yellow_record','body_frame','log_eof','strict_numeric'):need(method(olde,name)==method(newe,name),'PREVIOUS_CLOSED_GATE_DRIFT:'+name)
 actual=(ROOT/'scripts/t10_g5_y3_audit_20261013_v1/actual.py').read_text();calls=[x.func.id for x in ast.walk(ast.parse(actual)) if isinstance(x,ast.Call) and isinstance(x.func,ast.Name)];need('identity_prefix' in calls and 'yellow_coverage' in calls,'ACTUAL_HELPER_WIRING')
 return dict(status='PASS_STATIC_AFFECTED_DELIVERY_ONLY',card_sha256=sha(cp),source_digest=c['common_runtime_source_sha256'],checked_files=checked,historical_v3_live_superseded_paths=changed,unchanged_test_AST_methods=reuse['unchanged_previous_methods'],F01_source_coverage_reviewed=True,F02_source_wiring_reviewed=True,nonactive_independent_pool_join_reviewed=True,terminal_without_next_PRE_scope='SINGLE_JOURNAL_NOT_INDEPENDENT_POOL_CHECK',native_runs=0,new_runtime_tests_by_data=0,actual_N=None,native_safety_proven=False,rate_qualified=False)
if __name__=='__main__':print(json.dumps(main(),indent=2))

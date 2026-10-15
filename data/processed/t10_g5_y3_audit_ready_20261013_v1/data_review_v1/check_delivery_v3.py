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
 e=ROOT/TASK/'engineering/implementation_v3';b=e/'ENGINEERING_DELIVERY_BINDING_V3.json';need(sha(b)=='1c707af1c52aae072814a60b7ceea181a7e6103a56afe7d1e63941e3be0a02b3','EXACT_ENGINEERING_BINDER');checked={}
 for n,h in json.loads(b.read_text())['files_sha256'].items():need(sha(ROOT/n)==h,'ENGINEERING_FILE:'+n);checked[n]=h
 cp=ROOT/TASK/'engineering/packages_v3/UA_T10_G5Y3_FIXED750_S17_02/card.json';c=json.loads(cp.read_text());need(sha(cp)=='b84cb63eb49845759bbc259d7ce2a19a64b62479620be109b749e3dd073e2e6f' and len(c['sources_sha256'])==87 and c['common_runtime_source_sha256']=='2b3a960ee27b2f1802760805f43108c471ff73a87ed300a448c98b3987e4e616','CARD_IDENTITY')
 for key in ('sources_sha256','prepared_input_sha256','inherited_inputs_sha256'):
  for n,h in c[key].items():need(sha(ROOT/n)==h,'CARD_FILE:'+n);checked[n]=h
 for n,h in c['environment']['files_sha256'].items():need(sha(Path(n))==h,'STATIC_ENVIRONMENT:'+n)
 need(c['SUMO_execution_authorized'] is False and c['numerical_exception_authority']['enabled'] is False and all(v is None for v in c['observations'].values()),'OFFLINE_NULL_STRICT')
 need(c['spec']['end_s']==1270 and c['spec']['phase_durations_s']==[5,3,2] and c['spec']['total_resource_envelope']=={'monitored_s':300,'raw_bytes':300000000},'NEW_UNAPPROVED_FIXED_SCOPE')
 need(not(ROOT/c['output']).parent.exists() and not(ROOT/TASK/'authorizations').exists() and not(ROOT/TASK/'releases').exists(),'RAW_OR_PERMISSION_CREATED')
 old=ROOT/'artifacts/t10_g5_y3_candidate_20261013_v1/engineering/packages/UA_T10_G5Y3_FIXED750_S17_01/card.json';need(sha(old)=='6dc909466ddf8387db7a132c2609cb09564fb05c5d917ba9d67de7ba633b7476','OLD_CARD_DRIFT')
 for n,h in json.loads(old.read_text())['sources_sha256'].items():need(sha(ROOT/n)==h,'OLD73_SOURCE_DRIFT')
 oldb=ROOT/TASK/'engineering/implementation_v2/ENGINEERING_DELIVERY_BINDING_V2.json';need(sha(oldb)=='29df09f2834a5787e77591f810be2b96e6bc1729203b898c90c17cb0c5128ed2','OLD_BINDER_DRIFT');od=json.loads(oldb.read_text())['files_sha256'];changed=[]
 for n,h in od.items():
  if sha(ROOT/n)!=h:need(sha(e/'preimage_v2'/n)==h,'HISTORICAL_PREIMAGE_DRIFT');changed.append(n)
 expected=json.loads((e/'SOURCE_CARD_HISTORY_RECONCILIATION_V3.json').read_text())['historical_v2_changed_live_paths'];need(sorted(changed)==sorted(expected) and len(changed)==5,'EXACT_HISTORY_CHANGE_SCOPE')
 test=ROOT/'tests/t10_g5_y3_audit_20261013/test_audit.py';oldtest=e/'preimage_v2/tests/t10_g5_y3_audit_20261013/test_audit.py';reuse=json.loads((e/'TEST_METHOD_REUSE_V3.json').read_text())
 for name in reuse['unchanged_previous_methods']:need(method(test.read_text(),name)==method(oldtest.read_text(),name),'UNCHANGED_METHOD:'+name)
 actual=(ROOT/'scripts/t10_g5_y3_audit_20261013_v1/actual.py').read_text();calls=[x.func.id for x in ast.walk(ast.parse(actual)) if isinstance(x,ast.Call) and isinstance(x.func,ast.Name)];need('identity_prefix' in calls and 'yellow_coverage' in calls,'ACTUAL_HELPER_WIRING')
 return dict(status='PASS_STATIC_AFFECTED_DELIVERY_ONLY',card_sha256=sha(cp),source_digest=c['common_runtime_source_sha256'],checked_files=checked,historical_v2_live_superseded_paths=changed,unchanged_test_AST_methods=reuse['unchanged_previous_methods'],F01_source_coverage_reviewed=True,F02_source_wiring_reviewed=True,native_runs=0,new_runtime_tests_by_data=0,actual_N=None,native_safety_proven=False,rate_qualified=False)
if __name__=='__main__':print(json.dumps(main(),indent=2))

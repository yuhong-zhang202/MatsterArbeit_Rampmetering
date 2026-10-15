"""Minimal read-only independent delivery audit; no simulation imports."""
from pathlib import Path
import ast,json,hashlib,subprocess,xml.etree.ElementTree as ET
from fractions import Fraction
ROOT=Path(__file__).resolve().parents[4]
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def need(v,msg):
 if not v:raise ValueError(msg)
def function(src,name):
 tree=ast.parse(src)
 f=next(x for x in tree.body if isinstance(x,ast.FunctionDef) and x.name==name)
 return ast.get_source_segment(src,f)
def method(src,name):
 tree=ast.parse(src);return ast.dump(next(x for x in ast.walk(tree) if isinstance(x,ast.FunctionDef) and x.name==name),include_attributes=False)
def main():
 eng=ROOT/'artifacts/t10_g5_y3_candidate_20261013_v1/engineering/implementation_v1';b=json.loads((eng/'ENGINEERING_DELIVERY_BINDING_V1.json').read_text());need(sha(eng/'ENGINEERING_DELIVERY_BINDING_V1.json')=='f623f11444cf3dd8c9017d5f35125d65f19385aca4a92554b21b14d51a39e35a','BINDER_ID')
 checked={}
 for name,h in b['files_sha256'].items():
  if name=='tests/candidate_a_t10_g5_y3_20261013/test_candidate.py':
   prior=ROOT/'artifacts/t10_g5_y3_candidate_20261013_v1/engineering/implementation_revision02/TEST_SOURCE_PREIMAGE_0394949.py'
   blob=subprocess.run(['git','show','03949494d02c94802e5bc2461ca9daf2a82b341a:'+name],cwd=ROOT,capture_output=True,check=True).stdout
   need(sha(prior)==h==hashlib.sha256(blob).hexdigest(),'HISTORICAL_TEST_UNBOUND');checked[str(prior.relative_to(ROOT))]=h
  else:need(sha(ROOT/name)==h,'ENGINEERING_FILE_DRIFT');checked[name]=h
 revision=ROOT/'artifacts/t10_g5_y3_candidate_20261013_v1/engineering/implementation_revision02/ENGINEERING_REVISION02_BINDING_V1.json';need(sha(revision)=='d81bf35223ef12cb5a92df309b7b516a3fc3dc4e881c78e33b6f83ae087829c6','REVISION_BINDER_ID')
 for name,h in json.loads(revision.read_text())['files_sha256'].items():need(sha(ROOT/name)==h,'REVISION_FILE_DRIFT');checked[name]=h
 portability=ROOT/'artifacts/t10_g5_y3_candidate_20261013_v1/portability_v2/PORTABILITY_BINDINGS_V2.json'
 for name,h in json.loads(portability.read_text())['files'].items():need(sha(ROOT/name)==h,'PORTABILITY_FILE_DRIFT');checked[name]=h
 receipt=json.loads((portability.parent/'CLEAN_CHECKOUT_RECEIPT_V2.json').read_text())
 need(receipt['tested_commit']=='fb8397678650c327769589044fa454b55bb4189b' and receipt['exit_code']==0 and receipt['result']=='PASS' and receipt['native_starts']==0 and receipt['raw_files_before']==receipt['raw_files_after']==['data/raw/.gitkeep'] and receipt['checkout_status_after']=='','PUBLIC_CLEAN_TEST_RECEIPT')
 cp=ROOT/'artifacts/t10_g5_y3_candidate_20261013_v1/engineering/packages/UA_T10_G5Y3_FIXED750_S17_01/card.json';c=json.loads(cp.read_text());need(sha(cp)=='6dc909466ddf8387db7a132c2609cb09564fb05c5d917ba9d67de7ba633b7476' and len(c['sources_sha256'])==73 and c['common_runtime_source_sha256']=='013a7da7518bdf822e049ab833fd06854a2b1f294f8f2120e4796f878a0e71f2','CARD_SOURCE_ID')
 for key in ('sources_sha256','prepared_input_sha256'):
  for name,h in c[key].items():need(sha(ROOT/name)==h,'CARD_FILE_DRIFT');checked[name]=h
 need(c['SUMO_execution_authorized'] is False and c['runtime_authorization_generated'] is False and c['numerical_exception_authority']['enabled'] is False and c['spec']['restricted_numerical_exception_enabled'] is False and all(v is None for v in c['observations'].values()),'OFFLINE_STRICT_UNOBSERVED')
 need(c['resources_status']=='PROPOSED_REQUIRES_FUTURE_EXACT_USER_APPROVAL' and c['spec']['total_resource_envelope']=={'monitored_s':300,'raw_bytes':300000000},'NEW_PROPOSED_RESOURCE_SCOPE')
 need(not(ROOT/c['output']).parent.exists(),'RAW_ALLOCATED');task=ROOT/'artifacts/t10_g5_y3_candidate_20261013_v1';need(not(task/'authorizations').exists() and not(task/'releases').exists(),'CANONICAL_PERMISSION_CREATED')
 pkg=ROOT/c['package'];add=ET.parse(pkg/'scenario.add.xml').getroot();logic=add.find("tlLogic[@programID='T10_G5Y3_NATIVE']");need([(p.get('state'),p.get('duration'),p.get('next')) for p in logic]==[('G','5','1'),('y','3','2'),('r','2','0')],'NEW_PHASES')
 old=add.find("tlLogic[@programID='I12_PACKET8']");need([(p.get('state'),p.get('duration'),p.get('next')) for p in old]==[('G','4','1'),('y','2','2'),('r','2','0')],'T8_PRESERVED')
 donor=ROOT/'src/candidate_a_unified_alinea_20261013';new=ROOT/'src/candidate_a_t10_g5_y3_20261013';oldcard=json.loads((ROOT/'artifacts/unified_alinea_actuator_20261013_v1/engineering/packages/UA_ALINEA_S17_01/card.json').read_text())
 for name,h in oldcard['sources_sha256'].items():need(sha(ROOT/name)==h,'DONOR64_DRIFT')
 same={}
 for f,n in [('policy.py','yellow_scope'),('adapter.py','identity'),('adapter.py','inventory'),('adapter.py','require')]:
  need(function((new/f).read_text(),n)==function((donor/f).read_text(),n),'PROTECTED_FUNCTION_CHANGED');same[n]=True
 a=(new/'adapter.py').read_text();da=(donor/'adapter.py').read_text();need(a[a.index('        errors = []'):a.index('        # BEGIN_APPROVED_NUMERICAL_EVENT_SEAM')]==da[da.index('        errors = []'):da.index('        # BEGIN_APPROVED_NUMERICAL_EVENT_SEAM')],'POST_ERROR_BLOCK_CHANGED');same['post_error_block']=True
 need(any(isinstance(x,ast.Call) and isinstance(x.func,ast.Name) and x.func.id=="require" and len(x.args)==2 and ast.dump(x.args[0])==ast.dump(ast.parse("numerical_authority is None",mode="eval").body) and isinstance(x.args[1],ast.Constant) and x.args[1].value=="NEW_SCOPE_NUMERICAL_EXCEPTION_NOT_ENABLED" for x in ast.walk(ast.parse(a))),"NUM_AUTHORITY_NOT_REJECTED")
 test=(ROOT/'tests/candidate_a_t10_g5_y3_20261013/test_candidate.py').read_text();snapshot=(ROOT/'artifacts/t10_g5_y3_candidate_20261013_v1/engineering/implementation_revision02/TEST_SOURCE_PREIMAGE_0394949.py').read_text()
 unchanged=[]
 for name in ('test_Y3_unknown_stops_both_paths_before_first_yellow_motion','test_original_gates_and_strict_NUM_remain','test_real_helper_both_clock_paths_dynamic_red_and_uncapped_accounting'):
  need(method(test,name)==method(snapshot,name),'UNAFFECTED_TEST_METHOD_DRIFT');unchanged.append(name)
 bframe=(new/'bridge.py').read_text();need("remaining=cycle['end_s']-t" in bframe and "end = adapter.first_controlled_red_begin+1" in bframe,'DYNAMIC_RED_ACK_LOGIC')
 mathview=[]
 for green in (4,5):
  red_begin=1200+green+3;mathview.append({'illustrative_G_s':green,'Y_s':3,'R_s':10-green-3,'first_red_BEGIN':red_begin,'first_red_ACK':red_begin+1,'native_initial_red_end_without_duration_binding':1200+green+5,'red_duration_set_on_first_actual_red_ACK':1210-(red_begin+1)})
 need(Fraction(750*70,3600)==Fraction(175,12) and Fraction(720*70,3600)==14,'NOMINAL_INTEGRALS')
 return {'verdict':'PASS_STATIC_DELIVERY_OFFLINE_ONLY','card_sha256':sha(cp),'source73_digest':c['common_runtime_source_sha256'],'checked_paths':checked,'protected_functions':same,'old64_T8_preserved':True,'unaffected_methods_reused_exact_AST':unchanged,'illustrative_clock_math':mathview,'nominal_E_if7complete':14,'actual_N':None,'requested_integral_if70observed':'175/12','mapped_integral_if70observed':14,'NUM_default_strict':True,'new_resources_proposed_not_authorized':True,'native_runs':0,'new_runtime_tests_by_data':0,'public_test_commit':receipt['tested_commit'],'public_clean_test_source_sha256':receipt['test_source_sha256'],'public_clean_test_exit_code':0,'historical_original32_superseded_test_bound_to_git_blob':True}
if __name__=='__main__':print(json.dumps(main(),indent=2))

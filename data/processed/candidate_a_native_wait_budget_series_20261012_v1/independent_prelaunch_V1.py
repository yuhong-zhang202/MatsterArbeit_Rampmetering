"""Bounded public wrapper/card/physical-input/reuse audit; no native or raw."""
from pathlib import Path
import json,hashlib,re,importlib.util,xml.etree.ElementTree as ET
ROOT=Path(__file__).resolve().parents[3];TASK=Path('artifacts/candidate_a_native_wait_budget_series_20261012_v1');ENG=TASK/'engineering'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def load(p):return json.loads((ROOT/p).read_text())
def check(files):
 for n,h in files.items():assert sha(ROOT/n)==h,n
 return len(files)
def physics(path):
 root=ET.parse(path).getroot()
 for n in root.iter():
  if n.tag in ('net-file','route-files','additional-files'):n.set('value','BOUND_INPUT_'+n.tag)
  if n.tag in ('output','report'):
   for child in n:
    if child.get('value','').startswith('/'):child.set('value','BOUND_OUTPUT_'+child.tag)
  for key in ['file','dest']:
   if key in n.attrib:n.set(key,'BOUND_OUTPUT_'+key)
 def canonical(n):return[n.tag,sorted(n.attrib.items()),(n.text or '').strip(),[canonical(c)for c in n]]
 return canonical(root)
def audit():
 binding=ENG/'ENGINEERING_BINDING_V1.json';assert sha(ROOT/binding)=='4466f5223a35fc97ad00c10f73f1561abbf2c2b2b8c0c5e803e950b75fe53e40';assert check(load(binding)['files'])==58
 equ=ENG/'COMMON_CORE_INPUT_EQUIVALENCE_V1.json';assert sha(ROOT/equ)=='dfe86a871e98cd4fc406daccb9a085093259ef580156ce353d1bed2a3fe60deb';e=load(equ);assert check(e['common_core_sha256'])==31
 assert check(load('artifacts/candidate_a_native_receiver_wait_20261012_v1/engineering/INPUT_BINDINGS_V2.json')['files'])==77
 donor_path=Path('artifacts/candidate_a_native_receiver_wait_20261012_v1/engineering/packages/CA_NATIVE_PHASE_R300_S17_WAIT_DIAG01_V2/card.json');donor=load(donor_path);assert sha(ROOT/donor_path)==e['completed300_card_sha256']=='c6f8574a57396939b1b4be4c119041e78ce1f652050d5a621c6d121d8def10ac'
 oldbridge=(ROOT/'src/candidate_a_native_receiver_wait_20261012/bridge.py').read_text();newbridge=(ROOT/'src/candidate_a_native_wait_budget_series_20261012/bridge.py').read_text();assert newbridge.replace('src.candidate_a_native_wait_budget_series_20261012.profile','src.candidate_a_native_receiver_wait_20261012.profile')==oldbridge
 reader=Path(__file__).with_name('audit_budget_run_V1.py');sp=importlib.util.spec_from_file_location('new_strict_reader',reader);m=importlib.util.module_from_spec(sp);sp.loader.exec_module(m)
 assert len(m.CARDS)==3 and donor['spec']['run_id'] not in m.CARDS
 report=[]
 for run,info in e['cards'].items():
  path=ENG/'packages'/run/'card.json';c=load(path);assert sha(ROOT/path)==info['card_sha256']==m.CARDS[run]
  check(c['sources_sha256']);check(c['prepared_input_sha256']);check(c['inherited_inputs_sha256'])
  assert c['sources_sha256']!=donor['sources_sha256'] and all(c['sources_sha256'][n]==h for n,h in donor['sources_sha256'].items())
  assert c['spec']=={**donor['spec'],'run_id':run} and c['environment']==donor['environment'] and c['network_sha256']==donor['network_sha256']
  assert c['resources']=={**donor['resources'],'wall_limit_s':info['wall_limit_s']} and all(type(v)is int for v in c['resources'].values())
  assert c['resources']['wall_limit_s']in(360,420,480) and c['status']=='PREPARED_NOT_RELEASED'
  assert not (ROOT/c['output']).parent.exists() and not(ROOT/TASK/'authorization'/run/'AUTHORIZATION_NATIVE_EXECUTION.json').exists() and not(ROOT/ENG/'releases'/run/'EXECUTION_RELEASE.json').exists()
  package=ROOT/c['package'];old=ROOT/donor['package'];assert (package/'demand.rou.xml').read_bytes()==(old/'demand.rou.xml').read_bytes()
  assert physics(package/'scenario.sumocfg')==physics(old/'scenario.sumocfg') and physics(package/'scenario.add.xml')==physics(old/'scenario.add.xml')
  cfg=ET.parse(package/'scenario.sumocfg').getroot();assert cfg.find('./time/end').get('value')=='1272'and cfg.find('./time/step-length').get('value')=='1'
  assert Path(cfg.find('./input/route-files').get('value')).resolve()==(package/'demand.rou.xml').resolve()and Path(cfg.find('./input/additional-files').get('value')).resolve()==(package/'scenario.add.xml').resolve()
  assert Path(cfg.find('./input/net-file').get('value')).resolve()==(ROOT/'artifacts/stage6_baseline_localization_20260921_v1/LOC_M3350_S17/engineering/build_attempts/TV_BUILD01/network.net.xml').resolve()
  report.append({'run_id':run,'card_sha256':sha(ROOT/path),'wall_budget_s':c['resources']['wall_limit_s']})
 assert sha(Path(__file__).with_name('following_schema_V2.py'))==sha(ROOT/'data/processed/candidate_a_native_receiver_wait_20261012_v1/following_schema_V2.py')
 original=(ROOT/'data/processed/candidate_a_native_receiver_wait_20261012_v1/audit_wait_run_V2.py').read_text();new=reader.read_text();a=original.index('CARDS = {');b=original.index('\nfrom following_schema_V2',a);expected=original[:a]+'CARDS = '+repr(m.CARDS)+original[b:];expected=expected.replace("'data/raw/candidate_a_native_receiver_wait_20261012_v1'","'data/raw/candidate_a_native_wait_budget_series_20261012_v1'");assert new==expected
 log=(ROOT/ENG/'OFFLINE_CONFIGURATION_TESTS_V1.txt').read_text();assert 'Ran 2 tests' in log and re.search('^OK$',log,re.MULTILINE)
 return{'status':'PASS_MINIMUM_REMAINING_BUDGET_DATA_PRELAUNCH','engineering58_verified':58,'commoncore31_verified':31,'frozen77_verified':77,'cards':report,'whole_source_snapshot_equal_to300':False,'commonruntime_and_physical_inputs_equal':True,'reader_delta':'strict_identity_card_map_and_raw_namespace_only','engineering_two_config_tests_log_reviewed_not_rerun':True,'old11_or_datafixtures_rerun':False,'completed300_reuse':'single completed technical donor, samecore/input/seed/horizon; wrappersource differs; not independentreplication or causalbudgetperformance','actual_new_native_starts':0,'fresh_runtime_gates':'NOT_RUN_BY_DATA','formal_protocol':'EMPTY_NOT_FORMAL'}
if __name__=='__main__':print(json.dumps(audit(),indent=2))

from pathlib import Path
import json,hashlib,xml.etree.ElementTree as E,importlib.util,os,sys,copy
B=Path(__file__).resolve().parent;ROOT=B.parents[2];HOME=Path('/Library/Frameworks/EclipseSUMO.framework/Versions/1.26.0/EclipseSUMO/share/sumo');OLD=ROOT/'artifacts/stage6_recovery_p2_revision_01/engineering';spec=importlib.util.spec_from_file_location('e',B/'runtime_executor.py');e=importlib.util.module_from_spec(spec);spec.loader.exec_module(e)
def bind(p):p=Path(p);return {'path':str(p),'bytes':p.stat().st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()}
def save(p,x):
 with p.open('x') as f:json.dump(x,f,indent=2,sort_keys=True);f.write('\n')
m=json.loads((B/'input_manifest.json').read_text());checks=[]
def check(k,ok):checks.append({'check':k,'status':'PASS' if ok else 'FAIL'});assert ok,k
source=OLD/'runtime_validation_revision04/inputs/RV4_R720_S17_attempt1'
addnorm=[];cfgnorm=[]
for a in m['attempts']:
 inp=B/'inputs'/a['attempt_id'];cfg=E.parse(inp/'scenario.sumocfg').getroot();add=E.parse(inp/'scenario.add.xml').getroot();d=E.parse(inp/'demand.rou.xml').getroot()
 check(a['attempt_id']+'_demand_byte_identical',(inp/'demand.rou.xml').read_bytes()==(source/'demand.rou.xml').read_bytes())
 check(a['attempt_id']+'_type_default_no_override',len(d.findall('vType'))==1 and d.find('vType').attrib=={'id':'technical_passenger','vClass':'passenger'} and not d.findall('vehicle') and all(x.get('type')=='technical_passenger' for x in d.findall('flow')))
 check(a['attempt_id']+'_schema_hints',all(E.parse(inp/f).getroot().get('{http://www.w3.org/2001/XMLSchema-instance}noNamespaceSchemaLocation') for f in ['scenario.add.xml','demand.rou.xml']))
 check(a['attempt_id']+'_no_empty_detector_filters',all(x.get(k)!='' for x in add if x.tag in ['inductionLoop','laneAreaDetector'] for k in ['vTypes','nextEdges']))
 check(a['attempt_id']+'_two_TLS_logger',add.find('timedEvent').get('source') is None)
 check(a['attempt_id']+'_native_startProg',add.find('WAUT').get('startProg')==a['program'] and len(add.find('WAUT'))==0 and add.find('wautJunction').get('junctionID')=='ramp_mid')
 for x in add:
  for k in ['file','dest']:
   if k in x.attrib:x.set(k,Path(x.get(k)).name)
 add.find('WAUT').set('startProg','ARM');addnorm.append(E.tostring(add))
 for x in cfg.iter():
  if 'value' in x.attrib and '/' in x.get('value'):x.set('value',Path(x.get('value')).name)
 lc=cfg.find('output/lanechange-output');check(a['attempt_id']+'_lc_contract',(lc is not None)==a['lanechange_logging'])
 if lc is not None:cfg.find('output').remove(lc)
 
 for node in cfg.iter():node.text=None;node.tail=None
 cfgnorm.append(E.tostring(cfg));check(a['attempt_id']+'_run_root_absent',not Path(a['run_root']).exists())
 roles=json.loads((inp/'output_roles.json').read_text());check(a['attempt_id']+'_role_count',len(roles['required_xml_roles'])==(18 if a['lanechange_logging'] else 17))
check('ABC_additional_only_selector_diff',len(set(addnorm))==1);check('all_configs_identical_after_paths_and_lc_removed',len(set(cfgnorm))==1)
check('length_source_resolution','return 5; /*4.3*/' in (B/'references/SUMOVehicleClass.cpp').read_text() and 'length(getDefaultVehicleLength(vclass))' in (B/'references/SUMOVTypeParameter.cpp').read_text())
check('default_vclass_not_special_length_branch','case SVC_PASSENGER' not in (B/'references/SUMOVehicleClass.cpp').read_text().split('getDefaultVehicleLength(const SUMOVehicleClass vc)')[1])
check('measurement_fixtures_PASS',json.loads((B/'measurement_test_receipt_revision02.json').read_text())['status']=='PASS');check('executor_fake_PASS',json.loads((B/'executor_test_receipt.json').read_text())['status']=='PASS')
check('no_real_SUMO_new_task',not (ROOT/'data/raw/stage6_targeted_validation_20260920_v1').exists())
save(B/'static_receipt.json',{'status':'PASS','checks':checks,'compiled_checks':65,'runtime_XSD_checks':15,'real_netconvert_starts':1,'real_SUMO_starts':0,'TraCI':0,'GUI':0,'retained_failure':'First mixed-chain fixture placed U in internal lane; corrected fixture places U on shared_approach using34 vehicles; helper code unchanged. Initial failure/log retained.'})
save(B/'gate_contract.json',{'required_check_ids':e.REQUIRED,'technical_status':['PASS','FAIL','NOT_COMPLETE'],'physical_status':['suitable','partial_evidence_physical','complete_evidence_but_comparison_unsuitable_physical_event'],'progression':'True iff every14checkPASS and physical suitable, plus prior neutral gate before primary','required_bindings':['card_sha256','attempt_id','execution_receipt_sha256','output_manifest_sha256','analysis_version_binding'],'role_counts':{'ON':18,'OFF':17},'TLS_records':{'urban_tls':2700,'ramp_mid':2700},'native_lanechange_contract':'ON:root lanechanges; event IDs,time,from/to lanes validated including R aux0→mainlane; None gap values NA. OFF:explicit configuration logger absent and file absent. Empty ON events legal; absence of evidence not absence of movement.','meter_state_and_crossing_contract':'Selected program and every recorded phase/state match exact plan. R stopline crossings bracketed and counts reconciled with trajectory identity; lane topology internally reachable. Zero crossing is an observation, not automatically technical failure. Red/yellow bracket ambiguity retained.','vehicle_length_contract':'sole passenger type with no override: SUMO1.26 default5m supported by archived version source; no actual TraCI read claim','neutrality_required_roles':17,'neutrality_exclusions':['XML comments','format whitespace','summary/step@duration computational time only']})
save(B/'resource_budget.json',{'limits':e.LIMITS,'basis':'R720 baseline1.122348625s25,043,371bytes. Conservative1858*2700*200byte FCD frame allowance=1,003,320,000bytes plus other roles.180s1.5GB operational fail-stop ceilings.50ms polling, no hard cap guarantee.','earlier_RV4_closed':{'starts':5,'wallclock_s':25.30447662600636,'bytes':70616284,'transferable_starts':0},'this_task_build':bind(B/'build_attempts/TV_BUILD01/build_receipt.json'),'this_task_runtime_consumed':0,'technical_retry_policy':'separate immutable evidence-based card and reviewed repair; no automatic retry; cumulative audit must retain all actuals','followup_family':'at most one; all O1+O2 pass→exactly seed23 A/B/C, else at most one demand OR timing family after parent/scientific review; blocked in this executor'})
local=[HOME/'data/xsd/additional_file.xsd',HOME/'data/xsd/types/sumoConfigurationType.xsd',HOME/'tools/sumolib/scenario/pop2.py']
save(B/'environment_and_sources.json',{'SUMO_HOME':str(HOME),'version':'1.26.0 from installed framework path and earlier runtime log','sumo':bind(HOME.parent.parent/'bin/sumo'),'netconvert':bind(HOME.parent.parent/'bin/netconvert'),'python':bind(Path(sys.executable).resolve()),'local_examples':[bind(p) for p in local],'downloaded_version_sources':json.loads((B/'references/source_provenance.json').read_text()),'local_version_source_audit':'passenger default5m source decision chain confirmed; not empirical calibration or binary reproducible-build proof'})
# Bind all schema dependencies: includes recursive XSD files, no version probe execution.
schemas=[bind(p) for p in sorted((HOME/'data/xsd').rglob('*.xsd'))]
files=['RUNTIME_CONTRACT.md','gate_contract.json','resource_budget.json','measurement_helpers.py','measurement_test_receipt_revision02.json','test_measurement_revision02.py','environment_and_sources.json','compiled_audit.json','references/source_provenance.json','references/SUMOVehicleClass.cpp','references/SUMOVTypeParameter.cpp']
card={'kind':'TARGETED_FIVE_START_RUNTIME_CARD','approved':False,'limits':e.LIMITS,'attempts':m['attempts'],'binary':bind(HOME.parent.parent/'bin/sumo'),'network':m['common_network'],'executor':bind(B/'runtime_executor.py'),'test_receipt':bind(B/'executor_test_receipt.json'),'static_receipt':bind(B/'static_receipt.json'),'input_manifest':bind(B/'input_manifest.json'),'user_task_binding':bind(Path('/Users/yuhongzhang/.codex/attachments/6e3cc74b-84d3-471e-9426-4589a7a3b855/已粘贴的文本.txt')),'bindings':[bind(B/p) for p in files]+schemas,'cwd':str(ROOT),'SUMO_HOME':str(HOME),'approval_path':str(B/'RUNTIME_user_approval.json'),'review_path':str(B/'static_final_review_receipt.json'),'science_registration':'Programs/demand/seed supplied by parent under targeted task, exploratory only','followup_executable':False}
save(B/'RUNTIME_CARD.json',card)
approval={'status':'NOT_APPROVED_TEMPLATE','card_sha256':bind(B/'RUNTIME_CARD.json')['sha256'],'card_path':str(B/'RUNTIME_CARD.json'),'scope':'two technical fixtures then seed17 A/B/C','max_SUMO_starts':5,'synthetic_test_only':False,'user_task_binding':card['user_task_binding'],'review_receipt':None,'provenance':'User task authorizes bounded work; later exact card bound by primary after independent static review. Do not claim user saw later SHA.'};save(B/'RUNTIME_approval_TEMPLATE.json',approval)
print(json.dumps({'card':bind(B/'RUNTIME_CARD.json'),'static_checks':len(checks),'bindings':len(card['bindings'])},indent=2))

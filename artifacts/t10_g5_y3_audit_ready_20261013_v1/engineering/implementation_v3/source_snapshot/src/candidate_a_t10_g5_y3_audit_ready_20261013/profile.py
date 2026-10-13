"""One offline review card; future native permission must be separate and exact."""
from pathlib import Path
import hashlib,json,shutil,sys,importlib.metadata
import xml.etree.ElementTree as ET
from src.candidate_a_unified_alinea_20261013 import profile as base
ROOT=base.ROOT;NETWORK=base.NETWORK;SUMO=base.SUMO
TASK=Path('artifacts/t10_g5_y3_audit_ready_20261013_v1/engineering')
USER=TASK.parent/'USER_OFFLINE_AUDIT_SCOPE_V1.json'
SCIENCE=Path('artifacts/t10_g5_y3_candidate_20261013_v1/science/SCIENTIFIC_PREIMPLEMENTATION_GATE_V1.md')
BASE='63af3b4166b2582cb916877630706d1ff933be7a'
RUN='UA_T10_G5Y3_FIXED750_S17_02'
RAW=Path('data/raw/t10_g5_y3_audit_ready_20261013_v1')
DONOR=base.TASK/'packages/UA_FIXED750_S17_02'
sha=base.sha;write_new=base.write_new;require=base.require

def spec(run):
    require(run==RUN,'T10_FIXED750_ONLY_IDENTITY')
    old=json.loads((ROOT/DONOR/'card.json').read_text())['spec']
    return {**old,'run_id':RUN,'mode':'fixed750','fixed_command_veh_h':750,
        'service_command_veh_h':750,'end_s':1270,'period_s':10,'phase_durations_s':[5,3,2],
        'complete_cycles_target':7,'restricted_numerical_exception_enabled':False,
        'total_resource_envelope':{'monitored_s':300,'raw_bytes':300000000},
        'resources_provenance':'NEW_SINGLE_RUN_PROPOSED_NOT_OLD_SCOPE_AUTHORITY',
        'discrete_rates_veh_h':[720.0],'eligible_requested_rates_veh_h':[750.0],
        'native_permission_granted':False,
        'interpretation':'CONDITIONAL_OFFLINE_CANDIDATE_NOT_NATIVE_OR_SERVICE_QUALIFIED'}
def output(run):spec(run);return RAW/run/'outputs'
def resources(run):
    spec(run);return dict(wall_limit_s=300,startup_limit_s=60,run_limit_bytes=300000000,minimum_free_bytes=5000000000)
def sources(root):
    old=json.loads((root/'artifacts/t10_g5_y3_candidate_20261013_v1/engineering/packages/UA_T10_G5Y3_FIXED750_S17_01/card.json').read_text())['sources_sha256']
    require(all(sha(root/p)==h for p,h in old.items()),'PROTECTED_T10_SOURCE73_DRIFT')
    d=dict(old)
    for folder in ('src/candidate_a_t10_g5_y3_audit_ready_20261013','scripts/candidate_a_t10_g5_y3_audit_ready_20261013_v1','scripts/t10_g5_y3_audit_20261013_v1','tests/t10_g5_y3_audit_20261013'):
        for p in (root/folder).glob('*.py'):d[str(p.relative_to(root))]=sha(p)
    for p in (Path('scripts/unified_alinea_audit_20261013_v1/core.py'),Path('scripts/unified_alinea_audit_20261013_v1/signal_binding_v2.py'),Path('data/processed/issue12_alinea_actuation_20261012_v1/audit_data_V3.py'),Path('artifacts/t10_g5_y3_candidate_20261013_v1/engineering/packages/UA_T10_G5Y3_FIXED750_S17_01/card.json'),USER,SCIENCE):d[str(p)]=sha(root/p)
    return dict(sorted(d.items()))
def common_source_digest(root):
    return hashlib.sha256(json.dumps(sources(root),sort_keys=True,separators=(',',':')).encode()).hexdigest()

def stage_package(root,package,out,end=1270):
    require(type(end) is int and 1200<end<=1270,'OFFLINE_HORIZON')
    package.mkdir(parents=True,exist_ok=False)
    inherited={}
    for name in ('demand.rou.xml','scenario.sumocfg','scenario.add.xml'):
        donor=root/DONOR/name;inherited[str(donor.relative_to(root))]=sha(donor)
        shutil.copyfile(donor,package/name)
    p=package/'scenario.sumocfg';tree=ET.parse(p);r=tree.getroot()
    for tag,value in [('net-file',root/NETWORK),('route-files',package/'demand.rou.xml'),('additional-files',package/'scenario.add.xml')]:r.find('./input/'+tag).set('value',str(value))
    r.find('./time/end').set('value',str(end))
    for n in r.findall('./output/*')+r.findall('./report/*'):
        if n.get('value','').startswith('/'):n.set('value',str(out/Path(n.get('value')).name))
    ET.indent(tree);tree.write(p,encoding='utf-8',xml_declaration=True)
    p=package/'scenario.add.xml';tree=ET.parse(p);r=tree.getroot()
    for n in r.iter():
        for attr in ('file','dest'):
            if attr in n.attrib:n.set(attr,str(out/Path(n.get(attr)).name))
    logic=ET.SubElement(r,'tlLogic',dict(id='ramp_mid',type='static',programID='T10_G5Y3_NATIVE',offset='0'))
    for state,dur,nxt in [('G',5,1),('y',3,2),('r',2,0)]:ET.SubElement(logic,'phase',dict(duration=str(dur),state=state,next=str(nxt)))
    ET.indent(tree);tree.write(p,encoding='utf-8',xml_declaration=True)
    return inherited

def static_environment(root,reference):
    require(reference['complete'] and reference['python']=='.'.join(map(str,sys.version_info[:3])),'PYTHON_ENVIRONMENT_DRIFT')
    require(all(importlib.metadata.version(k)==v for k,v in reference['packages'].items()),'PACKAGE_METADATA_DRIFT')
    require(all(sha(Path(p))==h for p,h in reference['files_sha256'].items()),'ENVIRONMENT_FILE_HASH_DRIFT')
    return {'status':'PASS_STATIC_RECEIPT_AND_FILE_HASH_ONLY','native_version_call':False,'native_module_import':False}

def prepare(run=RUN,root=ROOT):
    root=Path(root).resolve();sp=spec(run);package=root/TASK/'packages_v3'/run;out=root/output(run)
    require(not out.parent.exists(),'ONE_USE_IDENTITY_CONSUMED')
    card=package/'card.json'
    if card.exists():validate(card,root);return card
    donor=json.loads((root/DONOR/'card.json').read_text());check=static_environment(root,donor['environment'])
    inherited=stage_package(root,package,out)
    data=dict(status='PREPARED_NOT_RELEASED',classification='OFFLINE_REVIEW_T10_G5Y3_NOT_NATIVE_AUTHORIZED',baseline_commit=BASE,
        spec=sp,package=str(package.relative_to(root)),output=str(output(run)),SUMO_execution_authorized=False,
        user_authorization={'path':str(USER),'sha256':sha(root/USER),'scope':'OFFLINE_ONLY'},
        sources_sha256=sources(root),common_runtime_source_sha256=common_source_digest(root),
        inherited_inputs_sha256=inherited,prepared_input_sha256={str(p.relative_to(root)):sha(p) for p in package.iterdir() if p.is_file()},network_sha256=sha(root/NETWORK),
        environment=donor['environment'],environment_provenance={'receipt':str(DONOR/'card.json'),'sha256':sha(root/DONOR/'card.json'),'fresh_static_check':check,'fresh_native_version_executed':False},
        resources=resources(run),resources_status='PROPOSED_REQUIRES_FUTURE_EXACT_USER_APPROVAL',
        proposed_new_single_run_envelope={'monitored_s':300,'raw_bytes':300000000},old_budget_remainder_not_execution_authorization=True,
        numerical_exception_authority={'enabled':False,'status':'PENDING_NEW_SCOPE_APPLICABILITY_AND_EXECUTION_APPROVAL','old_approval_reference':str(base.NUM_USER),'old_approval_sha256':sha(root/base.NUM_USER)},
        observations={'N':None,'E':None,'actual_phase_exposure':None,'native_safety':None,'body_clearance':None,'future_G5_population':None},
        audit_contract={'schema':'T10_G5_Y3_STRICT_ACTUAL_AUDIT_V1','reader':'scripts/t10_g5_y3_audit_20261013_v1/actual.py','NUM':'STRICT_NO_CONTINUE_CLASSIFICATION','EOF_and_terminal_arrival_audit':'MANDATORY_NO_SKIP'},
        binary_reference_provenance=donor['binary_reference_provenance'],source_binary_compiler_equivalence='NOT_VERIFIED',runtime_authorization_generated=False)
    write_new(card,data);return card

def validate(card_path,root=ROOT,require_environment=False):
    root=Path(root).resolve();p=Path(card_path).resolve();expected=root/TASK/'packages_v3'/RUN/'card.json'
    require(p==expected,'FOREIGN_CANDIDATE_CARD')
    c=json.loads(p.read_text());require(c['status']=='PREPARED_NOT_RELEASED' and c['classification']=='OFFLINE_REVIEW_T10_G5Y3_NOT_NATIVE_AUTHORIZED' and c['baseline_commit']==BASE and c['spec']==spec(RUN),'CANDIDATE_SPEC_DRIFT')
    require(c['package']==str(expected.parent.relative_to(root)) and c['output']==str(output(RUN)),'CANDIDATE_PACKAGE_OUTPUT_DRIFT')
    require(c['SUMO_execution_authorized'] is False and c['numerical_exception_authority']['enabled'] is False,'OFFLINE_OR_NUM_SCOPE_DRIFT')
    require(c['user_authorization']=={'path':str(USER),'sha256':sha(root/USER),'scope':'OFFLINE_ONLY'},'OFFLINE_USER_BINDING_DRIFT')
    require(json.loads((root/USER).read_text())['SUMO_execution_authorized'] is False,'OFFLINE_APPROVAL_CHANGED')
    require(c['sources_sha256']==sources(root) and c['common_runtime_source_sha256']==common_source_digest(root),'CANDIDATE_SOURCE_DRIFT')
    require(c['resources']==resources(RUN) and c['resources_status']=='PROPOSED_REQUIRES_FUTURE_EXACT_USER_APPROVAL','PROPOSED_RESOURCE_DRIFT')
    for key in ('inherited_inputs_sha256','prepared_input_sha256'):
        for n,h in c[key].items():require(sha(root/n)==h,'CANDIDATE_INPUT_DRIFT '+n)
    require(sha(root/NETWORK)==c['network_sha256'],'NETWORK_DRIFT')
    cfg=ET.parse(expected.parent/'scenario.sumocfg').getroot();add=ET.parse(expected.parent/'scenario.add.xml').getroot()
    require(cfg.find('./time/end').get('value')=='1270' and cfg.find('./time/step-length').get('value')=='1' and cfg.find('./output/precision').get('value')=='8','HORIZON_STEP_PRECISION_DRIFT')
    for tag,path in [('net-file',root/NETWORK),('route-files',expected.parent/'demand.rou.xml'),('additional-files',expected.parent/'scenario.add.xml')]:
        require(Path(cfg.find('./input/'+tag).get('value')).resolve()==path.resolve(),'FOREIGN_RUNTIME_INPUT')
    for node in cfg.findall('./output/*')+cfg.findall('./report/*'):
        if node.get('value','').startswith('/'):
            require(Path(node.get('value')).resolve().parent==(root/output(RUN)).resolve(),'FOREIGN_RUNTIME_OUTPUT')
    for node in add.iter():
        for attr in ('file','dest'):
            if attr in node.attrib:require(Path(node.get(attr)).resolve().parent==(root/output(RUN)).resolve(),'FOREIGN_DETECTOR_OUTPUT')
    logic=add.find("tlLogic[@programID='T10_G5Y3_NATIVE']")
    require([(x.get('state'),x.get('duration'),x.get('next'))for x in logic]==[('G','5','1'),('y','3','2'),('r','2','0')],'PHASE_CONFIGURATION_DRIFT')
    original=add.find("tlLogic[@programID='I12_PACKET8']")
    require([(x.get('state'),x.get('duration'),x.get('next'))for x in original]==[('G','4','1'),('y','2','2'),('r','2','0')],'ORIGINAL_T8_CHANGED')
    require(not(root/output(RUN)).parent.exists(),'ONE_USE_IDENTITY_CONSUMED')
    if require_environment:static_environment(root,c['environment'])
    return c

def validate_release(card_path,release_path,root=ROOT):
    root=Path(root).resolve();c=validate(card_path,root,require_environment=True)
    auth_path=root/TASK/'authorizations'/RUN/'AUTHORIZATION_NATIVE_EXECUTION.json'
    require(auth_path.is_file(),'FUTURE_EXACT_NATIVE_AUTHORIZATION_MISSING')
    auth=json.loads(auth_path.read_text());expected=root/TASK/'releases'/RUN/'EXECUTION_RELEASE.json'
    require(auth.get('SUMO_execution_authorized') is True and auth.get('run_id')==RUN and auth.get('card_sha256')==sha(Path(card_path)),'FUTURE_NATIVE_AUTHORIZATION_UNBOUND')
    ref=Path(auth['human_authorization_reference']);require(not ref.is_absolute() and '..' not in ref.parts and ref!=USER,'CANNOT_INHERIT_OFFLINE_AUTHORITY')
    human=json.loads((root/ref).read_text());require(sha(root/ref)==auth['human_authorization_sha256'],'FUTURE_HUMAN_APPROVAL_DRIFT')
    require(human.get('source')=='direct human explicit execution approval' and human.get('SUMO_execution_authorized') is True and
        human.get('run_id')==RUN and human.get('card_sha256')==sha(Path(card_path)) and human.get('common_runtime_source_sha256')==c['common_runtime_source_sha256'] and
        human.get('numerical_exception_enabled') is False and human.get('resources')==c['resources'] and human.get('resource_envelope')==c['proposed_new_single_run_envelope'],
        'FUTURE_HUMAN_RUN_SOURCE_STRICT_NUM_RESOURCE_APPROVAL_UNBOUND')
    require(auth.get('numerical_exception_enabled') is False and auth.get('resources')==c['resources'] and auth.get('resource_envelope')==c['proposed_new_single_run_envelope'],'FUTURE_NATIVE_CAPS_OR_NUM_UNBOUND')
    require(Path(release_path).resolve()==expected and expected.is_file(),'FUTURE_CANONICAL_RELEASE_MISSING')
    release=json.loads(expected.read_text());require(release.get('run_id')==RUN and release.get('card_sha256')==sha(Path(card_path)) and release.get('SUMO_execution_authorized') is True and
        release.get('authorization_sha256')==sha(auth_path),'FUTURE_RELEASE_UNBOUND')
    require(set(release.get('reviews',{}))=={'engineering','data','science'},'FUTURE_THREE_ROLE_RELEASE_MISSING')
    for item in release['reviews'].values():require(sha(root/item['path'])==item['sha256'] and item.get('card_sha256')==sha(Path(card_path)),'FUTURE_REVIEW_HASH_OR_CARD_UNBOUND')
    return c

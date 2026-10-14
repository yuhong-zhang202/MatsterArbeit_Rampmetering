"""One offline review card; future native permission must be separate and exact."""
from pathlib import Path
import hashlib,json,shutil,sys,importlib.metadata
import xml.etree.ElementTree as ET
from src.candidate_a_unified_alinea_20261013 import profile as base
ROOT=base.ROOT;NETWORK=base.NETWORK;SUMO=base.SUMO
TASK=Path('artifacts/cumulative_full_catalogue_followup_20261014_v1/engineering')
USER=Path('artifacts/cumulative_full_catalogue_implementation_20261014_v1/USER_AUTONOMOUS_CONTINUATION_AUTHORITY_V1.json')
DESIGN=Path('artifacts/cumulative_full_catalogue_followup_20261014_v1/engineering/PLAN_V2.md')
SCIENCE=Path('artifacts/cumulative_full_catalogue_followup_20261014_v1/SCIENCE_PLAN_REVIEW_V1.md')
BASE='3e95c545fd63765d1c15489c943bd80a78f6fdd5'
APPROVED_BOUND_END=1296
RUN='UA_CUMULATIVE_FULL_DYNAMIC_S17_01'
RUNS={RUN:('dynamic_commands',300),'UA_CUMULATIVE_FULL_ALINEA_S17_01':('real_alinea',900)}
RAW=Path('data/raw/cumulative_full_catalogue_followup_20261014_v1')
DONOR=base.TASK/'packages/UA_FIXED750_S17_02'
sha=base.sha;write_new=base.write_new;require=base.require

def spec(run):
    require(run in RUNS,'EXACT_FOLLOWUP_IDENTITY_REQUIRED')
    mode,initial=RUNS[run]
    from src.candidate_a_cumulative_full_catalogue_20261014 import profile as protected
    old=protected.spec(protected.RUN)
    return {**old,'run_id':run,'mode':mode,'fixed_command_veh_h':initial,
        'service_command_veh_h':None,'initial_command_veh_h':initial,
        'total_resource_envelope':{'monitored_s':600,'raw_bytes':None},
        'single_resource_envelope':{'monitored_s':300,'raw_bytes':None},
        'request_schedule':{'1200':300,'1201':750,'1226':900,'1237':300} if mode=='dynamic_commands' else None,
        'Feedback':{'target_percent':11,'gain_veh_h_per_percentage_point':70,'bounds_veh_h':[300,900],
            'initial_veh_h':900,'sample_s':30,'global_activation_s':1200,'logical_activation_s':600,
            'detector_ids':['p1_main_down_20_l0','p1_main_down_20_l1'],'lanes':['main_down_0','main_down_1'],'position_m':20} if mode=='real_alinea' else None,
        'terminal_partial_allowed':True,'resources_provenance':'NEW_TWO_RUN_600S_ENVELOPE_REQUIRES_EXACT_RELEASE_NO_OLD_REMAINDER'}
def output(run):spec(run);return RAW/run/'outputs'
def resources(run):
    spec(run);return dict(wall_limit_s=300,startup_limit_s=60,run_limit_bytes=None,minimum_free_bytes=5000000000)
def sources(root):
    old=json.loads((root/'artifacts/cumulative_full_catalogue_implementation_20261014_v1/engineering/packages_v1/UA_CUMULATIVE_FULL750_S17_01/card.json').read_text())['sources_sha256']
    require(all(sha(root/p)==h for p,h in old.items()),'PROTECTED_PREVIOUS125_SOURCE_DRIFT')
    d=dict(old)
    for folder in ('src/candidate_a_cumulative_full_followup_20261014','scripts/candidate_a_cumulative_full_followup_20261014_v1','tests/candidate_a_cumulative_full_followup_20261014'):
        for p in (root/folder).glob('*.py'):d[str(p.relative_to(root))]=sha(p)
    for p in (Path('scripts/unified_alinea_audit_20261013_v1/core.py'),Path('scripts/unified_alinea_audit_20261013_v1/signal_binding_v2.py'),Path('data/processed/issue12_alinea_actuation_20261012_v1/audit_data_V3.py'),Path('artifacts/t10_g5_y3_candidate_20261013_v1/engineering/packages/UA_T10_G5Y3_FIXED750_S17_01/card.json'),Path('artifacts/t10_g5_y3_audit_ready_20261013_v1/engineering/packages_v4/UA_T10_G5Y3_FIXED750_S17_02/card.json'),USER,SCIENCE,DESIGN):d[str(p)]=sha(root/p)
    audit=root/'scripts/cumulative_full_catalogue_followup_audit_20261014_v1'
    require((audit/'actual.py').is_file() and (audit/'scope.py').is_file(), 'AUDIT_SOURCE_NOT_READY')
    for p in audit.glob('*.py'):d[str(p.relative_to(root))]=sha(p)
    return dict(sorted(d.items()))
def common_source_digest(root):
    return hashlib.sha256(json.dumps(sources(root),sort_keys=True,separators=(',',':')).encode()).hexdigest()

def stage_package(root,package,out,end=1296):
    require(type(end) is int and 1200<end<=APPROVED_BOUND_END,'OFFLINE_HORIZON')
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
    root=Path(root).resolve();sp=spec(run);package=root/TASK/'packages_v1'/run;out=root/output(run)
    require(not out.parent.exists(),'ONE_USE_IDENTITY_CONSUMED')
    card=package/'card.json'
    if card.exists():validate(card,root);return card
    donor=json.loads((root/DONOR/'card.json').read_text());check=static_environment(root,donor['environment'])
    inherited=stage_package(root,package,out)
    data=dict(status='PREPARED_NOT_RELEASED',classification='OFFLINE_CUMULATIVE_TRACKING_NOT_NATIVE_AUTHORIZED',baseline_commit=BASE,
        spec=sp,package=str(package.relative_to(root)),output=str(output(run)),SUMO_execution_authorized=False,
        user_authorization={'path':str(USER),'sha256':sha(root/USER),'scope':'CONTINUING_AUTHORITY_REQUIRES_EXACT_CARD_CANONICAL_BINDING'},
        sources_sha256=sources(root),common_runtime_source_sha256=common_source_digest(root),
        inherited_inputs_sha256=inherited,prepared_input_sha256={str(p.relative_to(root)):sha(p) for p in package.iterdir() if p.is_file()},network_sha256=sha(root/NETWORK),
        environment=donor['environment'],environment_provenance={'receipt':str(DONOR/'card.json'),'sha256':sha(root/DONOR/'card.json'),'fresh_static_check':check,'fresh_native_version_executed':False},
        resources=resources(run),resources_status='PROPOSED_NEW_SCOPE_NOT_APPROVED_FOR_NATIVE',
        proposed_new_single_run_envelope={'monitored_s':300,'raw_bytes':None},new_two_run_envelope={'monitored_s':600,'raw_bytes':None},old_budget_remainder_not_execution_authorization=True,
        numerical_exception_authority={'enabled':False,'status':'PENDING_NEW_SCOPE_APPLICABILITY_AND_EXECUTION_APPROVAL','old_approval_reference':str(base.NUM_USER),'old_approval_sha256':sha(root/base.NUM_USER)},
        observations={'N':None,'E':None,'actual_phase_exposure':None,'native_safety':None,'body_clearance':None,'future_mixed_population':None},
        audit_contract={'schema':'CUMULATIVE_FULL_C_N_V1','reader':'scripts/cumulative_full_catalogue_followup_audit_20261014_v1/actual.py','status':'FROZEN_NEW_READER_REVIEW_REQUIRED_BEFORE_RELEASE','NUM':'STRICT_NO_CONTINUE_CLASSIFICATION','EOF_and_terminal_arrival_audit':'MANDATORY_NO_SKIP'},
        binary_reference_provenance=donor['binary_reference_provenance'],source_binary_compiler_equivalence='NOT_VERIFIED',runtime_authorization_generated=False)
    write_new(card,data);return card

def validate(card_path,root=ROOT,require_environment=False):
    root=Path(root).resolve();p=Path(card_path).resolve();c=json.loads(p.read_text());run=c['spec']['run_id'];spec(run);expected=root/TASK/'packages_v1'/run/'card.json'
    require(p==expected,'FOREIGN_CANDIDATE_CARD')
    c=json.loads(p.read_text());require(c['status']=='PREPARED_NOT_RELEASED' and c['classification']=='OFFLINE_CUMULATIVE_TRACKING_NOT_NATIVE_AUTHORIZED' and c['baseline_commit']==BASE and c['spec']==spec(run),'CANDIDATE_SPEC_DRIFT')
    require(c['package']==str(expected.parent.relative_to(root)) and c['output']==str(output(run)),'CANDIDATE_PACKAGE_OUTPUT_DRIFT')
    require(c['SUMO_execution_authorized'] is False and c['numerical_exception_authority']['enabled'] is False,'OFFLINE_OR_NUM_SCOPE_DRIFT')
    require(c['user_authorization']=={'path':str(USER),'sha256':sha(root/USER),'scope':'CONTINUING_AUTHORITY_REQUIRES_EXACT_CARD_CANONICAL_BINDING'},'OFFLINE_USER_BINDING_DRIFT')
    require(c['spec']['scheduler']=='ACTUAL_C_MINUS_N_BOUNDARY_ONLY' and c['spec']['catalogue_periods_s']==list(range(8,25)),'OFFLINE_DESIGN_DRIFT')

    require(c['sources_sha256']==sources(root) and c['common_runtime_source_sha256']==common_source_digest(root),'CANDIDATE_SOURCE_DRIFT')
    require(c['resources']==resources(run) and c['resources_status']=='PROPOSED_NEW_SCOPE_NOT_APPROVED_FOR_NATIVE','PROPOSED_RESOURCE_DRIFT')
    for key in ('inherited_inputs_sha256','prepared_input_sha256'):
        for n,h in c[key].items():require(sha(root/n)==h,'CANDIDATE_INPUT_DRIFT '+n)
    require(sha(root/NETWORK)==c['network_sha256'],'NETWORK_DRIFT')
    cfg=ET.parse(expected.parent/'scenario.sumocfg').getroot();add=ET.parse(expected.parent/'scenario.add.xml').getroot()
    require(cfg.find('./time/end').get('value')=='1296' and cfg.find('./time/step-length').get('value')=='1' and cfg.find('./output/precision').get('value')=='8','HORIZON_STEP_PRECISION_DRIFT')
    for tag,path in [('net-file',root/NETWORK),('route-files',expected.parent/'demand.rou.xml'),('additional-files',expected.parent/'scenario.add.xml')]:
        require(Path(cfg.find('./input/'+tag).get('value')).resolve()==path.resolve(),'FOREIGN_RUNTIME_INPUT')
    for node in cfg.findall('./output/*')+cfg.findall('./report/*'):
        if node.get('value','').startswith('/'):
            require(Path(node.get('value')).resolve().parent==(root/output(run)).resolve(),'FOREIGN_RUNTIME_OUTPUT')
    for node in add.iter():
        for attr in ('file','dest'):
            if attr in node.attrib:require(Path(node.get(attr)).resolve().parent==(root/output(run)).resolve(),'FOREIGN_DETECTOR_OUTPUT')
    logic=add.find("tlLogic[@programID='T10_G5Y3_NATIVE']")
    require([(x.get('state'),x.get('duration'),x.get('next'))for x in logic]==[('G','5','1'),('y','3','2'),('r','2','0')],'PHASE_CONFIGURATION_DRIFT')
    original=add.find("tlLogic[@programID='I12_PACKET8']")
    require([(x.get('state'),x.get('duration'),x.get('next'))for x in original]==[('G','4','1'),('y','2','2'),('r','2','0')],'ORIGINAL_T8_CHANGED')
    for t in range(8,25):
        name='T10_G5Y3_NATIVE' if t==10 else f'I12_PACKET{t}'
        node=add.find(f"tlLogic[@programID='{name}']")
        require(node is not None,'MISSING_FULL_CATALOGUE_PROGRAM')
        phase=spec(run)['phase_durations_s'][str(t)]
        require([(x.get('state'),int(x.get('duration')),int(x.get('next'))) for x in node]==[(m,d,n) for m,d,n in zip(('G','y','r'),phase,(1,2,0))],'FULL_CATALOGUE_XML_DRIFT')
    require(not(root/output(run)).parent.exists(),'ONE_USE_IDENTITY_CONSUMED')
    if require_environment:static_environment(root,c['environment'])
    return c

def validate_release(card_path,release_path,root=ROOT):
    root=Path(root).resolve();c=validate(card_path,root,require_environment=True);run=c['spec']['run_id']
    auth_path=root/TASK/'authorizations'/run/'AUTHORIZATION_NATIVE_EXECUTION.json'
    require(auth_path.is_file(),'FUTURE_EXACT_NATIVE_AUTHORIZATION_MISSING')
    auth=json.loads(auth_path.read_text());expected=root/TASK/'releases'/run/'EXECUTION_RELEASE.json'
    require(auth.get('SUMO_execution_authorized') is True and auth.get('run_id')==run and auth.get('card_sha256')==sha(Path(card_path)),'FUTURE_NATIVE_AUTHORIZATION_UNBOUND')
    ref=Path(auth['human_authorization_reference']);require(not ref.is_absolute() and '..' not in ref.parts and ref!=USER,'CANNOT_INHERIT_OFFLINE_AUTHORITY')
    human=json.loads((root/ref).read_text());require(sha(root/ref)==auth['human_authorization_sha256'],'FUTURE_HUMAN_APPROVAL_DRIFT')
    require(human.get('source')=='direct human explicit execution approval' and human.get('SUMO_execution_authorized') is True and
        human.get('run_id')==run and human.get('card_sha256')==sha(Path(card_path)) and human.get('common_runtime_source_sha256')==c['common_runtime_source_sha256'] and
        human.get('end_s')==c['spec']['end_s'] and human.get('catalogue_periods_s')==list(range(8,25)) and human.get('mode')==c['spec']['mode'] and human.get('numerical_exception_enabled') is False and human.get('resources')==c['resources'] and human.get('resource_envelope')==c['proposed_new_single_run_envelope'],
        'FUTURE_HUMAN_RUN_SOURCE_STRICT_NUM_RESOURCE_APPROVAL_UNBOUND')
    require(auth.get('numerical_exception_enabled') is False and auth.get('resources')==c['resources'] and auth.get('resource_envelope')==c['proposed_new_single_run_envelope'],'FUTURE_NATIVE_CAPS_OR_NUM_UNBOUND')
    require(Path(release_path).resolve()==expected and expected.is_file(),'FUTURE_CANONICAL_RELEASE_MISSING')
    release=json.loads(expected.read_text());require(release.get('run_id')==run and release.get('card_sha256')==sha(Path(card_path)) and release.get('SUMO_execution_authorized') is True and
        release.get('authorization_sha256')==sha(auth_path),'FUTURE_RELEASE_UNBOUND')
    require(set(release.get('reviews',{}))=={'engineering','data','science'},'FUTURE_THREE_ROLE_RELEASE_MISSING')
    for item in release['reviews'].values():require(sha(root/item['path'])==item['sha256'] and item.get('card_sha256')==sha(Path(card_path)),'FUTURE_REVIEW_HASH_OR_CARD_UNBOUND')
    audit=release['reviews']['data']
    require(audit.get('audit_contract')=='CUMULATIVE_FULL_C_N_V1' and
        audit.get('actual_reader_path')=='scripts/cumulative_full_catalogue_followup_audit_20261014_v1/actual.py' and
        sha(root/audit['actual_reader_path'])==audit.get('actual_reader_sha256'),
        'CUMULATIVE_ACTUAL_READER_NOT_REVIEWED_AND_BOUND')
    return c

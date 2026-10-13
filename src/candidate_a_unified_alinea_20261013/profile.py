"""Approved isolated unified technical cards; prepare is not runtime authorization."""
from pathlib import Path
import json
import re
import hashlib
import xml.etree.ElementTree as ET
from src.candidate_a_issue12_packet_policy_20261012 import profile as old
from src.candidate_a_unified_alinea_20261013 import budget
from src.candidate_a_unified_alinea_20261013.policy import parameters, PERIODS
ROOT=old.ROOT;NETWORK=old.NETWORK;SUMO=old.SUMO
BASE='9eb95e29ccc85423084bc6945668cd36c3298b06'
TASK=Path('artifacts/unified_alinea_actuator_20261013_v1/engineering')
USER=TASK.parent/'USER_SCOPE_APPROVAL.json'
SCOPE=TASK.parent/'SCOPE_AS_APPROVED.md'
RUN='UA_FIXED300_S17_02'
sha=old.sha;write_new=old.write_new;require=old.require
MODES={'FIXED300':('fixed300',300,1272),'FIXED750':('fixed750',750,1270),
       'DYNAMIC':('dynamic_commands',300,1266),'ALINEA':('real_alinea',900,1272)}


def spec(run):
    m=re.fullmatch(r'UA_(FIXED300|FIXED750|DYNAMIC|ALINEA)_S17_([0-9]{2})',run)
    require(m is not None and int(m[2])>=1,'UNKNOWN_APPROVED_IDENTITY')
    mode,rate,end=MODES[m[1]]
    return {**old.spec(old.RUN),'run_id':run,'end_s':end,'mode':mode,
        'fixed_command_veh_h':rate,'service_command_veh_h':rate,'period_s':None,
        'phase_durations_s':None,'complete_cycles_target':None,
        'input_origin':'PROJECT_FEEDBACK' if mode=='real_alinea' else mode,
        'total_resource_envelope':{'monitored_s':1200,'raw_bytes':1200000000},
        'feedback_reference':{'target_pct':11,'gain_veh_h_per_pct':70,'minimum_veh_h':300,
            'maximum_veh_h':900,'initial_veh_h':900,'global_activation_s':1200,
            'logical_activation_s':600,'update_global_s':[1230,1260],
            'detector_ids':['p1_main_down_20_l0','p1_main_down_20_l1']} if mode=='real_alinea' else None,
        'requested_schedule':{'1200':300,'1201':750,'1226':900,'1237':300} if mode=='dynamic_commands' else None,
        'partial_final_cycle_allowed':mode=='real_alinea',
        'interpretation':'BOUNDED_TECHNICAL_NOT_FORMAL_OR_LONG_TERM_QUALIFICATION'}


def output(run):spec(run);return budget.RAW/run/'outputs'
def resources(run):spec(run);return dict(wall_limit_s=300,startup_limit_s=60,run_limit_bytes=300000000,minimum_free_bytes=5000000000)


def sources(root):
    files=old.sources(root)
    for folder in ('src/candidate_a_unified_alinea_20261013','scripts/candidate_a_unified_alinea_20261013_v1'):
        for p in (root/folder).glob('*.py'):files[str(p.relative_to(root))]=sha(p)
    for p in (USER,SCOPE,Path('scripts/formal_development_20261007_v1/control.py'),
              Path('scripts/formal_development_20261007_v1/v15_worker.py')):
        files[str(p)]=sha(root/p)
    return dict(sorted(files.items()))


def common_source_digest(root):
    return hashlib.sha256(json.dumps(sources(root),sort_keys=True,separators=(',',':')).encode()).hexdigest()


def stage_package(root,package,out,end):
    inherited=old.stage_package(root,package,out)
    p=package/'scenario.sumocfg';tree=ET.parse(p);tree.getroot().find('./time/end').set('value',str(end))
    ET.indent(tree);tree.write(p,encoding='utf-8',xml_declaration=True)
    p=package/'scenario.add.xml';tree=ET.parse(p);r=tree.getroot()
    original=r.find("tlLogic[@programID='I12_PACKET8']");require(original is not None,'PARENT_PHASE_XML_MISSING');r.remove(original)
    for period in PERIODS:
        par=parameters(period);logic=ET.SubElement(r,'tlLogic',dict(id='ramp_mid',type='static',programID=par['program'],offset='0'))
        for state,duration,nxt in par['phases']:
            ET.SubElement(logic,'phase',dict(duration=str(duration),state=state,next=str(nxt)))
    ET.indent(tree);tree.write(p,encoding='utf-8',xml_declaration=True)
    return inherited


def prepare(run=RUN,root=ROOT):
    root=Path(root).resolve();sp=spec(run);package=root/TASK/'packages'/run;out=root/output(run)
    require(not out.parent.exists(),'ONE_USE_IDENTITY_CONSUMED')
    card=package/'card.json'
    if card.exists():validate(card,root);return card
    inherited=stage_package(root,package,out,sp['end_s'])
    previous=json.loads((root/old.TASK/'packages'/old.RUN/'card.json').read_text())
    data=dict(classification='BOUNDED_UNIFIED_NATIVE_TECHNICAL_DIAGNOSTIC_NOT_FORMAL',status='PREPARED_NOT_RELEASED',
        baseline_commit=BASE,spec=sp,package=str(package.relative_to(root)),output=str(output(run)),
        user_authorization={'path':str(USER),'sha256':sha(root/USER)},sources_sha256=sources(root),
        common_runtime_source_sha256=common_source_digest(root),
        inherited_inputs_sha256=inherited,network_sha256=sha(root/NETWORK),
        prepared_input_sha256={str(p.relative_to(root)):sha(p) for p in package.iterdir() if p.is_file()},
        resources=resources(run),total_budget_preparation_snapshot=budget.accounting(root),environment=old.old.base.environment(),
        runtime_authorization_generated=False,source_binary_compiler_equivalence='NOT_VERIFIED',
        binary_reference_provenance=previous['binary_reference_provenance'],
        interpretation={'native_safety_proven':False,'rate_qualified':False,'new_source_native_900_tested':False})
    write_new(card,data);return card


def validate(card_path,root=ROOT,require_environment=False):
    root=Path(root).resolve();p=Path(card_path).resolve();c=json.loads(p.read_text());run=c['spec']['run_id'];sp=spec(run)
    expected=root/TASK/'packages'/run/'card.json'
    require(p==expected and c['spec']==sp and c['baseline_commit']==BASE,'CARD_IDENTITY_SPEC_DRIFT')
    require(c['status']=='PREPARED_NOT_RELEASED' and c['classification']=='BOUNDED_UNIFIED_NATIVE_TECHNICAL_DIAGNOSTIC_NOT_FORMAL','CARD_STAGE_DRIFT')
    require(c['package']==str(expected.parent.relative_to(root)) and c['output']==str(output(run)),'CARD_PATH_DRIFT')
    require(c['resources']==resources(run) and c['sources_sha256']==sources(root),'SOURCE_RESOURCE_DRIFT')
    require(c['common_runtime_source_sha256']==common_source_digest(root),'COMMON_RUNTIME_DRIFT')
    require(c['user_authorization']=={'path':str(USER),'sha256':sha(root/USER)},'APPROVAL_DRIFT')
    approval=json.loads((root/USER).read_text());require(approval['scope_sha256']==sha(root/SCOPE),'APPROVED_SCOPE_DRIFT')
    for key in ('inherited_inputs_sha256','prepared_input_sha256'):
        for name,h in c[key].items():require(sha(root/name)==h,'INPUT_DRIFT '+name)
    require(sha(root/NETWORK)==c['network_sha256'],'NETWORK_DRIFT')
    cfg=ET.parse(expected.parent/'scenario.sumocfg').getroot()
    require(cfg.find('./time/end').get('value')==str(sp['end_s']) and cfg.find('./time/step-length').get('value')=='1','HORIZON_STEP_DRIFT')
    require(cfg.find('./output/precision').get('value')=='8','PRECISION_DRIFT')
    add=ET.parse(expected.parent/'scenario.add.xml').getroot()
    for period in PERIODS:
        par=parameters(period);logic=add.find(f"tlLogic[@programID='{par['program']}']")
        require(logic is not None and [(x.get('state'),int(x.get('duration')),int(x.get('next'))) for x in logic]==list(par['phases']),'PHASE_LIBRARY_DRIFT')
    protected=json.loads((root/'artifacts/candidate_a_a1_contract_20261011_v1/engineering/PROTECTED_BASELINE_SHA256.json').read_text())['files']
    require(len(protected)==536 and all(sha(root/n)==h for n,h in protected.items()),'PROTECTED_SOURCE_DRIFT')
    require(not (root/output(run)).parent.exists(),'ONE_USE_IDENTITY_CONSUMED')
    if require_environment:
        require(c['environment']['complete'] and c['environment']==old.old.base.environment(),'ENVIRONMENT_DRIFT')
        for tag,path in [('net-file',root/NETWORK),('route-files',expected.parent/'demand.rou.xml'),('additional-files',expected.parent/'scenario.add.xml')]:
            require(Path(cfg.find('./input/'+tag).get('value')).resolve()==path.resolve(),'FOREIGN_INPUT')
        for node in cfg.findall('./output/*')+cfg.findall('./report/*'):
            value=node.get('value','')
            if value.startswith('/'):require(Path(value).resolve().parent==(root/output(run)).resolve(),'FOREIGN_OUTPUT')
        for node in add.iter():
            for attr in ('file','dest'):
                if attr in node.attrib:require(Path(node.get(attr)).resolve().parent==(root/output(run)).resolve(),'FOREIGN_DETECTOR_OUTPUT')
    return c


def validate_release(card_path,release_path,root=ROOT):
    root=Path(root).resolve();c=validate(card_path,root,True);run=c['spec']['run_id']
    ap=root/TASK/'authorization'/run/'AUTHORIZATION_NATIVE_EXECUTION.json'
    rp=root/TASK/'releases'/run/'EXECUTION_RELEASE.json'
    require(ap.is_file() and rp.is_file() and Path(release_path).resolve()==rp,'CANONICAL_PERMISSION_MISSING')
    a=json.loads(ap.read_text());v=json.loads(rp.read_text())
    require(a.get('SUMO_execution_authorized') is True and a.get('run_id')==run and a.get('card_sha256')==sha(card_path),'AUTHORIZATION_DRIFT')
    require(a.get('human_authorization_reference')==str(USER) and a.get('human_authorization_sha256')==sha(root/USER),'HUMAN_SCOPE_BINDING_DRIFT')
    require(v.get('run_id')==run and v.get('card_sha256')==sha(card_path) and v.get('authorization_sha256')==sha(ap) and v.get('automatic_continuation') is False,'RELEASE_DRIFT')
    reviews=v.get('review_sha256');require(isinstance(reviews,dict) and set(reviews)=={'engineering','data','science'},'THREE_ROLE_RELEASE_MISSING')
    for item in reviews.values():require(sha(root/item['path'])==item['sha256'],'REVIEW_DRIFT')
    budget.accounting(root)
    return c

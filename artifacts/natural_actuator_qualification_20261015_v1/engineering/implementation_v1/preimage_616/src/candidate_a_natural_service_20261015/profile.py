"""Natural input/card preparation. Numeric budget and release remain separate."""
from pathlib import Path
import copy
import hashlib
import json
import shutil
import xml.etree.ElementTree as ET
from src.candidate_a_unified_alinea_20261013.profile import ROOT, NETWORK, SUMO, sha, write_new, require
from src.candidate_a_natural_service_20261015.policy import parameters, PERIODS

TASK = Path('artifacts/thesis_actuator_readiness_20261015_v1/engineering')
NATURAL = Path('artifacts/formal_development_20261007_v1/inputs/DEV_M3600_R900_S17_T1_A03')
RAW = Path('data/raw/thesis_actuator_readiness_20261015_v1')
APPROVED_BOUND_END = 4200
RUN = 'NATURAL_ALINEA_R900_S17_01'
USER = Path('artifacts/thesis_actuator_readiness_20261015_v1/USER_AUTHORITY.md')
READER = Path('scripts/natural_service_audit_20261015_v1/actual.py')
LEGACY_CARD = Path('artifacts/dynamic_native_yellow_minqual_20261015_v1/engineering/packages_v1/UA_NATIVEYELLOW_DYNAMIC_S17_01/card.json')


def spec():
    return dict(run_id=RUN, mode='real_alinea', fixed_command_veh_h=900,
        activation_s=600, end_s=4200, scheduler='RAW_C_MINUS_SCHEDULED_NOMINAL_E',
        Feedback=dict(target_percent=11, gain_veh_h_per_percentage_point=70,
            bounds_veh_h=[300,900], initial_veh_h=900, sample_s=30),
        counts=dict(M=3000,R=600,U=300,X=150), seed=17,
        yellow_responsibility_contract=dict(policy='NATIVE_YELLOW_RESPONSIBILITY_COMPLETE_INPUT_DIAGNOSTIC_V1', enabled=True),
        qualification='NOT_TESTED_NOT_QUALIFIED')


def stage_package(root, package, output, end=4200):
    """Copy unchanged natural requests, add only existing packet TLS programs."""
    require(type(end) is int and 600 < end <= 4200, 'NATURAL_HORIZON')
    package.mkdir(parents=True, exist_ok=False)
    for name in ('demand.rou.xml','scenario.sumocfg','scenario.add.xml'):
        shutil.copyfile(root/NATURAL/name, package/name)
    route = ET.parse(package/'demand.rou.xml').getroot()
    require(all(float(v.get('depart')) >= 600 for v in route.findall('vehicle') if v.get('id','').startswith('R_')),
            'UNSUPPORTED_PRECONTROL_R_REQUEST')
    tree = ET.parse(package/'scenario.sumocfg')
    for tag, value in [('net-file',root/NETWORK),('route-files',package/'demand.rou.xml'),('additional-files',package/'scenario.add.xml')]:
        tree.find('./input/'+tag).set('value',str(value))
    tree.find('./time/end').set('value',str(end))
    for node in tree.findall('./output/*')+tree.findall('./report/*'):
        if node.get('value','').startswith('/'):
            node.set('value',str(output/Path(node.get('value')).name))
    ET.indent(tree);tree.write(package/'scenario.sumocfg',encoding='utf-8',xml_declaration=True)
    tree = ET.parse(package/'scenario.add.xml');r=tree.getroot()
    for node in r.iter():
        for key in ('file','dest'):
            if key in node.attrib:node.set(key,str(output/Path(node.get(key)).name))
    for period in PERIODS:
        p=parameters(period)
        logic=ET.SubElement(r,'tlLogic',dict(id='ramp_mid',type='static',programID=p['program'],offset='0'))
        for state,duration,nxt in p['phases']:
            ET.SubElement(logic,'phase',dict(state=state,duration=str(duration),next=str(nxt)))
    ET.indent(tree);tree.write(package/'scenario.add.xml',encoding='utf-8',xml_declaration=True)


def sources(root):
    previous=json.loads((root/LEGACY_CARD).read_text())['sources_sha256']
    require(all(sha(root/p)==h for p,h in previous.items()), 'HISTORICAL154_SOURCE_DRIFT')
    result=dict(previous)
    for folder in ('src/candidate_a_natural_service_20261015','tests/candidate_a_natural_service_20261015',
                   'scripts/candidate_a_natural_service_20261015_v1','scripts/natural_service_audit_20261015_v1'):
        for p in (root/folder).glob('*.py'):result[str(p.relative_to(root))]=sha(p)
    require((root/READER).is_file(), 'INDEPENDENT_NATURAL_READER_NOT_READY')
    result[str(USER)]=sha(root/USER)
    return dict(sorted(result.items()))


def prepare(root=ROOT):
    root=Path(root).resolve();source=sources(root)
    package=root/TASK/'natural_package_v1'/RUN;output=root/RAW/RUN/'outputs'
    require(not output.parent.exists(), 'ONE_USE_IDENTITY_CONSUMED')
    stage_package(root,package,output)
    donor=json.loads((root/LEGACY_CARD).read_text())
    natural=json.loads((root/NATURAL/'card.json').read_text())
    card=dict(status='PREPARED_NOT_RELEASED',SUMO_execution_authorized=False,
        classification='NATURAL_TECHNICAL_NOT_FORMAL',spec=spec(),
        package=str(package.relative_to(root)),output=str(output.relative_to(root)),
        sources_sha256=source,common_runtime_source_sha256=hashlib.sha256(json.dumps(source,sort_keys=True,separators=(',',':')).encode()).hexdigest(),
        inherited_inputs_sha256={str(NATURAL/name):sha(root/NATURAL/name) for name in ('card.json','demand.rou.xml','scenario.add.xml','scenario.sumocfg')},
        prepared_input_sha256={str(p.relative_to(root)):sha(p) for p in package.iterdir() if p.is_file()},
        network_sha256=natural['network_sha256'],environment=donor['environment'],
        resources=dict(wall_limit_s=900,startup_limit_s=60,run_limit_bytes=None,minimum_free_bytes=5000000000),
        resources_status='PROPOSED_PENDING_NUMERIC_BUDGET_APPROVAL',
        numerical_exception_authority=dict(enabled=False),
        user_authorization=dict(path=str(USER),sha256=sha(root/USER),scope='IMPLEMENTATION_AND_PREPARATION_NUMERIC_BUDGET_PENDING'),
        audit_contract=dict(reader=str(READER),status='NEW_READER_REVIEW_REQUIRED'),
        qualification='NOT_TESTED_NOT_QUALIFIED')
    write_new(package/'card.json',card)
    return package/'card.json'


def validate_release(card_path, release_path, root=ROOT):
    """Fail before allocation/launch unless exact new authority is supplied."""
    from src.candidate_a_natural_service_20261015 import budget
    root=Path(root).resolve();p=Path(card_path).resolve()
    require(p==root/TASK/'natural_package_v1'/RUN/'card.json', 'FOREIGN_NATURAL_CARD')
    c=json.loads(p.read_text());require(c['spec']==spec() and c['SUMO_execution_authorized'] is False,'NATURAL_SPEC_DRIFT')
    require(c['sources_sha256']==sources(root),'NATURAL_SOURCE_DRIFT')
    for group in ('prepared_input_sha256','inherited_inputs_sha256'):
        require(all(sha(root/path)==h for path,h in c[group].items()),'NATURAL_INPUT_DRIFT')
    require(sha(root/NETWORK)==c['network_sha256'],'NATURAL_NETWORK_DRIFT')
    # Missing numeric approval is an explicit pending gate, not inferred from
    # the general goal, maximum starts, old remainder or proposed900s value.
    bound=budget.accounting(root)
    r=json.loads(Path(release_path).read_text())
    require(r['status']=='CANONICAL_NATURAL_EXECUTION_RELEASE' and r['card_sha256']==sha(p),'NATURAL_CANONICAL_RELEASE_MISMATCH')
    require(r['budget_approval_sha256']==bound['budget_approval_sha256'],'NATURAL_BUDGET_BINDING_MISMATCH')
    require(set(r['reviews'])=={'engineering','data','science'},'MISSING_NATURAL_REVIEWS')
    for item in r['reviews'].values():require(sha(root/item['path'])==item['sha256'],'NATURAL_REVIEW_DRIFT')
    require(r['user_authority']['path']==str(USER) and r['user_authority']['sha256']==sha(root/USER),'NATURAL_USER_SCOPE_DRIFT')
    require(c['environment']['python']=='.'.join(map(str,__import__('sys').version_info[:3])), 'PYTHON_ENVIRONMENT_DRIFT')
    require(all(sha(Path(path))==h for path,h in c['environment']['files_sha256'].items()),'NATIVE_ENVIRONMENT_FILE_DRIFT')
    return c

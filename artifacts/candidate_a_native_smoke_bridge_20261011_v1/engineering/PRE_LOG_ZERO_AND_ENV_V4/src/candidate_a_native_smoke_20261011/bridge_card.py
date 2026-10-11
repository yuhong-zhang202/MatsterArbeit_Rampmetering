"""Offline packaging and exact-card gates. Never executes native binaries."""
from pathlib import Path
import hashlib
import importlib.metadata
import json
import platform
import shutil
import sys
import xml.etree.ElementTree as ET

ROOT=Path(__file__).resolve().parents[2]
TASK=Path('artifacts/candidate_a_native_smoke_bridge_20261011_v1')
RUN='CA_NATIVE_PHASE_R300_S17_SMOKE01'
NETWORK=Path('artifacts/stage6_baseline_localization_20260921_v1/LOC_M3350_S17/engineering/build_attempts/TV_BUILD01/network.net.xml')
OLD=Path('config/candidate_a_qualification_20261008_v1/CA_FIXED_R300_S17_A07')
SUMO=Path('/Library/Frameworks/EclipseSUMO.framework/Versions/1.26.0/EclipseSUMO/bin/sumo')
BASE='833ac18db2c6b256f2782631830c9c849e090681'
SPEC={'run_id':RUN,'seed':17,'qMain':3600,'qRamp':900,'qUrban':360,'qCross':180,
      'service_command_veh_h':300,'step_s':1,'activation_s':1200,'end_s':1207,
      'phase_durations_s':[3,3,18],'initial_hold_s':[600,1200],
      'first_red_mandatory_pause':True,'automatic_continuation':False}


def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def write_new(path, value):
    with Path(path).open('x') as f:json.dump(value,f,indent=2,allow_nan=False);f.write('\n')


def require(condition, why):
    if not condition:raise ValueError(why)


def environment(binary=SUMO):
    files={str(Path(sys.executable).resolve()):sha(Path(sys.executable).resolve())}
    versions={}
    for name in ['traci','sumolib','sumoITScontrol']:
        try:
            d=importlib.metadata.distribution(name);versions[name]=d.version
            for f in d.files or []:
                if str(f).endswith('.py'):
                    p=Path(d.locate_file(f)).resolve()
                    if p.is_file():files[str(p)]=sha(p)
        except importlib.metadata.PackageNotFoundError:versions[name]=None
    if binary.is_file():files[str(binary)]=sha(binary)
    schemas=[binary.parent.parent/'share/sumo/data/xsd'/name for name in ['routes_file.xsd','additional_file.xsd','sumoConfiguration.xsd']]
    for p in schemas:
        if p.is_file():files[str(p)]=sha(p)
    return {'python':platform.python_version(),'packages':versions,'files_sha256':files,
            'binary':str(binary),'schema_files_present':all(p.is_file() for p in schemas),'complete':binary.is_file() and all(p.is_file() for p in schemas) and versions=={'traci':'1.26.0','sumolib':'1.26.0','sumoITScontrol':'0.1.0'},
            'native_version_executed':False}


def sources(root):
    names=['src/candidate_a_qualification_20261008/actor.py','src/candidate_a_qualification_20261008/safety.py',
        'scripts/candidate_a_qualification_20261008_v1/worker.py','scripts/candidate_a_qualification_20261008_v1/runner.py',
        'scripts/formal_development_20261007_v1/v15_worker.py','scripts/formal_development_20261007_v1/control.py',
        'scripts/formal_development_20261007_v1/safe_actuator_fix02.py','src/stage6_safe_actuator_v10.py',
        'src/candidate_a_native_smoke_20261011/adapter.py','config/candidate_a_qualification_20261008_v1/PHASE_RATE_CONTRACT.json']
    names += [str(p.relative_to(root)) for folder in ['src/candidate_a_native_smoke_20261011','scripts/candidate_a_native_smoke_bridge_20261011_v1'] for p in (root/folder).glob('*.py')]
    return {n:sha(root/n) for n in sorted(set(names))}


def stage_package(root, package, output):
    """Copy protected generated native program/demand; only paths/end/logging change."""
    package.mkdir(parents=True,exist_ok=False)
    shutil.copyfile(root/OLD/'demand.rou.xml',package/'demand.rou.xml')
    inputs={str(OLD/f):sha(root/OLD/f) for f in ['demand.rou.xml','scenario.add.xml','scenario.sumocfg']}
    for name in ['scenario.add.xml','scenario.sumocfg']:
        tree=ET.parse(root/OLD/name);x=tree.getroot()
        if name.endswith('add.xml'):
            for node in x.iter():
                for attr in ['file','dest']:
                    if attr in node.attrib:node.set(attr,str(output/Path(node.get(attr)).name))
        else:
            x.find('./input/net-file').set('value',str(root/NETWORK))
            x.find('./input/route-files').set('value',str(package/'demand.rou.xml'))
            x.find('./input/additional-files').set('value',str(package/'scenario.add.xml'))
            x.find('./time/end').set('value','1207')
            for node in x.findall('./output/*')+x.findall('./report/*'):
                value=node.get('value','')
                if value.startswith('/'):node.set('value',str(output/Path(value).name))
            for key,value in [('no-warnings','false'),('aggregate-warnings','-1')]:
                node=x.find('./report/'+key)
                if node is None:node=ET.SubElement(x.find('./report'),key)
                node.set('value',value)
        ET.indent(tree);tree.write(package/name,encoding='utf-8',xml_declaration=True)
    require(sha(package/'demand.rou.xml')==inputs[str(OLD/'demand.rou.xml')],'demand copy drift')
    phases=ET.parse(package/'scenario.add.xml').getroot().find("tlLogic[@programID='CA_C24']")
    require(phases is not None and [(p.get('state'),p.get('duration'),p.get('next')) for p in phases]==[('G','3','1'),('y','3','2'),('r','18','2')],'native phase XML drift')
    return inputs


def prepare(root=ROOT):
    root=Path(root).resolve()
    package=root/TASK/'engineering/packages'/RUN
    output=root/'data/raw/candidate_a_native_smoke_bridge_20261011_v1'/RUN/'outputs'
    require(not output.parent.exists(),'run output already consumed')
    if (package/'card.json').is_file():
        validate(package/'card.json',root,require_environment=False)
        return package/'card.json'
    inherited=stage_package(root,package,output)
    card={'classification':'ISOLATED_NATIVE_PHASE_TECHNICAL_SMOKE_NOT_FORMAL','status':'PREPARED_NOT_RELEASED',
          'baseline_commit':BASE,'spec':SPEC,'package':str(package.relative_to(root)),
          'output':str(output.relative_to(root)),'sources_sha256':sources(root),
          'inherited_inputs_sha256':inherited,'network_sha256':sha(root/NETWORK),
          'prepared_input_sha256':{str(p.relative_to(root)):sha(p) for p in package.glob('*.xml')},
          'environment':environment(),'resources':{'wall_limit_s':180,'startup_limit_s':60,'run_limit_bytes':300_000_000,'minimum_free_bytes':5_000_000_000},
          'resource_status':'INHERITED_REFERENCE_REQUIRES_EXACT_FUTURE_APPROVAL',
          'runtime_authorization_generated':False,'source_binary_compiler_equivalence':'NOT_VERIFIED'}
    card['prepared_input_sha256'][str((package/'scenario.sumocfg').relative_to(root))]=sha(package/'scenario.sumocfg')
    write_new(package/'card.json',card)
    return package/'card.json'


def validate(card_path, root=ROOT, require_environment=False):
    root=Path(root).resolve();card_path=Path(card_path).resolve()
    expected=root/TASK/'engineering/packages'/RUN/'card.json'
    require(card_path==expected,'card path/identity is not canonical')
    card=json.loads(card_path.read_text())
    require(card.get('classification')=='ISOLATED_NATIVE_PHASE_TECHNICAL_SMOKE_NOT_FORMAL' and card.get('status')=='PREPARED_NOT_RELEASED' and card.get('spec')==SPEC,'card specification mismatch')
    require(card['package']==str((expected.parent).relative_to(root)) and card['output']==str(Path('data/raw/candidate_a_native_smoke_bridge_20261011_v1')/RUN/'outputs'),'unsafe package/output path')
    require(card['sources_sha256']==sources(root),'source snapshot drift')
    for key in ['prepared_input_sha256','inherited_inputs_sha256']:
        for p,h in card[key].items():require(sha(root/p)==h,'input drift '+p)
    require(card['network_sha256']==sha(root/NETWORK),'network drift')
    protected=json.loads((root/'artifacts/candidate_a_a1_contract_20261011_v1/engineering/PROTECTED_BASELINE_SHA256.json').read_text())['files']
    require(len(protected)==536 and all(sha(root/p)==h for p,h in protected.items()),'protected drift')
    if require_environment:
        cfg=ET.parse(root/card['package']/'scenario.sumocfg').getroot()
        expected_inputs={'net-file':root/NETWORK,'route-files':root/card['package']/'demand.rou.xml','additional-files':root/card['package']/'scenario.add.xml'}
        for tag,path in expected_inputs.items():require(Path(cfg.find('./input/'+tag).get('value')).resolve()==path.resolve(),'foreign runtime input root '+tag)
        for node in cfg.findall('./output/*')+cfg.findall('./report/*'):
            value=node.get('value','')
            if value.startswith('/'):require(Path(value).resolve().parent==(root/card['output']).resolve(),'foreign native output root')
        additional=ET.parse(root/card['package']/'scenario.add.xml').getroot()
        for node in additional.iter():
            for attr in ['file','dest']:
                if attr in node.attrib:require(Path(node.get(attr)).resolve().parent==(root/card['output']).resolve(),'foreign detector output root')
        require(card['environment']['complete'] and card['environment']==environment(),'runtime binary/dependency/environment drift')
        require(card['environment']['files_sha256'].get(str(SUMO))=='3bd1eaa3b167fb527ac33b154dfb57b41b9a40d5bc3e26246489824dd7977179','unbound SUMO binary')
    return card


def validate_release(card_path, release_path, root=ROOT):
    root=Path(root).resolve()
    # Every execute call fails here this round: canonical future authorization
    # does not exist and offline prepare never creates it.
    authorization=root/TASK/'AUTHORIZATION_NATIVE_EXECUTION.json'
    require(authorization.is_file(),'explicit future native execution authorization missing')
    auth=json.loads(authorization.read_text())
    require(auth.get('SUMO_execution_authorized') is True and auth.get('run_id')==RUN and auth.get('card_sha256')==sha(card_path) and isinstance(auth.get('human_authorization_reference'),str) and auth['human_authorization_reference'],'no exact human execution authorization')
    expected=root/TASK/'engineering/EXECUTION_RELEASE.json'
    require(Path(release_path).resolve()==expected and expected.is_file(),'canonical exact-card release missing')
    release=json.loads(expected.read_text())
    require(release.get('run_id')==RUN and release.get('card_sha256')==sha(card_path) and release.get('authorization_sha256')==sha(authorization) and release.get('automatic_continuation') is False,'release does not bind exact approved card')
    reviews=release.get('review_sha256')
    require(isinstance(reviews,dict) and set(reviews)=={'engineering','data','science'},'all review receipts required')
    for entry in reviews.values():
        require(isinstance(entry,dict) and sha(root/entry['path'])==entry['sha256'],'review receipt drift')
    return validate(card_path,root,require_environment=True)

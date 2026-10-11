"""SMOKE02 identity/config gates; reuse SMOKE01 pure package/env/hash helpers.

No old globals are patched and no native process/connection at import/default.
"""
from pathlib import Path
import json
import xml.etree.ElementTree as ET
from src.candidate_a_native_smoke_20261011 import bridge_card as base

ROOT=base.ROOT
TASK=Path('artifacts/candidate_a_native_smoke_selfloop_fix_20261011_v1')
RUN='CA_NATIVE_PHASE_R300_S17_SMOKE02'
NETWORK=base.NETWORK
SUMO=base.SUMO
SPEC={**base.SPEC,'run_id':RUN}
BASE='09d77dab8d19f414277ade5b399675f0e4e13f01'
OUTPUT=Path('data/raw/candidate_a_native_smoke_selfloop_fix_20261011_v1')/RUN/'outputs'
sha=base.sha
write_new=base.write_new
require=base.require


def selfloop_warning_indices(logic):
    """Static replay of the pinned init predicate only, not native validation."""
    phases=list(logic)
    if len(phases)<=1:return []
    found=[]
    for i,phase in enumerate(phases):
        raw=phase.get('next','')
        nxt=[int(n) for n in raw.split()] if raw else [(i+1)%len(phases)]
        if nxt==[i]:found.append(i)
    return found


def sources(root):
    files=base.sources(root)
    for folder in ['src/candidate_a_native_smoke_selfloop_fix_20261011','scripts/candidate_a_native_smoke_selfloop_fix_20261011_v1']:
        for p in (root/folder).glob('*.py'):files[str(p.relative_to(root))]=sha(p)
    return dict(sorted(files.items()))


def stage_package(root, package, output):
    inherited=base.stage_package(root,package,output)
    path=package/'scenario.add.xml';tree=ET.parse(path);x=tree.getroot()
    # Only the two used multi-phase programs. A_OPEN comes from the network.
    for logic in list(x.findall('tlLogic')):
        if logic.get('programID') not in ['CA_C8','CA_C24']:x.remove(logic)
    holding=x.find("tlLogic[@programID='CA_C8']")
    require(holding is not None,'missing native holding program')
    holding[2].set('duration','600');holding[2].set('next','0')
    controlled=x.find("tlLogic[@programID='CA_C24']")
    controlled[2].set('next','0')
    ET.indent(tree);tree.write(path,encoding='utf-8',xml_declaration=True)
    require([(p.get('state'),p.get('duration'),p.get('next')) for p in holding]==[('G','3','1'),('y','3','2'),('r','600','0')],'holding semantics drift')
    require([(p.get('state'),p.get('duration'),p.get('next')) for p in controlled]==[('G','3','1'),('y','3','2'),('r','18','0')],'controlled semantics drift')
    return inherited


def prepare(root=ROOT):
    root=Path(root).resolve();package=root/TASK/'engineering/packages'/RUN;output=root/OUTPUT
    require(not output.parent.exists(),'new identity output already consumed')
    card=package/'card.json'
    if card.is_file():validate(card,root);return card
    inherited=stage_package(root,package,output)
    old_card=json.loads((root/base.TASK/'engineering/packages'/base.RUN/'card.json').read_text())
    data={'classification':'ISOLATED_NATIVE_PHASE_TECHNICAL_SMOKE_NOT_FORMAL','status':'PREPARED_NOT_RELEASED','baseline_commit':BASE,'spec':SPEC,
          'package':str(package.relative_to(root)),'output':str(OUTPUT),'sources_sha256':sources(root),'inherited_inputs_sha256':inherited,
          'network_sha256':sha(root/NETWORK),'prepared_input_sha256':{str(p.relative_to(root)):sha(p) for p in package.iterdir() if p.is_file()},
          'environment':base.environment(),'resources':old_card['resources'],'resources_provenance':old_card['resources_provenance'],
          'binary_reference_provenance':old_card['binary_reference_provenance'],'source_binary_compiler_equivalence':'NOT_VERIFIED','runtime_authorization_generated':False,
          'configuration_delta':{'holding_program_legacy_name':'CA_C8','holding_actual_cycle_s':606,'holding_yellow_start_s':600,'holding_red_start_s':603,'holding_red_duration_s':600,'holding_native_next_green_s':1203,'holding_control_replacement_s':1200,'controlled_red_next':'0','controlled_next_green_s':1224,'programs_removed':[f'CA_C{i}' for i in range(9,24)],'scope_end_s':1207,'future_cycles_validated':False}}
    write_new(card,data);return card


def validate(card_path,root=ROOT,require_environment=False):
    root=Path(root).resolve();p=Path(card_path).resolve();expected=root/TASK/'engineering/packages'/RUN/'card.json'
    require(p==expected,'new card path is not canonical');c=json.loads(p.read_text())
    require(c.get('classification')=='ISOLATED_NATIVE_PHASE_TECHNICAL_SMOKE_NOT_FORMAL' and c.get('status')=='PREPARED_NOT_RELEASED' and c.get('spec')==SPEC,'new card identity/spec drift')
    require(c.get('package')==str(expected.parent.relative_to(root)) and c.get('output')==str(OUTPUT),'new package/output identity drift')
    require(c['sources_sha256']==sources(root),'new or protected source drift')
    for key in ['prepared_input_sha256','inherited_inputs_sha256']:
        for name,h in c[key].items():require(sha(root/name)==h,'input drift '+name)
    require(c['network_sha256']==sha(root/NETWORK),'network drift')
    protected=json.loads((root/'artifacts/candidate_a_a1_contract_20261011_v1/engineering/PROTECTED_BASELINE_SHA256.json').read_text())['files']
    require(len(protected)==536 and all(sha(root/name)==h for name,h in protected.items()),'protected drift')
    require(not (root/OUTPUT).parent.exists(),'identity consumed')
    if require_environment:
        require(c['environment']['complete'] and c['environment']==base.environment(),'native environment drift')
        require(c['environment']['files_sha256'].get(str(SUMO))=='3bd1eaa3b167fb527ac33b154dfb57b41b9a40d5bc3e26246489824dd7977179','native binary drift')
        cfg=ET.parse(root/c['package']/'scenario.sumocfg').getroot()
        for tag,expected_path in [('net-file',root/NETWORK),('route-files',root/c['package']/'demand.rou.xml'),('additional-files',root/c['package']/'scenario.add.xml')]:
            require(Path(cfg.find('./input/'+tag).get('value')).resolve()==expected_path.resolve(),'foreign runtime input root '+tag)
        for node in cfg.findall('./output/*')+cfg.findall('./report/*'):
            value=node.get('value','')
            if value.startswith('/'):require(Path(value).resolve().parent==(root/OUTPUT).resolve(),'foreign runtime output root')
        for node in ET.parse(root/c['package']/'scenario.add.xml').getroot().iter():
            for attr in ['file','dest']:
                if attr in node.attrib:require(Path(node.get(attr)).resolve().parent==(root/OUTPUT).resolve(),'foreign detector output root')
    return c


def validate_release(card_path,release_path,root=ROOT):
    root=Path(root).resolve();auth_path=root/TASK/'AUTHORIZATION_NATIVE_EXECUTION.json'
    require(auth_path.is_file(),'explicit SMOKE02 native execution authorization missing')
    auth=json.loads(auth_path.read_text())
    require(auth.get('SUMO_execution_authorized') is True and auth.get('run_id')==RUN and auth.get('card_sha256')==sha(card_path) and isinstance(auth.get('human_authorization_reference'),str) and auth['human_authorization_reference'],'no exact new human authorization')
    expected=root/TASK/'engineering/EXECUTION_RELEASE.json'
    require(Path(release_path).resolve()==expected and expected.is_file(),'new canonical release missing')
    release=json.loads(expected.read_text())
    require(release.get('run_id')==RUN and release.get('card_sha256')==sha(card_path) and release.get('authorization_sha256')==sha(auth_path) and release.get('automatic_continuation') is False,'new release identity drift')
    reviews=release.get('review_sha256');require(isinstance(reviews,dict) and set(reviews)=={'engineering','data','science'},'new three-role review required')
    for entry in reviews.values():require(isinstance(entry,dict) and sha(root/entry['path'])==entry['sha256'],'new review drift')
    return validate(card_path,root,require_environment=True)

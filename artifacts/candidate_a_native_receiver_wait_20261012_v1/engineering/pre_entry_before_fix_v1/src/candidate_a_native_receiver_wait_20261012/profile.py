"""Four one-use, reviewed-series technical cards. No native activity at import."""
from pathlib import Path
import json
import xml.etree.ElementTree as ET
from src.candidate_a_native_smoke_20261011 import bridge_card as base
from src.candidate_a_native_budget_cycles_20261012 import profile as previous
from src.candidate_a_native_receiver_wait_20261012.receiver_wait import POLICY
ROOT=base.ROOT
TASK=Path('artifacts/candidate_a_native_receiver_wait_20261012_v1')
NETWORK=base.NETWORK
SUMO=base.SUMO
BASE='20e5e83ac059768320cdaa4c815d164e1022de45'
BUDGETS=(300,)
RUNS={'CA_NATIVE_PHASE_R300_S17_WAIT_DIAG01':300,'CA_NATIVE_PHASE_R300_S17_WAIT_DIAG02':300}
sha=base.sha
write_new=base.write_new
require=base.require


def spec(run):
    require(run in RUNS,'unknown technical run identity')
    return {**base.SPEC,'run_id':run,'end_s':1272,'first_red_mandatory_pause':False,
        'first_red_mandatory_checkpoint_s':1207,'within_run_checkpoint_continuation':True,
        'complete_cycles_target':3,'automatic_retry':False,'sequential_postreview_gate':True,'receiver_diagnostic_policy':POLICY}


def resources(run):
    require(run in RUNS,'unknown technical run identity')
    return {'wall_limit_s':RUNS[run],'startup_limit_s':60,'run_limit_bytes':300_000_000,'minimum_free_bytes':5_000_000_000}


def output(run):return Path('data/raw/candidate_a_native_receiver_wait_20261012_v1')/run/'outputs'


def sources(root):
    files=previous.sources(root)
    for folder in ['src/candidate_a_native_receiver_wait_20261012','scripts/candidate_a_native_receiver_wait_20261012_v1']:
        for p in (root/folder).glob('*.py'):files[str(p.relative_to(root))]=sha(p)
    return dict(sorted(files.items()))


def stage_package(root,package,out):
    inherited=previous.stage_package(root,package,out)
    p=package/'scenario.sumocfg';tree=ET.parse(p);tree.getroot().find('./time/end').set('value','1272');ET.indent(tree);tree.write(p,encoding='utf-8',xml_declaration=True)
    return inherited


def prepare(run,root=ROOT):
    root=Path(root).resolve();specification=spec(run);package=root/TASK/'engineering/packages'/run;out=root/output(run)
    require(not out.parent.exists(),'one-use identity already consumed')
    card=package/'card.json'
    if card.is_file():validate(card,root);return card
    inherited=stage_package(root,package,out)
    old=json.loads((root/base.TASK/'engineering/packages'/base.RUN/'card.json').read_text())
    data={'classification':'BOUNDED_NATIVE_PHASE_THREE_CYCLE_TECHNICAL_SMOKE_NOT_FORMAL','status':'PREPARED_NOT_RELEASED',
        'baseline_commit':BASE,'spec':specification,'user_authorization':{'path':str(TASK/'USER_AUTHORIZATION_V1.json'),'sha256':sha(root/TASK/'USER_AUTHORIZATION_V1.json')},'package':str(package.relative_to(root)),'output':str(output(run)),
        'sources_sha256':sources(root),'inherited_inputs_sha256':inherited,'network_sha256':sha(root/NETWORK),
        'prepared_input_sha256':{str(p.relative_to(root)):sha(p) for p in package.iterdir() if p.is_file()},
        'environment':base.environment(),'resources':resources(run),'runtime_authorization_generated':False,
        'resources_provenance':{'technical_series_wall_s':list(BUDGETS),'other_caps_unchanged':True,'basis':'explicit direct independent-worktree minimal repair authorization; one diagnostic plus at most one evidenced reviewed repair; three-role gated release required'},
        'source_binary_compiler_equivalence':'NOT_VERIFIED','binary_reference_provenance':old['binary_reference_provenance'],
        'configuration_delta':{'controlled_G_y_r_s':[3,3,18],'controlled_red_next':0,'holding_red_s':600,
            'simulation_end_s':1272,'mandatory_first_red_checkpoint_s':1207,'native_cycle_starts_s':[1200,1224,1248],
            'native_fourth_green_executed':False,'old_SMOKE04_identity_unchanged':True},
        'interpretation':{'native_safety_proven':False,'rate_qualified':False,'long_term_service_qualified':False}}
    write_new(card,data);return card


def validate(card_path,root=ROOT,require_environment=False):
    root=Path(root).resolve();p=Path(card_path).resolve();c=json.loads(p.read_text());run=c.get('spec',{}).get('run_id')
    require(run in RUNS,'unknown technical card identity')
    expected=root/TASK/'engineering/packages'/run/'card.json'
    require(p==expected,'foreign technical card path')
    require(c.get('classification')=='BOUNDED_NATIVE_PHASE_THREE_CYCLE_TECHNICAL_SMOKE_NOT_FORMAL' and c.get('status')=='PREPARED_NOT_RELEASED' and c.get('spec')==spec(run),'technical card spec drift')
    require(c.get('baseline_commit')==BASE and c.get('package')==str(expected.parent.relative_to(root)) and c.get('output')==str(output(run)),'baseline/package/output drift')
    require(isinstance(c.get('resources'),dict) and c['resources']==resources(run) and all(type(v) is int for v in c['resources'].values()),'exact integer resources drift')
    require(c['user_authorization']=={'path':str(TASK/'USER_AUTHORIZATION_V1.json'),'sha256':sha(root/TASK/'USER_AUTHORIZATION_V1.json')}, 'direct user authorization drift')
    require(c['sources_sha256']==sources(root),'source drift')
    for key in ['prepared_input_sha256','inherited_inputs_sha256']:
        for n,h in c[key].items():require(sha(root/n)==h,'input drift '+n)
    require(c['network_sha256']==sha(root/NETWORK),'network drift')
    cfg=ET.parse(expected.parent/'scenario.sumocfg').getroot()
    require(cfg.find('./time/end').get('value')=='1272' and cfg.find('./time/step-length').get('value')=='1','horizon/step drift')
    phases=ET.parse(expected.parent/'scenario.add.xml').getroot().find("tlLogic[@programID='CA_C24']")
    require([(q.get('state'),q.get('duration'),q.get('next')) for q in phases]==[('G','3','1'),('y','3','2'),('r','18','0')],'native continuous cycle drift')
    protected=json.loads((root/'artifacts/candidate_a_a1_contract_20261011_v1/engineering/PROTECTED_BASELINE_SHA256.json').read_text())['files']
    require(len(protected)==536 and all(sha(root/n)==h for n,h in protected.items()),'protected source drift')
    require(not (root/output(run)).parent.exists(),'one-use identity already consumed')
    if require_environment:
        require(c['environment']['complete'] and c['environment']==base.environment(),'environment drift')
        require(c['environment']['files_sha256'].get(str(SUMO))=='3bd1eaa3b167fb527ac33b154dfb57b41b9a40d5bc3e26246489824dd7977179','binary drift')
        for tag,path in [('net-file',root/NETWORK),('route-files',expected.parent/'demand.rou.xml'),('additional-files',expected.parent/'scenario.add.xml')]:
            require(Path(cfg.find('./input/'+tag).get('value')).resolve()==path.resolve(),'foreign runtime input '+tag)
        for node in cfg.findall('./output/*')+cfg.findall('./report/*'):
            value=node.get('value','')
            if value.startswith('/'):require(Path(value).resolve().parent==(root/output(run)).resolve(),'foreign runtime output')
        for node in ET.parse(expected.parent/'scenario.add.xml').getroot().iter():
            for attr in ['file','dest']:
                if attr in node.attrib:require(Path(node.get(attr)).resolve().parent==(root/output(run)).resolve(),'foreign detector output')
    return c


def validate_release(card_path,release_path,root=ROOT):
    root=Path(root).resolve();card=validate(card_path,root);run=card['spec']['run_id']
    auth_path=root/TASK/'authorization'/run/'AUTHORIZATION_NATIVE_EXECUTION.json'
    require(auth_path.is_file(),'exact technical series authorization missing')
    auth=json.loads(auth_path.read_text());expected=root/TASK/'engineering/releases'/run/'EXECUTION_RELEASE.json'
    require(auth.get('SUMO_execution_authorized') is True and auth.get('run_id')==run and auth.get('card_sha256')==sha(card_path) and isinstance(auth.get('human_authorization_reference'),str) and auth['human_authorization_reference'],'human authorization binding drift')
    require(Path(release_path).resolve()==expected and expected.is_file(),'canonical per-run release missing')
    release=json.loads(expected.read_text())
    require(release.get('run_id')==run and release.get('card_sha256')==sha(card_path) and release.get('authorization_sha256')==sha(auth_path) and release.get('automatic_continuation') is False,'release binding drift')
    reviews=release.get('review_sha256');require(isinstance(reviews,dict) and set(reviews)=={'engineering','data','science'},'three-role release required')
    for r in reviews.values():require(isinstance(r,dict) and sha(root/r['path'])==r['sha256'],'review drift')
    return validate(card_path,root,require_environment=True)

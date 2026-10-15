"""One fresh fixed900 packet card. Historical cards remain immutable."""
from pathlib import Path
import json
import xml.etree.ElementTree as ET
from src.candidate_a_issue12_signal_policy_20261012 import profile as old
from src.candidate_a_issue12_packet_policy_20261012 import budget
ROOT=old.ROOT;NETWORK=old.NETWORK;SUMO=old.SUMO;BASE=old.BASE
TASK=Path('artifacts/issue12_alinea_actuation_20261012_v1/engineering/packet_v1')
ISSUE=old.ISSUE
USER=Path('artifacts/issue12_alinea_actuation_20261012_v1/USER_RESOURCE_AUTHORIZATION_20261012.json')
DESIGN=old.TASK/'engineering/stop_gap_investigation_v1/SCIENTIFIC_PHASE_ONLY_DESIGN_REVIEW_V1.md'
RUN='CA_I12_PACKET_R900_S17_DIAG01'
sha=old.sha;write_new=old.write_new;require=old.require


def output(run):
    require(run==RUN,'unknown packet run');return budget.RAW/run/'outputs'


def spec(run):
    require(run==RUN,'unknown packet run')
    return {**old.spec('CA_I12_QUOTA_R900_S17_BOUNDARY01'),'run_id':run,'phase_durations_s':[4,2,2],
        'period_s':8,'complete_cycles_target':9,'discrete_rates_veh_h':[7200/t for t in range(24,7,-1)],
        'quotas':[2],'input_origin':'FIXED_PACKET_POLICY_DIAGNOSTIC','all_spanning_bodies':'ENTRY_ID_TIME_SIGNAL_TO_REAL_REAR_CLEAR_EACH_ACK_NO_YELLOW_DEADLINE',
        'total_resource_envelope':{'monitored_s':900,'raw_bytes':900000000},'fixed_start_count_limit':None}


def resources(run):require(run==RUN,'unknown packet run');return old.resources('CA_I12_QUOTA_R900_S17_BOUNDARY01')


def sources(root):
    files=old.sources(root)
    for folder in ['src/candidate_a_issue12_packet_policy_20261012','scripts/candidate_a_issue12_packet_policy_20261012_v1']:
        for p in (root/folder).glob('*.py'):files[str(p.relative_to(root))]=sha(p)
    for p in [USER,DESIGN,budget.HISTORY,TASK/'USER_STEERING_V1.json']:files[str(p)]=sha(root/p)
    return dict(sorted(files.items()))


def stage_package(root,package,out):
    inherited=old.stage_package(root,package,out)
    p=package/'scenario.add.xml';tree=ET.parse(p);logic=tree.getroot().find("tlLogic[@programID='I12_QUOTA24']")
    require(logic is not None,'packet parent XML missing')
    logic.set('programID','I12_PACKET8')
    for node,duration in zip(logic,('4','2','2')):node.set('duration',duration)
    ET.indent(tree);tree.write(p,encoding='utf-8',xml_declaration=True)
    return inherited


def prepare(run=RUN,root=ROOT):
    root=Path(root).resolve();package=root/TASK/'packages'/run;out=root/output(run)
    require(not out.parent.exists(),'packet identity already consumed')
    card=package/'card.json'
    if card.exists():validate(card,root);return card
    inherited=stage_package(root,package,out);prior=json.loads((root/old.TASK/'engineering/packages/CA_I12_QUOTA_R900_S17_BOUNDARY01/card.json').read_text())
    data={'classification':'BOUNDED_NATIVE_PACKET_TECHNICAL_DIAGNOSTIC_NOT_FORMAL','status':'PREPARED_NOT_RELEASED','baseline_commit':BASE,
        'spec':spec(run),'package':str(package.relative_to(root)),'output':str(output(run)),
        'user_authorization':{'path':str(USER),'sha256':sha(root/USER)},'sources_sha256':sources(root),
        'inherited_inputs_sha256':inherited,'network_sha256':sha(root/NETWORK),
        'prepared_input_sha256':{str(p.relative_to(root)):sha(p) for p in package.iterdir() if p.is_file()},
        'resources':resources(run),'total_budget_preparation_snapshot':budget.accounting(root),'environment':old.base.environment(),
        'runtime_authorization_generated':False,'source_binary_compiler_equivalence':'NOT_VERIFIED','binary_reference_provenance':prior['binary_reference_provenance'],
        'interpretation':{'native_safety_proven':False,'rate_qualified':False,'total_budget_numerical_provenance':'engineering-selected original3xceilings; latest human removed fixed-count stop, not literal numerical approval'},
        'necessity':'Test one short two-car packet at900 while preserving hard emergency9+1.1/normalbraking/unknown checks; observe actualY2/bodyclear/newcycleadmission/9cycles, not repeat longG or tune guard'}
    write_new(card,data);return card


def validate(card_path,root=ROOT,require_environment=False):
    root=Path(root).resolve();card_path=Path(card_path).resolve();c=json.loads(card_path.read_text());expected=root/TASK/'packages'/RUN/'card.json'
    require(card_path==expected and c['spec']==spec(RUN),'packet identity/spec drift')
    require(c['classification']=='BOUNDED_NATIVE_PACKET_TECHNICAL_DIAGNOSTIC_NOT_FORMAL' and c['status']=='PREPARED_NOT_RELEASED' and c['baseline_commit']==BASE,'packet stage drift')
    require(c['package']==str(expected.parent.relative_to(root)) and c['output']==str(output(RUN)),'packet paths drift')
    require(c['resources']==resources(RUN) and c['sources_sha256']==sources(root),'packet source/resource drift')
    require(c['user_authorization']=={'path':str(USER),'sha256':sha(root/USER)},'latest human steering binding drift')
    for key in ['inherited_inputs_sha256','prepared_input_sha256']:
        for n,h in c[key].items():require(sha(root/n)==h,'packet input drift '+n)
    require(sha(root/NETWORK)==c['network_sha256'],'packet network drift')
    cfg=ET.parse(expected.parent/'scenario.sumocfg').getroot();require(cfg.find('./time/end').get('value')=='1272' and cfg.find('./time/step-length').get('value')=='1','packet horizon drift')
    require(len(cfg.findall('./output/precision'))==1 and cfg.find('./output/precision').get('value')=='8','packet precision drift')
    logic=ET.parse(expected.parent/'scenario.add.xml').getroot().find("tlLogic[@programID='I12_PACKET8']")
    require(logic is not None and [(x.get('state'),x.get('duration'),x.get('next')) for x in logic]==[('G','4','1'),('y','2','2'),('r','2','0')],'packet phase drift')
    protected=json.loads((root/'artifacts/candidate_a_a1_contract_20261011_v1/engineering/PROTECTED_BASELINE_SHA256.json').read_text())['files']
    require(len(protected)==536 and all(sha(root/n)==h for n,h in protected.items()),'packet protected source drift')
    require(not (root/output(RUN)).parent.exists(),'packet identity already consumed')
    if require_environment:
        require(c['environment']['complete'] and c['environment']==old.base.environment(),'packet environment drift')
        for tag,path in [('net-file',root/NETWORK),('route-files',expected.parent/'demand.rou.xml'),('additional-files',expected.parent/'scenario.add.xml')]:require(Path(cfg.find('./input/'+tag).get('value')).resolve()==path.resolve(),'foreign packet input')
        for node in cfg.findall('./output/*')+cfg.findall('./report/*'):
            value=node.get('value','')
            if value.startswith('/'):require(Path(value).resolve().parent==(root/output(RUN)).resolve(),'foreign packet output')
        for node in ET.parse(expected.parent/'scenario.add.xml').getroot().iter():
            for attr in ['file','dest']:
                if attr in node.attrib:require(Path(node.get(attr)).resolve().parent==(root/output(RUN)).resolve(),'foreign packet detector')
    return c


def validate_release(card_path,release_path,root=ROOT):
    root=Path(root).resolve();c=validate(card_path,root,require_environment=True)
    ap=root/TASK/'authorization'/RUN/'AUTHORIZATION_NATIVE_EXECUTION.json';rp=root/TASK/'releases'/RUN/'EXECUTION_RELEASE.json'
    require(ap.is_file() and Path(release_path).resolve()==rp and rp.is_file(),'packet canonical permission missing')
    a=json.loads(ap.read_text());v=json.loads(rp.read_text())
    require(a.get('SUMO_execution_authorized') is True and a.get('run_id')==RUN and a.get('card_sha256')==sha(card_path),'packet human authorization drift')
    require(a.get('human_authorization_reference')==str(USER) and a.get('human_authorization_sha256')==sha(root/USER),'packet latest human authority drift')
    require(v.get('run_id')==RUN and v.get('card_sha256')==sha(card_path) and v.get('authorization_sha256')==sha(ap) and v.get('automatic_continuation') is False,'packet canonical release drift')
    reviews=v.get('review_sha256');require(isinstance(reviews,dict) and set(reviews)=={'engineering','data','science'},'packet three-role release missing')
    for x in reviews.values():require(sha(root/x['path'])==x['sha256'],'packet review drift')
    budget.accounting(root)  # No count cutoff; unknown parents remain fully charged.
    return c

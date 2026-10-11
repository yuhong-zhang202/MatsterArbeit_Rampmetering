"""Public offline source/XML/card audit; optional raw hashes explicitly local-only."""
from pathlib import Path
import argparse, collections, hashlib, json, re, sys
import xml.etree.ElementTree as ET
from unittest.mock import patch
ROOT=Path(__file__).resolve().parents[3];sys.path.insert(0,str(ROOT))
TASK=Path('artifacts/candidate_a_native_smoke_selfloop_fix_20261011_v1');ENG=ROOT/TASK/'engineering'
RUN='CA_NATIVE_PHASE_R300_S17_SMOKE02';PKG=ENG/'packages'/RUN
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def load(p):return json.loads(p.read_text())
def verify(files):
    for p,h in files.items():assert sha(ROOT/p)==h,p
    return len(files)
def predicates(path):
    found=[]
    for logic in ET.parse(path).getroot().findall('tlLogic'):
        phases=logic.findall('phase')
        for i,p in enumerate(phases):
            nexts=[int(x) for x in p.get('next',str((i+1)%len(phases))).split()]
            if len(phases)>1 and nexts==[i]:found.append((logic.get('id'),logic.get('programID'),i))
    return found

def main(local=False):
    binding_count=verify(load(ENG/'INPUT_BINDINGS_V1.json')['files']);assert binding_count==29
    source=load(ENG/'OFFICIAL_SOURCE_RECEIPT_R1.json');assert source['commit']=='fa7df22d7f1c4ae245192ecc32410a49f1ffb2a3'
    for x in source['excerpts']:
        assert hashlib.sha256(x['text'].encode()).hexdigest()==x['sha256']
        assert len(x['text'].splitlines())==x['line_end']-x['line_start']+1
        assert source['commit'] in x['url']
    oldpkg=ROOT/'artifacts/candidate_a_native_smoke_bridge_20261011_v1/engineering/packages/CA_NATIVE_PHASE_R300_S17_SMOKE01'
    old=predicates(oldpkg/'scenario.add.xml');new=predicates(PKG/'scenario.add.xml')
    warning=ROOT/'artifacts/candidate_a_native_smoke_execution_20261011_v1/engineering/RUNTIME_NATIVE_WARNING_EXTRACT.txt'
    mapped=[]
    for line in warning.read_text().splitlines():
        m=re.fullmatch(r"Warning: Phase (\d+) only loops backs to itself in tlLogic '([^']+)', program '([^']+)'.",line)
        assert m; mapped.append((m[2],m[3],int(m[1])))
    assert len(old)==17 and set(old)==set(mapped) and not new
    expected_old=ROOT/'src/candidate_a_native_smoke_20261011/bridge.py';current=ROOT/'src/candidate_a_native_smoke_selfloop_fix_20261011/bridge.py'
    expected=expected_old.read_text().replace('from src.candidate_a_native_smoke_20261011.bridge_card import','from src.candidate_a_native_smoke_selfloop_fix_20261011.profile import')
    assert current.read_text()==expected,'unexpected bridge changes beyond import'
    protected=load(ROOT/'artifacts/candidate_a_a1_contract_20261011_v1/engineering/PROTECTED_BASELINE_SHA256.json')['files'];assert verify(protected)==536
    r2=verify(load(ROOT/'artifacts/candidate_a_native_smoke_proposal_20261011_v1/engineering/INPUT_BINDINGS_R2.json')['files'])
    v5=verify(load(ROOT/'artifacts/candidate_a_native_smoke_bridge_20261011_v1/engineering/INPUT_BINDINGS_V5.json')['files'])
    assert r2==7 and v5==26
    assert sha(oldpkg/'card.json')=='7f74fa8cecb94a81e0d86a2ac2422fd10fa0ffcb3d7cf39a16bfa7d7f53b89d0'
    assert (PKG/'demand.rou.xml').read_bytes()==(oldpkg/'demand.rou.xml').read_bytes()
    demand=ET.parse(PKG/'demand.rou.xml').getroot();groups=collections.defaultdict(list)
    ids=[]
    for v in demand.findall('vehicle'):
        ids.append(v.get('id'));groups[v.get('id').split('_')[0]].append(float(v.get('depart')))
    assert len(ids)==len(set(ids))==4050 and not demand.findall('flow')
    rates={};counts={}
    for group,(vehicle_count,gap) in {'M':(3000,1),'R':(600,4),'U':(300,10),'X':(150,20)}.items():
        t=sorted(groups[group]);assert len(t)==vehicle_count and all(b-a==gap for a,b in zip(t,t[1:]));counts[group]=vehicle_count;rates[group]=3600/gap
    cfg=ET.parse(PKG/'scenario.sumocfg').getroot();assert cfg.find('./time/end').get('value')=='1207' and cfg.find('./time/step-length').get('value')=='1' and cfg.find('./random_number/seed').get('value')=='17'
    assert cfg.find('./report/no-warnings').get('value')=='false' and cfg.find('./report/aggregate-warnings').get('value')=='-1'
    logics=ET.parse(PKG/'scenario.add.xml').getroot().findall('tlLogic');assert [x.get('programID') for x in logics]==['CA_C8','CA_C24']
    h,c=logics
    assert [(p.get('state'),float(p.get('duration')),p.get('next')) for p in h]==[('G',3,'1'),('y',3,'2'),('r',600,'0')]
    assert [(p.get('state'),float(p.get('duration')),p.get('next')) for p in c]==[('G',3,'1'),('y',3,'2'),('r',18,'0')]
    holding_red=600+float(h[1].get('duration'));holding_next=holding_red+float(h[2].get('duration'));controlled_red=1200+sum(float(p.get('duration')) for p in c[:2]);next_green=controlled_red+float(c[2].get('duration'))
    assert (holding_red,holding_next,controlled_red,next_green)==(603,1203,1206,1224)
    from src.candidate_a_native_smoke_selfloop_fix_20261011.profile import validate,OUTPUT
    from src.candidate_a_native_smoke_selfloop_fix_20261011.bridge import execute
    card=validate(PKG/'card.json')
    assert sha(PKG/'card.json')=='a501e6005589de0d3ce6acd0fe7924ec84b589bec0849c4f3fcd3f51a4d552f3'
    assert not (ROOT/TASK/'AUTHORIZATION_NATIVE_EXECUTION.json').exists() and not (ENG/'EXECUTION_RELEASE.json').exists()
    with patch('subprocess.Popen',side_effect=AssertionError('no native spawn')) as popen:
        try:execute(PKG/'card.json',ENG/'EXECUTION_RELEASE.json')
        except ValueError as error:assert 'SMOKE02 native execution authorization missing' in str(error)
        else:raise AssertionError('missing authorization accepted')
        assert popen.call_count==0
    assert not (ROOT/OUTPUT).parent.exists()
    result={'status':'PASS_OFFLINE_BOUNDED_SELFLOOP_CORRECTION_NOT_NATIVE_VALIDATION','engineering_files':binding_count,'source_excerpt_count':len(source['excerpts']),'source_verification':'Bound published excerpt bytes/line counts/commit URLs; no new fetch/fullsource verification by this checker','old_warning_mapping':[list(x) for x in old],'old_warning_count':17,'new_program_selfloop_predicate_count':0,'protected_files':536,'R2_files':r2,'V5_files':v5,'nominal_active_rates_veh_h':rates,'planned_counts':counts,'planned_timeline':{'holding_yellow':600,'holding_red':holding_red,'holding_native_next_green_if_not_replaced':holding_next,'controlled_replacement':1200,'controlled_red':controlled_red,'mandatory_pause':1207,'controlled_native_next_green_not_reached':next_green},'dynamics_equivalence':'NOT_PROVED','native_validation':'NOT_RUN','Popen_calls':0,'new_raw_allocation':False,'raw_verification':'SKIP_PUBLIC_CHECK_NO_RAW_REQUIRED'}
    assert result['engineering_files']==29 and result['source_excerpt_count']==5
    if local:
        raw=load(ROOT/'artifacts/candidate_a_native_smoke_execution_20261011_v1/engineering/RAW_FINAL_SHA256.json')['files']
        result['local_raw_files']=verify(raw);result['raw_verification']='PASS_LOCAL_ONLY_53_HASHES'
    return result
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--local-raw',action='store_true');args=p.parse_args();print(json.dumps(main(args.local_raw),indent=2))

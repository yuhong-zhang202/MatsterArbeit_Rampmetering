"""Offline public binding/accounting and bounded cache probes; never native startup."""
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch
import argparse,collections,hashlib,json,sys
ROOT=Path(__file__).resolve().parents[3];sys.path.insert(0,str(ROOT))
ENG=ROOT/'artifacts/candidate_a_native_smoke_runtime_fix_20261012_v1/engineering'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def load(p):return json.loads(p.read_text())
def verify(files):
    for n,h in files.items():assert sha(ROOT/n)==h,n
    return len(files)
def main(local=False):
    from src.candidate_a_native_smoke_runtime_fix_20261012.frame_cache import FrameCache,CACHE_VEHICLE
    from src.candidate_a_native_smoke_runtime_fix_20261012.profile import validate,TASK,RUN,OUTPUT
    from src.candidate_a_native_smoke_runtime_fix_20261012.bridge import execute
    binding_count=verify(load(ENG/'INPUT_BINDINGS_V2.json')['files']);assert binding_count==36
    source=load(ENG/'GETTER_SOURCE_RECEIPT_R1.json');assert source['pin']=='fa7df22d7f1c4ae245192ecc32410a49f1ffb2a3'
    assert set(x['name'] for x in source['getters'])==CACHE_VEHICLE
    for item in source['getters']:
        assert hashlib.sha256(item['excerpt'].encode()).hexdigest()==item['sha256']
        assert len(item['excerpt'].splitlines())==item['line_end']-item['line_start']+1
    bench=load(ENG/'FAKE_QUERY_BENCH_V2.json');actual=bench['actual']
    old_queries=sum(actual['0']['calls'].values());new_queries=sum(actual['1']['calls'].values());avoided=old_queries-new_queries;percent=100*avoided/old_queries
    assert (old_queries,new_queries,avoided)==(149790,52016,97774)
    assert percent==bench['percent_reduction'] and actual['0']['last']==actual['1']['last']==1207
    assert actual['0']['calls']['getIDList']==actual['1']['calls']['getIDList'] and actual['0']['calls']['getLoadedIDList']==actual['1']['calls']['getLoadedIDList']
    card=ENG/'packages'/RUN/'card.json';c=validate(card);assert sha(card)=='892b415603df776bb70698ad66939bbad28993e87a1bc225d5553ba58ac6bba4'
    assert c['resources']=={'wall_limit_s':180,'startup_limit_s':60,'run_limit_bytes':300000000,'minimum_free_bytes':5000000000}
    assert not (ROOT/TASK/'AUTHORIZATION_NATIVE_EXECUTION.json').exists() and not (ENG/'EXECUTION_RELEASE.json').exists()
    with patch('subprocess.Popen',side_effect=AssertionError('must not launch')) as popen:
        try:execute(card,ENG/'EXECUTION_RELEASE.json')
        except ValueError as exc:assert 'SMOKE03 native execution authorization missing' in str(exc)
        else:raise AssertionError('missing approval accepted')
        assert popen.call_count==0
    assert not (ROOT/OUTPUT).parent.exists()
    # Independent composition probe: cache repeated read, clear on unknown mutator,
    # changing clock, then native getter error; retain typed and mutable separation.
    state={'time':0,'speed':10,'fail':False};calls=collections.Counter()
    def speed(vid):
        calls['speed']+=1
        if state['fail']:raise RuntimeError('independent_getter_error')
        return state['speed']
    raw=SimpleNamespace(simulation=SimpleNamespace(getTime=lambda:state['time']),vehicle=SimpleNamespace(getSpeed=speed,unknown_mutator=lambda:state.update(speed=20),getRoute=lambda v:[type(v).__name__],getIDList=lambda:('A',)))
    cache=FrameCache(raw);assert cache.vehicle.getSpeed('A')==cache.vehicle.getSpeed('A')==10 and calls['speed']==1
    cache.vehicle.unknown_mutator();assert cache.vehicle.getSpeed('A')==20 and calls['speed']==2
    state.update(time=1,speed=30);assert cache.simulation.getTime()==1 and cache.vehicle.getSpeed('A')==30 and calls['speed']==3
    r=cache.vehicle.getRoute(True);r.append('mutated');assert cache.vehicle.getRoute(True)==['bool'] and cache.vehicle.getRoute(1)==['int'] and cache.vehicle.getRoute(1.0)==['float']
    cache.invalidate('probe');state['fail']=True
    for _ in range(2):
        try:cache.vehicle.getSpeed('A')
        except RuntimeError as exc:assert str(exc)=='independent_getter_error'
        else:raise AssertionError('failed getter became cachedvalue')
        assert not cache.values
    checks={'protected_files':verify(load(ROOT/'artifacts/candidate_a_a1_contract_20261011_v1/engineering/PROTECTED_BASELINE_SHA256.json')['files']),'R2_files':verify(load(ROOT/'artifacts/candidate_a_native_smoke_proposal_20261011_v1/engineering/INPUT_BINDINGS_R2.json')['files']),'V5_files':verify(load(ROOT/'artifacts/candidate_a_native_smoke_bridge_20261011_v1/engineering/INPUT_BINDINGS_V5.json')['files'])}
    result={'status':'PASS_BOUNDED_OFFLINE_CACHE_DATA_REVIEW_NOT_NATIVE_SPEEDUP','engineering_binding_count':binding_count,'source_getter_count':len(source['getters']),'checks':checks,'fake_query_arithmetic':{'old_vehicle_queries':old_queries,'new_vehicle_queries':new_queries,'avoided':avoided,'percent':percent},'independent_cache_composition_probe':'PASS_REUSE_MUTATOR_CLOCK_TYPED_MUTABLE_ERROR','new_authorization_absent':True,'native_calls':0,'new_raw_absent':True,'raw_verification':'SKIP_PUBLIC_NO_RAW_REQUIRED','native_runtime_performance':'NOT_RUN','conditional_scope':'Single owned synchronousconnection; no externalmutations/concurrency; immutablewithinframe directread semantics; repeatedRPCfailuretiming not equivalent'}
    if local:
        rawdir=ROOT/'data/raw/candidate_a_native_smoke_selfloop_fix_20261011_v1/CA_NATIVE_PHASE_R300_S17_SMOKE02/outputs'
        pre=[json.loads(x) for x in (rawdir/'pre_steps.jsonl').read_text().splitlines()]
        world_visits=sum(len(x['bound_snapshot']['world']) for x in pre);loaded_visits=sum(len(x['bound_snapshot']['loaded']) for x in pre)
        overlap=sum(len(set(x['bound_snapshot']['world'])&set(x['bound_snapshot']['loaded'])) for x in pre)
        assert (world_visits,loaded_visits,overlap)==(56859,145833,56859)
        result['local_opportunities']={'pre_world':world_visits,'pre_loaded':loaded_visits,'overlap':overlap,'eleven_identity_query_opportunities':11*overlap,'scope':'Pre-only potentialduplicates, not profiler/native actualexecution/time'}
        result['raw_verification']='PASS_LOCAL_READONLY';result['checks']['raw58_hashes']=verify(load(ROOT/'artifacts/candidate_a_native_smoke02_execution_20261012_v1/engineering/RAW_FINAL_SHA256.json')['files'])
    assert result['engineering_binding_count']==36 and result['source_getter_count']==17
    return result
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--local-raw',action='store_true');a=p.parse_args();print(json.dumps(main(a.local_raw),indent=2))

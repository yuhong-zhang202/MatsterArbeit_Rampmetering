"""Read-only consumed SMOKE03 audit. Default uses public evidence, never runtime paths."""
import argparse,collections,gzip,hashlib,json
from pathlib import Path
import xml.etree.ElementTree as ET
ROOT=Path(__file__).resolve().parents[3]
ENG=ROOT/'artifacts/candidate_a_native_smoke03_execution_20261012_v1/engineering'
RAW=ROOT/'data/raw/candidate_a_native_smoke_runtime_fix_20261012_v1/CA_NATIVE_PHASE_R300_S17_SMOKE03'
def sha(b):return hashlib.sha256(b).hexdigest()
def load(p):return json.loads(p.read_text())
def rows(p):return [json.loads(x) for x in p.read_text().splitlines()]
def verify(mapping):
    for name,expected in mapping.items():assert sha((ROOT/name).read_bytes())==expected,name
    return len(mapping)
def review(local=False):
    result={'scope':'OBSERVED_TRUNCATED_PREFIX_NOT_QUALIFICATION','native_calls_by_audit':0,'checks':{}}
    checks=result['checks'];checks['engineering_bound_files']=verify(load(ENG/'ENGINEERING_DELIVERY_BINDING.json')['files'])
    auth=load(ENG/'consumed_authorization_snapshots/SMOKE03_AUTHORIZATION_EVIDENCE.json');release=load(ENG/'consumed_authorization_snapshots/SMOKE03_RELEASE_EVIDENCE.json')
    assert auth['run_id']==release['run_id']=='CA_NATIVE_PHASE_R300_S17_SMOKE03'
    assert auth['card_sha256']==release['card_sha256']=='892b415603df776bb70698ad66939bbad28993e87a1bc225d5553ba58ac6bba4'
    assert release['authorization_sha256']==sha((ENG/'consumed_authorization_snapshots/SMOKE03_AUTHORIZATION_EVIDENCE.json').read_bytes())
    assert sha((ROOT/auth['human_authorization_reference']).read_bytes())==auth['human_authorization_sha256']
    for item in release['review_sha256'].values():assert sha((ROOT/item['path']).read_bytes())==item['sha256']
    checks['protected_files']=verify(load(ROOT/'artifacts/candidate_a_a1_contract_20261011_v1/engineering/PROTECTED_BASELINE_SHA256.json')['files'])
    checks['R2_files']=verify(load(ROOT/'artifacts/candidate_a_native_smoke_proposal_20261011_v1/engineering/INPUT_BINDINGS_R2.json')['files'])
    checks['V5_files']=verify(load(ROOT/'artifacts/candidate_a_native_smoke_bridge_20261011_v1/engineering/INPUT_BINDINGS_V5.json')['files'])
    card=ROOT/'artifacts/candidate_a_native_smoke_runtime_fix_20261012_v1/engineering/packages/CA_NATIVE_PHASE_R300_S17_SMOKE03/card.json'
    assert sha(card.read_bytes())==auth['card_sha256'];carddata=load(card)
    checks['card_sources']=verify(carddata['sources_sha256']);checks['card_inputs']=verify(carddata['prepared_input_sha256']);checks['repair_bound_files']=verify(load(ROOT/'artifacts/candidate_a_native_smoke_runtime_fix_20261012_v1/engineering/INPUT_BINDINGS_V2.json')['files'])
    execution=load(ENG/'EXECUTION_RECEIPT.json');assert execution['HEAD']=='c2552635a7cd36e25a0eeb2c04819c04aab18130' and execution['native_starts']==1
    assert all(x is None for x in execution['controlled_service'].values())
    result.update(status='PASS_PUBLIC_HASH_AND_CONSUMED_AUTHORITY_AUDIT_ONLY',raw_status='SKIP_PUBLIC_NO_RAW_DEPENDENCY')
    if not local:return result
    manifest=load(ENG/'RAW_FINAL_SHA256.json');checks['raw_files']=verify(manifest['files'])
    files={str(p.relative_to(ROOT)) for p in RAW.rglob('*') if p.is_file()};assert files==set(manifest['files']) and len(files)==62
    checks['previous_SMOKE02_raw_files']=verify(load(ROOT/'artifacts/candidate_a_native_smoke02_execution_20261012_v1/engineering/RAW_FINAL_SHA256.json')['files'])
    checks['raw_bytes']=sum((ROOT/n).stat().st_size for n in files);assert checks['raw_bytes']==34183941
    out=RAW/'outputs';bridge=load(out/'bridge_receipt.json');failure=load(out/'failure_snapshot.json')
    assert bridge['last_completed_s']==bridge['last_accounted_s']==failure['last_completed_s']==failure['last_accounted_s']==1157
    assert bridge['error']=='ValueError:wall resource STOP' and bridge['status']=='ABORTED_UNKNOWN'
    assert bridge['final_logs']['status']=='BOUND_NO_OBSERVED_NATIVE_MESSAGE' and bridge['final_logs']['process_returncode']==0
    for p in (out/'snapshots').rglob('*'):
        if p.is_file():
            original=ROOT/p.relative_to(out/'snapshots');assert p.read_bytes()==original.read_bytes(),str(p)
    assert (out/'card.json').read_bytes()==card.read_bytes()
    assert (out/'release.json').read_bytes()==(ENG/'consumed_authorization_snapshots/SMOKE03_RELEASE_EVIDENCE.json').read_bytes()
    ack=rows(out/'step_ack.jsonl');pre=rows(out/'pre_steps.jsonl');post=rows(out/'post_steps.jsonl')
    assert len(ack)==3914 and len(pre)==len(post)==1157
    for index,(p,q) in enumerate(zip(pre,post)):
        target=index+1;first,verified=ack[2*index:2*index+2]
        assert first['requested_target_s']==verified['requested_target_s']==target and first['ACK_received'] is True and verified['ACK_received'] is True
        assert first['actual_time_verified'] is False and first['actual_readback_s'] is None
        assert verified['actual_time_verified'] is True and verified['actual_readback_s']==target
        assert p['time_s']==index and q['time_begin_s']==index and q['time_end_s']==q['observed_time_s']==target and q['accounting_complete'] is True
        assert q['status']=='RECONCILED_DIAGNOSTIC_ONLY'
        expected='G' if index<600 else 'y' if index<603 else 'r'
        assert p['bound_snapshot']['motion']==q['motion']==expected
    phases=collections.Counter(q['motion'] for q in post);assert phases=={'G':600,'y':3,'r':554}
    logrows=rows(out/'log_intervals.jsonl');assert len(logrows)==3916
    assert logrows[0]['stage']=='STARTUP_CONNECT_ACK' and logrows[-1]['stage']=='AFTER_NATIVE_CLOSE_PROCESS_EOF'
    cursor={n:0 for n in logrows[0]['streams']};identity={}
    for row in logrows:
        for name,s in row['streams'].items():
            data=(out/name).read_bytes();a,b=s['byte_start'],s['byte_end']
            assert a==cursor[name] and 0<=a<=b<=len(data)
            assert sha(data[:b])==s['prefix_sha256'] and sha(data[a:b])==s['fragment_sha256'] and data[a:b].hex()==s['raw_fragment_hex']
            ident=(s['device'],s['inode']);assert name not in identity or identity[name]==ident
            identity[name]=ident;cursor[name]=b
    assert all(cursor[n]==(out/n).stat().st_size for n in cursor)
    assert (out/'sumo_stderr.log').stat().st_size==(out/'sumo_error.log').stat().st_size==0
    log=(out/'sumo.log').read_text();assert 'loops backs to itself' not in log and 'ended at time: 1157.00.' in log
    xml=[];summary=[]
    for p in sorted(out.glob('*.xml*')):
        data=gzip.decompress(p.read_bytes()) if p.suffix=='.gz' else p.read_bytes()
        try:tree=ET.fromstring(data)
        except ET.ParseError as exc:xml.append({'name':p.name,'status':'INVALID_XML','error':str(exc)});continue
        entry={'name':p.name,'status':'WELL_FORMED_TRUNCATED_PREFIX','root':tree.tag,'child_count':len(tree)}
        if p.name in ('fcd.xml.gz','sumo_summary.xml'):
            times=[float(x.get('time')) for x in tree];assert times==list(range(1157));entry['first_time_s']=0;entry['last_time_s']=686
        if p.name=='sumo_summary.xml':
            summary=list(tree);entry['observed_collision_counter_max']=max(int(x.get('collisions')) for x in tree);entry['observed_teleport_counter_max']=max(int(x.get('teleports')) for x in tree);entry['last_summary']=dict(tree[-1].attrib)
        if tree.tag=='detector':
            assert len(tree)==39;assert [(float(x.get('begin')),float(x.get('end'))) for x in tree]==[(i*30,(i+1)*30) for i in range(38)]+[(1140,1157)]
            entry['last_interval']={'begin_s':1140,'end_s':1157,'duration_s':17,'partial_nominal30s':True}
        if p.name=='tls_states.xml':
            ramp=[x for x in tree if x.get('id')=='ramp_mid'];assert [float(x.get('time')) for x in ramp]==list(range(1157))
            assert collections.Counter(x.get('state') for x in ramp)==phases;entry['ramp_records']=len(ramp)
        if p.name=='tripinfo.xml':
            counts=collections.Counter('UNDEPARTED_END' if float(x.get('depart'))<0 else 'ARRIVED' if float(x.get('arrival'))>=0 else 'IN_NETWORK_CENSORED_END' for x in tree)
            entry['record_classification']=dict(counts);assert counts=={'ARRIVED':1208,'IN_NETWORK_CENSORED_END':207,'UNDEPARTED_END':57}
        xml.append(entry)
    trace=rows(out/'startup_trace.jsonl');assert len(trace)==239 and sum(x['outcome']=='CONNECTED' for x in trace)==1
    monitor={'actual_crossing_records_in_1157_post_rows':sum(len(x['actual_crossings']) for x in post),'post_receiver_available_false_count':sum(x['post_receiver'].get('available') is False for x in post),'scope':'Recorded checks in reconciled0..1157 prefix only; not completeprospective safety proof or activatedmetering qualification','collision_teleport_measurement':'Native summary actualprefix counters, unlike unobservedcontrolledphase outcomes'}
    cache=bridge['same_state_query_cache'];assert cache==failure['same_state_query_cache']==execution['same_state_query_cache'];assert cache=={'hits':6718670,'misses':3710361,'underlying_calls':3763936,'invalidations':1161,'verified_time_reads':4628}
    assert execution['resource_limits']==carddata['resources']
    result.update(same_state_query_cache=cache,cache_scope='Actualsingleprefix softwarecounters; no matchednative speedup or per-call timing inference',status='PASS_TRUNCATED_PREFIX_DATA_INTEGRITY_TARGET_NOT_REACHED',raw_status='PASS_LOCAL_ONLY',verified_steps=1157,ACK_records=2314,reconciled_intervals=1157,observed_motion_intervals=dict(phases),log_capture_records=len(logrows),final_logs_status=bridge['final_logs']['status'],log_stream_final_bytes=cursor,controlled_service={k:None for k in failure['accounting']},internal_initial_accounting=failure['accounting'],activation1200='NOT_REACHED',controlled_red1207='NOT_REACHED',full_control_cycles=0,available_monitor_evidence=monitor,xml=xml,connection_attempts=239,successful_connections=1)
    checks['final_raw_readback']=verify(manifest['files'])
    return result
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--local-raw',action='store_true');a=p.parse_args();print(json.dumps(review(a.local_raw),indent=2))

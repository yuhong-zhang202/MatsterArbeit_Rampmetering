"""Bounded readonly failure audit; raw verification requires explicit --local-raw."""
import argparse, gzip, hashlib, json
from pathlib import Path
import xml.etree.ElementTree as ET
ROOT = Path(__file__).resolve().parents[3]
ENG = ROOT / 'artifacts/candidate_a_native_smoke_execution_20261011_v1/engineering'
RAW = ROOT / 'data/raw/candidate_a_native_smoke_bridge_20261011_v1/CA_NATIVE_PHASE_R300_S17_SMOKE01'
def sha(b): return hashlib.sha256(b).hexdigest()
def load(p): return json.loads(p.read_text())
def verify(mapping):
    for name, expected in mapping.items():
        assert sha((ROOT/name).read_bytes()) == expected, name
    return len(mapping)
def review(local=False):
    result = {'scope': 'READONLY_FAILURE_PREFIX_NOT_QUALIFICATION', 'checks': {}, 'native_calls_by_checker': 0}
    c = result['checks']
    c['engineering_files'] = verify(load(ENG/'ENGINEERING_DELIVERY_BINDING.json')['files'])
    ctx = load(ROOT/'data/processed/candidate_a_native_smoke_bridge_20261011_v1/PRE_DATA_CONTEXT_BINDINGS.json')
    c['protected_files'] = verify(ctx['protected']); assert c['protected_files'] == 536
    # Historical context includes an absence expectation for authorization, now superseded.
    current = load(ROOT/'artifacts/candidate_a_native_smoke_bridge_20261011_v1/engineering/INPUT_BINDINGS_V5.json')
    c['unchanged_V5_files'] = verify(current['files'])
    a = load(ROOT/'artifacts/candidate_a_native_smoke_bridge_20261011_v1/AUTHORIZATION_NATIVE_EXECUTION.json')
    u = ROOT/a['human_authorization_reference']; assert sha(u.read_bytes()) == a['human_authorization_record_sha256']
    release = load(ROOT/'artifacts/candidate_a_native_smoke_bridge_20261011_v1/engineering/EXECUTION_RELEASE.json')
    assert release['authorization_sha256'] == sha((ROOT/'artifacts/candidate_a_native_smoke_bridge_20261011_v1/AUTHORIZATION_NATIVE_EXECUTION.json').read_bytes())
    for v in release['review_sha256'].values(): assert sha((ROOT/v['path']).read_bytes()) == v['sha256']
    receipt=load(ENG/'EXECUTION_RECEIPT.json')
    assert receipt['native_starts']==1 and receipt['CLI_exit_code']==1 and receipt['native_exit_code']==0
    assert receipt['card_sha256']==a['card_sha256']==release['card_sha256']
    result['local_raw_verification']='SKIP: raw private/ignored; use --local-raw on authorized host'
    if not local: result['status']='PASS_PUBLIC_RECEIPT_BINDING_ONLY'; return result
    manifest=load(ENG/'RAW_FINAL_SHA256.json'); c['raw_files']=verify(manifest['files'])
    actual={str(p.relative_to(ROOT)) for p in RAW.rglob('*') if p.is_file()}
    assert actual==set(manifest['files']) and len(actual)==53
    c['raw_bytes']=sum((ROOT/p).stat().st_size for p in actual); assert c['raw_bytes']==1804472
    out=RAW/'outputs'; failure=load(out/'failure_snapshot.json'); bridge=load(out/'bridge_receipt.json')
    for key in ('last_completed_s','last_accounted_s','last_step_ack'): assert failure[key] is None and bridge[key] is None
    assert not list(out.glob('*ack*')) and not list(out.glob('post*'))
    pre=[json.loads(x) for x in (out/'pre_steps.jsonl').read_text().splitlines()]
    assert len(pre)==1 and pre[0]['time_s']==0 and pre[0]['preparation']['step_advance_performed'] is False
    trace=[json.loads(x) for x in (out/'startup_trace.jsonl').read_text().splitlines()]
    assert len(trace)==248 and sum(x['outcome']=='CONNECTED' for x in trace)==1
    assert [x['attempt'] for x in trace]==list(range(1,249))
    stages=[json.loads(x) for x in (out/'log_intervals.jsonl').read_text().splitlines()]
    assert [x['stage'] for x in stages]==['STARTUP_CONNECT_ACK','PRE_MOTION_AFTER_CONTROL_AND_OBSERVATION','AFTER_NATIVE_CLOSE_PROCESS_EOF']
    cursor={n:0 for n in stages[0]['streams']}
    for stage in stages:
        for name,row in stage['streams'].items():
            b=(out/name).read_bytes(); start,end=row['byte_start'],row['byte_end']
            assert start==cursor[name] and 0<=start<=end<=len(b)
            assert sha(b[:end])==row['prefix_sha256'] and sha(b[start:end])==row['fragment_sha256']
            assert b[start:end].hex()==row['raw_fragment_hex']
            cursor[name]=end
    assert all(cursor[n]==(out/n).stat().st_size for n in cursor)
    stderr=(out/'sumo_stderr.log').read_text(); warnings=stderr.splitlines()
    assert len(warnings)==17 and all('Phase 2 only loops backs to itself' in x for x in warnings)
    assert stages[0]['streams']['sumo_stderr.log']['byte_end']==0
    assert stages[1]['streams']['sumo_stderr.log']['byte_end']==1443
    log=(out/'sumo.log').read_text()
    assert 'started with time: 0.00.' in log and 'ended at time: 0.00.' in log and 'Inserted: 0 (Loaded: 4)' in log
    xml=[]
    for p in sorted(out.glob('*.xml*')):
        b=gzip.decompress(p.read_bytes()) if p.suffix=='.gz' else p.read_bytes()
        if not b:
            assert p.name=='tls_states.xml'; xml.append({'name':p.name,'status':'EMPTY_NON_XML_NOT_OBSERVED'}); continue
        root=ET.fromstring(b)
        row={'name':p.name,'root':root.tag,'child_count':len(root)}
        if p.name=='tripinfo.xml':
            assert len(root)==3 and all(x.attrib['depart']=='-1' and x.attrib['arrival']=='-1.00' and x.attrib['vaporized']=='end' for x in root)
            row['records']=[dict(x.attrib) for x in root]; row['meaning']='UNDEPARTED_END_RECORDS_NOT_TRAVEL_OBSERVATIONS'
        else: assert len(root)==0
        xml.append(row)
    result.update(local_raw_verification='PASS', status='PASS_FAILURE_DATA_INTEGRITY_SMOKE_TARGET_NOT_REACHED', log_stages=[{'stage':x['stage'],'stderr_byte_end':x['streams']['sumo_stderr.log']['byte_end']} for x in stages], xml=xml, connection_attempts=248, successful_connections=1, step_ACK_count=0, pre_step_count=1, native_warning_lines=17, initial_ledger=dict(failure['accounting']), service_observations={k:None for k in failure['accounting']}, full_cycles=0, initialization603='NOT_REACHED', controlled1200='NOT_REACHED', first_red1207='NOT_REACHED', native_PID=None, observation_qualification='NOT_TESTED')
    # Final immutable readback after all analysis reads.
    c['raw_final_readback']=verify(manifest['files'])
    return result
if __name__=='__main__':
    parser=argparse.ArgumentParser(); parser.add_argument('--local-raw',action='store_true'); args=parser.parse_args()
    print(json.dumps(review(args.local_raw),indent=2,ensure_ascii=False))

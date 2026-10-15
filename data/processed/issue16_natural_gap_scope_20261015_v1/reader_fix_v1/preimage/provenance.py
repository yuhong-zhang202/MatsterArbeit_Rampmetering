"""Hash/identity/EOF provenance. No process launch or version invocation."""
import hashlib,json
from pathlib import Path
import xml.etree.ElementTree as ET
from scripts.natural_service_audit_20261015_v1.actual import need
from scripts.cumulative_full_catalogue_audit_20261014_v1.evidence import log_eof


def sha(path):
    h=hashlib.sha256()
    with Path(path).open('rb') as f:
        for block in iter(lambda:f.read(1048576),b''):h.update(block)
    return h.hexdigest()
def read(path):return json.loads(Path(path).read_text())
def resolve(root,path):
    p=Path(path);return p if p.is_absolute() else root/p


def verify(manifest_path,card_path,root):
    root=Path(root).resolve();card_path=Path(card_path).resolve();card=read(card_path);manifest=read(manifest_path)
    s=card['spec'];need(s['activation_s']==600 and s['end_s']==4200 and s['seed']==17 and s['mode']=='real_alinea' and s['scheduler']=='RAW_C_MINUS_SCHEDULED_NOMINAL_E','NATIVE_SCOPE')
    need(s['counts']==dict(M=3000,R=600,U=300,X=150),'NATIVE_COHORT_SCOPE')
    need(s['Feedback']==dict(target_percent=11,gain_veh_h_per_percentage_point=70,bounds_veh_h=[300,900],initial_veh_h=900,sample_s=30),'NATIVE_FEEDBACK_SCOPE')
    raw=resolve(root,card['output']);package=resolve(root,card['package'])
    need(raw==root/'data/raw/natural_actuator_qualification_20261015_v1'/s['run_id']/'outputs' and package==root/'artifacts/natural_actuator_qualification_20261015_v1/engineering/packages_v1'/s['run_id'],'NATIVE_OUTPUT_PACKAGE_NAMESPACE')
    need(raw.is_dir(),'NATIVE_NOT_RUN_NO_RAW')
    for path,value in manifest['files'].items():
        p=resolve(root,path);expected=value['sha256'] if isinstance(value,dict) else value
        need(p.is_file() and sha(p)==expected,'RAW_HASH:'+path)
        if isinstance(value,dict) and 'bytes' in value:need(p.stat().st_size==value['bytes'],'RAW_FILE_BYTES:'+path)
    actual={str(p.relative_to(root)) for p in raw.parent.rglob('*') if p.is_file()}
    need(actual==set(manifest['files']) and sum(resolve(root,p).stat().st_size for p in actual)==manifest['bytes'],'RAW_INVENTORY_OR_BYTES')
    if 'file_count' in manifest:need(manifest['file_count']==len(actual),'RAW_FILE_COUNT')
    for key in ('sources_sha256','prepared_input_sha256','inherited_inputs_sha256'):
        for path,h in card[key].items():need(sha(resolve(root,path))==h,'BOUND_FILE:'+path)
    for path,h in card['environment']['files_sha256'].items():need(sha(resolve(root,path))==h,'ENVIRONMENT_FILE:'+path)
    cfg=ET.parse(package/'scenario.sumocfg').getroot();need(cfg.find('./time/step-length').get('value')=='1' and cfg.find('./time/end').get('value')=='4200','CONFIG_CLOCK')
    for name,value in [('precision','8'),('tripinfo-output.write-unfinished','true'),('tripinfo-output.write-undeparted','true')]:
        need(cfg.find('./output/'+name) is not None and cfg.find('./output/'+name).get('value')==value,'CONFIG_REQUIRED_OUTPUT:'+name)
    net=resolve(root,cfg.find('./input/net-file').get('value'));need(sha(net)==card['network_sha256'],'NETWORK_HASH')
    receipt=read(raw/'bridge_receipt.json');need(receipt['native_started'] is True and receipt['run_id']==s['run_id'] and receipt['card_sha256']==sha(card_path),'NATIVE_RECEIPT_IDENTITY')
    need(read(raw/'card.json')==card,'RAW_CARD_IDENTITY')
    release=read(raw/'release.json');need(release['status']=='CANONICAL_NATURAL_EXECUTION_RELEASE' and release['card_sha256']==sha(card_path),'RELEASE_IDENTITY_OR_AUTHORIZATION')
    for item in release['reviews'].values():need(sha(resolve(root,item['path']))==item['sha256'],'RELEASE_REVIEW_HASH')
    need(set(release['reviews'])=={'engineering','data','science'},'RELEASE_REVIEWS')
    authority=release['direct_execution_authority'];need(sha(resolve(root,authority['path']))==authority['sha256'],'DIRECT_EXECUTION_AUTHORITY_HASH')
    a=read(resolve(root,authority['path']));need(a['status']=='DIRECT_USER_APPROVED_EXACT_NATURAL_EXECUTION' and a['run_id']==s['run_id'] and a['card_sha256']==sha(card_path) and a['lifts_current_no_SUMO_restriction'] is True,'DIRECT_NATIVE_AUTHORITY_NOT_GRANTED')
    budget=receipt['total_budget_before_run'];need(budget['scope_id']=='NATURAL_QUALIFICATION_20261015_V1' and budget['approved_total_monitored_s']==900 and budget['old_remainder_pooled'] is False and not budget['unknown_reserved'] and release['budget_approval_sha256']==budget['budget_approval_sha256'],'INDEPENDENT_RESOURCE_SCOPE_BINDING')
    budget_path=root/'artifacts/natural_actuator_qualification_20261015_v1/NATIVE_BUDGET_APPROVAL.json'
    need(sha(budget_path)==release['budget_approval_sha256'],'BUDGET_APPROVAL_HASH')
    b=read(budget_path);need(b['status']=='DIRECT_USER_APPROVED_INDEPENDENT_NUMERIC_BUDGET' and b['scope_id']==budget['scope_id'] and b['total_monitored_s']==900,'BUDGET_APPROVAL_NOT_GRANTED')
    need(sha(resolve(root,b['direct_user_authority']['path']))==b['direct_user_authority']['sha256'],'BUDGET_USER_AUTHORITY_HASH')
    need(card['guardian']==dict(schema='NATURAL_QUALIFICATION_GUARDIAN_V1',inner_wall_limit_s=870,cleanup_reserve_s=30,outer_wall_limit_s=900,receipt=card['guardian']['receipt'],fallback_receipt=card['guardian']['fallback_receipt']),'GUARDIAN_CARD_SCHEMA')
    inherited=[h for p,h in card['inherited_inputs_sha256'].items() if p.endswith('/demand.rou.xml')]
    need(len(inherited)==1 and sha(package/'demand.rou.xml')==inherited[0],'NATURAL_REQUESTS_CHANGED')
    return card,receipt,raw,package,net,dict(status='PASS_NATIVE_HASH_PROVENANCE',card_sha256=sha(card_path),manifest_sha256=sha(manifest_path),files=len(actual),bytes=manifest['bytes'])


def eof(raw,receipt,logs,guardian,identity,card_sha,release_sha):
    log_eof(logs,raw,receipt)
    need(receipt['final_logs']['process_returncode']==0 and receipt['final_logs']['all_streams_bound'] is True,'NATIVE_FINAL_PROCESS_EOF')
    need(guardian['card_sha256']==card_sha and guardian['release_sha256']==release_sha and guardian['run_id']==receipt['run_id'],'GUARDIAN_IDENTITY')
    clean=guardian['group_cleanup'];need(clean['ownership_verified'] is True and clean['no_live_owned_members'] is True,'OWNED_CLEANUP_UNKNOWN')
    need(guardian['worker_returncode']==0 and guardian['stop_reason']=='WORKER_EXITED' and guardian['native_identity_verified'] is True,'GUARDIAN_STOP_OR_EXIT')
    need(guardian['monitored_elapsed_through_cleanup_s']<=guardian['outer_wall_limit_s'],'GUARDIAN_BUDGET_EXCEEDED')
    need(identity['run_id']==receipt['run_id'] and identity['card_sha256']==card_sha and identity['release_sha256']==release_sha,'NATIVE_OWNED_IDENTITY_BINDING')
    need(identity['schema']=='NATURAL_OWNED_PROCESS_IDENTITY_V1' and identity['ownership_verified'] is True and
         identity['child_returncode_before'] is None and identity['child_returncode_after'] is None,'OWNED_NATIVE_STARTED_UNKNOWN')
    w,n=identity['worker'],identity['native']
    need(w==guardian['worker'] and w['status']==n['status']=='OBSERVED' and w['pid']==w['pgid']==w['sid']==n['pgid']==n['sid'] and
         type(n['pid']) is int and n['pid']>0,'OWNED_NATIVE_GROUP_BINDING')
    return dict(status='PASS_NATIVE_EOF_AND_OWNERSHIP',no_live_owned_members=True,scope='EXACT_OWNED_PROCESS_GROUP_NOT_GENERAL_DAEMON_CONTROL')

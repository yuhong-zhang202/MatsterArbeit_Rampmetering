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


POSTANALYSIS_PATHS=frozenset('scripts/natural_actuator_qualification_20261015_v1/'+n for n in ('actual.py','streaming.py','provenance.py'))
CURRENT_GAP_CONTRACT='ORDINARY_NATIVE_REFERENCE_OBSERVATION_V1'


def resource_card(card,root,budget=None):
    run=card['spec']['run_id']
    bounds={'QUAL_NATURAL_ALINEA_R900_S17_01':(900,870),'QUAL_NATURAL_ALINEA_R900_S17_02':(816,786),'QUAL_NATURAL_ALINEA_R900_S17_03':(641,611)}
    need(run in bounds,'UNKNOWN_NATURAL_RESOURCE_IDENTITY');outer,inner=bounds[run]
    need(card['resources']==dict(wall_limit_s=outer,startup_limit_s=60,run_limit_bytes=None,minimum_free_bytes=5000000000),'EXACT_RESOURCE_CARD_LIMITS')
    task='actuator_acceptance_20261015_v1' if run.endswith('_03') else 'natural_actuator_qualification_20261015_v1'
    expected=dict(schema='NATURAL_QUALIFICATION_GUARDIAN_V1',inner_wall_limit_s=inner,cleanup_reserve_s=30,outer_wall_limit_s=outer,receipt=f'data/raw/natural_actuator_qualification_20261015_v1/{run}/guardian_receipt.json',fallback_receipt=f'artifacts/{task}/engineering/runs/{run}/guardian_receipt.json')
    need(card['guardian']==expected,'GUARDIAN_CARD_SCHEMA')
    if run.endswith('_02'):
        spent=83.63743604102638
        need(card['spec'].get('current_gap_responsibility_contract',{}).get('policy')==CURRENT_GAP_CONTRACT,'RUN02_CURRENT_GAP_CONTRACT_REQUIRED')
        need(card['resources_status']=='PROPOSED_PENDING_EXACT_CARD_EXECUTION_APPROVAL','RUN02_RESOURCE_STATUS')
        need(card['resources_scope']==dict(scope_id='NATURAL_QUALIFICATION_20261015_V1',approved_total_monitored_s=900,charged_before_preparation_s=spent,remaining_before_preparation_s=900-spent,start_count_before_preparation=1,unknown_reserved_before_preparation=[],budget_approval_sha256=sha(resolve(root,'artifacts/natural_actuator_qualification_20261015_v1/NATIVE_BUDGET_APPROVAL.json')),old_scope_available_not_pooled=True,current_identity_ordinal=2,max_new_identities=2,further_identity_prepared=False),'RUN02_EXISTING_RESOURCE_SCOPE')
        need(card['qualification_proposal']==dict(status='PROPOSED_PENDING_EXACT_CARD_USER_CONFIRMATION',purpose='LIMITED_OPERATIONAL_AND_MEASUREMENT_QUALIFICATION_NOT_FORMAL',required_horizon_s=4200,required_evaluation_windows_s=[[t,t+300] for t in range(1200,3000,300)],technical_pass='EXACT_ACCOUNTING_VERSION_POPULATION_EOF_ONLY',not_qualified='HARD_ANOMALY_REQUIRED_UNKNOWN_OR_UNEXPLAINED_PERSISTENT_LOSS_WITH_OPPORTUNITY',not_tested='BRANCH_NOT_OBSERVED_OR_INSUFFICIENT_OPPORTUNITY',alinea_numeric_tracking_accuracy='NOT_ASSESSED',native_safety_proven=False,formal_experiment_authorized=False),'RUN02_QUALIFICATION_PROPOSAL')
        if budget is not None:need(budget['known_settled']=={'QUAL_NATURAL_ALINEA_R900_S17_01':spent} and budget['charged_monitored_s']==spent and budget['remaining_s']==900-spent and budget['start_count']==1,'RUN02_NATIVE_RESOURCE_BASELINE')
    if run.endswith('_03'):
        spent=258.87379404105013
        need(card['spec'].get('safety_acceptance_contract',{}).get('policy')=='FIRST_YELLOW_SOURCE_SCALE_OBSERVATION_V1' and
             card['resources_status']=='PROPOSED_PENDING_EXACT_CARD_EXECUTION_APPROVAL','RUN03_CONTRACT_AND_STATUS')
        need(card['resources_scope']==dict(scope_id='NATURAL_QUALIFICATION_20261015_V1',approved_total_monitored_s=900,
            charged_before_preparation_s=spent,remaining_before_preparation_s=900-spent,start_count_before_preparation=2,
            unknown_reserved_before_preparation=[],budget_approval_sha256=sha(resolve(root,'artifacts/natural_actuator_qualification_20261015_v1/NATIVE_BUDGET_APPROVAL.json')),
            old_scope_available_not_pooled=True,current_identity_ordinal=3,additional_exact_single_start_status='PROPOSED_NOT_APPROVED',
            max_prepared_new_identities=1,further_identity_prepared=False),'RUN03_RESOURCE_SCOPE')
        if budget is not None:need(budget['known_settled']=={'QUAL_NATURAL_ALINEA_R900_S17_01':83.63743604102638,'QUAL_NATURAL_ALINEA_R900_S17_02':175.23635800002376} and
            budget['charged_monitored_s']==spent and budget['remaining_s']==900-spent and budget['start_count']==2,'RUN03_NATIVE_RESOURCE_BASELINE')
    return dict(run_id=run,outer_wall_limit_s=outer,inner_wall_limit_s=inner,cleanup_reserve_s=30)


def guardian_receipt_limits(guardian,card_guardian):
    need(all(type(guardian.get(k)) is int and guardian[k]==card_guardian[k] for k in ('inner_wall_limit_s','cleanup_reserve_s','outer_wall_limit_s')),'GUARDIAN_RECEIPT_CARD_LIMITS')


def current_gap_contract(spec,root):
    item=spec.get('current_gap_responsibility_contract')
    if item is None:return dict(enabled=False)
    path='artifacts/issue16_natural_gap_scope_20261015_v1/HUMAN_CONTRACT_APPROVAL_RECEIPT_V1.json'
    need(item==dict(policy=CURRENT_GAP_CONTRACT,prospective_new_green='UNCHANGED_STRICT',ordinary_current_queries='OBSERVATIONAL_ONLY',approval_receipt=path,approval_sha256=item.get('approval_sha256'),native_safety_proven=False),'UNKNOWN_CURRENT_GAP_CARD_CONTRACT')
    need(item['native_safety_proven'] is False,'CURRENT_GAP_NOT_SAFETY_CERTIFICATE')
    need(sha(resolve(root,path))==item['approval_sha256'],'CURRENT_GAP_APPROVAL_HASH')
    approval=read(resolve(root,path))
    need(approval['schema']=='ISSUE16_CONTRACT_APPROVAL_RECEIPT_V1' and approval['answer']=='批准该合同及最小离线实现' and approval['approved_document']=='docs/development/ISSUE16_CURRENT_GAP_SCOPE_DECISION_20261015.md' and approval['SUMO_execution_authorized'] is False and approval['new_exact_card_approval_required'] is True,'CURRENT_GAP_EXPLICIT_APPROVAL')
    return dict(enabled=True,**item)


def safety_acceptance_proof(card,approval,card_sha,approval_sha,root):
    from scripts.natural_actuator_qualification_20261015_v1.episode import CONTRACT,RUN,SOURCE
    item=card['spec'].get('safety_acceptance_contract')
    if card['spec']['run_id']!=RUN:
        need(item is None,'OLD_RUN_NEW_SAFETY_CONTRACT');return None
    need(item and item['policy']==CONTRACT and item['status']=='PROPOSED_DEFAULT_INACTIVE' and item['source_commit']==SOURCE and
         item['configured_model']=='Krauss' and item['configured_Euler_dt_s']==1 and item['no_model_or_JM_override'] is True and
         item['classification']=='NUMERICAL_SCALE_COMPATIBLE_NOT_CONFIRMED_NUMERIC' and item['followup']=='ONE_UNCHANGED_STEP_REQUIRED_NO_RENEWAL_WHILE_PENDING','RUN03_SAFETY_CARD_SCOPE')
    need(card['spec'].get('accuracy_acceptance_contract')==dict(policy='PREDECLARED_LOCAL20_BACKLOG_EXTERNAL_BOUNDARY_V1',
         status='PROPOSED_PENDING_EXACT_CARD_APPROVAL',evaluator='scripts/actuator_acceptance_20261015_v1/accuracy.py',
         normalizer='scripts/actuator_acceptance_20261015_v1/normalize.py',absolute_bound_vehicles=2,relative_bound=.05,formal_experiment_authorized=False),'RUN03_ACCURACY_CONTRACT')
    need(card['spec'].get('acceptance_observation_contract')==dict(policy='FIXED_RECEIVER_DOMAIN_AND_LOCAL20_V1',local_storage_domain_m=[184.49,204.49],
         minimum_actual_R_fronts=2,receiver_lanes=[':ramp_mid_0_0','ramp_accel_0',':freeway_merge_2_0','merge_section_0','merge_section_1','merge_section_2'],
         cause='UNESTABLISHED_UNLESS_SEPARATELY_BOUND'),'RUN03_OBSERVATION_CONTRACT')
    need(item['standard']=='docs/development/ACTUATOR_ACCEPTANCE_CRITERIA.md' and sha(resolve(root,item['standard']))==item['standard_sha256'],'RUN03_STANDARD_HASH')
    need(approval['status']=='DIRECT_USER_APPROVED_EXACT_NATURAL_EXECUTION' and approval['run_id']==RUN and approval['card_sha256']==card_sha and
         approval['lifts_current_no_SUMO_restriction'] is True and approval['acceptance_contract_approved']==CONTRACT and approval['accuracy_criteria_approved']=='PREDECLARED_LOCAL20_BACKLOG_EXTERNAL_BOUNDARY_V1' and
         approval['acceptance_standard_sha256']==item['standard_sha256'] and approval['additional_exact_single_start_approved'] is True,'RUN03_DIRECT_EXTRA_AUTHORITY')
    return dict(enabled=True,contract=CONTRACT,source_commit=SOURCE,status='EXACT_ACCEPTANCE_CONTRACT_AUTHORITY_VERIFIED',
        configured_model='Krauss',configured_Euler_dt_s=1,no_model_or_JM_override=True,run_id=RUN,approval_sha256=approval_sha,execution_card_sha256=card_sha)


def execution_sources(root,raw,sources,postanalysis_reader_v1=False):
    changes=[]
    for path,h in sources.items():
        current=sha(resolve(root,path))
        if postanalysis_reader_v1:
            need(not Path(path).is_absolute() and '..' not in Path(path).parts,'EXECUTION_SNAPSHOT_PATH')
            need(sha(raw/'snapshots'/path)==h,'EXECUTION_SOURCE_SNAPSHOT:'+path)
        need(current==h or postanalysis_reader_v1 and path in POSTANALYSIS_PATHS,'BOUND_FILE:'+path)
        if current!=h:changes.append(dict(path=path,execution_sha256=h,postanalysis_sha256=current))
    return dict(mode='EXPLICIT_POSTANALYSIS_READER_V1' if postanalysis_reader_v1 else 'EXACT_CURRENT_CARD_SOURCES',execution_source_count=len(sources),changed_reader_files=changes)


def gap_stop(receipt,row):
    """Bind the one supported observed POST failure, never authorize motion."""
    last=receipt['last_completed_s'];error='DiagnosticStop:POST_CURRENT_GAP_BOUND_DENIED'
    need(type(last) is int and 600<last<=4200 and receipt['last_accounted_s']==last and receipt['status']=='ABORTED_UNKNOWN' and receipt['error']==error,'UNBOUND_GAP_STOP_RECEIPT')
    ack=receipt['last_step_ack']
    need(ack['requested_target_s']==last and ack['actual_readback_s']==last and ack['ACK_received'] is True and ack['actual_time_verified'] is True,'GAP_STOP_ACK')
    need(row is not None and row['time_begin_s']==last-1 and row['time_end_s']==row['observed_time_s']==last and row['accounting_complete'] is True and row['motion']=='G' and row['status']=='STOP_OBSERVED_AFTER_STEP','GAP_STOP_ROW')
    need(row.get('reasons')==['POST_CURRENT_GAP_BOUND_DENIED'] and row.get('terminal_reason')==error,'GAP_STOP_CAUSE')
    d=row['post_native_receiver_decision'];q=d['current_following'];receiver=row['post_receiver']
    need(d['decision']==q['status']=='STOP_CURRENT_GAP_BOUND_DENIED' and d['time_s']==q['time_s']==last and d['prospective_available'] is False and q['hard_screen_pass'] is False,'GAP_STOP_QUERY')
    need(d['original_prospective_receiver']==receiver and receiver['available'] is False and receiver['front_id']==q['vehicle_id'] and receiver['leader']['vehicle_id']==q['leader_id'],'GAP_STOP_RECEIVER_BINDING')
    return dict(status='OBSERVED_POST_GAP_STOP_RETAINED',last_ACK=last,error=error)


def verify(manifest_path,card_path,root,postanalysis_reader_v1=False):
    root=Path(root).resolve();card_path=Path(card_path).resolve();card=read(card_path);manifest=read(manifest_path)
    s=card['spec'];need(s['activation_s']==600 and s['end_s']==4200 and s['seed']==17 and s['mode']=='real_alinea' and s['scheduler']=='RAW_C_MINUS_SCHEDULED_NOMINAL_E','NATIVE_SCOPE')
    need(s['counts']==dict(M=3000,R=600,U=300,X=150),'NATIVE_COHORT_SCOPE')
    need(s['Feedback']==dict(target_percent=11,gain_veh_h_per_percentage_point=70,bounds_veh_h=[300,900],initial_veh_h=900,sample_s=30),'NATIVE_FEEDBACK_SCOPE')
    raw=resolve(root,card['output']);package=resolve(root,card['package'])
    task='actuator_acceptance_20261015_v1' if s['run_id']=='QUAL_NATURAL_ALINEA_R900_S17_03' else 'natural_actuator_qualification_20261015_v1'
    need(raw==root/'data/raw/natural_actuator_qualification_20261015_v1'/s['run_id']/'outputs' and package==root/'artifacts'/task/'engineering/packages_v1'/s['run_id'],'NATIVE_OUTPUT_PACKAGE_NAMESPACE')
    need(raw.is_dir(),'NATIVE_NOT_RUN_NO_RAW')
    for path,value in manifest['files'].items():
        p=resolve(root,path);expected=value['sha256'] if isinstance(value,dict) else value
        need(p.is_file() and sha(p)==expected,'RAW_HASH:'+path)
        if isinstance(value,dict) and 'bytes' in value:need(p.stat().st_size==value['bytes'],'RAW_FILE_BYTES:'+path)
    actual={str(p.relative_to(root)) for p in raw.parent.rglob('*') if p.is_file()}
    need(actual==set(manifest['files']) and sum(resolve(root,p).stat().st_size for p in actual)==manifest['bytes'],'RAW_INVENTORY_OR_BYTES')
    if 'file_count' in manifest:need(manifest['file_count']==len(actual),'RAW_FILE_COUNT')
    source_proof=execution_sources(root,raw,card['sources_sha256'],postanalysis_reader_v1)
    for key in ('prepared_input_sha256','inherited_inputs_sha256'):
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
    resource_proof=resource_card(card,root,budget)
    safety_proof=safety_acceptance_proof(card,a,sha(card_path),authority['sha256'],root)
    inherited=[h for p,h in card['inherited_inputs_sha256'].items() if p.endswith('/demand.rou.xml')]
    need(len(inherited)==1 and sha(package/'demand.rou.xml')==inherited[0],'NATURAL_REQUESTS_CHANGED')
    return card,receipt,raw,package,net,dict(status='PASS_NATIVE_HASH_PROVENANCE',card_sha256=sha(card_path),manifest_sha256=sha(manifest_path),files=len(actual),bytes=manifest['bytes'],source_versions=source_proof,current_gap_contract=current_gap_contract(s,root),resource_contract=resource_proof,safety_acceptance=safety_proof)


def eof(raw,receipt,logs,guardian,identity,card_sha,release_sha,terminal_row=None,card_guardian=None):
    log_eof(logs,raw,receipt)
    need(receipt['final_logs']['process_returncode']==0 and receipt['final_logs']['all_streams_bound'] is True,'NATIVE_FINAL_PROCESS_EOF')
    need(guardian['card_sha256']==card_sha and guardian['release_sha256']==release_sha and guardian['run_id']==receipt['run_id'],'GUARDIAN_IDENTITY')
    if card_guardian is not None:guardian_receipt_limits(guardian,card_guardian)
    clean=guardian['group_cleanup'];need(clean['ownership_verified'] is True and clean['no_live_owned_members'] is True,'OWNED_CLEANUP_UNKNOWN')
    failed_prefix=guardian['worker_returncode']==1
    if failed_prefix:gap_stop(receipt,terminal_row)
    need(type(guardian['worker_returncode']) is int and guardian['worker_returncode'] in (0,1) and guardian['stop_reason']=='WORKER_EXITED' and guardian['native_identity_verified'] is True and (failed_prefix or not receipt.get('error')),'GUARDIAN_STOP_OR_EXIT')
    need(guardian['monitored_elapsed_through_cleanup_s']<=guardian['outer_wall_limit_s'],'GUARDIAN_BUDGET_EXCEEDED')
    need(identity['run_id']==receipt['run_id'] and identity['card_sha256']==card_sha and identity['release_sha256']==release_sha,'NATIVE_OWNED_IDENTITY_BINDING')
    need(identity['schema']=='NATURAL_OWNED_PROCESS_IDENTITY_V1' and identity['ownership_verified'] is True and
         identity['child_returncode_before'] is None and identity['child_returncode_after'] is None,'OWNED_NATIVE_STARTED_UNKNOWN')
    w,n=identity['worker'],identity['native']
    need(w==guardian['worker'] and w['status']==n['status']=='OBSERVED' and w['pid']==w['pgid']==w['sid']==n['pgid']==n['sid'] and
         type(n['pid']) is int and n['pid']>0,'OWNED_NATIVE_GROUP_BINDING')
    return dict(status='OBSERVED_NATIVE_EOF_AFTER_CONTROLLER_STOP' if failed_prefix else 'PASS_NATIVE_EOF_AND_OWNERSHIP',worker_returncode=guardian['worker_returncode'],native_returncode=0,no_live_owned_members=True,scope='EXACT_OWNED_PROCESS_GROUP_NOT_GENERAL_DAEMON_CONTROL')

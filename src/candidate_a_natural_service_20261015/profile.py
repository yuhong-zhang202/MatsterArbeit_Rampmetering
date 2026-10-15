"""Natural input/card preparation. Numeric budget and release remain separate."""
from pathlib import Path
import hashlib
import json
import shutil
import xml.etree.ElementTree as ET
from src.candidate_a_unified_alinea_20261013.profile import ROOT, NETWORK, SUMO, sha, write_new, require
from src.candidate_a_natural_service_20261015.policy import parameters, PERIODS
from src.candidate_a_natural_service_20261015.current_gap_scope import CONTRACT

TASK = Path('artifacts/natural_actuator_qualification_20261015_v1/engineering')
NATURAL = Path('artifacts/formal_development_20261007_v1/inputs/DEV_M3600_R900_S17_T1_A03')
RAW = Path('data/raw/natural_actuator_qualification_20261015_v1')
APPROVED_BOUND_END = 4200
HISTORICAL_RUN = 'QUAL_NATURAL_ALINEA_R900_S17_01'
RUN = 'QUAL_NATURAL_ALINEA_R900_S17_02'
ACCEPTANCE_RUN = 'QUAL_NATURAL_ALINEA_R900_S17_03'
ACCEPTANCE_TASK = Path('artifacts/actuator_acceptance_20261015_v1/engineering')
ACCEPTANCE_STANDARD = Path('docs/development/ACTUATOR_ACCEPTANCE_CRITERIA.md')
ACCEPTANCE_USER = Path('artifacts/actuator_acceptance_20261015_v1/NONEXECUTING_TASK_AUTHORITY.md')
USER = Path('artifacts/thesis_actuator_readiness_20261015_v1/USER_AUTHORITY.md')
READER = Path('scripts/natural_actuator_qualification_20261015_v1/actual.py')
CURRENT_GAP_APPROVAL = Path('artifacts/issue16_natural_gap_scope_20261015_v1/HUMAN_CONTRACT_APPROVAL_RECEIPT_V1.json')
LEGACY_CARD = Path('artifacts/dynamic_native_yellow_minqual_20261015_v1/engineering/packages_v1/UA_NATIVEYELLOW_DYNAMIC_S17_01/card.json')


def spec(root=ROOT):
    return dict(run_id=RUN, mode='real_alinea', fixed_command_veh_h=900,
        activation_s=600, end_s=4200, scheduler='RAW_C_MINUS_SCHEDULED_NOMINAL_E',
        evaluation_window_s=[1200,3000], output_precision=8,
        Feedback=dict(target_percent=11, gain_veh_h_per_percentage_point=70,
            bounds_veh_h=[300,900], initial_veh_h=900, sample_s=30),
        counts=dict(M=3000,R=600,U=300,X=150), seed=17,
        yellow_responsibility_contract=dict(policy='NATIVE_YELLOW_RESPONSIBILITY_COMPLETE_INPUT_DIAGNOSTIC_V1', enabled=True),
        current_gap_responsibility_contract=dict(policy=CONTRACT,
            prospective_new_green='UNCHANGED_STRICT', ordinary_current_queries='OBSERVATIONAL_ONLY',
            approval_receipt=str(CURRENT_GAP_APPROVAL), approval_sha256=sha(Path(root)/CURRENT_GAP_APPROVAL),
            native_safety_proven=False),
        qualification='NOT_TESTED_NOT_QUALIFIED')


def paths_for_run(run):
    require(run in (HISTORICAL_RUN,RUN,ACCEPTANCE_RUN),'UNPREPARED_NATURAL_IDENTITY')
    return (ACCEPTANCE_TASK if run==ACCEPTANCE_RUN else TASK),RAW


def acceptance_spec(root=ROOT):
    from src.candidate_a_natural_service_20261015.acceptance_safety import CONTRACT as safety, SOURCE
    result=spec(root)
    result.update(run_id=ACCEPTANCE_RUN,
        safety_acceptance_contract=dict(policy=safety,status='PROPOSED_DEFAULT_INACTIVE',
            source_commit=SOURCE,configured_model='Krauss',configured_Euler_dt_s=1,
            no_model_or_JM_override=True,standard=str(ACCEPTANCE_STANDARD),
            standard_sha256=sha(Path(root)/ACCEPTANCE_STANDARD),
            classification='NUMERICAL_SCALE_COMPATIBLE_NOT_CONFIRMED_NUMERIC',
            followup='ONE_UNCHANGED_STEP_REQUIRED_NO_RENEWAL_WHILE_PENDING'),
        acceptance_observation_contract=dict(policy='FIXED_RECEIVER_DOMAIN_AND_LOCAL20_V1',
            local_storage_domain_m=[184.49,204.49],minimum_actual_R_fronts=2,
            receiver_lanes=[':ramp_mid_0_0','ramp_accel_0',':freeway_merge_2_0',
                            'merge_section_0','merge_section_1','merge_section_2'],
            cause='UNESTABLISHED_UNLESS_SEPARATELY_BOUND'),
        accuracy_acceptance_contract=dict(policy='PREDECLARED_LOCAL20_BACKLOG_EXTERNAL_BOUNDARY_V1',
            status='PROPOSED_PENDING_EXACT_CARD_APPROVAL',
            evaluator='scripts/actuator_acceptance_20261015_v1/accuracy.py',
            normalizer='scripts/actuator_acceptance_20261015_v1/normalize.py',
            absolute_bound_vehicles=2,relative_bound=.05,formal_experiment_authorized=False))
    return result


def acceptance_resource_scope(root):
    from src.candidate_a_natural_service_20261015 import budget
    bound=budget.accounting(root)
    require(bound['known_settled']=={HISTORICAL_RUN:83.63743604102638,RUN:175.23635800002376} and
        bound['start_count']==2 and not bound['unknown_reserved'] and
        bound['old_remainder_pooled'] is False and bound['remaining_s']>=641,
        'THIRD_PROPOSED_CARD_RESOURCE_BASELINE_DRIFT')
    return dict(scope_id=bound['scope_id'],approved_total_monitored_s=900,
        charged_before_preparation_s=bound['charged_monitored_s'],
        remaining_before_preparation_s=bound['remaining_s'],
        start_count_before_preparation=2,unknown_reserved_before_preparation=[],
        budget_approval_sha256=bound['budget_approval_sha256'],
        old_scope_available_not_pooled=True,current_identity_ordinal=3,
        additional_exact_single_start_status='PROPOSED_NOT_APPROVED',
        max_prepared_new_identities=1,further_identity_prepared=False)


def resource_scope(root):
    """Read the existing settled ledger; preparation cannot reset its cost."""
    from src.candidate_a_natural_service_20261015 import budget
    bound=budget.accounting(root)
    require(bound['known_settled']=={HISTORICAL_RUN:83.63743604102638} and
            bound['start_count']==1 and not bound['unknown_reserved'] and
            bound['old_remainder_pooled'] is False, 'SECOND_CARD_RESOURCE_BASELINE_DRIFT')
    return dict(scope_id=bound['scope_id'],approved_total_monitored_s=900,
        charged_before_preparation_s=bound['charged_monitored_s'],
        remaining_before_preparation_s=bound['remaining_s'],
        start_count_before_preparation=bound['start_count'],unknown_reserved_before_preparation=[],
        budget_approval_sha256=bound['budget_approval_sha256'],
        old_scope_available_not_pooled=True,current_identity_ordinal=2,
        max_new_identities=2,further_identity_prepared=False)


def resources():
    return dict(wall_limit_s=816,startup_limit_s=60,run_limit_bytes=None,minimum_free_bytes=5000000000)


def guardian_spec():
    return dict(schema='NATURAL_QUALIFICATION_GUARDIAN_V1',inner_wall_limit_s=786,
        cleanup_reserve_s=30,outer_wall_limit_s=816,
        receipt=str(RAW/RUN/'guardian_receipt.json'),
        fallback_receipt=str(TASK/'runs'/RUN/'guardian_receipt.json'))


def qualification_proposal():
    return dict(status='PROPOSED_PENDING_EXACT_CARD_USER_CONFIRMATION',
        purpose='LIMITED_OPERATIONAL_AND_MEASUREMENT_QUALIFICATION_NOT_FORMAL',
        required_horizon_s=4200,required_evaluation_windows_s=[[t,t+300] for t in range(1200,3000,300)],
        technical_pass='EXACT_ACCOUNTING_VERSION_POPULATION_EOF_ONLY',
        not_qualified='HARD_ANOMALY_REQUIRED_UNKNOWN_OR_UNEXPLAINED_PERSISTENT_LOSS_WITH_OPPORTUNITY',
        not_tested='BRANCH_NOT_OBSERVED_OR_INSUFFICIENT_OPPORTUNITY',
        alinea_numeric_tracking_accuracy='NOT_ASSESSED',native_safety_proven=False,
        formal_experiment_authorized=False)


def acceptance_qualification_proposal():
    proposal=qualification_proposal()
    proposal.update(alinea_numeric_tracking_accuracy='PROPOSED_WINDOW_CRITERION_NOT_YET_APPROVED',
        full_horizon_required=True,unobserved_branch='NOT_TESTED',
        conditional_subset_not_full_domain_qualification=True)
    return proposal


def acceptance_registration(root):
    """Preregister finite geometry without a self/card/future-result hash."""
    from src.candidate_a_natural_service_20261015.acceptance_safety import RECEIVER_LANES
    root=Path(root)
    lanes={x.get('id'):x for edge in ET.parse(root/NETWORK).getroot().findall('edge')
           for x in edge.findall('lane')}
    require('ramp_storage_0' in lanes and float(lanes['ramp_storage_0'].get('length'))==204.49,
        'ACCEPTANCE_STORAGE_GEOMETRY_DRIFT')
    geometry={lane:float(lanes[lane].get('length')) for lane in RECEIVER_LANES}
    require(all(__import__('math').isfinite(x) and x>0 for x in geometry.values()),
        'ACCEPTANCE_RECEIVER_GEOMETRY_UNKNOWN')
    source=dict(path=str(NETWORK),sha256=sha(root/NETWORK))
    return dict(run_id=ACCEPTANCE_RUN,opportunity_geometry=dict(source=source,
        lane_domains=[dict(lane_id='ramp_storage_0',start_pos_m=184.49,end_pos_m=204.49)],
        network_sha256=source['sha256'],receiver_domain_source=dict(source),
        receiver_lane_ids=list(RECEIVER_LANES),receiver_geometry_m=geometry))


def prepared_trees(root, package, output, end=4200):
    """Construct the exact output-only delta without allocating any paths."""
    require(type(end) is int and 600 < end <= 4200, 'NATURAL_HORIZON')
    route = ET.parse(root/NATURAL/'demand.rou.xml').getroot()
    require(all(float(v.get('depart')) >= 600 for v in route.findall('vehicle') if v.get('id','').startswith('R_')),
            'UNSUPPORTED_PRECONTROL_R_REQUEST')
    tree = ET.parse(root/NATURAL/'scenario.sumocfg')
    for tag, value in [('net-file',root/NETWORK),('route-files',package/'demand.rou.xml'),('additional-files',package/'scenario.add.xml')]:
        tree.find('./input/'+tag).set('value',str(value))
    tree.find('./time/end').set('value',str(end))
    tree.find('./output/precision').set('value','8')
    for node in tree.findall('./output/*')+tree.findall('./report/*'):
        if node.get('value','').startswith('/'):
            node.set('value',str(output/Path(node.get('value')).name))
    ET.indent(tree);cfg=tree
    tree = ET.parse(root/NATURAL/'scenario.add.xml');r=tree.getroot()
    for node in r.iter():
        for key in ('file','dest'):
            if key in node.attrib:node.set(key,str(output/Path(node.get(key)).name))
    for period in PERIODS:
        p=parameters(period)
        logic=ET.SubElement(r,'tlLogic',dict(id='ramp_mid',type='static',programID=p['program'],offset='0'))
        for state,duration,nxt in p['phases']:
            ET.SubElement(logic,'phase',dict(state=state,duration=str(duration),next=str(nxt)))
    ET.indent(tree)
    return cfg,tree


def stage_package(root, package, output, end=4200):
    """Copy natural requests unchanged, preserving all original inputs."""
    cfg,additional=prepared_trees(root,package,output,end)
    package.mkdir(parents=True,exist_ok=False)
    shutil.copyfile(root/NATURAL/'demand.rou.xml',package/'demand.rou.xml')
    cfg.write(package/'scenario.sumocfg',encoding='utf-8',xml_declaration=True)
    additional.write(package/'scenario.add.xml',encoding='utf-8',xml_declaration=True)


def sources(root):
    previous=json.loads((root/LEGACY_CARD).read_text())['sources_sha256']
    require(all(sha(root/p)==h for p,h in previous.items()), 'HISTORICAL154_SOURCE_DRIFT')
    result=dict(previous)
    for folder in ('src/candidate_a_natural_service_20261015','tests/candidate_a_natural_service_20261015',
                   'tests/natural_qualification_preparation_20261015',
                   'tests/issue16_current_gap_scope_20261015_v1',
                   'scripts/candidate_a_natural_service_20261015_v1',
                   'scripts/natural_actuator_qualification_20261015_v1'):
        for p in (root/folder).glob('*.py'):result[str(p.relative_to(root))]=sha(p)
    require((root/READER).is_file(), 'INDEPENDENT_NATURAL_READER_NOT_READY')
    dependency_file=root/READER.parent/'dependencies.json'
    require(dependency_file.is_file(),'NATIVE_READER_DEPENDENCIES_NOT_READY')
    result[str(dependency_file.relative_to(root))]=sha(dependency_file)
    for name in json.loads(dependency_file.read_text())['paths']:
        p=Path(name)
        require(not p.is_absolute() and '..' not in p.parts and (root/p).is_file(),'INVALID_READER_DEPENDENCY')
        result[str(p)]=sha(root/p)
    result[str(USER)]=sha(root/USER)
    result[str(CURRENT_GAP_APPROVAL)]=sha(root/CURRENT_GAP_APPROVAL)
    return dict(sorted(result.items()))


def acceptance_sources(root):
    result=sources(root)
    for folder in ('scripts/actuator_acceptance_20261015_v1',):
        for path in (root/folder).glob('*.py'):result[str(path.relative_to(root))]=sha(path)
    for name in ('tests/test_actuator_acceptance_safety.py','tests/test_actuator_acceptance_accuracy.py',
                 'tests/test_actuator_acceptance_normalize.py',str(ACCEPTANCE_STANDARD),
                 'tests/test_actuator_acceptance_episode_reader.py',
                 'tests/fixtures/actuator_acceptance_episode_v1.json',
                 str(ACCEPTANCE_USER),
                 'artifacts/actuator_acceptance_20261015_v1/engineering/SOURCE_REVIEW.md'):
        require((root/name).is_file(),'ACCEPTANCE_SOURCE_NOT_READY:'+name)
        result[name]=sha(root/name)
    require((root/'scripts/actuator_acceptance_20261015_v1/normalize.py').is_file(),
            'ACCEPTANCE_NORMALIZER_NOT_READY')
    return dict(sorted(result.items()))


def prepare(root=ROOT, *, acceptance=False):
    root=Path(root).resolve();source=acceptance_sources(root) if acceptance else sources(root)
    bound_resources=acceptance_resource_scope(root) if acceptance else resource_scope(root)
    run=ACCEPTANCE_RUN if acceptance else RUN;task,_=paths_for_run(run)
    package=root/task/'packages_v1'/run;output=root/RAW/run/'outputs'
    require(not output.parent.exists(), 'ONE_USE_IDENTITY_CONSUMED')
    stage_package(root,package,output)
    if acceptance:write_new(package/'accuracy_registration.json',acceptance_registration(root))
    donor=json.loads((root/LEGACY_CARD).read_text())
    natural=json.loads((root/NATURAL/'card.json').read_text())
    card=dict(schema='NATURAL_QUALIFICATION_CARD_V1',status='PREPARED_NOT_RELEASED',SUMO_execution_authorized=False,
        classification='NATURAL_TECHNICAL_NOT_FORMAL',spec=acceptance_spec(root) if acceptance else spec(root),
        package=str(package.relative_to(root)),output=str(output.relative_to(root)),
        sources_sha256=source,common_runtime_source_sha256=hashlib.sha256(json.dumps(source,sort_keys=True,separators=(',',':')).encode()).hexdigest(),
        inherited_inputs_sha256={str(NATURAL/name):sha(root/NATURAL/name) for name in ('card.json','demand.rou.xml','scenario.add.xml','scenario.sumocfg')},
        prepared_input_sha256={str(p.relative_to(root)):sha(p) for p in package.iterdir() if p.is_file()},
        network_sha256=natural['network_sha256'],environment=donor['environment'],
        resources=({**resources(),'wall_limit_s':641} if acceptance else resources()),resources_status='PROPOSED_PENDING_EXACT_CARD_EXECUTION_APPROVAL',
        resources_scope=bound_resources,guardian=(dict(schema='NATURAL_QUALIFICATION_GUARDIAN_V1',
            inner_wall_limit_s=611,cleanup_reserve_s=30,outer_wall_limit_s=641,
            receipt=str(RAW/run/'guardian_receipt.json'),
            fallback_receipt=str(task/'runs'/run/'guardian_receipt.json')) if acceptance else guardian_spec()),
        numerical_exception_authority=dict(enabled=False),
        user_authorization=dict(path=str(ACCEPTANCE_USER if acceptance else USER),
            sha256=sha(root/(ACCEPTANCE_USER if acceptance else USER)),
            scope='IMPLEMENTATION_AND_NONEXECUTING_PREPARATION_ONLY_EXACT_START_PENDING'),
        audit_contract=dict(reader=str(READER),status='NEW_READER_REVIEW_REQUIRED'),
        observations=dict.fromkeys(('native_safety','C_raw','E_scheduled_nominal','E_executed_nominal','N_actual','cohort','urban','EOF')),
        qualification='NOT_TESTED_NOT_QUALIFIED',qualification_proposal=(acceptance_qualification_proposal()
            if acceptance else qualification_proposal()))
    write_new(package/'card.json',card)
    return package/'card.json'


def validate_prepared(card_path, root=ROOT):
    """Read-only validation never requires authority or allocates raw output."""
    root=Path(root).resolve();p=Path(card_path).resolve()
    acceptance=p==root/ACCEPTANCE_TASK/'packages_v1'/ACCEPTANCE_RUN/'card.json'
    run=ACCEPTANCE_RUN if acceptance else RUN;task,_=paths_for_run(run)
    require(p==root/task/'packages_v1'/run/'card.json', 'FOREIGN_NATURAL_CARD')
    c=json.loads(p.read_text());require(c['spec']==(acceptance_spec(root) if acceptance else spec(root)) and c['SUMO_execution_authorized'] is False,'NATURAL_SPEC_DRIFT')
    require(c['schema']=='NATURAL_QUALIFICATION_CARD_V1' and c['status']=='PREPARED_NOT_RELEASED','NATURAL_CARD_STATUS')
    require(c['package']==str(task/'packages_v1'/run) and c['output']==str(RAW/run/'outputs'),'NATURAL_OUTPUT_IDENTITY')
    require(not (root/RAW/run).exists(),'ONE_USE_IDENTITY_CONSUMED')
    require(c['resources']==({**resources(),'wall_limit_s':641} if acceptance else resources()),'NATURAL_RESOURCE_DRIFT')
    require(c['resources_status']=='PROPOSED_PENDING_EXACT_CARD_EXECUTION_APPROVAL' and c['resources_scope']==(acceptance_resource_scope(root) if acceptance else resource_scope(root)),'NATURAL_BUDGET_SCOPE_DRIFT')
    expected_guardian=dict(schema='NATURAL_QUALIFICATION_GUARDIAN_V1',inner_wall_limit_s=611,
        cleanup_reserve_s=30,outer_wall_limit_s=641,receipt=str(RAW/run/'guardian_receipt.json'),
        fallback_receipt=str(task/'runs'/run/'guardian_receipt.json')) if acceptance else guardian_spec()
    require(c['guardian']==expected_guardian,'NATURAL_GUARDIAN_DRIFT')
    require(c['qualification_proposal']==(acceptance_qualification_proposal() if acceptance else qualification_proposal()),'NATURAL_QUALIFICATION_PROPOSAL_DRIFT')
    require(c['sources_sha256']==(acceptance_sources(root) if acceptance else sources(root)),'NATURAL_SOURCE_DRIFT')
    require(c['common_runtime_source_sha256']==hashlib.sha256(json.dumps(c['sources_sha256'],sort_keys=True,separators=(',',':')).encode()).hexdigest(),'NATURAL_SOURCE_DIGEST_DRIFT')
    donor=json.loads((root/LEGACY_CARD).read_text())
    require(c['environment']==donor['environment'],'NATURAL_ENVIRONMENT_CLOSURE_DRIFT')
    require(set(c['inherited_inputs_sha256'])=={str(NATURAL/n) for n in ('card.json','demand.rou.xml','scenario.add.xml','scenario.sumocfg')},'INHERITED_INPUT_CLOSURE')
    for group in ('prepared_input_sha256','inherited_inputs_sha256'):
        require(all(sha(root/path)==h for path,h in c[group].items()),'NATURAL_INPUT_DRIFT')
    require(sha(root/NETWORK)==c['network_sha256'],'NATURAL_NETWORK_DRIFT')
    input_names=('scenario.sumocfg','scenario.add.xml','demand.rou.xml')+(
        ('accuracy_registration.json',) if acceptance else ())
    require(set(c['prepared_input_sha256'])=={str(task/'packages_v1'/run/n) for n in input_names},'PREPARED_INPUT_CLOSURE')
    if acceptance:
        require(json.loads((p.parent/'accuracy_registration.json').read_text())==acceptance_registration(root),
            'ACCEPTANCE_REGISTRATION_DRIFT')
    require(c['observations']==dict.fromkeys(('native_safety','C_raw','E_scheduled_nominal','E_executed_nominal','N_actual','cohort','urban','EOF')),'PREPARED_OBSERVATIONS_NOT_NULL')
    cfg=ET.parse(p.parent/'scenario.sumocfg')
    require(cfg.find('./time/end').get('value')=='4200' and cfg.find('./time/step-length').get('value')=='1' and cfg.find('./random_number/seed').get('value')=='17','NATURAL_TIME_OR_SEED_DRIFT')
    require(cfg.find('./output/precision').get('value')=='8','NATIVE_OUTPUT_PRECISION')
    require(sha(p.parent/'demand.rou.xml')==sha(root/NATURAL/'demand.rou.xml'),'NATURAL_REQUEST_COHORT_DRIFT')
    for expected,name in zip(prepared_trees(root,p.parent,root/c['output']),('scenario.sumocfg','scenario.add.xml')):
        require(ET.tostring(expected.getroot())==ET.tostring(ET.parse(p.parent/name).getroot()),'UNAPPROVED_PREPARATION_DELTA')
    require(c['audit_contract']==dict(reader=str(READER),status='NEW_READER_REVIEW_REQUIRED'),'NATURAL_READER_PATH_DRIFT')
    expected_user=ACCEPTANCE_USER if acceptance else USER
    require(c['user_authorization']==dict(path=str(expected_user),sha256=sha(root/expected_user),
        scope='IMPLEMENTATION_AND_NONEXECUTING_PREPARATION_ONLY_EXACT_START_PENDING'),'NATURAL_PREPARATION_AUTHORITY_DRIFT')
    require(c['numerical_exception_authority']==dict(enabled=False),'NATURAL_NUMERICAL_AUTHORITY_DRIFT')
    require(c['qualification']=='NOT_TESTED_NOT_QUALIFIED' and c['classification']=='NATURAL_TECHNICAL_NOT_FORMAL','NATURAL_QUALIFICATION_DRIFT')
    return c


def validate_release(card_path, release_path, root=ROOT, *, guardian_preflight=False):
    """Fail before worker/raw allocation unless current exact authority exists."""
    from src.candidate_a_natural_service_20261015 import budget,guardian
    root=Path(root).resolve();p=Path(card_path).resolve()
    c=validate_prepared(p,root)
    # Missing numeric approval is an explicit pending gate, not inferred from
    # the general goal, maximum starts, old remainder or proposed900s value.
    bound=budget.accounting(root)
    r=json.loads(Path(release_path).read_text())
    require(r['status']=='CANONICAL_NATURAL_EXECUTION_RELEASE' and r['card_sha256']==sha(p),'NATURAL_CANONICAL_RELEASE_MISMATCH')
    require(r['budget_approval_sha256']==bound['budget_approval_sha256'],'NATURAL_BUDGET_BINDING_MISMATCH')
    require(set(r['reviews'])=={'engineering','data','science'},'MISSING_NATURAL_REVIEWS')
    for item in r['reviews'].values():require(sha(root/item['path'])==item['sha256'],'NATURAL_REVIEW_DRIFT')
    user=ACCEPTANCE_USER if c['spec']['run_id']==ACCEPTANCE_RUN else USER
    require(r['user_authority']['path']==str(user) and r['user_authority']['sha256']==sha(root/user),'NATURAL_USER_SCOPE_DRIFT')
    approval=r['direct_execution_authority']
    require(sha(root/approval['path'])==approval['sha256'],'CURRENT_EXECUTION_AUTHORITY_DRIFT')
    a=json.loads((root/approval['path']).read_text())
    require(a['status']=='DIRECT_USER_APPROVED_EXACT_NATURAL_EXECUTION' and a['run_id']==c['spec']['run_id'] and a['card_sha256']==sha(p) and a['lifts_current_no_SUMO_restriction'] is True,'CURRENT_NO_SUMO_NOT_LIFTED')
    if c['spec']['run_id']==ACCEPTANCE_RUN:
        from src.candidate_a_natural_service_20261015.acceptance_safety import runtime_authority
        runtime_authority(c,p,r,root)
    require(c['environment']['python']=='.'.join(map(str,__import__('sys').version_info[:3])), 'PYTHON_ENVIRONMENT_DRIFT')
    require(all(sha(Path(path))==h for path,h in c['environment']['files_sha256'].items()),'NATIVE_ENVIRONMENT_FILE_DRIFT')
    if not guardian_preflight:guardian.require_worker_context(p,release_path,root)
    return c

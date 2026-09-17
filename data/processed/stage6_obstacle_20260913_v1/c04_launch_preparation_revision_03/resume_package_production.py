"""Offline package production; fake adapter only, existing archives read-only."""
from pathlib import Path
import importlib.util
import json
import os
import subprocess
import sys
from unittest.mock import patch
from src.scenarios import stage6_h2_offline as o
from src.scenarios import stage6_h2_execution as x
from src.analysis import stage6_h2_measurement as m
from src.analysis import stage6_h2_pipeline as pipeline

OUT=Path(__file__).resolve().parent
card=o.read_json(OUT/'proposed_launch_card.json')
x.validate_launch_card(OUT/'proposed_launch_card.json')
checks=[]
for entry in card['attempts']:
    checks.append({'attempt_id':entry['attempt_id'],'status':'prepared_not_started','materialization':entry['materialization'],'verification':o.verify_materialization(Path(entry['materialization']['path']),o.BATCH)})
assert x.Journal(OUT/'budget_journal').counters()['sumo']==0
assert o.read_json(OUT/'materialization_verification.json')=={'count':5,'results':checks,'actual_attempts':0,'actual_SUMO_starts':0}

spec=importlib.util.spec_from_file_location('stage6_C04_synthetic_fixture',o.ROOT/'tests/test_stage6_h2_c04.py')
fixture_module=importlib.util.module_from_spec(spec);spec.loader.exec_module(fixture_module)
fixture=OUT/'synthetic_fixture_evidence';fixture.mkdir()
fake_card=x.prepare_launch_card(fixture);journal=x.Journal(fixture/'budget_journal');clock=fixture_module.FakeClock();analyses=[]
names={'tripinfo.xml','fcd.xml','tls_states.xml'}|{f'{p}_l{i}.xml' for p in ('merge_upstream_e1','mainline_merge_entry_e1','merge_downstream_e1') for i in (0,1)}
with patch('subprocess.Popen',side_effect=AssertionError('Real process forbidden in offline production')):
    for index in range(3):
        if index==1:
            x.exclusive_json(journal.directory/'smoke_acceptance.json',{'accepted':True,'launch_payload_sha256':x.payload_sha(fake_card),'evidence_bindings':[o.bind(fixture/'proposed_launch_card.json')],'evidence_scope':'synthetic_fixture'})
        entry=fake_card['attempts'][index]
        receipt=x.execute_attempt(fixture/'proposed_launch_card.json',entry['attempt_id'],journal,fixture_module.FakeAdapter(),clock=clock,sleep=clock.sleep,allow_fixture=True)
        assert receipt['execution_status']=='completed' and receipt['evidence_scope']=='synthetic_fixture'
        if index:
            rp=Path(entry['materialization']['path']).parent/'execution_receipt.json'
            source={n:receipt['output_bindings'][n] for n in names};source['network.net.xml']=receipt['network']
            target=fixture/(entry['run_id']+'_analysis')
            m.analyze_to_new_directory(source,entry['run_id'],target,execution_receipt=o.bind(rp),allow_fixture=True)
            analyses.append(o.bind(target/'analysis_manifest.json'))
    pipeline.assemble_rule_tables(analyses,fixture/'registered_rule_tables',allow_fixture=True)

archive=o.ROOT/'artifacts/stage2_completion_20260909_v1/runtime_archive/ML17_attempt1'
source={n:o.bind(archive/'outputs'/n) for n in names};source['network.net.xml']=o.bind(archive/'network.net.xml')
archive_manifest=m.analyze_to_new_directory(source,'S6_V0_ML_S17',OUT/'historical_ML17_compatibility')
assert archive_manifest['status']=='qualified_offline_measurements'

# Only pinned Python interpreters run here; both analyses read the same old archive.
archive_script = r"""
import sys
from pathlib import Path
from src.scenarios import stage6_h2_offline as o
from src.analysis import stage6_h2_measurement as m
archive=o.ROOT/'artifacts/stage2_completion_20260909_v1/runtime_archive/ML17_attempt1'
names={'tripinfo.xml','fcd.xml','tls_states.xml'}|{f'{p}_l{i}.xml' for p in ('merge_upstream_e1','mainline_merge_entry_e1','merge_downstream_e1') for i in (0,1)}
source={n:o.bind(archive/'outputs'/n) for n in names};source['network.net.xml']=o.bind(archive/'network.net.xml')
m.analyze_to_new_directory(source,'S6_V0_ML_S17',Path(sys.argv[1]))
"""
archive_products=[]
for hashseed in ('17','91'):
    target=OUT/('historical_ML17_hashseed_'+hashseed)
    subprocess.run([sys.executable,'-B','-c',archive_script,str(target)],cwd=o.ROOT,env=dict(os.environ,PYTHONDONTWRITEBYTECODE='1',PYTHONHASHSEED=hashseed),check=True,capture_output=True,timeout=60)
    archive_products.append(target/'measurements.json')
assert archive_products[0].read_bytes()==archive_products[1].read_bytes()==(OUT/'historical_ML17_compatibility/measurements.json').read_bytes()
def keyed_records(data):
    if isinstance(data,dict):return {k:keyed_records(v) for k,v in data.items()}
    if isinstance(data,list):
        rows=[keyed_records(v) for v in data]
        return sorted(rows,key=lambda r:r['vehicle_id']) if rows and all(isinstance(r,dict) and 'vehicle_id' in r for r in rows) else rows
    return data
old_product=o.BATCH/'c04_launch_preparation_revision_02/historical_ML17_compatibility/measurements.json'
assert keyed_records(o.read_json(old_product))==o.read_json(archive_products[0])
x.exclusive_json(OUT/'determinism_verification.json',{'registered_ordering_key':'vehicle_id lexical order; original sample chronological order unchanged','synthetic_subprocess_cases':8,'hashseeds':[1,17,23,91],'input_orders':['set_order','reversed_set_order'],'actual_archive_distinct_runs':1,'actual_archive_analysis_invocations':3,'explicit_archive_hashseeds':[17,91],'archive_products':[o.bind(p) for p in archive_products],'byte_identical_across_current_archive_analyses':True,'prior_revision02_measurements':o.bind(old_product),'all_prior_scientific_values_unchanged_after_ID_record_order_normalization':True,'scope':'serialization determinism only; no new traffic evidence'})

files=[o.ROOT/name for name in ('src/scenarios/stage6_h2_offline.py','src/scenarios/stage6_h2_execution.py','src/analysis/stage6_h2_measurement.py','src/analysis/stage6_h2_pipeline.py','tests/test_stage6_h2_offline.py','tests/test_stage6_h2_measurement.py','tests/test_stage6_h2_c04.py','tests/test_stage6_h2_determinism.py')]
for source_file in files:
    with (OUT/(source_file.name+'.snapshot')).open('xb') as stream:stream.write(source_file.read_bytes())
capabilities={
 'executed_source_chain':'implemented; execution receipt and separate source map commit logical/attempt/version/condition/seed, approved launch payload, registration/materialization/source/config/network/binary/argv/output hashes and durable journal event; real evidence rejects fake receipts',
 'analysis_and_rules':'V1 receipt -> source identity -> FCD/tripinfo/TLS/6E1/2E2 qualification -> companion reports -> registered same-seed ML/C pair -> fixed352 main/14 sensitivity rows; missing and unpaired remain explicit',
 'executor':'disabled by default; explicitly enabled RealProcessAdapter still requires exact User-approved card and hash-bound approval evidence; Proposed card never launches',
 'watchdog':'monotonic real clock and50ms polling;120s deadline terminate, bounded1s wait then kill; archive2GB threshold; detected overruns retained and stop subsequent reservations. Polling/termination can overshoot limits and is not a hard OS quota guarantee.',
 'budget_recovery':'exclusive journal hash chain with replay, reservation before start, observed starts/unknown states separate, one shared same-parameter retry, duplicate/stale lock/unknown relaunch refused; prelaunch rejection and failed outputs preserved',
 'review_order':'one independent smoke attempt -> accepted smoke gate -> ML17+C17 matched unit -> accepted first-unit gate -> ML23+C23; smoke and smoke retry excluded from scientific source qualification',
 'schedule':'exact independently verified schedule artifact validation implemented; no such actual SUMO schedule artifact supplied or verified. Current inlet qualifier uses registered reported depart/departDelay fields; no absence-of-additional-blockage claim',
 'not_verified':['actual real process launch/signal delivery/OS crash behavior','new V1 runtime insertion/coverage and traffic outputs','exact SUMO1.26 number-flow schedule reconstruction','scientific obstacle resolution','independent C04 data/scientific review']}
x.exclusive_json(OUT/'capability_audit.json',capabilities)
coverage={
 'approval_and_hash':['test_card_five_precise_materializations_zero_starts_and_disabled_live','test_live_approval_must_bind_payload_and_fixture_gate_cannot_pass_real','test_receipt_role_seed_condition_hash_and_status_tampering'],
 'persistent_budget':['test_journal_replay_detects_state_tamper_and_budget_reserves','test_persistent_stale_lock_and_alternate_journal_block','test_unique_same_parameter_retry_and_smoke_exclusion','test_archive_overrun_is_retained_and_blocks_retry'],
 'process_failures':['test_timeout_kill_and_failed_output_are_retained','test_crash_after_start_stops_fake_process_and_keeps_unknown','test_start_crash_stays_charged_unknown_and_cannot_resume','test_nonzero_and_signal_are_not_scientific_negatives','test_missing_output_and_warning_are_technical_failures','test_warning_fallback_is_preserved'],
 'full_source_rule_chain':['test_review_pause_and_source_identity_chain','test_auxiliary_E2_empty_or_wrong_period_is_not_coverage','test_exact_schedule_requires_independent_provenance'],
 'inherited12_failure_groups':'new final run includes both original Stage6 dedicated test modules;28 methods retained including typed source identity, registered E1 period, raw internal-stopped fixture,2699/2700 censor, unpaired union and six-state schema'}
x.exclusive_json(OUT/'failure_mode_coverage.json',coverage)
receipt={'scope':'C04/SG6-P offline preparation; independent review pending','engineering_self_review':'PASS_offline_only','launch_eligible':False,'user_launch_approval':None,'registration':o.bind(o.CARD),'Proposed_launch_card':o.bind(OUT/'proposed_launch_card.json'),'launch_payload_sha256':x.payload_sha(card),'files':[o.bind(p) for p in files],'test_receipt':o.bind(OUT/'test_receipt.json'),'test_log':o.bind(OUT/'offline_tests_final.log'),'materializations':o.bind(OUT/'materialization_verification.json'),'real_budget_counters':x.Journal(OUT/'budget_journal').counters(),'persistent_fixture_evidence':{'scope':'synthetic_fixture_only','fake_attempts':3,'physical_simulator_runs':0,'analysis_manifests':analyses,'rule_manifest':o.bind(fixture/'registered_rule_tables/rule_manifest.json')},'archive_compatibility':{'distinct_physical_archive':1,'offline_analysis_invocations_this_package':3,'analysis_manifest':o.bind(OUT/'historical_ML17_compatibility/analysis_manifest.json')},'capability_audit':o.bind(OUT/'capability_audit.json'),'coverage':o.bind(OUT/'failure_mode_coverage.json'),'simulation_invocations':{'SUMO':0,'netconvert':0,'TraCI':0,'GUI':0},'compiled_files_created':0,'preserved_development_failures':[o.bind(o.BATCH/'c04_launch_preparation_revision_01/development_test_failure_01.json'),o.bind(o.BATCH/'c04_launch_preparation_revision_01/development_test_failure_02.json')],'no_historical_config_raw_result_or_docs_modified':True}
receipt['supersedes']=o.bind(o.BATCH/'c04_launch_preparation_revision_02/engineering_receipt.json')
receipt['revision_reason']='Canonical vehicle_id ordering for cohort records, feeder raw speed arrays and descriptive ID records; preserve scientific values and previous XML repair; rebind all five materializations and Proposed card.'
receipt['package_producer_development_failure']=o.bind(OUT/'package_producer_development_failure.json')
receipt['inherited_XML_negative_cases']=53
receipt['required_XML_roles']=14
receipt['determinism_verification']=o.bind(OUT/'determinism_verification.json')
x.exclusive_json(OUT/'engineering_receipt.json',receipt)
x.exclusive_json(OUT/'package_manifest.json',{'engineering_receipt':o.bind(OUT/'engineering_receipt.json'),'registration':o.bind(o.CARD),'C03_spatial_acceptance':card['C03_spatial_acceptance'],'script':o.bind(Path(__file__)),'files':[o.bind(p) for p in sorted(OUT.rglob('*')) if p.is_file()],'launch_eligible':False,'scope':'offline preparation, synthetic fixtures explicitly separated from five proposed real attempts'})
print(json.dumps({'engineering_receipt':o.bind(OUT/'engineering_receipt.json'),'package_manifest':o.bind(OUT/'package_manifest.json'),'Proposed_launch_card':o.bind(OUT/'proposed_launch_card.json'),'launch_payload_sha256':x.payload_sha(card)},indent=2))

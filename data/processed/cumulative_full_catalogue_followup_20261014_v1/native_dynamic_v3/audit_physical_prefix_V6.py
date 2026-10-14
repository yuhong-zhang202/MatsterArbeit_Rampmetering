"""Recover physical-prefix calculations; missing raw ACK records stay UNKNOWN.

Uses corrected analysis-only V3, never alters raw, production or bound reader.
Derived application facts are explicitly separated from raw ledger ACK events.
"""
import pathlib,sys,json,importlib.util,copy,xml.etree.ElementTree as ET,hashlib
ROOT=pathlib.Path(__file__).resolve().parents[4];sys.path.insert(0,str(ROOT))
OUT=ROOT/'data/processed/cumulative_full_catalogue_followup_20261014_v1/native_dynamic_v3'
RAW=ROOT/'data/raw/cumulative_full_catalogue_followup_20261014_v1/UA_CUMULATIVE_FULL_DYNAMIC_S17_01/outputs'
ENG=ROOT/'artifacts/cumulative_full_catalogue_followup_20261014_v1/engineering/native_execution_v2/UA_CUMULATIVE_FULL_DYNAMIC_S17_01'
CARD=ROOT/'artifacts/cumulative_full_catalogue_followup_20261014_v1/engineering/packages_v2/UA_CUMULATIVE_FULL_DYNAMIC_S17_01/card.json'
source=ROOT/'data/processed/cumulative_full_catalogue_followup_20261014_v1/native_dynamic_v2/audit_actual_V3.py'
spec=importlib.util.spec_from_file_location('corrected_analysis_V3',source);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
from scripts.cumulative_full_catalogue_audit_20261014_v1.core import catalogue
pre=m.lines(RAW/'pre_steps.jsonl');ack=m.lines(RAW/'step_ack.jsonl')
tls=[e.attrib.copy() for e in ET.parse(RAW/'tls_states.xml').getroot() if e.attrib.get('id')=='ramp_mid']
from scripts.cumulative_full_catalogue_audit_20261014_v1 import evidence as original_evidence
import types
yss=importlib.util.spec_from_file_location('current_Y5_formula',OUT/'current_Y5_formula_V5.py');ys=importlib.util.module_from_spec(yss);yss.loader.exec_module(ys)
private_globals=dict(original_evidence.yellow_coverage.__globals__);private_globals['yellow_record']=ys.current_yellow_record
m.yellow_coverage=types.FunctionType(original_evidence.yellow_coverage.__code__,private_globals,'bounded_current_yellow_coverage')
executed_card=json.loads(CARD.read_text());frozen_manifest=json.loads((ENG/'RAW_FINAL_SHA256_V2.json').read_text());historical_bindings={};live_drift=[];base_sha=m.sha
for key in ('sources_sha256','inherited_inputs_sha256','prepared_input_sha256'):
    for name,h in executed_card[key].items():
        snapshot=RAW/'snapshots'/name;rel=str(snapshot.relative_to(ROOT));m.need(snapshot.is_file() and rel in frozen_manifest['files'] and base_sha(snapshot)==h and frozen_manifest['files'][rel]['sha256']==h,'IMMUTABLE_EXECUTED_SNAPSHOT_BINDING:'+name)
        historical_bindings[ROOT/name]=snapshot
        if base_sha(ROOT/name)!=h:live_drift.append({'path':name,'executed_snapshot_sha256':h,'current_unexecuted_sha256':base_sha(ROOT/name)})
def historical_sha(path):
    return base_sha(historical_bindings.get(pathlib.Path(path),pathlib.Path(path)))
m.sha=historical_sha
original=m.audit_accounting;derived=[]
def accounting_with_physical_binding(rows,events,entries,end):
    ev=copy.deepcopy(events);packets={q['application_global_s'] for q in ev if q['event']=='PACKET_ACK_OBSERVED'};requests={q['request_id']:q for q in ev if q['event']=='REQUESTED'};request_ack={q['request_id'] for q in ev if q['event']=='ACK_OBSERVED'}
    for q in [q for q in events if q['event']=='BOUNDARY_PACKET_SELECTED_NOT_APPLIED']:
        t=q['time_s']
        if t in packets or t+1>end:continue
        row=next(r for r in rows if r['time_begin_s']==t);P=catalogue(q['chosen_period_s']);rid=row['rate_chain']['applied_request_id'];req=requests[rid]
        m.need(row['time_end_s']==t+1 and row['motion']=='G' and rid==row['rate_chain']['pending_request_id'],'DERIVED_FIRST_G_REQUEST_ID_TIME')
        x=[x for x in tls if float(x['time'])==t];m.need(len(x)==1 and x[0]['state']=='G' and x[0]['phase']=='0' and x[0]['programID']==P['program'],'DERIVED_NATIVE_TLS_IDENTITY')
        aa=[a for a in ack if a['requested_target_s']==t+1];m.need(len(aa)==2 and aa[0]['ACK_received'] is True and aa[0]['actual_time_verified'] is False and aa[1]['ACK_received'] is True and aa[1]['actual_time_verified'] is True and aa[1]['actual_readback_s']==t+1,'DERIVED_TWO_STAGE_ACTUAL_ACK')
        b=pre[t]['bound_snapshot'];a=row['post_signal_application_binding'];po=row['phase_observation'];m.need(b['program']==P['program'] and a['status']=='BOUND_BEFORE_LEDGER' and a['ACK_s']==t+1 and a['actual_program']==P['program'] and type(a['actual_phase']) is int and a['actual_phase']==0 and a['actual_state']=='G' and a['actual_controlled_links']==[[['ramp_storage_0','ramp_accel_0',':ramp_mid_0_0']]] and po['state_after']=='G' and po['phase_after']==0 and po['next_switch_after_s']==t+P['max_green_s'],'DERIVED_POST_SIGNAL_PROGRAM_LINK_AND_CLOCK')
        record={'event':'PACKET_ACK_OBSERVED','request_id':rid,'application_global_s':t,'first_green_ACK_s':t+1,'period_s':P['period_s'],'max_green_s':P['max_green_s'],'yellow_s':P['yellow_s'],'applied_command_veh_h':7200/P['period_s'],'evidence_origin':'DERIVED_PHYSICAL_BINDING_NOT_RAW_COMMAND_ACK'};ev.append(record)
        if rid not in request_ack:
            ev.append({'event':'ACK_OBSERVED','request_id':rid,'application_global_s':t,'first_green_ACK_s':t+1,'application_delay_s':t-req['global_request_s'],'evidence_origin':'DERIVED_PHYSICAL_BINDING_NOT_RAW_COMMAND_ACK'})
        derived.append({'request_id':rid,'cycle_begin_s':t,'first_G_ACK_s':t+1,'raw_PACKET_ACK_present':False,'raw_request_ACK_present':rid in request_ack,'classification':'DERIVED_PHYSICAL_BINDING_ONLY_RAW_COMMAND_ACK_UNKNOWN','actual_TLS':x[0],'two_actual_ACKs':aa,'post_signal_binding':a,'post_clock':po,'request':req,'physical_packet':P})
    return original(rows,ev,entries,end)
m.audit_accounting=accounting_with_physical_binding
try:
    result=m.audit(ENG/'RAW_FINAL_SHA256_V2.json',CARD)
    result['original_corrected_pipeline_status']=result['status'];result['status']='UNKNOWN_RAW_COMMAND_ACK_COVERAGE_WITH_OBSERVED_PHYSICAL_PREFIX_AND_STOP'
    result['missing_or_unknown'].append({'kind':'RAW_COMMAND_APPLICATION_ACK_EVENTS_NOT_DURABLY_FLUSHED','derived_physical_bindings':derived,'full_raw_command_event_chain_PASS':False})
    result['derived_physical_bindings']=derived;result['planned_run_end_s']=1296;result['planned_run_end_observed']=result['last_ACK']==1296;result['physical_accounting_support']='OBSERVED_ACK_PREFIX_NOT_COMPLETE1296';result['original_bound_reader_PASS']=False;result['historical_snapshot_count']=len(historical_bindings);result['source136_historical_snapshot_binding']='PASS_ALL136_SOURCES_AND6_INPUTS_IMMUTABLE_RAW_MANIFEST';result['current_tree_drift_due_authorized_unexecuted_repair']=live_drift;result['current_source_and_environment_hashes_checked']='EXECUTED_SOURCE_INPUTS_FROM_IMMUTABLE_SNAPSHOTS_CURRENT_ENV_HASHES_SEPARATE';result['current_Y5_formula_results']=ys.CHECKED;result['original_Y5_schema_defect']='YELLOW_PERIOD old whitelist omitted legalT24Y5; separate existing-state formula check, not vehicle uncertainty'
except Exception as exc:
    import traceback
    result={'status':'UNKNOWN_PREFIX_COLLECTOR_EXCEPTION','reason':str(exc),'traceback':traceback.format_exc(),'derived_physical_bindings':derived,'native_safety_proven':False,'rate_qualified':False}
with (OUT/'PHYSICAL_PREFIX_RESULTS_V6.json').open('x') as f:json.dump(result,f,indent=2);f.write('\n')
print(json.dumps({k:result.get(k) for k in ('status','reason','last_ACK','last_accounted','runtime_error')},indent=2))
raise SystemExit(1)  # Missing raw event records and true STOP never become PASS.

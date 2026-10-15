"""Versioned numerical-event supplement; keep original actual audit and alarms."""
from pathlib import Path
import argparse,gzip,json,sys,traceback,xml.etree.ElementTree as ET
ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(ROOT))
from scripts.unified_alinea_audit_20261013_v1 import actual
from scripts.unified_alinea_audit_20261013_v1.numeric_event_audit import validate_formula
from scripts.unified_alinea_audit_20261013_v1.core import need,near

def audit(manifest,card_path):
    base=actual.audit(manifest,card_path);card=actual.read(card_path);raw=ROOT/card['output'];authority=dict(card['numerical_exception_authority'],execution_card_sha256=actual.sha(Path(card_path)))
    approval=ROOT/authority['approval_path'];need(actual.sha(approval)==authority['approval_sha256'] and actual.read(approval)['answer']=='批准受限数值例外并继续','NUMERICAL_APPROVAL_BYTES')
    need(actual.sha(ROOT/authority['source_reference_path'])==authority['source_reference_sha256'],'NUMERICAL_SOURCE_REFERENCE_BYTES')
    pre=actual.lines(raw/'pre_steps.jsonl');post=actual.flatten(actual.lines(raw/'post_steps.jsonl'));candidates=[]
    for row in post:
        for record in row.get('numeric_stop_classifications',[]):
            if record.get('decision')=='CONTINUE_RESTRICTED_NUMERICAL_EVENT':candidates.append((row,record))
    needed={row['time_begin_s'] for row,_ in candidates};frames={}
    if needed:
        with gzip.open(raw/'fcd.xml.gz','rb') as stream:
            for _,elem in ET.iterparse(stream,events=('end',)):
                if elem.tag!='timestep':continue
                t=float(elem.get('time'))
                if t in needed:frames[int(t)]={v.get('id'):v.attrib for v in elem}
                elem.clear()
    approved=[];seen=set();extra_alarms=[]
    for row,record in candidates:
        e=record['evidence'];vid=e['vehicle_id'];t=row['time_begin_s'];key=(vid,t);need(key not in seen,'DUPLICATE_NUMERIC_EVENT');seen.add(key)
        p=pre[t]['bound_snapshot'];need(e['before']==p['numeric_stop_before'][vid],'NUMERICAL_BEFORE_FRESH_RECORD_JOIN')
        need(e['time_begin_s']==t and e['time_end_s']==row['time_end_s'] and e['recorded_delta_v_m_s2']==row['braking_observation']['speed_difference_m_s2'][vid] and e['actual_native_acceleration_m_s2']==row['braking_observation']['actual_acceleration_m_s2'][vid],'NUMERICAL_ACTUAL_BRACKET_VALUES')
        need(vid in p['world'] and vid in row['post_world'] and near(e['before']['speed_m_s'],p['world'][vid]['speed_m_s']) and near(e['after']['speed_m_s'],row['post_world'][vid]['speed_m_s']),'NUMERICAL_WORLD_JOIN')
        meta=p['terminal_before'][vid];need(near(e['before']['position_m'],meta['position_m']) and e['before']['type_id']==meta['type_id'] and e['before']['route']==meta['route'],'NUMERICAL_POSITION_TYPE_ROUTE_JOIN')
        f=frames[t][vid];need(e['after']['lane_id']==f['lane'] and abs(e['after']['position_m']-float(f['pos']))<=.51e-8 and abs(e['after']['speed_m_s']-float(f['speed']))<=.51e-8,'NUMERICAL_INDEPENDENT_AFTER_FCD_JOIN')
        cycle=next(c for c in base['phase_audit']['cycles'] if c['begin_s']<=t<c['end_s']);need(cycle['green_end_s']==t and e['expected_program']==f"I12_PACKET{cycle['period_s']}" and row['motion']=='y','NUMERICAL_DERIVED_FIRST_YELLOW')
        sb=row['post_signal_application_binding'];need(e['actual_phase']==sb['actual_phase'] and e['actual_state']==sb['actual_state'] and e['actual_program']==sb['actual_program'] and e['controlled_links']==sb['actual_controlled_links'],'NUMERICAL_ACTUAL_SIGNAL_JOIN')
        need(vid not in {q['vehicle_id'] for q in row['actual_crossings']} and 'body_observation' in row and 'body_observation_error' not in row,'NUMERICAL_BODY_ENTRY_JOIN')
        need(e['native_event_counters']==row['native_event_counters'] and e['native_warning_observed']==any(x in row['warning_observation']['text'].lower() for x in ('emergency braking','emergency stop','collision','teleport')),'NUMERICAL_NATIVE_COUNTER_WARNING_JOIN')
        before=p['entry_following_before'][vid];after=e['following_after'];need(before['status']==e['before_current_gap_status'] and after['status']==e['after_current_gap_status'],'NUMERICAL_CURRENT_GAP_STATUS_JOIN')
        actual.following(before,vid,t,p['world'],p['terminal_before'],extra_alarms);actual.following(after,vid,t+1,row['post_world'],{},extra_alarms)
        checked=validate_formula(e,authority)
        need(record['native_safety_proven'] is False and record['source_reference']['private_offset_observed'] is False and near(record['source_reference']['predicted_speed_m_s'],checked['independent_reference_speed_m_s']),'NUMERICAL_REFERENCE_AND_LIMITS_RETENTION')
        need(record['classification']=='SOURCE_COMPATIBLE_NUMERICAL_STOP_EVENT' and record['legacy_strict_FAIL_retained'] is True and record['actual_branch_identified'] is False and record['approval_sha256']==authority['approval_sha256'] and near(record['observed_delta_v_m_s2'],checked['actual_delta_v_m_s2']) and near(record['observed_native_acceleration_m_s2'],checked['actual_native_acceleration_m_s2']),'NUMERICAL_CLASSIFICATION_RAW_RETENTION')
        need({'ORDINARY_BRAKING_EXCEEDED:'+vid,'UNKNOWN_OR_EXCESSIVE_ACCELERATION:'+vid}<=set(row['legacy_braking_reasons']),'LEGACY_STRICT_FAIL_NOT_RETAINED')
        approved.append(checked)
    covered={(q['vehicle_id'],q['ACK']) for q in approved};active=[a for a in base['observed_alarms'] if not(a['kind'] in ('NORMAL_BRAKING_BOUND','NORMAL_ACCELERATION_BOUND') and (a['vehicle_id'],a['ACK_s']) in covered)]
    base['approved_numerical_event_audit']={'status':'PASS_OBSERVED_APPROVED_CLASSIFICATION_ONLY','events':approved,'approval_sha256':authority['approval_sha256'],'legacy_observed_alarms_retained':base['observed_alarms'],'active_unexempted_alarms':active+extra_alarms,'native_safety_proven':False,'private_branch_observed':False}
    return base

def main():
    p=argparse.ArgumentParser();p.add_argument('--manifest',required=True);p.add_argument('--card',required=True);p.add_argument('--output',required=True);a=p.parse_args();out=Path(a.output).resolve();actual.need(out.is_relative_to(ROOT/'data/processed/unified_alinea_actuator_20261013_v1') and not out.exists(),'NEW_APPROVED_PROCESSED_PATH_ONLY');out.mkdir(parents=True)
    try:r=audit(a.manifest,a.card)
    except Exception as exc:r={'status':'UNKNOWN_NUMERICAL_EVENT_AUDIT','reason':str(exc),'traceback':traceback.format_exc(),'native_safety_proven':False,'rate_qualified':False}
    with (out/'ACTUAL_NUMERIC_RESULTS_V2.json').open('x') as f:json.dump(r,f,indent=2)
    print(json.dumps({k:v for k,v in r.items() if k in ('status','run_id','last_ACK','runtime_status','reason')},indent=2));return 0 if r['status']=='PASS_OBSERVED_DATA_INTEGRITY_ONLY' else 1
if __name__=='__main__':raise SystemExit(main())

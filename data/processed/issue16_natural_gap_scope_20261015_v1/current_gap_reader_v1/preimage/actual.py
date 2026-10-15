"""Independent native natural-actuator audit. Never starts a simulator.

Full world/FCD/identity data are joined one interval at a time. The preserved
synthetic reader supplies pure arithmetic over a small native projection; its
synthetic loader and labels are never used as native provenance or safety.
"""
from pathlib import Path
import argparse,json,sys,traceback,xml.etree.ElementTree as ET
ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(ROOT));sys.dont_write_bytecode=True
from scripts.natural_service_audit_20261015_v1.actual import audit as arithmetic,need,near,feedback_check
from scripts.natural_actuator_qualification_20261015_v1 import provenance,streaming,measurements,phases,yellow
from scripts.cumulative_full_catalogue_audit_20261014_v1.evidence import checkpoint


def lines(path,optional=False):return list(streaming.jsonl(path,optional))
def records(path,tag):return [dict(e.attrib) for e in ET.parse(path).getroot().findall(tag)]


def accounting_view(receipt,files):
    """Explicit native schema normalization; no synthetic classification."""
    common={k:receipt[k] for k in ('last_completed_s','last_accounted_s','error','cycles','command_records')}
    common['accounting']=receipt['control_accounting']
    return dict(receipt=common,files=files)


def phase_and_yellow(raw,receipt,scan,card):
    last=receipt['last_accounted_s'];cycles=receipt['cycles'];pre=scan['pre'];post=scan['post'];tls={t:q for (t,n),q in scan['tls'].items() if n=='ramp_mid'}
    result=phases.audit(pre,post,cycles,tls,lines(raw/'policy_duration_requests.jsonl',True),last)
    expected=set()
    for c in result['cycles']:
        if 'y' in c['motions']:expected.add(c['begin_s']+c['motions'].index('y'))
    screens=lines(raw/'yellow_scope.jsonl',True);by={q['time_s']:q for q in screens};need(len(by)==len(screens),'DUPLICATE_YELLOW_SCREEN')
    need(expected<=set(by),'MISSING_OBSERVED_YELLOW_SCREEN')
    extras=set(by)-expected
    need(not extras or bool(receipt['error']) and extras=={receipt['last_completed_s']} and scan['extra_pre_count']==1,'UNBOUND_UNOBSERVED_YELLOW')
    # Re-stream only required tiny before/after frames for yellow checks;
    # no full-world accumulation and no shifted clocks.
    pending_pre=iter(streaming.jsonl(raw/'pre_steps.jsonl'));p=next(pending_pre,None)
    checked=set()
    for r in streaming.posts(raw/'post_steps.jsonl'):
        t=r['time_end_s']
        if t not in by:continue
        while p is not None and p['time_s']<t:p=next(pending_pre,None)
        need(p is not None and p['time_s']==t,'YELLOW_PRE_FRAME_MISSING')
        before=p['bound_snapshot'];q=by[t]
        need(before['motion']=='y','YELLOW_FRESH_FRAME')
        need(q['screen_stage']=='PREPARED_BEFORE_FIRST_Y_MOTION' and q['source_program']==before['program'],'YELLOW_SOURCE_PROGRAM')
        yellow.yellow_record(q,cycles,r['post_world'],before['terminal_before'],receipt['last_completed_s'],card['spec']['yellow_responsibility_contract']);checked.add(t)
    need(checked==set(by),'YELLOW_AFTER_FRAME_MISSING')
    result['yellow']=dict(observed_first_Y=len(expected),prepared_unobserved=sorted(extras),status='PASS_OBSERVED_YELLOW_EVIDENCE' if expected else 'NOT_TESTED_NO_OBSERVED_YELLOW')
    return result


def setter_journal(raw,last,receipt):
    rows=lines(raw/'control_setters.jsonl');need(rows,'MISSING_DURABLE_CONTROL_SETTERS');groups={}
    for r in rows:groups.setdefault(r['setter_id'],[]).append(r)
    failures=[]
    for key,group in groups.items():
        need(group[0]['status']=='ATTEMPTED' and group[0]['call_completed'] is False,'SETTER_NO_ATTEMPT')
        final=group[-1];need(all(r['time_s']<=last for r in group),'FUTURE_SETTER')
        statuses=[r['status'] for r in group]
        if final['status']=='READBACK_OBSERVED':
            need(statuses==['ATTEMPTED','CALL_RETURNED','READBACK_OBSERVED'] and final['call_completed'] is True,'SETTER_RETURN_SEQUENCE')
            fields=final['actual_signal']['fields']
            need(all(fields[k]['status']=='OBSERVED' and fields[k]['value']==v for k,v in final['expected_readback'].items()),'SETTER_READBACK_MISMATCH')
        else:
            need(bool(receipt['error']) and final==receipt['last_control_setter'] and final['time_s']==last,'UNBOUND_FAILED_SETTER')
            need(final['status'] in ('CALL_FAILED_STOP','READBACK_UNKNOWN_STOP','READBACK_MISMATCH_STOP'),'UNKNOWN_SETTER_FAILURE')
            failures.append(final)
        for field in final.get('actual_signal',{}).get('fields',{}).values():
            need(field['status']=='OBSERVED' and field['value'] is not None or field['status']=='UNKNOWN' and field['value'] is None and field['error'],'SETTER_UNKNOWN_VALUE_FABRICATED')
    if not receipt['error']:need(all(r['time_s']<last for r in rows),'TERMINAL_SETTER_WITHOUT_MOTION')
    return dict(status='STOP_DURABLE_SETTER_FAILURE_RETAINED' if failures else 'PASS_DURABLE_SETTER_EVIDENCE',attempts=len(groups),failures=failures,getters_are_movement_ACK=False)


def feedback_prefix(events,requests,receipt,terminal_row):
    last=receipt['last_completed_s'];steps=[e for e in events if e['event']=='E1_POST_ACK_EVENTS']
    terminal_missing=not any(e['global_s']==last for e in steps) and last>600
    if terminal_missing:provenance.gap_stop(receipt,terminal_row)
    observed_end=last-1 if terminal_missing else last
    windows=feedback_check(events,observed_end,requests)
    return dict(status='PASS_OBSERVED_COMPLETE_FEEDBACK_WINDOWS',windows=windows,events_observed_through_s=observed_end,
                terminal_ACK_feedback_status='NOT_OBSERVED_AFTER_RETAINED_STOP' if terminal_missing else 'OBSERVED',unobserved_event_not_synthesized=True)


def endpoint_records(frame):
    need(all(v.get('id')==vid for vid,v in frame.items()),'ENDPOINT_ID_BINDING')
    return [dict(v,id=vid) for vid,v in frame.items()]


def audit(manifest_path,card_path,root=ROOT,postanalysis_reader_v1=False):
    root=Path(root).resolve();result=dict(classification='NATIVE_TECHNICAL_DIAGNOSTIC_NOT_FORMAL',qualified=False,service_qualification='NOT_ASSESSED_REQUIRES_SCIENTIFIC_REVIEW',domains={},missing_or_unknown=[],observed_alarms=[])
    def run(name,fn):
        try:
            value=fn();result['domains'][name]=value;return value
        except Exception as exc:
            value=dict(status='UNKNOWN_INCOMPLETE_EVIDENCE',reason=type(exc).__name__+':'+str(exc))
            result['domains'][name]=value;result['missing_or_unknown'].append(dict(domain=name,**value));return None
    paths=[str(p.relative_to(ROOT)) for p in Path(__file__).parent.glob('*.py')]+['scripts/natural_actuator_qualification_20261015_v1/dependencies.json']
    paths+=provenance.read(Path(__file__).parent/'dependencies.json')['paths']
    result['reader_version']=dict(mode='EXPLICIT_POSTANALYSIS_READER_V1' if postanalysis_reader_v1 else 'EXACT_CURRENT_CARD_SOURCES',current_source_closure_sha256={p:provenance.sha(ROOT/p) for p in sorted(set(paths))},historical_frozen_reader_verdict_not_rewritten=True)
    guard=run('provenance',lambda:provenance.verify(manifest_path,card_path,root,postanalysis_reader_v1))
    if guard is None:result['status']='UNKNOWN_NATIVE_PROVENANCE';return result
    card,receipt,raw,package,network,proof=guard;result['domains']['provenance']=proof;result['run_id']=receipt['run_id'];last=receipt['last_completed_s']
    result['native_terminal_evidence']={k:receipt.get(k) for k in ('status','error','last_completed_s','last_accounted_s','last_step_ack','last_control_setter','command_records','partial_final_cycle','body_censored_ids')}
    result['native_terminal_evidence']['last_selected_cycle']=receipt.get('cycles',[])[-1:]
    if (raw/'failure_snapshot.json').exists():result['native_terminal_evidence']['failure_snapshot']=provenance.read(raw/'failure_snapshot.json')
    trips=run('trip_schema',lambda:records(raw/'tripinfo.xml','tripinfo'))
    scan=run('native_stream_joins',lambda:streaming.scan(raw,receipt,network,trips)) if trips is not None else None
    if trips is not None:result['domains']['trip_schema']=dict(status='PASS_XML_SCHEMA',records=len(trips))
    if scan is not None:
        files={name:lines(raw/name,True) for name in ('command_events.jsonl','feedback_events.jsonl','admission.jsonl','policy_phase_requests.jsonl','policy_duration_requests.jsonl')}
        files.update({'pre_steps.jsonl':scan['pre'],'post_steps.jsonl':scan['post'],'step_ack.jsonl':scan['acks']})
        # A failed pre-motion tail remains in native files and is not presented
        # as observed execution. The narrow arithmetic reader may reject this
        # legitimate tail; retain UNKNOWN for that domain, never synthesize it.
        math=run('accounting',lambda:arithmetic(accounting_view(receipt,files)))
        if math is not None:
            result['domains']['accounting']={k:v for k,v in math.items() if k not in ('native_EOF','native_safety','lifecycle_4050','urban_exposure','service_qualification','observed_stop')}
            result['domains']['accounting']['status']='PASS_INDEPENDENT_NATIVE_ACCOUNTING'
            result['domains']['accounting']['native_terminal_state']='STOP_PREFIX' if receipt['error'] else 'OBSERVED_NATIVE_END'
        run('feedback_native_XML',lambda:measurements.feedback_xml(raw,files['feedback_events.jsonl'],last))
        run('feedback_event_accounting',lambda:feedback_prefix(files['feedback_events.jsonl'],[e for e in files['command_events.jsonl'] if e['event']=='REQUESTED'],receipt,scan['post'][-1]))
        run('phases_yellow',lambda:phase_and_yellow(raw,receipt,scan,card))
        run('native_queue_export',lambda:measurements.queue_xml(raw/'queues.xml',last))
        result['domains']['queue_rear_extent']=dict(status='PASS_NAMED_LANE_OBSERVATIONS' if not any(q['missing_length_ids'] for q in scan['queue_rows']) else 'UNKNOWN_MISSING_BODY_LENGTH',rows=scan['queue_rows'])
        result['endpoint_vehicles']=endpoint_records(scan['endpoint'])
        run('setters',lambda:setter_journal(raw,last,receipt))
        result['domains']['six_windows']=measurements.windows(scan['post'],last)
        cohort=run('cohort',lambda:measurements.cohort(package/'demand.rou.xml',trips,scan['observed'],last,records(raw/'sumo_summary.xml','step'),scan['endpoint']))
        if cohort is not None and cohort['missing_due_ids']:result['missing_or_unknown'].append(dict(domain='cohort',missing_due_ids=cohort['missing_due_ids']))
        result['domains']['constraints']=dict(status='OBSERVED_ONLY_NO_CAUSAL_ALLOCATION',WAIT_branch_status='OBSERVED' if scan['constraints'].get('WAIT_observations',0) else 'NOT_TESTED_NO_OBSERVED_WAIT',**scan['constraints'])
        result['domains']['urban']=dict(status='PASS_OBSERVED_DESCRIPTIVE_EXPOSURE' if last>=3000 else 'UNKNOWN_EVALUATION_NOT_COMPLETE',counts=scan['urban_counts'],U_context=scan['urban_contexts'],scope='Legacy1.389m/s descriptive exposure; not contiguous queue or causal delay')
        result['observed_alarms'].extend(scan['alarms']);result['missing_or_unknown'].extend(scan['missing'])
        result['domains']['native_stream_joins']=dict(status='PASS_JOIN_INTEGRITY',independent_physical_N=len(scan['entries']),entries=scan['entries'],body_rows_checked=scan['body_rows'],populations_checked=scan['populations'],arrivals_checked=len(scan['arrivals']),identity_scope=scan['identity_scope'],body_censored_ids=receipt['body_censored_ids'],partial_final_cycle=receipt.get('partial_final_cycle'),censor_scope='No clearance after last ACK is imputed',legacy_advisories=scan['advisories'])
        if scan['post'] and last>600:
            from fractions import Fraction
            req=[e for e in files['command_events.jsonl'] if e['event']=='REQUESTED']
            C=sum((Fraction(str([q for q in req if q['global_request_s']<=t][-1]['rate_veh_h']))/3600 for t in range(600,last)),Fraction(0))
            N=sum(x['time_begin_s']>=600 for x in scan['entries'])
            result['observed_prefix']=dict(C_exact_fraction=str(C),independent_physical_N=N,residual_C_minus_N=str(C-N),last_ACK=last,accounting_domain=result['domains'].get('accounting',{}).get('status'))
        result['per_step_accounting']=[dict(time_begin_s=r['time_begin_s'],motion=r['motion'],accounting=r['accounting'],constraints=r.get('constraint_observation')) for r in scan['post'] if r['time_begin_s']>=600]
        reds=[r for r in scan['post'] if r['time_begin_s']>=600 and r['motion']=='r']
        if reds:run('first_red_checkpoint',lambda:(checkpoint(provenance.read(raw/'first_red_checkpoint.json'),reds) or dict(status='PASS_FIRST_RED_CHECKPOINT')))
        else:result['domains']['first_red_checkpoint']=dict(status='NOT_TESTED_NO_CONTROLLED_RED')
    run('EOF_ownership',lambda:provenance.eof(raw,receipt,lines(raw/'log_intervals.jsonl'),provenance.read(provenance.resolve(root,card['guardian']['receipt'])),provenance.read(raw/'owned_process_identity.json'),proof['card_sha256'],provenance.sha(raw/'release.json'),scan['post'][-1] if scan is not None else None))
    if receipt['final_logs'].get('status')!='BOUND_NO_OBSERVED_NATIVE_MESSAGE':result['observed_alarms'].append(dict(kind='NATIVE_FINAL_LOG_MESSAGE_OR_UNKNOWN',detail=receipt['final_logs']))
    if receipt.get('error'):result['observed_alarms'].append(dict(kind='RUNTIME_STOP_RETAINED',status=receipt['status'],error=receipt['error'],last_completed=last,last_accounted=receipt['last_accounted_s'],unobserved_preparation_tail=receipt.get('pending')))
    if last!=4200:result['missing_or_unknown'].append(dict(domain='full_horizon',status='NOT_TESTED_OR_TRUNCATED',last_ACK=last,target=4200))
    result['status']='UNKNOWN_INCOMPLETE_EVIDENCE' if result['missing_or_unknown'] else 'STOP_OBSERVED_ALARM' if result['observed_alarms'] else 'PASS_NATIVE_OBSERVED_DATA_INTEGRITY_ONLY'
    result['native_safety_proven']=False;result['formal_effect_proven']=False
    return result


def main():
    p=argparse.ArgumentParser();p.add_argument('--manifest',required=True,type=Path);p.add_argument('--card',required=True,type=Path);p.add_argument('--out',required=True,type=Path);p.add_argument('--postanalysis-reader-v1',action='store_true');a=p.parse_args()
    need(not a.out.exists(),'REFUSE_EXISTING_PROCESSED_OUTPUT');a.out.mkdir(parents=True)
    try:r=audit(a.manifest,a.card,postanalysis_reader_v1=a.postanalysis_reader_v1)
    except Exception as exc:r=dict(status='UNKNOWN_AUDIT_EXCEPTION',reason=type(exc).__name__+':'+str(exc),traceback=traceback.format_exc(),qualified=False)
    with (a.out/'NATIVE_AUDIT_RESULT.json').open('x') as f:json.dump(r,f,indent=2,allow_nan=False);f.write('\n')
    print(r['status']);return 0 if r['status']=='PASS_NATIVE_OBSERVED_DATA_INTEGRITY_ONLY' else 1

if __name__=='__main__':raise SystemExit(main())

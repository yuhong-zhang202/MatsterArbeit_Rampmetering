"""Narrow independent ordinary-service log reconciliation; no native launch.

Current entrypoint accepts explicitly labelled engineering fake bundles only.
It does not certify EOF, full cohort, urban effects or native safety. Those
unmeasured domains remain NOT_TESTED, rather than inheriting old qualifications.
"""
import argparse
from fractions import Fraction
import json
import math
from pathlib import Path

DETECTORS=('p1_main_down_20_l0','p1_main_down_20_l1')


def need(ok,reason):
    if not ok:raise ValueError(reason)


def fraction(x):
    return Fraction(str(x))


def near(a,b):
    return type(a) in (int,float) and math.isfinite(a) and abs(a-float(b))<=1e-9


def read_bundle(path):
    path=Path(path)
    receipt=json.loads((path/'SYNTHETIC_RECEIPT.json').read_text())
    need(receipt['classification']=='FAKE_WORLD_NO_NATIVE_TRAFFIC_OR_SAFETY_EVIDENCE','not a supported synthetic bundle; native audit NOT_TESTED')
    files={p.name:[json.loads(line) for line in p.read_text().splitlines()] for p in path.glob('*.jsonl')}
    return dict(receipt=receipt,files=files)


def unique(rows,key,reason):
    result={}
    for row in rows:
        need(key in row and row[key] not in result,reason)
        result[row[key]]=row
    return result


def check_accounting(a,C,selected,applied,E,X,N,partial):
    need(fraction(a['C_exact_fraction'])==C and fraction(a['C_selected_exact_fraction'])==selected and
         fraction(a['C_applied_exact_fraction'])==applied,'corrupt C/selected/applied integral')
    need(a['E']==a['E_scheduled_nominal']==E and a['E_executed_nominal']==X and a['N']==N,'corrupt E_scheduled/E_exec/N')
    need(a['scheduled_minus_executed']==E-X and a['executed_minus_actual']==X-N and
         near(a['requested_minus_nominal'],C-E) and a['nominal_minus_actual']==E-N and
         near(a['requested_minus_actual'],C-N),'corrupt residual decomposition')
    need(a['partial_cycle'] is partial,'corrupt partial flag')


def feedback_check(events,end,request_rows):
    seed=[e for e in events if e['event']=='E1_ACTIVATION_SEED']
    need(len(seed)==1 and seed[0]['global_s']==seed[0]['logical_s']==seed[0]['window_begin_global_s']==600,'E1 activation not600')
    steps=unique([e for e in events if e['event']=='E1_POST_ACK_EVENTS'],'global_s','duplicate E1 ACK')
    need(sorted(steps)==list(range(601,end+1)),'missing E1 ACK window')
    decisions=unique([e for e in events if e['event']=='PROJECT_FEEDBACK_DECISION'],'global_s','duplicate feedback decision')
    need(sorted(decisions)==list(range(630,end,30)),'missing or terminal feedback decision')
    known={d:{} for d in DETECTORS}
    def add(raw):
        need(set(raw)==set(DETECTORS),'detector domain')
        for detector,items in raw.items():
            seen=set()
            for item in items:
                need(len(item)==5,'E1 schema')
                vid,length,entry,leave,type_id=item;key=(vid,entry)
                need(key not in seen and isinstance(vid,str) and vid and length>0 and
                     all(type(x) in (int,float) and math.isfinite(x) for x in (length,entry,leave)) and
                     (leave==-1 or leave>=entry),'E1 malformed or duplicate')
                seen.add(key)
                old=known[detector].get(key)
                need(old is None or (old[1]==length and old[4]==type_id and (old[3]==-1 or old[3]==leave)),'E1 rebound')
                known[detector][key]=item
    add(seed[0]['ongoing_events'])
    previous=900;reconstructed=[]
    for t in range(601,end+1):
        need(steps[t]['logical_s']==t,'E1 clock shifted')
        add(steps[t]['raw_events'])
        if t not in decisions:continue
        e=decisions[t];begin=t-30
        need(e['logical_s']==e['update_time_s']==e['global_window_end_s']==e['interval_end_s']==t and
             e['global_window_begin_s']==e['interval_begin_s']==begin,'feedback window binding')
        occ=[]
        for detector in DETECTORS:
            occupied=sum(max(0,min(t,x[3] if x[3]!=-1 else t)-max(begin,x[2])) for x in known[detector].values())
            occ.append(occupied/30*100)
        raw=previous+70*(11-sum(occ)/2);clipped=max(300,min(900,raw))
        need(near(e['occ_l0_pct'],occ[0]) and near(e['occ_l1_pct'],occ[1]) and
             near(e['rate_previous_veh_h'],previous) and near(e['rate_raw_veh_h'],raw) and
             near(e['rate_clipped_veh_h'],clipped),'feedback independently reconstructed mismatch')
        request=next((q for q in request_rows if q['request_id']==e['request_id']),None)
        need(request is not None and request['global_request_s']==t and near(request['rate_veh_h'],clipped),'feedback request not bound')
        previous=clipped;reconstructed.append(dict(begin_s=begin,end_s=t,rate_veh_h=clipped))
    return reconstructed


def audit(bundle):
    receipt,files=bundle['receipt'],bundle['files']
    end=receipt['last_accounted_s']
    need(type(end) is int and end>600 and receipt['last_completed_s']==end,'unaccounted endpoint')
    pre=unique(files['pre_steps.jsonl'],'time_s','duplicate pre ACK')
    rows=[]
    for r in files['post_steps.jsonl']:
        if 'retained_receipts' in r:rows.extend(r['retained_receipts'])
        else:rows.append(r)
    post=unique(rows,'time_begin_s','duplicate post ACK')
    need(sorted(pre)==sorted(post)==list(range(end)),'missing or extra whole-run pre/post interval')
    verified=[r for r in files['step_ack.jsonl'] if r['actual_time_verified']]
    ack=unique(verified,'requested_target_s','duplicate verified ACK')
    need(sorted(ack)==list(range(1,end+1)) and all(r['ACK_received'] is True and r['actual_readback_s']==t for t,r in ack.items()),'missing or false clock ACK')
    events=files['command_events.jsonl'];requests=[e for e in events if e['event']=='REQUESTED']
    request_ids=unique(requests,'request_id','duplicate request')
    need(requests and requests[0]['global_request_s']==600 and [e['global_request_s'] for e in requests]==sorted(e['global_request_s'] for e in requests),'request chronology or activation')
    selections=unique([e for e in events if e['event']=='BOUNDARY_PACKET_SELECTED_NOT_APPLIED'],'time_s','duplicate selection')
    admissions=unique(files['admission.jsonl'],'time_s','duplicate admission')
    need(set(selections)==set(admissions) and min(selections)==600,'missing selection/admission')
    initial=admissions[600]
    need(initial['initial_same_green'] is True and not initial['vehicle_states'] and initial['receiver']['available'] is True,'natural initial empty same-G precondition')
    need(not any(p['method']=='setProgram' and p['value']=='CA_C8' for r in pre.values() for p in r['phase_requests']),'artificial prequeue')
    selected_acks=unique([e for e in events if e['event'] in ('PACKET_ACK_OBSERVED','WITHHELD_RED_ACK_OBSERVED')],'cycle_id','duplicate execution ACK')
    completed=unique([e for e in events if e['event']=='NOMINAL_PACKET_COMPLETED'],'cycle_id','duplicate completion')
    C=Cs=Ca=Fraction(0);E=X=0;seen=set();cycles=[];current=None;first_application={};all_n=[]
    for t in range(600,end):
        r,p=post[t],pre[t]['bound_snapshot']
        need(r['time_end_s']==r['observed_time_s']==t+1 and r['accounting_complete'] is True,'missing accounting or post time')
        pending=[q for q in requests if q['global_request_s']<=t][-1]
        rate=fraction(pending['rate_veh_h']);need(300<=rate<=900,'invalid issued rate')
        if t in selections:
            need(current is None or current['end']==t,'selection before complete nominal packet')
            se,ad=selections[t],admissions[t]
            errors={period:C-E+rate*period/3600-2 for period in range(8,25)}
            period=min(errors,key=lambda v:(abs(errors[v]),-v))
            need(se['chosen_period_s']==ad['period_s']==period and fraction(se['actual_C_fraction'])==C and
                 se['scheduled_nominal_E']==E and fraction(se['scheduled_error_fraction'])==C-E,'physical debt catchup or corrupt selection')
            need(se['candidate_errors_fraction']=={str(k):str(v) for k,v in errors.items()},'corrupt candidate arithmetic')
            green,yellow,program=(5,3,'T10_G5Y3_NATIVE') if period==10 else (4,min(5,period-6),f'I12_PACKET{period}')
            executing=ad['receiver']['available'];need(type(executing) is bool,'unknown admission receiver')
            ca=selected_acks.get(len(cycles));need(ca is not None,'missing execution decision ACK')
            need(ca['event']==('PACKET_ACK_OBSERVED' if executing else 'WITHHELD_RED_ACK_OBSERVED'),'false executed packet')
            binding=r['post_signal_application_binding'];actual_program=binding['actual_program']
            current=dict(id=len(cycles),begin=t,end=t+period,period=period,executed=executing,program=actual_program,selected_request=pending['request_id'],N=0,phases={'G':0,'y':0,'r':0})
            need(ad['cycle_id']==current['id'] and ad['selected_request_id']==pending['request_id'],'selected request mismatch')
            calls=pre[t]['phase_requests']
            if executing:
                need(binding['actual_state']=='G' and binding['actual_phase']==0 and actual_program==ad['selected_program']==program and
                     ca['application_global_s']==t and ca['first_green_ACK_s']==t+1,'false G application ACK')
                need(any(v['method']=='setProgram' and v['value']==program for v in calls) and
                     any(v['method']=='setPhase' and v['value']==0 for v in calls),'missing actual program/green setter')
                first_application.setdefault(pending['request_id'],t)
            else:
                need(t>600 and binding['actual_state']=='r' and binding['actual_phase']==2 and
                     actual_program==post[t-1]['post_signal_application_binding']['actual_program'],'held phase/program not actual previous red')
                need(not any(v['method'] in ('setProgram','setPhase') for v in calls),'held selection falsely executed')
                need(any(v['method']=='setPhaseDuration' and v['call_completed'] and v['value']==period for v in calls),'held duration setter absent')
            cycles.append(current)
        need(current is not None and current['begin']<=t<current['end'],'uncovered packet')
        need(p['cycle_id']==current['id'] and p['time_s']==t,'pre cycle binding')
        b=r['post_signal_application_binding'];motion=r['motion']
        need(b['status']=='BOUND_BEFORE_LEDGER' and b['ACK_s']==t+1 and
             b['actual_program']==p['program']==current['program'] and b['actual_state']==p['motion']==motion and
             b['actual_phase']==p['motion_phase'],'unbound actual phase/program')
        chain=r['rate_chain']
        # rate_chain is captured before ledger.end_step; the first-G row
        # therefore still has null applied fields. Actual application is
        # independently established by that row's G binding and emitted ACK.
        chain_applied = current['executed'] and t>current['begin']
        expected_rate = Fraction(7200,current['period']) if chain_applied else None if current['executed'] else 0
        need(chain['selected_request_id']==current['selected_request'] and
             chain['applied_request_id']==(current['selected_request'] if chain_applied else None) and
             near(chain['r_policy_selected_veh_h'],Fraction(7200,current['period'])) and
             (chain['r_policy_applied_veh_h'] is None if expected_rate is None else near(chain['r_policy_applied_veh_h'],expected_rate)),
             'selected fields falsely reported as applied')
        if not current['executed']:need(motion=='r','held false nonred motion')
        current['phases'][motion]+=1
        for crossing in r['actual_crossings']:
            vid=crossing['vehicle_id']
            need(vid not in seen and crossing['cycle_id']==current['id'] and crossing['crossing_time_lower_s']==t and
                 crossing['crossing_time_upper_s']==t+1 and crossing['motion_signal_state']==motion and motion in ('G','y') and vid in r['post_world'],'duplicate red or unbound crossing')
            seen.add(vid);current['N']+=1
        C+=rate/3600;Cs+=Fraction(2,current['period'])
        if current['executed']:Ca+=Fraction(2,current['period'])
        partial=t+1<current['end']
        if not partial:
            E+=2;X+=2 if current['executed'] else 0
            ev=completed.get(current['id'])
            need(ev and ev['time_s']==t+1 and ev['executed'] is current['executed'] and ev['actual_packet_N']==current['N'] and
                 fraction(ev['C_exact_fraction'])==C and ev['E_scheduled']==E and ev['E_executed']==X and ev['N']==len(seen),'missing or corrupt nominal completion')
            all_n.append(current['N'])
        check_accounting(r['accounting'],C,Cs,Ca,E,X,len(seen),partial)
    need(len(selected_acks)==len(cycles) and len(completed)==E//2,'extra packet/completion event')
    check_accounting(receipt['accounting'],C,Cs,Ca,E,X,len(seen),end<cycles[-1]['end'])
    for c,actual in zip(cycles,receipt['cycles']):
        need(actual['applied_request_id']==(c['selected_request'] if c['executed'] else None) and
             (near(actual['applied_command_veh_h'],Fraction(7200,c['period'])) if c['executed'] else actual['applied_command_veh_h'] is None),
             'false cycle applied request or rate')
        need(actual['executed'] is c['executed'] and actual['period_s']==c['period'] and actual['signal_program']==c['program'] and
             actual['phase_exposure_s']==c['phases'] and sum(actual['N_'+m] for m in ('G','y','r'))==c['N'],'false cycle summary execution/exposure')
    need(len(receipt['cycles'])==len(cycles),'missing cycle summary')
    need(set(receipt['command_records'])==set(request_ids),'missing command record')
    actual_ack_ids=[e['request_id'] for e in events if e['event']=='ACK_OBSERVED']
    need(len(actual_ack_ids)==len(set(actual_ack_ids)) and set(actual_ack_ids)==set(first_application),'missing or duplicate first-application ACK')
    for rid,record in receipt['command_records'].items():
        need(rid in request_ids and record['first_application_s']==first_application.get(rid),'false application or pending record')
    for e in events:
        if e['event']=='ACK_OBSERVED':
            rid=e['request_id'];need(e['application_global_s']==first_application[rid] and e['application_delay_s']==first_application[rid]-request_ids[rid]['global_request_s'],'application delay mismatch')
    duration=files.get('policy_duration_requests.jsonl',[])
    for d in duration:
        t=d['time_s'];need(600<=t<end and d['cycle_end_s']-t==d['value']>=1,'terminal or malformed duration setter')
        if d['status']=='READBACK_VERIFIED':
            b=d['actual_readback'];need(d['call_completed'] and b['phase']==2 and b['state']=='r' and b['nextSwitch_s']==d['cycle_end_s'] and
                                      b['program']==pre[t]['bound_snapshot']['program'],'red duration binding')
    for name in ('policy_phase_requests.jsonl',):
        need(all(x['time_s']<end for x in files.get(name,[])),'setter at or after endpoint')
    for c in cycles:
        if not c['executed']:
            need(any(d['status']=='READBACK_VERIFIED' and d['time_s']==c['begin'] and d['cycle_end_s']==c['end'] for d in duration),'held duration readback missing')
    stops=[r for r in post.values() if r.get('status','').startswith('STOP_')]
    need(all(r['time_end_s']==end for r in stops),'movement after hard stop')
    need(bool(stops)==bool(receipt['error']),'hard stop receipt mismatch')
    for r in post.values():
        if any(r.get('native_event_counters',{}).values()) or r.get('reasons'):
            need(bool(receipt['error']) and r['time_end_s']==end,'safety failure falsely completed')
    feedback=feedback_check(files['feedback_events.jsonl'],end,requests) if not receipt['error'] else []
    return dict(status='PASS_OFFLINE_OBSERVATION_ACCOUNTING_ONLY',service_qualification='NOT_TESTED',native_EOF='NOT_TESTED',
        lifecycle_4050='NOT_TESTED',urban_exposure='NOT_TESTED',native_safety='NOT_TESTED',
        observed_stop='HARD_OR_UNKNOWN_STOP_RETAINED' if receipt['error'] else 'BOUNDED_SYNTHETIC_END',error=receipt['error'],
        begin_s=600,end_s=end,C=str(C),C_selected=str(Cs),C_applied=str(Ca),E_scheduled=E,E_executed=X,N=len(seen),
        C_minus_N=str(C-len(seen)),C_minus_E_scheduled=str(C-E),E_scheduled_minus_N=E-len(seen),
        complete_packet_actual_N=all_n,periods=[c['period'] for c in cycles],held_packets=[c['id'] for c in cycles if not c['executed']],
        partial=end<cycles[-1]['end'],first_applications=first_application,feedback_windows=feedback)


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--input',type=Path,required=True);parser.add_argument('--output',type=Path,required=True)
    args=parser.parse_args();result=audit(read_bundle(args.input))
    with args.output.open('x') as file:json.dump(result,file,indent=2,allow_nan=False);file.write('\n')
    print(result['status'])

if __name__=='__main__':main()

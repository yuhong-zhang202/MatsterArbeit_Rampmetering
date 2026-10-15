"""Natural600 executed/held phases; preserve valid unprepared terminal red."""
from scripts.natural_service_audit_20261015_v1.actual import need,near


def audit(pre,post,cycles,tls,durations,end):
    observed=[];used=set()
    for c in cycles:
        b,ce=c['begin_s'],c['end_s'];T=c['period_s'];G,Y=(5,3) if T==10 else (4,min(5,T-6))
        rows=[r for r in post if b<=r['time_begin_s']<ce]
        if not rows:continue
        seq=''.join(r['motion'] for r in rows);program=c['signal_program'];held=c['executed'] is False
        if held:
            need(seq=='r'*len(rows),'HELD_NOT_RED')
            at=b
        else:
            g=len(seq)-len(seq.lstrip('G'));need(1<=g<=G,'GREEN_PREFIX')
            ge=c['green_end_s'] if c['green_end_s'] is not None else b+G
            need(ge==b+g if g<len(seq) else ge>=b+g,'GREEN_END_TIME')
            need(seq==('G'*(ge-b)+'y'*Y+'r'*(ce-ge-Y))[:len(rows)],'PHASE_ORDER')
            need(ce-ge-Y>=2,'MINIMUM_RED')
            if ge<b+G:need(c['N_G']>=2 and c['green_end_reason']=='ACTUAL_QUOTA_ACK','EARLY_GREEN_WITHOUT_QUOTA')
            at=ge+Y+1
        records=[d for d in durations if d['time_s']==at]
        if at<end:
            need(len(records)==2 and [d['status'] for d in records]==['ATTEMPTED','READBACK_VERIFIED'],'REQUIRED_EARLIER_RED_SETTER_MISSING')
            for d in records:
                need(d['value']==ce-at and d['cycle_end_s']==ce,'RED_DURATION_VALUE')
                used.add(id(d))
            d=records[-1];rb=d['actual_readback'];need(d['call_completed'] and rb==dict(time_s=at,program=program,phase=2,state='r',nextSwitch_s=ce),'RED_DURATION_READBACK')
        elif at==end and not held:
            # Old processed V2 rule: no prepare/setter for an interval starting
            # at end. Require an actually bound partial first-red ACK.
            need(not records and not c['completed'] and rows[-1]['time_end_s']==end and rows[-1]['motion']=='r' and len(pre)==len(post),'TERMINAL_NO_FUTURE_SETTER')
            need(near(rows[-1]['phase_observation']['next_switch_after_s'],ce),'TERMINAL_NATIVE_CLOCK')
        for r in rows:
            t=r['time_begin_s'];state=r['motion'];phase={'G':0,'y':1,'r':2}[state];x=tls[t]
            need(x['programID']==program and x['state']==state and x['phase']==str(phase),'TLS_PROGRAM_PHASE')
            if held:switch=ce
            else:switch=b+G if state=='G' else ge+Y if state=='y' else ge+T-G if t==ge+Y else ce
            need(near(r['phase_observation']['next_switch_after_s'],switch),'ACTUAL_SWITCH_CLOCK')
            p=pre[t]['bound_snapshot'];need(p['program']==program and p['motion']==state,'PRE_ACTUAL_PHASE')
        observed.append(dict(begin_s=b,end_s=ce,program=program,held=held,motions=seq,completed=c['completed']))
    need(len(used)==len(durations),'UNBOUND_DURATION_OR_TERMINAL_SETTER')
    return dict(status='PASS_CONTINUOUS_NATIVE_PHASES',cycles=observed)

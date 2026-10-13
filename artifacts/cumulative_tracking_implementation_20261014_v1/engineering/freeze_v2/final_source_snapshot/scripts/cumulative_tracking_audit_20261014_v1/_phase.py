"""Protected continuous-phase checker adapted only to cycle catalogue metadata."""
from fractions import Fraction
from decimal import Decimal
from .core import need,near,moment,catalogue
def audit_phases(tls,posts,acks,cycles,phase_requests,durations,pre_rows=None):
    """Contiguous actual prefix G then y then r, variable T/early-G and timers.

    Cycle begin/T/ID must be independently derived by audit_accounting. Original
    TLS order is preserved. No unobserved phase or following green is invented.
    """
    need(len(tls)==len(posts) and len(acks)==2*len(posts),'PHASE_ACK_COVERAGE')
    if not posts:return {'status':'NOT_OBSERVED','cycles':[]}
    result=[];phase_calls=[];used_calls=set();used_duration=set()
    for event in phase_requests:
        for call in event.get('requests',[]):phase_calls.append((event,call))
    for cycle in cycles:
        b=cycle['begin_s'];end=cycle['end_s'];T=cycle['period_s'];P=catalogue(T);Y=P['yellow_s'];G=P['max_green_s'];program=P['program']
        rows=[q for q in posts if b<=q['time_begin_s']<end];states=''.join(q['motion'] for q in rows)
        g=len(states)-len(states.lstrip('G'));need(1<=g<=G,'GREEN_CONTINUITY')
        ge=b+g if g<len(states) else None
        # The final prefix may stop during G. A recorded post-ACK green-close
        # request is usable without pretending yellow was observed.
        yc=[(e,c) for e,c in phase_calls if c.get('method')=='setPhase' and c.get('value')==1 and b<c.get('time_s',-1)<=b+G]
        need(len(yc)<=1,'DUPLICATE_GREEN_CLOSE')
        if yc:
            e,c=yc[0];used_calls.add(id(c));need(c.get('call_completed') is True and moment(c['time_s'],b+g),'GREEN_CLOSE_ACK_TIME')
            need(sum(q['N_G'] for q in [cycle])>=2,'QUOTA_CLOSE_WITHOUT_ACTUAL_N')
            ge=c['time_s']
            rb=e.get('actual_readback',{});need(rb.get('phase')==1 and rb.get('state')=='y' and moment(rb.get('time_s'),ge) and moment(rb.get('nextSwitch_s'),ge+Y),'YELLOW_SETTER_READBACK')
        elif ge is not None:need(g==G,'EARLY_GREEN_WITHOUT_QUOTA_REQUEST')
        predicted='G'*g if ge is None else ('G'*g+'y'*Y+'r'*(T-g-Y))[:len(states)]
        need(states==predicted,'CONTINUOUS_G_Y_R_ORDER')
        if cycle['completed']:need(len(states)==T and cycle['phase_exposure_s']['y']==Y and cycle['phase_exposure_s']['r']>=2,'COMPLETED_CLEARANCE')
        result.append(dict(begin_s=b,end_s=end,period_s=T,observed_motion_sequence=states,green_end_s=ge,yellow_s=Y,max_green_s=G,program=program,completed=cycle['completed']))
        for row in rows:
            t=row['time_begin_s'];i=t-1200;state=row['motion'];phase={'G':0,'y':1,'r':2}[state];x=tls[i]
            need(Decimal(x.get('time','NaN')).is_finite() and Decimal(x['time'])==t and x.get('id')=='ramp_mid' and x.get('programID')==program and x.get('phase')==str(phase) and x.get('state')==state,'TLS_TIME_IDENTITY_OR_ORDER')
            a0,a1=acks[2*i:2*i+2];need(moment(a0.get('requested_target_s'),t+1) and a0.get('ACK_received') is True and a0.get('actual_time_verified') is False and a0.get('actual_readback_s') is None and moment(a1.get('requested_target_s'),t+1) and a1.get('ACK_received') is True and a1.get('actual_time_verified') is True and moment(a1.get('actual_readback_s'),t+1),'CONTINUOUS_TWO_STAGE_ACK')
            po=row['phase_observation'];need(type(po.get('phase_after')) is int and po['phase_after']==phase and po.get('state_after')==state,'POST_PHASE_IDENTITY')
            switch=b+G if state=='G' else ge+Y if state=='y' else (ge+T-G if t==ge+Y else end)
            need(moment(po.get('next_switch_after_s'),switch),'POST_SWITCH_CLOCK')
            before=po.get('state_before');bp=po.get('phase_before');bs=po.get('next_switch_before_s')
            need(type(bp) is int and bp=={'G':0,'y':1,'r':2}.get(before),'PRE_PHASE_IDENTITY')
            same=before==state and moment(bs,switch)
            due=(state=='r' and t==ge+Y and before=='y' and moment(bs,t)) or (state=='y' and t==ge and before=='G' and moment(bs,t)) or (state=='G' and t==b and b>1200 and before=='r' and moment(bs,t))
            need(same or due,'PRE_PENDING_SWITCH_BOUNDARY')
            if pre_rows is not None:
                if t==b:
                    changes=pre_rows[i].get('phase_requests',[])
                    prior=cycles[cycles.index(cycle)-1] if cycles.index(cycle)>0 else None
                    changed=prior is None or prior['period_s']!=T
                    need([(q.get('method'),q.get('value')) for q in changes]==([('setProgram',program),('setPhase',0)] if changed else []),'BOUNDARY_PROGRAM_REQUESTS')
                    need(all(q.get('time_s')==b and q.get('call_completed') is True for q in changes),'BOUNDARY_SETTER_CLOCK')
                else:need(not pre_rows[i].get('phase_requests',[]),'MIDCYCLE_PROGRAM_RESTART')
                pr=pre_rows[i]['bound_snapshot'];need(pr['phase_before']==bp and pr['state_before']==before and pr['next_switch_before_s']==bs and pr['program']==program,'PRE_SNAPSHOT_PHASE_BINDING')
        if ge is not None and ge+Y+1<=posts[-1]['time_end_s']:
            at=ge+Y+1;records=[q for q in durations if q.get('time_s')==at];need(len(records)==2,'RED_DURATION_TRACE_COVERAGE')
            attempted,verified=records;need(attempted.get('status')=='ATTEMPTED' and attempted.get('call_completed') is False and verified.get('status')=='READBACK_VERIFIED' and verified.get('call_completed') is True,'RED_DURATION_PAIR')
            for q in records:used_duration.add(id(q));need(q.get('method')=='setPhaseDuration' and type(q.get('value')) is int and q['value']==end-at and moment(q.get('cycle_end_s'),end),'RED_DURATION_VALUE_BINDING')
            rb=verified.get('actual_readback',{});need(moment(rb.get('time_s'),at) and rb.get('program')==program and type(rb.get('phase')) is int and rb['phase']==2 and rb.get('state')=='r' and moment(rb.get('nextSwitch_s'),end),'RED_DURATION_READBACK')
            rc=[(e,c) for e,c in phase_calls if c.get('method')=='setPhaseDuration' and c.get('time_s')==at]
            need(len(rc)==1,'RED_PHASE_TRACE_COVERAGE');event,call=rc[0];used_calls.add(id(call))
            need(verified==dict(call,status='READBACK_VERIFIED',cycle_end_s=end) and event.get('actual_readback',{}).get('state')=='r' and moment(event['actual_readback'].get('nextSwitch_s'),end),'RED_PHASE_DURATION_TRACE_JOIN')
    need(len(used_calls)==len(phase_calls) and len(used_duration)==len(durations),'UNCONSUMED_PHASE_OR_DURATION_REQUEST')
    need(len(result)==len(cycles),'CYCLE_COVERAGE')
    return {'status':'PASS_CONTINUOUS_PHASES','cycles':result,'observed_intercycle_r_to_G':max(0,len(result)-1),'rate_qualified':False,'native_safety_proven':False}


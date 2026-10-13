"""Independent finite-window command/phase/feedback audit; no simulator imports."""
from fractions import Fraction
from decimal import Decimal
import math

MAX_GREEN=5
YELLOW=3
PROGRAM='T10_G5Y3_NATIVE'
DETECTORS=('p1_main_down_20_l0','p1_main_down_20_l1')
ACCOUNT_KEYS=('C','C_mapped_pending','C_applied','E','N','policy_quantization','application_latency','C_applied_minus_E','E_minus_N')

def need(ok,why):
    if not ok:raise ValueError(why)

def number(x):return type(x) in (int,float) and math.isfinite(x)
def near(x,y):return number(x) and abs(x-y)<=1e-8
def moment(x,t):return number(x) and x==t

def mapping(rate):
    need(number(rate) and rate==750,'T10_FIXED750_ONLY_RATE')
    return 10,Fraction(720)


def audit_accounting(rows,events,entries,end_s):
    """Independent intervals and requested-ID chronology; E is completed quota.

    `entries` must come from independent FCD/TLS/ACK reconstruction, never merely
    copied controller records. Logical preparation alone is not observed apply.
    """
    need(type(end_s) is int and 1200<end_s<=1272,'CARD_END')
    requests={};ordered=[];observed_events={};last=1200
    for e in events:
        kind=e.get('event')
        if kind=='REQUESTED':
            rid=e.get('request_id');t=e.get('global_request_s');rate=e.get('rate_veh_h')
            need(isinstance(rid,str) and rid and rid not in requests and type(t) is int and last<=t<=end_s,'REQUEST_ID_OR_TIME')
            need(e.get('origin')=='FIXED','REQUEST_ORIGIN')
            period,nominal=mapping(rate)
            need(e.get('mapped_period_s')==period and near(e.get('mapped_rate_veh_h'),float(nominal)),'REQUEST_MAPPING')
            need(e.get('r_ALINEA') is None,'REQUEST_FEEDBACK_STATE')
            requests[rid]=e;ordered.append(e);last=t
        elif kind=='ACK_OBSERVED':
            rid=e.get('request_id');need(rid in requests and rid not in observed_events,'OBSERVED_APPLICATION_ID')
            t=e.get('application_global_s');need(type(t) is int and moment(e.get('first_green_ACK_s'),t+1) and e.get('application_delay_s')==t-requests[rid]['global_request_s'],'OBSERVED_APPLICATION_TIME')
            observed_events[rid]=e
        else:need(kind in ('PREPARED_NOT_OBSERVED','SUPERSEDED'),'UNKNOWN_COMMAND_EVENT')
    if not rows:
        need(not entries,'ENTRY_WITHOUT_OBSERVATION')
        return {'status':'NOT_OBSERVED','accounting':dict.fromkeys(ACCOUNT_KEYS),'cycles':[],'applications':[]}
    sums=[Fraction(0)]*3;E=N=0;cycles=[];seen=set();consumed=set();first_apply={};cursor=0;pending=None
    for index,row in enumerate(rows):
        t=1200+index;end=t+1
        need(row.get('time_begin_s')==t and row.get('time_end_s')==end and end<=end_s and row.get('accounting_complete') is True,'INTERVAL_OR_PARTIAL_ACK_UNKNOWN')
        while cursor<len(ordered) and ordered[cursor]['global_request_s']<=t:pending=ordered[cursor];cursor+=1
        need(pending is not None,'INITIAL_COMMAND_MISSING');rid=pending['request_id'];rc=row.get('rate_chain')
        need(isinstance(rc,dict) and rc.get('pending_request_id')==rid and rc.get('input_origin')==pending['origin'] and near(rc.get('r_final_veh_h'),pending['rate_veh_h']),'LATEST_PENDING_BINDING')
        pt,pr=mapping(pending['rate_veh_h']);need(near(rc.get('r_policy_pending_veh_h'),float(pr)),'PENDING_RATE')
        new=not cycles or t==cycles[-1]['end_s']
        if new:
            need(rc.get('applied_request_id')==rid,'BOUNDARY_LATEST_COMMAND_NOT_APPLIED')
            cycles.append(dict(begin_s=t,end_s=t+pt,period_s=pt,yellow_s=YELLOW,applied_request_id=rid,N=0,N_G=0,N_y=0,N_r=0,E=0,completed=False,phase_exposure_s={'G':0,'y':0,'r':0}))
            if rid not in first_apply:
                first_apply[rid]=t
                need(rid in observed_events and observed_events[rid]['application_global_s']==t and row.get('motion')=='G','PREPARED_APPLICATION_NOT_ACK_BOUND')
        cycle=cycles[-1];applied=requests[cycle['applied_request_id']];at,ar=mapping(applied['rate_veh_h'])
        need(rc.get('applied_request_id')==cycle['applied_request_id'] and rc.get('period_s')==at and type(rc.get('requested_quota')) is int and rc['requested_quota']==2 and near(rc.get('r_policy_applied_veh_h'),float(ar)),'MIDCYCLE_APPLICATION_DRIFT')
        # First-row rate chain is captured before the first ACK; null delay is
        # valid there, but the separate ACK_OBSERVED event is mandatory above.
        delay=rc.get('cycle_application_delay_s')
        need(delay is None and new or delay==first_apply[cycle['applied_request_id']]-applied['global_request_s'],'COMMAND_AGE_NOT_APPLICATION_DELAY')
        motion=row.get('motion');need(motion in ('G','y','r'),'UNKNOWN_MOTION')
        ids=[]
        for i,x in enumerate(entries):
            need(type(x.get('time_begin_s')) is int and type(x.get('time_end_s')) is int and x['time_end_s']==x['time_begin_s']+1,'INDEPENDENT_ENTRY_TIME')
            if x['time_begin_s']!=t:continue
            vid=x.get('vehicle_id');need(isinstance(vid,str) and vid.startswith('R_flow.') and vid not in seen and i not in consumed and x.get('motion')==motion,'DUPLICATE_OR_UNBOUND_ENTRY');seen.add(vid);consumed.add(i);ids.append(vid)
        need(sorted(ids)==sorted(x['vehicle_id'] for x in row.get('actual_crossings',[])),'RAW_ACTUAL_N_MISMATCH')
        N+=len(ids);cycle['N']+=len(ids);cycle['N_'+motion]+=len(ids);cycle['phase_exposure_s'][motion]+=1
        sums[0]+=Fraction(str(pending['rate_veh_h']))/3600;sums[1]+=pr/3600;sums[2]+=ar/3600
        if end==cycle['end_s']:cycle['completed']=True;cycle['E']=2;E+=2
        a=dict(C=float(sums[0]),C_mapped_pending=float(sums[1]),C_applied=float(sums[2]),E=E,N=N,policy_quantization=float(sums[0]-sums[1]),application_latency=float(sums[1]-sums[2]),C_applied_minus_E=float(sums[2]-E),E_minus_N=E-N)
        need(all(near(row.get('accounting',{}).get(k),v) for k,v in a.items()),'INDEPENDENT_INTERVAL_ACCOUNTING')
    need(consumed==set(range(len(entries))),'UNCONSUMED_ENTRY_OUTSIDE_PREFIX')
    apps=[dict(request_id=rid,application_global_s=t,application_delay_s=t-requests[rid]['global_request_s']) for rid,t in first_apply.items()]
    return {'status':'PASS_ACCOUNTING','accounting':a,'cycles':cycles,'applications':apps,'observed_end_s':rows[-1]['time_end_s'],'planned_end_observed':rows[-1]['time_end_s']==end_s,'requests_without_observed_application':[rid for rid in requests if rid not in first_apply],'rate_qualified':False}


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
        b=cycle['begin_s'];end=cycle['end_s'];T=cycle['period_s'];Y=YELLOW
        rows=[q for q in posts if b<=q['time_begin_s']<end];states=''.join(q['motion'] for q in rows)
        g=len(states)-len(states.lstrip('G'));need(1<=g<=MAX_GREEN,'GREEN_CONTINUITY')
        ge=b+g if g<len(states) else None
        # The final prefix may stop during G. A recorded post-ACK green-close
        # request is usable without pretending yellow was observed.
        yc=[(e,c) for e,c in phase_calls if c.get('method')=='setPhase' and c.get('value')==1 and b<c.get('time_s',-1)<=b+MAX_GREEN]
        need(len(yc)<=1,'DUPLICATE_GREEN_CLOSE')
        if yc:
            e,c=yc[0];used_calls.add(id(c));need(c.get('call_completed') is True and moment(c['time_s'],b+g),'GREEN_CLOSE_ACK_TIME')
            need(sum(q['N_G'] for q in [cycle])>=2,'QUOTA_CLOSE_WITHOUT_ACTUAL_N')
            ge=c['time_s']
            rb=e.get('actual_readback',{});need(rb.get('phase')==1 and rb.get('state')=='y' and moment(rb.get('time_s'),ge) and moment(rb.get('nextSwitch_s'),ge+Y),'YELLOW_SETTER_READBACK')
        elif ge is not None:need(g==MAX_GREEN,'EARLY_GREEN_WITHOUT_QUOTA_REQUEST')
        predicted='G'*g if ge is None else ('G'*g+'y'*Y+'r'*(T-g-Y))[:len(states)]
        need(states==predicted,'CONTINUOUS_G_Y_R_ORDER')
        if cycle['completed']:need(len(states)==T and cycle['phase_exposure_s']['y']==Y and cycle['phase_exposure_s']['r']>=2,'COMPLETED_CLEARANCE')
        result.append(dict(begin_s=b,end_s=end,period_s=T,observed_motion_sequence=states,green_end_s=ge,yellow_s=Y,completed=cycle['completed']))
        for row in rows:
            t=row['time_begin_s'];i=t-1200;state=row['motion'];phase={'G':0,'y':1,'r':2}[state];x=tls[i]
            need(Decimal(x.get('time','NaN')).is_finite() and Decimal(x['time'])==t and x.get('id')=='ramp_mid' and x.get('programID')==PROGRAM and x.get('phase')==str(phase) and x.get('state')==state,'TLS_TIME_IDENTITY_OR_ORDER')
            a0,a1=acks[2*i:2*i+2];need(moment(a0.get('requested_target_s'),t+1) and a0.get('ACK_received') is True and a0.get('actual_time_verified') is False and a0.get('actual_readback_s') is None and moment(a1.get('requested_target_s'),t+1) and a1.get('ACK_received') is True and a1.get('actual_time_verified') is True and moment(a1.get('actual_readback_s'),t+1),'CONTINUOUS_TWO_STAGE_ACK')
            po=row['phase_observation'];need(type(po.get('phase_after')) is int and po['phase_after']==phase and po.get('state_after')==state,'POST_PHASE_IDENTITY')
            switch=b+MAX_GREEN if state=='G' else ge+Y if state=='y' else (ge+T-MAX_GREEN if t==ge+Y else end)
            need(moment(po.get('next_switch_after_s'),switch),'POST_SWITCH_CLOCK')
            before=po.get('state_before');bp=po.get('phase_before');bs=po.get('next_switch_before_s')
            need(type(bp) is int and bp=={'G':0,'y':1,'r':2}.get(before),'PRE_PHASE_IDENTITY')
            same=before==state and moment(bs,switch)
            due=(state=='r' and t==ge+Y and before=='y' and moment(bs,t)) or (state=='y' and t==ge and before=='G' and moment(bs,t)) or (state=='G' and t==b and b>1200 and before=='r' and moment(bs,t))
            need(same or due,'PRE_PENDING_SWITCH_BOUNDARY')
            if pre_rows is not None:
                pr=pre_rows[i]['bound_snapshot'];need(pr['phase_before']==bp and pr['state_before']==before and pr['next_switch_before_s']==bs and pr['program']==PROGRAM,'PRE_SNAPSHOT_PHASE_BINDING')
        if ge is not None and ge+Y+1<=posts[-1]['time_end_s']:
            at=ge+Y+1;records=[q for q in durations if q.get('time_s')==at];need(len(records)==2,'RED_DURATION_TRACE_COVERAGE')
            attempted,verified=records;need(attempted.get('status')=='ATTEMPTED' and attempted.get('call_completed') is False and verified.get('status')=='READBACK_VERIFIED' and verified.get('call_completed') is True,'RED_DURATION_PAIR')
            for q in records:used_duration.add(id(q));need(q.get('method')=='setPhaseDuration' and type(q.get('value')) is int and q['value']==end-at and moment(q.get('cycle_end_s'),end),'RED_DURATION_VALUE_BINDING')
            rb=verified.get('actual_readback',{});need(moment(rb.get('time_s'),at) and rb.get('program')==PROGRAM and type(rb.get('phase')) is int and rb['phase']==2 and rb.get('state')=='r' and moment(rb.get('nextSwitch_s'),end),'RED_DURATION_READBACK')
            rc=[(e,c) for e,c in phase_calls if c.get('method')=='setPhaseDuration' and c.get('time_s')==at]
            need(len(rc)==1,'RED_PHASE_TRACE_COVERAGE');event,call=rc[0];used_calls.add(id(call))
            need(verified==dict(call,status='READBACK_VERIFIED',cycle_end_s=end) and event.get('actual_readback',{}).get('state')=='r' and moment(event['actual_readback'].get('nextSwitch_s'),end),'RED_PHASE_DURATION_TRACE_JOIN')
    need(len(used_calls)==len(phase_calls) and len(used_duration)==len(durations),'UNCONSUMED_PHASE_OR_DURATION_REQUEST')
    need(len(result)==len(cycles),'CYCLE_COVERAGE')
    return {'status':'PASS_CONTINUOUS_PHASES','cycles':result,'observed_intercycle_r_to_G':max(0,len(result)-1),'rate_qualified':False,'native_safety_proven':False}


from scripts.unified_alinea_audit_20261013_v1.core import audit_feedback

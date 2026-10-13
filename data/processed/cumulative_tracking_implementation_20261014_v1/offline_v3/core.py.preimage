"""Independent request/actual-N cumulative accounting; no production Ledger import."""
from fractions import Fraction as F
from scripts.t10_g5_y3_audit_20261013_v1.core import need,number,near,moment
KEYS=('C','C_nearest_reference','C_applied','E','N','requested_minus_nominal','nominal_minus_actual','requested_minus_actual')

def catalogue(T):
    need(type(T) is int and T in (8,10),'UNSUPPORTED_PACKET_CATALOGUE')
    return dict(period_s=T,max_green_s=4 if T==8 else 5,yellow_s=2 if T==8 else 3,minimum_red_s=2,program='I12_PACKET8' if T==8 else 'T10_G5Y3_NATIVE')

def nearest_reference(r):
    need(number(r) and 300<=r<=900,'INVALID_REFERENCE_REQUEST')
    # Literal legacy float rule: comparison only, never actual packet selection.
    T=min(range(8,25),key=lambda t:(abs(7200/t-r),-t))
    return T,F(str(7200/T))

def select(C,N,r):
    need(type(N) is int and N>=0 and number(r) and 720<=r<=900,'UNKNOWN_OR_UNSUPPORTED_BOUNDARY')
    D=C-N;scores={T:D+F(str(r))*T/3600-2 for T in (8,10)}
    return min(scores,key=lambda T:(abs(scores[T]),-T)),scores

def audit_accounting(rows,events,entries,end_s):
    need(type(end_s) is int and end_s>1200,'APPROVED_END')
    req={};ordered=[];observed={};packets={};selected={};last_request=1200
    for e in events:
        kind=e.get('event')
        if kind=='REQUESTED':
            rid=e.get('request_id');t=e.get('global_request_s');r=e.get('rate_veh_h')
            need(isinstance(rid,str) and rid and rid not in req and type(t) is int and last_request<=t<=end_s,'REQUEST_ID_TIME')
            need(e.get('origin') in ('FIXED','SCHEDULED','PROJECT_FEEDBACK'),'REQUEST_ORIGIN')
            T,rate=nearest_reference(r);need(e.get('nearest_reference_period_s')==T and near(e.get('nearest_reference_rate_veh_h'),float(rate)),'NEAREST_REFERENCE_NOT_POLICY')
            need((e.get('r_ALINEA') is None and e['origin']!='PROJECT_FEEDBACK') or (e['origin']=='PROJECT_FEEDBACK' and near(e.get('r_ALINEA'),r)),'REQUEST_FEEDBACK_VALUE');req[rid]=e;ordered.append(e);last_request=t
        elif kind=='ACK_OBSERVED':
            rid=e.get('request_id');t=e.get('application_global_s');need(rid in req and rid not in observed and type(t) is int and t>=req[rid]['global_request_s'] and moment(e.get('first_green_ACK_s'),t+1) and e.get('application_delay_s')==t-req[rid]['global_request_s'],'REQUEST_APPLICATION_ACK');observed[rid]=e
        elif kind=='PACKET_ACK_OBSERVED':
            t=e.get('application_global_s');need(type(t) is int and t not in packets and moment(e.get('first_green_ACK_s'),t+1),'PACKET_APPLICATION_ACK');packets[t]=e
        elif kind=='BOUNDARY_PACKET_SELECTED_NOT_APPLIED':
            t=e.get('time_s');need(type(t) is int and t not in selected,'BOUNDARY_DUPLICATE_TIME');selected[t]=e
        else:need(kind in ('PREPARED_NOT_OBSERVED','SUPERSEDED'),'UNKNOWN_COMMAND_EVENT')
    if not rows:
        need(not entries and not observed and not packets,'ENTRY_OR_APPLICATION_WITHOUT_ACK')
        return dict(status='NOT_OBSERVED',accounting=dict.fromkeys(KEYS),cycles=[],applications=[],cycle_applications=[],unobserved_boundary_selections=list(selected.values()))
    C=ref=applied=F(0);E=N=0;cycles=[];first={};seen=set();consumed=set();cursor=0;pending=None;used_selections=set();cycle_apps=[]
    for i,row in enumerate(rows):
        t=1200+i;end=t+1;need(row.get('time_begin_s')==t and row.get('time_end_s')==end and end<=end_s and row.get('accounting_complete') is True,'INTERVAL_ACK_COVERAGE')
        while cursor<len(ordered) and ordered[cursor]['global_request_s']<=t:pending=ordered[cursor];cursor+=1
        need(pending is not None,'NO_CURRENT_REQUEST');rid=pending['request_id'];r=pending['rate_veh_h'];rc=row.get('rate_chain',{})
        need(rc.get('pending_request_id')==rid and rc.get('input_origin')==pending['origin'] and near(rc.get('r_final_veh_h'),r) and rc.get('r_policy_pending_veh_h') is None and rc.get('pending_packet_status')=='SELECTED_ONLY_AT_COMPLETE_BOUNDARY','PENDING_REQUEST_NOT_NEAREST_POLICY')
        need(rc.get('r_ALINEA')==pending.get('r_ALINEA'),'RATE_CHAIN_FEEDBACK_BINDING');_,rref=nearest_reference(r);need(near(rc.get('nearest_reference_veh_h'),float(rref)),'REFERENCE_RATE')
        new=not cycles or t==cycles[-1]['end_s']
        if new:
            if cycles:need(cycles[-1]['completed'] and cycles[-1]['N']==2,'SERVICE_PACKET_MISMATCH_NO_AUTOMATIC_CATCHUP')
            T,scores=select(C,N,r);decision=selected.get(t);need(isinstance(decision,dict),'BOUNDARY_SELECTION_MISSING');used_selections.add(t)
            need(decision.get('actual_C_fraction')==str(C) and type(decision.get('actual_N')) is int and decision['actual_N']==N and decision.get('actual_error_fraction')==str(C-N) and decision.get('forecast_request_veh_h')==r and decision.get('forecast_assumption')=='CURRENT_REQUEST_HELD_NOT_OBSERVED_FUTURE','BOUNDARY_ACTUAL_VS_FORECAST')
            need(decision.get('candidate_errors_fraction')=={str(k):str(v) for k,v in scores.items()} and type(decision.get('chosen_period_s')) is int and decision['chosen_period_s']==T,'EXACT_FRACTION_SELECTION')
            P=catalogue(T);pa=packets.get(t);need(isinstance(pa,dict) and pa.get('request_id')==rid and pa.get('period_s')==T and pa.get('max_green_s')==P['max_green_s'] and pa.get('yellow_s')==P['yellow_s'] and near(pa.get('applied_command_veh_h'),7200/T),'PACKET_SELECTION_NOT_OBSERVED_FIRST_G_ACK');cycles.append(dict(begin_s=t,end_s=t+T,**P,applied_request_id=rid,packet_selection=decision,N=0,N_G=0,N_y=0,N_r=0,E=0,completed=False,phase_exposure_s={'G':0,'y':0,'r':0}))
            need(row.get('motion')=='G','PACKET_FIRST_ACK_NOT_G');cycle_apps.append(dict(request_id=rid,application_global_s=t,first_green_ACK_s=t+1,period_s=T))
            if rid not in first:need(rid in observed and observed[rid]['application_global_s']==t,'PREPARED_NOT_OBSERVED_APPLICATION');first[rid]=t
        c=cycles[-1];T=c['period_s'];need(rc.get('applied_request_id')==c['applied_request_id'] and type(rc.get('period_s')) is int and rc['period_s']==T and type(rc.get('requested_quota')) is int and rc['requested_quota']==2 and near(rc.get('r_policy_applied_veh_h'),7200/T),'ACTUAL_SELECTED_PERIOD_RATE_CHAIN')
        delay=rc.get('cycle_application_delay_s');correct=first[c['applied_request_id']]-req[c['applied_request_id']]['global_request_s'];need((new and delay is None) or delay==correct,'APPLICATION_DELAY_NOT_COMMAND_AGE')
        motion=row.get('motion');need(motion in ('G','y','r'),'UNKNOWN_MOTION');ids=[]
        for k,x in enumerate(entries):
            need(type(x.get('time_begin_s')) is int and type(x.get('time_end_s')) is int and x['time_end_s']==x['time_begin_s']+1,'ENTRY_TIME_BINDING')
            if x['time_begin_s']!=t:continue
            v=x.get('vehicle_id');need(isinstance(v,str) and v.startswith('R_flow.') and v not in seen and k not in consumed and x.get('motion')==motion,'DUPLICATE_OR_UNBOUND_ENTRY');seen.add(v);consumed.add(k);ids.append(v)
        reported=[q['vehicle_id'] for q in row.get('actual_crossings',[])];need(sorted(ids)==sorted(reported),'INDEPENDENT_ACTUAL_N')
        C+=F(str(r))/3600;ref+=rref/3600;applied+=F(7200,T)/3600;N+=len(ids);c['N']+=len(ids);c['N_'+motion]+=len(ids);c['phase_exposure_s'][motion]+=1
        if end==c['end_s']:E+=2;c['E']=2;c['completed']=True
        values=dict(C=float(C),C_nearest_reference=float(ref),C_applied=float(applied),E=E,N=N,requested_minus_nominal=float(C-E),nominal_minus_actual=E-N,requested_minus_actual=float(C-N));a=row.get('accounting',{})
        need(all(near(a.get(k),v) for k,v in values.items()) and a.get('C_exact_fraction')==str(C) and a.get('partial_cycle') is (not c['completed']) and a.get('nearest_reference_is_not_cumulative_scheduler_output') is True and a.get('E_support')=='COMPLETE_PACKETS_ONLY' and a.get('N_support')=='ALL_OBSERVED_ENTRY_BEGIN_INTERVALS','INDEPENDENT_CUMULATIVE_ACCOUNTING')
    need(consumed==set(range(len(entries))),'UNCONSUMED_ENTRY_OUTSIDE_PREFIX')
    need(set(observed)==set(first) and set(packets)=={c['begin_s'] for c in cycles},'UNCONSUMED_APPLICATION_NOT_ACK_OBSERVED')
    extras=set(selected)-used_selections;need(not extras or extras=={rows[-1]['time_end_s']},'UNBOUND_PREPARED_SELECTION')
    apps=[dict(request_id=rid,application_global_s=t,application_delay_s=t-req[rid]['global_request_s']) for rid,t in first.items()]
    return dict(status='PASS_CUMULATIVE_ACCOUNTING',accounting=values,cycles=cycles,applications=apps,cycle_applications=cycle_apps,observed_end_s=rows[-1]['time_end_s'],planned_end_observed=rows[-1]['time_end_s']==end_s,requests_without_observed_application=[rid for rid in req if rid not in first],unobserved_boundary_selections=[selected[t] for t in sorted(extras)],rate_qualified=False)

def audit_phases(*args,**kwargs):
    from ._phase import audit_phases as check
    return check(*args,**kwargs)

def audit_feedback(events,commands,account,end_s):
    from scripts.unified_alinea_audit_20261013_v1.core import audit_feedback as check
    result=check(events,commands,account,end_s)
    # Shared detector/Feedback math only; its nearest-derived label is discarded.
    result.pop('different_period_observed',None)
    result['different_period_observed']=len({x['period_s'] for x in account.get('cycle_applications',[])})>1
    result['period_source']='ACTUAL_FIRST_G_ACK_CYCLE_APPLICATIONS_NOT_NEAREST_REFERENCE'
    return result

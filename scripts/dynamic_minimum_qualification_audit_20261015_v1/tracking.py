"""Finite diagnostic tracking checks; original requests and observed entries only.

Arithmetic consistency is not service tolerance. No universal error bound or
long-run qualification is inferred from a finite trace.
"""
from fractions import Fraction as F
from scripts.cumulative_full_catalogue_audit_20261014_v1.core import need

def request_integral(requests,a,b):
    need(type(a) is int and type(b) is int and b>=a,'TRACKING_SUPPORT_TIME')
    value=F(0)
    for t in range(a,b):
        active=[q for q in requests if q['global_request_s']<=t]
        need(active,'TRACKING_REQUEST_UNKNOWN')
        value+=F(str(active[-1]['rate_veh_h']))/3600
    return value

def tracking_review(account,commands,mode,integrity_ok,feedback):
    requests=[q for q in commands if q.get('event')=='REQUESTED'];cycles=account.get('cycles',[])
    if not cycles:return {'status':'NOT_DEMONSTRATED','reason':'NO_OBSERVED_PACKET','whole_requested_minus_actual':None,'per_cycle':[],'qualification':False}
    end=account['observed_end_s'];C=F(0);N=0;rows=[];deficits=[F(0)];boundaries=[]
    for c in cycles:
        a=c['begin_s'];b=min(c['end_s'],end);I=request_integral(requests,a,b);r=F(str(c['packet_selection']['forecast_request_veh_h']));D=C-N
        need(str(C)==c['packet_selection']['actual_C_fraction'] and N==c['packet_selection']['actual_N'],'TRACKING_BOUNDARY_INPUT')
        C+=I;N+=c['N'];after=C-N;deficits.append(after)
        complete=c['completed'];forecast=D+r*c['period_s']/3600-2 if complete else None
        delta=I-r*c['period_s']/3600 if complete else None;shortfall=2-c['N'] if complete else None
        if complete:
            need(after==forecast+delta+shortfall,'TRACKING_RESIDUAL_DECOMPOSITION')
            boundaries.append((b,after));
        phase_counts={p:(c['N_'+p] if c['phase_exposure_s'][p]>0 else None) for p in ('G','y','r')}
        rows.append({'begin_s':a,'observed_end_s':b,'planned_end_s':c['end_s'],'completed':complete,'C_packet_fraction':str(I),'C_total_fraction':str(C),'N_packet':c['N'],'N_total':N,'E_packet':2 if complete else 0,'E_support':'COMPLETE_PACKETS_ONLY','error_before_fraction':str(D),'error_after_fraction':str(after),'selector_forecast_residual_fraction':str(forecast) if complete else None,'midpacket_request_change_fraction':str(delta) if complete else None,'packet_shortfall':shortfall,'phase_counts_on_observed_exposure':phase_counts,'phase_exposure_s':c['phase_exposure_s'],'partial_is_completed_quota':False})
    need(abs(float(C)-account['accounting']['C'])<1e-9 and N==account['accounting']['N'],'TRACKING_WHOLE_SUPPORT')
    problems=[]
    if not integrity_ok:problems.append('INTEGRITY_SAFETY_OR_RUNTIME_STOP')
    if not account.get('planned_end_observed'):problems.append('APPROVED_HORIZON_NOT_OBSERVED')
    if any(c['completed'] and c['N']!=2 for c in cycles):problems.append('COMPLETE_PACKET_NOT_TWO_ACTUAL_ENTRIES')
    apps=account.get('applications',[]);recovery={'status':'NOT_APPLICABLE_REAL_ALINEA'}
    if mode=='dynamic_commands':
        schedule=[(1200,300),(1201,750),(1226,900),(1237,300)]
        expected=[q for q in requests if q.get('origin')=='SCHEDULED']
        if [(q['global_request_s'],q['rate_veh_h']) for q in expected]!=schedule:problems.append('FOUR_ORIGINAL_REQUESTS_NOT_OBSERVED')
        amap={q['request_id']:q for q in apps};applied=[amap.get(q['request_id']) for q in expected]
        if len(applied)!=4 or any(q is None or not 0<=q['application_delay_s']<=23 for q in applied):problems.append('FOUR_APPLICATIONS_OR_DELAY_NOT_DEMONSTRATED')
        final=next((q for q in expected if q['global_request_s']==1237),None);app=amap.get(final['request_id']) if final else None
        if app:
            t=app['application_global_s'];start=next((F(row['error_before_fraction']) for row in rows if row['begin_s']==t),None);later=[(b,d) for b,d in boundaries if b>t]
            need(start is not None,'FINAL_LOWER_APPLICATION_BOUNDARY')
            positive=start;recovered=False
            for _,d in later:
                if positive>0 and d<positive:recovered=True
                positive=max(positive,d)
            if positive<=0:recovered=None
            recovery={'application_begin_s':t,'error_at_application_fraction':str(start),'maximum_positive_complete_boundary_error_fraction':str(max(F(0),positive)),'later_complete_boundary_errors':[{'time_s':b,'error_fraction':str(d)} for b,d in later],'status':'RECOVERY_OBSERVED' if recovered else 'NO_POSITIVE_DEFICIT_OBSERVED' if positive<=0 else 'RECOVERY_NOT_DEMONSTRATED'}
            if not later or (positive>0 and not recovered):problems.append('LOWER_300_DEBT_RECOVERY_NOT_DEMONSTRATED')
        else:
            recovery={'status':'FINAL_300_NOT_APPLIED'};problems.append('FINAL_300_NOT_APPLIED')
    else:
        if not feedback.get('feedback_command_applied'):problems.append('NON_INITIAL_REAL_FEEDBACK_NOT_APPLIED')
    return {'status':'FINITE_DIAGNOSTIC_TRACKING_DEMONSTRATED' if not problems else 'NOT_DEMONSTRATED','reasons':problems,'whole_requested_fraction':str(C),'whole_actual_N':N,'whole_requested_minus_actual_fraction':str(C-N),'maximum_positive_boundary_error_fraction':str(max(F(0),*deficits)),'per_cycle':rows,'final_300_recovery':recovery,'pending_unapplied_requests':account.get('requests_without_observed_application'),'qualification':False,'long_run_or_full_range_qualified':False,'no_percentage_or_instant_zero_threshold':True,'error_bound_is_not_allowed_service_deficit':True}

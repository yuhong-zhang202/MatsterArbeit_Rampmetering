"""Bounded independent accounting/terminal-join helpers; no simulator imports.

Actual crossing rows MUST be reconstructed separately from FCD/TLS/ACK. Passing
self-reported entries alone is not an independent runtime audit. Missing native
log/WAIT/yellow/manifest/identity coverage is a separate mandatory post-run gate.
"""
from fractions import Fraction
import math

KEYS=('C','C_mapped_pending','C_applied','E','N','policy_quantization','application_latency','C_applied_minus_E','E_minus_N')

def numeric(x):
    return type(x) in (int,float) and math.isfinite(x)

def unknown(reason):
    return {'status':'UNKNOWN','reason':reason}

def audit_rate_steps(rows, independent_entries):
    """Audit a contiguous control prefix; all-unobserved values are null.

Each independent entry: vehicle_id,time_begin_s,time_end_s,motion from actual
storage-to-internal transition plus verified motion TLS/ACK. No n=quota cap.
"""
    if not rows:
        return {'status':'NOT_OBSERVED','observed_steps':0,'accounting':dict.fromkeys(KEYS),'cycles':[]}
    sums=[Fraction(0),Fraction(0),Fraction(0)]; E=0; N=0; seen=set();cycles=[]
    expected=1200
    for row in rows:
        t=row.get('time_begin_s');end=row.get('time_end_s')
        if type(t) is not int or type(end) is not int or t!=expected or end!=t+1 or end>1272:
            return unknown('NONSEQUENTIAL_OR_UNBOUND_ACK_TIME')
        if row.get('accounting_complete') is not True:return unknown('UNRECONCILED_ADVANCED_STEP')
        motion=row.get('motion');po=row.get('phase_observation',{})
        if motion not in ('G','y','r') or po.get('state_after')!=motion:
            return unknown('UNBOUND_ACTUAL_MOTION')
        # phase_before may still be y at the event that moves under native r.
        phase=po.get('phase_after')
        if type(phase) is not int or phase != {'G':0,'y':1,'r':2}[motion]:return unknown('ACTUAL_PHASE_TYPE_OR_COLOR')
        rc=row.get('rate_chain',{})
        values=[rc.get(k) for k in ('r_final_veh_h','r_policy_pending_veh_h','r_policy_applied_veh_h')]
        if rc.get('input_origin')!='FIXED_POLICY_DIAGNOSTIC' or rc.get('r_ALINEA') is not None:
            return unknown('UNBOUND_FIXED_ORIGIN')
        if not all(numeric(x) and 300<=x<=900 for x in values):return unknown('INVALID_RATE_CHAIN')
        mapped=min((300,450,600,750,900),key=lambda q:(abs(q-values[0]),q))
        if values[1]!=mapped or values[2] not in (300,450,600,750,900):return unknown('RATE_MAPPING_MISMATCH')
        quota=rc.get('requested_quota')
        if type(quota) is not int or quota!=values[2]//150 or rc.get('period_s')!=24:
            return unknown('UNBOUND_REQUESTED_QUOTA')
        if (t-1200)%24==0:
            cycles.append({'begin_s':t,'end_s':t+24,'quota':quota,'applied':values[2],
                           'observed_steps':0,'completed':False,'E':0,'N':0,'phase_exposure_s':{'G':0,'y':0,'r':0}})
        c=cycles[-1]
        if quota!=c['quota'] or values[2]!=c['applied']:return unknown('MIDCYCLE_APPLICATION_DRIFT')
        entries=[e for e in independent_entries if e.get('time_begin_s')==t]
        reported=row.get('actual_crossings')
        if not isinstance(reported,list):return unknown('MISSING_ENTRY_RECORDS')
        ids=[]
        for e in entries:
            vid=e.get('vehicle_id')
            if not isinstance(vid,str) or not vid.startswith('R_flow.') or e.get('time_end_s')!=end or e.get('motion')!=motion or vid in seen or vid in ids:
                return unknown('DUPLICATE_OR_UNBOUND_INDEPENDENT_ENTRY')
            ids.append(vid)
        if sorted(ids)!=sorted(e.get('vehicle_id','') for e in reported):return unknown('ACTUAL_N_LEDGER_MISMATCH')
        seen.update(ids);N+=len(ids);c['N']+=len(ids);c['observed_steps']+=1;c['phase_exposure_s'][motion]+=1
        for i,v in enumerate(values):sums[i]+=Fraction(str(v))/3600
        if end==c['end_s']:
            if c['phase_exposure_s']['y']!=5 or c['phase_exposure_s']['r']<2:return unknown('INCOMPLETE_ACTUAL_CLEARANCE')
            c['completed']=True;c['E']=quota;E+=quota
        a=dict(zip(('C','C_mapped_pending','C_applied'),map(float,sums)))
        a.update(E=E,N=N,policy_quantization=float(sums[0]-sums[1]),application_latency=float(sums[1]-sums[2]),C_applied_minus_E=float(sums[2]-E),E_minus_N=E-N)
        reported_a=row.get('accounting',{})
        if any(not numeric(reported_a.get(k)) or abs(reported_a[k]-v)>1e-9 for k,v in a.items()):return unknown('INDEPENDENT_ACCOUNTING_MISMATCH')
        expected=end
    if any(e.get('vehicle_id') not in seen for e in independent_entries):return unknown('ENTRY_OUTSIDE_OBSERVED_PREFIX')
    return {'status':'PASS_ACCOUNTING_ONLY','observed_steps':len(rows),'accounting':a,'cycles':cycles,
            'complete_observation':len(rows)==72,'rate_qualified':False,'native_safety_proven':False}

def audit_terminal(before, trips, legal_lanes):
    """One bound arrived identity; duplicate/missing/rounded ambiguity => UNKNOWN.

arrivalSpeed is rounded to8 decimals. Same motion step uses dt1, irrespective
of fractional arrival timestamp. Explicit final route-edge lanes may differ
from the lane occupied before the last motion.
"""
    vid=before.get('vehicle_id');selected=[t for t in trips if t.get('id')==vid]
    if len(selected)!=1:return unknown('MISSING_OR_DUPLICATE_TERMINAL_TRIPINFO')
    tr=selected[0];b=before.get('time_begin_s');e=before.get('time_end_s')
    if type(b) is not int or type(e) is not int or e!=b+1 or before.get('time_s')!=b or before.get('arrived_id_bound') is not True:
        return unknown('UNBOUND_BEFORE_ARRIVAL_TIME')
    if not isinstance(vid,str) or not vid or tr.get('id')!=vid or before.get('type_id')!='technical_passenger' or tr.get('vType')!=before.get('type_id'):
        return unknown('UNBOUND_ARRIVAL_ID_OR_TYPE')
    route=before.get('route');edge=before.get('terminal_edge')
    if not isinstance(route,list) or not route or edge!=route[-1] or tr.get('arrivalLane') not in legal_lanes.get(edge,[]):return unknown('UNBOUND_TERMINAL_ROUTE_OR_LANE')
    if tr.get('vaporized') not in (None,''):return unknown('VAPORIZED_OR_ABNORMAL_REMOVAL')
    try: av=float(tr['arrivalSpeed']);at=float(tr['arrival']);bv=before['speed_m_s'];acc=before['acceleration_m_s2'];decel=before['normal_decel_m_s2']
    except (KeyError,TypeError,ValueError):return unknown('MISSING_TERMINAL_NUMERIC')
    if not all(numeric(v) for v in (av,at,bv,acc,decel)) or not 0<=bv<=55.55555555555556 or av<0 or abs(decel-4.5)>1e-8:
        return unknown('UNSUPPORTED_TERMINAL_DYNAMICS')
    epsilon=0.5e-8
    if not b < at-epsilon or at+epsilon > e+epsilon:return unknown('ARRIVAL_TIME_ROUNDING_NOT_BOUND_TO_STEP')
    if abs(acc-(-4.5))<1e-6: pass # Exact normal braking remains eligible.
    if acc < -4.5-1e-6:return {'status':'FAIL','reason':'BEFORE_FRAME_BRAKING_LIMIT'}
    low=max(0,av-epsilon)-bv;high=av+epsilon-bv;limit=-4.5-1e-6
    status='FAIL' if high<limit else 'PASS' if low>=limit else 'UNKNOWN'
    return {'status':status,'reason':'LAST_MOVEMENT_SPEED_DIFFERENCE_INTERVAL','vehicle_id':vid,
            'acceleration_interval_m_s2':[low,high],'limit_m_s2':limit,'scope':'POSTRUN_DT1_TERMINAL_JOIN_NOT_ONLINE_GLOBAL_SAFETY'}

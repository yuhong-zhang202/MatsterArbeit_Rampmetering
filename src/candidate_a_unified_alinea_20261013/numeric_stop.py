"""Explicitly approved, narrow source-compatible event; not unique branch proof.

Real acceleration and the legacy strict FAIL remain unchanged. No global
tolerance is enlarged. All missing/mismatched evidence returns STOP.
"""
import math
import re

EPS_DISTANCE_M = 0.001  # pinned config.h.cmake:230 / MSCFModel.cpp:851
POSITION_EPS_M = 0.1
DEFAULT_MAJOR_STOP_OFFSET_M = 1.0  # pinned MSVehicle.cpp:125
TOL = 1e-6  # unchanged numerical comparison tolerance, not new braking ceiling
STORAGE = 'ramp_storage_0'
LENGTH = 204.49
ROUTE = ('urban_in','shared_approach','ramp_storage','ramp_accel','merge_section','main_down')
DYNAMICS = {'accel':2.6,'decel':4.5,'emergency_decel':9.,'tau':1.,'action_step':1.,
            'sigma':.5,'max_speed':55.55555555555556,'min_gap':2.5}


def read_vehicle_state(conn, vid, t):
    need(conn.simulation.getTime()==t and vid in conn.vehicle.getIDList(), 'NUMERIC_STATE_ID_TIME_UNKNOWN')
    getters={'accel':'getAccel','decel':'getDecel','emergency_decel':'getEmergencyDecel',
        'tau':'getTau','action_step':'getActionStepLength','sigma':'getImperfection',
        'max_speed':'getMaxSpeed','min_gap':'getMinGap'}
    result=dict(vehicle_id=vid,time_s=t,lane_id=conn.vehicle.getLaneID(vid),
        type_id=conn.vehicle.getTypeID(vid),route=list(conn.vehicle.getRoute(vid)),
        speed_mode=conn.vehicle.getSpeedMode(vid),lane_change_mode=conn.vehicle.getLaneChangeMode(vid),
        speed_m_s=conn.vehicle.getSpeed(vid),position_m=conn.vehicle.getLanePosition(vid),
        length_m=conn.vehicle.getLength(vid),
        dynamics={k:getattr(conn.vehicle,v)(vid) for k,v in getters.items()})
    need(conn.simulation.getTime()==t, 'NUMERIC_STATE_TIME_DRIFT')
    return result


def finite(x):return type(x) in (int,float) and math.isfinite(x)
def need(ok, reason):
    if not ok:raise ValueError(reason)


def classify(evidence, authority):
    result={'decision':'STOP','classification':'NOT_SOURCE_BOUND_NUMERICAL_EVENT',
        'actual_branch_identified':False,'native_safety_proven':False,
        'legacy_strict_FAIL_retained':True,'evidence':evidence,'reason':''}
    try:
        need(isinstance(authority,dict) and authority.get('enabled') is True and
            isinstance(authority.get('approval_sha256'),str) and
            re.fullmatch('[0-9a-f]{64}',authority['approval_sha256']) and authority.get('source_commit')==
            'fa7df22d7f1c4ae245192ecc32410a49f1ffb2a3', 'NUMERICAL_EXCEPTION_NOT_AUTHORIZED')
        need(authority.get('actual_branch_identified') is False and
            authority.get('configured_model')=='Krauss' and
            type(authority.get('configured_Euler_dt_s')) is int and authority['configured_Euler_dt_s']==1 and
            authority.get('no_model_or_JM_override') is True, 'UNKNOWN_DECLARED_SOURCE_REFERENCE')
        e=evidence;vid=e['vehicle_id'];before=e['before'];after=e['after']
        need(e['run_id']==authority['run_id'] and e['mode']==authority['mode'] and
            e['mode'] in ('fixed300','fixed750','dynamic_commands','real_alinea') and
            isinstance(e['execution_card_sha256'],str) and re.fullmatch('[0-9a-f]{64}',e['execution_card_sha256']) and
            e['execution_card_sha256']==authority['execution_card_sha256'], 'UNBOUND_NUMERIC_RUN_CARD_MODE')
        need(isinstance(vid,str) and vid.startswith('R_flow.') and
            before['vehicle_id']==after['vehicle_id']==vid, 'UNBOUND_NUMERIC_VEHICLE_ID')
        need(type(e['time_begin_s']) is int and type(e['time_end_s']) is int and
            e['time_begin_s']>=1200 and e['time_end_s']==e['time_begin_s']+1 and
            before['time_s']==e['time_begin_s'] and after['time_s']==e['time_end_s'] and
            type(e['dt_s']) is int and e['dt_s']==1, 'UNKNOWN_NUMERIC_TIME_OR_UNITS')
        need(e['motion']=='y' and type(e['first_yellow_begin_s']) is int and e['first_yellow_begin_s']==e['time_begin_s'] and
            e['post_signal_binding_status']=='BOUND_BEFORE_LEDGER' and
            type(e['actual_phase']) is int and e['actual_phase']==1 and e['actual_state']=='y' and
            isinstance(e['actual_program'],str) and e['actual_program']==e['expected_program'] and
            re.fullmatch(r'I12_PACKET(?:[89]|1[0-9]|2[0-4])',e['actual_program']) and
            e['controlled_links']==[[['ramp_storage_0','ramp_accel_0',':ramp_mid_0_0']]],
            'UNKNOWN_NUMERIC_PHASE_OR_LINK')
        for x in (before,after):
            need(x['lane_id']==STORAGE and x['type_id']=='technical_passenger' and
                tuple(x['route'])==ROUTE and type(x['speed_mode']) is int and x['speed_mode']==31 and
                type(x['lane_change_mode']) is int and x['lane_change_mode']==1621,
                'UNKNOWN_NUMERIC_MODEL_OR_MODES')
            need(set(x['dynamics'])==set(DYNAMICS) and all(finite(x['dynamics'][k]) and
                abs(x['dynamics'][k]-v)<=1e-8 for k,v in DYNAMICS.items()), 'NUMERIC_DYNAMICS_MISMATCH')
            need(all(finite(x[k]) for k in ('position_m','speed_m_s','length_m')) and
                0<=x['position_m']<LENGTH and x['speed_m_s']>=0 and abs(x['length_m']-5.)<=1e-8,
                'UNKNOWN_NUMERIC_POSITION_OR_BODY')
        need(abs(before['length_m']-after['length_m'])<=1e-8 and
            abs(after['position_m']-before['position_m']-after['speed_m_s'])<=TOL,
            'NUMERIC_EULER_POSITION_MISMATCH')
        need(e['full_before_after_world_binding'] is True and e['entered_link'] is False and
            e['body_coverage_complete'] is True and
            e['before_current_gap_status'] in ('CURRENT_GAP_OBSERVED_WITHIN_BOUND','CLEAR_WITHIN_OBSERVED_LOOKAHEAD') and
            e['after_current_gap_status'] in ('CURRENT_GAP_OBSERVED_WITHIN_BOUND','CLEAR_WITHIN_OBSERVED_LOOKAHEAD'),
            'UNKNOWN_NUMERIC_COVERAGE_OR_CURRENT_GAP')
        need(all(type(x) is int and x==0 for x in e['native_event_counters'].values()) and
            set(e['native_event_counters'])=={'colliding_vehicles','starting_teleports','ending_teleports'} and
            e['native_warning_observed'] is False, 'NUMERIC_EVENT_COEXISTING_NATIVE_ALARM')
        v=before['speed_m_s'];decel=before['dynamics']['decel'];seen=LENGTH-before['position_m']
        need(decel+EPS_DISTANCE_M<v<2*decel, 'OUTSIDE_ONE_STEP_STOP_REFERENCE_DOMAIN')
        brake_gap=v-decel  # zero-headway Euler brakeGap, one braking step, dt1
        offset=seen-brake_gap
        need(POSITION_EPS_M<=offset<=DEFAULT_MAJOR_STOP_OFFSET_M,
            'UNKNOWN_DEFAULT_STOP_OFFSET_SATURATION_CONDITION')
        # This is a configuration/source-compatible conditional reference, not
        # an assertion that private stopDist/majorStopOffset were observed.
        g=brake_gap-EPS_DISTANCE_M;b=decel;t=1.;s=1.
        n=math.floor(.5-((t+math.sqrt(s*s+4*(s*(2*g/b-t)+t*t))*(-.5))/s))
        h=.5*n*(n-1)*b*s+n*b*t
        expected=n*b+(g-h)/(n*s+t)
        delta=after['speed_m_s']-v;alpha=e['actual_native_acceleration_m_s2']
        need(finite(alpha) and finite(e['recorded_delta_v_m_s2']) and
            abs(delta-e['recorded_delta_v_m_s2'])<=TOL and abs(delta-alpha)<=TOL,
            'NUMERIC_DELTA_ALPHA_BINDING_MISMATCH')
        need(abs(expected-after['speed_m_s'])<=TOL and
            abs((expected-v)-alpha)<=TOL, 'NOT_EXACT_SOURCE_FORMULA_MATCH')
        need(delta < -decel-TOL and alpha < -decel-TOL, 'NOT_A_LEGACY_BRAKING_FAILURE')
        result.update(decision='CONTINUE_RESTRICTED_NUMERICAL_EVENT',
            classification='SOURCE_COMPATIBLE_NUMERICAL_STOP_EVENT',
            observed_delta_v_m_s2=delta, observed_native_acceleration_m_s2=alpha,
            nominal_normal_decel_m_s2=decel, distance_margin_m=EPS_DISTANCE_M,
            source_reference={'brake_gap_m':brake_gap,'conditional_capped_offset_m':offset,
                'stop_gap_minus_epsilon_m':g,'n':n,'h':h,'predicted_speed_m_s':expected,
                'counterfactual_without_distance_margin_alpha_m_s2':-decel,
                'private_offset_observed':False,'model_from_bound_configuration_not_private_trace':True},
            approval_sha256=authority['approval_sha256'], reason='EXACT_BOUND_SOURCE_COMPATIBLE_EVENT_ONLY')
    except (KeyError,TypeError,ValueError,OverflowError) as exc:
        result['reason']=type(exc).__name__+':'+str(exc)
    return result

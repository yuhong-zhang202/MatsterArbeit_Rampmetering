"""Independent approved-event decoding; original measured alarms stay visible."""
import math
from scripts.unified_alinea_audit_20261013_v1.core import need,number,near
ROUTE=['urban_in','shared_approach','ramp_storage','ramp_accel','merge_section','main_down']
DYN={'accel':2.6,'decel':4.5,'emergency_decel':9.,'tau':1.,'action_step':1.,'sigma':.5,'max_speed':55.55555555555556,'min_gap':2.5}
def validate_formula(e,a):
    need(a.get('enabled') is True and a.get('source_commit')=='fa7df22d7f1c4ae245192ecc32410a49f1ffb2a3' and a.get('configured_model')=='Krauss' and type(a.get('configured_Euler_dt_s')) is int and a['configured_Euler_dt_s']==1 and a.get('no_model_or_JM_override') is True and a.get('actual_branch_identified') is False,'UNKNOWN_NUMERICAL_AUTHORITY')
    need(e['run_id']==a['run_id'] and e['mode']==a['mode'] and e['execution_card_sha256']==a['execution_card_sha256'],'NUMERICAL_RUN_CARD_MODE')
    t=e['time_begin_s'];vid=e['vehicle_id'];x=e['before'];z=e['after']
    need(type(t) is int and t>=1200 and type(e['time_end_s']) is int and e['time_end_s']==t+1 and type(e['dt_s']) is int and e['dt_s']==1,'NUMERICAL_INTERVAL')
    need(e['motion']=='y' and type(e['actual_phase']) is int and e['actual_phase']==1 and e['actual_state']=='y' and type(e['first_yellow_begin_s']) is int and e['first_yellow_begin_s']==t and e['actual_program']==e['expected_program'] and e['post_signal_binding_status']=='BOUND_BEFORE_LEDGER' and e['controlled_links']==[[['ramp_storage_0','ramp_accel_0',':ramp_mid_0_0']]],'NUMERICAL_FIRST_YELLOW')
    for state,time in [(x,t),(z,t+1)]:
        need(state['vehicle_id']==vid and isinstance(vid,str) and vid.startswith('R_flow.') and type(state['time_s']) in (int,float) and state['time_s']==time and state['lane_id']=='ramp_storage_0' and state['type_id']=='technical_passenger' and state['route']==ROUTE,'NUMERICAL_STATE_BINDING')
        need(type(state['speed_mode']) is int and state['speed_mode']==31 and type(state['lane_change_mode']) is int and state['lane_change_mode']==1621 and set(state['dynamics'])==set(DYN) and all(near(state['dynamics'][k],v) for k,v in DYN.items()),'NUMERICAL_MODEL_MODES_DYNAMICS')
        need(all(number(state[k]) for k in ('position_m','speed_m_s','length_m')) and 0<=state['position_m']<204.49 and state['speed_m_s']>=0 and near(state['length_m'],5),'NUMERICAL_POSITION_BODY')
    need(abs(z['position_m']-x['position_m']-z['speed_m_s'])<=1e-6,'NUMERICAL_EULER_POSITION')
    need(e['full_before_after_world_binding'] is True and e['entered_link'] is False and e['body_coverage_complete'] is True and e['native_warning_observed'] is False,'NUMERICAL_WORLD_BODY_WARNING')
    need(set(e['native_event_counters'])=={'colliding_vehicles','starting_teleports','ending_teleports'} and all(type(v) is int and v==0 for v in e['native_event_counters'].values()),'NUMERICAL_COEXISTING_NATIVE_EVENT')
    need(all(e[k] in ('CURRENT_GAP_OBSERVED_WITHIN_BOUND','CLEAR_WITHIN_OBSERVED_LOOKAHEAD') for k in ('before_current_gap_status','after_current_gap_status')),'NUMERICAL_GAP_DENIED_OR_UNKNOWN')
    v=x['speed_m_s'];need(4.501<v<9,'NUMERICAL_REFERENCE_DOMAIN');gap=v-4.5;offset=204.49-x['position_m']-gap;need(.1<=offset<=1,'NUMERICAL_DECLARED_OFFSET_DOMAIN')
    g=gap-.001;n=math.floor(-.5+.5*math.sqrt(1+8*g/4.5));h=.5*n*(n-1)*4.5+n*4.5;pred=n*4.5+(g-h)/(n+1);dv=z['speed_m_s']-v
    need(number(e['actual_native_acceleration_m_s2']) and number(e['recorded_delta_v_m_s2']) and dv< -4.5-1e-6 and abs(dv-e['recorded_delta_v_m_s2'])<=1e-6 and abs(dv-e['actual_native_acceleration_m_s2'])<=1e-6 and abs(pred-z['speed_m_s'])<=1e-6,'NUMERICAL_FORMULA_ACTUAL_MISMATCH')
    return {'vehicle_id':vid,'BEGIN':t,'ACK':t+1,'actual_delta_v_m_s2':dv,'actual_native_acceleration_m_s2':e['actual_native_acceleration_m_s2'],'independent_reference_speed_m_s':pred,'legacy_strict_FAIL':True,'approved_source_compatible_classification':True,'private_branch_observed':False,'native_safety_proven':False}

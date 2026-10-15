"""Exact follow-up scope and terminal supports; never a runtime authorization."""
from scripts.cumulative_full_catalogue_audit_20261014_v1.core import need
MODES={'UA_CUMULATIVE_FULL_DYNAMIC_S17_01':'dynamic_commands','UA_CUMULATIVE_FULL_ALINEA_S17_01':'real_alinea'}
COMPLETE='PACKET_CYCLES_OBSERVED_NO_MONITORED_ANOMALY_NOT_QUALIFIED'
PARTIAL='APPROVED_END_PARTIAL_OR_BODY_CENSORED_NOT_QUALIFIED'
def check_card_scope(card):
    s=card['spec'];run=s['run_id'];mode=s['mode']
    need(run in MODES and MODES[run]==mode,'EXACT_FOLLOWUP_ID_MODE')
    need(card['classification']=='OFFLINE_CUMULATIVE_TRACKING_NOT_NATIVE_AUTHORIZED' and s['end_s']==1296 and s['activation_s']==1200 and s['step_s']==1 and s['seed']==17,'EXACT_FOLLOWUP_CLOCK')
    expected={str(t):([5,3,2] if t==10 else [4,min(5,t-6),t-4-min(5,t-6)]) for t in range(8,25)}
    need(s['phase_durations_s']==expected and s['catalogue_periods_s']==list(range(8,25)) and s['scheduler']=='ACTUAL_C_MINUS_N_BOUNDARY_ONLY','UNCHANGED_FULL_CATALOGUE')
    need(card['numerical_exception_authority']['enabled'] is False,'STRICT_NUM_NO_EXTENSION')
    need(s.get('terminal_partial_allowed') is True and s.get('initial_command_veh_h')==(300 if mode=='dynamic_commands' else 900),'EXACT_MODE_INITIAL_AND_PARTIAL')
    schedule={'1200':300,'1201':750,'1226':900,'1237':300}
    feedback={'target_percent':11,'gain_veh_h_per_percentage_point':70,'bounds_veh_h':[300,900],'initial_veh_h':900,'sample_s':30,'global_activation_s':1200,'logical_activation_s':600,'detector_ids':['p1_main_down_20_l0','p1_main_down_20_l1'],'lanes':['main_down_0','main_down_1'],'position_m':20}
    need(s.get('request_schedule')==(schedule if mode=='dynamic_commands' else None) and s.get('Feedback')==(feedback if mode=='real_alinea' else None),'EXACT_SCHEDULE_OR_FEEDBACK_REFERENCE')
    need(s.get('input_origin')==('PROJECT_FEEDBACK' if mode=='real_alinea' else mode) and s.get('requested_schedule')==s['request_schedule'] and s.get('partial_final_cycle_allowed') is True,'MODE_METADATA_ALIASES')
    return mode

def terminal_scope(receipt,last,end,account,censored):
    need(type(last) is int and type(end) is int and 0<=last<=end,'TERMINAL_CLOCK')
    cycles=account.get('cycles',[]);partial=bool(cycles and not cycles[-1]['completed']);status=receipt.get('status');normal=status in (COMPLETE,PARTIAL)
    if normal:
        need(last==end and not receipt.get('error'),'EARLY_STOP_NOT_APPROVED_TERMINAL_PARTIAL')
        need(account.get('observed_end_s')==end and account.get('planned_end_observed') is True,'TERMINAL_ACCOUNTING_SUPPORT')
        need((status==PARTIAL)==(partial or bool(censored)),'TERMINAL_PARTIAL_CENSOR_CLASSIFICATION')
    return {'runtime_stop':not normal,'approved_horizon_observed':last==end,'partial_cycle':partial,'body_censored_ids':sorted(censored),'whole_window_C_N_support':'ALL_OBSERVED_ACK_INTERVALS_ENTRIES','E_support':'COMPLETE_PACKETS_ONLY','completed_packets_service_mismatches':[{'begin_s':c['begin_s'],'N':c['N'],'E':c['E']} for c in cycles if c['completed'] and c['N']!=2],'terminal_partial_is_service_qualification':False,'outside_observed_window_N':None,'outside_observed_window_E':None}

def resource_alarms(card,elapsed,charged_before,raw_bytes):
    """Separate single-run cleanup cost from two-identity accumulated cost."""
    from scripts.cumulative_full_catalogue_audit_20261014_v1.core import number
    need(number(elapsed) and elapsed>=0 and number(charged_before) and charged_before>=0,'MONITORED_COST_OR_HISTORY_UNKNOWN')
    single=card['resources']['wall_limit_s'];combined=card['spec']['combined_resource_envelope']['monitored_s']
    need(number(single) and single>0 and number(combined) and combined>=single,'RESOURCE_LIMIT_SCHEMA')
    if elapsed>single or charged_before+elapsed>combined:
        return [{'kind':'RESOURCE_CAP_OBSERVED_EXCEEDED','monitored_s':elapsed,'raw_bytes':raw_bytes,'single_limit_s':single,'charged_before_s':charged_before,'combined_monitored_s':charged_before+elapsed,'combined_limit_s':combined}]
    return []

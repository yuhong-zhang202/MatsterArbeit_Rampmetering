"""Small support-schema companion; original V6 result remains immutable."""
import pathlib,json,csv,hashlib
from fractions import Fraction
ROOT=pathlib.Path.cwd();OUT=ROOT/'data/processed/cumulative_full_catalogue_followup_20261014_v1/native_dynamic_v3';RAW=ROOT/'data/raw/cumulative_full_catalogue_followup_20261014_v1/UA_CUMULATIVE_FULL_DYNAMIC_S17_01/outputs';ENG=ROOT/'artifacts/cumulative_full_catalogue_followup_20261014_v1/engineering/native_execution_v2/UA_CUMULATIVE_FULL_DYNAMIC_S17_01'
d=json.loads((OUT/'PHYSICAL_PREFIX_RESULTS_V6.json').read_text());f=json.loads((RAW/'failure_snapshot.json').read_text());row=f['retained_last_observation'][-1];q=row['post_native_receiver_decision']['current_query'] if 'current_query' in row['post_native_receiver_decision'] else None
if q is None:
 # The exact retained query is serialized in the receiver record.
 q=row['post_receiver'].get('current_query')
if q is None:
 # Find the already bound actual-state query without using derived engineering numbers.
 def find(x):
  if isinstance(x,dict):
   if x.get('vehicle_id')=='R_flow.5' and x.get('time_s')==1233 and 'getSecureGap_args' in x:return x
   for v in x.values():
    z=find(v)
    if z:return z
  elif isinstance(x,list):
   for v in x:
    z=find(v)
    if z:return z
 q=find(row)
assert q is not None
args=q['getSecureGap_args'];gap=q['gap_excluding_minGap_m'];secure=q['actual_secure_gap_m'];margin=q['margin_m'];shortfall=secure+margin-gap
assert args['vehID']==q['vehicle_id']=='R_flow.5' and args['leaderID']==q['leader_id']=='R_flow.4' and args['speed']==q['actual_speed_m_s'] and args['leaderSpeed']==q['leader_speed_m_s'] and args['leaderMaxDecel']==9 and margin==1.1 and shortfall>0
bridge=json.loads((RAW/'bridge_receipt.json').read_text());before=bridge['total_budget_before_run'];elapsed=d['monitored_elapsed_s'];assert before['charged_monitored_s']==0 and elapsed<300 and elapsed+before['charged_monitored_s']<600 and d['log_EOF_verified']
cycles=[]
for c in d['accounting']['cycles']:
 exposure=c['phase_exposure_s'];cycles.append({'begin_s':c['begin_s'],'planned_end_s':c['end_s'],'period_s':c['period_s'],'completed':c['completed'],'observed_phase_exposure_s':exposure,'N_total_observed':c['N'],'N_G_observed':c['N_G'] if exposure['G'] else None,'N_y_observed':c['N_y'] if exposure['y'] else None,'N_r_observed':c['N_r'] if exposure['r'] else None,'E_complete_packet_counter':c['E'],'partial_quota_service_observation':None if not c['completed'] else c['N'],'raw_application_ACK_scope':'UNKNOWN' if c['begin_s']==1232 else 'OBSERVED'})
summary={'status':'BOUNDED_OBSERVED_PHYSICAL_PREFIX_WITH_RAW_ACK_EVENT_UNKNOWN_AND_GUARD_STOP','C_original_fraction':str(Fraction(300+25*750+7*900,3600)),'C_applied_physical_fraction':str(Fraction(300*24+900*9,3600)),'E_complete':4,'N_all_observed':5,'differences_exact':{'C_minus_E':str(Fraction(73,24)),'E_minus_N':-1,'C_minus_N':str(Fraction(49,24))},'complete_cycles':2,'partial_cycles':1,'cycles':cycles,'future_300_at1237':'NOT_OBSERVED_NOT_REQUESTED','real_Feedback':'NOT_RUN','unobserved_after1233':{'C_observed':None,'E':None,'N':None},'900_application':'DERIVED_PHYSICAL_FIRST_G_ACK1233_NOT_RAW_COMMAND_ACK','raw_missing_events':['PACKET_ACK_OBSERVED at1232','ACK_OBSERVED scheduled:1226 at1232'],'gap':{'raw_query':q,'required_m':secure+margin,'actual_gap_excluding_minGap_m':gap,'shortfall_m':shortfall,'entry_R4_following':row['actual_entry_following'],'native_collision_proven':False},'body_censored':['R_flow.4'],'normal_terminal_arrivals_count':len(d['terminal_results']),'normal_terminal_all_PASS':all(x['status']=='PASS' for x in d['terminal_results']),'currentY5_formula_reproduction':d['current_Y5_formula_results'],'budget':{'monitored_elapsed_s':elapsed,'single_limit_s':300,'aggregate_limit_s':600,'charged_before_s':before['charged_monitored_s'],'aggregate_actual_s':before['charged_monitored_s']+elapsed,'remaining600_s_if_actualsettled':600-before['charged_monitored_s']-elapsed,'raw_bytes':d['raw_bytes'],'log_EOF_verified':True,'data_recommendation':'ACTUAL_TIME_AND_RAW_COST_DEFENSIBLY_SETTLE_AFTER_SCIENCE; TRAFFIC_EVENT_CHAIN_REMAINS_UNKNOWN; NOT_RELEASE_NEXT_RUN','settled_by_data_agent':False}}
with (OUT/'OBSERVATION_SUPPORT_MAP_V1.json').open('x') as h:json.dump(summary,h,indent=2);h.write('\n')
with (OUT/'PREFIX_CYCLES_SUPPORT_V1.csv').open('x',newline='') as h:
 w=csv.DictWriter(h,fieldnames=['begin_s','planned_end_s','period_s','completed','G_s','y_s','r_s','N_G_observed','N_y_observed','N_r_observed','N_total_observed','E_complete_packet_counter','raw_application_ACK_scope']);w.writeheader()
 for c in cycles:
  e=c['observed_phase_exposure_s'];w.writerow({k:v for k,v in c.items() if k in w.fieldnames}|{'G_s':e['G'],'y_s':e['y'],'r_s':e['r']})
print('BOUNDED_SUPPORT_MAP_PASS',shortfall,'terminal',len(d['terminal_results']),'elapsed',elapsed)

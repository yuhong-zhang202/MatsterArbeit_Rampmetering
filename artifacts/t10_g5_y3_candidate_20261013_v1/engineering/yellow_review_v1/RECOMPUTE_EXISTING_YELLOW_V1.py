"""Bounded historical guard computation; no native import/launch or runtime edit."""
from pathlib import Path
from dataclasses import asdict
import json,hashlib,time
from src.candidate_a_unified_alinea_20261013.policy import yellow_scope
from src.candidate_a_qualification_20261008.safety import Vehicle
ROOT=Path(__file__).resolve().parents[4]
TASK=ROOT/'artifacts/t10_g5_y3_candidate_20261013_v1/engineering/yellow_review_v1'
OUT=ROOT/'data/processed/t10_g5_y3_candidate_20261013_v1/engineering_yellow_v1'
RAW=ROOT/'data/raw/unified_alinea_actuator_20261013_v1/UA_FIXED750_S17_02/outputs'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def new(p,v):
 p.parent.mkdir(parents=True,exist_ok=True)
 with p.open('x') as f:json.dump(v,f,indent=2,ensure_ascii=False,allow_nan=False);f.write('\n')

def main():
 start=time.monotonic();times=[1204+10*i for i in range(7)];snapshots={}
 for line in(RAW/'pre_steps.jsonl').open():
  r=json.loads(line)
  if r['time_s'] in times:snapshots[r['time_s']]=r['bound_snapshot']
 actual_entries={i:[] for i in range(7)};body_clears={}
 for line in(RAW/'post_steps.jsonl').open():
  r=json.loads(line)
  if 1200<=r['time_begin_s']<1270:
   for e in r['actual_crossings']:actual_entries[e['cycle_id']].append(e)
   for e in r['body_observation']['rows']:
    if e['status']=='REAR_CLEAR_OBSERVED':body_clears[e['vehicle_id']]=e['first_actual_rear_clear_ACK_s']
 rows=[]
 for i,t in enumerate(times):
  s=snapshots[t];v=[Vehicle(**x) for x in s['vehicle_states']]
  original=yellow_scope(v,t,4);recomputed=yellow_scope(v,t,3)
  assert original==s['yellow_scope'] and s['motion']=='y'
  assert recomputed['covered_ids']==sorted(set(s['storage'])|{x.vehicle_id for x in v if x.population=='ingress'})
  assert all(s['world'][x.vehicle_id]['role']=='R' and abs(s['world'][x.vehicle_id]['speed_m_s']-x.speed_m_s)<1e-8 for x in v)
  rows.append({'cycle_id':i,'actual_G4_yellow_begin_s':t,'actual_bound_vehicle_states':[asdict(x) for x in v],
   'original_observed_Y4_scope':original,'recomputed_Y3_on_OLD_G4_population':recomputed,
   'actual_G5_population_observed':False,'Y3_native_observed':False,
   'actual_old_body_clear_ACKs':{x['vehicle_id']:body_clears[x['vehicle_id']] for x in actual_entries[i]},
   'hypothetical_Y3_red_begin_on_old_same_Gclose_s':t+3,
   'old_entrant_body_cleared_before_hypothetical_Y3_red':all(body_clears[x['vehicle_id']]<=t+3 for x in actual_entries[i]),
   'native_branch_or_future_feasibility_proven':False})
 boundary=[]
 for name,speed,distance in [('fast_near_line',16.,1.),('current_low_speed',4.,.1),('moderate_near_line',10.,3.)]:
  v=Vehicle('R_BOUNDARY_SYNTHETIC','storage',204.49-distance,speed,5.,2.5,2.6,4.5,1.,1.,'technical_passenger')
  four=yellow_scope([v],1200,4);three=yellow_scope([v],1200,3)
  boundary.append({'name':name,'classification':'SYNTHETIC_LOGIC_ILLUSTRATION_NOT_NATIVE_EVIDENCE','input':asdict(v),'Y4':four,'Y3':three})
 assert boundary[0]['Y4']['status']=='PASS' and boundary[0]['Y3']['status']=='UNKNOWN'
 assert all(x['Y3']['status']=='PASS' for x in boundary[1:])
 new(OUT/'SEVEN_OLD_POPULATIONS_Y3_RECOMPUTE_V1.json',{'run_id':'UA_FIXED750_S17_02','status':'HISTORICAL_SCOPE_COMPATIBILITY_ONLY','rows':rows,
 'G5_future_population':'NOT_OBSERVED','native_Y3_safety':'NOT_VERIFIED','old_frozen_manifest':'artifacts/unified_alinea_actuator_20261013_v1/engineering/runs/UA_FIXED750_S17_02/RAW_FINAL_SHA256_V1.json'})
 new(OUT/'GUARD_BOUNDARY_ILLUSTRATIONS_V1.json',{'examples':boundary,'screen_margin_not_changed':True,'rule':'Same original yellow_scope; duration changes4→3 for computation only; any UNKNOWN must STOP before yellow motion'})
 reference=ROOT/'artifacts/candidate_a_a1_contract_20261011_v1/engineering/SOURCE_RECEIPT.json';rs=json.loads(reference.read_text());sources=[]
 for name in ['src/microsim/MSVehicle.cpp','src/microsim/cfmodels/MSCFModel.cpp','src/microsim/cfmodels/MSCFModel_Krauss.cpp']:
  ref=next(x for x in rs['sources'] if x['path']==name);cached=Path('/private/tmp/issue8_sumo_sources')/name
  assert sha(cached)==ref['sha256'];sources.append(ref)
 card=json.loads((RAW/'card.json').read_text());checks={}
 for name in ['src/candidate_a_unified_alinea_20261013/policy.py','src/candidate_a_unified_alinea_20261013/adapter.py','src/candidate_a_unified_alinea_20261013/bridge.py','src/candidate_a_unified_alinea_20261013/profile.py','src/candidate_a_unified_alinea_20261013/numeric_stop.py','src/candidate_a_issue12_packet_policy_20261012/body.py']:
  observed=sha(ROOT/name);assert observed==card['sources_sha256'][name];checks[name]=observed
 new(TASK/'ENGINEERING_RECOMPUTE_RECEIPT_V1.json',{'status':'PASS_BOUNDED_HISTORICAL_COMPUTATION','command':'.venv/bin/python '+str(Path(__file__).relative_to(ROOT)),
 'old_scopes':len(rows),'old_Y3_scope_PASS':sum(x['recomputed_Y3_on_OLD_G4_population']['status']=='PASS' for x in rows),
 'covered_old_snapshot_rows':sum(len(x['actual_bound_vehicle_states']) for x in rows),'scope_full_identity_world_population_binding_checked':True,
 'old_body_compatible_same_Gclose_cases':sum(x['old_entrant_body_cleared_before_hypothetical_Y3_red'] for x in rows),
 'proposed_new_G5_state_verified':False,'proposed_Y3_native_safe':False,'source_baseline_preserved':checks,'pinned_official_sources':sources,
 'derived_files':{str(p.relative_to(ROOT)):sha(p) for p in OUT.glob('*.json')},
 'selected_boundary_illustrations':3,'new_simulations':0,'runtime_edits':False,'regression_suite_run':False,'elapsed_s':time.monotonic()-start})
 print(json.dumps({'old_scopes':7,'scope_PASS':[x['recomputed_Y3_on_OLD_G4_population']['status'] for x in rows],'rows':sum(len(x['actual_bound_vehicle_states']) for x in rows),
 'max_old_speeds':[max(x.speed_m_s for x in [Vehicle(**v) for v in row['actual_bound_vehicle_states']]) for row in rows],
 'max_actual_old_clear_ACK_relative_to_yellow_start':[max(row['actual_old_body_clear_ACKs'].values())-row['actual_G4_yellow_begin_s'] for row in rows],
 'receipt_sha256':sha(TASK/'ENGINEERING_RECOMPUTE_RECEIPT_V1.json')},ensure_ascii=False))
if __name__=='__main__':main()

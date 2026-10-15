"""Independent algebra and old-population joins; no runtime imports/SUMO."""
from pathlib import Path
import json,math,hashlib
ROOT=Path(__file__).resolve().parents[4]
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def need(ok,msg):
 if not ok:raise ValueError(msg)
def screen(s,Y):
 p=s['position_m'];v=s['speed_m_s'];l=s['length_m'];b=s['normal_decel_m_s2'];a=s['action_step_s'];need(all(type(x) in (int,float) and math.isfinite(x) for x in (p,v,l,b,a)) and v>=0 and l>0 and b>0 and a>0,'SCREEN_VALID_VALUES');d=204.49-p;one=d>0 and v<=b*a;stop=d>0 and (one or d>=v*a+v*v/(2*b));time=None if v==0 else a+v/(2*b)+l/v;clear=v>0 and time<=Y and d+l<=v*(Y-a)
 return {'one_step':one,'stop':stop,'clear':clear,'PASS':stop or clear,'distance_m':d,'time_screen_s':time}
def main():
 eng=ROOT/'artifacts/t10_g5_y3_candidate_20261013_v1/engineering/yellow_review_v1';der=ROOT/'data/processed/t10_g5_y3_candidate_20261013_v1/engineering_yellow_v1';binding=json.loads((eng/'ENGINEERING_DELIVERY_BINDING_V1.json').read_text());need(sha(eng/'ENGINEERING_DELIVERY_BINDING_V1.json')=='9858c3ddcf40ea87032b7e0968249318a3bcc6520ae55712b8488888d5c6e917','BINDER_ID')
 for name,h in binding['files'].items():need(sha(ROOT/name)==(h['sha256'] if isinstance(h,dict) else h),'ENGINEERING_FILE_SHA')
 old=json.loads((der/'SEVEN_OLD_POPULATIONS_Y3_RECOMPUTE_V1.json').read_text());synth=json.loads((der/'GUARD_BOUNDARY_ILLUSTRATIONS_V1.json').read_text());raw=ROOT/'data/raw/unified_alinea_actuator_20261013_v1/UA_FIXED750_S17_02/outputs';manifest=json.loads((ROOT/old['old_frozen_manifest']).read_text());prepath=raw/'pre_steps.jsonl';need(sha(prepath)==manifest['files'][str(prepath.relative_to(ROOT))],'RELEVANT_PRE_SHA')
 times={r['actual_G4_yellow_begin_s'] for r in old['rows']};pre={}
 for line in prepath.open():
  q=json.loads(line)
  if q['time_s'] in times:need(q['time_s'] not in pre,'DUP_SELECTED_FRAME');pre[q['time_s']]=q['bound_snapshot']
 prior=json.loads((ROOT/'data/processed/unified_alinea_actuator_20261013_v1/UA_FIXED750_S17_02/revision01/ACTUAL_NUMERIC_RESULTS_V2.json').read_text());rows=[];count=0
 for r in old['rows']:
  t=r['actual_G4_yellow_begin_s'];p=pre[t];states=r['actual_bound_vehicle_states'];need(states==p['vehicle_states'],'ACTUAL_OLD_POPULATION_JOIN');ids=[s['vehicle_id'] for s in states];need(len(ids)==len(set(ids)),'POPULATION_DUPLICATE')
  expect={v for v,w in p['world'].items() if w['lane_id'] in ('ramp_storage_0',':urban_diverge_1_0')};need(set(ids)==expect==set(p['storage'])|{s['vehicle_id'] for s in states if s['population']=='ingress'},'FULL_WORLD_STORAGE_INGRESS_COVERAGE')
  sc4=r['original_observed_Y4_scope'];sc3=r['recomputed_Y3_on_OLD_G4_population'];need(sc4==p['yellow_scope'] and set(sc4['covered_ids'])==expect and set(sc3['covered_ids'])==expect,'ORIGINAL_SCREEN_AND_IDS');maps=[{x['vehicle_id']:x for x in sc['rows']} for sc in (sc4,sc3)];stops=clears=0
  for s in states:
   vid=s['vehicle_id'];w=p['world'][vid];meta=p['terminal_before'][vid];offset=113.08 if s['population']=='ingress' else 0;need(abs(s['position_m']-(meta['position_m']-offset))<=1e-8 and abs(s['speed_m_s']-w['speed_m_s'])<=1e-8 and s['length_m']==meta['length_m'],'ACTUAL_INPUT_POSITION_SPEED_BODY')
   four=screen(s,4);three=screen(s,3)
   for actual,calc in zip(maps,(four,three)):
    x=actual[vid];need(x['stop_possible']==calc['stop'] and x['clear_possible']==calc['clear'] and x['one_step_Euler_stop_possible']==calc['one_step'],'INDEPENDENT_SCREEN_FORMULA')
   need(not three['PASS'] or four['PASS'],'SAME_INPUT_MONOTONICITY');need(three['PASS'],'OLD_Y3_SCREEN_UNKNOWN');stops+=three['stop'];clears+=not three['stop'] and three['clear'];count+=1
  bodies=r['actual_old_body_clear_ACKs'];need(all(prior['body_first_clear_ACK'][vid]==ack and ack<=t+3 for vid,ack in bodies.items()),'HISTORICAL_BODY_CLEAR_JOIN');rows.append({'old_G4_Y_begin_s':t,'old_snapshots':len(states),'Y4_reproduced':True,'Y3_same_population_PASS':True,'stop_possible_count':stops,'clear_only_count':clears,'old_max_speed_m_s':max(x['speed_m_s'] for x in states),'old_actual_body_first_clear_ACKs':bodies,'hypothetical_Y3_red_begin_s':t+3,'future_G5_population_observed':False,'native_Y3_verified':False})
 need(count==248 and len(rows)==7,'248_OLD_SNAPSHOT_SCOPE');boundary=[]
 for e in synth['examples']:
  x=e['input'];a=screen(x,4);b=screen(x,3);need(e['Y4']['status']==('PASS' if a['PASS'] else 'UNKNOWN') and e['Y3']['status']==('PASS' if b['PASS'] else 'UNKNOWN'),'SYNTHETIC_BOUNDARY_RECOMPUTE');boundary.append({'name':e['name'],'synthetic':True,'Y4':a,'Y3':b})
 need(boundary[0]['Y4']['PASS'] and not boundary[0]['Y3']['PASS'],'Y3_STRICTER_COUNTEREXAMPLE')
 oldcard=json.loads((raw/'card.json').read_text());need(len(oldcard['sources_sha256'])==64,'OLD64_SCOPE')
 for name,h in oldcard['sources_sha256'].items():need(sha(ROOT/name)==h,'OLD64_SOURCE_DRIFT')
 add=json.loads((eng/'BASE64_T8_PRESERVATION_V1.json').read_text());need(add['original_T8_phase_tuple']==[['G',4,1],['y',2,2],['r',2,0]],'T8_PRESERVATION')
 need(not(ROOT/'src/candidate_a_t10_g5_y3_20261013').exists(),'UNEXPECTED_IMPLEMENTATION_BEFORE_GATE')
 return {'verdict':'GO_FOR_CONDITIONAL_OFFLINE_PREP_ONLY','old_selected_frames':rows,'old_snapshot_count':count,'synthetic_boundaries':boundary,'unchanged_algebra_monotone_only_same_input':True,'old13_body_historical_compatibility_only':True,'old64_source_hashes_preserved':True,'T8_G4Y2R2_unchanged':True,'NUM_scope_pending_default_strict':True,'future_G5_or_Y3_native_not_observed':True,'native_runs':0,'tests_run':0,'full_raw_inventory_or_arrivals_reaudited':False}
if __name__=='__main__':print(json.dumps(main(),indent=2))

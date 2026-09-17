"""Compare registered products with independent raw reconstruction; no SUT imports."""
from pathlib import Path
import json,math,csv,hashlib
R=Path.cwd();B=R/'data/processed/stage6_obstacle_20260913_v1';D=B/'d2_data_review_revision_01';G=B/'d2_engineering_seed17_revision_01'
def js(p):return json.loads(Path(p).read_text())
def bind(p):return {'path':str(p),'sha256':hashlib.sha256(Path(p).read_bytes()).hexdigest()}
def save(n,v):
 with (D/n).open('x') as f:json.dump(v,f,indent=2,sort_keys=True,allow_nan=False)
comparisons=[]
def eq(a,b,path):
 if isinstance(a,(int,float)) and isinstance(b,(int,float)):assert math.isclose(a,b,rel_tol=1e-12,abs_tol=1e-10),(path,a,b)
 elif isinstance(a,dict):
  assert isinstance(b,dict) and set(a)==set(b),(path,set(a),set(b))
  for k in a:eq(a[k],b[k],path+'/'+str(k))
 elif isinstance(a,list):
  assert len(a)==len(b),(path,len(a),len(b))
  for i,(aa,bb) in enumerate(zip(a,b)):eq(aa,bb,path+'/'+str(i))
 else:assert a==b,(path,a,b)
 comparisons.append(path)
raw={c:js(D/(c+'_raw_oracle.json')) for c in ('ML','C')};ind=js(D/'independent_pair_and_sensitivities.json')
for c in ('ML','C'):
 actual=js(D/(f'S6_V1_{c}_S17_registered_analysis')/'measurements.json');oracle=raw[c]
 eq(oracle['FCD_sample_count'],actual['trajectory_sample_count'],c+'/sample_count')
 eq(oracle['endpoints'],actual['endpoints'],c+'/endpoints')
 eq(oracle['regional_stops'],actual['regional_stops'],c+'/regional_stops')
 eq(oracle['U_exposed_unique'],actual['descriptive_companions']['U_unique_exposed_count'],c+'/U_exposed_unique')
 for name,prod in [('feeder',actual['feeder_science_inputs']['cohort']),('common',actual['common_background_cohort'])]:
  eq({k:oracle[name][k] for k in ('records','bounds')},prod,c+'/'+name)
 inputs=actual['feeder_science_inputs']
 for k in ('certain_counts','r_counts','ru_labels'):eq(oracle[k],inputs[k],c+'/'+k)
 means=[math.fsum(b)/len(b) if b else None for b in inputs['bin_speeds']];eq(oracle['bin_means'],means,c+'/bin_means');eq(oracle['bin_speed_sample_counts'],[len(b) for b in inputs['bin_speeds']],c+'/bin_sample_counts')
 eq(oracle['inlet_pass'],actual['inlet']['scientific_result']=='supported_bounded',c+'/inlet')
 for detector,vals in oracle['e1'].items():
  for suffix,key in [('nVehEntered','entered_rate'),('nVehContrib','contrib_rate')]:
   prod=actual['e1'][detector]['e1_'+suffix+'_rate'];eq(vals[key],prod['rate_vehph'],c+'/'+detector+'/'+key);eq(vals['contributor_speed'],prod['speed']['value'],c+'/'+detector+'/'+suffix+'/speed')
prod_pair=js(D/'registered_fixed_rule_tables/pair_results.json')['17']
for k in ('S_REF_QUAL','S_M_INFLOW','M_PRIMARY','M_SUPPORT_blocks','R_SUPPORT_blocks','RU_SUPPORT_blocks','Q4_blocks','bin_speed_ratios','bin_certain_counts_minimum','scientific_result'):eq(ind['primary'][k],prod_pair[k],'pair/'+k)
rows=js(D/'registered_fixed_rule_tables/resolution_rule_results.json');sens=js(D/'registered_fixed_rule_tables/sensitivity_rule_results.json');keys=list(csv.DictReader((B/'b02_registered_rule_keys_revision_02.csv').open()))
assert (len(rows),sum(r['applicable']=='true' for r in rows),sum(r['required_for_resolution']=='true' for r in rows),sum(r['applicable']=='false' for r in rows))==(352,150,148,202)
assert len(sens)==14 and len({r['sensitivity_id'] for r in sens})==7
fieldkey=lambda r:tuple(r[k] for k in ('rule_id','version','condition','seed','window'))
assert {fieldkey(r) for r in rows}=={fieldkey(r) for r in keys}
required=[r for r in rows if r['seed']=='17' and r['required_for_resolution']=='true'];assert len(required)==74
expected_science={'M_PRIMARY':ind['primary']['M_PRIMARY'],'M_SUPPORT':bool(ind['primary']['M_SUPPORT_blocks']),'R_SUPPORT':bool(ind['primary']['R_SUPPORT_blocks']),'S_RU_EXPOSURE':bool(ind['primary']['RU_SUPPORT_blocks']),'Q4_COEXIST':bool(ind['primary']['Q4_blocks']),'S_REF_QUAL':ind['primary']['S_REF_QUAL']}
for r in required:
 if r['version']=='V1':
  expected=True if r['rule_id'].startswith('T_') else raw[r['condition']]['inlet_pass'] if r['rule_id']=='S_M_INFLOW' else expected_science[r['rule_id']]
  eq(r['result']=='supported_bounded',expected,'required/'+str(fieldkey(r)))
 elif r['rule_id']=='S_M_INFLOW':
  prior=js(D/(f"S6_V0_{r['condition']}_S17_registered_reuse_analysis")/'measurements.json');trip=prior['tripinfo'];expected=all(0<=v['depart']<1500 and v['departDelay']<=1.01 for vid,v in trip.items() if vid[0]=='M');eq(r['result']=='supported_bounded',expected,'reusedV0/inlet/'+r['condition'])
 else:eq(r['result'],'supported_bounded','reusedV0/qualified/'+str(fieldkey(r)))
for s in sens:
 if s['seed']=='17':eq(s['result'],ind[s['sensitivity_id']]['scientific_result'],'sensitivity/'+s['sensitivity_id'])
 else:assert s['result']=='not_evaluated' and s['value_state']=='missing_observation'
assert all(r['result']=='not_evaluated' and r['value_state']=='missing_observation' for r in rows if r['seed']=='23' and r['applicable']=='true')
assert all(r.get('value') is None for r in rows if r['value_state'] in ('missing_observation','not_paired','not_applicable'))
seed_sens=[r for r in sens if r['seed']=='17'];allpass=all(r['result']=='supported_bounded' for r in required+seed_sens)
aggregate=[]
for rule in sorted({r['rule_id'] for r in required}):
 rs=[r for r in required if r['rule_id']==rule];aggregate.append({'rule_id':rule,'required_seed17':len(rs),'pass':sum(r['result']=='supported_bounded' for r in rs),'fail':sum(r['result']=='not_resolved' for r in rs),'not_evaluated':sum(r['result']=='not_evaluated' for r in rs),'classification':'PASS' if all(r['result']=='supported_bounded' for r in rs) else 'FAIL'})
with (D/'seed17_required_gate_summary.csv').open('x',newline='') as f:w=csv.DictWriter(f,fieldnames=list(aggregate[0]));w.writeheader();w.writerows(aggregate)
with (D/'seed17_required_rule_details.csv').open('x',newline='') as f:
 cols=['rule_id','version','condition','seed','window','required_for_resolution','value_state','result'];w=csv.DictWriter(f,fieldnames=cols);w.writeheader();w.writerows({k:r[k] for k in cols} for r in required)
with (D/'seed17_sensitivity_summary.csv').open('x',newline='') as f:
 cols=['sensitivity_id','version','condition','seed','window','required_for_resolution','value_state','result'];w=csv.DictWriter(f,fieldnames=cols);w.writeheader();w.writerows({k:r[k] for k in cols} for r in seed_sens)
# Descriptive 20-bin table makes absent passage/support transparent.
bins=[]
for i in range(20):bins.append({'begin':300+60*i,'end':360+60*i,'ML_M_speed':raw['ML']['bin_means'][i],'C_M_speed':raw['C']['bin_means'][i],'speed_ratio':ind['primary']['bin_speed_ratios'][i],'ML_certain_M':raw['ML']['certain_counts'][i],'C_certain_M':raw['C']['certain_counts'][i],'C_R_certain_passages':raw['C']['r_counts'][i],'C_shared_RU_labels':raw['C']['ru_labels'][i]})
with (D/'seed17_registered_B_bins.csv').open('x',newline='') as f:w=csv.DictWriter(f,fieldnames=list(bins[0]));w.writeheader();w.writerows(bins)
card=js(B/'d1_engineering_smoke_revision_01/approved_launch_card.json');previous=None;events=[]
for i,path in enumerate(sorted(Path(card['budget_journal_directory']).glob('event_*.json'))):
 e=js(path);assert e['sequence']==i and e['previous']==previous;previous=bind(path);events.append(e)
attempts=events[-1]['state']['attempts'];budget={'SUMO_starts':len(attempts),'retry':sum(a['role']=='retry' for a in attempts),'validation':sum(a['role']=='validation' for a in attempts),'wallclock_s':sum(a['wallclock_s'] for a in attempts),'archive_bytes':sum(a['archive_bytes'] for a in attempts)}
assert budget['SUMO_starts']==4 and budget['retry']==1 and budget['validation']==2 and not (Path(card['budget_journal_directory'])/'first_matched_unit_acceptance.json').exists()
limitations=['All scientific statements are bounded exploratory registered outcomes, not formal standards or controller benefits.','Historical V0 ML17/C17 are exact registered reuse; they are not new independent repetitions. Their source identities and derived qualification were checked using the registered adapter.','Seed23 remains missing/not_evaluated; no seed is replaced and the global 352+14 denominator is unchanged.','Non-required V0 C17 shared-RU background row is preserved not_evaluated by the existing pipeline; it does not enter the74 required gate.','No real data censor or infinite TT upper occurred in these two registered B cohorts; null/unbounded handling remains registered and tested in prior C02/C04 evidence.','Full OS environment values are not exported; the documented process-only SUMO_HOME change/restoration provenance limit remains.']
summary={'data_integrity_review':'PASS','decision':'FAIL_STOP_NOT_RESOLVED','classification':'not_resolved','all_required_seed17_checks_pass':allpass,'confidence':'High','open_findings':{'Blocker':0,'Major':0,'Minor':0},'scientific_negative_is_not_a_software_defect':True,'independent_value_comparisons':len(comparisons),'new_V1_source_runs':2,'reused_historical_V0_runs':2,'main_fixed_denominators':{'total':352,'applicable':150,'required':148,'NA':202},'sensitivity_total':14,'seed17_main':{'required':74,'passed':sum(r['result']=='supported_bounded' for r in required),'not_resolved':sum(r['result']=='not_resolved' for r in required),'missing':sum(r['result']=='not_evaluated' for r in required)},'seed17_sensitivity':{'required':7,'passed':sum(r['result']=='supported_bounded' for r in seed_sens),'not_resolved':sum(r['result']=='not_resolved' for r in seed_sens)},'required_gate_summary':aggregate,'primary':ind['primary'],'ML_TT_bounds':raw['ML']['feeder']['bounds'],'C_TT_bounds':raw['C']['feeder']['bounds'],'Q1_R_context':{c:{'full_R_passages':len(raw[c]['r_passages']),'B_certain_R_passages':sum(raw[c]['r_counts'])} for c in raw},'Q2_registered_M':'not_resolved: conservative10percent TT test fails; no registered0.95x3 M speed support','Q3_shared_context':{c:{'B_raw_shared_RU_labels':sum(raw[c]['ru_labels']),'full_U_unique_shared_R_exposed':raw[c]['U_exposed_unique']} for c in raw},'Q4_registered_joint':'not_resolved: no common M/R/RU support block; R_SUPPORT/RU_SUPPORT are coupled block rules, not claims of no raw R/U phenomenon','endpoints':{c:raw[c]['endpoints'] for c in raw},'budget':budget,'source_receipts':[raw[c]['receipt'] for c in raw],'registration':bind(B/'validation_card_draft_revision_03.json'),'engineering_manifest':bind(G/'d2_final_manifest.json'),'registered_rule_manifest':bind(D/'registered_fixed_rule_tables/rule_manifest.json'),'independent_oracle_receipt':bind(D/'raw_oracle_receipt.json'),'limitations':limitations,'simulation_calls':{'SUMO':0,'netconvert':0,'TraCI':0,'GUI':0},'seed23_released':False,'next_action':'Keep seed23 locked. Submit negative first matched unit for scientific review; do not proceed toward SG6-R resolution or formal-design unlock.'}
save('data_gate_receipt.json',summary);save('comparison_receipt.json',{'status':'PASS','value_comparisons':len(comparisons),'tolerance':{'absolute':1e-10,'relative':1e-12},'scalar_and_container_comparisons_overlap':True,'all_required_seed17_checks_pass':allpass})
save('review_manifest.json',{'authoritative_receipt':bind(D/'data_gate_receipt.json'),'files':[bind(p) for p in sorted(D.rglob('*')) if p.is_file()]})
print(json.dumps({k:summary[k] for k in ('decision','seed17_main','seed17_sensitivity','budget','open_findings','all_required_seed17_checks_pass')},indent=2));print(bind(D/'data_gate_receipt.json'));print(bind(D/'review_manifest.json'))

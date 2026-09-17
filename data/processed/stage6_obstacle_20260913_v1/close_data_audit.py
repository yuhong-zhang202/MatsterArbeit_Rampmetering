"""Append-only data audit receipts; no simulation or mutable source access."""
import csv,json,hashlib,ast
from pathlib import Path
B=Path(__file__).resolve().parent; ROOT=B.parents[2]; T=ROOT/'results/tables'/B.name; F=ROOT/'results/figures'/B.name
def rows(p):
 with p.open(newline='') as f:return list(csv.DictReader(f))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def out(n,x):
 with (B/n).open('x') as f:json.dump(x,f,indent=2);f.write('\n')
def table(n,x):
 with (B/n).open('x',newline='') as f:w=csv.DictWriter(f,fieldnames=x[0]);w.writeheader();w.writerows(x)
sources=rows(B/'source_registry.csv');assert len(sources)==12 and len({s['run_id'] for s in sources})==12
# All required archived fields are classified explicitly, including unavailable mechanisms.
fields=[('run_id_seed_demand','reusable','source_registry.csv; source_identity_verification.json','archived identity, requested demand and actual argv verified'),('compiled_topology','reusable','static_context_links.csv','original network hash, lanes and static links'),('FCD_id_lane_time_speed_position','requires_recalculation','lane_class_time.csv; entry_vehicle_records.csv','raw available; new scoped aggregation independently verified'),('E1_nVehContrib','requires_recalculation','section_window_metrics.csv','q_contrib_vehph; detector contributions, not requested/network inflow'),('E1_nVehEntered','requires_recalculation','section_window_metrics.csv','q_entered_vehph; detector entry counter distinct from contributions'),('E1_speed_occupancy_duration','requires_recalculation','e1_native_intervals.csv; section_window_metrics.csv','contribution-weighted speed; duration and lane-mean occupancy'),('TLS_state_time_movement','reusable','shared_label_timeline.csv','movement 0 R/U; movement 1 X; simultaneous labels not causal ordering'),('tripinfo_actual_entry_arrival','reusable','entry_vehicle_records.csv','actual depart lane/position/time and arrival; completed IDs'),('vehroute_class_route','reusable','entry_vehicle_records.csv','class identity and route checked against archived output'),('planned_cohort_and_endpoints','requires_recalculation','endpoint_accounting.csv','P/E/A/N/O at 1500/2700 only'),('M_observed_space_time','requires_recalculation','M_space_time_30s.csv; M_region_window.csv','observed traveled route; no synthetic upstream observations'),('R_passage_bracket','requires_recalculation','R_passage_events.csv','all R first downstream brackets; 1s labels not exact event time'),('R_regional_propagation','requires_recalculation','R_region_propagation.csv','technical stopped first labels; no congestion definition'),('RU_shared_exposure','requires_recalculation','shared_exposure.csv','technical stopped label cooccurrence'),('historical_EJMI','reusable','historical_ejmi_components.csv','unchanged historical definitions; not new classification'),('seed_contrast_pairing','requires_recalculation','historical_seed_outer_join.csv','403 union;398 paired;5 not_paired'),('lanechange_gap_acceptance','unavailable','none','not emitted; no imputation'),('untraveled_upstream_state','unavailable','none','cannot infer state upstream of actual insertion'),('continuous_outside_waiting_curve','unavailable','none','no exact planned individual schedule derived in this batch'),('causal_reference_and_control_benefit','unavailable','none','no newly registered counterfactual or controlled runs')]
frows=[dict(run_id=s['run_id'],field_id=i,availability=a,evidence=e,scope=q) for s in sources for i,a,e,q in fields];table('field_reuse_registry.csv',frows)
# Static configuration conclusions remain distinct from behavior.
static=rows(B/'static_context_links.csv')
for s in sources:
 rr=[r for r in static if r['run_id']==s['run_id']];assert len(rr)==6
 es={ast.literal_eval(r['attributes'])['id']:ast.literal_eval(r['attributes']) for r in rr if r['element']=='edge'}
 assert es['main_up']['priority']=='3' and es['ramp_accel']['priority']=='2'
 cc=[ast.literal_eval(r['attributes']) for r in rr if r['element']=='connection'];assert [x['state'] for x in cc if x['from']=='ramp_accel']==['m'];assert all(x['state']=='M' for x in cc if x['from']=='main_up')
idx=rows(B/'diagnostic_evidence_index_revision_02.csv');ids={r['evidence_id']:r for r in idx};assert len(ids)==len(idx)
for r in idx:assert sha(ROOT/r['path'])==r['sha256']
diag=rows(B/'obstacle_diagnosis_revision_02.csv');assert {r['hypothesis_id'] for r in diag}=={f'H{i}' for i in range(1,7)}
for r in diag:
 assert set(r['run_ids'].split('|'))=={s['run_id'] for s in sources}
 assert all(i in ids for i in r['evidence_ids'].split('|'))
outer=rows(T/'historical_seed_outer_join.csv');assert len(outer)==403 and sum(r['value_state']=='not_paired' for r in outer)==5
figs=['entry_domain.png','M_space_time_revision_02.png','RU_TLS_exposure.png','time_and_late_entry.png']
out('visual_qa.json',{'status':'reviewed','current_figure_groups':[{'path':str((F/p).relative_to(ROOT)),'sha256':sha(F/p)} for p in figs],'checks':['all four current images visually inspected','labels and legends readable','M revision02 scale covers all observed bin means without clipping','no technical stopped threshold redefined as congestion'],'superseded':'M_space_time.png; retained first version; see M_figure_revision_02.json'})
out('data_execution_ledger.json',{'phase':'S6-A exploratory archive-only','A01':'completed_data_scope','A02':'six_hypotheses_evidenced_pending_scientific_review','A03':'advisory_evidence_only_not_selected','physical_runs':12,'unique_runs':12,'source_files_verified':348,'required_field_cells_classified':len(frows),'required_field_cells_denominator':240,'hypotheses_with_explicit_status':6,'hypothesis_denominator':6,'evidence_ids_resolved':len(ids),'missing_values_imputed_as_zero':0,'historical_unpaired_keys_retained':5,'SUMO':0,'netconvert':0,'TraCI':0,'GUI':0,'independent_receipt':'independent_verification.json','fixtures':'fixture_test_result.json','fixture_scope':'12 A01 parsing tests; NOT full Stage6-C failure-mode coverage or SG6-L approval','current_diagnosis':'obstacle_diagnosis_revision_02.csv','current_evidence_index':'diagnostic_evidence_index_revision_02.csv','scientific_resolution':'not_claimed','historical_EJMI_changed':False,'protocol_status':'empty; formal parameters unknown','cancelled_run_scope':'q3350 logical cancellations remain in immutable Stage4 final ledger; excluded physical data denominator; see input_hashes.json','limitations':['no lane-change/gap-acceptance events','no observed long upstream feeder traveled before actual insertion','no eligible new causal reference selected','no continuous outside-waiting schedule reconstructed','complete coverage does not prove absent impairment or future suitability'],'documentation_owner':'primary agent; data analyst does not edit governance/docs'})
manifest=[]
for folder in [B,T,F]:
 for p in sorted(folder.iterdir()):
  if p.is_file() and p.name!='artifact_manifest.csv':manifest.append(dict(path=str(p.relative_to(ROOT)),sha256=sha(p),size_bytes=p.stat().st_size,status='superseded_preserved' if p.name in ['M_space_time.png','obstacle_diagnosis.csv','diagnostic_evidence_index.csv'] else 'current_or_support'))
table('artifact_manifest.csv',manifest)
print(json.dumps({'field_cells':len(frows),'evidence_ids':len(ids),'hypotheses':len(diag),'artifacts':len(manifest),'manifest_sha256':sha(B/'artifact_manifest.csv')}))

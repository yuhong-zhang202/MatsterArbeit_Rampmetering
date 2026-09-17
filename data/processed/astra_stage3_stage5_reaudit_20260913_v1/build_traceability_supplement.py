"""Create explicitly proposed audit supplements without modifying prior products."""
from pathlib import Path
import csv, json, hashlib
ROOT=Path(__file__).resolve().parents[3]; OUT=Path(__file__).resolve().parent
S3='data/processed/stage3_baseline_diagnostic_20260912_v2/'
S4='data/processed/stage4_qmain_sequential_20260912_v1/'
S5='data/processed/exploratory_validation_closeout_20260913_v1/'
def rows(p):
    with (ROOT/p).open(newline='') as f:return list(csv.DictReader(f))
def sha(p):return hashlib.sha256((ROOT/p).read_bytes()).hexdigest()
def csvout(name,data):
    with (OUT/name).open('x',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(data[0]));w.writeheader();w.writerows(data)
handover=rows(S5+'method_handover_draft.csv')
handover[0]['current_value_or_unknown']='Current synthetic two-lane freeway, one-lane ramp and shared R/U approach; bounded intended-use evidence gap; structural cause unknown.'
csvout('corrected_method_handover.csv',handover)
# Each E-* alias can map to multiple exact artifacts: no implied automatic EV-* conversion.
mapping={
 'E-PROTOCOL-EMPTY':[('docs/EXPERIMENT_PROTOCOL.md','Entire file; 0 bytes; no formal values selected')],
 'E-S2-G2':[('docs/STAGE2_COMPLETION_REPORT.md','Accepted finite Stage2 scope; accounting and timing limits')],
 'E-S3-FINAL':[(S3+'verification/T33_T34_independent_v3.json','All 8 run results and totals'),('docs/STAGE3_BASELINE_DIAGNOSTIC_REPORT.md','Sections 3-8; quantitative gates and interpretation limits'),(S3+'analysis_review/revision_06/claim_evidence.csv','Q1-Q4')],
 'E-S3-O1':[(S3+'measurement_contract.json','lanes, stop_definition, fcd, e1_detectors and TLS context'),(S3+'network_observation_map.csv','All observation rows')],
 'E-S3-O5':[(S3+'aggregate/revision_03/sensitivity.csv','96 M-only internal q/v window values'),(S3+'aggregate/revision_03/aggregation_timeseries.csv','1264 bins; 48 run/window/aggregation series'),(S3+'analysis_review/revision_06/aggregation_shape_summary.csv','48 shape summaries; q/v extrema, intervals and support'),(S3+'analysis_review/revision_06/seed_sign_consistency.csv','398 paired metrics; 43 inconsistent signs; 5 unpaired keys additionally disclosed by audit')],
 'E-S3-Q2':[(S3+'analysis_review/revision_06/claim_evidence.csv','question_id=Q2; not_identified')],
 'E-S3-Q3':[(S3+'analysis_review/revision_06/claim_evidence.csv','question_id=Q3; supported exposure, not causal U loss')],
 'E-S4-CONTRACT':[(S4+'measurement_contract.json','Registered exploratory measurement contract'),(S4+'registration_payload.json','Fixed registered factors and intervention limits')],
 'E-S4-FINAL':[(S4+'final_evidence_ledger_snapshot.json','Immutable normative final execution ledger and external evidence'),(S4+'analysis/final/revision_04/registered_final_decision.json','action and point_states'),('results/tables/stage4_qmain_sequential_20260912_v1/final/revision_03/final_run_matrix.csv','Registered terminal run matrix')],
 'E-S4-SCI':[(S4+'verification/T43_final_scientific_review_record_20260913.json','Final bounded scientific acceptance and causal/generalization limits')],
 'E-STAGE5-T50':[(S5+'artifact_inventory.csv','O1-O6 paths and hashes'),(S5+'gate_inventory.csv','G01-G08 recorded results; G08 timing text is historical'),(S5+'inventory_verification_revision_02.json','15 path/hash checks, 3 mirror checks; does not validate E-* resolution')],
 'E-STAGE5-T52':[(str(OUT.relative_to(ROOT))+'/corrected_method_handover.csv','22 qualified items; formal values remain unknown_not_selected; audit supplement, not automatically adopted')]
}
index=[]
for eid,refs in mapping.items():
    for p,scope in refs:
        assert (ROOT/p).is_file()
        index.append({'evidence_id':eid,'path':p,'sha256':sha(p),'locator_and_scope':scope,'alias_policy':'Explicit E-* alias defined by this audit supplement; no implicit EV-* prefix substitution','adoption_status':'Proposed audit supplement; original files preserved'})
csvout('evidence_index.csv',index)
gates=rows(S5+'gate_inventory.csv'); requested={i for r in handover+gates for i in r['evidence_id'].split('|')}
assert requested==set(mapping)
checks=json.loads((OUT/'audit_results.json').read_text())
unpaired=checks['unpaired_contrast_keys']
csvout('unpaired_seed_contrasts.csv',[{'contrast_family':r['key'][0],'window':r['key'][1],'entity':r['key'][2],'metric':r['key'][3],'unit':r['key'][4],'available_seeds':','.join(map(str,r['available_seeds'])),'qualification':'not_paired_across_both_seeds; absent episode row is not automatically a missing observation or a zero','included_in_398_sign_rows':False} for r in unpaired])
zero_keys=['missing_speed','negative_speed','nonfinite_speed','unknown_id','unknown_lane','duplicate_id_frame','missing_frames','extra_frames','duplicate_frames','tls_missing_labels','tls_extra_labels','tls_duplicate_labels','e1_negative_contrib','e1_positive_contrib_invalid_speed','unresolved_first_R']
explicit=[{'run_id':r['run_id'],**{k:r['counts'].get(k,0) for k in zero_keys}} for r in checks['raw_checks']]
assert all(r[k]==0 for r in explicit for k in zero_keys)
csvout('actual_raw_input_anomaly_counts.csv',explicit)
changed=[(i,k) for i,(a,b) in enumerate(zip(rows(S5+'method_handover_draft.csv'),handover)) for k in a if a[k]!=b[k]]
assert changed==[(0,'current_value_or_unknown')]
receipt={'status':'proposed_correction_verified','original_reference_ids':len(requested),'resolved_ids':len(mapping),'exact_path_hash_mapping_rows':len(index),'original_handover_rows':22,'corrected_handover_rows':len(handover),'changed_cells':changed,'formal_values_selected':0,'unpaired_contrast_keys_disclosed':len(unpaired),'original_files_unchanged':True,'new_artifacts':{p.name:sha(str(p.relative_to(ROOT))) for p in OUT.iterdir() if p.name in ['corrected_method_handover.csv','evidence_index.csv','unpaired_seed_contrasts.csv','actual_raw_input_anomaly_counts.csv']}}
with (OUT/'supplement_verification.json').open('x') as f:json.dump(receipt,f,indent=2);f.write('\n')
print(json.dumps(receipt))

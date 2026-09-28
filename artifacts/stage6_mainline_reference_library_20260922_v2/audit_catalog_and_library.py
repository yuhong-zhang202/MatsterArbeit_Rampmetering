#!/usr/bin/env python3
"""Independent, read-only audit of the Candidate-C catalogue and rerun tables."""
from __future__ import annotations
import csv, hashlib, json
from collections import Counter
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'data/processed/stage6_mainline_reference_library_20260922_v2'
EXPECTED={'A0':26,'M3350':45}
def sha(p):
    h=hashlib.sha256()
    with open(p,'rb') as f:
        for b in iter(lambda:f.read(1<<20),b''): h.update(b)
    return h.hexdigest()
def read(p): return list(csv.DictReader(open(p,newline='')))
cat=read(OUT/'disturbance_catalog.csv')
ledger=read(OUT/'reference_candidate_ledger.csv')
issues=[]; checks={}
checks['catalog_rows']=len(cat)
checks['catalog_rows_by_run']=dict(Counter(r['run'] for r in cat))
for run,n in EXPECTED.items():
    rr=[r for r in cat if r['run']==run]
    checks[f'{run}_catalog_count_ok']=len(rr)==n
    if len(rr)!=n: issues.append(f'{run}: catalogue count {len(rr)} != {n}')
    keys=[r['source_event_id'] for r in rr]
    source_path=Path(rr[0]['source_path']) if rr else None
    source_rows=[r for r in read(ROOT/source_path) if r.get('run')==({'A0':'A','M3350':'LOC'}[run]) and r.get('profile')=='L' and str(r.get('is_merge_core','')).lower()=='true' and int(r.get('low_speed_bins','0'))>=1] if source_path else []
    source_keys={r['event_id'] for r in source_rows}
    checks[f'{run}_source_catalog_id_set_equal']=set(keys)==source_keys
    if set(keys)!=source_keys: issues.append(f'{run}: catalogue/source event-id set mismatch')
    if len(keys)!=len(set(keys)): issues.append(f'{run}: duplicate source event id')
    if any(r['lane']!='pooled' or r['lane_assignment_status']!='NOT_AVAILABLE_FROM_LOCKED_C' for r in rr): issues.append(f'{run}: invalid lane scope')
    for r in rr:
        try: a=int(r['first_low_bin']); z=int(r['low_bin_end_exclusive']); c=int(r['cell']); start=int(r['start_s']); end=int(r['end_s']); dur=int(r['duration_s'])
        except Exception: issues.append(f'{run}: nonnumeric catalog row {r.get("catalog_id")}'); continue
        if not (0<=a<z<=90 and start==a*30 and end==z*30 and dur==end-start and 0<=c<22): issues.append(f'{run}: invalid boundary {r["catalog_id"]}')
        if r['source_sha256'] != sha(ROOT/r['source_path']): issues.append(f'{run}: source hash mismatch')
        if r['fcd_sha256'] != sha(ROOT/r['fcd_path']): issues.append(f'{run}: FCD hash mismatch')
        if r['vehroute_sha256'] != sha(ROOT/r['vehroute_path']): issues.append(f'{run}: vehroute hash mismatch')
        if r['locked_method_sha256'] != sha(ROOT/r['locked_method_path']): issues.append(f'{run}: method hash mismatch')
        if r['locked_analyzer_sha256'] != sha(ROOT/r['locked_analyzer_path']): issues.append(f'{run}: analyzer hash mismatch')
        if 'revision03' in r['source_path'].lower() or 'revision03' in r['locked_analyzer_path'].lower(): issues.append(f'{run}: revision03 contamination')
checks['catalog_identity_unique']=len({(r['run'],r['source_event_id']) for r in cat})==len(cat)
checks['all_catalog_rows_complete']=all(r['catalog_status']=='COMPLETE' for r in cat)
checks['source_hashes_and_boundaries']='none' if not issues else 'issues'
checks['ledger_rows']=len(ledger)
checks['ledger_704_periods']=len(ledger)==704*3
if len(ledger)!=2112: issues.append(f'ledger rows {len(ledger)} != 2112')
for run in EXPECTED:
    rr=[r for r in ledger if r['run']==run and r['lane']=='pooled']
    checks[f'{run}_pooled_periods']=len(rr)
    checks[f'{run}_accepted_periods']=sum(r['accepted']=='REFERENCE_ACCEPTED' for r in rr)
    if len(rr)!=352: issues.append(f'{run}: pooled periods {len(rr)} != 352')
checks['accepted_rows_total']=sum(r['accepted']=='REFERENCE_ACCEPTED' for r in ledger)
checks['accepted_pooled_total']=sum(r['accepted']=='REFERENCE_ACCEPTED' and r['lane']=='pooled' for r in ledger)
checks['fixture_pass']=all(r['pass']=='True' for r in read(OUT/'reference_fixture_test_receipt.csv'))
numeric=json.load(open(OUT/'independent_numeric_reconciliation.json'))
checks['independent_numeric_reconciliation_pass']=numeric.get('status')=='PASS' and all(x.get('matches_status') for x in numeric.get('samples',[])) and len(numeric.get('samples',[]))==4
if not checks['independent_numeric_reconciliation_pass']: issues.append('independent numeric reconciliation failed')
checks['revision03_excluded']=not any('revision03' in r.get('rejection_reason','').lower() for r in ledger)
status='PASS' if not issues and all(checks[k] for k in ('catalog_identity_unique','all_catalog_rows_complete','ledger_704_periods','fixture_pass','independent_numeric_reconciliation_pass','revision03_excluded')) else 'FAIL'
out={'status':status,'issues':issues,'checks':checks,'catalog_sha256':sha(OUT/'disturbance_catalog.csv'),'ledger_sha256':sha(OUT/'reference_candidate_ledger.csv'),'numeric_reconciliation_sha256':sha(OUT/'independent_numeric_reconciliation.json'),'audit_script_sha256':sha(Path(__file__)),'note':'Independent structural/hash and four-slice numerical audit; does not establish physical normality or formal thesis validity.'}
(OUT/'data_audit_review.json').write_text(json.dumps(out,indent=2)+'\n')
print(json.dumps(out,indent=2))

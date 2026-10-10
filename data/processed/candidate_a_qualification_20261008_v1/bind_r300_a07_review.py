"""Bind final independent R300 A07 audit artifacts; no simulation or raw writes."""
import csv
import hashlib
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[3]
DEST=Path(__file__).parent
ART=ROOT/'artifacts/candidate_a_qualification_20261008_v1/engineering'
TABLE=ROOT/'results/tables/candidate_a_qualification_20261008_v1'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
gate=json.loads((DEST/'R300_A07_ACTUAL_DATA_GATE_V2.json').read_text())
engineering=json.loads((ART/'R300_A07_RUNTIME_ENGINEERING_DIAGNOSTIC.json').read_text())
assert gate['manifest_files_verified']==engineering['manifest_files_verified']==45
assert gate['red_witness_count']==42
with (TABLE/'R300_A07_PRE_RED_WITNESSES.csv').open(newline='') as f:rows=list(csv.DictReader(f))
assert len(rows)==len({r['vehicle_id'] for r in rows})==42
assert sum(r['population']=='storage' for r in rows)==27
assert sum(r['population']=='ingress' for r in rows)==15
assert gate['C']==engineering['accounting']['C'] if 'accounting' in engineering else True
paths=[DEST/'audit_r300_a07_actual.py',DEST/'R300_A07_ACTUAL_DATA_GATE_V2.json',DEST/'R300_A07_ACTUAL_DATA_REVIEW.md',Path(__file__)]
paths+=sorted(TABLE.glob('R300_A07_*.csv'))
paths += [ART/name for name in ['R300_A07_RUNTIME_ENGINEERING_DIAGNOSTIC.json','R300_A07_RUNTIME_ENGINEERING_REPORT.md','R300_A07_GUARD_NATIVE_DIAGNOSIS.md','R300_A07_GUARD_NATIVE_DIAGNOSIS_RECEIPT.json','R300_A07_NATIVE_SOURCE_RECEIPT.json']]
result=dict(classification='FINAL_DERIVED_REVIEW_BINDINGS_NOT_QUALIFICATION',
            final_gate='R300_A07_ACTUAL_DATA_GATE_V2.json',
            preserved_superseded_gate='R300_A07_ACTUAL_DATA_GATE.json',
            counts=dict(guardian_manifest_total=45,non_snapshot=34,snapshot=11,red_witness_unique_ids=42,storage=27,ingress=15),
            hashes={str(p.relative_to(ROOT)):sha(p) for p in paths})
target=DEST/'R300_A07_FINAL_DERIVED_BINDINGS.json'
data=json.dumps(result,indent=2)+'\n'
if target.exists():assert target.read_text()==data,'Preserve existing bindings; changed inputs require new version'
else:
    with target.open('x') as f:f.write(data)
print(json.dumps(dict(path=str(target.relative_to(ROOT)),sha256=sha(target),final_gate_sha256=sha(DEST/'R300_A07_ACTUAL_DATA_GATE_V2.json'),review_sha256=sha(DEST/'R300_A07_ACTUAL_DATA_REVIEW.md')),indent=2))

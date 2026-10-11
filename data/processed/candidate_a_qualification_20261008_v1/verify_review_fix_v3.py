"""Verify PR #5 correction delta and immutable historical evidence; no SUMO."""
import csv
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
DEST = Path(__file__).parent
TABLE = ROOT / 'results/tables/candidate_a_qualification_20261008_v1'
PRE = ROOT / 'artifacts/candidate_a_qualification_20261008_v1/review_fix_20261011/PRE_FIX_BINDINGS.json'
SOURCE = str((DEST/'audit_r300_a07_actual.py').relative_to(ROOT))
FIELDS = {'C_observed', 'C_applied_observed', 'E_observed', 'N_observed',
          'command_latency', 'quantization', 'physical_shortfall'}


def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


def load(p):
    return json.loads(p.read_text())


def save(p, content):
    text = json.dumps(content, indent=2)+'\n'
    if p.exists():
        assert p.read_text() == text, 'Preserve existing: '+str(p)
    else:
        p.write_text(text)


def csv_rows(p):
    with p.open(newline='') as stream:
        return list(csv.DictReader(stream))


def main():
    pre = load(PRE)
    preserved = {p:h for p,h in pre['hashes'].items() if p != SOURCE}
    drift = [p for p,h in preserved.items() if sha(ROOT/p) != h]
    assert not drift, drift
    table_checks = []
    changes = []
    for original in sorted(TABLE.glob('R300_A07_*.csv')):
        if '_V' in original.stem:
            continue
        new = original.with_name(original.stem+'_V3.csv')
        before, after = csv_rows(original), csv_rows(new)
        assert len(before) == len(after)
        if 'SERVICE_WINDOWS' not in original.name:
            assert original.read_bytes() == new.read_bytes()
        else:
            assert before[0] == after[0]
            assert len(before) == 6
            for i, (old, revised) in enumerate(zip(before, after)):
                for key in old:
                    if i > 0 and key in FIELDS:
                        assert float(old[key]) == 0 and revised[key] == ''
                        changes.append(dict(row=i,begin_s=int(old['begin_s']),field=key,before=old[key],after=None))
                    else:
                        assert old[key] == revised[key], (i,key)
        table_checks.append(dict(original=str(original.relative_to(ROOT)),new=str(new.relative_to(ROOT)),
                                rows=len(before),byte_identical=original.read_bytes()==new.read_bytes(),
                                original_sha256=sha(original),new_sha256=sha(new)))
    assert len(table_checks)==8 and len(changes)==35
    old = load(DEST/'R300_A07_ACTUAL_DATA_GATE_V2.json')
    new = load(DEST/'R300_A07_ACTUAL_DATA_GATE_V3.json')
    assert old['service_windows'][0] == new['service_windows'][0]
    for i in range(1,6):
        for key in old['service_windows'][i]:
            if key in FIELDS:
                assert old['service_windows'][i][key] == 0 and new['service_windows'][i][key] is None
            else:
                assert old['service_windows'][i][key] == new['service_windows'][i][key]
    old_comparable = {k:v for k,v in old.items() if k not in ('service_windows','bindings')}
    new_comparable = {k:new[k] for k in old_comparable}
    assert old_comparable == new_comparable
    old_binding, new_binding = old['bindings'].copy(), new['bindings'].copy()
    old_binding.pop(SOURCE); new_binding.pop(SOURCE)
    assert old_binding == new_binding
    assert new['disposition']=='NOT_QUALIFIED_SAFETY_GUARD_STOP'
    assert new['highest_safe_qualified_rate_veh_h'] is None
    assert all(r['tracking_error'] is None and r['status']=='NOT_TESTED_INCOMPLETE_WINDOW' for r in new['service_windows'])
    receipt = dict(classification='EXPLORATORY_ENGINEERING_DATA_EXPRESSION_CORRECTION_NOT_FORMAL',
                   base_commit=pre['base_commit'],pre_fix_bindings_sha256=sha(PRE),
                   old_analysis_sha256=pre['hashes'][SOURCE],new_analysis_sha256=sha(ROOT/SOURCE),
                   historical_files_checked=len(preserved),historical_hash_drift=drift,
                   raw_files_preserved=sum(p.startswith('data/raw/') for p in preserved),
                   guard_and_contract_changed=False,new_SUMO_starts=0,
                   table_checks=table_checks,changed_csv_measurement_cells=changes,
                   changed_json_service_measurement_cells=35,first_six_seconds_record_identical=True,
                   all_other_original_gate_fields_identical=True,all_other_original_bindings_identical=True,
                   qualification_status_unchanged=True,service_errors_all_null=True,
                   manifest_files_verified=new['manifest_files_verified'],protected_files_verified=new['protected_hashes_verified'],
                   full_cycles_completed=0,qualified_rates=0,
                   STOP3='Scientific reviewer must independently recheck; preserved prospective guard witness evidence unchanged')
    save(DEST/'R300_A07_REVIEW_FIX_DELTA_V3.json',receipt)
    print(json.dumps({k:receipt[k] for k in ('historical_files_checked','historical_hash_drift','raw_files_preserved','changed_json_service_measurement_cells','manifest_files_verified','protected_files_verified')},indent=2))


if __name__=='__main__':
    main()

"""Bounded static receipt verifier; no network/raw/native runtime dependency."""
from pathlib import Path
import hashlib
import json
import sys
ROOT = Path(__file__).resolve().parents[2]
ENGINEERING = ROOT / 'artifacts/candidate_a_a1_proof_gap_20261011_v1/engineering'
SOURCE = 'fa7df22d7f1c4ae245192ecc32410a49f1ffb2a3'


def checked(ok, message):
    if not ok:
        raise ValueError(message)


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def verify():
    bindings = json.loads((ENGINEERING / 'INPUT_BINDINGS.json').read_text())
    for name, expected in bindings['files'].items():
        checked(not name.startswith('data/raw/'), 'raw input prohibited')
        checked(sha(ROOT / name) == expected, 'hash mismatch: ' + name)
    ledger = json.loads((ENGINEERING / 'SOURCE_TO_STATE_LEDGER.json').read_text())
    matrix = json.loads((ENGINEERING / 'COVERAGE_AND_JOINT_MATRIX.json').read_text())
    source = json.loads((ENGINEERING / 'SOURCE_EXCERPTS.json').read_text())
    receipt = json.loads((ENGINEERING / 'SOURCE_FETCH_RECEIPT.json').read_text())
    checked(ledger['source_commit'] == source['commit'] == receipt['commit'] == SOURCE, 'source identity')
    checked({p['id'] for p in matrix['proof_obligations']} == {f'P{i}' for i in range(11)}, 'P0-P10 coverage')
    refs = {ex['id'] for ex in source['excerpts']}
    checked(len(refs) == len(source['excerpts']), 'duplicate excerpt id')
    for ex in source['excerpts']:
        checked(hashlib.sha256(ex['text'].encode()).hexdigest() == ex['sha256'], 'excerpt bytes')
        checked(len(ex['text'].splitlines()) == ex['line_end'] - ex['line_start'] + 1, 'physical line count')
        checked('/' + SOURCE + '/' in ex['url'], 'permanent source anchor')
    checked(len(ledger['fields']) == ledger['count'] == 69, 'field coverage')
    for field in ledger['fields']:
        checked(set(field['source_excerpt_ids']) <= refs, 'unbound source reference')
        checked(field['observability_level'] in 'abcde', 'observation classification')
    checked(ledger['verdict'] == matrix['verdict'] == 'STOP_A1_UNDER_CURRENT_INTERFACE', 'bounded verdict')
    checked(ledger['all_stronger_conservative_proofs_impossible'] == 'NOT_PROVED', 'universal impossibility not proved')
    protected = json.loads((ROOT / 'artifacts/candidate_a_a1_contract_20261011_v1/engineering/PROTECTED_BASELINE_SHA256.json').read_text())['files']
    drift = [name for name, expected in protected.items() if sha(ROOT / name) != expected]
    checked(len(protected) == 536 and not drift, 'protected implementation/evidence drift')
    sys.path.insert(0, str(ROOT / 'scripts/candidate_a_a1_contract_20261011_v1'))
    import audit_public
    public = audit_public.audit(ROOT)
    old = json.loads((ROOT / 'artifacts/candidate_a_a1_contract_20261011_v1/review_fix_20261011/v6/PUBLIC_AUDIT_OUTPUT_V6.json').read_text())
    checked(public['a07_witness_mapping'] == old['a07_witness_mapping'], '42 historical witness mapping drift')
    checked(public['upstream_public_audit']['service_observed_steps'] == [6, 0, 0, 0, 0, 0], 'missing-window semantics')
    checked(public['a07_a1_decision'] == 'UNKNOWN' and public['current_contract_STOP3'] == 'PRESERVED', 'historical gate')
    return {'status': 'PASS', 'scope': 'STATIC_SOURCE_RECEIPT_SCHEMA_HASH_AND_UNCHANGED_PUBLIC_HISTORY_ONLY',
            'source_commit': SOURCE, 'bound_files': len(bindings['files']),
            'state_fields': len(ledger['fields']), 'source_excerpts': len(refs),
            'proof_ids': 11, 'coverage_rows': len(matrix['coverage']),
            'protected_files_checked': len(protected), 'protected_drift': drift,
            'old_a07_mapping_equal': True, 'a07_witnesses': 42,
            'service_observed_steps': [6, 0, 0, 0, 0, 0],
            'actual_native_branches_determined': 0, 'sumo_traci_starts': 0,
            'native_cpp_builds': 0, 'synthetic_new_tests': 0,
            'full_a1_eligibility_proven': False, 'clean_checkout_tested_here': False,
            'source_native_to_binary_build_equivalence': 'NOT_VERIFIED',
            'all_stronger_conservative_proofs_impossible': 'NOT_PROVED'}


if __name__ == '__main__':
    print(json.dumps(verify(), indent=2, allow_nan=False))

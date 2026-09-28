#!/usr/bin/env python3
"""Fail-closed, one-attempt launcher. Never run unless a separate hash-bound user approval exists."""
from __future__ import annotations
import argparse, fcntl, hashlib, importlib.util, json, os, resource, subprocess, sys
from importlib.metadata import version
from pathlib import Path

ROOT = Path('/Users/yuhongzhang/Desktop/Masterarbeit-Ramp-Metering')
CARD = ROOT/'docs/run_cards/STAGE6_BASELINE_LOC_M3350_S17_EXACT_CARD.json'
PKG = ROOT/'artifacts/stage6_baseline_localization_20260921_v1/LOC_M3350_S17'
ENG = PKG/'engineering'
RUN_ID = 'LOC_M3350_S17_attempt1'
RAW = ROOT/'data/raw/stage6_baseline_localization_20260921_v1'/RUN_ID
SUMO = Path('/Library/Frameworks/EclipseSUMO.framework/Versions/1.26.0/EclipseSUMO/bin/sumo')
SUMO_HOME = '/Library/Frameworks/EclipseSUMO.framework/Versions/1.26.0/EclipseSUMO/share/sumo'

def sha(path: Path) -> str:
    h = hashlib.sha256()
    with path.open('rb') as f:
        for block in iter(lambda: f.read(1 << 20), b''):
            h.update(block)
    return h.hexdigest()

def require(condition, message):
    if not condition:
        raise ValueError(message)

def verify_binding(row):
    p = Path(row['path'])
    if not p.is_absolute():
        p = ROOT/p
    require(p.is_file(), 'binding missing: '+str(p))
    require(not p.is_symlink(), 'symlink rejected: '+str(p))
    require(p.stat().st_size == row['bytes'] and sha(p) == row['sha256'], 'binding mismatch: '+str(p))

def load_review(path, card_sha, field, expected):
    review = json.loads(path.read_text())
    require(review.get('status') == expected and review.get('card_sha256') == card_sha,
            field+' review is not PASS for this exact card')
    counts = review.get('open_findings', {})
    require(counts == {'blocker':0, 'major':0, 'required_minor':0}, field+' review has open required findings')

def bounded_popen(argv, **kwargs):
    # Eighteen XML roles, two SUMO report logs, stdout and stderr are the only large files.
    # A kernel-enforced 65 MB per-file cap bounds their aggregate at 1.43 GB.
    def child_limits():
        resource.setrlimit(resource.RLIMIT_FSIZE, (65_000_000, 65_000_000))
        if hasattr(resource, 'RLIMIT_CORE'):
            resource.setrlimit(resource.RLIMIT_CORE, (0, 0))
    kwargs['preexec_fn'] = child_limits
    return subprocess.Popen(argv, **kwargs)

def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--approval', type=Path)
    ap.add_argument('--execute', action='store_true')
    args = ap.parse_args()
    require(CARD.is_file() and not CARD.is_symlink(), 'exact card missing or symlinked')
    card_sha = sha(CARD)
    card = json.loads(CARD.read_text())
    require(card.get('card_id') == 'LOC_M3350_S17' and card.get('status') == 'AWAITING_EXPLICIT_USER_APPROVAL', 'wrong or closed card')
    require(card.get('authorization') == {'user_approved': False, 'authorized_starts': 0, 'max_starts': 1, 'technical_retries': 0}, 'card authorization invariant changed')
    require(Path(sys.executable).resolve() == Path(card['runtime']['python_resolved_executable']) and
            sha(Path(sys.executable).resolve()) == card['runtime']['python_sha256'], 'Python executable binding mismatch')
    require(sys.version_info[:3] == (3, 13, 0), 'Python version mismatch')
    require({name:version(name) for name in ('traci','sumolib','sumoITScontrol')} ==
            {'traci':'1.26.0','sumolib':'1.26.0','sumoITScontrol':'0.1.0'}, 'venv package version mismatch')
    manifest_binding = card['input_manifest']
    verify_binding(manifest_binding)
    manifest = json.loads(Path(manifest_binding['path']).read_text())
    require(manifest.get('status') == 'PASS_STATIC_INPUT_MANIFEST' and manifest.get('run_id') == RUN_ID,
            'input manifest status or identity mismatch')
    for row in manifest['source_bindings']:
        verify_binding(row)
    require(card['runtime']['argv'] == [str(SUMO), '-c', str(ENG/'inputs'/RUN_ID/'scenario.sumocfg')], 'runtime argv drift')
    require(card['runtime']['expected_version'] == '1.26.0' and card['runtime']['SUMO_HOME'] == SUMO_HOME, 'runtime environment drift')
    require(card['runtime']['sumo_executable'] == str(SUMO) and
            card['runtime']['sumo_executable_sha256'] == sha(SUMO), 'SUMO executable binding mismatch')
    require(card['runtime_limits']['wallclock_stop_line_s'] == 180 and
            card['runtime_limits']['output_size_stop_line_bytes'] == 1_500_000_000 and
            card['runtime_limits']['max_sumo_starts'] == 1 and
            card['runtime_limits']['technical_retries'] == 0, 'runtime limits drift')
    require(not RAW.exists(), 'exclusive output path already exists; no start permitted')
    review_hashes = {}
    for key, expected in [('engineering_review','PASS_PRELAUNCH_ENGINEERING'), ('data_review','PASS_PRELAUNCH_DATA'), ('scientific_review','PASS_PRELAUNCH_SCIENTIFIC')]:
        load_review(ROOT/card['prelaunch_reviews']['review_receipts'][key], card_sha, key, expected)
        review_path = ROOT/card['prelaunch_reviews']['review_receipts'][key]
        review_hashes[key] = sha(review_path)
    if not args.execute:
        print(json.dumps({'status':'DRY_RUN_NO_PROCESS','card_sha256':card_sha,'run_id':RUN_ID,'output_path':str(RAW)}))
        return 0
    require(args.approval is not None, 'explicit user approval sidecar required')
    approval_path = args.approval.absolute()
    require(approval_path.is_file() and not approval_path.is_symlink(), 'approval sidecar missing or symlinked')
    approval = json.loads(approval_path.read_text())
    require(approval.get('status') == 'USER_APPROVED_EXACT_CARD' and approval.get('card_sha256') == card_sha,
            'approval is not bound to this exact card hash')
    require(approval.get('card_path') == str(CARD) and approval.get('run_id') == RUN_ID and
            approval.get('authorized_starts') == 1 and approval.get('technical_retries') == 0,
            'approval scope mismatch')
    require(approval.get('review_receipt_sha256') == review_hashes,
            'approval must bind the three current prelaunch review receipts')
    lock_path = ENG/'card'/'execution.lock'
    with lock_path.open('a') as lock:
        fcntl.flock(lock.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
        require(not RAW.exists(), 'output path consumed by another process; no retry')
        runner_path = ROOT/'artifacts/stage6_targeted_validation_20260920_v1/engineering/runtime_executor.py'
        spec = importlib.util.spec_from_file_location('locked_one_attempt_executor', runner_path)
        runner = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(runner)
        attempt = {'attempt_id':RUN_ID, 'run_root':str(RAW), 'output_root':str(RAW/'outputs'),
                   'argv':card['runtime']['argv']}
        # The underlying supervisor has one direct start and no retry path; this factory adds a kernel-enforced output-file cap.
        receipt = runner._run(attempt, card_sha, {'path':str(approval_path),'bytes':approval_path.stat().st_size,'sha256':sha(approval_path)},
                              factory=bounded_popen, timeout=180, cap=1_500_000_000, synthetic=False)
        print(json.dumps(receipt, sort_keys=True))
        return 0 if receipt.get('status') == 'process_completed_pending_gate' else 2

if __name__ == '__main__':
    try:
        sys.exit(main())
    except Exception as exc:
        print('FAIL_CLOSED_NO_START: '+repr(exc), file=sys.stderr)
        sys.exit(2)

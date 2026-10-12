"""Public static budget audit; optional immutable local raw hash readback.

No native execution, TraCI import, executable authorization dependency, or writes.
Output on stdout; caller preserves its versioned result.
"""
import argparse
import hashlib
import json
import math
from pathlib import Path
import re
import subprocess

ROOT = Path(__file__).resolve().parents[3]
TASK = 'artifacts/candidate_a_native_smoke_budget_20261012_v1'
ENG = TASK + '/engineering'
RUN = 'CA_NATIVE_PHASE_R300_S17_SMOKE04'
CARD = ENG + '/packages/' + RUN + '/card.json'
BASELINE = '22ec93c7b54d4ea15f55284026ded6c414de605b'


def sha(path):
    h = hashlib.sha256()
    with path.open('rb') as f:
        for block in iter(lambda: f.read(1024 * 1024), b''):
            h.update(block)
    return h.hexdigest()


def load(name):
    return json.loads((ROOT / name).read_text())


def hashes(mapping):
    assert isinstance(mapping, dict) and mapping
    bad = [name for name, value in mapping.items()
           if not (ROOT / name).is_file() or sha(ROOT / name) != value]
    assert not bad, bad
    return len(mapping)


def review(local_raw=False):
    inputs = load(ENG + '/INPUT_BINDINGS_V1.json')
    assert sha(ROOT / (ENG + '/INPUT_BINDINGS_V1.json')) == 'a261ddaaee2baa006d34e333d70c96b11d6bf4f717329e250033fb15495031ec'
    n = hashes(inputs['files']); assert n == 55
    card = load(CARD)
    assert sha(ROOT / CARD) == inputs['card_sha256'] == '1fe30783bb04fb79a3fc7e17b21e946be9cb0c58223258dd7a51dfda3898b086'
    old_card = load('artifacts/candidate_a_native_smoke_runtime_fix_20261012_v1/engineering/packages/CA_NATIVE_PHASE_R300_S17_SMOKE03/card.json')
    assert card['baseline_commit'] == BASELINE
    assert card['status'] == 'PREPARED_NOT_RELEASED'
    assert card['runtime_authorization_generated'] is False
    assert card['spec'] == {**old_card['spec'], 'run_id': RUN}
    assert card['spec']['end_s'] == 1207 and card['spec']['first_red_mandatory_pause'] is True
    assert card['spec']['automatic_continuation'] is False
    expected = {'wall_limit_s': 300, 'startup_limit_s': 60,
                'run_limit_bytes': 300000000, 'minimum_free_bytes': 5000000000}
    assert card['resources'] == expected
    assert all(type(v) is int for v in card['resources'].values())
    assert old_card['resources'] == {**expected, 'wall_limit_s': 180}
    assert card['environment'] == old_card['environment']
    nsources = hashes(card['sources_sha256'])
    hashes(card['prepared_input_sha256']); hashes(card['inherited_inputs_sha256'])
    assert sha(ROOT / 'artifacts/stage6_baseline_localization_20260921_v1/LOC_M3350_S17/engineering/build_attempts/TV_BUILD01/network.net.xml') == card['network_sha256']
    assert card['configuration_delta'] == old_card['configuration_delta']
    assert card['runtime_optimization'] == old_card['runtime_optimization']
    assert card['source_binary_compiler_equivalence'] == 'NOT_VERIFIED'
    assert not (ROOT / TASK / 'AUTHORIZATION_NATIVE_EXECUTION.json').exists()
    assert not (ROOT / ENG / 'EXECUTION_RELEASE.json').exists()
    assert not (ROOT / card['output']).parent.exists()
    protected = load('artifacts/candidate_a_a1_contract_20261011_v1/engineering/PROTECTED_BASELINE_SHA256.json')['files']
    nprotected = hashes(protected); assert nprotected == 536
    nold = hashes(old_card['sources_sha256']); assert nold == 22
    previous = ROOT / old_card['package']
    new = ROOT / card['package']
    normalized = {}
    for name in ('demand.rou.xml', 'scenario.add.xml', 'scenario.sumocfg'):
        a = (previous / name).read_text()
        b = (new / name).read_text()
        assert a == b.replace('candidate_a_native_smoke_budget_20261012_v1', 'candidate_a_native_smoke_runtime_fix_20261012_v1').replace(RUN, 'CA_NATIVE_PHASE_R300_S17_SMOKE03'), name
        normalized[name] = True
    bridge = (ROOT / 'src/candidate_a_native_smoke_budget_20261012/bridge.py').read_text()
    old_bridge = (ROOT / 'src/candidate_a_native_smoke_runtime_fix_20261012/bridge.py').read_text()
    assert bridge == old_bridge.replace('from src.candidate_a_native_smoke_runtime_fix_20261012.profile import', 'from src.candidate_a_native_smoke_budget_20261012.profile import')
    for fragment in ("resources['wall_limit_s']", "card['resources'],started", 'for t in range(1207):', "require(t==1206,'unexpected diagnostic pause')"):
        assert fragment in bridge
    profile = (ROOT / 'src/candidate_a_native_smoke_budget_20261012/profile.py').read_text()
    assert "all(type(v) is int" in profile and "c['resources']==RESOURCES" in profile
    assert "c.get('resources_provenance')==resources_provenance(root)" in profile
    assert "base.environment()" in profile and 'validate_release' in profile
    watchdog = (ROOT / 'src/candidate_a_native_smoke_20261011/bridge_resources.py').read_text()
    assert "self.limits['wall_limit_s']" in watchdog and 'self.done.wait(.2)' in watchdog
    assert bridge.index('started=time.monotonic()') > bridge.index("snaps=output/'snapshots'")
    assert bridge.index('started=time.monotonic()') < bridge.index('worker=protected_worker()')
    assert bridge.index('watchdog.close()') < bridge.index('capture.finalize(')
    runner = (ROOT / 'scripts/candidate_a_qualification_20261008_v1/runner.py').read_text()
    assert 'RESOURCES=dict(wall_limit_s=180,startup_limit_s=60' in runner
    issue = load('artifacts/candidate_a_qualification_20261008_v1/ISSUE_4_SNAPSHOT.json')['body']
    assert re.search(r'\b180\b', issue) is None
    assert 'wall' not in issue.lower()
    prior = load('artifacts/candidate_a_native_smoke03_execution_20261012_v1/engineering/EXECUTION_RECEIPT.json')
    assert prior['steps_verified_actual_readback'] == 1157
    assert prior['first_controlled_red_smoke_complete'] is False
    assert all(value is None for value in prior['controlled_service'].values())
    basis = load(ENG + '/BUDGET_BASIS_AND_PROPOSAL_V1.json')
    startup = prior['startup_connect_elapsed_s']
    assert startup == basis['observed_runs']['SMOKE03']['startup_connect_elapsed_s']
    duration = basis['observed_runs']['SMOKE03']['native_duration_s']
    assert duration == 154.78
    observation = startup + duration * 1207 / 1157
    maximum_startup_illustration = 60 + duration * 1207 / 1157
    arithmetic = basis['planning_arithmetic']
    for key, value in [('using_observed_startup_estimate_s', observation),
                       ('using_maximum_startup_estimate_s', maximum_startup_illustration),
                       ('headroom_300_s', 300 - maximum_startup_illustration),
                       ('headroom_240_s', 240 - maximum_startup_illustration)]:
        assert math.isclose(arithmetic[key], value, rel_tol=0, abs_tol=1e-10)
    assert 'not prediction/upper bound/confidence interval' in arithmetic['classification']
    provenance = card['resources_provenance']['proposed_change']
    assert provenance['before'] == 180 and provenance['after'] == 300
    assert provenance['basis_sha256'] == sha(ROOT / provenance['basis_path'])
    command_receipt = load(ENG + '/OFFLINE_COMMAND_RECEIPT_V2.json')
    for item in command_receipt['commands']:
        assert item['exit_code'] == 0
        assert sha(ROOT / item['output']) == item['output_sha256']
    test_log = (ROOT / ENG / 'TESTS_V2.txt').read_text()
    assert 'Ran 5 tests' in test_log and test_log.rstrip().endswith('OK')
    failed = (ROOT / ENG / 'TESTS_V1.txt').read_text()
    assert "has no attribute 'observe'" in failed and 'FAILED (errors=4)' in failed
    assert (ROOT / ENG / 'PRESERVATION_CHECK_PATH_FAILURE_V1.json').is_file()
    old_test_log = (ROOT / 'artifacts/candidate_a_native_smoke_runtime_fix_20261012_v1/engineering/OFFLINE_TEST_LOG_V2.txt').read_text()
    assert 'Ran 8 tests' in old_test_log and re.search(r'^OK$', old_test_log, re.MULTILINE)
    preservation = load(ENG + '/PRESERVATION_AND_MINIMAL_DELTA_V2.json')
    local = []
    for entry in preservation['immutable_raw']:
        manifest = load(entry['manifest'])
        assert sha(ROOT / entry['manifest']) == entry['sha256']
        assert len(manifest['files']) == entry['files_verified']
        if local_raw:
            local.append({'manifest': entry['manifest'], 'files_verified': hashes(manifest['files'])})
    if local_raw:
        log = ROOT / 'data/raw/candidate_a_native_smoke_runtime_fix_20261012_v1/CA_NATIVE_PHASE_R300_S17_SMOKE03/outputs/sumo.log'
        assert re.search(r'Duration:\s*154\.78s', log.read_text())
    return {'status': 'PASS_FOR_BOUNDED_OFFLINE_BUDGET_DATA_INTEGRITY_ONLY',
            'engineering_files_verified': n, 'protected_files_verified': nprotected,
            'old_sources_verified': nold, 'new_card_sources_verified': nsources,
            'card_sha256': sha(ROOT / CARD), 'package_normalized_equivalence': normalized,
            'resource_delta': {'wall_limit_s': [180, 300]},
            'planning_illustration_s': {'observed_startup': observation, 'maximum_startup': maximum_startup_illustration,
                                        'headroom_300': 300 - maximum_startup_illustration},
            'engineering_five_tests_log_reviewed_not_rerun': True,
            'old_eight_tests_reused_not_rerun': True,
            'clean_checkout': 'NOT_EXECUTED', 'new_native_starts_by_this_audit': 0,
            'local_raw_readback': local, 'public_default_does_not_require_local_raw': True,
            'native_duration154_78_local_confirmation': local_raw,
            'limitations': ['No 300 s native execution or completion guarantee',
                            'Clock excludes preparation and post-watchdog finalization; sampled stop is not strict whole CLI bound',
                            'No cross-version speed causal effect or hotspot estimate',
                            'No native safety, yellow adequacy or rate qualification',
                            'Native online logs exclude parent CLI warning output; unchanged final client capture',
                            'Protocol is empty; analysis is technical/exploratory only']}


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--local-raw', action='store_true')
    args = parser.parse_args()
    print(json.dumps(review(args.local_raw), indent=2, ensure_ascii=False))

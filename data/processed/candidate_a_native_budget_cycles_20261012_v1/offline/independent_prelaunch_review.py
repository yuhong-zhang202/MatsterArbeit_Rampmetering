"""Read-only public prelaunch audit: no native/raw/environment launch dependency."""
import hashlib
import json
from pathlib import Path
import re
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[4]
TASK = Path('artifacts/candidate_a_native_budget_cycles_20261012_v1')
ENG = TASK / 'engineering'
EXPECTED = {300: '25dccfa39d3ff716823f6ce7ceee18eba1c0b8c6393ae464b6db1d2b61c70386',
            360: '1289b33f53f54e2cdf4bcd504fc0774c4c4923c7ae1f9c31d5bf34c9ca848090',
            420: '624f774f5308aa00ff69d42f4436e9ffcc41a462e4cce1b8d0462c051fc799c1',
            480: '3ce1e92e7a21ea4b78aaccbcdaca19136cf67fb917d860a71f820b6de97799b3'}


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load(path):
    return json.loads((ROOT / path).read_text())


def hashes(files):
    for name, value in files.items():
        assert sha(ROOT / name) == value, name
    return len(files)


def audit():
    binding = load(ENG / 'INPUT_BINDINGS_V1.json')
    assert sha(ROOT / ENG / 'INPUT_BINDINGS_V1.json') == '4fb432812bc954dfe77d01f53d4ec991ebb4d6650ce0bfd35e166a5da587ce4d'
    assert binding['baseline_commit'] == 'd291707545e47ac5cd07379530eadca9f2e0db65'
    assert hashes(binding['files']) == binding['files_count'] == 59
    protected = load('artifacts/candidate_a_a1_contract_20261011_v1/engineering/PROTECTED_BASELINE_SHA256.json')['files']
    assert hashes(protected) == 536
    old_path = 'artifacts/candidate_a_native_smoke_budget_20261012_v1/engineering/packages/CA_NATIVE_PHASE_R300_S17_SMOKE04/card.json'
    old = load(old_path)
    assert sha(ROOT / old_path) == '1fe30783bb04fb79a3fc7e17b21e946be9cb0c58223258dd7a51dfda3898b086'
    assert hashes(old['sources_sha256']) == 25
    first = None
    cards = []
    for wall, digest in EXPECTED.items():
        run = 'CA_NATIVE_PHASE_R300_S17_CYCLES_W' + str(wall) + '_01'
        p = ENG / 'packages' / run / 'card.json'
        c = load(p)
        assert sha(ROOT / p) == digest
        assert c['baseline_commit'] == binding['baseline_commit'] and c['status'] == 'PREPARED_NOT_RELEASED'
        assert c['runtime_authorization_generated'] is False
        assert c['spec']['run_id'] == run and c['spec']['end_s'] == 1272
        assert c['spec']['first_red_mandatory_checkpoint_s'] == 1207
        assert c['spec']['first_red_mandatory_pause'] is False and c['spec']['within_run_checkpoint_continuation'] is True
        assert c['spec']['complete_cycles_target'] == 3 and c['spec']['automatic_retry'] is False
        assert c['resources'] == {'wall_limit_s': wall, 'startup_limit_s': 60, 'run_limit_bytes': 300000000, 'minimum_free_bytes': 5000000000}
        assert all(type(v) is int for v in c['resources'].values())
        hashes(c['sources_sha256']);hashes(c['prepared_input_sha256']);hashes(c['inherited_inputs_sha256'])
        assert c['environment'] == old['environment'] and c['network_sha256'] == old['network_sha256']
        assert c['interpretation'] == {'native_safety_proven': False, 'rate_qualified': False, 'long_term_service_qualified': False}
        assert not (ROOT / c['output']).parent.exists()
        assert not (ROOT / TASK / 'authorization' / run / 'AUTHORIZATION_NATIVE_EXECUTION.json').exists()
        assert not (ROOT / ENG / 'releases' / run / 'EXECUTION_RELEASE.json').exists()
        package = ROOT / c['package']
        xml = ET.parse(package / 'scenario.sumocfg').getroot()
        assert xml.find('./time/end').get('value') == '1272' and xml.find('./time/step-length').get('value') == '1'
        logic = ET.parse(package / 'scenario.add.xml').getroot().find("tlLogic[@programID='CA_C24']")
        assert [(q.get('state'), q.get('duration'), q.get('next')) for q in logic] == [('G', '3', '1'), ('y', '3', '2'), ('r', '18', '0')]
        demand = (package / 'demand.rou.xml').read_bytes()
        assert demand == (ROOT / old['package'] / 'demand.rou.xml').read_bytes()
        if first is None:
            first = c
        else:
            assert c['spec'] == {**first['spec'], 'run_id': run}
            assert c['sources_sha256'] == first['sources_sha256']
            for name in ['demand.rou.xml', 'scenario.add.xml', 'scenario.sumocfg']:
                assert (package / name).read_text().replace(run, first['spec']['run_id']) == (ROOT / first['package'] / name).read_text()
        cards.append({'run_id': run, 'wall_budget_s': wall, 'card_sha256': digest})
    adapter = (ROOT / 'src/candidate_a_native_budget_cycles_20261012/adapter.py').read_text()
    bridge = (ROOT / 'src/candidate_a_native_budget_cycles_20261012/bridge.py').read_text()
    for fragment in ['phases[2][1], 0', 'time_s in (1224,1248)', 'MANDATORY_CHECKPOINT_NOT_RELEASED',
                     'FIRST_RED_CHECKPOINT_MISSING', 'before & after', 'actual_acceleration_m_s2',
                     'excluded_before_only_ids', 'THREE_CYCLES_INCOMPLETE']:
        assert fragment in adapter, fragment
    for fragment in ['for t in range(1272):', 'if t in (1224,1248):', 'FIRST_RED_CHECKPOINT_PROVISIONAL_UNTIL_EOF',
                     'with (output/\'first_red_checkpoint.json\').open(\'x\')', 'os.fsync(f.fileno())',
                     "require(t==1271,'unexpected diagnostic pause')", "getNextSwitch(TLS)==1272"]:
        assert fragment in bridge, fragment
    # Subsequentnativegreen boundary branch must perform admission only, with no setter.
    branch = bridge.split('if t in (1224,1248):', 1)[1].split('before=adapter.prepare_step', 1)[0]
    assert 'admission(' in branch and 'request_phase' not in branch
    assert bridge.index('f.flush();os.fsync(f.fileno())\n    adapter.checkpoint_verified=True') > bridge.index("open('x')")
    source_trace = load(TASK / 'design/SOURCE_TRACE_V1.json')
    assert source_trace['source_commit'] == 'fa7df22d7f1c4ae245192ecc32410a49f1ffb2a3'
    excerpts = [e['text'] for s in source_trace['sources'] for e in s['excerpts']]
    assert any('writeOutput();' in e and 'myStep += DELTA_T;' in e for e in excerpts)
    assert any('MSFCDExport::write' in e and 'myStep' in e for e in excerpts)
    for source in source_trace['sources']:
        assert sha(ROOT / source['original_receipt']) == source['receipt_sha256']
    network = ROOT / 'artifacts/stage6_baseline_localization_20260921_v1/LOC_M3350_S17/engineering/build_attempts/TV_BUILD01/network.net.xml'
    assert sha(network) == first['network_sha256']
    net = ET.parse(network).getroot()
    internal = net.find("edge[@id=':ramp_mid_0']/lane[@id=':ramp_mid_0_0']")
    assert float(internal.get('length')) == 81.98 > 55.55555555555556 + 2.6
    connection = [n.attrib for n in net.findall('connection') if n.get('from') == 'ramp_storage']
    assert connection == [{'from': 'ramp_storage', 'to': 'ramp_accel', 'fromLane': '0', 'toLane': '0', 'via': ':ramp_mid_0_0', 'tl': 'ramp_mid', 'linkIndex': '0', 'dir': 's', 'state': 'O'}]
    receipt = load(ENG / 'OFFLINE_VERIFICATION_RECEIPT_V3.json')
    assert receipt['V3']['methods'] == 11 and receipt['V3']['exit'] == 0
    assert sha(ROOT / receipt['V3']['test_source']) == receipt['V3']['test_source_sha256']
    log = (ROOT / ENG / receipt['V3']['log']).read_text()
    assert 'Ran 11 tests' in log and re.search('^OK$', log, re.MULTILINE)
    assert 'FAILED (failures=1)' in (ROOT / ENG / receipt['V1']['log']).read_text()
    assert 'reconstructed after run' in receipt['V2']['source_record_method']
    return {'status': 'PASS_BOUNDED_OFFLINE_PRELAUNCH_DATA_REVIEW_ONLY', 'engineering_files_verified': 59,
            'protected_files_verified': 536, 'old_SMOKE04_sources_verified': 25, 'cards': cards,
            'input_source_seed_horizon_equal_across_budgets': True,
            'nominal_E_not_actual_N': True, 'native4thgreen_not_executed_at1272': True,
            'engineering11tests_log_reviewed_not_rerun': True, 'old8tests_not_rerun': True,
            'actual_native_runs': 0, 'clean_checkout': 'NOT_RUN',
            'environment_declared_binding_compared_not_fresh_version_process': True,
            'limitations': ['Offline/static tests not physical safety, native discharge, runtime or rate qualification',
                            '1207 checkpoint logs provisional until final EOF',
                            'Braking checks before-intersection-after and after population; exited final motion excluded',
                            'Parent CLI warnings outside four native streams online coverage',
                            'Formal protocol0B; only technical/exploratory analysis']}


if __name__ == '__main__':
    print(json.dumps(audit(), indent=2))

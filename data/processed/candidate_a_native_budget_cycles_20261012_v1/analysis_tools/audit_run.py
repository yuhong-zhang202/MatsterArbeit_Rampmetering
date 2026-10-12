"""Independent read-only native-output audit; no SUMO/TraCI imports or writes.

FCD timestamp t is the post-movement state of (t,t+1], not ACK t.
Default mode prints requirements. --raw requires a frozen whole-run manifest.
"""
import argparse
import gzip
import hashlib
import json
import math
from pathlib import Path
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[4]
STORAGE = 'ramp_storage_0'
INTERNAL = ':ramp_mid_0_0'
CONTROL = 1200
END = 1272
CARDS = {'CA_NATIVE_PHASE_R300_S17_CYCLES_W300_01': '25dccfa39d3ff716823f6ce7ceee18eba1c0b8c6393ae464b6db1d2b61c70386',
         'CA_NATIVE_PHASE_R300_S17_CYCLES_W360_01': '1289b33f53f54e2cdf4bcd504fc0774c4c4923c7ae1f9c31d5bf34c9ca848090',
         'CA_NATIVE_PHASE_R300_S17_CYCLES_W420_01': '624f774f5308aa00ff69d42f4436e9ffcc41a462e4cce1b8d0462c051fc799c1',
         'CA_NATIVE_PHASE_R300_S17_CYCLES_W480_01': '3ce1e92e7a21ea4b78aaccbcdaca19136cf67fb917d860a71f820b6de97799b3'}


class Unknown(ValueError):
    pass


def require(ok, message):
    if not ok:
        raise Unknown(message)


def sha(path):
    h = hashlib.sha256()
    with path.open('rb') as f:
        for block in iter(lambda: f.read(1024 * 1024), b''):
            h.update(block)
    return h.hexdigest()


def integer(value):
    return type(value) is int


def finite(value):
    return type(value) in (int, float) and math.isfinite(value)


def fcd_frames(path):
    frames = {}
    opener = gzip.open if str(path).endswith('.gz') else open
    with opener(path, 'rb') as stream:
        for _, elem in ET.iterparse(stream, events=('end',)):
            if elem.tag != 'timestep':
                continue
            t = float(elem.get('time'))
            require(t.is_integer() and int(t) not in frames, 'FCD_DUPLICATE_OR_FRACTIONAL_TIME')
            world = {}
            for vehicle in elem.findall('vehicle'):
                vid = vehicle.get('id')
                require(isinstance(vid, str) and vid not in world, 'FCD_DUPLICATE_ID')
                speed = float(vehicle.get('speed'))
                lane = vehicle.get('lane')
                require(finite(speed) and 0 <= speed <= 55.56156 and bool(lane), 'FCD_INVALID_STATE')
                world[vid] = {'lane_id': lane, 'speed_m_s': speed}
            frames[int(t)] = world
            elem.clear()
    return frames


def tls_frames(path):
    frames = {}
    for _, elem in ET.iterparse(path, events=('end',)):
        if elem.tag != 'tlsState' or elem.get('id') != 'ramp_mid':
            continue
        t = float(elem.get('time'))
        require(t.is_integer() and int(t) not in frames, 'TLS_DUPLICATE_OR_FRACTIONAL_TIME')
        frames[int(t)] = {'phase': int(elem.get('phase')), 'state': elem.get('state'),
                          'program': elem.get('programID')}
        elem.clear()
    return frames


def records(path):
    with path.open() as stream:
        return [json.loads(line) for line in stream if line.strip()]


def world_match(observed, fcd, reason):
    require(isinstance(observed, dict) and set(observed) == set(fcd), reason + '_POPULATION')
    for vid, state in observed.items():
        require(vid.split('_', 1)[0] in ('M', 'R', 'U', 'X'), reason + '_ROLE')
        require(state['lane_id'] == fcd[vid]['lane_id'], reason + '_LANE')
        # Native FCD precision2; ledger speeds are unrounded.
        require(finite(state['speed_m_s']) and abs(state['speed_m_s'] - fcd[vid]['speed_m_s']) <= .005001,
                reason + '_SPEED')


def expected(t):
    if t < 600:
        return 'A_OPEN', 0, 'G', -1
    if t < 1200:
        return 'CA_C8', 1 if t < 603 else 2, 'y' if t < 603 else 'r', -1
    elapsed = (t - 1200) % 24
    index = 0 if elapsed < 3 else 1 if elapsed < 6 else 2
    return 'CA_C24', index, ('G', 'y', 'r')[index], (t - 1200) // 24


def audit_measurements(pre, post, fcd, tls):
    """Return measured counts only when all observed rows bind independently."""
    require(isinstance(pre, list) and isinstance(post, list), 'ROWS_SCHEMA')
    count = len(post)
    require(count <= END and len(pre) >= count and set(fcd) == set(range(count)) and set(tls) == set(range(count)),
            'MISSING_DUPLICATE_OR_EXTRA_FCD_TLS_ROWS')
    crossed = set()
    crossings = []
    brake_ids = 0
    excluded = 0
    alarms = []
    for t, row in enumerate(post):
        require(integer(row.get('time_begin_s')) and row['time_begin_s'] == t and row.get('time_end_s') == t + 1,
                'POST_GAP_DUPLICATE_OR_ALIGNMENT')
        require(row.get('accounting_complete') is True, 'UNRECONCILED_ADVANCED_PREFIX')
        p = pre[t]
        require(integer(p.get('time_s')) and p['time_s'] == t, 'PRE_GAP_DUPLICATE_OR_ALIGNMENT')
        bound = p.get('bound_snapshot')
        require(isinstance(bound, dict) and bound.get('time_s') == t, 'PRE_BOUND_SCHEMA')
        before = {} if t == 0 else fcd[t - 1]
        after = fcd[t]
        world_match(bound['world'], before, 'PRE_VS_FCD_T_MINUS1')
        world_match(row.get('post_world'), after, 'POST_VS_FCD_T')
        program, phase, motion, cycle = expected(t)
        require(tls[t] == {'program': program, 'phase': phase, 'state': motion}, 'NATIVE_TLS_MOTION_MISMATCH')
        require(bound.get('program') == program and bound.get('motion') == row.get('motion') == motion,
                'BOUND_MOTION_PROGRAM_MISMATCH')
        require(bound.get('cycle_id') == cycle, 'CYCLE_ID_MISMATCH')
        observation = row.get('phase_observation')
        require(isinstance(observation, dict) and integer(observation.get('phase_before')) and integer(observation.get('phase_after')),
                'PHASE_TYPE_UNKNOWN')
        require(observation['phase_before'] == bound['phase_before'] and observation['state_before'] == bound['state_before'] and
                observation['next_switch_before_s'] == bound['next_switch_before_s'], 'PRE_PHASE_BINDING')
        require(observation['phase_after'] == phase and observation['state_after'] == motion, 'POST_PHASE_BINDING')
        # Phase at t+1 may still be the previous raw phase at a pending t+1 event.
        if t >= 1200:
            start = 1200 + cycle * 24
            nxt = start + (3 if phase == 0 else 6 if phase == 1 else 24)
            require(observation['next_switch_after_s'] == nxt, 'POST_NEXT_SWITCH_MISMATCH')
        storage = {vid for vid, value in before.items() if value['lane_id'] == STORAGE}
        internal_before = {vid for vid, value in before.items() if value['lane_id'] == INTERNAL}
        internal_after = {vid for vid, value in after.items() if value['lane_id'] == INTERNAL}
        require(set(bound.get('storage', [])) == storage and set(bound.get('internal', [])) == internal_before,
                'PRE_LOCAL_VS_FCD_COVERAGE')
        entrants = internal_after - internal_before
        require(entrants <= storage, 'UNBOUND_INTERNAL_ENTRANT')
        require(all(vid.startswith('R_') for vid in entrants | storage | internal_before | internal_after), 'NON_R_STOPLINE_ID')
        # The unique81.98m controlled internal is longer than conditional one-step58.16m max advance.
        skipped = {vid for vid in storage if vid not in after or after[vid]['lane_id'] not in (STORAGE, INTERNAL)}
        require(not skipped, 'SKIPPED_INTERNAL_UNMEASURABLE')
        require(not crossed.intersection(entrants), 'DUPLICATE_STOPLINE_CROSSING')
        independent = [{'vehicle_id': vid, 'crossing_time_lower_s': t, 'crossing_time_upper_s': t + 1,
                        'time_interval': '(lower,upper]', 'cycle_id': cycle, 'motion_signal_state': motion}
                       for vid in sorted(entrants)]
        require(row.get('actual_crossings') == independent, 'FCD_VS_LEDGER_CROSSINGS_MISMATCH')
        crossed.update(entrants)
        crossings.extend(independent)
        if motion == 'r' and entrants:
            alarms.append('RED_CROSSING')
        changes = row.get('identity_change', {})
        before_only = set(before) - set(after)
        after_only = set(after) - set(before)
        require(set(changes.get('before_only_ids', [])) == before_only and set(changes.get('after_only_ids', [])) == after_only,
                'POPULATION_CHANGE_BINDING')
        require(before_only <= set(changes.get('arrived_ids', [])) and after_only <= set(changes.get('departed_ids', [])),
                'ARRIVED_DEPARTED_BINDING')
        brake = row.get('braking_observation')
        require(isinstance(brake, dict), 'MISSING_BRAKING_OBSERVATION')
        shared = set(before) & set(after)
        require(set(brake.get('speed_difference_ids', [])) == set(brake.get('speed_difference_m_s2', {})) == shared,
                'BRAKE_DIFFERENCE_COVERAGE')
        require(set(brake.get('after_acceleration_ids', [])) == set(brake.get('actual_acceleration_m_s2', {})) == set(after),
                'BRAKE_ACCELERATION_COVERAGE')
        require(set(brake.get('excluded_before_only_ids', [])) == before_only and set(brake.get('arrived_ids', [])) == set(changes.get('arrived_ids', [])),
                'BRAKE_EXIT_EXCLUSION_BINDING')
        for vid, value in brake['speed_difference_m_s2'].items():
            actual = row['post_world'][vid]['speed_m_s'] - bound['world'][vid]['speed_m_s']
            require(finite(value) and abs(value - actual) < 1e-10, 'BRAKE_DIFFERENCE_VALUE_BINDING')
            if value < -4.5 - 1e-6:
                alarms.append('ORDINARY_BRAKING_EXCEEDED')
        for value in brake['actual_acceleration_m_s2'].values():
            require(finite(value), 'UNKNOWN_ACCELERATION_VALUE')
            if value < -4.5 - 1e-6:
                alarms.append('ORDINARY_ACCELERATION_EXCEEDED')
        brake_ids += len(shared)
        excluded += len(before_only)
        counters = row.get('native_event_counters')
        require(isinstance(counters, dict) and set(counters) == {'colliding_vehicles', 'starting_teleports', 'ending_teleports'} and
                all(integer(v) and v >= 0 for v in counters.values()), 'NATIVE_COUNTER_SCHEMA')
        if any(counters.values()):
            alarms.append('COLLISION_OR_TELEPORT')
        if row.get('reasons') or row.get('terminal_reason') or row.get('status', '').startswith('STOP_'):
            alarms.append('REPORTED_POST_STOP')
    control_crossings = [r for r in crossings if r['cycle_id'] >= 0]
    observed = max(0, count - CONTROL)
    per_cycle = []
    for index in range(3):
        begin = CONTROL + index * 24
        seconds = max(0, min(24, count - begin))
        selected = [r for r in control_crossings if r['cycle_id'] == index]
        n = None if seconds == 0 else len(selected)
        per_cycle.append({'cycle_id': index, 'begin_s': begin, 'end_s': begin + 24,
                          'observed_seconds': seconds,
                          'observation': 'NOT_OBSERVED' if seconds == 0 else 'COMPLETE' if seconds == 24 else 'PARTIAL',
                          'completed': seconds == 24, 'N': n,
                          'N_G': None if seconds == 0 else sum(r['motion_signal_state'] == 'G' for r in selected),
                          'N_y': None if seconds == 0 else sum(r['motion_signal_state'] == 'y' for r in selected),
                          'N_r': None if seconds == 0 else sum(r['motion_signal_state'] == 'r' for r in selected),
                          'crossing_ids': [r['vehicle_id'] for r in selected]})
    metrics = {'C': None, 'C_applied': None, 'E': None, 'N': None, 'C_minus_E': None, 'E_minus_N': None}
    if observed:
        metrics.update(C=observed / 12, C_applied=observed / 12, E=2 * (observed // 24), N=len(control_crossings))
        metrics.update(C_minus_E=metrics['C']-metrics['E'], E_minus_N=metrics['E']-metrics['N'])
        ledger = post[-1]['accounting']
        for key in metrics:
            require(finite(ledger.get(key)) and abs(ledger[key] - metrics[key]) <= 1e-10, 'ACCOUNTING_MISMATCH_' + key)
    return {'status': 'BOUND_OBSERVED_ANOMALY' if alarms else 'BOUND_PREFIX_MEASUREMENTS_ONLY',
            'observed_post_steps': count, 'controlled_seconds_observed': observed,
            'control_metrics': metrics, 'cycles': per_cycle, 'crossings': crossings,
            'unique_all_prefix_crossings': len(crossed), 'braking_difference_vehicle_intervals': brake_ids,
            'excluded_before_only_vehicle_intervals': excluded, 'alarms': sorted(set(alarms)),
            'first_red_observed': count >= 1207, 'three_cycles_observed': count == END,
            'safety_qualified': False, 'service_qualified': False}


def classification(receipt, measurements):
    logs = receipt.get('final_logs') or {}
    watchdog = receipt.get('resource_watchdog') or {}
    if logs.get('status') != 'BOUND_NO_OBSERVED_NATIVE_MESSAGE' or watchdog.get('error'):
        return 'STOP_LOG_OR_WATCHDOG_UNKNOWN'
    if measurements['alarms']:
        return 'STOP_OBSERVED_ANOMALY_NOT_BUDGET_REMEDIABLE'
    if receipt.get('last_completed_s') != measurements['observed_post_steps'] or receipt.get('last_accounted_s') != measurements['observed_post_steps']:
        return 'STOP_UNRECONCILED_OR_MISSING_PREFIX_UNKNOWN'
    if receipt.get('status') == 'THREE_CYCLES_OBSERVED_NO_MONITORED_ANOMALY_NOT_QUALIFIED' and measurements['three_cycles_observed']:
        return 'THREE_CYCLES_OBSERVED_NOT_QUALIFIED'
    if receipt.get('error') == 'ValueError:wall resource STOP' and watchdog.get('reason') in (None, 'WALL_LIMIT'):
        return 'RESOURCE_WALL_ONLY_BOUND_TRUNCATED_PREFIX'
    return 'STOP_OTHER_OR_UNKNOWN_NOT_AUTOMATIC_BUDGET_FAILURE'


def audit_raw(path, manifest_path):
    out = Path(path).resolve()
    require(out.name == 'outputs' and out.parent.parent == ROOT / 'data/raw/candidate_a_native_budget_cycles_20261012_v1', 'FOREIGN_RAW_IDENTITY')
    manifest = json.loads(Path(manifest_path).read_text())
    require(manifest.get('raw_immutable_after_owned_process_exit') is True and isinstance(manifest.get('files'), dict), 'UNFROZEN_MANIFEST')
    require(Path(manifest.get('raw_root', '')).as_posix() == str(out.parent.relative_to(ROOT)), 'MANIFEST_ROOT_BINDING')
    actual = {str(p.relative_to(ROOT)) for p in out.parent.rglob('*') if p.is_file()}
    require(actual == set(manifest['files']), 'RAW_MANIFEST_COVERAGE')
    for name, value in manifest['files'].items():
        require(sha(ROOT / name) == value, 'RAW_HASH_DRIFT_' + name)
    receipt = json.loads((out / 'bridge_receipt.json').read_text())
    card = json.loads((out / 'card.json').read_text())
    require(receipt.get('run_id') == card['spec']['run_id'] == out.parent.name and receipt.get('card_sha256') == sha(out / 'card.json'), 'RUN_CARD_IDENTITY')
    require(out.parent.name in CARDS and sha(out / 'card.json') == CARDS[out.parent.name], 'REVIEWED_CARD_BINDING')
    for name, value in card['sources_sha256'].items():
        require(sha(out / 'snapshots' / name) == value, 'EXECUTED_SOURCE_SNAPSHOT_DRIFT')
    pre, post = records(out / 'pre_steps.jsonl'), records(out / 'post_steps.jsonl')
    frames, tls = fcd_frames(out / 'fcd.xml.gz'), tls_frames(out / 'tls_states.xml')
    measurements = audit_measurements(pre, post, frames, tls)
    ack = records(out / 'step_ack.jsonl')
    require(len(ack) == 2 * measurements['observed_post_steps'], 'ACK_PAIR_COVERAGE')
    verified = [r for r in ack if r.get('actual_time_verified') is True]
    require([r.get('actual_readback_s') for r in verified] == list(range(1, measurements['observed_post_steps'] + 1)), 'ACK_PREFIX_BINDING')
    for row in verified:
        require(row.get('ACK_received') is True and row.get('requested_target_s') == row['actual_readback_s'], 'ACK_TARGET_BINDING')
    if measurements['first_red_observed']:
        checkpoint = json.loads((out / 'first_red_checkpoint.json').read_text())
        require(checkpoint.get('time_s') == checkpoint.get('last_accounted_s') == 1207 and
                checkpoint.get('log_scope') == 'PROVISIONAL_NATIVE_CAPTURE_FINAL_EOF_REQUIRED', 'CHECKPOINT_BINDING')
        require(receipt.get('first_red_checkpoint_verified') is True, 'CHECKPOINT_NOT_RELEASED')
    if measurements['controlled_seconds_observed']:
        cycles = receipt.get('cycles')
        require(isinstance(cycles, list) and len(cycles) == sum(c['observed_seconds'] > 0 for c in measurements['cycles']), 'FINAL_CYCLE_COVERAGE')
        for ledger, measured in zip(cycles, measurements['cycles']):
            for key in ('cycle_id', 'begin_s', 'end_s', 'completed', 'N_G', 'N_y', 'N_r', 'crossing_ids'):
                require(ledger.get(key) == measured[key], 'FINAL_CYCLE_MISMATCH_' + key)
    measurements['run_classification'] = classification(receipt, measurements)
    measurements['run_id'] = out.parent.name
    measurements['card_sha256'] = sha(out / 'card.json')
    measurements['raw_files_verified'] = len(actual)
    measurements['source_manifest_sha256'] = sha(Path(manifest_path))
    measurements['loop_terminal_elapsed_s'] = receipt.get('loop_terminal_elapsed_s')
    measurements['monitored_elapsed_through_cleanup_s'] = receipt.get('monitored_elapsed_through_cleanup_s')
    measurements['limitations'] = ['Technical smoke only; no universal safety or service qualification',
                                  'FCD lane/speed snapshots validate crossing count, not subsecond timestamps',
                                  'Front entry into unique internal lane, not downstream E1 or rear clearance',
                                  'Braking excludes last motion of arrived/before-only vehicles',
                                  'Native logger excludes parent CLI warning output from online STOP',
                                  'Source/binary compilation equivalence not verified']
    return measurements


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--raw', type=Path)
    parser.add_argument('--manifest', type=Path)
    args = parser.parse_args()
    if not args.raw:
        result = {'status': 'PRELAUNCH_MEASUREMENT_TOOL_NO_RUNTIME_RESULT',
                  'requirements': 'frozen manifest plus explicitly selected completed new raw outputs; no native execution',
                  'FCD_alignment': 'FCD t post-movement maps to ACK t+1', 'safety_qualified': False}
    else:
        try:
            require(args.manifest is not None, 'FROZEN_MANIFEST_REQUIRED')
            result = audit_raw(args.raw, args.manifest)
        except Exception as exc:
            result = {'status': 'UNKNOWN_INDEPENDENT_DATA_OR_OBSERVATION_BINDING',
                      'reason': type(exc).__name__ + ':' + str(exc),
                      'control_metrics': None, 'safety_qualified': False, 'service_qualified': False}
    print(json.dumps(result, indent=2, allow_nan=False))
    if result.get('status', '').startswith('UNKNOWN'):
        raise SystemExit(1)

"""Known deterministic tiny-world cases, not SUMO or engineering-suite reruns."""
from copy import deepcopy
import gzip
import importlib.util
from pathlib import Path
import tempfile
import unittest

path = Path(__file__).with_name('audit_run.py')
spec = importlib.util.spec_from_file_location('independent_cycles_audit', path)
audit = importlib.util.module_from_spec(spec)
spec.loader.exec_module(audit)


def fixture(count, per_cycle=1):
    pre, post, fcd, tls = [], [], {}, {}
    previous = {}
    for t in range(count):
        world = {f'R_flow.{i}': {'lane_id': audit.STORAGE, 'speed_m_s': 0.}
                 for i in range(per_cycle * 3)}
        for i in range(per_cycle * 3):
            if t >= 1200 + (i // per_cycle) * 24:
                world[f'R_flow.{i}']['lane_id'] = audit.INTERNAL
        program, phase, motion, cycle = audit.expected(t)
        elapsed = (t - 1200) % 24
        next_after = (1200 + cycle * 24 + (3 if phase == 0 else 6 if phase == 1 else 24)) if cycle >= 0 else (603 if phase == 1 else 1203)
        before_phase = (phase - 1) % 3 if t >= 1200 and elapsed in (0, 3, 6) and t != 1200 else phase
        before_state = ('G', 'y', 'r')[before_phase]
        storage = {v for v, s in previous.items() if s['lane_id'] == audit.STORAGE}
        internal_before = {v for v, s in previous.items() if s['lane_id'] == audit.INTERNAL}
        internal_after = {v for v, s in world.items() if s['lane_id'] == audit.INTERNAL}
        entrants = internal_after - internal_before
        bracket = [{'vehicle_id': v, 'crossing_time_lower_s': t, 'crossing_time_upper_s': t + 1,
                    'time_interval': '(lower,upper]', 'cycle_id': cycle, 'motion_signal_state': motion} for v in sorted(entrants)]
        bound = {'time_s': t, 'world': deepcopy(previous), 'storage': sorted(storage), 'internal': sorted(internal_before),
                 'program': program, 'motion': motion, 'cycle_id': cycle, 'phase_before': before_phase,
                 'state_before': before_state, 'next_switch_before_s': t if before_phase != phase else next_after}
        pre.append({'time_s': t, 'bound_snapshot': bound})
        observed = max(0, t + 1 - 1200)
        n = min(3, ((t - 1200) // 24) + 1) * per_cycle if t >= 1200 else 0
        ledger = {'C': observed / 12, 'C_applied': observed / 12, 'E': 2 * (observed // 24), 'N': n,
                  'C_minus_E': observed / 12 - 2 * (observed // 24), 'E_minus_N': 2 * (observed // 24) - n}
        shared = set(previous) & set(world)
        post.append({'time_begin_s': t, 'time_end_s': t + 1, 'accounting_complete': True,
                     'status': 'RECONCILED_DIAGNOSTIC_ONLY', 'post_world': deepcopy(world), 'motion': motion,
                     'phase_observation': {'phase_before': before_phase, 'state_before': before_state,
                       'next_switch_before_s': bound['next_switch_before_s'], 'phase_after': phase,
                       'state_after': motion, 'next_switch_after_s': next_after},
                     'actual_crossings': bracket, 'identity_change': {'before_only_ids': [],
                       'after_only_ids': sorted(set(world) - set(previous)), 'arrived_ids': [],
                       'departed_ids': sorted(set(world) - set(previous))},
                     'braking_observation': {'speed_difference_ids': sorted(shared),
                       'after_acceleration_ids': sorted(world), 'excluded_before_only_ids': [], 'arrived_ids': [],
                       'speed_difference_m_s2': {v: 0. for v in shared}, 'actual_acceleration_m_s2': {v: 0. for v in world}},
                     'native_event_counters': {'colliding_vehicles': 0, 'starting_teleports': 0, 'ending_teleports': 0},
                     'accounting': ledger})
        fcd[t] = deepcopy(world)
        tls[t] = {'program': program, 'phase': phase, 'state': motion}
        previous = deepcopy(world)
    return pre, post, fcd, tls


class MeasurementTests(unittest.TestCase):
    def test_unobserved_null_observed_zero_partial_and_full(self):
        unobserved = audit.audit_measurements(*fixture(1200, 0))
        zero = audit.audit_measurements(*fixture(1201, 0))
        partial = audit.audit_measurements(*fixture(1207))
        full = audit.audit_measurements(*fixture(1272))
        self.assertTrue(all(v is None for v in unobserved['control_metrics'].values()))
        self.assertEqual(zero['control_metrics']['N'], 0)
        self.assertEqual(zero['cycles'][0]['observation'], 'PARTIAL')
        self.assertEqual(partial['control_metrics']['C'], 7 / 12)
        self.assertEqual(partial['control_metrics']['E'], 0)
        self.assertEqual(partial['control_metrics']['N'], 1)
        self.assertIsNone(partial['cycles'][1]['N'])
        self.assertEqual(full['control_metrics']['N'], 3)
        self.assertEqual(full['control_metrics']['E'], 6)
        self.assertTrue(all(c['completed'] for c in full['cycles']))

    def test_N_above_nominal_is_measured_not_forced_or_rejected(self):
        result = audit.audit_measurements(*fixture(1272, 3))
        self.assertEqual((result['control_metrics']['N'], result['control_metrics']['E']), (9, 6))
        self.assertEqual(result['control_metrics']['E_minus_N'], -3)

    def test_missing_duplicate_unbound_skipped_and_phase_rows_unknown(self):
        for defect in ('missing', 'duplicate', 'unbound', 'skipped', 'phase', 'misaligned'):
            data = fixture(1201)
            pre, post, fcd, tls = data
            if defect == 'missing': del fcd[1200]
            if defect == 'duplicate': post[-1]['actual_crossings'] *= 2
            if defect == 'unbound': pre[-1]['bound_snapshot']['storage'] = []
            if defect == 'skipped': fcd[1200]['R_flow.0']['lane_id'] = 'ramp_accel_0';post[-1]['post_world']['R_flow.0']['lane_id'] = 'ramp_accel_0'
            if defect == 'phase': tls[1200]['state'] = 'r'
            if defect == 'misaligned': post[-1]['time_end_s'] = 1200
            with self.subTest(defect=defect), self.assertRaises(audit.Unknown):
                audit.audit_measurements(*data)

    def test_xml_FCD_time_after_movement_aligns_ACK_t_plus_one(self):
        with tempfile.TemporaryDirectory() as tmp:
            p = Path(tmp) / 'fcd.xml.gz'
            with gzip.open(p, 'wt') as f:f.write('<fcd-export><timestep time="1200.00"><vehicle id="R_flow.0" speed="1.23" lane=":ramp_mid_0_0"/></timestep></fcd-export>')
            frames = audit.fcd_frames(p)
            self.assertEqual(frames[1200]['R_flow.0']['lane_id'], audit.INTERNAL)
            result = audit.audit_measurements(*fixture(1201))
            r = result['crossings'][0]
            self.assertEqual((r['crossing_time_lower_s'], r['crossing_time_upper_s']), (1200, 1201))

    def test_resource_classification_requires_known_logs_and_no_anomaly(self):
        observed = audit.audit_measurements(*fixture(1201))
        receipt = {'status': 'ABORTED_UNKNOWN', 'error': 'ValueError:wall resource STOP',
                   'last_completed_s': 1201, 'last_accounted_s': 1201,
                   'final_logs': {'status': 'BOUND_NO_OBSERVED_NATIVE_MESSAGE'},
                   'resource_watchdog': {'reason': None, 'error': None}}
        self.assertEqual(audit.classification(receipt, observed), 'RESOURCE_WALL_ONLY_BOUND_TRUNCATED_PREFIX')
        receipt['final_logs']['status'] = 'UNKNOWN'
        self.assertEqual(audit.classification(receipt, observed), 'STOP_LOG_OR_WATCHDOG_UNKNOWN')
        receipt['final_logs']['status'] = 'BOUND_NO_OBSERVED_NATIVE_MESSAGE'
        observed['alarms'] = ['RED_CROSSING']
        self.assertEqual(audit.classification(receipt, observed), 'STOP_OBSERVED_ANOMALY_NOT_BUDGET_REMEDIABLE')


if __name__ == '__main__':
    unittest.main()

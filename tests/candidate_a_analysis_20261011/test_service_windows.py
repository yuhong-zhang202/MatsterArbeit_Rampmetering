"""Offline regression for observed-zero, missing and partial service evidence."""
import csv
import importlib.util
import io
import json
from pathlib import Path
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / 'data/processed/candidate_a_qualification_20261008_v1/audit_r300_a07_actual.py'
spec = importlib.util.spec_from_file_location('candidate_a_raw_audit', SOURCE)
audit = importlib.util.module_from_spec(spec)
spec.loader.exec_module(audit)
FIELDS = ('C_observed', 'C_applied_observed', 'E_observed', 'N_observed',
          'command_latency', 'quantization', 'physical_shortfall')


def row(t, c=0, a=0, e=0, n=0, supply='True'):
    return dict(time_begin_s=t, C_delta=c, C_applied_delta=a,
                E_delta=e, N_delta=n, storage_supply=supply)


class ServiceWindowTests(unittest.TestCase):
    def test_observed_zero_is_numeric_not_missing(self):
        actual = audit.service([row(1200)], 1200, 1500)
        self.assertEqual(actual['observed_steps'], 1)
        for field in FIELDS:
            self.assertIsNotNone(actual[field])
            self.assertEqual(actual[field], 0)
        self.assertEqual(actual['status'], 'NOT_TESTED_INCOMPLETE_WINDOW')
        self.assertIsNone(actual['tracking_error'])

    def test_completely_unobserved_is_null(self):
        actual = audit.service([row(1200)], 1500, 1800)
        self.assertEqual(actual['observed_steps'], 0)
        for field in FIELDS + ('tracking_error',):
            self.assertIsNone(actual[field])
        self.assertFalse(actual['full_window'])
        self.assertFalse(actual['sustained_supply_verified'])
        self.assertEqual(actual['status'], 'NOT_TESTED_INCOMPLETE_WINDOW')

    def test_partial_six_second_prefix_preserves_actual_sums(self):
        rows = [row(t, 300/3600, 300/3600, 0, int(t == 1200))
                for t in range(1200, 1206)]
        actual = audit.service(rows, 1200, 1500)
        self.assertEqual(actual['observed_steps'], 6)
        expected = (.5, .5, 0, 1, 0, .5, -1)
        for field, value in zip(FIELDS, expected):
            self.assertAlmostEqual(actual[field], value)
        self.assertIsNone(actual['tracking_error'])
        self.assertEqual(actual['status'], 'NOT_TESTED_INCOMPLETE_WINDOW')

    def test_json_null_and_csv_blank_preserve_numeric_zero(self):
        records = [audit.service([], 0, 300), audit.service([row(0)], 0, 300)]
        decoded = json.loads(json.dumps(records))
        buffer = io.StringIO(newline='')
        writer = csv.DictWriter(buffer, fieldnames=list(records[0]))
        writer.writeheader()
        writer.writerows(records)
        serialized = list(csv.DictReader(io.StringIO(buffer.getvalue())))
        for field in FIELDS:
            self.assertIsNone(decoded[0][field])
            self.assertEqual(serialized[0][field], '')
            self.assertEqual(decoded[1][field], 0)
            self.assertNotEqual(serialized[1][field], '')
            self.assertEqual(float(serialized[1][field]), 0)

    def test_original_inclusive_ten_percent_and_supply_screen(self):
        rows = [row(t, 1, 1, 1, 1) for t in range(10)]
        rows[-1]['N_delta'] = 0
        actual = audit.service(rows, 0, 10)
        self.assertEqual(actual['tracking_error'], .1)
        self.assertEqual(actual['status'], 'PASS')
        rows[-2]['N_delta'] = 0
        self.assertEqual(audit.service(rows, 0, 10)['status'], 'FAIL')
        rows[0]['storage_supply'] = 'False'
        actual = audit.service(rows, 0, 10)
        self.assertIsNone(actual['tracking_error'])
        self.assertEqual(actual['status'], 'NOT_TESTED_SUPPLY')

    def test_exclusive_artifact_write_preserves_existing_bytes(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / 'evidence.json'
            audit.save(path, '{"value":null}\n')
            audit.save(path, '{"value":null}\n')
            with self.assertRaises(AssertionError):
                audit.save(path, '{"value":0}\n')
            self.assertEqual(path.read_text(), '{"value":null}\n')


if __name__ == '__main__':
    unittest.main()

"""Offline regression tests for Issue #6's recorded-prefix audit."""

from __future__ import annotations

import importlib.util
import math
import unittest
from pathlib import Path

SCRIPT = Path(__file__).resolve().parents[2] / "scripts/candidate_a_safety_contract_20261011_v1/audit_a07.py"
SPEC = importlib.util.spec_from_file_location("candidate_a_a07_audit", SCRIPT)
assert SPEC and SPEC.loader
audit_module = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(audit_module)


def windows_fixture(first_steps: int, first_values: dict):
    fields = audit_module.WINDOW_FIELDS
    windows = []
    rows = []
    for index in range(6):
        steps = first_steps if index == 0 else 0
        values = first_values if index == 0 else {field: None for field in fields}
        record = {
            "observed_steps": steps,
            "full_window": False,
            "status": "NOT_TESTED_INCOMPLETE_WINDOW",
            **values,
        }
        windows.append(record)
        rows.append({
            "observed_steps": str(steps),
            "status": record["status"],
            **{field: "" if values[field] is None else str(values[field]) for field in fields},
        })
    return windows, rows


class AuditA07Tests(unittest.TestCase):
    def test_recorded_gap_and_one_constant_sensitivity(self):
        speed = 0.04573822948686786
        gap = 1.001999189766508
        current = audit_module.required_gap(speed, 1.0, 4.5)
        one_metre = audit_module.required_gap(speed, 1.0, 4.5, 1.0)
        self.assertTrue(math.isclose(current, 1.1459706723353782, abs_tol=1e-12))
        self.assertTrue(math.isclose(gap - current, -0.14397148256887027, abs_tol=1e-12))
        self.assertTrue(math.isclose(one_metre, 1.0459706723353782, abs_tol=1e-12))
        self.assertLess(gap - one_metre, 0)

    def test_measured_zero_is_not_missing(self):
        values = {field: 0 for field in audit_module.WINDOW_FIELDS}
        values["tracking_error"] = None
        windows, rows = windows_fixture(6, values)
        self.assertEqual(audit_module.validate_windows(windows, rows), [6, 0, 0, 0, 0, 0])
        self.assertEqual(rows[0]["E_observed"], "0")

    def test_partial_window_retains_values_without_qualification(self):
        values = {field: 0 for field in audit_module.WINDOW_FIELDS}
        values.update(C_observed=0.5, C_applied_observed=0.5, N_observed=1, tracking_error=None)
        windows, rows = windows_fixture(6, values)
        self.assertEqual(audit_module.validate_windows(windows, rows)[0], 6)
        self.assertFalse(windows[0]["full_window"])
        self.assertIsNone(windows[0]["tracking_error"])

    def test_fully_unobserved_measurements_must_be_null(self):
        values = {field: None for field in audit_module.WINDOW_FIELDS}
        windows, rows = windows_fixture(0, values)
        self.assertEqual(audit_module.validate_windows(windows, rows), [0] * 6)
        windows[1]["E_observed"] = 0
        rows[1]["E_observed"] = "0"
        with self.assertRaisesRegex(ValueError, "unobserved measurement"):
            audit_module.validate_windows(windows, rows)

    def test_bound_recorded_inputs(self):
        result = audit_module.audit()
        self.assertEqual(result["status"], "PASS")
        self.assertEqual(result["guard_witnesses"], 42)
        self.assertEqual(result["unsafe_ids"], ["R_flow.1"])
        self.assertEqual(result["service_observed_steps"], [6, 0, 0, 0, 0, 0])


if __name__ == "__main__":
    unittest.main()

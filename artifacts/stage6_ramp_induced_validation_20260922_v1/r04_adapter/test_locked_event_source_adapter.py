from __future__ import annotations

import hashlib
import json
import tempfile
import unittest
from pathlib import Path

import locked_event_source_adapter as source
import ri3350_control_adapter as adapter


class LockedEventSourceAdapterTests(unittest.TestCase):
    def setUp(self):
        self.analyzer = adapter.load_locked_analyzer()
        self.temp = tempfile.TemporaryDirectory()
        raw_manifest = Path(self.temp.name) / "synthetic-output-manifest.json"
        raw_manifest.write_text('{"fixture":"synthetic-not-raw"}\n', encoding="utf-8")
        paths = {"method": adapter.METHOD, "locked_analyzer": adapter.LOCKED_ANALYZER,
                 "design": adapter.DESIGN, "output_roles": adapter.OUTPUT_ROLES,
                 "raw_manifest": raw_manifest}
        self.binding = {"run_id": "SYNTHETIC_CTRL", "run_label": "CTRL",
                        "paths": paths,
                        "sha256": {key: source.sha256_file(path) for key, path in paths.items()}}
        self.metrics = []
        for cell in source.CELL_IDS:
            for profile in source.EXPECTED_PROFILES:
                alpha = self.analyzer.PROFILES[profile][0]
                for bin_id in source.BIN_IDS:
                    low = profile == "P" and cell == 14 and bin_id in (10, 11, 12)
                    self.metrics.append({"run": "CTRL", "run_id": "SYNTHETIC_CTRL",
                        "profile": profile, "cell": cell, "bin": bin_id,
                        "valid_bin": True,
                        "mean_model_reference_ratio": (alpha if low else 0.9),
                        "sample_slow_fraction": (0.5 if low else 0.0),
                        "labels_nslow_ge2": (15 if low else 0),
                        "low_state_bin": bool(low)})
        self.event = {"event_id": self.analyzer.cell_event_id("CTRL", "P", 14, 10),
            "run": "CTRL", "profile": "P", "cell": 14,
            "first_low_bin": 10, "low_bin_end_exclusive": 13,
            "low_speed_bins": 3, "required_bins": 3,
            "first_low_start_s": 300, "confirmation_time_s": 390,
            "event_status": "NUMERICAL_POSITIVE_ATTRIBUTION_REVIEW",
            "is_merge_core": True, "ref_eligible": True,
            "numerical_positive": True, "qualified_density_bins": 3,
            "qualified_density_bin_ids": "10;11;12"}
        self.attr = {"event_id": self.event["event_id"], "run": "CTRL",
                     "overall_attribution": "UNRESOLVED", "source_artifact_status": "UNRESOLVED"}

    def tearDown(self):
        self.temp.cleanup()

    def test_populated_grid_maps_locked_gates_without_mutation(self):
        before = json.loads(json.dumps(self.metrics))
        mapped, receipt = source.build_locked_event_source(
            self.metrics, [self.event], [self.attr], self.analyzer, self.binding)
        self.assertEqual(len(mapped), 1)
        self.assertEqual(mapped[0]["profile"], "P")
        self.assertTrue(mapped[0]["locked_numerical_positive"])
        self.assertTrue(mapped[0]["locked_reference_pass"])
        self.assertTrue(mapped[0]["locked_population_pass"])
        self.assertEqual(mapped[0]["locked_attribution_original"], self.attr)
        self.assertEqual(receipt["status"], "COMPLETE_EVENTS")
        self.assertEqual(self.metrics, before)

    def test_complete_zero_events_is_distinct_from_missing_and_incomplete(self):
        zero_metrics = [dict(row, mean_model_reference_ratio=0.9,
                             sample_slow_fraction=0.0, labels_nslow_ge2=0,
                             low_state_bin=False) for row in self.metrics]
        mapped, receipt = source.build_locked_event_source(
            zero_metrics, [], [], self.analyzer, self.binding)
        self.assertEqual(mapped, [])
        self.assertEqual(receipt["status"], "COMPLETE_ZERO_EVENTS")
        self.assertEqual(source.validate_locked_event_source(
            zero_metrics, [], [], receipt, self.analyzer, self.binding)[0], "PASS_ZERO")
        self.assertEqual(source.validate_locked_event_source(
            self.metrics, None, None, None, self.analyzer, self.binding)[0], "UNKNOWN")
        with self.assertRaisesRegex(source.LockedSourceError, "INCOMPLETE_METRIC_GRID"):
            source.build_locked_event_source(zero_metrics[:-1], [], [], self.analyzer, self.binding)

    def test_duplicate_grid_event_coverage_and_event_boundary_fail_closed(self):
        with self.assertRaisesRegex(source.LockedSourceError, "DUPLICATE_METRIC_BIN"):
            source.build_locked_event_source(self.metrics + [self.metrics[0]], [], [], self.analyzer, self.binding)
        with self.assertRaisesRegex(source.LockedSourceError, "EVENT_SOURCE_RUN_BOUNDARY_MISMATCH"):
            bad = {**self.event, "low_bin_end_exclusive": 14, "low_speed_bins": 4}
            source.build_locked_event_source(self.metrics, [bad], [self.attr], self.analyzer, self.binding)
        with self.assertRaisesRegex(source.LockedSourceError, "EVENT_DERIVATION_COVERAGE_MISMATCH"):
            source.build_locked_event_source(self.metrics, [], [], self.analyzer, self.binding)

    def test_locked_helper_gate_extraction_and_binding_drift_fail_closed(self):
        altered = [dict(row) for row in self.metrics]
        altered_index = next(i for i, row in enumerate(altered)
                             if (row["cell"], row["profile"], row["bin"]) == (14, "P", 10))
        altered[altered_index]["low_state_bin"] = False
        with self.assertRaisesRegex(source.LockedSourceError, "LOCKED_LOW_STATE_OUTPUT_MISMATCH"):
            source.build_locked_event_source(altered, [self.event], [self.attr], self.analyzer, self.binding)
        bad_binding = json.loads(json.dumps({"sha256": self.binding["sha256"],
                                             "run_id": self.binding["run_id"],
                                             "run_label": self.binding["run_label"]}))
        bad_binding["sha256"]["design"] = "0" * 64
        bad_binding["paths"] = self.binding["paths"]
        with self.assertRaisesRegex(source.LockedSourceError, "BINDING_HASH_MISMATCH:design"):
            source.build_locked_event_source(self.metrics, [self.event], [self.attr], self.analyzer, bad_binding)


if __name__ == "__main__":
    unittest.main()

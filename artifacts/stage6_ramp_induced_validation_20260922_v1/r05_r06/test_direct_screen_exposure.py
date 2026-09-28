import unittest
import hashlib
import json

from direct_screen_exposure import (
    PRE_BLOCKS, PRE_CELLS, PRE_SCOPES, build_pre_screen,
    bracket_route_crossing, crossing_bin_membership, earliest_crossing_interval,
    expand_disturbance_masks, find_t3, summarize_pre_screen,
    ongoing_exposure_status, validate_event_completeness, validate_r_coverage,
)


def make_bins():
    bins = {}
    for cell in range(12, 19):
        for scope in PRE_SCOPES:
            for b in range(12, 18):
                bins[(cell, scope, b)] = {
                    "observed_labels": 30, "unique_M": 3,
                    "mean_ratio": 0.85, "M_density": 10.0,
                    "MR_density": 10.5,
                }
    return bins


def make_r_coverage(ids):
    roles = ("demand", "fcd", "vehroute", "lanechanges", "lifecycle")
    source_bytes = {role: role.encode() for role in roles}
    identity_hash = hashlib.sha256(json.dumps(sorted(ids), separators=(",", ":")).encode()).hexdigest()
    receipt = {
        "complete": True, "r_lifecycle_reconciled": True,
        "route_scan_complete": True, "fcd_time_labels_complete": True,
        "source_sha256_by_role": {k: hashlib.sha256(v).hexdigest() for k, v in source_bytes.items()},
        "scheduled_r_count": len(ids), "lifecycle_r_count": len(ids),
        "scheduled_r_ids_sha256": identity_hash, "lifecycle_r_ids_sha256": identity_hash,
    }
    return receipt, source_bytes, ids, ids


class DirectScreenTests(unittest.TestCase):
    def receipt(self, n=0):
        source = b"source"
        catalog = b"catalog"
        return {"complete": True, "source_sha256": hashlib.sha256(source).hexdigest(),
                "source_event_count": n, "catalog_row_count": n,
                "catalog_sha256": hashlib.sha256(catalog).hexdigest(),
                "profiles_complete": ["P", "S", "L", "A", "C"]}, source, catalog

    def test_empty_catalog_needs_complete_bound_receipt(self):
        _, source, catalog = self.receipt()
        self.assertEqual(validate_event_completeness({}, source, catalog, []),
                         (False, "MISSING_COMPLETENESS_RECEIPT"))
        receipt, source, catalog = self.receipt()
        self.assertEqual(validate_event_completeness(receipt, source, catalog, []), (True, ""))

    def test_missing_profile_or_wrong_hash_is_unknown(self):
        rec, source, catalog = self.receipt()
        rec["profiles_complete"] = ["P", "S", "L", "A"]
        self.assertEqual(validate_event_completeness(rec, source, catalog, [])[1],
                         "PROFILE_COVERAGE_INCOMPLETE")
        rec, source, catalog = self.receipt()
        self.assertEqual(validate_event_completeness(rec, b"wrong", catalog, [])[1],
                         "SOURCE_HASH_MISMATCH")
        self.assertEqual(validate_event_completeness(rec, source, b"wrong", [])[1],
                         "CATALOG_HASH_MISMATCH")

    def test_fractional_population_is_unknown_and_fractional_mask_is_rejected(self):
        bins = make_bins()
        bins[(13, "lane0", 12)]["unique_M"] = 2.9
        rows = build_pre_screen(bins, expand_disturbance_masks([], True), True)
        target = next(r for r in rows if r["cell"] == 13 and r["scope"] == "lane0"
                      and r["block_start_s"] == 360)
        self.assertEqual(target["status"], "UNKNOWN")
        with self.assertRaisesRegex(ValueError, "malformed"):
            expand_disturbance_masks([{"family": "C", "event_id": "C1", "cell": 13.9,
                                      "start_s": 450, "end_s": 480}], True)

    def test_exact_085_pass_next_lower_fails(self):
        bins = make_bins()
        masks = expand_disturbance_masks([], True)
        self.assertEqual(len(build_pre_screen(bins, masks, True)), 30)
        self.assertTrue(all(r["status"] == "PASS" for r in build_pre_screen(bins, masks, True)))
        bins[(13, "lane0", 12)]["mean_ratio"] = 0.8499999999999999
        row = next(r for r in build_pre_screen(bins, masks, True)
                   if r["cell"] == 13 and r["scope"] == "lane0" and r["block_start_s"] == 360)
        self.assertEqual(row["status"], "FAIL")

    def test_each_lane_and_pooled_are_independent_gates(self):
        bins = make_bins()
        bins[(14, "lane1", 13)]["mean_ratio"] = 0.80
        rows = build_pre_screen(bins, expand_disturbance_masks([], True), True)
        self.assertEqual(next(r for r in rows if r["cell"] == 14 and r["scope"] == "lane1"
                              and r["block_start_s"] == 360)["status"], "FAIL")
        self.assertEqual(next(r for r in rows if r["cell"] == 14 and r["scope"] == "pooled"
                              and r["block_start_s"] == 360)["status"], "PASS")

    def test_missing_bin_is_unknown_and_valid_zero_population_is_fail(self):
        bins = make_bins()
        masks = expand_disturbance_masks([], True)
        del bins[(13, "lane0", 12)]
        rows = build_pre_screen(bins, masks, True)
        self.assertEqual(next(r for r in rows if r["cell"] == 13 and r["scope"] == "lane0"
                              and r["block_start_s"] == 360)["status"], "UNKNOWN")
        bins = make_bins()
        bins[(13, "lane0", 12)]["unique_M"] = 0
        rows = build_pre_screen(bins, masks, True)
        self.assertEqual(next(r for r in rows if r["cell"] == 13 and r["scope"] == "lane0"
                              and r["block_start_s"] == 360)["status"], "FAIL")
        bins = make_bins()
        bins[(13, "lane0", 12)]["unique_M"] = None
        rows = build_pre_screen(bins, masks, True)
        self.assertEqual(next(r for r in rows if r["cell"] == 13 and r["scope"] == "lane0"
                              and r["block_start_s"] == 360)["status"], "UNKNOWN")

    def test_masks_include_neighbor_and_half_open_block_boundary(self):
        rows = [{"family": "C", "event_id": "C_1", "cell": 12, "start_s": 360, "end_s": 390}]
        masks = expand_disturbance_masks(rows, True)
        bins = make_bins()
        out = build_pre_screen(bins, masks, True)
        target = next(r for r in out if r["cell"] == 13 and r["scope"] == "pooled"
                      and r["block_start_s"] == 360)
        self.assertEqual(target["status"], "FAIL")
        # An onset exactly at block end does not overlap or precede that block.
        rows = [{"family": "C", "event_id": "C_2", "cell": 13, "start_s": 450, "end_s": 480}]
        masks = expand_disturbance_masks(rows, True)
        target = next(r for r in build_pre_screen(bins, masks, True)
                      if r["cell"] == 13 and r["scope"] == "pooled" and r["block_start_s"] == 360)
        self.assertEqual(target["status"], "PASS")

    def test_incomplete_mask_is_unknown(self):
        rows = build_pre_screen(make_bins(), None, False)
        self.assertEqual(len(rows), 30)
        self.assertTrue(all(r["status"] == "UNKNOWN" for r in rows))
        self.assertEqual(summarize_pre_screen(rows)["status"], "UNKNOWN")

    def test_overall_pre_requires_exactly_30_all_pass_rows(self):
        rows = build_pre_screen(make_bins(), expand_disturbance_masks([], True), True)
        self.assertEqual(summarize_pre_screen(rows)["status"], "PASS")
        duplicate = rows[:-1] + [dict(rows[0])]
        self.assertEqual(summarize_pre_screen(duplicate)["status"], "UNKNOWN")
        missing = rows[:-1]
        self.assertEqual(summarize_pre_screen(missing)["status"], "UNKNOWN")
        out_of_domain = [dict(r) for r in rows]
        out_of_domain[0]["cell"] = 99
        self.assertEqual(summarize_pre_screen(out_of_domain)["status"], "UNKNOWN")
        bad_status = [dict(r) for r in rows]
        bad_status[0]["status"] = "BOGUS"
        self.assertEqual(summarize_pre_screen(bad_status)["status"], "UNKNOWN")
        rows[0]["status"] = "FAIL"
        self.assertEqual(summarize_pre_screen(rows)["status"], "FAIL")
        self.assertEqual(summarize_pre_screen(rows[:-1])["status"], "UNKNOWN")


class CrossingTests(unittest.TestCase):
    def test_r_coverage_requires_source_hashes_and_exact_identity_reconciliation(self):
        self.assertEqual(validate_r_coverage(None, None, ["R1"], ["R1"])["status"], "UNKNOWN")
        roles = ("demand", "fcd", "vehroute", "lanechanges", "lifecycle")
        source_bytes = {role: role.encode() for role in roles}
        valid = validate_r_coverage(*make_r_coverage(["R1"]))
        self.assertEqual(valid["status"], "PASS")
        self.assertEqual(validate_r_coverage({"complete": True}, source_bytes,
                                             ["R1"], ["R2"])["reason"],
                         "R_COVERAGE_ATTESTATION_INCOMPLETE")
        self.assertEqual(validate_r_coverage({
            **{"complete": True, "r_lifecycle_reconciled": True,
               "route_scan_complete": True, "fcd_time_labels_complete": True},
            "source_sha256_by_role": {},
        }, source_bytes, ["R1"], ["R1"])["reason"], "R_SOURCE_HASH_MISMATCH")

    def test_route_mapped_aux_crossing_can_be_bracketed_without_aux_sample(self):
        got = bracket_route_crossing("R1", "AUX_ENTRY",
            {"time_s": 29, "route_progress_m": 99.0},
            {"time_s": 30, "route_progress_m": 101.0}, 100.0, True, "fcd:29-30")
        self.assertEqual((got["lower_s"], got["upper_s"]), (29.0, 30.0))
        self.assertEqual((got["lower_inclusive"], got["upper_inclusive"]), (False, True))
        self.assertEqual(got["status"], "INTERVAL_BRACKETED")
        unknown = bracket_route_crossing("R1", "AUX_ENTRY",
            {"time_s": 29, "route_progress_m": 99.0},
            {"time_s": 30, "route_progress_m": 101.0}, 100.0, False, "fcd:29-30")
        self.assertEqual(unknown["status"], "UNKNOWN")

    def test_overlapping_earliest_vehicle_crossings_remain_unordered(self):
        ids = ["R1", "R2", "R3"]
        coverage = make_r_coverage(ids)
        got = earliest_crossing_interval([
            {"vehicle_id": "R1", "lower_s": 29, "upper_s": 30, "route_checked": True},
            {"vehicle_id": "R2", "lower_s": 29.5, "upper_s": 30, "route_checked": True},
            {"vehicle_id": "R3", "lower_s": 40, "upper_s": 41, "route_checked": True},
        ], *coverage)
        self.assertEqual(got["possible_earliest_ids"], ["R1", "R2"])
        self.assertFalse(got["order_resolved"])
        unknown = earliest_crossing_interval([
            {"vehicle_id": "R1", "lower_s": 29, "upper_s": 30, "route_checked": True},
            {"vehicle_id": "R2", "lower_s": None, "upper_s": None, "route_checked": False},
        ], *make_r_coverage(["R1", "R2"]))
        self.assertEqual(unknown["status"], "UNKNOWN")
        self.assertEqual(unknown["possible_earliest_ids"], ["R1"])
        missing = make_r_coverage(["R1"])
        self.assertEqual(earliest_crossing_interval([], None, None, missing[2], missing[3])["status"], "UNKNOWN")
        self.assertEqual(earliest_crossing_interval([], *make_r_coverage([]))["status"], "NO_R_POPULATION")
        self.assertEqual(earliest_crossing_interval([], *make_r_coverage(["R1"]))["status"], "NOT_OBSERVED")

    def test_exact_bin_and_cross_boundary_interval(self):
        rows = [
            {"vehicle_id": "R_exact", "lower_s": 30, "upper_s": 30, "route_checked": True},
            {"vehicle_id": "R_cross", "lower_s": 29, "upper_s": 30, "route_checked": True},
            {"vehicle_id": "R_whole", "lower_s": 31, "upper_s": 32, "route_checked": True},
        ]
        certain, possible, unknown = crossing_bin_membership(rows, [(0, 30), (30, 60)],
                                                              *make_r_coverage(["R_exact", "R_cross", "R_whole"]))
        self.assertEqual(certain[30], ["R_exact", "R_whole"])
        self.assertEqual(possible[0], ["R_cross"])
        self.assertEqual(possible[30], ["R_cross", "R_exact", "R_whole"])
        self.assertEqual(unknown[0], [])

    def test_missing_route_duplicate_identity_and_unknown_bounds(self):
        expected = ["R1"]
        coverage = make_r_coverage(expected)
        certain, possible, unknown = crossing_bin_membership(
            [{"vehicle_id": "R1", "lower_s": 2, "upper_s": 3,
              "route_checked": False}], [(0, 30)], *coverage)
        self.assertEqual(certain[0], [])
        self.assertEqual(possible[0], ["R1"])
        self.assertEqual(unknown[0], ["R1"])
        with self.assertRaises(ValueError):
            crossing_bin_membership([
                {"vehicle_id": "R1", "lower_s": 2, "upper_s": 3, "route_checked": True},
                {"vehicle_id": "R1", "lower_s": 5, "upper_s": 6, "route_checked": True}], [(0, 30)], *coverage)
        certain, possible, unknown = crossing_bin_membership(
            [{"vehicle_id": "R_unknown", "lower_s": None, "upper_s": None, "route_checked": False}],
            [(0, 30), (30, 60)], *make_r_coverage(["R_unknown"]))
        self.assertEqual(certain[0], [])
        self.assertEqual(possible[0], [])
        self.assertEqual(unknown[0], ["R_unknown"])
        no_coverage = crossing_bin_membership([], [(0, 30)], None, None, None, None)
        self.assertEqual(no_coverage[2][0], ["__RAW_COVERAGE_UNKNOWN__"])
        bad_source = make_r_coverage(expected)
        bad_source[0]["source_sha256_by_role"] = {}
        false_zero = crossing_bin_membership([], [(0, 30)], *bad_source)
        self.assertEqual(false_zero[2][0], ["__RAW_COVERAGE_UNKNOWN__"])

    def test_invalid_numbers_and_bins_rejected(self):
        with self.assertRaisesRegex(ValueError, "finite"):
            crossing_bin_membership([{"vehicle_id": "Rnan", "lower_s": float("nan"),
                                      "upper_s": 2, "route_checked": True}], [(0, 30)],
                                    *make_r_coverage(["Rnan"]))
        with self.assertRaisesRegex(ValueError, "contiguous"):
            crossing_bin_membership([], [(0, 30), (40, 70)], *make_r_coverage([]))
        bad = bracket_route_crossing("R1", "AUX_ENTRY",
            {"time_s": 1, "route_progress_m": float("nan")},
            {"time_s": 2, "route_progress_m": 3}, 2, True, "fixture")
        self.assertEqual(bad["status"], "UNKNOWN")

    def test_t3_boundary_and_ongoing_exposure(self):
        certain = {630: ["R1"], 660: ["R2"], 690: ["R3"]}
        complete = set(range(600, 720, 30))
        eligible = {b: certain.get(b, []) for b in complete}
        self.assertEqual(find_t3(eligible, 600, complete, set())["confirmation_s"], 720)
        self.assertEqual(find_t3(eligible, 600, complete, set())["status"], "PASS")
        self.assertEqual(find_t3(eligible, 631, complete, set())["status"], "NOT_ESTABLISHED")
        self.assertEqual(find_t3(eligible, 600, None, set())["status"], "UNKNOWN")
        self.assertEqual(find_t3(eligible, 600, complete, {630})["status"], "UNKNOWN")
        self.assertEqual(ongoing_exposure_status(certain, certain, [630, 660], {630, 660}, set()), "PASS")
        self.assertEqual(ongoing_exposure_status({}, certain, [630], {630}, set()), "UNKNOWN")
        self.assertEqual(ongoing_exposure_status({630: []}, {630: []}, [630], {630}, set()), "FAIL")


if __name__ == "__main__":
    unittest.main()

"""Offline helper contracts for the RI3350 direct PRE screen and R exposure.

This module intentionally consumes normalized per-bin metrics and route-checked
crossing intervals. It does not parse/run SUMO and does not replace the locked
P/S/L/A/C classifier. A missing completeness receipt is UNKNOWN, never empty.
"""
from __future__ import annotations

from collections import defaultdict
import hashlib
import json
from math import isfinite
from typing import Iterable, Mapping, Sequence


PRE_BLOCKS = ((360, 450), (450, 540))
PRE_CELLS = tuple(range(13, 18))
PRE_SCOPES = ("lane0", "lane1", "pooled")


def _strict_int(value):
    """Parse integer-valued inputs without truncating fractional numerics."""
    if isinstance(value, bool):
        raise ValueError("boolean is not an integer field")
    if isinstance(value, int):
        return value
    if isinstance(value, float):
        if not isfinite(value) or not value.is_integer():
            raise ValueError("non-integral numeric field")
        return int(value)
    if isinstance(value, str) and value.strip().lstrip("+-").isdigit():
        return int(value)
    raise ValueError("invalid integer field")


def validate_event_completeness(receipt: Mapping, source_bytes: bytes | None,
                                catalog_bytes: bytes | None,
                                event_rows: Sequence[Mapping]) -> tuple[bool, str]:
    """Distinguish verified zero events from absent/incomplete source coverage."""
    if not receipt:
        return False, "MISSING_COMPLETENESS_RECEIPT"
    if source_bytes is None or catalog_bytes is None:
        return False, "SOURCE_OR_CATALOG_BYTES_MISSING"
    source_sha256 = hashlib.sha256(source_bytes).hexdigest()
    catalog_sha256 = hashlib.sha256(catalog_bytes).hexdigest()
    if receipt.get("complete") is not True:
        return False, "SOURCE_NOT_COMPLETE"
    if receipt.get("source_sha256") != source_sha256:
        return False, "SOURCE_HASH_MISMATCH"
    if receipt.get("source_event_count") != len(event_rows):
        return False, "EVENT_COUNT_MISMATCH"
    if receipt.get("catalog_row_count") != len(event_rows):
        return False, "CATALOG_COUNT_MISMATCH"
    if receipt.get("catalog_sha256") != catalog_sha256:
        return False, "CATALOG_HASH_MISMATCH"
    if set(receipt.get("profiles_complete", [])) != {"P", "S", "L", "A", "C"}:
        return False, "PROFILE_COVERAGE_INCOMPLETE"
    return True, ""


R_COVERAGE_ROLES = ("demand", "fcd", "vehroute", "lanechanges", "lifecycle")


def _identity_sha(ids: Sequence[str]) -> str:
    return hashlib.sha256(json.dumps(sorted(ids), separators=(",", ":")).encode()).hexdigest()


def validate_r_coverage(receipt: Mapping | None,
                        source_bytes: Mapping[str, bytes] | None,
                        expected_r_ids: Sequence[str] | None,
                        lifecycle_r_ids: Sequence[str] | None) -> dict:
    """Validate source bytes and exact scheduled-vs-lifecycle R identity sets.

    The receipt is emitted only after parsers complete; this helper verifies its
    hash/count/set claims. It cannot independently certify parser semantics.
    """
    if not receipt or source_bytes is None or expected_r_ids is None or lifecycle_r_ids is None:
        return {"status": "UNKNOWN", "reason": "R_COVERAGE_INPUT_OR_RECEIPT_MISSING"}
    if set(source_bytes) != set(R_COVERAGE_ROLES) or any(not isinstance(source_bytes[k], bytes)
                                                        for k in R_COVERAGE_ROLES):
        return {"status": "UNKNOWN", "reason": "R_COVERAGE_SOURCE_BYTES_INCOMPLETE"}
    expected, lifecycle = list(expected_r_ids), list(lifecycle_r_ids)
    if (len(expected) != len(set(expected)) or len(lifecycle) != len(set(lifecycle))
            or any(not x for x in expected + lifecycle)):
        return {"status": "UNKNOWN", "reason": "R_IDENTITY_SET_MALFORMED_OR_DUPLICATE"}
    if (receipt.get("complete") is not True
            or receipt.get("r_lifecycle_reconciled") is not True
            or receipt.get("route_scan_complete") is not True
            or receipt.get("fcd_time_labels_complete") is not True):
        return {"status": "UNKNOWN", "reason": "R_COVERAGE_ATTESTATION_INCOMPLETE"}
    actual_hashes = {role: hashlib.sha256(source_bytes[role]).hexdigest() for role in R_COVERAGE_ROLES}
    if receipt.get("source_sha256_by_role") != actual_hashes:
        return {"status": "UNKNOWN", "reason": "R_SOURCE_HASH_MISMATCH"}
    if (receipt.get("scheduled_r_count") != len(expected)
            or receipt.get("lifecycle_r_count") != len(lifecycle)
            or receipt.get("scheduled_r_ids_sha256") != _identity_sha(expected)
            or receipt.get("lifecycle_r_ids_sha256") != _identity_sha(lifecycle)):
        return {"status": "UNKNOWN", "reason": "R_IDENTITY_RECEIPT_MISMATCH"}
    if set(expected) != set(lifecycle):
        return {"status": "UNKNOWN", "reason": "SCHEDULED_LIFECYCLE_R_ID_SET_MISMATCH"}
    return {"status": "PASS", "expected_r_ids": sorted(expected),
            "source_sha256_by_role": actual_hashes}


def expand_disturbance_masks(event_rows: Sequence[Mapping], complete: bool):
    """Expand the unchanged P/S/L/A/C intervals to each cell and its neighbors."""
    if not complete:
        return None
    masks = defaultdict(list)
    seen = set()
    for row in event_rows:
        try:
            family = str(row["family"])
            cell, start, end = (_strict_int(row["cell"]), _strict_int(row["start_s"]),
                                _strict_int(row["end_s"]))
            event_id = str(row["event_id"])
        except (KeyError, TypeError, ValueError):
            raise ValueError("malformed disturbance event row")
        key = (family, event_id)
        if key in seen:
            raise ValueError("duplicate family/event identity")
        seen.add(key)
        if (family not in {"P", "S", "L", "A", "C"} or not event_id
                or cell < 0 or cell > 21 or start < 0 or end <= start or end > 2700):
            raise ValueError("invalid locked event family or half-open interval")
        for neighbor in range(max(0, cell - 1), min(21, cell + 1) + 1):
            masks[neighbor].append((start, end, family))
    return dict(masks)


def _overlaps(start: int, end: int, intervals: Iterable[tuple[int, int, str]]) -> bool:
    return any(not (end <= a or start >= b) for a, b, _ in intervals)


def _first_onset(cell: int, masks: Mapping[int, Sequence[tuple[int, int, str]]]):
    # Expanded masks are attached to every affected cell; conservative onset is
    # the earliest event onset reaching this candidate cell.
    vals = masks.get(cell, ())
    return min((a for a, _, _ in vals), default=None)


def evaluate_pre_row(cell: int, scope: str, start: int, end: int,
                     bins: Mapping[tuple[int, str, int], Mapping], masks,
                     mask_complete: bool) -> dict:
    reasons = []
    if not mask_complete or masks is None:
        return {"status": "UNKNOWN", "reasons": ["DISTURBANCE_MASK_UNKNOWN"]}
    first_bin = start // 30
    expected_bins = tuple(range(first_bin, end // 30))
    vals = [bins.get((cell, scope, b)) for b in expected_bins]
    unknown = False
    if len(vals) != 3 or any(v is None for v in vals):
        unknown = True
        reasons.append("MISSING_BIN_METRICS")
    else:
        for b, v in zip(expected_bins, vals):
            if v.get("observed_labels") != 30:
                unknown = True
                reasons.append(f"INCOMPLETE_LABELS_BIN_{b}")
            unique_m = v.get("unique_M")
            if unique_m is None:
                unknown = True
                reasons.append(f"UNKNOWN_M_POPULATION_BIN_{b}")
            else:
                try:
                    unique_m = _strict_int(unique_m)
                except (TypeError, ValueError):
                    unique_m = -1
                if unique_m < 0:
                    unknown = True
                    reasons.append(f"INVALID_M_POPULATION_BIN_{b}")
                elif unique_m < 2:
                    reasons.append(f"LOW_M_POPULATION_BIN_{b}")
            ratio = v.get("mean_ratio")
            if ratio is None:
                unknown = True
                reasons.append(f"UNKNOWN_RATIO_BIN_{b}")
            else:
                try:
                    ratio = float(ratio)
                except (TypeError, ValueError):
                    ratio = float("nan")
                if not isfinite(ratio):
                    unknown = True
                    reasons.append(f"INVALID_RATIO_BIN_{b}")
                elif ratio < 0.85:
                    reasons.append(f"LOW_RATIO_BIN_{b}")
            for name in ("M_density", "MR_density"):
                value = v.get(name)
                if value is None:
                    unknown = True
                    reasons.append(f"UNKNOWN_{name.upper()}_BIN_{b}")
                else:
                    try:
                        value = float(value)
                    except (TypeError, ValueError):
                        value = float("nan")
                if value is not None and not isfinite(value):
                    unknown = True
                    reasons.append(f"INVALID_{name.upper()}_BIN_{b}")
                elif value is not None and value <= 0:
                    reasons.append(f"INVALID_{name.upper()}_BIN_{b}")
    if _overlaps(start, end, masks.get(cell, ())):
        reasons.append("DISTURBANCE_OVERLAP_CELL_OR_NEIGHBOR")
    onset = _first_onset(cell, masks)
    if onset is not None and end > onset:
        reasons.append("AFTER_FIRST_DISTURBANCE_ONSET_CELL_OR_NEIGHBOR")
    # Deduplicate without reordering; this keeps machine output deterministic.
    reasons = list(dict.fromkeys(reasons))
    status = "UNKNOWN" if unknown else ("FAIL" if reasons else "PASS")
    return {"status": status, "reasons": reasons}


def build_pre_screen(bins: Mapping[tuple[int, str, int], Mapping],
                     masks, mask_complete: bool) -> list[dict]:
    rows = []
    for cell in PRE_CELLS:
        for scope in PRE_SCOPES:
            for start, end in PRE_BLOCKS:
                result = evaluate_pre_row(cell, scope, start, end, bins, masks, mask_complete)
                rows.append({"cell": cell, "scope": scope, "block_start_s": start,
                             "block_end_s": end, **result})
    assert len(rows) == 30
    return rows


def summarize_pre_screen(rows: Sequence[Mapping]) -> dict:
    """Conjunctive 30-row PRE gate; uncertainty outranks a partial positive."""
    expected = {(cell, scope, start, end)
                for cell in PRE_CELLS for scope in PRE_SCOPES
                for start, end in PRE_BLOCKS}
    try:
        keys = [(_strict_int(r["cell"]), str(r["scope"]), _strict_int(r["block_start_s"]),
                 _strict_int(r["block_end_s"]))
                for r in rows]
        statuses = [r["status"] for r in rows]
    except (KeyError, TypeError, ValueError):
        return {"status": "UNKNOWN", "pass_rows": 0, "fail_rows": 0,
                "unknown_rows": 30, "reason": "MALFORMED_ROW_SCHEMA"}
    if len(rows) != 30 or len(set(keys)) != 30 or set(keys) != expected:
        return {"status": "UNKNOWN", "pass_rows": 0, "fail_rows": 0,
                "unknown_rows": 30, "reason": "ROW_KEYS_NOT_EXACT_CARTESIAN_SET"}
    if any(s not in {"PASS", "FAIL", "UNKNOWN"} for s in statuses):
        return {"status": "UNKNOWN", "pass_rows": 0, "fail_rows": 0,
                "unknown_rows": 30, "reason": "UNKNOWN_ROW_STATUS_ENUM"}
    counts = {s: sum(r.get("status") == s for r in rows) for s in ("PASS", "FAIL", "UNKNOWN")}
    if counts["UNKNOWN"]:
        status = "UNKNOWN"
    elif counts["FAIL"]:
        status = "FAIL"
    else:
        status = "PASS"
    return {"status": status, "pass_rows": counts["PASS"],
            "fail_rows": counts["FAIL"], "unknown_rows": counts["UNKNOWN"],
            "reason": ""}


def interval_intersects_bin(lower_s: float, upper_s: float,
                             bin_start_s: int, bin_end_s: int) -> bool:
    """Closed/open uncertainty interval overlaps the half-open detector bin."""
    return upper_s >= bin_start_s and lower_s < bin_end_s


def certain_bin(lower_s: float, upper_s: float, bin_width_s: int = 30):
    """Return unique half-open bin only when the whole interval lies in one bin."""
    if (not isfinite(float(lower_s)) or not isfinite(float(upper_s))
            or lower_s < 0 or upper_s > 2700 or upper_s < lower_s
            or not isinstance(bin_width_s, int) or bin_width_s <= 0):
        raise ValueError("crossing interval/bin width is invalid")
    lo = int(lower_s // bin_width_s)
    hi = int(upper_s // bin_width_s)
    if lower_s == upper_s:
        return lo
    # An upper bound exactly on the next bin boundary still allows crossing
    # at that boundary, so it is not wholly within the prior half-open bin.
    if hi == lo and upper_s < (lo + 1) * bin_width_s:
        return lo
    return None


def crossing_bin_membership(crossings: Sequence[Mapping], bins: Sequence[tuple[int, int]],
                            coverage_receipt: Mapping | None,
                            source_bytes: Mapping[str, bytes] | None,
                            expected_r_ids: Sequence[str] | None,
                            lifecycle_r_ids: Sequence[str] | None):
    """Create certain/possible IDs plus explicit unknown-bin coverage.

    Empty lists mean observed zero only when this function itself validates the
    hash-bound receipt and exact expected-vs-lifecycle R identity sets.
    Unknown-time intervals taint every bin; bounded but route-unchecked records
    taint their possible bins.
    """
    if not bins or bins != sorted(bins) or len(set(bins)) != len(bins):
        raise ValueError("bins must be unique, sorted, contiguous half-open intervals")
    for i, (a, b) in enumerate(bins):
        if (not isinstance(a, int) or not isinstance(b, int) or a < 0 or b > 2700
                or a % 30 or b - a != 30 or (i and bins[i - 1][1] != a)):
            raise ValueError("bins must be contiguous 30-second half-open intervals")
    certain = {a: set() for a, _ in bins}
    possible = {a: set() for a, _ in bins}
    unknown = {a: set() for a, _ in bins}
    coverage_check = validate_r_coverage(coverage_receipt, source_bytes,
                                         expected_r_ids, lifecycle_r_ids)
    valid_coverage = coverage_check.get("status") == "PASS"
    expected = set(expected_r_ids or [])
    seen = set()
    for row in crossings:
        vid = row.get("vehicle_id")
        if not vid or vid in seen:
            raise ValueError("missing or duplicate vehicle-boundary crossing identity")
        seen.add(vid)
        if vid not in expected:
            for a, _ in bins:
                unknown[a].add(vid)
            continue
        lo, hi = row.get("lower_s"), row.get("upper_s")
        if lo is None or hi is None:
            for a, _ in bins:
                unknown[a].add(vid)
            continue
        try:
            lo, hi = float(lo), float(hi)
        except (TypeError, ValueError):
            for a, _ in bins:
                unknown[a].add(vid)
            continue
        if not isfinite(lo) or not isfinite(hi) or lo < 0 or hi < lo or hi > bins[-1][1]:
            raise ValueError("crossing bounds must be finite, chronological, and within observed horizon")
        touched = []
        for a, b in bins:
            if interval_intersects_bin(lo, hi, a, b):
                possible[a].add(vid)
                touched.append(a)
        if row.get("route_checked") is not True:
            for a in (touched or [b[0] for b in bins]):
                unknown[a].add(vid)
            continue
        cbin = certain_bin(lo, hi)
        if cbin is not None:
            a = cbin * 30
            if a in certain:
                certain[a].add(vid)
    if not valid_coverage:
        for a, _ in bins:
            unknown[a].add("__RAW_COVERAGE_UNKNOWN__")
    return ({a: sorted(v) for a, v in certain.items()},
            {a: sorted(v) for a, v in possible.items()},
            {a: sorted(v) for a, v in unknown.items()})


def bracket_route_crossing(vehicle_id: str, boundary: str, previous: Mapping,
                           current: Mapping, boundary_progress_m: float,
                           route_checked: bool, evidence_id: str):
    """Bracket one route-boundary crossing from consecutive route-mapped FCD.

    Route progress must be derived from the archived route plus compiled edge/lane
    topology. This helper deliberately refuses to infer progress from edge IDs or
    lane suffixes alone. A skipped auxiliary sample remains inferable only when
    the route-mapped bracket straddles its boundary.
    """
    required = ("time_s", "route_progress_m")
    if not route_checked or any(previous.get(k) is None or current.get(k) is None for k in required):
        return {"vehicle_id": vehicle_id, "boundary": boundary, "lower_s": None,
                "upper_s": None, "route_checked": False, "status": "UNKNOWN",
                "unknown_reason": "ROUTE_OR_ROUTE_PROGRESS_UNVERIFIED"}
    try:
        t0, t1 = float(previous["time_s"]), float(current["time_s"])
        p0, p1 = float(previous["route_progress_m"]), float(current["route_progress_m"])
        boundary_progress_m = float(boundary_progress_m)
    except (TypeError, ValueError):
        t0 = t1 = p0 = p1 = boundary_progress_m = float("nan")
    if (not all(isfinite(x) for x in (t0, t1, p0, p1, boundary_progress_m))
            or t0 < 0 or t1 > 2700 or p0 < 0 or p1 < 0 or boundary_progress_m < 0
            or t1 <= t0 or p1 < p0):
        return {"vehicle_id": vehicle_id, "boundary": boundary, "lower_s": None,
                "upper_s": None, "route_checked": True, "status": "UNKNOWN",
                "unknown_reason": "INVALID_NUMERIC_OR_NONMONOTONE_OBSERVATION"}
    if p0 < boundary_progress_m <= p1:
        return {"vehicle_id": vehicle_id, "boundary": boundary,
                "lower_s": t0, "upper_s": t1,
                "lower_inclusive": False, "upper_inclusive": True,
                "route_checked": True, "status": "INTERVAL_BRACKETED",
                "evidence_id": evidence_id}
    return {"vehicle_id": vehicle_id, "boundary": boundary, "lower_s": None,
            "upper_s": None, "route_checked": True, "status": "NO_CROSSING_IN_BRACKET",
            "unknown_reason": "OBSERVATIONS_DO_NOT_STRADDLE_BOUNDARY"}


def earliest_crossing_interval(crossings: Sequence[Mapping], coverage_receipt: Mapping | None,
                              source_bytes: Mapping[str, bytes] | None,
                              expected_r_ids: Sequence[str] | None,
                              lifecycle_r_ids: Sequence[str] | None):
    """Return earliest crossing evidence, retaining ties/overlapping bounds."""
    unknown_ids = []
    known = []
    seen_ids = set()
    for row in crossings:
        vehicle_id = row.get("vehicle_id", "")
        if not vehicle_id or vehicle_id in seen_ids:
            return {"status": "UNKNOWN", "crossings": [], "reason": "MISSING_OR_DUPLICATE_CROSSING_ID"}
        seen_ids.add(vehicle_id)
        lo, hi = row.get("lower_s"), row.get("upper_s")
        try:
            lo, hi = float(lo), float(hi)
        except (TypeError, ValueError):
            unknown_ids.append(vehicle_id)
            continue
        if (row.get("route_checked") is not True or not isfinite(lo) or not isfinite(hi)
                or lo < 0 or hi < lo or hi > 2700):
            unknown_ids.append(vehicle_id)
            continue
        known.append({**row, "lower_s": lo, "upper_s": hi})
    unknown_ids = sorted(unknown_ids)
    coverage_check = validate_r_coverage(coverage_receipt, source_bytes,
                                         expected_r_ids, lifecycle_r_ids)
    valid_coverage = coverage_check.get("status") == "PASS"
    if not valid_coverage:
        return {"status": "UNKNOWN", "crossings": [], "reason": "R_POPULATION_OR_RAW_COVERAGE_NOT_PROVEN"}
    expected = list(expected_r_ids)
    if len(expected) != len(set(expected)) or any(not v for v in expected):
        return {"status": "UNKNOWN", "crossings": [], "reason": "INVALID_EXPECTED_R_ID_SET"}
    if any(r.get("vehicle_id") not in set(expected) for r in crossings):
        return {"status": "UNKNOWN", "crossings": [], "reason": "CROSSING_ID_OUTSIDE_RECONCILED_R_COHORT"}
    if len(expected) == 0:
        return {"status": "NO_R_POPULATION", "crossings": []} if not crossings else {
            "status": "UNKNOWN", "crossings": [], "reason": "CROSSING_WITH_ZERO_EXPECTED_R"}
    if not crossings:
        return {"status": "NOT_OBSERVED", "crossings": []}
    if not known:
        return {"status": "UNKNOWN", "crossings": [], "unknown_ids": unknown_ids}
    earliest_upper = min(float(r["upper_s"]) for r in known)
    possible = [r for r in known if float(r["lower_s"]) <= earliest_upper]
    return {"status": "UNKNOWN" if unknown_ids else "INTERVAL_BOUNDED",
            "lower_s": min(float(r["lower_s"]) for r in possible),
            "upper_s": min(float(r["upper_s"]) for r in possible),
            "possible_earliest_ids": sorted(r["vehicle_id"] for r in possible),
            "unknown_ids": unknown_ids,
            "order_resolved": len(possible) == 1 and not unknown_ids}


def find_t3(certain_aux: Mapping[int, Sequence[str]], t2_upper_s: float | None,
            complete_bins: set[int] | None,
            unknown_bins: set[int] | None = None,
            confirmation_deadline_s: int = 720):
    """First three eligible consecutive 30s bins with certain AUX_ENTRY >=1."""
    if t2_upper_s is None:
        return {"status": "UNKNOWN", "reason": "T2_UPPER_UNKNOWN", "bins": []}
    try:
        t2_upper_s = float(t2_upper_s)
    except (TypeError, ValueError):
        t2_upper_s = float("nan")
    if not isfinite(t2_upper_s) or t2_upper_s < 0 or t2_upper_s > 2700:
        return {"status": "UNKNOWN", "reason": "INVALID_T2_UPPER", "bins": []}
    if complete_bins is None:
        return {"status": "UNKNOWN", "reason": "BIN_COVERAGE_UNKNOWN", "bins": []}
    if unknown_bins is None:
        return {"status": "UNKNOWN", "reason": "CROSSING_COVERAGE_UNKNOWN", "bins": []}
    first_eligible = int(-(-t2_upper_s // 30) * 30)
    required_window = list(range(first_eligible, confirmation_deadline_s - 30 + 1, 30))
    if any(b not in complete_bins for b in required_window):
        return {"status": "UNKNOWN", "reason": "INCOMPLETE_T3_SEARCH_WINDOW", "bins": []}
    if any(b not in certain_aux for b in required_window):
        return {"status": "UNKNOWN", "reason": "MISSING_EXPLICIT_ZERO_OR_COUNT_BIN", "bins": []}
    if any(b in unknown_bins for b in required_window):
        return {"status": "UNKNOWN", "reason": "UNKNOWN_CROSSING_COULD_CHANGE_T3", "bins": []}
    starts = sorted(certain_aux)
    for triple in zip(starts, starts[1:], starts[2:]):
        a, b, c = triple
        if (b == a + 30 and c == b + 30 and all(x in complete_bins for x in triple)
                and a >= t2_upper_s
                and all(certain_aux[x] for x in triple)):
            confirmation = c + 30
            return {"status": "PASS" if confirmation <= confirmation_deadline_s else "FAIL",
                    "reason": "" if confirmation <= confirmation_deadline_s else "T3_AFTER_DEADLINE",
                    "bins": [a, b, c], "confirmation_s": confirmation}
    return {"status": "NOT_ESTABLISHED", "reason": "NO_THREE_CONSECUTIVE_CERTAIN_BINS", "bins": []}


def ongoing_exposure_status(certain_aux: Mapping[int, Sequence[str]],
                            possible_aux: Mapping[int, Sequence[str]],
                            qualification_bins: Sequence[int],
                            complete_bins: set[int],
                            unknown_bins: set[int] | None) -> str:
    """Conservative proposed mechanism-exposure check; does not alter locked P."""
    if (not qualification_bins or any(b not in complete_bins for b in qualification_bins)
            or unknown_bins is None or any(b in unknown_bins for b in qualification_bins)):
        return "UNKNOWN"
    if any(b not in certain_aux or b not in possible_aux for b in qualification_bins):
        return "UNKNOWN"
    if any(not possible_aux.get(b) for b in qualification_bins):
        return "FAIL"
    if all(certain_aux.get(b) for b in qualification_bins):
        return "PASS"
    return "UNKNOWN"

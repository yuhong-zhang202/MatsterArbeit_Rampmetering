"""Hash-bound mapping of unchanged locked-analyzer output to review events.

This module does not reimplement the state classifier. It validates the full
locked metric grid, derives the expected event index from the analyzer's own
``low_state_bin`` booleans, and requires the analyzer event/attribution tables
to match those derived identities exactly. Gate booleans are copied from
locked output or evaluated through its own low_state_gate helper.
"""
from __future__ import annotations

import hashlib
import json
import math
from pathlib import Path

CELL_IDS = tuple(range(22))  # locked [0,2200) 100 m cell mapping
BIN_IDS = tuple(range(90))  # locked 0..2699 seconds, 30 s bins
EXPECTED_PROFILES = ("P", "S", "L")


class LockedSourceError(ValueError):
    """Machine-readable (prefix-coded) integrity failure in locked outputs."""


def canonical_bytes(value) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":"),
                      allow_nan=False).encode("utf-8")


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with Path(path).open("rb") as stream:
        for block in iter(lambda: stream.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


def _content_sha(rows: list[dict], sort_fields: tuple[str, ...]) -> str:
    ordered = sorted(rows, key=lambda row: tuple(row.get(field) for field in sort_fields))
    return hashlib.sha256(canonical_bytes(ordered)).hexdigest()


def _bind_files(binding: dict, analyzer) -> dict:
    expected = binding.get("sha256")
    paths = binding.get("paths")
    names = ("method", "locked_analyzer", "design", "output_roles", "raw_manifest")
    if not isinstance(expected, dict) or not isinstance(paths, dict):
        raise LockedSourceError("BINDING_MISSING:hash/path maps are required")
    out = {}
    for name in names:
        digest = expected.get(name)
        path = paths.get(name)
        if (not isinstance(digest, str) or len(digest) != 64 or
                any(c not in "0123456789abcdef" for c in digest) or path is None):
            raise LockedSourceError(f"BINDING_INVALID:{name}")
        path = Path(path)
        if not path.is_file() or sha256_file(path) != digest:
            raise LockedSourceError(f"BINDING_HASH_MISMATCH:{name}")
        out[name] = {"path": str(path), "sha256": digest}
    if getattr(analyzer, "EXPECTED_METHOD", None) != out["method"]["sha256"]:
        raise LockedSourceError("ANALYZER_METHOD_BINDING_MISMATCH")
    if getattr(analyzer, "PROFILES", None) != {"P": (.70, 3, 1.0), "S": (.60, 4, 1.25), "L": (.80, 2, 1.0)}:
        raise LockedSourceError("ANALYZER_PROFILE_BINDING_MISMATCH")
    if tuple(analyzer.PROFILES) != EXPECTED_PROFILES:
        raise LockedSourceError("ANALYZER_PROFILE_ORDER_OR_COVERAGE_MISMATCH")
    return out


def _validate_grid(metrics: list[dict], analyzer, run_id: str, run_label: str) -> tuple[dict, str]:
    if metrics is None:
        raise LockedSourceError("METRIC_SOURCE_MISSING")
    if not isinstance(metrics, list):
        raise LockedSourceError("METRIC_SOURCE_INVALID")
    expected_keys = {(cell, profile, bin_id) for cell in CELL_IDS
                     for profile in EXPECTED_PROFILES for bin_id in BIN_IDS}
    index = {}
    for row in metrics:
        try:
            if type(row["cell"]) is not int or type(row["bin"]) is not int or not isinstance(row["profile"], str):
                raise TypeError("cell/bin/profile types must be int/int/string")
            key = (row["cell"], row["profile"], row["bin"])
        except (KeyError, TypeError, ValueError) as exc:
            raise LockedSourceError(f"METRIC_ROW_SCHEMA_INVALID:{exc}") from exc
        if key in index:
            raise LockedSourceError(f"DUPLICATE_METRIC_BIN:{key}")
        if key not in expected_keys:
            raise LockedSourceError(f"UNEXPECTED_METRIC_BIN:{key}")
        if row.get("run_id") != run_id or row.get("run") != run_label:
            raise LockedSourceError(f"METRIC_RUN_BINDING_MISMATCH:{key}")
        low = row.get("low_state_bin")
        if type(low) is not bool:
            raise LockedSourceError(f"LOW_STATE_BOOLEAN_MISSING:{key}")
        if type(row.get("valid_bin")) is not bool or type(row.get("labels_nslow_ge2")) is not int:
            raise LockedSourceError(f"LOCKED_LOW_STATE_INPUTS_MISSING:{key}")
        profile_alpha = analyzer.PROFILES[key[1]][0]
        try:
            helper_value = bool(analyzer.low_state_gate(
                row["valid_bin"], row.get("mean_model_reference_ratio"),
                row.get("sample_slow_fraction"), row["labels_nslow_ge2"], profile_alpha))
        except Exception as exc:
            raise LockedSourceError(f"LOCKED_LOW_STATE_HELPER_ERROR:{key}:{exc}") from exc
        if helper_value != low:
            raise LockedSourceError(f"LOCKED_LOW_STATE_OUTPUT_MISMATCH:{key}")
        try:
            canonical_bytes(row)
        except (ValueError, TypeError) as exc:
            raise LockedSourceError(f"METRIC_NONFINITE_OR_UNSERIALIZABLE:{key}:{exc}") from exc
        index[key] = row
    missing = expected_keys - set(index)
    if missing:
        first = sorted(missing)[:5]
        raise LockedSourceError(f"INCOMPLETE_METRIC_GRID:{len(missing)} missing; first={first}")
    ordered = [index[key] for key in sorted(index)]
    key_digest = hashlib.sha256(canonical_bytes([list(k) for k in sorted(index)])).hexdigest()
    return index, key_digest


def _derive_event_keys(metric_index: dict, analyzer, run_label: str) -> dict[tuple, tuple[int, int]]:
    expected = {}
    for profile in EXPECTED_PROFILES:
        for cell in CELL_IDS:
            values = [metric_index[(cell, profile, bin_id)]["low_state_bin"] for bin_id in BIN_IDS]
            start = None
            for i, low in enumerate(values + [False]):
                if low and start is None:
                    start = i
                elif not low and start is not None:
                    key = (profile, cell, start)
                    expected[key] = (start, i)
                    start = None
    return expected


def _event_projection(event: dict, attribution: dict, metric_index: dict,
                      analyzer, run_id: str) -> dict:
    profile, cell, start = event.get("profile"), event.get("cell"), event.get("first_low_bin")
    if profile not in EXPECTED_PROFILES or type(cell) is not int or type(start) is not int:
        raise LockedSourceError(f"EVENT_IDENTITY_INVALID:{event.get('event_id')}")
    for field in ("low_bin_end_exclusive", "required_bins", "low_speed_bins"):
        if type(event.get(field)) is not int:
            raise LockedSourceError(f"EVENT_INTEGER_FIELD_INVALID:{event.get('event_id')}:{field}")
    alpha, duration, density_factor = analyzer.PROFILES[profile]
    end = event["low_bin_end_exclusive"]
    if event.get("required_bins") != duration:
        raise LockedSourceError(f"EVENT_REQUIRED_BIN_MISMATCH:{event['event_id']}")
    if event.get("low_speed_bins") != end - start:
        raise LockedSourceError(f"EVENT_LOW_RUN_LENGTH_MISMATCH:{event['event_id']}")
    numerical = event.get("numerical_positive")
    reference = event.get("ref_eligible")
    if type(numerical) is not bool or type(reference) is not bool:
        raise LockedSourceError(f"EVENT_LOCKED_GATE_FIELD_MISSING:{event['event_id']}")
    if type(event.get("is_merge_core")) is not bool:
        raise LockedSourceError(f"EVENT_CORE_GATE_FIELD_MISSING:{event['event_id']}")
    if event.get("event_status") not in {
        "SHORT_LOW_STATE_CANDIDATE", "OUTSIDE_MERGE_CORE",
        "ONSET_REFERENCE_UNRESOLVED", "DENSITY_GATE_FAIL",
        "NUMERICAL_POSITIVE_ATTRIBUTION_REVIEW",
    }:
        raise LockedSourceError(f"EVENT_STATUS_INVALID:{event['event_id']}:{event.get('event_status')!r}")
    # The locked helper owns the simultaneous-population gate. Supplying values
    # that pass its other inputs isolates the helper's exact population clause,
    # without copying a threshold into this adapter.
    pop_pass = False
    pop_bins = []
    for bin_id in range(start, min(start + duration, end)):
        row = metric_index[(cell, profile, bin_id)]
        count = row.get("labels_nslow_ge2")
        if type(count) is not int or not 0 <= count <= 30:
            raise LockedSourceError(f"POPULATION_GATE_SOURCE_INVALID:{event['event_id']}:{bin_id}")
        passed = bool(analyzer.low_state_gate(True, 0.0, 1.0, count, alpha))
        pop_bins.append({"bin": bin_id, "labels_nslow_ge2": count,
                         "locked_population_gate_pass": passed})
    pop_pass = len(pop_bins) == duration and all(x["locked_population_gate_pass"] for x in pop_bins)
    exact_original = {key: attribution[key] for key in sorted(attribution)}
    return {
        "event_id": event["event_id"], "profile": profile, "cell": cell,
        "onset_lower": event.get("first_low_start_s"),
        "onset_upper": (30 * (int(event["first_low_bin"]) + 1)),
        "confirmation": event.get("confirmation_time_s"),
        "end": 30 * end,
        "locked_P_status": event.get("event_status"),
        "local_reference_status": reference,
        "numerical_gates": {
            "event_status": event.get("event_status"),
            "numerical_positive": numerical,
            "is_merge_core": event.get("is_merge_core"),
            "required_bins": duration,
            "low_speed_bins": event.get("low_speed_bins"),
            "density_factor": density_factor,
            "qualified_density_bins": event.get("qualified_density_bins"),
            "qualified_density_bin_ids": event.get("qualified_density_bin_ids"),
            "population_gate_bins": pop_bins,
        },
        "locked_numerical_positive": numerical,
        "locked_reference_pass": reference,
        "locked_population_pass": pop_pass,
        "locked_attribution_original": exact_original,
    }


def build_locked_event_source(metrics: list[dict] | None, events: list[dict] | None,
                              attribution_rows: list[dict] | None, analyzer,
                              binding: dict) -> tuple[list[dict], dict]:
    """Validate exact analyzer completeness and map events without reclassification."""
    if events is None or attribution_rows is None:
        raise LockedSourceError("EVENT_SOURCE_MISSING:events or attribution table absent")
    hashes = _bind_files(binding, analyzer)
    run_id = binding.get("run_id")
    run_label = binding.get("run_label")
    if not isinstance(run_id, str) or not run_id or not isinstance(run_label, str) or not run_label:
        raise LockedSourceError("RUN_BINDING_MISSING")
    metric_index, metric_key_sha = _validate_grid(metrics, analyzer, run_id, run_label)
    expected = _derive_event_keys(metric_index, analyzer, run_label)
    event_by_key = {}
    event_ids = set()
    for event in events:
        try:
            if (event.get("profile") not in EXPECTED_PROFILES or type(event.get("cell")) is not int
                    or type(event.get("first_low_bin")) is not int):
                raise TypeError("profile/cell/first_low_bin invalid")
            if type(event.get("low_bin_end_exclusive")) is not int:
                raise TypeError("low_bin_end_exclusive invalid")
            key = (event["profile"], event["cell"], event["first_low_bin"])
            eid = event["event_id"]
        except (KeyError, TypeError, ValueError) as exc:
            raise LockedSourceError(f"EVENT_ROW_SCHEMA_INVALID:{exc}") from exc
        if not isinstance(eid, str) or not eid or eid in event_ids or key in event_by_key:
            raise LockedSourceError(f"DUPLICATE_EVENT_SOURCE:{key}:{eid}")
        event_ids.add(eid)
        if key not in expected:
            raise LockedSourceError(f"UNEXPECTED_EVENT_SOURCE:{key}")
        if event.get("low_bin_end_exclusive") != expected[key][1]:
            raise LockedSourceError(f"EVENT_SOURCE_RUN_BOUNDARY_MISMATCH:{eid}")
        expected_id = analyzer.cell_event_id(run_label, key[0], key[1], key[2])
        if eid != expected_id or event.get("run") != run_label:
            raise LockedSourceError(f"EVENT_ID_OR_RUN_BINDING_MISMATCH:{eid}")
        event_by_key[key] = event
    if set(event_by_key) != set(expected):
        missing = set(expected) - set(event_by_key)
        extra = set(event_by_key) - set(expected)
        raise LockedSourceError(f"EVENT_DERIVATION_COVERAGE_MISMATCH:missing={len(missing)},extra={len(extra)}")
    attrib_by_id = {}
    for row in attribution_rows:
        eid = row.get("event_id")
        if not isinstance(eid, str) or not eid or eid in attrib_by_id:
            raise LockedSourceError(f"DUPLICATE_OR_MISSING_ATTRIBUTION_EVENT:{eid!r}")
        if row.get("run") != run_label:
            raise LockedSourceError(f"ATTRIBUTION_RUN_BINDING_MISMATCH:{eid}")
        attrib_by_id[eid] = row
    if set(attrib_by_id) != event_ids:
        raise LockedSourceError(
            f"ATTRIBUTION_EVENT_COVERAGE_MISMATCH:missing={len(event_ids-set(attrib_by_id))},"
            f"extra={len(set(attrib_by_id)-event_ids)}")
    mapped = []
    ordered_events = sorted(events, key=lambda row: row["event_id"])
    for event in ordered_events:
        key = (str(event["profile"]), int(event["cell"]), int(event["first_low_bin"]))
        mapped.append(_event_projection(event, attrib_by_id[event["event_id"]], metric_index,
                                        analyzer, run_id))
    event_source_digest = hashlib.sha256(canonical_bytes({
        "metrics_sha256": _content_sha(metrics, ("cell", "profile", "bin")),
        "events_sha256": _content_sha(events, ("event_id",)),
        "attribution_sha256": _content_sha(attribution_rows, ("event_id",)),
    })).hexdigest()
    receipt = {
        "schema_version": 1,
        "status": "COMPLETE_ZERO_EVENTS" if not events else "COMPLETE_EVENTS",
        "run_id": run_id, "run_label": run_label,
        "hash_bindings": hashes,
        "expected_grid": {"cells": list(CELL_IDS), "profiles": list(EXPECTED_PROFILES),
                          "bins": list(BIN_IDS), "metric_rows": len(CELL_IDS)*len(EXPECTED_PROFILES)*len(BIN_IDS)},
        "observed_metric_rows": len(metrics), "metric_key_sha256": metric_key_sha,
        "metric_content_sha256": _content_sha(metrics, ("cell", "profile", "bin")),
        "derived_event_count": len(expected), "source_event_count": len(events),
        "event_ids_sha256": hashlib.sha256(canonical_bytes(sorted(event_ids))).hexdigest(),
        "event_content_sha256": _content_sha(events, ("event_id",)),
        "attribution_row_count": len(attribution_rows),
        "attribution_content_sha256": _content_sha(attribution_rows, ("event_id",)),
        "event_source_sha256": event_source_digest,
        "event_source_adapter": {"path": str(Path(__file__).resolve()),
                                 "sha256": sha256_file(Path(__file__))},
        "event_derivation": "maximal contiguous true runs of locked low_state_bin per cell/profile; no gates recomputed",
        "gate_mapping": {
            "locked_P_status": "candidate_events.event_status (copied)",
            "locked_numerical_positive": "candidate_events.numerical_positive (copied)",
            "locked_reference_pass": "candidate_events.ref_eligible (copied)",
            "locked_population_pass": "locked low_state_gate called on each required bin with non-population inputs set to passing values",
            "locked_attribution_original": "full matching attribution row (copied)",
        },
        "review_interface_scope": "P-profile events only; S/L events remain fully source-covered in this receipt but are not relabelled as P adjudications",
        "population_gate_source": "hash-bound analyzer.low_state_gate with non-population arguments set to passing values",
        "zero_event_is_complete": len(expected) == 0 and not events,
    }
    return mapped, receipt


def validate_locked_event_source(metrics: list[dict] | None, events: list[dict] | None,
                                 attribution_rows: list[dict] | None, receipt: dict | None,
                                 analyzer, binding: dict) -> tuple[str, list[str]]:
    if receipt is None or events is None or attribution_rows is None or metrics is None:
        return "UNKNOWN", ["LOCKED_EVENT_SOURCE_OR_RECEIPT_MISSING"]
    try:
        _, expected = build_locked_event_source(metrics, events, attribution_rows, analyzer, binding)
    except LockedSourceError as exc:
        return "FAIL", [str(exc)]
    if receipt != expected:
        return "FAIL", ["LOCKED_EVENT_SOURCE_RECEIPT_MISMATCH"]
    return ("PASS_ZERO" if receipt["status"] == "COMPLETE_ZERO_EVENTS" else "PASS"), []

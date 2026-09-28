"""Fail-closed serializer/validator for the reviewed-attribution interface.

The module does not assess attribution evidence. It preserves supplied locked
event fields, emits one review row per event and §10 alternative, defaults all
reviews to UNKNOWN, and accepts non-UNKNOWN review only after caller-provided
signature verification and on-disk evidence hash checks. Production callers
must supply a trust-root-backed signature verifier; this module defines none.
"""
from __future__ import annotations

import csv
import hashlib
import io
import json
import math
from pathlib import Path
from typing import Callable

ALTERNATIVES = ("source_insertion", "downstream_tailback", "direct_tls",
                "geometry_unrelated_bottleneck")
STATUSES = {"CLEARED", "CONTRADICTED", "UNKNOWN"}
LOCKED_FIELDS = (
    "event_id", "cell", "onset_lower", "onset_upper", "confirmation", "end",
    "locked_P_status", "local_reference_status", "numerical_gates",
    "locked_numerical_positive", "locked_reference_pass", "locked_population_pass",
    "locked_attribution_original",
)
REVIEW_FIELDS = (
    "event_id", "alternative", "status", "evidence_paths", "hashes", "vehicle_ids",
    "cell_lane", "time_bounds", "reason", "reviewer", "reviewer_signature",
)
OUTPUT_FIELDS = LOCKED_FIELDS + ("alternative", "reviewed_attribution_status",
                                 "adjudicated_P_status") + REVIEW_FIELDS[2:]
PROVENANCE_FIELDS = ("run_id", "method_sha256", "locked_analyzer_sha256", "event_source_sha256")


def _is_sha256(value: object) -> bool:
    return isinstance(value, str) and len(value) == 64 and all(c in "0123456789abcdef" for c in value)


def _canonical(value: object) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False).encode("utf-8")


def csv_bytes(rows: list[dict]) -> bytes:
    buf = io.StringIO(newline="")
    writer = csv.DictWriter(buf, fieldnames=OUTPUT_FIELDS, extrasaction="raise", lineterminator="\n")
    writer.writeheader()
    writer.writerows({key: json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False)
                       if isinstance(value, (list, dict)) else value
                       for key, value in row.items()} for row in rows)
    return buf.getvalue().encode("utf-8")


def signing_payload(review: dict, provenance: dict, locked_event_sha256: str) -> bytes:
    """Context-bound canonical bytes for an external trusted signature system."""
    payload = {key: value for key, value in review.items() if key != "reviewer_signature"}
    return _canonical({"review": payload, "provenance": _validate_provenance(provenance),
                       "locked_event_sha256": locked_event_sha256})


def _validate_provenance(provenance: dict) -> dict:
    result = {key: provenance.get(key) for key in PROVENANCE_FIELDS}
    if not isinstance(result["run_id"], str) or not result["run_id"].strip():
        raise ValueError("provenance run_id is missing")
    for key in PROVENANCE_FIELDS[1:]:
        if not _is_sha256(result[key]):
            raise ValueError(f"provenance {key} must be a lowercase SHA-256")
    return result


def _validate_events(events: list[dict]) -> list[dict]:
    out = []
    seen = set()
    for event in events:
        missing = [field for field in LOCKED_FIELDS if field not in event]
        if missing:
            raise ValueError(f"locked event fields missing: {missing}")
        eid = event["event_id"]
        if not isinstance(eid, str) or not eid or eid in seen:
            raise ValueError(f"missing/duplicate locked event_id: {eid!r}")
        seen.add(eid)
        if any(type(event[field]) is not bool for field in
               ("locked_numerical_positive", "locked_reference_pass", "locked_population_pass")):
            raise ValueError(f"locked gate fields must be explicit booleans: {eid}")
        # Reject NaN/Infinity in copied metadata while preserving all values.
        _canonical({field: event[field] for field in LOCKED_FIELDS})
        out.append({field: event[field] for field in LOCKED_FIELDS})
    return sorted(out, key=lambda event: event["event_id"])


def event_locked_digest(event: dict) -> str:
    """Digest the exact locked classifier/event fields for one event."""
    canonical_event = {field: event[field] for field in LOCKED_FIELDS}
    return hashlib.sha256(_canonical(canonical_event)).hexdigest()


def _validate_evidence(review: dict, evidence_root: Path | None) -> tuple[list[str], dict[str, str]]:
    paths = review.get("evidence_paths")
    hashes = review.get("hashes")
    if not isinstance(paths, list) or not paths:
        raise ValueError("non-UNKNOWN review requires evidence_paths")
    if any(not isinstance(p, str) or not p for p in paths) or len(paths) != len(set(paths)):
        raise ValueError("review evidence_paths must be unique nonempty strings")
    if not isinstance(hashes, dict) or set(hashes) != set(paths):
        raise ValueError("review evidence path/hash keys do not match")
    root = evidence_root.resolve() if evidence_root is not None else None
    for raw in paths:
        path = Path(raw)
        path = path.resolve() if path.is_absolute() else ((root / path).resolve() if root else None)
        if path is None or (root is not None and not path.is_relative_to(root)):
            raise ValueError(f"evidence path missing, unbound, or escapes evidence root: {raw}")
        if not path.is_file():
            raise ValueError(f"review evidence file missing: {path}")
        digest = hashlib.sha256(path.read_bytes()).hexdigest()
        if not _is_sha256(hashes[raw]) or digest != hashes[raw]:
            raise ValueError(f"review evidence hash mismatch: {raw}")
    # Preserve exactly the signed path/hash strings; canonicalizing after
    # signature verification would make the emitted record differ from what
    # the external reviewer signed.
    return list(paths), dict(hashes)


def _normalize_review(event_id: str, alternative: str, review: dict | None,
                      evidence_root: Path | None,
                      provenance: dict, locked_event_sha256: str,
                      signature_verifier: Callable[[str, bytes, str], bool] | None) -> dict:
    if review is None:
        return {"event_id": event_id, "alternative": alternative, "status": "UNKNOWN",
                "evidence_paths": [], "hashes": {}, "vehicle_ids": [], "cell_lane": None,
                "time_bounds": None, "reason": "NO_REVIEW_RECORD", "reviewer": None,
                "reviewer_signature": None}
    if review.get("event_id") != event_id or review.get("alternative") != alternative:
        raise ValueError("review event/alternative key mismatch")
    status = review.get("status")
    if status not in STATUSES:
        raise ValueError(f"unsupported reviewed attribution status: {status!r}")
    normalized = {key: review.get(key) for key in REVIEW_FIELDS}
    if status == "UNKNOWN":
        if not isinstance(normalized["reason"], str) or not normalized["reason"].strip():
            raise ValueError("reviewed UNKNOWN requires a reason")
        if normalized["reviewer"] is not None and not str(normalized["reviewer"]).strip():
            raise ValueError("reviewer must be nonempty or null")
        normalized["evidence_paths"] = normalized["evidence_paths"] or []
        normalized["hashes"] = normalized["hashes"] or {}
        normalized["vehicle_ids"] = normalized["vehicle_ids"] or []
        return normalized
    if not isinstance(normalized["reviewer"], str) or not normalized["reviewer"].strip():
        raise ValueError("CLEARED/CONTRADICTED review requires reviewer")
    if not isinstance(normalized["reason"], str) or not normalized["reason"].strip():
        raise ValueError("CLEARED/CONTRADICTED review requires reason")
    if not isinstance(normalized["cell_lane"], str) or not normalized["cell_lane"].strip():
        raise ValueError("CLEARED/CONTRADICTED review requires cell_lane")
    bounds = normalized["time_bounds"]
    if (not isinstance(bounds, dict) or set(bounds) != {"lower", "upper"}
            or any(type(v) not in (int, float) or not math.isfinite(v) for v in bounds.values())
            or bounds["lower"] > bounds["upper"]):
        raise ValueError("CLEARED/CONTRADICTED review requires finite ordered time_bounds")
    ids = normalized["vehicle_ids"]
    if not isinstance(ids, list) or not ids or any(not isinstance(v, str) or not v for v in ids):
        raise ValueError("review vehicle_ids must be a nonempty explicit string list")
    evidence_paths, hashes = _validate_evidence(normalized, evidence_root)
    signature = normalized["reviewer_signature"]
    if not isinstance(signature, str) or not signature.strip() or signature_verifier is None:
        raise ValueError("review signature missing or no trusted verifier configured")
    payload = signing_payload(normalized, provenance, locked_event_sha256)
    if not signature_verifier(normalized["reviewer"], payload, signature):
        raise ValueError("review signature verification failed")
    normalized["evidence_paths"] = evidence_paths
    normalized["hashes"] = hashes
    return normalized


def build_interface(events: list[dict], provenance: dict, reviews: list[dict] | None = None,
                    *, evidence_root: Path | None = None,
                    signature_verifier: Callable[[str, bytes, str], bool] | None = None) -> tuple[list[dict], dict]:
    """Return complete event×alternative rows plus their bound receipt.

    No status is inferred: absent records become UNKNOWN. A qualifying
    adjudicated status requires all three locked gates true and every prescribed
    alternative explicitly CLEARED by valid signed evidence.
    """
    prov = _validate_provenance(provenance)
    locked_events = _validate_events(events)
    review_index = {}
    for review in reviews or []:
        key = (review.get("event_id"), review.get("alternative"))
        if key in review_index:
            raise ValueError(f"duplicate review record: {key}")
        review_index[key] = review
    event_ids = {e["event_id"] for e in locked_events}
    if any(eid not in event_ids or alt not in ALTERNATIVES for eid, alt in review_index):
        raise ValueError("review record refers to unknown event or alternative")
    rows = []
    for event in locked_events:
        event_reviews = []
        for alt in ALTERNATIVES:
            checked = _normalize_review(event["event_id"], alt, review_index.get((event["event_id"], alt)),
                                        evidence_root, prov, event_locked_digest(event), signature_verifier)
            event_reviews.append(checked)
        all_clear = all(row["status"] == "CLEARED" for row in event_reviews)
        locked_gates_pass = all(event[key] is True for key in
                                ("locked_numerical_positive", "locked_reference_pass", "locked_population_pass"))
        reviewed_status = "ALL_ALTERNATIVES_CLEARED" if all_clear else "REVIEW_NOT_ALL_CLEARED"
        if all_clear and locked_gates_pass:
            adjudicated = "RULE_GATES_SATISFIED_WITH_REVIEWED_ATTRIBUTION"
        elif not locked_gates_pass:
            adjudicated = "NOT_ADJUDICATED_LOCKED_GATES_NOT_ALL_PASS"
        else:
            adjudicated = "NOT_ADJUDICATED_ATTRIBUTION_NOT_ALL_CLEARED"
        for review in event_reviews:
            rows.append({**event, "alternative": review["alternative"],
                         "reviewed_attribution_status": reviewed_status,
                         "adjudicated_P_status": adjudicated,
                         **{key: review[key] for key in REVIEW_FIELDS[2:]}})
    csv_data = csv_bytes(rows)
    receipt = {"schema_version": 1, "status": "COMPLETE_BOUND_ZERO_EVENT" if not locked_events
               else "COMPLETE_REVIEW_INTERFACE_ROWS", **prov,
               "event_count": len(locked_events), "alternative_count_per_event": len(ALTERNATIVES),
               "row_count": len(rows), "csv_sha256": hashlib.sha256(csv_data).hexdigest(),
               "locked_events_sha256": hashlib.sha256(_canonical(locked_events)).hexdigest(),
               "alternative_labels": list(ALTERNATIVES),
               "signature_verification": ("CALLER_PROVIDED_VERIFIER_ACCEPTED_SIGNED_ROWS"
                                          if any((r.get("status") in {"CLEARED", "CONTRADICTED"})
                                                 for r in (reviews or []))
                                          else "NO_SIGNED_REVIEW_ROWS")}
    return rows, receipt


def validate_receipt(rows: list[dict], receipt: dict | None, provenance: dict, *,
                     evidence_root: Path | None = None,
                     signature_verifier: Callable[[str, bytes, str], bool] | None = None) -> tuple[str, list[str]]:
    if receipt is None:
        return "UNKNOWN", ["ATTRIBUTION_RECEIPT_MISSING"]
    reasons = []
    try:
        prov = _validate_provenance(provenance)
    except ValueError as exc:
        return "UNKNOWN", [f"EXPECTED_PROVENANCE_INVALID:{exc}"]
    for key, value in prov.items():
        if receipt.get(key) != value:
            reasons.append(f"PROVENANCE_MISMATCH:{key}")
    expected_n = receipt.get("event_count")
    if type(expected_n) is not int or expected_n < 0:
        reasons.append("EVENT_COUNT_INVALID")
    if receipt.get("alternative_count_per_event") != len(ALTERNATIVES):
        reasons.append("ALTERNATIVE_COUNT_MISMATCH")
    if receipt.get("row_count") != len(rows):
        reasons.append("ROW_COUNT_MISMATCH")
    if len(rows) != (expected_n * len(ALTERNATIVES) if isinstance(expected_n, int) else -1):
        reasons.append("EVENT_ALTERNATIVE_CARDINALITY_MISMATCH")
    actual_csv_hash = hashlib.sha256(csv_bytes(rows)).hexdigest()
    if receipt.get("csv_sha256") != actual_csv_hash:
        reasons.append("CSV_HASH_MISMATCH")
    groups = {}
    event_payloads = {}
    for row in rows:
        groups.setdefault(row.get("event_id"), []).append(row.get("alternative"))
        payload = {field: row.get(field) for field in LOCKED_FIELDS}
        prior = event_payloads.setdefault(row.get("event_id"), payload)
        if prior != payload:
            reasons.append(f"LOCKED_EVENT_FIELDS_INCONSISTENT:{row.get('event_id')}")
    if any(sorted(alts) != sorted(ALTERNATIVES) for alts in groups.values()):
        reasons.append("EVENT_ALTERNATIVE_COVERAGE_MISMATCH")
    for event_id, alternatives in groups.items():
        event_rows = [row for row in rows if row.get("event_id") == event_id]
        statuses = [row.get("status") for row in event_rows]
        if any(status not in STATUSES for status in statuses):
            reasons.append(f"REVIEW_STATUS_INVALID:{event_id}")
        all_clear = len(statuses) == len(ALTERNATIVES) and all(status == "CLEARED" for status in statuses)
        expected_reviewed = "ALL_ALTERNATIVES_CLEARED" if all_clear else "REVIEW_NOT_ALL_CLEARED"
        if any(row.get("reviewed_attribution_status") != expected_reviewed for row in event_rows):
            reasons.append(f"REVIEWED_ATTRIBUTION_LABEL_MISMATCH:{event_id}")
        locked_gates_pass = all(all(row.get(key) is True for key in
                                    ("locked_numerical_positive", "locked_reference_pass", "locked_population_pass"))
                                for row in event_rows)
        expected_adjudicated = (
            "RULE_GATES_SATISFIED_WITH_REVIEWED_ATTRIBUTION" if all_clear and locked_gates_pass else
            "NOT_ADJUDICATED_LOCKED_GATES_NOT_ALL_PASS" if not locked_gates_pass else
            "NOT_ADJUDICATED_ATTRIBUTION_NOT_ALL_CLEARED")
        if any(row.get("adjudicated_P_status") != expected_adjudicated for row in event_rows):
            reasons.append(f"ADJUDICATION_LABEL_MISMATCH:{event_id}")
        for row in event_rows:
            if row.get("status") == "UNKNOWN":
                continue
            review_record = {"event_id": event_id, "alternative": row.get("alternative"),
                             **{key: row.get(key) for key in REVIEW_FIELDS[2:]}}
            locked_event = {key: row.get(key) for key in LOCKED_FIELDS}
            try:
                _normalize_review(event_id, row.get("alternative"), review_record, evidence_root,
                                  prov, event_locked_digest(locked_event), signature_verifier)
            except (ValueError, TypeError) as exc:
                reasons.append(f"REVIEW_ROW_INVALID:{event_id}:{row.get('alternative')}:{exc}")
    locked_sorted = [event_payloads[eid] for eid in sorted(event_payloads)]
    if receipt.get("locked_events_sha256") != hashlib.sha256(_canonical(locked_sorted)).hexdigest():
        reasons.append("LOCKED_EVENT_HASH_MISMATCH")
    if not rows and receipt.get("status") != "COMPLETE_BOUND_ZERO_EVENT":
        reasons.append("ZERO_EVENT_RECEIPT_NOT_COMPLETE")
    if rows and receipt.get("status") != "COMPLETE_REVIEW_INTERFACE_ROWS":
        reasons.append("NONZERO_RECEIPT_STATUS_MISMATCH")
    if receipt.get("alternative_labels") != list(ALTERNATIVES):
        reasons.append("ALTERNATIVE_LABELS_MISMATCH")
    return ("UNKNOWN", reasons) if reasons else ("PASS", [])


def write_interface(csv_path: Path, receipt_path: Path, events: list[dict], provenance: dict,
                    reviews: list[dict] | None = None, *, evidence_root: Path | None = None,
                    signature_verifier: Callable[[str, bytes, str], bool] | None = None) -> dict:
    """Write new files only; caller is responsible for exclusive output paths."""
    if csv_path.exists() or receipt_path.exists():
        raise FileExistsError("attribution outputs already exist; use a new revision")
    rows, receipt = build_interface(events, provenance, reviews, evidence_root=evidence_root,
                                    signature_verifier=signature_verifier)
    csv_path.parent.mkdir(parents=True, exist_ok=True)
    receipt_path.parent.mkdir(parents=True, exist_ok=True)
    csv_path.write_bytes(csv_bytes(rows))
    receipt["csv_path"] = str(csv_path)
    receipt_path.write_text(json.dumps(receipt, indent=2, allow_nan=False) + "\n", encoding="utf-8")
    return receipt

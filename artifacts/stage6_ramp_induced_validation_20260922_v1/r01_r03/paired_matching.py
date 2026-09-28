"""Fail-visible, exact-field comparison primitives for future R03 pair audit.

No tolerances are applied. This module is pure/offline and does not read or write
simulation data; callers must bind rows to immutable raw-source hashes.
"""
from __future__ import annotations

from typing import Mapping

ID_FIELDS = ("class", "vehicle_id")
PLANNED_FIELDS = ("scheduled_depart", "route_id", "type_id", "depart_pos", "depart_lane", "depart_speed")
OBSERVED_FIELDS = ("actual_depart", "speed_factor_precise")
PRE_R_SAMPLE_FIELDS = ("time", "lane", "pos", "x", "speed")


def _key(row: Mapping) -> tuple[str, str]:
    return str(row["class"]), str(row["vehicle_id"])


def _compare_materialized(left: dict, right: dict, fields: tuple[str, ...]) -> dict:
    only_left = sorted(set(left) - set(right))
    only_right = sorted(set(right) - set(left))
    mismatches = []
    incomplete = []
    for key in sorted(set(left) & set(right)):
        missing = {field: {"control_present": field in left[key] and left[key].get(field) is not None,
                           "transition_present": field in right[key] and right[key].get(field) is not None}
                   for field in fields
                   if field not in left[key] or left[key].get(field) is None
                   or field not in right[key] or right[key].get(field) is None}
        if missing:
            incomplete.append({"key": list(key), "missing_fields": missing})
        diff = {field: {"control": left[key].get(field), "transition": right[key].get(field)}
                for field in fields if field in left[key] and field in right[key]
                and left[key].get(field) is not None and right[key].get(field) is not None
                and left[key].get(field) != right[key].get(field)}
        if diff:
            mismatches.append({"key": list(key), "fields": diff})
    status = ("INCOMPLETE_REQUIRED_FIELDS" if incomplete else
              "MISMATCH_VISIBLE" if only_left or only_right or mismatches else "PASS_EXACT")
    return {"status": status,
            "only_control": [list(x) for x in only_left], "only_transition": [list(x) for x in only_right],
            "mismatches": mismatches, "incomplete": incomplete}


def compare_pair(control_rows: list[Mapping], transition_rows: list[Mapping], fields: tuple[str, ...]) -> dict:
    left = {_key(row): row for row in control_rows}
    right = {_key(row): row for row in transition_rows}
    if len(left) != len(control_rows) or len(right) != len(transition_rows):
        raise ValueError("duplicate class/vehicle key")
    return _compare_materialized(left, right, fields)

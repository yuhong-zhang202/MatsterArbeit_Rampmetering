"""Minimum implementation correction for the unchanged post-red invariant.

No SUMO import. Original V15 checks/interlock remain immutable. The additional
precondition budgets the green advance AND subsequent red reaction/braking.
"""
from dataclasses import replace
import math
from pathlib import Path
import sys
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))
from stage6_safe_actuator_v10 import (VehicleState, assess_release as legacy_assess_release,
                                    immediate_red_stop_requirement_m)

REVISION = "FIX02_GREEN_ADVANCE_PLUS_POST_RED"
UPSTREAM_LANE = ":urban_diverge_1_0"


def required_pre_green_distance_m(state: VehicleState, margin_m=1.1):
    """Upper bound of advance during green plus unchanged post-red envelope.

    For dt=1, v1<=v+a and green distance<=v+a. The unchanged post test is
    monotone in nonnegative v1. Both stopped and moving followers may accelerate
    during green, so the stopped post shortcut does not remove their pre bound.
    """
    immediate_red_stop_requirement_m(state, margin_m)  # Existing validation.
    maximum_next_speed = state.speed_m_s + state.accel_m_s2
    return maximum_next_speed + immediate_red_stop_requirement_m(
        replace(state, speed_m_s=maximum_next_speed), margin_m)


def checked_upstream_geometry(network_path):
    root = ET.parse(network_path).getroot()
    upstream = root.find("./edge[@id=':urban_diverge_1']/lane[@id=':urban_diverge_1_0']")
    if upstream is None or float(upstream.get("length")) != 113.08:
        raise ValueError("upstream entrant geometry changed")
    incoming = [node for node in root.findall("connection") if node.get("to") == "ramp_storage"]
    expected = {(":urban_diverge_1", "0", "0", None),
                ("shared_approach", "0", "0", UPSTREAM_LANE)}
    actual = {(node.get("from"), node.get("fromLane"), node.get("toLane"), node.get("via")) for node in incoming}
    if actual != expected:
        raise ValueError("uncovered storage entry connection")
    return float(upstream.get("length"))


def checked_ramp_input_type(route_path):
    root = ET.parse(route_path).getroot()
    routes = {node.get("id"):node.get("edges").split() for node in root.findall("route")}
    types = set()
    for node in root.findall("vehicle"):
        if node.get("id", "").split("_", 1)[0] != "R":
            continue
        route = routes.get(node.get("route"), [])
        if route != ["urban_in", "shared_approach", "ramp_storage", "ramp_accel", "merge_section", "main_down"]:
            raise ValueError("uncovered ramp entry route")
        types.add(node.get("type"))
    if types != {"technical_passenger"}:
        raise ValueError("uncovered future ramp vehicle type")
    return next(iter(types))


def qualify_entrant_coverage(*, upstream_length_m, max_speed_m_s, accel_m_s2,
                            tau_s, action_step_s):
    values = (upstream_length_m, max_speed_m_s, accel_m_s2, tau_s, action_step_s)
    if not all(math.isfinite(value) and value > 0 for value in values):
        raise ValueError("invalid actual entrant coverage values")
    if tau_s != 1.0 or action_step_s != 1.0:
        raise ValueError("entrant dynamics violate fixed one-second contract")
    # All current internal-lane R are checked. Anything further upstream or
    # newly inserted on urban_in must traverse the whole internal connector.
    # This generous physical upper bound must be shorter than that connector.
    if max_speed_m_s + accel_m_s2 >= upstream_length_m:
        raise ValueError("future entrant coverage not proven")
    return dict(revision=REVISION, upstream_lane=UPSTREAM_LANE,
                upstream_length_m=upstream_length_m, maximum_type_speed_m_s=max_speed_m_s,
                type_accel_m_s2=accel_m_s2,
                maximum_one_step_advance_m=max_speed_m_s+accel_m_s2,
                tau_s=tau_s, action_step_s=action_step_s,
                coverage="all current storage followers and all internal-lane R; others/new route entrants cannot reach storage in one green step")


def assess_release(*, approaching_vehicles, **kwargs):
    """Retain legacy checks and add the missing pre/post invariant condition.

    Approaching positions are projected into storage-lane coordinates and must
    be <=0. The controlled front belongs to the storage population exclusively.
    """
    vehicles = kwargs["vehicles"]
    length = kwargs["storage_length_m"]
    margin = kwargs.get("margin_m", 1.1)
    if set(vehicles) & set(approaching_vehicles):
        raise ValueError("duplicate current/approaching guard identity")
    if any(state.position_m > 0 for state in approaching_vehicles.values()):
        raise ValueError("approaching coordinate must be upstream of storage")
    decision = legacy_assess_release(**kwargs)
    front = decision.get("front_id", "")
    prediction = []
    unsafe = []
    for vid, state in {**vehicles, **approaching_vehicles}.items():
        if vid == front:
            continue
        required = required_pre_green_distance_m(state, margin)
        gap = length - state.position_m
        safe = gap + 1e-9 >= required
        prediction.append(dict(vehicle_id=vid, projected_position_m=state.position_m,
                               speed_m_s=state.speed_m_s, accel_m_s2=state.accel_m_s2,
                               normal_decel_m_s2=state.normal_decel_m_s2,
                               gap_m=gap, required_m=required, safe=safe,
                               population="approaching" if vid in approaching_vehicles else "storage"))
        if not safe:
            unsafe.append(vid)
    decision["pre_green_post_red_prediction"] = prediction
    decision["guard_revision"] = REVISION
    if decision["allowed"] and unsafe:
        decision.update(allowed=False, reason="FOLLOWER_POST_RED_PREDICTION",
                        unsafe_followers=tuple(sorted(unsafe)))
    return decision

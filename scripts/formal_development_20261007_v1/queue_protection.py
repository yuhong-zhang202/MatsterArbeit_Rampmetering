"""Prospectively defined development risk proxy; not continuous spillback.

All distances use actual compiled lane lengths and actual vehicle body length.
The controller observes low-speed R on the upstream connector and storage.
The shared lane is recorded independently and cannot turn a city-red queue
into a ramp-risk trigger by itself. No formal acceptance threshold is defined.
"""
from dataclasses import dataclass
import math

LANES = ("shared_approach_0", ":urban_diverge_1_0", "ramp_storage_0")


@dataclass(frozen=True)
class QueueParameters:
    trigger_distance_m: float = 261.03
    release_distance_m: float = 102.245
    trigger_confirm_s: int = 10
    release_confirm_s: int = 30
    low_speed_m_s: float = 1.389
    protected_rate_veh_h: float = 900.0
    start_s: int = 600
    end_s: int = 4200

    def __post_init__(self):
        if not (0 <= self.release_distance_m < self.trigger_distance_m):
            raise ValueError("invalid hysteresis distances")
        if self.trigger_confirm_s < 1 or self.release_confirm_s < 1:
            raise ValueError("invalid confirmation periods")
        if self.protected_rate_veh_h != 900 or self.low_speed_m_s != 1.389:
            raise ValueError("outside authorized development definition")


def risk_snapshot(vehicles, lane_lengths):
    """Pre-step risk from a complete three-lane snapshot, in metres upstream.

    vehicles: (id, lane, front_position, speed, actual_length). Empty observed
    lanes are valid. Incomplete/invalid input raises before a simulation step.
    Risk is the farthest low-speed R rear in storage/upstream internal lane;
    gaps are allowed, so it is an extent proxy, not a meter-anchored queue.
    """
    if set(lane_lengths) != set(LANES):
        raise ValueError("incomplete mapped geometry")
    offsets = {}; distance = 0.0
    for lane in LANES:
        length = lane_lengths[lane]
        if not math.isfinite(length) or length <= 0:
            raise ValueError("invalid lane length")
        offsets[lane] = distance; distance += length
    ids = set(); risk = 0.0; shared_risk = 0.0; low = []; raw = []
    for vid, lane, pos, speed, length in vehicles:
        if vid in ids or lane not in offsets:
            raise ValueError("duplicate ID or unmapped lane")
        ids.add(vid)
        if not all(math.isfinite(x) for x in (pos, speed, length)):
            raise ValueError("nonfinite vehicle observation")
        if length <= 0 or speed < 0 or not (0 <= pos <= lane_lengths[lane] + 1e-6):
            raise ValueError("invalid vehicle observation")
        raw.append({"id": vid, "lane": lane, "front_m": pos,
                    "speed_m_s": speed, "length_m": length})
        if vid.split("_", 1)[0] != "R" or speed >= 1.389:
            continue
        rear_distance = distance - (offsets[lane] + pos - length)
        low.append({"id": vid, "lane": lane, "front_m": pos,
                    "speed_m_s": speed, "length_m": length,
                    "rear_distance_upstream_meter_m": rear_distance})
        if lane == LANES[0]:
            shared_risk = max(shared_risk, rear_distance)
        else:
            risk = max(risk, rear_distance)
    return {"risk_extent_m": risk, "shared_low_R_extent_m": shared_risk,
            "low_R_records": low, "observed_vehicle_records": raw,
            "mapped_vehicle_count": len(ids),
            "observation_valid": True}


class QueueOverride:
    def __init__(self, parameters=QueueParameters()):
        self.p = parameters; self.active = False
        self.trigger_streak = 0; self.release_streak = 0
        self.next_time_s = parameters.start_s

    def step(self, time_s, risk_extent_m, nominal_rate_veh_h):
        if time_s != self.next_time_s or time_s >= self.p.end_s:
            raise ValueError("nonsequential queue decision")
        if not math.isfinite(risk_extent_m) or risk_extent_m < 0:
            raise ValueError("invalid queue observation; no step permitted")
        if not math.isfinite(nominal_rate_veh_h) or not 300 <= nominal_rate_veh_h <= 900:
            raise ValueError("invalid nominal ALINEA rate")
        prior = self.active; transition = "NONE"
        if not self.active:
            self.release_streak = 0
            self.trigger_streak = self.trigger_streak + 1 if risk_extent_m >= self.p.trigger_distance_m else 0
            if self.trigger_streak >= self.p.trigger_confirm_s:
                self.active = True; self.trigger_streak = 0; transition = "ACTIVATE"
        else:
            self.trigger_streak = 0
            self.release_streak = self.release_streak + 1 if risk_extent_m <= self.p.release_distance_m else 0
            if self.release_streak >= self.p.release_confirm_s:
                self.active = False; self.release_streak = 0; transition = "RELEASE"
        self.next_time_s += 1
        # The nominal feedback object is never modified by this module.
        return {"override_active_before": prior, "override_active": self.active,
                "transition": transition, "trigger_streak_s": self.trigger_streak,
                "release_streak_s": self.release_streak,
                "override_request_veh_h": self.p.protected_rate_veh_h if self.active else None,
                "nominal_clipped_veh_h": nominal_rate_veh_h,
                "final_command_veh_h": max(nominal_rate_veh_h, self.p.protected_rate_veh_h) if self.active else nominal_rate_veh_h}

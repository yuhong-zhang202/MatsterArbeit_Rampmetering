"""Prospective Candidate A phase/rate contract, without SUMO imports.

E counts nominal packets at planned cycle ends independently of denied starts.
n is a mapping assumption and must never substitute for measured crossings.
"""
from dataclasses import dataclass
from fractions import Fraction
import math


def command_fraction(value):
    result = Fraction(str(value))
    if not 300 <= result <= 900:
        raise ValueError("command outside unchanged 300--900 veh/h domain")
    return result


@dataclass(frozen=True)
class PhaseEnvelope:
    green_s: int = 3
    yellow_s: int = 3
    minimum_red_s: int = 2
    nominal_n: int = 2

    def __post_init__(self):
        if any(type(v) is not int or v <= 0 for v in vars(self).values()):
            raise ValueError("positive integer envelope dimensions required")
        if self.nominal_n != 2:
            raise ValueError("this prospective card has exactly one nominal packet assumption")
        if self.minimum_cycle_s > 4 * self.nominal_n:
            raise ValueError("STOP: complete envelope cannot nominally represent 900 veh/h")

    @property
    def minimum_cycle_s(self):
        return self.green_s + self.yellow_s + self.minimum_red_s

    def phases(self, period_s):
        if type(period_s) is not int or period_s < self.minimum_cycle_s:
            raise ValueError("cycle cannot fit complete phase envelope")
        return (("G", self.green_s, 1), ("y", self.yellow_s, 2),
                ("r", period_s - self.green_s - self.yellow_s, 2))

    def state_at(self, elapsed_s, period_s, executed=True):
        if not 0 <= elapsed_s < period_s:
            raise ValueError("outside cycle")
        if not executed:
            return "r"
        if elapsed_s < self.green_s:
            return "G"
        if elapsed_s < self.green_s + self.yellow_s:
            return "y"
        return "r"


class CycleLedger:
    """One virtual schedule; actual safety denials cannot erase expected service."""
    def __init__(self, activation_s, envelope=None):
        if activation_s not in (600, 1200):
            raise ValueError("outside prospective activation contract")
        self.envelope = envelope or PhaseEnvelope()
        self.activation_s = activation_s
        self.next_time_s = activation_s
        self.pending_command = None
        self.pending_requested_s = None
        self.applied_command = None
        self.elapsed_ideal_s = Fraction(0)
        self.cycle = None
        self.cycle_id = -1
        self.C = Fraction(0)
        self.C_applied = Fraction(0)
        self.E = 0
        self.N = 0
        self.crossed_ids = set()
        self.rows = []

    def begin_step(self, time_s, final_command):
        if time_s != self.next_time_s:
            raise ValueError("nonsequential command time")
        requested = command_fraction(final_command)
        if requested != self.pending_command:
            self.pending_command = requested
            self.pending_requested_s = time_s
        new_cycle = self.cycle is None or time_s == self.cycle["end_s"]
        if new_cycle:
            self.applied_command = self.pending_command
            before = math.floor(self.elapsed_ideal_s)
            self.elapsed_ideal_s += Fraction(3600 * self.envelope.nominal_n, 1) / self.applied_command
            period = math.floor(self.elapsed_ideal_s) - before
            self.envelope.phases(period)
            self.cycle_id += 1
            self.cycle = {"cycle_id": self.cycle_id, "begin_s": time_s,
                          "end_s": time_s + period, "period_s": period,
                          "nominal_n": self.envelope.nominal_n,
                          "applied_command_veh_h": float(self.applied_command),
                          "command_requested_s": self.pending_requested_s,
                          "command_applied_s": time_s,
                          "application_delay_s": time_s-self.pending_requested_s,
                          "executed": None, "denial_reason": None,
                          "completed": False,
                          "N_G": 0, "N_y": 0, "N_r": 0,
                          "crossing_ids": []}
            self.rows.append(self.cycle)
        self.step_command = requested
        return new_cycle, self.cycle

    def mark_cycle_start(self, executed, denial_reason=""):
        if self.cycle is None or self.cycle["executed"] is not None:
            raise ValueError("duplicate or missing cycle start")
        self.cycle["executed"] = bool(executed)
        self.cycle["denial_reason"] = denial_reason

    def end_step(self, time_end_s, crossing_ids, motion_state):
        if time_end_s != self.next_time_s + 1 or self.cycle is None:
            raise ValueError("misaligned crossing bracket")
        if motion_state not in ("G", "y", "r"):
            raise ValueError("unknown crossing state")
        expected = self.envelope.state_at(self.next_time_s-self.cycle["begin_s"],
                                        self.cycle["period_s"], self.cycle["executed"])
        if motion_state != expected:
            raise ValueError("motion state differs from complete phase contract")
        ids = tuple(crossing_ids)
        if len(set(ids)) != len(ids) or self.crossed_ids.intersection(ids):
            raise ValueError("duplicate actual stopline crossing")
        self.crossed_ids.update(ids)
        self.C += self.step_command / 3600
        self.C_applied += self.applied_command / 3600
        self.N += len(ids)
        self.cycle["N_" + motion_state] += len(ids)
        self.cycle["crossing_ids"].extend(ids)
        e_delta = self.envelope.nominal_n if time_end_s == self.cycle["end_s"] else 0
        self.E += e_delta
        self.cycle["completed"] = bool(e_delta)
        self.next_time_s += 1
        return e_delta

    def accounting(self):
        return {"C": float(self.C), "C_applied": float(self.C_applied),
                "E": self.E, "N": self.N,
                "mapping_command_latency": float(self.C-self.C_applied),
                "mapping_quantization": float(self.C_applied-self.E),
                "physical_shortfall": self.E-self.N,
                "C_minus_E": float(self.C-self.E),
                "E_minus_N": self.E-self.N}


def motion_phase(observed_phase, observed_state, next_switch_s, time_s, phases):
    """SUMO1.26 switches at begin-of-step BEFORE motion.

    A nextSwitch==time event may be pending while the getter still shows the
    previous phase. Predict that one native transition before simulationStep.
    """
    if not (type(observed_phase) is int and 0 <= observed_phase < len(phases)):
        raise ValueError("missing/unknown observed phase")
    if not math.isfinite(next_switch_s) or next_switch_s < time_s-1e-7:
        raise ValueError("overdue/unobservable native phase event")
    if observed_state != phases[observed_phase][0]:
        raise ValueError("phase index/state mismatch")
    idx = phases[observed_phase][2] if next_switch_s <= time_s+1e-7 else observed_phase
    return idx, phases[idx][0]


def crossing_records(before_storage_ids, before_internal_ids, after_internal_ids,
                     time_s, cycle_id, motion_state):
    """Authoritative native link-entry bracket; no fictitious subsecond time."""
    new_ids = sorted(set(after_internal_ids)-set(before_internal_ids))
    if any(vid not in before_storage_ids for vid in new_ids):
        raise ValueError("uncovered stopline entrant")
    return [{"vehicle_id": vid, "crossing_time_lower_s": time_s,
             "crossing_time_upper_s": time_s+1, "time_interval": "(lower,upper]",
             "cycle_id": cycle_id, "motion_signal_state": motion_state}
            for vid in new_ids]

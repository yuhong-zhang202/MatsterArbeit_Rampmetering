"""Issue #2 offline contracts; no SUMO import and no production actuator.

Timing arguments are supplied test fixtures, not approved signal parameters.
Release opportunities and nominal vehicles per cycle are not actual crossings.
"""
from dataclasses import dataclass
from fractions import Fraction
import math


def rate_fraction(rate):
    value = Fraction(str(rate))
    if not 300 <= value <= 900:
        raise ValueError("outside the Issue #2 command domain")
    return value


@dataclass(frozen=True)
class CycleEnvelope:
    nominal_vehicles: int
    green_s: int
    yellow_s: int
    minimum_red_s: int

    def __post_init__(self):
        values = (self.nominal_vehicles, self.green_s, self.yellow_s,
                  self.minimum_red_s)
        if any(type(value) is not int or value <= 0 for value in values):
            raise ValueError("positive integer fixture dimensions required")
        if self.nominal_vehicles > 2:
            raise ValueError("investigation limited to one or two nominal vehicles")

    @property
    def minimum_cycle_s(self):
        return self.green_s + self.yellow_s + self.minimum_red_s

    @property
    def nominal_maximum_veh_h(self):
        return Fraction(3600 * self.nominal_vehicles, self.minimum_cycle_s)

    def program(self, cycle_s):
        if type(cycle_s) is not int or cycle_s < self.minimum_cycle_s:
            raise ValueError("cannot fit the full transition envelope")
        return (("G", self.green_s), ("y", self.yellow_s),
                ("r", cycle_s - self.green_s - self.yellow_s))

    def brackets(self, rate):
        period = Fraction(3600 * self.nominal_vehicles, 1) / rate_fraction(rate)
        lower, upper = math.floor(period), math.ceil(period)
        if lower < self.minimum_cycle_s:
            raise ValueError("requested rate exceeds the fixture timing envelope")
        # Fraction of cycles using upper period, not fraction of elapsed time.
        return lower, upper, period - lower

    def cycle_sequence(self, rate, cycles):
        lower, upper, upper_share = self.brackets(rate)
        if type(cycles) is not int or cycles <= 0:
            raise ValueError("positive cycle count required")
        residual = Fraction(0)
        result = []
        for _ in range(cycles):
            residual += upper_share
            use_upper = residual >= 1
            period = upper if use_upper else lower
            if use_upper:
                residual -= 1
            result.append(period)
        return result

    def closest_single_period(self, rate):
        lower, upper, _ = self.brackets(rate)
        command = rate_fraction(rate)
        period = min({lower, upper},
                     key=lambda c: (abs(Fraction(3600 * self.nominal_vehicles, c)
                                       - command), -c))
        mapped = Fraction(3600 * self.nominal_vehicles, period)
        return period, mapped, abs(mapped - command) / command


class SafeOpportunityLedger:
    """Idealized accounting, supplied eligibility, fixed service-cap headway.

    No vehicle dynamics or TLS switching are simulated. A denied credit may
    remain banked, with explicitly optional clipping. At the 900 command cap,
    denied opportunities cannot generally be recovered within the same window.
    """
    def __init__(self, minimum_headway_s=4, bank_limit=None):
        if type(minimum_headway_s) is not int or minimum_headway_s <= 0:
            raise ValueError("positive integer headway required")
        self.minimum_headway_s = minimum_headway_s
        self.bank_limit = None if bank_limit is None else Fraction(str(bank_limit))
        if self.bank_limit is not None and self.bank_limit < 1:
            raise ValueError("bank limit must hold at least one opportunity")
        self.next_time_s = 0
        self.last_release_s = None
        self.credit = Fraction(0)
        self.command_credit = Fraction(0)
        self.dropped_credit = Fraction(0)
        self.opportunities = 0

    def step(self, time_s, rate, *, demand=True, receiver=True, safe_gap=True):
        if time_s != self.next_time_s:
            raise ValueError("nonsequential replay")
        addition = rate_fraction(rate) / 3600
        self.command_credit += addition
        self.credit += addition
        headway = (self.last_release_s is None or
                   time_s - self.last_release_s >= self.minimum_headway_s)
        due = self.credit >= 1 and headway
        reason = "NOT_DUE_OR_HEADWAY"
        if due:
            reason = ("NO_DEMAND" if not demand else
                      "RECEIVER_BLOCKED" if not receiver else
                      "SAFE_GAP_DENIED" if not safe_gap else "OPPORTUNITY")
        release = reason == "OPPORTUNITY"
        if release:
            self.credit -= 1
            self.opportunities += 1
            self.last_release_s = time_s
        if self.bank_limit is not None and self.credit > self.bank_limit:
            self.dropped_credit += self.credit - self.bank_limit
            self.credit = self.bank_limit
        self.next_time_s += 1
        assert self.command_credit == (
            self.opportunities + self.dropped_credit + self.credit)
        return {"due": due, "opportunity": release, "reason": reason,
                "credit_after": self.credit, "dropped_credit": self.dropped_credit}

"""New prospective G/y/r safety witnesses, not migrated FIX02 qualification."""
from dataclasses import dataclass
import math


@dataclass(frozen=True)
class Vehicle:
    vehicle_id: str
    population: str
    position_m: float
    speed_m_s: float
    length_m: float
    min_gap_m: float
    accel_m_s2: float
    normal_decel_m_s2: float
    tau_s: float
    action_step_s: float
    type_id: str

    def validate(self):
        numeric=(self.position_m,self.speed_m_s,self.length_m,self.min_gap_m,
                 self.accel_m_s2,self.normal_decel_m_s2,self.tau_s,self.action_step_s)
        if (not self.vehicle_id.startswith("R_") or self.type_id != "technical_passenger"
                or not all(math.isfinite(v) for v in numeric)
                or self.speed_m_s < 0 or self.length_m <= 0 or self.min_gap_m < 0
                or self.accel_m_s2 <= 0 or self.normal_decel_m_s2 <= 0
                or self.tau_s != 1 or self.action_step_s != 1
                or self.population not in ("storage","ingress")):
            raise ValueError("unknown state/type/dynamics: fail closed")
        if self.population == "ingress" and self.position_m > 0:
            raise ValueError("uncovered ingress coordinate")


def normal_red_envelope_m(vehicle, margin_m=1.1):
    vehicle.validate()
    if vehicle.speed_m_s == 0:
        return 0.0
    return margin_m+vehicle.speed_m_s+vehicle.speed_m_s**2/(2*vehicle.normal_decel_m_s2)


def red_transition_witness(vehicles, storage_length_m=204.49):
    """Called BEFORE a step whose pending native transition enters red.

    No exemption for a nominal front or nominal n. Vehicles already on the
    internal receiving lane remain governed by native CF; all remaining
    storage/covered ingress must fit reaction plus comfortable-stop envelope.
    """
    if not math.isfinite(storage_length_m) or storage_length_m <= 0:
        raise ValueError("unknown stopline geometry")
    seen=set();rows=[]
    for v in vehicles:
        v.validate()
        if v.vehicle_id in seen or v.position_m > storage_length_m:
            raise ValueError("duplicate/out-of-range safety identity")
        seen.add(v.vehicle_id)
        gap=storage_length_m-v.position_m
        required=normal_red_envelope_m(v)
        rows.append({"vehicle_id":v.vehicle_id,"population":v.population,
                     "gap_m":gap,"required_normal_red_m":required,
                     "margin_m":gap-required,"safe":gap+1e-9>=required})
    unsafe=[r["vehicle_id"] for r in rows if not r["safe"]]
    return {"safe":not unsafe,"unsafe_ids":unsafe,"witnesses":rows,
            "invariant":"one reaction step plus normal braking for EVERY positive speed; only exactly zero speed is exempt under unchanged native red compliance; all remaining storage/ingress"}


def assert_ingress_and_crossing_coverage(max_type_speed_m_s, accel_m_s2,
                                       upstream_length_m=113.08, internal_length_m=81.98):
    vals=(max_type_speed_m_s,accel_m_s2,upstream_length_m,internal_length_m)
    if not all(math.isfinite(v) and v>0 for v in vals):
        raise ValueError("unknown advance geometry")
    advance=max_type_speed_m_s+accel_m_s2
    if advance >= min(upstream_length_m,internal_length_m):
        raise ValueError("STOP: unseen ingress/crossing omission possible")
    return {"maximum_one_step_advance_m":advance,
            "upstream_length_m":upstream_length_m,"internal_length_m":internal_length_m,
            "unseen_ingress_cannot_reach_storage_in_one_step":True,
            "new_crossing_cannot_skip_internal_lane_in_one_step":True}

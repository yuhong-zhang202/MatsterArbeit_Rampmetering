"""Read-only, offline audit of the bound Candidate A A07 safety witness.

This checks recorded data and an algebraic sensitivity. It does not run SUMO,
evaluate native red behaviour, or authorize a different safety contract.
"""

from __future__ import annotations

import csv
import hashlib
import json
import math
import argparse
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
RAW = ROOT / "data/raw/candidate_a_qualification_20261008_v1/CA_FIXED_R300_S17_A07"
PUBLIC = ROOT / "artifacts/candidate_a_qualification_20261008_v1/pr_review/CA_FIXED_R300_S17_A07/outputs"
PUBLIC_RECEIPT = PUBLIC.parent / "guardian_receipt.json"
GATE = ROOT / "data/processed/candidate_a_qualification_20261008_v1/R300_A07_ACTUAL_DATA_GATE_V3.json"
WINDOW_CSV = ROOT / "results/tables/candidate_a_qualification_20261008_v1/R300_A07_SERVICE_WINDOWS_V3.csv"
PHASE_THIN = ROOT / "results/tables/candidate_a_qualification_20261008_v1/R300_A07_PHASE_LEDGER_THIN_V3.csv"
BINDINGS = ROOT / "data/processed/candidate_a_qualification_20261008_v1/R300_A07_FINAL_DERIVED_BINDINGS_V3.json"
SNAPSHOT_SHA256 = "0cb77aa1549d500628fa136742d5119d0cdbdd94c5e23f357090b44c6ccc984d"
WINDOW_FIELDS = (
    "C_observed", "C_applied_observed", "E_observed", "N_observed",
    "command_latency", "quantization", "physical_shortfall", "tracking_error",
)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def required_gap(speed: float, step: float, decel: float, clearance: float = 1.1) -> float:
    """Replay only the recorded custom guard expression, including its zero rule."""
    if speed < 0 or step <= 0 or decel <= 0:
        raise ValueError("invalid recorded dynamics")
    if speed == 0:
        return 0.0
    return clearance + speed * step + speed * speed / (2 * decel)


def validate_windows(windows: list[dict], csv_rows: list[dict]) -> list[int]:
    """Preserve partial observations, measured zero, and no observation."""
    if len(windows) != 6 or len(csv_rows) != 6:
        raise ValueError("expected exactly six declared service windows")
    observed = []
    for index, (window, row) in enumerate(zip(windows, csv_rows)):
        steps = window["observed_steps"]
        if int(row["observed_steps"]) != steps or steps < 0 or steps > 300:
            raise ValueError(f"observed step mismatch in window {index}")
        if window["full_window"] or window["tracking_error"] is not None:
            raise ValueError(f"unexpected full-window qualification in window {index}")
        if row["status"] != window["status"] or row["status"] != "NOT_TESTED_INCOMPLETE_WINDOW":
            raise ValueError(f"status mismatch in window {index}")
        for field in WINDOW_FIELDS:
            value, csv_value = window[field], row[field]
            if steps == 0 and value is not None:
                raise ValueError(f"unobserved measurement is not null: {index} {field}")
            if value is None:
                if csv_value != "":
                    raise ValueError(f"null must serialize blank: {index} {field}")
            elif csv_value == "" or not math.isclose(float(csv_value), float(value), rel_tol=0, abs_tol=1e-12):
                raise ValueError(f"measured value mismatch: {index} {field}")
        observed.append(steps)
    return observed


def audit(*, verify_local_raw: bool = False) -> dict:
    """Audit committed evidence; optionally verify local raw against its guardian.

    The thin phase ledger is a committed derivative, not a byte-identical copy
    of the ignored raw phase_steps.csv. Its source-level reconstruction remains
    outside the public-only audit.
    """
    guardian = json.loads(PUBLIC_RECEIPT.read_text())
    for name in ("failure_snapshot.json", "cycles.csv", "crossings.csv"):
        if sha256(PUBLIC / name) != guardian["files_sha256"][name]:
            raise ValueError(f"public guardian hash mismatch: {name}")
    if sha256(PUBLIC / "failure_snapshot.json") != SNAPSHOT_SHA256:
        raise ValueError("bound public snapshot hash mismatch")

    bindings = json.loads(BINDINGS.read_text())["files_sha256"]
    for path in (GATE, WINDOW_CSV, PHASE_THIN):
        relative = path.relative_to(ROOT).as_posix()
        if sha256(path) != bindings[relative]:
            raise ValueError(f"V3 binding mismatch: {relative}")

    if verify_local_raw:
        output = RAW / "outputs"
        if sha256(RAW / "guardian_receipt.json") != sha256(PUBLIC_RECEIPT):
            raise ValueError("public/local guardian receipt drift")
        raw_guardian = json.loads((RAW / "guardian_receipt.json").read_text())
        for name in ("failure_snapshot.json", "phase_steps.csv", "cycles.csv", "crossings.csv"):
            if sha256(output / name) != raw_guardian["files_sha256"][name]:
                raise ValueError(f"local guardian hash mismatch: {name}")
        if sha256(output / "failure_snapshot.json") != SNAPSHOT_SHA256:
            raise ValueError("bound local raw snapshot hash mismatch")
        for name in ("failure_snapshot.json", "cycles.csv", "crossings.csv"):
            if sha256(output / name) != sha256(PUBLIC / name):
                raise ValueError(f"public/local byte drift: {name}")
        with (output / "phase_steps.csv").open(newline="") as stream:
            raw_phases = list(csv.DictReader(stream))
        with PHASE_THIN.open(newline="") as stream:
            thin_phases = list(csv.DictReader(stream))
        if len(raw_phases) != len(thin_phases) or any(
            any(raw_row.get(key) != value for key, value in thin_row.items())
            for raw_row, thin_row in zip(raw_phases, thin_phases)
        ):
            raise ValueError("committed thin phase fields drift from local raw")

    failure = json.loads((PUBLIC / "failure_snapshot.json").read_text())
    snapshot = failure["snapshot"]
    if not (
        failure["status"] == "ABORTED_SAFETY_BEFORE_RED"
        and failure["decision_time_s"] == 1206
        and failure["last_completed_step_s"] == failure["last_accounted_s"] == snapshot["time_s"] == 1206
        and snapshot["phase_before"] == 1
        and snapshot["state_before"] == "y"
        and snapshot["next_switch"] == 1206.0
        and snapshot["predicted_motion"] == "r"
    ):
        raise ValueError("A07 pre-red event identity drift")

    states = snapshot["vehicle_states"]
    witnesses = snapshot["red_transition"]["witnesses"]
    by_id = {state["vehicle_id"]: state for state in states}
    if len(states) != len(witnesses) or len(by_id) != 42 or {w["vehicle_id"] for w in witnesses} != set(by_id):
        raise ValueError("guard witness/state identity mismatch")
    counts = Counter(state["population"] for state in states)
    if counts != Counter(storage=27, ingress=15):
        raise ValueError("guard population mismatch")
    unsafe = []
    for witness in witnesses:
        state = by_id[witness["vehicle_id"]]
        expected = required_gap(state["speed_m_s"], state["action_step_s"], state["normal_decel_m_s2"])
        if not math.isclose(expected, witness["required_normal_red_m"], rel_tol=0, abs_tol=1e-10):
            raise ValueError(f"required-gap mismatch: {witness['vehicle_id']}")
        if not math.isclose(witness["gap_m"] - expected, witness["margin_m"], rel_tol=0, abs_tol=1e-10):
            raise ValueError(f"margin mismatch: {witness['vehicle_id']}")
        if witness["safe"] is False:
            unsafe.append(witness["vehicle_id"])
    if unsafe != snapshot["red_transition"]["unsafe_ids"] or unsafe != ["R_flow.1"]:
        raise ValueError("unsafe witness mismatch")
    front = by_id["R_flow.1"]
    front_witness = next(w for w in witnesses if w["vehicle_id"] == "R_flow.1")
    gap = 204.49 - front["position_m"]
    if not math.isclose(gap, front_witness["gap_m"], rel_tol=0, abs_tol=1e-12):
        raise ValueError("stopline gap mismatch")
    sensitivity = required_gap(front["speed_m_s"], front["action_step_s"], front["normal_decel_m_s2"], 1.0)
    if not sensitivity > gap:
        raise ValueError("one-constant algebra sensitivity unexpectedly passes")

    with PHASE_THIN.open(newline="") as stream:
        phases = list(csv.DictReader(stream))
    with (PUBLIC / "crossings.csv").open(newline="") as stream:
        crossings = list(csv.DictReader(stream))
    with (PUBLIC / "cycles.csv").open(newline="") as stream:
        cycles = list(csv.DictReader(stream))
    if len(phases) != 1206 or phases[-1]["time_end_s"] != "1206" or phases[-1]["state_after"] != "y":
        raise ValueError("committed thin phase prefix mismatch")
    if any(int(row["time_begin_s"]) != i or int(row["time_end_s"]) != i + 1 for i, row in enumerate(phases)):
        raise ValueError("committed thin phase prefix has missing or duplicate steps")
    if len(crossings) != 1 or crossings[0]["vehicle_id"] != "R_flow.0" or crossings[0]["motion_signal_state"] != "G":
        raise ValueError("crossing prefix mismatch")
    if len(cycles) != 1 or cycles[0]["completed"] != "False":
        raise ValueError("cycle completeness mismatch")

    gate = json.loads(GATE.read_text())
    with WINDOW_CSV.open(newline="") as stream:
        rows = list(csv.DictReader(stream))
    observed = validate_windows(gate["service_windows"], rows)
    if observed != [6, 0, 0, 0, 0, 0]:
        raise ValueError("service-window exposure mismatch")
    if gate["cycles_completed"] != 0 or gate["effective_qualifications"] != 0 or gate["highest_safe_qualified_rate_veh_h"] is not None:
        raise ValueError("qualification boundary mismatch")
    if gate["other_fixed_rates"] != "NOT_RUN_HELD" or gate["phaseC"] != "NOT_PREPARED_HELD":
        raise ValueError("held scenarios misclassified")
    return {
        "classification": "OFFLINE_COMMITTED_EVIDENCE_AUDIT_ONLY",
        "status": "PASS",
        "public_evidence_only": not verify_local_raw,
        "local_raw_verified": verify_local_raw,
        "thin_phase_fields_reconciled_to_local_raw": verify_local_raw,
        "phase_thin_sha256": sha256(PHASE_THIN),
        "public_guardian_sha256": sha256(PUBLIC_RECEIPT),
        "snapshot_sha256": SNAPSHOT_SHA256,
        "gate_sha256": sha256(GATE),
        "service_csv_sha256": sha256(WINDOW_CSV),
        "last_completed_s": 1206,
        "guard_witnesses": len(witnesses),
        "population_counts": dict(counts),
        "unsafe_ids": unsafe,
        "front_gap_m": gap,
        "current_required_m": front_witness["required_normal_red_m"],
        "current_margin_m": front_witness["margin_m"],
        "constant_1m_only_required_m": sensitivity,
        "constant_1m_only_margin_m": gap - sensitivity,
        "service_observed_steps": observed,
        "complete_cycles": 0,
        "effective_qualifications": 0,
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--verify-local-raw", action="store_true", help="Add guardian/hash checks of ignored local raw files; unavailable in a clean checkout")
    args = parser.parse_args()
    print(json.dumps(audit(verify_local_raw=args.verify_local_raw), indent=2, sort_keys=True))

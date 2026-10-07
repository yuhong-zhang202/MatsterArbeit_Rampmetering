"""Read-only runtime-log replay; never imports TraCI or launches SUMO."""
import collections
import csv
import hashlib
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "scripts/formal_development_20261007_v1"))
from control import PulseScheduler

raw = ROOT / "data/raw/formal_development_20261007_v1/DEV_M3600_R900_S17_T2_A02/outputs/controller_steps.csv"
rows = list(csv.DictReader(raw.open()))
pulse = PulseScheduler()
mismatches = []
for row in rows[600:]:
    result = pulse.step(int(row["time_begin_s"]), float(row["command_rate_veh_h"]), row["guard_allowed"] == "True")
    for key, value in result.items():
        if isinstance(value, bool):
            equal = row[key] == str(value)
        elif isinstance(value, (float, int)):
            equal = abs(float(row[key]) - value) < 1e-8
        else:
            equal = row[key] == value
        if not equal:
            mismatches.append([row["time_begin_s"], key, value, row[key]])
windows = []
leaders = collections.defaultdict(collections.Counter)
for begin in range(1200, 3000, 300):
    window = rows[begin:begin + 300]
    before = float(window[0]["credit_before"])
    after = float(window[-1]["credit_after"])
    dropped = float(window[-1]["dropped_credit_total"]) - float(rows[begin - 1]["dropped_credit_total"])
    command = sum(float(row["command_rate_veh_h"]) / 3600 for row in window)
    green = sum(row["slot_scheduled"] == "True" for row in window)
    actual = sum(len(json.loads(row["crossing_bracket_ids_json"])) for row in window)
    by_reason = collections.Counter()
    for row in window:
        time = int(row["time_begin_s"])
        increment = float(row["dropped_credit_total"]) - float(rows[time - 1]["dropped_credit_total"])
        if increment > 1e-10:
            by_reason[row["guard_reason"]] += increment
        if row["guard_reason"] in ("LEADER_SECURE_GAP", "INTERNAL_RECEIVER_CLEARANCE"):
            evidence = json.loads(row["guard_decision_json"])["input_evidence"]
            leaders[row["guard_reason"]][evidence["leader"]["lane_id"] if evidence["leader"] else "NONE"] += 1
    windows.append(dict(begin=begin, end=begin+300, command_credit=command,
                        credit_before=before, credit_after=after, dropped_credit=dropped,
                        green_slots=green, actual_crossings=actual,
                        accounting_residual=before+command-green-dropped-after,
                        drop_observed_by_reason_not_causal=dict(by_reason)))
result = dict(status="PASS_ACCOUNTING_NO_PARAMETER_CHANGE", raw_sha256=hashlib.sha256(raw.read_bytes()).hexdigest(),
              pulse_replay_mismatches=mismatches, windows=windows,
              due_denial_leader_lanes={key:dict(value) for key,value in leaders.items()},
              scope="Recorded guard inputs replay, not traffic counterfactual or causal denial allocation; no simulation.")
assert not mismatches
assert all(abs(window["accounting_residual"]) < 1e-8 and window["green_slots"] == window["actual_crossings"] for window in windows)
destination = Path(__file__).with_name("RATE_SHORTFALL_DIAGNOSIS.json")
with destination.open("x") as stream:
    json.dump(result, stream, indent=2)
    stream.write("\n")
print(json.dumps({"status": result["status"], "output": str(destination), "simulation_starts":0}))

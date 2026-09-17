"""Bounded, offline Stage 2 G1 diagnostic. Never launches a simulator.

The retained complete high trajectory is the supported scope. Flow schedules
are deliberately not expanded; prior audited cohort accounts remain attributed.
"""
from __future__ import annotations

import argparse
from collections import Counter
import csv
import hashlib
import json
import math
from pathlib import Path
import shlex
import sys
import xml.etree.ElementTree as ET

PROJECT = Path(__file__).resolve().parents[2]
EVIDENCE = PROJECT / "data/processed/stage2_evidence_package_20260909/evidence.json"
PAIRED = PROJECT / "data/processed/stage2_internal_accounting_20260909/paired_semantic_comparison_v3.json"
ACCOUNTING = PROJECT / "data/processed/stage2_internal_accounting_20260909/paired_accounting_v2.json"
ENGINEERING_REVIEW = PROJECT / "docs/STAGE2_G1_V2_ENGINEERING_REVIEW.md"
WINDOWS = {"A": (0, 1500), "B": (300, 1500), "post_demand": (1500, 2700)}
CLASSES = ("M", "R", "U", "X")
LANES = ("main_up_0", "main_up_1", "main_down_0", "main_down_1",
         ":freeway_merge_1_0", ":freeway_merge_1_1", ":freeway_merge_0_0")
RAMP_BEFORE = {"ramp_accel_0", ":freeway_merge_0_0"}


def digest(path):
    h = hashlib.sha256()
    with Path(path).open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def verify_hashes(hashes):
    changed = [p for p, old in hashes.items() if not Path(p).is_file() or digest(p) != old]
    if changed:
        raise ValueError(f"Source changed during analysis: {changed}")


def reserve_directories(paths):
    paths = [Path(p).resolve() for p in paths]
    if len(set(paths)) != len(paths):
        raise ValueError("Output directories must be distinct")
    for a in paths:
        if a.exists() or any(a in b.parents or b in a.parents for b in paths if a != b):
            raise FileExistsError(f"Refusing existing or nested output directory: {a}")
    for path in paths:
        path.mkdir(parents=True, exist_ok=False)


def number(value):
    result = float(value)
    if not math.isfinite(result):
        raise ValueError("Non-finite numeric field")
    return result


def e1_row(attrs, detector, lane):
    required = ("id", "begin", "end", "flow", "speed", "occupancy", "nVehContrib", "nVehEntered")
    if any(k not in attrs for k in required):
        raise ValueError(f"Missing E1 field: {attrs}")
    if attrs["id"] != detector:
        raise ValueError("E1 detector identity mismatch")
    row = {"detector_id": detector, "lane_id": lane}
    for key, out in (("begin", "begin_s"), ("end", "end_s"), ("flow", "flow_vehph"),
                     ("speed", "speed_raw_mps"), ("occupancy", "occupancy_pct"),
                     ("nVehContrib", "nVehContrib"), ("nVehEntered", "nVehEntered")):
        row[out] = number(attrs[key])
    for key in ("nVehContrib", "nVehEntered"):
        if row[key] < 0 or not row[key].is_integer():
            raise ValueError("Invalid E1 vehicle count")
        row[key] = int(row[key])
    # A numeric passage measurement, not a validated traffic-state estimate.
    row["speed_valid"] = row["nVehContrib"] > 0 and row["speed_raw_mps"] >= 0
    row["missing_reason"] = ("no_vehicle_contributions" if row["nVehContrib"] == 0 else
                             "negative_speed_with_contributions" if not row["speed_valid"] else "")
    return row


def measurement_notes(rows):
    """Attach reviewed cases only when their exact source record is present.

    These are source-specific annotations, never an automatic congestion rule.
    """
    cases = [
        ("merge_upstream_e1_l1", 450, 480, 12.60, 8, 8, "insertion_overlaps_detector", "Direct insertion near the upstream detector; raw E1 speed is not upstream traffic speed."),
        ("merge_upstream_e1_l1", 1500, 1530, 4.43, 1, 0, "insertion_and_interval_settlement", "M_flow.1332 inserted beyond the detector at 1499; contribution settles in the next interval, not evidence of post-demand slow traffic."),
        ("merge_downstream_e1_l1", 1980, 2010, 4.91, 1, 1, "lane_change_near_detector", "R_flow.200 changes lane near the detector; the isolated passage-speed contribution does not establish lane congestion."),
    ]
    flags = []
    for detector, begin, end, speed, contrib, entered, code, explanation in cases:
        matched = [r for r in rows if (r["detector_id"], r["begin_s"], r["end_s"], r["speed_raw_mps"], r["nVehContrib"], r["nVehEntered"]) == (detector, begin, end, speed, contrib, entered)]
        if matched:
            flags.append({"detector_id": detector, "begin_s": begin, "end_s": end,
                          "flag": code, "explanation": explanation, "scope": "reviewed retained source only",
                          "engineering_evidence": str(ENGINEERING_REVIEW)})
    return {"speed_valid_definition": "nVehContrib > 0 and nonnegative raw E1 passage speed; not traffic-state validity",
            "upstream_coverage_limitation": "Upstream E1 overlaps the route origin / departPos=last insertion positions. Raw flow, speed and occupancy are detector observations, not conventional upstream traffic-state estimates.",
            "specific_reviewed_cases": flags,
            "no_generalization": "No automatic low-contribution exclusion, congestion classifier, E1 defect claim or substitution with FCD speeds."}


def check_intervals(rows, begin=0, end=2700, period=30):
    expected = begin
    for row in rows:
        if row["begin_s"] != expected or row["end_s"] != expected + period:
            raise ValueError("E1 intervals duplicated, missing, unordered or wrong period")
        expected += period
    if expected != end:
        raise ValueError("E1 coverage does not reach the required endpoint")


def summarize_e1(rows, begin, end):
    selected = [r for r in rows if begin <= r["begin_s"] and r["end_s"] <= end]
    duration = sum(r["end_s"] - r["begin_s"] for r in selected)
    valid = [r for r in selected if r["speed_valid"]]
    weight = sum(r["nVehContrib"] for r in valid)
    return {"begin_s": begin, "end_s": end, "covered_seconds": duration,
            "nVehContrib": sum(r["nVehContrib"] for r in selected),
            "speed_contribution_denominator": weight,
            "speed_mps": sum(r["speed_raw_mps"] * r["nVehContrib"] for r in valid) / weight if weight else None,
            "flow_vehph": sum(r["flow_vehph"] * (r["end_s"] - r["begin_s"]) for r in selected) / duration if duration else None,
            "occupancy_pct": sum(r["occupancy_pct"] * (r["end_s"] - r["begin_s"]) for r in selected) / duration if duration else None,
            "missing_speed_intervals": len(selected) - len(valid)}


def event_before(event_time, t):
    return event_time is not None and event_time >= 0 and event_time < t


def vehicle_status(record, *, explicitly_unentered=False):
    if record is None:
        return "not_entered" if explicitly_unentered else "record_missing_unknown"
    if record["depart"] < 0:
        return "record_missing_unknown"
    return "arrived" if record["arrival"] >= 0 else "entered_unfinished"


def crossing_event(vid, previous, current):
    t, lane = current
    base = {"vehicle_id": vid, "previous_time_s": None, "previous_lane": None,
            "first_downstream_time_s": t, "first_downstream_lane": lane,
            "interval_semantics": "(previous_raw_label,first_downstream_raw_label]",
            "time_precision": "sample_bracket_not_exact_crossing_time",
            "boundary_30s_ambiguous": None, "status": "unresolved"}
    if previous is None:
        base["reason"] = "first_seen_downstream"
        return base
    prev_t, prev_lane = previous
    base.update(previous_time_s=prev_t, previous_lane=prev_lane)
    if t - prev_t != 1:
        base["reason"] = "non_unit_sample_gap"
    elif prev_lane not in RAMP_BEFORE:
        base["reason"] = "previous_lane_not_ramp_path"
    else:
        base.update(status="bracketed", reason="", boundary_30s_ambiguous=math.floor(prev_t / 30) != math.floor(t / 30))
    return base


def json_write(path, value):
    with Path(path).open("x") as f:
        json.dump(value, f, indent=2, allow_nan=False)
        f.write("\n")


def csv_write(path, rows):
    if not rows:
        raise ValueError(f"Refusing empty evidence table: {path}")
    with Path(path).open("x", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def parse_fcd(path, ramp_ids):
    timeline, times, events, previous = [], [], {}, {}
    all_ids, anomalies = set(), []
    for _, step in ET.iterparse(path, events=("end",)):
        if step.tag != "timestep":
            continue
        t = number(step.attrib["time"])
        if times and t <= times[-1]:
            raise ValueError("FCD timestamps not strictly increasing")
        times.append(t)
        seen, count, stopped = set(), Counter(), Counter()
        for node in step.findall("vehicle"):
            vid, lane, speed = node.attrib["id"], node.attrib["lane"], number(node.attrib["speed"])
            if vid in seen:
                raise ValueError(f"Duplicate FCD vehicle/time: {vid}/{t}")
            seen.add(vid)
            all_ids.add(vid)
            category = vid.split("_", 1)[0]
            if category not in CLASSES:
                raise ValueError(f"Unknown vehicle class: {vid}")
            if lane in LANES:
                if category not in ("M", "R"):
                    raise ValueError("Unexpected vehicle class on monitored freeway lane")
                count[lane, category] += 1
                stopped[lane, category] += int(speed <= 0.1)
            if vid in ramp_ids:
                if lane.startswith("main_down_") and vid not in events:
                    events[vid] = crossing_event(vid, previous.get(vid), (t, lane))
                previous[vid] = (t, lane)
        for lane in LANES:
            for category in ("M", "R"):
                timeline.append({"time_s": t, "lane_id": lane,
                                 "lane_role": "ramp_connection" if lane == ":freeway_merge_0_0" else "mainline",
                                 "vehicle_class": category, "observation_available": True,
                                 "vehicle_samples": count[lane, category], "stopped_samples": stopped[lane, category]})
        step.clear()
    missing = sorted(set(range(2700)) - set(times))
    if set(times) - set(range(2700)):
        raise ValueError("Unexpected FCD time labels outside 0..2699")
    # Missing samples, including the explicit unsampled endpoint, are never zeros.
    for t in missing + [2700]:
        for lane in LANES:
            for category in ("M", "R"):
                timeline.append({"time_s": t, "lane_id": lane,
                                 "lane_role": "ramp_connection" if lane == ":freeway_merge_0_0" else "mainline",
                                 "vehicle_class": category, "observation_available": False,
                                 "vehicle_samples": None, "stopped_samples": None})
    timeline.sort(key=lambda r: (r["time_s"], r["lane_id"], r["vehicle_class"]))
    for vid in sorted(ramp_ids - set(events)):
        events[vid] = {"vehicle_id": vid, "previous_time_s": None, "previous_lane": None,
                       "first_downstream_time_s": None, "first_downstream_lane": None,
                       "interval_semantics": "(previous_raw_label,first_downstream_raw_label]",
                       "time_precision": "unresolved", "boundary_30s_ambiguous": None,
                       "status": "unresolved", "reason": "no_downstream_observation"}
    return timeline, list(events.values()), {"observed_timestep_count": len(times), "missing_times_before_end": missing,
                                            "endpoint_2700_observed": False, "unique_fcd_ids": len(all_ids),
                                            "fcd_ids": all_ids, "anomalies": anomalies}


def plot_tables(table_dir, figure_dir):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    with (table_dir / "e1_native.csv").open() as f:
        rows = list(csv.DictReader(f))
    fig, axes = plt.subplots(3, 1, figsize=(12, 9), sharex=True)
    for detector in sorted({r["detector_id"] for r in rows}):
        selected = [r for r in rows if r["detector_id"] == detector]
        x = [float(r["begin_s"]) for r in selected]
        label = selected[0]["lane_id"]
        for ax, field in zip(axes, ("flow_vehph", "speed_raw_mps", "occupancy_pct")):
            y = [float(r[field]) if field != "speed_raw_mps" or r["speed_valid"] == "True" else math.nan for r in selected]
            # Post steps retain the interval's begin/end convention; no interpolation.
            ax.step(x + [float(selected[-1]["end_s"])] , y + [y[-1]], where="post", label=label, linewidth=1)
    for ax, label in zip(axes, ("Flow (veh/h)", "Speed (m/s)", "Occupancy (%)")):
        ax.set_ylabel(label)
        ax.axvline(1500, color="black", linestyle="--", linewidth=1)
        ax.axvspan(1500, 2700, color="gray", alpha=.10)
        ax.grid(alpha=.2)
        ax.set_xlim(0, 2700)
    axes[0].legend(ncol=4, loc="upper right")
    axes[-1].set_xlabel("SUMO time (s); native 30 s intervals, shaded: post-demand observation")
    fig.suptitle("Exploratory high demand, seed 17: raw E1 passage measurements\nUpstream E1 overlaps departPos=last insertion; isolated speed dips do not establish congestion", fontsize=12)
    fig.text(.5, .012, "Raw values retained. No-contribution speeds are missing. speed_valid is numeric availability, not traffic-state validity.", ha="center", fontsize=9)
    fig.tight_layout(rect=(0, .035, 1, .93))
    fig.savefig(figure_dir / "mainline_timeline.png", dpi=160)
    plt.close(fig)


def build(args):
    runtime = args.runtime_dir.resolve()
    output, tables, figures = args.output_dir.resolve(), args.table_dir.resolve(), args.figure_dir.resolve()
    summary_path = runtime / "summary.json"
    summary = json.loads(summary_path.read_text())
    command = summary["sumo_command"]
    def option(flag):
        return Path(command[command.index(flag) + 1]).resolve()
    config = option("-c")
    config_xml = ET.parse(config).getroot()
    def input_path(tag):
        return (config.parent / config_xml.find(f"input/{tag}").attrib["value"]).resolve()
    net, demand, additional = input_path("net-file"), input_path("route-files"), input_path("additional-files")
    source_files = [summary_path, config, net, demand, additional, EVIDENCE, PAIRED, ACCOUNTING, ENGINEERING_REVIEW]
    outputs = {name: option(flag) for name, flag in {
        "fcd": "--fcd-output", "tripinfo": "--tripinfo-output", "vehroute": "--vehroute-output",
        "sumo_summary": "--summary-output", "log": "--log", "error_log": "--error-log"}.items()}
    source_files.extend(outputs.values())
    add = ET.parse(additional).getroot()
    tls = Path(add.find("timedEvent").attrib["dest"]).resolve()
    source_files.append(tls)
    detectors = list(add.findall("inductionLoop"))
    if len(detectors) != 4:
        raise ValueError("Expected four E1 detectors")
    detector_files = [(d, (additional.parent / d.attrib["file"]).resolve()) for d in detectors]
    source_files.extend(p for _, p in detector_files)
    for p in [net, demand, additional, config, *outputs.values(), tls, *(p for _, p in detector_files)]:
        if runtime not in p.parents:
            raise ValueError(f"Runtime source escapes the selected run: {p}")
    hashes = {str(p): digest(p) for p in source_files}
    if summary["simulation"]["seed"] != 17 or float(command[command.index("--end") + 1]) != 2700:
        raise ValueError("Unsupported source identity")
    reserve_directories([output, tables, figures])
    ledger = {"authorization": "User approved docs/STAGE2_G1_EXECUTION_PLAN_V2.md D0-D7, 2026-09-09; parent delegated D2-D5; zero simulator starts",
              "new_simulator_starts": 0, "steps": {}}
    for step in range(8):
        ledger["steps"][f"D{step}"] = {"status": "completed" if step < 2 else "running" if step == 2 else "pending",
            "owner": "primary" if step in (0, 7) else "simulation_engineer" if step == 1 else "scientific_reviewer" if step == 6 else "data_analyst",
            "inputs": [str(runtime)], "outputs": [], "command": None, "verification": [], "issues": [], "resume_point": f"D{step}"}
    ledger["steps"]["D1"]["verification"] = ["Parent-supplied engineer: version 1.26, seed 17, demand end 1500, max end 2700; four E1; R via :freeway_merge_0_0 12.60 m; no exitTimes; zero warnings/collisions/teleports"]
    json_write(output / "execution_ledger.json", ledger)
    e1, summaries = [], {}
    for detector, path in detector_files:
        records = [e1_row(node.attrib, detector.attrib["id"], detector.attrib["lane"]) for node in ET.parse(path).getroot().findall("interval")]
        check_intervals(records)
        e1.extend(records)
        summaries[detector.attrib["id"]] = {name: summarize_e1(records, *bounds) for name, bounds in WINDOWS.items()}
    trips = {}
    for node in ET.parse(outputs["tripinfo"]).getroot().findall("tripinfo"):
        vid = node.attrib["id"]
        if vid in trips:
            raise ValueError("Duplicate tripinfo ID")
        trips[vid] = {k: number(node.attrib[k]) for k in ("depart", "arrival", "departDelay", "duration")}
    routes = {}
    for node in ET.parse(outputs["vehroute"]).getroot().findall("vehicle"):
        vid = node.attrib["id"]
        if vid in routes:
            raise ValueError("Duplicate vehroute ID")
        routes[vid] = node.find("route").attrib["edges"].split()
    if set(routes) != set(trips):
        raise ValueError("Trip/vehroute ID mismatch")
    ramp_ids = {vid for vid in trips if vid.startswith("R_flow.")}
    if any(routes[v][-2:] != ["ramp_accel", "main_down"] for v in ramp_ids):
        raise ValueError("R route does not reach the declared merge boundary")
    timeline, events, fcd_check = parse_fcd(outputs["fcd"], ramp_ids)
    if fcd_check.pop("fcd_ids") != set(trips):
        raise ValueError("FCD/tripinfo ID mismatch; bounded complete-run scope not met")
    audited = json.loads(EVIDENCE.read_text())
    cohort = []
    max_account_difference = 0
    for old in audited["timeline"]:
        t = old["time_s"]
        for category in CLASSES:
            selected = [v for k, v in trips.items() if k.startswith(category + "_flow.")]
            row = {"time_s": t, "vehicle_class": category, "semantics": "before_step_event_time_strictly_less_than_t",
                   "source": str(EVIDENCE), "source_role": "reused_previous_high_audit_with_paired_equivalence",
                   "schedule_status": "schedule_unverified_for_general_flow_expansion"}
            for field in ("planned", "entered", "arrived", "waiting_outside", "in_network"):
                row[field] = old[f"{category}_{field}_before_step"]
            actual_entered = sum(event_before(v["depart"], t) for v in selected)
            actual_arrived = sum(event_before(v["arrival"], t) for v in selected)
            max_account_difference = max(max_account_difference, abs(actual_entered - row["entered"]), abs(actual_arrived - row["arrived"]))
            if row["planned"] != row["waiting_outside"] + row["in_network"] + row["arrived"]:
                raise ValueError("Referenced cohort account does not conserve vehicles")
            cohort.append(row)
    if max_account_difference:
        raise ValueError("Retained trip times do not match the reused audit")
    planned = {node.attrib["id"].split("_")[0]: int(node.attrib["number"]) for node in ET.parse(demand).getroot().findall("flow")}
    actual_counts = dict(Counter(k.split("_")[0] for k in trips))
    statuses = dict(Counter(vehicle_status(r) for r in trips.values()))
    if actual_counts != planned or statuses != {"arrived": sum(planned.values())}:
        raise ValueError("Source is not the expected fully completed cohort; no schedule inference permitted")
    merge_status = "time_uncertain" if all(e["status"] == "bracketed" for e in events) and not fcd_check["missing_times_before_end"] else "not_measured"
    diagnostic = {"classification": "exploratory", "source_run": str(runtime), "source_windows": summary["time_windows"],
        "analysis_windows": WINDOWS, "schedule_status": "schedule_unverified_for_general_flow_expansion",
        "cohort_source": str(EVIDENCE), "paired_equivalence_source": str(PAIRED), "planned_counts_from_flow": planned,
        "trip_class_counts": actual_counts, "vehicle_status_counts": statuses, "referenced_account_max_difference": max_account_difference,
        "last_actual_departure_s": max(v["depart"] for v in trips.values()), "last_arrival_s": max(v["arrival"] for v in trips.values()),
        "post_demand_departures_by_class": {c: sum(v["depart"] >= 1500 for k, v in trips.items() if k.startswith(c + "_flow.")) for c in CLASSES},
        "completed_trip_reconstructed_schedule_check": {"method": "depart - departDelay for observed completed trips only; not a general flow schedule", "min_s": min(v["depart"]-v["departDelay"] for v in trips.values()), "max_s": max(v["depart"]-v["departDelay"] for v in trips.values())},
        "e1_summaries": summaries, "e1_measurement_interpretation": measurement_notes(e1), "e1_interval_count": len(e1), "e1_invalid_with_contributions": [r for r in e1 if r["missing_reason"] == "negative_speed_with_contributions"],
        "fcd_coverage": fcd_check, "mainline_stopped_samples": sum(r["stopped_samples"] or 0 for r in timeline if r["lane_role"] == "mainline"),
        "stopped_by_lane_class": {f"{lane}/{c}": sum(r["stopped_samples"] or 0 for r in timeline if r["lane_id"] == lane and r["vehicle_class"] == c) for lane in LANES for c in ("M", "R")},
        "merge": {"status": merge_status, "spatial_boundary": "entry to main_down_0 after ramp internal connector; first downstream sample can be either downstream lane",
                  "R_route_ids": len(ramp_ids), "event_status_counts": dict(Counter(e["status"] for e in events)),
                  "bin_boundary_ambiguous_events": sum(e["boundary_30s_ambiguous"] is True for e in events),
                  "event_time_semantics": "(previous raw FCD label,first downstream raw FCD label]; not exact physical crossing times",
                  "unresolved": [e for e in events if e["status"] != "bracketed"]},
        "referenced_events": audited["events"], "formal_breakdown": "not_evaluated", "capacity_drop": "not_evaluated", "sweet_spot": "not_evaluated",
        "limitations": ["One retained trajectory, seed 17; repeated seconds are not replications.", "No new speed/duration threshold or automatic scientific classifier.", "No-vehicle E1 speeds are missing; sampled stopping is not queue length or causal delay.", "Flow expansion is unverified: existing audited accounts are cited, not generalized to unfinished runs.", "No comparison of upstream/downstream simultaneous differences as ramp flow.", "No formal duration sufficiency, steady-state or capacity conclusion."]}
    csv_write(tables / "e1_native.csv", e1)
    csv_write(tables / "mainline_lane_timeline.csv", timeline)
    csv_write(tables / "cohort_accounts.csv", cohort)
    if merge_status == "time_uncertain":
        csv_write(tables / "merge_events.csv", sorted(events, key=lambda e: e["first_downstream_time_s"]))
    json_write(output / "diagnostic.json", diagnostic)
    plot_tables(tables, figures)
    verify_hashes(hashes)
    manifest = {"source_sha256": hashes, "script_sha256": digest(Path(__file__)), "script": str(Path(__file__).resolve()),
                "command": shlex.join([sys.executable, *sys.argv]), "source_run": str(runtime), "source_windows": summary["time_windows"],
                "analysis_windows": WINDOWS, "source_hashes_unchanged": True, "status": "built_pending_independent_review",
                "generated_sha256": {str(p): digest(p) for p in [output / "diagnostic.json", *tables.glob("*.csv"), *figures.glob("*.png")]}}
    json_write(output / "manifest.json", manifest)
    for d in ("D2", "D3", "D4"):
        ledger["steps"][d].update(status="completed", outputs=[str(output), str(tables), str(figures)], command=manifest["command"],
                                  verification=["Source hashes unchanged", "Actual interval coverage checked", "Reused trip accounts reconciled", "No simulator calls"], resume_point="D5")
    ledger["steps"]["D5"].update(status="running", verification=["Full offline build completed; dedicated unit tests and independent/visual checks to be recorded by analyst"], resume_point="D5")
    (output / "execution_ledger.json").write_text(json.dumps(ledger, indent=2) + "\n")
    print(json.dumps({"output": str(output), "e1_intervals": len(e1), "fcd_timeline_rows": len(timeline), "merge": diagnostic["merge"], "mainline_stopped_samples": diagnostic["mainline_stopped_samples"]}, indent=2))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ("runtime-dir", "output-dir", "table-dir", "figure-dir"):
        parser.add_argument("--" + name, type=Path, required=True)
    build(parser.parse_args())


if __name__ == "__main__":
    main()

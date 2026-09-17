"""Independent archive-only verifier for Stage 3 baseline diagnostics.

This module intentionally does not import the production Stage 3 analyzer.  It
reconstructs the registered quantitative evidence directly from immutable XML
archives and compares normalized records with the derived CSV/JSON package.
"""
from __future__ import annotations

import argparse
from collections import defaultdict
import csv
import hashlib
import json
import math
from pathlib import Path
import re
import xml.etree.ElementTree as ET


ROOT = Path(__file__).resolve().parents[2]
CLASSES = ("M", "R", "U", "X")
WINDOWS = {"Full": (0.0, 2700.0), "A": (0.0, 1500.0), "B": (300.0, 1500.0), "Post": (1500.0, 2700.0)}


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def load_json(path: Path) -> dict:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"expected object: {path}")
    return value


def rows(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def cls(vehicle_id: str) -> str:
    match = re.fullmatch(r"(M|R|U|X)_flow\.\d+", vehicle_id)
    if not match:
        raise ValueError(f"unknown vehicle id {vehicle_id}")
    return match.group(1)


def number(value: str | float | int | None) -> float | None:
    if value in (None, ""):
        return None
    result = float(value)
    if not math.isfinite(result):
        raise ValueError("non-finite value")
    return result


class Sources:
    def __init__(self, source_map: Path):
        data = load_json(source_map)
        if data.get("archive_status") != "complete":
            raise ValueError("archive incomplete")
        self.by_suffix: dict[str, Path] = {}
        for item in data["file_map"]:
            path = ROOT / item["archive_relative_path"]
            if sha256(path) != item["sha256"]:
                raise ValueError(f"source hash mismatch: {path}")
            suffix = str(Path(item["original_absolute_path"]).relative_to(data["source_runtime_path"]))
            if suffix in self.by_suffix:
                raise ValueError(f"duplicate suffix: {suffix}")
            self.by_suffix[suffix] = path

    def get(self, suffix: str) -> Path:
        return self.by_suffix[suffix]


def contiguous(times: list[float], step: float) -> list[tuple[float, float, int]]:
    ordered = sorted(times)
    if len(ordered) != len(set(ordered)):
        raise ValueError("duplicate episode time")
    if not ordered:
        return []
    result: list[tuple[float, float, int]] = []
    start = previous = ordered[0]
    count = 1
    for current in ordered[1:]:
        if not math.isclose(current - previous, step):
            result.append((start, previous, count))
            start, count = current, 1
        else:
            count += 1
        previous = current
    result.append((start, previous, count))
    return result


def scan_fcd(path: Path, contract: dict) -> dict:
    lanes = contract["lanes"]
    stop = float(contract["stop_definition"]["speed_threshold_mps"])
    step_s = float(contract["fcd"]["sampling_period_s"])
    timeline: dict[tuple, tuple] = {}
    vehicle_stop: defaultdict[tuple[str, str], list[float]] = defaultdict(list)
    region_stop: defaultdict[tuple[str, str], list[float]] = defaultdict(list)
    previous: dict[str, tuple[float, str]] = {}
    first: dict[str, tuple] = {}
    frames: set[float] = set()
    shared_stopped: defaultdict[str, set[float]] = defaultdict(set)
    for _, timestep in ET.iterparse(path, events=("end",)):
        if timestep.tag != "timestep":
            continue
        time_s = float(timestep.get("time"))
        if time_s in frames:
            raise ValueError("duplicate FCD frame")
        frames.add(time_s)
        seen: set[str] = set()
        grouped: defaultdict[tuple[str, str], dict] = defaultdict(lambda: {
            "present": 0, "stopped": 0, "speed_sum": 0.0, "speed_n": 0,
            "minimum": None, "maximum": None, "missing_speed": 0,
        })
        stopped_regions: set[tuple[str, str]] = set()
        for vehicle in list(timestep):
            vehicle_id = vehicle.get("id", "")
            if vehicle_id in seen:
                raise ValueError("duplicate FCD vehicle")
            seen.add(vehicle_id)
            vehicle_class = cls(vehicle_id)
            lane_id = vehicle.get("lane", "")
            if lane_id not in lanes:
                raise ValueError(f"unknown lane {lane_id}")
            lane = lanes[lane_id]
            region = lane["region"]
            entry = grouped[(lane_id, vehicle_class)]
            entry["present"] += 1
            raw_speed = vehicle.get("speed")
            is_stopped = False
            if raw_speed is None:
                entry["missing_speed"] += 1
            else:
                speed = float(raw_speed)
                entry["speed_sum"] += speed
                entry["speed_n"] += 1
                is_stopped = speed <= stop
                entry["stopped"] += int(is_stopped)
            if lane.get("r_path_start_m") is not None:
                path_position = float(lane["r_path_start_m"]) + float(vehicle.get("pos"))
                entry["minimum"] = path_position if entry["minimum"] is None else min(entry["minimum"], path_position)
                entry["maximum"] = path_position if entry["maximum"] is None else max(entry["maximum"], path_position)
            if is_stopped:
                vehicle_stop[(vehicle_id, region)].append(time_s)
                stopped_regions.add((region, vehicle_class))
                if region == "shared_approach":
                    shared_stopped[vehicle_class].add(time_s)
            if vehicle_class == "R" and lane.get("first_downstream_eligible") and vehicle_id not in first:
                prior = previous.get(vehicle_id)
                first[vehicle_id] = (vehicle_id, prior[0] if prior else None, prior[1] if prior else None,
                                     time_s, lane_id, "bracketed" if prior and math.isclose(time_s-prior[0], step_s) else "unresolved_previous_frame")
            previous[vehicle_id] = (time_s, lane_id)
        for item in stopped_regions:
            region_stop[item].append(time_s)
        for (lane_id, vehicle_class), item in grouped.items():
            timeline[(time_s, lane_id, vehicle_class)] = (
                item["present"], item["stopped"], item["speed_sum"], item["speed_n"],
                item["minimum"], item["maximum"], item["missing_speed"],
            )
        timestep.clear()
    expected = {float(i) for i in range(2700)}
    if frames != expected:
        raise ValueError(f"FCD labels differ: missing={len(expected-frames)} extra={len(frames-expected)}")
    episodes: list[tuple] = []
    for kind, groups in (("vehicle_stop", vehicle_stop), ("region_stop", region_stop)):
        for identity, times in sorted(groups.items()):
            vehicle_class = cls(identity[0]) if kind == "vehicle_stop" else identity[1]
            region = identity[1] if kind == "vehicle_stop" else identity[0]
            vehicle_id = identity[0] if kind == "vehicle_stop" else None
            for first_t, last_t, count in contiguous(times, step_s):
                left = first_t <= 0 or first_t-step_s not in frames
                right = last_t+step_s >= 2700 or last_t+step_s not in frames
                reason = "source_frame_missing" if ((first_t > 0 and first_t-step_s not in frames) or (last_t+step_s < 2700 and last_t+step_s not in frames)) else "source_boundary" if left or right else "stop_condition_false_or_entity_absent"
                full = (kind, vehicle_class, region, vehicle_id, "Full", first_t, last_t, count, count*step_s, left, right, reason)
                episodes.append(full)
                for window in ("A", "B", "Post"):
                    begin, end = WINDOWS[window]
                    kept_first = max(first_t, begin)
                    kept_last = min(last_t, end-step_s)
                    if kept_first > kept_last:
                        continue
                    kept_count = int(round((kept_last-kept_first)/step_s))+1
                    left_clip = kept_first > first_t
                    right_clip = kept_last < last_t
                    clipped_reason = "window_clip_both" if left_clip and right_clip else "window_clip_left" if left_clip else "window_clip_right" if right_clip else reason
                    episodes.append((kind, vehicle_class, region, vehicle_id, window, kept_first, kept_last,
                                     kept_count, kept_count*step_s, left if not left_clip else True,
                                     right if not right_clip else True, clipped_reason))
    return {"timeline": timeline, "episodes": episodes, "first": set(first.values()), "frames": frames,
            "cooccurrence": shared_stopped["R"] & shared_stopped["U"]}


def normalize_timeline(derived: list[dict]) -> dict[tuple, tuple]:
    result = {}
    for row in derived:
        key = (float(row["time_s"]), row["lane_id"], row["class"])
        result[key] = (int(row["present_count"]), int(row["stopped_count"]), float(row["speed_sum_mps"]),
                       int(row["speed_n"]), number(row["min_path_position_m"]), number(row["max_path_position_m"]),
                       int(row["missing_speed_count"]))
    return result


def close(a, b, tolerance=1e-8) -> bool:
    if isinstance(a, tuple) and isinstance(b, tuple):
        return len(a) == len(b) and all(close(x, y, tolerance) for x, y in zip(a, b))
    if a is None or b is None:
        return a is b
    if isinstance(a, (float, int)) and isinstance(b, (float, int)):
        return math.isclose(a, b, rel_tol=tolerance, abs_tol=tolerance)
    return a == b


def compare_mapping(expected: dict, observed: dict, label: str) -> None:
    if set(expected) != set(observed):
        raise AssertionError(f"{label} keys differ: expected={len(expected)} observed={len(observed)}")
    bad = [key for key in expected if not close(expected[key], observed[key])]
    if bad:
        raise AssertionError(f"{label} differs at {bad[:3]}")


def independent_sensitivity(source: Sources, contract: dict) -> list[tuple]:
    detector_rows: list[dict] = []
    detector_ids = set()
    for detector in contract["e1_detectors"]:
        if detector["group"] != "M-only_internal_merge_entry":
            continue
        detector_ids.add(detector["detector_id"])
        for _, node in ET.iterparse(source.get(detector["output_suffix"]), events=("end",)):
            if node.tag == "interval":
                n = int(node.get("nVehContrib"))
                speed = float(node.get("speed"))
                detector_rows.append({"detector": detector["detector_id"], "begin": float(node.get("begin")),
                                      "end": float(node.get("end")), "n": n, "speed": speed if n > 0 and speed >= 0 else None})
                node.clear()
    result = []
    for window in ("A", "B"):
        begin, end = WINDOWS[window]
        for aggregation in (30.0, 60.0, 120.0):
            cursor = begin
            total_n = total_speed_n = 0
            weighted_speed = 0.0
            covered = 0.0
            qualified = True
            while cursor < end:
                edge = min(end, cursor+aggregation)
                selected = [r for r in detector_rows if r["begin"] >= cursor and r["end"] <= edge]
                for detector_id in detector_ids:
                    group = sorted((r for r in selected if r["detector"] == detector_id), key=lambda r:r["begin"])
                    position = cursor
                    for item in group:
                        if not math.isclose(item["begin"], position): qualified = False
                        position = item["end"]
                    if not group or not math.isclose(position, edge): qualified = False
                if qualified:
                    covered += edge-cursor
                    total_n += sum(r["n"] for r in selected)
                    valid = [r for r in selected if r["n"] > 0 and r["speed"] is not None]
                    total_speed_n += sum(r["n"] for r in valid)
                    weighted_speed += sum(r["speed"]*r["n"] for r in valid)
                cursor = edge
            q = 3600*total_n/(end-begin) if qualified else None
            v = weighted_speed/total_speed_n if qualified and total_speed_n else None
            result.extend([(window, aggregation, "q", q, total_n if qualified else None, covered, "complete" if qualified else "incomplete"),
                           (window, aggregation, "v", v, total_n if qualified else None, covered, "complete" if qualified else "incomplete")])
    return result


def verify_run(ledger: dict, contract: dict, manifest_path: Path) -> dict:
    manifest = load_json(manifest_path)
    run_id = manifest["run_id"]
    source_row = next(row for row in ledger["source_runs"] if row["run_id"] == run_id)
    source = Sources(ROOT / source_row["source_map_path"])
    output_dir = manifest_path.parent
    table_dir = next((ROOT / p).parent for p in manifest["outputs"] if p.endswith("lane_class_timeline.csv"))
    fcd = scan_fcd(source.get("outputs/fcd.xml"), contract)
    compare_mapping(fcd["timeline"], normalize_timeline(rows(table_dir / "lane_class_timeline.csv")), f"{run_id} timeline")
    derived_first = set()
    for row in rows(output_dir / "first_downstream_events.csv"):
        derived_first.add((row["vehicle_id"], number(row["previous_time_s"]), row["previous_lane"] or None,
                           float(row["first_downstream_time_s"]), row["first_downstream_lane"], row["status"]))
    if fcd["first"] != derived_first:
        raise AssertionError(f"{run_id} first-downstream differs")
    derived_episodes = set()
    for row in rows(table_dir / "stopping_episodes.csv"):
        derived_episodes.add((row["kind"], row["class"], row["region"], row["vehicle_id_or_null"] or None,
                              row["observation_domain"], float(row["first_label"]), float(row["last_label"]),
                              int(row["sample_count"]), float(row["support_seconds"]), row["censor_left"] == "True",
                              row["censor_right"] == "True", row["gap_reason"]))
    if set(fcd["episodes"]) != derived_episodes:
        raise AssertionError(f"{run_id} normalized episodes differ: raw={len(fcd['episodes'])} derived={len(derived_episodes)}")
    propagation = load_json(output_dir / "propagation_event_sets.json")
    if set(propagation["shared_R_U_cooccurrence_labels_s"]) != fcd["cooccurrence"]:
        raise AssertionError(f"{run_id} R/U cooccurrence differs")
    propagation_regions = ("ramp_accel", "ramp_mid_internal", "ramp_storage", "ramp_diverge_internal", "shared_approach")
    coordinates = {}
    for region in propagation_regions:
        lane_rows = [lane for lane in contract["lanes"].values() if lane["region"] == region]
        starts = {float(lane["r_path_start_m"]) for lane in lane_rows}
        ends = {float(lane["r_path_end_m"]) for lane in lane_rows}
        if len(starts) != 1 or len(ends) != 1:
            raise AssertionError(f"{run_id} ambiguous independent propagation coordinate for {region}")
        coordinates[region] = (starts.pop(), ends.pop())
    derived_order = sorted(coordinates, key=lambda region:coordinates[region][0], reverse=True)
    if tuple(derived_order) != propagation_regions:
        raise AssertionError(f"{run_id} independent propagation order differs: {derived_order}")
    if any(not math.isclose(coordinates[d][0], coordinates[u][1], abs_tol=1e-8) for d,u in zip(derived_order,derived_order[1:])):
        raise AssertionError(f"{run_id} independent propagation spans are not contiguous")
    full_region_R = [episode for episode in fcd["episodes"] if episode[0] == "region_stop" and episode[1] == "R" and episode[4] == "Full"]
    first_by_region = {region:min((episode[5] for episode in full_region_R if episode[2] == region), default=None) for region in derived_order}
    observed_order = [region for region in derived_order if first_by_region[region] is not None]
    contradictions = [(d,u) for d,u in zip(observed_order,observed_order[1:]) if first_by_region[d] > first_by_region[u]]
    expected_status = "contradicted_order" if contradictions else "complete_ordered_observation" if len(observed_order)==len(derived_order) else "partial_observation" if observed_order else "not_identified"
    spatial_rows = rows(table_dir / "spatial_propagation_evidence.csv")
    if len(spatial_rows) != 1 or spatial_rows[0]["status"] != expected_status:
        raise AssertionError(f"{run_id} propagation status differs: expected {expected_status}")
    r_memberships = [set(propagation[key]) for key in ("ramp_end_event_ids","storage_event_ids","internal_event_ids","shared_R_event_ids")]
    if any(first_set & second_set for index,first_set in enumerate(r_memberships) for second_set in r_memberships[index+1:]):
        raise AssertionError(f"{run_id} propagation membership overlap")

    planned = {node.get("id").split("_")[0]: int(node.get("number")) for node in ET.parse(source.get("demand.rou.xml")).getroot().findall("flow")}
    trips: defaultdict[str, list[tuple[float, float]]] = defaultdict(list)
    trip_ids: set[str] = set()
    for _, node in ET.iterparse(source.get("outputs/tripinfo.xml"), events=("end",)):
        if node.tag == "tripinfo":
            vehicle_id = node.get("id")
            if vehicle_id in trip_ids:
                raise AssertionError(f"{run_id} duplicate tripinfo id")
            trip_ids.add(vehicle_id)
            trips[cls(vehicle_id)].append((float(node.get("depart")), float(node.get("arrival"))))
            node.clear()
    route_ids: set[str] = set()
    for _, node in ET.iterparse(source.get("outputs/vehroute.xml"), events=("end",)):
        if node.tag == "vehicle":
            vehicle_id = node.get("id")
            if vehicle_id in route_ids:
                raise AssertionError(f"{run_id} duplicate vehroute id")
            cls(vehicle_id)
            route_ids.add(vehicle_id)
            node.clear()
    if trip_ids != route_ids or len(trip_ids) != sum(planned.values()):
        raise AssertionError(f"{run_id} tripinfo/vehroute/plan identity coverage differs")
    boundaries = {}
    for _, node in ET.iterparse(source.get("outputs/sumo_summary.xml"), events=("end",)):
        if node.tag == "step" and float(node.get("time")) in (1499.0, 2699.0):
            boundaries[float(node.get("time"))+1.0] = tuple(int(node.get(k)) for k in ("loaded","inserted","arrived"))
        node.clear()
    endpoint_expected = {}
    for endpoint in (1500.0, 2700.0):
        all_entered = sum(depart < endpoint for records in trips.values() for depart,_ in records)
        all_arrived = sum(arrival < endpoint for records in trips.values() for _,arrival in records)
        if boundaries.get(endpoint) != (sum(planned.values()), all_entered, all_arrived):
            raise AssertionError(f"{run_id} SUMO summary endpoint coverage differs at {endpoint}")
        for vehicle_class in CLASSES:
            entered = sum(depart < endpoint for depart, _ in trips[vehicle_class])
            arrived = sum(arrival < endpoint for _, arrival in trips[vehicle_class])
            endpoint_expected[(vehicle_class, endpoint)] = (planned[vehicle_class], entered, arrived, planned[vehicle_class]-entered, entered-arrived)
    endpoint_observed = {(r["class"], float(r["endpoint_s"])): tuple(int(r[k]) for k in ("planned","entered","arrived","outside_confirmed","in_network")) for r in rows(output_dir / "endpoint_accounting.csv")}
    compare_mapping(endpoint_expected, endpoint_observed, f"{run_id} endpoints")

    expected_sensitivity = {(w,a,m):(v,n,c,q) for w,a,m,v,n,c,q in independent_sensitivity(source, contract)}
    observed_sensitivity = {(r["window"],float(r["aggregation_s"]),r["metric"]):(number(r["value"]),number(r["n_contrib"]),float(r["covered_seconds"]),r["qualification"]) for r in rows(output_dir / "sensitivity.csv")}
    compare_mapping(expected_sensitivity, observed_sensitivity, f"{run_id} sensitivity")

    questions = [r for r in rows(table_dir / "condition_evidence_summary.csv") if r["entity"].startswith("question:")]
    if len(questions) != 5 or any(not r["qualification"] for r in questions):
        raise AssertionError(f"{run_id} five-question coverage fails")
    known = None
    if run_id == "C17":
        known = {"planned": planned, "R_before_1500": sum(float(t) < 1500 for _,_,_,t,_,_ in fcd["first"]),
                 "R_total": len(fcd["first"])}
        if known != {"planned": {"M":1333,"R":300,"U":150,"X":75}, "R_before_1500":36, "R_total":300}:
            raise AssertionError(f"C17 known checks fail: {known}")
    return {"run_id":run_id, "status":"passed", "timeline_cells":len(fcd["timeline"]),
            "episode_records":len(fcd["episodes"]), "first_R_downstream":len(fcd["first"]),
            "shared_R_U_cooccurrence_labels":len(fcd["cooccurrence"]), "sensitivity_values":len(expected_sensitivity),
            "question_units":"5/5", "endpoint_identity_records":len(trip_ids),
            "endpoint_coverage_sources":"demand+tripinfo+vehroute+sumo_summary", "known_C17":known}


def main() -> int:
    parser = argparse.ArgumentParser(description="Independently verify Stage 3 archive-derived quantities")
    parser.add_argument("--ledger", required=True)
    parser.add_argument("--contract", required=True)
    parser.add_argument("--run-manifest", action="append", required=True)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()
    output = Path(args.output)
    if output.exists():
        raise FileExistsError(output)
    ledger = load_json(Path(args.ledger))
    contract = load_json(Path(args.contract))
    results = [verify_run(ledger, contract, Path(path)) for path in args.run_manifest]
    payload = {"schema_version":1, "status":"passed", "method":"independent raw XML reconstruction; no production analyzer imports",
               "run_count":len(results), "runs":results,
               "totals":{"timeline_cells":sum(r["timeline_cells"] for r in results),
                         "episode_records":sum(r["episode_records"] for r in results),
                         "first_R_downstream":sum(r["first_R_downstream"] for r in results),
                         "shared_R_U_cooccurrence_labels":sum(r["shared_R_U_cooccurrence_labels"] for r in results),
                         "sensitivity_values":sum(r["sensitivity_values"] for r in results)},
               "actual_sumo_starts":0}
    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open("x", encoding="utf-8") as handle:
        json.dump(payload, handle, indent=2, ensure_ascii=False, allow_nan=False)
        handle.write("\n")
    print(json.dumps(payload["totals"], sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

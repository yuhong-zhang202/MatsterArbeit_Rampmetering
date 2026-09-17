"""Independent raw-XML reconstruction for Stage 4 Tier 2.

This verifier intentionally does not import the production Stage 4 adapter.  It
reads only registered source maps, immutable archived files, the measurement
contract, and registered manifests.
"""
from __future__ import annotations

from collections import defaultdict
import argparse
import hashlib
import json
from pathlib import Path
import xml.etree.ElementTree as ET


ROOT = Path(__file__).resolve().parents[6]
BATCH = ROOT / "data/processed/stage4_qmain_sequential_20260912_v1"
RUN_IDS = ("QM3650S17", "QM3650S23")
CLASSES = ("M", "R", "U", "X")
WINDOWS = {"A": (0.0, 1500.0), "B": (300.0, 1500.0),
           "Post": (1500.0, 2700.0), "Full": (0.0, 2700.0)}
R_ORDER = ("ramp_accel", "ramp_mid_internal", "ramp_storage",
           "ramp_diverge_internal", "shared_approach")


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def archive_files(source_map_path: Path) -> tuple[dict[str, Path], dict]:
    source = load(source_map_path)
    files: dict[str, Path] = {}
    for row in source["file_map"]:
        suffix = row["original_absolute_path"].split(source["source_runtime_path"] + "/", 1)[-1]
        path = ROOT / row["archive_relative_path"]
        assert path.is_file(), path
        assert path.stat().st_size == row["size_bytes"], path
        assert sha256(path) == row["sha256"], path
        files[suffix] = path
    assert len(files) == source["source_file_count"] == source["archive_file_count"] == 29
    return files, source


def aggregate(rows: list[dict], begin: float, end: float) -> dict:
    selected = [r for r in rows if begin <= r["begin"] and r["end"] <= end]
    covered = sum(r["end"] - r["begin"] for r in selected)
    contributions = sum(r["n_contrib"] for r in selected)
    return {
        "begin": begin, "end": end, "covered_seconds": covered,
        "q_vehph": sum(r["q_vehph"] * (r["end"] - r["begin"]) for r in selected) / covered,
        "speed_mps": (sum(r["speed_mps"] * r["n_contrib"] for r in selected
                          if r["speed_mps"] is not None) / contributions
                      if contributions else None),
        "occupancy_percent": sum(r["occupancy_percent"] * (r["end"] - r["begin"])
                                 for r in selected) / covered,
        "n_contrib": contributions,
    }


def e1(files: dict[str, Path], prefix: str) -> dict:
    by_bin: defaultdict[tuple[float, float], list[dict]] = defaultdict(list)
    for lane in ("l0", "l1"):
        path = files[f"outputs/{prefix}_{lane}.xml"]
        for node in ET.parse(path).getroot().iter("interval"):
            begin, end = float(node.get("begin")), float(node.get("end"))
            by_bin[(begin, end)].append({
                "n_entered": int(node.get("nVehEntered")),
                "n_contrib": int(node.get("nVehContrib")),
                "speed_mps": float(node.get("speed")),
                "occupancy_percent": float(node.get("occupancy")),
            })
    rows = []
    for begin in range(0, 2700, 30):
        pair = by_bin[(float(begin), float(begin + 30))]
        assert len(pair) == 2, (prefix, begin, len(pair))
        n_contrib = sum(r["n_contrib"] for r in pair)
        rows.append({
            "begin": float(begin), "end": float(begin + 30),
            "n_contrib": n_contrib,
            "q_vehph": sum(r["n_entered"] for r in pair) * 120.0,
            "speed_mps": (sum(r["speed_mps"] * r["n_contrib"] for r in pair) / n_contrib
                          if n_contrib else None),
            "occupancy_percent": sum(r["occupancy_percent"] for r in pair) / 2.0,
        })
    return {"bins_30s": rows,
            "aggregates": {name: aggregate(rows, *limits) for name, limits in WINDOWS.items()}}


def episodes(times_by_key: dict[tuple, list[float]]) -> dict[tuple, tuple[int, int]]:
    result = {}
    for key, values in times_by_key.items():
        count, previous = 0, None
        for value in sorted(values):
            if previous is None or value - previous != 1.0:
                count += 1
            previous = value
        result[key] = (count, len(values))
    return result


def close(a, b, tolerance=1e-10) -> bool:
    if a is None or b is None:
        return a is b
    if isinstance(a, (int, float)) and isinstance(b, (int, float)):
        return abs(float(a) - float(b)) <= tolerance
    return a == b


def compare(checks: list[dict], name: str, observed, expected, tolerance=1e-10) -> None:
    passed = close(observed, expected, tolerance)
    checks.append({"check": name, "passed": passed, "observed": observed, "expected": expected})
    if not passed:
        raise AssertionError(f"{name}: {observed!r} != {expected!r}")


def endpoint_rows(planned: dict[str, int], first_seen: dict[str, float], arrivals: dict[str, float]) -> list[dict]:
    result = []
    for endpoint in (1500.0, 2700.0):
        for cls in CLASSES:
            entered = sum(identity.startswith(cls + "_flow.") and time < endpoint
                          for identity, time in first_seen.items())
            arrived = sum(identity.startswith(cls + "_flow.") and time < endpoint
                          for identity, time in arrivals.items())
            result.append({"class": cls, "endpoint_s": endpoint, "planned": planned[cls],
                           "entered": entered, "arrived": arrived,
                           "in_network": entered - arrived, "outside": planned[cls] - entered,
                           "coverage": True})
    return result


def compare_e1(checks: list[dict], prefix: str, observed: dict, expected: dict) -> None:
    for index, (left, right) in enumerate(zip(observed["bins_30s"], expected["bins_30s"], strict=True)):
        for key in ("begin", "end", "n_contrib", "q_vehph", "speed_mps", "occupancy_percent"):
            compare(checks, f"{prefix}.bin{index}.{key}", left[key], right[key])
    for window in expected["aggregates"]:
        for key in ("begin", "end", "covered_seconds", "n_contrib", "q_vehph", "speed_mps",
                    "occupancy_percent"):
            compare(checks, f"{prefix}.{window}.{key}", observed["aggregates"][window][key],
                    expected["aggregates"][window][key])


def strict_below_above(candidate: dict, lower: dict, upper: dict, dv=0.0, do=0.0) -> bool:
    return (candidate["speed_mps"] < min(lower["speed_mps"], upper["speed_mps"]) - dv
            and candidate["occupancy_percent"] > max(lower["occupancy_percent"],
                                                       upper["occupancy_percent"]) + do)


def ejmi(candidate: dict, lower: dict, upper: dict, contract: dict) -> dict:
    margins = contract["ejmi"]["margins"]
    aggregate_checks = {
        window: strict_below_above(candidate["aggregates"][window], lower["aggregates"][window],
                                   upper["aggregates"][window], margins[window]["delta_v_mps"],
                                   margins[window]["delta_occ_percentage_points"])
        for window in ("A", "B")
    }
    blocks = []
    for begin in range(300, 1500, 120):
        end = begin + 120
        c120, l120, u120 = (aggregate(x["bins_30s"], begin, end)
                            for x in (candidate, lower, upper))
        pass120 = strict_below_above(c120, l120, u120)
        pass60 = []
        for sub in (begin, begin + 60):
            c, l, u = (aggregate(x["bins_30s"], sub, sub + 60)
                       for x in (candidate, lower, upper))
            pass60.append(strict_below_above(c, l, u))
        pass30 = []
        for sub in range(begin, end, 30):
            c, l, u = (aggregate(x["bins_30s"], sub, sub + 30)
                       for x in (candidate, lower, upper))
            pass30.append(strict_below_above(c, l, u))
        passed = pass120 and all(pass60) and sum(pass30) >= 3
        blocks.append({"begin": begin, "end": end, "pass_120": pass120,
                       "pass_60_count": sum(pass60), "pass_30_count": sum(pass30),
                       "passed": passed})
    persistence = any(row["passed"] for row in blocks)
    return {"aggregate_checks": aggregate_checks,
            "persistence": {"blocks": blocks, "passed": persistence},
            "status": "positive" if all(aggregate_checks.values()) and persistence else "not_identified"}


def reconstruct(run_id: str, contract: dict) -> dict:
    source_map_path = BATCH / "source_maps" / f"{run_id}_attempt1.json"
    files, source = archive_files(source_map_path)
    manifest_path = BATCH / "analysis/tier2/engineering" / run_id / "run_manifest.json"
    production = load(manifest_path)
    checks: list[dict] = []

    planned: dict[str, int] = {}
    for node in ET.parse(files["demand.rou.xml"]).getroot().iter("flow"):
        cls = node.get("id", "").split("_flow", 1)[0]
        if cls in CLASSES:
            planned[cls] = planned.get(cls, 0) + int(node.get("number"))
    arrivals, depart_positions = {}, defaultdict(list)
    for node in ET.parse(files["outputs/tripinfo.xml"]).getroot().iter("tripinfo"):
        identity = node.get("id")
        arrivals[identity] = float(node.get("arrival"))
        if identity.startswith("M_flow."):
            depart_positions[node.get("departLane")].append(float(node.get("departPos")))

    lanes = contract["required_observations"]["lanes"]
    known_ids = {f"{cls}_flow.{index}" for cls in CLASSES for index in range(planned[cls])}
    expected_labels = {float(i) for i in range(2700)}
    labels, first_seen, previous_r, first_passage = [], {}, {}, {}
    stopped: defaultdict[tuple, list[float]] = defaultdict(list)
    m_positions: defaultdict[str, list[float]] = defaultdict(list)
    shared_times: defaultdict[str, set[float]] = defaultdict(set)
    first_region_time: dict[str, float] = {}
    duplicates = unknown_ids = unknown_lanes = 0
    for _, step in ET.iterparse(files["outputs/fcd.xml"], events=("end",)):
        if step.tag != "timestep":
            continue
        time_s = float(step.get("time")); labels.append(time_s); seen = set()
        for vehicle in step.findall("vehicle"):
            identity, lane_id = vehicle.get("id"), vehicle.get("lane")
            if identity in seen: duplicates += 1
            seen.add(identity)
            if identity not in known_ids: unknown_ids += 1
            if lane_id not in lanes: unknown_lanes += 1; continue
            first_seen.setdefault(identity, time_s)
            cls = identity.split("_flow.", 1)[0]
            if cls == "R" and identity not in first_passage and lanes[lane_id]["first_downstream_eligible"]:
                prior = previous_r.get(identity)
                first_passage[identity] = {"time": time_s,
                    "bracketed": bool(prior and time_s - prior[0] == 1.0)}
            if cls == "R": previous_r[identity] = (time_s, lane_id)
            if float(vehicle.get("speed")) <= 0.1:
                region = lanes[lane_id]["region"]
                stopped[(cls, identity, region)].append(time_s)
                if cls == "M": m_positions[lane_id].append(float(vehicle.get("pos")))
                if cls in ("R", "U") and region == "shared_approach": shared_times[cls].add(time_s)
                if cls == "R" and region in R_ORDER:
                    first_region_time.setdefault(region, time_s)
        step.clear()
    assert set(labels) == expected_labels and len(labels) == 2700
    ep = endpoint_rows(planned, first_seen, arrivals)
    production_ep = production["endpoints"]
    compare(checks, "endpoint_rows", ep, production_ep)
    planned_rates = {cls: planned[cls] * 3600.0 / 1500.0 for cls in CLASSES}
    realized_rates = {row["class"]: row["entered"] * 3600.0 / 1500.0 for row in ep
                      if row["endpoint_s"] == 1500.0}
    compare(checks, "planned_demand_vehph", planned_rates,
            production["required_observations"]["planned_demand_vehph"])
    compare(checks, "realized_entry_vehph_A", realized_rates,
            production["required_observations"]["realized_entry_vehph_A"])

    downstream = e1(files, "merge_downstream_e1")
    internal = e1(files, "mainline_merge_entry_e1")
    compare_e1(checks, "downstream", downstream,
               production["required_observations"]["downstream_e1"])
    compare_e1(checks, "internal", internal, production["e1"])
    episodes_by_key = episodes(stopped)
    m_episode_count = sum(v[0] for k, v in episodes_by_key.items() if k[0] == "M")
    m_sample_count = sum(v[1] for k, v in episodes_by_key.items() if k[0] == "M")
    compare(checks, "m_episode_count", m_episode_count,
            len(production["required_observations"]["m_stopped_episodes"]))
    compare(checks, "m_sample_count", m_sample_count,
            sum(row["stopped_sample_count"] for row in production["required_observations"]["m_stopped_position_range"]))
    m_ranges = [{"lane_id": lane, "stopped_sample_count": len(values),
                 "min_position_m": min(values), "max_position_m": max(values),
                 "min_distance_to_lane_end_m": lanes[lane]["length_m"] - max(values),
                 "max_distance_to_lane_end_m": lanes[lane]["length_m"] - min(values)}
                for lane, values in sorted(m_positions.items())]
    compare(checks, "m_stopped_position_range", m_ranges,
            production["required_observations"]["m_stopped_position_range"])
    depart_ranges = [{"lane_id": lane, "vehicle_count": len(values),
                      "min_depart_position_m": min(values), "max_depart_position_m": max(values)}
                     for lane, values in sorted(depart_positions.items())]
    compare(checks, "m_depart_position_range", depart_ranges,
            production["required_observations"]["m_depart_position_range"])

    a_arrivals = {identity for identity, time in arrivals.items()
                  if identity.startswith("R_flow.") and time < 1500.0}
    a_pass = {identity: row for identity, row in first_passage.items() if row["time"] < 1500.0}
    r_passage = {"a_arrival_count": len(a_arrivals),
                 "a_bracketed_event_count": sum(row["bracketed"] for row in a_pass.values()),
                 "a_unbracketed_event_count": sum(not row["bracketed"] for row in a_pass.values()),
                 "arrival_without_passage_ids": sorted(a_arrivals - set(a_pass)),
                 "coverage_complete": True,
                 "denominator_all_observed_r_passage_events": len(first_passage),
                 "status": ("clear_passage" if a_pass and a_arrivals <= set(a_pass)
                            else "clear_exclusion" if not a_pass and not a_arrivals
                            else "unresolved")}
    compare(checks, "r_passage", r_passage, production["r_passage"])
    sequence = [r for r in R_ORDER if r in first_region_time]
    compare(checks, "r_region_sequence", sequence,
            production["required_observations"]["r_propagation"]["event_sets"]["observed_region_sequence"])
    compare(checks, "r_contradictions", [],
            production["required_observations"]["r_propagation"]["event_sets"]["contradiction_details"])

    shared = {cls: {"episode_count": sum(v[0] for k, v in episodes_by_key.items()
                                             if k[0] == cls and k[2] == "shared_approach"),
                    "stopped_vehicle_seconds": float(sum(v[1] for k, v in episodes_by_key.items()
                                                         if k[0] == cls and k[2] == "shared_approach"))}
              for cls in ("R", "U")}
    shared_result = {"by_class": shared,
                     "cooccurrence_support_s": len(shared_times["R"] & shared_times["U"])}
    prod_shared = production["required_observations"]["shared_r_u_stopped_exposure"]
    compare(checks, "shared.by_class", shared_result["by_class"], prod_shared["by_class"])
    compare(checks, "shared.cooccurrence", shared_result["cooccurrence_support_s"],
            prod_shared["cooccurrence_support_s"])

    tls_rows = [(float(n.get("time")), n.get("state"))
                for n in ET.parse(files["outputs/tls_states.xml"]).getroot().iter("tlsState")
                if n.get("id") == "urban_tls"]
    tls = {"label_count": len(tls_rows), "states": sorted({r[1] for r in tls_rows}),
           "transition_count": sum(a[1] != b[1] for a, b in zip(tls_rows, tls_rows[1:]))}
    prod_tls = production["required_observations"]["tls_context"]
    for key in tls:
        compare(checks, f"tls.{key}", tls[key], prod_tls[key])

    audit = production["required_observations"]["warning_coverage_audit"]
    compare(checks, "fcd.frame_count", len(labels), audit["fcd"]["frame_count"])
    compare(checks, "fcd.duplicates", duplicates, audit["fcd"]["duplicate_identities"])
    compare(checks, "fcd.unknown_ids", unknown_ids, audit["fcd"]["unknown_ids"])
    compare(checks, "fcd.unknown_lanes", unknown_lanes, audit["fcd"]["unknown_lanes"])
    compare(checks, "source_inventory", len(files), audit["source_inventory"]["registered_file_count"])
    for suffix, expected_hash in production["source_inventory_hashes"].items():
        compare(checks, f"source_hash.{suffix}", sha256(files[suffix]), expected_hash)

    return {"run_id": run_id, "source_map_path": source_map_path.relative_to(ROOT).as_posix(),
            "source_map_sha256": sha256(source_map_path), "manifest_path": manifest_path.relative_to(ROOT).as_posix(),
            "manifest_sha256": sha256(manifest_path), "source_file_count": len(files),
            "planned": planned, "endpoints": ep, "planned_demand_vehph": planned_rates,
            "realized_entry_vehph_A": realized_rates, "downstream_e1": downstream,
            "internal_e1": internal, "r_passage": r_passage,
            "m_stopped_episode_count": m_episode_count, "m_stopped_sample_count": m_sample_count,
            "m_stopped_position_range": m_ranges, "m_depart_position_range": depart_ranges,
            "r_first_stopped_time_by_region": first_region_time, "r_observed_region_sequence": sequence,
            "shared_r_u_stopped_exposure": shared_result, "tls": tls,
            "fcd_audit": {"frame_count": len(labels), "missing_frames": len(expected_labels-set(labels)),
                          "extra_frames": len(set(labels)-expected_labels), "duplicate_identities": duplicates,
                          "unknown_ids": unknown_ids, "unknown_lanes": unknown_lanes},
            "comparison_check_count": len(checks), "all_checks_passed": all(r["passed"] for r in checks),
            "checks": checks}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    contract = load(BATCH / "measurement_contract.json")
    runs = [reconstruct(run_id, contract) for run_id in RUN_IDS]
    for run in runs:
        seed = run["run_id"][-2:]
        lower = load(BATCH / "verification" / f"reference_C{seed}_revision_01/run_manifest.json")
        upper = load(BATCH / "verification" / f"reference_MH{seed}_revision_01/run_manifest.json")
        lower_map, _ = archive_files(ROOT / lower["source_map_path"])
        upper_map, _ = archive_files(ROOT / upper["source_map_path"])
        lower_e1 = e1(lower_map, "mainline_merge_entry_e1")
        upper_e1 = e1(upper_map, "mainline_merge_entry_e1")
        independent = ejmi(run["internal_e1"], lower_e1, upper_e1, contract)
        production = load(ROOT / run["manifest_path"])["ejmi"]
        assert independent["aggregate_checks"] == production["aggregate_checks"]
        assert independent["persistence"] == production["persistence"]
        assert independent["status"] == production["status"]
        run["independent_ejmi"] = independent
        run["reference_manifest_paths"] = [lower["run_id"], upper["run_id"]]
    output = {"schema_version": 1, "batch_id": BATCH.name,
              "method": "independent standard-library raw XML reconstruction; no production adapter import",
              "interpretation_boundary": "exploratory local diagnostics; not formal thesis evidence",
              "runs": runs, "all_runs_passed": all(r["all_checks_passed"] for r in runs),
              "total_comparison_checks": sum(r["comparison_check_count"] for r in runs)}
    if not args.output.parent.is_dir() or args.output.exists():
        raise FileExistsError("output parent must exist and output must be new")
    args.output.write_text(json.dumps(output, indent=2, sort_keys=True) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()

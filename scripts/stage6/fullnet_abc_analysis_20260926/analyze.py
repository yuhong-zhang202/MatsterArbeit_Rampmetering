#!/usr/bin/env python3
"""Prospective, descriptive Stage 6 matched full-network audit.

Reads immutable SUMO raw and prospective demand XML. The JSON spec binds four
run directories and their demand files. No scientific disposition is automated.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
from collections import Counter, defaultdict
from pathlib import Path
import xml.etree.ElementTree as ET

CLASSES = "MRUX"
ARMS = ("R0", "A", "B", "C")
CORE_CELLS = range(13, 18)
MAIN_LANES = {
    "main_up_0", "main_up_1", ":freeway_merge_0_0", ":freeway_merge_0_1",
    "merge_section_1", "merge_section_2", ":merge_end_0_0",
    ":merge_end_0_1", "main_down_0", "main_down_1",
}
THROUGH_LANE = "merge_section_1"
STORAGE_LANE = "ramp_storage_0"
INTERNAL_LANE = ":urban_diverge_1_0"
SHARED_LANE = "shared_approach_0"
HORIZON = 2700
ACTIVATION = 540


def digest(path):
    h = hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda: f.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def route_class(vid):
    for c in CLASSES:
        if vid.startswith(c + "_flow."):
            return c
    raise ValueError(f"Unknown vehicle class: {vid}")


def parse_demand(path):
    """Require prospectively materialized per-vehicle definitions, no flow expansion."""
    root = ET.parse(path).getroot()
    if root.tag != "routes" or root.findall("flow"):
        raise ValueError(f"Expected materialized <routes> with no flows: {path}")
    routes = {x.get("id"): x.get("edges") for x in root.findall("route")}
    out = {}
    for v in root.findall("vehicle"):
        vid = v.get("id")
        if vid in out:
            raise ValueError(f"Duplicate demand ID: {vid}")
        c = route_class(vid)
        rt = v.find("route")
        edges = rt.get("edges") if rt is not None else routes.get(v.get("route"))
        if not edges:
            raise ValueError(f"Missing route for {vid}")
        needed = ("depart", "type", "speedFactor", "departLane", "departSpeed", "departPos")
        if any(v.get(k) is None for k in needed):
            raise ValueError(f"Missing exogenous field for {vid}")
        out[vid] = {"class": c, "depart": v.get("depart"), "type": v.get("type"),
                    "speedFactor": v.get("speedFactor"), "departLane": v.get("departLane"),
                    "departSpeed": v.get("departSpeed"), "departPos": v.get("departPos"),
                    "route": edges}
    return out


def verify_manifest(raw):
    p = raw / "output_manifest.json"
    m = json.loads(p.read_text())
    rows = m.get("artifact_roles", []) + m.get("support_files", [])
    if not rows:
        raise ValueError(f"Empty output manifest: {p}")
    for row in rows:
        rel = Path(row["relative_path"])
        if rel.is_absolute() or ".." in rel.parts:
            raise ValueError(f"Unsafe manifest path: {rel}")
        f = raw / rel
        if not f.is_file() or f.stat().st_size != row["size_bytes"] or digest(f) != row["sha256"]:
            raise ValueError(f"Raw manifest mismatch: {f}")
    return {"entries": len(rows), "sha256": digest(p)}


def unique_xml_rows(path, tag):
    out = {}
    for _, elem in ET.iterparse(path, events=("end",)):
        if elem.tag == tag:
            vid = elem.get("id")
            if vid in out:
                raise ValueError(f"Duplicate {tag} ID: {vid}")
            route_class(vid)
            out[vid] = dict(elem.attrib)
            elem.clear()
    return out


def detector_queue(path):
    rows = []
    for _, e in ET.iterparse(path, events=("end",)):
        if e.tag == "interval":
            begin = finite_number(e.get("begin"), "E2 begin")
            end = finite_number(e.get("end"), "E2 end")
            if end - begin != 30 or begin != 30 * len(rows):
                raise ValueError(f"Incomplete or unordered E2 bins: {path}")
            rows.append({"begin": int(begin), "end": int(end),
                         "max_jam_vehicles": int(e.get("maxJamLengthInVehicles")),
                         "max_jam_m": finite_number(e.get("maxJamLengthInMeters"), "E2 jam length"),
                         "mean_occupancy_pct": finite_number(e.get("meanOccupancy"), "E2 occupancy")})
            e.clear()
    if len(rows) != HORIZON // 30:
        raise ValueError(f"E2 expected {HORIZON // 30} bins, got {len(rows)}")
    return rows


def lanechange_through(path):
    first = {}
    for _, e in ET.iterparse(path, events=("end",)):
        if e.tag == "change" and e.get("id", "").startswith("R_flow.") and e.get("to") == THROUGH_LANE:
            vid = e.get("id")
            t = finite_number(e.get("time"), "lanechange time")
            first[vid] = min(t, first.get(vid, t))
            e.clear()
    return first


def finite_number(value, label):
    x = float(value)
    if not math.isfinite(x):
        raise ValueError(f"Nonfinite {label}: {value}")
    return x


def fcd_scan(path):
    """One pass. All 2700 time labels are mandatory; no interpolation."""
    pre = {}
    observed = {c: set() for c in CLASSES}
    first_through = {}
    first_aux = {}
    bins = defaultdict(lambda: {"n": 0, "speed_sum": 0.0, "ids": set(), "seconds": set(),
                                "count_sum": 0, "count_max": 0})
    occupancy = defaultdict(Counter)
    time_labels = []
    invalid_m = []
    for _, step in ET.iterparse(path, events=("end",)):
        if step.tag != "timestep":
            continue
        t = finite_number(step.get("time"), "FCD time")
        if t != int(t) or not 0 <= t < HORIZON:
            raise ValueError(f"FCD time outside integer horizon: {t}")
        t = int(t)
        if time_labels and t != time_labels[-1] + 1:
            raise ValueError(f"Missing or repeated FCD second at {t}")
        time_labels.append(t)
        cell_counts = Counter()
        for v in step:
            if v.tag != "vehicle":
                continue
            a = v.attrib
            vid = a["id"]
            c = route_class(vid)
            observed[c].add(vid)
            lane = a["lane"]
            if t < ACTIVATION:
                key = (vid, t)
                if key in pre:
                    raise ValueError(f"Duplicate FCD identity-second {key}")
                pre[key] = tuple(a.get(k) for k in ("lane", "pos", "speed", "x", "y"))
            if c == "R":
                if lane == THROUGH_LANE:
                    first_through.setdefault(vid, t)
                if lane == "merge_section_0":
                    first_aux.setdefault(vid, t)
                if lane in (STORAGE_LANE, INTERNAL_LANE, SHARED_LANE):
                    occupancy[(t, lane)]["R_all"] += 1
                    if finite_number(a["speed"], "R speed") < 0.1:
                        occupancy[(t, lane)]["R_stopped"] += 1
            if c != "M":
                continue
            if lane not in MAIN_LANES:
                invalid_m.append((vid, t, lane))
                continue
            x = finite_number(a["x"], "M x")
            if not 0 <= x <= 2200:
                invalid_m.append((vid, t, lane))
                continue
            cell = min(int(x // 100), 21)
            if cell not in CORE_CELLS:
                continue
            b = t // 30
            r = bins[(cell, b)]
            r["n"] += 1
            r["speed_sum"] += finite_number(a["speed"], "M speed")
            r["ids"].add(vid)
            r["seconds"].add(t)
            cell_counts[cell] += 1
        for cell in CORE_CELLS:
            r = bins[(cell, t // 30)]
            r["count_sum"] += cell_counts[cell]
            r["count_max"] = max(r["count_max"], cell_counts[cell])
        step.clear()
    if time_labels != list(range(HORIZON)):
        raise ValueError(f"FCD incomplete: {len(time_labels)} labels")
    return {"pre": pre, "observed": observed, "through": first_through, "aux": first_aux,
            "bins": bins, "occupancy": occupancy, "invalid_m": invalid_m}


def summarize_run(arm, raw, demand_path):
    manifest = verify_manifest(raw)
    demand = parse_demand(demand_path)
    trips = unique_xml_rows(raw / "tripinfo.xml", "tripinfo")
    veh = unique_xml_rows(raw / "vehroute.xml", "vehicle")
    fcd = fcd_scan(raw / "fcd.xml")
    through_changes = lanechange_through(raw / "lanechanges.xml")
    for vid, t in through_changes.items():
        fcd["through"][vid] = min(t, fcd["through"].get(vid, t))
    e2 = detector_queue(raw / "ramp_storage_e2.xml")
    unexpected = (set(trips) | set(veh) | set().union(*fcd["observed"].values())) - set(demand)
    if unexpected:
        raise ValueError(f"Unexpected raw IDs in {arm}: {sorted(unexpected)[:5]}")
    lifecycle = []
    for c in CLASSES:
        ids = {vid for vid in demand if route_class(vid) == c}
        inserted = ids & set(veh)
        arrived = {vid for vid in inserted if "arrival" in veh[vid] and finite_number(veh[vid]["arrival"], "arrival") >= 0}
        if set(trips) & ids != inserted:
            raise ValueError(f"Tripinfo/vehroute ID mismatch in {arm}/{c}")
        pre_inserted = {vid for vid in inserted if finite_number(veh[vid]["depart"], "depart") < ACTIVATION}
        lifecycle.append({"arm": arm, "class": c, "planned": len(ids), "inserted": len(inserted),
                          "arrived": len(arrived), "unfinished": len(inserted - arrived),
                          "never_inserted": len(ids - inserted), "inserted_before_540": len(pre_inserted),
                          "inserted_before_1500": sum(finite_number(veh[vid]["depart"], "depart") < 1500 for vid in inserted),
                          "fcd_ids": len(ids & fcd["observed"][c])})
    route_rows = []
    for c in ("M", "U", "R"):
        ids = sorted(vid for vid in demand if route_class(vid) == c)
        total_external = 0.0
        total_residence_lower = 0.0
        total_loss = 0.0
        n_loss = 0
        unfinished = 0
        never_inserted = 0
        arrived_ids = {vid for vid in ids if vid in veh and "arrival" in veh[vid]
                       and finite_number(veh[vid]["arrival"], "arrival") >= 0}
        for vid in ids:
            if vid not in veh:
                # Discarded insertion has no observed wait/residence. It stays in
                # the denominator and is flagged, never imputed as zero cost.
                external = 0.0
                residence = 0.0
                never_inserted += 1
            else:
                tr = trips[vid]
                external = finite_number(tr.get("departDelay", "nan"), "departDelay")
                depart = finite_number(veh[vid]["depart"], "depart")
                arrival = finite_number(veh[vid].get("arrival", HORIZON), "arrival or horizon")
                if arrival < 0:
                    arrival = HORIZON
                residence = max(0.0, arrival - depart)
                if vid not in arrived_ids:
                    unfinished += 1
                if tr.get("timeLoss") is not None:
                    total_loss += finite_number(tr["timeLoss"], "timeLoss")
                    n_loss += 1
            total_external += external
            total_residence_lower += residence
        route_rows.append({"arm": arm, "class": c, "planned": len(ids),
                           "external_wait_lower_sum_s": total_external,
                           "network_residence_lower_sum_s": total_residence_lower,
                           "timeLoss_recorded_sum_s": total_loss, "timeLoss_records": n_loss,
                           "unfinished": unfinished, "never_inserted": never_inserted,
                           "external_wait_observed_mean_per_planned_s": total_external / len(ids) if ids else None,
                           "network_residence_observed_mean_per_planned_s": total_residence_lower / len(ids) if ids else None,
                           "system_time_lower_mean_s": (total_external + total_residence_lower) / len(ids) if ids else None,
                           "interpretation": "observed contribution per planned ID; incomplete if unfinished or never inserted; not pure spillback"})
    core = []
    for cell in CORE_CELLS:
        for b in range(HORIZON // 30):
            r = fcd["bins"][(cell, b)]
            core.append({"arm": arm, "cell": cell, "begin": 30*b, "end": 30*(b+1),
                         "window": "pre" if 30*b < ACTIVATION else "active" if 30*b < 1500 else "tail",
                         "M_samples": r["n"], "M_unique": len(r["ids"]),
                         "M_mean_speed_mps": r["speed_sum"] / r["n"] if r["n"] else None,
                         "M_mean_simultaneous_count": r["count_sum"] / 30,
                         "M_max_simultaneous_count": r["count_max"],
                         "M_density_veh_per_km": r["count_sum"] / (30 * 0.2),
                         "full_30s_labels": True})
    exposure = []
    for cutoff in (1440, 1500, 2700):
        exposure.append({"arm": arm, "cutoff_inclusive_s": cutoff,
                         "R_aux_unique": sum(t <= cutoff for t in fcd["aux"].values()),
                         "R_through_unique": sum(t <= cutoff for t in fcd["through"].values()),
                         "R_first_aux_s": min(fcd["aux"].values(), default=None),
                         "R_first_through_s": min(fcd["through"].values(), default=None),
                         "through_method": "first FCD occupancy or lanechange into merge_section_1; 1s resolution bound"})
    queue = []
    for lane in (STORAGE_LANE, INTERNAL_LANE, SHARED_LANE):
        counts = [fcd["occupancy"][(t, lane)] for t in range(HORIZON)]
        queue.append({"arm": arm, "lane": lane, "R_vehicle_seconds": sum(x["R_all"] for x in counts),
                      "R_stopped_vehicle_seconds": sum(x["R_stopped"] for x in counts),
                      "R_max_count": max(x["R_all"] for x in counts),
                      "R_max_stopped_count": max(x["R_stopped"] for x in counts),
                      "seconds_with_stopped_R": sum(x["R_stopped"] > 0 for x in counts),
                      "note": "front-lane occupation, not meter-anchored queue or physical spillback"})
    queue_bins = [{"arm": arm, **row} for row in e2]
    return {"arm": arm, "manifest": manifest, "demand": demand, "demand_sha256": digest(demand_path),
            "raw_sha256": {n: digest(raw/n) for n in ("fcd.xml", "tripinfo.xml", "vehroute.xml",
                                                       "lanechanges.xml", "ramp_storage_e2.xml")},
            "fcd": fcd, "lifecycle": lifecycle, "route": route_rows, "core": core,
            "exposure": exposure, "queue": queue, "queue_bins": queue_bins}


def compare_exogenous(runs):
    rows = []
    baseline = runs["R0"]["demand"]
    for arm in ("A", "B", "C"):
        if arm not in runs:
            continue
        d = runs[arm]["demand"]
        common = {vid for vid in baseline if route_class(vid) != "R"}
        missing = common - set(d)
        changed = {vid for vid in common & set(d) if baseline[vid] != d[vid]}
        r0_r = {vid for vid in baseline if route_class(vid) == "R"}
        rows.append({"comparison": f"R0/{arm}", "common_expected": len(common),
                     "missing_common": len(missing), "changed_common": len(changed),
                     "R0_R_count": len(r0_r)})
    a = runs["A"]["demand"]
    for arm in ("B", "C"):
        if arm not in runs:
            continue
        d = runs[arm]["demand"]
        rows.append({"comparison": f"A/{arm}", "common_expected": len(a),
                     "missing_common": len(set(a) - set(d)),
                     "changed_common": sum(a[v] != d[v] for v in set(a) & set(d)),
                     "R0_R_count": 0})
    return rows


def compare_pre(runs):
    rows = []
    for left, right in (("R0", "A"), ("A", "B"), ("A", "C")):
        if right not in runs:
            continue
        a, b = runs[left]["fcd"]["pre"], runs[right]["fcd"]["pre"]
        for c in ("M", "U", "X"):
            ka = {k for k in a if route_class(k[0]) == c}
            kb = {k for k in b if route_class(k[0]) == c}
            common = ka & kb
            exact = sum(a[k] == b[k] for k in common)
            coarse = 0
            for k in common:
                x, y = a[k], b[k]
                coarse += (x[0] != y[0] or abs(float(x[1])-float(y[1])) > 10 or
                           abs(float(x[2])-float(y[2])) > 2)
            rows.append({"comparison": f"{left}/{right}", "class": c, "left_rows": len(ka),
                         "right_rows": len(kb), "common_rows": len(common),
                         "left_only": len(ka-kb), "right_only": len(kb-ka),
                         "exact_tuple_matches": exact, "coarse_mismatch_rows": coarse,
                         "coarse_rule": "lane differs OR |pos|>10m OR |speed|>2m/s; diagnostic"})
    return rows


def compare_core(runs):
    rows = []
    for left, right in (("R0", "A"), ("A", "B"), ("B", "C")):
        if right not in runs:
            continue
        a = {(r["cell"], r["begin"]): r for r in runs[left]["core"]}
        b = {(r["cell"], r["begin"]): r for r in runs[right]["core"]}
        if set(a) != set(b):
            raise ValueError(f"Core bin coverage mismatch {left}/{right}")
        for key in sorted(a):
            x, y = a[key], b[key]
            rows.append({"comparison": f"{right}-{left}", "cell": key[0],
                         "begin": key[1], "end": x["end"], "window": x["window"],
                         "left_M_samples": x["M_samples"], "right_M_samples": y["M_samples"],
                         "left_M_unique": x["M_unique"], "right_M_unique": y["M_unique"],
                         "right_minus_left_speed_mps": (
                             y["M_mean_speed_mps"] - x["M_mean_speed_mps"]
                             if x["M_mean_speed_mps"] is not None and y["M_mean_speed_mps"] is not None else None),
                         "right_minus_left_mean_count": y["M_mean_simultaneous_count"] - x["M_mean_simultaneous_count"],
                         "right_minus_left_density_veh_per_km": y["M_density_veh_per_km"] - x["M_density_veh_per_km"]})
    return rows


def write_csv(path, rows):
    if not rows:
        raise ValueError(f"No rows for {path}")
    with path.open("x", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def run(spec_path, output):
    spec = json.loads(spec_path.read_text())
    arms = tuple(spec.get("arms", {}))
    if arms not in (ARMS[:2], ARMS[:3], ARMS):
        raise ValueError("Spec arms must be ordered R0,A then optional B,C")
    expected = spec.get("expected_counts")
    if not isinstance(expected, dict) or set(expected) != set(CLASSES):
        raise ValueError("Spec must bind expected_counts for M,R,U,X")
    runs = {}
    for arm in arms:
        entry = spec["arms"][arm]
        raw = Path(entry["raw_outputs"]).resolve()
        demand = Path(entry["demand_xml"]).resolve()
        if not raw.is_dir() or not demand.is_file():
            raise FileNotFoundError(f"Missing raw/demand for {arm}")
        runs[arm] = summarize_run(arm, raw, demand)
        counts = Counter(route_class(vid) for vid in runs[arm]["demand"])
        for c in CLASSES:
            target = 0 if arm == "R0" and c == "R" else expected[c]
            if counts[c] != target:
                raise ValueError(f"Demand count mismatch {arm}/{c}: {counts[c]} != {target}")
    exogenous = compare_exogenous(runs)
    if any(r["missing_common"] or r["changed_common"] or r["R0_R_count"] for r in exogenous):
        raise ValueError("Exogenous input mismatch; no output written")
    pre = compare_pre(runs)
    output.mkdir(parents=True, exist_ok=False)
    for name, rows in (("lifecycle", [x for arm in arms for x in runs[arm]["lifecycle"]]),
                       ("route_costs", [x for arm in arms for x in runs[arm]["route"]]),
                       ("M_core_30s", [x for arm in arms for x in runs[arm]["core"]]),
                       ("R_exposure", [x for arm in arms for x in runs[arm]["exposure"]]),
                       ("R_occupation", [x for arm in arms for x in runs[arm]["queue"]]),
                       ("ramp_storage_E2_30s", [x for arm in arms for x in runs[arm]["queue_bins"]]),
                       ("exogenous", exogenous), ("pre_R_pairability", pre),
                       ("M_core_pairwise_30s", compare_core(runs))):
        write_csv(output / f"{name}.csv", rows)
    receipt = {"status": "DESCRIPTIVE_ONLY_NO_SCIENTIFIC_DISPOSITION", "spec_sha256": digest(spec_path),
               "runs": {arm: {"raw_manifest": runs[arm]["manifest"],
                               "demand_sha256": runs[arm]["demand_sha256"],
                               "raw_sha256": runs[arm]["raw_sha256"],
                               "invalid_M_samples": len(runs[arm]["fcd"]["invalid_m"])} for arm in arms}}
    (output / "receipt.json").write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n")
    return receipt


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--spec", required=True, type=Path)
    p.add_argument("--output", required=True, type=Path)
    args = p.parse_args()
    print(json.dumps(run(args.spec, args.output), indent=2))


if __name__ == "__main__":
    main()

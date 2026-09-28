#!/usr/bin/env python3
"""Raw-bound descriptive A_OPEN/B_REBALANCED28 exploratory audit.

This script does not run SUMO or assign a scientific A/B/C disposition. It
requires separate, immutable input manifests, cards and completed raw receipts.
All windows are fixed before the revised arm is observed.
"""
from __future__ import annotations

import argparse
import csv
import json
import math
import sys
from collections import Counter, defaultdict
from pathlib import Path
import xml.etree.ElementTree as ET

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE / "fullnet_abc_analysis_20260926"))
from analyze import MAIN_LANES, detector_queue, digest, route_class  # noqa: E402
from analyze_a_outcome import core_bins, whole_window, xml_rows  # noqa: E402
from analyze_sigma0 import demand, normalized_xml, verify_card, verify_manifest  # noqa: E402
from analyze_b import verify_raw_allow_outcome_warnings  # noqa: E402

HORIZON = 2700
ACTIVATION = 540
ACTIVE_END = 1500
SLOW_MPS = 5 / 3.6  # descriptive 5 km/h queue diagnostic, not an acceptance threshold
THROUGH_LANES = {"merge_section_0", "merge_section_1", "merge_section_2"}
RAMP_LANES = {"urban_in_0", ":urban_tls_0_0", "shared_approach_0",
              "ramp_storage_0", "ramp_accel_0", ":urban_diverge_1_0",
              ":ramp_mid_0_0", ":freeway_merge_2_0"}
URBAN_LANES = {"shared_approach_0", "urban_in_0", "urban_out_0",
               ":urban_diverge_0_0", ":urban_diverge_1_0",
               ":urban_tls_0_0", ":urban_tls_1_0"}
E2_NAMES = ("ramp_storage_e2.xml", "shared_boundary_e2.xml")
RAW_REQUIRED = {"fcd.xml", "tripinfo.xml", "vehroute.xml", "lanechanges.xml",
                "sumo_summary.xml", "sumo_error.log", "tls_states.xml",
                *E2_NAMES}


def require(ok: bool, message: str) -> None:
    if not ok:
        raise ValueError(message)


def finite(value: str | None, label: str) -> float:
    try:
        number = float(value)
    except (TypeError, ValueError) as exc:
        raise ValueError(f"Missing/invalid {label}: {value}") from exc
    require(math.isfinite(number), f"Nonfinite {label}: {value}")
    return number


def normalized_add_without_ramp_program(path: Path):
    """Compare all non-ramp-program semantics, including detector positions."""
    root = ET.parse(path).getroot()
    for child in list(root):
        if child.tag == "tlLogic" and child.get("id") == "ramp_mid":
            root.remove(child)
        elif child.tag == "WAUT":
            child.set("startProg", "RAMP_INTERVENTION")

    def node(e):
        attrs = dict(e.attrib)
        for key, value in list(attrs.items()):
            if key in {"file", "dest", "value"} and ("/" in value or "\\" in value):
                attrs[key] = Path(value).name
        return e.tag, tuple(sorted(attrs.items())), tuple(node(c) for c in e)

    return node(root)


def ramp_program(path: Path, expected: str, green: int, yellow: int, red: int):
    root = ET.parse(path).getroot()
    wauts = root.findall("WAUT")
    require(len(wauts) == 1 and wauts[0].get("startProg") == expected,
            f"Wrong WAUT ramp program in {path}")
    logics = [x for x in root.findall("tlLogic")
              if x.get("id") == "ramp_mid" and x.get("programID") == expected]
    all_ramp_logics = [x for x in root.findall("tlLogic") if x.get("id") == "ramp_mid"]
    if expected == "A_OPEN":
        # A_OPEN is an existing program in the compiled, hash-bound network.
        require(not all_ramp_logics, "A_OPEN additional unexpectedly defines ramp program")
        return []
    require(len(logics) == len(all_ramp_logics) == 1,
            f"Missing/extra ramp program in additional XML for {expected}")
    phases = [(finite(x.get("duration"), "ramp phase duration"), x.get("state"))
              for x in logics[0].findall("phase")]
    require(len(phases) == 3 and [int(x[0]) for x in phases] == [green, yellow, red]
            and sum(x[0] for x in phases) == 60,
            f"Wrong ramp phase durations for {expected}: {phases}")
    require(all(state and len(state) == 1 for _, state in phases),
            "Unexpected ramp signal state width")
    require(phases[0][1].upper() == "G" and phases[1][1].lower() == "y"
            and phases[2][1].lower() == "r", f"Wrong ramp signal colors: {phases}")
    return phases


def static_gate(args, cards):
    ap = args.a_package / "A"
    bp = args.b_package / "B_REBALANCED28"
    require((ap / "demand.rou.xml").read_bytes() == (bp / "demand.rou.xml").read_bytes(),
            "A/B28 requested demand bytes differ")
    da = demand(ap / "demand.rou.xml")
    db = demand(bp / "demand.rou.xml")
    require(da == db, "A/B28 demand semantics differ")
    require(Counter(route_class(x) for x in da["vehicles"]) ==
            Counter({"M": 1396, "R": 240, "U": 150, "X": 75}),
            "Unexpected planned cohort counts")
    require(normalized_xml(ap / "scenario.sumocfg") ==
            normalized_xml(bp / "scenario.sumocfg"), "A/B28 SUMO config differs")
    require(normalized_add_without_ramp_program(ap / "scenario.add.xml") ==
            normalized_add_without_ramp_program(bp / "scenario.add.xml"),
            "A/B28 non-ramp additional semantics differ")
    ramp_program(ap / "scenario.add.xml", "A_OPEN", 60, 0, 0)
    ramp_program(bp / "scenario.add.xml", "B_REBALANCED28", 28, 3, 29)
    for field in ("network_sha256", "sumo_sha256", "routes_schema_sha256",
                  "additional_schema_sha256"):
        require(cards["A"].get(field) == cards["B_REBALANCED28"].get(field)
                and cards["A"].get(field), f"A/B28 card {field} differs or missing")
    return da


def scan_fcd(path: Path):
    """Read whole timesteps so each vehicle keeps its actual parent timestamp."""
    pre = {}
    m = {}
    first_r = {}
    early_r = defaultdict(list)
    first_down = {}
    spatial = defaultdict(lambda: {"vehicle_seconds": 0, "slow_vehicle_seconds": 0,
                                   "stopped_vehicle_seconds": 0, "unique_ids": set(),
                                   "max_simultaneous": 0})
    times = []
    observed = {c: set() for c in "MRUX"}
    for _, step in ET.iterparse(path, events=("end",)):
        if step.tag != "timestep":
            continue
        tnum = finite(step.get("time"), "FCD time")
        require(tnum == int(tnum) and 0 <= tnum < HORIZON, f"Bad FCD time {tnum}")
        t = int(tnum)
        require(t == len(times), f"Missing/repeated FCD second at {t}")
        times.append(t)
        simultaneous = Counter()
        seen_this_second = set()
        for v in step:
            if v.tag != "vehicle":
                continue
            vid = v.get("id")
            cls = route_class(vid)
            require(vid not in seen_this_second, f"Duplicate FCD vehicle-second {(vid, t)}")
            seen_this_second.add(vid)
            lane = v.get("lane")
            x = finite(v.get("x"), "FCD x")
            speed = finite(v.get("speed"), "FCD speed")
            require(not (cls == "R" and t < ACTIVATION),
                    f"R vehicle appeared before activation at t={t}: {vid}")
            observed[cls].add(vid)
            key = (vid, t)
            if t < ACTIVATION and cls in "MUX":
                require(key not in pre, f"Duplicate pre-R FCD row {key}")
                pre[key] = tuple(v.get(k) for k in ("lane", "x", "y", "pos", "speed"))
            if cls == "M":
                require(key not in m, f"Duplicate M FCD row {key}")
                require(lane in MAIN_LANES and 0 <= x <= 2200,
                        f"M FCD outside expected freeway lanes/coordinates: {key} {lane} {x}")
                m[key] = (lane, x, finite(v.get("pos"), "FCD pos"), speed)
                if lane.startswith("main_down_"):
                    first_down.setdefault(vid, t)
            elif cls == "R" and lane in THROUGH_LANES:
                first_r.setdefault(vid, t)
            if cls == "R" and t <= 630:
                early_r[t].append({"id": vid, "lane": lane, "x": x})
            if ACTIVE_END > t >= ACTIVATION and (
                cls == "R" and lane in RAMP_LANES or cls == "U" and lane in URBAN_LANES
            ):
                z = spatial[(cls, lane)]
                z["vehicle_seconds"] += 1
                z["slow_vehicle_seconds"] += speed < SLOW_MPS
                z["stopped_vehicle_seconds"] += speed < 0.1
                z["unique_ids"].add(vid)
                simultaneous[(cls, lane)] += 1
        for k, n in simultaneous.items():
            spatial[k]["max_simultaneous"] = max(spatial[k]["max_simultaneous"], n)
        step.clear()
    require(times == list(range(HORIZON)), f"FCD horizon incomplete: {len(times)} seconds")
    rows = []
    for cls, lanes in (("R", RAMP_LANES), ("U", URBAN_LANES)):
        for lane in sorted(lanes):
            z = spatial[(cls, lane)]
            rows.append({"class": cls, "lane": lane,
                         **{k: len(v) if k == "unique_ids" else v for k, v in z.items()}})
    return {"pre": pre, "m": m, "first_r": first_r, "early_r": dict(early_r), "first_down": first_down,
            "spatial": rows, "observed": observed}


def r_merge_with_lanechanges(fcd_first: dict, path: Path):
    out = dict(fcd_first)
    for _, e in ET.iterparse(path, events=("end",)):
        if e.tag != "change" or not e.get("id", "").startswith("R_flow."):
            continue
        if e.get("to") in THROUGH_LANES:
            vid = e.get("id")
            t = finite(e.get("time"), "R lanechange time")
            out[vid] = min(t, out.get(vid, t))
        e.clear()
    return out


def lifecycle(planned, raw, fcd):
    ids = set(planned["vehicles"])
    trip = xml_rows(raw / "tripinfo.xml", "tripinfo")
    veh = xml_rows(raw / "vehroute.xml", "vehicle")
    require(set(trip) <= ids and set(veh) <= ids and
            all(obs <= ids for obs in fcd["observed"].values()),
            "Unexpected raw vehicle identity")
    rows = []
    actual_pre = set()
    for cls in "MRUX":
        cids = {v for v in ids if route_class(v) == cls}
        inserted = {v for v in cids if v in veh and
                    finite(veh[v].get("depart"), "actual depart") >= 0}
        observed = fcd["observed"][cls]
        require(observed <= inserted, f"FCD {cls} identity observed without actual insertion: "
                f"{sorted(observed - inserted)[:5]}")
        missing_fcd = inserted - observed
        boundary_only = {v for v in missing_fcd
                         if finite(veh[v].get("depart"), "actual depart") >= HORIZON - 1 or
                         0 <= finite(veh[v].get("arrival", "-1"), "arrival") -
                         finite(veh[v].get("depart"), "actual depart") <= 1}
        require(missing_fcd == boundary_only,
                f"Inserted {cls} vehicles absent from FCD outside boundary case: "
                f"{sorted(missing_fcd - boundary_only)[:5]}")
        require(inserted <= set(trip), f"Missing tripinfo for inserted {cls} vehicles")
        require(not {v for v in cids if v in trip and v not in inserted and
                     finite(trip[v].get("depart", "-1"), "trip depart") >= 0},
                f"Tripinfo reports inserted {cls} vehicle missing from vehroute")
        arrived = {v for v in inserted if finite(veh[v].get("arrival", "-1"), "arrival") >= 0}
        actual_pre |= {v for v in inserted if finite(veh[v]["depart"], "depart") < ACTIVATION}
        complete = [v for v in sorted(arrived)]
        delays = [finite(trip[v].get("departDelay"), "departDelay") for v in sorted(inserted)]
        rows.append({"class": cls, "planned": len(cids), "inserted": len(inserted),
                     "observed_in_FCD": len(observed),
                     "FCD_missing_boundary_ids": sorted(boundary_only),
                     "arrived": len(arrived), "unfinished": len(inserted - arrived),
                     "never_inserted": len(cids - inserted),
                     "unfinished_ids": sorted(inserted - arrived),
                     "never_inserted_ids": sorted(cids - inserted),
                     "mean_external_depart_delay_s": sum(delays) / len(delays) if delays else None,
                     "max_external_depart_delay_s": max(delays, default=None),
                     "mean_completed_duration_s": sum(finite(trip[v].get("duration"), "duration")
                        for v in complete) / len(complete) if complete else None,
                     "mean_completed_timeLoss_s": sum(finite(trip[v].get("timeLoss"), "timeLoss")
                        for v in complete) / len(complete) if complete else None,
                     "complete_cohort_mean_available": len(complete) == len(cids)})
    return rows, veh, trip, actual_pre


def verify_pre_departures(planned, va, vb, pre_a, pre_b):
    require(pre_a == pre_b,
            f"A/B28 pre-R M/U/X FCD mismatch: A={len(pre_a)} B={len(pre_b)}")
    a_pre = {v for v in va if route_class(v) in "MUX" and
             0 <= finite(va[v].get("depart"), "depart") < ACTIVATION}
    b_pre = {v for v in vb if route_class(v) in "MUX" and
             0 <= finite(vb[v].get("depart"), "depart") < ACTIVATION}
    require(a_pre == b_pre, "A/B28 pre-R departure ID mismatch")
    for vid in sorted(a_pre):
        require(vid in planned["vehicles"], f"Unplanned pre-R vehicle {vid}")
        require(all(va[vid].get(k) == vb[vid].get(k)
                    for k in ("depart", "departLane", "departPos", "departSpeed")),
                f"A/B28 pre-R realized departure mismatch {vid}")
    return {"equal_MUX_FCD_rows": len(pre_a),
            "by_class": dict(Counter(route_class(v) for v, _ in pre_a)),
            "matching_realized_departures": len(a_pre),
            "realized_departures_by_class": dict(Counter(route_class(v) for v in a_pre))}


def tls_audit(raws):
    allrows = {}
    for arm, raw in raws.items():
        by_id = defaultdict(list)
        for _, e in ET.iterparse(raw / "tls_states.xml", events=("end",)):
            if e.tag == "tlsState":
                by_id[e.get("id")].append(dict(e.attrib))
                e.clear()
        require(set(by_id) == {"ramp_mid", "urban_tls"}, f"{arm} unexpected TLS IDs")
        for ident, rows in by_id.items():
            require([finite(z.get("time"), "TLS time") for z in rows] ==
                    list(range(HORIZON)), f"{arm} {ident} incomplete TLS seconds")
        expected = "A_OPEN" if arm == "A" else "B_REBALANCED28"
        require({r.get("programID") for r in by_id["ramp_mid"]} == {expected},
                f"{arm} wrong realized ramp program")
        if arm == "B_REBALANCED28":
            for t, row in enumerate(by_id["ramp_mid"]):
                phase = t % 60
                want = "G" if phase < 28 else "y" if phase < 31 else "r"
                require(row.get("state") == want,
                        f"B28 realized ramp state differs at t={t}: {row.get('state')} != {want}")
        allrows[arm] = by_id
    require(allrows["A"]["urban_tls"] == allrows["B_REBALANCED28"]["urban_tls"],
            "A/B28 urban TLS differs")
    out = {}
    for arm, by_id in allrows.items():
        counts = Counter(r.get("state") for r in by_id["ramp_mid"])
        expected = {"A": {"G": 2700},
                    "B_REBALANCED28": {"G": 1260, "y": 135, "r": 1305}}[arm]
        require(counts == expected, f"{arm} unexpected realized ramp TLS seconds {counts}")
        out[arm] = {"program": next(iter({r["programID"] for r in by_id["ramp_mid"]})),
                    "state_seconds": dict(counts), "urban_tls_entries": len(by_id["urban_tls"])}
    return out


def summary_audit(path):
    last = None
    n = 0
    for _, e in ET.iterparse(path, events=("end",)):
        if e.tag == "step":
            t = finite(e.get("time"), "summary time")
            require(t == n, f"Summary missing/repeated second {t}")
            last = dict(e.attrib)
            n += 1
            e.clear()
    require(n == HORIZON, f"Summary horizon incomplete: {n}")
    return {"steps": n, "last_step": last}


def compare_core(ca, cb):
    a = {(r["cell"], r["begin"]): r for r in ca}
    b = {(r["cell"], r["begin"]): r for r in cb}
    require(set(a) == set(b) and len(a) == 450, "M fixed core coverage incomplete")
    out = []
    for cell, begin in sorted(a):
        x, y = a[(cell, begin)], b[(cell, begin)]
        xs, ys = x["M_mean_speed_mps"], y["M_mean_speed_mps"]
        out.append({"cell": cell, "begin": begin, "end": x["end"],
                    "window": x["window"], "A_M_samples": x["M_samples"],
                    "B28_M_samples": y["M_samples"], "A_speed_mps": xs,
                    "B28_speed_mps": ys,
                    "B28_minus_A_speed_mps": ys - xs if xs is not None and ys is not None else None,
                    "A_simultaneous_M": x["M_mean_simultaneous_count"],
                    "B28_simultaneous_M": y["M_mean_simultaneous_count"],
                    "A_density_veh_per_km": x["M_density_veh_per_km"],
                    "B28_density_veh_per_km": y["M_density_veh_per_km"]})
    return out


def e2_rows(raws):
    out = []
    for arm, raw in raws.items():
        for detector in E2_NAMES:
            for row in detector_queue(raw / detector):
                out.append({"arm": arm, "detector": detector, **row})
    require(len(out) == 360, "E2 rows incomplete")
    return out


def paired_trip_delta(planned, left_trip, right_trip, left_veh, right_veh):
    """Only report full-cohort paired means when every planned ID arrived."""
    out = {}
    for cls in "MRUX":
        ids = sorted(v for v in planned["vehicles"] if route_class(v) == cls)
        complete = bool(ids) and all(v in left_trip and v in right_trip and v in left_veh and v in right_veh
                       and finite(left_veh[v].get("arrival", "-1"), "arrival") >= 0
                       and finite(right_veh[v].get("arrival", "-1"), "arrival") >= 0
                       for v in ids)
        if not complete:
            out[cls] = {"planned": len(ids), "complete_cohort": False,
                        "mean_B28_minus_A_duration_s": None,
                        "mean_B28_minus_A_timeLoss_s": None,
                        "mean_B28_minus_A_external_departDelay_s": None}
            continue
        def mean_difference(field):
            return sum(finite(right_trip[v].get(field), field) -
                       finite(left_trip[v].get(field), field) for v in ids) / len(ids)
        out[cls] = {"planned": len(ids), "complete_cohort": True,
                    "mean_B28_minus_A_duration_s": mean_difference("duration"),
                    "mean_B28_minus_A_timeLoss_s": mean_difference("timeLoss"),
                    "mean_B28_minus_A_external_departDelay_s": mean_difference("departDelay")}
    return out


def early_divergence(ma, mb, ra=None, rb=None):
    """Retain absence/presence and distance without a causal classification."""
    common = set(ma) & set(mb)
    different = [(vid, t) for vid, t in common if t >= ACTIVATION and ma[(vid, t)] != mb[(vid, t)]]
    first = min(different, key=lambda z: (z[1], z[0]), default=None)
    early = []
    for t in range(ACTIVATION, 631):
        keys = [key for key in common if key[1] == t]
        diff = [key for key in keys if ma[key] != mb[key]]
        early.append({"time_s": t, "common_M": len(keys), "different_common_M": len(diff),
                      "different_A_x_below_1000": sum(ma[k][1] < 1000 for k in diff),
                      "different_B28_x_below_1000": sum(mb[k][1] < 1000 for k in diff),
                      "A_only_M": sum(k[1] == t for k in set(ma) - common),
                      "B28_only_M": sum(k[1] == t for k in set(mb) - common)})
    return {"first_common_M_difference": None if first is None else {
                "id": first[0], "time_s": first[1], "A": ma[first], "B28": mb[first],
                "A_R_at_same_second": (ra or {}).get(first[1], []),
                "B28_R_at_same_second": (rb or {}).get(first[1], [])},
            "first_A_only_M_second": min((t for vid, t in set(ma) - set(mb) if t >= ACTIVATION), default=None),
            "first_B28_only_M_second": min((t for vid, t in set(mb) - set(ma) if t >= ACTIVATION), default=None),
            "early_540_630": early}


def write_csv(path: Path, rows: list[dict]):
    require(bool(rows), f"Empty output table {path}")
    with path.open("x", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def run(args):
    args.a_package = args.a_package.resolve()
    args.b_package = args.b_package.resolve()
    raws = {"A": args.a_raw.resolve(), "B_REBALANCED28": args.b_raw.resolve()}
    packages = {"A": args.a_package, "B_REBALANCED28": args.b_package}
    card_paths = {"A": args.a_card.resolve(), "B_REBALANCED28": args.b_card.resolve()}
    cards = {}
    provenance = {}
    for arm in raws:
        _, msha = verify_manifest(packages[arm])
        card, csha = verify_card(card_paths[arm], packages[arm], arm, msha, raws[arm])
        cards[arm] = card
        rawinfo = verify_raw_allow_outcome_warnings(raws[arm], csha, arm)
        require(set(rawinfo["sumo_error_lines"]) == set(), f"{arm} SUMO error log nonempty")
        require(RAW_REQUIRED <= set(json.loads((raws[arm] / "execution_receipt.json").read_text())
                                   .get("output_manifest", {})), f"{arm} missing raw output roles")
        provenance[arm] = {"input_manifest_sha256": msha, "card_sha256": csha,
                           "raw_receipt_sha256": rawinfo["receipt_sha256"],
                           "verified_raw_files": rawinfo["verified_files"],
                           "fcd_sha256": digest(raws[arm] / "fcd.xml")}
        log_warnings = []
        for name in ("stderr.log", "sumo.log"):
            if (raws[arm] / name).exists():
                log_warnings += [f"{name}: {line}" for line in
                                 (raws[arm] / name).read_text(errors="replace").splitlines()
                                 if "warning:" in line.lower()]
        provenance[arm]["warning_lines_count"] = len(log_warnings)
        provenance[arm]["warning_lines_first_10"] = log_warnings[:10]
    planned = static_gate(args, cards)
    parsed = {arm: scan_fcd(raw / "fcd.xml") for arm, raw in raws.items()}
    life = {arm: lifecycle(planned, raws[arm], parsed[arm]) for arm in raws}
    pre = verify_pre_departures(planned, life["A"][1], life["B_REBALANCED28"][1],
                                parsed["A"]["pre"], parsed["B_REBALANCED28"]["pre"])
    tls = tls_audit(raws)
    summaries = {arm: summary_audit(raw / "sumo_summary.xml") for arm, raw in raws.items()}
    rmerge = {arm: r_merge_with_lanechanges(parsed[arm]["first_r"], raw / "lanechanges.xml")
              for arm, raw in raws.items()}
    rid = {v for v in planned["vehicles"] if route_class(v) == "R"}
    require(all(set(x) <= rid and x for x in rmerge.values()), "R merge exposure absent/unexpected")
    exposure = {arm: {"first_s": min(x.values()), "unique_by_cutoff":
                {str(c): sum(t <= c for t in x.values()) for c in (1440, 1500, 2700)},
                "unique_over_horizon": len(x)} for arm, x in rmerge.items()}
    ca = core_bins({k: (*v, None, None, None, None) for k, v in parsed["A"]["m"].items()}, "A")
    cb = core_bins({k: (*v, None, None, None, None) for k, v in parsed["B_REBALANCED28"]["m"].items()},
                   "B_REBALANCED28")
    core = compare_core(ca, cb)
    e2 = e2_rows(raws)
    spatial = [{"arm": arm, **row} for arm in raws for row in parsed[arm]["spatial"]]
    diagnostic = early_divergence(parsed["A"]["m"], parsed["B_REBALANCED28"]["m"],
                                  parsed["A"]["early_r"], parsed["B_REBALANCED28"]["early_r"])
    paired = paired_trip_delta(planned, life["A"][2], life["B_REBALANCED28"][2],
                               life["A"][1], life["B_REBALANCED28"][1])
    result = {"status": "DESCRIPTIVE_EXPLORATORY_SCIENTIFIC_REVIEW_REQUIRED",
              "provenance": provenance, "planned": dict(Counter(route_class(v) for v in planned["vehicles"])),
              "pre_R_pairability": pre, "R_merge_exposure": exposure,
              "tls": tls, "summary_coverage": summaries,
              "lifecycle": {arm: life[arm][0] for arm in raws},
              "paired_complete_cohort_cost": paired,
              "M_core_fixed_windows": whole_window(ca, "A") + whole_window(cb, "B_REBALANCED28"),
              "M_first_downstream_by_cutoff": {arm: {str(c): sum(t <= c for t in parsed[arm]["first_down"].values())
                 for c in (1440, 1500, 2700)} for arm in raws},
              "E2_summary": [{"arm": arm, "detector": detector,
                  "jam_positive_bins": sum(x["max_jam_vehicles"] > 0 for x in e2
                    if x["arm"] == arm and x["detector"] == detector),
                  "max_jam_vehicles": max(x["max_jam_vehicles"] for x in e2
                    if x["arm"] == arm and x["detector"] == detector)}
                 for arm in raws for detector in E2_NAMES],
              "early_M_divergence": diagnostic,
              "measurement_notes": ["Single seed and exploratory only; no physical attribution automated.",
                  "The 5 km/h FCD slow cut and x<1000 m region are prespecified diagnostics, not acceptance thresholds.",
                  "E2 is class-agnostic; class-specific FCD reports observed lane residence, not a continuous spillback front.",
                  "Completed-trip means are unavailable as full-cohort measures if any vehicle is unfinished or never inserted."],
              "analysis_script_sha256": digest(Path(__file__))}
    out = args.output_dir.resolve()
    require(not out.exists(), f"Output path already exists: {out}")
    require(out.is_relative_to((HERE.parents[1] / "data/processed").resolve()),
            "Output must be a new path under data/processed")
    out.mkdir(parents=True, exist_ok=False)
    (out / "A_B28_SUMMARY.json").write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    write_csv(out / "M_CORE_30S.csv", core)
    write_csv(out / "E2_30S.csv", e2)
    write_csv(out / "CLASS_SPATIAL_FCD_ACTIVE.csv", spatial)
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ("a_package", "b_package", "a_card", "b_card", "a_raw", "b_raw", "output_dir"):
        parser.add_argument("--" + name.replace("_", "-"), required=True, type=Path)
    args = parser.parse_args()
    try:
        result = run(args)
    except (ValueError, KeyError, OSError, ET.ParseError) as exc:
        print(json.dumps({"status": "STOP_NOT_EVALUABLE", "reason": str(exc)}))
        raise SystemExit(2) from exc
    print(json.dumps({"status": result["status"], "output_dir": str(args.output_dir),
                      "pre_R_pairability": result["pre_R_pairability"],
                      "R_merge_exposure": result["R_merge_exposure"]}, indent=2))


if __name__ == "__main__":
    main()

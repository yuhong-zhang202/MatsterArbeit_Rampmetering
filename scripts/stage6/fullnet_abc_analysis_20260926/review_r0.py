#!/usr/bin/env python3
"""Independent R0 V2 raw integrity and descriptive pre-A eligibility review."""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
from collections import Counter, defaultdict
from pathlib import Path
import xml.etree.ElementTree as ET

from analyze import CLASSES, CORE_CELLS, HORIZON, ACTIVATION, digest, fcd_scan, parse_demand, route_class, unique_xml_rows


def count_tags(path, tag):
    count = 0
    first = last = None
    final = None
    for _, e in ET.iterparse(path, events=("end",)):
        if e.tag == tag:
            count += 1
            if first is None:
                first = dict(e.attrib)
            last = dict(e.attrib)
            final = dict(e.attrib)
            e.clear()
    return count, first, last, final


def audit(raw, demand_path, card_path):
    receipt_path = raw / "execution_receipt.json"
    receipt = json.loads(receipt_path.read_text())
    card = json.loads(card_path.read_text())
    checks = {}
    checks["card_sha"] = receipt["card_sha256"] == digest(card_path)
    checks["run_id"] = receipt["run_id"] == card["run_id"]
    checks["execution"] = receipt["status"] == "COMPLETED" and receipt["return_code"] == 0
    checks["demand_sha"] = digest(demand_path) == card["input_sha256"]["demand"]
    for name, meta in receipt["output_manifest"].items():
        p = raw / name
        checks["raw_hash:"+name] = p.is_file() and p.stat().st_size == meta["bytes"] and digest(p) == meta["sha256"]
    demand = parse_demand(demand_path)
    trips = unique_xml_rows(raw / "tripinfo.xml", "tripinfo")
    veh = unique_xml_rows(raw / "vehroute.xml", "vehicle")
    fcd = fcd_scan(raw / "fcd.xml")
    planned = set(demand)
    expected = {"M": 1396, "R": 0, "U": 150, "X": 75}
    lifecycle = []
    for c in CLASSES:
        ids = {vid for vid in planned if route_class(vid) == c}
        trip_ids = ids & set(trips)
        veh_ids = ids & set(veh)
        arrived = {vid for vid in veh_ids if "arrival" in veh[vid] and float(veh[vid]["arrival"]) >= 0}
        pre_planned = {vid for vid in ids if float(demand[vid]["depart"]) < ACTIVATION}
        pre_actual = {vid for vid in veh_ids if float(veh[vid]["depart"]) < ACTIVATION}
        delay = [float(trips[vid]["departDelay"]) for vid in trip_ids]
        row = {"class": c, "planned": len(ids), "tripinfo": len(trip_ids), "vehroute_inserted": len(veh_ids),
               "arrived": len(arrived), "unfinished": len(veh_ids-arrived), "never_inserted": len(ids-veh_ids),
               "planned_before_540": len(pre_planned), "inserted_before_540": len(pre_actual),
               "pre_planned_not_pre_inserted": len(pre_planned-pre_actual),
               "FCD_unique": len(fcd["observed"][c]), "departDelay_sum_s": sum(delay),
               "departDelay_mean_s": sum(delay)/len(delay) if delay else None,
               "departDelay_max_s": max(delay) if delay else None}
        lifecycle.append(row)
        checks["count:"+c] = len(ids) == expected[c]
        checks["lifecycle:"+c] = ids == trip_ids == veh_ids == arrived == fcd["observed"][c]
    checks["no_unexpected_raw_ids"] = not ((set(trips)|set(veh)|set().union(*fcd["observed"].values()))-planned)
    checks["FCD_2700_labels"] = True  # fcd_scan raises on missing/repeated/out-of-order seconds
    checks["no_invalid_M_lane_or_x"] = len(fcd["invalid_m"]) == 0
    detectors = {}
    for name in sorted(x.name for x in raw.glob("p1_*.xml"))+["ramp_storage_e2.xml","shared_boundary_e2.xml"]:
        n, first, last, _ = count_tags(raw/name, "interval")
        detectors[name] = {"intervals": n, "first_begin": first.get("begin") if first else None,
                           "last_end": last.get("end") if last else None}
        checks["detector:"+name] = n == 90 and first.get("begin") == "0.00" and last.get("end") == "2700.00"
    nsteps, first, last, final = count_tags(raw/"sumo_summary.xml", "step")
    summary = {"steps": nsteps, "first_time": first.get("time"), "last_time": last.get("time"),
               "final": final}
    checks["summary_2700_steps"] = nsteps == HORIZON and first.get("time") == "0.00" and last.get("time") == "2699.00"
    checks["summary_final_population"] = all(final.get(k) == v for k,v in
        {"loaded":"1621","inserted":"1621","ended":"1621","arrived":"1621","running":"0","waiting":"0","discarded":"0","collisions":"0","teleports":"0"}.items())
    error_lines = [s for s in (raw/"sumo_error.log").read_text().splitlines() if s.strip()]
    stderr_lines = [s for s in (raw/"stderr.log").read_text().splitlines() if s.strip()]
    checks["no_error_or_stderr"] = not error_lines and not stderr_lines
    checks["no_R_trajectory"] = not fcd["observed"]["R"]
    core = []
    for cell in CORE_CELLS:
        for b in range(HORIZON//30):
            x = fcd["bins"][(cell,b)]
            core.append({"cell":cell,"begin":b*30,"end":(b+1)*30,
                         "window":"pre" if b*30<540 else "active" if b*30<1500 else "tail",
                         "M_samples":x["n"],"M_unique":len(x["ids"]),
                         "M_mean_speed_mps":x["speed_sum"]/x["n"] if x["n"] else None,
                         "M_mean_simultaneous_count":x["count_sum"]/30,
                         "M_max_simultaneous_count":x["count_max"],
                         "M_density_veh_per_km":x["count_sum"]/(30*.2)})
    window_summary=[]
    for window in ("pre","active","tail"):
        rows=[r for r in core if r["window"]==window]
        nonempty=[r for r in rows if r["M_samples"]>0]
        # Vehicle-second weighted, all fixed core cells. Descriptive, not a
        # calibrated breakdown or protectable-state screen.
        total=sum(r["M_samples"] for r in nonempty)
        speed=sum(r["M_mean_speed_mps"]*r["M_samples"] for r in nonempty)/total if total else None
        window_summary.append({"window":window,"core_cell_bins":len(rows),"nonempty_bins":len(nonempty),
                               "M_samples":total,"M_sample_weighted_speed_mps":speed,
                               "minimum_populated_bin_mean_speed_mps":min((r["M_mean_speed_mps"] for r in nonempty),default=None),
                               "maximum_M_mean_simultaneous_count":max((r["M_mean_simultaneous_count"] for r in rows),default=0)})
    output = {"disposition":"READY_FOR_A_PRELAUNCH_REVIEW" if all(checks.values()) else "HOLD",
              "scope":"R0 technical/data eligibility only; no A phenomenon or clean-baseline conclusion",
              "checks":checks,"lifecycle":lifecycle,"summary":summary,"detectors":detectors,
              "errors":error_lines,"stderr":stderr_lines,"window_summary":window_summary,
              "invalid_M_examples":fcd["invalid_m"][:20],
              "provenance":{"card_sha256":digest(card_path),"demand_sha256":digest(demand_path),
                            "execution_receipt_sha256":digest(receipt_path),
                            "raw_hashes":{n:digest(raw/n) for n in receipt["output_manifest"]}}}
    return output, core


def main():
    p=argparse.ArgumentParser()
    for arg in ("raw","demand","card","output"):
        p.add_argument("--"+arg, type=Path, required=True)
    a=p.parse_args()
    result, core=audit(a.raw,a.demand,a.card)
    a.output.mkdir(parents=True, exist_ok=False)
    (a.output/"R0_REVIEW.json").write_text(json.dumps(result,indent=2,sort_keys=True)+"\n")
    with (a.output/"M_CORE_30S.csv").open("x",newline="") as f:
        w=csv.DictWriter(f,fieldnames=list(core[0]));w.writeheader();w.writerows(core)
    print(result["disposition"])
    print("failed checks",[k for k,v in result["checks"].items() if not v])


if __name__=="__main__":
    main()

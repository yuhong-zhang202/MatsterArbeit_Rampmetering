#!/usr/bin/env python3
"""Independent tabular reconciliation and source-outcome supplement for sigma0."""
from __future__ import annotations

import argparse
import csv
import json
import statistics
from pathlib import Path

from analyze import digest
from analyze_a_outcome import xml_rows


def validate(directory,raw_root):
    x=json.loads((directory/"SIGMA0_DIAGNOSTIC.json").read_text())
    rows=list(csv.DictReader((directory/"M_CORE_CONTRAST_30S.csv").open()))
    trips=list(csv.DictReader((directory/"M_TRIP_PAIRED.csv").open()))
    neg=list(csv.DictReader((directory/"NEGATIVE_CONTROL_592_605.csv").open()))
    expected={(c,t) for c in range(13,18) for t in range(0,2700,30)}
    actual={(int(r["cell"]),int(r["begin"])) for r in rows}
    if len(rows)!=450 or actual!=expected or len(actual)!=450:
        raise ValueError("Fixed cell/bin coverage mismatch")
    ids=[r["id"] for r in trips]
    if len(ids)!=1396 or len(set(ids))!=1396:
        raise ValueError("M paired-trip coverage mismatch")
    if [int(r["time_s"]) for r in neg]!=list(range(592,606)):
        raise ValueError("Negative-control seconds incomplete")
    for arm,raw in (("R0",raw_root/"R0_SIGMA0"/"outputs"),("A",raw_root/"A_SIGMA0"/"outputs")):
        if digest(raw/"execution_receipt.json")!=x["provenance"]["cards_and_raw"][arm]["receipt_sha256"]:
            raise ValueError(f"{arm} raw receipt drift")
    source={}
    rv=xml_rows(raw_root/"R0_SIGMA0"/"outputs"/"vehroute.xml","vehicle")
    av=xml_rows(raw_root/"A_SIGMA0"/"outputs"/"vehroute.xml","vehicle")
    for c in "MUX":
        common=sorted(v for v in rv if v.startswith(c+"_flow."))
        if any(v not in av for v in common):raise ValueError(f"Missing A {c} source identity")
        source[c]={"n":len(common)}
        for field in ("depart","departLane","departPos","departSpeed"):
            source[c]["different_"+field+"_ids"]=sum(rv[v].get(field)!=av[v].get(field) for v in common)
    cell=[]
    for c in range(13,18):
        z=[r for r in rows if int(r["cell"])==c and r["window"]=="active"]
        if len(z)!=32:raise ValueError(f"Cell {c} missing active 30s bin")
        n0=sum(int(r["R0_M_samples"]) for r in z);n1=sum(int(r["A_M_samples"]) for r in z)
        s0=sum(float(r["R0_mean_speed_mps"])*int(r["R0_M_samples"]) for r in z if r["R0_mean_speed_mps"])/n0
        s1=sum(float(r["A_mean_speed_mps"])*int(r["A_M_samples"]) for r in z if r["A_mean_speed_mps"])/n1
        cell.append({"cell":c,"active_bins":32,"negative_speed_bins":sum(float(r["A_minus_R0_speed_mps"])<0 for r in z),
                     "R0_M_samples":n0,"A_M_samples":n1,"R0_weighted_speed_mps":s0,"A_weighted_speed_mps":s1,
                     "A_minus_R0_speed_mps":s1-s0,
                     "mean_simultaneous_M_delta":statistics.mean(float(r["A_minus_R0_mean_count"]) for r in z)})
    negsummary=[{"time_s":int(r["time_s"]),"different_M":int(r["different_M"]),
                 "different_M_x_below_1000m":int(r["different_M_x_below_1000m"]),
                 "different_M_x_below_1400m":int(r["different_M_x_below_1400m"])} for r in neg]
    original=x["default_V2_reference"]["negative_control"]
    return {"status":"PASS_DERIVED_COVERAGE_AND_SOURCE_RECONCILIATION",
            "coverage":{"fixed_cell_bin_rows":len(rows),"M_paired_trips":len(trips),"negative_control_seconds":len(neg)},
            "source_realization_differences":source,"active_cell":cell,
            "sigma0_negative_control":negsummary,
            "default_negative_control_at_599":next(r for r in original if r["time_s"]==599),
            "sigma0_negative_control_at_599":next(r for r in negsummary if r["time_s"]==599),
            "provenance":{"diagnostic_sha256":digest(directory/"SIGMA0_DIAGNOSTIC.json"),
                          "core_csv_sha256":digest(directory/"M_CORE_CONTRAST_30S.csv"),
                          "trip_csv_sha256":digest(directory/"M_TRIP_PAIRED.csv"),
                          "negative_csv_sha256":digest(directory/"NEGATIVE_CONTROL_592_605.csv"),
                          "analysis_code_sha256":digest(Path(__file__))}}


def main():
    p=argparse.ArgumentParser();p.add_argument("--outcome-dir",type=Path,required=True);p.add_argument("--raw-root",type=Path,required=True)
    a=p.parse_args();x=validate(a.outcome_dir,a.raw_root)
    with (a.outcome_dir/"OUTCOME_VALIDATION.json").open("x") as f:f.write(json.dumps(x,indent=2,sort_keys=True)+"\n")
    print(json.dumps({k:x[k] for k in ("coverage","source_realization_differences","active_cell","sigma0_negative_control_at_599")},indent=2))


if __name__=="__main__":main()

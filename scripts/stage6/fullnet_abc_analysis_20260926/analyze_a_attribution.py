#!/usr/bin/env python3
"""Descriptive spatial exposure audit for the new, phase-1-passed R0/A pair.

Exposure groups use R0 mainline trajectories against A ramp trajectories. This
avoids defining a cohort from the A mainline outcome, but still is not a
randomized or mechanistic mediation analysis. No distance cut is an official
phenomenon threshold.
"""
from __future__ import annotations

import argparse
import csv
import json
import statistics
from collections import defaultdict
from pathlib import Path
import xml.etree.ElementTree as ET

from analyze import digest
from analyze_a_outcome import xml_rows

MERGE_X = (1400.0, 1700.0)
CORE_CELLS = (14, 15)


def load_fcd(path, include_r):
    m = {}
    r_by_time = defaultdict(list)
    labels = []
    for _, step in ET.iterparse(path, events=("end",)):
        if step.tag != "timestep":
            continue
        t = int(float(step.get("time")))
        if labels and t != labels[-1] + 1:
            raise ValueError(f"Nonconsecutive FCD labels in {path}: {t}")
        labels.append(t)
        for v in step:
            vid = v.get("id", "")
            x = float(v.get("x"))
            if vid.startswith("M_flow."):
                key = (vid, t)
                if key in m:
                    raise ValueError(f"Duplicate M FCD: {key}")
                m[key] = (x, float(v.get("speed")), v.get("lane"))
            elif include_r and vid.startswith("R_flow.") and MERGE_X[0] <= x < MERGE_X[1]:
                r_by_time[t].append((vid, x, v.get("lane")))
        step.clear()
    if labels != list(range(2700)):
        raise ValueError(f"Incomplete FCD labels in {path}: {len(labels)}")
    return m, r_by_time


def exposure(r0_m, a_r):
    """Minimum same-second longitudinal gap within merge x, per R0 M ID."""
    out = {}
    for (vid, t), (x, speed, lane) in r0_m.items():
        if not MERGE_X[0] <= x < MERGE_X[1] or t < 540:
            continue
        for rid, rx, rlane in a_r.get(t, ()):
            gap = x - rx
            prior = out.get(vid)
            if prior is None or abs(gap) < abs(prior["signed_gap_m"]):
                out[vid] = {"min_abs_gap_m": abs(gap), "signed_gap_m": gap,
                            "time_s": t, "R_id": rid, "R_lane": rlane,
                            "R0_M_x_m": x, "A_R_x_m": rx}
    return out


def exposure_group(vid, exp):
    if vid not in exp:
        return "no_simultaneous_R_in_merge"
    gap = exp[vid]["min_abs_gap_m"]
    if gap <= 50:
        return "R_within_50m"
    if gap <= 100:
        return "R_50_to_100m"
    if gap <= 200:
        return "R_100_to_200m"
    return "R_over_200m"


def coarse_exposure_group(vid, exp):
    if vid not in exp:
        return "no_simultaneous_R_in_merge"
    return "R_within_50m" if exp[vid]["min_abs_gap_m"]<=50 else "R_over_50m"


def summarize(ids, trip0, tripa, veh0, veha, m0, ma, exp):
    rows = []
    for vid in ids:
        x0, xa = trip0[vid], tripa[vid]
        v0, va = veh0[vid], veha[vid]
        ex = exp.get(vid, {})
        rows.append({"id":vid,"exposure_group":exposure_group(vid,exp),
                     "coarse_exposure_group":coarse_exposure_group(vid,exp),
                     "min_abs_gap_m":ex.get("min_abs_gap_m"),
                     "nearest_gap_s":ex.get("time_s"),
                     "nearest_R_id":ex.get("R_id"),
                     "nearest_signed_gap_m":ex.get("signed_gap_m"),
                     "R0_depart_s":float(x0["depart"]),
                     "A_depart_s":float(xa["depart"]),
                     "same_realized_source_lane_speed":v0.get("departLane")==va.get("departLane") and v0.get("departSpeed")==va.get("departSpeed"),
                     "duration_delta_s":float(xa["duration"])-float(x0["duration"]),
                     "timeLoss_delta_s":float(xa["timeLoss"])-float(x0["timeLoss"]),
                     "R0_arrival_s":float(x0["arrival"]),
                     "A_arrival_s":float(xa["arrival"])})
    return rows


def sample_speed(m, group_by_id, cell, begin=540, end=1500):
    vals = defaultdict(list)
    for (vid,t),(x,speed,lane) in m.items():
        if begin <= t < end and int(x//100)==cell:
            vals[group_by_id[vid]].append(speed)
    return {g:{"samples":len(v),"mean_speed_mps":statistics.mean(v)} for g,v in vals.items()}


def same_sample_delta(m0,ma,group_by_id,cell):
    vals = defaultdict(list)
    for (vid,t), (x0,s0,l0) in m0.items():
        if not 540 <= t < 1500 or int(x0//100)!=cell:
            continue
        other = ma.get((vid,t))
        if other is None:
            continue
        x1,s1,l1=other
        if int(x1//100)==cell and l0==l1:
            vals[group_by_id[vid]].append(s1-s0)
    return {g:{"paired_samples":len(v),"mean_A_minus_R0_speed_mps":statistics.mean(v)} for g,v in vals.items()}


def first_difference_by_spatial_relation(m0,ma,a_r):
    different=[]
    for key in set(m0)&set(ma):
        vid,t=key
        if t>=540 and m0[key]!=ma[key]:
            different.append((t,vid))
    t,vid=min(different)
    x0,s0,l0=m0[(vid,t)];x1,s1,l1=ma[(vid,t)]
    nearest=sorted(((abs(x1-rx),x1-rx,rid,rx,rlane) for rid,rx,rlane in a_r.get(t,())),key=lambda z:z[0])
    return {"id":vid,"time_s":t,"R0_M":{"x_m":x0,"speed_mps":s0,"lane":l0},
            "A_M":{"x_m":x1,"speed_mps":s1,"lane":l1},
            "nearest_A_R_within_merge":nearest[0] if nearest else None}


def early_divergence(m0,ma,a_r,exp):
    first={}
    for key in set(m0)&set(ma):
        vid,t=key
        if t<540 or m0[key]==ma[key]:
            continue
        if vid not in first or t<first[vid]:
            first[vid]=t
    out=[]
    for vid,t in sorted(first.items(),key=lambda x:(x[1],x[0])):
        if t>630:
            break
        x=ma[(vid,t)][0]
        near=min(((abs(x-rx),x-rx,rid) for rid,rx,_ in a_r.get(t,())),default=None)
        out.append({"id":vid,"first_difference_s":t,"A_M_x_m":x,
                    "nearest_R_gap_at_first_difference_m":near[1] if near else None,
                    "nearest_R_id":near[2] if near else None,
                    "eventual_R0_spacetime_exposure_group":exposure_group(vid,exp)})
    return out


def early_frame_divergence(m0,ma):
    out=[]
    for t in range(592,606):
        changed=[(vid,m0[(vid,t)],ma[(vid,t)]) for vid,time in set(m0)&set(ma)
                 if time==t and m0[(vid,t)]!=ma[(vid,t)]]
        out.append({"time_s":t,"different_common_M":len(changed),
                    "R0_M_x_below_1000m":sum(x0[0]<1000 for _,x0,_ in changed),
                    "R0_M_x_below_1400m":sum(x0[0]<1400 for _,x0,_ in changed),
                    "different_speed_n":sum(x0[1]!=xa[1] for _,x0,xa in changed),
                    "different_lane_n":sum(x0[2]!=xa[2] for _,x0,xa in changed)})
    return out


def main():
    p=argparse.ArgumentParser()
    p.add_argument("--r0-raw",type=Path,required=True)
    p.add_argument("--a-raw",type=Path,required=True)
    p.add_argument("--phase1",type=Path,required=True)
    p.add_argument("--output-dir",type=Path,required=True)
    a=p.parse_args()
    gate=json.loads(a.phase1.read_text())
    if gate["disposition"]!="PASS_PHASE1_PAIRABILITY_AND_EXPOSURE":
        raise ValueError("Phase1 not released")
    for raw,key in ((a.r0_raw,"R0_raw_hashes"),(a.a_raw,"A_raw_hashes")):
        for name,sha in gate["provenance"][key].items():
            if digest(raw/name)!=sha:
                raise ValueError(f"Raw hash mismatch: {raw/name}")
    m0,_=load_fcd(a.r0_raw/"fcd.xml",False)
    ma,ar=load_fcd(a.a_raw/"fcd.xml",True)
    exp=exposure(m0,ar)
    t0=xml_rows(a.r0_raw/"tripinfo.xml","tripinfo")
    ta=xml_rows(a.a_raw/"tripinfo.xml","tripinfo")
    v0=xml_rows(a.r0_raw/"vehroute.xml","vehicle")
    va=xml_rows(a.a_raw/"vehroute.xml","vehicle")
    ids=sorted(x for x in t0 if x.startswith("M_flow."))
    if len(ids)!=1396 or set(ids)!={x for x in ta if x.startswith("M_flow.")}:
        raise ValueError("M trip coverage failed")
    if any(x not in v0 or x not in va for x in ids):
        raise ValueError("M vehroute coverage failed")
    rows=summarize(ids,t0,ta,v0,va,m0,ma,exp)
    groups={x["id"]:x["exposure_group"] for x in rows}
    coarse_groups={x["id"]:x["coarse_exposure_group"] for x in rows}
    summary=[]
    for g in sorted(set(groups.values())):
        for source in ("all","same_source_lane_speed"):
            selected=[x for x in rows if x["exposure_group"]==g and (source=="all" or x["same_realized_source_lane_speed"])]
            if not selected:
                continue
            summary.append({"group":g,"source_subset":source,"n":len(selected),
                            "mean_duration_delta_s":statistics.mean(x["duration_delta_s"] for x in selected),
                            "sum_duration_delta_s":sum(x["duration_delta_s"] for x in selected),
                            "mean_timeLoss_delta_s":statistics.mean(x["timeLoss_delta_s"] for x in selected),
                            "duration_worse_n":sum(x["duration_delta_s"]>0 for x in selected),
                            "duration_better_n":sum(x["duration_delta_s"]<0 for x in selected),
                            "M_depart_before_540_n":sum(x["R0_depart_s"]<540 for x in selected)})
    core=[]
    for cell in CORE_CELLS:
        s0=sample_speed(m0,groups,cell);sa=sample_speed(ma,groups,cell)
        paired=same_sample_delta(m0,ma,groups,cell)
        for g in sorted(set(groups.values())):
            x=s0.get(g,{});y=sa.get(g,{});z=paired.get(g,{})
            core.append({"cell":cell,"group":g,"R0_samples":x.get("samples",0),"A_samples":y.get("samples",0),
                         "R0_mean_speed_mps":x.get("mean_speed_mps"),"A_mean_speed_mps":y.get("mean_speed_mps"),
                         "A_minus_R0_speed_mps":y["mean_speed_mps"]-x["mean_speed_mps"] if x and y else None,
                         **z})
    coarse_summary=[]
    for g in ("R_within_50m","R_over_50m","no_simultaneous_R_in_merge"):
        for departure in ("all","actual_depart_ge_540","actual_depart_ge_592"):
            for source in ("all","same_source_lane_speed"):
                selected=[x for x in rows if x["coarse_exposure_group"]==g
                          and (departure=="all" or x["R0_depart_s"]>=int(departure.rsplit("_",1)[1]))
                          and (source=="all" or x["same_realized_source_lane_speed"])]
                if selected:
                    coarse_summary.append({"group":g,"departure_subset":departure,"source_subset":source,
                                           "n":len(selected),
                                           "mean_duration_delta_s":statistics.mean(x["duration_delta_s"] for x in selected),
                                           "sum_duration_delta_s":sum(x["duration_delta_s"] for x in selected),
                                           "mean_timeLoss_delta_s":statistics.mean(x["timeLoss_delta_s"] for x in selected),
                                           "duration_worse_n":sum(x["duration_delta_s"]>0 for x in selected),
                                           "duration_better_n":sum(x["duration_delta_s"]<0 for x in selected)})
    coarse_core=[]
    for cell in CORE_CELLS:
        s0=sample_speed(m0,coarse_groups,cell);sa=sample_speed(ma,coarse_groups,cell)
        paired=same_sample_delta(m0,ma,coarse_groups,cell)
        for g in ("R_within_50m","R_over_50m","no_simultaneous_R_in_merge"):
            x=s0.get(g,{});y=sa.get(g,{});z=paired.get(g,{})
            coarse_core.append({"cell":cell,"group":g,"R0_samples":x.get("samples",0),"A_samples":y.get("samples",0),
                                "R0_mean_speed_mps":x.get("mean_speed_mps"),"A_mean_speed_mps":y.get("mean_speed_mps"),
                                "A_minus_R0_speed_mps":y["mean_speed_mps"]-x["mean_speed_mps"] if x and y else None,
                                **z})
    out={"design":{"classification":"R0 M against A R, same integer second, longitudinal x in [1400,1700) m",
                   "distance_bands_m":[50,100,200],"analysis_window_s":[540,1500],
                   "threshold_status":"diagnostic bands only; not official phenomenon criteria"},
         "coverage":{"R0_M_FCD_rows":len(m0),"A_M_FCD_rows":len(ma),"A_R_merge_timepoints":sum(len(v) for v in ar.values()),
                     "M_trip_ids":len(ids),"M_with_simultaneous_R":len(exp)},
         "first_M_difference":first_difference_by_spatial_relation(m0,ma,ar),
         "early_first_differences_through_630_s":early_divergence(m0,ma,ar,exp),
         "early_frame_differences_592_to_605_s":early_frame_divergence(m0,ma),
         "M495_exposure":exp.get("M_flow.495"),
         "cohorts":summary,"core_cells":core,"coarse_cohorts":coarse_summary,"coarse_core_cells":coarse_core,
         "provenance":{"phase1_sha256":digest(a.phase1),"R0_fcd_sha256":digest(a.r0_raw/"fcd.xml"),
                       "A_fcd_sha256":digest(a.a_raw/"fcd.xml"),
                       "R0_tripinfo_sha256":digest(a.r0_raw/"tripinfo.xml"),"A_tripinfo_sha256":digest(a.a_raw/"tripinfo.xml")}}
    a.output_dir.mkdir(parents=True,exist_ok=False)
    (a.output_dir/"ATTRIBUTION_DIAGNOSTICS.json").write_text(json.dumps(out,indent=2,sort_keys=True)+"\n")
    for name,data in (("M_COHORTS.csv",rows),("M_GROUP_SUMMARY.csv",summary),("CORE_GROUPS.csv",core),
                      ("M_COARSE_SUMMARY.csv",coarse_summary),("CORE_COARSE_GROUPS.csv",coarse_core)):
        with (a.output_dir/name).open("x",newline="") as f:
            w=csv.DictWriter(f,fieldnames=list(data[0]));w.writeheader();w.writerows(data)
    print(json.dumps({"coverage":out["coverage"],"first":out["first_M_difference"],
                      "coarse_cohorts":coarse_summary,"coarse_core":coarse_core,
                      "early_first_differences_through_630_s":out["early_first_differences_through_630_s"]},indent=2))


if __name__=="__main__":
    main()

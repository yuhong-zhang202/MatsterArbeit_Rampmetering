#!/usr/bin/env python3
"""Versioned supplement: source, spatial persistence, R exposure and U/R costs."""
from __future__ import annotations

import argparse
import csv
import json
import statistics
from collections import Counter
from pathlib import Path
import xml.etree.ElementTree as ET

from analyze import digest


def rows(path,tag):
    d={}
    for _,e in ET.iterparse(path,events=("end",)):
        if e.tag==tag:
            d[e.get("id")]=dict(e.attrib);e.clear()
    return d


def first_m_difference(r0,a):
    def load(path):
        out={}
        for _,step in ET.iterparse(path,events=("end",)):
            if step.tag!="timestep":continue
            t=int(float(step.get("time")))
            if t<540:step.clear();continue
            for v in step:
                if v.get("id","").startswith("M_flow."):
                    out[(v.get("id"),t)]={k:v.get(k) for k in ("lane","x","y","pos","speed")}
            step.clear()
        return out
    x=load(r0);y=load(a)
    for key in sorted(set(x)&set(y),key=lambda z:(z[1],z[0])):
        if x[key]!=y[key]:
            return {"id":key[0],"time_s":key[1],"R0":x[key],"A":y[key]}
    return None


def source_differences(r0,a):
    out=[]
    common=set(r0)&set(a)
    for c in "MUX":
        ids={v for v in common if v.startswith(c+"_flow.")}
        for field in ("depart","departLane","departPos","departSpeed","speedFactor"):
            changed=[v for v in ids if r0[v].get(field)!=a[v].get(field)]
            first=min(changed,key=lambda v:float(r0[v]["depart"])) if changed else None
            out.append({"class":c,"field":field,"different_ids":len(changed),
                        "first_different_id":first,"first_actual_depart_s":float(r0[first]["depart"]) if first else None,
                        "first_R0_value":r0[first].get(field) if first else None,
                        "first_A_value":a[first].get(field) if first else None})
    return out


def class_costs(trips,arm):
    out=[]
    for c in "RUX":
        x=[r for v,r in trips.items() if v.startswith(c+"_flow.")]
        if not x:continue
        out.append({"arm":arm,"class":c,"n":len(x),
                    "departDelay_mean_s":statistics.mean(float(r["departDelay"]) for r in x),
                    "duration_mean_s":statistics.mean(float(r["duration"]) for r in x),
                    "timeLoss_mean_s":statistics.mean(float(r["timeLoss"]) for r in x),
                    "waitingTime_mean_s":statistics.mean(float(r["waitingTime"]) for r in x)})
    return out


def spatial_persistence(contrast):
    out=[]
    for cell in range(13,18):
        x=[r for r in contrast if int(r["cell"])==cell and r["window"]=="active"]
        x.sort(key=lambda r:int(r["begin"]))
        negative=[bool(r["A_minus_R0_speed_mps"]) and float(r["A_minus_R0_speed_mps"])<0 for r in x]
        spans=[];start=None
        for i,flag in enumerate(negative+[False]):
            if flag and start is None:start=i
            if not flag and start is not None:
                spans.append((int(x[start]["begin"]),int(x[i-1]["end"]),i-start));start=None
        n0=sum(int(r["R0_M_samples"]) for r in x)
        n1=sum(int(r["A_M_samples"]) for r in x)
        s0=sum(float(r["R0_mean_speed_mps"])*int(r["R0_M_samples"]) for r in x)/n0
        s1=sum(float(r["A_mean_speed_mps"])*int(r["A_M_samples"]) for r in x)/n1
        out.append({"cell":cell,"active_bins":len(x),"negative_direction_bins":sum(negative),
                    "nonnegative_bins":len(x)-sum(negative),"longest_negative_run_bins":max((z[2] for z in spans),default=0),
                    "negative_spans_s":spans,"R0_M_samples":n0,"A_M_samples":n1,
                    "R0_weighted_speed_mps":s0,"A_weighted_speed_mps":s1,
                    "A_minus_R0_weighted_speed_mps":s1-s0,
                    "mean_count_delta":statistics.mean(float(r["A_minus_R0_mean_count"]) for r in x)})
    return out


def first_r_through_by_bin(a_raw):
    # FCD or lanechange, same entry definition as phase-1; no detector E1 proxy.
    first={}
    for _,step in ET.iterparse(a_raw/"fcd.xml",events=("end",)):
        if step.tag!="timestep":continue
        t=int(float(step.get("time")))
        for v in step:
            if v.get("id","").startswith("R_flow.") and v.get("lane")=="merge_section_1":
                first.setdefault(v.get("id"),t)
        step.clear()
    for _,e in ET.iterparse(a_raw/"lanechanges.xml",events=("end",)):
        if e.tag=="change" and e.get("id","").startswith("R_flow.") and e.get("to")=="merge_section_1":
            vid=e.get("id");t=float(e.get("time"));first[vid]=min(t,first.get(vid,t));e.clear()
    bins=Counter(int(t//30)*30 for t in first.values())
    return [{"begin":t,"end":t+30,"new_unique_R_through":bins[t],
             "cumulative_unique_R_through":sum(n for b,n in bins.items() if b<=t)} for t in range(0,2700,30)]


def detector_summary(raw):
    out=[]
    for name in ("ramp_storage_e2.xml","shared_boundary_e2.xml"):
        rows=[]
        for _,e in ET.iterparse(raw/name,events=("end",)):
            if e.tag=="interval":rows.append(dict(e.attrib));e.clear()
        out.append({"detector":name,"intervals":len(rows),
                    "max_jam_m":max(float(r["maxJamLengthInMeters"]) for r in rows),
                    "max_jam_vehicles":max(int(r["maxJamLengthInVehicles"]) for r in rows),
                    "intervals_with_jam":sum(int(r["maxJamLengthInVehicles"])>0 for r in rows),
                    "max_occupancy_pct":max(float(r["maxOccupancy"]) for r in rows)})
    return out


def main():
    p=argparse.ArgumentParser()
    for n in ("r0_raw","a_raw","contrast","phase1","output"):
        p.add_argument("--"+n.replace("_","-"),type=Path,required=True)
    a=p.parse_args();gate=json.loads(a.phase1.read_text())
    if gate["disposition"]!="PASS_PHASE1_PAIRABILITY_AND_EXPOSURE":raise ValueError("Phase1 not released")
    for raw,k in ((a.r0_raw,"R0_raw_hashes"),(a.a_raw,"A_raw_hashes")):
        if any(digest(raw/n)!=h for n,h in gate["provenance"][k].items()):raise ValueError("Raw changed")
    rveh=rows(a.r0_raw/"vehroute.xml","vehicle");aveh=rows(a.a_raw/"vehroute.xml","vehicle")
    rt=rows(a.r0_raw/"tripinfo.xml","tripinfo");at=rows(a.a_raw/"tripinfo.xml","tripinfo")
    contrast=list(csv.DictReader(a.contrast.open()))
    result={"source_differences":source_differences(rveh,aveh),
            "first_M_FCD_difference":first_m_difference(a.r0_raw/"fcd.xml",a.a_raw/"fcd.xml"),
            "R0_other_class_costs":class_costs(rt,"R0"),"A_other_class_costs":class_costs(at,"A"),
            "active_core_spatial":spatial_persistence(contrast),
            "R0_E2":detector_summary(a.r0_raw),"A_E2":detector_summary(a.a_raw),
            "provenance":{"phase1_sha256":digest(a.phase1),"contrast_sha256":digest(a.contrast)}}
    a.output.write_text(json.dumps(result,indent=2,sort_keys=True)+"\n")
    with (a.output.parent/"R_THROUGH_30S.csv").open("x",newline="") as f:
        exposure_rows=first_r_through_by_bin(a.a_raw)
        w=csv.DictWriter(f,fieldnames=list(exposure_rows[0]));w.writeheader();w.writerows(exposure_rows)
    print(json.dumps({"first_M":result["first_M_FCD_difference"],"spatial":result["active_core_spatial"]},indent=2))


if __name__=="__main__":main()

#!/usr/bin/env python3
"""Fixed-window new R0/A outcome audit after the independent phase-1 release.

Descriptive only. Never uses the historical nonpairable A or old R0.
"""
from __future__ import annotations

import argparse
import csv
import json
import statistics
from collections import Counter, defaultdict
from pathlib import Path
import xml.etree.ElementTree as ET

from analyze import MAIN_LANES, CORE_CELLS, HORIZON, digest, parse_demand, route_class

CORE_BIN = 30
ACTIVATION = 540
DEMAND_END = 1500


def xml_rows(path, tag):
    rows = {}
    for _, e in ET.iterparse(path, events=("end",)):
        if e.tag == tag:
            vid = e.get("id")
            if vid in rows:
                raise ValueError(f"Duplicate {tag} {vid}")
            rows[vid] = dict(e.attrib)
            e.clear()
    return rows


def load_fcd(path):
    """All classes retained only for same-time provenance/source checks."""
    by_class = {c:{} for c in "MRUX"}
    seen = []
    invalid_m = []
    first_down = {}
    first_through_r = {}
    for _, step in ET.iterparse(path, events=("end",)):
        if step.tag != "timestep":
            continue
        t = float(step.get("time"))
        if t != int(t) or not 0 <= t < HORIZON:
            raise ValueError(f"Bad FCD time {t}")
        t = int(t)
        if seen and t != seen[-1]+1:
            raise ValueError(f"Missing/repeated FCD second at {t}")
        seen.append(t)
        for e in step:
            if e.tag != "vehicle":
                continue
            vid = e.get("id")
            c = route_class(vid)
            lane = e.get("lane")
            row = (lane, float(e.get("x")), float(e.get("pos")), float(e.get("speed")),
                   e.get("x"), e.get("y"), e.get("pos"), e.get("speed"))
            key = (vid,t)
            if key in by_class[c]:
                raise ValueError(f"Duplicate FCD key {key}")
            by_class[c][key] = row
            if c == "M":
                if lane not in MAIN_LANES or not 0 <= row[1] <= 2200:
                    invalid_m.append((vid,t,lane,row[1]))
                if lane.startswith("main_down_"):
                    first_down.setdefault(vid,t)
            if c == "R" and lane == "merge_section_1":
                first_through_r.setdefault(vid,t)
        step.clear()
    if seen != list(range(HORIZON)):
        raise ValueError(f"Expected 2700 FCD seconds, got {len(seen)}")
    return by_class, invalid_m, first_down, first_through_r


def core_bins(mrows, arm):
    bins = defaultdict(lambda:{"n":0,"speed_sum":0.0,"ids":set(),"count_sum":0,"count_max":0})
    counts = Counter()
    for (vid,t),v in mrows.items():
        if v[0] not in MAIN_LANES or not 0 <= v[1] <= 2200:
            continue
        cell = min(int(v[1]//100),21)
        if cell not in CORE_CELLS:
            continue
        b=t//CORE_BIN
        x=bins[(cell,b)]
        x["n"]+=1;x["speed_sum"]+=v[3];x["ids"].add(vid)
        counts[(cell,t)]+=1
    out=[]
    for cell in CORE_CELLS:
        for b in range(HORIZON//CORE_BIN):
            x=bins[(cell,b)]
            simult=[counts[(cell,t)] for t in range(b*CORE_BIN,(b+1)*CORE_BIN)]
            count_sum=sum(simult)
            out.append({"arm":arm,"cell":cell,"begin":b*CORE_BIN,"end":(b+1)*CORE_BIN,
                        "window":"pre" if b*CORE_BIN<ACTIVATION else "active" if b*CORE_BIN<DEMAND_END else "tail",
                        "M_samples":x["n"],"M_unique":len(x["ids"]),
                        "M_mean_speed_mps":x["speed_sum"]/x["n"] if x["n"] else None,
                        "M_mean_simultaneous_count":count_sum/CORE_BIN,
                        "M_max_simultaneous_count":max(simult),
                        "M_density_veh_per_km":count_sum/(CORE_BIN*.2)})
    return out


def compare_bins(r0,a):
    x={(r["cell"],r["begin"]):r for r in r0}
    y={(r["cell"],r["begin"]):r for r in a}
    if set(x)!=set(y):
        raise ValueError("Core coverage differs")
    out=[]
    for key in sorted(x):
        l,r=x[key],y[key]
        out.append({"cell":key[0],"begin":key[1],"end":l["end"],"window":l["window"],
                    "R0_M_samples":l["M_samples"],"A_M_samples":r["M_samples"],
                    "R0_M_unique":l["M_unique"],"A_M_unique":r["M_unique"],
                    "R0_mean_speed_mps":l["M_mean_speed_mps"],"A_mean_speed_mps":r["M_mean_speed_mps"],
                    "A_minus_R0_speed_mps":r["M_mean_speed_mps"]-l["M_mean_speed_mps"] if l["M_samples"] and r["M_samples"] else None,
                    "R0_mean_count":l["M_mean_simultaneous_count"],"A_mean_count":r["M_mean_simultaneous_count"],
                    "A_minus_R0_mean_count":r["M_mean_simultaneous_count"]-l["M_mean_simultaneous_count"],
                    "R0_density_veh_per_km":l["M_density_veh_per_km"],"A_density_veh_per_km":r["M_density_veh_per_km"],
                    "A_minus_R0_density_veh_per_km":r["M_density_veh_per_km"]-l["M_density_veh_per_km"]})
    return out


def whole_window(core, arm):
    rows=[]
    for window in ("pre","active","tail"):
        a=[r for r in core if r["window"]==window]
        n=sum(r["M_samples"] for r in a)
        rows.append({"arm":arm,"window":window,"fixed_cell_bins":len(a),
                     "populated_cell_bins":sum(r["M_samples"]>0 for r in a),
                     "M_samples":n,
                     "M_vehicle_second_weighted_speed_mps":sum(r["M_mean_speed_mps"]*r["M_samples"] for r in a if r["M_samples"])/n if n else None,
                     "M_mean_simultaneous_population_over_cells":sum(r["M_mean_simultaneous_count"] for r in a)/len(a)})
    return rows


def paired_trip_metrics(rt,at,planned):
    mids=sorted(v for v in planned if route_class(v)=="M")
    rows=[]
    for vid in mids:
        x,y=rt[vid],at[vid]
        if any(k not in x or k not in y for k in ("depart","arrival","duration","timeLoss")):
            raise ValueError(f"Incomplete M trip {vid}")
        rows.append({"id":vid,"planned_depart_s":float(planned[vid]["depart"]),
                     "R0_actual_depart_s":float(x["depart"]),"A_actual_depart_s":float(y["depart"]),
                     "R0_duration_s":float(x["duration"]),"A_duration_s":float(y["duration"]),
                     "A_minus_R0_duration_s":float(y["duration"])-float(x["duration"]),
                     "R0_timeLoss_s":float(x["timeLoss"]),"A_timeLoss_s":float(y["timeLoss"]),
                     "A_minus_R0_timeLoss_s":float(y["timeLoss"])-float(x["timeLoss"])})
    return rows


def summarize_trips(rows):
    out=[]
    for name, subset in (("all",rows),("desired_pre540",[r for r in rows if r["planned_depart_s"]<540]),
                         ("desired_540_1500",[r for r in rows if 540<=r["planned_depart_s"]<1500])):
        out.append({"cohort":name,"n":len(subset),
                    "R0_duration_mean_s":statistics.mean(r["R0_duration_s"] for r in subset),
                    "A_duration_mean_s":statistics.mean(r["A_duration_s"] for r in subset),
                    "A_minus_R0_duration_mean_s":statistics.mean(r["A_minus_R0_duration_s"] for r in subset),
                    "R0_timeLoss_mean_s":statistics.mean(r["R0_timeLoss_s"] for r in subset),
                    "A_timeLoss_mean_s":statistics.mean(r["A_timeLoss_s"] for r in subset),
                    "A_minus_R0_timeLoss_mean_s":statistics.mean(r["A_minus_R0_timeLoss_s"] for r in subset),
                    "A_duration_worse_count":sum(r["A_minus_R0_duration_s"]>0 for r in subset),
                    "A_duration_better_count":sum(r["A_minus_R0_duration_s"]<0 for r in subset)})
    return out


def first_divergence(left,right,c):
    a=left[c];b=right[c]
    common=set(a)&set(b)
    differ=[t for (vid,t) in common if a[(vid,t)]!=b[(vid,t)]]
    return {"class":c,"R0_rows":len(a),"A_rows":len(b),"common_rows":len(common),
            "R0_only":len(set(a)-set(b)),"A_only":len(set(b)-set(a)),
            "different_common_rows":len(differ),"first_difference_s":min(differ,default=None)}


def write_csv(path,rows):
    with path.open("x",newline="") as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)


def analyze(r0raw,araw,r0d,ad,phase1):
    gate=json.loads(phase1.read_text())
    if gate["disposition"]!="PASS_PHASE1_PAIRABILITY_AND_EXPOSURE":
        raise ValueError("Phase-1 gate has not passed")
    for raw,key in ((r0raw,"R0_raw_hashes"),(araw,"A_raw_hashes")):
        if any(digest(raw/n)!=h for n,h in gate["provenance"][key].items()):
            raise ValueError(f"Raw changed since phase-1: {raw}")
    demand0=parse_demand(r0d);demandA=parse_demand(ad)
    if any(demand0[k]!=demandA[k] for k in demand0):
        raise ValueError("Exogenous R0/A mismatch")
    f0,invalid0,down0,through0=load_fcd(r0raw/"fcd.xml")
    fa,invalidA,downA,throughA=load_fcd(araw/"fcd.xml")
    r0core=core_bins(f0["M"],"R0");acore=core_bins(fa["M"],"A")
    contrast=compare_bins(r0core,acore)
    rt=xml_rows(r0raw/"tripinfo.xml","tripinfo")
    at=xml_rows(araw/"tripinfo.xml","tripinfo")
    rv=xml_rows(r0raw/"vehroute.xml","vehicle")
    av=xml_rows(araw/"vehroute.xml","vehicle")
    trips=paired_trip_metrics(rt,at,demand0)
    trip_summary=summarize_trips(trips)
    lifecycle=[]
    for arm,d,t,v in (("R0",demand0,rt,rv),("A",demandA,at,av)):
        for c in "MRUX":
            ids={x for x in d if route_class(x)==c}
            done={x for x in ids&set(v) if "arrival" in v[x] and float(v[x]["arrival"])>=0}
            delays=[float(t[x]["departDelay"]) for x in ids&set(t)]
            lifecycle.append({"arm":arm,"class":c,"planned":len(ids),"inserted":len(ids&set(v)),
                              "arrived":len(done),"unfinished":len(ids&set(v)-done),
                              "never_inserted":len(ids-set(v)),"external_depart_delay_sum_s":sum(delays),
                              "external_depart_delay_mean_per_planned_s":sum(delays)/len(ids) if ids else None})
    passage=[]
    for arm,down in (("R0",down0),("A",downA)):
        for cut in (540,1440,1500,2700):
            passage.append({"arm":arm,"cutoff_inclusive_s":cut,"M_first_main_down_FCD_unique":sum(t<=cut for t in down.values())})
    divergence=[first_divergence(f0,fa,c) for c in "MUX"]
    depdiff=[]
    for c in "MUX":
        ids={x for x in demand0 if route_class(x)==c}
        diffs=[x for x in ids if float(rv[x]["depart"])!=float(av[x]["depart"])]
        depdiff.append({"class":c,"different_actual_departures":len(diffs),
                        "first_different_desired_depart_s":min((float(demand0[x]["depart"]) for x in diffs),default=None),
                        "first_different_actual_depart_s":min((float(av[x]["depart"]) for x in diffs),default=None)})
    result={"scope":"exploratory new matched R0/A; no B/C or formal inference",
            "phase1_receipt_sha256":digest(phase1),
            "raw_sha256":{"R0":{n:digest(r0raw/n) for n in gate["provenance"]["R0_raw_hashes"]},
                          "A":{n:digest(araw/n) for n in gate["provenance"]["A_raw_hashes"]}},
            "invalid_M_samples":{"R0":len(invalid0),"A":len(invalidA),"R0_examples":invalid0[:5],"A_examples":invalidA[:5]},
            "windows":whole_window(r0core,"R0")+whole_window(acore,"A"),
            "trip_summary":trip_summary,"lifecycle":lifecycle,"M_passage":passage,
            "first_FCD_divergence":divergence,"actual_departure_differences":depdiff,
            "R_through_FCD_first_s":min(throughA.values(),default=None),
            "notes":["FCD 1 Hz first-lane observation is a lower-resolution passage proxy; no mixed E1 used for M benefit.",
                     "Fixed 100m cells 13-17 and all 90 bins; empty-bin speed null. Density uses 0.2km mainline lane length per cell.",
                     "No P/S/L recomputation: this full-network outcome is not yet bound to the locked classifier adapter; historical diagnostics remain unchanged."]}
    return result,r0core+acore,contrast,trips


def main():
    p=argparse.ArgumentParser()
    for name in ("r0_raw","a_raw","r0_demand","a_demand","phase1","output"):
        p.add_argument("--"+name.replace("_","-"),type=Path,required=True)
    a=p.parse_args()
    result,core,contrast,trips=analyze(a.r0_raw,a.a_raw,a.r0_demand,a.a_demand,a.phase1)
    a.output.mkdir(parents=True,exist_ok=False)
    (a.output/"OUTCOME_SUMMARY.json").write_text(json.dumps(result,indent=2,sort_keys=True)+"\n")
    write_csv(a.output/"M_CORE_30S.csv",core)
    write_csv(a.output/"M_CORE_CONTRAST_30S.csv",contrast)
    write_csv(a.output/"M_TRIP_PAIRED.csv",trips)
    print(json.dumps({"windows":result["windows"],"trips":result["trip_summary"],
                      "divergence":result["first_FCD_divergence"]},indent=2))


if __name__=="__main__":
    main()

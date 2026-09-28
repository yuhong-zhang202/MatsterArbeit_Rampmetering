#!/usr/bin/env python3
"""Raw-bound spatial and boundary diagnostics supplement for default A/B.

All quantities are descriptive; source x and slow-speed cuts are diagnostic,
not new scientific acceptance thresholds.
"""
from __future__ import annotations

import csv
import json
from collections import Counter, defaultdict
from pathlib import Path
import xml.etree.ElementTree as ET

from analyze import MAIN_LANES, digest, route_class
from analyze_b import verify_raw_allow_outcome_warnings
from analyze_sigma0 import verify_card, verify_manifest
from analyze_a_outcome import xml_rows

ROOT = Path(__file__).resolve().parents[3]
BASE = ROOT / "artifacts/stage6_full_network_abc_matched_rebuild_20260926_v1"
PACKAGE = BASE / "inputs_retry2"
RAW = {a: ROOT / f"data/raw/stage6_fullnet_abc_matched_rebuild_20260926_v1_retry2/{a}/outputs" for a in ("A", "B")}
OUT = ROOT / "data/processed/stage6_fullnet_abc_matched_rebuild_20260926_v1/b_outcome_v1"


def fcd(path):
    rows = {}
    shared = Counter()
    shared_slow = Counter()
    shared_dwell = Counter()
    urban_lane_seconds = Counter()
    urban_lane_slow = Counter()
    tlast = -1
    for _, step in ET.iterparse(path, events=("end",)):
        if step.tag != "timestep":
            continue
        t = int(float(step.get("time")))
        if t != tlast + 1:
            raise ValueError(f"FCD gap or duplicate after {tlast}: {t}")
        tlast = t
        for v in step:
            vid = v.get("id")
            c = route_class(vid)
            if c in "MUX":
                key = (vid, t)
                if key in rows:
                    raise ValueError(f"Duplicate FCD identity/time {key}")
                rows[key] = (v.get("lane"), float(v.get("x")), float(v.get("speed")), v.get("pos"))
            if 540 <= t < 1500 and c in "RU" and v.get("lane") == "shared_approach_0":
                shared[(c,t)] += 1
                shared_dwell[(c,vid)] += 1
                if float(v.get("speed")) < 1.3888888888888888:
                    shared_slow[(c,t)] += 1
            if 540 <= t < 1500 and c == "U":
                lane=v.get("lane")
                urban_lane_seconds[lane]+=1
                if float(v.get("speed")) < 1.3888888888888888:
                    urban_lane_slow[lane]+=1
        step.clear()
    if tlast != 2699:
        raise ValueError(f"FCD must end at 2699, got {tlast}")
    return rows, shared, shared_slow, shared_dwell, urban_lane_seconds, urban_lane_slow


def main():
    _, msha = verify_manifest(PACKAGE)
    prov = {}
    for arm in ("A", "B"):
        card = BASE / f"FULLNET3350_{arm}_R900_S17_REBUILD_V2_CARD.json"
        _, sha = verify_card(card, PACKAGE, arm, msha, RAW[arm])
        chk = verify_raw_allow_outcome_warnings(RAW[arm], sha, arm)
        prov[arm] = {"card_sha256": sha, "fcd_sha256": digest(RAW[arm]/"fcd.xml"), **chk}
    parsed = {a: fcd(RAW[a]/"fcd.xml") for a in ("A", "B")}
    a, b = parsed["A"][0], parsed["B"][0]
    first = {}
    for c in "MUX":
        changed = [(t, vid, a.get((vid,t)), b.get((vid,t)))
                   for vid,t in set(a) | set(b)
                   if route_class(vid)==c and t>=540 and a.get((vid,t)) != b.get((vid,t))]
        if changed:
            t, vid, ar, br = min(changed, key=lambda z:(z[0],z[1]))
            first[c] = {"time_s":t,"id":vid,"A":ar,"B":br}
        else:
            first[c] = None
    early=[]
    for t in range(540, 631):
        same = [(vid,a[(vid,t)],b[(vid,t)]) for vid in {k[0] for k in a if k[1]==t and k in b and route_class(k[0])=="M"}]
        diff = [(vid,x,y) for vid,x,y in same if x!=y]
        early.append({"time_s":t,"common_M":len(same),"different_common_M":len(diff),
                      "different_A_x_below_1000":sum(x[1]<1000 for _,x,_ in diff),
                      "different_B_x_below_1000":sum(y[1]<1000 for _,_,y in diff),
                      "different_A_x_1400_1700":sum(1400<=x[1]<1700 for _,x,_ in diff)})
    # Independent re-aggregation from raw FCD, not the 30-second CSV.
    cells={arm:defaultdict(list) for arm in ("A","B")}
    for arm in ("A","B"):
        for (vid,t),(lane,x,speed,pos) in parsed[arm][0].items():
            if route_class(vid)=="M" and 540<=t<1500 and lane in MAIN_LANES:
                cell=min(int(x//100),21)
                if 13<=cell<=17:
                    cells[arm][cell].append(speed)
    core={str(cell):{arm:{"samples":len(cells[arm][cell]),"mean_speed_mps":sum(cells[arm][cell])/len(cells[arm][cell])}
                     for arm in ("A","B")} for cell in range(13,18)}
    summary=json.loads((OUT/"A_B_SUMMARY.json").read_text())
    for arm in ("A","B"):
        n=sum(core[str(c)][arm]["samples"] for c in range(13,18))
        mean=sum(sum(cells[arm][c]) for c in range(13,18))/n
        reference=next(z for z in summary["fixed_windows"] if z["arm"]==arm and z["window"]=="active")
        if n!=reference["M_samples"] or abs(mean-reference["M_vehicle_second_weighted_speed_mps"])>1e-9:
            raise ValueError(f"Independent raw core aggregation mismatch: {arm} n={n}/{reference['M_samples']} mean={mean}/{reference['M_vehicle_second_weighted_speed_mps']}")
    shared={}
    for arm in ("A","B"):
        _,n,slow,dwell,_,_=parsed[arm]
        shared[arm]={c:{"vehicle_seconds":sum(n[(c,t)] for t in range(540,1500)),
                         "slow_vehicle_seconds":sum(slow[(c,t)] for t in range(540,1500)),
                         "max_simultaneous":max(n[(c,t)] for t in range(540,1500)),
                         "vehicles_observed":len({vid for cc,vid in dwell if cc==c}),
                         "per_vehicle_mean_dwell_s_observed":sum(z for (cc,vid),z in dwell.items() if cc==c)/max(1,len({vid for cc,vid in dwell if cc==c}))}
                     for c in "RU"}
    trips={arm:xml_rows(RAW[arm]/"tripinfo.xml","tripinfo") for arm in ("A","B")}
    veh={arm:xml_rows(RAW[arm]/"vehroute.xml","vehicle") for arm in ("A","B")}
    paired={}
    for c in "MRUX":
        ids=[v for v in trips["A"] if route_class(v)==c]
        paired[c]={"n":len(ids),
                   "B_minus_A_mean_duration_s":sum(float(trips["B"][v]["duration"])-float(trips["A"][v]["duration"]) for v in ids)/len(ids),
                   "B_minus_A_mean_timeLoss_s":sum(float(trips["B"][v]["timeLoss"])-float(trips["A"][v]["timeLoss"]) for v in ids)/len(ids),
                   "B_minus_A_mean_external_departDelay_s":sum(float(trips["B"][v]["departDelay"])-float(trips["A"][v]["departDelay"]) for v in ids)/len(ids),
                   "B_minus_A_mean_arrival_s":sum(float(veh["B"][v]["arrival"])-float(veh["A"][v]["arrival"]) for v in ids)/len(ids)}
    report={"status":"RAW_BOUND_DESCRIPTIVE_DIAGNOSTIC","provenance":prov,
            "first_post540_differences":first,"early_M_spatial_negative_control_540_630":early,
            "M_core_active_raw_reaggregation":core,"shared_approach_active_540_1500":shared,
            "U_lane_vehicle_seconds_active_540_1500":{arm:dict(parsed[arm][4]) for arm in ("A","B")},
            "U_lane_slow_vehicle_seconds_active_540_1500":{arm:dict(parsed[arm][5]) for arm in ("A","B")},
            "paired_full_cohort":paired,"limitations":["Single seed; not a causal decomposition.",
                "x<1000 and slow-speed cuts are diagnostics, not acceptance thresholds.",
                "FCD shared dwell counts only the active window and is not full route residence."]}
    with (OUT/"B_POSTR_DIAGNOSTIC_REV2.json").open("x") as f:
        json.dump(report,f,indent=2,sort_keys=True);f.write("\n")
    print(json.dumps({"first":first,"paired":paired,"shared":shared,"core":core},indent=2))


if __name__=="__main__":main()

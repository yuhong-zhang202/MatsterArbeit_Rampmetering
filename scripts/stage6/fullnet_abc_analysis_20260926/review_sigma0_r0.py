#!/usr/bin/env python3
"""Immutable R0_SIGMA0 postrun integrity/lifecycle/prechallenge review."""
from __future__ import annotations

import argparse
import json
import statistics
from collections import Counter, defaultdict
from pathlib import Path
import xml.etree.ElementTree as ET

from analyze import digest, route_class
from analyze_a_outcome import xml_rows
from analyze_sigma0 import verify_manifest, verify_card, verify_raw, demand, pre_and_r_fcd


def fcd_coverage(path):
    times=[];all_ids=set();pre_ids=set();counts=Counter();pre_core_speed=[]
    for _,step in ET.iterparse(path,events=("end",)):
        if step.tag!="timestep":continue
        t=int(float(step.get("time")));times.append(t)
        for v in step:
            vid=v.get("id");c=route_class(vid);all_ids.add(vid)
            if t<540:
                counts[c]+=1;pre_ids.add(vid)
                x=float(v.get("x"))
                if c=="M" and 1300<=x<1800:
                    pre_core_speed.append(float(v.get("speed")))
        step.clear()
    if times!=list(range(2700)):raise ValueError("FCD labels incomplete/duplicate")
    return {"time_labels":len(times),"first_s":times[0],"last_s":times[-1],
            "all_observed_ids":len(all_ids),"pre_540_unique_ids":dict(Counter(route_class(v) for v in pre_ids)),
            "pre_540_vehicle_second_rows":dict(counts),
            "pre_540_M_core_vehicle_second_samples":len(pre_core_speed),
            "pre_540_M_core_weighted_speed_mps":statistics.mean(pre_core_speed) if pre_core_speed else None},all_ids


def lifecycle(requested,trips,veh):
    out=[]
    for c in "MRUX":
        ids={v for v in requested if route_class(v)==c}
        t_ids=ids&set(trips);v_ids=ids&set(veh)
        delays=[float(trips[v]["departDelay"]) for v in t_ids]
        pre_planned=sum(float(requested[v]["depart"])<540 for v in ids)
        pre_actual=sum(float(veh[v]["depart"])<540 for v in v_ids)
        out.append({"class":c,"planned":len(ids),"tripinfo":len(t_ids),"vehroute":len(v_ids),
                    "arrived":sum(float(veh[v].get("arrival","-1"))>=0 for v in v_ids),
                    "unfinished":sum(float(veh[v].get("arrival","-1"))<0 for v in v_ids),
                    "never_inserted":len(ids-set(trips)) + sum(float(trips[v].get("depart","-1"))<0 for v in t_ids),
                    "desired_depart_before_540":pre_planned,"actual_depart_before_540":pre_actual,
                    "departDelay_mean_s":statistics.mean(delays) if delays else None,
                    "departDelay_max_s":max(delays) if delays else None,
                    "departDelay_positive_n":sum(x>0 for x in delays)})
    return out


def final_summary(path):
    last=None;n=0
    for _,e in ET.iterparse(path,events=("end",)):
        if e.tag=="step":last=dict(e.attrib);n+=1;e.clear()
    if n!=2700 or last is None:raise ValueError(f"Summary coverage {n} != 2700")
    return {"steps":n,"last":last}


def analyze(package,card_path,raw):
    _,msha=verify_manifest(package)
    card,csha=verify_card(card_path,package,"R0_SIGMA0",msha,raw)
    integrity=verify_raw(raw,csha,"R0_SIGMA0")
    requested=demand(package/"R0_SIGMA0"/"demand.rou.xml")["vehicles"]
    trips=xml_rows(raw/"tripinfo.xml","tripinfo")
    veh=xml_rows(raw/"vehroute.xml","vehicle")
    if set(trips)!=set(requested) or set(veh)!=set(requested):
        raise ValueError("R0 requested/tripinfo/vehroute identity set mismatch")
    lc=lifecycle(requested,trips,veh)
    if any(r["never_inserted"] or r["unfinished"] or r["arrived"]!=r["planned"] for r in lc):
        raise ValueError("R0 lifecycle incomplete")
    pre,_=pre_and_r_fcd(raw/"fcd.xml",False)
    fcd,all_ids=fcd_coverage(raw/"fcd.xml")
    if all_ids!=set(requested):raise ValueError("R0 FCD vehicle coverage mismatch")
    summary=final_summary(raw/"sumo_summary.xml")
    errors=(raw/"sumo_error.log").read_text().splitlines()
    warnings=[line for name in ("sumo.log","stderr.log","stdout.log") for line in (raw/name).read_text().splitlines() if "Warning:" in line or "Error:" in line]
    if errors or warnings:raise ValueError("SUMO error/warning lines present")
    return {"disposition":"PASS_R0_POSTRUN_ELIGIBLE_FOR_A_PRELAUNCH_REVIEW",
            "scope":"single-arm technical sensitivity baseline only; no A attribution or clean-control classification",
            "input":{"card_sha256":csha,"input_manifest_sha256":msha,"network_sha256":card["network_sha256"]},
            "raw":{"root":str(raw),**integrity,"fcd_sha256":digest(raw/"fcd.xml"),
                   "tripinfo_sha256":digest(raw/"tripinfo.xml"),"vehroute_sha256":digest(raw/"vehroute.xml")},
            "lifecycle":lc,"fcd":fcd,"pre_FCD_exact_tuple_rows":len(pre),
            "summary":summary,"sumo_error_lines":errors,"warning_or_error_lines":warnings}


def main():
    p=argparse.ArgumentParser()
    for name in ("package","card","raw","output"):
        p.add_argument("--"+name,type=Path,required=True)
    a=p.parse_args()
    x=analyze(a.package.resolve(),a.card.resolve(),a.raw.resolve())
    a.output.parent.mkdir(parents=True,exist_ok=True)
    with a.output.open("x") as f:f.write(json.dumps(x,indent=2,sort_keys=True)+"\n")
    print(json.dumps({"disposition":x["disposition"],"lifecycle":x["lifecycle"],"fcd":x["fcd"]},indent=2))


if __name__=="__main__":main()

#!/usr/bin/env python3
"""Phase-1 R0/A pairability and R exposure; never reads post-540 M FCD."""
from __future__ import annotations

import argparse
import csv
import json
from collections import Counter
from pathlib import Path
import xml.etree.ElementTree as ET

from analyze import ACTIVATION, CLASSES, HORIZON, digest, parse_demand, route_class


def verify_receipt(raw, card):
    p = raw / "execution_receipt.json"
    r = json.loads(p.read_text())
    if r["card_sha256"] != digest(card):
        raise ValueError(f"Card hash mismatch: {raw}")
    bad = []
    for name, item in r["output_manifest"].items():
        f = raw / name
        if not f.is_file() or f.stat().st_size != item["bytes"] or digest(f) != item["sha256"]:
            bad.append(name)
    return r, bad


def lifecycle(raw, planned):
    """Only retain ID, actual departure and arrival presence; no M outcomes."""
    veh = {}
    trips = set()
    for _, e in ET.iterparse(raw / "vehroute.xml", events=("end",)):
        if e.tag == "vehicle":
            vid = e.get("id")
            if vid in veh:
                raise ValueError(f"Duplicate vehroute ID: {vid}")
            veh[vid] = {"depart": float(e.get("depart")),
                        "arrived": e.get("arrival") is not None and float(e.get("arrival")) >= 0}
            e.clear()
    for _, e in ET.iterparse(raw / "tripinfo.xml", events=("end",)):
        if e.tag == "tripinfo":
            vid = e.get("id")
            if vid in trips:
                raise ValueError(f"Duplicate tripinfo ID: {vid}")
            trips.add(vid)
            e.clear()
    rows = []
    for c in CLASSES:
        ids = {v for v in planned if route_class(v) == c}
        inserted = ids & set(veh)
        rows.append({"class":c,"planned":len(ids),"inserted":len(inserted),
                     "arrived":sum(veh[v]["arrived"] for v in inserted),
                     "unfinished":sum(not veh[v]["arrived"] for v in inserted),
                     "never_inserted":len(ids-inserted),"tripinfo":len(ids&trips),
                     "actual_depart_before_540":sum(veh[v]["depart"]<ACTIVATION for v in inserted)})
    unexpected = (set(veh)|trips)-set(planned)
    return veh, rows, sorted(unexpected)


def fcd_phase1(path):
    pre = {}
    first_aux = {}
    first_through = {}
    labels = []
    for _, step in ET.iterparse(path, events=("end",)):
        if step.tag != "timestep":
            continue
        t = float(step.get("time"))
        if t != int(t) or not 0 <= t < HORIZON:
            raise ValueError(f"Bad FCD label {t}")
        t = int(t)
        if labels and t != labels[-1]+1:
            raise ValueError(f"Missing/repeated FCD label {t}")
        labels.append(t)
        for v in step:
            if v.tag != "vehicle":
                continue
            vid = v.get("id")
            if t >= ACTIVATION and not vid.startswith("R_flow."):
                continue
            c = route_class(vid)
            if t < ACTIVATION and c in "MUX":
                key = (vid,t)
                if key in pre:
                    raise ValueError(f"Duplicate pre-R FCD {key}")
                pre[key] = tuple(v.get(k) for k in ("lane","pos","speed","x","y"))
            elif c == "R":
                lane = v.get("lane")
                if lane == "merge_section_0":
                    first_aux.setdefault(vid,t)
                if lane == "merge_section_1":
                    first_through.setdefault(vid,t)
            # No post-activation M values are retained or read.
        step.clear()
    if labels != list(range(HORIZON)):
        raise ValueError(f"Incomplete FCD: {len(labels)} labels")
    return pre, first_aux, first_through


def through_lanechanges(path, through):
    for _, e in ET.iterparse(path, events=("end",)):
        if e.tag == "change" and e.get("id","").startswith("R_flow.") and e.get("to") == "merge_section_1":
            vid = e.get("id")
            t = float(e.get("time"))
            through[vid] = min(t,through.get(vid,t))
            e.clear()


def compare_pre(a,b):
    rows=[]
    for c in "MUX":
        ka={k for k in a if route_class(k[0])==c}
        kb={k for k in b if route_class(k[0])==c}
        common=ka&kb
        exact=sum(a[k]==b[k] for k in common)
        coarse=sum(a[k][0]!=b[k][0] or abs(float(a[k][1])-float(b[k][1]))>10 or
                   abs(float(a[k][2])-float(b[k][2]))>2 for k in common)
        rows.append({"class":c,"R0_rows":len(ka),"A_rows":len(kb),"common_rows":len(common),
                     "R0_only":len(ka-kb),"A_only":len(kb-ka),"exact_tuple_matches":exact,
                     "coarse_mismatch":coarse})
    return rows


def main():
    p=argparse.ArgumentParser()
    for name in ("r0_raw","a_raw","r0_card","a_card","r0_demand","a_demand","r0_review","output"):
        p.add_argument("--"+name.replace("_","-"),type=Path,required=True)
    a=p.parse_args()
    r0r,r0bad=verify_receipt(a.r0_raw,a.r0_card)
    ar,abad=verify_receipt(a.a_raw,a.a_card)
    r0d=parse_demand(a.r0_demand)
    ad=parse_demand(a.a_demand)
    rv,rlife,ru=lifecycle(a.r0_raw,r0d)
    av,alife,au=lifecycle(a.a_raw,ad)
    rp,_,_=fcd_phase1(a.r0_raw/"fcd.xml")
    ap,aux,through=fcd_phase1(a.a_raw/"fcd.xml")
    through_lanechanges(a.a_raw/"lanechanges.xml",through)
    pre=compare_pre(rp,ap)
    departures=[]
    for c in "MUX":
        rpre={v:rv[v]["depart"] for v in r0d if route_class(v)==c and v in rv and rv[v]["depart"]<ACTIVATION}
        apre={v:av[v]["depart"] for v in ad if route_class(v)==c and v in av and av[v]["depart"]<ACTIVATION}
        departures.append({"class":c,"R0_pre_IDs":len(rpre),"A_pre_IDs":len(apre),
                           "R0_only":len(set(rpre)-set(apre)),"A_only":len(set(apre)-set(rpre)),
                           "different_actual_depart_time":sum(rpre[v]!=apre[v] for v in set(rpre)&set(apre))})
    errors=[x for x in (a.a_raw/"sumo_error.log").read_text().splitlines() if x.strip()]
    pre_errors=[x for x in errors if "U_flow." in x and any(f"U_flow.{i} " in x for i in range(54))]
    ramp_ids={v for v in ad if route_class(v)=="R"}
    exposure=[]
    for cut in (1440,1500,2700):
        exposure.append({"cutoff_inclusive_s":cut,"R_departed":sum(av[v]["depart"]<=cut for v in ramp_ids if v in av),
                         "R_aux_FCD_unique":sum(t<=cut for t in aux.values()),
                         "R_through_FCD_or_lanechange_unique":sum(t<=cut for t in through.values())})
    r0review=json.loads(a.r0_review.read_text())
    r0_unchanged=(r0review["provenance"]["execution_receipt_sha256"]==digest(a.r0_raw/"execution_receipt.json")
                  and all(digest(a.r0_raw/name)==sha for name,sha in r0review["provenance"]["raw_hashes"].items()))
    common={v for v in r0d if route_class(v) in "MUX"}
    checks={"R0_raw_hashes":not r0bad,"A_raw_hashes":not abad,
            "R0_completed":r0r["status"]=="COMPLETED" and r0r["return_code"]==0,
            "A_completed":ar["status"]=="COMPLETED" and ar["return_code"]==0,
            "R0_prior_review_unchanged":r0_unchanged,
            "demand_card_hashes":digest(a.r0_demand)==json.loads(a.r0_card.read_text())["input_sha256"]["demand"]
                                 and digest(a.a_demand)==json.loads(a.a_card.read_text())["input_sha256"]["demand"],
            "exogenous_MUX_equal":common=={v for v in ad if route_class(v) in "MUX"} and all(r0d[v]==ad[v] for v in common),
            "R240_planned":len(ramp_ids)==240,
            "complete_lifecycle":all(x["planned"]==x["inserted"]==x["arrived"]==x["tripinfo"] and
                                     x["unfinished"]==x["never_inserted"]==0 for x in rlife+alife),
            "no_unexpected_ids":not ru and not au,
            "pre_R_departures_identical":all(x["R0_only"]==x["A_only"]==x["different_actual_depart_time"]==0 for x in departures),
            "pre_R_FCD_exact":all(x["R0_only"]==x["A_only"]==0 and x["exact_tuple_matches"]==x["common_rows"] for x in pre),
            "no_pre_R_U_error":not pre_errors,
            "R_through_observed":bool(through)}
    result={"disposition":"PASS_PHASE1_PAIRABILITY_AND_EXPOSURE" if all(checks.values()) else "HOLD",
            "scope":"No post-540 M FCD, route time, timeLoss, P/S/L, or A phenomenon evaluated",
            "checks":checks,"R0_lifecycle":rlife,"A_lifecycle":alife,"pre_departures":departures,
            "pre_FCD":pre,"R_exposure":exposure,"R_first_actual_depart_s":min((av[v]["depart"] for v in ramp_ids if v in av),default=None),
            "R_first_aux_FCD_s":min(aux.values(),default=None),"R_first_through_FCD_or_lanechange_s":min(through.values(),default=None),
            "A_error_lines":errors,"A_pre_U_error_lines":pre_errors,
            "boundary_M_flow_502":{"planned_depart_s":r0d["M_flow.502"]["depart"],
                                   "R0_actual_depart_s":rv["M_flow.502"]["depart"],
                                   "A_actual_depart_s":av["M_flow.502"]["depart"]},
            "provenance":{"R0_card_sha256":digest(a.r0_card),"A_card_sha256":digest(a.a_card),
                          "R0_receipt_sha256":digest(a.r0_raw/"execution_receipt.json"),
                          "A_receipt_sha256":digest(a.a_raw/"execution_receipt.json"),
                          "R0_raw_hashes":{n:digest(a.r0_raw/n) for n in r0r["output_manifest"]},
                          "A_raw_hashes":{n:digest(a.a_raw/n) for n in ar["output_manifest"]}}}
    a.output.mkdir(parents=True,exist_ok=False)
    (a.output/"PHASE1_REVIEW.json").write_text(json.dumps(result,indent=2,sort_keys=True)+"\n")
    print(result["disposition"])
    print("failed checks",[k for k,v in checks.items() if not v])


if __name__=="__main__":
    main()

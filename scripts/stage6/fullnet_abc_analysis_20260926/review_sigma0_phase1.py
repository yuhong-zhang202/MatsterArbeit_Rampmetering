#!/usr/bin/env python3
"""Sigma0 pair phase-1 integrity, pre-R equality and actual R exposure only.

Never loads post-540 M FCD rows into the analysis or computes M outcomes.
"""
from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path

from analyze import digest, route_class
from analyze_sigma0 import verify_manifest, verify_card, verify_raw, static_gate, phase1_gate


def review(root,base,r0raw,araw,r0card,acard,base_r0card,base_acard):
    _,msha=verify_manifest(root)
    _,bmsha=verify_manifest(base)
    cards={};card_hashes={};raw_receipts={}
    for short,arm,path,raw in (("R0","R0_SIGMA0",r0card,r0raw),("A","A_SIGMA0",acard,araw)):
        cards[short],card_hashes[short]=verify_card(path,root,arm,msha,raw)
        raw_receipts[short]=verify_raw(raw,card_hashes[short],arm)
        if cards[short].get("base_manifest_sha256")!=bmsha:
            raise ValueError(f"{arm} base manifest hash mismatch")
    base_cards={}
    for short,path in (("R0",base_r0card),("A",base_acard)):
        c=json.loads(path.read_text());raw=Path(c["raw_root"])/short/"outputs"
        base_cards[short],_=verify_card(path,base,short,bmsha,raw)
    d=static_gate(root,base,cards,base_cards)
    phase,trips,veh,through=phase1_gate(r0raw,araw,d)
    requested={arm:Counter(route_class(v) for v in d[arm]["vehicles"]) for arm in ("R0","A")}
    actual_pre={arm:Counter(route_class(v) for v,row in veh[arm].items() if float(row["depart"])<540) for arm in ("R0","A")}
    if actual_pre["R0"]!=actual_pre["A"]:
        raise ValueError("Pre-R actual departure class count mismatch")
    for raw in (r0raw,araw):
        for name in ("sumo.log","stderr.log","stdout.log"):
            if any("Warning:" in line or "Error:" in line for line in (raw/name).read_text().splitlines()):
                raise ValueError(f"SUMO warning/error in {raw/name}")
    rids=sorted(v for v in d["A"]["vehicles"] if route_class(v)=="R")
    ractual={v:float(veh["A"][v]["depart"]) for v in rids}
    boundary={arm:{k:veh[arm]["M_flow.502"].get(k) for k in ("depart","departLane","departPos","departSpeed")}
              for arm in ("R0","A")}
    if boundary["R0"]["depart"]!="540.00" or boundary["R0"]!=boundary["A"]:
        raise ValueError("M_flow.502 t540 boundary mismatch")
    return {"disposition":"PASS_PHASE1_PAIRABILITY_AND_R_EXPOSURE_RELEASE_TO_SCIENTIFIC_REVIEW",
            "scope":"phase 1 only; post-R M outcome not inspected",
            "requested":{arm:dict(requested[arm]) for arm in ("R0","A")},
            "actual_depart_before_540":{arm:dict(actual_pre[arm]) for arm in ("R0","A")},
            "exact_pre_FCD_vehicle_second_tuples":phase["pre_FCD_rows"],
            "exact_pre_FCD_by_class":phase["pre_FCD_by_class"],
            "M_flow_502_boundary":boundary,
            "R_actual":{"planned":len(rids),"inserted":len(ractual),"arrived":sum(float(veh["A"][v]["arrival"])>=0 for v in rids),
                        "unfinished":sum(float(veh["A"][v]["arrival"])<0 for v in rids),
                        "first_actual_depart_s":min(ractual.values()),"first_through_s":phase["first_R_through_s"],
                        "unique_through_by_cutoff":phase["R_through_unique_by_cutoff"],
                        "first_five_through_entries":[{"id":v,"time_s":t} for v,t in sorted(through.items(),key=lambda z:(z[1],z[0]))[:5]]},
            "provenance":{"sigma_manifest_sha256":msha,"default_manifest_sha256":bmsha,
                          "sigma_card_sha256":card_hashes,"sigma_raw_receipts":raw_receipts,
                          "R0_FCD_sha256":digest(r0raw/"fcd.xml"),"A_FCD_sha256":digest(araw/"fcd.xml"),
                          "code_sha256":digest(Path(__file__))}}


def main():
    p=argparse.ArgumentParser()
    for name in ("sigma_package","default_package","r0_raw","a_raw","r0_card","a_card","default_r0_card","default_a_card","output"):
        p.add_argument("--"+name.replace("_","-"),type=Path,required=True)
    a=p.parse_args()
    out=review(a.sigma_package.resolve(),a.default_package.resolve(),a.r0_raw.resolve(),a.a_raw.resolve(),
               a.r0_card.resolve(),a.a_card.resolve(),a.default_r0_card.resolve(),a.default_a_card.resolve())
    a.output.parent.mkdir(parents=True,exist_ok=True)
    with a.output.open("x") as f:f.write(json.dumps(out,indent=2,sort_keys=True)+"\n")
    print(json.dumps({k:out[k] for k in ("disposition","requested","actual_depart_before_540","exact_pre_FCD_vehicle_second_tuples","R_actual")},indent=2))


if __name__=="__main__":main()

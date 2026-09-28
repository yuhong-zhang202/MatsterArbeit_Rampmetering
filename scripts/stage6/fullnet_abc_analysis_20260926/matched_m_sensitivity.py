#!/usr/bin/env python3
"""Same-ID/time/lane/cell M speed sensitivity for fixed merge-core windows."""
from __future__ import annotations

import argparse
import json
from collections import defaultdict
from pathlib import Path
import xml.etree.ElementTree as ET

from analyze import CORE_CELLS, MAIN_LANES, digest


def load(path):
    rows={}
    for _,step in ET.iterparse(path,events=("end",)):
        if step.tag!="timestep":continue
        t=int(float(step.get("time")))
        for v in step:
            if not v.get("id","").startswith("M_flow."):
                continue
            x=float(v.get("x"));lane=v.get("lane")
            if lane not in MAIN_LANES or not 0<=x<=2200:
                continue
            cell=min(int(x//100),21)
            if cell in CORE_CELLS:
                rows[(v.get("id"),t)]=(lane,cell,float(v.get("speed")))
        step.clear()
    return rows


def calculate(r0,a):
    stats=defaultdict(lambda:{"n":0,"sum_delta":0.0,"negative":0,"positive":0,"zero":0})
    for vid,t in set(r0)&set(a):
        l,r=r0[(vid,t)],a[(vid,t)]
        if l[:2]!=r[:2]:continue
        window="pre" if t<540 else "active" if t<1500 else "tail"
        x=stats[(window,l[1])]
        delta=r[2]-l[2]
        x["n"]+=1;x["sum_delta"]+=delta
        x["negative"]+=delta<0;x["positive"]+=delta>0;x["zero"]+=delta==0
    return [{"window":w,"cell":c,**x,"mean_A_minus_R0_speed_mps":x["sum_delta"]/x["n"] if x["n"] else None}
            for (w,c),x in sorted(stats.items())]


def main():
    p=argparse.ArgumentParser()
    for n in ("r0","a","phase1","output"):
        p.add_argument("--"+n,type=Path,required=True)
    x=p.parse_args();gate=json.loads(x.phase1.read_text())
    if gate["disposition"]!="PASS_PHASE1_PAIRABILITY_AND_EXPOSURE":raise ValueError("Phase 1 not released")
    for raw,k in ((x.r0,"R0_raw_hashes"),(x.a,"A_raw_hashes")):
        if digest(raw/"fcd.xml")!=gate["provenance"][k]["fcd.xml"]:raise ValueError("FCD hash drift")
    rows=calculate(load(x.r0/"fcd.xml"),load(x.a/"fcd.xml"))
    x.output.write_text(json.dumps({"rows":rows,"scope":"same vehicle-second, same lane and core cell; selection may change with treatment; descriptive sensitivity only",
                                    "phase1_sha256":digest(x.phase1)},indent=2,sort_keys=True)+"\n")
    print(json.dumps([r for r in rows if r["window"]=="active"],indent=2))


if __name__=="__main__":main()

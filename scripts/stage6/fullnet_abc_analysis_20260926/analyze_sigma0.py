#!/usr/bin/env python3
"""Fail-closed, descriptive R0/A M-sigma0 technical sensitivity analysis.

This analyzes an altered driving model and never promotes the default-model A
attribution. It does not run SUMO or modify raw files. All thresholds below are
coverage or exact-identity gates, not new traffic-phenomenon criteria.
"""
from __future__ import annotations

import argparse
import csv
import json
import statistics
from collections import Counter, defaultdict
from pathlib import Path
import xml.etree.ElementTree as ET

from analyze import CORE_CELLS, HORIZON, MAIN_LANES, digest, route_class
from analyze_a_outcome import core_bins, compare_bins, whole_window, xml_rows, paired_trip_metrics, summarize_trips

ACTIVATION=540
SIGMA_ARMS={"R0":"R0_SIGMA0","A":"A_SIGMA0"}
REQUIRED_RAW={"fcd.xml","tripinfo.xml","vehroute.xml","lanechanges.xml","sumo_summary.xml","sumo_error.log","tls_states.xml"}
VEH_FIELDS=("id","type","route","depart","departPos","departLane","departSpeed","speedFactor")
PRE_FCD_FIELDS=("lane","x","y","pos","speed")
THROUGH_LANES={"merge_section_0","merge_section_1","merge_section_2"}


class GateFailure(ValueError):
    pass


def fail(message):
    raise GateFailure(message)


def checked_json(path):
    if not path.is_file(): fail(f"Missing JSON: {path}")
    return json.loads(path.read_text())


def verify_manifest(package):
    manifest=package/"INPUT_MANIFEST.json"
    x=checked_json(manifest)
    files=x.get("files")
    if not isinstance(files,dict) or not files: fail("Empty or malformed input manifest")
    for rel,sha in files.items():
        p=Path(rel)
        if p.is_absolute() or ".." in p.parts: fail(f"Unsafe input path: {rel}")
        f=package/p
        if not f.is_file() or digest(f)!=sha: fail(f"Input manifest hash mismatch: {f}")
    return x,digest(manifest)


def verify_card(card_path,package,arm,manifest_sha,raw):
    c=checked_json(card_path)
    if c.get("arm")!=arm or c.get("package_manifest_sha256")!=manifest_sha:
        fail(f"{arm} card arm or package manifest mismatch")
    if Path(c.get("package_dir",""))!=package or Path(c.get("raw_root",""))/arm/"outputs"!=raw:
        fail(f"{arm} card package/raw binding mismatch")
    for key,name in (("demand","demand.rou.xml"),("additional","scenario.add.xml"),("sumocfg","scenario.sumocfg")):
        if digest(package/arm/name)!=c.get("input_sha256",{}).get(key):
            fail(f"{arm} card input hash mismatch: {name}")
    if not c.get("network_sha256") or not c.get("sumo_sha256"):
        fail(f"{arm} missing scientific/binary hash")
    return c,digest(card_path)


def verify_raw(raw,card_sha,arm):
    receipt=checked_json(raw/"execution_receipt.json")
    if receipt.get("arm")!=arm or receipt.get("card_sha256")!=card_sha or receipt.get("status")!="COMPLETED" or receipt.get("return_code")!=0:
        fail(f"{arm} raw execution receipt incomplete or unbound")
    files=receipt.get("output_manifest",{})
    if not REQUIRED_RAW<=set(files): fail(f"{arm} missing required raw output roles")
    for name,row in files.items():
        if Path(name).is_absolute() or ".." in Path(name).parts: fail(f"Unsafe raw output name {name}")
        p=raw/name
        if not p.is_file() or p.stat().st_size!=row.get("bytes") or digest(p)!=row.get("sha256"):
            fail(f"{arm} raw hash/size mismatch: {p}")
    if (raw/"sumo_error.log").stat().st_size: fail(f"{arm} SUMO error log nonempty")
    return {"receipt_sha256":digest(raw/"execution_receipt.json"),"output_files_verified":len(files)}


def demand(path):
    root=ET.parse(path).getroot()
    if root.tag!="routes" or root.findall("flow"): fail(f"Expected materialized routes: {path}")
    if any(e.tag not in ("vType","route","vehicle") for e in root):
        fail(f"Unrecognized demand element in {path}")
    if any(len(e) for e in root):fail(f"Nested demand semantics not supported: {path}")
    types={e.get("id"):dict(e.attrib) for e in root.findall("vType")}
    routes={e.get("id"):dict(e.attrib) for e in root.findall("route")}
    if len(types)!=len(root.findall("vType")) or len(routes)!=len(root.findall("route")):
        fail(f"Duplicate type/route definition: {path}")
    seq=[];vehicles={}
    for v in root.findall("vehicle"):
        d=dict(v.attrib)
        if set(d)!=set(VEH_FIELDS) or v.get("id") in vehicles:
            fail(f"Missing/duplicate vehicle attributes in {path}: {v.get('id')}")
        if v.get("route") not in routes or v.get("type") not in types:
            fail(f"Unbound vehicle route/type in {path}: {v.get('id')}")
        route_class(v.get("id"));vehicles[v.get("id")]=d;seq.append(v.get("id"))
    if not vehicles: fail("Empty demand")
    return {"types":types,"routes":routes,"vehicles":vehicles,"sequence":seq}


def normalized_xml(path):
    root=ET.parse(path).getroot()
    def node(e):
        attrs={}
        for k,v in e.attrib.items():
            attrs[k]=Path(v).name if k in ("value","file","dest") and ("/" in v or "\\" in v) else v
        return (e.tag,tuple(sorted(attrs.items())),tuple(node(z) for z in e))
    return node(root)


def static_gate(sigma,base,scards,bcards):
    sd={arm:demand(sigma/SIGMA_ARMS[arm]/"demand.rou.xml") for arm in ("R0","A")}
    bd={arm:demand(base/arm/"demand.rou.xml") for arm in ("R0","A")}
    for arm in ("R0","A"):
        s,b=sd[arm],bd[arm]
        if s["routes"]!=b["routes"] or s["sequence"]!=b["sequence"] or set(s["vehicles"])!=set(b["vehicles"]):
            fail(f"{arm} routes or vehicle ordering changed from default package")
        oldtypes=b["types"]
        if s["types"].get("technical_passenger")!=oldtypes.get("technical_passenger") or len(s["types"])!=len(oldtypes)+1:
            fail(f"{arm} base vehicle type changed or unexpected type count")
        mid_types={v["type"] for vid,v in s["vehicles"].items() if route_class(vid)=="M"}
        if len(mid_types)!=1 or "technical_passenger" in mid_types: fail(f"{arm} M sigma type not unique")
        mtype=next(iter(mid_types)); expected=dict(oldtypes["technical_passenger"]);expected["id"]=mtype;expected["sigma"]="0"
        if s["types"].get(mtype)!=expected: fail(f"{arm} M type differs beyond sigma=0")
        for vid,x in s["vehicles"].items():
            y=b["vehicles"][vid]
            expected=dict(y)
            if route_class(vid)=="M": expected["type"]=mtype
            if x!=expected: fail(f"{arm} default/sigma request differs beyond M type: {vid}")
        for name in ("scenario.add.xml","scenario.sumocfg"):
            if normalized_xml(sigma/SIGMA_ARMS[arm]/name)!=normalized_xml(base/arm/name):
                fail(f"{arm} {name} semantics differ from default package")
    if sd["R0"]["types"]!=sd["A"]["types"]:fail("Sigma R0/A type definitions differ")
    if set(sd["A"]["vehicles"])-set(sd["R0"]["vehicles"])!={v for v in sd["A"]["vehicles"] if route_class(v)=="R"}:
        fail("Sigma A differs from R0 by non-R demand")
    if any(sd["R0"]["vehicles"][vid]!=sd["A"]["vehicles"][vid] for vid in sd["R0"]["vehicles"]):
        fail("Sigma R0/A common requested vehicles differ")
    if len({c["network_sha256"] for c in list(scards.values())+list(bcards.values())})!=1:
        fail("Sigma/default network hash differs")
    if len({c["sumo_sha256"] for c in list(scards.values())+list(bcards.values())})!=1:
        fail("Sigma/default SUMO binary hash differs")
    if scards["R0"].get("runner_sha256")!=scards["A"].get("runner_sha256") or not scards["R0"].get("runner_sha256"):
        fail("Sigma R0/A runner hash differs or is missing")
    if len({c["routes_schema_sha256"] for c in list(scards.values())+list(bcards.values())})!=1 or len({c["additional_schema_sha256"] for c in list(scards.values())+list(bcards.values())})!=1:
        fail("Sigma/default XML schema hashes differ")
    config=ET.parse(sigma/SIGMA_ARMS["R0"]/"scenario.sumocfg").getroot()
    net=config.find("./input/net-file")
    if net is None or not net.get("value") or digest(Path(net.get("value")))!=scards["R0"]["network_sha256"]:
        fail("Bound network file hash does not match card")
    return sd


def pre_and_r_fcd(path, collect_r):
    pre={};rthrough={};times=[]
    for _,step in ET.iterparse(path,events=("end",)):
        if step.tag!="timestep":continue
        t=int(float(step.get("time")))
        if times and t!=times[-1]+1:fail(f"FCD missing/repeated time at {t}")
        times.append(t)
        for v in step:
            vid=v.get("id","");c=route_class(vid)
            if t<ACTIVATION and c in "MUX":
                key=(vid,t)
                if key in pre:fail(f"Duplicate pre-R FCD: {key}")
                pre[key]=tuple(v.get(k) for k in PRE_FCD_FIELDS)
            if collect_r and c=="R" and v.get("lane") in THROUGH_LANES:
                rthrough.setdefault(vid,t)
        step.clear()
    if times!=list(range(HORIZON)): fail(f"FCD must have 2700 consecutive labels: {path}")
    return pre,rthrough


def lanechange_through(path):
    out={}
    for _,e in ET.iterparse(path,events=("end",)):
        if e.tag=="change" and e.get("id","").startswith("R_flow.") and e.get("to") in THROUGH_LANES:
            vid=e.get("id");t=float(e.get("time"));out[vid]=min(t,out.get(vid,t));e.clear()
    return out


def phase1_gate(r0_raw,a_raw,sd):
    p0,_=pre_and_r_fcd(r0_raw/"fcd.xml",False)
    pa,rfcd=pre_and_r_fcd(a_raw/"fcd.xml",True)
    if p0!=pa: fail(f"Pre-R FCD mismatch: R0={len(p0)} A={len(pa)} common={len(set(p0)&set(pa))}")
    out={"pre_FCD_rows":len(p0),"pre_FCD_by_class":dict(Counter(route_class(v) for v,t in p0))}
    trips={arm:xml_rows(raw/"tripinfo.xml","tripinfo") for arm,raw in (("R0",r0_raw),("A",a_raw))}
    veh={arm:xml_rows(raw/"vehroute.xml","vehicle") for arm,raw in (("R0",r0_raw),("A",a_raw))}
    for arm in ("R0","A"):
        planned=set(sd[arm]["vehicles"])
        if set(trips[arm])!=planned or set(veh[arm])!=planned:fail(f"{arm} planned/inserted/arrived identities incomplete")
        if any(float(veh[arm][v].get("arrival","-1"))<0 for v in planned):fail(f"{arm} unfinished vehicle")
    for vid in sd["R0"]["vehicles"]:
        if route_class(vid) in "MUX":
            x,y=veh["R0"][vid],veh["A"][vid]
            if float(x["depart"])<ACTIVATION or float(y["depart"])<ACTIVATION:
                if x.get("depart")!=y.get("depart") or x.get("departLane")!=y.get("departLane") or x.get("departSpeed")!=y.get("departSpeed") or x.get("departPos")!=y.get("departPos"):
                    fail(f"Pre-R actual departure mismatch: {vid}")
    through=lanechange_through(a_raw/"lanechanges.xml")
    for vid,t in rfcd.items():through[vid]=min(t,through.get(vid,t))
    if not through:fail("No actual R through-lane exposure")
    rids={v for v in sd["A"]["vehicles"] if route_class(v)=="R"}
    if set(through)!=rids:fail(f"R through coverage {len(through)}/{len(rids)}")
    out["first_R_through_s"]=min(through.values())
    out["R_through_unique_by_cutoff"]={str(t):sum(x<=t for x in through.values()) for t in (1440,1500,2700)}
    out["planned_inserted_arrived"]={arm:dict(Counter(route_class(v) for v in sd[arm]["vehicles"])) for arm in ("R0","A")}
    return out,trips,veh,through


def load_full_m(path):
    m={};rby=defaultdict(list);times=[]
    for _,step in ET.iterparse(path,events=("end",)):
        if step.tag!="timestep":continue
        t=int(float(step.get("time")))
        if times and t!=times[-1]+1:fail("Full FCD nonconsecutive")
        times.append(t)
        for v in step:
            vid=v.get("id","");c=route_class(vid)
            if c=="M":
                key=(vid,t)
                if key in m:fail(f"Duplicate full M FCD: {key}")
                m[key]=(v.get("lane"),float(v.get("x")),float(v.get("pos")),float(v.get("speed")))
            elif c=="R":rby[t].append((vid,float(v.get("x")),v.get("lane")))
        step.clear()
    if times!=list(range(HORIZON)):fail("Full FCD time coverage failed")
    return m,rby


def negative_control(m0,ma,rby,begin=592,end=606):
    rows=[]
    for t in range(begin,end):
        keys={key for key in set(m0)&set(ma) if key[1]==t}
        diff=[(vid,m0[(vid,t)],ma[(vid,t)]) for vid,_ in keys if m0[(vid,t)]!=ma[(vid,t)]]
        details=[]
        for vid,x,y in sorted(diff):
            nearest=min(((abs(y[1]-r[1]),y[1]-r[1],r[0]) for r in rby.get(t,())),default=None)
            details.append({"id":vid,"R0_x_m":x[1],"A_x_m":y[1],
                            "R0_speed_mps":x[3],"A_speed_mps":y[3],
                            "R0_lane":x[0],"A_lane":y[0],
                            "nearest_A_R_signed_gap_m":nearest[1] if nearest else None,
                            "nearest_A_R_id":nearest[2] if nearest else None})
        rows.append({"time_s":t,"common_M":len(keys),"different_M":len(diff),
                     "different_M_x_below_1000m":sum(x[1]<1000 for _,x,y in diff),
                     "different_M_x_below_1400m":sum(x[1]<1400 for _,x,y in diff),
                     "different_M_ahead_of_all_R":sum(bool(rby.get(t)) and y[1]>max(r[1] for r in rby[t]) for _,x,y in diff),
                     "different_ids":sorted(vid for vid,x,y in diff),"differences":details})
    return rows


def output_analysis(r0_raw,a_raw,sd,trips,through):
    m0,_=load_full_m(r0_raw/"fcd.xml")
    ma,rby=load_full_m(a_raw/"fcd.xml")
    # Existing fixed-cell function expects an 8-field tuple; append unused placeholders.
    adapt=lambda d:{key:(v[0],v[1],v[2],v[3],None,None,None,None) for key,v in d.items()}
    c0=core_bins(adapt(m0),"R0");ca=core_bins(adapt(ma),"A")
    contrast=compare_bins(c0,ca)
    paired=paired_trip_metrics(trips["R0"],trips["A"],sd["R0"]["vehicles"])
    neg=negative_control(m0,ma,rby)
    first_r=int(min(through.values()))
    relative=negative_control(m0,ma,rby,first_r,min(first_r+14,HORIZON))
    first_down={}
    for arm,m in (("R0",m0),("A",ma)):
        first={}
        for (vid,t),v in m.items():
            if v[0].startswith("main_down_"):first[vid]=min(t,first.get(vid,t))
        first_down[arm]={str(cut):sum(t<=cut for t in first.values()) for cut in (1440,1500,2700)}
    return {"fixed_cell_windows":whole_window(c0,"R0")+whole_window(ca,"A"),
            "full_M_route":summarize_trips(paired),"M_first_down_unique_by_cutoff":first_down,
            "negative_control":neg,"negative_control_at_sigma_R_entry":relative,
            "fixed_592_605_contains_sigma_R_entry":592<=first_r<=605,
            "R_through_unique_by_cutoff":{str(t):sum(x<=t for x in through.values()) for t in (1440,1500,2700)}},contrast,paired


def default_reference(r0_raw,a_raw):
    """Recompute only the fixed comparable diagnostics from bound default V2 raw."""
    m0,_=load_full_m(r0_raw/"fcd.xml")
    ma,rby=load_full_m(a_raw/"fcd.xml")
    adapt=lambda d:{key:(v[0],v[1],v[2],v[3],None,None,None,None) for key,v in d.items()}
    contrast=compare_bins(core_bins(adapt(m0),"R0"),core_bins(adapt(ma),"A"))
    active={}
    for cell in (14,15):
        rows=[r for r in contrast if r["cell"]==cell and r["window"]=="active"]
        active[str(cell)]={"negative_bins":sum(r["A_minus_R0_speed_mps"] is not None and r["A_minus_R0_speed_mps"]<0 for r in rows),
                           "total_bins":len(rows),
                           "R0_samples":sum(r["R0_M_samples"] for r in rows),
                           "A_samples":sum(r["A_M_samples"] for r in rows),
                           "R0_weighted_speed_mps":sum(r["R0_mean_speed_mps"]*r["R0_M_samples"] for r in rows if r["R0_M_samples"])/sum(r["R0_M_samples"] for r in rows),
                           "A_weighted_speed_mps":sum(r["A_mean_speed_mps"]*r["A_M_samples"] for r in rows if r["A_M_samples"])/sum(r["A_M_samples"] for r in rows)}
    return {"active_cells_14_15":active,"negative_control":negative_control(m0,ma,rby),
            "R0_FCD_sha256":digest(r0_raw/"fcd.xml"),"A_FCD_sha256":digest(a_raw/"fcd.xml")}


def write_csv(path,rows):
    with path.open("x",newline="") as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)


def run(args):
    package=args.sigma_package.resolve();base=args.default_package.resolve()
    r0raw=args.r0_raw.resolve();araw=args.a_raw.resolve()
    manifest,msha=verify_manifest(package)
    bmanifest,base_manifest_sha=verify_manifest(base)
    cards={};bcards={};binding={}
    for arm,cardpath,raw in (("R0",args.r0_card.resolve(),r0raw),("A",args.a_card.resolve(),araw)):
        sigma_arm=SIGMA_ARMS[arm]
        cards[arm],cardsha=verify_card(cardpath,package,sigma_arm,msha,raw)
        binding[arm]={"card_sha256":cardsha,**verify_raw(raw,cardsha,sigma_arm)}
    for arm,cardpath in (("R0",args.default_r0_card.resolve()),("A",args.default_a_card.resolve())):
        raw_root=Path(checked_json(cardpath).get("raw_root",""))
        bcards[arm],_=verify_card(cardpath,base,arm,base_manifest_sha,raw_root/arm/"outputs")
    if any(cards[arm].get("base_manifest_sha256")!=base_manifest_sha for arm in ("R0","A")):
        fail("Sigma card base-package manifest binding mismatch")
    sd=static_gate(package,base,cards,bcards)
    phase,trips,veh,through=phase1_gate(r0raw,araw,sd)
    outcome,contrast,paired=output_analysis(r0raw,araw,sd,trips,through)
    default_raw={arm:Path(bcards[arm]["raw_root"])/arm/"outputs" for arm in ("R0","A")}
    default_binding={}
    for arm in ("R0","A"):
        default_binding[arm]=verify_raw(default_raw[arm],digest(args.default_r0_card if arm=="R0" else args.default_a_card),arm)
    default_outcome=default_reference(default_raw["R0"],default_raw["A"])
    result={"status":"DESCRIPTIVE_SIGMA0_PAIR_ANALYZED_SCIENTIFIC_REVIEW_REQUIRED",
            "phase1":phase,"outcome":outcome,"default_V2_reference":default_outcome,
            "limitations":["M driving model changed; no default-model causal fraction is identified",
                           "Single seed; exact FCD equality is at serialized output precision",
                           "First divergence timing alone is not physical merge onset"],
            "provenance":{"sigma_input_manifest_sha256":msha,"default_input_manifest_sha256":base_manifest_sha,
            "cards_and_raw":binding,"default_cards_and_raw":default_binding,
            "default_cards_sha256":{arm:digest(path) for arm,path in (("R0",args.default_r0_card),("A",args.default_a_card))},
            "analysis_code_sha256":digest(Path(__file__))}}
    args.output_dir.mkdir(parents=True,exist_ok=False)
    (args.output_dir/"SIGMA0_DIAGNOSTIC.json").write_text(json.dumps(result,indent=2,sort_keys=True)+"\n")
    write_csv(args.output_dir/"M_CORE_CONTRAST_30S.csv",contrast)
    write_csv(args.output_dir/"M_TRIP_PAIRED.csv",paired)
    write_csv(args.output_dir/"NEGATIVE_CONTROL_592_605.csv",[{**r,"different_ids":";".join(r["different_ids"]),
                                                                    "differences":json.dumps(r["differences"],sort_keys=True)}
                                                                   for r in outcome["negative_control"]])
    return result


def main():
    p=argparse.ArgumentParser()
    for name in ("sigma_package","default_package","r0_card","a_card","default_r0_card","default_a_card","r0_raw","a_raw","output_dir"):
        p.add_argument("--"+name.replace("_","-"),type=Path,required=True)
    a=p.parse_args()
    try:
        result=run(a)
    except (GateFailure,ValueError,KeyError,ET.ParseError) as e:
        print(json.dumps({"status":"STOP_NOT_EVALUABLE","reason":str(e)}))
        raise SystemExit(2)
    print(json.dumps({"status":result["status"],"phase1":result["phase1"],"outcome":result["outcome"]["fixed_cell_windows"]},indent=2))


if __name__=="__main__":main()

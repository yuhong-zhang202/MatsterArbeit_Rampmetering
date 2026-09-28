#!/usr/bin/env python3
"""Fail-closed exploratory default-model A_OPEN versus B_MODERATE analysis.

Reads immutable outputs. B is eligible only after exact input and pre-R gates.
Incomplete vehicles and external waiting remain visible, never silently dropped.
"""
from __future__ import annotations

import argparse
import csv
import json
import statistics
from collections import Counter,defaultdict
from pathlib import Path
import xml.etree.ElementTree as ET

from analyze import detector_queue,digest,route_class
from analyze_a_outcome import core_bins,whole_window,xml_rows
from analyze_sigma0 import verify_manifest,verify_card,demand,normalized_xml,pre_and_r_fcd,lanechange_through,load_full_m,REQUIRED_RAW


def require(condition,message):
    if not condition:raise ValueError(message)


def verify_raw_allow_outcome_warnings(raw,card_sha,arm):
    rec=json.loads((raw/"execution_receipt.json").read_text())
    require(rec.get("arm")==arm and rec.get("card_sha256")==card_sha and rec.get("status")=="COMPLETED" and rec.get("return_code")==0,
            f"{arm} raw receipt status/card mismatch")
    files=rec.get("output_manifest",{})
    require(REQUIRED_RAW<=set(files),f"{arm} required raw output missing")
    for name,item in files.items():
        rel=Path(name);require(not rel.is_absolute() and ".." not in rel.parts,"Unsafe raw manifest path")
        p=raw/rel
        require(p.is_file() and p.stat().st_size==item.get("bytes") and digest(p)==item.get("sha256"),f"{arm} raw hash/size mismatch {name}")
    return {"receipt_sha256":digest(raw/"execution_receipt.json"),"verified_files":len(files),
            "sumo_error_lines":(raw/"sumo_error.log").read_text().splitlines()}


def normalized_add_without_program(path):
    root=ET.parse(path).getroot()
    def rec(e):
        attr=dict(e.attrib)
        for k,v in list(attr.items()):
            if k in ("file","dest","value") and "/" in v:attr[k]=Path(v).name
        if e.tag=="WAUT":attr["startProg"]="INTERVENTION_PROGRAM"
        return (e.tag,tuple(sorted(attr.items())),tuple(rec(z) for z in e))
    return rec(root)


def static_gate(package,acard,bcard):
    a=package/"A";b=package/"B"
    require((a/"demand.rou.xml").read_bytes()==(b/"demand.rou.xml").read_bytes(),"A/B demand bytes differ")
    da=demand(a/"demand.rou.xml");db=demand(b/"demand.rou.xml")
    require(da==db,"A/B demand semantics differ")
    require(normalized_xml(a/"scenario.sumocfg")==normalized_xml(b/"scenario.sumocfg"),"A/B SUMO config semantics differ")
    require(normalized_add_without_program(a/"scenario.add.xml")==normalized_add_without_program(b/"scenario.add.xml"),"A/B detector/additional semantics differ")
    programs=[]
    for arm in (a,b):
        r=ET.parse(arm/"scenario.add.xml").getroot()
        w=[e.get("startProg") for e in r.findall("WAUT")]
        require(len(w)==1,"Unexpected TLS program selector")
        programs+=w
    require(programs==["A_OPEN","B_MODERATE"],f"Wrong A/B programs: {programs}")
    for field in ("network_sha256","sumo_sha256","routes_schema_sha256","additional_schema_sha256","runner_sha256"):
        require(acard.get(field)==bcard.get(field),f"A/B card {field} differs")
    counts=Counter(route_class(v) for v in da["vehicles"])
    require(counts==Counter({"M":1396,"R":240,"U":150,"X":75}),f"Unexpected A/B planned counts: {counts}")
    return da


def tls_check(araw,braw):
    def rows(path):
        out=defaultdict(list)
        for _,e in ET.iterparse(path,events=("end",)):
            if e.tag=="tlsState":out[e.get("id")].append(dict(e.attrib));e.clear()
        return out
    x=rows(araw/"tls_states.xml");y=rows(braw/"tls_states.xml")
    require(set(x)==set(y) and all(len(x[k])==len(y[k])==2700 for k in x),"TLS state coverage differs")
    require(x["urban_tls"]==y["urban_tls"],"Urban TLS program differs unexpectedly")
    require(x["ramp_mid"]!=y["ramp_mid"],"Meter intervention not realized in TLS")
    return {"urban_tls_entries_identical":len(x["urban_tls"]),"ramp_mid_entries_per_arm":len(x["ramp_mid"]),"ramp_mid_programs_differ":True}


def phase1_gate(araw,braw,planned):
    fa,ra=pre_and_r_fcd(araw/"fcd.xml",True)
    fb,rb=pre_and_r_fcd(braw/"fcd.xml",True)
    require(fa==fb,f"A/B pre-R MUX FCD mismatch: A={len(fa)} B={len(fb)} common={len(set(fa)&set(fb))}")
    va=xml_rows(araw/"vehroute.xml","vehicle");vb=xml_rows(braw/"vehroute.xml","vehicle")
    ta=xml_rows(araw/"tripinfo.xml","tripinfo");tb=xml_rows(braw/"tripinfo.xml","tripinfo")
    for vid in planned["vehicles"]:
        xa,xb=va.get(vid),vb.get(vid)
        if xa is not None and xb is not None and (float(xa.get("depart","-1"))<540 or float(xb.get("depart","-1"))<540):
            require(all(xa.get(k)==xb.get(k) for k in ("depart","departLane","departPos","departSpeed")),f"Pre-R departure mismatch {vid}")
        elif vid in va and float(va[vid].get("depart","-1"))<540 or vid in vb and float(vb[vid].get("depart","-1"))<540:
            raise ValueError(f"Unmatched pre-R departure {vid}")
    for raw,r in ((araw,ra),(braw,rb)):
        for vid,t in lanechange_through(raw/"lanechanges.xml").items():r[vid]=min(t,r.get(vid,t))
    require(rb,"B has no actual R merge-section entry")
    phase={"pre_R_MUX_FCD_equal_rows":len(fa),"pre_R_by_class":dict(Counter(route_class(v) for v,t in fa)),
           "R_through":{"A":{str(t):sum(s<=t for s in ra.values()) for t in (1440,1500,2700)},
                        "B":{str(t):sum(s<=t for s in rb.values()) for t in (1440,1500,2700)}},
           "first_R_through_s":{"A":min(ra.values(),default=None),"B":min(rb.values())}}
    return phase,{"A":ta,"B":tb},{"A":va,"B":vb}


def compare_core(a,b):
    x={(r["cell"],r["begin"]):r for r in a};y={(r["cell"],r["begin"]):r for r in b}
    require(set(x)==set(y) and len(x)==450,"Core 450-bin coverage differs")
    out=[]
    for key in sorted(x):
        u,v=x[key],y[key]
        su,sv=u["M_mean_speed_mps"],v["M_mean_speed_mps"]
        out.append({"cell":key[0],"begin":key[1],"end":u["end"],"window":u["window"],
                    "A_M_samples":u["M_samples"],"B_M_samples":v["M_samples"],
                    "A_mean_speed_mps":su,"B_mean_speed_mps":sv,
                    "B_minus_A_speed_mps":sv-su if su is not None and sv is not None else None,
                    "A_mean_count":u["M_mean_simultaneous_count"],"B_mean_count":v["M_mean_simultaneous_count"],
                    "B_minus_A_mean_count":v["M_mean_simultaneous_count"]-u["M_mean_simultaneous_count"],
                    "A_density_veh_per_km":u["M_density_veh_per_km"],"B_density_veh_per_km":v["M_density_veh_per_km"]})
    return out


def cohort_rows(planned,trips,veh):
    rows=[]
    for vid in sorted(planned["vehicles"]):
        c=route_class(vid);d=float(planned["vehicles"][vid]["depart"])
        a=trips["A"].get(vid);b=trips["B"].get(vid)
        for arm,t,v in (("A",a,veh["A"].get(vid)),("B",b,veh["B"].get(vid))):
            actual=float(t["depart"]) if t is not None and float(t.get("depart","-1"))>=0 else None
            arrived=v is not None and float(v.get("arrival","-1"))>=0
            rows.append({"id":vid,"class":c,"arm":arm,"planned_depart_s":d,
                         "actual_depart_s":actual,"external_depart_delay_s":float(t["departDelay"]) if actual is not None and t.get("departDelay") is not None else None,
                         "arrived":arrived,"unfinished_or_not_inserted":not arrived,
                         "observed_residence_s":float(t["duration"]) if t is not None and t.get("duration") is not None and actual is not None else None,
                         "completed_duration_s":float(t["duration"]) if arrived and t is not None else None,
                         "completed_timeLoss_s":float(t["timeLoss"]) if arrived and t is not None else None})
    return rows


def summarize_cohort(rows):
    out=[]
    for arm in ("A","B"):
        for c in "MRUX":
            z=[r for r in rows if r["arm"]==arm and r["class"]==c]
            complete=[r for r in z if r["arrived"]]
            inserted=[r for r in z if r["actual_depart_s"] is not None]
            out.append({"arm":arm,"class":c,"planned":len(z),"inserted":len(inserted),"arrived":len(complete),
                        "unfinished_or_not_inserted":len(z)-len(complete),
                        "external_delay_mean_inserted_s":statistics.mean(r["external_depart_delay_s"] for r in inserted) if inserted else None,
                        "completed_residence_mean_s":statistics.mean(r["completed_duration_s"] for r in complete) if complete else None,
                        "completed_timeLoss_mean_s":statistics.mean(r["completed_timeLoss_s"] for r in complete) if complete else None,
                        "complete_cohort_mean_available":len(complete)==len(z)})
    return out


def queue_bins(araw,braw):
    out=[]
    for arm,raw in (("A",araw),("B",braw)):
        for name in ("ramp_storage_e2.xml","shared_boundary_e2.xml"):
            for r in detector_queue(raw/name):out.append({"arm":arm,"detector":name,**r})
    require(len(out)==360,"Two-arm two-detector 30s coverage incomplete")
    return out


def first_down(m):
    first={}
    for (vid,t),row in m.items():
        if row[0].startswith("main_down_"):first[vid]=min(t,first.get(vid,t))
    return {str(c):sum(t<=c for t in first.values()) for c in (1440,1500,2700)}


def write_csv(path,rows):
    with path.open("x",newline="") as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)


def run(args):
    p=args.package.resolve();araw=args.a_raw.resolve();braw=args.b_raw.resolve()
    _,msha=verify_manifest(p)
    ac,asha=verify_card(args.a_card.resolve(),p,"A",msha,araw)
    bc,bsha=verify_card(args.b_card.resolve(),p,"B",msha,braw)
    planned=static_gate(p,ac,bc)
    rawcheck={"A":verify_raw_allow_outcome_warnings(araw,asha,"A"),"B":verify_raw_allow_outcome_warnings(braw,bsha,"B")}
    phase,trips,veh=phase1_gate(araw,braw,planned)
    tls=tls_check(araw,braw)
    ma,_=load_full_m(araw/"fcd.xml");mb,_=load_full_m(braw/"fcd.xml")
    adapt=lambda d:{k:(v[0],v[1],v[2],v[3],None,None,None,None) for k,v in d.items()}
    ca=core_bins(adapt(ma),"A");cb=core_bins(adapt(mb),"B")
    core=compare_core(ca,cb)
    cohort=cohort_rows(planned,trips,veh)
    queues=queue_bins(araw,braw)
    summary={"status":"DESCRIPTIVE_DEFAULT_A_B_ANALYSIS_SCIENTIFIC_REVIEW_REQUIRED",
             "phase1":phase,"TLS":tls,"raw_integrity":rawcheck,
             "fixed_windows":whole_window(ca,"A")+whole_window(cb,"B"),
             "class_lifecycle_cost":summarize_cohort(cohort),
             "M_first_down_unique_by_cutoff":{"A":first_down(ma),"B":first_down(mb)},
             "queue_detector_summary":[{"arm":arm,"detector":name,
                 "max_jam_vehicles":max(r["max_jam_vehicles"] for r in queues if r["arm"]==arm and r["detector"]==name),
                 "jam_positive_bins":sum(r["max_jam_vehicles"]>0 for r in queues if r["arm"]==arm and r["detector"]==name)}
                 for arm in ("A","B") for name in ("ramp_storage_e2.xml","shared_boundary_e2.xml")],
             "provenance":{"input_manifest_sha256":msha,"A_card_sha256":asha,"B_card_sha256":bsha,
                           "A_FCD_sha256":digest(araw/"fcd.xml"),"B_FCD_sha256":digest(braw/"fcd.xml"),
                           "analysis_code_sha256":digest(Path(__file__))}}
    args.output_dir.mkdir(parents=True,exist_ok=False)
    (args.output_dir/"A_B_SUMMARY.json").write_text(json.dumps(summary,indent=2,sort_keys=True)+"\n")
    write_csv(args.output_dir/"M_CORE_30S_CONTRAST.csv",core)
    write_csv(args.output_dir/"CLASS_COMPLETE_COHORT.csv",cohort)
    write_csv(args.output_dir/"QUEUE_E2_30S.csv",queues)
    return summary


def main():
    p=argparse.ArgumentParser()
    for name in ("package","a_card","b_card","a_raw","b_raw","output_dir"):
        p.add_argument("--"+name.replace("_","-"),type=Path,required=True)
    a=p.parse_args()
    try:x=run(a)
    except (ValueError,KeyError,ET.ParseError,FileNotFoundError) as e:
        print(json.dumps({"status":"STOP_NOT_EVALUABLE","reason":str(e)}));raise SystemExit(2)
    print(json.dumps({k:x[k] for k in ("status","phase1","fixed_windows","class_lifecycle_cost","queue_detector_summary")},indent=2))


if __name__=="__main__":main()

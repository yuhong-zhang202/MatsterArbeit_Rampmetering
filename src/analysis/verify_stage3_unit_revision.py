"""Independent check that aggregate revision_03 changes only the approved unit label."""
from __future__ import annotations
import argparse, csv, hashlib, json
from pathlib import Path

def records(path):
    with path.open(encoding="utf-8",newline="") as h: return list(csv.DictReader(h))
def digest(path): return hashlib.sha256(path.read_bytes()).hexdigest()

def main():
    p=argparse.ArgumentParser(); p.add_argument("--root",required=True); p.add_argument("--output",required=True); a=p.parse_args()
    root=Path(a.root); out=Path(a.output)
    if out.exists(): raise FileExistsError(out)
    old_d=root/"data/processed/stage3_baseline_diagnostic_20260912_v2/aggregate/revision_02"
    new_d=root/"data/processed/stage3_baseline_diagnostic_20260912_v2/aggregate/revision_03"
    old_t=root/"results/tables/stage3_baseline_diagnostic_20260912_v2/aggregate/revision_02"
    new_t=root/"results/tables/stage3_baseline_diagnostic_20260912_v2/aggregate/revision_03"
    unchanged=[]
    for name in ["aggregation_timeseries.csv","condition_event_sets.json","endpoint_accounting.csv","propagation_event_sets.json","sensitivity.csv"]:
        if digest(old_d/name)!=digest(new_d/name): raise AssertionError(name)
        unchanged.append(name)
    for name in ["coverage_audit.csv","lane_class_timeline.csv","spatial_propagation_evidence.csv","stopping_episodes.csv"]:
        if digest(old_t/name)!=digest(new_t/name): raise AssertionError(name)
        unchanged.append(name)
    before,after=records(old_t/"condition_evidence_summary.csv"),records(new_t/"condition_evidence_summary.csv")
    if len(before)!=len(after): raise AssertionError("row count")
    changed=[]
    for index,(first,second) in enumerate(zip(before,after)):
        differences={key:(first[key],second[key]) for key in first if first[key]!=second[key]}
        if differences:
            if differences!={"unit":("sampled_vehicle_presence_s","sampled_region_stop_support_s")} or first["metric"]!="stopped_episode_support":
                raise AssertionError((index,differences))
            changed.append(index)
    if len(changed)!=355: raise AssertionError(len(changed))
    review=root/"data/processed/stage3_baseline_diagnostic_20260912_v2/analysis_review/revision_05"
    stale=[]
    for name in ("same_seed_contrasts.csv","seed_sign_consistency.csv"):
        stale += [r for r in records(review/name) if r.get("metric")=="stopped_episode_support" and r.get("unit")!="sampled_region_stop_support_s"]
    if stale: raise AssertionError("review retained stale unit")
    payload={"schema_version":1,"status":"passed","changed_rows":355,"numeric_values_changed":0,
             "only_changed_field":"unit","new_unit":"sampled_region_stop_support_s",
             "unchanged_files":unchanged,"review_unit_check":"passed","actual_sumo_starts":0}
    out.parent.mkdir(parents=True,exist_ok=True)
    with out.open("x",encoding="utf-8") as h: json.dump(payload,h,indent=2); h.write("\n")
    print(json.dumps(payload,sort_keys=True)); return 0
if __name__=="__main__": raise SystemExit(main())

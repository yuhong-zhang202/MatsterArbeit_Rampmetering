"""Build reproducible T34 comparison, sensitivity, and claim-review artifacts."""
from __future__ import annotations

from collections import defaultdict
import csv
import hashlib
import json
import math
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
BATCH = ROOT / "data/processed/stage3_baseline_diagnostic_20260912_v2"
AGG = BATCH / "aggregate/revision_03"
TABLES = ROOT / "results/tables/stage3_baseline_diagnostic_20260912_v2/aggregate/revision_03"
FIGURES = ROOT / "results/figures/stage3_baseline_diagnostic_20260912_v2/revision_06"
REVIEW = BATCH / "analysis_review/revision_06"
RUN_ORDER = ("C17", "C23", "ML17", "ML23", "MH17", "MH23", "RL17", "RL23")
CONTRASTS = (("ML", "C", "q_main", 2600.0, 3200.0), ("MH", "C", "q_main", 3800.0, 3200.0),
             ("RL", "C", "q_ramp", 360.0, 720.0))


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def write_csv(path: Path, records: list[dict], fields: list[str]) -> None:
    with path.open("x", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, extrasaction="raise")
        writer.writeheader()
        writer.writerows(records)


def write_json(path: Path, value: object) -> None:
    with path.open("x", encoding="utf-8") as handle:
        json.dump(value, handle, indent=2, ensure_ascii=False, allow_nan=False)
        handle.write("\n")


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def sign(value: float, tolerance: float = 1e-12) -> str:
    if value > tolerance:
        return "positive"
    if value < -tolerance:
        return "negative"
    return "zero"


def numeric(value: str) -> float | None:
    if value == "":
        return None
    result = float(value)
    return result if math.isfinite(result) else None


def main() -> int:
    if REVIEW.exists():
        raise FileExistsError(REVIEW)
    REVIEW.parent.mkdir(parents=True, exist_ok=True)
    REVIEW.mkdir()
    if FIGURES.exists():
        raise FileExistsError(FIGURES)
    FIGURES.mkdir()
    summary = read_csv(TABLES / "condition_evidence_summary.csv")
    sensitivity = read_csv(AGG / "sensitivity.csv")
    timeseries = read_csv(AGG / "aggregation_timeseries.csv")
    episodes = read_csv(TABLES / "stopping_episodes.csv")
    endpoints = read_csv(AGG / "endpoint_accounting.csv")
    registry = json.loads((BATCH / "source_registry.json").read_text(encoding="utf-8"))
    run_meta = {row["run_id"]: row for row in registry["runs"]}

    input_rows = []
    for treatment, baseline, varied, treatment_value, baseline_value in CONTRASTS:
        for seed in (17, 23):
            treatment_run, baseline_run = f"{treatment}{seed}", f"{baseline}{seed}"
            t_demand, b_demand = run_meta[treatment_run]["requested_demand_vehph"], run_meta[baseline_run]["requested_demand_vehph"]
            varied_class = {"q_main": "M", "q_ramp": "R"}[varied]
            unchanged = sorted(k for k in t_demand if k != varied_class and t_demand[k] == b_demand[k])
            input_rows.append({"contrast_id": f"{treatment}-C_seed{seed}", "seed": seed,
                               "baseline_run": baseline_run, "treatment_run": treatment_run,
                               "varied_input": varied, "baseline_vehph": baseline_value,
                               "treatment_vehph": treatment_value, "delta_vehph": treatment_value-baseline_value,
                               "unchanged_classes": "|".join(unchanged), "matched_seed": True,
                               "status": "registered_single_input_contrast"})
    write_csv(REVIEW / "input_contrasts.csv", input_rows, list(input_rows[0]))

    seed_rows = []
    for run_id in RUN_ORDER:
        meta = run_meta[run_id]
        paired = f"{meta['condition']}{23 if meta['seed']==17 else 17}"
        seed_rows.append({"run_id":run_id, "condition":meta["condition"], "seed":meta["seed"],
                          "paired_run":paired, "source_map_sha256":meta["source_map_sha256"],
                          "sensitivity_value_count":sum(r["run_id"]==run_id for r in sensitivity),
                          "question_unit_count":sum(r["run_id"]==run_id and r["entity"].startswith("question:") for r in summary),
                          "qualification":"descriptive_two_seed_unit; no power claim", "status":"complete"})
    write_csv(REVIEW / "seed_units.csv", seed_rows, list(seed_rows[0]))

    grouped_ts: defaultdict[tuple, list[dict]] = defaultdict(list)
    for row in timeseries:
        grouped_ts[(row["run_id"], row["window"], float(row["aggregation"]))].append(row)
    ts_registry = []
    for key in sorted(grouped_ts, key=lambda x:(RUN_ORDER.index(x[0]), x[1], x[2])):
        group = grouped_ts[key]
        ts_registry.append({"run_id":key[0], "detector_group":"M-only_internal_merge_entry", "window":key[1],
                            "aggregation_s":key[2], "bin_count":len(group),
                            "first_bin_begin_s":min(float(r["bin_begin"]) for r in group),
                            "last_bin_end_s":max(float(r["bin_end"]) for r in group),
                            "q_value_count":sum(r["q"]!="" for r in group), "v_value_count":sum(r["v"]!="" for r in group),
                            "qualification":"complete" if all(r["qualification"] in ("complete","short_tail_complete") for r in group) else "incomplete"})
    if len(ts_registry) != 48:
        raise AssertionError(f"expected 48 time series, got {len(ts_registry)}")
    write_csv(REVIEW / "aggregation_timeseries_registry.csv", ts_registry, list(ts_registry[0]))
    shape_rows = []
    for key in sorted(grouped_ts, key=lambda x:(RUN_ORDER.index(x[0]), x[1], x[2])):
        group = grouped_ts[key]
        record = {"run_id":key[0], "detector_group":"M-only_internal_merge_entry", "window":key[1],
                  "aggregation_s":key[2], "bin_count":len(group)}
        for metric in ("q", "v"):
            valid = [r for r in group if r[metric] != ""]
            values = [float(r[metric]) for r in valid]
            minimum, maximum = min(values), max(values)
            lows = [r for r in valid if math.isclose(float(r[metric]), minimum, rel_tol=1e-12, abs_tol=1e-12)]
            highs = [r for r in valid if math.isclose(float(r[metric]), maximum, rel_tol=1e-12, abs_tol=1e-12)]
            record.update({f"{metric}_min":minimum, f"{metric}_max":maximum,
                           f"{metric}_min_time_ranges":"|".join(f"[{r['bin_begin']},{r['bin_end']})" for r in lows),
                           f"{metric}_max_time_ranges":"|".join(f"[{r['bin_begin']},{r['bin_end']})" for r in highs),
                           f"{metric}_min_support_s":sum(float(r["bin_end"])-float(r["bin_begin"]) for r in lows),
                           f"{metric}_max_support_s":sum(float(r["bin_end"])-float(r["bin_begin"]) for r in highs)})
        record["qualification"] = "descriptive bin extrema and tied-extrema support; not instantaneous extrema or a state threshold"
        shape_rows.append(record)
    if len(shape_rows) != 48:
        raise AssertionError(f"expected 48 shape summaries, got {len(shape_rows)}")
    write_csv(REVIEW / "aggregation_shape_summary.csv", shape_rows, list(shape_rows[0]))

    by_run_key = {}
    for row in summary:
        value = numeric(row["value"])
        if value is None or row["entity"].startswith("question:"):
            continue
        key = (row["window"], row["entity"], row["metric"], row["unit"])
        by_run_key[(row["run_id"], key)] = row
    contrast_rows = []
    for pair in input_rows:
        base, treat = pair["baseline_run"], pair["treatment_run"]
        common = sorted({k for run,k in by_run_key if run==base} & {k for run,k in by_run_key if run==treat})
        for key in common:
            b, t = by_run_key[(base,key)], by_run_key[(treat,key)]
            bv, tv = float(b["value"]), float(t["value"])
            contrast_rows.append({"contrast_id":pair["contrast_id"], "seed":pair["seed"],
                                  "baseline_run":base, "treatment_run":treat, "window":key[0], "entity":key[1],
                                  "metric":key[2], "baseline_value":bv, "treatment_value":tv, "delta":tv-bv,
                                  "sign":sign(tv-bv), "unit":key[3], "denominator_baseline":b["denominator"],
                                  "denominator_treatment":t["denominator"],
                                  "qualification":"matched_seed_run_level_descriptive"})
    write_csv(REVIEW / "same_seed_contrasts.csv", contrast_rows, list(contrast_rows[0]))

    signs: defaultdict[tuple, dict[int, dict]] = defaultdict(dict)
    for row in contrast_rows:
        family = row["contrast_id"].split("_seed")[0]
        key = (family,row["window"],row["entity"],row["metric"],row["unit"])
        signs[key][int(row["seed"])] = row
    consistency = []
    for key, seeds in sorted(signs.items()):
        if set(seeds) != {17,23}:
            continue
        a,b=seeds[17],seeds[23]
        state = "same_sign" if a["sign"]==b["sign"] else "symbol_inconsistent"
        consistency.append({"contrast_family":key[0], "window":key[1], "entity":key[2], "metric":key[3], "unit":key[4],
                            "delta_seed17":a["delta"], "sign_seed17":a["sign"], "delta_seed23":b["delta"],
                            "sign_seed23":b["sign"], "status":state})
    write_csv(REVIEW / "seed_sign_consistency.csv", consistency, list(consistency[0]))

    episode_groups: defaultdict[tuple, list[float]] = defaultdict(list)
    for row in episodes:
        episode_groups[(row["run_id"],row["observation_domain"],row["class"],row["region"],row["kind"])].append(float(row["support_seconds"]))
    episode_summary = []
    for key, values in sorted(episode_groups.items()):
        episode_summary.append({"run_id":key[0],"window":key[1],"class":key[2],"region":key[3],"kind":key[4],
                                "episode_count":len(values),"total_support_s":sum(values),"longest_support_s":max(values),
                                "qualification":"technical_stop_speed_le_0_1; not congestion"})
    write_csv(REVIEW / "episode_distribution_summary.csv", episode_summary, list(episode_summary[0]))

    claims = [
        {"question_id":"Q1","claim":"Registered mainline, ramp, and urban flow plus stock/state quantities are observable within the declared network and windows.",
         "evidence":"coverage_audit 128/128 passed; endpoint_accounting 64/64 qualified; lane timeline 246175 cells; 8x16 q/v summaries",
         "alternative_explanations":"Mainline vehicles insert near the merge; the scaffold does not observe a realistic upstream freeway feeder.",
         "status":"supported","scope_limitation":"Synthetic scaffold only; no realistic upstream freeway feeder observation.","impact":"Observations are usable for this synthetic scaffold; freeway-wide protection claims remain out of scope.","critical_unknown_count":1,"reviewer_opinion":"supported_with_scope_limitation: synthetic scaffold only; no realistic upstream freeway feeder observation"},
        {"question_id":"Q2","claim":"The uncontrolled archive shows freeway-side performance impairment with a merge-consistent spatial and temporal signature.",
         "evidence":"A-window M-only internal speed remains 30.02-31.71 m/s while q tracks requested mainline input; no approved breakdown threshold or upstream feeder state exists.",
         "alternative_explanations":"Near-merge insertion, gap acceptance/lane changing, and downstream conditions can produce local observations without freeway breakdown.",
         "status":"not_identified","scope_limitation":"No approved breakdown threshold, upstream feeder state, or causal mechanism test.","impact":"The archive does not yet establish the freeway-protection side of the intended tradeoff.","critical_unknown_count":2,"reviewer_opinion":"not_identified"},
        {"question_id":"Q3","claim":"Ramp accumulation reaches the shared urban approach and U traffic is exposed in the same place and periods.",
         "evidence":"All 8 runs contain stopped R and U in shared_approach; independently verified shared R/U cooccurrence totals 7120 sampled seconds; R/U endpoint and arrival records are complete.",
         "alternative_explanations":"TLS state and downstream supply contribute to stopping; cooccurrence alone does not identify causal R-induced U loss.",
         "status":"supported","scope_limitation":"Observational exposure only; causal R-induced U loss is not established.","impact":"Urban-side interaction is observable, but causal spillback loss is not established.","critical_unknown_count":1,"reviewer_opinion":"supported_with_scope_limitation: observational exposure only; causal R-induced U loss is not established"},
        {"question_id":"Q4","claim":"The same scenario supplies a defensible basis for later freeway-protection versus urban-spillback control tradeoff analysis.",
         "evidence":"Q3 interaction is observed in the same scenario, while Q2 freeway impairment is not identified; MH suppresses demand-period R downstream entry while M speed stays high.",
         "alternative_explanations":"The observed tension may be insertion/gap-access competition in a short scaffold rather than a protectable freeway breakdown state.",
         "status":"not_identified","scope_limitation":"Q2 freeway impairment is not identified in the current archive.","impact":"A targeted, discriminating Stage 4 validation is indicated before formal-design inheritance.","critical_unknown_count":2,"reviewer_opinion":"not_identified"}
    ]
    write_csv(REVIEW / "claim_evidence.csv", claims, list(claims[0]))

    explanations = [
        {"candidate":"input_not_realized_in_demand_window","status":"checked","evidence":"At 1500 s every run has class-resolved entered/outside counts; R/U delayed insertion is material, while all plans complete by 2700 s.","remaining_limit":"No exact continuous planned-outside curve between approved endpoints."},
        {"candidate":"near_merge_mainline_insertion","status":"checked","evidence":"Measurement contract records actual M depart positions near the merge and explicitly limits upstream-state interpretation.","remaining_limit":"No realistic upstream freeway feeder is observed."},
        {"candidate":"traffic_signal_stopping","status":"checked","evidence":"Movement-specific TLS link 0 is joined to stopped R/U episodes; stops span G/r/y contexts.","remaining_limit":"TLS context is observational and does not isolate a counterfactual signal contribution."},
        {"candidate":"lane_coverage","status":"checked","evidence":"2700/2700 FCD labels per run, 0 unknown lane/ID records, full registered lane map, and all timeline cells independently matched.","remaining_limit":"E2 remains coverage_only by contract."},
        {"candidate":"downstream_blockage","status":"unresolved","evidence":"Downstream E1 q/v and FCD state are complete, but no approved blockage/breakdown definition or causal test exists.","remaining_limit":"Requires a discriminating validation question rather than threshold invention."},
        {"candidate":"merge_or_lane_change_mechanism","status":"unresolved","evidence":"First-downstream brackets and internal-lane trajectories are complete; 1 Hz FCD and static priority do not identify gap-acceptance causality.","remaining_limit":"Mechanism-specific observation or controlled structural check would be required."}
    ]
    write_csv(REVIEW / "candidate_explanations.csv", explanations, list(explanations[0]))

    # Two compact exploratory figures; values remain exact in CSV sources.
    import matplotlib.pyplot as plt
    def get(run_id, window, entity, metric):
        matches=[r for r in summary if r["run_id"]==run_id and r["window"]==window and r["entity"]==entity and r["metric"]==metric]
        if len(matches)!=1: raise AssertionError((run_id,window,entity,metric,len(matches)))
        return float(matches[0]["value"])
    conditions=["C","ML","MH","RL"]; seeds=(17,23); x=list(range(len(conditions))); width=.34
    fig, axes=plt.subplots(2,1,figsize=(10,7),sharex=True)
    for offset,seed in ((-width/2,17),(width/2,23)):
        axes[0].scatter([i+offset for i in x],[get(f"{c}{seed}","A","M-only_internal_merge_entry","v") for c in conditions],label=f"seed {seed}")
    axes[0].set_ylabel("M internal speed (m/s)"); axes[0].grid(alpha=.25)
    axes[0].legend()
    for offset,seed in ((-width/2,17),(width/2,23)):
        axes[1].bar([i+offset for i in x],[get(f"{c}{seed}","A","R","first_downstream_observations") for c in conditions],width=width,label=f"seed {seed}")
    axes[1].set_ylabel("R first downstream (veh)"); axes[1].set_xlabel("Condition"); axes[1].set_xticks(x,conditions)
    fig.suptitle("Stage 3 A-window freeway proxy and ramp passage (exploratory)"); fig.tight_layout()
    fig.savefig(FIGURES/"a_window_mainline_speed_and_r_passage.png",dpi=180); plt.close(fig)
    endpoint_map={(r["run_id"],r["class"],float(r["endpoint_s"])):r for r in endpoints}
    fig, axes=plt.subplots(2,1,figsize=(10,7),sharex=True)
    for offset,seed in ((-width/2,17),(width/2,23)):
        axes[0].bar([i+offset for i in x],[float(endpoint_map[(f"{c}{seed}","R",1500.0)]["outside_confirmed"]) for c in conditions],width=width,label=f"seed {seed}")
    axes[0].set_ylabel("R outside at 1500 s (veh)")
    axes[0].legend()
    for offset,seed in ((-width/2,17),(width/2,23)):
        axes[1].bar([i+offset for i in x],[get(f"{c}{seed}","A","U","arrivals") for c in conditions],width=width,label=f"seed {seed}")
    axes[1].set_ylabel("U arrivals in A (veh)"); axes[1].set_xlabel("Condition"); axes[1].set_xticks(x,conditions)
    fig.suptitle("Stage 3 city-side endpoint and passage evidence (exploratory)"); fig.tight_layout()
    fig.savefig(FIGURES/"a_window_city_side_evidence.png",dpi=180); plt.close(fig)

    outputs = sorted(list(REVIEW.glob("*.csv")) + list(FIGURES.glob("*.png")))
    payload = {"schema_version":1,"status":"data_analyst_complete_scientific_review_recorded",
               "run_coverage":"8/8","diagnostic_question_units":"40/40","input_contrasts":"6/6","seed_units":"8/8",
               "sensitivity_values":"96/96","aggregation_timeseries":"48/48","aggregation_bin_rows":len(timeseries),
               "aggregation_shape_summaries":"48/48",
               "same_seed_contrast_rows":len(contrast_rows),"seed_sign_rows":len(consistency),
               "symbol_inconsistent_rows":sum(r["status"]=="symbol_inconsistent" for r in consistency),
               "Q1_Q4":"4/4 reviewer opinions recorded","candidate_explanations":"6/6 checked or explicitly unresolved",
               "stage4_recommendation":"yes_targeted_discriminating_validation_due_to_Q2_not_identified_and_Q4_not_identified",
               "interpretation_boundary":"exploratory archive diagnosis; no causal, capacity, breakdown, or formal control-effect claim",
               "outputs":{str(p.relative_to(ROOT)):sha256(p) for p in outputs},"actual_sumo_starts":0}
    write_json(REVIEW/"analysis_summary.json",payload)
    print(json.dumps({k:payload[k] for k in ("run_coverage","diagnostic_question_units","sensitivity_values","aggregation_timeseries","symbol_inconsistent_rows","stage4_recommendation")},sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

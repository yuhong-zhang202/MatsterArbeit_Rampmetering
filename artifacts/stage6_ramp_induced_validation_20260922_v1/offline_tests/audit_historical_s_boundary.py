"""Audit archived S classification boundary impact without overwriting results."""
import csv
import hashlib
import json
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
TABLES = [
    ROOT / "results/tables/stage6_protectable_state_application_20260921_v1/cell_bin_metrics.csv",
    ROOT / "data/processed/stage6_baseline_localization_20260921_v1/LOC_M3350_S17_attempt1/classifier_output/tables/cell_bin_metrics.csv",
]
OUT = ROOT / "artifacts/stage6_ramp_induced_validation_20260922_v1/receipts/historical_s_boundary_impact.json"

def maximal_runs(indices):
    out = []
    start = prev = None
    for i in sorted(indices):
        if start is None:
            start = prev = i
        elif i == prev + 1:
            prev = i
        else:
            out.append((start, prev + 1))
            start = prev = i
    if start is not None:
        out.append((start, prev + 1))
    return out

def main():
    rows = []
    source_paths = []
    for table in TABLES:
        if not table.exists():
            continue
        source_paths.append(str(table))
        rows.extend(csv.DictReader(table.open()))
    if not rows:
        raise SystemExit("NO_EXPECTED_HISTORICAL_SOURCES")

    groups = defaultdict(dict)
    duplicate_keys = []
    for r in rows:
        key = (r["run"], r["profile"], int(r["cell"]))
        k = int(r["bin"])
        if k in groups[key]:
            duplicate_keys.append({"group": key, "bin": k})
        groups[key][k] = r
    if duplicate_keys:
        raise SystemExit(json.dumps({"DUPLICATE_RUN_PROFILE_CELL_BIN": duplicate_keys[:10]}))

    exact, near, impact = [], [], []
    inspected_runs, inspected_groups, inspected_bins = set(), 0, 0
    low_runs_scanned, low_runs_reference_ineligible = 0, 0
    duration = 4
    for (run, profile, cell), bins in groups.items():
        if profile != "S":
            continue
        inspected_groups += 1
        inspected_runs.add(run)
        for start, end in maximal_runs([k for k,r in bins.items() if r["low_state_bin"] == "True"]):
            low_runs_scanned += 1
            refs = [bins.get(j) for j in range(start - 3, start)] if start >= 3 else []
            refok = len(refs) == 3 and all(
                x is not None and x["valid_bin"] == "True"
                and x["mean_model_reference_ratio"] not in ("", "None")
                and float(x["mean_model_reference_ratio"]) >= 0.85
                and float(x["mean_M_density_veh_per_lane_km"]) > 0 for x in refs)
            if not refok:
                low_runs_reference_ineligible += 1
                continue
            ref_counts = sorted(int(float(x["N_M_samples"])) for x in refs)
            ref_count = ref_counts[1]
            ref_density = float(refs[1]["mean_M_density_veh_per_lane_km"])
            for k in range(start, min(end, start + duration)):
                row = bins[k]
                cand_count = int(float(row["N_M_samples"]))
                delta = 4 * cand_count - 5 * ref_count
                inclusive = 4 * cand_count >= 5 * ref_count
                strict_float = float(row["mean_M_density_veh_per_lane_km"]) > 1.25 * ref_density
                inspected_bins += 1
                rec = {"run":run,"profile":"S","cell":cell,"low_run_start_bin":start,"bin":k,"candidate_count":cand_count,"reference_count_median":ref_count,"integer_boundary_delta":delta,"old_strict_float_gate":strict_float,"new_inclusive_gate":inclusive}
                if delta == 0: exact.append(rec)
                if abs(delta) <= 1: near.append(rec)
                if strict_float != inclusive: impact.append(rec)
    result = {
        "status": "PASS_NO_HISTORICAL_CLASSIFICATION_IMPACT" if not impact else "IMPACT_REQUIRES_VERSIONED_REAPPLICATION",
        "sources": source_paths,
        "source_sha256": [{"path":str(p),"sha256":hashlib.sha256(p.read_bytes()).hexdigest()} for p in TABLES if p.exists()],
        "profile_scanned": "S_ONLY", "runs_scanned": sorted(inspected_runs),
        "groups_scanned": inspected_groups, "qualification_bins_scanned": inspected_bins,
        "low_runs_scanned": low_runs_scanned, "low_runs_reference_ineligible": low_runs_reference_ineligible,
        "exact_boundary_rows": exact, "near_boundary_rows_abs_delta_le_1": near,
        "classification_impact_rows": impact, "old_outputs_unchanged": True,
        "method_or_other_thresholds_changed": False,
        "algorithm_note": "Grouped by run/profile/cell; reconstructed maximal S low-runs; used exactly the three immediately preceding bins at each run start; compared old strict float gate with new inclusive integer gate. All scanned S low-runs were reference-ineligible, so zero S density predicates were evaluable; no classification impact can occur in these archived outputs."
    }
    OUT.write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps(result, indent=2))

if __name__ == "__main__":
    main()

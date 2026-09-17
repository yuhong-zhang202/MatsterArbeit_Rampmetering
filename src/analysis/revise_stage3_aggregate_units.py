"""Create a non-overwriting aggregate revision correcting one unit label only."""
from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path
import shutil

ROOT = Path(__file__).resolve().parents[2]
SOURCE_DATA = ROOT / "data/processed/stage3_baseline_diagnostic_20260912_v2/aggregate/revision_02"
SOURCE_TABLES = ROOT / "results/tables/stage3_baseline_diagnostic_20260912_v2/aggregate/revision_02"
TARGET_DATA = ROOT / "data/processed/stage3_baseline_diagnostic_20260912_v2/aggregate/revision_03"
TARGET_TABLES = ROOT / "results/tables/stage3_baseline_diagnostic_20260912_v2/aggregate/revision_03"

def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()

def main() -> int:
    for target in (TARGET_DATA, TARGET_TABLES):
        if target.exists(): raise FileExistsError(target)
        target.mkdir()
    unchanged_data = ["aggregation_timeseries.csv", "condition_event_sets.json", "endpoint_accounting.csv", "propagation_event_sets.json", "sensitivity.csv"]
    unchanged_tables = ["coverage_audit.csv", "lane_class_timeline.csv", "spatial_propagation_evidence.csv", "stopping_episodes.csv"]
    for name in unchanged_data:
        shutil.copyfile(SOURCE_DATA/name, TARGET_DATA/name)
        assert digest(SOURCE_DATA/name) == digest(TARGET_DATA/name)
    for name in unchanged_tables:
        shutil.copyfile(SOURCE_TABLES/name, TARGET_TABLES/name)
        assert digest(SOURCE_TABLES/name) == digest(TARGET_TABLES/name)
    source_summary = SOURCE_TABLES / "condition_evidence_summary.csv"
    target_summary = TARGET_TABLES / "condition_evidence_summary.csv"
    with source_summary.open(encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle); fields = reader.fieldnames; records = list(reader)
    corrected = 0
    before_values = []
    for row in records:
        before_values.append(tuple((key,value) for key,value in row.items() if key != "unit"))
        if row["metric"] == "stopped_episode_support":
            if row["unit"] != "sampled_vehicle_presence_s": raise AssertionError("unexpected source unit")
            row["unit"] = "sampled_region_stop_support_s"; corrected += 1
    with target_summary.open("x", encoding="utf-8", newline="") as handle:
        writer=csv.DictWriter(handle,fieldnames=fields); writer.writeheader(); writer.writerows(records)
    with target_summary.open(encoding="utf-8", newline="") as handle:
        after=list(csv.DictReader(handle))
    after_values=[tuple((key,value) for key,value in row.items() if key != "unit") for row in after]
    if corrected != 355 or before_values != after_values: raise AssertionError("unit-only correction invariant failed")
    if any(row["unit"] != "sampled_region_stop_support_s" for row in after if row["metric"]=="stopped_episode_support"):
        raise AssertionError("corrected unit absent")
    manifest={"schema_version":1,"status":"aggregate_archive_only_unit_label_corrected",
              "parent_revision":"aggregate/revision_02","parent_manifest_sha256":digest(SOURCE_DATA/"manifest.json"),
              "correction":{"metric":"stopped_episode_support","from":"sampled_vehicle_presence_s","to":"sampled_region_stop_support_s","row_count":corrected,"numeric_values_changed":0},
              "unchanged_file_hashes":{name:digest(TARGET_DATA/name) for name in unchanged_data} | {name:digest(TARGET_TABLES/name) for name in unchanged_tables},
              "condition_evidence_summary_sha256":digest(target_summary),"actual_sumo_starts":0}
    with (TARGET_DATA/"manifest.json").open("x",encoding="utf-8") as handle:
        json.dump(manifest,handle,indent=2); handle.write("\n")
    print(json.dumps(manifest["correction"],sort_keys=True)); return 0

if __name__ == "__main__": raise SystemExit(main())

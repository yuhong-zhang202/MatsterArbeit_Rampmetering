"""Finalize and independently check the reviewer-opinion-only Stage 3 review revision."""
from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path
import shutil


ROOT = Path(__file__).resolve().parents[2]
BATCH = ROOT / "data/processed/stage3_baseline_diagnostic_20260912_v2"
OLD = BATCH / "analysis_review/revision_05"
NEW = BATCH / "analysis_review/revision_06"
OLD_FIGURES = ROOT / "results/figures/stage3_baseline_diagnostic_20260912_v2/revision_05"
NEW_FIGURES = ROOT / "results/figures/stage3_baseline_diagnostic_20260912_v2/revision_06"

EXPECTED = {
    "Q1": ("supported", "supported_with_scope_limitation: synthetic scaffold only; no realistic upstream freeway feeder observation"),
    "Q2": ("not_identified", "not_identified"),
    "Q3": ("supported", "supported_with_scope_limitation: observational exposure only; causal R-induced U loss is not established"),
    "Q4": ("not_identified", "not_identified"),
}


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def main() -> int:
    unchanged = sorted(p.name for p in OLD.glob("*.csv") if p.name != "claim_evidence.csv")
    for name in unchanged:
        if sha256(OLD / name) != sha256(NEW / name):
            raise AssertionError(f"unexpected non-claim change: {name}")

    old_rows = {row["question_id"]: row for row in read_csv(OLD / "claim_evidence.csv")}
    new_rows = {row["question_id"]: row for row in read_csv(NEW / "claim_evidence.csv")}
    if set(old_rows) != set(EXPECTED) or set(new_rows) != set(EXPECTED):
        raise AssertionError("claim coverage is not Q1-Q4 exactly")
    for question_id, (status, opinion) in EXPECTED.items():
        old = old_rows[question_id]
        new = new_rows[question_id]
        changed = {key for key in old if old[key] != new[key]}
        if changed != {"reviewer_opinion"}:
            raise AssertionError(f"{question_id} changed fields: {sorted(changed)}")
        if new["status"] != status or new["reviewer_opinion"] != opinion:
            raise AssertionError(f"{question_id} reviewer result mismatch")
        if old["reviewer_opinion"] != "pending":
            raise AssertionError(f"{question_id} old reviewer result was not pending")

    for source in sorted(OLD_FIGURES.glob("*.png")):
        destination = NEW_FIGURES / source.name
        if not destination.exists():
            with source.open("rb") as src, destination.open("xb") as dst:
                shutil.copyfileobj(src, dst)
        if sha256(source) != sha256(destination):
            raise AssertionError(f"figure copy mismatch: {source.name}")

    outputs = sorted(list(NEW.glob("*.csv")) + list(NEW_FIGURES.glob("*.png")))
    payload = json.loads((OLD / "analysis_summary.json").read_text(encoding="utf-8"))
    payload["status"] = "data_analyst_complete_scientific_review_recorded"
    payload["Q1_Q4"] = "4/4 reviewer opinions recorded"
    payload["outputs"] = {str(path.relative_to(ROOT)): sha256(path) for path in outputs}
    summary = NEW / "analysis_summary.json"
    if summary.exists():
        if json.loads(summary.read_text(encoding="utf-8")) != payload:
            raise AssertionError("existing analysis summary differs from reconstructed summary")
    else:
        with summary.open("x", encoding="utf-8") as handle:
            json.dump(payload, handle, indent=2, ensure_ascii=False, allow_nan=False)
            handle.write("\n")

    result = {
        "status": "passed",
        "claim_rows": len(new_rows),
        "changed_fields": ["reviewer_opinion"],
        "pending_opinions": sum(row["reviewer_opinion"] == "pending" for row in new_rows.values()),
        "unchanged_csv_files": unchanged,
        "unchanged_figure_hashes": len(list(NEW_FIGURES.glob("*.png"))),
        "scientific_status_or_numeric_changes": 0,
        "actual_sumo_starts": 0,
    }
    verification = BATCH / "verification/reviewer_opinion_revision_06.json"
    with verification.open("x", encoding="utf-8") as handle:
        json.dump(result, handle, indent=2, ensure_ascii=False, allow_nan=False)
        handle.write("\n")
    print(json.dumps(result, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

"""Reproduce four pre-repair defects from preserved source; synthetic inputs only."""
from pathlib import Path
import csv
import hashlib
import importlib.util
import json
import shutil
import sys
import tempfile
from unittest.mock import patch

AUDIT = Path(__file__).resolve().parent
ROOT = AUDIT.parents[2]
sys.path.insert(0, str(ROOT / "src/analysis"))


def load(name, filename):
    spec = importlib.util.spec_from_file_location(name, AUDIT / filename)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    module.ROOT = ROOT
    return module


def main():
    target = AUDIT / sys.argv[1]
    if target.parent != AUDIT or target.exists():
        raise ValueError("Provide one new direct-child output directory name")
    target.mkdir()
    original = load("original_stage3", "original_analyze_stage3_baseline.py")
    # Restore the original project-root default after relocating the preserved module.
    original.ArchiveResolver.__init__.__defaults__ = (ROOT,)
    fixture = load("original_stage3_tests", "original_test_stage3_baseline.py")
    fixture.analyze_run = original.analyze_run
    source_sha = hashlib.sha256(Path(original.__file__).read_bytes()).hexdigest()
    original_mkdtemp, original_write = tempfile.mkdtemp, Path.write_text
    records = []
    for name in ("missing_fcd_speed", "unknown_fcd_lane", "tls_shifted_label", "positive_e1_missing_speed"):
        locations = []

        def scoped_temp(suffix=None, prefix=None, dir=None):
            result = original_mkdtemp(suffix=suffix, prefix=name + "_", dir=target)
            locations.append(Path(result))
            return result

        def mutate_write(path, text, *args, **kwargs):
            if name == "missing_fcd_speed" and path.name == "fcd.xml":
                text = text.replace('speed="1" pos="1"', 'pos="1"')
            if name == "unknown_fcd_lane" and path.name == "fcd.xml":
                text = text.replace('lane="main_down_0"', 'lane="unknown_lane_0"')
            if name == "tls_shifted_label" and path.name == "tls_states.xml":
                text = text.replace('time="2699"', 'time="2700"')
            if name == "positive_e1_missing_speed" and path.name == "int0.xml":
                text = text.replace('speed="10"', 'speed="-1"')
            if path.name == "ledger.json":
                value = json.loads(text)
                value["code_hashes"]["analyze_stage3_baseline.py"] = source_sha
                text = json.dumps(value)
            return original_write(path, text, *args, **kwargs)

        caught = None
        with patch.object(tempfile, "mkdtemp", scoped_temp), patch.object(
            shutil, "rmtree", lambda *args, **kwargs: None
        ), patch.object(Path, "write_text", mutate_write):
            case = fixture.Stage3FailureModes("test_17_analyze_run_writes_all_contract_tables_from_synthetic_archive")
            try:
                case.test_17_analyze_run_writes_all_contract_tables_from_synthetic_archive()
            except Exception as exc:
                caught = f"{type(exc).__name__}: {exc}"
        base = locations[0]
        manifest = json.loads((base / "generated/output/manifest.json").read_text())
        with (base / "generated/tables/coverage_audit.csv").open() as handle:
            coverage = {row["output_id"]: row["status"] for row in csv.DictReader(handle)}
        records.append({"probe": name, "fixture": str(base.relative_to(ROOT)),
                        "manifest_status": manifest["status"], "coverage": coverage,
                        "original_fixture_assertion_failure": caught})
    with (target / "original_probe_results.json").open("x") as handle:
        json.dump(records, handle, indent=2)
    print(json.dumps({"probe_count": len(records), "output": str(target), "simulation_starts": 0}))


if __name__ == "__main__":
    main()

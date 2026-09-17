"""Run the bounded audit tests, redirecting fixture writes into a new audit child."""
from pathlib import Path
import contextlib
import io
import json
import sys
import tempfile
import unittest

AUDIT = Path(__file__).resolve().parent
ROOT = AUDIT.parents[2]
sys.path.insert(0, str(ROOT))
target = AUDIT / sys.argv[1]
if target.parent != AUDIT or target.exists():
    raise ValueError("Provide one new direct-child output directory name")
target.mkdir()
original = tempfile.mkdtemp


def scoped_temp(suffix=None, prefix=None, dir=None):
    return original(suffix=suffix, prefix=prefix, dir=target)


tempfile.mkdtemp = scoped_temp
targets = ["tests.test_stage3_baseline", "tests.test_verify_stage3_baseline",
           "tests.test_stage4_qmain.Stage4FinalEvidenceSnapshotTests",
           "tests.test_verify_stage4_qmain.IndependentFinalEvidenceSnapshotChecks"]
stream = io.StringIO()
with contextlib.redirect_stdout(stream), contextlib.redirect_stderr(stream):
    result = unittest.TextTestRunner(stream=stream, verbosity=2).run(
        unittest.defaultTestLoader.loadTestsFromNames(targets))
with (target / "test_log.txt").open("x") as handle:
    handle.write(stream.getvalue())
record = {"tests_run": result.testsRun, "failures": len(result.failures),
          "errors": len(result.errors), "skipped": len(result.skipped), "targets": targets,
          "python": sys.version, "simulation_starts": 0}
with (target / "test_result.json").open("x") as handle:
    json.dump(record, handle, indent=2)
print(stream.getvalue())
raise SystemExit(0 if result.wasSuccessful() else 1)

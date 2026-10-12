"""Three selected destination fixtures, no native allocation or card preparation."""
from pathlib import Path
import importlib.util
import unittest
import sys
ROOT=Path(__file__).resolve().parents[3]
sys.path.insert(0,str(ROOT))
source=ROOT/'tests/candidate_a_native_receiver_wait_20261012/test_wait.py'
spec=importlib.util.spec_from_file_location('destination_wait_tests',source)
module=importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)
methods=(
    'test_frozen_denial_pattern_current_query_is_separate_and_bound',
    'test_current_gap_denied_is_not_wait',
    'test_before_denied_after_pass_entry_still_stops_with_both_observations',
)
suite=unittest.TestSuite(module.WaitTests(method) for method in methods)
result=unittest.TextTestRunner(verbosity=2).run(suite)
sys.exit(0 if result.wasSuccessful() else 1)

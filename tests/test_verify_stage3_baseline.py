"""Focused tests for the independent Stage 3 verifier primitives."""
from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src" / "analysis"))

from verify_stage3_baseline import close, contiguous  # noqa: E402
from build_stage3_t34_review import sign  # noqa: E402


class IndependentVerifierTests(unittest.TestCase):
    def test_contiguous_splits_gaps(self):
        self.assertEqual(contiguous([1.0, 2.0, 4.0], 1.0), [(1.0, 2.0, 2), (4.0, 4.0, 1)])

    def test_contiguous_rejects_duplicates(self):
        with self.assertRaises(ValueError):
            contiguous([1.0, 1.0], 1.0)

    def test_close_handles_nested_numeric_and_none(self):
        self.assertTrue(close((1, 2.0, None), (1.0, 2, None)))
        self.assertFalse(close((1, None), (1, 0)))

    def test_sign_keeps_zero_separate(self):
        self.assertEqual(sign(2.0), "positive")
        self.assertEqual(sign(-2.0), "negative")
        self.assertEqual(sign(0.0), "zero")


if __name__ == "__main__":
    unittest.main(verbosity=2)

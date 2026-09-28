import unittest
from r07_coverage_audit import audit


class CoverageAuditTests(unittest.TestCase):
    def test_coverage_closes_only_with_explicit_g6_limitation(self):
        result = audit()
        self.assertEqual(result["status"], "PASS_COVERAGE_AUDIT_WITH_G6_LIMITATION")
        self.assertEqual(result["planned_observability"]["direct_same_identity_time_location_R_to_U_obstruction"]["status"],
                         "NOT_ESTABLISHED_BY_REGISTERED_OUTPUTS")
        self.assertTrue(result["release_policy"]["unknown_g6_blocks_baseline_suitability"])
        self.assertFalse(result["added_observers_or_detectors"])


if __name__ == "__main__":
    unittest.main()

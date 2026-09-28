import unittest

from analyze_a_attribution import exposure, exposure_group, coarse_exposure_group, same_sample_delta


class AttributionMathTest(unittest.TestCase):
    def test_counterfactual_spacetime_gap_and_cohorts(self):
        m = {("M_flow.1", 600): (1500.0, 25.0, "merge_section_1"),
             ("M_flow.2", 600): (1600.0, 25.0, "merge_section_0"),
             ("M_flow.3", 600): (1400.0, 25.0, "merge_section_0")}
        r = {600: [("R_flow.1", 1460.0, "merge_section_1")]}
        e = exposure(m, r)
        self.assertEqual(len(e), 3)
        self.assertEqual(e["M_flow.1"]["signed_gap_m"], 40.0)
        self.assertEqual(e["M_flow.3"]["signed_gap_m"], -60.0)
        self.assertEqual(exposure_group("M_flow.2", e), "R_100_to_200m")
        self.assertEqual(coarse_exposure_group("M_flow.1", e), "R_within_50m")
        self.assertEqual(coarse_exposure_group("M_flow.2", e), "R_over_50m")
        self.assertEqual(coarse_exposure_group("M_flow.4", e), "no_simultaneous_R_in_merge")

    def test_same_time_lane_cell_speed_only(self):
        base = {("M_flow.1", 600): (1450.0, 20.0, "merge_section_1"),
                ("M_flow.2", 600): (1450.0, 20.0, "merge_section_1")}
        arm = {("M_flow.1", 600): (1451.0, 18.0, "merge_section_1"),
               ("M_flow.2", 600): (1451.0, 10.0, "merge_section_0")}
        result = same_sample_delta(base, arm, {"M_flow.1": "near", "M_flow.2": "far"}, 14)
        self.assertEqual(result["near"]["paired_samples"], 1)
        self.assertEqual(result["near"]["mean_A_minus_R0_speed_mps"], -2.0)
        self.assertNotIn("far", result)


if __name__ == "__main__":
    unittest.main()

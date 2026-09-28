"""Known-value tests for the fixed-window A outcome calculations."""
import unittest

from analyze_a_outcome import core_bins, compare_bins, paired_trip_metrics, summarize_trips


class OutcomeMath(unittest.TestCase):
    def test_core_cell_population_and_empty_speed(self):
        # Same physical cell, two M observations in one complete 30 s bin.
        m = {("M_flow.0", 540): ("merge_section_1", 1450.0, 50.0, 20.0, "1450", "0", "50", "20"),
             ("M_flow.1", 540): ("merge_section_2", 1455.0, 55.0, 10.0, "1455", "0", "55", "10")}
        r0 = core_bins(m, "R0")
        row = next(r for r in r0 if r["cell"] == 14 and r["begin"] == 540)
        self.assertEqual(row["M_samples"], 2)
        self.assertEqual(row["M_mean_speed_mps"], 15)
        self.assertAlmostEqual(row["M_mean_simultaneous_count"], 2/30)
        self.assertAlmostEqual(row["M_density_veh_per_km"], 2/(30*.2))
        empty = next(r for r in r0 if r["cell"] == 14 and r["begin"] == 570)
        self.assertIsNone(empty["M_mean_speed_mps"])
        a = core_bins({("M_flow.0",540):("merge_section_1",1450.0,50.0,10.0,"1450","0","50","10")},"A")
        contrast = next(r for r in compare_bins(r0,a) if r["cell"]==14 and r["begin"]==540)
        self.assertEqual(contrast["A_minus_R0_speed_mps"], -5)
        self.assertAlmostEqual(contrast["A_minus_R0_mean_count"], -1/30)

    def test_paired_full_cohort_trip_arithmetic(self):
        planned={"M_flow.0":{"class":"M","depart":"0"},"M_flow.1":{"class":"M","depart":"540"}}
        r0={"M_flow.0":{"depart":"0","arrival":"10","duration":"10","timeLoss":"2"},
            "M_flow.1":{"depart":"540","arrival":"560","duration":"20","timeLoss":"4"}}
        a={"M_flow.0":{"depart":"0","arrival":"10","duration":"10","timeLoss":"2"},
           "M_flow.1":{"depart":"540","arrival":"565","duration":"25","timeLoss":"7"}}
        rows=paired_trip_metrics(r0,a,planned)
        overall=summarize_trips(rows)[0]
        self.assertEqual(overall["n"],2)
        self.assertEqual(overall["A_minus_R0_duration_mean_s"],2.5)
        self.assertEqual(overall["A_minus_R0_timeLoss_mean_s"],1.5)


if __name__=="__main__":unittest.main()

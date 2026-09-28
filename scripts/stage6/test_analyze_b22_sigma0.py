import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parent))
import analyze_b22_sigma0 as a


class B22Sigma0AnalysisTests(unittest.TestCase):
    def test_fcd_parent_time_all_merge_lanes_and_class_queue(self):
        xml = ('<fcd-export>'
               '<timestep time="0"/><timestep time="1"/>'
               '<timestep time="2"><vehicle id="R_flow.0" lane="ramp_storage_0" x="1010" pos="10" speed="0"/>'
               '<vehicle id="R_flow.2" lane="urban_in_0" x="1000" pos="0" speed="0"/>'
               '<vehicle id="U_flow.0" lane="shared_approach_0" x="1020" pos="20" speed="1"/></timestep>'
               '<timestep time="3"><vehicle id="R_flow.0" lane="merge_section_0" x="1420" pos="20" speed="20"/>'
               '<vehicle id="R_flow.2" lane=":urban_tls_0_0" x="1005" pos="5" speed="1"/>'
               '<vehicle id="R_flow.1" lane="merge_section_2" x="1425" pos="25" speed="20"/></timestep>'
               '<timestep time="4"/></fcd-export>')
        with tempfile.TemporaryDirectory() as tmp:
            f = Path(tmp) / "fcd.xml"
            f.write_text(xml)
            with patch.object(a, "HORIZON", 5), patch.object(a, "ACTIVATION", 2), patch.object(a, "ACTIVE_END", 5):
                got = a.scan_fcd(f)
        self.assertEqual(got["first_r"], {"R_flow.0": 3, "R_flow.1": 3})
        self.assertEqual(got["pre"], {})
        by_lane = {(x["class"], x["lane"]): x for x in got["spatial"]}
        self.assertEqual(by_lane[("R", "ramp_storage_0")]["slow_vehicle_seconds"], 1)
        self.assertEqual(by_lane[("R", "urban_in_0")]["slow_vehicle_seconds"], 1)
        self.assertEqual(by_lane[("R", ":urban_tls_0_0")]["slow_vehicle_seconds"], 1)
        self.assertEqual(by_lane[("U", "shared_approach_0")]["slow_vehicle_seconds"], 1)

    def test_fcd_missing_second_fails(self):
        with tempfile.TemporaryDirectory() as tmp:
            f = Path(tmp) / "fcd.xml"
            f.write_text('<fcd-export><timestep time="0"/><timestep time="2"/></fcd-export>')
            with patch.object(a, "HORIZON", 3):
                with self.assertRaisesRegex(ValueError, "Missing/repeated"):
                    a.scan_fcd(f)

    def test_one_vehicle_missing_interior_second_fails_with_complete_global_steps(self):
        xml = ('<fcd-export><timestep time="0"/><timestep time="1"/>'
               '<timestep time="2"><vehicle id="R_flow.0" lane="ramp_storage_0" '
               'x="1010" pos="10" speed="0"/></timestep>'
               '<timestep time="3"/>'
               '<timestep time="4"><vehicle id="R_flow.0" lane="ramp_storage_0" '
               'x="1010" pos="10" speed="0"/></timestep></fcd-export>')
        with tempfile.TemporaryDirectory() as tmp:
            f = Path(tmp) / "fcd.xml"
            f.write_text(xml)
            with patch.object(a, "HORIZON", 5), patch.object(a, "ACTIVATION", 2):
                with self.assertRaisesRegex(ValueError, "Interior FCD gap"):
                    a.scan_fcd(f)

    def test_duplicate_active_r_vehicle_second_fails(self):
        xml = ('<fcd-export><timestep time="0"/><timestep time="1"/>'
               '<timestep time="2"><vehicle id="R_flow.0" lane="urban_in_0" x="100" speed="0"/>'
               '<vehicle id="R_flow.0" lane="urban_in_0" x="100" speed="0"/></timestep>'
               '<timestep time="3"/><timestep time="4"/></fcd-export>')
        with tempfile.TemporaryDirectory() as tmp:
            f = Path(tmp) / "fcd.xml"
            f.write_text(xml)
            with patch.object(a, "HORIZON", 5), patch.object(a, "ACTIVATION", 2):
                with self.assertRaisesRegex(ValueError, "Duplicate FCD vehicle-second"):
                    a.scan_fcd(f)

    def test_observed_ids_reconcile_with_inserted_and_boundary_exception(self):
        planned = {"vehicles": {"R_flow.0": {}, "R_flow.1": {}, "R_flow.2": {}}}
        with tempfile.TemporaryDirectory() as tmp:
            raw = Path(tmp)
            (raw / "vehroute.xml").write_text('<routes><vehicle id="R_flow.0" depart="0" arrival="3"/>'
                                                '<vehicle id="R_flow.1" depart="4" arrival="-1"/></routes>')
            (raw / "tripinfo.xml").write_text('<tripinfos><tripinfo id="R_flow.0" depart="0" duration="3" '
                                               'timeLoss="1" departDelay="0"/><tripinfo id="R_flow.1" '
                                               'depart="4" duration="1" timeLoss="0" departDelay="0"/></tripinfos>')
            fcd = {"observed": {"M": set(), "R": {"R_flow.0"}, "U": set(), "X": set()},
                   "bounds": {"R_flow.0": (0, 2, 3), "R_flow.1": (4, 4, 1)}}
            with patch.object(a, "HORIZON", 5):
                rows, _, _, _ = a.lifecycle(planned, raw, fcd)
                r = next(row for row in rows if row["class"] == "R")
                self.assertEqual(r["observed_in_FCD"], 1)
                self.assertEqual(r["FCD_missing_boundary_ids"], ["R_flow.1"])
                fcd["observed"]["R"] = {"R_flow.1"}
                with self.assertRaisesRegex(ValueError, "absent from FCD outside boundary"):
                    a.lifecycle(planned, raw, fcd)
                fcd["observed"]["R"] = {"R_flow.0", "R_flow.1", "R_flow.2"}
                with self.assertRaisesRegex(ValueError, "without actual insertion"):
                    a.lifecycle(planned, raw, fcd)

    def test_vehicle_endpoint_reconciliation_fails_for_early_disappearance(self):
        planned = {"vehicles": {"R_flow.0": {}}}
        with tempfile.TemporaryDirectory() as tmp:
            raw = Path(tmp)
            (raw / "vehroute.xml").write_text('<routes><vehicle id="R_flow.0" depart="1" arrival="5"/></routes>')
            (raw / "tripinfo.xml").write_text('<tripinfos><tripinfo id="R_flow.0" depart="1" '
                                                'duration="4" timeLoss="0" departDelay="0"/></tripinfos>')
            fcd = {"observed": {"M": set(), "R": {"R_flow.0"}, "U": set(), "X": set()},
                   "bounds": {"R_flow.0": (1, 2, 2)}}
            with self.assertRaisesRegex(ValueError, "end/arrival endpoint mismatch"):
                a.lifecycle(planned, raw, fcd)
            fcd["bounds"]["R_flow.0"] = (1, 4, 4)
            rows, _, _, _ = a.lifecycle(planned, raw, fcd)
            r = next(x for x in rows if x["class"] == "R")
            self.assertEqual(r["arrival_minus_FCD_last_max_s"], 1)

    def test_predeparture_boundary_at_540(self):
        planned = {"vehicles": {"M_flow.0": {}, "M_flow.1": {}, "U_flow.0": {}}}
        va = {"M_flow.0": {"depart": "539", "departLane": "0", "departPos": "100", "departSpeed": "30"},
              "M_flow.1": {"depart": "540", "departLane": "1", "departPos": "100", "departSpeed": "30"},
              "U_flow.0": {"depart": "-1", "departLane": "0", "departPos": "100", "departSpeed": "0"}}
        vb = {k: dict(v) for k, v in va.items()}
        vb["M_flow.1"]["departSpeed"] = "25"
        pre = {("M_flow.0", 539): ("main_up_0", "100", "0", "100", "30")}
        got = a.verify_pre_departures(planned, va, vb, pre, dict(pre))
        self.assertEqual(got["matching_realized_departures"], 1)
        vb["M_flow.0"]["departSpeed"] = "25"
        with self.assertRaisesRegex(ValueError, "realized departure mismatch"):
            a.verify_pre_departures(planned, va, vb, pre, dict(pre))

    def test_additional_comparison_only_ignores_ramp_program(self):
        a_xml = ('<additional><laneAreaDetector id="e" lane="ramp_storage_0" file="/a/e.xml"/>'
                 '<WAUT id="selector" startProg="A_OPEN"/></additional>')
        b_xml = ('<additional><laneAreaDetector id="e" lane="ramp_storage_0" file="/b/e.xml"/>'
                 '<WAUT id="selector" startProg="B_MODERATE"/></additional>')
        with tempfile.TemporaryDirectory() as tmp:
            af, bf = Path(tmp) / "a.xml", Path(tmp) / "b.xml"
            af.write_text(a_xml)
            bf.write_text(b_xml)
            self.assertEqual(a.normalized_add_without_ramp_program(af),
                             a.normalized_add_without_ramp_program(bf))
            a.ramp_program(af, "A_OPEN", 60, 0, 0)
            a.ramp_program(bf, "B_MODERATE", 22, 3, 35)
            bf.write_text(b_xml.replace('lane="ramp_storage_0"', 'lane="shared_approach_0"'))
            self.assertNotEqual(a.normalized_add_without_ramp_program(af),
                                a.normalized_add_without_ramp_program(bf))

    def test_compiled_b22_program_exact_phase(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            net = root / "network.net.xml"
            config = root / "scenario.sumocfg"
            net.write_text('<net><tlLogic id="ramp_mid" programID="B_MODERATE">'
                           '<phase duration="22" state="G"/><phase duration="3" state="y"/>'
                           '<phase duration="35" state="r"/></tlLogic></net>')
            config.write_text(f'<sumoConfiguration><input><net-file value="{net}"/>'
                              '</input></sumoConfiguration>')
            a.compiled_ramp_program(config, a.digest(net), "B_MODERATE", 22, 3, 35)
            net.write_text(net.read_text().replace('duration="22"', 'duration="23"'))
            with self.assertRaisesRegex(ValueError, "Wrong ramp phase"):
                a.compiled_ramp_program(config, a.digest(net), "B_MODERATE", 22, 3, 35)

    def test_early_nonlocal_difference_retained(self):
        ma = {("M_flow.0", 594): ("main_down_0", 1715.0, 15.0, 26.0),
              ("M_flow.1", 599): ("main_up_0", 800.0, 800.0, 25.0)}
        mb = {("M_flow.0", 594): ("main_down_0", 1715.0, 15.0, 27.0),
              ("M_flow.1", 599): ("main_up_0", 800.0, 800.0, 26.0)}
        got = a.early_divergence(ma, mb)
        self.assertEqual(got["first_common_M_difference"]["time_s"], 594)
        self.assertEqual(got["early_540_630"][599 - 540]["different_A_x_below_1000"], 1)

    def test_t613_ahead_of_r_and_missing_id_retained(self):
        ma = {("M_flow.0", 613): ("main_down_0", 1510, 10, 25),
              ("M_flow.1", 613): ("main_up_0", 800, 800, 20),
              ("M_flow.2", 613): ("main_up_0", 900, 900, 20)}
        mb = {("M_flow.0", 613): ("main_down_0", 1510, 10, 24),
              ("M_flow.1", 613): ("main_up_0", 800, 800, 21)}
        r = {613: [{"id": "R_flow.0", "lane": "merge_section_0", "x": 1420}]}
        row = a.early_divergence(ma, mb, r, r)["early_540_630"][613 - 540]
        self.assertEqual(row["different_A_ahead_of_R_front"], 1)
        self.assertEqual(row["different_A_x_below_1400"], 1)
        self.assertEqual(row["A_only_M"], 1)

    def test_all_m_source_departures_late_difference_is_retained(self):
        planned = {"vehicles": {"M_flow.0": {}, "M_flow.1": {}}}
        va = {"M_flow.0": {"depart": "539", "departLane": "0", "departPos": "0", "departSpeed": "30"},
              "M_flow.1": {"depart": "620", "departLane": "0", "departPos": "0", "departSpeed": "30"}}
        vb = {key: dict(value) for key, value in va.items()}
        vb["M_flow.1"]["departSpeed"] = "28"
        rows = a.all_m_source_departures(planned, va, vb, expected_count=2)
        self.assertFalse(rows[0]["departSpeed_different"])
        self.assertTrue(rows[1]["departSpeed_different"])

    def test_e2_ninety_intervals_and_boundary(self):
        def interval(begin, end):
            return (f'<interval begin="{begin}" end="{end}" maxJamLengthInVehicles="1" '
                    'maxJamLengthInMeters="5" meanOccupancy="10"/>')
        with tempfile.TemporaryDirectory() as tmp:
            f = Path(tmp) / "e2.xml"
            f.write_text('<detector>' + ''.join(interval(i * 30, (i + 1) * 30)
                                                  for i in range(90)) + '</detector>')
            self.assertEqual(len(a.detector_queue(f)), 90)
            f.write_text('<detector>' + ''.join(interval(i * 30, (i + 1) * 30)
                                                  for i in range(89)) + '</detector>')
            with self.assertRaisesRegex(ValueError, "expected 90 bins"):
                a.detector_queue(f)

    def test_incomplete_vehicle_never_becomes_zero_cost(self):
        planned = {"vehicles": {"M_flow.0": {}, "R_flow.0": {}}}
        left_trip = {"M_flow.0": {"duration": "75", "timeLoss": "10", "departDelay": "0"},
                     "R_flow.0": {"duration": "90", "timeLoss": "30", "departDelay": "0"}}
        right_trip = {"M_flow.0": {"duration": "70", "timeLoss": "8", "departDelay": "0"}}
        left_veh = {"M_flow.0": {"arrival": "75"}, "R_flow.0": {"arrival": "90"}}
        right_veh = {"M_flow.0": {"arrival": "70"}}
        got = a.paired_trip_delta(planned, left_trip, right_trip, left_veh, right_veh)
        self.assertEqual(got["M"]["mean_B22_minus_A_duration_s"], -5)
        self.assertFalse(got["R"]["complete_cohort"])
        self.assertIsNone(got["R"]["mean_B22_minus_A_duration_s"])


if __name__ == "__main__":
    unittest.main()

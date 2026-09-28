from __future__ import annotations

import csv
import hashlib
import json
import math
import tempfile
import unittest
import xml.etree.ElementTree as ET
from pathlib import Path
from collections import Counter

import ri3350_control_adapter as a


class R04AdapterTests(unittest.TestCase):
    def test_retry_adapter_is_bound_to_distinct_output_not_consumed_attempt(self):
        self.assertEqual(a.RUN_ID, "RI3350_CTRL_S17_technical_retry1")
        expected_retry_dir = a.PACKAGE / "outputs" / a.RUN_ID
        self.assertEqual(expected_retry_dir.name, a.RUN_ID)
        self.assertNotEqual(expected_retry_dir.name, "RI3350_CTRL_S17_attempt1")
        old_attempt = a.PACKAGE / "outputs" / "RI3350_CTRL_S17_attempt1"
        original_raw_dir = a.RAW_RUN_DIR
        with tempfile.TemporaryDirectory() as td:
            expected_retry = Path(td) / a.RUN_ID
            a.RAW_RUN_DIR = expected_retry
            with self.assertRaisesRegex(ValueError, "raw directory must be the bound run output"):
                a.audit_raw_manifest(old_attempt)
        a.RAW_RUN_DIR = original_raw_dir

    def test_locked_method_analyzer_bindings_and_original_fixtures(self):
        mod = a.load_locked_analyzer()
        self.assertEqual(mod.EXPECTED_METHOD, a.METHOD_SHA256)
        self.assertEqual(len(mod.run_fixtures()), 22)

    def test_control_input_encodes_scheduled_R_zero(self):
        flows, expected = a.parse_demand_schedule(a.DEMAND)
        self.assertNotIn("R", flows)
        self.assertEqual(expected["R"], [])
        self.assertEqual({c: len(expected[c]) for c in "MUX"}, {"M": 1396, "U": 150, "X": 75})

    def test_sumotime_integer_number_flow_schedule_and_boundaries(self):
        flows, _ = a.parse_demand_schedule(a.DEMAND)
        m = flows["M"]
        self.assertEqual((m["begin_ms"], m["end_ms"], m["number"]), (0, 1_500_000, 1396))
        self.assertEqual((m["end_ms"] - m["begin_ms"]) // m["number"], 1074)
        self.assertEqual(a.flow_scheduled_depart_ms(m, 0), 0)
        self.assertEqual(a.flow_scheduled_depart_ms(m, 16), 17_184)
        self.assertEqual(a.flow_scheduled_depart_ms(m, 1395), 1_498_230)
        self.assertNotEqual(a.flow_scheduled_depart_ms(m, 1395), m["end_ms"])
        with self.assertRaisesRegex(ValueError, "outside positive number schedule"):
            a.flow_scheduled_depart_ms(m, 1396)
        self.assertEqual(a.flow_scheduled_depart_ms(flows["U"], 149), 1_490_000)
        self.assertEqual(a.flow_scheduled_depart_ms(flows["X"], 74), 1_480_000)

    def test_nondivisible_number_flow_interval_truncates_offset_in_sumo_time(self):
        flow = {"number": 3, "begin_ms": 0, "end_ms": 10_000}
        self.assertEqual(a.flow_scheduled_depart_ms(flow, 0), 0)
        self.assertEqual(a.flow_scheduled_depart_ms(flow, 1), 3_333)
        self.assertEqual(a.flow_scheduled_depart_ms(flow, 2), 6_666)
        self.assertNotEqual(a.flow_scheduled_depart_ms(flow, 2), flow["end_ms"])

    def test_tripinfo_delay_uses_output_precision_quantization_not_arbitrary_tolerance(self):
        # SUMO 1.26.0: schedule 17.184, actual 18.000, exact delay .816,
        # time2string at precision 2 emits .82. The old float schedule (.808...)
        # cannot reconcile with the serialized delay within one half-unit.
        self.assertTrue(a.serialized_depart_delay_matches("18.00", 17_184, "0.82"))
        self.assertFalse(a.serialized_depart_delay_matches("18.00", 17_192, "0.82"))
        self.assertFalse(a.serialized_depart_delay_matches("18.00", 17_184, "0.83"))

    def test_missing_vs_empty_manifest_is_not_zero(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            a.RAW_RUN_DIR = root
            with self.assertRaisesRegex(ValueError, "manifest.*missing"):
                a.audit_raw_manifest(root)
            (root / "output_manifest.json").write_text(json.dumps({
                "schema_version": "1", "run_id": root.name,
                "artifact_roles": [], "support_files": [], "actual_file_count": 0
            }))
            with self.assertRaisesRegex(ValueError, "required-role coverage"):
                a.audit_raw_manifest(root)

    def test_manifest_paths_cannot_escape_run_directory(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            raw = root / "raw"
            a.RAW_RUN_DIR = raw
            outside = root / "outside.xml"
            outside.write_text("<fcd-export/>")
            self._write_full_raw_fixture(raw)
            manifest = self._current_manifest(raw, extra_support=[{
                "category": "log", "relative_path": "../outside.xml",
                "size_bytes": outside.stat().st_size,
                "sha256": hashlib.sha256(outside.read_bytes()).hexdigest()}])
            (raw / "output_manifest.json").write_text(json.dumps(manifest))
            with self.assertRaisesRegex(ValueError, "escapes bound raw run directory"):
                a.audit_raw_manifest(raw)

    def test_current_runner_manifest_missing_role_hash_and_duplicate_are_rejected(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            raw = root / "raw"
            self._write_full_raw_fixture(raw)
            a.RAW_RUN_DIR = raw
            path = raw / "output_manifest.json"
            baseline = json.loads(path.read_text())
            self.assertEqual(len(baseline["artifact_roles"]), 18)
            damaged = json.loads(json.dumps(baseline))
            damaged["artifact_roles"].pop()
            damaged["actual_file_count"] -= 1
            path.write_text(json.dumps(damaged))
            with self.assertRaisesRegex(ValueError, "required-role coverage"):
                a.audit_raw_manifest(raw)
            path.write_text(json.dumps(baseline))
            role_path = raw / baseline["artifact_roles"][0]["relative_path"]
            rec = next(r for r in baseline["artifact_roles"] if r["relative_path"] == role_path.name)
            rec["sha256"] = "0" * 64
            path.write_text(json.dumps(baseline))
            with self.assertRaisesRegex(ValueError, "raw manifest mismatch"):
                a.audit_raw_manifest(raw)
            baseline = json.loads((raw / "output_manifest.json").read_text())
            baseline["artifact_roles"][-1] = dict(baseline["artifact_roles"][0])
            path.write_text(json.dumps(baseline))
            with self.assertRaisesRegex(ValueError, "duplicate manifest role"):
                a.audit_raw_manifest(raw)
            # Rebuild from the original complete inventory for the independent
            # duplicate-path case rather than carrying forward the bad role.
            baseline = self._current_manifest(raw)
            baseline["support_files"][0]["relative_path"] = baseline["artifact_roles"][0]["relative_path"]
            path.write_text(json.dumps(baseline))
            with self.assertRaisesRegex(ValueError, "duplicate manifest path"):
                a.audit_raw_manifest(raw)

    def test_complete_verified_zero_is_distinct_from_missing_source(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            raw = self._write_full_raw_fixture(root / "raw")
            a.RAW_RUN_DIR = raw
            _, file_audit = a.audit_raw_manifest(raw)
            self.assertEqual(len([r for r in file_audit if r["status"] == "PASS_HASH_BOUND"]), 20)
            # Missing required roles fail closed; only a complete grid reaching
            # the locked analyzer can produce a validated zero-event receipt.
            manifest_path = raw / "output_manifest.json"
            manifest = json.loads(manifest_path.read_text())
            manifest["artifact_roles"] = [r for r in manifest["artifact_roles"]
                                          if r["role"] != "fcd.xml"]
            manifest["actual_file_count"] -= 1
            manifest_path.write_text(json.dumps(manifest))
            with self.assertRaisesRegex(ValueError, "required-role coverage"):
                a.audit_raw_manifest(raw)

    def test_demand_guard_checks_caller_path_hash(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            altered = root / "alternate.rou.xml"
            altered.write_bytes(a.DEMAND.read_bytes() + b"\n<!-- altered -->\n")
            with self.assertRaisesRegex(ValueError, "caller-supplied control demand hash mismatch"):
                a.validate_demand_binding(altered)

    def test_design_document_hash_is_enforced(self):
        self.assertEqual(a.validate_design_binding(), a.DESIGN_SHA256)
        with tempfile.TemporaryDirectory() as td:
            altered = Path(td) / "design.md"
            altered.write_text("drift")
            original = a.DESIGN
            try:
                a.DESIGN = altered
                with self.assertRaisesRegex(ValueError, "design document hash mismatch"):
                    a.validate_design_binding()
            finally:
                a.DESIGN = original

    def test_apply_rejects_alternate_demand_before_analysis(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            a.OUTPUT_ROOT = root
            raw_dir = root / "raw"
            self._write_full_raw_fixture(raw_dir)
            altered = root / "alternate.rou.xml"
            altered.write_bytes(a.DEMAND.read_bytes() + b"\n<!-- altered -->\n")
            out = root / "processed"
            with self.assertRaisesRegex(ValueError, "caller-supplied control demand hash mismatch"):
                a.apply(raw_dir, out, altered)
            receipt = json.loads((out / "application_receipt.json").read_text())
            self.assertNotEqual(receipt["status"], "OFFLINE_CONTROL_APPLICATION_COMPLETED")

    def test_output_destination_rejects_arbitrary_raw_and_traversal(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            raw = root / "raw"
            raw.mkdir()
            a.OUTPUT_ROOT = root / "processed"
            a.RAW_RUN_DIR = raw
            with self.assertRaisesRegex(ValueError, "designated processed"):
                a.validate_output_destination(root / "other", raw)
            with self.assertRaisesRegex(ValueError, "data/raw"):
                a.validate_output_destination(a.ROOT / "data/raw/forbidden", raw)
            with self.assertRaisesRegex(ValueError, "designated processed"):
                a.validate_output_destination(a.OUTPUT_ROOT / ".." / "data/raw/escape", raw)

    def test_output_roles_detector_id_binding(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            outputs = self._write_full_raw_fixture(root / "raw")
            det = outputs / "p1_main_up_1300_l0.xml"
            tree = ET.parse(det)
            tree.getroot().find("interval").set("id", "wrong_detector")
            tree.write(det, encoding="utf-8", xml_declaration=True)
            self._refresh_manifest(root / "raw")
            with self.assertRaisesRegex(ValueError, "detector ID mismatch"):
                a.audit_raw_manifest(root / "raw")

    def _lifecycle_fixture(self, *, conflicting_arrival=False):
        td = tempfile.TemporaryDirectory()
        root = Path(td.name)
        demand = root / "demand.rou.xml"
        demand.write_text("""<routes>
          <route id="M_route" edges="main_up merge_section main_down"/>
          <route id="U_route" edges="urban_in shared_approach urban_out"/>
          <route id="X_route" edges="cross_in cross_out"/>
          <flow id="M_flow" type="t" route="M_route" begin="0" end="1500" number="2"/>
          <flow id="U_flow" type="t" route="U_route" begin="0" end="1500" number="1"/>
          <flow id="X_flow" type="t" route="X_route" begin="0" end="1500" number="1"/>
        </routes>""")
        routes = ET.Element("routes")
        trips = ET.Element("tripinfos")
        for vid, route, edges, depart, arrival in (
            ("M_flow.0", "M_route", "main_up merge_section main_down", "-1", "-1"),
            ("M_flow.1", "M_route", "main_up merge_section main_down", "1500", "-1"),
            ("U_flow.0", "U_route", "urban_in shared_approach urban_out", "0", "10"),
            ("X_flow.0", "X_route", "cross_in cross_out", "0", "10"),
        ):
            v = ET.SubElement(routes, "vehicle", id=vid, type="t", depart=depart,
                              arrival=(("10" if vid == "M_flow.1" else arrival)
                                       if conflicting_arrival else arrival), speedFactor="1.0")
            ET.SubElement(v, "route", edges=edges)
            ET.SubElement(trips, "tripinfo", id=vid, depart=depart,
                          departDelay="750" if vid == "M_flow.1" else "0",
                          arrival=arrival)
        ET.ElementTree(routes).write(root / "vehroute.xml")
        ET.ElementTree(trips).write(root / "tripinfo.xml")
        fcd = ET.Element("fcd-export")
        for t in range(a.HORIZON):
            ET.SubElement(fcd, "timestep", time=str(t))
        ET.ElementTree(fcd).write(root / "fcd.xml")
        flows, expected = a.parse_demand_schedule(demand)
        raws = {name: root / name for name in ("vehroute.xml", "tripinfo.xml", "fcd.xml")}
        return td, demand, raws, flows, expected

    def test_R_zero_and_explicit_never_inserted_late_unfinished(self):
        td, demand, raw, flows, expected = self._lifecycle_fixture()
        self.addCleanup(td.cleanup)
        rows, summary, audit = a.build_lifecycle(raw, flows, expected, demand_path=demand)
        byid = {r["vehicle_id"]: r for r in rows}
        self.assertEqual(audit["r_scheduled"], 0)
        self.assertEqual(audit["r_observed"], 0)
        self.assertEqual(byid["M_flow.0"]["status"], "NEVER_INSERTED_OR_EXPLICIT_UNDEPARTED")
        self.assertTrue(byid["M_flow.1"]["inserted_after_source_end"])
        self.assertTrue(byid["M_flow.1"]["unfinished_at_horizon"])
        self.assertEqual(byid["M_flow.1"]["scheduled_depart_s"], 750.0)
        self.assertEqual([r["class"] for r in summary], list("MRUX"))
        self.assertEqual(summary[1]["r_zero_source_status"], "SCHEDULE_ABSENT_AND_RAW_ABSENT")

    def test_conflicting_trip_and_vehroute_arrival_fails_closed(self):
        td, demand, raw, flows, expected = self._lifecycle_fixture(conflicting_arrival=True)
        self.addCleanup(td.cleanup)
        with self.assertRaisesRegex(ValueError, "arrival conflict"):
            a.build_lifecycle(raw, flows, expected, demand_path=demand)

    def test_missing_vehroute_depart_fails_even_with_positive_tripinfo_depart(self):
        td, demand, raw, flows, expected = self._lifecycle_fixture()
        self.addCleanup(td.cleanup)
        route_tree = ET.parse(raw["vehroute.xml"])
        route_tree.getroot().find("vehicle[@id='U_flow.0']").attrib.pop("depart")
        route_tree.write(raw["vehroute.xml"])
        with self.assertRaisesRegex(ValueError, "missing required depart"):
            a.build_lifecycle(raw, flows, expected, demand_path=demand)

    def test_missing_tripinfo_depart_fails_closed(self):
        td, demand, raw, flows, expected = self._lifecycle_fixture()
        self.addCleanup(td.cleanup)
        trip_tree = ET.parse(raw["tripinfo.xml"])
        trip_tree.getroot().find("tripinfo[@id='U_flow.0']").attrib.pop("depart")
        trip_tree.write(raw["tripinfo.xml"])
        with self.assertRaisesRegex(ValueError, "tripinfo identity missing required depart"):
            a.build_lifecycle(raw, flows, expected, demand_path=demand)

    def test_never_inserted_depart_conflicting_with_fcd_fails_closed(self):
        td, demand, raw, flows, expected = self._lifecycle_fixture()
        self.addCleanup(td.cleanup)
        fcd_tree = ET.parse(raw["fcd.xml"])
        timestep = fcd_tree.getroot().find("timestep")
        ET.SubElement(timestep, "vehicle", id="M_flow.0", x="100", speed="10")
        fcd_tree.write(raw["fcd.xml"])
        with self.assertRaisesRegex(ValueError, "FCD identity contradicts never-inserted"):
            a.build_lifecycle(raw, flows, expected, demand_path=demand)

    def test_route_must_match_exact_ordered_source_route(self):
        td, demand, raw, flows, expected = self._lifecycle_fixture()
        self.addCleanup(td.cleanup)
        route_tree = ET.parse(raw["vehroute.xml"])
        route_tree.getroot().find("vehicle[@id='U_flow.0']/route").set(
            "edges", "urban_in extra shared_approach urban_out")
        route_tree.write(raw["vehroute.xml"])
        with self.assertRaisesRegex(ValueError, "ordered source route mismatch"):
            a.build_lifecycle(raw, flows, expected, demand_path=demand)

    def test_tripinfo_depart_and_negative_sentinels_are_exact(self):
        td, demand, raw, flows, expected = self._lifecycle_fixture()
        self.addCleanup(td.cleanup)
        trip_tree = ET.parse(raw["tripinfo.xml"])
        trip_tree.getroot().find("tripinfo[@id='U_flow.0']").set("depart", "9")
        trip_tree.write(raw["tripinfo.xml"])
        with self.assertRaisesRegex(ValueError, "depart conflict"):
            a.build_lifecycle(raw, flows, expected, demand_path=demand)
        trip_tree = ET.parse(raw["tripinfo.xml"])
        trip_tree.getroot().find("tripinfo[@id='U_flow.0']").set("depart", "0")
        trip_tree.getroot().find("tripinfo[@id='M_flow.0']").set("depart", "-2")
        trip_tree.write(raw["tripinfo.xml"])
        with self.assertRaisesRegex(ValueError, "departure sentinel"):
            a.build_lifecycle(raw, flows, expected, demand_path=demand)

    def test_arrival_at_horizon_is_not_conflated_with_unfinished_sentinel(self):
        td, demand, raw, flows, expected = self._lifecycle_fixture()
        self.addCleanup(td.cleanup)
        for role in ("vehroute.xml", "tripinfo.xml"):
            tree = ET.parse(raw[role])
            node = tree.getroot().find("vehicle[@id='X_flow.0']" if role == "vehroute.xml"
                                       else "tripinfo[@id='X_flow.0']")
            node.set("arrival", str(a.HORIZON))
            tree.write(raw[role])
        rows, _, _ = a.build_lifecycle(raw, flows, expected, demand_path=demand)
        boundary = next(r for r in rows if r["vehicle_id"] == "X_flow.0")
        self.assertEqual(boundary["status"], "ARRIVED_AT_HORIZON_BOUNDARY")
        self.assertTrue(boundary["arrived_at_horizon_boundary"])
        self.assertFalse(boundary["unfinished_at_horizon"])
        self.assertFalse(boundary["arrived_before_horizon"])
        for role in ("vehroute.xml", "tripinfo.xml"):
            tree = ET.parse(raw[role])
            node = tree.getroot().find("vehicle[@id='X_flow.0']" if role == "vehroute.xml"
                                       else "tripinfo[@id='X_flow.0']")
            node.set("arrival", str(a.HORIZON + 1))
            tree.write(raw[role])
        with self.assertRaisesRegex(ValueError, "exceeds simulation horizon"):
            a.build_lifecycle(raw, flows, expected, demand_path=demand)

    def _lane_bins(self):
        out = []
        for cell in range(22):
            for scope in a.SCOPES:
                for start in range(0, a.HORIZON, 30):
                    out.append({"cell": cell, "scope": scope, "bin_start_s": start,
                                "observed_labels": 30, "unique_M": 3,
                                "mean_ratio": .90, "M_density_veh_per_lane_km": 10.0,
                                "MR_density_veh_per_lane_km": 10.0})
        return out

    def test_fixed_screen_cardinality_lane_failure_and_missing_unknown(self):
        bins = self._lane_bins()
        rows, pre, control = a.screen_rows(bins, [])
        self.assertEqual((len(rows), pre["actual_rows"], control["actual_rows"]), (180, 30, 150))
        self.assertEqual(pre["status"], "PASS")
        self.assertEqual(control["status"], "PASS")
        # A single lane's observed ratio failure cannot be hidden by pooled data.
        for r in bins:
            if r["cell"] == 13 and r["scope"] == "lane1" and r["bin_start_s"] == 360:
                r["mean_ratio"] = .84
        _, pre, _ = a.screen_rows(bins, [])
        self.assertEqual(pre["status"], "FAIL")
        # Missing required metric is UNKNOWN, not a pass or a classified FAIL.
        bins = self._lane_bins()
        bins = [r for r in bins if not (r["cell"] == 13 and r["scope"] == "lane0" and r["bin_start_s"] == 360)]
        rows, pre, _ = a.screen_rows(bins, [])
        self.assertEqual(pre["status"], "UNKNOWN")

    def test_disturbance_mask_uses_adjacent_cell_half_open_overlap(self):
        ev = [{"profile": "L", "cell": 14, "first_low_bin": 15,
               "low_bin_end_exclusive": 17, "event_id": "e1",
               "low_speed_bins": 2, "is_merge_core": True}]
        masks = a._profile_event_intervals(ev, [])
        self.assertEqual({m["family"] for m in masks}, {"L", "C"})
        bins = self._lane_bins()
        rows = {(r["cell"], r["scope"], r["bin_start_s"]): r for r in bins}
        at_block_end = a._state_for_screen(rows, masks, (360, 450), 13, "lane0")
        after_onset = a._state_for_screen(rows, masks, (450, 540), 13, "lane0")
        self.assertEqual(at_block_end["status"], "PASS")
        self.assertEqual(after_onset["status"], "FAIL")

    def test_catalog_receipt_validates_zero_nonzero_and_missing(self):
        zero = a.build_catalog_receipt([], [], [], run_id=a.RUN_ID, source_sha256="f" * 64)
        status, _ = a.validate_catalog_receipt(
            zero, [], run_id=a.RUN_ID, source_sha256="f" * 64)
        self.assertEqual(status, "PASS")
        status, reasons = a.validate_catalog_receipt(
            None, [], run_id=a.RUN_ID, source_sha256="f" * 64)
        self.assertEqual(status, "UNKNOWN")
        self.assertIn("CATALOG_RECEIPT_MISSING", reasons)
        events = [
            {"profile": p, "cell": 13, "first_low_bin": 10, "low_bin_end_exclusive": 12,
             "event_id": f"{p}1", "low_speed_bins": 2, "is_merge_core": True}
            for p in ("P", "S", "L")
        ]
        spatial = [{"cell_left": 13, "cell_right": 14, "common_first_low_bin": 10,
                    "qualification_bins": 4, "event_ids": "A1"}]
        masks = a._profile_event_intervals(events, spatial)
        masks = sorted(masks, key=lambda r: (r["family"], r["cell"], r["start_s"],
                                             r["end_s"], r["source_event_id"]))
        receipt = a.build_catalog_receipt(events, spatial, masks, run_id=a.RUN_ID,
                                          source_sha256="a" * 64)
        self.assertEqual(set(receipt["families"]), {"P", "S", "L", "A", "C"})
        self.assertEqual(receipt["families"]["C"]["source_event_count"], 1)
        self.assertEqual(a.validate_catalog_receipt(receipt, masks, run_id=a.RUN_ID,
                                                     source_sha256="a" * 64)[0], "PASS")
        damaged = dict(receipt, method_sha256="0" * 64)
        self.assertEqual(a.validate_catalog_receipt(damaged, masks, run_id=a.RUN_ID,
                                                     source_sha256="a" * 64)[0], "UNKNOWN")
        _, pre, control = a.screen_rows(self._lane_bins(), [], catalog_status="UNKNOWN",
                                        catalog_reasons=["CATALOG_RECEIPT_MISSING"])
        self.assertEqual((pre["status"], control["status"]), ("UNKNOWN", "UNKNOWN"))

    def test_integrity_warnings_never_pass_silently(self):
        base = {"fcd_labels": a.HORIZON, "fcd_errors": [], "r_scheduled": 0, "r_observed": 0}
        clean = {"duplicate_time_id_warnings": 0, "M_unexpected_lane_samples": 0,
                 "M_aux_samples": 0, "out_of_domain_samples": 0, "warnings": ""}
        self.assertEqual(a.integrity_disposition(base, clean)[0], "PASS")
        for key in ("duplicate_time_id_warnings", "M_unexpected_lane_samples",
                    "M_aux_samples", "out_of_domain_samples"):
            flagged = dict(clean, **{key: 1})
            self.assertEqual(a.integrity_disposition(base, flagged)[0], "FAIL", key)
        self.assertEqual(a.integrity_disposition(
            dict(base, fcd_errors=["BAD_FCD_ATTRIBUTE:missing-speed"]), clean)[0], "UNKNOWN")
        self.assertEqual(a.integrity_disposition(
            dict(base, fcd_labels=a.HORIZON - 1), clean)[0], "FAIL")
        self.assertEqual(a.integrity_disposition(
            base, dict(clean, warnings="NONINTEGER_TIME:12.5"))[0], "UNKNOWN")

    def _write_full_raw_fixture(self, raw_dir: Path):
        a.RAW_RUN_DIR = raw_dir
        raw_dir.mkdir(parents=True)
        outputs = raw_dir
        demand = ET.parse(a.DEMAND).getroot()
        routes_by_id = {r.get("id"): (r.get("edges") or "") for r in demand.findall("route")}
        flow_by_class = {f.get("id").split("_", 1)[0]: f for f in demand.findall("flow")}
        route_root = ET.Element("routes")
        trip_root = ET.Element("tripinfos")
        for cls in "MUX":
            flow = flow_by_class[cls]
            n = int(flow.get("number"))
            begin_ms = a._seconds_to_sumo_time(flow.get("begin"), "fixture.begin")
            end_ms = a._seconds_to_sumo_time(flow.get("end"), "fixture.end")
            edges = routes_by_id[flow.get("route")]
            for i in range(n):
                vid = f"{flow.get('id')}.{i}"
                scheduled = a.flow_scheduled_depart_ms(
                    {"number": n, "begin_ms": begin_ms, "end_ms": end_ms}, i) / 1000
                actual = math.ceil(scheduled)
                delay = round(actual - scheduled, 2)
                arrival = actual + 60
                v = ET.SubElement(route_root, "vehicle", id=vid, type=flow.get("type"),
                                  depart=f"{actual:.2f}", departLane="0", departPos="0",
                                  departSpeed="20", speedFactor="1.0", arrival=f"{arrival:.2f}")
                ET.SubElement(v, "route", edges=edges)
                ET.SubElement(trip_root, "tripinfo", id=vid, depart=f"{actual:.2f}",
                              departDelay=f"{delay:.2f}", arrival=f"{arrival:.2f}")
        ET.ElementTree(route_root).write(outputs / "vehroute.xml", encoding="utf-8", xml_declaration=True)
        ET.ElementTree(trip_root).write(outputs / "tripinfo.xml", encoding="utf-8", xml_declaration=True)
        fcd = ET.Element("fcd-export")
        for t in range(a.HORIZON):
            ET.SubElement(fcd, "timestep", time=str(t))
        ET.ElementTree(fcd).write(outputs / "fcd.xml", encoding="utf-8", xml_declaration=True)
        summary = ET.Element("summary")
        queue = ET.Element("queue-export")
        tls = ET.Element("tlsStates")
        for t in range(a.HORIZON):
            ET.SubElement(summary, "step", time=f"{t:.2f}")
            ET.SubElement(queue, "data", timestep=f"{t:.2f}")
            for tls_id, program, state in (("ramp_mid", "A_OPEN", "G"),
                                           ("urban_tls", "technical_placeholder", "Gr")):
                ET.SubElement(tls, "tlsState", time=f"{t:.2f}", id=tls_id,
                              programID=program, phase="0", state=state)
        for name, element in (("sumo_summary.xml", summary), ("queues.xml", queue),
                              ("tls_states.xml", tls), ("lanechanges.xml", ET.Element("lanechanges"))):
            ET.ElementTree(element).write(outputs / name, encoding="utf-8", xml_declaration=True)
        for name in ("ramp_storage_e2.xml", "shared_boundary_e2.xml"):
            root = ET.Element("detector")
            for start in range(0, a.HORIZON, 30):
                ET.SubElement(root, "interval", begin=f"{start:.2f}", end=f"{start+30:.2f}",
                              id=name[:-4], sampledSeconds="0", nVehEntered="0", nVehLeft="0",
                              nVehSeen="0", meanSpeed="-1", meanTimeLoss="0", meanOccupancy="0",
                              maxOccupancy="0", meanMaxJamLengthInVehicles="0",
                              meanMaxJamLengthInMeters="0", maxJamLengthInVehicles="0",
                              maxJamLengthInMeters="0", jamLengthInVehiclesSum="0",
                              jamLengthInMetersSum="0", meanHaltingDuration="0",
                              maxHaltingDuration="0", haltingDurationSum="0",
                              meanIntervalHaltingDuration="0", maxIntervalHaltingDuration="0",
                              intervalHaltingDurationSum="0", startedHalts="0",
                              meanVehicleNumber="0", maxVehicleNumber="0")
            ET.ElementTree(root).write(outputs / name, encoding="utf-8", xml_declaration=True)
        (outputs / "sumo_error.log").write_text("")
        (outputs / "sumo.log").write_text("")
        e1_names = ["p1_main_up_1300_l0.xml", "p1_main_up_1300_l1.xml",
                    "p1_merge_section_20_l0.xml", "p1_merge_section_20_l1.xml",
                    "p1_merge_section_20_l2.xml", "p1_main_down_20_l0.xml",
                    "p1_main_down_20_l1.xml", "p1_main_down_200_l0.xml",
                    "p1_main_down_200_l1.xml"]
        for name in e1_names:
            root = ET.Element("detector")
            for start in range(0, a.HORIZON, 30):
                ET.SubElement(root, "interval", id=name[:-4], begin=str(start), end=str(start + 30),
                              nVehContrib="0", speed="-1", flow="0", occupancy="0", nVehEntered="0")
            ET.ElementTree(root).write(outputs / name, encoding="utf-8", xml_declaration=True)
        manifest = self._current_manifest(raw_dir)
        (raw_dir / "output_manifest.json").write_text(json.dumps(manifest, indent=2))
        return outputs

    @staticmethod
    def _current_manifest(raw_dir: Path, extra_support=None):
        contract, _ = a.validate_output_roles()
        files = {p.name: p for p in raw_dir.iterdir()
                 if p.is_file() and p.name not in {"output_manifest.json", "execution_receipt.json"}}
        roles = []
        for expected in contract["required_xml_roles"]:
            name = expected["role"]
            p = files[name]
            roles.append({"role": name, "kind": expected["kind"],
                          "detector_id": expected.get("detector_id"),
                          "lane": expected.get("lane"), "root": expected["root"],
                          "relative_path": name, "status": "PRESENT",
                          "size_bytes": p.stat().st_size,
                          "sha256": hashlib.sha256(p.read_bytes()).hexdigest()})
        support = []
        role_names = {rec["role"] for rec in roles}
        for name, p in sorted(files.items()):
            if name in role_names:
                continue
            support.append({"category": "log", "relative_path": name,
                            "size_bytes": p.stat().st_size,
                            "sha256": hashlib.sha256(p.read_bytes()).hexdigest()})
        if extra_support:
            support.extend(extra_support)
        return {"schema_version": "1", "run_id": raw_dir.name,
                "artifact_roles": roles, "support_files": support,
                "actual_file_count": len(roles) + len(support)}

    @staticmethod
    def _refresh_manifest(raw_dir: Path):
        manifest_path = raw_dir / "output_manifest.json"
        manifest = json.loads(manifest_path.read_text())
        for rec in manifest["artifact_roles"] + manifest["support_files"]:
            path = raw_dir / rec["relative_path"]
            rec["size_bytes"] = path.stat().st_size
            rec["sha256"] = hashlib.sha256(path.read_bytes()).hexdigest()
        manifest_path.write_text(json.dumps(manifest, indent=2))

    def test_synthetic_end_to_end_apply_outputs_and_hashes(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            a.OUTPUT_ROOT = root
            raw_dir = root / "outputs" / "synthetic_R0_raw"
            outputs = self._write_full_raw_fixture(raw_dir)
            output_dir = root / "processed_R0"
            receipt = a.apply(raw_dir, output_dir)
            self.assertEqual(receipt["status"], "OFFLINE_CONTROL_APPLICATION_COMPLETED")
            self.assertEqual(receipt["R0_summary"]["status"], "PASS_ZERO")
            self.assertEqual(receipt["raw_completeness"], "PASS")
            self.assertEqual(receipt["pre_gate"]["actual_rows"], 30)
            self.assertEqual(receipt["control_gate"]["actual_rows"], 150)
            self.assertEqual(receipt["disturbance_catalog_status"], "PASS")
            for name, digest in receipt["output_hashes"].items():
                path = output_dir / name
                self.assertTrue(path.is_file(), name)
                self.assertEqual(hashlib.sha256(path.read_bytes()).hexdigest(), digest, name)
            catalog = json.loads((output_dir / "disturbance_catalog_completeness.json").read_text())
            self.assertEqual(catalog["families"], {
                family: {"source_event_count": 0, "catalog_row_count": 0}
                for family in ("P", "S", "L", "A", "C")})
            locked_source = json.loads((output_dir / "locked_event_source_receipt.json").read_text())
            self.assertEqual(locked_source["status"], "COMPLETE_ZERO_EVENTS")
            self.assertTrue(locked_source["zero_event_is_complete"])
            review_receipt = json.loads((output_dir / "reviewed_attribution_receipt.json").read_text())
            self.assertEqual(review_receipt["status"], "COMPLETE_BOUND_ZERO_EVENT")
            self.assertEqual(review_receipt["row_count"], 0)
            self.assertTrue((output_dir / "reviewed_attribution_interface.csv").is_file())
            manifest = json.loads((output_dir / "input_manifest.json").read_text())
            self.assertEqual(manifest["method"]["sha256"], a.METHOD_SHA256)
            self.assertEqual(manifest["locked_analyzer"]["sha256"], a.LOCKED_ANALYZER_SHA256)
            processing = json.loads((output_dir / "processing_manifest.json").read_text())
            self.assertEqual(processing["application_receipt"]["sha256"],
                             hashlib.sha256((output_dir / "application_receipt.json").read_bytes()).hexdigest())
            for name, digest in processing["artifact_hashes"].items():
                self.assertEqual(hashlib.sha256((output_dir / name).read_bytes()).hexdigest(), digest)
            self.assertTrue((outputs / "fcd.xml").is_file())
            inputs = json.loads((output_dir / "input_manifest.json").read_text())
            bridge = inputs["locked_analyzer_manifest_bridge"]
            self.assertEqual(bridge["source_manifest_sha256"], a.sha256(outputs / "output_manifest.json"))
            self.assertEqual(bridge["projection_manifest_sha256"],
                             receipt["compatibility_manifest_sha256"])
            self.assertEqual(bridge["projection_file_count"], 20)
            self.assertTrue(bridge["projection_paths_are_hash_verified_children_of_raw_run"])
            self.assertFalse(bridge["raw_files_copied_or_modified"])
            with (output_dir / "raw_hash_manifest.csv").open(newline="") as stream:
                raw_manifest_rows = list(csv.DictReader(stream))
            source_manifest_row = next(r for r in raw_manifest_rows
                                       if r["role_inferred_from_manifest_path"] == "output_manifest.json")
            self.assertEqual(source_manifest_row["resolved_path"], str(outputs / "output_manifest.json"))
            self.assertEqual(source_manifest_row["compatibility_manifest_sha256"],
                             bridge["projection_manifest_sha256"])
            for row in raw_manifest_rows:
                if row["role_inferred_from_manifest_path"] != "output_manifest.json":
                    self.assertTrue(Path(row["resolved_path"]).resolve().is_relative_to(outputs.resolve()), row)

    def test_incomplete_fcd_grid_persists_unknown_completeness(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            a.OUTPUT_ROOT = root
            raw_dir = root / "outputs" / "synthetic_R0_raw"
            outputs = self._write_full_raw_fixture(raw_dir)
            fcd = ET.parse(outputs / "fcd.xml")
            fcd.getroot().remove(fcd.getroot().findall("timestep")[-1])
            fcd.write(outputs / "fcd.xml", encoding="utf-8", xml_declaration=True)
            self._refresh_manifest(raw_dir)
            out = root / "processed_R0"
            with self.assertRaisesRegex(ValueError, "FCD time labels"):
                a.apply(raw_dir, out)
            result = json.loads((out / "raw_completeness.json").read_text())
            self.assertEqual(result["status"], "UNKNOWN")
            self.assertNotEqual(result["status"], "PASS")

    def test_analyzer_unknown_M_lane_warning_cannot_report_completeness_pass(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            a.OUTPUT_ROOT = root
            raw_dir = root / "outputs" / "synthetic_R0_raw"
            outputs = self._write_full_raw_fixture(raw_dir)
            fcd = ET.parse(outputs / "fcd.xml")
            ts = fcd.getroot().find("timestep")
            ET.SubElement(ts, "vehicle", id="M_flow.0", lane="not_a_compiled_lane",
                          x="100", speed="20", pos="100", angle="90", type="technical_passenger")
            fcd.write(outputs / "fcd.xml", encoding="utf-8", xml_declaration=True)
            self._refresh_manifest(raw_dir)
            receipt = a.apply(raw_dir, root / "processed_R0")
            completeness = json.loads((root / "processed_R0/raw_completeness.json").read_text())
            self.assertEqual(completeness["status"], "FAIL")
            self.assertIn("UNKNOWN_M_LANE", " ".join(completeness["integrity_reasons"]))
            self.assertEqual(receipt["raw_completeness"], "FAIL")


if __name__ == "__main__":
    unittest.main()

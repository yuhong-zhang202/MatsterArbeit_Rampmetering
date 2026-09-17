"""Synthetic-only failure-mode tests for the Stage 3 archive analyzer."""
from __future__ import annotations

import json
import argparse
import csv
import hashlib
from pathlib import Path
import shutil
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src" / "analysis"))

from analyze_stage3_baseline import (  # noqa: E402
    aggregate,
    analyze_run,
    build_condition_summary,
    build_episodes,
    endpoint_accounting,
    event_bin,
    full_episodes,
    build_propagation,
    reaggregate_e1,
    propagation_region_order,
    reject_temporary_output,
    reserve_directories,
    scan_fcd,
    slice_full_episodes,
    tls_state_at,
    validate_seed_consistency,
    validate_windows,
)


def contract(expected_end: float = 3.0) -> dict:
    return {
        "windows": {name: {"begin_s": bounds[0], "end_s": bounds[1]} for name, bounds in {
            "Full": (0, 2700), "A": (0, 1500), "B": (300, 1500), "Post": (1500, 2700)}.items()},
        "fcd": {"sampling_period_s": 1, "expected_begin_s": 0, "expected_end_s": expected_end},
        "stop_definition": {"speed_threshold_mps": 0.1},
        "lanes": {
            "shared_approach_0": {"region": "shared_approach", "is_internal": False, "r_path_start_m": 0, "r_path_end_m": 10, "tls_link": 0, "first_downstream_eligible": False},
            ":urban_diverge_1_0": {"region": "ramp_diverge_internal", "is_internal": True, "r_path_start_m": 10, "r_path_end_m": 20, "tls_link": None, "first_downstream_eligible": False},
            "ramp_storage_0": {"region": "ramp_storage", "is_internal": False, "r_path_start_m": 20, "r_path_end_m": 30, "tls_link": None, "first_downstream_eligible": False},
            ":ramp_mid_0_0": {"region": "ramp_mid_internal", "is_internal": True, "r_path_start_m": 30, "r_path_end_m": 40, "tls_link": None, "first_downstream_eligible": False},
            "ramp_accel_0": {"region": "ramp_accel", "is_internal": False, "r_path_start_m": 40, "r_path_end_m": 50, "tls_link": None, "first_downstream_eligible": False},
            ":freeway_merge_0_0": {"region": "ramp_merge_internal", "is_internal": True, "r_path_start_m": 50, "r_path_end_m": 60, "tls_link": None, "first_downstream_eligible": False},
            "main_down_0": {"region": "mainline_downstream", "is_internal": False, "r_path_start_m": 60, "r_path_end_m": 70, "tls_link": None, "first_downstream_eligible": True},
            "main_down_1": {"region": "mainline_downstream", "is_internal": False, "r_path_start_m": None, "tls_link": None, "first_downstream_eligible": True},
        },
    }


class Stage3FailureModes(unittest.TestCase):
    fixtures = 0
    assertions = 0
    categories: set[str] = set()

    @classmethod
    def tearDownClass(cls):
        print(json.dumps({"synthetic_fixture_count": cls.fixtures, "assertion_count": cls.assertions,
                          "failure_mode_categories": len(cls.categories)}, sort_keys=True))

    def fixture(self, category: str) -> None:
        type(self).fixtures += 1
        type(self).categories.add(category)

    def equal(self, first, second, message=None):
        type(self).assertions += 1
        self.assertEqual(first, second, message)

    def true(self, value, message=None):
        type(self).assertions += 1
        self.assertTrue(value, message)

    def almost(self, first, second, places=7):
        type(self).assertions += 1
        self.assertAlmostEqual(first, second, places=places)

    def raises(self, exc, func, *args, **kwargs):
        type(self).assertions += 1
        with self.assertRaises(exc):
            func(*args, **kwargs)

    def fcd(self, body: str, expected_end: float = 3.0) -> dict:
        self.fixture("fcd_xml")
        work = Path(tempfile.mkdtemp(dir=ROOT))
        try:
            path = work / "fixture.xml"
            path.write_text(f"<fcd-export>{body}</fcd-export>", encoding="utf-8")
            return scan_fcd(path, contract(expected_end))
        finally:
            shutil.rmtree(work)

    def test_01_duplicate_id(self):
        self.fixture("duplicate_id")
        body = '<timestep time="0"><vehicle id="R_flow.0" lane="ramp_storage_0" speed="1" pos="1"/><vehicle id="R_flow.0" lane="ramp_storage_0" speed="1" pos="2"/></timestep>'
        self.raises(ValueError, self.fcd, body, 1)

    def test_02_missing_frame_and_empty_frame(self):
        self.fixture("missing_frame")
        result = self.fcd('<timestep time="0"></timestep><timestep time="2"></timestep>', 3)
        self.equal(result["missing_frames"], [1.0])
        self.equal(result["frame_count"], 2)
        self.equal(result["frame_registry"][0]["frame_present"], True)
        self.equal(result["timeline"], [])

    def test_03_episode_split_1_2_4(self):
        self.fixture("episode_split")
        episodes = build_episodes([1, 2, 4], 1)
        self.equal(len(episodes), 2)
        self.equal((episodes[0]["first_label"], episodes[0]["last_label"], episodes[0]["sample_count"]), (1, 2, 2))
        self.equal((episodes[1]["first_label"], episodes[1]["last_label"], episodes[1]["sample_count"]), (4, 4, 1))
        self.equal(episodes[0]["support_seconds"], 2)

    def test_04_region_replacement_is_not_same_vehicle_episode(self):
        self.fixture("vehicle_replacement")
        body = ('<timestep time="0"><vehicle id="R_flow.0" lane="ramp_storage_0" speed="0.1" pos="1"/></timestep>'
                '<timestep time="1"><vehicle id="R_flow.1" lane="ramp_storage_0" speed="0" pos="2"/></timestep>')
        result = self.fcd(body, 2)
        region = [e for e in result["episodes"] if e["kind"] == "region_stop" and e["observation_domain"] == "Full"]
        vehicles = [e for e in result["episodes"] if e["kind"] == "vehicle_stop" and e["observation_domain"] == "Full"]
        self.equal(len(region), 1)
        self.equal(region[0]["sample_count"], 2)
        self.equal(len(vehicles), 2)
        self.equal({e["vehicle_id_or_null"] for e in vehicles}, {"R_flow.0", "R_flow.1"})

    def test_05_internal_lane_complete_without_double_count(self):
        self.fixture("internal_lane_accounting")
        body = ('<timestep time="0"><vehicle id="R_flow.0" lane=":freeway_merge_0_0" speed="1" pos="1"/>'
                '<vehicle id="M_flow.0" lane="main_down_1" speed="2" pos="3"/></timestep>')
        result = self.fcd(body, 1)
        rows = result["timeline"]
        self.equal(len(rows), 2)
        self.equal(sum(row["present_count"] for row in rows), 2)
        self.equal({row["lane_id"] for row in rows}, {":freeway_merge_0_0", "main_down_1"})
        self.equal(result["unknown_lane_count"], 0)

    def test_06_stop_boundary_and_missing_speed(self):
        self.fixture("stop_speed_semantics")
        body = ('<timestep time="0"><vehicle id="R_flow.0" lane="ramp_storage_0" speed="0.1" pos="1"/>'
                '<vehicle id="R_flow.1" lane="ramp_storage_0" speed="0.1001" pos="2"/>'
                '<vehicle id="R_flow.2" lane="ramp_storage_0" pos="3"/></timestep>')
        row = self.fcd(body, 1)["timeline"][0]
        self.equal(row["present_count"], 3)
        self.equal(row["stopped_count"], 1)
        self.equal(row["speed_n"], 2)
        self.equal(row["missing_speed_count"], 1)

    def test_07_first_r_downstream_is_unique(self):
        self.fixture("first_downstream_unique")
        body = ('<timestep time="0"><vehicle id="R_flow.0" lane="ramp_storage_0" speed="1" pos="1"/></timestep>'
                '<timestep time="1"><vehicle id="R_flow.0" lane="main_down_0" speed="1" pos="1"/></timestep>'
                '<timestep time="2"><vehicle id="R_flow.0" lane="main_down_1" speed="1" pos="2"/></timestep>')
        events = self.fcd(body, 3)["first_downstream"]
        self.equal(len(events), 1)
        self.equal(events[0]["first_downstream_time_s"], 1)
        self.equal(events[0]["previous_time_s"], 0)
        self.equal(events[0]["status"], "bracketed")

    def test_08_cross_bin_event_is_unknown(self):
        self.fixture("cross_bin_unknown")
        event = {"previous_time_s": 29, "first_downstream_time_s": 30}
        self.equal(event_bin(event, 0, 30), "unknown")
        self.equal(event_bin(event, 30, 60), "unknown")
        self.equal(event_bin({"previous_time_s": 10, "first_downstream_time_s": 11}, 0, 30), "inside")
        self.equal(event_bin({"previous_time_s": None, "first_downstream_time_s": 11}, 0, 30), "unknown")

    def test_09_endpoint_without_coverage_does_not_emit_zero(self):
        self.fixture("endpoint_coverage")
        unknown = endpoint_accounting(10, 10, 10, False)
        known = endpoint_accounting(10, 8, 7, True)
        self.equal(unknown["outside_confirmed"], None)
        self.equal(unknown["in_network"], None)
        self.equal(known["outside_confirmed"], 2)
        self.equal(known["in_network"], 1)

    def test_10_e1_zero_weighting_anchors_and_short_tail(self):
        self.fixture("e1_aggregation")
        rows = [
            {"detector_id": "l0", "begin_s": 0, "end_s": 30, "n_contrib": 0, "speed_mps": None},
            {"detector_id": "l1", "begin_s": 0, "end_s": 30, "n_contrib": 1, "speed_mps": 10},
            {"detector_id": "l0", "begin_s": 30, "end_s": 45, "n_contrib": 1, "speed_mps": 20},
            {"detector_id": "l1", "begin_s": 30, "end_s": 45, "n_contrib": 2, "speed_mps": 30},
        ]
        bins, total = reaggregate_e1(rows, 0, 45, 30, {"l0", "l1"})
        self.equal(len(bins), 2)
        self.equal(bins[0]["speed_mps"], 10)
        self.equal(bins[1]["qualification"], "short_tail_complete")
        self.almost(total["speed_mps"], 22.5)
        self.equal(total["n_contrib"], 4)
        anchor_rows = []
        for begin in range(300, 420, 30):
            anchor_rows.append({"detector_id": "l0", "begin_s": begin, "end_s": begin + 30, "n_contrib": 1, "speed_mps": 1})
        anchored, _ = reaggregate_e1(anchor_rows, 300, 420, 60, {"l0"})
        self.equal(anchored[0]["bin_begin_s"], 300)
        self.equal(anchored[1]["bin_begin_s"], 360)
        missing_rows = [row for row in rows if not (row["detector_id"] == "l1" and row["begin_s"] == 30)]
        missing_bins, missing_total = reaggregate_e1(missing_rows, 0, 45, 30, {"l0", "l1"})
        self.equal(missing_bins[1]["qualification"], "missing_detector_or_interval")
        self.equal(missing_bins[1]["missing_detectors"], "l1")
        self.equal(missing_total["qualification"], "incomplete")
        self.equal(missing_total["q_vehph"], None)
        self.raises(ValueError, reaggregate_e1, rows + [dict(rows[0])], 0, 45, 30, {"l0", "l1"})

    def test_11_tls_wrong_link(self):
        self.fixture("tls_link")
        self.equal(tls_state_at({0.0: "Gr"}, 0.0, 0), "G")
        self.equal(tls_state_at({0.0: "Gr"}, 0.0, 1), "r")
        self.raises(ValueError, tls_state_at, {0.0: "G"}, 0.0, 1)
        self.equal(tls_state_at({}, 0.0, 0), "unknown")

    def test_12_missing_seed_prohibits_consistency_claim(self):
        self.fixture("seed_coverage")
        self.raises(ValueError, validate_seed_consistency, [{"seed": 17}, {"seed": 17}])
        self.equal(validate_seed_consistency([{"seed": 17}, {"seed": 23}]), "two_seed_descriptive_direction_only")

    def test_13_guardrails_and_contract(self):
        self.fixture("guardrails")
        self.raises(ValueError, reject_temporary_output, Path("/private/tmp/stage3"))
        work = Path(tempfile.mkdtemp(dir=ROOT))
        try:
            existing = work / "existing"
            existing.mkdir()
            self.raises(FileExistsError, reserve_directories, [existing])
            output = work / "new"
            reserve_directories([output])
            self.true(output.is_dir())
        finally:
            shutil.rmtree(work)
        bad = contract()
        bad["windows"]["B"] = {"begin_s": 301, "end_s": 1500}
        self.raises(ValueError, validate_windows, bad)

    def test_14_full_episode_slices_parent_and_censor(self):
        self.fixture("episode_windows")
        base = full_episodes([0, 1, 2, 3, 4], 1, 0, 5, {0, 1, 2, 3, 4})[0]
        base.update({"episode_id": "full:1", "parent_episode_id": None, "class": "R", "region": "ramp_storage",
                     "kind": "region_stop", "vehicle_id_or_null": None, "observation_domain": "Full",
                     "stop_definition_id": "stop", "sampling_period_s": 1})
        rows = slice_full_episodes([base], {"A": (0, 2), "B": (1, 4), "Post": (4, 5), "Full": (0, 5)})
        self.equal(len(rows), 4)
        clips = {row["observation_domain"]: row for row in rows if row["observation_domain"] != "Full"}
        self.equal({row["parent_episode_id"] for row in clips.values()}, {"full:1"})
        self.true(clips["A"]["censor_right"])
        self.true(clips["B"]["censor_left"] and clips["B"]["censor_right"])
        self.true(clips["Post"]["censor_left"])
        missing = full_episodes([1, 3], 1, 0, 5, {0, 1, 3, 4})
        self.equal(len(missing), 2)
        self.true(missing[0]["censor_right"])
        self.true(missing[1]["censor_left"])
        self.equal(missing[0]["gap_reason"], "source_frame_missing")

    def test_15_propagation_endpoint_and_five_question_rows(self):
        self.fixture("propagation_and_questions")
        def episode(ident, cls, region, first):
            return {"episode_id": ident, "parent_episode_id": None, "class": cls, "region": region,
                    "kind": "region_stop", "vehicle_id_or_null": None, "observation_domain": "Full",
                    "stop_definition_id": "stop", "sampling_period_s": 1, "first_label": first,
                    "last_label": first + 1, "sample_count": 2, "support_seconds": 2,
                    "censor_left": False, "censor_right": False, "gap_reason": "stop_condition_false_or_entity_absent"}
        episodes = [episode("e1", "R", "ramp_accel", 1), episode("e2", "R", "ramp_mid_internal", 2),
                    episode("e3", "R", "ramp_storage", 3), episode("e4", "R", "ramp_diverge_internal", 4),
                    episode("e5", "R", "shared_approach", 5), episode("e6", "U", "shared_approach", 5)]
        propagation, event_set = build_propagation("C17", episodes, [], contract())
        self.equal(len(propagation), 1)
        self.equal(propagation[0]["status"], "complete_ordered_observation")
        self.equal(propagation[0]["cooccurrence_support_s"], 2)
        self.equal(event_set["shared_R_U_cooccurrence_labels_s"], [5, 6])
        event_groups = [set(event_set[key]) for key in ("ramp_end_event_ids", "storage_event_ids", "internal_event_ids", "shared_R_event_ids")]
        self.true(not any(first & second for index, first in enumerate(event_groups) for second in event_groups[index + 1:]))
        self.equal([row["region"] for row in event_set["contract_derived_region_order"]],
                   ["ramp_accel", "ramp_mid_internal", "ramp_storage", "ramp_diverge_internal", "shared_approach"])
        trips = {f"{cls}_flow.0": {"class": cls, "depart": 0, "arrival": 10} for cls in ("M", "R", "U", "X")}
        endpoints = [{"run_id": "C17", "class": cls, "endpoint_s": 2700.0, "planned": 1, "entered": 1,
                      "arrived": 1, "outside_confirmed": 0, "in_network": 0, "coverage": True,
                      "qualification": "verified"} for cls in ("M", "R", "U", "X")]
        metrics = [{"window": "Full", "entity": "M-only_internal_merge_entry", "metric": "q", "value": 1,
                    "unit": "veh/h", "denominator": 1, "qualification": "complete", "source_event_id": None,
                    "reason": "fixture"}]
        summary, sets = build_condition_summary("C17", "C", 17, trips, endpoints, episodes,
                                               [{"previous_time_s": 1, "first_downstream_time_s": 2}],
                                               metrics, propagation[0], True)
        questions = [row for row in summary if row["metric"] == "diagnostic_evidence_status"]
        self.equal(len(questions), 5)
        self.equal(len({row["entity"] for row in questions}), 5)
        self.true(any(row["entity"] == "question:spillback" and row["qualification"] == "observed" for row in questions))
        self.true(bool(sets))

    def test_15b_reversed_propagation_is_traceable_contradiction(self):
        self.fixture("propagation_reversed")
        def episode(ident, region, first):
            return {"episode_id": ident, "parent_episode_id": None, "class": "R", "region": region,
                    "kind": "region_stop", "vehicle_id_or_null": None, "observation_domain": "Full",
                    "stop_definition_id": "stop", "sampling_period_s": 1, "first_label": first,
                    "last_label": first, "sample_count": 1, "support_seconds": 1,
                    "censor_left": False, "censor_right": False, "gap_reason": "stop_condition_false_or_entity_absent"}
        reversed_rows = [episode("a", "ramp_accel", 5), episode("b", "ramp_mid_internal", 4),
                         episode("c", "ramp_storage", 3), episode("d", "ramp_diverge_internal", 2),
                         episode("e", "shared_approach", 1)]
        rows, event_set = build_propagation("REV", reversed_rows, [], contract())
        self.equal(rows[0]["status"], "contradicted_order")
        self.true(bool(rows[0]["contradiction_ids"]))
        self.equal(len(event_set["contradiction_details"]), 4)
        self.true(all("upstream region is first observed stopped" in item["reason"] for item in event_set["contradiction_details"]))
        bad_contract = contract()
        bad_contract["lanes"]["ramp_storage_0"]["r_path_start_m"] = 31
        self.raises(ValueError, propagation_region_order, bad_contract)

    def test_16_aggregate_combines_eight_nonempty_run_packages_and_checks_hashes(self):
        self.fixture("aggregate_eight_runs")
        work = Path(tempfile.mkdtemp(dir=ROOT))
        try:
            contract_path = work / "contract.json"
            contract_path.write_text(json.dumps(contract()), encoding="utf-8")
            contract_sha = hashlib.sha256(contract_path.read_bytes()).hexdigest()
            run_ids = ["C17", "C23", "ML17", "ML23", "MH17", "MH23", "RL17", "RL23"]
            sources = [{"run_id": run_id, "source_map_path": f"maps/{run_id}.json", "source_map_sha256": f"sha-{run_id}"}
                       for run_id in run_ids]
            ledger = {"stage": "Stage 3", "authorization": {"status": "user_approved"}, "actual_sumo_starts": 0,
                      "budget": {"max_sumo_starts": 0}, "input_hashes": {"measurement_contract_sha256": contract_sha},
                      "code_hashes": {"analyze_stage3_baseline.py": hashlib.sha256(
                          (ROOT / "src/analysis/analyze_stage3_baseline.py").read_bytes()).hexdigest()},
                      "source_runs": sources}
            ledger_path = work / "ledger.json"
            ledger_path.write_text(json.dumps(ledger), encoding="utf-8")
            manifests = []
            table_fields = {
                "coverage_audit.csv": ["run_id", "output_id", "path", "sha256", "schema_version", "time_count", "duplicate_count", "unknown_id_count", "unknown_lane_count", "missing_intervals", "status", "reason"],
                "lane_class_timeline.csv": ["run_id", "seed", "time_s", "lane_id", "region", "is_internal", "class", "present_count", "stopped_count", "speed_sum_mps", "speed_n", "min_path_position_m", "max_path_position_m", "position_mapping_status", "tls_link", "tls_state", "coverage", "missing_speed_count"],
                "stopping_episodes.csv": ["episode_id", "parent_episode_id", "run_id", "class", "region", "kind", "vehicle_id_or_null", "observation_domain", "stop_definition_id", "sampling_period_s", "first_label", "last_label", "sample_count", "support_seconds", "censor_left", "censor_right", "gap_reason", "TLS_context"],
                "spatial_propagation_evidence.csv": ["run_id", "chain_id", "ramp_end_event_id", "storage_event_id", "internal_event_set_id", "shared_R_event_id", "shared_U_event_id", "cooccurrence_support_s", "TLS_context_id", "contradiction_ids", "status", "reason"],
                "condition_evidence_summary.csv": ["run_id", "condition", "seed", "window", "entity", "metric", "value", "unit", "denominator", "qualification", "source_event_id", "reason"],
            }
            def write_table(path, fields, rows):
                with path.open("w", encoding="utf-8", newline="") as handle:
                    writer = csv.DictWriter(handle, fieldnames=fields)
                    writer.writeheader(); writer.writerows(rows)
            for source in sources:
                run_root = work / "runs" / source["run_id"]
                output = run_root / "output"; tables = run_root / "tables"
                output.mkdir(parents=True); tables.mkdir()
                for name, fields in table_fields.items():
                    if name == "condition_evidence_summary.csv":
                        rows = [{key: "" for key in fields} for _ in range(5)]
                        for index, row in enumerate(rows):
                            row.update(run_id=source["run_id"], condition="C", seed="17", window="Full",
                                       entity=f"question:{index}", metric="diagnostic_evidence_status", value="1",
                                       unit="evidence_count", qualification="observed", reason="fixture")
                    else:
                        row = {key: "" for key in fields}; row["run_id"] = source["run_id"]
                        rows = [row]
                    write_table(tables / name, fields, rows)
                sensitivity_fields = ["run_id", "detector_group", "aggregation_s", "window", "metric", "value", "unit", "n_contrib", "covered_seconds", "qualification", "residual_vs_30s"]
                sensitivity_rows = [{key: "" for key in sensitivity_fields} for _ in range(12)]
                for row in sensitivity_rows: row["run_id"] = source["run_id"]
                write_table(output / "sensitivity.csv", sensitivity_fields, sensitivity_rows)
                write_table(output / "aggregation_timeseries.csv", ["run_id", "value"], [{"run_id": source["run_id"], "value": 1}])
                write_table(output / "endpoint_accounting.csv", ["run_id", "class"], [{"run_id": source["run_id"], "class": "R"}])
                (output / "propagation_event_sets.json").write_text(json.dumps({"run_id": source["run_id"]}), encoding="utf-8")
                (output / "condition_event_sets.json").write_text(json.dumps({f"{source['run_id']}:set": ["e1"]}), encoding="utf-8")
                all_outputs = list(tables.iterdir()) + list(output.iterdir())
                manifest = {"run_id": source["run_id"], "status": "analyzed_archive_only", "contract_sha256": contract_sha,
                            "source_map_path": source["source_map_path"], "source_map_sha256": source["source_map_sha256"],
                            "outputs": {str(path.relative_to(ROOT)): hashlib.sha256(path.read_bytes()).hexdigest() for path in all_outputs}}
                manifest_path = output / "manifest.json"; manifest_path.write_text(json.dumps(manifest), encoding="utf-8")
                manifests.append(manifest_path)
            aggregate_parent = work / "aggregate"; aggregate_parent.mkdir()
            args = argparse.Namespace(ledger=str(ledger_path), contract=str(contract_path),
                                      run_manifest=[str(path) for path in manifests],
                                      output_dir=str(aggregate_parent / "output"), table_dir=str(aggregate_parent / "tables"),
                                      figure_dir=str(aggregate_parent / "figures"))
            aggregate(args)
            self.equal(len(list((aggregate_parent / "tables").glob("*.csv"))), 5)
            combined = json.loads((aggregate_parent / "output" / "manifest.json").read_text())
            self.equal(combined["diagnostic_question_units"], 40)
            self.equal(combined["sensitivity_values"], 96)
            (manifests[0].parent / "sensitivity.csv").write_text("tampered", encoding="utf-8")
            args.output_dir = str(aggregate_parent / "bad_output")
            args.table_dir = str(aggregate_parent / "bad_tables")
            args.figure_dir = str(aggregate_parent / "bad_figures")
            self.raises(ValueError, aggregate, args)
        finally:
            shutil.rmtree(work)

    def test_17_analyze_run_writes_all_contract_tables_from_synthetic_archive(self):
        self.fixture("analyze_run_end_to_end")
        work = Path(tempfile.mkdtemp(dir=ROOT))
        try:
            archive = work / "archive"; outputs = archive / "outputs"; outputs.mkdir(parents=True)
            (archive / "network.net.xml").write_text("<net/>", encoding="utf-8")
            (archive / "scenario.add.xml").write_text("<additional/>", encoding="utf-8")
            (archive / "scenario.sumocfg").write_text("<configuration/>", encoding="utf-8")
            demand = "<routes>" + "".join(
                f'<flow id="{cls}_flow" begin="0" end="1500" number="1"/>' for cls in ("M", "R", "U", "X")) + "</routes>"
            (archive / "demand.rou.xml").write_text(demand, encoding="utf-8")
            summary = {"simulation": {"seed": 17}, "sumo_command": ["sumo", "--seed", "17"],
                       "sumo_version": "Eclipse SUMO sumo 1.26.0",
                       "netconvert_version": "Eclipse SUMO netconvert 1.26.0"}
            (archive / "summary.json").write_text(json.dumps(summary), encoding="utf-8")
            fcd_lines = ["<fcd-export>"]
            for time_s in range(2700):
                vehicles = ""
                if time_s == 0:
                    vehicles = '<vehicle id="R_flow.0" lane="ramp_storage_0" speed="0" pos="1"/>'
                elif time_s == 1:
                    vehicles = '<vehicle id="R_flow.0" lane="main_down_0" speed="1" pos="1"/>'
                fcd_lines.append(f'<timestep time="{time_s}">{vehicles}</timestep>')
            fcd_lines.append("</fcd-export>")
            (outputs / "fcd.xml").write_text("".join(fcd_lines), encoding="utf-8")
            (outputs / "tls_states.xml").write_text("<tlsStates>" + "".join(
                f'<tlsState time="{time_s}" id="urban_tls" state="Gr"/>' for time_s in range(2700)) + "</tlsStates>", encoding="utf-8")
            trip_rows = "".join(f'<tripinfo id="{cls}_flow.0" depart="0" arrival="10" departLane="main_down_0" departPos="0"/>' for cls in ("M", "R", "U", "X"))
            (outputs / "tripinfo.xml").write_text(f"<tripinfos>{trip_rows}</tripinfos>", encoding="utf-8")
            route_rows = "".join(f'<vehicle id="{cls}_flow.0"/>' for cls in ("M", "R", "U", "X"))
            (outputs / "vehroute.xml").write_text(f"<routes>{route_rows}</routes>", encoding="utf-8")
            (outputs / "sumo_summary.xml").write_text(
                '<summary><step time="1499" loaded="4" inserted="4" arrived="4"/>'
                '<step time="2699" loaded="4" inserted="4" arrived="4"/></summary>', encoding="utf-8")
            detectors = [
                ("up0", "origin_insertion_contaminated"), ("up1", "origin_insertion_contaminated"),
                ("int0", "M-only_internal_merge_entry"), ("int1", "M-only_internal_merge_entry"),
                ("down0", "downstream_passage"), ("down1", "downstream_passage"),
            ]
            e1_contract = []
            for detector_id, group in detectors:
                suffix = f"outputs/{detector_id}.xml"
                e1_contract.append({"detector_id": detector_id, "group": group, "output_suffix": suffix})
                intervals = "".join(f'<interval begin="{begin}" end="{begin + 30}" nVehContrib="1" speed="10"/>'
                                    for begin in range(0, 2700, 30))
                (archive / suffix).write_text(f"<detector>{intervals}</detector>", encoding="utf-8")
            source_files = [path for path in archive.rglob("*") if path.is_file()]
            original_root = "/private/tmp/synthetic_stage3"
            file_map = []
            for path in source_files:
                suffix = path.relative_to(archive).as_posix()
                file_map.append({"original_absolute_path": f"{original_root}/{suffix}",
                                 "archive_relative_path": str(path.relative_to(ROOT)),
                                 "sha256": hashlib.sha256(path.read_bytes()).hexdigest()})
            source_map = {"archive_status": "complete", "source_runtime_path": original_root,
                          "archive_runtime_relative_path": str(archive.relative_to(ROOT)), "file_map": file_map}
            source_map_path = work / "source_map.json"; source_map_path.write_text(json.dumps(source_map), encoding="utf-8")
            measurement = contract(2700); measurement.update({"versions": {"sumo": "Eclipse SUMO sumo 1.26.0",
                "netconvert": "Eclipse SUMO netconvert 1.26.0"},
                "tls": {"id": "urban_tls"}, "e1_detectors": e1_contract})
            measurement["stop_definition"]["id"] = "technical_stop"
            contract_path = work / "contract.json"; contract_path.write_text(json.dumps(measurement), encoding="utf-8")
            source_row = {"run_id": "C17", "seed": 17, "condition": "C",
                          "source_map_path": str(source_map_path.relative_to(ROOT)),
                          "source_map_sha256": hashlib.sha256(source_map_path.read_bytes()).hexdigest()}
            ledger = {"stage": "Stage 3", "authorization": {"status": "user_approved"}, "actual_sumo_starts": 0,
                      "budget": {"max_sumo_starts": 0}, "input_hashes": {
                          "measurement_contract_sha256": hashlib.sha256(contract_path.read_bytes()).hexdigest()},
                      "code_hashes": {"analyze_stage3_baseline.py": hashlib.sha256(
                          (ROOT / "src/analysis/analyze_stage3_baseline.py").read_bytes()).hexdigest()},
                      "source_runs": [source_row]}
            ledger_path = work / "ledger.json"; ledger_path.write_text(json.dumps(ledger), encoding="utf-8")
            generated = work / "generated"; generated.mkdir()
            args = argparse.Namespace(ledger=str(ledger_path), contract=str(contract_path), run_id="C17",
                                      output_dir=str(generated / "output"), table_dir=str(generated / "tables"))
            analyze_run(args)
            for name in ("coverage_audit.csv", "lane_class_timeline.csv", "stopping_episodes.csv",
                         "spatial_propagation_evidence.csv", "condition_evidence_summary.csv"):
                with (generated / "tables" / name).open(encoding="utf-8", newline="") as handle:
                    rows = list(csv.DictReader(handle))
                self.true(bool(rows), name)
            with (generated / "tables" / "stopping_episodes.csv").open(encoding="utf-8", newline="") as handle:
                episode_rows = list(csv.DictReader(handle))
            self.equal({row["observation_domain"] for row in episode_rows}, {"Full", "A"})
            self.true(all(row["parent_episode_id"] for row in episode_rows if row["observation_domain"] != "Full"))
            with (generated / "tables" / "condition_evidence_summary.csv").open(encoding="utf-8", newline="") as handle:
                condition_rows = list(csv.DictReader(handle))
            self.equal(sum(row["metric"] == "diagnostic_evidence_status" for row in condition_rows), 5)
            with (generated / "output" / "endpoint_accounting.csv").open(encoding="utf-8", newline="") as handle:
                endpoint_rows = list(csv.DictReader(handle))
            self.equal(len(endpoint_rows), 8)
            self.true(all(row["coverage"] == "True" for row in endpoint_rows))
            with (generated / "output" / "sensitivity.csv").open(encoding="utf-8", newline="") as handle:
                self.equal(len(list(csv.DictReader(handle))), 12)
        finally:
            shutil.rmtree(work)


if __name__ == "__main__":
    unittest.main(verbosity=2)

"""Offline analysis and sequential-state adapter for the registered Stage 4 qMain block.

This module reads immutable archives through verified source maps.  It has no
simulation runner, subprocess, TraCI, SUMO, GUI, or network entry point.
"""

from __future__ import annotations

import argparse
from collections import defaultdict
import hashlib
import json
import math
import os
from pathlib import Path
import posixpath
import re
import sys
import xml.etree.ElementTree as ET

if __package__:
    from src.analysis import analyze_stage3_baseline as stage3
else:  # Direct CLI execution resolves the reviewed sibling module without changing sys.path.
    import analyze_stage3_baseline as stage3


ROOT = Path(__file__).resolve().parents[2]
BATCH_ID = "stage4_qmain_sequential_20260912_v1"
T42_AUTHORIZATION_QUOTE = "批准，继续stage 4"
T42_AUTHORIZATION_CONTEXT = (
    "请批准按 Stage 4精确注册方案执行 T42离线实现与三专业复审。"
    "完成后我会提交包含最终代码哈希、命令和零缺项合同的T43运行卡，"
    "再由你决定是否授权2–4次新仿真。"
)
REGISTRATION_PAYLOAD_RELATIVE_PATH = (
    "data/processed/stage4_qmain_sequential_20260912_v1/registration_payload.json"
)
REFERENCE_IDS = ("C17", "C23", "MH17", "MH23")
TIER1_IDS = ("QM3500S17", "QM3500S23")
LOWER_IDS = ("QM3350S17", "QM3350S23")
UPPER_IDS = ("QM3650S17", "QM3650S23")
ALL_RUN_IDS = REFERENCE_IDS + TIER1_IDS + LOWER_IDS + UPPER_IDS
MANIFEST_RECEIPT_REGISTRY_RELATIVE_PATH = (
    "data/processed/stage4_qmain_sequential_20260912_v1/"
    "candidate_manifest_receipt_registry.json"
)
MANIFEST_RECEIPT_DIRECTORY_RELATIVE_PATH = (
    "data/processed/stage4_qmain_sequential_20260912_v1/"
    "candidate_manifest_receipts"
)
TIER1_SCIENTIFIC_DECISION_RELATIVE_PATH = (
    "data/processed/stage4_qmain_sequential_20260912_v1/"
    "analysis/tier1/revision_05/decision/branch_decision.json"
)
TIER2_BRANCH_GATE_RELATIVE_PATH = (
    "data/processed/stage4_qmain_sequential_20260912_v1/"
    "tier2_branch_gate_registration.json"
)
TIER1_SCIENTIFIC_REVIEW_RECEIPT_RELATIVE_PATH = (
    "data/processed/stage4_qmain_sequential_20260912_v1/"
    "tier1_scientific_branch_review_receipt.json"
)
TIER1_MANIFEST_RECEIPT_REGISTRY_SNAPSHOT_RELATIVE_PATH = (
    "data/processed/stage4_qmain_sequential_20260912_v1/"
    "candidate_manifest_receipt_registry_snapshots/tier1_complete.json"
)
T43_AUTHORIZATION_QUOTE = (
    "批准按 `docs/STAGE4_T43_LAUNCH_CONFIRMATION_PACKAGE.md` 执行 T43。"
)
SCIENTIFIC_BRANCH_REVIEW_RELAY = "科学review确认唯一branch=run_q3650"
TERMINAL_STATES = {
    "reused_valid",
    "completed_valid",
    "completed_invalid",
    "failed",
    "cancelled_by_stop_rule",
}
EXPECTED_RUNTIME_SUFFIXES = (
    "scenario.nod.xml", "scenario.edg.xml", "scenario.con.xml",
    "scenario.tll.xml", "scenario.add.xml", "scenario.sumocfg",
    "network.net.xml", "demand.rou.xml", "netconvert.stdout.log",
    "netconvert.stderr.log", "summary.json", "outputs/fcd.xml",
    "outputs/mainline_merge_entry_e1_l0.xml",
    "outputs/mainline_merge_entry_e1_l1.xml",
    "outputs/merge_downstream_e1_l0.xml",
    "outputs/merge_downstream_e1_l1.xml",
    "outputs/merge_upstream_e1_l0.xml",
    "outputs/merge_upstream_e1_l1.xml", "outputs/queues.xml",
    "outputs/ramp_storage_e2.xml", "outputs/shared_boundary_e2.xml",
    "outputs/sumo.log", "outputs/sumo.stderr.log",
    "outputs/sumo.stdout.log", "outputs/sumo_error.log",
    "outputs/sumo_summary.xml", "outputs/tls_states.xml",
    "outputs/tripinfo.xml", "outputs/vehroute.xml",
)

REGISTERED_WINDOWS = {
    "A": [0.0, 1500.0], "B": [300.0, 1500.0],
    "Post": [1500.0, 2700.0], "Full": [0.0, 2700.0],
}
REGISTERED_E1 = {
    "internal_detector_ids": ["mainline_merge_entry_e1_l0", "mainline_merge_entry_e1_l1"],
    "internal_output_suffixes": [
        "outputs/mainline_merge_entry_e1_l0.xml",
        "outputs/mainline_merge_entry_e1_l1.xml",
    ],
    "period_s": 30.0,
    "q_rule": "sum nVehEntered across both lanes * 3600 / covered seconds",
    "speed_rule": (
        "sum(speed_mps*nVehContrib)/sum(nVehContrib) across both lanes; "
        "null when denominator=0"
    ),
    "occupancy_rule": (
        "arithmetic mean of the two lane occupancy percentages per aligned bin; "
        "duration-weighted across bins; never summed or called density"
    ),
}
REGISTERED_Q_DEFINITION = {
    "requested_input_unit": "veh/h",
    "demand_duration_s": 1500.0,
    "planned_demand_vehph_rule": "planned_count * 3600 / demand_duration_s",
    "realized_entry_window": "A=[0,1500)",
    "realized_entry_duration_s": 1500.0,
    "realized_entry_vehph_A_rule": (
        "covered class-specific entered count at endpoint_s=1500 * 3600 / A duration"
    ),
    "internal_and_downstream_e1_q_rule": (
        "sum nVehEntered across two declared lanes * 3600 / covered seconds"
    ),
    "warning": (
        "planned demand, realized network entry, and E1 passage flow are distinct quantities; "
        "Stage 4 E1 q uses nVehEntered; do not mix with Stage 3 nVehContrib q values"
    ),
}
REGISTERED_EJMI = {
    "name": "EJMI sufficient signature",
    "margins": {
        "A": {"delta_v_mps": 0.5516661889683938, "delta_occ_percentage_points": 0.1658},
        "B": {"delta_v_mps": 0.5020140721737434, "delta_occ_percentage_points": 0.17725},
    },
    "aggregate_rule": (
        "candidate speed below min same-seed C/MH minus margin and occupancy above max plus margin in A and B"
    ),
    "persistence_rule": (
        "within B: one aligned 120s block passes, both contained 60s bins pass, and at least 3/4 "
        "contained 30s bins pass against same-clock C/MH envelopes"
    ),
    "interpretation": (
        "exploratory local sufficient discriminator; not Breakdown, Capacity Drop, capacity, or absence evidence"
    ),
}
REGISTERED_BRANCH_RULE = {
    "tier1": list(TIER1_IDS),
    "passage_and_positive_ejmi": "stop_supports_A",
    "passage_and_not_identified_ejmi": list(UPPER_IDS),
    "exclusion_and_not_positive_ejmi": list(LOWER_IDS),
    "any_unqualified_seed_disagreement_or_nonbranchable": "stop_unresolved",
    "maximum_tier2_branches": 1,
}
REGISTERED_FINAL_DECISION_RULE = {
    "used_candidate_universes": [[3500], [3350, 3500], [3500, 3650]],
    "pair_requirement": "every used qMain has exactly seeds 17 and 23 and all manifests are technically qualified",
    "supports_A_within_registered_points": (
        "at least one used qMain has both seeds clear_passage and EJMI positive, with no unresolved state "
        "and no same-point clear_exclusion plus positive contradiction"
    ),
    "supports_B_pattern_within_registered_points": (
        "all used seeds are qualified and consistent, every EJMI is not_identified, and q-ordered R states "
        "contain one transition from one-or-more clear_passage points to one-or-more clear_exclusion points"
    ),
    "unresolved": (
        "same-point positive plus exclusion, missing/incomplete seed pair, unqualified run, seed disagreement, "
        "unregistered state, nonmonotone or nondiscriminating pattern"
    ),
    "additional_points_or_seeds_prohibited": True,
}
REGISTERED_BUDGET = {
    "regular_new_sumo_starts_min": 2,
    "regular_new_sumo_starts_max": 4,
    "technical_retry_allowance": 1,
    "hard_sumo_start_cap": 5,
    "hard_netconvert_operation_cap": 5,
    "reserved_sumo_starts": 0,
    "regular_netconvert_operations_min": 2,
    "regular_netconvert_operations_max": 4,
}
REGISTERED_OBSERVATIONS_SHA256 = "61d1a6921feb501f641d97ebc3faa462ba183d9df04bd0d1622f497112b8754e"
REGISTERED_REFERENCE_MAP_SHA256 = "1c061f9e5a18ffae50b1c5c41568255e765935b81a4f1535e5e10c05cb5d6e99"
REQUIRED_CANDIDATE_OBSERVATION_KEYS = (
    "planned_demand_vehph",
    "realized_entry_vehph_A",
    "q_definition",
    "downstream_e1",
    "m_stopped_episodes",
    "m_stopped_position_range",
    "m_depart_position_range",
    "r_propagation",
    "shared_r_u_stopped_exposure",
    "tls_context",
    "warning_coverage_audit",
    "qualification",
)
REQUIRED_OBSERVATION_AUDIT_KEYS = (
    "fcd", "downstream_e1", "tls", "entry_accounting", "m_depart_position",
    "technical_warnings", "source_inventory",
)
SOURCE_PATHS = {
    "run_minimal_uncontrolled.py": ROOT / "src/scenarios/run_minimal_uncontrolled.py",
    "internal_lane_accounting.py": ROOT / "src/analysis/internal_lane_accounting.py",
    "archive_stage2_runtime.py": ROOT / "src/analysis/archive_stage2_runtime.py",
    "analyze_stage3_baseline.py": ROOT / "src/analysis/analyze_stage3_baseline.py",
}
BINARY_PATHS = {
    "sumo": Path("/Library/Frameworks/EclipseSUMO.framework/Versions/1.26.0/EclipseSUMO/bin/sumo"),
    "netconvert": Path("/Library/Frameworks/EclipseSUMO.framework/Versions/1.26.0/EclipseSUMO/bin/netconvert"),
}
REGISTERED_ENDPOINT_RULE = {
    "classes": ["M", "R", "U", "X"],
    "times_s": [1500.0, 2700.0],
    "fields": ["planned", "entered", "arrived", "outside", "in_network", "coverage"],
    "identities": ["planned=entered+outside", "entered=arrived+in_network"],
}
REGISTERED_R_PASSAGE = {
    "window": [0.0, 1500.0],
    "downstream_lanes": ["main_down_0", "main_down_1"],
    "known_lane_ids": [
        ":freeway_merge_0_0", ":freeway_merge_1_0", ":freeway_merge_1_1", ":ramp_mid_0_0",
        ":urban_diverge_0_0", ":urban_diverge_1_0", ":urban_tls_0_0", ":urban_tls_1_0",
        "cross_in_0", "cross_out_0", "main_down_0", "main_down_1", "main_up_0", "main_up_1",
        "ramp_accel_0", "ramp_storage_0", "shared_approach_0", "urban_in_0", "urban_out_0",
    ],
    "clear_passage": "at least one identity-resolved consecutive-1Hz bracketed first downstream R event",
    "clear_exclusion": "zero such events with complete FCD/identity/boundary coverage and no arrival contradiction",
    "unresolved": "one-zero/one-nonzero across seeds, missing/duplicate/unknown coverage, unbracketed/arrival contradiction",
}
REGISTERED_DENOMINATORS = {
    "registration_universe_runs": 10,
    "tier1_used_runs": 6,
    "tier2_used_runs": 8,
    "tier1_endpoint_units": 48,
    "tier2_endpoint_units": 64,
    "tier1_adjacent_matched_seed_comparisons": 4,
    "tier2_adjacent_matched_seed_comparisons": 6,
    "cancelled_runs_remain_in_registered_terminal_denominator": True,
}


def digest(path: Path) -> str:
    value = hashlib.sha256()
    with Path(path).open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            value.update(block)
    return value.hexdigest()


def payload_digest(value: object) -> str:
    encoded = json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def load_json(path: Path) -> dict:
    value = json.loads(Path(path).read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"expected JSON object: {path}")
    return value


def write_json_exclusive(path: Path, value: object) -> None:
    path = Path(path)
    if not path.parent.is_dir():
        raise FileNotFoundError(f"output parent does not exist: {path.parent}")
    with path.open("x", encoding="utf-8") as stream:
        json.dump(value, stream, indent=2, sort_keys=True, allow_nan=False)
        stream.write("\n")


def write_json_atomic(path: Path, value: object, *, must_not_exist: bool = False) -> None:
    """Write JSON through a sibling partial file and an atomic rename."""

    path = Path(path)
    if not path.parent.is_dir():
        raise FileNotFoundError(f"output parent does not exist: {path.parent}")
    if must_not_exist and path.exists():
        raise FileExistsError(f"refusing to overwrite {path}")
    partial = path.with_name(f".{path.name}.partial")
    if partial.exists():
        raise FileExistsError(f"stale or concurrent partial file exists: {partial}")
    try:
        with partial.open("x", encoding="utf-8") as stream:
            json.dump(value, stream, indent=2, sort_keys=True, allow_nan=False)
            stream.write("\n")
        if must_not_exist and path.exists():
            raise FileExistsError(f"refusing to overwrite {path}")
        os.replace(partial, path)
    except Exception:
        if partial.exists():
            partial.unlink()
        raise


def _is_under(path: Path, parent: Path) -> bool:
    resolved = Path(path).resolve()
    root = Path(parent).resolve()
    return resolved == root or root in resolved.parents


def reject_temporary_output(path: Path) -> None:
    resolved = Path(path).resolve()
    for root in (Path("/tmp"), Path("/private/tmp"), Path("/var/tmp"), Path("/private/var/tmp")):
        if _is_under(resolved, root):
            raise ValueError(f"temporary output prohibited: {resolved}")


def reserve_directory(path: Path) -> Path:
    path = Path(path).resolve()
    reject_temporary_output(path)
    if not _is_under(path, ROOT):
        raise ValueError("output must remain inside project")
    if path.exists():
        raise FileExistsError(f"refusing to overwrite {path}")
    if not path.parent.is_dir():
        raise FileNotFoundError(f"output parent does not exist: {path.parent}")
    os.mkdir(path)
    return path


class ArchiveResolver:
    """Resolve archive entries only through a complete, verified source map."""

    def __init__(self, source_map: Path, project_root: Path = ROOT):
        self.project_root = Path(project_root).resolve()
        self.source_map_path = Path(source_map).resolve(strict=True)
        if not _is_under(self.source_map_path, self.project_root):
            raise ValueError("source map must remain inside project")
        source = load_json(self.source_map_path)
        if source.get("archive_status") != "complete":
            raise ValueError("archive is not complete")
        original_root = posixpath.normpath(source["source_runtime_path"])
        archive_root = (self.project_root / source["archive_runtime_relative_path"]).resolve()
        if not _is_under(archive_root, self.project_root):
            raise ValueError("archive root escapes project")
        self._entries: dict[str, tuple[Path, str]] = {}
        for row in source.get("file_map", []):
            original = posixpath.normpath(row["original_absolute_path"])
            if not original.startswith(original_root + "/"):
                raise ValueError("mapped source escapes original runtime")
            suffix = posixpath.relpath(original, original_root)
            archived = (self.project_root / row["archive_relative_path"]).resolve()
            if suffix in self._entries or not _is_under(archived, archive_root):
                raise ValueError("duplicate or escaping archive mapping")
            if archived.is_symlink() or not archived.is_file():
                raise ValueError(f"archive entry is not a regular file: {suffix}")
            if digest(archived) != row["sha256"]:
                raise ValueError(f"archive hash mismatch: {suffix}")
            self._entries[suffix] = (archived, row["sha256"])
        if set(EXPECTED_RUNTIME_SUFFIXES).difference(self._entries):
            raise ValueError("source map lacks required Stage 4 runtime outputs")

    def resolve(self, suffix: str) -> Path:
        if suffix.startswith("/") or posixpath.normpath(suffix).startswith("../"):
            raise ValueError("only registered runtime suffixes are accepted")
        item = self._entries.get(posixpath.normpath(suffix))
        if item is None:
            raise KeyError(f"unregistered archive suffix: {suffix}")
        path, expected = item
        if digest(path) != expected:
            raise ValueError(f"archive changed after resolver creation: {suffix}")
        return path

    def inventory_hashes(self) -> dict[str, str]:
        return {suffix: expected for suffix, (_, expected) in sorted(self._entries.items())}


def finite(value: object, field: str) -> float:
    try:
        result = float(value)
    except (TypeError, ValueError) as error:
        raise ValueError(f"{field} is not numeric") from error
    if not math.isfinite(result):
        raise ValueError(f"{field} is not finite")
    return result


def _mapped_archive_file(source_map_path: Path, suffix: str) -> Path:
    source = load_json(source_map_path)
    rows = [row for row in source.get("file_map", [])
            if row.get("original_absolute_path", "").endswith("/" + suffix)]
    if len(rows) != 1:
        raise ValueError(f"source map does not uniquely register {suffix}")
    path = (ROOT / rows[0]["archive_relative_path"]).resolve()
    if not _is_under(path, ROOT) or not path.is_file() or digest(path) != rows[0]["sha256"]:
        raise ValueError(f"mapped archive file invalid: {suffix}")
    return path


def validate_additional_semantics(path: Path, observations: dict, *, runtime: bool) -> None:
    root = ET.parse(path).getroot()
    e1 = {node.get("id"): node for node in root.findall("inductionLoop")}
    expected_e1 = {row["detector_id"]: row for row in observations["e1_detectors"]}
    if set(e1) != set(expected_e1):
        raise ValueError("scenario.add E1 detector IDs changed")
    for detector_id, expected in expected_e1.items():
        node = e1[detector_id]
        if (node.get("lane") != expected["lane_id"]
                or not math.isclose(finite(node.get("pos"), "E1 pos"), expected["position_m"])
                or not math.isclose(finite(node.get("period"), "E1 period"), expected["period_s"])):
            raise ValueError(f"scenario.add E1 semantics changed: {detector_id}")
    e2 = {node.get("id"): node for node in root.findall("laneAreaDetector")}
    expected_e2 = {row["detector_id"]: row for row in observations["e2_detectors"]}
    if set(e2) != set(expected_e2):
        raise ValueError("scenario.add E2 detector IDs changed")
    for detector_id, expected in expected_e2.items():
        node = e2[detector_id]
        expected_end = expected["end_pos_m"] if runtime else -0.1
        if (node.get("lane") != expected["lane_id"]
                or not math.isclose(finite(node.get("pos"), "E2 begin"), expected["begin_pos_m"])
                or not math.isclose(finite(node.get("endPos"), "E2 end"), expected_end)
                or not math.isclose(finite(node.get("period"), "E2 period"), expected["period_s"])):
            raise ValueError(f"scenario.add E2 semantics changed: {detector_id}")
    events = root.findall("timedEvent")
    expected_event = observations["scenario_add_semantics"]["tls_event"]
    if len(events) != 1 or any(events[0].get(key) != value for key, value in expected_event.items()):
        raise ValueError("scenario.add TLS-state event changed")


def validate_compiled_topology(path: Path, observations: dict) -> None:
    root = ET.parse(path).getroot()
    lanes: dict[str, tuple[str, float, float]] = {}
    for edge in root.findall("edge"):
        edge_id = edge.get("id")
        for lane in edge.findall("lane"):
            lanes[lane.get("id", "")] = (
                edge_id, finite(lane.get("length"), "lane length"), finite(lane.get("speed"), "lane speed")
            )
    expected_lanes = observations["lanes"]
    if set(lanes) != set(expected_lanes):
        raise ValueError("compiled topology lane universe changed")
    for lane_id, expected in expected_lanes.items():
        edge_id, length, speed = lanes[lane_id]
        if (edge_id != expected["edge_id"]
                or not math.isclose(length, expected["length_m"], abs_tol=1e-2)
                or not math.isclose(speed, expected["speed_limit_mps"], abs_tol=1e-2)):
            raise ValueError(f"compiled lane semantics changed: {lane_id}")
    tls = root.find(f"./tlLogic[@id='{observations['compiled_topology']['required_tls_id']}']")
    if tls is None or [node.get("state") for node in tls.findall("phase")] != observations["compiled_topology"]["required_tls_phase_states"]:
        raise ValueError("compiled TLS semantics changed")
    detector_lanes = {row["lane_id"] for row in observations["e1_detectors"] + observations["e2_detectors"]}
    if not detector_lanes.issubset(lanes):
        raise ValueError("registered detector lane absent from compiled topology")


def validate_registration_payload(payload: dict) -> None:
    observation_contract = payload.get("required_observations")
    reference_map = payload.get("ejmi_reference_map")
    if payload_digest(observation_contract) != REGISTERED_OBSERVATIONS_SHA256:
        raise ValueError("registered complete-observation contract changed")
    if payload_digest(reference_map) != REGISTERED_REFERENCE_MAP_SHA256:
        raise ValueError("registered same-seed EJMI reference map changed")
    stripped = dict(payload)
    stripped.pop("required_observations", None)
    stripped.pop("ejmi_reference_map", None)
    expected = {
        "schema_version": 1,
        "batch_id": BATCH_ID,
        "payload_id": "stage4_qmain_scientific_registration_v1",
        "classification": "exploratory targeted validation; not formal or thesis evidence",
        "logical_run_ids": list(ALL_RUN_IDS),
        "q_main_points": [3200, 3350, 3500, 3650, 3800],
        "seeds": [17, 23],
        "controller": "none",
        "only_intervention": "q_main",
        "fixed_demand_vehph": {"R": 720.0, "U": 360.0, "X": 180.0},
        "fixed_plan_counts": {"R": 300, "U": 150, "X": 75},
        "planned_M_counts": {"3200": 1333, "3350": 1396, "3500": 1458, "3650": 1521, "3800": 1583},
        "demand_xml_number_rule": "int(round(rate_vehph * 1500 / 3600.0))",
        "windows": REGISTERED_WINDOWS,
        "e1": REGISTERED_E1,
        "ejmi": REGISTERED_EJMI,
        "r_passage": REGISTERED_R_PASSAGE,
        "endpoint_rule": REGISTERED_ENDPOINT_RULE,
        "denominator_rules": REGISTERED_DENOMINATORS,
        "branch_rule": REGISTERED_BRANCH_RULE,
        "final_decision_rule": REGISTERED_FINAL_DECISION_RULE,
        "budget": REGISTERED_BUDGET,
        "authorization_boundary": {
            "t42_quote": T42_AUTHORIZATION_QUOTE,
            "t42_scope": "T42_offline_implementation_and_review_only",
            "t43_status": "prohibited",
            "t43_quote": None,
        },
        "additional_qmain_points_prohibited": True,
        "simulation_launch_capability": False,
    }
    if stripped != expected:
        raise ValueError("immutable Stage 4 scientific registration payload changed")


def validate_contract(contract: dict, payload: dict | None = None) -> None:
    if contract.get("batch_id") != BATCH_ID or contract.get("status") != "t42_offline_ready_t43_prohibited":
        raise ValueError("wrong Stage 4 contract identity/status")
    if tuple(contract.get("logical_run_ids", ())) != ALL_RUN_IDS:
        raise ValueError("contract logical-run universe changed")
    if contract.get("controller") != "none" or contract.get("only_intervention") != "q_main":
        raise ValueError("contract is not the registered uncontrolled qMain-only design")
    if contract.get("windows") != REGISTERED_WINDOWS:
        raise ValueError("Stage 4 windows changed")
    if contract.get("e1") != REGISTERED_E1:
        raise ValueError("registered E1 arithmetic or 30-second declaration changed")
    if contract.get("ejmi") != REGISTERED_EJMI:
        raise ValueError("registered EJMI definition or exact margins changed")
    if contract.get("branch_rule") != REGISTERED_BRANCH_RULE:
        raise ValueError("registered sequential branch rule changed")
    if contract.get("final_decision_rule") != REGISTERED_FINAL_DECISION_RULE:
        raise ValueError("registered final decision matrix changed")
    if contract.get("budget") != REGISTERED_BUDGET:
        raise ValueError("registered SUMO/netconvert budget changed")
    if payload_digest(contract.get("required_observations")) != REGISTERED_OBSERVATIONS_SHA256:
        raise ValueError("complete-observation contract changed")
    if payload_digest(contract.get("ejmi_reference_map")) != REGISTERED_REFERENCE_MAP_SHA256:
        raise ValueError("same-seed EJMI reference map changed")
    if contract.get("registration_payload_path") != REGISTRATION_PAYLOAD_RELATIVE_PATH:
        raise ValueError("registration payload path changed")
    if payload is not None:
        validate_registration_payload(payload)
        for key in (
            "classification", "logical_run_ids", "q_main_points", "seeds", "controller",
            "only_intervention", "fixed_demand_vehph", "fixed_plan_counts", "planned_M_counts",
            "demand_xml_number_rule", "windows", "e1", "ejmi", "r_passage", "endpoint_rule",
            "denominator_rules", "branch_rule", "final_decision_rule",
            "simulation_launch_capability",
            "required_observations", "ejmi_reference_map",
        ):
            if contract.get(key) != payload.get(key):
                raise ValueError(f"contract differs from immutable registration payload: {key}")


def validate_context(ledger_path: Path, contract_path: Path, registry_path: Path) -> tuple[dict, dict, dict]:
    ledger, contract, registry = map(load_json, (ledger_path, contract_path, registry_path))
    payload_path = ROOT / contract.get("registration_payload_path", "")
    if not payload_path.is_file():
        raise ValueError("immutable registration payload is missing")
    payload = load_json(payload_path)
    payload_hash = digest(payload_path)
    if contract.get("registration_payload_sha256") != payload_hash:
        raise ValueError("contract registration payload hash mismatch")
    validate_contract(contract, payload)
    if ledger.get("batch_id") != BATCH_ID or registry.get("batch_id") != BATCH_ID:
        raise ValueError("batch identity mismatch")
    if ledger.get("budget") != payload["budget"]:
        raise ValueError("ledger launch budget differs from immutable registration payload")
    if (registry.get("registration_payload_path") != REGISTRATION_PAYLOAD_RELATIVE_PATH
            or registry.get("registration_payload_sha256") != payload_hash):
        raise ValueError("source registry registration payload binding mismatch")
    if (registry.get("ejmi_reference_map") != payload["ejmi_reference_map"]
            or registry.get("required_observations_sha256") != REGISTERED_OBSERVATIONS_SHA256):
        raise ValueError("source registry science-map binding mismatch")
    auth = ledger.get("t42_authorization", {})
    if auth.get("quote") != T42_AUTHORIZATION_QUOTE or auth.get("scope") != "T42_offline_implementation_and_review_only":
        raise ValueError("T42 authorization record is absent or overbroad")
    launch = ledger.get("t43_launch_authorization", {})
    if launch.get("status") not in {"prohibited", "user_approved"}:
        raise ValueError("invalid T43 authorization state")
    execution_counters = (
        "actual_sumo_starts", "actual_netconvert_operations",
        "actual_traci_connections", "actual_gui_starts",
    )
    if launch.get("status") == "prohibited" and any(ledger.get(key) != 0 for key in execution_counters):
        raise ValueError("prohibited T43 ledger cannot contain starts")
    if launch.get("status") == "prohibited" and launch.get("quote") is not None:
        raise ValueError("prohibited T43 state cannot claim an authorization quote")
    if launch.get("status") == "user_approved":
        quote = launch.get("quote")
        required = {
            "scope": "T43_exact_registered_runs_only",
            "approved_registration_payload_sha256": payload_hash,
            "approved_contract_sha256": digest(contract_path),
            "approved_source_registry_sha256": digest(registry_path),
        }
        if (not isinstance(quote, str) or not quote.strip() or quote != quote.strip()
                or quote == T42_AUTHORIZATION_QUOTE
                or any(launch.get(key) != value for key, value in required.items())):
            raise ValueError("T43 approval lacks exact nonpending quote or launch-card hashes")
    hashes = ledger.get("input_hashes", {})
    if hashes.get("contract_sha256") != digest(contract_path):
        raise ValueError("contract hash mismatch")
    if hashes.get("source_registry_sha256") != digest(registry_path):
        raise ValueError("source registry hash mismatch")
    if hashes.get("registration_payload_sha256") != payload_hash:
        raise ValueError("ledger registration payload hash mismatch")
    if ledger.get("code_hashes", {}).get("analyze_stage4_qmain.py") != digest(Path(__file__)):
        raise ValueError("Stage 4 adapter hash mismatch")
    if tuple(row.get("run_id") for row in ledger.get("logical_runs", [])) != ALL_RUN_IDS:
        raise ValueError("ledger logical-run universe/order changed")
    if tuple(row.get("run_id") for row in registry.get("runs", [])) != ALL_RUN_IDS:
        raise ValueError("registry logical-run universe/order changed")
    ledger_rows = {row["run_id"]: row for row in ledger["logical_runs"]}
    registry_rows = {row["run_id"]: row for row in registry["runs"]}
    for run_id in ALL_RUN_IDS:
        for key in ("seed", "q_main"):
            if ledger_rows[run_id].get(key) != registry_rows[run_id].get(key):
                raise ValueError(f"ledger/registry {key} mismatch: {run_id}")
    for name, path in SOURCE_PATHS.items():
        if not path.is_file() or digest(path) != contract.get("source_code_hashes", {}).get(name):
            raise ValueError(f"registered source-code hash mismatch: {name}")
    for name, path in BINARY_PATHS.items():
        if not path.is_file() or digest(path) != contract.get("binary_hashes", {}).get(name):
            raise ValueError(f"registered binary hash mismatch: {name}")
    observations = contract["required_observations"]
    source_add = ROOT / observations["scenario_add_semantics"]["source_path"]
    if (not source_add.is_file()
            or digest(source_add) != observations["scenario_add_semantics"]["source_sha256"]):
        raise ValueError("scenario.add source hash mismatch")
    validate_additional_semantics(source_add, observations, runtime=False)
    for run_id in REFERENCE_IDS:
        registered = registry_rows[run_id]
        manifest_path_text = registered.get("reference_manifest_path")
        if not manifest_path_text:
            raise ValueError(f"registered reference manifest missing: {run_id}")
        manifest_path = (ROOT / manifest_path_text).resolve()
        if not _is_under(manifest_path, ROOT) or not manifest_path.is_file():
            raise ValueError(f"registered reference manifest path invalid: {run_id}")
        manifest = load_json(manifest_path)
        _validate_manifest(manifest, ledger_rows[run_id], True)
        if (registered.get("reference_manifest_payload_sha256") != _manifest_payload_hash(manifest)
                or manifest.get("source_map_path") != registered.get("source_map_path")
                or manifest.get("source_map_sha256") != registered.get("source_map_sha256")
                or not manifest.get("single_factor_hash_check")
                or not manifest.get("technical_qualified")):
            raise ValueError(f"registered reference manifest provenance invalid: {run_id}")
        source_map = ROOT / registered["source_map_path"]
        if not source_map.is_file() or digest(source_map) != registered["source_map_sha256"]:
            raise ValueError(f"registered reference source map invalid: {run_id}")
        validate_additional_semantics(_mapped_archive_file(source_map, "scenario.add.xml"), observations, runtime=True)
        network_path = _mapped_archive_file(source_map, "network.net.xml")
        if digest(network_path) != observations["compiled_topology"]["registered_reference_network_sha256"][run_id]:
            raise ValueError(f"registered compiled-network hash mismatch: {run_id}")
        validate_compiled_topology(network_path, observations)
    reference_map = contract["ejmi_reference_map"]
    for candidate_id in TIER1_IDS + LOWER_IDS + UPPER_IDS:
        expected = reference_map.get(candidate_id)
        if not expected or registry_rows[candidate_id].get("ejmi_references") != expected:
            raise ValueError(f"candidate EJMI reference binding missing: {candidate_id}")
        if (expected.get("candidate_run_id") != candidate_id
                or expected.get("candidate_seed") != registry_rows[candidate_id]["seed"]
                or expected.get("candidate_q_main") != registry_rows[candidate_id]["q_main"]):
            raise ValueError(f"candidate EJMI identity changed: {candidate_id}")
        for side, prefix, q_main in (("lower", "C", 3200), ("upper", "MH", 3800)):
            ref = expected[side]
            ref_id = f"{prefix}{expected['candidate_seed']}"
            if (ref.get("run_id") != ref_id or ref.get("seed") != expected["candidate_seed"]
                    or ref.get("q_main") != q_main
                    or ref.get("manifest_payload_sha256") != ledger_rows[ref_id]["manifest_payload_sha256"]
                    or ref.get("manifest_path") != registry_rows[ref_id]["reference_manifest_path"]
                    or ref.get("source_map_path") != registry_rows[ref_id]["source_map_path"]
                    or ref.get("source_map_sha256") != registry_rows[ref_id]["source_map_sha256"]):
                raise ValueError(f"candidate uses an unregistered {side} reference: {candidate_id}")
    return ledger, contract, registry


def read_e1(path: Path, detector_id: str) -> list[dict]:
    rows: list[dict] = []
    seen: set[tuple[float, float]] = set()
    for _, node in ET.iterparse(path, events=("end",)):
        if node.tag != "interval":
            continue
        begin = finite(node.get("begin"), "E1 begin")
        end = finite(node.get("end"), "E1 end")
        key = (begin, end)
        if key in seen or end <= begin:
            raise ValueError("duplicate or invalid E1 interval")
        seen.add(key)
        n_contrib = int(node.get("nVehContrib", "-1"))
        n_entered = int(node.get("nVehEntered", "-1"))
        speed = finite(node.get("speed", "-1"), "E1 speed")
        occupancy = finite(node.get("occupancy"), "E1 occupancy")
        if n_contrib < 0 or n_entered < 0 or occupancy < 0:
            raise ValueError("invalid E1 contribution/count/occupancy")
        if n_contrib and speed < 0:
            raise ValueError("contributing E1 interval lacks speed")
        rows.append({"detector_id": detector_id, "begin": begin, "end": end,
                     "n_contrib": n_contrib, "n_entered": n_entered,
                     "speed_mps": None if n_contrib == 0 else speed,
                     "occupancy_percent": occupancy})
        node.clear()
    return rows


def combine_two_lane_e1(rows: list[dict], detector_ids: set[str], expected_begin: float = 0.0,
                        expected_end: float = 2700.0, period_s: float = 30.0) -> list[dict]:
    grouped: defaultdict[tuple[float, float], list[dict]] = defaultdict(list)
    for row in rows:
        if row["detector_id"] not in detector_ids:
            raise ValueError("unexpected detector in M-only E1 rows")
        grouped[(row["begin"], row["end"])].append(row)
    bins: list[dict] = []
    cursor = expected_begin
    while cursor < expected_end:
        key = (cursor, min(cursor + period_s, expected_end))
        selected = grouped.get(key, [])
        if {row["detector_id"] for row in selected} != detector_ids or len(selected) != len(detector_ids):
            raise ValueError(f"M-only E1 lane coverage incomplete for {key}")
        duration = key[1] - key[0]
        contrib = sum(row["n_contrib"] for row in selected)
        speed_num = sum(row["speed_mps"] * row["n_contrib"] for row in selected if row["speed_mps"] is not None)
        bins.append({"begin": key[0], "end": key[1],
                     "q_vehph": sum(row["n_entered"] for row in selected) * 3600.0 / duration,
                     "speed_mps": speed_num / contrib if contrib else None,
                     "occupancy_percent": sum(row["occupancy_percent"] for row in selected) / len(detector_ids),
                     "n_contrib": contrib})
        cursor = key[1]
    if len(grouped) != len(bins):
        raise ValueError("E1 includes extra or misaligned intervals")
    return bins


def aggregate_bins(bins: list[dict], begin: float, end: float) -> dict:
    selected = [row for row in bins if row["begin"] >= begin and row["end"] <= end]
    covered = sum(row["end"] - row["begin"] for row in selected)
    if not math.isclose(covered, end - begin):
        raise ValueError(f"incomplete E1 coverage for [{begin},{end})")
    contributions = sum(row["n_contrib"] for row in selected)
    speed_num = sum(row["speed_mps"] * row["n_contrib"] for row in selected if row["speed_mps"] is not None)
    duration_weight = sum((row["end"] - row["begin"]) for row in selected)
    return {
        "begin": begin, "end": end, "covered_seconds": covered,
        "q_vehph": sum(row["q_vehph"] * (row["end"] - row["begin"]) for row in selected) / duration_weight,
        "speed_mps": speed_num / contributions if contributions else None,
        "occupancy_percent": sum(row["occupancy_percent"] * (row["end"] - row["begin"]) for row in selected) / duration_weight,
        "n_contrib": contributions,
    }


def reaggregate_bins(bins: list[dict], begin: float, end: float, width: float) -> list[dict]:
    result: list[dict] = []
    cursor = begin
    while cursor < end:
        result.append(aggregate_bins(bins, cursor, min(cursor + width, end)))
        cursor += width
    return result


def vehicle_class(vehicle_id: str) -> str:
    match = re.fullmatch(r"(M|R|U|X)_flow\.(\d+)", vehicle_id)
    if not match:
        raise ValueError(f"unregistered vehicle identity: {vehicle_id}")
    return match.group(1)


def read_plan(path: Path) -> dict[str, int]:
    result: dict[str, int] = {}
    for flow in ET.parse(path).getroot().findall("flow"):
        cls = flow.get("id", "").split("_", 1)[0]
        if cls not in {"M", "R", "U", "X"} or cls in result:
            raise ValueError("invalid demand class")
        if finite(flow.get("begin"), "flow begin") != 0 or finite(flow.get("end"), "flow end") != 1500:
            raise ValueError("undeclared demand window")
        result[cls] = int(flow.get("number", "-1"))
    if set(result) != {"M", "R", "U", "X"} or min(result.values()) < 0:
        raise ValueError("incomplete demand plan")
    return result


def read_tripinfo(path: Path) -> dict[str, dict]:
    result: dict[str, dict] = {}
    for _, node in ET.iterparse(path, events=("end",)):
        if node.tag != "tripinfo":
            continue
        vehicle_id = node.get("id", "")
        cls = vehicle_class(vehicle_id)
        if vehicle_id in result:
            raise ValueError("duplicate tripinfo identity")
        result[vehicle_id] = {"class": cls, "depart": finite(node.get("depart"), "depart"),
                              "arrival": finite(node.get("arrival"), "arrival"),
                              "depart_lane": node.get("departLane"),
                              "depart_pos_m": finite(node.get("departPos"), "departPos")}
        node.clear()
    return result


def read_vehroute_ids(path: Path) -> set[str]:
    result: set[str] = set()
    for _, node in ET.iterparse(path, events=("end",)):
        if node.tag != "vehicle":
            continue
        vehicle_id = node.get("id", "")
        vehicle_class(vehicle_id)
        if vehicle_id in result:
            raise ValueError("duplicate vehroute identity")
        result.add(vehicle_id)
        node.clear()
    return result


def read_summary_boundaries(path: Path) -> dict[float, dict[str, int]]:
    wanted = {1499.0: 1500.0, 2699.0: 2700.0}
    result: dict[float, dict[str, int]] = {}
    for _, node in ET.iterparse(path, events=("end",)):
        if node.tag != "step":
            continue
        time_s = finite(node.get("time"), "summary time")
        if time_s in wanted:
            result[wanted[time_s]] = {key: int(node.get(key, "-1")) for key in ("loaded", "inserted", "arrived")}
        node.clear()
    return result


def build_endpoints(plan: dict[str, int], trips: dict[str, dict], routes: set[str], boundaries: dict) -> list[dict]:
    rows: list[dict] = []
    if set(trips) != routes:
        raise ValueError("tripinfo/vehroute identity mismatch")
    for endpoint in (1500.0, 2700.0):
        boundary = boundaries.get(endpoint)
        entered_all = sum(0 <= row["depart"] < endpoint for row in trips.values())
        arrived_all = sum(0 <= row["arrival"] < endpoint for row in trips.values())
        coverage = bool(boundary and boundary["loaded"] == sum(plan.values())
                        and boundary["inserted"] == entered_all and boundary["arrived"] == arrived_all)
        for cls in ("M", "R", "U", "X"):
            entered = sum(row["class"] == cls and 0 <= row["depart"] < endpoint for row in trips.values())
            arrived = sum(row["class"] == cls and 0 <= row["arrival"] < endpoint for row in trips.values())
            rows.append({"class": cls, "endpoint_s": endpoint, "planned": plan[cls],
                         "entered": entered, "arrived": arrived,
                         "outside": plan[cls] - entered, "in_network": entered - arrived,
                         "coverage": coverage})
    return rows


def build_demand_rate_fields(plan: dict[str, int], endpoints: list[dict],
                             demand_duration_s: float, a_window: list[float]) -> tuple[dict, dict]:
    classes = ("M", "R", "U", "X")
    demand_duration = finite(demand_duration_s, "demand duration")
    if demand_duration <= 0 or len(a_window) != 2:
        raise ValueError("invalid demand or A-window duration")
    a_begin, a_end = map(lambda value: finite(value, "A window boundary"), a_window)
    a_duration = a_end - a_begin
    if a_begin != 0.0 or a_end != 1500.0 or a_duration <= 0:
        raise ValueError("realized-entry rate requires the registered A=[0,1500) window")
    if set(plan) != set(classes):
        raise ValueError("planned-demand classes incomplete")
    at_a_end = [row for row in endpoints if finite(row.get("endpoint_s"), "endpoint_s") == a_end]
    by_class = {row.get("class"): row for row in at_a_end}
    if (len(at_a_end) != len(classes) or set(by_class) != set(classes)
            or not all(row.get("coverage") is True for row in at_a_end)):
        raise ValueError("realized-entry rate requires one covered A-endpoint row per class")
    entered = {}
    for cls in classes:
        count = by_class[cls].get("entered")
        if not isinstance(count, int) or isinstance(count, bool) or not 0 <= count <= plan[cls]:
            raise ValueError(f"invalid A-endpoint entered count: {cls}")
        entered[cls] = count
    planned = {cls: plan[cls] * 3600.0 / demand_duration for cls in classes}
    realized = {cls: entered[cls] * 3600.0 / a_duration for cls in classes}
    return planned, realized


def read_r_passage(path: Path, downstream_lanes: set[str], expected_times: set[float],
                   known_lanes: set[str] | None = None) -> dict:
    seen_times: set[float] = set()
    first: dict[str, dict] = {}
    previous: dict[str, tuple[float, str]] = {}
    duplicate_frames = 0
    duplicate_vehicle_identities = 0
    unknown_ids = 0
    unknown_lanes = 0
    for _, step in ET.iterparse(path, events=("end",)):
        if step.tag != "timestep":
            continue
        time_s = finite(step.get("time"), "FCD time")
        if time_s in seen_times:
            duplicate_frames += 1
        seen_times.add(time_s)
        frame_identities: set[str] = set()
        for vehicle in step.findall(".//vehicle"):
            identity = vehicle.get("id", "")
            if identity in frame_identities:
                duplicate_vehicle_identities += 1
                continue
            frame_identities.add(identity)
            try:
                cls = vehicle_class(identity)
            except ValueError:
                unknown_ids += 1
                continue
            lane = vehicle.get("lane", "")
            if known_lanes is not None and lane not in known_lanes:
                unknown_lanes += 1
            if cls == "R" and identity not in first and lane in downstream_lanes:
                prior = previous.get(identity)
                first[identity] = {"vehicle_id": identity, "previous_time_s": prior[0] if prior else None,
                                   "previous_lane": prior[1] if prior else None,
                                   "first_downstream_time_s": time_s, "first_downstream_lane": lane,
                                   "bracketed": bool(prior and math.isclose(time_s - prior[0], 1.0))}
            previous[identity] = (time_s, lane)
        step.clear()
    missing = sorted(expected_times.difference(seen_times))
    extra = sorted(seen_times.difference(expected_times))
    return {"events": list(first.values()), "frame_count": len(seen_times), "missing_frames": missing,
            "extra_frames": extra, "duplicate_frames": duplicate_frames, "unknown_ids": unknown_ids,
            "unknown_lanes": unknown_lanes, "duplicate_vehicle_identities": duplicate_vehicle_identities,
            "coverage_complete": not missing and not extra and duplicate_frames == 0 and unknown_ids == 0
                                 and unknown_lanes == 0 and duplicate_vehicle_identities == 0}


def classify_r_passage(passage: dict, trips: dict[str, dict]) -> dict:
    events_a = [row for row in passage["events"] if row["first_downstream_time_s"] < 1500 and row["bracketed"]]
    unbracketed_a = [row for row in passage["events"] if row["first_downstream_time_s"] < 1500 and not row["bracketed"]]
    arrivals_a = [identity for identity, row in trips.items() if row["class"] == "R" and 0 <= row["arrival"] < 1500]
    event_ids = {row["vehicle_id"] for row in events_a}
    contradiction = sorted(set(arrivals_a).difference(event_ids))
    if not passage["coverage_complete"] or contradiction or unbracketed_a:
        status = "unresolved"
    elif events_a:
        status = "clear_passage"
    else:
        status = "clear_exclusion"
    return {"status": status, "a_bracketed_event_count": len(events_a),
            "a_unbracketed_event_count": len(unbracketed_a),
            "a_arrival_count": len(arrivals_a), "arrival_without_passage_ids": contradiction,
            "denominator_all_observed_r_passage_events": len(passage["events"]),
            "coverage_complete": passage["coverage_complete"]}


def compare_direction(candidate: dict, lower: dict, upper: dict, margin_v: float = 0.0,
                      margin_occ: float = 0.0) -> bool:
    values = [candidate.get("speed_mps"), lower.get("speed_mps"), upper.get("speed_mps")]
    if any(value is None for value in values):
        return False
    return (candidate["speed_mps"] < min(lower["speed_mps"], upper["speed_mps"]) - margin_v
            and candidate["occupancy_percent"] > max(lower["occupancy_percent"], upper["occupancy_percent"]) + margin_occ)


def _bins_by_interval(bins: list[dict]) -> dict[tuple[float, float], dict]:
    return {(row["begin"], row["end"]): row for row in bins}


def evaluate_ejmi(candidate: dict, lower: dict, upper: dict, contract: dict) -> dict:
    if candidate["seed"] != lower["seed"] or candidate["seed"] != upper["seed"]:
        raise ValueError("EJMI references must use the candidate seed")
    if not (lower["q_main"] < candidate["q_main"] < upper["q_main"]):
        raise ValueError("candidate qMain is outside the registered references")
    qualifications = {
        "candidate_technical": bool(candidate.get("technical_qualified")),
        "lower_technical": bool(lower.get("technical_qualified")),
        "upper_technical": bool(upper.get("technical_qualified")),
        "outside_M_1500_zero": candidate.get("outside_M_1500") == 0,
        "single_factor_hash_check": bool(candidate.get("single_factor_hash_check")),
    }
    if not all(qualifications.values()):
        return {"status": "unresolved", "qualification_checks": qualifications,
                "aggregate_checks": {}, "persistence": {"passed": False, "blocks": []}}
    aggregate_checks: dict[str, bool] = {}
    for window in ("A", "B"):
        margin = contract["ejmi"]["margins"][window]
        aggregate_checks[window] = compare_direction(
            candidate["e1"]["aggregates"][window], lower["e1"]["aggregates"][window],
            upper["e1"]["aggregates"][window], margin["delta_v_mps"],
            margin["delta_occ_percentage_points"],
        )
    c30, l30, u30 = map(_bins_by_interval, (
        candidate["e1"]["bins_30s"], lower["e1"]["bins_30s"], upper["e1"]["bins_30s"]
    ))
    c60 = _bins_by_interval(reaggregate_bins(candidate["e1"]["bins_30s"], 300, 1500, 60))
    l60 = _bins_by_interval(reaggregate_bins(lower["e1"]["bins_30s"], 300, 1500, 60))
    u60 = _bins_by_interval(reaggregate_bins(upper["e1"]["bins_30s"], 300, 1500, 60))
    c120 = reaggregate_bins(candidate["e1"]["bins_30s"], 300, 1500, 120)
    l120 = _bins_by_interval(reaggregate_bins(lower["e1"]["bins_30s"], 300, 1500, 120))
    u120 = _bins_by_interval(reaggregate_bins(upper["e1"]["bins_30s"], 300, 1500, 120))
    blocks = []
    for block in c120:
        key120 = (block["begin"], block["end"])
        sub60 = [(block["begin"], block["begin"] + 60), (block["begin"] + 60, block["end"])]
        sub30 = [(start, start + 30) for start in (block["begin"], block["begin"] + 30,
                                                   block["begin"] + 60, block["begin"] + 90)]
        pass120 = compare_direction(block, l120[key120], u120[key120])
        pass60 = [compare_direction(c60[key], l60[key], u60[key]) for key in sub60]
        pass30 = [compare_direction(c30[key], l30[key], u30[key]) for key in sub30]
        passed = pass120 and all(pass60) and sum(pass30) >= 3
        blocks.append({"begin": block["begin"], "end": block["end"], "pass_120": pass120,
                       "pass_60_count": sum(pass60), "pass_30_count": sum(pass30), "passed": passed})
    persistence = {"passed": any(row["passed"] for row in blocks), "blocks": blocks}
    positive = all(aggregate_checks.values()) and persistence["passed"]
    return {"status": "positive" if positive else "not_identified",
            "qualification_checks": qualifications, "aggregate_checks": aggregate_checks,
            "persistence": persistence}


def decide_tier1(manifests: list[dict]) -> dict:
    by_id = {row.get("run_id"): row for row in manifests}
    if set(by_id) != set(TIER1_IDS) or len(manifests) != 2:
        raise ValueError("Tier 1 decision requires exactly the two q3500 manifests")
    if {row.get("seed") for row in manifests} != {17, 23}:
        raise ValueError("Tier 1 seed coverage mismatch")
    expected = {
        "QM3500S17": {"run_id": "QM3500S17", "seed": 17, "q_main": 3500},
        "QM3500S23": {"run_id": "QM3500S23", "seed": 23, "q_main": 3500},
    }
    for run_id in TIER1_IDS:
        _validate_manifest(by_id[run_id], expected[run_id], False)
    r_states = [by_id[run_id]["r_passage"]["status"] for run_id in TIER1_IDS]
    e_states = [by_id[run_id]["ejmi"]["status"] for run_id in TIER1_IDS]
    if any(not by_id[run_id].get("technical_qualified") for run_id in TIER1_IDS) or "unresolved" in r_states + e_states:
        action, result = "stop_unresolved", "unresolved"
    elif r_states == ["clear_passage", "clear_passage"] and e_states == ["positive", "positive"]:
        action, result = "stop_supports_A", "supports_A_within_registered_points"
    elif r_states == ["clear_passage", "clear_passage"] and e_states == ["not_identified", "not_identified"]:
        action, result = "run_q3650", "tier2_upper_selected"
    elif r_states == ["clear_exclusion", "clear_exclusion"] and e_states == ["not_identified", "not_identified"]:
        action, result = "run_q3350", "tier2_lower_selected"
    else:
        action, result = "stop_unresolved", "unresolved"
    selected = list(UPPER_IDS if action == "run_q3650" else LOWER_IDS if action == "run_q3350" else ())
    cancelled = [run_id for run_id in LOWER_IDS + UPPER_IDS if run_id not in selected]
    return {"schema_version": 1, "batch_id": BATCH_ID, "decision_stage": "after_tier1",
            "action": action, "result_status": result, "selected_tier2_runs": selected,
            "cancelled_by_stop_rule": cancelled, "r_states": r_states, "ejmi_states": e_states,
            "additional_qmain_points_prohibited": True}


def decide_final(manifests: list[dict]) -> dict:
    """Apply the registered final Stage 4 matrix to used internal qMain points."""
    by_id = {row.get("run_id"): row for row in manifests}
    if len(by_id) != len(manifests) or not set(by_id).issubset(set(TIER1_IDS + LOWER_IDS + UPPER_IDS)):
        raise ValueError("final decision received duplicate, reference, or unregistered candidate manifests")
    q_groups: defaultdict[int, list[dict]] = defaultdict(list)
    for row in manifests:
        run_id = row["run_id"]
        expected_q = int(run_id[2:6])
        expected_seed = int(run_id[-2:])
        _validate_manifest(row, {"run_id": run_id, "q_main": expected_q, "seed": expected_seed}, False)
        q_groups[expected_q].append(row)
    used_q = sorted(q_groups)
    valid_universe = used_q in ([3500], [3350, 3500], [3500, 3650])
    complete_pairs = all(
        len(rows) == 2 and {row["seed"] for row in rows} == {17, 23}
        for rows in q_groups.values()
    )
    all_qualified = bool(manifests) and all(row.get("technical_qualified") is True for row in manifests)
    if not valid_universe or not complete_pairs or not all_qualified:
        return {"schema_version": 1, "batch_id": BATCH_ID, "action": "unresolved",
                "reason": "used candidate universe, seed pair, or technical qualification is incomplete",
                "used_qmain_points": used_q, "point_states": []}
    point_states = []
    for q_main in used_q:
        rows = sorted(q_groups[q_main], key=lambda row: row["seed"])
        r_states = [row.get("r_passage", {}).get("status") for row in rows]
        e_states = [row.get("ejmi", {}).get("status") for row in rows]
        r_consistent = len(set(r_states)) == 1 and r_states[0] in {"clear_passage", "clear_exclusion"}
        e_consistent = len(set(e_states)) == 1 and e_states[0] in {"positive", "not_identified"}
        point_states.append({"q_main": q_main, "run_ids": [row["run_id"] for row in rows],
                             "r_states": r_states, "ejmi_states": e_states,
                             "r_consistent": r_consistent, "ejmi_consistent": e_consistent})
    if not all(row["r_consistent"] and row["ejmi_consistent"] for row in point_states):
        action, reason = "unresolved", "seed disagreement or unresolved/nonregistered state"
    elif any(row["r_states"][0] == "clear_exclusion" and row["ejmi_states"][0] == "positive"
             for row in point_states):
        action, reason = "unresolved", "same-point EJMI positive and R exclusion contradiction"
    elif any(row["r_states"][0] == "clear_passage" and row["ejmi_states"][0] == "positive"
             for row in point_states):
        action, reason = "supports_A_within_registered_points", "a qualified two-seed internal point has clear passage and positive EJMI"
    elif (len(point_states) >= 2
          and all(row["ejmi_states"][0] == "not_identified" for row in point_states)):
        sequence = [row["r_states"][0] for row in point_states]
        first_exclusion = next((index for index, value in enumerate(sequence) if value == "clear_exclusion"), None)
        b_pattern = (first_exclusion is not None and first_exclusion > 0
                     and all(value == "clear_passage" for value in sequence[:first_exclusion])
                     and all(value == "clear_exclusion" for value in sequence[first_exclusion:]))
        if b_pattern:
            action, reason = "supports_B_pattern_within_registered_points", "qualified q-ordered passage-to-exclusion pattern without positive EJMI"
        else:
            action, reason = "unresolved", "no registered monotone low-q passage to high-q exclusion pattern"
    else:
        action, reason = "unresolved", "no registered discriminating final pattern"
    return {"schema_version": 1, "batch_id": BATCH_ID, "action": action, "reason": reason,
            "used_qmain_points": used_q, "point_states": point_states,
            "interpretation_boundary": "exploratory Stage 4 action; not causal proof, Breakdown, capacity, or thesis evidence"}


def _validate_branch_decision(decision: dict) -> tuple[set[str], set[str]]:
    action = decision.get("action")
    selected = set(decision.get("selected_tier2_runs", []))
    cancelled = set(decision.get("cancelled_by_stop_rule", []))
    allowed = {
        "run_q3350": (set(LOWER_IDS), set(UPPER_IDS), "tier2_lower_selected"),
        "run_q3650": (set(UPPER_IDS), set(LOWER_IDS), "tier2_upper_selected"),
        "stop_supports_A": (set(), set(LOWER_IDS + UPPER_IDS), "supports_A_within_registered_points"),
        "stop_unresolved": (set(), set(LOWER_IDS + UPPER_IDS), "unresolved"),
    }
    if action not in allowed:
        raise ValueError("unregistered Tier-1 action")
    expected_selected, expected_cancelled, expected_result = allowed[action]
    if (selected != expected_selected or cancelled != expected_cancelled
            or decision.get("result_status") != expected_result):
        raise ValueError("Tier-2 branch must be one complete same-q seed pair")
    return selected, cancelled


def _manifest_payload_hash(manifest: dict) -> str:
    encoded = json.dumps(manifest, sort_keys=True, separators=(",", ":"), allow_nan=False).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def _validate_candidate_observations(manifest: dict) -> None:
    run_id = manifest.get("run_id")
    if manifest.get("required_observations_contract_sha256") != REGISTERED_OBSERVATIONS_SHA256:
        raise ValueError(f"candidate complete-observation contract hash changed: {run_id}")
    observations = manifest.get("required_observations")
    if not isinstance(observations, dict):
        raise ValueError(f"candidate complete observations absent: {run_id}")
    if "actual_input_vehph" in observations:
        raise ValueError(f"candidate uses deprecated ambiguous actual_input_vehph field: {run_id}")
    missing = set(REQUIRED_CANDIDATE_OBSERVATION_KEYS).difference(observations)
    if missing:
        raise ValueError(f"candidate complete observations missing {sorted(missing)}: {run_id}")
    for key in ("planned_demand_vehph", "realized_entry_vehph_A"):
        rates = observations.get(key, {})
        if set(rates) != {"M", "R", "U", "X"}:
            raise ValueError(f"candidate {key} denominator incomplete: {run_id}")
        if any(finite(value, key) < 0 for value in rates.values()):
            raise ValueError(f"candidate {key} contains a negative rate: {run_id}")
    if observations.get("q_definition") != REGISTERED_Q_DEFINITION:
        raise ValueError(f"candidate demand/entry-flow definitions changed: {run_id}")
    expected_planned, expected_realized = build_demand_rate_fields(
        manifest.get("planned", {}), manifest.get("endpoints", []),
        REGISTERED_Q_DEFINITION["demand_duration_s"], REGISTERED_WINDOWS["A"])
    if (observations["planned_demand_vehph"] != expected_planned
            or observations["realized_entry_vehph_A"] != expected_realized):
        raise ValueError(f"candidate demand/entry rates differ from plan or A-endpoint accounting: {run_id}")
    downstream = observations.get("downstream_e1", {})
    if (len(downstream.get("bins_30s", [])) != 90
            or set(downstream.get("aggregates", {})) != {"A", "B", "Post", "Full"}):
        raise ValueError(f"candidate downstream E1 observations incomplete: {run_id}")
    for key in ("m_stopped_episodes", "m_stopped_position_range", "m_depart_position_range"):
        if not isinstance(observations.get(key), list):
            raise ValueError(f"candidate observation {key} is not a list: {run_id}")
    propagation = observations.get("r_propagation", {})
    if not isinstance(propagation.get("summary"), dict) or not isinstance(propagation.get("event_sets"), dict):
        raise ValueError(f"candidate R propagation observations incomplete: {run_id}")
    if not isinstance(observations.get("shared_r_u_stopped_exposure"), dict):
        raise ValueError(f"candidate shared R/U exposure absent: {run_id}")
    tls = observations.get("tls_context", {})
    if tls.get("label_count") != 2700:
        raise ValueError(f"candidate TLS observation coverage incomplete: {run_id}")
    audit = observations.get("warning_coverage_audit")
    if not isinstance(audit, dict) or set(audit) != set(REQUIRED_OBSERVATION_AUDIT_KEYS):
        raise ValueError(f"candidate warning/coverage audit incomplete: {run_id}")
    if not all(isinstance(audit[key], dict) and audit[key].get("passed") is True
               for key in REQUIRED_OBSERVATION_AUDIT_KEYS):
        raise ValueError(f"candidate warning/coverage audit failed: {run_id}")
    qualification = observations.get("qualification", {})
    if (qualification.get("passed") is not True
            or qualification.get("required_audit_items") != len(REQUIRED_OBSERVATION_AUDIT_KEYS)
            or qualification.get("passed_audit_items") != len(REQUIRED_OBSERVATION_AUDIT_KEYS)):
        raise ValueError(f"candidate complete-observation qualification failed: {run_id}")


def _validate_manifest(manifest: dict, registered: dict, require_registered_hash: bool,
                       require_complete_observations: bool = False) -> None:
    run_id = registered.get("run_id")
    if manifest.get("run_id") != run_id:
        raise ValueError("manifest run_id differs from ledger")
    if manifest.get("seed") != registered.get("seed"):
        raise ValueError(f"manifest seed differs from ledger: {run_id}")
    if finite(manifest.get("q_main"), "manifest q_main") != finite(registered.get("q_main"), "ledger q_main"):
        raise ValueError(f"manifest qMain differs from ledger: {run_id}")
    endpoints = manifest.get("endpoints")
    if not isinstance(endpoints, list):
        raise ValueError(f"manifest endpoints absent: {run_id}")
    endpoint_keys = [(row.get("class"), finite(row.get("endpoint_s"), "endpoint_s")) for row in endpoints]
    expected = {(cls, endpoint) for endpoint in (1500.0, 2700.0) for cls in ("M", "R", "U", "X")}
    if len(endpoint_keys) != 8 or set(endpoint_keys) != expected or not all(row.get("coverage") is True for row in endpoints):
        raise ValueError(f"manifest requires the unique covered 4-class x 2-endpoint set: {run_id}")
    if not isinstance(manifest.get("technical_qualified"), bool):
        raise ValueError(f"manifest technical qualification is not boolean: {run_id}")
    if require_complete_observations:
        _validate_candidate_observations(manifest)
    expected_hash = registered.get("manifest_payload_sha256")
    if require_registered_hash and not expected_hash:
        raise ValueError(f"manifest payload hash is not registered: {run_id}")
    if expected_hash and expected_hash != _manifest_payload_hash(manifest):
        raise ValueError(f"registered manifest payload hash mismatch: {run_id}")


def build_logical_statuses(ledger: dict, manifests: list[dict], decision: dict) -> dict:
    manifest_by_id = {row.get("run_id"): row for row in manifests}
    if len(manifest_by_id) != len(manifests) or not set(manifest_by_id).issubset(ALL_RUN_IDS):
        raise ValueError("duplicate or unregistered run manifest")
    selected, cancelled = _validate_branch_decision(decision)
    registered_by_id = {row.get("run_id"): row for row in ledger.get("logical_runs", [])}
    if tuple(registered_by_id) != ALL_RUN_IDS or len(registered_by_id) != len(ALL_RUN_IDS):
        raise ValueError("ledger logical-run universe/order changed")
    for run_id, manifest in manifest_by_id.items():
        _validate_manifest(
            manifest,
            registered_by_id[run_id],
            bool(ledger.get("manifest_hash_required")),
            bool(ledger.get("candidate_complete_observations_required")) and run_id not in REFERENCE_IDS,
        )
        if run_id in cancelled:
            raise ValueError(f"manifest supplied for a branch cancelled by the stop rule: {run_id}")
    statuses = []
    for registered in ledger["logical_runs"]:
        run_id = registered["run_id"]
        if run_id in REFERENCE_IDS and run_id not in manifest_by_id:
            state = "reference_manifest_missing"
        elif run_id in REFERENCE_IDS:
            state = "reused_valid" if manifest_by_id[run_id]["technical_qualified"] else "completed_invalid"
        elif run_id in manifest_by_id:
            state = "completed_valid" if manifest_by_id[run_id].get("technical_qualified") else "completed_invalid"
        elif run_id in cancelled:
            state = "cancelled_by_stop_rule"
        elif run_id in selected:
            state = "selected_pending_execution"
        else:
            state = "registered_pending_execution"
        manifest = manifest_by_id.get(run_id)
        evidence_ready = bool(manifest and manifest.get("technical_qualified"))
        included_in_used_design = state in {"reused_valid", "completed_valid"}
        statuses.append({"run_id": run_id, "state": state, "terminal": state in TERMINAL_STATES,
                         "included_in_used_design": included_in_used_design,
                         "used_as_evidence": evidence_ready,
                         "reason": decision.get("action") if state == "cancelled_by_stop_rule" else None})
    used = [row for row in statuses if row["included_in_used_design"]]
    evidence = [row for row in statuses if row["used_as_evidence"]]
    used_q = sorted({next(item["q_main"] for item in ledger["logical_runs"] if item["run_id"] == row["run_id"])
                     for row in used})
    denominator = {
        "registered_logical_runs": len(statuses),
        "registered_terminal_runs": sum(row["terminal"] for row in statuses),
        "used_logical_runs": len(used),
        "used_valid_run_manifests": len(evidence),
        "class_endpoint_units_expected": len(used) * 4 * 2,
        "class_endpoint_units_observed": sum(len(manifest_by_id[row["run_id"]]["endpoints"]) for row in evidence),
        "adjacent_matched_seed_comparisons_expected": max(0, len(used_q) - 1) * 2,
        "used_qmain_points": used_q,
    }
    return {"schema_version": 1, "batch_id": BATCH_ID, "logical_statuses": statuses,
            "denominators": denominator, "all_registered_terminal": all(row["terminal"] for row in statuses)}


def _summary_seed(summary: dict) -> int:
    command = summary.get("sumo_command", [])
    if "--seed" not in command:
        raise ValueError("summary lacks exact SUMO seed argv")
    return int(command[command.index("--seed") + 1])


def _technical_diagnostics(summary: dict) -> tuple[bool, dict]:
    simulation = summary.get("simulation", {})
    diagnostics = simulation.get("log_diagnostics", {})
    checks = {
        "completed_status": summary.get("status") == "completed",
        "technical_expectations": summary.get("technical_expectations_passed") is True,
        "collision_zero": simulation.get("collision_count") == 0,
        "teleport_zero": simulation.get("teleport_count") == 0,
        "emergency_braking_zero": simulation.get("emergency_braking_warning_count") == 0,
        "warnings_zero": diagnostics.get("warning_line_count") == 0,
        "errors_zero": diagnostics.get("error_line_count") == 0,
        "route_errors_zero": diagnostics.get("route_error_line_count") == 0,
    }
    return all(checks.values()), checks


def _m_episode_positions(fcd_path: Path, episodes: list[dict], observations: dict) -> list[dict]:
    selected = [dict(row) for row in episodes
                if row["kind"] == "vehicle_stop" and row["class"] == "M"]
    by_vehicle: defaultdict[str, list[dict]] = defaultdict(list)
    samples: defaultdict[str, defaultdict[str, list[float]]] = defaultdict(lambda: defaultdict(list))
    for row in selected:
        by_vehicle[row["vehicle_id_or_null"]].append(row)
    threshold = observations["stop_definition"]["speed_threshold_mps"]
    for _, step in ET.iterparse(fcd_path, events=("end",)):
        if step.tag != "timestep":
            continue
        time_s = finite(step.get("time"), "FCD time")
        for vehicle in step.findall(".//vehicle"):
            identity = vehicle.get("id", "")
            if not identity.startswith("M_flow.") or finite(vehicle.get("speed"), "FCD speed") > threshold:
                continue
            lane_id = vehicle.get("lane", "")
            pos = finite(vehicle.get("pos"), "FCD position")
            for episode in by_vehicle.get(identity, []):
                if (episode["region"] == observations["lanes"].get(lane_id, {}).get("region")
                        and episode["first_label"] <= time_s <= episode["last_label"]):
                    samples[episode["episode_id"]][lane_id].append(pos)
        step.clear()
    result = []
    for row in selected:
        lane_ranges = []
        for lane_id, values in sorted(samples[row["episode_id"]].items()):
            lane_length = observations["lanes"][lane_id]["length_m"]
            lane_ranges.append({"lane_id": lane_id, "sample_count": len(values),
                                "min_position_m": min(values), "max_position_m": max(values),
                                "min_distance_to_lane_end_m": lane_length - max(values),
                                "max_distance_to_lane_end_m": lane_length - min(values)})
        if sum(item["sample_count"] for item in lane_ranges) != row["sample_count"]:
            raise ValueError("M stopped-episode position denominator mismatch")
        result.append({**row, "lane_position_ranges": lane_ranges})
    return result


def _m_depart_position_ranges(trips: dict[str, dict]) -> list[dict]:
    groups: defaultdict[str, list[float]] = defaultdict(list)
    for row in trips.values():
        if row["class"] == "M":
            groups[row["depart_lane"]].append(row["depart_pos_m"])
    return [{"lane_id": lane, "vehicle_count": len(values), "min_depart_position_m": min(values),
             "max_depart_position_m": max(values)} for lane, values in sorted(groups.items())]


def build_required_observations(run_id: str, resolver: ArchiveResolver, contract: dict,
                                trips: dict[str, dict], plan: dict[str, int], endpoints: list[dict],
                                diagnostic_checks: dict) -> dict:
    observations = contract["required_observations"]
    stage3_contract = {key: observations[key] for key in ("fcd", "lanes", "stop_definition", "windows")}
    fcd_path = resolver.resolve("outputs/fcd.xml")
    fcd = stage3.scan_fcd(fcd_path, stage3_contract)
    tls = stage3.read_tls(resolver.resolve("outputs/tls_states.xml"), observations["tls"]["id"])
    for episode in fcd["episodes"]:
        link_index = 0 if episode["class"] in ("R", "U") else 1 if episode["class"] == "X" else None
        episode["TLS_context"] = stage3.episode_tls_context(episode, tls, link_index)
    downstream = [row for row in observations["e1_detectors"] if row["group"] == "downstream_passage"]
    downstream_rows = []
    for detector in downstream:
        downstream_rows.extend(read_e1(resolver.resolve(detector["output_suffix"]), detector["detector_id"]))
    downstream_ids = {row["detector_id"] for row in downstream}
    downstream_bins = combine_two_lane_e1(downstream_rows, downstream_ids)
    downstream_aggregates = {
        name: aggregate_bins(downstream_bins, *contract["windows"][name])
        for name in ("A", "B", "Post", "Full")
    }
    m_episodes = _m_episode_positions(fcd_path, fcd["episodes"], observations)
    m_position_summary = []
    full_m_episodes = [row for row in m_episodes if row["observation_domain"] == "Full"]
    for lane_id in sorted({item["lane_id"] for row in full_m_episodes for item in row["lane_position_ranges"]}):
        ranges = [item for row in full_m_episodes for item in row["lane_position_ranges"] if item["lane_id"] == lane_id]
        m_position_summary.append({"lane_id": lane_id, "stopped_sample_count": sum(x["sample_count"] for x in ranges),
                                   "min_position_m": min(x["min_position_m"] for x in ranges),
                                   "max_position_m": max(x["max_position_m"] for x in ranges),
                                   "min_distance_to_lane_end_m": min(x["min_distance_to_lane_end_m"] for x in ranges),
                                   "max_distance_to_lane_end_m": max(x["max_distance_to_lane_end_m"] for x in ranges)})
    propagation_rows, propagation_events = stage3.build_propagation(
        run_id, fcd["episodes"], fcd["missing_frames"], stage3_contract)
    full_shared = [row for row in fcd["episodes"] if row["observation_domain"] == "Full"
                   and row["kind"] == "vehicle_stop" and row["region"] == "shared_approach"
                   and row["class"] in {"R", "U"}]
    shared_by_class = {
        cls: {"episode_count": sum(row["class"] == cls for row in full_shared),
              "stopped_vehicle_seconds": sum(row["support_seconds"] for row in full_shared if row["class"] == cls)}
        for cls in ("R", "U")
    }
    expected_tls = {float(value) for value in range(2700)}
    fcd_coverage = (fcd["frame_count"] == 2700 and not fcd["missing_frames"] and not fcd["extra_frames"]
                    and fcd["duplicate_count"] == 0 and fcd["unknown_id_count"] == 0
                    and fcd["unknown_lane_count"] == 0)
    tls_coverage = set(tls) == expected_tls and all(len(state) == 2 for state in tls.values())
    downstream_coverage = len(downstream_bins) == 90
    depart_ranges = _m_depart_position_ranges(trips)
    depart_coverage = sum(row["vehicle_count"] for row in depart_ranges) == sum(
        row["class"] == "M" for row in trips.values())
    planned_demand, realized_entry = build_demand_rate_fields(
        plan, endpoints, observations["q_definition"]["demand_duration_s"], contract["windows"]["A"])
    audit = {
        "fcd": {"passed": fcd_coverage, "frame_count": fcd["frame_count"],
                "missing_frames": len(fcd["missing_frames"]), "extra_frames": len(fcd["extra_frames"]),
                "duplicate_identities": fcd["duplicate_count"], "unknown_ids": fcd["unknown_id_count"],
                "unknown_lanes": fcd["unknown_lane_count"]},
        "downstream_e1": {"passed": downstream_coverage, "combined_30s_bins": len(downstream_bins),
                          "detector_ids": sorted(downstream_ids)},
        "tls": {"passed": tls_coverage, "label_count": len(tls), "states": sorted(set(tls.values()))},
        "entry_accounting": {
            "passed": True,
            "endpoint_s": contract["windows"]["A"][1],
            "entered_by_class": {
                row["class"]: row["entered"] for row in endpoints
                if row["endpoint_s"] == contract["windows"]["A"][1]
            },
        },
        "m_depart_position": {"passed": depart_coverage, "vehicle_count": sum(row["vehicle_count"] for row in depart_ranges)},
        "technical_warnings": {"passed": all(diagnostic_checks.values()), "checks": diagnostic_checks},
        "source_inventory": {"passed": set(EXPECTED_RUNTIME_SUFFIXES).issubset(resolver.inventory_hashes()),
                             "registered_file_count": len(resolver.inventory_hashes())},
    }
    qualified = all(item["passed"] for item in audit.values())
    return {
        "qualification": {"passed": qualified, "required_audit_items": len(audit),
                          "passed_audit_items": sum(item["passed"] for item in audit.values())},
        "planned_demand_vehph": planned_demand,
        "realized_entry_vehph_A": realized_entry,
        "q_definition": observations["q_definition"],
        "downstream_e1": {"bins_30s": downstream_bins, "aggregates": downstream_aggregates},
        "m_stopped_episodes": m_episodes,
        "m_stopped_position_range": m_position_summary,
        "m_depart_position_range": depart_ranges,
        "r_propagation": {"summary": propagation_rows[0], "event_sets": propagation_events},
        "shared_r_u_stopped_exposure": {"by_class": shared_by_class,
                                        "cooccurrence_support_s": len(propagation_events["shared_R_U_cooccurrence_labels_s"]),
                                        "TLS_context_values": propagation_events["TLS_context_values"]},
        "tls_context": {"tls_id": observations["tls"]["id"], "label_count": len(tls),
                        "states": sorted(set(tls.values())),
                        "transition_count": sum(
                            a != b for a, b in zip(
                                [tls[label] for label in sorted(tls)],
                                [tls[label] for label in sorted(tls)][1:],
                            )
                        ),
                        "shared_episode_contexts": sorted({row["TLS_context"] for row in full_shared})},
        "warning_coverage_audit": audit,
    }


def analyze_registered_archive(run: dict, resolver: ArchiveResolver, contract: dict,
                               lower: dict | None = None, upper: dict | None = None) -> dict:
    validate_additional_semantics(
        resolver.resolve("scenario.add.xml"), contract["required_observations"], runtime=True)
    validate_compiled_topology(
        resolver.resolve("network.net.xml"), contract["required_observations"])
    summary = load_json(resolver.resolve("summary.json"))
    if summary.get("sumo_version") != contract["versions"]["sumo"] or summary.get("netconvert_version") != contract["versions"]["netconvert"]:
        raise ValueError("archived simulator version differs from contract")
    seed = _summary_seed(summary)
    requested = summary.get("input_validation", {}).get("requested_demand_vehph", {})
    if seed != run["seed"] or finite(requested.get("M"), "requested M") != run["q_main"]:
        raise ValueError("registered seed/qMain differs from archived summary")
    if {key: finite(requested.get(key), key) for key in ("R", "U", "X")} != {"R": 720.0, "U": 360.0, "X": 180.0}:
        raise ValueError("a fixed non-qMain demand changed")
    windows = summary.get("time_windows", {})
    expected_windows = {"warmup": (0, 0), "demand": (0, 1500), "measurement": (0, 1500),
                        "clearance": (1500, 2700), "simulation": (0, 2700)}
    for name, (begin, end) in expected_windows.items():
        if windows.get(name, {}).get("begin_s") != begin or windows.get(name, {}).get("end_s") != end:
            raise ValueError("archived time windows changed")
    rows = []
    for detector_id, suffix in zip(contract["e1"]["internal_detector_ids"], contract["e1"]["internal_output_suffixes"]):
        rows.extend(read_e1(resolver.resolve(suffix), detector_id))
    bins = combine_two_lane_e1(rows, set(contract["e1"]["internal_detector_ids"]))
    aggregates = {name: aggregate_bins(bins, *contract["windows"][name]) for name in ("A", "B")}
    plan = read_plan(resolver.resolve("demand.rou.xml"))
    expected_plan = {"M": contract["planned_M_counts"][str(int(run["q_main"]))], "R": 300, "U": 150, "X": 75}
    if plan != expected_plan:
        raise ValueError(f"generated demand counts changed: {plan} != {expected_plan}")
    input_validation = summary.get("input_validation", {})
    if input_validation.get("planned_counts") != plan or input_validation.get("insertion_settings") != {
        "departPos": "last", "departLane": "best", "departSpeed": "max"
    }:
        raise ValueError("summary demand/insertion validation changed")
    trips = read_tripinfo(resolver.resolve("outputs/tripinfo.xml"))
    routes = read_vehroute_ids(resolver.resolve("outputs/vehroute.xml"))
    endpoints = build_endpoints(plan, trips, routes, read_summary_boundaries(resolver.resolve("outputs/sumo_summary.xml")))
    expected_times = {float(value) for value in range(2700)}
    passage = read_r_passage(resolver.resolve("outputs/fcd.xml"), set(contract["r_passage"]["downstream_lanes"]),
                             expected_times, set(contract["r_passage"]["known_lane_ids"]))
    r_classification = classify_r_passage(passage, trips)
    diagnostic_ok, diagnostic_checks = _technical_diagnostics(summary)
    endpoint_ok = all(row["coverage"] and row["outside"] >= 0 and row["in_network"] >= 0 for row in endpoints)
    m1500 = next(row for row in endpoints if row["class"] == "M" and row["endpoint_s"] == 1500)
    fixed_hash_ok = all(resolver.inventory_hashes().get(suffix) == expected for suffix, expected in contract["fixed_runtime_hashes"].items())
    required_observations = build_required_observations(
        run["run_id"], resolver, contract, trips, plan, endpoints, diagnostic_checks)
    observation_ok = required_observations["qualification"]["passed"]
    manifest = {
        "schema_version": 1, "batch_id": BATCH_ID, "run_id": run["run_id"], "role": run["role"],
        "seed": seed, "q_main": run["q_main"], "q_ramp": 720.0, "q_urban": 360.0, "q_x": 180.0,
        "planned": plan, "endpoints": endpoints, "outside_M_1500": m1500["outside"],
        "e1": {"bins_30s": bins, "aggregates": aggregates}, "r_passage": r_classification,
        "diagnostic_checks": diagnostic_checks, "single_factor_hash_check": fixed_hash_ok,
        "required_observations_contract_sha256": REGISTERED_OBSERVATIONS_SHA256,
        "required_observations": required_observations,
        "technical_qualified": bool(diagnostic_ok and endpoint_ok and passage["coverage_complete"] and fixed_hash_ok and observation_ok
                                    and r_classification["status"] != "unresolved"),
        "source_inventory_hashes": resolver.inventory_hashes(),
        "interpretation_boundary": "exploratory local signature; not Breakdown, Capacity Drop, capacity, or thesis evidence",
    }
    manifest["ejmi"] = ({"status": "not_applicable_reference"} if run["role"].endswith("reference")
                         else evaluate_ejmi(manifest, lower, upper, contract) if lower and upper
                         else {"status": "unresolved", "reason": "candidate references absent"})
    manifest["ejmi_reference_registration"] = (
        None if run["role"].endswith("reference") else contract["ejmi_reference_map"][run["run_id"]])
    return manifest


def run_record(registry: dict, run_id: str) -> dict:
    found = [row for row in registry["runs"] if row["run_id"] == run_id]
    if len(found) != 1:
        raise ValueError("run must occur exactly once in registry")
    return found[0]


def _allowed_manifest_adapter_hashes(ledger: dict) -> set[str]:
    """Return current plus explicitly reviewed historical analysis adapters."""

    current = digest(Path(__file__))
    history = ledger.get("candidate_manifest_adapter_compatibility", [])
    if not isinstance(history, list):
        raise ValueError("candidate manifest adapter compatibility is invalid")
    allowed = {current}
    for item in history:
        if (
            not isinstance(item, dict)
            or not re.fullmatch(r"[0-9a-f]{64}", str(item.get("adapter_sha256", "")))
            or item.get("review_status") != "passed"
            or item.get("open_findings") != 0
        ):
            raise ValueError("historical candidate manifest adapter lacks passed review")
        allowed.add(item["adapter_sha256"])
    return allowed


def _registered_runtime_registry_hashes(ledger: dict) -> set[str]:
    """Verify and return current and immutable historical overlay hashes."""

    binding = ledger.get("runtime_source_registry_overlay", {})
    current = _registered_project_file(binding.get("path"), "ledger runtime overlay path")
    if digest(current) != binding.get("sha256"):
        raise ValueError("runtime registry hash differs from final ledger binding")
    hashes = {binding["sha256"]}
    history = ledger.get("runtime_source_registry_history", [])
    if not isinstance(history, list):
        raise ValueError("runtime source registry history is invalid")
    for item in history:
        if not isinstance(item, dict) or item.get("status") != "immutable_snapshot":
            raise ValueError("runtime source registry history entry is invalid")
        snapshot = _registered_project_file(
            item.get("path"), "historical runtime overlay snapshot path"
        )
        if digest(snapshot) != item.get("sha256"):
            raise ValueError("historical runtime overlay snapshot hash mismatch")
        hashes.add(item["sha256"])
    return hashes


def _validate_tier2_branch_decision_content(decision: dict) -> None:
    expected = {
        "schema_version": 1,
        "batch_id": BATCH_ID,
        "decision_stage": "after_tier1",
        "action": "run_q3650",
        "result_status": "tier2_upper_selected",
        "selected_tier2_runs": list(UPPER_IDS),
        "cancelled_by_stop_rule": list(LOWER_IDS),
        "r_states": ["clear_passage", "clear_passage"],
        "ejmi_states": ["not_identified", "not_identified"],
        "additional_qmain_points_prohibited": True,
    }
    if decision != expected:
        raise ValueError("scientific Tier-1 decision is not the exact run_q3650 branch")


def validate_scientific_tier1_review_receipt(
    receipt_path: Path,
    decision_path: Path,
    ledger: dict,
) -> dict:
    """Validate the explicit scientific-review relay without inventing an artifact."""

    expected_receipt_path = (ROOT / TIER1_SCIENTIFIC_REVIEW_RECEIPT_RELATIVE_PATH).resolve()
    resolved_receipt = Path(receipt_path).resolve(strict=True)
    if resolved_receipt != expected_receipt_path:
        raise ValueError("scientific review receipt path is not the fixed batch path")
    expected_decision_path = (ROOT / TIER1_SCIENTIFIC_DECISION_RELATIVE_PATH).resolve()
    resolved_decision = Path(decision_path).resolve(strict=True)
    if resolved_decision != expected_decision_path:
        raise ValueError("engineering decision output cannot substitute for scientific decision")
    decision = load_json(resolved_decision)
    _validate_tier2_branch_decision_content(decision)
    binding = ledger.get("tier1_candidate_manifest_receipt_registry_snapshot", {})
    snapshot = _registered_project_file(
        binding.get("path"), "Tier-1 candidate manifest receipt registry snapshot"
    )
    if digest(snapshot) != binding.get("sha256"):
        raise ValueError("Tier-1 candidate manifest receipt registry snapshot hash mismatch")
    receipt = load_json(resolved_receipt)
    expected = {
        "schema_version": 1,
        "batch_id": BATCH_ID,
        "reviewer_role": "scientific_reviewer",
        "review_status": "passed",
        "open_findings": 0,
        "review_evidence_kind": "parent_delegated_fact_without_standalone_artifact",
        "review_fact_relay": SCIENTIFIC_BRANCH_REVIEW_RELAY,
        "standalone_scientific_review_artifact_sha256": None,
        "decision_path": TIER1_SCIENTIFIC_DECISION_RELATIVE_PATH,
        "decision_sha256": digest(resolved_decision),
        "decision_action": "run_q3650",
        "selected_tier2_runs": list(UPPER_IDS),
        "cancelled_by_stop_rule": list(LOWER_IDS),
        "registration_payload_sha256": ledger["input_hashes"]["registration_payload_sha256"],
        "measurement_contract_sha256": ledger["input_hashes"]["contract_sha256"],
        "approved_source_registry_sha256": ledger["input_hashes"]["source_registry_sha256"],
        "tier1_manifest_receipt_registry_path": binding.get("path"),
        "tier1_manifest_receipt_registry_sha256": binding.get("sha256"),
    }
    if receipt != expected:
        raise ValueError("scientific Tier-1 review receipt is incomplete or drifted")
    return decision


def validate_tier2_branch_gate(ledger: dict, approved_registry: dict) -> dict:
    """Validate the reviewed upper-branch plan and exact logical-run states."""

    binding = ledger.get("tier2_branch_gate", {})
    gate_path = _registered_project_file(binding.get("path"), "Tier-2 branch gate path")
    expected_path = (ROOT / TIER2_BRANCH_GATE_RELATIVE_PATH).resolve()
    if gate_path != expected_path or digest(gate_path) != binding.get("sha256"):
        raise ValueError("Tier-2 branch gate path or hash mismatch")
    gate = load_json(gate_path)
    review_path = ROOT / TIER1_SCIENTIFIC_REVIEW_RECEIPT_RELATIVE_PATH
    decision_path = ROOT / TIER1_SCIENTIFIC_DECISION_RELATIVE_PATH
    validate_scientific_tier1_review_receipt(review_path, decision_path, ledger)
    receipt_binding = ledger.get("tier1_candidate_manifest_receipt_registry_snapshot", {})
    selected_contracts = [
        {
            "run_id": run_id,
            "seed": run_record(approved_registry, run_id)["seed"],
            "q_main": run_record(approved_registry, run_id)["q_main"],
            "exact_runner_command_argv": run_record(approved_registry, run_id)[
                "exact_runner_command_argv"
            ],
        }
        for run_id in UPPER_IDS
    ]
    expected = {
        "schema_version": 1,
        "batch_id": BATCH_ID,
        "status": "scientifically_reviewed_upper_pair_selected",
        "authorization_quote": T43_AUTHORIZATION_QUOTE,
        "registration_payload_sha256": ledger["input_hashes"]["registration_payload_sha256"],
        "measurement_contract_sha256": ledger["input_hashes"]["contract_sha256"],
        "approved_source_registry_sha256": ledger["input_hashes"]["source_registry_sha256"],
        "tier1_manifest_receipt_registry_path": receipt_binding.get("path"),
        "tier1_manifest_receipt_registry_sha256": receipt_binding.get("sha256"),
        "scientific_review_receipt_path": TIER1_SCIENTIFIC_REVIEW_RECEIPT_RELATIVE_PATH,
        "scientific_review_receipt_sha256": digest(review_path),
        "scientific_decision_path": TIER1_SCIENTIFIC_DECISION_RELATIVE_PATH,
        "scientific_decision_sha256": digest(decision_path),
        "action": "run_q3650",
        "selected_run_ids": list(UPPER_IDS),
        "selected_seed_pair": [17, 23],
        "selected_q_main": 3650,
        "selected_run_contracts": selected_contracts,
        "cancelled_run_ids": list(LOWER_IDS),
        "additional_qmain_points_or_seeds_prohibited": True,
        "adapter_sha256_at_registration": gate.get("adapter_sha256_at_registration"),
        "actual_execution_counters_at_registration": {
            "actual_sumo_starts": 2,
            "actual_netconvert_operations": 2,
            "actual_traci_connections": 0,
            "actual_gui_starts": 0,
        },
    }
    if (
        gate != expected
        or not re.fullmatch(
            r"[0-9a-f]{64}", str(gate.get("adapter_sha256_at_registration", ""))
        )
    ):
        raise ValueError("Tier-2 branch gate content is incomplete or drifted")
    registry_by_id = {row["run_id"]: row for row in approved_registry.get("runs", [])}
    ledger_by_id = {row["run_id"]: row for row in ledger.get("logical_runs", [])}
    if set(registry_by_id) != set(ALL_RUN_IDS) or set(ledger_by_id) != set(ALL_RUN_IDS):
        raise ValueError("Tier-2 gate run universe changed")
    for run_id in LOWER_IDS:
        row = ledger_by_id[run_id]
        if row.get("state") != "cancelled_by_stop_rule" or row.get("terminal") is not True:
            raise ValueError("all q3350 runs must be cancelled by the reviewed branch")
        if row.get("attempt_ids") or row.get("actual_sumo_starts") != 0:
            raise ValueError("cancelled q3350 runs cannot contain attempts")
    for run_id in UPPER_IDS:
        row = ledger_by_id[run_id]
        if row.get("state") not in {"selected_pending_execution", "completed_valid"}:
            raise ValueError("selected q3650 pair has an invalid state")
        if row.get("seed") != registry_by_id[run_id].get("seed") or row.get("q_main") != 3650:
            raise ValueError("selected q3650 pair identity changed")
    return gate


def register_tier2_plan(
    ledger_path: Path,
    contract_path: Path,
    approved_registry_path: Path,
    manifest_registry_path: Path,
    decision_path: Path,
    scientific_review_receipt_path: Path,
    gate_path: Path,
) -> dict:
    """Register the reviewed q3650 pair without creating an execution attempt."""

    ledger_path = Path(ledger_path).resolve(strict=True)
    starting_hash = digest(ledger_path)
    ledger, _, approved_registry = validate_context(
        ledger_path, Path(contract_path), Path(approved_registry_path)
    )
    if ledger.get("t43_launch_authorization", {}).get("quote") != T43_AUTHORIZATION_QUOTE:
        raise ValueError("Tier-2 plan requires the exact T43 authorization")
    if any(ledger.get(key) != value for key, value in {
        "actual_sumo_starts": 2,
        "actual_netconvert_operations": 2,
        "actual_traci_connections": 0,
        "actual_gui_starts": 0,
    }.items()):
        raise ValueError("Tier-2 plan registration requires unchanged Tier-1 counters")
    tier1_paths = []
    receipt_registry = load_json(Path(manifest_registry_path))
    tier1_snapshot_binding = ledger.get(
        "tier1_candidate_manifest_receipt_registry_snapshot", {}
    )
    tier1_snapshot = _registered_project_file(
        tier1_snapshot_binding.get("path"),
        "Tier-1 candidate manifest receipt registry snapshot",
    )
    if (
        digest(tier1_snapshot) != tier1_snapshot_binding.get("sha256")
        or digest(Path(manifest_registry_path)) != tier1_snapshot_binding.get("sha256")
        or load_json(tier1_snapshot) != receipt_registry
    ):
        raise ValueError("Tier-2 plan requires the frozen Tier-1 receipt registry")
    for run_id in TIER1_IDS:
        entries = [row for row in receipt_registry.get("receipts", []) if row.get("run_id") == run_id]
        if len(entries) != 1:
            raise ValueError("Tier-2 plan requires receipt-bound Tier-1 pair")
        tier1_paths.append(ROOT / entries[0]["manifest_path"])
    receipt_bound_ledger, manifests = validate_candidate_manifest_receipt_registry(
        Path(manifest_registry_path), ledger, Path(contract_path),
        Path(approved_registry_path), tier1_paths,
    )
    validate_candidate_decision_inputs(receipt_bound_ledger, manifests)
    computed = decide_tier1(manifests)
    supplied_decision = load_json(Path(decision_path))
    if supplied_decision != computed:
        raise ValueError("scientific Tier-1 decision differs from receipt-bound manifests")
    validate_scientific_tier1_review_receipt(
        scientific_review_receipt_path, decision_path, ledger
    )
    expected_gate_path = (ROOT / TIER2_BRANCH_GATE_RELATIVE_PATH).resolve()
    if Path(gate_path).resolve() != expected_gate_path:
        raise ValueError("Tier-2 branch gate path is not the fixed batch path")
    if expected_gate_path.exists() or ledger.get("tier2_branch_gate") is not None:
        raise FileExistsError("Tier-2 branch plan is already registered")
    receipt_binding = ledger["tier1_candidate_manifest_receipt_registry_snapshot"]
    selected_contracts = [
        {
            "run_id": run_id,
            "seed": run_record(approved_registry, run_id)["seed"],
            "q_main": run_record(approved_registry, run_id)["q_main"],
            "exact_runner_command_argv": run_record(approved_registry, run_id)[
                "exact_runner_command_argv"
            ],
        }
        for run_id in UPPER_IDS
    ]
    gate = {
        "schema_version": 1,
        "batch_id": BATCH_ID,
        "status": "scientifically_reviewed_upper_pair_selected",
        "authorization_quote": T43_AUTHORIZATION_QUOTE,
        "registration_payload_sha256": ledger["input_hashes"]["registration_payload_sha256"],
        "measurement_contract_sha256": ledger["input_hashes"]["contract_sha256"],
        "approved_source_registry_sha256": ledger["input_hashes"]["source_registry_sha256"],
        "tier1_manifest_receipt_registry_path": receipt_binding["path"],
        "tier1_manifest_receipt_registry_sha256": receipt_binding["sha256"],
        "scientific_review_receipt_path": TIER1_SCIENTIFIC_REVIEW_RECEIPT_RELATIVE_PATH,
        "scientific_review_receipt_sha256": digest(Path(scientific_review_receipt_path)),
        "scientific_decision_path": TIER1_SCIENTIFIC_DECISION_RELATIVE_PATH,
        "scientific_decision_sha256": digest(Path(decision_path)),
        "action": "run_q3650",
        "selected_run_ids": list(UPPER_IDS),
        "selected_seed_pair": [17, 23],
        "selected_q_main": 3650,
        "selected_run_contracts": selected_contracts,
        "cancelled_run_ids": list(LOWER_IDS),
        "additional_qmain_points_or_seeds_prohibited": True,
        "adapter_sha256_at_registration": digest(Path(__file__)),
        "actual_execution_counters_at_registration": {
            "actual_sumo_starts": 2,
            "actual_netconvert_operations": 2,
            "actual_traci_connections": 0,
            "actual_gui_starts": 0,
        },
    }
    write_json_atomic(expected_gate_path, gate, must_not_exist=True)
    if digest(ledger_path) != starting_hash:
        raise RuntimeError("ledger changed during Tier-2 plan registration")
    rows = {row["run_id"]: row for row in ledger["logical_runs"]}
    for run_id in LOWER_IDS:
        rows[run_id]["state"] = "cancelled_by_stop_rule"
        rows[run_id]["terminal"] = True
    for run_id in UPPER_IDS:
        rows[run_id]["state"] = "selected_pending_execution"
        rows[run_id]["terminal"] = False
    ledger["tier2_branch_gate"] = {
        "path": TIER2_BRANCH_GATE_RELATIVE_PATH,
        "sha256": digest(expected_gate_path),
        "status": "q3650_pair_selected_pending_execution",
    }
    ledger["status"] = "t43_tier2_q3650_pair_selected_pending_execution"
    write_json_atomic(ledger_path, ledger)
    validate_tier2_branch_gate(ledger, approved_registry)
    return gate


def _registered_project_file(relative_path: object, field: str) -> Path:
    """Resolve a registry path without permitting absolute or escaping paths."""

    if not isinstance(relative_path, str) or not relative_path:
        raise ValueError(f"{field} must be a nonempty project-relative path")
    candidate = Path(relative_path)
    if candidate.is_absolute():
        raise ValueError(f"{field} must be project-relative")
    resolved = (ROOT / candidate).resolve()
    if not _is_under(resolved, ROOT) or not resolved.is_file():
        raise ValueError(f"{field} is missing or escapes project")
    return resolved


def validate_runtime_source_registry(
    runtime_registry_path: Path,
    ledger: dict,
    approved_registry: dict,
    run_id: str,
) -> tuple[dict, Path]:
    """Resolve one completed Tier-1 source through the ledger-bound overlay.

    The approved source registry remains immutable.  This overlay may only add
    execution facts for a candidate whose approved source fields were null.
    """

    runtime_registry_path = Path(runtime_registry_path).resolve(strict=True)
    if not _is_under(runtime_registry_path, ROOT):
        raise ValueError("runtime registry must remain inside project")
    binding = ledger.get("runtime_source_registry_overlay", {})
    registered_overlay = _registered_project_file(
        binding.get("path"), "ledger runtime overlay path"
    )
    if runtime_registry_path != registered_overlay:
        raise ValueError("runtime registry path differs from final ledger binding")
    if binding.get("sha256") != digest(runtime_registry_path):
        raise ValueError("runtime registry hash differs from final ledger binding")

    overlay = load_json(runtime_registry_path)
    approved_registry_path = ROOT / (
        "data/processed/stage4_qmain_sequential_20260912_v1/source_registry.json"
    )
    approved_registry_hash = digest(approved_registry_path)
    if (
        overlay.get("batch_id") != BATCH_ID
        or overlay.get("approved_source_registry_path")
        != approved_registry_path.relative_to(ROOT).as_posix()
        or overlay.get("approved_source_registry_sha256") != approved_registry_hash
        or ledger.get("t43_launch_authorization", {}).get(
            "approved_source_registry_sha256"
        )
        != approved_registry_hash
        or ledger.get("input_hashes", {}).get("source_registry_sha256")
        != approved_registry_hash
        or overlay.get("registration_payload_sha256")
        != ledger.get("input_hashes", {}).get("registration_payload_sha256")
    ):
        raise ValueError("runtime registry approved-registry or payload binding mismatch")

    rows = overlay.get("runs")
    if not isinstance(rows, list) or not rows:
        raise ValueError("runtime registry contains no completed candidate facts")
    overlay_ids = [row.get("run_id") for row in rows if isinstance(row, dict)]
    if len(overlay_ids) != len(rows) or len(overlay_ids) != len(set(overlay_ids)):
        raise ValueError("runtime registry run identities are missing or duplicated")
    if any(candidate not in TIER1_IDS + UPPER_IDS for candidate in overlay_ids):
        raise ValueError(
            "runtime registry may contain Tier-1 and reviewed upper-branch candidates only"
        )
    if any(candidate in UPPER_IDS for candidate in overlay_ids) or run_id in UPPER_IDS:
        validate_tier2_branch_gate(ledger, approved_registry)
    if run_id not in TIER1_IDS + UPPER_IDS:
        raise ValueError("runtime registry cannot override references or cancelled runs")

    # Every overlay row must already correspond to one completed ledger attempt.
    # This prevents a valid requested Tier-1 row from masking an injected Tier-2
    # row that has no actual post-launch identity yet.
    ledger_rows = {item.get("run_id"): item for item in ledger.get("logical_runs", [])}
    for overlay_row in rows:
        overlay_id = overlay_row["run_id"]
        approved_row = run_record(approved_registry, overlay_id)
        ledger_row = ledger_rows.get(overlay_id)
        matching_attempts = [
            item for item in ledger.get("attempts", [])
            if item.get("attempt_id") == overlay_row.get("attempt_id")
        ]
        if (
            ledger_row is None
            or ledger_row.get("state") != "completed_valid"
            or ledger_row.get("terminal") is not True
            or ledger_row.get("actual_sumo_starts") != 1
            or ledger_row.get("attempt_ids") != [overlay_row.get("attempt_id")]
            or len(matching_attempts) != 1
            or matching_attempts[0].get("run_id") != overlay_id
            or matching_attempts[0].get("seed") != approved_row.get("seed")
            or matching_attempts[0].get("q_main") != approved_row.get("q_main")
            or matching_attempts[0].get("status") != "archived_technical_valid"
            or matching_attempts[0].get("technical_qualified") is not True
        ):
            raise ValueError("runtime registry contains a candidate without a completed authorized attempt")

    approved = run_record(approved_registry, run_id)
    if approved.get("source_map_path") is not None or approved.get("source_map_sha256") is not None:
        raise ValueError("runtime registry cannot override an approved source binding")
    row = next((item for item in rows if item["run_id"] == run_id), None)
    if row is None:
        raise ValueError("requested run is absent from the ledger-bound runtime registry")

    ledger_run = next(
        (item for item in ledger.get("logical_runs", []) if item.get("run_id") == run_id),
        None,
    )
    attempts = [
        item
        for item in ledger.get("attempts", [])
        if item.get("attempt_id") == row.get("attempt_id")
    ]
    if ledger_run is None or len(attempts) != 1:
        raise ValueError("runtime registry attempt is absent or duplicated in ledger")
    attempt = attempts[0]
    identity = ("run_id", "seed", "q_main")
    if any(ledger_run.get(key) != approved.get(key) for key in identity):
        raise ValueError("ledger candidate identity differs from approved registry")
    if (
        ledger_run.get("role") != approved.get("role")
        or ledger_run.get("state") != "completed_valid"
        or ledger_run.get("terminal") is not True
        or ledger_run.get("actual_sumo_starts") != 1
        or ledger_run.get("attempt_ids") != [row.get("attempt_id")]
        or attempt.get("run_id") != run_id
        or attempt.get("seed") != approved.get("seed")
        or attempt.get("q_main") != approved.get("q_main")
        or attempt.get("status") != "archived_technical_valid"
        or attempt.get("technical_qualified") is not True
        or attempt.get("actual_sumo_starts") != 1
        or attempt.get("actual_netconvert_operations") != 1
        or attempt.get("actual_traci_connections") != 0
        or attempt.get("actual_gui_starts") != 0
        or attempt.get("exact_runner_command_argv")
        != approved.get("exact_runner_command_argv")
    ):
        raise ValueError("runtime registry candidate is not a completed authorized attempt")

    exact_overlay_attempt = {
        "source_map_path": attempt.get("source_map_path"),
        "source_map_sha256": attempt.get("source_map_sha256"),
        "archive_runtime_path": attempt.get("archive_runtime_path"),
        "engineering_verification_path": attempt.get("engineering_verification_path"),
        "engineering_verification_sha256": attempt.get("engineering_verification_sha256"),
        "summary_sha256": attempt.get("summary_sha256"),
        "technical_qualified": attempt.get("technical_qualified"),
        "archive_file_count": attempt.get("archive_file_count"),
    }
    if any(row.get(key) != value for key, value in exact_overlay_attempt.items()):
        raise ValueError("runtime registry facts differ from the final ledger attempt")

    source_map_path = _registered_project_file(
        row.get("source_map_path"), "runtime source-map path"
    )
    if digest(source_map_path) != row.get("source_map_sha256"):
        raise ValueError("runtime source-map hash mismatch")
    source_map = load_json(source_map_path)
    if (
        source_map.get("batch_id") != BATCH_ID
        or source_map.get("logical_run_id") != run_id
        or source_map.get("attempt_id") != row.get("attempt_id")
        or source_map.get("archive_status") != "complete"
        or source_map.get("archive_runtime_relative_path")
        != row.get("archive_runtime_path")
        or source_map.get("source_file_count") != len(EXPECTED_RUNTIME_SUFFIXES)
        or source_map.get("archive_file_count") != len(EXPECTED_RUNTIME_SUFFIXES)
        or source_map.get("source_hashes_stable_during_copy") is not True
        or source_map.get("summary_present") is not True
        or len(source_map.get("file_map", [])) != len(EXPECTED_RUNTIME_SUFFIXES)
    ):
        raise ValueError("runtime source-map identity or 29-file archive contract mismatch")
    resolver = ArchiveResolver(source_map_path)
    if set(resolver.inventory_hashes()) != set(EXPECTED_RUNTIME_SUFFIXES):
        raise ValueError("runtime source-map must contain exactly 29 registered files")

    summary_path = resolver.resolve("summary.json")
    if digest(summary_path) != row.get("summary_sha256"):
        raise ValueError("runtime summary hash mismatch")
    summary = load_json(summary_path)
    requested = summary.get("input_validation", {}).get("requested_demand_vehph", {})
    expected_windows = {
        "warmup": (0, 0),
        "demand": (0, 1500),
        "measurement": (0, 1500),
        "clearance": (1500, 2700),
        "simulation": (0, 2700),
    }
    if (
        summary.get("status") != "completed"
        or summary.get("technical_expectations_passed") is not True
        or _summary_seed(summary) != approved.get("seed")
        or finite(requested.get("M"), "runtime requested M")
        != approved.get("q_main")
        or {key: finite(requested.get(key), key) for key in ("R", "U", "X")}
        != {"R": 720.0, "U": 360.0, "X": 180.0}
        or any(
            summary.get("time_windows", {}).get(name, {}).get("begin_s") != begin
            or summary.get("time_windows", {}).get(name, {}).get("end_s") != end
            for name, (begin, end) in expected_windows.items()
        )
    ):
        raise ValueError("runtime summary identity, demand, status, or windows mismatch")

    receipt_path = _registered_project_file(
        row.get("engineering_verification_path"),
        "runtime engineering-verification path",
    )
    if digest(receipt_path) != row.get("engineering_verification_sha256"):
        raise ValueError("runtime engineering-verification hash mismatch")
    receipt = load_json(receipt_path)
    runtime_identity = receipt.get("runtime_identity", {})
    if (
        receipt.get("batch_id") != BATCH_ID
        or receipt.get("run_id") != run_id
        or receipt.get("attempt_id") != row.get("attempt_id")
        or receipt.get("source_map_path") != row.get("source_map_path")
        or receipt.get("source_map_sha256") != row.get("source_map_sha256")
        or receipt.get("archive_runtime_path") != row.get("archive_runtime_path")
        or receipt.get("archive_file_count") != len(EXPECTED_RUNTIME_SUFFIXES)
        or receipt.get("summary_sha256") != row.get("summary_sha256")
        or receipt.get("technical_qualified") is not True
        or receipt.get("required_observation_audit", {}).get("passed") is not True
        or runtime_identity.get("seed") != approved.get("seed")
        or runtime_identity.get("q_main") != approved.get("q_main")
        or runtime_identity.get("q_ramp") != 720.0
        or runtime_identity.get("q_urban") != 360.0
        or runtime_identity.get("q_x") != 180.0
    ):
        raise ValueError("runtime engineering receipt identity or qualification mismatch")
    return row, source_map_path


def _manifest_file(path: Path) -> tuple[Path, str]:
    resolved = Path(path).resolve(strict=True)
    if not _is_under(resolved, ROOT) or not resolved.is_file():
        raise ValueError("candidate manifest must be a regular project file")
    return resolved, resolved.relative_to(ROOT).as_posix()


def _validate_candidate_manifest_provenance(
    manifest_path: Path,
    run: dict,
    overlay_run: dict,
    contract_path: Path,
) -> tuple[dict, str, str]:
    resolved, relative = _manifest_file(manifest_path)
    manifest = load_json(resolved)
    _validate_manifest(manifest, run, False, True)
    file_hash = digest(resolved)
    manifest_payload_sha256 = _manifest_payload_hash(manifest)
    if (
        manifest.get("source_map_path") != overlay_run.get("source_map_path")
        or manifest.get("source_map_sha256") != overlay_run.get("source_map_sha256")
        or manifest.get("contract_sha256") != digest(contract_path)
        or manifest.get("adapter_sha256") != digest(Path(__file__))
        or manifest.get("technical_qualified") is not True
        or manifest.get("required_observations", {})
        .get("qualification", {})
        .get("passed")
        is not True
        or manifest.get("required_observations", {})
        .get("qualification", {})
        .get("passed_audit_items")
        != len(REQUIRED_OBSERVATION_AUDIT_KEYS)
        or manifest.get("required_observations", {})
        .get("qualification", {})
        .get("required_audit_items")
        != len(REQUIRED_OBSERVATION_AUDIT_KEYS)
    ):
        raise ValueError("candidate manifest provenance or 7/7 qualification mismatch")
    return manifest, file_hash, manifest_payload_sha256


def register_candidate_manifest(
    ledger_path: Path,
    contract_path: Path,
    approved_registry_path: Path,
    runtime_registry_path: Path,
    manifest_registry_path: Path,
    run_id: str,
    manifest_path: Path,
) -> dict:
    """Append one verified, executed candidate manifest receipt."""

    ledger_path = Path(ledger_path).resolve(strict=True)
    contract_path = Path(contract_path).resolve(strict=True)
    approved_registry_path = Path(approved_registry_path).resolve(strict=True)
    starting_ledger_hash = digest(ledger_path)
    ledger, contract, approved_registry = validate_context(
        ledger_path, contract_path, approved_registry_path
    )
    if ledger.get("t43_launch_authorization", {}).get("status") != "user_approved":
        raise ValueError("candidate manifest registration requires T43 user authorization")
    if run_id not in TIER1_IDS + UPPER_IDS:
        raise ValueError("only Tier-1 or reviewed q3650 candidate manifests may be registered")
    if run_id in UPPER_IDS:
        validate_tier2_branch_gate(ledger, approved_registry)
    expected_registry = (ROOT / MANIFEST_RECEIPT_REGISTRY_RELATIVE_PATH).resolve()
    supplied_registry = Path(manifest_registry_path).resolve()
    if supplied_registry != expected_registry:
        raise ValueError("candidate manifest receipt registry path is not the fixed batch path")
    receipt_dir = (ROOT / MANIFEST_RECEIPT_DIRECTORY_RELATIVE_PATH).resolve()
    if not receipt_dir.is_dir():
        raise FileNotFoundError("candidate manifest receipt directory does not exist")
    receipt_path = receipt_dir / f"{run_id}_revision_01.json"
    if receipt_path.exists():
        raise FileExistsError(f"candidate manifest already has a receipt: {run_id}")
    overlay_run, _ = validate_runtime_source_registry(
        runtime_registry_path, ledger, approved_registry, run_id
    )
    run = run_record(approved_registry, run_id)
    manifest, file_hash, manifest_payload_sha256 = _validate_candidate_manifest_provenance(
        manifest_path, run, overlay_run, contract_path
    )

    if supplied_registry.exists():
        binding = ledger.get("candidate_manifest_receipt_registry", {})
        if (
            binding.get("path") != MANIFEST_RECEIPT_REGISTRY_RELATIVE_PATH
            or binding.get("sha256") != digest(supplied_registry)
        ):
            raise ValueError("existing manifest receipt registry is not ledger-bound")
        registry = load_json(supplied_registry)
        entries = registry.get("receipts")
        if not isinstance(entries, list):
            raise ValueError("manifest receipt registry entries are invalid")
        existing_paths = [
            ROOT / item["manifest_path"]
            for item in entries
            if isinstance(item, dict) and isinstance(item.get("manifest_path"), str)
        ]
        if len(existing_paths) != len(entries):
            raise ValueError("existing manifest receipt registry paths are invalid")
        validate_candidate_manifest_receipt_registry(
            supplied_registry,
            ledger,
            contract_path,
            approved_registry_path,
            existing_paths,
        )
    else:
        if ledger.get("candidate_manifest_receipt_registry") is not None:
            raise ValueError("ledger claims a missing candidate manifest receipt registry")
        registry = {
            "schema_version": 1,
            "batch_id": BATCH_ID,
            "role": "append-only verified candidate manifest receipt overlay",
            "approved_source_registry_sha256": digest(approved_registry_path),
            "runtime_source_registry_path": Path(runtime_registry_path)
            .resolve()
            .relative_to(ROOT)
            .as_posix(),
            "runtime_source_registry_sha256": digest(Path(runtime_registry_path)),
            "measurement_contract_sha256": digest(contract_path),
            "adapter_sha256": digest(Path(__file__)),
            "adapter_sha256s": [digest(Path(__file__))],
            "receipts": [],
            "status": "empty",
        }
        entries = registry["receipts"]
    if any(item.get("run_id") == run_id for item in entries):
        raise FileExistsError(f"candidate manifest already registered: {run_id}")

    manifest_resolved, manifest_relative = _manifest_file(manifest_path)
    receipt = {
        "schema_version": 1,
        "batch_id": BATCH_ID,
        "run_id": run_id,
        "seed": run["seed"],
        "q_main": run["q_main"],
        "attempt_id": overlay_run["attempt_id"],
        "manifest_path": manifest_relative,
        "manifest_file_sha256": file_hash,
        "manifest_payload_sha256": manifest_payload_sha256,
        "adapter_sha256": manifest["adapter_sha256"],
        "contract_sha256": manifest["contract_sha256"],
        "source_map_path": manifest["source_map_path"],
        "source_map_sha256": manifest["source_map_sha256"],
        "runtime_source_registry_sha256": digest(Path(runtime_registry_path)),
        "technical_qualified": True,
        "required_observation_audit": "7/7",
        "registration_status": "complete",
    }
    receipt_hash = payload_digest(receipt)
    index_entry = {
        "run_id": run_id,
        "receipt_path": receipt_path.relative_to(ROOT).as_posix(),
        "receipt_file_sha256": None,
        "receipt_payload_sha256": receipt_hash,
        "manifest_path": manifest_relative,
        "manifest_file_sha256": file_hash,
        "manifest_payload_sha256": manifest_payload_sha256,
    }

    # The receipt is immutable.  The registry and ledger are atomically replaced
    # one at a time; a crash between them fails closed on the next validation.
    write_json_atomic(receipt_path, receipt, must_not_exist=True)
    index_entry["receipt_file_sha256"] = digest(receipt_path)
    registry["receipts"].append(index_entry)
    adapter_hashes = set(registry.get("adapter_sha256s", [registry.get("adapter_sha256")]))
    adapter_hashes.add(manifest["adapter_sha256"])
    registry["adapter_sha256s"] = sorted(adapter_hashes)
    registered_ids = {item["run_id"] for item in registry["receipts"]}
    if registered_ids == set(TIER1_IDS + UPPER_IDS):
        registry["status"] = "tier1_and_selected_tier2_pairs_registered"
    elif set(TIER1_IDS).issubset(registered_ids):
        registry["status"] = (
            "selected_tier2_partial_registration"
            if registered_ids.intersection(UPPER_IDS)
            else "tier1_pair_registered"
        )
    else:
        registry["status"] = "tier1_partial_registration"
    write_json_atomic(
        supplied_registry, registry, must_not_exist=not supplied_registry.exists()
    )
    if digest(ledger_path) != starting_ledger_hash:
        raise RuntimeError("ledger changed during candidate manifest registration")
    ledger["candidate_manifest_receipt_registry"] = {
        "path": MANIFEST_RECEIPT_REGISTRY_RELATIVE_PATH,
        "sha256": digest(supplied_registry),
        "registered_run_ids": [item["run_id"] for item in registry["receipts"]],
        "status": registry["status"],
    }
    if registry["status"] == "tier1_and_selected_tier2_pairs_registered":
        ledger["status"] = "t43_selected_tier2_candidate_manifests_registered"
    elif registry["status"] == "selected_tier2_partial_registration":
        ledger["status"] = "t43_selected_tier2_candidate_manifest_registration_partial"
    elif registry["status"] == "tier1_pair_registered":
        ledger["status"] = "t43_tier1_candidate_manifests_registered_pending_decision"
    else:
        ledger["status"] = "t43_tier1_candidate_manifest_registration_partial"
    write_json_atomic(ledger_path, ledger)
    return index_entry


def validate_candidate_manifest_receipt_registry(
    manifest_registry_path: Path,
    ledger: dict,
    contract_path: Path,
    approved_registry_path: Path,
    manifest_paths: list[Path],
) -> tuple[dict, list[dict]]:
    """Validate supplied manifests through immutable per-run receipts."""

    manifest_registry_path = Path(manifest_registry_path).resolve(strict=True)
    binding = ledger.get("candidate_manifest_receipt_registry", {})
    registered_path = _registered_project_file(
        binding.get("path"), "candidate manifest receipt registry path"
    )
    if manifest_registry_path != registered_path:
        raise ValueError("candidate manifest receipt registry path differs from ledger")
    if digest(manifest_registry_path) != binding.get("sha256"):
        raise ValueError("candidate manifest receipt registry hash differs from ledger")
    registry = load_json(manifest_registry_path)
    approved_registry_path = Path(approved_registry_path).resolve(strict=True)
    runtime_binding = ledger.get("runtime_source_registry_overlay", {})
    allowed_adapters = _allowed_manifest_adapter_hashes(ledger)
    allowed_runtime_hashes = _registered_runtime_registry_hashes(ledger)
    registry_adapters = set(
        registry.get("adapter_sha256s", [registry.get("adapter_sha256")])
    )
    if (
        registry.get("batch_id") != BATCH_ID
        or registry.get("approved_source_registry_sha256")
        != digest(approved_registry_path)
        or registry.get("runtime_source_registry_path")
        != runtime_binding.get("path")
        or registry.get("runtime_source_registry_sha256") not in allowed_runtime_hashes
        or registry.get("measurement_contract_sha256")
        != digest(Path(contract_path))
        or not registry_adapters
        or not registry_adapters.issubset(allowed_adapters)
    ):
        raise ValueError("candidate manifest registry provenance binding mismatch")
    approved_registry = load_json(approved_registry_path)
    receipts = registry.get("receipts")
    if not isinstance(receipts, list):
        raise ValueError("candidate manifest receipt list is invalid")
    receipt_ids = [item.get("run_id") for item in receipts if isinstance(item, dict)]
    if (
        len(receipt_ids) != len(receipts)
        or len(receipt_ids) != len(set(receipt_ids))
        or any(run_id not in TIER1_IDS + UPPER_IDS for run_id in receipt_ids)
        or binding.get("registered_run_ids") != receipt_ids
    ):
        raise ValueError("candidate manifest receipt identities are invalid")
    if any(run_id in UPPER_IDS for run_id in receipt_ids):
        validate_tier2_branch_gate(ledger, approved_registry)

    ledger_with_receipts = json.loads(json.dumps(ledger))
    ledger_by_id = {
        item["run_id"]: item for item in ledger_with_receipts["logical_runs"]
    }
    receipts_by_id = {item["run_id"]: item for item in receipts}
    supplied: list[dict] = []
    supplied_ids: set[str] = set()
    for supplied_path in manifest_paths:
        resolved, relative = _manifest_file(supplied_path)
        manifest = load_json(resolved)
        run_id = manifest.get("run_id")
        if run_id in supplied_ids:
            raise ValueError("duplicate supplied manifest run identity")
        supplied_ids.add(run_id)
        expected = ledger_by_id.get(run_id)
        if expected is None:
            raise ValueError("supplied manifest run is not registered")
        if run_id in REFERENCE_IDS:
            _validate_manifest(manifest, expected, True, False)
            supplied.append(manifest)
            continue
        if run_id not in TIER1_IDS + UPPER_IDS:
            raise ValueError("unexecuted, cancelled, or unregistered candidate manifest is prohibited")
        if run_id in UPPER_IDS:
            validate_tier2_branch_gate(ledger, approved_registry)
        index_entry = receipts_by_id.get(run_id)
        if index_entry is None:
            raise ValueError("candidate manifest lacks a ledger-bound receipt")
        receipt_path = _registered_project_file(
            index_entry.get("receipt_path"), "candidate manifest receipt path"
        )
        if digest(receipt_path) != index_entry.get("receipt_file_sha256"):
            raise ValueError("candidate manifest receipt file hash mismatch")
        receipt = load_json(receipt_path)
        if payload_digest(receipt) != index_entry.get("receipt_payload_sha256"):
            raise ValueError("candidate manifest receipt payload hash mismatch")
        overlay_registry = load_json(ROOT / runtime_binding["path"])
        overlay_rows = {
            item["run_id"]: item for item in overlay_registry.get("runs", [])
        }
        overlay_run = overlay_rows.get(run_id)
        approved_run = run_record(approved_registry, run_id)
        expected_receipt = {
            "batch_id": BATCH_ID,
            "run_id": run_id,
            "seed": approved_run["seed"],
            "q_main": approved_run["q_main"],
            "attempt_id": overlay_run.get("attempt_id") if overlay_run else None,
            "manifest_path": relative,
            "manifest_file_sha256": digest(resolved),
            "manifest_payload_sha256": _manifest_payload_hash(manifest),
            "adapter_sha256": manifest.get("adapter_sha256"),
            "contract_sha256": digest(Path(contract_path)),
            "source_map_path": overlay_run.get("source_map_path") if overlay_run else None,
            "source_map_sha256": overlay_run.get("source_map_sha256") if overlay_run else None,
            "runtime_source_registry_sha256": receipt.get("runtime_source_registry_sha256"),
            "technical_qualified": True,
            "required_observation_audit": "7/7",
            "registration_status": "complete",
        }
        if any(receipt.get(key) != value for key, value in expected_receipt.items()):
            raise ValueError("candidate manifest receipt differs from registered provenance")
        if (
            manifest.get("adapter_sha256") not in allowed_adapters
            or receipt.get("runtime_source_registry_sha256") not in allowed_runtime_hashes
        ):
            raise ValueError("candidate manifest receipt uses an unreviewed adapter or runtime overlay")
        if any(
            index_entry.get(key) != value
            for key, value in {
                "manifest_path": relative,
                "manifest_file_sha256": digest(resolved),
                "manifest_payload_sha256": _manifest_payload_hash(manifest),
            }.items()
        ):
            raise ValueError("candidate manifest index differs from supplied file")
        expected["manifest_payload_sha256"] = receipt["manifest_payload_sha256"]
        _validate_manifest(manifest, expected, True, True)
        supplied.append(manifest)
    return ledger_with_receipts, supplied


def load_registered_ejmi_references(run: dict, contract: dict, lower_path: Path,
                                    upper_path: Path) -> tuple[dict, dict]:
    mapping = contract["ejmi_reference_map"].get(run["run_id"])
    if mapping is None:
        raise ValueError("candidate has no registered EJMI reference mapping")
    loaded = []
    for side, supplied in (("lower", Path(lower_path)), ("upper", Path(upper_path))):
        expected = mapping[side]
        registered_path = (ROOT / expected["manifest_path"]).resolve()
        if supplied.resolve() != registered_path or not registered_path.is_file():
            raise ValueError(f"candidate {side} manifest path differs from its registered same-seed reference")
        manifest = load_json(registered_path)
        identity = {"run_id": expected["run_id"], "seed": expected["seed"], "q_main": expected["q_main"]}
        _validate_manifest(manifest, identity, False)
        if (_manifest_payload_hash(manifest) != expected["manifest_payload_sha256"]
                or manifest.get("source_map_path") != expected["source_map_path"]
                or manifest.get("source_map_sha256") != expected["source_map_sha256"]
                or not manifest.get("technical_qualified")):
            raise ValueError(f"candidate {side} reference content/provenance changed")
        loaded.append(manifest)
    lower, upper = loaded
    if lower["seed"] != run["seed"] or upper["seed"] != run["seed"]:
        raise ValueError("candidate references are not same-seed")
    return lower, upper


def validate_candidate_decision_inputs(ledger: dict, manifests: list[dict]) -> None:
    registered_by_id = {row.get("run_id"): row for row in ledger.get("logical_runs", [])}
    if tuple(registered_by_id) != ALL_RUN_IDS:
        raise ValueError("ledger logical-run universe/order changed")
    supplied_ids = [row.get("run_id") for row in manifests]
    if len(supplied_ids) != len(set(supplied_ids)) or not set(supplied_ids).issubset(set(ALL_RUN_IDS) - set(REFERENCE_IDS)):
        raise ValueError("decision input contains duplicate, reference, or unregistered run manifest")
    for manifest in manifests:
        _validate_manifest(
            manifest,
            registered_by_id[manifest["run_id"]],
            bool(ledger.get("manifest_hash_required")),
            True,
        )


def validate_final_candidate_set(ledger: dict, manifests: list[dict]) -> None:
    supplied = {row.get("run_id") for row in manifests}
    if ledger.get("tier2_branch_gate") is not None:
        expected = set(TIER1_IDS + UPPER_IDS)
        if supplied != expected or len(manifests) != len(expected):
            raise ValueError("final decision requires the exact Tier-1 and q3650 seed pairs")
    elif supplied != set(TIER1_IDS) or len(manifests) != len(TIER1_IDS):
        raise ValueError("final decision without Tier-2 requires the exact Tier-1 seed pair")


def command_analyze(args: argparse.Namespace) -> None:
    ledger, contract, registry = validate_context(
        Path(args.ledger), Path(args.contract), Path(args.registry)
    )
    run = run_record(registry, args.run_id)
    if run["role"].endswith("reference"):
        if args.runtime_registry:
            raise ValueError("reference analysis cannot use a runtime registry overlay")
        if not run.get("source_map_path") or not run.get("source_map_sha256"):
            raise ValueError("reference has no immutable registered archived source")
        source_map = ROOT / run["source_map_path"]
        source_map_sha256 = run["source_map_sha256"]
        if digest(source_map) != source_map_sha256:
            raise ValueError("registered source-map hash mismatch")
        if args.lower_manifest or args.upper_manifest:
            raise ValueError("reference analysis does not accept candidate reference arguments")
        lower = upper = None
    else:
        if run.get("source_map_path") or run.get("source_map_sha256"):
            if args.runtime_registry:
                raise ValueError("runtime registry cannot override an immutable source binding")
            if not run.get("source_map_path") or not run.get("source_map_sha256"):
                raise ValueError("approved source binding is incomplete")
            source_map = ROOT / run["source_map_path"]
            source_map_sha256 = run["source_map_sha256"]
            if digest(source_map) != source_map_sha256:
                raise ValueError("registered source-map hash mismatch")
        else:
            if not args.runtime_registry:
                raise ValueError(
                    "run has no immutable archived source; explicit ledger-bound "
                    "--runtime-registry is required"
                )
            overlay_run, source_map = validate_runtime_source_registry(
                Path(args.runtime_registry), ledger, registry, args.run_id
            )
            source_map_sha256 = overlay_run["source_map_sha256"]
        if not args.lower_manifest or not args.upper_manifest:
            raise ValueError("candidate analysis requires both registered matched-seed reference manifests")
        lower, upper = load_registered_ejmi_references(
            run, contract, Path(args.lower_manifest), Path(args.upper_manifest))
    output_dir = reserve_directory(Path(args.output_dir))
    try:
        manifest = analyze_registered_archive(run, ArchiveResolver(source_map), contract, lower, upper)
        manifest["source_map_path"] = source_map.relative_to(ROOT).as_posix()
        manifest["source_map_sha256"] = source_map_sha256
        manifest["contract_sha256"] = digest(Path(args.contract))
        manifest["adapter_sha256"] = digest(Path(__file__))
        write_json_exclusive(output_dir / "run_manifest.json", manifest)
    except Exception:
        write_json_exclusive(output_dir / "INCOMPLETE.json", {"status": "incomplete", "run_id": args.run_id})
        raise


def command_register_manifest(args: argparse.Namespace) -> None:
    result = register_candidate_manifest(
        Path(args.ledger),
        Path(args.contract),
        Path(args.registry),
        Path(args.runtime_registry),
        Path(args.manifest_registry),
        args.run_id,
        Path(args.manifest_path),
    )
    print(json.dumps(result, sort_keys=True))


def command_register_tier2_plan(args: argparse.Namespace) -> None:
    result = register_tier2_plan(
        Path(args.ledger),
        Path(args.contract),
        Path(args.registry),
        Path(args.manifest_registry),
        Path(args.decision),
        Path(args.scientific_review_receipt),
        Path(args.gate_registration),
    )
    print(json.dumps(result, sort_keys=True))


def command_decide(args: argparse.Namespace) -> None:
    ledger, _, _ = validate_context(
        Path(args.ledger), Path(args.contract), Path(args.registry)
    )
    ledger, manifests = validate_candidate_manifest_receipt_registry(
        Path(args.manifest_registry),
        ledger,
        Path(args.contract),
        Path(args.registry),
        [Path(path) for path in args.run_manifest],
    )
    validate_candidate_decision_inputs(ledger, manifests)
    output_dir = reserve_directory(Path(args.output_dir))
    try:
        decision = decide_tier1(manifests)
        write_json_exclusive(output_dir / "branch_decision.json", decision)
    except Exception:
        write_json_exclusive(output_dir / "INCOMPLETE.json", {"status": "incomplete", "step": "tier1_decision"})
        raise


def command_status(args: argparse.Namespace) -> None:
    ledger, _, _ = validate_context(Path(args.ledger), Path(args.contract), Path(args.registry))
    ledger, manifests = validate_candidate_manifest_receipt_registry(
        Path(args.manifest_registry),
        ledger,
        Path(args.contract),
        Path(args.registry),
        [Path(path) for path in args.run_manifest],
    )
    if ledger.get("tier2_branch_gate") is not None:
        validate_tier2_branch_gate(ledger, load_json(Path(args.registry)))
        branch_path = Path(args.branch_decision).resolve(strict=True)
        if branch_path != (ROOT / TIER1_SCIENTIFIC_DECISION_RELATIVE_PATH).resolve():
            raise ValueError("status requires the registered scientific Tier-1 decision")
        _validate_tier2_branch_decision_content(load_json(branch_path))
    output_dir = reserve_directory(Path(args.output_dir))
    try:
        summary = build_logical_statuses(
            ledger, manifests, load_json(Path(args.branch_decision))
        )
        write_json_exclusive(output_dir / "logical_status_summary.json", summary)
    except Exception:
        write_json_exclusive(output_dir / "INCOMPLETE.json", {"status": "incomplete", "step": "logical_status"})
        raise


def command_final(args: argparse.Namespace) -> None:
    ledger, _, _ = validate_context(Path(args.ledger), Path(args.contract), Path(args.registry))
    ledger, manifests = validate_candidate_manifest_receipt_registry(
        Path(args.manifest_registry),
        ledger,
        Path(args.contract),
        Path(args.registry),
        [Path(path) for path in args.run_manifest],
    )
    validate_candidate_decision_inputs(ledger, manifests)
    validate_final_candidate_set(ledger, manifests)
    output_dir = reserve_directory(Path(args.output_dir))
    try:
        result = decide_final(manifests)
        write_json_exclusive(output_dir / "final_decision.json", result)
    except Exception:
        write_json_exclusive(output_dir / "INCOMPLETE.json", {"status": "incomplete", "step": "final_decision"})
        raise


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    register = sub.add_parser("register-manifest")
    register.add_argument("--ledger", required=True)
    register.add_argument("--contract", required=True)
    register.add_argument("--registry", required=True)
    register.add_argument("--runtime-registry", required=True)
    register.add_argument("--manifest-registry", required=True)
    register.add_argument("--run-id", required=True)
    register.add_argument("--manifest-path", required=True)
    register.set_defaults(func=command_register_manifest)
    register_tier2 = sub.add_parser("register-tier2-plan")
    register_tier2.add_argument("--ledger", required=True)
    register_tier2.add_argument("--contract", required=True)
    register_tier2.add_argument("--registry", required=True)
    register_tier2.add_argument("--manifest-registry", required=True)
    register_tier2.add_argument("--decision", required=True)
    register_tier2.add_argument("--scientific-review-receipt", required=True)
    register_tier2.add_argument("--gate-registration", required=True)
    register_tier2.set_defaults(func=command_register_tier2_plan)
    for name in ("analyze-run", "decide-tier1", "decide-final", "summarize-status"):
        command = sub.add_parser(name)
        command.add_argument("--ledger", required=True)
        command.add_argument("--contract", required=True)
        command.add_argument("--registry", required=True)
        command.add_argument("--output-dir", required=True)
        if name == "analyze-run":
            command.add_argument("--run-id", required=True)
            command.add_argument(
                "--runtime-registry",
                help=(
                    "Explicit ledger-bound post-authorization execution-fact overlay; "
                    "required for completed T43 candidates whose immutable source "
                    "registry fields are null"
                ),
            )
            command.add_argument("--lower-manifest")
            command.add_argument("--upper-manifest")
            command.set_defaults(func=command_analyze)
        elif name in {"decide-tier1", "decide-final"}:
            command.add_argument("--manifest-registry", required=True)
            command.add_argument("--run-manifest", action="append", required=True)
            command.set_defaults(func=command_decide if name == "decide-tier1" else command_final)
        else:
            command.add_argument("--manifest-registry", required=True)
            command.add_argument("--run-manifest", action="append", default=[])
            command.add_argument("--branch-decision", required=True)
            command.set_defaults(func=command_status)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    args.func(args)
    return 0


if __name__ == "__main__":
    sys.exit(main())

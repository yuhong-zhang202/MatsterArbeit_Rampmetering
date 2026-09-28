#!/usr/bin/env python3
"""Offline materializer and fail-closed checker for the minimal3350 R0 control.

No SUMO/TraCI/netconvert imports or process launch are permitted here.
"""
from __future__ import annotations

import hashlib
import json
from decimal import Decimal
from pathlib import Path
import shutil
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[3]
PACKAGE_REL = "artifacts/stage6_minimal3350_control_preparation_20260924_rev8"
SOURCE_DEMAND_REL = "artifacts/stage6_baseline_localization_20260921_v1/LOC_M3350_S17/engineering/inputs/LOC_M3350_S17_attempt1/demand.rou.xml"
SOURCE_VEHROUTE_REL = "data/raw/stage6_baseline_localization_20260921_v1/LOC_M3350_S17_attempt1/outputs/vehroute.xml"
NETWORK_REL = "artifacts/stage6_baseline_localization_20260921_v1/LOC_M3350_S17/engineering/build_attempts/TV_BUILD01/network.net.xml"
TEMPLATE_REL = "scripts/stage6/minimal3199/prepared_rev3/control"
RUN_ID = "MINIMAL3350_CTRL_S17"
EXPECTED_M = 1396
EXPECTED_OFFSET_MS = 1074
EXPECTED_END_MS = 1_500_000
PLAN_REL = "artifacts/stage6_minimal_ramp_induced_breakdown_existence_test_20260924_v1/PLAN.md"
LOCKED_METHOD_REL = "docs/methodology/FREEWAY_PROTECTABLE_STATE_EXPLORATORY_DEFINITION.md"
RUNNER_REL = "artifacts/stage6_ramp_induced_validation_20260922_v1/r02_single_start/runner.py"
OUTPUT_REL = "data/raw/stage6_minimal3350_ux0_20260924_v8/MINIMAL3350_CTRL_S17/outputs"
RUNTIME_REL = f"{PACKAGE_REL}/runtime_binding.json"
ROLE_SOURCE_REL = f"{PACKAGE_REL}/inputs/control/output_roles.json"
AUTHORIZATION = "USER_AUTHORIZED_CONDITIONAL_MINIMAL3350_CONTROL_START_AFTER_THREE_REVIEWS"


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def _vehicle_signature(node: ET.Element) -> tuple[str, ...]:
    required = ("id", "type", "route", "depart", "departPos", "departLane", "departSpeed", "speedFactor")
    if any(node.get(key) is None for key in required):
        raise ValueError(f"materialized vehicle misses required field: {node.get('id')}")
    return tuple(node.get(key, "") for key in required)


def extract_speed_factors(repo: Path = ROOT) -> dict[str, str]:
    """Read the exact observed 3350.4-seed17 M speedFactor realization.

    This source is the prior full-network run, whose M IDs and all 1396
    speedFactors reconcile. Its use as the explicit common-M realization is
    transparently bound in the manifest for data/science review.
    """
    source = repo / SOURCE_VEHROUTE_REL
    root = ET.parse(source).getroot()
    factors: dict[str, str] = {}
    for node in root:
        vid = node.get("id", "")
        if node.tag == "vehicle" and vid.startswith("M_flow."):
            if vid in factors or node.get("speedFactor") is None:
                raise ValueError(f"duplicate or missing M speedFactor: {vid}")
            index = int(vid.rsplit(".", 1)[1])
            if not 0 <= index < EXPECTED_M:
                raise ValueError(f"out-of-range M id: {vid}")
            factors[vid] = node.attrib["speedFactor"]
    expected = {f"M_flow.{i}" for i in range(EXPECTED_M)}
    if set(factors) != expected:
        raise ValueError(f"M speedFactor identity coverage mismatch: missing={len(expected-set(factors))}, extra={len(set(factors)-expected)}")
    return factors


def build_demand(repo: Path = ROOT) -> bytes:
    """Materialize SUMO 1.26 begin/end/number integer-ms offset semantics."""
    source = repo / SOURCE_DEMAND_REL
    source_root = ET.parse(source).getroot()
    vtypes = [n for n in source_root if n.tag == "vType"]
    routes = [n for n in source_root if n.tag == "route"]
    mflow = next((n for n in source_root if n.tag == "flow" and n.get("id") == "M_flow"), None)
    if mflow is None or (mflow.get("begin"), mflow.get("end"), mflow.get("number")) != ("0", "1500", "1396"):
        raise ValueError("source M flow no longer matches the approved 3350.4 input")
    source_ids = (mflow.get("type"), mflow.get("route"), mflow.get("departPos"), mflow.get("departLane"), mflow.get("departSpeed"))
    if source_ids != ("technical_passenger", "M_route", "100", "best", "max"):
        raise ValueError("source M flow attributes differ from accepted input")
    factors = extract_speed_factors(repo)
    root = ET.Element("routes", {"{http://www.w3.org/2001/XMLSchema-instance}noNamespaceSchemaLocation": "http://sumo.dlr.de/xsd/routes_file.xsd"})
    for node in (*vtypes, *routes):
        root.append(ET.fromstring(ET.tostring(node, encoding="utf-8")))
    prior: tuple[int, str] | None = None
    records = []
    for i in range(EXPECTED_M):
        vid = f"M_flow.{i}"
        depart_ms = i * EXPECTED_OFFSET_MS
        if depart_ms >= EXPECTED_END_MS:
            raise ValueError(f"M schedule exceeds half-open source interval at {vid}")
        node = ET.Element("vehicle", {
            "id": vid, "type": "technical_passenger", "route": "M_route",
            "depart": f"{Decimal(depart_ms) / Decimal(1000):.3f}",
            "departPos": "100", "departLane": "best", "departSpeed": "max",
            "speedFactor": factors[vid],
        })
        key = (depart_ms, vid)
        if prior is not None and key < prior:
            raise ValueError("M demand source order is not globally (depart_ms,id) sorted")
        prior = key
        records.append(node)
    for node in records:
        root.append(node)
    return ET.tostring(root, encoding="utf-8", xml_declaration=True) + b"\n"


def verify_demand(path: Path, *, expected_sha256: str | None = None) -> dict[str, object]:
    if expected_sha256 and sha256(path) != expected_sha256:
        raise ValueError("M demand hash mismatch")
    root = ET.parse(path).getroot()
    vehicles = [n for n in root if n.tag == "vehicle"]
    if any(n.tag not in {"vType", "route", "vehicle"} for n in root):
        raise ValueError("unsupported top-level route node")
    ids = [n.get("id") for n in vehicles]
    expected_ids = [f"M_flow.{i}" for i in range(EXPECTED_M)]
    if ids != expected_ids:
        raise ValueError("M vehicle count, exact ID sequence, or order mismatch")
    if {n.tag for n in root if n.tag not in {"vType", "route", "vehicle"}}:
        raise ValueError("non-M demand node present")
    if not any(n.tag == "vType" and n.attrib == {"id": "technical_passenger", "vClass": "passenger"} for n in root):
        raise ValueError("technical_passenger vType missing or altered")
    if not any(n.tag == "route" and n.attrib == {"id": "M_route", "edges": "main_up merge_section main_down"} for n in root):
        raise ValueError("M_route missing or altered")
    prior: tuple[int, str] | None = None
    for i, node in enumerate(vehicles):
        sig = _vehicle_signature(node)
        depart_ms = int(Decimal(sig[3]) * 1000)
        if depart_ms != i * EXPECTED_OFFSET_MS:
            raise ValueError(f"SUMO integer-offset schedule mismatch at M_flow.{i}")
        if sig[0] != f"M_flow.{i}" or sig[1:3] != ("technical_passenger", "M_route") or sig[4:7] != ("100", "best", "max"):
            raise ValueError(f"M attributes differ from approved flow source at M_flow.{i}")
        key = (depart_ms, sig[0])
        if prior is not None and key < prior:
            raise ValueError("vehicle order mismatch")
        prior = key
    return {"status": "PASS", "m_count": len(vehicles), "m_ids": len(set(ids)),
            "schedule_offset_ms": EXPECTED_OFFSET_MS, "last_depart_ms": (EXPECTED_M-1)*EXPECTED_OFFSET_MS,
            "explicit_R_U_X_zero": True, "all_M_speedFactors_explicit": True}


def verify_common_manifest(path: Path, demand_path: Path, *, expected_sha256: str) -> dict[str, object]:
    if sha256(path) != expected_sha256:
        raise ValueError("common M manifest SHA-256 mismatch")
    manifest = json.loads(path.read_text(encoding="utf-8"))
    if (manifest.get("schema") != "minimal3350_common_m_vehicle_list_v1"
            or manifest.get("qMain_veh_per_h") != 3350.4
            or manifest.get("seed") != 17
            or manifest.get("planned_count") != EXPECTED_M):
        raise ValueError("common M manifest header mismatch")
    demand_root = ET.parse(demand_path).getroot()
    demand_vehicles = [n for n in demand_root if n.tag == "vehicle"]
    records = manifest.get("records")
    if not isinstance(records, list) or len(records) != EXPECTED_M:
        raise ValueError("common M manifest row count mismatch")
    fields = ("id", "type", "route", "depart", "departPos", "departLane", "departSpeed", "speedFactor")
    for planned, actual in zip(records, demand_vehicles, strict=True):
        if any(planned.get(key) != actual.get(key) for key in fields):
            raise ValueError(f"common M manifest/demand row mismatch: {planned.get('id')}")
        if planned.get("desired_depart_ms") != int(Decimal(actual.get("depart", "0")) * 1000):
            raise ValueError(f"common M manifest depart_ms mismatch: {planned.get('id')}")
    return {"status": "PASS", "rows": len(records), "matches_demand": True}


def verify_output_bindings(config_path: Path, additional_path: Path, roles_path: Path,
                           output_directory: Path) -> dict[str, object]:
    """Require every configured SUMO output target to resolve under the bound output directory."""
    expected_root = output_directory.resolve(strict=False)
    role_data = json.loads(roles_path.read_text(encoding="utf-8"))
    roles = role_data.get("required_xml_roles")
    if not isinstance(roles, list) or len(roles) != 18:
        raise ValueError("required output role inventory must contain exactly 18 XML roles")
    role_paths = []
    for role in roles:
        path = Path(role.get("path", "")).resolve(strict=False)
        if path.parent != expected_root:
            raise ValueError(f"output role path escapes bound output directory: {path}")
        role_paths.append(path)
    if len(set(role_paths)) != len(role_paths):
        raise ValueError("duplicate output role path")

    config = ET.parse(config_path).getroot()
    config_targets = []
    for node in config.iter():
        value = node.get("value")
        if value and (node.tag.endswith("-output") or node.tag in {"log", "error-log"}):
            target = Path(value).resolve(strict=False)
            if target.parent != expected_root:
                raise ValueError(f"sumocfg output path escapes bound output directory: {target}")
            config_targets.append(target)

    additional = ET.parse(additional_path).getroot()
    additional_targets = []
    for node in additional.iter():
        for attr in ("file", "dest"):
            value = node.get(attr)
            if value:
                target = Path(value).resolve(strict=False)
                if target.parent != expected_root:
                    raise ValueError(f"additional output path escapes bound output directory: {target}")
                additional_targets.append(target)
    if len(config_targets) != 8 or len(additional_targets) != 12:
        raise ValueError("configured output target inventory differs from expected SUMO role inventory")
    return {"status": "PASS", "bound_output_directory": str(expected_root),
            "role_paths": len(role_paths), "sumocfg_targets": len(config_targets),
            "additional_targets": len(additional_targets), "all_targets_match": True}


def validate_control_card(card: dict[str, object], demand_path: Path, common_path: Path, repo: Path = ROOT) -> dict[str, object]:
    """Fail-closed card/condition/resource/hash check used by R02 and tests."""
    if (card.get("run_id") != RUN_ID or card.get("execution_attempt_id") != RUN_ID
            or card.get("pair_id") != "MINIMAL3350_UX0_S17"
            or card.get("qMain_veh_per_h") != 3350.4 or card.get("seed") != 17
            or card.get("R_veh_per_h") != 0 or card.get("R_window_s") != "NO_R_SOURCE"
            or card.get("U") != 0 or card.get("X") != 0 or card.get("TLS_program") != "A_OPEN"
            or card.get("horizon_s") != 2700 or card.get("step_s") != 1):
        raise ValueError("minimal3350 control scientific condition mismatch")
    expected_counts = {
        "M": {"planned_count": 1396, "status": "BOUND"},
        "R": {"planned_count": 0, "status": "PASS_ZERO"},
        "U": {"planned_count": 0, "status": "PASS_ZERO"},
        "X": {"planned_count": 0, "status": "PASS_ZERO"},
    }
    if card.get("class_counts") != expected_counts or card.get("M_planned_count") != 1396:
        raise ValueError("minimal3350 control planned class ledger mismatch")
    if card.get("output_directory") != OUTPUT_REL:
        raise ValueError("minimal3350 output path mismatch")
    runtime = card.get("runtime_binding")
    resource = card.get("resource_limits")
    if (not isinstance(runtime, dict) or runtime.get("max_runtime_s") != 90
            or runtime.get("max_output_bytes") != 60_000_000
            or runtime.get("guardian_runner_sha256") != sha256(repo / RUNNER_REL)
            or not isinstance(resource, dict) or resource.get("runtime_s") != 90
            or resource.get("storage_bytes") != 60_000_000
            or resource.get("scope") != RUN_ID or resource.get("status") != "AUTHORIZED_FOR_THIS_RUN"):
        raise ValueError("minimal3350 runtime/resource binding mismatch")
    inputs = card.get("input_sha256")
    if not isinstance(inputs, dict) or inputs.get("demand") != sha256(demand_path):
        raise ValueError("minimal3350 demand hash binding mismatch")
    common = card.get("common_m_manifest")
    if (not isinstance(common, dict) or common.get("path") != f"{PACKAGE_REL}/COMMON_M_DEMAND_MANIFEST.json"
            or common.get("sha256") != sha256(common_path)):
        raise ValueError("minimal3350 common M provenance mismatch")
    schedule = verify_demand(demand_path, expected_sha256=inputs["demand"])
    verify_common_manifest(common_path, demand_path, expected_sha256=common["sha256"])
    input_paths = card.get("inputs")
    if not isinstance(input_paths, dict):
        raise ValueError("minimal3350 input path map missing")
    package = common_path.parent
    output_binding = verify_output_bindings(
        package / input_paths["sumocfg"], package / input_paths["additional"],
        package / input_paths["output_roles"], repo / OUTPUT_REL)
    return {"status": "PASS", "run_id": RUN_ID, "m_count": schedule["m_count"],
            "resource_limits": [90, 60_000_000], "output_path_bound": True,
            "output_binding": output_binding}


def _write_json(path: Path, value: object) -> bytes:
    raw = (json.dumps(value, indent=2, sort_keys=True) + "\n").encode("utf-8")
    path.write_bytes(raw)
    return raw


def canonical_start_request_bytes(request: dict[str, object], runner_module: object) -> bytes:
    """Serialize the persisted START request exactly as R02 hashes and validates it."""
    canonical = getattr(runner_module, "canonical_json_bytes", None)
    if not callable(canonical):
        raise ValueError("R02 canonical JSON serializer is unavailable")
    payload = canonical(request)
    if not isinstance(payload, bytes) or json.loads(payload) != request:
        raise ValueError("R02 canonical START request serialization is invalid")
    return payload


def start_request_receipt_matches(request: dict[str, object], request_bytes: bytes,
                                  request_sha256: str, runner_module: object) -> bool:
    expected = canonical_start_request_bytes(request, runner_module)
    return request_bytes == expected and hashlib.sha256(expected).hexdigest() == request_sha256


def materialize_control_package(repo: Path = ROOT) -> dict[str, object]:
    """Create immutable, control-only exact-card preparation package.

    The existing M speedFactor sample is explicitly sourced from the reviewed
    3350.4 seed17 full-network vehroute output. Reviewers must assess that
    provenance; this function does not claim that seed equality alone matches
    RNG state across scenarios.
    """
    package = repo / PACKAGE_REL
    output_root = repo / OUTPUT_REL
    consumption = package / "r02_single_start/consumption"
    if package.exists() or output_root.exists() or output_root.parent.exists() or consumption.exists():
        raise FileExistsError("refusing to reuse package, output-root, or one-start reservation path")
    source = repo / SOURCE_DEMAND_REL
    source_vehicle = repo / SOURCE_VEHROUTE_REL
    template = repo / TEMPLATE_REL
    net = repo / NETWORK_REL
    for path in (source, source_vehicle, net, repo / PLAN_REL, repo / LOCKED_METHOD_REL, template / "scenario.sumocfg", template / "scenario.add.xml", template / "output_roles.json"):
        if not path.is_file():
            raise FileNotFoundError(path)
    old_run_prefix = "stage6_minimal3199_existence_20260924_v1/MINIMAL3199_CTRL_S17/outputs"
    old_output_absolute = str((repo / "data/raw" / old_run_prefix).resolve())
    new_output_absolute = str((repo / OUTPUT_REL).resolve())
    input_root = package / "inputs/control"
    input_root.mkdir(parents=True)

    demand_bytes = build_demand(repo)
    demand_path = input_root / "demand.rou.xml"
    demand_path.write_bytes(demand_bytes)

    config_text = (template / "scenario.sumocfg").read_text(encoding="utf-8")
    config_text = config_text.replace(
        str((repo / TEMPLATE_REL / "demand.rou.xml").resolve()), str(demand_path.resolve()))
    config_text = config_text.replace(
        str((repo / TEMPLATE_REL / "scenario.add.xml").resolve()), str((input_root / "scenario.add.xml").resolve()))
    config_text = config_text.replace(old_output_absolute, new_output_absolute)
    config_text = config_text.replace("MINIMAL3199_CTRL_S17", RUN_ID)
    add_text = (template / "scenario.add.xml").read_text(encoding="utf-8").replace(old_output_absolute, new_output_absolute)
    if "stage6_minimal3199_existence_20260924_v1" in config_text + add_text or "MINIMAL3199_CTRL_S17" in config_text + add_text:
        raise ValueError("stale 3199 path/run-id remains after deterministic path binding")
    (input_root / "scenario.sumocfg").write_text(config_text, encoding="utf-8")
    (input_root / "scenario.add.xml").write_text(add_text, encoding="utf-8")

    role_data = json.loads((template / "output_roles.json").read_text(encoding="utf-8"))
    role_data_text = json.dumps(role_data).replace(old_output_absolute, new_output_absolute).replace("MINIMAL3199_CTRL_S17", RUN_ID)
    role_data = json.loads(role_data_text)
    (input_root / "output_roles.json").write_text(json.dumps(role_data, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    output_binding = verify_output_bindings(input_root / "scenario.sumocfg", input_root / "scenario.add.xml",
                                            input_root / "output_roles.json", output_root)

    source_hashes = {
        "source_flow": sha256(source), "source_vehroute": sha256(source_vehicle),
        "network": sha256(net), "plan": sha256(repo / PLAN_REL),
        "locked_method": sha256(repo / LOCKED_METHOD_REL),
        "template_sumocfg": sha256(template / "scenario.sumocfg"),
        "template_additional": sha256(template / "scenario.add.xml"),
        "template_output_roles": sha256(template / "output_roles.json"),
        "materializer": sha256(Path(__file__).resolve()),
    }
    mroot = ET.parse(demand_path).getroot()
    records = []
    for node in mroot:
        if node.tag == "vehicle":
            records.append(dict(node.attrib, desired_depart_ms=int(Decimal(node.get("depart", "0")) * 1000)))
    common = {
        "schema": "minimal3350_common_m_vehicle_list_v1", "status": "CONTROL_LIST_BOUND_FOR_FUTURE_MATCHED_TREATMENT",
        "qMain_veh_per_h": 3350.4, "seed": 17, "planned_count": EXPECTED_M,
        "schedule_semantics": "SUMO 1.26.0 integer SUMOTime repetitionOffset = trunc((repetitionEnd - depart)/repetitionNumber); 1500000ms/1396 => 1074ms",
        "vehicle_order": "globally sorted by (desired_depart_ms, id)",
        "vehicle_fields": ["id", "desired_depart_ms", "type", "route", "departPos", "departLane", "departSpeed", "speedFactor"],
        "speedFactor_source": {"path": SOURCE_VEHROUTE_REL, "sha256": source_hashes["source_vehroute"],
                               "provenance_note": "Copied per-vehicle M speedFactor values from the prior qMain=3350.4 seed17 full-network run; U/X were nonzero there. This is explicit materialization for common-demand matching and is submitted for data/scientific review."},
        "source_flow": {"path": SOURCE_DEMAND_REL, "sha256": source_hashes["source_flow"],
                        "M_flow": {"begin_s": 0, "end_s": 1500, "number": 1396, "departPos": "100", "departLane": "best", "departSpeed": "max"}},
        "records": records,
    }
    common_path = package / "COMMON_M_DEMAND_MANIFEST.json"
    common_path.parent.mkdir(parents=True, exist_ok=True)
    common_bytes = _write_json(common_path, common)

    runtime_source = repo / "scripts/stage6/minimal3199/prepared_rev3/control/runtime_binding.json"
    runtime = json.loads(runtime_source.read_text(encoding="utf-8"))
    import importlib.util
    spec = importlib.util.spec_from_file_location("minimal3350_r02", repo / RUNNER_REL)
    if spec is None or spec.loader is None:
        raise RuntimeError("unable to load R02 module without starting a process")
    r02 = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(r02)
    runner_hash = sha256(repo / RUNNER_REL)
    runtime.update({
        "guardian_runner_sha256": runner_hash,
        "max_runtime_s": 90, "max_output_bytes": 60_000_000,
        "resource_proposal": {
            "basis": "User-accepted MINIMAL3350 control contract; prior 3350.4 completed raw output exists but U=X0 output size is new.",
            "enforcement": "100ms_polled_stop_trigger_with_possible_overshoot_not_hard_quota",
            "output_size_stop_limit_bytes_decimal": 60_000_000,
            "overshoot_accepted": True, "poll_interval_s": 0.1,
            "scope": RUN_ID, "status": "AUTHORIZED_FOR_THIS_RUN", "wallclock_stop_limit_s": 90,
        },
    })
    (package / "runtime_binding.json").write_text(json.dumps(runtime, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    runtime_hash = sha256(package / "runtime_binding.json")

    input_hashes = {
        "demand": sha256(demand_path), "sumocfg": sha256(input_root / "scenario.sumocfg"),
        "additional": sha256(input_root / "scenario.add.xml"), "output_roles": sha256(input_root / "output_roles.json"),
        "network": sha256(net),
    }
    input_paths = {
        "demand": f"inputs/control/demand.rou.xml", "sumocfg": f"inputs/control/scenario.sumocfg",
        "additional": f"inputs/control/scenario.add.xml", "output_roles": f"inputs/control/output_roles.json",
        "network": NETWORK_REL,
    }
    input_manifest = {
        "schema": "stage6_minimal3350_control_execution_manifest_v1", "package_id": PACKAGE_REL.split("/")[-1],
        "run_id": RUN_ID, "pair_id": "MINIMAL3350_UX0_S17", "design_path": PLAN_REL,
        "design_plan_sha256": source_hashes["plan"],
        "locked_method": {"path": LOCKED_METHOD_REL, "sha256": source_hashes["locked_method"]},
        "arm": "control", "arm_inputs": {"control": {role: {"path": input_paths[role], "sha256": input_hashes[role]} for role in input_paths}},
        "class_counts": {"control": {"M": {"planned_count": EXPECTED_M, "status": "BOUND"},
                                        "R": {"planned_count": 0, "status": "PASS_ZERO"},
                                        "U": {"planned_count": 0, "status": "PASS_ZERO"},
                                        "X": {"planned_count": 0, "status": "PASS_ZERO"}}},
        "common_m_manifest": {"path": f"{PACKAGE_REL}/COMMON_M_DEMAND_MANIFEST.json", "sha256": hashlib.sha256(common_bytes).hexdigest()},
        "source_hashes": source_hashes,
        "runner_path": RUNNER_REL, "runner_sha256": runner_hash,
        "runtime_binding_path": RUNTIME_REL, "runtime_binding_sha256": runtime_hash,
        "output_role_source": {"path": ROLE_SOURCE_REL, "sha256": input_hashes["output_roles"]},
    }
    manifest_bytes = _write_json(package / "INPUT_MANIFEST.json", input_manifest)
    manifest_hash = hashlib.sha256(manifest_bytes).hexdigest()

    card_path_rel = r02.MINIMAL3350_CONTROL_BINDING["card_path"]
    card = {
        "schema_version": "1", "card_revision": 2, "card_status": "FINAL_AUTHORIZED_FOR_ONE_START",
        "run_id": RUN_ID, "execution_attempt_id": RUN_ID, "pair_id": "MINIMAL3350_UX0_S17",
        "condition": "A_OPEN_R0_CONTROL", "qMain_veh_per_h": 3350.4, "R_veh_per_h": 0,
        "R_window_s": "NO_R_SOURCE", "U": 0, "X": 0, "TLS_program": "A_OPEN",
        "seed": 17, "horizon_s": 2700, "step_s": 1, "M_planned_count": EXPECTED_M,
        "class_counts": input_manifest["class_counts"]["control"],
        "design_plan": PLAN_REL, "design_sha256": source_hashes["plan"],
        "locked_method": {"path": LOCKED_METHOD_REL, "sha256": source_hashes["locked_method"]},
        "input_manifest": "INPUT_MANIFEST.json", "input_manifest_sha256": manifest_hash,
        "inputs": input_paths, "input_sha256": input_hashes,
        "common_m_manifest": input_manifest["common_m_manifest"],
        "output_directory": OUTPUT_REL,
        "output_role_source": {"path": ROLE_SOURCE_REL, "sha256": input_hashes["output_roles"]},
        "runtime_binding_path": RUNTIME_REL, "runtime_binding_sha256": runtime_hash, "runtime_binding": runtime,
        "runner": {"path": RUNNER_REL, "sha256": runner_hash, "status": "EXACT_FINAL_CARD_GUARDIAN_V2_BINDING"},
        "runner_binding": {"run_id": RUN_ID, "package_id": PACKAGE_REL.split("/")[-1],
                           "card_path": card_path_rel, "output_directory": OUTPUT_REL,
                           "consumption_directory": r02.MINIMAL3350_CONTROL_BINDING["consumption_directory"],
                           "kind": "PAIR_RUN"},
        "resource_limits": {"runtime_s": 90, "storage_bytes": 60_000_000,
                            "scope": RUN_ID, "status": "AUTHORIZED_FOR_THIS_RUN"},
        "authorization_record": {"authorization": AUTHORIZATION, "run_id": RUN_ID,
                                  "exact_card_path": card_path_rel, "max_starts": 1,
                                  "technical_retries": 0, "wallclock_stop_trigger_s": 90,
                                  "output_size_stop_trigger_bytes_decimal": 60_000_000,
                                  "output_polling_interval_ms": 100, "polling_overshoot_accepted": True,
                                  "prohibited_runs": ["treatment", "seed23", "B", "C", "other_qMain_qRamp"]},
        "execution_authorized": True, "approval_required": False, "max_starts": 1,
        "technical_retries": 0, "progression_allowed": False, "run_command": None,
        "guardian_request_binding": {"schema": "r02-start-v2", "request_path": f"{PACKAGE_REL}/START_REQUEST.json",
                                     "receipt_path": f"{PACKAGE_REL}/START_REQUEST_RECEIPT.json", "status": "PERSISTED_UNSENT"},
        "review_gate": {"required": ["engineering", "data_provenance", "scientific"],
                        "status": "PENDING_EXACT_CARD_REVIEWS"},
    }
    card_path = repo / card_path_rel
    _write_json(card_path, card)
    card_hash = sha256(card_path)

    # Build and persist an exact, unsent Guardian envelope for reviewer binding.
    reservation = repo / r02.MINIMAL3350_CONTROL_BINDING["consumption_directory"] / f"{RUN_ID}.json"
    role_data = json.loads((input_root / "output_roles.json").read_text(encoding="utf-8"))
    output = repo / OUTPUT_REL
    files = {"binary": Path(runtime["binary_path"]),
             "sumocfg": output / "scenario_control.sumocfg",
             "sumo_home": Path(runtime["sumo_home"]),
             "additional_schema": Path(runtime["additional_schema_path"]),
             "output_roles": role_data["required_xml_roles"],
             "output_role_source_sha256": input_hashes["output_roles"]}
    start = r02.build_guardian_start_spec(files, card, output, reservation, repo, RUN_ID,
                                          card_path=card_path, approved_card_sha256=card_hash)
    request_bytes = canonical_start_request_bytes(start, r02)
    (package / "START_REQUEST.json").write_bytes(request_bytes)
    request_hash = hashlib.sha256(request_bytes).hexdigest()
    receipt = {"schema": "r02_start_request_receipt_v1", "status": "PASS_PERSISTED_UNSENT",
               "run_id": RUN_ID, "card_sha256": card_hash, "request_sha256": request_hash,
               "dispatched": False, "guardian_started": False, "sumo_started": False}
    receipt_bytes = _write_json(package / "START_REQUEST_RECEIPT.json", receipt)

    return {"status": "CONTROL_PACKAGE_MATERIALIZED_REVIEW_PENDING", "run_id": RUN_ID,
            "card_path": card_path_rel, "card_sha256": card_hash,
            "demand_path": input_paths["demand"], "demand_sha256": input_hashes["demand"],
            "m_count": EXPECTED_M, "schedule_offset_ms": EXPECTED_OFFSET_MS,
            "last_depart_ms": (EXPECTED_M-1)*EXPECTED_OFFSET_MS,
            "speed_factor_source_sha256": source_hashes["source_vehroute"],
            "runner_sha256": runner_hash, "request_sha256": request_hash,
            "request_receipt_sha256": hashlib.sha256(receipt_bytes).hexdigest(),
            "outputs_absent": True, "output_binding": output_binding,
            "process_starts": {"guardian": 0, "sumo": 0, "traci": 0, "netconvert": 0}}


def main() -> int:
    raise SystemExit("Use the package generation command defined in the exact-card preparation receipt; this adapter is validation-only at runtime.")


if __name__ == "__main__":
    main()

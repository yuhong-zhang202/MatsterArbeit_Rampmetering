#!/usr/bin/env python3
"""Fail-closed offline binder for the Stage 6 minimal U=X=0 pair.

This module validates/materializes static inputs only. It has no simulator,
TraCI, netconvert, or process-launch code.
"""
from __future__ import annotations

import hashlib
import json
from decimal import Decimal
import re
import xml.etree.ElementTree as ET
from xml.parsers import expat
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[3]
PACKAGE = Path(__file__).resolve().parent / "prepared_rev3"
V5 = ROOT / "artifacts/stage6_pair_3199_matched_input_repair_20260923_v5"
PLAN = ROOT / "artifacts/stage6_minimal_ramp_induced_breakdown_existence_test_20260924_v1/PLAN.md"
LOCKED_METHOD = ROOT / "docs/methodology/FREEWAY_PROTECTABLE_STATE_EXPLORATORY_DEFINITION.md"
R04_ADAPTER = ROOT / "artifacts/stage6_ramp_induced_validation_20260922_v1/r04_adapter/ri3350_control_adapter.py"
NETWORK = ROOT / "artifacts/stage6_baseline_localization_20260921_v1/LOC_M3350_S17/engineering/build_attempts/TV_BUILD01/network.net.xml"
R02 = ROOT / "artifacts/stage6_ramp_induced_validation_20260922_v1/r02_single_start/runner.py"
OLD_RUNTIME = ROOT / "artifacts/stage6_pair_3199_s17_preparation_20260923_v1/runtime_bindings/PAIR_3199_CTRL_S17_FINAL_REV1.json"
V5_RECEIPT = V5 / "PROVENANCE_RECEIPT.json"

ATTRS = {"vType": {"id", "vClass"}, "route": {"id", "edges"},
         "vehicle": {"id", "type", "route", "depart", "departPos", "departLane", "departSpeed", "speedFactor"}}
XSI_SCHEMA = "{http://www.w3.org/2001/XMLSchema-instance}noNamespaceSchemaLocation"
EXPECTED_M = 1333
EXPECTED_R = 192
EXPECTED_R_DEPARTS_MS = [540_000 + i * 5_000 for i in range(EXPECTED_R)]


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1 << 20), b""):
            h.update(block)
    return h.hexdigest()


def dump(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def parse_routes(path: Path) -> tuple[dict[str, dict[str, str]], dict[str, dict[str, str]], dict[str, dict[str, str]]]:
    raw = path.read_bytes()
    if raw.startswith(b"\xef\xbb\xbf"):
        raise ValueError(f"UTF-8 BOM is unsupported in {path}")
    try:
        decoded = raw.decode("utf-8", errors="strict")
    except UnicodeDecodeError as exc:
        raise ValueError(f"route XML must be strict UTF-8 in {path}") from exc
    if "\x00" in decoded:
        raise ValueError(f"NUL characters are unsupported in route XML {path}")
    declaration = re.match(r"\s*<\?xml\s+[^?]*encoding\s*=\s*['\"]([^'\"]+)['\"]", decoded, re.IGNORECASE)
    if declaration and declaration.group(1).upper().replace("_", "-") not in {"UTF-8", "UTF8"}:
        raise ValueError(f"route XML declaration must specify UTF-8 in {path}")
    expat_parser = expat.ParserCreate(encoding="UTF-8")

    def reject(kind: str):
        def handler(*_args):
            raise ValueError(f"unsupported XML {kind} in {path}")
        return handler

    expat_parser.StartDoctypeDeclHandler = reject("DOCTYPE")
    expat_parser.EntityDeclHandler = reject("entity declaration")
    expat_parser.UnparsedEntityDeclHandler = reject("unparsed entity declaration")
    expat_parser.ExternalEntityRefHandler = reject("external entity")
    expat_parser.CommentHandler = reject("comment")
    expat_parser.ProcessingInstructionHandler = reject("processing instruction")
    try:
        expat_parser.Parse(raw, True)
    except ValueError:
        raise
    except expat.ExpatError as exc:
        raise ValueError(f"invalid or unsupported XML encoding/syntax in {path}: {exc}") from exc
    parser = ET.XMLParser(target=ET.TreeBuilder(insert_comments=True, insert_pis=True))
    root = ET.parse(path, parser=parser).getroot()
    if root.tag != "routes" or set(root.attrib) - {XSI_SCHEMA}:
        raise ValueError(f"unsupported route root or root attributes: {path}")
    vtypes: dict[str, dict[str, str]] = {}
    routes: dict[str, dict[str, str]] = {}
    vehicles: dict[str, dict[str, str]] = {}
    prior: tuple[int, str] | None = None
    for node in root:
        if not isinstance(node.tag, str) or node.tag not in ATTRS or set(node.attrib) != ATTRS[node.tag] or list(node):
            raise ValueError(f"unknown/malformed top-level node in {path}: {node.tag}")
        if (node.text and node.text.strip()) or (node.tail and node.tail.strip()):
            raise ValueError(f"unsupported mixed XML content in {path}: {node.tag}")
        a = dict(node.attrib)
        if node.tag == "vType":
            if a["id"] in vtypes:
                raise ValueError(f"duplicate vType {a['id']}")
            vtypes[a["id"]] = a
        elif node.tag == "route":
            if a["id"] in routes:
                raise ValueError(f"duplicate route {a['id']}")
            routes[a["id"]] = a
        else:
            vid = a["id"]
            if vid in vehicles:
                raise ValueError(f"duplicate vehicle {vid}")
            key = (int(Decimal(a["depart"]) * 1000), vid)
            if prior is not None and key < prior:
                raise ValueError(f"vehicle records are not globally sorted by (depart_ms,id): {path}")
            prior = key
            if a["route"] not in routes or a["type"] not in vtypes:
                raise ValueError(f"unresolved route/type for {vid}")
            vehicles[vid] = a
    return vtypes, routes, vehicles


def record_key(a: dict[str, str]) -> tuple[str, str, str, str, str, str, str, str]:
    return tuple(a[k] for k in ("id", "depart", "route", "type", "speedFactor", "departPos", "departLane", "departSpeed"))


def validate_pair(control: Path, treatment: Path, manifest: dict[str, Any], *,
                  runner: Path | None = None, output_paths: tuple[Path, Path] | None = None) -> dict[str, Any]:
    cv, cr, cm = parse_routes(control)
    tv, tr, tm = parse_routes(treatment)
    if cv != tv or cr != tr:
        raise ValueError("control/treatment route or vType definitions differ")
    m_c = {k: v for k, v in cm.items() if k.startswith("M_flow.")}
    m_t = {k: v for k, v in tm.items() if k.startswith("M_flow.")}
    expected_m_ids = {f"M_flow.{i}" for i in range(EXPECTED_M)}
    if len(m_c) != EXPECTED_M or len(m_t) != EXPECTED_M or set(m_c) != expected_m_ids or set(m_t) != expected_m_ids:
        raise ValueError("M counts or ID sets are not exactly matched at 1333")
    if any(record_key(m_c[k]) != record_key(m_t[k]) for k in m_c):
        raise ValueError("M identity/depart/route/type/speedFactor/depart parameters differ")
    r_c = {k for k in cm if k.startswith("R_flow.")}
    r_t = {k for k in tm if k.startswith("R_flow.")}
    non_m_c = set(cm) - set(m_c)
    non_m_t = set(tm) - set(m_t)
    if r_c or non_m_c:
        raise ValueError("control contains non-M demand; R must be explicitly zero and U/X absent")
    expected_r_ids = {f"R_flow.{i}" for i in range(EXPECTED_R)}
    if non_m_t != r_t or r_t != expected_r_ids:
        raise ValueError("treatment-only identities must be exactly R_flow.0..191")
    r_depart_ms = [round(float(tm[f"R_flow.{i}"]["depart"]) * 1000) for i in range(EXPECTED_R)]
    if r_depart_ms != EXPECTED_R_DEPARTS_MS:
        raise ValueError("R schedule is not exactly 540..1495 s in 5 s increments")

    classes = manifest.get("class_counts")
    for arm in ("control", "treatment"):
        if not isinstance(classes, dict) or arm not in classes:
            raise ValueError(f"explicit class ledger missing for {arm}")
        for cls, expected in (("U", 0), ("X", 0)):
            entry = classes[arm].get(cls)
            if not isinstance(entry, dict) or entry.get("status") != "PASS_ZERO" or entry.get("planned_count") != expected:
                raise ValueError(f"{arm} {cls} must be explicitly PASS_ZERO; missing is invalid")
    if classes["control"].get("R") != {"planned_count": 0, "status": "PASS_ZERO"}:
        raise ValueError("control R must be explicitly PASS_ZERO")
    if classes["treatment"].get("R", {}).get("planned_count") != EXPECTED_R:
        raise ValueError("treatment R planned count is not explicitly 192")

    if runner is not None:
        bound = manifest.get("runner", {})
        if not runner.is_file() or bound.get("path") != str(runner.relative_to(ROOT)) or bound.get("sha256") != sha256(runner):
            raise ValueError("runner path/hash provenance mismatch")
        runner_text = runner.read_text(encoding="utf-8")
        for run_id in ("MINIMAL3199_CTRL_S17", "MINIMAL3199_R720_DELAYED_S17"):
            if run_id not in runner_text:
                raise ValueError(f"runner does not explicitly allowlist {run_id}")
    if output_paths is not None:
        for arm_path in output_paths:
            if arm_path.exists():
                raise FileExistsError(f"output path already exists: {arm_path}")
    return {"status": "PASS_STATIC_PAIR_INPUTS", "m_count": len(m_c), "m_matches": len(m_c),
            "control_r_count": len(r_c), "treatment_r_count": len(r_t),
            "u_x_explicit_zero_both_arms": True,
            "m_attributes_checked": ["id", "desired_depart", "route", "vType", "speedFactor", "departPos", "departLane", "departSpeed"],
            "treatment_only_difference": "R_flow.0..191"}


def validate_file_bindings(root: Path, manifest: dict[str, Any], cards: dict[str, dict[str, Any]],
                           runtime: dict[str, Any], *, runner_path: Path,
                           output_paths: tuple[Path, Path]) -> dict[str, Any]:
    """Validate exact static hashes and refuse stale/mismatched execution binding."""
    errors: list[str] = []
    for arm, card in cards.items():
        if card.get("card_status") != "DRAFT_NOT_AUTHORIZED" or card.get("execution_authorized") is not False or card.get("run_command") is not None:
            errors.append(f"{arm}: draft/no-launch invariant failed")
        if card.get("run_id") != manifest.get("run_ids", {}).get(arm):
            errors.append(f"{arm}: card/run ID mismatch")
        if card.get("output_directory") != manifest.get("outputs", {}).get(arm):
            errors.append(f"{arm}: output path mismatch")
        for key, binding in manifest.get("arm_inputs", {}).get(arm, {}).items():
            path = root / binding["path"]
            if not path.is_file() or sha256(path) != binding["sha256"]:
                errors.append(f"{arm}: input hash mismatch: {key}")
            if card.get("input_sha256", {}).get(key) != binding["sha256"]:
                errors.append(f"{arm}: card hash mismatch: {key}")
        if any(path.exists() for path in output_paths):
            errors.append("output path collision")
    runner_binding = manifest.get("runner", {})
    actual_runner_sha = sha256(runner_path) if runner_path.is_file() else None
    if (runner_binding.get("path") != str(runner_path.relative_to(root))
            or runner_binding.get("sha256") != actual_runner_sha):
        errors.append("runner path/hash mismatch")
    runner_text = runner_path.read_text(encoding="utf-8") if runner_path.is_file() else ""
    for run_id in manifest.get("run_ids", {}).values():
        if run_id not in runner_text:
            errors.append(f"runner has no exact binding for {run_id}")
    if runtime.get("freshness_status") != "CURRENT_EXACT_CARD_READONLY_VERIFIED":
        errors.append("runtime evidence is historical or freshness unknown")
    ref = runtime.get("reference_path")
    ref_path = root / ref if isinstance(ref, str) else None
    if not ref_path or not ref_path.is_file() or runtime.get("reference_sha256") != sha256(ref_path):
        errors.append("runtime reference hash/path mismatch")
    if runtime.get("guardian_runner_sha256") != actual_runner_sha:
        errors.append("runtime Guardian runner hash differs from current runner")
    if errors:
        raise ValueError("; ".join(errors))
    return {"status": "PASS_STATIC_BINDINGS", "runner_sha256": actual_runner_sha,
            "runtime_freshness": runtime["freshness_status"], "outputs_absent": True}


def materialize() -> dict[str, Any]:
    if PACKAGE.exists():
        raise FileExistsError(f"refusing to overwrite {PACKAGE}")
    receipt = json.loads(V5_RECEIPT.read_text(encoding="utf-8"))
    for rel, digest in receipt["package_files"].items():
        path = ROOT / "artifacts/stage6_pair_3199_matched_input_repair_20260923_v5" / rel
        if sha256(path) != digest:
            raise ValueError(f"v5 source package hash mismatch: {rel}")
    manifest_v5 = json.loads((V5 / "COMMON_DEMAND_MANIFEST.json").read_text(encoding="utf-8"))
    shared = manifest_v5["shared_vehicle_records"]
    m_records = [v for k, v in shared.items() if k.startswith("M_flow.")]
    r_records = list(manifest_v5["treatment_only_vehicle_records"].values())
    if len(m_records) != EXPECTED_M or len(r_records) != EXPECTED_R:
        raise ValueError("reviewed v5 materialized counts differ from expected pair")
    source_control = ET.parse(V5 / "control/demand.rou.xml").getroot()
    vtype_nodes = [node for node in source_control if node.tag == "vType"]
    route_nodes = [node for node in source_control if node.tag == "route"]
    for arm, records in (("control", m_records), ("treatment", m_records + r_records)):
        root = ET.Element("routes", {"xmlns:xsi": "http://www.w3.org/2001/XMLSchema-instance",
                                      "xsi:noNamespaceSchemaLocation": "http://sumo.dlr.de/xsd/routes_file.xsd"})
        for node in vtype_nodes + route_nodes:
            root.append(ET.fromstring(ET.tostring(node)))
        for rec in sorted(records, key=lambda x: (int(x["depart_ms"]), x["id"])):
            attrs = {k: rec[k] for k in ("id", "type", "route", "departPos", "departLane", "departSpeed", "speedFactor")}
            attrs["depart"] = f"{int(rec['depart_ms']) // 1000}.{int(rec['depart_ms']) % 1000:03d}"
            ET.SubElement(root, "vehicle", attrs)
        ET.indent(root, space="  ")
        out = PACKAGE / arm / "demand.rou.xml"
        out.parent.mkdir(parents=True, exist_ok=True)
        ET.ElementTree(root).write(out, encoding="utf-8", xml_declaration=True)

    output_root = ROOT / "data/raw/stage6_minimal3199_existence_20260924_v1"
    output_roles_source = ROOT / "artifacts/stage6_pair_3199_s17_preparation_20260923_v1/inputs/control/output_roles.json"
    add_source = ROOT / "artifacts/stage6_pair_3199_s17_preparation_20260923_v1/inputs/control/scenario.add.xml"
    design_sha = sha256(PLAN)
    manifest: dict[str, Any] = {
        "schema_version": "1", "status": "DRAFT_INPUTS_NOT_AUTHORIZED", "execution_authorized": False,
        "pair_id": "MINIMAL3199_UX0_S17",
        "run_ids": {"control": "MINIMAL3199_CTRL_S17", "treatment": "MINIMAL3199_R720_DELAYED_S17"},
        "design_path": str(PLAN.relative_to(ROOT)), "design_plan_sha256": design_sha,
        "runner_path": str(R02.relative_to(ROOT)), "runner_sha256": sha256(R02),
        "validation_code": {
            "adapter": {"path": str(Path(__file__).resolve().relative_to(ROOT)), "sha256": sha256(Path(__file__).resolve())},
            "regression_tests": {"path": str((ROOT / "tests/test_minimal3199_adapter.py").relative_to(ROOT)),
                                 "sha256": sha256(ROOT / "tests/test_minimal3199_adapter.py")},
        },
        "locked_method": {"path": str(LOCKED_METHOD.relative_to(ROOT)), "sha256": sha256(LOCKED_METHOD)},
        "locked_R04_reference": {"path": str(R04_ADAPTER.relative_to(ROOT)), "sha256": sha256(R04_ADAPTER),
                                  "status": "HASH_BOUND_REFERENCE_ONLY_NOT_ADAPTED_OR_EXECUTED"},
        "fixed_conditions": {"qMain_veh_per_h": 3199.2, "seed": 17, "U": 0, "X": 0,
                             "qRamp_veh_per_h": {"control": 0, "treatment": 720},
                             "R_window_s": "[540,1500)", "A": "A_OPEN", "horizon_s": 2700, "step_s": 1},
        "class_counts": {
            "control": {"M": {"planned_count": EXPECTED_M, "status": "BOUND"},
                        "R": {"planned_count": 0, "status": "PASS_ZERO"},
                        "U": {"planned_count": 0, "status": "PASS_ZERO"},
                        "X": {"planned_count": 0, "status": "PASS_ZERO"}},
            "treatment": {"M": {"planned_count": EXPECTED_M, "status": "BOUND"},
                          "R": {"planned_count": EXPECTED_R, "status": "BOUND"},
                          "U": {"planned_count": 0, "status": "PASS_ZERO"},
                          "X": {"planned_count": 0, "status": "PASS_ZERO"}}},
        "source_hashes": {"v5_receipt": sha256(V5_RECEIPT), "v5_manifest": sha256(V5 / "COMMON_DEMAND_MANIFEST.json"),
                          "network": sha256(NETWORK), "plan": design_sha, "additional_template": sha256(add_source),
                          "output_roles_template": sha256(output_roles_source)},
        "runner": {"path": str(R02.relative_to(ROOT)), "sha256": sha256(R02),
                   "status": "EXACT_CARD_PRELAUNCH_BINDING_PRESENT_LAUNCH_BLOCKED_BY_DRAFT_STATUS"},
        "runtime": {"reference_path": str(OLD_RUNTIME.relative_to(ROOT)), "reference_sha256": sha256(OLD_RUNTIME),
                    "status": "READONLY_HOST_HASHES_VERIFIED_VERSION_EVIDENCE_PRIOR_PROBE_NO_SIMULATOR_PROCESS"},
        "outputs": {arm: str((output_root / run_id / "outputs").relative_to(ROOT))
                    for arm, run_id in (("control", "MINIMAL3199_CTRL_S17"),
                                        ("treatment", "MINIMAL3199_R720_DELAYED_S17"))},
        "source_vehicle_records": {"M_source": "reviewed v5 COMMON_DEMAND_MANIFEST.shared_vehicle_records", 
                                   "R_source": "reviewed v5 COMMON_DEMAND_MANIFEST.treatment_only_vehicle_records",
                                   "materialization": "explicit per-vehicle records globally sorted by integer depart_ms then id; no randomized flow expansion"},
        "authorization": {"execution_authorized": False, "max_starts": 0, "technical_retries": 0,
                          "run_command": None}
    }
    for arm in ("control", "treatment"):
        input_dir = PACKAGE / arm
        # Bind the immutable accepted network by absolute path in a run-local SUMO config.
        cfg = ET.Element("sumoConfiguration")
        inp = ET.SubElement(cfg, "input")
        ET.SubElement(inp, "net-file", {"value": str(NETWORK)})
        ET.SubElement(inp, "route-files", {"value": str(input_dir / "demand.rou.xml")})
        ET.SubElement(inp, "additional-files", {"value": str(input_dir / "scenario.add.xml")})
        time = ET.SubElement(cfg, "time")
        ET.SubElement(time, "begin", {"value": "0"}); ET.SubElement(time, "end", {"value": "2700"}); ET.SubElement(time, "step-length", {"value": "1"})
        processing = ET.SubElement(cfg, "processing")
        for name, value in (("time-to-teleport", "-1"), ("collision.action", "warn"), ("collision.check-junctions", "true"), ("extrapolate-departpos", "false")):
            ET.SubElement(processing, name, {"value": value})
        out = ET.SubElement(cfg, "output")
        files = {"fcd-output": "fcd.xml", "queue-output": "queues.xml", "summary-output": "sumo_summary.xml",
                 "tripinfo-output": "tripinfo.xml", "vehroute-output": "vehroute.xml", "lanechange-output": "lanechanges.xml"}
        for attr, leaf in files.items(): ET.SubElement(out, attr, {"value": str(ROOT / manifest["outputs"][arm] / leaf)})
        for attr, value in (("tripinfo-output.write-unfinished", "true"), ("vehroute-output.write-unfinished", "true"),
                            ("precision", "2"), ("tripinfo-output.write-undeparted", "true")):
            ET.SubElement(out, attr, {"value": value})
        rng = ET.SubElement(cfg, "random_number"); ET.SubElement(rng, "seed", {"value": "17"})
        report = ET.SubElement(cfg, "report")
        ET.SubElement(report, "log", {"value": str(ROOT / manifest["outputs"][arm] / "sumo.log")})
        ET.SubElement(report, "error-log", {"value": str(ROOT / manifest["outputs"][arm] / "sumo_error.log")})
        ET.SubElement(report, "no-step-log", {"value": "true"}); ET.SubElement(report, "xml-validation", {"value": "always"})
        ET.indent(cfg, space="  "); ET.ElementTree(cfg).write(input_dir / "scenario.sumocfg", encoding="utf-8", xml_declaration=True)

        add_root = ET.parse(add_source).getroot()
        for node in list(add_root):
            if "file" in node.attrib:
                node.set("file", str(ROOT / manifest["outputs"][arm] / Path(node.attrib["file"]).name))
            if "dest" in node.attrib:
                node.set("dest", str(ROOT / manifest["outputs"][arm] / Path(node.attrib["dest"]).name))
        ET.indent(add_root, space="  "); ET.ElementTree(add_root).write(input_dir / "scenario.add.xml", encoding="utf-8", xml_declaration=True)
        roles = json.loads(output_roles_source.read_text(encoding="utf-8"))
        for row in roles["required_xml_roles"]:
            row["path"] = str(output_root / manifest["run_ids"][arm] / "outputs" / Path(row["path"]).name)
        dump(input_dir / "output_roles.json", roles)
        manifest.setdefault("arm_inputs", {})[arm] = {
            "path_prefix": arm,
            "demand": {"path": f"{arm}/demand.rou.xml", "sha256": sha256(input_dir / "demand.rou.xml")},
            "sumocfg": {"path": f"{arm}/scenario.sumocfg", "sha256": sha256(input_dir / "scenario.sumocfg")},
            "additional": {"path": f"{arm}/scenario.add.xml", "sha256": sha256(input_dir / "scenario.add.xml")},
            "output_roles": {"path": f"{arm}/output_roles.json", "sha256": sha256(input_dir / "output_roles.json")},
            "network": {"path": str(NETWORK.relative_to(ROOT)), "sha256": sha256(NETWORK)}}

        dump(PACKAGE / "INPUT_MANIFEST.json", manifest)
    old_runtime = json.loads(OLD_RUNTIME.read_text(encoding="utf-8"))
    current_runner_sha = sha256(R02)
    for arm in ("control", "treatment"):
        run_id = manifest["run_ids"][arm]
        runtime_copy = json.loads(json.dumps(old_runtime))
        output_limit = 60_000_000 if arm == "control" else 75_000_000
        runtime_copy.update({"guardian_runner_sha256": current_runner_sha,
                             "max_runtime_s": 90, "max_output_bytes": output_limit})
        runtime_copy["resource_proposal"] = {"status": "PROPOSED_NOT_AUTHORIZED", "scope": run_id,
            "wallclock_stop_limit_s": 90, "output_size_stop_limit_bytes_decimal": output_limit,
            "poll_interval_s": 0.1, "overshoot_accepted": True,
            "enforcement": "100ms_polled_stop_trigger_with_possible_overshoot_not_hard_quota",
            "basis": "proposal only; prior full-horizon control observed 24.881003 s and 20,821,740 bytes; prior treatment observed 24.370309 s and 23,936,627 bytes; new U=X0 output sizes unobserved"}
        runtime_copy["runtime_provenance_status"] = "READONLY_PATH_AND_HASH_VERIFIED_NO_SUMO_VERSION_PROCESS"
        runtime_path = PACKAGE / arm / "runtime_binding.json"
        dump(runtime_path, runtime_copy)
        role_path = PACKAGE / arm / "output_roles.json"
        run_binding = {"run_id": run_id, "package_id": "MINIMAL3199_UX0_S17_PREPARATION_REV3",
                       "card_path": str((PACKAGE / f"{run_id}_CARD_DRAFT_NOT_AUTHORIZED_REV3.json").relative_to(ROOT)),
                       "output_directory": manifest["outputs"][arm], "consumption_directory": "scripts/stage6/minimal3199/consumption",
                       "kind": "MINIMAL3199_DRAFT"}
        card = {"schema_version": "1", "card_revision": 3, "run_id": run_id, "pair_id": "MINIMAL3199_UX0_S17",
                "condition": "A_OPEN_R0_CONTROL" if arm == "control" else "A_OPEN_R720_DELAYED_TREATMENT",
                "card_status": "DRAFT_NOT_AUTHORIZED", "execution_authorized": False, "approval_required": True, "max_starts": 1,
                "technical_retries": 0, "run_command": None, "qMain_veh_per_h": 3199.2, "seed": 17,
                "U": 0, "X": 0, "R_veh_per_h": 0 if arm == "control" else 720,
                "R_window_s": "NO_R_SOURCE" if arm == "control" else "[540,1500)", "TLS_program": "A_OPEN",
                "horizon_s": 2700, "step_s": 1, "design_plan": str(PLAN.relative_to(ROOT)), "design_sha256": design_sha,
                "input_manifest": "INPUT_MANIFEST.json",
                "input_manifest_sha256": sha256(PACKAGE / "INPUT_MANIFEST.json"),
                "inputs": {k: v["path"] for k, v in manifest["arm_inputs"][arm].items() if k != "path_prefix"},
                "input_sha256": {k: v["sha256"] for k, v in manifest["arm_inputs"][arm].items() if k != "path_prefix"},
                "output_directory": manifest["outputs"][arm],
                "runtime_binding_path": str(runtime_path.relative_to(ROOT)),
                "runtime_binding_sha256": sha256(runtime_path), "runtime_binding": runtime_copy,
                "runner": manifest["runner"],
                "runner_binding": run_binding,
                "resource_limits": {"status": "PROPOSED_NOT_AUTHORIZED", "scope": run_id,
                                    "runtime_s": 90, "storage_bytes": output_limit},
                "output_role_source": {"path": str(role_path.relative_to(ROOT)), "sha256": sha256(role_path)},
                "scope_prohibitions": ["No SUMO/netconvert/TraCI before separate authorization", "No other qMain/qRamp/seed/controller",
                                       "No scientific-input, geometry, classifier, threshold, or vehicle-behavior changes"],
                "prelaunch_disposition": "DRAFT_NOT_AUTHORIZED_RUNNER_WILL_REFUSE_LAUNCH",
                "note": "Exact offline input card draft only; does not authorize execution."}
        dump(PACKAGE / f"{run_id}_CARD_DRAFT_NOT_AUTHORIZED_REV3.json", card)
    control, treatment = PACKAGE / "control/demand.rou.xml", PACKAGE / "treatment/demand.rou.xml"
    report = validate_pair(control, treatment, manifest, output_paths=tuple(ROOT / p for p in manifest["outputs"].values()))
    dump(PACKAGE / "STATIC_INVARIANT_REPORT.json", report)
    files = {p.relative_to(PACKAGE).as_posix(): sha256(p) for p in sorted(PACKAGE.rglob("*")) if p.is_file() and p.name != "PROVENANCE_RECEIPT.json"}
    dump(PACKAGE / "PROVENANCE_RECEIPT.json", {"status": "DRAFT_NOT_AUTHORIZED", "files": files,
          "sumo_starts": 0, "traci_starts": 0, "netconvert_starts": 0})
    return report


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--materialize", action="store_true")
    args = parser.parse_args()
    if args.materialize:
        print(json.dumps(materialize(), indent=2, sort_keys=True))

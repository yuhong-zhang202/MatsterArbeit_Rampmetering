#!/usr/bin/env python3
"""Offline PAIR3199 common-demand materializer and fail-closed invariant checker.

This module never starts SUMO. It materializes shared M/U/X vehicles from the
approved flow definitions and the existing control's realized speedFactors.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import xml.etree.ElementTree as ET
from xml.parsers import expat
from decimal import Decimal
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
PREP = ROOT / "artifacts/stage6_pair_3199_s17_preparation_20260923_v1"
OUT = ROOT / "artifacts/stage6_pair_3199_matched_input_repair_20260923_v5"
CONTROL_ROUTES = PREP / "inputs/control/demand.rou.xml"
TREATMENT_ROUTES = PREP / "inputs/treatment/demand.rou.xml"
CONTROL_VEHROUTE = ROOT / "data/raw/stage6_bounded_pair_20260923_v1/PAIR_3199_CTRL_S17/outputs/vehroute.xml"
TREATMENT_VEHROUTE = ROOT / "data/raw/stage6_bounded_pair_20260923_v1/PAIR_3199_R720_DELAYED_S17/outputs/vehroute.xml"
NETWORK = ROOT / "artifacts/stage6_baseline_localization_20260921_v1/LOC_M3350_S17/engineering/build_attempts/TV_BUILD01/network.net.xml"
CLASSES = ("M", "U", "X")
EXPECTED = {"M": 1333, "U": 150, "X": 75, "R": 192}
XSI_SCHEMA_LOCATION = "{http://www.w3.org/2001/XMLSchema-instance}noNamespaceSchemaLocation"
ROOT_ATTRIBUTES = {XSI_SCHEMA_LOCATION}
NODE_ATTRIBUTES = {
    "vType": {"id", "vClass"},
    "route": {"id", "edges"},
    "vehicle": {"id", "type", "route", "depart", "departPos", "departLane", "departSpeed", "speedFactor"},
}


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def ms_text(ms: int) -> str:
    return f"{ms // 1000}.{ms % 1000:03d}"


def parse_flow_schedule(flow: ET.Element) -> list[int]:
    begin = int(Decimal(flow.attrib["begin"]) * 1000)
    end = int(Decimal(flow.attrib["end"]) * 1000)
    number = int(flow.attrib["number"])
    if number <= 0 or end < begin:
        raise ValueError(f"invalid flow interval/count: {flow.attrib}")
    offset = (end - begin) // number
    return [begin + i * offset for i in range(number)]


def realized_speed_factors(path: Path, expected_ids: set[str]) -> dict[str, str]:
    root = ET.parse(path).getroot()
    records: dict[str, str] = {}
    for node in root.findall("vehicle"):
        vid = node.get("id")
        if vid in expected_ids:
            sf = node.get("speedFactor")
            if sf is None:
                raise ValueError(f"speedFactor absent for {vid} in {path}")
            if vid in records:
                raise ValueError(f"duplicate tripinfo identity {vid} in {path}")
            records[vid] = sf
    missing = expected_ids - records.keys()
    extra = records.keys() - expected_ids
    if missing or extra:
        raise ValueError(f"tripinfo IDs differ; missing={len(missing)}, extra={len(extra)}")
    return records


def source_definitions(control_path: Path) -> tuple[dict[str, ET.Element], dict[str, ET.Element], dict[str, ET.Element]]:
    root = ET.parse(control_path).getroot()
    vtypes = {x.attrib["id"]: x for x in root.findall("vType")}
    routes = {x.attrib["id"]: x for x in root.findall("route")}
    flows = {x.attrib["id"]: x for x in root.findall("flow")}
    if not all(x in flows for x in ("M_flow", "U_flow", "X_flow")):
        raise ValueError("control source flow definitions are incomplete")
    return vtypes, routes, flows


def definition_attributes(nodes: dict[str, ET.Element]) -> dict[str, dict[str, str]]:
    return {ident: dict(node.attrib) for ident, node in nodes.items()}


def validate_safe_xml_bytes(raw: bytes, path: Path) -> None:
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

    parser = expat.ParserCreate(encoding="UTF-8")

    def reject(kind: str):
        def handler(*_args):
            raise ValueError(f"unsupported XML {kind} in {path}")
        return handler

    parser.StartDoctypeDeclHandler = reject("DOCTYPE")
    parser.EntityDeclHandler = reject("entity declaration")
    parser.UnparsedEntityDeclHandler = reject("unparsed entity declaration")
    parser.ExternalEntityRefHandler = reject("external entity")
    parser.CommentHandler = reject("comment")
    parser.ProcessingInstructionHandler = reject("processing instruction")
    try:
        parser.Parse(raw, True)
    except ValueError:
        raise
    except expat.ExpatError as exc:
        raise ValueError(f"invalid or unsupported XML encoding/syntax in {path}: {exc}") from exc


def materialize() -> dict[str, Any]:
    if OUT.exists():
        raise FileExistsError(f"refusing to overwrite existing package: {OUT}")
    vtypes, routes, control_flows = source_definitions(CONTROL_ROUTES)
    treatment_vtypes, treatment_routes, treatment_flows = source_definitions(TREATMENT_ROUTES)
    if definition_attributes(vtypes) != definition_attributes(treatment_vtypes):
        raise ValueError("source vType definitions differ between existing control and treatment inputs")
    if definition_attributes(routes) != definition_attributes(treatment_routes):
        raise ValueError("source route definitions, including edge lists, differ between existing control and treatment inputs")
    base_records: dict[str, dict[str, str]] = {}
    class_sched: dict[str, list[int]] = {}
    for cls in CLASSES:
        flow = control_flows[f"{cls}_flow"]
        sched = parse_flow_schedule(flow)
        class_sched[cls] = sched
        ids = {f"{cls}_flow.{i}" for i in range(len(sched))}
        sf_map = realized_speed_factors(CONTROL_VEHROUTE, ids)
        for i, depart_ms in enumerate(sched):
            vid = f"{cls}_flow.{i}"
            base_records[vid] = {
                "id": vid,
                "class": cls,
                "depart_ms": str(depart_ms),
                "route": flow.attrib["route"],
                "type": flow.attrib["type"],
                "speedFactor": sf_map[vid],
                "departPos": flow.attrib["departPos"],
                "departLane": flow.attrib["departLane"],
                "departSpeed": flow.attrib["departSpeed"],
            }

    treatment_r_flow = treatment_flows.get("R_flow")
    if treatment_r_flow is None:
        raise ValueError("treatment R_flow is missing")
    r_sched = parse_flow_schedule(treatment_r_flow)
    r_ids = {f"R_flow.{i}" for i in range(len(r_sched))}
    r_speed = realized_speed_factors(TREATMENT_VEHROUTE, r_ids)
    r_records: dict[str, dict[str, str]] = {}
    for i, depart_ms in enumerate(r_sched):
        vid = f"R_flow.{i}"
        r_records[vid] = {
            "id": vid,
            "class": "R",
            "depart_ms": str(depart_ms),
            "route": treatment_r_flow.attrib["route"],
            "type": treatment_r_flow.attrib["type"],
            "speedFactor": r_speed[vid],
            "departPos": treatment_r_flow.attrib["departPos"],
            "departLane": treatment_r_flow.attrib["departLane"],
            "departSpeed": treatment_r_flow.attrib["departSpeed"],
        }

    # Embed the source vType and route definitions; no route/network is changed.
    OUT.mkdir(parents=True)
    (OUT / "control").mkdir()
    (OUT / "treatment").mkdir()
    for arm, extras in (("control", {}), ("treatment", r_records)):
        root = ET.Element("routes", {"xmlns:xsi": "http://www.w3.org/2001/XMLSchema-instance",
                                      "xsi:noNamespaceSchemaLocation": "http://sumo.dlr.de/xsd/routes_file.xsd"})
        for node in vtypes.values():
            root.append(ET.fromstring(ET.tostring(node)))
        for node in routes.values():
            root.append(ET.fromstring(ET.tostring(node)))
        records = list(base_records.values()) + list(extras.values())
        records.sort(key=lambda rec: (int(rec["depart_ms"]), rec["id"]))
        for rec in records:
            attrs = {k: rec[k] for k in ("id", "type", "route", "departPos", "departLane", "departSpeed", "speedFactor")}
            attrs["depart"] = ms_text(int(rec["depart_ms"]))
            ET.SubElement(root, "vehicle", attrs)
        ET.indent(root, space="  ")
        ET.ElementTree(root).write(OUT / arm / "demand.rou.xml", encoding="utf-8", xml_declaration=True)

    manifest = {
        "schema_version": "1",
        "status": "REPAIRED_INPUTS_NOT_AUTHORIZED",
        "run_authorization": "NONE",
        "sumo_starts": 0,
        "input_sources": {
            "control_demand": {"path": str(CONTROL_ROUTES.relative_to(ROOT)), "sha256": sha256(CONTROL_ROUTES)},
            "treatment_demand": {"path": str(TREATMENT_ROUTES.relative_to(ROOT)), "sha256": sha256(TREATMENT_ROUTES)},
            "control_vehroute": {"path": str(CONTROL_VEHROUTE.relative_to(ROOT)), "sha256": sha256(CONTROL_VEHROUTE)},
            "treatment_vehroute_for_R_attributes_only": {"path": str(TREATMENT_VEHROUTE.relative_to(ROOT)), "sha256": sha256(TREATMENT_VEHROUTE)},
            "network_reference": {"path": str(NETWORK.relative_to(ROOT)), "sha256": sha256(NETWORK)},
        },
        "method": {
            "schedule": "SUMO 1.26 integer milliseconds: begin_ms + index * ((end_ms - begin_ms) // number)",
            "common_speedFactor": "materialized per identity from existing control vehroute; precise lexical values preserved (tripinfo rounding is not used)",
            "R_speedFactor": "materialized from existing treatment vehroute only for R IDs; no treatment outcomes interpreted",
            "attributes": "identity, desired depart, route, type, speedFactor, departPos, departLane, departSpeed",
            "sort_order": "all vehicle records globally sorted by (depart_ms, id)",
        },
        "counts": {"control": {"M": 1333, "U": 150, "X": 75, "R": 0},
                   "treatment": {"M": 1333, "U": 150, "X": 75, "R": 192}},
        "schedule_offsets_ms": {"M": 1125, "U": 10000, "X": 20000, "R": 5000},
        "shared_vehicle_records": base_records,
        "treatment_only_vehicle_records": r_records,
        "control_output": "control/demand.rou.xml",
        "treatment_output": "treatment/demand.rou.xml",
    }
    (OUT / "COMMON_DEMAND_MANIFEST.json").write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n")
    # Include direct hash bindings for every package payload, excluding receipt itself.
    receipt = {p.relative_to(OUT).as_posix(): sha256(p) for p in sorted(OUT.rglob("*")) if p.is_file()}
    (OUT / "PROVENANCE_RECEIPT.json").write_text(json.dumps({"files": receipt}, indent=2, sort_keys=True) + "\n")
    return check_pair(OUT / "control/demand.rou.xml", OUT / "treatment/demand.rou.xml")


def parse_materialized(path: Path) -> tuple[dict[str, dict[str, str]], dict[str, dict[str, str]], dict[str, dict[str, str]]]:
    raw = path.read_bytes()
    validate_safe_xml_bytes(raw, path)
    parser = ET.XMLParser(target=ET.TreeBuilder(insert_comments=True, insert_pis=True))
    root = ET.parse(path, parser=parser).getroot()
    if root.tag != "routes":
        raise ValueError(f"unexpected root element in {path}: {root.tag}")
    unknown_root_attributes = set(root.attrib) - ROOT_ATTRIBUTES
    if unknown_root_attributes:
        raise ValueError(f"unsupported root attributes in {path}: {sorted(unknown_root_attributes)}")
    if root.text and root.text.strip():
        raise ValueError(f"unsupported root text in {path}")
    vtypes: dict[str, dict[str, str]] = {}
    routes: dict[str, dict[str, str]] = {}
    out: dict[str, dict[str, str]] = {}
    last = (-1, "")
    for node in root:
        tag = node.tag
        if not isinstance(tag, str) or tag not in NODE_ATTRIBUTES:
            raise ValueError(f"unsupported top-level XML node in {path}: {tag}")
        if set(node.attrib) != NODE_ATTRIBUTES[tag]:
            missing = NODE_ATTRIBUTES[tag] - set(node.attrib)
            extra = set(node.attrib) - NODE_ATTRIBUTES[tag]
            raise ValueError(f"missing required or unsupported {tag} attributes in {path}: missing={sorted(missing)}, extra={sorted(extra)}")
        if list(node):
            raise ValueError(f"nested XML elements under {tag} are unsupported in {path}")
        if node.text and node.text.strip():
            raise ValueError(f"unsupported text inside {tag} in {path}")
        if node.tail and node.tail.strip():
            raise ValueError(f"unsupported mixed content after {tag} in {path}")
        if tag in ("vType", "route"):
            ident = node.get("id")
            target = vtypes if tag == "vType" else routes
            if not ident or ident in target:
                raise ValueError(f"missing or duplicate {tag} ID in {path}: {ident}")
            target[ident] = dict(node.attrib)
            continue
        a = node.attrib
        if a.get("type") not in vtypes or a.get("route") not in routes:
            raise ValueError(f"unresolved type/route for {a.get('id')} in {path}")
        if "speedFactor" not in a:
            raise ValueError(f"missing explicit speedFactor for {a.get('id')}")
        try:
            depart_ms = int(Decimal(a["depart"]) * 1000)
        except Exception as exc:
            raise ValueError(f"invalid departure time for {a.get('id')} in {path}") from exc
        key = (depart_ms, a.get("id", ""))
        if key < last:
            raise ValueError(f"route file not sorted by departure: {a.get('id')}")
        last = key
        if not a.get("id") or a["id"] in out:
            raise ValueError(f"missing or duplicate vehicle ID in {path}: {a.get('id')}")
        out[a["id"]] = {**a, "depart_ms": str(depart_ms)}
    if not vtypes or not routes:
        raise ValueError(f"vehicle inputs require at least one vType and route definition in {path}")
    if not root.text and len(root) == 0:
        raise ValueError(f"empty route file {path}")
    # Also reject hidden comments or processing instructions after the root's last child.
    if root.tail and root.tail.strip():
        raise ValueError(f"unsupported trailing text in {path}")
    return out, routes, vtypes


def check_pair(control_path: Path, treatment_path: Path) -> dict[str, Any]:
    control, control_routes, control_vtypes = parse_materialized(control_path)
    treatment, treatment_routes, treatment_vtypes = parse_materialized(treatment_path)
    shared_expected = {f"{c}_flow.{i}" for c in CLASSES for i in range(EXPECTED[c])}
    control_ids = set(control)
    treatment_ids = set(treatment)
    failures: list[str] = []
    if control_ids != shared_expected:
        failures.append("control M/U/X ID set differs from fixed expected set")
    if treatment_ids & shared_expected != shared_expected:
        failures.append("treatment is missing common M/U/X IDs")
    shared_diffs = [vid for vid in sorted(shared_expected) if control.get(vid) != treatment.get(vid)]
    if shared_diffs:
        failures.append("one or more common vehicle attributes differ")
    route_definitions_match = control_routes == treatment_routes
    if not route_definitions_match:
        failures.append("complete route definitions (including edge lists and all attributes) differ across arms")
    vtype_definitions_match = control_vtypes == treatment_vtypes
    if not vtype_definitions_match:
        failures.append("complete vType definitions (including all attributes) differ across arms")
    treatment_only = treatment_ids - control_ids
    control_only = control_ids - treatment_ids
    expected_r = {f"R_flow.{i}" for i in range(EXPECTED["R"])}
    if treatment_only != expected_r:
        failures.append("treatment-only identity set is not exactly R_flow.0..191")
    if control_only:
        failures.append("control has identities absent from treatment")
    schedule_specs = {
        "M": (0, 1_500_000, 1333, "M_route"),
        "U": (0, 1_500_000, 150, "U_route"),
        "X": (0, 1_500_000, 75, "X_route"),
        "R": (540_000, 1_500_000, 192, "R_route"),
    }
    for arm, records in (("control", control), ("treatment", treatment)):
        for cls in ("M", "U", "X") + (("R",) if arm == "treatment" else ()):
            begin, end, number, expected_route = schedule_specs[cls]
            offset = (end - begin) // number
            for i in range(number):
                vid = f"{cls}_flow.{i}"
                record = records.get(vid)
                if record is None:
                    continue
                expected_depart = begin + i * offset
                if int(record["depart_ms"]) != expected_depart:
                    failures.append(f"{arm} {vid} desired departure differs from approved integer-ms schedule")
                if record.get("route") != expected_route or record.get("type") != "technical_passenger":
                    failures.append(f"{arm} {vid} route/type differs from bound demand definition")
                try:
                    factor = Decimal(record["speedFactor"])
                    if not factor.is_finite() or factor <= 0:
                        raise ValueError
                except (ValueError, ArithmeticError):
                    failures.append(f"{arm} {vid} has invalid explicit speedFactor")
    class_counts = {
        arm: {cls: sum(1 for vid in ids if vid.startswith(f"{cls}_flow.")) for cls in ("M", "U", "X", "R")}
        for arm, ids in (("control", control_ids), ("treatment", treatment_ids))
    }
    if class_counts["control"] != {"M": 1333, "U": 150, "X": 75, "R": 0}:
        failures.append("control class counts mismatch")
    if class_counts["treatment"] != {"M": 1333, "U": 150, "X": 75, "R": 192}:
        failures.append("treatment class counts mismatch")
    sf_matches = sum(control[vid].get("speedFactor") == treatment[vid].get("speedFactor") for vid in shared_expected if vid in control and vid in treatment)
    schedule_matches = sum(control[vid].get("depart_ms") == treatment[vid].get("depart_ms") for vid in shared_expected if vid in control and vid in treatment)
    route_type_matches = sum((control[vid].get("route"), control[vid].get("type")) == (treatment[vid].get("route"), treatment[vid].get("type")) for vid in shared_expected if vid in control and vid in treatment)
    return {
        "status": "PASS" if not failures else "FAIL",
        "failures": failures,
        "counts": class_counts,
        "common_expected": len(shared_expected),
        "common_id_matches": len(shared_expected & control_ids & treatment_ids),
        "common_depart_schedule_matches": schedule_matches,
        "common_route_type_matches": route_type_matches,
        "common_speedFactor_matches": sf_matches,
        "common_full_record_matches": len(shared_expected) - len(shared_diffs),
        "route_definition_ids_match": set(control_routes) == set(treatment_routes),
        "route_definitions_match": route_definitions_match,
        "route_definition_count_control": len(control_routes),
        "route_definition_count_treatment": len(treatment_routes),
        "vtype_definition_ids_match": set(control_vtypes) == set(treatment_vtypes),
        "vtype_definitions_match": vtype_definitions_match,
        "vtype_definition_count_control": len(control_vtypes),
        "vtype_definition_count_treatment": len(treatment_vtypes),
        "treatment_only_count": len(treatment_only),
        "treatment_only_is_R_exactly": treatment_only == expected_r,
        "approved_integer_ms_schedules_match": not any("integer-ms schedule" in x for x in failures),
        "control_only_count": len(control_only),
        "checker_fail_closed": True,
        "mismatch_detected": bool(failures),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--build", action="store_true", help="materialize new offline package; refuses overwrite")
    parser.add_argument("--control", type=Path)
    parser.add_argument("--treatment", type=Path)
    args = parser.parse_args()
    if args.build:
        result = materialize()
    else:
        if not args.control or not args.treatment:
            parser.error("provide --build or both --control and --treatment")
        result = check_pair(args.control, args.treatment)
    print(json.dumps(result, indent=2, sort_keys=True))
    if result["status"] != "PASS":
        raise SystemExit(1)


if __name__ == "__main__":
    main()

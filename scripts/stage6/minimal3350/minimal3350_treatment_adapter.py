#!/usr/bin/env python3
"""Offline common-M + R-only materializer/checker for minimal3350 treatment."""
from __future__ import annotations

import hashlib
import json
from decimal import Decimal
from pathlib import Path
import xml.etree.ElementTree as ET

M_FIELDS = ("id", "type", "route", "depart", "departPos", "departLane", "departSpeed", "speedFactor")
R_FIELDS = M_FIELDS
R_SOURCE_REL = "scripts/stage6/minimal3199/prepared_rev3/treatment/demand.rou.xml"
EXPECTED_M = 1396
EXPECTED_R = 192
OFFSET_MS = 1074
R_BEGIN_MS = 540_000
R_INTERVAL_MS = 5_000


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def _ms(depart: str) -> int:
    v = Decimal(depart) * 1000
    if v != v.to_integral_value():
        raise ValueError(f"departure is not integer milliseconds: {depart}")
    return int(v)


def _vehicle_map(path: Path, prefix: str) -> dict[str, ET.Element]:
    root = ET.parse(path).getroot()
    result: dict[str, ET.Element] = {}
    for item in root:
        if item.tag != "vehicle":
            continue
        vid = item.get("id", "")
        if vid.startswith(prefix):
            if vid in result:
                raise ValueError(f"duplicate vehicle identity: {vid}")
            result[vid] = item
    return result


def _signature(node: ET.Element, fields: tuple[str, ...]) -> tuple[str, ...]:
    if any(node.get(k) is None for k in fields):
        raise ValueError(f"vehicle misses required attributes: {node.get('id')}")
    return tuple(node.get(k, "") for k in fields)


def _route_definitions(root: ET.Element) -> tuple[tuple[str, str], ...]:
    return tuple(sorted((n.tag, json.dumps(n.attrib, sort_keys=True))
                        for n in root if n.tag in {"route", "vType"}))


def materialize_treatment_demand(control_demand: Path, r_source: Path, destination: Path) -> dict[str, object]:
    """Copy the bound control M list and reviewed R list, sorted by (depart_ms,id)."""
    croot = ET.parse(control_demand).getroot()
    rroot = ET.parse(r_source).getroot()
    controls = [n for n in croot if n.tag == "vehicle"]
    if len(controls) != EXPECTED_M or any(not n.get("id", "").startswith("M_flow.") for n in controls):
        raise ValueError("control demand is not exactly the 1396-vehicle M vector")
    source_r = [n for n in rroot if n.tag == "vehicle" and n.get("id", "").startswith("R_flow.")]
    if len(source_r) != EXPECTED_R:
        raise ValueError("bound R source does not contain exactly R_flow.0..191")
    out = ET.Element(croot.tag, croot.attrib)
    for node in croot:
        if node.tag != "vehicle":
            out.append(ET.fromstring(ET.tostring(node, encoding="utf-8")))
    r_records=[]
    for i, node in enumerate(source_r):
        if node.get("id") != f"R_flow.{i}" or node.get("type") != "technical_passenger" or node.get("route") != "R_route":
            raise ValueError(f"R source identity/type/route mismatch: {node.get('id')}")
        expected_ms = R_BEGIN_MS + i * R_INTERVAL_MS
        if _ms(node.get("depart", "")) != expected_ms or not (R_BEGIN_MS <= expected_ms < 1_500_000):
            raise ValueError(f"R source departure mismatch: {node.get('id')}")
        r_records.append(ET.fromstring(ET.tostring(node, encoding="utf-8")))
    vehicles = controls + r_records
    vehicles.sort(key=lambda n: (_ms(n.get("depart", "")), n.get("id", "")))
    for node in vehicles:
        out.append(node)
    data = ET.tostring(out, encoding="utf-8", xml_declaration=True) + b"\n"
    destination.parent.mkdir(parents=True, exist_ok=True)
    with destination.open("xb") as f:
        f.write(data)
    return {"bytes": len(data), "sha256": sha256(destination), "m_count": len(controls), "r_count": len(r_records)}


def validate_treatment_card(card: dict[str, object], demand_path: Path, common_manifest_path: Path,
                            r_source: Path, repo: Path, control_demand_path: Path) -> dict[str, object]:
    if sha256(common_manifest_path) != card["common_m_manifest"]["sha256"]:
        raise ValueError("common M manifest hash mismatch")
    manifest = json.loads(common_manifest_path.read_text(encoding="utf-8"))
    if (manifest.get("schema") != "minimal3350_common_m_vehicle_list_v1"
            or manifest.get("qMain_veh_per_h") != 3350.4 or manifest.get("seed") != 17
            or manifest.get("planned_count") != EXPECTED_M):
        raise ValueError("common M manifest header mismatch")
    if sha256(r_source) != card["r_vehicle_source"]["sha256"]:
        raise ValueError("R source hash mismatch")
    if card["r_vehicle_source"]["path"] != R_SOURCE_REL:
        raise ValueError("R source path mismatch")
    croot = ET.parse(control_demand_path).getroot()
    troot = ET.parse(demand_path).getroot()
    if _route_definitions(croot) != _route_definitions(troot):
        raise ValueError("route/vType definitions changed between control and treatment")
    if any(n.tag not in {"vType", "route", "vehicle"} for n in troot):
        raise ValueError("unsupported top-level treatment demand node")
    c_m = _vehicle_map(control_demand_path, "M_flow.")
    t_m = _vehicle_map(demand_path, "M_flow.")
    common_rows = manifest.get("records")
    expected_ids = {f"M_flow.{i}" for i in range(EXPECTED_M)}
    if set(c_m) != expected_ids or set(t_m) != expected_ids or not isinstance(common_rows, list) or len(common_rows) != EXPECTED_M:
        raise ValueError("M identity/count mismatch")
    for row in common_rows:
        vid = row.get("id")
        if vid not in expected_ids:
            raise ValueError(f"unexpected common M identity: {vid}")
        expected = tuple(str(row[k]) for k in M_FIELDS)
        for arm, node in (("control", c_m[vid]), ("treatment", t_m[vid])):
            if _signature(node, M_FIELDS) != expected or row.get("desired_depart_ms") != _ms(node.get("depart", "")):
                raise ValueError(f"{arm} differs from common M manifest: {vid}")
        if _signature(c_m[vid], M_FIELDS) != _signature(t_m[vid], M_FIELDS):
            raise ValueError(f"control/treatment M mismatch: {vid}")
        idx = int(vid.split(".")[-1])
        if _ms(t_m[vid].get("depart", "")) != idx * OFFSET_MS:
            raise ValueError(f"integer SUMOTime M schedule mismatch: {vid}")
    t_r = _vehicle_map(demand_path, "R_flow.")
    s_r = _vehicle_map(r_source, "R_flow.")
    expected_r_ids = {f"R_flow.{i}" for i in range(EXPECTED_R)}
    if set(t_r) != expected_r_ids or set(s_r) != expected_r_ids:
        raise ValueError("treatment-only R identity mismatch")
    for i in range(EXPECTED_R):
        vid = f"R_flow.{i}"
        if _signature(t_r[vid], R_FIELDS) != _signature(s_r[vid], R_FIELDS):
            raise ValueError(f"treatment R differs from bound R source: {vid}")
        if _ms(t_r[vid].get("depart", "")) != R_BEGIN_MS + i * R_INTERVAL_MS:
            raise ValueError(f"R schedule mismatch: {vid}")
    all_nodes = [n for n in troot if n.tag == "vehicle"]
    keys = [(_ms(n.get("depart", "")), n.get("id", "")) for n in all_nodes]
    if keys != sorted(keys):
        raise ValueError("treatment records are not globally sorted by (depart_ms,id)")
    all_ids = {n.get("id", "") for n in all_nodes}
    if any(i.startswith(("U_flow.", "X_flow.")) for i in all_ids):
        raise ValueError("U/X must be explicitly zero")
    if all_ids != expected_ids | expected_r_ids:
        raise ValueError("treatment contains a non-M/R vehicle or omitted identity")
    return {"status": "PASS", "m_count": len(t_m), "r_count": len(t_r),
            "u_count": 0, "x_count": 0, "m_exact_matches_control": EXPECTED_M,
            "m_exact_matches_common_manifest": EXPECTED_M, "r_only_delta": "R_flow.0..R_flow.191",
            "sorted_by_depart_ms_and_id": True}

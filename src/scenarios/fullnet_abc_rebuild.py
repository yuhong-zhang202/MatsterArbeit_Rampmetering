"""Prospective, offline input builder for a matched Stage 6 R0/A/B/C quartet.

This module does not start SUMO. All output files are created in a new package
directory, and every demand attribute is derived from requested flow rules or
an independently generated speed-factor draw, never from simulation output.
"""

from __future__ import annotations

import argparse
from decimal import Decimal
import hashlib
import json
from pathlib import Path
import random
import sys
import xml.etree.ElementTree as ET


ROOT = Path(__file__).resolve().parents[2]
CONTROL_SOURCE = ROOT / "artifacts/stage6_ramp_induced_validation_20260922_v1/control_input/demand_control.rou.xml"
R_ROUTE_SOURCE = ROOT / "artifacts/stage6_baseline_localization_20260921_v1/LOC_M3350_S17/engineering/inputs/LOC_M3350_S17_attempt1/demand.rou.xml"
CONFIG_SOURCE = ROOT / "artifacts/stage6_full_network_abc_phenomenon_validation_plan_20260926_v1/A_launch_package/inputs/scenario.sumocfg"
ADDITIONAL_SOURCE = ROOT / "artifacts/stage6_full_network_abc_phenomenon_validation_plan_20260926_v1/A_launch_package/inputs/scenario.add.xml"

ARM_PROGRAM = {"R0": "A_OPEN", "A": "A_OPEN", "B": "B_MODERATE", "C": "C_STRONG"}
EXPECTED_COUNTS = {"M": 1396, "U": 150, "X": 75, "R": 240}
FIELDS = ("id", "type", "route", "depart", "departPos", "departLane", "departSpeed", "speedFactor")
XSI = "{http://www.w3.org/2001/XMLSchema-instance}noNamespaceSchemaLocation"


def digest(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1 << 20), b""):
            h.update(block)
    return h.hexdigest()


def schedule_ms(begin: str, end: str, number: int) -> list[int]:
    """SUMO 1.26 deterministic number-flow schedule used in prior adapters."""
    b = int(Decimal(begin) * 1000)
    e = int(Decimal(end) * 1000)
    if e <= b or number <= 0:
        raise ValueError("invalid flow schedule")
    spacing = (e - b) // number
    return [b + i * spacing for i in range(number)]


def ms_text(value: int) -> str:
    return f"{value // 1000}.{value % 1000:03d}"


def _flow_definitions() -> tuple[ET.Element, dict[str, ET.Element], dict[str, ET.Element]]:
    control = ET.parse(CONTROL_SOURCE).getroot()
    if len(control.findall("vType")) != 1 or len(control.findall("flow")) != 3:
        raise ValueError("unexpected R0 source definitions")
    flows = {node.get("id"): node for node in control.findall("flow")}
    if set(flows) != {"M_flow", "U_flow", "X_flow"}:
        raise ValueError("unexpected R0 flow IDs")
    for cls in "MUX":
        flow = flows[f"{cls}_flow"]
        if (flow.get("number"), flow.get("begin"), flow.get("end")) != (
            str(EXPECTED_COUNTS[cls]), "0", "1500"
        ):
            raise ValueError(f"unexpected {cls} demand")
        if (flow.get("departPos"), flow.get("departLane"), flow.get("departSpeed")) != (
            "100" if cls == "M" else "last", "best", "max"
        ):
            raise ValueError(f"unexpected {cls} departure rules")
    source_r = ET.parse(R_ROUTE_SOURCE).getroot()
    r_route = next((node for node in source_r.findall("route") if node.get("id") == "R_route"), None)
    if r_route is None or r_route.get("edges") != "urban_in shared_approach ramp_storage ramp_accel merge_section main_down":
        raise ValueError("unexpected R route definition")
    routes = {node.get("id"): node for node in control.findall("route")}
    routes["R_route"] = r_route
    if set(routes) != {"M_route", "R_route", "U_route", "X_route"}:
        raise ValueError("unexpected route definitions")
    r_flow = ET.Element("flow", {
        "id": "R_flow", "type": "technical_passenger", "route": "R_route",
        "begin": "540", "end": "1500", "number": "240", "departPos": "last",
        "departLane": "best", "departSpeed": "max",
    })
    flows["R_flow"] = r_flow
    return control.find("vType"), routes, flows


def _vehicle_records(flows: dict[str, ET.Element], seed: int, mean: float,
                     deviation: float, minimum: float, maximum: float) -> list[dict[str, str]]:
    if not (0 < minimum < mean < maximum and 0 < deviation < maximum - minimum):
        raise ValueError("invalid speedFactor distribution parameters")
    records = []
    for cls in "MRUX":
        flow = flows[f"{cls}_flow"]
        count = int(flow.get("number"))
        for index, depart_ms in enumerate(schedule_ms(flow.get("begin"), flow.get("end"), count)):
            records.append({
                "id": f"{cls}_flow.{index}", "type": flow.get("type"),
                "route": flow.get("route"), "depart": ms_text(depart_ms),
                "departPos": flow.get("departPos"), "departLane": flow.get("departLane"),
                "departSpeed": flow.get("departSpeed"), "_depart_ms": depart_ms,
            })
    # A single deterministic order fixes RNG consumption and XML ordering.
    records.sort(key=lambda record: (record["_depart_ms"], record["id"]))
    rng = random.Random(seed)
    for record in records:
        for _ in range(1_000_000):
            draw = rng.gauss(mean, deviation)
            if minimum <= draw <= maximum:
                record["speedFactor"] = f"{draw:.10f}"
                break
        else:
            raise ValueError("speedFactor rejection sampler did not accept a draw")
    return records


def _write_xml(path: Path, root: ET.Element) -> None:
    ET.indent(root, space="  ")
    ET.ElementTree(root).write(path, encoding="utf-8", xml_declaration=True)


def _route_xml(vtype: ET.Element, routes: dict[str, ET.Element], records: list[dict[str, str]], arm: str) -> ET.Element:
    root = ET.Element("routes", {XSI: "http://sumo.dlr.de/xsd/routes_file.xsd"})
    root.append(ET.fromstring(ET.tostring(vtype)))
    for route_id in ("M_route", "R_route", "U_route", "X_route"):
        root.append(ET.fromstring(ET.tostring(routes[route_id])))
    for record in records:
        if arm == "R0" and record["id"].startswith("R_flow."):
            continue
        ET.SubElement(root, "vehicle", {key: record[key] for key in FIELDS})
    return root


def _replace_output_path(original: str, output_dir: Path) -> str:
    name = Path(original).name
    if not name or name in {".", ".."}:
        raise ValueError("invalid output reference")
    return str(output_dir / name)


def _additional_xml(arm: str, output_dir: Path) -> ET.Element:
    root = ET.parse(ADDITIONAL_SOURCE).getroot()
    selectors = root.findall("WAUT")
    if len(selectors) != 1 or selectors[0].get("startProg") != "A_OPEN":
        raise ValueError("unexpected TLS selector")
    selectors[0].set("startProg", ARM_PROGRAM[arm])
    for node in root.iter():
        if node.tag in {"inductionLoop", "laneAreaDetector"}:
            node.set("file", _replace_output_path(node.get("file"), output_dir))
        elif node.tag == "timedEvent":
            node.set("dest", _replace_output_path(node.get("dest"), output_dir))
    return root


def _config_xml(route_file: Path, additional_file: Path, output_dir: Path) -> ET.Element:
    root = ET.parse(CONFIG_SOURCE).getroot()
    route_nodes = root.findall("./input/route-files")
    additional_nodes = root.findall("./input/additional-files")
    if len(route_nodes) != 1 or len(additional_nodes) != 1:
        raise ValueError("unexpected SUMO configuration")
    route_nodes[0].set("value", str(route_file))
    additional_nodes[0].set("value", str(additional_file))
    for node in root.findall("./output/*") + root.findall("./report/*"):
        value = node.get("value")
        if value and (node.tag.endswith("-output") or node.tag in {"log", "error-log", "lanechange-output"}):
            node.set("value", _replace_output_path(value, output_dir))
    return root


def _audit(output_dir: Path) -> dict:
    parsed = {}
    programs = {}
    configs = {}
    for arm in ARM_PROGRAM:
        directory = output_dir / arm
        demand = ET.parse(directory / "demand.rou.xml").getroot()
        vehicles = demand.findall("vehicle")
        ids = [node.get("id") for node in vehicles]
        if len(ids) != len(set(ids)):
            raise ValueError(f"duplicate vehicle ID in {arm}")
        parsed[arm] = {node.get("id"): tuple(node.get(key) for key in FIELDS) for node in vehicles}
        for node in vehicles:
            vid = node.get("id", "")
            cls, _, suffix = vid.partition("_flow.")
            if cls not in EXPECTED_COUNTS or not suffix.isdecimal():
                raise ValueError(f"unexpected vehicle identity in {arm}: {vid}")
            expected_depart_pos = "100" if cls == "M" else "last"
            if (node.get("departPos"), node.get("departLane"), node.get("departSpeed")) != (
                expected_depart_pos, "best", "max"
            ):
                raise ValueError(f"non-symbolic or unexpected departure rule in {arm}: {vid}")
            if node.get("type") != "technical_passenger" or node.get("route") != f"{cls}_route":
                raise ValueError(f"type or route mismatch in {arm}: {vid}")
        additional = ET.parse(directory / "scenario.add.xml").getroot()
        programs[arm] = additional.find("WAUT").get("startProg")
        configs[arm] = ET.parse(directory / "scenario.sumocfg").getroot()
    common_ids = {f"{cls}_flow.{i}" for cls in "MUX" for i in range(EXPECTED_COUNTS[cls])}
    r_ids = {f"R_flow.{i}" for i in range(EXPECTED_COUNTS["R"])}
    if set(parsed["R0"]) != common_ids:
        raise ValueError("R0 identity set mismatch")
    _, _, flow_defs = _flow_definitions()
    for cls in "MRUX":
        flow = flow_defs[f"{cls}_flow"]
        expected_times = schedule_ms(flow.get("begin"), flow.get("end"), int(flow.get("number")))
        source_arm = "A" if cls == "R" else "R0"
        for i, expected_ms in enumerate(expected_times):
            actual_depart = parsed[source_arm][f"{cls}_flow.{i}"][FIELDS.index("depart")]
            if actual_depart != ms_text(expected_ms):
                raise ValueError(f"desired departure schedule mismatch: {cls}_flow.{i}")
    for arm in "ABC":
        if set(parsed[arm]) != common_ids | r_ids:
            raise ValueError(f"{arm} identity set mismatch")
        if any(parsed[arm][vid] != parsed["R0"][vid] for vid in common_ids):
            raise ValueError(f"{arm} common requested demand differs from R0")
    if any(parsed[arm][vid] != parsed["A"][vid] for arm in "BC" for vid in r_ids):
        raise ValueError("R requested demand differs across A/B/C")
    if programs != ARM_PROGRAM:
        raise ValueError("TLS programs differ from fixed design")
    # Check all config settings except intentionally arm-specific paths.
    def settings(root: ET.Element) -> dict[str, str]:
        result = {}
        for parent in root:
            for node in parent:
                key = f"{parent.tag}/{node.tag}"
                if key in {"input/route-files", "input/additional-files"} or parent.tag in {"output", "report"}:
                    continue
                result[key] = node.get("value")
        return result
    if any(settings(configs[arm]) != settings(configs["R0"]) for arm in "ABC"):
        raise ValueError("non-intervention SUMO settings differ")
    return {
        "status": "STATIC_INPUT_EQUIVALENCE_PASS_NO_SUMO_STARTED",
        "counts": {arm: {cls: sum(vid.startswith(f"{cls}_flow.") for vid in parsed[arm]) for cls in "MRUX"} for arm in ARM_PROGRAM},
        "common_requested_identical": True, "r_requested_identical_across_abc": True,
        "programs": programs, "non_intervention_config_identical": True,
    }


def build(output_dir: Path, raw_root: Path, *, speed_seed: int, mean: float,
          deviation: float, minimum: float, maximum: float, source_note: str) -> dict:
    if output_dir.exists():
        raise FileExistsError(f"refusing to overwrite {output_dir}")
    if raw_root.exists():
        raise FileExistsError(f"raw root already exists: {raw_root}")
    if not output_dir.is_absolute() or not raw_root.is_absolute():
        raise ValueError("output and raw roots must be absolute")
    if not source_note.strip():
        raise ValueError("speedFactor source note is required")
    vtype, routes, flows = _flow_definitions()
    records = _vehicle_records(flows, speed_seed, mean, deviation, minimum, maximum)
    output_dir.mkdir(parents=True)
    for arm in ARM_PROGRAM:
        directory = output_dir / arm
        directory.mkdir()
        target_raw = raw_root / arm / "outputs"
        _write_xml(directory / "demand.rou.xml", _route_xml(vtype, routes, records, arm))
        _write_xml(directory / "scenario.add.xml", _additional_xml(arm, target_raw))
        _write_xml(directory / "scenario.sumocfg", _config_xml(
            directory / "demand.rou.xml", directory / "scenario.add.xml", target_raw
        ))
    audit = _audit(output_dir)
    (output_dir / "STATIC_AUDIT.json").write_text(json.dumps(audit, indent=2, sort_keys=True) + "\n")
    manifest = {
        "status": "INPUTS_BUILT_NOT_EXECUTION_AUTHORIZED", "sumo_starts": 0,
        "input_sources": {str(path.relative_to(ROOT)): digest(path) for path in (CONTROL_SOURCE, R_ROUTE_SOURCE, CONFIG_SOURCE, ADDITIONAL_SOURCE)},
        "generator_sha256": digest(Path(__file__)),
        "raw_root": str(raw_root),
        "speed_factor_generation": {
            "algorithm": "Python random.Random(seed).gauss(mean, deviation), reject values outside inclusive [min,max]; draw in sorted (depart_ms,id) order; serialize 10 decimal places",
            "seed": speed_seed, "mean": mean, "deviation": deviation, "minimum": minimum, "maximum": maximum,
            "source_note": source_note, "python_version": sys.version.split()[0],
        },
        "files": {str(path.relative_to(output_dir)): digest(path) for path in sorted(output_dir.rglob("*")) if path.is_file()},
    }
    (output_dir / "INPUT_MANIFEST.json").write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n")
    return audit


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("mode", choices=("build", "check"))
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--raw-root", type=Path)
    parser.add_argument("--speed-seed", type=int)
    parser.add_argument("--speed-mean", type=float)
    parser.add_argument("--speed-deviation", type=float)
    parser.add_argument("--speed-minimum", type=float)
    parser.add_argument("--speed-maximum", type=float)
    parser.add_argument("--speed-source-note")
    args = parser.parse_args()
    if args.mode == "check":
        result = _audit(args.output_dir)
    else:
        required = (args.raw_root, args.speed_seed, args.speed_mean, args.speed_deviation,
                    args.speed_minimum, args.speed_maximum, args.speed_source_note)
        if any(value is None for value in required):
            parser.error("build requires raw root and all speedFactor generation parameters")
        result = build(args.output_dir, args.raw_root, speed_seed=args.speed_seed,
                       mean=args.speed_mean, deviation=args.speed_deviation,
                       minimum=args.speed_minimum, maximum=args.speed_maximum,
                       source_note=args.speed_source_note)
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env python3
"""Fail-closed offline adapter for a future RI3350 R=0 control output.

This module imports (but never executes ``main`` from) the hash-bound locked
LOC_M3350 analyzer. It supplies isolated input paths, independently audits
scheduled/realized M/R/U/X lifecycle, and adds the fixed PRE/control mobility
screens. It does not launch SUMO or alter the classifier.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
import math
import statistics
import sys
import tempfile
import xml.etree.ElementTree as ET
from collections import Counter, defaultdict
from decimal import Decimal
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
PACKAGE = ROOT / "artifacts/stage6_ramp_induced_validation_20260922_v1"
METHOD = ROOT / "docs/methodology/FREEWAY_PROTECTABLE_STATE_EXPLORATORY_DEFINITION.md"
METHOD_SHA256 = "22fe22170c17ce74e261e717586a458a1b5173e9deabbee925bd4c1d606adfe7"
DESIGN = ROOT / "docs/methodology/STAGE6_RAMP_INDUCED_BREAKDOWN_VALIDATION_PLAN.md"
DESIGN_SHA256 = "62fb63eb49ae98b58bc45ad6bc7d60cd21fcdb73b3327c34b97c5151b01ca355"
LOCKED_ANALYZER = ROOT / "artifacts/stage6_baseline_localization_20260921_v1/LOC_M3350_S17/engineering/analysis/apply_rule.py"
LOCKED_ANALYZER_SHA256 = "78f001b7909bdda6797eae6aab5bf6bf0dd70bce83262d8f2619c3fa71149c55"
NETWORK_SHA256 = "887c232483f0c68dc024334ff5997250d7d36299ab2744bdcf49d5a314c700ca"
OUTPUT_ROLES = ROOT / "artifacts/stage6_baseline_localization_20260921_v1/LOC_M3350_S17/engineering/inputs/LOC_M3350_S17_attempt1/output_roles.json"
OUTPUT_ROLES_SHA256 = "e33b7439cc15b7b68048fa2bf63f659769b93e4718650c11eeda46959404b2b3"
DEMAND = PACKAGE / "control_input/demand_control.rou.xml"
NETWORK = ROOT / "artifacts/stage6_baseline_localization_20260921_v1/LOC_M3350_S17/engineering/build_attempts/TV_BUILD01/network.net.xml"
OUTPUT_ROOT = ROOT / "data/processed/stage6_ramp_induced_validation_20260922_v1"
DEMAND_SHA256 = "0edeb776e6656f3fd22f1e8d0b4c07ece17903695c901af576d93fb205b26865"
RUN_ID = "RI3350_CTRL_S17_technical_retry1"
RAW_RUN_DIR = PACKAGE / "outputs" / RUN_ID
HORIZON = 2700
DEMAND_END = 1500
MAINLINE_LANES = {
    "main_up_0": 0, ":freeway_merge_0_0": 0, "merge_section_1": 0,
    ":merge_end_0_0": 0, "main_down_0": 0,
    "main_up_1": 1, ":freeway_merge_0_1": 1, "merge_section_2": 1,
    ":merge_end_0_1": 1, "main_down_1": 1,
}
MAINLINE_WHITELIST = set(MAINLINE_LANES)
CORE_CELLS = tuple(range(13, 18))
SCOPES = ("lane0", "lane1", "pooled")
PRE_BLOCKS = ((360, 450), (450, 540))
CONTROL_BLOCKS = tuple((t, t + 90) for t in range(540, 1440, 90))
ALPHA_P = 0.70
HIGH_MOBILITY_RATIO = 0.85
SUMO_TIME_UNITS_PER_SECOND = 1000
TRIPINFO_TIME_PRECISION = 2
TRIPINFO_TIME_HALF_UNIT = Decimal(1).scaleb(-TRIPINFO_TIME_PRECISION) / 2


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for b in iter(lambda: f.read(1 << 20), b""):
            h.update(b)
    return h.hexdigest()


def write_csv(path: Path, rows: list[dict], fields: list[str] | None = None) -> None:
    path.write_bytes(csv_bytes(rows, fields))


def csv_bytes(rows: list[dict], fields: list[str] | None = None) -> bytes:
    if fields is None:
        fields = list(rows[0]) if rows else []
    buf = io.StringIO(newline="")
    w = csv.DictWriter(buf, fieldnames=fields, extrasaction="raise")
    w.writeheader()
    w.writerows(rows)
    return buf.getvalue().encode("utf-8")


def _canonical_sha(value) -> str:
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":"),
                                     allow_nan=False).encode("utf-8")).hexdigest()


def load_locked_analyzer():
    if sha256(METHOD) != METHOD_SHA256:
        raise ValueError("locked-method SHA-256 mismatch; stop")
    if sha256(LOCKED_ANALYZER) != LOCKED_ANALYZER_SHA256:
        raise ValueError("locked-analyzer SHA-256 mismatch; stop and re-review")
    # Audit module-scope statements, then execute definitions in memory. This
    # avoids importlib bytecode writes and does not invoke the legacy main().
    import ast
    import types
    parsed = ast.parse(LOCKED_ANALYZER.read_text(encoding="utf-8"))
    allowed = (ast.Import, ast.ImportFrom, ast.Assign, ast.AnnAssign,
               ast.FunctionDef, ast.If, ast.Expr)
    if any(not isinstance(n, allowed) for n in parsed.body):
        raise ValueError("unexpected module-level analyzer behavior; refuse reuse")
    for n in parsed.body:
        if isinstance(n, ast.Expr) and not (isinstance(n.value, ast.Constant) and isinstance(n.value.value, str)):
            raise ValueError("module-level analyzer expression may have side effects")
        if isinstance(n, ast.If) and not (
            isinstance(n.test, ast.Compare) and isinstance(n.test.left, ast.Name)
            and n.test.left.id == "__name__"
        ):
            raise ValueError("unexpected top-level conditional in analyzer")
    module = types.ModuleType("ri3350_locked_analyzer")
    module.__file__ = str(LOCKED_ANALYZER)
    exec(compile(parsed, str(LOCKED_ANALYZER), "exec"), module.__dict__)
    if module.EXPECTED_METHOD != METHOD_SHA256:
        raise ValueError("analyzer is not bound to the expected locked method")
    if module.PROFILES != {"P": (.70, 3, 1.0), "S": (.60, 4, 1.25), "L": (.80, 2, 1.0)}:
        raise ValueError("profile constants differ from the reviewed locked application")
    return module


def _finite_float(value: str | None, field: str, *, allow_negative: bool = True) -> float:
    if value in (None, ""):
        raise ValueError(f"missing required numeric field: {field}")
    x = float(value)
    if not math.isfinite(x) or (not allow_negative and x < 0):
        raise ValueError(f"invalid numeric field {field}={value!r}")
    return x


def _seconds_to_sumo_time(value: str, field: str) -> int:
    """Convert a decimal second value to SUMO's millisecond SUMOTime unit."""
    try:
        scaled = Decimal(value) * SUMO_TIME_UNITS_PER_SECOND
    except Exception as exc:
        raise ValueError(f"invalid SUMO time {field}={value!r}") from exc
    if not scaled.is_finite() or scaled != scaled.to_integral_value():
        raise ValueError(f"{field} is not exactly representable as SUMOTime milliseconds: {value!r}")
    return int(scaled)


def flow_scheduled_depart_ms(flow: dict, index: int) -> int:
    """Mirror SUMOVehicleParserHelper's integer repetitionOffset semantics."""
    number = int(flow["number"])
    if number <= 0 or not 0 <= index < number:
        raise ValueError(f"flow index outside positive number schedule: index={index}, number={number}")
    begin_ms = int(flow["begin_ms"])
    end_ms = int(flow["end_ms"])
    if end_ms < begin_ms:
        raise ValueError("flow end precedes begin")
    repetition_offset_ms = (end_ms - begin_ms) // number
    return begin_ms + index * repetition_offset_ms


def serialized_depart_delay_matches(actual_depart_raw: str, scheduled_depart_ms: int,
                                    serialized_delay_raw: str) -> bool:
    """Compare against tripinfo's documented two-decimal time serialization."""
    expected = Decimal(actual_depart_raw) - Decimal(scheduled_depart_ms) / SUMO_TIME_UNITS_PER_SECOND
    observed = Decimal(serialized_delay_raw)
    return abs(observed - expected) <= TRIPINFO_TIME_HALF_UNIT


def parse_demand_schedule(demand_path: Path) -> tuple[dict[str, dict], dict[str, list[str]]]:
    """Read exact scheduled IDs from SUMO number-flow contracts; no raw claims."""
    root = ET.parse(demand_path).getroot()
    if root.tag != "routes":
        raise ValueError("demand root must be <routes>")
    flows: dict[str, dict] = {}
    expected: dict[str, list[str]] = {c: [] for c in "MRUX"}
    for flow in root.findall("flow"):
        fid = flow.get("id", "")
        cls = fid.split("_", 1)[0]
        if cls not in expected or cls in flows:
            raise ValueError(f"unsupported/duplicate flow class: {fid}")
        count = int(flow.get("number", ""))
        begin_raw = flow.get("begin", "")
        end_raw = flow.get("end", "")
        begin = _finite_float(begin_raw, f"{fid}.begin", allow_negative=False)
        end = _finite_float(end_raw, f"{fid}.end", allow_negative=False)
        begin_ms = _seconds_to_sumo_time(begin_raw, f"{fid}.begin")
        end_ms = _seconds_to_sumo_time(end_raw, f"{fid}.end")
        if count < 0 or end <= begin or end > DEMAND_END:
            raise ValueError(f"invalid demand window/count for {fid}")
        flows[cls] = {"flow_id": fid, "number": count, "begin": begin, "end": end,
                      "begin_ms": begin_ms, "end_ms": end_ms,
                      "route_id": flow.get("route"), "type_id": flow.get("type"),
                      "departPos": flow.get("departPos"), "departLane": flow.get("departLane"),
                      "departSpeed": flow.get("departSpeed")}
        expected[cls] = [f"{fid}.{i}" for i in range(count)]
    for vehicle in root.findall("vehicle"):
        vid = vehicle.get("id", "")
        cls = vid.split("_", 1)[0]
        if cls not in expected or any(vid in ids for ids in expected.values()):
            raise ValueError(f"unsupported/duplicate scheduled vehicle: {vid}")
        expected[cls].append(vid)
    if not flows.get("M") or not flows.get("U") or not flows.get("X"):
        raise ValueError("control demand must contain M/U/X source definitions")
    if flows.get("R", {}).get("number", 0) != 0 or expected["R"]:
        raise ValueError("R=0 control input contains scheduled R demand")
    return flows, expected


def validate_output_destination(output_dir: Path, raw_dir: Path) -> Path:
    """Constrain writes to the designated processed tree and away from inputs."""
    target = output_dir.resolve()
    allowed = OUTPUT_ROOT.resolve()
    raw = raw_dir.resolve()
    if target == raw or raw in target.parents or target in raw.parents:
        raise ValueError("output destination overlaps raw source directory")
    raw_root = (ROOT / "data/raw").resolve()
    if target == raw_root or raw_root in target.parents or target in raw_root.parents:
        raise ValueError("output destination may not overlap data/raw")
    if target == allowed or allowed not in target.parents:
        raise ValueError("output destination must be a new child of the designated processed output root")
    if target.exists():
        raise FileExistsError("output directory already exists; use a new revision, never overwrite")
    return target


def validate_demand_binding(demand_path: Path) -> str:
    """Bind the actual caller-supplied path, not a separate package constant."""
    actual = sha256(demand_path)
    if actual != DEMAND_SHA256:
        raise ValueError("caller-supplied control demand hash mismatch")
    return actual


def validate_design_binding() -> str:
    """Fail if the bound mechanism/execution design has drifted."""
    actual = sha256(DESIGN)
    if actual != DESIGN_SHA256:
        raise ValueError("bound design document hash mismatch")
    return actual


def validate_output_roles() -> tuple[dict, str]:
    if sha256(OUTPUT_ROLES) != OUTPUT_ROLES_SHA256:
        raise ValueError("locked output_roles.json hash mismatch")
    roles = json.loads(OUTPUT_ROLES.read_text(encoding="utf-8"))
    xml_roles = roles.get("required_xml_roles")
    if roles.get("required_role_count") != 18 or not isinstance(xml_roles, list) or len(xml_roles) != 18:
        raise ValueError("output role declaration is not the locked 18-role contract")
    names = [item.get("role") for item in xml_roles]
    expected = {"fcd.xml", "vehroute.xml", "tripinfo.xml", "sumo_summary.xml",
                "tls_states.xml", "lanechanges.xml", "queues.xml",
                "ramp_storage_e2.xml", "shared_boundary_e2.xml",
                "p1_main_up_1300_l0.xml", "p1_main_up_1300_l1.xml",
                "p1_merge_section_20_l0.xml", "p1_merge_section_20_l1.xml",
                "p1_merge_section_20_l2.xml", "p1_main_down_20_l0.xml",
                "p1_main_down_20_l1.xml", "p1_main_down_200_l0.xml",
                "p1_main_down_200_l1.xml"}
    if len(names) != len(set(names)) or set(names) != expected:
        raise ValueError("output_roles.json role names do not match the adapter contract")
    return roles, OUTPUT_ROLES_SHA256


def audit_raw_manifest(raw_dir: Path) -> tuple[dict[str, Path], list[dict]]:
    """Verify the R02 v1 manifest before parsing. Missing != verified zero.

    R02 inventories required outputs in ``artifact_roles`` and non-role files
    in ``support_files``. This adapter intentionally rejects the obsolete
    ``files`` schema instead of silently interpreting an unknown inventory.
    """
    expected_run_root = RAW_RUN_DIR.resolve()
    resolved_raw = raw_dir.resolve()
    if resolved_raw != expected_run_root:
        raise ValueError(f"raw directory must be the bound run output directory: {expected_run_root}")
    if not resolved_raw.is_dir():
        raise ValueError("bound raw run directory is missing")
    mp = raw_dir / "output_manifest.json"
    if not mp.is_file():
        raise ValueError("output_manifest.json missing; completeness UNKNOWN")
    manifest = json.loads(mp.read_text(encoding="utf-8"))
    if manifest.get("schema_version") != "1" or manifest.get("run_id") != raw_dir.name:
        raise ValueError("manifest schema/run binding mismatch")
    role_records = manifest.get("artifact_roles")
    support_records = manifest.get("support_files")
    if not isinstance(role_records, list) or not isinstance(support_records, list):
        raise ValueError("manifest artifact_roles/support_files missing; completeness UNKNOWN")
    if manifest.get("files") is not None:
        raise ValueError("unsupported legacy manifest.files schema")
    role_contract, _ = validate_output_roles()
    declared = {item["role"]: item for item in role_contract["required_xml_roles"]}
    if len(role_records) != len(declared):
        raise ValueError("manifest required-role coverage count mismatch")
    expected_role_keys = set(declared)
    by_role = {}
    for rec in role_records:
        role = rec.get("role") if isinstance(rec, dict) else None
        if not isinstance(role, str) or role in by_role:
            raise ValueError(f"missing/duplicate manifest role: {role!r}")
        if role not in declared:
            raise ValueError(f"unexpected manifest role: {role}")
        expected = declared[role]
        for field in ("kind", "detector_id", "lane", "root"):
            if rec.get(field) != expected.get(field):
                raise ValueError(f"manifest role metadata mismatch for {role}: {field}")
        if rec.get("relative_path") != role:
            raise ValueError(f"manifest role path mismatch for {role}")
        if rec.get("status") != "PRESENT":
            raise ValueError(f"required manifest role is not present: {role} ({rec.get('status')})")
        by_role[role] = rec
    if set(by_role) != expected_role_keys:
        raise ValueError("manifest required-role coverage mismatch")
    if manifest.get("actual_file_count") != len(role_records) + len(support_records):
        raise ValueError("manifest actual_file_count mismatch")

    byname: dict[str, Path] = {}
    audit = []
    seen_paths = set()
    combined = [("role", rec) for rec in role_records] + [("support", rec) for rec in support_records]
    for category, rec in combined:
        if not isinstance(rec, dict):
            raise ValueError("manifest record must be an object")
        rel = rec.get("relative_path")
        if not isinstance(rel, str) or not rel or Path(rel).is_absolute():
            raise ValueError(f"invalid manifest relative_path: {rel!r}")
        p = (raw_dir / rel).resolve()
        if not p.is_relative_to(resolved_raw) or p == resolved_raw:
            raise ValueError(f"manifest path escapes bound raw run directory: {p}")
        if str(p) in seen_paths:
            raise ValueError(f"duplicate manifest path: {rel}")
        seen_paths.add(str(p))
        if category == "support" and any(part in {"", ".", ".."} for part in Path(rel).parts):
            raise ValueError(f"non-canonical manifest support path: {rel}")
        if category == "support" and rel in expected_role_keys:
            raise ValueError(f"required role duplicated as support file: {rel}")
        if not p.is_file():
            raise ValueError(f"manifest-listed raw file missing: {p}")
        actual = sha256(p)
        size = p.stat().st_size
        if actual != rec.get("sha256") or size != rec.get("size_bytes"):
            raise ValueError(f"raw manifest mismatch: {p}")
        if p.name in byname:
            raise ValueError(f"duplicate manifest basename: {p.name}")
        byname[p.name] = p
        audit.append({"role_or_basename": rec.get("role", p.name), "path": str(p),
                      "bytes": size, "sha256": actual, "status": "PASS_HASH_BOUND"})
    required = {"fcd.xml", "vehroute.xml", "tripinfo.xml", "sumo_summary.xml",
                "tls_states.xml", "lanechanges.xml", "queues.xml", "sumo_error.log",
                "ramp_storage_e2.xml", "shared_boundary_e2.xml"}
    if not required.issubset(byname):
        raise ValueError(f"missing required raw roles: {sorted(required - set(byname))}")
    if not set(declared).issubset(byname):
        raise ValueError(f"manifest missing roles bound by output_roles.json: {sorted(set(declared)-set(byname))}")
    for name, item in declared.items():
        path = byname[name]
        root = ET.parse(path).getroot()
        if root.tag != item.get("root"):
            raise ValueError(f"root mismatch for declared output role {name}: {root.tag}")
        if item.get("kind") in {"E1", "E2"}:
            expected_id = item.get("detector_id")
            interval_tag = "interval"
            intervals = root.findall(interval_tag)
            if any(row.get("id") != expected_id for row in intervals):
                raise ValueError(f"detector ID mismatch for declared role {name}")
            expected_intervals = [(float(t), float(t + 30)) for t in range(0, HORIZON, 30)]
            actual_intervals = [(float(row.get("begin", "nan")), float(row.get("end", "nan")))
                                for row in intervals]
            if actual_intervals != expected_intervals:
                raise ValueError(f"detector intervals differ from output_roles.json for {name}")
    e1 = [n for n in byname if n.startswith("p1_") and n.endswith(".xml")]
    if len(e1) != 9:
        raise ValueError(f"expected 9 E1 files, found {len(e1)}")
    for name, path in byname.items():
        if name.endswith(".xml"):
            ET.parse(path)  # force complete XML parse, not just a readable prefix
    # Bind the full time support of non-FCD outputs too; parseability alone is
    # not proof that a role covers the configured horizon.
    summary = ET.parse(byname["sumo_summary.xml"]).getroot()
    summary_steps = summary.findall("step")
    if [float(x.get("time", "nan")) for x in summary_steps] != [float(t) for t in range(HORIZON)]:
        raise ValueError("summary time grid incomplete or unordered")
    queues = ET.parse(byname["queues.xml"]).getroot()
    queue_steps = queues.findall("data")
    if [float(x.get("timestep", "nan")) for x in queue_steps] != [float(t) for t in range(HORIZON)]:
        raise ValueError("queue time grid incomplete or unordered")
    tls = ET.parse(byname["tls_states.xml"]).getroot()
    tls_by_id: dict[str, list[float]] = defaultdict(list)
    for state in tls.findall("tlsState"):
        tls_by_id[state.get("id", "")].append(float(state.get("time", "nan")))
    if set(tls_by_id) != {"ramp_mid", "urban_tls"} or any(
        values != [float(t) for t in range(HORIZON)] for values in tls_by_id.values()
    ):
        raise ValueError("TLS coverage/identity grid incomplete")
    for name in ("ramp_storage_e2.xml", "shared_boundary_e2.xml"):
        intervals = ET.parse(byname[name]).getroot().findall("interval")
        expected = [(float(t), float(t + 30)) for t in range(0, HORIZON, 30)]
        actual = [(float(x.get("begin", "nan")), float(x.get("end", "nan"))) for x in intervals]
        if actual != expected:
            raise ValueError(f"{name} interval grid incomplete")
    return byname, audit


def run_locked_analyzer_with_manifest_bridge(analyzer, raw_dir: Path,
                                             manifest_path: Path,
                                             file_map: dict[str, Path]):
    """Run the hash-locked analyzer via a temporary legacy-manifest view.

    The analyzer source is immutable and expects ``manifest.files``. R02's
    current schema stores identical path/size/hash evidence in two typed
    arrays. After ``audit_raw_manifest`` validates every entry, construct the
    lossless legacy projection in a temporary directory. The projected paths
    point to the original raw files; only the temporary manifest is synthetic.
    """
    source = json.loads(manifest_path.read_text(encoding="utf-8"))
    records = []
    for rec in source["artifact_roles"] + source["support_files"]:
        path = file_map[Path(rec["relative_path"]).name]
        records.append({"path": str(path), "bytes": rec["size_bytes"],
                        "sha256": rec["sha256"]})
    compat = {"files": records}
    compat_bytes = (json.dumps(compat, sort_keys=True, separators=(",", ":"),
                               allow_nan=False) + "\n").encode("utf-8")
    with tempfile.TemporaryDirectory(prefix="ri3350_manifest_bridge_") as td:
        temp_root = Path(td)
        run_view = temp_root / "outputs" / raw_dir.name
        run_view.mkdir(parents=True)
        (run_view / "output_manifest.json").write_bytes(compat_bytes)
        analyzer.RAW = temp_root / "outputs"
        analyzer.RUNS = {"CTRL": raw_dir.name}
        results = analyzer.run_one("CTRL", raw_dir.name)
    compatibility_sha = hashlib.sha256(compat_bytes).hexdigest()
    receipts = results[0]
    original_sha = sha256(manifest_path)
    original_size = manifest_path.stat().st_size
    for row in receipts:
        row["compatibility_manifest_sha256"] = None
        if row.get("role_inferred_from_manifest_path") == "output_manifest.json":
            row.update({"manifest_path": str(manifest_path),
                        "resolved_path": str(manifest_path),
                        "declared_bytes": original_size,
                        "actual_bytes": original_size,
                        "declared_sha256": original_sha,
                        "actual_sha256": original_sha,
                        "status": "SELF_HASHED_ORIGINAL_MANIFEST",
                        "compatibility_manifest_sha256": compatibility_sha})
    return results, compatibility_sha


def _dict_unique(root: ET.Element, child: str, id_key: str = "id") -> dict[str, ET.Element]:
    out: dict[str, ET.Element] = {}
    for elem in root.findall(child):
        key = elem.get(id_key)
        if not key or key in out:
            raise ValueError(f"missing/duplicate {child} identity: {key}")
        out[key] = elem
    return out


def build_lifecycle(raw: dict[str, Path], flows: dict[str, dict],
                    expected: dict[str, list[str]], run_id: str = RUN_ID,
                    demand_path: Path = DEMAND) -> tuple[list[dict], list[dict], dict]:
    """Independent identity-level accounting; never use FCD absence as arrival."""
    routes_root = ET.parse(raw["vehroute.xml"]).getroot()
    trips_root = ET.parse(raw["tripinfo.xml"]).getroot()
    fcd_root = ET.parse(raw["fcd.xml"]).getroot()
    if routes_root.tag != "routes" or trips_root.tag != "tripinfos" or fcd_root.tag != "fcd-export":
        raise ValueError("raw XML root mismatch")
    routes = _dict_unique(routes_root, "vehicle")
    trips = _dict_unique(trips_root, "tripinfo")
    fcd_ids: set[str] = set()
    fcd_time_ids: set[tuple[int, str]] = set()
    first_last: dict[str, list[int]] = {}
    fcd_labels = []
    first_core: dict[str, list[int]] = defaultdict(list)
    fcd_errors = []
    for ts in fcd_root.findall("timestep"):
        t = _finite_float(ts.get("time"), "FCD.time", allow_negative=False)
        ti = int(t)
        if t != ti:
            fcd_errors.append(f"NONINTEGER_TIME:{t}")
        fcd_labels.append(ti)
        for veh in ts.findall("vehicle"):
            vid = veh.get("id")
            key = (ti, vid)
            if not vid or key in fcd_time_ids:
                raise ValueError(f"duplicate/missing FCD (time,id): {key}")
            fcd_time_ids.add(key); fcd_ids.add(vid)
            if vid not in first_last:
                first_last[vid] = [ti, ti]
            else:
                first_last[vid][1] = ti
            x = _finite_float(veh.get("x"), f"FCD.{vid}.x")
            _finite_float(veh.get("speed"), f"FCD.{vid}.speed")
            if x >= 1300 and x < 1800:
                first_core[vid].append(ti)
    if fcd_labels != list(range(HORIZON)):
        raise ValueError("FCD time labels are missing, duplicated, unordered, or not 0..2699")
    scheduled = set().union(*(set(v) for v in expected.values()))
    observed = set(routes) | set(trips) | fcd_ids
    unknown_ids = observed - scheduled
    if unknown_ids:
        raise ValueError(f"raw contains unscheduled identities: {sorted(unknown_ids)[:10]}")
    # The bound control config requests write-undeparted and write-unfinished
    # outputs. Therefore a missing expected identity is a completeness gap,
    # not safe evidence of never-inserted status.
    if set(routes) != scheduled or set(trips) != scheduled:
        raise ValueError(
            f"lifecycle role identity coverage mismatch; missing vehroute={len(scheduled-set(routes))}, "
            f"extra vehroute={len(set(routes)-scheduled)}, missing tripinfo={len(scheduled-set(trips))}, "
            f"extra tripinfo={len(set(trips)-scheduled)}"
        )
    for vid in observed:
        cls = next(c for c, ids in expected.items() if vid in ids)
        rec = routes.get(vid)
        if rec is not None:
            route = rec.find("route")
            edges = route.get("edges", "").split() if route is not None else []
            route_name = flows.get(cls, {}).get("route_id")
            # Route XML expands edge IDs; check class via the source flow's route ID
            # using demand route definitions below, not a guessed edge substring.
            rec.attrib["_route_edges"] = " ".join(edges)
        else:
            rec = None
    demand_root = ET.parse(demand_path).getroot()
    route_edges = {r.get("id"): (r.get("edges") or "").split() for r in demand_root.findall("route")}
    expected_routes = {c: route_edges.get(f.get("route_id"), []) for c, f in flows.items()}
    rows = []
    class_summary = []
    for cls in "MRUX":
        ids = expected[cls]
        crows = []
        for vid in ids:
            vr = routes.get(vid); ti = trips.get(vid); seen_fcd = vid in fcd_ids
            if vr is None and (ti is not None or seen_fcd):
                raise ValueError(f"identity has FCD/tripinfo but no vehroute record: {vid}")
            if vr is not None:
                route = vr.find("route")
                edges = (route.get("edges", "") if route is not None else "").split()
                if expected_routes.get(cls) and edges != expected_routes[cls]:
                    raise ValueError(f"ordered source route mismatch for {vid}")
                expected_type = flows.get(cls, {}).get("type_id")
                if expected_type is not None and vr.get("type") != expected_type:
                    raise ValueError(f"class/type mismatch for {vid}: {vr.get('type')} != {expected_type}")
                sf = _finite_float(vr.get("speedFactor"), f"{vid}.speedFactor", allow_negative=False)
                if sf <= 0:
                    raise ValueError(f"nonpositive speedFactor for {vid}")
            else:
                sf = None
            depart_raw = (vr.get("depart") if vr is not None else None)
            if depart_raw is None:
                if vr is not None:
                    raise ValueError(f"vehroute identity missing required depart field: {vid}")
                actual_depart = None
            else:
                actual_depart = _finite_float(depart_raw, f"{vid}.depart")
                if actual_depart < 0 and actual_depart != -1:
                    raise ValueError(f"unsupported negative departure sentinel for {vid}: {actual_depart}")
            trip_depart_raw = ti.get("depart") if ti is not None else None
            if ti is not None and trip_depart_raw in (None, ""):
                raise ValueError(f"tripinfo identity missing required depart field: {vid}")
            if trip_depart_raw not in (None, ""):
                trip_depart = _finite_float(trip_depart_raw, f"{vid}.tripinfo.depart")
                if trip_depart < 0 and trip_depart != -1:
                    raise ValueError(f"unsupported tripinfo departure sentinel for {vid}: {trip_depart}")
                if actual_depart is not None and abs(trip_depart - actual_depart) > 0.011:
                    raise ValueError(f"vehroute/tripinfo depart conflict for {vid}: {actual_depart} vs {trip_depart}")
            inserted = actual_depart is not None and actual_depart >= 0
            late = bool(inserted and actual_depart >= DEMAND_END)
            route_arr_raw = vr.get("arrival") if vr is not None else None
            trip_arr_raw = ti.get("arrival") if ti is not None else None
            if route_arr_raw is not None and trip_arr_raw is not None:
                ra = _finite_float(route_arr_raw, f"{vid}.vehroute.arrival")
                ta = _finite_float(trip_arr_raw, f"{vid}.tripinfo.arrival")
                if (ra < 0 and ra != -1) or (ta < 0 and ta != -1):
                    raise ValueError(f"unsupported negative arrival sentinel for {vid}: {ra}/{ta}")
                if abs(ra - ta) > 0.011:
                    raise ValueError(f"vehroute/tripinfo arrival conflict for {vid}: {ra} vs {ta}")
                arrival = ta
            elif trip_arr_raw is not None:
                arrival = _finite_float(trip_arr_raw, f"{vid}.tripinfo.arrival")
                if arrival < 0 and arrival != -1:
                    raise ValueError(f"unsupported negative arrival sentinel for {vid}: {arrival}")
            elif route_arr_raw is not None:
                arrival = _finite_float(route_arr_raw, f"{vid}.vehroute.arrival")
                if arrival < 0 and arrival != -1:
                    raise ValueError(f"unsupported negative arrival sentinel for {vid}: {arrival}")
            else:
                arrival = None
            if not inserted:
                if seen_fcd:
                    raise ValueError(f"FCD identity contradicts never-inserted departure status: {vid}")
                if arrival is not None and arrival >= 0:
                    raise ValueError(f"undeparted identity has arrival evidence: {vid}")
                arrived = False; arrived_at_horizon = False; unfinished = False; never = True
                lifecycle_status = "NEVER_INSERTED_OR_EXPLICIT_UNDEPARTED"
            else:
                never = False
                if arrival is None:
                    raise ValueError(f"inserted identity missing arrival/unfinished sentinel: {vid}")
                if arrival > HORIZON:
                    raise ValueError(f"arrival exceeds simulation horizon for {vid}: {arrival}")
                arrived_at_horizon = arrival == HORIZON
                arrived = arrival >= 0 and arrival < HORIZON
                unfinished = arrival == -1
                if ti is None and arrival >= 0:
                    raise ValueError(f"arrival present without tripinfo for {vid}")
                lifecycle_status = ("ARRIVED" if arrived else
                                    "ARRIVED_AT_HORIZON_BOUNDARY" if arrived_at_horizon else
                                    "UNFINISHED_AT_HORIZON")
            # Scheduled depart: derive exactly from flow number semantics; fixed
            # vehicles use explicit depart. SUMO output precision is preserved.
            if cls in flows and vid.startswith(flows[cls]["flow_id"] + "."):
                index = int(vid.rsplit(".", 1)[1])
                flow = flows[cls]
                n = flow["number"]
                if not 0 <= index < n:
                    raise ValueError(f"flow index outside source schedule: {vid}")
                scheduled_depart = flow_scheduled_depart_ms(flow, index) / SUMO_TIME_UNITS_PER_SECOND
            else:
                scheduled_depart = _finite_float(vr.get("depart"), f"{vid}.scheduled_depart") if vr else None
            depart_delay = actual_depart - scheduled_depart if inserted and scheduled_depart is not None else None
            if inserted and ti is not None and ti.get("departDelay") not in (None, ""):
                _finite_float(ti.get("departDelay"), f"{vid}.departDelay", allow_negative=False)
                is_number_flow_id = cls in flows and vid.startswith(flows[cls]["flow_id"] + ".")
                if is_number_flow_id:
                    schedule_ms = flow_scheduled_depart_ms(
                        flows[cls], int(vid.rsplit(".", 1)[1]))
                    matches = serialized_depart_delay_matches(
                        trip_depart_raw, schedule_ms, ti.get("departDelay"))
                else:
                    expected_delay = Decimal(trip_depart_raw) - Decimal(str(scheduled_depart))
                    matches = abs(Decimal(ti.get("departDelay")) - expected_delay) <= TRIPINFO_TIME_HALF_UNIT
                # tripinfo serializes SUMOTime at --precision (default 2 here).
                # Accept only its mathematical half-unit rounding interval,
                # not a free-standing tolerance.
                if not matches:
                    raise ValueError(f"flow schedule/departDelay reconciliation failed for {vid}")
            core_times = first_core.get(vid, [])
            row = {"run_id": run_id, "vehicle_id": vid, "class": cls,
                   "route_id": flows.get(cls, {}).get("route_id"), "type_id": flows.get(cls, {}).get("type_id"),
                   "scheduled_depart_s": scheduled_depart, "actual_depart_s": actual_depart,
                   "depart_delay_s": depart_delay,
                   "inserted_before_source_end": bool(inserted and actual_depart < DEMAND_END),
                   "inserted_after_source_end": late, "arrival_s": arrival, "arrived_before_horizon": arrived,
                   "arrived_at_horizon_boundary": arrived_at_horizon,
                   "unfinished_at_horizon": unfinished, "never_inserted": never,
                   "first_fcd_s": first_last.get(vid, [None, None])[0],
                   "last_fcd_s": first_last.get(vid, [None, None])[1],
                   "first_core_time_lower_s": min(core_times) - 1 if core_times else None,
                   "first_core_time_upper_s": min(core_times) if core_times else None,
                   "speed_factor_precise": sf,
                   "source_evidence_ids": ";".join(x for x, yes in (("vehroute", vr is not None), ("tripinfo", ti is not None), ("fcd", seen_fcd)) if yes),
                   "status": lifecycle_status, "reasons": ""}
            rows.append(row); crows.append(row)
        f = flows.get(cls)
        requested = (f["number"] if f else 0)
        inserted_n = sum(r["inserted_before_source_end"] for r in crows)
        class_summary.append({"run_id": run_id, "class": cls,
                              "requested_rate_veh_per_h": (
                                  requested * 3600.0 / (f["end"] - f["begin"]) if f else 0.0),
                              "scheduled": len(ids), "inserted_in_demand_window": inserted_n,
                              "inserted_late": sum(r["inserted_after_source_end"] for r in crows),
                              "never_inserted": sum(r["never_inserted"] for r in crows),
                              "arrived_before_horizon": sum(r["arrived_before_horizon"] for r in crows),
                              "arrived_at_horizon_boundary": sum(r["arrived_at_horizon_boundary"] for r in crows),
                              "unfinished_at_horizon": sum(r["unfinished_at_horizon"] for r in crows),
                              "depart_delay_min_s": min((r["depart_delay_s"] for r in crows if r["depart_delay_s"] is not None), default=None),
                              "depart_delay_median_s": statistics.median([r["depart_delay_s"] for r in crows if r["depart_delay_s"] is not None]) if any(r["depart_delay_s"] is not None for r in crows) else None,
                              "depart_delay_max_s": max((r["depart_delay_s"] for r in crows if r["depart_delay_s"] is not None), default=None),
                              "class_source": f["flow_id"] if f else "ABSENT_FROM_SCHEDULE",
                              "r_zero_source_status": "SCHEDULE_ABSENT_AND_RAW_ABSENT" if cls == "R" and not ids and not any(i.startswith("R_") for i in observed) else ("PASS_ZERO" if cls == "R" and not ids else "NOT_ZERO")})
    return rows, class_summary, {"fcd_labels": len(fcd_labels), "fcd_unique_time_id": len(fcd_time_ids),
                                "scheduled_ids": len(scheduled), "observed_ids": len(observed),
                                "unseen_scheduled_ids": len(scheduled - observed), "unexpected_ids": len(unknown_ids),
                                "fcd_errors": fcd_errors, "r_scheduled": len(expected["R"]),
                                "r_observed": sum(i.startswith("R_") for i in observed)}


def _profile_event_intervals(events: list[dict], spatial_events: list[dict]) -> list[dict]:
    rows = []
    for e in events:
        rows.append({"family": e["profile"], "cell": int(e["cell"]),
                     "start_s": 30 * int(e["first_low_bin"]),
                     "end_s": 30 * int(e["low_bin_end_exclusive"]),
                     "source_event_id": e["event_id"], "mask_status": "KNOWN_EVENT_OR_CANDIDATE"})
        if e["profile"] == "L" and e["is_merge_core"] and e["low_speed_bins"] >= 1:
            rows.append({"family": "C", "cell": int(e["cell"]),
                         "start_s": 30 * int(e["first_low_bin"]),
                         "end_s": 30 * int(e["first_low_bin"]) + 30,
                         "source_event_id": "C_FROM_LOCKED_L_WARNING:" + e["event_id"],
                         "mask_status": "KNOWN_EARLY_WARNING"})
    for e in spatial_events:
        rows.append({"family": "A", "cell": int(e["cell_left"]),
                     "start_s": 30 * int(e["common_first_low_bin"]),
                     "end_s": 30 * (int(e["common_first_low_bin"]) + int(e["qualification_bins"])),
                     "source_event_id": e["event_ids"], "mask_status": "KNOWN_SPATIAL_CANDIDATE"})
        rows.append({"family": "A", "cell": int(e["cell_right"]),
                     "start_s": 30 * int(e["common_first_low_bin"]),
                     "end_s": 30 * (int(e["common_first_low_bin"]) + int(e["qualification_bins"])),
                     "source_event_id": e["event_ids"], "mask_status": "KNOWN_SPATIAL_CANDIDATE"})
    return rows


def build_catalog_receipt(events: list[dict], spatial_events: list[dict], masks: list[dict],
                          *, run_id: str, source_sha256: str,
                          method_sha256: str = METHOD_SHA256,
                          analyzer_sha256: str = LOCKED_ANALYZER_SHA256) -> dict:
    """Bind complete event traversal, including valid zero rows, to locked inputs."""
    families = {x: {"source_event_count": 0, "catalog_row_count": 0} for x in ("P", "S", "L", "A", "C")}
    for e in events:
        if e["profile"] in {"P", "S", "L"}:
            families[e["profile"]]["source_event_count"] += 1
    families["A"]["source_event_count"] = len(spatial_events)
    families["C"]["source_event_count"] = sum(
        e["profile"] == "L" and e["is_merge_core"] and e["low_speed_bins"] >= 1 for e in events)
    for row in masks:
        families[row["family"]]["catalog_row_count"] += 1
    ordered = sorted(masks, key=lambda r: (r["family"], r["cell"], r["start_s"], r["end_s"], r["source_event_id"]))
    catalog_fields = ["family", "cell", "start_s", "end_s", "source_event_id", "mask_status"]
    return {"schema_version": "1", "run_id": run_id, "status": "COMPLETE",
            "complete": True, "families": families,
            "source_sha256": source_sha256, "method_sha256": method_sha256,
            "analyzer_sha256": analyzer_sha256,
            "catalog_canonical_sha256": _canonical_sha(ordered),
            "catalog_csv_sha256": hashlib.sha256(csv_bytes(ordered, catalog_fields)).hexdigest(),
            "source_event_count": sum(v["source_event_count"] for v in families.values()),
            "catalog_row_count": len(masks),
            "empty_catalog_is_valid_only_with_this_receipt": True}


def validate_catalog_receipt(receipt: dict | None, masks: list[dict], *, run_id: str,
                             source_sha256: str, method_sha256: str = METHOD_SHA256,
                             analyzer_sha256: str = LOCKED_ANALYZER_SHA256) -> tuple[str, list[str]]:
    if receipt is None:
        return "UNKNOWN", ["CATALOG_RECEIPT_MISSING"]
    reasons = []
    expected_families = {"P", "S", "L", "A", "C"}
    if receipt.get("complete") is not True or receipt.get("status") != "COMPLETE":
        reasons.append("CATALOG_NOT_COMPLETE")
    if receipt.get("run_id") != run_id:
        reasons.append("CATALOG_RUN_MISMATCH")
    if receipt.get("source_sha256") != source_sha256:
        reasons.append("CATALOG_SOURCE_HASH_MISMATCH")
    if receipt.get("method_sha256") != method_sha256 or receipt.get("analyzer_sha256") != analyzer_sha256:
        reasons.append("CATALOG_METHOD_OR_ANALYZER_HASH_MISMATCH")
    fam = receipt.get("families")
    if not isinstance(fam, dict) or set(fam) != expected_families:
        reasons.append("CATALOG_FAMILY_COVERAGE_INCOMPLETE")
    ordered = sorted(masks, key=lambda r: (r["family"], r["cell"], r["start_s"], r["end_s"], r["source_event_id"]))
    if receipt.get("catalog_canonical_sha256") != _canonical_sha(ordered):
        reasons.append("CATALOG_CONTENT_HASH_MISMATCH")
    fields = ["family", "cell", "start_s", "end_s", "source_event_id", "mask_status"]
    if receipt.get("catalog_csv_sha256") != hashlib.sha256(csv_bytes(ordered, fields)).hexdigest():
        reasons.append("CATALOG_CSV_HASH_MISMATCH")
    if receipt.get("catalog_row_count") != len(masks):
        reasons.append("CATALOG_ROW_COUNT_MISMATCH")
    if isinstance(fam, dict):
        actual_rows = Counter(row["family"] for row in masks)
        for family in sorted(expected_families):
            item = fam.get(family, {})
            src_count = item.get("source_event_count")
            row_count = item.get("catalog_row_count")
            expected_rows = actual_rows.get(family, 0)
            source_rows_ok = (src_count == expected_rows if family in {"P", "S", "L", "C"}
                              else isinstance(src_count, int) and src_count * 2 == expected_rows)
            if row_count != expected_rows or not source_rows_ok:
                reasons.append(f"CATALOG_FAMILY_COUNT_MISMATCH:{family}")
    if reasons:
        return "UNKNOWN", reasons
    return "PASS", []


def integrity_disposition(lifecycle: dict, analyzer_integrity: dict) -> tuple[str, list[str]]:
    """Never report PASS when the locked parser emitted a registered blocker/warning."""
    reasons = list(lifecycle.get("fcd_errors", []))
    if lifecycle.get("fcd_labels") != HORIZON:
        reasons.append("FCD_GRID_INCOMPLETE")
    if lifecycle.get("r_scheduled") != 0 or lifecycle.get("r_observed") != 0:
        reasons.append("R_ZERO_INVARIANT_FAILED")
    hard_counts = {
        "duplicate_time_id_warnings": "DUPLICATE_TIME_ID",
        "M_unexpected_lane_samples": "UNKNOWN_M_LANE",
        "M_aux_samples": "M_ON_AUX_LANE",
        "out_of_domain_samples": "M_OUT_OF_DOMAIN",
    }
    for key, label in hard_counts.items():
        if int(analyzer_integrity.get(key, 0) or 0) > 0:
            reasons.append(f"{label}:{analyzer_integrity[key]}")
    warning_text = analyzer_integrity.get("warnings", "") or ""
    warnings = [w for w in warning_text.split(";") if w]
    if warnings:
        reasons.extend(f"ANALYZER_WARNING:{w}" for w in warnings)
    if any(x.startswith(("DUPLICATE_TIME_ID", "UNKNOWN_M_LANE", "M_ON_AUX_LANE", "M_OUT_OF_DOMAIN",
                         "FCD_GRID_INCOMPLETE", "R_ZERO_INVARIANT_FAILED")) for x in reasons):
        return "FAIL", reasons
    if reasons:
        return "UNKNOWN", reasons
    return "PASS", []


def make_lane_bins(raw_fcd: Path, vehroute: Path, network: Path, analyzer, source_hash: str) -> list[dict]:
    """Fixed-resolution 30 s M/M+R metrics for physical lanes 0/1 and pooled."""
    routes = _dict_unique(ET.parse(vehroute).getroot(), "vehicle")
    lane_info = {x.get("id"): {"speed": float(x.get("speed")), "length": float(x.get("length"))}
                 for x in ET.parse(network).getroot().findall(".//lane")}
    rows = []
    fcd = ET.parse(raw_fcd).getroot()
    samples: dict[tuple[int, int, int], list[tuple[str, float, float, int]]] = defaultdict(list)
    # sample key cell, second, physical lane; retain M and R, but M governs speed.
    for ts in fcd.findall("timestep"):
        t = int(float(ts.get("time")))
        for v in ts.findall("vehicle"):
            vid = v.get("id", "")
            cls = vid.split("_", 1)[0]
            lane = v.get("lane")
            if lane not in MAINLINE_LANES or cls not in {"M", "R"}:
                continue
            x = float(v.get("x")); cell, terminal = analyzer.lane_cell(x)
            if cell is None:
                continue
            if cls == "M":
                vr = routes.get(vid)
                if vr is None:
                    raise ValueError(f"M FCD lacks vehroute: {vid}")
                sf = float(vr.get("speedFactor", "nan")); lim = lane_info[lane]["speed"]
                if not math.isfinite(sf) or sf <= 0 or lim <= 0:
                    raise ValueError(f"invalid speed reference for {vid} / {lane}")
                speed = float(v.get("speed")); ratio = speed / (lim * sf)
            else:
                speed = float(v.get("speed")); ratio = None
            samples[(cell, t, MAINLINE_LANES[lane])].append((vid, speed, ratio, 1 if cls == "M" else 0))
    for cell in range(22):
        for scope in SCOPES:
            lane_ids = (0, 1) if scope == "pooled" else (int(scope[-1]),)
            length_m = (min((cell + 1) * 100, 2200) - cell * 100) * len(lane_ids)
            for bstart in range(0, HORIZON, 30):
                vals = [z for t in range(bstart, bstart + 30) for ix in lane_ids
                        for z in samples.get((cell, t, ix), [])]
                m = [z for z in vals if z[3] == 1]
                mr_n = len(vals)
                all_seconds = set(range(bstart, bstart + 30))
                n_m = len(m); uniq = len({z[0] for z in m})
                ratio = sum(z[2] for z in m) / n_m if n_m else None
                abs_speed = sum(z[1] for z in m) / n_m if n_m else None
                slow = sum(z[2] <= ALPHA_P for z in m) / n_m if n_m else None
                simultaneous = sum(any(z[3] == 1 and z[2] <= ALPHA_P for z in samples.get((cell, t, ix), []))
                                   for t in all_seconds for ix in lane_ids)
                density_den = 30 * (length_m / 1000.0)
                m_density = n_m / density_den if density_den else None
                mr_density = mr_n / density_den if density_den else None
                valid = len(all_seconds) == 30 and uniq >= 2 and n_m > 0
                rows.append({"run_id": RUN_ID, "cell": cell, "scope": scope,
                             "bin_start_s": bstart, "bin_end_s": bstart + 30,
                             "observed_labels": 30, "unique_M": uniq, "N_M_samples": n_m,
                             "mean_abs_speed_mps": abs_speed, "mean_ratio": ratio,
                             "slow_fraction_P": slow, "simultaneous_slow_labels": simultaneous,
                             "M_density_veh_per_lane_km": m_density,
                             "MR_density_veh_per_lane_km": mr_density,
                             "valid": valid, "validity_reason": "" if valid else ("NO_M_SAMPLES" if not n_m else "UNIQUE_M_LT_2"),
                             "source_fcd_sha256": source_hash})
    return rows


def _state_for_screen(bin_rows: dict[tuple[int, str, int], dict], masks: list[dict],
                      block: tuple[int, int], cell: int, scope: str) -> dict:
    b0, b1 = block
    reasons = []
    component = []
    for start in range(b0, b1, 30):
        r = bin_rows.get((cell, scope, start))
        if r is None:
            reasons.append(f"MISSING_BIN:{start}"); continue
        component.append(r)
        if r["observed_labels"] != 30:
            reasons.append(f"INCOMPLETE_LABELS:{start}")
        if r["unique_M"] < 2:
            reasons.append(f"UNIQUE_M_LT_2:{start}")
        if r["mean_ratio"] is None:
            reasons.append(f"RATIO_UNKNOWN:{start}")
        elif r["mean_ratio"] < HIGH_MOBILITY_RATIO:
            reasons.append(f"RATIO_LT_0.85:{start}")
        for key in ("M_density_veh_per_lane_km", "MR_density_veh_per_lane_km"):
            value = r[key]
            if value is None or not math.isfinite(value):
                reasons.append(f"DENSITY_UNKNOWN:{key}:{start}")
            elif value <= 0:
                reasons.append(f"DENSITY_NONPOSITIVE:{key}:{start}")
    # Candidate masks intersect the cell and immediate neighbors. Both any-bin
    # overlap and end-at/before-earliest-onset condition are retained explicitly.
    relevant = [m for m in masks if m["cell"] in {cell - 1, cell, cell + 1}]
    earliest = min((m["start_s"] for m in relevant), default=None)
    overlaps = [m for m in relevant if max(b0, m["start_s"]) < min(b1, m["end_s"])]
    if overlaps:
        reasons.append("DISTURBANCE_OVERLAP:" + ";".join(sorted({m["source_event_id"] for m in overlaps})))
    if earliest is not None and b1 > earliest:
        reasons.append(f"BLOCK_END_AFTER_EARLIEST_DISTURBANCE:{earliest}")
    unknown = any(x.startswith(("MISSING_BIN:", "INCOMPLETE_LABELS:", "RATIO_UNKNOWN:", "DENSITY_UNKNOWN:"))
                  for x in reasons)
    status = "PASS" if not reasons and len(component) == 3 else ("UNKNOWN" if unknown else "FAIL")
    return {"cell": cell, "scope": scope, "block_start_s": b0, "block_end_s": b1,
            "constituent_bins": len(component), "status": status,
            "mean_ratio_min": min((r["mean_ratio"] for r in component if r["mean_ratio"] is not None), default=None),
            "M_density_min": min((r["M_density_veh_per_lane_km"] for r in component if r["M_density_veh_per_lane_km"] is not None), default=None),
            "MR_density_min": min((r["MR_density_veh_per_lane_km"] for r in component if r["MR_density_veh_per_lane_km"] is not None), default=None),
            "earliest_disturbance_start_s": earliest,
            "mask_event_ids": ";".join(sorted({m["source_event_id"] for m in relevant})),
            "reasons": ";".join(reasons)}


def screen_rows(lane_bins: list[dict], masks: list[dict], *, catalog_status: str = "PASS",
                catalog_reasons: list[str] | None = None) -> tuple[list[dict], dict, dict]:
    by = {(int(r["cell"]), r["scope"], int(r["bin_start_s"])): r for r in lane_bins}
    pre = [_state_for_screen(by, masks, b, c, s) for b in PRE_BLOCKS for c in CORE_CELLS for s in SCOPES]
    control = [_state_for_screen(by, masks, b, c, s) for b in CONTROL_BLOCKS for c in CORE_CELLS for s in SCOPES]
    if catalog_status != "PASS":
        reason = ";".join(catalog_reasons or ["CATALOG_NOT_VERIFIED"])
        for row in pre + control:
            row["status"] = "UNKNOWN"
            row["reasons"] = ";".join(filter(None, (row["reasons"], reason)))
    pre_status = ("PASS" if len(pre) == 30 and all(r["status"] == "PASS" for r in pre)
                  else "UNKNOWN" if any(r["status"] == "UNKNOWN" for r in pre) else "FAIL")
    control_status = ("PASS" if len(control) == 150 and all(r["status"] == "PASS" for r in control)
                      else "UNKNOWN" if any(r["status"] == "UNKNOWN" for r in control) else "FAIL")
    return pre + control, {"status": pre_status, "expected_rows": 30, "actual_rows": len(pre)}, {
        "status": control_status, "expected_rows": 150, "actual_rows": len(control),
        "window_s": [540, 1440]}


def classifier_status_ok(rows: list[dict]) -> bool:
    keys = {(int(r["cell"]), r["profile"], int(r["bin"])) for r in rows}
    return len(rows) == 22 * 3 * 90 and len(keys) == 22 * 3 * 90


def _apply_impl(raw_dir: Path, output_dir: Path, demand_path: Path = DEMAND,
                network_path: Path = NETWORK) -> dict:
    output_dir = validate_output_destination(output_dir, raw_dir)
    demand_hash = validate_demand_binding(demand_path)
    design_hash = validate_design_binding()
    output_roles, output_roles_hash = validate_output_roles()
    if sha256(network_path) != NETWORK_SHA256:
        raise ValueError("accepted network hash mismatch")
    raw, file_audit = audit_raw_manifest(raw_dir)
    flows, expected = parse_demand_schedule(demand_path)
    ledger, class_summary, lifecycle = build_lifecycle(raw, flows, expected, demand_path=demand_path)
    if lifecycle["r_scheduled"] != 0 or lifecycle["r_observed"] != 0:
        raise ValueError("R=0 invariant violated by schedule or raw output")
    analyzer = load_locked_analyzer()
    # Import only defines functions/constants. Patch globals in memory before a
    # single data pass. Never call its main(), which has historical write paths.
    analyzer.NET = network_path
    results, compatibility_manifest_sha256 = run_locked_analyzer_with_manifest_bridge(
        analyzer, raw_dir, raw_dir / "output_manifest.json", raw)
    raw_receipts, classifier_bins, events, attribution, e1, integrity, spatial_a = results
    expected_classifier_rows = 22 * 3 * 90
    classifier_keys = {(r["cell"], r["profile"], r["bin"]) for r in classifier_bins}
    if len(classifier_bins) != expected_classifier_rows or len(classifier_keys) != expected_classifier_rows:
        raise ValueError("locked classifier output grid incomplete/duplicate; disturbance zero cannot be inferred")
    # Bind the exact, complete locked analyzer tables to a source-coverage
    # receipt. This mapper validates rather than recalculates P/S/L decisions.
    import locked_event_source_adapter as event_source
    import reviewed_attribution_interface as reviewed_attribution
    event_binding = {
        "run_id": raw_dir.name, "run_label": "CTRL",
        "paths": {"method": METHOD, "locked_analyzer": LOCKED_ANALYZER,
                  "design": DESIGN, "output_roles": OUTPUT_ROLES,
                  "raw_manifest": raw_dir / "output_manifest.json"},
        "sha256": {"method": METHOD_SHA256, "locked_analyzer": LOCKED_ANALYZER_SHA256,
                   "design": DESIGN_SHA256, "output_roles": OUTPUT_ROLES_SHA256,
                   "raw_manifest": sha256(raw_dir / "output_manifest.json")},
    }
    mapped_events, locked_event_receipt = event_source.build_locked_event_source(
        classifier_bins, events, attribution, analyzer, event_binding)
    event_source_status, event_source_reasons = event_source.validate_locked_event_source(
        classifier_bins, events, attribution, locked_event_receipt, analyzer, event_binding)
    if event_source_status not in {"PASS", "PASS_ZERO"}:
        raise ValueError(f"locked event source validation failed: {event_source_reasons}")
    review_provenance = {"run_id": RUN_ID, "method_sha256": METHOD_SHA256,
                         "locked_analyzer_sha256": LOCKED_ANALYZER_SHA256,
                         "event_source_sha256": locked_event_receipt["event_source_sha256"]}
    p_review_events = [{key: value for key, value in event.items() if key != "profile"}
                       for event in mapped_events if event["profile"] == "P"]
    review_rows, review_receipt = reviewed_attribution.build_interface(
        p_review_events, review_provenance, reviews=None)
    review_status, review_reasons = reviewed_attribution.validate_receipt(
        review_rows, review_receipt, review_provenance)
    if review_status != "PASS":
        raise ValueError(f"review-interface receipt validation failed: {review_reasons}")
    source = {r["role_inferred_from_manifest_path"]: r["actual_sha256"] for r in raw_receipts}
    mask = sorted(_profile_event_intervals(events, spatial_a),
                  key=lambda r: (r["family"], r["cell"], r["start_s"], r["end_s"], r["source_event_id"]))
    lane_bins = make_lane_bins(raw["fcd.xml"], raw["vehroute.xml"], network_path, analyzer,
                               source["fcd.xml"])
    catalog_receipt = build_catalog_receipt(
        events, spatial_a, mask, run_id=RUN_ID, source_sha256=source["fcd.xml"])
    catalog_status, catalog_reasons = validate_catalog_receipt(
        catalog_receipt, mask, run_id=RUN_ID, source_sha256=source["fcd.xml"])
    screens, pre_gate, control_gate = screen_rows(
        lane_bins, mask, catalog_status=catalog_status, catalog_reasons=catalog_reasons)
    # The analyzer's original output rows and labels remain separately stored.
    classifier_matrix = []
    for rule, profile in (("P", "P"), ("S", "S"), ("L", "L"),
                          ("C_EARLY_WARNING", "L"), ("A_SPATIAL_S", "S")):
        pe = [e for e in events if e["profile"] == profile]
        if rule == "C_EARLY_WARNING":
            chosen = [e for e in pe if e["low_speed_bins"] >= 1 and e["is_merge_core"]]
            result = "EARLY_WARNING_PRESENT_NOT_STATE1" if chosen else "NO_EARLY_WARNING"
        elif rule == "A_SPATIAL_S":
            chosen = spatial_a
            result = "SPATIALLY_CORROBORATED_CANDIDATE_ATTRIBUTION_UNRESOLVED" if chosen else "NO_SPATIAL_CANDIDATE"
        else:
            chosen = [e for e in pe if e["numerical_positive"]]
            if chosen:
                result = "CANDIDATE_ATTRIBUTION_UNRESOLVED"
            elif any(e["event_status"] == "ONSET_REFERENCE_UNRESOLVED" for e in pe):
                result = "ONSET_REFERENCE_UNRESOLVED"
            elif any(e["event_status"] == "DENSITY_GATE_FAIL" for e in pe):
                result = "NO_QUALIFYING_EVENT_WITH_DENSITY_CANDIDATES"
            else:
                result = "NO_QUALIFYING_EVENT"
        classifier_matrix.append({"run_id": RUN_ID, "profile": rule, "classification": result,
                                  "candidate_cell_event_count": len(chosen),
                                  "cell_event_count_not_physical_event_count": True,
                                  "physical_event_count": "NOT_ESTIMATED"})
    output_dir.mkdir(parents=True, exist_ok=False)
    write_csv(output_dir / "vehicle_lifecycle_ledger.csv", ledger)
    write_csv(output_dir / "class_lifecycle_summary.csv", class_summary)
    write_csv(output_dir / "raw_hash_manifest.csv", raw_receipts)
    write_csv(output_dir / "raw_completeness_files.csv", file_audit)
    write_csv(output_dir / "locked_cell_bin_metrics.csv", classifier_bins)
    write_csv(output_dir / "locked_candidate_events.csv", events)
    write_csv(output_dir / "locked_attribution_ledger.csv", attribution)
    write_csv(output_dir / "reviewed_attribution_interface.csv", review_rows)
    (output_dir / "reviewed_attribution_receipt.json").write_text(
        json.dumps(review_receipt, indent=2, allow_nan=False) + "\n")
    (output_dir / "locked_event_source_receipt.json").write_text(
        json.dumps(locked_event_receipt, indent=2, allow_nan=False) + "\n")
    write_csv(output_dir / "locked_candidate_A.csv", spatial_a)
    write_csv(output_dir / "cell_lane_bins.csv", lane_bins)
    catalog_fields = ["family", "cell", "start_s", "end_s", "source_event_id", "mask_status"]
    write_csv(output_dir / "disturbance_mask.csv", mask, catalog_fields)
    (output_dir / "disturbance_catalog_completeness.json").write_text(
        json.dumps(catalog_receipt, indent=2, allow_nan=False) + "\n")
    write_csv(output_dir / "reference_screen_rows.csv", screens)
    write_csv(output_dir / "locked_classifier_summary.csv", classifier_matrix)
    integrity_status, integrity_reasons = integrity_disposition(lifecycle, integrity)
    completeness = {"run_id": RUN_ID, "raw_roles_and_hashes": file_audit,
                    "fcd_label_count": lifecycle["fcd_labels"], "fcd_labels_exact_0_2699": True,
                    "fcd_unique_time_id_count": lifecycle["fcd_unique_time_id"],
                    "class_identity_accounting": lifecycle,
                    "R_zero": {"scheduled": lifecycle["r_scheduled"], "inserted": 0,
                               "arrived": 0, "unfinished": 0, "raw_observed_ids": lifecycle["r_observed"],
                               "source_flow_absent": "R" not in flows,
                               "status": "PASS_ZERO"},
                    "e1_role_count": 9, "analyzer_integrity": integrity,
                    "integrity_status": integrity_status, "integrity_reasons": integrity_reasons,
                    "locked_event_source_status": event_source_status,
                    "locked_event_source_reasons": event_source_reasons,
                    "reviewed_attribution_status": "UNKNOWN_DEFAULT_NO_EXTERNAL_REVIEW",
                    "review_interface_integrity": review_status,
                    "review_interface_reasons": review_reasons,
                    "disturbance_catalog_status": catalog_status,
                    "pre_state_gate": pre_gate, "control_high_mobility_gate": control_gate,
                    "status": integrity_status if classifier_status_ok(classifier_bins) else "FAIL"}
    (output_dir / "raw_completeness.json").write_text(json.dumps(completeness, indent=2, allow_nan=False) + "\n")
    inputs = {"run_id": RUN_ID, "method": {"path": str(METHOD.relative_to(ROOT)), "sha256": sha256(METHOD)},
              "design": {"path": str(DESIGN.relative_to(ROOT)), "sha256": design_hash},
              "locked_analyzer": {"path": str(LOCKED_ANALYZER.relative_to(ROOT)), "sha256": sha256(LOCKED_ANALYZER)},
              "raw_dir": str(raw_dir), "raw_manifest_sha256": sha256(raw_dir / "output_manifest.json"),
              "locked_analyzer_manifest_bridge": {
                  "source_manifest_schema": "R02-v1 artifact_roles + support_files",
                  "projection_schema": "locked analyzer legacy files[path,bytes,sha256]",
                  "source_manifest_sha256": sha256(raw_dir / "output_manifest.json"),
                  "projection_manifest_sha256": compatibility_manifest_sha256,
                  "projection_file_count": len(raw),
                  "projection_paths_are_hash_verified_children_of_raw_run": True,
                  "raw_files_copied_or_modified": False},
              "demand_sha256": demand_hash, "network_sha256": sha256(network_path),
              "output_roles": {"path": str(OUTPUT_ROLES.relative_to(ROOT)), "sha256": output_roles_hash,
                               "required_role_count": output_roles["required_role_count"]},
              "locked_event_source": {"receipt_path": "locked_event_source_receipt.json",
                                      "receipt_sha256": sha256(output_dir / "locked_event_source_receipt.json"),
                                      "event_source_sha256": locked_event_receipt["event_source_sha256"],
                                      "status": event_source_status,
                                      "complete_profile_event_count": locked_event_receipt["source_event_count"]},
              "reviewed_attribution_interface": {
                  "receipt_path": "reviewed_attribution_receipt.json",
                  "receipt_sha256": sha256(output_dir / "reviewed_attribution_receipt.json"),
                  "status": review_status,
                  "P_event_count": review_receipt["event_count"],
                  "review_state": "UNKNOWN_DEFAULT_NO_EXTERNAL_REVIEW"},
              "adapter_sha256": sha256(Path(__file__)),
              "semantics": {"P/S/L/A/C": "unchanged hash-bound locked analyzer", "R0": "independent source+raw identity audit",
                            "screens": "fixed execution-spec windows; not a State 1 classifier"}}
    (output_dir / "input_manifest.json").write_text(json.dumps(inputs, indent=2, allow_nan=False) + "\n")
    outputs = {str(p.name): sha256(p) for p in sorted(output_dir.iterdir()) if p.is_file()}
    receipt = {"status": "OFFLINE_CONTROL_APPLICATION_COMPLETED", "run_id": RUN_ID,
               "method_sha256": METHOD_SHA256, "locked_analyzer_sha256": LOCKED_ANALYZER_SHA256,
               "source_manifest_sha256": sha256(raw_dir / "output_manifest.json"),
               "compatibility_manifest_sha256": compatibility_manifest_sha256,
               "adapter_sha256": sha256(Path(__file__)), "output_hashes": outputs,
               "raw_completeness": completeness["status"], "lifecycle_rows": len(ledger),
               "R0_summary": completeness["R_zero"],
              "disturbance_catalog_status": catalog_status, "pre_gate": pre_gate,
               "control_gate": control_gate, "locked_event_source_status": event_source_status,
               "reviewed_attribution_status": "UNKNOWN_DEFAULT_NO_EXTERNAL_REVIEW",
               "sumo_started": False}
    (output_dir / "application_receipt.json").write_text(json.dumps(receipt, indent=2, allow_nan=False) + "\n")
    processing_records = {p.name: sha256(p) for p in sorted(output_dir.iterdir())
                          if p.is_file() and p.name != "processing_manifest.json"}
    processing_manifest = {"schema_version": 1, "run_id": RUN_ID,
                          "status": "COMPLETE_OUTPUT_HASH_COVERAGE",
                          "application_receipt": {"path": "application_receipt.json",
                                                  "sha256": processing_records["application_receipt.json"],
                                                  "adapter_sha256": receipt["adapter_sha256"],
                                                  "input_manifest_sha256": sha256(output_dir / "input_manifest.json"),
                                                  "raw_manifest_sha256": inputs["raw_manifest_sha256"]},
                          "artifact_hashes": processing_records}
    (output_dir / "processing_manifest.json").write_text(
        json.dumps(processing_manifest, indent=2, allow_nan=False) + "\n")
    return receipt


def _record_preflight_failure(output_dir: Path, status: str, reason: str) -> None:
    """Persist a fail-closed completeness result when parsing stops before normal outputs."""
    output_dir.mkdir(parents=True, exist_ok=True)
    target = output_dir / "raw_completeness.json"
    if target.exists():
        return
    result = {"run_id": RUN_ID, "status": status, "stage": "PREFLIGHT_OR_PARSE",
              "reasons": [reason], "R_zero": "UNKNOWN",
              "classifier_application": "NOT_COMPLETED", "sumo_started": False}
    target.write_text(json.dumps(result, indent=2, allow_nan=False) + "\n")
    receipt = {"status": "NOT_EVALUABLE_RAW_COMPLETENESS", "run_id": RUN_ID,
               "raw_completeness": status, "reasons": [reason], "sumo_started": False}
    (output_dir / "application_receipt.json").write_text(json.dumps(receipt, indent=2) + "\n")


def apply(raw_dir: Path, output_dir: Path, demand_path: Path = DEMAND,
          network_path: Path = NETWORK) -> dict:
    validate_output_destination(output_dir, raw_dir)
    try:
        return _apply_impl(raw_dir, output_dir, demand_path, network_path)
    except (ValueError, FileNotFoundError, KeyError, ET.ParseError) as exc:
        msg = f"{type(exc).__name__}:{exc}"
        lowered = str(exc).lower()
        status = "UNKNOWN" if any(x in lowered for x in
                                  ("missing", "incomplete", "not exact", "not found", "manifest")) else "FAIL"
        _record_preflight_failure(output_dir, status, msg)
        raise


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--raw-dir", type=Path, required=True, help="immutable run directory containing output_manifest.json")
    ap.add_argument("--output-dir", type=Path, required=True, help="new, non-existing processed output directory")
    ap.add_argument("--demand", type=Path, default=DEMAND)
    ap.add_argument("--network", type=Path, default=NETWORK)
    args = ap.parse_args(argv)
    print(json.dumps(apply(args.raw_dir, args.output_dir, args.demand, args.network), indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

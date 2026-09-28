#!/usr/bin/env python3
"""Build immutable, hash-bound inputs for CLEAN3199 Candidate A (no execution)."""
from __future__ import annotations
import copy, hashlib, json
from pathlib import Path
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[3]
PKG = ROOT / "artifacts/stage6_clean_onset_3199_r900_preparation_20260925_v1"
RUN = "CLEAN3199_A_R900_DELAYED_S17"
OUT_REL = f"data/raw/stage6_clean_onset_3199_ux0_20260925_v1/{RUN}/outputs"
CONTROL = ROOT / "scripts/stage6/minimal3199/prepared_rev3/control"
NETWORK = ROOT / "artifacts/stage6_baseline_localization_20260921_v1/LOC_M3350_S17/engineering/build_attempts/TV_BUILD01/network.net.xml"
R900 = ROOT / "artifacts/stage6_minimal3350_e1_r900_preparation_20260925_rev20/inputs/treatment/r900_vehicle_source.rou.xml"
DEST = PKG / "inputs/treatment"

def sha(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()

def dump_json(p: Path, obj: object) -> None:
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(obj, indent=2, sort_keys=True) + "\n", encoding="utf-8")

def ms(s: str) -> int:
    # source depart values are exact decimal seconds; SUMO 1.26 uses ms ticks.
    from decimal import Decimal
    d = Decimal(s) * 1000
    if d != d.to_integral_value():
        raise ValueError(f"non-integer-ms depart: {s}")
    return int(d)

def main() -> None:
    DEST.mkdir(parents=True, exist_ok=True)
    control_tree = ET.parse(CONTROL / "demand.rou.xml")
    source_tree = ET.parse(R900)
    croot, rroot = control_tree.getroot(), source_tree.getroot()
    for tag in ("route", "vType"):
        cdefs = sorted((x.tag, tuple(sorted(x.attrib.items()))) for x in croot.findall(tag))
        rdefs = sorted((x.tag, tuple(sorted(x.attrib.items()))) for x in rroot.findall(tag))
        if cdefs != rdefs:
            raise SystemExit(f"route/vType definitions differ: {tag}")
    m_control = {v.get("id"): v for v in croot.findall("vehicle") if v.get("id", "").startswith("M_flow.")}
    if len(m_control) != 1333:
        raise SystemExit(f"expected 1333 M, got {len(m_control)}")
    if any(v.get("id", "").startswith(("U_flow.", "X_flow.")) for v in croot.findall("vehicle")):
        raise SystemExit("control U/X must be explicit zero")
    rs = [copy.deepcopy(v) for v in rroot.findall("vehicle") if v.get("id", "").startswith("R_flow.")]
    if len(rs) != 240 or {v.get("id") for v in rs} != {f"R_flow.{i}" for i in range(240)}:
        raise SystemExit(f"expected R_flow.0..239, got {len(rs)}")
    # Only materialized R vehicles are added. Existing route and vType definitions are retained once.
    treatment_root = copy.deepcopy(croot)
    vehicles = treatment_root.findall("vehicle")
    treatment_root[:] = [e for e in treatment_root if e.tag != "vehicle"]
    vehicles.extend(rs)
    vehicles.sort(key=lambda v: (ms(v.attrib["depart"]), v.attrib["id"]))
    for v in vehicles:
        treatment_root.append(v)
    demand = DEST / "demand.rou.xml"
    ET.ElementTree(treatment_root).write(demand, encoding="utf-8", xml_declaration=True)
    # Reparse serialized bytes and verify exact M attribute equality, explicit U/X zero, R-only delta.
    troot = ET.parse(demand).getroot()
    tvehicles = troot.findall("vehicle")
    m_treatment = {v.get("id"): v for v in tvehicles if v.get("id", "").startswith("M_flow.")}
    if m_control.keys() != m_treatment.keys():
        raise SystemExit("M ID set mismatch")
    fields = ("id", "depart", "route", "type", "speedFactor", "departLane", "departPos", "departSpeed", "arrivalLane", "arrivalPos", "arrivalSpeed", "line", "color", "personNumber", "containerNumber")
    def attrs(v): return tuple(v.get(k) for k in fields if v.get(k) is not None)
    if any(attrs(m_control[k]) != attrs(m_treatment[k]) for k in m_control):
        raise SystemExit("M per-vehicle identity/schedule/route/type/speedFactor/attributes mismatch")
    if any(v.get("id", "").startswith(("U_flow.", "X_flow.")) for v in tvehicles):
        raise SystemExit("treatment U/X must be explicit zero")
    if len([v for v in tvehicles if v.get("id", "").startswith("R_flow.")]) != 240:
        raise SystemExit("R-only addition must equal 240 vehicles")
    ordering = [(ms(v.attrib["depart"]), v.attrib["id"]) for v in tvehicles]
    if ordering != sorted(ordering):
        raise SystemExit("global input ordering invalid")
    same_tick = {}
    for tick, vid in ordering: same_tick.setdefault(tick, []).append(vid)
    ties = {t: ids for t, ids in same_tick.items() if len(ids) > 1}
    if len(ties) != 27:
        raise SystemExit(f"expected 27 exact-time M/R ties, got {len(ties)}")

    output_roles_src = CONTROL / "output_roles.json"
    roles = json.loads(output_roles_src.read_text(encoding="utf-8"))
    old_root = "data/raw/stage6_minimal3199_existence_20260924_v1/MINIMAL3199_CTRL_S17/outputs"
    abs_old = str(ROOT / old_root)
    abs_new = str(ROOT / OUT_REL)
    output_roles_bytes = output_roles_src.read_text(encoding="utf-8").replace(abs_old, abs_new)
    if output_roles_bytes.count(abs_old) != 0 or output_roles_bytes.count(abs_new) != 18:
        raise SystemExit("output role path replacement count mismatch")
    role_path = DEST / "output_roles.json"
    role_path.write_text(output_roles_bytes, encoding="utf-8")

    add_src = CONTROL / "scenario.add.xml"
    add_text = add_src.read_text(encoding="utf-8")
    if add_text.count(abs_old) != 12:
        raise SystemExit("source additional output-root reference count is not 12")
    add_text = add_text.replace(abs_old, abs_new)
    add_path = DEST / "scenario.add.xml"
    add_path.write_text(add_text, encoding="utf-8")

    cfg_src = CONTROL / "scenario.sumocfg"
    cfg_text = cfg_src.read_text(encoding="utf-8")
    src_demand = str(CONTROL / "demand.rou.xml")
    src_add = str(CONTROL / "scenario.add.xml")
    if cfg_text.count(src_demand) != 1 or cfg_text.count(src_add) != 1 or cfg_text.count(abs_old) != 8:
        raise SystemExit("source sumocfg reference counts mismatch")
    cfg_text = cfg_text.replace(src_demand, str(demand)).replace(src_add, str(add_path)).replace(abs_old, abs_new)
    cfg_path = DEST / "scenario.sumocfg"
    cfg_path.write_text(cfg_text, encoding="utf-8")
    # Nested references and all destination paths are checked before recording hashes.
    config = ET.parse(cfg_path).getroot()
    adds = [e.get("value") for e in config.findall("./input/additional-files")]
    if adds != [str(add_path.resolve())]:
        raise SystemExit(f"sumocfg nested additional reference mismatch: {adds}")
    for elem in ET.parse(add_path).getroot():
        for attr in ("file", "dest"):
            value = elem.get(attr)
            if value and not Path(value).resolve(strict=False).is_relative_to((ROOT / OUT_REL).resolve(strict=False)):
                raise SystemExit(f"additional output escapes run root: {value}")
    if OUT_REL in [str(p.relative_to(ROOT)) for p in (ROOT / "data/raw").glob("**/outputs") if p.exists()]:
        raise SystemExit("candidate output already exists")
    # Reconfirm absence of target and immediate parent; preparation must not create raw output directories.
    output = ROOT / OUT_REL
    if output.exists() or output.parent.exists():
        raise SystemExit("candidate output path/parent already exists")

    manifest = {
        "schema": "clean_onset_candidate_a_input_manifest_v1",
        "run_id": RUN,
        "pair_id": "PAIR_3199_S17",
        "design_plan_sha256": sha(ROOT / "artifacts/stage6_clean_onset_witness_test_plan_20260925_v1/CLEAN_ONSET_WITNESS_TEST.md"),
        "input_order": "global stable sort by SUMOTime integer milliseconds, then vehicle ID; retained control ordering except R insertion",
        "planned_counts": {"M": 1333, "R": 240, "U": 0, "X": 0},
        "M_vehicle_match": {"control_path": "scripts/stage6/minimal3199/prepared_rev3/control/demand.rou.xml", "identity_count": 1333, "fields_checked": list(fields), "exact": True},
        "R_only_delta": True,
        "R_ids": ["R_flow.0", "R_flow.239"],
        "exact_depart_ties_count": len(ties),
        "source_hashes": {
            "scripts/stage6/minimal3199/prepared_rev3/control/demand.rou.xml": sha(CONTROL / "demand.rou.xml"),
            "artifacts/stage6_minimal3350_e1_r900_preparation_20260925_rev20/inputs/treatment/r900_vehicle_source.rou.xml": sha(R900),
            "artifacts/stage6_baseline_localization_20260921_v1/LOC_M3350_S17/engineering/build_attempts/TV_BUILD01/network.net.xml": sha(NETWORK),
            "scripts/stage6/minimal3199/prepared_rev3/control/scenario.add.xml": sha(add_src),
            "scripts/stage6/minimal3199/prepared_rev3/control/scenario.sumocfg": sha(cfg_src),
            "scripts/stage6/minimal3199/prepared_rev3/control/output_roles.json": sha(output_roles_src),
        },
        "inputs": {"demand": "inputs/treatment/demand.rou.xml", "additional": "inputs/treatment/scenario.add.xml", "sumocfg": "inputs/treatment/scenario.sumocfg", "output_roles": "inputs/treatment/output_roles.json", "network": "artifacts/stage6_baseline_localization_20260921_v1/LOC_M3350_S17/engineering/build_attempts/TV_BUILD01/network.net.xml"},
        "input_sha256": {"demand": sha(demand), "additional": sha(add_path), "sumocfg": sha(cfg_path), "output_roles": sha(role_path), "network": sha(NETWORK)},
        "output_directory": OUT_REL,
        "output_path_status": "ABSENT_PARENT_ABSENT_NO_DIRECTORY_CREATED",
    }
    dump_json(PKG / "INPUT_MANIFEST.json", manifest)
    dump_json(PKG / "M_MATCH_CHECK.json", {"status":"PASS","M_count":1333,"identities_exact":True,"depart_route_vType_speedFactor_all_attributes_exact":True,"U_zero_control_and_treatment":True,"X_zero_control_and_treatment":True,"R_only_treatment_delta":True,"R_count":240,"global_input_order":"(depart_ms,id)","same_tick_tie_groups":len(ties)})
    print(json.dumps({"run_id":RUN,"counts":manifest["planned_counts"],"M_match":"PASS 1333/1333","R_only":"PASS R_flow.0..239","ties":len(ties),"hashes":manifest["input_sha256"],"output_absent":True},indent=2))

if __name__ == "__main__": main()

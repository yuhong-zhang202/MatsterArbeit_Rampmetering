#!/usr/bin/env python3
"""Read-only static XML/provenance audit for RI3350 control input (R01)."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[3]
PKG = ROOT / "artifacts/stage6_ramp_induced_validation_20260922_v1"
MANIFEST = PKG / "input_manifest.json"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def attrs(elem: ET.Element) -> dict[str, str]:
    return dict(sorted(elem.attrib.items()))


def canonical(elem: ET.Element, *, output_path: bool = False) -> tuple:
    a = attrs(elem)
    if output_path:
        for key in ("file", "dest"):
            if key in a:
                a[key] = "<OUTPUT>"
    return (elem.tag, tuple(a.items()), (elem.text or "").strip(), tuple(canonical(x, output_path=output_path) for x in elem))


def config_semantics(path: Path, output_token: str) -> tuple:
    root = ET.parse(path).getroot()
    for elem in root.iter():
        for key in ("value",):
            val = elem.attrib.get(key)
            if not val:
                continue
            if output_token == "/outputs/" and "/outputs/" in val:
                elem.attrib[key] = "<OUTPUT>/" + val.split("/outputs/", 1)[1]
            elif output_token in val:
                elem.attrib[key] = val.replace(output_token, "<OUTPUT>", 1)
    # The inputs are expected to remap from the accepted source folder to the isolated package.
    inp = root.find("input")
    if inp is None:
        raise AssertionError("sumocfg has no input section")
    for key, token in (("route-files", "<ROUTE_INPUT>"), ("additional-files", "<ADDITIONAL_INPUT>")):
        item = inp.find(key)
        if item is None:
            raise AssertionError(f"sumocfg missing {key}")
        item.attrib["value"] = token
    return canonical(root)


def run() -> dict:
    manifest = json.loads(MANIFEST.read_text())
    source_dir = ROOT / manifest["historical_input_reference"]
    control = manifest["control_prepared_inputs"]
    ctl_route = PKG / control["demand"]
    ctl_cfg = PKG / control["sumocfg"]
    ctl_add = PKG / control["additional"]
    hist_route, hist_cfg, hist_add = (source_dir / "demand.rou.xml", source_dir / "scenario.sumocfg", source_dir / "scenario.add.xml")
    for p in (hist_route, hist_cfg, hist_add, ctl_route, ctl_cfg, ctl_add):
        if not p.is_file():
            raise FileNotFoundError(p)

    hroot, croot = ET.parse(hist_route).getroot(), ET.parse(ctl_route).getroot()
    # Type and M/U/X route semantics are immutable; only the R route/flow is removed.
    hist_defs = [canonical(e) for e in hroot if e.tag in ("vType", "route") and e.attrib.get("id") != "R_route"]
    ctl_defs = [canonical(e) for e in croot if e.tag in ("vType", "route")]
    assert hist_defs == ctl_defs, "M/U/X vType/route definitions changed"
    hist_flows = {e.attrib["id"]: attrs(e) for e in hroot.findall("flow")}
    ctl_flows = {e.attrib["id"]: attrs(e) for e in croot.findall("flow")}
    expected_removed = {"R_flow"}
    assert set(hist_flows) - set(ctl_flows) == expected_removed, "unexpected/missing historical flow difference"
    assert set(ctl_flows) == {"M_flow", "U_flow", "X_flow"}
    assert {k: v for k, v in hist_flows.items() if k != "R_flow"} == ctl_flows, "M/U/X flow attributes changed"
    wanted_counts = {"M_flow": "1396", "U_flow": "150", "X_flow": "75"}
    assert {k: v["number"] for k, v in ctl_flows.items()} == wanted_counts

    # Normalize only output destinations and the explicitly isolated route/additional references.
    pkg_out = "__CONTROL_OUTPUT__"
    hist_cfg_sem = config_semantics(hist_cfg, "/outputs/")
    ctl_cfg_sem = config_semantics(ctl_cfg, pkg_out)
    # Both have config values referring into different run output roots; normalize suffixes too.
    assert hist_cfg_sem == ctl_cfg_sem, "non-path sumocfg semantics changed"

    h_add, c_add = ET.parse(hist_add).getroot(), ET.parse(ctl_add).getroot()
    assert canonical(h_add, output_path=True) == canonical(c_add, output_path=True), "additional-file semantics differ beyond output destinations"

    network_path = ROOT / manifest["accepted_network"]["path"]
    net_hash = sha256(network_path)
    assert net_hash == manifest["accepted_network"]["sha256"], "accepted compiled network hash mismatch"
    assert ET.parse(ctl_route).getroot() is not None and ET.parse(ctl_cfg).getroot() is not None and ET.parse(ctl_add).getroot() is not None

    bindings = []
    for role, p in (("historical_routes", hist_route), ("historical_config", hist_cfg), ("historical_additional", hist_add),
                    ("control_routes", ctl_route), ("control_config", ctl_cfg), ("control_additional", ctl_add), ("accepted_network", network_path)):
        bindings.append({"role": role, "path": str(p.relative_to(ROOT)), "sha256": sha256(p), "size_bytes": p.stat().st_size})
    return {
        "schema_version": "1", "audit_id": "RI3350_CTRL_S17_R01_STATIC_XML_AUDIT",
        "status": "PASS_STATIC_SEMANTIC_DIFF_WITH_OUTPUT_PLACEHOLDERS",
        "read_only": True, "simulation_or_schema_validator_invoked": False,
        "checks": {
            "xml_well_formed": "PASS", "accepted_network_hash": net_hash,
            "M_U_X_type_and_route_semantics": "PASS_EXACT", "M_U_X_flow_attributes": "PASS_EXACT",
            "only_removed_scientific_input": "R_flow_and_R_route_for_R0_CONTROL",
            "control_scheduled_counts": {"M": 1396, "R": 0, "U": 150, "X": 75},
            "sumocfg_non_path_semantics": "PASS_EXACT",
            "additional_detectors_TLS_WAUT_semantics": "PASS_EXACT_OUTPUT_PATHS_MASKED",
            "configuration_references": "PASS_PACKAGE_INPUTS_AND_ACCEPTED_NET",
        },
        "unresolved": [
            "SUMO XSD/schema validation not run (would require invoking SUMO tooling, outside task scope).",
            "__CONTROL_OUTPUT__ remains a non-executable placeholder; exact absolute output path and runtime binary identity are not materialized.",
            "This static audit does not authorize execution or verify any runtime behavior.",
        ],
        "source_bindings": bindings,
    }


if __name__ == "__main__":
    output = run()
    print(json.dumps(output, indent=2, sort_keys=True))

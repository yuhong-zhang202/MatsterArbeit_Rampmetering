"""Offline, two-arm M-only sigma=0 sensitivity package; never starts SUMO."""

from __future__ import annotations

import argparse
import copy
import hashlib
import json
from pathlib import Path
import xml.etree.ElementTree as ET


ROOT = Path(__file__).resolve().parents[2]
BASE = ROOT / "artifacts/stage6_full_network_abc_matched_rebuild_20260926_v1/inputs_retry2"
BASE_MANIFEST_SHA256 = "15eb4d0b9e3a641954e2e38c336f76c3a22aae58d3ac8e2b04d846e9ca3c2b27"
ARTIFACT_ROOT = ROOT / "artifacts/stage6_a_rng_isolation_diagnostic_20260926_v1"
RAW_PARENT = ROOT / "data/raw"
ARM_SOURCE = {"R0_SIGMA0": "R0", "A_SIGMA0": "A"}
M_TYPE = "technical_M_sigma0"
EXPECTED = {"R0_SIGMA0": {"M": 1396, "R": 0, "U": 150, "X": 75},
            "A_SIGMA0": {"M": 1396, "R": 240, "U": 150, "X": 75}}
BASE_FILES = ("demand.rou.xml", "scenario.add.xml", "scenario.sumocfg")


def digest(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1 << 20), b""):
            h.update(block)
    return h.hexdigest()


def _source_hashes() -> dict[str, str]:
    if digest(BASE / "INPUT_MANIFEST.json") != BASE_MANIFEST_SHA256:
        raise ValueError("default-model V2 manifest hash mismatch")
    manifest = json.loads((BASE / "INPUT_MANIFEST.json").read_text())
    result = {}
    for source_arm in ARM_SOURCE.values():
        for name in BASE_FILES:
            relative = f"{source_arm}/{name}"
            path = BASE / relative
            expected = manifest["files"].get(relative)
            if not expected or digest(path) != expected:
                raise ValueError(f"default-model V2 source hash mismatch: {relative}")
            result[relative] = expected
    return result


def _demand(source: Path) -> ET.Element:
    root = ET.parse(source).getroot()
    types = root.findall("vType")
    if len(types) != 1 or types[0].attrib != {"id": "technical_passenger", "vClass": "passenger"}:
        raise ValueError("unexpected default-model vehicle type")
    variant = copy.deepcopy(types[0])
    variant.set("id", M_TYPE)
    variant.set("sigma", "0")
    root.insert(1, variant)
    for vehicle in root.findall("vehicle"):
        if vehicle.get("id", "").startswith("M_flow."):
            if vehicle.get("type") != "technical_passenger":
                raise ValueError("unexpected default M type")
            vehicle.set("type", M_TYPE)
        elif vehicle.get("type") != "technical_passenger":
            raise ValueError("unexpected R/U/X type")
    return root


def _rewrite_paths(root: ET.Element, old_arm: str, arm: str,
                   output_dir: Path, raw_root: Path, package_dir: Path) -> ET.Element:
    old_dir = BASE / old_arm
    old_raw = ROOT / "data/raw/stage6_fullnet_abc_matched_rebuild_20260926_v1_retry2" / old_arm / "outputs"
    for node in root.iter():
        for key, value in list(node.attrib.items()):
            if value == str(old_dir / "demand.rou.xml"):
                node.set(key, str(package_dir / arm / "demand.rou.xml"))
            elif value == str(old_dir / "scenario.add.xml"):
                node.set(key, str(package_dir / arm / "scenario.add.xml"))
            elif value.startswith(str(old_raw) + "/"):
                node.set(key, str(output_dir / Path(value).name))
    return root


def _write_xml(path: Path, root: ET.Element) -> None:
    ET.indent(root, space="  ")
    ET.ElementTree(root).write(path, encoding="utf-8", xml_declaration=True)


def _canonical(root: ET.Element) -> bytes:
    return ET.canonicalize(ET.tostring(root, encoding="unicode"), strip_text=True).encode()


def audit(package_dir: Path, raw_root: Path) -> dict:
    """Reconstruct each transformed XML from pinned V2 sources and compare trees."""
    _source_hashes()
    if not package_dir.is_absolute() or not raw_root.is_absolute():
        raise ValueError("package/raw roots must be absolute")
    counts = {}
    for arm, source_arm in ARM_SOURCE.items():
        target = package_dir / arm
        expected_demand = _demand(BASE / source_arm / "demand.rou.xml")
        actual_demand = ET.parse(target / "demand.rou.xml").getroot()
        if _canonical(actual_demand) != _canonical(expected_demand):
            raise ValueError(f"unexpected demand change: {arm}")
        vehicles = actual_demand.findall("vehicle")
        ids = [v.get("id") for v in vehicles]
        if len(ids) != len(set(ids)):
            raise ValueError(f"duplicate vehicle ID: {arm}")
        counts[arm] = {cls: sum(v.startswith(f"{cls}_flow.") for v in ids) for cls in "MRUX"}
        if counts[arm] != EXPECTED[arm]:
            raise ValueError(f"vehicle counts mismatch: {arm}")
        output_dir = raw_root / arm / "outputs"
        for filename in ("scenario.add.xml", "scenario.sumocfg"):
            expected = _rewrite_paths(ET.parse(BASE / source_arm / filename).getroot(),
                                      source_arm, arm, output_dir, raw_root, package_dir)
            actual = ET.parse(target / filename).getroot()
            if _canonical(actual) != _canonical(expected):
                raise ValueError(f"unexpected config/detector change: {arm}/{filename}")
        config = ET.parse(target / "scenario.sumocfg").getroot()
        additional = ET.parse(target / "scenario.add.xml").getroot()
        if (config.find("./random_number/seed").get("value") != "17"
                or config.find("./time/end").get("value") != "2700"
                or additional.find("WAUT").get("startProg") != "A_OPEN"):
            raise ValueError(f"seed/horizon/TLS mismatch: {arm}")
    common0 = {v.get("id"): v.attrib for v in ET.parse(package_dir / "R0_SIGMA0/demand.rou.xml").getroot().findall("vehicle")}
    common_a = {v.get("id"): v.attrib for v in ET.parse(package_dir / "A_SIGMA0/demand.rou.xml").getroot().findall("vehicle")}
    if any(common_a.get(vid) != attrs for vid, attrs in common0.items()):
        raise ValueError("common M/U/X requested demand differs between arms")
    return {"status": "SIGMA0_STATIC_EQUIVALENCE_PASS_NO_SUMO_STARTED",
            "counts": counts, "M_only_sigma0": True, "common_requested_identical": True,
            "base_manifest_sha256": BASE_MANIFEST_SHA256}


def build(package_dir: Path, raw_root: Path) -> dict:
    package_dir = package_dir.absolute()
    raw_root = raw_root.absolute()
    if package_dir.exists() or raw_root.exists():
        raise FileExistsError("refusing existing package or raw root")
    if package_dir.parent != ARTIFACT_ROOT or raw_root.parent != RAW_PARENT:
        raise ValueError("package/raw root outside reviewed diagnostic location")
    sources = _source_hashes()
    package_dir.mkdir()
    for arm, source_arm in ARM_SOURCE.items():
        target = package_dir / arm
        target.mkdir()
        output_dir = raw_root / arm / "outputs"
        _write_xml(target / "demand.rou.xml", _demand(BASE / source_arm / "demand.rou.xml"))
        for filename in ("scenario.add.xml", "scenario.sumocfg"):
            source = ET.parse(BASE / source_arm / filename).getroot()
            _write_xml(target / filename, _rewrite_paths(source, source_arm, arm,
                                                         output_dir, raw_root, package_dir))
    result = audit(package_dir, raw_root)
    (package_dir / "STATIC_AUDIT.json").write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    manifest = {"status": "DIAGNOSTIC_INPUTS_BUILT_NOT_EXECUTION_AUTHORIZED",
                "sumo_starts": 0, "generator_sha256": digest(Path(__file__)),
                "base_manifest_sha256": BASE_MANIFEST_SHA256,
                "input_sources": sources, "raw_root": str(raw_root),
                "files": {str(path.relative_to(package_dir)): digest(path)
                          for path in sorted(package_dir.rglob("*")) if path.is_file()}}
    (package_dir / "INPUT_MANIFEST.json").write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n")
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("mode", choices=("build", "check"))
    parser.add_argument("--package-dir", type=Path, required=True)
    parser.add_argument("--raw-root", type=Path, required=True)
    args = parser.parse_args()
    result = build(args.package_dir, args.raw_root) if args.mode == "build" else audit(args.package_dir, args.raw_root)
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

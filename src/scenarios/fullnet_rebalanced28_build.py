"""Build one immutable Stage 6 B_REBALANCED28 input package offline.

The default-model V2 A demand is copied byte-for-byte. Only the new ramp-mid
signal program, its WAUT selection, and arm-specific input/output paths change.
This module never starts SUMO and makes no scientific outcome judgment.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import shutil
import xml.etree.ElementTree as ET


ROOT = Path(__file__).resolve().parents[2]
ARTIFACT_ROOT = ROOT / "artifacts/stage6_moderate_rebalance_20260926_v1"
RAW_ROOT = ROOT / "data/raw/stage6_moderate_rebalance_20260926_v1"
BASE = ROOT / "artifacts/stage6_full_network_abc_matched_rebuild_20260926_v1/inputs_retry2"
BASE_MANIFEST_SHA256 = "15eb4d0b9e3a641954e2e38c336f76c3a22aae58d3ac8e2b04d846e9ca3c2b27"
ARM = "B_REBALANCED28"
RUN_ID = "FULLNET3350_B_REBALANCED28_R900_S17_V1"
FILES = ("demand.rou.xml", "scenario.add.xml", "scenario.sumocfg")


def digest(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1 << 20), b""):
            h.update(block)
    return h.hexdigest()


def source_hashes() -> dict[str, str]:
    if digest(BASE / "INPUT_MANIFEST.json") != BASE_MANIFEST_SHA256:
        raise ValueError("default V2 manifest hash mismatch")
    manifest = json.loads((BASE / "INPUT_MANIFEST.json").read_text())
    result = {}
    for name in FILES:
        relative = f"A/{name}"
        expected = manifest["files"].get(relative)
        if not expected or digest(BASE / relative) != expected:
            raise ValueError(f"default V2 A source mismatch: {relative}")
        result[relative] = expected
    return result


def _replace_path(value: str, old: Path, new: Path) -> str:
    if value == str(old):
        return str(new)
    raise ValueError(f"unexpected source path: {value}")


def _additional(output_dir: Path) -> ET.Element:
    root = ET.parse(BASE / "A/scenario.add.xml").getroot()
    selectors = root.findall("WAUT")
    if len(selectors) != 1 or selectors[0].get("startProg") != "A_OPEN":
        raise ValueError("unexpected source WAUT")
    if root.findall("tlLogic"):
        raise ValueError("source additional already has tlLogic")
    old_output = ROOT / "data/raw/stage6_fullnet_abc_matched_rebuild_20260926_v1_retry2/A/outputs"
    for node in root.iter():
        if node.tag in {"inductionLoop", "laneAreaDetector"}:
            path = node.get("file")
            node.set("file", _replace_path(path, old_output / Path(path).name,
                                           output_dir / Path(path).name))
        elif node.tag == "timedEvent":
            path = node.get("dest")
            node.set("dest", _replace_path(path, old_output / Path(path).name,
                                           output_dir / Path(path).name))
    program = ET.Element("tlLogic", {"id": "ramp_mid", "type": "static",
                                      "programID": ARM, "offset": "0"})
    for duration, state in (("28", "G"), ("3", "y"), ("29", "r")):
        ET.SubElement(program, "phase", {"duration": duration, "state": state})
    root.insert(list(root).index(selectors[0]), program)
    selectors[0].set("startProg", ARM)
    return root


def _config(package_dir: Path, output_dir: Path) -> ET.Element:
    root = ET.parse(BASE / "A/scenario.sumocfg").getroot()
    old_arm = BASE / "A"
    new_arm = package_dir / ARM
    old_output = ROOT / "data/raw/stage6_fullnet_abc_matched_rebuild_20260926_v1_retry2/A/outputs"
    for tag, name in (("route-files", "demand.rou.xml"),
                      ("additional-files", "scenario.add.xml")):
        node = root.find(f"./input/{tag}")
        if node is None:
            raise ValueError(f"missing {tag}")
        node.set("value", _replace_path(node.get("value"), old_arm / name, new_arm / name))
    for node in root.findall("./output/*") + root.findall("./report/*"):
        value = node.get("value")
        if value and value.startswith(str(old_output) + "/"):
            node.set("value", _replace_path(value, old_output / Path(value).name,
                                            output_dir / Path(value).name))
    return root


def _xml_bytes(root: ET.Element) -> bytes:
    ET.indent(root, space="  ")
    return ET.tostring(root, encoding="utf-8", xml_declaration=True)


def audit(package_dir: Path, raw_root: Path) -> dict:
    sources = source_hashes()
    arm_dir = package_dir / ARM
    if digest(arm_dir / "demand.rou.xml") != sources["A/demand.rou.xml"]:
        raise ValueError("demand not byte-identical to default V2 A")
    output_dir = raw_root / ARM / "outputs"
    for name, expected in (("scenario.add.xml", _xml_bytes(_additional(output_dir))),
                           ("scenario.sumocfg", _xml_bytes(_config(package_dir, output_dir)))):
        if (arm_dir / name).read_bytes() != expected:
            raise ValueError(f"unexpected new arm content: {name}")
    config = ET.parse(arm_dir / "scenario.sumocfg").getroot()
    if (config.find("./random_number/seed").get("value") != "17"
            or config.find("./time/end").get("value") != "2700"):
        raise ValueError("seed or horizon changed")
    demand = ET.parse(arm_dir / "demand.rou.xml").getroot()
    counts = {cls: sum(v.get("id", "").startswith(f"{cls}_flow.")
                       for v in demand.findall("vehicle")) for cls in "MRUX"}
    if counts != {"M": 1396, "R": 240, "U": 150, "X": 75}:
        raise ValueError("demand counts changed")
    return {"status": "REBALANCED28_STATIC_EQUIVALENCE_PASS_NO_SUMO_STARTED",
            "arm": ARM, "program": "28G+3y+29r", "counts": counts,
            "demand_byte_identical_to_default_A": True,
            "base_manifest_sha256": BASE_MANIFEST_SHA256}


def build(package_dir: Path, raw_root: Path) -> dict:
    if not package_dir.is_absolute() or not raw_root.is_absolute():
        raise ValueError("package and raw roots must be absolute")
    if package_dir.parent != ARTIFACT_ROOT or raw_root != RAW_ROOT:
        raise ValueError("package/raw location differs from reviewed candidate")
    if package_dir.exists() or package_dir.is_symlink() or raw_root.exists() or raw_root.is_symlink():
        raise FileExistsError("refusing existing package or raw root")
    sources = source_hashes()
    package_dir.mkdir()
    arm_dir = package_dir / ARM
    arm_dir.mkdir()
    shutil.copyfile(BASE / "A/demand.rou.xml", arm_dir / "demand.rou.xml")
    output_dir = raw_root / ARM / "outputs"
    (arm_dir / "scenario.add.xml").write_bytes(_xml_bytes(_additional(output_dir)))
    (arm_dir / "scenario.sumocfg").write_bytes(_xml_bytes(_config(package_dir, output_dir)))
    result = audit(package_dir, raw_root)
    (package_dir / "STATIC_AUDIT.json").write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    manifest = {"status": "REBALANCED28_INPUTS_BUILT_NOT_EXECUTION_AUTHORIZED",
                "sumo_starts": 0, "arm": ARM, "run_id": RUN_ID,
                "generator_sha256": digest(Path(__file__)),
                "base_manifest_sha256": BASE_MANIFEST_SHA256,
                "input_sources": sources, "raw_root": str(raw_root),
                "files": {str(p.relative_to(package_dir)): digest(p)
                          for p in sorted(package_dir.rglob("*")) if p.is_file()}}
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

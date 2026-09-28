"""Build the single B22_SIGMA0 Stage 6 diagnostic package without running SUMO."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import shutil
import xml.etree.ElementTree as ET


ROOT = Path(__file__).resolve().parents[2]
ARTIFACT_ROOT = ROOT / "artifacts/stage6_b22_sigma0_completion_20260926_v1"
RAW_ROOT = ROOT / "data/raw/stage6_b22_sigma0_completion_20260926_v1"
BASE = ROOT / "artifacts/stage6_a_rng_isolation_diagnostic_20260926_v1/inputs"
BASE_MANIFEST_SHA256 = "858b157d48202cc501021eee4b539140ce61443fbbd93c21bf223597648813fa"
ARM = "B22_SIGMA0"
RUN_ID = "FULLNET3350_B22_SIGMA0_S17_DIAG_V1"
FILES = ("demand.rou.xml", "scenario.add.xml", "scenario.sumocfg")


def digest(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1 << 20), b""):
            h.update(block)
    return h.hexdigest()


def source_hashes() -> dict[str, str]:
    if digest(BASE / "INPUT_MANIFEST.json") != BASE_MANIFEST_SHA256:
        raise ValueError("A_SIGMA0 manifest hash mismatch")
    manifest = json.loads((BASE / "INPUT_MANIFEST.json").read_text())
    result = {}
    for name in FILES:
        relative = f"A_SIGMA0/{name}"
        expected = manifest["files"].get(relative)
        if not expected or digest(BASE / relative) != expected:
            raise ValueError(f"A_SIGMA0 source mismatch: {relative}")
        result[relative] = expected
    return result


def _xml_bytes(root: ET.Element) -> bytes:
    ET.indent(root, space="  ")
    return ET.tostring(root, encoding="utf-8", xml_declaration=True)


def _replace_exact(value: str | None, old: Path, new: Path) -> str:
    if value != str(old):
        raise ValueError(f"unexpected source path: {value}")
    return str(new)


def _additional(output_dir: Path) -> ET.Element:
    root = ET.parse(BASE / "A_SIGMA0/scenario.add.xml").getroot()
    selectors = root.findall("WAUT")
    if len(selectors) != 1 or selectors[0].get("startProg") != "A_OPEN":
        raise ValueError("unexpected source WAUT")
    if root.findall("tlLogic"):
        raise ValueError("source additional unexpectedly overrides signal program")
    old_output = ROOT / "data/raw/stage6_a_rng_isolation_diagnostic_20260926_v1/A_SIGMA0/outputs"
    for node in root.iter():
        if node.tag in {"inductionLoop", "laneAreaDetector"}:
            old = node.get("file")
            node.set("file", _replace_exact(old, old_output / Path(old).name,
                                            output_dir / Path(old).name))
        elif node.tag == "timedEvent":
            old = node.get("dest")
            node.set("dest", _replace_exact(old, old_output / Path(old).name,
                                            output_dir / Path(old).name))
    selectors[0].set("startProg", "B_MODERATE")
    return root


def _config(package_dir: Path, output_dir: Path) -> ET.Element:
    root = ET.parse(BASE / "A_SIGMA0/scenario.sumocfg").getroot()
    old_arm = BASE / "A_SIGMA0"
    new_arm = package_dir / ARM
    old_output = ROOT / "data/raw/stage6_a_rng_isolation_diagnostic_20260926_v1/A_SIGMA0/outputs"
    for tag, name in (("route-files", "demand.rou.xml"),
                      ("additional-files", "scenario.add.xml")):
        node = root.find(f"./input/{tag}")
        if node is None:
            raise ValueError(f"missing {tag}")
        node.set("value", _replace_exact(node.get("value"), old_arm / name, new_arm / name))
    for node in root.findall("./output/*") + root.findall("./report/*"):
        old = node.get("value")
        if old and old.startswith(str(old_output) + "/"):
            node.set("value", _replace_exact(old, old_output / Path(old).name,
                                             output_dir / Path(old).name))
    return root


def audit(package_dir: Path, raw_root: Path) -> dict:
    sources = source_hashes()
    arm_dir = package_dir / ARM
    if digest(arm_dir / "demand.rou.xml") != sources["A_SIGMA0/demand.rou.xml"]:
        raise ValueError("demand not byte-identical to A_SIGMA0")
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
    network = ET.parse(Path(config.find("./input/net-file").get("value"))).getroot()
    programs = [p for p in network.findall("tlLogic")
                if p.get("id") == "ramp_mid" and p.get("programID") == "B_MODERATE"]
    if len(programs) != 1 or [(p.get("duration"), p.get("state"))
                              for p in programs[0].findall("phase")] != [
                                  ("22", "G"), ("3", "y"), ("35", "r")]:
        raise ValueError("compiled network lacks exact B_MODERATE 22G+3y+35r")
    return {"status": "B22_SIGMA0_STATIC_EQUIVALENCE_PASS_NO_SUMO_STARTED",
            "arm": ARM, "program": "22G+3y+35r", "counts": counts,
            "demand_byte_identical_to_A_SIGMA0": True,
            "base_manifest_sha256": BASE_MANIFEST_SHA256}


def build(package_dir: Path, raw_root: Path) -> dict:
    if not package_dir.is_absolute() or not raw_root.is_absolute():
        raise ValueError("package and raw roots must be absolute")
    if package_dir.parent != ARTIFACT_ROOT or raw_root != RAW_ROOT:
        raise ValueError("package/raw location differs from reviewed diagnostic")
    if package_dir.exists() or package_dir.is_symlink() or raw_root.exists() or raw_root.is_symlink():
        raise FileExistsError("refusing existing package or raw root")
    sources = source_hashes()
    package_dir.mkdir()
    arm_dir = package_dir / ARM
    arm_dir.mkdir()
    shutil.copyfile(BASE / "A_SIGMA0/demand.rou.xml", arm_dir / "demand.rou.xml")
    output_dir = raw_root / ARM / "outputs"
    (arm_dir / "scenario.add.xml").write_bytes(_xml_bytes(_additional(output_dir)))
    (arm_dir / "scenario.sumocfg").write_bytes(_xml_bytes(_config(package_dir, output_dir)))
    result = audit(package_dir, raw_root)
    (package_dir / "STATIC_AUDIT.json").write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    manifest = {"status": "B22_SIGMA0_INPUTS_BUILT_NOT_EXECUTION_AUTHORIZED",
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

"""Fail-closed, one-use SUMO launcher for a reviewed matched R0/A/B/C card.

Card schema is intentionally small and exact. ``preflight`` is read-only;
``launch`` consumes one reservation before it starts SUMO. The raw directory is
unique and never reused. This runner makes no scientific outcome judgment.
"""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import re
import signal
import subprocess
import sys
import time
import xml.etree.ElementTree as ET

from src.scenarios import fullnet_abc_rebuild as rebuild


SUMO_BINARY = Path("/Library/Frameworks/EclipseSUMO.framework/Versions/1.26.0/EclipseSUMO/bin/sumo")
SUMO_SHA256 = "3bd1eaa3b167fb527ac33b154dfb57b41b9a40d5bc3e26246489824dd7977179"
SUMO_HOME = Path("/Library/Frameworks/EclipseSUMO.framework/Versions/1.26.0/EclipseSUMO/share/sumo")
ADDITIONAL_SCHEMA = SUMO_HOME / "data/xsd/additional_file.xsd"
ADDITIONAL_SCHEMA_SHA256 = "c755f45b68590c4313eb8123b2cd9c56e0097ade83c5f2176f35e14f25bec97e"
ROUTES_SCHEMA = SUMO_HOME / "data/xsd/routes_file.xsd"
ROUTES_SCHEMA_SHA256 = "2ce8e88b6644d87cc6d8acd49b2fc9da29f74e953e67ab4c6e475de5cfe0cb11"
RUNNER_VERSION = "2"
MAX_RUNTIME_S = 120
MAX_OUTPUT_BYTES = 100_000_000
POLL_MS = 100
ARM_PROGRAM = rebuild.ARM_PROGRAM
ID_PATTERN = re.compile(r"^[A-Za-z0-9][A-Za-z0-9_.-]{0,100}$")
REQUIRED_XML = {
    "fcd.xml", "queues.xml", "sumo_summary.xml", "tripinfo.xml", "vehroute.xml",
    "tls_states.xml", "lanechanges.xml", "shared_boundary_e2.xml", "ramp_storage_e2.xml",
    "p1_main_up_1300_l0.xml", "p1_main_up_1300_l1.xml",
    "p1_merge_section_20_l0.xml", "p1_merge_section_20_l1.xml", "p1_merge_section_20_l2.xml",
    "p1_main_down_20_l0.xml", "p1_main_down_20_l1.xml",
    "p1_main_down_200_l0.xml", "p1_main_down_200_l1.xml",
}


class GateError(ValueError):
    """A card, binding or launch gate failed before SUMO starts."""


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _json_bytes(value: dict) -> bytes:
    return (json.dumps(value, indent=2, sort_keys=True) + "\n").encode("utf-8")


def _write_exclusive(path: Path, value: dict) -> None:
    fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o644)
    with os.fdopen(fd, "wb") as stream:
        stream.write(_json_bytes(value))
        stream.flush()
        os.fsync(stream.fileno())


def _atomic_replace(path: Path, value: dict) -> None:
    temporary = path.with_name(path.name + f".tmp.{os.getpid()}")
    _write_exclusive(temporary, value)
    os.replace(temporary, path)


def _descendant(path: Path, root: Path) -> bool:
    return path == root or root in path.parents


def _required_file_hash(path: Path, expected: str) -> None:
    if not path.is_file() or path.is_symlink() or rebuild.digest(path) != expected:
        raise GateError(f"hash or file mismatch: {path}")


def _output_refs(arm_dir: Path) -> set[str]:
    refs = set()
    config = ET.parse(arm_dir / "scenario.sumocfg").getroot()
    for node in config.findall("./output/*") + config.findall("./report/*"):
        if node.tag.endswith("-output") or node.tag in {"log", "error-log"}:
            value = node.get("value")
            if value and value.startswith("/"):
                refs.add(value)
    additional = ET.parse(arm_dir / "scenario.add.xml").getroot()
    for node in additional.iter():
        for attr in ("file", "dest"):
            value = node.get(attr)
            if value and value.startswith("/"):
                refs.add(value)
    return refs


def preflight(card_path: Path, expected_card_sha256: str) -> dict:
    card_path = card_path.resolve(strict=True)
    _required_file_hash(card_path, expected_card_sha256)
    card = json.loads(card_path.read_text())
    required = {"schema_version", "run_id", "arm", "package_dir", "raw_root", "package_manifest_sha256",
                "input_sha256", "network_sha256", "sumo_sha256", "max_runtime_s", "max_output_bytes",
                "poll_ms", "design_review_status", "sumo_home", "additional_schema_sha256",
                "routes_schema_sha256", "runner_sha256", "runner_version"}
    if set(card) != required or card["schema_version"] != "2":
        raise GateError("exact card schema mismatch")
    run_id, arm = card["run_id"], card["arm"]
    if not isinstance(run_id, str) or not ID_PATTERN.fullmatch(run_id) or arm not in ARM_PROGRAM:
        raise GateError("invalid run ID or arm")
    if card["design_review_status"] != "PASS_FOR_EXPLORATORY_PRELAUNCH_DESIGN":
        raise GateError("independent scientific design review not passed")
    if (card["max_runtime_s"], card["max_output_bytes"], card["poll_ms"]) != (
        MAX_RUNTIME_S, MAX_OUTPUT_BYTES, POLL_MS
    ):
        raise GateError("resource contract mismatch")
    if card["sumo_sha256"] != SUMO_SHA256:
        raise GateError("SUMO binary binding mismatch")
    _required_file_hash(SUMO_BINARY, SUMO_SHA256)
    if (card["sumo_home"] != str(SUMO_HOME)
            or card["additional_schema_sha256"] != ADDITIONAL_SCHEMA_SHA256
            or card["routes_schema_sha256"] != ROUTES_SCHEMA_SHA256):
        raise GateError("SUMO_HOME or schema binding mismatch")
    if not SUMO_HOME.is_dir() or SUMO_HOME.is_symlink():
        raise GateError("SUMO_HOME path missing or symlinked")
    _required_file_hash(ADDITIONAL_SCHEMA, ADDITIONAL_SCHEMA_SHA256)
    _required_file_hash(ROUTES_SCHEMA, ROUTES_SCHEMA_SHA256)
    if card["runner_version"] != RUNNER_VERSION or card["runner_sha256"] != rebuild.digest(Path(__file__)):
        raise GateError("runner version or hash mismatch")
    package_dir = Path(card["package_dir"])
    raw_root = Path(card["raw_root"])
    if not package_dir.is_absolute() or not raw_root.is_absolute():
        raise GateError("package/raw root must be absolute")
    package_dir = package_dir.resolve(strict=True)
    raw_root = raw_root.resolve(strict=False)
    if not _descendant(package_dir, rebuild.ROOT / "artifacts"):
        raise GateError("package outside artifacts")
    if not _descendant(raw_root, rebuild.ROOT / "data/raw"):
        raise GateError("raw root outside data/raw")
    if raw_root.exists():
        # Other arms may already exist. The target arm must remain untouched.
        target = raw_root / arm
        if target.exists() or target.is_symlink():
            raise GateError("target raw arm already exists")
    manifest_path = package_dir / "INPUT_MANIFEST.json"
    _required_file_hash(manifest_path, card["package_manifest_sha256"])
    manifest = json.loads(manifest_path.read_text())
    if (Path(manifest.get("raw_root", "")).resolve(strict=False) != raw_root
            or manifest.get("status") != "INPUTS_BUILT_NOT_EXECUTION_AUTHORIZED"):
        raise GateError("package manifest binding mismatch")
    if manifest.get("generator_sha256") != rebuild.digest(Path(rebuild.__file__)):
        raise GateError("input generator version mismatch")
    for relative, expected in manifest.get("input_sources", {}).items():
        source = rebuild.ROOT / relative
        if not _descendant(source.resolve(strict=True), rebuild.ROOT):
            raise GateError("source path escapes repository")
        _required_file_hash(source, expected)
    speed = manifest.get("speed_factor_generation", {})
    if (speed.get("seed"), speed.get("mean"), speed.get("deviation"),
            speed.get("minimum"), speed.get("maximum")) != (170026, 1.0, 0.1, 0.2, 2.0):
        raise GateError("reviewed speedFactor specification mismatch")
    for relative, expected in manifest["files"].items():
        target = package_dir / relative
        if not _descendant(target.resolve(strict=True), package_dir):
            raise GateError("manifest path escapes package")
        _required_file_hash(target, expected)
    if rebuild.digest(package_dir / "STATIC_AUDIT.json") != manifest["files"].get("STATIC_AUDIT.json"):
        raise GateError("static audit hash mismatch")
    audit = rebuild._audit(package_dir)
    if audit["status"] != "STATIC_INPUT_EQUIVALENCE_PASS_NO_SUMO_STARTED":
        raise GateError("static input equivalence did not pass")
    _, _, flow_defs = rebuild._flow_definitions()
    expected_records = rebuild._vehicle_records(flow_defs, 170026, 1.0, 0.1, 0.2, 2.0)
    expected_factors = {record["id"]: record["speedFactor"] for record in expected_records}
    a_demand = ET.parse(package_dir / "A/demand.rou.xml").getroot()
    if any(node.get("speedFactor") != expected_factors.get(node.get("id")) for node in a_demand.findall("vehicle")):
        raise GateError("prospective speedFactor vector mismatch")
    arm_dir = package_dir / arm
    expected_input = card["input_sha256"]
    if set(expected_input) != {"demand", "additional", "sumocfg"}:
        raise GateError("input hash binding incomplete")
    for role, filename in (("demand", "demand.rou.xml"), ("additional", "scenario.add.xml"),
                           ("sumocfg", "scenario.sumocfg")):
        _required_file_hash(arm_dir / filename, expected_input[role])
    config = ET.parse(arm_dir / "scenario.sumocfg").getroot()
    network = Path(config.find("./input/net-file").get("value"))
    _required_file_hash(network, card["network_sha256"])
    if network != rebuild.ROOT / "artifacts/stage6_baseline_localization_20260921_v1/LOC_M3350_S17/engineering/build_attempts/TV_BUILD01/network.net.xml":
        raise GateError("unexpected network path")
    if Path(config.find("./input/route-files").get("value")).resolve(strict=False) != arm_dir / "demand.rou.xml":
        raise GateError("route path mismatch")
    if Path(config.find("./input/additional-files").get("value")).resolve(strict=False) != arm_dir / "scenario.add.xml":
        raise GateError("additional path mismatch")
    output_dir = raw_root / arm / "outputs"
    refs = _output_refs(arm_dir)
    if len(refs) < 18 or any(not _descendant(Path(ref).resolve(strict=False), output_dir) for ref in refs):
        raise GateError("output references absent or outside arm raw directory")
    reservation = package_dir / "reservations" / f"{run_id}.json"
    if reservation.exists() or reservation.is_symlink():
        raise GateError("run authorization already consumed")
    return {
        "status": "PREFLIGHT_PASS_NO_PROCESS_STARTED", "run_id": run_id, "arm": arm,
        "card_sha256": expected_card_sha256, "card_path": str(card_path),
        "package_dir": str(package_dir), "output_dir": str(output_dir),
        "reservation": str(reservation), "output_refs": len(refs),
        "resource_contract": {"runtime_s": MAX_RUNTIME_S, "bytes": MAX_OUTPUT_BYTES, "poll_ms": POLL_MS},
        "sumo_home_for_child": str(SUMO_HOME),
    }


def _directory_bytes(path: Path) -> int:
    return sum(item.stat().st_size for item in path.rglob("*") if item.is_file())


def _stop_group(process: subprocess.Popen) -> None:
    if process.poll() is None:
        try:
            os.killpg(process.pid, signal.SIGTERM)
        except ProcessLookupError:
            return
        try:
            process.wait(timeout=3)
        except subprocess.TimeoutExpired:
            try:
                os.killpg(process.pid, signal.SIGKILL)
            except ProcessLookupError:
                pass
            process.wait(timeout=3)


def _check_required_xml(output_dir: Path) -> str | None:
    for name in sorted(REQUIRED_XML):
        path = output_dir / name
        if not path.is_file() or path.stat().st_size == 0:
            return f"REQUIRED_OUTPUT_MISSING_OR_EMPTY:{name}"
        try:
            for _event, node in ET.iterparse(path, events=("end",)):
                node.clear()
        except ET.ParseError as exc:
            return f"REQUIRED_OUTPUT_MALFORMED:{name}:{exc}"
    return None


def launch(card_path: Path, expected_card_sha256: str) -> dict:
    plan = preflight(card_path, expected_card_sha256)
    package_dir = Path(plan["package_dir"])
    output_dir = Path(plan["output_dir"])
    reservation = Path(plan["reservation"])
    reservation.parent.mkdir(exist_ok=True)
    reserved = {"status": "CONSUMED", "reserved_at_utc": _utc_now(),
                "run_id": plan["run_id"], "arm": plan["arm"], "card_sha256": expected_card_sha256,
                "max_starts": 1, "retry_allowed": False}
    _write_exclusive(reservation, reserved)
    start = time.monotonic()
    process = None
    stop_reason = None
    return_code = None
    failure = None
    try:
        output_dir.mkdir(parents=True, exist_ok=False)
        with (output_dir / "stdout.log").open("wb") as stdout, (output_dir / "stderr.log").open("wb") as stderr:
            child_env = os.environ.copy()
            child_env["SUMO_HOME"] = str(SUMO_HOME)
            process = subprocess.Popen([str(SUMO_BINARY), "-c", str(package_dir / plan["arm"] / "scenario.sumocfg")],
                                       stdout=stdout, stderr=stderr, start_new_session=True, env=child_env)
            reserved["sumo_pid"] = process.pid
            _atomic_replace(reservation, reserved)
            while process.poll() is None:
                elapsed = time.monotonic() - start
                size = _directory_bytes(output_dir)
                if elapsed >= MAX_RUNTIME_S:
                    stop_reason = "RUNTIME_LIMIT"
                    _stop_group(process)
                    break
                if size >= MAX_OUTPUT_BYTES:
                    stop_reason = "OUTPUT_LIMIT"
                    _stop_group(process)
                    break
                time.sleep(POLL_MS / 1000)
            return_code = process.wait()
            if stop_reason is None and _directory_bytes(output_dir) >= MAX_OUTPUT_BYTES:
                stop_reason = "OUTPUT_LIMIT_AT_EXIT"
            if stop_reason is None and time.monotonic() - start >= MAX_RUNTIME_S:
                stop_reason = "RUNTIME_LIMIT_AT_EXIT"
            if return_code == 0 and stop_reason is None:
                failure = _check_required_xml(output_dir)
    except Exception as exc:
        failure = f"{type(exc).__name__}: {exc}"
        if process is not None:
            _stop_group(process)
            return_code = process.returncode
    finally:
        elapsed = round(time.monotonic() - start, 6)
        files = {}
        if output_dir.exists():
            files = {str(p.relative_to(output_dir)): {"sha256": rebuild.digest(p), "bytes": p.stat().st_size}
                     for p in sorted(output_dir.rglob("*")) if p.is_file()}
        status = "COMPLETED" if return_code == 0 and stop_reason is None and failure is None else "FAILED"
        receipt = {
            "status": status, "run_id": plan["run_id"], "arm": plan["arm"],
            "card_sha256": expected_card_sha256, "started_at_utc": reserved["reserved_at_utc"],
            "finished_at_utc": _utc_now(), "runtime_wall_s": elapsed,
            "sumo_pid": reserved.get("sumo_pid"), "return_code": return_code,
            "stop_reason": stop_reason, "failure": failure, "retry_allowed": False,
            "output_payload_bytes": sum(item["bytes"] for item in files.values()),
            "output_manifest": files,
            "sumo_home_for_child": str(SUMO_HOME),
        }
        _atomic_replace(reservation, {**reserved, "final_status": status,
                                      "receipt_sha256": hashlib.sha256(_json_bytes(receipt)).hexdigest()})
        receipt_dir = package_dir / "run_receipts"
        receipt_dir.mkdir(exist_ok=True)
        _write_exclusive(receipt_dir / f"{plan['run_id']}.json", receipt)
        if output_dir.exists():
            _write_exclusive(output_dir / "execution_receipt.json", receipt)
    return receipt


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("mode", choices=("preflight", "launch"))
    parser.add_argument("--card", type=Path, required=True)
    parser.add_argument("--approved-card-sha256", required=True)
    args = parser.parse_args()
    try:
        result = preflight(args.card, args.approved_card_sha256) if args.mode == "preflight" else launch(args.card, args.approved_card_sha256)
        print(json.dumps(result, indent=2, sort_keys=True))
        return 0 if result["status"] in {"PREFLIGHT_PASS_NO_PROCESS_STARTED", "COMPLETED"} else 1
    except (GateError, FileExistsError, OSError, ValueError) as exc:
        print(json.dumps({"status": "BLOCKED_NO_SUMO_STARTED", "error": str(exc)}), file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())

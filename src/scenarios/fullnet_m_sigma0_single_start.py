"""One-use, fail-closed launcher for reviewed M-only sigma=0 diagnostic cards."""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import signal
import subprocess
import sys
import time
import xml.etree.ElementTree as ET

from src.scenarios import fullnet_m_sigma0_diagnostic as builder


SUMO_BINARY = Path("/Library/Frameworks/EclipseSUMO.framework/Versions/1.26.0/EclipseSUMO/bin/sumo")
SUMO_SHA256 = "3bd1eaa3b167fb527ac33b154dfb57b41b9a40d5bc3e26246489824dd7977179"
SUMO_HOME = Path("/Library/Frameworks/EclipseSUMO.framework/Versions/1.26.0/EclipseSUMO/share/sumo")
ADDITIONAL_SCHEMA = SUMO_HOME / "data/xsd/additional_file.xsd"
ADDITIONAL_SCHEMA_SHA256 = "c755f45b68590c4313eb8123b2cd9c56e0097ade83c5f2176f35e14f25bec97e"
ROUTES_SCHEMA = SUMO_HOME / "data/xsd/routes_file.xsd"
ROUTES_SCHEMA_SHA256 = "2ce8e88b6644d87cc6d8acd49b2fc9da29f74e953e67ab4c6e475de5cfe0cb11"
NETWORK = builder.ROOT / "artifacts/stage6_baseline_localization_20260921_v1/LOC_M3350_S17/engineering/build_attempts/TV_BUILD01/network.net.xml"
NETWORK_SHA256 = "887c232483f0c68dc024334ff5997250d7d36299ab2744bdcf49d5a314c700ca"
RUNNER_VERSION = "1"
MAX_RUNTIME_S = 120
MAX_OUTPUT_BYTES = 100_000_000
POLL_MS = 100
RUN_IDS = {"R0_SIGMA0": "FULLNET3350_R0_SIGMA0_S17_DIAG_V1",
           "A_SIGMA0": "FULLNET3350_A_SIGMA0_S17_DIAG_V1"}
REQUIRED_XML = {
    "fcd.xml", "queues.xml", "sumo_summary.xml", "tripinfo.xml", "vehroute.xml",
    "tls_states.xml", "lanechanges.xml", "shared_boundary_e2.xml", "ramp_storage_e2.xml",
    "p1_main_up_1300_l0.xml", "p1_main_up_1300_l1.xml",
    "p1_merge_section_20_l0.xml", "p1_merge_section_20_l1.xml", "p1_merge_section_20_l2.xml",
    "p1_main_down_20_l0.xml", "p1_main_down_20_l1.xml",
    "p1_main_down_200_l0.xml", "p1_main_down_200_l1.xml",
}


class GateError(ValueError):
    """Input, card, resource or one-use authorization gate failed."""


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _json_bytes(value: dict) -> bytes:
    return (json.dumps(value, indent=2, sort_keys=True) + "\n").encode()


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


def _required_hash(path: Path, expected: str) -> None:
    if not path.is_file() or path.is_symlink() or builder.digest(path) != expected:
        raise GateError(f"hash or file mismatch: {path}")


def _descendant(path: Path, root: Path) -> bool:
    return path == root or root in path.parents


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
    _required_hash(card_path, expected_card_sha256)
    card = json.loads(card_path.read_text())
    base_keys = {"schema_version", "run_id", "arm", "package_dir", "raw_root", "package_manifest_sha256",
                 "input_sha256", "base_manifest_sha256", "network_sha256", "sumo_sha256",
                 "sumo_home", "additional_schema_sha256", "routes_schema_sha256",
                 "runner_sha256", "runner_version", "max_runtime_s", "max_output_bytes", "poll_ms",
                 "design_review_status"}
    arm = card.get("arm")
    expected_keys = base_keys | ({"r0_receipt_sha256"} if arm == "A_SIGMA0" else set())
    if set(card) != expected_keys or card.get("schema_version") != "sigma0-diagnostic-1":
        raise GateError("exact diagnostic card schema mismatch")
    if arm not in RUN_IDS or card["run_id"] != RUN_IDS[arm]:
        raise GateError("unexpected diagnostic arm or run ID")
    if card["design_review_status"] != "PASS_PLAN_ONLY":
        raise GateError("independent scientific plan review status mismatch")
    if (card["max_runtime_s"], card["max_output_bytes"], card["poll_ms"]) != (
            MAX_RUNTIME_S, MAX_OUTPUT_BYTES, POLL_MS):
        raise GateError("resource contract mismatch")
    for field, expected in (("sumo_sha256", SUMO_SHA256), ("network_sha256", NETWORK_SHA256),
                            ("base_manifest_sha256", builder.BASE_MANIFEST_SHA256),
                            ("sumo_home", str(SUMO_HOME)),
                            ("additional_schema_sha256", ADDITIONAL_SCHEMA_SHA256),
                            ("routes_schema_sha256", ROUTES_SCHEMA_SHA256),
                            ("runner_version", RUNNER_VERSION),
                            ("runner_sha256", builder.digest(Path(__file__)))):
        if card[field] != expected:
            raise GateError(f"{field} binding mismatch")
    for path, expected in ((SUMO_BINARY, SUMO_SHA256), (NETWORK, NETWORK_SHA256),
                           (ADDITIONAL_SCHEMA, ADDITIONAL_SCHEMA_SHA256),
                           (ROUTES_SCHEMA, ROUTES_SCHEMA_SHA256)):
        _required_hash(path, expected)
    if not SUMO_HOME.is_dir() or SUMO_HOME.is_symlink():
        raise GateError("SUMO_HOME unavailable")
    package_dir = Path(card["package_dir"])
    raw_root = Path(card["raw_root"])
    if not package_dir.is_absolute() or not raw_root.is_absolute():
        raise GateError("package/raw roots must be absolute")
    package_dir = package_dir.resolve(strict=True)
    raw_root = raw_root.resolve(strict=False)
    if package_dir.parent != builder.ARTIFACT_ROOT or raw_root.parent != builder.RAW_PARENT:
        raise GateError("package/raw root outside diagnostic location")
    if raw_root.exists() and ((raw_root / arm).exists() or (raw_root / arm).is_symlink()):
        raise GateError("target raw arm already exists")
    manifest_path = package_dir / "INPUT_MANIFEST.json"
    _required_hash(manifest_path, card["package_manifest_sha256"])
    manifest = json.loads(manifest_path.read_text())
    if (manifest.get("status") != "DIAGNOSTIC_INPUTS_BUILT_NOT_EXECUTION_AUTHORIZED"
            or manifest.get("raw_root") != str(raw_root)
            or manifest.get("generator_sha256") != builder.digest(Path(builder.__file__))
            or manifest.get("base_manifest_sha256") != builder.BASE_MANIFEST_SHA256):
        raise GateError("diagnostic manifest binding mismatch")
    if manifest.get("input_sources") != builder._source_hashes():
        raise GateError("default V2 source binding mismatch")
    for relative, expected in manifest.get("files", {}).items():
        target = (package_dir / relative).resolve(strict=True)
        if not _descendant(target, package_dir):
            raise GateError("manifest path escapes package")
        _required_hash(target, expected)
    if manifest.get("files", {}).get("STATIC_AUDIT.json") != builder.digest(package_dir / "STATIC_AUDIT.json"):
        raise GateError("static audit binding mismatch")
    audit = builder.audit(package_dir, raw_root)
    if audit["status"] != "SIGMA0_STATIC_EQUIVALENCE_PASS_NO_SUMO_STARTED":
        raise GateError("diagnostic static audit failed")
    arm_dir = package_dir / arm
    expected_input = card["input_sha256"]
    if set(expected_input) != {"demand", "additional", "sumocfg"}:
        raise GateError("input hash binding incomplete")
    for role, filename in (("demand", "demand.rou.xml"), ("additional", "scenario.add.xml"),
                           ("sumocfg", "scenario.sumocfg")):
        _required_hash(arm_dir / filename, expected_input[role])
    refs = _output_refs(arm_dir)
    output_dir = raw_root / arm / "outputs"
    if len(refs) < 18 or any(not _descendant(Path(ref).resolve(strict=False), output_dir) for ref in refs):
        raise GateError("output references missing or outside target raw arm")
    reservation = package_dir / "reservations" / f"{card['run_id']}.json"
    if reservation.exists() or reservation.is_symlink():
        raise GateError("one-use start already consumed")
    if arm == "A_SIGMA0":
        receipt = package_dir / "run_receipts" / f"{RUN_IDS['R0_SIGMA0']}.json"
        _required_hash(receipt, card["r0_receipt_sha256"])
        if json.loads(receipt.read_text()).get("status") != "COMPLETED":
            raise GateError("R0 diagnostic did not complete")
    return {"status": "PREFLIGHT_PASS_NO_PROCESS_STARTED", "run_id": card["run_id"],
            "arm": arm, "card_sha256": expected_card_sha256, "package_dir": str(package_dir),
            "raw_root": str(raw_root), "output_dir": str(output_dir), "reservation": str(reservation),
            "output_refs": len(refs), "sumo_home_for_child": str(SUMO_HOME),
            "resource_contract": {"runtime_s": MAX_RUNTIME_S, "bytes": MAX_OUTPUT_BYTES, "poll_ms": POLL_MS}}


def _directory_bytes(path: Path) -> int:
    return sum(item.stat().st_size for item in path.rglob("*") if item.is_file())


def _stop_group(process: subprocess.Popen) -> None:
    if process.poll() is not None:
        return
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


def _check_xml(output_dir: Path) -> str | None:
    for name in sorted(REQUIRED_XML):
        path = output_dir / name
        if not path.is_file() or path.stat().st_size == 0:
            return f"REQUIRED_OUTPUT_MISSING_OR_EMPTY:{name}"
        try:
            for _event, element in ET.iterparse(path, events=("end",)):
                element.clear()
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
                "run_id": plan["run_id"], "arm": plan["arm"],
                "card_sha256": expected_card_sha256, "max_starts": 1, "retry_allowed": False}
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
                if time.monotonic() - start >= MAX_RUNTIME_S:
                    stop_reason = "RUNTIME_LIMIT"
                    _stop_group(process)
                    break
                if _directory_bytes(output_dir) >= MAX_OUTPUT_BYTES:
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
                failure = _check_xml(output_dir)
    except Exception as exc:
        failure = f"{type(exc).__name__}: {exc}"
        if process is not None:
            _stop_group(process)
            return_code = process.returncode
    finally:
        elapsed = round(time.monotonic() - start, 6)
        files = ({str(path.relative_to(output_dir)): {"sha256": builder.digest(path), "bytes": path.stat().st_size}
                  for path in sorted(output_dir.rglob("*")) if path.is_file()} if output_dir.exists() else {})
        status = "COMPLETED" if return_code == 0 and stop_reason is None and failure is None else "FAILED"
        receipt = {"status": status, "run_id": plan["run_id"], "arm": plan["arm"],
                   "card_sha256": expected_card_sha256, "started_at_utc": reserved["reserved_at_utc"],
                   "finished_at_utc": _utc_now(), "runtime_wall_s": elapsed,
                   "sumo_pid": reserved.get("sumo_pid"), "return_code": return_code,
                   "stop_reason": stop_reason, "failure": failure, "retry_allowed": False,
                   "output_payload_bytes": sum(info["bytes"] for info in files.values()),
                   "output_manifest": files, "sumo_home_for_child": str(SUMO_HOME)}
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

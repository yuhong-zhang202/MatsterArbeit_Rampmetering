"""Load a copied SUMO network/additional pair and verify named-lane E2 coverage.

The probe does not advance simulation time.  It redirects every additional-file
output to a new /private/tmp directory so it cannot overwrite a supplied run.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
from pathlib import Path
import shutil
import socket
import subprocess
import sys
import tempfile
import xml.etree.ElementTree as ET

import traci

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.scenarios.run_minimal_uncontrolled import E2_NAMED_LANE_COVERAGE


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def free_loopback_port() -> int:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as listener:
        listener.bind(("127.0.0.1", 0))
        return int(listener.getsockname()[1])


def copied_probe_additional(source: Path, probe_root: Path) -> Path:
    probe_additional = probe_root / "scenario.add.xml"
    tree = ET.parse(source)
    for element in tree.getroot():
        if element.tag == "timedEvent":
            element.set("dest", str(probe_root / "tls_states.xml"))
        elif element.get("id"):
            element.set("file", str(probe_root / f"{element.get('id')}.xml"))
    tree.write(probe_additional, encoding="UTF-8", xml_declaration=True)
    return probe_additional


def verify_loaded_e2_coverage(
    net_file: Path,
    additional_file: Path,
    sumo_binary: Path,
) -> dict[str, object]:
    """Return TraCI-observed E2 anchors and lengths without advancing time."""

    net_file, additional_file, sumo_binary = (
        net_file.resolve(),
        additional_file.resolve(),
        sumo_binary.resolve(),
    )
    source_net_sha256 = sha256(net_file)
    source_additional_sha256 = sha256(additional_file)
    with tempfile.TemporaryDirectory(prefix="e2_coverage_probe_", dir="/private/tmp") as directory:
        probe_root = Path(directory)
        probe_net = probe_root / "network.net.xml"
        shutil.copy2(net_file, probe_net)
        probe_additional = copied_probe_additional(additional_file, probe_root)
        port = free_loopback_port()
        traci.start(
            [
                str(sumo_binary),
                "-n",
                str(probe_net),
                "--additional-files",
                str(probe_additional),
                "--no-step-log",
                "true",
            ],
            port=port,
        )
        try:
            traci_version = list(traci.getVersion())
            simulation_time_s = traci.simulation.getTime()
            loaded_ids = set(traci.lanearea.getIDList())
            detectors: dict[str, dict[str, object]] = {}
            for detector_id, expected_lane in E2_NAMED_LANE_COVERAGE.items():
                if detector_id not in loaded_ids:
                    raise RuntimeError(f"E2 was not loaded: {detector_id}")
                lane_id = traci.lanearea.getLaneID(detector_id)
                position_m = traci.lanearea.getPosition(detector_id)
                length_m = traci.lanearea.getLength(detector_id)
                lane_length_m = traci.lane.getLength(lane_id)
                exact_named_lane = (
                    lane_id == expected_lane
                    and math.isclose(position_m, 0.0, abs_tol=1e-9)
                    and math.isclose(length_m, lane_length_m, abs_tol=1e-6)
                )
                detectors[detector_id] = {
                    "expected_lane_id": expected_lane,
                    "loaded_lane_id": lane_id,
                    "begin_pos_m": position_m,
                    "loaded_length_m": length_m,
                    "loaded_lane_length_m": lane_length_m,
                    "exact_named_lane_coverage": exact_named_lane,
                    "successor_chain": (
                        "not queried: detector length equals its named lane length"
                        if exact_named_lane
                        else "not established by lanearea TraCI API"
                    ),
                }
        finally:
            traci.close()
    sumo_version = subprocess.run(
        [str(sumo_binary), "--version"],
        capture_output=True,
        check=True,
        text=True,
    ).stdout.splitlines()[0]
    return {
        "classification": "technical no-step TraCI E2 coverage probe",
        "all_exact_named_lane_coverage": all(
            item["exact_named_lane_coverage"] for item in detectors.values()
        ),
        "detectors": detectors,
        "provenance": {
            "source_net_file": str(net_file),
            "source_net_sha256_before": source_net_sha256,
            "source_net_sha256_after": sha256(net_file),
            "source_additional_file": str(additional_file),
            "source_additional_sha256_before": source_additional_sha256,
            "source_additional_sha256_after": sha256(additional_file),
            "sumo_version": sumo_version,
            "traci_version": traci_version,
            "simulation_time_s_without_step": simulation_time_s,
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--net-file", required=True, type=Path)
    parser.add_argument("--additional-file", required=True, type=Path)
    parser.add_argument("--sumo-binary", required=True, type=Path)
    parser.add_argument(
        "--output",
        type=Path,
        help="Optional new JSON report path; refuses to overwrite an existing file.",
    )
    args = parser.parse_args()
    report = verify_loaded_e2_coverage(
        args.net_file, args.additional_file, args.sumo_binary
    )
    rendered = json.dumps(report, indent=2, sort_keys=True)
    if args.output is not None:
        if args.output.exists():
            raise FileExistsError(f"Refusing to overwrite E2 report: {args.output}")
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(rendered + "\n", encoding="utf-8")
    print(rendered)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

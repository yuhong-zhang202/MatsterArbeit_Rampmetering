"""Run the fixed upstream ALINEA example as a technical smoke test.

The controller and simulation values mirror the upstream v0.1.0 demo. They
are example values only and are not approved thesis experiment parameters.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import shutil
import sys
import tempfile
import xml.etree.ElementTree as ET


UPSTREAM_TAG = "v0.1.0"
UPSTREAM_COMMIT = "5776c6c79a888a37e55079db63eedc7db0570863"
PROJECT_ROOT = Path(__file__).resolve().parents[2]
UPSTREAM_ROOT = PROJECT_ROOT / "config" / "smoke_tests" / "alinea" / "upstream"
UPSTREAM_MODEL = UPSTREAM_ROOT / "model"
DEFAULT_SUMO_HOME = Path(
    "/Library/Frameworks/EclipseSUMO.framework/Versions/1.26.0/"
    "EclipseSUMO/share/sumo"
)
MODEL_FILES = (
    "Configuration_1.sumocfg",
    "Demand_1.rou.xml",
    "Network.net.xml",
    "Sensors.add.xml",
)
EXPECTED_SHA256 = {
    "demo_ALINEA.py": "56a1f1fd30b5ddba9961c3e92674b10a2796b6243c167e731d7ed9da950320fe",
    "model/Configuration_1.sumocfg": "310b9190e07496ad7ee2e652047f0b0b930b3761f9ddc59cdd4771089803b8de",
    "model/Demand_1.rou.xml": "f562625377d07352b10a3f0d13802cb16657806030191a539d21b36d9cc17a39",
    "model/Network.net.xml": "1c61ca10ed8a0210ba5eb63af084ae88b9c5ae0fab5c63ca1892bec39f58e9e8",
    "model/Sensors.add.xml": "aa008c6137d28f9c924a59d9d3d0d6727113ec3e32ceea444ad81c74b653610c",
}
GUI_SCREENSHOT_STEP = 1200
GUI_FOCUS_RADIUS_M = 500.0
GUI_SCREENSHOT_VALIDATION_DEADLINE_STEP = GUI_SCREENSHOT_STEP + 5


class GuiScreenshotError(RuntimeError):
    def __init__(self, message: str, evidence: dict[str, object]) -> None:
        super().__init__(message)
        self.evidence = evidence


def nonnegative_int(value: str) -> int:
    parsed = int(value)
    if parsed < 0:
        raise argparse.ArgumentTypeError("must be a non-negative integer")
    return parsed


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run or statically validate the upstream ALINEA technical smoke test."
    )
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument(
        "--gui",
        action="store_true",
        help="Use sumo-gui. The default is the headless sumo binary.",
    )
    mode.add_argument(
        "--validate-only",
        action="store_true",
        help="Validate inputs and prepare a temporary copy without starting SUMO.",
    )
    parser.add_argument(
        "--seed",
        type=int,
        default=2,
        help="SUMO random seed for this smoke test (upstream default: 2).",
    )
    parser.add_argument(
        "--sumo-binary",
        help="Explicit SUMO executable path or name; otherwise select sumo/sumo-gui.",
    )
    parser.add_argument(
        "--gui-delay-ms",
        type=nonnegative_int,
        default=10,
        help="GUI step delay in milliseconds (default: 10; ignored in headless mode).",
    )
    return parser.parse_args()


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def validate_upstream_assets() -> dict[str, str]:
    actual: dict[str, str] = {}
    for relative_path, expected in EXPECTED_SHA256.items():
        path = UPSTREAM_ROOT / relative_path
        if not path.is_file():
            raise FileNotFoundError(f"Missing fixed upstream asset: {path}")
        actual_digest = sha256(path)
        if actual_digest != expected:
            raise RuntimeError(
                f"Upstream asset checksum mismatch: {path}; "
                f"expected {expected}, got {actual_digest}"
            )
        actual[relative_path] = actual_digest
    return actual


def resolve_sumo_home() -> Path:
    candidates: list[Path] = []
    configured = os.environ.get("SUMO_HOME")
    if configured:
        configured_path = Path(configured).expanduser()
        candidates.extend((configured_path, configured_path / "share" / "sumo"))
    candidates.append(DEFAULT_SUMO_HOME)

    for candidate in candidates:
        if (candidate / "bin").exists() and (candidate / "tools").is_dir():
            resolved = candidate.resolve()
            os.environ["SUMO_HOME"] = str(resolved)
            path_parts = os.environ.get("PATH", "").split(os.pathsep)
            bin_path = str(resolved / "bin")
            if bin_path not in path_parts:
                os.environ["PATH"] = os.pathsep.join((bin_path, *path_parts))
            return resolved

    checked = ", ".join(str(path) for path in candidates)
    raise RuntimeError(f"Could not find a SUMO_HOME containing bin/ and tools/: {checked}")


def resolve_sumo_binary(gui: bool, explicit: str | None) -> Path:
    requested = explicit or ("sumo-gui" if gui else "sumo")
    located = shutil.which(requested)
    if located is None:
        explicit_path = Path(requested).expanduser()
        if explicit_path.is_file() and os.access(explicit_path, os.X_OK):
            located = str(explicit_path)
    if located is None:
        raise FileNotFoundError(f"SUMO executable not found: {requested}")
    return Path(located).resolve()


def validate_model() -> dict[str, object]:
    config_path = UPSTREAM_MODEL / "Configuration_1.sumocfg"
    config_root = ET.parse(config_path).getroot()
    expected_inputs = {
        "net-file": "Network.net.xml",
        "route-files": "Demand_1.rou.xml",
        "additional-files": "Sensors.add.xml",
    }
    for element_name, expected_value in expected_inputs.items():
        element = config_root.find(f"./input/{element_name}")
        actual_value = None if element is None else element.get("value")
        if actual_value != expected_value:
            raise RuntimeError(
                f"Unexpected {element_name}: expected {expected_value}, got {actual_value}"
            )

    sensor_root = ET.parse(UPSTREAM_MODEL / "Sensors.add.xml").getroot()
    sensors = {element.get("id"): element for element in sensor_root}
    expected_sensors = {"e2_0", "e2_4", "e2_5"}
    if not expected_sensors.issubset(sensors):
        missing = sorted(expected_sensors.difference(sensors))
        raise RuntimeError(f"Missing ALINEA sensors: {missing}")

    network_root = ET.parse(UPSTREAM_MODEL / "Network.net.xml").getroot()
    j0_logic = network_root.find("./tlLogic[@id='J0']")
    if j0_logic is None:
        raise RuntimeError("Missing ramp-meter traffic light logic J0")
    phases = [phase.get("state") for phase in j0_logic.findall("phase")]
    if phases[:2] != ["G", "r"]:
        raise RuntimeError(f"Unexpected J0 phase states: {phases}")

    return {
        "config": str(config_path),
        "inputs": expected_inputs,
        "alinea_sensors": sorted(expected_sensors),
        "traffic_light": "J0",
        "initial_phase_states": phases,
    }


def prepare_runtime_copy() -> tuple[Path, Path, list[str]]:
    run_root = Path(tempfile.mkdtemp(prefix="alinea_smoke_", dir="/private/tmp"))
    model_dir = run_root / "model"
    output_dir = run_root / "detector_outputs"
    model_dir.mkdir()
    output_dir.mkdir()

    for filename in MODEL_FILES:
        shutil.copy2(UPSTREAM_MODEL / filename, model_dir / filename)

    sensor_path = model_dir / "Sensors.add.xml"
    sensor_tree = ET.parse(sensor_path)
    output_files: list[str] = []
    for detector in sensor_tree.getroot():
        detector_id = detector.get("id")
        if detector_id is None:
            raise RuntimeError("Detector without id in Sensors.add.xml")
        output_path = output_dir / f"{detector_id}.xml"
        detector.set("file", str(output_path))
        output_files.append(str(output_path))
    sensor_tree.write(sensor_path, encoding="UTF-8", xml_declaration=True)
    return run_root, model_dir / "Configuration_1.sumocfg", output_files


def build_sumo_command(
    binary: Path,
    config_path: Path,
    seed: int,
    gui: bool,
    gui_delay_ms: int,
) -> list[str]:
    command = [
        str(binary),
        "-c",
        str(config_path),
        "--start",
        "--quit-on-end",
        "--time-to-teleport",
        "-1",
        "--seed",
        str(seed),
    ]
    if gui:
        command.extend(("--delay", str(gui_delay_ms)))
    return command


def capture_gui_evidence(
    traci_module: object,
    screenshot_path: Path,
) -> dict[str, object]:
    view_ids = list(traci_module.gui.getIDList())
    if not view_ids:
        raise GuiScreenshotError(
            "SUMO GUI exposed no view IDs at screenshot step",
            {
                "gui_screenshot_path": str(screenshot_path),
                "gui_screenshot_step": GUI_SCREENSHOT_STEP,
                "gui_screenshot_status": "no_view",
            },
        )

    view_id = view_ids[0]
    j0_x, j0_y = traci_module.junction.getPosition("J0")
    traci_module.gui.setBoundary(
        view_id,
        j0_x - GUI_FOCUS_RADIUS_M,
        j0_y - GUI_FOCUS_RADIUS_M,
        j0_x + GUI_FOCUS_RADIUS_M,
        j0_y + GUI_FOCUS_RADIUS_M,
    )
    vehicle_count = traci_module.vehicle.getIDCount()
    j0_signal_state = traci_module.trafficlight.getRedYellowGreenState("J0")
    simulation_time_s = traci_module.simulation.getTime()
    evidence: dict[str, object] = {
        "gui_screenshot_path": str(screenshot_path),
        "gui_view_id": view_id,
        "gui_screenshot_vehicle_count": vehicle_count,
        "gui_screenshot_j0_signal_state": j0_signal_state,
        "gui_screenshot_simulation_time_s": simulation_time_s,
        "gui_screenshot_step": GUI_SCREENSHOT_STEP,
        "gui_focus_radius_m": GUI_FOCUS_RADIUS_M,
        "gui_screenshot_status": "requested",
        "gui_screenshot_validation_deadline_step": (
            GUI_SCREENSHOT_VALIDATION_DEADLINE_STEP
        ),
    }
    try:
        traci_module.gui.screenshot(view_id, str(screenshot_path))
    except Exception as error:
        evidence["gui_screenshot_status"] = "request_failed"
        evidence["gui_screenshot_error"] = str(error)
        raise GuiScreenshotError(
            f"SUMO GUI screenshot request failed: {error}", evidence
        ) from error
    return evidence


def capture_gui_evidence_if_due(
    gui: bool,
    simulation_step: int,
    traci_module: object,
    screenshot_path: Path,
) -> dict[str, object] | None:
    if not gui or simulation_step != GUI_SCREENSHOT_STEP:
        return None
    return capture_gui_evidence(traci_module, screenshot_path)


def validate_gui_screenshot_if_due(
    simulation_step: int,
    evidence: dict[str, object],
) -> bool:
    if simulation_step <= GUI_SCREENSHOT_STEP:
        return False

    screenshot_path = Path(str(evidence["gui_screenshot_path"]))
    screenshot_size = screenshot_path.stat().st_size if screenshot_path.is_file() else 0
    if screenshot_size > 0:
        evidence.update(
            {
                "gui_screenshot_status": "created",
                "gui_screenshot_validation_step": simulation_step,
                "gui_screenshot_size_bytes": screenshot_size,
            }
        )
        return True

    if simulation_step < GUI_SCREENSHOT_VALIDATION_DEADLINE_STEP:
        return False

    failure_status = "empty" if screenshot_path.is_file() else "missing"
    evidence.update(
        {
            "gui_screenshot_status": failure_status,
            "gui_screenshot_validation_step": simulation_step,
            "gui_screenshot_size_bytes": screenshot_size,
        }
    )
    raise GuiScreenshotError(
        "SUMO GUI screenshot remained "
        f"{failure_status} through simulation step {simulation_step} after "
        f"the request at step {GUI_SCREENSHOT_STEP}: {screenshot_path}",
        evidence,
    )


def run_simulation(
    binary: Path,
    config_path: Path,
    seed: int,
    gui: bool,
    gui_delay_ms: int,
    screenshot_path: Path,
) -> dict[str, object]:
    import traci
    from sumoITScontrol import RampMeter
    from sumoITScontrol.control.ramp_metering import ALINEA

    command = build_sumo_command(binary, config_path, seed, gui, gui_delay_ms)

    # These values are copied from the upstream v0.1.0 demo for smoke testing.
    ramp_meter = RampMeter(
        tl_id="J0",
        mainline_sensors=["e2_5", "e2_4"],
        queue_sensors=["e2_0"],
    )
    controller = ALINEA(
        params={
            "target_occupancy": 10,
            "K_P": 30,
            "K_I": 0,
            "cycle_duration": 60,
            "measurement_period": int(60 / 0.5),
            "min_rate": 5,
            "max_rate": 100,
        },
        ramp_meter=ramp_meter,
    )

    execute_control_calls = 0
    gui_evidence: dict[str, object] = {}
    screenshot_verified = False
    started = False
    try:
        traci.start(command)
        started = True
        for simulation_step in range(1, int(4200 / 0.5) + 1):
            traci.simulationStep()
            current_time = traci.simulation.getCurrentTime()
            controller.execute_control(current_time)
            execute_control_calls += 1
            if gui_evidence and not screenshot_verified:
                screenshot_verified = validate_gui_screenshot_if_due(
                    simulation_step,
                    gui_evidence,
                )
            captured = capture_gui_evidence_if_due(
                gui,
                simulation_step,
                traci,
                screenshot_path,
            )
            if captured is not None:
                gui_evidence = captured
        if gui and not gui_evidence:
            raise RuntimeError(
                f"GUI evidence was not captured at simulation step {GUI_SCREENSHOT_STEP}"
            )
        if gui and not screenshot_verified:
            raise GuiScreenshotError(
                "GUI screenshot was requested but never verified",
                gui_evidence,
            )
    except Exception:
        if started:
            try:
                traci.close()
            except Exception as close_error:
                print(f"TraCI close after failure also failed: {close_error}", file=sys.stderr)
        raise
    else:
        traci.close()

    result: dict[str, object] = {
        "gui": gui,
        "gui_delay_ms": gui_delay_ms,
        "seed": seed,
        "sumo_binary": str(binary),
        "sumo_command": command,
        "simulation_steps": int(4200 / 0.5),
        "alinea_execute_control_calls": execute_control_calls,
        "alinea_control_updates": len(controller.measurement_data["metering_rate"]) - 1,
    }
    result.update(gui_evidence)
    return result


def main() -> int:
    args = parse_args()
    checksums = validate_upstream_assets()
    model_summary = validate_model()
    sumo_home = resolve_sumo_home()
    binary = resolve_sumo_binary(args.gui, args.sumo_binary)
    run_root, runtime_config, detector_outputs = prepare_runtime_copy()

    summary: dict[str, object] = {
        "status": "validated" if args.validate_only else "running",
        "classification": "technical smoke test; not thesis evidence",
        "upstream_tag": UPSTREAM_TAG,
        "upstream_commit": UPSTREAM_COMMIT,
        "sumo_home": str(sumo_home),
        "sumo_binary": str(binary),
        "gui_delay_ms": args.gui_delay_ms,
        "runtime_directory": str(run_root),
        "runtime_config": str(runtime_config),
        "detector_outputs": detector_outputs,
        "upstream_sha256": checksums,
        "model": model_summary,
    }
    summary_path = run_root / "summary.json"
    if not args.validate_only:
        try:
            summary.update(
                run_simulation(
                    binary,
                    runtime_config,
                    args.seed,
                    args.gui,
                    args.gui_delay_ms,
                    run_root / "gui_screenshot.png",
                )
            )
        except GuiScreenshotError as error:
            summary.update(error.evidence)
            summary["status"] = "failed"
            summary["error"] = str(error)
            summary_path.write_text(
                json.dumps(summary, indent=2, sort_keys=True) + "\n",
                encoding="utf-8",
            )
            print(json.dumps(summary, indent=2, sort_keys=True), file=sys.stderr)
            print(f"Failure summary written to: {summary_path}", file=sys.stderr)
            raise
        summary["status"] = "completed"

    summary_path.write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(summary, indent=2, sort_keys=True))
    print(f"Summary written to: {summary_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

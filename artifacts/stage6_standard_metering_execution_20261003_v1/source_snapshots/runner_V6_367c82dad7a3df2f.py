"""S1-only preparation of matched exploratory TraCI cards; launch is gated.

Never call launch without an independent exact-card release. Existing OPEN
inputs/results and the boundary runner are immutable. All failures count.
"""
from __future__ import annotations

import argparse
import csv
from datetime import datetime, timezone
import gzip
import hashlib
import json
import math
import os
from pathlib import Path
import platform
import re
import shutil
import signal
import socket
import subprocess
import sys
import time
import xml.etree.ElementTree as ET

from control import Feedback, FeedbackParameters, PulseScheduler, classify_service_window, front_at_stopline

ROOT = Path(__file__).resolve().parents[3]
BASE_PACKAGES = ROOT / "artifacts/stage6_boundary_search_20261002_v1/inputs"
BASE_RAW = ROOT / "data/raw/stage6_boundary_search_20261002_v1"
PACKAGES = ROOT / "artifacts/stage6_standard_metering_execution_20261003_v1/inputs"
RAW = ROOT / "data/raw/stage6_standard_metering_20261003_v1"
PLAN = ROOT / "docs/stage6/STAGE6_CURRENT_VERSION_STANDARD_METERING_PLAN_20261003.md"
NETWORK = ROOT / "artifacts/stage6_baseline_localization_20260921_v1/LOC_M3350_S17/engineering/build_attempts/TV_BUILD01/network.net.xml"
SUMO = Path("/Library/Frameworks/EclipseSUMO.framework/Versions/1.26.0/EclipseSUMO/bin/sumo")
SUMO_SHA = "3bd1eaa3b167fb527ac33b154dfb57b41b9a40d5bc3e26246489824dd7977179"
NETWORK_SHA = "887c232483f0c68dc024334ff5997250d7d36299ab2744bdcf49d5a314c700ca"
CONTROL = Path(__file__).with_name("control.py")
MAX_GLOBAL_STARTS, MAX_NEW_STARTS = 40, 8
MAX_TOTAL_BYTES, MAX_RUN_BYTES, MAX_WALL_S = 8_000_000_000, 250_000_000, 120
SEEDS = (17, 23, 42)
MODES = {"NOOP", "ALINEA"}
PARAMETERS = dict(target_pct=11.0, gain_veh_h_per_pct=70.0,
                  minimum_veh_h=300.0, maximum_veh_h=1200.0,
                  initial_veh_h=900.0)
OCCUPANCY_SAMPLING = {"source":"TraCI E1 getLastStepOccupancy",
                      "window":"30 consecutive post-step samples for [decision_time-30,decision_time)",
                      "aggregation":"arithmetic mean of 30 percentage values",
                      "first_step_end_s":601,"first_decision_s":630,
                      "last_decision_s":4170,"legacy_interval_api":"observation only"}
BASE_FILES = ("demand.rou.xml", "scenario.add.xml", "scenario.sumocfg")
DETECTORS = ("p1_main_down_20_l0", "p1_main_down_20_l1")
STORAGE_LANE, INTERNAL_LANE, TLS = "ramp_storage_0", ":ramp_mid_0_0", "ramp_mid"
HORIZON = 4200


def sha(path):
    digest = hashlib.sha256()
    with Path(path).open("rb") as stream:
        for block in iter(lambda: stream.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


def now():
    return datetime.now(timezone.utc).isoformat()


def write_json_exclusive(path, obj):
    with Path(path).open("x") as stream:
        json.dump(obj, stream, indent=2, sort_keys=True)
        stream.write("\n")


def tree_bytes(path):
    return sum(p.stat().st_size for p in path.rglob("*") if p.is_file()) if path.exists() else 0


def base_path(seed):
    if seed not in SEEDS:
        raise ValueError("unreviewed seed")
    return BASE_PACKAGES / f"M3600_R900_S{seed}"


def assert_network_controlled_link():
    root = ET.parse(NETWORK).getroot()
    links = [x for x in root.findall("connection") if x.get("tl") == TLS]
    expected = [("ramp_storage", "ramp_accel", "0", "0", INTERNAL_LANE, "0")]
    actual = [(x.get("from"), x.get("to"), x.get("fromLane"), x.get("toLane"),
               x.get("via"), x.get("linkIndex")) for x in links]
    if actual != expected:
        raise ValueError(f"ramp controlled-link topology changed: {actual}")
    tls_open = root.find("./tlLogic[@id='ramp_mid'][@programID='A_OPEN']")
    if tls_open is None or [x.get("state") for x in tls_open.findall("phase")] != ["G"]:
        raise ValueError("open ramp phase changed")
    lane = root.find("./edge[@id='ramp_storage']/lane[@id='ramp_storage_0']")
    if lane is None or abs(float(lane.get("length")) - 204.49) > 0.01:
        raise ValueError("storage stopline position changed")
    return float(lane.get("length"))


def budget_snapshot():
    old_res = BASE_PACKAGES / "reservations"
    new_res = PACKAGES / "reservations"
    old = len(list(old_res.glob("*.json"))) if old_res.exists() else 0
    new = len(list(new_res.glob("*.json"))) if new_res.exists() else 0
    if old < 18:
        raise ValueError("public 18-start baseline ledger incomplete")
    return {"old_starts": old, "new_starts": new, "global_starts": old + new,
            "old_raw_bytes": tree_bytes(BASE_RAW), "new_raw_bytes": tree_bytes(RAW),
            "shared_raw_bytes": tree_bytes(BASE_RAW) + tree_bytes(RAW)}


def prepare(mode, seed, revision="V1"):
    if mode not in MODES or seed not in SEEDS or (mode == "NOOP" and seed != 17):
        raise ValueError("unreviewed mode/seed")
    if not re.fullmatch(r"V[1-9][0-9]*",revision):
        raise ValueError("invalid revision")
    FeedbackParameters(**PARAMETERS)
    if sha(SUMO) != SUMO_SHA or sha(NETWORK) != NETWORK_SHA:
        raise ValueError("runtime or network drift")
    stopline = assert_network_controlled_link()
    base = base_path(seed)
    baseline_card = json.loads((base / "card.json").read_text())
    if baseline_card["seed"] != seed or baseline_card["counts"] != {"M":3000,"R":600,"U":300,"X":150}:
        raise ValueError("baseline card population drift")
    if any(sha(base / name) != baseline_card["input_sha256"][name] for name in BASE_FILES):
        raise ValueError("baseline inputs changed")
    baseline_output = BASE_RAW / baseline_card["run_id"] / "outputs"
    baseline_receipt = baseline_output / "execution_receipt.json"
    if not baseline_receipt.is_file() or json.loads(baseline_receipt.read_text()).get("status") != "COMPLETED":
        raise ValueError("baseline receipt unavailable")
    run_id = f"M3600_R900_S{seed}_{mode}_TRACI_{revision}"
    package, output = PACKAGES / run_id, RAW / run_id / "outputs"
    if package.exists() or output.parent.exists():
        raise FileExistsError("run already exists")
    package.mkdir(parents=True, exist_ok=False)
    shutil.copyfile(base / "demand.rou.xml", package / "demand.rou.xml")
    add = ET.parse(base / "scenario.add.xml")
    for node in add.getroot().iter():
        for key in ("file", "dest"):
            if key in node.attrib:
                node.set(key, str(output / Path(node.get(key)).name))
    ET.indent(add)
    add.write(package / "scenario.add.xml", encoding="utf-8", xml_declaration=True)
    cfg = ET.parse(base / "scenario.sumocfg")
    cfg.find("./input/route-files").set("value", str(package / "demand.rou.xml"))
    cfg.find("./input/additional-files").set("value", str(package / "scenario.add.xml"))
    for node in cfg.findall("./output/*") + cfg.findall("./report/*"):
        if node.get("value", "").startswith("/"):
            node.set("value", str(output / Path(node.get("value")).name))
    ET.indent(cfg)
    cfg.write(package / "scenario.sumocfg", encoding="utf-8", xml_declaration=True)
    snapshot = budget_snapshot()
    card = {"schema_version":1, "classification":"EXPLORATORY", "status":"PREPARED_NOT_RELEASED",
            "mode":mode, "revision":revision, "run_id":run_id, "seed":seed, "counts":baseline_card["counts"],
            "package":str(package), "output":str(output), "plan":str(PLAN),
            "plan_sha256":sha(PLAN), "runner_sha256":sha(__file__),
            "controller_sha256":sha(CONTROL), "sumo_sha256":sha(SUMO),
            "network_sha256":sha(NETWORK), "base_card_sha256":sha(base / "card.json"),
            "base_receipt_sha256":sha(baseline_receipt), "base_output":str(baseline_output),
            "base_input_sha256":baseline_card["input_sha256"],
            "input_sha256":{name:sha(package / name) for name in BASE_FILES},
            "python":platform.python_version(), "traci_version_expected":"1.26.0",
            "sumoitscontrol_version_expected":"0.1.0", "horizon_s":HORIZON,
            "feedback":PARAMETERS, "feedback_update_s":[630,4170,30],
            "occupancy_sampling":OCCUPANCY_SAMPLING,
            "meter_start_s":600, "initial_credit":0.0, "first_slot_at_initial_rate_s":603,
            "meter_controlled_link":{"from":"ramp_storage_0","to":"ramp_accel_0",
                                      "via":INTERNAL_LANE,"tls":TLS,"link_index":0,
                                      "storage_length_m":stopline},
            "service_candidate":{"minimum_qualified_slots_across_run":20,"minimum_crossing_ratio":0.9,
                                 "queue_distance_to_stopline_m":1.1,"queue_speed_strictly_below_m_s":0.1,
                                 "downstream_clearance":"nearest_internal_vehicle_rear >= front_length+front_minGap"},
            "limits":{"wall_s":MAX_WALL_S,"run_bytes":MAX_RUN_BYTES,
                      "total_raw_bytes":MAX_TOTAL_BYTES,"global_starts":MAX_GLOBAL_STARTS,
                      "new_control_technical_starts":MAX_NEW_STARTS,"poll_s":0.1},
            "budget_at_prepare":snapshot}
    write_json_exclusive(package / "card.json", card)
    return {"status":"PREPARED_NO_SIMULATION","card":str(package / "card.json"),
            "card_sha256":sha(package / "card.json"),"budget":snapshot}


def preflight(card_path, approved_hash, release_path=None):
    card_path = Path(card_path).resolve(strict=True)
    if sha(card_path) != approved_hash:
        raise ValueError("card hash mismatch")
    card = json.loads(card_path.read_text())
    mode, seed = card["mode"], card["seed"]
    if mode not in MODES or seed not in SEEDS or (mode == "NOOP" and seed != 17):
        raise ValueError("mode/seed not reviewed")
    package, output = Path(card["package"]), Path(card["output"])
    revision = card["revision"]
    if not re.fullmatch(r"V[1-9][0-9]*",revision):
        raise ValueError("invalid card revision")
    run_id = f"M3600_R900_S{seed}_{mode}_TRACI_{revision}"
    if (card["run_id"] != run_id or package != PACKAGES / run_id or
            output != RAW / run_id / "outputs" or card_path != package / "card.json"):
        raise ValueError("path binding mismatch")
    if output.parent.exists() or (PACKAGES / "reservations" / f"{run_id}.json").exists():
        raise FileExistsError("one-use start already consumed")
    for path, key in ((Path(__file__),"runner_sha256"),(CONTROL,"controller_sha256"),
                      (SUMO,"sumo_sha256"),(NETWORK,"network_sha256"),(PLAN,"plan_sha256"),
                      (base_path(seed)/"card.json","base_card_sha256"),
                      (Path(card["base_output"])/"execution_receipt.json","base_receipt_sha256")):
        if sha(path) != card[key]:
            raise ValueError(f"bound file changed: {path}")
    if card["sumo_sha256"] != SUMO_SHA or card["network_sha256"] != NETWORK_SHA:
        raise ValueError("unreviewed SUMO/network")
    if (card["feedback"] != PARAMETERS or card["occupancy_sampling"] != OCCUPANCY_SAMPLING
            or card["python"] != platform.python_version()):
        raise ValueError("parameter or runtime drift")
    for name in BASE_FILES:
        if sha(package/name) != card["input_sha256"][name]:
            raise ValueError(f"input changed: {name}")
    if sha(package/"demand.rou.xml") != card["base_input_sha256"]["demand.rou.xml"]:
        raise ValueError("demand not byte-identical")
    config = ET.parse(package/"scenario.sumocfg").getroot()
    if config.find("./time/end").get("value") != "4200" or config.find("./time/step-length").get("value") != "1":
        raise ValueError("time contract changed")
    if config.find("./random_number/seed").get("value") != str(seed):
        raise ValueError("seed changed")
    if config.find("./input/net-file").get("value") != str(NETWORK):
        raise ValueError("network path changed")
    if config.find("./input/route-files").get("value") != str(package/"demand.rou.xml"):
        raise ValueError("route path changed")
    if config.find("./input/additional-files").get("value") != str(package/"scenario.add.xml"):
        raise ValueError("additional path changed")
    if ET.parse(package/"scenario.add.xml").getroot().find("WAUT").get("startProg") != "A_OPEN":
        raise ValueError("ramp baseline program changed")
    # Materialized XML must differ from its OPEN parent only by relocated
    # input/output paths. Compare the complete trees, including all detectors,
    # vehicle types, TLS selection, processing, and output flags.
    parent=base_path(seed)
    expected_add=ET.parse(parent/"scenario.add.xml")
    for node in expected_add.getroot().iter():
        for key in ("file","dest"):
            if key in node.attrib: node.set(key,str(output/Path(node.get(key)).name))
    if ET.tostring(expected_add.getroot()) != ET.tostring(ET.parse(package/"scenario.add.xml").getroot()):
        raise ValueError("additional XML differs beyond output paths")
    expected_cfg=ET.parse(parent/"scenario.sumocfg")
    expected_cfg.find("./input/route-files").set("value",str(package/"demand.rou.xml"))
    expected_cfg.find("./input/additional-files").set("value",str(package/"scenario.add.xml"))
    for node in expected_cfg.findall("./output/*")+expected_cfg.findall("./report/*"):
        if node.get("value","").startswith("/"):
            node.set("value",str(output/Path(node.get("value")).name))
    if ET.tostring(expected_cfg.getroot()) != ET.tostring(config):
        raise ValueError("scenario config differs beyond relocated paths")
    assert_network_controlled_link()
    snapshot = budget_snapshot()
    if snapshot["global_starts"] >= MAX_GLOBAL_STARTS or snapshot["new_starts"] >= MAX_NEW_STARTS:
        raise ValueError("start cap reached")
    if snapshot["shared_raw_bytes"] >= MAX_TOTAL_BYTES:
        raise ValueError("shared raw cap reached")
    if release_path is not None:
        release = json.loads(Path(release_path).read_text())
        if (release.get("status") != "PASS_FOR_EXPLORATORY_EXECUTION" or
                release.get("cards",{}).get(run_id) != approved_hash or
                release.get("runner_sha256") != card["runner_sha256"] or
                release.get("plan_sha256") != card["plan_sha256"]):
            raise ValueError("independent exact-card release mismatch")
    return card


def free_port():
    with socket.socket() as sock:
        sock.bind(("127.0.0.1",0))
        return sock.getsockname()[1]


def connect_traci(traci_module,port,process,trace,deadline_s=10.0,
                  clock=None,sleeper=None,enforce_alarm=True):
    """Bounded TraCI handshakes with timestamped child-status evidence.

    Each attempt is one TraCI protocol connection. No separate TCP probe may
    consume the server's single-client slot. ``proc`` makes early exit visible.
    """
    clock=clock or time.monotonic
    sleeper=sleeper or time.sleep
    started=clock()
    for attempt in range(1,102):
        before=clock()
        remaining=deadline_s-(before-started)
        if remaining <= 0:
            raise TimeoutError(f"TraCI startup deadline {deadline_s}s expired")
        poll_before=process.poll()
        if poll_before is not None:
            raise RuntimeError(f"SUMO exited before TraCI attempt {attempt}: {poll_before}")
        try:
            if enforce_alarm:
                old_handler=signal.getsignal(signal.SIGALRM)
                def deadline_expired(signum,frame):
                    raise TimeoutError(f"TraCI startup deadline {deadline_s}s expired during handshake")
                signal.signal(signal.SIGALRM,deadline_expired)
                signal.setitimer(signal.ITIMER_REAL,remaining)
            try:
                conn=traci_module.connect(port=port,host="localhost",proc=process,
                                          numRetries=0,waitBetweenRetries=0)
            finally:
                if enforce_alarm:
                    signal.setitimer(signal.ITIMER_REAL,0)
                    signal.signal(signal.SIGALRM,old_handler)
            trace({"attempt":attempt,"at_utc":now(),"elapsed_since_start_s":before-started,
                   "startup_deadline_monotonic_s":started+deadline_s,
                   "duration_s":clock()-before,"poll_before":poll_before,
                   "poll_after":process.poll(),"outcome":"CONNECTED"})
            return conn
        except Exception as exc:
            polled=process.poll()
            trace({"attempt":attempt,"at_utc":now(),"elapsed_since_start_s":before-started,
                   "startup_deadline_monotonic_s":started+deadline_s,
                   "duration_s":clock()-before,"poll_before":poll_before,
                   "poll_after":polled,"outcome":"FAILED","error_type":type(exc).__name__,
                   "error":str(exc)})
            if polled is not None:
                raise RuntimeError(f"SUMO exited during TraCI startup: {polled}") from exc
            if isinstance(exc,TimeoutError):
                raise
            if clock()-started >= deadline_s:
                raise TimeoutError(f"TraCI startup deadline {deadline_s}s expired after {attempt} attempts") from exc
            if type(exc).__name__ != "FatalTraCIError":
                raise
            sleeper(min(0.1,max(0.0,deadline_s-(clock()-started))))
    raise TimeoutError(f"TraCI startup deadline {deadline_s}s exhausted at 101 attempts")


def passive_startup_probe(pid,output,mark_s,deadline_at,run=None,clock=None):
    """Inspect one existing SUMO child; never open a TraCI/TCP connection."""
    run=run or subprocess.run
    clock=clock or time.monotonic
    startup_at=deadline_at-10.0
    checks=[("tcp_listeners",["/usr/sbin/lsof","-nP","-a","-p",str(pid),"-iTCP"],0.5,0.1),
            ("process_state",["/bin/ps","-o","pid,ppid,state,wchan,command","-p",str(pid)],0.5,0.1)]
    if mark_s==6:
        checks.append(("stack_sample",["/usr/bin/sample",str(pid),"1","10","-file",
                                       str(output/"sumo_startup_sample_6s.txt")],1.75,1.25))
    result={"at_utc":now(),"mark_s":mark_s,"pid":pid,"checks":{}}
    for name,command,timeout_s,minimum_start_s in checks:
        started_at=clock()
        remaining=deadline_at-started_at-0.05
        if remaining<minimum_start_s:
            result["checks"][name]={"command":command,"status":"SKIPPED_DEADLINE",
                                    "at_utc":now(),"elapsed_since_start_s":started_at-startup_at,
                                    "remaining_s":max(0,remaining)}
            continue
        command_timeout=min(timeout_s,remaining)
        try:
            completed=run(command,capture_output=True,text=True,timeout=command_timeout)
            result["checks"][name]={"command":command,"return_code":completed.returncode,
                                    "at_utc":now(),"elapsed_since_start_s":started_at-startup_at,
                                    "duration_s":clock()-started_at,"timeout_s":command_timeout,
                                    "stdout":completed.stdout[-16000:],
                                    "stderr":completed.stderr[-16000:]}
        except subprocess.TimeoutExpired as exc:
            result["checks"][name]={"command":command,"status":"TIMEOUT",
                                    "at_utc":now(),"elapsed_since_start_s":started_at-startup_at,
                                    "duration_s":clock()-started_at,"timeout_s":command_timeout,
                                    "stdout_tail":str(exc.stdout)[-16000:],
                                    "stderr_tail":str(exc.stderr)[-16000:]}
        except Exception as exc:
            result["checks"][name]={"command":command,"status":"ERROR",
                                    "at_utc":now(),"elapsed_since_start_s":started_at-startup_at,
                                    "duration_s":clock()-started_at,"timeout_s":command_timeout,
                                    "error":f"{type(exc).__name__}: {exc}"}
    return result


def due_startup_probes(record,completed_marks):
    if record.get("outcome")!="FAILED": return []
    return [mark for mark in (2,6) if mark not in completed_marks and
            record["elapsed_since_start_s"] >= mark]


def csv_writer(path, fields):
    stream = path.open("x", newline="")
    writer = csv.DictWriter(stream, fieldnames=fields)
    writer.writeheader()
    return stream, writer


def completed_occupancy_window(samples, decision_time):
    """Return exact [decision_time-30, decision_time) E1 last-step mean."""
    if len(samples) != 30 or [row[0] for row in samples] != list(range(decision_time-29,decision_time+1)):
        raise ValueError(f"incomplete E1 step occupancy window ending {decision_time}")
    values = [[],[]]
    for _,l0,l1 in samples:
        for lane,value in enumerate((l0,l1)):
            if not math.isfinite(value) or not 0 <= value <= 100:
                raise ValueError("invalid E1 last-step occupancy")
            values[lane].append(value)
    return [sum(lane_values)/30 for lane_values in values]


def validate_output(output):
    required = {"fcd.xml.gz","tripinfo.xml","vehroute.xml","lanechanges.xml",
                "queues.xml","sumo_summary.xml","tls_states.xml",
                "shared_boundary_e2.xml","ramp_storage_e2.xml",
                "controller_steps.csv","feedback_updates.csv","detector_step_occupancy.csv",
                "service_windows.csv",
                "vehicle_metadata.csv"}
    required |= {f"p1_{edge}_{pos}_l{lane}.xml"
                 for edge,pos,lanes in (("main_up",1300,2),("merge_section",20,3),
                                        ("main_down",20,2),("main_down",200,2))
                 for lane in range(lanes)}
    for name in sorted(required):
        path=output/name
        if not path.is_file() or path.stat().st_size==0:
            raise ValueError(f"missing/empty output {name}")
        if name.endswith(".xml") or name.endswith(".xml.gz"):
            with (gzip.open(path,"rb") if name.endswith(".gz") else path.open("rb")) as stream:
                for _,node in ET.iterparse(stream,events=("end",)):
                    node.clear()


def worker(card_path):
    """Child of budget guardian. Called only after parent release/reservation."""
    import traci  # intentionally lazy: S1 imports and tests cannot launch SUMO
    card = json.loads(Path(card_path).read_text())
    package, output, mode = Path(card["package"]), Path(card["output"]), card["mode"]
    reservation = PACKAGES/"reservations"/f"{card['run_id']}.json"
    if not reservation.is_file() or not output.is_dir() or not (PACKAGES/"launch.lock").is_file():
        raise ValueError("worker requires live one-use guardian reservation")
    if json.loads(reservation.read_text()).get("card_sha256") != sha(card_path):
        raise ValueError("worker reservation/card mismatch")
    port = free_port()
    env = dict(os.environ, SUMO_HOME=str(SUMO.parent.parent/"share/sumo"))
    command = [str(SUMO),"-c",str(package/"scenario.sumocfg"),"--remote-port",str(port)]
    baseline_receipt=json.loads((Path(card["base_output"])/"execution_receipt.json").read_text())
    write_json_exclusive(output/"startup_context.json",
        {"worker_command":command,"baseline_command":baseline_receipt.get("command"),
         "worker_cwd":os.getcwd(),"sumo_home":env["SUMO_HOME"],
         "environment_override_keys":["SUMO_HOME"],
         "other_environment":"inherited unchanged from guardian",
         "traci_host":"localhost","port":port,"startup_deadline_s":10.0,
         "baseline_runner_mode":"standalone SUMO without --remote-port"})
    sumo_stdout, sumo_stderr = (output/"sumo_stdout.log").open("x"), (output/"sumo_stderr.log").open("x")
    proc = subprocess.Popen(command, stdout=sumo_stdout, stderr=sumo_stderr, env=env)
    conn = None
    startup_trace=(output/"traci_startup.jsonl").open("x")
    probe_trace=(output/"startup_probe.jsonl").open("x")
    completed_probes=set()
    def trace_startup(record):
        startup_trace.write(json.dumps(record,sort_keys=True)+"\n")
        startup_trace.flush()
        for mark in due_startup_probes(record,completed_probes):
            completed_probes.add(mark)
            evidence=passive_startup_probe(proc.pid,output,mark,
                                           record["startup_deadline_monotonic_s"])
            probe_trace.write(json.dumps(evidence,sort_keys=True)+"\n")
            probe_trace.flush()
    steps_fields = ["time_begin_s","time_end_s","mode","command_rate_veh_h","credit_before",
                    "credit_after","slot_scheduled","requested_state","observed_state",
                    "queue_vehicle_count","queued_unblocked_slot","front_queued_vehicle_id",
                    "stopline_gap_m","downstream_rear_clearance_m","required_clearance_m",
                    "internal_before_ids_json",
                    "crossing_bracket_ids_json","red_crossing_bracket_ids_json",
                    "sampling_uncertain","dropped_credit_total"]
    feedback_fields = ["decision_time_s","application_time_s","interval_begin_s","interval_end_s",
                       "detector_l0","detector_l1","occupancy_source","sample_count",
                       "occ_l0_pct","occ_l1_pct","occ_mean_pct",
                       "legacy_last_interval_l0_pct","legacy_last_interval_l1_pct",
                       "n_vehicle_l0","n_vehicle_l1","valid","target_pct","gain_veh_h_per_pct",
                       "rate_previous_veh_h","rate_raw_veh_h","rate_clipped_veh_h"]
    service_fields = ["window_begin_s","window_end_s","scheduled_slots","queued_unblocked_slots",
                      "crossings_in_slots","empty_slots","red_crossings","repeated_slots",
                      "wrong_vehicle_slots","classification"]
    sf, sw = csv_writer(output/"controller_steps.csv",steps_fields)
    ff, fw = csv_writer(output/"feedback_updates.csv",feedback_fields)
    of, ow = csv_writer(output/"detector_step_occupancy.csv",
                        ["time_begin_s","time_end_s","detector_l0","detector_l1",
                         "occ_l0_pct","occ_l1_pct"])
    vf, vw = csv_writer(output/"service_windows.csv",service_fields)
    mf, mw = csv_writer(output/"vehicle_metadata.csv",
                        ["vehicle_id","class","first_departed_step_end_s","type_id",
                         "vehicle_length_m","min_gap_m"])
    feedback = Feedback(FeedbackParameters(**card["feedback"]))
    occupancy_samples = []
    pulses = PulseScheduler()
    window = dict(scheduled_slots=0, queued_unblocked_slots=0, crossings_in_slots=0,
                  empty_slots=0, red_crossings=0, repeated_slots=0, wrong_vehicle_slots=0)
    cumulative = dict(queued_unblocked_slots=0,crossings_in_slots=0,red_crossings=0,
                      repeated_slots=0,wrong_vehicle_slots=0)
    try:
        conn = connect_traci(traci,port,proc,trace_startup)
        lane_length = card["meter_controlled_link"]["storage_length_m"]
        for t in range(HORIZON):
            if abs(conn.simulation.getTime()-t) > 1e-6:
                raise ValueError(f"TraCI time misalignment at {t}")
            if t in range(630,4171,30):
                occ = completed_occupancy_window(occupancy_samples,t)
                occupancy_samples.clear()
                legacy_occ = [conn.inductionloop.getLastIntervalOccupancy(d) for d in DETECTORS]
                counts = [conn.inductionloop.getLastIntervalVehicleNumber(d) for d in DETECTORS]
                if mode == "ALINEA":
                    update = feedback.update(t,t-30,t,*occ)
                    update.pop("update_time_s")
                else:
                    update = dict(interval_begin_s=t-30,interval_end_s=t,
                                  occ_l0_pct=occ[0],occ_l1_pct=occ[1],
                                  occ_mean_pct=(occ[0]+occ[1])/2,
                                  rate_previous_veh_h="",rate_raw_veh_h="",rate_clipped_veh_h="")
                fw.writerow(dict(decision_time_s=t,application_time_s=t,detector_l0=DETECTORS[0],
                                 detector_l1=DETECTORS[1],occupancy_source="mean_last_step_30",
                                 sample_count=30,
                                 legacy_last_interval_l0_pct=legacy_occ[0],
                                 legacy_last_interval_l1_pct=legacy_occ[1],
                                 n_vehicle_l0=counts[0],n_vehicle_l1=counts[1],
                                 valid=True,target_pct=PARAMETERS["target_pct"],
                                 gain_veh_h_per_pct=PARAMETERS["gain_veh_h_per_pct"],**update))
            before_ids = set(conn.lane.getLastStepVehicleIDs(INTERNAL_LANE)) if mode == "ALINEA" and t >= 600 else set()
            if mode == "ALINEA" and t >= 600:
                queue_ids = conn.lane.getLastStepVehicleIDs(STORAGE_LANE)
                front, front_ready, clearance, required_clearance = front_at_stopline(
                    {vid:(conn.vehicle.getLanePosition(vid),conn.vehicle.getSpeed(vid),
                          conn.vehicle.getLength(vid),conn.vehicle.getMinGap(vid)) for vid in queue_ids},
                    {vid:(conn.vehicle.getLanePosition(vid),conn.vehicle.getLength(vid)) for vid in before_ids},
                    lane_length)
                stopline_gap = lane_length-conn.vehicle.getLanePosition(front) if front else ""
                pulse = pulses.step(t,feedback.rate)
                requested = pulse["requested_state"]
                conn.trafficlight.setRedYellowGreenState(TLS,requested)
                actual = conn.trafficlight.getRedYellowGreenState(TLS)
                if actual != requested:
                    raise ValueError("commanded and observed signal differ before step")
            else:
                front=""; front_ready=False; clearance=""; required_clearance=""; stopline_gap=""
                queue_ids=[]; pulse={"credit_before":"","credit_after":"","slot_scheduled":False,
                                                 "dropped_credit_total":""}
                requested=""; actual=conn.trafficlight.getRedYellowGreenState(TLS)
            if mode == "NOOP" or t < 600:
                if actual != "G":
                    raise ValueError("pre-control/no-op ramp not continuously green")
            conn.simulationStep(t+1)
            if 600 <= t < 4170:
                step_occ = [conn.inductionloop.getLastStepOccupancy(d) for d in DETECTORS]
                if any(not math.isfinite(value) or not 0 <= value <= 100 for value in step_occ):
                    raise ValueError(f"invalid E1 last-step occupancy at step end {t+1}")
                occupancy_samples.append((t+1,*step_occ))
                ow.writerow(dict(time_begin_s=t,time_end_s=t+1,detector_l0=DETECTORS[0],
                                detector_l1=DETECTORS[1],occ_l0_pct=step_occ[0],
                                occ_l1_pct=step_occ[1]))
            for vid in conn.simulation.getDepartedIDList():
                mw.writerow({"vehicle_id":vid,"class":vid.split("_",1)[0],
                             "first_departed_step_end_s":t+1,
                             "type_id":conn.vehicle.getTypeID(vid),
                             "vehicle_length_m":conn.vehicle.getLength(vid),
                             "min_gap_m":conn.vehicle.getMinGap(vid)})
            after_ids = set(conn.lane.getLastStepVehicleIDs(INTERNAL_LANE)) if mode == "ALINEA" and t >= 600 else set()
            crossing = sorted(after_ids-before_ids)
            if mode == "ALINEA" and t >= 600:
                slot = bool(pulse["slot_scheduled"])
                queued_unblocked = bool(slot and front_ready)
                window["scheduled_slots"] += int(slot)
                window["queued_unblocked_slots"] += int(queued_unblocked)
                unique_front = bool(queued_unblocked and crossing == [front])
                window["crossings_in_slots"] += int(unique_front)
                window["empty_slots"] += int(slot and not crossing)
                window["red_crossings"] += len(crossing) if not slot else 0
                window["repeated_slots"] += int(slot and len(crossing)>1)
                window["wrong_vehicle_slots"] += int(slot and queued_unblocked and crossing and not unique_front)
                cumulative["queued_unblocked_slots"] += int(queued_unblocked)
                cumulative["crossings_in_slots"] += int(unique_front)
                cumulative["red_crossings"] += len(crossing) if not slot else 0
                cumulative["repeated_slots"] += int(slot and len(crossing)>1)
                cumulative["wrong_vehicle_slots"] += int(slot and queued_unblocked and crossing and not unique_front)
            sw.writerow(dict(time_begin_s=t,time_end_s=t+1,mode=mode,
                            command_rate_veh_h=feedback.rate if mode=="ALINEA" and t>=600 else "",
                            credit_before=pulse["credit_before"],credit_after=pulse["credit_after"],
                            slot_scheduled=pulse["slot_scheduled"],requested_state=requested,
                            observed_state=actual,queue_vehicle_count=len(queue_ids),
                            queued_unblocked_slot=bool(mode=="ALINEA" and t>=600 and queued_unblocked),
                            front_queued_vehicle_id=front,
                            stopline_gap_m=stopline_gap,
                            downstream_rear_clearance_m=clearance,
                            required_clearance_m=required_clearance,
                            internal_before_ids_json=json.dumps(sorted(before_ids)),
                            crossing_bracket_ids_json=json.dumps(crossing),
                            red_crossing_bracket_ids_json=json.dumps(crossing if mode=="ALINEA" and t>=600 and not pulse["slot_scheduled"] else []),
                            sampling_uncertain=bool(crossing),dropped_credit_total=pulse["dropped_credit_total"]))
            if mode == "ALINEA" and t >= 600 and (t+1-600)%120 == 0:
                classification = classify_service_window(**{k:window[k] for k in
                    ("queued_unblocked_slots","crossings_in_slots","red_crossings","repeated_slots","wrong_vehicle_slots")})
                vw.writerow(dict(window_begin_s=t+1-120,window_end_s=t+1,
                                 classification=classification,**window))
                window = dict.fromkeys(window,0)
            if (t+1)%30 == 0:
                sf.flush(); ff.flush(); of.flush(); vf.flush(); mf.flush()
        if mode == "ALINEA" and feedback.last_update != 4170:
            raise ValueError("missing terminal feedback update")
        if abs(conn.simulation.getTime()-4200)>1e-6:
            raise ValueError("incomplete horizon")
        if mode == "ALINEA":
            classification=classify_service_window(**cumulative)
            vw.writerow(dict(window_begin_s=600,window_end_s=4200,
                             scheduled_slots="ALL",empty_slots="ALL",classification=classification,**cumulative))
    except Exception as exc:
        print(f"SUMO_WORKER_EXCEPTION pid={proc.pid} poll_returncode={proc.poll()} "
              f"error={type(exc).__name__}: {exc}",file=sys.stderr,flush=True)
        raise
    finally:
        for stream in (sf,ff,of,vf,mf,startup_trace,probe_trace): stream.close()
        if conn is not None:
            try: conn.close(False)
            except Exception: pass
        if proc.poll() is None:
            try: proc.wait(timeout=3)
            except subprocess.TimeoutExpired:
                proc.terminate()
                try: proc.wait(timeout=3)
                except subprocess.TimeoutExpired:
                    proc.kill(); proc.wait(timeout=3)
        sumo_stdout.close(); sumo_stderr.close()
        print(f"SUMO_CHILD_EXIT pid={proc.pid} returncode={proc.returncode}",file=sys.stderr,flush=True)
        for label,path in (("sumo_stdout",output/"sumo_stdout.log"),
                           ("sumo_stderr",output/"sumo_stderr.log"),
                           ("sumo_log",output/"sumo.log"),
                           ("sumo_error_log",output/"sumo_error.log")):
            if path.exists():
                with path.open("rb") as stream:
                    stream.seek(max(0,path.stat().st_size-4096))
                    tail=stream.read().decode("utf-8","replace")
                print(f"SUMO_OUTPUT_STATUS {label} bytes={path.stat().st_size} tail={tail!r}",
                      file=sys.stderr,flush=True)
            else:
                print(f"SUMO_OUTPUT_STATUS {label} missing",file=sys.stderr,flush=True)
    if proc.returncode != 0:
        raise RuntimeError(f"SUMO exited {proc.returncode}")
    validate_output(output)


def launch(card_path, approved_hash, release_path):
    card = preflight(card_path,approved_hash,release_path)
    PACKAGES.mkdir(parents=True,exist_ok=True)
    lock = PACKAGES/"launch.lock"
    lock_fd = os.open(lock,os.O_CREAT|os.O_EXCL|os.O_WRONLY,0o644)
    os.close(lock_fd)
    started=now(); clock=time.monotonic(); child=None; reason=None; failure=None
    output=Path(card["output"])
    try:
        preflight(card_path,approved_hash,release_path)
        reservations=PACKAGES/"reservations"; reservations.mkdir(exist_ok=True)
        write_json_exclusive(reservations/f"{card['run_id']}.json",
                             {"run_id":card["run_id"],"reserved_at":started,
                              "card_sha256":approved_hash,"release_sha256":sha(release_path),
                              "counts_toward_global_and_new_caps":True})
        output.mkdir(parents=True,exist_ok=False)
        with (output/"worker_stdout.log").open("x") as out, (output/"worker_stderr.log").open("x") as err:
            child=subprocess.Popen([sys.executable,str(Path(__file__)),"_worker","--card",str(card_path)],
                                   stdout=out,stderr=err,start_new_session=True)
            while child.poll() is None:
                if time.monotonic()-clock >= MAX_WALL_S: reason="WALL_LIMIT"
                elif tree_bytes(output)>=MAX_RUN_BYTES: reason="RUN_BYTES_LIMIT"
                elif tree_bytes(BASE_RAW)+tree_bytes(RAW)>=MAX_TOTAL_BYTES: reason="GLOBAL_RAW_LIMIT"
                if reason:
                    os.killpg(child.pid,signal.SIGTERM)
                    try: child.wait(timeout=3)
                    except subprocess.TimeoutExpired:
                        os.killpg(child.pid,signal.SIGKILL);child.wait(timeout=3)
                    break
                time.sleep(0.1)
            if not reason and child.returncode != 0: reason="WORKER_FAILED"
            if not reason and (time.monotonic()-clock >= MAX_WALL_S or tree_bytes(output)>=MAX_RUN_BYTES or tree_bytes(BASE_RAW)+tree_bytes(RAW)>=MAX_TOTAL_BYTES):
                reason="LIMIT_AT_EXIT"
    except Exception as exc:
        failure=f"{type(exc).__name__}: {exc}"
        if child is not None and child.poll() is None:
            os.killpg(child.pid,signal.SIGTERM);child.wait(timeout=3)
    finally:
        lock.unlink()
    files={p.name:{"sha256":sha(p),"bytes":p.stat().st_size} for p in sorted(output.glob("*")) if p.is_file()}
    receipt=build_receipt(card=card,approved_hash=approved_hash,release_sha=sha(release_path),
                          started=started,wall_s=time.monotonic()-clock,child=child,
                          reason=reason,failure=failure,files=files,budget_after=budget_snapshot())
    write_json_exclusive((output if output.exists() else Path(card["package"])) / "execution_receipt.json",receipt)
    return receipt


def build_receipt(*,card,approved_hash,release_sha,started,wall_s,child,reason,failure,files,budget_after):
    """One manifest contract shared with the existing boundary validator."""
    if any(Path(name).name!=name or meta.get("bytes",-1)<0 or len(meta.get("sha256",""))!=64
           for name,meta in files.items()):
        raise ValueError("invalid output manifest")
    return {"status":"COMPLETED" if child is not None and child.returncode==0 and not reason and not failure else "FAILED",
            "run_id":card["run_id"],"classification":"EXPLORATORY","started_at":started,
            "finished_at":now(),"wall_s":wall_s,"worker_pid":child.pid if child else None,
            "return_code":child.returncode if child else None,"stop_reason":reason,"failure":failure,
            "card_sha256":approved_hash,"release_sha256":release_sha,
            "output_manifest":files,"output_bytes":sum(x["bytes"] for x in files.values()),
            "budget_after":budget_after}


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    sub=parser.add_subparsers(dest="action",required=True)
    prep=sub.add_parser("prepare");prep.add_argument("--mode",choices=sorted(MODES),required=True)
    prep.add_argument("--seed",type=int,required=True)
    prep.add_argument("--revision",default="V1")
    for action in ("preflight","launch"):
        p=sub.add_parser(action);p.add_argument("--card",required=True)
        p.add_argument("--approved-card-sha256",required=True)
        p.add_argument("--release",required=action=="launch")
    internal=sub.add_parser("_worker");internal.add_argument("--card",required=True)
    a=parser.parse_args()
    if a.action=="prepare": result=prepare(a.mode,a.seed,a.revision)
    elif a.action=="preflight":
        card=preflight(a.card,a.approved_card_sha256,a.release)
        result={"status":"STATIC_PREFLIGHT_PASS_NO_SIMULATION","run_id":card["run_id"]}
    elif a.action=="launch": result=launch(a.card,a.approved_card_sha256,a.release)
    else: worker(a.card);result={"status":"WORKER_COMPLETED"}
    print(json.dumps(result,indent=2,sort_keys=True))
    return int(result["status"] in {"FAILED"})


if __name__=="__main__": raise SystemExit(main())

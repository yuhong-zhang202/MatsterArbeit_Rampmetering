"""Bounded exploratory Stage 6 search: immutable inputs and one-use execution.

No defaults in this module are formal research parameters. A launch requires a
hash-bound card and a separate release JSON produced after independent review.
"""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import gzip
import hashlib
import json
import os
from pathlib import Path
import platform
import random
import re
import signal
import subprocess
import sys
import time
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[3]
REFERENCE = ROOT / "artifacts/stage6_full_network_abc_matched_rebuild_20260926_v1/inputs_retry2/A"
NETWORK = ROOT / "artifacts/stage6_baseline_localization_20260921_v1/LOC_M3350_S17/engineering/build_attempts/TV_BUILD01/network.net.xml"
SUMO = Path("/Library/Frameworks/EclipseSUMO.framework/Versions/1.26.0/EclipseSUMO/bin/sumo")
SUMO_HOME = SUMO.parent.parent / "share/sumo"
SUMO_SHA = "3bd1eaa3b167fb527ac33b154dfb57b41b9a40d5bc3e26246489824dd7977179"
RAW = ROOT / "data/raw/stage6_boundary_search_20261002_v1"
PACKAGES = ROOT / "artifacts/stage6_boundary_search_20261002_v1/inputs"
MAX_STARTS, MAX_RAW, MAX_RUN_BYTES, MAX_SECONDS = 40, 8_000_000_000, 250_000_000, 120
HORIZON = 4200
REQUIRED = {"fcd.xml.gz", "tripinfo.xml", "vehroute.xml", "lanechanges.xml", "queues.xml", "sumo_summary.xml", "tls_states.xml", "shared_boundary_e2.xml", "ramp_storage_e2.xml"}


def sha(path):
    h = hashlib.sha256()
    with Path(path).open("rb") as f:
        for block in iter(lambda: f.read(1 << 20), b""): h.update(block)
    return h.hexdigest()


def now():
    return datetime.now(timezone.utc).isoformat()


def write_json(path, value):
    with Path(path).open("x") as f:
        json.dump(value, f, indent=2, sort_keys=True)
        f.write("\n")


def write_xml(path, root):
    ET.indent(root, space="  ")
    with Path(path).open("xb") as f:
        ET.ElementTree(root).write(f, encoding="utf-8", xml_declaration=True)


def speed_factor(seed, cls, index):
    """ID-keyed, prospectively generated truncated Gaussian; no SUMO output."""
    key = f"stage6-boundary-v1|{seed}|{cls}|{index}".encode()
    rng = random.Random(int.from_bytes(hashlib.sha256(key).digest(), "big"))
    for _ in range(1000000):
        value = rng.gauss(1.0, 0.1)
        if 0.2 <= value <= 2.0: return f"{value:.10f}"
    raise ValueError("speedFactor draw failed")


def vehicle_records(q_main, q_ramp, seed):
    records = []
    for cls, rate, begin, end in (("M", q_main, 0, 3000), ("R", q_ramp, 600, 3000), ("U", 360, 0, 3000), ("X", 180, 0, 3000)):
        # Rates in this design yield exact integer counts. Refuse silent rounding.
        count_exact = rate * (end - begin) / 3600
        count = round(count_exact)
        if abs(count_exact - count) > 1e-8: raise ValueError("rate produces noninteger cohort")
        for index in range(count):
            ms = begin * 1000 + (index * (end - begin) * 1000 // count)
            record = {"id": f"{cls}_flow.{index}", "type": "technical_passenger", "route": f"{cls}_route", "depart": f"{ms // 1000}.{ms % 1000:03d}", "departPos": "100" if cls == "M" else "last", "departLane": "best", "departSpeed": "max", "speedFactor": speed_factor(seed, cls, index)}
            records.append((ms, record))
    return [r for _, r in sorted(records, key=lambda x: (x[0], x[1]["id"]))]


def prepare(run_id, q_main, q_ramp, seed, plan):
    if not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9_.-]{0,100}", run_id): raise ValueError("invalid run ID")
    if q_main <= 0 or q_ramp < 0 or seed < 0: raise ValueError("invalid demand/seed")
    plan = Path(plan).resolve(strict=True)
    package, output = PACKAGES / run_id, RAW / run_id / "outputs"
    if package.exists() or output.parent.exists(): raise FileExistsError("run ID already exists")
    records = vehicle_records(q_main, q_ramp, seed)
    package.mkdir(parents=True, exist_ok=False)
    routes = ET.Element("routes")
    reference_routes = ET.parse(REFERENCE / "demand.rou.xml").getroot()
    for node in reference_routes:
        if node.tag in {"vType", "route"}: routes.append(node)
    if routes.find("vType").attrib != {"id": "technical_passenger", "vClass": "passenger"}: raise ValueError("reference vehicle type changed")
    for record in records: ET.SubElement(routes, "vehicle", record)
    write_xml(package / "demand.rou.xml", routes)
    additional = ET.parse(REFERENCE / "scenario.add.xml").getroot()
    additional.find("WAUT").set("startProg", "A_OPEN")
    for node in additional.iter():
        for key in ("file", "dest"):
            if key in node.attrib: node.set(key, str(output / Path(node.get(key)).name))
    write_xml(package / "scenario.add.xml", additional)
    config = ET.parse(REFERENCE / "scenario.sumocfg").getroot()
    config.find("./input/net-file").set("value", str(NETWORK))
    config.find("./input/route-files").set("value", str(package / "demand.rou.xml"))
    config.find("./input/additional-files").set("value", str(package / "scenario.add.xml"))
    config.find("./time/end").set("value", str(HORIZON))
    config.find("./random_number/seed").set("value", str(seed))
    for node in config.findall("./output/*") + config.findall("./report/*"):
        if node.get("value", "").startswith("/"):
            filename = "fcd.xml.gz" if node.tag == "fcd-output" else Path(node.get("value")).name
            node.set("value", str(output / filename))
    write_xml(package / "scenario.sumocfg", config)
    card = {"schema_version": 1, "classification": "EXPLORATORY", "mode": "OPEN", "run_id": run_id, "q_main_veh_h": q_main, "q_ramp_veh_h": q_ramp, "seed": seed, "horizon_s": HORIZON, "schedule": {"M": [0,3000], "R": [600,3000], "U": [0,3000], "X": [0,3000]}, "background_rates_veh_h": {"U":360,"X":180}, "counts": {c: sum(r["id"].startswith(c + "_") for r in records) for c in "MRUX"}, "speed_factors": "SHA256(stage6-boundary-v1|seed|class|index) seeded Python Random.gauss(1,0.1), rejection [0.2,2], ten decimals", "package": str(package), "output": str(output), "plan": str(plan), "plan_sha256": sha(plan), "runner_sha256": sha(__file__), "network_sha256": sha(NETWORK), "sumo_sha256": sha(SUMO), "input_sha256": {p.name: sha(p) for p in package.iterdir()}, "reference_sha256": {p.name: sha(p) for p in REFERENCE.iterdir() if p.name in {"scenario.add.xml", "scenario.sumocfg", "demand.rou.xml"}}, "limits": {"seconds":MAX_SECONDS,"run_bytes":MAX_RUN_BYTES,"total_raw_bytes":MAX_RAW,"starts":MAX_STARTS,"poll_seconds":0.1}}
    card["python"] = {"version": platform.python_version(), "implementation": platform.python_implementation(), "full_version": sys.version}
    write_json(package / "card.json", card)
    return {"status":"PREPARED_NO_SIMULATION", "card":str(package / "card.json"), "card_sha256":sha(package / "card.json"), "counts":card["counts"]}


def directory_bytes(path):
    return sum(p.stat().st_size for p in Path(path).rglob("*") if p.is_file()) if Path(path).exists() else 0


def preflight(card_path, approved_hash, release_path=None):
    card_path = Path(card_path).resolve(strict=True)
    if sha(card_path) != approved_hash: raise ValueError("card hash mismatch")
    card = json.loads(card_path.read_text())
    package, output = Path(card["package"]), Path(card["output"])
    if package != PACKAGES / card["run_id"] or output != RAW / card["run_id"] / "outputs" or card_path != package / "card.json": raise ValueError("path binding mismatch")
    if output.parent.exists() or (PACKAGES / "reservations" / (card["run_id"] + ".json")).exists(): raise FileExistsError("run already consumed")
    for p, expected in [(Path(__file__),card["runner_sha256"]),(NETWORK,card["network_sha256"]),(SUMO,card["sumo_sha256"]),(Path(card["plan"]),card["plan_sha256"])]:
        if sha(p) != expected: raise ValueError(f"hash mismatch: {p}")
    if card["sumo_sha256"] != SUMO_SHA: raise ValueError("unreviewed SUMO version")
    if card["python"] != {"version": platform.python_version(), "implementation": platform.python_implementation(), "full_version": sys.version}: raise ValueError("Python runtime changed")
    for filename, expected in card["input_sha256"].items():
        if Path(filename).name != filename or sha(package / filename) != expected: raise ValueError("input mismatch")
    for filename, expected in card["reference_sha256"].items():
        if Path(filename).name != filename or sha(REFERENCE / filename) != expected: raise ValueError("reference changed")
    if card.get("classification") != "EXPLORATORY" or card.get("mode") != "OPEN": raise ValueError("invalid run class")
    if card.get("limits") != {"seconds":MAX_SECONDS,"run_bytes":MAX_RUN_BYTES,"total_raw_bytes":MAX_RAW,"starts":MAX_STARTS,"poll_seconds":0.1}: raise ValueError("resource contract mismatch")
    routes = ET.parse(package / "demand.rou.xml").getroot()
    reference_routes = ET.parse(REFERENCE / "demand.rou.xml").getroot()
    if [(n.tag,n.attrib) for n in routes if n.tag != "vehicle"] != [(n.tag,n.attrib) for n in reference_routes if n.tag != "vehicle"]: raise ValueError("vehicle type or routes changed")
    expected_records = vehicle_records(card["q_main_veh_h"], card["q_ramp_veh_h"], card["seed"])
    if [v.attrib for v in routes.findall("vehicle")] != expected_records: raise ValueError("demand materialization mismatch")
    config = ET.parse(package / "scenario.sumocfg").getroot()
    if config.find("./time/end").get("value") != str(HORIZON): raise ValueError("horizon mismatch")
    for field, value in (("net-file",NETWORK),("route-files",package/"demand.rou.xml"),("additional-files",package/"scenario.add.xml")):
        if config.find("./input/"+field).get("value") != str(value): raise ValueError("config input path mismatch")
    if config.find("./random_number/seed").get("value") != str(card["seed"]): raise ValueError("seed mismatch")
    if config.find("./time/step-length").get("value") != "1": raise ValueError("step mismatch")
    for name in ("tripinfo-output.write-unfinished", "tripinfo-output.write-undeparted", "vehroute-output.write-unfinished"):
        if config.find("./output/"+name).get("value") != "true": raise ValueError("censored output disabled")
    if config.find("./processing/time-to-teleport").get("value") != "-1": raise ValueError("teleports enabled")
    if config.find("./processing/collision.action").get("value") != "warn" or config.find("./processing/collision.check-junctions").get("value") != "true": raise ValueError("collision observation changed")
    additional = ET.parse(package / "scenario.add.xml").getroot()
    if additional.find("WAUT").get("startProg") != "A_OPEN" or additional.find("WAUT").findall("wautSwitch"): raise ValueError("ramp selector changed")
    program = ET.parse(NETWORK).getroot().find("./tlLogic[@id='ramp_mid'][@programID='A_OPEN']")
    if program is None or [p.get("state") for p in program.findall("phase")] != ["G"]: raise ValueError("open ramp is not continuously green")
    reference_config = ET.parse(REFERENCE / "scenario.sumocfg").getroot()
    allowed_differences = {"time/end", "random_number/seed"}
    def fixed_settings(root):
        return {f"{parent.tag}/{node.tag}":node.get("value") for parent in root for node in parent if parent.tag not in {"input","output","report"} and f"{parent.tag}/{node.tag}" not in allowed_differences}
    if fixed_settings(config) != fixed_settings(reference_config): raise ValueError("nonexperimental settings changed")
    for node in config.findall("./output/*") + config.findall("./report/*"):
        value = node.get("value", "")
        if value.startswith("/") and Path(value).parent != output: raise ValueError("output escapes run")
    for node in ET.parse(package / "scenario.add.xml").getroot().iter():
        for key in ("file", "dest"):
            if key in node.attrib and Path(node.get(key)).parent != output: raise ValueError("detector output escapes run")
    if directory_bytes(RAW) >= MAX_RAW: raise ValueError("total raw budget exhausted")
    reservations = PACKAGES / "reservations"
    if reservations.exists() and len(list(reservations.glob("*.json"))) >= MAX_STARTS: raise ValueError("start budget exhausted")
    if release_path:
        release = json.loads(Path(release_path).read_text())
        if release.get("status") != "PASS_FOR_EXPLORATORY_EXECUTION" or release.get("plan_sha256") != card["plan_sha256"] or release.get("runner_sha256") != card["runner_sha256"] or release.get("cards", {}).get(card["run_id"]) != approved_hash: raise ValueError("independent execution release mismatch")
    return card


def stop_process(p):
    if p.poll() is None:
        os.killpg(p.pid, signal.SIGTERM)
        try: p.wait(timeout=3)
        except subprocess.TimeoutExpired:
            os.killpg(p.pid, signal.SIGKILL)
            p.wait(timeout=3)


def validate_output(output):
    required = set(REQUIRED)
    required |= {f"p1_{edge}_{pos}_l{lane}.xml" for edge,pos,lanes in [("main_up",1300,2),("merge_section",20,3),("main_down",20,2),("main_down",200,2)] for lane in range(lanes)}
    for name in sorted(required):
        p = output / name
        if not p.is_file() or p.stat().st_size == 0: raise ValueError(f"missing output {name}")
        with (gzip.open(p,"rb") if name.endswith(".gz") else p.open("rb")) as f:
            for _, node in ET.iterparse(f, events=("end",)): node.clear()


def launch(card_path, approved_hash, release_path):
    card = preflight(card_path, approved_hash, release_path)
    reservations = PACKAGES / "reservations"
    reservations.mkdir(exist_ok=True)
    lock = PACKAGES / "launch.lock"
    # Exclusive lock covers budget recheck and whole run: no parallel cap races.
    fd = os.open(lock, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o644)
    os.close(fd)
    p = None
    output = Path(card["output"])
    started, reason, error = now(), None, None
    timer = time.monotonic()
    try:
        preflight(card_path, approved_hash, release_path)
        write_json(reservations / (card["run_id"] + ".json"), {"run_id":card["run_id"],"card_sha256":approved_hash,"reserved_at":started,"classification":"EXPLORATORY","release_sha256":sha(release_path)})
        output.mkdir(parents=True, exist_ok=False)
        cmd = [str(SUMO), "-c", str(Path(card["package"]) / "scenario.sumocfg")]
        env = dict(os.environ, SUMO_HOME=str(SUMO_HOME))
        with (output/"stdout.log").open("xb") as out, (output/"stderr.log").open("xb") as err:
            p = subprocess.Popen(cmd, stdout=out, stderr=err, start_new_session=True, env=env)
            while p.poll() is None:
                if time.monotonic()-timer >= MAX_SECONDS: reason="WALL_LIMIT"
                elif directory_bytes(output) >= MAX_RUN_BYTES: reason="RUN_OUTPUT_LIMIT"
                elif directory_bytes(RAW) >= MAX_RAW: reason="TOTAL_RAW_LIMIT"
                if reason:
                    stop_process(p)
                    break
                time.sleep(0.1)
            if not reason and directory_bytes(output) >= MAX_RUN_BYTES: reason="RUN_OUTPUT_LIMIT_AT_EXIT"
            if not reason and directory_bytes(RAW) >= MAX_RAW: reason="TOTAL_RAW_LIMIT_AT_EXIT"
            if not reason and time.monotonic()-timer >= MAX_SECONDS: reason="WALL_LIMIT_AT_EXIT"
            if p.returncode == 0 and not reason: validate_output(output)
    except Exception as exc:
        error = f"{type(exc).__name__}: {exc}"
        if p: stop_process(p)
    finally:
        lock.unlink()
    files = {f.name:{"sha256":sha(f),"bytes":f.stat().st_size} for f in sorted(output.glob("*")) if f.is_file()}
    receipt = {"status":"COMPLETED" if p and p.returncode==0 and not reason and not error else "FAILED", "classification":"EXPLORATORY", "run_id":card["run_id"], "started_at":started, "finished_at":now(), "runtime_wall_s":time.monotonic()-timer, "return_code":p.returncode if p else None,"sumo_pid":p.pid if p else None,"stop_reason":reason,"failure":error,"card_sha256":approved_hash,"release_sha256":sha(release_path),"command":[str(SUMO),"-c",str(Path(card["package"])/"scenario.sumocfg")],"output_manifest":files,"output_bytes":sum(v["bytes"] for v in files.values())}
    if output.exists(): write_json(output/"execution_receipt.json",receipt)
    else: write_json(Path(card["package"])/"failed_execution_receipt.json",receipt)
    return receipt


def main():
    p=argparse.ArgumentParser(description=__doc__)
    sub=p.add_subparsers(dest="mode",required=True)
    prepare_p=sub.add_parser("prepare")
    for field in ("run-id","plan"): prepare_p.add_argument("--"+field,required=True)
    for field in ("q-main","q-ramp","seed"): prepare_p.add_argument("--"+field,type=int,required=True)
    for mode in ("preflight","launch"):
        a=sub.add_parser(mode)
        a.add_argument("--card",required=True)
        a.add_argument("--approved-card-sha256",required=True)
        a.add_argument("--release",required=mode=="launch")
    a=p.parse_args()
    if a.mode=="prepare": result=prepare(a.run_id,a.q_main,a.q_ramp,a.seed,a.plan)
    elif a.mode=="preflight":
        result=preflight(a.card,a.approved_card_sha256,a.release)
        result={"status":"PREFLIGHT_PASS_NO_PROCESS_STARTED","run_id":result["run_id"]}
    else: result=launch(a.card,a.approved_card_sha256,a.release)
    print(json.dumps(result,indent=2,sort_keys=True))
    return int(result.get("status")=="FAILED")


if __name__=="__main__": raise SystemExit(main())

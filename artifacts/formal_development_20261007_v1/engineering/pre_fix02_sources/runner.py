"""Independent bounded development launcher. Preparation never starts SUMO.

Launch requires an exact-card independent release supplied by the primary
agent. Historic input/raw files and the original V15 source remain immutable.
"""
from __future__ import annotations
import argparse
from dataclasses import asdict
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import shutil
import signal
import subprocess
import sys
import time
import xml.etree.ElementTree as ET
from queue_protection import QueueParameters

ROOT = Path(__file__).resolve().parents[2]
BASE = ROOT / "artifacts/formal_development_20261007_v1"
INPUTS = BASE / "inputs"
RECEIPTS = BASE / "receipts"
RAW = ROOT / "data/raw/formal_development_20261007_v1"
LEGACY = ROOT / "artifacts/stage6_boundary_search_20261002_v1/inputs"
CONTRACT = BASE / "engineering/PARAMETER_CONTRACT.json"
SUMO = Path("/Library/Frameworks/EclipseSUMO.framework/Versions/1.26.0/EclipseSUMO/bin/sumo")
PYTHON = ROOT / ".venv/bin/python"
NETWORK = ROOT / "artifacts/stage6_baseline_localization_20260921_v1/LOC_M3350_S17/engineering/build_attempts/TV_BUILD01/network.net.xml"
SUMO_SHA = "3bd1eaa3b167fb527ac33b154dfb57b41b9a40d5bc3e26246489824dd7977179"
NETWORK_SHA = "887c232483f0c68dc024334ff5997250d7d36299ab2744bdcf49d5a314c700ca"
RESOURCES = {"wall_limit_s":180, "startup_limit_s":60, "run_limit_bytes":300_000_000,
             "new_raw_limit_bytes":4_000_000_000, "minimum_free_bytes":5_000_000_000}
FEEDBACK = dict(target_pct=11.0,gain_veh_h_per_pct=70.0,
                minimum_veh_h=300.0,maximum_veh_h=900.0,initial_veh_h=900.0)
SOURCE_FILES = tuple(Path(__file__).parent / name for name in
                    ("runner.py","v15_worker.py","control.py","queue_protection.py","test_offline.py"))
IMMUTABLE_SOURCES = (ROOT / "src/stage6_safe_actuator_v10.py",
                    ROOT / "scripts/stage6/standard_metering_20261003/control.py",
                    ROOT / "scripts/stage6/standard_metering_20261003/runner.py")


def sha(path):
    h=hashlib.sha256()
    with Path(path).open("rb") as f:
        for b in iter(lambda:f.read(1<<20),b""): h.update(b)
    return h.hexdigest()


def now(): return datetime.now(timezone.utc).isoformat()


def exclusive(path, value):
    Path(path).parent.mkdir(parents=True,exist_ok=True)
    with Path(path).open("x") as f: json.dump(value,f,indent=2,sort_keys=True); f.write("\n")


def tree_bytes(path):
    return sum(p.stat().st_size for p in Path(path).rglob("*") if p.is_file()) if Path(path).exists() else 0


def prepare(ramp,seed,treatment,attempt=1):
    if ramp not in (750,900) or seed not in (17,23,42) or treatment not in ("OPEN","T1","T2") or attempt<1:
        raise ValueError("outside authorized development scope")
    if not CONTRACT.is_file(): raise ValueError("prospective parameter contract missing")
    parent=LEGACY/f"M3600_R{ramp}_S{seed}"; old=json.loads((parent/"card.json").read_text())
    run_id=f"DEV_M3600_R{ramp}_S{seed}_{treatment}_A{attempt:02}"
    package=INPUTS/run_id; output=RAW/run_id/"outputs"
    if package.exists() or output.parent.exists(): raise FileExistsError(run_id)
    package.mkdir(parents=True,exist_ok=False)
    shutil.copyfile(parent/"demand.rou.xml",package/"demand.rou.xml")
    for name in ("scenario.add.xml","scenario.sumocfg"):
        xml=ET.parse(parent/name)
        if name=="scenario.add.xml":
            for node in xml.getroot().iter():
                for key in ("file","dest"):
                    if key in node.attrib: node.set(key,str(output/Path(node.get(key)).name))
        else:
            xml.find("./input/route-files").set("value",str(package/"demand.rou.xml"))
            xml.find("./input/additional-files").set("value",str(package/"scenario.add.xml"))
            for node in xml.findall("./output/*")+xml.findall("./report/*"):
                if node.get("value","").startswith("/"): node.set("value",str(output/Path(node.get("value")).name))
        ET.indent(xml); xml.write(package/name,encoding="utf-8",xml_declaration=True)
    baseline=ROOT/f"data/raw/stage6_boundary_search_20261002_v1/M3600_R{ramp}_S{seed}/outputs"
    card={"schema_version":1,"classification":"DEVELOPMENT","status":"PREPARED_NOT_RELEASED",
          "run_id":run_id,"ramp_veh_h":ramp,"main_veh_h":3600,"seed":seed,
          "treatment":treatment,"mode":"NOOP" if treatment=="OPEN" else "ALINEA",
          "attempt":attempt,"package":str(package),"output":str(output),"counts":old["counts"],
          "base_output":str(baseline),"legacy_card":str(parent/"card.json"),
          "legacy_card_sha256":sha(parent/"card.json"),"baseline_receipt_sha256":sha(baseline/"execution_receipt.json"),
          "input_sha256":{n:sha(package/n) for n in ("demand.rou.xml","scenario.add.xml","scenario.sumocfg")},
          "source_sha256":{str(p):sha(p) for p in SOURCE_FILES+IMMUTABLE_SOURCES},
          "contract_sha256":sha(CONTRACT),"network_sha256":sha(NETWORK),"sumo_sha256":sha(SUMO),
          "python_executable":str(PYTHON),"feedback":FEEDBACK,"queue_protection":asdict(QueueParameters()),
          "startup_deadline_s":RESOURCES["startup_limit_s"],
          "resources":RESOURCES,"horizon_s":4200,"meter_start_s":600,
          "meter_controlled_link":{"storage_length_m":204.49,"via":":ramp_mid_0_0"},
          "matching":"complete same legacy request; no realized-departure substitution",
          "observation_timing":"queue pre-step t; command held [t,t+1); crossing bracket after step t+1"}
    exclusive(package/"card.json",card)
    return {"status":"PREPARED_NO_SIMULATION","card":str(package/"card.json"),"sha256":sha(package/"card.json")}


def preflight(card_path,release_path=None):
    card_path=Path(card_path).resolve(); c=json.loads(card_path.read_text())
    if c["ramp_veh_h"] not in (750,900) or c["seed"] not in (17,23,42) or c["treatment"] not in ("OPEN","T1","T2"):
        raise ValueError("scope mismatch")
    if c["feedback"]!=FEEDBACK or c["queue_protection"]!=asdict(QueueParameters()) or c["resources"]!=RESOURCES:
        raise ValueError("parameter drift")
    from v15_worker import validate_worker_card
    validate_worker_card(c)
    if c["sumo_sha256"]!=SUMO_SHA or sha(SUMO)!=SUMO_SHA or c["network_sha256"]!=NETWORK_SHA or sha(NETWORK)!=NETWORK_SHA:
        raise ValueError("binary/network drift")
    if sha(CONTRACT)!=c["contract_sha256"]: raise ValueError("contract drift")
    for p,h in c["source_sha256"].items():
        if sha(p)!=h: raise ValueError("source drift: "+p)
    if sha(Path(__file__).parent/"control.py")!=sha(IMMUTABLE_SOURCES[1]): raise ValueError("V15 feedback/pulse changed")
    for n,h in c["input_sha256"].items():
        if sha(Path(c["package"])/n)!=h: raise ValueError("input drift")
    if sha(c["legacy_card"])!=c["legacy_card_sha256"]: raise ValueError("legacy card drift")
    if sha(Path(c["base_output"])/"execution_receipt.json")!=c["baseline_receipt_sha256"]: raise ValueError("baseline receipt drift")
    parent=Path(c["legacy_card"]).parent
    if sha(parent/"demand.rou.xml")!=c["input_sha256"]["demand.rou.xml"]: raise ValueError("request mismatch")
    cfg=ET.parse(Path(c["package"])/"scenario.sumocfg").getroot()
    if cfg.find("./time/end").get("value")!="4200" or cfg.find("./time/step-length").get("value")!="1": raise ValueError("time drift")
    if cfg.find("./input/net-file").get("value")!=str(NETWORK): raise ValueError("network reference drift")
    if cfg.find("./random_number/seed").get("value")!=str(c["seed"]): raise ValueError("seed drift")
    if tree_bytes(RAW)>=RESOURCES["new_raw_limit_bytes"] or shutil.disk_usage(ROOT).free<RESOURCES["minimum_free_bytes"]:
        raise ValueError("resource reserve gate")
    if release_path:
        r=json.loads(Path(release_path).read_text())
        if r.get("status")!="PASS_FOR_DEVELOPMENT_EXECUTION" or r.get("cards",{}).get(c["run_id"])!=sha(card_path) or r.get("contract_sha256")!=c["contract_sha256"]:
            raise ValueError("independent exact-card release missing/mismatch")
    return c


def worker(card_path):
    # No SUMO import/start occurs in preparation, preflight or offline tests.
    import v15_worker
    v15_worker.worker(card_path)


def launch(card_path,release_path):
    c=preflight(card_path,release_path); output=Path(c["output"])
    if output.parent.exists(): raise FileExistsError("immutable attempt already exists")
    INPUTS.mkdir(parents=True,exist_ok=True); lock=INPUTS/"launch.lock"
    fd=os.open(lock,os.O_CREAT|os.O_EXCL|os.O_WRONLY,0o644); os.close(fd)
    child=None; reason=None; failure=None; begun=now(); clock=time.monotonic()
    try:
        preflight(card_path,release_path)
        exclusive(INPUTS/"reservations"/(c["run_id"]+".json"),{"card_sha256":sha(card_path),"release_sha256":sha(release_path),"reserved_at":begun})
        output.mkdir(parents=True,exist_ok=False)
        with (output/"worker_stdout.log").open("x") as out,(output/"worker_stderr.log").open("x") as err:
            child=subprocess.Popen([str(PYTHON),str(Path(__file__).resolve()),"worker","--card",str(card_path)],stdout=out,stderr=err,start_new_session=True,cwd=ROOT)
            while child.poll() is None:
                if time.monotonic()-clock>=RESOURCES["wall_limit_s"]: reason="WALL_LIMIT"
                elif tree_bytes(output)>=RESOURCES["run_limit_bytes"]: reason="RUN_BYTES_LIMIT"
                elif tree_bytes(RAW)>=RESOURCES["new_raw_limit_bytes"]: reason="NEW_RAW_LIMIT"
                elif shutil.disk_usage(ROOT).free<RESOURCES["minimum_free_bytes"]: reason="FREE_RESERVE_LIMIT"
                if reason:
                    os.killpg(child.pid,signal.SIGTERM)
                    try: child.wait(timeout=3)
                    except subprocess.TimeoutExpired: os.killpg(child.pid,signal.SIGKILL); child.wait(timeout=3)
                    break
                time.sleep(.2)
            if not reason and child.returncode!=0: reason="WORKER_FAILED"
            if not reason:
                if time.monotonic()-clock>=RESOURCES["wall_limit_s"]: reason="WALL_LIMIT_AT_EXIT"
                elif tree_bytes(output)>=RESOURCES["run_limit_bytes"]: reason="RUN_BYTES_LIMIT_AT_EXIT"
                elif tree_bytes(RAW)>=RESOURCES["new_raw_limit_bytes"]: reason="NEW_RAW_LIMIT_AT_EXIT"
                elif shutil.disk_usage(ROOT).free<RESOURCES["minimum_free_bytes"]: reason="FREE_RESERVE_LIMIT_AT_EXIT"
    except Exception as e:
        failure=f"{type(e).__name__}: {e}"
        if child is not None and child.poll() is None:
            os.killpg(child.pid,signal.SIGTERM)
            try: child.wait(timeout=3)
            except subprocess.TimeoutExpired: os.killpg(child.pid,signal.SIGKILL); child.wait(timeout=3)
    finally: lock.unlink()
    files={p.name:{"bytes":p.stat().st_size,"sha256":sha(p)} for p in sorted(output.glob("*")) if p.is_file()}
    receipt={"run_id":c["run_id"],"classification":"DEVELOPMENT","treatment":c["treatment"],
             "status":"COMPLETED" if child is not None and child.returncode==0 and not reason and not failure else "FAILED",
             "started_at":begun,"finished_at":now(),"wall_s":time.monotonic()-clock,
             "return_code":child.returncode if child else None,"stop_reason":reason,"failure":failure,
             "card_sha256":sha(card_path),"release_sha256":sha(release_path),"output_manifest":files,
             "output_bytes":sum(v["bytes"] for v in files.values()),"new_raw_bytes":tree_bytes(RAW),
             "purpose":"OPEN_NEUTRALITY_BASELINE" if c["treatment"]=="OPEN" else "DEVELOPMENT_COMPARISON",
             "attempt":c["attempt"],"ramp_veh_h":c["ramp_veh_h"],"seed":c["seed"]}
    exclusive((output if output.exists() else Path(c["package"]))/"execution_receipt.json",receipt)
    exclusive(RECEIPTS/(c["run_id"]+".json"),receipt)
    return receipt


def main():
    p=argparse.ArgumentParser(description=__doc__); p.add_argument("action",choices=("prepare","preflight","launch","worker"))
    p.add_argument("--ramp",type=int);p.add_argument("--seed",type=int);p.add_argument("--treatment",choices=("OPEN","T1","T2"));p.add_argument("--attempt",type=int,default=1)
    p.add_argument("--card");p.add_argument("--release");a=p.parse_args()
    if a.action=="prepare": result=prepare(a.ramp,a.seed,a.treatment,a.attempt)
    elif a.action=="preflight": result={"status":"STATIC_PREFLIGHT_PASS_NO_SIMULATION","run_id":preflight(a.card)["run_id"]}
    elif a.action=="launch":
        if not a.release: p.error("launch requires independent --release")
        result=launch(a.card,a.release)
    else: worker(a.card);result={"status":"WORKER_COMPLETED"}
    print(json.dumps(result,indent=2,sort_keys=True));return int(result.get("status")=="FAILED")


if __name__=="__main__": raise SystemExit(main())

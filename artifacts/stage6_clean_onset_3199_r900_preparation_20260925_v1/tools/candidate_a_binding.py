"""Fail-closed verifier for CLEAN3199 Candidate A demand, provenance and staging."""
from __future__ import annotations
import hashlib, json, os
from decimal import Decimal
from pathlib import Path
import xml.etree.ElementTree as ET

RUN_ID = "CLEAN3199_A_R900_DELAYED_S17"
OUTPUT_REL = "data/raw/stage6_clean_onset_3199_ux0_20260925_v1/CLEAN3199_A_R900_DELAYED_S17/outputs"
NETWORK_REL = "artifacts/stage6_baseline_localization_20260921_v1/LOC_M3350_S17/engineering/build_attempts/TV_BUILD01/network.net.xml"
CONTROL_DEMAND_REL = "scripts/stage6/minimal3199/prepared_rev3/control/demand.rou.xml"
R900_SOURCE_REL = "artifacts/stage6_minimal3350_e1_r900_preparation_20260925_rev20/inputs/treatment/r900_vehicle_source.rou.xml"
PLAN_REL = "artifacts/stage6_clean_onset_witness_test_plan_20260925_v1/CLEAN_ONSET_WITNESS_TEST.md"
ADOPTION_REL = "artifacts/stage6_clean_onset_witness_test_plan_20260925_v1/ADOPTION_RECEIPT.json"
R720_RECEIPT_REL = "data/processed/stage6_clean_onset_3199_r720_exposure_baseline_20260925_v1/SUMMARY_METHOD_RECEIPT.json"

def sha(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()

def check_hash(repo: Path, rel: str, expected: str, label: str) -> Path:
    p = (repo / rel).resolve(strict=True)
    if not p.is_file() or sha(p) != expected:
        raise ValueError(f"bound source hash mismatch:{label}")
    return p

def parse(path: Path):
    root = ET.parse(path).getroot()
    return root, root.findall("vehicle")

def validate_card(card: dict, package_root: Path, repo: Path) -> dict:
    if (card.get("run_id") != RUN_ID or card.get("pair_id") != "PAIR_3199_S17"
        or card.get("qMain_veh_per_h") != 3199.2 or card.get("R_veh_per_h") != 900
        or card.get("R_window_s") != "[540,1500)" or card.get("seed") != 17
        or card.get("U") != 0 or card.get("X") != 0 or card.get("TLS_program") != "A_OPEN"):
        raise ValueError("scientific condition mismatch")
    if card.get("card_status") in {"DRAFT_NOT_AUTHORIZED","PRELAUNCH_READY_AWAITING_AUTHORIZATION"}:
        if card.get("execution_authorized") is not False:
            raise ValueError("unapproved card execution flag mismatch")
    elif card.get("card_status") == "FINAL_AUTHORIZED_FOR_ONE_START":
        auth=card.get("authorization_record", {})
        if (card.get("execution_authorized") is not True or card.get("approval_required") is not False
                or auth.get("run_id") != RUN_ID or auth.get("max_starts") != 1
                or auth.get("technical_retries") != 0
                or auth.get("wallclock_stop_trigger_s") != 90
                or auth.get("output_size_stop_trigger_bytes_decimal") != 75000000
                or auth.get("output_polling_interval_ms") != 100
                or auth.get("polling_overshoot_accepted") is not True):
            raise ValueError("final authorization/resource contract mismatch")
    else:
        raise ValueError("unsupported card status")
    plan_hash=card.get("design_sha256")
    if card.get("witness_contract") != {"path":PLAN_REL,"sha256":plan_hash}:
        raise ValueError("adopted CLEAN_ONSET plan is not bound as contract")
    check_hash(repo, PLAN_REL, plan_hash, "CLEAN_ONSET plan")
    adoption=card.get("adopted_plan_binding",{})
    if adoption.get("decision_id") != "D-009":
        raise ValueError("D-009 adoption missing")
    check_hash(repo, ADOPTION_REL, adoption.get("adoption_receipt_sha256"), "D-009 adoption")
    gate=card.get("existing_control_gate",{})
    if gate.get("required_disposition")!="LOW_R_BACKGROUND_ACCEPTABLE" or gate.get("legacy_high_mobility_rescreen_required") is not False:
        raise ValueError("control eligibility or no-rescreen boundary unclear")
    if card.get("treatment_release_gate")!="CLEAN_ONSET_WITNESS_TEST_D009_CANDIDATE_A_ONLY":
        raise ValueError("release gate mismatch")

    expected={"sumocfg":"inputs/treatment/scenario.sumocfg","demand":"inputs/treatment/demand.rou.xml","additional":"inputs/treatment/scenario.add.xml","output_roles":"inputs/treatment/output_roles.json","network":NETWORK_REL}
    if card.get("inputs")!=expected: raise ValueError("input path mapping mismatch")
    paths={k:(package_root/v).resolve(strict=True) if v.startswith("inputs/") else (repo/v).resolve(strict=True) for k,v in expected.items()}
    for k,p in paths.items():
        if not p.is_file() or sha(p)!=card.get("input_sha256",{}).get(k): raise ValueError(f"input hash mismatch:{k}")

    manifest_path=package_root/"INPUT_MANIFEST.json"
    manifest=json.loads(manifest_path.read_text())
    if card.get("input_manifest_sha256")!=sha(manifest_path): raise ValueError("manifest hash mismatch")
    if manifest.get("input_sha256")!=card.get("input_sha256") or manifest.get("inputs")!=card.get("inputs"):
        raise ValueError("card/manifest input binding mismatch")
    for rel,digest in manifest.get("source_hashes",{}).items(): check_hash(repo,rel,digest,"manifest:"+rel)

    control=card["matched_control_binding"]
    control_path=check_hash(repo,CONTROL_DEMAND_REL,control["control_demand_sha256"],"control demand")
    for key in ("card_path","data_review_path","scientific_review_path","output_manifest_path"):
        check_hash(repo,control[key],control[key.replace("_path","_sha256")],"control:"+key)
    baseline=card["r720_exposure_comparator"]
    check_hash(repo,R720_RECEIPT_REL,baseline["data_receipt_sha256"],"R720 baseline")
    for key in ("extractor_path","csv_path"):
        check_hash(repo,baseline[key],baseline[key.replace("_path","_sha256")],"R720 "+key)
    if baseline.get("unique_R_ids_by_cutoff_inclusive")!={"1440":167,"1500":183}:
        raise ValueError("fixed R720 comparator counts mismatch")

    cr,cv=parse(control_path); tr,tv=parse(paths["demand"])
    cids=[v.get("id") for v in cv]; tids=[v.get("id") for v in tv]
    if len(cids)!=len(set(cids)) or len(tids)!=len(set(tids)): raise ValueError("duplicate IDs")
    if len(cv)!=1333 or len(tv)!=1573: raise ValueError("vehicle total mismatch")
    if any(not v.get("id","").startswith("M_flow.") for v in cv): raise ValueError("control non-M identity")
    if any(not (v.get("id","").startswith("M_flow.") or v.get("id","").startswith("R_flow.")) for v in tv): raise ValueError("unknown treatment identity")
    cm={v.get("id"):v for v in cv}; tm={v.get("id"):v for v in tv if v.get("id","").startswith("M_flow.")}
    if len(cm)!=1333 or cm.keys()!=tm.keys(): raise ValueError("M ID set mismatch")
    for vid in cm:
        if cm[vid].attrib!=tm[vid].attrib: raise ValueError(f"M full attribute mismatch:{vid}")
        ms=Decimal(cm[vid].get("depart"))*1000
        if ms!=ms.to_integral_value(): raise ValueError(f"M noninteger-ms depart:{vid}")
    r0=[v for v in cv if v.get("id","").startswith("R_flow.")]
    rt=[v for v in tv if v.get("id","").startswith("R_flow.")]
    if r0 or len(rt)!=240 or {v.get("id") for v in rt}!={f"R_flow.{i}" for i in range(240)}: raise ValueError("R-only delta mismatch")
    _,rsource=parse(check_hash(repo,R900_SOURCE_REL,manifest["source_hashes"][R900_SOURCE_REL],"R900 source"))
    sm={v.get("id"):v for v in rsource}; rm={v.get("id"):v for v in rt}
    if len(sm)!=240 or sm.keys()!=rm.keys(): raise ValueError("R source identity mismatch")
    for vid in sm:
        if sm[vid].attrib!=rm[vid].attrib: raise ValueError(f"R source attr mismatch:{vid}")
        dep=Decimal(rm[vid].get("depart"))*1000
        idx=int(vid.split(".")[-1])
        if dep!=dep.to_integral_value() or int(dep)!=540000+4000*idx: raise ValueError(f"R schedule mismatch:{vid}")
    if any(v.get("id","").startswith(("U_flow.","X_flow.")) for v in cv+tv): raise ValueError("U/X not zero")
    order=[(Decimal(v.get("depart"))*1000,v.get("id")) for v in tv]
    if any(t!=t.to_integral_value() for t,_ in order) or order!=sorted(order): raise ValueError("global input order mismatch")

    output=repo/OUTPUT_REL
    if output.exists() or output.parent.exists(): raise ValueError("output target or parent exists")
    cfg=ET.parse(paths["sumocfg"]).getroot()
    cin={e.tag:e.get("value") for e in cfg.findall("./input/*")}
    if cin.get("net-file")!=str(paths["network"]) or cin.get("route-files")!=str(paths["demand"]) or cin.get("additional-files")!=str(paths["additional"]):
        raise ValueError("sumocfg source references mismatch")
    role_data=json.loads(paths["output_roles"].read_text())
    roles=role_data.get("required_xml_roles",[])
    if len(roles)!=18 or role_data.get("required_role_count")!=18: raise ValueError("role count mismatch")
    role_paths={Path(r["path"]).resolve(strict=False) for r in roles}
    if len(role_paths)!=18 or any(not p.is_relative_to(output.resolve(strict=False)) for p in role_paths): raise ValueError("role paths not closed")
    dest=[]
    for elem in list(cfg.findall("./output/*"))+list(cfg.findall("./report/*")):
        val=elem.get("value")
        if val and (elem.tag.endswith("-output") or elem.tag in {"log","error-log"}): dest.append(Path(val).resolve(strict=False))
    for node in ET.parse(paths["additional"]).getroot():
        for attr in ("file","dest"):
            val=node.get(attr)
            if val: dest.append(Path(val).resolve(strict=False))
    expected_logs={output.resolve(strict=False)/"sumo.log",output.resolve(strict=False)/"sumo_error.log"}
    if len(dest)!=20 or set(dest)!=(role_paths|expected_logs) or any(not p.is_relative_to(output.resolve(strict=False)) for p in dest):
        raise ValueError("sumocfg/additional/role nested destination mismatch")
    for source in (paths["sumocfg"],paths["additional"]):
        text=source.read_text()
        if "stage6_minimal3199_existence_20260924" in text or "rev14" in text.lower(): raise ValueError("stale revision reference")

    stage=card.get("staged_inputs",{})
    cfg_bytes=paths["sumocfg"].read_bytes(); add_bytes=paths["additional"].read_bytes()
    old_add=str(paths["additional"]).encode(); new_add=str(output/"scenario_control.add.xml").encode()
    if cfg_bytes.count(old_add)!=1: raise ValueError("staged additional replacement count mismatch")
    staged_cfg=cfg_bytes.replace(old_add,new_add)
    if (stage.get("sumocfg",{}).get("bytes")!=len(staged_cfg) or stage.get("sumocfg",{}).get("sha256")!=hashlib.sha256(staged_cfg).hexdigest()
        or stage.get("additional",{}).get("bytes")!=len(add_bytes) or stage.get("additional",{}).get("sha256")!=hashlib.sha256(add_bytes).hexdigest()):
        raise ValueError("staged bytes/hash mismatch")
    return {"status":"PASS","M_count":1333,"M_full_attr_exact":True,"R_count":240,"R_source_full_attr_exact":True,"R_schedule":"540000+4000*i ms","U_zero":True,"X_zero":True,"global_order":"integer_ms_then_id","r720_baseline":{"t1440":167,"t1500":183},"roles":18,"nested_paths_closed":True,"staged_hashes_bound":True,"output_absent":True}

#!/usr/bin/env python3
"""Bind the exact candidate card/runtime/runner; preparation only."""
import hashlib, json, shutil
from pathlib import Path

ROOT=Path(__file__).resolve().parents[3]
PKG=ROOT/"artifacts/stage6_clean_onset_3199_r900_preparation_20260925_v1"
RID="CLEAN3199_A_R900_DELAYED_S17"
RUNNER=PKG/"r02_single_start/runner.py"
RUNNER_SOURCE=ROOT/"artifacts/stage6_ramp_induced_validation_20260922_v1/r02_single_start/runner.py"
CARD=PKG/f"{RID}_CARD_PRELAUNCH_READY_NOT_AUTHORIZED_REV2.json"
RUNTIME=PKG/"runtime_binding.json"

def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def write(p,obj): p.parent.mkdir(parents=True,exist_ok=True); p.write_text(json.dumps(obj,indent=2,sort_keys=True)+"\n")

def main():
    shutil.copy2(RUNNER_SOURCE, RUNNER)
    source=RUNNER.read_text()
    bind = '''
# Candidate A is deliberately prelaunch-only. It cannot be launched until a
# separately authorized, reviewed FINAL card is created under a new revision.
CLEAN_ONSET_A_ID = "CLEAN3199_A_R900_DELAYED_S17"
CLEAN_ONSET_A_BINDING = {
    "package_id": "stage6_clean_onset_3199_r900_preparation_20260925_v1",
    "card_path": "artifacts/stage6_clean_onset_3199_r900_preparation_20260925_v1/CLEAN3199_A_R900_DELAYED_S17_CARD_PRELAUNCH_READY_NOT_AUTHORIZED_REV2.json",
    "output_root": "data/raw/stage6_clean_onset_3199_ux0_20260925_v1",
    "output_directory": "data/raw/stage6_clean_onset_3199_ux0_20260925_v1/CLEAN3199_A_R900_DELAYED_S17/outputs",
    "consumption_directory": "artifacts/stage6_clean_onset_3199_r900_preparation_20260925_v1/consumption",
    "runtime_binding_path": "artifacts/stage6_clean_onset_3199_r900_preparation_20260925_v1/runtime_binding.json",
    "output_role_source": "artifacts/stage6_clean_onset_3199_r900_preparation_20260925_v1/inputs/treatment/output_roles.json",
    "request_schema": "r02-start-v2",
    "authorized_wallclock_s": 90,
    "authorized_output_bytes": 75000000,
    "kind": "PAIR_RUN",
}
SUPPORTED_RUN_BINDINGS[CLEAN_ONSET_A_ID] = CLEAN_ONSET_A_BINDING
PRELAUNCH_ONLY_BINDINGS[CLEAN_ONSET_A_ID] = CLEAN_ONSET_A_BINDING
'''
    source=source.replace('\n\ndef _run_binding(', '\n'+bind+'\n\ndef _run_binding(', 1)
    source=source.replace('return run_id in MINIMAL3199_RETRY_BINDINGS or run_id in MINIMAL3350_V2_RUN_IDS',
                          'return run_id in MINIMAL3199_RETRY_BINDINGS or run_id in MINIMAL3350_V2_RUN_IDS or run_id == CLEAN_ONSET_A_ID', 1)
    old_v2='''        binding = (MINIMAL3199_RETRY_BINDINGS[run_id] if run_id in MINIMAL3199_RETRY_BINDINGS
                   else MINIMAL3350_CONTROL_BINDING)'''
    new_v2='''        binding = (MINIMAL3199_RETRY_BINDINGS[run_id] if run_id in MINIMAL3199_RETRY_BINDINGS
                   else MINIMAL3350_CONTROL_BINDING if run_id in MINIMAL3350_V2_RUN_IDS
                   else SUPPORTED_RUN_BINDINGS[run_id])'''
    if old_v2 not in source:
        raise SystemExit("v2 START request run-binding selector not found")
    source=source.replace(old_v2,new_v2,1)
    hook = '''
    if card.get("run_id") == CLEAN_ONSET_A_ID:
        try:
            adapter_path = package_root / "tools/candidate_a_binding.py"
            adapter_binding = card.get("candidate_binding_adapter", {})
            if (adapter_binding.get("path") != "artifacts/stage6_clean_onset_3199_r900_preparation_20260925_v1/tools/candidate_a_binding.py"
                    or adapter_binding.get("sha256") != sha256_file(adapter_path)):
                raise ValueError("candidate adapter hash binding mismatch")
            adapter_spec = importlib.util.spec_from_file_location("clean_onset_candidate_a_binding", adapter_path)
            if adapter_spec is None or adapter_spec.loader is None:
                raise ImportError("Candidate A binding adapter unavailable")
            adapter = importlib.util.module_from_spec(adapter_spec)
            adapter_spec.loader.exec_module(adapter)
            adapter.validate_card(card, package_root, repo)
        except (ImportError, OSError, ValueError, KeyError) as exc:
            raise GateError(f"CLEAN_ONSET_CANDIDATE_A_BINDING_FAILED:{exc}") from exc
'''
    source=source.replace('\n    return card, resolved\n\n\ndef _write_exclusive', '\n'+hook+'\n    return card, resolved\n\n\ndef _write_exclusive', 1)
    source=source.replace('''        expected_keys = {''','''        expected_keys = {''',1)
    old_check='''    if is_prelaunch_only or is_final_treatment:
        contract = card.get("witness_contract")
        if (not isinstance(contract, dict)
                or contract.get("path") != STAGE6_WITNESS_CONTRACT_PATH
                or contract.get("sha256") != STAGE6_WITNESS_CONTRACT_SHA256):
            raise GateError("WITNESS_CONTRACT_BINDING_MISMATCH")
        contract_path = _resolve_repo_file(repo, STAGE6_WITNESS_CONTRACT_PATH)
        if sha256_file(contract_path) != STAGE6_WITNESS_CONTRACT_SHA256:
            raise GateError("WITNESS_CONTRACT_HASH_MISMATCH")
        if card.get("treatment_release_gate") != "STAGE6_EXPLORATORY_RAMP_INDUCED_WITNESS_CONTRACT_ONLY" or card.get("LOW_R_BACKGROUND_ACCEPTABLE_required_for_release") is not False:
            raise GateError("OLD_LOW_R_GATE_MUST_NOT_RELEASE_TREATMENT")
'''
    new_check='''    if is_prelaunch_only or is_final_treatment:
        contract = card.get("witness_contract")
        if card.get("run_id") == CLEAN_ONSET_A_ID:
            contract_path_rel = "artifacts/stage6_clean_onset_witness_test_plan_20260925_v1/CLEAN_ONSET_WITNESS_TEST.md"
            contract_hash = card.get("design_sha256")
            expected_gate = "CLEAN_ONSET_WITNESS_TEST_D009_CANDIDATE_A_ONLY"
            expected_low_r_gate = True
        else:
            contract_path_rel = STAGE6_WITNESS_CONTRACT_PATH
            contract_hash = STAGE6_WITNESS_CONTRACT_SHA256
            expected_gate = "STAGE6_EXPLORATORY_RAMP_INDUCED_WITNESS_CONTRACT_ONLY"
            expected_low_r_gate = False
        if (not isinstance(contract, dict)
                or contract.get("path") != contract_path_rel
                or contract.get("sha256") != contract_hash):
            raise GateError("WITNESS_CONTRACT_BINDING_MISMATCH")
        contract_path = _resolve_repo_file(repo, contract_path_rel)
        if sha256_file(contract_path) != contract_hash:
            raise GateError("WITNESS_CONTRACT_HASH_MISMATCH")
        if (card.get("treatment_release_gate") != expected_gate
                or card.get("LOW_R_BACKGROUND_ACCEPTABLE_required_for_release") is not expected_low_r_gate):
            raise GateError("TREATMENT_RELEASE_GATE_BINDING_MISMATCH")
        if card.get("run_id") == CLEAN_ONSET_A_ID:
            control_gate = card.get("existing_control_gate")
            if (not isinstance(control_gate, dict)
                    or control_gate.get("required_disposition") != "LOW_R_BACKGROUND_ACCEPTABLE"
                    or control_gate.get("legacy_high_mobility_rescreen_required") is not False):
                raise GateError("CLEAN_ONSET_CONTROL_GATE_BINDING_MISMATCH")
'''
    if old_check not in source:
        raise SystemExit("generic witness contract validation block not found")
    source=source.replace(old_check,new_check,1)
    old_stage='''        else:
            output.mkdir(parents=True, exist_ok=False)
            cfg = files["sumocfg"].read_text(encoding="utf-8")
            add = files["additional"].read_text(encoding="utf-8")
            add_bytes = add.replace(OUTPUT_TOKEN, str(output)).encode("utf-8")
            cfg_bytes = cfg.replace(OUTPUT_TOKEN, str(output)).replace(str(files["additional"]), str(add_copy)).encode("utf-8")
'''
    new_stage='''        elif card.get("run_id") == CLEAN_ONSET_A_ID:
            output.mkdir(parents=True, exist_ok=False)
            cfg = files["sumocfg"].read_text(encoding="utf-8")
            add = files["additional"].read_text(encoding="utf-8")
            add_bytes = add.replace(OUTPUT_TOKEN, str(output)).encode("utf-8")
            cfg_bytes = cfg.replace(OUTPUT_TOKEN, str(output)).replace(str(files["additional"]), str(add_copy)).encode("utf-8")
            preview = card.get("staged_inputs", {})
            expected_cfg = preview.get("sumocfg", {})
            expected_add = preview.get("additional", {})
            if (len(cfg_bytes) != expected_cfg.get("bytes")
                    or hashlib.sha256(cfg_bytes).hexdigest() != expected_cfg.get("sha256")
                    or len(add_bytes) != expected_add.get("bytes")
                    or hashlib.sha256(add_bytes).hexdigest() != expected_add.get("sha256")):
                raise GateError("CLEAN_ONSET_STAGED_BYTES_HASH_MISMATCH")
        else:
            output.mkdir(parents=True, exist_ok=False)
            cfg = files["sumocfg"].read_text(encoding="utf-8")
            add = files["additional"].read_text(encoding="utf-8")
            add_bytes = add.replace(OUTPUT_TOKEN, str(output)).encode("utf-8")
            cfg_bytes = cfg.replace(OUTPUT_TOKEN, str(output)).replace(str(files["additional"]), str(add_copy)).encode("utf-8")
'''
    if old_stage not in source:
        raise SystemExit("generic launch staging branch not found")
    source=source.replace(old_stage,new_stage,1)
    RUNNER.write_text(source)
    runner_hash=sha(RUNNER)
    manifest=json.loads((PKG/"INPUT_MANIFEST.json").read_text())
    runtime_source=json.loads((ROOT/"scripts/stage6/minimal3199/prepared_rev3/control/runtime_binding.json").read_text())
    runtime_source["guardian_runner_sha256"]=runner_hash
    runtime_source["max_runtime_s"]=90
    runtime_source["max_output_bytes"]=75_000_000
    runtime_source["resource_proposal"]={
      "basis":"Candidate-specific proposal based on observed minimal3199 R720 3.165857 s / 21,151,489 total output bytes, minimal3350 R720 24.638514 s / 22,012,984 bytes, and minimal3350 R900 2.879677 s / 22,841,112 bytes; set to 90 s (about 3.65x the slowest observed comparable run) and 75,000,000 bytes (about 3.28x the largest observed comparable output) to allow variability with margin.",
      "enforcement":"100ms_polled_stop_trigger_with_possible_overshoot_not_hard_quota",
      "output_size_stop_limit_bytes_decimal":75_000_000,"overshoot_accepted":True,
      "poll_interval_s":0.1,"scope":RID,"status":"PROPOSED_NOT_AUTHORIZED","wallclock_stop_limit_s":90
    }
    write(RUNTIME,runtime_source)
    mhash=sha(PKG/"INPUT_MANIFEST.json")
    plan_path="artifacts/stage6_clean_onset_witness_test_plan_20260925_v1/CLEAN_ONSET_WITNESS_TEST.md"
    plan_hash=sha(ROOT/plan_path)
    witness_path="docs/methodology/STAGE6_EXPLORATORY_RAMP_INDUCED_WITNESS_CONTRACT.md"
    witness_hash=sha(ROOT/witness_path)
    card={
      "schema_version":"1","card_revision":2,"card_status":"PRELAUNCH_READY_AWAITING_AUTHORIZATION",
      "run_id":RID,"execution_attempt_id":RID,"pair_id":"PAIR_3199_S17",
      "condition":"A_OPEN_R900_DELAYED_CLEAN_ONSET_CANDIDATE_A",
      "design_plan":plan_path,"design_sha256":plan_hash,
      "witness_contract":{"path":plan_path,"sha256":plan_hash},
      "adopted_plan_binding":{"decision_id":"D-009","adoption_receipt_path":"artifacts/stage6_clean_onset_witness_test_plan_20260925_v1/ADOPTION_RECEIPT.json","adoption_receipt_sha256":sha(ROOT/"artifacts/stage6_clean_onset_witness_test_plan_20260925_v1/ADOPTION_RECEIPT.json")},
      "qMain_veh_per_h":3199.2,"R_veh_per_h":900,"R_window_s":"[540,1500)","seed":17,"U":0,"X":0,"TLS_program":"A_OPEN",
      "horizon_s":2700,"step_s":1,
      "class_counts":{"M":{"planned_count":1333,"status":"BOUND"},"R":{"planned_count":240,"status":"BOUND"},"U":{"planned_count":0,"status":"PASS_ZERO"},"X":{"planned_count":0,"status":"PASS_ZERO"}},
      "matched_control_binding":{
        "run_id":"MINIMAL3199_CTRL_S17_TECH_RETRY2",
        "card_path":"artifacts/stage6_minimal3199_ctrl_technical_retry2_20260924_v1/MINIMAL3199_CTRL_S17_TECH_RETRY2_CARD_FINAL.json",
        "card_sha256":sha(ROOT/"artifacts/stage6_minimal3199_ctrl_technical_retry2_20260924_v1/MINIMAL3199_CTRL_S17_TECH_RETRY2_CARD_FINAL.json"),
        "data_review_path":"artifacts/stage6_minimal3199_ctrl_technical_retry2_20260924_v1/DATA_LIFECYCLE_POSTRUN_REVIEW.json",
        "data_review_sha256":sha(ROOT/"artifacts/stage6_minimal3199_ctrl_technical_retry2_20260924_v1/DATA_LIFECYCLE_POSTRUN_REVIEW.json"),
        "scientific_review_path":"artifacts/stage6_minimal3199_ctrl_technical_retry2_20260924_v1/SCIENTIFIC_POSTRUN_REVIEW.json",
        "scientific_review_sha256":sha(ROOT/"artifacts/stage6_minimal3199_ctrl_technical_retry2_20260924_v1/SCIENTIFIC_POSTRUN_REVIEW.json"),
        "output_manifest_path":"data/raw/stage6_minimal3199_existence_20260924_v3/MINIMAL3199_CTRL_S17_TECH_RETRY2/outputs/output_manifest.json",
        "output_manifest_sha256":sha(ROOT/"data/raw/stage6_minimal3199_existence_20260924_v3/MINIMAL3199_CTRL_S17_TECH_RETRY2/outputs/output_manifest.json"),
        "control_demand_path":"scripts/stage6/minimal3199/prepared_rev3/control/demand.rou.xml",
        "control_demand_sha256":sha(ROOT/"scripts/stage6/minimal3199/prepared_rev3/control/demand.rou.xml"),
        "disposition":"LOW_R_BACKGROUND_ACCEPTABLE_WITHIN_MINIMAL_UX0_MODULE_NOT_CLEAN_NORMAL_BASELINE"
      },
      "r720_exposure_comparator":{
        "run_id":"MINIMAL3199_R720_DELAYED_S17_UX0_ATTEMPT1",
        "data_receipt_path":"data/processed/stage6_clean_onset_3199_r720_exposure_baseline_20260925_v1/SUMMARY_METHOD_RECEIPT.json",
        "data_receipt_sha256":sha(ROOT/"data/processed/stage6_clean_onset_3199_r720_exposure_baseline_20260925_v1/SUMMARY_METHOD_RECEIPT.json"),
        "extractor_path":"data/processed/stage6_clean_onset_3199_r720_exposure_baseline_20260925_v1/extract_through_lane_entries.py",
        "extractor_sha256":sha(ROOT/"data/processed/stage6_clean_onset_3199_r720_exposure_baseline_20260925_v1/extract_through_lane_entries.py"),
        "csv_path":"data/processed/stage6_clean_onset_3199_r720_exposure_baseline_20260925_v1/r720_first_through_lane_entries.csv",
        "csv_sha256":sha(ROOT/"data/processed/stage6_clean_onset_3199_r720_exposure_baseline_20260925_v1/r720_first_through_lane_entries.csv"),
        "method":"first FCD observation on mapped freeway through-lane whitelist, count each R identity once at earliest frame, inclusive cutoffs; exclude merge_section_0 auxiliary lane",
        "unique_R_ids_by_cutoff_inclusive":{"1440":167,"1500":183}
      },
      "actual_merge_exposure_comparison":{
        "must_report_unique_first_through_lane_R_ids_by_cutoff_inclusive":["1440","1500"],
        "baseline_counts":{"1440":167,"1500":183},
        "method_source":"r720_exposure_comparator.data_receipt_path",
        "no_substitution_or_method_change_after_treatment":True
      },
      "existing_control_gate":{"required_disposition":"LOW_R_BACKGROUND_ACCEPTABLE","source_review_path":"artifacts/stage6_minimal3199_ctrl_technical_retry2_20260924_v1/SCIENTIFIC_POSTRUN_REVIEW.json","legacy_high_mobility_rescreen_required":False,"control_requalification_required":False,"scope":"Previously reviewed minimal U=X=0 module only."},
      "legacy_high_mobility_rescreen_required":False,
      "inputs":manifest["inputs"],"input_sha256":manifest["input_sha256"],
      "input_manifest":"INPUT_MANIFEST.json","input_manifest_sha256":mhash,
      "output_directory":manifest["output_directory"],
      "output_role_source":{"path":"artifacts/stage6_clean_onset_3199_r900_preparation_20260925_v1/inputs/treatment/output_roles.json","sha256":manifest["input_sha256"]["output_roles"]},
      "runner":{"path":"artifacts/stage6_clean_onset_3199_r900_preparation_20260925_v1/r02_single_start/runner.py","sha256":runner_hash,"status":"CANDIDATE_A_EXACT_RUN_BINDING_DRAFT_ONLY"},
      "candidate_binding_adapter":{"path":"artifacts/stage6_clean_onset_3199_r900_preparation_20260925_v1/tools/candidate_a_binding.py","sha256":sha(PKG/"tools/candidate_a_binding.py")},
      "runner_binding":{"run_id":RID,"package_id":"stage6_clean_onset_3199_r900_preparation_20260925_v1","card_path":CARD.relative_to(ROOT).as_posix(),"output_directory":manifest["output_directory"],"consumption_directory":"artifacts/stage6_clean_onset_3199_r900_preparation_20260925_v1/consumption","kind":"PAIR_RUN"},
      "runtime_binding_path":"artifacts/stage6_clean_onset_3199_r900_preparation_20260925_v1/runtime_binding.json","runtime_binding_sha256":sha(RUNTIME),"runtime_binding":runtime_source,
      "resource_limits":{"scope":RID,"runtime_s":90,"storage_bytes":75_000_000,"status":"PROPOSED_NOT_AUTHORIZED","polling_interval_ms":100,"polling_overshoot_accepted":True},
      "execution_authorized":False,"approval_required":True,"max_starts":1,"technical_retries":0,"progression_allowed":False,
      "prelaunch_disposition":"PASS_ALL_PRELAUNCH_REVIEWS_AWAITING_SEPARATE_USER_LAUNCH_AUTHORIZATION",
      "LOW_R_BACKGROUND_ACCEPTABLE_required_for_release":True,
      "treatment_release_gate":"CLEAN_ONSET_WITNESS_TEST_D009_CANDIDATE_A_ONLY",
      "required_event_timeline_markers":["R_demand_activation","first_scheduled_R_departure","first_actual_R_departure","first_R_arrival_near_merge","first_meaningful_merge_exposure","first_M_deterioration","State1_onset"],
      "scope_prohibitions":["No R1080 or Candidate B preparation","No other qMain/qRamp, seed23, B/C, or formal run","No classifier, threshold, geometry, vehicle behavior, formal protocol changes"],
      "run_command":None
    }
    # Deterministic launch-copy preview from the exact source bytes. The runner
    # only rewrites the additional-files pointer to the output-local copy.
    cfg_src=PKG/"inputs/treatment/scenario.sumocfg"
    add_src=PKG/"inputs/treatment/scenario.add.xml"
    cfg_bytes=cfg_src.read_bytes()
    old_add=str(add_src.resolve()).encode("utf-8")
    new_add=(ROOT/manifest["output_directory"]/"scenario_control.add.xml").resolve(strict=False)
    if cfg_bytes.count(old_add)!=1:
        raise SystemExit("expected exactly one staged additional-files path occurrence")
    staged_cfg=cfg_bytes.replace(old_add,str(new_add).encode("utf-8"))
    add_bytes=add_src.read_bytes()
    card["staged_inputs"]={
      "transformation":"UTF-8 byte-preserving sumocfg replacement: package scenario.add.xml absolute path -> output-local scenario_control.add.xml; additional XML copied byte-identically",
      "sumocfg":{"bytes":len(staged_cfg),"sha256":hashlib.sha256(staged_cfg).hexdigest()},
      "additional":{"bytes":len(add_bytes),"sha256":hashlib.sha256(add_bytes).hexdigest()},
      "output_local_additional_path":str(new_add)
    }
    write(CARD,card)
    print(json.dumps({"card":CARD.relative_to(ROOT).as_posix(),"card_sha256":sha(CARD),"runner_sha256":runner_hash,"runtime_binding_sha256":sha(RUNTIME),"status":card["card_status"],"launch_authorized":False},indent=2))
if __name__=="__main__": main()

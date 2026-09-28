#!/usr/bin/env python3
"""Prepare the exact, review-gated minimal3350 delayed-R720 treatment package."""
from __future__ import annotations

import hashlib
import importlib.util
import json
from pathlib import Path
import shutil
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[3]
PACKAGE_REL = "artifacts/stage6_minimal3350_r720_treatment_preparation_20260924_rev7"
OUTPUT_REL = "data/raw/stage6_minimal3350_ux0_20260924_v15/MINIMAL3350_R720_DELAYED_S17/outputs"
RUN_ID = "MINIMAL3350_R720_DELAYED_S17"
CONTROL_RUN_ID = "MINIMAL3350_CTRL_S17"
RUNNER_SOURCE_REL = "artifacts/stage6_minimal3350_r720_treatment_preparation_20260924_rev3/r02_single_start/runner.py"
RUNNER_REL = f"{PACKAGE_REL}/r02_single_start/runner.py"
ADAPTER_REL = "scripts/stage6/minimal3350/minimal3350_treatment_adapter.py"
CONTROL_PACKAGE_REL = "artifacts/stage6_minimal3350_control_preparation_20260924_rev8"
CONTROL_OUTPUT_REL = "data/raw/stage6_minimal3350_ux0_20260924_v8/MINIMAL3350_CTRL_S17/outputs"
R_SOURCE_REL = "scripts/stage6/minimal3199/prepared_rev3/treatment/demand.rou.xml"
PLAN_REL = "artifacts/stage6_minimal_ramp_induced_breakdown_existence_test_20260924_v1/PLAN.md"
CONTRACT_REL = "docs/methodology/STAGE6_EXPLORATORY_RAMP_INDUCED_WITNESS_CONTRACT.md"
METHOD_REL = "docs/methodology/FREEWAY_PROTECTABLE_STATE_EXPLORATORY_DEFINITION.md"
NETWORK_REL = "artifacts/stage6_baseline_localization_20260921_v1/LOC_M3350_S17/engineering/build_attempts/TV_BUILD01/network.net.xml"


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def dump(path: Path, value: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("xb") as stream:
        stream.write((json.dumps(value, indent=2, sort_keys=True) + "\n").encode())


def main() -> int:
    repo = ROOT.resolve(strict=True)
    package = repo / PACKAGE_REL
    output = repo / OUTPUT_REL
    output_parent = output.parent
    control_package = repo / CONTROL_PACKAGE_REL
    control_card_path = control_package / f"{CONTROL_RUN_ID}_S17_CARD_FINAL.json"
    if not control_card_path.exists():
        control_card_path = control_package / "MINIMAL3350_CTRL_S17_CARD_FINAL.json"
    control_card = json.loads(control_card_path.read_text(encoding="utf-8"))
    control_data_path = control_package / "DATA_POSTRUN_REVIEW.json"
    control_science_path = control_package / "SCIENTIFIC_POSTRUN_REVIEW.json"
    control_manifest_path = repo / CONTROL_OUTPUT_REL / "output_manifest.json"
    control_demand = control_package / "inputs/control/demand.rou.xml"
    control_cfg = control_package / "inputs/control/scenario.sumocfg"
    control_add = control_package / "inputs/control/scenario.add.xml"
    control_roles = control_package / "inputs/control/output_roles.json"
    common_path = control_package / "COMMON_M_DEMAND_MANIFEST.json"
    runner_source_path = repo / RUNNER_SOURCE_REL
    adapter_path = repo / ADAPTER_REL
    r_source = repo / R_SOURCE_REL
    required = [control_card_path, control_data_path, control_science_path, control_manifest_path,
                control_demand, control_cfg, control_add, control_roles, common_path, runner_source_path,
                adapter_path, runner_source_path, r_source, repo / PLAN_REL, repo / CONTRACT_REL, repo / METHOD_REL,
                repo / NETWORK_REL]
    for path in required:
        if not path.is_file():
            raise FileNotFoundError(path)
    control_science = json.loads(control_science_path.read_text(encoding="utf-8"))
    if (control_science.get("run_id") != CONTROL_RUN_ID
            or control_science.get("disposition") != "LOW_R_BACKGROUND_ACCEPTABLE"
            or control_science.get("card_sha256") != sha(control_card_path)):
        raise ValueError("conditional control scientific release is absent or mismatched")
    if package.exists() or output.exists() or output_parent.exists():
        raise FileExistsError("refusing package/output reuse")

    adapter_spec = importlib.util.spec_from_file_location("minimal3350_treatment_adapter_prep", adapter_path)
    if adapter_spec is None or adapter_spec.loader is None:
        raise ImportError("treatment adapter unavailable")
    adapter = importlib.util.module_from_spec(adapter_spec)
    adapter_spec.loader.exec_module(adapter)
    package.mkdir(parents=True)
    runner_path = repo / RUNNER_REL
    runner_path.parent.mkdir(parents=True, exist_ok=True)
    runner_text = runner_source_path.read_text(encoding="utf-8")
    runner_text = runner_text.replace(
        'stage6_minimal3350_r720_treatment_preparation_20260924_rev3',
        'stage6_minimal3350_r720_treatment_preparation_20260924_rev7')
    runner_text = runner_text.replace(
        'data/raw/stage6_minimal3350_ux0_20260924_v11',
        'data/raw/stage6_minimal3350_ux0_20260924_v15')
    old_release_check = 'if card.get("treatment_release_gate") != "STAGE6_EXPLORATORY_RAMP_INDUCED_WITNESS_CONTRACT_ONLY" or card.get("LOW_R_BACKGROUND_ACCEPTABLE_required_for_release") is not False:'
    new_release_check = ('if (card.get("treatment_release_gate") != "STAGE6_EXPLORATORY_RAMP_INDUCED_WITNESS_CONTRACT_ONLY"\n'
                         '                or card.get("legacy_clean_high_mobility_screen_required_for_release") is not False\n'
                         '                or card.get("stage6_exploratory_control_disposition_required_for_release") is not True\n'
                         '                or card.get("stage6_exploratory_control_disposition_required") != "LOW_R_BACKGROUND_ACCEPTABLE"):')
    if old_release_check not in runner_text:
        raise ValueError("REV3 runner release-gate source did not match expected bytes")
    runner_text = runner_text.replace(old_release_check, new_release_check)
    old_treatment_gate = '    if is_minimal3350_treatment:\n        if (card.get("qMain_veh_per_h") != 3350.4'
    new_treatment_gate = '    if is_minimal3350_treatment:\n        validate_minimal3350_control_release_binding(repo, card)\n        if (card.get("qMain_veh_per_h") != 3350.4'
    if old_treatment_gate not in runner_text:
        raise ValueError("REV3 runner treatment gate insertion point missing")
    runner_text = runner_text.replace(old_treatment_gate, new_treatment_gate)
    helper_anchor = 'def minimal3350_review_receipt_valid(role: str, receipt: Any, run_id: str,'
    helper = '''def validate_minimal3350_control_release_receipts(card: dict[str, Any],
        binding: dict[str, Any], control_card: dict[str, Any], data_review: dict[str, Any],
        science_review: dict[str, Any], output_manifest: dict[str, Any], observed_hashes: dict[str, str]) -> None:
    """Pure fail-closed check for the exact user-required matched-control release."""
    if (not isinstance(card, dict) or not isinstance(binding, dict)
            or not isinstance(control_card, dict) or not isinstance(data_review, dict)
            or not isinstance(science_review, dict) or not isinstance(output_manifest, dict)
            or not isinstance(observed_hashes, dict)):
        raise GateError("MINIMAL3350_MATCHED_CONTROL_RECEIPT_MISSING_OR_MALFORMED")
    if (card.get("legacy_clean_high_mobility_screen_required_for_release") is not False
            or card.get("stage6_exploratory_control_disposition_required_for_release") is not True
            or card.get("stage6_exploratory_control_disposition_required") != "LOW_R_BACKGROUND_ACCEPTABLE"):
        raise GateError("MINIMAL3350_EXPLORATORY_CONTROL_PREREQUISITE_CARD_MISMATCH")
    if binding.get("run_id") != MINIMAL3350_CTRL_RUN_ID:
        raise GateError("MINIMAL3350_MATCHED_CONTROL_BINDING_MISSING_OR_WRONG_RUN")
    expected_card_hash = binding.get("card_sha256")
    expected_science_hash = binding.get("scientific_review_sha256")
    expected_data_hash = binding.get("data_review_sha256")
    expected_manifest_hash = binding.get("output_manifest_sha256")
    findings = science_review.get("findings")
    zero_findings = (isinstance(findings, dict)
                     and all(type(findings.get(k)) is int and findings[k] == 0
                             for k in ("blocker", "major", "required_minor")))
    if (observed_hashes.get("card") != expected_card_hash
            or control_card.get("run_id") != MINIMAL3350_CTRL_RUN_ID
            or control_card.get("qMain_veh_per_h") != 3350.4
            or control_card.get("R_veh_per_h") != 0
            or control_card.get("U") != 0 or control_card.get("X") != 0
            or control_card.get("seed") != 17
            or observed_hashes.get("data_review") != expected_data_hash
            or data_review.get("schema") != "stage6_minimal3350_control_data_postrun_review_v1"
            or data_review.get("run_id") != MINIMAL3350_CTRL_RUN_ID
            or data_review.get("card_sha256") != expected_card_hash
            or data_review.get("disposition") != "PASS_DATA_LIFECYCLE"
            or data_review.get("data_side_control_category") != "LOW_R_BACKGROUND_ACCEPTABLE"
            or observed_hashes.get("science_review") != expected_science_hash
            or science_review.get("schema") != "stage6_minimal3350_scientific_postrun_review_v1"
            or science_review.get("run_id") != MINIMAL3350_CTRL_RUN_ID
            or science_review.get("card_sha256") != expected_card_hash
            or science_review.get("disposition") != "LOW_R_BACKGROUND_ACCEPTABLE"
            or not zero_findings
            or observed_hashes.get("output_manifest") != expected_manifest_hash
            or output_manifest.get("run_id") != MINIMAL3350_CTRL_RUN_ID):
        raise GateError("MINIMAL3350_MATCHED_CONTROL_ACCEPTANCE_BINDING_MISMATCH")


def validate_minimal3350_control_release_binding(repo: Path, card: dict[str, Any]) -> None:
    """Require the exact reviewed LOW_R control before accepting this treatment card."""
    binding = card.get("matched_control_binding")
    if not isinstance(binding, dict) or binding.get("run_id") != MINIMAL3350_CTRL_RUN_ID:
        raise GateError("MINIMAL3350_MATCHED_CONTROL_BINDING_MISSING_OR_WRONG_RUN")
    try:
        card_path = _resolve_repo_file(repo, binding["card_path"])
        data_path = _resolve_repo_file(repo, binding["data_review_path"])
        science_path = _resolve_repo_file(repo, binding["scientific_review_path"])
        manifest_path = _resolve_repo_file(repo, binding["output_manifest_path"])
        control_card = load_json(card_path)
        data_review = load_json(data_path)
        science_review = load_json(science_path)
        output_manifest = load_json(manifest_path)
    except (KeyError, OSError, GateError, ValueError) as exc:
        raise GateError(f"MINIMAL3350_MATCHED_CONTROL_RECEIPT_UNREADABLE:{exc}") from exc
    validate_minimal3350_control_release_receipts(card, binding, control_card, data_review,
        science_review, output_manifest, {"card": sha256_file(card_path),
            "data_review": sha256_file(data_path), "science_review": sha256_file(science_path),
            "output_manifest": sha256_file(manifest_path)})


'''
    if helper_anchor not in runner_text:
        raise ValueError("REV3 runner review helper insertion point missing")
    runner_text = runner_text.replace(helper_anchor, helper + helper_anchor)
    receipt_call = 'passed = minimal3350_review_receipt_valid(role, value, run_id, approved_card_sha256)'
    receipt_call_new = 'passed = minimal3350_review_receipt_valid(role, value, run_id, approved_card_sha256, repo)'
    if receipt_call not in runner_text:
        raise ValueError("REV3 review-gate receipt call did not match")
    runner_text = runner_text.replace(receipt_call, receipt_call_new)
    receipt_signature = ('def minimal3350_review_receipt_valid(role: str, receipt: Any, run_id: str,\n'
                         '                                     approved_card_sha256: str) -> bool:')
    receipt_signature_new = ('def minimal3350_review_receipt_valid(role: str, receipt: Any, run_id: str,\n'
                             '                                     approved_card_sha256: str, repo: Path | None = None) -> bool:')
    if receipt_signature not in runner_text:
        raise ValueError("REV3 review validator signature did not match")
    runner_text = runner_text.replace(receipt_signature, receipt_signature_new)
    receipt_guard = ('    if not isinstance(receipt, dict) or receipt.get("run_id") != run_id:\n'
                     '        return False\n'
                     '    if receipt.get("card_sha256") != approved_card_sha256:\n'
                     '        return False\n')
    receipt_guard_new = ('    if run_id == MINIMAL3350_TREATMENT_RUN_ID and role == "data_provenance":\n'
                         '        return minimal3350_treatment_data_receipt_valid(repo, receipt, run_id, approved_card_sha256)\n'
                         '    if not isinstance(receipt, dict) or receipt.get("run_id") != run_id:\n'
                         '        return False\n'
                         '    if receipt.get("card_sha256") != approved_card_sha256:\n'
                         '        return False\n')
    if receipt_guard not in runner_text:
        raise ValueError("REV3 review validator guard did not match")
    data_receipt_helper = '''def minimal3350_treatment_data_receipt_valid(repo: Path | None, receipt: Any,
        run_id: str, approved_card_sha256: str) -> bool:
    """Validate the declared nested-binding data receipt against current REV7 bytes."""
    if repo is None or not isinstance(receipt, dict):
        return False
    findings = receipt.get("findings")
    if (receipt.get("schema") != "stage6_minimal3350_treatment_data_provenance_prelaunch_review_v1"
            or receipt.get("status") != "PASS_DATA_PROVENANCE_PRELAUNCH"
            or receipt.get("run_id") != run_id
            or receipt.get("package_id") != MINIMAL3350_TREATMENT_PACKAGE_ID
            or not isinstance(findings, dict)
            or any(type(findings.get(k)) is not int or findings[k] != 0
                   for k in ("blocker", "major", "required_minor"))):
        return False
    b = receipt.get("bindings")
    if not isinstance(b, dict):
        return False
    package = Path("artifacts") / MINIMAL3350_TREATMENT_PACKAGE_ID
    expected_paths = {
        "card_path": MINIMAL3350_TREATMENT_BINDING["card_path"],
        "input_manifest_sha256": repo / package / "INPUT_MANIFEST.json",
        "runtime_binding_sha256": repo / MINIMAL3350_TREATMENT_BINDING["runtime_binding_path"],
        "runner_sha256": repo / package / "r02_single_start/runner.py",
        "start_request_sha256": repo / package / "START_REQUEST.json",
        "start_request_receipt_sha256": repo / package / "START_REQUEST_RECEIPT.json",
        "provenance_receipt_sha256": repo / package / "PROVENANCE_RECEIPT.json",
    }
    card_path = repo / MINIMAL3350_TREATMENT_BINDING["card_path"]
    try:
        current_card = load_json(card_path)
        if (b.get("card_path") != MINIMAL3350_TREATMENT_BINDING["card_path"]
                or b.get("card_sha256") != approved_card_sha256
                or sha256_file(card_path) != approved_card_sha256):
            return False
        for key, path in expected_paths.items():
            if key == "card_path":
                continue
            if not path.is_file() or b.get(key) != sha256_file(path):
                return False
        if (b.get("design_plan_sha256") != current_card.get("design_sha256")
                or b.get("witness_contract_sha256") != current_card.get("witness_contract", {}).get("sha256")
                or b.get("adapter_sha256") != sha256_file(repo / "scripts/stage6/minimal3350/minimal3350_treatment_adapter.py")):
            return False
        control = current_card.get("matched_control_binding", {})
        gate = receipt.get("matched_control_gate", {})
        if (gate.get("run_id") != control.get("run_id")
                or gate.get("card_sha256") != control.get("card_sha256")
                or gate.get("data_review_sha256") != control.get("data_review_sha256")
                or gate.get("data_review_disposition") != "PASS_DATA_LIFECYCLE"
                or gate.get("data_side_control_category") != "LOW_R_BACKGROUND_ACCEPTABLE"
                or gate.get("scientific_review_sha256") != control.get("scientific_review_sha256")
                or gate.get("scientific_disposition") != "LOW_R_BACKGROUND_ACCEPTABLE"
                or gate.get("scientific_findings") != {"blocker": 0, "major": 0, "required_minor": 0}
                or gate.get("output_manifest_sha256") != control.get("output_manifest_sha256")
                or gate.get("result") != "PASS_EXACT_BOUND_CONTROL_RECEIPTS"):
            return False
        condition = receipt.get("condition_check", {})
        if (condition.get("qMain_veh_per_h") != 3350.4 or condition.get("seed") != 17
                or condition.get("R_veh_per_h") != 720 or condition.get("R_window_s") != "[540,1500)"
                or condition.get("U") != 0 or condition.get("X") != 0
                or condition.get("legacy_clean_high_mobility_screen_required_for_release") is not False
                or condition.get("stage6_exploratory_control_disposition_required_for_release") is not True
                or condition.get("required_exploratory_control_disposition") != "LOW_R_BACKGROUND_ACCEPTABLE"):
            return False
    except (GateError, OSError, KeyError, TypeError):
        return False
    return True


'''
    receipt_function = 'def minimal3350_review_receipt_valid(role: str, receipt: Any, run_id: str,'
    if receipt_function not in runner_text:
        raise ValueError("REV3 review validator insertion point missing")
    runner_text = runner_text.replace(receipt_function, data_receipt_helper + receipt_function)
    runner_text = runner_text.replace(receipt_guard, receipt_guard_new)
    runner_path.write_text(runner_text, encoding="utf-8")
    inputs = package / "inputs/treatment"
    inputs.mkdir(parents=True)
    demand = inputs / "demand.rou.xml"
    demand_summary = adapter.materialize_treatment_demand(control_demand, r_source, demand)

    old_output = str((repo / CONTROL_OUTPUT_REL).resolve())
    new_output = str((repo / OUTPUT_REL).resolve())
    config = control_cfg.read_text(encoding="utf-8")
    old_demand = str(control_demand.resolve())
    old_additional = str(control_add.resolve())
    config = config.replace(old_demand, str(demand.resolve()))
    config = config.replace(old_additional, str((inputs / "scenario.add.xml").resolve()))
    config = config.replace(old_output, new_output).replace(CONTROL_RUN_ID, RUN_ID)
    additional = control_add.read_text(encoding="utf-8").replace(old_output, new_output).replace(CONTROL_RUN_ID, RUN_ID)
    if any(stale in config + additional for stale in (old_output, CONTROL_RUN_ID, "stage6_minimal3350_ux0_20260924_v8")):
        raise ValueError("stale control output path or run ID remains in treatment config")
    (inputs / "scenario.sumocfg").write_text(config, encoding="utf-8")
    (inputs / "scenario.add.xml").write_text(additional, encoding="utf-8")
    roles = json.loads(control_roles.read_text(encoding="utf-8"))
    for item in roles["required_xml_roles"]:
        item["path"] = item["path"].replace(old_output, new_output).replace(CONTROL_RUN_ID, RUN_ID)
    roles_path = inputs / "output_roles.json"
    dump(roles_path, roles)
    role_paths = [Path(item["path"]).resolve(strict=False) for item in roles["required_xml_roles"]]
    if len(role_paths) != 18 or len(set(role_paths)) != 18 or any(p.parent != output.resolve(strict=False) for p in role_paths):
        raise ValueError("treatment output-role binding invalid")
    for xml_path in (inputs / "scenario.sumocfg", inputs / "scenario.add.xml"):
        for element in ET.parse(xml_path).getroot().iter():
            value = element.get("value") or element.get("file") or element.get("dest")
            if value and "/outputs/" in value and Path(value).resolve(strict=False).parent != output.resolve(strict=False):
                raise ValueError(f"configured output path escaped treatment directory: {value}")

    runner_hash = sha(runner_path)
    runtime = json.loads((control_package / "runtime_binding.json").read_text(encoding="utf-8"))
    runtime["guardian_runner_sha256"] = runner_hash
    runtime["max_runtime_s"] = 90
    runtime["max_output_bytes"] = 75_000_000
    runtime["resource_proposal"] = {
        "basis": "User-authorized conditional MINIMAL3350 R720 treatment; the qMain=3350.4 control completed within its accepted contract. Treatment output size remains unobserved.",
        "enforcement": "100ms_polled_stop_trigger_with_possible_overshoot_not_hard_quota",
        "output_size_stop_limit_bytes_decimal": 75_000_000,
        "overshoot_accepted": True,
        "poll_interval_s": 0.1,
        "scope": RUN_ID,
        "status": "AUTHORIZED_FOR_THIS_RUN",
        "wallclock_stop_limit_s": 90,
    }
    runtime_path = package / "runtime_binding.json"
    dump(runtime_path, runtime)
    runtime_hash = sha(runtime_path)
    common_hash = sha(common_path)
    r_hash = sha(r_source)
    hashes = {"sumocfg": sha(inputs / "scenario.sumocfg"), "demand": sha(demand),
              "additional": sha(inputs / "scenario.add.xml"), "output_roles": sha(roles_path),
              "network": sha(repo / NETWORK_REL)}
    control_binding = {
        "run_id": CONTROL_RUN_ID,
        "card_path": str(control_card_path.relative_to(repo)),
        "card_sha256": sha(control_card_path),
        "data_review_path": str(control_data_path.relative_to(repo)),
        "data_review_sha256": sha(control_data_path),
        "scientific_review_path": str(control_science_path.relative_to(repo)),
        "scientific_review_sha256": sha(control_science_path),
        "output_manifest_path": str(control_manifest_path.relative_to(repo)),
        "output_manifest_sha256": sha(control_manifest_path),
        "demand_input_path": str(control_demand.relative_to(repo)),
        "demand_input_sha256": sha(control_demand),
    }
    plan_hash, contract_hash, method_hash = sha(repo / PLAN_REL), sha(repo / CONTRACT_REL), sha(repo / METHOD_REL)
    input_manifest = {
        "schema": "stage6_minimal3350_treatment_execution_manifest_v1",
        "package_id": PACKAGE_REL.split("/")[-1],
        "run_id": RUN_ID,
        "pair_id": "MINIMAL3350_UX0_S17",
        "arm": "treatment",
        "design_plan_sha256": plan_hash,
        "fixed_conditions": {"qMain_veh_per_h": 3350.4, "qRamp_veh_per_h": 720, "R_window_s": "[540,1500)",
                             "seed": 17, "U": 0, "X": 0, "A": "A_OPEN", "step_s": 1, "horizon_s": 2700},
        "class_counts": {"M": {"planned_count": 1396, "status": "BOUND"}, "R": {"planned_count": 192, "status": "BOUND"},
                         "U": {"planned_count": 0, "status": "PASS_ZERO"}, "X": {"planned_count": 0, "status": "PASS_ZERO"}},
        "common_m_manifest": {"path": str(common_path.relative_to(repo)), "sha256": common_hash},
        "r_vehicle_source": {"path": R_SOURCE_REL, "sha256": r_hash},
        "inputs": {"sumocfg": {"path": "inputs/treatment/scenario.sumocfg", "sha256": hashes["sumocfg"]},
                   "demand": {"path": "inputs/treatment/demand.rou.xml", "sha256": hashes["demand"]},
                   "additional": {"path": "inputs/treatment/scenario.add.xml", "sha256": hashes["additional"]},
                   "output_roles": {"path": "inputs/treatment/output_roles.json", "sha256": hashes["output_roles"]},
                   "network": {"path": NETWORK_REL, "sha256": hashes["network"]}},
        "output_directory": OUTPUT_REL,
        "runtime_binding_path": str(runtime_path.relative_to(repo)),
        "runtime_binding_sha256": runtime_hash,
        "runner_path": RUNNER_REL,
        "runner_sha256": runner_hash,
        "plan_sha256": plan_hash,
        "witness_contract_sha256": contract_hash,
        "control_binding": control_binding,
        "provenance": {"scope": "PRELAUNCH_ONLY_NO_GUARDIAN_NO_SIMULATOR", "sumo_starts": 0, "traci_starts": 0, "netconvert_starts": 0},
        "source_hashes": {"adapter": sha(adapter_path), "control_card": control_binding["card_sha256"],
                          "control_data_review": control_binding["data_review_sha256"], "control_science_review": control_binding["scientific_review_sha256"],
                          "common_m_manifest": common_hash, "r_vehicle_source": r_hash, "runner": runner_hash,
                          "network": hashes["network"], "plan": plan_hash, "witness_contract": contract_hash, "locked_method": method_hash},
    }
    manifest_path = package / "INPUT_MANIFEST.json"
    dump(manifest_path, input_manifest)
    manifest_hash = sha(manifest_path)
    card_path_rel = f"{PACKAGE_REL}/{RUN_ID}_CARD_REV1.json"
    card = {
        "schema_version": "1", "card_revision": 1, "run_id": RUN_ID, "execution_attempt_id": RUN_ID,
        "pair_id": "MINIMAL3350_UX0_S17", "condition": "A_OPEN_R720_DELAYED_TREATMENT",
        "qMain_veh_per_h": 3350.4, "R_veh_per_h": 720, "R_window_s": "[540,1500)",
        "seed": 17, "U": 0, "X": 0, "TLS_program": "A_OPEN", "horizon_s": 2700, "step_s": 1,
        "M_planned_count": 1396,
        "class_counts": input_manifest["class_counts"],
        "card_status": "FINAL_AUTHORIZED_FOR_ONE_START", "execution_authorized": True, "approval_required": False,
        "authorization_record": {
            "authorization": "USER_AUTHORIZED_CONDITIONAL_ONE_MINIMAL3350_TREATMENT_START_AFTER_CONTROL_AND_THREE_REVIEWS",
            "run_id": RUN_ID, "exact_card_path": card_path_rel, "max_starts": 1, "technical_retries": 0,
            "wallclock_stop_trigger_s": 90, "output_size_stop_trigger_bytes_decimal": 75_000_000,
            "output_polling_interval_ms": 100, "polling_overshoot_accepted": True,
            "prohibited_runs": ["R900", "R1080", "higher_qMain", "seed23", "B", "C"],
        },
        "design_plan": PLAN_REL, "design_sha256": plan_hash,
        "witness_contract": {"path": CONTRACT_REL, "sha256": contract_hash},
        "treatment_release_gate": "STAGE6_EXPLORATORY_RAMP_INDUCED_WITNESS_CONTRACT_ONLY",
        "legacy_clean_high_mobility_screen_required_for_release": False,
        "stage6_exploratory_control_disposition_required_for_release": True,
        "stage6_exploratory_control_disposition_required": "LOW_R_BACKGROUND_ACCEPTABLE",
        "required_event_timeline_markers": ["R_demand_activation", "first_scheduled_R_departure", "first_actual_R_departure",
                                            "first_R_arrival_near_merge", "first_meaningful_merge_exposure",
                                            "first_M_deterioration", "State1_onset"],
        "common_m_manifest": {"path": str(common_path.relative_to(repo)), "sha256": common_hash},
        "r_vehicle_source": {"path": R_SOURCE_REL, "sha256": r_hash},
        "matched_control_binding": control_binding,
        "input_manifest": "INPUT_MANIFEST.json", "input_manifest_sha256": manifest_hash,
        "inputs": {"sumocfg": "inputs/treatment/scenario.sumocfg", "demand": "inputs/treatment/demand.rou.xml",
                   "additional": "inputs/treatment/scenario.add.xml", "output_roles": "inputs/treatment/output_roles.json", "network": NETWORK_REL},
        "input_sha256": hashes, "output_directory": OUTPUT_REL,
        "output_role_source": {"path": f"{PACKAGE_REL}/inputs/treatment/output_roles.json", "sha256": hashes["output_roles"]},
        "runtime_binding": runtime, "runtime_binding_path": str(runtime_path.relative_to(repo)), "runtime_binding_sha256": runtime_hash,
        "runner": {"path": RUNNER_REL, "sha256": runner_hash, "status": "EXACT_MINIMAL3350_TREATMENT_RUNNER_REVIEW_GATED"},
        "runner_binding": {"package_id": PACKAGE_REL.split("/")[-1], "run_id": RUN_ID, "card_path": card_path_rel,
                           "output_directory": OUTPUT_REL, "consumption_directory": f"{PACKAGE_REL}/r02_single_start/consumption", "kind": "PAIR_RUN"},
        "resource_limits": {"runtime_s": 90, "storage_bytes": 75_000_000, "scope": RUN_ID,
                            "status": "AUTHORIZED_FOR_THIS_RUN", "polling_interval_ms": 100, "polling_overshoot_accepted": True},
        "guardian_request_binding": {"schema": "r02-start-v2", "request_path": f"{PACKAGE_REL}/START_REQUEST.json",
                                     "receipt_path": f"{PACKAGE_REL}/START_REQUEST_RECEIPT.json", "status": "PERSISTED_UNSENT"},
        "review_gate": {"required": ["engineering", "data_provenance", "scientific"],
                        "status": "PENDING_EXACT_CARD_REVIEWS", "binding_path": f"{PACKAGE_REL}/FINAL_PRELAUNCH_REVIEW_BINDING.json"},
        "prelaunch_disposition": "FINAL_CARD_READY_FOR_REVIEWS_NOT_LAUNCHABLE_UNTIL_REVIEW_BINDING_PASS",
        "max_starts": 1, "technical_retries": 0, "progression_allowed": False, "run_command": None,
        "note": "Conditional user authorization: one treatment start only after fresh exact-card engineering/data/scientific PASS reviews and final launchable preflight. No retry.",
    }
    card_path = repo / card_path_rel
    dump(card_path, card)
    card_hash = sha(card_path)

    runner_spec = importlib.util.spec_from_file_location("minimal3350_r02_treatment_prepare", runner_path)
    if runner_spec is None or runner_spec.loader is None:
        raise ImportError("R02 runner could not be loaded without process launch")
    r02 = importlib.util.module_from_spec(runner_spec)
    runner_spec.loader.exec_module(r02)
    verified, files = r02.verify_card(repo, card_path, card_hash, allow_prelaunch=False)
    output_path = files["output"]
    staged = dict(files)
    staged["sumocfg"] = output_path / "scenario_control.sumocfg"
    reservation = repo / f"{PACKAGE_REL}/r02_single_start/consumption/{RUN_ID}.json"
    request = r02.build_guardian_start_spec(staged, verified, output_path, reservation, repo, RUN_ID,
                                            card_path=card_path, approved_card_sha256=card_hash)
    r02.validate_guardian_start_request(request, repo, require_reviews=False)
    request_bytes = r02.canonical_json_bytes(request)
    request_hash = hashlib.sha256(request_bytes).hexdigest()
    (package / "START_REQUEST.json").write_bytes(request_bytes)
    request_receipt = {
        "schema_version": "1", "status": "PASS_PERSISTED_UNSENT", "dispatched": False, "run_id": RUN_ID,
        "request_schema": "r02-start-v2", "card_path": card_path_rel, "card_sha256": card_hash,
        "request_path": f"{PACKAGE_REL}/START_REQUEST.json", "request_sha256": request_hash,
        "request_bytes": len(request_bytes), "output_directory": OUTPUT_REL,
        "reservation_path": f"{PACKAGE_REL}/r02_single_start/consumption/{RUN_ID}.json",
        "max_runtime_s": 90, "max_output_bytes": 75_000_000,
    }
    dump(package / "START_REQUEST_RECEIPT.json", request_receipt)
    provenance = {
        "schema": "stage6_minimal3350_treatment_provenance_receipt_v1", "run_id": RUN_ID,
        "card_sha256": card_hash, "input_manifest_sha256": manifest_hash, "input_sha256": hashes,
        "runner_sha256": runner_hash, "runtime_binding_sha256": runtime_hash,
        "common_m_manifest_sha256": common_hash, "r_vehicle_source_sha256": r_hash,
        "start_request_sha256": request_hash,
        "start_request_receipt_sha256": sha(package / "START_REQUEST_RECEIPT.json"),
        "control_scientific_disposition": "LOW_R_BACKGROUND_ACCEPTABLE",
        "control_scientific_review_sha256": control_binding["scientific_review_sha256"],
        "output_directory": OUTPUT_REL, "output_parent_absent": True,
        "class_counts": input_manifest["class_counts"], "M_exact_common_matches": 1396,
        "treatment_only_delta": "R_flow.0..R_flow.191", "U_explicit_zero": True, "X_explicit_zero": True,
        "R_schedule_first_last_interval_ms": [540_000, 1_495_000, 5_000],
        "resource_limits": {"wallclock_s": 90, "output_bytes": 75_000_000, "poll_interval_ms": 100, "overshoot_accepted": True},
        "process_starts": {"guardian": 0, "sumo": 0, "traci": 0, "netconvert": 0},
    }
    dump(package / "PROVENANCE_RECEIPT.json", provenance)
    # Request serialization and every input are statically revalidated. Reviews are absent, so it must stay gated.
    preflight = r02.make_plan(repo, card_path, card_hash)
    if preflight.get("launchable_now") is not False or preflight.get("simulator_process_started") is not False:
        raise RuntimeError("treatment became launchable before fresh exact-card reviews")
    dump(package / "STATIC_PREFLIGHT.json", preflight)
    result = {"package": PACKAGE_REL, "run_id": RUN_ID, "card_sha256": card_hash,
              "runner_sha256": runner_hash, "runtime_binding_sha256": runtime_hash,
              "input_manifest_sha256": manifest_hash, "demand_sha256": hashes["demand"],
              "demand_bytes": demand_summary["bytes"], "M_count": demand_summary["m_count"],
              "R_count": demand_summary["r_count"], "common_m_manifest_sha256": common_hash,
              "R_source_sha256": r_hash, "start_request_sha256": request_hash,
              "preflight_status": preflight.get("status"), "launchable_now": preflight.get("launchable_now"),
              "review_gate": preflight.get("launch_review_gate", {}).get("status"),
              "output_path_exists": output.exists(), "guardian_sumo_traci_netconvert_starts": [0,0,0,0]}
    print(json.dumps(result, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

"""Static, fail-closed coverage audit for planned unchanged RI3350 outputs."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PKG = ROOT / "artifacts/stage6_ramp_induced_validation_20260922_v1"
ROLES = ROOT / "artifacts/stage6_baseline_localization_20260921_v1/LOC_M3350_S17/engineering/inputs/LOC_M3350_S17_attempt1/output_roles.json"
HIST_DATA = ROOT / "artifacts/stage6_baseline_localization_20260921_v1/LOC_M3350_S17/postrun_reviews/data_postrun_review.json"
HIST_SCI = ROOT / "artifacts/stage6_baseline_localization_20260921_v1/LOC_M3350_S17/postrun_reviews/scientific_postrun_review.json"
GATE_CONTRACT = ROOT / "artifacts/stage6_baseline_localization_20260921_v1/LOC_M3350_S17/engineering/gate_contract.json"
NETWORK_AUDIT = ROOT / "artifacts/stage6_baseline_localization_20260921_v1/LOC_M3350_S17/engineering/compiled_audit.json"
URBAN_DIAGNOSTIC = ROOT / "docs/STAGE2_TIMING_DIAGNOSTIC.md"


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def audit():
    roles = json.loads(ROLES.read_text())
    ids = {r["role"] for r in roles["required_xml_roles"]}
    required = {"fcd.xml", "lanechanges.xml", "queues.xml", "sumo_summary.xml",
                "tripinfo.xml", "vehroute.xml", "tls_states.xml",
                "ramp_storage_e2.xml", "shared_boundary_e2.xml"}
    e1 = {r["role"] for r in roles["required_xml_roles"] if r["kind"] == "E1"}
    assert required <= ids
    assert len(e1) == 9
    assert roles["lanechange_logging_enabled"] is True
    assert not any("internal" in r["role"].lower() for r in roles["required_xml_roles"])
    data_review = json.loads(HIST_DATA.read_text())
    sci_review = json.loads(HIST_SCI.read_text())
    gate_contract = json.loads(GATE_CONTRACT.read_text())
    network_audit = json.loads(NETWORK_AUDIT.read_text())
    assert data_review["gates"]["G6"].startswith("NOT_EVALUABLE")
    assert sci_review["gates"]["G6"] == "NOT_EVALUABLE_FOR_RELEASE"
    assert any("same R blocker/U victim/time/location" in str(g) for g in gate_contract["gates"])
    connector = network_audit["lanes"].get(":urban_diverge_1_0", {})
    assert float(connector.get("length", "nan")) == 113.08
    assert "113.08 m internal connection" in URBAN_DIAGNOSTIC.read_text()
    package_inputs = {
        "output_roles": {"path": str(ROLES.relative_to(ROOT)), "sha256": sha(ROLES)},
        "control_additional": {"path": "artifacts/stage6_ramp_induced_validation_20260922_v1/control_input/scenario_control.add.xml",
                               "sha256": sha(PKG / "control_input/scenario_control.add.xml")},
        "historical_data_review": {"path": str(HIST_DATA.relative_to(ROOT)), "sha256": sha(HIST_DATA)},
        "historical_scientific_review": {"path": str(HIST_SCI.relative_to(ROOT)), "sha256": sha(HIST_SCI)},
        "registered_G6_gate": {"path": str(GATE_CONTRACT.relative_to(ROOT)), "sha256": sha(GATE_CONTRACT)},
        "compiled_geometry_audit": {"path": str(NETWORK_AUDIT.relative_to(ROOT)), "sha256": sha(NETWORK_AUDIT)},
        "prior_urban_detector_scope_diagnostic": {"path": str(URBAN_DIAGNOSTIC.relative_to(ROOT)), "sha256": sha(URBAN_DIAGNOSTIC)},
    }
    return {
        "schema_version": "1",
        "scope": "PRELAUNCH_OUTPUT_COVERAGE_AUDIT_ONLY",
        "status": "PASS_COVERAGE_AUDIT_WITH_G6_LIMITATION",
        "starts": 0,
        "added_observers_or_detectors": False,
        "planned_observability": {
            "source_and_insertion": {"status": "CONDITIONAL_DETECTABLE",
                "evidence_roles": ["demand_control.rou.xml", "sumo_summary.xml", "fcd.xml", "vehroute.xml", "tripinfo.xml"],
                "limits": ["no approved numeric material-insertion cutoff", "report exact counts/delays; do not infer artifact clearance mechanically"]},
            "downstream_tailback": {"status": "CONDITIONAL_DETECTABLE",
                "evidence_roles": ["fcd.xml", "p1_main_down_20_l0.xml", "p1_main_down_20_l1.xml", "p1_main_down_200_l0.xml", "p1_main_down_200_l1.xml"],
                "limits": ["E1 flow/occupancy is not class-attributed", "coarse simultaneity remains UNKNOWN"]},
            "direct_mainline_tls": {"status": "DETECTABLE_WITH_STATIC_TOPOLOGY_CONTEXT",
                "evidence_roles": ["tls_states.xml", "network.net.xml"],
                "limits": ["does not exclude urban platoon/TLS timing effects"]},
            "geometry_or_unrelated_bottleneck": {"status": "CONDITIONAL_DETECTABLE",
                "evidence_roles": ["network.net.xml", "fcd.xml", "vehroute.xml", "lanechanges.xml"],
                "limits": ["accepted geometry is context, not automatic event-specific clearance"]},
            "ramp_internal_shared_occupancy": {"status": "PARTIAL_COVERAGE",
                "evidence_roles": ["fcd.xml", "ramp_storage_e2.xml", "shared_boundary_e2.xml", "queues.xml"],
                "limits": ["E2 covers storage and shared approach only; 113.08 m :urban_diverge_1_0 connector has no dedicated E2; FCD can provide trajectories but does not itself establish a registered queue/storage predicate"]},
            "storage_cross_or_connected_stopped_chain": {"status": "CONDITIONAL_FCD_ADJUDICATION_REQUIRED",
                "evidence_roles": ["fcd.xml", "lanechanges.xml", "network.net.xml"],
                "limits": ["no approved new numeric queue-connectivity predicate; no positive event is not evidence of absence unless coverage adequacy is established"]},
            "direct_same_identity_time_location_R_to_U_obstruction": {"status": "NOT_ESTABLISHED_BY_REGISTERED_OUTPUTS",
                "evidence_roles": ["fcd.xml", "lanechanges.xml", "tripinfo.xml", "vehroute.xml", "ramp_storage_e2.xml", "shared_boundary_e2.xml"],
                "limits": ["historical M3350 G6 remained NOT_EVALUABLE_FOR_RELEASE; strict storage_cross and linked same-R/same-U/time/location obstruction were not independently established; proximity/R-ahead of stopped U is not causal linkage; no approved obstruction threshold"]},
            "U_exposure_and_lifecycle": {"status": "DESCRIPTIVE_DETECTABLE",
                "evidence_roles": ["tripinfo.xml", "vehroute.xml", "sumo_summary.xml", "fcd.xml"],
                "limits": ["delay and unfinished counts do not prove R caused U harm without linked obstruction evidence"]},
        },
        "release_policy": {
            "unknown_g6_blocks_baseline_suitability": True,
            "unknown_g6_does_not_erase_separately_supported_mainline_mechanism": True,
            "no_positive_evidence_does_not_equal_cleared": True,
            "no_new_sensor_or_runtime_observer_authorized": True,
            "no_user_facing_claim_of_urban_safety_or_G6_clearance": True,
        },
        "historical_review_status": {"data_G6": data_review["gates"]["G6"],
                                      "scientific_G6": sci_review["gates"]["G6"]},
        "explicit_G6_evidence_boundary": {
            "registered_hard_predicate": "same R blocker/U victim/time/location plus same-U overlapping positive insertion delay or unfinished status",
            "historical_finding": "NOT_EVALUABLE_FOR_RELEASE; strict storage_cross and direct linkage not independently established",
            "internal_connector_with_no_dedicated_E2": {"lane": ":urban_diverge_1_0", "length_m": 113.08},
            "meaning": "output coverage supports conditional post-run review but cannot turn unobserved/unlinked evidence into a clearance"
        },
        "source_manifest": package_inputs,
        "limitations": ["This is a coverage/readiness conclusion, not an audit of a future RI3350 run.",
                        "R07 closes only as bounded observability specification; direct G6 remains an explicit post-run UNKNOWN unless evidence resolves it."]
    }


if __name__ == "__main__":
    out = audit()
    target = PKG / "r07_coverage_audit.json"
    target.write_text(json.dumps(out, indent=2) + "\n")
    print(json.dumps({"status": out["status"], "g6": out["release_policy"]["unknown_g6_blocks_baseline_suitability"],
                      "output": str(target.relative_to(ROOT))}, indent=2))

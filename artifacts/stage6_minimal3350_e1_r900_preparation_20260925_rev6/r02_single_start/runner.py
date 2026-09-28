#!/usr/bin/env python3
"""Fail-closed, one-attempt SUMO launcher for a supported exact run card.

The module is safe to import and its ``preflight`` command never starts a
process.  A launch consumes its one-use reservation before process creation;
any exception or unsuccessful process remains consumed and cannot be retried.
"""
from __future__ import annotations

import argparse
import hashlib
import importlib.metadata
import importlib.util
import json
import math
import os
from pathlib import Path
import platform
import re
import select
import signal
import subprocess
import sys
import time
from datetime import datetime, timezone
from typing import Any
import xml.etree.ElementTree as ET
from xml.parsers import expat


LEGACY_PACKAGE_ID = "stage6_ramp_induced_validation_20260922_v1"
REPO_ROOT = Path(__file__).resolve().parents[3]
PAIR_PACKAGE_ID = "stage6_pair_3199_s17_preparation_20260923_v1"
MINIMAL3199_PACKAGE_ID = "MINIMAL3199_UX0_S17_PREPARATION"
LEGACY_RUN_ID = "RI3350_CTRL_S17_technical_retry1"
RETRY_OF_RUN_ID = "RI3350_CTRL_S17_attempt1"
RETRY_OF_CARD_PATH = "artifacts/stage6_ramp_induced_validation_20260922_v1/control_card_FINAL_RI3350_CTRL_S17_attempt1_REV1.json"
RETRY_OF_CARD_SHA256 = "c306646c4b73ec86b243a7936e2bf5f838d4c764c37756d763e9c4c2365c97e3"
RETRY_OF_RESERVATION_PATH = "artifacts/stage6_ramp_induced_validation_20260922_v1/r02_single_start/consumption/RI3350_CTRL_S17_attempt1.json"
RETRY_OF_RESERVATION_SHA256 = "309759c8fa498cedac00ff2bc865b86432658e26552c4830912790960ead37d9"
OUTPUT_TOKEN = "__CONTROL_OUTPUT__"
REQUIRED_INPUTS = {
    "sumocfg": "control_input/scenario_control.sumocfg",
    "demand": "control_input/demand_control.rou.xml",
    "additional": "control_input/scenario_control.add.xml",
    "network": "artifacts/stage6_baseline_localization_20260921_v1/LOC_M3350_S17/engineering/build_attempts/TV_BUILD01/network.net.xml",
}
REQUIRED_RUNTIME_KEYS = {
    "binary_path", "binary_sha256", "binary_version", "version_evidence",
    "python_environment", "max_runtime_s", "max_output_bytes", "guardian_runner_sha256",
    "sumo_home", "additional_schema_path", "additional_schema_sha256"
}
REQUIRED_PYTHON_PACKAGES = ("traci", "sumolib", "sumoITScontrol")
EXPECTED_SUMO_PATH = "/Library/Frameworks/EclipseSUMO.framework/Versions/1.26.0/EclipseSUMO/bin/sumo"
EXPECTED_SUMO_SHA256 = "3bd1eaa3b167fb527ac33b154dfb57b41b9a40d5bc3e26246489824dd7977179"
EXPECTED_SUMO_VERSION = "1.26.0"
EXPECTED_SUMO_HOME = "/Library/Frameworks/EclipseSUMO.framework/Versions/1.26.0/EclipseSUMO/share/sumo"
EXPECTED_ADDITIONAL_SCHEMA = f"{EXPECTED_SUMO_HOME}/data/xsd/additional_file.xsd"
EXPECTED_ADDITIONAL_SCHEMA_SHA256 = "c755f45b68590c4313eb8123b2cd9c56e0097ade83c5f2176f35e14f25bec97e"
STAGE6_WITNESS_CONTRACT_PATH = "docs/methodology/STAGE6_EXPLORATORY_RAMP_INDUCED_WITNESS_CONTRACT.md"
STAGE6_WITNESS_CONTRACT_SHA256 = "958890a7dd017110787a85d77ebfa3e6dac2b7d862f0fd91f6bafb7cf1738d9a"
LEGACY_OUTPUT_ROLE_SOURCE = "artifacts/stage6_baseline_localization_20260921_v1/LOC_M3350_S17/engineering/inputs/LOC_M3350_S17_attempt1/output_roles.json"
PAIR_OUTPUT_ROLE_SOURCE = "artifacts/stage6_pair_3199_s17_preparation_20260923_v1/inputs/{arm}/output_roles.json"
SUPPORTED_RUN_BINDINGS = {
    LEGACY_RUN_ID: {
        "package_id": LEGACY_PACKAGE_ID,
        "card_path": "artifacts/stage6_ramp_induced_validation_20260922_v1/control_card_FINAL_RI3350_CTRL_S17_technical_retry1_REV1.json",
        "output_directory": f"artifacts/{LEGACY_PACKAGE_ID}/outputs/{LEGACY_RUN_ID}",
        "consumption_directory": f"artifacts/{LEGACY_PACKAGE_ID}/r02_single_start/consumption",
        "kind": "TECHNICAL_RETRY",
    },
    "PAIR_3199_CTRL_S17": {
        "package_id": PAIR_PACKAGE_ID,
        "card_path": f"artifacts/{PAIR_PACKAGE_ID}/PAIR_3199_CTRL_S17_CARD_DRAFT_NOT_AUTHORIZED_REV2.json",
        "output_directory": "data/raw/stage6_bounded_pair_20260923_v1/PAIR_3199_CTRL_S17/outputs",
        "consumption_directory": f"artifacts/{PAIR_PACKAGE_ID}/r02_single_start/consumption",
        "kind": "PAIR_RUN",
    },
    "PAIR_3199_R720_DELAYED_S17": {
        "package_id": PAIR_PACKAGE_ID,
        "card_path": f"artifacts/{PAIR_PACKAGE_ID}/PAIR_3199_R720_DELAYED_S17_CARD_DRAFT_NOT_AUTHORIZED_REV2.json",
        "output_directory": "data/raw/stage6_bounded_pair_20260923_v1/PAIR_3199_R720_DELAYED_S17/outputs",
        "consumption_directory": f"artifacts/{PAIR_PACKAGE_ID}/r02_single_start/consumption",
        "kind": "PAIR_RUN",
    },
}
FINAL_AUTHORIZED_BINDINGS = {
    "PAIR_3199_CTRL_S17": {
        **SUPPORTED_RUN_BINDINGS["PAIR_3199_CTRL_S17"],
        "card_path": f"artifacts/{PAIR_PACKAGE_ID}/PAIR_3199_CTRL_S17_CARD_FINAL_REV1.json",
        "runtime_binding_path": f"artifacts/{PAIR_PACKAGE_ID}/runtime_bindings/PAIR_3199_CTRL_S17_FINAL_REV1.json",
    },
    "PAIR_3199_R720_DELAYED_S17": {
        **SUPPORTED_RUN_BINDINGS["PAIR_3199_R720_DELAYED_S17"],
        "card_path": f"artifacts/{PAIR_PACKAGE_ID}/PAIR_3199_R720_DELAYED_S17_CARD_FINAL_REV1.json",
        "runtime_binding_path": f"artifacts/{PAIR_PACKAGE_ID}/runtime_bindings/PAIR_3199_R720_DELAYED_S17_FINAL_REV1.json",
    },
}
PRELAUNCH_ONLY_BINDINGS = {
    "PAIR_3199_R720_DELAYED_S17": {
        **SUPPORTED_RUN_BINDINGS["PAIR_3199_R720_DELAYED_S17"],
        "card_path": f"artifacts/{PAIR_PACKAGE_ID}/PAIR_3199_R720_DELAYED_S17_CARD_PRELAUNCH_REV2.json",
        "runtime_binding_path": f"artifacts/{PAIR_PACKAGE_ID}/runtime_bindings/PAIR_3199_R720_DELAYED_S17_PRELAUNCH_REV2.json",
    }
}
MINIMAL3199_RUN_BINDINGS = {
    "MINIMAL3199_CTRL_S17": {
        "package_id": MINIMAL3199_PACKAGE_ID,
        "package_root": "scripts/stage6/minimal3199/prepared_rev3",
        "card_path": "scripts/stage6/minimal3199/prepared_rev3/MINIMAL3199_CTRL_S17_CARD_DRAFT_NOT_AUTHORIZED_REV3.json",
        "output_root": "data/raw/stage6_minimal3199_existence_20260924_v1",
        "output_directory": "data/raw/stage6_minimal3199_existence_20260924_v1/MINIMAL3199_CTRL_S17/outputs",
        "consumption_directory": "scripts/stage6/minimal3199/consumption",
        "output_role_source": "scripts/stage6/minimal3199/prepared_rev3/control/output_roles.json",
        "arm": "control",
        "kind": "MINIMAL3199_DRAFT",
    },
    "MINIMAL3199_R720_DELAYED_S17": {
        "package_id": MINIMAL3199_PACKAGE_ID,
        "package_root": "scripts/stage6/minimal3199/prepared_rev3",
        "card_path": "scripts/stage6/minimal3199/prepared_rev3/MINIMAL3199_R720_DELAYED_S17_CARD_DRAFT_NOT_AUTHORIZED_REV3.json",
        "output_root": "data/raw/stage6_minimal3199_existence_20260924_v1",
        "output_directory": "data/raw/stage6_minimal3199_existence_20260924_v1/MINIMAL3199_R720_DELAYED_S17/outputs",
        "consumption_directory": "scripts/stage6/minimal3199/consumption",
        "output_role_source": "scripts/stage6/minimal3199/prepared_rev3/treatment/output_roles.json",
        "arm": "treatment",
        "kind": "MINIMAL3199_DRAFT",
    },
}
MINIMAL3199_FINAL_CONTROL_BINDING = {
    "package_id": "stage6_minimal3199_ctrl_execution_20260924_v1",
    "package_root": "artifacts/stage6_minimal3199_ctrl_execution_20260924_v1",
    "input_package_root": "scripts/stage6/minimal3199/prepared_rev3",
    "card_path": "artifacts/stage6_minimal3199_ctrl_execution_20260924_v1/MINIMAL3199_CTRL_S17_CARD_FINAL.json",
    "manifest_path": "artifacts/stage6_minimal3199_ctrl_execution_20260924_v1/EXECUTION_MANIFEST.json",
    "runtime_binding_path": "artifacts/stage6_minimal3199_ctrl_execution_20260924_v1/runtime_binding.json",
    "output_root": "data/raw/stage6_minimal3199_existence_20260924_v1",
    "output_directory": "data/raw/stage6_minimal3199_existence_20260924_v1/MINIMAL3199_CTRL_S17/outputs",
    "consumption_directory": "artifacts/stage6_minimal3199_ctrl_execution_20260924_v1/consumption",
    "output_role_source": "scripts/stage6/minimal3199/prepared_rev3/control/output_roles.json",
    "arm": "control",
    "kind": "MINIMAL3199_FINAL_CONTROL",
    "authorized_wallclock_s": 90,
    "authorized_output_bytes": 60_000_000,
}
MINIMAL3199_FINAL_BINDINGS = {"MINIMAL3199_CTRL_S17": MINIMAL3199_FINAL_CONTROL_BINDING}
SUPPORTED_RUN_BINDINGS["MINIMAL3199_CTRL_S17"] = MINIMAL3199_FINAL_CONTROL_BINDING
# Fresh, unauthorized technical retry preparation after the earlier control
# authorization was consumed by a pre-Guardian failure. This binding is draft
# only: _verify_minimal3199_draft accepts it only with allow_prelaunch=True.
MINIMAL3199_RETRY_RUN_ID = "MINIMAL3199_CTRL_S17_TECH_RETRY1"
MINIMAL3199_RETRY_BINDING = {
    "package_id": "stage6_minimal3199_ctrl_technical_retry_20260924_v1",
    "package_root": "artifacts/stage6_minimal3199_ctrl_technical_retry_20260924_v1",
    "input_package_root": "scripts/stage6/minimal3199/prepared_rev3",
    "card_path": "artifacts/stage6_minimal3199_ctrl_technical_retry_20260924_v1/MINIMAL3199_CTRL_S17_TECH_RETRY1_CARD_DRAFT.json",
    "manifest_path": "artifacts/stage6_minimal3199_ctrl_technical_retry_20260924_v1/INPUT_MANIFEST.json",
    "runtime_binding_path": "artifacts/stage6_minimal3199_ctrl_technical_retry_20260924_v1/control/runtime_binding.json",
    "output_root": "data/raw/stage6_minimal3199_existence_20260924_v2",
    "output_directory": "data/raw/stage6_minimal3199_existence_20260924_v2/MINIMAL3199_CTRL_S17_TECH_RETRY1/outputs",
    "consumption_directory": "artifacts/stage6_minimal3199_ctrl_technical_retry_20260924_v1/consumption",
    "output_role_source": "scripts/stage6/minimal3199/prepared_rev3/control/output_roles.json",
    "source_prelaunch_review_bundle_path": "artifacts/stage6_minimal3199_pair_preparation_20260924_rev3/PROVENANCE_RECEIPT.json",
    "arm": "control",
    "kind": "MINIMAL3199_TECH_RETRY_DRAFT",
}
MINIMAL3199_RETRY_FINAL_BINDING = {
    **MINIMAL3199_RETRY_BINDING,
    "card_path": "artifacts/stage6_minimal3199_ctrl_technical_retry_20260924_v1/MINIMAL3199_CTRL_S17_TECH_RETRY1_CARD_FINAL.json",
    "runtime_binding_path": "artifacts/stage6_minimal3199_ctrl_technical_retry_20260924_v1/control/runtime_binding_final.json",
    "kind": "MINIMAL3199_TECH_RETRY_FINAL_CONTROL",
    "authorized_wallclock_s": 90,
    "authorized_output_bytes": 60_000_000,
    "required_review_receipts": {
        "engineering": "artifacts/stage6_minimal3199_ctrl_technical_retry_20260924_v1/FINAL_ENGINEERING_PRELAUNCH_REVIEW.json",
        "data_provenance": "artifacts/stage6_minimal3199_ctrl_technical_retry_20260924_v1/FINAL_DATA_PROVENANCE_PRELAUNCH_REVIEW.json",
        "scientific": "artifacts/stage6_minimal3199_ctrl_technical_retry_20260924_v1/FINAL_SCIENTIFIC_PRELAUNCH_REVIEW.json",
    },
    "review_binding": "artifacts/stage6_minimal3199_ctrl_technical_retry_20260924_v1/FINAL_PRELAUNCH_REVIEW_BINDING.json",
}
# The retry is an exact-card Guardian dispatch too. Keep this entry additive;
# stale runner/runtime hashes still make the consumed card fail closed.
MINIMAL3199_RETRY_FINAL_BINDING.update({
    "approved_card_sha256": "027d7dc7b74561648ec6c0799abd64a99b7fb746273d1ecb78905c00c082c672",
    "runtime_binding_sha256": "5fdd6901c089d0df1346e0d01131c37d75682fe134f5c354d5ec2f3e74834052",
    "request_schema": "r02-start-v2",
    "authorization_label": "USER_AUTHORIZED_EXACTLY_ONE_CONTROL_TECHNICAL_RETRY_START",
})
SUPPORTED_RUN_BINDINGS[MINIMAL3199_RETRY_RUN_ID] = MINIMAL3199_RETRY_FINAL_BINDING
MINIMAL3199_RETRY2_RUN_ID = "MINIMAL3199_CTRL_S17_TECH_RETRY2"
MINIMAL3199_RETRY2_FINAL_BINDING = {
    **MINIMAL3199_RETRY_FINAL_BINDING,
    "package_id": "stage6_minimal3199_ctrl_technical_retry2_20260924_v1",
    "package_root": "artifacts/stage6_minimal3199_ctrl_technical_retry2_20260924_v1",
    "card_path": "artifacts/stage6_minimal3199_ctrl_technical_retry2_20260924_v1/MINIMAL3199_CTRL_S17_TECH_RETRY2_CARD_FINAL.json",
    "manifest_path": "artifacts/stage6_minimal3199_ctrl_technical_retry2_20260924_v1/EXECUTION_MANIFEST.json",
    "runtime_binding_path": "artifacts/stage6_minimal3199_ctrl_technical_retry2_20260924_v1/runtime_binding_final.json",
    "output_root": "data/raw/stage6_minimal3199_existence_20260924_v3",
    "output_directory": "data/raw/stage6_minimal3199_existence_20260924_v3/MINIMAL3199_CTRL_S17_TECH_RETRY2/outputs",
    "consumption_directory": "artifacts/stage6_minimal3199_ctrl_technical_retry2_20260924_v1/consumption",
    "output_role_source": "scripts/stage6/minimal3199/prepared_rev3/control/output_roles.json",
    "source_prelaunch_review_bundle_path": "artifacts/stage6_minimal3199_pair_preparation_20260924_rev3/PROVENANCE_RECEIPT.json",
    "required_review_receipts": {
        "engineering": "artifacts/stage6_minimal3199_ctrl_technical_retry2_20260924_v1/FINAL_ENGINEERING_PRELAUNCH_REVIEW.json",
        "data_provenance": "artifacts/stage6_minimal3199_ctrl_technical_retry2_20260924_v1/FINAL_DATA_PROVENANCE_PRELAUNCH_REVIEW.json",
        "scientific": "artifacts/stage6_minimal3199_ctrl_technical_retry2_20260924_v1/FINAL_SCIENTIFIC_PRELAUNCH_REVIEW.json",
    },
    "review_binding": "artifacts/stage6_minimal3199_ctrl_technical_retry2_20260924_v1/FINAL_PRELAUNCH_REVIEW_BINDING.json",
    "approved_card_sha256": None,
    "runtime_binding_sha256": None,
    "authorization_label": "USER_AUTHORIZED_BOUNDED_AUTONOMOUS_CONTROL_RECOVERY",
}
MINIMAL3199_RETRY_BINDINGS = {
    MINIMAL3199_RETRY_RUN_ID: MINIMAL3199_RETRY_FINAL_BINDING,
    MINIMAL3199_RETRY2_RUN_ID: MINIMAL3199_RETRY2_FINAL_BINDING,
}
SUPPORTED_RUN_BINDINGS[MINIMAL3199_RETRY2_RUN_ID] = MINIMAL3199_RETRY2_FINAL_BINDING
# Fresh U=X=0 Stage-6 treatment attempt. The exact card is authorized for one
# conditional start, but both launcher preflight and Guardian require fresh
# exact-card engineering/data/scientific review receipts before any handoff.
MINIMAL3199_TREATMENT_ATTEMPT1_RUN_ID = "MINIMAL3199_R720_DELAYED_S17_UX0_ATTEMPT1"
MINIMAL3199_TREATMENT_ATTEMPT1_BINDING = {
    "package_id": "stage6_minimal3199_ux0_r720_treatment_attempt1_20260924_rev2",
    "package_root": "artifacts/stage6_minimal3199_ux0_r720_treatment_attempt1_20260924_rev2",
    "input_package_root": "scripts/stage6/minimal3199/prepared_rev3",
    "card_path": "artifacts/stage6_minimal3199_ux0_r720_treatment_attempt1_20260924_rev2/MINIMAL3199_R720_DELAYED_S17_UX0_ATTEMPT1_CARD_FINAL_REV2.json",
    "manifest_path": "artifacts/stage6_minimal3199_ux0_r720_treatment_attempt1_20260924_rev2/INPUT_MANIFEST.json",
    "runtime_binding_path": "artifacts/stage6_minimal3199_ux0_r720_treatment_attempt1_20260924_rev2/runtime_binding_final.json",
    "output_root": "data/raw/stage6_minimal3199_existence_20260924_v4",
    "output_directory": "data/raw/stage6_minimal3199_existence_20260924_v4/MINIMAL3199_R720_DELAYED_S17_UX0_ATTEMPT1/outputs",
    "consumption_directory": "artifacts/stage6_minimal3199_ux0_r720_treatment_attempt1_20260924_rev2/consumption",
    "output_role_source": "scripts/stage6/minimal3199/prepared_rev3/treatment/output_roles.json",
    "source_prelaunch_review_bundle_path": "artifacts/stage6_minimal3199_pair_preparation_20260924_rev3/PROVENANCE_RECEIPT.json",
    "arm": "treatment",
    "kind": "MINIMAL3199_UX0_TREATMENT_FINAL",
    "authorized_wallclock_s": 120,
    "authorized_output_bytes": 100_000_000,
    "authorization_label": "USER_AUTHORIZED_CONDITIONAL_ONE_UX0_TREATMENT_START_AFTER_THREE_REVIEWS",
    "request_schema": "r02-start-v2",
    "required_review_receipts": {
        "engineering": "artifacts/stage6_minimal3199_ux0_r720_treatment_attempt1_20260924_rev2/FINAL_ENGINEERING_PRELAUNCH_REVIEW.json",
        "data_provenance": "artifacts/stage6_minimal3199_ux0_r720_treatment_attempt1_20260924_rev2/FINAL_DATA_PROVENANCE_PRELAUNCH_REVIEW.json",
        "scientific": "artifacts/stage6_minimal3199_ux0_r720_treatment_attempt1_20260924_rev2/FINAL_SCIENTIFIC_PRELAUNCH_REVIEW.json",
    },
    "review_binding": "artifacts/stage6_minimal3199_ux0_r720_treatment_attempt1_20260924_rev2/FINAL_PRELAUNCH_REVIEW_BINDING.json",
    "start_request_path": "artifacts/stage6_minimal3199_ux0_r720_treatment_attempt1_20260924_rev2/START_REQUEST.json",
    "start_request_receipt_path": "artifacts/stage6_minimal3199_ux0_r720_treatment_attempt1_20260924_rev2/START_REQUEST_RECEIPT.json",
    "matched_control_card_path": "artifacts/stage6_minimal3199_ctrl_technical_retry2_20260924_v1/MINIMAL3199_CTRL_S17_TECH_RETRY2_CARD_FINAL.json",
    "matched_control_card_sha256": "b387a750f9f41fe7439d79ead7133fc07ac817fe8da497a8e045433a4accee5a",
    "matched_control_scientific_review_path": "artifacts/stage6_minimal3199_ctrl_technical_retry2_20260924_v1/SCIENTIFIC_POSTRUN_REVIEW.json",
    "matched_control_scientific_review_sha256": "f7892d4d6fa974dbea2c373092760749b5764c8c79fbd01cd2ec49e6ca99784d",
    "matched_control_data_review_path": "artifacts/stage6_minimal3199_ctrl_technical_retry2_20260924_v1/DATA_LIFECYCLE_POSTRUN_REVIEW.json",
    "matched_control_data_review_sha256": "3579107c935b3f0a91f1f4f79d0791742b462a45548917c8ad317304fff70b37",
    "matched_control_output_manifest_path": "data/raw/stage6_minimal3199_existence_20260924_v3/MINIMAL3199_CTRL_S17_TECH_RETRY2/outputs/output_manifest.json",
    "matched_control_output_manifest_sha256": "07cd3cd1707e3717f9401f3e164a932cb6c10196af1461f267869f1d582e5e5e",
    "approved_card_sha256": None,
    "runtime_binding_sha256": None,
}
MINIMAL3199_RETRY_BINDINGS[MINIMAL3199_TREATMENT_ATTEMPT1_RUN_ID] = MINIMAL3199_TREATMENT_ATTEMPT1_BINDING
SUPPORTED_RUN_BINDINGS[MINIMAL3199_TREATMENT_ATTEMPT1_RUN_ID] = MINIMAL3199_TREATMENT_ATTEMPT1_BINDING
# A separately user-authorized repaired-v5 attempt gets a unique run ID so its
# one-use reservation cannot collide with the already-consumed D-006 run ID.
REPAIRED_V5_ATTEMPT_ID = "PAIR3199_R720_DELAYED_S17_REPAIRED_V5_ATTEMPT1"
REPAIRED_V5_FINAL_BINDING = {
    "package_id": "stage6_pair_3199_repaired_treatment_execution_20260923_v1",
    "card_path": (
        "artifacts/stage6_pair_3199_repaired_treatment_execution_20260923_v1/"
        "PAIR3199_R720_DELAYED_S17_REPAIRED_V5_ATTEMPT1_CARD_FINAL.json"
    ),
    "output_directory": (
        "data/raw/stage6_bounded_pair_repaired_20260923_v2/"
        "PAIR3199_R720_DELAYED_S17_REPAIRED_V5_ATTEMPT1/outputs"
    ),
    "output_root": "data/raw/stage6_bounded_pair_repaired_20260923_v2",
    "consumption_directory": (
        "artifacts/stage6_pair_3199_repaired_treatment_execution_20260923_v1/"
        "r02_single_start/consumption"
    ),
    "output_role_source": (
        "artifacts/stage6_pair_3199_repaired_treatment_execution_20260923_v1/"
        "inputs/treatment/output_roles.json"
    ),
    "kind": "PAIR_RUN",
    "runtime_binding_path": (
        "artifacts/stage6_pair_3199_repaired_treatment_execution_20260923_v1/"
        "runtime_bindings/PAIR3199_R720_DELAYED_S17_REPAIRED_V5_ATTEMPT1_FINAL.json"
    ),
    "authorized_wallclock_s": 120,
    "authorized_output_bytes": 100_000_000,
    "required_review_receipts": {
        "engineering": (
            "artifacts/stage6_pair_3199_repaired_treatment_execution_20260923_v1/"
            "FINAL_ENGINEERING_PRELAUNCH_REVIEW.json"
        ),
        "data_provenance": (
            "artifacts/stage6_pair_3199_repaired_treatment_execution_20260923_v1/"
            "FINAL_DATA_PROVENANCE_PRELAUNCH_REVIEW.json"
        ),
        "scientific": (
            "artifacts/stage6_pair_3199_repaired_treatment_execution_20260923_v1/"
            "FINAL_SCIENTIFIC_PRELAUNCH_REVIEW.json"
        ),
    },
    "review_binding": (
        "artifacts/stage6_pair_3199_repaired_treatment_execution_20260923_v1/"
        "FINAL_PRELAUNCH_REVIEW_BINDING.json"
    ),
}
SUPPORTED_RUN_BINDINGS[REPAIRED_V5_ATTEMPT_ID] = REPAIRED_V5_FINAL_BINDING
FINAL_AUTHORIZED_BINDINGS[REPAIRED_V5_ATTEMPT_ID] = REPAIRED_V5_FINAL_BINDING

# Exact, one-use control binding for the adopted minimal qMain=3350.4 module.
# This remains a PAIR_RUN for the generic card/input resolver, while START uses
# the stricter r02-start-v2 Guardian envelope and fresh, hash-bound reviews.
MINIMAL3350_CTRL_RUN_ID = "MINIMAL3350_CTRL_S17"
MINIMAL3350_PACKAGE_ID = "stage6_minimal3350_control_preparation_20260924_rev8"
MINIMAL3350_CONTROL_BINDING = {
    "package_id": MINIMAL3350_PACKAGE_ID,
    "card_path": f"artifacts/{MINIMAL3350_PACKAGE_ID}/MINIMAL3350_CTRL_S17_CARD_FINAL.json",
    "output_directory": "data/raw/stage6_minimal3350_ux0_20260924_v8/MINIMAL3350_CTRL_S17/outputs",
    "output_root": "data/raw/stage6_minimal3350_ux0_20260924_v8",
    "consumption_directory": f"artifacts/{MINIMAL3350_PACKAGE_ID}/r02_single_start/consumption",
    "output_role_source": f"artifacts/{MINIMAL3350_PACKAGE_ID}/inputs/control/output_roles.json",
    "runtime_binding_path": f"artifacts/{MINIMAL3350_PACKAGE_ID}/runtime_binding.json",
    "input_paths": {
        "sumocfg": "inputs/control/scenario.sumocfg",
        "demand": "inputs/control/demand.rou.xml",
        "additional": "inputs/control/scenario.add.xml",
        "output_roles": "inputs/control/output_roles.json",
        "network": "artifacts/stage6_baseline_localization_20260921_v1/LOC_M3350_S17/engineering/build_attempts/TV_BUILD01/network.net.xml",
    },
    "kind": "PAIR_RUN",
    "request_schema": "r02-start-v2",
    "start_request_path": f"artifacts/{MINIMAL3350_PACKAGE_ID}/START_REQUEST.json",
    "start_request_receipt_path": f"artifacts/{MINIMAL3350_PACKAGE_ID}/START_REQUEST_RECEIPT.json",
    "authorized_wallclock_s": 90,
    "authorized_output_bytes": 60_000_000,
    "required_review_receipts": {
        "engineering": f"artifacts/{MINIMAL3350_PACKAGE_ID}/ENGINEERING_PRELAUNCH_REVIEW.json",
        "data_provenance": f"artifacts/{MINIMAL3350_PACKAGE_ID}/DATA_PROVENANCE_PRELAUNCH_REVIEW.json",
        "scientific": f"artifacts/{MINIMAL3350_PACKAGE_ID}/SCIENTIFIC_PRELAUNCH_REVIEW.json",
    },
    "review_binding": f"artifacts/{MINIMAL3350_PACKAGE_ID}/FINAL_PRELAUNCH_REVIEW_BINDING.json",
}
MINIMAL3350_TREATMENT_RUN_ID = "MINIMAL3350_E1_R900_DELAYED_S17"
MINIMAL3350_TREATMENT_PACKAGE_ID = "stage6_minimal3350_e1_r900_preparation_20260925_rev6"
MINIMAL3350_TREATMENT_BINDING = {
    "package_id": MINIMAL3350_TREATMENT_PACKAGE_ID,
    "card_path": f"artifacts/{MINIMAL3350_TREATMENT_PACKAGE_ID}/{MINIMAL3350_TREATMENT_RUN_ID}_CARD_PRELAUNCH_REV1.json",
    "output_directory": "data/raw/stage6_minimal3350_ux0_20260925_v16/MINIMAL3350_E1_R900_DELAYED_S17/outputs",
    "output_root": "data/raw/stage6_minimal3350_ux0_20260925_v16",
    "consumption_directory": f"artifacts/{MINIMAL3350_TREATMENT_PACKAGE_ID}/r02_single_start/consumption",
    "output_role_source": f"artifacts/{MINIMAL3350_TREATMENT_PACKAGE_ID}/inputs/treatment/output_roles.json",
    "runtime_binding_path": f"artifacts/{MINIMAL3350_TREATMENT_PACKAGE_ID}/runtime_binding.json",
    "input_paths": {
        "sumocfg": "inputs/treatment/scenario.sumocfg",
        "demand": "inputs/treatment/demand.rou.xml",
        "additional": "inputs/treatment/scenario.add.xml",
        "output_roles": "inputs/treatment/output_roles.json",
        "network": "artifacts/stage6_baseline_localization_20260921_v1/LOC_M3350_S17/engineering/build_attempts/TV_BUILD01/network.net.xml",
    },
    "kind": "PAIR_RUN",
    "request_schema": "r02-start-v2",
    "start_request_path": f"artifacts/{MINIMAL3350_TREATMENT_PACKAGE_ID}/START_REQUEST.json",
    "start_request_receipt_path": f"artifacts/{MINIMAL3350_TREATMENT_PACKAGE_ID}/START_REQUEST_RECEIPT.json",
    "authorized_wallclock_s": 120,
    "authorized_output_bytes": 100_000_000,
    "required_review_receipts": {
        "engineering": f"artifacts/{MINIMAL3350_TREATMENT_PACKAGE_ID}/ENGINEERING_PRELAUNCH_REVIEW.json",
        "data_provenance": f"artifacts/{MINIMAL3350_TREATMENT_PACKAGE_ID}/DATA_PROVENANCE_PRELAUNCH_REVIEW.json",
        "scientific": f"artifacts/{MINIMAL3350_TREATMENT_PACKAGE_ID}/SCIENTIFIC_PRELAUNCH_REVIEW.json",
    },
    "review_binding": f"artifacts/{MINIMAL3350_TREATMENT_PACKAGE_ID}/FINAL_PRELAUNCH_REVIEW_BINDING.json",
}
MINIMAL3350_BINDINGS = {
    MINIMAL3350_CTRL_RUN_ID: MINIMAL3350_CONTROL_BINDING,
    MINIMAL3350_TREATMENT_RUN_ID: MINIMAL3350_TREATMENT_BINDING,
}
SUPPORTED_RUN_BINDINGS.update(MINIMAL3350_BINDINGS)
MINIMAL3350_V2_RUN_IDS = set(MINIMAL3350_BINDINGS)
PRELAUNCH_ONLY_BINDINGS[MINIMAL3350_TREATMENT_RUN_ID] = {
    **MINIMAL3350_TREATMENT_BINDING,
    "card_path": f"artifacts/{MINIMAL3350_TREATMENT_PACKAGE_ID}/{MINIMAL3350_TREATMENT_RUN_ID}_CARD_PRELAUNCH_REV1.json",
}
MINIMAL3350_TREATMENT_BINDING["card_path"] = PRELAUNCH_ONLY_BINDINGS[MINIMAL3350_TREATMENT_RUN_ID]["card_path"]
MINIMAL3350_TREATMENT_BINDING["authorized_wallclock_s"] = 120
MINIMAL3350_TREATMENT_BINDING["authorized_output_bytes"] = 100_000_000


def minimal3350_binding(run_id: str) -> dict[str, Any]:
    binding = MINIMAL3350_BINDINGS.get(run_id)
    if binding is None:
        raise GateError("MINIMAL3350_RUN_BINDING_UNSUPPORTED")
    return binding


def _requires_v2_start(run_id: Any) -> bool:
    return run_id in MINIMAL3199_RETRY_BINDINGS or run_id in MINIMAL3350_V2_RUN_IDS
# Additive, exact-card-only binding for the repaired PAIR3199 treatment.  The
# run ID is intentionally the same historical treatment ID; resolution is by
# exact card path so the consumed run binding above remains untouched.
REPAIRED_PRELAUNCH_CARD_PATH = (
    "artifacts/stage6_pair_3199_repaired_treatment_preparation_20260923_v1/"
    "PAIR_3199_R720_DELAYED_S17_CARD_DRAFT_NOT_AUTHORIZED_REV1.json"
)
REPAIRED_PRELAUNCH_BINDING = {
    "package_id": "stage6_pair_3199_repaired_treatment_preparation_20260923_v1",
    "card_path": REPAIRED_PRELAUNCH_CARD_PATH,
    "output_directory": (
        "data/raw/stage6_bounded_pair_repaired_20260923_v1/"
        "PAIR_3199_R720_DELAYED_S17/outputs"
    ),
    "output_root": "data/raw/stage6_bounded_pair_repaired_20260923_v1",
    "consumption_directory": (
        "artifacts/stage6_pair_3199_repaired_treatment_preparation_20260923_v1/"
        "r02_single_start/consumption"
    ),
    "output_role_source": (
        "artifacts/stage6_pair_3199_repaired_treatment_preparation_20260923_v1/"
        "inputs/treatment/output_roles.json"
    ),
    "kind": "PAIR_RUN",
    "runtime_binding_path": (
        "artifacts/stage6_pair_3199_repaired_treatment_preparation_20260923_v1/"
        "runtime_bindings/PAIR_3199_R720_DELAYED_S17_PRELAUNCH_REV1.json"
    ),
}
GUARDIAN_POLL_S = 0.10
GUARDIAN_READY_TIMEOUT_S = 5.0
GUARDIAN_SHUTDOWN_GRACE_S = 5.0


class GateError(RuntimeError):
    pass


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def canonical_json_bytes(value: Any) -> bytes:
    return (json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False) + "\n").encode()


def load_json(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise GateError(f"CARD_READ_ERROR:{exc}") from exc
    if not isinstance(value, dict):
        raise GateError("CARD_NOT_OBJECT")
    return value


def _resolve_repo_file(repo: Path, rel: str) -> Path:
    p = (repo / rel).resolve(strict=True)
    if not p.is_relative_to(repo.resolve(strict=True)):
        raise GateError(f"INPUT_PATH_ESCAPES_REPOSITORY:{rel}")
    if not p.is_file():
        raise GateError(f"INPUT_NOT_FILE:{rel}")
    return p


def _run_binding(repo: Path, card_path: Path, card: dict[str, Any]) -> dict[str, Any]:
    run_id = card.get("run_id")
    if run_id in MINIMAL3199_RETRY_BINDINGS:
        retry_final_binding = MINIMAL3199_RETRY_BINDINGS[run_id]
        retry_rel = card_path.relative_to(repo).as_posix()
        if retry_rel == retry_final_binding["card_path"]:
            expected_retry_binding = retry_final_binding
        elif run_id == MINIMAL3199_RETRY_RUN_ID and retry_rel == MINIMAL3199_RETRY_BINDING["card_path"]:
            expected_retry_binding = MINIMAL3199_RETRY_BINDING
        else:
            raise GateError("CARD_PATH_RUN_ID_BINDING_MISMATCH")
        if card.get("output_directory") != expected_retry_binding["output_directory"]:
            raise GateError("OUTPUT_DIRECTORY_BINDING_MISMATCH")
        binding = card.get("runner_binding")
        if not isinstance(binding, dict):
            raise GateError("RUNNER_BINDING_MISSING")
        for key in ("run_id", "package_id", "card_path", "output_directory", "consumption_directory", "kind"):
            expected_value = run_id if key == "run_id" else expected_retry_binding[key]
            if binding.get(key) != expected_value:
                raise GateError(f"RUNNER_BINDING_MISMATCH:{key}")
        return expected_retry_binding
    minimal_final = MINIMAL3199_FINAL_BINDINGS.get(run_id) if isinstance(run_id, str) else None
    if minimal_final is not None:
        card_rel = card_path.relative_to(repo).as_posix()
        if card_rel != minimal_final["card_path"]:
            raise GateError("CARD_PATH_RUN_ID_BINDING_MISMATCH")
        if card.get("output_directory") != minimal_final["output_directory"]:
            raise GateError("OUTPUT_DIRECTORY_BINDING_MISMATCH")
        binding = card.get("runner_binding")
        if not isinstance(binding, dict):
            raise GateError("RUNNER_BINDING_MISSING")
        for key in ("run_id", "package_id", "card_path", "output_directory", "consumption_directory", "kind"):
            if binding.get(key) != (run_id if key == "run_id" else minimal_final[key]):
                raise GateError(f"RUNNER_BINDING_MISMATCH:{key}")
        return minimal_final
    minimal_binding = MINIMAL3199_RUN_BINDINGS.get(run_id) if isinstance(run_id, str) else None
    if minimal_binding is not None:
        card_rel = card_path.relative_to(repo).as_posix()
        if card_rel != minimal_binding["card_path"]:
            raise GateError("CARD_PATH_RUN_ID_BINDING_MISMATCH")
        if card.get("output_directory") != minimal_binding["output_directory"]:
            raise GateError("OUTPUT_DIRECTORY_BINDING_MISMATCH")
        binding = card.get("runner_binding")
        if not isinstance(binding, dict):
            raise GateError("RUNNER_BINDING_MISSING")
        for key in ("run_id", "package_id", "card_path", "output_directory", "consumption_directory", "kind"):
            if binding.get(key) != (run_id if key == "run_id" else minimal_binding[key]):
                raise GateError(f"RUNNER_BINDING_MISMATCH:{key}")
        return minimal_binding
    expected = SUPPORTED_RUN_BINDINGS.get(run_id) if isinstance(run_id, str) else None
    if expected is None:
        raise GateError("UNSUPPORTED_RUN_ID")
    card_rel = card_path.relative_to(repo).as_posix()
    if (run_id == "PAIR_3199_R720_DELAYED_S17"
            and card_rel == REPAIRED_PRELAUNCH_BINDING["card_path"]):
        expected = REPAIRED_PRELAUNCH_BINDING
    final_binding = FINAL_AUTHORIZED_BINDINGS.get(run_id)
    if final_binding is not None and card_rel == final_binding["card_path"]:
        expected = final_binding
    prelaunch_binding = PRELAUNCH_ONLY_BINDINGS.get(run_id)
    if card_rel == REPAIRED_PRELAUNCH_BINDING["card_path"]:
        prelaunch_binding = REPAIRED_PRELAUNCH_BINDING
    if prelaunch_binding is not None and card_rel == prelaunch_binding["card_path"]:
        expected = prelaunch_binding
    if run_id == LEGACY_RUN_ID and card_rel == expected["card_path"]:
        if card.get("output_directory") != expected["output_directory"]:
            raise GateError("OUTPUT_DIRECTORY_BINDING_MISMATCH")
        return expected
    binding = card.get("runner_binding")
    if not isinstance(binding, dict):
        raise GateError("RUNNER_BINDING_MISSING")
    for key in ("run_id", "package_id", "card_path", "output_directory", "consumption_directory", "kind"):
        if binding.get(key) != (run_id if key == "run_id" else expected[key]):
            raise GateError(f"RUNNER_BINDING_MISMATCH:{key}")
    if card_rel != expected["card_path"]:
        raise GateError("CARD_PATH_RUN_ID_BINDING_MISMATCH")
    if card.get("output_directory") != expected["output_directory"]:
        raise GateError("OUTPUT_DIRECTORY_BINDING_MISMATCH")
    package = (repo / "artifacts" / expected["package_id"]).resolve(strict=True)
    if not card_path.is_relative_to(package):
        raise GateError("CARD_PACKAGE_BINDING_MISMATCH")
    return expected


def verify_sumo_schema_binding(runtime: dict[str, Any]) -> Path:
    """Fail closed unless card binds the canonical local SUMO schema path/hash."""
    raw_home = runtime.get("sumo_home")
    raw_schema = runtime.get("additional_schema_path")
    if not isinstance(raw_home, str) or not Path(raw_home).is_absolute():
        raise GateError("SUMO_HOME_BINDING_INVALID")
    try:
        home = Path(raw_home).resolve(strict=True)
    except OSError as exc:
        raise GateError("SUMO_HOME_PATH_NOT_FOUND") from exc
    if not home.is_dir() or str(home) != EXPECTED_SUMO_HOME:
        raise GateError("SUMO_HOME_PATH_MISMATCH")
    expected_schema = (home / "data" / "xsd" / "additional_file.xsd").resolve(strict=False)
    if raw_schema != str(expected_schema):
        raise GateError("ADDITIONAL_SCHEMA_PATH_MISMATCH")
    if not expected_schema.is_file():
        raise GateError("ADDITIONAL_SCHEMA_NOT_FOUND")
    actual_hash = sha256_file(expected_schema)
    if actual_hash != EXPECTED_ADDITIONAL_SCHEMA_SHA256 or runtime.get("additional_schema_sha256") != actual_hash:
        raise GateError("ADDITIONAL_SCHEMA_HASH_MISMATCH")
    return home


def verified_additional_schema(runtime: dict[str, Any]) -> Path:
    """Return the validated schema file, translating absent/malformed fields to GateError."""
    verify_sumo_schema_binding(runtime)
    raw_schema = runtime.get("additional_schema_path")
    if not isinstance(raw_schema, str) or not Path(raw_schema).is_absolute():
        raise GateError("ADDITIONAL_SCHEMA_PATH_BINDING_INVALID")
    try:
        schema = Path(raw_schema).resolve(strict=True)
    except OSError as exc:
        raise GateError("ADDITIONAL_SCHEMA_NOT_FOUND") from exc
    if not schema.is_file() or sha256_file(schema) != runtime.get("additional_schema_sha256"):
        raise GateError("ADDITIONAL_SCHEMA_HASH_MISMATCH")
    return schema


def stage_minimal3199_inputs(source_cfg: Path, source_additional: Path,
                             source_output_directory: Path, output_directory: Path
                             ) -> tuple[bytes, bytes, dict[str, Any]]:
    """Build exact run-scoped config and additional-file bytes for preflight/staging.

    Replacements are deliberately ordered: relocate every simulator output from
    the consumed attempt in the sumocfg and additional file, then point the
    additional-files input at the staged scenario_control.add.xml.
    """
    try:
        source_text = source_cfg.read_bytes().decode("utf-8", errors="strict")
        additional_text = source_additional.read_bytes().decode("utf-8", errors="strict")
    except (OSError, UnicodeDecodeError) as exc:
        raise GateError("MINIMAL3199_STAGED_INPUT_SOURCE_UNREADABLE") from exc
    old_output = str(source_output_directory.resolve(strict=False))
    new_output = str(output_directory.resolve(strict=False))
    old_additional = str(source_additional.resolve(strict=False))
    new_additional = str((output_directory / "scenario_control.add.xml").resolve(strict=False))
    cfg_output_count = source_text.count(old_output)
    cfg_additional_count = source_text.count(old_additional)
    add_output_count = additional_text.count(old_output)
    if (cfg_output_count != 8 or cfg_additional_count != 1 or add_output_count != 12):
        raise GateError("MINIMAL3199_STAGED_INPUT_TRANSFORM_SOURCE_OCCURRENCE_MISMATCH")
    staged_cfg_text = source_text.replace(old_output, new_output)
    staged_cfg_text = staged_cfg_text.replace(old_additional, new_additional)
    staged_additional_text = additional_text.replace(old_output, new_output)
    if (old_output in staged_cfg_text or old_additional in staged_cfg_text
            or old_output in staged_additional_text):
        raise GateError("MINIMAL3199_STAGED_INPUT_TRANSFORM_INCOMPLETE")
    cfg_data = staged_cfg_text.encode("utf-8")
    add_data = staged_additional_text.encode("utf-8")
    transform = {
        "encoding": "UTF-8",
        "rules_in_order": [
            {"file": "sumocfg", "source": old_output, "target": new_output, "expected_occurrences": 8},
            {"file": "sumocfg", "source": old_additional, "target": new_additional, "expected_occurrences": 1},
            {"file": "additional", "source": old_output, "target": new_output, "expected_occurrences": 12},
        ],
        "sumocfg": {"expected_staged_bytes": len(cfg_data),
                    "expected_staged_sha256": hashlib.sha256(cfg_data).hexdigest()},
        "additional": {"expected_staged_bytes": len(add_data),
                       "expected_staged_sha256": hashlib.sha256(add_data).hexdigest()},
    }
    return cfg_data, add_data, transform


def validate_staged_config_binding(staged_spec: Any, card: dict[str, Any],
                                   source: dict[str, Any], transform: dict[str, Any]) -> None:
    """Validate complete source and deterministic staged config/additional bindings."""
    if (not isinstance(staged_spec, dict) or staged_spec.get("sumocfg_source") != source.get("sumocfg")
            or staged_spec.get("additional_source") != source.get("additional")):
        raise GateError("MINIMAL3199_STAGED_INPUT_SOURCE_BINDING_MISMATCH")
    if (staged_spec.get("transform") != transform
            or card.get("staged_config_sha256") != transform["sumocfg"]["expected_staged_sha256"]
            or card.get("staged_config_bytes") != transform["sumocfg"]["expected_staged_bytes"]
            or card.get("staged_additional_sha256") != transform["additional"]["expected_staged_sha256"]
            or card.get("staged_additional_bytes") != transform["additional"]["expected_staged_bytes"]):
        raise GateError("MINIMAL3199_STAGED_INPUT_EXPECTATION_MISMATCH")


def validate_minimal3199_runner_hashes(manifest: dict[str, Any], card: dict[str, Any],
                                       runtime: dict[str, Any], runner_path: Path, repo: Path,
                                       actual_sha256: str) -> None:
    """Require all extant runner hash references to agree; reject stale duplicates."""
    duplicate = manifest.get("runner")
    if duplicate is not None and (not isinstance(duplicate, dict)
            or duplicate.get("path") != str(runner_path)
            or duplicate.get("sha256") != actual_sha256):
        raise GateError("MINIMAL3199_DUPLICATE_RUNNER_HASH_MISMATCH")
    if (manifest.get("runner_path") != runner_path.resolve(strict=True).relative_to(repo.resolve(strict=True)).as_posix()
            or manifest.get("runner_sha256") != actual_sha256
            or card.get("runner", {}).get("sha256") != actual_sha256
            or runtime.get("guardian_runner_sha256") != actual_sha256):
        raise GateError("MINIMAL3199_RUNNER_HASH_BINDING_MISMATCH")


def build_guardian_start_spec(files: dict[str, Any], card: dict[str, Any], output: Path,
                              reservation: Path, repo: Path, run_id: str,
                              card_path: Path | None = None,
                              approved_card_sha256: str | None = None) -> dict[str, Any]:
    """Fail closed on an incomplete resolved START input map before Guardian."""
    required = {"binary", "sumocfg", "sumo_home", "additional_schema", "output_roles",
                "output_role_source_sha256"}
    missing = sorted(required - set(files))
    if missing:
        raise GateError(f"RESOLVED_START_INPUT_MISSING:{','.join(missing)}")
    schema = files["additional_schema"]
    if not isinstance(schema, Path) or not schema.is_file():
        raise GateError("RESOLVED_ADDITIONAL_SCHEMA_INVALID")
    runtime = card.get("runtime_binding")
    if not isinstance(runtime, dict) or sha256_file(schema) != runtime.get("additional_schema_sha256"):
        raise GateError("RESOLVED_ADDITIONAL_SCHEMA_HASH_MISMATCH")
    spec = {
        "action": "START", "run_id": run_id,
        "command": [str(files["binary"]), "-c", str(files["sumocfg"])],
        "cwd": str(repo), "output_directory": str(output), "reservation_path": str(reservation),
        "sumo_home": str(files["sumo_home"]),
        "additional_schema_path": str(schema),
        "additional_schema_sha256": runtime["additional_schema_sha256"],
        "max_runtime_s": runtime["max_runtime_s"], "max_output_bytes": runtime["max_output_bytes"],
        "output_roles": files["output_roles"],
        "output_role_source": card["output_role_source"]["path"],
        "output_role_source_sha256": files["output_role_source_sha256"],
    }
    if _requires_v2_start(run_id):
        if card_path is None or approved_card_sha256 is None:
            raise GateError("MINIMAL3199_START_CARD_PROVENANCE_MISSING")
        binding = (MINIMAL3199_RETRY_BINDINGS[run_id] if run_id in MINIMAL3199_RETRY_BINDINGS
                   else minimal3350_binding(run_id))
        runner_path = Path(__file__).resolve()
        runtime_path = repo / binding["runtime_binding_path"]
        spec.update({
            "request_schema": binding["request_schema"],
            "card_path": card_path.resolve(strict=True).relative_to(repo.resolve(strict=True)).as_posix(),
            "card_sha256": approved_card_sha256,
            "runtime_binding_path": binding["runtime_binding_path"],
            "runtime_binding_sha256": sha256_file(runtime_path),
            "runner_path": runner_path.relative_to(repo.resolve(strict=True)).as_posix(),
            "runner_sha256": sha256_file(runner_path),
        })
    return spec


def validate_guardian_start_request(start: Any, repo: Path,
                                    bindings: dict[str, dict[str, Any]] | None = None, *,
                                    require_reviews: bool = True) -> dict[str, Any]:
    """Validate the exact MINIMAL3199 v2 START envelope before Guardian can spawn.

    `bindings` is injectable only to make the pure validator independently
    testable with temporary fixtures. Production calls use the immutable
    SUPPORTED_RUN_BINDINGS registry.
    """
    if not isinstance(start, dict):
        raise GateError("INVALID_START_REQUEST")
    run_id = start.get("run_id")
    registry = SUPPORTED_RUN_BINDINGS if bindings is None else bindings
    binding = registry.get(run_id) if isinstance(run_id, str) else None
    if binding is None or not _requires_v2_start(run_id):
        raise GateError("INVALID_START_REQUEST")
    expected_keys = {
        "action", "run_id", "command", "cwd", "output_directory", "reservation_path",
        "sumo_home", "additional_schema_path", "additional_schema_sha256",
        "max_runtime_s", "max_output_bytes", "output_roles", "output_role_source",
        "output_role_source_sha256", "request_schema", "card_path", "card_sha256",
        "runtime_binding_path", "runtime_binding_sha256", "runner_path", "runner_sha256",
    }
    if set(start) != expected_keys:
        raise GateError("INVALID_START_REQUEST_SCHEMA")
    if start.get("action") != "START" or start.get("request_schema") != binding.get("request_schema"):
        raise GateError("INVALID_START_REQUEST_SCHEMA")
    if any(not isinstance(start.get(k), str) for k in (
        "run_id", "cwd", "output_directory", "reservation_path", "sumo_home",
        "additional_schema_path", "additional_schema_sha256", "output_role_source",
        "output_role_source_sha256", "card_path", "card_sha256", "runtime_binding_path",
        "runtime_binding_sha256", "runner_path", "runner_sha256")):
        raise GateError("INVALID_START_REQUEST_TYPES")
    if type(start.get("max_runtime_s")) not in (int, float) or type(start.get("max_output_bytes")) is not int:
        raise GateError("INVALID_START_REQUEST_TYPES")
    if not isinstance(start.get("command"), list) or any(not isinstance(x, str) for x in start["command"]):
        raise GateError("INVALID_START_REQUEST_TYPES")
    if not isinstance(start.get("output_roles"), list):
        raise GateError("INVALID_START_REQUEST_TYPES")

    root = repo.resolve(strict=True)
    expected_output = (root / binding["output_directory"]).resolve(strict=False)
    expected_reservation = (root / binding["consumption_directory"] / f"{run_id}.json").resolve(strict=False)
    expected_card = binding["card_path"]
    expected_runtime = binding["runtime_binding_path"]
    expected_role_source = binding["output_role_source"]
    if start["cwd"] != str(root):
        raise GateError("START_CWD_BINDING_MISMATCH")
    if start["output_directory"] != str(expected_output) or start["reservation_path"] != str(expected_reservation):
        raise GateError("START_PROVENANCE_BINDING_MISMATCH")
    if (start["card_path"] != expected_card
            or (binding.get("approved_card_sha256") is not None
                and start["card_sha256"] != binding["approved_card_sha256"])):
        raise GateError("START_CARD_BINDING_MISMATCH")
    if (start["runtime_binding_path"] != expected_runtime
            or (binding.get("runtime_binding_sha256") is not None
                and start["runtime_binding_sha256"] != binding["runtime_binding_sha256"])):
        raise GateError("START_RUNTIME_BINDING_MISMATCH")
    if start["sumo_home"] != EXPECTED_SUMO_HOME or start["additional_schema_path"] != EXPECTED_ADDITIONAL_SCHEMA:
        raise GateError("START_SCHEMA_PATH_BINDING_MISMATCH")
    if start["additional_schema_sha256"] != EXPECTED_ADDITIONAL_SCHEMA_SHA256:
        raise GateError("START_SCHEMA_HASH_BINDING_MISMATCH")
    expected_runtime_s = binding.get("authorized_wallclock_s", 90)
    expected_output_bytes = binding.get("authorized_output_bytes", 60_000_000)
    if (start["max_runtime_s"] != expected_runtime_s
            or start["max_output_bytes"] != expected_output_bytes):
        raise GateError("START_RESOURCE_BINDING_MISMATCH")
    if start["output_role_source"] != expected_role_source:
        raise GateError("START_OUTPUT_ROLE_SOURCE_BINDING_MISMATCH")

    card_file = (root / expected_card).resolve(strict=True)
    if not card_file.is_relative_to(root) or sha256_file(card_file) != start["card_sha256"]:
        raise GateError("START_CARD_HASH_MISMATCH")
    card = load_json(card_file)
    expected_card_status = "FINAL_AUTHORIZED_FOR_ONE_START"
    if (card.get("run_id") != run_id or card.get("execution_attempt_id") != run_id
            or card.get("execution_authorized") is not True
            or card.get("card_status") != expected_card_status):
        raise GateError("START_CARD_RUN_ID_MISMATCH")
    card_runner_binding = card.get("runner_binding")
    if not isinstance(card_runner_binding, dict):
        raise GateError("START_CARD_RUN_BINDING_MISSING")
    for key in ("run_id", "package_id", "card_path", "output_directory", "consumption_directory", "kind"):
        expected_value = run_id if key == "run_id" else binding.get(key)
        if card_runner_binding.get(key) != expected_value:
            raise GateError(f"START_CARD_RUN_BINDING_MISMATCH:{key}")
    if card.get("output_directory") != binding.get("output_directory"):
        raise GateError("START_CARD_OUTPUT_BINDING_MISMATCH")
    if (card.get("runtime_binding", {}).get("max_runtime_s") != start["max_runtime_s"]
            or card.get("runtime_binding", {}).get("max_output_bytes") != start["max_output_bytes"]):
        raise GateError("START_CARD_RESOURCE_BINDING_MISMATCH")
    runtime_file = (root / expected_runtime).resolve(strict=True)
    if not runtime_file.is_relative_to(root) or sha256_file(runtime_file) != start["runtime_binding_sha256"]:
        raise GateError("START_RUNTIME_HASH_MISMATCH")
    runtime = load_json(runtime_file)
    if runtime != card.get("runtime_binding"):
        raise GateError("START_RUNTIME_CONTENT_MISMATCH")

    card_runner = card.get("runner")
    if (not isinstance(card_runner, dict) or card_runner.get("path") != start["runner_path"]
            or card_runner.get("sha256") != start["runner_sha256"]):
        raise GateError("START_RUNNER_CARD_BINDING_MISMATCH")
    runner_file = (root / start["runner_path"]).resolve(strict=True)
    if (not runner_file.is_relative_to(root) or sha256_file(runner_file) != start["runner_sha256"]
            or runtime.get("guardian_runner_sha256") != start["runner_sha256"]):
        raise GateError("START_RUNNER_HASH_BINDING_MISMATCH")
    binary = runtime.get("binary_path")
    expected_cfg = expected_output / "scenario_control.sumocfg"
    if (not isinstance(binary, str) or start["command"] != [binary, "-c", str(expected_cfg)]
            or not Path(binary).is_absolute()):
        raise GateError("START_COMMAND_BINDING_MISMATCH")
    if start["output_role_source_sha256"] != card.get("output_role_source", {}).get("sha256"):
        raise GateError("START_OUTPUT_ROLE_HASH_BINDING_MISMATCH")
    if run_id == MINIMAL3199_TREATMENT_ATTEMPT1_RUN_ID and require_reviews:
        review_gate = minimal3199_retry_final_review_gate(repo, start["card_sha256"], run_id)
        if review_gate.get("status") != "PASS":
            raise GateError("MINIMAL3199_TREATMENT_REVIEWS_NOT_PASSED_AND_HASH_BOUND")
    if run_id in MINIMAL3350_V2_RUN_IDS and require_reviews:
        review_gate = minimal3350_final_review_gate(repo, start["card_sha256"], run_id)
        if review_gate.get("status") != "PASS":
            raise GateError("MINIMAL3350_REVIEWS_NOT_PASSED_AND_HASH_BOUND")
    role_path = (root / expected_role_source).resolve(strict=True)
    if not role_path.is_relative_to(root) or sha256_file(role_path) != start["output_role_source_sha256"]:
        raise GateError("START_OUTPUT_ROLE_HASH_MISMATCH")
    role_data = load_json(role_path)
    if start["output_roles"] != role_data.get("required_xml_roles"):
        raise GateError("START_OUTPUT_ROLES_CONTENT_MISMATCH")
    if not isinstance(start["output_roles"], list) or len(start["output_roles"]) != 18:
        raise GateError("START_OUTPUT_ROLES_SCHEMA_MISMATCH")
    return binding


def validate_persisted_treatment_start_request(
        repo: Path, card_path: Path, approved_card_sha256: str,
        card: dict[str, Any], files: dict[str, Any], output: Path) -> dict[str, Any]:
    """Rebuild and verify the exact persisted, unsent START request and receipt."""
    run_id = card.get("run_id")
    binding = MINIMAL3199_RETRY_BINDINGS.get(run_id)
    if binding is None or binding.get("kind") != "MINIMAL3199_UX0_TREATMENT_FINAL":
        raise GateError("PERSISTED_START_REQUEST_UNSUPPORTED_RUN")
    request_rel = binding.get("start_request_path")
    receipt_rel = binding.get("start_request_receipt_path")
    card_request = card.get("guardian_request_binding")
    expected_card_request = {
        "schema": binding["request_schema"],
        "request_path": request_rel,
        "receipt_path": receipt_rel,
        "status": "PERSISTED_UNSENT",
    }
    manifest_path = repo / binding["manifest_path"]
    manifest = load_json(manifest_path)
    if (card_request != expected_card_request
            or manifest.get("guardian_request_binding") != expected_card_request):
        raise GateError("PERSISTED_START_REQUEST_CARD_BINDING_MISMATCH")
    request_path = _resolve_repo_file(repo, request_rel)
    receipt_path = _resolve_repo_file(repo, receipt_rel)
    reservation = (repo / binding["consumption_directory"] / f"{run_id}.json").resolve(strict=False)
    if reservation.exists():
        raise GateError("ONE_START_ALREADY_CONSUMED")
    staged_files = dict(files)
    staged_files["sumocfg"] = output / "scenario_control.sumocfg"
    expected = build_guardian_start_spec(
        staged_files, card, output, reservation, repo, run_id,
        card_path=card_path, approved_card_sha256=approved_card_sha256)
    expected_bytes = canonical_json_bytes(expected)
    try:
        actual_bytes = request_path.read_bytes()
        receipt = load_json(receipt_path)
    except OSError as exc:
        raise GateError("PERSISTED_START_REQUEST_OR_RECEIPT_MISSING") from exc
    request_hash = hashlib.sha256(expected_bytes).hexdigest()
    if actual_bytes != expected_bytes:
        raise GateError("PERSISTED_START_REQUEST_CONTENT_MISMATCH")
    expected_receipt = {
        "schema_version": "1",
        "status": "PERSISTED_UNSENT",
        "dispatched": False,
        "run_id": run_id,
        "request_schema": binding["request_schema"],
        "card_path": binding["card_path"],
        "card_sha256": approved_card_sha256,
        "request_path": request_rel,
        "request_sha256": request_hash,
        "request_bytes": len(expected_bytes),
        "output_directory": binding["output_directory"],
        "reservation_path": reservation.relative_to(repo.resolve(strict=True)).as_posix(),
        "max_runtime_s": binding["authorized_wallclock_s"],
        "max_output_bytes": binding["authorized_output_bytes"],
    }
    if receipt != expected_receipt:
        raise GateError("PERSISTED_START_REQUEST_RECEIPT_MISMATCH")
    validate_guardian_start_request(expected, repo, require_reviews=False)
    return {"request": expected, "request_sha256": request_hash,
            "request_receipt_path": receipt_rel}


def prepare_minimal3199_guardian_start(repo: Path, card_path: Path, approved_hash: str,
                                       card: dict[str, Any], files: dict[str, Any],
                                       output: Path, reservation: Path) -> dict[str, Any]:
    """Build and validate the same exact START payload before one-use consumption."""
    if not _requires_v2_start(card.get("run_id")):
        raise GateError("MINIMAL3199_START_RUN_ID_UNSUPPORTED")
    cfg_path = output / "scenario_control.sumocfg"
    add_path = output / "scenario_control.add.xml"
    if card.get("run_id") in MINIMAL3199_RETRY_BINDINGS and (not cfg_path.is_file() or not add_path.is_file()):
        raise GateError("MINIMAL3199_STAGED_INPUTS_NOT_MATERIALIZED")
    staged_files = dict(files)
    staged_files["sumocfg"] = cfg_path
    start = build_guardian_start_spec(
        staged_files, card, output, reservation, repo, card["run_id"],
        card_path=card_path, approved_card_sha256=approved_hash)
    if card["run_id"] == MINIMAL3199_TREATMENT_ATTEMPT1_RUN_ID:
        persisted = validate_persisted_treatment_start_request(
            repo, card_path, approved_hash, card, files, output)
        if canonical_json_bytes(persisted["request"]) != canonical_json_bytes(start):
            raise GateError("PERSISTED_START_REQUEST_REBUILD_MISMATCH")
    validate_guardian_start_request(start, repo)
    if card.get("run_id") in MINIMAL3350_V2_RUN_IDS:
        binding = minimal3350_binding(card["run_id"])
        expected_binding = {
            "schema": binding["request_schema"],
            "request_path": binding["start_request_path"],
            "receipt_path": binding["start_request_receipt_path"],
            "status": "PERSISTED_UNSENT",
        }
        if card.get("guardian_request_binding") != expected_binding:
            raise GateError("MINIMAL3350_REQUEST_BINDING_MISMATCH")
        request_path = _resolve_repo_file(repo, expected_binding["request_path"])
        receipt_path = _resolve_repo_file(repo, expected_binding["receipt_path"])
        persisted = load_json(request_path)
        receipt = load_json(receipt_path)
        request_hash = hashlib.sha256(canonical_json_bytes(start)).hexdigest()
        if (canonical_json_bytes(persisted) != canonical_json_bytes(start)
                or receipt.get("status") != "PASS_PERSISTED_UNSENT"
                or receipt.get("run_id") != card["run_id"]
                or receipt.get("card_sha256") != approved_hash
                or receipt.get("request_sha256") != request_hash
                or receipt.get("dispatched") is not False):
            raise GateError("MINIMAL3350_PERSISTED_REQUEST_PROVENANCE_MISMATCH")
    return start


def repaired_final_review_gate(repo: Path, approved_card_sha256: str) -> dict[str, Any]:
    """Require fresh, exact-card, zero-finding reviews before repaired launch."""
    results: dict[str, Any] = {}
    for role, rel in REPAIRED_V5_FINAL_BINDING["required_review_receipts"].items():
        path = repo / rel
        if not path.is_file():
            results[role] = {"status": "MISSING", "path": rel}
            continue
        try:
            value = load_json(path)
        except GateError as exc:
            results[role] = {"status": "INVALID", "path": rel, "reason": str(exc)}
            continue
        findings = value.get("findings")
        passed = (
            value.get("status") == "PASS_PRELAUNCH"
            and value.get("card_sha256") == approved_card_sha256
            and isinstance(findings, dict)
            and findings.get("blocker") == 0
            and findings.get("major") == 0
            and findings.get("required_minor") == 0
        )
        results[role] = {"status": "PASS" if passed else "FAIL", "path": rel}
    reviews_pass = all(item["status"] == "PASS" for item in results.values())
    sidecar_rel = REPAIRED_V5_FINAL_BINDING["review_binding"]
    sidecar_path = repo / sidecar_rel
    sidecar_pass = False
    if reviews_pass and sidecar_path.is_file():
        try:
            sidecar = load_json(sidecar_path)
            expected_hashes = {
                role: sha256_file(repo / rel)
                for role, rel in REPAIRED_V5_FINAL_BINDING["required_review_receipts"].items()
            }
            sidecar_pass = (
                sidecar.get("status") == "FINAL_PRELAUNCH_REVIEW_GATE_PASS"
                and sidecar.get("card_sha256") == approved_card_sha256
                and sidecar.get("review_receipt_sha256") == expected_hashes
            )
        except (GateError, OSError):
            sidecar_pass = False
    return {
        "status": "PASS" if reviews_pass and sidecar_pass else "WAITING_FOR_REQUIRED_REVIEWS",
        "reviews": results,
        "review_binding_path": sidecar_rel,
        "review_binding_status": "PASS" if sidecar_pass else ("MISSING_OR_INVALID" if reviews_pass else "PENDING_REVIEWS"),
    }


def minimal3199_retry_final_review_gate(repo: Path, approved_card_sha256: str,
                                       run_id: str = MINIMAL3199_RETRY_RUN_ID) -> dict[str, Any]:
    """Require fresh reviews bound to the exact technical-retry FINAL card."""
    binding = (MINIMAL3199_RETRY_BINDINGS.get(run_id) or
               (minimal3350_binding(run_id) if run_id in MINIMAL3350_V2_RUN_IDS else None))
    if binding is None:
        return {"status": "UNSUPPORTED_RUN_ID", "reviews": {}}
    results: dict[str, Any] = {}
    for role, rel in binding["required_review_receipts"].items():
        path = repo / rel
        if not path.is_file():
            results[role] = {"status": "MISSING", "path": rel}
            continue
        try:
            value = load_json(path)
        except GateError as exc:
            results[role] = {"status": "INVALID", "path": rel, "reason": str(exc)}
            continue
        findings = value.get("findings")
        if run_id in MINIMAL3350_V2_RUN_IDS:
            passed = minimal3350_review_receipt_valid(role, value, run_id, approved_card_sha256, repo)
        else:
            passed = (
                value.get("status") == "PASS_PRELAUNCH"
                and value.get("run_id") == run_id
                and value.get("card_sha256") == approved_card_sha256
                and isinstance(findings, dict)
                and all(type(findings.get(key)) is int and findings[key] == 0
                        for key in ("blocker", "major", "required_minor"))
            )
        results[role] = {"status": "PASS" if passed else "FAIL", "path": rel}
    reviews_pass = all(item["status"] == "PASS" for item in results.values())
    sidecar_rel = binding["review_binding"]
    sidecar_path = repo / sidecar_rel
    sidecar_pass = False
    if reviews_pass and sidecar_path.is_file():
        try:
            sidecar = load_json(sidecar_path)
            expected_hashes = {
                role: sha256_file(repo / rel)
                for role, rel in binding["required_review_receipts"].items()
            }
            if run_id in MINIMAL3350_V2_RUN_IDS:
                sidecar_pass = minimal3350_review_sidecar_valid(sidecar, run_id, approved_card_sha256, expected_hashes)
            else:
                sidecar_pass = (
                    sidecar.get("status") == "FINAL_PRELAUNCH_REVIEW_GATE_PASS"
                    and sidecar.get("run_id") == run_id
                    and sidecar.get("card_sha256") == approved_card_sha256
                    and sidecar.get("review_receipt_sha256") == expected_hashes
                )
        except (GateError, OSError):
            sidecar_pass = False
    return {
        "status": "PASS" if reviews_pass and sidecar_pass else "WAITING_FOR_REQUIRED_REVIEWS",
        "reviews": results,
        "review_binding_path": sidecar_rel,
        "review_binding_status": "PASS" if sidecar_pass else ("MISSING_OR_INVALID" if reviews_pass else "PENDING_REVIEWS"),
    }


def validate_minimal3350_control_release_receipts(card: dict[str, Any],
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


def minimal3350_treatment_data_receipt_valid(repo: Path | None, receipt: Any,
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
                or b.get("adapter_sha256") != sha256_file(repo / f"artifacts/{MINIMAL3350_TREATMENT_PACKAGE_ID}/minimal3350_e1_r900_adapter.py")):
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
                or condition.get("R_veh_per_h") != 900 or condition.get("R_window_s") != "[540,1500)"
                or condition.get("U") != 0 or condition.get("X") != 0
                or condition.get("legacy_clean_high_mobility_screen_required_for_release") is not False
                or condition.get("stage6_exploratory_control_disposition_required_for_release") is not True
                or condition.get("required_exploratory_control_disposition") != "LOW_R_BACKGROUND_ACCEPTABLE"):
            return False
    except (GateError, OSError, KeyError, TypeError):
        return False
    return True


def minimal3350_review_receipt_valid(role: str, receipt: Any, run_id: str,
                                     approved_card_sha256: str, repo: Path | None = None) -> bool:
    """Normalize only the three declared MINIMAL3350 receipt schemas, fail closed."""
    if run_id == MINIMAL3350_TREATMENT_RUN_ID and role == "data_provenance":
        return minimal3350_treatment_data_receipt_valid(repo, receipt, run_id, approved_card_sha256)
    if not isinstance(receipt, dict) or receipt.get("run_id") != run_id:
        return False
    if receipt.get("card_sha256") != approved_card_sha256:
        return False
    findings = receipt.get("findings")
    if not isinstance(findings, dict) or any(
            type(findings.get(key)) is not int or findings[key] != 0
            for key in ("blocker", "major", "required_minor")):
        return False
    expected = {
        "engineering": ({"stage6_engineering_prelaunch_review_v1"}, "status", "PASS_PRELAUNCH"),
        "data_provenance": ({"stage6_minimal3350_data_provenance_prelaunch_review_v2",
                             "stage6_minimal3350_data_provenance_prelaunch_review_v3"},
                            "status", "PASS_DATA_PROVENANCE_PRELAUNCH"),
        "scientific": ({"stage6_minimal3350_scientific_prelaunch_review_v1"},
                       "disposition", "PASS_PRELAUNCH"),
    }
    if run_id == MINIMAL3350_TREATMENT_RUN_ID:
        expected = {
            "engineering": ({"stage6_minimal3350_treatment_engineering_prelaunch_review_v1"}, "status", "PASS_PRELAUNCH"),
            "data_provenance": ({"stage6_minimal3350_treatment_data_provenance_prelaunch_review_v1"}, "status", "PASS_DATA_PROVENANCE_PRELAUNCH"),
            "scientific": ({"stage6_minimal3350_treatment_scientific_prelaunch_review_v1"}, "disposition", "PASS_PRELAUNCH"),
        }
    if role not in expected:
        return False
    schemas, field, accepted_value = expected[role]
    return receipt.get("schema") in schemas and receipt.get(field) == accepted_value


def minimal3350_review_sidecar_valid(sidecar: Any, run_id: str, approved_card_sha256: str,
                                     expected_hashes: dict[str, str]) -> bool:
    return (
        isinstance(sidecar, dict)
        and sidecar.get("status") == "FINAL_PRELAUNCH_REVIEW_GATE_PASS"
        and sidecar.get("run_id") == run_id
        and sidecar.get("card_sha256") == approved_card_sha256
        and sidecar.get("review_receipt_sha256") == expected_hashes
    )


def minimal3350_final_review_gate(repo: Path, approved_card_sha256: str,
                                  run_id: str = MINIMAL3350_CTRL_RUN_ID) -> dict[str, Any]:
    """Require engineering, data and science receipts for this exact card hash."""
    if run_id not in MINIMAL3350_V2_RUN_IDS:
        return {"status": "UNSUPPORTED_RUN_ID", "reviews": {}}
    return minimal3199_retry_final_review_gate(repo, approved_card_sha256, run_id)


def _verify_minimal3199_draft(repo: Path, card_path: Path, approved_hash: str,
                              card: dict[str, Any], binding: dict[str, Any], *,
                              allow_prelaunch: bool) -> tuple[dict[str, Any], dict[str, Path]]:
    """Read-only, exact-card preflight for U=X=0 drafts and one authorized control."""
    is_retry_final = binding.get("kind") == "MINIMAL3199_TECH_RETRY_FINAL_CONTROL"
    is_treatment_final = binding.get("kind") == "MINIMAL3199_UX0_TREATMENT_FINAL"
    is_final_control = binding.get("kind") in {"MINIMAL3199_FINAL_CONTROL", "MINIMAL3199_TECH_RETRY_FINAL_CONTROL"}
    if is_final_control or is_treatment_final:
        if (card.get("card_status") != "FINAL_AUTHORIZED_FOR_ONE_START"
                or card.get("execution_authorized") is not True
                or card.get("max_starts") != 1
                or card.get("technical_retries") != 0
                or card.get("approval_required") is not False
                or card.get("progression_allowed") is not False):
            raise GateError("MINIMAL3199_FINAL_STATUS_INVALID")
        resource = card.get("resource_limits", {})
        if (resource.get("status") != "AUTHORIZED_FOR_THIS_RUN"
                or resource.get("scope") != card.get("run_id")
                or resource.get("runtime_s") != binding["authorized_wallclock_s"]
                or resource.get("storage_bytes") != binding["authorized_output_bytes"]):
            raise GateError("MINIMAL3199_FINAL_RESOURCE_AUTHORIZATION_MISMATCH")
        if is_retry_final:
            authorization = card.get("authorization_record")
            if (not isinstance(authorization, dict)
                    or authorization.get("authorization") != binding["authorization_label"]
                    or authorization.get("run_id") != card["run_id"]
                    or authorization.get("exact_card_path") != binding["card_path"]
                    or authorization.get("max_starts") != 1
                    or authorization.get("technical_retries") != 0
                    or authorization.get("wallclock_stop_trigger_s") != binding["authorized_wallclock_s"]
                    or authorization.get("output_size_stop_trigger_bytes_decimal") != binding["authorized_output_bytes"]
                    or authorization.get("output_polling_interval_ms") != 100
                    or authorization.get("polling_overshoot_accepted") is not True
                    or authorization.get("prohibited_runs") != ["treatment", "3350", "seed23", "B", "C", "other_qMain_qRamp"]):
                raise GateError("MINIMAL3199_RETRY_AUTHORIZATION_SCOPE_MISMATCH")
        if is_treatment_final:
            authorization = card.get("authorization_record")
            if (not isinstance(authorization, dict)
                    or authorization.get("authorization") != binding["authorization_label"]
                    or authorization.get("run_id") != card["run_id"]
                    or authorization.get("exact_card_path") != binding["card_path"]
                    or authorization.get("max_starts") != 1
                    or authorization.get("technical_retries") != 0
                    or authorization.get("wallclock_stop_trigger_s") != binding["authorized_wallclock_s"]
                    or authorization.get("output_size_stop_trigger_bytes_decimal") != binding["authorized_output_bytes"]
                    or authorization.get("output_polling_interval_ms") != 100
                    or authorization.get("polling_overshoot_accepted") is not True
                    or authorization.get("prohibited_runs") != ["3350", "seed23", "B", "C", "transition", "other_qMain_qRamp"]):
                raise GateError("MINIMAL3199_TREATMENT_AUTHORIZATION_SCOPE_MISMATCH")
    else:
        if not allow_prelaunch:
            raise GateError("CARD_NOT_EXACTLY_AUTHORIZED")
        if (card.get("card_status") != "DRAFT_NOT_AUTHORIZED"
                or card.get("execution_authorized") is not False
                or card.get("run_command") is not None
                or card.get("max_starts") != 1
                or card.get("technical_retries") != 0
                or card.get("approval_required") is not True):
            raise GateError("MINIMAL3199_DRAFT_STATUS_INVALID")
    if (card.get("pair_id") != "MINIMAL3199_UX0_S17"
            or card.get("condition") != ("A_OPEN_R0_CONTROL" if binding["arm"] == "control"
                                          else "A_OPEN_R720_DELAYED_TREATMENT")
            or card.get("qMain_veh_per_h") != 3199.2
            or card.get("seed") != 17 or card.get("horizon_s") != 2700
            or card.get("step_s") != 1 or card.get("TLS_program") != "A_OPEN"
            or card.get("U") != 0 or card.get("X") != 0
            or card.get("R_veh_per_h") != (0 if binding["arm"] == "control" else 720)
            or card.get("R_window_s") != ("NO_R_SOURCE" if binding["arm"] == "control" else "[540,1500)")):
        raise GateError("MINIMAL3199_CONDITION_MISMATCH")
    card_rel = card_path.relative_to(repo).as_posix()
    if card_rel != binding["card_path"]:
        raise GateError("CARD_PATH_RUN_ID_BINDING_MISMATCH")
    package_root = (repo / binding["package_root"]).resolve(strict=True)
    if not card_path.is_relative_to(package_root):
        raise GateError("CARD_PACKAGE_BINDING_MISMATCH")

    manifest_rel = card.get("input_manifest")
    expected_manifest_rel = "EXECUTION_MANIFEST.json" if is_final_control else "INPUT_MANIFEST.json"
    if manifest_rel != expected_manifest_rel:
        raise GateError("INPUT_MANIFEST_PATH_MISMATCH")
    manifest_path = _resolve_repo_file(repo, f"{binding['package_root']}/{manifest_rel}")
    if sha256_file(manifest_path) != card.get("input_manifest_sha256"):
        raise GateError("INPUT_MANIFEST_HASH_MISMATCH")
    manifest = load_json(manifest_path)
    if (manifest.get("pair_id") != card["pair_id"]
            or manifest.get("design_plan_sha256") != card.get("design_sha256")
            or manifest.get("run_ids", {}).get(binding["arm"]) != card["run_id"]):
        raise GateError("INPUT_MANIFEST_RUN_PROVENANCE_MISMATCH")
    if is_retry_final:
        auth = manifest.get("authorization", {})
        if (auth.get("status") != "AUTHORIZED_EXACTLY_ONE_START"
                or auth.get("execution_authorized") is not True
                or auth.get("run_id") != card["run_id"]
                or auth.get("max_starts") != 1 or auth.get("technical_retries") != 0
                or auth.get("wallclock_stop_limit_s") != binding["authorized_wallclock_s"]
                or auth.get("output_size_stop_limit_bytes_decimal") != binding["authorized_output_bytes"]):
            raise GateError("MINIMAL3199_RETRY_MANIFEST_AUTHORIZATION_MISMATCH")
    if is_treatment_final:
        auth = manifest.get("authorization", {})
        if (auth.get("status") != "AUTHORIZED_EXACTLY_ONE_START_AFTER_REVIEWS"
                or auth.get("execution_authorized") is not True
                or auth.get("run_id") != card["run_id"]
                or auth.get("max_starts") != 1 or auth.get("technical_retries") != 0
                or auth.get("wallclock_stop_limit_s") != binding["authorized_wallclock_s"]
                or auth.get("output_size_stop_limit_bytes_decimal") != binding["authorized_output_bytes"]
                or auth.get("review_gate_required") is not True):
            raise GateError("MINIMAL3199_TREATMENT_MANIFEST_AUTHORIZATION_MISMATCH")
        expected_request_binding = {
            "schema": binding["request_schema"],
            "request_path": binding["start_request_path"],
            "receipt_path": binding["start_request_receipt_path"],
            "status": "PERSISTED_UNSENT",
        }
        if (card.get("guardian_request_binding") != expected_request_binding
                or manifest.get("guardian_request_binding") != expected_request_binding):
            raise GateError("PERSISTED_START_REQUEST_CARD_BINDING_MISMATCH")
    input_package_root = binding.get("input_package_root", binding["package_root"])
    if binding["kind"] in {"MINIMAL3199_TECH_RETRY_DRAFT", "MINIMAL3199_TECH_RETRY_FINAL_CONTROL", "MINIMAL3199_UX0_TREATMENT_FINAL"}:
        source_review = manifest.get("source_prelaunch_review_bundle")
        if (not isinstance(source_review, dict)
                or source_review.get("path") != binding["source_prelaunch_review_bundle_path"]):
            raise GateError("MINIMAL3199_SOURCE_PRELAUNCH_REVIEW_BINDING_MISSING")
        source_review_path = _resolve_repo_file(repo, source_review["path"])
        if sha256_file(source_review_path) != source_review.get("sha256"):
            raise GateError("MINIMAL3199_SOURCE_PRELAUNCH_REVIEW_HASH_MISMATCH")
        validate_minimal3199_runner_hashes(
            manifest, card, card.get("runtime_binding", {}), Path(__file__).resolve(),
            repo, sha256_file(Path(__file__).resolve()))
    if is_final_control:
        prelaunch = manifest.get("source_prelaunch_review_bundle", {})
        receipt_path = _resolve_repo_file(repo, prelaunch.get("path", ""))
        if sha256_file(receipt_path) != prelaunch.get("sha256"):
            raise GateError("PRELAUNCH_REVIEW_RECEIPT_HASH_MISMATCH")
        review_receipt = load_json(receipt_path)
        reviews = review_receipt.get("reviews", {})
        review_root = receipt_path.parent
        review_files = review_receipt.get("review_files", {})
        expected_review_files = {
            "engineering": "ENGINEERING_REVIEW.md",
            "data_provenance": "DATA_PROVENANCE_REVIEW.md",
            "scientific": "SCIENTIFIC_REVIEW.md",
        }
        review_hashes_valid = True
        for role, filename in expected_review_files.items():
            record = review_files.get(filename, {})
            path = _resolve_repo_file(repo, f"{prelaunch['path'].rsplit('/', 1)[0]}/{record.get('path', '')}")
            if (record.get("path") != filename or not path.is_relative_to(review_root)
                    or sha256_file(path) != record.get("sha256")):
                review_hashes_valid = False
        if (review_receipt.get("status") != "MINIMAL3199_CTRL_PRELAUNCH_READY_AWAITING_AUTHORIZATION"
                or not review_hashes_valid
                or any(reviews.get(role, {}).get("disposition") not in {"PASS", "PASS_STATIC_EXECUTION_BINDING", "PASS_BOUNDED_CONTROL_INPUT_ALIGNMENT"}
                       for role in ("engineering", "data_provenance", "scientific"))
                or any(reviews.get(role, {}).get("blocker") != 0
                       or reviews.get(role, {}).get("major") != 0
                       or reviews.get(role, {}).get("required_minor") != 0
                       for role in ("engineering", "data_provenance", "scientific"))):
            raise GateError("PRELAUNCH_REVIEW_RECEIPT_NOT_PASS")
    if (manifest.get("runner_path") != str(Path(__file__).resolve().relative_to(repo).as_posix())
            or manifest.get("runner_sha256") != sha256_file(Path(__file__).resolve())):
        raise GateError("RUNNER_MANIFEST_HASH_MISMATCH")
    code_bindings = manifest.get("validation_code")
    expected_code = {
        "adapter": "scripts/stage6/minimal3199/minimal3199_adapter.py",
        "regression_tests": "tests/test_minimal3199_adapter.py",
        "execution_tests": "tests/test_minimal3199_final_execution.py",
        "treatment_attempt_tests": "tests/test_minimal3199_treatment_attempt.py",
    }
    if not isinstance(code_bindings, dict) or set(code_bindings) != set(expected_code):
        raise GateError("VALIDATION_CODE_BINDING_MISSING")
    for key, rel in expected_code.items():
        spec = code_bindings.get(key)
        if not isinstance(spec, dict) or spec.get("path") != rel:
            raise GateError("VALIDATION_CODE_PATH_MISMATCH")
        code_path = _resolve_repo_file(repo, rel)
        if spec.get("sha256") != sha256_file(code_path):
            raise GateError("VALIDATION_CODE_HASH_MISMATCH")
    design = _resolve_repo_file(repo, manifest.get("design_path", ""))
    if sha256_file(design) != card.get("design_sha256"):
        raise GateError("DESIGN_HASH_MISMATCH")
    method = manifest.get("locked_method", {})
    method_path = _resolve_repo_file(repo, method.get("path", ""))
    if sha256_file(method_path) != method.get("sha256"):
        raise GateError("LOCKED_METHOD_HASH_MISMATCH")

    arm = binding["arm"]
    input_bindings = manifest.get("arm_inputs", {}).get(arm)
    card_inputs, card_hashes = card.get("inputs"), card.get("input_sha256")
    if not isinstance(input_bindings, dict) or not isinstance(card_inputs, dict) or not isinstance(card_hashes, dict):
        raise GateError("CARD_INPUT_BINDINGS_MISSING")
    resolved: dict[str, Path] = {}
    expected_roles = {"demand", "sumocfg", "additional", "output_roles", "network"}
    if (set(input_bindings) - {"path_prefix"}) != expected_roles or set(card_inputs) != expected_roles or set(card_hashes) != expected_roles:
        raise GateError("MINIMAL3199_INPUT_ROLE_SET_MISMATCH")
    for role in sorted(expected_roles):
        spec = input_bindings[role]
        rel = spec.get("path")
        if card_inputs.get(role) != rel or card_hashes.get(role) != spec.get("sha256"):
            raise GateError(f"INPUT_PATH_OR_HASH_BINDING_MISMATCH:{role}")
        if role == "network":
            path = _resolve_repo_file(repo, rel)
        else:
            path = _resolve_repo_file(repo, f"{input_package_root}/{rel}")
        if sha256_file(path) != spec.get("sha256"):
            raise GateError(f"INPUT_HASH_MISMATCH:{role}")
        resolved[role] = path

    if is_treatment_final:
        control = manifest.get("matched_control_binding")
        if not isinstance(control, dict):
            raise GateError("MINIMAL3199_MATCHED_CONTROL_BINDING_MISSING")
        control_card_path = _resolve_repo_file(repo, binding["matched_control_card_path"])
        control_data_path = _resolve_repo_file(repo, binding["matched_control_data_review_path"])
        control_science_path = _resolve_repo_file(repo, binding["matched_control_scientific_review_path"])
        control_manifest_path = _resolve_repo_file(repo, binding["matched_control_output_manifest_path"])
        control_card = load_json(control_card_path)
        control_data = load_json(control_data_path)
        control_science = load_json(control_science_path)
        control_manifest = load_json(control_manifest_path)
        expected_control_demand = control_card.get("input_sha256", {}).get("demand")
        control_input_rel = control_card.get("inputs", {}).get("demand")
        if (sha256_file(control_card_path) != binding["matched_control_card_sha256"]
                or control_card.get("run_id") != "MINIMAL3199_CTRL_S17_TECH_RETRY2"
                or control_card.get("execution_authorized") is not True
                or expected_control_demand != manifest.get("arm_inputs", {}).get("control", {}).get("demand", {}).get("sha256")
                or control_input_rel != "control/demand.rou.xml"
                or sha256_file(control_data_path) != binding["matched_control_data_review_sha256"]
                or control_data.get("disposition") != "PASS_DATA_LIFECYCLE_WITH_RETAINED_CANDIDATE_C_WARNINGS"
                or control_data.get("run_id") != control_card.get("run_id")
                or sha256_file(control_science_path) != binding["matched_control_scientific_review_sha256"]
                or control_science.get("disposition") != "LOW_R_BACKGROUND_ACCEPTABLE"
                or control_science.get("run_id") != control_card.get("run_id")
                or sha256_file(control_manifest_path) != binding["matched_control_output_manifest_sha256"]
                or control_manifest.get("run_id") != control_card.get("run_id")
                or control.get("card_path") != binding["matched_control_card_path"]
                or control.get("card_sha256") != binding["matched_control_card_sha256"]
                or control.get("run_id") != control_card.get("run_id")
                or control.get("demand_input_path") != f"{input_package_root}/control/demand.rou.xml"
                or control.get("demand_input_sha256") != expected_control_demand
                or control.get("output_manifest_sha256") != binding["matched_control_output_manifest_sha256"]
                or control.get("data_review_sha256") != binding["matched_control_data_review_sha256"]
                or control.get("scientific_review_sha256") != binding["matched_control_scientific_review_sha256"]):
            raise GateError("MINIMAL3199_MATCHED_CONTROL_BINDING_MISMATCH")

    counts = manifest.get("class_counts", {})
    arm_counts = counts.get(arm, {})
    for cls in ("U", "X"):
        if arm_counts.get(cls) != {"planned_count": 0, "status": "PASS_ZERO"}:
            raise GateError(f"MINIMAL3199_{cls}_NOT_EXPLICIT_ZERO")
    if arm == "control" and arm_counts.get("R") != {"planned_count": 0, "status": "PASS_ZERO"}:
        raise GateError("MINIMAL3199_CONTROL_R_NOT_EXPLICIT_ZERO")
    if arm == "treatment" and arm_counts.get("R", {}).get("planned_count") != 192:
        raise GateError("MINIMAL3199_TREATMENT_R_COUNT_MISMATCH")

    import xml.etree.ElementTree as ET
    control_path = repo / input_package_root / manifest["arm_inputs"]["control"].get("path_prefix", "control") / "demand.rou.xml"
    treatment_path = repo / input_package_root / manifest["arm_inputs"]["treatment"].get("path_prefix", "treatment") / "demand.rou.xml"
    def strict_route_file(path: Path) -> tuple[dict[str, dict[str, str]], dict[str, dict[str, str]], dict[str, dict[str, str]]]:
        raw = path.read_bytes()
        if raw.startswith(b"\xef\xbb\xbf"):
            raise GateError("MINIMAL3199_ROUTE_UTF8_BOM")
        try:
            decoded = raw.decode("utf-8", errors="strict")
        except UnicodeDecodeError as exc:
            raise GateError("MINIMAL3199_ROUTE_NOT_UTF8") from exc
        if "\x00" in decoded:
            raise GateError("MINIMAL3199_ROUTE_NUL")
        declaration = re.match(r"\s*<\?xml\s+[^?]*encoding\s*=\s*['\"]([^'\"]+)['\"]", decoded, re.IGNORECASE)
        if declaration and declaration.group(1).upper().replace("_", "-") not in {"UTF-8", "UTF8"}:
            raise GateError("MINIMAL3199_ROUTE_ENCODING_DECLARATION")
        expat_parser = expat.ParserCreate(encoding="UTF-8")

        def reject(kind: str):
            def handler(*_args):
                raise GateError(f"MINIMAL3199_ROUTE_UNSUPPORTED_XML:{kind}")
            return handler

        expat_parser.StartDoctypeDeclHandler = reject("DOCTYPE")
        expat_parser.EntityDeclHandler = reject("ENTITY")
        expat_parser.UnparsedEntityDeclHandler = reject("UNPARSED_ENTITY")
        expat_parser.ExternalEntityRefHandler = reject("EXTERNAL_ENTITY")
        expat_parser.CommentHandler = reject("COMMENT")
        expat_parser.ProcessingInstructionHandler = reject("PROCESSING_INSTRUCTION")
        try:
            expat_parser.Parse(raw, True)
        except GateError:
            raise
        except expat.ExpatError as exc:
            raise GateError(f"MINIMAL3199_ROUTE_XML_INVALID:{exc}") from exc
        parser = ET.XMLParser(target=ET.TreeBuilder(insert_comments=True, insert_pis=True))
        try:
            root = ET.parse(path, parser=parser).getroot()
        except ET.ParseError as exc:
            raise GateError(f"MINIMAL3199_ROUTE_XML_INVALID:{exc}") from exc
        if root.tag != "routes" or set(root.attrib) - {"{http://www.w3.org/2001/XMLSchema-instance}noNamespaceSchemaLocation"}:
            raise GateError("MINIMAL3199_ROUTE_ROOT_INVALID")
        definitions: dict[str, dict[str, dict[str, str]]] = {"vType": {}, "route": {}}
        attrs_allowed = {"vType": {"id", "vClass"}, "route": {"id", "edges"},
                         "vehicle": {"id", "type", "route", "depart", "departPos", "departLane", "departSpeed", "speedFactor"}}
        result: dict[str, dict[str, str]] = {}
        last: tuple[int, str] | None = None
        for node in root:
            if not isinstance(node.tag, str) or node.tag not in attrs_allowed or set(node.attrib) != attrs_allowed[node.tag] or list(node):
                raise GateError("MINIMAL3199_ROUTE_NODE_INVALID")
            if (node.text and node.text.strip()) or (node.tail and node.tail.strip()):
                raise GateError("MINIMAL3199_ROUTE_MIXED_CONTENT")
            attrs = dict(node.attrib)
            if node.tag in ("vType", "route"):
                ident = attrs["id"]
                if ident in definitions[node.tag]:
                    raise GateError("MINIMAL3199_ROUTE_DEFINITION_DUPLICATE")
                definitions[node.tag][ident] = attrs
                continue
            try:
                depart_ms = int(round(float(attrs["depart"]) * 1000))
            except (KeyError, ValueError) as exc:
                raise GateError("MINIMAL3199_DEPART_PARSE_ERROR") from exc
            key = (depart_ms, attrs.get("id", ""))
            if last is not None and key < last:
                raise GateError("MINIMAL3199_INPUT_ORDER_INVALID")
            last = key
            if attrs.get("id") in result:
                raise GateError("MINIMAL3199_DUPLICATE_VEHICLE_ID")
            result[attrs["id"]] = attrs
        for attrs in result.values():
            if attrs.get("type") not in definitions["vType"] or attrs.get("route") not in definitions["route"]:
                raise GateError("MINIMAL3199_ROUTE_REFERENCE_UNRESOLVED")
        return definitions["vType"], definitions["route"], result
    cvt, croutes, ctl = strict_route_file(control_path)
    tvt, troutes, trt = strict_route_file(treatment_path)
    if cvt != tvt or croutes != troutes:
        raise GateError("MINIMAL3199_ROUTE_OR_VTYPE_DEFINITIONS_MISMATCH")
    mctl = {k: v for k, v in ctl.items() if k.startswith("M_flow.")}
    mtrt = {k: v for k, v in trt.items() if k.startswith("M_flow.")}
    def common_signature(value: dict[str, str]) -> tuple[str, ...]:
        return tuple(value[k] for k in ("id", "depart", "route", "type", "speedFactor", "departPos", "departLane", "departSpeed"))
    if len(mctl) != 1333 or len(mtrt) != 1333 or set(mctl) != set(mtrt):
        raise GateError("MINIMAL3199_M_ID_OR_COUNT_MISMATCH")
    if any(common_signature(mctl[k]) != common_signature(mtrt[k]) for k in mctl):
        raise GateError("MINIMAL3199_M_ATTRIBUTE_MISMATCH")
    rctl = {k for k in ctl if k.startswith("R_flow.")}
    rtrt = {k for k in trt if k.startswith("R_flow.")}
    if rctl or (set(ctl) - set(mctl)):
        raise GateError("MINIMAL3199_CONTROL_HAS_NON_M_DEMAND")
    if (set(trt) - set(mtrt)) != rtrt or len(rtrt) != 192:
        raise GateError("MINIMAL3199_TREATMENT_ONLY_DEMAND_NOT_R192")
    expected_r = [f"R_flow.{i}" for i in range(192)]
    if set(rtrt) != set(expected_r):
        raise GateError("MINIMAL3199_R_ID_SET_MISMATCH")
    for i, vid in enumerate(expected_r):
        if int(round(float(trt[vid]["depart"]) * 1000)) != 540_000 + i * 5_000:
            raise GateError("MINIMAL3199_R_SCHEDULE_MISMATCH")

    role_source_rel = binding["output_role_source"]
    if card.get("output_role_source", {}).get("path") != role_source_rel:
        raise GateError("OUTPUT_ROLE_SOURCE_BINDING_MISSING")
    role_source = _resolve_repo_file(repo, role_source_rel)
    role_hash = sha256_file(role_source)
    if card["output_role_source"].get("sha256") != role_hash:
        raise GateError("OUTPUT_ROLE_SOURCE_HASH_MISMATCH")
    roles = load_json(role_source).get("required_xml_roles")
    if not isinstance(roles, list) or not roles:
        raise GateError("OUTPUT_ROLE_SOURCE_SCHEMA_INVALID")
    resolved["output_role_source"] = role_source
    resolved["output_role_source_sha256"] = role_hash

    runtime = card.get("runtime_binding")
    resource = card.get("resource_limits")
    if not isinstance(runtime, dict) or not isinstance(resource, dict) or not REQUIRED_RUNTIME_KEYS.issubset(runtime):
        raise GateError("RUNTIME_OR_RESOURCE_BINDING_MISSING")
    runtime_rel = card.get("runtime_binding_path")
    runtime_sidecar = _resolve_repo_file(repo, runtime_rel) if isinstance(runtime_rel, str) else None
    expected_runtime_rel = (binding["runtime_binding_path"] if is_final_control or is_treatment_final or binding["kind"] == "MINIMAL3199_TECH_RETRY_DRAFT"
                            else f"{binding['package_root']}/{arm}/runtime_binding.json")
    if (runtime_sidecar is None or runtime_rel != expected_runtime_rel
            or sha256_file(runtime_sidecar) != card.get("runtime_binding_sha256")
            or load_json(runtime_sidecar) != runtime):
        raise GateError("RUNTIME_BINDING_FILE_HASH_OR_CONTENT_MISMATCH")
    actual_runner_sha = sha256_file(Path(__file__).resolve())
    if runtime.get("guardian_runner_sha256") != actual_runner_sha:
        raise GateError("GUARDIAN_RUNNER_HASH_MISMATCH")
    expected_resource_status = "AUTHORIZED_FOR_THIS_RUN" if (is_final_control or is_treatment_final) else "PROPOSED_NOT_AUTHORIZED"
    if resource.get("scope") != card["run_id"] or resource.get("status") != expected_resource_status:
        raise GateError("MINIMAL3199_RESOURCE_SCOPE_OR_STATUS_MISMATCH")
    runtime_s, runtime_bytes = runtime.get("max_runtime_s"), runtime.get("max_output_bytes")
    if (type(runtime_s) not in (int, float) or not math.isfinite(runtime_s) or runtime_s <= 0
            or type(runtime_bytes) is not int or runtime_bytes <= 0
            or resource.get("runtime_s") != runtime_s or resource.get("storage_bytes") != runtime_bytes):
        raise GateError("INVALID_RESOURCE_LIMIT")
    proposal = runtime.get("resource_proposal", {})
    expected_proposal_status = "AUTHORIZED_FOR_THIS_RUN" if (is_final_control or is_treatment_final) else "PROPOSED_NOT_AUTHORIZED"
    if (proposal.get("status") != expected_proposal_status or proposal.get("scope") != card["run_id"]
            or proposal.get("wallclock_stop_limit_s") != runtime_s
            or proposal.get("output_size_stop_limit_bytes_decimal") != runtime_bytes
            or proposal.get("poll_interval_s") != 0.1 or proposal.get("overshoot_accepted") is not True):
        raise GateError("MINIMAL3199_RESOURCE_PROPOSAL_MISMATCH")
    if (is_final_control or is_treatment_final) and (runtime_s != binding["authorized_wallclock_s"]
            or runtime_bytes != binding["authorized_output_bytes"]):
        raise GateError("MINIMAL3199_AUTHORIZED_LIMITS_MISMATCH")
    resolved["sumo_home"] = verify_sumo_schema_binding(runtime)
    resolved["additional_schema"] = verified_additional_schema(runtime)
    binary = Path(runtime["binary_path"]).resolve(strict=True)
    version_evidence = runtime.get("version_evidence")
    if (not os.access(binary, os.X_OK) or sha256_file(binary) != runtime.get("binary_sha256")
            or str(binary) != EXPECTED_SUMO_PATH
            or runtime.get("binary_sha256") != EXPECTED_SUMO_SHA256
            or runtime.get("binary_version") != EXPECTED_SUMO_VERSION
            or not isinstance(version_evidence, dict)
            or version_evidence.get("binary_path") != str(binary)
            or version_evidence.get("binary_sha256") != runtime.get("binary_sha256")
            or version_evidence.get("reported_version") != EXPECTED_SUMO_VERSION
            or version_evidence.get("query") != "sumo --version (environment probe; no simulation)"):
        raise GateError("BINARY_HASH_MISMATCH")
    resolved["binary"] = binary
    try:
        python_exe = Path(runtime["python_environment"]["executable_path"]).resolve(strict=True)
    except (KeyError, OSError) as exc:
        raise GateError("PYTHON_EXECUTABLE_UNAVAILABLE") from exc
    if sha256_file(python_exe) != runtime["python_environment"].get("executable_sha256"):
        raise GateError("PYTHON_EXECUTABLE_HASH_MISMATCH")
    if str(python_exe) != str(Path(sys.executable).resolve(strict=True)):
        raise GateError("PYTHON_EXECUTABLE_PATH_MISMATCH")
    pyenv = runtime["python_environment"]
    if (pyenv.get("version") != platform.python_version()
            or pyenv.get("implementation") != platform.python_implementation()):
        raise GateError("PYTHON_VERSION_OR_IMPLEMENTATION_MISMATCH")
    package_versions = pyenv.get("package_versions")
    if not isinstance(package_versions, dict):
        raise GateError("PYTHON_PACKAGE_BINDINGS_MISSING")
    for package_name in REQUIRED_PYTHON_PACKAGES:
        try:
            observed = importlib.metadata.version(package_name)
        except importlib.metadata.PackageNotFoundError as exc:
            raise GateError(f"PYTHON_REQUIRED_PACKAGE_MISSING:{package_name}") from exc
        if package_versions.get(package_name) != observed:
            raise GateError(f"PYTHON_PACKAGE_VERSION_MISMATCH:{package_name}")

    output_rel = card.get("output_directory")
    output = _validate_minimal3199_output_path(repo, binding, output_rel, card)
    resolved["output"] = output
    cfg_text = resolved["sumocfg"].read_text(encoding="utf-8")
    add_text = resolved["additional"].read_text(encoding="utf-8")
    if OUTPUT_TOKEN in cfg_text or OUTPUT_TOKEN in add_text:
        raise GateError("MINIMAL3199_OUTPUT_PROVENANCE_MISMATCH")
    resolved["output_roles"] = roles
    if binding["kind"] in {"MINIMAL3199_TECH_RETRY_DRAFT", "MINIMAL3199_TECH_RETRY_FINAL_CONTROL", "MINIMAL3199_UX0_TREATMENT_FINAL"}:
        staged_spec = manifest.get("staged_config")
        if is_treatment_final:
            expected_source = {
                "sumocfg": {"path": "treatment/scenario.sumocfg", "sha256": input_bindings["sumocfg"]["sha256"], "bytes": resolved["sumocfg"].stat().st_size},
                "additional": {"path": "treatment/scenario.add.xml", "sha256": input_bindings["additional"]["sha256"], "bytes": resolved["additional"].stat().st_size},
            }
            prior_output = repo / "data/raw/stage6_minimal3199_existence_20260924_v1/MINIMAL3199_R720_DELAYED_S17/outputs"
        else:
            expected_source = {
                "sumocfg": {"path": "control/scenario.sumocfg",
                             "sha256": "a6be97aba1ab00d6f17ae15788d45765d0a0efca7e297cc1423e4fb720853b1c",
                             "bytes": 2656},
                "additional": {"path": "control/scenario.add.xml",
                                "sha256": "6bd3555c983db506800cab40524767229a3a03c94e893e0ccdc506f95690d8ef",
                                "bytes": 3796},
            }
            prior_output = repo / "data/raw/stage6_minimal3199_existence_20260924_v1/MINIMAL3199_CTRL_S17/outputs"
        staged_cfg_bytes, staged_additional_bytes, transform = stage_minimal3199_inputs(
            resolved["sumocfg"], resolved["additional"], prior_output, output)
        validate_staged_config_binding(staged_spec, card, expected_source, transform)
        if is_retry_final or is_treatment_final:
            staged_cfg = output / "scenario_control.sumocfg"
            staged_additional = output / "scenario_control.add.xml"
            if (sha256_file(staged_cfg) != transform["sumocfg"]["expected_staged_sha256"]
                    or staged_cfg.stat().st_size != transform["sumocfg"]["expected_staged_bytes"]
                    or sha256_file(staged_additional) != transform["additional"]["expected_staged_sha256"]
                    or staged_additional.stat().st_size != transform["additional"]["expected_staged_bytes"]):
                raise GateError("MINIMAL3199_PRESTAGED_FILE_HASH_MISMATCH")
            for staged_path in (staged_cfg, staged_additional):
                staged_text = staged_path.read_text(encoding="utf-8")
                if (str(prior_output.relative_to(repo)) in staged_text
                        or "prepared_rev3/control/scenario.add.xml" in staged_text):
                    raise GateError("MINIMAL3199_PRESTAGED_PATH_RESIDUAL")
        resolved["staged_config_bytes"] = staged_cfg_bytes
        resolved["staged_additional_bytes"] = staged_additional_bytes
        resolved["staged_config_transform"] = transform
    else:
        expected_prefix = f"/{output_rel}/"
        if expected_prefix not in cfg_text or expected_prefix not in add_text:
            raise GateError("MINIMAL3199_OUTPUT_PROVENANCE_MISMATCH")
        if card["run_id"] not in cfg_text:
            raise GateError("MINIMAL3199_RUN_ID_CONFIG_MISMATCH")
    return card, resolved


def bound_sumo_environment(inherited: dict[str, str], sumo_home: Path) -> dict[str, str]:
    """Copy the inherited environment while overriding the version-bound SUMO_HOME."""
    environment = dict(inherited)
    environment["SUMO_HOME"] = str(sumo_home)
    return environment


def _validate_minimal3199_output_path(repo: Path, binding: dict[str, Any], output_rel: str,
                                      card: dict[str, Any]) -> Path:
    """Allow an existing shared pair root, but require this arm's exact output path to be fresh."""
    if output_rel != binding["output_directory"]:
        raise GateError("OUTPUT_DIRECTORY_BINDING_MISMATCH")
    output = repo / output_rel
    output_root = repo / binding["output_root"]
    rel_parts = Path(output_rel).parts
    symlink_component = any(repo.joinpath(*rel_parts[:i]).is_symlink() for i in range(1, len(rel_parts) + 1))
    if output_root.is_symlink() or symlink_component or (output_root.exists() and not output_root.is_dir()):
        raise GateError("OUTPUT_DIRECTORY_ALREADY_EXISTS")
    if binding["kind"] == "MINIMAL3199_TECH_RETRY_FINAL_CONTROL":
        if (not output.is_dir() or output.is_symlink()
                or set(p.name for p in output.iterdir()) != {"scenario_control.sumocfg", "scenario_control.add.xml"}):
            raise GateError("MINIMAL3199_PRESTAGED_OUTPUT_CONTENT_INVALID")
        cfg, add = output / "scenario_control.sumocfg", output / "scenario_control.add.xml"
        if (cfg.is_symlink() or add.is_symlink() or not cfg.is_file() or not add.is_file()
                or cfg.stat().st_size != card.get("staged_config_bytes")
                or sha256_file(cfg) != card.get("staged_config_sha256")
                or add.stat().st_size != card.get("staged_additional_bytes")
                or sha256_file(add) != card.get("staged_additional_sha256")):
            raise GateError("MINIMAL3199_PRESTAGED_OUTPUT_HASH_MISMATCH")
        return output
    if binding["kind"] == "MINIMAL3199_UX0_TREATMENT_FINAL":
        if (not output.is_dir() or output.is_symlink()
                or set(p.name for p in output.iterdir()) != {"scenario_control.sumocfg", "scenario_control.add.xml"}):
            raise GateError("MINIMAL3199_PRESTAGED_OUTPUT_CONTENT_INVALID")
        cfg, add = output / "scenario_control.sumocfg", output / "scenario_control.add.xml"
        if (cfg.is_symlink() or add.is_symlink() or not cfg.is_file() or not add.is_file()
                or cfg.stat().st_size != card.get("staged_config_bytes")
                or sha256_file(cfg) != card.get("staged_config_sha256")
                or add.stat().st_size != card.get("staged_additional_bytes")
                or sha256_file(add) != card.get("staged_additional_sha256")):
            raise GateError("MINIMAL3199_PRESTAGED_OUTPUT_HASH_MISMATCH")
        return output
    if output.exists() or output.parent.exists():
        raise GateError("OUTPUT_DIRECTORY_ALREADY_EXISTS")
    return output


def verify_card(repo: Path, card_path: Path, approved_hash: str, *, allow_prelaunch: bool = False) -> tuple[dict[str, Any], dict[str, Path]]:
    repo = repo.resolve(strict=True)
    card_path = card_path.resolve(strict=True)
    if not card_path.is_relative_to(repo):
        raise GateError("CARD_PATH_OUTSIDE_REPOSITORY")
    actual_card_hash = sha256_file(card_path)
    if actual_card_hash != approved_hash:
        raise GateError("APPROVED_CARD_HASH_MISMATCH")
    card = load_json(card_path)

    minimal_final_binding = MINIMAL3199_FINAL_BINDINGS.get(card.get("run_id"))
    if (minimal_final_binding is not None
            and card_path.relative_to(repo).as_posix() == minimal_final_binding["card_path"]):
        return _verify_minimal3199_draft(repo, card_path, approved_hash, card,
                                         minimal_final_binding, allow_prelaunch=allow_prelaunch)
    if card.get("run_id") in MINIMAL3199_RETRY_BINDINGS:
        card_rel = card_path.relative_to(repo).as_posix()
        retry_final_binding = MINIMAL3199_RETRY_BINDINGS[card["run_id"]]
        if card_rel == retry_final_binding["card_path"]:
            retry_binding = retry_final_binding
        elif card_rel == MINIMAL3199_RETRY_BINDING["card_path"]:
            retry_binding = MINIMAL3199_RETRY_BINDING
        else:
            raise GateError("CARD_PATH_RUN_ID_BINDING_MISMATCH")
        return _verify_minimal3199_draft(repo, card_path, approved_hash, card,
                                         retry_binding, allow_prelaunch=allow_prelaunch)
    minimal_binding = MINIMAL3199_RUN_BINDINGS.get(card.get("run_id"))
    if minimal_binding is not None:
        return _verify_minimal3199_draft(repo, card_path, approved_hash, card,
                                         minimal_binding, allow_prelaunch=allow_prelaunch)

    run_binding = _run_binding(repo, card_path, card)
    package_id = run_binding["package_id"]
    package_root = (repo / "artifacts" / package_id).resolve(strict=True)

    manifest_rel = card.get("input_manifest")
    manifest_digest = card.get("input_manifest_sha256")
    design_digest = card.get("design_sha256")
    if (not isinstance(manifest_rel, str) or Path(manifest_rel).is_absolute()
            or ".." in Path(manifest_rel).parts):
        raise GateError("INPUT_MANIFEST_PATH_MISMATCH")
    manifest_path = _resolve_repo_file(repo, str((package_root / manifest_rel).relative_to(repo)))
    if not isinstance(manifest_digest, str) or sha256_file(manifest_path) != manifest_digest:
        raise GateError("INPUT_MANIFEST_HASH_MISMATCH")
    manifest = load_json(manifest_path)
    if run_binding["kind"] == "TECHNICAL_RETRY" and manifest.get("package_id") != package_id:
        raise GateError("INPUT_MANIFEST_PACKAGE_MISMATCH")
    if run_binding["kind"] == "TECHNICAL_RETRY":
        design_rel = manifest.get("design_path")
        method_rel = manifest.get("locked_method_path")
        if not isinstance(design_rel, str) or not isinstance(method_rel, str):
            raise GateError("DESIGN_OR_METHOD_BINDING_MISSING")
        design_file = _resolve_repo_file(repo, design_rel)
        method_file = _resolve_repo_file(repo, method_rel)
        if not isinstance(design_digest, str) or sha256_file(design_file) != design_digest:
            raise GateError("DESIGN_HASH_MISMATCH")
        if sha256_file(method_file) != manifest.get("locked_method_sha256"):
            raise GateError("LOCKED_METHOD_HASH_MISMATCH")
    else:
        if manifest.get("run_id") != card.get("run_id") or manifest.get("pair_id") != card.get("pair_id"):
            raise GateError("INPUT_MANIFEST_RUN_PROVENANCE_MISMATCH")
        if manifest.get("design_plan_sha256") != card.get("design_sha256"):
            raise GateError("DESIGN_HASH_MISMATCH")

    # Exact authorization boundary: a revised card/hash must be approved by the user.
    if run_binding["kind"] == "TECHNICAL_RETRY":
        retry = card.get("retry_context")
        if (not isinstance(retry, dict) or retry.get("type") != "TECHNICAL_RETRY"
                or retry.get("retry_of_run_id") != RETRY_OF_RUN_ID
                or retry.get("retry_of_card_sha256") != RETRY_OF_CARD_SHA256
                or retry.get("retry_of_reservation_sha256") != RETRY_OF_RESERVATION_SHA256):
            raise GateError("TECHNICAL_RETRY_PARENT_BINDING_MISMATCH")
        prior_card = _resolve_repo_file(repo, RETRY_OF_CARD_PATH)
        prior_reservation = _resolve_repo_file(repo, RETRY_OF_RESERVATION_PATH)
        if (sha256_file(prior_card) != RETRY_OF_CARD_SHA256
                or sha256_file(prior_reservation) != RETRY_OF_RESERVATION_SHA256):
            raise GateError("TECHNICAL_RETRY_PARENT_ARTIFACT_HASH_MISMATCH")
        prior_state = load_json(prior_reservation)
        if (prior_state.get("run_id") != RETRY_OF_RUN_ID
                or prior_state.get("status") != "FINAL_STATUS_HANDED_OFF"
                or prior_state.get("retry_allowed") is not False):
            raise GateError("TECHNICAL_RETRY_PARENT_NOT_CONSUMED")
    is_minimal3350_control = (card.get("run_id") == MINIMAL3350_CTRL_RUN_ID
                              and run_binding.get("kind") == "PAIR_RUN")
    is_minimal3350_treatment = (card.get("run_id") == MINIMAL3350_TREATMENT_RUN_ID
                                and run_binding.get("kind") == "PAIR_RUN")
    is_final_control = is_minimal3350_control or (card.get("run_id") == "PAIR_3199_CTRL_S17"
                        and run_binding.get("card_path") == FINAL_AUTHORIZED_BINDINGS[
                            "PAIR_3199_CTRL_S17"]["card_path"])
    is_final_treatment = (card.get("run_id") == "PAIR_3199_R720_DELAYED_S17"
                          and run_binding.get("card_path") == FINAL_AUTHORIZED_BINDINGS[
                              "PAIR_3199_R720_DELAYED_S17"]["card_path"])
    is_final_repaired_treatment = (
        card.get("run_id") == REPAIRED_V5_ATTEMPT_ID
        and run_binding.get("card_path") == REPAIRED_V5_FINAL_BINDING["card_path"]
    )
    is_final_minimal3350_treatment = (
        is_minimal3350_treatment
        and run_binding.get("card_path") == MINIMAL3350_TREATMENT_BINDING["card_path"]
    )
    is_final_treatment = is_final_treatment or is_final_repaired_treatment or is_final_minimal3350_treatment
    is_prelaunch_only = run_binding.get("card_path") in {
        binding.get("card_path") for binding in PRELAUNCH_ONLY_BINDINGS.values()
    } | {REPAIRED_PRELAUNCH_BINDING["card_path"]}
    expected_status = "FINAL_AUTHORIZED_FOR_ONE_START" if (is_final_control or is_final_treatment) else "AUTHORIZED_EXACT_CARD"
    if is_prelaunch_only:
        if (not allow_prelaunch or card.get("card_status") not in {
                    "PRELAUNCH_READY_AWAITING_AUTHORIZATION", "DRAFT_NOT_AUTHORIZED"}
                or card.get("execution_authorized") is not False):
            raise GateError("CARD_NOT_EXACTLY_AUTHORIZED")
        if card.get("approval_required") is not True:
            raise GateError("PRELAUNCH_APPROVAL_FLAG_INCONSISTENT")
    elif card.get("card_status") != expected_status or card.get("execution_authorized") is not True:
        raise GateError("CARD_NOT_EXACTLY_AUTHORIZED")
    if not is_prelaunch_only and card.get("approval_required") is not False:
        raise GateError("CARD_APPROVAL_FLAG_INCONSISTENT")
    if card.get("max_starts") != 1 or card.get("technical_retries") != 0:
        raise GateError("START_OR_RETRY_LIMIT_NOT_EXACT")
    if card.get("progression_allowed") is not False:
        raise GateError("PROGRESSION_MUST_BE_DISABLED")
    if card.get("horizon_s") != 2700 or card.get("seed") != 17:
        raise GateError("RUN_CONDITION_MISMATCH")
    if (run_binding["kind"] == "PAIR_RUN" and not (is_minimal3350_control or is_minimal3350_treatment)
            and card.get("pair_id") != "PAIR_3199_S17"):
        raise GateError("PAIR_ID_BINDING_MISMATCH")
    if is_minimal3350_control and card.get("pair_id") != "MINIMAL3350_UX0_S17":
        raise GateError("MINIMAL3350_PAIR_ID_BINDING_MISMATCH")
    if is_minimal3350_treatment and card.get("pair_id") != "MINIMAL3350_UX0_S17":
        raise GateError("MINIMAL3350_TREATMENT_PAIR_ID_BINDING_MISMATCH")
    if is_prelaunch_only or is_final_treatment:
        contract = card.get("witness_contract")
        if (not isinstance(contract, dict)
                or contract.get("path") != STAGE6_WITNESS_CONTRACT_PATH
                or contract.get("sha256") != STAGE6_WITNESS_CONTRACT_SHA256):
            raise GateError("WITNESS_CONTRACT_BINDING_MISMATCH")
        contract_path = _resolve_repo_file(repo, STAGE6_WITNESS_CONTRACT_PATH)
        if sha256_file(contract_path) != STAGE6_WITNESS_CONTRACT_SHA256:
            raise GateError("WITNESS_CONTRACT_HASH_MISMATCH")
        if (card.get("treatment_release_gate") != "STAGE6_EXPLORATORY_RAMP_INDUCED_WITNESS_CONTRACT_ONLY"
                or card.get("legacy_clean_high_mobility_screen_required_for_release") is not False
                or card.get("stage6_exploratory_control_disposition_required_for_release") is not True
                or card.get("stage6_exploratory_control_disposition_required") != "LOW_R_BACKGROUND_ACCEPTABLE"):
            raise GateError("OLD_LOW_R_GATE_MUST_NOT_RELEASE_TREATMENT")
        markers = card.get("required_event_timeline_markers")
        expected_markers = [
            "R_demand_activation", "first_scheduled_R_departure", "first_actual_R_departure",
            "first_R_arrival_near_merge", "first_meaningful_merge_exposure",
            "first_M_deterioration", "State1_onset",
        ]
        if markers != expected_markers:
            raise GateError("TREATMENT_EVENT_TIMELINE_MARKERS_MISMATCH")
    if is_final_control and is_minimal3350_control:
        authorization = card.get("authorization_record")
        if (not isinstance(authorization, dict)
                or authorization.get("authorization") != "USER_AUTHORIZED_CONDITIONAL_MINIMAL3350_CONTROL_START_AFTER_THREE_REVIEWS"
                or authorization.get("run_id") != MINIMAL3350_CTRL_RUN_ID
                or authorization.get("exact_card_path") != run_binding["card_path"]
                or authorization.get("max_starts") != 1
                or authorization.get("technical_retries") != 0
                or authorization.get("wallclock_stop_trigger_s") != run_binding["authorized_wallclock_s"]
                or authorization.get("output_size_stop_trigger_bytes_decimal") != run_binding["authorized_output_bytes"]
                or authorization.get("output_polling_interval_ms") != 100
                or authorization.get("polling_overshoot_accepted") is not True
                or authorization.get("prohibited_runs") != ["treatment", "seed23", "B", "C", "other_qMain_qRamp"]):
            raise GateError("MINIMAL3350_CONTROL_AUTHORIZATION_SCOPE_MISMATCH")
    if is_final_minimal3350_treatment:
        authorization = card.get("authorization_record")
        if (not isinstance(authorization, dict)
                or authorization.get("authorization") != "USER_AUTHORIZED_CONDITIONAL_ONE_E1_QRAMP900_START_AFTER_FRESH_THREE_REVIEWS"
                or authorization.get("run_id") != MINIMAL3350_TREATMENT_RUN_ID
                or authorization.get("exact_card_path") != run_binding["card_path"]
                or authorization.get("max_starts") != 1
                or authorization.get("technical_retries") != 0
                or authorization.get("wallclock_stop_trigger_s") != run_binding["authorized_wallclock_s"]
                or authorization.get("output_size_stop_trigger_bytes_decimal") != run_binding["authorized_output_bytes"]
                or authorization.get("output_polling_interval_ms") != 100
                or authorization.get("polling_overshoot_accepted") is not True
                or authorization.get("prohibited_runs") != ["R1080", "higher_qMain", "seed23", "B", "C"]):
            raise GateError("MINIMAL3350_TREATMENT_AUTHORIZATION_SCOPE_MISMATCH")
    elif is_final_control:
        authorization = card.get("authorization_record")
        if (not isinstance(authorization, dict)
                or authorization.get("authorization") != "USER_AUTHORIZED_EXACTLY_ONE_CONTROL_START"
                or authorization.get("run_id") != "PAIR_3199_CTRL_S17"
                or authorization.get("max_starts") != 1
                or authorization.get("technical_retries") != 0
                or authorization.get("prohibited_runs") != [
                    "PAIR_3199_R720_DELAYED_S17", "seed23", "B", "C", "other_qMain_qRamp"]):
            raise GateError("FINAL_CARD_AUTHORIZATION_SCOPE_MISMATCH")
    if is_final_treatment and not (is_final_repaired_treatment or is_final_minimal3350_treatment):
        authorization = card.get("authorization_record")
        if (not isinstance(authorization, dict)
                or authorization.get("authorization") != "USER_AUTHORIZED_EXACTLY_ONE_TREATMENT_START"
                or authorization.get("run_id") != "PAIR_3199_R720_DELAYED_S17"
                or authorization.get("exact_card_path") != run_binding["card_path"]
                or authorization.get("max_starts") != 1
                or authorization.get("technical_retries") != 0
                or authorization.get("wallclock_stop_trigger_s") != 120
                or authorization.get("output_size_stop_trigger_bytes_decimal") != 90_000_000
                or authorization.get("output_polling_interval_ms") != 100
                or authorization.get("polling_overshoot_accepted") is not True
                or authorization.get("prohibited_runs") != [
                    "seed23", "B", "C", "transition", "other_qMain_qRamp"]):
            raise GateError("FINAL_TREATMENT_AUTHORIZATION_SCOPE_MISMATCH")
    if is_final_repaired_treatment:
        authorization = card.get("authorization_record")
        if (not isinstance(authorization, dict)
                or authorization.get("authorization") != "USER_AUTHORIZED_EXACTLY_ONE_REPAIRED_TREATMENT_START"
                or authorization.get("scenario_id") != "PAIR_3199_R720_DELAYED_S17"
                or authorization.get("run_id") != REPAIRED_V5_ATTEMPT_ID
                or authorization.get("attempt_id") != REPAIRED_V5_ATTEMPT_ID
                or authorization.get("execution_id") != card.get("execution_id")
                or authorization.get("exact_card_path") != run_binding["card_path"]
                or authorization.get("max_starts") != 1
                or authorization.get("technical_retries") != 0
                or authorization.get("wallclock_stop_trigger_s") != REPAIRED_V5_FINAL_BINDING["authorized_wallclock_s"]
                or authorization.get("output_size_stop_trigger_bytes_decimal") != REPAIRED_V5_FINAL_BINDING["authorized_output_bytes"]
                or authorization.get("output_polling_interval_ms") != 100
                or authorization.get("polling_overshoot_accepted") is not True
                or authorization.get("prohibited_runs") != [
                    "seed23", "B", "C", "transition", "other_qMain_qRamp"]):
            raise GateError("REPAIRED_TREATMENT_AUTHORIZATION_SCOPE_MISMATCH")

    inmap = card.get("control_inputs") if run_binding["kind"] == "TECHNICAL_RETRY" else card.get("inputs")
    hashes = card.get("control_input_sha256") if run_binding["kind"] == "TECHNICAL_RETRY" else card.get("input_sha256")
    if not isinstance(inmap, dict) or not isinstance(hashes, dict):
        raise GateError("CARD_INPUT_BINDINGS_MISSING")
    resolved: dict[str, Path] = {}
    for role, expected_rel in REQUIRED_INPUTS.items():
        if is_minimal3350_control:
            expected_rel = run_binding["input_paths"][role]
        elif role in {"sumocfg", "demand", "additional"} and run_binding["kind"] == "PAIR_RUN":
            expected_rel = f"inputs/{'control' if card['run_id'] == 'PAIR_3199_CTRL_S17' else 'treatment'}/" + {
                "sumocfg": "scenario.sumocfg", "demand": "demand.rou.xml", "additional": "scenario.add.xml"
            }[role]
        if role == "network" and run_binding["kind"] == "PAIR_RUN":
            expected_rel = "artifacts/stage6_baseline_localization_20260921_v1/LOC_M3350_S17/engineering/build_attempts/TV_BUILD01/network.net.xml"
        if inmap.get(role) != expected_rel:
            raise GateError(f"INPUT_PATH_BINDING_MISMATCH:{role}")
        if role in {"sumocfg", "demand", "additional"} and run_binding["kind"] == "TECHNICAL_RETRY":
            p = _resolve_repo_file(repo, str((package_root / expected_rel).relative_to(repo)))
        elif (run_binding["kind"] == "PAIR_RUN" and role in {"sumocfg", "demand", "additional", "output_roles"}
              and expected_rel.startswith("inputs/")):
            p = _resolve_repo_file(repo, str((package_root / expected_rel).relative_to(repo)))
        else:
            p = _resolve_repo_file(repo, expected_rel)
        expected_digest = hashes.get(role)
        if not isinstance(expected_digest, str) or len(expected_digest) != 64:
            raise GateError(f"INPUT_HASH_BINDING_MISSING:{role}")
        if sha256_file(p) != expected_digest:
            raise GateError(f"INPUT_HASH_MISMATCH:{role}")
        resolved[role] = p

    role_binding = card.get("output_role_source")
    expected_role_source = (LEGACY_OUTPUT_ROLE_SOURCE if run_binding["kind"] == "TECHNICAL_RETRY" else
                            run_binding.get("output_role_source") if is_minimal3350_control else
                            run_binding.get("output_role_source") or
                            PAIR_OUTPUT_ROLE_SOURCE.format(arm=("control" if card["run_id"] == "PAIR_3199_CTRL_S17" else "treatment")))
    if not isinstance(role_binding, dict) or role_binding.get("path") != expected_role_source:
        raise GateError("OUTPUT_ROLE_SOURCE_BINDING_MISSING")
    role_source = _resolve_repo_file(repo, expected_role_source)
    role_source_hash = sha256_file(role_source)
    if role_binding.get("sha256") != role_source_hash:
        raise GateError("OUTPUT_ROLE_SOURCE_HASH_MISMATCH")
    if run_binding["kind"] == "PAIR_RUN" and not is_minimal3350_control:
        expected_roles_rel = f"inputs/{'control' if card['run_id'] == 'PAIR_3199_CTRL_S17' else 'treatment'}/output_roles.json"
        if inmap.get("output_roles") != expected_roles_rel or hashes.get("output_roles") != role_source_hash:
            raise GateError("OUTPUT_ROLES_INPUT_PROVENANCE_MISMATCH")
    role_data = load_json(role_source)
    roles = role_data.get("required_xml_roles")
    if not isinstance(roles, list) or role_data.get("required_role_count") != len(roles):
        raise GateError("OUTPUT_ROLE_SOURCE_SCHEMA_INVALID")
    names = []
    for item in roles:
        if not isinstance(item, dict) or not isinstance(item.get("role"), str):
            raise GateError("OUTPUT_ROLE_RECORD_INVALID")
        role_name = item["role"]
        if Path(role_name).name != role_name or role_name in {".", ".."}:
            raise GateError("OUTPUT_ROLE_PATH_UNSAFE")
        names.append(role_name)
    if len(set(names)) != len(names):
        raise GateError("OUTPUT_ROLE_DUPLICATE")
    resolved["output_role_source"] = role_source
    resolved["output_roles"] = roles
    resolved["output_role_source_sha256"] = role_source_hash

    resource = card.get("resource_limits")
    runtime = card.get("runtime_binding")
    if not isinstance(resource, dict) or not isinstance(runtime, dict):
        raise GateError("RUNTIME_OR_RESOURCE_BINDING_MISSING")
    if not REQUIRED_RUNTIME_KEYS.issubset(runtime):
        raise GateError("RUNTIME_BINDING_FIELDS_MISSING")
    legacy_runner_sha = "abba1b31970a4690a262881cec1ea0957b2386c65a20c4105a711cebf3c80154"
    actual_runner_sha = sha256_file(Path(__file__).resolve())
    if (runtime.get("guardian_runner_sha256") != actual_runner_sha
            and not (run_binding["kind"] == "TECHNICAL_RETRY" and runtime.get("guardian_runner_sha256") == legacy_runner_sha)):
        raise GateError("GUARDIAN_RUNNER_HASH_MISMATCH")
    if run_binding["kind"] == "PAIR_RUN":
        runtime_rel = card.get("runtime_binding_path")
        runtime_hash = card.get("runtime_binding_sha256")
        if not isinstance(runtime_rel, str) or not isinstance(runtime_hash, str):
            raise GateError("RUNTIME_BINDING_FILE_MISSING")
        expected_runtime_rel = run_binding.get(
            "runtime_binding_path",
            f"artifacts/{package_id}/runtime_bindings/{card['run_id']}.json")
        if runtime_rel != expected_runtime_rel:
            raise GateError("RUNTIME_BINDING_PATH_MISMATCH")
        runtime_file = _resolve_repo_file(repo, runtime_rel)
        if sha256_file(runtime_file) != runtime_hash:
            raise GateError("RUNTIME_BINDING_FILE_HASH_MISMATCH")
        if load_json(runtime_file) != runtime:
            raise GateError("RUNTIME_BINDING_FILE_CONTENT_MISMATCH")
        resolved["runtime_binding_file"] = runtime_file
    resolved["sumo_home"] = verify_sumo_schema_binding(runtime)
    resolved["additional_schema"] = verified_additional_schema(runtime)
    max_runtime = runtime["max_runtime_s"]
    max_bytes = runtime["max_output_bytes"]
    if (type(max_runtime) not in (int, float) or not math.isfinite(max_runtime)
            or max_runtime <= 0 or type(max_bytes) is not int or max_bytes <= 0):
        raise GateError("INVALID_RESOURCE_LIMIT")
    if resource.get("runtime_s") != max_runtime or resource.get("storage_bytes") != max_bytes:
        raise GateError("RUNTIME_RESOURCE_BINDING_MISMATCH")
    if run_binding["kind"] == "PAIR_RUN":
        proposal = runtime.get("resource_proposal")
        if (resource.get("scope") != card["run_id"] or not isinstance(proposal, dict)
                or proposal.get("scope") != card["run_id"]):
            raise GateError("PAIR_RESOURCE_SCOPE_MISMATCH")
        expected_resource_status = "PROPOSED_NOT_AUTHORIZED" if is_prelaunch_only else "AUTHORIZED_FOR_THIS_RUN"
        if resource.get("status") != expected_resource_status:
            raise GateError("PAIR_RESOURCE_LIMITS_NOT_AUTHORIZED")
        if is_prelaunch_only and proposal.get("status") != "PROPOSED_NOT_AUTHORIZED":
            raise GateError("PRELAUNCH_RESOURCE_PROPOSAL_STATUS_MISMATCH")
        if is_final_control and (proposal.get("status") != "AUTHORIZED_FOR_THIS_RUN"
                or proposal.get("wallclock_stop_limit_s") != max_runtime
                or proposal.get("output_size_stop_limit_bytes_decimal") != max_bytes
                or proposal.get("enforcement") != "100ms_polled_stop_trigger_with_possible_overshoot_not_hard_quota"):
            raise GateError("FINAL_RESOURCE_AUTHORIZATION_MISMATCH")
        if is_final_minimal3350_treatment and (proposal.get("status") != "AUTHORIZED_FOR_THIS_RUN"
                or proposal.get("wallclock_stop_limit_s") != max_runtime
                or proposal.get("output_size_stop_limit_bytes_decimal") != max_bytes
                or proposal.get("enforcement") != "100ms_polled_stop_trigger_with_possible_overshoot_not_hard_quota"
                or max_runtime != 90 or max_bytes != 75_000_000):
            raise GateError("MINIMAL3350_TREATMENT_RESOURCE_AUTHORIZATION_MISMATCH")
        if is_final_treatment and not is_final_minimal3350_treatment and (proposal.get("status") != "AUTHORIZED_FOR_THIS_RUN"
                or proposal.get("wallclock_stop_limit_s") != max_runtime
                or proposal.get("output_size_stop_limit_bytes_decimal") != max_bytes
                or proposal.get("enforcement") != "100ms_polled_stop_trigger_with_possible_overshoot_not_hard_quota"
                or (not is_final_repaired_treatment and (max_runtime != 120 or max_bytes != 90_000_000))
                or (is_final_repaired_treatment and (
                    max_runtime != REPAIRED_V5_FINAL_BINDING["authorized_wallclock_s"]
                    or max_bytes != REPAIRED_V5_FINAL_BINDING["authorized_output_bytes"]))):
            raise GateError("FINAL_TREATMENT_RESOURCE_AUTHORIZATION_MISMATCH")

    # Match the approved project venv exactly; do not silently use system Python.
    pyenv = runtime.get("python_environment")
    if not isinstance(pyenv, dict):
        raise GateError("PYTHON_ENVIRONMENT_BINDING_MISSING")
    executable = Path(sys.executable).absolute()
    if pyenv.get("executable_path") != str(executable):
        raise GateError("PYTHON_EXECUTABLE_PATH_MISMATCH")
    try:
        executable_hash = sha256_file(executable.resolve(strict=True))
    except OSError as exc:
        raise GateError("PYTHON_EXECUTABLE_UNAVAILABLE") from exc
    if pyenv.get("executable_sha256") != executable_hash:
        raise GateError("PYTHON_EXECUTABLE_HASH_MISMATCH")
    if pyenv.get("version") != platform.python_version() or pyenv.get("implementation") != platform.python_implementation():
        raise GateError("PYTHON_VERSION_OR_IMPLEMENTATION_MISMATCH")
    package_versions = pyenv.get("package_versions")
    if not isinstance(package_versions, dict):
        raise GateError("PYTHON_PACKAGE_BINDINGS_MISSING")
    for name in REQUIRED_PYTHON_PACKAGES:
        try:
            observed = importlib.metadata.version(name)
        except importlib.metadata.PackageNotFoundError as exc:
            raise GateError(f"PYTHON_REQUIRED_PACKAGE_MISSING:{name}") from exc
        if package_versions.get(name) != observed:
            raise GateError(f"PYTHON_PACKAGE_VERSION_MISMATCH:{name}")

    binary = Path(runtime["binary_path"])
    if not binary.is_absolute():
        raise GateError("BINARY_PATH_MUST_BE_ABSOLUTE")
    try:
        binary = binary.resolve(strict=True)
    except OSError as exc:
        raise GateError("BINARY_NOT_FOUND") from exc
    if not binary.is_file() or not os.access(binary, os.X_OK):
        raise GateError("BINARY_NOT_EXECUTABLE")
    binary_hash = sha256_file(binary)
    if binary_hash != runtime["binary_sha256"]:
        raise GateError("BINARY_HASH_MISMATCH")
    version_evidence = runtime.get("version_evidence")
    if (str(binary) != EXPECTED_SUMO_PATH or binary_hash != EXPECTED_SUMO_SHA256
            or runtime.get("binary_version") != EXPECTED_SUMO_VERSION
            or not isinstance(version_evidence, dict)
            or version_evidence.get("binary_path") != str(binary)
            or version_evidence.get("binary_sha256") != binary_hash
            or version_evidence.get("reported_version") != EXPECTED_SUMO_VERSION
            or version_evidence.get("query") != "sumo --version (environment probe; no simulation)"):
        raise GateError("SUMO_VERSION_EVIDENCE_MISMATCH")
    resolved["binary"] = binary

    output_rel = card.get("output_directory")
    expected_output_rel = run_binding["output_directory"]
    if not isinstance(output_rel, str) or not output_rel:
        raise GateError("OUTPUT_DIRECTORY_BINDING_MISSING")
    if output_rel != expected_output_rel:
        raise GateError("OUTPUT_DIRECTORY_BINDING_MISMATCH")
    output = (repo / output_rel).resolve(strict=False)
    outputs_unresolved = ((repo / "artifacts" / package_id / "outputs") if run_binding["kind"] == "TECHNICAL_RETRY"
                          else (repo / run_binding.get("output_root", "data/raw/stage6_bounded_pair_20260923_v1")))
    if outputs_unresolved.is_symlink() or (outputs_unresolved.exists() and not outputs_unresolved.is_dir()):
        raise GateError("PACKAGE_OUTPUTS_ROOT_UNSAFE")
    outputs_root = outputs_unresolved.resolve(strict=False)
    valid_parent = (output.parent == outputs_root and output.name == card["run_id"]
                    if run_binding["kind"] == "TECHNICAL_RETRY"
                    else output.parent == outputs_root / card["run_id"] and output.name == "outputs")
    if not output.is_relative_to(outputs_root) or not valid_parent:
        raise GateError("OUTPUT_DIRECTORY_OUTSIDE_EXCLUSIVE_RUN_OUTPUTS")
    if output.exists():
        raise GateError("OUTPUT_DIRECTORY_ALREADY_EXISTS")
    if run_binding["kind"] == "PAIR_RUN" and output.parent.exists():
        raise GateError("OUTPUT_RUN_ROOT_ALREADY_EXISTS")
    resolved["output"] = output

    # Bind all simulator destinations to the exclusive output path; no unresolved token.
    cfg_text = resolved["sumocfg"].read_text(encoding="utf-8")
    add_text = resolved["additional"].read_text(encoding="utf-8")
    if run_binding["kind"] == "TECHNICAL_RETRY" and (cfg_text.count(OUTPUT_TOKEN) != 8 or add_text.count(OUTPUT_TOKEN) != 12):
        raise GateError("OUTPUT_PLACEHOLDER_COUNT_MISMATCH")
    if run_binding["kind"] == "PAIR_RUN":
        if OUTPUT_TOKEN in cfg_text or OUTPUT_TOKEN in add_text:
            raise GateError("PAIR_CONFIG_HAS_UNRESOLVED_OUTPUT_PLACEHOLDER")
        expected_output_text = f"/{output_rel}/"
        for text in (cfg_text, add_text):
            if expected_output_text not in text:
                raise GateError("PAIR_OUTPUT_PROVENANCE_MISMATCH")
    if is_minimal3350_control:
        if (card.get("qMain_veh_per_h") != 3350.4 or card.get("R_veh_per_h") != 0
                or card.get("U") != 0 or card.get("X") != 0
                or card.get("class_counts") != {
                    "M": {"planned_count": 1396, "status": "BOUND"},
                    "R": {"planned_count": 0, "status": "PASS_ZERO"},
                    "U": {"planned_count": 0, "status": "PASS_ZERO"},
                    "X": {"planned_count": 0, "status": "PASS_ZERO"}}):
            raise GateError("MINIMAL3350_CONTROL_CONDITION_OR_ZERO_LEDGER_MISMATCH")
        if (f"/{output_rel}/" not in cfg_text or f"/{output_rel}/" not in add_text
                or card.get("input_sha256", {}).get("demand") != sha256_file(resolved["demand"])):
            raise GateError("MINIMAL3350_CONTROL_OUTPUT_OR_DEMAND_BINDING_MISMATCH")
        try:
            adapter_path = repo / "scripts/stage6/minimal3350/minimal3350_control_adapter.py"
            adapter_spec = importlib.util.spec_from_file_location("stage6_minimal3350_adapter_runtime", adapter_path)
            if adapter_spec is None or adapter_spec.loader is None:
                raise ImportError("minimal3350 adapter module spec unavailable")
            adapter_module = importlib.util.module_from_spec(adapter_spec)
            adapter_spec.loader.exec_module(adapter_module)
            common_binding = card.get("common_m_manifest")
            if not isinstance(common_binding, dict) or not isinstance(common_binding.get("path"), str):
                raise ValueError("common M demand manifest binding missing")
            common_path = _resolve_repo_file(repo, common_binding["path"])
            demand_check = adapter_module.validate_control_card(card, resolved["demand"], common_path, repo)
        except (ImportError, OSError, ValueError, KeyError) as exc:
            raise GateError(f"MINIMAL3350_CONTROL_DEMAND_INVARIANT_FAILED:{exc}") from exc
        if demand_check.get("m_count") != 1396:
            raise GateError("MINIMAL3350_CONTROL_DEMAND_SCHEDULE_MISMATCH")
    if is_minimal3350_treatment:
        validate_minimal3350_control_release_binding(repo, card)
        if (card.get("qMain_veh_per_h") != 3350.4 or card.get("R_veh_per_h") != 900
                or card.get("R_window_s") != "[540,1500)" or card.get("U") != 0 or card.get("X") != 0
                or card.get("class_counts") != {
                    "M": {"planned_count": 1396, "status": "BOUND"},
                    "R": {"planned_count": 240, "status": "BOUND"},
                    "U": {"planned_count": 0, "status": "PASS_ZERO"},
                    "X": {"planned_count": 0, "status": "PASS_ZERO"}}):
            raise GateError("MINIMAL3350_TREATMENT_CONDITION_OR_ZERO_LEDGER_MISMATCH")
        if (f"/{output_rel}/" not in cfg_text or f"/{output_rel}/" not in add_text
                or card.get("input_sha256", {}).get("demand") != sha256_file(resolved["demand"])):
            raise GateError("MINIMAL3350_TREATMENT_OUTPUT_OR_DEMAND_BINDING_MISMATCH")
        try:
            adapter_path = repo / f"artifacts/{MINIMAL3350_TREATMENT_PACKAGE_ID}/minimal3350_e1_r900_adapter.py"
            adapter_spec = importlib.util.spec_from_file_location("stage6_minimal3350_treatment_adapter_runtime", adapter_path)
            if adapter_spec is None or adapter_spec.loader is None:
                raise ImportError("minimal3350 treatment adapter module spec unavailable")
            adapter_module = importlib.util.module_from_spec(adapter_spec)
            adapter_spec.loader.exec_module(adapter_module)
            common_binding = card.get("common_m_manifest")
            if not isinstance(common_binding, dict) or not isinstance(common_binding.get("path"), str):
                raise ValueError("common M demand manifest binding missing")
            common_path = _resolve_repo_file(repo, common_binding["path"])
            r_source_binding = card.get("r_vehicle_source")
            if not isinstance(r_source_binding, dict) or not isinstance(r_source_binding.get("path"), str):
                raise ValueError("R vehicle source binding missing")
            r_source = _resolve_repo_file(repo, r_source_binding["path"])
            matched = card.get("matched_control_binding")
            if not isinstance(matched, dict) or not isinstance(matched.get("demand_input_path"), str):
                raise ValueError("matched control demand binding missing")
            control_demand = _resolve_repo_file(repo, matched["demand_input_path"])
            if sha256_file(control_demand) != matched.get("demand_input_sha256"):
                raise ValueError("matched control demand hash mismatch")
            demand_check = adapter_module.validate_treatment_card(
                card, resolved["demand"], common_path, r_source, repo, control_demand)
        except (ImportError, OSError, ValueError, KeyError) as exc:
            raise GateError(f"MINIMAL3350_TREATMENT_DEMAND_INVARIANT_FAILED:{exc}") from exc
        if demand_check.get("m_count") != 1396 or demand_check.get("r_count") != 240:
            raise GateError("MINIMAL3350_TREATMENT_DEMAND_SCHEDULE_MISMATCH")
    return card, resolved


def _write_exclusive(path: Path, data: bytes) -> None:
    fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    with os.fdopen(fd, "wb") as f:
        f.write(data)
        f.flush()
        os.fsync(f.fileno())


def _atomic_status(path: Path, data: bytes) -> None:
    temp = path.with_name(path.name + f".tmp.{os.getpid()}")
    _write_exclusive(temp, data)
    os.replace(temp, path)
    _fsync_directory(path.parent)


def make_plan(repo: Path, card_path: Path, approved_hash: str) -> dict[str, Any]:
    card, files = verify_card(repo, card_path, approved_hash, allow_prelaunch=True)
    output = files["output"]
    result = {
        "status": "PREFLIGHT_PASS_NO_PROCESS_STARTED",
        "run_id": card["run_id"],
        "approved_card_sha256": approved_hash,
        "output_directory": str(output),
        "binary_path": str(files["binary"]),
        "binary_sha256": card["runtime_binding"]["binary_sha256"],
        "binary_version": card["runtime_binding"]["binary_version"],
        "sumo_home": card["runtime_binding"]["sumo_home"],
        "additional_schema_path": card["runtime_binding"]["additional_schema_path"],
        "additional_schema_sha256": card["runtime_binding"]["additional_schema_sha256"],
        "python_executable": card["runtime_binding"]["python_environment"]["executable_path"],
        "python_version": card["runtime_binding"]["python_environment"]["version"],
        "guardian_runner_sha256": card["runtime_binding"]["guardian_runner_sha256"],
        "output_role_source": str(files["output_role_source"]),
        "output_role_source_sha256": files["output_role_source_sha256"],
        "max_starts": card.get("max_starts", 1),
        "technical_retries": 0,
        "simulator_process_started": False,
        "launch_authorized": card.get("execution_authorized") is True,
    }
    if card.get("run_id") == REPAIRED_V5_ATTEMPT_ID:
        result["launch_review_gate"] = repaired_final_review_gate(repo.resolve(strict=True), approved_hash)
        result["launchable_now"] = result["launch_authorized"] and result["launch_review_gate"]["status"] == "PASS"
    elif card.get("run_id") in MINIMAL3199_RETRY_BINDINGS and card.get("card_status") == "FINAL_AUTHORIZED_FOR_ONE_START":
        result["launch_review_gate"] = minimal3199_retry_final_review_gate(
            repo.resolve(strict=True), approved_hash, card["run_id"])
        result["launchable_now"] = result["launch_authorized"] and result["launch_review_gate"]["status"] == "PASS"
        if card.get("run_id") == MINIMAL3199_TREATMENT_ATTEMPT1_RUN_ID:
            persisted = validate_persisted_treatment_start_request(
                repo.resolve(strict=True), card_path, approved_hash, card, files, output)
            result["persisted_start_request"] = {
                "status": "PASS_UNSENT",
                "request_schema": card["guardian_request_binding"]["schema"],
                "request_sha256": persisted["request_sha256"],
                "receipt_path": persisted["request_receipt_path"],
                "dispatched": False,
            }
        if result["launchable_now"]:
            reservation = (repo / MINIMAL3199_RETRY_BINDINGS[card["run_id"]]["consumption_directory"]
                          / f"{card['run_id']}.json")
            start = prepare_minimal3199_guardian_start(
                repo, card_path, approved_hash, card, files, output, reservation)
            result["guardian_request_validation"] = {
                "status": "PASS", "request_schema": start["request_schema"],
                "request_sha256": hashlib.sha256(canonical_json_bytes(start)).hexdigest(),
                "simulator_process_started": False,
            }
        else:
            result["guardian_request_validation"] = {"status": "BLOCKED_BY_REVIEW_GATE"}
    elif card.get("run_id") in MINIMAL3350_V2_RUN_IDS:
        gate = minimal3350_final_review_gate(repo.resolve(strict=True), approved_hash, card["run_id"])
        result["launch_review_gate"] = gate
        result["launchable_now"] = result["launch_authorized"] and gate["status"] == "PASS"
        if result["launchable_now"]:
            binding = minimal3350_binding(card["run_id"])
            reservation = repo / binding["consumption_directory"] / f"{card['run_id']}.json"
            start = prepare_minimal3199_guardian_start(repo, card_path, approved_hash, card, files, output, reservation)
            result["guardian_request_validation"] = {
                "status": "PASS", "request_schema": start["request_schema"],
                "request_sha256": hashlib.sha256(canonical_json_bytes(start)).hexdigest(),
                "simulator_process_started": False,
            }
        else:
            result["guardian_request_validation"] = {"status": "BLOCKED_BY_REVIEW_GATE"}
    else:
        result["launchable_now"] = result["launch_authorized"]
    return result


def _dir_bytes(root: Path) -> int:
    total = 0
    for path in root.rglob("*"):
        if path.is_symlink():
            raise GateError("OUTPUT_SYMLINK_DETECTED")
        if path.is_file():
            total += path.stat().st_size
    return total


def resource_stop_reason(elapsed_s: float, output_bytes: int, max_runtime_s: float,
                         max_output_bytes: int, launcher_gone: bool = False) -> str | None:
    """Return the first polled stop reason; the byte limit is a trigger, not quota."""
    if launcher_gone:
        return "LAUNCHER_DISAPPEARED"
    if elapsed_s >= max_runtime_s:
        return "WALLCLOCK_LIMIT"
    if output_bytes >= max_output_bytes:
        return "OUTPUT_SIZE_LIMIT"
    return None


def terminate_process_group(pid: int, proc: subprocess.Popen, grace_s: float) -> None:
    """Terminate the owned process group, escalating to SIGKILL after grace."""
    try:
        os.killpg(pid, signal.SIGTERM)
        proc.wait(timeout=grace_s)
    except (ProcessLookupError, subprocess.TimeoutExpired):
        try:
            os.killpg(pid, signal.SIGKILL)
        except ProcessLookupError:
            pass
        proc.wait()


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="microseconds").replace("+00:00", "Z")


def build_output_manifest(output: Path, role_records: list[dict[str, Any]], role_source: str,
                          role_source_sha256: str, run_id: str = LEGACY_RUN_ID) -> dict[str, Any]:
    """Deterministic inventory. It excludes only manifest and final receipt files."""
    manifest_path = output / "output_manifest.json"
    receipt_path = output / "execution_receipt.json"
    files: dict[str, Path] = {}
    for path in output.rglob("*"):
        if path.is_symlink():
            raise GateError("OUTPUT_SYMLINK_DETECTED")
        if path.is_file() and path not in {manifest_path, receipt_path}:
            files[path.relative_to(output).as_posix()] = path

    by_role = {record["role"]: record for record in role_records}
    artifact_roles = []
    for name in sorted(by_role):
        record = by_role[name]
        path = files.get(name)
        entry = {
            "role": name,
            "kind": record.get("kind"),
            "detector_id": record.get("detector_id"),
            "lane": record.get("lane"),
            "root": record.get("root"),
            "relative_path": name,
            "status": "PRESENT" if path else "MISSING",
            "size_bytes": path.stat().st_size if path else None,
            "sha256": sha256_file(path) if path else None,
        }
        artifact_roles.append(entry)

    role_names = set(by_role)
    support_files = []
    for name in sorted(files):
        if name in role_names:
            continue
        path = files[name]
        if name in {"scenario_control.sumocfg", "scenario_control.add.xml"}:
            category = "materialized_config"
        elif name.endswith(".log"):
            category = "log"
        else:
            category = "unclassified_output"
        support_files.append({
            "category": category,
            "relative_path": name,
            "size_bytes": path.stat().st_size,
            "sha256": sha256_file(path),
        })

    payload_bytes = sum(item["size_bytes"] for item in support_files)
    payload_bytes += sum(item["size_bytes"] or 0 for item in artifact_roles)
    return {
        "schema_version": "1",
        "run_id": run_id,
        "role_source": {"path": role_source, "sha256": role_source_sha256},
        "artifact_roles": artifact_roles,
        "support_files": support_files,
        "inventory_policy": {
            "sort_order": "UTF-8 relative POSIX path lexicographic; artifact roles sorted by role",
            "included": "All files present in the run output directory at inventory time, classified by bound role when matching a required role filename; other files are support_files/unclassified_output.",
            "excluded": ["output_manifest.json", "execution_receipt.json"],
            "exclusion_reason": "Self-hash recursion and receipt embeds the output-manifest hash.",
            "configs_and_logs": "Included in support_files with explicit materialized_config/log category.",
        },
        "actual_file_count": len(files),
        "payload_bytes_excluding_manifest_and_receipt": payload_bytes,
    }


def write_output_manifest(output: Path, role_records: list[dict[str, Any]], role_source: str,
                          role_source_sha256: str, run_id: str = LEGACY_RUN_ID) -> tuple[str, int, int]:
    manifest = build_output_manifest(output, role_records, role_source, role_source_sha256, run_id)
    data = canonical_json_bytes(manifest)
    _write_exclusive(output / "output_manifest.json", data)
    return hashlib.sha256(data).hexdigest(), len(data), manifest["payload_bytes_excluding_manifest_and_receipt"]


def write_execution_receipt(output: Path, *, started_at_utc: str | None, finished_at_utc: str,
                            wallclock_runtime_s: float | None, process_status: str,
                            return_code: int | None, stop_reason: str | None,
                            manifest_sha256: str | None, manifest_size_bytes: int | None,
                            payload_bytes: int | None, run_id: str = LEGACY_RUN_ID) -> bytes:
    receipt = {
        "schema_version": "1",
        "run_id": run_id,
        "started_at_utc": started_at_utc,
        "finished_at_utc": finished_at_utc,
        "wallclock_runtime_s": wallclock_runtime_s,
        "process_status": process_status,
        "return_code": return_code,
        "stop_reason": stop_reason,
        "output_manifest": {
            "path": "output_manifest.json" if manifest_sha256 else None,
            "sha256": manifest_sha256,
            "size_bytes": manifest_size_bytes,
        },
        "payload_bytes_excluding_manifest_and_receipt": payload_bytes,
        "immutable": True,
        "retry_allowed": False,
    }
    data = canonical_json_bytes(receipt)
    _write_exclusive(output / "execution_receipt.json", data)
    return data


def _write_json_line(stream, value: dict[str, Any]) -> None:
    stream.write(canonical_json_bytes(value).decode("utf-8"))
    stream.flush()


def _read_json_line(stream) -> dict[str, Any]:
    line = stream.readline()
    if not line:
        raise EOFError("LAUNCHER_PIPE_CLOSED")
    value = json.loads(line)
    if not isinstance(value, dict):
        raise GateError("GUARDIAN_PROTOCOL_INVALID")
    return value


def _update_reservation(state_path: Path, state: dict[str, Any]) -> None:
    _atomic_status(state_path, canonical_json_bytes(state))


def _fsync_directory(path: Path) -> None:
    fd = os.open(path, os.O_RDONLY)
    try:
        os.fsync(fd)
    finally:
        os.close(fd)


def _read_guardian_event(stream, timeout_s: float) -> dict[str, Any] | None:
    ready, _, _ = select.select([stream], [], [], timeout_s)
    if not ready:
        return None
    return _read_json_line(stream)


def start_guardian(output: Path, sumo_home: Path) -> subprocess.Popen:
    """Start independent guardian and require READY before any SUMO start."""
    stderr_path = output / "guardian_stderr.log"
    child_environment = bound_sumo_environment(os.environ, sumo_home)
    with stderr_path.open("xb") as stderr_log:
        guardian = subprocess.Popen(
            [sys.executable, str(Path(__file__).resolve()), "_guardian"],
            stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=stderr_log,
            cwd=Path(__file__).resolve().parents[3], text=True, encoding="utf-8",
            bufsize=1, start_new_session=True, env=child_environment)
    try:
        ready = _read_guardian_event(guardian.stdout, GUARDIAN_READY_TIMEOUT_S)
        if not ready or ready.get("event") != "READY" or ready.get("protocol") != "r02-guardian-v1":
            raise GateError("GUARDIAN_NOT_READY")
    except BaseException:
        if guardian.stdin:
            guardian.stdin.close()
        if guardian.poll() is None:
            guardian.terminate()
        guardian.wait(timeout=GUARDIAN_SHUTDOWN_GRACE_S)
        raise
    return guardian


def _ensure_final_output_files(spec: dict[str, Any], process_status: str,
                               return_code: int | None, stop_reason: str | None,
                               started_at_utc: str | None, finished_at_utc: str,
                               wallclock_runtime_s: float | None) -> dict[str, Any]:
    output = Path(spec["output_directory"])
    manifest_path = output / "output_manifest.json"
    if manifest_path.exists():
        manifest_data = manifest_path.read_bytes()
        manifest_obj = json.loads(manifest_data)
        manifest_hash = hashlib.sha256(manifest_data).hexdigest()
        manifest_size = len(manifest_data)
        payload_bytes = manifest_obj["payload_bytes_excluding_manifest_and_receipt"]
    else:
        manifest_hash, manifest_size, payload_bytes = write_output_manifest(
            output, spec["output_roles"], spec["output_role_source"], spec["output_role_source_sha256"], spec["run_id"])
    receipt_path = output / "execution_receipt.json"
    if receipt_path.exists():
        receipt_data = receipt_path.read_bytes()
        receipt = json.loads(receipt_data)
        if receipt.get("output_manifest", {}).get("sha256") != manifest_hash:
            raise GateError("EXISTING_EXECUTION_RECEIPT_MANIFEST_MISMATCH")
    else:
        receipt_data = write_execution_receipt(
            output, started_at_utc=started_at_utc, finished_at_utc=finished_at_utc,
            wallclock_runtime_s=wallclock_runtime_s, process_status=process_status,
            return_code=return_code, stop_reason=stop_reason, manifest_sha256=manifest_hash,
            manifest_size_bytes=manifest_size, payload_bytes=payload_bytes, run_id=spec["run_id"])
    return {
        "execution_receipt_sha256": hashlib.sha256(receipt_data).hexdigest(),
        "output_manifest_sha256": manifest_hash,
        "output_manifest_size_bytes": manifest_size,
        "output_payload_bytes": payload_bytes,
    }


def guardian_main() -> int:
    """Independent process supervisor. Launcher liveness is the control-pipe EOF."""
    _write_json_line(sys.stdout, {"event": "READY", "protocol": "r02-guardian-v1", "pid": os.getpid()})
    try:
        start = _read_json_line(sys.stdin)
    except EOFError:
        return 0  # launcher vanished before START; no simulator child was created
    start_run_id = start.get("run_id") if isinstance(start, dict) else None
    try:
        if _requires_v2_start(start_run_id):
            run_binding = validate_guardian_start_request(start, REPO_ROOT)
        else:
            if start.get("action") != "START" or start_run_id not in SUPPORTED_RUN_BINDINGS:
                raise GateError("INVALID_START_REQUEST")
            run_binding = SUPPORTED_RUN_BINDINGS[start_run_id]
            if (start.get("output_directory") != str(Path(start["cwd"]) / run_binding["output_directory"])
                    or start.get("reservation_path") != str(Path(start["cwd"]) / run_binding["consumption_directory"] / f"{start_run_id}.json")):
                raise GateError("START_PROVENANCE_BINDING_MISMATCH")
    except (GateError, TypeError, KeyError) as exc:
        _write_json_line(sys.stdout, {"event": "ERROR", "reason": str(exc)})
        return 2

    output = Path(start["output_directory"])
    state_path = Path(start["reservation_path"])
    cmd = start["command"]
    runtime_schema_binding = {
        "sumo_home": start.get("sumo_home"),
        "additional_schema_path": start.get("additional_schema_path"),
        "additional_schema_sha256": start.get("additional_schema_sha256"),
    }
    try:
        sumo_home = verify_sumo_schema_binding(runtime_schema_binding)
    except GateError as exc:
        _write_json_line(sys.stdout, {"event": "ERROR", "reason": str(exc)})
        return 2
    if not isinstance(cmd, list) or not cmd or not Path(cmd[0]).is_absolute():
        _write_json_line(sys.stdout, {"event": "ERROR", "reason": "INVALID_COMMAND"})
        return 2

    started_at_utc: str | None = None
    started_mono: float | None = None
    proc: subprocess.Popen | None = None
    stop_reason: str | None = None
    return_code: int | None = None
    state = json.loads(state_path.read_text(encoding="utf-8"))
    try:
        stdout_path = output / "runner_stdout.log"
        stderr_path = output / "runner_stderr.log"
        with stdout_path.open("xb") as stdout_log, stderr_path.open("xb") as stderr_log:
            child_environment = bound_sumo_environment(os.environ, sumo_home)
            proc = subprocess.Popen(cmd, cwd=start["cwd"], stdin=subprocess.DEVNULL,
                                    stdout=stdout_log, stderr=stderr_log,
                                    start_new_session=True, env=child_environment)
            started_at_utc = _utc_now()
            started_mono = time.monotonic()
            state.update({"status": "CHILD_STARTED", "guardian_pid": os.getpid(),
                          "simulator_pid": proc.pid, "simulator_pgid": proc.pid,
                          "started_at_utc": started_at_utc})
            _update_reservation(state_path, state)
            try:
                _write_json_line(sys.stdout, {"event": "SPAWNED", "pid": proc.pid,
                                              "started_at_utc": started_at_utc})
            except (BrokenPipeError, OSError):
                stop_reason = "LAUNCHER_DISAPPEARED"

            launcher_gone = stop_reason == "LAUNCHER_DISAPPEARED"
            while proc.poll() is None:
                ready, _, _ = select.select([sys.stdin], [], [], GUARDIAN_POLL_S)
                if ready:
                    line = sys.stdin.readline()
                    if not line:
                        launcher_gone = True
                    else:
                        # DISARM cannot be accepted until the child has exited and receipt is verified.
                        try:
                            msg = json.loads(line)
                        except json.JSONDecodeError:
                            msg = {}
                        if msg.get("action") != "KEEPALIVE":
                            launcher_gone = True
                elapsed = time.monotonic() - started_mono
                try:
                    current_bytes = _dir_bytes(output)
                except GateError:
                    stop_reason = "OUTPUT_SYMLINK_DETECTED"
                    break
                stop_reason = resource_stop_reason(
                    elapsed, current_bytes, float(start["max_runtime_s"]),
                    int(start["max_output_bytes"]), launcher_gone)
                if stop_reason:
                    break

            if proc.poll() is None:
                terminate_process_group(proc.pid, proc, GUARDIAN_SHUTDOWN_GRACE_S)
            return_code = proc.wait()
            finished_at_utc = _utc_now()
            runtime_s = round(time.monotonic() - started_mono, 6)
            process_status = "TERMINATED" if stop_reason else "PROCESS_EXITED"
            try:
                _write_json_line(sys.stdout, {"event": "EXITED", "process_status": process_status,
                                              "return_code": return_code, "stop_reason": stop_reason,
                                              "started_at_utc": started_at_utc,
                                              "finished_at_utc": finished_at_utc,
                                              "wallclock_runtime_s": runtime_s})
            except (BrokenPipeError, OSError):
                launcher_gone = True
            # Keep guardian alive after child exit until final status is durably handed off.
            while not launcher_gone:
                ready, _, _ = select.select([sys.stdin], [], [], GUARDIAN_POLL_S)
                if not ready:
                    continue
                line = sys.stdin.readline()
                if not line:
                    launcher_gone = True
                    break
                msg = json.loads(line)
                if msg.get("action") == "DISARM":
                    receipt_path = output / "execution_receipt.json"
                    manifest_path = output / "output_manifest.json"
                    if (not receipt_path.is_file() or not manifest_path.is_file()
                            or sha256_file(receipt_path) != msg.get("execution_receipt_sha256")
                            or sha256_file(manifest_path) != msg.get("output_manifest_sha256")):
                        raise GateError("FINAL_STATUS_HANDOFF_INVALID")
                    receipt = json.loads(receipt_path.read_text(encoding="utf-8"))
                    if (receipt.get("process_status") != process_status
                            or receipt.get("return_code") != return_code
                            or receipt.get("output_manifest", {}).get("sha256") != msg["output_manifest_sha256"]):
                        raise GateError("FINAL_STATUS_RECEIPT_MISMATCH")
                    state.update({"status": "FINAL_STATUS_HANDED_OFF", "process_status": process_status,
                                  "return_code": return_code, "stop_reason": stop_reason,
                                  "finished_at_utc": finished_at_utc, "wallclock_runtime_s": runtime_s,
                                  "execution_receipt_sha256": msg["execution_receipt_sha256"],
                                  "output_manifest_sha256": msg["output_manifest_sha256"],
                                  "output_manifest_size_bytes": manifest_path.stat().st_size,
                                  "reservation_durability": "file_fsync_then_atomic_replace_then_parent_directory_fsync",
                                  "guardian_disarmed_at_utc": _utc_now(), "retry_allowed": False})
                    _update_reservation(state_path, state)
                    _write_json_line(sys.stdout, {"event": "DISARMED"})
                    return 0
                # Any unexpected post-exit command is not accepted as a handoff.
                raise GateError("GUARDIAN_PROTOCOL_INVALID_POST_EXIT")

            # Launcher died before handoff. Guardian writes final artifacts itself.
            if launcher_gone:
                stop_reason = stop_reason or "LAUNCHER_DISAPPEARED_AFTER_EXIT"
                handoff = _ensure_final_output_files(
                    start, process_status, return_code, stop_reason, started_at_utc,
                    finished_at_utc, runtime_s)
                _fsync_directory(output)
                receipt_path = output / "execution_receipt.json"
                manifest_path = output / "output_manifest.json"
                state.update({"status": "GUARDIAN_FINALIZED_AFTER_LAUNCHER_EXIT",
                              "process_status": process_status, "return_code": return_code,
                              "stop_reason": stop_reason,
                              "finished_at_utc": finished_at_utc, "wallclock_runtime_s": runtime_s,
                              **handoff,
                              "reservation_durability": "file_fsync_then_atomic_replace_then_parent_directory_fsync",
                              "guardian_disarmed_at_utc": _utc_now(), "retry_allowed": False})
                _update_reservation(state_path, state)
                return 0
    except BaseException as exc:
        if proc is not None and proc.poll() is None:
            terminate_process_group(proc.pid, proc, GUARDIAN_SHUTDOWN_GRACE_S)
        finished_at_utc = _utc_now()
        runtime_s = round(time.monotonic() - started_mono, 6) if started_mono is not None else None
        final_status = "TERMINATED" if proc is not None else "FAILED"
        return_code = proc.poll() if proc is not None else None
        handoff = {}
        if output.is_dir():
            try:
                handoff = _ensure_final_output_files(
                    start, final_status, return_code, f"GUARDIAN_ERROR:{type(exc).__name__}:{exc}",
                    started_at_utc, finished_at_utc, runtime_s)
                _fsync_directory(output)
            except Exception as finalize_exc:
                state["finalization_error"] = f"{type(finalize_exc).__name__}:{finalize_exc}"
        state.update({"status": "GUARDIAN_FAILED_CLEANUP", "guardian_error": f"{type(exc).__name__}:{exc}",
                      "process_status": final_status, "return_code": return_code,
                      "finished_at_utc": finished_at_utc, "wallclock_runtime_s": runtime_s,
                      "retry_allowed": False, **handoff})
        try:
            _update_reservation(state_path, state)
        except Exception:
            pass
        try:
            _write_json_line(sys.stdout, {"event": "ERROR", "reason": f"{type(exc).__name__}:{exc}"})
        except Exception:
            pass
        return 2
    return 2


def launch(repo: Path, card_path: Path, approved_hash: str) -> int:
    repo = repo.resolve(strict=True)
    card_path = card_path.resolve(strict=True)
    if sha256_file(card_path) != approved_hash:
        raise GateError("APPROVED_CARD_HASH_MISMATCH")
    # Use only an allowlisted, exact card path to locate the irreversible reservation.
    # Check this before output existence so a consumed run always reports no-retry.
    header = load_json(card_path)
    header_binding = _run_binding(repo, card_path, header)
    header_run_id = header["run_id"]
    header_reservation = repo / header_binding["consumption_directory"] / f"{header_run_id}.json"
    if header_reservation.exists():
        raise GateError("ONE_START_ALREADY_CONSUMED")
    # All checks precede the irreversible one-use reservation.
    card, files = verify_card(repo, card_path, approved_hash, allow_prelaunch=False)
    run_id = card["run_id"]
    binding = header_binding
    if run_id == REPAIRED_V5_ATTEMPT_ID:
        review_gate = repaired_final_review_gate(repo, approved_hash)
        if review_gate["status"] != "PASS":
            raise GateError("REPAIRED_TREATMENT_REVIEWS_NOT_PASSED_AND_HASH_BOUND")
    if run_id in MINIMAL3199_RETRY_BINDINGS and card.get("card_status") == "FINAL_AUTHORIZED_FOR_ONE_START":
        review_gate = minimal3199_retry_final_review_gate(repo, approved_hash, run_id)
        if review_gate["status"] != "PASS":
            raise GateError("MINIMAL3199_TECHNICAL_RETRY_REVIEWS_NOT_PASSED_AND_HASH_BOUND")
    prevalidated_start = None
    if run_id in MINIMAL3199_RETRY_BINDINGS:
        prevalidated_start = prepare_minimal3199_guardian_start(
            repo, card_path, approved_hash, card, files, files["output"],
            repo / binding["consumption_directory"] / f"{run_id}.json")
    if run_id in MINIMAL3350_V2_RUN_IDS:
        gate = minimal3350_final_review_gate(repo, approved_hash, run_id)
        if gate["status"] != "PASS":
            raise GateError("MINIMAL3350_REVIEWS_NOT_PASSED_AND_HASH_BOUND")
        prevalidated_start = prepare_minimal3199_guardian_start(
            repo, card_path, approved_hash, card, files, files["output"],
            repo / binding["consumption_directory"] / f"{run_id}.json")
    package = repo / "artifacts" / binding["package_id"] / "r02_single_start"
    consumed_dir = repo / binding["consumption_directory"]
    reservation = consumed_dir / f"{run_id}.json"
    if reservation.exists():
        raise GateError("ONE_START_ALREADY_CONSUMED")
    if (files["output"].parent.exists()
            and binding["kind"] in {"PAIR_RUN", "MINIMAL3199_FINAL_CONTROL"}):
        raise GateError("OUTPUT_RUN_ROOT_ALREADY_EXISTS")
    consumed_dir.mkdir(parents=True, exist_ok=True)
    initial = {
        "schema_version": "1", "run_id": run_id, "status": "START_ATTEMPT_CONSUMED",
        "approved_card_sha256": approved_hash,
        "reserved_at_unix": time.time(), "reserved_at_utc": _utc_now(), "retry_allowed": False,
        "max_starts": 1, "simulator_pid": None,
        "note": "Reservation is irreversible. Any spawn failure, timeout, cap breach or nonzero exit stays consumed; never retry.",
    }
    try:
        _write_exclusive(reservation, canonical_json_bytes(initial))
        _fsync_directory(consumed_dir)
    except FileExistsError as exc:
        raise GateError("ONE_START_ALREADY_CONSUMED") from exc

    output = files["output"]
    guardian: subprocess.Popen | None = None
    started_at_utc: str | None = None
    started_monotonic: float | None = None
    guardian_started = False
    spec: dict[str, Any] | None = None
    try:
        add_copy = output / "scenario_control.add.xml"
        cfg_copy = output / "scenario_control.sumocfg"
        if binding["kind"] in {"MINIMAL3199_TECH_RETRY_FINAL_CONTROL", "MINIMAL3199_UX0_TREATMENT_FINAL"}:
            # The exact, hash-verified files were materialized before launch.
            # Never overwrite them; rederive and recheck their contents here.
            cfg_bytes = cfg_copy.read_bytes()
            add_bytes = add_copy.read_bytes()
            source_output = (repo / "data/raw/stage6_minimal3199_existence_20260924_v1/MINIMAL3199_R720_DELAYED_S17/outputs"
                             if binding["kind"] == "MINIMAL3199_UX0_TREATMENT_FINAL"
                             else repo / "data/raw/stage6_minimal3199_existence_20260924_v1/MINIMAL3199_CTRL_S17/outputs")
            expected_cfg, expected_add, transform = stage_minimal3199_inputs(
                files["sumocfg"], files["additional"], source_output, output)
            if (transform != files.get("staged_config_transform") or cfg_bytes != expected_cfg or add_bytes != expected_add
                    or hashlib.sha256(cfg_bytes).hexdigest() != transform["sumocfg"]["expected_staged_sha256"]
                    or hashlib.sha256(add_bytes).hexdigest() != transform["additional"]["expected_staged_sha256"]):
                raise GateError("STAGED_INPUTS_CHANGED_AFTER_PREFLIGHT")
        elif binding["kind"] == "MINIMAL3199_TECH_RETRY_DRAFT":
            output.mkdir(parents=True, exist_ok=False)
            cfg_bytes, add_bytes, transform = stage_minimal3199_inputs(
                files["sumocfg"], files["additional"],
                repo / "data/raw/stage6_minimal3199_existence_20260924_v1/MINIMAL3199_CTRL_S17/outputs",
                output)
            if (transform != files.get("staged_config_transform")
                    or hashlib.sha256(cfg_bytes).hexdigest() != transform["sumocfg"]["expected_staged_sha256"]
                    or hashlib.sha256(add_bytes).hexdigest() != transform["additional"]["expected_staged_sha256"]):
                raise GateError("STAGED_INPUTS_CHANGED_AFTER_PREFLIGHT")
        else:
            output.mkdir(parents=True, exist_ok=False)
            cfg = files["sumocfg"].read_text(encoding="utf-8")
            add = files["additional"].read_text(encoding="utf-8")
            add_bytes = add.replace(OUTPUT_TOKEN, str(output)).encode("utf-8")
            cfg_bytes = cfg.replace(OUTPUT_TOKEN, str(output)).replace(str(files["additional"]), str(add_copy)).encode("utf-8")
        if OUTPUT_TOKEN.encode() in cfg_bytes or OUTPUT_TOKEN.encode() in add_bytes:
            raise GateError("UNRESOLVED_OUTPUT_PLACEHOLDER")
        if binding["kind"] not in {"MINIMAL3199_TECH_RETRY_FINAL_CONTROL", "MINIMAL3199_UX0_TREATMENT_FINAL"}:
            _write_exclusive(add_copy, add_bytes)
            _write_exclusive(cfg_copy, cfg_bytes)
        spec_files = dict(files)
        spec_files["sumocfg"] = cfg_copy
        spec = build_guardian_start_spec(
            spec_files, card, output, reservation, repo, run_id,
            card_path=card_path, approved_card_sha256=approved_hash)
        if prevalidated_start is not None and spec != prevalidated_start:
            raise GateError("GUARDIAN_START_SPEC_CHANGED_AFTER_PREFLIGHT")
        staged_records = {
            "source_sumocfg_sha256": sha256_file(files["sumocfg"]),
            "source_additional_sha256": sha256_file(files["additional"]),
            "staged_sumocfg_sha256": sha256_file(cfg_copy),
            "staged_additional_sha256": sha256_file(add_copy),
            "staged_sumocfg_bytes": cfg_copy.stat().st_size,
            "staged_additional_bytes": add_copy.stat().st_size,
        }
        if binding["kind"] in {"MINIMAL3199_TECH_RETRY_DRAFT", "MINIMAL3199_TECH_RETRY_FINAL_CONTROL", "MINIMAL3199_UX0_TREATMENT_FINAL"}:
            staged_records["transform"] = files["staged_config_transform"]
            if (staged_records["staged_sumocfg_sha256"] != transform["sumocfg"]["expected_staged_sha256"]
                    or staged_records["staged_sumocfg_bytes"] != transform["sumocfg"]["expected_staged_bytes"]
                    or staged_records["staged_additional_sha256"] != transform["additional"]["expected_staged_sha256"]
                    or staged_records["staged_additional_bytes"] != transform["additional"]["expected_staged_bytes"]):
                raise GateError("STAGED_INPUTS_COPY_HASH_MISMATCH")
        initial["staged_inputs"] = staged_records
        _atomic_status(reservation, canonical_json_bytes(initial))
        # Start independent Guardian and require a READY handshake before it can spawn the child.
        guardian = start_guardian(output, files["sumo_home"])
        guardian_started = True
        started_monotonic = time.monotonic()
        _write_json_line(guardian.stdin, spec)
        event = _read_guardian_event(guardian.stdout, GUARDIAN_READY_TIMEOUT_S)
        if not event or event.get("event") != "SPAWNED":
            raise GateError(f"GUARDIAN_SPAWN_HANDSHAKE_FAILED:{event}")
        initial.update({"status": "CHILD_STARTED", "guardian_pid": guardian.pid,
                        "simulator_pid": event["pid"], "simulator_pgid": event["pid"],
                        "started_at_utc": event["started_at_utc"]})
        _atomic_status(reservation, canonical_json_bytes(initial))
        started_at_utc = event["started_at_utc"]

        while True:
            event = _read_guardian_event(guardian.stdout, GUARDIAN_POLL_S * 20)
            if event is None:
                if guardian.poll() is not None:
                    raise GateError("GUARDIAN_EXITED_WITHOUT_FINAL_EVENT")
                _write_json_line(guardian.stdin, {"action": "KEEPALIVE"})
                continue
            if event.get("event") == "ERROR":
                raise GateError(f"GUARDIAN_ERROR:{event.get('reason')}")
            if event.get("event") == "EXITED":
                break
            raise GateError(f"GUARDIAN_UNEXPECTED_EVENT:{event}")

        return_code = event["return_code"]
        process_status = event["process_status"]
        stop_reason = event.get("stop_reason")
        finished_at_utc = event["finished_at_utc"]
        wallclock_runtime_s = event["wallclock_runtime_s"]
        handoff = _ensure_final_output_files(
            spec, process_status, return_code, stop_reason, started_at_utc,
            finished_at_utc, wallclock_runtime_s)
        _fsync_directory(output)
        _write_json_line(guardian.stdin, {
            "action": "DISARM", "execution_receipt_sha256": handoff["execution_receipt_sha256"],
            "output_manifest_sha256": handoff["output_manifest_sha256"],
        })
        final_event = _read_guardian_event(guardian.stdout, GUARDIAN_READY_TIMEOUT_S)
        if not final_event or final_event.get("event") != "DISARMED":
            raise GateError(f"GUARDIAN_FINAL_HANDOFF_FAILED:{final_event}")
        guardian.wait(timeout=GUARDIAN_SHUTDOWN_GRACE_S)
        outcome = dict(initial)
        outcome.update({"status": "FINAL_STATUS_HANDED_OFF", "process_status": process_status,
                        "finished_at_utc": finished_at_utc, "wallclock_runtime_s": wallclock_runtime_s,
                        "return_code": return_code, "stop_reason": stop_reason,
                        **handoff, "retry_allowed": False})
        _atomic_status(reservation, canonical_json_bytes(outcome))
        return return_code if process_status == "PROCESS_EXITED" and return_code == 0 else 124
    except BaseException as exc:
        if guardian is not None and guardian.poll() is None and guardian.stdin:
            # Closing the control pipe is the guardian's liveness signal; it owns cleanup.
            try:
                guardian.stdin.close()
            except OSError:
                pass
            try:
                guardian.wait(timeout=GUARDIAN_SHUTDOWN_GRACE_S + 10)
            except subprocess.TimeoutExpired:
                # Do not kill Guardian here: that would defeat independent cleanup.
                pass
        finished_at_utc = _utc_now()
        handoff = {}
        if output.is_dir() and not guardian_started and spec is not None:
            try:
                handoff = _ensure_final_output_files(
                    spec, "FAILED", None, f"{type(exc).__name__}:{exc}", None,
                    finished_at_utc, None)
                _fsync_directory(output)
            except Exception:
                pass
        failed = dict(initial)
        if guardian_started and reservation.is_file():
            try:
                persisted = json.loads(reservation.read_text(encoding="utf-8"))
                if isinstance(persisted, dict):
                    failed.update(persisted)
            except (OSError, json.JSONDecodeError):
                pass
        guardian_final = failed.get("status") in {
            "FINAL_STATUS_HANDED_OFF", "GUARDIAN_FINALIZED_AFTER_LAUNCHER_EXIT", "GUARDIAN_FAILED_CLEANUP"
        }
        failed.update({"status": failed.get("status") if guardian_final else
                       ("GUARDIAN_HANDOFF_PENDING" if guardian_started else "FAILED"),
                       "finished_at_utc": failed.get("finished_at_utc", finished_at_utc),
                       "wallclock_runtime_s": failed.get("wallclock_runtime_s") or
                       (round(time.monotonic() - started_monotonic, 6) if started_monotonic else None),
                       "failure": f"{type(exc).__name__}:{exc}", "retry_allowed": False, **handoff})
        try:
            _atomic_status(reservation, canonical_json_bytes(failed))
        except Exception:
            pass
        raise


def main(argv: list[str] | None = None) -> int:
    actual_argv = sys.argv[1:] if argv is None else argv
    if actual_argv and actual_argv[0] == "_guardian":
        return guardian_main()
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("mode", choices=("preflight", "launch"))
    parser.add_argument("--repo", type=Path, required=True)
    parser.add_argument("--card", type=Path, required=True)
    parser.add_argument("--approved-card-sha256", required=True)
    args = parser.parse_args(actual_argv)
    try:
        if args.mode == "preflight":
            print(json.dumps(make_plan(args.repo, args.card, args.approved_card_sha256), indent=2))
            return 0
        return launch(args.repo.resolve(strict=True), args.card, args.approved_card_sha256)
    except GateError as exc:
        print(json.dumps({"status": "BLOCKED", "reason": str(exc), "simulator_process_started": False}), file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())

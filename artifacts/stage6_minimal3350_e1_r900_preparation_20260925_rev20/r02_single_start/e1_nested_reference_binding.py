"""Fail-closed XML path closure for the one-use E1 R900 retry package."""
from __future__ import annotations

import hashlib
import os
from pathlib import Path
import re
import xml.etree.ElementTree as ET
from typing import Any

STALE_MARKERS = (
    "stage6_minimal3350_ux0_20260925_v14",
    "stage6_minimal3350_ux0_20260925_v16",
    "stage6_minimal3350_ux0_20260925_v17",
    "stage6_minimal3350_ux0_20260925_v18",
    "stage6_minimal3350_ux0_20260925_v19",
    "stage6_minimal3350_e1_r900_preparation_20260925_rev14",
    "stage6_minimal3350_e1_r900_preparation_20260925_rev16",
    "stage6_minimal3350_e1_r900_preparation_20260925_rev17",
    "stage6_minimal3350_e1_r900_preparation_20260925_rev18",
    "stage6_minimal3350_e1_r900_preparation_20260925_rev19",
)
CFG_OUTPUT_TAGS = {
    "fcd-output", "queue-output", "summary-output", "tripinfo-output",
    "vehroute-output", "lanechange-output", "log", "error-log",
}


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _canonical_absolute(value: Any, label: str) -> Path:
    if not isinstance(value, str) or not value or not Path(value).is_absolute():
        raise ValueError(f"{label}:ABSOLUTE_PATH_REQUIRED")
    path = Path(value)
    if ".." in path.parts:
        raise ValueError(f"{label}:PATH_TRAVERSAL")
    resolved = path.resolve(strict=False)
    if str(resolved) != value:
        raise ValueError(f"{label}:NONCANONICAL_PATH")
    if any(marker in value for marker in STALE_MARKERS):
        raise ValueError(f"{label}:STALE_REVISION_PATH")
    for old_rev in re.findall(r"stage6_minimal3350_e1_r900_preparation_20260925_rev(\d+)", value):
        if old_rev != "20":
            raise ValueError(f"{label}:STALE_PACKAGE_REVISION")
    return resolved


def _reject_symlink_components(path: Path, repo: Path) -> None:
    try:
        rel = path.relative_to(repo)
    except ValueError as exc:
        raise ValueError("PATH_OUTSIDE_REPOSITORY") from exc
    current = repo
    if current.is_symlink():
        raise ValueError("REPOSITORY_ROOT_SYMLINK")
    for part in rel.parts:
        current = current / part
        if current.is_symlink():
            raise ValueError(f"SYMLINK_PATH_COMPONENT:{current}")


def _existing_writable_ancestor(target: Path, repo: Path) -> Path:
    _reject_symlink_components(target, repo)
    cursor = target
    while not cursor.exists():
        if cursor == repo or repo not in cursor.parents:
            raise ValueError("NO_EXISTING_PARENT_WITHIN_REPOSITORY")
        cursor = cursor.parent
    if not cursor.is_dir() or not os.access(cursor, os.W_OK):
        raise ValueError("OUTPUT_PARENT_NOT_WRITABLE_DIRECTORY")
    _reject_symlink_components(cursor, repo)
    return cursor


def _one_value(root: ET.Element, tag: str, label: str) -> str:
    found = [n for n in root.iter(tag)]
    if len(found) != 1 or not found[0].get("value"):
        raise ValueError(f"{label}:EXPECTED_ONE_VALUE")
    return found[0].get("value")  # type: ignore[return-value]


def _cfg_output_paths(root: ET.Element) -> list[str]:
    values=[]
    for node in root.iter():
        if isinstance(node.tag,str) and node.tag.endswith("-output") and node.tag not in CFG_OUTPUT_TAGS:
            raise ValueError(f"UNEXPECTED_CFG_OUTPUT_REFERENCE:{node.tag}")
        if node.tag in CFG_OUTPUT_TAGS:
            value=node.get("value")
            if not value:
                raise ValueError(f"CFG_OUTPUT_VALUE_MISSING:{node.tag}")
            values.append(value)
    return values


def _additional_output_paths(root: ET.Element) -> list[str]:
    values=[]
    for node in root.iter():
        if any(k in node.attrib for k in ("file","dest")) and node.tag not in {"laneAreaDetector", "inductionLoop", "e1Detector", "e2Detector", "timedEvent"}:
            raise ValueError(f"UNEXPECTED_ADDITIONAL_PATH_REFERENCE:{node.tag}")
        if node.tag in {"laneAreaDetector", "inductionLoop", "e1Detector", "e2Detector"}:
            value=node.get("file")
            if not value:
                raise ValueError(f"ADDITIONAL_OUTPUT_FILE_MISSING:{node.tag}")
            values.append(value)
        elif node.tag == "timedEvent" and node.get("type") == "SaveTLSStates":
            value=node.get("dest")
            if not value:
                raise ValueError("ADDITIONAL_TLS_DEST_MISSING")
            values.append(value)
    return values


def _validate_outputs(cfg_root: ET.Element, add_root: ET.Element, roles: list[dict[str, Any]],
                      output: Path, repo: Path) -> dict[str, int]:
    output = _canonical_absolute(str(output), "output_directory")
    all_roles=[]
    for role in roles:
        p=_canonical_absolute(role.get("path"), f"output_role:{role.get('role')}")
        if not p.is_relative_to(output):
            raise ValueError(f"OUTPUT_ROLE_OUTSIDE_RUN_ROOT:{role.get('role')}")
        _reject_symlink_components(p,repo)
        all_roles.append(str(p))
    if len(all_roles)!=len(set(all_roles)):
        raise ValueError("OUTPUT_ROLE_DUPLICATE_PATH")
    cfg_paths=[str(_canonical_absolute(p,"sumocfg_output")) for p in _cfg_output_paths(cfg_root)]
    add_paths=[str(_canonical_absolute(p,"additional_output")) for p in _additional_output_paths(add_root)]
    for path in cfg_paths+add_paths:
        _reject_symlink_components(Path(path),repo)
    expected=set(all_roles)
    support={str(output/"sumo.log"),str(output/"sumo_error.log")}
    actual=set(cfg_paths+add_paths)
    if len(cfg_paths+add_paths)!=len(actual):
        raise ValueError("DUPLICATE_CONFIGURED_OUTPUT_PATH")
    if actual!=expected|support:
        raise ValueError("CONFIGURED_OUTPUT_ROLE_SET_MISMATCH")
    if any(not Path(p).is_relative_to(output) for p in actual):
        raise ValueError("CONFIGURED_OUTPUT_OUTSIDE_RUN_ROOT")
    return {"configured_unique_paths":len(actual),"configured_role_records":len(roles),
            "config_outputs":len(cfg_paths),"additional_outputs":len(add_paths)}


def build_and_validate_staged_inputs(*, repo: Path, package_root: Path,
        source_cfg: Path, source_demand: Path, source_additional: Path,
        network: Path, output_directory: Path, roles: list[dict[str, Any]],
        expected_cfg_sha256: str | None = None,
        expected_additional_sha256: str | None = None,
        actual_staged_cfg: bytes | None = None,
        actual_staged_additional: bytes | None = None) -> tuple[bytes, bytes, dict[str, Any]]:
    """Build staged bytes, then validate the actual bytes used by the runner.

    Optional persisted preview bytes are mandatory at runtime preflight. When
    supplied, they must be byte-identical to the deterministic transform and
    the XML validation below is performed against those exact bytes.
    """
    repo=repo.resolve(strict=True); package_root=package_root.resolve(strict=True)
    for p,label in ((source_cfg,"source_sumocfg"),(source_demand,"source_demand"),
                    (source_additional,"source_additional"),(network,"network")):
        p=p.resolve(strict=True)
        if not p.is_file() or (label!="network" and not p.is_relative_to(package_root)):
            raise ValueError(f"INVALID_BOUND_SOURCE:{label}")
    output=output_directory.resolve(strict=False)
    expected_output_rel=Path("data/raw/stage6_minimal3350_ux0_20260925_v20")
    if (not output.is_relative_to(repo/expected_output_rel)
            or output.parent.name==".." or output.exists()):
        raise ValueError("OUTPUT_DIRECTORY_NOT_EXACT_FRESH_V20_TARGET")
    raw_root=repo/expected_output_rel
    _existing_writable_ancestor(raw_root,repo)
    for p in (source_cfg,source_demand,source_additional,network):
        _reject_symlink_components(p.resolve(strict=True),repo)
    try:
        cfg_text=source_cfg.read_bytes().decode("utf-8",errors="strict")
        add_bytes=source_additional.read_bytes()
        add_text=add_bytes.decode("utf-8",errors="strict")
    except (OSError,UnicodeDecodeError) as exc:
        raise ValueError("SOURCE_XML_UNREADABLE_OR_NOT_UTF8") from exc
    try:
        cfg_root=ET.fromstring(cfg_text)
        add_root=ET.fromstring(add_text)
    except ET.ParseError as exc:
        raise ValueError("SOURCE_XML_INVALID") from exc
    expected_inputs={
        "net-file":str(network.resolve(strict=True)),
        "route-files":str(source_demand.resolve(strict=True)),
        "additional-files":str(source_additional.resolve(strict=True)),
    }
    for tag,expected in expected_inputs.items():
        actual=_canonical_absolute(_one_value(cfg_root,tag,tag),tag)
        if str(actual)!=expected:
            raise ValueError(f"SUMOCFG_INPUT_REFERENCE_MISMATCH:{tag}")
    # Validate source outputs first, then stage only the nested additional input edge.
    _validate_outputs(cfg_root,add_root,roles,output,repo)
    staged_add=output/"scenario_control.add.xml"
    staged_cfg_text=cfg_text.replace(expected_inputs["additional-files"],str(staged_add))
    if staged_cfg_text==cfg_text or staged_cfg_text.count(str(staged_add))!=1:
        raise ValueError("STAGED_ADDITIONAL_REFERENCE_REWRITE_COUNT_MISMATCH")
    if any(mark in staged_cfg_text for mark in STALE_MARKERS) or any(mark in add_text for mark in STALE_MARKERS):
        raise ValueError("STALE_REVISION_TOKEN_IN_STAGED_XML")
    staged_cfg=staged_cfg_text.encode("utf-8")
    if actual_staged_cfg is not None and actual_staged_cfg != staged_cfg:
        raise ValueError("PERSISTED_STAGED_SUMOCFG_NOT_DETERMINISTIC")
    if actual_staged_additional is not None and actual_staged_additional != add_bytes:
        raise ValueError("PERSISTED_STAGED_ADDITIONAL_NOT_SOURCE_IDENTICAL")
    staged_cfg_to_validate = actual_staged_cfg if actual_staged_cfg is not None else staged_cfg
    staged_add_to_validate = actual_staged_additional if actual_staged_additional is not None else add_bytes
    try:
        staged_cfg_root=ET.fromstring(staged_cfg_to_validate)
        staged_add_root=ET.fromstring(staged_add_to_validate)
    except ET.ParseError as exc:
        raise ValueError("ACTUAL_STAGED_XML_INVALID") from exc
    staged_add_value=_canonical_absolute(_one_value(staged_cfg_root,"additional-files","additional-files"),"additional-files")
    if str(staged_add_value)!=str(staged_add):
        raise ValueError("STAGED_ADDITIONAL_REFERENCE_NOT_EXACT_OUTPUT_PATH")
    counts=_validate_outputs(staged_cfg_root,staged_add_root,roles,output,repo)
    staged_cfg_sha=sha256_bytes(staged_cfg); staged_add_sha=sha256_bytes(add_bytes)
    if expected_cfg_sha256 is not None and staged_cfg_sha!=expected_cfg_sha256:
        raise ValueError("STAGED_SUMOCFG_HASH_MISMATCH")
    if expected_additional_sha256 is not None and staged_add_sha!=expected_additional_sha256:
        raise ValueError("STAGED_ADDITIONAL_HASH_MISMATCH")
    transform={
        "schema":"e1-staged-reference-closure-v1",
        "source_sumocfg_sha256":sha256_bytes(source_cfg.read_bytes()),
        "source_demand_sha256":sha256_bytes(source_demand.read_bytes()),
        "source_additional_sha256":sha256_bytes(add_bytes),
        "staged_sumocfg_sha256":staged_cfg_sha,
        "staged_sumocfg_bytes":len(staged_cfg),
        "staged_additional_sha256":staged_add_sha,
        "staged_additional_bytes":len(add_bytes),
        "staged_additional_path":str(staged_add),
        "validated_actual_staged_bytes":actual_staged_cfg is not None and actual_staged_additional is not None,
        "route_file_path":expected_inputs["route-files"],
        "network_path":expected_inputs["net-file"],
        **counts,
    }
    return staged_cfg,add_bytes,transform

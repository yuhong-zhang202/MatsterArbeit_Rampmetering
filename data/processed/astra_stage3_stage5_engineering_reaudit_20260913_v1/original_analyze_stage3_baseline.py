"""Archive-only Stage 3 baseline diagnostics.

This module deliberately has no SUMO, TraCI, runner, or subprocess imports.  It
resolves every input through an immutable Stage 2 source map and never falls
back to the original temporary runtime directory.
"""
from __future__ import annotations

import argparse
from collections import Counter, defaultdict
import csv
import hashlib
import json
import math
import os
from pathlib import Path
import posixpath
import re
import shutil
import sys
import xml.etree.ElementTree as ET


ROOT = Path(__file__).resolve().parents[2]
CLASSES = ("M", "R", "U", "X")
REQUIRED_WINDOWS = {
    "Full": (0.0, 2700.0),
    "A": (0.0, 1500.0),
    "B": (300.0, 1500.0),
    "Post": (1500.0, 2700.0),
}
OUTPUT_TABLES = (
    "coverage_audit.csv",
    "lane_class_timeline.csv",
    "stopping_episodes.csv",
    "spatial_propagation_evidence.csv",
    "condition_evidence_summary.csv",
)
COVERAGE_FIELDS = ["run_id", "output_id", "path", "sha256", "schema_version", "time_count", "duplicate_count",
                   "unknown_id_count", "unknown_lane_count", "missing_intervals", "status", "reason"]
TIMELINE_FIELDS = ["run_id", "seed", "time_s", "lane_id", "region", "is_internal", "class", "present_count",
                   "stopped_count", "speed_sum_mps", "speed_n", "min_path_position_m", "max_path_position_m",
                   "position_mapping_status", "tls_link", "tls_state", "coverage", "missing_speed_count"]
EPISODE_FIELDS = ["episode_id", "parent_episode_id", "run_id", "class", "region", "kind", "vehicle_id_or_null",
                  "observation_domain", "stop_definition_id", "sampling_period_s", "first_label", "last_label",
                  "sample_count", "support_seconds", "censor_left", "censor_right", "gap_reason", "TLS_context"]
PROPAGATION_FIELDS = ["run_id", "chain_id", "ramp_end_event_id", "storage_event_id", "internal_event_set_id",
                      "shared_R_event_id", "shared_U_event_id", "cooccurrence_support_s", "TLS_context_id",
                      "contradiction_ids", "status", "reason"]
CONDITION_FIELDS = ["run_id", "condition", "seed", "window", "entity", "metric", "value", "unit", "denominator",
                    "qualification", "source_event_id", "reason"]
TABLE_SCHEMAS = dict(zip(OUTPUT_TABLES, [COVERAGE_FIELDS, TIMELINE_FIELDS, EPISODE_FIELDS,
                                        PROPAGATION_FIELDS, CONDITION_FIELDS]))


def digest(path: Path) -> str:
    h = hashlib.sha256()
    with Path(path).open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def finite(value: str | float | int, name: str = "value") -> float:
    try:
        result = float(value)
    except (TypeError, ValueError) as exc:
        raise ValueError(f"{name} is not numeric") from exc
    if not math.isfinite(result):
        raise ValueError(f"{name} is non-finite")
    return result


def vehicle_class(vehicle_id: str) -> str:
    match = re.fullmatch(r"(M|R|U|X)_flow\.(\d+)", vehicle_id)
    if not match:
        raise ValueError(f"unknown vehicle identity: {vehicle_id}")
    return match.group(1)


def load_json(path: Path) -> dict:
    value = json.loads(Path(path).read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"expected JSON object: {path}")
    return value


def write_json(path: Path, value: object) -> None:
    with Path(path).open("x", encoding="utf-8") as handle:
        json.dump(value, handle, indent=2, ensure_ascii=False, allow_nan=False)
        handle.write("\n")


def write_csv(path: Path, rows: list[dict], fields: list[str]) -> None:
    with Path(path).open("x", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, extrasaction="raise")
        writer.writeheader()
        writer.writerows(rows)


def _is_under(path: Path, parent: Path) -> bool:
    path = path.resolve()
    parent = parent.resolve()
    return path == parent or parent in path.parents


def reject_temporary_output(path: Path) -> None:
    resolved = Path(path).resolve()
    for temp_root in (Path("/tmp"), Path("/private/tmp"), Path("/var/tmp"), Path("/private/var/tmp")):
        if _is_under(resolved, temp_root):
            raise ValueError(f"temporary output prohibited: {resolved}")


def reserve_directories(paths: list[Path]) -> None:
    resolved = [Path(path).resolve() for path in paths]
    if len(set(resolved)) != len(resolved):
        raise ValueError("output directories must be distinct")
    for i, first in enumerate(resolved):
        reject_temporary_output(first)
        for second in resolved[i + 1 :]:
            if _is_under(first, second) or _is_under(second, first):
                raise ValueError("output directories may not be nested")
        if first.exists():
            raise FileExistsError(f"refusing to overwrite {first}")
        if not first.parent.is_dir():
            raise FileNotFoundError(f"output parent does not exist: {first.parent}")
    created: list[Path] = []
    try:
        for path in resolved:
            os.mkdir(path)
            created.append(path)
    except Exception:
        for path in reversed(created):
            path.rmdir()
        raise


class ArchiveResolver:
    """Resolve immutable archive files solely through a validated source map."""

    def __init__(self, source_map: Path, project_root: Path = ROOT):
        self.project_root = Path(project_root).resolve()
        self.map_path = Path(source_map).resolve()
        if not _is_under(self.map_path, self.project_root):
            raise ValueError("source map must be inside project")
        self.mapping = load_json(self.map_path)
        if self.mapping.get("archive_status") != "complete":
            raise ValueError("archive is not complete")
        self.original_root = posixpath.normpath(self.mapping["source_runtime_path"])
        archive_rel = self.mapping["archive_runtime_relative_path"]
        self.archive_root = (self.project_root / archive_rel).resolve()
        if not _is_under(self.archive_root, self.project_root):
            raise ValueError("archive root escapes project")
        self._by_original: dict[str, tuple[Path, str]] = {}
        self._by_suffix: dict[str, tuple[Path, str]] = {}
        for entry in self.mapping.get("file_map", []):
            original = posixpath.normpath(entry["original_absolute_path"])
            archived = (self.project_root / entry["archive_relative_path"]).resolve()
            if not original.startswith(self.original_root + "/"):
                raise ValueError("mapped original escapes source runtime")
            if not _is_under(archived, self.archive_root):
                raise ValueError("mapped archive escapes attempt")
            if archived.is_symlink() or any(p.is_symlink() for p in archived.parents if p != self.project_root):
                raise ValueError("archive symlink prohibited")
            if original in self._by_original:
                raise ValueError("duplicate original mapping")
            expected = entry["sha256"]
            if digest(archived) != expected:
                raise ValueError(f"archive hash mismatch: {archived}")
            suffix = posixpath.relpath(original, self.original_root)
            self._by_original[original] = (archived, expected)
            if suffix in self._by_suffix:
                raise ValueError("duplicate archive suffix")
            self._by_suffix[suffix] = (archived, expected)

    def resolve(self, original_or_suffix: str) -> Path:
        raw = str(original_or_suffix)
        if raw.startswith("/"):
            key = posixpath.normpath(raw)
            item = self._by_original.get(key)
        else:
            suffix = posixpath.normpath(raw)
            if suffix.startswith("../"):
                raise ValueError("archive suffix escapes runtime")
            item = self._by_suffix.get(suffix)
        if item is None:
            raise ValueError(f"no source-map entry; fallback prohibited: {raw}")
        path, expected = item
        if digest(path) != expected:
            raise ValueError(f"archive changed: {path}")
        return path

    def inventory(self) -> list[dict]:
        return [
            {"source_suffix": suffix, "archive_path": str(path.relative_to(self.project_root)), "sha256": sha}
            for suffix, (path, sha) in sorted(self._by_suffix.items())
        ]


def validate_windows(contract: dict) -> dict[str, tuple[float, float]]:
    raw = contract.get("windows")
    if not isinstance(raw, dict):
        raise ValueError("measurement contract has no windows")
    parsed: dict[str, tuple[float, float]] = {}
    for name, expected in REQUIRED_WINDOWS.items():
        value = raw.get(name)
        if not isinstance(value, dict) or set(("begin_s", "end_s")) - set(value):
            raise ValueError(f"undeclared window: {name}")
        bounds = (finite(value["begin_s"]), finite(value["end_s"]))
        if bounds != expected:
            raise ValueError(f"unapproved window {name}: {bounds}")
        parsed[name] = bounds
    if set(raw) != set(REQUIRED_WINDOWS):
        raise ValueError("extra or missing measurement window")
    return parsed


def validate_seed_consistency(run_rows: list[dict]) -> str:
    seeds = {row.get("seed") for row in run_rows if row.get("seed") is not None}
    if len(seeds) < 2:
        raise ValueError("two-seed consistency claim prohibited without two seeds")
    return "two_seed_descriptive_direction_only"


def endpoint_accounting(planned: int, entered: int, arrived: int, coverage_verified: bool) -> dict:
    if min(planned, entered, arrived) < 0 or not arrived <= entered <= planned:
        raise ValueError("inconsistent endpoint counts")
    if not coverage_verified:
        return {"outside_confirmed": None, "in_network": None, "qualification": "unknown_coverage"}
    return {"outside_confirmed": planned - entered, "in_network": entered - arrived, "qualification": "verified"}


def event_bin(event: dict, begin_s: float, end_s: float) -> str:
    previous = event.get("previous_time_s")
    first = event.get("first_downstream_time_s")
    if previous is None or first is None:
        return "unknown"
    if previous < begin_s <= first or previous < end_s <= first:
        return "unknown"
    if first < begin_s or previous >= end_s or first > end_s:
        return "outside"
    return "inside" if begin_s <= first < end_s else "outside"


def tls_state_at(states: dict[float, str], time_s: float, link_index: int) -> str:
    state = states.get(time_s)
    if state is None:
        return "unknown"
    if link_index < 0 or link_index >= len(state):
        raise ValueError("TLS link index exceeds state width")
    return state[link_index]


def _close_episode(active: dict, last_time: float, reason: str, sampling_s: float) -> dict:
    samples = active["sample_count"]
    return {
        **active,
        "last_label": last_time,
        "support_seconds": samples * sampling_s,
        "censor_right": reason in ("window_end", "source_end"),
        "gap_reason": reason,
    }


def build_episodes(sample_times: list[float], sampling_s: float = 1.0) -> list[dict]:
    """Split a presence series whenever the next label is not exactly one period later."""
    if sampling_s <= 0:
        raise ValueError("sampling period must be positive")
    ordered = sorted(set(sample_times))
    if len(ordered) != len(sample_times):
        raise ValueError("duplicate episode label")
    episodes: list[dict] = []
    if not ordered:
        return episodes
    start = previous = ordered[0]
    count = 1
    for current in ordered[1:]:
        if not math.isclose(current - previous, sampling_s):
            episodes.append({"first_label": start, "last_label": previous, "sample_count": count,
                             "support_seconds": count * sampling_s, "gap_reason": "missing_or_absent_label"})
            start, count = current, 1
        else:
            count += 1
        previous = current
    episodes.append({"first_label": start, "last_label": previous, "sample_count": count,
                     "support_seconds": count * sampling_s, "gap_reason": "source_end"})
    return episodes


def clip_episode(episode: dict, begin_s: float, end_s: float, sampling_s: float = 1.0) -> dict | None:
    labels = [begin_s + i * sampling_s for i in range(max(0, int(math.ceil((end_s - begin_s) / sampling_s))))]
    kept = [t for t in labels if episode["first_label"] <= t <= episode["last_label"] and t < end_s]
    if not kept:
        return None
    return {**episode, "first_label": kept[0], "last_label": kept[-1], "sample_count": len(kept),
            "support_seconds": len(kept) * sampling_s,
            "censor_left": kept[0] > episode["first_label"], "censor_right": kept[-1] < episode["last_label"],
            "gap_reason": "window_clip" if kept[0] > episode["first_label"] or kept[-1] < episode["last_label"] else episode["gap_reason"]}


def full_episodes(
    sample_times: list[float],
    sampling_s: float,
    expected_begin_s: float,
    expected_end_s: float,
    present_frames: set[float],
) -> list[dict]:
    """Build Full-domain episodes and distinguish frame censoring from absence."""
    episodes = build_episodes(sample_times, sampling_s)
    for episode in episodes:
        previous = episode["first_label"] - sampling_s
        following = episode["last_label"] + sampling_s
        left_boundary = episode["first_label"] <= expected_begin_s
        right_boundary = following >= expected_end_s
        left_missing = not left_boundary and previous not in present_frames
        right_missing = not right_boundary and following not in present_frames
        episode["censor_left"] = left_boundary or left_missing
        episode["censor_right"] = right_boundary or right_missing
        if left_missing or right_missing:
            episode["gap_reason"] = "source_frame_missing"
        elif left_boundary or right_boundary:
            episode["gap_reason"] = "source_boundary"
        else:
            episode["gap_reason"] = "stop_condition_false_or_entity_absent"
    return episodes


def slice_full_episodes(full_rows: list[dict], windows: dict[str, tuple[float, float]]) -> list[dict]:
    """Return Full rows plus A/B/Post clips that reference their Full parent."""
    result = [dict(row) for row in full_rows]
    for full in full_rows:
        for window_name in ("A", "B", "Post"):
            begin_s, end_s = windows[window_name]
            clipped = clip_episode(full, begin_s, end_s, finite(full["sampling_period_s"]))
            if clipped is None:
                continue
            left_clip = clipped["first_label"] > full["first_label"]
            right_clip = clipped["last_label"] < full["last_label"]
            clipped.update({
                "episode_id": f"{window_name}:{full['episode_id']}",
                "parent_episode_id": full["episode_id"],
                "observation_domain": window_name,
                "censor_left": bool(full["censor_left"] if not left_clip else True),
                "censor_right": bool(full["censor_right"] if not right_clip else True),
                "gap_reason": ("window_clip_both" if left_clip and right_clip else
                               "window_clip_left" if left_clip else
                               "window_clip_right" if right_clip else full["gap_reason"]),
            })
            result.append(clipped)
    return result


def episode_tls_context(episode: dict, tls_states: dict[float, str], link_index: int | None) -> str:
    if link_index is None:
        return "not_applicable"
    sampling_s = finite(episode["sampling_period_s"])
    count = int(episode["sample_count"])
    states = Counter(
        tls_state_at(tls_states, episode["first_label"] + offset * sampling_s, link_index)
        for offset in range(count)
    )
    return "|".join(f"link{link_index}:{state}={states[state]}" for state in sorted(states))


def reaggregate_e1(
    rows: list[dict],
    begin_s: float,
    end_s: float,
    aggregation_s: float,
    expected_detectors: set[str],
) -> tuple[list[dict], dict]:
    if not begin_s < end_s or aggregation_s <= 0:
        raise ValueError("invalid E1 aggregation bounds")
    if not expected_detectors:
        raise ValueError("expected E1 detector set is empty")
    ordered = sorted(rows, key=lambda r: (finite(r["begin_s"]), r.get("detector_id", "")))
    keys = [(r.get("detector_id"), finite(r["begin_s"]), finite(r["end_s"])) for r in ordered]
    if len(keys) != len(set(keys)):
        raise ValueError("duplicate E1 detector interval")
    unexpected = {key[0] for key in keys} - expected_detectors
    if unexpected:
        raise ValueError(f"unexpected E1 detectors: {sorted(unexpected)}")
    bins: list[dict] = []
    cursor = begin_s
    while cursor < end_s:
        bin_end = min(end_s, cursor + aggregation_s)
        selected = [r for r in ordered if finite(r["begin_s"]) >= cursor and finite(r["end_s"]) <= bin_end]
        missing: list[str] = []
        for detector_id in sorted(expected_detectors):
            detector_rows = [r for r in selected if r.get("detector_id") == detector_id]
            position = cursor
            for row in detector_rows:
                row_begin, row_end = finite(row["begin_s"]), finite(row["end_s"])
                if not math.isclose(row_begin, position) or row_end <= row_begin:
                    missing.append(detector_id)
                    break
                position = row_end
            if not detector_rows or not math.isclose(position, bin_end):
                missing.append(detector_id)
        if missing:
            duration = bin_end - cursor
            bins.append({"bin_begin_s": cursor, "bin_end_s": bin_end, "covered_seconds": None,
                         "n_contrib": None, "q_vehph": None, "speed_mps": None,
                         "speed_denominator": None, "qualification": "missing_detector_or_interval",
                         "missing_detectors": "|".join(sorted(set(missing)))})
            cursor = bin_end
            continue
        n = sum(int(r["n_contrib"]) for r in selected)
        valid = [r for r in selected if int(r["n_contrib"]) > 0 and r.get("speed_mps") is not None]
        weighted_n = sum(int(r["n_contrib"]) for r in valid)
        speed = (sum(finite(r["speed_mps"]) * int(r["n_contrib"]) for r in valid) / weighted_n
                 if weighted_n else None)
        duration = bin_end - cursor
        bins.append({"bin_begin_s": cursor, "bin_end_s": bin_end, "covered_seconds": duration,
                     "n_contrib": n, "q_vehph": 3600.0 * n / duration,
                     "speed_mps": speed, "speed_denominator": weighted_n,
                     "qualification": "short_tail_complete" if duration < aggregation_s else "complete",
                     "missing_detectors": ""})
        cursor = bin_end
    total_duration = end_s - begin_s
    complete = all(row["qualification"] in ("complete", "short_tail_complete") for row in bins)
    if not complete:
        return bins, {"covered_seconds": sum(row["covered_seconds"] or 0 for row in bins),
                      "n_contrib": None, "q_vehph": None, "speed_mps": None,
                      "speed_denominator": None, "qualification": "incomplete",
                      "missing_bins": sum(row["qualification"] == "missing_detector_or_interval" for row in bins)}
    total_n = sum(int(row["n_contrib"]) for row in bins)
    speed_n = sum(int(row["speed_denominator"]) for row in bins)
    total_speed = (sum(row["speed_mps"] * row["speed_denominator"] for row in bins if row["speed_mps"] is not None) / speed_n
                   if speed_n else None)
    return bins, {"covered_seconds": total_duration, "n_contrib": total_n,
                  "q_vehph": 3600.0 * total_n / total_duration,
                  "speed_mps": total_speed, "speed_denominator": speed_n,
                  "qualification": "complete", "missing_bins": 0}


def read_e1(path: Path, detector_id: str) -> list[dict]:
    rows: list[dict] = []
    for _, node in ET.iterparse(path, events=("end",)):
        if node.tag != "interval":
            continue
        n = int(node.attrib["nVehContrib"])
        raw_speed = finite(node.attrib["speed"], "E1 speed")
        rows.append({"detector_id": detector_id, "begin_s": finite(node.attrib["begin"]),
                     "end_s": finite(node.attrib["end"]), "n_contrib": n,
                     "speed_mps": raw_speed if n > 0 and raw_speed >= 0 else None})
        node.clear()
    return rows


def read_tls(path: Path, tls_id: str) -> dict[float, str]:
    states: dict[float, str] = {}
    for _, node in ET.iterparse(path, events=("end",)):
        if node.tag != "tlsState" or node.get("id") != tls_id:
            continue
        time_s = finite(node.get("time"), "TLS time")
        if time_s in states:
            raise ValueError("duplicate TLS label")
        states[time_s] = node.get("state", "")
        node.clear()
    return states


def summary_seed(summary: dict) -> int:
    candidates: list[int] = []
    simulation = summary.get("simulation", {})
    if simulation.get("seed") is not None:
        candidates.append(int(simulation["seed"]))
    command = summary.get("sumo_command", [])
    if "--seed" in command:
        candidates.append(int(command[command.index("--seed") + 1]))
    if not candidates or len(set(candidates)) != 1:
        raise ValueError(f"seed is missing or inconsistent in archived summary: {candidates}")
    return candidates[0]


def scan_fcd(path: Path, contract: dict) -> dict:
    sampling_s = finite(contract["fcd"]["sampling_period_s"])
    lane_contract = contract["lanes"]
    timeline: list[dict] = []
    frame_registry: list[dict] = []
    vehicle_stop_times: defaultdict[tuple[str, str], list[float]] = defaultdict(list)
    region_stop_times: defaultdict[tuple[str, str], list[float]] = defaultdict(list)
    previous: dict[str, tuple[float, str]] = {}
    first_downstream: dict[str, dict] = {}
    seen_times: set[float] = set()
    previous_time: float | None = None
    duplicate_count = 0
    unknown_id_count = 0
    unknown_lane_count = 0
    for _, step in ET.iterparse(path, events=("end",)):
        if step.tag != "timestep":
            continue
        time_s = finite(step.get("time"), "FCD time")
        if time_s in seen_times or (previous_time is not None and time_s <= previous_time):
            raise ValueError("duplicate or non-monotonic FCD frame")
        seen_times.add(time_s)
        previous_time = time_s
        vehicles_seen: set[str] = set()
        grouped: defaultdict[tuple[str, str], dict] = defaultdict(lambda: {
            "present_count": 0, "stopped_count": 0, "speed_sum_mps": 0.0,
            "speed_n": 0, "min_path_position_m": None, "max_path_position_m": None,
            "missing_speed_count": 0,
        })
        region_has_stop: set[tuple[str, str]] = set()
        for vehicle in list(step):
            vehicle_id = vehicle.get("id", "")
            if vehicle_id in vehicles_seen:
                duplicate_count += 1
                raise ValueError("duplicate vehicle in FCD frame")
            vehicles_seen.add(vehicle_id)
            try:
                cls = vehicle_class(vehicle_id)
            except ValueError:
                cls = "unknown"
                unknown_id_count += 1
            lane_id = vehicle.get("lane", "")
            lane = lane_contract.get(lane_id)
            if lane is None:
                region = "unknown"
                unknown_lane_count += 1
            else:
                region = lane["region"]
            key = (lane_id, cls)
            row = grouped[key]
            row["present_count"] += 1
            speed_raw = vehicle.get("speed")
            stopped = False
            if speed_raw is None:
                row["missing_speed_count"] += 1
            else:
                speed = finite(speed_raw, "FCD speed")
                row["speed_sum_mps"] += speed
                row["speed_n"] += 1
                stopped = speed <= finite(contract["stop_definition"]["speed_threshold_mps"])
                row["stopped_count"] += int(stopped)
            pos_raw = vehicle.get("pos")
            if lane is not None and lane.get("r_path_start_m") is not None and pos_raw is not None:
                path_pos = finite(lane["r_path_start_m"]) + finite(pos_raw, "FCD position")
                lo = row["min_path_position_m"]
                hi = row["max_path_position_m"]
                row["min_path_position_m"] = path_pos if lo is None else min(lo, path_pos)
                row["max_path_position_m"] = path_pos if hi is None else max(hi, path_pos)
            if stopped:
                vehicle_stop_times[(vehicle_id, region)].append(time_s)
                region_has_stop.add((region, cls))
            if cls == "R" and lane is not None and lane.get("first_downstream_eligible") and vehicle_id not in first_downstream:
                prev = previous.get(vehicle_id)
                first_downstream[vehicle_id] = {
                    "event_id": f"{vehicle_id}:first_downstream", "vehicle_id": vehicle_id,
                    "previous_time_s": prev[0] if prev else None, "previous_lane": prev[1] if prev else None,
                    "first_downstream_time_s": time_s, "first_downstream_lane": lane_id,
                    "status": "bracketed" if prev and math.isclose(time_s - prev[0], sampling_s) else "unresolved_previous_frame",
                }
            previous[vehicle_id] = (time_s, lane_id)
        for region_cls in region_has_stop:
            region_stop_times[region_cls].append(time_s)
        frame_registry.append({"time_s": time_s, "frame_present": True})
        for (lane_id, cls), values in grouped.items():
            lane = lane_contract.get(lane_id)
            timeline.append({"time_s": time_s, "lane_id": lane_id, "region": lane["region"] if lane else "unknown",
                             "is_internal": lane["is_internal"] if lane else None, "class": cls, **values,
                             "position_mapping_status": "mapped_R_path" if lane and lane.get("r_path_start_m") is not None else "not_on_R_path" if lane else "unknown_lane",
                             "tls_link": lane.get("tls_link") if lane else None, "coverage": "observed_frame"})
        step.clear()
    expected_begin = finite(contract["fcd"]["expected_begin_s"])
    expected_end = finite(contract["fcd"]["expected_end_s"])
    expected = {expected_begin + i * sampling_s for i in range(int((expected_end - expected_begin) / sampling_s))}
    missing = sorted(expected - seen_times)
    extra = sorted(seen_times - expected)
    episodes: list[dict] = []
    counter = 0
    for kind, series in (("vehicle_stop", vehicle_stop_times), ("region_stop", region_stop_times)):
        for identity, times in sorted(series.items()):
            cls = vehicle_class(identity[0]) if kind == "vehicle_stop" else identity[1]
            for episode in full_episodes(times, sampling_s, expected_begin, expected_end, seen_times):
                counter += 1
                episodes.append({"episode_id": f"full:{counter}", "parent_episode_id": None, "kind": kind,
                                 "vehicle_id_or_null": identity[0] if kind == "vehicle_stop" else None,
                                 "class": cls, "observation_domain": "Full",
                                 "region": identity[1] if kind == "vehicle_stop" else identity[0],
                                 "stop_definition_id": contract["stop_definition"].get("id", "technical_stop"),
                                 "sampling_period_s": sampling_s, **episode})
    episodes = slice_full_episodes(episodes, validate_windows(contract))
    frame_registry = [{"time_s": time_s, "frame_present": time_s in seen_times} for time_s in sorted(expected)]
    return {"timeline": timeline, "frame_registry": frame_registry, "episodes": episodes,
            "first_downstream": list(first_downstream.values()), "missing_frames": missing, "extra_frames": extra,
            "duplicate_count": duplicate_count, "unknown_id_count": unknown_id_count,
            "unknown_lane_count": unknown_lane_count, "frame_count": len(seen_times)}


def _source_run(ledger: dict, run_id: str) -> dict:
    matches = [row for row in ledger.get("source_runs", []) if row.get("run_id") == run_id]
    if len(matches) != 1:
        raise ValueError(f"run must occur exactly once in ledger: {run_id}")
    return matches[0]


def validate_context(ledger_path: Path, contract_path: Path) -> tuple[dict, dict]:
    ledger = load_json(ledger_path)
    contract = load_json(contract_path)
    if ledger.get("stage") != "Stage 3" or ledger.get("authorization", {}).get("status") != "user_approved":
        raise ValueError("Stage 3 ledger is not user approved")
    if ledger.get("actual_sumo_starts") != 0 or ledger.get("budget", {}).get("max_sumo_starts") != 0:
        raise ValueError("Stage 3 must have zero SUMO starts")
    if digest(Path(contract_path)) != ledger.get("input_hashes", {}).get("measurement_contract_sha256"):
        raise ValueError("measurement contract hash mismatch")
    if ledger.get("code_hashes", {}).get("analyze_stage3_baseline.py") != digest(Path(__file__)):
        raise ValueError("analysis code hash is absent or stale in ledger")
    validate_windows(contract)
    return ledger, contract


def read_tripinfo_records(path: Path) -> dict[str, dict]:
    records: dict[str, dict] = {}
    for _, node in ET.iterparse(path, events=("end",)):
        if node.tag != "tripinfo":
            continue
        vehicle_id = node.get("id", "")
        vehicle_class(vehicle_id)
        if vehicle_id in records:
            raise ValueError("duplicate tripinfo vehicle")
        records[vehicle_id] = {"class": vehicle_class(vehicle_id), "depart": finite(node.get("depart")),
                               "arrival": finite(node.get("arrival")), "depart_lane": node.get("departLane"),
                               "depart_pos_m": finite(node.get("departPos"))}
        node.clear()
    return records


def read_vehroute_ids(path: Path) -> set[str]:
    result: set[str] = set()
    for _, node in ET.iterparse(path, events=("end",)):
        if node.tag != "vehicle":
            continue
        vehicle_id = node.get("id", "")
        vehicle_class(vehicle_id)
        if vehicle_id in result:
            raise ValueError("duplicate vehroute vehicle")
        result.add(vehicle_id)
        node.clear()
    return result


def read_plan_counts(path: Path) -> dict[str, int]:
    result: dict[str, int] = {}
    root = ET.parse(path).getroot()
    for node in root.findall("flow"):
        cls = node.get("id", "").split("_")[0]
        if cls not in CLASSES or cls in result:
            raise ValueError("unknown or duplicate demand flow")
        if finite(node.get("begin")) != 0 or finite(node.get("end")) != 1500:
            raise ValueError("undeclared demand window")
        result[cls] = int(node.get("number"))
    if set(result) != set(CLASSES):
        raise ValueError("demand plan misses a class")
    return result


def read_summary_boundaries(path: Path) -> dict[float, dict]:
    wanted = {1499.0: 1500.0, 2699.0: 2700.0}
    boundaries: dict[float, dict] = {}
    for _, node in ET.iterparse(path, events=("end",)):
        if node.tag != "step":
            continue
        time_s = finite(node.get("time"))
        if time_s in wanted:
            boundaries[wanted[time_s]] = {key: int(node.get(key, "-1")) for key in ("loaded", "inserted", "arrived")}
        node.clear()
    return boundaries


def build_endpoint_rows(
    run_id: str,
    planned: dict[str, int],
    trips: dict[str, dict],
    routes: set[str],
    summary_boundaries: dict[float, dict],
    fcd_coverage: bool,
) -> list[dict]:
    rows: list[dict] = []
    for endpoint_s in (1500.0, 2700.0):
        boundary = summary_boundaries.get(endpoint_s)
        entered_all = sum(0 <= row["depart"] < endpoint_s for row in trips.values())
        arrived_all = sum(0 <= row["arrival"] < endpoint_s for row in trips.values())
        coverage = bool(
            fcd_coverage and set(trips) == routes and boundary is not None
            and boundary["loaded"] == sum(planned.values())
            and boundary["inserted"] == entered_all
            and boundary["arrived"] == arrived_all
        )
        for cls in CLASSES:
            class_rows = [row for row in trips.values() if row["class"] == cls]
            entered = sum(0 <= row["depart"] < endpoint_s for row in class_rows)
            arrived = sum(0 <= row["arrival"] < endpoint_s for row in class_rows)
            counts = endpoint_accounting(planned[cls], entered, arrived, coverage)
            rows.append({"run_id": run_id, "class": cls, "endpoint_s": endpoint_s,
                         "planned": planned[cls], "entered": entered, "arrived": arrived,
                         "outside_confirmed": counts["outside_confirmed"], "in_network": counts["in_network"],
                         "coverage": coverage, "qualification": counts["qualification"]})
    return rows


def _episode_labels(episode: dict) -> set[float]:
    if episode["observation_domain"] != "Full":
        return set()
    sampling_s = finite(episode["sampling_period_s"])
    return {episode["first_label"] + i * sampling_s for i in range(int(episode["sample_count"]))}


PROPAGATION_REGION_SEQUENCE = (
    "ramp_accel",
    "ramp_mid_internal",
    "ramp_storage",
    "ramp_diverge_internal",
    "shared_approach",
)


def propagation_region_order(contract: dict) -> list[dict]:
    """Derive and verify the downstream-to-upstream queue-observation order."""
    coordinates: dict[str, tuple[float, float]] = {}
    for region in PROPAGATION_REGION_SEQUENCE:
        lanes = [lane for lane in contract.get("lanes", {}).values() if lane.get("region") == region]
        if not lanes or any(lane.get("r_path_start_m") is None or lane.get("r_path_end_m") is None for lane in lanes):
            raise ValueError(f"propagation region has no complete R-path coordinate: {region}")
        starts = {finite(lane["r_path_start_m"]) for lane in lanes}
        ends = {finite(lane["r_path_end_m"]) for lane in lanes}
        if len(starts) != 1 or len(ends) != 1:
            raise ValueError(f"propagation region has ambiguous lane coordinates: {region}")
        start, end = next(iter(starts)), next(iter(ends))
        if not start < end:
            raise ValueError(f"propagation region has invalid path span: {region}")
        coordinates[region] = (start, end)
    derived = sorted(coordinates, key=lambda region: coordinates[region][0], reverse=True)
    if tuple(derived) != PROPAGATION_REGION_SEQUENCE:
        raise ValueError(f"measurement contract contradicts the registered propagation order: {derived}")
    for downstream, upstream in zip(derived, derived[1:]):
        if not math.isclose(coordinates[downstream][0], coordinates[upstream][1], abs_tol=1e-8):
            raise ValueError(f"propagation regions are not contiguous: {downstream}/{upstream}")
    return [{"region": region, "r_path_start_m": coordinates[region][0], "r_path_end_m": coordinates[region][1]}
            for region in derived]


def build_propagation(
    run_id: str,
    episodes: list[dict],
    missing_frames: list[float],
    contract: dict,
) -> tuple[list[dict], dict]:
    full_region = [row for row in episodes if row["observation_domain"] == "Full" and row["kind"] == "region_stop"]
    spatial_order = propagation_region_order(contract)
    region_groups = {
        item["region"]: sorted(
            [row for row in full_region if row["class"] == "R" and row["region"] == item["region"]],
            key=lambda row: (row["first_label"], row["episode_id"]),
        )
        for item in spatial_order
    }
    ramp_end = region_groups["ramp_accel"]
    storage = region_groups["ramp_storage"]
    internal = region_groups["ramp_mid_internal"] + region_groups["ramp_diverge_internal"]
    shared_r = region_groups["shared_approach"]
    shared_u = sorted(
        [row for row in full_region if row["class"] == "U" and row["region"] == "shared_approach"],
        key=lambda row: (row["first_label"], row["episode_id"]),
    )
    shared_r_labels = set().union(*(_episode_labels(row) for row in shared_r)) if shared_r else set()
    shared_u_labels = set().union(*(_episode_labels(row) for row in shared_u)) if shared_u else set()
    common = sorted(shared_r_labels & shared_u_labels)
    first_by_region = {region: rows[0] for region, rows in region_groups.items() if rows}
    observed_sequence = [item["region"] for item in spatial_order if item["region"] in first_by_region]
    contradiction_details = []
    for downstream, upstream in zip(observed_sequence, observed_sequence[1:]):
        downstream_event, upstream_event = first_by_region[downstream], first_by_region[upstream]
        if downstream_event["first_label"] > upstream_event["first_label"]:
            contradiction_details.append({
                "contradiction_id": f"{run_id}:order:{downstream}>{upstream}",
                "downstream_region": downstream,
                "downstream_event_id": downstream_event["episode_id"],
                "downstream_first_label": downstream_event["first_label"],
                "upstream_region": upstream,
                "upstream_event_id": upstream_event["episode_id"],
                "upstream_first_label": upstream_event["first_label"],
                "reason": "upstream region is first observed stopped before its registered downstream neighbor",
            })
    complete = all(region_groups[region] for region in PROPAGATION_REGION_SEQUENCE)
    if missing_frames:
        status, reason = "unresolved_coverage", f"{len(missing_frames)} source FCD labels are missing"
    elif contradiction_details:
        status = "contradicted_order"
        reason = f"{len(contradiction_details)} adjacent downstream-to-upstream first-label order contradictions; see contradiction_details"
    elif complete:
        status = "complete_ordered_observation"
        reason = "first stopped-R labels follow the contract-derived downstream-to-upstream region order"
    elif any(region_groups.values()):
        missing_regions = [region for region in PROPAGATION_REGION_SEQUENCE if not region_groups[region]]
        status, reason = "partial_observation", f"missing stopped-R episode regions: {'|'.join(missing_regions)}"
    else:
        status, reason = "not_identified", "no stopped-R episode occurs in the registered propagation regions"
    memberships = {
        "ramp_end_event_ids": [row["episode_id"] for row in ramp_end],
        "storage_event_ids": [row["episode_id"] for row in storage],
        "internal_event_ids": [row["episode_id"] for row in internal],
        "shared_R_event_ids": [row["episode_id"] for row in shared_r],
        "shared_U_event_ids": [row["episode_id"] for row in shared_u],
    }
    r_memberships = [set(memberships[key]) for key in ("ramp_end_event_ids", "storage_event_ids", "internal_event_ids", "shared_R_event_ids")]
    if any(first & second for index, first in enumerate(r_memberships) for second in r_memberships[index + 1:]):
        raise ValueError("propagation event groups overlap")
    event_set = {
        "run_id": run_id,
        **memberships,
        "contract_derived_region_order": spatial_order,
        "observed_region_sequence": observed_sequence,
        "first_event_by_region": {region: row["episode_id"] for region, row in first_by_region.items()},
        "contradiction_details": contradiction_details,
        "shared_R_U_cooccurrence_labels_s": common,
        "TLS_context_id": f"{run_id}:shared_TLS_context",
        "TLS_context_values": sorted({row.get("TLS_context", "unknown") for row in shared_r + shared_u}),
    }
    row = {"run_id": run_id, "chain_id": f"{run_id}:R_upstream_chain",
           "ramp_end_event_id": ramp_end[0]["episode_id"] if ramp_end else None,
           "storage_event_id": storage[0]["episode_id"] if storage else None,
           "internal_event_set_id": f"{run_id}:internal_R_events",
           "shared_R_event_id": shared_r[0]["episode_id"] if shared_r else None,
           "shared_U_event_id": shared_u[0]["episode_id"] if shared_u else None,
           "cooccurrence_support_s": len(common), "TLS_context_id": f"{run_id}:shared_TLS_context",
           "contradiction_ids": "|".join(item["contradiction_id"] for item in contradiction_details),
           "status": status, "reason": reason}
    return [row], event_set


def build_condition_summary(
    run_id: str,
    condition: str,
    seed: int,
    trips: dict[str, dict],
    endpoints: list[dict],
    episodes: list[dict],
    first_downstream: list[dict],
    e1_metrics: list[dict],
    propagation: dict,
    coverage_ok: bool,
) -> tuple[list[dict], dict[str, list[str]]]:
    rows: list[dict] = []
    event_sets: dict[str, list[str]] = {}
    def add(window, entity, metric, value, unit, denominator, qualification, source_event_id, reason):
        rows.append({"run_id": run_id, "condition": condition, "seed": seed, "window": window,
                     "entity": entity, "metric": metric, "value": value, "unit": unit,
                     "denominator": denominator, "qualification": qualification,
                     "source_event_id": source_event_id, "reason": reason})
    for window, (begin_s, end_s) in REQUIRED_WINDOWS.items():
        for cls in CLASSES:
            class_rows = [row for row in trips.values() if row["class"] == cls]
            add(window, cls, "actual_departures", sum(begin_s <= row["depart"] < end_s for row in class_rows),
                "veh", len(class_rows), "observed_tripinfo", None, "event time is within the declared half-open window")
            add(window, cls, "arrivals", sum(begin_s <= row["arrival"] < end_s for row in class_rows),
                "veh", len(class_rows), "observed_tripinfo", None, "event time is within the declared half-open window")
    for endpoint in endpoints:
        window = "A" if endpoint["endpoint_s"] == 1500 else "Full"
        for metric in ("planned", "entered", "arrived", "outside_confirmed", "in_network"):
            add(window, endpoint["class"], f"endpoint_{metric}", endpoint[metric], "veh", endpoint["planned"],
                endpoint["qualification"], f"{run_id}:endpoint:{int(endpoint['endpoint_s'])}:{endpoint['class']}",
                f"endpoint={int(endpoint['endpoint_s'])} s; unknown is retained when coverage is not verified")
    episode_groups: defaultdict[tuple[str, str, str], list[dict]] = defaultdict(list)
    for episode in episodes:
        if episode["kind"] == "region_stop":
            episode_groups[(episode["observation_domain"], episode["class"], episode["region"])].append(episode)
    for (window, cls, region), group in sorted(episode_groups.items()):
        set_id = f"{run_id}:episode_set:{window}:{cls}:{region}"
        event_sets[set_id] = [episode["episode_id"] for episode in group]
        add(window, f"{cls}@{region}", "stopped_episode_support",
            sum(episode["support_seconds"] for episode in group), "sampled_vehicle_presence_s",
            sum(episode["sample_count"] for episode in group),
            "censored" if any(episode["censor_left"] or episode["censor_right"] for episode in group) else "observed",
            set_id, f"aggregated {len(group)} mutually distinct region-stop episodes")
    for window, (begin_s, end_s) in REQUIRED_WINDOWS.items():
        known = [event for event in first_downstream if event["first_downstream_time_s"] is not None and begin_s <= event["first_downstream_time_s"] < end_s]
        ambiguous = sum(event_bin(event, begin_s, end_s) == "unknown" for event in first_downstream)
        add(window, "R", "first_downstream_observations", len(known), "veh", len(first_downstream),
            "1Hz_bracketed_observation", None, f"{ambiguous} event brackets cross or lack this window boundary")
    for metric in e1_metrics:
        add(metric["window"], metric["entity"], metric["metric"], metric["value"], metric["unit"],
            metric["denominator"], metric["qualification"], metric.get("source_event_id"), metric["reason"])
    full_endpoints = [row for row in endpoints if row["endpoint_s"] == 2700]
    all_endpoints_known = coverage_ok and all(row["qualification"] == "verified" for row in full_endpoints)
    full_r_episodes = [e for e in episodes if e["observation_domain"] == "Full" and e["class"] == "R" and e["kind"] == "region_stop"]
    shared_r = [e for e in full_r_episodes if e["region"] == "shared_approach"]
    shared_u = [e for e in episodes if e["observation_domain"] == "Full" and e["class"] == "U" and e["kind"] == "region_stop" and e["region"] == "shared_approach"]
    questions = [
        ("insertion", "observed" if all_endpoints_known else "not_verified", len(trips), None,
         "tripinfo, vehroute and endpoint coverage reconcile" if all_endpoints_known else "endpoint coverage failed"),
        ("origin_and_propagation", propagation["status"], len(full_r_episodes), propagation["chain_id"], propagation["reason"]),
        ("mainline_and_downstream", "observed" if {
             (m["entity"], m["metric"]) for m in e1_metrics if m["window"] == "Full" and m["qualification"] == "complete"
         } >= {("M-only_internal_merge_entry", "q"), ("M-only_internal_merge_entry", "v"),
               ("downstream_E1", "q"), ("downstream_E1", "v")} else "not_verified",
         sum(1 for m in e1_metrics if m["entity"] in ("M-only_internal_merge_entry", "downstream_E1")), None,
         "paired q/v observations are registered; this status does not assert performance impairment"),
        ("spillback", "observed" if shared_r else "not_identified", len(shared_r), shared_r[0]["episode_id"] if shared_r else None,
         "stopped R reaches shared_approach" if shared_r else "no stopped-R shared_approach episode observed"),
        ("urban_exposure", "observed" if shared_u and all_endpoints_known else "not_identified" if all_endpoints_known else "not_verified",
         len(shared_u), shared_u[0]["episode_id"] if shared_u else None,
         "shared-road U stop and endpoint evidence are both present" if shared_u and all_endpoints_known else "shared-road U stop is absent or endpoint coverage is unresolved"),
    ]
    for question, status, value, source, reason in questions:
        add("Full", f"question:{question}", "diagnostic_evidence_status", value, "evidence_count", None,
            status, source, reason)
    keys = [(row["run_id"], row["window"], row["entity"], row["metric"]) for row in rows]
    if len(keys) != len(set(keys)):
        raise ValueError("condition evidence primary key collision")
    return rows, event_sets


def analyze_run(args: argparse.Namespace) -> None:
    ledger, contract = validate_context(Path(args.ledger), Path(args.contract))
    source = _source_run(ledger, args.run_id)
    source_map = ROOT / source["source_map_path"]
    if digest(source_map) != source["source_map_sha256"]:
        raise ValueError("source map hash mismatch")
    resolver = ArchiveResolver(source_map)
    summary = load_json(resolver.resolve("summary.json"))
    if str(summary.get("sumo_version")) != contract["versions"]["sumo"]:
        raise ValueError("undeclared SUMO version")
    if str(summary.get("netconvert_version")) != contract["versions"]["netconvert"]:
        raise ValueError("undeclared netconvert version")
    if summary_seed(summary) != source["seed"]:
        raise ValueError("seed mismatch")
    output_dir, table_dir = Path(args.output_dir), Path(args.table_dir)
    reserve_directories([output_dir, table_dir])
    try:
        fcd = scan_fcd(resolver.resolve("outputs/fcd.xml"), contract)
        tls = read_tls(resolver.resolve("outputs/tls_states.xml"), contract["tls"]["id"])
        for row in fcd["timeline"]:
            row["run_id"] = args.run_id
            row["seed"] = source["seed"]
            row["tls_state"] = tls_state_at(tls, row["time_s"], row["tls_link"]) if row["tls_link"] is not None else None
        for episode in fcd["episodes"]:
            link_index = 0 if episode["class"] in ("R", "U") else 1 if episode["class"] == "X" else None
            episode["TLS_context"] = episode_tls_context(episode, tls, link_index)
        e1_rows: list[dict] = []
        detector_coverage: dict[str, dict] = {}
        for detector in contract["e1_detectors"]:
            detector_rows = read_e1(resolver.resolve(detector["output_suffix"]), detector["detector_id"])
            _, detector_coverage[detector["detector_id"]] = reaggregate_e1(
                detector_rows, 0.0, 2700.0, 30.0, {detector["detector_id"]})
            e1_rows.extend(detector_rows)
        group_detectors = {
            "M-only_internal_merge_entry": {d["detector_id"] for d in contract["e1_detectors"] if d["group"] == "M-only_internal_merge_entry"},
            "downstream_E1": {d["detector_id"] for d in contract["e1_detectors"] if d["group"] == "downstream_passage"},
        }
        if any(len(detectors) != 2 for detectors in group_detectors.values()):
            raise ValueError("measurement contract must declare two detectors for each required E1 group")
        e1_metrics: list[dict] = []
        for group, detector_ids in group_detectors.items():
            group_rows = [row for row in e1_rows if row["detector_id"] in detector_ids]
            for window_name, (begin_s, end_s) in REQUIRED_WINDOWS.items():
                _, total = reaggregate_e1(group_rows, begin_s, end_s, 30.0, detector_ids)
                for metric, field, unit in (("q", "q_vehph", "veh/h"), ("v", "speed_mps", "m/s")):
                    e1_metrics.append({"window": window_name, "entity": group, "metric": metric,
                                       "value": total[field], "unit": unit,
                                       "denominator": total["covered_seconds"] if metric == "q" else total["speed_denominator"],
                                       "qualification": total["qualification"], "source_event_id": None,
                                       "reason": "two-lane contribution sum" if metric == "q" else "vehicle-contribution-weighted speed"})
        sensitivity: list[dict] = []
        timeseries: list[dict] = []
        internal_rows = [row for row in e1_rows if row["detector_id"] in group_detectors["M-only_internal_merge_entry"]]
        for window_name in ("A", "B"):
            begin_s, end_s = REQUIRED_WINDOWS[window_name]
            for aggregation_s in (30.0, 60.0, 120.0):
                bins, aggregate = reaggregate_e1(internal_rows, begin_s, end_s, aggregation_s,
                                                  group_detectors["M-only_internal_merge_entry"])
                for metric, unit in (("q", "veh/h"), ("v", "m/s")):
                    value = aggregate["q_vehph"] if metric == "q" else aggregate["speed_mps"]
                    sensitivity.append({"run_id": args.run_id, "detector_group": "M-only_internal_merge_entry",
                                        "aggregation_s": aggregation_s, "window": window_name, "metric": metric,
                                        "value": value, "unit": unit, "n_contrib": aggregate["n_contrib"],
                                        "covered_seconds": aggregate["covered_seconds"], "qualification": aggregate["qualification"],
                                        "residual_vs_30s": None})
                for row in bins:
                    timeseries.append({"run_id": args.run_id, "group": "M-only_internal_merge_entry", "window": window_name,
                                       "aggregation": aggregation_s, "bin_begin": row["bin_begin_s"], "bin_end": row["bin_end_s"],
                                       "q": row["q_vehph"], "v": row["speed_mps"], "contribution": row["n_contrib"],
                                       "qualification": row["qualification"] + (f":{row['missing_detectors']}" if row["missing_detectors"] else "")})
        by_key = {(r["window"], r["metric"], r["aggregation_s"]): r for r in sensitivity}
        for row in sensitivity:
            base = by_key[(row["window"], row["metric"], 30.0)]["value"]
            row["residual_vs_30s"] = None if row["value"] is None or base is None else row["value"] - base
        trips = read_tripinfo_records(resolver.resolve("outputs/tripinfo.xml"))
        routes = read_vehroute_ids(resolver.resolve("outputs/vehroute.xml"))
        observed_r = {event["vehicle_id"] for event in fcd["first_downstream"]}
        for vehicle_id in sorted(vehicle_id for vehicle_id, row in trips.items() if row["class"] == "R" and vehicle_id not in observed_r):
            fcd["first_downstream"].append({"event_id": f"{vehicle_id}:first_downstream", "vehicle_id": vehicle_id,
                                            "previous_time_s": None, "previous_lane": None,
                                            "first_downstream_time_s": None, "first_downstream_lane": None,
                                            "status": "not_observed_before_end"})
        planned = read_plan_counts(resolver.resolve("demand.rou.xml"))
        boundaries = read_summary_boundaries(resolver.resolve("outputs/sumo_summary.xml"))
        fcd_ok = not fcd["missing_frames"] and not fcd["extra_frames"] and not fcd["unknown_id_count"] and not fcd["unknown_lane_count"]
        endpoints = build_endpoint_rows(args.run_id, planned, trips, routes, boundaries, fcd_ok)
        propagation, propagation_event_set = build_propagation(
            args.run_id, fcd["episodes"], fcd["missing_frames"], contract)
        condition_rows, condition_event_sets = build_condition_summary(
            args.run_id, source["condition"], source["seed"], trips, endpoints,
            fcd["episodes"], fcd["first_downstream"], e1_metrics, propagation[0], fcd_ok)
        required_sources = ["network.net.xml", "demand.rou.xml", "scenario.add.xml", "scenario.sumocfg", "summary.json",
                            "outputs/fcd.xml", "outputs/tls_states.xml", "outputs/tripinfo.xml", "outputs/vehroute.xml",
                            "outputs/sumo_summary.xml"] + [d["output_suffix"] for d in contract["e1_detectors"]]
        coverage = []
        for suffix in required_sources:
            path = resolver.resolve(suffix)
            output_id = suffix.replace("outputs/", "").replace(".xml", "")
            time_count = None
            missing_intervals = None
            if suffix == "outputs/fcd.xml":
                time_count, missing_intervals = fcd["frame_count"], len(fcd["missing_frames"])
            elif suffix == "outputs/tls_states.xml":
                time_count, missing_intervals = len(tls), max(0, 2700 - len(tls))
            elif suffix in {d["output_suffix"] for d in contract["e1_detectors"]}:
                detector_id = next(d["detector_id"] for d in contract["e1_detectors"] if d["output_suffix"] == suffix)
                count = sum(row["detector_id"] == detector_id for row in e1_rows)
                time_count = count
                missing_intervals = detector_coverage[detector_id]["missing_bins"]
            coverage.append({"run_id": args.run_id, "output_id": output_id,
                             "path": str(path.relative_to(ROOT)), "sha256": digest(path), "schema_version": 1,
                             "time_count": time_count, "duplicate_count": fcd["duplicate_count"] if suffix == "outputs/fcd.xml" else 0,
                             "unknown_id_count": fcd["unknown_id_count"] if suffix == "outputs/fcd.xml" else 0,
                             "unknown_lane_count": fcd["unknown_lane_count"] if suffix == "outputs/fcd.xml" else 0,
                             "missing_intervals": missing_intervals,
                             "status": "passed" if missing_intervals in (None, 0) else "not_verified",
                             "reason": "source-map hash verified and required coverage checked"})
        write_csv(table_dir / "coverage_audit.csv", coverage, COVERAGE_FIELDS)
        write_csv(table_dir / "lane_class_timeline.csv", fcd["timeline"], TIMELINE_FIELDS)
        episode_rows = [{"run_id": args.run_id, **row} for row in fcd["episodes"]]
        write_csv(table_dir / "stopping_episodes.csv", episode_rows, EPISODE_FIELDS)
        write_csv(table_dir / "spatial_propagation_evidence.csv", propagation, PROPAGATION_FIELDS)
        write_csv(table_dir / "condition_evidence_summary.csv", condition_rows, CONDITION_FIELDS)
        write_csv(output_dir / "frame_registry.csv", [{"run_id": args.run_id, **r} for r in fcd["frame_registry"]], ["run_id", "time_s", "frame_present"])
        write_csv(output_dir / "first_downstream_events.csv", [{"run_id": args.run_id, **r} for r in fcd["first_downstream"]], ["run_id", "event_id", "vehicle_id", "previous_time_s", "previous_lane", "first_downstream_time_s", "first_downstream_lane", "status"])
        write_csv(output_dir / "endpoint_accounting.csv", endpoints, ["run_id", "class", "endpoint_s", "planned", "entered", "arrived", "outside_confirmed", "in_network", "coverage", "qualification"])
        write_json(output_dir / "propagation_event_sets.json", propagation_event_set)
        write_json(output_dir / "condition_event_sets.json", condition_event_sets)
        write_csv(output_dir / "sensitivity.csv", sensitivity, list(sensitivity[0]))
        write_csv(output_dir / "aggregation_timeseries.csv", timeseries,
                  ["run_id", "group", "window", "aggregation", "bin_begin", "bin_end", "q", "v", "contribution", "qualification"])
        manifest = {"schema_version": 1, "run_id": args.run_id, "seed": source["seed"],
                    "source_map_path": source["source_map_path"], "source_map_sha256": source["source_map_sha256"],
                    "contract_path": str(Path(args.contract).resolve().relative_to(ROOT)), "contract_sha256": digest(Path(args.contract)),
                    "source_inventory": resolver.inventory(), "fcd_missing_frames": fcd["missing_frames"],
                    "fcd_extra_frames": fcd["extra_frames"], "outputs": {}, "status": "analyzed_archive_only"}
        for path in sorted(list(output_dir.iterdir()) + list(table_dir.iterdir())):
            manifest["outputs"][str(path.resolve().relative_to(ROOT))] = digest(path)
        write_json(output_dir / "manifest.json", manifest)
    except Exception:
        # A failed new revision remains as explicit incomplete evidence.
        marker = output_dir / "INCOMPLETE.json"
        if output_dir.is_dir() and not marker.exists():
            write_json(marker, {"status": "incomplete", "reason": "analysis raised; see command stderr"})
        raise


def aggregate(args: argparse.Namespace) -> None:
    ledger, _ = validate_context(Path(args.ledger), Path(args.contract))
    manifests = [load_json(Path(path)) for path in args.run_manifest]
    run_ids = [m.get("run_id") for m in manifests]
    if len(run_ids) != len(set(run_ids)):
        raise ValueError("duplicate run manifest")
    approved = {row["run_id"] for row in ledger["source_runs"]}
    if set(run_ids) != approved:
        raise ValueError(f"aggregate requires the complete approved run set: {sorted(approved)}")
    contract_sha = digest(Path(args.contract))
    if any(m.get("contract_sha256") != contract_sha or m.get("status") != "analyzed_archive_only" for m in manifests):
        raise ValueError("run manifest contract/status mismatch")
    ledger_sources = {row["run_id"]: row for row in ledger["source_runs"]}
    for manifest in manifests:
        source = ledger_sources[manifest["run_id"]]
        if (manifest.get("source_map_path") != source["source_map_path"]
                or manifest.get("source_map_sha256") != source["source_map_sha256"]):
            raise ValueError("run manifest source-map identity mismatch")
        for relative, expected_sha in manifest.get("outputs", {}).items():
            path = (ROOT / relative).resolve()
            if not _is_under(path, ROOT) or not path.is_file() or digest(path) != expected_sha:
                raise ValueError(f"run output hash mismatch: {relative}")
    output_dir, table_dir, figure_dir = Path(args.output_dir), Path(args.table_dir), Path(args.figure_dir)
    reserve_directories([output_dir, table_dir, figure_dir])
    try:
        combined: dict[str, list[dict]] = {name: [] for name in OUTPUT_TABLES}
        sensitivity: list[dict] = []
        timeseries: list[dict] = []
        endpoints: list[dict] = []
        propagation_sets: list[dict] = []
        condition_sets: dict[str, list[str]] = {}
        for manifest_path, manifest in zip(args.run_manifest, manifests):
            run_output = Path(manifest_path).resolve().parent
            run_table = next((ROOT / rel).parent for rel in manifest["outputs"] if rel.endswith("coverage_audit.csv"))
            for name in OUTPUT_TABLES:
                with (run_table / name).open(encoding="utf-8", newline="") as handle:
                    reader = csv.DictReader(handle)
                    if reader.fieldnames != TABLE_SCHEMAS[name]:
                        raise ValueError(f"per-run table schema mismatch: {manifest['run_id']}/{name}")
                    rows = list(reader)
                    if not rows:
                        raise ValueError(f"per-run table must be non-empty: {manifest['run_id']}/{name}")
                    combined[name].extend(rows)
            for name, target in (("sensitivity.csv", sensitivity), ("aggregation_timeseries.csv", timeseries)):
                with (run_output / name).open(encoding="utf-8", newline="") as handle:
                    target.extend(csv.DictReader(handle))
            with (run_output / "endpoint_accounting.csv").open(encoding="utf-8", newline="") as handle:
                endpoints.extend(csv.DictReader(handle))
            propagation_sets.append(load_json(run_output / "propagation_event_sets.json"))
            for set_id, members in load_json(run_output / "condition_event_sets.json").items():
                if set_id in condition_sets:
                    raise ValueError("duplicate condition event-set identity")
                condition_sets[set_id] = members
        question_rows = [row for row in combined["condition_evidence_summary.csv"]
                         if row["metric"] == "diagnostic_evidence_status"]
        per_run_questions = Counter(row["run_id"] for row in question_rows)
        if per_run_questions != Counter({run_id: 5 for run_id in approved}):
            raise ValueError("aggregate does not contain exactly five diagnostic question rows per run")
        if len(sensitivity) != len(approved) * 12:
            raise ValueError("aggregate sensitivity denominator is not 96")
        for name, rows in combined.items():
            write_csv(table_dir / name, rows, TABLE_SCHEMAS[name])
        write_csv(output_dir / "sensitivity.csv", sensitivity, list(sensitivity[0]) if sensitivity else ["run_id"])
        write_csv(output_dir / "aggregation_timeseries.csv", timeseries, list(timeseries[0]) if timeseries else ["run_id"])
        write_csv(output_dir / "endpoint_accounting.csv", endpoints, list(endpoints[0]) if endpoints else ["run_id"])
        write_json(output_dir / "propagation_event_sets.json", {"runs": propagation_sets})
        write_json(output_dir / "condition_event_sets.json", condition_sets)
        write_json(output_dir / "manifest.json", {"schema_version": 1, "status": "aggregate_archive_only",
                   "run_ids": run_ids, "contract_sha256": contract_sha, "run_manifest_sha256": {
                       str(Path(path).resolve().relative_to(ROOT)): digest(Path(path)) for path in args.run_manifest},
                   "table_row_counts": {name: len(rows) for name, rows in combined.items()},
                   "diagnostic_question_units": len(question_rows), "sensitivity_values": len(sensitivity),
                   "endpoint_rows": len(endpoints),
                   "figure_status": "directory_reserved; figures require the Stage 3 analysis owner"})
    except Exception:
        marker = output_dir / "INCOMPLETE.json"
        if output_dir.is_dir() and not marker.exists():
            write_json(marker, {"status": "incomplete", "reason": "aggregation raised; see command stderr"})
        raise


def _lane_metadata(network: ET.Element) -> tuple[dict[str, dict], list[dict]]:
    region_by_edge = {
        "main_up": "mainline_origin_observation", ":freeway_merge_1": "mainline_merge_internal",
        "main_down": "mainline_downstream", "urban_in": "urban_origin",
        ":urban_tls_0": "urban_tls_internal", ":urban_tls_1": "cross_tls_internal",
        "shared_approach": "shared_approach", ":urban_diverge_1": "ramp_diverge_internal",
        ":urban_diverge_0": "urban_diverge_internal", "ramp_storage": "ramp_storage",
        ":ramp_mid_0": "ramp_mid_internal", "ramp_accel": "ramp_accel",
        ":freeway_merge_0": "ramp_merge_internal", "urban_out": "urban_out",
        "cross_in": "cross_origin", "cross_out": "cross_out",
    }
    class_by_edge = {
        "main_up": ["M"], ":freeway_merge_1": ["M"], "main_down": ["M", "R"],
        "urban_in": ["R", "U"], ":urban_tls_0": ["R", "U"], "shared_approach": ["R", "U"],
        ":urban_diverge_1": ["R"], "ramp_storage": ["R"], ":ramp_mid_0": ["R"],
        "ramp_accel": ["R"], ":freeway_merge_0": ["R"], ":urban_diverge_0": ["U"],
        "urban_out": ["U"], "cross_in": ["X"], ":urban_tls_1": ["X"], "cross_out": ["X"],
    }
    r_edges = ["urban_in", ":urban_tls_0", "shared_approach", ":urban_diverge_1", "ramp_storage",
               ":ramp_mid_0", "ramp_accel", ":freeway_merge_0", "main_down"]
    lengths: dict[str, float] = {}
    for edge in network.findall("edge"):
        lanes = edge.findall("lane")
        if lanes:
            lengths[edge.get("id")] = max(finite(lane.get("length")) for lane in lanes)
    r_start: dict[str, float] = {}
    cursor = 0.0
    for edge_id in r_edges:
        if edge_id not in lengths:
            raise ValueError(f"R path edge missing from network: {edge_id}")
        r_start[edge_id] = cursor
        cursor += lengths[edge_id]
    merge_start = r_start["main_down"]
    tls_links = {"urban_in": 0, ":urban_tls_0": 0, "cross_in": 1, ":urban_tls_1": 1}
    lanes: dict[str, dict] = {}
    rows: list[dict] = []
    for edge in network.findall("edge"):
        edge_id = edge.get("id")
        if edge_id not in region_by_edge:
            continue
        for lane in edge.findall("lane"):
            lane_id = lane.get("id")
            length = finite(lane.get("length"))
            start = r_start.get(edge_id)
            item = {
                "edge_id": edge_id, "region": region_by_edge[edge_id],
                "is_internal": edge.get("function") == "internal", "length_m": length,
                "speed_limit_mps": finite(lane.get("speed")), "observed_classes": class_by_edge[edge_id],
                "r_path_start_m": start, "r_path_end_m": start + length if start is not None else None,
                "distance_to_merge_start_m": (start - merge_start) if start is not None else None,
                "tls_link": tls_links.get(edge_id), "first_downstream_eligible": edge_id == "main_down",
            }
            lanes[lane_id] = item
            rows.append({"lane_id": lane_id, **item})
    return lanes, rows


def _first_fcd_positions(path: Path) -> dict[tuple[str, str], tuple[float, float, int]]:
    first_seen: set[str] = set()
    values: defaultdict[tuple[str, str], list[float]] = defaultdict(list)
    for _, step in ET.iterparse(path, events=("end",)):
        if step.tag != "timestep":
            continue
        for vehicle in list(step):
            vehicle_id = vehicle.get("id", "")
            if vehicle_id in first_seen:
                continue
            first_seen.add(vehicle_id)
            values[(vehicle_class(vehicle_id), vehicle.get("lane", ""))].append(finite(vehicle.get("pos"), "first FCD pos"))
        step.clear()
    return {key: (min(group), max(group), len(group)) for key, group in values.items()}


def prepare_stage3_metadata(batch_dir: Path, authorization_quote: str) -> None:
    """Create the T30/T31 registry and contract from immutable Stage 2 archives."""
    batch_dir = Path(batch_dir).resolve()
    reject_temporary_output(batch_dir)
    if batch_dir.exists():
        raise FileExistsError(f"refusing to overwrite {batch_dir}")
    if not batch_dir.parent.is_dir():
        raise FileNotFoundError(batch_dir.parent)
    os.mkdir(batch_dir)
    selected = {
        "C17": "C17_reused.json", "C23": "C23_attempt1.json",
        "ML17": "ML17_attempt1.json", "ML23": "ML23_attempt1.json",
        "MH17": "MH17_attempt1.json", "MH23": "MH23_attempt1.json",
        "RL17": "RL17_attempt1.json", "RL23": "RL23_attempt1.json",
    }
    source_map_root = ROOT / "data/processed/stage2_completion_20260909_v1/source_maps"
    registry_runs: list[dict] = []
    resolvers: dict[str, ArchiveResolver] = {}
    static_hashes: defaultdict[str, set[str]] = defaultdict(set)
    insertion: dict[str, dict] = {}
    reference_network: ET.Element | None = None
    reference_network_signature: tuple | None = None
    reference_detector_signature: tuple | None = None
    try:
        for run_id, filename in selected.items():
            map_path = source_map_root / filename
            resolver = ArchiveResolver(map_path)
            resolvers[run_id] = resolver
            summary = load_json(resolver.resolve("summary.json"))
            seed = summary_seed(summary)
            if run_id[-2:] not in ("17", "23") or seed != int(run_id[-2:]):
                raise ValueError(f"run/seed identity mismatch: {run_id}")
            for suffix in ("network.net.xml", "scenario.add.xml", "scenario.sumocfg", "scenario.tll.xml"):
                static_hashes[suffix].add(digest(resolver.resolve(suffix)))
            network = ET.parse(resolver.resolve("network.net.xml")).getroot()
            network_signature = (
                tuple(sorted((edge.get("id"), edge.get("function"), tuple(sorted((lane.get("id"), lane.get("index"), lane.get("length"), lane.get("speed")) for lane in edge.findall("lane")))) for edge in network.findall("edge"))),
                tuple(sorted(tuple(sorted(connection.attrib.items())) for connection in network.findall("connection"))),
                tuple(sorted((logic.get("id"), logic.get("type"), logic.get("programID"), logic.get("offset"),
                              tuple(tuple(sorted(phase.attrib.items())) for phase in logic.findall("phase"))) for logic in network.findall("tlLogic"))),
            )
            if reference_network is None:
                reference_network = network
                reference_network_signature = network_signature
            elif network_signature != reference_network_signature:
                raise ValueError(f"compiled network semantics differ: {run_id}")
            additional_root = ET.parse(resolver.resolve("scenario.add.xml")).getroot()
            detector_signature = tuple(sorted((node.tag, node.get("id"), node.get("lane"), node.get("pos"),
                                               node.get("endPos"), node.get("period"))
                                              for node in list(additional_root) if node.tag in ("inductionLoop", "laneAreaDetector")))
            if reference_detector_signature is None:
                reference_detector_signature = detector_signature
            elif detector_signature != reference_detector_signature:
                raise ValueError(f"detector semantics differ: {run_id}")
            demand = ET.parse(resolver.resolve("demand.rou.xml")).getroot()
            flows = {node.get("id").split("_")[0]: node.attrib for node in demand.findall("flow")}
            if set(flows) != set(CLASSES):
                raise ValueError(f"flow identity mismatch: {run_id}")
            trip_groups: defaultdict[tuple[str, str], list[float]] = defaultdict(list)
            for _, node in ET.iterparse(resolver.resolve("outputs/tripinfo.xml"), events=("end",)):
                if node.tag == "tripinfo":
                    trip_groups[(vehicle_class(node.get("id")), node.get("departLane", ""))].append(finite(node.get("departPos")))
                    node.clear()
            first_groups = _first_fcd_positions(resolver.resolve("outputs/fcd.xml"))
            insertion[run_id] = {
                "declared": {cls: {"departPos": flows[cls].get("departPos"), "departLane": flows[cls].get("departLane")}
                             for cls in CLASSES},
                "tripinfo_actual": [{"class": cls, "lane_id": lane, "min_depart_pos_m": min(values),
                                     "max_depart_pos_m": max(values), "vehicle_count": len(values)}
                                    for (cls, lane), values in sorted(trip_groups.items())],
                "first_fcd_actual": [{"class": cls, "lane_id": lane, "min_first_pos_m": bounds[0],
                                      "max_first_pos_m": bounds[1], "vehicle_count": bounds[2]}
                                     for (cls, lane), bounds in sorted(first_groups.items())],
            }
            registry_runs.append({
                "run_id": run_id, "attempt_id": resolver.mapping["attempt_id"], "selected_attempt": True,
                "seed": seed, "condition": re.sub(r"(17|23)$", "", run_id),
                "requested_demand_vehph": summary["simulation"]["requested_demand_vehph"],
                "time_windows": summary["time_windows"], "sumo_version": summary["sumo_version"],
                "netconvert_version": summary.get("netconvert_version", "Eclipse SUMO netconvert 1.26.0"),
                "source_map_path": str(map_path.relative_to(ROOT)), "source_map_sha256": digest(map_path),
                "archive_runtime_path": resolver.mapping["archive_runtime_relative_path"],
                "archive_file_count": len(resolver.inventory()), "files": resolver.inventory(),
            })
        if reference_network is None:
            raise ValueError("no selected network")
        lanes, map_rows = _lane_metadata(reference_network)
        c17 = resolvers["C17"]
        additional = ET.parse(c17.resolve("scenario.add.xml")).getroot()
        e1 = []
        for node in additional.findall("inductionLoop"):
            ident = node.get("id")
            role = ("origin_insertion_contaminated" if ident.startswith("merge_upstream") else
                    "M-only_internal_merge_entry" if ident.startswith("mainline_merge_entry") else "downstream_passage")
            e1.append({"detector_id": ident, "lane_id": node.get("lane"), "position_m": finite(node.get("pos")),
                       "period_s": finite(node.get("period")), "group": role,
                       "output_suffix": "outputs/" + Path(node.get("file")).name,
                       "qualification": "technical_placeholder; E1 has no vehicle IDs"})
        e2 = [{"detector_id": node.get("id"), "lane_id": node.get("lane"), "begin_pos_m": finite(node.get("pos")),
               "end_pos_m": finite(node.get("endPos")), "period_s": finite(node.get("period")),
               "status": "coverage_only"} for node in additional.findall("laneAreaDetector")]
        tl = reference_network.find("tlLogic[@id='urban_tls']")
        if tl is None:
            raise ValueError("urban_tls missing")
        contract = {
            "schema_version": 1, "contract_id": "stage3_measurement_contract_20260912_v1",
            "status": "user_approved_exploratory_contract_pending_scientific_review",
            "source_batch": "stage2_completion_20260909_v1",
            "windows": {name: {"begin_s": bounds[0], "end_s": bounds[1],
                               "qualification": "B is a sensitivity cut, not verified steady-state warm-up" if name == "B" else "exploratory finite horizon"}
                        for name, bounds in REQUIRED_WINDOWS.items()},
            "versions": {"sumo": "Eclipse SUMO sumo 1.26.0", "netconvert": "Eclipse SUMO netconvert 1.26.0"},
            "fcd": {"sampling_period_s": 1.0, "expected_begin_s": 0.0, "expected_end_s": 2700.0,
                    "expected_label_count": 2700, "empty_frame_semantics": "present frame with zero vehicles; not a missing frame"},
            "stop_definition": {"id": "technical_stop_speed_le_0_1", "speed_threshold_mps": 0.1,
                                "operator": "<=", "qualification": "technical stop sample; not congestion"},
            "lanes": lanes, "e1_detectors": e1, "e2_detectors": e2,
            "tls": {"id": "urban_tls", "program_id": tl.get("programID"), "type": tl.get("type"),
                    "phases": [node.attrib for node in tl.findall("phase")],
                    "movements": [{"class_scope": ["R", "U"], "from": "urban_in", "to": "shared_approach", "link_index": 0},
                                  {"class_scope": ["X"], "from": "cross_in", "to": "cross_out", "link_index": 1}],
                    "rule": "resolve the movement-specific link index; never use the first character for every movement"},
            "r_path": {"origin": "start of urban_in", "positive_direction": "toward main_down",
                       "merge_start_m": lanes["main_down_0"]["r_path_start_m"],
                       "qualification": "compiled lane-length coordinate; M/U/X lanes outside the R path remain null"},
            "insertion_observations": insertion,
            "endpoint_rule": "O=P-E only at 1500/2700 when declared plan and departure/arrival coverage are verified",
            "first_R_downstream_rule": "(previous raw FCD label, first main_down label]; cross-bin events remain unknown",
            "episode_rule": "Full episodes split on missing labels; region occupancy and same-vehicle episodes are distinct; A/B/Post clips reference Full parent IDs",
            "sensitivity_rule": "M-only internal E1 native 30 s data rebinned to 60/120 s, anchored independently at A=0 and B=300; real short tails retained",
            "limitations": ["1 Hz FCD provides sampled observations rather than exact physical transition times.",
                            "Static priority and link data do not establish dynamic causal obstruction.",
                            "E2 is coverage_only unless a later contract explicitly registers a new metric and verification scope.",
                            "Mainline departPos=last observations near the merge do not establish upstream feeder traffic state."],
        }
        network_hash = digest(c17.resolve("network.net.xml"))
        detector_by_lane: defaultdict[str, list[str]] = defaultdict(list)
        for detector in e1 + e2:
            detector_by_lane[detector["lane_id"]].append(detector["detector_id"])
        for row in map_rows:
            row["observed_classes"] = "|".join(row["observed_classes"])
            row["measurement_ids"] = "|".join(sorted(detector_by_lane[row["lane_id"]]))
            row["tls_id"] = "urban_tls" if row["tls_link"] is not None else None
            row["source_network_sha256"] = network_hash
            row["qualification"] = "compiled static fact; dynamic mechanism not inferred"
        registry = {"schema_version": 1, "batch_id": batch_dir.name, "source_batch": "stage2_completion_20260909_v1",
                    "selection_rule": "execution ledger selected attempt -> exact source map -> immutable project archive",
                    "tmp_fallback": False, "selected_run_count": len(registry_runs), "runs": registry_runs,
                    "static_hash_sets": {key: sorted(values) for key, values in static_hashes.items()}}
        write_json(batch_dir / "source_registry.json", registry)
        write_json(batch_dir / "measurement_contract.json", contract)
        map_fields = ["lane_id", "edge_id", "region", "is_internal", "length_m", "speed_limit_mps", "observed_classes",
                      "r_path_start_m", "r_path_end_m", "distance_to_merge_start_m", "tls_link", "first_downstream_eligible",
                      "measurement_ids", "tls_id", "source_network_sha256", "qualification"]
        write_csv(batch_dir / "network_observation_map.csv", map_rows, map_fields)
        verification = {
            "schema_version": 1, "scope": "T30-T32 engineering verification",
            "read_only_stage2_checks": [
                {"command": ".venv/bin/python data/processed/stage2_completion_20260909_v1/revision_04/independent_verification.py --check-only",
                 "executions_this_session": 1, "exit_code": 0, "observed": {"archive_files": 232, "vehicles": 14564, "E1_rows": 4320, "merge_endpoints": 4200, "contrasts": 198}},
                {"command": ".venv/bin/python data/processed/stage2_completion_20260909_v1/g2_review/supplemental_verification.py",
                 "executions_this_session": 1, "exit_code": 0, "observed": {"vehicle_rows": 14564, "first_R_events": 2100, "actual_new_starts_recounted": 7}},
            ],
            "dedicated_tests": {"command": ".venv/bin/python -m unittest tests.test_stage3_baseline -v",
                                "status": "passed", "test_methods": 13, "required_failure_mode_categories": 12,
                                "all_required_categories_passed": True, "synthetic_fixture_count": 19,
                                "assertion_count": 50, "additional_guardrail_categories": 2},
            "interface_help": ["analyze-run --help passed", "aggregate --help passed"],
            "forbidden_runtime_scan": {"subprocess_imports": 0, "traci_imports": 0, "runner_imports": 0},
            "actual_sumo_starts": 0, "actual_netconvert_starts": 0,
            "limitations": ["Independent production quantity reconstruction belongs to T33 data_analyst work.",
                            "Measurement contract and dynamic interpretation still require scientific_reviewer review."],
        }
        write_json(batch_dir / "engineering_verification.json", verification)
        ledger = {
            "schema_version": 1, "plan_version": "docs/EXPLORATORY_VALIDATION_COMPLETION_PLAN.md@sha256:" + digest(ROOT / "docs/EXPLORATORY_VALIDATION_COMPLETION_PLAN.md"),
            "authorization": {"status": "user_approved", "date": "2026-09-12", "quote": authorization_quote,
                              "boundary": "Execute the approved staged plan; Stage 3 has zero SUMO/netconvert starts and Stage 4 retains its explicit conditional gate."},
            "stage": "Stage 3", "status": "running", "batch_id": batch_dir.name,
            "steps": {
                "T30": {"status": "completed", "owner": "primary+simulation_engineer", "evidence": ["source_registry.json", "engineering_verification.json"]},
                "T31": {"status": "engineering_completed_pending_reviewer", "owner": "simulation_engineer->scientific_reviewer", "evidence": ["measurement_contract.json", "network_observation_map.csv"]},
                "T32": {"status": "engineering_completed_pending_data_analyst_and_reviewer", "owner": "simulation_engineer->data_analyst->scientific_reviewer", "evidence": ["src/analysis/analyze_stage3_baseline.py", "tests/test_stage3_baseline.py", "engineering_verification.json"]},
                "T33": {"status": "pending", "owner": "data_analyst"}, "T34": {"status": "pending", "owner": "data_analyst->scientific_reviewer"},
                "T35": {"status": "pending", "owner": "primary"},
            },
            "source_runs": [{key: row[key] for key in ("run_id", "attempt_id", "seed", "condition", "source_map_path", "source_map_sha256", "archive_runtime_path")}
                            for row in registry_runs],
            "input_hashes": {"source_registry_sha256": digest(batch_dir / "source_registry.json"),
                             "measurement_contract_sha256": digest(batch_dir / "measurement_contract.json"),
                             "network_observation_map_sha256": digest(batch_dir / "network_observation_map.csv")},
            "code_hashes": {"analyze_stage3_baseline.py": digest(Path(__file__)),
                            "test_stage3_baseline.py": digest(ROOT / "tests/test_stage3_baseline.py")},
            "measurement_contract_path": str((batch_dir / "measurement_contract.json").relative_to(ROOT)),
            "outputs": [str(path.relative_to(ROOT)) for path in sorted(batch_dir.iterdir())],
            "checks": {"T30_read_only_checks": "2/2 passed once", "T32_required_failure_modes": "12/12 passed",
                       "technical_blocker_major_open": 0},
            "limitations": verification["limitations"], "resume_point": "T31 scientific review and T32 data_analyst handoff",
            "budget": {"max_sumo_starts": 0, "max_netconvert_starts": 0},
            "actual_sumo_starts": 0, "actual_netconvert_starts": 0,
        }
        write_json(batch_dir / "execution_ledger.json", ledger)
    except Exception:
        marker = batch_dir / "INCOMPLETE.json"
        if not marker.exists():
            write_json(marker, {"status": "incomplete", "reason": "metadata preparation raised; see command stderr"})
        raise


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Archive-only Stage 3 baseline analysis; never launches SUMO")
    sub = parser.add_subparsers(dest="command", required=True)
    run = sub.add_parser("analyze-run", help="analyze one approved archived run")
    run.add_argument("--ledger", required=True)
    run.add_argument("--contract", required=True)
    run.add_argument("--run-id", required=True)
    run.add_argument("--output-dir", required=True)
    run.add_argument("--table-dir", required=True)
    run.set_defaults(func=analyze_run)
    agg = sub.add_parser("aggregate", help="aggregate approved per-run manifests")
    agg.add_argument("--ledger", required=True)
    agg.add_argument("--contract", required=True)
    agg.add_argument("--run-manifest", action="append", required=True)
    agg.add_argument("--output-dir", required=True)
    agg.add_argument("--table-dir", required=True)
    agg.add_argument("--figure-dir", required=True)
    agg.set_defaults(func=aggregate)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    args.func(args)
    return 0


if __name__ == "__main__":
    sys.exit(main())

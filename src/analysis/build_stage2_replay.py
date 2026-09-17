"""Build an exclusive, exploratory offline replay from retained SUMO records.

No SUMO calls, interpolation, source writes, or formal parameter selection.
The HTML template is a literal fragment, supplied separately with --template.
"""
from __future__ import annotations

import argparse
from collections import Counter
import hashlib
import json
import math
from pathlib import Path
import xml.etree.ElementTree as ET


def digest(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def points(value: str) -> list[list[float]]:
    result = [[float(v) for v in pair.split(",")] for pair in value.split()]
    assert result and all(len(p) == 2 and all(map(math.isfinite, p)) for p in result)
    return result


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run", type=Path, required=True)
    parser.add_argument("--reference", type=Path, required=True)
    parser.add_argument("--template", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--html", type=Path, required=True)
    args = parser.parse_args()
    assert not args.output_dir.exists(), "Refusing to overwrite existing derived directory"
    assert not args.html.exists(), "Refusing to overwrite existing visualization"
    sources = {
        "network": args.run / "network.net.xml",
        "fcd": args.run / "outputs/fcd.xml",
        "tls": args.run / "outputs/tls_states.xml",
        "reference": args.reference,
        "template": args.template,
    }
    before = {key: digest(path) for key, path in sources.items()}
    reference = json.loads(args.reference.read_text())
    assert reference["sources"]["fcd_sha256"] == before["fcd"]
    assert reference["sources"]["compiled_network_sha256"] == before["network"]
    net = ET.parse(sources["network"]).getroot()
    assert net.tag == "net"
    lanes = []
    for edge in net.findall("edge"):
        for lane in edge.findall("lane"):
            lanes.append({"id": lane.attrib["id"], "internal": edge.get("function") == "internal",
                          "shape": points(lane.attrib["shape"]), "length": float(lane.attrib["length"])})
    lane_ids = {lane["id"] for lane in lanes}
    assert len(lane_ids) == len(lanes)
    junctions = [{"id": j.attrib["id"], "shape": points(j.attrib["shape"])}
                 for j in net.findall("junction") if j.get("shape")]
    tls = {}
    for row in ET.parse(sources["tls"]).getroot().iter("tlsState"):
        t = float(row.attrib["time"])
        if 390 <= t <= 430:
            assert t not in tls and row.attrib["id"] == "urban_tls"
            tls[t] = row.attrib["state"]
    expected = {r["time_s"]: r for r in reference["instantaneous_by_timestep"]}
    frames = []
    checks = []
    all_samples = 0
    for _, element in ET.iterparse(sources["fcd"], events=("end",)):
        if element.tag != "timestep":
            continue
        t = float(element.attrib["time"])
        if 390 <= t <= 430:
            assert t.is_integer()
            vehicles, ids = [], set()
            counts, stopped = Counter(), Counter()
            for v in element:
                assert v.tag == "vehicle"
                a = v.attrib
                vehicle_id, lane = a["id"], a["lane"]
                cls = vehicle_id.split("_", 1)[0]
                assert cls in ("M", "R", "U", "X") and lane in lane_ids and vehicle_id not in ids
                ids.add(vehicle_id)
                x, y, speed = (float(a[k]) for k in ("x", "y", "speed"))
                assert all(map(math.isfinite, (x, y, speed))) and speed >= 0
                vehicles.append([vehicle_id, lane, x, y, speed])
                counts[f"{lane}/{cls}"] += 1
                if speed <= 0.1:
                    stopped[f"{lane}/{cls}"] += 1
            prior = expected[t]
            assert dict(counts) == prior["lane_class_counts"], (t, "lane counts mismatch")
            assert dict(stopped) == prior["stopped_lane_class_counts"], (t, "stopped counts mismatch")
            assert len(vehicles) == prior["vehicle_samples"]
            all_samples += len(vehicles)
            frames.append({"t": int(t), "tls": tls[t], "v": vehicles, "stopped": dict(sorted(stopped.items()))})
            checks.append({"time_s": int(t), "vehicle_samples": len(vehicles), "v2_exact_match": True})
        element.clear()
    assert [f["t"] for f in frames] == list(range(390, 431))
    assert set(tls) == set(range(390, 431))
    for cls, first, vehicle_id in (("R", 412, "R_flow.74"), ("U", 414, "U_flow.37")):
        observed = [f["t"] for f in frames if f["stopped"].get(f"shared_approach_0/{cls}", 0)]
        assert min(observed) == first
        frame = frames[first - 390]
        assert any(v[0] == vehicle_id and v[1] == "shared_approach_0" and v[4] <= 0.1 for v in frame["v"])
    data = {"classification": "exploratory saved-trajectory replay; not SUMO GUI or model validation",
            "start": 390, "end": 430, "step": 1, "default": 414,
            "vehicle_columns": ["id", "lane", "x_m", "y_m", "speed_m_s"],
            "lanes": lanes, "junctions": junctions, "frames": frames}
    payload = json.dumps(data, ensure_ascii=False, separators=(",", ":"), allow_nan=False)
    template = args.template.read_text()
    assert template.count("__REPLAY_DATA__") == 1
    html = template.replace("__REPLAY_DATA__", payload.replace("</", "<\\/"))
    assert len(html.encode()) < 1_000_000
    after = {key: digest(path) for key, path in sources.items()}
    assert before == after, "Input changed while processing"
    args.output_dir.mkdir(parents=True, exist_ok=False)
    data_path = args.output_dir / "replay.json"
    with data_path.open("x") as stream:
        stream.write(payload + "\n")
    with args.html.open("x") as stream:
        stream.write(html)
    manifest = {
        "classification": data["classification"],
        "sources": {k: {"path": str(p.resolve()), "sha256_before": before[k], "sha256_after": after[k]}
                    for k, p in sources.items()},
        "generator": {"path": str(Path(__file__).resolve()), "sha256": digest(Path(__file__))},
        "artifacts": {str(p.resolve()): digest(p) for p in (data_path, args.html)},
        "transformations": {"time_window": "390 <= original time <= 430", "sampling": "all original 1 s frames",
                            "coordinates": "original FCD x/y and compiled shapes; no added netOffset",
                            "vehicles": "all classes/lanes retained in data, map clips spatially",
                            "stopped": "existing technical speed <= 0.1 m/s; no official metric",
                            "tls_join": "exact raw timestamp; no shift/interpolation",
                            "exclusions": "time outside requested window; unused FCD attributes omitted",
                            "rounding": "none beyond original source precision", "animation": "discrete frames, no loop"},
        "checks": {"frame_count": len(frames), "vehicle_samples": all_samples, "duplicate_ids": 0,
                   "missing_or_unknown_lanes": 0, "source_hashes_unchanged": True,
                   "all_frame_lane_class_and_stopped_counts_equal_v2": True,
                   "anchors": {"shared_R_first_within_clip": 412, "shared_U_first_within_clip": 414},
                   "frames": checks},
        "limitations": ["Single seed 17 retained exploratory run; protocol empty/unfrozen.",
                        "No queue-length, causality, storage-capacity, timing-selection or thesis claim.",
                        "Vehicles outside display crop and outside-network waiting are not drawn.",
                        "Marker sizes are not physical vehicle dimensions.",
                        "TLS controls the upstream urban inlet only, not the ramp path.",
                        "Within-step TLS/FCD update ordering was not verified against implementation; exact raw timestamp join only, no phase-boundary causality claim.",
                        "Dynamic playback UI and visual QA are separate from these data checks."],
    }
    with (args.output_dir / "manifest.json").open("x") as stream:
        json.dump(manifest, stream, ensure_ascii=False, indent=2)
        stream.write("\n")
    print(json.dumps({"frames": len(frames), "samples": all_samples, "html_bytes": len(html.encode()),
                      "source_hashes_unchanged": before == after, "v2_frame_checks": len(checks)}))


if __name__ == "__main__":
    main()

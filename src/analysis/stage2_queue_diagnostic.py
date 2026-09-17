"""Read-only trajectory diagnostics; no causal or steady-state classification."""
import argparse
import hashlib
import json
import xml.etree.ElementTree as ET
from collections import Counter, defaultdict
from pathlib import Path

EDGES = ("ramp_accel", "ramp_storage", "shared_approach", "urban_in")


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def episodes(times):
    result = []
    for t in times:
        if result and t == result[-1][1]:
            result[-1][1] = t + 1
        else:
            result.append([t, t + 1])
    return result


def analyze(root):
    paths = [root / "summary.json"] + [root / "outputs" / name for name in
             ("fcd.xml", "tripinfo.xml", "tls_states.xml")]
    hashes = {str(p): digest(p) for p in paths}
    source = json.loads(paths[0].read_text())
    trips = ET.parse(root / "outputs/tripinfo.xml").getroot().findall("tripinfo")
    records = []
    for v in trips:
        depart, delay, arrival = (float(v.get(k)) for k in
                                  ("depart", "departDelay", "arrival"))
        assert depart >= 0 and delay >= 0 and arrival >= depart
        records.append((v.get("id"), v.get("id")[0], depart - delay, depart, arrival))
    ids = {r[0] for r in records}
    assert len(ids) == len(records) == sum(source["simulation"]["planned"].values())
    tls = {float(v.get("time")): v.get("state") for v in
           ET.parse(root / "outputs/tls_states.xml").getroot().findall("tlsState")}
    stopped_times = defaultdict(list)
    head_times = defaultdict(list)
    first = {}
    maxima = Counter()
    timeline = []
    seen_ids = set()
    waiting_times = defaultdict(list)
    last_t = None
    for _, node in ET.iterparse(root / "outputs/fcd.xml", events=("end",)):
        if node.tag != "timestep":
            continue
        t = float(node.get("time"))
        assert last_t is None or t == last_t + 1
        last_t = t
        counts = Counter()
        by_edge = defaultdict(list)
        for v in node:
            seen_ids.add(v.get("id"))
            edge = v.get("lane").rsplit("_", 1)[0]
            c = v.get("id")[0]
            if edge not in EDGES or c not in "RU":
                continue
            by_edge[edge].append(v)
            if float(v.get("speed")) <= 0.1:
                key = edge + "/" + c
                counts[key] += 1
                first.setdefault(key, {"time_s": t, "vehicle_id": v.get("id"),
                                       "position_m": float(v.get("pos")),
                                       "tls_state": tls[t]})
        for key, count in counts.items():
            stopped_times[key].append(t)
            maxima[key] = max(maxima[key], count)
        for edge, vehicles in by_edge.items():
            head = max(vehicles, key=lambda v: float(v.get("pos")))
            if float(head.get("speed")) <= 0.1:
                head_times[edge + "/" + head.get("id")].append(t)
        backlog = {c: sum(s < t <= d for _, cl, s, d, _ in records if cl == c)
                   for c in "RU"}
        for c, n in backlog.items():
            if n:
                waiting_times[c].append(t)
        if t % 30 == 0:
            timeline.append({"time_s": t, "tls_state": tls[t],
                             "stopped_counts": dict(counts),
                             "waiting_to_insert_before_step": backlog})
        node.clear()
    assert seen_ids == ids
    edge_report = {}
    for edge in EDGES:
        for c in "RU":
            key = edge + "/" + c
            runs = episodes(stopped_times[key])
            edge_report[key] = {
                "first_stop": first.get(key), "max_stopped_count": maxima[key],
                "seconds_with_any_stopped": len(stopped_times[key]),
                "longest_contiguous_episodes": sorted(runs, key=lambda z: z[1]-z[0], reverse=True)[:5],
                "green_state_seconds_with_stops": sum(tls[t][0] in "Gg" for t in stopped_times[key]),
            }
    heads = []
    for key, times in head_times.items():
        for a, b in episodes(times):
            heads.append({"edge_vehicle": key, "begin_s": a, "end_s": b,
                          "duration_s": b-a})
    end = source["time_windows"]["demand"]["end_s"]
    demand_end_backlog = {c: sum(s < end <= d for _, cl, s, d, _ in records if cl == c)
                          for c in "RU"}
    assert hashes == {str(p): digest(p) for p in paths}
    return {"classification": "exploratory single-trajectory diagnostic",
            "source_sha256": hashes, "all_sources_unchanged": True,
            "definitions": {"stopped": "FCD speed <= 0.1 m/s (existing technical placeholder)",
                            "episode": "consecutive one-second samples, reported [begin,end)",
                            "head": "furthest downstream R/U vehicle on each edge; lane-independent",
                            "backlog": "reported planned depart = depart - departDelay; scheduled < t <= actual depart",
                            "green": "first urban TLS signal character; relevance requires connection review",
                            "boundary": "stop episodes and temporal ordering do not establish causation"},
            "vehicle_count": len(ids), "demand_end_s": end,
            "waiting_at_demand_end": demand_end_backlog,
            "last_depart_s": max(r[3] for r in records),
            "last_arrival_s": max(r[4] for r in records),
            "edge_diagnostics": edge_report,
            "longest_same_vehicle_head_stops": sorted(heads,key=lambda z:z["duration_s"],reverse=True)[:20],
            "waiting_episodes": {c: episodes(waiting_times[c]) for c in "RU"},
            "timeline_30s": timeline}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    if args.output.exists():
        raise FileExistsError(args.output)
    # Known examples verify half-open continuous episode encoding.
    assert episodes([1, 2, 4]) == [[1, 3], [4, 5]]
    result = {"high_long": analyze(Path("/private/tmp/minimal_uncontrolled_eozyn46f")),
              "low": analyze(Path("/private/tmp/minimal_uncontrolled_17p2c9eo"))}
    assert result["high_long"]["waiting_at_demand_end"] == {"R": 150, "U": 75}
    assert result["low"]["waiting_at_demand_end"] == {"R": 0, "U": 0}
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("x") as stream:
        json.dump(result, stream, indent=2)
    print(args.output)


if __name__ == "__main__":
    main()

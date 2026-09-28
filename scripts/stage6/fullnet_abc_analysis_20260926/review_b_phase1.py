#!/usr/bin/env python3
"""Strict, outcome-blinded A/B pre-R and run-integrity review.

Reads post-R lifecycle/exposure only to establish technical completeness. It
never reads post-R M trajectories or computes freeway, queue, or U outcomes.
"""
from __future__ import annotations

import json
from collections import Counter, defaultdict
from pathlib import Path
import xml.etree.ElementTree as ET

from analyze import digest, route_class
from analyze_b import (phase1_gate, require, static_gate,
                       verify_raw_allow_outcome_warnings)
from analyze_sigma0 import verify_card, verify_manifest


ROOT = Path(__file__).resolve().parents[3]
PACKAGE = ROOT / "artifacts/stage6_full_network_abc_matched_rebuild_20260926_v1/inputs_retry2"
CARDS = {arm: ROOT / f"artifacts/stage6_full_network_abc_matched_rebuild_20260926_v1/FULLNET3350_{arm}_R900_S17_REBUILD_V2_CARD.json" for arm in ("A", "B")}
RAW = {arm: ROOT / f"data/raw/stage6_fullnet_abc_matched_rebuild_20260926_v1_retry2/{arm}/outputs" for arm in ("A", "B")}
OUT = ROOT / "data/processed/stage6_fullnet_abc_matched_rebuild_20260926_v1/b_phase1"


def summary_steps(path: Path):
    times = []
    final = None
    for _, e in ET.iterparse(path, events=("end",)):
        if e.tag == "step":
            times.append(float(e.get("time")))
            final = dict(e.attrib)
            e.clear()
    require(times == [float(i) for i in range(2700)], "Summary time coverage incomplete")
    return {"steps": len(times), "final_step": final}


def tls_audit(araw: Path, braw: Path):
    records = {}
    for arm, raw in (("A", araw), ("B", braw)):
        data = defaultdict(list)
        for _, e in ET.iterparse(raw / "tls_states.xml", events=("end",)):
            if e.tag == "tlsState":
                data[e.get("id")].append(dict(e.attrib))
                e.clear()
        require(set(data) == {"ramp_mid", "urban_tls"}, f"{arm} unexpected TLS IDs")
        for ident in data:
            require([float(x["time"]) for x in data[ident]] == [float(i) for i in range(2700)], f"{arm} {ident} TLS coverage incomplete")
        expected = "A_OPEN" if arm == "A" else "B_MODERATE"
        require({x["programID"] for x in data["ramp_mid"]} == {expected}, f"{arm} wrong realized ramp program")
        records[arm] = data
    require(records["A"]["urban_tls"] == records["B"]["urban_tls"], "Urban TLS differs")
    return {arm: {"ramp_program": next(iter({x["programID"] for x in records[arm]["ramp_mid"]})),
                  "ramp_state_seconds": dict(Counter(x["state"] for x in records[arm]["ramp_mid"])),
                  "ramp_phase_seconds": dict(Counter(x["phase"] for x in records[arm]["ramp_mid"])),
                  "urban_programs": sorted({x["programID"] for x in records[arm]["urban_tls"]}),
                  "urban_entries": len(records[arm]["urban_tls"])} for arm in ("A", "B")}


def lifecycle(planned, trips, veh):
    ids = set(planned["vehicles"])
    out = {}
    pre = {}
    for arm in ("A", "B"):
        require(set(trips[arm]) == ids and set(veh[arm]) == ids, f"{arm} lifecycle identities incomplete")
        rows = []
        pre[arm] = {}
        for c in "MRUX":
            cids = [v for v in ids if route_class(v) == c]
            inserted = [v for v in cids if float(trips[arm][v].get("depart", "-1")) >= 0]
            arrived = [v for v in cids if float(veh[arm][v].get("arrival", "-1")) >= 0]
            actual_pre = {v for v in inserted if float(veh[arm][v]["depart"]) < 540}
            pre[arm][c] = actual_pre
            delays = [float(trips[arm][v]["departDelay"]) for v in inserted]
            rows.append({"class": c, "planned": len(cids), "inserted": len(inserted),
                         "arrived": len(arrived), "unfinished_or_not_inserted": len(cids)-len(arrived),
                         "actual_departures_before_540": len(actual_pre),
                         "external_depart_delay_sum_s": sum(delays),
                         "external_depart_delay_max_s": max(delays, default=None),
                         "external_depart_delay_positive": sum(x > 0 for x in delays)})
        out[arm] = rows
    for c in "MUX":
        require(pre["A"][c] == pre["B"][c], f"Pre-R {c} actual departure identities differ")
    return out


def main():
    _, manifest_sha = verify_manifest(PACKAGE)
    cards, card_sha = {}, {}
    for arm in ("A", "B"):
        cards[arm], card_sha[arm] = verify_card(CARDS[arm], PACKAGE, arm, manifest_sha, RAW[arm])
    planned = static_gate(PACKAGE, cards["A"], cards["B"])
    integrity = {arm: verify_raw_allow_outcome_warnings(RAW[arm], card_sha[arm], arm) for arm in ("A", "B")}
    phase, trips, veh = phase1_gate(RAW["A"], RAW["B"], planned)
    life = lifecycle(planned, trips, veh)
    tls = tls_audit(RAW["A"], RAW["B"])
    summary = {arm: summary_steps(RAW[arm] / "sumo_summary.xml") for arm in ("A", "B")}
    require(phase["R_through"]["A"]["2700"] == phase["R_through"]["B"]["2700"] == 240,
            "R through-lane coverage incomplete")
    require(all(row["unfinished_or_not_inserted"] == 0 for arm in life for row in life[arm]),
            "Incomplete lifecycle")
    output = {"status": "PASS_PHASE1_DATA_GATE_SCIENTIFIC_RELEASE_PENDING",
              "scope": "Technical provenance, pre-R pairability, R exposure and lifecycle; no post-R outcomes",
              "package_manifest_sha256": manifest_sha, "card_sha256": card_sha,
              "integrity": integrity, "planned": dict(Counter(route_class(v) for v in planned["vehicles"])),
              "pre_R_and_R_exposure": phase, "lifecycle": life, "tls": tls, "summary": summary,
              "script_sha256": digest(Path(__file__))}
    OUT.mkdir(parents=True, exist_ok=False)
    with (OUT / "B_PHASE1_REVIEW.json").open("x") as f:
        json.dump(output, f, indent=2, sort_keys=True)
        f.write("\n")
    print(json.dumps({"status": output["status"], "report": str(OUT / "B_PHASE1_REVIEW.json"),
                      "pre_R_rows": phase["pre_R_MUX_FCD_equal_rows"], "R_through": phase["R_through"]}))


if __name__ == "__main__":
    main()

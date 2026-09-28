# Independent data/lifecycle post-run review — repaired PAIR3199 attempt 1

**Disposition: `NOT_EVALUABLE`.** The pre-meaningful-R trajectory gate is **NOT PASSED**. This review stops before post-R locked P/S/L, Candidate A/C, event attribution, or witness/no-witness interpretation. Confidence is **High** for raw hash/lifecycle counts and the measured pre-merge mismatch; **Moderate** for the physical explanation of that mismatch.

## Context and scope

Completed the required project Context Preflight: `AGENTS.md`, `docs/PROJECT_STATE.md`, `docs/DECISIONS.md`, `docs/EXPERIMENT_PROTOCOL.md`, and `docs/WORKLOG.md`; then read the bounded scan plan, adopted Stage 6 witness contract, v5 common-demand repair and independent reviews, new FINAL card and prelaunch review bindings, prior consumed `NOT_EVALUABLE` treatment records, and engineering post-run receipt. The current run is a single authorized repaired v5 attempt; Stage 6 remains exploratory and the formal protocol remains unfrozen. The prior treatment is a separate immutable attempt and is not reinterpreted.

The delegated review answers the first required gate: compare M/U/X FCD trajectories at identical absolute seconds and common vehicle IDs before the first physically observed R through-merge entry. Since that gate does not pass, no post-R classifier or causal/event analysis was run.

## Hash-bound sources

- Attempt: `PAIR3199_R720_DELAYED_S17_REPAIRED_V5_ATTEMPT1`; execution UUID `b095cce4-baba-4c40-aa79-08b5e58b9ce1`.
- Exact FINAL card SHA-256: `0801dc1e15ade92babe33640d521ba831174210a200b9e5a66aaeb3bd472e0ef`.
- Adopted witness contract SHA-256: `958890a7dd017110787a85d77ebfa3e6dac2b7d862f0fd91f6bafb7cf1738d9a`.
- V5 invariant report SHA-256: `509f1a46873b6922ce22e18f4100fa2dcb84a632d80ee9a014750efc6c857d54`; static construction report says 1,558/1,558 M/U/X planned records match and the only added identities are R192.
- Treatment output manifest SHA-256: `f36f336473792c2af246abf75c3b7b2e9217abb537e7b42e15685e6af46b7173`; the raw FCD/vehroute/tripinfo/lanechange hashes recorded in this manifest were independently recomputed and matched.
- Treatment FCD SHA-256: `ac5b74632b6d445aea5d5dfc4d58b3cc4b38d379418483bc71c408daf3c94f89`.
- Treatment vehroute SHA-256: `0cb8c77d435f10951067c2acb3100b83d80cc7342056632258f9eab933d8374d`.
- Treatment tripinfo SHA-256: `ff1974c3c6db5d01dbb539f63eef53c5ceb561197ab1289de134be84190a48a9`.
- Treatment lanechanges SHA-256: `b0087dc4a9e1159d1b3c3f2b0debee6dfaf51e29c47d7c963666916e41363bbb`.
- Control output-manifest hash is bound by the FINAL card; control FCD SHA-256: `ebefb9486daa7da96242a5ee525c232763ea6460368ad06645891ac8b4ca9a33`.
- Derived gate receipt SHA-256 and reproducible analyzer SHA-256 are recorded in the adjacent structured review JSON and `data/processed/stage6_pair_3199_repaired_treatment_postrun_20260923_v1/postrun_data_gate_receipt.json`.

The complete per-file manifest verification is in `data/processed/stage6_pair_3199_repaired_treatment_postrun_20260923_v1/raw_role_hash_verification.csv`. All 25 manifested payload/support files match their recorded bytes and SHA-256.

## Lifecycle and measurement census

Planned treatment identities are M=1,333, U=150, X=75, R=192. `vehroute.xml`, `tripinfo.xml`, and FCD each contain all **1,750/1,750** expected IDs, with no unexpected or missing identity. There are no duplicate route/trip records or duplicate FCD `(second, vehicle ID)` rows. FCD labels are exactly 0–2699 (2,700 labels). Tripinfo records 1,750 arrivals and zero unfinished/no-arrival vehicles. M departure delay is present for all 1,333, maximum 0.88 s (mean 0.4404 s); U/X/R tripinfo delays are zero. SUMO's engineering receipt independently records the full 2700 s terminal step and 18/18 required output roles.

All nine E1 records have 90 complete 30 s intervals spanning [0,2700); both E2 records (`ramp_storage_e2`, `shared_boundary_e2`) also have 90 complete intervals over that horizon. This is a coverage census only; no detector flow or occupancy outcome is interpreted. The raw lane-change and TLS records exist and are hash-bound. The lane-change census identifies the first R auxiliary-to-through lane change at 591 s. No post-R alternative-cause verdict is made because the first gate stopped the analysis.

## First gate: pre-merge M/U/X trajectory equivalence

The compared pre-exposure interval is every integer-second FCD frame with **t < 591 s**, exclusive of the first observed R through-merge frame/lane change at t=591 s. Both runs have full 0–2699 labels; in [0,591), each has 41,042 M/U/X vehicle-time rows. The matched key set is 41,042/41,042, with zero control-only or treatment-only `(time, identity)` samples and no duplicate keys.

Exact equality was checked on each matched sample's FCD tuple `(x, y, pos, lane, speed, type)`:

- Exact tuples: **40,844/41,042 (99.518%)**.
- Different tuples: **198/41,042 (0.482%)**, all U-class records.
- Affected common vehicles: **7**, `U_flow.53`–`U_flow.59`.
- M and X have exact tuple equality throughout this interval.
- First mismatch: `U_flow.54` at t=540 s, when `R_flow.0` also first actually departs and first appears in FCD. It is on `urban_in_0`; U_flow.54 is also on `urban_in_0`. At that frame the control U position is y=363.09 m and treatment y=341.06 m. The differing U identities continue through t=590 s; several have later same-time absolute-y differences around 20–40 m and lane-label divergence. Full first-difference/interval rows are in `pre_r_differing_common_vehicle_ids.csv`.
- First actual R departure/FCD: t=540 s on `urban_in_0`; first FCD on the ramp acceleration lane: t=587 s; first R FCD in a through-merge lane and first native `merge_section_0 → merge_section_1` lane change: t=591 s.
- Native lane-change records show certain R auxiliary-to-through entries in three consecutive complete 30 s bins beginning at 570, 600 and 630 s, with 3, 6 and 4 unique R IDs respectively; confirmation is t=660 s. The first through entry occurs at t=591, inside the first bin.

The common planned input binding passes, but the required **realized pre-merge common-stream equivalence does not**. The divergence is concentrated in U vehicles beginning at the same time and location as the first R source insertion; raw samples are consistent with an R-related source/approach interaction. That possible explanation does not restore equivalence and does not clear whether the source-side change can affect the later timing or conditions at which R enters the merge. Under the preregistered gate, the effect is not cleared before the downstream comparison; therefore stop here and label the pair `NOT_EVALUABLE`.

## Boundary and outputs

No locked post-R P/S/L or Candidate A/C analysis, matched post-R cell ledger, M deterioration onset, downstream/source/TLS/geometry causal adjudication, or witness/no-witness assessment was performed. Such analysis would cross the failed first gate. Existing historical control labels and old treatment `NOT_EVALUABLE` record remain unchanged.

Reproducible derived outputs:

- `data/processed/stage6_pair_3199_repaired_treatment_postrun_20260923_v1/analyze_pre_r_gate.py`
- `data/processed/stage6_pair_3199_repaired_treatment_postrun_20260923_v1/postrun_data_gate_receipt.json`
- `data/processed/stage6_pair_3199_repaired_treatment_postrun_20260923_v1/pre_r_differing_common_vehicle_ids.csv`
- `data/processed/stage6_pair_3199_repaired_treatment_postrun_20260923_v1/raw_role_hash_verification.csv`

No raw file was modified. No scientific inputs, classifier, threshold, witness contract, geometry, demand or formal protocol were changed. SUMO/TraCI/netconvert starts during this analysis: 0/0/0.

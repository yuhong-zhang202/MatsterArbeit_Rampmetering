# MINIMAL3350 E1 R900 RETRY3 — data/lifecycle post-run review

**Scope:** independent data/lifecycle review only. Raw trees are immutable. No independent scientific disposition is made here.

## Bound evidence

- Run/card: `MINIMAL3350_E1_R900_DELAYED_S17_TECH_RETRY3`; card SHA-256 `c5e94245dc44cc190dbcb2e402c28213c7e7e3ea90edf35e708a8d332209f31a`.
- Execution receipt SHA-256 `d8a4801db1fcf8100c866f2d71c811f7ddc75d1e6409058bcbea61d0b5101687`; output manifest SHA-256 `46be6b1681837e4f77224ebcd02eb13216a5e2e6b81818d5b610c64d7a3e9aeb`.
- Raw R900: `data/raw/stage6_minimal3350_ux0_20260925_v20/MINIMAL3350_E1_R900_DELAYED_S17_TECH_RETRY3/outputs/`.
- Matched control: REV8; R720 comparison: REV7. Their raw manifest hashes are recorded in `raw_hash_manifest.json`.
- Analysis script: `analyze_retry3.py`; classifier definition, existence-test plan and witness-contract hashes are in `raw_hash_manifest.json`.

## Integrity and lifecycle

All three raw output manifests reconcile byte size and SHA for every listed artifact. FCD has 2,700 complete integer-second frames (0–2699), no duplicate vehicle IDs per frame. Planned identities are complete: control 1,396 M; R720 1,396 M + 192 R; R900 1,396 M + 240 R; U=0 and X=0 explicitly. Each run has loaded=inserted=ended=arrived, running=waiting=unfinished=0, collisions=teleports=discarded=0. R900 actual R departures span [540.0, 1496.0] s and arrivals span [610.0, 1583.0] s; all 240 arrived. M schedule/type/speedFactor/route checks report `{'M_speedFactor': 1360}` mismatches.

## Matched M and R exposure

Pre-R M FCD comparison `[0,540)` has 34,491 common vehicle-seconds, no missing keys, and zero exact tuple divergences across lane, x/y, angle, type, speed, pos and slope. First M tuple divergence after R activation is [585, 'M_flow.494']; this is post-treatment and is not by itself a State1 classification.

R900 actual first departure is 540.0 s; first observed shared approach 541 s, ramp storage 566 s, merge-section/through-entry 583 s, downstream 593 s. T3 is confirmed at 660 s, within the 720 s requirement. Unique first merge-section entries by 1440 s (exclusive) are R900 209 vs R720 166; by 1500 s (exclusive): R900 223 vs R720 183. Both fixed-cutoff counts increase. The R720 convention independently reproduces reviewed 30-second entry counts 4/5/6 in bins starting 570/600/630 s.

## Locked classifier and matched cells

Using the unchanged P/S/L profiles and core cells 13–17: R900 has no qualifying core P, S or L episode; Candidate A=0. Candidate C has 80 warning bins overall, 40 in merge core during `[720,1440)`; control has 28 overall and 0 core in that window (R720 has 65 overall, 28 core). These warnings remain visible and are not reclassified as sustained events.

The primary same-time/lane/cell table has 1177 rows; 409 core cell/lane/bin rows have samples in both arms and 6,725 common M vehicle-seconds. In 197 rows the pooled treatment speed was lower than control and in 62 higher. This is descriptive only; the row-level table retains sample counts and common-vehicle contrasts. No P/S/L event is established by this comparison.

## Artifact/alternative-cause checks

- TLS output has 5,400 records per run; ramp-mid non-green records=0 and mainline-red records=0.
- Queue export has a complete 2,700-frame time grid, but zero lane records in each run, so queue morphology cannot be checked.
- Upstream E1 aggregate `main_up_1300` entered totals are {'control': 1397.0, 'r720': 1397.0, 'r900': 1398.0} (control M planned=1,396; no identity attribution). The aggregate differs slightly from planned/class counts, and cannot identify which vehicles contributed.
- Merge-section E1 lane0 totals (all classes) are control 0, R720 158.0, R900 205.0; these support traffic passage but are not R-identity counts. Downstream E1 records and FCD show downstream passage; no mainline red/TLS restriction was observed.
- R900 FCD/lane-change records show R presence and merge-lane transitions; no insertion/lifecycle loss was detected. Geometry and lane mapping remain bound to the reviewed unchanged network hashes in the package.

## Data-side recommendation and limits

Data integrity, pre-R matching, and actual exposure checks pass. Locked classifier output supports a **data-side `NO_WITNESS` recommendation** for this run: no qualifying sustained core P/S/L event and no Candidate A, despite verified increased R merge exposure. Independent scientific review must issue the final disposition. This is one fixed seed/materialized vehicle vector; it is exploratory and does not establish a general absence of the mechanism. Empty queue lane arrays, aggregate-only E1 identity limits, and fixed-seed scope remain limitations.


## Receipt binding

JSON review receipt: `DATA_POSTRUN_REVIEW.json`.


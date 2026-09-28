# Data/provenance prelaunch review — MINIMAL3350_CTRL_S17

**Disposition:** `PASS_DATA_PROVENANCE_PRELAUNCH`  
**Findings:** Blocker 0 / Major 0 / required Minor 0  
**Scope:** Read-only review of the exact control card and bound inputs. No process was started and no treatment outcome was inspected.

## Context and boundary

The current phase is the Stage 6 minimal U=X=0 existence test. The qMain=3199.2 pair has a valid `NO_WITNESS`; the prior independent review classified its R=0 control `LOW_R_BACKGROUND_ACCEPTABLE` for that control gate only. The qMain=3350.4 control has a one-start authorization. The adopted second-tier plan remains conditional on completing and reviewing the whole 3350 pair; it releases no earlier run. Formal protocol remains unchanged and unfrozen.

## Data checks

- Exact control card SHA-256 is `6095e498eb560d2ed8dc16548e19902313d7a89be92057db0d2fae689497c2ac`. Its bound common-M manifest, input manifest, runtime binding, START request and request receipt all match their declared hashes and cross-bind to this card/run.
- The input schedule contains 1,396 unique M identities (`M_flow.0`–`M_flow.1395`). SUMO 1.26.0's integer schedule is represented as `trunc(1,500,000 / 1,396) = 1,074 ms`; each desired departure equals `index × 1,074 ms`, with last desired departure at 1,498.230 s. All vehicles use `M_route` and `technical_passenger`; `departPos`, `departLane`, `departSpeed`, and speedFactor are explicitly present.
- The speedFactor list matches all 1,396 identities in the hash-bound prior `vehroute.xml`. R, U and X are explicit zero-count ledger entries (`PASS_ZERO`), not missing classes. The control demand materializes M vehicles only.
- Runner, runtime, SUMO 1.26.0 binary, SUMO_HOME, additional schema, request and resource values are hash-bound. The request is persisted unsent. The unique raw output directory was absent at review time.

## SpeedFactor source scope and interpretation

The explicit per-M speedFactor values come from an earlier qMain=3350.4, seed17 **full-network** run in which U/X were nonzero. This source is fully hash-bound and covers every M identity. Materializing these values fixes the M attribute vector and avoids relying on same-seed RNG ordering. If a later treatment reuses the exact common-M manifest, the pair can support a direct comparison conditional on this fixed M vector, and the only treatment-only added exogenous vehicles can be R.

This does **not** establish an independently generated or representative U=X=0 seed17 random realization. The comparison's scope is conditional on the explicitly fixed M vector. The future treatment still needs its own independent prelaunch proof that every M identity and attribute matches this manifest; this review does not certify that future arm.

## Provenance and execution status

The data review JSON contains the full source and binding hash inventory. Engineering's separate exact-card prelaunch receipt reports PASS and four binding tests pass. At this review, Guardian/SUMO/TraCI/netconvert starts are 0/0/0/0; the START request remains unsent and output path absent. This is a data/provenance PASS only, not a scientific control acceptance or a treatment release.

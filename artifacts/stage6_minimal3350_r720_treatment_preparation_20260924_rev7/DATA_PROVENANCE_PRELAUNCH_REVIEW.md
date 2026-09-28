# MINIMAL3350_R720_DELAYED_S17 REV7 — Data/Provenance Prelaunch Review

**Disposition:** `PASS_DATA_PROVENANCE_PRELAUNCH`  
**Findings:** Blocker/Major/required Minor = **0/0/0**  
**Scope:** Fresh independent, read-only data/provenance review of REV7. No run outcome was inspected, and this review launched no process.

## Exact binding and control prerequisite

REV7 card SHA-256: `d610c5c47c440014a3b8254b36de8d93a48c5d32be928746b93f50003ebcb125`. It fixes qMain=3350.4 veh/h, seed17, A_OPEN, R720 over `[540,1500)`, U=0 and X=0. The zero counts are explicitly ledgered. The legacy clean-high-mobility release flag is false; separately, the Stage 6 exploratory control-disposition prerequisite is true and requires `LOW_R_BACKGROUND_ACCEPTABLE`.

The card binds `MINIMAL3350_CTRL_S17` REV8. Its data receipt is `PASS_DATA_LIFECYCLE`, data-side category `LOW_R_BACKGROUND_ACCEPTABLE` (SHA `24711f151751cb1d6b0ba852388824f1f8e69be7fea3678900b872498870ab4d`). Its scientific review disposition is `LOW_R_BACKGROUND_ACCEPTABLE`, findings 0/0/0 (SHA `8078d5ee902eb355623d29e7cc78c7d9cdf61e918903d9a3040fe0f320ae3738`). The exact control output-manifest SHA is `48456bb607b4e4679dd13274696c60ab7f5ae020aa6ecbf2462110e1fdcd752f`.

REV7 runner code loads and verifies those exact bound control receipts before accepting the treatment card. It independently checks the separate exploratory release flag/category and leaves the legacy strict-screen flag false. The runner's nested data-review validator requires the REV7 package/run ID/schema/status, zero findings, nested exact hashes for card/manifest/runtime/runner/START request/request receipt/provenance, design/contract/adapter bindings, and accepted control hashes/dispositions. Inspected negative fixtures reject missing/wrong nested hashes, wrong package/status/run ID, nonzero findings, and wrong control disposition.

## Matched inputs

The common M manifest, control demand and treatment demand agree for **1,396/1,396 M vehicles**, with no mismatch in identity, desired departure, serialized departure, route, vType, speedFactor, depart lane/position/speed. Desired departures conform exactly to the SUMO 1.26.0 integer schedule `i × 1,074 ms`, indices 0 through 1,395. Route and vType definitions are consistent.

Treatment adds only `R_flow.0` through `R_flow.191`: 192 vehicles at 540,000 through 1,495,000 ms in exact 5,000 ms increments. Control has zero R/U/X; treatment U/X are explicit zero. This satisfies the planned R-only input difference.

**Provenance limitation retained:** explicit M speedFactors were copied from the prior qMain=3350.4, seed17 full-network run with nonzero U/X (source SHA `0183782a60172b5c038d7c0dcd0a9172478803a1c1673df6eadb29f2a6ea1702`). The full same vector is bound in both arms, establishing common planned M attributes. It does not show independent stochastic realization under U=X=0. This is disclosed and is nonblocking for the matched-input provenance gate.

## Hashes, output paths and resource contract

All actual input bytes match card/manifest hashes: demand `569b9f…ecce53`, additional XML `bf30ad…844d15`, network `887c23…700ca`, output roles `3ab602…7ddd7`, and sumocfg `d8c53d…c4195`. Plan, witness-contract, adapter, runtime, runner, manifest, persisted unsent START request, its receipt and provenance receipt match their declared bindings. SUMO runtime is 1.26.0 with its versioned binary and schema hashes recorded in the exact runtime binding.

All 18 output roles are unique and located directly within the exact card-bound v15 output directory. The directory and every target are absent. Resource contract: 90 s wall-clock, 75,000,000 bytes, 100 ms polling with slight overshoot accepted, one maximum start, zero technical retries.

The static preflight reports `PREFLIGHT_PASS_NO_PROCESS_STARTED` and `launchable_now=false` while fresh reviews are pending. Preparation records report Guardian/SUMO/TraCI/netconvert starts `0/0/0/0`; request receipt says `dispatched=false`. A live process listing could not be read because the execution environment denied the command. No process was started by this review, and all output locations remained absent at capture.

Engineering reports 25 focused tests passed, including nested receipt-schema positive and fail-closed cases; this reviewer inspected the test source but did not rerun tests.

## Boundary

This PASS covers REV7 data/provenance prelaunch checks only. It does not replace the independent scientific review, make static preflight launchable, or create any additional execution authorization. No treatment raw or post-run conclusion exists here.

Machine-readable review: `DATA_PROVENANCE_PRELAUNCH_REVIEW.json` (schema `stage6_minimal3350_treatment_data_provenance_prelaunch_review_v1`).

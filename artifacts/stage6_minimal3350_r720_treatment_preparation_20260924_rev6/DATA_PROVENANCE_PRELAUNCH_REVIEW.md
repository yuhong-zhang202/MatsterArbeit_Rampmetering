# MINIMAL3350_R720_DELAYED_S17 REV6 — Data/Provenance Prelaunch Review

**Disposition:** `PASS_DATA_PROVENANCE_PRELAUNCH`  
**Findings:** Blocker/Major/required Minor = **0/0/0**  
**Scope:** Independent, read-only review of REV6. No treatment outcome was inspected, no raw data was created or changed, and no process was launched.

## Binding and condition

The exact-card SHA-256 is `dadbfd3c3dd1460a648b478ff9c0f4a7c69806d605e27fc951de1082cfa9cca7`. The card binds qMain=3350.4 veh/h, seed 17, R=720 veh/h over `[540,1500)`, U=0 and X=0. Both zero classes are explicit (`PASS_ZERO`). The legacy clean-high-mobility release flag remains false. Separately, the required Stage 6 exploratory control disposition is enabled and explicitly requires `LOW_R_BACKGROUND_ACCEPTABLE`.

The exact bound control is `MINIMAL3350_CTRL_S17` REV8 (card SHA `15544478e8e7ced98b12673bec65cfe646b1f73e9e471ed501ddee052306bbfd`). Its data receipt is `PASS_DATA_LIFECYCLE` and data-side category `LOW_R_BACKGROUND_ACCEPTABLE` (SHA `24711f151751cb1d6b0ba852388824f1f8e69be7fea3678900b872498870ab4d`). Its scientific receipt disposition is `LOW_R_BACKGROUND_ACCEPTABLE`, findings 0/0/0 (SHA `8078d5ee902eb355623d29e7cc78c7d9cdf61e918903d9a3040fe0f320ae3738`). The output-manifest SHA is `48456bb607b4e4679dd13274696c60ab7f5ae020aa6ecbf2462110e1fdcd752f`. The reviewed runner calls the fail-closed receipt binding verifier before the treatment adapter path.

## Matched demand and treatment-only delta

Independent comparison of the common M manifest, control demand and treatment demand found **1,396/1,396** identical M identities and exact fields: ID, desired integer departure, serialized departure, route, vType, speedFactor, depart lane, position and speed. M desired departures satisfy the bound SUMO integer-time schedule `desired_depart_ms(i) = i × 1,074` for all indices 0–1,395. No per-field mismatch was found; route and vType definitions are consistent.

The treatment has exactly 192 additional `R_flow.0`–`R_flow.191` vehicles, scheduled at 540,000 ms through 1,495,000 ms in 5,000 ms intervals. The control has zero R/U/X; the treatment has explicit zero U/X. Thus the bound external-demand difference is R only.

**Scope limitation retained:** the common M speedFactor vector was materialized from a prior qMain=3350.4, seed-17 full-network run with nonzero U/X (source SHA `0183782a60172b5c038d7c0dcd0a9172478803a1c1673df6eadb29f2a6ea1702`). The same complete, explicit vector is bound in both arms, which closes this matched-input comparison. It does not establish an independently sampled U=X=0 RNG realization. This provenance limitation is disclosed and is nonblocking for this data/provenance gate; no broader stochastic-generation claim is made.

## Hashes, runtime, paths, and limits

Actual bytes match the card/manifest hashes for demand (`569b9f…ecce53`), additional XML (`26953d…e3f80`), network (`887c23…700ca`), output roles (`ebd49a…b271d`) and sumocfg (`584951…1be4`). Plan, adopted witness contract, adapter, common-M manifest, runner, runtime binding, persisted START request and request receipt hashes also match their bindings. START request status is `PERSISTED_UNSENT` and its receipt says `dispatched=false`.

All 18 output roles are unique, under the exact card-bound output directory, and absent; the output parent directory is absent. The resource contract is 90 s wall-clock, 75,000,000 bytes, 100 ms polling with slight overshoot accepted, one maximum start, zero technical retries. SUMO is bound to 1.26.0 and its versioned binary/schema hashes.

The static preflight reports `PREFLIGHT_PASS_NO_PROCESS_STARTED`, with `launchable_now=false` while exact-card reviews are pending. Preparation receipts report Guardian/SUMO/TraCI/netconvert starts of zero. A read-only OS process listing could not be obtained because the environment denied that command; no launch was attempted in this review, and persisted unsent request plus absent output locations agree with zero launch for REV6.

Engineering reports 20 focused tests passed, including negative cases for missing/false exploratory-control prerequisite, missing or mismatched control binding, missing receipts, wrong disposition, nonzero findings and wrong control identity/hash. The tests were inspected but not rerun in this read-only data review.

## Boundary

This PASS establishes the data/provenance prelaunch checks for REV6 only. It does not itself make the package launchable or constitute scientific review or new execution authorization. No treatment raw or post-run conclusion exists in this review.

Machine-readable evidence: `DATA_PROVENANCE_PRELAUNCH_REVIEW.json` (schema `stage6_minimal3350_treatment_data_provenance_prelaunch_review_v1`).

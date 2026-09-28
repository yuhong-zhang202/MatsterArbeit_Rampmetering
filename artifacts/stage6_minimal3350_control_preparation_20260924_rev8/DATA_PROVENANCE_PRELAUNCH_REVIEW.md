# Data/provenance prelaunch review — MINIMAL3350_CTRL_S17 REV8

**Disposition:** `PASS_DATA_PROVENANCE_PRELAUNCH`  
**Findings:** Blocker 0 / Major 0 / required Minor 0  
**Card SHA-256:** `15544478e8e7ced98b12673bec65cfe646b1f73e9e471ed501ddee052306bbfd`  
**Scope:** Fresh read-only review of REV8. No inputs/raw were edited; no process was started.

## Context

Stage 6 remains the minimal U=X=0 existence test. The 3199.2 pair is a reviewed `NO_WITNESS`. The 3350.4/R=0 control is the authorized next arm; its treatment remains conditional on control review. Adopted D-008 escalation is still gated on the full minimal3350 pair. The formal protocol is unchanged and unfrozen. No treatment outcome was reviewed.

## Card, inputs and runtime

- Card, common-M manifest, input manifest, runtime binding, provenance receipt, START request and request receipt hashes were checked. All package references cross-bind to this run/card. I independently rehashed the demand, additional XML, sumocfg, output-role manifest, network, original source flow, speedFactor vehroute source, runner, adapter, SUMO binary, Python executable and additional schema.
- Demand contains exactly 1,396 unique M IDs (`M_flow.0`–`M_flow.1395`). Every desired departure is `i × 1,074 ms`, matching `trunc(1,500,000 ms / 1,396) = 1,074 ms`; the last is 1,498.230 s. All records use `M_route` and `technical_passenger` and carry explicit departure and behavior fields.
- R=0, U=0 and X=0 are explicit `PASS_ZERO` class entries. The demand file contains 1,396 M vehicles and no R/U/X vehicles.
- The per-identity speedFactor values match the declared source for all 1,396 M identities. The source is a prior qMain=3350.4, seed17 full-network run where U/X were nonzero. This establishes a fixed, hash-bound M vector, not a representative independent U=X=0 RNG sample. A future treatment must reuse this exact manifest for the pair to compare M inputs conditionally and add only R.

## START request serialization and digest

`START_REQUEST.json` is 6,914 bytes. Its bytes equal R02's canonical JSON serialization (sorted keys, compact separators, UTF-8, final newline). SHA-256 `fca034d475dbbd104b9a0466d877792b119c0299d05db65d393375d5b69c4c25` equals the persisted receipt digest; the receipt binds the exact card SHA and run ID and records `PERSISTED_UNSENT`, with dispatch/Guardian/SUMO flags false. An indented pretty-JSON encoding has different bytes and a different digest.

I inspected the adapter and regression fixture: it asserts canonical byte equality and receipt digest match, and asserts that a pretty serialization/digest is rejected. I did not run tests; the engineering receipt reports 9 focused tests passing. The review gate remains fail-closed on the exact run ID, card hash, request bytes/digest and receipt fields.

## Output path and process checks

The six configured simulator outputs and two log targets, twelve additional XML destinations and eighteen output roles are all unique and directly under the same card-bound output directory. The eighteen roles exactly equal the six configured outputs plus the twelve additional destinations. The output directory and run parent are absent. The request is persisted but unsent. Guardian/SUMO/TraCI/netconvert starts: 0/0/0/0.

## Status boundary

Engineering REV8 reports PASS (0/0/0) and 9 focused tests passed; the prelaunch remains pending fresh exact-card data/scientific reviews, so execution remains blocked by the review gate. This data/provenance PASS does not classify control suitability or release treatment.

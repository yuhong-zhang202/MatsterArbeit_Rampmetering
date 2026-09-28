# Data/provenance prelaunch review — MINIMAL3350_CTRL_S17 REV7

**Disposition:** `PASS_DATA_PROVENANCE_PRELAUNCH`  
**Findings:** Blocker 0 / Major 0 / required Minor 0  
**Exact card SHA-256:** `c488ab86fd29799bba1aea882cae2aad908cd2e0b45ae8cef01ad13b7a9385f4`  
**Scope:** Fresh read-only review of REV7 only. No source inputs or raw were edited; no process was started.

## Context

The project remains in the Stage 6 minimal U=X=0 existence test. The 3199.2 pair is a reviewed `NO_WITNESS`; the authorized next arm is the 3350.4 R=0 control, with treatment conditional on the control review. Adopted D-008 stress escalation remains gated on a complete acceptable 3350/R0–R720 pair. Formal protocol remains unchanged and unfrozen. This review does not inspect or assign a 3350 traffic outcome. Earlier revision packages, including the historical REV2 review, remain unchanged.

## Input and execution provenance

- Exact card, common-M manifest, input manifest, runtime binding, provenance receipt, START request and START receipt hashes agree with their declarations and cross-bind to the same run/card. Actual hashes were checked for runner, adapter, network, source flow, source vehroute, SUMO binary, Python executable and additional schema.
- Demand contains exactly 1,396 M vehicles with unique IDs `M_flow.0`–`M_flow.1395`. Desired departure is `i × 1,074 ms`, consistent with `trunc(1,500,000 ms / 1,396) = 1,074 ms`; the final planned M departure is 1,498.230 s. All use `M_route` and `technical_passenger`; per-vehicle departure and behavior fields are explicit.
- SpeedFactor values match the source by M identity for 1,396/1,396. R, U and X are explicit `PASS_ZERO` ledger entries, not missing observations.
- Request status is `PASS_PERSISTED_UNSENT`. Authorized resource binding is 90 s / 60,000,000 bytes with 100 ms polling and slight overshoot accepted.

## Output locations

Direct parsing of the actual sumocfg found eight targets: six simulator outputs and two logs. The additional XML binds twelve detector/TLS destinations. All eighteen required output roles are unique and exactly equal to the six simulator output paths plus those twelve additional destinations. All twenty configured targets have distinct basenames and resolve directly under the card's one output directory. That directory and its run parent are absent. The sumocfg input references resolve to the REV7 demand, additional file and bound network.

## Review receipt schema gate

I inspected the runner validator and its fixtures. For the data role, the gate permits only schemas v2 and v3 with exact `PASS_DATA_PROVENANCE_PRELAUNCH`; each receipt must also match exact run ID and card SHA and contain integer zeros for blocker, major and required_minor (`true` is not accepted as integer zero). The aggregate sidecar must bind the exact run, card, required status and hash map for all three review receipts. Fixtures explicitly accept v2 and v3 and reject unsupported v99, wrong status, missing schema/disposition, boolean findings, wrong run/card and mismatched sidecar hashes. I inspected but did not execute the tests; engineering reports its focused suite passed 8 tests. This report uses the supported v3 schema and exact status/run/card/findings fields.

## SpeedFactor source scope

The values were copied from the historical qMain=3350.4 seed17 full-network `vehroute.xml` where U/X were nonzero. Its declared hash and all 1,396 identity/value matches are verified. The comparison is conditional on this explicitly fixed M vector; if a future treatment uses this exact manifest, it preserves common M inputs and adds only R. It does not establish an independent or representative U=X=0 RNG realization. Future treatment matching remains a separate mandatory prelaunch check.

## Status and limitations

Engineering REV7 reports PASS, 0/0/0 and eight focused tests passed. Preflight remains pending fresh exact-card data/scientific receipts and is not launchable. This review does not classify control suitability, release treatment or establish an outcome. Guardian/SUMO/TraCI/netconvert starts are 0/0/0/0.

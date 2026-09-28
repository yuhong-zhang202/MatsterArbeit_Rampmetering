# Data/provenance prelaunch review — MINIMAL3350_CTRL_S17 REV6

**Disposition:** `PASS_DATA_PROVENANCE_PRELAUNCH`  
**Findings:** Blocker 0 / Major 0 / required Minor 0  
**Card SHA-256:** `b0a4a40c1efd01640277a915858196fd737f0ba4821d6a97ff59642ad9f3a7e7`  
**Scope:** Fresh read-only review of REV6. No inputs/raw were edited and no process was started.

## Context

The project remains in the Stage 6 minimal U=X=0 existence test. The qMain=3199.2 matched pair is reviewed `NO_WITNESS`. The qMain=3350.4 control is the next authorized arm; treatment remains conditional on the control's completed engineering, data and scientific reviews. The user-adopted D-008 extension applies only after the complete 3350 pair passes its conditional entry gate. The formal protocol is unchanged and unfrozen. No 3350 treatment result exists in this review's scope.

## Input and runtime provenance

- The exact card SHA, common-M manifest, input manifest, runtime binding, provenance receipt, START request and START receipt were independently hashed and their cross-bindings checked. Runner, adapter, network, source flow, speedFactor source, SUMO binary, Python executable and additional schema hashes also match their declared values.
- The demand file contains 1,396 unique M vehicles (`M_flow.0`–`M_flow.1395`), with no other demand vehicles. Each has explicit desired departure, route, vType and behavioral attributes. Every route is `M_route`; every vType is `technical_passenger`.
- Desired departure is exactly `index × 1,074 ms`, matching the SUMO 1.26.0 integer-time schedule `trunc(1,500,000 ms / 1,396) = 1,074 ms`; the last is 1,498.230 s.
- M speedFactors match the declared source by identity for 1,396/1,396 vehicles. R, U and X appear as explicit zero-count `PASS_ZERO` ledger entries.
- START request is persisted with a hash-bound receipt and remains unsent. Resource binding is 90 s and 60,000,000 bytes, 100 ms polling with slight overshoot accepted.

## Output path audit

I parsed the sumocfg, additional XML and output-role file directly. The eight sumocfg target paths comprise six simulator outputs and two logs. All twelve additional XML destinations and all eighteen role paths resolve directly under the same card-bound output directory. The eighteen roles equal the union of six simulator outputs and twelve additional destinations; target basenames are unique. The output directory and its run parent do not exist. The configured input paths resolve to this REV6 demand/additional configuration and the bound network.

## Fixed speedFactor vector

SpeedFactor values come from the earlier qMain=3350.4, seed17 full-network `vehroute.xml` with U/X nonzero. Source hash and all 1,396 M identity/value matches are verified. The new control uses an explicitly fixed M vector. If a future treatment reuses this exact manifest, the paired comparison is conditional on that vector and R is the only additional exogenous demand. This does not establish an independently generated or representative U=X=0 seed17 RNG realization; the future treatment still needs an independent exact M match check.

## Status and limitations

Engineering REV6 reports PASS, 0/0/0, eight focused tests passed, with static preflight pending exact-card data/scientific receipts and therefore non-launchable. This data/provenance review does not classify control suitability or release the treatment. Guardian/SUMO/TraCI/netconvert starts remain 0/0/0/0.

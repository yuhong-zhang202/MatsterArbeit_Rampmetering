# STAGE6_FINAL_MECHANISM_CLOSEOUT_REASSESSMENT

**Status:** Independent scientific review PASS (0/0/0); Stage 6 `PARTIAL` is the reviewed recommendation, pending discussion with Robert.  
**Scope:** Read-only interpretation of existing Stage 6 exploratory evidence. SUMO/Guardian/TraCI/netconvert starts in this reassessment: 0/0/0/0. No classifier, threshold, geometry, demand, vehicle behavior, witness contract or formal protocol change.

## Decision proposed for review

**B — keep Stage 6 `PARTIAL` and report the bounded result to Robert.** The adopted second-tier plan stops at an E1 `NOT_EVALUABLE` outcome. R1080 and any new qMain, seed or B/C run are outside this reassessment. Strong Stage 6 closeout remains unsupported because no locked ramp-induced State1 witness or subsequent full-network freeway-protection/ramp-urban-cost chain has been established.

## Evidence and limits

| Existing comparison | Locked result | Mechanism information retained |
| --- | --- | --- |
| minimal3199 R0/R720, seed17, U=X=0 | Valid `NO_WITNESS` | R merge exposure occurred; a local L-only 60 s disturbance was retained but did not satisfy the P/S witness rule. |
| minimal3350 R0/R720, seed17, U=X=0 | Valid `NO_WITNESS` | R192/192 arrived, T3=660 s, no qualifying P/S; Candidate C warnings retained. |
| minimal3350 R0/R900 RETRY3, seed17, U=X=0 | `NOT_EVALUABLE` / `ONSET_REFERENCE_UNRESOLVED` | M1396 and R240 all arrived; 34,491 pre-R M vehicle-seconds matched exactly; T3=660 s. Unique R first merge entries were 209 vs R720 166 by 1440 s, and 223 vs 183 by 1500 s. Treatment has a four-bin P low-state run in core cell15 `[1260,1380)` with contemporaneous lane-specific slowing/density increase relative to matched R0. Immediate reference ratios 0.839884, 0.780261, 0.762122 fail the locked 0.85 eligibility rule. |

The R900 pattern is **descriptive evidence of sustained, local M deterioration after R admission**, with greater realized R merge exposure and no identified lifecycle, direct mainline TLS, or raw-provenance defect. It supports a **credible R-admission-associated deterioration potential** in this U=X=0 synthetic module (proposed confidence: Moderate). Do not state without qualification that merge pressure caused a confirmed State1 breakdown or that the scenario has established the full freeway–ramp–urban trade-off. The locked onset is unresolved, one seed/vector was used, queue XML has no lane records, and E1 aggregates do not identify vehicle classes. Same-time/lane/cell differences are not identical-cohort counterfactuals.

The 120 s interval is four consecutive 30 s **aggregate low-state bins**, not proof that the same vehicles were continuously slow for 120 s. It may be reported with cell, lane, timing, density and matched-control values while preserving `ONSET_REFERENCE_UNRESOLVED` as the official classification. Candidate C remains diagnostic; no capacity drop or metering effect is inferred.

The older lifecycle report's 1,360 M speedFactor mismatch flags compare four-decimal materialized/vehroute values with two-decimal tripinfo output at an overly exact tolerance. A new offline audit reconciled all 1,396 materialized M speedFactors exactly with demand and vehroute; tripinfo differences are bounded by 0.005 and the locked speed-ratio calculation uses vehroute, not tripinfo. Twelve exact decimal half-ties have formatter behavior not independently verified, so the limited serialization caveat is retained. This check does not change the R900 outcome.

## Six answers

1. **Original environment goal:** The cumulative record supports a qualified plausibility statement about R-admission-associated, sustained local mainline deterioration potential, with Moderate confidence. The exact unqualified phrase “demonstrates ramp-pressure-induced sustained freeway deterioration” overstates causal specificity and spatial extent. The locked State1 witness remains unestablished.
2. **R900 120 s:** Yes, as descriptive local mechanism evidence. Name four 30 s low bins in core cell15 `[1260,1380)`, state the matched-control difference, and keep `ONSET_REFERENCE_UNRESOLVED` and one-seed limitations attached.
3. **Stage 6 status:** **B, keep `PARTIAL` and report to Robert.** A would silently waive the predeclared witness plus A/B/C closeout evidence; C would contradict the adopted E1 stop rule. This is a recommendation for discussion, not a frozen project decision.
4. **Minimum offline checks:** The only newly surfaced data-integrity ambiguity relevant to this reassessment was the speedFactor serialization flag; the 1,396-ID check is complete. No further offline check is mandatory to report this bounded result. Stronger merge-specific attribution would need better queue and alternative-cause evidence and a separately agreed design; it cannot be obtained by relabeling the existing onset.
5. **R1080:** Stop. The pre-registered E1 `NOT_EVALUABLE` condition closes that branch; running R1080 to seek a positive classification would be outcome-driven escalation.
6. **Supervisor communication:** Use `ROBERT_TECHNICAL_SUMMARY.md`. Robert's preserved guidance supports initial uncontrolled demand exploration and insertion/merge/geometry diagnosis. It did not approve these exact rates, the U=X=0 module, or a formal protocol.

## Source bindings

- minimal3199 R720 independent scientific receipt: SHA-256 `291570279be3bef29b31bf079455ff140e91b5c68254ad252eeba81a2e9b004e`.
- minimal3350 R720 independent scientific receipt: SHA-256 `99c938a83f41724420d5d5cdd48aa0835f07d8a34c0bac6d0e72a92bb3bc2642`.
- minimal3350 R900 RETRY3 independent scientific receipt: SHA-256 `7c621613ad7ebe33c00fa0295e5517613861105ee9869932440fa3307c63f2f3`.
- R900 corrected data review: SHA-256 `c700e2d0c4d3c66cd8115e46cb8058e902a6cb79dd20e45bfddc308a610dc653`; matched lane/cell table: SHA-256 `feb09130cc17f8803cd8ff2c62341129d640372a64b4c2e8f3c5517544ebd071`.
- M speedFactor serialization audit: SHA-256 `eddb602a707cb5a0a54beca0af4a7714f6c1c1336c7a6feab01efedd1399e3a2`.
- User-adopted second-tier plan: SHA-256 `dee35d966d3fb00b1320092e49c1ebc228fbbbe3c5a8c3320e7966960e976776`; Robert's source email: SHA-256 `e788f4c12d36118fab865ed6fe9a7f1f1d6a7255d907daf4fc2d1850ed4c5023`.

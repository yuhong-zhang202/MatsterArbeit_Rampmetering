# Stage 6 exploratory ramp-induced witness contract — Amendment V1

**Status:** Versioned proposal for independent scientific review and possible user adoption. This document has no operative force until separately adopted. It does not alter the original contract, its locked classifier, any historical disposition, or the formal experiment protocol.

**Scope:** Only the Stage 6 exploratory matched comparison of `PAIR_3199_CTRL_S17` with the repaired v5 treatment attempt `PAIR3199_R720_DELAYED_S17_REPAIRED_V5_ATTEMPT1`. It changes how pre-exposure trajectory matching is *evaluated*, not the designed demand, geometry, seed, route, vehicle behavior, measurement definitions, or the original witness question. The target remains an **R-admission-associated exploratory witness**, not proof of pure merge friction or an optimized demand point.

**Parent contract:** `docs/methodology/STAGE6_EXPLORATORY_RAMP_INDUCED_WITNESS_CONTRACT.md`, SHA-256 `958890a7dd017110787a85d77ebfa3e6dac2b7d862f0fd91f6bafb7cf1738d9a`. All parent provisions not explicitly narrowed below remain in force if this amendment is adopted. In particular, keep its T3 rule, fixed event window, locked P/S/L and Candidate A/C rules, matched time/location/lane/cell comparison, independent raw reconstruction, and alternative-cause checks.

## 1. Disclosure and interpretation boundary

This amendment was proposed **after** the repaired treatment's pre-first-through-merge audit observed seven U identities diverging from the R=0 control beginning at t=540, while M and X remained matched through t=590. The original-contract post-run disposition is `NOT_EVALUABLE`; it and the earlier treatment's separate `NOT_EVALUABLE` record remain unchanged. Neither result is retroactively converted to a pass.

Any use of this amendment on the already generated raw must be reported as `RETROSPECTIVE_EXPLORATORY_SENSITIVITY_ANALYSIS`, alongside the original-contract result. The amendment must be reviewed and adopted, and its analysis plan frozen, **before** inspecting this repaired attempt's post-591 P/S/L, Candidate A/C, M deterioration or witness outcomes. A favorable later result cannot be used to revise this amendment.

## 2. Four fixed time periods and gates

Use the stated half-open intervals at the observed 1 s record labels. Preserve raw FCD/lane-change timing bounds rather than treating a sampled label as an exact physical crossing instant.

### A. t < 540: pre-treatment

R demand is not active. Require matched-control consistency for M, U and X: identical planned identities and attributes (desired departure, route, vType and explicit speedFactor), realized identity/departure coverage, and same-time vehicle-linked FCD position, lane, speed and type records wherever each vehicle is present. Reconcile missing or duplicate samples, insertion delay and incomplete/censored vehicles. A material unexplained difference or insufficient coverage makes this pair `NOT_EVALUABLE` under the amendment. Verify this period anew from immutable raw; do not rely only on the prior pooled t<591 summary.

### B. 540 <= t < 591: R active in shared source/approach; no observed freeway through-lane entry yet

R is present in the shared urban/source system. Require M trajectories and complete M identity/sample coverage to remain matched. Require X and any other variable **independently established to lie outside the R treatment pathway** to remain matched; document the route, lane and physical reason for that classification before treating X as a negative-control stream. If M diverges before observed freeway entry, or a verified non-pathway stream materially diverges without explanation, do not pass this gate.

Record all U differences by vehicle, time, lane, location and magnitude. A U difference can be a **potential treatment-pathway response** after R activation; it is neither an automatic baseline confound nor proof of a physical R effect. Its presence alone does not fail or pass the gate. Before passing, independently examine R/U vehicle order and contact opportunities, actual departures and insertion delays, source queues/receiving space, route and lane changes, randomness/vehicle-attribute realization, raw measurement consistency, and whether a U/source pathway could explain later M behavior independently of R freeway entry. Retain the full U divergence history in any later matched comparison. A material unresolved source, downstream, insertion, randomness or measurement alternative makes the pair `NOT_EVALUABLE` under this amendment. Do not infer pure merge pressure from an allowed U response.

### C. 591 <= t < 660: first observed freeway entry; meaningful exposure still accumulating

The first observed R through-lane FCD/native lane-change entry is at t=591 for this attempt. Reconcile certain versus possible R entries and the three consecutive complete 30 s bins required by the parent T3 rule. The observed sequence `[570,600)`, `[600,630)`, `[630,660)` can confirm T3 only at t=660 after all three bins are complete. Record exposure accumulation and coverage; do not declare a witness or treat t=591 alone as T3 confirmation. Resolve timing uncertainty with the parent contract's interval-bound rules.

### D. t >= 660: T3 confirmation, subject to the unchanged parent criteria

Only after the preceding gates and T3 are confirmed may an amended analysis evaluate the locked P/S/L rules, same-time/location/lane/cell control comparison, R exposure → treatment-specific M deterioration → State1 ordering, and source/downstream/geometry/TLS/measurement alternatives. The parent first-qualifying-low-bin window `[720,1440)`, confirmation before t=1500 while R continues entering, all numerical thresholds, reference/persistence/population/density rules and decision labels are unchanged. T3 confirmation is necessary, not sufficient, for a witness.

## 3. Review sequence and failure handling for existing raw

1. Freeze the versioned amendment and a separate raw-only analysis plan, then obtain independent scientific review and explicit user adoption. No post-591 outcome inspection is authorized by this document itself.
2. An independent data reviewer recomputes A and B directly from hash-bound control/treatment FCD, vehroute, tripinfo and lane-change records, including identity/departure, sample coverage and U/R contact chronology. An engineering reviewer checks source insertion, lane/route/geometry mapping, detector and TLS coverage and whether apparent U differences could arise from technical or measurement artifacts.
3. A scientific reviewer decides whether A/B matching and U/source-path adjudication are sufficient for this exploratory R-admission estimand. If not, retain `NOT_EVALUABLE`; do not inspect later outcomes to rescue the gate.
4. Only after that gate passes may a separate offline sensitivity analysis use the already available raw to apply unchanged T3 and locked post-exposure rules. Independent data and scientific reviews remain required for any resulting claim. Preserve the original-contract `NOT_EVALUABLE` next to any sensitivity label.

No new SUMO run is inherently required for this offline sequence. If existing raw cannot distinguish a physical R-to-U response from an insertion, stochastic or measurement artifact, or cannot bound a material U/source alternative pathway, the smallest next action is a vehicle-linked source/approach chronology and lane/geometry mapping from existing raw; if that still fails, retain `NOT_EVALUABLE`. A new simulation requires a separate design, review and authorization.

## 4. Non-amendments

This V1 does not change `docs/EXPERIMENT_PROTOCOL.md`, the older fixed PRE/control or `LOW_R_BACKGROUND_ACCEPTABLE` gates, P/S/L thresholds, Candidate A/C definitions, the local reference, event windows, the control's historical warnings/status, the original witness contract bytes, or either treatment attempt's historical `NOT_EVALUABLE` result. It creates no run card or execution authorization.

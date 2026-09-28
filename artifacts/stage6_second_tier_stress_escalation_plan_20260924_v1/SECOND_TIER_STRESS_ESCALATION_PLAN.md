# SECOND_TIER_STRESS_ESCALATION_PLAN

**Status:** `PROPOSED_PROSPECTIVE_STAGE6_EXPLORATORY_PLAN — NO_RUN_AUTHORIZATION`  
**Registered before:** any minimal3350 treatment outcome or new second-tier run.  
**Reason for revision:** the already reviewed minimal3199 pair yielded a valid `NO_WITNESS`; the original two-qMain/four-start module would stop after a second valid negative pair. This proposed extension changes that future stop boundary only if separately adopted. It does not reclassify the 3199 pair or change any earlier result.

## 1. Question and fixed scientific boundary

Test whether the validated freeway–ramp scenario can produce **ramp-admission/merge-associated sustained collective M deterioration** under a small, prospectively bounded increase in stress. This is a Stage 6 mechanism-existence search, not demand optimization, a capacity estimate, a formal experiment, or automatic selection of thesis qMain/qRamp values.

Keep the accepted network/geometry, vehicle behavior, seed17, U=X=0, A_OPEN, 0–2700 s horizon, delayed R window `[540,1500)`, measurement chain, locked P/S/L and Candidate A/C, event windows and witness criteria unchanged. At each qMain, a newly reviewed R=0 control precedes a matched R treatment; every common M vehicle must match in ID, integer-ms desired depart, route, vType, speedFactor and other bound attributes. Same seed alone is insufficient. A full-network U/X-positive run cannot replace a minimal U=X=0 arm.

This document is written before any minimal3350 treatment outcome. The current 3350.4/R=0 and R720 pair must finish under its already authorized, separately reviewed sequence. This plan does not reinterpret that pair or authorize another start.

## 2. Entry gate and order

The second tier opens only if **all** of the following are independently reviewed for the minimal3350 pair:

1. qMain=3350.4, seed17, U=X=0, R=0 control is `LOW_R_BACKGROUND_ACCEPTABLE` under the approved minimal control gate. A `LOW_R_SELF_CONGESTED` or `NOT_EVALUABLE` control ends the scan; no treatment or second tier follows.
2. Its delayed R720 treatment has matched pre-R M inputs/trajectories, complete lifecycle/measurement, actual R insertion and meaningful merge exposure, and an evaluable `NO_WITNESS` under the unchanged locked rules. A witness ends demand scanning; a `NOT_EVALUABLE` result stops for technical/scientific diagnosis.
3. The existing minimal3199 pair remains the separate valid `NO_WITNESS` anchor. Its raw and classification are not recomputed for this plan.

Once the entry gate is met, use the exact sequential order below. Stop at the first witness, self-congested control, non-evaluable arm, failed exposure-scaling gate, or exhausted cap. No cell is run just to fill a matrix.

## 3. Ramp stress first at fixed qMain=3350.4

| Step | Nominal qRamp | Planned R in `[540,1500)` | Condition to proceed |
| --- | ---: | ---: | --- |
| E1 | 900 veh/h | 240 | Run only after the entry gate. If witness: stop. If `NOT_EVALUABLE` or R exposure fails to increase over R720: stop. |
| E2, conditional | 1080 veh/h | 288 | Run only if E1 is evaluable `NO_WITNESS`, its additional planned demand produces greater actual merge exposure, and source/TLS/downstream checks show no material alternative. If witness or non-evaluable: stop. |

Both values are **proposed stress steps**, not proven physical capacities. With a 960 s window, 900 adds 48 planned R vehicles over 720 and gives an exact 4 s schedule; 1080 adds another 48. SUMO 1.26.0 integer-time flow semantics mean any 1080 schedule must be materialized and hash-bound exactly before a future card is reviewed. Historical reviewed minimal3199 R720 inserted and arrived 192/192 with first through-lane entry at 583 s and T3 confirmation at 660 s. Reviewed data do not establish insertion or merge capacity at 900 or 1080. Geometry lengths and an all-green `ramp_mid` state are not throughput measurements.

**Exposure-scaling gate (fixed before new outcomes):** For each compared rate at the same qMain, count unique R identities at their *first* through-lane entry by t=1440 and by t=1500, cross-check auxiliary E1 30 s entries and the route-stage FCD chronology, and report planned/inserted/arrived/unfinished R and actual departure delay. The higher nominal rate must produce a strictly higher unique-identity count by both fixed cutoffs and retain three consecutive positive complete auxiliary E1 bins by t<=720. Also require no material R source starvation, TLS admission, downstream receiving-space/tailback, geometry, detector or censoring alternative that would make the rate comparison uninterpretable. Lane-change event count is not a unique-vehicle count. If higher nominal demand fails this gate, **do not increase qRamp again**. A negative locked classifier result with inadequate exposure is `NOT_EVALUABLE`, not a valid `NO_WITNESS`.

## 4. Conditional qMain stress after ramp stress

Only after **both** E1 and E2 yield evaluable `NO_WITNESS` with increased actual merge exposure does qMain escalation open. For that branch, fix `qR*=1080` in advance. If E2 cannot pass its exact-card engineering/data/scientific prelaunch gates, or its execution is `NOT_EVALUABLE`, stop this plan; do not skip it and choose R900 for a higher-qMain treatment. This removes a discretionary post-E1 branch.

| Step | qMain | Planned M over `[0,1500)` | Pair decision |
| --- | ---: | ---: | --- |
| E3 | 3499.2 veh/h | 1458 | Run a new R=0 control first. Only `LOW_R_BACKGROUND_ACCEPTABLE` releases one matched delayed `qR*` treatment. |
| E4, conditional | 3650.4 veh/h | 1521 | Run only after the complete E3 pair is evaluable `NO_WITNESS`. Again, control first, then one matched delayed `qR*` treatment only if control is acceptable. |

At either qMain, sustained R=0 self-congestion ends that point **and the entire proposed escalation**; do not jump to a higher qMain. `NOT_EVALUABLE` also stops. A treatment witness immediately stops demand scanning. A valid negative treatment permits only the next predeclared step. With two valid negative qMain pairs, report `NO_WITNESS_WITHIN_EXTENDED_BOUNDED_SCAN` and stop. Never describe that as proof that the scenario cannot break down.

The values 3499.2 and 3650.4 correspond to integer M counts for the fixed 1500 s demand window and occupy the predeclared approximately 3500–3650 stress range. They are not an optimization grid. New qMain input materialization and common-M matching require independent prelaunch review before any start.

## 5. Why 3800/4000 are outside this plan

Neither 3800 nor 4000 is a candidate or authorized start here. A separately registered and reviewed proposal could consider one such point only if both 3499.2 and 3650.4 R=0 controls are acceptable, their paired higher-R treatments are evaluable negative despite verified increased merge exposure, and source/TLS/downstream/measurement checks leave a credible need for still greater M pressure. Before that decision, check that the proposed R=0 control can remain interpretable and that actual R merge exposure can still be delivered. A self-congested control, failed R scaling, or non-evaluable arm makes this further escalation unjustified. If ever considered, 3800 would precede 4000 with its own R=0 control gate; neither can be appended automatically to this budget.

## 6. Budget and immutable stop rules

- **Maximum new qRamp levels after a valid 3350/R720 negative:** 2 (900, then conditional 1080).
- **Maximum new qMain levels:** 2 (3499.2, then conditional 3650.4).
- **Maximum additional SUMO starts after the complete minimal3350 R0/R720 pair:** 6 = two additional 3350 treatments plus two new qMain pairs of control/treatment. These are ceilings, not targets or authorizations.
- **Maximum cumulative starts for the U=X=0 minimal module:** 10 = already completed 3199 pair (2), planned 3350 pair (up to 2), and second tier (up to 6). Any technical failure consumes its individual start; it does not automatically add a replacement to the cap. A scientific negative consumes its cell and never justifies rerunning it.

At every future proposed start: create a new exact card, absent output path, hash-bound materialized demand/runtime/runner/staging, a separate positive resource contract, and engineering/data/scientific prelaunch review. Earlier 90 s / 60 or 75 MB contracts belong to the 3350 pair only; higher-demand output size is unverified and cannot inherit those limits. Complete engineering/data/scientific post-run review precedes each branch decision. No automatic seed23, B/C, intermediate demand, third qMain, parameter adjustment, threshold revision or formal-protocol change.

The primary witness rule remains the approved P-primary or independently coherent qualifying S event after meaningful R exposure, in the fixed onset window, absent equivalent matched-control deterioration and material alternative causes. Candidate C, isolated low speed, L-only evidence or nominal R demand do not become witness by this extension. A witness ends the freeway demand scan and requires a separately reviewed return to the full U/X network for A/B/C trade-off validation; witness qMain/qRamp are not automatically thesis parameters.

## 7. Evidence and proposal status

This plan uses the approved minimal existence-test plan, its independent review, the hash-bound minimal3199 post-run reviews, the existing network, and read-only engineering/data feasibility audits. R720 realization is observed in reviewed runs; qRamp900/1080 capacity is unknown. The explicit six-start extension is motivated by the known 3199 negative and drafted before the 3350 outcome. It requires independent scientific review before finalizing and user adoption before it supersedes the old second-candidate stop boundary. **No SUMO, Guardian, TraCI or netconvert process is run to create or review this plan.**

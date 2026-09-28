# PAIR3199 retrospective exploratory sensitivity analysis

**Required label:** `RETROSPECTIVE_EXPLORATORY_SENSITIVITY_ANALYSIS`  
**Final disposition:** `NOT_EVALUABLE`  
**Stage 6 scope only.** This result does not modify the parent-contract or prior attempt `NOT_EVALUABLE` histories, and is not a formal experiment result.

## Outcome

The sensitivity analysis stopped after Gate B. Gate A passed, as did the M component of Gate B. Gate B as a whole did not clear because the post-activation U divergence leaves a material source/insertion/randomness alternative unresolved for later M attribution. Per Amendment V1, no Gate C or D outcome analysis followed. This is **not** a finding of `NO_WITNESS` and provides no witness/no-witness result.

## Gate A — t < 540

**PASS.** The independent data reviewer compared the two hash-bound raw FCD streams through labels 0–539. It found 37,333 common M/U/X vehicle-second records, zero tuple mismatches and zero unmatched sample keys. Planned M/U/X input bindings contain 1,558 common identities with no planned-attribute mismatch. The lifecycle supplement confirms identity-set coverage and aggregate completion: all planned vehicles were loaded, inserted and arrived in each arm; no terminal running/waiting vehicles or teleports. It did not inspect or compare arrival times.

## Gate B — 540 <= t < 591

- **M: PASS.** All 3,243 common M vehicle-second records match exactly.
- **X: exact match observed, pathway condition not established.** The 178 X records match, but X shares the signalized `urban_tls` with R on a conflicting movement. X cannot be certified as an unaffected negative control; its observed equality is descriptive.
- **U: unresolved.** There are 198 different vehicle-time tuples across U_flow.53–.59, beginning at U_flow.54 at t=540. U54's actual departure is 540 s in both arms with zero recorded departure delay. At that label, treatment U54 is 13.80 m from R_flow.0 on the same `urban_in_0`; recorded positions are U54 341.06 m in treatment, U54 363.09 m in control, R0 354.86 m in treatment. Later listed U changes also occur in shared source/approach space near R vehicles. This supports a possible treatment-pathway response.
- **Alternatives:** Engineering found no affirmative geometry/measurement defect or failed R insertion in its bounded inspection. The evidence does not separate a physical shared-source response from insertion sequencing, stochastic/RNG draw-order, or source-queue effects. The runtime RNG draw order is not recorded. These remain material alternatives to later M attribution under the amendment.

The exact common identity binding and successful lifecycle reconciliation establish planned-input and terminal coverage; they do not resolve the mechanism of the U trajectory differences. The static network also prevents treating X as a verified pathway-excluded stream.

## Gate C/D and analysis boundary

**Gate C was not formally evaluated for this sensitivity analysis. Gate D was not opened.** No P/S/L, Candidate A/C, matched post-exposure M comparison, event ordering, or witness outcome was calculated or inspected. Accordingly the final label is `NOT_EVALUABLE` under the amendment's stop rule.

**Process deviation:** During engineering review, the reviewer prematurely inspected treatment FCD/lane-change records labeled 591–659 and detector interval coverage before the data and scientific A/B signoffs. This was outside the frozen gate order and is recorded as a deviation. It did not supply a Gate C disposition and was not used to pass Gate B. The data reviewer stopped before opening label 591; the independent Gate A/B scientific reviewer did not inspect exposure values; no t>=660 data or outcome was opened by either. The reviewer concluded the deviation does not change the A/B disposition, but it must be disclosed in any later continuation.

## Preservation

- Amendment V1 is adopted for this Stage 6 exploratory sensitivity analysis only.
- The original contract and historical `NOT_EVALUABLE` results remain unchanged.
- Locked P/S/L thresholds, Candidate A/C rules, event window and formal protocol remain unchanged.
- Raw files remain immutable; only hash-bound offline derived reports were created.
- SUMO / TraCI / netconvert starts: **0 / 0 / 0**.

See `ANALYSIS_PLAN_FROZEN.md`, `ENGINEERING_GATE_REVIEW.md`, `SCIENTIFIC_GATE_REVIEW.md`, and `data/processed/stage6_pair3199_retrospective_sensitivity_20260924_v1/gates_ab/` for methods, evidence and detailed hashes.

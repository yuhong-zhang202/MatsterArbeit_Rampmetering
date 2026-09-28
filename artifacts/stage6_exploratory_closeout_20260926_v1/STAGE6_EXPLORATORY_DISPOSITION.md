# Stage 6 exploratory validation: bounded disposition

**Date:** 2026-09-26  
**Status:** `PARTIAL` (High confidence that the complete A/B/C gate is unmet). This report is an exploratory model-capability assessment, not a frozen formal experiment or real-world validation. The historical full-network A remains `A_NOT_EVALUABLE` and its corrected static relation to old R0 remains `NOT_PAIRABLE`; neither result was overwritten.

## Mechanism judgment

| Question | Disposition and confidence | Most decisive evidence |
|---|---|---|
| A: Can R pressure produce local M deterioration? | `SUPPORTED_EXPLORATORY_CAPABILITY` for the altered M-only sigma0 model (High within its pair); transfer to the default model Moderate, default numerical effect/dominant physical attribution Unknown. | Exact pre-R R0_SIGMA0/A_SIGMA0 pairing, R240 actual merge exposure, first M difference near R with no x<1000 differences t592–605, fixed cell14/15 M speed −1.379/−1.218 m/s and M trip +0.381 s. Default V2 A slowed but had early distant M divergence, so its pure merge share is unidentified. |
| B: Does a manageable-cost middle meter protect M? | `NOT_IDENTIFIED`; protection not supported in either tested default pair (High for descriptive signs), and not in the one sigma0 B22 sensitivity. | Default B22 materially reduced R merge entry by1500 A226→170 but M core speed 26.964→26.572 m/s and M trip +0.266 s while R/U trip +153.821/+26.473 s. Prospective B28 admitted A226/B222 and M core 26.964→25.376 m/s, M trip +0.721 s; R trip +15.642 s, U unchanged. Altered-model B22_SIGMA0 admitted A226/B170 but M core 28.413→28.336 m/s, cell signs mixed, M trip +0.005 s, and R/U trip +154.417/+26.473 s. Default B pairs retain early nonlocal M divergence, so their physical effect sign is Unknown. |
| C: Does stronger restriction transfer cost to R/U? | Cost **direction supported descriptively**, High for these single-seed outputs; a complete C leg paired with a successful moderate B is `NOT_IDENTIFIED`. | Within matched default A/B22, R residence +153.821 s and U +26.473 s, ramp/shared E2 jam-positive 44/22 of 90 vs A0, with all vehicles completed and zero external R/U delay. Relative to milder B28, B22 has markedly greater R/U cost; historical full-network B/C also showed stronger queue and U cost, but the prospective original C12G here was held. Queue front continuously crossing internal branches is not proven. |
| Complete freeway–ramp–urban trade-off? | **Not established** (High confidence in evidence gap). | The necessary manageable-cost B protection is absent in all bounded tests. A evidence is altered-model/qualified; C cost direction alone cannot supply the missing freeway-benefit leg. |

## What was done and why

1. Rebuilt a new full-network R0/A/B/C prospective input package from requested schedules and a common pre-generated speedFactor vector; it did not reuse old realized lane/speed/position as new exogenous input. The old A outcome stayed `A_NOT_EVALUABLE`. Completed default V2 R0/A and B22 with exact pre-R pairability and full vehicles. A default M deterioration was descriptive but early distant M divergence blocked physical attribution.
2. Completed the prespecified M-only sigma0 R0/A technical sensitivity. Its clean early local chronology and fixed M deterioration support a limited A model capability while changing M behavior, so it cannot numerically correct default A.
3. After independent negative B22 review, fixed **one** milder candidate by a rough one-point proportional service extrapolation, B28 28G+3y+29r. Its single exact-card run was complete and matched; it did not protect M. The 28-second value is a project design judgment, not a published threshold.
4. Completed exactly one missing sigma0/B22 diagnostic cell using the already tested 22G program to test whether default-model stochastic divergence was hiding an obvious local protective response. It did not show coherent M protection. This altered-model negative does not prove structural impossibility.
5. Independent `simulation_engineer`, `data_analyst` and read-only `scientific_reviewer` reviewed designs/cards/runs/outcomes according to project routing. Hash-bound cards, immutable raw, versioned processed outputs, failed pretraffic V1 R0 receipt and attribution corrections remain available. No new seed/demand/green-time sweep, C12G, ALINEA run or formal experiment was performed.

## Artifact and alternative-explanation audit

The new matched comparisons bind the network, behavior setting, seed17, requested common M/U/X demand and prospective speedFactor identities; R-demand treatment arms use the same requested R240, while R0 controls intentionally contain no R. Exact pre-540 common FCD and realized departure matches, 22/22 raw file hashes, full 2700 s output, actual R exposure in treatment arms, complete insertion/arrival and zero unfinished vehicles rule out the old realized-input semantic mismatch, obvious missing demand and gross output truncation for these pairs (High technical confidence). Independent A/B28 and default B22 per-vehicle FCD supplements found zero missing interior samples, duplicate vehicle-seconds or depart/arrival endpoint exceptions; other measurement coverage remains claim-specific. Actual signal phases and unchanged urban TLS were checked. R/U extra time in B22 is in-network; external R/U departure delay is zero.

The default-model A/B22/B28 first M differences include distant upstream vehicles before a plausible local merge-mediated path. This **unresolved stochastic/model-coupling alternative** prevents clean default numerical causal attribution. The sigma0 sensitivity suppresses M stochastic speed perturbation but also changes following/capacity and may leave other stochastic channels. Neither difference-of-differences subtraction nor direct splicing across the behavior settings is valid. E2 measures only its named lane geometry; class-specific FCD documents spatial residence but does not prove a continuous cross-connector spillback front. A synthetic network without real-world calibration supports only exploratory pattern capability, not external validity. Single seed cannot establish robustness or a precise sweet spot.

## Scientific basis versus local decisions

| Scientific issue | External basis | What is project judgment / not supplied by literature |
|---|---|---|
| Model validation versus code correctness | Sargent separates conceptual/data validity, verification and operational validity ([Sargent 2013](https://doi.org/10.1057/jos.2012.20)). | Complete outputs and matched inputs do not certify traffic-mechanism validity; no source supplies this synthetic network's speed or duration threshold. |
| Metering mechanism and queue cost | ALINEA treats ramp admission and downstream freeway state as control/response ([Papageorgiou et al. 1991](https://onlinepubs.trb.org/Onlinepubs/trr/1991/1320/1320-008.pdf)); FHWA advises considering ramp storage, arrival/release balance and adjacent-road effects ([FHWA Ramp Management Handbook](https://ops.fhwa.dot.gov/publications/ramp_mgmt_handbook/manual/manual/10_1.htm)). | These runs are fixed-time 22G/28G, **not ALINEA**. Neither source certifies a 22G/28G value, a queue threshold, or freeway benefit in this network. |
| Randomness and replication | SUMO documents separate RNG uses and Krauß sigma variation ([SUMO Randomness](https://sumo.dlr.de/docs/Simulation/Randomness.html)); FHWA discusses multiple replications for quantitative alternative comparison ([FHWA microsimulation guidance](https://ops.fhwa.dot.gov/publications/fhwahop18036/chapter6.htm)). | The early x<1000 region and sigma0 sensitivity are local diagnostic choices. One seed demonstrates an observed realization, not prevalence, statistical superiority, or a pure causal RNG decomposition. |

## Stop and Robert decision boundary

The prespecified B28 and B22_SIGMA0 candidate chains are consumed. Further green-time, demand or seed changes now would be a new scientific design, not completion of these cards. The project does **not** have evidence that a manageable-cost B leg exists under the current default full-network setting; it also does not have evidence that the thesis mechanism is structurally impossible. Stage 6 cannot be marked `COMPLETE` or a formal protocol frozen. `FAILED` would overclaim structural inability from limited tested conditions.

Robert should receive the concrete A/B/C evidence and decide whether to prioritize (a) a revised merge/scenario construction, (b) a different controller or metering-response design within the accepted thesis question, or (c) a narrower thesis claim if B cannot be elicited without untenable costs; also how to handle default-model stochastic coupling and real-world validation limits in the formal methodology. No supervisor feedback or approval is inferred from the absence of a reply. The next authorized step is consultation and a separately reviewed bounded redesign if chosen, **before** formal multi-seed experiments. A draft decision brief is adjacent. No message was sent.

## Key run and parameter register

All new full-network tests used qMain3350.4 veh/h (M1396), U150/X75, seed17, SUMO 1.26.0, 1-s step, 2700-s horizon and fixed M cells13–17 (100 m, x=[1300,1800), 30-s bins). R-demand arms used delayed qRamp900 veh/h (R240, `[540,1500)`); R0 controls had no R demand. Default model retained Krauß sigma0.5; sensitivity changed M only to sigma0. A_OPEN 60G, B_MODERATE22G+3y+35r, B_REBALANCED28 28G+3y+29r. The formal experiment protocol remains empty/unfrozen.

| Run/pair | Role | Scientific outcome source |
|---|---|---|
| Default V2 R0/A | Pressure pair; actual input matched | `artifacts/stage6_full_network_abc_matched_rebuild_20260926_v1/` and versioned `a_attribution/A_OUTCOME_REPORT_REV2.md` |
| R0_SIGMA0/A_SIGMA0 | Altered-model A capability diagnostic | `artifacts/stage6_a_rng_isolation_diagnostic_20260926_v1/SCIENTIFIC_OUTCOME_REVIEW.md` |
| Default A/B22 | Tested strong-cost fixed-time program, failed moderate B role | `artifacts/stage6_full_network_abc_matched_rebuild_20260926_v1/B_SCIENTIFIC_OUTCOME_REVIEW.md` and `B22_FCD_CONTINUITY_SUPPLEMENT.md` |
| Default A/B28 | One prespecified milder correction, failed B role | `artifacts/stage6_moderate_rebalance_20260926_v1/B28_SCIENTIFIC_OUTCOME_REVIEW.md` and `B28_FCD_CONTINUITY_SUPPLEMENT.md` |
| A_SIGMA0/B22_SIGMA0 | One missing altered-model sensitivity cell | `artifacts/stage6_b22_sigma0_completion_20260926_v1/SCIENTIFIC_OUTCOME_REVIEW.md` |

`docs/DECISIONS.md` was not changed: no new user-approved durable decision or formal parameter freeze was supplied. The factual current state and worklog are updated separately. The Tencent MemoryCore read was attempted but unavailable because the configured `colima-memory-pilot` Docker context does not exist on this host; live repository documents, immutable receipts and raw outputs take precedence.

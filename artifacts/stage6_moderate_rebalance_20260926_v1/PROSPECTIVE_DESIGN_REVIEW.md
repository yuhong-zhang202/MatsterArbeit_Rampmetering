# Prospective 28G exploratory correction: independent reviews

**Date:** 2026-09-26  
**Disposition:** `PASS_PLAN_ONLY`; no simulation or phenomenon outcome is approved by this document. Stage 6 remains `PARTIAL`.

## Scientific review

The independent `scientific_reviewer` completed Context Preflight and initially held the plan over two interpretation rules. The plan now calls `22 × 216/170 = 27.95 s` a rough proportional extrapolation from one realized service point, not a capacity estimate or literature threshold. It also requires evaluation of whether early nonlocal M divergence could materially explain any claimed protection **regardless of apparent effect size**; unresolved attribution yields `B_NOT_IDENTIFIED`. Final read-only review: `PASS_PLAN_ONLY`, zero remaining Blocker/Major/required Minor. The reviewer permits one bounded 28G exploratory arm against default V2 A, then independent outcome review. It does not predict a B effect, release C12G, or complete Stage 6.

## Data review

The independent `data_analyst` checked the arithmetic and requested prespecified R-specific FCD occupancy and slow vehicle-seconds on shared approach, ramp storage, ramp acceleration and internal connectors because E2 is class-agnostic. These measures, separate U-specific FCD, and the distinction between internal queue and external waiting are now in the plan. Review: conditional data-side plan PASS after those amendments; no raw analysis or outcome claim.

## Engineering review

The independent `simulation_engineer` reported `PASS_STATIC_FEASIBILITY`: SUMO additional XML can define `B_REBALANCED28` as a 28G/3y/29r program for existing `ramp_mid`, and WAUT can select it without changing the compiled network. An in-memory modified A additional XML passed local SUMO 1.26 XSD validation. The existing four-arm builder/runner hardcodes its arm set; the new single-arm builder and one-use runner require separate implementation and exact-card prelaunch audit. Static feasibility does not establish actual TLS behavior or scientific validity.

## Boundaries

The old 22G negative finding and original C12G HOLD remain intact. The next gate is offline package construction and exact-card engineering, data, and scientific review; **no run is released by this plan review alone**. The formal protocol remains empty/unfrozen. FHWA ramp-management guidance supports balancing release, arrivals, storage and adjacent-road effects, but provides no transferable 28-second value for this synthetic network.

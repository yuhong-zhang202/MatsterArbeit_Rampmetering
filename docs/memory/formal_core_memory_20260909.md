# Masterarbeit-Ramp-Metering — Core Project Memory

## Identity and authority

This is auxiliary long-term memory for the TU Berlin ramp-metering master's thesis workspace. Repository documents remain authoritative. Read `AGENTS.md` and route current status to `docs/PROJECT_STATE.md`, approved choices to `docs/DECISIONS.md`, supervisor statements to `docs/SUPERVISOR_FEEDBACK.md` and original sources, and formal simulation work to `docs/EXPERIMENT_PROTOCOL.md`. Later documents override stale memory. AI memory is not academic evidence and does not create approval.

## Working research direction

Study the ramp-metering sweet spot with SUMO and `sumoITScontrol`: protect freeway operation without allowing persistent ramp queues to spill back and harm urban through-traffic. The user provisionally defines the sweet spot as an acceptable control-outcome region, not one point. `qMain × qRamp` describes demand conditions, not the sweet spot. The planned progression is uncontrolled baseline, standard ALINEA, and only if the conflict appears, a simple urban-protection override. No-override-needed and no-feasible-region outcomes are valid.

The minimal concept separates mainline (`M`), ramp-bound (`R`) and urban through (`U`) traffic; `R` and `U` share an approach before diverging so persistent ramp queues can impose additional delay, throughput loss or upstream queueing on `U`. Exact geometry, thresholds, metrics, demand ranges, seeds, timings, controller and override details remain unresolved.

## Approval boundaries

Robert Hilbrich supports `sumoITScontrol`, beginning with ALINEA, a deliberately simple synthetic freeway/on-ramp/small urban network, uncontrolled demand exploration near breakdown, Krauss defaults as a starting point, and strict validation of realized vehicle insertion. He considers the finite-storage trade-off and when metering should be reduced or overridden for the subordinate network interesting. He has not confirmed the formal sweet-spot definition, final research question, title, contribution scope or experiment protocol. Peter Wagner's earlier workflow guidance is historical and is not Robert's approval.

## Current state

Stage 1 instrumentation and the core literature/measurement gate are complete. Stage 2 exploratory uncontrolled checks are incomplete. No formal protocol is frozen, no formal thesis experiment has begun, and no freeway breakdown, capacity drop, causal urban loss or sweet spot has been established.

The measurement repair distinguishes internal/external FCD lanes and verifies named-lane E2 coverage for the shared lane (0–238.80 m) and ramp-storage lane (0–204.49 m). It changed no geometry, signals, demand or behavior. Legacy E2 values are not directly comparable, and the 494.87 m compiled path is not an approved queue-storage capacity. A matched seed-17 regression preserved traffic records; this is technical evidence only.

Warm-up, measurement and clearance are configurable but not selected. Stable mean freeway speed alone is insufficient while outside-network insertion queues grow. Clearance stops new scheduling but queued vehicles may enter later. The 0/1500/1200-second arrangement is only a finite-horizon candidate. Existing high-demand outputs should first support a bounded mainline/merge diagnosis and reliable visual inspection. Any new simulations, demand grid, ALINEA, override, geometry change or formal protocol require the appropriate review and user authorization.

## Working preferences

Communicate with the user in plain Chinese. Explain the project framework before technical details, keep provisional items visibly provisional, and continue follow-through after delegated work finishes. Preserve the dirty worktree and raw data. Keep this project's memory isolated from all other projects.

Seed date: 2026-09-09. Detailed source hashes and normalized facts are in `docs/memory/formal_import_bundle_20260909.md`.

# Masterarbeit-Ramp-Metering — Core Project Memory

## Identity and authority

This is auxiliary long-term memory for the TU Berlin ramp-metering master's thesis workspace. Repository documents remain authoritative. Read `AGENTS.md`; use `docs/PROJECT_STATE.md` for current status, `docs/DECISIONS.md` for user-approved choices, `docs/SUPERVISOR_FEEDBACK.md` plus original sources for supervisor statements, and `docs/EXPERIMENT_PROTOCOL.md` before formal simulation work. Later repository evidence overrides stale memory. AI memory is not academic evidence and creates no authorization.

## Working research direction

Study a ramp-metering sweet spot with SUMO and `sumoITScontrol`: protect freeway operation while preventing persistent ramp queues from spilling back and harming urban through-traffic. The user provisionally treats the sweet spot as an acceptable control-outcome region, not one point. `qMain × qRamp` describes demand conditions, not the sweet spot. The provisional comparison route is uncontrolled baseline, standard ALINEA, and only if evidence supports the conflict, a transparent urban-protection override. No-override-needed and no-feasible-region outcomes remain valid.

The minimal concept separates mainline (`M`), ramp-bound (`R`) and urban through (`U`) traffic. `R` and `U` share an urban approach before diverging so persistent R queues can affect U. Exact geometry, safe/effective storage, metrics, thresholds, demand ranges, seeds, timing, controller settings and override logic remain unresolved.

## Approval and supervisor boundaries

User-approved provisional decisions D-001–D-004 cover the evaluation-oriented scope, acceptable-region concept, minimal M/R/U spillback mechanism, and preparation sequence. None freezes a formal parameter.

Robert Hilbrich supports `sumoITScontrol`, starting with ALINEA, a deliberately simple freeway/on-ramp/small urban network, uncontrolled demand exploration near breakdown, Krauß defaults as a starting point, and validation of realized insertion. He considers the finite-storage conflict and when metering may need reduction or override for the subordinate network interesting. He has not confirmed the final research question, title, contribution scope, sweet-spot definition, formal metrics, experiment settings or protocol. Peter Wagner's earlier workflow guidance is historical, not Robert's approval.

## Current phase

Stage 1 instrumentation and the core literature/measurement gate are complete. The user accepted G2 and closed Stage 2 as a finite uncontrolled diagnostic milestone. This closure does not complete broader exploratory validation or establish readiness for formal ALINEA comparison.

Stage 2 contains eight logical records: reused C17 plus seven new runs for C/ML/MH/RL with seeds 17/23 and a 0/1500/1200-second finite horizon. Seven of eight authorized new starts were used and no retry was used. All vehicles eventually entered and arrived before 2700 s, but every run retained R/U insertion after 1500 s; clearance was not zero-inflow recovery and final completion does not prove demand-period realization. The archived evidence and final analysis reconciled 232 files, 14,564 run-vehicle records, 4,320 E1 rows, 2,912 cohort rows, 2,100 R first-downstream observations and 198 matched-seed contrasts. Scientific review accepted the bounded diagnostic scope without a Blocker or Major.

At qRamp=720, lower qMain produced more demand-period R downstream observations, lower R/U outside accumulation and more U arrivals in both seeds. Higher qMain produced zero demand-period R downstream observations in both seeds, more R/U outside accumulation and fewer U arrivals, while the internal M-only section retained high passage and speed. At qMain=3200, lower qRamp strongly reduced outside accumulation and increased U arrivals, but did not consistently improve all urban or freeway measures. These are two-seed exploratory sensitivities, not statistical robustness or causal conclusions.

No freeway Breakdown, Capacity Drop, steady state, capacity, causal urban loss or sweet spot has been established. Internal M-only E1 loops support their declared aggregate merge-entry scope only. Ordinary E1 per-vehicle completeness, exact aggregate-flow schedule timing and full mid-run outside-waiting curves remain unverified. The 0/1500/1200 arrangement is a finite-horizon candidate, not a selected formal timing design. Old upstream E1 values affected by insertion overlap remain ineligible for state inference; the superseded diagonal G1 package remains unauthorized.

## Proposed route and next action

`docs/EXPLORATORY_VALIDATION_COMPLETION_PLAN.md` is Proposed and not authorized for execution. It defines six outputs and eight gates, then Stage 3 archive-only diagnosis, conditional Stage 4 bounded targeted validation, Stage 5 exploratory assessment closeout, and Stage 6 our formal-design proposal for Robert. Stage 3 would add zero simulations. Stage 4 requires a separately approved registration card and may be not required. Stage 5 must distinguish completed assessment from `preliminary_ready`, `specific_obstacle`, or `unresolved`. Stage 6 does not itself authorize supervisor contact, protocol freezing or formal runs.

The current proposed next action is to review and explicitly approve or reject Stage 3's archive-only analysis contract. Formal-design drafting may be informed by targeted exploration, but formal comparison, protocol freezing and production runs require explicit authorization and resolution of the selected question's critical measurement and baseline definitions. `docs/EXPERIMENT_PROTOCOL.md` is empty; no formal thesis experiment has begun.

## Operational boundaries

Communicate in clear Chinese and mark proposals, observations, approvals and unknowns separately. Preserve the dirty worktree, archived evidence and read-only raw data. Use required specialist routing for material simulation, data-analysis and scientific-design work.

Keep ordinary Codex work on the existing subscription provider. Tencent memory recall is an explicit local aid and can be stale. Prepare updates only when explicitly requested. Every paid update requires fresh approval of the exact delta and complete L3 hashes, model, request count and cost ceiling. Never reuse a dry-run-only manifest as paid authorization and keep this project's identity isolated from other memories.

Candidate date: 2026-09-10. Detailed changed facts and source hashes are in `docs/memory/incremental_update_20260910.md`.


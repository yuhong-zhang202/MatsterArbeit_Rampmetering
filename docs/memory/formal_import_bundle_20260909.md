# Masterarbeit Ramp Metering — formal memory seed 2026-09-09

Project identity: `Masterarbeit-Ramp-Metering`  
Workspace: `/Users/yuhongzhang/Desktop/Masterarbeit-Ramp-Metering`  
Memory identity: team `team-masterarbeit-ramp-metering`, agent `agent-project-memory`, user `user-yuhong-zhang`.

## Authority and safety rules

This is a traceable, normalized seed for auxiliary long-term project memory. It is not academic evidence and must not replace the current repository documents. On every substantive task, read `AGENTS.md` and the relevant current project documents. Use `docs/PROJECT_STATE.md` for current status, `docs/DECISIONS.md` for user-approved decisions, `docs/SUPERVISOR_FEEDBACK.md` plus original sources for supervisor statements, and `docs/EXPERIMENT_PROTOCOL.md` before formal simulation work. Resolve conflicts explicitly. Never treat AI-generated memory, old chat, silence, or a historical supervisor statement as current approval. Do not reuse old execution authorization.

## Research direction and status boundaries

The working topic is a SUMO and `sumoITScontrol` study of the ramp-metering sweet spot: balancing freeway protection against persistent ramp-queue spillback into a connected urban network. The current direction is supported by Robert Hilbrich, but the final research question, title, contribution scope, formal sweet-spot definition, experimental design, and protocol are not supervisor-confirmed or frozen.

The user-approved provisional concept treats the sweet spot as an acceptable control-outcome region, not a unique point. Candidate controls should first satisfy minimum freeway and urban protection requirements; system-wide loss may then be compared within the acceptable region. `qMain × qRamp` is the demand-condition backbone, not the sweet spot itself. The intended comparison sequence is uncontrolled baseline, then standard ALINEA, and only if the explored conflict appears, a simple transparent urban-protection override. The override is conditional and is not the thesis topic. A result showing that no override is needed, or that no feasible acceptable region exists, is valid. Metrics, thresholds, weights, robustness rules, and override logic remain unresolved.

The provisional minimal mechanism distinguishes freeway mainline vehicles (`M`), ramp-bound vehicles (`R`), and urban through-traffic (`U`) that does not enter the freeway. `R` and `U` share a one-lane urban approach before diverging, so a persistent ramp queue can cross the finite-storage boundary and impose measurable additional delay, throughput loss, or upstream queueing on `U`. `X` is technical cross traffic. Exact topology, lane lengths, signal placement, demand, queue definitions, detectors, and parameters remain provisional.

Stage 1 technical instrumentation and the core literature/measurement gate are complete. Stage 2 exploratory uncontrolled checks are incomplete. No formal protocol is frozen, no formal thesis experiment has started, and no preliminary output may be presented as thesis evidence. No freeway breakdown, capacity drop, causal urban loss, or sweet spot has been established.

## Explicit supervisor guidance

Peter Wagner's 2026-06-18 and 2026-07-15 emails are historical guidance. He proposed the freeway-versus-urban trade-off, recommended learning and running `sumoITScontrol`, starting with a synthetic scenario, scanning `qMain` and `qRamp`, examining travel times, speeds, densities and capacity limits, then adding control and checking the connected urban network. His statements do not constitute Robert Hilbrich's approval.

Robert Hilbrich's reply received 2026-08-25 is current supervisor guidance. He supports starting with `sumoITScontrol`, ALINEA, a deliberately simple synthetic freeway with one on-ramp and a small upstream urban network with initially fixed-time signal control, and an uncontrolled demand-grid exploration near breakdown. He described `qRamp <= C - qMain` only as an intentionally simplified starting hypothesis: real capacity is variable and unknown, the merge affects effective capacity, capacity drop may reduce post-breakdown discharge, ramp demand can exceed admissible inflow, and finite storage can force a controller to release traffic to protect the subordinate network even when the freeway lacks residual capacity. He sees the timing of reducing or overriding metering for the subordinate network as interesting.

Robert recommends SUMO's standard Krauss car-following model with default parameters initially, without forcing desired behavior absent calibration data. First check whether plausible breakdown and capacity drop emerge; if not, investigate car following, lane changing and merging, ramp geometry, and demand. Validate that intended high demand actually enters the network; his starting examples are `departPos="last"`, `departLane="best"`, and `departSpeed="max"`. He considered an interim presentation in late October or early November realistic if the framework runs, the scenario exists, and initial uncontrolled results are available. English is acceptable to him, but institutional permission and the exact presentation date remain to be clarified.

## Current technical and measurement state

The local environment uses macOS 15.3 on Apple Silicon, SUMO/sumo-gui 1.26.0, Python 3.13.0, `sumoITScontrol` 0.1.0, TraCI 1.26.0 and sumolib 1.26.0. The fixed upstream ALINEA example passed a technical smoke test but contains warnings and is not a formal experiment configuration.

The project-owned minimal scenario is a working technical scaffold. It contains a two-lane freeway, one entrance ramp, the shared `R/U` urban approach, a fixed-time upstream signal, and separate `M/R/U/X` routes. Low-load and overloaded headless checks showed the intended spillback mechanism can be triggered, but the overload had incomplete insertion and cannot support scientific conclusions. Geometry, demand, signals, duration and seeds remain placeholders.

Stage 1 added four lane-specific E1 detectors immediately upstream and downstream of the merge, configurable `qMain/qRamp`, and accounting for requested, planned, inserted, arrived, in-network and non-inserted vehicles. Independent validation reconciled E1 summaries with raw XML. Technical execution success is kept separate from scientific eligibility; all runs remain ineligible for capacity conclusions.

The authorized measurement repair added separate internal/external FCD accounting and verified that each E2 observes its named lane: shared lane 0–238.80 m and ramp-storage lane 0–204.49 m. It did not change geometry, priorities, signals, demand, behavior, or formal storage definitions. Legacy 250 m successor-lane coverage remains unverified and old/new E2 values are not directly comparable. The compiled path from shared boundary to ramp end is 494.87 m, but neither that path nor the named storage edge is an approved safe/effective queue capacity. A matched seed-17 regression preserved identical traffic records; 17 tests and five narrow measurement checks passed. This is technical evidence only.

## Stage 2 timing and diagnosis

Warm-up, measurement and post-demand clearance are separately configurable, but their durations are not selected or frozen. Five preliminary runs used seed 17 only. A 600-second warm-up excludes observed shared-approach stopping around 412–414 seconds; such events cannot automatically be called startup artifacts. Stable mean freeway speed does not prove global stability because outside-network insertion queues may continue to grow. Clearance stops scheduling new demand, but vehicles already waiting outside may enter later; in-network travel time omits that departure delay.

The longest retained trajectory has `qMain=3200 veh/h`, `qRamp=720 veh/h`, seed 17 and a 2700-second horizon. Waiting-to-insert counts continued growing across candidate cutpoints, and the last vehicle entered at 2245 seconds and arrived at 2401 seconds. These are single-trajectory diagnostics, not selected durations or independent replications. The later G1 review proposes retaining 0/1500/1200 seconds only as a finite-horizon candidate while first diagnosing mainline/merge behavior from existing outputs. It recommends no automatic six-run diagonal matrix: changing `qMain` and `qRamp` together cannot identify their individual effects, and a second seed does not fix that confounding. No new simulation, demand value, seed, retry, timing, threshold or detector change is approved by that review.

Current next work is bounded: reuse existing high-demand outputs for a stopped-boundary mainline/merge diagnosis; complete reliable dynamic visual inspection; then submit only the minimum discriminating additional run proposal, if needed, for user approval. Do not automatically expand to a demand grid, ALINEA, override implementation, geometry changes, or formal protocol. Prepare compact initial evidence and ask Robert to confirm the sweet-spot concept, evaluation-oriented scope, research-question hierarchy, and roles of urban demand and ramp storage.

## Source manifest

The following repository files were normalized into this seed. Their contents remain authoritative at the recorded hashes; later versions supersede this seed.

- `docs/PROJECT_STATE.md` — SHA-256 `94b952d1ea76dd86616b69e78c164b5b64f891f0d9d6d38b216397eb9921d827`
- `docs/DECISIONS.md` — SHA-256 `4e440204b812a9ed28181b6b4aa54818ca5e7a39d207aeaadcab12cf8cb00d7a`
- `docs/SUPERVISOR_FEEDBACK.md` — SHA-256 `49d8d410f5c68e56c023b9e0f92b23cdf00bde55658e993a4f7ce5be996ec446`
- `docs/memory/project_snapshot_20260909.md` — SHA-256 `0cb4c5f173eaa416c1dc8d0c0d5fd97e2e9d35fd2faedcc69d0c4e7e7b057a8f`
- `docs/STAGE2_G1_REVIEW_20260909.md` — SHA-256 `0973040000e78c9360c924d1161665d71d0524b3441e4a5f37d91803b2c0a17f`

Seed date: 2026-09-09. Later project documents must override stale memory.

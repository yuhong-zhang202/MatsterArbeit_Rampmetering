# Proposed bounded uncontrolled demand probe — 2026-09-30

**Status: Proposed for user and supervisor discussion only.** This document does not approve, prepare, or release a SUMO run, change scientific inputs, or freeze `docs/EXPERIMENT_PROTOCOL.md`. Stage 6 remains exploratory `PARTIAL`.

## Why a new probe is considered

Robert's 2026-09-30 reply asks for geometry, lane connection, and actual insertion checks before an uncontrolled `qMain × qRamp` scan. The rebuilt seed-17 R0/A/B22/B28 network has two preserved M lanes plus a 294.51 m auxiliary lane, complete M insertion (maximum `departDelay` 1 s), and, for each R-demand arm, 240/240 recorded R changes from `merge_section_0` to mainline `merge_section_1` before the auxiliary lane ends. These observations establish runtime merging in those stored runs, not a capacity boundary. Source: `docs/supervision/2026-09-30_robert_hilbrich_reply.md`, `docs/PROJECT_STATE.md`, and the raw `lanechanges.xml`/`fcd.xml`/`tripinfo.xml` paths recorded in `docs/WORKLOG.md` on 2026-09-30.

## Candidate first stage, not an adopted design

Consider a **maximum 2 × 3 exploratory first-stage matrix**: `qMain ∈ {3199.2, 3350.4} veh/h` and `qRamp ∈ {0, 720, 900} veh/h`. These are previously investigated demand levels, not an inferred capacity range. Hold network, vehicle behaviour, U/X background, route construction, output definitions, and the demand time windows identical across the proposed cells. A possible common temporal pattern is R demand in `[540,1500)` with an open ramp; it must be fixed before any comparison. A single common seed could locate candidates, but cannot establish a robust boundary. No cell, including historical 3199 or 3350 runs, is counted as reusable until requested inputs, actual departures, network/behaviour and measurement windows are independently verified to match this design. If a common time pattern is changed to investigate steady state, none of the historical arms is automatically reusable.

Before execution, specify a reviewed exact input and resource card for each permitted run, a maximum number of new starts, stop triggers, and a common analysis script. A separate user execution authorization is required. Do not infer authorization from Robert's email, this proposal, or D-011.

## Prespecified measurements and gates to resolve before execution

For each cell, report requested versus actual M/R departures, `departDelay`, all-vehicle lifecycle and output completeness; unique R auxiliary-to-mainline lane changes; per-vehicle first `merge_section` edge entry and downstream passage in fixed half-open time bins; M local speed, accumulation, full-trip time; and ramp/urban queue and delay under the same spatial and temporal definitions. Keep source insertion, entering `merge_section`, lane change, and downstream passage as distinct events. Define the duration and spatial pattern required to call a result a *candidate* critical transition before inspecting new outcomes; no threshold is selected after observing a cell.

Stop interpretation for any cell with unintended mismatch in fixed exogenous fields of a planned comparison (network, U/X background, seed/vehicle attribute vector, timing, routes, or behaviour), source insertion limitation, incomplete output, or an unresolved comparison confound; intended M/R demand differences remain the variables under test. If the first stage does not bracket a change from relatively stable to sustained deterioration, report only that the boundary was **not located within the tested range**. Even a bracketed change under delayed R loading would describe that transient demand pattern, not steady-state merge capacity or capacity drop. Any extension to lower or higher demand needs its own bounded proposal, budget, review, and authorization. A single-seed synthetic probe cannot yield a robust numerical capacity or thesis-level causal conclusion.

## Existing-result boundaries

The original RI3350 R0/A remains `NOT_PAIRABLE` / `A_NOT_EVALUABLE` and is excluded. Later rebuilt default-model R0/A passed its pre-R matching check, but default-model M deterioration has unresolved attribution. B22/B28 did not show M protection and are controlled arms, not cells of the proposed uncontrolled matrix. A's old 226 R by `t<=1500` counts first entry to the `merge_section` edge; actual auxiliary-to-mainline changes by that cutoff are 225. Those measures must not be relabelled as one another. Fixed-time platooning remains a hypothesis, not a demonstrated cause.

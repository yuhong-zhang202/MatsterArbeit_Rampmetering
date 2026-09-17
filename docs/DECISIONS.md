# Research and Implementation Decisions

This file records choices explicitly approved by the user. A user-approved item is not automatically supervisor-confirmed or frozen. Formal experiment settings belong in `EXPERIMENT_PROTOCOL.md` and remain unset until separately authorized.

## D-001 — Evaluation-oriented thesis scope

- **Date:** 2026-08-31
- **Status:** `User-approved — provisional, pending Robert Hilbrich confirmation`
- **Decision:** Keep the ramp-metering sweet spot as the main research focus. Use ALINEA as the first controller and treat a simple urban-protection override only as a possible intervention for studying the sweet spot. Do not make complex controller development a core requirement unless Robert considers the evaluation-oriented contribution insufficient.
- **Boundary:** This does not establish the final research question, thesis title, controller implementation, or formal experiment design.

## D-002 — Provisional sweet-spot concept

- **Date:** 2026-08-31
- **Status:** `User-approved conceptual direction — pending Robert Hilbrich confirmation`
- **Decision:** Treat the sweet spot as a potentially non-empty acceptable region rather than a unique point. At a high level, candidate control choices must protect both freeway and urban-network performance to minimum acceptable levels; system-wide loss may then be compared within that region. A full Pareto analysis is not currently required.
- **Boundary:** Protection metrics, thresholds, weighting, robustness rules, and the formal definition remain unresolved. The sweet spot is a control-outcome concept conditional on demand and network conditions, not simply a favourable point in the `qMain × qRamp` demand plane.

## D-003 — Provisional minimal urban-spillback mechanism

- **Date:** 2026-08-31
- **Status:** `User-approved exploratory starting mechanism — not frozen`
- **Decision:** For the first project-owned scenario, distinguish freeway-mainline traffic (`M`), ramp-bound traffic (`R`), and urban through-traffic that does not use the freeway (`U`). Use a simple shared urban approach and downstream divergence so that a persistent ramp queue can cross the finite-storage boundary and impose measurable additional effects on `U` traffic.
- **Boundary:** Exact topology, lanes, lengths, traffic-signal placement, demands, queue definitions, detectors, and parameters remain proposed technical choices. The scenario must first be validated as exploratory work.

## D-004 — Preparation workflow before Stage 2

- **Date:** 2026-08-31
- **Status:** `User-approved workflow sequence`
- **Decision:** Complete Stage 1 technical instrumentation first, then pause simulation work to complete the core literature and measurement-knowledge gate, and only afterward begin Stage 2 with a few representative uncontrolled conditions.
- **Boundary:** This sequence does not approve Stage 2 demand values, measurement windows, clearance handling, Breakdown or Capacity Drop definitions, seeds, formal exclusion rules, or a full demand grid.

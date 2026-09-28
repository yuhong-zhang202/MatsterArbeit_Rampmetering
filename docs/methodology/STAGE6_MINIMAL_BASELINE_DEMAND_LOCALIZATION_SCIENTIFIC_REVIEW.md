# Scientific Review — Stage 6 Minimal Baseline Demand Localization Design

**Date:** 2026-09-21

**Scope:** Read-only review of an exploratory design proposal; no simulation execution authorization

**Final disposition:** `PASS_EXPLORATORY_DESIGN`

**Open findings:** Blocker 0 / Major 0 / Required Minor 0

## Reviewed artifacts

|Artifact|SHA-256|
|---|---|
|`STAGE6_MINIMAL_BASELINE_DEMAND_LOCALIZATION_PLAN.md`|`92b81e9283bb55f3d99f1ed812e121f014c15dcef782a52209d008ac6dc636a9`|
|`STAGE6_MINIMAL_BASELINE_DEMAND_LOCALIZATION_MATRIX.csv`|`88374d7ca3394fc47ac8d30652a601ca0fdfe0e8d6460f2710087ddb5e5fa321`|
|`STAGE6_MINIMAL_BASELINE_DEMAND_LOCALIZATION_LAUNCH_CARD_DRAFT.json`|`edefd87208146790a08348b9b5d185eb18f1416ae925893dac01291466c4d431`|

The independent `scientific_reviewer` performed the required Context Preflight and checked the locked method, existing application and A/P decomposition, accepted inputs, project state, decision/protocol boundaries, Robert Hilbrich's source feedback, and the proposed design artifacts. No SUMO, netconvert or TraCI process was started.

## Review checks

The final design passed the requested checks against result-chasing, an unbounded ladder, excessive points, formalization of P-positive, single-seed overclaiming, insertion artifacts, urban-overloaded baselines, classifier drift, transfer from old geometry, unjustified demand spacing, excessive run budget, and missing early-stop conditions.

The 150 veh/h nominal qMain spacing is explicitly a `PROJECT OPERATIONALIZATION`, not a literature-derived increment, capacity estimate, or supervisor-approved value. The old-geometry observations constrain risk and the ceiling only; they cannot accept a current-geometry baseline.

## Findings closed during review

1. The plan, CSV matrix and draft launch card now use the same adaptive state machine. A higher qMain point is released only after complete `NO_QUALIFYING_EVENT` with every release gate clear. P-positive-but-unsuitable, unresolved, not-evaluable, overload, realization, artifact and technical states stop the ladder.
2. Mainline source-delay context is evaluated by exact requested-versus-actual identity sets on the locked 30 s grid. Cross-bin shifts in decision-relevant bins remain `M_SOURCE_CONTEXT_UNRESOLVED`; they are not silently accepted, converted to demand failure, or used to release a higher point.
3. The direct urban-harm hard condition requires registered same-identity/time/location R-blocker/U-victim evidence. Unlinked qualitative warnings cannot be converted into an overload rejection by discretionary terms such as “persistent” or “dominant.”
4. `NO_BASELINE_WITHIN_BUDGET` is reserved for a completed valid, non-overloaded L1–L3 ladder with complete negative P results. Specific borderline, overloaded or not-evaluable labels take precedence.

## Scientific boundary

The review approves the internal coherence of the **design only**. It does not validate the numerical qMain ladder empirically, establish physical breakdown, approve a formal thesis baseline, estimate breakdown probability, freeze a formal protocol, resolve O2, or authorize execution. The draft launch card is deliberately unmaterialized. Future execution requires exclusive paths, generated-input hashes, executable and analyzer bindings, technical/data/scientific review of the materialized card, and explicit user approval of that exact final card.

## Remaining limitations

- Seed17 localization plus one seed23 confirmation is a minimal repeatability check, not a stochastic breakdown-probability design.
- The first current-geometry State-1 neighborhood is unknown until the authorized sequence is actually run.
- A categorical source-context or urban-harm ambiguity can terminate the small ladder without locating a baseline; that conservative false-negative risk is intentional.
- Capacity-drop evidence remains supporting only and is not required for baseline acceptance.

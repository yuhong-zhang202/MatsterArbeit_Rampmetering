# Independent scientific prelaunch review — repaired PAIR3199 delayed-R treatment

**Disposition: PASS for preparation only; no execution authorization.**  
**Findings:** Blocker 0 / Major 0 / required Minor 0.  
**Confidence:** High for the prospective design boundaries and static-input claim; Moderate for any future single-run attribution.  
**Execution:** Not authorized. This review did not start SUMO, TraCI, or netconvert.

## Context preflight

Read `AGENTS.md`, `docs/PROJECT_STATE.md`, `docs/DECISIONS.md`, `docs/EXPERIMENT_PROTOCOL.md`, and `docs/WORKLOG.md`; the approved bounded scan plan; and the adopted `docs/methodology/STAGE6_EXPLORATORY_RAMP_INDUCED_WITNESS_CONTRACT.md`.

Current phase: offline v5 common-input repair followed by a separately reviewed treatment proposal. Stage 6 is PARTIAL, O2 is NOT_RESOLVED, and the formal experiment protocol remains empty/unfrozen. D-005 adopts the witness contract only for the PAIR3199 exploratory matched pair. D-006's single treatment authorization is consumed. The previous treatment remains `NOT_EVALUABLE`; its raw/card are not reinterpreted or reused. The exact review question is whether the new v5-bound card and preregistered post-run sequence are scientifically suitable for a prospective exploratory attempt, while remaining unauthorized.

## Materials reviewed

- Bounded scan plan and adopted witness-contract text/hash.
- v5 repair scientific review, invariant report and provenance receipt.
- Previous treatment status and consumed D-006 card identity in current project state/decision records.
- New draft card, preparation provenance receipt, independent engineering and data/provenance reviews, engineering receipt, R02 read-only preflight, and post-run matching/witness sequence.
- No raw data were reanalyzed. The engineering/data receipts and static checker results were reviewed as evidence; their computations were not repeated in this scientific review.

Key provenance: v5 invariant report SHA-256 `509f1a46873b6922ce22e18f4100fa2dcb84a632d80ee9a014750efc6c857d54`; v5 provenance receipt `3a2531c3bbf3d9d69ac6c94f0f2663b67b47ffde7ce36c7ea0e1a943b74e32c9`; adopted contract `958890a7dd017110787a85d77ebfa3e6dac2b7d862f0fd91f6bafb7cf1738d9a`.

## Scientific assessment

### Design and contrast

The new card binds qMain 3199.2 veh/h, seed 17, A_OPEN, M=1333, U=150, X=75, and delayed R=192 on `[540,1500)` (720 veh/h). It references the v5 repaired treatment inputs and the adopted contract hash. The v5 independent reviews and invariant report support a **planned-input** contrast: 1,558/1,558 M/U/X identities match in ID, desired departure schedule, route, vType and recorded-precision speedFactor; the 192 treatment-only identities are exactly `R_flow.0–191`. This is appropriate evidence for preparing the R-only demand contrast.

This does **not** establish runtime insertion, identical microscopic trajectories, or identical simulator-internal random decisions. The reviewed v5 scientific record explicitly preserves those limits. The card also does not make the existing control a clean normal baseline: it retains `historical_low_r_status=NOT_EVALUABLE` and `use_as_clean_normal_baseline=false`; existing screen failures and low-speed/C warnings remain historical evidence. The older treatment's `NOT_EVALUABLE` disposition and consumed authorization are explicitly linked by immutable card hash, with reuse/reinterpretation disabled.

### Preregistered post-run gate

The sequence correctly separates static planned-input matching from observed trajectory equivalence. Before any witness classification, it requires a same-time/location/cell/lane, identity- and coverage-aware comparison of M/U/X trajectories over the interval before first meaningful R exposure. It directs that material unexplained pre-exposure divergence, or failed identity/coverage checks, make the **pair** `NOT_EVALUABLE`; post-exposure witness analysis is allowed only after the gate is evaluable and passes.

That order addresses the specific prior failure mode without asserting that v5 inputs guarantee trajectories. It does not add a numeric tolerance, modify P/S/L or Candidate A/C, or relax a historical screen. Subsequent analysis remains bound to the adopted contract's fixed exposure/event windows, locked event criteria, same-time/location control comparison, independent raw-FCD/route reconstruction, event ordering, and alternative-cause checks. If an incremental treatment event cannot be distinguished from the control warnings or another material cause, the existing contract returns `NOT_EVALUABLE`, not a favorable witness or a negative result. The scientific scope remains one exploratory synthetic-scene observation, not a formal experiment, capacity estimate, probability claim, or separation of added volume from merge friction.

### Resources and authorization boundary

The exact card is `DRAFT_NOT_AUTHORIZED`, with `execution_authorized=false`, `approval_required=true`, `run_command=null`, `max_starts=1`, `technical_retries=0`, and progression disabled. The proposed 90 s / 75,000,000 decimal-byte polled stop triggers are explicitly `PROPOSED_NOT_AUTHORIZED`; the 100 ms polling/possible slight overshoot is stated. They are not inherited from D-006 and this review does not approve them. The R02 receipt reports read-only preflight with no process started. A separate user authorization and any required resource acceptance remain necessary.

## Findings by severity

- **Blocker:** None.
- **Major:** None.
- **Required Minor:** None.
- **Observation:** None requiring action before preparation is considered complete. The future report must continue to identify this as a new card/attempt using its exact hash; the reused human-readable condition ID alone is not enough to identify which immutable attempt is being discussed. The new card already records the previous card hash and binds distinct package, output and consumption paths.

## Measurement checks

Not applicable to this prelaunch design review: no simulation measurements, output-processing implementation, or new raw results were assessed. This review does not validate future detector coverage, lifecycle completeness, FCD sampling, or post-run computations; those remain required engineering/data post-run checks under the adopted contract.

## Recommendation

**PASS** for `PAIR3199_REPAIRED_TREATMENT_PRELAUNCH_READY_AWAITING_AUTHORIZATION` as a preparation-only disposition, provided the reviewed exact card, receipts, and hashes remain unchanged. No execution permission is granted. No scientific inputs, thresholds, classifier, witness contract, formal protocol, or historical disposition are changed.

# Independent scientific review — PAIR3199 matched-input repair v5

**Disposition: PASS for the bounded offline common-input construction.**  
**Findings:** Blocker 0 / Major 0 / required Minor 0; one Observation.  
**Confidence:** High for the static input contrast and v5 parser safeguards; Moderate for historical stochastic-cause attribution and future traffic interpretation.  
**Authorization:** None. This review grants no card or simulation start.

## Context preflight and review scope

Reviewed `AGENTS.md`, `docs/PROJECT_STATE.md`, `docs/DECISIONS.md`, `docs/EXPERIMENT_PROTOCOL.md`, `docs/WORKLOG.md`, the adopted `docs/methodology/STAGE6_EXPLORATORY_RAMP_INDUCED_WITNESS_CONTRACT.md`, the prior treatment data/lifecycle review and scientific post-run review, and the v5 repair report, engineering and data/provenance reviews, XML inputs, manifest, invariant report, provenance receipt, checker, and tests.

The current phase is offline v5 matched-input repair. The previous single treatment start is consumed and remains `NOT_EVALUABLE`; it is neither a witness nor an evaluable negative. D-005 adopts the exploratory contract for this pair only. The formal protocol is unchanged and unfrozen. Earlier repair packages are preserved but superseded; this disposition relies on v5 evidence only. The exact question is whether v5 provides an adequately bound planned-input R-only contrast and whether a separately reviewed treatment proposal is scientifically worth preparing.

## Assessment and findings

### Blocker / Major / required Minor

None for the stated static input-construction objective.

### Observation — matched inputs do not guarantee matched trajectories

V5's independently reviewed pair has M/U/X counts 1,333/150/75 on both sides and 1,558/1,558 exact common IDs and complete records. Per-identity integer-millisecond departures, routes, types and recorded-precision speedFactors match; route definitions match 4/4 and vType definitions 1/1. Treatment-only IDs are exactly `R_flow.0`–`R_flow.191`, at 5-second intervals from 540 through 1,495 seconds. The data review independently recomputed these invariants and package/source hashes. This is a defensible **planned-input** contrast: among these two constructed route files, the added exogenous vehicle records are R only.

V5 also closes the described parser bypass class at the input boundary: it accepts strict UTF-8 without BOM, performs an Expat safety parse that rejects DTD/entity declarations and references, comments and processing instructions, then applies a strict top-level/node-attribute/nesting whitelist. The 12/12 tests include UTF-16 and UTF-8 DTD/default-attribute attempts, BOM, treatment-only flow, nested parameter, unknown attribute, and common route/type/factor mismatches. Engineering and data/provenance reviews independently report the suite and exact-hash package checks passing. I rely on v5, not on any earlier revision's PASS.

This does not prove future insertion/lifecycle success, trajectory equivalence, or equality of all simulator-internal random decisions. R traffic changes interactions and may change simulation-time stochastic draws. Nor does v5 change the provenance of the existing control raw: that run used its original flow input. A new treatment must still pass the adopted contract's post-run lifecycle, actual R exposure, pre-R trajectory, and same-time/location/lane checks; material pre-R divergence remains a reason not to make an R-associated witness claim.

**Smallest action for any later use:** Prepare a new exact proposal bound to the v5 route-input hashes, accepted network/configuration hashes, and adopted contract hash. Retain the pre-R and lifecycle checks and describe this as planned-input matching, not trajectory matching. Any start needs fresh reviews and separate explicit user authorization because the previous authorization was consumed.

## Historical root-cause distinction

- **U/X omission — immediate mechanism supported, High confidence.** The prior treatment data review records SUMO log warnings that it ignored U and X because the old treatment route source was not departure-sorted; the R=0 control realized both flows. V5 materializes the complete U/X identities into globally departure-sorted explicit vehicle records on both sides. This supports route-source ordering as the immediate omission mechanism.
- **M speedFactor mismatch — absent per-identity materialization supported; precise RNG-order mechanism unproven.** The previous raw comparison found only 2/1,333 exact M-factor matches, including vehicles scheduled before R activation. The previous common vType did not fix sampled factors to vehicle identities, so equal seeds alone did not guarantee a match. Adding delayed R is consistent with changed random draw/construction order, but existing evidence does not isolate or prove that mechanism. V5 fixes the prospective contrast by applying each identity's recorded control `vehroute.xml` speedFactor to both arms. This repairs the input match; it does not retrospectively prove why the old factors differed.

Using recorded `vehroute.xml` factors rather than two-decimal `tripinfo.xml` avoids the documented serialization-precision trap. Exactness means lexical equality at the most precise stored record; unrecorded floating-point bits are not claimed.

## Measurement checks

Not applicable to this static input-design review: I did not review measurement code, detector coverage, aggregates, or new run outputs. Prior result reports are cited only to establish why the input repair is needed. No previous outcome is reinterpreted.

## Recommendation and boundary

It is scientifically reasonable to **separately prepare** a repaired PAIR3199 treatment proposal using v5, because the identified input-level comparability failures are directly addressed and the scoped exploratory question remains testable. Preserve the control's historical `NOT_EVALUABLE`, screen, and warning status. Preparation does not imply execution. Fresh engineering, data/provenance, and scientific prelaunch reviews must inspect the exact future card and its hashes; the consumed authorization cannot be reused.

No SUMO, TraCI, or netconvert was run. No demand or geometry value, classifier, threshold, witness contract, formal protocol, or prior treatment disposition was changed.

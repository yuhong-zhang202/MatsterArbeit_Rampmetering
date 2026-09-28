# Independent scientific review — PAIR3199 matched-input repair v3

**Disposition: PASS for the narrowly stated offline input-construction objective.**  
**Findings:** Blocker 0 / Major 0 / required Minor 0; one Observation.  
**Confidence:** High that the static M/U/X input records are matched; Moderate that the observed causes are fully attributable as described.  
**Authorization:** None. This review does not authorize a run or a new treatment card.

## Context preflight and scope

Reviewed `AGENTS.md`, `docs/PROJECT_STATE.md`, `docs/DECISIONS.md`, `docs/EXPERIMENT_PROTOCOL.md`, `docs/WORKLOG.md`, the adopted `docs/methodology/STAGE6_EXPLORATORY_RAMP_INDUCED_WITNESS_CONTRACT.md`, the prior treatment lifecycle/data review and scientific post-run review, and the v3 repair report, common-demand manifest, invariant report, provenance receipt, and independent data/provenance review.

The current phase records the single authorized treatment start as consumed and its pair outcome as `NOT_EVALUABLE`; the formal protocol is not frozen. The adopted witness contract is limited to Stage 6 exploratory existence validation. The exact review question is whether v3 repairs the input-level R-only contrast sufficiently to merit separate future preparation. This review does not re-adjudicate the prior run's witness result.

## Findings

### Blocker / Major / required Minor

None for the stated static-input construction objective.

### Observation — input matching does not establish trajectory matching

V3 fixes the common M/U/X identities, integer-millisecond desired departures, route and vType assignments, precise lexical speedFactors, and departure placement attributes in both files. Its checker also compares full route and vType definitions and restricts treatment-only vehicle IDs to the 192 R records. The independent data/provenance review reports 1,558/1,558 exact common records, 1,558/1,558 exact speedFactors, 4/4 equal route definitions, 1/1 equal vType definitions, and matching package/source hashes. This is a defensible **input-level** R-only contrast.

These invariants do not guarantee identical realized trajectories or all internal random decisions. Traffic interactions change once R enters, and SUMO may consume stochastic draws through behavior that is not represented by the four bound fields. The v3 report appropriately says that the exact old speedFactor RNG draw order is unproven. Any later analysis must still compare pre-R trajectories and lifecycle from raw outputs under the adopted contract; a pre-R divergence material to the event remains grounds for `NOT_EVALUABLE`.

**Smallest action:** Preserve that limitation on any future card/review; make no claim of trajectory equivalence from static checker PASS alone. No user or supervisor confirmation is required for this caution; any future start still requires separate user authorization.

## Root-cause assessment

- **U/X omission — supported, High confidence.** The prior treatment data review records SUMO's `sumo.log` warnings that it ignored `U_flow` and `X_flow` because the route source was not departure-sorted. The prior control realized those flows. V3 replaces the unordered flow mixture with globally departure-sorted explicit vehicle records; independent static review verifies U=150 and X=75 on both sides. The evidence supports source ordering as the immediate omission mechanism.
- **M speedFactor mismatch — missing explicit per-vehicle binding is supported; precise RNG mechanism remains unproven.** Prior results had only 2/1,333 exact M speedFactor matches, including vehicles departing before R activation, while the old common vType did not fix each identity's factor. Same seed alone therefore did not bind factors to vehicle IDs. Adding the delayed R flow is consistent with changed random draw/vehicle construction order, but the reviewed records do not isolate or prove that causal mechanism. V3 addresses the failure prospectively by assigning both arms each common vehicle's precise factor from the immutable control `vehroute.xml`; it does not prove why every old factor differed.

The speedFactors were taken from `vehroute.xml`, not rounded `tripinfo.xml`; that is a suitable recorded-precision source for this pairing. The data review notes that unrecorded internal floating-point bits cannot be recovered, so “exact” here means exact lexical equality of the recorded values.

## Assessment of the v3 contrast

The v3 package preserves M/U/X counts at 1,333/150/75 and has those same 1,558 IDs in both arms. Desired departures are reconstructed in integer milliseconds; route, type and speedFactor match per identity. The treatment adds exactly `R_flow.0`–`R_flow.191`, scheduled every 5,000 ms from 540,000 through 1,495,000 ms. The manifest retains the previously adopted qMain, R schedule, geometry, and contract references; no formal protocol amendment is represented. The fail-closed checker report has no mismatches, and the independent data review reports 6/6 mutation tests passing, including missing U identity and common speedFactor/route/vType changes.

This supports a controlled **planned-input** contrast, not a guarantee that both future runs will realize all scheduled identities or that post-R trajectories share the same random stream. The original control raw is an existing observation, not a newly replayed control under this materialized file; do not imply that the v3 control XML retroactively changes its raw provenance. The contract's lifecycle, exposure, same-time/location/lane comparison, and pre-R trajectory checks remain essential.

## Mandatory measurement checks

Not applicable to this review: no measurement code, aggregation, detector interpretation, or run output was analyzed as a measurement result. I used prior output-review findings only to assess the motivation and scope of the input repair. No new measurement coverage or regression-test claim is made beyond the independent package report.

## Recommendation and boundary

It is scientifically reasonable to consider **separately preparing** a repaired PAIR3199 treatment using these hashes, because the principal input-level comparability defects are corrected and the exploratory question remains bounded. That is a recommendation to prepare a reviewable proposal only; it is not a run recommendation or authorization. A new exact card and fresh engineering, data/provenance, and scientific prelaunch reviews must verify that they bind these exact files and preserve the adopted contract. Any execution needs a new explicit user authorization because the prior one-start authorization is consumed.

No SUMO, TraCI, or netconvert was run. No project decision, threshold, witness contract, demand value, geometry, classifier, or formal protocol was changed.

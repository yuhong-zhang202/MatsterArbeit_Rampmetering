# Independent scientific review — PAIR3199 matched-input repair v4

**Disposition: PASS for offline matched-input construction and its stated limited purpose.**  
**Findings:** Blocker 0 / Major 0 / required Minor 0; one Observation.  
**Confidence:** High for the static input contrast and whitelist behavior; Moderate for the historical stochastic root-cause attribution and future trajectory interpretation.  
**Authorization:** None. This report does not authorize a card or a simulation start.

## Context preflight and review question

Reviewed `AGENTS.md`, `docs/PROJECT_STATE.md`, `docs/DECISIONS.md`, `docs/EXPERIMENT_PROTOCOL.md`, `docs/WORKLOG.md`, the adopted `docs/methodology/STAGE6_EXPLORATORY_RAMP_INDUCED_WITNESS_CONTRACT.md`, the previous treatment lifecycle/data and scientific post-run reviews, and the v4 repair report, XML inputs, invariant report, common-demand manifest, provenance receipt, checker, and tests.

Current status is that the single PAIR3199 treatment authorization is consumed and the prior pair result remains `NOT_EVALUABLE`; the formal experiment protocol is unchanged and unfrozen. D-005 adopts the exploratory witness contract for this pair only. V4 is the current offline input package; v2 and v3 are superseded histories and are not accepted as evidence of v4 checker completeness. The review question is whether v4's static inputs and checker provide a defensible M/U/X-matched, R-only planned-input contrast, and whether separate future card preparation is scientifically reasonable. The old treatment is not re-adjudicated here.

## Findings

### Blocker / Major / required Minor

None for the bounded v4 input-construction objective.

### Observation — exact input match is not trajectory or replay equivalence

The v4 report and invariant receipt record M/U/X counts of 1,333/150/75 in both arms; 1,558 common identities and complete records; matching integer-millisecond desired departures, routes, types and recorded-precision speedFactors; four identical route definitions and one identical vType definition; and exactly 192 treatment-only R identities. The manifest identifies treatment R departures at 5-second intervals from 540 through 1,495 seconds. This is an appropriate planned-input contrast for the adopted exploratory question. The exact common vehicle attribute and definition whitelist is materially stronger than relying on equal seeds.

The checker implementation rejects any unapproved top-level node, any nested element under a route/vType/vehicle, any unlisted or missing node attribute, mixed content, duplicate IDs/definitions, and DTD/entity declarations. The visible v4 test suite includes the formerly bypassed treatment-only `<flow>` and nested vehicle `<param>` cases, plus unsupported vehicle attributes and common-record/definition mutations; the report records 9/9 passing tests. This assessment relies on v4 code/tests and its hashes, not on v3's prior 6/6 report.

One scope limitation remains: the checker proves arm-to-arm equality for route/vType definition maps; the package provenance receipt and any future exact card must continue binding the approved v4 bytes so a simultaneous edit to both arms is not mistaken for preservation of the accepted scenario. This is not a defect in the hash-bound v4 package, but a boundary on treating the pairwise checker alone as proof that all shared inputs remain unchanged.

Static input matching cannot prove future insertion/lifecycle success, bitwise identity of unrecorded floating-point values, or matching traffic trajectories. It also cannot establish that future pre-R trajectories will match the existing control raw. The original control raw remains an observation generated from its original inputs; v4 does not retroactively replace that provenance. The adopted contract's lifecycle, actual R exposure, pre-R trajectory and time/location/lane matched checks remain necessary after any separately authorized run.

**Smallest action:** Any future exact card should bind the v4 control and treatment input hashes, accepted network/configuration hashes and this contract hash, then retain post-run lifecycle and pre-R checks. Do not describe checker PASS as trajectory equivalence. Fresh execution authorization remains necessary.

## Root-cause assessment

- **U/X omission — supported, High confidence.** The prior treatment review records SUMO log messages that it ignored U and X flows because the old route source was not departure-sorted; the control realized both flows. V4 materializes explicit, globally departure-sorted vehicle records and the static pair contains U=150/X=75 in both arms. This supports source ordering as the immediate omission mechanism.
- **M speedFactor mismatch — lack of per-identity materialization is supported; exact RNG-order explanation is unproven.** The prior comparison found only 2/1,333 exact M speedFactor matches, including pre-540-second vehicles; the old common vType did not pin an individual factor to each identity. Equal seeds did not ensure identity-level equality. The inserted delayed-R flow is consistent with a changed shared random draw/construction order, but the reviewed evidence does not isolate that mechanism. V4 instead assigns the same recorded-precision factor to each common M/U/X identity from immutable control `vehroute.xml`; this repairs prospective input matching without proving the exact historical cause.

The use of `vehroute.xml` rather than two-decimal `tripinfo.xml` avoids the known serialization-rounding trap. “Exact” equality is at the precision stored in the source records; unrecorded internal floating-point bits are not claimed.

## Measurement checks

Not applicable: this is a static input-construction review. It does not evaluate measurement targets, detector coverage, sample reconciliation, computed outcomes, or analysis-code regression behavior. I cite prior output reviews only to assess why matching is needed; no previous outcome is reclassified.

## Recommendation and boundary

It is scientifically reasonable to separately prepare a reviewable repaired PAIR3199 treatment proposal using the hash-bound v4 inputs. This is preparation only. It must preserve the adopted exploratory contract and the control's historical `NOT_EVALUABLE`/warning status. Fresh engineering, data/provenance and scientific prelaunch reviews must inspect the exact future card and its input bindings. The consumed D-006 authorization cannot be reused; a future launch requires new explicit user authorization.

No SUMO, TraCI, or netconvert was run. No demand, qMain/R value, geometry, classifier, threshold, witness contract, formal protocol, or historical treatment disposition was changed.

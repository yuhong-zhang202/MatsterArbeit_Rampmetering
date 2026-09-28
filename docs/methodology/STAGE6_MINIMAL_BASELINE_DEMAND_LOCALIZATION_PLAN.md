# Stage 6 Minimal Baseline Demand Localization Design

Date: 2026-09-21

Status: **EXPLORATORY DESIGN PROPOSAL / NOT AUTHORIZED FOR EXECUTION**

Scope: locate, with a bounded number of new open-condition runs, the first demand neighborhood in which the accepted geometry produces a P-defined State 1 without invalid demand realization or urban-side overload. This is not a formal experiment, a controller comparison, a formal breakdown definition, or a thesis-baseline selection.

## 1. Executive decision

Use a **qMain-only, fixed-qRamp sequential ladder**. Keep `qRamp=720`, `qUrban=360`, `qX=180`, A_OPEN, geometry, vehicle behavior, signal programs, observation windows and the locked P/S/L/Candidate A/Candidate C classifier unchanged. Test at most three new demand points with seed17, one at a time:

1. nominal qMain 3350 veh/h (`M number=1396`, exact scheduled rate 3350.4 veh/h);
2. nominal qMain 3500 veh/h (`M number=1458`, exact scheduled rate 3499.2 veh/h);
3. nominal qMain 3650 veh/h (`M number=1521`, exact scheduled rate 3650.4 veh/h).

Stop the ladder at the first seed17 point that is P-positive **and** passes all baseline-suitability gates. Run seed23 only at that point. A seed17-only success is `BASELINE_CANDIDATE_PENDING_REPLICATION`; `SUITABLE_BASELINE_FOUND` requires the same demand point to pass with seed23. If an overload, demand-realization failure, invalid measurement or hard cap occurs, stop rather than increasing demand until a positive result appears.

`MAX_NEW_DEMAND_POINTS=3`. `MAX_NEW_SUMO_STARTS=4`, including every failed start. `MAX_TECHNICAL_RETRIES=0`: a technical failure stops this card and requires a new decision rather than consuming localization budget through repair attempts. There is no qRamp branch in this design.

Confidence: **Moderate** for this being the smallest interpretable next design; **High** that it respects the current classifier and evidence boundaries; **Unknown** whether any proposed point will be suitable or P-positive.

## 2. Context and recovered exact A baseline

The accepted A run is `TV_A_S17_attempt1`. Its bound network is:

- `artifacts/stage6_targeted_validation_20260920_v1/engineering/build_attempts/TV_BUILD01/network.net.xml`
- SHA-256 `887c232483f0c68dc024334ff5997250d7d36299ab2744bdcf49d5a314c700ca`

The exact A route input uses `number` flows over `[0,1500)` s:

|Class|Number|Exact scheduled rate|Route role|
|---|---:|---:|---|
|M|1333|3199.2 veh/h|freeway mainline through traffic|
|R|300|720.0 veh/h|urban-to-ramp traffic|
|U|150|360.0 veh/h|unrelated urban through traffic|
|X|75|180.0 veh/h|technical cross traffic|

The project label `qMain=3200` is nominal; the integer-number realization is exactly 3199.2 veh/h. The run uses seed17, `[0,2700)` s, 1 s steps, and A_OPEN (`60G`). There is no warm-up: demand begins at 0 s. Existing A accounting reports all planned classes inserted by 1500 s and no unfinished vehicles at 2700 s.

Binding anchors:

|Source|SHA-256|
|---|---|
|A demand route|`70d90d477c97141086b87cd248064c2c27c5965060e04fe9a2cbec67ec20e1cd`|
|A SUMO configuration|`793d6ecd387f5ed958eb9aff0f13f1628f64bf1422d28c5400db0ddc34ff3c7c`|
|A additional/detector file|`4198c04ce39bdfb5b91d965f2ec2ca9c7de42777415d77f68e87d4b239a22c2b`|
|Locked protectable-state method|`22fe22170c17ce74e261e717586a458a1b5173e9deabbee925bd4c1d606adfe7`|

A/open seed17 is P-negative, with two L numerical candidates and Candidate C warnings. The strongest L evidence is not a one-gate near miss: magnitude, slow-population and persistence all remain limiting. This motivates a small demand increase but supplies no calibrated demand-response function.

## 3. Why qMain only

### Chosen option: Option 1

Hold qRamp fixed and increase qMain first.

- It isolates the proposed mechanism most directly: whether additional freeway-mainline loading turns the existing short merge disturbances into a persistent collective M state.
- Increasing qRamp first would simultaneously increase merge disturbance, ramp storage pressure and the probability of R/U interference. A P-positive result would then be harder to separate from a baseline that has already consumed its urban-side headroom.
- A useful future metering comparison requires a mainline problem that can plausibly be protected while retaining room for metering to move R waiting between freeway and ramp. Keeping qRamp at 720 preserves the currently observed merge interaction without deliberately increasing the very queue pressure that later control must manage.
- Robert supported a qMain × qRamp scan around breakdown, but did not require a full grid or specify its resolution. A bounded first-axis localization is consistent with that guidance and does not claim supervisor approval of these points.

### Why no two-dimensional confirmation now

A qRamp change would answer a different question and would add a second cause of both mainline and urban changes. If qMain-only localization fails within this budget, a later decision may consider a small two-dimensional design; it is not an automatic branch here. This protects against result-chasing and prevents a baseline search from becoming a wide grid.

## 4. Demand-ladder provenance

The proposed nominal increment is 150 veh/h, 4.6875% of the nominal 3200 baseline. Because the accepted input uses integer `number` over 1500 s, exact scheduled rates differ by at most 0.8 veh/h from the labels:

|Point|Nominal qMain|M number|Exact qMain|Increment from prior exact point|Exact total M+R scheduled rate|
|---|---:|---:|---:|---:|---:|
|A0 archived|3200|1333|3199.2|—|3919.2|
|L1|3350|1396|3350.4|151.2|4070.4|
|L2|3500|1458|3499.2|148.8|4219.2|
|L3|3650|1521|3650.4|151.2|4370.4|

This is a **PROJECT OPERATIONALIZATION**, not a literature-derived spacing or a capacity estimate. The increment is large enough to change the 25 min population by 62–63 M vehicles per step, but small enough to avoid the prior coarse 3200→3800 jump. Historical old-geometry results at nominal 3500 and 3650 show that increasing qMain can quickly reduce R access before the old impairment signature appears. Those results are not current-geometry evidence; they justify the upper cap and strict realization/overload checks only. No point is selected from the locked P threshold algebra or fitted to make P positive.

## 5. Phases and sequential state machine

### Phase 0 — frozen-input verification

No simulator call. Verify the network, A_OPEN signal program, route/type semantics, Krauß/default behavior, lane-changing inputs, detector/output roles, demand and horizon against the source hashes. Verify the locked method hash. Materialize each future run in a new exclusive directory and bind every input/output path. Any unplanned scientific difference is `PRELAUNCH_FAIL`.

### Phase 1 — seed17 localization

1. Launch L1 only after an exact materialized launch card is separately approved.
2. Audit raw completeness, class accounting, demand realization, overload and attribution; apply the locked classifier offline.
3. If L1 is a suitable P-positive candidate, stop increasing demand and proceed to Phase 2 at L1.
4. If and only if L1 returns complete `NO_QUALIFYING_EVENT` and every release gate is clear, launch L2. Apply the same decision logic.
5. If and only if L2 returns complete `NO_QUALIFYING_EVENT` and every release gate is clear, launch L3. Apply the same decision logic.
6. Do not launch a higher point after `DEMAND_REALIZATION_FAIL`, `OVERLOADED_NOT_SUITABLE_BASELINE`, `NOT_EVALUABLE`, an unresolved technical failure, or exhaustion of the start cap.

Only a complete `NO_QUALIFYING_EVENT` with all realization, measurement, attribution-context and overload checks otherwise clear may release the next higher point. `ONSET_REFERENCE_UNRESOLVED`, `CANDIDATE_ATTRIBUTION_UNRESOLVED` and `NOT_EVALUABLE` are scientifically distinct non-acceptance states and stop the ladder as borderline/unresolved; they are not collapsed into “ordinary P-negative.” Only `STATE1_EXPLORATORY_RULE_POSITIVE` can enter the baseline gate.

### Phase 2 — one independent-seed confirmation

Use seed23 only at the **earliest** seed17 point passing the complete candidate gate. Do not run seed23 at lower negative points or every ladder point. Seed23 checks repeatability of the P-defined state and suitability at the candidate demand; it does not estimate breakdown probability.

The missing accepted-geometry qMain≈3200 seed23 run means this design does not create a two-seed matched demand-response contrast from A0. It deliberately spends the one confirmation start at the decision-relevant candidate. Formal inference would need a separately approved replication design later.

### Phase 3 — closeout labels

- `SUITABLE_BASELINE_FOUND`: the same demand passes the complete gate under seed17 and seed23.
- `BORDERLINE_ONLY`: a seed17 candidate fails seed23, or only L/Candidate C/unresolved evidence is found within the budget.
- `OVERLOADED_ONLY`: P-positive evidence occurs only in a run rejected by the overload gate.
- `NO_BASELINE_WITHIN_BUDGET`: the released ladder is completed through L3, every evaluated point is valid and non-overloaded, and all three return complete `NO_QUALIFYING_EVENT`.
- `LOCALIZATION_NOT_EVALUABLE`: technical, completeness or demand-realization failure prevents the planned scientific decision and cannot be repaired within the same hard cap.

Specific terminal labels take precedence over the generic budget outcome: any unresolved/ambiguous case is `BORDERLINE_ONLY` or `LOCALIZATION_NOT_EVALUABLE`, any overload-only positive evidence is `OVERLOADED_ONLY`, and a technical/completeness/realization failure is `LOCALIZATION_NOT_EVALUABLE`. Hard-cap exhaustion alone never converts one of those states into `NO_BASELINE_WITHIN_BUDGET`. These labels do not select a formal thesis baseline.

## 6. BASELINE_CANDIDATE_GATE

P-positive is **necessary but not sufficient** because this task explicitly localizes a P-defined State 1 neighborhood. Accepting L or Candidate C instead would silently change the target. For seed17, all required items yield `BASELINE_CANDIDATE_PENDING_REPLICATION`; the same gate under seed23 yields `SUITABLE_BASELINE_FOUND`.

### Required

1. Locked P output is `STATE1_EXPLORATORY_RULE_POSITIVE` in A_OPEN.
2. At least one P episode passes every locked numerical and attribution gate; no material source, downstream-tailback, direct TLS, geometry or unrelated-bottleneck cause remains unresolved for that accepted event.
3. Raw XML, time grid, identities, manifest hashes and required output roles pass completeness/integrity checks.
4. `DEMAND_REALIZATION_PASS` is obtained under section 7.
5. Mainline exposure is sufficient: all scheduled M enter within demand time, candidate/reference bins are valid, the event is observed in the merge core with downstream receiving context, and the state is not manufactured by source starvation.
6. No `OVERLOADED_NOT_SUITABLE_BASELINE` condition in section 8 is present.
7. No collision, teleport, emergency-braking anomaly, unplanned TLS program or geometry mismatch materially dominates the event.

### Robustness/supporting only

- S-positive strengthens specificity but is not required.
- L, Candidate A, Candidate C, state duration, recovery and upstream propagation describe robustness/structure; none replaces P.
- Candidate A spatial corroboration is strong support, not a mandatory gate because pinned localized congestion need not extend to a second cell.
- A possible capacity drop or congested discharge is supporting State 2 evidence, not required for baseline acceptance.

## 7. DEMAND_REALIZATION_GATE

For each M/R/U/X class report: scheduled IDs/count; actual insertion time; inserted in `[0,1500)`; inserted after 1500; never inserted; arrival count/time; unfinished at 2700; last known location; and depart-delay distribution. Reconcile route, vehroute, tripinfo and FCD identities.

`DEMAND_REALIZATION_PASS` requires:

- exact planned identity/count agreement;
- every scheduled M, R, U and X vehicle inserted within `[0,1500)`;
- zero inserted-after-1500 and zero never-inserted identities;
- zero unknown/duplicate identities and complete class accounting;
- all M completed by 2700, so mainline results are not dominated by terminal censoring.

`M_SOURCE_CONTEXT_PASS` is a separate event-attribution check. Reconstruct each M vehicle's requested departure as `actual_depart - departDelay`, retain exact identities, and compare requested versus actual insertion in the already locked 30 s bins. The rule is categorical, not a fitted delay threshold:

- to release a higher point after `NO_QUALIFYING_EVENT`, the requested-ID and actual-inserted-ID sets must match within every demand-time bin used by the P evaluation;
- to accept a P-positive candidate, they must match within every reference and candidate bin of the accepted episode;
- a positive delay wholly inside the same 30 s bin is reported as a warning but does not by itself fail this check;
- any delayed identity crossing into or out of a decision-relevant 30 s bin yields `M_SOURCE_CONTEXT_UNRESOLVED`.

For a P-positive point, `M_SOURCE_CONTEXT_UNRESOLVED` closes the ladder as `BORDERLINE_ONLY`; for a P-negative point it closes as `LOCALIZATION_NOT_EVALUABLE`. It can never release the next qMain. A cross-bin shift outside all accepted-event bins is retained as a warning for a P-positive candidate, but must still be shown in the source-entry ledger. This uses the locked time grid and exact identities and adds no new numerical cutoff.

Any violation of the five `DEMAND_REALIZATION_PASS` bullet requirements above is `DEMAND_REALIZATION_FAIL`, retained as an observed result rather than silently excluded. This sentence does not collapse `M_SOURCE_CONTEXT_UNRESOLVED` into demand-realization failure. The zero-tolerance demand-window rule is a conservative **exploratory project convention**, motivated by the need to isolate scheduled qMain and by the accepted A realization. It is not a supervisor-approved formal threshold. Departure-delay distributions remain reported; no post-hoc delay cutoff is introduced.

R/U unfinished-at-2700 and late insertion additionally enter the overload gate. X completion is reported; an X terminal exception is a measurement/technical review item and cannot be silently ignored.

## 8. OVERLOAD_REJECTION_GATE

A P-positive run is `OVERLOADED_NOT_SUITABLE_BASELINE` if any predeclared hard condition holds:

1. any R or U vehicle is inserted after 1500, never inserted, or unfinished at 2700;
2. the locked/registered strict `storage_cross` indicator is positive;
3. a registered direct R-to-U obstruction record identifies the R blocker, U victim, time and location, and that same U victim has positive insertion delay whose delay interval overlaps the obstruction interval or is unfinished at 2700 (`OVERLOAD_LINKED_URBAN_HARM`);
4. the network develops persistent system-wide gridlock, or M downstream supply collapses because vehicles cannot enter rather than because an attributable merge state forms;
5. collisions, teleports, emergency behavior, direct TLS restriction, geometry error, downstream tailback or another artifact materially dominates the P classification;
6. the P episode lacks interpretable upstream supply or downstream receiving-space evidence.

The following are diagnostic warnings, not automatic rejection by an invented magnitude threshold: nonzero R storage queue, increased U travel/system time, positive U insertion delay without the exact same-identity/time link in hard condition 3, and stopped R occupation in shared/internal sections without registered `storage_cross` or a direct linked U victim. They must be reported against A0. No approved numerical “severe U delay,” “persistent reservoir,” “co-occurrence,” or ramp-queue materiality threshold exists, so this design does not create one post hoc. If the registered evidence cannot establish the categorical link required by hard condition 3, classify the point `BORDERLINE_ONLY` after P-positive or `LOCALIZATION_NOT_EVALUABLE` after P-negative; do not accept it, reject it as overloaded by discretion, or release a higher demand point.

This gate deliberately risks false negatives: a mildly urban-affected but scientifically usable point may be rejected or left ambiguous. That is safer than accepting a baseline whose urban side is already exhausted before metering.

## 9. Required outputs for every new point

### Mainline suitability

- locked P/S/L, Candidate A and Candidate C outputs with all event tables and uncertainty flags;
- M travel time, system time, timeLoss and class-specific completion/censoring;
- M-only downstream unique count;
- 1 s and 30 s merge-local M speed, model-reference ratio, slow fraction, simultaneous slow population and M density;
- native E1 lane/station speed, flow and occupancy with contribution conventions preserved;
- P-state location, duration, recovery and attribution ledger;
- supporting discharge/capacity-drop evidence only if separately computable without inventing a threshold.

### Ramp/urban safety

- ramp-storage queue/occupancy and anchored queue extent/count;
- R storage/internal/shared moving and stopped occupation;
- U travel time, restricted system time, timeLoss, waiting and insertion delay;
- scheduled/inserted/arrived/unfinished R/U accounting;
- `storage_cross` and local R-to-U obstruction events;
- TLS context and last-position tables for every unfinished identity.

These are exploratory baseline diagnostics, not thesis results.

## 10. Proposed localization matrix

The machine-readable matrix is `docs/methodology/STAGE6_MINIMAL_BASELINE_DEMAND_LOCALIZATION_MATRIX.csv`. All confirmation rows are mutually exclusive; at most one seed23 row may run.

|Order|Point|Exact qMain|qRamp|Seed|Launch condition|Primary decision|
|---:|---|---:|---:|---:|---|---|
|0|A0 archived|3199.2|720|17|already completed|negative anchor; no new start|
|1|L1-M3350|3350.4|720|17|Phase 0 PASS + exact-card approval|accept candidate, stop, or release L2|
|2|L1-M3500|3499.2|720|17|prior point = complete `NO_QUALIFYING_EVENT`; every release gate clear|accept candidate, stop, or release L3|
|3|L1-M3650|3650.4|720|17|prior point = complete `NO_QUALIFYING_EVENT`; every release gate clear|accept candidate or close search|
|conditional|L2-confirm|same as earliest candidate|720|23|seed17 complete candidate gate|confirm or classify borderline|

No row is authorized by this document.

## 11. Early-stop rules

### EARLY_STOP_SUCCESS

Stop increasing qMain immediately when the earliest seed17 point passes the complete candidate gate. Release only its seed23 confirmation. If seed23 also passes, close `SUITABLE_BASELINE_FOUND`; do not run higher points.

### EARLY_STOP_FAILURE

Stop without further demand increase when:

- a point is overloaded;
- demand realization or required measurement fails;
- a material artifact is identified or remains unresolved for all candidate episodes;
- the start cap is exhausted;
- L3 is P-negative;
- a technical failure cannot be repaired inside the same fixed cap.

Negative and ambiguous closeout is scientifically acceptable. There is no instruction to keep increasing demand until P becomes positive.

## 12. Resource budget

Historical accepted runs used:

|Run|Wall time|Output bytes|
|---|---:|---:|
|A/open|1.144 s|25,522,462|
|B/moderate|1.252 s|28,368,278|
|C/strong|2.139 s|59,984,655|

B/C are not qMain-only predictors. For planning, use a conservative expected allowance of **3 s and 75 MB per new run**.

- **Preferred budget:** 3 starts (two seed17 localization points plus one confirmation, or all three seed17 points with no candidate); approximately ≤9 s and ≤225 MB expected output.
- **Hard scientific ceiling:** 4 starts; approximately ≤12 s and ≤300 MB expected output.
- **Operational fail-stop ceiling for a future card:** 180 monitored s and 1.5 GB per attempt, therefore 720 s and 6 GB aggregate. These are safety ceilings, not expected use and not authorization.
- No technical retry is available in this draft. Any failed start counts against the four-start ceiling and stops the card for a new review/decision.

## 13. Capacity-drop boundary

Baseline localization requires sustained P-defined mainline impairment, not a measured capacity drop. A discharge/capacity-drop candidate is supporting evidence about severity/mechanism. Absence of a clear capacity drop does not reject an otherwise suitable baseline. Whether the later thesis efficiency mechanism must include capacity drop remains a future user/supervisor decision.

## 14. Historical archive and supervisor alignment

The current manifested archive contains no additional established same-geometry, full-horizon A/open baseline. Old Stage 3/4 runs may inform the small step and upper cap, but their geometry, source placement and impairment rule differ; they cannot satisfy any acceptance gate here.

The design aligns with Robert's explicit working guidance by retaining a simple synthetic scenario, scanning uncontrolled demand near breakdown, leaving Krauß/default behavior untouched, validating actual insertion, and inspecting plausible breakdown/capacity-drop evidence. Robert did not approve these qMain points, this seed allocation, P, the overload gate, or the run budget. Those remain proposed.

## 15. Draft launch-card boundary

The non-executable draft is `docs/methodology/STAGE6_MINIMAL_BASELINE_DEMAND_LOCALIZATION_LAUNCH_CARD_DRAFT.json`. It binds the scientific values and source anchors but intentionally has no materialized future input/output hashes. Before any execution, a separate preparation step must:

1. create exclusive run directories and deterministic route/config/additional/output-role files;
2. prove that only M `number`, seed and path fields vary as registered;
3. bind all bytes, executable/version, method/analyzer version and resource counters;
4. pass engineering, data and scientific prelaunch review;
5. produce a final exact-card SHA-256;
6. obtain explicit user approval citing that exact final card.

This proposal and its draft card do **not** authorize SUMO, netconvert, TraCI, GUI, input materialization, demand execution or analysis production.

## 16. Limitations and future confirmations

- P is an exploratory operational screen, not formal physical breakdown proof.
- A P-negative point may contain moving, intermittent or lane-specific congestion missed by the rule.
- A P-positive point identifies a plausible protection opportunity, not metering benefit.
- Two seeds provide only a minimal reproducibility check, not probability estimation.
- The accepted-geometry A0 lacks seed23, so this plan does not produce a two-seed matched demand-response curve.
- Exact urban-overload magnitude thresholds are not approved; this design uses conservative categorical rejection and ambiguity rather than inventing a delay cutoff.
- The formal persistence/reference validation, eventual baseline selection, capacity-drop role and formal replication design remain for later user/supervisor confirmation.

## 17. Execution status

**还不能运行，等待用户批准 exact launch card。** `docs/EXPERIMENT_PROTOCOL.md` remains unchanged and empty. O2 remains `NOT_RESOLVED`; Stage 6 remains `PARTIAL`.

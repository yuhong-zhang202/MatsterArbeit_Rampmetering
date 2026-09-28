# Independent Mainline Reference-State Method Proposal

Date: 2026-09-22. Status: **PROPOSED REFERENCE-STATE EXTENSION; NOT APPROVED FOR CLASSIFIER INTEGRATION OR FORMAL USE.**

This is a method and archived-data capability assessment, not an application. No simulation, reclassification, demand-point selection or scientific-input change is authorized by this document. The companion `MAINLINE_REFERENCE_SELECTION_SPEC.md` specifies a future offline diagnostic implementation.

## 1. Executive conclusion

**An independent reference can contextualize an observed state, but cannot reconstruct an unobserved transition.** Recommend R5, a deliberately separated hybrid: retain R1 unchanged for local transition and density-rise evidence; use a deterministic R2/R4 same-run reference bank for supplementary mobility context, with a screened R3/R4 A0 bank as fallback. Neither bank replaces the existing local density comparator or creates a P-positive result.

Literature sufficiency: **PARTIALLY**. It supports separation of free/congested states, transitions, concentration, spatial evidence and downstream influence. It does not validate this network's normal-speed cutoff, stable-period duration, critical density or reference distribution. Existing 0.85 is a project convention, not measured free-flow ground truth. The proposed bank must therefore be called a **screened high-mobility reference**, not a validated normal-state distribution.

The current failure is principally an observed preceding state failing the locked reference-speed screen, not absent data. It does not establish that traffic was congested from the beginning. Confidence: **High** for the code/table distinctions below; **Moderate** for the proposed design; **Unknown** for its classification accuracy, availability of eligible bank windows and physical interpretation of 3350.

## 2. Research problem

Separate three questions: (i) what mobility and concentration were observed; (ii) whether a local normal-to-impaired transition was observed; (iii) whether there is an attributable, persistent condition worth protecting. A reference bank helps (i); chronological local evidence is needed for (ii); neither alone answers (iii). Comparing a higher-demand run with a lower-demand run is not a counterfactual estimate of congestion or control benefit.

The required project context was inspected, including the locked method/review, localization plan, archived application, A failure decomposition, 3350 classifier and revision03 diagnostic. The formal protocol exists but is empty. PROJECT_STATE contains recent execution/diagnostic records absent from the latest WORKLOG entry; this task does not retrospectively invent those missing approvals or logs.

## 3. Literature support

Page locators are one-based PDF pages of the repository copies, not necessarily printed pages. Claims below are paraphrases; none of these sources prescribes this proposal's bank-selection algorithm.

|Source|Relevant evidence and limitation|
|---|---|
|Treiber & Kesting, `literature/core_reading/Traffic Flow Dynamics.pdf`|Chapter 18, PDF 360: high load, bottlenecks and disturbances jointly motivate breakdown; floating-car observations can support recognition when sufficiently frequent. Chapter 17, PDF 351 distinguishes stable congested patterns with minimal/zero capacity drop. State and spatial evolution matter; isolated speed minima and a universal capacity-drop requirement are unjustified. Chapters 3/4 distinguish measured aggregates from equilibrium concepts; a speed limit is not observed free flow. These concepts support multivariate references, not a universal 0.85 or 90 s criterion.|
|Brilon, Geistefeldt & Regler, `literature/core_reading/RELIABILITY OF FREEWAY TRAFFIC FLOW.pdf`|PDF 5 separates fluent-before-breakdown, already congested, and downstream-tailback intervals. PDF 6 identifies speed/flow sequences and permits more detailed/site-dependent criteria. German 70 km/h is not transferable; PDF 5 calls five minutes a measurement compromise, not a universal state duration. Already congested observations do not supply a missing breakdown transition. Its statistical capacity censoring is not automatically the same as missing onset observation here.|
|Cassidy & Bertini, `literature/core_reading/Some trac features at freeway bottlenecks.pdf`|PDF 4 uses conserved cumulative counts, ramp correction and free-flow travel-time shifts to expose excess accumulation; pre-queue and queued conditions have different interpretations. PDF 12–13 addresses downstream tailback. This motivates conservation/spatial corroboration, not a ready-made automatic donor rule. Neither a speed-only reference nor mixed detector counts establish queue formation.|
|Papageorgiou & Kotsialos, `literature/core_reading/Freeway_ramp_metering_an_overview.pdf`|PDF 4 defines critical occupancy at maximum flow and says ALINEA's desired occupancy is typically, not necessarily, that value; targets can change. Therefore a control set-point is neither an independent normal-state label nor proof of breakdown. High-throughput normal operation need not have very low density.|
|Riehl et al., `literature/sumoITScontrol.pdf`, repository preprint|PDF 4–5 separates measured quantities and desired occupancy feedback; PDF 17–20 discusses geometry/sensing implementation. Detector location and lane assignment constrain interpretation. Its controller example cannot calibrate this network's free state. Preserve its preprint status; no final publication/DOI is inferred.|

**The literature does not support directly freezing numerical reference thresholds.** Normalization, sampling unit, eligibility and exclusions require project operationalization and later validation. Capacity drop remains supporting post-breakdown evidence, not a reference or baseline necessity.

## 4. Existing method limitation and audit corrections

Authoritative implementation: `artifacts/stage6_baseline_localization_20260921_v1/LOC_M3350_S17/engineering/analysis/apply_rule.py`, SHA-256 `00ab445634523d74b8fb55f3ee15d765c5879636884af9bc3ccd9488e91e66e1`. Locked method SHA-256 `22fe22170c17ce74e261e717586a458a1b5173e9deabbee925bd4c1d606adfe7`.

For the first bin of a maximal low-state run, R1 uses exactly the three immediately preceding 30 s bins in the same 100 m cell. Each must be valid and have mean model-reference speed ratio at least 0.85; reference M density is their positive median. Validity includes a complete time grid and at least two unique M vehicles per bin. Ratio is `speed / (compiled lane speed limit * archived vehroute speedFactor)`. This is not measured free-flow speed. There is no backward search or onset relocation. The low-state magnitude/population/persistence gates remain separately necessary. Density must exceed the local reference as specified by the locked profile.

The 0.85 screen separates the conventionally higher-mobility reference from low-state profiles; it was not calibrated as the true free/congested boundary. A value below it may reflect loaded free flow, perturbations, normalization mismatch or actual impairment. The screen alone cannot distinguish these explanations.

Existing 3350 `classifier_output/tables/candidate_events.csv` (SHA-256 `1ede09107dbdbc10ed3074ae8b155dbf057b39356e70604eb299f44c7baf8ba6`) contains 94 rows overall, of which 53 are P/L core rows:

|Profile|Duration-qualified, reference unresolved|Short, reference ineligible|Short, reference eligible|
|---|---:|---:|---:|
|P|1|6|1|
|L|20|22|3|

Thus **49 failed-reference rows are not 49 duration-qualified breakdown candidates**: 21 meet the relevant low-state duration and 28 are also short. Four more rows have eligible reference but insufficient duration. These are overlapping cell/profile records, not independent physical events. P's first low candidate at 420 s is short; its duration-qualified unresolved episode begins at 960 s. L first appears at 270 s. These times do not justify saying the run was congested from its start.

Distinguish: **unavailable past** (pre-run or missing labels); **insufficient population** (observed but too few vehicles); **observed reference rejected by speed screen** (not proof of congestion); and **eligible reference with short low state**. The last remains short regardless of donor availability. For failed reference, the implementation passes no reference density to its recovery helper, which then returns unresolved. Consequently unresolved recovery here is not independent evidence that speed never recovered.

### Supplemental-source quarantine

The independent read-only data audit found revision03 `diagnose.py` SHA-256 `2a8a5a66bf2d66d8f62213b7cf280006d52351667267eabfc8208de194825073` incompatible with the locked computation: lines 32–33 use `13.89 * speedFactor` instead of compiled through-lane 33.33 m/s; ratios are inflated by approximately 2.40065. Edge-local `pos` 1300–1800 selects principally the last approximately 98.38 m of `main_up`, not a physical 500 m cross-merge interval. Its simultaneous-slow count uses at least one rather than two vehicles; line 45 hardcodes P/L timeline flags False. Do not reuse these supplemental normalized metrics/timeline flags to select references, infer onset or establish recovery. Raw records and the locked analyzer are not implicated by these defects. The previous diagnostic/review remain historical records, not validation of these quantities. Repair is a separate scoped offline task; no old file is changed here.

The analyst also noted the existing S density boundary differs between method-table `>= 1.25` and implementation `> 1.25`. Preserve both sources, flag the discrepancy for separately authorized reconciliation, and do not use equality-edge cases to justify this extension.

## 5. Candidate reference strategies

**R1 — local preceding state.** Best direct chronological comparator: same cell, realization and nominal demand, with observed density change. Vulnerable to gradual deterioration, already-loaded references and unobserved past. Retain for transition inference; failure is information, not a defect to bypass.

**R2 — same-run stable-period bank.** Generate fixed, non-overlapping windows before inspecting target episodes, keep all eligible windows, and never rank by highest speed or lowest density. Per-lane exposure and concentration are required. Earlier windows may characterize an earlier condition but cannot prove an immediate transition across an intervening gap. Later windows are retrospective state context only and are excluded from the primary bank below. Valid recovery periods could inform a separately labelled future bank, but not this conservative first extension.

**R3 — cross-run lower-pressure bank.** A0 is a possible donor, not a free-flow label. Require matched geometry/behavior/open control/sensing, route mix definitions and qRamp/qUrban/qX; allow qMain to differ only for explicitly qualified mobility comparison. Do not import its lower density as the target's pre-event density. Same seed is neither vehicle matching nor independent replication.

**R4 — distribution/envelope.** Retain all screened observations, summarize medians/quantiles/ranges by cell and lane, with vehicle exposure and density/flow support. This avoids selecting one attractive window but does not make correlated observations independent. A descriptive range is not a confidence/prediction interval, calibrated anomaly threshold or critical-density curve. Multi-run future references need run-level weighting and held-out validation, not pooled vehicle-seconds treated as replicates.

**R5 — separated hybrid.** R1 answers local-transition eligibility; R2/R4, then R3/R4, supply a fixed descriptive benchmark. A fallback must not mean “choose the bank that produces a positive result.” Bank availability is decided before target comparisons; results from all eligible sources remain visible. Model-based normalization alone is a reproducible coordinate system, not a sixth empirical normal-state certificate.

## 6. Candidate comparison

|Strategy|Scientific strength|Bias / simplicity / current executability|
|---|---|---|
|R1|Observed local contrast|Simple and implemented; selective evaluability under loaded pre-state.|
|R2|Same-run empirical mobility|Moderate complexity; retrospective selection bias unless windows/masks fixed; computable, eligibility unknown.|
|R3|External benchmark independent of target window|Simple donor policy; demand/composition/seed confounding; computable, not ground truth.|
|R4|Shows heterogeneity rather than one chosen baseline|Requires explicit weighting; finite correlated single-seed archive is not a validated normal population.|
|R5|Keeps state context distinct from transition evidence|Recommended; modest bookkeeping, intentionally no automatic resolution of P.|

## 7. Recommended primary strategy

**PRIMARY: R5 with unchanged R1 plus an R2/R4 screened, pre-disturbance bank.** R1 remains the only source of the existing local density/reference gate. The independent bank is computed once per run/cell using fixed windows and a fixed exclusion mask, not per target episode. Pool both lanes only after each independently passes donor eligibility. Use all eligible windows equally at the bin level. It is independent of a particular target event, not statistically independent of the run or retrospectively unseen data.

This bank provides “observed high-mobility conditions under these exposures.” It does not certify low concentration relative to an unknown critical density. If a validated free-flow reference is required, the correct output remains `NORMAL_STATE_NOT_VALIDATED` until independent calibration exists. That limitation is preferable to inventing a critical-density threshold.

## 8. Recommended fallback

**SECONDARY: screened A0 R3/R4 bank**, fixed before future target analysis and never selected by its effect on 3350. Apply the identical donor algorithm to A0, whose L/C warnings preclude treating all time as normal. No target3350 observations may calibrate the A0 bank. If no eligible or support-compatible donor exists, return no comparable reference, not a looser screen. If both banks exist, report both; use the primary for contextual comparison and disclose disagreement without switching. Do not add further fallback tiers.

## 9. Reference selection spec and numerical provenance

The companion specification is normative for this proposal's future **diagnostic** implementation. It defines fixed windows, lane checks, exclusions, complete rejection logs, descriptive summaries, support flags and fixtures. It is not permission to run or modify the classifier.

|Number/convention|Provenance and role|
|---|---|
|1 s labels, 30 s bins, 100 m cells|Existing archived sampling/locked aggregation; unchanged.|
|0.85; three bins/90 s; at least two unique M|Inherited exploratory reference conventions, not literature-direct validity. Extension applies the population/speed checks separately to each through lane; this is a new proposed donor safeguard, not a P change.|
|Fixed 90 s windows anchored at 0; truncate incomplete final window|New literature-informed project operationalization for deterministic donor generation; not a discovered stable-state duration.|
|Median, 25th/75th percentiles, min/max|Descriptive reporting conventions, not decision thresholds or probability bounds.|
|0.70/0.60/0.80; 90/120/60 s and existing population/density gates|Locked P/S/L; never replaced, tuned or recalculated under new semantics here.|

No new critical density, occupancy, anomaly cutoff, recovery rule, significance level or warm-up duration is selected. No numbers are derived from 3350 minima.

## 10. Early-onset logic

Use orthogonal fields: `local_reference_status`, `independent_reference_status`, `transition_observation_status`, and unchanged historical classification. An observed preceding period that fails 0.85 is `LOCAL_REFERENCE_SCREEN_FAILED`, not “missing” or automatically “congested.” Its transition is `TRANSITION_NOT_IDENTIFIED`. Reserve `ONSET_LEFT_CENSORED` for an impairment already present at the earliest adequately populated observed interval, where no earlier usable state was observed; do not assign this simply because any later reference is rejected.

External context can describe low mobility when local reference is unavailable/rejected. It cannot assert when breakdown occurred, resolve source/merge attribution, establish the legacy density increase, or prove sustained State 1. A short episode stays short. Recovery speed and concentration can be described separately, but the locked joint recovery label stays unchanged if its comparator is unavailable.

## 11. Cross-run reference policy

**YES**, as a screened descriptive mobility benchmark; **NO**, as an automatic replacement for the locked local onset/density comparator. Require same compiled network, vehicle-type/behavior settings, open TLS programs, route definitions, sensing/step/horizon/demand-time profile, qRamp/qUrban/qX and measurement semantics. qMain may differ and must be declared. Seed need not match in a future registered bank, but seed identities and independence limits must remain explicit; this proposal's only named external donor is existing A0 seed17.

Use each vehicle's precise vehroute speedFactor and actual compiled lane speed; preserve absolute speed alongside normalized ratio. Keep per-lane type/length/speedFactor composition, lane shares, M/M+R density and realized passage exposure. No vehicle-ID matching across runs. Extrapolation outside donor exposure support is labelled, never repaired by reweighting/tolerance fitted to the target. A0-versus3350 differences alone remain demand-associated descriptions, not sufficient state classification.

## 12. Lane, population and density handling

|Dimension|Role|
|---|---|
|Normalized and absolute speed|REQUIRED mobility description; model normalization is not empirical free speed.|
|M exposure and precise identity/type joins|REQUIRED; an empty cell is not a normal cell. Minimum two IDs is observability, not representative sampling.|
|M and physical M+R spatial density|REQUIRED reference descriptor and transfer-support check. No lower-demand density substitution in the P gate. A validated low-concentration boundary is unavailable.|
|Lane-specific speeds, population and density|REQUIRED; pooled mobility cannot conceal a lane failing the donor screen. Auxiliary lane excluded from M through reference.|
|E1 occupancy and flow|SUPPORTING; native loop samples differ from spatial FCD, downstream loops mix M/R. No occupancy target ground truth.|
|Unique M passage, downstream state, accumulation, recovery, composition|DIAGNOSTIC/contextual safeguards; availability flags do not fabricate attribution.|

Physical x, not edge-local pos, defines cells. Include mapped internal through lanes and actual lane-kilometres. Density is counted spatially, not calculated from mismatched q/v. Low density alone cannot certify normal operation, while high-density fluent operation is not automatically congested.

## 13. Circularity and post-hoc safeguards

Publish this specification and hash-bound input whitelist before application. This is a retrospective proposal informed by known reference failures, not a claim of prospective preregistration or independent validation. Keep every window/rejection, all cells, both banks, and all unchanged historical results. No fastest-window ranking, backward search, manual exclusions, target-fitted tolerances, B/C outcomes, urban harm or ALINEA target enters donor eligibility. No event receives a separately optimized donor. Revisions require new version/review and side-by-side reporting, including negative/no-reference outcomes.

## 14. A0/3350 data capability

Read-only data_analyst checked both raw FCD/vehroute/tripinfo and an E1 example against manifests: matching hashes, exact 2700 labels 0–2699, precise speedFactor joins available. This is not a new exhaustive audit of every raw file.

|Use|Field capability|Scientific availability|
|---|---|---|
|R1 reproduction|AVAILABLE|Reference may fail; existing result retained.|
|R2 deterministic donor bank|AVAILABLE|PARTIALLY_AVAILABLE: eligible windows and representativeness untested.|
|R3 A0 donor bank|AVAILABLE|PARTIALLY_AVAILABLE: comparable screened windows/support untested; A0 not ground truth.|
|R4 empirical summaries|AVAILABLE|Validated multi-run normal envelope NOT_AVAILABLE.|

Inputs: FCD time/id/x/y/lane/pos/speed; vehroute route/type/speedFactor; compiled lane geometry/limit; tripinfo departures/delays/arrivals/duration/timeLoss; E1 native 30 s counts/speed/occupancy; original classifier outputs, config and manifests. Missing: independently validated normal-state labels, critical density, held-out seed validation and donor-support results. E1 lacks vehicle IDs; use trajectories for M-only metrics. Required processing: validated joins, physical-cell and lane aggregation, fixed-window screening/masks, density/exposure support, complete audit tables and fixtures. Do not reuse revision03 supplemental calculations.

**No new SUMO run is required to implement and audit the proposed descriptive reference selection on existing A0/3350 raw data.** Data sufficiency does not guarantee a donor or permit State 1 reclassification. Future revised-classifier application would need separately approved semantics, new offline outputs and independent review; missing observed history cannot be generated offline.

## 15. Future simulation-design implications

Option A, low-demand pre-period then target demand, can supply an observed earlier high-mobility state but changes history, total vehicles and the estimand toward a demand-step transition experiment. It does not guarantee free flow or eliminate signal phase/queue initialization confounding. It requires a separate design, fixed switch rule, demand-realization checks and matched control histories; no duration or demand value is selected here.

Option B, longer observation at unchanged constant demand, cannot guarantee a normal preceding state and may merely lengthen an already-loaded episode. Removing an arbitrary warm-up would hide rather than solve the issue. Recording earlier can help only when there actually is an earlier observable state.

Option C, retain constant demand with an external benchmark, is appropriate for state-burden description with unknown onset, not a direct transition or capacity estimate. Recommendation: implement the offline diagnostic bank first if authorized; select a future transition-oriented design only if the research endpoint requires observed onset. No simulation change is presently necessary or approved.

## 16. Limitations and method-revision boundary

The proposal intentionally does not fully solve physical normal/congested classification: high-mobility screened donors are not independently calibrated normal labels. Single-seed autocorrelation, loaded free flow, lane mixing, sparse exposure, conservative masks and limited donor support may yield no reference. An external-density comparison would systematically make a higher-demand run easier to label accumulated; prohibited here.

If reference failure is to stop blocking State 1, that is a substantive classifier revision: separate state-only evidence from observed-onset evidence and design an independently justified concentration/spatial requirement. Merely keeping the numeric density multiplier while swapping its comparator would still change the density gate. This task does neither. Preserve old P/L/S outputs, evaluate any future version in parallel on both A0 and3350 (and held-out data when available), and obtain new review before claims. G6/G7 remain unresolved; a reference extension cannot release a new run.

## 17. What needs Robert confirmation

Confirm whether the thesis endpoint requires observed breakdown transition or can include sustained state burden with unknown onset; what evidence validates a synthetic normal-state bank and its concentration support; acceptable cross-demand/seed transportability; whether a demand-step experiment is appropriate; how to validate model-reference normalization and sparse lane exposure; and whether capacity drop is a later mechanism endpoint. Existing guidance supports simple uncontrolled near-breakdown investigation and insertion validation, not approval of these new reference rules.

Stage 6 remains **PARTIAL**, O2 **NOT_RESOLVED**, formal protocol empty/unfrozen. No classifier, raw/scientific input, historical result, controller or formal protocol is modified.

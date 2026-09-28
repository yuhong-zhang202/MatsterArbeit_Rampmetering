# Freeway Protectable State: Exploratory Operational Definition

Date: 2026-09-21. Status: **Proposed exploratory operationalization; pending application.**
Scope: existing Stage 6 matched A/B/C seed17. This document defines a measurement procedure; it does not classify those runs, change their scientific results, approve a controller, or freeze a formal protocol.

## 1. Executive conclusion

**PARTIALLY.** The existing literature supports a scientifically defensible *structure* for an exploratory definition. It does not supply transferable numerical thresholds for this synthetic merge. Confidence: **High** for that distinction; **Moderate** for the proposed operationalization; predictive validity and actual A/B/C classification: **Unknown** until application and validation.

> Current literature is sufficient for the structure of the rule, but not for freezing its numerical threshold.

The target is a collective, persistent reduction in mainline mobility near the merge, corroborated by vehicle accumulation or a coherent congestion pattern, with plausible local bottleneck attribution. A single slow vehicle, a brief speed minimum, a controller set-point exceedance, or reduced downstream flow alone does not establish it.

Recommend **Candidate B**, a two-layer, 30 s aggregate-state and 1 s trajectory rule. A deliberately explicit provisional numerical profile is supplied for reproducible exploratory screening. Its numbers are project conventions, not empirically validated critical values. Reports must say `STATE1_EXPLORATORY_RULE_POSITIVE`, not unqualified “confirmed physical breakdown.” Candidate A and the fixed sensitivity profiles provide the secondary checks. A positive result identifies a plausible protection opportunity, not proven controllability or net benefit. A negative result means no qualifying event under these definitions, not that metering can never help.

No new SUMO run is required to apply the exploratory rule to existing A/B/C seed17. This is a statement about archived measurement capability; code implementation, integrity checks, event attribution and actual classification remain pending.

## 2. Research need

The latest pressure diagnosis establishes that merge-local M disturbances are observable. It does not establish a sustained baseline state. The matched audit does not identify a consistent freeway protection direction, while restriction-related R queue growth and C's urban-side deterioration are separately documented. These are different questions:

1. Does A contain a relevant freeway state?
2. Does B/C improve that state or other M outcomes?
3. Are any benefits worth their R/U costs?

The present task addresses the definition needed for question 1. It must not make questions 2–3 true by construction. Early prevention of a plausible future breakdown can also justify metering; already observed State 1 is a strong baseline eligibility route, not a universal necessary condition for every ramp-metering application.

Authoritative project evidence reviewed:

- `data/processed/stage6_o2_matched_abc_assessment_20260921_v1/REPORT_revision03.md` and `SCIENTIFIC_REVIEW_FINAL_RECORD.md`.
- `data/processed/stage6_o2_causal_diagnostic_20260921_v1/attempt03_data_audit_revision01/REPORT_revision04.md` and `SCIENTIFIC_REVIEW_FINAL_REVISION04.md`.
- `data/processed/stage6_o2_freeway_pressure_diagnosis_20260921_v1/REPORT_revision02.md`, `detector_mapping.csv`, and `source_hashes.json`.
- `docs/PROJECT_STATE.md` and latest `docs/WORKLOG.md` entry record scientific PASS for the pressure diagnosis. Its report itself still says pending review; no separate final review file was located in that package. Preserve this provenance distinction rather than inventing a reviewer receipt.

Context Preflight also read AGENTS, DECISIONS, SUPERVISOR_FEEDBACK, the relevant WORKLOG entries and Robert's original archived reply. `docs/EXPERIMENT_PROTOCOL.md` exists and is empty. O2 remains `NOT_RESOLVED`, Stage 6 `PARTIAL`. Existing uncommitted changes predate this task and are preserved.

## 3. Evidence from existing literature

All locators below refer to repository PDFs. PDF page means the one-based file page, not necessarily the printed page. Summaries are paraphrases. The operational rule in sections 9–14 is this project's proposal, not a rule quoted from any paper.

### Treiber and Kesting (2013), Traffic Flow Dynamics [T]

Source: `literature/core_reading/Traffic Flow Dynamics.pdf`.

- Chapter 3, printed pp. 15–17 / PDF 26–28: temporal detector averages and spatial averages differ; occupancy is time over a detector, density is vehicles per road length. Therefore E1 speed, FCD sample speed and density cannot be silently interchanged.
- Chapter 4.4, printed pp. 31–33 / PDF 42–44: a fundamental diagram represents equilibrium; observed scatter includes measurement, heterogeneity and non-equilibrium effects. Maximum observed flow is not automatically capacity, and q divided by a mismatched speed is not an independent density measurement.
- Chapter 17, printed pp. 339–350 / PDF 344–355: localized pinned congestion and extended congestion are distinct. A pinned localized cluster need not propagate upstream to a remote detector. Class 3 includes congested states with minimal or zero capacity drop (printed p. 346 / PDF 351). Thus neither remote upstream propagation nor nonzero capacity drop is a universal necessary condition for congestion.
- Chapter 18.1, printed pp. 355–360 / PDF 359–364: high traffic load, bottlenecks and disturbances jointly explain most observed breakdowns. Individual perturbations and collective evolving states are different levels of description.
- Chapter 18.3, printed pp. 361–363 / PDF 365–367: localized/extended patterns, stationary bottleneck fronts, upstream-moving structures and queue dissolution motivate space-time evidence. Do not transplant real-road kilometre lengths or wave velocities into this synthetic network.
- Chapter 21.3, printed pp. 407–410 / PDF 409–412: metering can prevent breakdown, but release platoons and secondary-network spillover can make matters worse. Its example is model-specific and calibrated; its numerical values are not project parameters.

### Brilon, Geistefeldt and Regler (2005) [B]

Source: `literature/core_reading/RELIABILITY OF FREEWAY TRAFFIC FLOW.pdf`; paper title: *Reliability of Freeway Traffic Flow: A Stochastic Concept of Capacity*, proceedings pp. 125–144.

- PDF 3, 5–6: breakdown is a transition in an aggregated speed/flow sequence; already congested intervals are not repeated breakdown-capacity observations. The paper explicitly identifies about 70 km/h as representative for German freeway conditions and says other roads may require different or more detailed criteria, including a speed difference.
- PDF 5: 5 min is a compromise after considering detector reliability and usefulness. The text states that ideally one minute or less would be used. It is not a universal minimum duration for congestion and not a persistence requirement transferable to this project.
- PDF 5–6, 9: downstream tailback must be distinguished from local breakdown.
- PDF 11–15: onset, congested state, recovery and queue discharge are separate. Flow during congestion need not equal discharge capacity. Capacity-drop estimates depend strongly on the estimator and site. PDF 13 even notes exceptions with higher synchronized-flow averages under variable speed control.

### Cassidy and Bertini (1999) [C]

Source: `literature/core_reading/Some trac features at freeway bottlenecks.pdf`; *Transportation Research Part B* 33, pp. 25–42.

- Printed p. 27 / PDF 3: measurements were collected at 30 s and 20 s, showing that 5 min is not mandatory for queue diagnosis.
- Printed pp. 28–32 / PDF 4–8: time-shifted cumulative counts, corrected for ramp inflow, identify excess accumulation; occupancy changes corroborate backward-moving queue arrival. Downstream flow and occupancy can both decrease in an expansion wave. Therefore “occupancy must rise at every detector” would be wrong.
- Printed pp. 36–37 / PDF 12–13: downstream tailback can deactivate the studied bottleneck, invalidating that location as an unrestricted discharge measurement.
- Printed pp. 39–41 / PDF 15–17: repeated observations support lower mean queue discharge at the studied sites, but geographic transfer and underlying driver mechanisms remain limited.

Its diagnostic logic can be adapted. Its plotted queue-arrival times, long durations, flow-drop percentages and qualitative curve inspection are **not** an already specified detector classifier for this network. Raw lane-loop contribution counts also cannot simply be substituted for conserved unique M counts through a merge.

### Papageorgiou and Kotsialos (2002) [P]

Source: `literature/core_reading/Freeway_ramp_metering_an_overview.pdf`; *IEEE Transactions on Intelligent Transportation Systems* 3(4), pp. 271–281; DOI 10.1109/TITS.2002.806803.

- Printed p. 272 / PDF 2, II-B: preventing reduced congested outflow can improve total time including ramp waiting.
- II-C explicitly considers **no capacity drop** and an upstream off-ramp whose discharge is obstructed by freeway congestion. This establishes another possible benefit mechanism, but our single-entrance topology does not automatically contain that off-ramp mechanism.
- Printed pp. 273–274 / PDF 3–4: poorly chosen metering can leave the freeway underused. Restriction is not monotonically beneficial.
- Printed p. 274 / PDF 4: critical occupancy refers to maximum flow; ALINEA's desired downstream occupancy is typically, **not necessarily**, that value. Its feedback is preventive and responds before a crude threshold switch. A target is not a state label.
- Printed p. 275 / PDF 5: excessive ramp queues can require override to protect surface streets.

### Riehl, Kouvelas and Makridis, sumoITScontrol [S]

Source: `literature/sumoITScontrol.pdf`, repository version labelled **PRE-PRINT VERSION**, with placeholder DOI. Cite this version as a preprint; do not invent final publication metadata.

- PDF 4–5: merge bottlenecks, downstream occupancy feedback, a desired occupancy target and transportation efficiency motivate ALINEA sensing. The printed recursive equation is integral feedback despite inconsistent prose labels; this task relies on its sensing concept, not its terminology as proof of implementation behavior.
- PDF 17–20: merge geometry, signal acceleration distance, lane connections and sensor location affect behavior and interpretation. Mainline sensors must be distinguished from auxiliary-lane diagnostics.
- PDF 20–22: realized supply must be checked. Its case-specific heterogeneity and insertion recommendations are not permission to override Robert's Krauß-default starting guidance.
- PDF 25–27: replicated evaluation and reproducibility are needed for controller comparisons. PDF 34's target occupancy of 10% is a demonstration setting, not an independent critical occupancy estimate or project breakdown threshold.

## 4. What the literature does NOT determine

It does not determine this network's independent free-flow baseline, critical occupancy, critical density, capacity distribution, persistence/recovery duration, minimum affected population, spatial resolution, or acceptable misclassification rate. It does not prove that the current synthetic model produces a realistic capacity drop or that A must contain a protectable state.

Project operationalization must specify the population, speed reference, aggregation, observation validity, persistence, accumulation/propagation evidence, onset/recovery logic and exclusions. The transferable elements are the concepts and measurement cautions. The following are not directly transferable: 70 km/h, 5 min, a real-road wave speed, kilometre-scale cluster length, Cassidy's observed drop percentages, or an ALINEA example occupancy target.

## 5. Conceptual state hierarchy

|State|Meaning|Permitted interpretation|
|---|---|---|
|State 0: NORMAL MERGE DISTURBANCE|One or several vehicles slow during interaction, then the local traffic population returns toward its reference state without sustained accumulation or a persistent collective pattern.|Normal interaction is compatible with nonzero delay. This label requires observed recovery; failing State 1 alone does not prove State 0.|
|State 1: PROTECTABLE MAINLINE CONGESTION / BREAKDOWN|A collective non-free-flow condition near the merge persists beyond an isolated interaction, with accumulation or coherent spatial structure, and a plausible local bottleneck association.|There is a reasonable mainline protection opportunity to test. Congestion is a state; breakdown is the observed transition into it. A state present at the observation boundary has unknown onset.|
|State 2: CONGESTED DISCHARGE / POSSIBLE CAPACITY-DROP STATE|State 1 coexists with an upstream congested reservoir discharging through the bottleneck into an unblocked downstream receiving section.|Discharge may be measured; capacity drop remains a separate hypothesis requiring a defensible pre-breakdown comparator and comparable supply.|

These are operational evidence labels, not a claim that traffic always traverses 0→1→2 in a unique order. Recovery, recurrence, and left/right censoring must be retained. Additional output labels are `EARLY_WARNING`, `AMBIGUOUS`, `NOT_EVALUABLE`, and `NO_QUALIFYING_EVENT`; they must not be collapsed into State 0.

## 6. Evidence dimensions

|Dimension|Useful evidence|Insufficient or misleading evidence|
|---|---|---|
|Speed|Aggregated M mobility loss relative to an explicit reference, distributed over vehicles, persistent across windows; report absolute speed as well.|One minimum, speed below the posted limit, or arithmetic E1 speed treated as space mean.|
|Occupancy / density|Increased local vehicle concentration during sustained slowdown; occupancy at a queue arrival station; separate physical density from loop occupancy.|Occupancy alone; auxiliary R occupancy called mainline congestion; low downstream occupancy interpreted as absence of upstream queue.|
|Flow|Actual mainline/ramp supply, unique downstream throughput, pre-onset versus congested discharge with consistent boundaries.|Lower flow due to meter suppression, demand ending, missing vehicles, or a different lane count called capacity drop.|
|Duration|Persistence in a fixed spatial region affecting successive traffic, plus trajectory checks inside the aggregate windows.|A 5–15 s single-vehicle drop proves neither a persistent population state nor breakdown. A brief event can be part of a larger wave; do not automatically label all short events normal.|
|Spatial propagation|Coherent upstream arrival sequence or a pinned localized cluster with repeated affected vehicles and surrounding recovery.|Two simultaneous slow detectors alone prove direction; a forward-moving platoon called a backward-moving queue.|
|Recovery|Local group speed and concentration recover; queue boundary retreats or disappears; subsequent vehicles pass without the same impairment.|One vehicle accelerates while following vehicles remain queued; absence of vehicles counted as recovery.|
|Bottleneck attribution|Earliest observable impairment near merge, downstream receiving space available, mapped topology and trajectories compatible with merging.|Downstream-first tailback, source insertion effects, unintended direct signal restriction, geometry faults or another bottleneck attributed to ramp demand.|

No reviewed source supplies a universal persistence threshold directly portable to this synthetic scenario. A 30 s average can hide short events or blend multiple separate events. A 1 s trajectory can overemphasize individual behavior. Use both; trip outcomes contextualize consequences but do not locate onset or propagation.

## 7. Required vs supporting criteria

|Criterion|General classification|Reason|
|---|---|---|
|Collective mainline speed degradation|REQUIRED|The target is impaired M operation, not merely a queue elsewhere.|
|Persistence across population/time, or a sustained tracked spatial pattern|REQUIRED|Separates state from an isolated maneuver; spatial movement does not waive temporal evidence.|
|Adequate M population/coverage and bottleneck attribution|REQUIRED|Avoids single-vehicle, missing-data and wrong-cause labels.|
|Corroboration by accumulation or a coherent congested spatial pattern|REQUIRED as an alternative-evidence group|Speed alone is insufficient. These measurements need not be statistically independent, and often share FCD.|
|Occupancy increase at a particular E1|SUPPORTING|Position and vehicle lengths matter; equivalent FCD density can provide corroboration.|
|Upstream propagation|SUPPORTING|Pinned localized congestion can be real. Required only for a label claiming propagation.|
|Queue formation|SUPPORTING if this means a stopped, connected queue; REQUIRED only in the broader collective accumulation/spatial-pattern alternative above|Moving congestion need not contain stopped vehicles or a meter-anchored chain.|
|Flow reduction|SUPPORTING / DIAGNOSTIC|Congestion can coexist with substantial flow; reduced arrivals can also lower flow.|
|Capacity drop|OPTIONAL / DIAGNOSTIC for State 1; a separate endpoint for State 2|Neither necessary for detecting congestion nor established by one low-outflow bin.|
|Observed recovery|SUPPORTING for State 1; REQUIRED for calling an event recovered State 0|Right censoring must not erase persistent episodes.|

## 8. Candidate operational definitions

### Candidate A — Conservative / High-specificity

Concept: persistent collective slowdown plus sustained accumulation, also supported at an independent spatial location. Required: Candidate B gates, the stricter numerical profile below, and coherent impairment in at least two adjacent fixed spatial cells during the qualifying period. At least one cell intersects the merge core. Supporting: E1 occupancy/flow sequence and a demonstrable upstream front. Exclusions: all section 14 exclusions; no inference of propagation merely from adjacency.

Existing FCD supports the measurements; E1 alone may miss an in-between cluster. Main false negative: localized or one-lane congestion diluted by cross-section pooling; main false positive: a long platoon or recurring signal releases passing the selected area. Suitable for exploratory high-specificity robustness. Formal use requires validation/approval. Not an ALINEA actuation law.

### Candidate B — Balanced (recommended)

Concept: a fixed near-merge cell has persistent population-level M slowdown with increased M spatial concentration and concurrent slow vehicles, together with a cleared attribution check. Required: the exact primary gates in sections 9 and 14. Supporting: neighboring-cell structure, E1 changes, increased local M travel time and upstream propagation. Exclusions: missing reference/population, unobserved onset, unresolved alternative cause, source or downstream-boundary origin.

The fixed-cell requirement conservatively operationalizes pinned or extended congestion; a wave that moves through too quickly is separately retained as a diagnostic candidate. FCD permits observation between current loops. False positive: recurring platoons or chronic geometric friction. False negative: modest moving congestion, oscillatory patterns with intervening recoveries, or lane-specific impairment diluted over two lanes. Suitable as the present exploratory primary rule. Not validated for formal experiments or real-time ALINEA operation.

### Candidate C — Sensitive / Early-warning

Concept: an emerging group slowdown or growing disturbance that may precede sustained congestion. Required: one valid aggregate bin meeting the sensitive speed/population gates; retain accumulation and propagation indicators whether positive or negative. Supporting: continued supply, increasing concentration or a following-bin repetition. Same artifact flags apply. Output only `EARLY_WARNING`; do not call it near-capacity probability, metastability, or confirmed breakdown.

Current data support a diagnostic screen. High false-positive risk from ordinary merging; lower false-negative risk for mild/brief events than A/B. Useful for selecting events for examination. Formal risk prediction needs independent validation. Could inform later controller research but is not a calibrated activation trigger.

## 9. Recommended exploratory rule

**PRIMARY EXPLORATORY RULE = Candidate B, profile P.** All requirements are conjunctive:

1. Valid 30 s M aggregates in the same fixed spatial cell for three consecutive bins.
2. Mean normalized M speed at most 0.70 in every bin, with at least half of M vehicle-time samples individually at or below 0.70.
3. In every bin, at least two slow M vehicles are simultaneously present at at least 15 of the 30 recorded labels. This is an explicit small-population safeguard, not a statistically validated sample size.
4. Mean M spatial density exceeds the median density of the three immediately preceding reference bins in every qualifying bin. Each reference bin must be valid and have normalized mean speed at least 0.85. A zero-density reference is invalid. Density must be counted from FCD, not calculated as q/v.
5. The cell intersects the merge core; mapped temporal/spatial evidence clears the attribution gates. Otherwise retain a numerical candidate with unresolved attribution.

This is a proposed screening definition of a sustained, accumulating local condition. The strict density comparison is deliberately reported with its absolute and relative margin; a tiny positive difference cannot establish robust accumulation. Secondary checks below expose this vulnerability.

The modeled reference is `v_ref(i,lane) = archived_lane_speed_limit × archived_vehicle_speedFactor`. Call the resulting quantity **model-reference speed ratio**, not observed free-flow speed or actual allowed speed. No implicit vType maximum, leader constraint or stochastic speed effect is assumed known. It supplies a reproducible normalization independent of selecting observed A/B/C minima. Use each run's own archived vehicle attributes and identical formulas; do not assume same seed guarantees identical realized attributes.

**SECONDARY ROBUSTNESS RULE:** run exactly the predeclared stricter profile S and more sensitive profile L in addition to P, and Candidate A's spatial gate. This is offline rule sensitivity, not a simulation parameter sweep. Do not search for a favorable profile.

|Profile|Mean and sample speed ratio|Consecutive 30 s bins|Density requirement vs same prior-reference definition|Purpose|
|---|---:|---:|---|---|
|P: primary|≤0.70|3 (90 s aggregate window)|strict increase|Balanced screen|
|S: stricter|≤0.60|4 (120 s)|≥1.25 times reference|Specificity and accumulation-margin check|
|L: more sensitive|≤0.80|2 (60 s)|strict increase|Detect dependence on a stricter primary cut|

All keep the same half-sample, simultaneous-population, attribution and reference-speed gates. Because reference/onset eligibility can change with episode boundaries, these are not mathematically guaranteed nested event sets. Publish each result; do not force monotonicity. Primary-negative/L-positive means threshold-sensitive, not normal traffic. Agreement across profiles is robustness within this small declared family, not proof of the correct threshold.

**Why these provisional numbers:** coarse 20/30/40% speed reductions and 2/3/4 existing detector intervals make magnitude and duration sensitivity transparent. Ninety seconds spans repeated 30 s observations; it is not a discovered traffic constant or a proof that shorter collective congestion is impossible. No number was obtained by solving for the observed extrema or desired A/B/C ranking. The existing outcomes were already known, so this is transparent retrospective exploratory design, not outcome-blind preregistration. Lock this document before subsequent application and disclose that limitation.

## 10. Numerical threshold provenance and formal persistence workflow

|Number or quantity|Provenance|Use here|
|---|---|---|
|About 70 km/h; 5 min|LITERATURE-DIRECT for Brilon's empirical study only; applicability to this synthetic merge not established|Not adopted|
|20/30 s source measurements in Cassidy|LITERATURE-DIRECT for those sites|Supports feasibility of shorter aggregation, not project threshold validity|
|1 s FCD; 30 s native E1; 0–2700 s run; demand ends 1500 s; lane speed 33.33 m/s|DATA-DERIVED / archived configuration and output facts|Observation grid and normalization input, not scientific thresholds|
|Vehicle speedFactor and resulting v_ref|DATA-DERIVED from archived attributes plus declared formula|Model scale; empirical free-flow baseline remains uncalibrated|
|100 m spatial cells; 0.60/0.70/0.80, 0.85; 2/3/4 bins; 50% samples; 2 simultaneous vehicles at 15 labels; density factor 1.25; two-bin recovery and adjacent-cell requirement|LITERATURE-INFORMED PROJECT OPERATIONALIZATION|Proposed reproducibility conventions; no source directly validates these numbers|

There is no LITERATURE-DIRECT numerical **decision threshold** established as transferable to this project. There is no data-fitted speed or persistence threshold in this report. Published observation periods are not evidence that a particular minimum persistence is optimal.

Before formal experiments: define the intended error costs; obtain an independent reference/free-flow characterization; label a calibration event set using population trajectories, density and fronts with controller labels hidden; compare predeclared temporal/spatial resolutions and persistence choices against those labels; assess errors by whole event and run rather than treating vehicle-seconds as independent replicates; validate on held-out conditions/replications; then obtain user/supervisor decisions and freeze the definition before formal outcome comparison. Calibration and validation data must be separated. Future extra data, if necessary, need a separate authorization; this task starts none.

## 11. Measurement compatibility

|Existing source|Capability|Limitation|
|---|---|---|
|main_up1300, two lanes|Aggregate upstream state before the merge|One upstream section cannot localize all upstream fronts; absence of its activation does not exclude a pinned cluster|
|merge20 main lanes, two loops|Early merge-section state|Upstream of many actual interactions; cannot rule out impairment around pos 70–110 m or farther downstream|
|merge20 auxiliary lane|Ramp delivery/acceleration diagnostic|Not an M mainline state sensor; keep separate|
|main_down20 and main_down200|Post-merge discharge/recovery context|Vehicles may have recovered before crossing; M/R mixed; 30 s timing weakens direction inference|
|Full 1 s FCD, including through internal lanes|Between-loop collective state, density, trajectory recovery, approximate onset and propagation|Subsecond behavior and exact crossing times unresolved; no complete microscopic braking-cause log|
|vehroute + tripinfo + demand/config/network|Identity/type/route/reference joins, actual insertion, censoring and geometry mapping|Free-flow speed and critical occupancy are not independently calibrated|

Native E1 alone is insufficient for a reliable negative classification of a small in-between cluster. Existing FCD plus E1 can calculate P/S/L and Candidate A, subject to their coverage gates. Positional loop gaps are not necessarily archived-data gaps. FCD enables observed upstream propagation where it persists over enough sampled locations; the onset/front location remains bracketed, and movement outside the network is unobserved.

Needed processing: raw-ID joins, exact lane whitelist, spatial cells, time-bin population summaries, reference/episode logic, attribution evidence and uncertainty reporting. No new physical sensor is needed to perform that offline calculation. Missing calibrated free-flow, critical occupancy and causal counterfactuals are methodological/inference gaps; simply rerunning SUMO would not fill them.

## 12. Capacity-drop role

**Capacity drop is not required for State 1. Confidence: High.**

- A. Breakdown detection: establish a transition and persistent collective congestion. Requiring a measured drop would wrongly reject congested states without an identified pre-breakdown capacity or adequate discharge window [T, B].
- B. Controller justification: prevention of discharge loss is a strong mechanism [P, T]. Other network mechanisms exist [P II-C], but must actually exist in the studied topology. In a simple fixed-demand merge with no capacity drop or blocked exit, moving delay from M to R may redistribute costs without lowering system loss. State 1 therefore justifies testing an opportunity, not claiming a net efficiency gain.
- C. Post-breakdown severity: sustained lower discharge while an upstream queue and unconstrained downstream receiving space remain is useful evidence [C]. A transient trough, falling demand or restricted R supply is insufficient.
- D. Later thesis analysis: estimate pre-breakdown and discharge quantities with comparable boundaries and supply, account for stochastic capacity and exclusion of tailback [B, C], and use replicated observations. Do not compare arbitrary maxima with arbitrary congested averages.

Robert asked whether plausible breakdown and capacity drop emerge; his archived reply does not define the latter as a necessary diagnostic condition for the former. These remain two questions.

## 13. ALINEA circularity check

`target occupancy = critical state → target exceedance = breakdown` is invalid as an evidential chain. The first equality needs independent estimation at the relevant detector with the relevant vehicle composition and aggregation. Even an independently estimated critical occupancy does not make every noisy exceedance a sustained state transition [P]. A chosen controller target may deliberately differ from critical occupancy.

Keep the state classifier independent of target occupancy and evaluate control using its state incidence/duration plus M mobility and R/U consequences. Occupancy tracking error can be a controller diagnostic; it cannot simultaneously be the ground truth establishing congestion and the sole proof of controller success. The 10% example in [S] is not used here.

## 14. APPLICATION_SPEC

### 14.1 Scope, inputs and output locations

Task for subsequent Luna High / `data_analyst`: implement and apply **this exact version** offline to A/B/C. Read Context Preflight, preserve all original records, and create a new exclusive output directory. Do not alter this document's thresholds on seeing results.

Raw root: `data/raw/stage6_targeted_validation_20260920_v1/`.
Run IDs: `TV_A_S17_attempt1`, `TV_B_S17_attempt1`, `TV_C_S17_attempt1`.
For each, read `output_manifest.json`, `outputs/fcd.xml`, `outputs/vehroute.xml`, `outputs/tripinfo.xml`, all nine `outputs/p1_*.xml` E1 files, and available archived TLS, summary/error and lane-change outputs resolved by manifest roles, not guessed filenames.

Static inputs: `artifacts/stage6_targeted_validation_20260920_v1/engineering/build_attempts/TV_BUILD01/network.net.xml`; each run's `engineering/inputs/<run>/demand.rou.xml`, `scenario.add.xml`, `scenario.sumocfg` under the same artifact root. Source hashes in the pressure package are useful anchors; verify actual sources rather than trusting copied results.

New derived data/code/receipt: `data/processed/stage6_protectable_state_application_<date>_v1/` (exclusive create; choose a new suffix if it exists). Tables: corresponding new directory in `results/tables/`. Figures, if produced: corresponding new directory in `results/figures/`. Raw data read-only. No simulation, simulator import that launches a process, network build, parameter change, new seed, or controller experiment.

### 14.2 Preprocessing and population

Verify complete XML and manifest hashes; unique `(run,time,vehicle_id)` keys; timestep grid; route/type joins; M identity prefix corroborated by M route; per-run speedFactor >0; no unknown lanes or silently omitted internal sections. Reconcile M identity counts with tripinfo/vehroute, and preserve missing/censored observations. Original raw FCD has speed, lane, pos, x/y and time; speedFactor comes from vehroute. Missing attributes produce `NOT_EVALUABLE`, not a default.

Whitelisted mainline lanes: `main_up_0`, `main_up_1`, `:freeway_merge_0_0`, `:freeway_merge_0_1`, `merge_section_1`, `merge_section_2`, `:merge_end_0_0`, `:merge_end_0_1`, `main_down_0`, `main_down_1`. Verify these against compiled connections. Exclude auxiliary `merge_section_0` from the mainline aggregate; retain separately. M on an unexpected auxiliary/ramp lane raises a coverage/geometry flag rather than being dropped. For total physical population, count M and merged R on whitelisted lanes; retain class-specific M density for the primary gate.

### 14.3 Temporal and spatial aggregation

Use original labels t=0…2699 and half-open bins `[30k,30(k+1))`; no interpolation of speed and no filling missing timesteps. Scan the complete run. Tag pre-300, demand-time and post-1500 observations without excluding them; these tags do not create a new approved warm-up.

Use fixed 100 m longitudinal physical cells anchored at x=0 on the compiled straight mainline, spanning [0,2200). Validate mainline lane shapes and direction first. Include through internal lanes; classify by physical coordinate, not a discontinuous edge-position sum. All cells with positive-length intersection with the compiled merge_section or its adjacent through internal connectors form the **merge core**. Use full cells for measurement; record core overlap. Count each vehicle front once, with left-closed/right-open boundaries; an exact x=2200 terminal sample is assigned to the last cell and explicitly counted as a terminal-boundary exception. Other out-of-domain samples are flagged, not clipped. Cells outside the core remain available for upstream/downstream context. Report actual two-lane road length per cell and stop if physical geometry contradicts this map; do not invent a replacement mapping silently.

For each cell/bin, compute `nM(t)`, `nSlowM(t)`, unique M IDs, total M sample count N, mean absolute speed, normalized mean `r = sum(v_i/v_ref_i)/N`, slow fraction `f = count(v_i/v_ref_i <= alpha)/N`, and mean spatial density `kM = sum_t nM(t)/(30 × lane_length_km)`. Compute total mainline M+R density separately. Empty labels count zero in density; speed with N=0 is NA. A valid bin has all 30 time labels and at least two unique M IDs; this is a minimum observation gate, not statistical independence. The simultaneous slow-vehicle gate in section 9 is additionally required for a low-state bin.

Native E1: retain lane level, normalize no-contribution speed to NA, report contribution-weighted station speed, equal-lane mean occupancy and summed flow with original denominators. Do not treat E1 as M-only after the merge, do not deduplicate lane-loop events without identities, and do not require E1 and spatial FCD means to agree numerically.

### 14.4 State-transition and persistence logic

For each profile and core cell, form a maximal consecutive run of **low-state bins** satisfying its speed, slow-fraction and simultaneous-population gates. Missing/invalid/nonqualifying bins terminate the run; no gap bridging. Assess reference conditions using exactly the three bins immediately before the first low bin; do not search backward for a favorable reference.

If the run is shorter than the profile's duration, retain a disturbance/early-warning candidate. If long enough, use the first required 3/4/2 low bins for the profile's qualification and density comparison. Retain subsequent low bins as the episode's observed low-speed continuation; flag any later density gate failure separately. A later subrun may not be relabelled as a new onset merely to obtain a more favorable reference. An episode lacking eligible prior reference is `ONSET_REFERENCE_UNRESOLVED`; do not call it absent or confirmed.

Numerical onset lies within the first qualifying 30 s bin; confirmation is available only at the end of the required run. The 90 s profile duration denotes three low aggregate bins, not 90 continuously slow seconds. Report actual slow-label counts and internal within-bin recoveries. Use 1 s trajectories to bracket finer changes, never manufacture subsecond exact onset.

After low-state continuation ends, recovery is confirmed only by two consecutive valid bins in the same cell with normalized mean speed ≥0.85 and mean M density ≤the pre-event reference. The first recovery-bin start is the aggregate recovery boundary. Bins between last low and recovery are transitional, not automatically congested. If no recovery is observed, flag `RECOVERY_UNRESOLVED` or `RIGHT_CENSORED`; disappearance of M is `POPULATION_ENDED`, not speed recovery.

Candidate A: apply S and require at least two adjacent cells to pass its low-state and density conditions in the same four-bin qualification window, with eligible local references; one intersects the core. Label the result spatially corroborated; upstream propagation remains a separate diagnostic. Candidate C: apply L's per-bin low-state gates to a single bin; no State 1 designation.

Run output precedence, separately for each rule: `STATE1_EXPLORATORY_RULE_POSITIVE` if at least one episode passes all numerical and attribution gates, while retaining unresolved events alongside it; otherwise `CANDIDATE_ATTRIBUTION_UNRESOLVED` if a numerical-positive episode has unresolved attribution; otherwise `ONSET_REFERENCE_UNRESOLVED` if a duration-qualified low-state run lacks an eligible prior reference; otherwise `NOT_EVALUABLE` if missing data or another material observation failure prevents evaluation; otherwise `NO_QUALIFYING_EVENT`. Report excluded episodes and early warnings in every case. Absence of an identified transition cannot establish absence of an already-congested state. Empty population before first entry and after last exit is outside M state exposure, not a data failure; partially populated edge bins remain subject to the specified validity rules. State 0 can be assigned to a documented short event only when recovery and absence of a surrounding sustained pattern are established.

Use deterministic cell-event IDs `(run,profile,cell,first_low_bin)`. Adjacent-cell detections remain separate records and must not be added as independent congestion events. If summarizing a run's **qualifying-episode-associated low-speed duration**, take the union of its qualified episodes' low-bin intervals; do not sum simultaneous cells or include transitional/recovery bins. This measure includes low-speed continuation whose density gate may later fail, so it is not fully qualified State 1 duration. Output density and attribution eligibility separately for every continuation bin. Any fully qualified State 1 burden must include only bins that retain all applicable gates, without reselecting the reference; unresolved bins remain separate. Report cell-event count separately from physical event count, which is `NOT_ESTIMATED` in this specification. Candidate A spatial confirmations list their contributing cell-event IDs and common qualification window, without double counting overlapping windows.

### 14.5 Attribution and exclusions

Each numerical candidate receives a mandatory attribution record with `CLEAR`, `EXCLUDED`, or `UNRESOLVED` for each item. This is a bounded evidence review, not permission for the analyst to change thresholds. Machine-positive candidates with any unresolved material cause stay unresolved. Record evidence even when it contradicts the expected result.

- Downstream tailback: examine downstream cells and loops preceding and spanning onset; a downstream-first connected slowing pattern is excluded as *locally generated merge* breakdown. Simultaneous/coarse timing without a clear order is unresolved.
- Source artifact: inspect source-side speed/population/insertion and whether the disturbance starts upstream and travels forward. Delayed insertion is reported separately; low realized supply cannot establish high demand at the merge.
- Signal artifact: inspect topology and archived TLS. A direct mainline red constraint is excluded. Ramp-release platoons may be a real treatment effect; record them as such rather than automatically excluding B/C events.
- Geometry/unrelated bottleneck: use compiled lane permissions, speed limits, through connections and event location. O1's bounded earlier acceptance is context, not proof against every possible artifact. A specific unexplained restriction leaves attribution unresolved.
- Boundary/censoring: unknown prehistory, insufficient downstream coverage or end-of-population must be explicit. No numeric event deletion; retain the event and exclusion reason.

M/R local merging and a clear downstream receiving section support `MERGE_ASSOCIATED`. They do not identify the unique driver's braking constraint or the causal counterfactual “removing one R would prevent breakdown.” Upstream propagation can be reported only if successive upstream positions show later onset and a coherent slow region affecting different vehicles. A trace moving with the same vehicles downstream is not upstream propagation. Ambiguous ordering is unidentifiable.

### 14.6 Outputs, verification and prohibited inferences

Deliver: input/hash manifest and mapping; per-cell/bin numeric table for P/S/L; lane-specific diagnostic table; complete candidate event catalogue with references, qualification margins, low/transition/recovery intervals and flags; attribution ledger with source locators; A/B/C classification matrix by rule; short report and machine-readable receipt. Optional space-time figures use identical axes and scales across A/B/C. Preserve all negative and ambiguous events.

Uncertainty flags must include missing data, low population, unknown lane, model-reference-not-calibrated, ratio near cut/rounding, weak density margin, onset-reference failure, bin alignment, one-lane dilution, downstream attribution, source artifact, boundary censoring and population ended. Any borderline value within raw serialization precision must be flagged; repeat rounding-bound calculations or mark undecidable rather than rounding to pass.

Before application, test hand-constructed cases: one slow vehicle; brief dip; persistent group with accumulation; stationary local cluster without remote propagation; forward platoon; downstream-first tailback; zero passage; empty population; missing timestep; internal-lane traversal; exact bin/cell boundary; recovery missing; speedFactor join failure. Reconcile a small real raw slice independently. These are offline analyzer tests, not SUMO smoke tests. Independent scientific review follows the application; this document's review cannot certify unimplemented processing.

Must NOT infer: formal breakdown probability, calibrated critical density/occupancy, physical capacity, capacity drop, ALINEA efficacy, a causal M-versus-U trade-off, O2 resolution, or cross-seed generality. Even a P-positive A and P-negative B/C requires inspection of actual supply and exposure before attributing improvement to metering. If all profiles are negative, report that result; never retune to force a positive.

State 2 output for this application is only `DISCHARGE_CANDIDATE` when a State 1 event has a continuing upstream reservoir and clear downstream receiving space. Capacity drop remains `NOT_ESTIMATED` unless separately authorized with its own comparison rule; do not improvise a discharge-capacity estimator.

## 15. Limitations

The operational profile is a deliberately conventional exploratory screen and has not been calibrated for accuracy. Its numerical choices can create both false positives and false negatives. A nominal model-reference ratio does not establish a free/congested branch boundary. FCD speed and density share observations and are mechanically related through residence time; their agreement is structural corroboration, not independent statistical replication. Two-lane pooling can hide one-lane congestion; fixed-cell persistence can miss traveling or intermittent waves. All conclusions remain conditional on the declared scope and rules.

Existing seed17 results were known before proposing this rule. The fixed sensitivity family and explicit provenance mitigate discretionary tuning but cannot turn retrospective exploration into confirmatory evidence. No A/B/C event was classified in this task. O2 remains open. The pressure report's stale pending-review text is preserved as an existing documentation discrepancy.

## 16. What needs supervisor confirmation later

Confirm whether the thesis will study sustained freeway mobility impairment, breakdown prevention risk, capacity preservation, or a combination; whether localized/one-lane moving congestion suffices; how a freeway benefit is valued against R/U harm; whether capacity drop is a separate validation target or a necessary feature of the intended efficiency mechanism; how to validate independent reference states, persistence and spatial scales; and the eventual formal replication/exclusion design.

These are future research decisions. No contact with Robert is made by this report, and no formal criterion is approved.

## Review and documentation status

Prepared by the primary agent from the repository sources. Independent `data_analyst` performed a read-only measurement-capability audit: relevant archived fields, straight mainline coordinates and through internal lanes support the proposed computations. This was schema/example inspection, not a new full-output integrity audit; no classifications were computed. The independent scientific disposition and any required corrections are recorded separately in `FREEWAY_PROTECTABLE_STATE_SCIENTIFIC_REVIEW.md` when review is complete. This text does not by itself claim that review has passed.

Subagent routing: simulation_engineer — not required (no simulation/configuration implementation or execution); data_analyst — used for measurement-capability verification; scientific_reviewer — required for final review.

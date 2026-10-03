# Stage 6 uncontrolled boundary search — prospective exploratory plan

Date: 2026-10-02. Status: ready for independent execution review; exploratory only.

## Authorization and purpose

The user's current instruction delegates bounded design, execution and interpretation of the next Stage 6 exploration, including demand ranges, seeds, metrics and stopping rules. It conditionally authorizes control comparisons after suitable uncontrolled operating points are identified. The follow-up explicitly requires deciding whether exploration can close when evidence is sufficient, rather than continuing because more runs are possible. This is new authorization, not reactivation of consumed historical run cards. Individual numbers below are researcher-selected operational choices, not parameters specified by Robert or individually approved by the user. The empty `docs/EXPERIMENT_PROTOCOL.md` remains unfrozen; none of these runs is formal thesis validation.

Question: under the current synthetic network/model, where does increasing requested and realized M/R demand create persistent mainline impairment associated with the merge, and is there a credible operating point for testing ramp metering? A negative or supply-limited result is valid. No desired A/B/C ordering is required.

## Evidence and fixed model

- Robert's original 2026-09-30 message: `docs/supervision/2026-09-30_robert_hilbrich_reply.md`, Gmail message `1a0f26498f391980`. Geometry/insertion/connection checks precede an uncontrolled demand search; fixed 22/28 s green times must not be used to manufacture the narrative.
- Current authoritative compiled network: `artifacts/stage6_baseline_localization_20260921_v1/LOC_M3350_S17/engineering/build_attempts/TV_BUILD01/network.net.xml`.
- Reference default-model inputs: `artifacts/stage6_full_network_abc_matched_rebuild_20260926_v1/inputs_retry2/A/`.
- Historical disposition: `artifacts/stage6_exploratory_closeout_20260926_v1/STAGE6_EXPLORATORY_DISPOSITION.md` and Sep30 runtime audit in PROJECT_STATE/WORKLOG. Original RI3350 R0/A remain NOT_PAIRABLE / A_NOT_EVALUABLE. Rebuilt R0/A/B22/B28 are a separate evidence series. Neither is a replication of the new sustained-loading design.
- Existing seed17 trajectories support the 2-mainline-plus-ending-auxiliary geometry, R lane changes and absence of substantial insertion backlog at those tested points. Higher demand requires fresh checks. Platooning is an unproven mechanism, not an established explanation.

Keep network, lane connections, default passenger behavior including sigma, routes, urban signal and departure semantics unchanged: M best/max/100; R/U/X best/max/last. Ramp signal is continuously green. SUMO 1.26.0, one-second simulation and FCD sampling. Urban TLS retains 45G/3y/9G/3y. Archive all software/input hashes.

Historical U150/X75 are **counts over 1500 s**: U every10 s =360 veh/h, X every20 s =180 veh/h. Preserve those rates, resulting in U300/X150 in the new loading interval.

## Time and stochastic inputs

M/U/X scheduled in [0,3000) s; R in [600,3000) s; run to4200 s. Retain the full history; primary loaded-state window [1200,3000), R-free reference [300,600), and clearance [3000,4200). This is a finite sustained-loading test, not proof of steady-state or universal capacity.

Regular explicit departures at interval3600/q, serialized in milliseconds by floor; require integer cohort counts. Speed factors use a new prospective matched-input realization: UTF-8 `stage6-boundary-v1|{seed}|{class}|{index}`, SHA256 digest converted to big-endian integer, separate Python `random.Random` per vehicle, `gauss(1.0,0.1)` repeatedly until within inclusive[0.2,2.0], ten decimal places. Record Python version. This preserves the specified truncated-normal marginal family while fixing a vehicle's attribute across same-seed demand/treatment variations. It does not reproduce SUMO's historical random stream. SUMO seed also varies and stochastic driving remains enabled. Post-treatment trajectory/RNG divergence is not itself an invalid matched policy comparison; runs/seeds, not seconds or vehicles, are the independent replication units.

## Adaptive search and finite budgets

1. Begin seed17 at qM={2400,3000,3600,4200} veh/h with qR=0. Each has a clear purpose: establish mainline-only range and identify injection limits before attributing problems to ramp flow.
2. At interpretable qM rows, explore qR={600,1200} veh/h. Retain R0 self-congested rows as capacity evidence, but prioritize rows with relatively free R0 for metering opportunities. Do not automatically run an entire Cartesian grid if earlier evidence makes a row uninformative.
3. If no low/high state bracket exists and actual exposure keeps rising, allow one finite extension: qM=4800 and/or qR=1800 (at no more than four additional seed17 cells). If urban/source delivery plateaus, diagnose that constraint instead of repeatedly raising nominal demand.
4. Refine one or two relevant brackets with midpoint steps of150–300 veh/h. Rates must yield integer cohorts. Report a region/interval and nonmonotonicity, not an exact universal capacity.
5. Replicate the useful free/transition/congested neighborhood using seeds17/23/42. If seed results conflict materially, predeclared extra seeds71/101 may be used, maximum five seeds at a cell. Preserve corresponding R0 comparators where needed. Report x/n and individual results, not a precise breakdown probability from n=3–5.
6. Maximum32 uncontrolled starts and8 conditional control/technical starts,40 total; failed starts count. Per-run120s wall/250MB on-disk output; total new raw8GB. One-use input cards, no overwrite, no automatic retry. All failures/anomalies remain in the record. This is an upper bound, not a target sample size.

Each batch has a recorded question, selected cells and stopping decision, with exact input-card release after review. Stop immediately for malformed/missing outputs, changed fixed inputs, unreviewed scientific settings or resource caps; investigate before a separately documented continuation.

## Measurements and integrity

Preserve FCD gzip, lanechanges, tripinfo including unfinished/undeparted, vehroute, summary, TLS states, all existing E1/E2 and queue outputs. Require complete XML, consecutive one-second4200-label FCD, no duplicate IDs per label or interior gaps, lifecycle reconciliation, archived demand and raw SHA256 verification, and explicit reporting of teleports/collisions/unfinished demand. Failures are not silently dropped.

For each class M/R/U/X: requested, actual departed, arrived, unfinished and undeparted counts; external insertion wait; in-network time and scheduled-to-arrival/observation-end time. Report completed trip summaries only alongside censoring. Across different demands, total time differences are not causal policy effects.

Distinguish insertion, first FCD observation on merge edge, actual auxiliary-to-mainline lane change, first downstream observation and arrival. Use half-open intervals, note one-second FCD crossing resolution, retain exact lanechange times. Measure actual arrival profiles, not just requested q. E1 after merge is mixed M/R.

FCD: 100m cells anchored x=0 through2200; two mainline lanes including internal through lanes; exclude auxiliary from mainline population. Retain pooled and continuous lane-track views, absolute speed, M mean model-reference ratio v/(lane limit×explicit vehicle speedFactor), M sample fractions below0.6/0.7/0.8, simultaneous slow-M counts, unique M, direct M and total-mainline density. Thirty-second bins; missing labels invalidate coverage; empty speed is NA. Queue diagnostics cover ramp, internal connectors, shared approach, urban sources and cross approaches; stopped<0.1m/s and slow<5m/s are diagnostics, not automatic spillback proof.

Source backlog after a merge-origin queue reaches the source is a consequence and later censoring, not grounds for discarding the preceding onset. Backlog before near-merge congestion with freely moving downstream source area suggests insertion limitation. Urban signals may cap actual ramp delivery. Record each separately from state classification and examine downstream-first tailback and TLS effects.

## Prospective state classifier (new version, historical rules unchanged)

These are reproducible project screening conventions, not literature-validated traffic constants. Core cells13–17 intersect the merge and through connectors. Use complete half-open30s bins and at least two unique M per cell/bin. Normalize using per-vehicle explicit speedFactor and archived lane limit; call it model-reference ratio, not empirically calibrated free-flow speed.

Profiles P/L/S use alpha0.70/0.80/0.60 and duration3/2/4 consecutive bins respectively. A numerical low bin requires mean ratio<=alpha, at least half M samples<=alpha, and >=15 of30 labels with at least two simultaneously slow M. Follow a fixed cell's maximal consecutive low episode; no bridging gaps or relabeling a later subrun to seek favorable onset references.

A duration-qualified episode has sustained-state support if either (a) the same adjacent pair of cells are low throughout the required3/2/4-bin window and at least one cell is core, or (b) one core cell has M density>=1.25×its fixed reference median in every qualifying bin. Reference [300,600) must have10/10 populated valid bins, every mean ratio>=0.85, and nonzero median density; otherwise density support is unavailable, but spatial support remains possible. Do not substitute different neighboring cell pairs over time. Support/continuation must be reported separately; union simultaneous cell intervals rather than counting them as independent events.

Sustained state and observed onset are separate labels. Observed breakdown additionally needs three populated normal bins (mean ratio>=0.85) immediately before the maximal low episode, plus a reviewed plausible merge-associated origin. Missing pre-onset reference yields sustained state with onset unresolved, not absence of congestion. Capacity drop and remote upstream propagation are not mandatory; pinned persistent congestion is valid if supported.

FREE_FLOW_CANDIDATE requires all60 primary-evaluation bins valid in each core cell13–17, each such cell having at least57/60 bins with mean ratio>=0.85, and no supported L sustained episode in the active[600,3000) window. Audit source/lifecycle/space plots for ongoing queue growth and actual recovery before interpreting the candidate as free flow. Other complete non-sustained results remain TRANSITION_OR_DISTURBED, a heterogeneous residual class that does not itself establish proximity to capacity. Coverage failures are MEASUREMENT_INCOMPLETE. A P-positive numeric result is SUSTAINED_CONGESTION_CANDIDATE pending source/downstream/lane-level review; a P-negative/L-positive point is threshold-sensitive. Always report all P/L/S, actual burden/durations, lane evidence and exclusions; retain active-window early events even if recovered before the primary window.

## Conditional control comparison

Enter only after replicated uncontrolled evidence identifies a near-boundary merge-associated sustained risk with relatively free same-qM R0. Match complete demand XML including explicit vehicle attributes, network/model, seed, windows and outputs; change only the ramp controller/program. Use independent seeds as paired units. Select an ALINEA target from observed downstream occupancy–flow–state evidence, separately from the independent state classifier. Do not adopt an example10% target without evidence. Document controller gain, update interval, bounds and signal actuation before execution.

The installed sumoITScontrol0.1.0 ALINEA assumes a two-phaseG/r program and green-share units; the existing first A_OPEN program has onlyG and B_MODERATE hasG/y/r. Stock invocation is therefore not yet a verified treatment. A new compatible adapter/program requires engineering and science review, bounded technical verification and archived actual TLS/admissions. Exact control parameters must be a separate prospective amendment before control starts. Historical22/28 runs need no repetition unless a specific new mechanism question requires it.

Compare M state/mobility/downstream throughput, R queue/storage exposure and total requested-cohort cost, U/X cost and unfinished demand. A mainline benefit with larger system cost is a valid tradeoff result. Do not claim feasible sweet spot without accounting for all classes and withheld demand.

## Sufficient evidence and closure decision

Exploration may close when integrity and geometry/exposure gates pass and either: (i) a replicated, bounded free-to-sustained region with interpretable origin and at least one usable control comparison has been characterized; or (ii) the finite search identifies a decisive delivery/insertion/model limitation, or no sustained/protectable region in the examined scope, with enough mechanism evidence to specify the next formal design or the precise unresolved blocker. No claim of universally absent sweet spot follows from a finite negative search.

Before further runs, state what unresolved decision they could change. Stop if additional runs merely add similar examples. A closing report must explicitly choose CLOSE_EXPLORATORY_VALIDATION, PARTIAL_WITH_IDENTIFIED_BLOCKER, or OPEN_INSUFFICIENT_EVIDENCE, with independent scientific review, evidence, limitations and handoff.

Formal handoff is a draft, not automatic freeze: select scope and candidate scenarios; fix controller/queue rules; calibrate and separately validate state thresholds and metrics; define independent formal seeds/sample-size precision, windows, exclusions, censoring, pair matching and reproducibility; obtain required user/supervisor decisions; populate and explicitly freeze EXPERIMENT_PROTOCOL before formal runs. Exploratory seeds/results stay labeled exposed design/calibration evidence, not held-out confirmation. Formal performance or sweet-spot claims remain unestablished until that stage.

## Sources for methodological boundaries

- SUMO VehicleInsertion: https://sumo.dlr.de/docs/Simulation/VehicleInsertion.html
- SUMO Randomness: https://sumo.dlr.de/docs/Simulation/Randomness.html
- SUMO vehicle definitions: https://sumo.dlr.de/docs/Definition_of_Vehicles%2C_Vehicle_Types%2C_and_Routes.html
- FHWA Ramp Metering Primer (ALINEA occupancy feedback): https://ops.fhwa.dot.gov/publications/fhwahop14020/sec1.htm
- Historical local screening definition: `docs/methodology/FREEWAY_PROTECTABLE_STATE_EXPLORATORY_DEFINITION.md`; its historical application is preserved, not retroactively rewritten.

# Stage 6 Targeted Causal Validation Report

Status: revision04 final report after scientific review of revision03: PASS, Blocker/Major/required Minor=0/0/0, no must-fix issue. O1 is RESOLVED only for the tested synthetic seed17 condition; O2 NOT_RESOLVED; overall PARTIAL. Stage 6 scientific exit and research applicability remain incomplete. No formal protocol freeze or new simulator start. Current card is exhausted5/5.

## Executive Summary

**Observed:** Candidate acceleration-lane merging works in these seed17 records: A/B each300 native R merges, C252; every observed merge has a native event and valid route/lane evidence. **Calculated:** Strong C raises R/U residence and creates shared-section stopping, but the registered continuous all-stopped meter-connected chain never reaches the shared section. **Interpretation:** Do not call this “no queue/spillback”: the criterion misses connectivity through creeping vehicles. Multiple freeway indicators do not support the intended protection pattern. Final scoped reviewer disposition: O1 RESOLVED only for the tested synthetic seed17 condition; O2 NOT_RESOLVED; overall PARTIAL. Stage 6 scientific exit and research applicability remain incomplete. Strict storage_cross=0 is valid for its registered definition; mixed stop/creep queue propagation is not adjudicated. Shared-section R→U following obstruction is observed as a candidate; the specific junction/priority/internal-blocking cause remains unknown.

Confidence: High for exact parsed events/accounting/registered criterion results; Moderate for mechanism interpretation; Unknown for unobserved subsecond dynamics and generalization to other seeds/demands.

## Priority diagnosis update — registered spillback versus shared/internal blocking

Revision03 integrated two independent engineering forensic records, retained unchanged in this revision04 final status update: [C junction/queue trace](../../artifacts/stage6_targeted_validation_20260920_v1/engineering/runtime_audits/TV_C_S17_junction_queue_forensics_revision01.json) SHA `4b1ac602f0d964adc5d7359830380ea06b23b538551322c82552ce2141b542bc`, and [A/B/C merge/terminal audit](../../artifacts/stage6_targeted_validation_20260920_v1/engineering/runtime_audits/TV_ABC_merge_and_terminal_forensics_revision01.json) SHA `fc3714c9ee3295c90d9f8ec2f74ea0c8d0cd5d4c25cdf09afc27baab266cf707`. They corroborate the independent data calculations; neither is substituted for raw XML analysis. Numeric tables and figures are byte-identical copies of revision02. No numerical result or threshold has changed; the scoped final reviewer disposition is recorded in revision04.

1. **Where are the54 unfinished vehicles?** Observed status is at2700; positions are latest FCD2699. R252–279 (28) are in ramp_storage; R280–290 (11) in :urban_diverge_1_0; R291–299 (9) in shared_approach. All48 R are upstream of the meter, none in freeway merge/auxiliary section. U145–149 are on shared; U144 is on urban_out at32.09m,11.27m/s. The appendix and54-row table give every ID/route/lane/position. None is classified as arrived or assigned zero delay.
2. **Is there one connected stopped queue?** No under the registered conjunction. The overall vehicle footprint extends from R252 front s316.57 (1m before meter) to R299 rear s−130.99, but intermediate creeping vehicles interrupt the all-stopped component. Maximum registered extent238.16m occurs at1740: R190 internalpos84.41/v0.07 ends it; R191 internalpos76.81/v0.21 follows at2.60m gap. This is a speed-rule break, not a large void. At2699 the corresponding break is R280→R281,2.73m gap,v0.09→0.15. No detector or coordinate correction is needed to obtain the strict result.
3. **Does the sensing support317.57m?** The forward reference is113.08m internal plus204.49m ramp_storage, from shared downstream endpoint to meter stopline. E2 coverage is separately204.49m ramp_storage and238.80m shared; the113.08m internal is not covered by E2, but is observed and mapped in FCD. E2 lengths cannot be added to prove a continuous317.57m queue. Nor could an E2 zero alone disprove crossing: coverage, aggregation and stopping criteria differ. Actual C E2 maxima are nonzero. The10m gap rule is applied at recorded1cm coordinate precision; a10.01m reported gap is only1cm above threshold, with approximately1cm combined coordinate quantization width. Preserve the classification without portraying it as a robustly large separation.
4. **Did R first block U, and is this a junction fault?** First shared stoppedR71 is at400 (399,400],pos232.81,v0.06,behind internalR70pos9.03/v0:reported gap10.02m,then about10.01m. U36 becomes stopped behind R72 at403 (402,403],sharedpos217.78/v0.07;R72pos225.31/v0.01. These onset brackets are ordered, with urbanTLS Gr and rampTLS r. However moving R farther downstream prevent proven continuous meter-anchored all-stopped linkage. The strict storage-crossing event is missing, so its order relative to U effect remains unidentified, not imputed. Compiled urban_diverge has no TLS, legal route connections, and requests with response/foes=`00`; no conflicting-priority fault is established. R71 subsequently moves shared→internal within(413,414], rejecting a permanently unreachable route interpretation. The observed shared/internal entry-region blocking is a **candidate** mechanism; it is not proven malformed priority, a large-gap artifact, or a demonstrated unrelated downstream exit obstruction.
5. **Answer A versus B and the minimum next evidence.** A (registered meter-connected ramp-storage spillback) is not established. B (shared/internal stopping with local R→U following obstruction) is observed as a candidate; its specific cause is not isolated. This does not disprove physical queue propagation through creeping vehicles, nor prove an independent junction defect. Existing1Hz FCD/native events cannot directly report SUMO's selected leader/conflict reason or exact subsecond ordering. First specify and review a dynamic creeping-queue linkage definition using existing records, retaining the old strict result. Only if that still leaves the mechanism unidentified, propose a separately approved bounded diagnostic logging actual leaderID/gap, junction blocking/conflict reason and selected TLS around the observed onset; preserve original scientific inputs, classify logger changes as instrumentation, and repeat logger neutrality if needed. No run or new parameter choice is authorized here.

**Merge-specific corroboration:** A/B/C nativeR aux0→lane1 counts300/300/252, all tagged `strategic|urgent`; positions0.48–181.44/0.65–197.83/0.02–162.00m are before auxiliary end294.51m. M does not stop below0.1 in the inspected merge domains, but observed minimum M speeds are10.97/3.61/5.43m/s. Consequently “no stop” is not “no disturbance.” One B/C example has R0 merge at75s,pos71.04 while M26 follows on the same lane at6.92m gap and changes speed29.37→24.87m/s. This is concurrent merge/following interaction, not a causal decomposition proving forced priority yielding. Engineering finds no invalid transition/route and provides compiled nonconflicting merge evidence; realism and generalized absence of artifacts remain unproven.

Confidence: High for identities,positions,compiled semantics and exact registered labels; Unknown for the specific internal blocking reason or forced-yield attribution. One seed, C censoring and all failed analysis versions remain explicit.

## Priority diagnostic: C's54 unfinished vehicles and what storage_cross=0 means

**Observed:** At simulation termination2700, C has48 R+6 U unfinished. Positions at2700 were not recorded: the last FCD positions are at2699. The complete54-row identity/lane/edge/position/speed/route/status list is [C_terminal_positions.csv](../../results/tables/stage6_targeted_validation_20260920_v1/revision03/C_terminal_positions.csv), with an abbreviated position table in the appendix. Unfinished is not undeparted: all1858 planned vehicles eventually entered, but some entered after1500. No arrival or zero-delay value is invented.

|Class|Last observed lane|Count|
|---|---|---:|
|R|ramp_storage_0|28|
|R|:urban_diverge_1_0|11|
|R|shared_approach_0|9|
|U|shared_approach_0|5|
|U|urban_out_0|1|

**Calculated coordinate mapping:** s increases in the driving direction. shared_approach occupies[-238.80,0]; :urban_diverge_1_0 occupies[0,113.08]; ramp_storage occupies[113.08,317.57]. The meter stopline is s317.57. The81.98m ramp_mid internal lane lies downstream, [317.57,399.55], and is excluded from upstream storage. Thus317.57m is a path-length reference from shared's downstream endpoint to meter; it is not calibrated vehicle capacity and is not the sole ramp_storage lane length204.49m.

**Observed at2699:** The front of the related53-vehicle upstream path population is R252 at ramp_storage pos203.49/s316.57,1m before meter. The last is R299 on shared pos112.81/s−125.99, rear−130.99. One other U is already on urban_out. This population is spatially extended into shared, but it is not a single fully stopped connected component. [Terminal map](../../results/figures/stage6_targeted_validation_20260920_v1/revision03/C_terminal_spatial.png) separates stopped and creeping/moving vehicles.

**Why the registered component stops:** At2699 its tail is R280, internal pos106.30/speed0.09. The next R281 is internal pos98.57/speed0.15, bumper gap2.73m. The speed rule `<0.1` breaks the chain, despite a short gap. At1740 the analogous break is R190 speed0.07 → R191 speed0.21, gap2.60m. At400 it breaks in ramp_storage at R50 speed0.06 → R51 speed0.50, gap2.59m. These are directly recorded facts, not a large-gap hypothesis. See [every selected chain break](../../results/tables/stage6_targeted_validation_20260920_v1/revision03/C_meter_chain_breaks.csv).

**Coverage check:** E2 shared detector covers shared_approach_0[0,238.80]; ramp E2 covers ramp_storage_0[0,204.49]. The113.08m internal connector is outside these two E2 detectors but is included in the independent FCD path mapping and all chain calculations. Both detectors emit90 complete30s intervals. E2 speedThreshold1.3888888888888888m/s,timeThreshold1s,jamThreshold10m differ from the registered all-stopped FCD threshold0.1m/s. Therefore E2 jam and FCD strict component are different measurements. C maximum E2 jam204.12m(storage) and233.92m(shared) are not inconsistent with strict storage_cross=0. Integer-centimetre rerun rules out binary floating-point threshold artifacts; results unchanged.

**Interpretation:** `storage_cross=0` is valid for the registered simultaneous all-stopped connected-component definition. It does not establish that traffic queues failed to reach shared. A genuine mixed stopping/creeping queue footprint and U following R are observed; no malformed junction priority or unrelated exit blockage is established by these observations. Do not label this “junction artifact” merely because strict continuity fails. Current data do not adjudicate a more general dynamic spillback definition; that would require a separately specified analysis definition, not silent threshold relaxation.

## 1. Question

Can this fixed geometry support (O1) normal ramp merging and (O2) an exploratory chain from increased ramp restriction to freeway protection, upstream queue, finite-storage crossing and additional U harm? This is a bounded diagnostic intervention, not ALINEA evaluation, optimal-control search or formal thesis experiment.

## 2. Prior Evidence

The accepted earlier RV4 pair had300 R downstream observations, but local M travel-time measurement difference crossed0 and U additional delay was not causally localized. Its `specific_obstacle=NOT_RESOLVED` remains historical evidence. Source: [prior paired report](../../data/processed/stage6_obstacle_20260913_v1/runtime_gate_revision02/revision04/paired_seed17_comparison01/REPORT.md). The present task is separate, with5new starts; no old quota reset.

## 3. Candidate Geometry

Compiled network SHA887c232483f0c68dc024334ff5997250d7d36299ab2744bdcf49d5a314c700ca. Auxiliary lane294.51m; same-edge native left merge to freeway. Mainline lanes and geometry retained. Meter is native ramp_mid TLS; downstream internal connector81.98m is not upstream storage. Passenger-right restriction on merge_section_1 is retained and affects merged R as well as M. See the bound [runtime contract](../../artifacts/stage6_targeted_validation_20260920_v1/engineering/RUNTIME_CONTRACT.md).

## 4. Instrumentation and definitions

All actual XML independently parsed: FCD/summary/queues1Hz, both TLS1Hz,9E1+2E2 detectors30s, tripinfo/vehroute and native lanechanges (18roles in ON/A/B/C,17OFF). Native gaps `None` remainNA. Vehicle5m is the verified sole-passenger software default; no empirical length calibration or runtime TraCI read claimed.

FCD stop `<0.1m/s`; meter anchor stopped R within10m; add only actual adjacent stopped vehicles with bumper gap≤10m, retaining U and breaking on any moving intermediate. No persistence threshold is added. Episodes report sample count and first-to-last observed span; first onset and first count-increase are distinct. Coordinates are integer centimetres for gap/anchor comparisons. Event time brackets use adjacent1s samples; overlapping event brackets imply temporal_order_unidentified.

Trip-level restricted system time is min(arrival,2700)−reported scheduled time, with scheduled time reconstructed as depart−departDelay for inserted vehicles. This is reported-schedule reconstruction, not independently proven exogenous number-flow timestamps. All vehicles in these runs entered; a never-inserted case with unknown schedule would beNA. Recorded waiting/timeLoss for unfinished vehicles are accumulated-to-cutoff outputs, not final values. Completed-only duration is separately labelled and cannot stand in for all-cohort travel time.

## 5. Technical Troubleshooting and analysis versions

No SUMO failure in this new five-start card. Retain prior task failures in their own ledger. The first ON analysis13/14FAIL incorrectly omitted legal lateral moves on straight internal edges; corrected revision02 passed and was independently reviewed. Initial neutrality receipt failed only because identity-manifest attempt_id differed; every17 common output already matched, and explicit metadata handling was reviewed. No traffic behavior changed.

Final-analysis revision01 is preserved. Revision02 uses exact integer-centimetre chain-boundary arithmetic to eliminate possible floating-point10m errors; complete rerun yielded identical aggregate findings. C native-event lifecycle guard was made explicit for arrival<0 (unfinished): a recorded event before2700 is valid; no arrival is invented. All frozen gates remain unchanged. Full lineage is in source/delivery manifests.

## 6. Final Technical Smoke

ON/OFF each passed14gates and physical suitability, with final independent review.17common XML semantic streams match exactly, preserving event order and all traffic attributes. Only comments,format whitespace and summary/step@duration computation time are excluded. Smoke pair provides instrumentation neutrality for this B/S17 fixture; it is not two scientific replicates.

## 7. Scientific Run Matrix

A/B/C share qMain3200(nominal;1333/1500s=3199.2),qRamp720,qUrban360,qX180,seed17,demand0–1500,run0–2700,step1. Programs: A60G; B22G/3y/35r; C12G/3y/45r,offset0. Timing tiers are not calibrated discharge rates; yellow can permit passage. Full matrix: [run_matrix.csv](../../results/tables/stage6_targeted_validation_20260920_v1/revision03/run_matrix.csv).

## 8. Data Quality and Censoring

All three runs pass14technical gates and physical suitability from raw files. All1858 planned IDs exist; all eventually inserted. M1333/X75 all arrived everywhere. A/B allR300/U150 arrived. C R252/300 andU144/150 arrived; remaining48R+6U explicitly retained. By1500, C only221R and111U entered; no claim of equal realized network demand over time. All original output manifests and source hashes verified. No collision/teleport/discarded/emergency-braking event recorded.

## 9. O1 Merge Audit

**Observed:** A/B/C native ramp merges300/300/252; all observed R merges have legal auxiliary-to-main transition, route and same-label FCD destination. Merge position ranges A0.48–181.44m, B0.65–197.83m, C0.02–162.00m on294.51m section. Mean positions62.37/68.77/42.25m are descriptive, not design targets. Exact [merge_events.csv](../../results/tables/stage6_targeted_validation_20260920_v1/revision03/merge_events.csv) includes all native changes and explicit R_merge classification; representative trajectories available separately.

A/B have71/70 mergedR lacking an aux1Hz sample. C has129 of252 mergedR lacking an aux sample; total177 includes48not-yet-merged unfinished R. Do not interpret177 as ambiguous completed merge events. Native logs supply events but not continuous trajectories. No M samples speed<0.1 anywhere; no observed stopped mainline bottleneck can be localized. Slower-moving congestion is not ruled out; no posthoc breakdown threshold is invented. Priority-artifact assessment requires engineering compiled-request and runtime evidence; successful arrivals alone are insufficient. Final review accepts O1 only within the tested synthetic seed17 condition, without a universal claim or resolution of the remaining urban mechanism.

## 10. Freeway Comparison

[Aligned speed/flow/occupancy figure](../../results/figures/stage6_targeted_validation_20260920_v1/revision03/freeway_ABC_timeseries.png); [M-only domain data](../../results/tables/stage6_targeted_validation_20260920_v1/revision03/M_domains_30s.csv).

|Calculated metric|A|B|C|
|---|---:|---:|---:|
|M full-route duration mean,s (all1333)|73.4591|74.2236|73.7667|
|M recorded timeLoss mean,s|9.7148|10.4799|10.0317|
|M observed stopped vehicle-seconds (<0.1)|0|0|0|
|Upstream E1 speed,300–1500,m/s|28.8404|28.5710|28.4806|
|Downstream E1 speed,300–1500,m/s|27.7976|27.7478|27.7442|
|Upstream lane occupancy mean,%|7.7853|7.8469|7.8975|
|Downstream lane occupancy mean,%|9.9425|9.8373|9.0794|
|Downstream E1 completed passages,300–1500|1315|1301|1189|
|Unique first-downstream M,300–1500|1071|1071|1071|
|Unique first-downstream R,300–1500|241|227|115|

E1 station mixes classes downstream and is passage-based; its denominator is30s bin completed contributions. Speed is contribution-weighted; occupancy averages two lanes equally then time bins equally. Values are not identity throughputs. M local main_up1200→main_down200 all1333 measurement bounds: A[24.2311,26.2311],B[24.7592,26.7592],C[24.3241,26.3241]s. Thus B−A[−1.4719,+2.5281], C−A[−1.9070,+2.0930]s; these are crossing measurement bounds, not CIs.

**Interpretation:** No multiple-direction consistent freeway-protection pattern. Lower C downstream occupancy/flow accompanies reduced R passage; M completed throughput is unchanged. This cannot be called freeway improvement from speed alone, and does not indicate mainline M starvation. Capacity drop and congestion duration remain unestablished under an accepted congestion definition.

## 11. Ramp Queue

[Queue figure](../../results/figures/stage6_targeted_validation_20260920_v1/revision03/ramp_queue_storage.png), [every frame](../../results/tables/stage6_targeted_validation_20260920_v1/revision03/frames_1s.csv), [actual members](../../results/tables/stage6_targeted_validation_20260920_v1/revision03/queue_members.csv).

|Calculated|A|B|C|
|---|---:|---:|---:|
|Max anchored extent,m|0|148.58|238.16|
|Max anchored vehicles|0|19|31|
|Max all-network stoppedR|2|21|54|
|Nonempty anchored episodes|0|27|45|
|Anchored sample count|0|868|1998|
|Longest observed span,s|0|36|47|
|Strict shared-crossing samples|0|0|0|

B/C first anchored onset(38,39]; first observed increase from nonempty component(45,46]. No additional sustained-growth criterion was registered; do not invent one after seeing results. `queue_growth` episode rows denote registered component existence and are accompanied by separate first-count-increase output. The317.57m line is geometric; zero crossings does not negate separately observed downstream-to-shared stopping/creeping footprint.

## 12. Urban U

[Urban figure](../../results/figures/stage6_targeted_validation_20260920_v1/revision03/urban_U_impact.png); [per-vehicle outcomes](../../results/tables/stage6_targeted_validation_20260920_v1/revision03/vehicle_metrics.csv); [matched differences](../../results/tables/stage6_targeted_validation_20260920_v1/revision03/matched_vehicle_contrasts.csv).

|Calculated mean over all150plannedU,s|A|B|C|
|---|---:|---:|---:|
|Restricted system time|67.2133|67.2267|556.2800|
|Recorded waitingTime|0.6667|0.6667|112.9400|
|Recorded timeLoss|11.6624|11.6828|275.0491|
|External insertion wait|0|0|212.4133|
|In-network restricted residence|67.2133|67.2267|343.8667|

C−A restricted difference489.0667s is not a pure spillback delay estimate:212.4133s average is external insertion waiting,276.6533s is in-network restricted residence difference, and6U are unfinished. C completed-only mean340.625s uses144vehicles and is unsuitable as whole-cohort answer. Full-duration upper bound remains unbounded for unfinishedU. C R restricted mean855.5367s includes210.74s average external waiting;48R unfinished. External backlog maximum79R/39U at sampled30s endpoints; it is a separate consequence/measurement, not network spillback itself.

## 13. Causal Timeline and spatial linkage

C evidence from [snapshots](../../results/tables/stage6_targeted_validation_20260920_v1/revision03/C_representative_snapshots.csv), [front links](../../results/tables/stage6_targeted_validation_20260920_v1/revision03/U_front_links.csv), [episodes](../../results/tables/stage6_targeted_validation_20260920_v1/revision03/spillback_events.csv):

|Event|1s onset bracket|Meaning|
|Meter-anchored stopped component|(38,39]|Observed component,not yet growth trend|
|First nonempty count increase|(45,46]|Observed increase,not formal persistence|
|First stoppedR on shared|(399,400]|R71,pos232.81,speed0.06;not meter-connected component|
|First U blocked-candidate chain|(402,403]|U36,pos217.78,speed0.07→R72,pos225.31,speed0.01;gap2.53m|
|Strict storage crossing/shared-obstruction-potential|NA|Registered component criterion never met|
|Causal additional U-impact onset|Unidentified|Candidate stopping has timestamp; causal increment not a single observed event|

R shared stop precedes the specific U candidate stop in disjoint brackets. Both have urbanTLS Gr and rampTLS r; U is on shared downstream of the urban signal. At402 U36 still moves0.29m/s while R72 already0.02. This supports a local R→U following obstruction observation, not the full registered meter-to-shared all-stopped chain.114distinctU have some such stopped-front-chain candidate;2262time labels contain at least one. A/B have none by the same definition. Storage crossing and its defined shared-obstruction event would be the same spatial event, not two independent ordered successes. Where brackets overlap or events are missing, preserve temporal_order_unidentified.

## 14. Counterfactual Comparison

All conditions retain network/demand/seed and vary only meter program. Same-seed is not proof of identical micro-random streams after trajectory changes. B raises R restricted residence while U remains approximately unchanged; C creates prolonged R/U impacts and delayed insertion. However mainline indicators fail the intended protection leg, and strict storage-crossing definition is unmet. Thus the complete registered O2 chain cannot be accepted. Local sharedR/U obstruction is consistent with a restriction-related mechanism in this synthetic matched diagnostic, but no formal causal estimate or malformed-junction diagnosis follows.

## 15. Seed Replication

No seed23 run. Three scientific-condition runs, one seed each; two technical logger fixtures are not replications. No p-value or confidence interval. The optional follow-up family is not executable under this exhausted card.

## 16. Limitations

1Hz may skip short auxiliary/internal observations. Native lanechange events are discrete simulation events,not empirical trajectories. C truncation leaves54unfinished; finished-only averaging biases comparisons. All schedules are reported reconstructions. Exact strict all-stopped connectivity can fragment creeping queues; do not quietly raise speed/gap thresholds. E2 covers two lanes and has different jam rules. No formal congestion definition,calibrated capacity,capacity-drop measurement or general model validation. Five figures visually checked against derived data; raw reconciliation recomputes class means/counts independently. Source insertion materially changes realized exposure in C. Bounds/NA are retained,not filled with zeros.

## 17. Final scoped scientific disposition

`O1_MERGE_GEOMETRY = RESOLVED` **only for the tested synthetic seed17 condition**, as recorded in the final reviewer disposition. This is not general validation across seeds, demands or all junction mechanisms.

`O2_FREEWAY_URBAN_TRADEOFF = NOT_RESOLVED`: absent consistent freeway protection and unmet strict crossing chain. This does not mean no shared-urban queue or no U harm.

`SPECIFIC_OBSTACLE_OVERALL = PARTIAL`. **Stage 6 scientific exit and research applicability remain incomplete.** The formal protocol remains unfrozen. Review PASS accepts this bounded analysis and disposition; it does not imply O2 completion or formal-experiment readiness.

## 18. Recommended Next Step

**Recommendation A: bring this bounded evidence and explicit design questions to Robert.** Final internal scientific review has passed; no communication is sent by this report. Do not start formal experiments or tune qMain/timing to chase a positive result. The near-term zero-run work is to discuss whether a dynamic stopping/creeping spillback definition is scientifically appropriate, then preregister any new analysis before applying it; retain the original strict result. Existing FCD/native/TLS/identity records suffice for that discussion. If a later approved validation needs finer causal linkage, minimally log vehicle leader IDs/gaps and junction waiting/conflict state at the registered event locations, preserving controller/demand and using an explicit budget; do not automatically execute. Mainline challenge level and acceptable U exposure/clearance require design decisions before formal protocol.

## Artifacts, versions and verification

Authoritative final package is [final_analysis_revision04](../../data/processed/stage6_targeted_validation_20260920_v1/final_analysis_revision04/source_manifest.json); numerical computation remains revision02, with revisions01–03 retained unchanged. The complete revision03 report is preserved in `final_analysis_revision04/archive/STAGE6_TARGETED_CAUSAL_VALIDATION_REPORT_revision03.md` with SHA `743c1b3cdbee501c64f4b0a0c1bf6bdb1347853c3256ce8da7f8d97837416056`. The prior report bytes are archived at `final_analysis_revision03/archive/STAGE6_TARGETED_CAUSAL_VALIDATION_REPORT_revision02.md` (SHA `9a680ef5654abba38fdd835fdf4bdb7188f594fbe8174b0af16c86e1f10f89b8`). Required tables: [run_matrix](../../results/tables/stage6_targeted_validation_20260920_v1/revision03/run_matrix.csv),[merge_events](../../results/tables/stage6_targeted_validation_20260920_v1/revision03/merge_events.csv),[spillback_events](../../results/tables/stage6_targeted_validation_20260920_v1/revision03/spillback_events.csv). Five figures (PNG+PDF): [merge_behavior](../../results/figures/stage6_targeted_validation_20260920_v1/revision03/merge_behavior.png),[freeway_ABC_timeseries](../../results/figures/stage6_targeted_validation_20260920_v1/revision03/freeway_ABC_timeseries.png),[ramp_queue_storage](../../results/figures/stage6_targeted_validation_20260920_v1/revision03/ramp_queue_storage.png),[urban_U_impact](../../results/figures/stage6_targeted_validation_20260920_v1/revision03/urban_U_impact.png),[ABC_summary](../../results/figures/stage6_targeted_validation_20260920_v1/revision03/ABC_summary.png);additional [C_terminal_spatial](../../results/figures/stage6_targeted_validation_20260920_v1/revision03/C_terminal_spatial.png). Scripts/tests/commands/hashes in final manifests. No new simulator calls or raw modifications by analysis. Final scientific review is recorded separately from the analyst's self-checks in the [disposition receipt](../../data/processed/stage6_targeted_validation_20260920_v1/final_analysis_revision04/final_reviewer_disposition_receipt.json). The receipt transcribes the parent-reported findings and does not invent reviewer identity.

## Appendix: all54 unfinished last positions

Position timestamp2699; status unfinished at2700 for every row. R route `urban_in shared_approach ramp_storage ramp_accel merge_section main_down`; U route `urban_in shared_approach urban_out`. Internal lanes occur between those external route edges.

|ID|Class|Last lane|Position,m|Speed,m/s|Path s,m|
|---|---|---|---:|---:|---:|
|R_flow.252|R|ramp_storage_0|203.49|0.0|316.57|
|R_flow.253|R|ramp_storage_0|195.99|0.0|309.07|
|R_flow.254|R|ramp_storage_0|188.49|0.0|301.57|
|R_flow.255|R|ramp_storage_0|180.99|0.0|294.07|
|R_flow.256|R|ramp_storage_0|173.48|0.0|286.56|
|R_flow.257|R|ramp_storage_0|165.98|0.0|279.06|
|R_flow.258|R|ramp_storage_0|158.48|0.0|271.56|
|R_flow.259|R|ramp_storage_0|150.98|0.0|264.06|
|R_flow.260|R|ramp_storage_0|143.48|0.0|256.56|
|R_flow.261|R|ramp_storage_0|135.98|0.0|249.06|
|R_flow.262|R|ramp_storage_0|128.48|0.0|241.56|
|R_flow.263|R|ramp_storage_0|120.98|0.0|234.06|
|R_flow.264|R|ramp_storage_0|113.48|0.0|226.56|
|R_flow.265|R|ramp_storage_0|105.98|0.0|219.06|
|R_flow.266|R|ramp_storage_0|98.47|0.0|211.55|
|R_flow.267|R|ramp_storage_0|90.97|0.0|204.05|
|R_flow.268|R|ramp_storage_0|83.47|0.0|196.55|
|R_flow.269|R|ramp_storage_0|75.97|0.0|189.05|
|R_flow.270|R|ramp_storage_0|68.47|0.0|181.55|
|R_flow.271|R|ramp_storage_0|60.97|0.0|174.05|
|R_flow.272|R|ramp_storage_0|53.47|0.0|166.55|
|R_flow.273|R|ramp_storage_0|45.97|0.0|159.05|
|R_flow.274|R|ramp_storage_0|38.47|0.0|151.55|
|R_flow.275|R|ramp_storage_0|30.96|0.0|144.04|
|R_flow.276|R|ramp_storage_0|23.46|0.0|136.54|
|R_flow.277|R|ramp_storage_0|15.95|0.02|129.03|
|R_flow.278|R|ramp_storage_0|8.43|0.04|121.51|
|R_flow.279|R|ramp_storage_0|0.87|0.06|113.95|
|R_flow.280|R|:urban_diverge_1_0|106.3|0.09|106.3|
|R_flow.281|R|:urban_diverge_1_0|98.57|0.15|98.57|
|R_flow.282|R|:urban_diverge_1_0|90.83|0.12|90.83|
|R_flow.283|R|:urban_diverge_1_0|83.13|0.75|83.13|
|R_flow.284|R|:urban_diverge_1_0|74.43|0.51|74.43|
|R_flow.285|R|:urban_diverge_1_0|65.91|1.12|65.91|
|R_flow.286|R|:urban_diverge_1_0|57.12|3.3|57.12|
|R_flow.287|R|:urban_diverge_1_0|44.92|4.02|44.92|
|R_flow.288|R|:urban_diverge_1_0|32.16|3.79|32.16|
|R_flow.289|R|:urban_diverge_1_0|18.58|5.87|18.58|
|R_flow.290|R|:urban_diverge_1_0|2.16|7.31|2.16|
|R_flow.291|R|shared_approach_0|211.59|3.96|-27.21|
|R_flow.292|R|shared_approach_0|199.31|2.58|-39.49|
|R_flow.293|R|shared_approach_0|180.67|0.19|-58.13|
|R_flow.294|R|shared_approach_0|172.95|0.05|-65.85|
|R_flow.295|R|shared_approach_0|157.83|0.01|-80.97|
|R_flow.296|R|shared_approach_0|150.32|0.0|-88.48|
|R_flow.297|R|shared_approach_0|135.31|0.0|-103.49|
|R_flow.298|R|shared_approach_0|127.81|0.0|-110.99|
|R_flow.299|R|shared_approach_0|112.81|0.0|-125.99|
|U_flow.144|U|urban_out_0|32.09|11.27|NA:off ramp path|
|U_flow.145|U|shared_approach_0|225.16|5.39|-13.64|
|U_flow.146|U|shared_approach_0|189.03|0.78|-49.77|
|U_flow.147|U|shared_approach_0|165.38|0.05|-73.42|
|U_flow.148|U|shared_approach_0|142.81|0.0|-95.99|
|U_flow.149|U|shared_approach_0|120.31|0.0|-118.49|

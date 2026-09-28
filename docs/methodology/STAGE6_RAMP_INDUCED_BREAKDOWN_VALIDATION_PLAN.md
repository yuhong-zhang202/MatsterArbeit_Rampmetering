# Stage 6 — Minimal Ramp-Induced Breakdown Validation Design

Status: **EXPLORATORY DESIGN PROPOSAL — NOT AUTHORIZED FOR EXECUTION**

Date: 2026-09-22. This document proposes observations, not executable inputs or a launch card. No historical authorization carries forward. All numbers introduced here are PROJECT OPERATIONALIZATION unless explicitly described as verified historical inputs. P/S/L, Candidate A/C, spatial mapping, population/density gates and reference selection rules remain unchanged.

## 1. Executive conclusion

Propose one seed17 pair at constant qMain=3350.4 veh/h: a no-R freeway control with unchanged urban background, followed conditionally by an always-open transition with R demand beginning at 540 s at 720 veh/h. First establish a fixed high-mobility PRE, then test whether actual R arrival precedes sustained collective M deterioration while the no-R control remains high-mobility at corresponding times. **This is a test of R-admission-associated deterioration, not proof of pure merging friction or a formal physical breakdown threshold.**

3350.4 as first candidate: **PARTIALLY** supported; useful pressure context and clean historical demand realization, but neither M-alone stability nor near-criticality is established. Preferred budget two starts; hard ceiling four over at most two qMain candidates, each separately approved. No automatic progression, retries or seed23 starts.

## 2. Correct causal mechanism

The intended chain remains R admission → merge-associated freeway deterioration → moderate control potentially protects freeway → stronger restriction potentially increases R queues/internal/shared obstruction and U harm. Every arrow remains a hypothesis to test. Failure to demonstrate ramp-induced deterioration in historical A is an evidential gap, not an identified physical cause of all O2 failures.

Two-arm identification estimates the total effect of admitting R under this synthetic network, including additional total freeway volume, interactions, and urban-TLS-mediated arrival patterns. It does **not** isolate lane-changing friction from added demand, or prove a general causal law from one seed. A constant-total-flow alternative would be another experiment and is not proposed here.

## 3. Why qMain-only localization was insufficient; source reconstruction

Raising M until M itself deteriorates would not establish an R-triggered mechanism. Historical A0/M3350 both admitted R from t=0 and do not supply a no-R counterfactual or this delayed-onset PRE.

| Verified input | A0 | Historical M3350 |
|---|---:|---:|
| M scheduled / exact rate | 1333 / 3199.2 veh/h | 1396 / 3350.4 veh/h |
| R scheduled / rate | 300 / 720 | 300 / 720 |
| U scheduled / rate | 150 / 360 | 150 / 360 |
| X scheduled / rate | 75 / 180 | 75 / 180 |
| All demand / simulation | [0,1500) / [0,2700) s | same |
| Step / seed | 1 s / 17 | same |

Bound source directories:

- A0: `artifacts/stage6_targeted_validation_20260920_v1/engineering/inputs/TV_A_S17_attempt1/`.
- M3350: `artifacts/stage6_baseline_localization_20260921_v1/LOC_M3350_S17/engineering/inputs/LOC_M3350_S17_attempt1/`.
- Network: `artifacts/stage6_baseline_localization_20260921_v1/LOC_M3350_S17/engineering/build_attempts/TV_BUILD01/network.net.xml`, SHA-256 `887c232483f0c68dc024334ff5997250d7d36299ab2744bdcf49d5a314c700ca` (both accepted inputs identical).
- A0 demand SHA-256 `70d90d477c97141086b87cd248064c2c27c5965060e04fe9a2cbec67ec20e1cd`; M3350 demand `e64057692b4194b6f395c7a5349104a407d806b2b5a6bda9efcbac29489fdac3`.
- Locked method: `docs/methodology/FREEWAY_PROTECTABLE_STATE_EXPLORATORY_DEFINITION.md`, SHA-256 `22fe22170c17ce74e261e717586a458a1b5173e9deabbee925bd4c1d606adfe7`.
- A0 application/decomposition: `data/processed/stage6_protectable_state_application_20260921_v1/REPORT.md` and `data/processed/stage6_A_P_failure_decomposition_20260921_v1/REPORT.md`.
- M3350 ledger/audit: `data/processed/stage6_baseline_localization_20260921_v1/LOC_M3350_S17_attempt1/`; review: `artifacts/stage6_baseline_localization_20260921_v1/LOC_M3350_S17/postrun_reviews/`.
- Reference specification: `docs/methodology/MAINLINE_REFERENCE_SELECTION_SPEC.md`; library v2 and offset analysis: `data/processed/stage6_mainline_reference_library_20260922_v2/` and `data/processed/stage6_3350_reference_offset_20260922_v1/`.

A0 has zero qualifying P and short L/C disturbances. M3350 has complete M/R/U/X insertion and arrival (1396/300/150/75), but P onset-reference unresolved, S no qualifying event, L unresolved, C warnings and no Candidate A. Historical terminal remains LOCALIZATION_NOT_EVALUABLE; G5 unresolved and G6 not evaluable for release. Zero unfinished vehicles is not urban-safety proof.

Reference counts 82 A0 and 38 M3350 are accepted **cell-periods**, not independent experiments or network-wide normal seconds. The screen has 22×16=352 pooled candidates per run, 704 across two runs. Durations 7380/3420 are cell-seconds. C episodes of 30–180 s do not by themselves prove every bin jointly has sustained low speed and elevated density.

Source limitation: the prior offset script's pooled `ref_for(c,-99,...)` lookup and missing explicit target-support enforcement require a separate audit before its pooled-availability or exact offsets support new decisions. Prior PASS records do not remove this limitation. No historical products are repaired or reclassified in this design. We use raw-based classifier context and verified lifecycle facts, not revision03 supplemental metrics or those exact offsets, to motivate the first candidate.

## 4. Transition options

**Recommend delayed R demand.** No R exists before activation, no deliberately stored release queue, and A_OPEN stays unchanged. It remains an artificial demand step and changes R total count/time profile; natural platoons from the existing urban TLS remain possible. It does not guarantee smooth merge flow or known arrival time.

Reject initial red then release for this test: it introduces stored queue, release shock and possible pre-treatment urban harm, conflating admission with queue discharge. This is not a ban on later metering experiments.

## 5. Recommended design and frozen technical context

M/U/X start0 and end1500; empty initialization; simulation ends2700. Pair1 M1396, U150, X75. Control has R0 throughout. Transition has R192 in [540,1500): 192×3600/960=720 veh/h, R0 beforehand. Retaining R300 in this shorter interval would incorrectly impose1125 veh/h.

Preserve accepted network, 1 s step, passenger type/behavior defaults, M departPos100 and other existing departure semantics, outputs, urban TLS and A_OPEN. Urban TLS is60 s (45 Gr,3 yr,9 rG,3 ry), offset0; ramp A_OPEN is a single60 s G phase selected from t0. No controller, speedFactor distribution, Krauß/LC parameter or detector redesign is proposed. Existing E1 period30, FCD1Hz, tripinfo/vehroute/summary/queue/lanechange/TLS outputs remain required.

## 6. qMain candidates and bounded adaptation

Pair1 uses3350.4 because the accepted historical realization shows greater disturbance context without failed insertion, making the M-alone counterfactual informative. This is not a capacity estimate or an endorsement based on already having run it. Confidence in candidate informativeness Moderate; success Unknown.

MAX_QMAIN_CANDIDATES=2. Conditional Pair2 uses only3199.2 (M1333), a150-ish veh/h downward step (exact151.2, about4.5%) to the accepted A0 demand semantics. It is eligible for consideration **only after F1 confirms sustained no-R deterioration**, not merely a missing PRE observation or C warning. No upward candidate is designed. F2/F3/F4/F5 stop and require scientific reassessment; they do not release Pair2. Even after F1, Pair2 requires new user approval and fresh exact cards. These bounds are design conventions, not literature-derived thresholds.

## 7. PRE-state definition

Fixed PRE=[360,540), six consecutive30 s bins, two complete90 s reference blocks. Duration180 s is PROJECT OPERATIONALIZATION: two existing reference blocks, three urban60 s cycles, and multiple historical M traversal times; not a physical stabilization constant. Evaluate both arms independently, without moving the window after seeing data.

For every merge-core cell13–17, require both physical through lanes and pooled observations to pass the existing numerical reference screen in both blocks: complete samples, at least two unique M vehicles in every constituent lane/bin, normalized sample-mean M speed≥0.85, finite positive M and M+R density with actual lane lengths, no P/S/L/A/C overlap or adjacent-cell disturbance, and the specification's conservative first-disturbance restriction. Earlier disqualifying disturbance cannot be erased by selecting a later quiet PRE. Report all failures. The two-ID minimum is an observability gate, not evidence of near-capacity load.

Substantial M exposure additionally requires the planned high M demand to be realized: enumerate M inserted, unique M passages into core and through each lane, upstream counts, and delays for PRE and each post bin. No blocked-source absence can be called free flow. Demand integrity gate below and populated lane bins are required; no unapproved throughput cutoff is invented.

There is no established numerical critical density. Here 'acceptable density' means valid, physically mapped, nonzero density accompanying the high-mobility/no-disturbance screen; report its distribution without claiming density below capacity. External-bank comparison must obey unchanged same-cell/lane density/population/composition support checks; unsupported comparisons remain UNKNOWN and cannot veto or validate the direct PRE by themselves.

The old bank's input whitelist covers historical R720 runs. New R0 PRE is **not automatically an accepted member of that bank**. This design proposes reuse of its unchanged numerical screen for direct PRE verification, not modification of the stored bank or its rules. A future approved implementation must explicitly bind new run inputs and test this reuse separately. PRE is a screened high-mobility state, not independently established physical normality.

## 8. Activation and chronology

R generation starts540, aligned to the existing60 s urban cycle; it does not imply merge arrival at540. Historical first20 M scheduled-to-x≥1400 passage median41 s/max48 s in3350; corresponding R median50/max58 s. These are historical travel observations, not predictions for delayed onset. PRE begins far later but must still pass empirically.

Source-active R duration960 s; clearance1200 s. Record all [0,2700) data. Fixed primary sustained-exposure observation=[720,1440), leaving early onset and final-demand bins visible as separate diagnostics. No adverse event outside this window is suppressed; success eligibility below includes qualifying post-arrival episodes before1500. If sustained R exposure has not been established by720, mark observation-plan failure F5 rather than sliding the window.

| Marker | Exact reporting rule |
|---|---|
| T0 | PRE gate confirmed at540; its observed interval is[360,540), not a discovered steady-state onset |
| T1 | scheduled R source activation540; report first actual insertion separately |
| T2 | first R entry to merge auxiliary, with 1Hz interval bounds; report first actual through-lane entry/lanechange separately |
| T3 | first three consecutive complete30 s bins after T2 with positive observed unique R auxiliary-entry counts; report through-lane entry counts too |
| T4 | first post-T2 locked C or stronger M event, retaining earlier warnings rather than overwriting them |
| T5 | locked P low-run start and later confirmation separately; reference/attribution-unresolved candidates are not P-positive |
| T6 | locked spatial propagation and recovery markers, or UNKNOWN; clearance-only recovery identified explicitly |

T3 is an exposure-persistence convention, not proof of a720 veh/h realized merge rate. Report all R counts, gaps and per-cycle flow. Confirm ongoing R entry during the qualifying event, not only earlier T3. A repeated warning without complete population/speed/density/persistence gates cannot substitute for P.

Missing auxiliary-lane samples are not zero entries. Infer route-consistent auxiliary-entry boundary crossings from preceding/following FCD positions and lanechange records; retain an interval between bounding labels rather than inventing an exact timestamp. For every30 s bin report certain entries (the complete inferred crossing interval lies within the bin) and possible entries (the interval overlaps it). At edges use half-open bins and retain interval censoring. T3 passes only if the three bins each have positive certain counts; if only possible counts could satisfy T3 by720, return F5 rather than absent exposure. Missing route/trajectory bounds make exposure UNKNOWN. Apply the same interval logic to R-before-M ordering and ongoing exposure during a P episode. Do not double-count one crossing as certain in multiple bins.

Also report the first R downstream passage, defined as first entry into `main_down`, with vehicle ID and 1Hz bounding interval; retain UNKNOWN if no route-consistent crossing can be reconstructed. Include this alongside requested/scheduled/actual insertion, insertion delay, auxiliary/through-lane entries and unfinished counts in the lifecycle/timeline outputs.

Any decline before R can physically reach merge undermines the proposed sequence. Require high-mobility/no-warning evidence from540 through the last complete bin wholly before T2; inspect the boundary bin at1Hz, without changing classifier bins. If event start and T2 share an unresolved bin, order is UNKNOWN unless raw trajectories resolve it. Do not equate first auxiliary entry with exact lateral merge.

## 9. Matched M-only control

Keep U/X and TLS: 'M-only' refers to freeway demand, not removal of urban background. Same M/U/X IDs, schedules, routes, types, explicit attributes, network and outputs; only R source profile differs. Run and audit the control first. Only a suitable control may be submitted for separate transition-card approval.

Same seed17 does not guarantee identical per-vehicle random draws after changing demand. Compare M/U/X realized speedFactors and pre-R FCD/insertion/lane traces; record mismatches. Future cards must specify a tested matching method without silently changing the behavior model. Unexplained pre-R divergence prevents strong mechanism attribution (F5); do not call an unmatched realization a strict paired counterfactual.

For conservative 'control stays high-mobility', require the same lane/pooled numerical screen and absence of disqualifying disturbances in all fixed90 s blocks [540,1440), plus report[1440,1500) bins and the full horizon. Any sustained control deterioration gives F1. An isolated failed screen without sustained deterioration gives F5, not automatic 'qMain too high'. No favorable-time matching after outcome inspection.

## 10. Success criteria and application outputs

Report two separate statuses:

**MECHANISM_SUPPORTED_EXPLORATORY** requires: both PRE pass; control stays screened high-mobility; actual sustained R merge exposure established; at least one fully qualifying locked P episode in core13–17 starts after physically resolved R arrival and confirms before1500; original immediately preceding local90 s reference, density/population and attribution gates pass; no pre-R deterioration; event exposure persists; downstream-origin tailback, source artifacts and direct TLS/geometry causes are excluded. PRE or control must never replace P's exact local onset reference. Require exact-time control context also for any eligible episode outside[720,1440). An event beginning within the primary window but confirming after1500 is descriptive only for this gate.

Report speed (absolute/normalized), M and M+R density, unique/simultaneous populations, cell/lane, P/S/L/A/C, onset and confirmation, duration, E1 occupancy/flow, M-only downstream passages, M travel time/timeLoss, recovery and propagation. S and spatial A strengthen evidence but are not compulsory. Capacity drop/discharge is supporting, never necessary. L/C-only deterioration is an informative failure to meet this P-based success gate, not 'nothing happened'. P-positive is an exploratory label, not formal physical proof.

**BASELINE_SUITABILITY_PASS** additionally requires complete raw/provenance audit, independently reconciled M/R/U/X lifecycle ledger, good realized demand, no serious source or geometry/TLS artifact, interpretable observation window and non-overloaded urban baseline. Only both statuses yield BASELINE_MECHANISM_CANDIDATE, never a formal thesis baseline or O2 resolution.

Demand gate (new conservative PROJECT OPERATIONALIZATION): every scheduled vehicle inserted within its prescribed source-active interval; zero never-inserted/after-demand-inserted vehicles; zero unfinished at2700; identities reconcile independently across scheduled/inserted/arrived/unfinished records. Report class-specific delay distributions, phase counts, source backlog and core-arrival flux. This strict screen can reject a physically interesting case. A ledger PASS is necessary but not sufficient: a material insertion bottleneck or upstream starvation still vetoes acceptance. If materiality cannot be resolved from outputs, F5; no invented 'approved' delay tolerance.

## 11. Failure branches — every branch STOP

| Branch | Evidence and interpretation | Action |
|---|---|---|
| F1 | sustained collective deterioration in no-R control; source/geometry causes first assessed | unsuitable M background for isolation; consider separately approved lower Pair2 only if genuine no-R deterioration established |
| F2 | valid control/PRE/exposure; transition remains screened high-mobility | chosen R admission did not induce qualifying deterioration in this realization; not proof qMain physically too low |
| F3 | valid comparison but only short/L/C or non-P deterioration | boundary/sensitivity evidence, mechanism success not established; no threshold relaxation |
| F4 | freeway deterioration but urban/source overload compromises baseline, including urban failure before deterioration | separate possible mechanism signal from unsuitable baseline; reject candidate |
| F5 | missing data/reference, inadequate exposure, unmatched PRE, ordering or attribution unresolved | NOT_EVALUABLE; no demand release |

Adjudication order: technical/data/matching limitations F5 first; valid no-R sustained impairment F1; inspect transition urban suitability F4; fully evaluable outcomes then success/F2/F3. Preserve secondary flags, do not hide urban failure behind another branch. All outcomes including success terminate this design's progression; no automatic B/C or repeat seed.

## 12. Ramp/urban safety

For both runs and matched absolute windows report R storage queue, internal/shared R occupancy, stopped-queue connectivity, storage_cross, direct location/time-consistent R→U obstruction, U travel/system time and insertion delays, class counts and unfinished R/U. Mere R occupancy or R-ahead/U-stopped coincidence is not proof of obstructive spillback.

Conservative candidate veto: any independently established stopped R storage-crossing chain linked to U obstruction, network gridlock, or unresolved source-limited throughput. This zero-confirmed-obstructive-spillback veto is PROJECT OPERATIONALIZATION, deliberately stricter than an unapproved severity threshold. Urban degradation without established linkage must still be reported; unexplained material deterioration yields suitability NOT_EVALUABLE, not PASS. No numeric 'severe U delay' criterion is presently approved.

Existing historical G6 was not established. Future output adequacy for direct obstruction must be verified before card approval; unavailable evidence remains UNKNOWN. No new runtime observer is implicitly authorized here. If existing output cannot resolve G6, mechanism evidence may still be described but BASELINE_MECHANISM_CANDIDATE is withheld.

## 13. Seeds

Seed17 first minimizes nominal changes, not stochastic confounding. If successful, recommend a complete independent seed23 pair under later authorization: transition-only repetition cannot establish whether that seed's M-alone control was stable. Two seeds still do not estimate breakdown probability reliably. Seed23 is outside the four-start design ceiling and requires a separately defined budget, not an automatic fifth/sixth run.

## 14. Budget

Preferred: two new starts, or stop after one unsuitable control. Hard ceiling: four starts across at most two qMain pairs; technical retries0; each consumed failure counts. No start is authorized now. Historical3350 ran24.293463 wallclock seconds with26,679,773 output bytes; rough two-run compute50 s/output53 MB and four-run100 s/107 MB are planning anchors only. Conservative planning allowance five minutes/150 MB preferred and ten minutes/300 MB ceiling; analysis/review time additional. Exceeding runtime/storage allowance triggers review, not extra scientific starts. Do not invent assured performance for changed traffic.

## 15. Proposed non-executable matrix

Machine-readable file: `results/tables/stage6_ramp_induced_design_20260922_v1/PROPOSED_RAMP_INDUCED_BREAKDOWN_MATRIX.csv`.

| Order | Pair | Condition | qMain | R before/after540 | seed | Eligibility |
|---|---|---|---:|---:|---:|---|
| 1 | RI3350 | no-R control |3350.4|0/0|17|new exact-card approval |
| 2 | RI3350 | delayed R open |3350.4|0/720|17|control audit suitable plus separate approval |
| 3 | RI3199 | no-R control |3199.2|0/0|17|only confirmed F1, reassessment and new approval |
| 4 | RI3199 | delayed R open |3199.2|0/720|17|Pair2 control suitable plus separate approval |

Rows3–4 are conditional alternatives, not queued work. Every run ends with raw/lifecycle/classifier/engineering/data/scientific reviews before any release decision. Proposed rows contain no command, executable route/config or authorization token.

## 16. How B/C follow

Only after supported mechanism plus suitability and separate approval, propose A/B/C using **identical delayed R time profile, M/U/X, seed and observation windows**, differing in meter policy. A=open tests repeat deterioration; B=moderate tests freeway benefit with tolerable R/U cost; C=stronger tests protection and increased internal/shared spillback/U harm. These are hypotheses; stronger restriction need not protect freeway. No gain, occupancy target, cycles or override chosen. Returning to constant demand would require a separate justification/validation, not reuse this transient pair as an interchangeable baseline. Sweet spot remains freeway benefit versus ramp/urban cost, not a new thesis topic.

## 17. Limitations and confidence

High: recovered demand arithmetic, network identity, historical lifecycle and absence of approved new starts. Moderate: delayed-source design is cleaner than stored red-release for this bounded question; timing offers usable observation if empirical gates pass. Unknown: M-alone stability, P transition, causal attribution, urban suitability and reproducibility. Added volume and merge interaction remain inseparable here. Step forcing, stochastic draws, urban platooning, stringent PRE/urban screens and30 s onset resolution may prevent success. A negative or NOT_EVALUABLE result is acceptable; no threshold or demand chasing.

Scientific-source use is limited to the already reviewed project operational framework and recorded supervisor guidance. No real-road70 km/h/5 min rule, critical density or capacity-drop necessity is imported. The formal protocol remains empty/unfrozen and unchanged; Stage6 PARTIAL, O2 NOT_RESOLVED. No SUMO/netconvert/TraCI, geometry/classifier/raw changes or formal baseline selection occurs in this task.

## 18. Later supervisor confirmation and implementation prerequisites

Ask Robert later, not contact now: whether delayed-demand transient diagnostics adequately prepare the intended steady demand backbone; interpretation of added volume versus merging friction; sufficiency of screened PRE and local P reference; stochastic replication and matching; role of capacity-drop analysis; urban suitability tolerances and output sufficiency. Existing guidance supports simple synthetic scenarios, defaults, insertion verification and near-breakdown exploration; it does not approve this exact timing or candidate.

Before future card creation: approve this design explicitly; resolve/test matching and reference-screen reuse; verify direct urban-evidence coverage; bind all actual inputs/software/output schema and immutable method hashes; define fail-closed checks without revising scientific thresholds. New requests changing those decisions require review. Approval of this proposal alone is not authorization to launch.

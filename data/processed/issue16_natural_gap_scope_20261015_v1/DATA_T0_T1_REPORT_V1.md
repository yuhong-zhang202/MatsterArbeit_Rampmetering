# Issue16 bounded terminal-frame evidence V1

**Observed existing hard-rule trigger verified; native motion responsibility is not identified by the POST query alone.** This report supplies T0/T1 measurements, not authority to relax a safety rule or run SUMO. Scientific T1 choice must use the engineering official-source mechanism review. The old650 STOP/NOT_QUALIFIED and frozen-reader UNKNOWN remain unchanged.

## Context and scope

Reviewed AGENTS, PROJECT_STATE (current top plus assigned161–320 in full), DECISIONS, empty0-byte EXPERIMENT_PROTOCOL, WORKLOG (assigned1001–2000 in full, plus recent native work), problem_records index, entire artifacts/issue16_natural_gap_scope_20261015_v1/ISSUE16_SOURCE.md and prior data/scientific native postreview. Some long tool outputs were truncated and affected sections reread in smaller ranges. Formal protocol is unfrozen; this is exploratory technical evidence. Current work is one bounded existing-raw investigation under Issue16. Prior unique card b73/sourceb6/run01 stopped650;83.637436041s settled,816.362563959s balance supplies no new start. PR13 REVIEW_PENDING/NO_VERDICT, no repeat request; PR15 baseline af988faddaa271ac2a8f80fe3fd3558ff2898618 supplied by root. No Git/native/environment/reader tests or source changes were performed by this analyst.

Allowed output only this new processed directory. Existing raw, cards, readers, inputs, rules, old failed outputs and binders remain untouched. No repeat227-file audit; previous full hash validation is explicitly reused at its original scope. This extraction reads only the relevant existing JSONL streams, FCD/TLS endpoint frames and actual prepared demand/network. Raw is not modified.

## Finite evidence table

Rows below use simulation time in seconds, speed in m/s, lane path position/gap in metres. FCD label648 represents post-step ACK649 and label649 represents ACK650 in this actual bound output, independently matched to retained journals; labels are not relabelled as raw650.

|Actual frame|R0 lane/position/speed|R1 lane/position/speed|Signal and observation|
|---|---|---|---|
|PRE648|storage200.706334658 /6.089874891|storage167.553200752 /17.078004000|I12_PACKET9/r, nextSwitch649, frontR0, receiverAVAILABLE/internalempty|
|POST649=PRE649|storage202.296209549 /1.589874891|storage180.324798762 /12.771598010|Previous red motion648..649; then setter programI12_PACKET8/phase0 at649, actual readbackG nextSwitch653|
|POST650|internal :ramp_mid_0_0 pos1.740238864 /3.934029315|storage189.119744925 /8.794946163|G motion649..650; R0 first crosses; storage front changes toR1; POSTreceiver denied|

Raw fields and exact line references are saved in TERMINAL_FRAMES_V1.json. For both vehicles, identity_journal at648/649/650 records type technical_passenger, same R_route, speedMode31/laneChangeMode1621, accel2.6, normal decel4.5, emergencyDecel9, tau1, actionStep1, sigma0.5, maxSpeed55.5555555556. Query independently records vehicle length5/minGap2.5 and lane/path positions. Materialized vType XML itself declares only id/vClass; carFollowModel is not explicitly assigned there. The raw identity record explicitly scopes itself as bound input/model rather than observed private native branch. Actual native motion CF function inputs, influencing leader set, chosen branch and leaderDecel passed to that private branch are NOT_RECORDED. Official default-model/source inference belongs to the separately version-bound engineering review, not a direct raw observation.

## Distance and query binding

PRE649 R1 current_following already contains fresh getLeader(R1,478.67)=[R0,14.47141078710817], actual follower speed12.771598010037966, leader1.5898748913376206, getSecureGap leaderMaxDecel9, leaderIDR0, result24.814794030113898; deficit−10.343383243005729. R1 does not cross in this step. PREreceiver selects frontR0/internalempty and returnsREADY; its separate R0 entry query is CLEAR_WITHIN_OBSERVED_LOOKAHEAD. The existence of a R1 failed query before motion is recorded; it is not a checked R1 admission decision or a claim that native motion was unsafe.

POST650 frontR1 query is fresh, uses follower8.794946163265283, leaderR0 speed3.9340293150224332, leaderMaxDecel9 and leaderIDR0. getLeader gap excluding follower minGap9.610493938865318; getSecureGap13.089892326530567; exact deficit−3.479398387665249. Physical front-to-leader-rear bumper gap =204.49−189.11974492544257+1.7402388643078837−5 =12.110493938865318. Subtract follower minGap2.5 gives9.610493938865318, matching query units; these are route-path gaps, not Euclidean chord distances. R0 internal rear =1.7402388643078837−5=−3.2597611356921163 spans the line; it is not a new red front entry.

The separate original prospective receiver record reports secure_gap20.68483848979585 rather than13.089892326530567. It must not be conflated with the fresh current query; its arguments/role are assessed in engineering. No parameter was substituted to make either query pass. Extra1.1m is advisory, not this hard-failure cause. All values are same observed time650; no sub-step ordering/time is logged. The current_following function checks getTime==time_s before reading; no native monotonic per-getter call trace or private CF motion-call trace exists.

## Responsibility chain and limits

Owning current source src/candidate_a_natural_service_20261015/adapter.py imports current_following/classify_receiver from src/candidate_a_dynamic_minqual_20261015/receiver_wait.py. After a650 ACK it binds actual signal/entry and ledger accounting, then observes postreceiver. Only when prepared motion isG, the postreceiver classification must beREADY/WAIT or POST_CURRENT_GAP_BOUND_DENIED is appended. Separate actual-entry checks run for R0, which has before/after bounded-clear records; R1 remains behind the line and is not the actual-entry vehicle. The source chain and raw therefore support a *role change*: R1's current-following denial existed in PRE649 as a noncrossing follower record, then became operative atPOST650 when R0 moved internal and R1 became storage front. This is not a newly demonstrated bad gap created solely by green switching.

649→650 actual R1 acceleration−3.9766518467726826 and R0+2.3441544236848126 reconcile their speed differences. The previous648→649 red motion has R0−4.5/R1−4.306405990071887. Signal readbacks/journal at649 are program/phase setters, no setSpeed or vehicle braking command recorded in these scoped identity rows (setter_calls0). No next step, next setter650 or R1 crossing is present. Counterfactual continuation, native private followSpeed actual input/timing, emergency response and future internal tail clearance remain unknown. Thus POSTgetSecureGap(actual POSTspeeds,leaderEmergency9) is not evidence of the exact query performed internally before649→650 movement.

Local648..650 counters show0 collision/teleport and no excess beyond existing4.5m/s² normal braking bound; prior accepted full-prefix report separately found the same over0..650. The retained local yellow witness failure and safety qualification limits remain; no no-warning/no-collision fact proves the actuation harmless. Relevant controller risks include changingG/y/r with moving followers, R0 body spanning controlled internal, receiving space and fresh/complete population queries. Native ordinary motion also has model-specific braking/distance assumptions, which this observation cannot verify counterfactually. Scientific review must distinguish controlling signal responsibility from a normal moving follower's post-state diagnostic reference.

## Assigned historical reading and authority conflicts

WORKLOG1001–2000 covers09-13 qualifiednegative,09-19–20 build/runtime recovery,09-21 measurement/O2,09-22 references,09-23–25 matching/T3,09-26 models/fixedtiming and memory, through10-02 boundary-search transition. STATE161–320 retains many corresponding older snapshots and old technical/memory environments.

1. Sep19 “until successful output” and Sep24 boundedautonomous recovery authorized particular old build/technical conditions only. They cannot license Issue16 reruns or consume its remaining numeric balance. Historical5/5 run cards remain exhausted; new Issue16 exact authority governs.
2. Old dated “current Stage6PARTIAL/formaldesignlocked/noALINEA” paragraphs are historical against D018 and the current native top summary, not competing current research state. Old90s/60MB,120s/100MB and model-sensitive cards do not replace the separate900 scope.
3. D009 literal E1-T3 rule conflicted with physical per-vehicle crossing evidence; D010 explicitly adopted a retrospective clarification while preserving oldNOT_EVALUABLE. This supports preserving distinctions between a rule-trigger fact, a physical-event fact and authority to change a contract; it is not automatic permission to relax a safety obligation.
4. Sep26 sigma0 sensitivity was explicitly altered-model and not spliceable with default evidence; it cannot authorize current vehicle-model/decel changes. Historical source/pairability and FCD timestamp bugs were corrected with old evidence preserved, underscoring exactframe/role/version binding here.
5. Historical missing memory/Docker/context and generated-memory inaccuracies are auxiliary history; current files/raw prevail. No memory operation is needed or authorized in this data task.

No unresolved historical authority conflict prevents the assigned read-only investigation. Uncertainty about real safety relevance remains substantive and is left for source-informed engineering/scientific judgement, not filled from history.

## Commands, outputs and impact

`.venv/bin/python data/processed/issue16_natural_gap_scope_20261015_v1/extract_terminal_frames_v1.py` exit0, tool measured0.8s. It streamed existing files, retained only the specified frames/IDs, independently asserted route-coordinate gap equality and actual sameframe speed/query arguments. No synthetic fixture, native executable or fullhistorical analysis was run. One subsequent display-only command used required key `reasons` on a legal earlier row without it and failed KeyError; using `.get` displayed the optional absence correctly, with no analysis output/source change. This inspection failure is logged in INSPECTION_NOTE_V1.txt.

Outputs: extraction script, TERMINAL_FRAMES_V1.json, this report and source/data binding. root owns minimal PROJECT_STATE/WORKLOG/Issue/PR updates. Engineering report cross-check is pending; no T1 scientific verdict is claimed here.

## Bounded engineering-source cross-check

Engineering supplied official v1_26_0 annotated tag de3c3f37a2908397bc398a2bfe3b98232252ba8f pointing to commit fa7df22d7f1c4ae245192ecc32410a49f1ffb2a3. Independently read its saved MSCFModel.cpp77–98/168–184, Krauss.cppfollowSpeed and MSVehicle.cppgetCurrentApparentDecel. Conditional on that source Euler formula/dt1, brakeGap = n*v−b*n*(n+1)/2+v*tau, n=int(v/b). Both recorded query results independently reproduce exactly with followernormal4.5/tau1. In these two frames leader speeds1.589875/3.934029 are below both4.5 and9, so tau0 leader brakeGap is0 with either leaderMaxDecel. Pure diagnostic comparison9→4.5 therefore leaves both same query deficits; this is not a proposed parameter change or native motion replay. QUERY_MATH_CROSSCHECK_V1.json records the inputs/results. Command crosscheck_query_math_v1.py exits0 (tool0.1s).

Actual649→650 path displacements equal post-speed*dt1 for both vehicles (R1 8.79494616326527m; R0 3.934029315022423m), supporting an Euler-consistent observed step. Actual cfg has dt1 and no explicit step-method.ballistic item; absence alone is not an observation of the native private update flag. No internal native followSpeed call trace was acquired. Therefore the official distinction between a POST secureGap reference and a next-speed control calculation is compatible with this raw, while actual pervehicle native influencing branch remains unknown. This closes only the requested key-parameter cross-check; no other data analysis is needed.

Reader plan is separately proposed in READER_MINIMAL_PLAN_V1.md; runtime safety contract unchanged. Parent may reconcile source/mechanism and scientific T1 verdict before authorizing any local implementation.

# Dynamic actuator minimum qualification — native report, 2026-10-15

**Current verdict: dynamic tracking NOT_DEMONSTRATED; real ALINEA NOT_RUN.** The single authorized native run stopped before a yellow step at1236, not at approved1296. The approved current-following change operated as specified, but another unchanged local yellow witness blocked continuation. This is a bounded technical result; no formal experiment, global safety/service qualification or Stage6/A1 decision is made. Final scientific postreview permits delivery of this verified stopped prefix only; it does not permit retry or ALINEA.

## Goal and exact scope

Track original cumulative ALINEA requests C with independent physical releases N, rather than merely mapped/applied commands or program exit. Direct human approval “批准，请继续” is preserved in [USER_APPROVAL_V1](../../artifacts/dynamic_minimum_qualification_20261015_v1/USER_APPROVAL_V1.json). Only the current-following check changes: the same bound native-query floor remains hard, extra1.1m is advisory with its old strict failure retained. Strict new-G/prospective, other safety/coverage/UNKNOWN checks, vehicle models, original cumulative selector/Producer/Feedback, phase catalogue and formal design remain unchanged.

Engineering implementation→independent data→readonly science passed the offline exact gate. Card classification compatibility and a missing imported yellow-helper hash were corrected before native; all earlier cards/preimages/failures remain versioned. [V3 engineering](../../artifacts/dynamic_minimum_qualification_20261015_v1/engineering/implementation_revision03/ENGINEERING_REVIEW_V3.md), [V3 data](../../data/processed/dynamic_minimum_qualification_20261015_v1/implementation_v3/FINAL_CARD_REVIEW_V3.md), [prestart science](../../artifacts/dynamic_minimum_qualification_20261015_v1/SCIENCE_PRESTART_REVIEW_V3.md). Focused synthetic/schema tests do not establish physical service or safety.

## Exact execution

- Run: `UA_NATIVEGAP_DYNAMIC_S17_01`; M3600/R900/U360/X180 demand, seed17, step1s, control activation1200. Metering requests300at1200→750at1201→900at1226→300at1237; these are control requests, not demand changes.
- Executed source commit `f14aa49cb4a4dbb4168999e0bb543e7442d9c3f8`; all141 card-bound Git blobs match. Historical card baselineee59840 is distinct from actual execution commit.
- V3 Dynamic cardSHA `4afd7e4fb7b39b87ec7d4033840293eef15b45e732c0a2285aca17dcc4283d13`; common141source digest `dfdddab74a862903ba75b3c8a4a9a7953e827cee6f049dc086f2bcb5fccb3cc7`; canonical release `5a3072cd1946c61339207cb96edf97c0b663e5abdc549ec3464ae58a39372695`.
- One CLI74492/SUMO74499, session42647. Connected24.56895s; actual monitored throughcleanup163.07205774995964s<300. CLIexit1/nativeexit0: orderly native shutdown preserves diagnostic STOP, not PASS.
- LastACK/accounted1236; `UNKNOWN_LOCAL_YELLOW_SCOPE` before thirdpacket first-Y movement. No resource trigger. Original end1296 retained in card, but not reached. No retry or ALINEA start.
- Frozen191rawfiles403265825bytes; manifestSHA `f64eca9ba38189361b79d3b8f91b9c81cd258bac11babbbe6cf2a8f9ae7d37ed`. Raw stays read-only under `data/raw/dynamic_minimum_qualification_20261015_v1/UA_NATIVEGAP_DYNAMIC_S17_01/`; this local raw is not uploaded.

[Engineering postreview](../../artifacts/dynamic_minimum_qualification_20261015_v1/engineering/native_execution_v1/UA_NATIVEGAP_DYNAMIC_S17_01/POST_ENGINEERING_REVIEW_V1.md), [manifest](../../artifacts/dynamic_minimum_qualification_20261015_v1/engineering/native_execution_v1/UA_NATIVEGAP_DYNAMIC_S17_01/RAW_FINAL_SHA256_V1.json), [local commit readback](../../artifacts/dynamic_minimum_qualification_20261015_v1/LOCAL_IMPLEMENTATION_COMMIT_READBACK_V1.json). Actual launch command/environment/source/input snapshot references are in the receipts/card, without rerunning native version checks.

## Independent actual accounting

The exact bound full reader ran **once**, exit1 with finalresult `STOP_OBSERVED_ALARM` because runtime_stop=true. It reached final return, not a parser crash; missing_or_unknown=[] and observed_alarms=[]. The failed prospective yellow witness is preserved separately. Source/input/inventory hashes, dualACK/FCD/TLS continuity, actual entries/counters, identity/model pools, bodies, terminal arrivals and four native-log EOF were checked. [Actual data review](../../data/processed/dynamic_minimum_qualification_20261015_v1/native_dynamic_v1/DATA_NATIVE_POSTREVIEW_V1.md), [receipt](../../data/processed/dynamic_minimum_qualification_20261015_v1/native_dynamic_v1/ACTUAL_AUDIT_RECEIPT_V1.json), [summary](../../data/processed/dynamic_minimum_qualification_20261015_v1/native_dynamic_v1/PREFIX_SUMMARY_V1.json).

| Observed support | Packet / phase exposure | Actual N | Complete E | Interpretation |
|---|---|---:|---:|---|
|1200–1224|T24: G4/Y5/r15|2|2|Complete packet; original request changed inside it|
|1224–1232|T8: G4/Y2/r2|2|2|Complete packet|
|1232–1236|PlannedT8; onlyG4 observed|1|0 eligible complete quota|Partial; y/r counts null, not measuredzero; future quota unobserved|

Whole observed control prefix[1200,1236): **original C=187/24=7.7916667veh, applied-command integral5veh, complete E4veh, actual N5veh, C−N=67/24=2.7916667veh**. E−N=−1 is a support difference: the real partial-packet entry is counted inN but not completeE. AppliedC=N5 is not success against originalC. Boundary residual decomposition remains in the independent summary; no instantaneouszero or fabricated percentage tolerance.

Three original commands are genuinely ACK/TLS bound:1200→1200delay0s,1201→1224delay23s,1226→1232delay6s. Fourthrequest1237 was **not reached/requested/applied**, not merely pending. Final300 debt recovery and full horizon are unobserved, so ALINEA continuation fails its gate. All5 actual entries were green and rear-clear;1299 normal arrivals passed last-motion audit; no bodycensor. Observed minimum acceleration/speed difference−4.5m/s², nativeeventcountermax0. These finite observations do not establish future safety. FinalAFTER nonactive pools remain single-journal without nextPRE.

## What was solved and what stopped this run

At1233 R5→R4 gap2.0951522156549345m versus query1.022884125080513m: hardfloorPASS. Legacy+1.1requires2.122884125080513m and fails by0.02773190942557857m; fully retained as advisory. Two records are post/nextpre of the **same frame**, not two independent incidents. No below-query result or other alarm was suppressed. Raw command ACKs now persist for all observed applications; the historical missingACK gap was not backfilled or reclassified.

At1236, original yellow precheck binds38 local IDs, one rejectedR5: distance0.146160014m, speed4.973246722m/s, length5m, normaldecel4.5m/s², actionStep1s, chosenY2. Fields exist; this is a failed sufficient witness, not missing data. Original policy computes stopdistance v·dt+v²/(2b)=7.721378161m>d; one-stepstop v≤b·dt also fails. Clear-time expression dt+v/(2b)+L/v=2.557962408s>2. Separate clearance inequality d+L≤v·(Y−dt) fails by0.172913293m.

This expression includes one action step plus an engineering braking-time allowance. It is **not measured clearance time or a proven worst-case following envelope**. Constant-speed(d+L)/v≈1.03477s is also only a counterfactual estimate. First-Y native motion was never executed; neither actual danger nor actual safety has been established. The original STOP is retained under the unchanged contract. [Bound yellow failure](../../artifacts/dynamic_minimum_qualification_20261015_v1/engineering/native_execution_v1/UA_NATIVEGAP_DYNAMIC_S17_01/YELLOW_STOP_INPUT_DETAIL_V1.json), [independent formula/input audit](../../data/processed/dynamic_minimum_qualification_20261015_v1/native_dynamic_v1/YELLOW_STOP_SUPPORT_V1.json).

Pinned official SUMO1.26 [MSVehicle.cpp3711–3727](https://github.com/eclipse-sumo/sumo/blob/fa7df22d7f1c4ae245192ecc32410a49f1ffb2a3/src/microsim/MSVehicle.cpp#L3711-L3727) handles yellowwaiting with native brakeGap/canBrake, stopline/ignoreRed state; [MSCFModel.cpp76–98](https://github.com/eclipse-sumo/sumo/blob/fa7df22d7f1c4ae245192ecc32410a49f1ffb2a3/src/microsim/cfmodels/MSCFModel.cpp#L76-L98) defines selected discreteEuler braking behavior. These are not the project's clearance expression. Private branch/stopoffset and rejected future motion remain unobserved; source/binary/compiler equivalence is not proven.

## Handoff: concrete boundary, not another tuning loop

Confirmed: scoped advisory and durable event logging operated on real records; originalC/N and three applications independently reconstruct. **Not demonstrated:** complete four-request dynamic tracking, final300 recovery, realALINEA, global safety/service, formal readiness. Existing oldSTOP3/FAIL/750/900 implementations remain distinct. Stage6 closure and A1UNRESOLVED unchanged.

**Proposed next decision, not execution authorization:** review whether native yellow stop/commit responsibility plus retained observed-safety monitoring can replace this separate local sufficient witness in another explicitly bounded contract. No newA1 proof, broad testmatrix or threshold tuned to0.173m/2.558s. Do not simply replace the formula with constant-speedPASS. Keeping this hard witness leaves the encountered state ineligible; substituting longer minimum periods changes physical service capacity (two cars per9s=800veh/h), so it cannot be sold as an unchanged300–900 tracking repair. No such change is implemented.

The unused conditional ALINEA card remains unreleased; unused resource is not authority for another Dynamic. No automaticretry or new simulation is proposed as an already-approved action. Required next owner: user/Chat for yellow responsibility decision; Codex may implement only the resulting explicit scope.

## Final three-role disposition and resources

Engineering→data→readonly science completed. [Science actual review](../../artifacts/dynamic_minimum_qualification_20261015_v1/SCIENCE_NATIVE_POSTREVIEW_V1.md): GO_FOR_VERIFIED_STOPPED_PREFIX_EVIDENCE_DELIVERY_ONLY. No new evidence-delivery Blocker/Major; applicability remains unresolved. [Resource-only settlement](../../artifacts/dynamic_minimum_qualification_20261015_v1/engineering/settlements/UA_NATIVEGAP_DYNAMIC_S17_01/SETTLEMENT.json) records163.07205775s/403265825B; fresh accountingverified no unsettledidentity and436.92794225s mathematical remainder in new600. Neither remainder nor settlement releases anotherDynamic or conditionalALINEA. Old147.815s/401074259B is a separate unchanged stage.

Documentation impact: PROJECT_STATE and WORKLOG updated for actualstop, reviews and nextdecision; this newreport preserves traceable implementation/actualresults. DECISIONS, formalprotocol, supervision, AGENTS and thesisstructure unchanged. README usage unchanged. Originalraw/FAIL/STOP3 and unrelatedMemoryCore/privatechanges preserved. Local implementation checkpointf14aa49 is verified; GitHub upload is not claimed by this report.

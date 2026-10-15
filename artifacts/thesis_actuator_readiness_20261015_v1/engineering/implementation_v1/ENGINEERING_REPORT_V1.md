# Natural-service implementation: offline engineering handoff

Status: IMPLEMENTED_OFFLINE / NOT_NATIVE_TESTED / NOT_QUALIFIED. No SUMO launch, TraCI connection, run card, numeric budget approval, release, commit or push was performed. The latest user instruction again prohibits SUMO and merging; this report complies.

## Context and bounded change

Repeated Context Preflight reviewed AGENTS, STATE, DECISIONS, recent WORKLOG, empty/unfrozen formal protocol and USER_AUTHORITY. The new user objective authorizes ordinary-service implementation; the earlier finite-only seam is historical and insufficient for that objective. Root's SCIENCE_PLAN_REVIEW supports implementation/offline checks. Research/ALINEA core/network/demand/model/timing choices and formal protocol are unchanged. Existing unrelated changes are preserved.

New runtime namespace: `src/candidate_a_natural_service_20261015/` with policy, adapter, producer, bridge, profile and budget modules. One small CLI and one grouped offline-test module were added. The old154 files all hash-match the executed card, and the preceding three finite-scope modules match HEAD exactly; see PRESERVATION_AND_COMPILE_V1.json.

The actual loop, adapter and producer now use the natural600 activation. OPEN remains active before600; no CA_C8 red/prequeue hold is issued. The exact initial frame must be A_OPEN/G with empty R storage/ingress/internal and available receiver before any control setter. Unexpected nonempty/blocked initial traffic stops as an unsupported initial transition; it is not abruptly switched G->R. Natural input preparation keeps the existing4050 requests, seed, network, vehicle type/attributes and urban signals, adding only existing packet programs.

The selector uses C_raw minus E_scheduled_nominal. Complete N0/N1 and legal G/y extra entries continue; N is always counted and never drives physical catch-up. E_scheduled advances2 per completed planned packet. E_executed advances only for an executed complete packet. C_selected integrates selected7200/T; C_applied integrates it only during executed packets. Whole red-held packets have C_applied0, applied_request_id/rate=None, selected fields preserved and no false green application. Raw C/E/N and both schedule/execution/actual differences remain visible. Partial N is counted, partial E is not filled.

At later complete Y/R boundaries, a known receiver refusal holds the actual existing red for the whole selected nominal period with setPhaseDuration and readback. The selected program is not falsely installed while held; actual signal_program is separate. No green/program setter occurs during a held interval. The next ordinary boundary rechecks admission and uses the current pending request, without repaying missed physical service. Unknown receiver input remains STOP.

All original identity/geometry/phase/ACK, current native following, warning, red-entry, body, braking, collision/teleport and EOF checks remain in the real adapter path. The original complete-input yellow responsibility mode is explicit and retains failed-witness rows; no universal safety claim is made. Legal G/y overdelivery is a logged service deviation; a red front crossing is still a hard error. Command application requires a real G ACK. Supersession, missing application and pending status remain explicit.

The immutable Command schema also needed a new600 lower bound: the inherited generic validator was itself hard-coded to1200. Only the new class changes that time bound; its fields, rate/origin/own-previous validation and the actual project Feedback formula are preserved. Real E1 seed is600, first full feedback window600..630, with global/logical times identical. The unused dynamic_commands test interface still contains historical1201/1226/1237 schedule entries; it is not a tested600 dynamic schedule or a qualification candidate. The proposed natural card permits only real_alinea.

## Verification

Python `.venv/bin/python`,3.13.0. No new dependency or environment change.

Command for attempts1..3:

```
.venv/bin/python -m unittest discover -s tests/candidate_a_natural_service_20261015 -p 'test_natural.py' -v
```

- ATTEMPT1_TEST_OUTPUT.txt: exit1,3 grouped methods,0.075s,8 errors. This exposed the actual inherited Command>=1200 validation defect. New source/test preimages are preserved under attempt1_preimage; no error was suppressed.
- ATTEMPT2_TEST_OUTPUT.txt: exit0,3 methods,4.879s, after the new natural Command fix.
- ATTEMPT3_TEST_OUTPUT.txt: exit0,3 methods,4.906s, after selected/applied field separation was strengthened so withheld packets cannot claim a rate/request application. Affected policy/bridge preimages are retained under attempt2_preimage.

The grouped checks cover nominal period equality under full/0/1/3/withheld service, no physical catch-up, exact C decomposition, E_executed/selected/applied separation, dynamic pending request and first actual application, terminal partial accounting, own-previous Feedback, real new loop/adapter activation600, real Feedback630 window, natural empty/late/one-car observations, full-red denial/recovery, bad ACK, true braking, unknown receiver, unsupported initial frame and missing numeric authority before allocation.

The same already-passed loop method's four existing cases were exported, without expanding cases or a rate/seed matrix:

```
CA_NATURAL_FIXTURE_EXPORT=artifacts/thesis_actuator_readiness_20261015_v1/engineering/implementation_v1/synthetic_bundles .venv/bin/python -m unittest discover -s tests/candidate_a_natural_service_20261015 -p 'test_natural.py' -k test_real_loop_empty_one_late_and_receiver_red_wait_then_recovery -v
```

EXPORT_AFFECTED_METHOD_OUTPUT.txt: exit0,1 grouped method,3.234s. Four saved bundles are empty_none_641, supply_none_641, late_none_641 and blocked_none_641. These are fake movement/clock fixtures, not microscopic traffic or safety evidence. Their requests all yield raw C=41/4 and E_scheduled=10 while actual N and execution differ. The blocked case demonstrates withheld-red recovery and partial final packet640..648.

One concrete terminal risk remained: the new all-red branch's exact complete EOF must not prepare a setter/interval beginning at the endpoint. A single narrowly targeted method at640 was therefore added and run once; this is not an added traffic scenario or matrix:

```
CA_NATURAL_FIXTURE_EXPORT=artifacts/thesis_actuator_readiness_20261015_v1/engineering/implementation_v1/synthetic_bundles .venv/bin/python -m unittest discover -s tests/candidate_a_natural_service_20261015 -p 'test_natural.py' -k test_exact_complete_endpoint_does_not_prepare_a_future_interval -v
```

EXACT_ENDPOINT_TEST_OUTPUT.txt: exit0,1 method,0.743s. blocked_none_640 is saved. No setter at/after640; complete nominal accounting retained. The final source contains four methods, supported by the three-method run plus this targeted endpoint run, not a claimed final four-method suite run.

Static compile passed all8 new Python files. CLI `--help` passed without preparation/allocation/native import. The pending-budget test raises NEW_NUMERIC_BUDGET_NOT_APPROVED on an empty temporary root and leaves it empty. No actual preparation/card/release or native environment launch was tested.

## Independent-reader schema and handoff

Each saved bundle contains SYNTHETIC_RECEIPT.json (accounting, cycles, command records, actual endpoints/error), pre/post_steps.jsonl, step_ack.jsonl, command_events, feedback_events, admission, phase/duration requests and identity journal. Held cases additionally contain withheld_packets.jsonl. All intervals begin at the real clock; there is no hidden clock-shift facade. Cycle selected_request_id/selected_command_veh_h must be distinguished from applied_request_id/applied_command_veh_h and actual signal_program.

Independent audit should reconstruct C from issued request IDs and observed intervals, nominal selection from C-E_scheduled and complete boundaries, E_executed from real first-G ACK, C_applied with held periods excluded, and N from unique actual entry brackets. It must check absence of G setters in held intervals, pending/superseded application, actual warning/phase/coverage support and terminal partial/complete boundaries. The reported totals are not independent evidence. An empty/blocked period need not satisfy C=N and must not be discarded. A sustained unexplained deficit can still block qualification.

The new independent reader path is scripts/natural_service_audit_20261015_v1/actual.py, owned by data. Its final closure and the terminal postanalysis behavior remain to be reviewed/bound; old readers and the old processed terminal repair are unchanged. Existing fake logs can be reused directly; no suite rerun is needed for accounting.

## Authority, remaining limits and next step

Profile and budget are preparation/gating code only. Missing numeric approval fails before raw reservation or native launch. Proposed900/start60/free5GB has not become approved; the old600 ledger's475.645467625 consumed seconds and124.354532375 remainder remain visible. No actual new card or final closure was frozen, and no approval file was created. Reproducibility of native launch/new budget settlement is untested and must not be inferred from fake-loop success.

Ordinary-service source behavior is implemented, but natural4200 service/safety, throughput/cost/queues, all vehicles' lifecycle, actual held states and general qualification remain NOT_TESTED. Root/data/science must reconcile the independent audit, source closure, first-frame assumptions and observed-scope limits. The latest instruction prohibits native starts; continue only review, documentation and the authorized existing PR13 update/review. Root owns STATE/WORKLOG/problem records/Dashboard/GitHub. No governance file was edited by this agent. Stop engineering expansion once material review findings are handled.

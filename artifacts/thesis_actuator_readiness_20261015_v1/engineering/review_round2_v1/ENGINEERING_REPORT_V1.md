# Review5527104163: partial control application evidence

Reviewed commit24ec690de67818355076247f9192ed48a75ad390, comment4278226978. Scope: only natural bridge control-setter journaling and one targeted offline test. No native/SUMO/TraCI start, research/algorithm/safety contract change, matrix, governance edit, git commit/push or merge.

Context Preflight repeated: AGENTS/current STATE, DECISIONS, recent WORKLOG and empty/unfrozen protocol. Ordinary natural-service implementation remains offline only; natural safety/service NOT_TESTED, overall NOT_QUALIFIED. The latest user instruction prohibits SUMO and merging. Existing unrelated state/worklog/memory/release changes were preserved. Root owns current status/document updates; data owns its two readers/tests.

## Root cause and repair

The reviewed loop kept phase_requests in memory until pre_steps or a later phase journal write. A successful setProgram followed by a failing setPhase/readback could therefore change the actual signal but leave no durable record of the attempt or partial outcome. Exact reviewed source preimages and hashes are saved in reviewed_source_preimage and REVIEWED_PREIMAGE_BINDING_V1.json; both live files initially matched24ec.

The natural bridge now routes initial OPEN, new-packet program/green and quota-yellow setters through one small durable function. The underlying protected setter and all command values remain unchanged. Each setter writes/fsyncs ATTEMPTED before calling the API, CALL_RETURNED immediately after a normal return, then current readback status before another API or simulationStep. A thrown call records CALL_FAILED_STOP, the exception and independent best-effort actual signal fields; it explicitly allows unknown partial application. A missing field records READBACK_UNKNOWN_STOP; a known wrong value records READBACK_MISMATCH_STOP. Both stop immediately. No retry or subsequent motion is attempted.

Each current signal field is independently OBSERVED/value or UNKNOWN/None/error. Program/state observations survive an unavailable phase getter, without converting the unavailable phase to a fake value or claiming a movement ACK. Readbacks cover time, program, phase, state and nextSwitch. The prior all-or-nothing duplicate readback checks are replaced with the same explicit expected values in this durable path. Existing red-duration journaling remains unchanged.

Native execute failure_snapshot and bridge_receipt now include last_control_setter, the in-memory phase API request list and the durable control_setters.jsonl pointer. This preserves the latest attempt/readback even before a pre-step observation exists. The setter journal separately preserves earlier successful operations, so the last failing setPhase does not erase the preceding successful setProgram.

## Verification

Python `.venv/bin/python`,3.13.0. One targeted method, four distinct API-failure boundaries, no traffic parameter/seed matrix:

```
CA_SETTER_FAILURE_EXPORT=artifacts/thesis_actuator_readiness_20261015_v1/engineering/review_round2_v1/baseline_failure_bundles .venv/bin/python -m unittest discover -s tests/candidate_a_natural_service_20261015 -p 'test_natural.py' -k test_setter_partial_application_is_durable_and_stops_before_more_motion -v
```

Reviewed-source baseline: exit1,1 method,4 failures,1.840s. Every injected stop lacked the required durable setter journal. BASELINE_FAIL_OUTPUT.txt and baseline_failure_bundles preserve the actual failures; no totals were backfilled.

The exact same method after the bridge repair used the fixed_failure_bundles destination: exit0,1 method,1.742s; FIXED_TARGETED_OUTPUT.txt. Cases: initial OPEN setProgram succeeds/setPhase throws at0; natural new-green setProgram succeeds/setPhase throws at600; setPhase returns but phase readback is unavailable at600; quota-yellow setPhase throws after the603 actual ACK. The fake clock stops at the injected point in every case. There is no subsequent movement, retry or invented application. The readback failure retains program/state/nextSwitch observations and phase UNKNOWN/None. The yellow case retains its prior real-helper command/entry prefix and current G observation, not a fictitious yellow ACK.

The test uses XMLFakeConnection and synthetic vehicle movement exclusively. It validates control/error evidence and stop behavior, not native API reliability, real traffic or safety. No whole-suite or native rerun was performed. Compile passed the two modified files; scoped git diff --check passed. All154 historical source hashes remain identical, and the five other natural source modules match the reviewed commit. Old finite sources, readers, fixed f7 bundles and prior evidence/binders remain unchanged by engineering.

## Saved schema and remaining limits

Each fixed bundle contains control_setters.jsonl, SYNTHETIC_STOP.json and the actual pre/post/step ACK/command journals present before failure. A record contains setter_id, request time/method/value, expected_readback, status, call_completed and, when attempted, actual_signal.fields. CALL_FAILED_STOP.call_completed=false means the worker did not return normally; it does **not** establish that the mutation had no effect. actual_signal.scope explicitly says current getters after control, not movement ACK. No application or qualification is inferred solely from the journal status.

New file/version binding is in ENGINEERING_BINDING_V1.json. Data can inspect these saved four bundles without rerunning the loop; independent reader boundary checks and scientific review remain external gates. Unknown current signal information remains a stop and a limitation. Root should minimally update worklog/state/delivery with this review-specific evidence, publish only the authorized repaired scope and request the accurate-head final bounded review. No further engineering expansion is needed for this finding.

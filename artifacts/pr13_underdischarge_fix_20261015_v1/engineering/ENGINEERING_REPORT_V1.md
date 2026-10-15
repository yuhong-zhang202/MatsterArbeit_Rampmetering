# PR13 complete-packet underdelivery: bounded engineering repair

Status: OFFLINE_REVIEW_ONLY; no native run, run card, release, qualification or formal use.

## Context and root cause

Reviewed AGENTS.md, PROJECT_STATE.md, DECISIONS.md, the empty/unfrozen EXPERIMENT_PROTOCOL.md, relevant recent WORKLOG entries and the simulation-engineer instructions. Stage6 exploratory closeout stands; the finite Dynamic/ALINEA node is complete with limitations; A1 remains UNRESOLVED and Candidate A NOT_QUALIFIED. No formal protocol or general-service controller is approved by this repair. Existing unrelated changes were preserved.

The reviewed 154-source lineage reaches `native_yellow.bridge._diagnostic_loop -> ledger.begin_step -> SERVICE_PACKET_MISMATCH_HOLD_NO_CATCHUP` before new admission. Complete N=0/1 is not sufficient evidence of an actuator fault. The source observer can declare available=True with no front, so underdelivery is reachable without a saturated queue. An existing native WAIT during green is also distinct from a forbidden new-green receiver denial. The original lineage, cards, safety contract and raw evidence remain unchanged.

Pure-ledger baseline reproduction at750veh/h over one T10 packet gave C=25/12,E=2 and N=0/1 followed by the old unconditional exception; N=2 continued. This synthetic arithmetic observation does not identify a physical cause.

## New isolated implementation

`src/candidate_a_service_scope_20261015/policy.py` requires the exact explicit purpose FINITE_PACKET_DIAGNOSTIC_ONLY. It preserves the original accumulation and selection algorithm. A successfully reconciled complete packet records actual N, raw C/E/N/C-N and validated pre-step supply IDs, positions/speeds, receiver and native WAIT observations. The observations establish no readiness/saturation threshold or causal proof.

`adapter.py` uses the original complete prepare/reconcile paths. Only after original reconciliation succeeds does it assess the complete target. N=0/1 produces DIAGNOSTIC_TARGET_NOT_MET_CAUSE_UNESTABLISHED and stops without preparing another packet or recovering under-target service. N>2 remains abnormal. Original unknown, signal, safety, current-gap, numerical and new-green receiver gates run first. Partial packets are not compared with2; an exact final complete packet is assessed before return.

`bridge.py` is the real loop connection: it requires the new adapter and exact purpose, then uses the original loop. FORMAL/GENERAL purposes are rejected before inherited setters/advance. The new seam provides no launch function or execution authorization. It creates dedicated receipt/event files with exclusive creation before the loop and persists all ledger events in `finally`, including assessment on a stopped or terminal frame. General-service eligibility is always false. The old154 entry points are historical diagnostic code; they have not acquired new qualification.

This repair deliberately retains a service-capability blocker: there is no ordinary constrained-service continuation mode or new anti-windup/control policy. Raw unmet requests remain visible and no claim of physically unrecoverable debt is made.

## Verification and exact limits

Interpreter: `.venv/bin/python`, Python3.13.0. Command for all three attempts:

```
.venv/bin/python -m unittest discover -s tests/candidate_a_service_scope_20261015 -p 'test_scope.py' -v
```

- Attempt1: exit1,5 methods,15.917s,5 fixture assertion failures. Original output is retained in the tool transcript/session84130; the file receipt explicitly identifies its concise transcription, and the exact test preimage is retained under `attempt1/`. Four expectations assumed750/T10 while the real Feedback producer initialized900/T8; the partial fixture also correctly hit the original first-red checkpoint gate.
- Attempt2: exit1,5 methods,23.554s,1 fixture failure. Actual stdout/stderr are in `ATTEMPT2_TEST_OUTPUT.txt`, source preimage under `attempt2/`. The attempted partial's second admission correctly hit the original receiving gate because the late second synthetic entry remained internal.
- Attempt3: exit0,5 methods,35.374s; exact output in `ATTEMPT3_TEST_OUTPUT.txt`. Only the existing synthetic `early=True` two-car fixture was used to make the legal partial window: second entry at1204 rather than1205, clearing the fixture's internal lane by1210. This is fake movement, not native readiness or physical validation.

The five methods cover raw-accounting/selection equivalence for N2; neutral stopping for complete N0/N1; overquota; unknown completion; partial/pending; actual new adapter/loop wiring for empty, one-car, late-entry and native-WAIT observations; complete EOF assessment; hard-braking/unknown-receiver/new-green receiver priority; and purpose/adapter rejection before loop entry. At under-target stop the fake clock and accounted time are1210, one packet exists and no setter or advance occurs for a later packet. No test claims SUMO vehicle physics, independent native safety or general controller service.

`PRESERVED154_CHECK_V1.json`: all154 source files hash-match the executed Dynamic card (`53ffc491...`), common digest `089a2fefb9fb4d68aced499b532636c3a551b672f9130a1fd2e6acb468ff4ae2`. No old source, reader, approval/card, raw result or research parameter was changed. No SUMO, TraCI connection, merge, commit or push was performed.

Documentation impact: material technical repair requires root-owned minimal STATE/WORKLOG/report updates. No governance file was edited by this agent. The safest next step is independent data accounting/stop-evidence review and read-only scientific review, followed by publication to the existing PR and the authorized targeted review request. General-service continuation and native reuse remain separate, unresolved qualification work.

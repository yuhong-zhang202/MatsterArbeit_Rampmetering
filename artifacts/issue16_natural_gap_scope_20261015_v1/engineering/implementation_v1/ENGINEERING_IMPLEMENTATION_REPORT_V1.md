# Issue16 approved current-gap contract implementation V1

**Implemented for offline review; three bounded test methods PASS on the first attempt. No SUMO execution, new card, raw allocation, canonical or qualification was produced.** The old run remains STOP_RETAINED / NOT_QUALIFIED. Its exact card, 173 executed sources, raw, original failed reader and historical reports are unchanged.

## Context and authorization

Context Preflight read AGENTS, current PROJECT_STATE, DECISIONS, empty EXPERIMENT_PROTOCOL, recent relevant WORKLOG and the four-clause Issue16 decision. Prior investigation included the complete assigned WORKLOG1–1000 and STATE1–160 history. D018 historical exploration closeout remains; the current actuator is not qualified, formal protocol is 0B/unfrozen, first native start already consumed. Later direct user approval is recorded in artifacts/issue16_natural_gap_scope_20261015_v1/HUMAN_CONTRACT_APPROVAL_RECEIPT_V1.json: “批准该合同及最小离线实现”. This approves the four current-gap clauses and offline implementation only, explicitly no SUMO/new execution authority.

Work started with source preimages preserved before editing. Root committed the prior investigation/reader delivery during this task at72a2e617986fe3a26f65d3c0f17eae5ca0f1cdb0; that commit did not change these runtime preimages. Existing memory ledger/WORKLOG/unrelated authority changes and data-owned three readers/tests were preserved. No Git mutation was performed by this engineer.

## Exact code scope and all call paths

- New src/candidate_a_natural_service_20261015/current_gap_scope.py wraps the unchanged dynamic legacy current_following/classify_receiver functions. Fresh getLeader/getSecureGap queries, exact input dynamics/modes, original query parameters (including emergency9), numeric values, status/hard/legacy fields and receiver.available are preserved. Only the explicit ordinary-current responsibility classification changes. A below-reference record additionally binds actual leader lane/position/length to route-distance coordinates before it can continue. Invalid/nonfinite/negative gap, wrong identity/mode/time/path remain exceptions.
- Natural adapter.py uses the same new seam at ongoing PRE receiver, POST receiver, storage entry-before snapshots and actual entry-after snapshots. A legacy STOP_CURRENT_GAP_BOUND_DENIED may continue only as BELOW_NATIVE_REFERENCE_OBSERVED under the approved passive contract. Reference insufficiency never implies physical supply/receiver cause or safety. All existing real collision/teleport, negative gap, excessive braking, red entry, phase/ACK/identity/body/log checks remain unchanged. The disabled numerical-exception path receives an explicit role but remains disabled by the unchanged constructor rejection.
- Natural profile.py declares the contract/version, strict prospective responsibility and real approval receipt hash in spec; sources includes the new engineering test and approval receipt. Its consumed run01 identity is deliberately not reused or silently updated. Existing prepare/validate cannot generate a usable new card until the separate preparation stage changes identity/resources and the new reader has been reviewed.
- New independent tests/issue16_current_gap_scope_20261015_v1/test_scope.py owns the three bounded checks.

The actual bridge admission/new-G setter/held-red code is byte-identical to its preimage. Its fresh strict prospective receiver.available decision still occurs before any new G setters; false admits only the unchanged complete-period actual-red hold. The adapter still independently rejects a new executed cycle with receiver false. policy.py, producer.py and old dynamic receiver_wait.py are byte-identical. No ALINEA, schedule/debt accounting, parameters, models, demand, network, yellow/red timings, budget, guardian, source card or protocol change.

## Reader schema handoff

Every queried ordinary record retains all old keys and appends:

```
ordinary_current_gap_observation = {
  contract: ORDINARY_NATIVE_REFERENCE_OBSERVATION_V1,
  role: ONGOING_PRE_RECEIVER | POST_RECEIVER | ENTRY_BEFORE | ENTRY_AFTER,
  time_s: exact query time,
  classification: BELOW_NATIVE_REFERENCE_OBSERVED | CURRENT_GAP_OBSERVED_WITHIN_BOUND | CLEAR_WITHIN_OBSERVED_LOOKAHEAD,
  observational_only: true,
  native_safety_proven: false
}
```

A deficit still has original query.status=STOP_CURRENT_GAP_BOUND_DENIED, hard_screen_pass=false, legacy_margin_pass/legacy_contract_status/margin_classification unchanged. Below-reference queries additionally retain passive_leader_geometry {lane_id,position_m,length_m,reconstructed_gap_excluding_minGap_m,status}. Parallel merge lanes share their route station; gap coordinates exclude follower minGap, and a spanning leader rear is allowed only with a nonnegative bound actual gap. No vehicle length is silently treated as head-to-head distance.

Receiver decision adds current_gap_responsibility_contract and legacy_decision; only its decision may become BELOW_NATIVE_REFERENCE_OBSERVED. original_prospective_receiver.available remains false. READY/WAIT remain their existing meanings. New card.spec.current_gap_responsibility_contract binds policy, prospective_new_green=UNCHANGED_STRICT, ordinary_current_queries=OBSERVATIONAL_ONLY, approval_receipt/hash and native_safety_proven=false. Data agent owns independent validation and explicit reader version separation; this implementation does not edit those files.

## Offline verification and retained evidence

Exact command:

```
.venv/bin/python -m unittest discover -s tests/issue16_current_gap_scope_20261015_v1 -p test_scope.py -v
```

ATTEMPT1_COMMAND.json records exit0, unittest3methods/2.976s and wrapper3.193015458s. stdout/stderr are saved unchanged. No failing test or hidden rerun occurred. The three methods discriminate:

1. Exact saved649/650 query primitive replay: every old query field equals the original JSON; both old FAIL statuses remain, native query args remain unchanged, and the new observational classification is explicit. This is getter-fixture replay, not native motion or a counterfactual650→651 replay.
2. The true natural adapter and bridge loop with XMLFakeConnection: all four passive call paths accept a fully bound synthetic reference deficit; the receiver-limited packet at608 remains real-red for its complete cycle and a new G can occur at616. Complete N0 continues, partial remains partial, and C/E_scheduled versus E_executed remain distinct. This is synthetic movement and no physical safety or native constrained-service guarantee.
3. Five malformed query cases (negative gap, nonfinite query, wrong time, wrong mode, inconsistent path coordinates) reject; a coexisting native collision counter or actual acceleration−5 still immediately stops with the below-reference observation retained; wrong ACK signal still stops before command accounting/application. The fake world clock does not move past the failing ACK.

AST parse of the three owning runtime files and new test succeeds. Hash checks confirm unchanged bridge/policy/producer/old receiver. No full suite, old raw reanalysis, native process, TraCI connection, --version, environment change or optional matrix was run. A few read-only path searches encountered missing historical test folder/glob names; corrected searches found the actual fixtures before implementation. Those search errors changed no source and are not test results.

Five saved fixtures in attempt1_fixtures/ retain the exact test output: recorded_queries.json; loop_None.json; loop_collision.json; loop_braking.json; loop_badACK.json. Their explicit labels distinguish saved query replay and synthetic traffic from native evidence. Full test fixture export includes preactivation rows and is local engineering evidence; root chooses an appropriately bounded public evidence subset rather than publishing old raw.

## Limits and next gate

Three-way engineering/data/science review must finish before new-card preparation. No real650 continuation, native receiving hold/recovery,4200 horizon, six1200–3000 windows, sustained physical service or future safety has been measured for this contract. Keep current method NOT_TESTED / NOT_QUALIFIED. Exact accounting/version/population/EOF may support TECHNICAL_PASS only; actual hard anomalies/required UNKNOWN or unexplained persistent service loss when opportunities exist prevent qualification. Unencountered/insufficient-opportunity branches remain NOT_TESTED. ALINEA numerical tracking tolerance remains NOT_ASSESSED; no5%/10% threshold is invented.

Minimum separate preparation changes, not implemented here: profile needs a new run02 identity/package/output and exact proposal resources; budget inventory must explicitly preserve and recognize settled run01 plus new run02 (not rename the old run or reset its settlement). Existing effective_limits already supports a smaller requested ceiling: min(card outer, true remaining), then subtract cleanup30. Guardian imports the exact profile RUN and otherwise consumes those effective limits; no new control/guardian framework is needed. Current validate_prepared hard-codes900/870 and current budget inventory allows only RUN, so changing RUN alone would reject the old settlement or misbind resources. Both need the small exact-identity/resource update in that stage, with a targeted preparation-only check and new independent reader contract support.

Resource proposal only: preserve the independent total900 ledger, spent83.63743604102638 and remaining816.3625639589736; prepare outer816/worker786/cleanup30, startup60, free5GB, no byte cap. This is below the actual ledger remainder, contains cleanup, and is not a new900 allocation or execution approval. Only a separately approved exact new card/three-party/canonical can start; no automatic retry or extra matrix. The root controls the subsequent non-running preparation stage and final human gate.

Documentation impact: root owns minimal PROJECT_STATE/WORKLOG/decision/Issue updates; this engineer changes no governance. All source/test/receipt hashes and preserved preimages are recorded in IMPLEMENTATION_BINDING_V1.json. This binder is this engineering implementation's source/evidence binding, not the future complete execution closure or card.

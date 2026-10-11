# SMOKE02 self-loop correction — engineering review

**Minimal isolated configuration correction prepared, offline checks PASS; native validation NOT_RUN and native execution NOT_AUTHORIZED.** New identity `CA_NATIVE_PHASE_R300_S17_SMOKE02` cannot consume the old SMOKE01 authorization. No SUMO binary/version command, actual TraCI connection, installation or raw allocation in this task.

Context refreshed AGENTS, PROJECT_STATE, DECISIONS, WORKLOG, empty EXPERIMENT_PROTOCOL, SMOKE01 result, reviewed bridge/card/R2/protected phase helpers. Baseline `09d77dab8d19f414277ade5b399675f0e4e13f01`. SMOKE01 remains a consumed one-start premotion failure with immutable evidence; Stage6 closeout, A1 unresolved, Candidate A NOT_QUALIFIED, historical STOP3 and formal protocol0B unchanged. Parent separately authorized only this minimal offline correction/new identity preparation.

## Source-supported mechanism

SUMO v1_26_0 commit `fa7df22d7f1c4ae245192ecc32410a49f1ffb2a3`: `MSTrafficLightLogic.cpp135–159` warns when a multi-phase program has exactly one successor and it points to that same phase. This is an initialization predicate, not a collision/red-safety test. `NLJunctionControlBuilder.cpp518–525` initializes every collected network/additional logic, explaining why unused C9–C23 can warn while A_OPEN is selected. Native warning capture timing still does not establish an exact emission wallclock.

`MSSimpleTrafficLightLogic.cpp80–109` selects explicit `nextPhases.front()`, otherwise increments and wraps to0; the new XML uses explicit 0 rather than relying on omitted-next parsing. Phase events are begin-of-timestep scheduled; switch command/changeStepAndDuration excerpts retained. Three official files freshly fetched read-only, whole SHA and physical excerpts/URLs in OFFICIAL_SOURCE_RECEIPT_R1.json; initial two-file receipt preserved. One rg option-order error was corrected and disclosed; no test/artifact loss or native action.

## Exact new-package delta

Only new paths/package changed. Preserve byte-identical explicit demand, existing network/model/detectors, seed17/step1, demand3600/900/360/180veh/h, service command300veh/h, activation1200, end1207, no-warning suppression and warning aggregation disabled.

- Retain only used additional programs CA_C8 and CA_C24; remove unused C9–C23 from the **new** package. A_OPEN remains provided by the unchanged network and WAUT start selection.
- Holding program CA_C8 retains G3/y3 but red duration becomes600s with successor0. Its legacy name is only a reused identifier: actual cycle606s, **not8s**. Requested yellow at600 yields red603; finite red would next switch at1203. At1200 the unchanged bridge first verifies red/receiver and selects controlled CA_C24, preserving planned red throughout603–1200. Simply next0 with old2s red would prematurely turn green605; it is not the applied correction.
- Controlled CA_C24 retains G3/y3/r18, changing only red successor2→0. New controlled red begins1206; next automatic green would1224, after mandatory1207 close/pause. This delivery does not validate or authorize reaching1224 or using the package for complete-cycle/rate qualification.

Finite red and self-loop red have equivalent **planned colors within this bounded schedule** under specified phase requests. Full vehicle dynamics equivalence is not proven; changed native duration/graph may affect internal planning. Static graph predicate0 is not a prediction that native startup has no other warnings, nor a safety PASS. Three-second yellow adequacy remains context-limited/unverified.

## Versioned reuse and gates

New bridge is a versioned copy of reviewed old bridge with **exactly one import line changed**: old bridge_card → new profile. All step/ACK/readback/admission/coverage/post-check/log/cleanup/watchdog/mandatory-pause logic is identical. BRIDGE_VERSIONED_COPY_RECEIPT.json binds both hashes. New profile reuses old pure stage/env/source/hash functions, then edits only freshly created package XML. No old globals are monkeypatched; old source globs do not include the new namespace.

New card/CLI explicitly bind new run/task/output/source/input/environment. Default is offline prepare; an existing unconsumed card is read-only checked rather than overwritten. Supported execute uses new canonical auth/release and three-review hashes before importing native runtime or allocating raw. Both new authorization/release files are absent. Old local consumed SMOKE01 auth cannot satisfy the new namespace. Relocated checkout can publicly check hashed inputs but strict runtime own-root paths/environment reject foreign paths; it requires controlled rebind/new card authorization. Review hashes are provenance, not cryptographic proof of human approval.

Same logger/guard/admission/observer/adapter are reused unchanged. Original17 warnings still stop the new fake loop before motion; nothing is filtered, whitelisted or ignored. The prior unsupported prospective envelope remains only its existing isolated shadow advisory. Post-step monitoring detects/preserves, not prevents that already-executed step.

## Actual checks

- `PYTHONDONTWRITEBYTECODE=1 .venv/bin/python -m unittest discover -s tests/candidate_a_native_smoke_selfloop_fix_20261011 -v`: **5/5 PASS**,0FAIL/0ERROR/0SKIP, OFFLINE_TEST_LOG_V1.txt. Tests replay exact old17/new0 graph predicate, default/single-phase cases, byte-identical demand/newpackage/seed/logging, missing new auth before Popen, original-warning STOP, and actual new bridge loop driven by XML fake phase events.
- XML-driven fake empty world: y600–602, red603–1199, controlled G1200, red1206→1207, paused at1207 with nextSwitch1224; no automatic continuation. It is a source/event/identity pipeline check, not microscopic traffic evidence.
- New CLI `--prepare` and `--check-card <new canonical card>` each PASS; PREPARE_OUTPUT.txt/CARD_CHECK_OUTPUT.json. Default public checks use committed input/evidence and need neither ignored raw nor old canonical auth.
- Read-only `validate(card,require_environment=True)` PASS static current-root binding; Python3.13.0, traci/sumolib1.26.0, sumoITScontrol0.1.0, selected binary SHA matches inherited3bd1eaa3...; no native invocation. No full native-build/compiler or transitive-XSD certification. Full XSD validation not performed; lxml absent, no install.
- Local preservation audit:536protected/7R2/26V5/53SMOKE01raw files and oldcard7f74fa8c unchanged. OLD_EVIDENCE_PRESERVATION_RECEIPT.json records actual local hashes. Public checks do not claim access to uncommitted raw; original raw verification is local-only.

New card SHA `a501e6005589de0d3ce6acd0fe7924ec84b589bec0849c4f3fcd3f51a4d552f3`. Inherited180s/60s/300MB/5GB resource references require exact future user approval; watchdog remains sampled, not hard-real-time. Engineering source/card freeze precedes data→science review. Parent will separately perform a lightweight Git-archive materialized checkout, not label it a full Git clean clone. No old11/43 suites or native retries were run. No failing test occurred in the five-test suite; historical failures preserved.

Next: independent data review → read-only science → user/Chat review exact card/resources and native limitations. Any future launch needs separate explicit single-run authorization. Offline correction does not declare the red smoke completed, A1 proven, service qualified, sweet spot found or formal experiment ready.

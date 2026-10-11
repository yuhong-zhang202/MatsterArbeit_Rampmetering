# SMOKE03 bounded runtime-overhead correction — V2 engineering delivery

**Minimal query-reuse implementation prepared; eight offline tests PASS. No new SUMO/version command, real TraCI connection, raw allocation or runtime approval. Real performance and1207 target remain unverified.** Existing SMOKE02's one start/resource-stop687 and frozen58files remain separate from this new technical preparation.

## Context and measured cost boundary

AGENTS/custom instruction, PROJECT_STATE/DECISIONS/WORKLOG/empty EXPERIMENT_PROTOCOL, old bridge/adapter/worker and frozen SMOKE02 raw were refreshed. Exact preparation baseline59a9394071828ef25c86b7ae6d417e0c28b6119f. Latest user instruction permits technical diagnosis/fix, but previous unique-start/no automatic retry boundary remains. New identity CA_NATIVE_PHASE_R300_S17_SMOKE03 is PREPARED_NOT_RELEASED; newauth/release are absent. Phase/demand/model/seed/controller/safety/resource parameters were not changed.

Native facts:180s wall-budget stop after687steps, startup connect22.003s. ACK data has no per-operation wallclock profiling, so traffic-engine, RPC, Python serialization and filesystem shares are **UNKNOWN**. No claimed percentage of real walltime is assigned to a hotspot.

Readonly raw count: pre snapshots contain56,859world visits and145,833loaded visits, with56,859same-state overlap. Identity performs11 getters (type/route/2modes/7effective-dynamics); at least625,449pre-only duplicate getter opportunities exist. This is an opportunity count, **not measured native call reduction or time saved**. Post/cross-boundary reuse is not folded into that conservative raw count.

1376logcaptures show all four log prefixes0B before finalEOF; finalsumo.log1009B. Although whole-prefix log rereads can be quadratic for growing logs, that growth was **not observed here**. LogCapture is unchanged. Recursive output scans/fsync may cost time but their shares were not profiled; watchdog/scans/writes are retained. Existing source lookup/path errors are disclosed in the cost/source receipts and do not represent native activity or test failure.

## Smallest supported optimization

A new facade memoizes only17 explicit vehicle direct-value getters per bound native state time. Code/source whitelist in frame_cache.py/GETTER_SOURCE_RECEIPT_R1.json. Type/model fields are parameter reads, not random samples, planned speeds or hypothetical native branches. Official pinned1.26 source/wholeSHA/physicalgetter excerpts are bound; existing TraCI command-loop excerpt supports the synchronous stateframe premise.

Population IDs, loaded/pending/departed/arrived sets, lane enumeration/geometry, actual time, TLS/program/link/nextswitch, receiver leader/securegap/routeindex, vehicletype-domain reads, native collision/teleport counters and every log observation remain **fresh each call**. All old identity/coverage/receiver/mode/dynamics/deceleration/phase/admission/warning checks still run; only identical underlying direct-value requests are coalesced. CHECK_PRESERVATION_MATRIX_V2.json maps each check; its initial ambiguous type-getter wording is retained separately.

Frame time is established by an actual uncached getTime. Every simulationStep, setter and unknown exposed call invalidates before delegation; changed actual time clears values. A poststep frame may also serve the next prestep at that same physical time if no intervening mutator occurs. Trafficlight setters invalidate, including initialization/activation. No value survives the native step mutation as a memoized current value; old p.world snapshots remain intentionally separate for speed-difference checks.

Typed argument/keyword keys distinguish True/1/1.0. Unhashable arguments bypass caching with invalidation. Cached mutable results are copied both on storage and return. Getter/step/time/missing-attribute errors invalidate and propagate; old bridge still aborts/closes on exceptions. Unsupported noncallable connection/domain attributes reject instead of returning a mutable raw domain. Private implementation references are not an OS/security sandbox and arbitrary external raw access is outside the supported call graph.

**Required condition:** one owned synchronous connection, no external/asynchronous mutators, all state-mutating supported operations pass through the facade. This is explicitly recorded in the card. It is not a universal proof about arbitrary extensions or other clients. Eliminating repeated RPCs cannot reproduce the exact occurrence/timing of every transient failure that an omitted redundant RPC might have experienced; fresh time/population/TLS/step/log gates and propagated errors remain. Native transport/dynamics equivalence has not been tested.

## Versioned reuse, evidence and tests

New bridge is a versioned oldbridge copy: newprofile import, facade construction around the loop, and querycounter receipt fields. VERSIONED_BRIDGE_DIFF.txt is exact. Worker/observer/actor/R2/logger/watchdog/admission/cleanup/1207pause code is reused unchanged, without monkeypatching old globals or source globs. New profile delegates pure SMOKE02 package generation, preserving byte-identical demand and finiteholding/program semantics; it binds newnamespace/source/env/input/card/output/auth paths.

V1 seven tests passed. Parent review found two necessary facade boundary gaps: Python equality aliases in keys and unsupported noncallable raw-object leakage. ExactV1 sources/tests/CLI are preserved PRE_FACADE_BOUNDARY_FIX_V1; V1log/bench remain. V2 typedkeys/rejectunsupportedattributes add one bounded regression; **eight tests PASS/0FAIL/0ERROR/0SKIP**. Neither V1 nor V2 involved native processes.

Actual commands:

- `PYTHONDONTWRITEBYTECODE=1 .venv/bin/python -m unittest discover -s tests/candidate_a_native_smoke_runtime_fix_20261012 -v` — V2eightPASS, OFFLINE_TEST_LOG_V2.txt.
- New CLI `--prepare` and `--check-card <SMOKE03canonicalcard>` — PASS, PREPARE_OUTPUT_V2.txt/CARD_CHECK_OUTPUT_V2.json.
- Newprofile `validate(card,require_environment=True)` — PASS static own-root/environment/hash check, noexecute. Python3.13.0/traci-sumolib1.26.0/sumoITScontrol0.1.0; inherited binary SHA3bd1eaa3... matches. No compiled-equivalence/fulltransitive-XSD certificate or dependency installation.

Tests cover same-state return/identity equivalence, freshpopulation readers, step/time/setter/unknowncall invalidation, mutable isolation/typedID&args, missinggetter/nativegetter/step/time errors, duplicatecoverage/mode/warningSTOP, absentnewauthbeforePopen and complete XML fake1207old/new loop output equivalence. Comparison drops only temporarylog source/device/inode; all state/time/status/motion/accounting/receiver/logtext/hash/offset fields remain equal. Empty ramp with2M/1futureloadedR is **not** a realistic receiver/CF-dynamics or stochastictraffic proof.

Fake vehicle getter counts149,790→52,016 (97,774fewer,65.27%); freshID/loaded enumeration counts equal. Exact rawfake counters in FAKE_QUERY_BENCH_V2.json. Zero-RPC-latency fake CPUtimes: V1baseline1.430s/new1.690s; V2baseline1.900s/new1.860s, single samples with filesystem/host variance. These do not show a reliable speedup; no native timing extrapolation, promised1207 completion or target-oriented tuning.

## Preservation, authorization and handoff

536protected/7R2/26V5/29SMOKE02engineering-bound/53SMOKE01raw/58SMOKE02raw whole-file hashes unchanged. Local raw cost/count and preservation audits are local-only; default newtests/package checks use committed public fixtures/XML, not ignoredraw or consumedcanonicalauth. New resource bounds unchanged180s/60s/300MB/5GB, nativephase end1207, no warningfilters/extra futurecycles/qualification. No old tests or native reruns.

Newcard SHA892b415603df776bb70698ad66939bbad28993e87a1bc225d5553ba58ac6bba4. Source/input/actualverification bindings follow INPUT_BINDINGS_V2.json/OFFLINE_VERIFICATION_RECEIPT_V2.json. Prepared own-host paths/environment are strict at runtime; relocated launch would need controlledrebinding/newexactapproval, not silent card overwrite. New executableauth/release/raw are absent; oldSMOKE02authority is consumed and cannot satisfy SMOKE03 gate.

Engineering freeze now → independent data review → readonly science → user/Chat. Native latency/performance, complete real firstcontrolledred and qualification remain unresolved. No additional technical optimization is necessary within this bounded delivery unless review identifies a concrete defect. Later one SMOKE03 run requires explicit approval of actual reviewed HEAD/card; current work is no launch authority. Stage6 closure/A1unresolved/historicalSTOP3/CandidateANOT_QUALIFIED/formalprotocol0B remain.

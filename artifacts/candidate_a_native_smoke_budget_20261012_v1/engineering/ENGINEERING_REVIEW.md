# Engineering review — bounded SMOKE04 technical wall-budget proposal

**PASS_FOR_BOUNDED_OFFLINE_300S_BUDGET_PROPOSAL_ONLY. No SUMO, native version query, actual TraCI connection or new raw/auth/release was created.** The only proposed runtime resource change is wall_limit_s 180 → 300 for the new identity CA_NATIVE_PHASE_R300_S17_SMOKE04. It remains unreleased and requires future explicit exact-version/card execution approval.

## Context and approval boundary

Reviewed AGENTS.md, PROJECT_STATE.md, DECISIONS.md, empty EXPERIMENT_PROTOCOL.md and relevant recent WORKLOG entries. Baseline22ec93c7b54d4ea15f55284026ded6c414de605b. Current SMOKE03 authorized one-start consumed, stopped1157 at180 wall seconds. Older prepared-SMOKE03 state is historical; top current entry supersedes it. Stage6 closeout, original STOP3, Candidate A NOT_QUALIFIED, A1 UNRESOLVED and900 NOT_TESTED unchanged. No formal protocol is set/frozen; no formal values inferred. Latest user explicitly requests budget investigation/new prepared card, forbids SUMO this round. Parent owns governance documentation; engineering touched only new technical namespaces/evidence.

## Source and reason for180 seconds

Original scripts/candidate_a_qualification_20261008_v1/runner.py line23 hardcodes180 with60 startup/300MB run/5GB free-space. First tracked file commit30e547cbca1fa7ef97a0c9b0e043b4d870a1ab98. Issue #4 archived body has no180 or wall-clock requirement. SMOKE01 V5 card resources_provenance binds that runner SHA d0f16717d80ba2dbbf5f93ea4878916caa570e8b75ae95f0c9c4d05dceedff4d; SMOKE02/03 reuse it. It was a bounded engineering resource choice, later explicitly accepted for specific cards, not a traffic safety predicate or Robert instruction. Targeted provenance sources contain no current-bridge runtime calibration for180. This is not an exhaustive private communication search or claim original choice was never reasonable.

The bridge starts its wall clock after static checks, initial output reservation and source snapshots, before capture/worker import/native spawn/connect. Startup and loop observer/admission/phase/ACK/log/resources/reconciliation work share the cap. Watchdog .2s samples and between-step <= condition use the same card limit; watchdog may run during cleanup. Earlier preparation/audits and post watchdog-close finalization are outside this clock. Cleanup/scheduling overshoot is possible: the cap is not a hard real-time limit on total CLI/audit duration.

## Measured inputs and proposed finite headroom

SMOKE02:687 completed steps;22.003270457993494s connection time. SMOKE03:1157 steps;24.95967800001381s connection;154.78s SUMO native duration. These runs differ in implementation; they are not a matched speedup experiment. Native duration/TraCI metrics are not component CPU or unique hotspot measurements.

Illustrative whole-prefix proportional planning:24.959678 +154.78×1207/1157 ≈186.43s. Replacing startup with the unchanged60s maximum gives ≈221.47s. Remaining50 steps have not been observed and include new admission/control phases and increased population; native/startup timers differ from bridge wall. Neither estimate is a prediction, upper bound, confidence interval, or safety proof.240s would leave about18.53s against the latter illustration; it is not proven inadequate. Recommend one300s finite resource proposal with about78.53s illustrative headroom, to prioritize finishing the original bounded diagnostic over more optimization.300 does not guarantee reaching1207, remove a safety abort, or authorize reruns. A further abort is retained and returned for review; no automatic cap escalation.

## Minimal implementation and preservation

New bridge is byte-identical to reviewed SMOKE03 bridge except one profile import. Reuses original FrameCache, R2 adapter, observer/actor/worker, watchdog, logs and cleanup. New profile/CLI gates new identity/package/output and exact integer resources; malformed/altered limits or provenance fail closed. No monkeypatch of old globals. New card binds current sources, public demand/config/network and unchanged environment hashes. Candidate A hardware/traffic/check behavior is unchanged.

All identity, mode/dynamics, TLS/link/phase, all loaded/current/entering vehicle coverage, receiver/admission, braking/collision/teleport/red crossing checks, log classifier, source preservation, no retry and1207 stop remain. Startup60s/output300,000,000B/free5,000,000,000B/watchdog.2s unchanged. M3600/R900/U360/X180 demand/service300/seed17/dt1/activation1200/finite holding red600/controlledG3-y3-r18 unchanged. Prepared package matches SMOKE03 after only new path/identity substitution; demand byte-identical. Online native four-stream coverage still excludes parent CLI warning output, captured only finally; known TraCI integer-step compatibility warning scope remains disclosed. No warning suppression or API float-argument change.

536 protected files,22 old bound source files and original cards unchanged. All53 SMOKE01/58 SMOKE02/62 SMOKE03 raw files matched their immutable hashes locally. Full raw is local-only; public evidence does not recreate it. Exact new card SHA1fe30783bb04fb79a3fc7e17b21e946be9cb0c58223258dd7a51dfda3898b086.

## Verification, real failures and limits

New five-test suite V1 had four fake-gate ERROR subcases because the test fake worker omitted observe, before any resource gate. Exact V1 source/log/receipt saved; V2 only adds the missing fake attribute. Actual V2 five tests PASS: exact bridge body/1207 stop; strict resource/provenance/environment card; synchronous180-at200 abort vs300-at200 accepts resource gate;300 boundary and sampled watchdog stops; unchanged disk/output fail; absent newauthorization blocks before spawn/raw. Default prepare/card check PASS. A preservation checker first constructed the SMOKE01 manifest name without underscore; this path failure is retained; explicit known-path V2 passes. No raw/source/card changed in either correction. No failed result was silently removed.

Existing eight same-frame safety/query tests are reused via unchanged exact source/test hashes and bridge-body equivalence, not rerun or claimed newly executed. No native performance, yellow adequacy, physical safety,1207 completion, service tracking or qualification is demonstrated by these offline checks. No new timing instrumentation/optimization, actuator change, new A1 proof or research design. Data and scientific independent reviews remain required before parent delivers this prepared proposal.

Commands and byte bindings: OFFLINE_COMMAND_RECEIPT_V1/V2.json, BUDGET_BASIS_AND_PROPOSAL_V1.json, ISSUE_RESOURCE_ORIGIN_SUPPLEMENT_V1.json, PRESERVATION_AND_MINIMAL_DELTA_V2.json, BRIDGE_MINIMAL_DIFF_V1.json, INPUT_BINDINGS_V1.json. Only new technical files/evidence were written. Parent documentation impact check should append factual current preparation status, preserve historical180/no-cap-change evidence and decisions/protocol untouched.

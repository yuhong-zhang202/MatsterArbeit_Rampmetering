# Ordinary-service independent offline reader review

Status: PASS_OFFLINE_OBSERVATION_ACCOUNTING_ONLY. Natural/native qualification, EOF, full4050 lifecycle, urban exposure and native safety are NOT_TESTED. No native/SUMO/fake-loop execution occurred in this data task. Existing engineering bundles were read only; their scope is0..640/641 fake-clock traffic with control600 onward.

## Context and binding

Repeated mandatory context preflight: AGENTS, current STATE (expanded thesis-readiness goal and PR13 P2), DECISIONS, empty/unfrozen protocol, recent WORKLOG; new USER_AUTHORITY, scientific plan and measurement preflight; new six runtime modules and engineering tests/export schema. Stage6 remains exploratory closed, A1 UNRESOLVED/NOT_QUALIFIED. Latest instruction prohibits SUMO; no card/Issue preparation was performed.

Engineering handoff: artifacts/thesis_actuator_readiness_20261015_v1/engineering/implementation_v1/ENGINEERING_BINDING_V1.json SHA25647415e55e71b52e8ed4894ca6070f84fff3c2a2a5bf3521722e6042c9894bc38. Its bound files were hash read back. Engineering three grouped methods PASS4.906s plus exact-end affected one method PASS0.743s are prior engineering evidence, not rerun by data. New data reader scripts/natural_service_audit_20261015_v1/actual.py and test tests/natural_service_audit_20261015_v1/test_actual.py are independently owned and hash bound below. No old runtime/reader/binder/raw was modified by this task.

## Inputs and calculations

Read exactly five existing engineering exports under implementation_v1/synthetic_bundles/: empty_none_641, supply_none_641, late_none_641, blocked_none_641 and blocked_none_640. No new rates/seeds/matrix. Uses original pre/post-step, verified step ACK, admission, command/feedback events, nominal completion, phase/duration requests and synthetic receipt. Source snapshots/event hashes remain traceable; summary totals are comparisons rather than reconstruction inputs.

Reader is stdlib-only and imports no runtime policy/selector, simulation driver or TraCI. It independently integrates chronological issued REQUESTED rates on observed1s intervals, chooses period8..24 by minimum absolute C−E_scheduled+rate*T/3600−2 (ties prefer longer), reconstructs complete nominal E_scheduled, executed E_executed from actual first-G signal binding/ACK, selected/applied integrals2/T per acknowledged step (zero applied on held periods), and unique ACK-bound G/Y crossingsN. It verifies per-step and final C/E/N residual decomposition, completion/partial, request first applications/delay, cycle summary and actual signal/program. Legal G/Y actualN is never clipped at2 or used to select a shorter recovery packet.

Held-red evidence checks actual previous red program and phase, absence of setProgram/setPhase, setPhaseDuration request/readback to the selected nominal end, no false green ACK, and applied request/rate fields. Duration setters at or beyond endpoint are rejected; exact complete endpoint is distinct from a partial cycle. No physical lost-service offset, reset or removal of C is introduced.

Full pre/post and verified clock ACK coverage0..end is required; control accounting begins600, with empty same-G initial admission and no CA_C8 artificial prequeue. E1 activation seed is600 and post-ACK E1 observations are contiguous601..end. Each complete feedback decision strictly before end is reconstructed using recorded detector event intervals, original Feedback own previous bounded request,11%/70/300..900 formula and matching request. All observed engineering E1 windows here are empty-detector zero occupancy; the reader's nonempty event arithmetic has not been independently qualified by these fixtures.

Post row rate_chain is sampled immediately before ledger.end_step. Thus a new executed packet's first-G row legitimately has null applied request/rate, while the same row's actual signal binding, emitted PACKET_ACK and post-ledger accounting establish real application. Subsequent rows have applied fields; held rows always null request/rate0. Final cycle summary uses null applied_command/rate for held. Reader explicitly checks these different sampling supports.

## Exact independent results

| Existing fake bundle | C | E_scheduled | E_executed | C_selected | C_applied | ActualN | Endpoint |
|---|---:|---:|---:|---:|---:|---:|---|
|empty_none_641|41/4|10|10|41/4|41/4|0|641, partial|
|supply_none_641|41/4|10|10|41/4|41/4|5|641, partial|
|late_none_641|41/4|10|10|41/4|41/4|4|641, partial|
|blocked_none_641|41/4|10|8|41/4|33/4|4|641, partial|
|blocked_none_640|10|10|8|10|8|4|640, complete|

All select six8s periods for641 (last640..648partial) or five complete8s periods for640. N0/N1 observations do not terminate ordinary operation. Blocked nominal packet608..616 stays actual red with original program; ordinary execution resumes616. It contributes2 to completed E_scheduled but0 to E_executed/C_applied. No lost physical service is chased: selection uses scheduled error, independent of actualN/held status. All have original bounded request900 over observed time; C−N remains visible (41/4,21/4,25/4,25/4 for641;6 for640). This is a correct observed mismatch, not service PASS.

Every case independently confirms one original Feedback decision at630 over600..630: empty detector occupancy0, raw1670/clipped900, own previous900. First application for initial real request600 is600 and feedback630 is632, delay2s. Initial placeholder request is superseded and never applied. No final unapplied feedback request occurs in these five bundles; actual natural pending behavior beyond the source/pure engineering tests is NOT_TESTED by this saved bundle review. Partial last nominal E is not filled; partial observed N is counted.

## Commands, failures and targeted checks

1. `.venv/bin/python scripts/natural_service_audit_20261015_v1/actual.py --input artifacts/thesis_actuator_readiness_20261015_v1/engineering/implementation_v1/synthetic_bundles/blocked_none_641 --output data/processed/thesis_actuator_readiness_20261015_v1/natural_reader_v1/blocked_attempt1.json` — initial reader CLI exit0; historical intermediate reader result retained, not the final reader certification.
2. `.venv/bin/python -m unittest discover -s tests/natural_service_audit_20261015_v1 -p test_actual.py -v` — initial five saved bundles/9mutations+synthetic hard annotation PASS,1group0.924s, OFFLINE_RESULT_V1.json.
3. Same group after direct selected/applied field binding was strengthened: exit1,1group0.156s,6errors. Reader incorrectly expected rate_chain to be after ledger ACK; runtime schema proves it is before ledger.end_step. FIELD_BINDING_FAILURE.txt and exact FIELD_BINDING_FAILURE_READER.py retained. No runtime defect/data alteration or simulation occurred.
4. Same group after reader timing correction: exit0,1group0.970s,10mutations, OFFLINE_RESULT_V2.json. No fake loop/suite rerun; only read saved logs and in-memory mutations. No subsequent optional validation.

Ten focused invalid variants rejected: missing verified ACK, false executed held cycle, false held applied request, physical-debt selection error, selected program falsely called actual while held, missing held duration readback, terminal setter, missing E1 interval, missing request record and unreported safety-stop receipt. Additionally, an explicitly labelled in-memory terminal hard annotation of blocked641 is accepted as HARD_OR_UNKNOWN_STOP_RETAINED with original accounting. This annotation tests reader retention/classification only; it is not a new actual fake-loop or native safety event. Engineering's actual hard-fault tests remain separate evidence.

## Interpretation boundaries and missing domains

Current entrypoint deliberately accepts only SYNTHETIC_RECEIPT-labelled engineering bundles; unsupported native input fails instead of falsely qualifying. No current native execution card exists and latest user instruction prohibits SUMO. Native EOF closure (owned-process final logs/exit, raw manifest), independent final-tripinfo normal-arrival/tail audit, full planned4050 lifecycle, source-wait/unfinished costs, urban shared-lane exposure and whole-network safety coverage are explicitly NOT_TESTED. This reader does not create a full raw/FCD or lifecycle framework.

Future authorized native audit needs exact card/source/raw manifest and bridge receipt with final EOF logs, full scheduled-demand4050 IDs, final tripinfo write-unfinished/write-undeparted, summary/insertion counts and endpoint identities. Existing formal_development parsers can supply cohort-restricted source/in-network/system accounting and shared-road observations only after matching new files/time semantics and source binding; no current reuse is claimed. A budget proposal or offline reader PASS is not execution authority, general scientific qualification or formal protocol approval.

No substantive new runtime finding remains within the observed offline repair scope. New source real-loop plus this independent saved-log reader support PR13 repair review only. Root should minimally update STATE/WORKLOG/problem records as integration requires; this data agent did not edit governance. Safest next step: read-only scientific final source/data review, then the authorized existing PR13 update/review. Stop additional tests and native preparation under current instruction.

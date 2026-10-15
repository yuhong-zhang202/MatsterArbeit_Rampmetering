# Definite stop-event logging repair engineering review

2026-10-14. PASS_FOR_MINIMAL_OFFLINE_LOGGING_REPAIR_ONLY; no new card/native, physical Dynamic gap blocker unchanged.

Context: AGENTS and updated STATE/WORKLOG/known unfrozen protocol read; root explicitly authorized this logging repair separately from the current-gap investigation. Three PRE states1230–1232 plus STOP1233 establish NO_GO_FOR_EXISTING_READINESS_WAIT_REUSE_AS_CURRENT_FIX, preserved in readiness_and_flush_investigation_v1/INVESTIGATION_V1.md. The existing READY branch evaluates R4 at1232; after its entry, nextfrontR5 fails the retained margin. Existing WAIT requires currentgap alreadypass. Holding an additional red step would need a new reviewed WAIT state/clock/request integration, not reuse an existing permissible branch. No future-safe delay or solution is inferred from these frames.

## Concrete change and preservation

Only current followup bridge.py is changed. Executed V2 bytes match the consumed card and are saved at preimages/BRIDGE_EXECUTED_V2.py. New bridgeSHA ae40d38a4f46c5a9de4ec64083563339363338599f9afcf7b5e52bc350bffddd. Original125 policy/adapter/Producer/guards/phase/Feedback and currentprofile/budget stay byte-exact; no threshold/model/SUMO modification.

Extracted `_flush_observed_events` writes only events already present in Ledger/Producer, advancing its command/feedback cursor after each successful durable row. Reconcile-error handling flushes those events and the retained stop row, then the original `raise` preserves its exact exception. Logging failure writes UNKNOWN_STOP_EVENT_LOGGING with original stop, write error and successful cursors; it raises a chained error preserving the original cause, never resumes motion or retries an uncertain write. If even the error-record write fails, that failure remains in the raised error. On success, observed command ACK events are flushed before subsequent telemetry can fail, and the later feedback flush only appends new rows. No application is manufactured from a prepared state or guessed future ACK.

## Actual verification and genuine failure

New synthetic logging suite: `.venv/bin/python -m unittest tests.candidate_a_cumulative_full_followup_20261014.test_stop_journal -v`, V1 two PASS/one ERROR,0.004s. The tiny test-only FrameCache facade lacked stats; source/test snapshots and complete ERROR log retained. Production did not fail this way. Add only fake.stats; rerun only affected real-loop method: PASS0.002s. Other two unchanged method bodies reuse original PASS; no claim of rerunning all three on final test bytes.

The loop regression uses real Ledger-created events and a synthetic clock/facade solely to test bridge error control flow, not vehicle/safety behavior. It creates the first-G application events, then raises the stop; events are retained exactly once, the exact original exception propagates and only one synthetic simulation step occurs. Normal repeated flush has no duplicates or fabricated events. I/O regression retains original cause and UNKNOWN record, holds the successful first-row cursor and performs no implicit write/native retry; explicit unit-only resumed flushing after a known pre-write failure demonstrates prefix idempotence. This is not permission to retry an uncertain filesystem write or native run.

Real profile validation now rejects both old V2 cards with CANDIDATE_SOURCE_DRIFT, while old card/auth/raw snapshots remain unchanged and interpretable. Dynamic identity is consumed; unused Feedback requires a future V3 exact source/card binding. No new card/auth/release/raw/start/version call was created in this repair. The fixed750 actual result remains source125 evidence, not evidence for this newly repaired bridge SHA.

## Remaining gate and next step

Independent data owns the audit shadow-variable repair and any future full reader/first-yellow source coverage correction. Existing raw and consumed card-bound reader must remain immutable; separate offline audit code or versioned future source must disclose coverage/reconstruction limits. This repair does not retroactively append the missing events to the old raw, turn Dynamic into fullPASS, clear R4's censored tail, or reduce the physical gap margin. Original native/private-branch and finalAFTER single-source limits remain.

Root/data/science review this exact logging repair before any future release. A separately reviewed realFeedback interface diagnostic is a distinct question from the failed Dynamic history, not an unchanged reroll; it remains dependent on actual postreview/settlement and one new exact unused Feedback card. Charge the known147.815189833s to the same600 envelope once properly settled, not a new600 reset. No newDynamic card or unsafe WAIT implementation is proposed or prepared here. Root owns governance/documentation/Git updates.

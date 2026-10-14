# Bounded engineering review: followup auditor repair

**GO_FOR_TWO_DEFECT_OFFLINE_REPAIR_REVIEW_ONLY. No new Blocker/Major found in the reviewed diff.** This is an advisory technical review, not native safety, service qualification, full actual-audit PASS or authorization.

Context refreshed: AGENTS, latest PROJECT_STATE, DECISIONS D-018/D-019, empty/unfrozen EXPERIMENT_PROTOCOL and relevant WORKLOG. Current gap-contract proposal remains unapproved; no new SUMO/card preparation. Stage6/A1/NOT_QUALIFIED unchanged.

## Frozen evidence independently read back

- Data report SHA `6a04044da31dbddd5b0de736601112a3411f2f3080cc12e8754dad13e80e7a62`.
- Data 11-file binder SHA `b555c55ac0aa8cf5951324eef293433eaeeb6cdab1b699fbb467e5d33a3812a2`: 11 file hashes independently matched, mismatches=[].
- Actual reader SHA `def3432ef9688cffd72795eea8a85796a9cba5d50a56e5d9ac4d11685614ce0b`.
- Exact-catalogue yellow helper SHA `555614050be6cf497903d8ff541d1139b4ea57d27a0296efaabebfd85dbe4f98`.
- Protected original source/card dependencies: 125 independently compared against recorded original expected hashes, mismatches=[]. No raw rescanning.
- Current followup bridge SHA `ae40d38a4f46c5a9de4ec64083563339363338599f9afcf7b5e52bc350bffddd` retains the separately reviewed logging-only repair; this auditor repair does not alter it. No runtime/guard/budget source changed in the reviewed diff.

## Technical assessment

1. **Terminal shadow fixed:** `actual.py` still imports the real terminal module globally and calls its arrival audit at line92. Only the later result variable and two uses become `terminal_support` (190–192), removing Python's whole-function local-variable shadow. The AST-extracted original call plus assignment reproduces old UnboundLocalError, and new call invokes the module spy. This is binding evidence; it is not execution of the whole actual-reader pipeline or a new normal-arrival physical verification.
2. **Exact yellow catalogue:** the new `yellow.py:8–13` uses the unchanged independent catalogue(period), requiring legal integer period, exact Gmax and exact yellow duration. T8=G4/Y2, T9=G4/Y3, T10=G5/Y3, T11…24=G4/Y5 match current production `policy.parameters`/independent core. It neither accepts arbitrary2–5s nor restores historical T10/Y4. No production phase or yellow-screen formula changes.
3. **Missing evidence remains failure:** the rest of yellow_record/yellow_coverage is copied unchanged from protected evidence: population/ID/time/speed/position/dynamics/formula binding, observed first-Y completeness, duplicate/extra record rejection and narrowly distinguished aborted prepared-not-observed prefix. Tests exercise missing firstY, unknown speed, missing position, wrong ID/clock, duration/type/Gmax mismatch; they do not turn missing raw ACK into reconstructed PASS or skip unknowns.
4. **Preservation:** old actual079 source, protected evidence reference, original failures, native raw, card/release and runtime contract remain historical. New reader hashes are not valid substitutes for a consumed card's original source snapshot. Any future run needs fresh reviewed source bindings; no new card is made here.

## Verification actually used / limits

Data executed `.venv/bin/python -B -m unittest discover -s tests/cumulative_full_catalogue_followup_audit_20261014 -p test_reader_compatibility_fix.py -v` once: 3 methods PASS, exit0,0.009s; exact source/test/log receipts were inspected. Engineering did **not** rerun tests or the actual reader. The new tiny fixtures are synthetic, including 17 parameter lookups rather than 17 simulations. Existing 1294 normal-arrival joins belong to historical bounded data reconciliation using the unchanged terminal helper, not this new complete pipeline.

Original Dynamic remains1233 STOP, partial packet/body censor and two missing raw command ACKs UNKNOWN. New helper compatibility does not establish future yellow feasibility or solve current-gap contract. No tolerance/guard/model/policy/budget was relaxed. No source edits, native/version process, raw allocation, authorization/release or tests performed by this review.

Next: read-only scientific review of this narrow repair. Parent maintains STATE/WORKLOG; no decision/protocol changes are implied.

# Signal ACK binding repair — engineering review V2

2026-10-13. **READY_FOR_INDEPENDENT_DATA_AND_SCIENTIFIC_REVIEW_ONLY.** No SUMO, new raw directory or executable authorization/release was created. Stage 6, A1, service qualification and the unfrozen formal protocol are unchanged.

## Context and defect

AGENTS, current PROJECT_STATE, DECISIONS, empty EXPERIMENT_PROTOCOL, recent WORKLOG and explicit scope approval were reread. The current delegation is a bounded technical correction within that approved scope. Current local HEAD is `1b6bd3011ca1419a884482f52de6ddf556982ec4`; this repair is an exact uncommitted source snapshot above that commit. The original approved project baseline remains `9eb95e29ccc85423084bc6945668cd36c3298b06`.

Scientific prelaunch review identified that the ledger confirmed `ACK_OBSERVED` from the expected G motion before the actual post phase/state/program/link checks. A wrong signal could therefore stop the run but leave a false first application timestamp.

One new regression method reproduced the defect on the preserved V1 runtime: four same-nextSwitch mutations (wrong state, phase, program or controlled link) each stopped but incorrectly retained `first_application_s=1200`. Actual result: **1 method / 4 failing subcases**, exit1. `NEGATIVE_CONTROL_OLD_SOURCE_FAIL_V1.log`, the exact test, source preimage and `OLD_SOURCE_FAILURE_RECEIPT_V1.json` are retained. This was an offline failure, not a SUMO run.

## Smallest correction

Before invoking the ledger, the adapter now records and validates the actual post phase/state, program, controlled links and matching ACK time. An unbound signal raises `POST_SIGNAL_APPLICATION_BINDING_MISMATCH` before any command application or expected-motion accounting. The observed entry ID/bracket is retained in the incomplete receipt; it is not promoted to validated signal/accounting evidence. `first_application_s` remains null and no `ACK_OBSERVED` event is emitted. The original later physical guard block remains byte-identical, including receiver/current gap, emergency9+1.1 m, collision/teleport, red entry, braking, actual-entry before/after and body checks. No phase timing, mapping, Feedback formula, model, demand or stopping threshold was changed.

The CLI default now prepares the new identity **UA_FIXED300_S17_02**. The original01 card is retained with unchanged SHA `2c2330d4c977fb26c8ef52a36a16d56a7a6c94cb5334e8d5557f19eb967bed09`; it is superseded and not releasable with this changed source. Old reports and binders remain historical, not overwritten.

## Actual verification

`AFFECTED_TESTS_FIXED_SOURCE_V2.log`: **3 methods PASS**, 10.038s:

```
.venv/bin/python -m unittest \
  tests.candidate_a_unified_alinea_20261013.test_unified.UnifiedTests.test_same_clock_wrong_post_signal_program_or_link_never_applies_command \
  tests.candidate_a_unified_alinea_20261013.test_unified.UnifiedTests.test_real_helper_dynamic_bridge_continuous_phases_and_boundary_switches \
  tests.candidate_a_unified_alinea_20261013.test_unified.UnifiedTests.test_actual_feedback_class_global_seed_ongoing_windows_and_own_clipped_state -v
```

All four wrong-signal subcases now stop without an application timestamp/event. Positive XML/real-setter-helper dynamic and actual project Feedback bridge fixtures still confirm the correct observed requests. The unaffected period/mapping, accounting, hard-gap/yellow and resource checks are reused from the previous five-method suite; they were not claimed rerun. These fixture movements/E1 data remain synthetic, not native safety evidence.

`HISTORICAL900_COMPATIBILITY_V2.json`: affected local recorded900 replay PASS,72 motion/clock/entry rows and20 exact setter requests/readbacks. Every recorded post state and phase is compatible with the new early binding; historical successful original guard checks already required the matching program/link. The physical guard block and world identity functions remain identical. This is historical trace/source compatibility, not a new native900 run. The replay depends on immutable local raw; the new regression does not.

`FRESH_CARD_PERMISSION_CHECK_V2.log`: new card/source/input/environment validation PASS; missing canonical permission rejects before allocation; all536 protected files and old01 card hash are unchanged. The new-stage budget remains0 spent/1200s and1.2GB available.

## Frozen replacement card

- Card: `../packages/UA_FIXED300_S17_02/card.json`.
- SHA-256: `49bcb2863acf9c0334cbcd9e398521978f4436514ee8d2350390233db90fc4b6`.
- Common61-record runtime digest: `a2b25659131bae5d9628ff5ab2f35e0c89987705daa5ef84a67ce426967b4b2b`.
- `SOURCE_AND_INPUT_BINDING_V2.json` SHA: `7db9b5082f170000b8d9685be5685492c824447de5bd557158d2e7aed5154260`.

All previous native, physical safety, last-step arrival and long-term qualification limitations remain. The next step is independent data review and exact-card scientific review. Parent owns factual governance updates and Git checkpointing. This engineering correction is not native release or user acceptance.

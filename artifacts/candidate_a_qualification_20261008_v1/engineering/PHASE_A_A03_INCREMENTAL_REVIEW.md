# Phase A A03 incremental engineering review

Status: offline ready for incremental scientific review. **0 SUMO starts; no release.** A01/A02 remain unlaunched historical cards. Use A03 only after exact review/release. Earlier reviewed source files, original18-test receipt and report are preserved under `reviewed_a02_sources/`; every saved source hash was verified against the A02 receipt.

## Minimal correction

The worker now separately records `last_completed_step_s` and `last_accounted_s` for every segment, including precontrol/external hold. Immediately after motion advances, the failure snapshot marks that advance; subsequent TLS state, internal IDs and crossing observations are retained as soon as available. If any post-step getter, crossing reconciliation or ledger commit fails before accounting completes, the receipt and failure snapshot explicitly state `accounting_complete=false`, `accounting_status=UNRECONCILED_UNSUPPORTED`, the unaccounted completed interval, and prohibit accounting qualification. Existing algebraic C/E/N totals describe only the retained accounted prefix; no unknown actual crossing is fabricated. A pre-step stop and a post-commit failure remain distinguishable.

Prefix naming is corrected: `prefix_total_crossings` covers PRECONTROL plus EXTERNAL_HOLD, while `prefix_crossings_by_segment` provides their separate totals. Existing per-step segment records allow independent reconstruction. No actor timings, inputs, safety gates, demand, upper feedback parameters or resource limits changed.

## Verification

The full previous18 tests plus3 directed accounting-failure tests pass: **21/21**. New tests cover pending TLS/internal/crossing/commit failure flags, precontrol post-step failure versus pre-step stop, and successfully committed post-step failure. Python syntax check passes. All67 protected hashes pass. No SUMO or environment startup test was run.

Final source hashes, commands, log hash and exact five A03 card hashes are in `PHASE_A_A03_OFFLINE_RECEIPT.json`; card manifest is `PHASE_A_A03_FINAL_CARDS.json`. These fresh cards bind the changed worker/test sources. A02 cards and their source snapshots were not overwritten.

Next step: exact incremental science/data review, then root may release **R300 A03 only**. All runtime phase, actual discharge, safety and range qualification remain unverified. All limitations and STOP gates in the prior engineering report remain in force.

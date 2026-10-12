# WAIT implementation V2 — entry before/after STOP correction

2026-10-12 Europe/Berlin. PASS_FOR_BOUNDED_OFFLINE_WAIT_IMPLEMENTATION_PRELAUNCH_REVIEW_V2; data/scientific release pending. Native starts remain zero. This report supersedes the V1 implementation delivery claim only for the identified entry-status coverage; all V1 evidence is preserved.

Scientific prelaunch review found that current_following returns STOP_CURRENT_GAP_BOUND_DENIED without raising. The V1 entry check required a before observation/ID, but checked only the after rejection; before-denied × after-pass could evade the designed STOP. This was a concrete implementation defect, not a change to the safety threshold or research design.

The minimum correction permits only CURRENT_GAP_OBSERVED_WITHIN_BOUND or CLEAR_WITHIN_OBSERVED_LOOKAHEAD on both actual-entry observations. Known denied before/after states append explicit STOP reasons; missing or unknown statuses append UNKNOWN reasons. The after observation is retained even when before denies, so the failed combination remains auditable. Advanced entry and C/E/N accounting are preserved before termination. The current-gap definition, 1.1 m margin, original prospective query/denial, WAIT policy, native signal/model/demand, cycle admission, other monitors, 1207 checkpoint and 1272 end are unchanged.

Actual checks:

- The one new combination regression was executed against the exact preserved V1 adapter. It failed with “ValueError not raised”, exit1; actual source hash, log and failure are retained in PRE_FIX_COMPOSITION_REGRESSION_FAIL_V1.txt. No full old suite or native run was repeated.
- The corrected actual implementation ran the new WAIT directory:11 methods passed, exit0,10.965 s. OFFLINE_TESTS_V3.txt and the current test/source hashes bind this result. The original8/10-test PASS logs and exact V1 source are preserved; their coverage did not include this composition.
- A fresh prepared identity CA_NATIVE_PHASE_R300_S17_WAIT_DIAG01_V2 was generated offline; card SHA c6f8574a57396939b1b4be4c119041e78ce1f652050d5a621c6d121d8def10ac. Exact source/environment/input checks passed. Missing canonical authorization denied before allocation/spawn. No actual native version command or TraCI connection occurred.
- Original DIAG01 card973e0a75... remains byte-for-byte preserved and unconsumed. Full V1 new source/CLI/tests/card/binder/report snapshots are in pre_entry_before_fix_v1; no original result or raw was overwritten. Updated source is an uncommitted hash-bound worktree snapshot, not code claimed tested at historical baseline20e5e83.

The only code changes are entry before/after allowlist enforcement and default preparation of the new versioned identity. The actual bounded diagnostic allowance remains one DIAG01 start and at most one separately evidenced/reviewed repair start; preparation/version changes consume no native count. Caps300s/60s/300MB/5GB, source policy and three-cycle horizon remain.

Next: one independent data recheck and read-only scientific finding closure, then exact-source/card/authority release for DIAG01_V2. No further optional tests, mathematical proof work, new threshold or blind native retry is needed. Actual current-query values, WAIT handling, native yellow/red, full cycles, measured N, final logs and physical behavior are still unverified.

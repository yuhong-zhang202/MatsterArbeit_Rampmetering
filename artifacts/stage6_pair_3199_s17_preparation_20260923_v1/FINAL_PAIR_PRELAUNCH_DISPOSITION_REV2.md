# Final prelaunch disposition — PAIR_3199_S17 rev2

**Status: `PAIR_3199_PRELAUNCH_READY_AWAITING_RESOURCE_AUTHORIZATION`.** Engineering, data/provenance and scientific reviews all PASS. This is prelaunch readiness only; neither run is authorized and no command, reservation, raw output or simulator start exists.

The per-run proposals are 90 s wall-clock and 60,000,000 decimal bytes, scoped independently to each run and marked `PROPOSED_NOT_AUTHORIZED`. They are based on the successful RI3350 retry's recorded 24.465112 s and 21,720,062 payload bytes. The output trigger polls every 100 ms, can overshoot and is not a hard quota.

Cards remain `DRAFT_NOT_AUTHORIZED`. Following separate user resource authorization, new exact card revisions/hashes and current-runtime preflight are still required before any start. If later released, control is first; its raw must pass the full independent `LOW_R_BACKGROUND_ACCEPTABLE` gate before treatment can be separately authorized. No automatic treatment start or retry.

The 23-test predecessor source could not be recovered after replacement; current R02 suite has 16 mock-only tests, including reconstructed Guardian/durability contract cases. No test invokes SUMO. This limits compatibility evidence to static binding and mock behavior.

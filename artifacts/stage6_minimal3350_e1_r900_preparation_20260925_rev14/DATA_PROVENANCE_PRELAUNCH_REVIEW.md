# Data/provenance prelaunch review — E1 qRamp900 REV14

**Disposition: `BLOCKED_DATA_PROVENANCE_PRELAUNCH` (Blocker/Major/required Minor = 1/0/0).** No process was started.

## Verified

- Exact card SHA-256 `cb9bba717e262cdc9328495b6b71b7dff5244094d05c9ad92acfdbcb43e7376b`; card remains prelaunch-only and execution is unauthorized.
- Offline adapter validation passed 1,396/1,396 M common fields; treatment adds only R_flow.0–239. U/X are explicit zero.
- R has 240 identities with departures 540000 through 1496000 ms at 4000 ms intervals. The fixed identity-keyed speedFactor values match the bound historical realized-vehroute source and materialized vector. This is vector reuse, not independent RNG or rate-capacity evidence.
- 18 requested XML targets are unique, have role names matching the output-role set, are under the card output directory, and the output parent is absent. Runtime/card/runner/adapter/input/request/receipt hashes are recorded in the JSON. Resource proposal: 120 s / 100,000,000 bytes / 100 ms polling, slight overshoot accepted, no retry, one maximum start.
- The five focused unit tests pass. Read-only static preflight reports `launchable_now=false`; no Guardian/SUMO/TraCI/netconvert process started.

## Blocker: persisted START request points at prior R720 paths

`START_REQUEST.json` names E1 R900 in its run/card/output fields, but its SUMO `-c` command points to the prior R720 raw output config under `...v15/MINIMAL3350_R720_DELAYED_S17/outputs/`. Its `reservation_path` likewise points to the R720 REV7 consumption record. Correct E1 bindings should use the v16 E1 output config and this REV14 package's E1 consumption file. The request receipt is internally hash-consistent with those stale bytes. Current static preflight stops at the missing-review gate and does not inspect this persisted request; focused tests do not test stale command/reservation paths.

A fresh immutable revision must rebuild and bind the START request and receipt and add negative tests for both path mismatches before this review can PASS. Evidence and hashes: `DATA_PROVENANCE_PRELAUNCH_REVIEW.json`.

# Data/provenance prelaunch review — E1 qRamp900 REV15

**Disposition: `PASS_DATA_PROVENANCE_PRELAUNCH` (Blocker/Major/required Minor = 0/0/0; High confidence).** Read-only review; no Guardian/SUMO/TraCI/netconvert process started. This review does not authorize execution.

## Checks

- Exact card SHA-256 `95b577a8b62bb79cccbcba8aa04869a96d3c04fa9dcc7db6d38489627d94b148`; card is `PRELAUNCH_READY_AWAITING_AUTHORIZATION` and `execution_authorized=false`.
- The adopted D-008 entry gate is met: 3350.4 R0 control is `LOW_R_BACKGROUND_ACCEPTABLE`; matched R720 treatment is `NO_WITNESS`. D-008 is Stage 6 exploratory only, and the plan itself grants no run authorization.
- Offline adapter validates 1,396/1,396 M identities and all bound fields against common manifest/control demand. U/X are explicit zeros; treatment-only addition is R_flow.0–239. R schedule is 540000–1496000 ms every 4000 ms inside `[540,1500)`.
- R speedFactor vector lineage is hash-bound to historical realized vehicle records and materialized by identity. This is fixed vector reuse, not fresh stochastic evidence or capacity evidence.
- START request, receipt, card, runner, runtime and output paths reconcile: config points to the E1 v16 output path; reservation points to REV15 consumption. All 18 output roles are unique, under the absent E1 output directory; reservation is absent.
- Resource proposal is 120 s / 100,000,000 bytes / 100 ms polling, slight overshoot accepted; no retries, max one start. The adopted plan's unique-entry cutoffs (t=1440 and 1500), three positive auxiliary bins by t≤720, and stop-on-witness/non-evaluable/no-exposure-scaling rules remain in force.
- Nine focused tests pass, including stale R720 config/reservation negative fixtures. Read-only static preflight reports `launchable_now=false` pending required reviews and separate authorization.

Full hashes and field-level evidence are in `DATA_PROVENANCE_PRELAUNCH_REVIEW.json`. Output staging is not materialized before launch; the persisted request binds its future E1-specific output config path.

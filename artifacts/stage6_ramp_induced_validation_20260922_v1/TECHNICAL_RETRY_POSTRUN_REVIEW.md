# RI3350 Technical Retry — Post-run Review

Date: 2026-09-23  
Run: `RI3350_CTRL_S17_technical_retry1`  
Overall scientific disposition: **NOT EVALUABLE**  
Engineering: **PASS (0/0/0; High)**  
Data application: **NOT EVALUABLE**  
Scientific review: **NOT EVALUABLE (Blocker/Major/required Minor 1/0/0)**

## Execution and provenance

The exact card is `control_card_FINAL_RI3350_CTRL_S17_technical_retry1_REV1.json`, SHA-256 `28be8560664c75f0176b048206f50b50392c3ed1c03a64dae02d2e01c0daf91e`. Its read-only preflight passed and bound the same digest. Exactly one retry start was consumed. SUMO 1.26.0 exited normally with code 0 after 24.465112 s, completed the 2700 s horizon, and hit neither stop trigger. The final reservation is `FINAL_STATUS_HANDED_OFF`, `retry_allowed=false`; no further start is permitted.

Execution receipt SHA-256: `9d793f26cdce43f6f6856398d0c3e127a3f51bb0f50856ff391df1479f0e199c`. Output-manifest SHA-256: `e72ee6da030083da1ce3c96996c7169d80e7734d71e788eb3e8b326d11cfb3cd`. The manifest inventories 25 files, including all 18/18 required roles with matching size and SHA-256. Payload is 21,720,062 bytes. These records establish a technically complete execution, not scientific eligibility.

## Data application and scientific limit

The R04 adapter was applied once to this run's immutable raw directory. It failed closed during `build_lifecycle` at `M_flow.16`, before producing a lifecycle ledger, locked classifier outputs, event-source receipt, PRE/control screens, or processing manifest. The saved `application_receipt.json` is `NOT_EVALUABLE_RAW_COMPLETENESS` (SHA-256 `d8800d5c0b3d33e5003d44049e9422ef901e7a5a67c6e64739e285537610dd2a`); `raw_completeness.json` is `FAIL` (SHA-256 `0a991e5a8cb383196aaed59d2563b4850c3d1103e80e59248742b39f5e58f913`). No adapter rerun was made.

The reconciliation assumption reconstructed ideal flow departures as `begin + index × (end−begin)/number`. For `M_flow.16`, this gives 17.191977 s, while `vehroute.depart`, `tripinfo.depart`, and the first FCD appearance are 18.00 s; `tripinfo.departDelay` is 0.82 s. The reconstructed departure difference is 0.011977 s, just above the adapter's 0.011 s tolerance. The same condition was reported for 1373/1396 M-flow vehicles, with maximum residual 0.697507 s; U/X had no such mismatch. This is evidence that the adapter's schedule reconstruction may not match the simulator's recorded departure semantics. The exact SUMO flow scheduling semantics were not independently verified, so raw corruption cannot be ruled out.

A bounded manual census reported 1,621 scheduled IDs in both `vehroute` and `tripinfo`; M/U/X counts of 1,396/150/75 all inserted and arrived; zero unfinished vehicles; no R vehicles in demand, route/tripinfo, or FCD; and 2,700 unique FCD labels 0–2699 with 117,349 samples covering all 1,621 IDs. These checks do not replace the failed formal lifecycle reconciliation.

The independent scientific reviewer concluded that no traffic, classifier/event, no-event, controller, baseline-suitability, G6, mechanism, or thesis-level claim is supportable from this application. No classifier state or event outcome has been established. Stage 6 remains PARTIAL, O2 remains NOT_RESOLVED, and the formal protocol remains unfrozen.

## Review dispositions

- **Engineering post-run:** PASS, Blocker/Major/required Minor 0/0/0, High confidence. Card/preflight/reservation/receipt/manifest identity, one-start boundary, full-horizon normal exit, resource triggers, and all required output hashes reconcile.
- **Data post-run:** NOT EVALUABLE. R04 stopped at the schedule/departDelay discrepancy; raw data are preserved, and classifier outputs were not generated.
- **Scientific post-run:** NOT EVALUABLE, Blocker/Major/required Minor 1/0/0. Confidence is High that scientific outcomes cannot be claimed from current processed evidence; Moderate that the discrepancy is an adapter assumption rather than a raw defect.

No scientific inputs, classifier, geometry, demand, TLS, vehicle behavior, or formal protocol were changed. No further SUMO start, technical retry, transition, seed23, Point 2/3, B, or C run was launched.

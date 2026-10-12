# Independent data review — proposed SMOKE04 wall budget

**PASS_FOR_BOUNDED_OFFLINE_BUDGET_DATA_INTEGRITY_ONLY. No required unresolved data finding.** This is a technical/exploratory planning review, not formal results, safety qualification or evidence that 300 seconds reaches the target.

## Context and scope

Reviewed AGENTS.md; current PROJECT_STATE; DECISIONS; recent relevant WORKLOG; EXPERIMENT_PROTOCOL.md (0 bytes, explicitly known/unfrozen). Stage 6 closeout and historical STOP3, Candidate A NOT_QUALIFIED, A1 UNRESOLVED and 900 NOT_TESTED remain. User authorized only investigation/minimal proposal/new card, explicitly no SUMO this round. Baseline 22ec93c7b54d4ea15f55284026ded6c414de605b. Current SMOKE03 authorization consumed and target not reached at 1157 seconds. Historical prepared-state entries were not interpreted as current runtime permission. Only this new processed-data namespace was written; governance, production sources, engineering evidence and raw files were not modified.

## Inputs, deterministic transformations and actual verification

Engineering INPUT_BINDINGS_V1.json SHA a261ddaaee2baa006d34e333d70c96b11d6bf4f717329e250033fb15495031ec binds 55 files. The current new card SHA is **1fe30783bb04fb79a3fc7e17b21e946be9cb0c58223258dd7a51dfda3898b086** for CA_NATIVE_PHASE_R300_S17_SMOKE04, PREPARED_NOT_RELEASED. The independent checker verified those 55 hashes, 536 protected files, 22 old source files and 25 new-card sources; public input/network hashes; unchanged environment declaration; and no new executable authorization/release/raw directory. Environment hashes were compared as bound declarations, not newly surveyed or version-executed.

Demand bytes are identical. XML input comparisons allow only the exact new identity/path substitutions; all remaining bytes match. Specification differs only in run_id; resource limits only wall_limit_s 180→300. Startup60, run300,000,000 bytes, free5,000,000,000 bytes, dt1, activation1200, end1207, first-red mandatory pause/no continuation and prior phase configuration remain. New bridge equals old reviewed body with one profile import substitution. Both synchronous and sampled watchdog consumers obtain the same card resources. Static reading confirmed exact non-boolean integer limits/provenance/source/environment gates and release checks. Full native behavior is untested.

Actual command: `.venv/bin/python data/processed/candidate_a_native_smoke_budget_20261012_v1/independent_budget_review.py --local-raw`. Corrected V2 exited0, preserving stdout/stderr SHA and result receipt. Raw manifests additionally verified **53 / 58 / 62** immutable SMOKE01/02/03 file hashes; SMOKE03 raw sumo.log independently confirms Duration154.78s. All raw files are read-only, local-only; this is not remote access or recreation evidence. Default public checker does not read raw files or require executable authorizations; it reviews committed raw manifests and selected public receipts. The default branch was inspected but **not separately executed**, and no clean checkout was executed or claimed.

## Budget origin and arithmetic

Runner line23 contains the original hardcoded wall180; archived Issue4 body has neither 180 nor wall wording. The engineering origin supplement identifies first tracked commit30e547cbca1fa7ef97a0c9b0e043b4d870a1ab98. Subsequent cards explicitly bound those resources, so they were valid constraints for their approved runs. Targeted sources do not establish a scientific/safety threshold or empirical calibration for this bridge; no exhaustive email/communication absence claim is made.

Independent arithmetic from bound SMOKE03 startup24.95967800001381s, native Duration154.78s and 1157 verified steps:

- Observed-startup illustration: 24.95967800001381 + 154.78×1207/1157 = **186.42852847538114s**.
- Maximum-startup illustration: 60 + 154.78×1207/1157 = **221.46885047536733s**.
- 300-second illustrative headroom = **78.53114952463267s**; 240-second headroom18.531149524632667s.

These are whole-prefix proportional planning illustrations, not predictions, measured marginal cost, upper bounds, confidence intervals or evidence240 is inadequate. Remaining50 steps include previously unobserved admission/control and increasing population; timer scopes differ. Native Duration/TraCI duration are not pure CPU/hotspot shares. SMOKE02 and03 implementations differ, so their completion counts cannot establish a paired causal speedup. A finite300s proposed engineering allowance is compatible with the bound evidence, but does not guarantee completion or require further optimization.

The bridge wall clock starts after static checks/output reservation/source snapshots, before capture/worker/native spawn/connect, including startup and loop checks/ACK/logging/reconciliation. Cleanup may still be watched. Preparation before started and final logging/receipt after watchdog close are excluded. Between-step check and0.2s sampled watchdog are not hard real-time limits on entire CLI duration. No safety check or1207 stop changes follow from a longer resource clock.

## Preserved failures and test coverage

Engineering five V2 tests PASS and prepare/card check exit0 were reviewed from bound logs/command receipts; **not rerun by data review**. Original V1 fake worker lacked observe, producing four actual error subcases; original test/source/receipt retained. Engineering preservation path failure is retained. Old eight cache/query tests are reused through unchanged bound source/body/test bytes and their genuine old PASS; not new execution of those tests or native validation.

Independent checker V1 exited1 because it incorrectly required the historical eight-test log to end in OK. That log correctly contains OK followed by an archived fake benchmark. Exact failed output/receipt and checker preimage PRE_LOG_SUFFIX_FIX_V1.py are preserved. The smallest correction checks the standalone OK line and eight-test count while retaining benchmark text; V2 passed. No engineering, raw, safety or budget evidence changed. No exclusions, missing values or zero substitutes were introduced. Earlier controlled-service metrics remain null/NOT_OBSERVED, and historical failures remain visible.

## Limits and safest next step

No SUMO/native version/actual TraCI/native starts, new profiling/optimization, formal protocol changes, safety-contract changes, guard relaxation or additional A1 proof. Native online four-stream logging still excludes parent CLI compatibility warning output, captured only finally; no universal logging or warning-free claim. Old STOP3 and A1/Candidate A qualification boundaries remain. The safest next step is read-only scientific review, then user review of this exact new card and finite budget; any future native start requires a separate explicit source/card authorization. A further abort must be preserved, not automatically retried or escalated.

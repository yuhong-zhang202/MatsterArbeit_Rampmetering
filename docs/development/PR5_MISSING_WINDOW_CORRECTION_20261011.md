# PR #5 missing-window correction — 2026-10-11

**P2 data-expression repair completed / awaiting user review.** Original PR #5 / Issue #4; no new Issue. Data and scientific review PASS for this correction. **Candidate A NOT_QUALIFIED; current-contract STOP3 remains;900 not tested.** No SUMO, guard/contract, actor, environment or research-design change.

## Defect, authorization and controlled versioning

[GitHub P2 finding](https://github.com/yuhong-zhang202/MatsterArbeit_Rampmetering/pull/5#discussion_r4239491964): V2 used sum(empty)=0 for five entirely unobserved windows, contradicting the earlier no-zero-imputation claim. User explicitly authorized direct PR5 repair, versioned regeneration, three-state regression and data_analyst→scientific_reviewer. [Authorization](../../artifacts/candidate_a_qualification_20261008_v1/review_fix_20261011/AUTHORIZATION.md).

Minimal analysis repair: when selected step set is empty, C_observed/C_applied_observed/E_observed/N_observed and command_latency/quantization/physical_shortfall are **JSON null / CSV blank**. CSV has no native null type; blank is declared missing. Counts/coverage/status metadata stay numeric0/false/incomplete. Observed numeric zero is not converted to missing. Original6s record remains C/applied C≈.5,E0,N1,differences0/≈.5/−1; no full-window rate qualification.

New authoritative [gate V3](../../data/processed/candidate_a_qualification_20261008_v1/R300_A07_ACTUAL_DATA_GATE_V3.json), [service CSV V3](../../results/tables/candidate_a_qualification_20261008_v1/R300_A07_SERVICE_WINDOWS_V3.csv) and7otherCSV V3; former outputs/old signedreviews remain byte-identical. The old no-zero-imputation statement is explicitly superseded, not silently rewritten. Original analysis source is preserved in review_fix_20261011/pre_fix_source and at commit30e547cbca1fa7ef97a0c9b0e043b4d870a1ab98. Exclusive-create/identical-readback output behavior prevents silent overwrite.

## Validation and exact change

- 6/6offline regression tests: measured zero, unobserved,6spartial,JSONCSV roundtrip, original inclusive10%/supply rule, overwrite rejection. [Test receipt](../../data/processed/candidate_a_qualification_20261008_v1/R300_A07_REGRESSION_RECEIPT_V3.json) records tested source/test SHA and Python3.13.0. Command `.venv/bin/python -m unittest discover -s tests/candidate_a_analysis_20261011 -v`.
- Reanalysis command `.venv/bin/python data/processed/candidate_a_qualification_20261008_v1/audit_r300_a07_actual.py`; verification command `.venv/bin/python data/processed/candidate_a_qualification_20261008_v1/verify_review_fix_v3.py`. Immutable local raw required; no simulation/native API invocation. No additional test rerun for publishing.
- 283historical bindings including113raw unchanged;45A07rawmanifest/67protected/1206steps/21170prestates rechecked. Other7CSV byte-identical. CSV and JSON each change only35service measurement cells (five×seven); entire6sfirstrecord unchanged. [Exact delta](../../data/processed/candidate_a_qualification_20261008_v1/R300_A07_REVIEW_FIX_DELTA_V3.json).
- [Data review V3](../../data/processed/candidate_a_qualification_20261008_v1/R300_A07_ACTUAL_DATA_REVIEW_V3.md) and [15-file binding](../../data/processed/candidate_a_qualification_20261008_v1/R300_A07_FINAL_DERIVED_BINDINGS_V3.json): SHA2567e1aa4ff8f9f6823e7209194dfec1b669c23f17b8c42a91cd8275ea189a523dc. Binding's pending scientific status describes its creation checkpoint; the subsequent final independent science below supersedes that operational status.

## Independent scientific reassessment

[Final science V3](../../artifacts/candidate_a_qualification_20261008_v1/review_fix_20261011/FINAL_SCIENTIFIC_REVIEW_V3.md): **PASS_FOR_PR5_P2_DATA_EXPRESSION_CORRECTION**, delivery findings0/0/0. Direct raw step sums[6,0,0,0,0,0], FCDcrossing and42guard coverage independently checked. Guard refusal at1206s unchanged: R_flow.1 gap1.0019991898m versus required1.1459706723m, margin−.1439714826m; failed red motion step not executed. Existing bounded engineering diagnosis found no preserving-contract minimal repair; **current-contract STOP3 still applies**.

Not evidence of SUMO native red danger, inevitable collision, Candidate A universal infeasibility or900physical impossibility. Guard1.1m/reaction/braking remains a declared conservative sufficient condition, not a proved necessary/empirically calibrated/native-equivalent rule. Unverified fullcycle/service/native secureGap aspects remain disclosed. All six fullwindow errors null;300partial, fourrates held/unrun; highestverifiedrateunknown. Original3SUMOstarts unchanged, correction adds0. No new formal evidence, sweetspot, scope decision or B/fallback trigger.

## Delivery and handoff

PR #5 stays Draft, stacked base codex/issue-2-actuator-investigation; PR1/3 unchanged. Only analysis, tests, new-version derived evidence and factual documentation updated. AGENTS/DECISIONS/protocol/old signedreview/raw/oldoutputs untouched; unrelatedMemoryCore/privateemail excluded. Test ran before commit; publication verifies tested source/test bytes against delivery commit rather than claiming a new test run against a laterSHA. Fullraw remains local per originalmanifest; newV3tables/reports/receipts online inPR.

Subagent routing: simulation_engineer not required (analysis-only correction, no simulation code/config/execution); data_analyst implemented/tested/reprocessed and validated preserved evidence; scientific_reviewer independently checked measurement/STOP3. Findings addressed; qualifications remain incomplete. Next user/Chat reviews correction. **下一步建议不构成执行授权。** No GitHubreview retrigger/auto-resolution/merge/Issueclose.

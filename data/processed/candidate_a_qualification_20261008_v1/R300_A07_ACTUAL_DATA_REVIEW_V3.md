# Independent PR #5 P2 data correction review — V3

2026-10-11. **Data correction PASS; Candidate A qualification remains NOT_QUALIFIED_SAFETY_GUARD_STOP.** This is an original Issue #4 / PR #5 exploratory engineering correction, not a formal analysis or new scientific design. The authoritative corrected data gate is `R300_A07_ACTUAL_DATA_GATE_V3.json`; current tables are the eight `R300_A07_*_V3.csv` files. Older gates, CSVs, signed reviews and all raw records remain intact.

## Context, authority and historical correction

Reviewed AGENTS.md, the data analyst role, PROJECT_STATE.md, DECISIONS.md, EXPERIMENT_PROTOCOL.md (0 bytes/unfrozen), relevant WORKLOG history, user correction authorization and PRE_FIX_BINDINGS.json. Stage6 remains closed; D-018 allows formal-design preparation, not formal execution. The authorized work is representation of missing service observations, controlled versioning and offline regression. No actor, runner, safety contract, SUMO environment, configuration or research decision change was made.

The former V2 audit computed `sum(empty)=0` for C/applied C/E/N and their differences in five wholly unobserved windows. Its accompanying claim that no missing result was zero-filled was incorrect. That statement is explicitly superseded here; the signed historical review is preserved without alteration. The original source is recoverable at base commit `30e547cbca1fa7ef97a0c9b0e043b4d870a1ab98`, SHA-256 `986a298b1e3345cb4c822d6934708c8a7d20ed19c7e55135edb71f0993084521`. V3 fixes measurement expression, not observation completeness or qualification.

## Inputs and transformation

The same immutable CA_FIXED_R300_S17_A07 raw records were independently reprocessed by `audit_r300_a07_actual.py`, using Python standard library only. No simulation was started and no actor or native API was imported. Reproduce:

```sh
.venv/bin/python -m unittest discover -s tests/candidate_a_analysis_20261011 -v
.venv/bin/python data/processed/candidate_a_qualification_20261008_v1/audit_r300_a07_actual.py
.venv/bin/python data/processed/candidate_a_qualification_20261008_v1/verify_review_fix_v3.py
```

The generator writes V3 names exclusively; an existing artifact must be byte-identical or the command fails rather than overwrites it. Historical source snapshots and output versions are not regenerated in place. JSON missing observations use literal `null`; CSV, which has no native null type, uses an empty cell. Numeric measured zero remains numeric zero/`0` or `0.0`; no `NaN` or numeric sentinel represents missing data.

Window selection remains `begin <= time_begin_s < end`, with unchanged duration, supplied-screen and inclusive10% tolerance. For no selected step, all seven fields C_observed/C_applied_observed/E_observed/N_observed/command_latency/quantization/physical_shortfall are null. Metadata observed_steps=0, full_window=false, sustained_supply_verified=false, status=NOT_TESTED_INCOMPLETE_WINDOW and tracking_error=null remain unchanged.

| Window (s) | Recorded steps | C / applied C | E / N | Latency / quantization / physical term | Tracking |
|---|---:|---|---|---|---|
| [1200,1500) | 6/300 | ~0.5 / ~0.5 | 0 / 1 | 0 / ~0.5 / −1 | null; incomplete |
| [1500,1800) | 0/300 | null / null | null / null | null / null / null | null; incomplete |
| [1800,2100) | 0/300 | null / null | null / null | null / null / null | null; incomplete |
| [2100,2400) | 0/300 | null / null | null / null | null / null / null | null; incomplete |
| [2400,2700) | 0/300 | null / null | null / null | null / null / null | null; incomplete |
| [2700,3000) | 0/300 | null / null | null / null | null / null / null | null; incomplete |

The first record remains exactly equal to V2, including floating representation `0.49999999999999994`. E−N=−1 still represents an unfinished nominal packet at the stop boundary, not completed-cycle overservice or physical service loss. It is not a six-second rate qualification.

## Independent checks and exact delta

Six regression tests pass: observed numeric zero; wholly unobserved; six-second partial sums; JSON/CSV missing-versus-zero roundtrip; original inclusive10% and supply screen; exclusive-create / identical-readback / mismatch rejection. No SUMO test is required for this expression-only repair. Test command and source/test hashes are in `R300_A07_REGRESSION_RECEIPT_V3.json`.

The regenerated audit independently verifies45 raw manifest files,67 protected baseline hashes,1206 consecutive FCD/TLS/native-summary steps,21170 pre-state observations, all seven API requests, one green crossing and42 prospective-red witnesses. Guard witness R_flow.1 remains positive speed0.0457382295m/s, gap1.0019991898m, required1.1459706723m and margin−0.1439714826m. The rejected next red motion step remains unexecuted. No observed collision/teleport/emergency is promoted to safety qualification.

`R300_A07_REVIEW_FIX_DELTA_V3.json` proves283 historical bindings unchanged, including113 raw files across the three attempts. Exactly35 service measurement cells change in both CSV and JSON; every other original service field and the first entire record match. The other seven regenerated CSVs are byte-identical to their historical counterparts. All other original gate fields and raw/release bindings match, apart from the intentional analysis-source hash and explicit V3/supersession/correction metadata. No raw result, prior audit or model snapshot was edited.

All4050 planned IDs retain their original classification:1467 inserted,1267 arrived,200 unfinished in-network,73 due source backlog and2510 future scheduled. No cost or effect was recomputed or inferred.

## Qualification and interpretation boundary

R300 has only six qualification seconds and no completed cycle or full300s window; actual service and phase qualification remain NOT_PASSED. R450/R600/R750/R900 remain unrun/held. Highest verified safe rate remains unknown, and900 is not tested. Three original actual starts and zero complete qualification runs are unchanged; this correction adds zero starts.

The data expression defect does not alter the prospective guard evidence or the bounded engineering diagnosis supporting the prior current-contract STOP3 disposition. Independent scientific review must confirm that conclusion after inspecting V3; this data review does not itself decide scientific STOP. Neither the old run nor V3 establishes SUMO native red unsafety, inevitable collision, Candidate A universal infeasibility, or900 physical impossibility. The1.1m/reaction/braking guard remains a declared conservative contract with its original source/validation limitations. No threshold or safety assumption is relaxed.

Safest next step: independent read-only scientific re-review, then parent updates the original PR #5 with this bounded correction. No future run, Candidate B, formal parameter, protocol freeze or user acceptance follows from this review. Governance documentation remains parent-owned.

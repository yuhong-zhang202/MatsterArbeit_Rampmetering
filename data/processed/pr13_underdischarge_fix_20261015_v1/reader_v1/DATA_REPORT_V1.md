# Independent narrow service-scope audit

Result: PASS_OFFLINE_SYNTHETIC_OBSERVATION_ACCOUNTING_ONLY. No material new repair defect found within the assigned seam. This does not pass service qualification: complete N0/N1 remain diagnostic target failures with unestablished cause, and ordinary constrained-service continuation remains unavailable.

## Context and evidence

Read AGENTS.md, current PROJECT_STATE (P1 under repair), DECISIONS current approved boundaries, empty/unfrozen EXPERIMENT_PROTOCOL, relevant recent WORKLOG and engineering/science/feedback records. Stage6 exploratory closeout stands; A1 UNRESOLVED, Candidate A NOT_QUALIFIED. Formal parameters remain unknown. This is offline exploratory interface verification only.

Engineering binding SHA256 efb8fa680974391080ded3318f8307c2c7a5f5758f176b110e2edebcf50178a9 matched the delegated source. New reader: scripts/pr13_service_scope_audit_20261015/audit.py. Source and saved synthetic data hashes are in DATA_BINDING_V1.json. Existing native raw, 154 executed sources/cards and old readers were not modified or reinterpreted as passing a new version.

## Method and retained scope

Only four existing run_fixture cases were executed through the new adapter and actual inherited diagnostic loop, using fake movement: empty, one exact-end, existing two-car terminal partial and terminal hard braking. Fixture temporary files are removed by the existing fixture; public evidence contains only controlled ACK intervals from1200 onward, chronological ledger events, receipt and small setter history. ACK fields are reduced explicitly to interval/readback time, accounting completeness, accounting, crossing observations, post-world identities and status. These are synthetic observations, not native logs or independent physical trajectory evidence. No native data excluded or reprocessed.

Reader independently integrates the latest chronological REQUESTED rate over each acknowledged one-second interval, reconstructs unique N from ACK crossing intervals joined to post-world identity, and calculates E=2 times acknowledged elapsed complete packet periods. Per-step and final accounting are compared, never used as the reconstruction inputs. Assessments require complete context coverage and C/E/N/residual consistency. Packet N<2 is classified separately from observation-accounting validity. A terminal partial has no complete-target comparison. Hard braking retains a hard/unknown stop and no neutral target assessment. Reader checks no next packet selection/setter/advance after neutral stop.

Actual code chain inspected: new bridge rejects purpose/adapter before inherited loop; original loop invokes new ledger.begin_step, adapter.prepare_step, fake simulationStep, adapter.reconcile_step. New adapter delegates original full reconciliation first, assesses a completed packet only on success, and stops immediately. Wrapper finally writes the dedicated receipt/events including terminal assessment. This preserves exact-end evidence; inherited stopped reconcile retains final ACK. It provides no launch function/card or general-use authorization.

## Exact results

- Empty supply, requested end1218: acknowledged STOP1210, C25/12, E2, N0, C-N25/12. Complete target not met, cause unestablished; no new packet/setter/advance.
- One vehicle, exact end1210: acknowledged STOP1210, C25/12, E2, N1, C-N13/12. Same neutral target failure persisted at endpoint, no next packet/setter/advance.
- Existing two-car partial, end1212: C5/2, E2, N4, C-N−3/2. One complete packet plus one partial; terminal receipt assessment null, no N2 assertion on partial. Four distinct fake crossings, not a physical rate claim.
- One vehicle with original final braking fault: STOP1210, C25/12, E2, N1, C-N13/12. HARD_OR_UNKNOWN_GATE_STOP takes priority; no diagnostic-target assessment falsely downgrades it.
- Existing pure-ledger pending example: 750 for1s then900 for2s independently gives C17/24, E0, N1; pending first application null, partial unassessed. No application/nominal quota invented.

Nine focused saved-data corruptions rejected: missing ACK, duplicate ACK, malformed interval, duplicate crossing, false completed/PASS status, corrupt C, missing terminal assessment, post-stop setter and false formal eligibility. No rates/seeds/experiment matrix was added. Existing engineering five-method suite was not rerun.

## Commands and verification history

`.venv/bin/python scripts/pr13_service_scope_audit_20261015/audit.py --output data/processed/pr13_underdischarge_fix_20261015_v1/reader_v1`

First invocation completed all four cases, nine mutation checks and pending example, saved AUDIT_RESULT_V1.json, then exited1 during hash binding because relative output paths were passed to relative_to(absolute ROOT). Exact original reader and concise failure receipt are retained as ATTEMPT1_READER.py and ATTEMPT1_FAILURE.txt. Fixed only reader output path normalization. A separate import/audit command re-read the four saved bundles using corrected reader and wrote the hash binding: exit0, SAVED_DATA_REAUDIT_AND_BINDING_PASS. No fake loop was rerun for this bookkeeping correction. Final standalone fresh-output main was not rerun; the affected saved-data read/audit/binding path was validated directly.

## Limits and next step

The fixtures establish accounting/interface behavior, not native vehicle readiness, receiver capacity, physical safety, service availability, long-horizon debt recovery, or qualification. No cause of underdelivery is inferred. Original C and residual remain visible, and under-target recovery is not attempted because the diagnostic stops. Formal/general runtime entry is rejected; this repair does not supply a usable general constrained-service controller. Old153/154 reader validity is unchanged, and future native use needs new source binding/readers/reviews and execution authority.

Documentation impact: root should minimally log this material repair/data check and retain the qualification limitation in STATE/WORKLOG. This agent did not edit governance. Safest next step: read-only scientific final review of this source/data binding, then authorized publication/new targeted Codex review. No additional validation requested by this report.

# Candidate A — single native-phase smoke result

**Technical smoke FAILED / NOT_REACHED: stopped before the first motion and controlled yellow/red checkpoint. One native start consumed; no retry or continuation. Engineering, data and scientific reviews complete; awaiting user/Chat discussion.**

## Authority and exact run

The user explicitly accepted delivery `e85b3c815ea6fef1bc054cd8249e3a138fc0cac0` and authorized one `CA_NATIVE_PHASE_R300_S17_SMOKE01`, with mandatory stop at1207s, earlier stop on anomaly/logging unknown, complete evidence retention and no automatic retry/continuation. [Verbatim authorization](../../artifacts/candidate_a_native_smoke_execution_20261011_v1/USER_AUTHORIZATION_RECORD.json). Source bytes match previously tested `87d905b0c6aa6852447e21dfb0eb0ee4f4cd8789`; no implementation changes were made in this task.

Exact card SHA-256: `7f74fa8cecb94a81e0d86a2ac2422fd10fa0ffcb3d7cf39a16bfa7d7f53b89d0`. Nominal active demand M3600/R900/U360/X180veh/h; metering command300veh/h, seed17, step1s, G3/y3/r18, R starts600s, controlled activation1200s, intended first-red stop1207s. R300 in the run name denotes service command, not ramp demand. This is a technical diagnostic, not exploratory reopening, pilot or formal evaluation.

Static installed metadata: Python3.13.0, TraCI/SUMOLib1.26.0, sumoITScontrol0.1.0, binary/dependency/input/source hashes match reviewed card. No installation or separate native version command. Formal protocol remains0B/unfrozen.

## Actual operations and resource gate

1. The first static check blocked with4,861,722,624B free, below the unchanged5,000,000,000B requirement. No native start/raw allocation occurred at that checkpoint. [Original receipt](../../artifacts/candidate_a_native_smoke_execution_20261011_v1/engineering/PRELAUNCH_STATIC_RECEIPT.json).
2. The primary agent preserved its earlier clean temporary checkout in a verified full recovery Git bundle and removed only that clean copied checkout. Original project/source/raw and all recorded test outputs remain. [Recovery binding](../../artifacts/candidate_a_native_smoke_execution_20261011_v1/TEMP_CHECKOUT_RECOVERY_BINDING.json), [cleanup result](../../artifacts/candidate_a_native_smoke_execution_20261011_v1/TEMP_CHECKOUT_CLEANUP_RESULT.json). The original actual-code receipt still describes the checkout tested at that historical checkpoint; it was not rewritten. A metadata mkdir collision before authorization writing was preserved separately, not counted as a native retry.
3. Static V2 check passed at6,707,851,264B free. Canonical exact-card authorization/release bound the user request and prior engineering/data/scientific implementation reviews; these reviews are not pre-run safety certification. [V2 receipt](../../artifacts/candidate_a_native_smoke_execution_20261011_v1/engineering/PRELAUNCH_STATIC_RECEIPT_V2.json).
4. Engineering invoked the reviewed CLI once with local socket permissions and `PYTHONDONTWRITEBYTECODE=1`.248 connection attempts targeted **one** child; startup connection took25.924s. No repeated SUMO launch, changed configuration or resumed identity. Native PID was not persisted; it remains unknown rather than reconstructed. [Actual command/exits](../../artifacts/candidate_a_native_smoke_execution_20261011_v1/engineering/EXECUTION_RECEIPT.json).
5. The bridge captured native stderr before first motion and stopped, closed TraCI and the owned process, finalized original logs and froze raw. CLIexit1; nativeexit0. A native normal exit does not mean the diagnostic checkpoint passed.

## Confirmed observation and stop reason

stderr contains17 lines, one each for CA_C8 through CA_C24, with this warning:

> Warning: Phase 2 only loops backs to itself in tlLogic 'ramp_mid', program 'CA_C8'.

[Exact public warning extract](../../artifacts/candidate_a_native_smoke_execution_20261011_v1/engineering/RUNTIME_NATIVE_WARNING_EXTRACT.txt), byte-identical to raw stderr; SHA-256 `6ab8072a52bed5930fc04c47344ac10243705e76cf237aa25161bd55340df02f`.

Actual bridge status: `STOP_UNKNOWN_LOG_COVERAGE_OR_NATIVE_MESSAGE`; error: `ValueError:native stderr before motion`. Final log status: `UNKNOWN_OR_NATIVE_MESSAGE`. STARTUP_CONNECT_ACK first captured no stderr; PRE_MOTION_AFTER_CONTROL_AND_OBSERVATION captured1443 bytes. This establishes capture order/stages, not the unique cause or precise native emission time. Initialization/configuration origin is a supported interpretation, while delayed emission/read timing remains unresolved. No warnings were suppressed or whitelisted.

Native log reports started0.00/ended0.00; no simulation-step ACK file exists. The time0 pre-step snapshot is distinct from a completed motion interval. Raw completed/accounted fields remain null. Initialization603, activation1200, first red1206→1207 and all later complete cycles/service windows were not reached.

The phase library intentionally includes holding-red self-loops, but these warnings and this unexecuted movement test establish neither unsafe native red nor full Candidate A infeasibility. Collision/emergency-braking/red-crossing behavior at the intended transition was not evaluated.

## Measurement and evidence boundary

Raw failure accounting contains initialized C/appliedC/E/N and derived zero accumulators. With no completed interval or service observation, those are **internal initialization values, not measured zero service**. Independent processed reporting must use null/NOT_OBSERVED for unobserved measurements. No rate, safety or capacity qualification can be inferred. No formal effect comparison is available.

Independent parsing found16 XML outputs with empty bodies, plus three tripinfo termination records: M_flow.0/U_flow.0/X_flow.0, each depart=-1/arrival=-1/vaporized=end. These are scheduled-but-not-inserted termination records, not completed trips or travel-cost measurements. `tls_states.xml` is0B and not valid XML. They remain in the frozen manifest; normal native exit and final log-file EOF do not imply a complete traffic-output dataset. Costs, motion safety and service metrics remain unobserved/null.

Whole final files were captured after normal child exit0; capture/failure preservation worked for this warning stop. Conditional CERR/ACK assumptions, source-to-installed-binary/compiler equivalence and universal per-step native logging are not certified by a run that executed no motion. Post-monitoring does not prevent an already executed violation. General3s yellow adequacy and joint vehicle safety remain unresolved.

Raw location: `data/raw/candidate_a_native_smoke_bridge_20261011_v1/CA_NATIVE_PHASE_R300_S17_SMOKE01/outputs`. Engineering froze53 files,1,804,472B. [Manifest](../../artifacts/candidate_a_native_smoke_execution_20261011_v1/engineering/RAW_FINAL_SHA256.json), SHA-256 `0e0857bb444008531d9e98fdde57f54620185a5794932256fe0188a0c21d631c`; [engineering binding](../../artifacts/candidate_a_native_smoke_execution_20261011_v1/engineering/ENGINEERING_DELIVERY_BINDING.json). Raw/source/input/card/old evidence remain immutable. Raw is stored locally and is not automatically uploaded; the public selected extract, receipts/manifests and derived audit provide reviewable summaries without claiming all raw is remotely available.

## Reviews and handoff

[Engineering postreview](../../artifacts/candidate_a_native_smoke_execution_20261011_v1/engineering/ENGINEERING_POSTREVIEW.md): actual failure is a technical stop;536 protected files and7 R2 files unchanged. [Independent data review](../../data/processed/candidate_a_native_smoke_execution_20261011_v1/FINAL_DATA_REVIEW.md): `PASS_FOR_FAILURE_DATA_INTEGRITY_ONLY`. One local-raw checker invocation exited0 and matched53 raw/8 engineering/26 V5/536 protected/7 R2 files and current card/auth/release;0 stepACK/null measurements and empty/uninserted outputs are retained. [Read-only final scientific review](../../artifacts/candidate_a_native_smoke_execution_20261011_v1/FINAL_SCIENTIFIC_REVIEW.md): `PASS_FOR_BOUNDED_PREMOTION_STOP_AND_FAILURE_EVIDENCE_DELIVERY`, no unresolved required delivery finding. The missing first-draft preimage is a disclosed Minor document-reproducibility limitation, not a loss of raw evidence. This closes the bounded failure-audit delivery; the intended first-red smoke remains uncompleted. No further source/configuration/guard changes or native starts in this round.

Consumed canonical authorization/release originals remain local beside the immutable one-use raw reservation. Exact evidence copies are provided at non-executable snapshot paths ([receipt](../../artifacts/candidate_a_native_smoke_execution_20261011_v1/CONSUMED_AUTHORIZATION_EVIDENCE_RECEIPT.json)). They will not be staged at executable canonical paths while the consumed raw reservation remains local. The actual-raw checker is explicitly local-only; no clean-checkout raw audit is claimed, and historical absence-of-authorization offline fixtures are not rerun or promoted to post-run validation.

Data-review provenance limitation: the first draft incorrectly described the default checker as publicly complete despite its local canonical authorization/release dependency. The corrected report states that boundary. Exact V1 report/receipt/binding bytes were not saved before that documentation correction; old binding SHA`bd4ff2deeab2184acd07d4126b7b1c4332a31f1dbba008d8b4b0bd7a4dc31fa0` alone cannot restore its contents. [Explicit correction disclosure](../../data/processed/candidate_a_native_smoke_execution_20261011_v1/CONTROLLED_DOCUMENTATION_CORRECTION_RECEIPT.json) and [current V2 binding](../../data/processed/candidate_a_native_smoke_execution_20261011_v1/FINAL_DATA_BINDINGS_V2.json), SHA`5c52d56d8ccc67c0aab86a5251b4c675fc1621e748a6cd650861418231957034`, preserve the actual current review and this limitation. Raw files, actual checker output/source, engineering evidence and runtime authorization are unchanged; no claim of complete draft-version preservation is made.

Current Candidate A NOT_QUALIFIED, A1 UNRESOLVED, historical contract-bounded STOP3, actuator900 NOT_TESTED, Stage6 closeout and formal protocol unchanged. This new stop is not a reinterpretation of old STOP3. The one approved run ID is consumed and cannot be reused.

Next owner is user/Chat. Suggested next discussion: separately review the native phase-library self-loop warnings and the diagnostic warning policy before deciding whether a narrow configuration/log-handling correction and a **new** run identity should be proposed. No silent suppression, guard relaxation, new A1 proof or new run is authorized by this result.

Documentation impact: factual PROJECT_STATE/WORKLOG and README link/current interface status; this new result supplements historical implementation/reviews. DECISIONS/protocol/AGENTS/supervisor/thesis documents are unchanged.

# Candidate A — SMOKE02 single-run result

**The requested first controlled-red smoke was NOT_REACHED. One authorized native start was consumed; the unchanged 180 s wall-time guard stopped execution at simulation time687 s. There was no retry, continuation or resource-cap change.** Engineering and independent data audits preserve the original truncated run; scientific review is recorded separately.

## Authority and actual execution

User approved commit `59a9394071828ef25c86b7ae6d417e0c28b6119f` and card SHA-256 `a501e6005589de0d3ce6acd0fe7924ec84b589bec0849c4f3fcd3f51a4d552f3` for exactly one `CA_NATIVE_PHASE_R300_S17_SMOKE02`. The conditions were earlier stop on anomaly/unknown log coverage, mandatory close/pause after the first activated1206→1207 s red interval, complete evidence retention and no automatic retry. [Exact human authorization](../../artifacts/candidate_a_native_smoke02_execution_20261012_v1/USER_AUTHORIZATION_RECORD.json).

Demand M3600/R900/U360/X180 veh/h, service command300 veh/h, seed17, step1 s, activation1200 s and end1207 s are unchanged. The finite holding program and normal successors were the reviewed isolated correction; production guard, behavioral model, network and formal design were not changed. Static source/input/environment/protected-file and resource checks passed before the single launch. Python3.13.0, TraCI/SUMOLib1.26.0 and sumoITScontrol0.1.0 were bound by metadata/hashes; no separate native version/probe or installation was performed.

One child was launched: PID48105, parentPID48010. Startup connected after22.003 s with211 client attempts against that same child; these are not211 launches. CLI exit1 and native exit0 reflect different outcomes. The owned native child closed normally when the diagnostic stopped. [Exact command, process evidence and exits](../../artifacts/candidate_a_native_smoke02_execution_20261012_v1/engineering/EXECUTION_RECEIPT.json).

## Why it stopped and what was reached

Raw bridge status is `ABORTED_UNKNOWN`, with the specific error `ValueError:wall resource STOP`. The synchronous wall guard fired between steps, before687→688. Watchdog reason/error are null because that guard fired first. The final log status is `BOUND_NO_OBSERVED_NATIVE_MESSAGE`; this resource abort must not be mislabeled as unknown final log coverage or unsafe red.

687 motion intervals were completed, read back at actual time and reconciled. ACK has1374 records: initial ACK plus verified readback for each target1..687. Last completed and accounted times are687 s. [Observed phase/step receipt](../../artifacts/candidate_a_native_smoke02_execution_20261012_v1/engineering/OBSERVED_PREFIX_PHASE_RECEIPT.json).

| Segment | Observed interval starts | Completed intervals |
|---|---|---:|
| OPEN | 0–599 s | 600 |
| Initialization yellow | 600–602 s | 3 |
| Initialization holding red | 603–686 s | 84 |
| Control activation / controlled yellow / controlled red | 1200 /1203 /1206→1207 s | NOT_REACHED |

The initialization red at603 s is distinct from the intended first **activated** red at1206 s. All controlled C/appliedC/E/N and derived measurements remain `null / NOT_OBSERVED`. Raw initialized ledger zeros are preserved as initialization state. Zero completed control cycles is not a service-rate qualification.

The card still specifies wall180 s, startup60 s, output300,000,000 B and minimum free-space5,000,000,000 B. Initial/post free space was5,559,439,360 /5,540,503,552 B; these are two samples, not a continuously measured minimum. Startup timing is measured, but this run recorded no per-stage wall-time profile. It cannot uniquely attribute the remaining time to getter calls, fsync, logging, simulation or another hotspot. [Engineering postreview](../../artifacts/candidate_a_native_smoke02_execution_20261012_v1/engineering/ENGINEERING_POSTREVIEW.md).

## Warning correction and monitor evidence

stderr and error-log are empty through final owned-process EOF. All four log streams and1376 capture records were independently reconciled to offsets, fragment/prefix hashes and stable file identities. The original17 phase self-loop warnings did not recur in this observed startup/prefix. This is a bounded native observation supporting the configuration correction, not a guarantee of future warning-free operation.

The existing checks did not report a monitored anomaly in these687 reconciled intervals. Native summary collision/teleport counters are observed zero in the recorded prefix; crossing records are empty. These available observations are distinct from unobserved controlled service and do not prove prospective joint safety, universal event coverage, all-speed yellow adequacy or safety at1206 s. Post-step checks inspect an already completed step.

## Data integrity and truncation

58 raw files,15,571,432 B, are frozen locally at `data/raw/candidate_a_native_smoke_selfloop_fix_20261011_v1/CA_NATIVE_PHASE_R300_S17_SMOKE02/outputs`. [Immutable manifest](../../artifacts/candidate_a_native_smoke02_execution_20261012_v1/engineering/RAW_FINAL_SHA256.json), SHA-256 `7ee3af11ab1070d6c98bc2648de73e84358e1cc982ca101b778dcfba7a012dec`.

All18 XML outputs parse and close for this truncated prefix. FCD/summary contain687 samples labeled0..686; actual step ACK/readback reaches687, so left-end sample labels must not be confused with completed time. Each of11 detectors ends with a partial660..687 interval of27 s. Tripinfo has814 records:708 arrived,105 censored in-network at termination, and1 undeparted. Censored costs stop at687 s; undeparted serialization zeros are not travel observations. Normal XML closure/native exit does not make this a completed1207 s run or formal cost comparison.

[Independent data review](../../data/processed/candidate_a_native_smoke02_execution_20261012_v1/FINAL_DATA_REVIEW_V1.md) ran one actual `--local-raw` checker, exit0, and verified all raw/engineering/source/input/consumed authority bindings. The default public mode uses summaries and non-executable consumed snapshots and skips full raw; it was not separately run in a clean checkout. Full raw is local-only, while receipts/manifests/results are available for review. [Independent result](../../data/processed/candidate_a_native_smoke02_execution_20261012_v1/INDEPENDENT_RESULT_V1.json).

536 protected files,7 R2 files,26 V5 files,29 reviewed SMOKE02 bindings, both original cards and all53 SMOKE01 raw files remain unchanged. Consumed canonical authorization/release originals and the one-use raw reservation stay local; [non-executable evidence copies and provenance](../../artifacts/candidate_a_native_smoke02_execution_20261012_v1/engineering/CONSUMED_AUTHORIZATION_EVIDENCE_RECEIPT.json) do not constitute a new runnable approval.

## Interpretation and current handoff

**Confirmed:** one start, complete687-step prefix accounting, initialization phase observation, absent old warnings in that prefix, explicit wall-resource stop, preserved raw and unobserved controlled measurements. **Not established:** the first controlled-red smoke, native safety/service qualification, future warning/logging behavior or the exact runtime bottleneck.

User subsequently instructed autonomous technical diagnosis and repair. That is a separate implementation scope: preserve this run, investigate overhead and prepare the minimum versioned fix with offline equivalence checks. It is not a retroactive repair of SMOKE02, approval to change its cap or permission to retry it. Any new native identity needs new explicit execution authorization after review.

Stage6 closeout, historical bounded STOP3, Candidate A NOT_QUALIFIED, A1 UNRESOLVED, actuator900 NOT_TESTED and empty/unfrozen formal protocol remain unchanged. No decision, research-design or upstream PR change follows from this resource-stop result. Documentation updates are factual PROJECT_STATE/WORKLOG/README and this separate result report; DECISIONS, protocol, AGENTS, supervisor and thesis files are unchanged.

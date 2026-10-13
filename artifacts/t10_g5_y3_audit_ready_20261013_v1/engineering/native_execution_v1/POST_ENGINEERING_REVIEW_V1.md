# Actual engineering post review — UA_T10_G5Y3_FIXED750_S17_02

**RESOURCE STOP before control activation; actual controlled response NOT_OBSERVED.** Exactly one authorized native start, CLI exit1, no retry or code/reader repair. Evidence is frozen for independent data→science review; this is not a technical-run completion, safety, service or qualification PASS.

## Exact execution and outcome

Ran the approved c82333d/current packages_v4/card18774ee7…/87-source4deb99f4… with .venv CLI --execute/--release6bbed02a…. Tool session65557, CLI PID38733, SUMO PID38762 (owned parent38733, port61813). One child only. Startup connected at24.580044583s after235 connection polls to the same child; these are connection attempts, not new native starts. Monitored startup+loop+cleanup137.066217083s is below300s. No runtime implementation/parameter/environment change.

Last verified ACK and accounting1038s, before1200s activation;1270 endpoint was not reached. Existing output limit and sampled watchdog triggered OUTPUT_BYTES. Status STOP_UNKNOWN_LOG_FINALIZATION; error retains output bytes STOP, watchdog OUTPUT_BYTES and normal process EOF not established. First controlled yellow/red/checkpoint did not occur, controlled cycles empty. C/C_mapped_pending/C_applied/E/N and derived differences all null, not measured zero; no planned cycle rows or N14 are synthesized.

## Byte accounting and immutable evidence

Frozen parent130files total300852929B, of which outputs subtree300851878B; reservation files outside outputs add1051B. Both final totals exceed300000000B (parent excess852929B; outputs excess851878B). The main-loop/watchdog trigger counts outputs subtree, whereas the total envelope also considers the run parent. Exact sampled byte total at triggering instant was not persisted: report it as unknown, not equal to final frozen size. Final size includes cleanup output, failure snapshot and receipt metadata. Their presence must not be subtracted to claim that actual output remained below the cap.

Major files:

| Frozen file | Bytes |
|---|---:|
| identity_journal.jsonl |186529915|
| pre_steps.jsonl |79626464|
| post_steps.jsonl |22953192|
| log_intervals.jsonl |4640918|
| fcd.xml.gz |2321924|

This measured size distribution supports that evidence logging consumed the output envelope; it does not show a physical G5/Y3 or service failure because that phase was not reached. No compression/deletion/limit change is performed.

RAW_FINAL_SHA256_V1.json is stored outside raw, contains all parent files including reservations/snapshots/native outputs/failure/receipt, SHA9f0a55efb1c0279782635f5556c9fe4101b50fb9a85328e779405b26b00a38dd. File sizes/mtimes were stable before and after hashing. Existing raw and all87 source/card files remain unchanged by engineering post work.

## Process and logging limits

Owned process check `ps -p38733,38762 -o pid,ppid,etime,command` returned header only/exit1: neither owned process remains. The initial non-escalated process-list permission denial is recorded; authorized readonly escalation confirmed owned PIDs and later exit. No unrelated process was operated on.

Normal SUMO/TraCI EOF was not established after the resource stop; bridge final_logs is null. This is distinct from confirming OS process exit and freezing final bytes. Native exit code was not persisted because normal finalize rejected; it remains unknown and is not reconstructed as0 or a signal code. The CLI exit code1 is actually observed. Raw streams include shutdown output; no normal, complete scientific logfile qualification is claimed.

Client/tool stderr contains the existing TraCI UserWarning “API change now handles step as floating point seconds” at protected frame_cache.py61. CLI_TOOL_OUTPUT_V1.txt preserves the observed message separately from four native streams; nothing is suppressed or relabelled as a traffic safety event. Complete native monitoring/normal arrivals/EOF and actual control cannot be certified from this interrupted prefix.

## Handoff

Current authorization is consumed. No further native/start/identity/retry, source/reader change, raw edit or safety/budget relaxation is authorized. Independent data should use the frozen130-file manifest, receipt, original run logs and exact current reader at most once; if UNKNOWN is returned, retain it and inspect only necessary prefix/file volume. Science then limits conclusion to truthful resource-stop evidence delivery. No resource settlement is performed by engineering before those gates. Parent owns project-state/worklog and user report.

# Independent data postreview — UA_CUMULATIVE750_S17_01

Disposition: **GO_FOR_OBSERVED_PREFIX_EVIDENCE_DELIVERY_ONLY**. The authorized run **STOPPED**, not completed or qualified. The one bound actual-reader invocation returned **exit 1 / STOP_OBSERVED_ALARM**; the complete result is retained in ACTUAL_RESULTS_V1.json. No parser exception, rerun, source patch, guard change, or SUMO start occurred during this review.

## Context and authority

Mandatory preflight read AGENTS.md, current PROJECT_STATE.md, DECISIONS.md, 0-byte EXPERIMENT_PROTOCOL.md and relevant WORKLOG.md. This is a bounded technical diagnostic; Stage 6 status and D018/D019 remain unchanged. Formal protocol is unfrozen. Approved commit: 3e95c545fd63765d1c15489c943bd80a78f6fdd5. Exact card c4464cd13b64a2eed0e9ea6143b16cac308562608426d6adc3023fa6b4b3fc3b; 111-source digest b351723aac24e5938ebd608be8b567a1d5d6e3527d22fc564049b4d8b306067b.

## Actual measurement

Frozen manifest cf38cadb8d17991c43ebcc40db784afc5227a9ff0f07e02bf33b3a9d6fbc15fe covers 161 files / 426650300 bytes. One independent reader checked manifest/source/environment, FCD-to-storage/internal entries, continuous TLS and paired ACKs, per-cycle request/nominal/actual accounting, vehicle identity/dynamics pools, body clearance, yellow scopes, normal terminal arrivals and final log EOF. The extraction then checked only the final R15 frame/screen and the engineering binder; it did not repeat full raw auditing. Exact commands and reader hash are in ACTUAL_AUDIT_COMMAND_RECEIPT_V1.json.

The first 1200–1248 s block comprises five complete packets T10/T10/T8/T10/T10: C=E=N=10 vehicles, all green entries. This supports one conditional finite demonstration of mixed-packet tracking, not long-run or full-demand qualification. From 1200–1272 s, seven packets completed, with an eighth T8 packet partial: C=15, C_applied=15, E=14 complete-packet quota, independent N=15. Differences C−E=1, E−N=−1 and C−N=0 are a prefix alignment, not two completed 48-second blocks. The partial packet has four observed green seconds and one entry; its yellow/red counts are **unobserved/null**, rather than measured zero. E contribution zero denotes complete-packet accounting support, not an observed zero service rate. All observations after 1272 remain null; planned1296 was not reached.

The successful T8 at1220–1228 has GGGGyyrr and N2. The stopped T8 beginning1268 has only GGGG and N1. Final native TLS BEGIN1271 is I12_PACKET8 / phase0 / G; paired post ACK1272 still phase0/G. The attempted first-Y preparation at1272 was rejected **before any yellow motion in that last packet**. It is not an observed yellow violation.

## Independently confirmed stopping condition

Fresh scope1272 identifies R_flow.15 on ramp_storage_0, front position204.32186848969542 m, v4.98795857460537 m/s, length5 m, normal decel4.5 m/s² and action step1 s. FCD BEGIN1271 (movement ending ACK1272) agrees to precision8: position204.32186849 / speed4.98795857. Distance to meter204.49 m is0.1681315103045904 m. The unchanged screen computes v·dt+v²/(2b)=7.752373101491952 m and dt+v/(2b)+length/v=2.556631718317924 s > proposed Y2. One-step stop also fails v≤4.5. Both local stop/clear predicates therefore fail with finite, bound inputs, causing UNKNOWN_LOCAL_YELLOW_SCOPE. This is a prospective contract refusal; actual future native yellow behavior/private branch, physical danger and universally insufficient T8 remain unproved. Any T9/Y3 alternative is only an engineering proposal requiring separate design and approval.

## Coverage and limitations

Independent accounting and continuous-phase checks PASS for the observed prefix; no missing/unknown observational records or post-motion alarms are reported. Fifteen independent entries, all green, have uncensored body clearance. All1339 normal terminal arrivals PASS the precision8 final-movement check. Observed minimum speed difference and native acceleration are−4.5 m/s²; maximum native event counter is0. Four native streams are bound at normal owned-child EOF(returncode0); client warnings are separately scoped. Runtime status remains ABORTED_UNKNOWN despite observational integrity checks. Terminal AFTER loaded/pending pools lack an independent next PRE and retain SINGLE_JOURNAL_NOT_INDEPENDENT_POOL_CHECK; other joins do not establish universal observation or safety.

Monitored startup/loop/cleanup173.9491367500159 s; whole CLI duration is unmeasured. Budget is not settled here. Strict NUM remains unchanged. Fixed750 only: no new closed-loop feedback, full300–900 support, native safety, service qualification, formal efficacy, or long-run original-ALINEA tracking is established. Prior versions and failures are preserved and are not combined into a same-version effect.

## Delivery and handoff

OBSERVED_CYCLES_V1.csv distinguishes actual phase exposure and unobserved counts. PREFIX_AND_SCREEN_READBACK_V1.json and extract_prefix_V1.py provide the bounded reproducible extraction. Existing ACTUAL_RESULTS_V1.json and original raw remain untouched. Parent owns PROJECT_STATE/WORKLOG updates; no governance files were edited. Next step is read-only scientific review and user decision on the retained STOP and any separate proposal. This report grants no restart or execution authorization.

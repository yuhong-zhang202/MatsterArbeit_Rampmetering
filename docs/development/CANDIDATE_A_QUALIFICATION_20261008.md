# Candidate A minimal implementation and qualification — Issue #4

Date: 2026-10-08. Delivery status: **部分完成，待用户/Chat审查**. Engineering result: **NOT_QUALIFIED_PROSPECTIVE_RED_GUARD_STOP**. Current-contract **Issue STOP3 / STOP_EXPANSION**; no further runs. This report delivers implementation and a scientifically reviewed negative qualification attempt, not formal traffic results.

## Authority and stack

[Issue #4](https://github.com/yuhong-zhang202/MatsterArbeit_Rampmetering/issues/4): 实现与资格验证 Candidate A：完整短周期 / 离散周期 ALINEA 执行器. Source snapshot: [Issue](../../artifacts/candidate_a_qualification_20261008_v1/ISSUE_4_SNAPSHOT.json), [authorization](../../artifacts/candidate_a_qualification_20261008_v1/AUTHORIZATION.md). Branch codex/issue-4-candidate-a-qualification starts at PR #3 exact head **35651751a2e03d1906ff32a267a95077553c4404**. Draft base **codex/issue-2-actuator-investigation**; depends on PR #3, which depends on PR #1. PR #1/#3 unchanged; user decides merge and order. Delivery node: pre-formal engineering qualification/STOP evidence. No separate WBS ID specified.

Stage6 stays completed/preliminary_ready; D-018/D-019 unchanged. Formal protocol empty/unfrozen. This task does not establish formal readiness, thesis effects, a sweet spot or a B/fallback decision.

## Implementation, prospective choices and gates

Separate actor/guard, runner/worker, contract, 35 preserved preparation cards (five rates × A01–A07), one-use scientific release/reservation/guardian ledger, crossing/cycle/phase/API/state logs and fail-closed snapshots. No protected old implementation modified. [Contract](../../config/candidate_a_qualification_20261008_v1/PHASE_RATE_CONTRACT.json) fixes **3G→3y→r(T−6)** with minimum red2s; adjacent integer periods8–24s, nominal packet2 **unqualified**. Timing is an initial engineering choice/reference, not a literature-certified safety minimum. Native red self-loop prevents unsolicited restart. Rate changes apply at next planned cycle boundary, never feedback-reset green; pending/applied latency separately logged.

C integrates requested command, applied C separately; E adds2 at each planned cycle end including a denied green; N is unique actual internal-entry IDs, all G/y/r counted. Fixed-window nominal quantization bound ≤4.5 vehicle-equivalents does not certify real service; variable-command bound is rate-weighted with latency separately accounted. Nominal two-car service and 900 capacity are not assumed true.

Phase B prospective common supply fixture uses unchanged M3600/R900/S17 input: OPEN before600s, native yellow[600,603), external red hold[603,1200), candidate activation1200. Prefix C/E=0, all prefix actual crossings separate. Six300s service windows[1200,3000); storage supply every step required; original10% tracking screen unchanged. No post-result hold extension/seed/demand change. This prequeued technical fixture cannot estimate traffic effects; Phase C would use natural600s activation without preload, only after all required B rates qualify. Its condition was not met.

All approaching storage/ingress checked; route-aware receiver/secure gap before green, every remaining positive-speed vehicle normal-braking witness before prospective red, exact-zero native-compliance exemption only. Missing/unsafe state stops before motion. No tau/step/speed/lane/receiver/native-safety changes.

## Actual execution and technical repairs

| Attempt | Actual SUMO starts | Accounted seconds | Result / replacement |
|---|---:|---:|---|
| CA_FIXED_R300_S17_A04 | 1 | 0 | Startup callback incorrectly passed Path; preserved. Repaired callback/test, replaced by A05. |
| CA_FIXED_R300_S17_A05 | 1 | 0 | TraCI connected but native schema loading failed; child SUMO_HOME transfer omitted. Preserved. Restore installed schema environment matching protected worker; no install/global env change; replaced by A07. |
| CA_FIXED_R300_S17_A07 | 1 | 1206 | Native runtime progressed; before first candidate y→r, guard rejected remaining creeping R_flow.1; no refused red motion step executed. STOP. |

Total **3 actual starts / 0 complete4200s runs / 0 effective qualified runs / 0 qualified rates**. A01/A02/A03/A06 are preparations, not starts. One A05 release-payload field rejection occurred before worker/reservation/SUMO and adds **0 starts**; corrected release and reconstructed rejected payload are transparently labeled. All failures and replacements retained in [execution ledger](../../artifacts/candidate_a_qualification_20261008_v1/engineering/EXECUTION_LEDGER.jsonl).

A07 guardian32.412148542s,10,797,838bytes,exit1, no guardian resource limit trigger. No unnecessary simulation/test rerun for packaging.

## Actual data and STOP rationale

Independent raw audit reconciles **45 manifest files,1206 FCD/TLS steps,21,170 pre-state observations,7 phase API requests,42 final guard IDs(27storage+15ingress)**. The first candidate cycle[1200,1224) only executes3G+3y. One actual crossing R_flow.0 in(1200,1201], green. C=applied C=.5,E=0,N=1; C−E=.5,E−N=−1 are **partial boundary accounts**, not complete-cycle overservice or physical service shortfall. Actual complete-cycle n unknown; cannot reinterpret n as1.

R_flow.1 fullprecision speed0.04573822948686786m/s, stopline distance1.001999189766508m; current guard `1.1+v*1+v²/(2*4.5)` requires1.1459706723353782m, margin−0.14397148256887027m. FCD rounding does not remove rejection. Root, engineer, analyst and scientist agree the recorded guard was correctly implemented and refused before motion. Engineering found no identity/geometry/event-order/formula bug preserving the contract. Science classifies current-contract STOP3, with scope limited to bounded diagnosis; no exhaustive alternative-design impossibility claim.

Official native SUMO1.26 sources use default1.0m stopline gap and native yellow/red braking rules differing from custom guard. Source-based interpretation: native near-stopline creeping can violate this conservative witness. **Not proved:** actual red necessarily unsafe, 900 physically impossible, all alternative designs invalid. Lowering margin/reaction, reinstating low-positive-speed exemption, changing packet or timing would change the reviewed contract; not authorized as a bugfix.

No observed prefix collision/teleport/emergency.17 native self-loop initialization warnings retained. This absence is not a new transition safety PASS. Endpoint:4050planned=1467inserted+73due source+2510future; inserted=1267arrived+200in-network. All unfinished/future/source waiting retained; no effect/cost claim.

## Five fixed rates

| Command veh/h | Nominal E | Actual N | Relative tracking error | Complete-cycle discharge | Safety / qualification |
|---:|---|---|---|---|---|
| 300 | 0, unfinished6s candidate prefix; nominal packet2 unqualified | 1G, same6s prefix | null; six full300s windows NOT_TESTED_INCOMPLETE | Unknown; no completed cycle | Guard STOP before red; NOT_QUALIFIED |
| 450 | Unobserved; proposed packet2 | Unobserved | null / not tested | Unknown | Unrun/HOLD |
| 600 | Unobserved; proposed packet2 | Unobserved | null / not tested | Unknown | Unrun/HOLD |
| 750 | Unobserved; proposed packet2 | Unobserved | null / not tested | Unknown | Unrun/HOLD |
| 900 | Unobserved; proposed packet2 | Unobserved | null / not tested | Unknown | Unrun/HOLD |

Highest **verified** safe rate: unknown/null; not0 and not300. No supplied full window completed; cannot report failure percentages or expand runs to bypass STOP. Phase C two T1 runs not launched.

## Issue acceptance, exact conditions

| # | Issue acceptance question | Self-check | Answer / limitation |
|---|---|---|---|
| 1 | Candidate A 是否已经实现为独立、可审计的 phase actor？ | 满足 | Independent source/contract/ledgers implemented; actual qualification remains separate. |
| 2 | r_cmd → E → N 的 mapping/accounting 是否闭合？ | 部分满足 | Observed prefix closes; whole cycle/window service not established. |
| 3 | 实际 phase sequence 是否与设计一致？ | 部分满足 | All executed steps consistent; candidate red/full cycle never executed. |
| 4 | 每个固定 command 300/450/600/750/900 的 nominal service、actual service、relative tracking error、actual per-cycle discharge、safety result 是什么？ | 部分满足 | Five-rate table explicitly reports partial300 and unrun other rates; complete values unavailable under STOP. |
| 5 | 当前场景下安全可实现的最高已验证 metering rate 是多少？ | 未验证 | Unknown/null; no rate qualified. |
| 6 | 900 veh/h 是否实际资格通过？若否，最小限制是什么？ | 未验证 | Not tested. Current minimum progress blocker is locked guard rejection at first300 cycle; not a900-specific capacity result. |
| 7 | Candidate A 是否可以进入下一步正式设计讨论？ | 满足 | Can discuss explicit engineering limitation; cannot claim execution readiness. |
| 8 | 是否需要触发 Candidate B 或 fallback？只能建议，不能自行改变研究范围。 | 满足 | Necessity not established; no trigger/execution. Proposed safety-contract reassessment first; user decides. |

These labels distinguish implementation/answer delivery from unavailable qualification. STOP evidence delivery does not mean all rate capabilities passed or user accepted Issue.

## Verification, versions and reproducibility

Required sequence completed **simulation_engineer → data_analyst → scientific_reviewer**. Engineer implementation,26offline tests/syntax and bounded execution/native diagnosis; analyst independent raw/time/identity/CEN/endpoint/hash audit; scientist direct selective raw/recompute/official-source verification and STOP interpretation. Findings addressed; final delivery findings0/0/0, one advancement blocker. [Final science](../../artifacts/candidate_a_qualification_20261008_v1/FINAL_SCIENTIFIC_REVIEW.md), [engineering](../../artifacts/candidate_a_qualification_20261008_v1/engineering/R300_A07_RUNTIME_ENGINEERING_REPORT.md), [data](../../data/processed/candidate_a_qualification_20261008_v1/R300_A07_ACTUAL_DATA_REVIEW.md).

Actual environment: Python3.13.0 projectvenv; SUMO/TraCI/sumolib1.26.0; sumoITScontrol0.1.0;1s step. SUMO binarySHA256 `3bd1eaa3b167fb527ac33b154dfb57b41b9a40d5bc3e26246489824dd7977179`; networkSHA256 `887c232483f0c68dc024334ff5997250d7d36299ab2744bdcf49d5a314c700ca`. All67protected files unchanged. Native XML validation always; optional offline XSD validation unavailable(lxml missing), not passed/disabled. Existing installed schemas restored in childenv only.

Tests before commit on source snapshot rooted in3565175; [26-test receipt](../../artifacts/candidate_a_qualification_20261008_v1/engineering/R300_A07_REPAIR_OFFLINE_RECEIPT.json) records all six exact file SHA256s. Test command `.venv/bin/python -m unittest discover -s tests/candidate_a_qualification_20261008 -v`; syntax command inreceipt. No tests claimed against an untested new commit; publication readback must compare committed sixbytes toreceipt. Actual command A07: `.venv/bin/python scripts/candidate_a_qualification_20261008_v1/runner.py --launch config/candidate_a_qualification_20261008_v1/CA_FIXED_R300_S17_A07/card.json --release artifacts/candidate_a_qualification_20261008_v1/RELEASE_FIXED_R300_A07.json`. This documents history, **not permission to reuse consumed card**.

Raw source/snapshot/receipt hashes are authoritative perattempt. Historical reviewed source revisions remain separately preserved; not pooled into A07 behavior. [Final data bindings V2](../../data/processed/candidate_a_qualification_20261008_v1/R300_A07_FINAL_DERIVED_BINDINGS_V2.json) bind18final files; science45raw+18bound hashes no drift. Preliminary pending reviews remain historical; final review supersedes their operational status. Manual prose43 counts were reconciled to raw45files/42witnesses, with no raw/source/table alteration.

## Public evidence and handoff

Fullraw remains immutable locally at `/Users/yuhongzhang/Desktop/Masterarbeit-Ramp-Metering/data/raw/candidate_a_qualification_20261008_v1/`; not remotely accessible. PR supplies byte-identical curated receipts/failure snapshots/API/startup traces/source snapshots, original manifest hashes, eight independent small CSV tables and detailed reviews. Public selection/copy identity manifest: `artifacts/candidate_a_qualification_20261008_v1/pr_review/PUBLIC_EVIDENCE_MANIFEST.json`. BulkFCD/detector/fullstate not published; fulldata reproduction requires owner access to listedlocalraw. Absolute-path cards require installation/path adaptation with new reviewed identities; no out-of-box portability claim. No private Robert email or unrelated MemoryCore work uploaded.

Updated STATE/WORKLOG/README for engineering STOP and implementation entrypoint; unchanged decisions/protocol/Stage6 scientific reports remain authoritative. No unsynchronized research decision is created. Next handler **用户/Chat**: review negative evidence and decide whether separately authorize sourced safety-contract reassessment. Rejected transition qualification, fullcycle n and300–900 capability remain open; Candidate B/fallback not automatically needed or released. **下一步建议不构成执行授权。**

# Unified ALINEA actuator — bounded validation and handoff

2026-10-13. **Completed bounded technical task / awaiting user and Chat review. Candidate A remains NOT_QUALIFIED.** This records the approved technical task, not acceptance of Candidate A or permission for formal experiments.

本轮结论：四类技术任务均有可审查数据，真实ALINEA反馈和周期边界应用已验证，可以结束本次有界技术工作。750档仍为计划14辆、实际13辆；最终源码没有重新原生测试固定300/900，真实反馈也没有使映射档位变化。因此执行器仍未合格，不启动正式实验。原始失败、旧STOP3和全部版本证据保留，下一方为用户/Chat。

## 1. Scope and authority

The [approved scope](UNIFIED_ALINEA_ACTUATOR_SCOPE_20261013.md) contains four sequential technical tasks: fixed300, fixed750 mapped720, scheduled command changes, and real ALINEA feedback. Demand remains M3600/R900/U360/X180 veh/h, seed17, dt1 s. A service request of300 or750 does not change ramp demand. Activation is global1200 s; endpoints are1272/1270/1266/1272 respectively. The total ceiling is1200 monitored seconds and1,200,000,000 raw bytes; single-run ceilings300 s/300 MB, startup60 s and minimum free space5 GB. These are technical observation limits, not thesis horizons.

The baseline is PR13 head `9eb95e29ccc85423084bc6945668cd36c3298b06`. Work is isolated on `codex/unified-alinea-actuator`; upstream PR13 and earlier stacked PRs are unchanged. No formal protocol, demand/seed/model, thesis structure or research decision was changed. The original qualification launcher, old prospective-red guard/STOP3 evidence and536 protected dependency files are preserved. Canonical execution permissions are local, single-use and excluded from Git delivery.

The user subsequently [explicitly approved a restricted numerical exception](../../artifacts/unified_alinea_actuator_20261013_v1/USER_NUMERICAL_EXCEPTION_APPROVAL_V1.json). It applies only to fully bound events matching the pinned SUMO1mm source expression, within these diagnostics. It does not globally raise a braking threshold. Actual values, original strict FAIL and all other safety/UNKNOWN stops remain. The private native branch and stop offset were not directly observed, so expression compatibility is not a unique causal or general safety proof. Current following emergency9+1.1m, fresh receiving-space admission, actual-yellow screening, crossed-body tracking, collision/teleport/red-entry, identity/log/coverage and other braking stops remain. A failed or unknown applicable check still stops.

## 2. Implementation and source versions

The existing short two-car packet implementation is reused through new namespaces. The library covers integer periods8–24 s, maximum green4 s, yellow min(5,T−6) s, minimum red2 s, and nominal two-car quota. Requested rate maps to nearest7200/T veh/h, with ties selecting lower release. A new valid command during a cycle remains pending until a complete cycle boundary; same-value requests retain separate IDs. Actual application requires matching signal/program/link/time and first-green ACK. C requested, mapped-pending and applied integrals are separate; E counts nominal quota of completed cycles, while N counts every actual entry without capping or forcing equality.

Two technical changes occurred and remain versioned:

1. Early post-signal binding was added before recording application. Four wrong state/phase/program/link negative controls reproduced false application timestamps on V1 and now stop with no application timestamp. The original failure and source preimage remain. [Engineering V2](../../artifacts/unified_alinea_actuator_20261013_v1/engineering/signal_ack_fix_v2/ENGINEERING_REVIEW_V2.md).
2. After the original750 strict stop, the user-approved numerical-event classifier was added. Identity, first-yellow phase, fresh before/after state, model/dynamics, position, following/receiver state and source expression must jointly match; other alarms remain active. [Engineering numerical review](../../artifacts/unified_alinea_actuator_20261013_v1/engineering/numerical_exception_v1/ENGINEERING_PRELAUNCH_REVIEW_V1.md).

Fixed300/02 and original750/01 ran the61-record runtime digest `a2b25659131bae5d9628ff5ab2f35e0c89987705daa5ef84a67ce426967b4b2b`. Numerical750/02, Dynamic/01 and the final ALINEA card bind the64-record digest `ea180197848843bd3cca7d326a7016454fe8bd0db406302a64ad11f03347b29b`, implementation checkpoint `1749e040ac8b738e8530dd690236d6ef4da800fd`; evidence checkpoint `ff309c8` retains the same runtime bytes. Consequently,300 is not a native test of the final64-record version. Historical900 compatibility replay is also not a new native900 run of that version.

## 3. Actual runs and limitations

| Run identity | Runtime | Actual endpoint | Completed cycles / E / N | Bounded finding |
|---|---|---:|---|---|
| UA_FIXED300_S17_02 |61-record V2|1272|3 /6 /6|Three complete24s cycles; short actual discharge agrees with nominal300.|
| UA_FIXED750_S17_01 |61-record V2|1265 STOP|6 plus partial /12 /13|Original strict braking FAIL preserved. The additional entry belongs to the partial cycle; it does not establish over-service.|
| UA_FIXED750_S17_02 |64-record numerical version|1270|7 /14 /13|Bounded monitored execution completed with one approved numerical event; service target NOT_MET.|
| UA_DYNAMIC_S17_01 |64-record numerical version|1266|4 /8 /8|Actual boundary applications and delayed commands verified; scripted input, not ALINEA feedback.|
| UA_ALINEA_S17_01 |64-record numerical version|1272|9 /18 /18|Actual real-feedback chain reconstructed; bounded technical postreviews complete; mapped period stayed8s.|

The original750 stop records R_flow.13 speed4.69222772465427→0.19122772465426985 m/s, native acceleration and speed difference−4.501 m/s² at1264→1265, exceeding the old−4.500001 rule. The event was finite and bound, not a missing-data condition. The same measured numerical event in750/02 is retained with its legacy FAIL reasons and the approved conditional classification. Pinned official SUMO1.26 source commit `fa7df22d7f1c4ae245192ecc32410a49f1ffb2a3` gives a compatible Euler1mm expression, but the selected internal branch is not uniquely identified. [Source replay](../../artifacts/unified_alinea_actuator_20261013_v1/engineering/technical_recovery_v1/SOURCE_EXPRESSION_REPLAY_V1.json).

750/02 has six cycles with two actual cars and a final cycle with one; green ended at its4s deadline. Actual rate is13×3600/70=668.57 veh/h over this70s observation, below mapped720 by7.14% and requested750 by10.86%. Mapping itself contributes−4%; mapping error and execution shortfall must not be merged. No retiming, seed selection or model change was made to remove this deficit. [Independent750 data postreview](../../data/processed/unified_alinea_actuator_20261013_v1/UA_FIXED750_S17_02/revision01/DATA_POSTREVIEW_V1.md).

Dynamic requests at1200/1201/1226/1237 s were applied at1200/1224/1234/1242 s and confirmed by G ACK one second later. Delays are0/23/8/5 s. Only those four cycle boundaries contain program/green-start calls; no midcycle restart. Complete periods are24/10/8/24 s. Independent integrals are C=251/24, mapped-pending=41/4, applied=E=N=8. Pending minus applied2.25 is a vehicle-equivalent integral difference, not delay seconds. [Independent Dynamic data postreview](../../data/processed/unified_alinea_actuator_20261013_v1/UA_DYNAMIC_S17_01/revision01/DATA_POSTREVIEW_V1.md).

## 4. Genuine ALINEA chain

Frozen actual data reconstructs two genuine feedback decisions using downstream point E1 IDs `p1_main_down_20_l0/l1`, complete global30s windows[1200,1230)/[1230,1260) and ongoing event handling. Both detectors were observed empty at activation; this is measured zero, not missing observation.72 consecutive subsequent E1 observations are present. The instance is the unchanged project `Feedback` using the approved development references:11% target, gain70 veh/h per percentage point,30s update, bounds300–900, initial900. Its own clipped previous requested rate remains the prior state. Only its call clock shifts global1200/1230/1260→logical600/630/660. This is not direct use of the sumoITScontrol percentage-green class.

| Window / decision | Mean occupancy | Previous requested | Raw / clipped request (veh/h) | Applied BEGIN / firstG ACK | Delay | Mapped rate / period |
|---|---:|---:|---|---|---:|---|
|[1200,1230) /1230|8.47780733%|900|1076.55348678 /900|1232 /1233|2s|900 /8s|
|[1230,1260) /1260|11.25582333%|900|882.09236708 /882.09236708|1264 /1265|4s|900 /8s|

Displayed decimals are rounded; raw exact values and contributors are retained in the actual audit. Both non-initial feedback request IDs received bound actual applications. The second requested value changed but still maps to900, so this run **does not validate a physical period change in response to feedback**. Scheduled Dynamic separately validates physical period changes; it cannot substitute genuine feedback evidence. No tuning, fake input or extra horizon was used.

Nine complete8s cycles give E=N18, all18 entries during green, all entrant tails observed clear, no partial final cycle or body censor. Crequested=17.940307890282597, mapped-pending=applied18. Pending minus applied0 is an integral difference; it does not mean actual delays2/4s were zero. Initial program/phase-zero calls occur only at1200, not midcycle. Actual monitoring has no unexempted alarm/coverageUNKNOWN, numerical exceptions0 and minimum acceleration−4.5m/s². The normal-arrival and full EOF checks are in the independent actual audit. Independent data and final scientific postreviews are complete; the known actual costs are settled. The final12s E1 interval[1260,1272) is a partial measurement window, retained separately from the nine complete actuator cycles. Independent E1/FCD joins cover98 tuple observations including17 ongoing observations, not98 unique vehicles. All1338 normal arrivals pass the precision8/last-movement audit. [Actual ALINEA data postreview](../../data/processed/unified_alinea_actuator_20261013_v1/UA_ALINEA_S17_01/revision01/DATA_POSTREVIEW_V1.md).

## 5. Verification and public/local evidence boundary

The [initial engineering review](../../artifacts/unified_alinea_actuator_20261013_v1/engineering/ENGINEERING_REVIEW_V1.md) records five final offline methods covering all17 phase configurations, mapping/ties/invalid values, boundary/latest-command behavior, three integrals, partial/null/excess N, real project Feedback/E1 fixtures, hard-gap/yellow-UNKNOWN stops and resource gates. Synthetic fixture movements do not establish traffic safety. Affected signal tests were rerun after V2; unaffected suites were reused by source scope. The numerical repair has three targeted methods plus independent decoder negatives, including mismatch and other-alarm stop behavior. Original fixture/source/test failures remain.

[Clean checkout V4](../../artifacts/unified_alinea_actuator_20261013_v1/clean_checkout_v4/RECEIPT_V2.json) tested commit1749e040: three targeted numerical methods PASS, all64 runtime hashes match, only data/raw/.gitkeep present, clean Git status. Earlier V1/V2/V3 clean receipts retain their exact commit and test scope; no claim that every suite was rerun on the final evidence commit. A receipt metadata error occurred after the successful tests and was preserved; corrected V2 reuses that successful log without a test rerun.

Environment is bound in each card: project Python3.13.0, TraCI/sumolib1.26.0, sumoITScontrol0.1.0 and the existing SUMO1.26.0 binary with SHA. Source/binary compiler equivalence is NOT_VERIFIED. No installation or new environment was performed. Execution used the existing `.venv` interpreter and exact card/release; each engineering execution receipt preserves the actual command and process identity.

Full raw FCD/TLS/ACK/crossings/body/arrival/native logs remain read-only under `data/raw/unified_alinea_actuator_20261013_v1/<run>/outputs/`; every full raw parent inventory and SHA is in the corresponding engineering/runs manifest. Raw files are ignored and not uploaded. Full actual audits and historical900 replay require these local raw files. Committed summaries, hash manifests and public offline fixtures permit review of reported results and portable regressions; they do not remotely reconstruct the full raw audit. No GitHub upload or new PR is claimed.

The [five-identity independent data summary](../../data/processed/unified_alinea_actuator_20261013_v1/final_summary_v1/DATA_NODE_SUMMARY_V1.md) and its25-file binding preserve the61/64-source boundary, original FAIL, service NOT_MET and final ALINEA observation. It is a direct consolidation of existing audits, with no repeat raw scan.

## 6. Final disposition, resources and handoff

The four planned technical tasks now have actual data; five native identities include the preserved original750 FAIL and its explicitly approved repair/retry. This is **task coverage**, not a claim that every service target passed. [Final scientific review](../../artifacts/unified_alinea_actuator_20261013_v1/science/UA_ALINEA_S17_01_POSTREVIEW_V1.md) returns limited technical GO with no new Blocker/Major and supports stopping this approved node. This is not actuator qualification or user acceptance. No more simulations are proposed within this packet.

| Requirement | Evidence-based disposition | Remaining boundary |
|---|---|---|
| Integer mapping/configuration/boundary/null and stop regressions | Offline scope passed; failures/preimages retained | Synthetic traffic is not native safety/service proof. |
| Fixed300 physical short test | V2 native3 completecycles/E=N6 | Not rerun on final64-record source; no long-term qualification. |
| Fixed750 physical short test | Original strict FAIL preserved; repaired technical observation complete | **Service NOT_MET: E14/N13**, actual668.57veh/h; no retiming to erase deficit. |
| Scheduled changing commands | Four actual boundary applications and0/23/8/5s delays, four different-period slots | Only one approved schedule/seed. |
| Real ALINEA input/math/application | Two genuine feedback commands applied at1232/1264; E=N18 | Requested changes but mappedT8 stays unchanged; no efficacy result. |
| Safety/data completeness | Required observed monitors, body/arrival/EOF audits pass in completed identities; one explicit restricted numeric event in750/02 | Not universal safety; actual private numerical branch not directly observed; old STOP3 remains. |
| Overall actuator qualification/formal authorization | **NOT_QUALIFIED / not authorized** |750 deficit, source-version coverage, broader sustained service/safety and formal protocol remain unresolved. |

[Final resource settlement](../../artifacts/unified_alinea_actuator_20261013_v1/FINAL_RESOURCE_SETTLEMENT_V1.json) verifies all five actual identities after three-role review: **777.1210645419778 monitored seconds /815,616,282 raw bytes**. Remaining original envelope is422.87893545802217s /384,383,718B, with no unknown reservation; it is not authorization for further runs. Monitoring means startup+owned loop+cleanup, excluding preparation/analysis/reviewer wall time. All actual failures count. Raw and consumed run cards remain; no automatic replay.

Candidate A remains NOT_QUALIFIED, A1 UNRESOLVED, Stage6 closure unchanged and formal protocol empty/unfrozen. No formal sweet spot, freeway benefit or universal safety claim follows. The next party is **user/Chat**: decide whether a new bounded engineering task should first investigate the750 shortfall and the required final-source/native coverage before any larger qualification work. A future scientific evaluation needs a separately approved/frozen design. These are suggestions, not execution authorization; no new task/parameter change/run/PR is started.

Documentation impact: PROJECT_STATE and WORKLOG updated with actual completion/limits/resource settlement; the mutable scope's stale operational status and README updated with this handoff link. Immutable approved scope snapshot, decisions, formal protocol, supervision records, thesis outline and AGENTS stay untouched. This is factual technical reporting, not new research approval or user acceptance.

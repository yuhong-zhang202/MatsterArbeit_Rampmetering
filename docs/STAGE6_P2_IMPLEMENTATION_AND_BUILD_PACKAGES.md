# Stage 6 P2：离线实现与构建申请包

日期：2026-09-19。状态：**BUILD02 成功；工程、独立数据与科学静态编译门均通过（PASS_STATIC_COMPILED_ONLY）；SUMO 启动仍阻断。**

## 1. 授权和结论

用户指示“进行P2”后，本轮依据已审查的 P1 Candidate B 和 proposed registration，完成隔离输入、离线测量适配器、离线检查，以及一次受限 `netconvert` 构建申请包。该授权不冻结 P1 科学值，不授权 `netconvert`、SUMO、TraCI 或 GUI；构建和仿真各自仍需明确用户批准。

**结论：**离线输入与适配器范围通过专业审查。BUILD01在30秒监控阈值触发后超时且未生成网络；系统日志显示同一进程遭遇读取`kern.bootargs`的sandbox拒绝，但因果关系未知。用户随后授权排查并根据证据尝试直至成功。独立审查后的BUILD02保持五份网络输入哈希不变，4.657秒成功生成网络。工程静态审计155通过/0失败/4运行期不可评价，数据独立审计207通过/0失败/5不可评价，科学最终复审通过`PASS_STATIC_COMPILED_ONLY`，开放B/M/required Minor=0/0/0。编译网络SHA为`e47b0f94521414e55d0e5337b87204dc38d98a0a3a7c5466f2a5883f80b52710`。这仅验收当前compiled文件的静态结构与来源，`specific_obstacle`尚未解决；交通行为和候选效果未知。旧D2的`not_resolved`、停止门和正式实验设计锁保持不变。

## 2. 实现内容和修订记录

所有新输入位于 `artifacts/stage6_recovery_p2_revision_01/engineering/`，数据适配器和派生回执位于 `data/processed/stage6_obstacle_20260913_v1/recovery_p2_revision_01/data/`。

- 生成隔离网络源文件及五份 attempt 输入包：一次 R720/seed17 技术 smoke，以及 R0/R720 × seed17/23 四条验证输入。每包绑定 17 个 XML 输出角色、计划身份和输出路径；当前都标为未启动、不可 launch。
- revision02 修正配置 XML 根标签，使其符合本机 SUMO 1.26 XSD。
- revision03 只给 tripinfo 增加 `write-undeparted=true`，明确保留从未入网身份；17 个输出角色、需求、seed、路线、信号和车辆行为参数未变。未入网必须有显式负 depart 记录；缺少 tripinfo 记录不能推断未入网，未知计划时间保持 NA。
- 数据适配器 revision02 在生成采样时间网格前拒绝负出发时间、非有限值和倒序生命周期，并保留合法空采样区间与未入网 NA 分支。已修复审查发现的倒序到达缺陷；早期版本和回执保留。

## 3. 离线验证和审查

| 检查 | 结果 | 证据边界 |
|---|---:|---|
| 工程静态检查 | 178 项通过；15 份完整 XML 通过本机 XSD；5 份 additional 模板因等待编译后长度而按预期拒绝；5 个危险配置负例被拒绝 | 未编译网络，不证明 SUMO 行为 |
| 数据输入检查 | 140 项通过 | 仅绑定未编译的五套输入 |
| 数据适配器测试 | 42 项通过，包括数学、边界及 17-role 合成 XML；生命周期修复后增加 5 个回归 | 不等于真实 SUMO 输出复算 |
| BUILD01 执行门测试 | 19 项通过，包括 Python 假进程正常完成、超时终止、绑定错误拒绝和重复 claim 拒绝 | 未执行 netconvert |
| 最终科学审查 | P2 离线范围 PASS；开放 Blocker/Major/required Minor = 0/0/0 | 不评价候选运行表现或障碍是否解决 |

可追溯绑定：

- 最终构建申请卡 [SG6_BUILD_request_card_revision03.json](../artifacts/stage6_recovery_p2_revision_01/engineering/SG6_BUILD_request_card_revision03.json)，SHA-256 `33ee32943e8420a38514bd67d372204c7f019569187ed95202c8daf4961095bd`。
- 累计账目 [budget_reconciliation_revision02.json](../artifacts/stage6_recovery_p2_revision_01/engineering/budget_reconciliation_revision02.json)，SHA-256 `a3f853ea5a919fe55aeaea62a7a0558333ffbf69a5781b7d5e978cb6fc2260d4`。
- 工程最终绑定 [engineering_P2_executor_delivery_manifest.json](../artifacts/stage6_recovery_p2_revision_01/engineering/engineering_P2_executor_delivery_manifest.json)，SHA-256 `74f373c5aeebb81d3d16454b3823cb485a3a5dfa668609850436097ca376c0ce`，231/231 文件绑定通过；原工程 manifest 的 63/63 绑定也复核通过。
- 数据回执 [offline_adapter_receipt_revision02.json](../data/processed/stage6_obstacle_20260913_v1/recovery_p2_revision_01/data/offline_adapter_receipt_revision02.json)，SHA-256 `de6fa2bc67664d605f6a3e7388dcd42a2b5cbc86ea000a3aaabb7e2bf287bf22`；manifest 8/8 绑定通过。
- 假进程回执 [test_receipt.json](../artifacts/stage6_recovery_p2_revision_01/engineering/fake_process_tests_revision02/test_receipt.json)，SHA-256 `868e37452051823eb6bae016315c8df257bfc7be708ced400fc0a3264a63e21d`。

审查确认修订只补齐输出/身份校验，没有改变 P1 科学设计。实际内部车道映射、编译检测器覆盖、真实 SUMO 输出兼容性和运行后独立数据复算仍未验证。

## 4. 预算和当前调用

累计账目只报告可追溯的保守下界，不把早期未逐进程登记的运行伪装成精确全项目总数：Stage 1/2/4/旧 Stage 6 指定证据范围至少 **25 次 SUMO、12 次 netconvert、1 次 TraCI**；GUI 总数未知。早期 ALINEA/scaffold 集成、部分 GUI 尝试及零散进程数明确列为未完全汇总。Stage 2/4/旧 Stage 6 具体账本、样例摘要及 WORKLOG 证据均由预算文件按哈希绑定。旧阶段未用额度不转入新预算。

BUILD01与BUILD02两次真实调用累计为：**netconvert 2、SUMO 0、TraCI 0、GUI 0。** BUILD01在30.032秒终止，return code −15，stdout/stderr均为0字节，未生成网络；系统日志记录一个与PID和启动时刻匹配的sandbox拒绝，但根因仍未知。BUILD02在4.657秒退出0，生成12,244字节网络，SHA-256 `e47b0f94521414e55d0e5337b87204dc38d98a0a3a7c5466f2a5883f80b52710`；六个attempt文件共21,096字节，独立复核哈希吻合。启动栈采样未启动：父代理首次检查时PID已不存在，无法验证检查相对t+2的精确时点；该诊断偏差已记录，不据此补栈或推断根因。BUILD01、BUILD02回执和closeout均保留，不覆盖失败证据。

SG6_BUILD 草案只请求一次 `netconvert`，零重试、零 SUMO/TraCI/GUI；监测阈值为 30 秒和输出目录 100,000,000 字节。执行器先校验批准 sidecar 对最终卡 SHA 的绑定，再检查 binary、全部输入和 schema，独占 `BUILD01` 并持久登记预算后才可启动。

BUILD01 监控语义已在首次真实调用中验证为：约 30 秒触发终止，终止滞后约 0.032 秒；该次 stdout/stderr 无增长且进程组确已停止。它没有揭示 `netconvert` 为什么在启动后无输出。原批准卡不允许重试，且额度现已耗尽；绝不重用或修改该卡/receipt。用户的新指令单独授权排查及有依据的后续构建尝试。每次新尝试必须新编号、新执行记录，保留旧 attempt；先完成失败诊断和独立复审，再执行明确的最小修正。若修正涉及科学网络输入而非执行/环境层，须按相应项目审查门处理，不能擅自更改候选设计。

## 5. 接下来的门

**编译门结果：`PASS_STATIC_COMPILED_ONLY`。**工程静态审计为155 PASS/0 FAIL/4 runtime NOT_EVALUABLE；独立数据审计为207 PASS/0 FAIL/5 NOT_EVALUABLE；科学最终复审开放Blocker/Major/required Minor=0/0/0。辅助lane可用长294.51m、下游496m、三入口request无冲突、aux0无outgoing、城市/TLS和存储几何保持，11个detector位置静态兼容。编译器生成的`acceleration="1"`与`changeRight="authority"`已绑定到网络哈希并须进入未来运行登记；它们的实际效果未验证。源文件宽度省略值与compiled显式3.20只在本机sumolib缺省规范化下相等，不是字节级等同。t+2启动栈采样时点未捕获，作为已披露诊断流程偏差接受；不补造采样或据BUILD02成功归因sandbox。仍未证明SUMO实际加载、车辆安全换道、E1/E2运行时加载、17-role数据链或specific_obstacle解决。静态验收本身不释放任何交通运行。

SUMO 启动申请仍是草案：最多 1 smoke + 4 validation + 1 个全局技术 retry 的结构建议，但 `launch_eligible=false`、批准次数为 0。编译验收后，必须填实附加文件终点、compiled hash、最终运行配置与哈希、重试展开、输出预算和执行回执，再提供独立精确启动卡并等待单独批准。

无新运行就不能判定候选是否解决 `specific_obstacle`，也不能判定匝道权衡、Breakdown、Capacity Drop、控制收益或正式实验准备就绪。正式协议仍未冻结，未联系 Robert。

## 6. 子代理路由与维护

- `simulation_engineer`：隔离网络输入、fail-closed构建器与假进程测试；BUILD01超时后找到一条同PID sandbox拒绝日志（因果仍未知），在新卡及独立审查下执行BUILD02并完成155项静态工程审计。
- `data_analyst`：测量适配器、42项测试、140项输入审计及历史调用下界核查；另独立解析BUILD02 compiled XML，207项通过、0失败、5项运行期不可评价。
- `scientific_reviewer`：构建前P2审查和BUILD02 compiled gate最终审查均通过；开放Blocker/Major/required Minor=0/0/0。审查接受静态编译范围，不推断行为或specific_obstacle解决。

维护：同步更新了 `docs/PROJECT_STATE.md`、`docs/WORKLOG.md`、本恢复方案的执行进度和 Stage 6 ledger。未改 `data/raw/`、历史运行、原始配置、`DECISIONS.md`、`EXPERIMENT_PROTOCOL.md` 或 supervisor 记录。


## Runtime validation revision03 — schema-loading repair

The first real smoke (revision02) stopped before the first simulation step: SUMO had loaded BUILD02 but rejected the root element of `scenario.add.xml` because runtime XML schema discovery failed. This was a technical package failure, not a traffic-structure observation. The user instructed us to diagnose and continue. Revision03 adds SUMO 1.26 schema-location hints to the route/additional XML files; it makes no traffic or experimental-parameter change and retains the old attempt unchanged.

The exact revision03 card (`c6dd680580ed3ca78400811d2b78bba9050b1da570a717310eb0428551b8b742`) received engineering, data, and scientific static PASS. The existing authorization now releases one repaired R720/S17 smoke. Only if that full technical/data/physical gate passes may the same-seed R0/S17 and R720/S17 diagnostic pair proceed in order. The package allows at most three new starts and no automatic retry. This entry does not assert that SUMO has yet accepted the schema hints, or that `specific_obstacle` has changed.


### Revision03 real-SUMO outcome — stopped before time step

The schema-location correction progressed past the previous missing declaration error, and SUMO loaded the compiled BUILD02 network. It then rejected explicit empty `vTypes` and `nextEdges` attributes on 11 detector elements (22 loader errors) and exited with code 1 after 12.658841 s. The exact run receipt is bound at `artifacts/stage6_recovery_p2_revision_01/engineering/runtime_validation_revision03/runs/RV3_SMOKE_R720_S17_attempt1/execution_receipt.json`. No simulation timestep or traffic evidence exists. The attempt consumed one start; R0/R720 remain blocked by the smoke gate. The current package prohibits retries, so a further attempt requires a separately reviewed immutable package within the bounded cumulative authorization. No `specific_obstacle` conclusion follows.


### Revision04 launch release — second technical repair

Independent engineering, data and scientific exact-card reviews passed the immutable revision04 runtime card. It omits only explicitly empty `vTypes` and `nextEdges` detector filters, whose SUMO 1.26 defaults match the intended unfiltered detector measurement. A compatible rev04 source-provenance adapter passed 16 synthetic tests and 325 binding checks; it is not the complete twelve-gate analysis.

The user-directed troubleshooting scope releases one smoke retry and, only if its complete gate passes, the R0/S17 then R720/S17 pair. The cumulative start ceiling is explicitly 5, one above revision03's operational ceiling; previous two starts are counted. Original total runtime/output limits remain unchanged. At this entry, only `RV4_SMOKE_R720_S17_attempt1` is released and has not started. Any failure stops the card.


### Revision04 smoke process result — full gate pending

`RV4_SMOKE_R720_S17_attempt1` returned 0 after completing 0–2700 s (1.199602417 s) and generated all 17 XML roles. Receipt SHA-256 `c9d7c4b1941b39850f69dd0ee46770b9f57d80c520b61207018f2f09eedaceb1`; manifest SHA-256 `34b48fff76bbcbab8ca60ab7f8e3290a0db5ddedfbe64d30029916e9486b0de5`. This is `process_completed_pending_gate`; the independent twelve-check data gate and engineering physical/log audit must pass before R0/S17. R0/R720 have not started, and no traffic mechanism or `specific_obstacle` conclusion is asserted at this point.


### Smoke gate accepted — R0/S17 released

The RV4 smoke has all 12 independent data checks `PASS`, physical suitability `suitable`, and scientific technical-gate review `PASS`. Gate SHA-256 `c2f5048ff753b342e796fb1e78d0fb030d1b542f3c075ccc8d0d22b1619676ea`. All 1,858 identities entered and arrived; 11 detector files×90 bins, 2,700 TLS states, 138,809 FCD samples, and 6,978 observed lane transitions reconciled. All 300 R vehicles had downstream observations, but 71 lack direct aux0 sampling so their exact merge location is unknown. This is runtime/measuring-chain qualification only and says nothing by itself about `specific_obstacle`, causal bottleneck, or control effect. Only R0/S17 is released; R720/S17 still requires its own full gate.


### R0/S17 process result — gate pending

After the smoke gate was placed at its card-bound path byte-identically, RV4_R0_S17_attempt1 returned 0 and completed 0–2700 s in 0.949802958 s, creating all 17 XML roles (receipt SHA `eb82468fb0593a27112ff2ba32036104fb40463340c949b4edeb63b25499e1b7`). This is process completion only. Independent data review passed all 12 checks; scientific review found no substantive blocker and required correction of the remaining cumulative budget arithmetic. Four of five cumulative starts are used; after subtracting both the smoke and R0, remaining limits are 525.1917540829963433 s and 4,454,450,639 bytes. The single remaining R720/S17 attempt stays locked until its card-bound R0 gate is present and all current records are consistent.


### R0 gate passed — final R720 start released

R0/S17 passed all 12 data checks and scientific review. Gate SHA `ad39fae7016163b59c778ab8b031b43112c409fd1dd7def3804580da993f6570`; its byte-identical mirror is at the card-required gate path. The remaining budget was recalculated using all four receipts: one final start, 525.1917540829963433 s and 4,454,450,639 bytes. The project records and ledger have been corrected. `RV4_R720_S17_attempt1` is released as start five; no additional simulation start is allowed after it.


### Final R720/S17 process result — start budget exhausted

The last authorized attempt `RV4_R720_S17_attempt1` returned 0 and completed 0–2700 s (receipt SHA `cc5c1844be0d88dbac0da6563ffdecf36d3240a651142e38395bae26417b2f2a`). All 17 output roles were generated, and engineering reported no runtime or physical warning. All five cumulative starts are consumed. No additional process may be launched under this card, regardless of the pending gate result. The independent 12-check data audit and scientific R0/R720 interpretation are pending; no `specific_obstacle` conclusion is asserted yet.


### Bounded RV4 diagnostic scientific closeout

Smoke, R0/S17 and R720/S17 all passed their 12 technical checks and physical suitability; the independent scientific review passed the bounded descriptive interpretation. All five starts are consumed; no further simulation is allowed under the card. Paired report: `data/processed/stage6_obstacle_20260913_v1/runtime_gate_revision02/revision04/paired_seed17_comparison01/REPORT.md` (SHA `89584754169062f9cf6c27b6539abfccfc034faf0634b62388b844b4cfbe5a40`). The former symptom of scarce in-demand-period R downstream passage did not recur in this Candidate B seed17 run (300/300 downstream; 240 certain+1 possible in B), but 71 exact merge positions remain unknown. Registered M B travel-time difference bounds cross zero (`positive_response_unidentified`), and U restricted system time increases descriptively by 6.773333 s without identified causal spillback loss. Therefore retain the historic D2 `not_resolved`: the symptom is narrowed as not reproduced once, but `specific_obstacle`, control trade-off, causal bottleneck and formal readiness remain unresolved. This pair is one seed, not inferential evidence; smoke is not an extra replicate.

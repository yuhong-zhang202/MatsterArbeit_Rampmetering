# Independent G2 acceptance review

日期：2026-09-09。范围：用户要求重新审核 G2 是否应该批准；不代替用户验收。

后续验收更新：用户已明确“批准 G2，正式关闭 Stage 2。”当前状态为 accepted；下文 pending_user 为独立审核发生时的历史状态，保留原审核意见。

## 1. 审核结论

**建议批准经本轮小项修正的 G2，关闭 Stage 2 有限无控制诊断。无需新增仿真。**没有发现影响该验收范围的 Blocker 或 Major。核心证据及有限诊断可验收性的置信度 High；下一步研究方向判断 Moderate。

`stage2_acceptance=pending_user` 保持不变。验收不表示整个论文探索结束，不确认当前场景已经适合正式 ALINEA 对照，也不冻结时长、容量、Breakdown、Capacity Drop 或 sweet-spot 定义。

## 2. 审核依据与独立性

本轮重新读取 AGENTS、PROJECT_STATE、DECISIONS、EXPERIMENT_PROTOCOL、相关 WORKLOG、STAGE2_COMPLETION_PLAN、STAGE2_COMPLETION_REPORT 和 Robert 原邮件。正式协议为空是获批有限探索计划明确记录的条件，不额外制造正式实验门槛。

data_analyst 独立检查原始归档与最终派生产物；scientific_reviewer 只读审查方法、解释、测量范围及实际编译网络。主代理核对验收范围、导师原意及文档一致性，并处理修订。二者意见为审核建议，不能替代用户或导师批准。

### 数据证据

- 既有 `revision_04/independent_verification.py --check-only` 实跑通过：232 文件 hash、14,564 车辆、4,320 E1 行、4,200 合流括号端点和 198 同 seed 对照差值。
- 该旧脚本并不单独证明所有逐车字段、E1 窗口组合量和真正首次下游事件：其部分检查使用已有派生分组，事件检查针对给定端点；不应夸大其独立性。
- 本轮补充直接读取八份原始 XML：tripinfo、vehroute、逐车表完整 ID 集一一对应且无重复；全部车辆 depart、arrival、departDelay、duration 一致；内部 E1 Full/A/B/Post 组贡献、流量和加权速度一致；2,100 个 R 真正首次 main_down 观察及前帧一致；八条运行末次入网/到达一致；全部新 attempts 的实际 SUMO 启动数重算为 7。
- 补核可复现入口和结果：`data/processed/stage2_completion_20260909_v1/g2_review/supplemental_verification.py` 与 `supplemental_verification.json`。该检查直接核原始记录，不导入生产分析的聚合函数。
- scientific_reviewer 逐项检查八份 compiled network/additional：两内部 E1 位于各自 8.64 m 内部车道的 4.32 m 处，连接均为 M-only `main_up → main_down`；这不证明上游 feeder 状态。

## 3. 问题处理

| 等级 | 原问题 | 最小处理 | 对结论影响 |
| --- | --- | --- | --- |
| Minor | PROJECT_STATE 保留旧的 Stage 2 incomplete 状态 | 改为 C0–C5 complete、G2 pending、正式时长/储存未确定 | 状态澄清，数据未变 |
| Minor | 当前 ledger 的六个 attempt 仍 pending_revision_03，C17/C23 指向旧通过版本 | 八个选定 attempt 同步 passed_revision_04，并加最终版本与审计路径 | 无数据缺失；历史 ledger_snapshot 不改 |
| Minor | 旧独立 checker 的实际覆盖小于“完整独立复算”的可能读法 | 明确旧脚本边界；补充原始核验并保存可复现入口 | 补核全部一致，不需要改结果或新仿真 |
| Minor | 下一步“唯一优先”未显式写建议状态 | 明确 Proposed | 不自动成为已批准方向 |
| Minor | 方案末尾编制时的 Proposed/not_verified 容易误读为当前状态 | 第 13 节增加历史语境说明 | 保留原审查记录 |
| 文案澄清 | “有贡献负速度异常为零”可能被读为异常值填零 | 改为“未发现有贡献负速度异常记录” | 未改变数据处理 |

上一轮“文档完全一致”及无剩余 Minor 的概括不能替代本次实际检查。本轮发现的是收尾记录和验证范围说明问题；补充独立复算未发现数值错误。

## 4. 三段时长与五项测量审核

| 阶段 | 判断 | 保留限制 |
| --- | --- | --- |
| 0 s warm-up | 适合保留空网加载全过程 | B 切窗不证明稳态，不能移植为正式预热设置 |
| 1500 s demand/measurement | 足以回答本批预定的有限比较问题 | 未证明更长需求期不会出现新行为；不能识别正式 Breakdown 或容量 |
| 1200 s clearance | 对本批八条运行充分；最晚到达 2558 s，距 2700 s 截止 142 s | 仍有延迟入网，不能称零入流恢复或未来工况保证 |

五项检查均在声明范围通过：测量目标；实际覆盖；车辆记录与聚合的遗漏/重复；旧 checker 加本次补核的独立对账；既有离线测试的回归保护。普通 E1 逐 ID 零遗漏/零重复和精确逐车计划时刻仍 Not verified。既有 25 项测试记录被复用，本轮没有为复审重复启动仿真或改变测量规则。

## 5. 验收与后续研究的分界

支持批准的理由是：获批矩阵完整，原始证据可读可复算，主要单因素比较有可靠的有限答案，限制被显式保留。不能以“尚无 Breakdown”为由无限延长这个已经完成的有限工作包。

仍需研究的是当前无控制基线是否适合后续控制比较。MH 两个 seed 在需求期内均无 R 首次下游观察，而主线通过仍高，这是可追踪的线索，不是机制因果证明。不能直接把主线速度高解释成整个系统良好，也不能据此断言 ALINEA 会有效或无效。

Robert 原邮件 `docs/supervision/2026-08-25_robert_hilbrich_reply.md` 明确建议：未出现合理交通崩溃/Capacity Drop 时，应定点检查合流、换道、几何和需求等原因，不通过特殊参数强迫现象。因此提出“主线输入与匝道合流机会关系”的后续诊断方案符合该指导；具体方案及新运行仍待单独授权。

## 6. 路由与文件安全

- simulation_engineer：not required；本轮没有仿真实现、配置修改、环境操作或仿真执行。
- data_analyst：used；完成结果复核和补充核验产物，发现的台账与验证范围问题已处理。
- scientific_reviewer：used；只读复核方法、测量覆盖、时长和解释，建议批准有限诊断；保留正式研究限制。

原始归档、source maps、revision_04 和此前版本均保留；没有修改原始数据、DECISIONS、正式协议、导师记录或仿真配置。当前 ledger 仅补最终分析状态和引用。用户最终验收尚未发生。

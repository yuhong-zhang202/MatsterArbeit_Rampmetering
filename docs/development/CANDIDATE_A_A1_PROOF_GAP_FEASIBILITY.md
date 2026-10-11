# Candidate A A1 safety proof-gap feasibility — Issue #10

2026-10-11. Baseline: PR #9 `7ce8f5e19d737117dc6f25165993fc436244c599`; branch `codex/issue-10-a1-proof-gap-feasibility`; Draft base `codex/issue-8-a1-eligibility-contract`. [Issue #10](https://github.com/yuhong-zhang202/MatsterArbeit_Rampmetering/issues/10).

## 1. 要回答的问题与停止规则

本轮只问：**不改 SUMO 1.26 核心源码和既有车辆模型，仅依赖当前公开接口及受保护项目输入，是否能取得足够的同一时刻状态，建立可验证的 A1 安全规则？** 用户再次明确这是一轮有界 GO/NO-GO 判断，而不是无限延长安全证明。

停止规则：按旧 P0–P10 核心义务检查源码、getter 的实际返回语义与时点、可能的严格界限和车辆覆盖；决定性缺口明确后即结束。未知不生成 ELIGIBLE，不追加大量 synthetic cases 来替代不可观测原生状态。本轮禁止 SUMO/TraCI 启动、core/model/guard/actor/config 改动、科研设计或协议改变。

## 2. 单一候选结论

**Proposed NO-GO：`STOP_A1_UNDER_CURRENT_INTERFACE`，工程、独立数据和科学source/data复审支持；实际交付门与用户决定另行记录。** 在当前接口、固定模型和本轮已验证界限下，没有足够依据实现能够放行的 A1 联合安全规则。建议停止继续扩展当前 A1 的离线资格工具和运行时实现投入，先由用户决定下一条工程路线。

此结论不是“A1 在物理上不可能”，也不是“SUMO 原生红灯不安全”；它是当前可实施证明的工程 NO-GO。没有证明任何未来严格保守方法都数学不可能。新增 core instrumentation 或新的完整联合区间证明属于另一个授权范围，本轮不借此继续调查。STOP3、Candidate A NOT_QUALIFIED、HOLD 和 900 NOT_TESTED 不解除。

## 3. 关键状态可观测性

完整逐变量表及固定源码 URL／物理行／SHA 在 [source-to-state ledger](../../artifacts/candidate_a_a1_proof_gap_20261011_v1/engineering/SOURCE_TO_STATE_LEDGER.json)；[源码读取回执](../../artifacts/candidate_a_a1_proof_gap_20261011_v1/engineering/SOURCE_FETCH_RECEIPT.json)和[限定摘录](../../artifacts/candidate_a_a1_proof_gap_20261011_v1/engineering/SOURCE_EXCERPTS.json)保留来源。源码内部存在不等于公开 getter 直接可读。类别 a–e 分别为：已保存证据、正确时点直接读取、严格源码推导／可信界限、需新增 instrumentation、目前不可取得／可靠界定。

| 状态 | 当前能力与限制 | 影响 |
|---|---|---|
| TLS phase/state/nextSwitch、controlled link、车辆位置与模式 | 有公开getter/现有保存字段；仍必须绑定同一pre-event时点和完整写入历史 | 可以构造身份／事件前提，不能单独证明安全 |
| last action time／action-step alignment | 存在getLastActionTime；源码action-step条件可推导，缩小旧缺口。[getter](https://github.com/eclipse-sumo/sumo/blob/fa7df22d7f1c4ae245192ecc32410a49f1ffb2a3/src/libsumo/Vehicle.cpp#L1012-L1072) / [action条件](https://github.com/eclipse-sumo/sumo/blob/fa7df22d7f1c4ae245192ecc32410a49f1ffb2a3/src/microsim/MSVehicle.h#L633-L637) | 不是所有下一步plan已确定的证明 |
| getNextLinks与原生DriveProcessItems | getter重建路线连接并估算opened，未返回未来plan的request/wait/pass/dist/arrival完整记录。[Vehicle.cpp物理579–608行](https://github.com/eclipse-sumo/sumo/blob/fa7df22d7f1c4ae245192ecc32410a49f1ffb2a3/src/libsumo/Vehicle.cpp#L579-L608) | 不可把nextLinks当未来原生分支证据 |
| getJunctionFoes与未来receiver/foe预约 | approach信息来自上一运动步起点并做运动修正。[Vehicle.cpp物理369–418行](https://github.com/eclipse-sumo/sumo/blob/fa7df22d7f1c4ae245192ecc32410a49f1ffb2a3/src/libsumo/Vehicle.cpp#L369-L418) | 不能作为下一红灯步重算预约的同态返回 |
| getStopSpeed／getFollowSpeed与actual CURRENT／finalized speed | 接口用于计算特定情景，CalcReason FUTURE与CURRENT分支可能不同。[接口](https://github.com/eclipse-sumo/sumo/blob/fa7df22d7f1c4ae245192ecc32410a49f1ffb2a3/src/libsumo/Vehicle.cpp#L894-L929) / [Krauss分支](https://github.com/eclipse-sumo/sumo/blob/fa7df22d7f1c4ae245192ecc32410a49f1ffb2a3/src/microsim/cfmodels/MSCFModel_Krauss.cpp#L101-L108) | 单个可调用公式不是未来实际速度 getter |
| 未来 seen／effective offset／DriveProcessItem、vSafeMin、最终速度与联合后车／receiver状态 | 需要完整内部决策输入或严格覆盖全部分支的界限；现接口证据未闭合 | 核心普通制动、不越线与联合安全不能靠已知scalar补齐 |

直接可读的状态仍有价值，但当前缺口不是“再多抓几个相同快照字段”即可闭合。seed 或自报proof_complete不能替代实际branch、RNG/device/LC及联合状态证明。

## 4. 车辆覆盖与联合条件

逐角色／路径和 P0–P10 状态见 [coverage/joint matrix](../../artifacts/candidate_a_a1_proof_gap_20261011_v1/engineering/COVERAGE_AND_JOINT_MATRIX.json)。每一条件区分 PROVED / CONDITIONAL / UNRESOLVED / NOT_OBSERVABLE；身份和源码子条件通过不能替代整个义务通过。69条记录覆盖P0–P10及12类population，但明确不是整个模型依赖的穷尽schema；S69归档friction/stops/startup/influencer/RNGcontinuation、length/minGap/class等未完整审计依赖。

- storage front/followers和ingress：旧snapshot有27+15，但仅证明A07保存范围。未来每一步须重新枚举、绑定route/class/type/modes/action/device，并处理内部／shadow／插入／遥控路径。
- 一步内可能到达的未枚举车辆：已知固定路径长度和运动界限只能给条件排除；不能由一次几何不等式宣布所有未来入口覆盖。
- receiver/leader/foe：ramp_mid静态foes0限于该junction；不排除同向占用、后车或下游merge风险。旧nearest vehicle与secureGap返回不是完整jointreservation证明。
- M/R/U/X：受保护静态路线可限定谁经过meter；M/U/X仍可能在下游交互，不能把meter路径排除扩大成整网无影响。

必须同时满足普通制动（不用emergency rescue代替）、不越线、front/follower相互运动界限、lane-change/shadow、黄转红event和receiver/foe响应。当前粗速度包络可以在未知时拒绝，却不能为实际关键状态提供足以放行的联合充分条件。小范围源码公式计算通过不是这些义务已证实。两个说明性数学例子（非native轨迹）：v=9m/s、普通减速度4.5m/s²、emergency9m/s²、Δ=1s，粗区间允许0m/s就不能证明全部结果≥4.5m/s；旧front若只用v+aΔ上界，约2.646m位移也超过约1.002m目标距离。这只说明当前粗界限不足，不声称SUMO实际选择这些结果。[输入、算式与适用边界](../../artifacts/candidate_a_a1_proof_gap_20261011_v1/engineering/COVERAGE_AND_JOINT_MATRIX.json)。

## 5. 工程代价与最小下一步

本轮不实施替代路线。以下为 Proposed，不能改写为用户批准或Robert意见：

| 路线 | 能解决什么／仍缺什么 | 代价与风险边界 |
|---|---|---|
| 继续仅加现有getter／重复offline tests | 可补部分身份和观测记录，但不暴露未来完整内部plan | 不建议作为下一实现任务；可能继续产生UNKNOWN工具而无放行证据 |
| core内步只读instrumentation设计 | 有机会取得正确决策阶段的plan/final-speed/预约状态 | 超出本轮不改core约束；仍需时点、observer效应、构建版本和独立联合证明；不可预先保证成功 |
| 与Robert讨论更简单、来源明确的signal/actuator operation | 可重新确定工程安全责任和能验证的接口路线 | 不等于Candidate B启动或立即删除guard；应由新Issue定义实现与最小资格门 |

**最小后续任务：用户／Chat先审查此NO-GO和缺口清单，决定是否向Robert讨论更简单operation，或另行批准instrumentation可行性设计。** 本轮结束，不以“仍可以多试”扩展。源内插桩、改变模型、新runtime/smoke、CandidateB或放宽合同都没有授权。工程初步估计：一次用户／Robert讨论和静态设计审阅需约 **2–4工程小时**；若另外明确要求内部观测设计，设计评估约 **1–3工程日**。假设一名熟悉现代码的工程人员、仅做方案与接口审阅，不含native实现／构建维护／运行验证；后者无法可靠估计，也不在当前授权内。这些不是实测工时。[估计、前提与风险](../../artifacts/candidate_a_a1_proof_gap_20261011_v1/engineering/COVERAGE_AND_JOINT_MATRIX.json)。

## 6. 数据、验证与公开复现边界

独立旧证据重核：42unique witnesses（27storage+15ingress），旧gap/required/margin和唯一R_flow.1拒绝一致；六窗口观测步数[6,0,0,0,0,0]，五未观测窗口保持null/blank，所有完整窗口trackingerror blank，零完整cycle、1206行derivedthinledger；536保护文件未变。[旧证据独立回执](../../data/processed/candidate_a_a1_proof_gap_20261011_v1/OLD_EVIDENCE_RECHECK.json)。

实际红后继1206→1207从未运行；条件性canBrake42/42不是完整nativebranch（仍0/42），无新native red observation。公开checker只读已提交证据、源回执／摘录和静态ledger；不读取ignoredraw、不启动server、不从Synthetic产生安全证书。旧43helper回归不因本轮文档／新静态ledger重新执行；原版本证据保留。

实际工程公开静态checker与独立数据checker均return0/PASS，Python3.13.0标准库；0新增unit/synthetic tests，旧43项SKIP（实现未改且旧精确版本已有验证）。18份官方源真实读取837752bytes；含继承缓存共25完整源、44物理行摘录由独立本地读回核对。公开复现只验证receipt/excerpt一致，完整源字节本地增强需官方refetch，不冒充公开runtime认证。[工程回执](../../artifacts/candidate_a_a1_proof_gap_20261011_v1/engineering/STATIC_VERIFICATION_RECEIPT.json)；[独立数据报告](../../data/processed/candidate_a_a1_proof_gap_20261011_v1/DATA_REVIEW.md)／[实际回执](../../data/processed/candidate_a_a1_proof_gap_20261011_v1/INDEPENDENT_REVIEW_RECEIPT.json)。

首次68-row draft PASS输出保留，但初始binding未保存，不能用final69-row R1binding为旧PASS补签；只有当前R1具精确可复现绑定。父任务实际交付codecleancheckout与最终science门尚待独立回执，不声称已通过。

```sh
python3 scripts/candidate_a_a1_proof_gap_20261011_v1/verify_public.py
python3 data/processed/candidate_a_a1_proof_gap_20261011_v1/independent_review.py
```

## 7. Issue验收逐条核对

| # | Issue原验收条件 | 当前交付范围 |
|---|---|---|
| 1 | 现有核心证明义务是否逐项关联 SUMO v1_26_0 源码/官方接口、准确的状态时间点与可观测性级别？ | 已覆盖：69-row源码／接口时间点和P0–P10双向引用；非穷尽schema。 |
| 2 | 是否明确列出 TraCI **直接可读**与仅**源码内部存在 / 推断 / 尚未知**的区别？ | 已覆盖：类别a–e及getter同态／时点边界，关键源码物理行引用。 |
| 3 | front、followers、ingress、receiver、foes 与其他可能进入车辆的覆盖证明和边界是否清楚？ | 已覆盖：12类population枚举／条件排除／UNKNOWN合同，未来全覆盖未认证。 |
| 4 | 是否检查了普通制动、后车、红灯转换与下游接收的联合条件，而非只检验一个离散停车不等式？ | 已覆盖：联合义务表和两个粗区间不足的分析例，非native轨迹。 |
| 5 | A07 42 witness / STOP3 / V3 缺失值保持，未把未执行红灯步写成真实观测或将合成数据当作安全证据？ | 已覆盖：独立42映射／六窗口／536保护重核；0完整nativebranch／red后继。 |
| 6 | 是否有明确的 GO / bounded evidence / STOP 决策与一个**最小后续任务**，列时间/工程成本与风险（可给区间，不得虚构已测量值）？ | 已覆盖：单一ProposedNO-GO／最小用户决策任务／估计2–4h、1–3日设计与风险。 |
| 7 | 是否如实保留 Candidate A `NOT_QUALIFIED`、当前 `STOP3`、900 `NOT_TESTED`、formal protocol 未冻结，以及 no-new-SUMO runs？ | 已覆盖：原native/guard/core/model/协议/旧数据不改，0starts；资格和冻结状态保留。 |
| 8 | 代码/证据/测试在干净 checkout 中可复现；若需本地 raw，分开注明公开复现能力和本地额外核验，报告真实 PASS/FAIL/SKIP 和 provenance。 | 工程与独立数据公开静态检查PASS；实际交付commitcleancheckout及最终science门仍待记录。 |

## 8. 当前状态与交接

Stage6既有结项保持；formal protocol为空／未冻结。No new SUMO/TraCI runs。所有旧失败／raw／reviews保留。DECISIONS、协议和规范安全合同不改。工程与数据／科学结论均为advisory，自检不等于用户验收。下一位用户／Chat审查新DraftPR；任何下一步建议不构成执行授权。

工程→数据→只读科学source/data门通过；无未解决交付Blocker/Major/requiredMinor。P3/P4/P5/P7/P8/P9仍为A1推进blocker，不是本轮调查交付失败。[科学checkpoint](../../artifacts/candidate_a_a1_proof_gap_20261011_v1/SCIENTIFIC_SOURCE_DATA_REVIEW.md)。

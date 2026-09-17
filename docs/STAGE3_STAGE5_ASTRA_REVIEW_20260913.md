# Stage 3 / Stage 5 独立复审与更正说明

日期：2026-09-13。性质：对既有探索结果的独立复审，不是新仿真或正式实验。

状态：复审完成；最终科学复审确认本次历史探索评估范围内无剩余Blocker、Major或必要修改。推荐接受修订版T54；T54待用户接受。

## 1. 审查问题与权限

用户要求判断 Stage 3、Stage 5 是否需要重做、哪些结论应推翻，以及是否建议批准 T54 后进入 Stage 6。该问句不记录为用户已经接受 T54。

本轮从当前文件、原始 XML、代码及异常输入探针重新核查，未用历史代理的 PASS 作为新的独立验证。Stage 2 的用户验收与 Stage 4 的实际运行记录保持有效；本轮不改变研究方向、注册判据、需求、seed、时窗或正式协议。

## 2. 已确认保留的结果

独立全量复算重新检查 Stage 3 八条档案：246,175 个 lane/class/time 单元、99,955 个 episode、2,100 个 R 首次下游事件、7,120 个 shared R/U 共现标签以及 96 个敏感性值与既有结果一致。额外原 XML 扫描确认 232 个源文件哈希通过，八条运行的 FCD/TLS 时间标签与 4,320 条 E1 记录完整；本次发现的缺速、未知身份/车道、错误时间标签及有贡献无有效速度等故障未出现在本批档案中。[A-DATA]

1,264 个聚合区间、48 条时序及其峰谷摘要、96 个整窗值均从原 E1 数据复算一致。Stage 3 并非没有做时序敏感性；但极值箱支持秒不等于一段连续高/低交通状态的持续时间，也不证明任何聚合粒度最合适。[A-DATA]

## 3. 本轮发现及处理

### R1：异常输入可能被错误标为通过

四类端到端故障探针分别注入：缺失 FCD 速度、未知 lane、保持条数但改变 TLS 时间标签、E1 有贡献却无有效速度。旧分析器仍可生成 `analyzed_archive_only`，覆盖表也可显示 passed。旧的 26/26 离线测试通过并没有覆盖这些组合，因此不能据此声明分析器普遍能拒绝异常输入。[A-ENG]

这些故障影响未来处理资格；本批历史数据是否受影响须由原 XML 全量检查与独立复算决定。前述检查没有发现本批触发，故不推翻旧观测值。修复范围限定为异常输入拒绝、资格检查及对应离线回归，保留原源码和历史合同。现已修复：33/33离线测试通过，15种端到端异常变异均被拒绝并留下INCOMPLETE，未生成通过manifest或结果表；内部车道真实停驶归属与1499/1500/1501入网边界也已测试。修复后八条固定档案的96/96结果文件与原件逐字节一致，manifest除输出路径外一致。[A-ENG; A-INV]

### R2：交接证据编号没有定义映射

旧交接表和门表使用 `E-S3-FINAL` 等编号，报告索引使用 `EV-*`，不存在完整显式对应。旧 15/15 验证只核 artifact inventory 的文件哈希，不能证明每个方法项的 evidence_id 都能解析。本轮新增精确路径/哈希/定位索引及更正交接表，保留旧表。本更正报告明确采用 `evidence_index.csv`、`corrected_method_handover.csv` 和 `unpaired_seed_contrasts.csv` 作为 T53/T54 的当前补件，补件不产生新研究决定。[A-DATA]

### R3：五个不可配对项目未披露

原 801 条对照记录中，796 条形成 398 个可作双 seed 比较的键，其余五个键仅有单 seed。旧脚本跳过了这五个键。43 个符号不一致是 398 个可比较键中的真实计数；五个缺配对键不属于新增符号翻转，也不能补造零值。[A-DATA]

更正表逐项保留以下键及可用 seed，并标记 `not_paired_across_both_seeds`（不可作双 seed 比较）：

| 对照 | 窗口 | 类别/区域 | 已有 seed |
| --- | --- | --- | ---: |
| ML−C | Post | X@cross_tls_internal | 17 |
| RL−C | A | R@urban_tls_internal | 23 |
| RL−C | B | R@urban_tls_internal | 23 |
| RL−C | Full | R@urban_tls_internal | 23 |
| RL−C | Post | U@urban_diverge_internal | 23 |

五项指标均为 `stopped_episode_support`，单位为 `sampled_region_stop_support_s`。旧对照摘要脚本不能未经缺配对检查直接用于新批次。

### R4：用途缺口被描述成已证明的结构障碍

旧交接首行 `structural suitability obstacle` 和报告中 `before ... protectable mainline-side state` 的措辞偏强。注册 EJMI 要求中间候选同时比 C/MH 两端包络更低速、更高占有率，并满足 A/B、两个 seed 与持续性条件。这是一个较窄的充分判据；不满足它，不排除较小、较短或单调的主线受损。[A-S4]

**更正后的事实：**在已运行 qMain=3500/3650、两个 seed 和 A=[0,1500) 内，q3500 的 R 首次下游事件为 14/11，q3650 为 0/0；四条候选均未满足注册 EJMI。没有在已注册候选中识别出 EJMI 与 R 通行共存。不能据此认定结构因果、真实损伤与匝道排除的时间顺序、所有未测需求点均不适用，或强制选择加长主线。[A-S4]

`specific_obstacle` 只能表示这个具体的用途证据缺口，不能表示已证明场景结构错误。Q1/Q3 保留声明范围内的 `supported`；Q2/Q4 保留 `not_identified`。旧注册机器动作保持原值，不通过事后更改阈值制造阳性结果。

### R5：阶段状态叙述陈旧

计划及 T43 文件部分正文仍写 Tier 2 未启动，与已完成四次运行的状态冲突。本轮只更正可变状态说明；已归档合同、运行、原始结果与哈希绑定历史报告不改。

## 4. 证据入口与复用限制

- A-DATA：`data/processed/astra_stage3_stage5_reaudit_20260913_v1/audit_results.json`、`independent_all_runs.json`；同目录 `corrected_method_handover.csv`、`evidence_index.csv`、`unpaired_seed_contrasts.csv` 与 `supplement_verification.json` 为本次采用的补件；12个原证据编号已有23条精确路径/哈希/位置映射。
- A-INV：`data/processed/astra_stage3_stage5_reaudit_20260913_v1/repaired_invariance.json`，SHA-256 `17588ed3f6c790442b11f2986122dbad470d8883f162ccc2bb5bf7e50d2550cc`；8/8档案及96/96结果不变。
- A-ENG：`data/processed/astra_stage3_stage5_engineering_reaudit_20260913_v1/ENGINEERING_REAUDIT_REPORT.md`、`postfix_test_result.json`、`static_observation_recheck.json`；同目录保存旧代码副本、故障探针、修复后测试及来源记录。
- A-S4：`data/processed/stage4_qmain_sequential_20260912_v1/final_evidence_ledger_snapshot.json`、`analysis/final/revision_04/registered_final_decision.json`；`docs/STAGE4_QMAIN_SEQUENTIAL_REGISTRATION_PROPOSAL.md` §5（注册 EJMI 的定义）。

本轮 Stage 4 复核限于不可变快照、注册决策及其既有来源链，没有重新复算四条新增运行的全部原始 XML。Stage 3 的原 XML 复算与 Stage 4 的来源核验应分别报告。G06仍只支持描述性敏感性检查，不构成统计功效、跨 seed 稳健性或时长充分性的证明。

## 5. 修订后的验收建议

**无需重跑 Stage 3/4 仿真，无需推翻已独立复现的核心观测；原 T54 包不能原样沿用，应连同本轮更正与补件验收。**

| 项目 | 本次建议 |
| --- | --- |
| Stage 3 固定八条历史分析 | 保留；最小防错修复后96/96结果不变 |
| G05 实现核验 | 在本次修复、回归与固定档案核验范围内通过；不承诺所有未来异常都已覆盖 |
| G06 敏感性 | 保留描述性结果，增加5个不可配对项披露；不能宣称统计稳健 |
| G08 方法交接 | 连同新增12 IDs/23路径映射和更正22项表验收 |
| Q1 / Q3 | supported，仅为声明范围内的可观测性及城市侧暴露 |
| Q2 / Q4 | not_identified；核心question-level unknown=2 |
| T54分类 | 建议 completed / specific_obstacle；preliminary_ready=false |
| 用户接受状态 | pending_user_acceptance；本轮用户是在请求审查是否应批准 |
| Stage 6 | 接受修订验收后可进入Proposed设计草案；不是正式实验资格 |

`completed` 指这轮有边界的探索评估任务可结束，不表示后续不需要任何验证。`specific_obstacle` 指当前有限证据未识别所需主线侧特征，且q3650需求期R通行为零；结构原因、其它需求点、修改后的场景及控制效果仍未知。

Stage 6应优先把“保持匝道权衡研究方向，如何获得合适的基准场景与测量”写成待讨论设计问题，再提出候选方案给用户及Robert。加长主线、调整插入、改变行为模型或缩小研究范围均未因此获批。正式协议仍为空；没有新增仿真、实现控制器或发送导师消息。

旧 Stage 3/4 合同故意绑定旧源码哈希，修复后的源码不能冒充旧版本运行。原源码及测试副本保存在工程审计目录，新复算使用单独的audit-only ledger并记录新源码哈希；不得回写旧合同或关闭来源检查。旧 `build_stage3_t34_review.py` 对单seed键仍会跳过，未来新批次复用前必须增加显式缺配对输出；本批已由新补件完整披露，不继续宣称该旧脚本可直接通用复用。

新源码SHA-256：`6558f971bc713397e26a41fd4b2b4a71255a38ff7b6122d77df6056b88b6b8f6`。旧源码副本SHA-256：`195fcc2f8c534919eac540fd4e3692e111dda447d15373dec14b64f052a47b96`。

置信度：本批数量/不变性与具体缺陷 **High**；有限用途分类建议 **High**；结构原因、未来场景适用性与控制收益 **Unknown**。


## 6. 五项测量复审与交付边界

| 项目 | 本轮结论 |
| --- | --- |
| 测量目标 | 声明cohort、lane、时窗、技术停驶及端点范围内通过；不等同完整系统损失 |
| 实际覆盖 | 八档案静态lane/detector/互斥R路径核验通过；本轮未做新的运行时加载 |
| 遗漏/重复 | Stage3原XML样本及对照披露通过；普通E1逐ID零遗漏仍未验证 |
| 独立对账 | Stage3全量重构与96产品修复前后不变通过；Stage4为快照/决策依赖复核 |
| 回归保护 | 已发现四类缺陷及新增边界测试通过；旧对照生成器未来复用限制继续保留 |

原复审文件及原T54包保留为历史记录；当前接受对象为 `docs/EXPLORATORY_VALIDATION_T54_ACCEPTANCE_PACKAGE_REVISION_02.md` 加本报告与引用补件。仅修正文档、代码防错和已授权旧档案离线处理，没有提交git commit或改动不相关未提交文件。

Subagent routing：simulation_engineer used（故障复现、最小修复和离线回归）；data_analyst used（新原XML复算、索引与缺配对补件、96产品不变性）；scientific_reviewer used（只读复核实现、实物哈希、解释及验收建议）。

# Issue16 source snapshot

URL: https://github.com/yuhong-zhang202/MatsterArbeit_Rampmetering/issues/16

## 任务性质、用户意图与最终目标

**用户授权创建一个整合性工程 Issue，由 Codex 担任工程负责人，在合理边界内连续完成问题定位、必要源码/文献调查、最小修复、审查、真实自然条件资格验证和 GitHub 交付；避免每个细小工程决策来回请示。**

**唯一科研目标：**让已经能在短时测试中跟随 ALINEA 的 SUMO 匝道信号执行器，在论文所需的**自然交通输入**下，足够安全、准确、可核账、可复现地运行，取得**有明确适用范围的正式实验前执行器资格**，而不是开发工业级安全控制系统。

**成功不是“无论代价都跑出 PASS”。** 这次必须有界：若不能在可信的最小改动和经授权的有限运行内达到资格，就如实给出 `NOT_QUALIFIED / BLOCKED`，停止无限改 guard、重新跑直到通过或为追踪服务量而强行放车，并将根本性技术/方法取舍交用户与 Robert Hilbrich。

本 Issue **批准 Codex 自主进行只读调查、必要的有限实现、离线验证、风险相称的内部审查、文档/新 Draft PR 更新和运行卡准备**。**它本身不是新的 SUMO 单次执行许可证**，不授予独立 runtime budget 的重新分配、已消费 canonical release 重用、自动扩大运行次数、改变研究问题/协议或放宽真实安全要求。需按照下方“真实运行权限门”办理。

## 当前版本与不可改写的失败事实（2026-10-15）

上游：
- [Issue #12](https://github.com/yuhong-zhang202/MatsterArbeit_Rampmetering/issues/12) / [Draft PR #13](https://github.com/yuhong-zhang202/MatsterArbeit_Rampmetering/pull/13)：短时固定、动态和真实 ALINEA 技术证据，以及普通供车不足/受限时的执行方案，**未取得完整自然场景资格**。PR13 最后一轮 GitHub `@codex review` 为 `REVIEW_PENDING / NO_VERDICT`，不可写成 PASS 或 CANCELLED，也不以无限复审阻塞其他获批准备。
- [Issue #14](https://github.com/yuhong-zhang202/MatsterArbeit_Rampmetering/issues/14) / [Draft PR #15](https://github.com/yuhong-zhang202/MatsterArbeit_Rampmetering/pull/15)：首次自然需求资格。发布本 Issue 前 PR15 head = **`af988faddaa271ac2a8f80fe3fd3558ff2898618`**；branch **`codex/natural-actuator-qualification`**，base为PR13分支 `codex/issue-12-alinea-signal-policy`。执行源 checkpoint `b6c60b927fc71a8750f5674f2cf168824b78cf05`；执行精确卡 `b73c678130604d1cef41dd5ecb70a79cc868084e91ae5033cc179393c25f6982`，已经一次消费。开始前重查真实最新 head、卡、分支、未提交工作与依赖差异，不能混用版本。

**第一次自然运行：**
- Run `QUAL_NATURAL_ALINEA_R900_S17_01`，自然输入 M3600/R900/U360/X180，seed17，1s step，计划0–4200s、控制从600s开始，预定六个[1200,3000)的300s评价窗；非正式实验。
- **实际在 t=650 STOP，`POST_CURRENT_GAP_BOUND_DENIED`，`NOT_QUALIFIED`**；全六窗口、持续放行/下游恢复和正式效果均 **NOT_TESTED**。此失败不是仿真碰撞观察，也不自动等于误报。
- 保存的同一帧原生查询：后车 R_flow.1 在 ramp_storage；前车 R_flow.0 已进入 controlled internal；查询可比间距 **9.610493939m**，`getSecureGap`（当时输入/leader emergency brake 等）返回 **13.089892327m**，差 **−3.479398388m**。**先前额外1.1m不是本次硬拒绝原因**；不能把旧1.1m改小当作本次问题的答案。
- 六完整周期各N=0仍继续，说明原“少于两车无条件当故障”已有有限改进。独立 [600,650) 原始C≈12.311518、E_scheduled=E_executed12、实际N=1，`C−N≈11.311518`；37/50 pre-frames储存段为空但不能解释全部缺额。不得把物理欠额加到C−E_scheduled中追赶。
- 原冻结 reader `exit1 / UNKNOWN`（STOP终点枚举及非零worker出站限制）；单独 processed 观察前缀已独立核账，但不可回写原 PASS。R0最终车尾被截断，原raw保留，本地227文件/157,210,133 bytes；github公开仅摘要、manifest/hash。
- 新**独立900秒预算**已真实使用83.637436041秒，账面剩816.362563959秒，**原唯一启动许可已消耗；余额不授权任何新启动**。旧scope余额不可pool。未合并上游、正式协议0B未冻结、A1 UNRESOLVED/正式资格NOT_QUALIFIED保留。

权威资料：
- [首次自然运行收口](https://github.com/yuhong-zhang202/MatsterArbeit_Rampmetering/blob/af988faddaa271ac2a8f80fe3fd3558ff2898618/docs/development/NATURAL_ACTUATOR_FIRST_NATIVE_CLOSEOUT_20261015.md)
- [独立真实数据](https://github.com/yuhong-zhang202/MatsterArbeit_Rampmetering/blob/af988faddaa271ac2a8f80fe3fd3558ff2898618/data/processed/natural_actuator_qualification_20261015_v1/first_native_execution_v1/DATA_NATIVE_REPORT_V1.md)
- [最终科学审查](https://github.com/yuhong-zhang202/MatsterArbeit_Rampmetering/blob/af988faddaa271ac2a8f80fe3fd3558ff2898618/artifacts/natural_actuator_qualification_20261015_v1/SCIENCE_FIRST_NATIVE_POSTREVIEW_V1.md)
- 先前 Issue14 自然资格七项要求及 `docs/development/THESIS_ACTUATOR_MINIMUM_QUALIFICATION_PLAN_20261015.md`。

## T0：Context Preflight 与证据复核

读取 `AGENTS.md`、`docs/PROJECT_STATE.md`、`docs/DECISIONS.md`、`docs/WORKLOG.md`、`docs/problem_records/README.md`、未冻结的 `docs/EXPERIMENT_PROTOCOL.md`、Issue12/14、PR13/15及准确头部差异，现有 protected 源、首卡、raw manifest、数据/科学审查。

**首先确定完整执行链的位置和时间：** t650 的 STOP 由哪个对象/函数在 POST 状态抛出？是在同一辆后车的普通跟驰中，还是绿灯准入、黄转红/下游接收的特殊保护？是否会把**已经发生在 SUMO 原生车辆运动后的安全间距参考值**不满足，视为控制器本身的危险并强制停止？

以现有真实原始证据优先；禁止为重复解释t650再跑一次。记录完全一致的距离口径、车辆速度/车长/minGap/跟驰模型参数、leaderEmergencyDecel与原生CF使用的实际减速度、query参数及调用时刻，必要时检查真实相关的跟车类型/route/occupied internal link。若证据不能唯一判定，标记UNKNOWN，不补造状态。

## T1：一次有边界的科学/技术判定（最重要）

**必须引用官方机制及必要文献，不用“感觉可以放行”替代依据。** 优先查：
- SUMO官方 `TraCI Vehicle Value Retrieval` 中 `getLeader / getSecureGap` 参数与结果语义，`Car-Following Models`、`Simulation/Safety`、`Traffic Lights`、`VehicleInsertion`；
- **固定 SUMO 1.26.0 tag `v1_26_0` 官方源码**中 Krauss、`getSecureGap` 调用/处理及红灯/normal car-following/车道连接的相关分支，源码commit、物理行与适用时点；
- Papageorgiou & Papamichail (2008), _Overview of Traffic Signal Operation Policies for Ramp Metering_, DOI 10.3141/2047-04；Kotsialos et al. (2006), _Discrete release rate impact on ramp metering performance_, DOI 10.1049/ip-its:20055003；FHWA Ramp Management and Control Handbook，及现有项目文献索引。它们主要支持政策与研究定位，**不直接证明本次gap安全**。若需要，补1–2篇与微观跟车、信号安全/冲突界限直接相关的文章，不启动大规模综述。
- 对每项结论分别标记 **源码/官方直接支持、实测事实、工程推断、仍未验证**；未取得全文就注明摘要层次。

作出且**只作出一个**有证据支撑的判定：
1. **KEEP_HARD_STOP**：当前触发真实且必要的安全边界，不安全地调整会影响研究可信度；
2. **MINIMAL_SCOPE_CHANGE_PROPOSED**：该硬门误把现有原生正常跟驰/诊断参考条件当成控制器失效，存在可以明确限定时点/角色/责任、并保留真正安全STOP的**最小替代合同**；
3. **UNRESOLVED_ESCALATE**：现有证据不足以判定该规则的必要性和更改风险；不继续自造更复杂安全证明，建议咨询Robert。

**不能仅因为过了9秒/差几厘米就当误报**，也不能无证据删除 `getSecureGap`、改参数造 PASS。真实碰撞、急刹、红灯违规、相位/车辆覆盖UNKNOWN、后车和接收空间重大风险仍要停止。优先最简单的官方原生机制 + 合理信号配时 + 独立在线/后验安全记录。A1完备预测证明不再重开。

## T2：可安全推进时的最小实现／离线检查（无需逐项请示）

只有 T1 支持 **MINIMAL_SCOPE_CHANGE_PROPOSED** 且不越过已有批准的科研/安全边界时，Codex 可在**新独立分支**实施最小且局部、可回退的修复，并做必要的离线反例测试；如实保存旧规则、旧FAIL及新的责任界限。任何实质性放宽原安全硬停合同必须先完成科学审查并取得**用户明确批准该合同**，不能用这个新Issue的笼统授权代替。

优先复用 PR15 的普通自然需求执行器、C−E_scheduled scheduler、E1、reader、guardian。不得换算法/seed/路网/需求/车辆模型/速度因子/黄红时间或改ALINEA数学来追求资格。不能因供车不足、receiver已知受限而自动STOP，但不能让未知接收或真正危险悄悄通过；暂不能确证的真实安全义务 fail-closed 并说明局限。

最低测试覆盖：保留原 t650 输入回放、需要拒绝的异常状态、正常供车不足/接收受限、合法恢复、原始C/E/N和partial/pending分账；真实 native 才能证明的状态明确 `NOT_TESTED`。修复原reader能正确保留 STOP/失败前缀与EOF的必要限定分类，**不可把旧截断结果写成完整资格**。不要扩大临时框架/离线case矩阵。

工程→独立数据→只读科学复核根据风险进行；**修复真实阻塞，不为0条低风险review意见无限循环**。GitHub @codex review有结果即可分析；未返回时记PENDING/NO_VERDICT，不自动重发卡住的PR13复审。

## T3：真正自然交通条件的有界资格验证（授权门前准备与门后执行）

**优先争取一轮**沿用原M3600/R900/U360/X180、seed17、dt1、0–4200s、600起控、[1200,3000)六个完整300s窗的真实动态ALINEA资格运行。禁止使用600–1200人工蓄队、短R900预条件假装自然输入，禁止拿旧技术短测或合成fixture拼成同版本资格。

**真实启动必须另有可核的全部权限：**
- 重新创建**独立新身份**、精确card、冻结运行源/inputs/reader/SUMO1.26/env，三方精确预审及 canonical release；
- 获取用户对**本次安全合同（若变更）和这一新精确运行卡**的明确批准。上一轮卡 `b73c678...` 和任何已消费 release 不可重用；
- 核对独立900s资源账 **83.637436已耗/816.362564剩余**，其中数值余额≠一次新运行权限；若下一轮需要独立新预算/新的start许可，另行询问、不得自行授权、扩大或与旧预算混用；
- 保留安全和资源 guardian/PID/超时/硬盘/cleanup 门，真实异常/UNKNOWN严格STOP；不为成功改变失败数据、重启相同卡或换seed；
- 如果全部权限不足，**持续完成所有非运行步骤，准备精确批准材料，然后明确等待人类授权**。不要把“持续推进直到QUALIFIED”理解为可以跳过权限。

运行如获批准，必须：
1. 保存 Chronological **原始ALINEA C**、E_scheduled/E_executed、C_selected/C_applied、独立真实N和完整C−N分解，记录每次Feedback及申请/实际应用延迟；供给不足、接收受限、实际非可达容量缺额不得以名义算术抹掉或无限追债。
2. 连续完整周期、pending/partial E1、正常供车不足/receiver红保持/恢复、历史失败起因、所有必要安全监测；特别关注t650类状态的作用域与边界。
3. 保存碰撞/teleport、异常制动、红灯新入口、TLS/G/y/r实际相位、车尾/正常离网、四流EOF、完整4050请求/已插入/尚未出发/已完成/未完成、匝道及城市共享路段观察，并以同一明确口径核账。
4. **必须达到真实证据标准才可判有限`QUALIFIED_FOR_NATURAL_PREEXPERIMENT`**：运行到预定4200、六个评价窗足量观测、必要安全无不可接受异常、独立数据完整、目标与实际放行/供给/容量约束解释合理、异常和截断未冒充零。误差容差应在运行前依据研究目的/来源先界定并记录，不因结果事后调阈值；一次seed只证明该条件的预实验资格，不证明全部300–900所有状态/多seed/正式效果。
5. 首次再次 STOP 或证据不足时，必须先报告 **NOT_QUALIFIED + 原因**，不自动继续跑第二次。只有新证据给出**明确单一的可修复真实问题**并取得新精确授权后才允许一个定向后续尝试；若触及真实安全未知或反复守门失败，**停止该路线，优先与Robert讨论更简单的官方操作路线**。

**停止边界：一次核心有界调查、最多一次关键局部修复与一次经批准的主要自然运行；后续如确有新信息仅建议至多一次经重新批准的针对性复验。不允许“直到PASS”的无限自动循环。**

## T4：交付与GitHub规范

必须遵守 Issue → Codex → Draft PR → 用户/Chat审查。以 PR15 新分支 head 为基线，新 Draft PR base = `codex/natural-actuator-qualification`，开始前若head变化先重新核对；**不得修改/合并/retarget PR13/PR15 或其他上游**，也不自动关闭现有Issue。仅当本任务有真实增量才提交新 Draft；避免把已有上游已发布的证据再复制大批文件。

交付尽量精简，至少：
- 一份 `docs/development/` 间距硬STOP适用性判定（含官方出处/车距口径/源码/风险/结论/最小更改边界）；
- 必要的隔离源码差异、少量覆盖真正风险的测试及测试命令/结果；新run确实执行则提供真实卡/manifest/有限结果和数据、科学审核，不上传完整raw/个人文件/canonical；
- 更新既有 `docs/problem_records/PRB-004...`（若更适合新PRB则只新增1个）、PROJECT_STATE、WORKLOG及Dashboard任务状态。原STOP、FAIL、reader exit1/UNKNOWN、尾部截断、未测六窗、旧证据原字节保留。DECISIONS或正式EXPERIMENT_PROTOCOL须用户批准，不能自动冻结；正式实验不在本Issue范围。
- 如果资格未达标，**不能仅把相同NO-GO记录反复生成多层文档/Issue**；交付一个证据支持的决策点，让用户/Robert决定继续、换路线或调整正式实验范围。

## 最终必须报告

**① 通俗解释**根因与修复，判断是合理安全 STOP、合同范围问题还是无法证明；**② 硕士论文整体进度估计**；**③ 真正执行的步骤、实际运行身份/权限和测试结果，直接指向Issue/PR/commit，并给用户唯一下一步**；**④ 建议当前AI模型**。另外列清 `TECHNICAL_PASS / LIMITED_QUALIFIED / NOT_QUALIFIED / NOT_TESTED`，不能夸大。

**最高优先级：科研可信与及时毕业。** 若已足以进行下一阶段，不继续安全工程“打磨”；若不能在合理成本内安全获得资格，坦诚停止并及早找 Robert，而不是让安全执行器成为新的论文课题。



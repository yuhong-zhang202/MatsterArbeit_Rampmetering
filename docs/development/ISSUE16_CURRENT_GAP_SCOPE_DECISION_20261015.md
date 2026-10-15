# Issue16：650秒间距硬停止的适用性判定

**本轮有界收口：STOP_RETAINED / NOT_QUALIFIED。** 获批最小合同已实现并完成离线审查；唯一新自然运行run02在1262秒触发保留的制动硬门。未取得有限运行资格，不改门、不自动重跑。下面T1、准备和批准内容保留其版本；实际结果见末节。

**T1结论：MINIMAL_SCOPE_CHANGE_PROPOSED；用户现已批准四条合同及最小离线实现。** 直接答复为“批准该合同及最小离线实现”，见[非执行批准回执](../../artifacts/issue16_natural_gap_scope_20261015_v1/HUMAN_CONTRACT_APPROVAL_RECEIPT_V1.json)。最小实现及工程→数据→科学离线审查已完成，GO仅支持离线交付与非执行新卡准备；新SUMO运行未授权，仍须准确新卡单独放行。旧650 STOP保持。

## 任务与版本

[Issue16](https://github.com/yuhong-zhang202/MatsterArbeit_Rampmetering/issues/16)要求一次有界根因调查、至多一次必要局部修复及一次获授权的自然复验。开始时GitHub PR15与本地均为 `af988faddaa271ac2a8f80fe3fd3558ff2898618`；新分支 `codex/issue-16-natural-gap-scope` 从该精确提交建立，后续Draft PR以 `codex/natural-actuator-qualification` 为base。PR13仍为61612bf，末轮REVIEW_PENDING / NO_VERDICT，不重复触发。未改上游分支或重用旧运行身份。

主代理完整读取Issue16/14/12和PR15/13正文及可见评论/审查、AGENTS、DECISIONS、七项资格方案、问题索引和相关三方回执。PROJECT_STATE470行与WORKLOG3054行由三代理分段完整阅读并回报历史冲突，相关长输出截断处补读。旧Stage6状态及旧恢复授权不能覆盖D018、当前Issue16和已消费的单次启动许可；无关memory ledger与WORKLOG插入保留。正式协议仍0B/未冻结。

首次自然run01的650 STOP、原reader exit1/UNKNOWN、车尾截断、六窗未测和NOT_QUALIFIED均不改判。173执行源及卡b73保留。独立900预算已耗83.637436041、余816.362563959秒，但唯一启动权已消费；余额不批准新启动。[首次收口](NATURAL_ACTUATOR_FIRST_NATIVE_CLOSEOUT_20261015.md)。

## 科研定位与完成边界

执行器服务于可信的交通效果实验，不重开A1完备预测证明，不改ALINEA核心、模型、路网、输入或黄红配时。直接实测、固定官方源码、工程推断和未验证项分别记录。只有经过科学审查且用户明确批准的安全合同才能实施；新精确卡/预算/三方/canonical仍是后续独立门。

论文整体阶段判断：场景探索已依D018结项，当前卡在正式实验前执行器资格；正式设计尚未冻结，正式结果与论文章节完成率缺少可核证据，因此不编百分比或毕业日期。后续资格即使通过，也只支持固定自然条件的预实验用途。

## 根因及唯一合同提案

实测确认：R1在PRE649已经低于相同的参考间距；R0跨入内部连接后，R1成为储存段首车，POST650检查才硬停。固定SUMO1.26源码中，getSecureGap按当前速度计算参考，而普通Krauss跟驰按当时条件计算下一步速度；未找到必须在运动后满足该参考不等式的原生要求。**旧合同确实被触发；尚未证明实际危险，也未证明误报。** 两帧把前车制动参数9改为4.5均不会改变查询，不能这样造PASS。[工程源码与实测判定](../../artifacts/issue16_natural_gap_scope_20261015_v1/engineering/T1_MECHANISM_AND_SCOPE_REPORT_V1.md)、[科学终审](../../artifacts/issue16_natural_gap_scope_20261015_v1/SCIENCE_T1_REVIEW_V1.md)。

下列四项合同已经用户明确批准，仅允许最小实现和离线验证：

1. **每次新G严格准入保持。** fresh完整观测、原prospective接收/空间检查不变；已知不足保持实际红灯，必要观测未知停止。不改配时、模型或接收布尔值。
2. **普通被动跟驰查询统一改为观测责任。** 在有效既有信号计划、无车辆速度/安全模式/车型setter、前后车与路径/距离完整绑定、query有限且实际gap非负时，ongoing PRE、POSTreceiver及实际entry前后快照中的参考不足单独保留为BELOW_NATIVE_REFERENCE_OBSERVED，不再仅凭该值停止。查询参数、数值和旧失败字段仍保留；这不是接收容量或安全通过证明。
3. **真实异常和必要观测UNKNOWN仍停止。** 碰撞/teleport、既有超过4.5m/s²制动、红灯新入口、负gap/重叠、相位/ACK/身份/车尾/路径/日志异常保持硬停。黄灯责任沿既有已批诊断合同，不扩大证明。
4. **只限科研技术诊断责任。** 旧STOP/FAIL/UNKNOWN/raw不改；未来仍需新合同实现/reader精确绑定、单独新卡批准、真实剩余预算及canonical。未记录的native私有分支和未来动作是限制，不另建A1完整预测器。

科学审查未发现阻碍提交此提案的新Blocker/Major；这不等于新执行器安全或资格通过。用户现已接受上述责任边界；若后续仍有无法消除的实质安全或科研阻塞，应停止本路线追加调试，交Robert讨论更简单的原生信号操作路线。

## 运行前资格口径（建议，未冻结）

账目、唯一N、指令应用和partial/pending采用精确复算；表示误差沿既有输出精度，跨界不确定保留UNKNOWN。六窗全部保留，不能删除空/受限窗。C−E_scheduled的调度误差与实际E_executed−N分开；不能宣称动态误差始终≤1/8辆。现有文献不支持通用5%/10%实际服务阈值，不强求供给不足时C=N，也不免除未解释持续短放。若需要数值物理服务门，必须在新运行前以用途/可评条件论证并审定；不能跑后挑阈值。整个4200秒、六窗、完整人口/安全/实际服务审查仍是后续资格门，不能由本次提案代替。

## 获批合同的离线实现

自然版本新增被动参考分类模块，接入PRE/POST/实际entry前后；新G仍严格准入，原query/legacy失败保持，真实硬异常独立停止。policy、producer、bridge和旧receiver字节未变。工程3方法首轮PASS2.976秒；独立data加强字段核对后3方法PASS0.068秒，再仅受影响pending/held方法PASS0.067秒。26项工程、35项data、8项静态绑定获科学只读核对，无未处理Blocker/Major；这不是最终全套重跑或原生验证。[科学终审](../../artifacts/issue16_natural_gap_scope_20261015_v1/SCIENCE_IMPLEMENTATION_REVIEW_V1.md)。保存fixture缺REQUESTED/feedback/command_records，完整生命周期仍未测。

独立run02已唯一prepare/validate成功（exit0，各1.675902417/1.410167541秒）。准确卡SHA `dc9c1ce418ab61eb4e36b26e1436c94b31ba78cde9a630df596a0e5a4ce4c509`，176源摘要 `4eb466ec0a28f783089230941f1a6139ce9f0ed45a0e0dced82a7dc1e278d66f`；工程199/data20最终绑定获科学复核，GO仅交人审。卡拟使用原900账剩余中的总816秒（worker786+清理30），不重置已耗83.637436041及start1。卡execution=false/观测null，无新raw/guardian/canonical/启动权。准确卡及有限用途仍须用户确认。[唯一运行请求](../../artifacts/issue16_natural_gap_scope_20261015_v1/RUN02_REQUEST_V1.md)、[精确卡科学复核](../../artifacts/issue16_natural_gap_scope_20261015_v1/SCIENCE_EXACT_CARD_REVIEW_V1.md)。公开推送72a2e61时被自动审批拒绝，要求具体发布范围的人类批准；当前仅本地交付，待最终文件范围固定后统一提交批准请求。

## 已完成的失败前缀读取修复

独立reader修复、工程静态复核和科学终审均仅支持失败前缀交付。4方法/17拒绝变体通过（0.567秒）；最终V3对同一旧raw只读审计exit1，完整时域未到仍UNKNOWN，qualified=false。精确终止原因、ACK及query绑定下分别解释worker1与nativeEOF0；原间距告警、650 STOP、partial、六窗null和车尾截断全部保留。新到达的endpoint重复ID异常已窄修，第一次失败和源重建限制保留。显式后分析模式区分173执行快照与15项当前reader闭包，不向旧卡写入新源码。[reader报告](../../data/processed/issue16_natural_gap_scope_20261015_v1/reader_fix_v1/READER_FIX_REPORT_V1.md)、[科学复核](../../artifacts/issue16_natural_gap_scope_20261015_v1/SCIENCE_READER_REVIEW_V1.md)。

新合同后的运行/测量资格与数值跟踪精度应分开：前者仍需完整4200秒和七域实际证据；后者没有获批数值容差，建议NOT_ASSESSED。该用途限定仍是待用户随准确新卡确认的方法建议，不能偷换成完整ALINEA服务准确资格。[预声明口径建议](../../artifacts/issue16_natural_gap_scope_20261015_v1/SCIENCE_PREDECLARED_CRITERIA_PROPOSAL_V1.md)。

## 证据入口

- [有限原始证据与角色/时点核查](../../data/processed/issue16_natural_gap_scope_20261015_v1/DATA_T0_T1_REPORT_V1.md)
- [reader最小修复计划](../../data/processed/issue16_natural_gap_scope_20261015_v1/READER_MINIMAL_PLAN_V1.md)
- 固定官方SUMO v1_26_0 commit `fa7df22d7f1c4ae245192ecc32410a49f1ffb2a3`；源码索引与本地缓存位于 `artifacts/issue16_natural_gap_scope_20261015_v1/engineering/`，完整第三方源码不重复公开导入PR。

## 模型建议

建议复杂根因与科学边界判定使用GPT-6 Astra；常规局部实现可用GPT-6.1 Sol。官方将Astra定位于复杂推理/编码、Sol定位于能力与成本平衡；这是任务选择建议，不是正确性保证，也未改变本聊天或代理设置。[OpenAI模型说明](https://developers.openai.com/api/docs/models)（2026-10-15实际检索并打开）。

## 唯一自然复验与科学收口

用户明确批准公开101文件及准确run02一次启动/限定用途后，已发布[Draft PR17](https://github.com/yuhong-zhang202/MatsterArbeit_Rampmetering/pull/17)，执行checkpoint `daa149bd296e1ab24da82b47b03f33d7d3e6904a`。新真实canonical及全部来源/输入/环境/三方/PID/磁盘/预算门通过；一次native连接25.135秒后开始运动。没有第二次启动或源码修改。

**1262秒STOP。** R_flow.109在1261→1262黄灯步的速度差和加速度getter均为−4.501m/s²，超过原4.5+1e−6门；原两条制动告警保持。碰撞/teleport观测0，不能据此判数值误报或未来安全，也不能仅凭微小超额证明实际危险。原650 gapSTOP不改判，新版越过650是本次过程证据。[实际工程报告](../../artifacts/issue16_natural_gap_scope_20261015_v1/engineering/run02_execution_v1/ENGINEERING_EXECUTION_REPORT_V1.md)。

独立[600,1262)662秒：C≈133.174013、E_scheduled=E_executed132、N109，描述平均592.749辆/小时；C−N≈24.174013全部保留，不能把物理缺额追到调度账。66完整周期和末partial、1260请求pending、22完整反馈窗口获核对。第一评价窗仅62/300秒，其余五窗null；下游完整边界红保持恢复未测，供给/receiver/WAIT重叠不能唯一解释23辆名义与实际差额。全4050人口=1462到达+157未完+2431future，截断不当零。[独立数据报告](../../data/processed/issue16_natural_gap_scope_20261015_v1/run02_native_v1/DATA_RUN02_REPORT_V1.md)。

原reader唯一exit1/UNKNOWN：反馈尾部及EOF两个UNBOUND_GAP_STOP_RECEIPT保留，未扩豁免造PASS。补充独立完整反馈前缀、nativeEOF0/四流绑定/清组为空是另列的事实，不替代原UNKNOWN域。231raw文件/402,556,357字节封存，manifest207f7183；工程19/data27/全部raw经只读科学核对一致。[最终科学审查](../../artifacts/issue16_natural_gap_scope_20261015_v1/SCIENCE_RUN02_POSTREVIEW_V1.md)。

状态边界：离线TECHNICAL_PASS仅对应已述测试；此次实际NOT_QUALIFIED，LIMITED_QUALIFIED未取得；完整4200/完整六窗/真实边界受限恢复NOT_TESTED，数值跟踪精度NOT_ASSESSED。正式实验未启动，论文仍卡在正式实验前执行器资格，不能给无依据完成百分比。

唯一建议：把本次−4.501事件及既有数值事件历史交用户/Robert，一次性裁定“逐步绝对4.5制动门”是否适合论文资格标准。此前保持停止与未资格，不继续自动修改guard/新增预测系统/测试矩阵或重跑；未向Robert发消息。

真实资源结算已回读通过：本次guardian含清理175.236358000秒（CLI179.816117125秒为不同范围），累计258.873794041秒，余641.126205959秒，start2/unknown预留空；旧账/预算不pool或reset。余额不授予第三次启动。[最终资源摘要](../../artifacts/issue16_natural_gap_scope_20261015_v1/RUN02_RESOURCE_ACCOUNT_FINAL_V1.json)。

# GPT sol：Stage 6 暂停点与逐步执行交接

日期：2026-10-02。

**2026-10-03当前交接：探索验证COMPLETE_WITH_LIMITATIONS，正式实验方案设计待开展。** 旧城市能力证据转用及独立科学验收已完成；详见[限定用途结项](STAGE6_EXPLORATORY_CAPABILITY_CLOSEOUT_20261003.md)。ALINEA/控制收益不是探索验收前提。下方控制实现/参数仅为后续设计候选，需重新审核及适用授权，不能自动执行。
项目根目录：`/Users/yuhongzhang/Desktop/Masterarbeit-Ramp-Metering`。

## 0. 接手时首先遵守的边界

**当前已按用户要求暂停。读取本文件不等于恢复仿真授权。** 用户明确要求继续后，按下面顺序推进；如果只是要求讨论或读文档，保持只读。最新授权为证据适用性核对、重新结项及相关文档/Dashboard同步，不是启动控制实验。

本次18个无控运行已经完成，全部卡片已消费，无待执行卡片。场景能力探索整体已限定结项；正式方案设计待开展。ALINEA尚未编写、未准备运行卡、未执行。正式`docs/EXPERIMENT_PROTOCOL.md`仍为空、未冻结。不要把本方案中的Proposed参数或科研建议记为用户逐项批准、导师确认或正式冻结。

## 1. 最小必读顺序

先读`STAGE6_EXPLORATORY_CAPABILITY_CLOSEOUT_20261003.md`与DECISIONS D-012，再读以下历史结果/设计候选。

1. `AGENTS.md`，尤其分工、科研输入和正式协议边界。
2. `docs/PROJECT_STATE.md`顶部最新状态、本目录`STAGE6_BOUNDARY_SEARCH_20261002_REPORT.md`。
3. `docs/WORKLOG.md`最后2026-10-02条目；`docs/DECISIONS.md`只用于分辨历史批准范围。
4. `docs/supervision/2026-09-30_robert_hilbrich_reply.md`与`docs/SUPERVISOR_FEEDBACK.md`相关原文。不要把聊天转述替代邮件。
5. `artifacts/stage6_boundary_search_20261002_v1/PLAN.md`、`REVIEW_BATCH01.md`至`REVIEW_BATCH05.md`、`BATCH05_ENGINEERING.md`。
6. `results/tables/stage6_boundary_search_20261002_v1/batch05_seed_neighborhood/`中的`batch_summary.csv`、`seed_summary.csv`、`handoff_data_index.json`、`queue_summary.csv`、`pre600_comparison.json`。
7. 查看同名`results/figures/.../batch05_seed_neighborhood/speed_mps.png`和`model_reference_ratio.png`，并按问题读取原始证据。无需先扫全仓库或重跑18组。

MemoryCore只是辅助；仓库原始证据优先。需要记忆时使用项目既有`node scripts/memory/read_formal_memory.mjs --full`。记忆服务故障不应推翻可直接读取的实验结果，也不要借此自动改系统服务。本次不写付费记忆。

## 2. 已回答的问题与可选运行点

现网络两条高速主线+独立294.51m辅助车道，随后恢复两条主线。在已测范围内没有必须先重建网络的证据。高需求主线入口等待必须按时序区分：若Merge队列先向上游发展再到入口，它是拥堵后果，不是自动判实验失效。

已测M3600、R750–900之间有从短局部扰动到严重上游回堵的转换区间，三种子17/23/42复核支持。R900的P支持秒1800/1560/1800、S1800/1500/1800；R750的P240/90/0且S全0；R600的P0/90/0且S全0。不能把这些x/3称为精确breakdown概率。M3600/R900的R/U无源头延误，比R1200城市供给受限点更适合首轮控制。

**当前城市OPEN补充：** 已读三组seed17 M3600/R1200、M3000/R1200、M3600/R900的既存FCD/TLS，均无shared R/U历史阈值慢停或E2 jam；R1200的源等待/urban_in成本不能称shared spillback。不要为复现旧B22限流队列机械补跑旧M3350.4/R900 OPEN。见结项报告的追加核查与原始绑定报告。

**后续优先候选：M3600/R900，seeds17/23/42。** 已有无控baseline可直接复用。R750作为较轻边缘参考，R600/R0作为相对畅通参照，不自动都扩成控制矩阵。不要再跑旧2×3网格，也不自动增加71/101、4800/1800或更小需求步长。只有某个新实验能改变明确未决判断时才考虑它。

边界只适用于当前合成模型、随机实现与有限加载期；不是普适容量值。严格数值onset门槛与空间机制证据分开。原始RI3350、后续重建固定配时、本次新搜索三套历史分开保留。

## 3. 可复用输入、数据和代码

- 网络：`artifacts/stage6_baseline_localization_20260921_v1/LOC_M3350_S17/engineering/build_attempts/TV_BUILD01/network.net.xml`。
- 每组输入：`artifacts/stage6_boundary_search_20261002_v1/inputs/<RUN_ID>/`，包含demand、additional、sumocfg、card。
- 无控候选ID：`M3600_R900_S17`、`M3600_R900_S23`、`M3600_R900_S42`；卡片哈希和解析索引见`handoff_data_index.json`，不要手抄旧哈希替代现查。
- 原始输出：`data/raw/stage6_boundary_search_20261002_v1/<RUN_ID>/outputs/`。每组execution_receipt绑定所有输出哈希；原始目录只读。
- 解析结果：`data/processed/stage6_boundary_search_20261002_v1/<RUN_ID>/`。
- 脚本：`scripts/stage6/boundary_search_20261002/{runner.py,analyze.py,summarize.py}`。
- 分析配置：`artifacts/stage6_boundary_search_20261002_v1/analysis_config.json`。
- SUMO1.26.0：`/Library/Frameworks/EclipseSUMO.framework/Versions/1.26.0/EclipseSUMO/bin/sumo`；CPython3.13.0、TraCI1.26.0、sumoITScontrol0.1.0。精确版本/哈希以card为准。

固定输入：M/U/X请求[0,3000)，R[600,3000)，观察4200，评价[1200,3000)，步长1s；U/X360/180veh/h。M使用best/max/100，其他best/max/last；城市TLS45G/3y/9G/3y；默认随机驾驶保留。逐车speedFactor已显式固定，匹配控制应直接复制同seed的完整demand XML，不重新抽样。

已消费18次启动，0失败/重试，原始数据197,935,338B。原计划总上限40次（无控最多32、控制/技术最多8），120s/次、250MB/次、原始总8GB。**余额不是自动启动许可，也不得换runner后重置计数。** 不删除reservations，不复用消费过的card，不覆盖历史输出。

## 4. 步骤A：接手核对与分工（先只读）

**产出：一页接手核对记录。** 确认用户确已恢复后续工作；核对git现有修改，保留他人内容。核对18张已消费卡、18个COMPLETED回执、18个解析summary、无执行锁、正式协议状态。无需重复解析所有大文件；优先检查索引哈希和候选三组关键源。

必需分工：simulation_engineer负责控制实现/输入卡/运行；data_analyst负责放行账、群体成本和数据处理；scientific_reviewer只读审查设计与结论。各自先做项目Context Preflight；写文件责任不重叠。

已有无仿真测试可使用：

```bash
.venv/bin/python -m unittest discover -s tests -p 'test_boundary_search_*.py'
```

仅在代码/环境发生变化或需恢复测试证据时重跑。不要为了“准备好”而重新执行SUMO baseline。

## 5. 步骤B：正式阶段设计中的前瞻控制候选与独立审查

**问题：在相同M3600/R900需求下，标准占有率反馈能否减少持续主线拥堵，代价是否转移到匝道/城市？** 不预设一定有效或存在sweet spot。

先写独立`CONTROL_PLAN_V1.md`（建议新artifact子目录），明确以下候选。当前均为**Proposed，未执行、未冻结**：

| 项目 | 首轮候选 | 依据/审查点 |
|---|---|---|
| 策略 | 基础ALINEA，首轮无queue override | 先识别基础保护与成本，再决定是否有必要加队列约束 |
| 点/种子 | M3600/R900，17/23/42 | 复用已有严重状态baseline；已暴露设计/技术比较种子，不是未见过的正式验证种子 |
| 反馈位置 | main_down上20m，两条主线E1 | 占有率为两lane算术均值，百分比单位 |
| 更新 | 每30s一次，上一个完整区间 | 与原E1周期对齐，不取未完成区间、不使用未来数据 |
| 占有率目标 | 11% | S17 R600无P工作点约10.997%；R750三seed约11.59–11.77%，R900约13.66–14.51%；并非已估计critical occupancy |
| 增益 | 70 veh/h/百分点 | 明确工程初值及单位；不是本场景已校准最优值 |
| 请求放行率 | 初始900，下限300，上限1200 veh/h | 检查执行器实际服务能力与积分饱和，不等同实际放行 |
| 控制时段 | 600s开始，建议持续至观察终点4200s | 不以后验拥堵发生时刻触发；不要3000s突然全绿把代价藏到清空期 |
| 信号执行 | 候选1s绿脉冲+红间隔，最小红及相位连续规则须锁定 | 一次绿不自动等于一辆车，必须验证实际过线 |

计算式（占有率以百分数输入，例如11.0）：

`r_next = clip(r_prev + 70 * (11.0 - occupancy_pct), 300, 1200)`

若使用0–1占有率，增益也必须相应换算；不能直接以0.11减比例再乘70。写清首个反馈更新时间、初始化、截断后用于下一步的状态以及积分饱和处理。目标来源数据为已暴露探索校准，不能用同一target同时定义拥堵和证明控制成功。外部方法依据：[FHWA ALINEA说明](https://ops.fhwa.dot.gov/publications/fhwahop14020/sec1.htm)；本项目数值需独立审查，不能称导师指定。

**通过条件：** reviewer接受问题、匹配、时序、测量、参数单位和资源安排；工程确认信号语义可实现。未通过只修设计，不启动。不能把本文件自动转换为已批准运行卡。

## 6. 步骤C：实现并验证执行器

现有`runner.py`只支持OPEN，已被18张历史卡哈希绑定。**不要直接修改它后强行复用历史卡。** 建议新增`control_runner.py`及对应测试，复用安全/预算逻辑但保持原文件和原始输出。

已知阻断：sumoITScontrol0.1.0原ALINEA假设第一个TLS程序有G/r两相位，并用绿占比单位；当前首程序A_OPEN只有G，旧B_MODERATE为G/y/r。直接调用stock方法不构成已验证标准ALINEA。优先实现小型透明TraCI适配器：veh/h反馈律与信号执行层分开。

必须验证：

1. 同seed需求字节完全相同；network、路线、行为、城市信号和时间窗相同，只改变ramp控制。TraCI驱动循环不引入多走/少走一步。
2. 采用`h=3600/r`等价的相位连续或累计误差调度处理1s量化；不能每30s重置绿灯产生额外放行，也不能把小数headway一律取整。
3. 无车时不无限积累放行额度；绿灯宽度、最小红、是否黄灯、更新时跨周期处理在运行前写死。
4. 检查启动损失、同一绿脉冲零/一/多车、红灯通行和紧急制动。若“一车一绿”实际不成立，如实标出并暂停解释，不能把命令率当实测率。
5. 每30s日志保存两lane原占有率、均值、target、未截断/截断rate；每秒保存命令/实际信号；逐车保存穿过ramp_mid信号边界的时间与ID。信号边界过线、进入merge边、实际换道、下游通过是四件不同的事。
6. 继承全局启动预算、一次性卡、资源监控、全部失败保留、无自动重试。新输出须与现分析器接口兼容，额外控制日志也进入哈希manifest。

先做纯逻辑单元/静态核对。若TraCI时序的无干预一致性仍不能确认，可前瞻登记最多1个全绿技术对照，与已存baseline比FCD；它回答runner是否改变仿真，不是新的容量实验。随后先执行一个已锁定控制方案的seed17技术/探索运行，验收实际信号与放行。技术/校准pilot与正式运行资格须事先定义，不能事后挑好结果转正；正式运行要求协议冻结。技术失败保留，先找原因；不能自动改参数让结果好看。

## 7. 步骤D：最小控制比较

技术与科学审查通过、当前用户授权有效后，生成全新run ID与输入card，记录父baseline哈希、控制代码/参数、网络/需求/软件版本。由审查后的精确release启动。旧OPEN runner的CLI只有prepare/preflight/launch；**当前没有可直接执行的ALINEA命令**，下一位必须先完成步骤C，不能猜命令。

顺序：seed17先完整核查，再seed23/42。对照使用现有同seed OPEN，不机械重跑。保留全R900请求需求，不把控制组R请求改成600冒充metering。前三个控制case就能回答首轮可行性，不默认扩到R600/750/1200或扫多target/K。

通过每组后按`analyze.py`同公式输出新目录，不能覆盖旧processed：

```bash
.venv/bin/python scripts/stage6/boundary_search_20261002/analyze.py \
  --card NEW_CONTROL_CARD_PATH \
  --config artifacts/stage6_boundary_search_20261002_v1/analysis_config.json \
  --out NEW_PROCESSED_DIRECTORY
```

上面路径占位符须用新实现真实产物替换；只有新card/output兼容且技术审查通过才执行。

## 8. 步骤E：必须同时回答的结果账

- **M保护：** 每seed P/L/S并集时长、主线速度/密度空间结构、上游队列范围、M全请求群体计划出发至到达时间、实际下游完成量。不要把FCD每秒/车辆当独立重复。
- **R服务与队列：** 请求、实际插入、到信号、实际放行、到merge、实际换道；累计到达减放行；3000s和4200s未服务/未完成；最大队列和持续时间。反复跨边界不能重复计入。
- **城市成本：** R/U/X全群体成本与源头等待，shared approach及内部连接停车/慢行。内部`:urban_diverge_1_0`长113.08m，不能只用ramp_storage的E2说没有spillback。空间连通的排队达到共享路段才是回溢证据，零星停车不能直接替代它。
- **系统：** 所有请求车辆的外部等待+网络内时间总和，matched policy difference；若4200s仍未完成，保留限制时间成本和数量，不能只比较完成者均值。
- **清空期：** 与加载期分开；不能在清空时放完车辆后声称加载时没有积压，也不能把空路当速度恢复。

各seed先列原值和配对差，再给范围/描述性均值。n=3不支持精确成功概率或充分统计功效。一个策略让M改善但R/U显著变差也是有效结论。

## 9. 后续控制研究的条件分支与停止（不是探索验收门）

A. **M改善且无明显队列/城市代价：** 先确认不是少放车、截断或未完成造成的假收益。若三seed一致，可作为候选保护区间；仍不能从一个点/一套参数宣称全局最优sweet spot。

B. **M改善但R排队/城市成本明显：** 如需回答“能否避免回溢同时保护M”，才前瞻设计一套queue override，与基础ALINEA对比。阈值必须依据物理存储/排队测量，先审后跑；不要盲扫阈值。若只是将R900长期压成R600，2400s内净积压约200辆，不能称稳定sweet spot。

C. **没有M改善：** 先检查反馈位置/单位、实际放行、信号执行、到达团簇及拥堵状态；技术正确仍无收益就如实报告。不能立刻连改target/K/geometry/sigma追求正例。

D. **技术或测量失败：** 暂停后续case，保留失败和已消耗预算，修复后另行版本与release；不默默丢弃。

探索已依据技术完整性、主线临界状态、城市受阻能力及机制不变性核对结项。后续控制收益/城市代价/sweetspot应在正式设计及适用批准的技术pilot或正式实验中回答，不重新设为探索结束门。研究结果可以是没有发现可行sweetspot。

**当前决定：探索COMPLETE_WITH_LIMITATIONS；正式设计待开展；所有新仿真仍暂停/未授权。** 不继续追加无控点或重复城市能力运行。

## 10. 正式实验的准确交接

探索已结项。下一位先交付正式实验设计与`FORMAL_PROTOCOL_DRAFT`供审查，不等待控制先取得成功，也不直接正式运行。至少逐项固定：

1. 研究问题、模型版本与可外推范围，是否研究缓解持续拥堵或避免崩溃、权衡目标如何定义。
2. 场景与需求时间结构、背景流、热身/评价/清空窗口、源边界和实际交付处理。
3. 冻结控制算法、执行器、检测器、目标/增益/边界、queue override定义；固定待比较集合。
4. 状态判据及独立校准/验证；当前P/L/S与严格FREE/onset的局限应处理，不能用控制target循环自证。
5. 正式独立seeds/重复数与精度或功效依据；17/23/42为已暴露探索数据。事先制定失败、删失、异常和非单调结果处理。
6. 完整M/R/U/X/系统指标、效应方向/可接受代价及配对分析，不能事后改成功标准。
7. 环境/输入快照、哈希、run ID、预算、安全停止和复现实验流程。
8. scientific_reviewer独立通过；用户明确批准并冻结`docs/EXPERIMENT_PROTOCOL.md`后才可正式运行。导师指导不自动等于用户批准。

每个实质节点更新PROJECT_STATE与WORKLOG；仅有新明确导师反馈才更新SUPERVISOR_FEEDBACK；只有用户批准决定状态才改DECISIONS。禁止覆盖历史、静默排除失败或改AGENTS。

## 11. 给 GPT sol 的恢复提示词

> 请读取限定用途结项报告、本文件及最小必读来源。我现在授权开始正式实验方案设计，不授权仿真。复用18组无控与有效旧城市能力证据；保持各系列范围，不扩无控网格，不为探索结项先跑ALINEA。先由simulation_engineer、data_analyst、scientific_reviewer审查控制执行器/测量、匹配条件、全群体M/R/U/X成本、独立种子与精度、失败和停止规则。所有数值保持Proposed；输出可审阅正式设计与协议草案。若确需技术或校准pilot，明确它回答的问题与有界运行卡后单独提交，不自动启动。正式协议经明确批准冻结后才可执行正式实验，不强求sweetspot。

上段仅供用户未来主动发送；本文件自身不触发执行。最新外部Notion/Space未在本轮同步，若接手方只看旧页面，应先获取本报告及本交接正文。

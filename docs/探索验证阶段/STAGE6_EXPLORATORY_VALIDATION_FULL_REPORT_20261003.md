# 探索验证阶段完整报告：指标、操作、数据与结项判定

**截至日期：**2026-10-03（Europe/Rome）
**性质：**合成 SUMO 场景的探索验证复盘；不是正式实验结果或现实交通校准。
**最终状态：**依据 D-018，Stage 6 为 `completed / preliminary_ready`，下一步仅为**正式实验方案设计**。[当前状态](../PROJECT_STATE.md)、[结项决定](../DECISIONS.md)、[精确交接](STAGE6_EXPLORATORY_CLOSEOUT_AND_FORMAL_HANDOFF_20261003.md)。正式实验协议仍为空、未冻结。

## 1. 验证问题与判定口径

用户对本阶段的核心要求是：在大规模正式实验之前，确认这个仿真场景能够产生论文要研究的**主线临界拥堵、匝道积压和城市道路受影响**等现象，并排查已知建模错误。验证不是保证任意需求下都出现完整 A→B→C，也不能证明模型绝无错误或与真实道路相符。[早期完成标准 §0、§4](EXPLORATORY_VALIDATION_COMPLETION_PLAN.md)。

早期标准分三层：O1–O6 检查**工作产物是否齐全**，G01–G08 检查**来源和分析过程是否可核**，Q1–Q4 判断**场景能否支持研究用途**。O/G 通过不自动使 Q 通过；`completed / preliminary_ready` 还要求核心用途无未解关键缺口、独立复核和用户接受。早期计划明确写明：探索阶段**不要求** ALINEA 有效、找到 sweet spot 或完整需求曲线。[原标准 §3–4.2](EXPLORATORY_VALIDATION_COMPLETION_PLAN.md)。

Robert 于 2026-09-30 建议先核对两条主线加独立加速车道、lane-to-lane 连接与实际车辆插入，再扫描无控 `qMain × qRamp`，从临界区选择运行点比较控制；他不建议当前用 22/28 秒固定配时刻意构造 A/B/C。[导师反馈记录](../SUPERVISOR_FEEDBACK.md)。用户随后明确拒绝只用旧城市证据与新无控证据拼接的“有限范围结项”，要求**同一当前版本**的标准匝道控制比较，之后依证据决定结项。这是 D-013–D-018 的补充验收范围，不能倒写成 2026-09-09 原计划已有 ALINEA 必达门槛，更不是 Robert 批准了具体控制参数。[决策记录](../DECISIONS.md)。

本报告把“已观察事实”“有界解释”“未证实事项”分开。下文“支持”均指所述合成网络、需求、时域与种子内的**探索用途**；不等于正式统计推断。

## 2. 实验系列与操作经过

| 阶段与目的 | 实际操作和状态 | 能作为本次主要证据的范围 |
|---|---|---|
| Stage 1–5 早期场景与评估 | 场景、观测合同、八条归档运行的诊断、qMain=3500/3650 的两个种子定点验证、敏感性及方法交接完成。早期 Stage 5 判断为 `specific_obstacle`：当时 Q1/Q3 在限定范围内支持，Q2/Q4 未识别；T54 用户接受另列待定。[早期总结](EXPLORATORY_VALIDATION_REPORT.md)、[独立更正](STAGE3_STAGE5_ASTRA_REVIEW_20260913.md)。 | 历史方法和障碍线索。不能把早期 Q2/Q4 改写为已通过，亦不能把早期归档当当前版本三种子重复。 |
| 原始 RI3350 R0/A | R0 请求动态 `best/max/last` 出发规则，A 使用从 R0 输出复制的数值车道/位置/速度；A 的 U 车 57/150 未插入，前匝道时段已有 M/U/X 不匹配，M FCD 在 t12 分歧，故 `NOT_PAIRABLE`、A `A_NOT_EVALUABLE`。[原始配对纠正](../../artifacts/stage6_full_network_abc_phenomenon_validation_plan_20260926_v1/A_launch_package/PAIRABILITY_REAUDIT_CORRECTION_20260926.md)。 | 故障诊断；**不可**用于 A 对 M 的有效配对效果。 |
| 后续重建 V2 A/B22/B28 | Seed17、2700 s；重建网络在 A/B22/B28 各 240 辆 R 全部完成并从独立加速车道换入主线。B22 的 M 核心速度 A→B22 为 26.964→26.572 m/s、M平均行程+0.266s，R/U 平均网内时间+153.821/+26.473s，共享 U 慢行987车辆秒；B28 M核心速度26.964→25.376m/s、平均行程+0.721s。两者均未显示主线保护；旧默认模型的早期远处 M 轨迹分歧限制物理归因。[旧科学判定](../../artifacts/stage6_exploratory_closeout_20260926_v1/STAGE6_EXPLORATORY_DISPOSITION.md)、[B22](../../artifacts/stage6_full_network_abc_matched_rebuild_20260926_v1/B_SCIENTIFIC_OUTCOME_REVIEW.md)、[B28](../../artifacts/stage6_moderate_rebalance_20260926_v1/B28_SCIENTIFIC_OUTCOME_REVIEW.md)。 | 保留为旧设置的城市现象和方法诊断。固定配时车团机制仅是待检验解释；不能并入当前 OPEN/V15 配对效果。 |
| 当前版本无控需求探索 | 相同编译网络与城市信号，显式逐车速度因子；M/U/X 在 `[0,3000)` 请求，R 在 `[600,3000)`，观察到 4200 s，主评价 `[1200,3000)`。先沿 M、R 方向找状态，再在 M3600 的 R0/600/750/900 使用 seeds17/23/42 复核。**18 个唯一运行、18 完成、0 失败、0 重试**；跨批表中重复出现的是复用运行，不是额外启动。[预先计划](../../artifacts/stage6_boundary_search_20261002_v1/PLAN.md)、[批次报告](STAGE6_BOUNDARY_SEARCH_20261002_REPORT.md)、[最终三种子邻域表](../../results/tables/stage6_boundary_search_20261002_v1/batch05_seed_neighborhood/batch_summary.csv)。 | 当前版本临界状态与 OPEN 基线；未给出精确二维容量曲线。 |
| 当前版本控制比较准备与技术修复 | 用已有 OPEN 做同种子基线；先验证 TraCI 全绿无干预与 OPEN 等价，修复检测器占有率重构，再试控制。V8 初次 S17 有不安全绿转红急刹，V9 安全但持续排队下实际 564 veh/h 跟不上约 1071 veh/h 指令。重新审查单车放行执行器，固定 V15 前瞻规则；V12–V14 技术失败均保留，不作控制效果。[原执行计划](STAGE6_CURRENT_VERSION_STANDARD_METERING_PLAN_20261003.md)、[V15 设计记录](STAGE6_SAFE_ACTUATOR_EXPLORATORY_DESIGN_20261003.md)、[工作日志](../WORKLOG.md)。 | 技术资格与失败机制。失败试验不被静默删除或当成策略阴性。 |
| V15 三种子配对 | M3600/R900，U360/X180 veh/h；seeds17/23/42 的 OPEN 对 V15，当前网络、逐车需求、城市信号、时间结构相同。占有率反馈每 30 s 更新，目标 11%、增益 70 veh/h/百分点，速率限幅 300–900 veh/h、初始 900；1 s 单车绿灯、至少 2 s 红灯，保守前车/跟车检查和绿后立即转红安全检查。先 S17 技术验证，合格后顺序完成 S23、S42；未做事后参数扫。[V15 设计](STAGE6_SAFE_ACTUATOR_EXPLORATORY_DESIGN_20261003.md)、[S17](../../data/processed/stage6_safe_actuator_v15_audit_20261003_v1/S17_GATE_REVIEW.md)、[S23](../../data/processed/stage6_safe_actuator_s23_v15_audit_20261003_v1/S23_GATE_REVIEW.md)、[S42](../../data/processed/stage6_safe_actuator_s42_v15_audit_20261003_v1/S42_GATE_REVIEW.md)。 | 当前版本三组有效探索配对；不是独立的正式确认样本。 |

### 2.1 早期 Stage 2–5 的实际运行与诊断

Stage 2 固定 U360、X180 veh/h，需求期 `[0,1500)`、清空至2700s；四种无控条件各 seeds17/23。C17 复用已有运行，另七条实际启动、七条完成、0重试，八条最终车辆均到达。下表斜线依次为 seed17/23；R 是 **1500s 前第一次在下游被 FCD 观察到的车辆数**，不等于精确断面流量。[Stage 2 完整运行台账和原表](STAGE2_COMPLETION_REPORT.md)。

| 条件 qMain/qRamp (veh/h) | M 内部 E1 需求期速度 (m/s) | R 首次下游数 | 1500s R/U 网外车辆数，17；23 | 限定结果 |
|---:|---:|---:|---|---|
| C 3200/720 | 30.873/30.321 | 36/40 | 150/75；146/73 | 对照，有R通过也有积压。 |
| ML 2600/720 | 30.422/30.022 | 67/69 | 122/61；121/60 | 降主线需求后R通过机会增加，但不是主线容量证据。 |
| MH 3800/720 | 31.709/31.521 | 0/0 | 180/90；181/90 | 需求期R被排除，M局部仍高通过；不是永久排除，所有车2700s前完成。 |
| RL 3200/360 | 30.496/30.366 | 38/40 | 9/9；9/10 | 降匝道需求改善部分端点，但R下游只比C多2/0，不能说所有指标改善。 |

Stage 3 **不新增仿真**，独立分析上述8条档案：14,564个运行–车辆身份、40/40行为问答、7,120个共享道R/U同时技术停驶标签；R停驶在路径上的观察次序8/8一致。Q1/Q3因此在早期声明范围内支持，Q2/Q4仍未识别；`speed≤0.1m/s` 是技术停车，不能直接等于因R造成的U损失。[Stage 3 诊断报告](STAGE3_BASELINE_DIAGNOSTIC_REPORT.md)、[修订复审](STAGE3_STAGE5_ASTRA_REVIEW_20260913.md)。

Stage 4 在 qRamp720、U360、X180 veh/h、seeds17/23下，**先**运行 qMain3500 两种子；依预定分支再运行3650两种子，取消3350分支。四次新运行全部完成、0重试。`[0,1500)` 的 R 首次下游数在3500为 **14/11**，在3650为 **0/0**；四点均不满足当时预登记的局部 EJMI 充分判据。3650的R虽在需求窗未下游通过，2700s前仍全部完成。这只支持原登记点上的具体障碍，不能证明任意临界点不存在或路网结构必然错误。[Stage 4 原始判定报告](STAGE4_TARGETED_VALIDATION_REPORT.md)。

Stage 5 **不新增仿真**：完成O/G清单、敏感性及交接审查，原 Q1/Q3支持、Q2/Q4未识别，所以是 `specific_obstacle`，不是 `preliminary_ready`。独立复审修正了异常输入拒绝、12个证据ID到23条路径的映射以及5个不可双seed配对键；旧定点结果不因这些更正变成阳性。[Stage 5 历史报告](EXPLORATORY_VALIDATION_REPORT.md)、[修订复审](STAGE3_STAGE5_ASTRA_REVIEW_20260913.md)。Stage 2–5 与后续 RI3350/V2/当前 M3600 系列的输入、时域及门槛不同，故不能合成一个因果效应估计。

D-016 的**当前版本 Stage 6 启动账本**截至结项为**32 次登记的启动尝试**：18 次无控，之后 14 次 NOOP/控制；此数不包含上述早期 Stage 2–4 的运行；其中 11 次归技术诊断或修复，21 次计入实验额度（18 无控、V8 S17、V15 S23/S42）。V12 在导入 TraCI 时失败，未启动 SUMO，故 32 不能说成 32 个 SUMO 进程。V15 S17 在账本中仍是技术验证，但其通过全部门槛的数据可作有注明的探索观察；不因结果可用就事后改账本分类。[D-016–D-018](../DECISIONS.md)、[执行记录](../../artifacts/stage6_standard_metering_execution_20261003_v1/EXECUTION_RECORD.md)。没有为撰写本报告新增仿真。

### 2.2 标准控制执行器的实际修复顺序

下表只报告**确已启动**的版本；V1/V4 等准备卡未运行，不算进32次账本。技术失败留有独立目录和回执，不选取有利结果替代失败记录。[执行记录与逐次回执](../../artifacts/stage6_standard_metering_execution_20261003_v1/EXECUTION_RECORD.md)、[工作日志](../WORKLOG.md)。

| 版本/运行 | 实际观测 | 处置 |
|---|---|---|
| V2/V3 NOOP | V2 未建立 TraCI 连接；V3 受启动期限阻断，未得到完整交通输出。 | 查启动问题，原尝试保留。 |
| V5/V6 NOOP | 4200s 中性交通与 OPEN 等价、4050车完成；V5 API 占有率与 XML 不同。V6 有 **173/238** lane 窗占有率超出 XML 原容差，均差 −1.352、最大差 −5.892 个百分点；车辆数核对仍通过。 | 测量反馈暂停，不以错误占有率控制。 |
| V7 NOOP | 启动时停留于 dyld 加载期，超时前未进入可测交通步骤。 | 不据此否定新检测器算法。 |
| V8 NOOP | 事件驻留法重构 **7140** 观察组，**238/238** lane 窗与 XML 一致；4200s/4050车中性检查通过。 | 放行首次 S17 控制技术试验。 |
| V8 S17 控制 | 完成 4200s，已判资格前车 228/228 放行；但 **10 次紧急制动**，含 **8 次红灯急停**。 | 安全 NO-GO；不复制 S23/S42，不把主线变化认定为合格控制效果。 |
| V9 S17 控制 | 安全/检测门通过，556/556有资格服务；持续排队的主评价时段指令约 **1070.866 veh/h**，实放 **564 veh/h**。 | 速率跟踪 NO-GO；定位为当时停驶前车安全门限制，不将低服务量误称标准控制有效。 |
| V12/V13/V14 技术修复 | V12 系统 Python 无 TraCI，SUMO 未起；V13 运行至 t1 因未初始化日志字段停；V14 在 t653 首辆 R 正确越线后被过严的绿后制动界限安全阻断。 | 逐项修复并用新卡复审，未调整网络、需求、城市信号、反馈目标或增益来制造结果。 |
| V15 S17/S23/S42 | 新绿后界限采用真实绿后速度；三种子均完成全部安全、测量、车辆及速率门，结果见 §4。 | 三组有效探索配对，停止额外探索启动。 |

V8 危险信号切换和 V9 实际速率不足是**真实的技术失败**，不能将两者的主线/城市结果纳入 V15 效果平均。[V8 S17 核查](../../data/processed/stage6_standard_metering_execution_20261003_v1/alinea_s17_v8/S17_REVIEW.md)、[V9 速率诊断](../../data/processed/stage6_safe_actuator_feasibility_20261003_v1/FEASIBILITY_NOTE.md)、[V15 预定设计](STAGE6_SAFE_ACTUATOR_EXPLORATORY_DESIGN_20261003.md)。

## 3. 当前版本无控需求探索：完整 18 次结果

下表 `P/S` 是项目预先声明的探索性主线低速状态支持秒数（固定 `[1200,3000)` 的 1800 s 窗）；它们不是已校准的普适 breakdown 概率。`M 系统时间均值`为**全请求 M 群体**从计划出发到到达的观测时间，包含源头插入等待；所有 18 次均在 4200 s 前完成。前批次同一运行在后批汇总表重现，本表按唯一 run ID 只列一次。[无控报告 §2–4](STAGE6_BOUNDARY_SEARCH_20261002_REPORT.md)、[批次 1](../../results/tables/stage6_boundary_search_20261002_v1/batch01_r0/batch_summary.csv)、[批次 2](../../results/tables/stage6_boundary_search_20261002_v1/batch02_ramp/batch_summary.csv)、[批次 3](../../results/tables/stage6_boundary_search_20261002_v1/batch03_refine/batch_summary.csv)、[三种子邻域](../../results/tables/stage6_boundary_search_20261002_v1/batch05_seed_neighborhood/batch_summary.csv)。

| qMain/qRamp 请求 (veh/h) | seed | P (s) | S (s) | M 系统时间均值 (s/辆) |
|---:|---:|---:|---:|---:|
| 2400/0 | 17 | 0 | 0 | 70.82 |
| 3000/0 | 17 | 0 | 0 | 73.75 |
| 3000/600 | 17 | 0 | 0 | 74.09 |
| 3000/1200 | 17 | 0 | 0 | 74.60 |
| 3600/0 | 17 | 0 | 0 | 75.85 |
| 3600/600 | 17 | 0 | 0 | 76.88 |
| 3600/750 | 17 | 240 | 0 | 77.59 |
| 3600/900 | 17 | 1800 | 1800 | 155.74 |
| 3600/1200 | 17 | 1800 | 1800 | 191.34 |
| 4200/0 | 17 | 150 | 0 | 79.86 |
| 3600/0 | 23 | 0 | 0 | 75.47 |
| 3600/600 | 23 | 90 | 0 | 76.45 |
| 3600/750 | 23 | 90 | 0 | 77.08 |
| 3600/900 | 23 | 1560 | 1500 | 110.03 |
| 3600/0 | 42 | 0 | 0 | 74.88 |
| 3600/600 | 42 | 0 | 0 | 75.93 |
| 3600/750 | 42 | 0 | 0 | 76.62 |
| 3600/900 | 42 | 1800 | 1800 | 139.50 |

**有界解释。**在 M3600 的已测网格内，R600–750 主要是弱或短暂局部扰动，R900 三个种子均出现长时间严重主线状态，故 R750–900 **夹住已采样的状态变化区**，M3600/R900 是可解释的控制比较候选，而非容量的精确值。空间图与逐秒检查支持低速先在 Merge 附近形成、后向上游传播；R900 主评价窗实际 R 换入主线约 **900/904/898 veh/h**。R900 的 M 源头插入延迟最大为 **58/0/65 s**：S17/S42 的入口积压晚于道路内部恶化，S23 无 M 源等待，故不能把所见严重状态简单解释成“车辆一开始就没进网”。R1200 的实际汇入约 1044 veh/h，名义请求不等于真实输入；M4200/R0 的短暂 P 更像移动扰动，不能当固定 Merge 瓶颈。[无控报告 §4](STAGE6_BOUNDARY_SEARCH_20261002_REPORT.md)。

![三种子主线速度时空图](../../results/figures/stage6_boundary_search_20261002_v1/batch05_seed_neighborhood/speed_mps.png)

## 4. 当前版本 V15 控制：技术门与具体结果

每一对请求 M3000、R600、U300、X150，共 **4050 辆**；三次 V15 与各自 OPEN 均 4050/4050 入网且到达、4200 s 时无未完成车。三个种子各自的控制前 600 个逐秒 FCD 标签与 OPEN **600/600 完全一致**。每次 119 次反馈更新、**238/238** 主线 E1 lane 窗与 XML 对齐；各有 **600/600** 个唯一、预期 R 绿灯过线，红灯过线、多车/错车、空绿灯、interlock 中止、SUMO 交通警告均为 0。每个种子 `[1200,3000)` 的六个固定 300 s 窗内，储存车道每秒均有需求；全部 18 个窗按预定 `|实际−指令|/指令 ≤10%` 通过，三种子最大偏差 **5.33%/4.27%/5.46%**。这里的 900 veh/h 是速率上限设置，不能写成恒定实测通行能力。[三份独立 gate：S17](../../data/processed/stage6_safe_actuator_v15_audit_20261003_v1/S17_GATE_REVIEW.md)、[S23](../../data/processed/stage6_safe_actuator_s23_v15_audit_20261003_v1/S23_GATE_REVIEW.md)、[S42](../../data/processed/stage6_safe_actuator_s42_v15_audit_20261003_v1/S42_GATE_REVIEW.md)。

下表时间为**全请求群体系统秒**（计划出发至到达；包括网外源等待）；速度是主评价窗内主线 cells13–17 的 M 车辆秒加权均速。数字依次为同 seed 的 OPEN→V15，差值为 V15−OPEN。[独立三种子综合](../../data/processed/stage6_safe_actuator_three_seed_synthesis_20261003_v1/THREE_SEED_REPORT.md)、[逐类配对表](../../results/tables/stage6_safe_actuator_three_seed_synthesis_20261003_v1/paired_results.csv)。

| seed | M 速度 (m/s) | M 系统秒 | R 系统秒 | U 系统秒 | X 系统秒 | 全网变化 (s) |
|---:|---:|---:|---:|---:|---:|---:|
| 17 | 9.666→25.903 | 467230→230515 (**−236715**) | 58984→365441 (**+306457**) | 19888→110473 (**+90585**) | 10289→10486 (+197) | **+160524** |
| 23 | 11.836→26.024 | 330104→228936 (**−101168**) | 57314→399909 (**+342595**) | 20022→123469 (**+103447**) | 10303→10432 (+129) | **+345003** |
| 42 | 9.958→26.328 | 418512→227221 (**−191291**) | 58971→409993 (**+351022**) | 19828→126519 (**+106691**) | 10355→10737 (+382) | **+266804** |

主线的保护反应在三组均出现；主线平均速度的车辆秒分母随交通状态变化，所以速度本身不等于相同车流量下的旅行时间节省。M 系统时间改善中，S17/S42 还包含 OPEN 的 M 源等待 **19762/19452 s** 被消除；S23 两臂均无 M 源等待。R 的 V15 网外源等待为 **143668/169917/175759 s**，U 为 **57454/67986/70292 s**，不能将全部 U 成本归于共享道路上的物理阻塞。全网 M+R+U+X 时间在三组均上升，本 V15 策略**未显示可接受的总量 sweet spot**。[三种子综合](../../data/processed/stage6_safe_actuator_three_seed_synthesis_20261003_v1/THREE_SEED_REPORT.md)。

### 4.1 匝道积压与城市共享路段

以 `speed <1.389 m/s`（约 5 km/h）定义逐秒慢行，控制臂 R 首次在 storage、内部连接 `:urban_diverge_1_0`、共享道 `shared_approach_0` 出现慢行的时刻分别为：S17 **649/1020/1140 s**，S23 **647/1023/1106 s**，S42 **646/914/1010 s**。在每个首次共享道 R 慢行时刻，其他两个路段也各有慢行 R；但这些是不同车辆的逐秒观察，**没有证实车身间连续、从 meter 一直连到共享道的队列**。[共享道逐车核查](../../data/processed/stage6_safe_actuator_three_seed_synthesis_20261003_v1/SCIENCE_CHAIN_EVIDENCE.md)。

在 `[1200,3000)`，OPEN 的共享道 R/U 慢行车辆秒三种子均为 0；V15 的 R 为 **7681/8421/7058**，U 为 **3076/3338/2813**。其中 U 在城市入口绿灯期间慢行为 **2303/2498/2098** 车辆秒，最近同车道前车是 R 的 U 慢行观察为 **2889/3131/2643**；两个子集重叠，不能相加成独立延误。S23 的一个原始 FCD 例子：`U_flow.188` 在 `R_flow.320` 后方、同一共享车道、城市绿灯，**t2363–2384 连续 22 s** 两车均低速。它支持局部 U 受 R 队列暴露的机制，但不提供 U 总成本的唯一因果分解。预先规定的“meter 锚定、空间连续且持续 ≥30 s 的慢行链”在三种子均为 **0 个合格事件**，不能事后降低时长门槛并宣称通过。[共享道逐车核查](../../data/processed/stage6_safe_actuator_three_seed_synthesis_20261003_v1/SCIENCE_CHAIN_EVIDENCE.md)、[配对综合](../../data/processed/stage6_safe_actuator_three_seed_synthesis_20261003_v1/THREE_SEED_REPORT.md)。

## 5. 逐项指标判定

### 5.1 原 O1–O6：工作产物

这些是 **Stage 3–5 历史产物合同**；其通过表示旧批次评估工作完成，不等于旧 Q2/Q4 或当前 Stage 6 自然通过。新系列另由独立卡、原始回执、三种子表和本报告交接。[原标准 §3](EXPLORATORY_VALIDATION_COMPLETION_PLAN.md)、[历史清单](../../data/processed/exploratory_validation_closeout_20260913_v1/artifact_inventory.csv)、[更正复审](STAGE3_STAGE5_ASTRA_REVIEW_20260913.md)。

| 项 | 要求 | 证据与历史判定 | 对当前结项的解释 |
|---|---|---|---|
| O1 场景与测量 | 网络、lane、群体、信号、指标/单位/边界 | 历史产物齐；当前两条 M 主线＋独立约294.51 m加速车道，R 实际换入 M；V15 E1 窗核验238/238/种子。**完成**。[Merge 核查](Stage%206%20Merge%20与车辆插入调查.md)、[V15 gate](../../data/processed/stage6_safe_actuator_v15_audit_20261003_v1/S17_GATE_REVIEW.md) | 支持测量用途，不等于现实几何校准。 |
| O2 需求与车辆账 | 每类计划、入网、到达、未完成/网外 | 历史32/32 run-class、64/64端点；当前无控18次均核账；V15每组4050/4050完成。**完成**。[历史门清单](../../data/processed/exploratory_validation_closeout_20260913_v1/gate_inventory.csv)、[无控报告](STAGE6_BOUNDARY_SEARCH_20261002_REPORT.md) | 来源等待与网内排队分列。 |
| O3 代表行为诊断 | 停驶、传播、R汇入、U暴露、M上下游 | 历史40/40问答单元；当前18次 P/S及空间传播、V15共享道逐车证据。**完成**。[早期总结](EXPLORATORY_VALIDATION_REPORT.md)、[共享道核查](../../data/processed/stage6_safe_actuator_three_seed_synthesis_20261003_v1/SCIENCE_CHAIN_EVIDENCE.md) | 阴性严格连续链保留。 |
| O4 用途评估 | Q1–Q4、替代解释和范围 | 历史完成时为 `specific_obstacle`；当前按 §5.3 重新判定，记录支持与未证。**评估工作完成**。[旧审计](STAGE6_COMPLETION_CRITERIA_AUDIT_20261002.md)、[最终交接](STAGE6_EXPLORATORY_CLOSEOUT_AND_FORMAL_HANDOFF_20261003.md) | O4 完成不等于所有科学主张完全证明。 |
| O5 时间/敏感性 | 全时域、切窗、重聚合、seed/输入局限 | 历史6/6输入对照、8/8 seed 单元、96/96值、48/48时序；当前 M3600邻域三种子、固定1800s评价与4200s终点。**有界完成**。[历史更正](STAGE3_STAGE5_ASTRA_REVIEW_20260913.md)、[无控报告](STAGE6_BOUNDARY_SEARCH_20261002_REPORT.md) | 无正式功效、稳态或全需求鲁棒性结论。 |
| O6 总结交接 | 证据、限制、分类及正式设计问题 | 历史22/22交接项；本报告、D-018、精确正式设计交接及状态记录。**完成**。[历史总结](EXPLORATORY_VALIDATION_REPORT.md)、[正式交接](STAGE6_EXPLORATORY_CLOSEOUT_AND_FORMAL_HANDOFF_20261003.md) | 正式参数仍须另行决定。 |

### 5.2 原 G01–G08：证据和处理完整性

**历史合同的状态不追认改写。**下表旧分母只覆盖原 Stage 3–5 批次。当前 18 无控＋3 个 V15 的对应来源/处理资格由各自报告和 gate 独立核验；新批次未自动继承旧矩阵分母。[原标准 §4](EXPLORATORY_VALIDATION_COMPLETION_PLAN.md)、[历史 gate 清单](../../data/processed/exploratory_validation_closeout_20260913_v1/gate_inventory.csv)、[当前数据 gate](../../data/processed/stage6_safe_actuator_three_seed_synthesis_20261003_v1/THREE_SEED_REPORT.md)。

| 门 | 原始检查内容 | 历史实测/判定 | 当前版本复核与适用范围 |
|---|---|---|---|
| G01 | 注册运行、原始来源/哈希 | 8/8运行、232/232档案文件；**通过** | 无控18个唯一ID全完成；V15每 seed 32/32 raw manifest 哈希/大小匹配。 |
| G02 | 类别/端点/身份核账 | 32/32 run-class、64/64端点；**通过** | V15每 arm 4050/4050入网到达，未完成/未出发0。 |
| G03 | 测量元数据与时序 | FCD21600/21600标签、E1 4320/4320区间；**通过** | V15控制/轨迹4200s连续，238/238 E1 lane 窗/种子与 XML 对齐。 |
| G04 | 五类行为诊断 | 8运行×5=40/40单元；**通过** | 无控 P/S 和时空传播、控制后 R/U 共享道均分析，阴性仍列出。 |
| G05 | 处理可信度/故障模式 | 修正后33/33离线测试、15类异常输入拒绝、96/96旧产品不变；**通过历史批次范围** | 当前执行器安全算术、真实过线、检测器事件和信用账由数据 gate 独立复算；不承诺任何未来异常全覆盖。 |
| G06 | 敏感性、随机性、时域 | 6/6输入对照、8/8 seed 单元、96/96值、48/48时序；43个符号不一致和5个不可双seed配对键显式保留；**通过诊断完成门** | 当前 M3600四档R三seed，控制为同需求三配对；不声称统计功效或普适稳定性。 |
| G07 | Q1–Q4评估完整 | 4/4有判定；旧 Q2/Q4仍 `not_identified`；**通过评估工作门** | 当前用途另按下表审查；G07绝非自动“全部Q支持”。 |
| G08 | 六类产物与交接分类 | 6/6、修正后22/22项和12证据ID/23精确映射；**通过** | 新交接保留负结果、卡/回执和正式协议未冻结事实。 |

### 5.3 核心 Q1–Q4 与补充 V1–V6：当前用途能否成立

早期 Q 定义来自[原标准 §4.1](EXPLORATORY_VALIDATION_COMPLETION_PLAN.md)。V1–V6 是为新系列提出的**适用范围映射**，不是可追认的旧数值门或正式协议。[旧指标核对](STAGE6_COMPLETION_CRITERIA_AUDIT_20261002.md)。

| 当前指标 | 必须回答的问题 | 实测依据 | 结项判定及界限 |
|---|---|---|---|
| Q1 / V1 技术可观测 | M/R/U/X的流动和积存、lane/信号/时间/端点能否核对？ | 两主线＋独立结束加速车道，重建 R 确有实际换道；18无控完整，V15每臂4050/4050、238/238 E1、控制前600/600完全同轨。[Merge 核查](Stage%206%20Merge%20与车辆插入调查.md)、[三 gate](../../data/processed/stage6_safe_actuator_three_seed_synthesis_20261003_v1/THREE_SEED_REPORT.md) | **支持声明的合成场景观测用途。**未证明任意模型缺陷均不存在。 |
| V2 真实供给 | 请求需求是否真正到达 Merge，源头是否先限流？ | R900主评价实汇入900/904/898 veh/h；M源等待58/0/65s上限出现在路内恶化后；R1200实际约1044veh/h，已显式区分。[无控报告 §4](STAGE6_BOUNDARY_SEARCH_20261002_REPORT.md) | **支持对已测点的供给解释。**不能把 q 请求一律当实际流率。 |
| Q2 / V3 主线临界现象 | 是否有与 Merge 时空关系一致、可比较的轻/重状态？ | M3600/R0–750 P≤240s、S=0；R900 P1560–1800s、S1500–1800s，M全群体均时110.03–155.74s；空间传播向上游，三seed重复。P/S 分类依据主评价窗 `[1200,3000)` 的30s主线空间单元速度、慢车与密度等预定规则；断面流量和占有率完整时序用于交叉解释，并与 `[0,4200)` 的源头/网内累计车辆时序区分；例如 [S17 R900主线单元时序](../../data/processed/stage6_boundary_search_20261002_v1/M3600_R900_S17/mainline_cells.csv)、[断面流量/占有率时序](../../data/processed/stage6_boundary_search_20261002_v1/M3600_R900_S17/detectors.csv)、[车辆累计时序](../../data/processed/stage6_boundary_search_20261002_v1/M3600_R900_S17/cumulative.csv)与[三种子空间图](../../results/figures/stage6_boundary_search_20261002_v1/batch05_seed_neighborhood/speed_mps.png)均可回查；[批次总表](../../results/tables/stage6_boundary_search_20261002_v1/batch05_seed_neighborhood/batch_summary.csv)列三种子状态。 | **支持已采样临界区与持续主线恶化。**不是精确容量、概率或现实 breakdown 标定；旧 EJMI/State1历史门不追认通过。 |
| Q3 / V4 匝道和城市侧 | R是否到达共享路，U有无可观察暴露/通行代价，并排查单纯红灯/网外等待？ | V15三seed共享道 R慢行7681/8421/7058、U慢行3076/3338/2813车辆秒，对应 OPEN均0；U在绿灯期间慢行和同车道R在前均有大量记录；S23同车道22s原始例；U全群体成本增加。[共享道证据](../../data/processed/stage6_safe_actuator_three_seed_synthesis_20261003_v1/SCIENCE_CHAIN_EVIDENCE.md)、[配对表](../../results/tables/stage6_safe_actuator_three_seed_synthesis_20261003_v1/paired_results.csv) | **支持同版局部物理暴露和城市代价可观测。**严格≥30s空间连续链0/3；U成本含大量网外等待，未证明全部增加均由R物理阻塞造成。 |
| Q4 / V5 同版本双侧关联 | 主线保护与 R/U 风险能否在可比条件下共同观察？ | 无控 R900定位严重主线状态；同需求、同seed OPEN/V15三对前600s完全相同。M系统秒各降，R/U各增；R/U共享道暴露直接在V15出现。[配对综合](../../data/processed/stage6_safe_actuator_three_seed_synthesis_20261003_v1/THREE_SEED_REPORT.md) | **支持这一个当前版本工作点上的可研究权衡。**并未识别净收益 sweet spot，也没有跨需求外推资格。 |
| V6 有界结项与交接 | 来源、阴性、随机/时域限制、用户接受和后续边界是否完整？ | 18 OPEN和V15三seed卡/回执/数据审计；D-018条件授权与独立科学 PASS；精确交接。[决策](../DECISIONS.md)、[结项交接](STAGE6_EXPLORATORY_CLOSEOUT_AND_FORMAL_HANDOFF_20261003.md) | **通过探索交接。**正式设计仍须新seed、需求、策略、指标与协议审查。 |

若把 Q3 提升为“已证明从 meter 到共享道、车身间无断裂且至少持续30s的物理队列”或“已定量识别R引起的全部U额外损失”，证据**不支持**；上述不是本次用户要求的最低“现象可发生且可观测”口径。阴性结果在本报告和后续设计中保留，不以语义替换追认。用户此前不接受 D-012 那种旧/新系列拼接；本次 Q2–Q4 的关键证据来自当前同版本的无控及 V15 三配对，不依赖旧 B22 成功故事。[D-013、D-018](../DECISIONS.md)。

## 6. 统一结论及不能越界的地方

**已确认事实：**当前合成 Merge 的几何/插入和观测链在已测范围可核；18次无控运行定位 M3600、R750–900 的已采样状态转变；M3600/R900 的三组有效 V15 配对均显示主线改善、R/U成本增加及共享道路 R/U 低速暴露。控制安全和实际速率门通过；总系统时间在三组均增加；严格 ≥30s 空间连续慢行链在三组均为 0。[无控报告](STAGE6_BOUNDARY_SEARCH_20261002_REPORT.md)、[三种子综合](../../data/processed/stage6_safe_actuator_three_seed_synthesis_20261003_v1/THREE_SEED_REPORT.md)、[连续链核查](../../data/processed/stage6_safe_actuator_three_seed_synthesis_20261003_v1/SCIENCE_CHAIN_EVIDENCE.md)。

**有界推断：**这些现象在同一当前版本、相同需求和配对种子下构成值得正式研究的高速保护—匝道/城市代价问题；已核查的几何接错、源头先限流、检测器错配、无车却假称放行等明显替代解释未解释掉观察结果。不能由此证明现实道路有效、全部 U 成本的唯一因果机制、精确容量值或其他控制策略一定找到 sweet spot。[工程和数据 gate](../../data/processed/stage6_safe_actuator_v15_audit_20261003_v1/S17_GATE_REVIEW.md)、[科学结项](STAGE6_EXPLORATORY_CLOSEOUT_AND_FORMAL_HANDOFF_20261003.md)。

**完整判定：**O1–O6 的历史工作产物与 G01–G08 的历史完整性门各有完整记录，旧 Q2/Q4 当时仍未识别，状态不追认更改；针对用户后来明确要求的**当前版本完整探索用途**，Q1–Q4/V1–V6 在上述限定口径下已有证据和独立科学审查支持。因此按 D-018 登记 **`completed / preliminary_ready for formal experiment design`**，停止仅因额度尚余而继续探索。这个状态既不等于本 V15 政策成功，也不冻结正式实验协议。[早期标准](EXPLORATORY_VALIDATION_COMPLETION_PLAN.md)、[D-018](../DECISIONS.md)、[正式设计交接](STAGE6_EXPLORATORY_CLOSEOUT_AND_FORMAL_HANDOFF_20261003.md)。

**仍未解决：**只有一个控制需求点和三个已观察种子，S17用于执行器开发；严格30s连续链阴性；城市损失中的网外等待与共享道阻塞不能唯一拆分；无精确 breakdown 概率、可迁移 ALINEA 参数、可接受队列边界、可行 sweet spot 或现实校准。原始 RI3350、旧固定时制 V2、V8/V9 失败/阴性与 V15 有不同适用范围，必须继续分开。[结项交接的限制与步骤](STAGE6_EXPLORATORY_CLOSEOUT_AND_FORMAL_HANDOFF_20261003.md)。

**下一阶段的精确入口：**在正式设计中预先选新需求/独立种子与政策集合，明确主线、实际匝道放行与排队、U/X和全网成本、共享道暴露、网外等待、失败及删失处理、统计与停止规则；配对条件和调参/评估集合分开。经独立审查与用户批准后才填写并冻结 [`EXPERIMENT_PROTOCOL.md`](../EXPERIMENT_PROTOCOL.md)，随后另行执行正式仿真。无需为本报告再跑探索仿真。[正式交接 §4](STAGE6_EXPLORATORY_CLOSEOUT_AND_FORMAL_HANDOFF_20261003.md)。

# SUMO 探索验证阶段：文献依据与项目适用边界

日期：2026-09-09。类型：有目标的文献与官方方法资料检索，不是系统综述。服务于 [探索验证完成方案](../docs/EXPLORATORY_VALIDATION_COMPLETION_PLAN.md)。本文件不批准实验、不冻结参数。

## 1. 核心判断

六类产出可以作为项目的文档结构，但不存在文献规定的“交齐这六项即验证通过”。需要同时区分实现核验、行为证据和特定用途的适用性；敏感性与随机性必须另外有可追踪检查项。没有现场观测的合成场景，本轮能做技术核验与行为合理性评估，不能宣称已经完成实证校准。

完成标准应提前公开。数学恒等式、记录完整性可以设零差错/百分比门槛；交通行为则应报告效应大小、持续时间、空间关系和未知项，不能把任意速度下降百分比包装成统一科学标准。研究用途上的关键缺口不能通过其他检查的高分抵消。

## 2. 检索与选择记录

- 检索日期：2026-09-09。
- 主要检索式：`FHWA traffic microsimulation 2019 calibration variation confidence initialization`；`Sargent verification validation simulation models`；`SUMO VehicleInsertion TripInfo E1 E2`；`Papageorgiou Kotsialos freeway ramp metering overview`；`Cassidy Bertini freeway bottlenecks`；`sumoITScontrol paper`。
- 优先官方指南、原作者论文、作者机构库和 SUMO 官方文档。使用 FHWA **2019** 更新版；单独标明 2004 的历史例子，不混用版本。
- Sargent 2013 期刊页可核标题与摘要；本综述的方法内容改用可读全文的 **Sargent 2010 WSC**，不把两篇页码混用。
- Brilon 等 2005 已在项目阅读包；本轮网页全文获取失败，未据此新增详细规则。未把搜索摘要、二手网站或未读全文当作具体阈值依据。
- SUMO 在线文档不保证固定在 1.26.0；用于理解字段，版本相关行为仍须核对本项目实际配置/输出及 1.26.0。没有升级软件或安装依赖。
- 以下条目写明读取层级。数值来自特定案例时不直接转成项目验收线。

## 3. 一手来源与可采用的结论

| ID | 来源及已读范围 | 支持的原则 | 本项目如何使用／不能如何使用 |
| --- | --- | --- | --- |
| L1 | Sargent, R. G. (2010), *Verification and Validation of Simulation Models*, WSC, pp.166–183；[会议原文](https://informs-sim.org/wsc10papers/016.pdf)，§1、§2、§8、§10、§12 | 模型有效性针对用途与适用域；实现核验不等于行为有效；不可观察系统的证据受限；作者反对掩盖缺陷的加权总分 | 六产出是组织方式；采用逐项门，不设“80分毕业”。本项目不能通过合成数据自证真实世界准确性 |
| L2 | FHWA (2019), *Traffic Analysis Toolbox Volume III*, FHWA-HOP-18-036；[第1章](https://ops.fhwa.dot.gov/publications/fhwahop18036/chapter1.htm)，Purpose、Measures、Scope、Preliminary Plan | 用途、指标、空间时间范围和资源需一起定义；关注相邻受影响设施与边界 | 同时观察 M/R/U、网外边界和清空期；分析计划可迭代。不是先跑完再按结果挑指标 |
| L3 | FHWA 2019 [第3章](https://ops.fhwa.dot.gov/publications/fhwahop18036/chapter3.htm)，Simulation Run Control Data；[第4章](https://ops.fhwa.dot.gov/publications/fhwahop18036/chapter4.htm)，Software/Input/Animation/Key Decision | 输入、软件、动态行为检查先于校准；时域覆盖所研究的形成与消散过程；单seed可以用于错误检查 | 复用 Stage 1/2 技术核验；新增功能做针对性测试。不是每次错误检查都重跑多seed，也不是动画能独自证明因果 |
| L4 | FHWA 2019 [第5章](https://ops.fhwa.dot.gov/publications/fhwahop18036/chapter5.htm)，代表日、变化包络与接受准则 | 校准围绕观测数据及其变化，默认设置不是校准证据 | 没有现场数据则实证校准保持未完成，不虚构“与现实误差<5%” |
| L5 | FHWA 2019 [第6章](https://ops.fhwa.dot.gov/publications/fhwahop18036/chapter6.htm)，Replications、Sensitivity Testing | 随机重复数与指标方差和精度有关；敏感性是另一种检验 | 其四个初始重复用于该章替代方案分析流程，不是所有探索必须四seed的规则；两个seed一致也不等于统计稳健 |
| L6 | FHWA 2004 [§5.6](https://ops.fhwa.dot.gov/trafficanalysistools/tat_vol3/sect5.htm)，历史 Calibration Targets | GEH 等用于模拟与观测数据的校准比较；指南列有特定应用实例 | 不把 GEH<5、85% 等直接拿来验收没有实测流量的合成场景 |
| L7 | SUMO [VehicleInsertion](https://sumo.dlr.de/docs/Simulation/VehicleInsertion.html)，Insertion、Step Length、Departure options | 插入会受安全条件、时间步和位置/车道/速度设置影响 | 比较请求需求与实际入网，核对实际入网位置。不能为“100%插入”关闭安全检查；也不能由配置意图推断上游道路已被实际使用 |
| L8 | SUMO [TripInfo](https://sumo.dlr.de/docs/Simulation/Output/TripInfo.html)，Generated Output、Unfinished | depart 是实际入网，departDelay 与 duration 含义不同；默认到达才输出，未完成需显式记录 | 分开入网延迟与路内行程，声明样本分母和截尾。0.1 m/s 为软件等待量相关定义，不是 freeway Breakdown 定义 |
| L9 | SUMO [E1](https://sumo.dlr.de/docs/Simulation/Output/Induction_Loops_Detectors_(E1).html)、[E2](https://sumo.dlr.de/docs/Simulation/Output/Lanearea_Detectors_(E2).html)，定义与输出字段 | 断面与区间检测有不同空间和计数语义；无车速度/贡献、队列参数必须按输出解释 | 以编译位置、lane、区间和实际记录限定覆盖，E1 不凭名字成为全路段状态，E2 jam 不自动成为全匝道队列 |
| L10 | Cassidy, M. J. & Bertini, R. L. (1999), *Some Traffic Features at Freeway Bottlenecks*, TR-B 33(1),25–42；[作者机构库摘要及书目信息](https://digitalcommons.calpoly.edu/cenv_fac/307/)，[DOI](https://doi.org/10.1016/S0191-2615(98)00023-X) | 实测瓶颈研究关联邻近检测点的累计曲线、排队状态和排队前后出流 | 需要时空证据；两处实测瓶颈约10%的差异不是本项目必须出现的Capacity Drop标准。本轮未据全文细节制定新算法 |
| L11 | Papageorgiou, M. & Kotsialos, A. (2002), *Freeway Ramp Metering: An Overview*, IEEE T-ITS 3(4),271–281；[作者机构记录与摘要](https://sndbx.library.tuc.gr/view/61894?locale=en)，[DOI](https://doi.org/10.1109/TITS.2002.806803) | 匝道计量属于对高速公路输入的控制，控制评价有别于单纯改变需求 | 本轮不实施控制；无控制适用性通过不证明ALINEA有效。没有从摘要提取任何项目参数 |
| L12 | Riehl, K., Kouvelas, A., & Makridis, M. A. (2026), *sumoITScontrol: Traffic Controller Collection for SUMO Traffic Simulations*；[DLR会议预印本](https://sumo.dlr.de/preprints/pre-print-3284.pdf)，摘要、§1、§3–4；[作者预印本记录](https://arxiv.org/abs/2604.23240) | 控制器比较需要可复现实现，并重视随机变化、测量与统计评价 | 支持正式阶段单独设计重复与公平比较；论文示例的优化参数不移植为当前探索门槛。此处明确引用预印本版本，不填写占位DOI |

## 4. 六产出的映射

| 原产出 | 文献支持 | 应补充的可检验要求 |
| --- | --- | --- |
| 场景与测量说明 | L1、L2、L3、L7、L9 | 每个核心观测有位置/车辆/单位/区间；编译与实际使用的道路分开 |
| 需求与车辆账目 | L7、L8 | 已知总体的身份、计数守恒；缺失与真零分开；入网和合流分开 |
| 代表条件行为诊断 | L2、L3、L10 | 原始时序、空间定位、持续样本和信号上下文；不是仅报告均值 |
| 场景适用性 | L1、L11 | 针对选定问题的主张—证据矩阵，不能由“结果表都填好”推出通过 |
| 方法与时长适用性 | L2、L3、L5、L8 | 加载/截止/延迟入网/窗口敏感性，以及输入扰动与seed变化分开 |
| 探索交接 | L1、L2、L5、L12 | 可沿用／待验证／待讨论逐项有依据；正式样本量不能照搬探索seed数 |

横向增加独立的“敏感性与随机性”检查：它同时约束行为诊断、时长和适用性。检查完成率可以量化，科学方向不要求所有seed或窗口一致；不一致本身必须被解释和报告。

## 5. 对本项目的结论

Stage 1/2 已支持实现与测量的有限可信性，并得到无控制需求响应。它们未建立四种交通状态的覆盖，也未证明整个场景支持正式控制权衡。后续优先补八条既有运行的空间时间解释和主线侧证据；新运行必须由明确缺口驱动。

本项目提出的100%记录覆盖、0个未解释错误、全部预定对照完成、各阶段数量上限等属于透明的技术或管理合同，不是文献证明的科学充分样本量。它们在获批后可执行；科学用途仍须经过逐项证据审核。

方法原则置信度 High；合成场景对真实道路的外部有效性 Unknown；下游阶段是否能获得所需主线现象 Unknown。文献不能保证当前场景一定适用，也不能保证任何模型在低推理档位完全无误执行。

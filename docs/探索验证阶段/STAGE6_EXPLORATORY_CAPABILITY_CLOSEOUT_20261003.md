> Historical D-012 limited closeout, rejected by the user. D-018 later closed the current-version exploratory validation after V15 matched controls; see [the final closeout and formal-design handoff](STAGE6_EXPLORATORY_CLOSEOUT_AND_FORMAL_HANDOFF_20261003.md). Earlier PARTIAL statements below retain their checkpoint dates.

# Stage 6 探索验证结项：场景能力与正式阶段交接

**2026-10-03当前状态更正：用户明确不接受有限范围结项；探索恢复PARTIAL，当前版本标准ramp metering比较正在设计，未实现/未运行。D-012结项解释已撤回，由D-013取代。本文件下方有限结项及正式设计解锁文字为历史记录，不是当前接受状态或执行权限；已有原始证据和科学复核的限定结论保留。最新任务见PROJECT_STATE及STAGE6_CURRENT_VERSION_STANDARD_METERING_PLAN_20261003.md（方案已审查，未实施/运行）。**

日期：2026-10-03（Europe/Rome）。证据复核开始于2026-10-02，因此复核产物目录保留20261002。性质：有范围限制的探索验证；本轮新仿真次数0。

## 1. 结项决定

**探索验证阶段：COMPLETE_WITH_LIMITATIONS。当前同一结构的合成场景已具有论文所需的双侧现象能力，可进入正式实验方案设计；不继续探索仿真。正式实验尚未开始，协议仍为空、未冻结。**

依据用户最新明确目的：正式大规模实验前，确认场景能产生论文研究现象，并检查这些现象是否由建模错误造成；结合Robert2026-09-30“先技术核查和无控需求定位、再选点比较控制”的原始指导。这里确认的是相关现象与已检查技术链，不是模型全无错误、现实校准或控制收益。

用户已条件授权证据达标后登记结束，并要求核对旧证据适用性后重新评估。工程、数据及独立科学复审通过后，执行该限定结项。ALINEA feasibility、成功B、完整ABC、精确容量值或可行sweet spot不是本次阶段结束条件。

## 2. 旧城市证据能否沿用：已核对实际输入

[工程转用审计](../../artifacts/stage6_capability_closeout_20261002_v1/ENGINEERING_TRANSFER_AUDIT.md)及[机器记录](../../artifacts/stage6_capability_closeout_20261002_v1/ENGINEERING_TRANSFER_AUDIT.json)核对旧默认V2 A/B22与新M3600/R900的17/23/42输入，而不是只看计划文字：12项检查通过。

| 核对项 | 实际结果 | 对沿用的意义 |
|---|---|---|
| 编译网络、lane连接、路权和共享结构 | 同一network，SHA256 `887c232483f0c68dc024334ff5997250d7d36299ab2744bdcf49d5a314c700ca` | 城市共享区/匝道/两主线+辅助道的物理联系相同 |
| SUMO及默认行为 | 同1.26.0及二进制哈希；同technical_passenger声明，无sigma覆盖 | 不把sigma0敏感性混入默认模型 |
| 城市TLS、四条路线、depart规则 | 相同；城市45G/3y/9G/3y | 不存在把城市信号改差后拼接能力的情况 |
| 11检测器、FCD和输出角色 | 位置/参数/周期相同；FCD压缩只是保存形式变化 | 共享区暴露、队列与生命周期含义可对应 |
| 旧A/B22处理内匹配 | demand XML字节一致；匝道A_OPEN与B_MODERATE有意不同 | 旧城市侧对比仍有效，原始RI3350不作为效应来源 |
| 加载/随机属性变化 | M3350.4→3600；R540→600s；请求截止1500→3000s；终止2700→4200s；speedFactor实现改变 | 明确不同工况，不迁移成本数值、不当成同一重复或新R900联合效应 |

**结论：旧有效重建实验的城市受阻能力可以沿用。** 双侧能力可以在不同工况分层举证；不要求同一需求同时出现两侧现象。当前并不声称新R900开放匝道具有旧B22的城市成本。

## 3. 双侧现象的实测证据

### 主线侧：新无控需求探索

[18运行报告](STAGE6_BOUNDARY_SEARCH_20261002_REPORT.md)和[无控最终科学复核](../../artifacts/stage6_boundary_search_20261002_v1/FINAL_SCIENTIFIC_REVIEW.md)：18/18完成，无失败/重试，全部车辆完成。M3600下R600/750较轻或短暂，R900在seeds17/23/42均出现Merge附近形成并向上游发展的持续拥堵。评价窗1800s内P支持1800/1560/1800s、S1800/1500/1800s；实际R评价流率900/904/898veh/h，R/U无源头插入等待。主线部分高种子源头等待出现在拥堵传播到入口后。

这些结果夹住已测R750–900弱/强变化区间，提供M3600/R900控制候选。不宣称完整二维容量曲线、精确breakdown概率或已证明capacity drop。

### 城市侧：旧默认V2匹配A/B22原始复算

[城市能力独立复核](../../data/processed/stage6_capability_closeout_20261002_v1/CITY_CAPABILITY_RECHECK.md)、[原始绑定数字](../../data/processed/stage6_capability_closeout_20261002_v1/city_recheck.json)：每臂5个关键raw对receipt的哈希/大小匹配；FCD覆盖2700秒、1861完整ID、连续轨迹与端点通过，全部完成，无排除。

- R平均网内停留A88.3125s、B242.1333s，增加153.8208s；U A64.9133s、B91.3867s，增加26.4733s。两臂所有R/U departDelay为0。
- 活跃窗[540,1500)s共享路段B有U慢行987车辆秒、停止508车辆秒，A两者0；共享R慢行2487、停止1261车辆秒。**慢行阈值<1.389m/s（约5km/h），停止<0.1m/s**；不能误记为慢行<5m/s。
- 共享E2 jam-positive22/90个30s区间、最大19辆；ramp storage44/90、最大27辆，A均0。E2混合车辆统计与U-specific FCD分别复核，不能将E2直接称U专属队列。
- B的987个U慢行车辆秒中，980个同秒共享lane有慢行R，902个最近同lane前车为R；511个发生于城市入口绿灯。A/B城市TLS2700个标签完全相同。t1064可见U103低速跟随同lane低速R122，城市绿、匝道红。

因此，这不是只由网外插入等待、输出截断或城市红灯直接停车解释的观察。它支持内部R积压、共享区R/U慢停与额外U停留的城市侧现象能力。它不将每秒U损失唯一归因于ramp spillback，也不证明连续meter-anchored队首跨越全部内部connector。

### 对固定配时疑虑的追加核查：当前三组OPEN城市轨迹

用户提出：Robert暂不支持固定22/28构造ABC，是否应按旧B22需求用当前OPEN重新运行。我们先只读现存数据，没有新启动。[当前OPEN复核](../../data/processed/stage6_capability_closeout_20261002_v1/current_open_city/REPORT.md)对M3600/R1200、M3000/R1200、M3600/R900的seed17逐秒FCD/TLS核对：三份各4200秒完整、六份raw哈希对receipt匹配。全程、active与eval窗口中共享R/U低于1.389m/s慢行及0.1m/s停止均0；储存/共享E2均0/140 jam-positive。R1200的U最大入口等待275s和上游urban_in慢停，不能改称共享路段回溢。

旧有效A本来就是B22同需求的OPEN对照，shared U慢行0。按旧M3350.4/R900改跑当前OPEN是实现/时程对照，取消了产生旧队列的限流处理；不能当旧B22城市现象的等价复验。已有更强M3600/R900及R1200 OPEN城市轨迹也未呈现该共享事件，数据不支持将重复旧名义需求设为必须补跑的结项项。

Robert原邮件暂缓的是以固定22/28配时刻意建立ABC，未要求作废已有有效城市观察。本次不继续固定配时、不把B22当标准ALINEA或成功主线保护证据。限定结项仍使用共同结构的分工况能力证据，**不声称当前三个OPEN点已经出现共享区回溢**。若用户另行明确采用“全部仅由当前OPEN同时证明双侧”的新用途，应单独登记待评估；不是静默删除旧证据或强行加需求凑现象。只有现存数据不足、且新run能改变具体候选点/模型或机制判断时才设计追加，另行审核和授权。

## 4. 逐项验收与历史范围

| 当前适用的能力指标 | 结项判断 | 限制 |
|---|---|---|
| Q1 / V1–V2 技术链、可观测性、真实供给 | 支持 | 限已核查输入/输出；不是模型任何工况无错 |
| Q2 / V3 主线临界现象 | 支持 | 当前有限加载期、三种子邻域；严格历史onset门不追认 |
| Q3 / V4 匝道及共享城市受阻能力 | 有限支持，足以存在性验收 | 旧默认V2 seed17，非新R900数值、非纯因果损失或连续全connector回溢证明 |
| Q4 / V5 双侧场景能力联系 | 支持限定用途 | 相关结构/信号/路线/行为/观测不变量已核对；分工况能力，不是一个点的sweetspot/联合政策效果 |
| V6 完整追溯、复审、边界与交接 | 完成 | 新正式样本、指标资格及协议需另行设计和批准 |

历史O1–O6/G01–G08完成与修订补件见[完成指标审计](STAGE6_COMPLETION_CRITERIA_AUDIT_20261002.md)。历史T54、SG6-R、D-011 ABC、State1/NO_WITNESS/NOT_EVALUABLE结果不改判；**本次不是“所有旧注册阈值均通过”**，而是按用户当前明确的场景能力用途结项。新旧实验分系列保留，原始RI3350的NOT_PAIRABLE/A_NOT_EVALUABLE保持。

## 5. 为什么停止，哪些限制移交

结项理由：已核查技术完整性；无控主线持续拥堵与较轻状态可区别；同一机制结构已有有效城市侧R/U受阻原始证据；能力转用的实际输入和测量不变量已核查；独立复审支持这个有界用途。继续相似无控点、重跑旧B22或先证明ALINEA并不是回答场景是否具备研究能力所必需。

尚未解决并移交正式设计/后续实验：ALINEA主线收益、执行器可行性与实际放行；是否存在sweet spot；完整连续回溢定义与必要轨迹链；城市侧跨种子/工况稳健性及因果分解；精确容量/占有率目标、capacity drop、状态校准；旧默认配对早期非局部M随机耦合。旧B22的M效应不作为本次主线因果证据，所以该历史问题不被隐瞒，也不被强行改判。合成场景未作现实交通校准。

## 6. 正式阶段的精确交接

**下一阶段：正式实验方案设计，尚未执行。** [GPT sol逐步交接](STAGE6_GPT_SOL_HANDOFF_20261002.md)保留原参数候选并更正阶段边界。

1. 先读本结项、PROJECT_STATE、DECISIONS D-012、Robert原邮件、工程与城市复核、18运行报告。无需重跑数据或开启SUMO。
2. 起草研究设计：优先M3600/R900为候选，R750作较轻参照；候选需求点不是已冻结参数。明确控制目标和M/R/U/X全请求群体成本、城市共享区暴露、请求与实际服务、未完成处理及可接受区的定义。
3. 设计标准ALINEA实现/占有率测量/执行器、匹配条件和独立种子/精度方案。旧11%目标与70增益等只能是Proposed工程初值，不作为已验证最优参数。复用已有baseline作设计/技术比较；17/23/42是已暴露数据，不称独立正式验证集。
4. simulation_engineer、data_analyst和只读scientific_reviewer逐项审查。若需要纯技术smoke或有限校准pilot，写明它回答的问题、预算和输出，单独获得运行授权，标签不得转成正式实验。它不重新开启已经完成的场景能力探索。
5. 方案经必要的用户/导师讨论后，只有用户明确批准才能写入/冻结EXPERIMENT_PROTOCOL。正式运行必须协议冻结且有对应运行授权；本次结项不授权新控制/正式仿真、参数扫描、发信或发布。
6. 正式结果允许“没有可行sweetspot”，不得为成功故事改参数、删失败或拼接不可配对数据。

当前状态：`exploration=COMPLETE_WITH_LIMITATIONS`；`formal_design=NEXT_NOT_STARTED`；`formal_protocol=EMPTY_UNFROZEN`；`formal_runs=NOT_STARTED`；`new_simulation_authorization=NONE`。用户要求的暂停继续适用于仿真执行。

## 7. 独立复审与文档核验

[本次最终科学复审](../../artifacts/stage6_capability_closeout_20261002_v1/FINAL_SCIENTIFIC_REVIEW.md)记录限定结项的PASS与限制；工程与data意见已纳入，不把技术核验单独当科学验收。

本次相关更新：PROJECT_STATE、WORKLOG、DECISIONS限定结项记录、README交接入口、旧新报告/交接的最新状态提示及本地Dashboard。旧原始数据、历史判定与EXPERIMENT_PROTOCOL保持；未向Robert发信、未写外部Page/Notion、未部署Dashboard。

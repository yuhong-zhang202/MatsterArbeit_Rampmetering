# Stage 6 P1：单一候选设计与验证注册草案

日期：2026-09-19。状态：**P1 设计交付与工程/数据/科学审查完成；候选与数值仍为 Proposed，待用户选择；未构建、未运行。**

## 1. 结论、主要问题与执行边界

推荐一个候选 **B：同 edge 的附加加速车道，通过安全换道并入两条连续主线车道**。不同时运行另一个几何选项，不调 Krauß/换道模型参数、不加控制器、不制造外部瓶颈。

唯一主要问题：**在同一候选几何、固定 M/U/X 需求和信号下，R 需求从 0 增至 720 veh/h 后，B 窗进入固定局部观测域的主线车辆，其遍历时间是否出现测量可以区分的正向变化？**

这里的主量是局部入口群体的描述性对比。R 增加同时改变城市道路与合流交通，两臂的局部入口车辆和随机数抽样也可能不同，不能称为纯合流因果效应。它不是控制试验，也不估计几何修复的因果收益。

R 送达、城市 U 时间负担、共享区暴露分别报告，作为解释与后续用途评估，不再组合成一个必须全部通过的成功门。即使两个 seed 都出现主线正差，也不自动关闭 `specific_obstacle`、证明 Breakdown/Capacity Drop 或解锁正式实验设计。

本次 P1 仅产出设计、表图、注册合同及专业审查。P2 实现、netconvert 构建、SUMO 运行分别需要后续明确授权；旧运行卡剩余预算不得挪用。原 D2 阴性和 seed23 的旧卡停止状态保持不变，新卡若使用 seed23 是独立登记的任务。

## 2. 为什么选 B，为什么不同时做 A

| 选项 | 具体机制 | 优点 | 局限 | 本次处理 |
| --- | --- | --- | --- | --- |
| A：修正右侧接入的节点合流 | 保留匝道直接接主线右车道，修正路径及不必要的跨左车道冲突 | 路径和储存变化较小 | 仍依赖节点接受间隙，不提供并排加速/换道空间；不能保证摆脱旧受限状态 | 保留书面比较，不实现、不运行 |
| B：同 edge 附加车道 | R 先进入 lane0，再安全换到主线 lane1/2；lane0 无下游连接 | 明确表达高速公路加速车道机制，便于观察沿程并入 | 改变路径、储存和换道机会；末端仍可能排队；效果未知 | 唯一推荐候选 |

P0 已观察到 R 末端长期等待且 B 内下游通过很少，并核实旧节点 R 向两个 M movement 让行。这说明 B 值得检验，不证明 A 无效，也不证明 B 一定恢复研究所需状态。

SUMO 官方资料支持上述附加车道末端无连接的建模机制及车道换道限制，但不提供本项目 300 m 的适用性证明。[Motorways](https://sumo.dlr.de/docs/Simulation/Motorways.html)

![旧结构与候选结构](../results/figures/stage6_recovery_candidate_revision_01/engineering/old_candidate_comparison_revision02.png)

上图旧版为已执行 compiled 几何；候选为输入设计示意，未编译。两者不能当作已经完成的干预对比。

## 3. 候选几何与所有伴随变化

坐标均采用**原始输入坐标（米）**；旧 compiled 图的 `(800,900)` 平移只用于对照展示。

| 字段 | Proposed 输入值 | 理由及核验 |
| --- | --- | --- |
| 原主线入口 | main_in=(-800,0) | 保留；M 实际 p100 入网 |
| 匝道接入节点 | freeway_merge=(600,0) | 保留节点位置，改变后继连接 |
| 附加车道末端 | merge_end=(900,0) | 新节点；名义加速区长 300 m |
| 主线出口 | main_out=(1400,0) | 保留；名义主线总跨度 2200 m |
| main_up | 2 lane，33.33 m/s，priority3，width3.2 m | 保留源定义，编译后复核实际长度 |
| merge_section | 3 lane，33.33 m/s，priority3，width3.2 m | lane0 为匝道附加 lane，lane1/2 为主线 |
| main_down | 2 lane，33.33 m/s，名义 500 m | 原 800 m 下游拆成 300+500；不能继续使用旧 pos700 观测点 |
| ramp_accel shape | (500,-15) (550,-5) (600,-6.4) | 加显式右侧终点，避免旧 shape 上延跨越主线；compiled 必须验证 |
| 城市/TLS/共享区 | 既有 nodes/edges/connections/TLS 源值保留 | 除源 hash，还需核编译结果，不能凭意图宣称不变 |

完整输入清单为 `results/tables/stage6_recovery_candidate_revision_01/engineering/` 中的 `candidate_nodes.csv`、`candidate_edges.csv`、`candidate_lanes.csv`、`candidate_connections.csv`、`candidate_routes.csv`。这些是设计表，不是可运行输入文件。

必须实现的合流连接：

1. main_up lane0 → merge_section lane1；main_up lane1 → merge_section lane2。
2. ramp_accel lane0 → merge_section lane0。
3. merge_section lane1 → main_down lane0；merge_section lane2 → main_down lane1。
4. merge_section lane0 **没有** main_down 连接；R 必须安全左换道。两条原主线 lane 都连续，不新增主线直行车道消失。
5. merge_section lane1 设置 `changeRight="authority"`，当前 passenger 不能从 lane1 进入 lane0。该限制也约束已并入的 R 返回 lane0，不是只限制 M。
6. lane0→lane1、lane1→lane2、lane2→lane1 保留默认安全换道机会。不得设置 `pass=true`、强制不安全换道、关闭安全检查或新增车辆参数。`acceleration` 属性不额外设置。

换道限制是明确的**网络通行规则变化**，会改变交互机会，不能称为纯技术细节；现有证据也未证明它是唯一必要选择。两条需求臂固定同一规则。其语义依据为官方 lane 属性定义。[PlainXML](https://sumo.dlr.de/docs/Networks/PlainXML.html)

300 m 的用途理由：在原 800 m 下游空间内留出一个有限可观察的并行合流区，并保留约 500 m 下游；以 27.78/33.33 m/s 计算名义行驶时间约 10.8/9.0 s。它不是校准长度、设计规范推荐、最佳值或安全间隙保证。编译 usable length 的 Proposed 工程范围为 [280,300] m，最多容许 20 m 节点裁切；超界回到设计审核，不能偷偷延长至行为阳性。

必须披露的伴随变化：R 可利用的存储增加、实际换道位置变为可变、ramp_mid 邻近节点裁切可能影响储存段、主线实际路长可能因内部连接变化、原下游观测点物理位置移动、lane1 右换道权限改变。构建后填入真实 compiled 差额，禁止用名义 2200 m 宣称实际路长完全等同旧版。

## 4. 唯一验证矩阵与固定输入

所有数值为本轮探索注册候选，未经经验校准，不是正式论文参数。

| 字段 | R0 对照 | R720 处理 | 解释 |
| --- | --- | --- | --- |
| 名义 qMain | 3200 veh/h | 3200 veh/h | 保留已观察 C 负荷，不同时扫 qMain |
| 计划 M 数 | 1333 | 1333 | 1500 秒内均值实际为 3199.2 veh/h，区别名义请求 |
| 名义 qRamp / R 数 | 0 / 0 | 720 / 300 | 最大限度简化有/无 R 的场景对照，不是剂量响应 |
| U / X | 360/180 veh/h；150/75 辆 | 相同 | 外生请求、signal、vType 保持相同 |
| seeds | 17、23 | 17、23 | 两个已见 seed，有限异质性检查，非 holdout/功效保证 |
| 需求 / 运行 | [0,1500) / [0,2700) s | 相同 | 不以阴性为由延长；Post 含延迟入网 |
| 三阶段窗 | Pre [0,300)、B [300,1500)、Post [1500,2700) | 相同 | B 不是经验证的平稳状态 |
| 时间步 / FCD / TLS | 1 s / 1 Hz / 1 Hz | 相同 | 保留现有动态分辨率；全车辆及内部 lane |
| E1/E2 | 新 9 E1 + 2 E2，30 s 输出 | 相同 | 合计 17 个 XML 输出角色；不能复用旧 14 角色检查器 |
| M 入口 | departPos100、best、max | 相同 | 保留 H2 实际上游遍历修复 |
| R/U/X 入口 | 既有 last/best/max | 相同 | 不强制入网、不代替记录入网延迟 |
| 车辆与控制 | 既有 technical_passenger/default行为，无匝道控制 | 相同 | 不调参制造目标现象 |

仪器精确合同见 `engineering/instrumentation_and_tls_supplement.json`：9 个 E1 的 lane/pos 固定在工程表；2 个 E2 的名义用途为 shared_approach 与 ramp_storage 全指定 lane，shared 终点238.8 m需编译保持核验，ramp_storage 终点用编译实际长度填实。E2 timeThreshold=1 s、speedThreshold=5/3.6 m/s、jamThreshold=10 m、friendlyPos=false，不与 FCD 0.1 m/s 停驶口径混用。TLS保留 offset0 与45Gr/3yr/9rG/3ry，movement0=R/U、1=X。

需求生成保留既有 number-flow；共同 flow 定义/身份规则必须相同，顺序 M,R,U,X，R0 省略零数量 R flow。同 seed 不保证改变车辆集合后 M/U 的微观随机抽样逐车一致；记录可能取得的实际 speedFactor/发车属性，但不能宣称完全共同随机数。不得为“匹配”暗改车辆随机模型。[SUMO Randomness](https://sumo.dlr.de/docs/Simulation/Randomness.html)

四条验证逻辑 ID 固定为 `P1B_R0_S17`、`P1B_R720_S17`、`P1B_R0_S23`、`P1B_R720_S23`。旧几何档案不能替代其中任何一条。技术 smoke 不计科学重复。

## 5. 观测合同与完整分母

### 5.1 主线 M

唯一主域：**main_up pos1200 → main_down pos200**，包含上游尾段、内部连接、整个 merge_section 及下游 200 m。主 cohort 为 B 内局部入域车辆，certain/possible 分开。每辆跨段 TT 只算一次；换道不剔除、不重复。两臂 cohort 可以不同，另列共同 M-ID 的描述性对账，不能偷偷用交集替换主群体。

辅助域：main_up [100,200)、旧 feeder [200,1200)、近合流 [1200,end]、全部内部 lane、merge_section、main_down [0,200)、固定背景 [200,400)、尾段 [400,end]。按实际 lane 归属，45 个 60 秒箱完整输出；空箱为 NA/no_contributors，不补零。main_down 编译长度必须大于 400 m，否则停止构建门，不裁剪观测域。旧 common [100,700) 不再可用。

跨界 `[last_before,first_at_or_after]`，TT 为 `[max(0,exit_lower-entry_upper),exit_upper-entry_lower]`；保留边界 cohort 的最不利纳入/排除界。lane 末端标签留在实际 lane，跨 edge 根据 route rank 推进。观察末仍未离域者使用最后一条有效 FCD 中确认仍在主域内的标签 `t_censor`，下界=`max(0,t_censor-entry_upper)`，上界=+∞；必须有可追溯 unfinished 状态且无身份观测缺口。末标签2699不能凭2700终止设定改为2700，不做完整案例替代。无解释身份消失或必要来源缺失属于证据错误。

主门以完整 B 为唯一判断窗。四个固定子窗 [300,600)、[600,900)、[900,1200)、[1200,1500) 及全部 60 秒时序用于展示时间差异，无 2/4 通过或持续 180 秒门。报告 certain/possible 人数、区间宽度、删失和分布；不设 400/100 人为样本门。非空且可确认存在的 cohort 是定义条件，不是充分样本量证明。

### 5.2 R 送达、并入与储存

R720 每 seed 300 个身份全部保留；两条 R720 验证合计 600 个计划身份。R0 的计划/事件计数为0；依赖非零 R 分母的率、均值以及 through 状态为 `not_applicable_zero_demand`，不是缺失。

分别记录入网、城市信号后、共享/分流、ramp_storage、ramp_accel、merge_section lane0、首次安全换至 lane1/2、首次 main_down、到达。进入附加车道不等于完成并入；主线 lane0→section lane1 的 edge 连接也不是换道。

换道事件只能按实际轨迹括区：若跳帧错过换道位置，仅记 route 可证明已完成、时间宽括区及位置 unknown，不能造精确位置。每箱输出 certain/possible 到达、离开、积存以及末端等待。网外等待单列，不能当作匝道存储。

不设 60 次通过或 10/20 箱门。B 内没有确定下游通过不等于没有 M/R 互动，R 可能已经在附加车道影响其他车辆。必须同时看附加车道进入、换道、下游通过三个状态。

### 5.3 U 与城市侧

每臂全部 150 个计划 U 为分母，报告入网延迟、路内完成/删失、截止 2700 秒受限系统时间：`max(0,min(arrival,2700)-scheduled_time)`。未完成 arrival 使用 2700；未入网车辆只有在可追溯计划时刻存在时才能计算，否则全计划均值 unavailable，禁止只取完成车辆。

已入网的 scheduled_time=`depart-departDelay` 仅为输出报告的计划时刻重建，不能称独立核实 number-flow 排程。分解截止时间内网外与网内部分。令 T=2700，s 为有来源的计划时刻：已入网时 `w=max(0,min(depart,T)-s)`，`v=max(0,min(arrival,T)-max(depart,s))`（未到达将 arrival 视为+∞）；未入网且 s 已知时 `w=max(0,T-s)`、`v=0`。输入时序须合法，逐车验证 `w+v=S`；s 未知时三者均 NA。不可用未截断 departDelay 冒充受限网外时间。报告两臂全计划均值差和量级，不设置实际重要性门。

共享区 R/U 同时技术停驶（≤0.1 m/s）报告标签总数、最长连续段、位置、涉及身份，以及与 M 子窗的重叠。不设 60 标签门；>0 只证明观察到该现象。R0/R720 改变城市负荷，因此 U 差异不能解释为纯回溢额外损失。

## 6. 固定决策树：分别报告结果，不用总成功印章

证据完整性：来源/hash/身份/schema/完整时域/范围/整数守恒必须通过。新 detector 的编译映射与实际覆盖需分别核实；P1 静态设计不是运行覆盖已验证。

记录完整的真实 collision/teleport 为 `complete_evidence_but_comparison_unsuitable_physical_event`，保留结果并停后续启动，不使用技术 retry；来源或观测缺失为 `evidence_incomplete`。emergency braking 独立记录，不自动当缺证/停止。真实排队、延迟入网和未完成不是技术故障。

每 seed 计算主 M 差值界 `ΔL=R720_lower−R0_upper`、`ΔU=R720_upper−R0_lower`：

| 条件 | 状态 | 能说什么 |
| --- | --- | --- |
| 两臂 cohort 可定义且 ΔL>0 | measurement_resolved_positive | 该局部群体对比方向超出测量边界；不是实用重要性或 Breakdown |
| 可定义且 ΔU≤0 | positive_response_not_supported | 这个有限对比不支持正方向；不是全局零效应 |
| ΔL≤0<ΔU | positive_response_unidentified | 测量界跨零 |
| cohort 不存在/可能为空，或不能形成合法界 | comparison_unavailable | 写明定义/观测/删失原因 |

整数时间步与精确有理数比较用于避免浮点微小误差改变方向；不声称物理测量精度提高。含无穷界使用扩展区间，不把 `∞−∞` 产生的 NaN 误判为通过；具体可推断/不可定义分支和测试见 `data/measurement_contract_revision04.md`。两臂下界有限，上界可以无穷；两臂都无穷上界时差值为[-∞,+∞]，不是NaN。

R 的通过状态独立：先排除 R0 零需求适用性（NA），只对 R720 分类；certain>0 为 `R_through_observed`；certain=0 且 possible>0 为 `R_through_timing_unidentified`；possible=0 为 `R_through_not_observed_in_B`，后者仍可能有辅助车道交互。U 均值差按正/零/负/不可用报告；RU 暴露独立报告。

两个 seed 完成后：双 positive → `positive_response_supported_at_two_registered_seeds`；双 not_supported → `positive_response_not_supported_at_registered_seeds`；一明确 positive、一明确 not_supported → `seed_dependent_response`；其余完整组合 → `partial_or_unidentified_response`。一个 positive、一个跨零不能称方向相反。有证据错误或物理停止则单列，未运行 seed 不缩小分母。

P3 接收向量 `{证据状态,物理适用性,两seed M状态及量级,R送达/并入,U全计划结果,RU暴露,时间差异}`。不以“两侧都看起来变差”自动宣布探索验证结束。

## 7. 顺序、停止与预算边界

拟定后续执行顺序（**本轮不执行**）：

1. P1 候选与科学字段提交用户选择；若用户改动关键值，先修订注册并复审。
2. 获 P2 离线实现授权后，按工程表实现隔离输入与新测量适配；完成小范围针对性离线验证，旧源码/档案保留。
3. 形成独立 netconvert 构建卡（输入、binary/argv/hash、次数、墙钟、磁盘上限、失败保留），获批后才编译。
4. 编译后填写全部 compiled 字段，独立检查城市/TLS保持、M连续、R安全换道路径、[280,300]附加长度、下游>400、权限、detector 与路径/存储差额。任何设计不符均暂停，不自动改参数。
5. 形成精确启动卡和总预算，获批后技术 smoke `R720/17`，采用完整 [0,2700) 时域及同一科学输入；smoke 不可用于调参、筛选科学方向或取消有效阴性验证。后续 validation 是单独 attempt，同输入/seed 的重复不增加科学重复数。
6. smoke技术合格后依次 `R0/17 → R720/17`，暂停独立数据复算与科学审查；若无技术/已登记物理停止，无论方向如何继续 `R0/23 → R720/23`。
7. 四条验证后独立复算与科学审核，把完整向量交 P3；无效或阴性不加扫描、不换seed、不延长2700秒。

后续结构上限建议：1 smoke + 4 validation + 全局 1 次同输入技术 retry，即最多 6 次 SUMO。只有瞬时环境/进程故障可按注册条件 retry；设计/配置错误需修卡，碰撞/teleport、排队、负结果、低送达均不能触发技术 retry。具体墙钟/空间估计、netconvert 次数、跨阶段项目累计消耗对账和全部 argv 属于 P2 启动/构建卡字段，当前 `pending_build`，不继承旧卡 120s/2GB 等数字。当前获准 SUMO/netconvert/TraCI/GUI 次数均为 0。

## 8. P2 必须完成的实现检查（不得让执行模型猜值）

| 检查类别 | 明确要求 | 不通过处理 |
| --- | --- | --- |
| 源与身份 | 精确绑定每个输入/output role；R0零流合法；四逻辑run/两seed固定 | 停止，不能glob猜输入 |
| 编译网络 | 输入表→compiled节点/lane/connection/request逐项映射；含所有内部lane | 设计不符回审，不能自改形状/路权 |
| 换道权限 | M不能进aux；R能0→1；1↔2可用；R并入后不能回0；aux无出口 | 修设计/构建卡，不能强制换道 |
| 完整人口 | M/R/U/X计划、入网、在网、到达、未入网逐类对账，残差0 | 证据错误或真实未完成分开 |
| 跨界/分母 | 半开窗边界、精确lane端点、跳内部lane、optional cohort、唯一车辆和lane换道 | 所有分支离线fixture一致 |
| 删失与无穷 | 未离域下界、无穷上界、双方无穷、cohort可能空、精确符号比较 | 合法扩展界按§6分类；仅cohort/测量无法定义才unavailable，不NaN通过 |
| R并入 | aux进入≠换道完成≠down通过；跳帧位置unknown；R0为NA | 不伪造事件或用E1计数替身份 |
| U全计划 | 150身份含未入网/未到达，受限时间分解一致，缺计划时间全均值不可用 | 不做完整案例替换 |
| 停止分支 | 数据缺失、物理碰撞/teleport、emergency warning、环境retry分别测试 | 不把科学阴性升级为retry |
| 独立复算 | 独立实现全部主域/差值/人口/R/U/子窗，不能导入生产计算作为oracle | 未解释差异0才推进审查 |
| 最终覆盖 | 所有预定run有终态；失败保留，预算追加/重启有记录 | 不减分母、不覆盖旧attempt |

工程逐项构建门见 [p2_build_verification_checklist.csv](../../results/tables/stage6_recovery_candidate_revision_01/engineering/p2_build_verification_checklist.csv)。新入口3个movement不得有非预期跨主线冲突或R向M让行冲突；compiled aux lane0 outgoing必须精确为0。若PlainXML猜出连接，必须经获批输入显式处理并重新构建，禁止手改compiled XML。

上述均是后续待实现检查，不宣称已通过。已有 P0 的77文件绑定与两个 endpoint 修复可作为回归背景；新几何不能沿用旧运行覆盖PASS。

## 9. P1 完成线、评审与用户选择

P1 设计交付完成：唯一推荐候选 B、唯一主要问题、具体输入表、39 个测量/科学字段和 4 个逻辑验证 run 已形成。design-critical 未填写项为 0；compiled hash/via/实际长度、真实 argv 与预算等 6 类后续工程项，均在 `p1_registration_draft.json` 中列责任人、关闭条件与构建/启动前门，保持 `pending_build`，不冒充已实现。

| 审查 | 结果 | 问题处理与局限 |
| --- | --- | --- |
| simulation_engineer | 静态设计与主文一致；25 项工程文件绑定通过 | 11节点/10edge/14外部lane/10连接静态可达；不等于compiled或运行可行 |
| data_analyst | revision04 39字段；23离线数学fixture通过 | 关闭无穷界误判、R0适用性、U受限分解、截尾来源等歧义；不是未来解析器全管线测试 |
| scientific_reviewer | PASS；开放Blocker/Major/required Minor=0/0/0 | 主问题措辞、2699/2700截尾两项required Minor已关闭；数值/几何仍需用户选择 |

审查撤回的早期数量硬门、原图caption裁切版以及数据revision01–03均保留作过程证据，不能进入执行。最终图revision02已逐张可视检查。独立科学代理复核工程25、data handoff2、data receipt7项绑定，并只读复算23数学fixture。

本次 SUMO/netconvert/TraCI/GUI 调用均为0；未改旧配置、原始数据、既有注册门、正式协议或 DECISIONS。此处的“完成”仅指 P1 方案交付，不表示新场景有效或用户已接受具体参数。

用户后续需要选择的是这一个候选及本注册问题/测量规则，**不是**批准已经存在的可运行网络或新仿真。关于适用性、控制保护目标与合理 Breakdown/Capacity Drop 的问题，仍按 P3 向 Robert 提交我们的设计与证据；本文件不代拟导师接受标准，也未发送任何消息。

权威数据口径为 `data/measurement_contract_revision04.md` 和 `results/tables/stage6_recovery_candidate_revision_01/data/measurement_fields_revision04.csv`（39字段）。数据revision01/02的数量硬门已被撤回；revision03已被revision04的语义与截尾补充取代，仅留审查历史，不得用于实现。

机器注册草案：[p1_registration_draft.json](../../data/processed/stage6_obstacle_20260913_v1/recovery_candidate_design_revision_01/p1_registration_draft.json)，`launch_eligible=false`、`authorized_starts=0`。科学审查及交付绑定由同目录 `p1_scientific_review.json` 和 `p1_final_delivery_receipt.json` 保存。

文件根：`data/processed/stage6_obstacle_20260913_v1/recovery_candidate_design_revision_01/`。工程表/图位于 `results/tables/stage6_recovery_candidate_revision_01/engineering/` 与对应 figures 路径；最终数据合同和审查记录由最终回执精确绑定。先前 data proposal 版本仅作审查过程记录，不能作为启动标准。

方法与已知边界置信度 High；候选工程可行性/科学设计建议 Moderate；未来能否解决障碍 Unknown。

# Stage 6 SG6-P：定点验证启动确认包

日期：2026-09-13  
状态：**Proposed；离线工程与数据复核通过，科学终审待本包确认；尚未授权或启动SUMO。**

## 1. 本次要批准什么

本包申请的不是正式实验，而是一次有停止门的探索性定点验证，用于判断 H2 补救场景能否同时呈现可研究的主线受损、匝道实际通行和城市共享区暴露，从而解决 `specific_obstacle`。只有后续 SG6-R 通过，才允许开始正式实验设计草案。

批准对象同时绑定：

- 完整启动卡：`data/processed/stage6_obstacle_20260913_v1/c04_launch_preparation_revision_03/proposed_launch_card.json`，SHA256 `6dad07d6862eb6dfd6ca5ffd4bd09ccffa3563ff63106b67a983dcbaba765067`；
- 稳定启动载荷：SHA256 `4f65deb5ee65eb23ff071d6b79e85d1afcff1dd12fd50242cc7ed07b2161a1d3`；
- 门控与停止规则：`data/processed/stage6_obstacle_20260913_v1/c04_launch_preparation_revision_03/launch_gate_policy.json`，SHA256 `d57cd0a14bbb5d38f1539c7bf2460191caebaa15964ef1d7b6a83217a3784eab`；
- 包清单：SHA256 `e17d06c6c8e4cbaa1eb7a205818ab02f412bd64b802533a5f37fb4e852c67137`；
- 工程回执：SHA256 `5c6d8e5959f1af8cb32d7c96b039710da6622d6031cb88c4bfc49359e99d9b5a`；
- 独立数据复核回执：SHA256 `8e3de44bd99a5476dd7366188e5a1b45539e79865e983df5307f38d57a14aa41`。

批准后只允许按下列顺序逐个启动，不允许并发、换参数、换seed或临时增加条件。

## 2. 矩阵和预算

| 顺序 | 条件 | seed | 用途 | 预定attempt |
| ---: | --- | ---: | --- | --- |
| 1 | V1-ML | 17 | 技术 smoke，不作科学证据 | `S6_V1_ML_S17_attempt1` |
| 2 | V1-ML | 17 | 验证 | `S6_V1_ML_S17_attempt3` |
| 3 | V1-C | 17 | 配对验证 | `S6_V1_C_S17_attempt1` |
| 4 | V1-ML | 23 | 验证 | `S6_V1_ML_S23_attempt1` |
| 5 | V1-C | 23 | 配对验证 | `S6_V1_C_S23_attempt1` |

硬上限为6次SUMO启动：1次smoke、4次验证，以及全块共享的1次同参数技术重试。每次最多120秒，总墙钟最多720秒；每attempt最多2 GB，新归档总计最多12 GB。失败或超时的进程启动也计数。netconvert、TraCI、GUI均为0。watchdog是轮询后终止进程的控制机制，不是操作系统级硬资源配额。

## 3. 三段执行和强制停止门

### D1：只运行 smoke

运行 `S6_V1_ML_S17_attempt1` 后立即暂停。工程、数据和科学三方必须基于真实输出和哈希签署门回执，不能只把JSON中的 `accepted` 改成 `true`。

必须确认：真实source-map/receipt身份正确；M实际从登记的约100 m位置进入且没有fallback或错位；真实FCD确实记录入口和登记的feeder与common观测域覆盖，不能只检查route；TLS、link和检测器已加载；完整时间端点存在；14类运行XML均非空、结构和根节点正确并含所需记录；输出及smoke专用技术测量回执已归档并绑定哈希。合法未完成或未穿越状态必须明确保留，并按既定截尾与资格规则处理，不新增“每辆车必须到达”的门。该回执不得调用会拒绝smoke的科学分析入口，也不得进入352项主规则或14项敏感性分母。smoke结果不得替代ML17验证，也不得作为Q2–Q4科学证据。

技术故障只有符合预登记定义时才可消耗全局唯一retry。身份、证据或入口资格错误立即停止，分类为 `blocked_by_evidence_error` 或 `not_resolved`，不进入D2。

### D2：运行首个配对单元

smoke通过后，依次运行ML17验证和C17验证，然后再次暂停。必须确认二者身份合格且构成同seed配对。数据代理必须从两条真实原XML独立重建核心计量、旅行时间区间边界与截尾状态、共同支持块、主判据、Q1–Q4、R通行、R/U共享区以及7项敏感性结果；科学复核代理审查证据和规则判定后，二者均通过才能签署此门。阴性、未配对、无限上界和缺证据必须原样保留。

停止规则固定如下：

- seed17全部必需检查通过：进入D3；
- 完整、合格的数据中任一必需科学门或敏感性门失败：记为 `not_resolved` 并停止，不运行seed23，因为预登记的双seed成功标准已不可能满足；
- 证据链错误：记为 `blocked_by_evidence_error` 并停止；
- 合格技术故障：可消耗唯一共享retry；无retry或重试仍失败则停止。

### D3：完成第二个seed

D2通过后，依次运行ML23与C23，并对两个配对seed执行完整分析。两seed的全部必需规则和固定敏感性均通过，只表示可以提交SG6-R复核，不自动宣告障碍已解决。若失败，保留阴性结果并按规则关闭，不追加需求点或第三个seed。

## 4. 不可变更项与最终出口

批准范围内不得改变输入、阈值、seed、attempt映射、SUMO可执行文件、预算、停止规则或任何绑定哈希。任何变化都使本批准失效，必须制作修订包。

执行结束后交付：逐attempt不可变归档与回执、预算journal、来源和身份核验、主规则与14项敏感性结果、异常及失败全集、工程/数据/科学三方复核，以及SG6-R候选结论 `resolved_for_baseline_design`、`not_resolved` 或 `blocked_by_evidence_error`。只有用户另行接受SG6-R后，才进入正式实验设计草案。

## 5. 当前离线证据的边界

工程测试为49个最终测试方法（含此前28个）；数据侧278项主检查、56个XML负例和26项补件检查存在重叠，不能合称为360个独立科学验证。当前正向执行链只由synthetic fixture验证；三次ML17分析来自同一个历史physical run，不能当作三个重复。真实SUMO输出schema、运行性能、信号传递和V1实际入口覆盖仍未验证，因此必须保留D1 smoke停止门。

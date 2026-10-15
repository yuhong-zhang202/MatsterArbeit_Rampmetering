# Issue12 独立数据预启动审查 V2

2026-10-12。结论：PASS，仅限当前离线数据准备；无真实新运行、安全或服务资格。Context Preflight读取AGENTS／当前STATE／DECISIONS／WORKLOG，协议0B、未冻结；Issue12工程准备进行中，既有Stage6结项、A1 UNRESOLVED、Candidate A NOT_QUALIFIED保持。未改旧raw、执行器／guard／卡片／研究设计。

## 实际核对

工程ENGINEERING_BINDING_V1.json的105文件SHA全部匹配；三张当前卡及各sources／prepared／inherited输入SHA匹配。R300 4ddbe480…、R900 afbe76e1…、R600 37d8e820…均PREPARED_NOT_RELEASED；输出父目录不存在，资源300s／启动60s／300MB／余量5GB不变。执行代码为baseline20e5e83上的未提交精确快照，不能声称历史commit测试了新实现。全部现有工程失败／精度准备失败／源前像保留。本审查读取工程7个method的分段PASS证据，不复跑工程套件，也没有调用prepare／environment／SUMO／TraCI／生成权限。

当前policy将300–900映射五档、24s周期quota2–6。固定诊断r_ALINEA=null，r_final／pending／cycle-applied各自积分；量化差和应用延迟不同。实际N对同ACK多个G和黄灯额外车全量计数，无quota硬截断。E是完成周期时累计的请求quota，部分周期E0不伪称完整窗口；未观测所有派生值null，实测零保留0。前述事实是代码检查，尚无实际达成证据。

桥接在quota ACK后启动Y5，或17G截止进入Y5；首次实际red ACK延长至固定24s终点，最低总red2s，首次red检查点动态而非固定1207；1272结束前不执行第四G。local yellow screen只为完整绑定的局部工程筛查，不是未来原生安全证明。条件WAIT／entry前后检查沿用受保护机制，退出车辆最后运动只在EOF后补审，不声称在线全覆盖。

## 新独立数据工具及实际小回归

`audit_data_V2.py`无仿真导入，只接受已独立重建的入口ID／时间／motion与post-step率链。它独立重算C、pending、applied、E、N和派生差，拒绝重复／漏计／未绑定／非顺序ACK／相位类型错误；不把源码ledger自报告当原始入口证据。无观测、零、部分和同ACK多G／黄额外车已用极小公开fixture验证。运行`python3 data/processed/issue12_alinea_actuation_20261012_v1/test_data_V2.py`，两个test methods实际PASS（0.001s）；这些数据fixture不代表工程实际fake loop，更不代表原生车辆动力学。

终点工具联结唯一before-only arrived身份、类型／末路段合法lane、ACK dt1与precision8 tripinfo。允许合法末步换道，不要求arrivalLane等于before lane。SUMO1.26 normal arrival字段绑定interval BEGIN，物理运动仍为(begin,end]；不取分数arrivalTime作差分分母。arrivalSpeed±0.5e−8舍入区间和before速度差用于检查−4.5−1e−6m/s²；跨阈值／缺失／重复／vaporized／不合法lane／分数时间UNKNOWN，明确违反为FAIL。PASS／FAIL／舍入UNKNOWN／缺失／重复等极小组合已运行。依据为工程和[方案中的官方源链](../../../docs/development/RAMP_METERING_SIGNAL_POLICY_DECISION.md)，不声称本审查重新读取全部官方源码。

V1两个methods曾真实PASS，但采用分数arrival fixture和排除BEGIN的错误时间条件，不能覆盖真实SUMO arrival schema。V1源码／fixture／PASS日志与V1_LIMITATION_RECEIPT.json保留；V2明确修正，不将旧PASS隐去或包装成真实native错误。未改runtime绑定，V2仅新数据reader。

## 真实运行后必须完成的门

暂无raw；当前工具不是完整自动runtime审计器。首轮后需按精确最终manifest冻结全部输入，独立FCD储存车道→internal入口／运动TLS／每秒ACK逐ID核对，验证所有已请求黄绿／动态red／实际首次red检查点、最终EOF四流、WAIT及entry前后联合字段、yellow局部覆盖。缺测／未经重建入口不能以自报告或exit0代替；若数据schema不符，保留首次失败并做有界版本修正。

before-only必须与arrived IDs一一相等，逐车terminal metadata及最终tripinfo唯一完整，所有末步缺口PASS后才能称指定覆盖范围内观测通过；UNKNOWN阻塞下一诊断。planned demand需区分截至终点已到期未插入与未来计划；unfinished、实际供给、队列及shared-road仅诊断记录，不推断正式主线／城市效应。任何阶段UNKNOWN／危险STOP保留实际前缀账，不填未观测零。短72s服务误差不能推出长期300–900资格。

建议进入只读科学预启动审查；此前没有canonical release，不授权启动。先且仅R300，后续须工程→独立数据→科学运行后门与明确权限。下一步建议不构成执行授权。

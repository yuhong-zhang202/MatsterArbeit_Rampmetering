# Issue12 FIX01 R300 独立实际数据复核

2026-10-12。结论：**指定技术观察与独立数据门PASS；当前72s单seed诊断不等于长期rate qualification或普遍安全。** 没有本数据任务新SUMO／TraCI／测试矩阵、raw／guard／政策修改。Context已刷新AGENTS、STATE、DECISIONS、WORKLOG、0B未冻结正式协议；接收工程已冻结的第二次Issue12运行，不改变Stage6结项、A1 UNRESOLVED或Candidate A NOT_QUALIFIED。

## 版本与范围

CA_I12_QUOTA_R300_S17_FIX01／card9f914d8b307df524d47b56999280b8a58fc76da13d4d57f4f743cdf2fe0478ee；修复工程6520b77d…的未提交精确源快照，baseline20e5e83不是新实现已测试commit。82原文件163,352,995B逐SHA匹配manifest c63436ebcaf75efc969c8778c3cde11de6181b41c7ce9a13a2536d9e4e268ea6，工程交付清单全部匹配。旧失败与历史数据不混入。

R300指固定服务指令300veh/h，需求始终M3600/R900/U360/X180、seed17、dt1；r_ALINEA=null。此次native及CLI退出0，监控清理126.599176s／whole CLI127.020932s，均据实际工程receipt而非数据脚本新测，未触发预算。Issue12累计2/3启动，900尚需实际三方门，不自动启动。

## 五项独立实际门

| 门 | 已核查实测 | 边界 |
|---|---|---|
| 完整FCD/TLS/ACK及入口 | 1272帧FCD完整身份／lane／precision8速度与post-state匹配；2544 ACK两阶段逐秒绑定；独立storage→internal重建六入口与原计数完全一致 | FCD label是BEGIN、tuple为运动后；入口区间不虚构亚秒 |
| 完整72s率链／周期／时钟 | C=pending=applied=E=N6，量化／积分延迟及E−N0；每24s周期实际G4/y5/r15、N_G2／N_y0／N_r0；每步有storage供给 | 相等只证明此短诊断账与实测；不替代多个服务窗口、fresh seeds或动态ALINEA率链 |
| red setter及checkpoint | duration六条ATTEMPTED／READBACK_VERIFIED在1210／1234／1258，remaining14，nextSwitch到1224／1248／1272；firstred BEGIN1209／ACK1210，checkpoint字段及同期账匹配；最终EOF绑定 | native真实duration已执行，不再是fake；checkpoint时日志provisional，至最终EOF才能补足范围 |
| 全部末步到达及安全观测 | before-only=arrived，1335唯一正常tripinfo联结，BEGIN时间／类型／路由终点合法lane／precision8速度差全部PASS；common速度差和native实际加速度最低−4.5m/s²；native碰撞／teleport计数最大0 | 离网补审为运行后，不宣称在线全覆盖或未来原生安全；异常／舍入straddle／缺测UNKNOWN会阻后续 |
| WAIT／yellow／日志／身份供给 | 21条件WAIT逐ID/time/mode/actual-speed查询及6入口before/after核对；三个yellow event1204/1228/1252完整local ID／位置／速度／车长／decel／停车筛查重算；2547原生日志区间fragment及prefix哈希到EOF一致 | WAIT帧可能重叠，非21独立事件；黄灯屏幕是局部工程分类；父CLI兼容提示仍不属于四原生日志在线分类 |

六入口：R0(1200,1201]、R1(1203,1204]、R2(1224,1225]、R3(1227,1228]、R4(1248,1249]、R5(1251,1252]，全为G；12s G、15s y、45s r真实观察，黄／红零是实测零，不是未观测补零。第四G未执行。周期24/48s字段为恒定指令的request age，不解读为新命令延迟；率积分延迟0。

截至ACK1272，depart<1272的到期计划M1272/R168/U128/X64，实际插入M1272/R100/U100/X64；到期未插入M0/R68/U28/X0，未来M1728/R432/U172/X86另列。unfinished网内M77/R97/U23/X4，不忽略R/U源等待或把未来计划写成failed insertion。固定R需求900与服务指令300明显不同；不得称本轮研究效果或全网成本已验证。

原queue-export最后BEGIN1271的各原始length字段及ACK1272 shared-road R/U逐类车辆数、实测静止数与速度范围见SUPPLEMENT_RECEIPT_V1.json；描述现有tuple，不新增科研低速阈值，不唯一归因物理回溢或ALINEA效果。

## 数据执行、失败保留与下一步

复用已冻结audit_data_V3；新run-specific V1首次实际FAIL是checker把provisional范围误合成checkpoint status，实际源把它分为status和log_scope。V1源码／日志／failure receipt原样保留。V2仅严格映射真实字段，另外绑定first-red BEGIN／同期账，未改raw／runtime／放宽门。实际命令`python3 data/processed/issue12_alinea_actuation_20261012_v1/CA_I12_QUOTA_R300_S17_FIX01/revision01/audit_actual_V2.py` PASS约1.88s，未复跑工程套件。必要末帧shared及工程delivery哈希补核PASS。原始证据及可复算输出见FINAL_DATA_BINDINGS_V1.json。

本轮支持“所选执行政策在此R300短窗实际放行双车且完整周期／日志补审可运行”的工程判断，不隔离G／Y变动的独立因果，也不声称政策普遍合格。建议科学审查是否用剩余一次R900固定服务指令边界诊断，检验quota6能否在17G截止／Y5／最低red2内实现；这有明确服务域问题，而非追加预算或调参追求PASS。必须精确新卡／权限／三方预启动；任何真实危险或UNKNOWN立即停止。R600因总启动预算SKIPPED，900仍NOT_TESTED，正式协议未冻结。

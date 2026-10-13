# G5/Y3 日志审计器适配与运行审查交付

2026-10-13。基线 `63af3b4166b2582cb916877630706d1ff933be7a`。用户已认可上一轮离线候选，授权本轮最小审计适配、离线验证、工程／数据／科学审查及完整绑定卡；**本轮无 SUMO 运行授权**。[原始授权记录](../../artifacts/t10_g5_y3_audit_ready_20261013_v1/USER_OFFLINE_AUDIT_SCOPE_V1.json)。

## 本轮范围

新增隔离的 `scripts/t10_g5_y3_audit_20261013_v1/` 审计器，以及对应新02身份的 profile／薄 bridge／测试。旧01卡及73项来源、G4审计器、900档、原始数据和旧失败记录保留。G5/Y3配时、车辆模型、种子和安全阈值未改变。正式协议仍为空且未冻结。

新审计器从 FCD、TLS、ACK 和相位请求独立核对实际放行、连续转相与时刻、两条关绿路径的红灯补时和动态首红检查点；区分 requested／mapped／applied C、完整周期名义E、实际全部入口N以及partial／未观测null。合法的红灯车尾清线与新的红灯front入口分开，额外黄灯入口仍计入N。

保留完整车尾到实际清线、接收9+1.1、制动、碰撞／警告、正常离网precision8 BEGIN、日志字节/hash/EOF及缺失UNKNOWN检查。NUM默认严格，不继承旧受限例外。旧日志未保存的模式、动力学实际值和active／loaded／pending身份，现由新02桥接追加before／after日志，复用原读取及FrameCache；审计器按time/world/type/route逐帧核对。原生私有vsafe、RNG分支和源码—二进制等价仍未证实。

## 版本和审查发现

工程V2先完成6个重点离线方法；初版source/card和测试前像按版本保留。独立数据审查发现F01：逐条黄灯记录检查缺少与全部已观测firstY的集合覆盖绑定；F02：最后额外PRE日志接线需要受影响回归。[发现原件](../../data/processed/t10_g5_y3_audit_ready_20261013_v1/data_review_v1/DATA_FINDINGS_V1.json)。

F01进一步定位为new02截止路径已执行原adapter鲜活筛查，但未写独立journal。修复只调整日志：早关尝试保留为attempts，成功firstY prepare记录唯一definitive筛查；审计器要求已观测边界恰好一份记录，保留尚未观测／UNKNOWN／STOP前缀事实，不伪造未来Y。原公式、动作顺序和安全阈值保持。

工程V3已冻结，独立数据已复核并关闭F01/F02，当前待干净checkout和数据／科学最终门。[工程修复报告](../../artifacts/t10_g5_y3_audit_ready_20261013_v1/engineering/implementation_v3/ENGINEERING_FINDINGS_REPAIR_REVIEW_V3.md)。

- 当前唯一卡：[UA_T10_G5Y3_FIXED750_S17_02 / packages_v3](../../artifacts/t10_g5_y3_audit_ready_20261013_v1/engineering/packages_v3/UA_T10_G5Y3_FIXED750_S17_02/card.json)。SHA-256 `b84cb63eb49845759bbc259d7ce2a19a64b62479620be109b749e3dd073e2e6f`。
- 87项完整源摘要：`2b3a960ee27b2f1802760805f43108c471ff73a87ed300a448c98b3987e4e616`。工程41文件binder `1c707af1c52aae072814a60b7ceea181a7e6103a56afe7d1e63941e3be0a02b3`。
- 原01卡不改；新02未释放初版及packages_v2、源码前像与旧binder都保留，但当前profile拒绝旧路径，只有packages_v3可进入未来精确审批。
- 三个受影响方法PASS17.500s；随后真正deadline fixture只有1个实际入口并断言MAX_GREEN_DEADLINE，及新reader with-open后只复测同桥接方法PASS16.906s。首次ResourceWarning未屏蔽，原log和前像保留。五个原方法AST未变，复用既有证据。
- 生产桥接两路径实测于XML假连接，不能视为真实SUMO安全／服务结果。缺、重复、错时、额外黄灯记录及prepared-unobserved前缀核查；额外PRE日志缺失/重复/time/ID负例通过。data独立静态check_delivery_v3 exit0，不重复套件或旧raw。

本文件最终按真实回执更新，不把假日志、计划或源码检查写成实际仿真结果。

## 后续运行边界

未来一次02诊断及1270终点、300s／300MB等资源仍是待审提案；当前无canonical授权、release或新raw。所有新实际N、黄灯安全、车尾及服务结果为null。完整运行审查包通过后，也必须由用户明确批准精确卡／源码／资源才可启动。保持异常／未知停止，不自动重试，不把短诊断当资格或正式实验。

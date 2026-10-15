# G5/Y3 日志审计器适配与运行审查交付

2026-10-13。**离线完整包已完成，可供用户运行审查；本轮零SUMO。** 基线 `63af3b4166b2582cb916877630706d1ff933be7a`。用户已认可上一轮离线候选，授权本轮最小审计适配、离线验证、工程／数据／科学审查及完整绑定卡；**本轮无 SUMO 运行授权**。[原始授权记录](../../artifacts/t10_g5_y3_audit_ready_20261013_v1/USER_OFFLINE_AUDIT_SCOPE_V1.json)。

## 本轮范围

新增隔离的 `scripts/t10_g5_y3_audit_20261013_v1/` 审计器，以及对应新02身份的 profile／薄 bridge／测试。旧01卡及73项来源、G4审计器、900档、原始数据和旧失败记录保留。G5/Y3配时、车辆模型、种子和安全阈值未改变。正式协议仍为空且未冻结。

新审计器从 FCD、TLS、ACK 和相位请求独立核对实际放行、连续转相与时刻、两条关绿路径的红灯补时和动态首红检查点；区分 requested／mapped／applied C、完整周期名义E、实际全部入口N以及partial／未观测null。合法的红灯车尾清线与新的红灯front入口分开，额外黄灯入口仍计入N。

保留完整车尾到实际清线、接收9+1.1、制动、碰撞／警告、正常离网precision8 BEGIN、日志字节/hash/EOF及缺失UNKNOWN检查。NUM默认严格，不继承旧受限例外。旧日志未保存的模式、动力学实际值和active／loaded／pending身份，现由新02桥接追加before／after日志，复用原读取及FrameCache；审计器按time/world/type/route逐帧核对。原生私有vsafe、RNG分支和源码—二进制等价仍未证实。

## 版本和审查发现

工程V2先完成6个重点离线方法；初版source/card和测试前像按版本保留。独立数据审查发现F01：逐条黄灯记录检查缺少与全部已观测firstY的集合覆盖绑定；F02：最后额外PRE日志接线需要受影响回归。[发现原件](../../data/processed/t10_g5_y3_audit_ready_20261013_v1/data_review_v1/DATA_FINDINGS_V1.json)。

F01进一步定位为new02截止路径已执行原adapter鲜活筛查，但未写独立journal。修复只调整日志：早关尝试保留为attempts，成功firstY prepare记录唯一definitive筛查；审计器要求已观测边界恰好一份记录，保留尚未观测／UNKNOWN／STOP前缀事实，不伪造未来Y。原公式、动作顺序和安全阈值保持。

工程V3和数据V3是历史检查点，F01/F02已关闭；后续科学发现和V4修复见下文。[工程修复报告](../../artifacts/t10_g5_y3_audit_ready_20261013_v1/engineering/implementation_v3/ENGINEERING_FINDINGS_REPAIR_REVIEW_V3.md)。

- 当前唯一卡：[UA_T10_G5Y3_FIXED750_S17_02 / packages_v4](../../artifacts/t10_g5_y3_audit_ready_20261013_v1/engineering/packages_v4/UA_T10_G5Y3_FIXED750_S17_02/card.json)。SHA-256 `18774ee7aba5319b9947cf6c817c29db00339e7b5f52bb2abef509cf4313755e`。
- 87项当前完整源摘要：`4deb99f4a6c0b053d810d3b61123a5fff8a15df09cd9cd659e2b4f39bff9fd40`。工程V4的37文件binder `65fa264562e4a721e91c7eb484191b3f6c00a0904e58624b10a6ee379aa8225a`。
- 原01卡不改；新02未释放初版及packages_v2/v3、源码前像与旧binder都保留，但当前profile拒绝旧路径，只有packages_v4可进入未来精确审批。
- 三个受影响方法PASS17.500s；随后真正deadline fixture只有1个实际入口并断言MAX_GREEN_DEADLINE，及新reader with-open后只复测同桥接方法PASS16.906s。首次ResourceWarning未屏蔽，原log和前像保留。五个原方法AST未变，复用既有证据。
- 生产桥接两路径实测于XML假连接，不能视为真实SUMO安全／服务结果。缺、重复、错时、额外黄灯记录及prepared-unobserved前缀核查；额外PRE日志缺失/重复/time/ID负例通过。data独立静态check_delivery_v3 exit0，不重复套件或旧raw。

本文件最终按真实回执更新，不把假日志、计划或源码检查写成实际仿真结果。

## 后续运行边界

未来一次02诊断及1270终点、300s／300MB等资源仍是待审提案；当前无canonical授权、release或新raw。所有新实际N、黄灯安全、车尾及服务结果为null。完整运行审查包通过后，也必须由用户明确批准精确卡／源码／资源才可启动。保持异常／未知停止，不自动重试，不把短诊断当资格或正式实验。

## 历史V3公开回归与数据审查

实际测试检查点：`041632a840c69e1a2dc191575e70dcf68a014b17`。干净checkout的当前8方法全部PASS，unittest耗时17.052s、外层17.305225417s；raw前后只有`.gitkeep`、Git仍干净。本机已有venv及安装文件哈希复用，无安装或SUMO version进程。[完整回执与作用范围](../../artifacts/t10_g5_y3_audit_ready_20261013_v1/portability_v1/CLEAN_CHECKOUT_RECEIPT_V1.json)。这不是完整新配置native integration、另一台机器验证或真实安全/服务结果。

独立data静态check_delivery_v3实际exit0，核41工程binder、87源/输入、五个V2 live变更的历史前像、原73/01/900不变及当前测试/卡/回执一致。最终结论 **GO_FOR_RUN_REVIEW_PACKAGE_ONLY_NOT_EXECUTION_AUTHORIZED**，F01/F02均解决、无未解决实质数据问题。16文件binder `f4b7273e17ff4381166abe069f2463ca963d2f1fba7fec88b335530aaf2d1573`。[数据最终报告](../../data/processed/t10_g5_y3_audit_ready_20261013_v1/data_review_v1/DATA_FINAL_REVIEW_V3.md)。没有重复套件或旧raw重审；旧警告、发现、probe及所有版本保留。

## 科学Major与V4最小修复

科学V3暂不给完整包GO：原PRE已保存loaded/pending，但journal仅自洽检查；同时删池ID与state行仍可能通过。非空组合回归在旧V3源码真实FAIL；V4的BEFORE/额外PRE精确join原PRE池，AFTER有下一同刻PRE时同样独立对齐。**末AFTER没有下一PRE时，仅检查单日志内的非active池，不声称独立验证其完整性。** 活跃车辆仍与world核对。未增加getter、动作或安全数学证明；旧FAIL、V3卡/前像、8PASS、原警告和Major均保留，F01/F02不重开。[科学发现](../../artifacts/t10_g5_y3_audit_ready_20261013_v1/science/SCIENTIFIC_FINDING_NONACTIVE_POOLS_V1.md)、[V4工程修复](../../artifacts/t10_g5_y3_audit_ready_20261013_v1/engineering/implementation_v4/ENGINEERING_NONACTIVE_POOLS_REPAIR_V4.md)。

V4只复测三个受影响方法PASS0.239s；随后对实际代码检查点 `8b3a879aeb2a9e6f4acf5c8cdb317d3e1572ea84` 做一次干净checkout当前9方法，全部PASS17.279s（外层17.443157958s）。前后raw只有`.gitkeep`、Git干净，卡和87源匹配；复用本机已有venv，不是异机环境验证，不是完整native integration或安全/服务证明。[当前回执](../../artifacts/t10_g5_y3_audit_ready_20261013_v1/portability_v2/CLEAN_CHECKOUT_RECEIPT_V2.json)。

V4独立data已冻结：24文件binder `27b039dc789c921a2d66320db147421370f496313ff8227f6ce8e95955e9b2e3`；报告SHA `c6ad429227879d424b200388ec57b054a8bb1065a06c8b3baa28dd0252a784d4`，结论 **GO_FOR_RUN_REVIEW_PACKAGE_ONLY_NOT_EXECUTION_AUTHORIZED**，无新增实质问题。独立check_delivery_v4只执行一次exit0，未重跑套件或旧raw。[数据当前最终报告](../../data/processed/t10_g5_y3_audit_ready_20261013_v1/data_review_v1/DATA_FINAL_REVIEW_V4.md)。科学只读V4终审已完成，结论同为 **GO_FOR_RUN_REVIEW_PACKAGE_ONLY_NOT_EXECUTION_AUTHORIZED**，上一nonactive池Major关闭、F01/F02保持关闭，无未解决交付Blocker/Major。停止离线扩展，交用户审查。[科学最终回执](../../artifacts/t10_g5_y3_audit_ready_20261013_v1/science/SCIENTIFIC_FINAL_REVIEW_V4.md)。

## 运行审查需保留的限制

- 新日志的只读调用、体积及耗时尚未实测；未来可能因300s/300MB上限停止。旧750的−4.501事件仍可能触发严格停止，本轮不沿用旧受限例外。
- private vsafe/RNG/原生分支、源码与实际二进制等价、未来G5状态和真实reader端到端集成未验证。
- 只有公开fake／负例离线证据，02实际放行、转相、车尾、终端离网及EOF均未观测。最后AFTER非active池为单来源限制。
- 用户认可离线包不构成native授权，资源和1270终点仍为提案。未来须精确卡/源/资源批准及canonical三方release；异常或UNKNOWN停止，不自动重试。
- Candidate A仍NOT_QUALIFIED、A1仍UNRESOLVED；Stage6既有结项保持，正式协议未冻结、正式实验未授权。原900档和所有旧结果保持。

## 用户运行审查与后续交接

1. 审查本报告、V4工程／数据／科学回执、当前packages_v4卡及87源摘要；旧02卡与01不能替代当前卡。
2. 当前拟议身份为`UA_T10_G5Y3_FIXED750_S17_02`，M3600/R900/U360/X180、seed17、dt1不改；指令750、映射720、T10、Gmax5/Y3/redmin2、quota2，七个计划完整周期至1270。绿灯可因实测quota提前结束并补红；计划E14不是实际N14。
3. 本轮只交审查。若用户以后批准精确版本／卡／资源和严格NUM，才写新human依据、绑定授权及三方canonical release；不得沿用旧卡／剩预算／受限数值例外。bridge启动门会拒绝缺失或未绑定权限，未创建新raw。
4. 获准后未来一次native诊断结束或异常停止，冻结原始manifest，再由新reader用`--manifest`、`--card`及新的processed `--output`审计。任何UNKNOWN/STOP返回非零，不覆盖结果；再完成工程→数据→科学实际post审查。历史−4.501可再次严格STOP，不自动重试。
5. 新真实日志若出现覆盖缺口或超预算，应报告具体已观测前缀与未观测部分；不得用离线PASS补齐。取得技术观测仍不等于全域安全、服务资格或正式实验许可。

Documentation Impact Check：更新PROJECT_STATE的当前状态、WORKLOG的实际工作和发现、README的当前卡路径及本报告；DECISIONS、EXPERIMENT_PROTOCOL、AGENTS、导师记录、论文结构与上游PR均未修改。仅本地交付，未推送GitHub；无新Issue/PR/合并。本次下一位接手为用户/Chat审查，建议不构成执行授权。

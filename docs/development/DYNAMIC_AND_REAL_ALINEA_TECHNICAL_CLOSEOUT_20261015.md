# 动态执行器与真实 ALINEA：有界技术节点收口报告

2026-10-15。**已批准的最小动态验证及同版本短真实 ALINEA 技术节点完成，待用户／Chat审查。停止追加本轮诊断。** 不是长期、全范围、安全或服务资格通过；总体`NOT_QUALIFIED`、A1 `UNRESOLVED`、既有Stage6结项及空且未冻结的正式协议保持。没有正式实验或新的研究决策。

## 1. 目标、权限与最小解决方案

目标是让真实放行跟随**原始ALINEA请求的累计量**，不是只跟最近档名义流率，也不是要求每秒请求量等于整数车辆数。

既有累计执行器保留原请求积分C，使用独立真实车辆入口N，在完整周期边界根据C−N选择既有8–24秒周期包；每包2辆是待实际核查的计划，不以名义配额替代N。原30秒ALINEA公式、目标11%、增益70、限幅300–900及车辆模型未改。这些是技术诊断输入，不是已调优或正式冻结的ALINEA参数。

本轮最小补项是解除两项不适配的**工程前置约束**对动态验证的阻断：

- 额外1.1m查明为项目历史工程裕量，未找到官方要求或标定依据。获批后仅在current-following中改为保留告警，原生同参数query底线仍硬停止；新绿灯准入严格检查保持。query不是未来安全证明。
- 对输入完整且联合绑定、但原停车／清尾充分见证未成立的黄灯，仅在获批独立诊断模式交由SUMO原生相位机制观察；原UNKNOWN和数值保持，未改写成安全PASS。身份／模式／动力学／信号／车辆覆盖／接收检查和运行后异常／UNKNOWN停止仍保留。

SUMO官方说明原生黄灯下车辆根据制动可行性选择停车或通过；它不保证本项目全部状态安全。参见[Traffic Lights](https://sumo.dlr.de/docs/Simulation/Traffic_Lights.html)、[Safety](https://sumo.dlr.de/docs/Simulation/Safety.html)及[已固定1.26源码](https://github.com/eclipse-sumo/sumo/blob/fa7df22d7f1c4ae245192ecc32410a49f1ffb2a3/src/microsim/MSVehicle.cpp#L3711-L3727)。源码与实际二进制／编译选项等价性未验证。

直接批准为“批准合同、实施及有界运行”，见[批准记录](../../artifacts/dynamic_yellow_contract_proposal_20261015_v1/USER_APPROVAL_V1.json)。批准范围：隔离实现／三方审查后一次Dynamic；真实技术成功及结算后才一次同执行器ALINEA；同600秒总监控预算、终点1296、无自动重试。不以本报告反向授权历史或未来运行。

## 2. 执行版本、环境及运行

两次新运行均使用执行提交`3d82ed578e4e5e028ed3db14e596bd44e845956b`及相同154源摘要`089a2fefb9fb4d68aced499b532636c3a551b672f9130a1fd2e6acb468ff4ae2`。最终主代理再次核对全部154文件的现场及执行提交Git字节；data23项、终点修复工程12项绑定均一致。[核对记录](../../artifacts/dynamic_native_yellow_minqual_20261015_v1/ROOT_FINAL_BINDING_READBACK_V1.json)。

必要环境：SUMO1.26.0，Python3.13.0，traci/sumolib1.26.0，sumoITScontrol0.1.0；精确文件哈希及输入见各卡片。没有安装依赖或更改环境。以下均为seed17、0–1296秒仿真，其中控制观察1200–1296秒。

| 运行 | 精确卡SHA前缀 | 实际监控秒 | 结果及边界 |
|---|---|---:|---|
| UA_NATIVEYELLOW_DYNAMIC_S17_01 | 53ffc491 | 155.480803208 | 到1296；有限动态技术门通过；末周期partial |
| UA_NATIVEYELLOW_ALINEA_S17_01 | 36d30fff | 157.092606667 | 到1296；短真实闭环有限证据通过；末周期partial、末请求pending |

实际启动命令见各运行的`CLI_SESSION_RECEIPT_V1.json`；进程、端口、输入及原生EOF分别见[Dynamic工程receipt](../../artifacts/dynamic_native_yellow_minqual_20261015_v1/engineering/native_execution_v1/UA_NATIVEYELLOW_DYNAMIC_S17_01/EXECUTION_RECEIPT_V1.json)和[ALINEA工程receipt](../../artifacts/dynamic_native_yellow_minqual_20261015_v1/engineering/native_execution_v1/UA_NATIVEYELLOW_ALINEA_S17_01/EXECUTION_RECEIPT_V1.json)。CLI/native退出0只是过程记录，结论依据独立数据审计。

## 3. 动态300→750→900→300：实际结果

原请求1200/1201/1226/1237秒，真实应用1200/1224/1232/1240秒，应用延迟**0/23/6/3秒**。延迟来自周期边界应用，不能把指令年龄当新应用延迟。

原始累计C=311/24≈12.958333辆；真实N=14辆；完整周期计划E=12辆。六个完整包各真实放行2辆，末T24部分包已放行2辆，不能把它补为完整E。第三T8实际绿灯进入1辆、黄灯进入1辆，如实保留。

最后300实际应用时正欠额55/24辆，随后完整边界降为23/24、1/24、1/24辆，已观察到欠额恢复。终点C−N=−25/24辆包含末部分包前置放行，不以该终点单独判断长期误差。采样完整边界最大正欠额23/8辆不是全时刻最大值。`C_applied=155/12`只是选中周期名义7200/T积分，不是原始请求延后后的积分。

七次firstY、14入口／14车尾、1372正常离网末步及EOF独立通过；1236旧黄灯见证UNKNOWN保留，新模式下运动已真实观察，不等于普遍安全。见[完整数据后审](../../data/processed/dynamic_native_yellow_minqual_20261015_v1/native_dynamic_v1/DATA_NATIVE_POSTREVIEW_V1.md)、[字段定义](../../data/processed/dynamic_native_yellow_minqual_20261015_v1/native_dynamic_v1/APPLIED_FIELD_DEFINITION_V1.md)、[科学后审](../../artifacts/dynamic_native_yellow_minqual_20261015_v1/SCIENCE_DYNAMIC_POSTREVIEW_V1.md)。

## 4. 同执行器真实ALINEA：实际结果

| 反馈计算秒 | 独立两车道30秒占有率% | clipped原始请求veh/h | 实际应用秒 |
|---:|---:|---:|---|
| 1230 | 8.477807332 | 900 | 1232 |
| 1260 | 11.255823327 | 882.092367085 | 1264 |
| 1290 | 12.007010804 | 811.601610838 | 截止1296仍pending |

独立重建E1事件／ongoing车辆与own-previous公式，确认不是固定指令冒充Feedback。1290新请求已计入原始C，但未伪报应用；初始被替代记录也未冒充pending。

**C=23.7034390771辆，N=24辆，完整E=22辆，C−N=−0.2965609229辆。** 十一个完整包均N2；最后T8[1289,1297)仅观察G4/Y2/R1，已经N2，但未完成。选周期名义积分C_applied=23.75单独保留。

完整边界C−N至1256为0，1264/1272/1280约−0.019897/−0.059692/−0.099487辆，选T9后1289约+0.105744辆。每完整包2−N=0；已核查的短窗口无持续无法解释的欠放。周期实际由十T8转T9再到末部分T8；不是仅看程序跑通或强行凑目标车辆数。

24入口均G、24车尾、1376正常离网末步、12次firstY、四流EOF通过；最低实测加速度及速度差均−4.5m/s²，无新数值例外。该ALINEA样本没有legacy黄灯见证失败，不重复验证Dynamic里的UNKNOWN继续路径。详见[数据V2后审](../../data/processed/dynamic_native_yellow_minqual_20261015_v1/native_alinea_v2/DATA_ALINEA_POSTREVIEW_V2.md)、[有限核账](../../data/processed/dynamic_native_yellow_minqual_20261015_v1/native_alinea_v2/FINITE_ALINEA_SUMMARY_V1.json)。

## 5. 必要修复、测试及失败保留

原始绑定ALINEA reader确实exit1：外层UNKNOWN_PHASE_FOR_YELLOW_COVERAGE，底层RED_DURATION_TRACE_COVERAGE。原因是末首redACK1296恰为终点，bridge不再prepare1296；reader却要求此时未执行的setter。真实native nextSwitch1297、dualACK和相位均完整。这是后分析终点边界错误，不能写成原生运行安全FAIL，也不能声称原reader通过。

只在`data/processed/.../native_alinea_v2/`新建分析副本，严格核实末partial/nativeclock/无下一PRE/无已执行setter后接受终点缺setter；更早缺失、错误clock、伪completed、残缺已执行setter仍拒绝。原154源、guard、卡、raw和原FAIL不动。

| 检查 | 实际结果 | 适用范围 |
|---|---|---|
| 新黄灯实现工程检查 | 首次2PASS/1fixtureERROR；仅修helper后受影响1方法PASS | 未声称重跑整套 |
| 独立黄灯reader离线检查 | 3方法PASS0.017s | 不是原生安全证明 |
| Dynamic完整绑定reader | 一次exit0／无missing或alarm | 本次有限原生数据 |
| 终点修复回归 | 真实子集旧FAIL／新1方法PASS0.012s及必要反例 | 首次入口importERROR／0测试记录保留 |
| ALINEA原reader／新版后分析 | 原一次exit1保留；新版同raw一次exit0 | 无重跑SUMO；不是原154版本reader已修复 |
| 最终哈希与预算结算 | 154源、35审查绑定及三run完整manifest核对通过 | 没有重复大FCD解析或新clean-checkout原生主张 |

准确命令、版本差异及日志见[后分析receipt](../../data/processed/dynamic_native_yellow_minqual_20261015_v1/native_alinea_v2/ACTUAL_AUDIT_RECEIPT_V2.json)、[工程修复审查](../../artifacts/dynamic_native_yellow_minqual_20261015_v1/engineering/analysis_boundary_review_v1/ENGINEERING_ANALYSIS_BOUNDARY_REVIEW_V1.md)。原始失败、STOP3、旧guard、不同版本及未观测null不改判；旧固定750证据不拼为新154版本同一因果比较。

## 6. 资源、证据保存与Git

同600秒账包含旧UA_NATIVEGAP_DYNAMIC的163.072057750秒及本次两运行；已三方后审结算合计**475.645467625秒**、剩124.354532375秒、无unknownreserve。余额不构成追加运行理由或权限。[最终账](../../artifacts/dynamic_native_yellow_minqual_20261015_v1/RESOURCE_ACCOUNT_FINAL_V1.json)。两次新raw共884563972B，全部留在本地immutable路径`data/raw/dynamic_minimum_qualification_20261015_v1/`各run，manifest记录文件级哈希。不是公开在线原始产物。

本次只整理选定本地提交，不自动推送、合并或修改上游PR。最终交付提交见Git历史；执行测试仍对应3d82ed57和单独记录的后分析副本，不声称测试过未来文档提交。未提交私人邮件、无关MemoryCore改动或全部raw。

## 7. 最终判定与下一步

工程→独立数据→只读科学终审完成，无阻碍本节点收口的实质finding。科学判定[GO_FOR_BOUNDED_DYNAMIC_AND_REAL_ALINEA_TECHNICAL_NODE_CLOSEOUT](../../artifacts/dynamic_native_yellow_minqual_20261015_v1/SCIENCE_FINAL_POSTREVIEW_V1.md)。

已确认：动态四请求真实应用／欠额恢复；同版本真实E1→ALINEA→执行器→实际N链路及有限累计跟踪。推断：累计纠偏方案已解决本次诊断暴露的名义率量化和切换阻断问题，可作为后续审查基础。未证明：长期均值、全连续300–900需求／全部周期／未来请求历史、多seed、一般安全／完整服务资格或论文sweet spot。

所有观测安全结论只限本次日志。末AFTER人口池单来源、私有模型分支、源码／二进制等价性、事后离网审计不等于在线预防等限制保留。不得用本报告解除旧NOT_QUALIFIED或A1UNRESOLVED。

下一位用户／Chat：审查本技术节点与停止合同的实际证据，决定是否及如何进入下一项开发或正式方案准备；正式实验仍需明确授权及冻结协议。若未来复用，先把已审终点边界处理纳入新版本reader并重新绑定，不能直接把旧绑定reader标为已修。**下一步建议不构成执行授权。** 不继续本轮额外矩阵、A1数学证明或无依据调参。

Documentation Impact Check：更新PROJECT_STATE当前快照、追加WORKLOG、形成此报告和目标清单V4；绑定历史文档原字节保留。README使用方式未变；DECISIONS、正式协议、AGENTS、导师反馈和论文结构未改。

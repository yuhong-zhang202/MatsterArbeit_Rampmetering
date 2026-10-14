# 完整周期库动态诊断：实际停止与修复记录

2026-10-14运行，2026-10-15完成有限物理前缀的数据/科学后审。技术诊断，不是正式实验或执行器资格。[独立数据最终报告](../../data/processed/cumulative_full_catalogue_followup_20261014_v1/native_dynamic_v3/DATA_BOUNDED_DYNAMIC_POSTREVIEW_V1.md)、[科学后审回执](../../artifacts/dynamic_minimum_qualification_20261015_v1/SCIENCE_HISTORICAL_DYNAMIC_POSTREVIEW_V1.md)。判定为`DELIVER_VERIFIED_PHYSICAL_PREFIX_WITH_GUARD_STOP_AND_RAW_EVENT_COVERAGE_UNKNOWN`；本文件不替代原始失败及版本化审计产物。

## 结论

`UA_CUMULATIVE_FULL_DYNAMIC_S17_01`在1233秒触发原有跟车间距门并停止，没有到1296。前两周期各实际放行2辆，第三周期只观察到第一秒绿灯、放行1辆。动态任务未通过，真实ALINEA尚未运行。

这是一个实际项目检查拒绝，另伴有明确的停止路径日志缺陷及离线审计器缺陷。不能把它们混成一个原因，也不能通过修复日志把本次运行改判通过。既有固定750的96秒20辆结果保持有效；它不能补足本次动态缺口。

## 运行身份与输入

- 执行提交：`ee5984024987e6cf7c6b2e571c083e06a9773a8b`。
- 执行卡SHA-256：`68e9b2c73d7164a1bd10199e77ca43bcb42332e680a240b0828091ec45a3ed34`。
- 136源摘要：`5d0695195a2062f4708f455b227901b9084a76acca86dc81b34cc59e93d6d85e`。
- M3600/R900/U360/X180、seed17、dt1；1200启用，计划1296结束。
- 指令：1200→300、1201→750、1226→900、1237→300 veh/h。最后一项未观测。
- 单次监控300秒、启动60秒、无固定输出字节上限、至少5GB磁盘余量；两项后续任务合计600监控秒。
- 唯一CLI61749/SUMO61776，实际监控147.815189833秒，CLI1/native EOF0。没有重试。

原始数据位于`data/raw/cumulative_full_catalogue_followup_20261014_v1/UA_CUMULATIVE_FULL_DYNAMIC_S17_01/outputs/`，186文件、401074259B；[原始清单](../../artifacts/cumulative_full_catalogue_followup_20261014_v1/engineering/native_execution_v2/UA_CUMULATIVE_FULL_DYNAMIC_S17_01/RAW_FINAL_SHA256_V2.json) SHA `fae54a894ca43db10999857a1c11db8371ac8c57b992f5cb0007b8f0f268eb75`。raw仅本地保存，没有上传或修改。执行时源与6个输入均有不可变快照，不用随后修复的工作区字节冒充旧运行版本。

## 已观测核账

| 周期 | 实际相位前缀 | 状态 | 实际N | 完整周期累计E的新增量 |
|---|---|---|---:|---:|
| 1200–1224，T24 | G4/y5/r15 | 完整 | 2 | 2 |
| 1224–1232，T8 | G4/y2/r2 | 完整 | 2 | 2 |
| 1232–1240，T8 | 仅G1，实际止于1233 | 部分观测 | 1 | 0（尚无完整周期） |

1200–1233原请求积分C=169/24≈7.041667辆，已应用名义积分4.25辆，完整周期E=4，独立入口N=5。第三周期黄/红的服务观测为null；账本对应计数器0只表示截至当前未累计该类事件，不能写成测得黄/红放行0。1233之后均未观测。

750首次物理应用1224，延迟23秒；900首次物理应用1232，延迟6秒。后者由TLS、两条步ACK、程序/相位/连接及时间联合核对得出，**原始command_events缺少对应两条应用ACK事件**，因此仅标为`DERIVED_PHYSICAL_BINDING_ONLY_RAW_COMMAND_ACK_UNKNOWN`，完整事件链仍为UNKNOWN。未将推导事件写回raw。

独立FCD识别5个入口，前4辆车尾已清线，R_flow.4车尾在停止时仍截断；1294个正常离网末步被核对。相位前缀及原生四日志EOF已检查。末端AFTER非活动车辆池没有下一同刻PRE作第二来源，保持单日志来源限制。详见[限定物理前缀V6](../../data/processed/cumulative_full_catalogue_followup_20261014_v1/native_dynamic_v3/PHYSICAL_PREFIX_RESULTS_V6.json)。

## 间距停止的实际含义

1232开始绿灯前，准入车辆R_flow.4处于READY。首个绿灯运动后R4跨线，下一个队首变为R_flow.5。R5跟随R4时：

- 查询净间距2.095152216m，已扣除车辆minGap；几何复算一致。
- `getSecureGap`返回1.022884125m，项目门另加1.1m，要求2.122884125m。
- 实际比项目门少0.027731909m；R5速度4.306578→1.022884m/s，1秒速度差约−3.283694m/s²。

R4自身跨线前后的跟车检查通过，失败的是新队首R5的当前状态。不能把本次拒绝写成已证明的碰撞、SUMO原生不安全或Candidate A普遍不可行。额外1.1m是保留的项目合同，不是本次源码核查证明的SUMO原生通用最小值；净间距高于查询值本身也不能证明通用安全。[工程源码核对](../../artifacts/cumulative_full_catalogue_followup_20261014_v1/engineering/native_execution_v2/UA_CUMULATIVE_FULL_DYNAMIC_S17_01/GAP_SOURCE_SUPPLEMENT_V2.md)、[SUMO 1.26固定版本MSVehicle](https://github.com/eclipse-sumo/sumo/blob/fa7df22d7f1c4ae245192ecc32410a49f1ffb2a3/src/microsim/MSVehicle.cpp#L6690-L6720)、[跟驰查询源码](https://github.com/eclipse-sumo/sumo/blob/fa7df22d7f1c4ae245192ecc32410a49f1ffb2a3/src/microsim/cfmodels/MSCFModel.cpp#L168-L184)。未证明源码与本机二进制构建等价或唯一识别内部动力学分支。

现有WAIT只接受“预期接收不足、但当前间距门通过”的状态；它不能接纳本次当前间距失败。墙钟暂停不会改变仿真状态，新增红灯等待则需要另行设计连续请求积分、周期和应用时钟，且已有三帧不能证明这种反事实调整有效或安全。本轮未实现该等待方案。[有界调查](../../artifacts/cumulative_full_catalogue_followup_20261014_v1/engineering/readiness_and_flush_investigation_v1/INVESTIGATION_V1.md)。

## 确认的技术缺陷与证据边界

1. **停止路径未写出已生成的ACK事件。** Ledger已处理真实首G ACK，之后间距检查raise，bridge跳过正常flush。修复仅持久化已有事件、保留原STOP、写失败时UNKNOWN并保留原错误，不额外推进SUMO或制造事件。
2. **离线reader局部变量遮蔽terminal模块。** 原reader在正常离网审核时抛UnboundLocalError；分析副本只改局部变量名，原失败保留。
3. **旧reader把合法黄灯限定为2/3秒。** 动态首T24的Y5因此触发YELLOW_PERIOD。限定分析按原始车辆/几何独立复算Y5筛查，未修改运行黄灯或安全门。未来reader需与已存在的完整周期库规则一致。
4. **修复期间历史源码绑定。** 一次分析使用已改工作区而触发source drift；失败保留。V6逐项核对执行时136源及6输入的raw快照，未跳过哈希或还原覆盖原数据。

上述审计失败及每个副本版本均保留，原始绑定reader没有PASS。V6全局状态仍为`UNKNOWN_RAW_COMMAND_ACK_COVERAGE_WITH_OBSERVED_PHYSICAL_PREFIX_AND_STOP`，不能用部分子检查通过宣称完整审计通过。

## 后续边界

以10/15用户新顺序为准：先完成[最小资格方案](DYNAMIC_ACTUATOR_MINIMUM_QUALIFICATION_PLAN_20261015.md)中的1.1m依据/合同方案和必要离线审查；具体新方案获授权后先动态技术验证，通过后才做一次短真实ALINEA。旧147.815189833秒及失败状态继续保留，不以新预算清除历史。当前无新运行授权，不原条件盲目重试、不用闭环接口结果代替动态失败。

[条件误差界](CUMULATIVE_TRACKING_CONDITIONAL_BOUND_20261014.md)解释原请求与实际计数的递推；其每包实放2辆、连续执行等条件不能由本次STOP补足。正式协议、科研设计、既有Stage6结项、A1 UNRESOLVED、Candidate A NOT_QUALIFIED均保持。

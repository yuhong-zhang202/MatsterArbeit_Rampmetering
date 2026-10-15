# G5/Y3 实际放行核验与资源问题处理

2026-10-13。当前目标是解决 ALINEA 指令、执行器应用的计划与实际放行车辆数之间的不一致。03 已运行一次并正常到达1270秒，独立数据及科学post均已完成，7周期E=N=14；原始请求750与映射/实际720的差额尚未消除。本文保留02失败，并追加03结果。

## 1. 需要解决的两个差额

旧 `UA_FIXED750_S17_02` 的请求是750 veh/h，整数周期映射为720 veh/h；70秒、7个完整周期名义 E=14，实际 N=13，实际率668.57 veh/h。因此有两个不同问题：

- **实际服务缺额：** N 比 E 少1辆。已有轨迹确认第二辆在4秒绿灯结束时距离停止线还差约0.519 m，未发现漏记过线或提前关绿的软件缺陷。
- **指令换算误差：** 即使 N=14，70秒平均也只是720 veh/h，比750低4%。不能以 E=N 宣称精确跟踪750。

当前已批准 Gmax5/Y3/redmin2、T10 单点诊断检验第一个问题。分析会继续保留请求积分、映射、应用、名义 E 和真实 N，并据此判断整体目标还有什么缺口。[原始缺额调查](UA_FIXED750_SHORTFALL_CAUSE_ANALYSIS_20261013.md)、[统一执行器已有技术结果](UNIFIED_ALINEA_ACTUATOR_VALIDATION_REPORT_20261013.md)。

## 2. 02：原300 MB限制阻止进入控制区间

`UA_T10_G5Y3_FIXED750_S17_02` 按批准提交 c82333d77de1367f0d6fce4b8ceb2742bfd8ed80、V4卡18774ee7…运行一次，最后核实 ACK 为1038 s，尚未到1200 s控制启用。监控约137.066217 s，其中启动24.580045 s；OUTPUT_BYTES触发停止，CLI exit1，状态 STOP_UNKNOWN_LOG_FINALIZATION。1270 s目标未到达。

冻结原始父目录130文件共300,852,929 B，outputs为300,851,878 B。触发瞬间的抽样字节数未保存，不能拿最终清理后的大小冒充触发值。identity_journal/pre_steps/post_steps三个必要日志共占输出96.097%。因此固定300 MB对于这次完整日志诊断偏小；这是技术资源阻碍，没有提供控制失效或危险的证据。

|02项目|核实结果|
|---|---|
|请求/映射/应用积分、E、N及差值|null，控制未观测；不是零|
|受控首次黄灯/红灯、完整周期|未观测|
|完整正常EOF、native exit code|UNKNOWN；final_logs=null|
|CLI及进程|CLI exit1；进程结束不等于正常日志闭合|
|放行匹配/服务资格|无法判断|

[冻结原始清单](../../artifacts/t10_g5_y3_audit_ready_20261013_v1/engineering/native_execution_v1/RAW_FINAL_SHA256_V1.json) SHA-256 `9f0a55efb1c0279782635f5556c9fe4101b50fb9a85328e779405b26b00a38dd`。原始文件留在本地 `data/raw/t10_g5_y3_audit_ready_20261013_v1/UA_T10_G5Y3_FIXED750_S17_02/`，不上传。

工程→独立数据→科学完成限定失败证据复核：130哈希、2076 ACK元组及1038完整post匹配。完整交通reader未运行，没有伪报PASS或FAIL。科学意见为 `GO_LIMITED_FROZEN_RESOURCE_STOP_EVIDENCE_ONLY`。[工程报告](../../artifacts/t10_g5_y3_audit_ready_20261013_v1/engineering/native_execution_v1/POST_ENGINEERING_REVIEW_V1.md)、[数据报告](../../data/processed/t10_g5_y3_audit_ready_20261013_v1/native_post_v1/DATA_NATIVE_POST_REVIEW_V1.md)、[科学意见](../../artifacts/t10_g5_y3_audit_ready_20261013_v1/science/NATIVE_POST_RESOURCE_STOP_V1.md)。原 TraCI 浮点step API警告保留。

## 3. 03：必要资源修正及执行依据

用户明确要求“别管300MB的限制，继续跑完”，随后明确目标是解决实际放行与ALINEA指令不一致，技术问题应先评估、解决并继续推进。[原指令](../../artifacts/t10_g5_y3_no_output_cap_20261013_v1/USER_CONTINUATION_SCOPE_V1.json)、[目标澄清](../../artifacts/t10_g5_y3_no_output_cap_20261013_v1/USER_GOAL_CLARIFICATION_V1.json)。

02进程已经结束且没有可恢复状态，因此采用新身份 `UA_T10_G5Y3_FIXED750_S17_03` 从0开始。只在隔离版本中取消固定输出及总字节停止门，明确为null，不另加任意400/500 MB上限。继续记录实际文件量，保留实时5 GB磁盘余量、300 s监控、60 s启动、1270 s仿真终点、严格NUM及全部安全/UNKNOWN停止。旧实现、原始失败、配时、车辆模型、需求、seed、900档及正式实验配置保持各自版本。

依据02前缀作储存规划：恒定每秒字节假设约368.10 MB，每步日志负载线性增长假设约450.37 MB。这些是规划情景，不是完成上界、概率区间或新上限；实际03大小另行记录。

|绑定项目|值|
|---|---|
|实现检查点|ec2e13f7df62dc36833fd6dfe87555b74f95d053|
|03卡SHA-256|9daacfd217e17388ec8057a82677756e95036e0fcb9756b6a0cdef1f7669f9da|
|96源摘要|aaa47f9890cb9f30018b0344989e6f13cd0ecc993759263a8a4e05fbe9942d46|
|canonical release SHA-256|8a3859a76bf037a3fb8a704f122793b57e4e537431f5c79733407f049aff86bf|
|启动规则|本次新03一次；先核实进程/消费记录，防止中断后重复启动|

3项针对性离线测试PASS，并补充UNKNOWN负例；测试发生于提交前，相关源码字节与检查点一致。原02/87源及guard不变。data独立核查32工程绑定/96源及资源门保留，科学限定GO；canonical fresh验证PASS。[工程预审](../../artifacts/t10_g5_y3_no_output_cap_20261013_v1/engineering/implementation_v1/ENGINEERING_NO_OUTPUT_CAP_REVIEW_V1.md)、[数据预审](../../data/processed/t10_g5_y3_no_output_cap_20261013_v1/native_prelaunch_v1/DATA_NO_BYTE_CAP_PRELAUNCH_REVIEW_V1.md)、[科学预审](../../artifacts/t10_g5_y3_no_output_cap_20261013_v1/science/NATIVE_PRELAUNCH_GO_V1.md)。

## 4. 已完成的指令换算调查

只读代码调查确认：`period_for()`选择与请求最接近的7200/T（T为8–24的整数），750距离720为30，距离800为50，因此选择T10。请求积分C、映射积分和应用积分会持续保留；但它们的差额仅用于报告，下一周期不读取差额补发，仍为最近档和两车配额。因此“差额没有补偿”准确，“请求账被丢弃”不准确。[映射实现](../../src/candidate_a_issue12_packet_policy_20261012/policy.py)、[G5/Y3周期及积分实现](../../src/candidate_a_t10_g5_y3_20261013/policy.py)。

已批准范围明确允许本次使用750→720并要求分开报告−4%，但没有给出最终实际跟踪ALINEA的允许误差阈值。不能事后把4%自行宣布可接受，也不能把获批映射冒称计数bug。[既有范围](UNIFIED_ALINEA_ACTUATOR_SCOPE_20261013.md)。

若03完整70秒且N14，条件算术为：C=750×70/3600=175/12≈14.5833辆，映射/应用/E=14，E−N=0，而C−N=7/12≈0.5833辆。在持续固定请求、每周期恰放两辆的假设下，现有规则长期仍是720，延长同配置仿真不能消除30 veh/h的系统性映射偏差。后两项是代码及算术推断，不是新仿真观察。

最小后续应根据03真实结果选择：若仍有E−N缺额，继续分析逐周期轨迹及准入/转相原因；若缺额消失，则转入同一版本的控制接口整合和请求误差处理评议，复用已有变指令与真实ALINEA日志，不为了凑齐矩阵重跑。改变最近档调度、设置资格容差或加入新的原生控制配置，都应明确给出技术方案及适用安全条件，不能以成功计数为由暗中更改。

### 可直接接手的最小统一接线方案（Proposed）

工程只读核对后建议保留旧实现，新建一个统一版本，复用已经通过检查的通用Command和最近档规则。仅映射为T10时使用Gmax5/Y3/Rmin2；其他T8–24保持原相位程序。把当前周期的绿灯预算写入周期对象，Ledger、adapter、bridge中的deadline、nextSwitch、quota早关和补红统一读取该对象，避免残留固定4秒。

输入侧继续使用原统一版本的动态Producer、真实E1窗口和Feedback；03的固定750 Producer不能充当ALINEA。日志侧复用03的黄灯、身份池、车尾及独立审计；新profile绑定同一个源版本及相位库，原数值例外不自动带入。

最少受影响离线验证为：①17周期参数对照，仅T10有预定差异，T8/900逐setter及检查相容；②真实helper驱动T24→T10→T8→T24，核对边界应用、延迟以及G4 quota早关/G5截止两路；③复用Feedback/E1窗口fixture接入新Ledger，并保留错误ACK、黄灯UNKNOWN停止负控。不增加需求点或种子矩阵。

03固定T10和旧动态/闭环日志可以支持已有组件判断，不能拼成“新统一版本已完成动态ALINEA验证”。完成同版本离线接线后，是否需要一个新的有界闭环运行，应由具体覆盖缺口决定。若目标包含消除750→720的长期偏差，则还需明确累计误差调度要求；这不是本次固定T10成功已经解决的内容。本方案尚未实现，不构成新的运行卡或安全认可。

## 5. 实际结果与后续判断

03唯一原生启动已完成：CLI及原生EOF退出码均0，ACK/accounted1270；监控启动、循环及清理共176.628029 s（非整个CLI/审查耗时）。完整原始父目录145文件、424,961,934 B，约425 MB；这直接说明原300 MB上限不足以容纳本次所需证据。没有新增重试或关闭安全门。[工程实际复核](../../artifacts/t10_g5_y3_no_output_cap_20261013_v1/engineering/native_execution_v1/POST_ENGINEERING_REVIEW_V1.md)、[实际执行回执](../../artifacts/t10_g5_y3_no_output_cap_20261013_v1/engineering/native_execution_v1/EXECUTION_RECEIPT_V1.json)。

工程初核7完整周期各2辆绿灯入口，E=N14；前6周期实际G4/Y3/R3，末周期G5/Y3/R2，均在实际quota ACK后结束绿灯。首次受控红灯begin1207、checkpoint ACK1208。运行四个原生日志最终EOF无已观测严重消息；客户端浮点step UserWarning保留，不能把它隐藏成“所有警告均无”。完整独立reader一次exit0，已核对FCD、2540 ACK、连续相位、身份/动力学及池覆盖、14入口/车尾、1337正常离网末步和完整EOF；无required UNKNOWN/截断车尾。最低实测速度差与加速度均−4.5 m/s²，无NUM例外。

[03冻结清单](../../artifacts/t10_g5_y3_no_output_cap_20261013_v1/engineering/native_execution_v1/RAW_FINAL_SHA256_V1.json) SHA-256 `029045ebc588b2a040714484c8850b15acaf0402cc796994bb1b4eaff08d9c7b`；原始目录 `data/raw/t10_g5_y3_no_output_cap_20261013_v1/UA_T10_G5Y3_FIXED750_S17_03/` 只读、仅本地保存。旧02及03合计原始725,814,863 B；总量是证据存储核账，不是追设的新资源上限。

已有日志覆盖限制继续披露：末次AFTER若没有同刻下一PRE，其非活动loaded/pending池仅单一journal来源，不能声称独立完整覆盖。SUMO私有内部分支和官方源码与本机二进制编译等价性未验证。单次技术成功不能升级为通用安全、全部速率服务资格或正式研究结论。

Stage6既有结项、A1 UNRESOLVED、Candidate A NOT_QUALIFIED及空且未冻结的正式协议不变。本轮未推送GitHub、未改变上游PR或正式研究设计。

## 6. 最终判定与继续推进

[独立数据报告](../../data/processed/t10_g5_y3_no_output_cap_20261013_v1/native_post_v1/DATA_NATIVE_POST_REVIEW_V1.md)及18文件binder `3847b4813bd05c4c7663f1095a5bff2eb9794a3464b80cdf20d69b735d03b381`已冻结；元数据helper最初KeyError保留，修正只读schema后通过，完整reader未改、未重跑。新轨迹确认R13在ACK1264还差0.51862986 m，1264→1265的第五G步实际跨线且尾清。

[只读科学复审](../../artifacts/t10_g5_y3_no_output_cap_20261013_v1/science/NATIVE_POST_FIXED_T10_REVIEW_V1.md)为 **GO_FOR_OBSERVED_FIXED_T10_DIAGNOSTIC_DELIVERY**，无新增Blocker/Major。结论仅为：本样本E−N缺额消除，资源阻碍解决；750→720仍在，整体原始ALINEA跟踪目标未完成。不能因为完成本报告而停止分析剩余问题。

用户随后明确要求实际长期平均跟上原始请求，已据此继续[累计补偿设计](CUMULATIVE_DISCHARGE_TRACKING_DESIGN_20261014_V2.md)。新设计替代独立最近档选择，以C−N累计差额在完整周期边界选包；当前仅设计审查，不将48秒名义算术当新实际数据，不改变本次1270终点或旧结果。

累计补偿设计V2已完成工程/数据/科学限定GO；原V1和精确算术证据保留。本次后续仅设计完成，未实现新调度或启动新仿真。

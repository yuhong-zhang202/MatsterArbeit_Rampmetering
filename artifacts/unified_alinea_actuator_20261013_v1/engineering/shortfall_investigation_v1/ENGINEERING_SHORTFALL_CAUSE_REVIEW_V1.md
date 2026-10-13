# 750档最后周期缺额：既有证据工程调查 V1

**结论：没有发现相位、应用、过线计数或WAIT接线的纯技术缺陷。可确认的直接原因是最后次车在完整4秒绿灯内实际只走8.042649m，仍差0.518630m未过线；随后进入黄灯并停车。E2是每周期请求配额，既有实现从未保证4秒绿灯足以实放2辆。当前不应改代码、任意延绿或重跑同一配置。**

本报告只对应最终64源 `ea180197848843bd3cca7d326a7016454fe8bd0db406302a64ad11f03347b29b` 的 UA_FIXED750_S17_02、seed17、750→720/T10/Gmax4/Y4/redmin2/quota2、1200–1270技术窗口。Stage6既有结项、Candidate A NOT_QUALIFIED、A1 UNRESOLVED和空未冻结正式协议不变。旧75001严格STOP版本仅用来确认选定前缀与时间先后，不混合为同版本资格或控制效应。

## 1. 数据、时钟及范围

读取已三方核账的原始FCD/TLS/ACK/pre/post/crossings/周期账。复用111raw既有冻结manifest `c8d6e35fd9144124447739dce8bd4598ff4f9f63cefc57b0e48458bb01d97815`，不重复全量SHA或完整raw审计。FCD/TLS时间k为移动BEGIN标签，与ACK k+1对齐；每次G开始前的位置以同一ACK的实际TraCI预观测为准。

[派生七周期轨迹](../../../../data/processed/unified_alinea_actuator_20261013_v1/shortfall_engineering_v1/SEVEN_CYCLE_TRAJECTORY_V1.json)和[最后周期/历史版本时间线](../../../../data/processed/unified_alinea_actuator_20261013_v1/shortfall_engineering_v1/LAST_CYCLE_AND_VERSION_TIMELINE_V1.json)保留41选定ACK帧、真实前后速度/α/leader-gap查询、相位和两条ACK记录。最终周期额外覆盖1260–1270。FCD8位舍入与实际getter差异按显式容差核对，不改变原制动阈值或raw值。

已执行 `.venv/bin/python artifacts/unified_alinea_actuator_20261013_v1/engineering/shortfall_investigation_v1/EXTRACT_EXISTING_TRACE_V1.py`：选定速度/位置Euler位移、TLS/phase、双ACK、真实crossing与周期N一致性PASS（约1秒）。不是新SUMO或回归测试。四个相关运行源码的SHA仍与卡一致；未改runtime/raw/模型/配时/guard/seed。

## 2. 已确认的七周期对照

储存lane长度/控制连接入口位置为204.49m。表中“绿末相对线位置”把内部lane坐标加204.49m，正数为已进入内部连接，负数为仍在storage；实际入口仍以原crossing/FCD独立确认，不以该计算替代计数。

| 周期 | G开始s | 次车 | 初始距线m | 四个G步实际前进m | 绿末相对线位置m | 实际G入口N |
|---|---|---|---:|---:|---:|---:|
| 1 | 1200 | R_flow.1 | 8.502046 | 8.581192 | 0.079146 | 2 |
| 2 | 1210 | R_flow.3 | 8.560117 | 12.144825 | 3.584708 | 2 |
| 3 | 1220 | R_flow.5 | 8.503716 | 9.171128 | 0.667412 | 2 |
| 4 | 1230 | R_flow.7 | 8.654479 | 11.215095 | 2.560616 | 2 |
| 5 | 1240 | R_flow.9 | 8.702789 | 10.921016 | 2.218227 | 2 |
| 6 | 1250 | R_flow.11 | 8.565132 | 8.938424 | 0.373292 | 2 |
| 7 | 1260 | R_flow.13 | 8.561279 | 8.042649 | -0.518630 | 1 |

七个G开始均有足够供给：storage队列28/26/24/22/21/21/21辆；每个front实际接收准入available=true。次车均在约8.50–8.70m后的队列中，接近静止但不是一概严格速度0。前六次次车均到最后第4个G步才过线，最窄第一周期仅超过连接入口0.079146m。这显示“每个G4正好2辆”的余量很小，不能把前六次成功推成保证。最后初始位置195.928721335669m、速度0.062034934530m/s，首车位置203.488496562763m、速度0.003554812662m/s。以上见派生七周期原始frame与native getter。

## 3. 最后周期1260–1270：时间顺序足以区分缺额与数值事件

| ACK s | R13位置m（storage） | 速度m/s | 本次移动信号 |
|---:|---:|---:|---|
|1260|195.92872134|0.06203493|前一周期r已完成，新G从BEGIN1260开始|
|1261|195.96008414|0.03136280|G|
|1262|196.95297854|0.99289441|G|
|1263|199.27914242|2.32616387|G|
|1264|203.97137014|4.69222772|G|
|1265|204.16259786|0.19122772|y|
|1266–1270|204.16259786|0|y随后r|

4个G移动区间是BEGIN1260/1261/1262/1263→ACK1261/1262/1263/1264。R12在(1260,1261]进入，持续在内部连接加速，ACK1264速度7.242803m/s、位置15.158973m；未见该窗口下游接收封死或首车被执行器拦停。R13首G步近乎不前进，之后逐步起步；四个实测post速度之和8.042648804400m，与实际Euler位移一致。初始距线8.561278664331m，因此在G截止ACK1264仍缺0.518629859931m。TLS/ACK均确认完整G4，并无漏掉一秒绿或提早setPhase。

BEGIN1264→ACK1265才是首黄步、原生α/dv=−4.501m/s²。这是已批准数值兼容事件，原始值和两条legacy严格FAIL保留；actual private branch未唯一识别。**次车在此事件之前已未完成G窗口过线，所以该数值异常不能作为前4秒缺额的前因。** 进入黄灯后车辆减速并停在距入口0.327402135277m处；该后续停车解释为什么黄/红未额外补到第14辆。此轨迹符合信号停车解释，但不把源码匹配升级成私有分支已观测。

旧61源75001在1260–1264的两车world速度/lane、R13局部位置与当前64源逐字数值一致；仅确认原失败前缀也已有相同绿末缺额。旧版本后来1265严格STOP，当前版本获批有限例外继续到1270，不能因此合并整次验证或抹去旧FAIL。

## 4. 工程判定：名义包配额与原生起步/跟驰限制

- 750映射720/T10是明确量化，不是时钟bug；7个完整cycle的名义2车产生E14，真实入口仍N13。`requested_quota=2`并标记`REQUESTED_NOT_EMPIRICALLY_QUALIFIED`，完整周期时E+=2；N只随实际crossing增加。[policy.py](../../../../src/candidate_a_unified_alinea_20261013/policy.py#L87)（文件行87–89、148–151）。
- Runtime提前转y必须已经观察到quota。最后周期N_G=1，因此没有提前quota setter；G4届满按原生程序转y，周期green_end_reason为MAX_GREEN_DEADLINE。[bridge.py](../../../../src/candidate_a_unified_alinea_20261013/bridge.py#L117)及原policy_phase_requests/周期账。其余相位均G4/y4/r2，应用在1200后沿原生周期边界，无中周期重启或collector漏数。
- WAIT/current_following是只读getter分类；没有车辆setSpeed/setAcceleration/setPosition，也没有额外暂停正常native simulationStep。保留的hypothetical加速准入可能被拒绝，READY/WAIT仅决定观察合同是否可以继续，并不命令SUMO压低车辆速度。[receiver_wait.py](../../../../src/candidate_a_native_receiver_wait_20261012/receiver_wait.py)。R13在1260静态队列的额外1.1m观测predicate曾显示deny，但它不是实际front准入或已进入车辆的硬门，也没有setter作用；后续实际front current-state检查与受限事件前后均在原门内。不得据此把队列等待解释成执行器人为拦车。
- 车型实际参数accel2.6、decel4.5、tau1、actionStep1、sigma0.5、length5、minGap2.5保持。accel2.6是参数上界，不是每步必然加2.6。SUMO1.26官方Krauss的followSpeed受安全跟驰与maxNextSpeed限制，patchSpeedBeforeLC/dawdle2使用随机慢化；这与实际各周期起步/加速度不同相容。[官方源码](https://github.com/eclipse-sumo/sumo/blob/fa7df22d7f1c4ae245192ecc32410a49f1ffb2a3/src/microsim/cfmodels/MSCFModel_Krauss.cpp#L67)（67–94、112–149）。缓存SHA与原official SOURCE_RECEIPT匹配，见EXTRACTION_RECEIPT。

**已确认直接机制：供给充足，但末次车的原生实际起步/跟驰轨迹在G4截止前没有走够距线距离；之后按黄灯停车。没有证据需要修相位/计数/WAIT实现。**

**有限推断：** 4秒2车包对当前起步状态/微观轨迹的余量不足，最终周期体现了能力边界。实际减速/加速差异与跟驰/随机慢化机制相容，但未记录私有vsafe/vmax/RNG draw，无法唯一分解二者贡献，也不能证明所有750场景/所有seed必定短缺。单次7周期不建立长期放行能力或失败概率；不指向SUMO原生不安全。

## 5. 最小解决建议与重试边界

本范围最小有据动作是：保留750服务NOT_MET、E14/N13和原FAIL，交独立data/science确认上述因果边界；不做没有缺陷依据的代码修改，不对同一输入/配时/seed再跑相同身份或另一个相同试验。现有报告/ledger已正确区分请求与实际，缺额已被检测，不需用新状态覆盖。

若后续要求尽量可靠做到2车/周期，需要另行明确批准“政策服务能力”修改和验收条件，而不是称之为bug修复。G、Y、minred与周期必须联合满足：现T10已是G4+Y4+R2；只加1秒G并保留Y4/R2至少需要T11，名义2车率变为约654.55veh/h，不能假称仍是原750档或必然改善。缩黄、缩红、调车型/seed或增加quota均不在本调查授权内。即便新的配时允许更长G，也不能凭当前轨迹假定一定放够2；安全与实际服务仍要新卡/三方门验证。

当前**没有必要重试身份**：未发现可修纯技术缺陷。仅未来有明确获批政策delta时，可提出UA_FIXED750_S17_03（新源码/参数/卡，不复用旧卡/旧身份）及一次必要诊断，但本报告不创建该卡或授权运行。若独立审查找出纯技术绑定/collector缺陷，则先给最小diff和离线重现，再决定新身份；不能据此调参凑14辆。

## 6. 工作记录与待审

工程脚本/receipt在本目录，真正派生轨迹在`data/processed/.../shortfall_engineering_v1`；原raw与历史manifest/数据结果均只读。无新SUMO、native版本调用、测试矩阵、runtime/guard/模型/配时/seed/科研变更。已用官方缓存一次小范围说明机制，不扩A1证明。Parent负责PROJECT_STATE/WORKLOG；下一门data独立核41选定ACK/7周期/时间先后，scientific读审技术vs物理及建议边界。

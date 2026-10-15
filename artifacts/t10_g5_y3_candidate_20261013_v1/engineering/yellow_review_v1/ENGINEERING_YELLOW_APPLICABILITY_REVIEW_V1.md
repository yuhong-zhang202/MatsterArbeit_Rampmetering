# T10/Gmax5/Y3/redmin2：黄灯适用性及离线准备边界

**工程建议：GO_FOR_CONDITIONAL_OFFLINE_PREP，仅允许后续经data/science确认后做隔离的最小实现、离线核查和待审卡。不是Y3原生安全通过，不是服务通过或SUMO放行。**

已完成Context Preflight。用户新批准仅黄灯调查及有条件离线实现，USER_OFFLINE_SCOPE_V1.json SHAca732c8cc3ca078a73f6ad27f4fb6d3eefbf65e5d98b69c93c1edf29c0923e2c；基线48dafb3605687b4738a6c8c45581032a79f8c8ec。Stage6结项、Candidate A NOT_QUALIFIED、A1 UNRESOLVED、正式协议0B/unfrozen、旧750 E14/N13与严格FAIL不改。本步骤无执行器实现、新卡或SUMO。

## 1. 官方机制支持什么

SUMO1.26源码将黄/红作为车辆计划停车条件：stopDecel采用MAX(MIN(tls.yellow.min-decel, emergencyDecel), normalDecel)，当前绑定normal4.5/emergency9及默认yellow.min-decel3使其为4.5m/s²；该配置的3是**减速度单位，不是3秒黄灯依据**。能够在距离内刹车时黄灯采用waiting速度；不能刹车的情形继续受原生链接/跟驰处理。原生红灯及speedMode仍参与禁止新front过线。[MSVehicle.cpp2728–2775](https://github.com/eclipse-sumo/sumo/blob/fa7df22d7f1c4ae245192ecc32410a49f1ffb2a3/src/microsim/MSVehicle.cpp#L2728)、[2871–2879](https://github.com/eclipse-sumo/sumo/blob/fa7df22d7f1c4ae245192ecc32410a49f1ffb2a3/src/microsim/MSVehicle.cpp#L2871)、[3712–3731](https://github.com/eclipse-sumo/sumo/blob/fa7df22d7f1c4ae245192ecc32410a49f1ffb2a3/src/microsim/MSVehicle.cpp#L3712)、[4468附近红灯门](https://github.com/eclipse-sumo/sumo/blob/fa7df22d7f1c4ae245192ecc32410a49f1ffb2a3/src/microsim/MSVehicle.cpp#L4468)。三份缓存源SHA与既有official receipt一致，源码commit fa7df22d…，未下载/安装/运行；二进制编译分支等价仍未证明。

原生信号机制允许设定黄相位并自动推进到红，但没有在上述源码中找到“本场景3秒对未来所有车辆足够”的保证。原生支持某个相位时长、官方一般行为说明、当前旧数据相容，均不能冒充Y3安全认证。具体车辆的native私有canBrake/vsafe/offset/RNG和未来G5人口未直接观测，本调查不继续扩展A1数学证明。

## 2. 完全复用原local stop-or-clear screen：Y3更严格，不放宽

原screen基于实际绑定position/speed/length/normalDecel/actionStep与完整storage+ingress人口：

- d=204.49−position>0；v≤b×actionStep时允许一Euler步停止，或者d≥v×actionStep+v²/(2b)。这条stop分支与黄时长无关，未改阈值。
- clear分支要求v>0，actionStep+v/(2b)+length/v≤Y，并且d+length≤v×(Y−actionStep)。Y4→Y3使这两条同时收紧。
- 若两分支均不满足或身份/相位/时间/覆盖/有效数值不确定，必须在首次黄色运动之前STOP，不能把旧Y4 PASS或低速标签作新豁免。[原policy.py yellow_scope](../../../../src/candidate_a_unified_alinea_20261013/policy.py#L175)。

现有绑定包含dt/actionStep/tau1、长5、normal4.5、accel2.6、sigma0.5、modes31/1621、实际速度≤55.555556m/s以及actual route/type/lane。已有完整世界与局部人口交叉核对；同样必须在新G5每次实际first-yellow重采，不能用旧人群固定代入。局部覆盖113.08m ingress+204.49m storage=317.57m，Y3×原上限55.555556=166.666667m，保持覆盖边界；原一秒最大advance58.155556m仍小于ingress113.08m及internal81.98m，原crossing漏观测门不变。这只是既有约束下的覆盖逻辑，不是未来全球制动/接收证明。

## 3. 仅对旧G4人口的有限相容结果

[派生七次重算](../../../../data/processed/t10_g5_y3_candidate_20261013_v1/engineering_yellow_v1/SEVEN_OLD_POPULATIONS_Y3_RECOMPUTE_V1.json)：UA_FIXED750_S17_02的实际first-yellow1204/1214/1224/1234/1244/1254/1264，完整248个重复车辆快照。原Y4 screen与pre-step记录逐项复现；这些**相同旧G4**状态代入未改screen的Y3，7/7计算PASS。前六次全部stop_possible；最后32个状态中31stop_possible，只有R13走clear-only分支。局部最高实测速度2.509/3.819/3.889/4.048/4.445/4.401/4.692m/s，未覆盖未来更快的G5边界状态。

旧13个实际entrant rear-clear均在同Gclose下假想Y3-red之前；前六周期最后rear-clear在yellowBegin+1，最后在yellowBegin−1。只是旧轨迹相容，**不能证明新Y3提前转red后或新G5增加entrant后的车尾行为**。旧R13 screen clear-only但实际选择停车且出现获批−4.501，也直接说明这个screen是条件式可行性筛查，不是原生驾驶选择的预测。

[三个纯逻辑边界例](../../../../data/processed/t10_g5_y3_candidate_20261013_v1/engineering_yellow_v1/GUARD_BOUNDARY_ILLUSTRATIONS_V1.json)：v16m/s、距线1m、长5、b4.5、actionStep1时Y4 PASS/Y3 UNKNOWN；v4m/s距线0.1m通过一Euler步stop分支；v10m/s距线3m通过Y3 clear分支。均明确为synthetic illustration，不是native输入或仿真通过。首例说明保留原screen时Y3会拒绝此前Y4可接受的状态，不能删门去适配候选。

## 4. 必须保留的安全责任与新的时钟边界

| 门／观测 | 新候选要求与限制 |
|---|---|
| 身份、实际模式／动力学、完整world/storage/ingress/internal覆盖 | 同原硬门；每步鲜活绑定，缺失或漂移STOP |
| 黄色准备 | 每次actualGclose先对真实新人口做原screen(Y3)；quota提前转相与nativeGmax届满两路径均检查，不从旧数据自动PASS |
| 原生G/y/r、phase/program/link/nextSwitch及ACK | 新T10原生Gmax5/y3/red2；提前quota若G4则补红至3，不跳相或重启G凑数 |
| first-red检查点 | 根据实际Gclose+3得到firstRed begin、下一ACK做durable provisional checkpoint；G4close对应begin+7/ACK+8，G5close对应begin+8/ACK+9，不硬套旧1207/1209；最终EOF仍必要 |
| 原current gap／接收门 | emergency9+原1.1m及所有actual entrant before/after约束不变；新周期G必须freshreceiver available，不由“黄3+红2”推定接收就绪 |
| all crossed bodies | 每ACK全ID的rear-clear/active body跟踪不变。已front进入而rear仍在R不是新的red entry；不发明yellow末必须全尾清空的deadline，也不假定未来清空已证明 |
| 红灯、碰撞、teleport、ordinary braking／native warnings | 所有实际未豁免异常与UNKNOWN仍STOP；原prospective-red公式只记录shadow，不能将其宣传为active数学证明 |
| 正常离网与日志 | 保留before/arrived/route末端/precision8 BEGIN+finalarrivalSpeed离线必要门（不是实时完整离网制动）；四stream EOF与未知STOP不变 |
| E/N及服务状态 | E仍是名义quota，N仍实际全部G/y/r入口；黄额外入口不cap，不预填N14。G5/Y3不是已修成服务PASS |

缩黄能更早触及原生红及异常门；不放宽任何阈值、不改单车模型或停止条件来减少报警。预先无法取得的新G5人口、未来接收、全部native分支／制动／车尾轨迹，必须留为NOT_OBSERVED并由未来独立授权运行的actual日志核查，不能从offline计算补全。

## 5. NUM例外与900/T8保护

旧USER_NUMERICAL_EXCEPTION_APPROVAL只对应先前已批准的技术模式和极窄绑定条件，actualbranch仍未唯一识别。**新候选中的后续作用范围为PENDING，不随本次offline授权自动enable。** 最小离线实现可原样复用numeric_stop源码和默认严格STOP；新卡把旧批准作为来源/待定项，不能改程序身份匹配、公式、domain、normal阈值或globaltol来吞新报警。未来若要启用，需明确绑定本新卡/新来源与已有有限批准范围，并经三方/用户实际运行授权；本轮无native许可。即使某事件再次匹配，也保留rawα/dv/legacyFAIL与未唯一识别的限制，不称安全通过。

BASE64_T8_PRESERVATION_V1.json确认全部64源当前SHA仍等于ea180197…，原T8 phase tuple仍G4/Y2/R2；没有实现或修改任何旧namespace。这是字节/参数保护，不是新native900资格。后续必须保留原64源码和全部旧卡/raw；新T10候选限定独立namespace，不允许全局monkeypatch、改MAX_GREEN影响900或改旧card。

## 6. 推荐最小实施范围及待审卡条件

建议在独立`src/candidate_a_t10_g5_y3_20261013`及对应scripts/tests中机械复用必要的policy/adapter/bridge/profile逻辑，仅暴露固定T10/750→720候选；body/FrameCache/worker/identity/dynamics/currentgap/log/watchdog/normalarrival/numeric公式等原模块只读复用。旧900/T8继续运行原namespace，候选profile拒绝非T10，不因fork将它宣称为已解决全300–900库。少量针对参数/clock的必要fork比修改原64来源或全局patch更容易核对。

若data与science接受本条件GO，下一步离线只需验证：Gmax5/y3/r2和提前quota→G4/y3/r3、actualred补时/动态firstred/实际ACK绑定；真实官方helper/新XML驱动的有限假连接回放；Y3 UNKNOWN/身份／相位／覆盖/原硬门及NUM默认strict负例；真实N/E/partial/null、原64/T8保护。每项必须留实际PASS/FAIL并披露fake不是native安全。无必要重跑旧完整suite、A1证明或扩需求／seed矩阵。

待审卡应标**OFFLINE_PREPARED_NOT_NATIVE_AUTHORIZED**，运行身份、输入、源、环境、guard矩阵、未观测状态、新phase预算及NUM-pending独立绑定；没有canonical authorization/release，不配置自动重试或可执行许可。0.52m短缺只提供试探启动余量的动机，不推出多1G步必够或Y3必安全。具体终点／资源／NUM作用范围和未来一次诊断是否批准仍属后续新卡审查，而非沿用旧剩预算即运行。

## 7. 工作与风险收口

成功执行RECOMPUTE_EXISTING_YELLOW_V2.py完成一次必要七旧snapshot重算/覆盖/body相容和三个边界逻辑校验；初始V1因standalone脚本缺src import path退出1，未输出派生数据，V1源码和FAILED_EXTRACTION_V1.json保留。V2仅为分析脚本补project root路径，未改runtime。三pinned官方源SHA、旧64源以及T8参数保护PASS，回归suite/版本调用/SUMO均0。

关键风险是：旧低速G4人群不代表新G5；local stop-or-clear不是唯一native分支或全球预测；旧NUM批准不能自动扩；Y3未来可能触发UNKNOWN或其它原硬门而NO_GO。没有离线证据可将这些状态预先写成PASS。因此建议只进入条件式offline preparation，**禁止任何native或生产部署、安全资格/服务资格宣称**。Parent负责STATE/WORKLOG；下一门data独立核重算及来源、science核是否允许这一有界实施。

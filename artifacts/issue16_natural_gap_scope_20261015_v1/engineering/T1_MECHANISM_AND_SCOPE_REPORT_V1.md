# Issue16：650秒间距硬停的机制与最小责任边界提案

**唯一T1建议：MINIMAL_SCOPE_CHANGE_PROPOSED。尚未获安全合同变更批准，不实施、不运行。** 现有代码确实按其合同正确停止；问题是该合同将一次当前速度的模型参考间距，作为原生普通跟驰运动后的必须恒成立条件。固定版本源码没有把这个POST比较用作普通车辆运动的判据。可以提出一个一致、局部的责任边界调整：保留严格新绿灯准入，把完整、有效的普通原生跟驰查询及其不足分类为观测；保留真实安全事件、空间/覆盖未知的硬停。**这不是已证明t650无危险，更不是将旧STOP改判PASS。**

## 范围、历史及版本

完整读取Issue16原文；AGENTS、DECISIONS、0B/未冻结EXPERIMENT_PROTOCOL、problem_records索引、当前工程/data/science收口、指定WORKLOG1–1000行及PROJECT_STATE1–160行已读。长工具输出截断的相关段落分段补读。历史Stage2测量/入口域修复、Stage3/5证据资格、旧Stage6限定结项，与本次Candidate A尚未资格分开；旧STOP、旧车型敏感性、旧预算/自主继续文字不能授权本次改合同或新启动。未发现阻碍只读调查的现行授权冲突。当前独立900账已耗83.637436041秒、余816.362563959秒，唯一启动权已用；余额不是新许可。

本分支codex/issue-16-natural-gap-scope，读取HEAD af988faddaa271ac2a8f80fe3fd3558ff2898618；运行源b6c60b927fc71a8750f5674f2cf168824b78cf05、卡b73c678130604d1cef41dd5ecb70a79cc868084e91ae5033cc179393c25f6982、173源摘要c2f00d7f66ea66e331e436248bf34d510fc8ba11a99b16792cd80e18f61055b2。本次未改src/scripts/tests、卡、raw、合同或文档；无SUMO/TraCI连接/--version/netconvert/安装/构建/新测试。官方源码GET和两帧纯算术不是仿真重放。

## T0：实际停止对象、时点和距离

实际链为 `bridge._diagnostic_loop` simulationStep(650) → 两阶段ACK/实际时间校验 → `StepAdapter.reconcile_step` →先核实际信号并完成ledger.end_step/原C/E/N→ `observe` → `classify_receiver` → `current_following`。当前following查询返回STOP后，adapter追加POST_CURRENT_GAP_BOUND_DENIED，仍完成事件/制动/车尾检查，再抛DiagnosticStop；bridge保存已发生运动和异常退出。它不是SUMO自身抛出的碰撞/跟驰异常，也不是绿色setter失败。[bridge341–357](../../../src/candidate_a_natural_service_20261015/bridge.py)、[adapter283–328及391–394](../../../src/candidate_a_natural_service_20261015/adapter.py)、[receiver_wait21–89](../../../src/candidate_a_dynamic_minqual_20261015/receiver_wait.py)。

|实际帧|被查询的R1 / 前车R0（m/s）|gap，不含后车minGap（m）|getSecureGap（m）|作用|
|---|---|---|---|---|
|PRE649|12.771598010 / 1.589874891|14.471410787|24.814794030|R1查询已不足，但R0是front，R1未跨线；R0准入为READY|
|POST650|8.794946163 / 3.934029315|9.610493939|13.089892327|R0跨入internal后R1变front，同一普通跟驰不足开始触发POST硬停|

实际649→650为G，R0跨线、R1未跨线；R1加速度−3.976651847，R0+2.344154424，均是已发生的原生运动。更早648→649为red；不足不是在绿灯切换后才首次出现。不能仅凭角色转变就证明误报或归因于信号。

同帧路径车距：204.49−189.119744925+1.740238864−5=12.110493939m，是物理前后保险杠间距；再减R1 minGap2.5，得9.610493939m。R0车尾相对internal入口−3.259761136m，仍跨线；不能把该负位置当保险杠重叠/负车距，也不能忽略车尾。该查询口径与官方getLeader定义及跨lane源码一致。[TraCI固定源码610–626](https://github.com/eclipse-sumo/sumo/blob/fa7df22d7f1c4ae245192ecc32410a49f1ffb2a3/tools/traci/_vehicle.py#L610)、[MSVehicle6690–6715](https://github.com/eclipse-sumo/sumo/blob/fa7df22d7f1c4ae245192ecc32410a49f1ffb2a3/src/microsim/MSVehicle.cpp#L6690)、[MSLane3005–3028](https://github.com/eclipse-sumo/sumo/blob/fa7df22d7f1c4ae245192ecc32410a49f1ffb2a3/src/microsim/MSLane.cpp#L3005)。

另有prospective receiver secure20.684838490m，其用途是新绿灯/下一释放状态；fresh current query13.089892327m用途不同，不得混用。旧额外1.1m已是advisory，本次即不加1.1也拒绝。实际query用leaderEmergencyDecel9；双方原始identity有normal4.5/emergency9/tau1/actionStep1/sigma0.5、speedMode31/laneChangeMode1621。完整提取和原行号见[TERMINAL_FRAMES](../../../data/processed/issue16_natural_gap_scope_20261015_v1/TERMINAL_FRAMES_V1.json)。

## T1：固定官方源码直接支持什么

官方annotated tag v1_26_0为de3c3f37a2908397bc398a2bfe3b98232252ba8f，指向commit **fa7df22d7f1c4ae245192ecc32410a49f1ffb2a3**。本地下载13个有直接用途的拥有源码，逐文件URL/物理行数/字节/SHA在OFFICIAL_SOURCE_INDEX_V2.json；源码缓存仅本地，公开只需该索引、下列固定URL和短必要解释。网页渲染会省空行，本文行号取下载原文件，不能混用网页文本行号。

- **getter是按输入求模型值，不是车辆下一步已选动作。** Python getSecureGap709–714→libsumo Vehicle907–915→CFModel168–184。该base实现使用当前速度的制动距离和tau，减前车的无headway制动距离；其pred对象在该实现未使用，不能因为传入leaderID就声称读取了那辆车的未来计划。[Vehicle](https://github.com/eclipse-sumo/sumo/blob/fa7df22d7f1c4ae245192ecc32410a49f1ffb2a3/src/libsumo/Vehicle.cpp#L907)、[CFModel](https://github.com/eclipse-sumo/sumo/blob/fa7df22d7f1c4ae245192ecc32410a49f1ffb2a3/src/microsim/cfmodels/MSCFModel.cpp#L168)。
- **普通运动计算下一步速度。** Krauss followSpeed112–125调用maximumSafeFollowSpeed；后者947–1000根据当前gap、速度和前车制动情况求下一速度，并包含必要减速处理；finalizeSpeed188起另施加限速、加减速等约束，Krauss patchSpeedBeforeLC67–96加入dawdling。它不在运动后调用gap≥getSecureGap(current speed)断言。[Krauss](https://github.com/eclipse-sumo/sumo/blob/fa7df22d7f1c4ae245192ecc32410a49f1ffb2a3/src/microsim/cfmodels/MSCFModel_Krauss.cpp#L112)、[next-speed实现](https://github.com/eclipse-sumo/sumo/blob/fa7df22d7f1c4ae245192ecc32410a49f1ffb2a3/src/microsim/cfmodels/MSCFModel.cpp#L947)。因此当前参考不足意味着需要继续响应，不能直接替代原生运动判定；这不保证所有继续运动安全。
- **9与普通分支输入不能混说。** MSVehicle.adaptToLeader3288、junctionLeader3342传leader.getCurrentApparentDecel；其7873–7875返回CF apparentDecel。CFModel构造61在未显式配置时令apparentDecel=normalDecel。本run未直接记录private followSpeed选择、分支/leader集合、传入apparentDecel或RNG；“普通路径应使用4.5”是固定源与输入一致时的推断，不能当实际调用日志。[ordinary调用](https://github.com/eclipse-sumo/sumo/blob/fa7df22d7f1c4ae245192ecc32410a49f1ffb2a3/src/microsim/MSVehicle.cpp#L3288)、[apparent getter](https://github.com/eclipse-sumo/sumo/blob/fa7df22d7f1c4ae245192ecc32410a49f1ffb2a3/src/microsim/MSVehicle.cpp#L7873)。
- **不能用4.5替换9取得PASS。** 两帧前车v均<4.5，在dt1的Euler brakeGap92–98中前车tau0制动距离均0，无论maxDecel4.5或9。原查询分别精确复算为24.814794030113898和13.089892326530567，差额仍在。QUERY_FORMULA_RESULT_V1.json及data独立QUERY_MATH_CROSSCHECK_V1.json一致；没有发新TraCI查询或改变参数。
- **积分/车型依据限于源码配置推断。** MSFrame367–368默认非ballistic；1185–1194另有显式default.action-step-length的切换分支，本卡/argv未设该项或ballistic。MSVehicleType405–408默认选择Krauss，vType未显式指定其他CF。两车位移恰等于POST速度×1s，且query值复现Euler公式，支持这一解释；native flag和CF private对象没有直接journal。二进制141环境哈希已绑定，但它与此tag源码的可复现编译等价仍未证明。[MSFrame](https://github.com/eclipse-sumo/sumo/blob/fa7df22d7f1c4ae245192ecc32410a49f1ffb2a3/src/microsim/MSFrame.cpp#L1185)、[车型](https://github.com/eclipse-sumo/sumo/blob/fa7df22d7f1c4ae245192ecc32410a49f1ffb2a3/src/microsim/MSVehicleType.cpp#L405)。
- **信号和连接是另一些真实约束。** MSVehicle2728–2743、2871–2899区分G与黄/红、停车线与是否可刹；后继lane/部分车体在MSLane3005起另处理，不能从单一gap查询得出完整接收/黄红安全。项目新G严格receiver、实际G/y/r顺序、车尾、冲突/急刹监控均应保留。[信号分支](https://github.com/eclipse-sumo/sumo/blob/fa7df22d7f1c4ae245192ecc32410a49f1ffb2a3/src/microsim/MSVehicle.cpp#L2728)。

[官方Safety](https://sumo.dlr.de/docs/Simulation/Safety.html)区分跟驰、变道和路口风险，明确短黄灯、反应时间/模型设置可造成危险；它不承诺启用原生模式就普遍无碰撞。[Traffic Lights](https://sumo.dlr.de/docs/Simulation/Traffic_Lights.html#signal-state-definitions)说明G允许通行，y/r仍有各自响应；[VehicleInsertion](https://sumo.dlr.de/docs/Simulation/VehicleInsertion.html)说明有安全/间距约束的插入可延迟，不能把供给不足当控制故障。这些living docs只作机制支持，版本敏感解释以上述固定源码为准。

## 事实、推断、未知与风险

**事实：** 旧合同触发可复现；R1普通跟驰不足在变front前已记录；原生减速未超本项目4.5界；原C/E/N和partial核账完整保存；真实车尾/接收空间不应被抹去。旧650 STOP及NOT_QUALIFIED保持，评价窗/长时域仍未测。

**工程推断：** 触发的必要性不能由getSecureGap名字或差额本身推出；它混合了新信号准入责任与已发生普通运动的参考值。固定源直接说明二者时点与函数不同，足以提出范围调整供科学/用户决定；不是把“小差额/过几秒”当作误报理由。

**未知且影响资格：** t650若继续的实际private动作、未来制动/尾部清空、正常receiver保持与恢复、全部4200/六窗/一般服务与城市影响。当前没有证据判定碰撞必然或绝不可能。降低hard门是实质合同变更，必须科学复核及用户明确批准；本Issue一般工程授权不能代替。

## 单一最小合同草案（PROPOSED，待审）

责任按**是否在批准新的信号动作**分开，而非按某个ID/t650或差额阈值特赦。

1. **新G准入不变。** 每个包新G前仍需fresh完整观测、原严格prospective receiver/geometry通过；known不足则完整原Y/R后实际red保持，UNKNOWN硬停。不得把receiver.available从false改true，不采用4.5替换9或改配时来制造准入。原E/C/N/pending/partial、不给物理欠额追债均不变。
2. **普通原生跟驰的已发生/当前观测改责任。** 在已有有效信号计划内、无车速/安全模式/车型setter、路线/前后车/距离完整绑定、query有限且实际gap非负的范围内，current-query不足记录为BELOW_NATIVE_REFERENCE_OBSERVED，保留旧legacy失败/全部args/数值及原因；该数值本身不再升级为控制器故障或安全证明。此一致语义涉及ongoing PRE、POST及actual-entry前后被动快照，不能只删除POST一行、下一PRE仍同义硬停；所有入口仍要正确G/y、真实ACK及body/身份约束。若科学只允许更窄边界，应在实施前一次明确，不能靠多次native失败逐项开洞。
3. **真实危险和未知保留。** 碰撞/teleport、现有超4.5制动、红灯新front、相位/ACK/身份/车尾/路径/日志缺失或不一致、负gap/重叠/异常mode等仍STOP。接收geometry不足仍禁止下一次新G；当前跟驰观测不生成车速、急切红、补偿服务或额外green命令。黄灯责任仍保留原已批准诊断合同和失败见证，不升级为安全证明。
4. **适用界限透明。** 这是采用原生微观运动并保留独立实际监测的有限科研合同，不能保证拒绝所有尚未发生危险。新卡必须绑定新合同/实现/reader，另获单次权限；旧raw/旧reader UNKNOWN/旧安全FAIL不改判。若无法接受该观察责任，应选UNRESOLVED交Robert，而非继续构造完备A1预测证明。

## 最小实施/离线计划，尚未执行

先工程→只读science评审此草案并取得用户明确合同批准。若通过，仅在隔离新版本接入一个明确的current-reference观测分类，保持原current_following查询/legacy字段、strict新G和所有其他硬门；三类调用点共同使用同一语义，不增加预测器、阈值、native core patch或车型setter。最少范围是新receiver分类/adapter接线及必要profile绑定，producer/policy/guardian复用。旧154/finite/natural执行版本与证据完整保留。

离线分三组而非扩大矩阵：①原649/650只读fixture保留旧STOP并在新合同中得到带不足的观测，缺query/错误时刻/非finite/负gap仍拒绝；②strict新G接收不足/未知仍拒绝，已知约束red保持及合法恢复复用必要小fake，实际碰撞/超刹/红入口/ACK坏例不被观测分类吞掉；③原C/E/N和pending/partial守恒及新reader历史版本分离。不得用fake作4200或receiver native恢复证据。每次native需新精确卡/三方/独立资源账/用户明确批准及canonical，旧卡和单次许可不可复用。当前0新native。

## 独立reader计划的静态审阅

READER_MINIMAL_PLAN_V1.md总体GO_FOR_MINIMAL_OFFLINE_READER_REPAIR：仅精确terminalcause/lastACK/query绑定承认失败前缀，保留CURRENT_NATIVE_QUERY_FLOOR_DENIED alarm；原生EOF0与worker失败1分层，timeout/非零native/ownership未知不伪EOF；完整E1窗可核、terminal未执行更新保持缺失；最终仍STOP/qualifiedfalse/未测窗null及censor。

新增且必要的版本门：任何新后分析代码不能要求旧卡的执行source SHA等于新reader而同时声称同版。仅显式opt-in后分析允许已列出的3个owning reader源码变化；旧执行173源必须按raw/snapshots复核，未列runtime/deps仍严格旧hash。结果分列execution source与当前reader closure/SHA，默认旧source校验继续fail-closed。原card/reader退出UNKNOWN不改写，新processed输出不能命名full qualification PASS。该reader分类修复不改变运行安全合同，可独立进行；实际diff仍由data负责并另作最小审阅。

## 必要学术来源的用途与限制

项目已核的[文献依据](../../thesis_actuator_readiness_20261015_v1/LITERATURE_AND_METHOD_BASIS.md)中，Papageorgiou/Papamichail2008仅publisher/TRB摘要层，Kotsialos2006作者全文相关方法、FHWA handbook检测与flow-control相关节，支持政策与离散执行/供给限制分开，不直接证明本次gap安全。本文不转用其配时/容量、不伪称新全文阅读，也未扩展1–2篇无必要综述。核心判断依赖本run时序与固定官方源码；一般资格仍需新经授权自然数据，非文献替代。

本轮纯算术命令 `.venv/bin/python artifacts/issue16_natural_gap_scope_20261015_v1/engineering/query_formula_check_v1.py` exit0；没有native API调用。初次source GET在沙箱DNS失败保留，批准的官方只读GET成功。一次并发显示在补充源码下载完成前看到MSVehicleType路径暂不存在，随后wait完成并直接读到文件；未据暂缺输出作结论。文档影响由主代理负责STATE/WORKLOG/PRB/Dashboard；本代理仅新engineering目录。下一步唯一决策：science评审这一个最小合同草案，再向用户明确呈现是否接受其责任边界。

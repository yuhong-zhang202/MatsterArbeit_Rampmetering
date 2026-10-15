# PRB-004 — 名义双车映射未获实际放行支持

**以下为原问题归档快照；当前状态与后续实测见末尾Issue12进展。原OPEN和未选择政策描述保留其历史适用范围。**

- **日期／阶段：**2026-10-12；两个已完成单seed原生三周期诊断的只读原因分析。
- **现象：**WAIT_DIAG01_V2和WAIT_BUDGET_W360_01各72s内C=applied C=E6、N3；三个唯一入口R0／R1／R2都在G，每周期1辆，真实y／r过线0。两run相关轨迹相同，不是六个独立重复。
- **证据与版本：**[最小原因报告](../development/CANDIDATE_A_NATIVE_DISCHARGE_CAUSE_20261012.md)、[六周期小表](../../data/processed/candidate_a_native_discharge_cause_20261012_v1/SIX_CYCLE_SUMMARY_V1.csv)、[输入映射](../../data/processed/candidate_a_native_discharge_cause_20261012_v1/SOURCE_MAPPING_V1.json)、[科学限定复核](../../artifacts/candidate_a_native_discharge_cause_20261012_v1/FINAL_SCIENTIFIC_REVIEW_V1.md)。名义300veh/h不是R需求：本run需求M3600/R900/U360/X180、seed17、dt1、G3/y3/r18。
- **科研影响：**72s描述平均150veh/h不是稳定长期容量；E−N=3不能改E或计数消除。nominal_n=2明确UNQUALIFIED_DISCHARGE_ASSUMPTION，24s=3600×2/300只是映射，不是实测资格。
- **根因：**已观测次车起始静止、距线约8.502m、首G秒不动；三个周期3s绿末还差5.008／4.351／2.993m，后在黄灯逼近并停车，R1／R2下一绿灯才过线。支持排队起步／跟驰占用短G的解释；未记录getStopSpeed、有效模型ID或最终内部决策，不能唯一归因某native分支／tau。未发现N硬限一辆、丢计数或WAIT设车速；首黄秒旧接收已可用，不支持持续下游阻塞唯一解释。
- **采取的方案及效果：**仅提取既有轨迹、核对FCD／TLS／ACK及原入口计数；原E6/N3、失败和模型／相位不改。未新增SUMO。对300单点延长G仅旧报告建议，不是已验证解决方案；n2/y3/最低r2在900对应8s周期，不能全局加G便假定300–900可达。
- **最终状态／停止条件：**OPEN。未证明当前执行政策实现ALINEA目标率，Candidate A仍NOT_QUALIFIED；先完成文献与执行域检查，不因想要N2而改写数据或研究设计。
- **下一链接：**[Issue #12](https://github.com/yuhong-zhang202/MatsterArbeit_Rampmetering/issues/12)负责文献驱动政策选择及有界工程验证；当前尚未选择新政策、实现或启动。Stage6既有结项不重开，正式协议仍未冻结。

**主要来源快照 SHA-256：** `8d35a75645acc9234970f86e2fbec8b14dec3f94dbdbfc5124956870263eda91`（CANDIDATE_A_NATIVE_DISCHARGE_CAUSE_20261012.md；归档时校验，不替代该报告引用的原始证据）。

## 2026-10-12 Issue12 有界后续证据

旧G3/E6/N3结果保持。新fixed24/FIX300实测每周期G4/Y5/red15两辆、三个周期C=E=N6；旧helper duration FAIL及修复保留。900长G6前缀被原9+1.1 current-gap合同拒绝（N2/C1.5/E0），没有证据证明900物理不可达。后续只改phase的两车包T8/Gmax4/Y2/red2单次1272诊断，九周期实际各2辆，C=appliedC=E=N18；原硬检查不放宽，未重试。工程/独立数据/只读科学postreview已完成，GO技术交付并停止追加native，当前状态限定MITIGATED而非全域资格CLOSED。450/600/750、长窗/多seed/连续ALINEA仍未验证。参见[完整交付](../development/ISSUE12_EXECUTION_POLICY_DELIVERY_20261012.md)。

---

## 2026-10-15 版本化补充：从名义双车不足到有限动态／真实反馈核验

### 当前状态与阅读边界

**MITIGATED：获批的最小动态＋同版本短真实ALINEA技术节点已完成；不是全域服务资格通过。** 上面的10月12日原文保持为历史快照，其“未选择政策／尚未运行／仍缺闭环”等描述只对应当时版本。当前权威收口见[完整技术报告](../development/DYNAMIC_AND_REAL_ALINEA_TECHNICAL_CLOSEOUT_20261015.md)及[科学终审](../../artifacts/dynamic_native_yellow_minqual_20261015_v1/SCIENCE_FINAL_POSTREVIEW_V1.md)。总体Candidate A仍`NOT_QUALIFIED`，A1仍`UNRESOLVED`；Stage6既有结项不重判，正式协议仍空且未冻结。用户／Chat尚需审查此有限技术交付，不以AI自检或科学GO代替用户验收。

这条问题记录追踪同一个核心问题：**控制器要求放多少车，信号名义安排多少车，车辆实际上通过多少车，三者是否一致。** 后续经历了服务窗口失败、短绿起步不足、整数映射残差和动态适用性阻断；它们有联系，但不是一个软件bug的多次重现。以下按实际版本说明发现、调查、依据、处理和结果，不把旧单点拼成同版本因果效应。

### 1. 如何发现：先分清三层量，再定位缺口

`r_ALINEA`是原控制器自身限幅后的请求，还没有经过信号周期量化；例如请求750 veh/h，不等于匝道需求qRamp=750。后续诊断通常保持M3600/R900/U360/X180、seed17、dt1，改变的是执行请求或独立版本的执行政策。[统一运行范围与版本报告](../development/UNIFIED_ALINEA_ACTUATOR_VALIDATION_REPORT_20261013.md)。

- **原始累计请求C：** 实际控制窗口内请求的时间积分，单位为车辆当量；包括等待下个周期应用的新请求。
- **完整包计划E：** 只累计已经完整观察的周期配额；每包计划2辆并不证明实际2辆。
- **真实放行N：** 逐车入口与FCD／跨线记录独立核对，包括黄灯额外入口和末部分周期实测车辆，不截成quota。
- **名义映射／已应用量：** 依具体版本解释。最终累计版本的`C_applied`是选中周期名义速率7200/T的积分，不是把原始请求延迟后的积分，更不是实际N。历史最近档参考也不能充当新累计政策输出。

差额必须分开：C−N是主要请求跟踪量；C−E包含量化、边界应用及时间支撑影响；E−N只有在完整／部分观测范围匹配时才能解释。未进入控制区的项目是null，观察到没有入口才是0，部分周期保留已测数值而不补成完整包。[累计账设计V2](../development/CUMULATIVE_DISCHARGE_TRACKING_DESIGN_20261014_V2.md)、[最终字段定义及实际结果](../development/DYNAMIC_AND_REAL_ALINEA_TECHNICAL_CLOSEOUT_20261015.md#3-动态300750900300实际结果)。

**更早的FIX02背景不能被本次短诊断覆盖。** 2026-10-07的12个FIX02控制运行整体服务能力NOT_QUALIFIED；[1200,3000)的72个持续供给300秒窗口中71失败、1通过。数据、观测安全和控制规则通过，并不等于指令得到实际实施。R900组4200秒仍有残留，成本截断；拒绝秒数也不能直接换算为少放车辆的唯一原因。[PRB-001原问题](PRB-001_FIX02_SERVICE_TRACKING.md)、[开发总结](../development/DEVELOPMENT_TRIAL_SUMMARY_20261007.md)。这与下文的`CA_I12_QUOTA_R300_S17_FIX01`不是同一“FIX”版本。

### 2. 2026-10-12：名义两辆首先被实测否定

旧两次运行`CA_NATIVE_PHASE_R300_S17_WAIT_DIAG01_V2`与`CA_NATIVE_PHASE_R300_S17_WAIT_BUDGET_W360_01`，均为3个24秒周期，G3/y3/r18。各自72秒C=applied C=E6、N3，每周期仅1辆；两者相同seed及相关轨迹相同，不能作为六个独立随机重复。等待修正和增加技术预算使程序能够完成周期，却没有增加已测实际服务能力。[原因报告](../development/CANDIDATE_A_NATIVE_DISCHARGE_CAUSE_20261012.md)、[PRB-003等待与预算边界](PRB-003_RECEIVER_WAIT_AND_BUDGET.md)。

调查没有发现N被硬限为1、漏掉已跨线车或WAIT调用速度setter。第二辆起始静止、距线约8.502m；3个周期的3秒绿末仍差5.008／4.351／2.993m，随后在黄灯逼近并停下。**直接证据是短G窗口内没有走够，不是已经唯一识别SUMO某个tau／随机分支。** 有效内部模型决策未完整观测，不能把推断写成已证根因。300 veh/h名义映射24=3600×2/300只用了“每周期2辆”的假设；实测3×3600/72=150 veh/h也只是该72秒窗口平均，不是稳定容量估计。[同一原因报告及逐周期来源](../development/CANDIDATE_A_NATIVE_DISCHARGE_CAUSE_20261012.md)。

必要后续是重新审查**信号执行政策**，并用实际计数和完整相位核验，而不是改E、补N或调种子。首个fixed24诊断在1210秒因旧helper不支持`setPhaseDuration`停止；修复官方API桥接后，`CA_I12_QUOTA_R300_S17_FIX01`实际完成3个G4/Y5/red15周期，各2辆，C=E=N6。失败身份保留，不能把技术修复前缀并入修后结果。[Issue12完整交付](../development/ISSUE12_EXECUTION_POLICY_DELIVERY_20261012.md)。

### 3. 文献／官方依据支持了什么，没有支持什么

以下使用**2026-10-12已核原文的项目记录**，本次仅核对该记录及相关技术报告，没有重新下载论文或宣称新完成全文审阅。[唯一文献索引，含取得层次与访问失败](../../artifacts/issue12_alinea_actuation_20261012_v1/literature/REFERENCES.md)。

| 来源及既有获取层次 | 对本问题实际有用的依据 | 不能据此作出的主张 |
|---|---|---|
| Papageorgiou与Papamichail，2008，*Overview of Traffic Signal Operation Policies for Ramp Metering*；只核出版社／TRB摘要，未取得全文。[DOI](https://doi.org/10.3141/2047-04) | 流率控制策略与one-car／n-car等信号执行政策须区分 | 不能引用未读全文来指定本场景绿灯秒数或保证每周期2辆 |
| Kotsialos等，2006，*Discrete release rate impact on ramp metering performance*；既有审核取得作者公开全文并读相关方法段。[DOI](https://doi.org/10.1049/ip-its:20055003) | 连续ALINEA请求可经离散率实施，量化影响和ALINEA原previous-request状态应分开 | METANET情境不提供本SUMO微观起步／黄灯实际能力；其偏差结论不无条件适用于供给、接收或饱和约束 |
| Dadashzadeh与Ergun，2019；既有审核读机构公开全文。[DOI](https://doi.org/10.3390/su11226326) | g=(r/rsat)C说明流率需要实施换算 | 未标定rsat及startup时，不能用该式保证N；其VISSIM／公交情境和秒数不能直接移植 |
| Wang与Liu，2014，*The Minimum Yellow Timing for Ramp Meters*；既有审核读作者全文及出版社摘要。[DOI](https://doi.org/10.1260/2046-0430.3.4.365) | 黄灯适用性依赖接近车辆、排队、距离与动力学，不能只按目标流率选时长 | 文中特定情境约3.6秒不是此项目无条件下限，也不是Y2／Y3安全认证 |
| FHWA官方*Ramp Management and Control Handbook*正文，§5.3.6等。[官方章节](https://ops.fhwa.dot.gov/publications/ramp_mgmt_handbook/manual/manual/5_1.htm) | 实际passage检测可以结束绿灯，适合核对真实n而不只假设n | 现实手册能力范围不是本SUMO的资格证据 |
| SUMO官方信号／TraCI文档及固定1.26源码。[相位机制](https://sumo.dlr.de/docs/Simulation/Traffic_Lights.html)、[setter](https://sumo.dlr.de/docs/TraCI/Change_Traffic_Lights_State.html)、[固定源码](https://github.com/eclipse-sumo/sumo/blob/fa7df22d7f1c4ae245192ecc32410a49f1ffb2a3/src/microsim/MSVehicle.cpp#L3711-L3727) | 预定义G/y/r、`setPhase`／`setPhaseDuration`及program／phase／nextSwitch读回；原生黄灯按制动可行性处理停车或通过 | 使用官方API不证明当前轨迹无风险；固定源码与本机二进制编译等价性未验证 |

由这些原则形成的工程方案是：沿用原生G→y→r；以真实过线quota结束G、设置最大G截止并把剩余红灯绑定回周期边界；N保留额外黄灯入口，不强制等于2。未知饱和率不靠臆造rsat填补。具体参数选择、检查合同和运行仍分别需要项目证据、批准及三方门，文献不提供这些授权。[Issue12政策取舍与来源](../development/RAMP_METERING_SIGNAL_POLICY_DECISION.md)。

### 4. 从短两车包到750的两种缺额：不能只看E=N

Issue12的fixed24／quota6高率前缀在1206秒、N2时被既有current-gap合同拒绝，尚无完整周期。该合同包含同参数query与额外1.1m；拒绝不证明900物理不可行。后续独立`CA_I12_PACKET_R900_S17_DIAG01`采用T8/Gmax4/Y2/red≥2，完成9周期／72秒，每周期实际两辆，全绿入口，C=applied C=E=N18。当时硬合同未放宽，但只是该seed短窗，不证明混合切换或全部速率。[Issue12实际记录](../development/ISSUE12_EXECUTION_POLICY_DELIVERY_20261012.md)。

整数最近档库T=8…24按7200/T选率，750最近档为720/T10。原统一750中，`UA_FIXED750_S17_01`在1265秒被严格制动检查停止；随后**显式获批的受限数值例外**只允许完整绑定、匹配固定源码1mm Euler表达式的诊断分类继续。实际−4.501m/s²和旧严格FAIL原样保留，不是提高通用制动上限，也没有唯一识别内部私有分支。[统一版本／数值例外报告](../development/UNIFIED_ALINEA_ACTUATOR_VALIDATION_REPORT_20261013.md)。

修后`UA_FIXED750_S17_02`为64源`ea180197…`，请求750→映射720，T10/G4/Y4/red2；1200–1270七完整周期E14/N13，实测13×3600/70≈668.57 veh/h。末周期R13在新G前距入口8.561278664331m，四个G步只走8.042648804400m，到ACK1264还差0.518629859931m；ACK1265首黄步的−4.501发生在缺额已经出现之后，不能倒过来解释此前没有走够。[独立七周期／末周期调查](../development/UA_FIXED750_SHORTFALL_CAUSE_ANALYSIS_20261013.md)。

队列有车，七周期相位／ACK／Euler位移／入口核账一致，没有证实漏计、提前关绿或WAIT速度干预的软件bug；Krauss私有安全速度和随机数未唯一观测。**结论是本次起步／跟驰轨迹没在G4走够；不是宣布SUMO模型错误，也不是750必然不可行。** 该调查因此没有做无依据的代码“修复”。

经单独黄灯适用性审核和批准，后续只为T10建立Gmax5/Y3/redmin2候选，quota提前达到仍早关G。资源STOP身份`UA_T10_G5Y3_FIXED750_S17_02`在ACK1038因300MB门停止，未到1200，C/E/N为null；其失败不能算G5有效或无效。用户另行批准取消固定字节门、保留监控／实时5GB／严格安全后，新03才完成实际核验。[资源问题及G5/Y3完整报告](../development/T10_G5_Y3_NATIVE_CONTINUATION_REPORT_20261013.md)。

`UA_T10_G5Y3_FIXED750_S17_03`（执行提交`ec2e13f7…`、卡`9daacfd2…`、96源`aaa47f98…`）到1270：7周期E=N14，前六G4/Y3/R3、末G5/Y3/R2，R13确在第五G步跨线。14车尾／1337正常离网末步／EOF独立核查通过，最低制动−4.5，无数值例外。**它改善了本样本E−N，但14×3600/70仍为720，比原750低4%。** 原请求C=175/12、N14，C−N=7/12；固定最近档重复更久不能消除这项30 veh/h映射偏差。这一代码／算术推断与新原生观察分开记录。[同一实际报告及独立审查链接](../development/T10_G5_Y3_NATIVE_CONTINUATION_REPORT_20261013.md)。

### 5. 累计补偿：用原C和真实N选包，不用名义包掩盖物理不足

用户随后明确目标是原始ALINEA请求的长期平均，不接受把750改称720后宣布匹配。累计方案保留原ALINEA公式、30秒时钟和自身clipped previous-request；在完整周期边界依据真实D=C−N，对候选T比较`D+当前请求×T/3600−2`，选绝对预测差最小的完整包，平局取较低率。预测假设不冒充未来请求；中途新请求继续积分，真实首G ACK后才记应用。完整包实际N≠2或未知时停止调查，不以更快包无限追物理欠债。[设计V2](../development/CUMULATIVE_DISCHARGE_TRACKING_DESIGN_20261014_V2.md)。

最初仅T8/T10库的`UA_CUMULATIVE750_S17_01`（111源`b351723a…`）在1272首黄前按旧见证UNKNOWN停止。首48秒C=E=N10；全前缀72秒C15/E14/N15包括末部分包，不能以终点C=N宣布两块完成。末T8部分包尚未观察黄／红，相关phase metrics为null；第二48秒块未完成，但其中此前完整包已有黄／红观察。后来扩回原T8…24完整库、保留T10既有特例，而不是孤立反复试T9或更改车辆参数。[原失败报告](../development/CUMULATIVE_TRACKING_NATIVE_REPORT_20261014.md)、[完整目录计划](../development/CUMULATIVE_FULL_CATALOGUE_PLAN_20261014.md)。

`UA_CUMULATIVE_FULL750_S17_01`（卡`da64599b…`、125源`c4787966…`）在1200–1296实际选择`[10,9,10,9,10]×2`，两个48秒块各C=applied C=E=N10，合计20辆／96秒=750 veh/h；20车尾／1374正常离网末步／EOF受检通过。实际每包G4/Y3，T10红3／T9红2；本轨迹没用到T10第五G，不否定其他轨迹需要它。两个块属于同一次运行，不是两次随机重复；125文件为当时未提交的精确源码快照，不能说基线commit已经包含它。[完整750实际报告](../development/CUMULATIVE_FULL_CATALOGUE_NATIVE_REPORT_20261014.md)。

### 6. 固定750成功后，为什么动态仍会停；后来改变了什么

| 执行版本／独立身份 | 实际观察与停止 | 调查、处理及不能作出的外推 |
|---|---|---|
| 136源`5d069519…`，`UA_CUMULATIVE_FULL_DYNAMIC_S17_01` | 1233按旧current-gap门STOP；C169/24、完整E4、N5，最后300尚未请求；R4车尾截断 | R5净距2.095152216m、query1.022884125m，加1.1需2.122884125m；不足0.027731909m不是新容差。绑定／单位／minGap未发现bug，不能说发生碰撞或SUMO原生不安全。另有已生成应用事件未flush、reader遮蔽／黄灯目录错误；必要修复保留原FAIL与缺事件UNKNOWN，不能追补raw改判成功。[历史动态报告](../development/CUMULATIVE_DYNAMIC_NATIVE_REPORT_20261014.md) |
| 141源`dfdddab7…`，`UA_NATIVEGAP_DYNAMIC_S17_01` | 新current-following分类实际生效，但1236首Y前触发另一条旧黄灯见证UNKNOWN；C187/24、完整E4、N5，末300尚未发生 | 溯源确认额外1.1m是历史工程裕量，代码忠实保留并非算错。用户明确批准后，仅current-following把“通过query但不足额外裕量”改为留告警；同参数query硬底线及严格新G准入保留，不能偷偷改query参数或称其通用安全标准。旧1233STOP不改判。[依据及原合同边界](../development/DYNAMIC_ACTUATOR_MINIMUM_QUALIFICATION_PLAN_20261015.md)、[141实际报告](../development/DYNAMIC_MINIMUM_QUALIFICATION_NATIVE_REPORT_20261015.md) |
| 新黄灯合同提案，尚未运行时的责任评议 | 1236的R5距线约0.146m、v约4.973m/s；原表达式清尾2.558s>Y2，停车见证也不成立 | 完整输入不等于未来必危险。项目见证尚未证明是原生机制必要条件或严格充分条件；匀速估计约1.035s同样不能预测。由前置阻止改为原生运动＋后续监测，是实质责任变化，不能伪称普通bug修复；一个步内的事件不能被事后监测撤销。[完整责任提案](../development/DYNAMIC_YELLOW_MINIMUM_DECISION_PROPOSAL_20261015.md) |

1.1m处理和黄灯处理分别有明确用户批准；仅获批的隔离诊断版本采用新合同。新黄灯模式必须是严格布尔True及精确policy，缺失／错绑／不完整／非有限输入继续硬STOP；只有联合绑定完整而两项工程见证均不成立时，保留原UNKNOWN／原行／数值，另外记录`DIAGNOSTIC_WITNESS_NOT_ESTABLISHED`后由原生相位处理。碰撞、异常制动、红灯新入口、接收、身份／模式／相位／人口／车尾／日志及其他UNKNOWN门不被吞掉；不改G/y/r、车辆模型、quota或Feedback。[直接黄灯批准及限制](../../artifacts/dynamic_yellow_contract_proposal_20261015_v1/USER_APPROVAL_V1.json)、[最终实际收口§1](../development/DYNAMIC_AND_REAL_ALINEA_TECHNICAL_CLOSEOUT_20261015.md#1-目标权限与最小解决方案)。

### 7. 2026-10-15：同154源的动态与真实ALINEA分别验证到什么程度

两次运行均为执行提交`3d82ed578e4e5e028ed3db14e596bd44e845956b`、共同154源摘要`089a2fefb9fb4d68aced499b532636c3a551b672f9130a1fd2e6acb468ff4ae2`、seed17、控制1200–1296。不是用旧固定750替代新动态／闭环。以下结果均完成工程→独立数据→只读科学实际后审。[完整收口及准确环境／命令](../development/DYNAMIC_AND_REAL_ALINEA_TECHNICAL_CLOSEOUT_20261015.md)。

**Dynamic：`UA_NATIVEYELLOW_DYNAMIC_S17_01`，卡`53ffc491…`。** 原请求300@1200、750@1201、900@1226、300@1237，实际首次应用1200／1224／1232／1240，延迟0／23／6／3秒。六完整包各N2、完整E12；末T24[1285,1309)只观察到1296但已N2，全窗口C311/24≈12.9583、N14、C−N=−25/24。最后300应用时正欠额55/24，在后续完整边界依次回落到23/24、1/24、1/24，支持本条有限轨迹的累计恢复，而不是仅exit0或任意时刻强迫C=N。[独立Dynamic后审](../../data/processed/dynamic_native_yellow_minqual_20261015_v1/native_dynamic_v1/DATA_NATIVE_POSTREVIEW_V1.md)。

第三T8实际是绿灯1辆＋黄灯1辆，不能篡改成双绿；1236原黄灯见证UNKNOWN仍在，新合同下该Y运动才被实际观察。7次firstY／14入口与车尾／1372正常离网末步／EOF受检通过，最低速度差和加速度−4.5。该观察不能认证所有Y2状态安全。`C_applied=155/12`是选包名义积分，完整E和全窗口N支撑不同，E−N=−2不解释为“多放两辆的完整包错误”。[Dynamic科学后审](../../artifacts/dynamic_native_yellow_minqual_20261015_v1/SCIENCE_DYNAMIC_POSTREVIEW_V1.md)。

**真实ALINEA：`UA_NATIVEYELLOW_ALINEA_S17_01`，卡`36d30fff…`。** 动态实际技术门和资源结算后，才以相同154源做条件闭环。使用项目原Feedback：目标11%、增益70 veh/h/百分点、30秒更新、clipped300–900、初值900；这是development reference，不是本问题新选参数。两条下游20m E1分别为`p1_main_down_20_l0/l1`；独立重建三个30秒窗及ongoing车辆事件，不以模式名冒充真实反馈。[ALINEA数据V2后审](../../data/processed/dynamic_native_yellow_minqual_20261015_v1/native_alinea_v2/DATA_ALINEA_POSTREVIEW_V2.md)。

| 决策时刻 | 独立两车道平均占有率 | 原始clipped请求veh/h | 实际首次应用 |
|---:|---:|---:|---|
|1230|8.477807332%|900|1232，延迟2秒|
|1260|11.255823327%|882.092367085|1264，延迟4秒|
|1290|12.007010804%|811.601610838|截止1296仍PENDING，不伪报应用|

Feedback使用自己的前一clipped请求，不回灌映射率或实际N；1290未应用请求仍进入原始C。11完整包均N2，最后T8[1289,1297)只观察G4/Y2/R1但已N2。全窗口C≈23.7034390771、N24、完整E22、C−N≈−0.2965609229；选周期名义积分`C_applied=23.75`单列。实际经历T8→T9→末部分T8；24入口均G、24车尾／1376正常离网末步／12次firstY／EOF受检通过，最低制动−4.5且无数值例外。此ALINEA样本没有原黄灯见证失败，不能重复声称它验证了Dynamic的UNKNOWN继续路径。[有限ALINEA数据摘要](../../data/processed/dynamic_native_yellow_minqual_20261015_v1/native_alinea_v2/FINITE_ALINEA_SUMMARY_V1.json)、[科学终审](../../artifacts/dynamic_native_yellow_minqual_20261015_v1/SCIENCE_FINAL_POSTREVIEW_V1.md)。

原ALINEA绑定reader实际exit1也必须保留：首个redACK1296恰为终点，bridge不再执行下一prepare／duration setter，而旧审计器要求该未执行的setter双记录。只在新processed后分析副本中以末partial、真实双ACK、native nextSwitch1297、无下一PRE／无setter等联合事实处理终点；较早缺失、错clock、伪completed或残缺已执行setter仍拒绝。受影响子集旧FAIL／新1方法PASS及必要负例保留；新版同raw完整审计一次exit0，不重跑SUMO、不改154源／卡／raw，也不宣称原reader通过。[工程独立边界复核](../../artifacts/dynamic_native_yellow_minqual_20261015_v1/engineering/analysis_boundary_review_v1/ENGINEERING_ANALYSIS_BOUNDARY_REVIEW_V1.md)。

### 8. 如何判定“问题缓解”，以及仍未解决什么

**已确认的有限改善：** 旧750版本观察13/14，新G5/Y3单点观察14/14；两者是独立版本的有限观察，不是单参数配对因果估计。累计完整库在一次750／96秒实现20/20；最终同154版本的四请求实际应用／正欠额恢复及真实E1→Feedback→执行器→独立N链路完成有限技术核验。它们各有版本和窗口，不能合并成全域试验。

**仍未证明：** 长期平均误差在全部原始连续300–900请求及未来历史下保持可接受；所有库周期／供给接收条件／多seed的实际能力；一般安全或完整执行器资格；正式freeway benefit／urban cost／sweet spot。末AFTER非活动池缺同刻下一PRE时仍为单日志来源，SUMO私有分支及源码／二进制等价未验证；正常离网最后一步依赖事后审计而非完全在线预防。[最终科学限制](../../artifacts/dynamic_native_yellow_minqual_20261015_v1/SCIENCE_FINAL_POSTREVIEW_V1.md)。

本节点因此保持**MITIGATED、有限技术完成／待用户与Chat审查**，不记作全域CLOSED／QUALIFIED，不反向改判FIX02、STOP3、旧13/14或其他STOP。三次同600秒账（旧native-gap失败＋两个新成功观察）已结算475.645467625秒、余124.354532375秒；余额不是追加运行理由或权限。[最终资源账](../../artifacts/dynamic_native_yellow_minqual_20261015_v1/RESOURCE_ACCOUNT_FINAL_V1.json)。

原始日志只读保存在各本机`data/raw/<stage>/<run>`目录，公开报告、派生审计和文件级manifest供查阅，不假称完整raw在线可访问。最终新Dynamic为203文件442183368B，ALINEA为204文件442380604B；完整manifest链接见下表。后续如复用，须把已审终点边界处理纳入新版本reader重新绑定，不能沿用已知会失败的原绑定reader并称已修。下一位为用户／Chat审查；任何进一步开发、资格容差或正式实验须按对应批准边界决定。**本记录建议不构成执行授权。**

### 9. 可复核来源快照与本次整理范围

本次补充只整理已有受审证据，未重新跑测试／SUMO、未改代码、guard、研究设计或原始数据。上方原归档全文按原字节保留；补充前PRB-004 SHA为`78f6fce6a728f91af933bcd545e34d570cbf56c85dc6ffff30ee195c7eff6e8f`。以下SHA在本次整理时按本地文件实际读取，代表引用快照，不代替其指向的原始审计；后续修改须新版本记录。

| 来源 | SHA-256 |
|---|---|
| [FIX02开发总结](../development/DEVELOPMENT_TRIAL_SUMMARY_20261007.md) | `8d09c930b33ea49573134ab114435df6f47f73a3e167efbaef75565b816fcdb0` |
| [G3双车原因报告](../development/CANDIDATE_A_NATIVE_DISCHARGE_CAUSE_20261012.md) | `8d35a75645acc9234970f86e2fbec8b14dec3f94dbdbfc5124956870263eda91` |
| [已核文献索引](../../artifacts/issue12_alinea_actuation_20261012_v1/literature/REFERENCES.md) | `5aedde5867b5005a9f95e32e42f39deb401debcf4e3d4549910d9a22d609d4c1` |
| [Issue12政策记录](../development/RAMP_METERING_SIGNAL_POLICY_DECISION.md) | `42773a72ac9dace0259da46227757e8760a2072eb386730d7c147cb6ff73c5c4` |
| [750缺额调查](../development/UA_FIXED750_SHORTFALL_CAUSE_ANALYSIS_20261013.md) | `c814a1b456e739a2fab4e2d8a855d74eff1e3efc053c4693513e8d59e93f86d3` |
| [G5/Y3新03报告](../development/T10_G5_Y3_NATIVE_CONTINUATION_REPORT_20261013.md) | `3f9be272e856c5d7efed6ccb7822078b14466e46c9bf4bcfe1546ed647094a5b` |
| [完整库750实际报告](../development/CUMULATIVE_FULL_CATALOGUE_NATIVE_REPORT_20261014.md) | `6398b0642b0c15492075d0aa95d9e21b1903ead99142ce24b11bf5b7432f37ca` |
| [Dynamic新原始manifest](../../artifacts/dynamic_native_yellow_minqual_20261015_v1/engineering/native_execution_v1/UA_NATIVEYELLOW_DYNAMIC_S17_01/RAW_FINAL_SHA256_V1.json) | `6793f677b0f4ddb29d61ece72da56fb3612bbf37c94f9a89a6e9d5504087ab15` |
| [ALINEA新原始manifest](../../artifacts/dynamic_native_yellow_minqual_20261015_v1/engineering/native_execution_v1/UA_NATIVEYELLOW_ALINEA_S17_01/RAW_FINAL_SHA256_V1.json) | `879ec71f1bad2e6aebbb637a98c7fddb014306efd246d0f1ad4377804944cb04` |
| [10/15技术收口报告](../development/DYNAMIC_AND_REAL_ALINEA_TECHNICAL_CLOSEOUT_20261015.md) | `508e84417a78e83c3e63df4a6ed73f003949bc81e7985f78082d6a2aa1597a61` |
| [最终科学后审](../../artifacts/dynamic_native_yellow_minqual_20261015_v1/SCIENCE_FINAL_POSTREVIEW_V1.md) | `c785f9868a3c5d6e0378dd1b61e8d90883ffbf6eeded7e58cf3a422b86f8ecd2` |

Documentation Impact Check：本代理只扩充本问题记录；PROJECT_STATE／WORKLOG及问题索引的必要同步由主代理负责。DECISIONS、EXPERIMENT_PROTOCOL、导师反馈、README、AGENTS、论文结构及其余问题文件未由本任务改写。

### 10. 后续P1与自然需求资格目标（2026-10-15）

PR13实际审查`9a9c96ed…`指出：上一完整周期N<2并不证明执行器故障，空供给、未就绪或接收受限均可能造成该结果。`6dc1680d…`新有限诊断入口已修正误归因并限定用途；其复审已完成，两项失败证据审计P2已修复并通过限定回归；该入口仍会中性停止，不能作为普通服务持续控制已解决的依据。[有限修复报告](../development/PR13_FINITE_SERVICE_SCOPE_FIX_20261015.md)。

用户随后明确要求继续实现可信论文所需的自然运行能力，而非停在有限诊断。当前工程方案将原始C、名义调度机会E_scheduled、真实应用及N分开，拟以C−E_scheduled校正量化，不让物理短放E_scheduled−N驱动追债；受限条件保留观测，真实安全／UNKNOWN仍停止。方案已获科学允许离线实施，新namespace实现及3组合＋1终点方法已通过必要离线验证；独立reader五保存案例／十反例通过，科学终审允许准确head的限定离线复审。真实自然交通尚未测试。[新授权](../../artifacts/thesis_actuator_readiness_20261015_v1/USER_AUTHORITY.md)、[文献及官方依据](../../artifacts/thesis_actuator_readiness_20261015_v1/LITERATURE_AND_METHOD_BASIS.md)、[精确工程提案](../../artifacts/thesis_actuator_readiness_20261015_v1/engineering/PROPOSED_IMPLEMENTATION_V1.md)。

自然候选复用既有4050车、4200秒、600秒起控输入；旧154人为600–1200蓄队不能冒充自然需求。真实资格仍NOT_TESTED／总体NOT_QUALIFIED。900秒墙钟预算仅提案，旧600秒实耗475.645秒及124.355余额保持；不得重置旧账或把最多两次身份直接当精确预算/运行放行。后续实际结果须新版本追加，不覆盖前述历史FAIL、STOP及有界改善。

本轮最新限制为不运行SUMO、不合并PR。普通服务新实现、P2处理、失败保留及精确版本边界见[PR13修复交付](../development/PR13_ORDINARY_SERVICE_REVIEW_FIX_20261015.md)；旧finite与154实测不混作新实现资格。

24ec690d精确复审5527104163已完成：新增三项失败／时序证据P2（setter部分应用持久化、command生命周期完整绑定、later-hard原因绑定），并未报告新的N0/1误停或物理追债缺陷。第二轮三项限定修复及必要离线工程／data／science复核已完成，待准确新head复审；review未指出某问题不等于安全或自然资格认证。实际finding见[本轮回执](../../artifacts/thesis_actuator_readiness_20261015_v1/PR13_REVIEW_24EC_V1.json)。

第二轮review5527262368精确审查5b08d28f，剩一项逐row pending ID／rate语义校验P2。仅补这两字段及原保存材料反例，不更改控制政策；到两轮上限停止自动扩审与资格推进，最终小修与最后实际review源分开。[末轮回执](../../artifacts/thesis_actuator_readiness_20261015_v1/PR13_REVIEW_5B08_V1.json)。

最后pending两字段已修；5保存材料／2指定反例0.314秒通过，科学仅GO小修交付。修后reader只由新58项e08cc79a绑定说明，不以5b08远端review冒充修后已审。达到两轮上限，停止自动扩审／资格推进；需要第三次仅此字段定点review时交用户明确指示。自然资格仍NOT_TESTED。[最后修复记录](../../data/processed/thesis_actuator_readiness_20261015_v1/final_pending_fix_v1/DATA_REPORT_V1.md)。

### 11. 用户批准定点复审，资格准备独立依赖（2026-10-15）

用户已明确批准追加一次仅pending三行的定点复审。[请求6191040336](https://github.com/yuhong-zhang202/MatsterArbeit_Rampmetering/pull/13#issuecomment-6191040336)指定PR13 head `61612bf6e240d41d2ca4be95a02429f48c9ddd54`；在未收到实际回执前仍标待审，不将eyes当完成，不扩大成第三轮完整矩阵。上文“待用户指示／停止资格推进”属于该批准前的快照。

完整目标继续落实为唯一[Issue #14](https://github.com/yuhong-zhang202/MatsterArbeit_Rampmetering/issues/14)，新分支以PR13为上游，准备原生审计、精确卡和资源／进程保护。原普通服务政策不变，bridge仅允许必要启动进程身份记录；旧154源及其成功／失败不改判。设计科学GO仅允许非运行实施，不认证实际安全或持续服务。当前仍MITIGATED、自然资格NOT_TESTED／总体NOT_QUALIFIED；新增独立900秒仍提案，旧124.355秒不pool，不运行SUMO、不合并。实际交付及必要离线验证见[资格准备说明](../development/NATURAL_ACTUATOR_QUALIFICATION_PREPARATION_20261015.md)。

资格准备现已完成原生七域实现／必要离线验证／独立schema复核／科学终审。唯一首卡b73c6781（checkpoint b6c60b9，173源摘要c2f00d7f）prepare／validate exit0且实际字段三方GO；[Draft PR15](https://github.com/yuhong-zhang202/MatsterArbeit_Rampmetering/pull/15)正确依赖PR13。卡仍未释放、观测全null、无新raw／新增预算批准／canonical。第一身份900总额仍仅提案；PR13定点review仍Running。后续只有真实人类预算与此卡运行放行等全部门有效才可一次技术验证，状态仍MITIGATED／自然NOT_TESTED／总体NOT_QUALIFIED；不能以这次实现交付关闭服务问题。


### 12. 自动审查无结论与非运行准备交付（2026-10-15）

按用户最新指令，616本轮记录为REVIEW_PENDING / NO_VERDICT，不记PASS或CANCELLED，不再新发review。已完成的普通服务修复、限定回归及内部科学准备GO仍按原版本和范围有效；非运行准备不依赖外部review完成。原生七域实现、首卡、三方准备核查及独立资源保护均已交付，本次14项准备文件hash无漂移、运行源无改动。未发现剩余独立非运行实施项。独立900及准确首卡有条件批准已经存在（上文未批准是历史快照），但本次不改变执行条件；真实自然服务、安全及城市结果仍NOT_TESTED，问题MITIGATED／总体NOT_QUALIFIED。见资格准备说明及NONRUNNING_PREPARATION_STATUS_V1.json。


## 2026-10-15 首次自然交通173源实际诊断

**首次自然交通诊断已完成后审：STOP_RETAINED / NOT_QUALIFIED。** 精确卡b73／执行源b6／173源c2f00d7f唯一运行于650秒触发POST_CURRENT_GAP_BOUND_DENIED，未到4200秒及六评价窗。六完整周期N0均继续；独立C≈12.311518、E_scheduled=E_executed12、真实N1，物理短放保留。间距9.610494m低于同帧native查询13.089892m，证实规则触发，未证明碰撞、必然危险或保守误判。下游受限等待恢复、完整时域及长期放行率NOT_TESTED；原reader exit1/UNKNOWN、partial和车尾截断不改判。227raw文件封存，工程→data→science后审完成，科学仅允许资源结算。独立900预算实际账见资源回执；唯一启动权已消耗，不重跑、不正式实验、不合并。GitHub末轮仍REVIEW_PENDING / NO_VERDICT，用户仅撤销其完成作为本次额外门，不再复审。[完整证据及版本边界](../development/NATURAL_ACTUATOR_FIRST_NATIVE_CLOSEOUT_20261015.md)。原154源预排队短诊断不与此运行拼接，不因六个N0周期继续而认定全部普通交通已获资格。

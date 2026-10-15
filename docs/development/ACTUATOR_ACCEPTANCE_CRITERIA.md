# 执行器安全与真实放行精度：最小资格标准

状态：**PROPOSED 事前标准；本文不授予新合同、验收尺度或新运行批准。** 本文服务于 Issue #16 / Draft PR #17 的一次自然条件资格诊断，不是正式实验协议，也不是工业安全证明。旧 run02 继续为 STOP_RETAINED / NOT_QUALIFIED，数值跟踪精度仍为 NOT_ASSESSED。

## 1. 版本、问题与不可追溯改判的证据

本次起点为报告提交 `ad205d4098f9e00e4517ff5adf0347e134a9b75b`，run02 实际执行提交为 `daa149bd296e1ab24da82b47b03f33d7d3e6904a`、176 源摘要 `4eb466ec0a28f783089230941f1a6139ce9f0ed45a0e0dced82a7dc1e278d66f`，精确卡 `dc9c1ce418ab61eb4e36b26e1436c94b31ba78cde9a630df596a0e5a4ce4c509`。报告版本不能冒充执行版本。

R_flow.109 在 ramp_storage_0 的 1261→1262 首黄灯步，速度从 4.56232916440366 降至 0.06132916440365965 m/s；速度差/1s 与 getter 同为 −4.501 m/s²，超过旧门 4.5+1e−6，原两条 STOP 不变。部分外部状态与旧停车数值表达式相容；专用前后观测缺失，旧例外未启用，不能确认私有分支、数值误报、安全或危险。[原始版本的数据报告](../../data/processed/issue16_natural_gap_scope_20261015_v1/run02_native_v1/DATA_RUN02_REPORT_V1.md)、[科学后审](../../artifacts/issue16_natural_gap_scope_20261015_v1/SCIENCE_RUN02_POSTREVIEW_V1.md)。

[600,1262) 共 662s：C=133.17401344830656，E_scheduled=E_executed=132，N=109，C−N=24.17401344830656 辆；供给/接收/等待记录重叠，不能将 23 辆 E−N 全部分配给其中一因。首评价窗只有 62/300s，后五窗未到；不得用本次前缀挑选能通过的阈值。旧数据只作探索性规则设计/反例，不能成为新标准的独立验证集。[问题沿革 PRB-004](../problem_records/PRB-004_NOMINAL_TWO_CAR_DISCHARGE.md)。

## 2. 来源到决策（唯一登记表）

| 来源ID | 实际阅读范围与获取层级 | 直接支持什么 | 本项目采用及额外假设 |
|---|---|---|---|
| S1 SUMO 官方 | [CF](https://sumo.dlr.de/docs/Car-Following-Models/index.html) reaction/actionStep、tau、decel三参数；[Safety](https://sumo.dlr.de/docs/Simulation/Safety.html) collision/CF/junction；[TLS](https://sumo.dlr.de/docs/Simulation/Traffic_Lights.html) states/TraCI control；[Retrieval](https://sumo.dlr.de/docs/TraCI/Vehicle_Value_Retrieval.html) last-step、acceleration、position及gap/stop query。已读官方完整相关HTML，无页码；living docs并非1.26冻结文档 | Krauss正常decel被称为hard limit，同时另有紧急制动；黄灯停车/通过与接近状态有关；事后查询并非私有运动输入 | 保留正常4.5、紧急能力9、warning门三者区别；网页未要求任何轻微逐步超限必使整场科研实验无效。无warning仅表示未观察到配置告警，不证明无普通超限、冲突或数据缺口 |
| S2 SUMO v1_26_0，固定 `fa7df22d7f1c4ae245192ecc32410a49f1ffb2a3` | [MSCFModel.cpp](https://github.com/eclipse-sumo/sumo/blob/fa7df22d7f1c4ae245192ecc32410a49f1ffb2a3/src/microsim/cfmodels/MSCFModel.cpp#L849) 77–98/796–815/849–871；config.h.cmake229–233；Krauss101–125；MSVehicle2738–2776/3288/3712–3727/4908/4916–4928；MSFrame556–557等，固定官方源码已读及缓存hash复核。完整定位见[工程核查](../../artifacts/actuator_acceptance_20261015_v1/engineering/SOURCE_REVIEW.md) | stopping expression减距离epsilon；getter加速度本身来自速度差，二者一致不是独立物理证明；warning取决于普通/紧急能力及历史条件 | 仅条件式数值尺度，不认定实际私有分支。源码/已装二进制的编译等价未验证；卡继续绑定实际二进制与环境。模型/动作步/dt/参数不变 |
| S3 Treiber & Kanagaraj，2015，DOI [10.1016/j.physa.2014.09.061](https://doi.org/10.1016/j.physa.2014.09.061) | [作者预印本正文](https://arxiv.org/pdf/1403.4881)，PDF 第7–8页 §2.3–2.4（预印本页码，非期刊页码），并读 §4.3–4.4 第15–17页的非光滑轨迹讨论；实际取得全文，只读相关段 | 有限步积分在停车附近需要特殊处理；不连续轨迹改变精度与成本关系 | 用于解释为何要保留停车情境、步长与峰值。研究对象为连续时间跟驰模型；不能认证 Krauss/R109，不更换模型、步长或积分方法 |
| S4 FHWA-HRT-08-051，2008 | [Chapter 2 官方全文 HTML](https://www.fhwa.dot.gov/publications/research/safety/08051/02.cfm)，Workflow、Conflict Identification Algorithms、Terms and Definitions/Definitions of Surrogate Measures；HTML无印刷页码 | TTC/PET 用于定义冲突，冲突数量与各事件峰值/速度/位置等描述不同维度；MaxD 保留瞬时最小加速度 | 只保留现有可可靠读取的峰值、时长、间距、相位、入口/碰撞与相邻车辆记录；不部署SSAM、TTC预测器或照搬默认阈值。网页对DR/MaxD单位文字不严谨，本项目按加速度定义使用m/s² |
| S5 FHWA Ramp Management and Control Handbook | [Ch5](https://ops.fhwa.dot.gov/publications/ramp_mgmt_handbook/manual/manual/5_1.htm) §5.3.6/Table5-8单/多车及检测；[Ch9](https://ops.fhwa.dot.gov/publications/ramp_mgmt_handbook/manual/manual/9_1.htm) §9.2.3–9.2.5、§9.3.1–9.3.4/Tables9-2–9-5及§9.5，官方全文相关HTML，无印刷页码 | 单车感应方式由存在检测请求绿灯、通过检测结束绿灯，无车维持红灯；多车方式通常每绿2辆、有时3辆，但较长周期使吞吐不成倍增加。目标、车辆存在和实际通过须分别测量；评价覆盖匝道、高速与邻接道路 | 保留全系统原始误差与交通成本，再单列有服务机会时的精度。现场容量范围不作为SUMO资格证明 |
| S6 Kotsialos等，2006，DOI [10.1049/ip-its:20055003](https://doi.org/10.1049/ip-its:20055003) | [作者上传正文](https://www.researchgate.net/publication/3465157_Discrete_release_rate_impact_on_ramp_metering_performance)，§2.1–2.2 pp86–87，§3.1–3.3 pp87–88，§5 pp93–95；可见HTML正文及印刷页脚，未另验证出版社PDF排版 | ALINEA自身previous request、连续率与离散执行率分离；需求充分且约束未激活等是相关稳态结论的条件；METANET未显式模拟信号周期 | 保持原ALINEA；C−E_scheduled选包与不追回C−N是本项目工程政策，不冒称论文原算法。宏观结论不证明本微观放行能力，也不提供统一5%门限 |

S7 未新增读取或借用数值：既有 Papageorgiou/Papamichail 2008、Tak等2015只有摘要层证据；本次 S1–S6 已覆盖当前决策，不将摘要升级为全文，不扩展综述。

## 3. 制动事件分级：一个推荐合同（待批准）

实际记录的 Krauss 类型 `decel=4.5`、`emergencyDecel=9`、`tau=actionStep=dt=1s`；apparentDecel=4.5、Euler及native warning threshold=1来自固定源码默认值和无override配置推断，不能冒充专门getter观测。固定warning代码按超普通制动相对紧急余量的比例、历史加速度等条件判断，阈值1不是4.5。保留junction碰撞检查和完整日志EOF；无告警不足以证明普通制动合格。[工程配置和调用链核查](../../artifacts/actuator_acceptance_20261015_v1/engineering/SOURCE_REVIEW.md)。

**立即停止：** 现有全部车辆/道路/相位的碰撞、实际重叠或适用minGap侵入、违规新过线、相位/ACK不一致、必要车辆/车身/邻车/日志观测缺失、异常native告警等门保留。普通超制动若不满足下述窄条件仍停，称“超出获批诊断范围”，不因此宣称已证明真实危险。9m/s²不成为普通合格门限；不改变任何车辆、信号目录、黄灯长度或ALINEA核心。

**可受控继续的唯一候选：** 仅本卡受控storage车道首黄灯步，任意车辆ID/时刻/seed满足固定配置、仍在同一lane且没有新入口；保存原始峰值与旧严格失败。必须同时满足下面数值关系、完整前后观测、无并发硬风险，并获得新合同授权。标签为 `NUMERICAL_SCALE_COMPATIBLE`，不是“已证数值误差”或“安全PASS”。别的路段/相位不外推。

令动作步h、仿真步Δ（秒），正常减速度b（m/s²），该停车表达式中的距离修正εx=0.001m。固定Euler分支n的速度修正为 `−εx/(nΔ+h)`，相应加速度修正为 `−εx/[Δ(nΔ+h)]`。仅在n=0、h=Δ、单步制动域 `bΔ<v<2bΔ` 及条件式stop gap恰为Euler brakeGap的情形，得到 `v_next=v−bΔ−εx/Δ`、超额尺度 `εx/Δ²`。本卡Δ=1才得到0.001m/s²；不得直接把0.001m当加速度容差。

外部相容见证包括：速度域、车道末端距离、按固定源码可用stop-offset范围推导的offset、下一速度和Euler位移与条件表达式在原1e−6比较精度内相容；超额须大于旧比较精度且不大于 `εx/Δ²+1e−6m/s²`。这不声称观察到私有stopDist或唯一调用分支。POSITION_EPS=0.1m为offset夹持项；FCD8位输出舍入、浮点roundoff、时间离散误差与有意1mm距离修正是四件事，不互相冒充。

必须真实记录前后车辆及同车道前后邻车身份（或覆盖至已知边界的明确不存在）、位置/车长/路径间距/速度/加速度、实际相位/链接/ACK、native counters和日志游标。已批准的普通被动gap参考不足仍记录；不重新把它一律设为硬STOP，也不拿它作为“无风险”证明。不可读取的私有机制不是缺少关键风险观测；真实邻车或相位缺失则是。

未来获批后，候选只允许**下一步原样运动并复核**，不修改速度、相位或参数制造恢复。该步前后全部硬门仍有效；新超刹、缺观测或硬风险即停；EOF前未完成复核保持UNKNOWN。复核关闭仅表示该观测事件完成，全部事件仍需运行后逐项审查，保留峰值、时长、邻车、位置、频次、日志尾部。pending期间不得连续续放；一次已闭合后同车再次出现须重新满足全条件，逐次记录，不设置无依据的终身车辆ID否决。

S3仅支持停车数值处理需要情境，不认证上述Krauss事件；S4支持冲突与制动峰值/情境分开记录，不提供本阈值。上述受限继续是**基于固定源码、外部观测和研究用途的项目风险选择**，需您明确批准。新规则不追溯覆盖run02 STOP，也不是为R109/1262/seed17设置例外。

## 4. ALINEA真实放行精度（待批准）

**保留两个评价层。** 全控制时段H=[600,4200)与固定六窗Wk=[1200+300k,1500+300k)全部报告，不删除预热、空车、受阻或失败尾部。300s包含10个原30s反馈周期，跨多个8–24s离散包，适合观察持续放行而非逐秒整数误差；不是10个统计独立样本，也不改变既定交通效果评价设计。到达不足300s仅PARTIAL，未到达为null/NOT_TESTED。

C为原始clipped请求按真实更新时间积分；E_scheduled为名义完成包累计2辆，E_executed为实际执行完成包的名义配额，N为FCD/TLS/ACK独立核对的真实车头过线数。C_selected/C_applied是所选/实际ACK包名义率积分，不能替代C或N。每窗独立求增量；完成事件按a<end≤b计，真实运动按a≤step_begin<b计，partial/pending和端点残余另列。恒等式 `C−N=(C−E_scheduled)+(E_scheduled−E_executed)+(E_executed−N)` 仅是核账，不是缺额原因证明。

报告带符号及绝对车辆差、`3600(C−N)/时长` veh/h、原始请求与实际率；C≥20辆才报相对误差，否则null/SMALL_DENOMINATOR，不用1替换零分母。全六窗合计与H同样报告原始差，不用合计抵消失败的单窗。

**主推荐精度界：** 每个完整服务机会窗及全部机会窗合计，`|N−C|≤B=max(2辆,0.05C)`。300s下目标300/600/900veh/h对应容许2/2.5/3.75辆，即24/30/45veh/h；低率端实际容许8%而非统一5%。2辆取一个名义包的端点量级，5%是控制持续比例偏差的用途目标，均不是文献统一尺度或本执行器必达定理。该资格只能支持更大尺度的交通影响比较，不能据此区分与执行偏差同量级的微小效果，仍需正式实验设计与配对条件审查。

**端点和延迟另列，不自动扩容差。** 连续完整选包支持下，C_selected−E_scheduled为两端未完成配额之差，绝对值<2辆；这不保证C−N<2。一次300↔900请求延迟24s可造成4辆积分差，仍保留真实C−N。非superseded请求须在首个合法可用边界选择并绑定first-G ACK；连续机会情况下应用≤24s且必须是首边界。受外部约束时完整保留pending及年龄，无假ACK；本策略造成的延迟不能当外部豁免。实现正确但真实精度不达标，应判precision_not_met，不冒称API故障或修改目标。

**供给/接收机会必须先定义再看N。** 不以N、E、实际绿灯或“第二辆赶上本绿灯”为机会依据，不因短绿、启动损失或本策略释放的车造成接收受限而剔除。候车域固定为ramp_storage_0最后20m（当前[184.49,204.49]），每个完整1秒观察至少2个R车头在域，绑定网络SHA、lane坐标及ID/顺序/位置/速度/长度/minGap；远处ingress不计。20m是覆盖近线数辆车的项目空间操作定义，不是文献常数或容量证明，不随结果调宽。少于2辆只表示局部backlog未建立，不能据此直接认定供给不足。接收观察固定六lane：:ramp_mid_0_0、ramp_accel_0、:freeway_merge_2_0、merge_section_0/1/2。卡绑定该域及原网络SHA，每秒完整lane成员与已有world/identity位置、速度、车长、类型和route相核；注册网络几何须与回读一致。红段未采fresh CURRENT query如实记未采，不将它自动变为外因或丢弃红段；被动reference不足不自动排除策略造成的服务损失。无独立外部阻塞证据不得以available布尔排除。无法区分外部限制与策略影响则UNKNOWN，不能贴“受阻”标签消除欠额。最低条件精度证据拟为两个相邻完整300s机会窗，每窗C≥20、合计C≥50，且所有六窗仍完整到达/报告；这只是有限开发覆盖，不是统计功效证明。

单个机会窗超界即精度不合格；两个相邻机会窗各欠额超界且合计超界，另标持续欠放行。之后超放不能抵消前窗失败。全时域原始目标MET/NOT_MET与条件精度分开；局部机会精度通过不自动解决其他时段未能解释的持续亏额，若其它两个相邻完整窗均持续欠额超界且缺独立约束解释，总体仍NOT_QUALIFIED / UNRESOLVED；不要求逐辆准确分配重叠原因，但不得把receiver=false当解释。机会不足为精度证据NOT_TESTED，整体仍NOT_QUALIFIED；只建议确有必要的最少补测，不自动追加。

当前C−E_scheduled调度保持；绝不把C−N物理缺额追回或借E遮住N。完整N0/1不单凭数量判故障，合法G/Y额外过线仍是实际超放偏差。细化定义与独立方案审查见[数据方法](../../data/processed/actuator_acceptance_20261015_v1/DATA_METHOD_PROPOSAL.md)。

## 5. 实现、审查与下一运行门

当前仅隔离离线设计/实现工作获授权；新合同、数值标准、运行卡和实际资格尚未获批。运行规则没有因本文生效。拟新身份 QUAL_NATURAL_ALINEA_R900_S17_03：同4050请求/seed17/dt1/0–4200s/600起控/六窗，不调整模型、输入或算法。

只读实账：独立900s已耗258.87379404105013s，余641.1262059589499s，start_count=2、unknown_reserved=[]；两次启动许可均已消费。建议这一次新卡上限641s=worker611+cleanup30，启动60s、最低5GB、无固定字节门，仍须您明确新启动许可及准确卡、三方审查和新canonical/全部实时门。预算够用不是完成保证，超时也保留NOT_QUALIFIED，不自动第二次。

离线实现采用默认关闭的新安全分类器/原adapter与bridge窄接线、独立精度计算和原日志薄投影，以及精确03卡/保护器身份路由。既有ALINEA policy、producer和已批准current_gap_scope字节不变。保存旧默认STOP与新opt-in、硬风险、pending/EOF和准确批准否决的少量正反例。具体实现/测试/最终卡审查回执单独记录，不能由本文推定已全部完成；稳定源经工程/数据/科学审查后给一份具体审批包。无新SUMO、canonical或公开发布批准被本文推定；旧原始证据、旧STOP和正式空协议保持。正式实验不会自动启动。

设计审查：[只读科学结论及已采纳修正](../../artifacts/actuator_acceptance_20261015_v1/SCIENCE_DESIGN_REVIEW.md)。允许隔离实现不等于用户合同批准。本文是拟绑定精确卡的事前标准；以后批准、测试和实测状态由独立回执与PROJECT_STATE记录，不反向修改已执行卡所绑定的标准。

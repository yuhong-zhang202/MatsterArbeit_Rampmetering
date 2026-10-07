# ALINEA 指令到实际放行：执行层技术调查（Issue #2）

日期：2026-10-07

状态：**技术调查交付，待用户 / Chat 审查；方案建议均为 Proposed。**

任务：[Issue #2](https://github.com/yuhong-zhang202/MatsterArbeit_Rampmetering/issues/2)。依赖：[Draft PR #1](https://github.com/yuhong-zhang202/MatsterArbeit_Rampmetering/pull/1)。

调查基线：`e8bf608a15cf4c4484914467c5550d041c017a62`；独立分支：`codex/issue-2-actuator-investigation`。

## 1. 结论与范围

**建议下一步优先实现 Candidate A：由完整信号相位程序执行的短周期、离散周期放行层；Candidate B 保留为第二候选。**理由是当前主要问题来自放行条件、立即转红安全约束与额度丢弃的组合，增加 credit 算法复杂度不足以解决。A 可以把相位、目标服务和实测服务分层核查，更接近现有框架的 controller / actor 分工。这个排序是工程建议，不是已批准的正式控制方案，也不依据主线效果筛选。

两候选仅在**有条件的数学机会模型**中覆盖300–900 veh/h；尚未证明在当前车辆/几何/信号条件下达到实际900 veh/h，更未取得新的安全与服务资格。完整程序不保证安全，预定每绿两辆也不等于真的只过两辆。需要下一工程任务的实际车辆计数与相位安全检查。

本轮没有运行SUMO场景，没有更改旧FIX02、网络、需求、车辆模型、1s步长、ALINEA目标/增益/上限、城市信号或queue override。没有重开Stage6、改变科研结论、冻结正式协议或授权正式实验。原12控制的服务NOT_QUALIFIED及R900截断结果原样保留。

[文献映射台账](ACTUATOR_SOURCE_TO_DESIGN_LEDGER_20261007.md)覆盖Issue指定的五类资料。2008综述的出版社摘要已核实，**全文未取得**；出版方PDF403，作者机构记录被bot challenge阻挡，镜像403。该限制明确记录，不将未读细节写成论文结论。其他论文全文/预印本的实际阅读范围及公开源码commit见台账和[访问回执](../../artifacts/actuator_investigation_20261007_v1/LITERATURE_ACCESS_RECEIPT.json)。

## 2. 当前FIX02究竟缺什么

现有反馈模块能输出最终指令，现有日志也能记录实际过线。短缺发生在中间执行层。

现有调度每秒增加 `r_final/3600` credit；达到1且与上次绿灯间隔至少3s，才形成名义机会。安全guard通过才给1s绿，消耗1credit；之后至少2s红。额度超过1会丢弃，避免积累后补放大车团。安全检查包括front可达、leader gap、内部接收空间、follower停车距离与FIX02新增的“绿一秒后立即转红”预测；新进入内部车道的R也在预测范围。原源码及哈希保持不变，见[保护基线](../../artifacts/actuator_investigation_20261007_v1/PROTECTED_BASELINE.json)。

### 2.1 新核账，而非重复历史摘要

独立数据审计读取全部12个A03版本控制CSV：50,400行，其中43,200个控制秒；核对原始回执哈希、逐秒时间与credit、请求/观察灯色、实际crossing、全部72个持续供给300s窗口和12个权威run gate。原始数据只读。

全控制时段：6,288次绿灯对应6,288次唯一日志过线，没有日志中的红灯/多车/重复过线。本轮未重复FCD物理安全分析；此前独立FCD资格证据仍按原源码/输入哈希引用，不能扩展到新候选。

72个评估窗口结果如下：

| 项目 | 核对结果 | 适用范围 |
|---|---:|---|
| 最终指令积分C | 4,905.089178 辆等价额度 | 12运行各6个300s窗口，合计[1200,3000) |
| 实际过线G | 3,331辆 | 同上 |
| 丢弃credit D | 1,572.003668 辆等价额度 | 同上 |
| 窗口边界credit增加ΣΔB | 2.085511 辆等价额度 | 同上 |
| 服务资格 | 71FAIL / 1PASS；12运行整体NOT_QUALIFIED | 原10%屏障保持 |
| 唯一PASS | R750/S23/T1，[2100,2400)：C46.529768、G43、误差7.586% | 单窗口，不是该运行通过 |

核账恒等式：

`C − G = D + B_end − B_start`

因此差额1,574.089178完全闭合；最大逐秒守恒误差仅2.85×10⁻¹⁴辆等价额度。全[600,4200)指令10,142.511992、过线6,288、丢弃3,844.261992、终点保留credit合计10.25。

证据：[独立分解报告](../../data/processed/actuator_investigation_20261007_v1/FIX02_FAILURE_DECOMPOSITION.md)、[核账回执](../../data/processed/actuator_investigation_20261007_v1/DECOMPOSITION_RECEIPT.json)、[窗口表](../../results/tables/actuator_investigation_20261007_v1/window_credit_balance.csv)。所有数值是技术回顾，不是正式论文估计。

### 2.2 七种原因逐项判定

| Issue要求的原因 | 当前证据 | 限制 |
|---|---|---|
| 指令离散化 | 没有有限rate菜单量化；逐秒积分已有最终rate。相同已观察指令去掉guard的纯算术机会回放，每窗口与指令相差<0.961辆。 | 能排除大幅短缺纯粹来自取整，不能证明这些机会能安全过线。 |
| safety denial | 评估时段8,147个“已到期但拒绝”秒；post-red prediction5,140、follower stop-distance1,475、leader secure-gap1,532。 | 是按优先级选中的理由，其他条件可能被遮蔽；秒数不是损失辆数。 |
| receiver/downstream | 内部接收净空选中845个到期拒绝秒。 | 是局部receiver检查，不等于主线拥堵唯一归因。 |
| no-demand | 72窗口每秒storage有车；评估NO_FRONT到期拒绝为0。 | 全控制期间有2,129个NO_FRONT秒，不可拿来解释持续供给窗口失败。storage有车也不等于front可立即安全到线。 |
| dropped credit | capped-credit核账解释持续服务差额；安全选中步骤关联丢弃1,453.670195、receiver关联118.333473。 | 丢弃是约束后的记账结果，与安全/接收原因相加会重复计数；不能推算去掉guard可恢复多少辆。 |
| phase / timestep | 控制请求/实际灯色一致；1s绿/至少2s红；无guard算术回放误差小。 | 当前没有完整yellow/clearance序列；新的完整转换会改变名义capacity，不可沿用旧上限证明。 |
| 其他 | FRONT_NOT_ONE_STEP_REACHABLE选中74秒，同一步丢弃额度0；未发现缺行/重复过线/不闭合。 | 0同一步丢弃不表示无间接影响；不补写未经证明的原因。 |

完整分账见[reason表](../../results/tables/actuator_investigation_20261007_v1/reason_step_accounting.csv)和[category表](../../results/tables/actuator_investigation_20261007_v1/category_step_accounting.csv)。原因分账只是同一步观察账，不是互斥的因果损失或反事实收益。

`sampled_service.json`保留了旧stopped-only检查，部分仍写FAIL_RECONCILIATION；当前权威替代项是原`FIX02_DATA_GATE.json.actual_service`及其FCD审计。这个命名/版本陷阱已记录，未删除旧产物或混用判断。

## 3. 文献/官方机制对设计的影响

逐来源原文范围、出处、支持机制和不能推出的事项见[台账](ACTUATOR_SOURCE_TO_DESIGN_LEDGER_20261007.md)，这里仅归纳本项目建议：

1. 将ALINEA rate选择与signal operation分开；替换执行层不顺带调整反馈目标/增益。
2. 将整数周期菜单误差、可用服务机会、实际放行短缺分别记账。论文中的“十个rate足够”不直接设成本项目标准。
3. 完整G→y→r转换交给明确的TLS program；TraCI在安全边界选择phase/duration，不能任意重启green或跳过clearance。
4. 单车安全gap需考虑车辆状态和下游预测；远处meter的可达性检查不等于merge-gap证明。
5. 用实测停止线过车核实service；绿信比、green秒数和command都不能代替实际车辆数。

公开sumoITScontrol源码固定在`48a88131f35e2a42f6e0b4511f2f1ee0792daa40`。其RampMeter使用normalized green share，`int(share×cycle)`产生green时长、其余red，更新program后设phase0。该映射没有使用默认nominal saturation_flow来资格验证veh/h。可借用分层接口思路，不能直接当本项目完整安全执行层。源码永久链接/哈希和本地0.1.0差异保留在[工程来源回执](../../artifacts/actuator_investigation_20261007_v1/engineering/PUBLIC_SOURCE_AND_ENVIRONMENT_RECEIPT.json)。

## 4. Candidate A — 完整短周期 / 离散周期执行器

**Proposed；尚未接入TraCI或实际流量测试。**

| 合同项 | 草图 |
|---|---|
| command input | 原ALINEA与override输出的r_final[veh/h]，300–900；另记录r_ALINEA和override状态。两者算法保持。 |
| internal state | 当前program/phase、已用/剩余时长、当前cycle、整数周期余数、待应用rate、每cycle目标n/实际过线、供给/receiver状态。 |
| phase逻辑 | 明确G/y/r（若需额外clearance则入总cycle）；green结束进入yellow，让program完成转换。仅在安全cycle边界更新整数周期/green政策；不得每30s反馈无条件重置phase0。 |
| safety逻辑 | 原车跟驰/换道/红灯模型保留；front/follower/内部入口及receiver检查按新的转换过程重新审计。状态不完整fail closed。不得通过忽略红灯、减小tau、放宽collision或强制speed/lane来提高服务。 |
| accounting | 连续指令C、菜单名义期望E、实际N分别累计；量化误差C−E与物理短缺E−N分列。停止线所有G/y/r状态实际过线都计入N，yellow合法过线归入实际cycle服务，red过线需单独判定；不得只数green事件。 |
| expected service | 仅在持续供给、receiver允许、已经验证每cycle实际可服务n辆时，名义r=3600n/T。n、startup loss、跨yellow过线必须实测，不能由时长直接假定。 |
| required logs | rate生效时刻/旧新command、phase请求/实际与nextSwitch、完整cycle ID/起止/n计划/实际车辆ID、供给/receiver/拒绝、各灯色过线、相位延迟、mapping residual、warning/collision和源码/输入哈希。 |
| gates | 菜单与单位/边界正确→全相位时序一致→cycle逐车计数/总额闭合→物理安全→原同供给窗口service门。每步单独结论，不能安全通过替代服务通过。 |
| failure modes | 停车启动损失、每绿多/少过车、yellow尾部过车、rate更新延迟、receiver blockage、cycle rounding、TraCI重置、未知入口/follower状态、低rate长红或高rate不够clearance。 |
| 最小差异 | 增加独立phase actor与unit adapter/日志；替换FIX02的立即G→r pulse执行方式，原feedback/override/模型不变。旧FIX02仅作版本绑定技术参考，不合并效果。 |

### 4.1 数学可行性及300–900覆盖条件

设经资格验证的每cycle服务n辆、最小完整周期`T_min=G_min+Y_min+R_min(+clearance)`，均按1s步长实现。

`r_max_nominal = 3600n/T_min`。要在数学上覆盖900，需要`T_min ≤ 4n s`：
- 单车要求完整周期≤4s。若合格完整转换需要5s，单车上限720而不能说支持900。
- 两车要求完整周期≤8s，并且真实车辆确能在该green/transition内安全服务两辆。名义cycle8–24s对应900–300；这不证明当前scenario有合格n=2。

对任意rate可在相邻整数周期`floor(3600n/r)`和`ceil(3600n/r)`之间按**周期次数**配比，使平均周期趋于3600n/r。必须以`3600n/平均周期`计算名义rate，不能把两个rate简单按cycle次数平均。新离线工具用有理数余数调度；1,000cycle累计时间误差<1s。静态选择单一周期会有明显误差：数学示例n1、810指令，最近周期5s只有720，即11.11%偏差。

离线fixture的G/y/r数字只是构造合法代数包络，并非推荐相位参数。真实startup/saturation/n与yellow/clearance不能由fixture认证。A推荐优先，但是否采用单车或两车必须在下一工程卡中据实确定。

## 5. Candidate B — 安全gap单车放行

**Proposed；不会因保留credit自动提高实际安全服务。**

| 合同项 | 草图 |
|---|---|
| command input/state | 原r_final；积分quota、保留/丢弃/超期额度、最近服务时间、front/follower/leader速度位置制动能力、预测gap、internal entrants、receiver、phase状态。 |
| opportunity / release | 指令形成机会；供给→receiver→following/merge预测→相位合法且headway允许，才放行。以全部约束标志+主拒绝原因记录，避免优先级遮蔽。unknown fail closed。 |
| gap safety | 以当前Krauss/几何/速度与制动条件建立可解释的front/follower停止约束及预测leader/follower净距；meter距merge及lanechange使安全预测不确定，需原生规则及事后安全核对。不能直接把V2I论文公式当本场景已证实安全。 |
| credit/accounting | 拒绝后的retain/delay/drop必须显式；余额上限/超期规则仍是技术候选，未批准。允许保留额度也不能突破安全headway/服务上限补放；C=N+D+ΔB，必要时加明确未成交quota，不凭green消耗虚报成交。 |
| expected service | 理想无拒绝机会可跟踪300–900；实际受可用安全gap、信号时序和receiver共同约束。保持所有denied backlog会在长期capacity不足时发散，需要报告受限，不能悄悄增大服务上限。 |
| logs/gates | 与A相同rate/phase/过车/供给/receiver/安全版本日志，额外gap预测/实际、保留/延期/丢弃、reason flags与quota闭合。原service屏障不放宽。 |
| failure modes | gap预测误差、过度保守、稀少merge-gap、等待额度无法在900上限内追赶、长期bank增长、立即红造成follower制动、入口遗漏、多车实际过线。 |
| 最小差异 | 整理为一个状态/物理约束合同与auditable ledger；仍需新的安全/过车验证。没有授权简单移除FIX02 guard或调阈值直到服务“好看”。 |

数学条件：实际合格服务headway≤4s才可能单车900；6s安全headway只能600。离线无拒绝601个整数rate300–900均准确生成一小时机会；拒绝100s后在900机会cap下无法在同窗口完全补偿，即使额度保留。这个反例说明“保留credit”不是安全capacity的替代。

B比A更需新的预测有效性与微观gap调查，且与论文V2I条件不同。因此保留为第二候选，而非叠加更多FIX02互锁的默认方向。

## 6. 实际验证与未运行事项

精确代码/测试/来源/环境/输出绑定见工程与数据回执。工程离线测试使用项目.venv Python3.13.0；数据核账使用系统Python3.12.4和标准库。历史运行环境及输入哈希来自PR1原receipt；不把今日离线测试写成旧仿真重测。

| 检查 | 实际方法 | 结果与界限 |
|---|---|---|
| FIX02 raw-bound审计 | 最后一次实际命令：`python3 data/processed/actuator_investigation_20261007_v1/decompose_fix02.py --refresh-derived`；默认无flag核对现有同字节产物、不同即停止 | 12原始CSV/72窗口/守恒/连续credit/过线/权威gate通过；不新分析物理FCD安全 |
| 新离线合同 | `.venv/bin/python -m unittest discover -s tests/actuator_investigation_20261007 -v`；回执绑定源码hash | 10/10PASS、18.594s；原scheduler无guard、A整数cycle/包络、B机会/headway/denial/accounting反例；只测数学与状态合同 |
| 官方/框架核查 | web原文+公开commit+本地API静态核查 | paper/source/安装版本区分；L2全文访问受限 |
| 生产文件保护 | 对PROTECTED_BASELINE逐项SHA-256 | 旧脚本/AGENTS/DECISIONS/空协议保持；新文件独立命名 |
| 候选SUMO smoke | **未运行，两候选各0次** | 为本轮理论调查不必启动；完整traffic-phase actor和安全合同尚未实现，仓促smoke无独立资格价值 |
| 正式/新需求矩阵 | **未运行** | Issue明确排除，protocol0B/unfrozen；不扩展R825/qMain，不调ALINEA或rule |

本轮的“检查通过”只覆盖这些已执行离线/静态/回顾检查。新的执行层安全与实际service状态均为**NOT_VERIFIED**。

## 7. 下一步最小工程交接（待批准）

下一任务应只围绕**A的一套最小实现及资格验证**；不同时启动两候选的大型开发矩阵。

1. 明确unit contract与拟用完整phase图、rate生效边界、实际过线计数口径、名义n及300–900包络。源头1s步长、网络、需求、feedback/override参数保持。没有依据的yellow/red数值先作待确认工程参数，不能来源伪装。
2. 实现单一TraCI actor、顺序phase更新和全部跨灯色过车ledger；静态/离线核查余数、边界/反馈中途更新、延迟、receiver、unknown状态及安全退出。
3. engineering / data / scientific审查明确卡片：以已经授权的数据点/seed技术目的做最小代表性traffic资格，必须先量化startup/discharge/每cycle过车数与yellow净空，再判service。具体运行授权与资源预算需下一Issue/用户确认；本次未使用的smoke额度不能跨任务自动继承。
4. 按原服务门分开检查安全、数据/相位、持续供给rate跟踪；记录供给不足或受阻。A若不能稳定服务900，诚实报告受限，先查机制；不改变上限、车辆模型、步长或网络。需要这些改动则STOP交Chat/用户。
5. 仅若A经真实最小检查失败且B能提出明确可验证的安全headway合同，再讨论第二候选。正式比较/重跑12控制或60/90矩阵需独立批准，不能用本调查代替。

**Fallback继续保留为条件性方法备选，但当前没有证据显示A/B皆不可行，因此不触发。**若后续均无法在既有模型下通过服务资格，需用户/Robert决定是否把“受限反馈+执行器整体”作为研究对象；届时必须公开实际指令/服务差别，不称纯ALINEA效果。这会涉及研究定位，不能由Codex自行采用。

**下一步建议不构成执行授权。**下一位接手：用户 / Chat审查本DraftPR并决定下一工程Issue；Codex按明确Issue实施。

## 8. Issue验收逐项回答

| 条件 | 调查回答 | 证据/边界 |
|---|---|---|
| 1 当前FIX02为何不能稳定命令流率 | 安全/receiver等约束拒绝后credit被cap丢弃，守恒闭合；纯取整误差不足解释短缺 | §2；全部12run/72window，原因分账非因果可恢复量 |
| 2 文献与SUMO借鉴思想 | 分层、离散cycle菜单、微观状态gap、完整TLS转换、实测stopline service | §3与source ledger；2008全文未取得，不宣称全篇核查 |
| 3 A/B首选与理由 | A优先Proposed；可审计phase/rate分层，Bgap预测成本更高 | §§4–5；不以trafficbenefit选择，不等于A合格 |
| 4 300–900理论/最小技术覆盖 | A需T_min≤4n且n实际合格；B需安全headway≤4s、gap足够；离线条件成立 | 代数/fixture检查；当前actual覆盖NOT_VERIFIED |
| 5 保留安全/相位约束 | nativeCF/lanechange/red、完整转换/制动/follower/入口/receiver/unknown failclosed及warning gates | 即时红专用互锁不可套为所有policy安全定理 |
| 6 最小下一工程任务 | 单一A actor+完整ledger+资格卡片；先实际phase/service，再考虑重跑 | §7；不触发正式实验或改设计 |
| 7 是否需要fallback | 保留未触发；仅A/B均不能qualified后另行方法讨论 | 不改研究对象，不写成已批准 |

## 9. 审查、文档影响与证据访问

simulation_engineer承担源码/API/环境版本、两候选技术合同与离线测试，10/10PASS；data_analyst独立核账通过，并修正工具的credit连续性/输入表hash/防静默覆盖，相关离线重跑通过且4数值表字节一致。scientific_reviewer完成预审与最终只读审查：**PASS_FOR_BOUNDED_TECHNICAL_INVESTIGATION_DELIVERY**，无未处理Blocker/Major/必改Minor。详见[最终独立科学审查](../../artifacts/actuator_investigation_20261007_v1/FINAL_SCIENTIFIC_REVIEW.md)。2008全文访问限制仍保留，新执行器actual-service/safety仍NOT_VERIFIED；审查PASS不代表用户验收或正式实验授权。

PROJECT_STATE仅更新当前Issue技术工作和标记原未标注历史章节；WORKLOG追加本轮记录。DECISIONS、EXPERIMENT_PROTOCOL、Stage6/开发试跑报告、监督记录、AGENTS及旧实现已是该历史版本权威记录，本轮不改。没有Notion/MemoryCore同步任务。

GitHub提供本调查报告、源码/测试、来源回执、审查记录、4张小型表及输入哈希；原始控制CSV/FCD留本地原data/raw路径，PR1已有公开审查摘要与hash，不假称raw可在线访问。未上传私人邮件、memory修改或无关工作区文件；full-paper版权资料只给原链接。旧失败/阴性/截断结果保留，不新决定Stage6结项或正式实验状态。

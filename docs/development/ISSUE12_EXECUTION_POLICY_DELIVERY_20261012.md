# Issue #12 执行政策工程交付与资格边界

2026-10-12｜基线20e5e83ac059768320cdaa4c815d164e1022de45；新900诊断和独立数据复核已完成；工程→独立数据→只读科学终审已完成，GO交付并停止追加native；交付待用户/Chat审查。

## 任务和方法

任务：[Issue #12](https://github.com/yuhong-zhang202/MatsterArbeit_Rampmetering/issues/12)。正式实验前工程资格准备；阶段6既有completed/preliminary_ready不重判。原生产guard、SUMO核心、车辆模型、路网、M3600/R900/U360/X180输入、seed17及ALINEA数学不改变；r300/r900运行名指服务请求，不是改变qRamp。固定率诊断r_ALINEA=null，不伪称closed-loop控制效果。

[问题索引](../problem_records/README.md)以4条记录覆盖FIX02服务不足、STOP3/A1证明缺口、receiver等待/预算和双车起步不足；相关旧报告保持原位，未发现已有独立问题文件需迁移。小fixture/Reviewer缺陷不拆成新问题文件。文献/官方机制依据和三方案比较见[政策决策](RAMP_METERING_SIGNAL_POLICY_DECISION.md)、[唯一文献索引](../../artifacts/issue12_alinea_actuation_20261012_v1/literature/REFERENCES.md)。文献全文/摘要/书目等级分别标记，不虚称2008综述全文已读。

## 原始诊断与本次变化

| 独立身份 | 实际终点 | 真实运行/结果 | 适用范围 |
|---|---:|---|---|
| WAIT_DIAG01_V2与WAIT_BUDGET_W360_01（旧独立工作区） |1272s|各3周期，C=appliedC=E6,N3；300/360s预算均足够，420/480按用户收敛SKIPPED|同seed轨迹，非统计重复；3s绿灯不支持名义双车 |
| CA_I12_QUOTA_R300_S17_DIAG01 |1210s|helper不支持duration，native setter前停止；N2,C=appliedC5/6,E0，0完整周期|真实技术FAIL，不资格；末步/1271arrival审计PASS |
| CA_I12_QUOTA_R300_S17_FIX01 |1272s|官方duration最小修复；3×24s，G4/Y5/red15，每周期2辆；C=appliedC=E=N6|72s技术限定PASS；不是长期300资格；1335arrival审计PASS |
| CA_I12_QUOTA_R900_S17_BOUNDARY01 |1206s|G6时原post-gap拒绝；N2,C=appliedC1.5,E0，0完整周期，无受控Y/red|仅guard合同拒绝，非900物理NO-GO；1267arrival审计PASS |
| CA_I12_PACKET_R900_S17_DIAG01 |1272s|9×8s，实际每周期G4/Y2/red2、2绿车、黄/红入口0；C=pending=applied=E=N18|一次实际诊断，firstred1207；18ID均rear-clear；独立FCD/TLS/ACK/body/1338arrival复核PASS |

首helper故障仅修新namespace官方setPhaseDuration桥接，ATTEMPTED/readback/failedSTOP持久化；旧worker/guard未改。原fixed24源、卡、raw、技术FAIL及API修复前后真实测试记录均保留。后续shortpacket独立namespace复用Candidate A、WAIT/cache/log/watchdog，新增全部车尾清空观测和总预算门。新checks只追加缺测STOP，不替代原硬检查。

900前缀ID/时刻/单位/minGap绑定未发现bug。原query leaderEmergencyDecel9 secureGap9.621192519298493m，gap9.630877589859532m，加原1.1m需10.721192519298492m，故拒绝。baregap比query大0.00968507056m不能当作项目guard通过。官方普通CF采用current apparentDecel；4.5只是本配置源码推断/假设算例，不是实际getter或准许降低硬检查。见[源码调查](../../artifacts/issue12_alinea_actuation_20261012_v1/engineering/stop_gap_investigation_v1/ENGINEERING_ROOT_CAUSE_V1.md)。

## 率、供给和安全核账

request→pending→实际applied分别积分；E只在完整周期计请求quota，N独立从unique计量入口重建，绿/黄额外车辆不丢失、不cap。无观测为null，部分观测保留真实C/N/E0，不冒充完整周期资格。工程bodytracker逐ACK全internal/uncleared IDs，绑定entry区间/信号与实际rear-clear；合法先前过线的车尾在red下不能误记红灯新入口；新红灯前车过线仍STOP。

保持原9+1.1 current-following、正常减速4.5、身份/车辆覆盖、每newG receiver、实际Y2 approaching停/通过、collision/teleport、phase/link、日志四流/EOF及终端arrival检查。旧六帧Y2同状态screen41/39/37全通过，旧Y5首黄ACK尾部清空；不是新Y2实际证据或未来安全保证，不建立A1形式化证明。

FIX300终点due未插入R68/U28/M0/X0；unfinished M77/R97/U23/X4。共享区R20（4停止）、U8（2停止）是终点描述，不是正式spillback阈值或U成本唯一因果结论。技术holding-red预加载不用于全系统控制效益比较。完整输出供给/队列和截断状态见独立run数据报告。

## 实际测试、环境与失败保留

Python3.13.0，traci/sumolib1.26.0，sumoITScontrol0.1.0；SUMO1.26二进制SHA3bd1eaa3b167fb527ac33b154dfb57b41b9a40d5bc3e26246489824dd7977179。二进制与引用源码的构建等价未验证；未安装依赖或改环境。

- 原signalpolicy7方法的各次实际PASS/prepare/card检查留存；不冒称一次全新7方法总套件。
- 官方duration真实旧helper回归FAIL，修复后同1方法PASS，包含完整时钟/错误/readback；其他源码/历史bytes不变，未为PR重跑昂贵历史run。
- packet受影响4方法：首套3PASS/1fixture期待理由FAIL保留；fixture人口修正后仅该method重跑PASS。真实XML+旧helper9 fakecycles与fresh admission/duration/bodyunderred、旧gap和Y2UNKNOWNSTOP、partial/null/实测零及未知资源reservation均有单独PASS。Fake dynamics不是native物理证据。[工程回执](../../artifacts/issue12_alinea_actuation_20261012_v1/engineering/packet_v1/ENGINEERING_RECEIPT_V1.json)。
- data的实际工具适配FAIL、arrival末wrapper错误、工程900 V2 self-hash错误均保留；新版本修正并独立绑定，不修改raw。V3工程15文件/数据额外5文件独立核对PASS，原14文件不覆盖。
- 六旧帧提取V2曾复用V1派生结果路径且未先保留旧结果SHA。此历史追溯限制明确披露；脚本/log、独立V2及版本receipt保留，不能虚称完全版本证明。后续新产物独立版本路径，不为历史缺口增加native run。

实际native运行发生在历史HEAD20e5加精确未提交源快照；每card/input/source/raw SHA绑定，不声称20e5已含新代码。交付commit一致性和最小clean checkout测试将在提交时单独记录，不能把代码提交时间当native运行版本。

## 预算与范围

最新直接用户消息取消固定启动次数停止条件；选择沿用原3份最大额度的900s/900MB总包络为工程决定，不冒称用户逐字数字。前三次原native监控137.2967030419968+126.59917641701759+117.30937795899808=381.2052574180125s；raw148115726+163352995+146880941=458349662B。原预算结论不追溯重判。新guardian把未知目录保守预留300s/300MB，不隐式释放；单次300s/300MB/start60/free5GB、异常UNKNOWN停止及1272固定终点保持。监控包括startup/cleanup，静态prepare/最后CLI输出与独立审核不计，采样STOP不构成绝对数学上界。无额外付费模型调用。新packet运行实耗监控154.08922300001723s、raw95份164333753B；总535.2944804180297s/622683415B，余364.7055195819703s/277316585B。剩余资源不构成继续运行的理由；wholeCLI154.99017116700998s采用独立时钟，不能混写为监控时间。

## 公共证据和未完成边界

raw只读、本地保存；GitHub交付包括精确卡、源/input绑定、raw清单/每文件SHA、紧凑derived表、review和失败记录，不上传完整raw、私人邮件、MemoryCore无关改动、canonical执行权限或Python cache。旧WAIT fullraw在独立工作区；Issue12新raw在主工作区data/raw/issue12_alinea_actuation_20261012_v1/。公开摘要可审查不等于公开完整raw重算能力；本地原数据核查单独标记。

短窗实际放行与全域qualification分开：300限定实测6/72s；旧900 STOP不是物理不可达。新900在72s、seed17供给下实际18辆，即900veh/h；原hardguard在观测范围均未拒绝。此事实支持当前短两车包高端的局部可行性，最终数据和科学复核已限定PASS/GO交付；450/600/750未新native，不写PASS。整数周期映射仅名义最大相对误差5.882%，实际N、连续rate更新延迟、长窗安全、多seed服务与正式ALINEA效果尚未验证。原Stage6结项、A1 UNRESOLVED、Candidate A NOT_QUALIFIED、旧STOP3与空未冻结协议保持。

下一步建议不构成执行授权。[Draft PR #13](https://github.com/yuhong-zhang202/MatsterArbeit_Rampmetering/pull/13)已提交，初始两提交与578条远程分页路径核对一致，直接base codex/candidate-a-native-smoke-proposal /20e5，保留PR1→3→5→7→9→11，上游不修改/retarget/合并。用户/Chat负责审查接受及重大科研取舍，Codex不代替验收。

## 原始数据版本身份

| 本次身份 | raw文件/字节 | manifest SHA-256 | 本地原始重算/公共审查 |
|---|---:|---|---|
| QUOTA_R300_DIAG01 |81/148115726|358e427bef1ba58d291376d6fed36e767a223603f6e0a29ea3a6a127353f6486|完整raw仅主目录；公开清单/摘要/FAIL |
| QUOTA_R300_FIX01 |82/163352995|c63436ebcaf75efc969c8778c3cde11de6181b41c7ce9a13a2536d9e4e268ea6|完整raw仅主目录；公开独立数据和有限PASS |
| QUOTA_R900_BOUNDARY01 |79/146880941|f2ed45d66b2087a88cf8b7ce4af4d0d38131e6302ef43ded251a908cd655fa7f|完整raw仅主目录；公开STOP/源码调查/审计修订 |
| PACKET_R900_DIAG01 |95/164333753|253c894c52c21a009094dbb7ee80586473f21a0e194abce4d86ccdfb54efde40|完整raw仅主目录；公开精确卡/工程/数据与科学复核 |

工程41binder `cfef72429d1f4dc454dc0632237e82297dfe59d6cff6e4a0472525857d1ad415`，实际新run工程binder `b1c324b9442bb0a28ab279247cb02b62513e8e00f305c2005ffb79c91cede4f8`；所有旧38依赖/536保护、新49源均核对一致。完整单次启动命令/PID/两种时间口径见[真实工程receipt](../../artifacts/issue12_alinea_actuation_20261012_v1/runs/CA_I12_PACKET_R900_S17_DIAG01/engineering/EXECUTION_RECEIPT_V1.json)。所有实际运行均各自消费精确卡；不能照抄命令重跑。

## 新packet900独立数据结论和全域判断

[实际数据报告](../../data/processed/issue12_alinea_actuation_20261012_v1/CA_I12_PACKET_R900_S17_DIAG01/revision01/FINAL_DATA_REVIEW_V1.md)9文件绑定 `8a660303b570b275cf108e27a98dd93d52cd2fe4373733ebef1e4a430db0c856`：1272FCD/TLS帧、2544ACK、18uniqueG、九周期、40body观察行/18真实清尾、九新G准入、1338正常terminal、61WAIT记录及九Y2人口全量独立核对PASS；2547日志记录到EOF。等待记录不是61独立episode。实际正常制动下界−4.5m/s²、collision/teleport0，仅限观测与退出补核。Firstred BEGIN1206/ACK1207；每周期red2是实测总曝光，duration剩余1是在首red ACK之后，不能误写红灯只有1秒。全部18车在下一G前实际清尾，无原9+1.1放宽。

新run截止ACK1272，到期未插入M0/R68/U28/X0；unfinished M78/R93/U23/X4。shared R18（4零速）/U7（2零速）只是末帧描述，不是控制效益或物理回溢唯一因果。原FIX300的different终点值另列，不混合。

| 目标服务率veh/h | 新库名义T/Y/red（Gmax4） | 已观测支持 | 正式/全域状态 |
|---|---|---|---|
|300|24/5/≥15|旧FIX300不同namespace实测3周期2辆；不是新packet300的验证|新namespace NOT_TESTED；长期NOT_QUALIFIED|
|450|16/5/≥7|只有映射/时长算术，无原生运行|NOT_TESTED|
|600|12/5/≥3|只有映射/时长算术，无原生运行|NOT_TESTED|
|750（映射720）|10/4/≥2|名义量化−4%，不是实际放行误差|NOT_TESTED|
|900|8/2/≥2|本新namespace9×2辆，72s实际900|限本次技术观察；长期NOT_QUALIFIED|

**有界可行性判断：** 不能再以原G3单车或长G6 STOP宣称900物理不可达；新短双车包在该供给/seed17下实际能实现高端请求，300另有有限旧版本支持。整数周期消除了先前统一G增加却不核算高端时长的矛盾；这提供工程候选依据，未证明任意rate/queue/state的完整安全或服务资格。当前可执行的新桥接只有fixed900/T8，映射库≠全域runner或liveALINEA。

**停止本次机制诊断：** 旧欠放行原因已观测、原硬门保留、新低端有限支持与新高端精确观测/独立核账已回答Issue要求的有界问题；不靠未测试档填PASS。补600或再改参数不能替代长窗口/连续控制的资格定义，因此不继续机械补矩阵。最终科学审查已确认GO交付、停止追加诊断；随后提交Draft PR。下一重大取舍仅建议用户/Chat决定是否将该候选政策纳入后续正式方法/资格计划，并明确rate窗口、控制更新和验收要求；这不是批准记录或运行授权。

非阻塞来源标签差：卡片FIXED_PACKET_POLICY_DIAGNOSTIC，继承telemetry FIXED_POLICY_DIAGNOSTIC。独立审核显式记录/映射，二者均fixed900/period8/quota2/r_ALINEA=null且精确源已绑定；不改已冻raw，不宣称文本相同或动态反馈。

真实公共clean checkout `403094d6e82c65cf578e562bf4cf97ba3821eecf`一次4/4离线测试PASS，raw仅.gitkeep、Git状态空；49卡片源与主目录和clone逐哈希一致。此后只追加文档/derived/review/receipt，不称后续doc-only head单独测试或raw审计能在公开checkout运行。[测试和范围receipt](../../artifacts/issue12_alinea_actuation_20261012_v1/portability_v1/CLEAN_CHECKOUT_RECEIPT_V1.json)、[源码一致性](../../artifacts/issue12_alinea_actuation_20261012_v1/portability_v1/CLONE_SCOPE_SOURCE_MATCH_V1.json)。全tree `git diff --check`真实FAIL（冻结CSV CRLF/原patch文本），保留日志；源码/脚本/测试/当前docs的scoped检查实际PASS，不静默修改绑定数据或宣称全treePASS。

## 最终科学审查与交接

[最终科学审查](../../artifacts/issue12_alinea_actuation_20261012_v1/runs/CA_I12_PACKET_R900_S17_DIAG01/FINAL_SCIENTIFIC_REVIEW_V1.md)支持GO交付并停止本轮追加native，无新增Blocker/Major、无必须补600信息缺口；历史追溯/来源标签限制披露，PRB-004历史状态Minor已修正。Issue验收1–3满足限定工程交付、4满足有界可行性判断而非全域资格，5在审查当时因PR尚未创建为部分满足，远程Draft PR创建及完整分页文件核对已补齐此交付动作（不修改科学审查原时间快照）。自检不是用户验收。

Documentation Impact Check：更新PROJECT_STATE当前节点/资格边界，WORKLOG真实实现/运行/审查记录，policy/index与PRB-004机制进展，README必要入口与CLI单次卡说明；Dashboard仅新增Issue12待审查条目/更新时间，不改变原阶段/章节/决策状态。本次DECISIONS、EXPERIMENT_PROTOCOL、AGENTS、SUPERVISOR_FEEDBACK、thesis outline没有新授权事项，未修改；MemoryCore和私人邮件无关改动保留不提交。无正式研究决定状态提升或新的阶段结项。完整raw本地限制不是未上传证据已提供在线的说法。

## GitHub交付记录

[Draft PR #13](https://github.com/yuhong-zhang202/MatsterArbeit_Rampmetering/pull/13)，关联Issue #12，base `codex/candidate-a-native-smoke-proposal`/20e5e83ac059768320cdaa4c815d164e1022de45。实现测试提交403094d6…，证据文档提交0fba4616…；初始remote正文/base/head/两提交/全部578分页路径已真实核对。随后仅补PR链接、Dashboard交接和这份回执，运行源码/测试仍与403094d及精确卡相同。Head SHA以PR最新远程元数据为准，避免在自身提交中制造自哈希循环。[初始远程checkpoint](../../artifacts/issue12_alinea_actuation_20261012_v1/GITHUB_DELIVERY_CHECKPOINT_V1.json)明确是链接回填前版本，不冒称当前Head测试。PR为Open/Draft，未合并、未关闭Issue、未用户验收。

## 2026-10-13 — PR #13 P2相位顺序审计修订（revision02）

[Reviewer P2](https://github.com/yuhong-zhang202/MatsterArbeit_Rampmetering/pull/13#discussion_r4253092187)指出原revision01只核对每周期G/y/r样本总数，不能单独证明连续G→y→r和真实转相时刻。保留原版本/审核记录，新增revision02；不把旧缺口事后写成原V1已有核查。

新纯离线helper逐72条原XML控制样本、72个post区间与144条ACK，验证九周期严格连续`GGGGyyrr`、程序/phase映射、BEGIN/ACK连续性、native pending-switch步前/步后及nextSwitch。完整18条phase request和18条duration ATTEMPTED/READBACK与G末ACK之后setter、首red ACK之后duration读回对账；确认8次周期间r→G。每周期b=1200+8k：G开始b、Y开始b+4、r开始b+6、首red ACK b+7、周期结束b+8；末周期1264/1268/1270/1272，不虚构1272之后第十绿灯。

原数据TLS时间是运动BEGIN，post是ACK END；原生转相到期时phase_before可能仍是上一相位（1206前y、1208前r），不能误判正常pending为异常。新核查证明的是当前1s步长下已记录运动区间的完整相位顺序和边界，不是普遍安全保证。

本次4项回归方法通过（19种负例），覆盖同计数重排/中断、缺失/重复/未知或错时样本、ACK不绑定、nextSwitch及setter trace破坏。正例使用已提交的原run相位子集，五源SHA和逐字段核对；公开回归不依赖完整本地raw，fixture不取代本地95份raw完整审计。首V1测试文件遗漏冒号导致importERROR，源码/log/receipt保留，计划4方法不能写成该失败版本已执行4方法；V2仅修语法后实际4方法PASS。

[revision02实际输出](../../data/processed/issue12_alinea_actuation_20261012_v1/CA_I12_PACKET_R900_S17_DIAG01/revision02/PACKET_DATA_RESULTS_V2.json)唯一真实离线重审通过，原V1全部raw/FCD/N/body/arrival/EOF核查保留，C=pending=applied=E=N18不变。独立数据/科学复审完成状态及最终提交由本轮新回执记录，不改原日期审核结论。

本轮0SUMO，配时/safety guard/原49源和精确卡/raw全部不变；没有改变正式协议或Candidate A NOT_QUALIFIED/A1 UNRESOLVED/旧STOP3。450/600/750、动态ALINEA、长窗口/全域资格仍未验证。公开新fixture/helper/回归与真实完整raw审核的边界分别说明；不修改上游PR、不新建Issue、不自动合并或resolve审查线程。

独立[data revision02复审](../../data/processed/issue12_alinea_actuation_20261012_v1/CA_I12_PACKET_R900_S17_DIAG01/revision02/FINAL_DATA_REVIEW_V2.md)17文件绑定`ceb419041514dea7904870430446f048683cb5ad847f32f124c632d66f799827`通过；[科学复审](../../artifacts/issue12_phase_order_fix_20261013_v1/FINAL_SCIENTIFIC_REVIEW_V1.md)GO修复交付、无新增finding。原V1数值字段全部相同，1338terminal结果字节相同，95raw/原9文件保护通过。本复审没有把公开subset称为完整raw在线重算，也不提前声称未来commit已测试。

真实干净checkout测试提交`2f24afa154fa74808f40f6087c54bf06cdde4d0b`：4/4新回归方法、19负例通过；工作目录Gitclean，raw仅.gitkeep，新helper/test/publicfixture逐字节等主目录。[独立回执](../../artifacts/issue12_phase_order_fix_20261013_v1/clean_checkout_v1/CLEAN_CHECKOUT_RECEIPT_V1.json)注明Git对象借用本地、复用现有Python环境、跳过无关LFS；测试工作文件来自完整已提交tree，不读取main的ignoredraw，没有重跑完整raw audit或SUMO。随后仅追加文档/回执，分析实现和测试不变。修复交付在原PR13，回复原P2而不自动resolve线程或宣称Reviewer已接受；下一步仍用户/Chat审查。

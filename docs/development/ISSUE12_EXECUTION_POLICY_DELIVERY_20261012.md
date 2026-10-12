# Issue #12 执行政策工程交付与资格边界

2026-10-12｜基线20e5e83ac059768320cdaa4c815d164e1022de45；新900诊断已完成；独立数据与科学最终复核进行中，尚非用户验收。

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
| CA_I12_PACKET_R900_S17_DIAG01 |1272s|9×8s，实际每周期G4/Y2/red2、2绿车、黄/红入口0；C=pending=applied=E=N18|一次实际诊断，firstred1207；18ID均rear-clear；数据独立复核待完成 |

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

短窗实际放行与全域qualification分开：300限定实测6/72s；旧900 STOP不是物理不可达。新900在72s、seed17供给下实际18辆，即900veh/h；原hardguard在观测范围均未拒绝。此事实支持当前短两车包高端的局部可行性，最终数据/科学GO仍待复核；450/600/750未新native，不写PASS。整数周期映射仅名义最大相对误差5.882%，实际N、连续rate更新延迟、长窗安全、多seed服务与正式ALINEA效果尚未验证。原Stage6结项、A1 UNRESOLVED、Candidate A NOT_QUALIFIED、旧STOP3与空未冻结协议保持。

下一步建议不构成执行授权。新Draft PR待完整证据/三方postreview后提交，直接base codex/candidate-a-native-smoke-proposal /20e5，保留PR1→3→5→7→9→11，上游不修改/retarget/合并。用户/Chat负责审查接受及重大科研取舍，Codex不代替验收。

## 原始数据版本身份

| 本次身份 | raw文件/字节 | manifest SHA-256 | 本地原始重算/公共审查 |
|---|---:|---|---|
| QUOTA_R300_DIAG01 |81/148115726|358e427bef1ba58d291376d6fed36e767a223603f6e0a29ea3a6a127353f6486|完整raw仅主目录；公开清单/摘要/FAIL |
| QUOTA_R300_FIX01 |82/163352995|c63436ebcaf75efc969c8778c3cde11de6181b41c7ce9a13a2536d9e4e268ea6|完整raw仅主目录；公开独立数据和有限PASS |
| QUOTA_R900_BOUNDARY01 |79/146880941|f2ed45d66b2087a88cf8b7ce4af4d0d38131e6302ef43ded251a908cd655fa7f|完整raw仅主目录；公开STOP/源码调查/审计修订 |
| PACKET_R900_DIAG01 |95/164333753|253c894c52c21a009094dbb7ee80586473f21a0e194abce4d86ccdfb54efde40|完整raw仅主目录；公开精确卡/工程/数据与科学复核 |

工程41binder `cfef72429d1f4dc454dc0632237e82297dfe59d6cff6e4a0472525857d1ad415`，实际新run工程binder `b1c324b9442bb0a28ab279247cb02b62513e8e00f305c2005ffb79c91cede4f8`；所有旧38依赖/536保护、新49源均核对一致。完整单次启动命令/PID/两种时间口径见[真实工程receipt](../../artifacts/issue12_alinea_actuation_20261012_v1/runs/CA_I12_PACKET_R900_S17_DIAG01/engineering/EXECUTION_RECEIPT_V1.json)。所有实际运行均各自消费精确卡；不能照抄命令重跑。

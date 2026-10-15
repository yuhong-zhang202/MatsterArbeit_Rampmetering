# PR #13 P2：packet900相位顺序独立数据复审 revision02

2026-10-13。**PASS：已用既有真实TLS／ACK记录明确验证九个连续GGGGyyrr周期及八次周期间r→G，修复旧V1只有每周期计数与自报motion相互吻合的覆盖不足。** 没有新SUMO、相位／guard／卡片／运行配置修改，没有上游PR操作；本次PASS不扩大长期安全或服务资格。

## Context与原问题边界

读取AGENTS、PROJECT_STATE、DECISIONS、WORKLOG及空／未冻结EXPERIMENT_PROTOCOL。项目仍正式实验前工程交付、原Draft PR #13待审；本用户任务是4552241审查版本的P2离线修复，不是新Issue或研究设计。Stage6既有结项、A1 UNRESOLVED、Candidate A NOT_QUALIFIED不变。

旧revision01/audit_packet_actual_V1.py核了原始SHA、逐步FCD／TLS与自报motion、C/E/N、各周期G/y/r秒数；未独立要求时间上连续的G→y→r顺序，相同计数的重排可能漏检，TLS转dict也可能隐藏重复时间。旧报告及9文件绑定原样保留，明确它不具备本轮新增顺序证明。原有N、body、末步arrival等结果没有因修复改变。

## 新增顺序门：时间与证据各自绑定

原XML TLS time=t是运动BEGIN，post和两阶段ACK end=t+1；新helper在转dict之前接收原始有序72行，保留重复，逐条要求BEGIN1200…1271／ACK1201…1272连续。程序必须I12_PACKET8，受控灯ramp_mid且phase0/G、1/y、2/r一致。每周期明确连续`GGGGyyrr`，缺失、重复、未知、同计数重排／打断均拒绝，不以Counter或selfreported totals替代。

原生转换到期前getter可能仍处于旧相位：BEGIN1206 pre是phase1/y且nextSwitch1206，但本运动及ACK1207为phase2/r；BEGIN1208 pre是phase2/r且nextSwitch1208，本运动及ACK1209为phase0/G。helper分别核两侧身份和switchclock，不错误要求phase_before等于该步motion。

每周期ACK(begin+4)完成最后G后setPhase1，读回y／nextSwitch(begin+6)，这是setter之后状态，不是刚完成运动TLS。每个首red ACK(begin+7)实际phase2/r后setPhaseDuration1，完整ATTEMPTED／READBACK_VERIFIED、请求时刻／cycle／quota／nextSwitch(end)核对。新检查同时使用18 phase-request事件和18 duration记录，准确区分这两种trace阶段。

精确观测区间：

| 周期BEGIN | G | y | r | 首red ACK |
|---:|---|---|---|---:|
|1200|[1200,1204)|[1204,1206)|[1206,1208)|1207|
|1208|[1208,1212)|[1212,1214)|[1214,1216)|1215|
|1216|[1216,1220)|[1220,1222)|[1222,1224)|1223|
|1224|[1224,1228)|[1228,1230)|[1230,1232)|1231|
|1232|[1232,1236)|[1236,1238)|[1238,1240)|1239|
|1240|[1240,1244)|[1244,1246)|[1246,1248)|1247|
|1248|[1248,1252)|[1252,1254)|[1254,1256)|1255|
|1256|[1256,1260)|[1260,1262)|[1262,1264)|1263|
|1264|[1264,1268)|[1268,1270)|[1270,1272)|1271|

周期间r→G实际观察于1208、1216、1224、1232、1240、1248、1256、1264，共8次；最后观测TLS BEGIN1271和ACK1272仍r，不推断或伪称第10G已执行。

## 独立实际复算与父回归审查

新audit_packet_actual_V2.py从真实raw构建有序TLS／post72／ACK144及两条完整request traces，先逐字段与父公开fixture相等核对，再把**真实raw构造的输入**送入独立helper；没有以fixture代替真实raw审核。五个源文件及95文件manifest SHA仍完整核查。父fixture是可公开顺序测试子集，不能独自替代原FCD／末步arrival／native日志全量审计。

独立阅读phase_sequence.py及父回归：4methods／19negative mutations针对同计数重排3例、missing／duplicate／fractional／unknown／identity／ACK问题9例和switch／setter／trace问题7例；positive保留真实pre pending边界。四项helper／test／fixture／provenance源SHA与父REGRESSION_RECEIPT_V2相符。父V1语法导入ERROR没有执行计划4methods；原失败源码／日志／receipt保留。父V2实际4methods PASS，unittest内0.017s与完整进程receipt0.101648s是不同口径。本data任务**未重跑父4method套件**。父随后可能做clean checkout验证，当前本记录不声称该验证已执行。

唯一必要实际命令：`.venv/bin/python -B data/processed/issue12_alinea_actuation_20261012_v1/CA_I12_PACKET_R900_S17_DIAG01/revision02/audit_packet_actual_V2.py`，returncode0、2.047646s、stderr为空；source快照SHA07f316795f6f08faa713406514d8b2e08a97daa87dd9ac947f8c411f6ffb1d7a。新helper是审查基线4552241上的未提交分析实现，不能声称已测试未来修复commit。

保留执行原V1全部实际数据核查：95raw／164,333,753B原manifest253c894c…；1272FCD／TLS／ACK、18唯一G入口、九G4/y2/r2及C=pending=applied=E=N18、18body actual-clear／40观察行、1338正常到达末步、61条件WAIT、nine yellow筛查／2547原生日志EOF均PASS。除新增phase顺序和fixture来源字段，新JSON结果逐字段等于旧结果，1338终点结果逐字节相同；旧9文件SHA全部不变。旧原始源、卡及runtime未改，不复跑native或旧工程套件。

## 判定与交接

本轮准确补足P2顺序覆盖，未发现新增必修data finding；建议父代理进行顺序scientific_reviewer复审后更新原Draft PR #13并回复评论。只证明冻结packet900短窗中的相位序列／绑定与原数据一致，不证明长期RATE_QUALIFIED、300–900全域、live ALINEA或正式实验就绪。当前协议仍0B，未冻结；建议不构成新仿真授权。

完整实际日志／收据／新输出／保护证据与源哈希见FINAL_DATA_BINDINGS_V2.json；原revision01保留历史局限，不覆盖。

# Stage 6 Ramp-Induced Mechanism — Luna High Operational Specification

Date: 2026-09-22. Status: **PROPOSED OPERATIONAL SPECIFICATION / ZERO STARTS AUTHORIZED**.

本文件把已审查的设计转换为分阶段操作合同；不是 exact launch card，不含仿真启动命令。当前任务只编写本规范。下述工程物化、离线测试和运行步骤是未来获批后的工作，不代表本轮已执行或已授权。Luna 是执行协调者，不能替代项目要求的独立 engineering/data/scientific review。

## 0. 先读这四句话

1. 明确结论包括 `NOT_EVALUABLE`。不能为了交付二元结论而推断未知量。
2. 不把同 seed 当逐车随机属性相同；不把全部插入/到达当没有源端问题；不把E2零队长当城市侧安全。
3. 不更改P/S/L/A/C、100 m、30 s、参考窗、阈值或归因规则。原始 classifier 输出与本设计的配对判决分列保存。
4. 每个 start 单独授权、最多1次、零重试。所有运行结果后 STOP；不能因 control PASS 自动启动 transition。

## 1. 权限状态机与交接物

|阶段|Luna操作|必须产出|停止边界|
|---|---|---|---|
|A0 Context|只读核对设计与来源|`context_receipt.json`、冲突表|缺来源/冲突→停止|
|A1 Offline preparation|在另行授权的工程准备任务中编写新目录适配器、合成fixtures、输入草案；禁止调用模拟器|`readiness_register.json`、离线测试与静态diff|科学含义不明确→`PREPARATION_BLOCKED`|
|A2 Review / card|先工程/数据审查，再科学审查；全部required issues关闭后才制作单run未授权卡|input/code/output manifest、`DRAFT_NOT_AUTHORIZED` card/hash|等待用户批准该exact card/hash|
|B Control start|只执行获批control卡1次|start计数、receipt、完整raw manifest|任意结果停止，无retry|
|C Control closeout|离线生命周期、classifier、PRE/control screen、独立审查|`control_decision.json`|PASS仅允许请求transition制卡/审批，不放行start|
|D Transition start|仅control允许且另有exact transition卡批准后1次|该run独立raw/receipt|任意结果停止|
|E Pair closeout|两run完整审计、时序与适用性分开判定、科学复核|`pair_decision.json`、`REPORT.md`|所有分支STOP；无B/C/seed23/下一qMain自动运行|

不要复制旧 `USER_APPROVAL.json`、`execution.lock`、历史launch card或未消费start标志。旧3350唯一start已消费，与这里无关。方案上限不是授权额度。

## 2. 不可变设计合同

Authority: `docs/methodology/STAGE6_RAMP_INDUCED_BREAKDOWN_VALIDATION_PLAN.md` SHA-256 `62fb63eb49ae98b58bc45ad6bc7d60cd21fcdb73b3327c34b97c5151b01ca355`；对应review `STAGE6_RAMP_INDUCED_BREAKDOWN_SCIENTIFIC_REVIEW.md`。若内容hash改变，停止核对，不能静默更新期望hash。

|字段|首选control|首选transition|
|---|---|---|
|Proposed run ID|`RI3350_CTRL_S17_attempt1`|`RI3350_RON_S17_attempt1`|
|qMain / M number|3350.4 /1396|相同|
|qUrban / U number|360 /150|相同|
|qX / X number|180 /75|相同|
|M/U/X时间|[0,1500)|相同|
|R number /时间|0 /无R|192 /[540,1500)|
|qRamp source rate|0|540前0，之后720 veh/h|
|seed / horizon /step|17 /[0,2700) /1 s|相同|
|meter /urban TLS|A_OPEN /已接受固定TLS|相同|

PRE=[360,540)，固定90 s blocks [360,450)、[450,540)，6个30 s bins；core cells13–17，邻居掩码也要读12/18。control观察blocks=[540+90j,630+90j)，j=0…9。主要R持续暴露观察=[720,1440)，[1440,1500)尾段和完整0–2700仍输出。需求结束1500，clearance1200 s。

MAX_QMAIN_CANDIDATES=2；preferred starts2；hard ceiling4；retry0。3199.2/seed17完整配对仅为确认F1后另行审批的备选，本规范不给它生成输入。seed23、B/C均在本规范执行范围外。

以上窗口和需求完整性screen来自设计的PROJECT OPERATIONALIZATION，不是新物理常数。此SOP如需增加实质判据，标记 `PROPOSED_CLARIFICATION_REQUIRES_REVIEW`，不可声称原设计已批准。

## 3. A0：Context与来源绑定

按顺序读取AGENTS、PROJECT_STATE、DECISIONS、SUPERVISOR_FEEDBACK、WORKLOG最新相关项、EXPERIMENT_PROTOCOL，再读设计及review、locked method及review、MAINLINE_REFERENCE_SELECTION_SPEC。空formal protocol是已知探索性边界，不授权正式实验。新冲突须记录。

来源清单：

- 历史3350输入目录：`artifacts/stage6_baseline_localization_20260921_v1/LOC_M3350_S17/engineering/inputs/LOC_M3350_S17_attempt1/`，读取`demand.rou.xml`、`scenario.sumocfg`、`scenario.add.xml`、`output_roles.json`及manifest。
- accepted net：同engineering目录下`build_attempts/TV_BUILD01/network.net.xml`，hash `887c232483f0c68dc024334ff5997250d7d36299ab2744bdcf49d5a314c700ca`。复用字节，不运行netconvert。
- locked method：`docs/methodology/FREEWAY_PROTECTABLE_STATE_EXPLORATORY_DEFINITION.md`，hash `22fe22170c17ce74e261e717586a458a1b5173e9deabbee925bd4c1d606adfe7`。
- 原analyzer：`data/processed/stage6_protectable_state_application_20260921_v1/apply_rule.py`；3350适配器：`artifacts/stage6_baseline_localization_20260921_v1/LOC_M3350_S17/engineering/analysis/apply_rule.py`。先审查入口和输出路径，不直接运行旧脚本。
- 参考screen实现候选：`artifacts/stage6_mainline_reference_library_20260922_v2/reference_selector.py`；先验证真实路径/依赖/是否写入旧目录。规范是语义来源，历史脚本PASS不保证泛化。
- 旧ledger/audit：`data/processed/stage6_baseline_localization_20260921_v1/LOC_M3350_S17_attempt1/`；用途是schema/对账参考，不是新run结果。

每项receipt记录`role,path,sha256,size_bytes,exists,read_only_source`。路径不存在不猜替代；用repo检索确认并记录理由。禁止导入有顶层写入/启动副作用的模块来“检查”。无必要不执行`sumo --version`；从已有receipt读版本，未来exact card需核对可执行文件身份。

排除revision03补充指标和旧offset脚本作为新状态/参考算法。保留历史输出，不在本任务顺手修复。不得将82/38个cell-periods当独立样本。

静态工程审计已发现以下复用陷阱，未来必须有专门回归：3350 `apply_rule.py`的`parents[4]`根路径在该位置并非repo根，且RUNS/RAW/ENG/APP、independent_slice('LOC')及R300报告文字硬编码；`reference_selector.py`顶层会创建旧输出目录，main会重写历史结果；旧`launch_once.py`绑定已用授权和lock。禁止直接import/main执行。新适配器显式注入路径，科学helper保留AST等价与原fixtures/历史数值回归证明；单凭py_compile不够。若发现原科学helper与规范有实质不一致，STOP审查，不偷偷修复。

旧生命周期例子确切路径为`data/processed/stage6_baseline_localization_20260921_v1/LOC_M3350_S17_attempt1/audit_lifecycle.py`；它硬编码旧class counts/window/card与部分sentinel处理，只借鉴schema。`artifacts/stage6_targeted_validation_20260920_v1/engineering/runtime_executor.py`和`test_runtime_executor.py`同样仅静态借鉴，禁止运行其历史多run顺序或写入旧fake-test receipt。

## 4. A1：输出目录和物化允许差异

未来准备任务使用新版本根，例如 `artifacts/stage6_ramp_induced_validation_<date>_v1/`。若存在则选新版本，不覆盖。输入/适配器/fixtures/receipts/review放artifact；仅获批运行的输出写独立`data/raw/stage6_ramp_induced_validation_<date>_v1/<run_id>/`并在run完成后不可变；解析结果放对应`data/processed/`，表格`results/tables/`。本规范不创建这些run目录。

未来静态diff允许项仅：run/output路径，source绑定，R flow删除或开始时间540/number192，独立run ID。M/U/X既有number、begin/end、route、type、departPos/Lane/Speed、geometry、step、seed、TLS和行为参数不可改变。control和transition共同M/U/X XML语义必须一致；M保持departPos100，不能“顺手优化”成last。

XML解析核验而非纯文本替换：

1. 只含期望route/type/flows；M1396/U150/X75，R0或192；不留隐藏重复flow。
2. R192×3600/(1500−540)=720；total scheduled control1621、transition1813。
3. 所有文件引用存在，指向新输出目录；没有引用旧授权/旧raw写路径。
4. compiled net byte hash相同；TLS A_OPEN从0启用，不引入前段红灯。
5. 九个E1和原E2/TLS/FCD/vehroute/tripinfo/summary/lanechange输出角色齐全；1Hz/30s不变；unfinished/undeparted记录能力保留。
6. 输出`scientific_input_diff.json`：逐属性before/after/reason/allowed；不在白名单的差异均FAIL。

不要在当前设计任务执行这些物化操作；这是一份后续工程准备步骤。

## 5. 运行前必须关闭的readiness register

每项用`PASS / FAIL / UNKNOWN`，附证据路径/hash和审查人。UNKNOWN不能写成PASS。

|ID|待验证项目|达到PASS的证据|未关闭时|
|---|---|---|---|
|R01|source/hash/input diff|静态核验通过|不制卡|
|R02|单start runner|离线mock证明重复调用、旧批准、卡hash不符均拒绝；异常也不retry|不制卡|
|R03|配对随机实现|记录同M/U/X输入、属性抽样/存档策略；不悄悄预固定speedFactor改变模型；明确后验比较字段|不制卡或提交方法问题，不能承诺严格匹配|
|R04|classifier adapter|只有I/O与run mapping变化；旧fixture回归及未知归因传播通过|不制卡|
|R05|新R0 PRE screen|保持原数值/掩码语义，新输入whitelist仅用于直接PRE，不冒充旧bank；边界fixtures通过|不制卡|
|R06|R区间暴露|漏aux、跨bin、route缺失、重复crossing fixtures通过|不制卡|
|R07|urban/source归因可观察性|逐项说明哪些现有raw能判定、哪些只能UNKNOWN，独立审查是否足以完成计划|无法支持baseline acceptance就不得承诺该结论；缺失必需覆盖先停止制卡|
|R08|结论逻辑|本文件§12真值fixtures通过，保留两个独立结论|不制卡|
|R09|工程/数据/科学review|required issues0且全部证据绑定|不制卡|

R03不是要求在运行前证明实际轨迹相同；它要求明确并审查核对方案。新run实际匹配只能后验验证。若实现必须修改抽样/车辆属性，STOP提出新方法审批，不能把它当普通路径适配。

R07不得通过新TraCI observer隐式补齐；额外观测代码或新增输出需单独声明、检查其非干预性并获批。G6既有NOT_ESTABLISHED不能复制成新run的FAIL或PASS。

## 6. A2/B/D：单run card与执行合同

只有未来明确获批制卡任务才生成exact card。卡必须绑定：run ID、condition、所有输入/脚本/方法hash、binary身份、输出角色/绝对路径、完整argv、seed、horizon、max_starts=1、retries=0、approval_required=true、progression_allowed=false、当前pair累计start数。

卡还须明确单run timeout/storage stop-line及中断收据处理。设计中的“两run五分钟/150 MB”是预算估计，不是已批准的单run kill阈值；不要复制旧卡180s等限额冒充本次批准。新resource guard随exact card一起交用户审阅；触发也消费该次start，无retry。binary/environment与历史不一致先报告，不自动安装或升级。

用户批准必须指向该run、该revision、该hash；检查后原子创建不可复用的消费记录，再允许单次launch。即使技术失败也消费，不清除lock重试。异常中断后先只读查process/receipt，不重新launch。不得把“执行整份SOP”解释为未限定的仿真批准。

进程结束立即保存return code、start/end/wallclock、stdout/stderr、实际输出清单hash/size、是否完整到2700、启动总数。raw归档后只能读。技术失败仍写receipt和可用ledger，结论F5_TECHNICAL_FAILURE，停止。零输出不等于零车辆。

## 7. C/E第一步：原始完整性与独立生命周期账本

必须先账本，后baseline/next-step判断。不得让analyzer正常退出代替完整性检查。

解析manifest绑定的source XML：scheduled来自输入需求语义（流量发车时刻以SUMO既定语义核验，不猜舍入）；actual depart/arrival来自vehroute/tripinfo和summary交叉证据；FCD证明观察覆盖，不能独自代表全部scheduled IDs。prefix与route双重校验M/R/U/X。

`vehicle_lifecycle_ledger.csv`每个scheduled ID一行：

`run_id,vehicle_id,class,route_id,type_id,scheduled_depart,actual_depart,depart_delay,inserted_before_source_end,arrival,arrived,unfinished,never_inserted,first_fcd,last_fcd,first_core_time_lower,first_core_time_upper,speed_factor_precise,source_evidence_ids,status,reasons`

control R无行，但class summary必须显式R scheduled0。不要虚构一个R0车辆。缺失observed车辆与never inserted分开；后者必须由完整记录/对账证实。

核对集合而不是仅核对总数：

```text
Scheduled = Inserted disjoint-union NeverInserted
Inserted = Arrived disjoint-union Unfinished
No observed ID outside Scheduled; no duplicate identity/event
Delay = actual_depart - scheduled_depart (only when both known)
```

class summary记录requested rate、scheduled、demand内inserted、late inserted、never inserted、arrived、unfinished、delay min/median/p95/max、每30s插入/到core数和source waiting曲线。`p95`统一linear interpolation；仅描述，不新增门槛。

设计demand screen要求全部在对应source window插入、无late/never、2700无unfinished。数值边界[0,1500)、R[540,1500)；不能将1500时插入算需求内。若某守恒式UNKNOWN→F5；守恒通过但需求screen FAIL，保留真实损失，不能删车计算。

检查XML结束、0…2699 labels、重复(time,id)、finite speed/x、route/type关联、precise speedFactor、未知M lane、内部lane映射。完整时间标签中无车可以是真空，不是缺数据；缺时间标签是缺测。raw completeness和population validity分别记录。

显式解析负值sentinel：arrival=-1不是“已经在2700前到达”；结合actual depart和undeparted标志区分未插入与已插入未完成。缺字段/缺record不是合法sentinel。最后FCD标签2699不是arrival时间2700，也不能据其推断已到达。为负arrival、负depart、缺记录和双源冲突分别建fixture。

## 8. 第二步：锁定classifier与直接PRE/control screen

### 8.1 classifier

完整0–2700应用原P/S/L/A/C逻辑；不裁掉初始化/尾部，也不以PRE替换原exact preceding90 s reference。不得强行让S/P/L嵌套。独立保存原始输出、数值候选、归因标志及配对判决；任何外部新证据只能进入有provenance的审计层，不能覆盖历史列。

绝对速度用m/s；ratio逐样本`speed/(actual lane speed limit * precise vehroute speedFactor)`，再按样本平均，不先按车辆等权平均。density用实际lane length与完整30labels；pooled分母两条through lane总长度，不能用单lane长度或两lane平均速度代替sample pooling。merge_section_0 auxiliary单列。

物理lane0：main_up_0→:freeway_merge_0_0→merge_section_1→:merge_end_0_0→main_down_0；lane1对应_1→_1→_2→_1→_1。从compiled connections复核，不按后缀猜lane。

### 8.2 新run直接screen，不创建跨run参考库

`cell_lane_bins.csv`主键(run,cell,physical_lane_or_pooled,bin_start)，包含N samples、unique M、labels、speed/ratio、M/MR density、slow fractions和simultaneous counts、validity/reasons、source hash。

`disturbance_mask.csv`从该run全套P/S/L/A/C事件构建，含短候选/unknown reference事件及C；按cell及邻居交集排除。catalog缺失≠空catalog，missing→UNKNOWN。C是pooled cell事件，不推断哪条lane触发。

合法零事件必须有独立`catalog_completeness.json`，绑定run/source/hash与`source_event_count=0, catalog_row_count=0, complete=true`。现有selector把无C rows当unknown，不能直接继承这一输入缺陷；新adapter只修正“已验证空集 vs 缺失”的数据契约，不减免掩码。若零行但无receipt、hash不符或源未处理，仍UNKNOWN。其他profiles同理。

固定PRE只有2 blocks×5 cells×3 scopes=30 screen rows；每row检查3 bins全部满足原screen：完整labels、unique M≥2、mean ratio≥0.85、positive finite densities、两个lane与pooled一致、无禁止mask，并满足block end≤cell±1最早disturbance onset。不得因早期事件不喜欢而删除mask。

`pre_state_gate.json` PASS仅当30 rows全部PASS；UNKNOWN优先于任何“正常”结论，全部reason保留。0.85是高通行screen不是物理freeflow真值；无critical density阈值可用。

control另有10 blocks×5 cells×3 scopes=150 rows，[540,1440)全部PASS才可称`CONTROL_HIGH_MOBILITY_PASS`。尾段1440/1470 bins及全horizon仍报告。若transition合格事件落在primary window外，补核其同绝对时间control bins及相关固定90s blocks；不得自选不同对照时段。1500后事件只报告，不用于本设计success。

不需要用旧A0/3350 bank判断新PRE：直接screen满足就报告；它不是bank whitelist扩展。未来如额外引用旧bank，须独立满足原composition/density/exposure support，失败UNKNOWN，不影响或替代P reference。

## 9. 第三步：配对一致性与R暴露时间线

### 9.1 Matching

`pair_matching.csv`逐M/U/X ID比较scheduled time、route、type定义、显式depart属性、precise speedFactor。再比较[0,540)实际插入与FCD(time,id,lane,pos,x,speed)的存档精度值。不发明数值容差；序列化相同字段按解析数值比较，并报告max absolute difference和不匹配ID列表。

输入差异不在白名单→FAIL；pre-R已分歧且无法解释→F5。post-R轨迹差异本来是研究结果，不能要求相同；但post-R生成车辆的type/speedFactor抽样差异属于潜在混杂，必须单列。不能靠删除不匹配车辆“恢复配对”。若属性差异影响归因且无已审查处理，mechanism=NOT_EVALUABLE，不给强匹配结论。

### 9.2 Crossing ledger

`r_crossings.csv`一行一个车辆一个边界：`run_id,id,boundary,lower_s,upper_s,lower_inclusive,upper_inclusive,observed_or_inferred,route_checked,evidence_id,unknown_reason`。boundary至少SOURCE_INSERT、AUX_ENTRY、THROUGH_ENTRY、DOWNSTREAM_ENTRY(main_down)。车辆换lane不能重复统计边界。

前一label仍upstream、后一label已经downstream→真实crossing在两label之间（通常(lower,upper]）；同一step路径可跨aux但未采到aux：以route连续性推断crossing区间，不能伪造aux停留sample。lanechange补充证据也保留其时间精度。不完整route或缺上界→UNKNOWN。

每30s bin输出certain与possible unique crossing counts；certain只在**所有可能时间都落在该半开bin**时+1，possible为区间与bin相交的上界计数，跨bin同车只能有一个certain归属。exact time若为边界30归[30,60)，(29,30]跨bin不是certain。上游通行首次见到不是一定首次实际进入，标明左删失。

`r_exposure_bins.csv`最小字段：`run_id,bin_start,bin_end,aux_certain_ids,aux_possible_ids,through_certain_ids,through_possible_ids,aux_certain_count,aux_possible_count,through_certain_count,through_possible_count,t2_lower,t2_upper,t3_eligible,r_exposure_status,evidence_refs,unknown_reason`。ID lists按唯一ID排序并用JSON数组编码；possible为可能进入的全集上界，包含certain，不将二者相加。缺失上界/route evidence用UNKNOWN和null count表示，不能写0；保留已确定ID集合。possible只能诊断，不能单独通过T3。

T2取所有R最早aux-entry的区间：同时报告哪个ID可能/确定最早，不能按首次采到aux样本排序冒充真实顺序。T3仅用在T2最晚可能到达之后开始的完整bins，找首组三个连续bins各certain aux-entry≥1；confirmation为第三bin end。T3 confirmation≤720才能通过预定暴露计划；only possible满足→UNKNOWN/F5，不能滑窗。

每个候选P qualification bin也记录ongoing R entry的certain/possible counts。为消除“ongoing”的执行歧义，本SOP提出保守细化（**PROJECT OPERATIONALIZATION / PROPOSED_CLARIFICATION_REQUIRES_REVIEW**）：P的每个qualification bin均有≥1 certain AUX_ENTRY才令`R_ongoing_exposure=PASS`；任一完整可观测bin的possible上界为0则FAIL；否则only possible或未知覆盖为UNKNOWN。保留不通过事件，并注明该暴露细化可能拒绝间歇信号车队导致的真实效应。这是配对机制资格规则，不改变P事件或原classifier。该细化需随SOP被审查并在制卡前明确接受，不得事后调整。辅助入口是merge opportunity，through entry证明实际主线加入，两者分别报告，不用一个替代另一个。

### 9.3 Chronology

`timeline.csv`至少T0 PRE confirmation540、T1 scheduled540/actual insertion、T2 aux/through、T3 start/confirmation、T4首次C/更强M事件、T5P onset区间与confirmation、first R downstream、T6propagation/recovery。所有marker有lower/upper/status/evidence；不存在写NOT_OBSERVED，缺测写UNKNOWN，不用0。

从540到T2前完整bins仍须high-mobility/no-warning；边界bin用1Hz解释，不改30s classifier。R-before-M判定使用区间不重叠的时间顺序；区间重叠而raw不能消除→ORDER_UNRESOLVED。T4是已锁定事件级最早warning，不伪称第一次微观刹车。P onset为首low-bin内区间，不等于confirmation时刻；90 s aggregate低态不是90秒每辆车连续慢。

## 10. 第四步：归因与城市侧适用性

`attribution_audit.csv`每事件×alternative一行：source insertion、downstream tailback、direct TLS、geometry/unrelated bottleneck。字段`status(CLEARED/CONTRADICTED/UNKNOWN),evidence_paths,hashes,vehicle_ids,cell_lane,time_bounds,reason,reviewer`。不得把空数组当CLEARED。

必须给出事件前/期间/后的全空间lane-bin表，以及upstream/merge/downstream FCD与E1上下文。E1混合M/R，不称M-only flow；M downstream count从ID cross ledger计算。空间传播顺序若相差不足30s不能凭相同bin声称上游传播。无传播不自动否定localized P。

source审计看scheduled vs实际插入、delay曲线、boundary queue与实际M supply；全部最终到达仍可能需求期受限。已接受geometry不等于任何新事件的几何归因自动清除。TLS程序同样不保证urban platoon未影响R暴露。

`urban_audit.csv`按run、fixed phase/bin记录ramp/E2队长、internal/shared R occupancy、stopped-chain/storage_cross证据、同地点时间方向的R→U阻塞证据、U depart/system/travel/delay、R/Uunfinished。区分：R存在、R排队、storage_cross、直接U obstruction四级证据；不能由前一级自动推出后一级。

队列/阻塞采用已审查的项目谓词并绑定版本。若现有谓词不足以形成direct evidence，登记UNKNOWN并提请方法审查；Luna不得新增车距/停速/持续时间阈值。stopped-R crossing chain与U阻塞有明确关联→baseline veto。没有检测事件只有在完整覆盖且检测方法adequate已验证时才支持absence；否则NOT_ESTABLISHED。

“material insertion artifact”“severe urban deterioration”没有approved全自动数字阈值。此SOP不补造：输出事实和候选证据，由独立review作有证据的CLEARED/CONTRADICTED/UNKNOWN；review无法判定→F5或suitability NOT_EVALUABLE。不能只写主观“看起来正常”。若必须新增定量阈值，须在新run outcome前另行审查批准，不能事后调到过关。

## 11. 第五步：逐事件资格表

`mechanism_event_gate.csv`保留所有core事件，每事件字段：

`event_id,cell,onset_lower,onset_upper,confirmation,end,locked_P_status,local_reference_status,numerical_gates,attribution_status,control_PRE,transition_PRE,control_same_time,pre_R_stability,R_T3_by720,R_before_event,R_ongoing_exposure,identity_measurement_integrity,strict_demand_suitability,pair_matching,event_eligible,reasons`

event eligible只在设计所有required gates PASS且confirmation<1500时TRUE；=1500按设计“before1500”不通过，保留边界原因。事件必须在真实R之后，而非540之后即可。若P duration成立但reference unresolved，记UNKNOWN，不能写P-negative或改参考。S/L/A/C独立保存作robustness，不替代P。

这里的required gates仅指**机制识别**要求：身份/观测完整、足够M/R实际暴露、配对、时序及替代原因排除。`strict_demand_suitability`（所有车辆source window内插入、零unfinished等）是另一个轴，不直接决定`event_eligible`。例如一个late/unfinished U必须使strict suitability失败，但只有它破坏暴露/配对/归因时才同时否定机制识别。观测或身份缺失与完整记录下确认存在late/unfinished必须分开。

现有analyzer会保留source/tailback归因UNRESOLVED。独立review补齐证据不等于修改原输出：增加`locked_numerical_positive`、`locked_attribution_original`、`reviewed_attribution_status`、`adjudicated_P_status`与签名证据。只有原数值/reference/population门槛全过且经review逐项CLEARED，审计层才可写`adjudicated_P_status=RULE_GATES_SATISFIED_WITH_REVIEWED_ATTRIBUTION`。这不是重新定义P或把未知强行改CLEAR。控制组存在本身不足以清除归因。未完成该独立归因接口验证前，R04/R07不可PASS。

不用“最明显事件”替代全量表。总结首个eligible onset和全部eligible数量/空间，分别报告cell-seconds与unique union time，不能累加多cell当总拥堵时长。速度/density summary注明sample/bin/event权重，不把相关bin当独立统计样本。

## 12. 结论状态机：不确定性本身是明确结论

下面是保守执行映射，不扩张原设计的科学定义。F1若仅有reference-unresolved长低态，不能由Luna自行解释为确定“qMain太高”；提交审查，否则F5。F2也不能仅用P-negative推出正常。

### 12.1 仅完成control

1. 资料/输入/账本/原始覆盖错误→`CONTROL_NOT_EVALUABLE_F5`。
2. 原P完整阳性且归因支持真正无R持续恶化→`CONTROL_UNSUITABLE_F1`。非P的持续pattern只有独立review明确支持且不修改classifier才能记录F1；未审定→F5。
3. PRE30rows和control150rows全部通过、需求与source检查通过、无未解决的相关artifact→`CONTROL_READY_FOR_TRANSITION_CARD_REVIEW`。
4. screen失败但无足够F1证据→F5；不能强行二选一。

任何control状态都`progression_allowed=false`；READY仅允许请求另行制卡/批准。此时pair机制/适用性均为NOT_EVALUATED，不能报success。

### 12.2 完成pair后的两个独立轴

- `mechanism_status`: SUPPORTED_EXPLORATORY / NOT_SUPPORTED_THIS_REALIZATION / NOT_EVALUABLE。
- `baseline_suitability`: PASS / FAIL / NOT_EVALUABLE / NOT_ASSESSED_NO_MECHANISM。

mechanism只由PRE、control、匹配、R exposure、时序、完整P和替代原因证据判定。urban suitability未知**不能抹掉已建立的机制证据**；但若城市故障解释了主线事件本身，它也影响mechanism attribution。

```text
if global_required_identification_gap:
    branch = F5; mechanism = NOT_EVALUABLE
elif confirmed no-R sustained impairment:
    branch = F1; mechanism = NOT_SUPPORTED_THIS_REALIZATION
elif eligible P event exists:
    mechanism = SUPPORTED_EXPLORATORY
    if suitability == PASS: branch = SUCCESS
    elif suitability == FAIL: branch = F4
    else: branch = F5_SUITABILITY_ONLY  # preserve supported mechanism
elif valid post-R high-mobility screen throughout evaluable exposure:
    branch = F2; mechanism = NOT_SUPPORTED_THIS_REALIZATION
elif observed L/C/other fully evaluated non-P impairment:
    branch = F3; mechanism = NOT_SUPPORTED_THIS_REALIZATION
else:
    branch = F5; mechanism = NOT_EVALUABLE
```

F2完整screen适用固定post blocks和实际R到达后的边界诊断；不对没有暴露的时间假称“R无效”。F3仅用于没有未解决P级持续候选/关键归因缺口的可评价结果；如有则F5。已确认城市veto作为独立flag始终保留，即使主branch F1/F5，不隐藏。

`global_required_identification_gap`只包括影响本次机制结论所必需的全局资料/配对/暴露缺口。逐事件reference/attribution不明只使该事件ineligible/UNKNOWN；若另有完整eligible事件，可保留SUPPORTED，并同时列出其他unresolved事件。不能因为任意一个无关事件不明就抹去有效证据；也不能用一个有效事件掩盖影响全局解释的真实缺口。若没有eligible事件且存在影响结论的unresolved候选，最终F5而不是F3。

`BASELINE_MECHANISM_CANDIDATE`仅mechanism SUPPORTED且suitability PASS。任何结论均不是正式baseline/O2 resolved。独立review可能修正审计结论，但不得改变门槛来追求success。

## 13. 最小机器可读交付合同

所有CSV UTF-8，数值单位列明确；NA与0区分，unknown reason不可空。JSON不写NaN/Infinity。每条派生记录有run_id、source evidence ID；manifest把ID关联到不可变path/hash。

必需文件：

|输出|最小内容|
|---|---|
|`input_manifest.json`, `processing_manifest.json`|raw/config/network/method/code hashes，软件环境，输出hash，禁止路径写入检查|
|`raw_completeness.json`|XML/grid/fields/IDs/mapping/output-role checks，observed vs missing|
|`vehicle_lifecycle_ledger.csv`, `class_lifecycle_summary.csv`|逐ID守恒、各class时间内实现、未插入/未完成|
|`cell_lane_bins.csv`, `reference_screen_rows.csv`|全部30s时空数据，固定block拒绝原因，PRE/control分开|
|`locked_classifier_outputs/`, `disturbance_mask.csv`|原分类各profile、所有episode和候选，不覆盖来源|
|`pair_matching.csv`, `r_crossings.csv`, `r_exposure_bins.csv`|属性/前段配对，certain/possible crossings与R flow|
|`timeline.csv`, `mechanism_event_gate.csv`|T0–T6及所有事件资格|
|`attribution_audit.csv`, `urban_audit.csv`|四类替代解释和城市侧分级证据|
|`control_decision.json`或`pair_decision.json`|两轴结论、branch、unknowns、start数、STOP|
|`independent_data_review.json`, `SCIENTIFIC_REVIEW.md`, `REPORT.md`|独立核对、required findings closure、通俗结论|

decision JSON模板（占位符，不是当前实验结论）：

```json
{
  "schema_version": "1",
  "pair_id": "RI3350",
  "design_hash": "62fb63eb49ae98b58bc45ad6bc7d60cd21fcdb73b3327c34b97c5151b01ca355",
  "run_ids": [],
  "starts_consumed": 0,
  "mechanism_status": "NOT_EVALUABLE",
  "baseline_suitability": "NOT_EVALUABLE",
  "branch": "PENDING_EVIDENCE",
  "baseline_mechanism_candidate": false,
  "evidence_refs": [],
  "unknowns": [],
  "review_status": "NOT_REVIEWED",
  "progression_allowed": false,
  "next_action": "STOP"
}
```

## 14. 离线fixtures与独立核对清单

禁止以测试名义start SUMO。只能合成内存/小XML fixture或读取已存raw，不写旧结果。

必须覆盖：

1. 单start runner mock重复/错hash/失败/中断后拒绝重启；不允许mock子进程调用真实SUMO。
2. R192 rate正确；R300/错start/end、M number漂移、旧输出路径、非白名单TLS/geometry diff拒绝。
3. R=0账本、never inserted、late at1500、unfinished、duplicate/unexpected ID、集合总数相同但IDs不一致。
4. PRE bin ratio=.85恰通过/<.85失败、只有1个unique失败、缺label与empty label区分、pooled好但单lane坏失败。
5. disturbance恰从block end开始不重叠，之前事件永久排除；相邻cell触发，missing C catalog→UNKNOWN。
   同时测试有完整receipt的零C/零其他事件→有效空掩码，而不是missing；无receipt零行仍UNKNOWN。
6. speedFactor精度/内部lane映射/实际长度；pooled unequal sample counts不能等权lane均值。
7. 原classifier fixtures；额外测试exact preceding reference、密度strict boundary、maximal run、population ended非recovery；method/code已有边界不一致→报告，不修门槛。
8. aux sample缺失但route可推断，(29,30]跨bin，exact30，missing upper，重复vehicle boundary；only possible三bins不通过T3。
9. T3 confirmation720通过/>720失败；R与P onset interval overlap→UNKNOWN；P confirm1500不success。
10. same seed但speedFactor变、pre-R轨迹差异、仅post-R速度变化应区别处理。
11. P-positive但urban unknown→mechanism可支持、suitability UNKNOWN；P unresolved≠F2；control单bin失败≠自动F1；F1不自动放行Pair2；所有terminal progression false。
12. 一条完整eligible P事件加另一条reference-unresolved事件→SUPPORTED并保留secondary unknown，而不是全局F5；全局matching坏仍F5。
13. 完整对账且P合格、存在已知late/unfinished U但不影响高速识别→mechanism SUPPORTED、suitability FAIL；U记录缺失/身份无法对账则是data gap，不能当已知censoring。
14. ongoing exposure三qualification bins都有certain≥1→PASS；一bin完整possible=0→FAIL；无确定零但一bin only possible或unknown→UNKNOWN；原P分类在三种情况下均保持不变。

独立data analyst必须从原XML另写小范围核对，不仅调用同一aggregation helper：至少一个PRE通过/失败fixture、一个pooled lane-weighting slice、一个R crossing边界、完整class lifecycle集合；有新run时按实际数据选择可用正/负slice，某类不存在明确写not applicable，不能捏造事件。科学review核对每个核心结论的evidence link；required issues全部关闭后交付。无可计算事件也要审查negative/UNKNOWN结论。

## 15. 最终给用户的固定报告结构

1. 执行了哪一步、哪些run、消费start数、是否出现technical failure。
2. control是否持续高通行；PRE失败精确到cell/lane/bin和原因。
3. R何时生成、插入、到aux、入through、出downstream；暴露是否足够，时间区间是否重叠。
4. 状态结论：速度/密度/人口/持续性、两lane影响、P/S/L/A/C；不是仅报最终P字样。
5. 转变/机制结论：时序与对照是否支持R admission associated deterioration。
6. 城市侧适用性单独结论和未知项；最后才给candidate布尔值。
7. F1–F5/SUCCESS及全部secondary flags；STOP，不建议自动执行下一点。
8. engineering/data/scientific disposition、文件path/hash、不可推断事项、下一项需要什么明确批准。

## 16. 当前完成度与置信度

本轮只有规范与交接文件，不存在新run、适配器实现、fixture执行或已授权卡。规范可指导工程准备及未来获批执行；不能承诺现有输出足够形成正面结论。High confidence：边界、需求算术、固定窗口和fail-closed交付；Moderate：方案可产生有辨识力的证据；Unknown：matching/urban attribution能否闭合以及是否出现P。

只最小更新WORKLOG/PROJECT_STATE；不更新DECISIONS、formal protocol、classifier、geometry、raw或旧review。阶段仍PARTIAL，O2仍NOT_RESOLVED。

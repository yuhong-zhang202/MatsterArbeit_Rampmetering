# 统一ALINEA执行器：最小实施与验收范围

**2026-10-13｜User-approved implementation and bounded technical diagnostics；离线及逐卡工程/数据/科学门仍须实际通过。** [用户批准及原文SHA](../../artifacts/unified_alinea_actuator_20261013_v1/USER_SCOPE_APPROVAL.json)；[批准时完整原稿](../../artifacts/unified_alinea_actuator_20261013_v1/SCOPE_AS_APPROVED.md)。 基线PR13/head `9eb95e29ccc85423084bc6945668cd36c3298b06`（Open/Draft，已复查无实质性finding）；旧900的revision02是历史技术证据，不是新统一执行器资格。主代理只读核对，工程/数据意见不等于批准。

## 1. 最小实施

- 在独立新namespace/任务分支复用现有packet、body、相位API、日志、resource guardian和原硬检查，不改或合并PR13。移除固定900/T8/终点的运行限定，按卡片支持整数T=8…24；请求quota仍2、Gmax4、Y=min(5,T−6)、red≥2，实际quota达到可提前结束绿灯并延长红至周期末。
- r_policy=7200/T，取最近档、平局取低率。周期中收到的新指令在下一完整周期边界应用，恰在边界收到的有效指令可当场应用，当前G/y/r不打断；同周期多条指令采用最新有效版本。控制器requested、mapped pending、实际applied各自积分，E为完成周期请求，N计全部真实入口（含yellow额外车辆），不cap、不补0、不强制E=N。
- 单独记录新指令ID/请求与实际应用时刻，恒定指令年龄不再冒充延迟。周期/相位审计由实际卡片及setter/readback/BEGIN/ACK对账，支持不同周期和partial；不沿用只适合旧900的硬编码GGGGyyrr checker。
- 复用项目`Feedback`标准ALINEA公式实例，沿用实际下游E1 `p1_main_down_20_l0` / `p1_main_down_20_l1` 的完整30s车辆事件占用率均值；无queue override、虚拟输入、调参或新控制算法。沿用[D019开发参考](../DECISIONS.md#d-019--execute-the-bounded-formal-design-development-trial)：11%、KR70 veh/h/百分点、30s、min300/max900/init900、dt1。`r_previous`仍是控制器自身clipped requested率，不回灌映射720或实测N。此为项目ALINEA实现，不冒称直接调用sumoITScontrol百分比green-share类。
- 初始化采用显式全局/控制器时钟平移：global1200对应既有class600；1200发初值，1230/1260用真实完整30s事件窗口反馈（logical630/660）。事件台账保持global时间，初始化时纳入正在占用检测器的车辆，窗口为[1200,1230)/[1230,1260)，保留跨窗ongoing事件；保存两种时间、检测器ID/单位/原始事件。该技术时钟适配已获本次用户批准，不改公式或跳过原时间校验。

## 2. 离线门（先通过再运行）

小规模回归覆盖17个整数周期的配置/连续相位与early-G关闭、nearest/tie/invalid映射、周期边界更新/多指令合并/延迟、requested→pending→applied→E/N账、partial/null、必要安全/未知停止。公开fixture/clean checkout可执行；不开展性能优化或A1完整证明。

固定900分支离线对照现有记录，核对实际setter序列、阶段时钟和安全判定相容；才能复用旧900为政策历史物理见证。即便相容，也不称新代码SHA已原生运行900。若产生实质行为变化，停止并申请调整范围，不偷偷补一个900或把旧结果拼成新版本资格。

## 3. 最小SUMO验证：4个计划任务，依次执行

输入沿用当前技术场景M3600/R需求900/U360/X180、seed17、dt1与原0–1200准备段；300/750是服务请求而非改变R需求。每任务新身份/目录/精确卡，前一项工程→数据→科学复核后才能进入后一项。

| 顺序 | 技术任务 | 已批准观察范围 | 核心判断 |
|---|---|---|---|
|1|同一新版本固定300→T24|1200–1272，3完整周期|真实双车及实际率是否支持300；不预填N6|
|2|同一新版本固定750→720/T10|1200–1270，7完整周期|−4%量化与实际执行误差分开；E14仅计划，不预填N14|
|3|有序变指令300→750→900→300|请求1200/1201/1226/1237；应应用1200/1224/1234/1242；至1266四完整slot|应有0/23/8/5s延迟，不重启当前周期；三种积分独立复算，不预填动态C或N|
|4|真实ALINEA闭环|激活1200，初值900；真实反馈1230/1260；至1272|检测器→反馈公式→限幅→映射→实际应用→真实N；partial/pending/censored如实保留|

任务2/3的终点1270/1266是本次已批准的技术周期对齐，不追改原1272运行。任务4可能有部分周期、未应用末条指令或未清尾；不能把这些当完整安全/服务PASS。若控制输入/输出/映射不变化，报告仅观察到实际闭环链路或固定档反馈，动态周期覆盖不足；不调参数制造变化或自行追加运行。

## 4. 验收及停止

1. 同一新实现离线覆盖300–900映射，实际300/750有可信连续TLS/ACK、真实相位边界、readback和独立入口账；物理缺额/额外车辆明确记失败或能力边界，E不当N。
2. 动态任务验证指令版本、应用边界和上述非零延迟；ALINEA任务必须真实E1与反馈状态可重算，至少一条真实反馈产生的新指令被实际应用，不能以初始化900、离线fake或预录900代替。无有效周期变化就不宣布该闭环run验证了变化。
3. 原9+1.1、减速、身份/车辆覆盖、每新G receiver、actual-yellow筛查、全body至实际清尾、红灯新入口、正常离网末步和EOF检查保留。碰撞/危险/覆盖UNKNOWN立即停止后续运行；未完整观测用null/partial/censor，保留所有失败和旧STOP3。
4. 达到目的或明确无法在本范围实现就停止，不机械补450/600/其他seed；交付版本化源/卡/原始与摘要/三方报告/当前状态。只判断有限技术兼容性和可行性，仍非全域长期RATE_QUALIFIED、sweet spot或正式实验。

## 5. 已批准资源与交付边界

新阶段总监控预算1200s、raw1,200,000,000B；单次≤300s/300MB、startup≤60s、free≥5GB，沿用现有watchdog口径。新总额由本次明确批准，不转入或追改旧Issue12余量。4个计划任务每项首次1次；技术故障修复不以固定启动次数STOP，任何有据重试需独立身份、完整记账和三方精确release，计入总预算，不能增加测试点/参数变体或越总额；需要扩大覆盖/资源时重新批准。

每卡绑定源/输入/参数/环境/终点，保留canonical门和UNKNOWN保守资源预留。本plan已获用户批准，仍需实际实现/离线门及每卡三方GO；范围批准本身不替代精确card的canonical release。运行流程共用开发参数仅为技术测试，不写入或冻结EXPERIMENT_PROTOCOL，不改变Stage6/A1/Candidate A既有状态，不安装新环境，不购买资源。

当前进入独立分支codex/unified-alinea-actuator的实现与离线验证；尚无新的原生诊断结果。后续GitHub任务关联按用户/Chat工作流确定，不自行编造Issue或新建PR。目标整体尚未完成，执行严格依序通过离线与精确card三方门；技术资源/覆盖扩展仍需另批。

## 6. 本次只读范围评议

- `simulation_engineer`：复用方式、周期/时钟/四任务边界无实质性工程冲突；已明确边界到达指令可当场应用。没有运行实现测试或SUMO。
- `data_analyst`：各层积分、完整/部分周期、750量化及旧900复用边界无实质性数据finding；已明确真实反馈新指令须实际应用，初值不替代闭环证据。没有重新处理raw或跑测试。
- `scientific_reviewer`：范围级条件GO，供用户批准；未发现Blocker/Major。已补检测器精确ID、全局事件窗口和ongoing覆盖，保留短闭环无档位变化的限制；此意见不是安全、服务资格或运行授权。

依据为[现有Feedback公式与状态](../../scripts/formal_development_20261007_v1/control.py)、[实际E1事件与检测器](../../scripts/formal_development_20261007_v1/v15_worker.py)、[旧900独立数据审查](../../data/processed/issue12_alinea_actuation_20261012_v1/CA_I12_PACKET_R900_S17_DIAG01/revision02/FINAL_DATA_REVIEW_V2.md)及上述D019。此次仅审查未来范围，所有新实现和运行结果仍待验证。

# PRB-010 — 同版本双侧现象证据不足与物理回溢归因边界

- 日期／阶段：2026-10-02至03，探索验证结项审查。
- 影响：高；旧城市积压与新无控主线结果不能拼成当前版本完整证据。
- 状态：当前版本探索能力缺口依D-018已CLOSED；严格连续链、U因果分解和sweet spot并未证明，不重开或重判Stage6结项。

## 发现及决定来源

旧ABC曾见R/U积压，但原RI3350、重建固定配时与后续当前版本属于不同输入/实现。用户不接受只拼旧城市证据与新无控边界的“有限范围完成”，明确要求当前版本标准metering比较；该补充验收来自后续用户要求，不能倒写成早期计划已有ALINEA必达门。[D-013–D-018](../DECISIONS.md)、[完整报告§1–2](../探索验证阶段/STAGE6_EXPLORATORY_VALIDATION_FULL_REPORT_20261003.md)。

## 最后方案与观察事实

在M3600/R900、U360/X180下，用当前OPEN/V15进行seeds17/23/42同输入配对。每组处理前600/600秒同轨，各臂4050/4050到达。三组均见M改善、R/U成本增加和共享道路R/U低速暴露。[三seed综合原报告](../../data/processed/stage6_safe_actuator_three_seed_synthesis_20261003_v1/THREE_SEED_REPORT.md)、[配对数据](../../results/tables/stage6_safe_actuator_three_seed_synthesis_20261003_v1/paired_results.csv)。

全网总system time分别增加160524/345003/266804秒，因此该V15不是已找到的sweet spot。U源等待57454/67986/70292秒必须与路内影响分开；不能把所有U损失唯一归为物理回溢。

## 阴性结果必须保留

严格meter锚定、空间连续且持续≥30秒的慢行链为0/3；S23有局部同车道R在U前的直接例子持续22秒，但22不等于30，局部不等于从meter连通城市。[链证据审查](../../data/processed/stage6_safe_actuator_three_seed_synthesis_20261003_v1/SCIENCE_CHAIN_EVIDENCE.md)。不事后降阈值、不用共享区暴露替代连续物理回溢证明。

## 最终判定与后续边界

D-018认可的是“场景能产生可研究现象且排除明显技术错误”，状态completed / preliminary_ready for formal experiment design，不是正式效果证据或参数认证。[原结项交接](../探索验证阶段/STAGE6_EXPLORATORY_CLOSEOUT_AND_FORMAL_HANDOFF_20261003.md)。S17参与开发，三个seed不是独立正式确认；11%/70/900均为探索实现值，不是Robert确认或冻结参数。

后续正式问题应研究收益与代价及可接受条件，而不是强行复现ABC或保证找到sweet spot。当前正式协议仍空未冻结，本文不改变研究决定或授权仿真。后续执行器开发另见[PRB-001](PRB-001_FIX02_SERVICE_TRACKING.md)和[PRB-004](PRB-004_NOMINAL_TWO_CAR_DISCHARGE.md)。

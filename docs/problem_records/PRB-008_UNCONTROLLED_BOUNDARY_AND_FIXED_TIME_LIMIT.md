# PRB-008 — 固定配时未保护主线与容量临界区未知

- 日期／阶段：2026-09末至10-02，重建ABC诊断→当前无控需求定位。
- 影响：高；尚不知道哪个需求点真正需要metering，不能靠配时人为构造预期故事。
- 状态：探索工作点定位子问题CLOSED；精确容量、breakdown probability与完整需求域仍未识别。

## 发现：少放R并不自动改善M

旧重建seed17中，B22使M核心速度26.964→26.572m/s、平均行程+0.266s；B28为26.964→25.376m/s、+0.721s，均未建立主线保护。[B22科学判定](../../artifacts/stage6_full_network_abc_matched_rebuild_20260926_v1/B_SCIENTIFIC_OUTCOME_REVIEW.md)、[B28科学判定](../../artifacts/stage6_moderate_rebalance_20260926_v1/B28_SCIENTIFIC_OUTCOME_REVIEW.md)。

固定绿灯释放车团是可能解释，没有被这些数据证明；早期远处M轨迹分歧和单seed也限制因果解释，不能写成已识别platoon根因。

## 指导依据与研究路线调整

Robert2026-09-30明确建议先核Merge几何、连接和实际插入，再研究uncontrolled qMain×qRamp，从临界区选点比较控制，不再用22/28秒人为建立ABC。[导师反馈记录](../SUPERVISOR_FEEDBACK.md)。原邮件本地位于docs/supervision/2026-09-30_robert_hilbrich_reply.md，私人邮件不随本文上传；反馈记录是可审查摘要。该指导不等于导师批准后续具体ALINEA参数。

## 最后实施与结果

当前版本18个唯一无控运行完成：M3600/R600–750主要轻或短扰动，M3600/R900在seeds17/23/42均长期严重，主要由Merge附近向上游发展。R750–900夹住已采样状态变化区域，足以挑控制比较点，不是精确容量值或breakdown概率。[无控原报告](../探索验证阶段/STAGE6_BOUNDARY_SEARCH_20261002_REPORT.md)。

R900实际汇入约900/904/898veh/h；M最大插入延迟58/0/65s，S17/S42出现在路内恶化后。不能把旧重建点最大约1s的departDelay描述套到此系列，或把输入积压／merge拥堵无差别混同。[全报告](../探索验证阶段/STAGE6_EXPLORATORY_VALIDATION_FULL_REPORT_20261003.md)。

下一步当时转入当前版本同需求/同seed控制比较，见[PRB-009](PRB-009_STAGE6_CONTROL_PIPELINE_AND_MEASUREMENT.md)与[PRB-010](PRB-010_CURRENT_VERSION_TRADEOFF_AND_SPILLBACK_EVIDENCE.md)。探索定位完成后不为多跑而继续网格；后续正式需求／阈值仍需明确设计。本文不新增需求或运行。

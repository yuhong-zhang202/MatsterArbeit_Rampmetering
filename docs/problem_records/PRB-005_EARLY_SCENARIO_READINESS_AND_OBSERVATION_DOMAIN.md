# PRB-005 — 早期场景未呈现目标现象与实际入口观测域

- 日期／阶段：2026-09，Stage2–6早期探索。
- 影响：高；不能确定场景能否研究主线保护与城市代价，不能直接开展正式比较。
- 状态：历史观测域技术子问题CLOSED；旧State1/EJMI科学阴性保留。后续当前版本探索能力依据D-018结项，不反改早期门。

## 发现：加需求不等于出现目标拥堵

[Stage2完成报告](../探索验证阶段/STAGE2_COMPLETION_REPORT.md)中，qMain3800/qRamp720时，两seed在1500秒前R首次下游观察均0，但M内部断面仍高流速；这说明R进入受限，不能解释成系统改善或已发现主线breakdown。Stage4的qMain3500两seed，R首次下游14/11；3650为0/0，四候选均未满足原EJMI。Stage5虽完成评估工作，Q2/Q4仍not_identified、preliminary_ready=false。[早期总结](../探索验证阶段/EXPLORATORY_VALIDATION_REPORT.md)。

## 调查与已证事实

复核12条独立早期运行发现16,622辆M实际入网点距main_up末端仅0.10–286.75m，远短于该lane1394.87m。车辆没有走过所声称的整个上游观测域，这是实际入口问题；尚不能断言它是没有主线受损的唯一原因。H2被选为最小可反驳候选，而非同时重调路权、模型和需求。[障碍诊断H2](../探索验证阶段/STAGE6_OBSTACLE_DIAGNOSIS_REPORT.md)。

后续H2把实际入口固定100m，1083/1083辆穿过登记观测域，技术覆盖修复；但当时科学specific_obstacle仍not_resolved。[技术接受包](../探索验证阶段/STAGE6_OBSTACLE_RESOLUTION_ACCEPTANCE_PACKAGE.md)。P0又区分旧独立ramp_accel edge经junction接主线与真正同edge结束加速车道，不能把文件名叫“accel”当作已验证合流语义。[P0原报告](../探索验证阶段/STAGE6_P0_MECHANISM_DIAGNOSTIC_REPORT.md)。

## 最后处置与防复发

后续重建采用两条持续主线加独立结束加速车道，约294.51m辅助段；实际换入主线与连接/插入证据另核。[Merge调查](../探索验证阶段/Stage%206%20Merge%20与车辆插入调查.md)。不同网络、实际入口和需求实现属于新系列，不替原系列“补通过”。后续需求定位与同版本标准控制见[PRB-008](PRB-008_UNCONTROLLED_BOUNDARY_AND_FIXED_TIME_LIMIT.md)及[PRB-010](PRB-010_CURRENT_VERSION_TRADEOFF_AND_SPILLBACK_EVIDENCE.md)。

经验：先确认车辆真实经过哪个观测域、实际流量及合流连接，再解释需求—状态关系。没有EJMI/State1见证不等于普遍不存在拥堵；技术修复成功也不等于科学门自动成立。本文仅回顾已审档案，无新仿真或新模型校准。

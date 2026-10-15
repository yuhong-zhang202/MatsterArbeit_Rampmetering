# PRB-009 — Stage6标准控制链路的启动、占有率、安全与服务阻碍

- 日期／阶段：2026-10-03，当前版本标准metering探索。
- 影响：高；控制端跑通不等于反馈正确、安全或实际放行合格。
- 状态：当时V15限定探索技术门已完成；前版FAIL保留，不代表后续FIX02或新执行器全域资格。

## 必须按版本记录的阻碍与处理

| 子问题 | 发现与实际影响 | 处置／已知边界 |
|---|---|---|
| TraCI与环境桥接 | V2/V3 NOOP连接/启动失败，V7 dyld失败；V12系统Python无TraCI，SUMO未启动；V13 t1日志字段未初始化 | 按精确版本修复、保留失败，不把启动未完成记为交通效果 |
| E1占有率重构不等价 | V6有173/238 lane窗超容差，反馈输入不可靠 | V8按事件驻留重构，7140观察组、238/238窗对齐；NOOP4200s/4050车与OPEN等价 |
| 直接绿转红急刹 | V8控制有10次紧急制动，其中8次红灯急停 | 安全NO-GO，不用于控制效果；不能改上限抹掉报警 |
| 安全检查通过但服务不足 | V9约1070.866veh/h请求仅实际564veh/h | rate-tracking NO-GO；不能以安全PASS冒充ALINEA效果 |
| 过严绿后界限 | V14在t653停止 | V15以真实绿后速度的前瞻界限及已审规则处理，后完成三seed探索门；不是普遍安全证明 |

以上均来自[完整报告§2.1–2.2](../探索验证阶段/STAGE6_EXPLORATORY_VALIDATION_FULL_REPORT_20261003.md)、[原执行台账](../../artifacts/stage6_standard_metering_execution_20261003_v1/EXECUTION_RECORD.md)、[可行性原注](../../data/processed/stage6_safe_actuator_feasibility_20261003_v1/FEASIBILITY_NOTE.md)。表内不同版本不是独立可合并重复，也不是同一causal effect。

## 最后方案、证据与经验

先验证全绿NOOP不改变交通，再验证检测器重构，继而验证实际安全和放行，最后才开展OPEN/V15配对。V15各seed独立gate：[S17](../../data/processed/stage6_safe_actuator_v15_audit_20261003_v1/S17_GATE_REVIEW.md)、[S23](../../data/processed/stage6_safe_actuator_s23_v15_audit_20261003_v1/S23_GATE_REVIEW.md)、[S42](../../data/processed/stage6_safe_actuator_s42_v15_audit_20261003_v1/S42_GATE_REVIEW.md)。

计数纠正：全报告明确32是**登记启动尝试**，不是32个SUMO进程；V12没有启动SUMO。部分历史handoff的physical starts用词过宽，引用时采用全报告准确口径，不静默覆盖其历史原文。

后来的FIX02 71/72服务窗FAIL属于另一开发系列，[PRB-001](PRB-001_FIX02_SERVICE_TRACKING.md)；2026-10-15新154源动态与短真实闭环属于[PRB-004](PRB-004_NOMINAL_TWO_CAR_DISCHARGE.md)。后者成功不追改V8/V9失败，也不把前者阴性迁移成V15探索未完成。最终目标现象结项边界见[PRB-010](PRB-010_CURRENT_VERSION_TRADEOFF_AND_SPILLBACK_EVIDENCE.md)。

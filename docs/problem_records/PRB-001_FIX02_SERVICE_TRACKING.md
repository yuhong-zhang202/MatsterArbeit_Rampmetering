# PRB-001 — FIX02 指令与实际服务脱节

- **日期／阶段：**2026-10-07；正式实验前开发试跑。
- **现象：**12个FIX02控制运行整体NOT_QUALIFIED；[1200,3000)的72个持续供给300s窗口，71 FAIL、1 PASS。唯一PASS为R750/S23/T1的[2100,2400)，指令46.5298辆、实际43辆、误差7.586%。原10%标准是工程服务标准，不是sweet-spot阈值。
- **证据与版本：**[开发总结§6](../development/DEVELOPMENT_TRIAL_SUMMARY_20261007.md)、[逐窗口原表](../../results/tables/formal_development_20261007_v1/service_windows_fix02_final.csv)、[最终科学审查](../../artifacts/formal_development_20261007_v1/FINAL_SCIENTIFIC_REVIEW.md)。FIX02与修复前控制分开；历史OPEN复用不冒充新增独立运行。
- **科研影响：**数据、观测安全和反馈／队列规则通过，不等于实际服务合格。不能把指令强度当成实际处理强度。R900控制到4200s仍有残留，成本是截断成本；未建立sweet spot，也未唯一识别全部U损失的物理回溢原因。
- **根因：**服务缺额已确认；各接收拒绝、安全限制和执行映射的贡献不能由拒绝秒数直接等同丢失车辆数，未得到唯一因果分解。
- **采取的方案及效果：**保留全部72窗口和失败；[Issue #2调查](https://github.com/yuhong-zhang202/MatsterArbeit_Rampmetering/issues/2)与[PR #3](https://github.com/yuhong-zhang202/MatsterArbeit_Rampmetering/pull/3)转向独立执行器调查。开发覆盖交付完成，服务问题仍未关闭。
- **最终状态／停止条件：**OPEN。未取得可审查的目标率—实际率资格前，不能宣称正式控制比较就绪；不删除受阻窗口制造达标。
- **下一链接：**[Issue #12](https://github.com/yuhong-zhang202/MatsterArbeit_Rampmetering/issues/12)，文献驱动执行政策与最小资格准备；尚未由本记录选择政策或批准新运行。

**主要来源快照 SHA-256：** `8d09c930b33ea49573134ab114435df6f47f73a3e167efbaef75565b816fcdb0`（DEVELOPMENT_TRIAL_SUMMARY_20261007.md；归档时校验，不替代该报告引用的原始证据）。

---

2026-10-15补记：原FIX02的71/72失败及整体NOT_QUALIFIED保持。后续累计执行器已有有限动态／同源真实ALINEA节点完成证据，详见[PRB-004](PRB-004_NOMINAL_TWO_CAR_DISCHARGE.md)，不反改原系列或替代全域服务资格。

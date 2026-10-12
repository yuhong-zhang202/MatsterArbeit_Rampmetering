# PRB-004 — 名义双车映射未获实际放行支持

- **日期／阶段：**2026-10-12；两个已完成单seed原生三周期诊断的只读原因分析。
- **现象：**WAIT_DIAG01_V2和WAIT_BUDGET_W360_01各72s内C=applied C=E6、N3；三个唯一入口R0／R1／R2都在G，每周期1辆，真实y／r过线0。两run相关轨迹相同，不是六个独立重复。
- **证据与版本：**[最小原因报告](../development/CANDIDATE_A_NATIVE_DISCHARGE_CAUSE_20261012.md)、[六周期小表](../../data/processed/candidate_a_native_discharge_cause_20261012_v1/SIX_CYCLE_SUMMARY_V1.csv)、[输入映射](../../data/processed/candidate_a_native_discharge_cause_20261012_v1/SOURCE_MAPPING_V1.json)、[科学限定复核](../../artifacts/candidate_a_native_discharge_cause_20261012_v1/FINAL_SCIENTIFIC_REVIEW_V1.md)。名义300veh/h不是R需求：本run需求M3600/R900/U360/X180、seed17、dt1、G3/y3/r18。
- **科研影响：**72s描述平均150veh/h不是稳定长期容量；E−N=3不能改E或计数消除。nominal_n=2明确UNQUALIFIED_DISCHARGE_ASSUMPTION，24s=3600×2/300只是映射，不是实测资格。
- **根因：**已观测次车起始静止、距线约8.502m、首G秒不动；三个周期3s绿末还差5.008／4.351／2.993m，后在黄灯逼近并停车，R1／R2下一绿灯才过线。支持排队起步／跟驰占用短G的解释；未记录getStopSpeed、有效模型ID或最终内部决策，不能唯一归因某native分支／tau。未发现N硬限一辆、丢计数或WAIT设车速；首黄秒旧接收已可用，不支持持续下游阻塞唯一解释。
- **采取的方案及效果：**仅提取既有轨迹、核对FCD／TLS／ACK及原入口计数；原E6/N3、失败和模型／相位不改。未新增SUMO。对300单点延长G仅旧报告建议，不是已验证解决方案；n2/y3/最低r2在900对应8s周期，不能全局加G便假定300–900可达。
- **最终状态／停止条件：**OPEN。未证明当前执行政策实现ALINEA目标率，Candidate A仍NOT_QUALIFIED；先完成文献与执行域检查，不因想要N2而改写数据或研究设计。
- **下一链接：**[Issue #12](https://github.com/yuhong-zhang202/MatsterArbeit_Rampmetering/issues/12)负责文献驱动政策选择及有界工程验证；当前尚未选择新政策、实现或启动。Stage6既有结项不重开，正式协议仍未冻结。

**主要来源快照 SHA-256：** `8d35a75645acc9234970f86e2fbec8b14dec3f94dbdbfc5124956870263eda91`（CANDIDATE_A_NATIVE_DISCHARGE_CAUSE_20261012.md；归档时校验，不替代该报告引用的原始证据）。

## 2026-10-12 Issue12 有界后续证据

旧G3/E6/N3结果保持。新fixed24/FIX300实测每周期G4/Y5/red15两辆、三个周期C=E=N6；旧helper duration FAIL及修复保留。900长G6前缀被原9+1.1 current-gap合同拒绝（N2/C1.5/E0），没有证据证明900物理不可达。后续只改phase的两车包T8/Gmax4/Y2/red2单次1272诊断，九周期实际各2辆，C=appliedC=E=N18；原硬检查不放宽，未重试。数据/科学postreview尚待完成，当前状态限定MITIGATED而非全域资格CLOSED。450/600/750、长窗/多seed/连续ALINEA仍未验证。参见[完整交付](../development/ISSUE12_EXECUTION_POLICY_DELIVERY_20261012.md)。

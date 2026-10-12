# PRB-002 — 旧 STOP3 与当前接口 A1 证明缺口

- **日期／阶段：**2026-10-08至11；Candidate A 技术资格与离线可行性调查。
- **现象：**A07完成至1206s；旧prospective-red guard拒绝1206→1207。R_flow.1距线1.001999m、速度0.045738m/s；旧条件需求1.145971m、余量−0.143971m。被拒绝的红灯运动步未执行。
- **证据与版本：**[A07工程原报告](../../artifacts/candidate_a_qualification_20261008_v1/engineering/R300_A07_RUNTIME_ENGINEERING_REPORT.md)、[安全责任重评](../development/CANDIDATE_A_SAFETY_CONTRACT_REASSESSMENT.md)、[A1三态合同](../development/CANDIDATE_A_A1_ELIGIBILITY_CONTRACT.md)、[Issue #10有界可行性报告](../development/CANDIDATE_A_A1_PROOF_GAP_FEASIBILITY.md)。Issue #10基线为PR #9的7ce8f5e19d737117dc6f25165993fc436244c599；SUMO 1.26固定源码依据在原报告中。
- **科研影响：**STOP3只证明自定义合同拒绝，不能改写成SUMO原生红灯不安全、Candidate A物理不可行或900不可能。A07仅6s控制前缀；完全未观测窗口保持null，部分观测不作完整rate qualification。450/600/750/900四档未测试。
- **根因：**拒绝谓词可重现；其作为完整原生安全证明的充分性未证。公开接口未暴露下一步完整DriveProcessItems计划、未来预约和最终速度联合分支；单项getter或离线PASS不能补齐完整证明。
- **采取的方案及效果：**[Issue #6](https://github.com/yuhong-zhang202/MatsterArbeit_Rampmetering/issues/6)、[#8](https://github.com/yuhong-zhang202/MatsterArbeit_Rampmetering/issues/8)、[#10](https://github.com/yuhong-zhang202/MatsterArbeit_Rampmetering/issues/10)及[PR #11](https://github.com/yuhong-zhang202/MatsterArbeit_Rampmetering/pull/11)限定调查，得到Proposed STOP_A1_UNDER_CURRENT_INTERFACE；未改SUMO核心、模型或生产guard。历史表示缺陷的修正／失败／复审仍在各原报告，不另拆成问题记录。
- **最终状态／停止条件：**NO-GO，仅指当前接口下继续扩展完整A1证明的调查建议，非普遍安全结论或新研究决定。A1仍UNRESOLVED；旧STOP3和Candidate A NOT_QUALIFIED保留。
- **下一链接：**后续独立原生WAIT诊断见[PRB-003](PRB-003_RECEIVER_WAIT_AND_BUDGET.md)；它没有追溯解除A1证明缺口。[Issue #12](https://github.com/yuhong-zhang202/MatsterArbeit_Rampmetering/issues/12)转向工程资格准备。

**主要来源快照 SHA-256：** `39ecbf80524c4f8cea446b2b93d715dfdb42fee1de8110e884436fdd0714a4fd`（CANDIDATE_A_SAFETY_CONTRACT_REASSESSMENT.md；归档时校验，不替代该报告引用的原始证据）。

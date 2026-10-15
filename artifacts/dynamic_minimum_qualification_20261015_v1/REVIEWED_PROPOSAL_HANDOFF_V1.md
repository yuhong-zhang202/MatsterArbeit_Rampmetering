# 动态执行器最小资格：已审提案与待批准内容

2026-10-15。**送审方案完成；新的动态资格尚未建立，未新运行SUMO。**

1.1m源自V9停车线几何/停车包络裕量，经V10扩展到接收间距，后来被WAIT合同明确保留。代码符合该合同，未找到将它视为SUMO官方额外必要距离的依据；不能把原失败改判计算错误。

**推荐的唯一最小改动提案：** 只在运动中的当前跟驰检查中，以同参数getSecureGap查询值保留硬筛查，额外1.1m继续计算并记录为advisory。新绿灯的严格prospective准入、模型/模式、完整覆盖、接收空间、黄灯、实际入口前后、制动、碰撞/teleport、红灯、车尾及UNKNOWN停止保留。该提案改变现行停止合同，尚未批准或实现；不是官方安全认证。具体代码逻辑草案见工程报告。

动态测试仍为原需求/seed17/dt1/1200–1296，指令300→750→900→300。必须有四指令实际应用与延迟证据、连续信号/周期一致、完整周期实测N2、独立原请求C和真实N、残差分解及降回300后的欠额恢复。解释得通或程序结束不能单独通过，终点差额不要求零，partial/pending/censor/null保留。动态未通过则不启动ALINEA；通过后才一次同一冻结执行器的短真实E1/Feedback闭环，并再次直接核C/N。

最多拟议2次、各300监控秒/60启动秒、无固定输出字节门、至少5GB余量、终点1296；最多600新增监控秒尚待批准。旧147.815秒与失败另账保留。不会机械补档位矩阵或按本次2.8cm缺额调阈值；遇无法解决的真实约束则交付限制与替代方案，停止无效重试。

## 审查与证据

- [完整方案](../../docs/development/DYNAMIC_ACTUATOR_MINIMUM_QUALIFICATION_PLAN_20261015.md)，原文SHA8890116e…冻结保持。
- [误差与验收补充](MEASUREMENT_REVIEW_RESOLUTION_V1.md)，明确请求变化、周期选择与实放缺额，不以解释替代实际恢复。
- [工程溯源和具体改动草案](engineering/GAP_MARGIN_MINIMUM_TREATMENT_V1.md)，SHA69e48475…；未实现、未测试新合同。
- [数据/日志审查](../../data/processed/dynamic_minimum_qualification_20261015_v1/DATA_MEASUREMENT_AND_LOGGING_REVIEW_V1.md)，SHAaa312bce…；原日志修复已有限验证，未来reader兼容修复尚待实施。
- [科学提案审查](SCIENCE_PROPOSED_CONTRACT_REVIEW_V1.md)：GO_FOR_PROPOSED_BOUNDED_DIAGNOSTIC_CONTRACT_REVIEW_ONLY，无阻碍送审的实质finding。
- [旧动态最终数据报告](../../data/processed/cumulative_full_catalogue_followup_20261014_v1/native_dynamic_v3/DATA_BOUNDED_DYNAMIC_POSTREVIEW_V1.md)、[其科学后审](SCIENCE_HISTORICAL_DYNAMIC_POSTREVIEW_V1.md)：C169/24,N5,C−N49/24；规则STOP与缺两条rawACK的UNKNOWN保持。

后续必须先明确批准上述合同变更/实施范围；新仿真另须明确授权，可在批准时一次性写明“离线三方与精确版本/卡门通过后一次动态，成功后一次ALINEA”的条件顺序。当前没有新card/auth/release或新SUMO。正式协议、Stage6、A1及Candidate A总体资格不由本提案改变。

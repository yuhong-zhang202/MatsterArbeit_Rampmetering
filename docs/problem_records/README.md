# 项目问题与解决经验索引

更新：2026-10-15。这里记录**已经在权威文档中查到的主要阻碍**：如何发现、依据、处置、实际效果及未解决边界。不是所有聊天或小Reviewer缺陷的流水账，也不声称穷尽全部历史。Stage1尚未发现需单独归档的独立阻碍，不自行补造。

现状以[PROJECT_STATE](../PROJECT_STATE.md)为准；批准依据看DECISIONS，原始结果／失败保持原路径。这里不替代Issue／PR、阶段验收或正式协议。CLOSED只关闭明确限定的历史技术子问题；MITIGATED仅表示限定范围缓解；NO-GO为指定路线建议，不代表物理不可能；OPEN仍未解决。分级不是Reviewer P等级。

## 当前优先阅读

- **执行器放行不足的完整过程：**[PRB-004](PRB-004_NOMINAL_TWO_CAR_DISCHARGE.md)，含发现、轨迹调查、文献取得层次、方案演变、原始C／实际N、当前有限成果和限制。2026-10-15最小动态＋同源短真实ALINEA节点完成待审，长期／全域资格仍未证明。
- **探索阶段为何多次受阻及如何收口：**PRB-005至010按独立主题记录。原RI3350、重建ABC、当前OPEN/V15和后续FIX02／新执行器不得混成同一因果效果。
- [Draft PR #13](https://github.com/yuhong-zhang202/MatsterArbeit_Rampmetering/pull/13)为当前工程审查交付；不合并、不代用户验收或自动授权下一轮。

| ID／问题 | 日期／阶段 | 影响 | 当前归档状态 | 已证原因／处置与剩余边界 | 后续研究是否仍受约束 |
|---|---|---|---|---|---|
| [PRB-001 FIX02服务跟踪](PRB-001_FIX02_SERVICE_TRACKING.md) | 10-07开发 | 高 | OPEN（原系列） | 72服务窗71FAIL；拒绝秒数不是唯一缺额因果分解；新短诊断不反改旧结果 | 是，不能用FIX02宣称完整服务合格 |
| [PRB-002 STOP3／A1证明缺口](PRB-002_STOP3_A1_PROOF_GAP.md) | 10-08～11离线/技术 | 高 | NO-GO（当前接口完备证明路线建议） | 原guard拒绝可重现；原生未来联合状态不足，A1仍UNRESOLVED | 是，不能把原生相位观察写成A1证明 |
| [PRB-003 receiver WAIT／预算](PRB-003_RECEIVER_WAIT_AND_BUDGET.md) | 10-12诊断 | 中 | MITIGATED；预算子问题CLOSED | 分清假设推进和实际等待；300/360完成，420/480跳过，不能称绝对最优 | 原局部问题缓解，不保证未来供给／服务 |
| [PRB-004 放行不足与原始ALINEA累计跟踪](PRB-004_NOMINAL_TWO_CAR_DISCHARGE.md) | 10-12～15开发 | 高 | 旧短技术节点MITIGATED；自然条件NOT_QUALIFIED | run02首黄−4.501旧STOP保留；S1–S6验收标准与隔离实现准备中，新合同/尺度/运行待批 | 是，真实C/N精度与安全资格未建立；方法见PRB-004末节 |
| [PRB-005 早期目标现象与实际入口域](PRB-005_EARLY_SCENARIO_READINESS_AND_OBSERVATION_DOMAIN.md) | 09月Stage2–6 | 高 | 观测域技术子问题CLOSED；旧科学阴性保留 | 车辆实际近合流入网，H2覆盖修复不自动通过State1；重建网络独立归档 | 精确容量/真实校准未建立 |
| [PRB-006 分析假通过与T54证据资格](PRB-006_ANALYSIS_VALIDITY_AND_T54_HANDOFF.md) | 09-13复审 | 高 | 限定处理缺陷CLOSED | 四类坏输入、证据映射和5缺配对键修复；不追认T54用户接受 | 未来输入仍须资格检查 |
| [PRB-007 原RI3350不可配对](PRB-007_RI3350_INPUT_PAIRABILITY.md) | 09-26原系列 | 高 | 历史比较排除处置CLOSED | 动态请求与复制输出不是同输入；NOT_PAIRABLE/A_NOT_EVALUABLE保留 | 原系列不能用于A因果效果 |
| [PRB-008 固定配时失败与需求临界区未知](PRB-008_UNCONTROLLED_BOUNDARY_AND_FIXED_TIME_LIMIT.md) | 09末～10-02 | 高 | 探索工作点定位CLOSED | B22/B28无主线保护；Robert指导转无控定位，18次无控运行夹住已采样变化区 | 非精确容量或概率，不强造ABC |
| [PRB-009 控制启动／检测器／安全／服务链](PRB-009_STAGE6_CONTROL_PIPELINE_AND_MEASUREMENT.md) | 10-03 Stage6 | 高 | V15限定探索门完成；历史FAIL保留 | TraCI/173窗占有率/V8急刹/V9服务不足分版处理；32为启动尝试非SUMO进程 | 不转移成FIX02或新执行器全资格 |
| [PRB-010 同版本trade-off／回溢证据](PRB-010_CURRENT_VERSION_TRADEOFF_AND_SPILLBACK_EVIDENCE.md) | 10-02～03结项 | 高 | 探索能力缺口依D-018 CLOSED | 同版M改善/RU代价；严格≥30s链0/3、总成本增加，阴性保留 | sweet spot、U唯一物理回溢归因未证明 |

## 阅读与更新规则

每个独立问题沿固定字段追加：现象→证据和版本→科研影响→根因已知／未知→措施和实际效果→限定状态／停止条件→下一链接。小日志或表示缺陷并入主问题，不新增一串文件。重要版本变化保留时间线，不用新成功覆盖旧FAIL、null、部分周期或未运行。

本次基于Stage2完成、Stage3–5复审、Stage6障碍/P0/配对/无控边界/权威全报告及已审开发系列补档；未重新解析raw或运行SUMO。未找到可直接支持“曾只测lane0而漏掉全车道且已修复”的原始bug报告，暂不把该说法当已证根因；已证入口覆盖、测量合同和E1重构分别记录。T54直接批准若无源则未知，不由D-018替代。

完整raw只在本地原目录，GitHub为文档、派生审计、卡片和文件级哈希；本目录相对链接优先于旧docs/stage6路径。Stage6既有结项、Candidate A NOT_QUALIFIED、A1 UNRESOLVED与空未冻结正式协议保持。**下一步建议不构成执行授权。**

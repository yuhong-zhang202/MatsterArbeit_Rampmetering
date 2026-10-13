# 原始 ALINEA 请求累计跟踪：最小离线实现

> 当前更新：用户随后批准的一次原生运行已执行，1272秒按黄灯UNKNOWN停止；工程、数据、科学复审完成。见[原生结果与后续边界](CUMULATIVE_TRACKING_NATIVE_REPORT_20261014.md)。以下保留运行前的离线交付说明，不作为当前执行状态。

2026-10-14。当前状态：最小离线实现及工程→数据→科学审查完成，`GO_FOR_OFFLINE_REVIEW_PACKAGE_ONLY`，交用户审查。尚无累计版本的SUMO结果，不能宣称长期跟踪已经解决；停止追加离线检查。

## 目标及已确认的起点

用户明确要求实际放行长期平均跟上原始 ALINEA 请求。此前新03固定750诊断的七个完整周期 E=N=14，证明该样本的物理欠放消除；70秒14辆仍为720辆/小时，比原始750请求低4%。这两个问题应分别核账。[03实际报告](T10_G5_Y3_NATIVE_CONTINUATION_REPORT_20261013.md)

新实现依据已审[累计补偿设计V2](CUMULATIVE_DISCHARGE_TRACKING_DESIGN_20261014_V2.md)，保留限幅后、量化前的原请求及真实累计过线N。每个完整周期边界根据C−N选择下一包，预测只参与选择；真实首G的ACK才确认应用。完整周期N不等于2或观测未知时停止调查，不把能力不足变成无限追债。

初始目录只有T8=G4/Y2/R2及T10=Gmax5/Y3/Rmin2；满额提前关绿时补足红灯，保持周期总长。900档、车辆模型及安全规则不变。750在每完整包实际两辆、无准入延期等条件下可采用10/10/8/10/10秒，48秒10辆；这是有条件的调度算术，不是新的实测结果。

## 改动与核账边界

实现隔离在 `src/candidate_a_cumulative_tracking_20261014/`，旧源和原始数据不改。新接口复用原Command、E1、Feedback及Candidate A安全/日志桥接；周期对象携带Gmax、黄灯和红灯约束。Feedback的公式、原请求previous状态与30秒更新周期保持。

独立reader位于 `scripts/cumulative_tracking_audit_20261014_v1/`。旧reader按每条请求独立取最近档反推周期，不能直接用于新调度；新reader需从请求真实时刻、边界决策、实际TLS/ACK和crossings独立复算。`C_nearest_reference`仅为旧算法对照，不是新政策的应用量。C−E、E−N、C−N分别保留，部分观测、完全未观测与实测零不得混用。

## 本轮验证与下一门

工程V4实际执行四个测试方法，4/4通过，51.608秒：[日志](../../artifacts/cumulative_tracking_implementation_20261014_v1/engineering/offline_v4/ACTUAL_TEST_LOG.txt)。覆盖精确累计选择与500个完整假设包、动态请求及未应用状态、真实XML/helper的混合相位接线、真实Feedback接口及无授权拒绝。该次测试是在提交前源码快照上执行；最终交付须绑定相关文件字节，不冒称测试了后来生成的提交。

合成固定750桥接记录在1296秒结束，C=E=N=20；真实Feedback接口合成记录包含1230、1260、1290三次更新，最后一个未应用请求保持null；独立G5截止样例保留E=2/N=1并拒绝下一包。所有车辆运动均由假接口提供，尤其T8样例在首G秒放入两辆，不能用于证明真实车辆加速、跟驰或容量。[合成fixture目录](../../artifacts/cumulative_tracking_implementation_20261014_v1/engineering/offline_v4/fixtures/)

V1/V2的接收空间拒绝及前像仍保留：问题在假车辆移动时序，不通过放宽实际接收检查来消除失败。V3已通过；V4补入每包实际ACK事件和第三次Feedback时钟后完成对应检查。工程失败、源前像和卡片修订保存于 `artifacts/cumulative_tracking_implementation_20261014_v1/engineering/`。

独立审计最终四个方法在最终源码上一次全通过，0.859秒：[最终日志](../../data/processed/cumulative_tracking_implementation_20261014_v1/offline_final_v1/TEST_LOG_FINAL_V1.txt)。它不调用受测Ledger作为真值，重算请求积分、全部过线计数、每包首G应用、连续相位与三个Feedback窗口。新reader补齐显式null与缺字段的区别；V1暖机ACK截取、V2假数据识别、V3零计数与quota关绿不一致的测试失败均保留。零/额外过线的变异样例验证账本和审计层，不是完整FCD或原生交通重放。

工程最终核查通过：[报告V3](../../artifacts/cumulative_tracking_implementation_20261014_v1/engineering/freeze_v2/ENGINEERING_FINAL_REVIEW_V3.md)。独立数据终审给出 `GO_FOR_OFFLINE_REVIEW_PACKAGE`：[数据报告V1](../../data/processed/cumulative_tracking_implementation_20261014_v1/final_review_v1/FINAL_DATA_REVIEW_V1.md)。175个工程绑定文件、111个源文件及当前卡精确匹配；数据binder SHA-256为 `1c1db661927f60869d4c97cda9be6243a5514e14a1c3bbc125f052b000eff5bf`。只读[科学终审](../../artifacts/cumulative_tracking_implementation_20261014_v1/science/SCIENTIFIC_FINAL_REVIEW_V1.md)给出限定GO，无未解决Blocker、Major或实质性Minor；不构成运行许可或安全/服务资格。

本轮未运行新的干净checkout测试或完整原生actual流水线；实际验证范围以上述源码快照和合成日志为准。暂存差异检查保留了哈希绑定日志/前像及 `_phase.py` 末尾空行的格式提示（exit2），没有为格式改写证据或重制卡，也不把它写成全项PASS。[提交前读回](../../artifacts/cumulative_tracking_implementation_20261014_v1/DELIVERY_READBACK_V1.json)

## 唯一当前待审卡

- 身份：`UA_CUMULATIVE750_S17_01`。
- [卡片 packages_v5/card.json](../../artifacts/cumulative_tracking_implementation_20261014_v1/engineering/packages_v5/UA_CUMULATIVE750_S17_01/card.json)。SHA-256：`c4464cd13b64a2eed0e9ea6143b16cac308562608426d6adc3023fa6b4b3fc3b`。
- 111个绑定源文件摘要：`b351723aac24e5938ebd608be8b567a1d5d6e3527d22fc564049b4d8b306067b`。
- 状态：`PREPARED_NOT_RELEASED`。无授权执行在导入执行器或创建raw前拒绝；旧packages/v2/v3/v4保留且不是当前有效卡。
- 卡内 `audit_contract.reader` 仍为null，状态仍是生成时的待适配文字；不能声称该字段已填写。四个reader文件已精确纳入111源绑定。实际release门另外强制新审计路径及SHA；未来必须绑定本轮最终数据审查及新actual reader，旧reader不能凭此卡放行。保留这项元数据限制，不为改文字再次生成卡或重复桥接测试。
- 测试后动作、账本、Adapter、Producer、CLI及测试字节未变；profile另做最终reader绑定和包版本更新，执行了该卡的prepare/静态环境/validate/缺许可拒绝核查，没有把这些检查写成重跑四项桥接测试。旧binder中的历史live路径漂移有对应源码前像，不假称旧卡绑定当前字节。

仅离线核卡命令（工程已经执行；不是SUMO启动命令）：

```sh
.venv/bin/python -B scripts/candidate_a_cumulative_tracking_20261014_v1/cli.py --check-card artifacts/cumulative_tracking_implementation_20261014_v1/engineering/packages_v5/UA_CUMULATIVE750_S17_01/card.json
```

新身份 `UA_CUMULATIVE750_S17_01` 的1296秒终点用于拟议的两组48秒机制检查；它不继承旧03的执行许可。这里750是放行请求，需求仍为M3600/R900/U360/X180、seed17、dt=1秒。当前没有新canonical release或SUMO运行。300秒监控、无固定输出字节门、60秒启动和5GB剩余空间为待审资源设置，既有约177秒/425MB仅是规划依据，不是未来上界。

## 尚未完成的完整目标

T8/T10只覆盖名义720–900；低请求需明确UNSUPPORTED。原T8…T24库可作为300–900后续接线基础，但配置存在不等于实际服务通过。新同版本混合周期、动态请求、真实闭环及持续实际能力仍待检验，不能拼接旧T8、T10和T24不同版本的结果宣布合格。[完整要求](ALINEA_TRACKING_GOAL_REQUIREMENTS_20261014_V2.md)

Stage6既有结项、Candidate A NOT_QUALIFIED、A1 UNRESOLVED和空且未冻结的正式协议保持。本轮没有更改科研设计、安全合同或正式参数；下一步建议不构成正式实验授权。

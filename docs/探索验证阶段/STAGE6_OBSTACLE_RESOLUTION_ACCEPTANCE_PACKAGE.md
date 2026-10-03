# Stage 6 SG6-R 障碍解决验收包

日期：2026-09-13  
候选状态：**`not_resolved`**  
结论置信度：**High，仅限预登记的有限验证与停止判断。**

**Astra复审补充（2026-09-13）：** 旧卡停止与`not_resolved`候选保留，但不据此宣告项目不可行。后续路线见 [Astra复审与解决方案](STAGE6_ASTRA_REASSESSMENT_AND_RECOVERY_PLAN.md)：先离线核合流语义、实际R送达和局部主线响应，再决定新候选；不必暂停所有诊断等待Robert。旧数值回执/规则保持不变。

## 验收结论

本轮 H2 改动成功修复了工程观测问题：主线车辆实际从100 m位置进入，1083/1083辆均穿越feeder和common观测域，真实运行、检测器、TLS及数据链可用。但该场景没有通过预登记的双侧研究适用性门，因此 `specific_obstacle` 没有解决，正式实验设计不能解锁。

D2的seed17配对是完整且合格的科学阴性，不是缺文件、解析错误或技术失败。按事先批准的停止规则，seed23已取消，不能使用剩余预算继续寻找阳性。

## 实际运行与预算

| 项目 | 结果 |
| --- | ---: |
| SUMO启动 | 4/6 |
| 技术smoke | 2次，其中attempt1技术失败、attempt2通过 |
| validation | 2/4：ML17、C17 |
| 技术retry | 1/1，已耗尽 |
| 预算墙钟 | 38.306105/720 s |
| 预算归档 | 223,178,564/12,000,000,000 B |
| netconvert / TraCI / GUI | 0 / 0 / 0 |
| seed23 | `cancelled_by_stop_rule / not_evaluated` |

## 核心结果

- 74项seed17必需主规则：69通过、5项合格阴性、0缺失。
- 未通过项：`M_PRIMARY`、`M_SUPPORT`、`R_SUPPORT`、`S_RU_EXPOSURE`、`Q4_COEXIST`。
- 7项预登记敏感性：0通过、7项均为 `not_resolved`。
- ML主线保守旅行时间区间为 `[31.9320, 33.9342] s`；C为 `[33.1427, 35.1517] s`。注册的10%保守受损门未通过；这些为测量边界，不是统计置信区间，不能断言真实差异小于10%。
- 没有连续三个60秒时间箱满足主线速度比不高于0.95，因此不存在注册的M/R/RU共同支持块。
- 两个条件全时域均观察到300次R通行，也观察到共享区R/U共暴露。联合规则失败不能写成“匝道没有车辆通过”或“城市侧没有暴露”。
- ML参考资格通过：半窗变化约1.5802%，CV约2.2199%；这不等于证明不存在额外插入等待。

## RG1–RG8

| 门 | 状态 | 判断 |
| --- | --- | --- |
| RG1 来源和技术完整 | Passed | 来源、端点、覆盖及独立复算完整，数据缺陷0 |
| RG2 真实观察域 | Passed | H2恢复了M真实入口和feeder/common覆盖；R/U域也有记录 |
| RG3 主线受损 | **Failed** | TT主门和连续速度支持均未通过 |
| RG4 R/城市证据 | **Failed** | 原始R和R/U现象存在，但登记的最低联合支持未通过 |
| RG5 双侧关联 | **Failed** | Q2/Q4及共同支持块未成立 |
| RG6 随机性和时域边界 | **Failed by stop** | seed17阴性触发预登记停止；seed23必须保留为未评估 |
| RG7 独立科学复审 | Passed | 工程、数据与科学复核完成，开放B/M/m为0/0/0 |
| RG8 用户接受resolved | Not applicable | RG3–RG6失败，不能请求接受为resolved |

## 可接受的状态记录

接受本包只表示同意按 `not_resolved` 收口本次候选，承认结果有效并停止追加运行。它不表示同意降低阈值、推翻Stage3/5、改变研究方向或开始正式实验。

下一步建议按Astra复审方案完成有限离线机制诊断，形成具体候选后使用 [STAGE6_ROBERT_OBSTACLE_BRIEF.md](STAGE6_ROBERT_OBSTACLE_BRIEF.md) 与Robert讨论场景选择。可以现在咨询；不将等待回复设为全部离线诊断的前提。发送材料仍需用户明确授权；收到真实反馈前不更新 `SUPERVISOR_FEEDBACK.md`。

## 证据绑定

- D2工程清单：`48aa1578226ed5c983d0d06ff565381d65f95f487bfc404cfc7bb562665ea148`
- D2数据回执：`ae2fc3a1bdf596a106358b36eb69098a7b84473272c97b5fd665f7cf82f9c2b5`
- D2数据清单：`92b415ca8152557fb4d483f1ac16cc8f8c9640e7b122867140c5d7da9620c7f3`
- 科学裁决：`data/processed/stage6_obstacle_20260913_v1/d2_scientific_first_pair_decision_revision_01.json`
- 逐规则结果：`data/processed/stage6_obstacle_20260913_v1/d2_data_review_revision_01/registered_fixed_rule_tables/resolution_rule_results.csv`
- RG汇总：`data/processed/stage6_obstacle_20260913_v1/d2_data_review_revision_01/resolution_gate.csv`

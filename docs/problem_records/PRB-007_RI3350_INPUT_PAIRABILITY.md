# PRB-007 — 原始RI3350 R0/A输入不可配对

- 日期／阶段：2026-09-26，原始RI3350全网对照审计。
- 影响：高；不能把A与R0差异归因于匝道处理。
- 状态：历史比较排除处置CLOSED；原R0/A仍NOT_PAIRABLE，A仍A_NOT_EVALUABLE，未被修复为有效效果对照。

## 如何发现

原A中U有57/150辆未插入，其中19辆在R启用前已发生；M FCD从t12就分歧。若研究处理尚未启用，其他流已不同，单凭同seed不能证明公平对照。[原始配对重审更正](../../artifacts/stage6_full_network_abc_phenomenon_validation_plan_20260926_v1/A_launch_package/PAIRABILITY_REAUDIT_CORRECTION_20260926.md)。

## 根因：不能将输出复制成“相同请求”

R0用best/max/last动态出发请求，A把R0输出的实际lane/position/speed复制为固定数值输入，两者不是同一外生请求。U_flow.1以固定14.0817m/s出发被SUMO拒绝是至少一项插入失败的直接证据；其余M/X差异的完整随机机制仍未知，不能从此例推导全部原因。

## 处置与最后方案

保留原raw、更正错误比较状态，原结果只作输入/插入诊断；不通过删未入网车辆或只比到达车辆挽救A效果。后续建立独立重建配对系列，使用显式逐车输入和处理前轨迹同一性审计。[重建A阶段配对审查](../../artifacts/stage6_full_network_abc_matched_rebuild_20260926_v1/A_PHASE1_PAIRABILITY_REVIEW.md)。

必须分开原RI3350、后续V2 A/B22/B28及当前OPEN/V15。原系列不可配对不自动传染到重建系列，后续成功也不追溯解除原失败。[权威全报告§2](../探索验证阶段/STAGE6_EXPLORATORY_VALIDATION_FULL_REPORT_20261003.md)。

防复发：逐车核实请求属性与处理前共同轨迹；分开planned、departed、arrived、source waiting和路内残留。输出相等不等于请求相等，同seed也不保证改动后随机分支一致。未获公平性证据前不能开展因果效果解释。

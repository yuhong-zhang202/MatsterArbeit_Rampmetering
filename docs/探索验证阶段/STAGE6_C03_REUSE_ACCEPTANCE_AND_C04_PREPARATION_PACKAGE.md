# Stage 6 C03：既有网络复用验收与 C04 准备授权包

日期：2026-09-13  
状态：**C03 static reuse PASS；等待用户授权 C04/SG6-P 的离线准备工作**

## C03 结论

H2 只改变 M 的插入位置，不改变网络拓扑。因此 C03 不需要调用 netconvert，可以复用已有编译网络：

- 来源：`artifacts/stage2_completion_20260909_v1/runtime_archive/C17_reused/network.net.xml`
- byte SHA-256：`a83bb0c3a03b7e74cf8c2360336eb0dfbb330073cf8b8f6aea9940ff7cf3d8ea`
- semantic SHA-256：`29b7b3350e19462380ba44db1535e7aa426af7f4cb5ba355357f8628060ec635`

工程、数据和科学审查均通过，开放 Blocker/Major/required Minor 为 0/0/0。静态检查覆盖 19 lane、8 internal lane、16 connections、via/priority/TLS、四份 materialization 的 6 E1/2 E2、feeder/common 域以及完整 R/U 路径。48 行网络语义比较没有未解释差异；91 行空间映射具有定位补件。

位置关系已核实：

- p100 与 feeder `[200,1200)` 位于长度 1394.87 m 的 `main_up` 内；
- common `[100,700)` 位于长度 796.49 m 的 `main_down` 内；
- 旧 upstream E1 位于 `main_up` 1393.87 m，距离 p100 下游 1293.87 m。它不能代替 feeder 入口、请求需求或实际入网计数；
- 下游 E1 含 M/R 混合群体，不能代替按 M 身份过滤的公共域指标；
- E2 只覆盖指定 ordinary lane，不代表完整 R 路径。

当前 C03 manifest：`data/processed/stage6_obstacle_20260913_v1/c03_reuse_spatial_package_revision_01/final_package_manifest_revision_02.json`，SHA-256 `6e5bb6a87beedb91d9cc64b2c32b23867d58951b0cae31596619358dae52233f`。

## 分类修订

入口位置 fallback 或实际位置错位属于机械/证据错误。配置和输出均正确、但逐 ID 入网或 `departDelay<=1.01 s` 资格失败，属于合格的 `not_resolved`，不能用技术重试改善。通过该 reported-field 资格也不证明“没有额外插入阻塞”；精确 number-flow 排程仍待后续独立核验。

## 请求授权的下一工作

请求只授权 **C04/SG6-P 准备阶段的离线实现与验收**：

1. 实现真实 V1 executed-source-map/receipt schema，并绑定 logical run、版本、condition、seed、配置、network、binary、argv 和每类输出 hash；
2. 将真实 V1 输出安全接入严格测量链、同 seed ML/C 科学配对、352 主 keys 和 14 敏感性 keys；
3. 实现执行器的 fail-closed 入口、全局预算预扣、120 s watchdog、唯一 attempt、失败保留、中断/崩溃恢复和禁止覆盖；
4. 用 synthetic/fake process 和已有档案进行零 SUMO 回归，验证成功、超时、非零退出、中断、重复 attempt、预算耗尽、缺文件/坏 hash/串 seed 等分支；
5. 生成四个 V1 attempt 的精确目录、materialization、argv 和预期 hash，形成最终 `STAGE6_VALIDATION_LAUNCH_PACKAGE.md`；
6. 完成工程、独立数据和科学复审，再把 SG6-P 精确启动卡交用户批准。

本次拟授权保持 `netconvert=0`，并且不执行 SUMO、TraCI 或 GUI。它不授权任何 smoke/验证运行。真实车辆入口、feeder 覆盖和科学结果只能在之后单独批准的 D 阶段得到。

## 当前计数和停止边界

- Stage 6 实际 SUMO/netconvert/TraCI/GUI：0/0/0/0。
- `specific_obstacle`：unresolved。
- SG6-P：未准备完成、未批准。
- 正式实验设计：仍由 SG6-R 锁定。


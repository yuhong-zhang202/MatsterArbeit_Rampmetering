# T10 Gmax5/Y3/redmin2 候选：黄灯依据及离线交付

2026-10-13。基线：`48dafb3605687b4738a6c8c45581032a79f8c8ec`。本文件记录用户授权的黄灯核查及条件式离线准备；不是正式实验、原生安全认证或新的运行许可。

## 黄灯核查结论与适用范围

工程、独立数据与只读科学预审同意 **GO_FOR_CONDITIONAL_OFFLINE_PREPARATION**：依据足以准备隔离的 T10 候选，前提是保留原安全检查、实际转黄前重新检查车辆、UNKNOWN 停止。Y3 对新 G5 状态的原生适用性尚未实测。

7 次旧 G4 转黄前的 248 个车辆快照，原 Y4 筛查均得到复现；同一人群代入不改公式的 Y3 筛查也全部通过。停止分支不依赖黄灯时长；清线分支在 Y3 下更严格。纯逻辑反例（速度 16 m/s、距线 1 m、车长 5 m）在 Y4 下通过、Y3 下 UNKNOWN，必须保留其停止结果。旧 13 辆已进入车辆的车尾记录仅与同一旧关绿时刻下的假想 Y3 红灯相容，不能证明新 G5 轨迹或新提前转红后的车尾行为。旧 R13 虽通过 clear-only 筛查却实际停车并出现 −4.501 m/s²，说明筛查不是原生驾驶选择的预测。[工程报告](../../artifacts/t10_g5_y3_candidate_20261013_v1/engineering/yellow_review_v1/ENGINEERING_YELLOW_APPLICABILITY_REVIEW_V1.md)、[独立数据评议](../../data/processed/t10_g5_y3_candidate_20261013_v1/data_yellow_v1/DATA_YELLOW_APPLICABILITY_REVIEW_V1.md)。

SUMO 原生支持 G/y/r 相位与转相控制；官方说明没有给出本场景 Y3 对所有未来车辆安全的保证。固定 SUMO 1.26 源码中的 `tls.yellow.min-decel=3` 是 **m/s²**，不是 3 秒黄灯依据。源码缓存已按固定 commit/hash 核对，但与安装二进制的编译分支等价未证明。[官方信号文档](https://sumo.dlr.de/docs/Simulation/Traffic_Lights.html)、[固定源码与边界调查](../../artifacts/t10_g5_y3_candidate_20261013_v1/engineering/yellow_review_v1/ENGINEERING_YELLOW_APPLICABILITY_REVIEW_V1.md)。

## 隔离实施边界

- 仅固定 750 veh/h 指令对应的 T10 候选；映射名义速率仍为 720 veh/h，不承诺实际两辆/周期。
- Gmax5/Y3/redmin2；提前 quota 关绿时把红灯补足至周期末，例如 G4/Y3/R3；到 G5 上限时采用 G5/Y3/R2。提前关绿也可能更早，不能把 G4 当作唯一 quota 路径。
- 每次转黄前对实际完整人口执行原 Y3 筛查，保留原接收、9+1.1、身份、车尾、红灯入口、制动、覆盖、异常和 EOF 检查。first-red 检查点从实际关绿 +3 及下一 ACK 得到。
- 新候选默认严格制动规则；旧受限数值例外不会自动扩大至新卡。原 FAIL、STOP3、全部原始证据及旧64源/900档保持。
- 本轮零 SUMO 启动。待审卡没有 canonical authorization/release，不建立新 raw 目录，不以旧剩余预算作为许可。原生观测值必须保留 null。

[用户本轮授权](../../artifacts/t10_g5_y3_candidate_20261013_v1/USER_OFFLINE_SCOPE_V1.json)、[科学实施前门](../../artifacts/t10_g5_y3_candidate_20261013_v1/science/SCIENTIFIC_PREIMPLEMENTATION_GATE_V1.md)。

## 实施与最终审查状态

工程实现及卡片已冻结；独立数据、科学最终门尚待完成。新增源码仅在 `src/candidate_a_t10_g5_y3_20261013/` 与对应 CLI/tests；原缓存、接收、车尾、worker、日志/EOF helpers 只读复用，无全局 patch。[工程实施报告](../../artifacts/t10_g5_y3_candidate_20261013_v1/engineering/implementation_v1/ENGINEERING_REVIEW_V1.md)。

**新卡：** [UA_T10_G5Y3_FIXED750_S17_01](../../artifacts/t10_g5_y3_candidate_20261013_v1/engineering/packages/UA_T10_G5Y3_FIXED750_S17_01/card.json)。

- 卡 SHA-256：`6dc909466ddf8387db7a132c2609cb09564fb05c5d917ba9d67de7ba633b7476`。
- 73 项源绑定摘要：`013a7da7518bdf822e049ab833fd06854a2b1f294f8f2120e4796f878a0e71f2`。
- 工程 32 文件 binder：`f623f11444cf3dd8c9017d5f35125d65f19385aca4a92554b21b14d51a39e35a`。
- 拟议同一运行内窗口 1200–1270 s、7 个 T10 周期，seed17，需求 M3600/R900/U360/X180 veh/h、step1 s。首次实际红灯 ACK 为持久检查点；不硬套旧红灯时刻。此窗口仍待未来明确运行授权。
- 拟议单次监控300 s、启动60 s、原始输出300000000 B、最低磁盘5 GB；均非本轮运行授权，不继承旧四任务剩预算。
- `PREPARED_NOT_RELEASED`、`SUMO_execution_authorized=false`、NUM disabled/pending，N/E/实际相位、未来人口/尾部/原生安全观测均 null。

实际验证：三个最初方法通过18.843 s；四方法版本通过18.885 s；之后只变动 startup 假接口，已改变的同一 clock 方法单独复测通过9.354 s。CLI card-check及历史环境回执对应的当前 Python/包 metadata/文件 SHA 静态核查通过，没有新 SUMO version 进程。全部日志、旧测试快照和当前源码快照保留，未声称在旧 commit 上测试新源码。[工程绑定与快照](../../artifacts/t10_g5_y3_candidate_20261013_v1/engineering/implementation_v1/SOURCE_AND_CARD_BINDING_V1.json)。

覆盖两条关绿/读回时钟、动态红灯点、Y3 拒绝于首黄运动前停止、部分与未观测核账、黄灯额外入口、模式/相位/接收/红灯/碰撞/制动/警告拒绝和无授权拒绝。原身份/inventory/yellow_scope及完整 post error block 比较相同。并非每个组合穷举测试，也没有真实七周期、正常离网或 native EOF 结果。假接口刻意从新 program 起步时，桥接仍在首次运动前选择 A_OPEN；实际原生加载默认选择未测。

## 干净 checkout 核查：V1 未通过，修复中

精确本地检查点 `03949494d02c94802e5bc2461ca9daf2a82b341a` 的四个当前方法实测3通过、1ERROR（19.387 s）：提交卡片绑定主工作区的绝对输入路径，另一目录的checkout正确得到 `FOREIGN_RUNTIME_INPUT`。这是测试fixture跨目录适用性缺陷；不放宽路径门、不重绑原卡或修改运行实现。仅制作独立公共依赖离线包供回归，最终门尚未完成。[原失败与回执](../../artifacts/t10_g5_y3_candidate_20261013_v1/portability_v1/CLEAN_CHECKOUT_RECEIPT_V1.json)。checkout raw仅`.gitkeep`、Git保持干净，无SUMO。

工程 revision02 仅修改测试，未修改真实卡片、73项源或任何校验门。两个独立公共依赖临时目录分别验证 foreign 卡拒绝与新离线 fixture 的真实 prepare/validate/缺许可拒绝；没有 mock 掉 validator。路径别名首次FAIL（0.125 s）及源码前像保留，fixture.resolve()最小修复后受影响方法PASS（0.133 s）；还待新检查点干净四方法与data/science最终门。[修订记录](../../artifacts/t10_g5_y3_candidate_20261013_v1/engineering/implementation_revision02/ENGINEERING_PORTABILITY_REVIEW_V2.md)。

# T10 Gmax5/Y3/redmin2 候选：黄灯依据及离线交付

2026-10-13。基线：`48dafb3605687b4738a6c8c45581032a79f8c8ec`。本文件记录用户授权的黄灯核查及条件式离线准备；不是正式实验、原生安全认证或新的运行许可。

**最终状态：离线候选、最小实现、针对性回归及工程→独立数据→只读科学审查完成；GO仅限交付用户审查。** 本轮零SUMO，不再追加离线扩展。Y3未来原生安全和750服务能力尚未验证。

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

工程实现及卡片已冻结；独立数据与科学最终门均已完成，仅限离线交付。新增源码仅在 `src/candidate_a_t10_g5_y3_20261013/` 与对应 CLI/tests；原缓存、接收、车尾、worker、日志/EOF helpers 只读复用，无全局 patch。[工程实施报告](../../artifacts/t10_g5_y3_candidate_20261013_v1/engineering/implementation_v1/ENGINEERING_REVIEW_V1.md)。

**新卡：** [UA_T10_G5Y3_FIXED750_S17_01](../../artifacts/t10_g5_y3_candidate_20261013_v1/engineering/packages/UA_T10_G5Y3_FIXED750_S17_01/card.json)。

- 卡 SHA-256：`6dc909466ddf8387db7a132c2609cb09564fb05c5d917ba9d67de7ba633b7476`。
- 73 项源绑定摘要：`013a7da7518bdf822e049ab833fd06854a2b1f294f8f2120e4796f878a0e71f2`。
- 工程 32 文件 binder：`f623f11444cf3dd8c9017d5f35125d65f19385aca4a92554b21b14d51a39e35a`。
- 拟议同一运行内窗口 1200–1270 s、7 个 T10 周期，seed17，需求 M3600/R900/U360/X180 veh/h、step1 s。首次实际红灯 ACK 为持久检查点；不硬套旧红灯时刻。此窗口仍待未来明确运行授权。
- 拟议单次监控300 s、启动60 s、原始输出300000000 B、最低磁盘5 GB；均非本轮运行授权，不继承旧四任务剩预算。
- `PREPARED_NOT_RELEASED`、`SUMO_execution_authorized=false`、NUM disabled/pending，N/E/实际相位、未来人口/尾部/原生安全观测均 null。

实际验证：三个最初方法通过18.843 s；四方法版本通过18.885 s；之后只变动 startup 假接口，已改变的同一 clock 方法单独复测通过9.354 s。CLI card-check及历史环境回执对应的当前 Python/包 metadata/文件 SHA 静态核查通过，没有新 SUMO version 进程。全部日志、旧测试快照和当前源码快照保留，未声称在旧 commit 上测试新源码。[工程绑定与快照](../../artifacts/t10_g5_y3_candidate_20261013_v1/engineering/implementation_v1/SOURCE_AND_CARD_BINDING_V1.json)。

覆盖两条关绿/读回时钟、动态红灯点、Y3 拒绝于首黄运动前停止、部分与未观测核账、黄灯额外入口、模式/相位/接收/红灯/碰撞/制动/警告拒绝和无授权拒绝。原身份/inventory/yellow_scope及完整 post error block 比较相同。并非每个组合穷举测试，也没有真实七周期、正常离网或 native EOF 结果。假接口刻意从新 program 起步时，桥接仍在首次运动前选择 A_OPEN；实际原生加载默认选择未测。

## 干净 checkout 核查：V1 失败保留，V2 已通过

精确本地检查点 `03949494d02c94802e5bc2461ca9daf2a82b341a` 的四个当前方法实测3通过、1ERROR（19.387 s）：提交卡片绑定主工作区的绝对输入路径，另一目录的checkout正确得到 `FOREIGN_RUNTIME_INPUT`。这是测试fixture跨目录适用性缺陷；不放宽路径门、不重绑原卡或修改运行实现。当时最终门暂停，随后仅修复独立公共依赖离线包；V2通过及最终审查见下文。[原失败与回执](../../artifacts/t10_g5_y3_candidate_20261013_v1/portability_v1/CLEAN_CHECKOUT_RECEIPT_V1.json)。checkout raw仅`.gitkeep`、Git保持干净，无SUMO。

工程 revision02 仅修改测试，未修改真实卡片、73项源或任何校验门。两个独立公共依赖临时目录分别验证 foreign 卡拒绝与新离线 fixture 的真实 prepare/validate/缺许可拒绝；没有 mock 掉 validator。路径别名首次FAIL（0.125 s）及源码前像保留，fixture.resolve()最小修复后受影响方法PASS（0.133 s）；其后的新检查点干净四方法及data/science最终门均已完成，详见下文。[修订记录](../../artifacts/t10_g5_y3_candidate_20261013_v1/engineering/implementation_revision02/ENGINEERING_PORTABILITY_REVIEW_V2.md)。

最终可移植测试检查点 `fb8397678650c327769589044fa454b55bb4189b` 的四个当前方法在干净 checkout 全部PASS（19.986 s，外层20.169899 s）；raw只含`.gitkeep`、Git仍干净。它使用本机已有主工作区venv及安装文件哈希，未安装依赖，不是另一台机器的环境验证。公开回归不依赖完整raw；旧248快照/车尾原始复算仍需要本地raw/cache，不能把两种覆盖混称为公开完整审计。[V2真实回执](../../artifacts/t10_g5_y3_candidate_20261013_v1/portability_v2/CLEAN_CHECKOUT_RECEIPT_V2.json)。卡和73项源码在测试修复期间保持不变；最终data/science门已完成，仅限离线交付。

## 独立数据最终审查与后续门

独立静态 V4 实际exit0，最终结论 **GO_FOR_OFFLINE_DELIVERY_REVIEW_ONLY**、无未解决实质数据问题。22文件binder：`840b23d49b3481ba0a95bb04985b2c3216adfa2dbddd21c964d39b459133a3f0`。原32工程binder中被替换的测试按0394949 Gitblob/前像核实，其他31项当前不变；当前测试后三个方法AST未改变。V1/V2独立checker表达错误、V3原静态PASS、V4新版本PASS均保留，没有隐藏失败或重写历史。[最终数据审查](../../data/processed/t10_g5_y3_candidate_20261013_v1/data_offline_v1/DATA_OFFLINE_FINAL_REVIEW_V1.md)。

**运行前缺口：** 原G4实际数据审计器尚未完成G5/Y3版本适配；当前交付不声明native-ready。后续若计划运行，应先完成有界、版本化的实际phase/clock/body/EOF审计适配和三方精确运行门，再取得新卡/源码/资源的明确用户授权与canonical release。当前离线GO不能代替运行预审GO，旧剩余预算与NUM批准也不能代替新许可。

## 科学终审、结项范围与交接

只读科学终审 **GO_FOR_OFFLINE_DELIVERY_ONLY**、无新增Blocker/Major，确认本轮预审条件落实。可停止继续离线扩展，交用户审查精确候选。旧G4 actualreader适配不阻塞当前离线交付，但属于未来release前门；本意见不是native预启动GO。[完整科学记录](../../artifacts/t10_g5_y3_candidate_20261013_v1/science/SCIENTIFIC_FINAL_OFFLINE_REVIEW_V1.md)。

已确认：版本化相位/时钟实现与公开回归通过；旧source64/900T8/guard阈值/真实卡不变；E/N/null边界、未知和无许可拒绝通过限定离线核查。有限推断：旧低速G4同输入相容与更严格Y3筛查支持准备有界诊断候选。仍未确认：未来G5人口/真实接收、制动、尾部/EOF、实际N、服务改善、源码二进制等价及NUM新scope适用性。加1秒绿灯不保证N14。

更新 PROJECT_STATE、WORKLOG 和 README，是为了同步本轮离线结果、CLI/回归接口与下一门；DECISIONS、空未冻结的EXPERIMENT_PROTOCOL、AGENTS、thesis和监督材料未改。所有旧原始数据、失败和资格状态保留。新源码/卡实际测试快照对应上列源SHA和fb839767；之后仅文档与审查产物更新，不声称在未来交付commit上重新跑了SUMO或回归。

下一位：用户/Chat审查本方案及卡片。若之后希望运行，先完成版本化G5/Y3 actualreader准备和三方精确运行评议，再明确批准本卡/源码/拟议资源；这份建议本身不构成执行授权。本轮不创建新Issue/PR、不push或merge；本地提交与证据可以审查，尚未发布GitHub。

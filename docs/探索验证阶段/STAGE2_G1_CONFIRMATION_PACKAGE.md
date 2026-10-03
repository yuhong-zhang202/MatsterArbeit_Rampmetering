# Stage 2 G1 集中确认包（S2）

日期：2026-09-09

状态：**Historical proposal / superseded。** `docs/STAGE2_G1_EXECUTION_PLAN_V2.md` D0–D7 已完成，结果及当前唯一待决定提案见 `docs/STAGE2_G1_V2_DIAGNOSTIC_REPORT.md`。以下旧六行矩阵及运行建议仅供追溯，不再作为当前推荐，不可据此启动仿真。

## 推荐方案 A：完整计划出发 cohort 的有限时域观察

观察目标：从空网开始，记录匝道末端积压如何延伸至共享城市道路及网外等待，并跟踪同一批计划车辆直至批准的最大截止；不声称稳态。

- `warmup_s=0`：不删除 46、192、412/414 s 的形成过程。
- `measurement_duration_s=1500`：需求安排窗口 `[0,1500)`；主分析对象是该窗口内全部计划出发 cohort。
- `post_demand_clearance_s=1200`：最大仿真截止 2700 s。达到截止仍未清空即标记截尾，不自动延长。
- 固定时间窗用于 E1/FCD 状态描述；车辆结果以计划出发 cohort 为主。所有窗口继续从 t=0 记录，不能把 cohort 完成者子集当作全体。

这组秒数来自一条已保留高需求轨迹的覆盖能力，只是探索候选，不是跨条件均能清空的保证。现有修复后高轨迹可以支持该候选的窗口敏感性证据；它不自动替代未来矩阵项，因为其原 summary 的 measurement 标签是 600–1500 s，且 G1 尚未批准复用等价性。

## 次要窗口敏感性 B：固定比较窗

将同一方案 A 输出离线重聚合为 `[300,1500)` 固定比较窗，同时保留 t=0 起的加载诊断和全部计划 cohort 账目。该窗口保留 412/414 s 共享道事件，却把 46/192 s 放在比较窗外，因此只用于检查摘要对分析窗口是否敏感，不替代主问题。它与方案 A 具有相同需求安排和 2700 s 截止，无控制交通轨迹不应因报告窗口改变而另跑一组六行；如分析入口暂不支持该窗口，S3 补离线重聚合，不新增仿真。

## 拟议字段与算法

| 层级 | 字段（单位） | 空间/时间 | 算法与状态 |
| --- | --- | --- | --- |
| 执行有效性 | run ID、版本、配置/代码 hash、日志告警、状态 | 全运行 | 原样保存；任一来源缺失则该运行 `output_incomplete` |
| 测量完整性 | E1 `flow` (veh/h)、`speed` (m/s)、`occupancy` (%)、`nVehContrib` | 四个点检测器；原始 30 s `[begin,end)` | 直接解析原始 interval，不移动时间标签 |
| 路径观察 | R/U 各车道/内部组的 vehicle samples、stopped samples | 明确命名车道和内部连接；FCD 1 s | `speed<=0.1 m/s`；仅描述，阈值仍是技术占位 |
| 需求实现 | planned、entered、waiting outside (veh) | M/R/U/X；每个 before-step 时刻 | 以运行生成的计划 ID＋计划时刻清单为总体，再左连接实际入网/到达记录；已完成车辆可用 `depart-departDelay` 独立核对计划时刻 |
| 车辆结果 | arrived、in network (veh)，`departDelay`、`duration`、二者之和 (s) | 计划 cohort，从计划时刻到截止 | 未入网、已入网未到达和输出缺失分别保留；总时间不解释为因果额外延误 |
| 科学资格 | Breakdown、Capacity Drop、sweet spot | 未定义 | `not_evaluated`；本批最多提供探索性描述 |
| 合流断面 | ramp merge flow | 匝道进入 `main_down_0` 的明确断面 | `not_measured`；不得以 E1 差值或 R 入网量代理 |

需求实现、清空、Breakdown、Capacity Drop、有效储存和显著性阈值均为 **Unknown/not_evaluated**。G1 只批准记录精确数值及截尾状态，不把未知阈值补成 pass/fail。

允许的储存观察边界仅为已核验四段路径：`:urban_diverge_1_0`、`ramp_storage_0`、`:ramp_mid_0_0`、`ramp_accel_0`。总编译长度 494.87 m 仅作空间定位，不是批准的有效储存容量。`shared_approach_0` 与 `urban_in_0` 单列为越界/上游影响观察。

## Proposed 无控制运行矩阵（上限六项）

所有行固定 `qUrban=360 veh/h`、`qX=180 veh/h`，使用方案 A 的 `0/1500/1200 s`。三条件来自已有探索锚点，用于低积压参照、可能过渡、明显受约束三类行为，不预设实际分类一定成立。

| 行 | qMain | qRamp | seed | 理由 |
| ---: | ---: | ---: | ---: | --- |
| 1 | 1080 | 360 | 17 | 已有低需求锚点的统一时长复查 |
| 2 | 1080 | 360 | 19 | 同条件预先指定第二 seed |
| 3 | 2600 | 600 | 17 | 已有中间需求锚点的统一时长复查 |
| 4 | 2600 | 600 | 19 | 同条件预先指定第二 seed |
| 5 | 3200 | 720 | 17 | 已有受约束锚点；不强制用旧运行替代 |
| 6 | 3200 | 720 | 19 | 同条件预先指定第二 seed |

种子规则在看到新结果前固定为：保留历史 seed 17 以便连续核对，再取其后的最小素数 19。此规则只是防止按结果挑 seed；两 seed 不具有统计充分性。

## 失败、截尾、重试与停止规则

1. 先只执行第 1 行。data_analyst 核对配置、输出结构、M/R/U/X 守恒、30 s E1 覆盖及来源 hash 后，才允许继续其余已批准行。
2. 运行到 2700 s 仍有网外等待或在网车辆：保留数量。runner 的原始 `clearance_status` 保持不变，离线报告另将该项标记为 `censored_at_2700`；不延长、不删除、不换 seed。
3. 重试预算：每行最多一次，仅限已定位的执行/写盘故障，必须保持同参数和 seed；交通积压、未清空或“不好看”不构成重试理由。最多六个计划运行加最多六次故障重试；首次核验失败时先暂停全部余项。
4. 出现覆盖缺失、车辆守恒失败、源/输出覆盖风险、新严重 SUMO 警告或需要改变交通行为时立即停止后续矩阵并报告。
5. 六行完成后不自动加需求点。若三类行为仍无法区分，只允许提出一轮有明确信息目标的补充包或导师问题单。

保持不变：网络几何、连接优先权、固定信号、车辆模型/行为参数、插入设置、E1/E2/FCD 定义、无控制状态、qUrban/qX、SUMO 1.26.0，以及原始文件只读规则。不得进入 ALINEA、override、正式网格或论文结论。

所有新运行只能通过项目 runner 启动；禁止直接加载任何历史 `/private/tmp/minimal_uncontrolled_*/scenario.sumocfg`，因为旧配置包含历史绝对输出路径。执行时维护六行 ledger，记录 planned row、attempt、`retry_of`、精确命令、runtime 路径、开始/结束时间、退出状态、原始 `clearance_status` 和分析状态。runner 不自动强制首次暂停、总运行数或重试预算，这些边界由 ledger 和代理执行顺序控制。

runner 现有的 `TECHNICAL_MAX_END_IN_NETWORK_FRACTION=0.15` 及 vehicle-outcome gate 继续作为旧技术字段保留；它不是本 G1 包的需求实现、清空或科学合格阈值，不得据此把运行判为探索性科学 `pass/fail`。

方案 A 的命令模板如下；每行只替换已批准表中的三个占位值：

```bash
.venv/bin/python src/scenarios/run_minimal_uncontrolled.py \
  --profile low \
  --q-main <approved_q_main> \
  --q-ramp <approved_q_ramp> \
  --seed <approved_seed> \
  --warmup-s 0 \
  --measurement-duration-s 1500 \
  --demand-end-s 1500 \
  --post-demand-clearance-s 1200
```

方案 B 仅把 `--warmup-s` 改为 `300`、`--measurement-duration-s` 改为 `1200`；显式保留 `--demand-end-s 1500`，由 runner 校验三者一致。

## S3 最小代码缺口与 observation-only 补充

Runner 已支持三时段，无需改交通执行逻辑。S3 只需让离线分析对任意新运行生成同口径 cohort/time-line 报告：以需求/route 文件中的计划 ID 和计划时刻为总体，左连接实际入网及到达记录，并显式区分未入网、已入网未到达、输出缺失和 `censored_at_2700`；现有固定路径 queue diagnostic/replay 不能直接冒充通用入口。该离线入口还应独占创建输出、记录 source hash；首次暂停和重试 ledger 无需开发批处理平台。

匝道合流断面流量当前 `not_measured`。它不阻碍本轮积压传播和需求实现问题。若用户希望下一批同时定量分解合流流量，最小补充是在匝道进入 `main_down_0` 的唯一连接处增加 observation-only 断面计数，并验证一车一次、遗漏/重复及 30 s 汇总；该补充涉及新的运行输出，应随 G1 单独明确批准。未批准时矩阵仍可运行，但报告必须继续标为 `not_measured`。

## G1 需要用户一次确认的内容

经工程、数据和科学审查后的推荐确认内容如下：

1. 采用方案 A：`0/1500/1200 s`；同时从相同输出报告 `[300,1500)` 次要窗口 B，不为 B 新增运行。
2. 批准六行无控制矩阵及 seed 17/19 的预先规则；这只是探索预算，不是统计充分性结论。
3. 首次只运行第 1 行，完成数据核验后再继续其余已批准行。
4. 每行批准最多一次同参数、同 seed 的技术故障重试；交通拥堵、未清空或结果不理想不允许重试。
5. 批准 2700 s 为共同最大截止，未清空时按 `censored_at_2700` 保留，不延长、不剔除。
6. 本批不新增合流断面 observation-only 测量，继续标为 `not_measured`；S5 必须披露主线/匝道通过量的定量分解尚未完成。若以后需要该量，另行提交测量实现、独立对账、配对回归和额外运行预算。

用户可整体批准，或逐项修改。任何确认仍属于探索阶段，不冻结正式协议或科学阈值。

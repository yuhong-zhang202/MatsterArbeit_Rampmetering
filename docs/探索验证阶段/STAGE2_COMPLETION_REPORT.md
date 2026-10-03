# Stage 2 completion report and C6/G2 acceptance package

日期：2026-09-09。

```text
execution_status: C0-C5 completed
diagnostic_closure: completed_and_scientifically_reviewed
stage2_acceptance: accepted
next_step_readiness: ready_for_next_exploration
formal_experiment_status: not_started
```

## 1. 给用户的一页结论

获批的 Stage 2 收尾已按 `docs/STAGE2_COMPLETION_PLAN.md` 完成。八条逻辑记录全部有可追溯来源；C17 复用，七条新运行实际启动 SUMO 七次，技术重试零次，未使用第八次上限。全部新运行使用 SUMO/netconvert 1.26.0、同一场景、0/1500/1200 s 和预先固定的 seeds 17/23。没有隐藏失败运行，也没有因结果方向增加点、seed 或时长。

八条运行都在 2700 s 前完成全部计划车辆，六条 E1 每运行均为 90 个连续区间。运行日志和 SUMO summary 没有登记 warning、error、collision、teleport、emergency braking 或 route error。232 个归档文件经逐文件 SHA-256 对账；最终离线分析独立核验了 14,564 条运行-车辆记录、4,320 条 E1、2,912 条 cohort 时间线、2,100 个 R 合流事件的 4,200 个括号端点和 198 个同 seed 差值。

有限比较得到的主要结果：

1. 固定 qRamp=720 veh/h，将 qMain 从 3200 降至 2600 时，两个 seed 在需求期内观察到更多 R 首次进入下游，R/U 在 1500 s 时的网外数量减少，U 到达数增加。
2. 将 qMain 从 3200 提至 3800 时，两个 seed 在 1500 s 前都没有观察到 R 首次进入下游；R/U 网外数量增加，U 到达数减少。与此同时，M-only 内部断面仍实现请求附近的高通过量且速度较高。该组合描述“主线保持通过而匝道机会被压制”，不能据此称容量提升、无拥堵或系统改善。
3. 固定 qMain=3200，将 qRamp 从 720 降至 360 时，1500 s 的 R/U 网外数量明显减少，U 到达数增加；但 R 首次进入下游只增加 2/0 辆，U 路内存量增加 14/13 辆，M 速度差值方向也不一致。因此不能概括为“匝道吞吐明显提高”或“所有城市指标改善”。
4. 两个 seed 的主要计数方向大体一致，但这只是早期敏感性描述，不是统计稳健性证明。

本轮没有建立主线 Breakdown、Capacity Drop、稳态、容量、sweet spot 或因果机制。Stage 2 不以必须出现这些现象为完成条件。当前证据足以关闭本轮有限诊断，并支持提出一个新的、单独审批的定点探索方案。因此科学审查建议 `next_step_readiness=ready_for_next_exploration`；这不授权任何新运行、ALINEA、正式需求网格或协议冻结。

核心事实置信度 High；对下一个探索问题的适配判断 Moderate；正式容量与 Breakdown/Capacity Drop 仍 Unknown。

## 2. C0–C5 执行状态

| 步骤 | 状态 | 主要证据 |
| --- | --- | --- |
| C0 | Completed | 授权、台账、C17 29 文件无损归档和 source map |
| C1 | Completed | archive-only 分析入口；25 项离线测试；C17 revision_01；科学合同审查通过 |
| C2 | Completed | 七条新运行，7/8 启动、0 重试；每条技术验收及归档通过 |
| C3 | Completed | revision_02 首项门；revision_03 全批分析；revision_04 统一图轴且表格字节不变 |
| C4 | Completed | 数据独立核验和 scientific_reviewer 五项测量审查全部通过声明范围 |
| C5 | Completed | 本报告、项目状态和工作日志一致；G2 包形成 |
| C6/G2 | Accepted | 用户明确批准 G2，正式关闭 Stage 2 有限诊断 |

## 3. 运行台账与预算

全部固定 qUrban=360、qX=180 veh/h，warm-up/measurement/clearance=0/1500/1200 s。

| Run | qMain/qRamp | Seed | 来源或 runtime | 新 SUMO 启动 | 最后到达 s | 状态 |
| --- | ---: | ---: | --- | ---: | ---: | --- |
| C17 | 3200/720 | 17 | `/private/tmp/minimal_uncontrolled__5s3s06d`，复用 | 0 | 2401 | Complete |
| C23 | 3200/720 | 23 | `/private/tmp/minimal_uncontrolled_5tr62jan` | 1 | 2387 | Complete |
| ML17 | 2600/720 | 17 | `/private/tmp/minimal_uncontrolled_ci4lj3q7` | 1 | 2286 | Complete |
| ML23 | 2600/720 | 23 | `/private/tmp/minimal_uncontrolled_g9vzf7is` | 1 | 2274 | Complete |
| MH17 | 3800/720 | 17 | `/private/tmp/minimal_uncontrolled_ph15kccg` | 1 | 2551 | Complete |
| MH23 | 3800/720 | 23 | `/private/tmp/minimal_uncontrolled_v7i71hkb` | 1 | 2558 | Complete |
| RL17 | 3200/360 | 17 | `/private/tmp/minimal_uncontrolled_l63nafev` | 1 | 1864 | Complete |
| RL23 | 3200/360 | 23 | `/private/tmp/minimal_uncontrolled_meqptc23` | 1 | 1859 | Complete |

预算：计划七次常规新启动，硬上限八次；实际七次，重试零次，余下的一次不使用。C23 启动前有一次外层 shell 重定向失败，因为 runner log 目录尚未建立；Python、netconvert 和 SUMO 均未启动，故不计 SUMO 启动或技术重试。该事件保留在 ledger，没有被删除。

每条运行归档 29 个普通文件，无 symlink 或特殊文件。C17 和七次新运行共 232 个文件；七次新运行归档共 329,768,964 bytes。原 `/private/tmp` 输出未修改，`data/raw/` 未写入。离线分析只经 source map 读取项目内归档，禁止静默回退到临时路径。

## 4. 条件结果

斜线前后为 seed 17/23。M 流量和速度来自 M-only internal merge-entry E1 的 A `[0,1500)` 窗口；R 数量是首次下游 FCD 观察，不是精确物理过断面时刻。

| 条件 | M A流量 veh/h | M A速度 m/s | 1500前R首次下游 | 1500时R/U网外 | 1500前U到达 | 最后到达 s |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| C | 3194.4 / 3189.6 | 30.873 / 30.321 | 36 / 40 | 150/75；146/73 | 49 / 51 | 2401 / 2387 |
| ML | 2589.6 / 2592.0 | 30.422 / 30.022 | 67 / 69 | 122/61；121/60 | 63 / 64 | 2286 / 2274 |
| MH | 3794.4 / 3796.8 | 31.709 / 31.521 | 0 / 0 | 180/90；181/90 | 33 / 33 | 2551 / 2558 |
| RL | 3194.4 / 3189.6 | 30.496 / 30.366 | 38 / 40 | 9/9；9/10 | 101 / 101 | 1864 / 1859 |

### 4.1 ML−C：降低主线请求量

- R 在 1500 s 前首次下游观察增加 31/29 辆。
- 1500 s 的 R 网外数量减少 28/25，U 网外数量减少 14/13。
- 1500 s 前 U 到达增加 14/13。
- 最后到达提前 115/113 s。
- M A 流量按设计降低约 604.8/597.6 veh/h；速度也降低 0.450/0.299 m/s。速度变化不能独立解释交通质量或容量。

### 4.2 MH−C：提高主线请求量

- M A 流量增加 600.0/607.2 veh/h；本条件的计划 M 数均得到内部 E1 全程聚合贡献。
- R 在 1500 s 前首次下游观察从 36/40 降为 0/0。
- 1500 s 的 R 网外数量增加 30/35，U 网外数量增加 15/17。
- 1500 s 前 U 到达减少 16/18；最后到达推迟 150/171 s。
- M A 速度比 C 高 0.837/1.200 m/s。该现象与匝道受限并存，不可解释为系统改善、容量提升或没有拥堵。

### 4.3 RL−C：降低匝道请求量

- 1500 s 的 R 网外数量减少 141/137，U 网外数量减少 66/63。
- 1500 s 前 U 到达增加 52/50；最后到达提前 537/528 s。
- R 在 1500 s 前首次下游观察只增加 2/0，不能称匝道吞吐明显改善。
- U 在 1500 s 的路内数量增加 14/13；这与网外减少和到达增加描述不同状态，不能合并成“所有城市指标改善”。
- M A 流量与 C 相同；A 速度差为 −0.377/+0.045 m/s，B 流量差为 +6/−9 veh/h，方向不一致。

## 5. 三阶段时长审查

### 0 s warm-up

本轮明确观察空网加载全过程。B `[300,1500)` 只是同一条轨迹的敏感性切窗，不是独立重复或经验证的稳态预热。A/B 主线聚合相近也不能证明全系统稳定。

### 1500 s measurement/demand

1500 s 足以显示本批次主线通过、R 合流机会以及 R/U 累积状态如何随单一需求轴变化。它不证明更长需求期不会出现新行为，也没有验证稳态或正式 Breakdown 识别。

八条运行都有 R/U 在 1500 s 后才入网：

| 条件 | R post departures，seed17/23 | U post departures，seed17/23 |
| --- | ---: | ---: |
| C | 150 / 146 | 75 / 73 |
| ML | 122 / 121 | 61 / 60 |
| MH | 180 / 181 | 90 / 90 |
| RL | 9 / 9 | 9 / 10 |

因此“全部车辆最终到达”不能代替“请求需求在需求期内实现”。

### 1200 s post-demand clearance

本批次所有运行在 2700 s 前完成，最晚到达 2558 s。1200 s 清空预算对这八条运行足够，置信度 High。它不是零入流恢复：清空期仍有延迟车辆持续入网；也不是对未来工况的通用时长保证。未来正式时长仍未冻结。

## 6. 测量资格与限制

| 项目 | 状态 | 含义 |
| --- | --- | --- |
| `plan_count_status` | Verified | 生成需求 XML 的 flow number 按类核验 |
| `departure_coverage_status` | Verified | 正常结束记录中实际入网身份/数量核验 |
| `arrival_coverage_status` | Verified | 到达和 unfinished 覆盖核验；本批最终无 unfinished |
| `schedule_time_status` | Unverified | 聚合 flow 没有可独立核验的逐 ID 计划时刻 |
| 内部 E1 聚合覆盖 | Passed | 声明的 M-only 两内部断面、区间及聚合可用 |
| 内部 E1 逐 ID 零遗漏/零重复 | Not verified | 普通 E1 无 vehID；FCD 在短内部车道不是完整过车名单 |
| 旧 upstream E1 | Ineligible for state inference | `departPos=last` 与 detector 重叠，受起点插入污染 |

旧 `duration×index/count` 公式与 C17 M 的 `depart-departDelay` 最大相差 0.379437 s，不能用于给缺失车辆补造精确排程。中途精确网外等待曲线和全总体精确网外延误因此不报告。1500/2700 s 端点只在计划总数、SUMO loaded/inserted/arrived 及输出覆盖共同核验时计算 P−E 和 E−A。

无贡献 E1 interval 的速度保留缺值；未发现有贡献负速度异常记录。全部 R 有相邻 FCD 合流括号；跨 30 s 箱界歧义按 C17、C23、ML17、ML23、MH17、MH23、RL17、RL23 分别为 4、8、12、11、10、15、2、3，没有强行分配为精确 30 s 流量。

主线车辆使用 `departPos=last`，可在 `main_up` 末端插入；当前结果不能代表长 feeder 上游路段已形成真实交通状态。所有结果仅属于这个合成场景和有限探索条件。

## 7. 独立验证与科学审查

最终数据版本：`revision_04`。`revision_03` 保留；revision_04 只统一图的横轴标签及同列纵轴，五张 CSV 与 revision_03 字节相同。

验证结果：

- archive-only `independent_verification.py --check-only` 通过；
- 25 项离线单元/静态分析测试通过；`py_compile` 和 `git diff --check` 通过；
- 232 文件 hash、14,564 车辆、4,320 E1、2,912 cohort 行、4,200 合流端点和 198 对照差值独立一致；
- 两张最终图经 data_analyst、scientific_reviewer 和主代理查看，使用统一坐标并明确累计入网/到达不是网外等待曲线；
- 正式 protocol 为空，结果持续标为 exploratory，不作为正式论文证据。

scientific_reviewer 的五项结论：

| 检查 | 状态 |
| --- | --- |
| 测量目标 | Passed |
| 实际覆盖 | Passed，限声明断面、FCD 路内和端点范围 |
| 遗漏/重复 | Passed，限本批记录与聚合；E1 逐 ID仍 not_verified |
| 独立对账 | Passed |
| 回归保护 | Passed，限已实现合同 |

原 C4 审查没有 Blocker、Major 或要求继续修改数据的 Minor。随后独立 G2 复审发现状态台账残留和验证覆盖表述问题；处理记录见 `docs/STAGE2_G2_REVIEW_20260909.md`。不能将既有 `independent_verification.py` 单独视为逐车全部字段、E1 各窗口组合量和真正首次合流事件的完整独立证明。置信度 High（本批记录与有限描述），Moderate（下一步建议）。

G2 复审补核已通过并保存在 `data/processed/stage2_completion_20260909_v1/g2_review/`：直接核验 14,564 车辆的四个分析用字段及 tripinfo/vehroute/表格完整身份集合、96 项内部 E1 分组窗口指标、2,100 个真正首次 R 下游事件及前帧、八条运行末次入网/到达和七次新启动。它与原 checker 共同构成独立核验证据；不声称检查了所有 XML 属性。台账和文档小项已修正，复审建议批准有限诊断，用户验收仍 pending。

## 8. 下一步去向

`next_step_readiness=ready_for_next_exploration`，理由是本轮有限比较有完整、可复算的核心证据，并提出了一个明确的下一问题。该状态不表示正式实验、ALINEA 或控制比较已经就绪。

Proposed（待批准的优先建议）：**先提交一份关于“主线输入与匝道合流机会关系”的定点探索提案**。它应以 MH 在两个 seed 的需求期内 R 首次下游观察均为零为具体起点，判断当前无控制基线对后续 ALINEA 对照是否合适。任何新增运行、几何/优先权/行为改变或 ALINEA 均需另行批准。

可给 Robert Hilbrich 的三个确认问题：

1. 当前“主线保持通过、匝道受限并累积城市侧等待”的无控制基线，是否适合拟议的控制比较？
2. 下一阶段是否继续采用有限时域全过程评价，还是另行设计稳态问题？
3. 主线保护、城市保护和允许储存范围，应优先明确哪些正式评价定义？

导师答复不是 G2 验收前提，本轮未发送外部消息。

## 9. G2 验收清单

- [x] 正确复用既有测量成果，未用受污染 upstream E1 做主线状态结论。
- [x] 八条记录身份明确；失败、缺失和预算可独立对账。
- [x] 三组同 seed 单因素问题均有有限、可靠且不过度解释的答案。
- [x] 计划需求、实际入网、合流观察、到达、网内、网外和 Unknown 严格区分。
- [x] 窗口和截尾限制明确，时长未冒充稳态或正式冻结选择。
- [x] 两个 seed 分列且未冒充统计稳健性或需求空间覆盖。
- [x] 结论通过独立数据核验和 scientific_reviewer 审查；无未关闭实质问题。
- [x] 原始归档、hash、source map 和分析入口足以复算最终包。
- [x] 完成报告、PROJECT_STATE、WORKLOG 和执行台账一致；未擅改 DECISIONS、EXPERIMENT_PROTOCOL、导师记录或 thesis structure。
- [x] 用户明确接受 Stage 2 有限诊断收尾；后续具体研究方案仍待确认。

**G2 决定：用户已接受。**用户原话：“批准 G2，正式关闭 Stage 2。”本轮有限诊断正式关闭；验收不授权新仿真，不冻结正式设计，也不表示整个探索阶段结束。上文复审时 pending 的表述是验收前历史记录。

## 10. 产物索引

- 执行计划：`docs/STAGE2_COMPLETION_PLAN.md`
- 执行台账：`data/processed/stage2_completion_20260909_v1/execution_ledger.json`
- 最终分析：`data/processed/stage2_completion_20260909_v1/revision_04/`
- 最终表格：`results/tables/stage2_completion_20260909_v1/revision_04/`
- 最终图：`results/figures/stage2_completion_20260909_v1/revision_04/`
- 原始运行归档：`artifacts/stage2_completion_20260909_v1/runtime_archive/`
- source maps：`data/processed/stage2_completion_20260909_v1/source_maps/`
- 外层 runner logs：`artifacts/stage2_completion_20260909_v1/runner_logs/`

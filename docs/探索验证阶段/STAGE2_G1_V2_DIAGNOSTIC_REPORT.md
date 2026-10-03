# Stage 2 G1 v2 定点离线诊断报告

日期：2026-09-09。

状态：**D0–D7 completed；其 D7 提案随后获批并完成定点 S3–S5。Exploratory，不是正式实验或论文证据。** 本文件记录执行前诊断；完成结果见 `docs/STAGE2_S3_S5_VALIDATION_REPORT.md`。

## 1. 问题与来源

本轮复用修复后高需求 seed 17 轨迹 `/private/tmp/minimal_uncontrolled_8egb0qb1`，不重复旧六行矩阵。实际需求 qMain/qRamp/qUrban/qX=3200/720/360/180 veh/h，计划 M/R/U/X=1333/300/150/75，需求 `[0,1500)`，执行截止 2700 s，SUMO 1.26.0。原 summary 的 warm-up/measurement 为 600/900 s；A=`[0,1500)`、B=`[300,1500)` 是对同一交通轨迹的新离线观察窗，没有改写原运行标签。

来源 hash、命令和输出登记在 `data/processed/stage2_g1_v2_20260909_r2/manifest.json`。首版产物保留；本文只使用经解释修订和科学复核的 `_r2` 版本。正式协议为空，breakdown、capacity drop、有效储存、显著性和 sweet spot 定义仍未批准。

## 2. 技术与测量结果

### 主线与 E1

- 四个 E1 各有 90 个原始 `[begin,end)` 30 s interval，共 360 行，覆盖 `[0,2700)`；121 个 interval 没有有效速度贡献，原始值保留并按缺值处理。
- FCD 有 2700 个原始标签 `0..2699`、1858 个唯一车辆 ID；2700 s 没有 FCD 标签，明确为缺值。主线外部及内部六条 lane 的 `speed<=0.1 m/s` 技术停驶样本数均为 0。
- 上述“0 个停驶样本”不证明主线没有拥堵或 breakdown。FCD 是 1 Hz 离散快照，停驶阈值也不是批准的 breakdown 定义。
- 原始上游 E1 位于 `main_up_0/1` 终点前 1 m，与 `departPos=last` 的插入位置重合，不能作为常规上游断面交通状态。三个低速值已核对为原 XML 值而非解析错误：upstream lane 1 `[450,480)` 12.60 m/s、`[1500,1530)` 4.43 m/s，以及 downstream lane 1 `[1980,2010)` 4.91 m/s。前两项受插入/跨区间结算影响，第三项对应 detector 位置附近换道；它们不能单独证明拥堵。
- `_r2` 的 `speed_valid` 只表示 E1 有贡献且原值非负，不表示交通状态解释有效。原值未删除、未替换为 FCD，也没有增加低贡献自动排除阈值。

工程证据与解释合同详见 `docs/STAGE2_G1_V2_ENGINEERING_REVIEW.md`。因此，E1 的记录提取通过，但“常规上游断面状态”用途的实际覆盖失败。

### 匝道供给与合流

- 300 辆 R 均有唯一的 FCD 相邻样本括号：`:freeway_merge_0_0 at t → main_down_0 at t+1`。事件时间只能表示 `(previous_label, first_downstream_label]`，不是精确物理 crossing time。
- 四个事件的 1 s 括号触及 30 s 边界，已标 `boundary_30s_ambiguous=True`，没有强行分配到某个精确 E1 interval。
- 首个/末个 R 首次下游观测标签为 68/2373 s。1500 s 前仅 36/300 辆首次在下游被观测；1800 s 前为 153/300，2100 s 前为 231/300，2400 s 前为 300/300。
- 计划需求、实际入网和合流通过是三个不同事件。既有完整 cohort 账目显示 R/U 分别有 150/75 辆在 1500 s 以后才入网；最后实际入网 2245 s，最后到达 2401 s。不能用请求 qRamp、R 入网数或上下游 E1 差值代替同期匝道合流流量。

这些记录支持“本轨迹存在严重的匝道/城市侧供给延迟，并在需求结束后继续释放”的描述。它们不证明该延迟的唯一原因、不构成反事实城市损失，也不建立匝道容量或 capacity drop。

## 3. 对主线/合流问题的回答

| 解释框架 | 本轮判断 | 依据与限制 |
| --- | --- | --- |
| H1 主线观测较通畅、匝道受限 | **部分支持** | 主线声明 lane 无技术停驶样本，而 R 合流与入网明显延迟；但上游 E1 状态用途失败，不能升级为“主线自由流已证明”。 |
| H2 主线存在局部拥堵 | **未建立** | E1 低速尖峰受到插入/换道测量语义影响；没有批准的局部拥堵/breakdown 定义。未建立不等于证明不存在。 |
| H3 覆盖或辨别证据不足 | **成立，限上游断面状态** | origin 与 detector/插入边界重合，缺少可靠的 mainline-only 连续通过测量；已有 FCD 可描述采样车辆，不能完全替代断面 flow/occupancy。 |

最强结论是：本轨迹清楚显示匝道与城市侧积压和延迟释放；当前观测不能可靠判断 Robert 所关心的主线 breakdown/capacity-drop。继续按旧对角矩阵增加第二 seed 不会修复这一测量缺口。

## 4. 三阶段时长判断

| 时段 | D4 判断 | 置信度 |
| --- | --- | --- |
| 0 s warm-up | `retain_for_this_exploration`：研究对象是从空网开始的加载过程，保留早期 46、192、412/414 s 事件；不声称稳态。 | Moderate |
| 1500 s demand | `retain_for_this_exploration`：已覆盖匝道、共享道和网外等待的发展；不能证明对其他条件或主线 breakdown 足够。 | Moderate |
| 1200 s post-demand | `retain_for_this_exploration`：本轨迹在 2700 s 截止前完成；只作为共同最大观察预算，不保证未来条件清空。 | Moderate |
| B `[300,1500)` | 保留为同轨迹切窗敏感性；不是独立运行、预热验证或持续时间试验。 | High（用途定义） |

1500 s 后仍有之前计划的车辆入网，因此 post-demand 不是零入流恢复阶段。需求停止后的出流变化不能自动解释为 capacity drop。现有证据没有要求立即改变三阶段秒数，也没有证明其对未来条件的充分性。

## 5. 验证与科学审查

- 14 项专用标准库 unittest 通过；只覆盖新离线解析、时间/缺值/重复/加权、合流括号和解释标记，不调用仿真。
- 独立核验逐字段对账 360 个 E1 interval、300 辆 R 的 600 个原始 FCD 括号端点；科学审查另抽查 8 个原始 FCD 时点、112 个 lane×M/R 计数及停驶数，差异为 0。
- 四张 `_r2` CSV 与首版逐字节一致；解释修订只增加结构化限制、测试和图注。图表已做数据来源与视觉检查。

科学 reviewer 最终五项结论：目标定义 passed；实际覆盖 failed（仅常规上游断面状态用途）；遗漏/重复 passed；独立对账 passed（仅记录提取）；回归保护 passed（仅现有离线合同）。这些状态不能合并成“科学测量全部通过”。

## 6. Historical D7 proposal：mainline merge-entry observation-only 修复

本节提案已由用户批准并完成定点 S3–S5。以下文字保留批准时的设计和停止边界；实际实现、运行、数据与科学验收见 `docs/STAGE2_S3_S5_VALIDATION_REPORT.md` 和 `docs/STAGE2_S3_S4_ENGINEERING_REPORT.md`。实际 SUMO 启动 1 次、重试 0；internal-lane E1 已在本项目 SUMO 1.26.0 成功加载。

目的：在保留 `departPos=last` 的需求实现机制下，获得不受 origin 插入重合影响的 **mainline-only 合流节点通过测量**。它不是更上游 feeder 状态，也不自动解决 breakdown 定义。

### 精确拟议差异

在 `config/scenarios/minimal_uncontrolled/scenario.add.xml` 保留全部旧 detector，并拟新增：

```xml
<inductionLoop id="mainline_merge_entry_e1_l0"
               lane=":freeway_merge_1_0"
               pos="4.32" period="30"
               file="mainline_merge_entry_l0.xml"/>
<inductionLoop id="mainline_merge_entry_e1_l1"
               lane=":freeway_merge_1_1"
               pos="4.32" period="30"
               file="mainline_merge_entry_l1.xml"/>
```

两条 internal lane 各长 8.64 m、只承载 M；4.32 m 是其技术中点，不是研究参数。R 使用独立 `:freeway_merge_0_0`（12.60 m）。旧 upstream E1 保留用于历史兼容，但标为 `origin_insertion_contaminated`，不用于主线拥堵判断。

Runner 拟只增加：两个 detector 的 ID/lane/position 静态与编译检查、runtime 输出路径重写、输出完整性检查，以及独立 `mainline_merge_entry` 汇总组。不得混入旧 upstream/downstream 组，不改变 network、route、demand、seed、TLS、车辆行为或仿真逻辑。

### 拟议配对验证运行（当前未授权）

- qMain/qRamp/qUrban/qX=3200/720/360/180 veh/h；seed 17；0/1500/1200 s；无控制。
- 参考 `/private/tmp/minimal_uncontrolled_8egb0qb1`。
- 交通语义回归要求 FCD 2700 个 timestep、tripinfo 1858 个记录、TLS 2700 个记录、vehroute 的 ID/route/depart/arrival、旧四 E1 各 90 interval 均与参考差异为 0。
- 新两 E1 各需 90 个 interval 覆盖 `[0,2700)`，ID/lane 正确且无缺失；另核对路线拓扑只允许 M 通过，并将聚合 `nVehContrib` 总量与完成 M 总量的关系明确解释。普通 E1 interval 没有 vehID，因此逐车成员资格、零遗漏和零重复仍为 `not_verified`；不能仅以贡献总量=1333 证明逐车覆盖。1 Hz FCD 可能漏采 8.64 m 短 internal lane，不能把 internal-lane FCD ID 集合当完整名单，也不能要求新 E1 逐 interval 等于 FCD 样本。

启动预算提案：正常配对探索运行 1 次；仅定位到 detector 加载/写盘技术故障时允许同参数重试 1 次；总启动上限 2。无 GUI、TraCI probe、其他 seed 或其他需求点。

停止条件：SUMO 拒绝 internal-lane E1、输出/区间覆盖不完整、交通语义回归不为 0、新 warning/teleport/collision/route error、或新 E1 contributions 无法与 M 路线拓扑和聚合车辆量形成一致解释。90 个 interval 只证明输出时间覆盖，不自动证明短 internal lane 上的 detector 测量有效。只有定位到纯 detector 配置/写盘故障才可使用一次重试；不得移动 detector 或改拓扑直至“通过”。

批准前的技术与科学提案审查置信度为 Moderate。实际运行后，声明断面覆盖、聚合独立对账和回归保护通过；逐车遗漏/重复仍为 not_verified。若未来必须测真实 feeder upstream 状态，仍需另提新增 feeder edge 的结构变更，因为它会改变路段、储存和旅行时间。

**用户于 2026-09-09 批准本提案进入定点 S3–S5。** 授权范围是上述 detector 修改、必要测试、一次匹配探索运行及最多一次纯技术故障同参数重试、数据分析与科学审查；不批准新需求点、其他 seed、旧六行矩阵、ALINEA 或正式实验。

## 7. 产物

- 分析入口：`src/analysis/build_stage2_g1_diagnostic.py`
- 专用测试：`tests/test_stage2_g1_diagnostic.py`
- 审查后数据：`data/processed/stage2_g1_v2_20260909_r2/`
- 审查后表格：`results/tables/stage2_g1_v2_20260909_r2/`
- 审查后图：`results/figures/stage2_g1_v2_20260909_r2/mainline_timeline.png`
- 工程测量审查：`docs/STAGE2_G1_V2_ENGINEERING_REVIEW.md`

Stage 2 与 G2 均未标为完成；正式实验协议、研究阈值及导师确认状态没有变化。

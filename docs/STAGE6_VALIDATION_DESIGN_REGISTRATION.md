# Stage 6 B：H2 验证设计注册草案

日期：2026-09-13  
状态：**User-approved for bounded Stage 6 validation design；C00–C02/SG6-L complete**  
机器卡：`data/processed/stage6_obstacle_20260913_v1/validation_card_draft_revision_03.json`  
机器卡 SHA-256：`d0ef6270f5bdd687621ab3513e9ba533c979a6ea37dbd9e8efd268b5234d1dfb`

## 1. 要验证的问题

当前主线车辆虽然声明使用约 1.4 km 的 `main_up`，但历史 16,622 辆 M 实际只在合流前 0.10–286.75 m 进入。Stage 6 B 只注册一个补救候选：在不改变路网、合流路权、驾驶行为、信号、匝道储存和需求生成规则的情况下，让 M 从现有上游道路的固定位置进入，并真实经过登记的上游形成区。

本验证回答：修正实际入口和观测域后，同一个无控制候选版本是否能在有限条件中同时观察到可解释的主线受损、R 实际通行以及 R/U 共享区暴露。它不检验控制收益，不定义正式 Breakdown/Capacity Drop，不证明纯因果城市损失，也不冻结论文指标。

## 2. 唯一候选与固定项

| 项目 | 注册草案值 |
| --- | --- |
| V0 历史背景 | M `departPos="last"` |
| V1 候选 | 仅 M `departPos=100 m` |
| 上游科学主域 | V1 `main_up [200,1200) m`，两条 M lane |
| 跨版本背景域 | `main_down [100,700) m`，只统计 M 身份 |
| 插入其他属性 | `departLane="best"`，`departSpeed="max"` |
| SUMO选项 | `extrapolate-departpos=false`；非法位置 warning 必须失败关闭 |
| 固定因素 | 原 nod/edg/con/tll、compiled network、routes、vTypes、跟驰/换道、合流连接和路权、R/U/X 插入、TLS、存储、step-length |

100 m 是透明、位于现有 lane 内的探索性选择，留下约 1,294.87 m 上游行程；没有证据表明它最优。50/200 m 不构成扫描点，也不能在结果不理想后替换。

位置 0.02 m 只作为配置与输出比较容差，不表示物理测量精度。1 Hz FCD 过界保留相邻帧时间括区，不宣称 0.01 s 事件分辨率。

## 3. 条件、种子与时间

| 轴 | 注册草案 |
| --- | --- |
| reference | ML：M=1083、R=300、U=150、X=75；名义 qMain=2600、qRamp=720 veh/h |
| challenge | C：M=1333、R=300、U=150、X=75；名义 qMain=3200、qRamp=720 veh/h |
| seeds | 17、23；全部保留，不按结果换 seed |
| V0 | 复用 ML17/23、C17/23 四条历史档案，仅作 seen background |
| V1 | ML/C × seed17/23，共四条新候选运行 |
| demand | `[0,1500) s` |
| observation | `[0,2700) s` |
| primary B window | `[300,1500) s`，20 个固定 60 s 半开区间 |

V0 没有真实经过 V1 feeder，不能用 V0 下游结果代替 V1 feeder 主判。V1 的四条数据才提供前瞻新信息；17/23 已经用于历史版本，因此结论仅限于这两个预选 seed，不构成独立随机 holdout 或统计功效保证。

## 4. 数据和 reference 资格

每个 V1 ML seed 必须同时满足：

1. B 窗至少 500 辆确定属于 cohort 的 M，每个 60 s bin 至少 20 辆；
2. feeder 前半窗 `[300,900)` 与后半窗 `[900,1500)` 的 vehicle-label 加权均速满足 `abs(v_late/v_early - 1) <= 0.05`；
3. 20 个 bin 均速的 sample SD/arithmetic mean `<=0.05`，sample SD 使用 `ddof=1`；
4. 不删除瞬态 bin，也不要求相邻 bin 变化不超过 5%；
5. 通过只表示有限 reference 可比较，不表示自由流或严格平稳。

M 入网资格逐逻辑运行检查：计划 M 全部纳入身份账目、全部实际 `depart<1500 s`、报告的最大 `departDelay<=1.01 s`。这个阈值命名为“预注册最大入网延迟资格”，不能解释为严格证明没有错过最早可插入步。number-flow 的精确量化排程算法仍为 `pending_C`，不得用名义公式代替实现核验。

如果配置和输出完整但固定入口造成注入不足或新入口瓶颈，结果是有效的 `not_resolved`，不能作为技术错误重试。只有来源、身份、时间网格、关键观测或解析错误才可记 `blocked_by_evidence_error`。

## 5. 主判、佐证和共同 180 s 支持块

主判按同 seed 比较 V1 feeder 全 B 窗的保守 M 行程时间区间：

```text
V1_C_mean_TT_lower > 1.10 × V1_ML_mean_TT_upper
```

同时必须存在同一个连续 180 s 支持块，由三个完整、合格、无间断的 60 s bin 组成，并全部满足：

- 每个 bin 的 V1 C/ML feeder M 加权均速比 `<=0.95`；
- 三个 bin 的确定 R 进入 `main_down` passage 总数至少 10；
- 每个 bin 至少一个确定 R passage；
- 每个 bin 都实际观察到共享区 R 与 U 同时技术停止的标签；
- 同时报告 feeder 积存、进入/离开、技术停止、未完成，R 路径停止分布，U 暴露车辆数/持续量，TLS movement 上下文及端点。

该城市侧门只确认同一时间块内反复可观察的共享暴露，不设没有依据的“每 bin 10 个 R/U 标签”门，也不证明纯因果 U 损失。

## 6. 模糊边界和截尾

- crossing 保留 last-below/first-at-or-above 时间括区；每辆 TT 为 `[max(0,end_lower-start_upper), end_upper-start_lower]`。
- 确定 cohort 与边界模糊 cohort 分开；用最不利的纳入/排除和排序组合计算总体上下界，并保留达到极值的实际分母。
- 观察结束仍未离域时，上界为 `+∞`；下界使用该车最后一次确认仍在终断面上游的有效样本时间减去 start upper。最后 FCD 标签为 2699 时不得自动使用 2700。
- 只有额外可追溯端点证据才能延伸确认时间；身份无解释消失是证据错误，不自行视为右截尾。
- reference 上界无穷或保守比较不能建立时，结果为 `not_resolved`，不得只分析完成车辆来获得通过。

## 7. 预登记敏感性

以下 7 个单因素变化分别对 V1 seed17/23 形成 14 个 required keys；其余规则保持不变：

1. TT ratio=1.05；
2. TT ratio=1.15；
3. speed ratio=0.90；
4. speed ratio=0.98；
5. M persistence=240 s，内部仍须有原 R/RU 180 s 支持块；
6. reference half-change≤3%、CV≤4%；
7. reference half-change≤7%、CV≤6%。

14 项必须全部保持支持；任一不支持、无法判定或 seed 不一致，整体为 `not_resolved`。这是严格的有限鲁棒门，不是正式统计样本量设计。

## 8. 固定分母

- 主规则：352 keys；150 applicable；148 required；202 not applicable。
- 其中四类技术门 128 required，V1 feeder 四类科学门 8 required，V1 ML reference 2 required，M inlet 8 required，RU 4 applicable/其中 V1 两项 required。
- V0 四个 feeder 科学 rule 全部 NA；V0/V1 公共下游背景另列 32 行，不填进不存在的 feeder 主判。
- 14 个敏感性 required keys 单独登记，不混入 148。
- 取消、失败或缺失不会缩小预登记分母。

## 9. 预算草案与实现边界

若 V0 四条合法复用，建议新 SUMO 上限 6 次：V1 smoke 1、V1 四条验证 4、全局同参数技术重试 1。每次 SUMO 进程墙钟上限 120 s，总 720 s；每 attempt 原始归档上限 2 GB，总 12 GB。TraCI/GUI 为 0。

现有路网可由 V0/V1 共同复用，B 不需要 netconvert。未来是否复用已编译网络、是否需要一次受控构建及精确 netconvert 预算必须在 C 工程实现后写入 SG6-BUILD/SG6-P 包；本注册不授权任何构建或运行。

## 10. B 阶段结论和下一门

科学审查已对 revision_03 给出 PASS，开放 Blocker/Major/必要 Minor 为 0/0/0。工程 argv、实现源码 hash、materialization、compiled-network绑定、number-flow 量化核验、失败模式 fixture 和独立验证器仍为 `pending_C`；`launch_eligible=false`。

用户已明确接受上述具体科学注册值并授权 C00–C02 离线实现。C00–C02 已完成并通过 SG6-L；该批准不包含 netconvert、SUMO、TraCI、GUI、正式实验协议或 SG6-R 接受。C03 随后确认可直接复用既有 compiled network，netconvert 计划/实际为 0/0。下一步仍须单独批准 C04/SG6-P 离线准备，最终启动卡形成后再决定是否运行。

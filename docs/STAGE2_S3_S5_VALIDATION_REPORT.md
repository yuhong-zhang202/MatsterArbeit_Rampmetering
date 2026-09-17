# Stage 2 targeted S3–S5 validation report

日期：2026-09-09。状态：**Completed；exploratory measurement validation，不是 Stage 2 完成或正式论文证据。**

## 完成范围

用户批准的定点 S3–S5 已依次完成：

1. S3 在 M-only internal merge lanes `:freeway_merge_1_0/1` 中点 4.32 m 新增两个 observation-only E1，并补 source/runtime/compiled topology/output 验证与测试；
2. S4 以 qMain/qRamp/qUrban/qX=3200/720/360/180 veh/h、seed 17、0/1500/1200 s 执行一次匹配探索运行；
3. S5 对新 E1、配对交通记录和分析窗口作独立数据核验与科学审查。

实际 SUMO 启动 1 次，技术重试 0 次。没有 GUI、TraCI probe、其他 seed 或需求点。运行目录为 `/private/tmp/minimal_uncontrolled__5s3s06d`。

## S3–S4 工程结果

| Detector | Lane | position | period |
| --- | --- | ---: | ---: |
| `mainline_merge_entry_e1_l0` | `:freeway_merge_1_0` | 4.32 m | 30 s |
| `mainline_merge_entry_e1_l1` | `:freeway_merge_1_1` | 4.32 m | 30 s |

两条 compiled lane 各长 8.64 m、只承载 `main_up → main_down` 的 M；R 使用独立 `:freeway_merge_0_0`。旧 detector 全部保留，旧 upstream 组标为 `origin_insertion_contaminated`。

运行成功，SUMO/netconvert 均为 1.26.0；warning、error、collision、teleport、emergency braking 和 route error 均为 0。FCD 2700 timestep、tripinfo 1858 records、TLS 2700 records、vehroute 1858 records 和旧四个 E1 各 90 interval 与参考 `/private/tmp/minimal_uncontrolled_8egb0qb1` 的语义比较差异均为 0。因此本次新增观察没有改变记录到的配对交通。

## S5 数据结果

| 窗口 | nVehContrib | 两 lane 合计 flow (veh/h) | 贡献加权 speed (m/s) |
| --- | ---: | ---: | ---: |
| Full `[0,2700)` | 1333 | 1777.333 | 30.8735 |
| A `[0,1500)` | 1331 | 3194.4 | 30.8728 |
| B `[300,1500)` | 1066 | 3198.0 | 30.8290 |
| Post `[1500,2700)` | 2 | 6.0 | 31.30 |

- 两 detector 各有 90 个连续 interval；全程 nVehContrib/nVehEntered 分别为 715/715 和 618/618，合计 1333。
- M 计划、实际入网、最终完成均为 1333。聚合数一致支持本次断面的可行性，但普通 E1 不提供 vehID，不能证明逐车零遗漏/零重复。
- 1 Hz FCD 在两条 8.64 m internal lanes 上只采到 321 个 M IDs，不能作为完整逐车名单。
- 78 个无贡献 interval 的速度保留为缺值；有贡献记录没有负速度。有效 interval 最低速度为 lane 0 的 25.94 m/s、lane 1 的 30.52 m/s。未设置或反推拥堵阈值。
- A 与 B 的聚合流量/速度相近只描述本轨迹，不证明稳态、容量或时长充分性。Post 仅两个贡献，31.30 m/s 不能代表持续交通状态。

## 验证

- simulation-engineer 静态/离线测试 9 项通过；data-analysis 专用测试 4 项通过；主代理组合复跑 13 项通过。
- S5 独立读取原 XML，对账 180 行 × 7 字段，并重算两 lane × 四窗口的贡献、合计流量和贡献加权速度。
- 工程全量交通语义比较保存在 `docs/STAGE2_S3_S4_ENGINEERING_REPORT.md`；S5 另抽查 5 条 trip 完整属性及 9 帧 FCD。
- 来源与登记产物 hash 保持不变；没有生成重复图表。

## 科学审查

| 检查 | 最终状态 |
| --- | --- |
| 测量目标 | Passed |
| 实际覆盖 | Passed，限两条 M-only internal merge-entry 断面 |
| 遗漏/重复 | Interval coverage passed；逐车完整性 not_verified |
| 独立对账 | Passed，限聚合结果与交通记录不变性 |
| 回归保护 | Passed，限本次测量合同 |

scientific_reviewer 未发现需要再次运行或修复才能关闭的 Blocker/Major，接受本次聚合通过测量可行性。置信度：High（本次技术验收），Moderate（推广到后续探索）。

不能从本次结果推出：真实 feeder 上游排队状态、逐车 detector 完整性、主线容量、Breakdown、Capacity Drop、因果城市损失、统计稳健性或 sweet spot。旧 upstream E1 仍受 `departPos=last` 插入污染。

## 三阶段与下一步

0/1500/1200 s 可继续作为下一份探索方案的候选，置信度 Moderate：0 s 保留空网加载，1500 s 覆盖本轨迹的积压发展但未证明足以观察主线 breakdown，1200 s 只是在本轨迹足以完成的截止预算。Post-demand 仍有延迟入网，不能称零入流恢复；B 仍只是同轨迹切窗。

定点 S3–S5 技术里程碑完成，但整个 Stage 2 未完成。下一步应先制定一个有边界的需求探索方案，明确区分“主线负荷不足”和“匝道/城市侧供给限制”，避免同时沿对角线改变 qMain/qRamp。具体需求点、seed、运行预算与判断规则仍需用户批准；本报告不选择或授权它们。

## 产物

- 工程报告：`docs/STAGE2_S3_S4_ENGINEERING_REPORT.md`
- 运行 summary：`/private/tmp/minimal_uncontrolled__5s3s06d/summary.json`
- S5 分析入口：`src/analysis/validate_internal_e1.py`
- S5 专用测试：`tests/test_internal_e1_analysis.py`
- S5 数据与 manifest：`data/processed/stage2_g1_internal_e1_validation_20260909/`
- S5 表格：`results/tables/stage2_g1_internal_e1_validation_20260909/`

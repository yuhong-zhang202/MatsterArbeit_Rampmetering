# Stage 2 G1 v2 engineering measurement review

日期：2026-09-09。范围：D1 与 D5 定点技术核查；只读，未执行 SUMO、netconvert、TraCI 或 GUI。

## 来源与空间合同

- 运行：`/private/tmp/minimal_uncontrolled_8egb0qb1`，SUMO 1.26.0，seed 17，需求 `[0,1500)`，截止 2700 s。
- 上游 E1 位于 `main_up_0/1` 终点前 1 m，即 lane position 1393.87 m；两车道长 1394.87 m。
- 下游 E1 位于 `main_down_0/1` 起点后 100 m；两车道长 796.49 m。
- R 合流路径为 `ramp_accel_0 → :freeway_merge_0_0 → main_down_0`；R internal via lane 长 12.60 m。8.64 m 属于主线 internal lanes `:freeway_merge_1_0/1`。
- 运行使用 `departPos=last`、`departLane=best`、`departSpeed=max`。现有 vehroute 没有 exit-times。

以上均由实际 `network.net.xml`、`demand.rou.xml`、`scenario.add.xml`、`scenario.sumocfg` 和输出核对；输入 hash 记录在 `data/processed/stage2_g1_v2_20260909/manifest.json`。

## 三处 E1/FCD 差异

`results/tables/stage2_g1_v2_20260909/e1_native.csv` 与原始 E1 XML 逐字段一致，以下不是 CSV 解析错误。

1. `merge_upstream_e1_l1 [450,480)`：原 E1 为 nVehContrib=8、nVehEntered=8、speed=12.60 m/s、occupancy=23.41%。同 lane 的 1 Hz FCD 最低为 29.63 m/s。至少六辆主线车直接在 lane position 1394.77 m 插入，即位于 1393.87 m detector 下游约 0.9 m；FCD 首见速度为 29.63–37.44 m/s。该 detector 的贡献受插入位置重合影响，12.60 m/s 不能解释为上游车流速度。
2. `merge_upstream_e1_l1 [1500,1530)`：原 E1 为 nVehContrib=1、nVehEntered=0、speed=4.43 m/s。`M_flow.1332` 在 1499 s 于 position 1394.77 m 插入，FCD speed=32.72 m/s；1500 s 已在 `main_down_1`，speed=31.59 m/s。贡献跨区间结算且插入在 detector 下游；4.43 m/s 不能作为 post-demand 主线低速证据。
3. `merge_downstream_e1_l1 [1980,2010)`：原 E1 为 nVehContrib=1、nVehEntered=1、speed=4.91 m/s。`R_flow.200` 在 1986 s 位于 `main_down_0` position 83.48 m、speed=19.74 m/s，1987 s 换至 `main_down_1` position 104.60 m、speed=21.13 m/s。车辆在 detector 位置附近换道；E1 通过测量与离散 FCD 纵向快照语义不同，4.91 m/s 不能证明 lane 1 拥堵。

## 解释合同

- 原始 E1 值、nVehContrib 与 nVehEntered 必须保留，不按自动低贡献阈值删除或改成 FCD 数值。
- `speed_valid` 只能表示 E1 有贡献且原值非负，不表示该值是有效的主线交通状态估计。
- 上游 E1 与 route origin/车辆插入位置重合，不能当作常规上游断面状态测量；其 flow/speed/occupancy 只能作为原始 detector observation 并披露插入覆盖限制。
- 下游换道点的单车低速贡献同样不能自动解释为拥堵。
- 这些事实不证明 E1 实现有缺陷，也不证明主线没有局部拥堵；它们限制可以从 E1 尖峰推出的结论。

## R 合流采样事件

新表的合同是：前一样本位于 `ramp_accel_0` 或 `:freeway_merge_0_0`，首次下游样本位于 `main_down_*`。300 个 R 事件均为 `:freeway_merge_0_0 at t → main_down_0 at t+1`；四个事件触及 30 s 箱边界并明确标歧义。事件时间只能写成 `(previous_label, first_downstream_label]`，不是精确物理过断面时刻或 E1 流量。

结论：解析表不需修正；持久诊断、图注和最终报告必须加入上述测量解释限制后再由 scientific_reviewer 复核。置信度：High。

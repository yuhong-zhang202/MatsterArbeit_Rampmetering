# Stage 2 targeted S3–S4 engineering report

日期：2026-09-09。状态：**S3–S4 completed；exploratory measurement validation，不是正式实验。**

## 授权与实现

用户批准 `docs/STAGE2_G1_V2_DIAGNOSTIC_REPORT.md` 第 6 节提案。工程修改限于：

- `config/scenarios/minimal_uncontrolled/scenario.add.xml`：在 M-only internal lanes `:freeway_merge_1_0/1` 各新增 E1，ID 为 `mainline_merge_entry_e1_l0/l1`，position 4.32 m，period 30 s；旧 detectors 保留。
- `src/scenarios/run_minimal_uncontrolled.py`：新增显式映射、source/runtime/compiled topology/position/output 路径检查、六 E1 完整性检查、独立 `mainline_merge_entry` 汇总组，并将旧 upstream 组标为 `origin_insertion_contaminated`。
- `tests/test_minimal_uncontrolled.py`：新增 source 属性及 compiled topology 的离线验证。

网络、路线、需求、TLS、seed、车辆行为与插入设置未改变。

## 测试与运行

静态/离线测试：

```text
.venv/bin/python -m unittest tests.test_minimal_uncontrolled.MinimalUncontrolledScenarioTests
```

9 项通过；此命令未启动 SUMO。

唯一探索运行：

```text
.venv/bin/python src/scenarios/run_minimal_uncontrolled.py \
  --profile low --q-main 3200 --q-ramp 720 --seed 17 \
  --warmup-s 0 --measurement-duration-s 1500 \
  --demand-end-s 1500 --post-demand-clearance-s 1200
```

- 新运行：`/private/tmp/minimal_uncontrolled__5s3s06d`
- 参考运行：`/private/tmp/minimal_uncontrolled_8egb0qb1`
- SUMO/netconvert：1.26.0。
- 实际 SUMO 启动 1；技术重试 0；总预算未超出。
- 状态 completed；warnings/errors/collisions/teleports/emergency braking/route errors 均为 0；1858 辆全部出发并到达。

## 交通语义不变性

工程代理对实际 XML 记录作语义比较：

| 输出 | 参考记录 | 新记录 | 差异 |
| --- | ---: | ---: | ---: |
| FCD timestep | 2700 | 2700 | 0 |
| tripinfo | 1858 | 1858 | 0 |
| TLS state | 2700 | 2700 | 0 |
| vehroute ID/route/depart/arrival | 1858 | 1858 | 0 |
| 原四个 E1 | 各 90 interval | 各 90 interval | 0 |

这证明本次配对运行记录到的交通与参考运行一致，不证明所有未来 detector-only 修改必然无行为影响。

## 新 E1

| Detector | 时间覆盖 | nVehContrib | nVehEntered |
| --- | --- | ---: | ---: |
| `mainline_merge_entry_e1_l0` | 90 个连续 interval，`[0,2700)` | 715 | 715 |
| `mainline_merge_entry_e1_l1` | 90 个连续 interval，`[0,2700)` | 618 | 618 |
| 合计 | 完整 | 1333 | 1333 |

编译网络确认两 lane 各长 8.64 m、detector 位于 4.32 m，连接均为 `main_up → main_down` 且 `state=M`。聚合贡献与完成 M 总数 1333 一致。

普通 E1 XML 没有 vehID，因此逐 ID 零遗漏/零重复仍为 `not_verified`；不能仅由总量相等推断逐车完整性。1 Hz FCD 也不能为 8.64 m internal lane 提供完整车辆名单。本轮未触发任何停止条件，没有使用重试。

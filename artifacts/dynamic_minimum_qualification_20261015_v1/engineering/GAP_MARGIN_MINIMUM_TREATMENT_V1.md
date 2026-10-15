# 动态执行器：1.1 m 来源及最小处理建议 V1

**结论：现有 STOP 符合已审合同；没有发现本次间距计算的技术错误。额外 1.1 m 是地方工程裕量，不能当作 SUMO 官方必要安全距离。建议只评审一个最小新诊断合同：当前实测跟驰使用原 emergency9 的 getSecureGap 作为硬筛查底线，额外 1.1 m 继续完整记录但不单独触发 STOP；原始新绿灯准入、黄灯适用性及其他安全/UNKNOWN 门不变。此项尚未批准、未实现，不是已证明安全或取消安全监测。**

## 1. 当前范围及来源

本次只读工程调查，HEAD `ee5984024987e6cf7c6b2e571c083e06a9773a8b`，含已记录但尚未提交的事件刷盘修复。Stage6 既有结项不变，Candidate A NOT_QUALIFIED、A1 UNRESOLVED；正式协议 0 bytes，未冻结。最新直接指令不授权新 SUMO，也未批准替换安全合同。[USER_SCOPE_V1](../USER_SCOPE_V1.json)、PROJECT_STATE 顶部、DECISIONS D-018/D-019。

以下行号指当前实际文件；历史 Git 对象与当前相关文件全部逐字 SHA-256 相同。精确文件、Git blob、commit、官方缓存 SHA 在 [来源回执](GAP_MARGIN_SOURCE_PROVENANCE_V1.json)。未重复扫描 raw、复算已有间距或运行测试。

## 2. 1.1 m 的可核查历史链

1. **V8 已用作停车线前排队资格范围**：`artifacts/stage6_standard_metering_execution_20261003_v1/source_snapshots/runner_V8_27207f56e76e2724.py:194–196` 的 `queue_distance_to_stopline_m=1.1`。不能据此推断数值来自“1.0+0.1”或现实标定。
2. **V9 明确命名 fixed geometry margin**：同目录 `V9_ACTUATOR_REPAIR_CONTRACT.md:12–20` 要求 front 距停车线≤1.1 m、低速；followers 则检查 `stopline_distance >= 1.1+(v+a)*1+(v+a)^2/(2b)`。第20行明确这只是 engineering bound，不能复制完整跟驰或证明安全。`source_snapshots/V9_control.py:89–118,133–151` 实现相同含义。
3. **V10 将原停车线裕量复用到接收跟车条件**：`src/stage6_safe_actuator_v10.py:12` 注释“Reuse ... V9 guard margin”；`:78–100` 查询假定下一秒加速后的 follower speed、leader emergencyDecel；`:172–175` 增加 `gap >= secure_gap+margin`。这是从停车线/停车包络到假定下一步接收空间的用途扩展，不是官方推导。V9/V10 最早此次核实的发布 commit 为 `1be9568af215c4c8330f8b7d4332b70d4fe14065`；它是历史汇总发布，不能充当最初创设或批准日期。
4. **Candidate A 接收检查继承**：`scripts/candidate_a_qualification_20261008_v1/worker.py:64–75` 保留 internal 接收空间和 `secure+1.1`；commit `30e547cbca1fa7ef97a0c9b0e043b4d870a1ab98` 与当前字节一致。
5. **WAIT 版本明确、有意保留到当前后态**：`artifacts/candidate_a_native_receiver_wait_20261012_v1/design/MINIMAL_WAIT_DESIGN_V3.md:17–27` 明确区分假想加速查询与实际速度查询，同时要求 actual gap≥current secure+1.1，禁止为了 PASS 降裕量。`src/candidate_a_native_receiver_wait_20261012/receiver_wait.py:6,21–63,67–80` 对应实现；提交 `403094d6e82c65cf578e562bf4cf97ba3821eecf` 与当前字节一致。因此它是后来明确保留的项目合同，不是意外多写了 1.1，也不是本次新发现的单位/minGap bug。

**依据强度**：以上证明“从哪里继承、实际怎样执行”，不证明 1.1 m 数值必要或被现实标定。项目较早 `docs/development/CANDIDATE_A_SAFETY_CONTRACT_REASSESSMENT.md:26,41,64–72` 已明确其物理/官方最低距离地位未验证。此次有界调查未找到额外官方或校准依据；不声称穷尽所有历史材料。

## 3. 官方机制与当前检查的范围差别

版本固定 SUMO 1.26、pin `fa7df22d7f1c4ae245192ecc32410a49f1ffb2a3`，本次读取已有官方源码缓存：

- [MSCFModel.cpp:168–184](https://github.com/eclipse-sumo/sumo/blob/fa7df22d7f1c4ae245192ecc32410a49f1ffb2a3/src/microsim/cfmodels/MSCFModel.cpp#L168-L184) 按传入的速度、leaderMaxDecel 和模型 headway 计算 secureGap，没有项目额外 1.1 m。它是给定场景的模型查询，不是所有后态都必须满足的未来安全证明。
- [MSVehicle.cpp:3288–3299](https://github.com/eclipse-sumo/sumo/blob/fa7df22d7f1c4ae245192ecc32410a49f1ffb2a3/src/microsim/MSVehicle.cpp#L3288-L3299) 用 leader current apparentDecel 调用 followSpeed、限制计划速度；[Krauss.cpp:112–124](https://github.com/eclipse-sumo/sumo/blob/fa7df22d7f1c4ae245192ecc32410a49f1ffb2a3/src/microsim/cfmodels/MSCFModel_Krauss.cpp#L112-L124) 根据 safe-follow speed 和 next-speed 界选择运动速度。项目传 emergency9 是额外保守场景，不是 API 错误；本建议不改成 apparent4.5。
- [MSVehicle.cpp:3711–3727](https://github.com/eclipse-sumo/sumo/blob/fa7df22d7f1c4ae245192ecc32410a49f1ffb2a3/src/microsim/MSVehicle.cpp#L3711-L3727) 在原生黄灯下依据能否停车决定等待；这支持复用原生相位/跟驰责任，不认证当前配时，也不能删除黄灯/红灯监测。

原 V9 是“一秒 G 后立即红灯”的人为脉冲前置停车包络。当前执行器是原生 G/y/r 连续相位；前一车已跨线时，post 检查对象可变成下一辆仍在 storage 的排队车。`adapter.py:293–299` 对这个新 front 再调用 current_following；`:306–325` 另外独立核查真正 entrant 的 before/after，二者没有混用。**实现与后来的 WAIT 合同一致，但把原 margin 拒绝升级为原生车辆已危险，没有依据。**

现有1233事件与冻结原始失败保持：实际 entrant R4 的 before/after 检查通过，queued R5 因 gap 低于 secure+1.1 约0.02773 m 被拒；它仍高于同次 secure 查询值。没有据此创造“2.8厘米容差”，也不把原生事件计数0说成安全证书。[既有工程后审](../../cumulative_full_catalogue_followup_20261014_v1/engineering/native_execution_v2/UA_CUMULATIVE_FULL_DYNAMIC_S17_01/POST_ENGINEERING_REVIEW_V2.md)、同目录 `STOP_INPUT_DETAIL_V2.json`、`GAP_SOURCE_SUPPLEMENT_V2.md`。

## 4. 三个选项与推荐

| 选项 | 对已知失败的含义 | 最小性与限制 |
|---|---|---|
| 保持 secure+1.1 硬门 | 同帧仍 STOP；不应无修改重跑 | 合同不变，但不能从当前证据继续验证完整动态任务；不代表全 Candidate A 不可行 |
| **仅 current-following 的额外1.1改为 advisory；secure 硬底线保留** | 此已知帧不再因额外margin单独失败；后续未知 | **推荐送审**。原生负责运动、项目仍作保守数值筛查及实际事件监测；是明确的新诊断合同，不是“旧代码bug修复”或官方保证 |
| 新 readiness/红灯等待算法 | 已有 WAIT不能直接用于当前失败，因为它先要求 actual+margin PASS | 增加相位延后、C累积/应用ACK/周期边界处理，改变执行政策；没有证据保证延迟就会满足旧门，不宜作为硕士任务首选 |

保留 secure 硬底线本身也是工程诊断选择，不把它宣称为官方强制不变量。若之后因该底线或真实制动/接收/黄灯门 STOP，应如实区分原因，不能再次自动放宽。建议不是承诺新的 dynamic 一定通过。

## 5. 精确最小 patch sketch（仅提案，没有应用）

不直接修改受保护旧 WAIT helper 或原125源。若合同获批准，使用新诊断 helper/薄adapter seam，变动范围只含当前跟驰分类与对应独立审计/身份源绑定：

```python
# Keep exact same validated IDs, time, route/modes, actual speeds,
# getLeader net-gap convention, emergency9 query, finite/coverage guards.
base_pass = bumper_gap > 0 and gap + 1e-9 >= secure
legacy_margin_pass = bumper_gap > 0 and gap + 1e-9 >= secure + 1.1
# Always serialize both booleans and exact gap, secure, +1.1 requirement.
status = CURRENT_GAP_OBSERVED_WITHIN_BOUND if base_pass else STOP_CURRENT_GAP_BOUND_DENIED
margin_classification = 'WITHIN_LEGACY_MARGIN' if legacy_margin_pass else 'EXTRA_MARGIN_ADVISORY'
```

原 helper `receiver_wait.py:59–63` 是唯一谓词 delta；`:78–80` 的 WAIT 分类及 entrant-before/after 使用同一新明示 policy。原 prospective `worker.py:64–75` 与每个新G的 `adapter.py:158–162` 准入保持硬门；不把 `receiver.available=False` 改写为 True，不强制任何车辆速度、放行数或延长G。必须保留 fresh receiver、身份/模式/动力学/全人口、相位/链接/nextSwitch、local yellow、红灯新front过线、全body到尾、碰撞/teleport、严格NUM及正常离网末步/日志/EOF UNKNOWN STOP；已获批事件刷盘修复保留。当前代码不能靠一行全局 `MARGIN_M=0` 修改，因为那会失去历史常量/合同分层，且旧审计仍会硬拒绝。

需要的最小离线核对：真实已冻结失败输入的分类对照（不是新native观测）；低于secure、missing/nonfinite/wrong-ID/time及其它STOP共存均仍拒绝；margin-only分类不得绕过新G准入或entrant before/after独立检查；失败路径ACK事件可持久化且原错误保留；独立reader重算两个门。仅在审查和明确授权后准备同一新版本的一次300→750→900→300、end1296 bounded诊断；技术成功后才条件式一次短真实Feedback。**本轮不写实现、不测试、不制卡、不创建权限、不启动。** 不追求每秒零误差，核实原请求C、真实N、累积残差、应用延迟和partial/pending；没有依据的最终容差不自行补入。

## 6. 交付及停止点

本轮仅新增本报告和来源回执；所有历史原始失败、原安全合同、logging修复及正式协议保持。必要安全责任没有被此次报告自动重新批准。下一步由数据/科学审查本提案的可接受边界；未达成合同共识则报告当前限制，停止无效重试，不用等待算法或新矩阵绕过。

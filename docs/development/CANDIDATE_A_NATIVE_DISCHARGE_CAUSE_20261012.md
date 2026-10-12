# Candidate A 原生三周期放行缺额：最小原因分析

2026-10-12。仅分析已完成 WAIT_DIAG01_V2（300s）及 WAIT_BUDGET_W360_01（360s）；不运行SUMO、不调参、不修改结果或资格状态。

## 结论

已确认：每周期第二辆车静止排队、前端距计量线约8.502m，第一绿灯秒仍未移动。到3秒绿灯结束仍未到线，随后在黄灯向前并减速、在约1m前停下；前两周期的第二车直到下一绿灯首步才过线。每周期一辆的计数与FCD／TLS／ACK／过线记录一致，没有发现丢计数或程序硬性限一辆。

两个run的相关轨迹完全相同，以下三行各在两个run出现一次，合计六周期；不是六个独立随机重复。

| 绿起点(s) | 首车→次车 | 首／次车初始距线(m)及速度 | 次车G1／G2／G3后速度(m/s) | 次车G末剩余距线(m) | 实际N／名义E |
|---|---|---|---|---:|---|
|1200|R0→R1|约1.001／8.502，均0m/s|0／0.794／2.700|5.008|1／2|
|1224|R1→R2|约1.001／8.502，均0m/s|0／1.532／2.618|4.351|1／2|
|1248|R2→R3|约1.001／8.502，均0m/s|0／1.616／3.893|2.993|1／2|

计量线为ramp_storage_0末端204.49m、车辆前端进入internal的边界；停车位置约在其上游1m。过线只定位到1秒运动区间，不虚构亚秒时刻。R1／R2分别在(1224,1225]／(1248,1249]通过；R3截至1272未观察过线，不代表永远不能过线。

## 已确认事实与有限推断

[E来源工程核查](../../artifacts/candidate_a_native_discharge_cause_20261012_v1/ENGINEERING_CAUSE_REVIEW_V1.md)确认：contract明确标注nominal_n2为UNQUALIFIED_DISCHARGE_ASSUMPTION；E每完成周期累计2，24s来自3600×2／300。此为未验证名义放行映射，不是实际两车饱和能力。C／appliedC／E各6、N3、缺额3完整保留；不将E改成3制造达标。

事实链支持“排队起步／跟驰占用绿灯时间，3秒内移动距离不足，随后轨迹与黄灯停车相符”。黄灯不是额外保证放行窗口，官方说明可停车车辆会减速：[SUMO信号语义](https://sumo.dlr.de/docs/Simulation/Traffic_Lights.html#signal-state-definitions)。具体native分支、随机扰动与各因素贡献未记录，不能唯一归因于tau、模型或黄灯某行源码。

G末首车在internal移动，旧prospective接收谓词仍拒绝；次车实际当前跟驰gap则通过。这两个条件不同，不能把PASS改写成旧availableTrue或普遍安全。第一黄秒后旧接收检查已可用，但次车仍不越线，因此没有证据支持整个周期持续物理接收封锁是唯一原因。WAIT只有getter／分类，无车速／停车setter，无跳步或缩短绿灯。

## 最简单建议与是否再测试

为解释现有N3，不需新仿真。保留两车名义映射的UNQUALIFIED标记、原E/N/失败记录，停止用该映射保证300veh/h。短窗实际150veh/h只是描述，不是长期容量。

若后续目标仍为在当前300veh/h点验证两车包，值得另行批准一次单点技术测试：检验更长有效G能否让第二车到线；需先明确新的相位卡及比较条件，现证据不足以保证某个秒数即可成功。本轮不修改G/y/r、模型、guard或原合同，也不授权运行。现有n2、y3、最低r2在900veh/h要求周期≤8s，即G≤3s；延长G的300点测试不能自动取得300–900全范围资格，不应扩成矩阵或强制N2。

## 验证与交接

[六周期及300条精选轨迹报告](../../data/processed/candidate_a_native_discharge_cause_20261012_v1/MINIMUM_CAUSE_REPORT_V1.md)，[逐周期CSV](../../data/processed/candidate_a_native_discharge_cause_20261012_v1/SIX_CYCLE_SUMMARY_V1.csv)，[原始文件映射和哈希](../../data/processed/candidate_a_native_discharge_cause_20261012_v1/SOURCE_MAPPING_V1.json)。一次1.4s提取PASS、每run五个必要输入文件对冻结manifest SHA校验；数据10文件绑定e8b06e66…，两manifest990386cf…／61aae130…保留；原raw在独立工作区只读，未重跑全审计或测试。

[独立科学审查](../../artifacts/candidate_a_native_discharge_cause_20261012_v1/FINAL_SCIENTIFIC_REVIEW_V1.md)限定PASS、无必修finding：必要位置／速度和原N对账一致。新提取代码独立回归未验证，本轮直接数值核对及已有时间／计数保护不构成更广泛软件验证。下一位用户／Chat决定是否定义一个新单点技术任务；建议Proposed，不构成正式研究设计、协议变更或仿真授权。Stage6结项、A1 UNRESOLVED、Candidate A NOT_QUALIFIED、旧STOP3及所有失败保持。

# Candidate A 原生周期技术预算结项与交接

日期：2026-10-12。状态：技术诊断及最小实现已完成；按用户最新要求收敛剩余档位。没有完成四档全矩阵，也没有取得安全／服务资格或正式实验授权。

## 结论

采用300s现实时间上限作为本次已测试足够的最小技术预算。5分钟和6分钟两次诊断均完成首次受控黄转红、1207s耐久检查点、三个完整周期及1272s终点；两次实际监控清理均不到150s。用户明确允许足够预算已确认后省略剩余档，420／480s因此记为SKIPPED_BY_USER_CONVERGENCE，不是PASS或FAIL。300s不是绝对最优、普遍可靠下限，也不是要求运行满五分钟。

| 新等待处理诊断 | wall预算(s) | 监控至清理(s) | 整个CLI(s) | 1207／1272／完整周期 | C／applied C／E | 实际N |
|---|---:|---:|---:|---|---|---:|
| WAIT_DIAG01_V2 | 300 | 144.848700 | 145.409144 | 完成／完成／3 | 6／6／6 | 3 |
| WAIT_BUDGET_W360_01 | 360 | 135.124102 | 135.392720 | 完成／完成／3 | 6／6／6 | 3 |
| WAIT_BUDGET_W420_01 | 420 | 未运行 | 未运行 | 未观测 | 未观测 | 未观测 |
| WAIT_BUDGET_W480_01 | 480 | 未运行 | 未运行 | 未观测 | 未观测 | 未观测 |

耗时采用相同口径并列，非交付/审查总时长。较大预算没有被证明导致运行加快。共同31文件运行核心与规范化物理输入相同，完整源码快照不同；两次不是独立随机种子重复，也不是控制效果比较。未运行档不补零、不填写派生差值。

## 实现和验证范围

旧W300在1201s因POST_GREEN_RECEIVER_DENIED停止，未耗尽300s；它不是预算不足，也不是SUMO原生不安全的证明。旧源码、旧STOP3、失败与原始证据保留。新独立WAIT处理保留原prospective拒绝和1.1m裕量，只有绑定身份/模式/车辆覆盖/路线/时间/实际当前间距的正常等待可继续；未知或当前条件拒绝仍STOP，新周期准入严格保持。进入车辆前态拒绝／后态通过的漏STOP已最小修复：旧精确源回归FAIL保留，修复后11项PASS；原300s移植后3项针对性测试PASS。不得把它解释为修改生产guard或A1合同通过。

两个实际运行均有1272步FCD/TLS/ACK，三个唯一绿灯入口ID，每周期1辆，黄／红过线0且分别有9／54s真实曝光；G曝光9s。15条pre/post WAIT记录包含重复物理帧，不是15个独立等待事件。实际N3相对E6缺额3，72s平均150veh/h只是描述值，不能认定300veh/h长期服务资格。保留最后退出车辆制动覆盖缺口及父CLI兼容提示不在四流原生日志在线分类内的边界；本次原生运行没有故意注入危险，危险/未知STOP的反例来自离线验证。

## 可追溯证据

- [300s最小实现与实际诊断报告](CANDIDATE_A_NATIVE_WAIT_DIAGNOSTIC_20261012.md)：原生单次、72raw／69,002,098B，manifest990386cf…；预启动、实际工程/数据/科学及115文件最小移植证据。
- [360s工程运行后报告](../../artifacts/candidate_a_native_wait_budget_series_20261012_v1/runs/CA_NATIVE_PHASE_R300_S17_WAIT_BUDGET_W360_01/engineering/POST_ENGINEERING_REVIEW_V1.md)：单次CLI58178／SUMO58179；75raw／69,157,056B，manifest61aae130…，工程12文件绑定11bcad09…。
- [360s独立数据复核](../../data/processed/candidate_a_native_wait_budget_series_20261012_v1/runs/CA_NATIVE_PHASE_R300_S17_WAIT_BUDGET_W360_01/FINAL_DATA_REVIEW_V1.md)：26文件绑定634037ca…，真实主审计及补充PASS。清单schemaUNKNOWN、摘要字段KeyError与最小适配版本保留，未改raw或运行核心。
- [360s科学复核](../../artifacts/candidate_a_native_wait_budget_series_20261012_v1/runs/CA_NATIVE_PHASE_R300_S17_WAIT_BUDGET_W360_01/FINAL_SCIENTIFIC_REVIEW_V1.md)；[最终科学收敛审查](../../artifacts/candidate_a_native_wait_budget_series_20261012_v1/closing/FINAL_SCIENTIFIC_CONVERGENCE_REVIEW_V1.md)。
- [剩余档跳过及无启动核查](../../artifacts/candidate_a_native_wait_budget_series_20261012_v1/closing/SKIPPED_BY_USER_SUFFICIENT_MINIMUM_BUDGET_V1.json)：420／480两卡仍PREPARED_NOT_RELEASED，canonical授权/release/raw/消费记录均不存在。
- [最终73文件移植收据](../../artifacts/candidate_a_native_wait_budget_series_20261012_v1/transplant/TRANSPLANT_RECEIPT_V1.json)：2,455,812B，计划acf08a2f…，全部逐字节SHA一致；[最终目的地工程核查](../../artifacts/candidate_a_native_wait_budget_series_20261012_v1/transplant/DESTINATION_ENGINEERING_RECEIPT_V1.json)确认73文件／31共同核心／三卡依赖匹配、主历史CSV仍普通文件、无新主目录raw或权限。复用未变化源的既有配置测试，不为交付重跑SUMO。

完整raw与canonical已消费执行权限保存在独立工作区 `/Users/yuhongzhang/.codex/worktrees/native-receiver-wait/Masterarbeit-Ramp-Metering`；主目录提供可审查汇总、原始清单和哈希，不假称完整raw已在线提供。六历史CSV副本归档/引用仅在用户精确批准独立区执行，未移回其文件类型变化、恢复payload、raw、缓存或执行权限。卡片绝对路径与源码快照保留真实来源，复制仅历史证据，不构成主目录运行权限。

## 下一步交接

本轮结束进一步技术预算诊断。用户／Chat审查已交付最小实现及实际放行缺额，决定是否另立后续服务能力调查；此建议不构成执行授权，不因N不足自行调整G/y/r、guard、车辆模型或研究设计。Candidate A仍NOT_QUALIFIED、A1仍UNRESOLVED；Stage6既有结项及未冻结正式协议不变。本轮未新commit、push、发起PR或修改上游PR。

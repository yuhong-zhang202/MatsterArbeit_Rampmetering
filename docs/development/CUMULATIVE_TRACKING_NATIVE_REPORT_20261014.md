# 累计750请求跟踪：首次原生诊断结果

2026-10-14。**本次运行未完成：1272秒按黄灯UNKNOWN停止，未达到获批1296秒。** 第一组48秒的实际放行符合750请求，第二组未完成；整体跟踪任务、安全及服务资格均不能宣布通过。工程→独立数据→科学复核完成，限定允许交付失败及已观测前缀证据。

## 本次范围与实际执行

用户明确批准一次 `UA_CUMULATIVE750_S17_01`，不自动重试。执行源码为 `3e95c545fd63765d1c15489c943bd80a78f6fdd5`；固定原始请求750 veh/h，需求M3600/R900/U360/X180，seed17，步长1秒，控制从1200秒开始。750是控制请求，R900是匝道交通需求。

唯一当前卡SHA-256为 `c4464cd13b64a2eed0e9ea6143b16cac308562608426d6adc3023fa6b4b3fc3b`，111源摘要 `b351723aac24e5938ebd608be8b567a1d5d6e3527d22fc564049b4d8b306067b`。精确许可校验通过后仅启动一个SUMO子进程。使用T8/G4/Y2/R2和T10/Gmax5/Y3/Rmin2，严格NUM及全部安全/UNKNOWN停止门保持。

实际监控启动、循环及清理共173.949秒，启动连接18.330秒；均在300秒/60秒预算内。没有固定输出字节上限，要求保留5GB磁盘余量；未触发资源门。CLI退出1，原生子进程正常关闭且EOF退出0，后者不意味着运行目标通过。实际最后ACK和核账时刻均为1272秒。没有重试、修改代码、guard、模型、配时或正式实验设计。

依据：[直接用户授权](../../artifacts/cumulative_tracking_implementation_20261014_v1/USER_NATIVE_EXECUTION_APPROVAL_V1.json)、[实际执行receipt](../../artifacts/cumulative_tracking_implementation_20261014_v1/engineering/native_execution_v1/EXECUTION_RECEIPT_V1.json)、[工程报告](../../artifacts/cumulative_tracking_implementation_20261014_v1/engineering/native_execution_v1/POST_ENGINEERING_REVIEW_V1.md)。

## 实际放行是否跟上请求

C表示原始请求的时间积分；E只统计完整周期的计划配额；N包括全部已观测入口，不截断额外车辆，也不丢弃部分周期车辆。

|观测范围|完整周期|部分周期|C|E|N|可作出的判断|
|---|---:|---:|---:|---:|---:|---|
|1200–1248秒|5|0|10|10|10|10/10/8/10/10秒混合周期在本组实际实现10辆/48秒，即750 veh/h|
|1248–1272秒|2|1|5|4|5|末T8仅完成4秒绿灯、通过1辆；第二组未完成|
|1200–1272秒累计|7|1|15|14|15|C−N=0只是停止时的已观测前缀，不能代替两组完整验证|

全前缀的E−N=−1来自统计支撑不同：E排除部分周期配额，N保留部分周期实测入口；它不是超放一辆的证据。末包未实际进入黄灯或红灯，其相应过线计数为未观测/null；1272秒后的结果均未观测，不能补零。

成功的首个T8为1220–1228秒，实际相序`GGGGyyrr`、N=2。第二个T8从1268秒开始，仅观察到`GGGG`、N=1。它说明同一个短周期在不同车辆状态下不能仅凭先前成功就保证适用。

依据：[独立数据报告](../../data/processed/cumulative_tracking_implementation_20261014_v1/native_actual_v1/DATA_POSTREVIEW_V1.md)、[逐周期观测](../../data/processed/cumulative_tracking_implementation_20261014_v1/native_actual_v1/OBSERVED_CYCLES_V1.csv)。

## 停止原因：已确认与未确认

**已确认：** 1272秒准备首次转黄时，R_flow.15距离停止线0.1681315103 m，速度4.9879585746 m/s，车长5 m，正常减速度4.5 m/s²，动作步长1秒。新鲜车辆记录与FCD精度8结果一致，必要输入均存在且有限，不是字段缺失或资源问题。

保持不变的项目筛查计算：停车距离约7.752373 m，超过可用0.168132 m；车尾清空时间约2.556632秒，超过拟采用的2秒黄灯。两条可接受路径均未满足，触发 `UNKNOWN_LOCAL_YELLOW_SCOPE`。最后TLS/ACK仍为绿灯，该包被拒绝的黄灯运动没有执行。

**未确认：** 若继续转黄，SUMO原生车辆究竟会怎样反应。此次没有观察到该黄灯运动，不能称发生了黄灯违规、已证明原生红灯不安全，或T8在所有状态下均不可行。也没有证据把这次拒绝归类为可以直接删掉的检查误报。

依据：[绑定输入与代码分支复算](../../artifacts/cumulative_tracking_implementation_20261014_v1/engineering/native_execution_v1/STOP_INPUT_DETAIL_V1.json)、[独立快照复算](../../data/processed/cumulative_tracking_implementation_20261014_v1/native_actual_v1/PREFIX_AND_SCREEN_READBACK_V1.json)。

## 数据完整性和审查边界

绑定的实际审计器只调用一次，真实返回 **exit1 / STOP_OBSERVED_ALARM**，完整失败输出保留；没有修改审计器让结果通过。已观测前缀的连续TLS/ACK、15个全绿入口及车尾、1339个正常离网末步和最终EOF核对通过。观测最小速度差及原生加速度均为−4.5 m/s²；没有采用旧数值例外。末AFTER的非活动车辆池仍为单日志来源，未冒称全域独立验证。

原始161文件共426,650,300字节，保留在本机 `data/raw/cumulative_tracking_implementation_20261014_v1/UA_CUMULATIVE750_S17_01/`，不上传全部raw。清单SHA为 `cf38cadb8d17991c43ebcc40db784afc5227a9ff0f07e02bf33b3a9d6fbc15fe`。数据报告SHA为 `62924531c4f8fcd273805e1617412d93cd3964392f37716cd0d4b8b37b15b561`，绑定清单SHA为 `d847b00a81e2c50319278355bd7d3ece341169aca8710c85343734bd1de3a0de`。旧失败及历史raw均保留，本轮没有GitHub上传。

审查记录：[工程](../../artifacts/cumulative_tracking_implementation_20261014_v1/engineering/native_execution_v1/POST_ENGINEERING_REVIEW_V1.md) → [独立数据](../../data/processed/cumulative_tracking_implementation_20261014_v1/native_actual_v1/DATA_POSTREVIEW_V1.md) → [科学复核](../../artifacts/cumulative_tracking_implementation_20261014_v1/science/NATIVE_SCIENTIFIC_POSTREVIEW_V1.md)。科学结论为 `GO_FOR_OBSERVED_PREFIX_EVIDENCE_DELIVERY_ONLY`，没有新增证据交付Blocker或实质性Minor；保留一项 **Major：当前混合政策的持续适用性未成立**。此问题阻塞本次运行完成及长期跟踪主张，不阻塞失败证据归档。未通过放宽检查或重复原条件消除该问题。

## 最小下一步建议（未实施、未授权新运行）

累计选包及独立核账已得到一组真实混合周期支持；当前直接障碍是下一短包的黄灯适用性。应先用现有数据评估与当前检查兼容的周期选择，不继续调整输出预算或重复原运行。

工程提出待审候选：T9/Gmax4/Y3/Rmin2与T10搭配。当前失败快照满足3秒黄灯筛查；名义上2个9秒加3个10秒共48秒，可安排10辆。但这是快照与算术结论，**没有证明新时序下G4能实际放行2辆、未来每次筛查均通过或长期服务合格**。实现此候选需新目录、源码、卡片与审查，运行需另有明确许可；不能改写当前T8、旧900证据或已消耗身份。

完整300–900覆盖、同版本动态请求、真实ALINEA闭环及持续实际跟踪仍未完成。Stage6既有结项、Candidate A NOT_QUALIFIED、A1 UNRESOLVED及空/未冻结的正式协议保持。下一步建议不构成执行授权。

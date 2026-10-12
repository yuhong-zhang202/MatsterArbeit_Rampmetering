# Candidate A 原生信号等待处理：最小实现与真实诊断

日期：2026-10-12，Europe/Berlin。状态：独立运行及工程／数据／科学审查通过限定技术节点；最小新文件已移回，目的地一致性验证已通过。未取得安全、服务资格或正式实验授权；四预算比较尚未完整完成。

## 问题与最小解决方案

原 W300 在1201s停止：第一辆R进入内部车道后，observer换成下一辆静止车，并以“当前速度＋下一秒全加速”的假设计算接收条件。旧合同把该条件拒绝转为整个运行终止。实际前车占用与读数绑定正常，未发现采样错误，也未证明静止队列危险。

新独立 namespace 保留 observer、原拒绝、两项阈值及1.1m裕量，增加当前实际速度的完整跟驰查询。已激活绿灯中，身份、模式、路线、车辆覆盖、前车、间距和时间均已绑定且当前间距条件通过时，可以记录为条件性WAIT，继续由SUMO原生机制限制运动。未知、当前条件拒绝、实际异常仍STOP；新周期开始的严格准入保持。CLEAR仅覆盖有效fresh空前车查询及478.67m路径，不能表示无条件未来安全。

这属于用户明确授权的独立诊断语义修订。原生产guard、旧STOP3、旧实现和原始证据均保留，未改车辆模型、网络、G/y/r时长、需求、随机种子或正式研究设计。

## 实现、回归与版本记录

新源码：`src/candidate_a_native_receiver_wait_20261012/`；入口：`scripts/candidate_a_native_receiver_wait_20261012_v1/cli.py`；测试：`tests/candidate_a_native_receiver_wait_20261012/test_wait.py`。

预启动审查发现过一项漏洞：进入车辆的前态拒绝、后态通过可能漏STOP。修复后两侧只接受明确current-gap PASS或有限CLEAR；拒绝／未知保留前后观察、实际过线及核账后停止。精确保留的旧源码对同一组合实际FAIL，修复后11项离线测试PASS；独立数据反例核验也通过。数据检查器的历史路径／reason假设FAIL与修正结果保留，真实运行审计未发生解析修复。

[工程V2](../../artifacts/candidate_a_native_receiver_wait_20261012_v1/engineering/ENGINEERING_REVIEW_V2.md)；[数据预审V2](../../data/processed/candidate_a_native_receiver_wait_20261012_v1/FINAL_DATA_PRELAUNCH_REVIEW_V2.md)；[科学预启动审查](../../artifacts/candidate_a_native_receiver_wait_20261012_v1/PRELAUNCH_SCIENTIFIC_REVIEW_V2.md)。执行源是baseline `20e5e83ac059768320cdaa4c815d164e1022de45` 上的未提交、精确哈希快照，不能声称历史baseline已测试新代码。

## 一次真实诊断

身份：`CA_NATIVE_PHASE_R300_S17_WAIT_DIAG01_V2`；卡片SHA-256：`c6f8574a57396939b1b4be4c119041e78ce1f652050d5a621c6d121d8def10ac`。需求M3600/R900/U360/X180veh/h，名义控制率300veh/h，seed17、dt1s、G3/y3/r18。身份中的R300指控制率，匝道需求仍为900veh/h。

只启动一次SUMO，PID96903；CLI96902退出0，原生进程退出0。1207s强制耐久检查点通过后继续；1272s按既定终点结束，第四次绿灯事件未执行。监控至清理144.8487s、整个CLI145.4091s，低于300s上限。预算是最大允许现实时间，不要求运行满五分钟；此单次结果不能保证其他机器负载或更小预算。

| 完整周期 | 仿真区间 | C／applied C／E | 实际N | 相位 |
|---|---|---|---:|---|
| 0 | [1200,1224) | 2／2／2 | 1 | G |
| 1 | [1224,1248) | 2／2／2 | 1 | G |
| 2 | [1248,1272) | 2／2／2 | 1 | G |
| 合计 | 72s | 6／6／6 | 3 | G3／y0／r0 |

三个唯一入口ID为R_flow.0、R_flow.1、R_flow.2，每辆有独立前后状态；FCD／TLS／ACK逐步核账一致。G/y/r分别实际暴露9/9/54s，因此黄／红零过线是已观测零，区别于旧W300未观测黄／红。E−N=3；72s内描述平均放行为150veh/h，不能据此认定长期能力或300veh/h资格。旧字段24/48s表示未改变指令的request age，不是新控制命令延迟。

共15条条件性WAIT记录：6条前态、9条后态，包含重复物理帧，不是15次独立等待事件。首条真实记录保留原prospective secureGap2.6m与available=False；对静止R1的实际速度0m/s另行查询，返回secureGap0m，间距1.3163m满足原1.1m裕量。查询参数、结果、车辆与前车ID、模式、时间及路径均有记录。

覆盖范围内的制动最小值约−4.5m/s²，碰撞／teleport及红过线监测未见异常；完整原生四流最终EOF绑定通过。退出车辆最后运动仍不在共同before/after制动检查内；父CLI兼容性提示不属于四流在线分类。危险／未知STOP由已执行的离线负控验证，本次native没有故意制造危险。不得把本次无报警扩大为普遍安全证明。

[真实工程报告](../../artifacts/candidate_a_native_receiver_wait_20261012_v1/runs/CA_NATIVE_PHASE_R300_S17_WAIT_DIAG01_V2/engineering/POST_ENGINEERING_REVIEW_V1.md)；[独立实际数据核账](../../data/processed/candidate_a_native_receiver_wait_20261012_v1/runs/CA_NATIVE_PHASE_R300_S17_WAIT_DIAG01_V2/FINAL_DATA_REVIEW_V1.md)；[科学运行后审查](../../artifacts/candidate_a_native_receiver_wait_20261012_v1/runs/CA_NATIVE_PHASE_R300_S17_WAIT_DIAG01_V2/FINAL_SCIENTIFIC_REVIEW_V1.md)。72份原始文件共69,002,098B保留在独立工作区，manifest SHA `990386cf6d40d70b5f59d6754cde56555e7e7021f0910a8918373b19afb94199`。

## 资源处理与移植边界

初始磁盘余量不足以容纳已知输出。自动审批首次拒绝六个历史CSV重复副本改为引用，拒绝时零修改。用户随后明确批准清单SHA `9f8dffd24a5eee9be683128df3065c5eb6aa180851bff7ca3c5a6972697488a7`；仅独立工作区六副本在完整归档、CRC／解压哈希校验后改为主原件引用，回收138,223,616B。主原件与全部旧raw未改；符号链接不是操作系统写保护，本任务不写这些历史路径。后续系统余量跳至约15GB不能归因于此次138MB回收。

115份最小源码／测试／可审查证据（2,017,914B）已逐文件移回并核对哈希。没有移回六个历史表的类型变化、原始输出、恢复payload、缓存或canonical执行权限。独立工作区仍保留完整raw、归档与一次性权限；已消费c6卡片绑定独立绝对路径，复制到主目录仅作为历史证据，不能当作新主目录运行卡片。主目的地115文件、77来源绑定、旧59依赖及536保护文件均匹配；3项针对性离线测试实际PASS（1.332s）。已消费独立卡片的严格执行环境检查在主目录明确拒绝foreign runtime input，主目录没有新raw或canonical权限。主目的地依赖与针对性测试结果见[移植记录](../../artifacts/candidate_a_native_receiver_wait_20261012_v1/transplant/TRANSPLANT_RECEIPT_V1.json)。

## 结论与接手

已确认：本版本可在此一次诊断中处理暂时等待、完成原生三个周期，并准确记录实际3辆放行；离线危险／未知反例保持STOP。科学审查允许最小移植，目的地哈希、依赖及针对性测试验证已通过。

仍未证明：普遍安全、A1数学安全、长期服务能力、300veh/h资格、精确等待原因的唯一归因或正式控制效果。Candidate A仍NOT_QUALIFIED，A1仍UNRESOLVED，既有Stage6结项与未冻结正式协议保持。后续360s已单次完成并经三方复核；用户允许足够预算确认后省略剩余420/480s，已记SKIPPED。采用300s为已测足够最小预算，按用户最新收敛可结束技术目标，不称全四档已执行。见[预算结项与交接](CANDIDATE_A_NATIVE_BUDGET_SUFFICIENCY_CLOSEOUT_20261012.md)。下一步建议不构成正式实验或调参授权。

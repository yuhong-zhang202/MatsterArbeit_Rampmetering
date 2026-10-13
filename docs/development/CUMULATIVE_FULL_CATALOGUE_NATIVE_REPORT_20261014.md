# 完整周期库累计750：实际诊断报告

2026-10-14。技术诊断；正式实验协议仍为空且未冻结。工程、独立数据和只读科学实际后审均已完成，限定GO；无新增交付阻塞，持续适用性Major仍开放。既有 Stage6 结项、Candidate A NOT_QUALIFIED、A1 UNRESOLVED 不由此报告改变。

## 结论

**这次同一版本固定750请求的96秒观察中，真实放行跟上了原始请求：C=applied C=E=N=20。** 两个独立48秒区间各为10辆，没有以固定720的名义计划替代750原请求。结果支持有限时段的累计补偿机制；尚不能宣布全300–900实际能力、持续闭环跟踪或安全／服务资格。

原来的8/10混合运行在1272秒黄灯前置检查停止，仍是有效历史失败。新运行使用完整既有T8…24目录及T10 Gmax5/Y3例外，实际选择路径不同；不能将两个版本拼成一次连续成功运行，也不能据新结果否定旧UNKNOWN。

## 为什么运行及实现边界

此前固定T10虽实际14辆匹配名义720，仍低于原始750请求。首个累计8/10运行只完成第一组48秒，第二组遇到黄灯适用范围UNKNOWN。已有数据反事实筛查不能证明新轨迹，因此本次必要问题是：完整目录选择出的混合路径能否在不改安全门的情况下实际完成两组48秒。

新目录复用原有T8…24；T10保留已经实现的Gmax5/Y3/redmin2。C按原始请求积分，选择依赖真实C−N；完整包N≠2停止后续补偿。未改ALINEA公式、自身previous状态、30秒反馈时钟、车辆模型、种子、quota或strict NUM。候选目录扩大改变周期选择，不宣称轨迹与旧版本相同。

## 实际版本与操作

- 身份：`UA_CUMULATIVE_FULL750_S17_01`，一次启动，无重试。
- 实际Git HEAD为基线`3e95c545fd63765d1c15489c943bd80a78f6fdd5`；新增实现当时尚未提交，以125文件精确快照为测试版本，不能声称基线commit包含新代码。
- 卡SHA：`da64599b03875f92bb99a6d45691f5d918b9cc77420c0a0b755d3ef0acc5db8c`。
- 125源摘要：`c47879667efe4e92ae867353233b96ade1fb48d0cf879fdeed6b6921e86bab21`；canonical release：`eade38c9bb0d78d82eaef396a4aadd6a478843dd44b1251f42ea27ad7abcae0b`。
- M3600/R900/U360/X180，seed17，固定请求750 veh/h，控制1200至1296，dt1秒。`r_ALINEA=null`，本次不是反馈闭环。
- 资源：监控300秒、启动60秒、无固定输出字节门、实时剩余磁盘至少5GB。实际启动24.7884秒；监控启动／循环／清理188.2434秒。native自身计时163.199秒，是另一计时范围；未单独测量整个CLI用时。
- CLI57558、SUMO57577、session31100；CLI/native EOF均0，owned进程已退出。231次连接轮询属于同一子进程，不是231次SUMO启动。

真实启动命令见[执行receipt](../../artifacts/cumulative_full_catalogue_implementation_20261014_v1/engineering/native_execution_v1/EXECUTION_RECEIPT_V1.json)。卡与环境记录包含本地SUMO、Python及依赖绑定；本次没有重新安装依赖或宣称源码与二进制编译等价。

## 实际结果与支持范围

| 区间 | 完整周期T，秒 | 原请求C | 应用C | 完整包E | 全部实际入口N |
|---|---|---:|---:|---:|---:|
| 1200–1248 | 10,9,10,9,10 | 10 | 10 | 10 | 10 |
| 1248–1296 | 10,9,10,9,10 | 10 | 10 | 10 | 10 |
| 1200–1296 | 上述两组 | 20 | 20 | 20 | 20 |

原始请求积分为750×96/3600=20辆，实际20×3600/96=750 veh/h。最近档参考720×96/3600=19.2仅作量化参照，不是本次执行器的计划或实测结果。

10个完整周期均实际两辆绿灯入口，无黄／红入口，N未按quota截断。每次实际G4/Y3；T10为R3，T9为R2。本次没有用到T10第五绿秒，不能因此证明其他轨迹不需要它。两组车辆分别R0…9、R10…19；没有最终部分周期或车尾截断。

独立审计一次真实exit0，状态`PASS_OBSERVED_DATA_INTEGRITY_ONLY`；确认20车尾、1374正常离网末步、10次黄灯筛查、连续TLS/ACK及最终EOF，最小已观测加速度−4.5 m/s²。末AFTER非活动车辆池仍有单日志来源限制。保留客户端floating-step API UserWarning；没有将其冒充SUMO安全报警，也没有据无报警宣称普遍安全。

依据：[工程后审](../../artifacts/cumulative_full_catalogue_implementation_20261014_v1/engineering/native_execution_v1/POST_ENGINEERING_REVIEW_V1.md)、[独立数据后审](../../data/processed/cumulative_full_catalogue_implementation_20261014_v1/native_actual_v1/DATA_NATIVE_POSTREVIEW_V1.md)。

## 原始与派生证据

174原始文件共441,858,515字节，保存在本地`data/raw/cumulative_full_catalogue_implementation_20261014_v1/UA_CUMULATIVE_FULL750_S17_01/`，保持只读且未上传GitHub。[原始manifest](../../artifacts/cumulative_full_catalogue_implementation_20261014_v1/engineering/native_execution_v1/RAW_FINAL_SHA256_V1.json) SHA `ba93f78efcc74d95506f61fc4114c67e806f01e6433545370842c5b019f8f769`。

数据报告SHA `1734ba21dab246ef99b24ef0acda342d56c845a15041e74bacdcad0755aa2cbb`；[16项数据绑定](../../data/processed/cumulative_full_catalogue_implementation_20261014_v1/native_actual_v1/DATA_NATIVE_POSTREVIEW_BINDINGS_V1.json) SHA `418f3119fb5da022b5f690ebbc44de4284a1dc1c0762475fd0e5257b6d2751e8`。公开摘要不替代本地完整raw审计；没有伪称在线原始访问或干净checkout原生运行。

## 尚缺及下一步

固定750已经取得有限实际匹配证据。尚缺同一累计实现对既有动态300→750→900→300指令的应用与误差核账，以及真实E1→Feedback→请求→实际放行链路。优先补足这两类不同接口行为，不为每个周期再运行完整矩阵。具体后续卡、固定观察终点、部分周期语义和必要检查先完成三方审查，由负责人依据用户持续授权推进。

长期适用性、未测周期／轨迹、安全／服务资格和正式实验仍未建立。任何实际供给／接收不足都必须保留原始C及实测N，不能改结果、放宽门或选择种子来满足20辆预期。

科学依据：[实际科学后审](../../artifacts/cumulative_full_catalogue_implementation_20261014_v1/SCIENCE_NATIVE_POSTREVIEW_V1.md)。两个48秒块属于同一次运行，不是两次独立重复。

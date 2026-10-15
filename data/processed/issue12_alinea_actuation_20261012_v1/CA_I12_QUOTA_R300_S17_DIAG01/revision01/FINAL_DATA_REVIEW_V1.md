# Issue12 R300 DIAG01 独立实际前缀复核

日期2026-10-12。结论：**数据及指定观测覆盖PASS；运行是技术失败，不是完成周期、安全证明或rate qualification。** 本轮仅一次既有raw核账，没有SUMO／TraCI启动、raw或runtime修改。Context Preflight按当前Issue12工程准备读取；正式协议0B／未冻结，Stage6既有结项、A1 UNRESOLVED、Candidate A NOT_QUALIFIED保持。

## 版本与输入

实际运行CA_I12_QUOTA_R300_S17_DIAG01、卡SHA4ddbe480758fb8b0212912a36c07359eae34675b961cf1e1e49c434a031762a5；源是20e5e83基线上的精确未提交快照，不能声称基线源码已测试新实现。81原文件148,115,726B逐SHA匹配冻结manifest358e427bef1ba58d291376d6fed36e767a223603f6e0a29ea3a6a127353f6486；工程delivery清单全部匹配，完整raw保留原目录。

R300是固定服务指令300veh/h，不是qRamp300；需求M3600/R900/U360/X180、seed17，原车辆／需求不改。r_ALINEA=null，未运行ALINEA反馈。native进程退出0／CLI退出1不能相互代替。耗时依EXECUTION_RECEIPT_V1.json：监控清理137.296703s、whole CLI137.670531s；工程文字写137.672064s，存在约0.001533s口径差，此处不混写，均非本数据脚本重测。

## 五项实际检查

| 检查 | 独立证据及实测结果 | 适用边界 |
|---|---|---|
| FCD／运动TLS／ACK／实际入口 | 1210帧逐ID、lane、speed舍入与post-world一致；2420 ACK记录两阶段绑定；R0(1200,1201]和R1(1203,1204]各一次G过线，独立N2与ledger一致 | FCD标签BEGIN，车辆tuple为该步运动后状态；不虚构亚秒过线 |
| 率链及周期 | 控制10秒：C=pending=applied5/6辆当量，E0、N2；G4/y5/r1，quota2、G于1204实测达quota关闭 | 无完整24s周期，E0是未完成周期账；E−N−2不是持续超服务证明；1224／1248未观测均null |
| 全部末步离网车辆 | before-only=arrived IDs，1271个正常到达对应唯一tripinfo；类型／路由末edge合法lane、arrival==BEGIN、dt1和precision8速度差区间全部PASS | 运行后补审，不是新增在线全覆盖；有异常或UNKNOWN须阻下一诊断 |
| 安全及接收观测 | common速度差和post实际加速度最低均−4.5m/s²；碰撞／teleport计数最大0；两入口before/after及7条条件WAIT完整绑定；Y事件1204的41ID=26storage+15实际:urban_diverge_1_0 ingress，位置／速度／车长／decel和停车筛查重核 | WAIT记录可能重叠，不是7独立事件；Y5仅局部屏幕；未见报警不证未来安全。黄0／红0是真实5／1秒暴露，但red最低2秒未完成 |
| 完整日志、供给与残留 | 四原生日志2422捕获逐区间fragment／prefix SHA与最终EOF一致；stderr/error/stdout为空，native事件计数0；控制10步storage均有供给 | 父CLI兼容提示不在四流在线分类，保留既有边界；初次red checkpoint未生成，不能写通过 |

到ACK1210，以计划depart<1210为已到期：M1210／R153／U121／X61；实际插入M1210／R100／U100／X61；到期未插入M0／R53／U21／X0。未来计划M1790／R447／U179／X89单列，不作为插入失败。当前网内unfinished M73／R100／U23／X4。这是技术截断前缀，不比较科研效应。

queue-export BEGIN1209的ramp_storage_0 queueing_length208.528891m、shared_approach_0为236.006208m；experimental字段分别156.021705／183.499034m。原字段保留，仅作队列诊断，不混用定义，不证明全部城市损失物理回溢或sweet spot。

## 停止原因及是否支持技术修复

实际第一red ACK1210之后，bridge请求延长剩余红灯时，旧helper仅允许setProgram／setPhase，拒绝setPhaseDuration并报ValueError:unsupported phase request。只有1204的setPhase1请求实际记录；该duration setter没有进入native API。watchdog未触发，实际日志／制动／身份没有发现解释此异常的交通安全拒绝。因此证据支持**新namespace内最小接口兼容修复，再以新身份做R300技术重试**；不是放宽安全检查，不等于原生red不安全，也不能直接跳过未完成first-red检查点／整周期。建议以修复离线测试、新源码／卡片完整绑定及工程→数据→科学预启动／运行后门为前提；剩余启动预算和R900准入由父代理按Issue与实际权限处理，不自动重试。

## 实际数据执行与保留失败

V1 checker真实FAIL：误写CLEAR status名称；原状态为CLEAR_WITHIN_OBSERVED_LOOKAHEAD。V2修正后真实FAIL：把INGRESS误映射shared_approach_0，实际受保护源码为:urban_diverge_1_0。父代理明确允许第二处确定映射修复；V1/V2 source、traceback及failure receipts保留。两项均是离线reader错误，不能包装成native运行失败或改raw。

最终命令`python3 data/processed/issue12_alinea_actuation_20261012_v1/CA_I12_QUOTA_R300_S17_DIAG01/revision01/audit_prefix_V3.py`实际PASS（约1.94s）；复用已冻结audit_data_V3。另一次必要41-row yellow实际字段／停距重算及工程清单校验PASS，见SUPPLEMENT_RECEIPT_V1.json。没有复跑旧测试或扩大合成矩阵。输出PREFIX_DATA_RESULTS_V1.json、1271行终点结果与本报告；读取raw不可变，所有版本与来源SHA见FINAL_DATA_BINDINGS_V1.json。

建议交只读科学运行后审查；本数据PASS不提供native安全、完整red≥2、三周期或300–900服务资格，不改变正式实验状态。

# Issue12 packet900 独立实际数据复核

2026-10-12。**DATA PASS：精确新policy在本次72s／seed17实际完成九周期、18辆放行与指定安全观察。不是长期rate qualification、300–900全域资格或正式实验就绪。** 这已回答本次有界技术问题；不需仅因还有预算继续重复native。建议科学运行后审查后结束此诊断节点，后续资格／live ALINEA需明确范围和证据要求。

## Context、版本与原始证据

Context读取AGENTS／当前STATE／DECISIONS／WORKLOG／0B未冻结协议。最新用户取消固定启动次数，但原安全／研究及未知异常STOP保持；累计900s／900MB为父代理选择的原预算包络，不伪称用户逐字数值批准。源baseline20e5e83上的未提交精确快照，card5eba2e774682a6f4475e57ff4d6da8b9c472fcccd7fdb2ba148bba0cc4070fa2；工程41/49源冻结b1c324b9…实际运行交付记录匹配。不声称历史commit测试新实现。

95原文件164,333,753B逐SHA匹配manifest253c894c52c21a009094dbb7ee80586473f21a0e194abce4d86ccdfb54efde40；完整raw保留原目录，只写本新revision01。原STOP／失败／旧guard不改。M3600/R900/U360/X180需求、seed17、dt1保持；900指固定服务指令，ALINEA未运行。

## 实际独立检查

| 检查 | 结果 | 范围 |
|---|---|---|
| FCD／运动TLS／ACK／独立N | 1272FCD帧逐ID、lane、速度precision8与post世界对应，2544ACK两阶段连续；storage→internal独立重建18个唯一R0–R17，全部G；无黄／红新增front | 不用selfreported N代替重建；FCD标签BEGIN、tuple运动后，入口仅定位到1s区间 |
| 九周期及率链 | 每周期8s，实际G4/y2/r2，quota请求2、独立N2；72s C=pending=applied=E=N18，各积分差／E−N0；72步有储存供给 | E仍requested packet，不把名义两车当永远保证；900veh/h仅本短窗描述值，不是长期容量 |
| 实际red时钟／checkpoint／newG | 18duration ATTEMPTED/READBACK在1207+8k到1208+8k周期终点，actual red/remaining1/readback完整；firstred BEGIN1206／ACK1207账和provisional日志绑定，最终EOF补核；9fresh admission完整world／receiver匹配pre，fresh receiver全部通过 | red2为实际曝光，remaining1是第一个red ACK之后剩余秒数，不能误写红灯只有1s；1272不执行第十G |
| 全部body观察 | 每ACK独立枚举internal及active，40观察行、18entry ID/区间/颜色和位置／车长／速度／rear全绑定；18条first-actual-clear逐ID重建一致；九newG admission无残留spanning | head已过、tail仍跨线不是新red front入口；未加Yend清空硬阈值；是本run实测，不是未来保证 |
| 正常末步到达 | before-only=arrived，1338唯一tripinfo；ID／类型／终点route合法lane／arrival BEGIN／dt1／precision8舍入加速度区间全部PASS | 运行后补审，非在线全部未来安全；缺失/重复/straddle仍UNKNOWN门 |
| 保留原安全／yellow／WAIT／日志 | common差分及native加速度最低−4.5m/s²，collision/teleport计数0；61条件WAIT及18入口before/after联合绑定；九实际Y2 local人口41/39/37/35/33/31/29/28/28全覆盖、位置速度车长decel和停车筛查重算；2547原生四流fragment/prefix到EOF哈希完整 | 重叠WAIT不是61独立等待事件；原emergency9+1.1硬检查未被normal4.5替代；父CLI兼容提示不在四流在线分类范围，无报警不证极端未来安全 |

周期起点1200/1208/1216/1224/1232/1240/1248/1256/1264。每个首车在(begin,begin+1]进入，第二车在(begin+3,begin+4]进入；都是独立FCD/TLS核对结果。36s G／18s y／18s r全部实际观察，黄／红0是实测零，不是补缺失。具体18入口和18body-clear ACK见PREFIX_DATA_RESULTS_V1.json；所有车在下一新G之前已实际rear-clear。body重建没有强制计数18，先逐ID消费、比对真实跨线，再对账。

## 源等待、残留与共享区描述

截至ACK1272，已到期depart<1272计划M1272/R168/U128/X64，实际插入M1272/R100/U100/X64；到期未插入M0/R68/U28/X0。未来M1728/R432/U172/X86单列，未当失败。网内unfinished M78/R93/U23/X4；meter N18不等于R旅程已完成数。

shared_approach_0 ACK1272实测R18辆（4辆速度恰0，max6.300856m/s），U7辆（2辆恰0，max4.196180m/s）；仅描述原tuple，无新低速阈值、formal effect或唯一spillback归因。queue-export最后BEGIN1271原length／experimental字段保持JSON，不把两种定义混合。此run不与旧fixed24/Y5或STOP前缀合并统计控制效果。

## 资源与实际执行

工程receipt监控startup+loop+cleanup154.089223s，whole CLI154.990171s（不同口径），无watchdog触发。与精确settled history实际合计535.294480418s／622,683,415B；相对selected900s／900MB余额364.705519582s／277,316,585B。余额不是新运行许可；新run在history未正式settled前按guardian未知reservation保守占用，不隐式释放。原count取消不删除历史实耗。

实际一次命令：`python3 data/processed/issue12_alinea_actuation_20261012_v1/CA_I12_PACKET_R900_S17_DIAG01/revision01/audit_packet_actual_V1.py` PASS约1.83s，没有本次reader失败或重跑工程离线。新period8率账函数独立实现，不直接调用旧period24／300的rate reader；正常terminal helper复用已冻结audit_data_V3，其源码SHA纳入依赖。随后唯一必要9admission/Y2/工程delivery和实际资源／共享末帧补核PASS。未运行任何新SUMO或新增测试矩阵，不覆盖旧派生产物。

一个非阻塞schema标签差已明确：精确card origin=FIXED_PACKET_POLICY_DIAGNOSTIC，继承实际telemetry origin=FIXED_POLICY_DIAGNOSTIC。两者都绑定固定900、period8/quota2／ALINEA=null和精确runtime源；本审计显式映射并记录两标签，不宣称字面相同或动态ALINEA。后续交付文档应保留这项来源说明，不静默修改已冻结raw。

## 判定与交接

本run解决“保留原检查，通过短两车packet与真实Y2／red2能否避免此前长G6的当前gap拒绝并完成正常周期”的技术诊断问题：实测支持；没有从旧Y5同状态假设替代本run观测，也没改guard追PASS。不能把本差异唯一归因某单项Y/G变化或推广至所有队列状态。

无需为了此问题再追加native；交只读scientific_reviewer收尾和父代理Issue12／PR交付。当前仅packet period8/fixed900 executable，其他T8–24是映射候选，live ALINEA未集成；原300/Y5三周期属于不同版本，不能拼成当前policy300–900全域资格。450/600/750未测试、长期最高合格率未知、全域NOT_QUALIFIED仍保持。任何后续集成／资格或正式实验需另明示范围和证据门，建议不构成执行授权。

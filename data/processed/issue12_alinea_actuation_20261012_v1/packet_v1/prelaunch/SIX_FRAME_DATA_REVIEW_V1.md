# Phase-only packet候选：既有六帧独立数据准备

2026-10-12。PASS只限既有Y5三次绿末／首黄步的绑定与Y2同状态算术；不是Y2实跑、新native未来保证或新policy release。

Context刷新AGENTS／STATE／DECISIONS／WORKLOG／未冻结0B协议；最新用户取消固定次数，原安全／研究／异常STOP不变，父代理采用累计900s／900MB且单次300s／300MB／free5GB。设计科学conditional GO仅实施，工程新namespace／卡片未冻结，本数据任务无native／新配置／guard修改。

只从冻结FIX300的五个相关输入提取ACK1204/1205、1228/1229、1252/1253六帧。每个G末41／39／37 approaching storage＋实际ingress IDs与world／FCD完整相等，位置／速度precision8、车长5／decel4.5／step1及G→y真实motion TLS匹配。保留原stop-or-pass条件，只将局部Y长度2代入：各帧全部PASS_SAME_STATE_Y2_SCREEN。新policy可能改变后续状态，不能把该结果当9周期Y2的实际覆盖。

已front-crossed且车尾仍跨线的完整body清单恰为R1／R3／R5：G末internal front位置0.079146／0.334532／0.567474m，车长5m，尾距线−4.920854／−4.665468／−4.432526m，速度5.087526／4.820973／4.624245m/s。入口区间分别(1203,1204]／(1227,1228]／(1251,1252]，均G，不是黄／红新增front过线。首个实际旧Y5 ACK后的rear距线+2.219973／+2.741821／+2.262888m；当步已全部rear-clear。位置、长度、速度、ID／路由与entrytime一一绑定，全体internal人口枚举而非只挑一个车。

原approaching-screen公式约2.55s不得转为already-crossed body的新Yend硬阈值；上述旧Y5第一步观察只支持候选，并不证明新Y2或Y2+red2保证未来body-clear。责任边界依已读SCIENTIFIC_PHASE_ONLY_DESIGN_REVIEW_V1.md（官方processLinkApproaches的beyondStopLine与approaching区分）；原emergency9+1.1仍硬检查，新周期fresh receiver准入不删除。新实现必须逐ACK追踪全body直到实际rear-clear／下次G，缺ID或位置UNKNOWN STOP，新red front入口仍STOP。

实际V1提取PASS约1.06s；V2只补独立六帧TLS program/G-y绑定，原V1代码和日志保留。无需重新旧run／旧suite／额外fixture矩阵。两次均只既有文件读取／最小同状态计算，无SUMO／native query。SIX_FRAME_RESULTS_V1.json保留123行approaching算术与3条spanning-body表，各输入SHA可复查。

后续数据受影响预启动核查须等待新packet工程源／卡／binding：fixed900 period8／9cycles／1272、全body缺测STOP、累计资源归账／fresh exact授权及实际率链／null schema。现在没有新的卡片或raw结果，不补零或宣称预启动整体PASS。

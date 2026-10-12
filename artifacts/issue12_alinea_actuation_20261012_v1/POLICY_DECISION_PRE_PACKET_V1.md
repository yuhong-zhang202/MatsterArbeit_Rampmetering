# ALINEA流率到原生信号执行政策：Issue12工程选择

2026-10-12。工程／科学设计复核条件GO，采用下述单一政策进入最小实现；尚未运行或取得资格，后续回填实际结论。科研研究问题、ALINEA数学、网络、需求和车辆模型保持；正式协议未冻结。

## 选择原则与证据

ALINEA决定目标率，信号政策实施它，两者不能混同。A1只有摘要；A2/A3/A4取得可读正文，FHWA及SUMO官方正文已审阅，具体访问等级、题名、链接、不能外推内容以唯一[参考文献决策索引](../../artifacts/issue12_alinea_actuation_20261012_v1/literature/REFERENCES.md)为准。A2离散rate研究没有显式微观配时，不是当前SUMO物理能力的验证。选择属于Issue授权的工程准备，不是导师确认或正式科研决定。

现有两次同seed诊断每24s释放1辆、3周期E6/N3；第二车静止距线8.5m且首绿秒不动，3s绿末仍余3–5m。不能复制未经验证的nominal_n2，不能用扩大wall预算补模拟绿时，也不继续A1未来联合安全证明。[现有原因与限定结论](CANDIDATE_A_NATIVE_DISCHARGE_CAUSE_20261012.md)。

## 三政策比较：名义上限与实际能力分开

| 政策 | 名义换算／约束 | 当前实证／问题 | 本次取舍 |
|---|---|---|---|
|单车每绿|T=3600/r；若G3+y3+rmin2不变，Tmin8→名义上限450veh/h|旧三周期确实各1辆，但不证明长期450可服务；900需4s周期，无法直接复用此三相下限|不作为完整300–900主路线，不为900压缩黄红|
|固定n车包|T=3600n/r；n2在900需T8，留下G3／y3／r2|n2在已测300点未实现；全局G改5/6而不重新算周期会破坏高端，且黄灯非保证额外放行|不继续固定G3加未经验证每周期名义请求两辆的映射；旧E本来不是实际N，不将它误写为物理完成|
|离散执行档／饱和流率绿比|g=(r/rsat)C需有效rsat及startup-loss校准；若C24/y3/rmin2，gmax19、理想rmax≤rsat×19/24，900至少需rsat约1137veh/h，尚非物理证明|当前rsat未校准，不借公式造N。离散level量化误差与执行误差必须分开；文献十档／现场容量不照搬|选择一条有限离散档＋实际入口计数终止绿的n车政策；不用未知rsat或三套软件|

## 单一候选：固定24s周期、实际过线反馈结束绿灯

拟验证离散目标300／450／600／750／900veh/h，对应请求quota2／3／4／5／6辆每24s。任意r_final映射最近档，平局取低档；量化最大绝对差75veh/h（低率可达较大相对差），不隐藏为“精确连续ALINEA”。不改变ALINEA前一步数学反馈为实际N；原控制器输出和队列override不改。只在执行层区分r_final与r_policy。没有实测支持前这些是请求档，不能命名RATE_QUALIFIED。

绿灯持续至实际计量线unique-entry N达到quota或G最大时限，使用官方setPhase进入预定义yellow，再native red。黄灯期间合法额外入口全部记N；不可限数、倒扣、强制车速或抹掉overshoot。空供给、receiver不满足或超时都记录完整status/shortfall，不把E当N。E名称明确REQUESTED_PACKET_QUOTA，而不是guaranteed physical discharge。

工程提议的保守yellow参考5s、最低red2s，Gmax17s；尚待本地速度／正常制动／离散步／车辆长度的依据及设计审查，不把5s当现实或所有情形安全证明。必须证明每次实际yellow长度、受控link、red时钟未被earlyG close提前。若提前转yellow，首次实际native red ACK后在下一步前只调整剩余red至原24s周期末，严格验证nextSwitch与剩余最低red；不能在还处yellow的getter上错误操作。下一G新准入、WAIT条件、未知/危险STOP、四流日志/resource guardian维持。

新动态相位的首次red检查点按真实yellow结束计算，不能冒称旧1207 first-red时刻仍适用；旧卡/1272终点/旧结果不改。诊断拟仍到1272，24s×3受控周期。具体新卡须完整绑定已审查源、环境、输出和权限，不复用旧消耗卡。

退出车辆最小补齐拟保存before∖after速度／到达ID，运行后用精确绑定tripinfo arrivalSpeed与最后dt复核制动，normal arrival时间标记是interval begin而非ACK end。未观测、截断、vaporized、ID/精度不匹配为UNKNOWN停止后续；不能说已实现全部在线监测或改SUMO核心。以官方1.26源码链及数据审查确认适用。

## 核账与有界验证

完整链：r_ALINEA→r_final（既有clamp／override）→r_policy（离散请求档／生效时间）→信号G/y/r及请求quotaE→实际N。C积分r_final，C_applied积分真正生效r_policy；E是周期请求额度，N为unique过线数，分绿／黄／红。分别显示量化误差、packet缺额／overshoot和实际窗口误差；不将欠供给或未观察窗口填0。固定率技术诊断需将ALINEA未实际运行标明，不伪造其输出；实现可对既有接口做离线接入回归，生产T1资格门仍阻断未合格政策。

Issue批准最多3新小诊断，先300/seed17，机制与安全足够后再900边界，第三次仅用于有明确假设的中档600或一次有据小修；不是三点全部无条件执行，不试420/480预算。每个canonical授权/release及guardian须真实通过；若具体新卡还须用户另放行，准备IMPLEMENTED_NOT_RUN并报告，不能绕过。300s wall为已测短诊断参考，需fresh资源门、全raw/日志/阶段/逐车账及三方放行。

任何碰撞、违规则、异常制动或覆盖UNKNOWN停止相关运行/后档。900无法在合理相位和接收条件下完成请求6辆，保留原因与范围，不增加quota、缩黄红或继续网格“调成功”。最多3诊断只判断300–900可行性，未运行档NOT_TESTED；短窗SMOKE_PASS不等于服务范围RATE_QUALIFIED、长期安全或正式论文效果。

## 当前交付状态

历史问题[统一入口](../problem_records/README.md)已回填四条、预算并入receiver问题；未发现已有独立problem record待迁移，原诊断/实验报告与raw保持原位，目录通过链接整合而不是破坏来源。最小新源码正在实施，尚未验证或启动新诊断。本次最终运行证据、可用范围／NO-GO与Draft PR待后续门通过回填；不得将本草案记为已验收。

# ALINEA signal execution policy decision — Issue #12

**2026-10-12｜工程选择，待用户/Chat审查；不是正式协议、用户验收或执行器资格。** 文献唯一索引：[REFERENCES.md](../../artifacts/issue12_alinea_actuation_20261012_v1/literature/REFERENCES.md)。原政策草案保存在[版本V1](../../artifacts/issue12_alinea_actuation_20261012_v1/POLICY_DECISION_PRE_PACKET_V1.md)，原raw、STOP3及所有失败保持。

## 问题和政策取舍

ALINEA计算目标流率，信号实施决定实际车辆能否实现它。这两个层次不能用名义周期辆数混为一谈。2008综述仅核实摘要；2006作者全文支持有限离散率实施，但采用METANET，不能提供本场景微观配时能力。FHWA允许通过实际passage count结束绿灯；现场能力不是本SUMO资格。[2008综述](https://doi.org/10.3141/2047-04)、[2006全文依据](https://doi.org/10.1049/ip-its:20055003)、[FHWA §5.3.6](https://ops.fhwa.dot.gov/publications/ramp_mgmt_handbook/manual/manual/5_1.htm)。

| 方案 | 名义换算和限制 | 本次取舍 |
|---|---|---|
| 单车/绿灯 | T=3600/r；旧G3/Y3/red≥2下T至少8s，名义最大450veh/h；不是物理容量 | 不直接覆盖300–900；不另开发一套 |
| 多车/绿灯 | T=3600n/r；实际n必须测量；旧G3只测得每周期1辆，不能填2 | 采用实际入口计数结束绿灯，E只代表请求 |
| 饱和率绿比/离散率 | g=(r/rsat)C需要实测rsat/startup；未知rsat不能保证N；量化和执行误差分开 | 用有限整数周期映射，避免引入未校准rsat |

2019论文确实使用绿比换算及one-car政策，但其巴士/VISSIM情境不能认证本SUMO能力。[2019论文](https://doi.org/10.3390/su11226326)。2014论文的黄灯建议依赖车辆、距离和反应假设，约3.6s不是本模型无条件下限，更不是允许任意压短黄灯的依据。[黄灯研究](https://doi.org/10.1260/2046-0430.3.4.365)。

## 实际发现如何改变工程选择

同一seed17的旧WAIT两次均是三个24s周期C=appliedC=E6、N3。六周期第二辆绿末仍距线5.008/4.351/2.993m，支持起步与短G的机制解释，不唯一识别原生分支。[原因报告](CANDIDATE_A_NATIVE_DISCHARGE_CAUSE_20261012.md)。

首个新fixed24/quota2诊断在1210因旧helper不支持duration终止；只修复官方setPhaseDuration桥接，保留失败。随后FIX300完整三个G4/Y5/red15周期，每周期实际2辆、C=appliedC=E=N6。这说明延长有效G在该有限情境确实改善放行，不能推及全域。

同一fixed24政策900请求quota6，1206秒N2时被原current-gap检查拒绝：实测gap9.6308775899m，secureGap9.6211925193m，加原1.1m需10.7211925193m。ID、时刻、单位和minGap绑定未发现技术错误。observer有意采用leaderEmergencyDecel9，原生普通跟驰使用current apparentDecel；后者本配置4.5仍为源码/配置推断，未实际查询。该保守合同失败不证明原生危险，也不证明900物理不可能。[工程源码调查](../../artifacts/issue12_alinea_actuation_20261012_v1/engineering/stop_gap_investigation_v1/ENGINEERING_ROOT_CAUSE_V1.md)。

因此保留9+1.1硬检查，不采用shadow或4.5替换；只评估短双车包。没有继续A1联合未来状态数学证明，既有A1 UNRESOLVED与当前接口NO-GO边界保持。

## 单一最小后续候选：实际计数的两车包

映射库采用请求quota2，整数周期T=8…24s，r_policy=7200/T，选最近档、平局取低率。300/450/600/900名义对应24/16/12/8s，750映射720/T10。连续300–900的最大名义相对量化误差约5.882%（850→800），不是实际服务误差；每周期真实两辆尚不能先验保证。

最大绿4s，Y=min(5,T−4−2)，red≥2；实际quota达到时可以提前转黄，剩余红严格延长至周期边界。只准备/运行一个新900/T8/Gmax4/Y2/red≥2诊断；其他period仅库候选，未声称live ALINEA集成或全档已测试。所有绿/黄额外入口均计N，不cap、不改车速、不倒扣。r_ALINEA在固定率技术运行中为null；r_final/requested、pending和applied分别积分，E只在完整周期累计请求quota。原生产T1资格门仍阻断未合格政策。

每次Y前用实际Y2和完整approaching人口执行原停/通过筛查，UNKNOWN停止。所有已跨线但rear仍覆盖计量线的车辆逐ACK记录真实清尾；新G原fresh receiver准入不变。官方源码区分approaching和beyondStopLine，没有规定已过线车尾必须在黄灯结束前清空；不加未经建立的deadline，也不以Y+red算术保证清尾。[SUMO1.26固定源码](https://github.com/eclipse-sumo/sumo/blob/fa7df22d7f1c4ae245192ecc32410a49f1ffb2a3/src/microsim/MSVehicle.cpp#L3680-L3741)。旧Y5轨迹首黄ACK已清尾，仅支持候选，不能替代新Y2观察。[独立预审](../../data/processed/issue12_alinea_actuation_20261012_v1/packet_v1/prelaunch/affected_v1/PACKET_DATA_PRELAUNCH_REVIEW_V1.md)。

沿用标准native G→y→r、官方setPhase/setPhaseDuration及readback；不改SUMO核心、车辆模型、网络、需求、ALINEA数学或正式研究设计。[官方相位机制](https://sumo.dlr.de/docs/Simulation/Traffic_Lights.html)、[setter](https://sumo.dlr.de/docs/TraCI/Change_Traffic_Lights_State.html)。当前网页与安装1.26二进制构建等价仍未验证。

## 验证和停止边界

最新用户取消固定启动次数的停止条件；900s/900MB累计额度为工程沿用原三份最大额度的保守选择，不冒称用户逐字批准数字。单次300s/300MB、启动60s、free5GB及异常/UNKNOWN停止保持；未知reservation不隐式释放。每次run独立ID、精确card和三方canonical release，raw不可覆盖。历史三次381.205257418s/458349662B计入累计。WATCHDOG采样/cleanup并非数学绝对上界。[授权及预算来源](../../artifacts/issue12_alinea_actuation_20261012_v1/USER_RESOURCE_AUTHORIZATION_20261012.json)。

精确新900卡三方预审GO仅允许一次技术诊断。最终实际结果、300–900可行性边界及停止理由汇总至[交付报告](ISSUE12_EXECUTION_POLICY_DELIVERY_20261012.md)。碰撞、异常制动、新红灯入口、coverage/phase/receiver未知均停止，不调guard追PASS。短窗SMOKE_PASS不等于RATE_QUALIFIED、长期安全、所有中档或正式研究效果。当前Candidate A NOT_QUALIFIED，正式协议空/未冻结，Stage6既有结项不重新决定。

# Issue12 文献与官方资料决策索引

核对日期2026-10-12。全文表示实际取得正文可读副本，并审阅与执行政策直接相关的章节，不表示已重现实验。A1仅摘要，不能据其编造具体配时结论。来源不可访问的失败保留，不购买或绕过权限。表中技术方案仍待工程／科学审查；文献不等于当前SUMO资格证据。

## A 核心资料：全部审阅，证据等级分开

| ID／完整题名与作者年份 | DOI／原来源与获取层次 | 实际支持的原则／直接关系 | 不能推出的结论 |
|---|---|---|---|
|A1 Overview of Traffic Signal Operation Policies for Ramp Metering — Markos Papageorgiou, Ioannis Papamichail (2008), TRR2047:28–36|[10.3141/2047-04](https://journals.sagepub.com/doi/10.3141/2047-04)；出版社摘要／[TRB目录](https://trid.trb.org/View/847664)，无全文|区分流率控制策略与信号执行政策；列one-car、n-car、full-cycle、discrete rates|不推出本场景G秒数、每周期车辆保证或政策优劣数值|
|A2 Discrete release rate impact on ramp metering performance — Apostolos Kotsialos, Markos Papageorgiou, J. Hayden, R. Higginson, K. McCabe, N. Rayman (2006), IEE Proc ITS153(1):85–96|[10.1049/ip-its:20055003](https://doi.org/10.1049/ip-its:20055003)；[作者上传正文](https://www.researchgate.net/publication/3465157_Discrete_release_rate_impact_on_ramp_metering_performance)，正文§1、§2、§3.3及§5已读|可把ALINEA输出映射到最近离散档，披露量化偏差；不得任意改ALINEA前一指令项|METANET未显式模拟微观配时；其十档建议、2000上限或偏差抵消不可视为本场景实际放行及饱和下保证|
|A3 An Integrated Variable Speed Limit and ALINEA Ramp Metering Model in the Presence of High Bus Volume — Nima Dadashzadeh, Murat Ergun (2019), Sustainability11(22):6326|[10.3390/su11226326](https://doi.org/10.3390/su11226326)；[作者机构公开全文PDF](https://researchportal.port.ac.uk/files/28563433/sustainability_11_06326_v3.pdf)，正文§3／p8 Eq5及邻段已读|给出g=(r/rsat)C及one-car操作实现；说明连续流率需实施映射|不是SUMO实现；其公交／VisVAP环境和4s规则不移植；未知rsat不能拿公式保证N|
|A4 The Minimum Yellow Timing for Ramp Meters — Zhongren Wang, Chiu Liu (2014), IJTST3(4):365–377|[10.1260/2046-0430.3.4.365](https://doi.org/10.1260/2046-0430.3.4.365)；[出版社摘要](https://www.sciencedirect.com/science/article/pii/S2046043016301009)、[作者上传正文](https://www.researchgate.net/publication/276489395_The_Minimum_Yellow_Timing_for_Ramp_Meters)，§2–5已读|黄灯应考虑排队和正在接近车辆、动力学／几何／检测位置；真实清空约束优先于流率|特定双车情境约3.6s不是此项目无条件数值要求；不以论文表格认证旧y3安全|
|A5 Ramp Management and Control Handbook — U.S. FHWA (官方手册)|[Ch5 §5.3.6](https://ops.fhwa.dot.gov/publications/ramp_mgmt_handbook/manual/manual/5_1.htm)、[Ch6](https://ops.fhwa.dot.gov/publications/ramp_mgmt_handbook/manual/manual/6_1.htm)、[Ch10 detectors](https://ops.fhwa.dot.gov/publications/ramp_mgmt_handbook/manual/manual/10_1.htm)，官方正文|区分single／multiple／tandem；demand／passage检测可触发并终止green；评价ramp及arterial后果|手册现实范围不能当当前SUMO能力、不得为900缩短安全清空；本任务不开发tandem或城市协同控制|
|A6 Traffic Lights；Change Traffic Lights State；Traffic Lights Value Retrieval — Eclipse SUMO／DLR (官方，当前文档；运行源另绑定1.26)|[Traffic Lights](https://sumo.dlr.de/docs/Simulation/Traffic_Lights.html)、[TraCI setters](https://sumo.dlr.de/docs/TraCI/Change_Traffic_Lights_State.html)、[TraCI getters](https://sumo.dlr.de/docs/TraCI/Traffic_Lights_Value_Retrieval.html)，官方正文|预定义G/y/r及setPhase／setPhaseDuration；读program/link/phase/nextSwitch验证实际相位；黄灯可停车而非额外保证green|API正确不等于车辆安全或计数合格；current文档不冒充与已安装1.26二进制完全等价源码|

## B 补充背景：不据此扩大本次实现

| ID／完整题名与作者年份 | 来源／层次 | 相关原则及禁止外推 |
|---|---|---|
|B7 Evaluation of Ramp Metering Impacts on Travel Time Reliability and Traffic Operations through Simulation — Mohammad K.H. Shehada, Alexandra Kondyli (2019)|[10.1155/2019/8740158](https://onlinelibrary.wiley.com/doi/10.1155/2019/8740158)，出版社检索摘要／元数据，非本次全文依据|系统效益评价背景；不用于给绿灯秒数或证明本次效应|
|B8 Perimeter Control-Based Coordinated Ramp Metering with Linked Queue Management for Freeway Networks — Ziang He, Yu Han, Weihong Guo, Yanjie Ji, Pan Liu (online2024-08-06；issue2025-02,2679(2):338–358)|[10.1177/03611981241262313](https://journals.sagepub.com/doi/10.1177/03611981241262313)，出版社摘要／元数据|minG与queue约束背景；不开发MFD或协同控制；online／issue年份区分|
|B9 Integrated corridor management by cooperative traffic signal and ramp metering control — Abdullah Al Farabi, Rasool Mohebifard, Ramin Niroumand, Ali Hajbabaie, Mohammed Hadi, Lily Elefteriadou (2024),39:2439–2456|[10.1111/mice.13199](https://doi.org/10.1111/mice.13199)，出版社／[TRB元数据](https://trid.trb.org/View/2414013)；本次仅背景段核对|freeway/arterial成本需分开；不移植MPC/MILP或现场校准结果|
|B10 Statistical evaluation of data requirement for ramp metering performance assessment — X. Ma, A. Karimpour, Y.-J. Wu (2020),TR A141:248–261（按Issue缩写登记；未擅自扩写姓名）|[10.1016/j.tra.2020.09.011](https://www.sciencedirect.com/science/article/pii/S0965856420307217)，出版社摘要|数据充分性背景；现场两月结论不机械套用短期仿真，短诊断不变正式效果证据|

## C 仅保留Issue提供的检索目录：未全文审阅，不作技术选择依据

下列题名／缩写作者／年份按Issue注册，尚未独立验证完整书目；不把Consensus详情页当论文原始证据。无实施引用，也不扩大技术任务。

| ID | Issue提供书目 | 检索入口 |
|---|---|---|
|C11|Tajdari,F.et al.(2023), Optimal flow metering and lane-changing control with ramp-metering saturation|[目录](https://consensus.app/papers/details/321e91482f165446bc0a22e939af4dbd/)|
|C12|Tajdari,F.et al.(2022), Flow metering and lane-changing optimal control with ramp-metering saturation|[目录](https://consensus.app/papers/details/f6f2c31012f75310a156974b419ddbd8/)|
|C13|Chen,X., Li,T.-N., Ma,Z.(2020/2022元数据待核), Integrated mainline and ramp signal control for expressway on-ramp bottleneck with unequal lane-setting|[目录](https://consensus.app/papers/details/8f6914e2dd8458a1be0279a84e90fda0/)|
|C14|Ma,Y.et al.(2025), An On-Ramp Metering Control Strategy Considering Freeway Moving Bottlenecks in Intelligent and Connected Transportation Systems|[目录](https://consensus.app/papers/details/8c58620465bd5c4eb67fc093f892a7bb/)|
|C15|Gu,C.et al.(2022), A Smoothing Method for Ramp Metering|[目录](https://consensus.app/papers/details/040424de8bd15a93b3165f59f70f0bad/)|

## 访问限制与本次具体读法

DOI跳转A1/A2/A4在web不可直接读取；MDPI原页429，ScienceDirect全文403，TUC repository一次cache-miss；均未认定全文成功。随后A1出版社/TRB摘要、A2作者公开正文、A3机构26页PDF、A4作者公开正文/出版社摘要可读。只依实际可见正文方法部分决定原则；没有采用未经取得A1全文的数值或B/C高级控制。原文不复制到仓库；此表为简短释义，具体方案为本项目工程推断，需要既有轨迹及新批准诊断验证。

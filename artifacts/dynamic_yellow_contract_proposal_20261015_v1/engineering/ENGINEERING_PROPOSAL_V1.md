# 黄灯职责最小修正：工程提案 V1

**结论：可送审一个显式有界诊断合同；当前不得应用或运行。** 官方原生信号/跟驰机制支持职责划分这一方向，但不证明Y2在本场景安全。原局部停车/清尾表达式不是官方必要判据，本项目也未证明其为严格充分条件。不能把有限输入下见证false与缺数据UNKNOWN混为一谈；也不能把它改写为SAFE。

Context Preflight已读AGENTS/current STATE/DECISIONS/0字节未冻结protocol/WORKLOG及本次三方actual报告。当前proposal HEAD为b52b6138…；实际运行仍是f14aa49…/141源dfdddab7，全部执行源哈希复核不变。原STOP、Stage6/A1UNRESOLVED/NOT_QUALIFIED保持。ROOT_SCOPE仅授权新文档与patch文本；root中文方案第3–5节与本工程建议一致。

## 1. 唯一拟议变化

保留原`yellow_scope`函数、参数、原`scope.status='UNKNOWN'`、全部rows/failed IDs和完整数值。在**新隔离版本**增加解释层：

- 默认开关False，原见证false仍STOP；缺新卡显式contract或新用户授权不得启用。
- 原函数校验异常，或者车辆/时间/模式/模型/位置/人口/相位/日志联合绑定不完整，仍原硬STOP；不得catch任意异常后改advisory。
- 只有原有全量fresh-frame硬检查已通过、原结果与同一输入纯函数结果完全一致，且UNKNOWN唯一来自至少一个合法row的`stop_possible=False AND clear_possible=False`，才记录`DIAGNOSTIC_WITNESS_NOT_ESTABLISHED`并由获批模式允许进入原生相位观察。保留legacy UNKNOWN/rows；`safety_certified=null`、`future_native_safety_proven=false`。
- 新scope解释只能影响该见证门，不能吞碰撞/制动/红灯/接收/身份/覆盖/EOF等独立错误。原current-query底线、1.1告警、严格新G、NUM严格及全部G/Y/r/模型/策略/Feedback不变。

这是从额外前置阻止转向原生执行及实际后监测的**实质责任改变**。单步异常仍可能先发生，再被监测停止；不能宣称保留监测等于保留原预防责任。仅同意“不能提供独立见证仍可做有界原生诊断”，不是确认安全。

## 2. 精确最小修改面（仅文本）

[PROPOSED_MINIMAL_PATCH_V1.diff](PROPOSED_MINIMAL_PATCH_V1.diff)提供新隔离副本的关键差异，`NEW_ISOLATED_NAMESPACE`/`NEW_ISOLATED_AUDIT_NAMESPACE`是明确待实施占位符，不是当前存在或已可运行模块。未apply、未编译或测试。只增加一个小解释helper，复用原始纯函数；不重建执行器。

1. **adapter初始化/首黄准备**：`src/candidate_a_dynamic_minqual_20261015/adapter.py:77–87,167–169`对应新副本添加默认False模式；先保留原scope，再检查解释层许可。原世界/ID/车型/时间/位置/几何完整性检查在这之前继续执行。deadline与已quota切黄均进入这条fresh首Y准备路径。
2. **bridge quota前setter门**：`bridge.py:130–155`新副本在完整live绑定后、setPhase(1)之前计算原scope及解释层，durable写attempt，然后检查许可；不得先发黄灯再补日志。
3. **唯一definitive firstY日志**：`bridge.py:169–175`检查fresh time及新解释层许可；保存旧scope.status/rows和新分类，不再错误只接受legacy PASS。每次已观察首Y仍必须恰好一条记录；prepared-but-not-observed与实际Y分开。
4. **运行构造/精确权限**：profile与canonical必须绑定新contract ID/enabled及真正新直接批准，缺失默认拒绝；execute把已校验flag传给adapter。原margin-only批准和旧未用ALINEA卡不能继承。此处只列明必需字段接线，不生成任何卡或权限。
5. **独立reader**：隔离复制当前exact-catalogue黄灯helper及actual导入/call。完整保留时序/全人口/车型/字段/firstY集合/partial检查；逐行重算stop距离、clear timing、三项布尔、row.status和overall.status。分别输出绑定完整性、legacy见证失败和新诊断继续，不能只删除`need(stop or clear)`。缺字段、缺开关、伪报原PASS或其它UNKNOWN仍FAIL。

## 3. 实际Y/red监测是否仍存在

代码检查确认以下监测不受G/y/r分支豁免：

|监测|当前证据位置/范围|
|---|---|
|实际时间、program/phase/link/nextSwitch及ACK|adapter209–290；bridge每步ACK及pre/post日志|
|世界/模式/有效模型/本地人口/loaded/pending绑定|adapter44–72,122–150；独立identity审计保持|
|Y入口真实before/after跟驰底线及C/E/N|adapter179,258–325；N未被quota封顶|
|红灯新front跨线|adapter330；已在G/Y跨front后车尾在red清空不伪作新红灯入口|
|碰撞/teleport/普通制动和原生告警|adapter326–344；世界交集速度差、after加速度及实际counter/log，无NUM例外|
|全部spanning bodies|BodyTracker.observe逐ACK检查所有internal及active ID至实际rear clear；未知/丢失/回退STOP，无新黄末清尾deadline|
|新G接收/几何/无spanning bodies|bridge.admission和body_admission仍在每个新周期前硬检查|
|最终正常离网及EOF|运行后独立tripinfo末步核查及四stream最终EOF；未完成不能释放后项|

**限度**：离网车辆最后一步不属于在线after-getter覆盖；由强制post审计补核。末AFTER非活动池缺nextPRE时保持single-journal范围。原red_transition_witness本来记录为shadow，并非一个已证明A1前置硬保证。未来canBrake/private计划/RNG、源码二进制一致性以及一秒内无任何异常没有被现有监测证明。对本项目既有监测项目没有发现需额外补建的平台缺口；若审批要求这些未来/全局预防保证，则本最小方案**NO_GO**，不能仅把见证advisory。不能以实际观测零事件反证未来安全。

## 4. 官方字节锚点及本次事实

读取已有SUMO1.26 pin`fa7df22d7f1c4ae245192ecc32410a49f1ffb2a3`源码缓存，MSVehicle.cpp SHA`8499ebe445906b19395d5c70945b012f320a439327e9cb3c20f0abd26d15a6a4`：物理行3713 yellow，3714–15 canBrake/native brakeGap，3717–19 stopoffset/ignoreRed/yellow条件，3720–21等待速度。[官方固定源码](https://github.com/eclipse-sumo/sumo/blob/fa7df22d7f1c4ae245192ecc32410a49f1ffb2a3/src/microsim/MSVehicle.cpp#L3711-L3727)。此前#L3711–3727锚点匹配；web抽取3563等是显示行号差异，无需勘误旧binder。官方TraCI原生相位过渡的支持与具体Y2安全是两回事。

本次三方确认：1236的38个local输入完整，R5距线0.146m/v4.973m/s，仅两个工程见证均false；首Y从未执行。匀速1.035s与工程表达式2.558s均非测得未来清尾。原STOP正确适用于旧合同；不是已确认软件bug、实际危险或Candidate A普遍不可行。新的解释只是待批准诊断责任，不改历史判定。[工程actual4dd30fee](../../dynamic_minimum_qualification_20261015_v1/engineering/native_execution_v1/UA_NATIVEGAP_DYNAMIC_S17_01/POST_ENGINEERING_REVIEW_V1.md)、data7f0ec5c3、sciencecb9724c3见来源回执。

## 5. 获批后的有界验收与预算，不在本轮执行

只需未来针对完整见证false、默认strict、缺字段/错绑定/伪PASS、quota/deadline双路及其它STOP不吞的少量离线验证；不做新A1证明或矩阵。独立审计必须重算原结果并分层。之后精确新版本/新身份/reader/三方与canonical通过，才一次原300→750→900→300诊断；真实C/N、四应用与延迟、最终300后的欠额恢复及partial/pending是验收，不能拿退出0/名义E=N替代。成功后才同冻结执行器一次短真实ALINEA，失败不重试。

资源仅提案：沿用当前600s总账，已settle163.07205774995964s，余436.92794225004036s；不得重置。新身份纳账时保留旧已消费ID及其settlement，旧未用ALINEA不能执行；仅需小型ID/引用接线而非预算框架。单次有效上限min(300,当时总账剩余)，startup60、end1296、free5GB/no bytecap保持；后项还受真实剩余与必要观察可完成性约束，不够则不启动。

本轮仅新增报告、patch文本、来源回执和binder；无实现/新卡/权限/native/测试。下一位为独立data/science提案审查与用户合同决定。root维护治理文档，正式协议/原141源/raw均未动。

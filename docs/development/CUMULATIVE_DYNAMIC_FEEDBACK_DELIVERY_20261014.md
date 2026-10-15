# 累计执行器：动态请求与真实Feedback接线交付

2026-10-14。用户持续授权下的技术诊断；不改变正式实验设计。工程、独立数据和科学修复复审已完成，预算分层Major关闭；允许精确Dynamic现场门后启动，ALINEA仍待Dynamic实际复审。两项实际结果仍未观测。

## 目的与最小改动

[固定750实际节点](CUMULATIVE_FULL_CATALOGUE_NATIVE_REPORT_20261014.md)已确认96秒内C=E=N20。本阶段补两个不同缺口：原有动态300→750→900→300请求的实际应用／延迟，以及真实E1→原Feedback→请求→实际应用。无需逐一运行17个周期或重跑固定750。

直接复用`candidate_a_cumulative_full_catalogue_20261014`的policy、adapter和producer。新增薄profile、bridge、budget及CLI；bridge仅改导入与动态模式在固定终点的partial分类。原安全／UNKNOWN停止、strictNUM、车辆模型、相位、quota和Feedback公式不变。正常到1296时的未完成周期如实截断，提前异常不能归为正常截断；不补运行步、完整E或清尾。

新的独立reader复用原数学、相位及车辆／日志审计；精确接收两个新身份，保留完整包E与全窗口C/N不同支持范围、pending/null与body censor。

## 当前精确V2卡

| 项目 | Dynamic | Real Feedback |
|---|---|---|
| 身份 | UA_CUMULATIVE_FULL_DYNAMIC_S17_01 | UA_CUMULATIVE_FULL_ALINEA_S17_01 |
| 模式 | dynamic_commands | real_alinea |
| 请求来源 | 既有1200:300、1201:750、1226:900、1237:300 | 初始900，原E1/Feedback，30秒时钟 |
| 卡SHA | 68e9b2c73d7164a1bd10199e77ca43bcb42332e680a240b0828091ec45a3ed34 | f26cdd8e72a66d4efc782628a4107734af18c3539fc1a0073bd16f2e717786db |

卡在`artifacts/cumulative_full_catalogue_followup_20261014_v1/engineering/packages_v2/<run_id>/card.json`。共同136源摘要`5d0695195a2062f4708f455b227901b9084a76acca86dc81b34cc59e93d6d85e`。每次固定end1296、seed17和原需求，监控300秒／启动60秒／无固定输出字节门／磁盘余量至少5GB；两项累计新600秒，不继承旧余额。先动态实际工程→data→science复审与结算，再判断真实Feedback是否启动。每身份一次，无未改变条件的盲目重试。

## 离线验证与发现的Major

工程三项受影响方法PASS18.083秒；随后只调整profile元数据，真实双卡静态／缺权限前置拒绝门另行核查。独立数据三项方法一次PASS0.081秒；合成dynamic为C311/24、applied155/12、E12/N14，其中最后包只观察11秒；合成Feedback三窗口、两条应用／一条pending。这些是软件账本测试，假运动不是物理放行证据，动态C=N不是接口通过条件。

科学审查发现新reader仍把两次累计用时按单次300秒检查：180+180秒会误报超限。旧源、V1卡／报告／未使用授权及真实反例FAIL保留。最小修复分别读取单300与合计600门，一项受影响回归PASS0.004秒；单301、累计601仍拒绝。生产监控预算本来正确，未修改guard或重跑SUMO来验证纯核账错误。

修复后V2两卡真实静态门PASS、旧V1卡明确拒绝。profile只变更卡及授权版本路径，原125源及运动逻辑未改。E1文字Minor另在PLANV2澄清：`p1_main_down_20_l0/l1`为detector IDs，`main_down_0/1`为lane IDs；原producer一直使用正确检测器。

依据：[工程V2](../../artifacts/cumulative_full_catalogue_followup_20261014_v1/engineering/repair_v1/FINAL_ENGINEERING_REVIEW_V2.md)、[数据V2](../../data/processed/cumulative_full_catalogue_followup_20261014_v1/offline_v2/FINAL_EXACT_CARDS_DATA_REPAIR_REVIEW_V2.md)、[原Major记录](../../artifacts/cumulative_full_catalogue_followup_20261014_v1/SCIENCE_OFFLINE_REVIEW_V1_MAJOR.md)。V1与V2证据分别适用各自源码，不宣称V1对当前源码仍全哈希匹配。

## 尚未证明

尚无这两个新身份的真实车辆、转相、清尾、EOF及实际反馈应用证据。正常partial终止不是完整服务／安全验证。需至少一条非初始Feedback命令有实际ACK应用；若数值或档位不变，应照实报告，不调参制造变化。

长期服务、全部请求历史、普遍安全和正式实验资格仍未建立。Stage6既有结项、A1状态及正式协议不由本交付改变。下一步由负责人依据已保存的用户持续授权，在精确科学复审和canonical现场门通过后执行动态诊断。

科学依据：[V2关闭意见](../../artifacts/cumulative_full_catalogue_followup_20261014_v1/SCIENCE_OFFLINE_REVIEW_V2_CLOSED.md)。

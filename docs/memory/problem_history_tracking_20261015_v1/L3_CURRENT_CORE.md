# Masterarbeit-Ramp-Metering 当前核心记忆

截至2026-10-15。记忆仅为辅助背景；当前仓库文档和原始证据始终更权威。项目为TU Berlin硕士论文，用SUMO研究匝道控制保护主线M与匝道R／连接城市U代价的权衡，X为技术横向流。导师Robert Hilbrich的真实意见以docs/SUPERVISOR_FEEDBACK.md及原源为准，角色模拟不构成导师确认。

## 当前状态

D-018规定的Stage6探索验证保持completed / preliminary_ready for formal experiment design。当前版本OPEN/V15在M3600/R900、seeds17/23/42见M改善、R/U成本及全网总成本增加；严格meter到shared、持续≥30秒连续慢行链为0/3。未找到sweet spot，未证明精确容量、breakdown概率、全部U损失唯一由物理回溢造成或独立正式确认。原RI3350 NOT_PAIRABLE／A_NOT_EVALUABLE、重建固定B22/B28分别保留，不能和当前系列拼成因果效果。Robert2026-09-30指导：先核几何／连接／实际插入，再无控需求空间定位临界区，选点比较控制，不用22/28秒人为造ABC；不等于批准具体ALINEA参数。

之后开发发现FIX02的72服务窗口71失败，进入执行器调查。最新**获批最小动态＋同版本短真实ALINEA技术节点完成，待用户／Chat审查**：执行提交3d82ed578e4e5e028ed3db14e596bd44e845956b、同154源摘要089a2fefb9fb4d68aced499b532636c3a551b672f9130a1fd2e6acb468ff4ae2。动态300→750→900→300真实应用延迟0/23/6/3秒，最后300正欠额恢复；真实ALINEA独立E1→own-previous公式→执行器→实际N链路完成。原始C23.7034390771辆／实际N24／完整E22，11完整包各N2，末partial另N2；两非初始应用延迟2/4秒，1290请求在1296仍pending。两条控制观察各96秒、seed17，不证明长期均值、完整连续300–900域、全部周期／未来请求历史或普遍安全。Candidate A仍NOT_QUALIFIED，A1仍UNRESOLVED。正式协议docs/EXPERIMENT_PROTOCOL.md仍0字节、未冻结，正式实验未授权。

累计纠偏以原始请求积分C与实际N选既有周期，不能用名义E／最近档参考／C_applied代替实际跟踪；最终C_applied是7200/T名义周期率积分。G3 E6/N3、旧750 13/14、独立G5/Y3 14/14但750→720偏差、累计750 20/20分属不同版本，不是单参数配对因果比较。用户分别明确批准current-following原生query硬底线+额外1.1m告警，以及完整输入下原黄灯工程见证失败时原生观察的独立诊断合同；原STOP3／旧guard／UNKNOWN／真异常停止保留，不是原生未来安全证明。

原ALINEA reader因终点1296未执行的next-prepare setter预期而exit1，保留该FAIL；仅processed版本窄修复后同raw完整审计通过，原154执行源、卡和raw未改。未来复用须新版本合入／绑定，不能称原reader已经修好。同600秒监控账结算475.645467625秒、余124.354532375秒；余额不构成追加运行理由或权限。

## 交接入口与历史问题

先读docs/PROJECT_STATE.md、docs/DECISIONS.md、docs/development/DYNAMIC_AND_REAL_ALINEA_TECHNICAL_CLOSEOUT_20261015.md和目标清单V4。docs/problem_records/README.md为唯一主要问题入口，现10主题；PRB004详细记录放行不足发现→轨迹研究→文献／官方依据及取得层次→方案演变→实际效果与限制。PRB005–010分别记录早期实际入口观测域、分析假通过／T54、RI3350配对、固定配时／无控边界、TraCI／E1／安全与服务、同版trade-off及严格回溢阴性。未声称穷尽所有历史；尚未找到只测lane0遗漏全车道的直接bug源或T54直接接受，勿凭聊天补造。32为登记启动尝试，不是32个SUMO进程。

现有Draft PR13关联Issue12；base codex/candidate-a-native-smoke-proposal／20e5e83不变。最近已核发布head69c25796c1a215faa7e638410ae0ceed80c96393是本次文档补档前快照，当前head请实时查看。未合并／关闭Issue。完整raw仅本地，公开卡／manifest／派生报告不意味着干净公开checkout可重跑全量实际审计。下一位用户／Chat审查；下一步建议、AI自检和科学GO都不等于用户验收或新增执行授权。

## 工作与记忆规则

中文、结论先行，清楚区分事实／计算／推断／建议／用户批准／导师明确意见／未知。实质simulation/data/scientific任务按AGENTS调用相应项目agent；raw只读，失败和版本边界保留，不自行改科研范围、正式参数、协议或审批状态。问题按独立主题追加，不为每个小Reviewer缺陷开文件。

Tencent正式身份保持volume tdai-ramp-metering-memory-v1、service ramp-metering-formal-memory-v1、team team-masterarbeit-ramp-metering、agent agent-project-memory、user user-yuhong-zhang。本次用户明确要求更新，采用network none下官方API确定性L2/L3写入，0模型／付费请求，L0/L1和非目标L2不变，既有阶段场景旧正文先备份保留；未声称生成新L1。未来付费仍需精确内容／模型／请求／费用批准。记忆不得反向变成科研事实或批准源。

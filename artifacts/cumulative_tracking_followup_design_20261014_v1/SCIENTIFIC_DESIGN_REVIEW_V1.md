# Scientific review: bounded full catalogue offline design

2026-10-14。主agent保存只读scientific_reviewer最终意见，链接使用仓库相对路径，结论不变。

**GO_FOR_BOUNDED_FULL_CATALOGUE_OFFLINE_DESIGN。** 扩回原T8…24目录、保留当前T10例外，是合理的最小后续设计，能够恢复300–900的名义表示范围，并保留累计跟踪的完整目标。它不能解决已经发现的实际适用性问题，也不是新运行授权。

已完成Context Preflight及指定证据阅读。正式协议仍为空且未冻结；上一运行STOP、混合政策持续适用性未成立的Major、Candidate A NOT_QUALIFIED、A1 UNRESOLVED均保留。最终binder ff7035af所指前序绑定与补充解释版本一致。

## 科学判断与授权边界

可以复用原17种相位配置、已单独审查的T10/G5/Y3例外、Command/E1/Feedback接口，以及当前C−N评分、真实入口定义和全部停止门。原目录源码明确采用Gmax4、Y=min(5,T−6)、剩余红灯；T8/900动作保持原样。[工程设计](engineering/ENGINEERING_FOLLOWUP_DESIGN_V1.md)、[原目录](../../src/candidate_a_unified_alinea_20261013/policy.py)

候选集合由2种扩到17种会改变执行器选择，不能写成“全部策略行为不变”。它保留原C−N评分公式，是针对既有完整请求范围的接线扩展，并未替换ALINEA反馈算法。可以在现有持续技术任务授权内做隔离、可逆的离线准备；本科学意见不能登记为用户批准新配时或新运行。

以下变化不属于本次最小准备，应暂停并取得明确决定：新增相位数值或包大小、改变quota、修改评分目标、缩黄/红、放宽安全条件、改变模型或Feedback状态。新身份、终点、资源及SUMO执行仍须单独授权。

## Findings及证据边界

没有发现阻碍这项离线设计的新增Blocker或Major。既有实际Major仍未解决：目录存在不等于所有包在动态历史中均可安全适用或放满两辆。

8次尝试、277行同快照Y3筛查通过，只说明原谓词对这些既有输入的结果，不是277次独立运行或反事实成功。当前T10的第二辆在第五绿秒通过，不能推出新T9整包一定N1；黄灯入口计入N，改变信号会改变轨迹。补充解释修正准确。[数据审查](../../data/processed/cumulative_tracking_followup_design_20261014_v1/DATA_FOLLOWUP_DESIGN_REVIEW_V1.md)、[解释边界](../../data/processed/cumulative_tracking_followup_design_20261014_v1/T9_INTERPRETATION_BOUNDARY_ADDENDUM_V1.md)

## 五项测量检查

|检查|判定|
|---|---|
|目标|设计通过；原始限幅请求C、完整名义E及全部实际入口N分开，完整300–900目标未缩减。|
|实际覆盖|既有快照范围通过，未来未验证；新目录车辆、黄灯和接收状态尚无运行证据。|
|遗漏/重复|限定通过；8次尝试及277行已核，未来继续保留全部颜色入口、partial/null和UNKNOWN。|
|独立核账|同状态筛查及算术通过，不构成新政策实际服务、安全或长期跟踪核证。|
|回归保护|尚待实现；最小检查足够，不要求大矩阵。|

## 最小验证及下一步

只需核对17行参数/XML与原目录及T10例外一致；验证300/750/900和原动态指令的精确C−N选择、ID/延迟/partial/null及N≠2停止；用真实helper检查一条T9/T10切换路径；确认Feedback自身previous及30秒窗口不变。未变安全负控可按源码哈希复用。

完成这些接线检查和独立复审即可交付离线包。不要为覆盖17档运行17组仿真，也不要用更长包掩盖900能力不足。若持续可适用的两车包平均周期大于8秒，实际900目标无法由该目录保证，应报告约束冲突，不修改账本或安全条件。

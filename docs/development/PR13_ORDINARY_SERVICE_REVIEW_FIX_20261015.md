# PR13：普通服务P1与审计器两项P2修复

2026-10-15。当前交付仅包含实现、必要离线验证和复审；用户最新指令禁止SUMO及合并PR。自然交通资格仍为NOT_TESTED，总体NOT_QUALIFIED。本文件不改变正式实验协议、ALINEA核心或科研设计。

## 实际审查版本和问题

已通过GitHub原始review API核对：review `5526924792` 的实际 `commit_id` 为 **`6dc1680de32bad325aa7151f107cd61f8bb51b4d`**，状态COMMENTED，提交时间2026-10-15 01:28:28 UTC。[实际review](https://github.com/yuhong-zhang202/MatsterArbeit_Rampmetering/pull/13#pullrequestreview-5526924792)；[保存回执](../../artifacts/thesis_actuator_readiness_20261015_v1/PR13_REVIEW_6DC_V1.json)。先前P1实际review为`9a9c96ed…`，不是最初请求的`69c25796…`；版本不能互相替代。

该轮两项P2均影响失败证据可信度：[超额包](https://github.com/yuhong-zhang202/MatsterArbeit_Rampmetering/pull/13#discussion_r4278071195)的硬停止被审计器误当假PASS；[后续周期硬故障](https://github.com/yuhong-zhang202/MatsterArbeit_Rampmetering/pull/13#discussion_r4278071201)因仍保存早期正常评估而被错误拒绝。`scripts/pr13_service_scope_audit_20261015/audit.py` 已分别接受与硬receipt一致的quota-exceeded评估，以及早期正常评估；当前故障周期的中性评估仍不能掩盖硬故障。[独立修复报告及版本边界](../../data/processed/thesis_actuator_readiness_20261015_v1/pr13_reader_p2_fix_v1/DATA_REVIEW_FIX_REPORT_V1.md)。

原有限诊断修复只能中性停止，并未解决普通持续控制。根据先前明确的[完整用户任务](../../artifacts/thesis_actuator_readiness_20261015_v1/USER_AUTHORITY.md)，本次在新隔离 `src/candidate_a_natural_service_20261015/` 实现普通服务候选，原有限入口、原154源、已执行卡、raw及原终点分析失败全部保留。

## 最小处理方法

周期选择以原始累计请求 **C−E_scheduled** 校正离散化。E_scheduled是完整名义周期的调度机会，即使接收拒绝而整周期保持红灯也不表示实际服务。另存E_executed、C_selected、C_applied、唯一真实过线N，以及 `C−N=(C−E_scheduled)+(E_scheduled−N)`。物理短放项不回灌周期选择，不靠删除欠额或篡改N取得匹配。依据与推断层次见[方法依据](../../artifacts/thesis_actuator_readiness_20261015_v1/LITERATURE_AND_METHOD_BASIS.md)。

完整周期N0/1可以继续；合法G/Y中多于两辆保留真实数和偏差。供给、车辆状态、receiver与WAIT是观察证据，不能由N<2唯一归因于故障或某种交通原因。已知接收受限只在实际完成清尾并处于红灯的周期边界延长当前红灯，下一名义边界重新检查；全红周期没有虚构G ACK、应用指令或服务。真实违规入口、重复计数、错误ACK、碰撞、异常制动、缺失或UNKNOWN仍按原硬门停止。

新入口使用真实600秒时钟，复用既有自然输入和原Feedback（自身前一clipped请求、11%、70、30秒、300–900、初值900）。不再用600–1200人为蓄队。600首次OPEN→G同色转换在setter前核验实际局部R／内部为空及接收状态；意外非空或受阻直接停止，不临时创造初始化政策。完整／部分周期、pending与实际首次应用分别保存；终点不要求尚未发生的下一prepare或setter。

## 验证与限制

P2：一组针对性回归最终PASS（0.008秒），旧reader对两个新增案例实际拒绝，新reader接受合法硬停止；四份原保存案例重审、五种无效变体拒绝。超额案例是明确标注的合成ledger／ACK材料，不是三车原生轨迹。后续硬故障案例使用既有假世界loop。首次测试脚本名称错误及旧reader前像保留，没有把失败重写成通过。

普通服务工程：三项组合方法最终PASS（4.906秒），覆盖服务数不影响同一名义调度、N0/1继续、接收红灯等待／恢复、真实600入口和Feedback接线、partial／pending及原硬门。另一个精确完整终点方法PASS（0.743秒），没有声称最终四方法整套重跑；同一既有loop方法导出四案例耗时3.234秒，加终点案例共五份保存材料。首次暴露旧Command起点硬编码1200的真实接线错误，已在新namespace修复并保留失败。8份新Python静态编译及CLI help通过，未实际准备卡或启动原生环境。[工程报告](../../artifacts/thesis_actuator_readiness_20261015_v1/engineering/implementation_v1/ENGINEERING_REPORT_V1.md)及67文件绑定SHA `47415e55e71b52e8ed4894ca6070f84fff3c2a2a5bf3521722e6042c9894bc38`。假世界只能证明软件接线与核账，不能证明SUMO物理或自然需求资格。不扩展正式矩阵。


独立新reader为stdlib实现，不导入运行时selector；五份保存材料重建核账通过，十种损坏被拒绝，最终一组PASS（0.970秒）。641案例均C=41/4、E_scheduled=10；空供给N0，接收受限案例E_executed=8、C_applied=33/4、N4，640完整终点另核为C10/E_scheduled10/E_executed8/C_applied8/N4。首个完整Feedback窗600–630及630请求在632首次应用、延迟2秒独立核对。记录中的rate_chain在ledger更新前采样，reader中途误读导致的FAIL及修正前像保留；未修改runtime。该reader只接受明确标注的synthetic bundle，原生审计能力没有据此完成。[独立核账报告](../../data/processed/thesis_actuator_readiness_20261015_v1/natural_reader_v1/DATA_REPORT_V1.md)，绑定SHA `121aa891b9e38146030d49d5471c882f118b66950b953b1cec5fff7a5a0e23e4`。只读科学终审结论为GO_FOR_PR13_ORDINARY_SERVICE_AND_READER_P2_OFFLINE_FIX_REREVIEW，无阻碍本次离线送审的实质Blocker/Major；逐项回读工程67、P2 17、新reader 62及历史154源哈希通过。[科学回执及五项测量边界](../../artifacts/thesis_actuator_readiness_20261015_v1/SCIENCE_FINAL_OFFLINE_REVIEW_V1.md)。TECHNICAL_PASS仅限软件接线与合成观察核账。

自然实际安全、持续服务、4050车生命周期／源等待／未完成行程及城市侧暴露均未在新版本运行验证。已有输入预检和[七项最小资格方案](THESIS_ACTUATOR_MINIMUM_QUALIFICATION_PLAN_20261015.md)是准备材料；新900秒预算仅提案，旧账不重置，本轮不生成native release或执行运行。旧短测试及处理后终点修复不能充当新自然版本的实测。

## 文档和交付边界

PROJECT_STATE、WORKLOG、PRB-004与Dashboard仅更新当前事实和待办；DECISIONS、EXPERIMENT_PROTOCOL、AGENTS、导师反馈及论文结构不变。原PR13和base依赖链保持，既有无关记忆／私人文件修改不纳入提交。准确发布head、复审请求和后续实际结果以GitHub回执为准，不把内部GO当作用户验收或QUALIFIED。


## 本地提交与公开发布阻塞

修复代码／证据已提交为 `f7a9badaecef1c0aa5775ae4143687ee2959828a`。正常快进推送到原公开库 `https://github.com/yuhong-zhang202/MatsterArbeit_Rampmetering.git` 的 `codex/issue-12-alinea-signal-policy` 两次均遭自动审批拒绝。第二次理由：授权依据来自不受信的goal/tool输出，可验证用户指令未明确批准这113个具体文件的公开外发。拒绝后没有改用其他传输方式。

发布内容已备好：113文件，约27.4MB，包含新代码、限定测试、治理／方法文档和明确标注的合成观察／审计材料。最大单文件约2.13MB；高置信凭据模式0；真实data/raw、私人supervision、无关memory及其账本／WORKLOG插入均排除。Git remote与GitHub PR13 API的head repo、clone URL、分支完全一致。全量whitespace检查只命中按原字节保留的授权／PR旧正文末空行和首次失败测试日志尾空格；src/scripts/tests/docs/dashboard范围检查通过，不修改原证据消除格式提示。

远端仍为6dc1680，已完成的review只对应该版本。本地修复没有被新一轮GitHub reviewer审查；批准公开推送后，才可核对准确远端head并申请新的review。当前状态为本地离线修复完成／发布待明确批准，非远端复审完成。后续状态说明提交仅更正文档／Dashboard，不改变已审绑定的实现或测试证据。

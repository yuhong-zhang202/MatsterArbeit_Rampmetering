# PR13：普通服务P1与审计器两项P2修复

2026-10-15。当前最新为本文末的第二轮限定P2修复及新绑定；前文第一轮绑定／结果保留为历史。当前交付仅包含实现、必要离线验证和复审；用户最新指令禁止SUMO及合并PR。自然交通资格仍为NOT_TESTED，总体NOT_QUALIFIED。本文件不改变正式实验协议、ALINEA核心或科研设计。

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


### 发布批准及实际推送更新

用户对上述113文件、约27.4MB、明确公开目的地和原PR13分支直接回复“批准公开推送并复审”。审批后同一正常推送成功，远端由6dc1680快进至37ab8056bc1e72ccc658242f153daa20c56baa8e；没有force、合并或新增SUMO。前节阻塞描述属于批准前历史。随后只同步当前文档／Dashboard事实，并对最终远端准确head申请针对性review；实际审查结果仍待返回，不能把内部GO或旧6dc review当作新版本已审。


### 本轮准确head复审请求

最终远端head已通过GitHub原始PR API核对为`24ec690de67818355076247f9192ed48a75ad390`，base20e5e83、Draft及未合并状态保持。相对实现提交f7a9bada仅四个治理／发布状态文件变化，实现、测试和绑定证据字节不变。113文件发布范围核对一致。

已回复原P1及两项P2线程（4278189787／4278189214／4278189546），保留线程供reviewer确认；[本轮@codex review请求6182550931](https://github.com/yuhong-zhang202/MatsterArbeit_Rampmetering/pull/13#issuecomment-6182550931)明确限定准确head、普通服务误停／物理追债／真实红灯保持、C/E/N、partial/pending和失败版本边界，并禁止SUMO、改代码／合同或扩大矩阵。机器人eyes只表示接收，不代表完成或通过。当前等待正式review结果及实际commit_id；历史空白人工review条目不能算本轮bot审查完成。


### 24ec复审完成：第二轮限定修复

review5527104163实际commit_id为24ec690de67818355076247f9192ed48a75ad390，与请求及远端一致；[原始回执](../../artifacts/thesis_actuator_readiness_20261015_v1/PR13_REVIEW_24EC_V1.json)。三项实质P2为[setter部分失败证据](https://github.com/yuhong-zhang202/MatsterArbeit_Rampmetering/pull/13#discussion_r4278226978)、[最终command生命周期绑定](https://github.com/yuhong-zhang202/MatsterArbeit_Rampmetering/pull/13#discussion_r4278226984)、[硬停止原因与reasons绑定](https://github.com/yuhong-zhang202/MatsterArbeit_Rampmetering/pull/13#discussion_r4278226992)。这不是新自然交通或安全运行结果。

进入最多两轮额外实质修复中的第二轮：工程仅修natural bridge逐setter证据及小故障注入，data仅修两reader与相应最少反例核账，然后科学终审及准确新head复审。旧源、报告、绑定和保存案例不覆盖；缺失reasons的旧证据不得追填或借新reader改判为更强证据。仍禁止SUMO、合并、改合同／科研输入或扩矩阵。


### 第二轮离线修复及新证据版本

三项P2已完成最小修复。Natural bridge在初始OPEN、新包程序／绿灯、quota黄灯每次setter前后逐次fsync记录ATTEMPTED、正常返回、读回或失败；每个读回字段分别OBSERVED或UNKNOWN。失败可能已部分改变信号，不能标成无效果；未读到的phase保持null／错误，后续不advance、不虚构G ACK。失败快照／receipt新增最后setter及journal指针。旧24ec同一故障方法四子案真实FAIL1.840秒保留，修复后同1方法PASS1.742秒，不是整套／native重跑。[工程round2](../../artifacts/thesis_actuator_readiness_20261015_v1/engineering/review_round2_v1/ENGINEERING_REPORT_V1.md)，新45文件绑定`9cace32950a7cff0404d167772e46ba8282962f149b473953c3ca49fc1feba29`。

Natural reader独立重建完整nested command、first preparation、首次实际G应用、superseded／最终status与事件顺序，并核对cycle请求／应用／延迟。Held周期可保留该请求历史首次应用时间，但当前applied ID／rate仍null。Finite reader普通after-step硬停要求真实terminal reasons与DiagnosticStop精确对应；quota异常则由完整超额assessment和精确ValueError链单独支持。

三种旧reader错误接受已实际重现。新最终针对性组PASS0.939秒／14种损坏拒绝，旧finite保存回归0.007秒；初次8.751秒只新增一次相同finite later-hard假故障V2，此后只读保存材料。四份新setter故障边界独立核对通过。旧later_hard／safety_priority投影缺reasons，修后明确NOT_CERTIFIED，不从error追填原因；不删除旧通过记录或把新证据当成旧证据。[data round2](../../data/processed/thesis_actuator_readiness_20261015_v1/review_round2_v1/DATA_REPORT_V1.md)，新绑定`3eeafcc712a215d063619485fa7d74ae617f290f0a7570e358c3f6e8471c4125`。

原154、其余五个natural模块和既有raw／旧bundle／旧binder保持。当前改动的bridge、两个reader和测试只由新round2绑定说明；旧47415／121aa／19ac绑定仍对应其旧源快照，不是当前源码证书。只读科学终审GO_FOR_SECOND_BOUNDED_REPAIR_PUBLICATION_AND_EXACT_HEAD_REREVIEW，新工程45／data88项及原154源哈希现场核对通过；[round2科学回执](../../artifacts/thesis_actuator_readiness_20261015_v1/SCIENCE_ROUND2_OFFLINE_REVIEW_V1.md)。待准确新head复审；自然交通、native安全／EOF／4050生命周期／城市暴露仍NOT_TESTED，本轮未启动SUMO或修改合同／算法／正式输入。


### 第二轮结果：5b08精确审查及最后pending字段P2

Review5527262368实际commit_id为5b08d28fe96fb160f51ae21a566a74ba50093db0，精确等于请求／远端。唯一新[P2 4278340629](https://github.com/yuhong-zhang202/MatsterArbeit_Rampmetering/pull/13#discussion_r4278340629)指出：每post row的rate_chain.pending_request_id及r_policy_pending_veh_h null语义尚未核对，改为虚构ID或900仍可能PASS。[原始回执](../../artifacts/thesis_actuator_readiness_20261015_v1/PR13_REVIEW_5B08_V1.json)。这不是实际native pending观测；保存材料仍只是合成观察。

Data只修这两个字段、复用五份保存材料与两个反例，随后只读科学复核；不更改runtime、算法、输入或旧证据。已到原任务两轮额外实质复审上限，不自动开展第三次完整review或资格运行。最终小修复和最后实际review版本必须明确分开，不能把5b08 review当作之后未审源通过。


### 最后小修已离线完成，超限定点复审待明确指示

Reader逐控制row要求pending_request_id精确等于该时刻最新REQUESTED ID，且pending packet rate字段必须存在并为null；选择与实际应用时刻不变。精确5b08前像对两个指定篡改的旧错误接受已真实复现；修后五保存材料＋两反例1组PASS0.314秒，无fake／native重跑。[数据最后修复](../../data/processed/thesis_actuator_readiness_20261015_v1/final_pending_fix_v1/DATA_REPORT_V1.md)，新58项绑定`e08cc79a65f8dd5d74272c244735e99845b4746e2fbb1c0909f54dd1756d805e`现场核对一致。

[只读科学终核](../../artifacts/thesis_actuator_readiness_20261015_v1/SCIENCE_FINAL_PENDING_FIX_V1.md)允许小修交付，未要求更多测试；不包含GitHub修后审查或native资格。原先两轮复审均已完成并核对精确commit，最后修后源尚未GitHub review。按上限停止自动扩审和资格推进；如用户决定追加，仅对这个准备好提交的pending两字段修复做一次定点review，不扩为第三次完整控制器审查。

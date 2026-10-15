# 自然需求执行器：最小资格准备

**当前状态：PR13为 `REVIEW_PENDING / NO_VERDICT`；非运行资格准备已完成。** 用户明确要求不再发起新的自动review，也不因其等待阻塞已授权非运行工作。现有修复、针对性测试及科学准备回执继续作为各自范围内的依据；没有把GitHub状态改判为PASS或CANCELLED。首卡14项绑定本次机械回读无漂移，src/scripts/tests相对执行checkpoint无变化；已有审查无阻碍未释放准备的实质finding。七域审计、精确卡、三方准备回执和资源保护均已交付，未发现剩余的独立非运行实施项。[准备交接状态](../../artifacts/natural_actuator_qualification_20261015_v1/NONRUNNING_PREPARATION_STATUS_V1.json)。实际自然验证仍NOT_TESTED、总体NOT_QUALIFIED；本次只调整非运行工作的依赖，不改原精确卡有条件执行授权，不生成canonical或启动SUMO。

2026-10-15。当前为**非运行实施与审查准备**；自然运行NOT_TESTED，总体NOT_QUALIFIED。唯一工作项为[Issue #14](https://github.com/yuhong-zhang202/MatsterArbeit_Rampmetering/issues/14)，分支`codex/natural-actuator-qualification`从PR13准确head `61612bf6e240d41d2ca4be95a02429f48c9ddd54`建立，[Draft PR #15](https://github.com/yuhong-zhang202/MatsterArbeit_Rampmetering/pull/15)以PR13分支为base。不得通过本记录放行SUMO或合并。

## 为什么需要这项工作

PR13已把普通供给不足与执行器故障分开，使用C−E_scheduled校正离散映射，保留真实C−N及物理短放。旧154源的96秒预排队诊断、有限诊断和五份保存合成案例，均不能替代自然需求下的持续服务、安全和完整人口审计。[方法及七项资格标准](THESIS_ACTUATOR_MINIMUM_QUALIFICATION_PLAN_20261015.md)、[文献与SUMO机制依据](../../artifacts/thesis_actuator_readiness_20261015_v1/LITERATURE_AND_METHOD_BASIS.md)。

PR13最后三行pending校验已经推送61612bf；用户明确批准追加一次定点复审，见[请求6191040336](https://github.com/yuhong-zhang202/MatsterArbeit_Rampmetering/pull/13#issuecomment-6191040336)。本资格分支不得冒充PR13本轮实际审查的代码，也不得把未返回结果记为通过。

## 不改变控制政策的实现范围

`policy.py`、`adapter.py`、`producer.py`保持61612bf行为。`bridge.py`仅增加在直接Popen后、TraCI连接前记录实际worker/native PID、PGID、SID和卡／release绑定的启动钩子；这仍是新的bridge字节，不能宣称与616完全同源。身份缺失／异组／早退时不启动运动控制。[工程设计](../../artifacts/natural_actuator_qualification_20261015_v1/engineering/PIPELINE_DESIGN_V1.md)、[进程归属补充](../../artifacts/natural_actuator_qualification_20261015_v1/engineering/GUARDIAN_OWNERSHIP_V1.md)、[只读科学设计复核](../../artifacts/natural_actuator_qualification_20261015_v1/SCIENCE_PIPELINE_DESIGN_REVIEW_V1.md)。

新`profile.py`／`budget.py`／CLI准备独立新scope和精确卡；外层guardian只管理其直接创建的专属Python worker及已核对的同组native子进程。worker异常退出后仍检查实际同组存活者并清理，未知身份／清理／EOF保留UNKNOWN和资源预留；不按进程名扫描或清理别的仿真。普通Python过程测试不是native进程行为证明。

## 实际数据审计的七项边界

新入口`scripts/natural_actuator_qualification_20261015_v1/actual.py`独立接入native provenance／bridge receipt，流式读取FCD与pre/post行，保留薄的控制账投影；旧synthetic reader保持原用途。不能重标合成材料为原生结果。具体源与待检字段见[数据设计](../../data/processed/natural_actuator_qualification_20261015_v1/design_preflight/NATIVE_READER_DESIGN_V1.md)。

1. 逐步重算C、E_scheduled、E_executed、C_selected、C_applied和真实N，分解C−N；原生FCD／TLS／ACK过线须独立成立。
2. 所有REQUESTED／SELECTED／PREPARED／APPLIED、superseded、held-red、pending与末尾未执行意图分开；未执行不补成G ACK。
3. 600秒开始E1真实占有率与原Feedback逐窗核对，包括正在检测器上的车辆；不能只用空事件fixture证明。
4. 全部相关入口、车尾、正常离网末步、warning、制动、碰撞和EOF列覆盖分母；缺失或未知不能记0次异常。
5. 全4050计划ID分清未来、已到请求时刻、已插入、已抵达、仍运行和未插入；源等待＋网内成本与独立累计式互核，不能把缺trip记录自动归作未插入。
6. 六个既有300秒评价窗完整保留，标complete／partial／unreached；终点部分周期、车尾与未满E1窗明确截尾。
7. 队列后沿、共享城市路段R/U暴露及EOF可追溯；描述性暴露不冒充因果回溢或新的30秒分类器。运行／输入／reader／环境／卡／权限均绑定准确版本。

审计程序可以给出指定字段的TECHNICAL_PASS；不能仅凭退出0或名义账相等自动给QUALIFIED。供给充足、接收可用时持续服务偏差仍须按实际结果解释，不任意创造百分比阈值，也不因“正常物理原因”删除差额。

## 第一张卡与真实权限门（批准前准备快照）

拟首身份`QUAL_NATURAL_ALINEA_R900_S17_01`，复用既有自然输入，seed17、dt1、0–4200秒、600秒起控，4050计划ID，既有六窗[1200,3000)。新包仅将输出precision从2提高到8以支持物理复算；网络、需求、车型、speedFactor、控制参数不变。原始候选输入只读，旧低精度raw不改判为高精度通过。

新增独立scope **900墙钟秒仅为提案**：worker内限870秒，清理预留30秒包含在900内，启动60秒，最低5GB空闲，无固定输出字节门。旧scope实耗475.645467625秒／余额124.354532375秒只作为历史披露，不合并可用量；新增批准缺失时可用量null。第二身份不预备，只有首项实质结果支持、审查完成且同一新scope剩余真实可用才另作准确卡；最多两次并不等于预算或权限。

精确卡只能标PREPARED_NOT_RELEASED。全部实现、离线验证、卡与三方审查材料完整后，仍必须取得本卡直接人类运行放行、新增数字预算及当前canonical release；旧批准、完整目标文字、Reviewer回复和本记录都不能替代。预备／check-card不创建raw、批准、canonical或native进程。

## 当前验证与下一步

工程实现已完成：[报告V1](../../artifacts/natural_actuator_qualification_20261015_v1/engineering/implementation_v1/ENGINEERING_REPORT_V1.md)、[58文件绑定](../../artifacts/natural_actuator_qualification_20261015_v1/engineering/implementation_v1/ENGINEERING_BINDING_V1.json)，SHA `b5954b752ef9c06d8f5d18ece87ab150ebe2441bcaa7961fe6a4396105f7fee6`，主代理逐项复核无漂移。四个有界方法均有最终PASS；不是一次最终完整suite。首次fixture路径错误及沙箱拒绝ps的UNKNOWN保留，允许读取ps后同一普通Python正常／超时／父进程早退三组合PASS1.012秒。未来native运行仍需实际进程组观察权限，这些普通进程结果不认证SUMO。

独立data实现已完成：[报告V1](../../data/processed/natural_actuator_qualification_20261015_v1/implementation_v1/DATA_IMPLEMENTATION_REPORT_V1.md)、[22项绑定](../../data/processed/natural_actuator_qualification_20261015_v1/implementation_v1/DATA_BINDING_V1.json)，SHA `fbacd0b9f5066447b4cc5d60a94db71e6e879dbc71d4c1db5d24a9b8bccd75dd`，主代理逐项复核无漂移。9组整体PASS0.242秒后，仅补强非空E1方法PASS0.002秒，未重跑全组。E1已测试两车道3／6秒占用→10／20%→原Feedback900降至620的计算，不是新交通请求矩阵；流式两帧join是已保存假材料的schema投影与构造XML，不是原生运行。队列后沿、queue XML、终点身份与截尾名单已经接入；保留一个binder旧schema KeyError并纠正，只读绑定失败不改动数据。

执行前失败尾可能使旧纯数学完整周期校验为UNKNOWN，新native封装另存已观察C/N前缀、六窗、请求／意图／last setter／故障，不能把UNKNOWN伪报通过。全规模内存、用时、native物理与EOF均未实测。[工程独立schema兼容](../../artifacts/natural_actuator_qualification_20261015_v1/ENGINEERING_NATIVE_SCHEMA_COMPATIBILITY_V1.md)确认173项实际源闭包完整且无动态状态文档递归；[只读科学终审](../../artifacts/natural_actuator_qualification_20261015_v1/SCIENCE_FINAL_IMPLEMENTATION_REVIEW_V1.md)为GO_FOR_FIRST_EXACT_PREPARED_NOT_RELEASED_CARD_PREPARATION，无阻碍首卡准备的实质finding。首卡已唯一生成且只读validate-prepared exit0，见下节；尚无运行输出，未运行SUMO、TraCI或native --version。正式协议仍空且未冻结，未修改DECISIONS、导师意见或研究设计。

## 实际首卡与唯一下一步

可执行checkpoint `b6c60b927fc71a8750f5674f2cf168824b78cf05`。实际卡SHA `b73c678130604d1cef41dd5ecb70a79cc868084e91ae5033cc179393c25f6982`，173源摘要 `c2f00d7f66ea66e331e436248bf34d510fc8ba11a99b16792cd80e18f61055b2`。唯一prepare0.130秒／只读validate0.107秒均exit0，不代表native测试。实际XML、4050人口、600／4200／六窗、E1两lane30秒、precision8、141环境hash和所有源／输入经工程→独立data→只读science回读，无阻碍未释放交付的实质问题。[实际卡](../../artifacts/natural_actuator_qualification_20261015_v1/engineering/packages_v1/QUAL_NATURAL_ALINEA_R900_S17_01/card.json)、[三方14文件绑定](../../artifacts/natural_actuator_qualification_20261015_v1/card_preparation_v1/THREE_ROLE_CARD_BINDING_V1.json)，绑定SHA `fd4d1bdb1a0d7c8350ccd11053ca987931196f27590b5746b66d9fb0bd29083b`。

全部独立实现／离线验证／精确卡准备已完成；[RUN_REQUEST_V1](../../artifacts/natural_actuator_qualification_20261015_v1/RUN_REQUEST_V1.md)明确真实预算及仅本卡解除noSUMO的范围，**它不是批准**。PR13准确616定点review仍Running、未给结论；只有该审查无未处理实质阻碍且真实数字预算／精确人工运行批准／canonical／PID观察权限与实时资源门均有效后，才可仅本卡一次技术运行。卡执行false、观测null；native安全、持续C/N、供给／接收分支、城市结果和性能仍NOT_TESTED，总体NOT_QUALIFIED。不自动预备第二卡或开展正式矩阵。

## 后续直接批准：仍等待review条件

用户已明确回复“批准独立900秒并有条件释放上述首卡”，仅对b73c6781卡一次非正式技术运行解除noSUMO；[直接授权非执行回执](../../artifacts/natural_actuator_qualification_20261015_v1/HUMAN_APPROVAL_RECEIPT_V1.md)。新增独立总900已获真实批准，本地账已耗0／余900／start0、旧账不pool，无unknown预留。原卡和14文件准备绑定保持不变；卡内资源提案状态是生成时快照，实际数字批准由独立账记录绑定。review准确616仍Running，所以不创建canonical/raw/guardian身份、不启动SUMO。review完成无实质阻碍及其余实时门有效后，只能本卡一次运行；第二身份仍无放行。以上批准不是native通过或资格提升。

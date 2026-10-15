# PR13：完整周期欠放的有限诊断用途修复

2026-10-15。状态：新隔离版本完成工程→独立数据→只读科学后审，可交现有Draft PR13针对性复审；未执行原生仿真，未建立普通服务或正式实验资格。

## 审查与问题

本轮GitHub review已完成。原始review API的`commit_id`为`9a9c96ede571af3a45790f0049d160511577a97e`，不是请求中指定的`69c25796…`；二者间的补档提交没有改变原154执行源。唯一新增实质反馈为[P1：两车断言应限定于饱和供给诊断](https://github.com/yuhong-zhang202/MatsterArbeit_Rampmetering/pull/13#discussion_r4277926222)。[版本和反馈回执](../../artifacts/pr13_underdischarge_fix_20261015_v1/REVIEW_FEEDBACK_V1.json)。

原ledger在下一周期准入前要求上一完整周期N=2。实际入口允许空front且receiver available的状态，因此N0/1不必由执行器故障造成。若直接将此路径用于普通资格验证，会选择性截断供给不足、未及时就绪或接收受限的轨迹。既有两条96秒轨迹的完整周期均N2，此反馈不改写其有限观测结果。

## 最小修复及适用范围

新`src/candidate_a_service_scope_20261015/`包含policy、adapter及实际loop接线。adapter构造和loop入口均要求显式`FINITE_PACKET_DIAGNOSTIC_ONLY`，拒绝普通资格／正式用途；用途名称本身不证明两车实际可服务。

在原adapter所有安全、信号、入口与ACK核查成功后，新版本评估已完整周期。N0/1保留为`DIAGNOSTIC_TARGET_NOT_MET_CAUSE_UNESTABLISHED`：两车诊断目标未满足、原因未建立、服务未获资格。记录逐步storage车辆ID、原车辆状态、receiver和native WAIT观测；不凭过线数量推断供给不足或故障。随后停止，不注册下一条指令、不选择下一周期或追回欠放。原始C、E、N、C−N均保留，无offset、重置或新增补偿政策。

评估也覆盖恰好在观察终点结束的完整周期；末部分周期不按完整两车配额判定。原N>2、重复入口、UNKNOWN及安全硬门继续异常停止；真实安全检查优先于中性服务判定。新loop在执行前独占创建证据文件，并在退出时独立保存事件和结构化停止记录，避免原loop尚未flush时丢失最终评估。

本修复提供**有限诊断的正确用途和中性停止**，没有提供普通供给／接收受限条件下的持续控制能力；后一能力仍为下一阶段阻碍。初审讨论的欠额扣除或继续运行策略均未实施，也没有被记录为正式科研决定。

## 验证与证据

工程使用纯FakeWorld经新adapter和继承的实际loop验证。命令：

```
.venv/bin/python -m unittest discover -s tests/candidate_a_service_scope_20261015 -p 'test_scope.py' -v
```

最终5个方法通过，exit0、35.374秒；覆盖空／单车／晚到／native WAIT的中性停止、N2原账及选择等价、partial与pending、完整终点、超额、UNKNOWN／真实安全优先及实际用途门。此前两轮fixture失败分别保留：首轮错误假设反馈初值750及不合法partial检查点，次轮合法接收门拒绝尚有内部前车的fixture；只修假数据，不放宽原门。首轮输出只有工具原记录和明确标注的摘要，未伪造完整字节日志。[工程报告](../../artifacts/pr13_underdischarge_fix_20261015_v1/engineering/ENGINEERING_REPORT_V1.md)、[9文件工程绑定](../../artifacts/pr13_underdischarge_fix_20261015_v1/engineering/ENGINEERING_BINDING_V1.json)。

独立数据使用新`pr13_service_scope_audit_20261015` reader，从按时间排列的请求、逐ACK实际入口与完整周期边界重新构造C/E/N。四个既有假案例中，空供给及单车完整终点分别在1210停止，C/E/N为25/12、2、0及25/12、2、1；末partial案例C/E/N为5/2、2、4（含末部分包两车，E没有补为4）；硬制动案例仍优先保留异常。原pending算例C17/24、E0、N1，未伪报应用。九项最小数据损坏均拒绝，观测核账完整与诊断目标未满足分别记录。[独立数据报告](../../data/processed/pr13_underdischarge_fix_20261015_v1/reader_v1/DATA_REPORT_V1.md)、[最终数据绑定](../../data/processed/pr13_underdischarge_fix_20261015_v1/reader_v1/FINAL_BINDING_V1.json)。

数据首条主命令完成四案例及检查后，在生成绑定时因相对路径处理错误exit1；原代码和失败记录保留。仅修新reader路径处理后，同一已保存数据核账与绑定exit0，没有重跑案例，也未声称完整主命令重新通过。

只读科学终审为`GO_FOR_BOUNDED_OFFLINE_P1_SCOPE_FIX_AND_REREVIEW`，无阻碍本限定修复送审的实质Blocker/Major；递归核对24项绑定及历史154源一致。结论仅支持新入口的误归因／用途范围修复，不能声称已解决普通受限服务持续控制。[科学终审记录](../../artifacts/pr13_underdischarge_fix_20261015_v1/SCIENCE_FINAL_REVIEW_V1.md)。

## 版本、文档与交接

原154源、卡、权限、raw、旧reader及终点processed修复版本保持原字节；工程逐文件哈希复核154/154一致。新代码没有原生启动函数、卡或release。原ALINEA reader失败与processed后分析通过仍按各自版本保留，本修复未合入该终点后分析处理。

Stage6探索结项、Candidate A NOT_QUALIFIED、A1 UNRESOLVED、空未冻结正式协议保持。没有新SUMO／TraCI连接、参数矩阵、模型改变或PR合并。最小更新PROJECT_STATE与WORKLOG记录实际反馈及新离线版本；正式协议、DECISIONS、导师反馈、论文结构和AGENTS不变。README的既有运行方式没有改变。

下一步：向现有Draft PR13发布限定修复，并申请针对性复审。复审通过也不构成用户验收、通用控制能力或正式运行授权。

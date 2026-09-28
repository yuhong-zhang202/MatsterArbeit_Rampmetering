# Luna High Handoff — Offline Preparation First

这是未来任务的交接文本。阅读本文件不授权SUMO，也不代表工程准备已执行。用户如选择交给Luna，可明确授权下面的离线准备范围；每个仿真start仍必须另批exact card/hash。

## 可复制的下一任务说明

继续 Masterarbeit-Ramp-Metering，执行 **ramp-induced mechanism validation 的离线工程准备阶段**，不是仿真执行。

先做AGENTS规定的Context Preflight，然后完整读取：

- `docs/methodology/STAGE6_RAMP_INDUCED_BREAKDOWN_VALIDATION_PLAN.md`
- `docs/methodology/STAGE6_RAMP_INDUCED_BREAKDOWN_SCIENTIFIC_REVIEW.md`
- `docs/methodology/STAGE6_RAMP_INDUCED_BREAKDOWN_LUNA_EXECUTION_SPEC.md`
- `docs/methodology/STAGE6_RAMP_INDUCED_BREAKDOWN_LUNA_SPEC_REVIEW.md`

你的目标是按Execution Spec的A0–A2完成离线准备，输出经工程/数据/科学审查的control exact-card草案，或者列明具名IMPLEMENTATION_BLOCKER。不是承诺一定能出卡。

使用simulation_engineer做新目录适配和纯mock测试，data_analyst独立核对数据合同，最后scientific_reviewer只读审查。你负责协调、修复required issues与最终报告，不用自己的检查代替独立审查。

禁止SUMO、netconvert、TraCI、版本命令、任何smoke/scientific run；禁止跑旧launcher/main/test脚本造成历史写入。raw只读。新适配器只改I/O/run mapping及已声明数据合同，保留classifier科学逻辑。参考空catalog必须区分已验证0事件与缺失；ledger必须处理arrival=-1等sentinel。不得自动修历史offset或revision03。

按SOP逐项交付context receipt、source/input/code manifests、静态XML/科学差异白名单、matching方案、PRE screen适配、区间R crossing实现、生命周期账本实现与fixtures、urban/source证据覆盖表、结论状态机fixtures和readiness register。新运行数据尚不存在，不能把未来raw审计写为PASS。

优先只物化`RI3350_CTRL_S17_attempt1` control卡。transition仅保留设计/静态配对方案，不制作已授权卡；control尚不存在时不宣称它已允许transition。若R01–R09不能关闭，停止在具名blocker，不创造新阈值、改变随机分布或新增observer。全部required issues关闭后，输出control卡revision/hash和“等待用户批准，0 starts”。

报告逐项列出已完成、未完成、失败/UNKNOWN、使用的证据与hash。此任务的完成条件是可审查的离线准备交付或明确blocker，不是baseline成功。O2仍NOT_RESOLVED，Stage6仍PARTIAL。

## 后续任务不得混在一起

1. 用户批准control exact card →仅control单start→停止并完整postrun审查。
2. control合格→单独申请transition制卡/审批，不自动运行。
3. 用户批准transition exact card→仅transition单start→停止并pair审查。
4. 最后输出机制结论与baseline适用性两个轴，不能以一个P label替代；任何branch都不自动放行3199.2、seed23、B/C。

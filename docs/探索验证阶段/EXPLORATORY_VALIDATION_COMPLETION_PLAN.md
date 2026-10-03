# 探索验证完成标准、缺口与后续分阶段方案

日期：2026-09-09。版本：1。执行状态更新：2026-09-13。状态：**Stage 3与Stage 4已完成并通过；Stage 4累计4/4/0/0且无重试，snapshot-bound 116/116测试和最终科学复审通过；Stage 5 T50–T53及Astra复审补正已完成，T54需按修订包由用户结项；Stage6详细计划已制定，实际执行尚未开始。** Stage 2 / G2 保持 accepted。

## 0. 先读本页：我们要做到什么程度

目标：在**不加入匝道控制器**的前提下，判断当前合成场景是否具有研究高速公路与城市道路权衡所需的可观测行为，或具体说明缺哪一环；随后由我们提出正式实验设计，交 Robert 审核。无控制仍保留入口匝道、城市道路与既有固定配时城市信号。

原始文件交付没有启动 SUMO、netconvert 或数据重算，也没有修改研究决策或正式协议。2026-09-12 后续执行完成 Stage 3 档案诊断和 Stage 4 T42。用户随后以“批准按 `docs/STAGE4_T43_LAUNCH_CONFIRMATION_PACKAGE.md` 执行 T43。”精确授权 [T43确认包](STAGE4_T43_LAUNCH_CONFIRMATION_PACKAGE.md)。Tier 1 的 qMain=3500 与注册规则选中的 Tier 2 qMain=3650 均已完成 seeds 17/23 并归档；最终分析和科学复审已完成，累计 SUMO/netconvert/TraCI/GUI 为 4/4/0/0，重试为0。2026-09-13 用户请求对 Stage 3/5 独立复审，最新更正及验收建议见 `docs/STAGE3_STAGE5_ASTRA_REVIEW_20260913.md`；T54仍待用户接受。正式协议仍未修改。

总体路线（2026-09-13用户修订）：**Stage 3：档案诊断 → Stage 4：定点验证 → Stage 5：上一轮探索评估结项 → Stage 6A–E：specific_obstacle诊断与验证、用户确认解决 → Stage 6F：正式设计草案与Robert审核 → 另行批准正式执行。**Stage6A–E仍属探索/场景验证；未解决则走Robert障碍咨询，不能提前编写正式设计。当前执行细则以 `docs/STAGE6_OBSTACLE_RESOLUTION_EXECUTION_PLAN.md` 为准，不要与旧Stage2的S3–S5混淆。

建议优先批准 Stage 3 零新仿真工作；Stage 4 只有明确证据缺口才启动，不预设一定需要。按照用户偏好，集中导师讨论放在探索总结和设计草案之后；遇到无法自行确定的关键研究选择可提前带问题讨论，不无限试验。

## 1. 文献结论及适用限制

检索方法、原文链接、版本和采用边界见 [文献核查](../../literature/EXPLORATORY_VALIDATION_REVIEW_20260909.md)，以下 L1–L12 对应该文件来源表。

- L1、L2：有效性针对用途，必须事先明确研究问题、观测范围和判断依据；“表格齐全”不等于模型适用。
- L3、L4：实现错误检查、实测校准和研究比较是不同层次。没有现场真值，不要求也不声称经验校准通过。
- L5、L12：随机重复和敏感性需单列；探索两个seed不能替代正式精度或统计设计。
- L7–L10：需求输入、实际入网、路内排队、断面通过、时间窗和未完成记录须区分。

本方案保留六类产出，另设敏感性与随机性门。量化技术门是本项目提出的质量合同；文献支持的是原则，不是本项目具体行数、运行预算或统一拥堵阈值。禁止套用 GEH<5、85%、四seed、固定15分钟或必达10% Capacity Drop作为通用完成标准。

不要求探索已经证明ALINEA有效、找到sweet spot或完整扫描需求空间。也不把“当前场景无论如何都不适用”作为先验结论。

## 2. 已有证据与缺口基线

权威状态为 [PROJECT_STATE](../PROJECT_STATE.md)，接受边界为 [Stage 2完成报告](STAGE2_COMPLETION_REPORT.md)、[G2复审](STAGE2_G2_REVIEW_20260909.md)。Stage 1技术证据记录在 PROJECT_STATE 的 Stage 1 Instrumentation Status 与相应 WORKLOG。

| 证据ID | 已核事实 | 可以复用 | 不能据此推断／仍需做什么 |
| --- | --- | --- | --- |
| E01 | Stage 1 技术场景、M/R/U/X区分、参数入口、车辆账目及基础测量已完成 | 路网与分析基础；版本化代码和测试记录 | 技术成功不是容量验证；旧upstream E1污染问题以后续修复结论为准 |
| E02 | 内部lane核算、命名E2覆盖、几何v4及局部回放已核 | 空间映射和已审核轨迹 | 494.87 m路径不等于允许/有效储存容量；局部回放不覆盖八条运行 |
| E03 | C/ML/MH/RL×seed17/23，复用1条、新跑7条，8条有效记录 | 固定矩阵、预算、归档与原始输出 | 四输入设置不是四种交通状态；历史low/stress时长不同，不补成匹配参考 |
| E04 | 232归档文件、14,564车辆、4,320 E1行、2,100 R首次下游事件及198同seed差值核验通过 | revision_04和补充核验入口 | 不能把旧checker单独说成全部原始字段独立验证 |
| E05 | R在1500前首次下游观察：C36/40、ML67/69、MH0/0、RL38/40 | 真实数量及1Hz事件括号 | 只有MH需求期为零；不是整个Stage2无合流；不是精确物理过断面时间 |
| E06 | 八条最终全部入网到达，最晚到达2558s；各条仍有R/U在1500后入网 | 端点账目与迟到入网证据 | 不代表需求期实现、不代表零入流恢复；未来更长需求期未验证 |
| E07 | 历史基准46s匝道末端、192s储存段、412/414s共享道R/U首次停驶 | 已记录的空间传播线索 | 技术停驶不等于正式拥堵；八条分别的传播/首次回溢尚未完整分析 |
| E08 | 两内部M-only E1聚合可用；普通E1无vehID；精确逐车排程未独立核验 | 声明断面和可核端点 | 不补造逐时网外排程；不称全主线上游状态或逐车E1零遗漏 |
| E09 | 主线输入提高时R通过变少、U积压变大；没有建立主线Breakdown/Capacity Drop | 有限单因素响应 | 仍缺主线侧性能恶化与合流状态的充分联系；无控制数据不证明控制收益 |

核心已有事实置信度 High；场景用途适配仍 Unknown/待证据；新方案执行可行性 Moderate，必须经过实际验收。

## 3. 六类必交产出

| 产出 | 具体内容 | 最小可检查形态 | 去向 |
| --- | --- | --- | --- |
| O1 场景与测量说明 | 每种核心观测的lane/车辆/时间/单位/边界；编译拓扑、实际插入位置、信号link | `measurement_contract.json` + `network_observation_map.csv` | Stage3 |
| O2 需求与车辆账目 | M/R/U/X计划总数、入网/到达/网内/网外端点、完整性/Unknown | 复用既有表，新增覆盖审计；新run另派生 | Stage3/4 |
| O3 代表条件行为诊断 | 八run逐条件停驶、传播、R下游、U共现、M与下游时序及替代解释 | §6规定5张表；最多3张必要静态图；正文逐run摘要 | Stage3/4 |
| O4 场景适用性判定 | Q1–Q4主张、支持/反证/未识别、关键缺口 | `claim_evidence.csv` + `suitability_review.md` | Stage3初判，Stage5结项 |
| O5 方法时长与敏感性 | 完整时域、A/B/Post、30/60/120s重聚合、seed分列、输入与结构限制 | `sensitivity.csv` + 时长/边界说明 | Stage3/4 |
| O6 探索总结与设计交接 | 可沿用/有条件/待验证/导师选择、不支持的用途、后续设计问题 | `handover_register.csv` + `EXPLORATORY_VALIDATION_REPORT.md` | Stage5 |

以上文件为**计划接口，除明确复用项外尚不存在**。O3重用现有车辆/E1/合流表；不再生成同义副本。O5为必验维度，不被埋在报告备注中。

## 4. 量化完成门：不使用加权总分

状态字典：`passed / failed / not_verified / not_applicable`。NA必须有范围理由，经reviewer确认；未知核心项不能填NA。全部分母在运行前登记，不得靠删除失败项提高完成率。

| 门 | 量化指标与计算 | 完成线 | 来源性质 |
| --- | --- | --- | --- |
| G01 来源与运行覆盖 | 已登记且有终态run/预定run；必需源hash通过/必需源；未知身份数 | Stage3为8/8；必需来源100%；无解释身份冲突=0 | 项目技术合同，L1/L3支持原则 |
| G02 计数与身份 | 重复(run,time,id)、未知lane/ID；P−E−O、E−A−N（适用端点） | 未解释重复/未知=0；整数残差=0；32个run×class全部分列 | 技术恒等式；端点资格见§5 |
| G03 测量覆盖 | O1核心指标元数据完整率；原始与派生计数/时标对账；必需区间缺失 | 元数据100%；整数完全一致；Stage2每E1 90个30s区间；缺失=0或阻断所依赖主张 | L7–L9，项目技术门 |
| G04 行为诊断 | 8run×5问题证据单元完成率：入网、起点/传播、M/下游、回溢、U；未识别须定位原因 | 40/40有结果或明确缺证据说明；其中支持性结论不得依赖缺证据单元 | 诊断记录完成不等于用途通过 |
| G05 新处理可信性 | §7.3的12种失败模式测试；核心数量独立重算覆盖；Blocker/Major | 12/12预期测试通过；核心数量100%独立核对；未关闭Blocker/Major=0 | 未来执行未验证；不是复测既有全部工程 |
| G06 敏感性与随机性 | 3种输入对照×2seed；4条件×2seed；8run×3聚合×2窗口×2量（仅M-only内部E1合并） | 对照6/6、seed单元8/8；q/v登记96/96；对应48条聚合时序均保留并比较形态，缺值附资格；零隐藏符号翻转 | Proposed分析覆盖；不要求方向一致、不宣称功效 |
| G07 用途评估 | Q1–Q4逐项：量化证据、替代解释、主张状态、影响、reviewer意见 | 4/4完整；关键unknown计数明确；按下方出口决定ready，不能只看表完成率 | L1用途门；有科学判断，不能由Sol low自动打勾 |
| G08 交接 | O1–O6完整率、继承清单、未来每项拟用量是否有资格 | 6/6产出；§10交接项100%分类；未披露关键限制=0 | 管理门，L1/L2/L12 |

浮点技术一致性：若两程序从同一已舍入XML值按同公式计算，以 `max(1e-9, 1e-8×abs(reference))` 比较计算误差；若比较再次舍入的CSV列，另加该列最后小数位的半单位。精度来自实际输出与写出格式，逐列写入合同。此容差不表示模型对现实误差。时间按原始离散标签/括号核对，不给1Hz事件伪造亚秒精度。

不设“入网率≥95%才有效”“截止必须清空”“所有seed同方向”“主线速度降20%才合格”等门。它们会把真实拥堵、随机差异或无预期现象筛掉。缺失数据和真实没有观察到事件是两种状态。

### 4.1 Q1–Q4：用途判定必须回答什么

- Q1 **可观测性**：关键主线/匝道/城市通行与等待是否都在声明范围可观测？每类至少一个实际流动量和一个状态/积存量，并列单位、分母、完整时序；边界缺口是否影响所选用途？
- Q2 **高速公路侧**：是否有与合流时空关系一致的性能受损证据？逐候选工况报告速度、通过量、占有率或路内积存中至少两类量的完整配套时序，以及持续样本、范围、差值。两条量并存不是自动因果证明，主线高输入/高速度本身不满足本项。
- Q3 **城市侧**：是否观察到R积压达到共享道路、U暴露及其通行表现？给R路径和U位置/时序、TLS上下文、样本数/持续支持、U端点；单有网外等待或红灯停驶不足以确认回溢导致的影响。
- Q4 **同一场景下的研究关联**：Q2与Q3是否来自一致的场景版本和可比较条件，存在以后研究放行权衡的合理基础？主线与城市问题不必每秒同时发生，但必须解释其关联；不得用两个无关场景拼成“双向权衡”。无控制资料只评估适用性，不验证控制可逆性或收益。

每条主张只能取 `supported / contradicted / not_identified`，附观测值、时空位置、反例和替代解释。不得把非零差值直接解释为研究意义或显著性。不强制四交通状态/Breakdown/Capacity Drop均出现。若未来论文把Breakdown作为核心问题，其“未建立”就是核心缺口，不能改名绕过；改变问题需用户/导师讨论。

### 4.2 两种完成、三种结论

分别维护 `assessment_completion` 与 `design_readiness`：

1. **`completed / preliminary_ready`**：O1–O6、G01–G08齐备；Q1–Q4支持所声明的无控制场景用途；影响该用途的未解决关键缺口=0；reviewer通过；用户接受探索结项。仅允许准备正式设计，不是正式执行或现实校准通过。
2. **`completed / specific_obstacle`**：证据支持一项具体障碍，报告问题及最小备选；不能说场景验证通过。可以带约束设计/备选给Robert。
3. **`completed / unresolved`**：规定工作完成，但关键问题仍未识别；必须列缺什么观测及为何当前预算无法回答。需要问题驱动的决定，不能无限追加运行。

关键原始来源缺失、分析错误未关闭则为 `blocked`，不能归入“已完成但无现象”。Stage2的accepted不变；这里评估的是更广的用途。

## 5. 统一分析合同（Proposed）

1. 固定旧批次为 `stage2_completion_20260909_v1`；选择 C17/C23/ML17/ML23/MH17/MH23/RL17/RL23。档案按ledger selected_attempt→source map→项目归档解析，禁止最新目录glob或回退/tmp。
2. 旧八条需求结束1500s、记录结束2700s；A=[0,1500)、B=[300,1500)、Post=[1500,2700)、Full=[0,2700)。B只是切窗，不是稳态预热。FCD和TLS保留原标签。
3. `E_c(t)=Σ1[0≤depart_i<t]`，`A_c(t)=Σ1[0≤arrival_i<t]`，已核覆盖才计算`N=E−A`。P是XML计划总数；只在已完成需求安排且账目资格通过的1500/2700端点计算`O=P−E`。中途逐ID排程仍未核验，不生成精确连续O曲线。
4. FCD技术停驶沿用`speed≤0.1m/s`以保持旧口径，明确不等于拥堵。`ΣH(t)Δt`为采样停止车辆秒；`Σ1[H(t)>0]Δt`为区域停止采样支持秒。每个episode记录首末标签和样本数，缺帧即断开，不说精确物理起止。
5. 区域至少一车停驶与同一车连续停驶分别计算，车辆接替不得混为一车长停。区域来源由编译lane决定，包含内部lane且互斥；观测到所有在范围的lane，不静默忽略未知者。
6. R首次下游沿用`(previous_label,first_downstream_label]`；跨箱界标不确定数量，不硬配精确30s过线流量。若缺前帧仍可记录首次观察，但事件括号为unresolved。
7. 内部E1总流量`q=3600ΣnVehContrib/T`（两lane合计，非每lane）；速度按贡献数加权。无贡献速度null；逐lane占有率单列，不直接加总为路段密度。不同cohort/空间的检测点差值不能自动解释为R流量。
8. 主线降速或队列采用连续描述：最小/分位速度、全时序、最长观测段、q/occupancy配套、lane位置和边界。当前不预定“80%参考速度×90s”阈值；如后续需要状态分类，必须先审批参考工况资格、定义及敏感性规则。
9. TLS由路径对应link index解析，不能取state字符串第一字符代表所有车辆；无对应link标unknown。绿灯期共现停驶可报告，不足以证明R导致U反事实损失。
10. 只对同seed的run-level量做ML−C/MH−C/RL−C，列基准、处理、差值、单位、分母和窗口。改变需求不保证相同ID使用相同随机序列，不做伪逐车因果配对。
11. 敏感性：仅将两条M-only内部E1合并后的原生30s数据重聚合为60/120s，A从0、B从300各自起箱；完整合并原生区间，尾部保留真实短箱、用真实时长，不删尾、不按比例拆跨窗大箱。两种q/v×八run×三个聚合×A/B=96整窗记录；这是重聚合守恒检查，不独自证明形态不敏感。另保留48条(run,聚合,窗口)时序，每条含q/v；逐run/窗口比较三个粒度的峰谷值、峰谷所在时间范围及可观察高低段持续支持，不能把箱均值极值当瞬时极值。原生下游E1时序独立报告，若增加同样敏感性则另设分母，不混入96。Post/Full继续完整报告。
12. 三种敏感性分别标记：输入扰动已有6组配对；随机性为同条件两seed分列；结构/行为假设敏感性尚未检验，不以时间重分箱替代它。需要结构检验时走Stage4。

## 6. 文件、责任与中断恢复

主代理独占docs；simulation_engineer负责受批技术实现/配置及运行；data_analyst负责分析、表图和独立数量核查；scientific_reviewer只读且审查结论。每位代理先做项目Context Preflight。不允许两个代理同时编辑同文件。Sol low负责按清单调度，不能替代专业判断，也不能保证任何模型完美执行。

执行批准后创建唯一新批次（例：`stage3_baseline_diagnostic_<YYYYMMDD>_v1`，日期取实际执行日；名称冲突递增版本，不覆盖）：

| 内容 | 计划写入位置 |
| --- | --- |
| ledger/合同 | `data/processed/<batch>/`，执行可更新ledger；合同变更另编号 |
| 分run新分析、manifest/核验 | `data/processed/<batch>/runs/<run_id>/revision_01/`；汇总另建`aggregate/revision_01/` |
| 五张新表 | 分run写`results/tables/<batch>/runs/<run_id>/revision_01/`，最终五张同名表写`aggregate/revision_01/`：`coverage_audit.csv`、`lane_class_timeline.csv`、`stopping_episodes.csv`、`spatial_propagation_evidence.csv`、`condition_evidence_summary.csv` |
| 新派生审核 | processed下`claim_evidence.csv`、`sensitivity.csv`、`verification.json` |
| 最多3张静态诊断图 | `results/figures/<batch>/`，同单位同列统一坐标 |
| 阶段报告 | `docs/STAGE3_BASELINE_DIAGNOSTIC_REPORT.md`（若已存在则新版本，不替换历史） |
| 新代码/测试（待实现） | `src/analysis/analyze_stage3_baseline.py`、`tests/test_stage3_baseline.py` |
| 后续Stage4新运行归档 | 批准注册表指定的`artifacts/<stage4_batch>/runtime_archive/<attempt>/`，不写data/raw |

新ledger最少字段：`plan_version,authorization_quote,stage,steps,status,batch_id,source_runs,input_hashes,code_hashes,measurement_contract_path,outputs,checks,limitations,resume_point,actual_sumo_starts`。每步`pending/running/completed/blocked`和证据路径。Stage3预算固定0。

每张表关键schema（英文列名，单位写进列名或unit列）：

- coverage：`run_id,output_id,path,sha256,schema_version,time_count,duplicate_count,unknown_id_count,unknown_lane_count,missing_intervals,status,reason`，主键run/output；缺口明细引用processed记录。
- lane timeline：`run_id,seed,time_s,lane_id,region,is_internal,class,present_count,stopped_count,speed_sum_mps,speed_n,min_path_position_m,max_path_position_m,position_mapping_status,tls_link,tls_state,coverage`。主键(run,time,lane,class)；采用稀疏行，仅present>0输出；同时保存完整`frame_registry.csv`（run,time,frame_present），只有frame_present=true时缺少合法lane/class行才解读为0。未知身份不省略。
- 路径位置由O1定义原点、正向、各条lane在R路径的累计起点及内部lane次序；非该路径的M/U位置留null并标not_on_R_path，不能把不同lane本地pos相加/比较。位置范围取该行车辆min/max。
- episodes：`episode_id,parent_episode_id,run_id,class,region,kind,vehicle_id_or_null,observation_domain,stop_definition_id,sampling_period_s,first_label,last_label,sample_count,support_seconds,censor_left,censor_right,gap_reason,TLS_context`。先Full建episode（parent_episode_id=null），再以A/B/Post切片并引用Full的episode_id；因窗口截断与源缺帧截断分别记录。主键episode_id。
- propagation：`run_id,chain_id,ramp_end_event_id,storage_event_id,internal_event_set_id,shared_R_event_id,shared_U_event_id,cooccurrence_support_s,TLS_context_id,contradiction_ids,status,reason`，复杂事件集合放processed关联表，CSV仅引用ID。
- condition summary使用long form：`run_id,condition,seed,window,entity,metric,value,unit,denominator,qualification,source_event_id,reason`，主键(run,window,entity,metric)。R/U、q/v分别成行，不把多值塞进一格。
- sensitivity long form：`run_id,detector_group,aggregation_s,window,metric,value,unit,n_contrib,covered_seconds,qualification,residual_vs_30s`，主键前5列；固定detector_group=M-only_internal_merge_entry。48条箱级时序放processed `aggregation_timeseries.csv`，列run/group/window/aggregation/bin_begin/bin_end/q/v/contribution/qualification。

G05的100%独立核对集合固定为：所有run/class端点账目；所有lane/class/time的present/stopped；全部区域及同车episode的first/last/sample_count/support/censor；全部R首次下游和前帧；全部共享R/U共现支持；全部96个G06窗口值。核验器从原XML独立重建，不导入生产聚合/episode函数。TLS/link和路径静态合同由工程/reviewer另核；数量复算不证明空间定义正确。解释用代表车辆抽查不能替代该集合的全量数量对账。

重启从ledger最早未完成步骤接续；已通过且源/合同/代码hash未变的run输出直接复用。中断的部分输出保留并标incomplete，在新revision重做该run，不向未知状态文件追加；不得删旧结果。running的模拟attempt先找进程状态/已登记runtime/输出，不自动重跑。源文件、Stage2归档、revision_04、补充核验receipt及历史快照只读。当前ledger的G2批准改变了元数据hash，旧receipt指批准前版本；不得据此认定车辆输出损坏或重写旧receipt。

## 7. Stage 3 — 现有八条档案的场景适用性诊断

**进入条件：用户明确批准本阶段及§5分析合同。新增SUMO=0；不运行netconvert、不改变场景，不添加控制器。**

### 7.1 T30：接续与来源登记（primary + engineer）

1. 读AGENTS、PROJECT_STATE、DECISIONS、空协议状态、最近WORKLOG、本计划及两份Stage2最终报告。
2. `git status --short`留存起始状态；不提交、不重置、不移动原文件。
3. 建立§6新批次和ledger。登记8个selected attempts、source maps、运行版本与时窗。
4. 对将使用的文件核hash和存在性，复用已通过核验；进入新解析前执行下面两个只读检查各一次，已在本次执行会话通过则不重复。

```bash
.venv/bin/python data/processed/stage2_completion_20260909_v1/revision_04/independent_verification.py --check-only
.venv/bin/python data/processed/stage2_completion_20260909_v1/g2_review/supplemental_verification.py
```

第二条不要加`--record`。旧receipt不覆盖。代码已存在；这两条与下文待实现接口不同。

**出口：**G01；已登记运行8/8，new SUMO=0；缺原始文件则列blocked，不通过新跑掩盖缺失。

### 7.2 T31：实际网络、空间与信号合同（engineer → reviewer）

1. 从8份归档读取network、demand、additional、sumocfg、summary。以hash相同的静态结构去重阅读，但逐run身份都登记。
2. 列主线→内部连接→下游、匝道全部内外lane、城市共享与分流路径。给每个观测量指定空间范围。
3. 核对E1/E2实际编译位置、length、后继范围；复用几何v4，不重新绘制同一几何。Stage3的E2默认只复用空间核验，标coverage_only，不声称重算全部E2指标；若确需新增E2指标，先在合同登记所需原始输出和语义/核验范围，不扩大“全部核验”声明。
4. 对TLS解析movement/link index；对主线/匝道路权仅记静态事实，不把priority数值当成动态受阻的已证原因。
5. 从实际tripinfo departPos/departLane与FCD首次样本核查车辆在哪些位置入网；逐class/入网lane报告位置范围及离合流点距离，区分原始实际departPos与第一FCD样本位置。
6. reviewer核对合同，明确哪些动态机制无法从1Hz FCD/静态结构识别。

**出口：**O1元数据100%；未知lane/link若影响核心主张，挂入G07缺口；不改几何/插入参数。

### 7.3 T32：最小离线分析工具（engineer/data_analyst 顺序交接）

新接口**待实现，当前不可直接运行**：

```text
analyze_stage3_baseline.py analyze-run --ledger <approved-ledger> --contract <measurement-contract>
                         --run-id <run-id> --output-dir <new-run-revision> --table-dir <new-run-tables>
analyze_stage3_baseline.py aggregate --ledger <approved-ledger> --contract <measurement-contract>
                         --run-manifest <manifest-1> [--run-manifest <manifest-2> ...]
                         --output-dir <new-aggregate-revision> --table-dir <new-aggregate-tables>
                         --figure-dir <new-aggregate-figures>
```

1. 实现前读取现有ArchiveResolver、内部lane分组和R事件合同；不复制旧脚本的/tmp硬编码与固定车辆断言。
2. 根据§5/6实现流式FCD解析、episodes、TLS对齐、汇总、敏感性。先做合成fixture，不读大档案进行调试。
3. 拒绝覆盖、拒绝tmp回退、拒绝未经合同声明的时窗/版本。ledger/contract父目录可以已存在；每次生成的run/aggregate revision目录必须不存在，由工具原子创建。新版本不覆盖旧版。未知必要字段写错误或资格标记，不能填0。
4. 新分析模块不得导入会启动SUMO的runner流程；扫描subprocess/TraCI连接路径，保证零仿真。
5. 12项失败模式逐一测试：重复ID；缺帧（含无车帧不等于缺帧）；[1,2,4]episode分裂；区域车辆接替与同车episode不同；内部lane无遗漏/双计；速度0.1边界/缺速度；R首次唯一；跨箱事件unknown；端点缺覆盖不出O=0；E1零贡献/加权/A-B锚点及短尾箱已知贡献例；TLS错误link；缺seed禁止“两seed一致”。每类所列全部子情况均须有assert，另记录实际fixture/assert数；12/12只表示类别覆盖，不能用一条assert代替未测子项。
6. data_analyst准备独立核验函数：直接读原始XML重建数量和事件，不调用生产聚合函数再次“验证自己”。reviewer先审测量合同及测试覆盖。

**出口：**新12模式全部通过；0个未关闭技术Blocker/Major；命令帮助与字段一致后才把接口标implemented。跳过测试不算通过。

### 7.4 T33：首项门与八run离线分析（data_analyst）

1. 先分析C17，核对已知P=M1333/R300/U150/X75、R需求期36、全程R300；只用作已核基准，不要求其它run同数。
2. 验证新lane/group汇总与原始FCD一致；first-event与前帧、TLS、episode人工抽查须有记录ID；独立核验所有核心计数。
3. 首项通过后使用analyze-run依次C23、ML17、ML23、MH17、MH23、RL17、RL23，每条独立新revision，不重复C17。八份run-manifest齐备后aggregate一次读取全部八份产物并核对源/合同hash，不追加或覆盖C17结果。
4. 每run回答五问题；完整原始时间网格包括无车帧，不能以车辆行不存在判断时间帧缺失。按sumocfg/输出设置预期1Hz共2700时间标签，若输出不同先解释再调整合同，不自动补帧。
5. 生成§6五表，复用旧q/v/车辆表；产生新的来源manifest和核验结果。最多3张静态图：空间时间与信号；主线/下游及R累计观察；R/U入网到达与已核端点。空白/unknown不得画0线。

**出口：**40/40问题有可追溯状态；G02–G05在范围内通过；不能答的列具体缺口，不宣称全部科学问题已解决。

### 7.5 T34：敏感性、反例与解释（data_analyst → reviewer）

1. 完成G06的6组输入对照、8个seed单元、96条聚合/窗口量；按§5.11处理尾箱。
2. 报告停止episode分布/最长支持及真实时序，不自动发明拥堵阈值；将短停与长时间区域占位分开。
3. 按Q1–Q4填主张—证据—替代解释—缺证据。至少核查输入未实现、靠近合流插入、信号停驶、lane覆盖、下游阻塞、合流/换道机制这6类候选解释的`checked/unresolved/not_applicable`状态，不要求每项都排除。
4. seed/窗口符号不同全部保留；没有发现主线受损不等于证明没有，也不意味着多跑到出现为止。
5. reviewer逐项审目标、实际覆盖、遗漏/重复、独立对账、回归保护。集中修订一轮；仍有实质问题记录blocked或unresolved，不开启新仿真。

**出口：**G06完成，Q1–Q4状态4/4；未关闭实质分析问题0，或明确blocked包。

### 7.6 T35：Stage 3 报告和分支（primary）

交付O1–O5及O6初稿、§4所有门的实际值/分母/状态、工程与科学review记录。所有新指标/状态都引用证据。按以下唯一分支：

- 关键主张已有支持且无需新运行：提出跳过Stage4，直接Stage5。
- 关键缺口可通过一个有明确区分能力的干预解决：形成Stage4注册提案，等待精确批准。
- 找不到可区分的试验、需要改变研究问题或预算不可承受：形成障碍/未识别报告；向用户提出带证据的决定，必要时提前问Robert。

**阶段完成线：**规定产物齐全+状态无遗漏+新仿真0；不把Stage3报告完成与场景适用通过混为一谈。

## 8. Stage 4 — 有条件、预注册的定点验证

**不默认执行。准备门：T35存在明确核心缺口，用户批准限定的干预提案与离线实现范围，才可做T40–T42准备。启动门：实现后完整运行卡含真实代码hash/命令、预算和分析合同，经工程/data/reviewer核定并被明确运行授权覆盖，才可做T43。当前具体运行卡尚不存在，Sol low不得自行选数。**已授权内容若明确覆盖实际实现且没有偏离，不要求重复批准；缺少精确运行授权则提交完成的运行卡供最终批准。本阶段仍无匝道控制器，保留既有城市固定配时，除非该变化成为另行批准的唯一干预。

### 8.1 T40：把缺口变成可区分的问题

按T35证据选择一条，不把下面所有选项都运行：

| 观察到的缺口 | 先做的无仿真检查 | 可能的唯一干预类别（需审批） | 区分证据与限制 |
| --- | --- | --- | --- |
| 主线实际入网靠近合流，feeder观测不足 | 实际departPos分布、路径使用、编译结构 | 插入方式或入口位置的单一变体 | 同时核实际M实现量；入口改变导致流量不同要报告，不能宣称纯位置效应 |
| 原始采样无法分辨合流/换道原因 | 静态连接与FCD可观察边界 | 只添加所需观测的匹配运行 | 检查观测改动是否保持交通记录；只能补机制证据，不能改变行为来“测原因” |
| 路权/几何存在有证据的问题 | 接续lane、request/foe/response、轨迹核查 | 一个明确几何或连接/行为设置变体 | 不同时改插入、需求、路权；变体是合成假设检验，不称现实校准 |
| 需求范围无法区分主线与匝道响应 | 已实现输入、下游状态、R进入量 | 一个需求轴的有限匹配比较 | 不直接命名临界容量；qUrban/qX固定，另一轴不变 |
| 相关现象可能被时域截断 | 到1500/2700的排队、累计入网/到达、尾部趋势 | 单一需求持续时间或清空时长变体 | 延长需求改变总车辆数，使用统一共同窗口加尾部报告；不是只改变观测的纯重复 |
| 需要证明R回溢造成U的纯额外损失 | 同空间、信号与通行证据是否充分 | 先定义因果对照再决定是否运行 | qRamp减半不是自动的“无回溢反事实”；无法定义则留待正式设计讨论 |

每个问题必须写：已有证据、至少两个能被该试验区分的解释、干预、固定项、支持/反驳/无法区分三种结果各对应什么动作。若三种结果都无法改变判断，试验信息价值不足，不执行。

### 8.2 T41：预算和精确运行卡

**提出的管理上限：最多2个诊断块，每块至多4次常规新SUMO启动；全Stage4至多1次同参技术重试，硬上限9次。**这不是统计充分样本量；选择理由是限制为最多两个独立问题、每个最多“2设置×2seed”的有限对照。用户可以批准更小范围；上限不是必须用满的配额。

每块默认沿用17/23以配对旧证据（如有科学理由改seed，必须在注册卡中明确审批），记录baseline/treatment各两条逻辑运行；完全匹配的既有baseline可复用、不耗启动。不能为达到四次而重复有效baseline。任何SUMO smoke/GUI/TraCI探针/集成测试都消耗同一个总额度；netconvert-only单独记操作但不冒充SUMO运行。

第二块的允许问题与触发条件必须在Stage4总批准时登记；如果只能根据第一块结果再提出新问题，则重新提交具体第二块卡，不自动获得授权。最多一个集中离线修订轮；失败不能通过换seed/加时长称为重试。

运行卡必填字段（缺1项都不能启动）：

```text
block_id, question_id, hypothesis_A, hypothesis_B, discriminating_observations
run_id, attempt_id, role, reused_run_or_null, seed, paired_run_id
q_main, q_ramp, q_urban, q_x, demand_xml_number_rule
warmup_s, demand_end_s, measurement_windows, clearance_s, simulation_end_s
one_intervention, fixed_fields, scenario_variant_path, source_code_hashes
sumo_version, netconvert_version, traci_version, step_length, output_periods
exact_command_argv, expected_outputs, runtime_identity_method, archive_path
analysis_contract, comparison_cohorts, rounding_tolerances, technical_checks
support_action, contradiction_action, unresolved_action, stop_conditions
max_new_starts, technical_retry_condition, approved_authorization_quote
```

T41先准备注册卡，只有尚待实现的代码hash/新命令可临时标pending_implementation，此时不能启动。T42完成后、进入T43前主代理审核条件必填字段无TBD/模板/pending；schema逐字段规定合法null/NA及理由，例如新run的reused_run_or_null必须null，复用项的exact_command_argv保存历史命令并标不执行。核心研究参数未知不能以NA绕过。工程验证命令真实存在；data_analyst确认比较分母和可观察量；reviewer确认单因素逻辑/停止规则。任何人不得将前述示例类别擅自补成已批准参数。

### 8.3 T42：实现和技术验证（engineer）

1. 新场景变体使用新路径，保留Stage2配置/数据；所有变更先给精确diff与来源说明。
2. 当前runner不支持变体/输出目录参数时先实现明确接口并离线验证，不向旧CLI传虚构参数。
3. 冻结本次探索运行的代码/输入快照，含U/X、信号、vType、路由、编译lane、输出设置；这是**批准试验的配置快照**，不是正式EXPERIMENT_PROTOCOL冻结。
4. T42只完成离线测试及技术SUMO的准备。需要技术SUMO验证时也须满足T43启动门，由T43顺序执行并计入同一预算；观测改动的交通语义匹配检查在该已授权运行完成后进行，不能只比较exit code。
5. 记录实际命令、版本、开始时间及将如何唯一绑定runtime；启动前预登记attempt。若外层命令在SUMO前失败，保留原因，确认未启动后不计SUMO预算。

### 8.4 T43：顺序执行与归档（engineer）

1. 每次启动前读ledger，确认剩余额度、授权、代码hash和固定参数；一次只启动一条。
2. 完成后绑定runtime、保存stdout/stderr与summary、原始输入/输出及版本。按source map归档，hash100%一致，不改临时原目录。
3. 检查必需输出、身份、期间覆盖、警告/碰撞/teleport/紧急制动、计划/入网/到达/未完成。未分类异常数必须为0；有实质异常则标不适用或blocked，不能静默删除。
4. 不清空、入网低、没有Breakdown、结果方向相反不属于技术重试理由。技术重试仅已定位加载/输出故障，参数完全相同；首尝试保留。
5. 启动前预留额度，SUMO实际启动立即更新actual_starts，不等结束才扣额。中断且启动与否未明的attempt继续占用预留额度，直到证明确未启动才能释放；不因stdout丢失自动重跑。硬上限到达即停。

### 8.5 T44：配对分析与收口（analyst → reviewer → primary）

1. 先适配分析合同到新时窗/配置，禁止把Stage2固定0/1500/2700直接套入不同设计。
2. 用相同测量合同处理baseline和variant，新表保留run/variant/seed/窗口/计数分母/差值；单因素配置差异100%核对。
3. independent原始核对、相关fixture、五项科学检查；失败/未完成/Unknown全部进覆盖表。
4. 按预登记support/contradiction/unresolved规则结论，不根据效果扩大搜索或切换假说。
5. 输出`docs/STAGE4_TARGETED_VALIDATION_REPORT.md`及新ledger；二块用量、失败和重试全部列出。预登记但按批准停止规则不再启动的项记`cancelled_by_stop_rule`、实际启动0、触发证据和原因，不删除、不计为有效数据。终态覆盖率分母仍含这些项，科学证据分母另列实际有效run。正常出口要求预定逻辑run终态100%、实际使用证据技术门通过、主张均有状态；缺失核心证据不能用取消记录冒充ready。

**停止：**问题已可判断、没有可区分的新试验、预批准块完成、预算耗尽或发现需改变研究问题，任一成立即停止新增运行。若仍无主线侧证据，则进入Stage5的specific_obstacle/unresolved，不新建Stage4b/4c无限续跑。

## 9. Stage 5 — 探索验证评估结项（零新仿真）

此阶段只对已完成证据做收口，不用“写报告”掩盖未完成分析。Stage4可经审核标not_required；若Stage4已触发但关键资料损坏，不能跳过其技术问题声称ready。

| 步骤 | 具体操作 | 数量化出口 |
| --- | --- | --- |
| T50 产物清点 | **completed**：列O1–O6和G01–G08实际文件、版本、hash、分母、状态；引用Stage2已验收证据，不复制重算 | 6/6产出；8/8门有结果；预定run终态100% |
| T51 用途审核 | **completed**：reviewer逐条审核Q1–Q4及反例，标supported/contradicted/not_identified；指出适用需求/场景版本 | 4/4判断；核心unknown=2；未关闭分析Blocker/Major=0 |
| T52 方法交接 | **completed**：按§10给每项值/状态/适用范围/依据/待办；不把参数快照当最优选择 | 22/22分类；没有无来源“已验证”；正式值选择0 |
| T53 总报告 | **completed**：形成`docs/EXPLORATORY_VALIDATION_REPORT.md`，含发现、未发现、可沿用范围、3状态结论、后续设计限制 | 科学陈述使用证据ID；未来正式资格仍not_started |
| T54 用户结项 | 提交“评估已完成”和“是否preliminary_ready”两个独立结论供用户确认 | 用户明确接受后才更新探索状态；不自动接受协议 |

若为`preliminary_ready`，探索可以结束并起草正式实验设计；若为`obstacle/unresolved`，可以完成探索评估并提交受约束的设计备选，但必须先解决/讨论关键缺口才能冻结正式设计。两种情况下都不会预先证明控制收益。

## 10. 原Stage 6安排（历史设计内容，执行顺序已被新方案替代）

**2026-09-13用户明确要求先解决并确认specific_obstacle，再写正式实验设计草案。后续执行只使用 `docs/STAGE6_OBSTACLE_RESOLUTION_EXECUTION_PLAN.md` 的S6-A00等编号；下列T60–T63保留为历史设计主题，不授权提前实施。新方案SG6-R未通过时禁止进入正式草案。**

遵循用户顺序：先依据探索交接讨论能沿用什么，再起草设计，然后问Robert。实际正式协议`docs/EXPERIMENT_PROTOCOL.md`仍为空；未经明确批准不写入或冻结。

### 10.1 T60：参数与指标继承登记

每项列：`item,current_value_or_unknown,evidence_id,domain,qualification,proposed_formal_value,reason,decision_owner,next_action`。状态仅四类：

- `reuse_with_scope`：有适用证据，可以在声明范围复用；不表示跨场景普适。
- `candidate_requires_validation`：可提出候选，但仍需检验或正式pilot。
- `requires_scientific_decision`：阈值/目标/权重等不能靠运行事实自行决定。
- `not_available_or_ineligible`：现有数据或方法不能提供，不可填造。

最低20类：①路网/合流结构；②实际入口位置/插入规则；③M/R/U/X与需求实现；④车辆行为参数；⑤城市信号；⑥匝道允许储存边界；⑦E1/E2/FCD空间；⑧采样/聚合与事件精度；⑨加载/预热；⑩测量窗；⑪需求时长；⑫清空/截尾；⑬主线评价量；⑭R评价量；⑮U评价量；⑯网外等待及总体延误资格；⑰Breakdown/Capacity Drop定义是否需要；⑱研究需求范围；⑲seed/重复精度；⑳正式对照方案与控制设置。另列sweet-spot保护阈值/权重/可接受性及随机稳健规则，均不能由技术通过自动确定。

初始方向：内部E1及身份/计数方法可有限复用；0/1500/1200与seed17/23不是正式充分方案；0.1m/s停驶不升级为拥堵；精确排程、有效储存、容量和保护阈值仍未知/待决定。Stage4若改变结构，必须重审受影响的继承项。

### 10.2 T61：正式设计草案（另行批准后编写）

新建`docs/FORMAL_EXPERIMENT_DESIGN_PROPOSAL.md`，状态Proposed，至少包括：问题/假设；场景版本与适用域；无控制和拟比较控制方案；固定/干预因素；需求范围及依据；评价指标/单位/总体；时窗与截尾；随机重复及精度规划；控制校准与评估数据分离；异常规则；分析/统计方法；预算与执行停止条件。

正式重复数应从拟用主指标的方差和需要分辨的差异/区间精度规划，不能照抄两个seed或文献示例；若需要额外pilot，另列有预算的提案。本阶段只设计，不实现控制器、不跑正式批次。

**出口：**上述12主题每项有具体提案或编号未决项，空白字段0；每个数值有“已证/候选/研究选择”标签。核心未决数可以大于0，但不能称ready_to_freeze。

### 10.3 T62：Robert材料与反馈处理

一页现象/证据概述 + 一页设计与选择摘要 + 完整草案链接。最多三个主问题：

1. 当前场景适用证据/明确障碍，是否足以支持拟议的高速公路—城市权衡；Breakdown/Capacity Drop在论文中是必需目标还是待解释现象？
2. 我们提出的对照、指标和城市保护/储存定义，能否回答问题，贡献与工作量是否合适？
3. 对仍缺依据的时域/随机性/场景假设，我们提出的处理方案是否可接受，哪些应追加验证？

发送需用户明确授权；本方案不发送任何消息。收到真实反馈才更新SUPERVISOR_FEEDBACK并保存原始来源。建立`comment→design_section→proposed_change→verification→approval`对应表，反馈条目100%处理或明确待确认。不猜导师会同意，不把沉默当批准。

T63：反馈处理和必要验证后，由用户批准正式协议内容与冻结，再单独授权正式批次。Stage6完成不自动启动正式实验。

## 11. Sol low执行防错清单

这份方案通过小步骤、字段约束、专业审核和停点降低执行歧义，**不能保证模型完美执行**。不要改变用户模型设置；主代理用Sol low执行时，项目专业代理按其角色指令工作，科学裁决不得简化为主代理自己的打勾。

### 11.1 已有真实入口与禁用情形

| 入口 | 实际能力／风险 | 本方案规则 |
| --- | --- | --- |
| `analyze_stage2_exploration.py` | 固定Stage2时窗、6E1、版本等合同 | 只用于符合旧合同的复用；新设计先适配 |
| `stage2_queue_diagnostic.py` | 仅`--output`、硬编码两/tmp、普通edge、旧排程/TLS假设 | 不作为Stage3通用工具 |
| `build_stage2_replay.py` | 固定390–430s和具体车辆事件断言 | 不直接传新时窗；当前优先静态诊断图，非必要不重写回放 |
| `internal_lane_accounting.py` | 有`--fcd --network --output`，只覆盖其已实现核算 | 可复用底层映射；不是完整Stage3工具 |
| runner `--validate-only` | 会创建tmp、调用netconvert和写文件 | Stage3禁止；不能叫只读检查 |
| runner `--reanalyze-summary` | 旧runtime解析并写tmp | 不替代archive-only入口 |
| 全库测试／`test_minimal_uncontrolled.py`全模块 | 含真实SUMO集成运行 | Stage3禁止；只运行已核不启动SUMO的指定测试 |
| 原runtime的sumocfg | 重跑可能覆盖原输出 | 永远不从原目录运行新验证 |

真实runner参数：`--profile --q-main --q-ramp --seed --warmup-s --measurement-duration-s --demand-end-s --post-demand-clearance-s --sumo-binary --netconvert-binary --validate-only --reanalyze-summary`。q-main/q-ramp必须成对。**没有现成`--q-urban`、`--q-x`、`--output-dir`或几何/路权/控制器变体参数。**不可伪造命令。

Stage3新测试接口实现后精确运行`tests.test_stage3_baseline`；既有回归只选择受修改影响的已核离线模块。例如`tests.test_internal_lane_accounting`、`tests.test_stage2_exploration_analysis`；不因计划提及就全部反复跑。只读inspect源码确认不启动模拟后执行。既有保留/tmp依赖缺失导致skip时明确报告，不能算通过。

### 11.2 每步固定执行顺序

1. 读授权原话、ledger与本步输入；确认输出目录不存在或本步明确可续写。
2. 路由对应专业代理并给输入、独占写路径、禁止项、验证和交付。
3. 未实现接口先实现并测试；不得将方案示例当现成CLI。
4. 先最小fixture，再首项门，后完整已批清单；任何失败保留记录。
5. 检查完成线及证据，不以进程exit0代替科学通过。
6. 更新ledger与WORKLOG；实际阶段/阻塞变化才更新PROJECT_STATE。
7. 在已批准范围内继续，不每条重复问；到研究变更、新运行卡或阶段验收门才停。

### 11.3 给Sol low的Stage3接续文本

> 先读AGENTS、PROJECT_STATE、docs/EXPLORATORY_VALIDATION_COMPLETION_PLAN.md和现有Stage2完成/G2报告。检查用户是否明确批准Stage3及分析合同。只编制过计划不等于执行授权。获批后从T30开始，严格按T30–T35，使用simulation_engineer、data_analyst、scientific_reviewer，各自Context Preflight。Stage3新增SUMO/netconvert为0；保留data/raw、Stage2归档、revision_04、原始输出、receipt和dirty worktree。以ledger→source map定位原始归档，不回退/tmp。只做本计划的空间时序诊断和敏感性；不加控制器，不发明交通状态阈值，不通过全库测试启动SUMO。尚不存在的Stage3接口先离线实现和测试。每步完成记录证据，断点续接。T35提交40个问题单元、G01–G08状态及Q1–Q4主张，按证据建议Stage4或Stage5。Stage4注册卡未获批准时停止新仿真。不得因没有Breakdown追加需求或改参数。

## 12. 审批边界、审查与验收清单

未来可分别批准：A=Stage3零新仿真及本计划分析合同；B=具体Stage4运行卡/变更/预算；C=Stage5探索结项；D=Stage6草案及导师消息发送（发送单独授权）；E=正式协议冻结与批次。这里的分段是不同研究权限，不是对每次可逆操作重复确认。

当前状态：方案编制已授权；A–E均不由本文件自动批准。Stage4精确干预值必须依据Stage3证据决定，当前故意不虚构；Sol low遇到未填卡必须停，不能凭模型猜测。研究决策门是本方案可执行性的一部分。

方案交付自检：

- [x] 六产出与额外敏感性维度均有来源与量化检查。
- [x] Stage1/2事实和缺口分开，MH零观察范围准确。
- [x] 技术门、诊断完成和用途ready区分，保留障碍/未识别出口。
- [x] Stage3零新仿真；Stage4条件触发、上限和注册字段明确；Stage5/6顺序符合用户要求。
- [x] 已有CLI与待实现接口明确，保留版本、原始数据、日志和中断恢复。
- [x] 工程/分析/科学代理已审核最终正文；必要修订已关闭。

规划中的新测量与试验尚未实施，五项实际测量检查仍not_verified；文献方法审核不是执行通过。

### 12.1 本轮最终审核记录

| 专业路由 | 实际审核范围 | 发现及处理 | 最终状态 |
| --- | --- | --- | --- |
| simulation_engineer used | 真实CLI、零新模拟边界、首项/汇总/恢复、运行注册和预算 | 分run及aggregate独占输出、即时扣额、取消终态、合法空值、实现准备与启动分门均已修正 | 无剩余技术Blocker/Major/必要修改 |
| data_analyst used | 已有证据、量化分母、时间/空间/身份合同、表schema和独立核查 | 96条仅内部M、48条时序；A/B锚点/尾箱；frame registry/路径/episode parent；核心全量核验和12类子断言均已补齐 | 分析合同可供批准，未来实现未验证 |
| scientific_reviewer used | 文献范围、量化门、Q1–Q4、停止状态、Stage5/6顺序及最终补丁 | 禁止任意速度降幅作成功门；修正空值及重聚合含义；确认完成评估不等于用途ready | 最终无Blocker/Major/未关闭必要Minor |

方案方法与内部一致性置信度High；未来实现能否全部通过、是否出现所需交通现象仍Unknown。Sol low可在该分工和研究停门内按步骤执行，不能承诺完美或授权之外自主补参数。未用专业代理输出替代用户决定。

# Stage 6：先解决场景用途缺口，再编写正式实验设计

日期：2026-09-13。版本：1。状态：**Proposed，工程/数据/科学规划审查完成；本轮仅编制计划，尚未授权实施或启动。**

## 0. 当前授权与本方案的含义

用户已明确确认顺序：“按照这个顺序进行”，并要求“设计详细的stage6，应该包含specific_obstacle的方案，确认解决后再开始设计草案”。这授权本轮制定方案和同步工作路线；**不等于本轮开始新仿真、选定场景参数、实施控制器或冻结协议。**规划可现在完成，不为编写规划重复请求T54确认。T54的正式用户接受状态仍按PROJECT_STATE记录，不由本文件追认。

本文件取代旧 `EXPLORATORY_VALIDATION_COMPLETION_PLAN.md` §10 中“进入Stage6即可写正式设计草案”的顺序。旧T60–T63是历史编号；后续用本文件唯一的 `S6-A00` 等ID，禁止按旧编号跳到正式草案。

**Stage6A–E仍属于场景探索/验证；Stage6F才属于正式实验设计。**Stage5关闭只能结束上一轮有边界的评估，不代表整个研究的场景验证已成功。

运行卡配套模板：`docs/stage6/STAGE6_VALIDATION_CARD_TEMPLATE.json`；这是草案字段模板，不是现成runner接口或已批准卡。未来工程必须先实现对应validator。

本次交付到“计划专业审查完成”即停止。以下全部是未来执行步骤；文中将来产物不存在不是本次造假或漏交。没有运行卡实值、实现验收和启动授权，不得把模板当可运行命令。

## 1. 我们究竟要解决什么

已核事实（E01–E04）：Stage3八条旧运行的核心量已复算；qMain=3500时两seed在A窗的R首次下游事件为14/11，qMain=3650为0/0，四候选均未满足注册EJMI。原始观测可以保留。不能写成“已证明近端插入造成结构错误”“主线没有损失”或“R排除早于真实主线受损”。

EJMI要求中间候选同时超出C/MH两端速度/占有率包络，另满足窗口、两seed和持续性条件；它可能不识别单调、小幅或短时受损。Stage6不得事后改Stage4阈值或重标Stage4机器决策来制造成功。

目标：为一个**明确版本、明确需求范围的无控制场景**建立以下四项证据，达到可开始正式设计的最低适用性。研究方向保持D001–D003；无需先证明控制收益。

| 用途问题 | 成功所需证据 | 不足以通过的情况 |
| --- | --- | --- |
| Q1 可观测性 | M/R/U各有流动量与状态/积存量、完整时间和空间范围；关键边界能对账 | 仅文件存在、仅局部E1、仅最终清空 |
| Q2 主线侧 | 在有效上游—合流—下游观测域内，有与合流时空关系一致、满足预登记规则的M性能受损证据 | 高流量、高输入；单点速度差；EJMI阴性被当成无损失 |
| Q3 城市侧 | R路径积压延伸至共享区、U暴露及通行表现可解释，列TLS与替代解释 | 只有网外等待；只有红灯停车；把共现称纯因果额外损失 |
| Q4 同场景联系 | Q2/Q3来自同一版本、可比较条件；有足够R实际合流证据支撑后续研究放行权衡 | 拼接不同版本两侧；所有研究条件都只有R完全被排除；把一个R通过当充分条件 |

Q2/Q3不必同一秒出现；必须在注册的有限条件集合中有明确时空/需求联系。允许结论 `resolved_for_baseline_design`、`not_resolved` 或 `blocked_by_evidence_error`。第一项也不表示模型已被现实数据校准、不保证控制有效、不保证sweet spot存在。

## 2. 已有输入与权威关系

后续每次恢复先读：AGENTS、PROJECT_STATE、DECISIONS、EXPERIMENT_PROTOCOL、WORKLOG、本文、当前ledger。正式协议目前为空是已知状态，正式参数视unknown，不能因此阻止已授权的探索规划。

| 证据ID | 输入 | 用法/限制 |
| --- | --- | --- |
| E01 | `docs/STAGE3_STAGE5_ASTRA_REVIEW_20260913.md` | 对旧强表述、防错、缺配对项的最新更正 |
| E02 | `data/processed/stage3_baseline_diagnostic_20260912_v2/` | 8条Stage2档案的Stage3测量合同及派生诊断 |
| E03 | `data/processed/stage4_qmain_sequential_20260912_v1/final_evidence_ledger_snapshot.json` | Stage4最终唯一规范ledger，SHA `f589c905067887536037fe6fe045438e8a1588cbf3246dcc50b573facecb4516` |
| E04 | `data/processed/astra_stage3_stage5_reaudit_20260913_v1/` | 原XML复核、更正22项handover、12 IDs映射、5未配对及96产品不变性 |
| E05 | `data/processed/astra_stage3_stage5_engineering_reaudit_20260913_v1/` | 旧代码副本、新代码审核和audit-only ledger；不能覆盖旧源码合同 |
| E06 | `docs/supervision/2026-08-25_robert_hilbrich_reply.md` | 简单场景、初始Krauß、检查插入及不强迫预想行为的原始指导；不是任何新参数的批准 |
| E07 | `docs/DECISIONS.md` D001–D003 | 研究方向、sweet-spot概念和最小城市机制；暂定，不是Frozen |
| E08 | `literature/EXPLORATORY_VALIDATION_REVIEW_20260909.md` | 方法资料及既有适用边界；不提供自动通过阈值 |

A阶段锁定 **12条独立实际运行**：C17/C23、ML17/ML23、MH17/MH23、RL17/RL23、QM3500S17/S23、QM3650S17/S23。C/MH在Stage4中是复用引用，不另算4条；q3350的取消逻辑记录保留，绝不计作实际运行。历史低负荷smoke不补成匹配参考。

每个ID必须通过ledger→source map/receipt→项目归档解析，登记真实绝对路径与SHA。不用“最新目录”、glob猜对应关系或失效/tmp作后备。缺源标blocked，不能跳过后提高完成率。

## 3. 责任、目录和阶段门

- 主代理独占docs、任务拆分、授权与状态记录；不代替专家作科学裁决。
- simulation_engineer：源码/配置/运行卡实现、技术门与运行；不自选研究参数。
- data_analyst：新合同、解析、表图、独立数量核验；不改原始数据。
- scientific_reviewer：只读，审核解释、规则、实验可区分性及成功门。每位均先做Context Preflight。

首次获执行授权后创建 `data/processed/stage6_obstacle_<YYYYMMDD>_v1/`（BASE）；同名已存在则读取其ledger恢复，若新任务则v2；不得覆盖。表在 `results/tables/<batch>/`（TABLES），图在 `results/figures/<batch>/`（FIGURES）。新仿真每attempt单独工作目录、归档到 `artifacts/<batch>/<attempt_id>/`；归档后原始输出不可变。所有后续修订用revision_XX。

| 段 | 工作 | 最低出口 | 是否可能运行SUMO |
| --- | --- | --- | --- |
| A | 已有证据诊断、候选解释排序 | 12运行索引、6解释均有证据状态；确定最小待验证问题 | 否 |
| B | 补救方案及科学验证注册 | 研究问题、规则、矩阵与参数填实；reviewer通过；形成待实现的卡草案 | 否 |
| C | 隔离实现、离线测试、获批构建与启动卡 | 离线门→单独记账的netconvert构建→实际空间核验→精确启动卡获批 | SUMO否；C03允许已批准netconvert |
| D | 已批准最小验证块 | 全部登记运行终态、归档与独立分析 | 是，只按卡 |
| E | 缺口解决验收 | Q1–Q4及成功规则通过，用户接受SG6-R | 否 |
| F | 正式设计草案、Robert材料 | 原T60–T62所需主题齐备，全部仍Proposed | 否 |

**强制门：SG6-BUILD=有预算的网络构建；SG6-L=实现离线门；SG6-P=编译与空间核验后的具体SUMO运行卡；SG6-R=缺口解决验收。SG6-R未通过时禁止新建 `FORMAL_EXPERIMENT_DESIGN_PROPOSAL.md`。**失败仅形成障碍咨询材料，不能把咨询材料伪装成正式设计草案。

## 4. A段：先把问题分清，不再盲扫需求

### S6-A00 — 入口及来源快照（主代理+工程）

1. 登记用户授权原话/范围，区分T54结项、Stage6方案批准、离线执行、运行卡启动。T54 pending不妨碍本轮规划；实施时明确状态，不追认验收。
2. 保存相关源码/配置/合同/注册payload哈希、git dirty清单和原文件只读边界；不提交/重置。
3. 创建BASE/ledger.json与evidence_index.csv，所有source路径必须存在且实际SHA匹配。登记每步owner/status/input/output/error。
4. 确认Stage3修复源码与旧Stage3/4合同绑定不同。选择新派生分析合同，不修改旧hash、旧判据或旧ledger；精确记录旧版和新版角色。

产物：source_registry.csv、ledger.json、tool_capability_audit.md。完成：12/12实际运行唯一映射，重复实际run=0，未解释hash冲突=0；取消记录可追踪；本段SUMO/netconvert/TraCI/GUI=0/0/0/0。

### S6-A01 — 构造可跨批次读取的索引（数据，工程支持）

1. 列12条run的四类车辆、时间合同、拓扑hash、FCD/E1/TLS/tripinfo是否有源；只读取已有档案，不重新生成网络。
2. 将Stage3 `nVehContrib`流量、Stage4 `nVehEntered`流量保留不同metric_id；只有同scope/字段/窗口的量才作差。需要统一时必须从原XML另派生同定义量，保留原值。
3. 修补将被复用的旧对照生成器：按键外连接两seed，单边缺失显式not_paired；禁止静默continue和自动填零。无需动原398/43或原801表。
4. 新入口先使用小fixture验证：内部lane、缺/多帧、缺/非有限速度、TLS标签、正贡献无速度、空贡献、尾箱、跨窗入网、单seed缺配对、未知ID与hash冲突；沿用已修复逻辑但不得直接放松旧合同。

产物：schema_compatibility.csv、offline_adapter_contract.json、新模块与定点测试记录。完成：12/12合同差异已列；每必需字段的“可复用/需重算/不可得”分类100%；单seed缺配对fixture必须保留记录。新CLI未实现前标not_implemented，不在交接中写成可用命令。

### S6-A02 — 六类候选解释（数据+工程；reviewer审）

| ID | 待检解释，均非既定原因 | 档案检查动作 | 能区分什么/仍不能证明什么 |
| --- | --- | --- | --- |
| H1 | EJMI或观测范围未捕获受损 | 逐seed并列M速度、通过量、占有率/积存、停止轨迹与断面位置；列不满足EJMI的具体分项 | 可发现判据盲区；事后新判据只能是候选发现 |
| H2 | 近合流入网使上游状态不可观测或形成受限 | 对所有M记录实际depart位置、到合流的可用距离/路径、沿程覆盖；将计划位置与实际位置分列 | 说明真实观测域；不能凭短距离证明因果 |
| H3 | 合流路权/换道/车道连接限制R进入 | 读编译connection/priority/link、R停止位置与周边M轨迹；列请求但没有的换道/接受间隙输出 | FCD只能描述轨迹，不能反推驾驶员意图或未经输出的精确gap接受机制 |
| H4 | 下游供给或终点边界主导结果 | 画停止/积存首次位置、下游断面和到达；检查是否接近出口边界、是否有独立瓶颈 | 区分合流附近与边界传播线索；缺观测则unknown |
| H5 | 加载、有限需求期及迟到入网掩盖响应 | 复用A/B/Post/Full全时域、端点P/E/A/N/O；按实际入网/到达与R passage画对齐时序 | B切窗不等预热；post仍有入网不等恢复；不能用清空证明1500s足够 |
| H6 | 城市信号/共享区使U暴露解释混杂 | R路径区域、U状态与各movement TLS上下文对齐，列绿/红时观察 | 可确认暴露和替代解释；不证明纯因果U额外损失 |

另建 `obstacle_diagnosis.csv`，将 `coverage_status=complete/incomplete/not_observable/unknown` 与 `phenomenon_status=observed/not_observed_within_scope/not_identified` 分开；缺观测不能编码为真零或现象不存在。

每解释填写 `hypothesis_id,claim,run_ids,evidence_ids,predicted_observation,observed_result,alternative,status,next_discriminating_action`；状态 `supported_as_candidate / weakened / not_identified`。H矩阵6/6有结论，不能给缺证据项填“已排除”。产物最多4组有用途的图：空间入口图、M时空/断面、R-U-TLS时序、时窗/端点；图只辅助，关键数字必须有表。

### S6-A03 — 候选补救及最小可区分对比（工程提出，reviewer裁核）

- 若仅需补测/新解释规则：优先同一场景，登记测量修订；涉及新诊断定义要在新验证数据前冻结，不重标Stage4。
- 源节点main_in=(-800,0)、merge=(600,0)名义间距已约1.4km（E06指导之外的当前工程文件事实：`config/scenarios/minimal_uncontrolled/scenario.nod.xml`）；物理边长与真实入网至合流行程不是同一量。
- 若H2有证据优先级：提出独立入网/上游观测方案；长度、departPos和检测位置必须有物理/观测依据，不默认加长即可解决。长度和插入一起改应标组合干预，不能归因单一长度。
- 若H3/H4优先：只提出能区分该解释的connection/下游供给等定点对比；不同时改行为模型、几何、需求来追逐阳性。
- H5/H6优先时先判是否可用已有记录排除，必要时单独注册时长/观测变化；不自动改城市配时/储存边界。

产物 `docs/STAGE6_OBSTACLE_DIAGNOSIS_REPORT.md`、`BASE/candidate_change_register.csv`。每候选至少写问题、改变/固定因素、预测差异、不能识别的混杂、能否用现有源验证、失败解释、实现成本。reviewer选择“进入B的一项最小候选”或“资料不足→咨询Robert”；不得自动连续尝试六类修改。

完成：H1–H6覆盖6/6，12条运行适用域说明12/12；候选优先级有证据，选择/不选理由齐全。A只形成诊断结论，**即使旧档案经新口径出现阳性也不自动宣告缺口解决**。

## 5. B段：把补救方案填成可执行卡

### S6-B00 — 确定验证问题及对照

至少登记一个reference条件和一个challenge条件。reference必须在同一候选场景版本中有合格入口/观测，能服务选定M指标的基准；不能把旧污染upstream E1或不同几何均速直接当reference。

将每项参数依次填入：①旧值及来源；②候选新值及依据；③为什么该变化能区分H；④固定因素及同步必要变化；⑤预测支持/反证/无法区分的结果；⑥reviewer意见；⑦用户批准的最终值。未确定的数值保持 `unknown_requires_registration`，说明由谁、用哪项证据在本步决定。**任何科学设计必填未知未解决则B未完成；工程实现字段可登记pending_C，所有launch-critical字段必须在SG6-P前齐全。**

### S6-B01 — 注册量化诊断与成功规则

在新运行前制作 `diagnostic_rules.json`，定义以下实值字段（不是此刻选定正式指标）：

- M空间范围/比较cohort、reference资格、速度损失或行程时间/停止/积存等至少两类配套量，单位和统计口径；主张需哪一项主判据、哪一项佐证。
- 降幅/差值、最少样本、连续/累计支持时间、允许间断、起止括号、空间关系容差、参考波动处理及必要敏感性取值。**每个阈值都要有来源或标明探索性研究选择并审查，不能由Sol low看完新结果再选择。**
- R通过计数/分母/窗口、最少可解释通行支持、积存/队列状态与未完成处理。非零事件是必要观测，非充分适用性证据；由reviewer在卡中说明多大支持足以回答这个有限用途。
- R到达共享区的路径规则、U暴露/流动量、TLS解释、已知混杂；不设需要证明纯因果U损失的额外门。
- Q4连接证据：相同场景版本、需求对比、种子、窗口可比性，以及M受损和R通行是否有注册的重叠窗口或可解释的相邻状态关系。
- 预热/需求/观测/后段的数值、理由、边界判定。长路段新增旅行时间必须进入时域设计；若改变时域需对照对称应用，不沿用旧1500/2700作为当然充分。
- 关键来源/观测缺失、解析或身份错误记为blocked_by_evidence_error；完整合格但方向冲突、阈值边界不满足、仅单seed通过记为not_resolved。技术失败保留attempt，不与科学阴性混为一类；禁止删除不利seed或用补跑seed替换。

新规则从旧记录形成是探索性制定，不称独立检验。B完成后仅对有新验证信息的数据用于事先注册判定。旧reference可列为seen/reused背景；同版本同需求同seed的确定性重跑或新目录不使旧轨迹成为未见证据。仅新阈值重标旧轨迹不足以解锁RG3/RG5。真正新增观测若提供旧档案无法获得的信息，应在B明确其确认价值；需要未见seed/条件的分支也在B预先登记，不能事后增加。若纯技术测量修正，旧数据重算可证明修复正确，但一般不能单独完成科学适用性确认。

### S6-B02 — 有限矩阵及预算（管理提案，不是充分样本量）

默认可审查上限：**一项候选方案、至多两个场景版本（当前与候选）、每版本两个条件、每条件两个固定seed。**注册时填写具体run_id、参数、seed，整卡预算可以下调，不能默认为已授权。

| 用途 | 新SUMO启动上限 | 使用条件 |
| --- | ---: | --- |
| 候选版本技术smoke | 1 | 只验证加载/路径/检测，不作Q2-Q4成功证据 |
| 完整匹配验证矩阵 | 8 | 2版本×2条件×2seed；当前版已有兼容档案可合法复用时扣减，不伪造新独立重复 |
| 同参数技术重试 | 1 | 仅明确定义的技术失败，保留原attempt；不能因现象不理想重试 |
| **硬上限** | **10** | 包括失败启动；不动Stage4剩余retry |

建议netconvert硬上限6次：最多2次/版本的构建或静态核验（4），另2次技术修复余量；**若现有runner每run自动netconvert导致不能满足此上限，C阶段必须先实现编译产物复用，或在B卡明确提高netconvert上限并重新批准，不能暗中超额。**TraCI/GUI=0；需要时另列理由和精确上限。CPU墙钟/磁盘上限由A实际档案规模、运行日志和新路网规模估算，B填写 `max_wallclock_s_per_run,total_wallclock_budget_s,max_total_archive_bytes` 实值，提供估算依据；不可留null启动。

上述预算是整个本Stage6验证块共享：smoke和验证合计只能使用一次同参数技术重试，不能每run/每段各重试一次；6次netconvert从SG6-BUILD到D累计，包含失败构建，不在下一段重置。预算检查同时计入实际启动和未解除的reserved/unknown；binary版本查询单列invocations日志，不冒充交通运行也不隐藏。

两seed用于有限重复和不一致暴露，不代表统计功效。reference未确认、候选无鉴别力或条件参数未定时，不能套用这张表运行。精确注册可采取首组后停止，但必须在卡中写清：首组失败/矛盾则停止；首组阳性也不能跳过剩余已要求seed。不能用结果决定再发明第三条件/第二候选。

### S6-B03 — 锁定科学卡草案，列实现依赖

产物 `BASE/validation_card_draft.json` 与 `docs/STAGE6_VALIDATION_DESIGN_REGISTRATION.md`：锁定研究问题、比较矩阵、阈值/窗口与失败规则、候选参数、预算及其依据。科学必填字段无unknown，工程实现尚未生成的argv/source/compiled hash明确列为 `pending_C`，`launch_eligible=false`。

工程核实现方案，数据核分母/schema，reviewer核可区分性。B通过只允许进入已授权的C段准备，不能启动SUMO/netconvert，也不能把未实现命令说成真实可用。**先设计研究规则，后实现/构建，再批准最终运行卡**，避免要求尚未生成的network哈希导致循环。

## 6. C段：隔离实现、离线核验，再受控构建与精确启动审批

### S6-C00 — 隔离新版本

只在新 `config/scenarios/<candidate_id>/` 与新运行目录修改；保留原minimal scenario。记录变更文件hash、编译输入、实际几何/连接/插入规则、必须同步改变的检测位置。禁止为通过门而关闭安全插入/警告/碰撞处理。

旧Stage3/4脚本合同不能接受新拓扑时，工程建立新的Stage6入口与合同，不更改旧合同让它“通过”。拟新增CLI名称由工程在capability_audit登记；本计划不把尚未存在的 `--scenario-dir/--output-dir` 当成现成参数。

### S6-C01 — 最小实现及测量合同

需要时新增：隔离配置选择、已编译network复用、独占输出目录、运行前计数、fail-closed校验、不可变来源快照和独立验证器。新配置编译使用netconvert属于有预算的执行，不能偷偷塞进“离线测试”。本步先验证已有编译fixture/模板；真候选编译留C03的独立构建门。

新合同必须覆盖编译后的全部相关lane（含internal）、M入口至下游、完整R路径及U共享区、检测器坐标/cohort、TLS movement link、原始输出频率、每项单位/分母、无车null/缺观测、端点、图/表定位。若改M路段，测试必须防止departPos仍跳过上游，使名义长度无实际交通。

### S6-C02 — 离线首项门与SG6-L

至少以下12组失败模式各有fixture和独立可核预期：

1. source/config/hash漂移；2. 未登记scenario/seed/启动预算；3. lane/ID未知或重复；4. FCD缺速/非有限/缺多帧；5. TLS错标签/错误link；6. E1有贡献坏速度/空贡献；7. internal-lane停止及路径互斥；8. 入网跨窗口/末端截尾；9. 聚合真实尾箱/贡献权重；10. 两seed缺一边不自动补零；11. nVehEntered与nVehContrib/请求与实际流量混用拒绝；12.中断恢复/唯一attempt/取消终态/禁止覆盖。

每组子例列明预期拒绝或数值，不把“12个测试函数通过”当12类全覆盖。测试不得调用真实SUMO/netconvert。必须保证失败留下错误记录且无成功manifest；独立check不导入生产聚合/分类函数作为oracle。

SG6-L完成：12/12组有有效覆盖、fixture断言全部通过，实际argv能对应真实已实现入口、B科学卡仍同hash、路径无覆盖、专业Blocker/Major=0。这里是已批范围内部工程门，不向用户逐条重复索取确认。若为实现必须改变卡参数/预算才重新提交修改卡。

### S6-C03 — SG6-BUILD：实际编译及空间核验

先形成构建包：真实已实现编译入口的argv、source/XML/input hash、限定输出目录、预期变更及最多6次netconvert的细分额度、无SUMO/TraCI/GUI说明。若此前阶段执行授权已明确包含该构建包及额度，则直接执行，不重复询问；否则只请求这项具体构建授权。

每次netconvert预扣额度、保留命令/日志/exit、输出network哈希。独立检查实际lane长度/连接/via/优先权/内部lane、detector物理坐标及TLS link，并逐项对照批准的变化清单。编译意外改变R/U路径、merge或信号时停止，查明后用新revision修复，不以“编译成功”代替一致性。

产物：编译归档、compiled_semantic_diff.csv、actual_observation_map.csv、build_receipts.json。完成：构建输入到输出全绑定，变更清单外未解释语义差异0，必需观察域映射100%，只消耗已批准netconvert次数。

### S6-C04 — SG6-P：最终SUMO运行卡

产物 `docs/STAGE6_VALIDATION_LAUNCH_PACKAGE.md` 和 `BASE/approved_launch_card.json`（批准前文件状态为Proposed）。逐run写真实argv、source/compiled/data-contract/rules/binary hash、预算、输出、顺序和停止分支。必须在SG6-P前为每个登记attempt预分配独占目录并生成其demand/additional/sumocfg及materialization_manifest，或批准明确确定性路径展开规则并在启动前核验展开结果。不得批准后随机mkdtemp并无绑定地重写已hash配置或E2 endpoints。compiled network只读复用；每attempt生成文件内容和路径均有卡内预期hash或经批准的确定性构造合同。工程确认无需隐含编译，数据确认分母及独立复算方法，reviewer确认编译后的空间仍能回答B问题。

完成：所有launch-critical字段实值齐全，source/evidence解析失败0，关键Blocker/Major=0；用户明确批准精确卡和相应hash后方可进入D。compiled hash存在不代表运行获批。若B科学设计因构建变化失效，应回B按新版本审核，不能只换一个hash。

## 7. D段：执行已批最小验证块

### S6-D00 — 已编译配置的smoke

启动前先写attempt、命令、软件版本、配置hash及预算预扣；进程启动即计数，不因退出失败回退。单次运行后依次存stdout/stderr、exit、时间、实际目录、每个原输出hash与状态。已存在receipt禁止重启同attempt。

读取C03绑定的编译产物、核hash，再跑最多1次smoke（本步不默认重新netconvert）。核M实际入口位置/沿程覆盖、M/R/U/X连通、信号link、无源外引用、输出/schema、异常。smoke不能作“缺口解决”证据；仅退出0不算通过。技术失败按卡处理，最多一个同参数重试；语义不合格不能借技术重试改参数。

### S6-D01 — 首个完整可比较单元

按注册顺序运行首seed所需reference+challenge及版本对照，保持匹配因素。复用旧档案必须满足拓扑、需求、时间、版本、原输出/schema与判据所需字段的兼容审计；否则只能作背景，不能计为匹配运行。

工程归档→数据检查→reviewer查首组能否解释，完成后才继续。任何数据错误/预算越界/不可比较配置立即停止；交通结果不支持假设属于有效阴性，不删除。首组不能临时改成功判据或测点。

### S6-D02 — 剩余登记单元

只运行卡中剩余条件/seed。若停规则触发，把未运行行标cancelled_by_stop_rule并说明，不计为完整科学矩阵。每个attempt分列 `execution_status=not_started/running/completed/technical_failure`、`analysis_qualification=qualified/incomplete/invalid`、`scientific_result=supports/does_not_support/inconclusive/not_evaluated`；逻辑run另有cancelled，取消项不是已执行attempt。技术完成可以同时科学阴性，不能用一个status互相覆盖。

### S6-D03 — 全量独立核验与报告

输出格式按§9，12旧run背景和新验证run分层。最终推断使用的全部reference/challenge、所有seed及必需指标都须独立核验，不只验证新run或阳性seed。新run的来源/端点/指标/关键事件全量独立复算；旧reference的旧核验只有在来源、定义、窗口、空间、分母与代码资格均一致且有receipt时才可复用，否则从旧XML按新定义派生并独立复算。比较表保留所有注册条件，NULL必须有解释。逐seed执行预登记规则，展示阈值附近的原数据与已注册敏感性，不用事后调整重分类。

完成：注册逻辑行终态100%，已运行attempt记录100%，必需source哈希100%，整数账目残差0，未知/重复/关键缺帧0（否则受影响结论blocked），新run×4class×登记端点100%分列；核心计量独立复算100%。浮点容差预登记为数值误差容差，不解释为现实误差。

## 8. E段：什么才算解决specific_obstacle

### S6-E00 — SG6-R逐项审核

B阶段登记全部 `rule_id × scenario × condition × seed × window` 必需键及聚合规则。`resolution_rule_results.csv` 一行一个明细键，包含rule_hash、metric/evidence IDs、实测值、分母、阈值、qualification与判定。`resolution_gate.csv` 一行一个RG汇总，引用明细及reviewer理由，分列required/passed/failed/inconclusive/not_executed数量。因停止取消的必需seed仍在成功门分母中，不能删除后宣称resolved。

| 门 | 必须满足的完成线 |
| --- | --- |
| RG1 来源和技术完整 | 规定source/端点/覆盖/独立复算100%，未关闭关键数据问题0；不以删除失败提高分母 |
| RG2 真实观察域 | 实际M入口、上游—合流—下游路径覆盖满足注册空间界限；R/U范围对应同一版本；名义长度不代替实际轨迹 |
| RG3 主线受损 | 至少一个注册challenge在全部规定seed达到B01已批准的主判据与佐证规则，给出完整时空证据及参考资格；未知或冲突不能pass |
| RG4 R/城市证据 | 同一注册版本内有满足卡中最低支持的R通行与积压/共享区U暴露；给出TLS解释、R/U账目；纯红灯/网外排队不够 |
| RG5 双侧关联 | Q1–Q4均在声明用途内supported；M与城市证据条件可比、有解释关系，受影响核心question-level unknown=0 |
| RG6 判据/随机性/时域边界 | 两seed全部列出，规则未经事后修改，预登记窗口/阈值敏感性全部有结果；时域不足、窗口冲突如何处理按卡，不强称稳健 |
| RG7 独立科学复审 | 五项测量检查有具体证据和范围；重要科学Blocker/Major=0，普通E1逐ID限制等非核心限制全部披露 |
| RG8 用户接受 | 用户明确接受“该版本在该需求范围内达到开始正式设计的无控制基准适用性” |

RG3/RG4具体阈值在B01填实并预批准；本文件不伪造统一80%速度/90s或95%入网标准。RG5的零未知只针对最低基准用途，不要求解决正式controller、权重、最优seed数和纯因果U损失等后续设计问题。

### S6-E01 — 通过出口

先提交 `docs/STAGE6_OBSTACLE_RESOLUTION_ACCEPTANCE_PACKAGE.md`，包括：改变了什么、真实结果、Q1–Q4、RG1–RG7、反例、失效域、各预算实际使用、22项继承修订、仍未知事项。RG1–RG7全满足且RG8用户接受后写 `obstacle_status=resolved_for_baseline_design`。如果用户此前已明确批准“满足RG1–RG7并经科学复审后自动进入F”，在RG8引用该条件授权与实际通过证据即可，不重复索取相同许可；一般“继续执行方案”不自动改写为这种特定接受。

**只有该状态才解锁F。**预登记结果不充分时不得用“解释了为什么失败”代替“用途已成立”。找出原因与解决适用性缺口分别记录。

### S6-E02 — 阴性/预算停止出口

任何一项成立即停止新运行：精确卡矩阵完成；硬预算达到；首项技术门失败且无合法重试；没有可区分的新试验；需改变研究方向/行为模型/核心参数而卡未授权。

状态 `not_resolved`（合格证据但用途未成立）或 `blocked_by_evidence_error`（资料/解析错误），不得合并。生成 `docs/STAGE6_ROBERT_OBSTACLE_BRIEF.md`：一页问题/现象/范围、一页我们提出的最小选择及理由、最多3个需Robert判断的问题。**这不是正式实验设计草案。**不自动新增Stage6b、第二候选、更多seed或增加需求；需要新依据和新的预算提案。发送仍需明确授权。收到真实反馈才更新SUPERVISOR_FEEDBACK。

## 9. 数据及运行登记最小格式

| 文件 | 必填字段/检查 |
| --- | --- |
| source_registry.csv | source_id,physical_run_id,stage,scenario_hash,condition,seed,path,sha256,role,compatibility；实际run去重，path/hash100%核验 |
| hypothesis_evidence.csv | H1–H6、预测、反证、观察与未知、evidence_id、下一步动作 |
| metric_registry.csv | metric_id,source_field,cohort,space,unit,window,denominator,missing_rule,aggregation_rule；禁止无区别q字段 |
| run_registry.csv | run_id,scenario,condition,seed,planned_or_reused,attempt_id,status,cancel_reason；逻辑run与attempt分开 |
| entry_vehicle_records.csv | run_id,id,class,depart_time,depart_lane,depart_pos,first_fcd_time,lane,pos,distance_to_merge,depart_delay,coverage；实际departPos与首FCD位置分开；按实际入网车辆登记分母 |
| endpoint_accounting.csv | run_id,class,t,P,E,A,N,O,qualification；只在计划总体已定义的端点用P−E；中途未核排程不能伪造O曲线 |
| space_time_metrics.csv | run_id,cohort,lane_or_region,begin,end,measure,value,unit,n_obs,coverage,qualification |
| event_evidence.csv | run_id,event_id,event_type,vehicle_or_region,first/previous_label,last_label,sample_count,censoring,TLS_context,qualification |
| paired_comparisons.csv | comparison_id,scenario_pair,condition,seed,metric_id,lhs,rhs,delta,eligibility,missing_reason；单边缺失保留 |
| evidence_index.csv | evidence_id,path,sha256,locator,scope；所有表/报告引用反向解析100%，不能只验非空 |
| resolution_rule_results.csv | 预登记rule×scenario×condition×seed×window键；实值、适用分母、资格、缺失/未执行与规则判定 |
| resolution_gate.csv | RG1–RG8汇总；明细引用、required/passed/failed/inconclusive/not_executed数量、review意见 |
| independent_verification.json | 独立方法、所有分母、实际重算数、容差、逐类差异、失败、限制、来源/实现hash |

所有数值表增加 `value_state=observed/observed_zero/no_contributors/missing_observation/not_applicable/not_paired` 与reason。完整无贡献区间计数/计数率可0、加权速度null；缺样本或坏速度不能填0；无episode行不能自动视作零；R零事件必须同时有合格观察时长与车辆分母，不能仅凭空表判排除。

候选配置、工具、raw归档、派生表和报告分别存hash，不构造报告↔manifest循环依赖。最终事实锁在不可变evidence snapshot；操作ledger可更新但不是旧报告的规范输入。不得用模型生成的“审核PASS”冒充可追踪实际审核来源。

## 10. F段：解决后才开始正式实验设计草案

### S6-F00 — 22项继承和研究问题细化

读取SG6-R批准版本与更正handover，逐项更新范围/依据/资格，不照抄0/1500/1200、17/23、EJMI或储存长度。保留四类资格：reuse_with_scope、candidate_requires_validation、requires_scientific_decision、not_available_or_ineligible。正式选择须标签“已有证据/候选/研究选择”。未决项有ID、责任人、决定所需依据；不填虚构值。

### S6-F01 — 正式设计草案

新建 `docs/FORMAL_EXPERIMENT_DESIGN_PROPOSAL.md`，Proposed。逐项写：1问题/假设；2场景/适用域；3无控制与ALINEA、必要时override对照；4固定与干预因素；5需求范围；6主次指标/单位/总体；7时域与截尾；8重复数/精度；9校准/评估数据分离；10异常/缺失规则；11比较/不确定性/敏感性方法；12预算/停止。12/12主题有提案或编号未决项，空白无说明=0。

这里才讨论正式主线/城市保护阈值、系统延误/外部等待、sweet-spot可接受区、控制参数及统计精度。正式重复数需主指标方差和需区分差异/区间宽度，不机械用探索两seed；若需pilot，另写有预算的pilot卡，不在F执行。

### S6-F02 — Robert审核材料与反馈

一页证据/解决过程，一页我们提出的设计/选择，附完整草案。最多3个核心问题：研究贡献及Breakdown/Capacity Drop角色；对照/保护指标/储存与城市假设；时域/随机性及剩余验证。先由用户审阅，明确授权才发送。反馈按comment→section→proposed_change→verification→approval逐条追踪，100%有处理或待确认状态。

### S6-F03 — 终点

完成草案与材料并提交用户。收到反馈、必要验证和内容批准之后才另行写入/冻结EXPERIMENT_PROTOCOL；正式运行另行授权。不能以“Stage6完成”暗示正式批次已经获批。

## 11. Sol low执行顺序与恢复

每一步严格：读ledger和本步输入→专业路由→验证输入路径/hash/授权→执行唯一动作→核预登记分母及失败→写独占新revision→数据/科学门→更新ledger与WORKLOG→进入下一步。到SG6-P/SG6-R等研究审批点才停，不对每个已授权文件读写重复确认。

恢复时先核是否有attempt已启动、目录/receipt已有，不能把中断当从未运行。进程状态无法确定则先查日志/进程证据，不再启动。失败保留INCOMPLETE；同参数合法技术重试用新attempt并消耗预算。变更结果目录或hash只用于真实新revision，不用于绕过已失败判据。

已知真实入口及风险：

- `src/scenarios/run_minimal_uncontrolled.py` 有 `--profile --q-main --q-ramp --seed --warmup-s --measurement-duration-s --demand-end-s --post-demand-clearance-s --sumo-binary --netconvert-binary --validate-only --reanalyze-summary`；q-main/q-ramp成对。没有承诺现成几何/--scenario-dir/--q-urban/--output-dir入口。
- `--validate-only` 会调用netconvert并写文件，不能用于A或C00–C02零启动工作；整库测试可能启动SUMO，禁止用作“快速检查”。
- 旧 `analyze_stage3_baseline.py`、`analyze_stage4_qmain.py` 受batch/topology/source hash约束；Stage3修复hash与旧合同不同。A/C必须建立新映射/合同，禁止编辑旧批准hash。
- `stage2_queue_diagnostic.py` 硬编码旧/tmp与事件；`--reanalyze-summary`依赖runtime并写tmp；`check_e2_coverage.py`调用TraCI，均不能冒充A段档案只读入口。
- 旧 `build_stage3_t34_review.py` 未配对键处理需修复/替代并测试后才复用；原398/43及5个补件不覆盖所有未来missing模式。
- 精确命令由工程在实际实现后写进运行卡的argv数组（可执行文件真实绝对路径），Sol low只执行已审argv，不拼写猜测flag、不用原runtime的sumocfg直接重跑。

给Sol low接续文本：

> 按docs/STAGE6_OBSTACLE_RESOLUTION_EXECUTION_PLAN.md执行已批准范围。先核本次是仅规划、A段离线执行、还是具体运行卡启动；不要把它们混成一次授权。保持specific_obstacle为待解决的有限用途缺口，保留旧源与dirty worktree。依A→B→C→D→E→F推进，必须使用对应专业代理。A及C00–C02零SUMO零netconvert；C03只允许已批准构建；D只能按精确批准卡。SG6-R通过且用户接受前不得创建正式实验设计草案。卡字段未填、接口未实现、缺证据或预算不足时留下具体缺项，不猜数、不换seed、不软化标准。阴性按E02收口为Robert障碍咨询，不无限续跑。按步骤记录并恢复，不重复索取已授权动作的确认。

## 12. 方法依据、限制与规划验收

本轮重新核对一手资料：FHWA的错误检查流程支持先查软件、输入和行为，避免用参数补偿编码问题；技术smoke只证明技术可用。[FHWA 2019 Chapter 4](https://ops.fhwa.dot.gov/publications/fhwahop18036/chapter4.htm)

插入选项会影响实际入网，配置意图不能代替实际轨迹；本计划据此要求核实际入口与观测域。[SUMO VehicleInsertion](https://sumo.dlr.de/docs/Simulation/VehicleInsertion.html)

随机性需独立考虑，正式替代方案重复数应考虑波动；本计划两seed和10-start上限只是有限探索/管理提案，不是文献证明的充分样本量。[FHWA 2019 Chapter 6](https://ops.fhwa.dot.gov/publications/fhwahop18036/chapter6.htm)

正式freeze仍需研究选择和反馈；上述指南不能保证指定模型能产生想要的现象。本方案不能保证specific_obstacle一定能解决，也不能保证Sol low完美执行；它通过明确输入、规则、专业审核与停止门减少可自行猜测的步骤。

规划交付核验：顺序符合用户；科学成功门与技术完成率分开；12条历史run不重复计数；未定值有填实步骤及责任；新接口标未实现；预算包含smoke/失败/重试；阴性有出口；SG6-R阻止提前草案；没有本轮新运行、参数选择、控制器或正式协议修改。专业审查记录见下表。


### 12.1 本轮规划审查记录

| 角色 | 实际检查及已处理事项 | 最终意见 |
| --- | --- | --- |
| simulation_engineer used | 实际入口、约1.4km名义主线与有效行程区别、构建先于compiled-hash运行卡、运行时文件绑定、共享预算/预留计数及隐藏启动入口 | 规划检查通过，无剩余必须修改项 |
| data_analyst used | 12实际run、两种q、复用参考核验、值状态、未配对保留、规则明细/门汇总和取消分母 | 数据规划通过，无剩余必要修订 |
| scientific_reviewer used | 不强迫阳性、旧reference与新信息、无效证据与有效阴性、Q1–Q4用途门、先SG6-R再F、失败咨询和条件授权 | 指定Minor已修正，规划审查通过；不表示未来用途已通过 |

科学终审最后要求B00区分科学必填与工程pending_C，已按原建议修正；主代理复核其与B03/C04一致。主代理检查24个步骤ID唯一、JSON可解析且不可执行、10-start预算算式、正式草案不存在及协议仍为空，均通过。未来实现、运行覆盖、独立对账与用途门仍为not_verified。

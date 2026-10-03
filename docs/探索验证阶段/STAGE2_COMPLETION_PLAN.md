# Stage 2 完整收尾与 G2 验收执行方案

日期：2026-09-09。版本：1。**状态：C0–C5 completed；C6/G2 用户已批准，Stage 2 有限诊断正式关闭。**下文待批准/待验收指令保留为原执行流程，不代表当前状态。

本方案接续已经完成的 S0–S2、G1 v2 D0–D7 和定点 S3–S5，不重做这些步骤。使用 C0–C6 标记剩余工作，避免把已经完成的 S3–S5 再称为未执行。用户批准本方案后，它才成为本轮收尾执行依据；旧六行 G1 运行清单不恢复授权。

## 1. 完成目标与边界

**本轮要完成的是 Stage 2 有限无控制场景诊断和用户验收，不是完成整篇论文的探索，也不是必须制造 Breakdown 或 Capacity Drop。**

最终回答五个问题：

1. 现有观测能可靠描述哪些位置、车辆和事件，不能描述什么？
2. 固定匝道需求时，降低/提高主线需求对应怎样的主线通过和 R/U 积压表现？
3. 固定主线需求时，降低匝道需求对应怎样的合流通过和城市侧表现？
4. 0/1500/1200 s 适合本轮什么观察；哪些运行受加载、延迟入网、截止截尾限制？
5. 下一步可以研究什么；若有实质缺口，最小待确认问题是什么？

完成不要求：正式容量数值、正式 Breakdown/Capacity Drop 定义、稳态证明、统计显著性、sweet spot、ALINEA、override、正式需求网格、导师已回复或正式协议冻结。

不能把技术错误或缺失关键证据包装为“没有发现现象”。研究现象未建立可以是有效诊断结果；无法证明运行身份、无法读取主要输出等属于真正未完成。

最终使用两个独立状态：

- `stage2_acceptance`: `pending_user` / `accepted` / `blocked`。只能在用户明确 G2 验收后写 accepted。
- `next_step_readiness`: `ready_for_next_exploration` / `requires_specific_decision`。无 Breakdown 或存在已解释截尾，都不自动决定 readiness；依据下一步具体问题所需证据判定。

提出建议和科学审查通过都不等于用户或导师批准。G2 接受诊断收尾也不等于接受正式科学结论。

## 2. 当前事实与复用清单

| 事实/输入 | 本轮处理 |
| --- | --- |
| `docs/STAGE2_S3_S5_VALIDATION_REPORT.md`：新增内部 E1 聚合测量已验收 | 直接复用，不重复测量修复 |
| 基准 `/private/tmp/minimal_uncontrolled__5s3s06d` | C17 唯一既有基准；注意双下划线；只读 |
| C17：3200/720/360/180 veh/h，seed 17，0/1500/1200 s | 与本轮矩阵一致；1858 辆全部入网和到达 |
| 新内部两 E1 全程贡献 715+618=1333；A 窗 1331 | 作为离线新分析入口的已知校验值，不要求新运行得到相同数值 |
| 旧上游 E1 受起点插入污染；新内部 E1 没有 vehID | 保留两个限制，不把 FCD 短内部车道采样名单当完整过车名单 |
| C17 只有 36/300 个 R 首次下游样本在 1500 s 前；最终全部完成 | 说明计划匝道需求和需求期内合流通过不同；不是精确物理过断面时刻 |
| 五个历史探索运行与两次匹配修复 | 保留上下文；时长/需求不匹配的旧点不进入本轮配对比较；同轨迹修复不是独立重复 |
| E2 修复、内部车道核算、几何 v4 和回放 | 已完成，复用对应报告，不新做动画 |
| `docs/EXPERIMENT_PROTOCOL.md` 为空 | 正式参数 Unknown；不阻碍获批的有限探索，不在本轮填充或冻结 |

当前状态与已通过技术证据置信度 High；对新需求条件的可推广性 Moderate；未来现象和正式参数 Unknown。

## 3. 集中批准范围与固定运行矩阵

批准本方案意味着授权 C0–C6 中必要的最小离线实现、以下 7 个新运行、至多 1 次符合条件的技术重试、对应分析和文档。批准不包含新点、新 seed、时长延长、路网/信号/优先权/行为/插入设置改变，或外部消息发送。

### 3.1 推荐且唯一执行矩阵

单位 veh/h。全部固定 qUrban=360、qX=180；全部无控制、同一场景和软件版本。

| 条件 | qMain | qRamp | seed 17 | seed 23 | 信息目标 |
| --- | ---: | ---: | --- | --- | --- |
| C | 3200 | 720 | 复用 C17 | 新 C23 | 当前基准及早期 seed 敏感性 |
| ML | 2600 | 720 | 新 ML17 | 新 ML23 | 放松主线压力后，R 通过及 R/U 积压如何变化 |
| MH | 3800 | 720 | 新 MH17 | 新 MH23 | 增加主线压力后的实现需求、通过与积压表现 |
| RL | 3200 | 360 | 新 RL17 | 新 RL23 | 固定主线时降低匝道请求需求的表现 |

按 **C23 → ML17 → ML23 → MH17 → MH23 → RL17 → RL23** 顺序，逐项启动。C23 先检验新分析合同在同需求另一个 seed 下是否可用。不要后台并行跑完整批次。

选择解释：主线 ±600 是围绕可复用基准的双向探索扰动，匝道减半用于单独改变城市侧 R 请求量。它们不是容量估计或经实证校准的最佳间距。seed 23 是预先固定的第二个随机实现，没有特殊统计意义。该设计是推荐的有限设计，不声称最小样本量或统计充分性。

只计算同 seed 的 ML−C、MH−C、RL−C 对照。两 seed 分别展示，再说明方向一致或不一致；不做显著性检验或稳健性宣称。匹配 seed 也不保证需求改变后每辆车使用完全相同的随机数。

### 3.2 固定时长与预算

| 项目 | 固定值 | 本轮含义与判断 |
| --- | ---: | --- |
| warm-up | 0 s | 保留从空网加载开始的过程，不声称稳态 |
| measurement | 1500 s | 统一有限需求时域，覆盖已有轨迹的积压发展，不保证观察到 Breakdown |
| post-demand clearance | 1200 s | 统一截止预算；1500 s 后仍可能有网外车辆入网 |
| demand end / simulation end | 1500 / 2700 s | 不因清空早晚或结果方向而修改 |
| 常规新 SUMO 启动 | 7 次 | 既有 C17 不计新启动 |
| 全包技术重试 | 至多 1 次 | 仅已定位的加载/写出技术故障；同点、同 seed、同时长 |
| 新 SUMO 硬上限 | 8 次 | smoke、GUI、TraCI 探针及测试中的实际仿真均计数；本方案不额外安排这些 |

重试不得用于：未清空、低实际入网、没有 Breakdown、结果不同、技术 summary 的探索阈值未通过。不得把某点失败后换点或换 seed 称作重试。

需求文件由当前 runner 的实际取整规则生成，**读取生成 XML 才是计划车辆数的权威来源**。预期 M/R/U/X 数量为 C=1333/300/150/75，ML=1083/300/150/75，MH=1583/300/150/75，RL=1333/150/150/75；不一致先解释生成规则，不修改 XML 凑预期。

报告同时保留 requested rate、XML number 和 `number×3600/1500` 离散计划率。例如 M 的离散计划率为 2599.2/3199.2/3799.2 veh/h；它们仍不同于实际入网率和 detector 通过率。

8 条计划记录必须全部留在台账。程序在 SUMO 未启动前失败只记构建失败、不耗 SUMO 启动数；一旦实际启动即占预算，失败输出和重试输出分别保留。预算不是必须用尽的配额。

## 4. 文件、责任和统一执行台账

主代理拥有本方案、最终报告、PROJECT_STATE、WORKLOG、必要 README 更新；simulation_engineer 负责运行登记及必要技术适配；data_analyst 负责新分析入口、测试与派生产物；scientific_reviewer 严格只读。所有角色先完成自身 Context Preflight。禁止两个代理并发编辑同一文件。

执行批准还包含主代理在检查现有内容后添加一条窄 `.gitignore` 规则 `/artifacts/stage2_completion_*/runtime_archive/`，并在 README 说明归档用途和离线入口。保留其他规则；不忽略整个 artifacts，不自动提交大型原始归档或 private 监督材料。本轮编制方案不修改 `.gitignore` 或 README。

拟新增路径（执行批准后才创建）：

- `src/analysis/analyze_stage2_exploration.py`：专用离线分析入口。
- `tests/test_stage2_exploration_analysis.py`：纯离线边界测试。
- `data/processed/stage2_completion_<batch>/`：manifest、运行台账、审计、比较、独立验证及必要中间数据。
- `results/tables/stage2_completion_<batch>/`：有限表格。
- `results/figures/stage2_completion_<batch>/`：至多两张标准静态诊断图。
- `docs/STAGE2_COMPLETION_REPORT.md`：C0–C6、科学审查和 G2 确认包。
- `artifacts/stage2_completion_<batch>/runtime_archive/<run_attempt>/`：C17 与本轮全部实际尝试的原始输出无损归档，包括失败尝试。该新目录纳入本方案集中批准范围，不向 `data/raw/` 写入。

`<batch>` 在 C0 创建一次，使用实际日期及无冲突序号；后续复用该值，不使用“最新目录”glob。新版本用新 `_r2` 目录，保留首版。不覆盖旧 dataset、结果、报告或运行目录。`data/raw/` 全程只读。

运行台账每条至少包含：逻辑 run_id、条件、seed、计划参数、来源/配置 hash、原始目录、实际命令、SUMO/netconvert 版本、启动/结束时间、实际启动次数、退出码、运行完整性、分析适用性、失败原因、重试关联、分析产物路径。

台账顶层固定为 `schema_version=1,batch_id,authorization,budget,runs`；`budget` 含 `planned_new_starts=7,max_new_starts=8,retry_allowance=1,actual_new_starts,retries_used`。`runs` 固定八条逻辑记录（`C17,C23,ML17,ML23,MH17,MH23,RL17,RL23`），每条有 `condition,q_main,q_ramp,q_urban,q_x,seed,warmup_s,measurement_s,clearance_s,status,attempts`；每次尝试另存 `attempt_id,runtime_dir,archive_dir,sumo_started,exit_code,retry_of,source_manifest,execution_status,measurement_status,analysis_status,reason`。未开始的数值/路径为 null，不伪填通过。C17 标记 reused，不计新启动；技术重试追加 attempt，不替换首条。

补充 `steps` 记录 C0–C6 的 owner/status/evidence/resume_point；每条运行有 `origin=reused|new,selected_attempt_id`；attempt 记录命令、版本、时间和 `analysis_revision`。预算由全部新 attempt 的实际启动状态重算，不能用成功条数代替。只有首条技术失败且获规则允许的同参重试成功时选择重试作为分析来源，不在两个有效结果中择优。

每一步按 `pending → running → completed / blocked` 记录；每个运行同时区分 execution、measurement、scientific eligibility，禁止合并为一个 pass。中断后先读台账和已登记目录核对状态，不根据 stdout 丢失自动重跑。

## 5. C0：接续、授权与来源检查

**负责人：主代理；工程支持必要的只读检查。**

1. 读取 AGENTS、PROJECT_STATE、本方案、DECISIONS、最新 S3–S5 报告和相关 WORKLOG。明确是执行授权还是仅规划；仅规划停在方案交付，不启动 C1 后实现。
2. 读取 `git status --short`。保留已有 dirty worktree；不提交、不建分支、不重置。预期之外的目标文件冲突才暂停相关写入，不把既知未提交变更当作必须清理的问题。
3. 建立批次目录和台账，登记 8 条逻辑记录及 7 个待运行项、预算计数为 0。登记用户批准原话和范围，不自行更新 DECISIONS。
4. 检查 C17 的 summary、运行配置、compiled network、需求、additional、tripinfo、vehroute、FCD、六 E1、E2、TLS 和日志路径是否存在可读。由配置和实际命令解析路径，禁止猜文件名。
5. 为实际使用的源文件和代码登记 hash，按 C17 实际大小和本轮有限批次检查可用磁盘空间。既有临时原始文件不移动、不删除、不重写；将 C17 无损复制到排他新建的归档目录，复制前后逐文件 SHA-256 对账。manifest 记录原绝对路径、归档相对路径、大小和 hash；不改复制文件内部的路径。只归档本包所需 C17 和未来本轮尝试，不复制其他历史运行。如关键源已丢失，标记 dependent task blocked，不自动耗新预算补跑基准。
6. 验证当前配置仍与已验收观测合同一致，软件仍为 SUMO/netconvert 1.26.0；已发生实质版本/场景改变时先报告差异，禁止把新状态当匹配基准。

**出口：**授权、身份、来源、预算都可核查；不要求重做历史回放或 17 项旧修复验收。

## 6. C1：在仿真前补齐最小离线分析合同

**顺序：simulation_engineer 输出技术合同 → data_analyst 实现 → scientific_reviewer 审查新合同。**

### 6.1 工程先确认的内容

1. 确认 runner 现有参数和输出选项；不得发明 `--output-dir` 等不存在的参数。
2. 核查当前版本的 flow ID、number 调度和仿真时间离散化，及 unfinished tripinfo/vehroute 输出覆盖。先用本地实现、版本材料和既有完整 C17 核查；必要时查官方资料，写明哪些规则仍未证明。
3. 旧 `analyze_departure_realization` 的名义排程和“缺 trip 即 waiting”不得当作新截尾数据的可靠事实。保留旧 summary，另建本轮审计字段；不借此大幅重构 runner。
4. 若静态证据无法证明未入网车辆排程，给出 `schedule_status=unverified` 的受限合同；不得为此偷偷加仿真或改成显式 vehicle 需求，因为后者可能改变实际调度。

### 6.2 分析入口必须实现的内容

建立只读源文件的批次入口，建议 CLI 合同：

```text
.venv/bin/python src/analysis/analyze_stage2_exploration.py \
  --ledger <batch>/execution_ledger.json \
  --output-dir <new_processed_revision> \
  --table-dir <new_table_revision> \
  --figure-dir <new_figure_revision>
```

这是**待实现接口**，不是声称当前已存在。支持台账中 pending/failed 项，只分析有可用输出的记录，并将其他项显式带入覆盖报告。仿真调用必须为零。

入口通过 manifest 将源配置/summary 中的原绝对路径解析到归档文件；不依赖临时目录继续存在，不重写归档配置。缺映射、hash 不符或路径越出本次归档范围必须报错，不静默退回另一份文件。代码 hash 单独记录，不把代码路径误解析为运行输出。

每次归档在 processed 保存 `source_map.json`，明确 original absolute path → archive relative path → SHA-256；路径只能落入本 attempt 目录。复制期间源文件变化则本次归档未完成，等待写入结束后重新核验，不能修改原输出。归档复制失败不占 SUMO 重试预算，也不是重新启动仿真的理由。

归档先排他写入同级 `.partial` 目录，拒绝 symlink 和特殊文件；source 复制前后 hash 不变、复制件逐文件大小/hash 全相等后，才原子改名为未存在的最终目录并登记 complete。失败 attempt 可以没有 summary，但所有现存文件仍保留并标 partial/source_incomplete。manifest 是 processed 侧的独立映射，不能通过字符串替换原 XML/summary 来“修复”路径。磁盘不足时保留当前文件和台账，暂停新启动；不删旧数据腾空间。

固定分析版本：`revision_01` 只验证 C17，`revision_02` 验证 C17+C23，`revision_03` 分析全部条目终态；集中审查确需修改时才加 `revision_04`。processed/table/figure 下各建对应独占子目录，台账指向当前有效版本，保留全部旧版。无需每跑一项重算整个批次。

可复用旧模块的 E1 转换/加权、hash、拒绝覆盖和内部车道映射；不能直接复用旧主入口的固定 C17 IDs、配对记录相等断言、完整 cohort 假定及旧账目依赖。新需求和新 seed 的轨迹无需等于 C17。

**逐车合同：**有可靠计划身份时每个计划 ID 一行，记录 class、planned time/source、actual depart、arrival、departDelay、observation end 和证据状态。没有可靠计划身份时只列已知成员和聚合未知量，不生成虚构 ID。

| 车辆状态 | 必要证据 |
| --- | --- |
| arrived | 有实际入网和有效到达记录 |
| entered_unfinished | 有实际入网，截止仍未完成；正确处理 arrival 哨兵 |
| not_entered_confirmed | 计划身份和入网记录覆盖已核验，且 FCD/vehroute 无已入网反证 |
| record_missing_unknown | 有计划/其他来源但缺失记录原因未能证明 |
| plan_identity_unknown | 计划 ID 总体无法核验；可另列未知数量 |

对有 depart/arrival 的车辆，以 `depart-departDelay` 检查其计划时刻；该检查只覆盖观察到的成员，不证明缺失成员。核验通过才计算依赖计划时间的网外等待。缺记录不能填成零。

为避免把不同未知混成一个状态，固定四个资格字段：`plan_count_status`、`schedule_time_status`、`departure_coverage_status`、`arrival_coverage_status`；`schedule_status` 作为总体说明，不替代这四项。

逐 ID 计划时刻未知不自动抹掉可靠终点总量：若生成计划数 P、唯一实际入网 E、有效到达 A 及输出覆盖均核验，可报告按类终点未入网 P−E、网内 E−A，不声称已识别每个未入网 ID。1500 s 也使用此关系时，先确认全部计划需求属于 `[0,1500)`，且 E/A 使用 `<1500`。覆盖未核验时，P−已观察入网只能叫 `unaccounted_count`。中途逐时计划数和精确网外延误仍需计划时间资格，不能套用终点总量的许可。

**时间和守恒：**cohort 用 event `<t` 的 before-step 定义；仅在计划总体和排程可靠时检查 `planned_before(t)=outside(t)+in_network(t)+arrived(t)+unknown(t)`。unknown 非零不能称完整守恒通过。网内状态另与含内部车道的 FCD 核对，明确采样时点差异。FCD/TLS 保留原标签；完整空帧为零、缺帧为缺值；没有 t=2700 FCD 帧不能补零。

**截尾：**2700 s 仍在网、未入网和未知分别记录。只对完成者报告完整旅行时间并标明分母；不以完成者均值代表整个计划总体。计划时刻不可靠时不得报告整个总体的精确网外延误。截尾结果不自动触发重跑。

### 6.3 最小离线验证和入口门

1. 用手工小 fixture 测试：0/1500/2700 边界、unfinished arrival、缺记录 vs 确认未入网、未知/重复 ID、零计划分母、E1 零贡献/缺区间、FCD 缺帧、跨箱 R 事件、源 hash 变化和拒绝覆盖。所有测试禁止启动 SUMO。
   加一项路径解析测试：通过测试 resolver 禁止读取原 `/private/tmp` 来源，仍可从归档重算 C17；不移动、删除或重命名真实原始目录。
2. 用完整 C17 验证新入口：1858 总体、1333/300/150/75 分组、实际到达/插入、两内部 E1 各 90 区间、1333 全程贡献及 A 窗 1331。原始数据 hash 前后相同。
3. 运行已存在的静态测试类：`.venv/bin/python -m unittest tests.test_minimal_uncontrolled.MinimalUncontrolledScenarioTests tests.test_internal_e1_analysis`；新增纯离线测试按新模块运行。**不运行整个 `tests.test_minimal_uncontrolled`，其中包含真实 SUMO integration tests。**
4. reviewer 审查计划身份、覆盖、遗漏重复、独立核算和边界测试。未核验排程可保留 Unknown，但若连可靠的实际入网/到达与主要测量都不能输出，则不进入 C2；先做一次集中离线修订。
   核心可用性按问题逐项检查：M 的新 E1/实际入网、R 合流观察和 R/U 路内状态须有足够有效证据回答对应问题。不得把这些全部降级为 Unknown 后仍称核心问题已回答。`schedule_status=unverified` 主要限制依赖排程的网外时序和延误，不把缺值解释为零或稳定。
5. 一轮修订后仍有阻止本轮核心比较的 Blocker/Major，交具体阻塞包，不启动批次。不因可选增强或正式协议未冻结而阻止限定探索。

**出口：**新入口能读 C17；所有依赖推算都有来源状态；后续有限运行不依赖虚构排程；不是要求新入口在所有未来情形完全通用。

执行分支固定如下：仅逐车排程未知但实际状态/主要测量可靠→继续并禁用相关推算；可核验截尾或有效阴性→继续；有可靠证据界定局限但下一问题需额外决定→报告 `requires_specific_decision`；身份错误、关键输出损坏、实际状态无法辨明或核心比较无可靠证据→blocked。不能把后一类通过“诊断收尾”自动豁免。

## 7. C2：执行 7 个已批准条件

**负责人：simulation_engineer；data_analyst 在首项后确认输出可分析。**

现有合法命令模板如下，实际用矩阵数值替换，逐项执行并保存 stdout/stderr：

```text
.venv/bin/python src/scenarios/run_minimal_uncontrolled.py \
  --profile low --q-main 3200 --q-ramp 720 --seed 23 \
  --warmup-s 0 --measurement-duration-s 1500 \
  --demand-end-s 1500 --post-demand-clearance-s 1200
```

1. 启动前核对本项参数、剩余预算、代码/源配置 hash。保存当前 `/private/tmp/minimal_uncontrolled_*` 完整目录集合及开始时间，台账写 running，再执行。这里的集合用于精确差集恢复，不是“挑最新目录”；不删除或读取无关目录内容。
2. 使用 runner 返回的唯一新 `/private/tmp/minimal_uncontrolled_*` 目录，立即登记；不得从模糊“最新目录”推断本项身份。不得直接重用旧 sumocfg 运行，避免写回旧输出。若执行中断且实际启动状态不明，标记 unknown 并核对保存日志/进程和候选目录的命令、时间、参数；不能以“没有看到完成消息”认定没跑。无法排除已启动时按占用一个预算处理，不重跑来解决不确定性。
   stdout 未给出目录时，计算本项前后目录集合差集。仅差集唯一且 summary/生成需求/seed/窗口/时间核对一致，才绑定本项；多个候选即暂停而非选最新。没有候选或 summary 未写完时先核对进程和保存日志，不重新执行命令。不能检查进程时如实保留启动状态不明及已预留预算。
3. 记录实际 SUMO 启动、退出码、版本、命令和全部日志；分开判断 runner 退出状态与文件是否可分析。旧技术阈值失败不等于仿真输出坏。
4. 检查生成需求/seed/三时长、compiled topology、6 个 E1 各 90 个连续区间 `[0,2700)`（完整运行共 540 行，ID/lane/区间唯一键先核验）、E2 命名车道覆盖及主要输出结构；不改 detector 布置。运行内参数与登记不符，隔离本项并停止后续启动。每项结束（包括失败）立即按 C0 的逐文件 hash/路径映射合同独占归档；不能因失败删掉半成品输出或重写其内容。
5. C23 后运行一次新入口，确认 schema、已观察车辆状态与新内部 E1 聚合可核对。不是要求 seed23 复制 seed17 交通。
6. 首项合同有效后继续剩余 6 项，不逐项请求用户确认；每项落账。新结果令人意外但数据有效则继续，不能挑结果停止。
7. 缺文件/损坏 XML/异常版本属于技术问题，先定位；至多使用全包唯一重试。若修复需要改变交通配置或预算，停在边界，不代替用户决定。
8. collision、teleport、路线错误等影响车辆守恒的异常不能被“退出 0”掩盖；暂停新启动交工程和科学审查，保留已跑结果，不自动过滤。普通 warning 逐项评估，不能以任何 warning 自动要求重跑。

**出口：**全部条目均有状态。正常路线为 8 个可审计记录；若预算内无法取得核心比较，C6 可以交阻塞包，但不得声称 Stage 2 已完成。

## 8. C3：统一汇总、三时长诊断和单因素比较

**负责人：data_analyst。只读取登记原始输出，写新派生目录。**

### 8.1 固定窗口与测量

- Full `[0,2700)`、A `[0,1500)`、B `[300,1500)`、Post `[1500,2700)`；B 只是同轨迹敏感性切窗，不是独立运行，不删去总体中较早出发车辆。
- 六 E1 保留原 30 s 区间。新内部两 E1 用于 M-only 聚合通过；流量按平行车道相加，速度按贡献加权，占有率逐车道保留。零贡献速度缺值；有贡献负速度单列异常。
- 旧 upstream 两 E1 始终标记 insertion contamination，不进入主线拥堵诊断。下游 E1 保留换道/孤立过车限制，单个低速度值不是 Breakdown。
- FCD 包含相关外部/内部车道，沿用既有 speed≤0.1 m/s 技术停驶描述，不新增拥堵、有效储存或持续性阈值。零停驶样本不证明无拥堵。
- R 合流用相邻 FCD 的首次下游观测括号；首次即在下游、缺帧、路径不符、重复事件单列。跨 30 s 箱界的事件保留歧义，不强行输出精确箱流量。总入网、合流贡献、到达属于不同事件，不要求同窗计数相等。
- `departPos=last` 可使主线车辆在 main_up 末端插入；不得把长 upstream edge 当已验证的真实上游发展/排队区。更改插入位置或几何不属于本轮。

### 8.2 每项必须回答的时长问题

| 问题 | 机械报告规则 |
| --- | --- |
| 0 s 是否可以保留？ | 明确本轮研究空网加载全过程；另列 A/B 差异，不称选出了稳态预热 |
| 1500 s 够不够？ | 报需求期内累计实际插入、通过、积压时序及期末状态；只评价本次有限时域能回答的问题；不能证明更久不会出现新行为 |
| 1200 s 是否完成清空？ | 同时核查网外、网内、未知及最后实际入网/到达；全部已核验完成才写 complete，否则 censored 或 unknown |
| Post 能否称恢复？ | 先报告 post 仍实际入网数量；有延迟入网时不能称零入流恢复实验 |
| 下一步是否沿用？ | 给出“本轮描述适用/完整车辆结果受限/未核验”的分项结论；未来时长仍 Proposed，不反推最优秒数 |

时间线固定用 0..2700 的 30 s 网格，必要增加有来源的事件时点；网外排程未核验则该列缺值并解释，可展示已确认的实际累计入网/到达和未知数。不给 Unknown 画伪精确连续曲线。

### 8.3 有限产物与比较解释

必需表：`vehicle_accounting.csv`、`cohort_timeline.csv`、`e1_native.csv`、`run_window_summary.csv`、`merge_events.csv`（不可可靠识别时保留表结构和原因，不填造事件）。manifest/审计/比较放 processed；含失败与缺失记录的覆盖表必须存在，可并入 run audit。

至多两张图：①按条件/seed 分面的内部及下游 E1 完整时序；②R/U 网内与经核验的网外积压时序。维持统一坐标与缺值标记，不新做动画、热图或交互平台。

若逐时排程未核验，第二图改画 R/U 累计实际入网与累计到达，另标 1500/2700 可核验的边界数量或 Unknown；图题不得称网外等待曲线。无法可靠识别 R 事件时，审计必须写 `not_measured` 及原因，schema-only 表不意味着零事件。

对每一组同 seed 差值同时给基准值、处理值、差值、单位和分母。仅描述该合成场景中单因素干预对应的响应；不从匝道需求下降推出“纯信号容量”或“纯合流原因”。主线实际输入没实现时，必须同时展示请求量和实现量，不能按请求量给容量点命名。

## 9. C4：独立核验与最终科学审查

**顺序：data_analyst 独立核算证据 → scientific_reviewer 审查 → 主代理协调一轮集中修订。**

1. 每运行直接读取原始 XML，对新内部 E1 全部区间的 ID、时间、贡献、进入量、速度、占有率及流量核对；独立重算 A/B/Full/Post。不能调用同一个加权函数两次冒充独立核验。
2. 对原 tripinfo/vehroute 独立核对总量和 M/R/U/X；有可靠计划身份时对账完整 ID 集；所有未知、重复、未完成和确认未入网类别都检查。抽样核查边界车辆与 FCD 记录，不声称逐车 E1 完整性已验证。
3. 核查每点两个 seed、单因素参数差异、实际启动次数/失败/重试、源 hash 不变和派生 manifest；复用 C17 不算新 seed。
4. reviewer 对五项测量检查分别给 passed/failed/not_verified；审核新窗口比较、截尾、seed 限制、三时长说明及每个研究句子是否有证据。
5. 将所有 Blocker/Major 一次集中修订，限离线分析/文档；不自动触发额外运行或研究改参。修订后复核受影响项目。
6. 仍有实质问题则交 C6 阻塞包；可选改进和已清楚限制的普通 E1 无 vehID 不能成为无限返工理由。不要把审查意见多数票当科学决定。

**出口：**没有未解决的、影响所提交结论的 Blocker/Major；或已清楚标记无法验收的具体阻塞及最小恢复条件。小样本、有限时域、无正式容量结论本身不是失败。

## 10. C5：撰写最终收尾报告

**负责人：主代理，引用代理的实际验证，不自行虚构通过。**

`docs/STAGE2_COMPLETION_REPORT.md` 必须包含：

1. 一页通俗结论：已完成什么、五个问题的答案、哪些不知道。
2. 8 条逻辑记录及实际新启动/失败/重试清单、输入和产物索引。
3. 同 seed 单因素比较和两 seed 方向一致/不一致，显式列异常及截尾。
4. 0/1500/1200 三段各自的适用性，不写“时长已科学验证并冻结”。
5. 当前观测的空间、cohort、时间限制；主线起点插入与内部 E1 逐车未知尤其要保留。
6. 科学审查五项结果、问题处理表、未解决限制和置信度。
7. `next_step_readiness` 及理由；只给一个优先下一步建议，至多三条有证据的导师确认问题。没有观测到现象时可建议有目标的几何/合流/需求检查，禁止立即实施。
8. 下列 G2 清单，每项指向证据；`stage2_acceptance=pending_user`。

### G2 验收清单

- [ ] 当前已完成测量成果被正确复用，未用旧污染 E1 做主线结论。
- [ ] 8 条记录身份明确；失败/缺失不隐去；预算可独立对账。
- [ ] 本轮核心单因素问题有可靠比较，或有被明确接受范围内的有证据诊断答案；单纯丢失关键数据不能代替答案。
- [ ] 计划需求、实际入网、合流通过、到达、网内/网外/未知严格区分。
- [ ] 有效窗口与截尾限制明示，时长没有被误报为稳态或正式选择。
- [ ] 两 seed 如实展示，未冒充统计稳健性或完整需求空间。
- [ ] 所提交结论通过实际独立核验和科学审查，实质问题已关闭。
- [ ] 原始来源可读、hash 和分析入口足以重算本包；关键文件丢失时验收受阻。
- [ ] 完成报告、PROJECT_STATE、WORKLOG 一致；正式协议/决策/导师记录不被擅自改变。
- [ ] 用户明确接受 Stage 2 本轮诊断收尾及下一步去向。

前九项完成后才提交最后一项。报告可称“Stage 2 执行与审查完成，等待 G2 用户验收”；不能提前写整个 Stage 2 accepted。

## 11. C6：用户验收与终点

提交一份集中确认包，明确建议接受或暂不接受、证据、限制及下一步。无需在 C0–C5 的已授权范围内反复确认。G2 是用户此前就要求保留的里程碑验收，不是新增的权限障碍。

用户接受后：最小更新 PROJECT_STATE 的阶段完成和下一步、WORKLOG 的实际验收原话/范围，以及报告 `stage2_acceptance=accepted`。不自动冻结 protocol、改 DECISIONS、运行 ALINEA 或开始新网格。存在方向问题时，Stage 2 可以作为完整的诊断包被用户接受，下一步仍为 `requires_specific_decision`。

若关键输入损坏、核心比较无可靠数据、预算用完而技术阻塞仍在、或实际科学审查未完成：写 `blocked` 并列出最小恢复动作和所需权限，不伪称已完成；不偷偷追加运行。导师未回信不是这个包的技术阻塞，不自动发送任何邮件。

## 12. 给 Sol medium 的总指令

> 阅读 AGENTS、PROJECT_STATE 和 docs/STAGE2_COMPLETION_PLAN.md，检查用户是否已经明确批准该方案的 C0–C6、矩阵、预算和验收边界。未批准时只说明尚待批准；不得从模型切换推断仿真授权。
>
> 获批后，按 C0→C1→C2→C3→C4→C5 顺序自主完成，维护台账，从最早未完成步骤接续。按 AGENTS 使用 simulation_engineer、data_analyst、scientific_reviewer，每个代理先做 Context Preflight；主代理协调文件所有权，不代替科学审查做研究决定。
>
> 复用 C17，仅运行清单内 7 个新条件，全包最多 1 次符合规定的同参技术重试、新 SUMO 启动硬上限 8。保留 dirty worktree 和全部来源。不得为获得 Breakdown、清空或显著性而加跑、改参、换seed。分析纯离线，缺失和不确定性显式记录。
>
> 完成离线适配与首项验证后继续已批准矩阵，不每步索取确认。遇到真正超范围变化或实质阻塞时提交具体差异，继续不受影响的文档工作。最终提交 C6/G2 验收包并等待用户接受；不要自行宣布 Stage2全部完成或启动后续阶段。

Sol medium 可负责调度和受约束实现；方案把关键研究判断交给专业代理并设置可核查出口。**不能保证任何模型“完美执行”**。执行可行性置信度 Moderate；最终是否通过以文件、原始数据、测试和独立审查为依据。

## 13. 方案审查与来源

以下为方案编制时的历史审查记录；其中 Proposed 和 not_verified 描述当时状态。后续 C0–C5 已获用户授权并完成，C6/G2 已获用户验收；当前状态以页首、执行台账和完成报告为准。

编制依据：PROJECT_STATE、DECISIONS D-001–004、STAGE2_EXECUTION_PLAN、STAGE2_S3_S5_VALIDATION_REPORT、当前 runner/analysis 代码；导师意图依据 SUPERVISOR_FEEDBACK 和 `docs/supervision/2026-08-25_robert_hilbrich_reply.md` 原文。Robert 支持简单场景、无控制探索和插入检查，没有批准本矩阵、时长或 seed。

simulation_engineer：只读核查执行入口、输出和预算，确认不需重构 runner；其目录身份恢复、原子归档和窄忽略规则建议已纳入。data_analyst：只读设计排程/截尾/测量合同；其四类资格、终点聚合许可、路径解析、图表降级和版本安排已纳入。

scientific_reviewer 已全文审查并核对最终补丁：没有 Blocker/Major，此前要求明确核心证据底线的 Minor 已关闭，没有剩余必须修改项。五项测量检查的**方案合同均充分**；未来运行、分析结果、归档实现及实际测量五项检查仍全部 `not_verified`，本次审查不能代替 C1/C4 的执行验证。方案合同清晰性置信度 High，未来执行与数据适用性 Moderate。

归档建议中的分歧已协调：不用工程初议的 `data/raw/` 新写入，采用本方案明确提出的新 artifacts 目录，保持用户原始数据只读边界；warning 依实际影响审查，不以任意 warning 自动重跑。主代理已完成文档影响检查，只更新本方案、原 Stage2 路线、PROJECT_STATE 和 WORKLOG；未执行仿真或实现新分析代码。所有新参数与完成规则仍为 Proposed，待用户集中批准。

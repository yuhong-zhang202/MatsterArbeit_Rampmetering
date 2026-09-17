# 论文项目记忆增量更新教程

日期：2026-09-09。适用项目：`Masterarbeit-Ramp-Metering`。

本文说明现有正式 Tencent MemoryCore L0–L3 种子如何在项目里程碑后更新。它不是本次资料上传或模型调用授权。

截至 2026-09-09，增量更新器和本地安全门已经实现，但没有执行任何正式增量更新。正式记忆仍保持首次导入时的内容；只有用户明确说“更新腾讯记忆”后，才制作本次增量包和 L3 候选，再单独取得付费执行批准。

## 一、什么时候更新

长期记忆应按里程碑更新，不应在每次仿真、每个子任务或每个聊天窗口结束后更新。

是否值得更新不由聊天长度或任务自动触发。只有用户明确要求更新，并且下列条件同时满足后才执行：

1. `docs/PROJECT_STATE.md` 已写入经核对的最新阶段状态；
2. Stage 2 的交付报告、工程验证和科学审查已经完成，主要问题已处理；
3. `docs/DECISIONS.md`、`docs/SUPERVISOR_FEEDBACK.md` 等权威文件如有变化，已先正确更新；
4. 用户明确批准本次发送给 OpenAI 的两个文件、各自 SHA-256、模型、请求上限和本轮调用预算；
5. 待发送内容不含 API Key、账号、私人聊天、无关项目或未经授权的数据。

适合触发更新的其他情况包括：导师给出新的明确意见、研究阶段正式切换、重要决定被用户批准、旧结论被证据推翻，以及准备切换到长期新任务之前。

## 二、为什么不能重跑首次导入器

现有 `scripts/memory/run_formal_memory_import.mjs` 是一次性首次导入器。它会检查正式项目身份是否为空，并拒绝覆盖已有记忆。

后续更新必须使用独立的增量更新器。不能通过更换 volume、service ID 或 team/agent/user 来绕过非空检查；那会创建另一个互不相通的实例，而不是更新现有项目记忆。

## 三、先更新权威项目文档

记忆是辅助层，不是事实源。正确顺序是：

```text
完成和核验项目工作
  → 更新 PROJECT_STATE / WORKLOG / 相关权威报告
  → 必要时按审批规则更新 DECISIONS 或 SUPERVISOR_FEEDBACK
  → 生成记忆增量包
  → 更新 L0–L3
```

不得先让模型“总结项目”，再反过来用模型总结修改权威文档。

## 四、制作只包含变化的增量包

创建带日期的文件，例如：

```text
docs/memory/incremental_update_YYYYMMDD.md
```

只记录上次正式种子之后的变化：

- 新完成的里程碑；
- 新增或改变的决定及准确审批等级；
- 新的明确导师意见；
- 被推翻、取代或已经过时的旧状态；
- 新验证的技术事实及其证据边界；
- 当前阻断、未决问题和唯一下一步；
- 每个来源文件的路径与 SHA-256。

每条信息必须区分：

```text
observed
calculated
proposed
user-approved
supervisor-confirmed
frozen
unknown
```

不要再次发送整个 `PROJECT_STATE.md` 和旧种子。重复全文会制造重复 L1、相互竞争的 L2 场景和更大的 L3 合并请求。

## 五、固定正式身份

所有更新必须继续使用：

```text
volume: tdai-ramp-metering-memory-v1
service_id: ramp-metering-formal-memory-v1
team_id: team-masterarbeit-ramp-metering
agent_id: agent-project-memory
user_id: user-yuhong-zhang
```

任一字段改变都可能形成另一套隔离记忆。

每次更新使用唯一 `session_id`，例如：

```text
stage2-milestone-202609XX-v1
```

增量更新器必须先查询该 session 是否已经存在；若存在，应拒绝重复追加，而不是再次计费和生成重复记忆。

## 六、L0、L1、L2、L3分别如何更新

### L0

追加经审核的增量包原文。历史 L0保持不可变，不重写、不删除。

### L1

让 MemoryCore 从本次增量会话提取新的原子记忆。必须逐条读取正文，检查：

- 是否把待确认写成已批准；
- 是否把技术测试写成论文证据；
- 是否捏造时间、因果关系或精确数字；
- 是否遗漏本次更新的核心变化。

`total > 0` 只证明有记录，不证明记录正确。

### L2

检查新场景是否正确整合了工作过程，尤其注意：

- 是否无意覆盖关键旧场景；
- 是否生成内容近似的重复场景；
- 是否把不同证据范围混在一起；
- 是否把探索性结果升级成正式结论。

### L3

L3代表当前核心项目状态，不能只在旧正文末尾追加。

正确流程：

1. 通过 `core/read` 读取现有 L3；
2. 对照最新权威文档和增量包生成完整候选版本；
3. 展示旧版与新版的实质变化；
4. 清除或明确标记已经过时的状态；
5. 经审核后通过 `core/write` 整体写回；
6. 不把人工审核的 L3冒充 GPT 自动生成。

首次接入已经发现，L2 工具续轮可能超过 20,000 字节门。不得静默提高请求上限。自动 L3无法可靠完成时，继续使用“GPT 辅助 L1/L2＋经审核的确定性 L3”。

## 七、模型、预算与 Key

- 使用实际验证可见的模型别名 `gpt-4.1-mini`；更新前先做无文本生成的模型可见性检查。
- 现有总账已经记录 6/41 次尝试，剩余 35 次；不得重置旧账本伪造预算。
- 先测量增量包及实际请求体大小，再提出本轮最大调用数和费用上界。
- 用户批准前不得发送真实项目内容。
- Key 只从 macOS 钥匙串读取，不写入聊天、命令参数、仓库、Docker长期环境、日志或回执。
- 不使用已经实测会截断长值的 `security ... -w` 交互保存方式；通过“钥匙串访问”图形界面维护完整 Key。

## 八、验收与文档

联网提取结束后立即停止预算代理。随后用全新的 `--network none` 容器重新打开持久卷并验证：

- L0新增数量及 session 唯一性；
- L1逐条正文和审批状态；
- L2场景内容及旧场景保留情况；
- L3是否包含最新阶段并正确处理旧状态；
- 错误项目身份是否返回空；
- 账本请求数、HTTP状态、token和费用是否与最终回执一致；
- 容器和联网代理是否完全停止。

最后更新 `docs/memory/` 下的增量证据与回执、`docs/PROJECT_STATE.md`、`docs/WORKLOG.md`，读取方式变化时再更新 `README.md`。不要为了让记忆一致而修改研究决定、导师反馈或实验协议。

## 九、已实现的手动执行入口

正式入口是：

```bash
node scripts/memory/run_incremental_memory_update.mjs \
  --approval docs/memory/<本次已批准清单>.json \
  --dry-run
```

`--dry-run` 只验证审批状态、路径、文件哈希、敏感信息扫描、历史账本和本轮调用上限；它不会读取钥匙串、启动 Docker、联网、调用模型或写记忆。示例结构见 `docs/memory/incremental_update_approval_TEMPLATE.json`。模板的状态故意是 `template-not-approved`，不能直接执行。

只获准制作候选和干跑时，清单使用 `dry-run-authorized`。执行器仅在带 `--dry-run` 时接受该状态；去掉参数会拒绝运行。真正付费执行仍必须依据后续明确授权将同一最终哈希清单改为 `user-approved`，并记录新的批准时间和原话。

干跑结果展示给用户并取得对同一份哈希清单的明确付费执行批准后，才允许去掉 `--dry-run`：

```bash
node scripts/memory/run_incremental_memory_update.mjs \
  --approval docs/memory/<本次已批准清单>.json
```

执行器沿用固定 volume、service/team/agent/user 和历史账本；额外施加本轮 `max_new_attempts` 上限。它拒绝重复 receipt 和重复 session，追加 L0，等待 L1/L2 确实发生变化，再写入完整的经审核 L3。联网代理随后停止，新的断网容器重新读取全部层并核对 L3。每次执行在独立的 `data/processed/memory_incremental_<update_id>/receipt.json` 留下账本、token、费用、哈希和失败信息。

安全边界：自动生成审批清单、自动把模板改成 `user-approved`、自动准备里程碑增量、自动调用 API 和自动更新每次普通对话都不属于该入口。

## 十、给论文项目 Codex 的可复制指令

```text
请为 Masterarbeit-Ramp-Metering 准备一次里程碑式增量记忆更新。先完整遵守 AGENTS.md，并读取 docs/PROJECT_STATE.md、docs/DECISIONS.md、docs/SUPERVISOR_FEEDBACK.md、docs/memory/FORMAL_PROJECT_MEMORY_20260909.md，以及本次 Stage 2 的最终权威报告。不要运行新的 SUMO 仿真，不改变研究设计或实验协议。

先判断 Stage 2 是否真的达到可记录里程碑；如果仍是“差不多完成”，只列出缺口，不上传。若已达到里程碑，生成一份只包含上次正式种子之后变化的增量包，列明来源路径和 SHA-256，严格区分 observed / calculated / proposed / user-approved / supervisor-confirmed / frozen / unknown。检查并排除密钥、账号、私人聊天及未授权文件。

随后提出：本次文件清单、字节数、固定 MemoryCore 身份、唯一 session_id、gpt-4.1-mini 可见性、单请求上限、最多模型调用次数和最坏费用。得到我的明确批准后，才实现或执行增量更新器。沿用 tdai-ramp-metering-memory-v1、ramp-metering-formal-memory-v1 和既有 team/agent/user；不得重置历史账本、修改身份或重复初始导入。

更新 L0 后逐条审查 L1，核对 L2，并以 core/read → 完整差异审查 → core/write 更新 L3。最后关闭联网代理，用全新断网容器完整召回 L1/L2/L3，记录层数、哈希、实际 token、费用、失败和限制。当前仓库文件始终比记忆权威。
```

## 十一、当前最安全的下一步

平时不做任何记忆更新。需要时，用户先明确说“更新腾讯记忆”；Codex 再根据当时的权威文件制作增量包和完整 L3 候选，并提交文件哈希、模型、本轮最多调用次数和费用上界。只有再次明确批准后才执行。当前工具已就绪，但正式记忆仍未更新。

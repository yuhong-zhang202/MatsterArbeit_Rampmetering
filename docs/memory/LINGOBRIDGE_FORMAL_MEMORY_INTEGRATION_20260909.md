# LingoBridge 正式项目记忆接入教程

日期：2026-09-09。目标项目：`/Users/yuhongzhang/Desktop/LingoBridge`。

本文供 LingoBridge 项目的 Codex执行。它不是外部模型调用、真实资料上传、Key读取或项目文件修改授权。Codex 应先完成只读预检并提交授权包，得到用户明确批准后才能正式导入。

## 一、当前状态

LingoBridge 并非完全没有接入记忆。现有项目已经具备：

- Colima环境 `memory-pilot`；
- 固定 MemoryCore 镜像 `sha256:9798254a8cc06276b7c5b3c19df49f136fae25d579564e1f01f9c4b9b8cd2d11`；
- 旧快照卷 `tdai-project-snapshot-20260905`；
- 项目级 MCP `lingobridge_memory`；
- 零参数工具 `read_project_memory`；
- 已验证的旧快照读取及 SHA检查。

尚未完成的是正式项目隔离的 L0/L1/L2/L3实例、当前状态导入、增量更新、MCP迁移和新 Codex任务实际加载验收。旧快照含有已被后续决定覆盖的状态，应保留为历史证据，但不能继续冒充实时状态。

## 二、目标架构

```text
LingoBridge 权威项目文档
  └─ 经审核、去敏、带来源哈希的项目简报
       ├─ L0：简报原文
       ├─ L1：GPT 原子记忆（辅助）
       ├─ L2：工作场景／方法记忆（辅助）
       └─ L3：经审核的核心项目状态（主要接续入口）

新 LingoBridge Codex 任务
  └─ 项目级 lingobridge_memory MCP
       └─ 断网读取固定正式身份的 L1/L2/L3
            └─ 再读取 Project_State.md 和相关权威原文校正
```

现有真实 L1 Probe 已证明自动摘要会遗漏批准背景和关键边界。因此 GPT只负责辅助提取 L1/L2，L3建议使用经审核的完整核心状态，通过 MemoryCore 官方 `core/write` 保存。

## 三、项目隔离与凭证

不能复用论文项目的卷、service ID、team/agent/user、预算账本或 Keychain项目。建议固定：

```text
volume: tdai-lingobridge-memory-v1
service_id: lingobridge-formal-memory-v1
team_id: team-lingobridge
agent_id: agent-lingobridge-project-memory
user_id: user-yuhong-zhang
Keychain account: lingobridge-memory
Keychain service: openai-api-key-lingobridge-memory
```

service ID也是 MemoryCore 的实际隔离维度。导入器和读取器若使用不同 service ID，会出现“卷存在但记忆为空”的假象。

建议在 OpenAI Platform 为 LingoBridge 建立独立项目和项目 Key。不要让用户把 Key贴入聊天。使用 macOS“钥匙串访问”图形界面保存完整 Key；不要使用本机已经证明会截断长值的 `security ... -w` 交互保存命令。

## 四、阶段 A：只读预检

Codex 首先必须：

1. 完整读取 LingoBridge `AGENTS.md`；
2. 读取 `Project_State.md` 最新接续；
3. 完整读取 `outputs/tencent-memory-pilot-preflight-2026-09-05.md` 的最新结论和历史限制；
4. 读取 `scripts/memory/tencent-readonly.mjs`、测试和 `.codex/config.toml`；
5. 检查 Git状态并保护现有未提交改动；
6. 核实 `memory-pilot`、固定镜像、旧卷和 MCP实际状态；
7. 不调用模型、不读取 Key、不修改生产、不扫描全聊天。

问题分类是 Engineering＋Security/Privacy＋Product handoff，不触碰业务 AI prompt、Gold、生产数据库、训练或部署。

按 LingoBridge `AGENTS.md` 路由：`security-auditor`只读审查边界；合适的架构角色检查重复建设和身份设计；用户批准后才由 `fix-engineer`实施；最终由 `qa-engineer`验证异常与重启。不要让通用 agent独立决定产品或安全边界。

## 五、阶段 B：冻结导入范围

候选来源应来自当前权威文件，例如：

- `Project_State.md` 最新接续；
- `docs/PRODUCT_INVARIANTS.md`；
- 当前 No Match／Ranking 唯一主记录；
- 已批准台账及原始证据；
- 当前版本、部署、业务阶段和唯一下一步的权威来源；
- 真正需要跨任务保留的稳定协作规则。

默认排除真实用户故事全文、邮箱、账号、Key、数据库导出、生产日志、整段聊天、已被替代的旧交接稿、未经真人批准的 draft Gold以及其他项目资料。

生成 `docs/memory/formal_import_bundle_YYYYMMDD.md`，列明每个来源的路径、SHA-256、摘录理由、审批状态和排除内容。每条 L0消息不得超过 MemoryCore 的8192字符限制；需要时按段落拆分并保持同一 session。

## 六、阶段 C：提交授权包

任何付费调用前，Codex必须报告：

- 将发送给 OpenAI 的确切资料和内容摘要；
- 总字节数和 L0分片数；
- 模型别名及无文本生成可见性；
- 单请求字节和单次输出 token上限；
- 最大模型调用次数和费用上界；
- volume、service/team/agent/user；
- L3生成方案；
- 失败后保留策略；
- session重复检测和恢复办法。

用户明确批准前不得读取 LingoBridge Key 或发送真实资料。不能继承论文项目的41次授权或历史 Manifest。

## 七、阶段 D：实现与正式导入

可以参考论文项目的架构经验，但不能复用硬编码路径和身份。

必须满足：

1. 先用假模型和临时卷验证 L0→L3及预算门；假语义不能作为质量通过。
2. 使用独立持久账本，在转发请求前登记 attempt。
3. 拒绝超字节、超输出、模型不匹配、并发代理和账本策略漂移。
4. 正式卷已存在时不得静默覆盖。
5. 同一 session已存在时不得重复导入。
6. Key只在宿主预算代理进程内存在，不进入容器、日志、账本和仓库。
7. 使用实际验证可见的模型别名，不默认快照 ID可用。
8. L0保存完整审核简报，L1/L2作为辅助提取。
9. L3优先采用完整审核核心状态，通过 `core/write`写入。
10. 首次写入前确认没有正式 L3；后续更新必须先 `core/read`并审查完整差异。

正式导入后逐条阅读 L1正文，重点检查批准状态、数字、时间、线上状态和唯一下一步。不能以 `total > 0` 代替内容验收。

## 八、阶段 E：断网持久化与隔离验收

提取结束后关闭联网预算代理，再用全新 `--network none` 容器验证：

- L0、L1、L2、L3均可读；
- 核心状态和审批边界正确；
- 错误 team/agent/user返回空；
- 错误 service ID不会被误判为正式实例；
- 重启后哈希和数量稳定；
- 账本 HTTP状态、token和费用与回执一致；
- 没有遗留联网代理或导入容器。

最终回执记录来源、身份、层数、哈希、模型、调用数、token、费用、失败、隔离结果和限制。

## 九、阶段 F：升级现有 MCP

不要先删除旧快照或直接覆盖现有读取器。先让正式读取脚本独立通过测试和安全审查，再升级 `lingobridge_memory`，最后在新的 LingoBridge Codex任务中实际调用。

MCP要求：

- 可继续保留工具名 `read_project_memory`；
- 固定 volume、service/team/agent/user，不接受外部路径或身份参数；
- Docker禁网、禁止拉镜像、禁止创建卷、禁止模型调用；
- 返回正式 L3，并可附带有界 L1/L2内容；
- 始终说明记忆日期、来源和 `Project_State.md` 更权威；
- 旧快照保留为显式历史回退，正式读取失败时不能静默返回旧快照冒充最新；
- 限制响应大小、超时和并发；
- 测试缺卷、错SHA／身份、超大响应、恶意参数、并发和 Docker失败。

新任务至少核对当前线上版本、业务阶段、批准／draft边界、唯一下一步和已过时状态。

## 十、文档维护

完成后按 LingoBridge 自己的规则更新 `Project_State.md`、`AGENTS.md`记忆说明、正式接入证据、README或使用文档、MCP测试和安全审计证据。需要写 `DISCUSSION_LOG.md` 时遵守 `recorder` 的唯一写权限。

## 十一、给 LingoBridge Codex 的可复制总指令

```text
你正在 /Users/yuhongzhang/Desktop/LingoBridge 工作。目标是在现有固定快照＋lingobridge_memory MCP 的基础上，正式接入项目隔离的腾讯 MemoryCore L0/L1/L2/L3，并让新 Codex 任务可读取；不是重新建设另一套互相冲突的记忆，也不是导入全部聊天。

先完整遵守本项目 AGENTS.md。完整读取 Project_State.md 的最新接续、outputs/tencent-memory-pilot-preflight-2026-09-05.md、scripts/memory/tencent-readonly.mjs、对应测试和 .codex/config.toml；检查 Git状态。明确当前已有旧快照卷 tdai-project-snapshot-20260905 和 read_project_memory，只缺正式分层、增量更新及新任务验收。旧快照必须保留为历史证据，不得覆盖或冒充实时状态。

先做只读设计，不调用外部模型、不读取 Key、不修改生产、不扫描全聊天。按 AGENTS.md 路由 security-auditor、合适的架构角色、fix-engineer和qa-engineer。提出独立身份：tdai-lingobridge-memory-v1、lingobridge-formal-memory-v1、team-lingobridge、agent-lingobridge-project-memory、user-yuhong-zhang；不得复用论文项目身份、账本或 Keychain项目。

从当前权威资料制作一份紧凑、去敏、带来源 SHA的正式导入包。优先使用 Project_State.md最新接续、PRODUCT_INVARIANTS、当前 No Match／Ranking唯一主记录和已批准台账；排除真实用户正文、邮箱、账号、密钥、数据库导出、生产日志、整段聊天、旧交接稿和未批准 draft。明确哪些事实是已批准、已上线、提案、争议、历史或未知。

先向我提交授权包：文件清单、字节数、L0分片、模型可见性、固定身份、单请求与输出上限、最大调用数、最坏费用、失败恢复和 L3方案。没有我的明确批准，不得上传真实资料或读取 LingoBridge API Key。建议在 OpenAI Platform创建 LingoBridge独立项目 Key，并通过 macOS“钥匙串访问”图形界面保存到 account=lingobridge-memory、service=openai-api-key-lingobridge-memory；不要让我把 Key发到聊天框，也不要使用已证明会截断长值的 security ... -w交互保存命令。

批准后再由 fix-engineer做最小实现：GPT辅助生成 L1/L2，经审核的完整核心状态通过 MemoryCore core/write写入 L3。所有调用经过持久预算门；导入器必须幂等，现有卷或 session不得静默覆盖。真实导入后逐条核对正文和审批状态，停止联网代理，再用全新断网容器完整召回并执行错误身份隔离查询。

最后在不删除旧快照的前提下升级现有 lingobridge_memory MCP，使 read_project_memory固定、无参数、断网读取新的正式身份；失败时明确报错，不能静默回退成过时快照。运行项目级测试、安全审计和一次真正的新 Codex任务读取。更新 Project_State.md、AGENTS.md中的记忆说明、预检证据、README或使用文档，并报告实际层数、哈希、token、费用、失败和限制。不要宣称自动增量更新或完整聊天迁移，除非它们另行实现并真实验证。
```

## 十二、停止边界

第一次交给 LingoBridge Codex 后，它应停在“只读预检＋授权包”，不得直接执行真实导入。用户审核资料范围、预算、身份和 L3方案并明确批准后，才进入实施。

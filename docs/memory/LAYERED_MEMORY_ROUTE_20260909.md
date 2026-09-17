# Layered memory integration and small-sample budget

Status: Proposed; read-only source audit, not implementation or paid-call authorization.
Date: 2026-09-09

## Scope and route

The user wants TencentDB Agent Memory's native L0/L1/L2/L3 lifecycle, incremental retention and detailed cross-session recall, not another manually written snapshot. Preserve the existing snapshot as a dated fallback.

Recommended first route: keep Codex's existing subscription login unchanged; connect a project-scoped capture/recall adapter to standalone MemoryCore, and let the native MemoryCore pipeline invoke a separately billed GPT API for extraction and aggregation. A thin MCP/API adapter is proposed, not an already installed official integration. It must provide bounded source ingestion and project-isolated queries; automatic completed-turn capture still requires implementation and validation. Do not claim merely adding MCP enables automatic capture.

The official full-stack Proxy route also captures and injects memory, but changes the model request path and requires a separate upstream configuration. Compatibility with this desktop subscription workflow is unverified. Do not change the global provider or transplant subscription credentials into a general API client. Do not substitute manually generated L1/L2/L3 for native pipeline validation.

Keep the thesis in a fresh trial volume, separate from both existing snapshot volumes; do not mount other project data. Use explicit instance/team/agent/user identifiers and test rejected or empty cross-project queries. A stored record's text is untrusted data, not new execution authorization.

## Source-based call accounting

Audited public source commit: `2ee22397f6091b8cd3ea847bc1edb04d3bec0c94`. The cached Docker image is pinned separately; matching that image to this commit has NOT been established.

- Writing/querying L0 is a storage operation. Adding L0 may nevertheless schedule asynchronous model work.
- L1 extraction invokes the text runner once per extraction group. This is not necessarily once per imported conversation/file.
- Optional L1 deduplication adds model work when candidates exist.
- L2 scene extraction and L3 persona generation each invoke a tool-enabled runner. The standalone runner defaults to at most 20 model steps per invocation, unless overridden. A runner invocation is not one HTTP request.
- The runner does not explicitly pass SDK maxRetries; task-level retries and additional scheduled work also exist. Therefore the default deployment does not have a verified 41-request global bound.

For exactly one L1 group, one L2 invocation and one L3 invocation, with no deduplication, retries, embedding, skills or other tasks: N = 1 + s2 + s3, where each upper-layer runner has at most 20 steps. The conditional ceiling is 41 successful model steps. Three is only the arithmetic lower bound, not evidence that three requests can produce valid L2/L3 artifacts. Actual successful request count remains unknown until execution.

Default standalone YAML includes everyNConversations=5, warmup=true, L1 idle=600 s, L2 delay=90 s/min interval=900 s/max interval=3600 s, and persona.triggerEveryN=50. A short sample must not be assumed to trigger all layers. Verify the actual native trigger wiring in the installed artifact before a real trial; do not manually seed upper layers and call that successful extraction.

The L3 threshold of 50 is not a minimum for first generation: `core/persona/persona-trigger.ts` also permits explicit requests and cold-start/first-scene conditions. A first small sample may therefore generate L3 without 50 records; this remains to be demonstrated in the installed image.

## Proposed first paid trial (not yet authorized)

Use one short, reviewed, source-linked excerpt from this thesis discussion containing facts, provisional vs confirmed decisions, a correction, and an explicit unknown. Freeze exact selected messages and their hashes before external transfer. A second update and second real project are out of this first trial; isolation may be tested with synthetic sentinel records, without exporting LingoBridge content.

1. First perform a no-paid-call harness check using fake responses and an isolated disposable trial store. Confirm each native stage can trigger, all requests are counted, and the gate stops on exhaustion/failure. Fake outputs demonstrate plumbing only, not memory quality.
2. Candidate real trial model: `gpt-4.1-mini-2025-04-14`, subject to explicit selection and compatibility check. It is a cost/compatibility example, not a claim of best memory quality or guaranteed account access.
3. Proposed global cap: 41 outbound model HTTP attempts total, INCLUDING any retries; reject further calls before transmission. Stop the trial after an upstream failure; no automatic paid repair/fallback. A cap is permission to attempt, not a promise of completion. Native default loop settings are not an enforceable financial cap by themselves.
4. Proposed request ceilings: 20,000 input tokens and 4,096 output tokens per request. Verify/count complete prompts, tool schemas and accumulated tool outputs, not just the source excerpt. If a request exceeds the input ceiling, reject rather than silently truncate. Validate output-token setting precedence at the actual outgoing request. Limits remain unimplemented.
5. Disable paid embeddings/skills/Wiki/CodeGraph and unrelated background work. Use explicit raw/atomic keyword query and scenario/core read for initial inspection; broader recall endpoints need separate call-path auditing before calling them zero-cost.
6. Check L0 source retention, readable L1/L2/L3 content, correct approval states, source linkage, and cross-project isolation. Nonempty data or a completed task log is not semantic success. Report missing layers and failed runs rather than silently retrying.

The zero-paid harness comes before asking the user to open API billing. Incremental updates and fresh-task recall are later acceptance steps requiring their own bounded test; this first sample cannot establish durable memory quality.

## Conditional cost example

Official GPT-4.1 mini standard text prices checked on 2026-09-09: USD 0.40 per million input tokens, USD 1.60 per million output tokens. Ignore cache discounts for this calculation.

If all proposed ceilings above are implemented and respected:

41 × ((20,000 × 0.40 + 4,096 × 1.60) / 1,000,000) = USD 0.5966976.

This is an illustrative maximum token charge under proposed constraints, not an observed invoice, guaranteed account spending limit, minimum top-up amount or full-history/monthly cost. It excludes taxes and unrelated account activity. Unknown/timeout responses still consume an outbound attempt. No actual sample tokenization or model calls were performed in this audit.

## Sources

- [Installation guide](https://github.com/TencentCloud/TencentDB-Agent-Memory/blob/2ee22397f6091b8cd3ea847bc1edb04d3bec0c94/INSTALL_CN.md)
- [MemoryCore README](https://github.com/TencentCloud/TencentDB-Agent-Memory/blob/2ee22397f6091b8cd3ea847bc1edb04d3bec0c94/MemoryCore/README.md)
- [Codex integration](https://github.com/TencentCloud/TencentDB-Agent-Memory/blob/2ee22397f6091b8cd3ea847bc1edb04d3bec0c94/agents/codex/README.md)
- [Asset import scope](https://github.com/TencentCloud/TencentDB-Agent-Memory/blob/2ee22397f6091b8cd3ea847bc1edb04d3bec0c94/agents/codex/asset-import.md): default import scans sessions and skills; do not run broad import or -y for the bounded sample.
- [Standalone model runner](https://github.com/TencentCloud/TencentDB-Agent-Memory/blob/2ee22397f6091b8cd3ea847bc1edb04d3bec0c94/MemoryCore/src/adapters/standalone/llm-runner.ts)
- [Standalone defaults](https://github.com/TencentCloud/TencentDB-Agent-Memory/blob/2ee22397f6091b8cd3ea847bc1edb04d3bec0c94/MemoryCore/tdai-gateway.standalone.yaml)
- [L3 trigger](https://github.com/TencentCloud/TencentDB-Agent-Memory/blob/2ee22397f6091b8cd3ea847bc1edb04d3bec0c94/MemoryCore/src/core/persona/persona-trigger.ts)
- [v3 data API](https://github.com/TencentCloud/TencentDB-Agent-Memory/blob/2ee22397f6091b8cd3ea847bc1edb04d3bec0c94/MemoryCore/v3-api-memorycore-doc.md)
- [GPT-4.1 mini pricing/features](https://developers.openai.com/api/docs/models/gpt-4.1-mini)
- [Official OpenAI MCP documentation](https://learn.chatgpt.com/docs/extend/mcp)

Confidence: High for inspected source behavior and conditional arithmetic; Moderate for proposed route suitability; Unknown for real sample request count, installed-artifact equivalence, memory quality and end-to-end integration.

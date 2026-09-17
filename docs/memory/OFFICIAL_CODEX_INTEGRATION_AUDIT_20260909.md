# TencentDB Agent Memory Codex integration audit — 2026-09-09

## Verdict

The thesis project has a verified, project-isolated MemoryCore L0–L3 seed and now has an on-demand, project-scoped Codex MCP recall tool. It is **not** a complete official Proxy integration.

The official Codex route at source commit `2ee22397f6091b8cd3ea847bc1edb04d3bec0c94` changes Codex's model provider and `base_url` to MemoryProxy. The Proxy then performs session initialization, L2/L3 injection and L0 archiving while forwarding every model request to a separately configured upstream. This is materially different from the present subscription-backed desktop route.

## Source checklist

| Official capability | Local status | Evidence or gap |
| --- | --- | --- |
| MemoryCore L0/L1/L2/L3 persistence | Implemented and verified | `tdai-ramp-metering-memory-v1`; `docs/memory/FORMAL_PROJECT_MEMORY_20260909.md` |
| v3 team/agent/user isolation on memory data | Implemented and tested | Fixed IDs in import and recall; wrong-identity query returned empty |
| Full L2 document retrieval | Implemented in this audit | `scenario/ls` followed by `scenario/read` in `formal_persistence_probe.mjs` |
| Project-scoped Codex recall | Implemented in this audit | `.codex/config.toml`; zero-argument `read_project_memory` MCP tool |
| Memory recall without an LLM call | Implemented | Fresh `--network none` container; BM25/read-only path |
| Persistent MemoryCore service | Not implemented for thesis | Current reader starts a disposable network-disabled gateway |
| Memory Hub / Panel | Not implemented for thesis | Hub image exists locally but no thesis Hub deployment or business assets exist |
| Team / Agent / Task management entities | Not implemented | Existing IDs scope memory records but were not created as v3 metadata entities |
| MemoryProxy Codex provider route | Not implemented | Codex provider/base URL remains unchanged |
| Automatic L2/L3 injection on every turn | Not implemented | MCP recall is explicit/on-demand |
| Automatic completed-conversation L0 capture | Not implemented | Formal seed was imported explicitly; future turns are not archived automatically |
| Automatic incremental L1/L2/L3 generation | Deliberately not implemented | Automatic updates conflict with the user's explicit trigger/cost boundary |
| Guarded manual incremental L0–L3 update | Implemented, not yet executed | Exact-hash approval manifest, unique session/receipt, persistent global and per-run budget gates, reviewed L3 write and offline readback |
| Skill, Wiki and CodeGraph assets | Not implemented | Outside the bounded thesis-memory seed |
| Historical Codex session import | Deliberately not performed | Official importer scans broad session/skill locations; no such broad transfer was authorized |

## Changes made in this audit

1. `read_formal_memory.mjs --full` now returns the L2 scenario body, not only its index entry.
2. `.codex/config.toml` registers `ramp_project_memory` with one fixed, zero-argument, read-only tool: `read_project_memory`.
3. The MCP tool fixes the project root and formal reader path; callers cannot select another volume, identity, route or file.
4. The tool refuses responses above 64 KiB instead of silently omitting L3.
5. Protocol unit tests and a real end-to-end, network-disabled recall passed.
6. A separate user-triggered incremental updater now validates an exact approval manifest in a no-side-effect dry run and can execute only after a fresh approval. Its real MemoryCore write path remains unexecuted.

## Why the official Proxy route was not silently enabled

The official configuration would set `model_provider = "team-proxy"` and point Codex at `http://127.0.0.1:8096/codex/<spaceId>`. It also requires a Proxy upstream URL, API key and model. This would route ordinary Codex model inference through the separately billed upstream instead of merely paying for memory extraction. The existing authorization for a small memory-extraction sample does not define this ongoing inference cost or authorize replacing the subscription model path.

Current official OpenAI Codex configuration documentation also states that project-local `.codex/config.toml` ignores `model_provider` and `model_providers`; provider definitions belong in user-level configuration. A true Proxy switch therefore cannot be confined by adding those provider keys to this repository alone. The project-local MCP server remains supported and does not require that provider change.

The fixed Codex documentation also states that the session-init form requires Plan mode; in Default mode the Proxy permanently skips initialization and performs no injection. Therefore starting Core/Hub/Proxy containers alone would not complete the integration.

## User clarification and selected route

The user subsequently clarified that ordinary Codex conversations must not be routed through separately billed OpenAI API inference. Therefore the official full Proxy route is excluded for normal project work. The selected integration route is:

- preserve the Codex subscription provider for ordinary work;
- use the project-scoped MCP tool for explicit, zero-model-call recall;
- prepare and perform a bounded milestone delta update only when the user explicitly asks to update Tencent memory;
- present the exact files, model calls and cost ceiling for approval before each paid update;
- keep repository documents authoritative and do not import broad session history.

Do not proactively prepare, upload or refresh memory merely because a task or milestone ended. This route deliberately does not provide automatic per-turn capture or injection. Those official Proxy features are inseparable from forwarding the corresponding model request to a configured upstream in the audited design.

No paid model request, project upload, provider change, Hub initialization or historical session import was performed by this audit.

## Audited upstream sources

- [Root README](https://github.com/TencentCloud/TencentDB-Agent-Memory/blob/2ee22397f6091b8cd3ea847bc1edb04d3bec0c94/README.md)
- [Installation guide](https://github.com/TencentCloud/TencentDB-Agent-Memory/blob/2ee22397f6091b8cd3ea847bc1edb04d3bec0c94/INSTALL_CN.md)
- [MemoryCore README](https://github.com/TencentCloud/TencentDB-Agent-Memory/blob/2ee22397f6091b8cd3ea847bc1edb04d3bec0c94/MemoryCore/README.md)
- [Codex adapter README](https://github.com/TencentCloud/TencentDB-Agent-Memory/blob/2ee22397f6091b8cd3ea847bc1edb04d3bec0c94/agents/codex/README.md)
- [Codex asset-import scope](https://github.com/TencentCloud/TencentDB-Agent-Memory/blob/2ee22397f6091b8cd3ea847bc1edb04d3bec0c94/agents/codex/asset-import.md)
- [OpenAI Codex configuration reference](https://learn.chatgpt.com/docs/config-file/config-reference)

Confidence: High for the source-to-local checklist and completed verification; Unknown for subscription compatibility and real ongoing Proxy cost because that route was not executed.

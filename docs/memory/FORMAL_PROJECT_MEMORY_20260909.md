# Formal project memory import — 2026-09-09

## Outcome

The bounded thesis-project seed is persisted in Tencent MemoryCore volume `tdai-ramp-metering-memory-v1` under service ID `ramp-metering-formal-memory-v1` and the fixed identity `team-masterarbeit-ramp-metering` / `agent-project-memory` / `user-yuhong-zhang`.

A fresh container with networking disabled reopened the volume and returned L0=4, L1=6, L2=1 and L3 present. Full retrieval included the project identity, ramp-metering sweet-spot direction, Robert Hilbrich's guidance and non-approvals, the incomplete Stage 2 status, measurement-repair boundaries, unresolved timing, and next-action restrictions.

## Inputs and processing

`docs/memory/formal_import_bundle_20260909.md` is a 9,882-byte normalized seed derived from the five explicitly authorized project files. It records their paths and SHA-256 hashes. The source files remain authoritative.

The MemoryCore native pipeline used `gpt-4.1-mini` through Chat Completions to create six L1 atomic memories and one L2 scene. Automatic continuation after L2 did not finish under the 20,000-byte request gate. The reviewed core summary `docs/memory/formal_core_memory_20260909.md` was therefore written to L3 through MemoryCore's official `/v3/core/write` endpoint in a network-disabled container. L3 is a deterministic reviewed seed, not GPT-generated output.

## Cost and failures

The original 41-attempt ceiling is preserved across two immutable ledgers:

- fixed-snapshot ledger: four attempts, all zero-token failures — three HTTP 401 invalid-key responses caused by the documented Keychain CLI truncation and one HTTP 403 for the API-project-inaccessible exact snapshot;
- alias ledger: two HTTP 200 attempts, 8,582 prompt tokens and 1,322 completion tokens in total;
- combined: six claimed attempts, 35 remaining;
- estimated token charge at published GPT-4.1 mini rates: USD 0.005548.

The model metadata endpoint returned 404 for `gpt-4.1-mini-2025-04-14` in this API project and 200 for `gpt-4.1-mini`. The formal successful extraction therefore uses the stable alias. No API key is stored in Docker, repository files, ledgers or receipts.

## Retrieval

From the repository root:

```bash
node scripts/memory/read_formal_memory.mjs
node scripts/memory/read_formal_memory.mjs --full
```

Both commands start a disposable, network-disabled container. The compact command validates counts, identity and hashes. `--full` returns L1/L2/L3 content for task handoff. This does not automatically inject memory into a new Codex task; the new task must execute the reader or read current project documents.

The project-scoped Codex configuration also exposes a zero-argument, read-only MCP tool named `read_project_memory`. It calls the same fixed reader and does not change the Codex model provider. The full reader now follows the L2 index with `scenario/read`, so the scenario body is returned rather than only its path entry. Invocation remains explicit/on-demand, not automatic per-turn injection.

## Verification hashes

- L0 query: `896bc29442581ebc36274e5467df513acc89a0b30784d76d280f245d26ced9b5`
- L1 query: `7ef063bfe7001b9b8dbe844d35f6bcb054570eaab52bc33bc59c8969655645d9`
- L2 query: `0d616c74eac71abe1ca35cb2ca2164a5595eebca9052da8c6d5643ddbf6d9447`
- L3 query: `a350c926ab8a6201a9361a020490a439afc2453ce811b81cd11aef76d50e154a`
- reviewed L3 source body: `3419574243e4496f6a29d62730686be3ca8c97005f5df3bbbcfe5a0b651ab13c`

The L3 query hash differs from the source-body hash because the API response includes structured metadata around the stored content.

## Limitations

- Memory is auxiliary and can become stale; repository documents override it.
- Automatic incremental capture and automatic per-turn/new-task injection are not implemented; the MCP tool must be called explicitly.
- A guarded manual incremental updater is implemented but has not been executed. It requires an explicit `user-approved` manifest, exact source hashes, a unique session/update ID and a separately approved per-run model-attempt ceiling. Ordinary tasks never trigger it.
- The volume also retains initialization/failed-attempt namespaces under earlier service IDs; the formal reader is hard-coded to the final service ID and does not query them.
- Project isolation was verified for the configured identity in the earlier native harness and the formal reader fixes all identity fields, but this is not an adversarial security audit.

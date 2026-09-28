# Stage 6 MemoryCore content correction — V1 result

**Disposition: `CONTENT_ACCEPTANCE_FAILED` — STOP.** The three false sentences were removed from current L1/L2/L3, but the official L1 update unexpectedly changed the target atom's type from `episodic` to `persona`. The installed official `atomic/update` request accepts only `id`, `content` and optional `background`; it provides no documented type setter. Deleting/recreating the atom would not preserve the original record and is outside this task. No further write was attempted after the final read established the type change.

## Provenance and execution

- Original incremental-write receipt remains unchanged: `data/processed/memory_incremental_stage6-partial-pairability-20260926-v1/receipt.json` (SHA-256 `2bfd7df3c2305f00afc953fa8a4d134f2d741a1a4e89b9c917246b53cf784ea2`). L0 history was not changed.
- `PRECORRECTION_READ_RECEIPT.json` records a fresh network-disabled read matching the original receipt's four layer hashes and all target versions/content hashes.
- `EXECUTION_RECEIPT.json` records three successful official calls (`atomic/update`, `scenario/write`, `core/write`) followed by a failed immediate verifier. The verifier found that L1's original Chinese `background` had changed to an English default. It did **not** retry the incremental update.
- `L1_BACKGROUND_RESTORE_RECEIPT.json` records one further official `atomic/update` with unchanged corrected content and the original background explicitly supplied. A fresh read confirms the background is restored. The restore script reported failure because it expected a version increment to 2; the installed interface's `atomic/query` still returned version 1.
- `FINAL_VERIFICATION_RECEIPT.json` records another **fresh** `--network none` read. L0 remained 10 records with its original hash; L1/L2 counts remained 13/2. All unrelated L1 and L2 records are byte-for-byte unchanged in their returned fields. The corrected L1 text, corrected L2 body and complete corrected L3 match the versioned candidate hashes. The old “without writing” and “candidate only / last confirmed 2026-09-10” statements are absent from every current L1/L2/L3 item.
- No external model call, new paid attempt, replay of the increment, direct database write, scientific input change or SUMO start occurred. The gateway ran in a network-disabled container with capture/extraction disabled and an unreachable LLM endpoint.

## Remaining blocker

The target L1 atom `m_1790425813551_503da35b` was `type=episodic` in the original write receipt and the pre-correction read. It is now `type=persona` despite retaining the same ID, corrected text, original background and version 1. This is a **material metadata change outside the requested factual correction**. The [pinned official MemoryCore v3 API reference](https://github.com/TencentCloud/TencentDB-Agent-Memory/blob/2ee22397f6091b8cd3ea847bc1edb04d3bec0c94/MemoryCore/v3-api-memorycore-doc.md) documents no way to set L1 type through `atomic/update`; the installed handler also omits a type input. Therefore the official interface used here cannot safely restore the original atom type. The stored memory must **not** be marked content-accepted. Repository records and the original execution receipt remain authoritative.

The new L2 still contains earlier unsupported user-trait inferences; they were outside this narrowly authorized three-error correction and remain non-authoritative. No additional mutation is recommended without a separately reviewed safe type-preserving route.

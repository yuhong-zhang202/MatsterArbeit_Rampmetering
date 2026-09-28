# Stage 6 MemoryCore content correction — V1

**Scope:** Repair only three false operational statements persisted by `stage6-partial-pairability-20260926-v1`. The original update receipt and L0 source session remain unchanged. No Stage 6 scientific classification, approval boundary, supervisor statement, formal protocol or research data changes.

**Source:** `data/processed/memory_incremental_stage6-partial-pairability-20260926-v1/receipt.json`, SHA-256 `2bfd7df3c2305f00afc953fa8a4d134f2d741a1a4e89b9c917246b53cf784ea2`. A separate pre-correction `--network none` MemoryCore read matched the original receipt's L0/L1/L2/L3 layer hashes and counts 10/13/2/present. The original receipt is never edited.

**Official API:** The installed image `sha256:9798254a8cc06276b7c5b3c19df49f136fae25d579564e1f01f9c4b9b8cd2d11` supports `/v3/atomic/update`, `/v3/scenario/write` and `/v3/core/write` for L1, L2 and L3 respectively. The [pinned Tencent MemoryCore v3 API reference](https://github.com/TencentCloud/TencentDB-Agent-Memory/blob/2ee22397f6091b8cd3ea847bc1edb04d3bec0c94/MemoryCore/v3-api-memorycore-doc.md) documents these routes, response versions and historical-version reads for L2/L3. The installed handler confirms `scenario/write` expects the L2 body without the META header; it maintains `created`, updates `updated`, and preserves `summary` when omitted. No delete endpoint, direct SQLite access or model pipeline will be used.

## Exact correction

| Layer | Target | Prior text SHA-256 | Change |
| --- | --- | --- | --- |
| L1 | `m_1790425813551_503da35b` | `576dfe8dce6400779de8207a271651d5bb108b9fcdc41c24d0f9741aca54e4e3` | Replace the false “without writing” clause with the verified MemoryCore write/readback fact. Preserve ID, type and background. |
| L2 | `Project-Memory-Management-Stage6.md` | `c0adf8800e2cd6eaa16d9579abb370164f767f201d42dc876bb29980088a2b61` | Replace the same false clause. Preserve all other body text and META fields except the API-managed `updated` timestamp. |
| L3 | `core/read` for the fixed project identity | `750018619d885e46a9a6076280078eb0e7dba3824448c82bb09b5a69e2da2fe3` | Replace “last confirmed write 2026-09-10 / candidate only” with the confirmed 2026-09-26 write and change the final `Candidate date` label to `Stored content date`. Preserve every scientific paragraph. |

Exact replacements, identity, expected layer hashes, old versions and new candidate hashes are machine-bound in `CORRECTION_SPEC.json`. The corrected L2 body and full corrected L3 are stored in `SCENARIO_BODY_CORRECTED.md` and `CORE_CORRECTED.md`. The L1 corrected text is in the JSON spec. These are new versioned correction artifacts; they do not overwrite the approved 2026-09-26 source candidates.

## Execution guards and acceptance

The one-use runner `scripts/memory/run_stage6_content_correction_20260926.mjs` first validates the original receipt and candidate hashes. It starts an isolated `--network none` container with capture/extraction disabled and LLM endpoint intentionally unreachable. The container reads all four layers through official APIs, checks exact layer and target hashes and expected versions, then issues exactly one update each to L1, L2 and L3. Any mismatch stops before a write. A partial write failure stops without automatic retry and is recorded.

Immediate readback must find exact corrected target text, unchanged L0 count/hash, unchanged L1/L2 counts, unchanged unrelated L1/L2 records and no forbidden false phrase in target records. A separate **fresh** `--network none` reader container must then independently confirm L1/L2/L3 and produce a final verification receipt. Until both stages pass, content acceptance remains pending. The prior L2's broad user-trait inference and all other material outside the three specified errors remain outside this correction's scope and non-authoritative.

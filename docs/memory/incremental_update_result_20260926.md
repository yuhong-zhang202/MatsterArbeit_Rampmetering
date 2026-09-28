# Tencent project-memory incremental update result — 2026-09-26

Update/session: `stage6-partial-pairability-20260926-v1`  
Execution: **passed mechanically, with content-quality exceptions below**.  
Authoritative machine receipt: `data/processed/memory_incremental_stage6-partial-pairability-20260926-v1/receipt.json`.

## Authorization and exact inputs

After review of the two displayed hashes and limits, the user replied “批准”. Paid manifest: `docs/memory/incremental_update_approval_20260926.json`, SHA-256 `4f6c207aa72e614353e6fe49b6ecab85b71547afe77c3722e48f81c351167450`. The separate dry-run manifest remains unchanged. Delta: `docs/memory/incremental_update_20260926.md`, 7,216 bytes, SHA-256 `05193487a842d8a61395431407b989c44c1250b7f992af5ab3f5c4e7f62be2eb`. Complete L3 candidate: `docs/memory/formal_core_memory_20260926_candidate.md`, 7,435 bytes, SHA-256 `b6e3b2f0daec6cb30fbbd0d136f5e238e17f1d74ea4199e6de19659c5af7e353`. Fixed model `gpt-4.1-mini`; approved maximum three new attempts and USD 0.0436608.

The `memory-pilot` Colima profile was restarted. A pre-write network-disabled read showed L0/L1/L2 8/9/1 and the Stage 2 L3. The paid manifest passed the local hash/budget/replay dry-run immediately before execution.

## Persisted layers and budget

| Layer | Before | After | Readback |
| --- | ---: | ---: | --- |
| L0 | 8 | 10 | Unique new session; retained old entries |
| L1 | 9 | 13 | Four new generated items, one incorrect |
| L2 | 1 | 2 | New generated Stage 6 scene, with unsupported inference and one incorrect assertion |
| L3 | present | present | Exact reviewed candidate matches network-disabled readback after MemoryCore trimming |

The native update and a fresh network-disabled container readback both passed. Three API attempts used 7,955 prompt and 997 completion tokens (8,952 total). The ledger estimate at approved rates is **USD 0.0047772**, below the ceiling; it is not the provider's final invoice. Combined attempts are **12/41**, leaving 29. The budget proxy was stopped after execution. No simulation, scientific input, research protocol or supervisor record changed.

## Original content-quality exceptions

1. New L1 `m_1790425813551_503da35b` incorrectly claims that the approved update occurred “without writing to the Tencent MemoryCore”. The new L2 `Project-Memory-Management-Stage6.md` repeats that incorrect claim and adds unsupported user-trait language. The machine receipt and network-disabled readback prove the write **did** occur. Treat those generated sentences as false and non-authoritative. The older L2 scene also retains broad traits and compressed decision timing from 2026-09-10.
2. L3's Stage 6 scientific status, correction and authority boundaries match the approved candidate, but its final operational paragraph still says “last confirmed write was 2026-09-10” and “candidate only until ... execution”. Those lines were valid at drafting time and became stale after this write. The actual current confirmed write is **`stage6-partial-pairability-20260926-v1`**. `docs/PROJECT_STATE.md` and this receipt override that operational wording.
3. No fourth model attempt, repeat session, deletion of generated records, or post-approval alteration of the approved L3 bytes was performed. A future separately reviewed memory-quality correction may remove the erroneous generated records/phrases; it must preserve the source history and use the then-applicable authorization workflow. Do not silently replay this update ID.

## Effective scientific state

The repository and the reviewed L3 body agree that Stage 6 remains `PARTIAL`, full-network A is `A_NOT_EVALUABLE`, the original R0/A static pair is corrected to `NOT_PAIRABLE`, and B/C were not run. The historical R0 `CONTROL_NOT_EVALUABLE`, locked P/S/L and 0.85 rules, and unfrozen formal protocol remain unchanged. The memory update does not authorize any simulation or scientific change.

## Versioned correction attempt, later on 2026-09-26

The user requested a narrow repair of the three false operational statements. The original machine receipt above remains untouched. Using official MemoryCore v3 interfaces in network-disabled containers, the false text was replaced in L1, L2 and L3 and a fresh read confirmed the corrected content. **Content acceptance remains `FAILED`** because `atomic/update` unexpectedly changed the target L1 atom's type from `episodic` to `persona`. Its background was restored through a second official update; its original type could not be restored through the documented interface. All unrelated L1/L2 records and L0 are unchanged. No further write, model call or incremental replay occurred. Exact read/write sequence, hashes and stop rationale: `docs/memory/stage6_content_correction_20260926_v1/CORRECTION_RESULT.md` and its JSON receipts.

## Later L1 type restoration, 2026-09-26

At the user's request, the remaining L1 type side effect was repaired through a one-use, network-disabled gateway patch after a byte-identical backup and a passing isolated-volume test. The installed `atomic/update` handler had taken the first row returned by `queryL1Records`, while the SQLite implementation ignored its `recordIds` filter. The temporary patch selected the exact ID and enforced the target identity, current type/version, content hash and background before changing only the type to `episodic`; the normal version/update time advanced. A fresh **unpatched** gateway read of a byte-verified post-repair copy confirmed L1 type-filter behavior and unchanged L0/L2/L3 hashes. The original three erroneous statements are absent. This narrowly scoped correction is now accepted; unrelated generated L2 user-trait inferences remain non-authoritative and unaudited. The original failed correction receipt remains historical evidence. Full repair, negative-test and readback records: `docs/memory/stage6_l1_type_restore_20260926_v1/TYPE_RESTORE_RESULT.md`. No model call or incremental replay occurred.

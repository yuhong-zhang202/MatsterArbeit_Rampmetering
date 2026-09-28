# Independent engineering review — PAIR3199 matched-input repair v5

**Disposition: PASS for offline matched-input construction and fail-closed validation.**  
**Findings:** Blocker 0 / Major 0 / required Minor 0.  
**Confidence:** High for current input invariants, parser behavior, and hash provenance.  
**Authorization:** None. The previous one-start treatment authorization remains consumed.

## Context and scope

Read `AGENTS.md`, `docs/PROJECT_STATE.md`, `docs/DECISIONS.md`, `docs/EXPERIMENT_PROTOCOL.md`, and `docs/WORKLOG.md`, along with the v5 repair report, invariant report, provenance receipt, manifest, checker and tests. Project state records offline input repair as the current phase, the former treatment result as `NOT_EVALUABLE`, the treatment authorization as consumed, and the formal protocol as unfrozen. This was a read-only engineering review; no simulation, code, or raw data was changed.

## Independent verification

- The 12-case targeted suite passes **12/12**. It includes the former v3/v4 bypass regressions: treatment-only top-level `<flow>`, nested common-vehicle `<param>`, unknown vehicle attribute, UTF-16 DTD default-attribute attempt, UTF-8 DTD default-attribute attempt, and UTF-8 BOM. It also covers missing U, factor mismatch/absence, route mutation, vType mutation, and valid exact-R-only inputs.
- Running the checker on the v5 route files returns `PASS`, with M/U/X counts 1,333/150/75 in both arms; treatment additionally has R=192. Common identities, complete vehicle attribute records, integer-ms departures, routes/types, and exact lexical speedFactors match **1,558/1,558**. Treatment-only IDs are exactly `R_flow.0`–`R_flow.191`.
- I checked the v5 XML validation path: it requires strict UTF-8 without BOM/NUL, rejects non-UTF-8 XML declarations, and runs an Expat safety pass whose callbacks reject DOCTYPE/entity declarations, external entity references, comments, and processing instructions before ElementTree parsing. The final parser then rejects unsupported top-level tags, every nested element, missing/unknown attributes, non-whitespace text, duplicates and unsorted vehicle records. This closes the tested UTF-16 DTD/default-attribute bypass.
- The schedule formula independently matches the manifest/checker integer-ms schedules: M offset 1,125 ms, U 10,000 ms, X 20,000 ms, and R 5,000 ms. Counts and schedules are fully represented in the checker’s fixed expected specifications.
- I recomputed receipt hashes for the checker, tests, v5 manifest/report/invariant report and both route XML files; all match. I also recomputed all five source hashes referenced by the manifest; all match.
- Code inspection found no subprocess, `os.system`, SUMO, TraCI, or netconvert launch path. The materializer refuses to overwrite an existing v5 output directory. Receipt status says `HASH_BOUND_OFFLINE_INPUT_PACKAGE_NOT_AUTHORIZED` and records zero simulator starts.

## Disposition and limits

The prior critical checker bypass is closed for the stated UTF-8-only format: a valid UTF-16 DTD cannot reach the XML parser, and UTF-8 DTD declarations are explicitly rejected by Expat before default attributes can be applied. The v3/v4 top-level flow and nested vehicle bypasses are also covered and rejected. The current v5 package therefore passes this bounded engineering review for **planned-input** matching. This does not establish future vehicle insertion, trajectory equivalence, or a witness result; any future run requires a newly reviewed exact card and separate user authorization. SUMO/TraCI/netconvert starts for this review: **0/0/0**.

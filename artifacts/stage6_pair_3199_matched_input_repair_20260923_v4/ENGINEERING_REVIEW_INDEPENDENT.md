# Independent engineering review — PAIR3199 matched-input repair v4

**Disposition: NOT PASS — one required fail-closed XML parsing issue.**  
**Findings:** Blocker 0 / Major 1 / required Minor 0.  
**Confidence:** High for tested parser behavior, invariants, and receipt hashes.  
**Scope:** Read-only review of v4 materializer/checker, test suite, input package, provenance, and current project state. No simulator or code edit.

## Context

Reviewed `AGENTS.md`, `docs/PROJECT_STATE.md`, `docs/DECISIONS.md`, `docs/EXPERIMENT_PROTOCOL.md`, `docs/WORKLOG.md`, v4's repair report, manifest, invariant report, provenance receipt, and checker/tests. Current phase is offline matched-input repair; the previous single treatment authorization is consumed; no new card or authorization exists; formal protocol is unchanged and unfrozen.

## Verified

- The nine-case targeted suite passes 9/9. It covers an ordinary valid pair, missing U identity, common speedFactor mismatch, missing speedFactor, treatment-only top-level flow, nested vehicle `<param>`, unknown vehicle attribute, route-edge mutation, and vType-attribute mutation.
- Independent checker execution returns PASS: control M/U/X=1333/150/75; treatment M/U/X/R=1333/150/75/192; common IDs, scheduled departures, route/type assignments, speedFactors and full vehicle attributes match 1,558/1,558. Treatment-only IDs are exactly R_flow.0–R_flow.191.
- Top-level unsupported nodes, nested elements, unknown or missing node attributes, mixed non-whitespace text, in-root comments/PIs, duplicate IDs and ordering violations are rejected by code inspection or exercised mutations. Ordinary UTF-8 DTD/entity declarations are rejected by the raw-byte check.
- Receipt hashes independently match for checker, tests, generated route files, recorded package files, and all five source inputs.
- No launch path is present: the checker/materializer uses XML, file hashing, JSON and filesystem operations; it does not invoke subprocesses, SUMO, TraCI, or netconvert. The materializer refuses an already-existing v4 output directory.
- The integer-millisecond schedules and counts match the fixed pair specification in the checker and manifest (M 1,125 ms, U 10,000 ms, X 20,000 ms, R 5,000 ms). These are planned-input checks only.

## Required issue — UTF-16 DTD bypass can supply apparently explicit attributes

The DTD/entity guard searches raw bytes for the ASCII sequences `<!DOCTYPE` and `<!ENTITY`. A valid UTF-16 document contains interleaved NUL bytes, so those sequences are not found. Python's XML parser then processes the internal DTD and supplies default attributes to parsed elements.

I verified this with temporary files only. I converted the treatment route XML to valid BOM-prefixed UTF-16, added an internal DTD declaring a default `speedFactor` equal to control `M_flow.0`, and removed the literal `speedFactor` attribute from treatment `M_flow.0`. `parse_materialized()` returned the DTD-supplied value and `check_pair()` returned **PASS**. Thus v4 can accept a document where the required vehicle attribute is not explicitly materialized and where DTD semantics contribute the checked record. This contradicts the stated policy that DTD/entities are unsupported and weakens the explicit-attribute invariant.

**Required closure:** Reject DTD/entity declarations encoding-independently before normal parsing, or use a parser configuration that rejects DTD and entity declarations. Add a regression using UTF-16 (at minimum) with a DTD-supplied default for a required vehicle attribute; assert the checker rejects it. Rebuild/re-hash the checker, tests, report and receipt and rerun the independent review.

There is also a narrow documentation precision point: comments/PIs inside the root are rejected, while trailing comments/PIs after `</routes>` are discarded by ElementTree and accepted. They do not add route records, so I do not count this as a separate required issue; either reject epilog misc nodes too or avoid claiming every comment/PI is rejected.

## Boundary

The current unmodified v4 package itself passes all recorded static checks and its provenance. The required issue concerns the checker’s fail-closed behavior under a valid XML encoding/DTD mutation; engineering disposition remains **NOT PASS** until closed. This review does not authorize a card or run and makes no claim about future insertion, trajectory equivalence, or the previous treatment's witness result. SUMO/TraCI/netconvert starts for this review: 0/0/0.

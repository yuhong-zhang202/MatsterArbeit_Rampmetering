# Issue16 independent static reader review V1

**GO_FOR_FAILED_PREFIX_READER_ONLY.** No material blocker found in the bounded reader repair. This does not approve a runtime contract change, reclassify the original run as safe, qualify the actuator, or authorize a new native start.

## Context and scope

Mandatory Context Preflight and the complete assigned historical ranges are recorded in CONTEXT_AND_COMMAND_RECEIPT_V1.json. Review was limited to the three owning reader modules, the final data repair report/binder/result, and the unchanged original card's source hashes. The prior T1 mechanism report and investigation binder remain unchanged. Governance, runtime, raw, cards and safety rules were read-only.

## Static findings

1. The default remains exact-current-card source validation. Explicit --postanalysis-reader-v1 separates the 173 original execution-source snapshots from the 15 current reader/dependency hashes. Only actual.py, streaming.py and provenance.py are allowed to differ; the remaining current runtime/dependency sources must still match the original card. All three saved verbatim preimages match the original card's source hashes. This prevents presenting the new reader as the executed old version.
2. Supported failed-prefix classification requires the exact retained terminal cause, last ACK/accounted step, G movement, receiver/front/leader/query identity and timestamp joins. Independent following reconstruction still emits CURRENT_NATIVE_QUERY_FLOOR_DENIED. Interior missing feedback remains rejected; only the exact retained terminal event may remain explicitly unobserved.
3. Worker exit 1 and native EOF 0 remain distinct. The supported controller STOP requires verified native identity, four-log EOF and owned-group cleanup; it is not a general worker success or traffic safety certificate.
4. The endpoint helper validates frame-key/record-ID agreement before copying the native record, avoiding the newly reached duplicate keyword TypeError without discarding endpoint evidence. The first real failure is preserved in the data report; its transient reconstructed source is explicitly distinguished from verbatim original preimages.

## Evidence checked

- READER_FIX_REPORT_V1.md SHA256 3561335b20b76414fd85214d804bf3a13a0c43a351dbf7b6c18e40c283714d05.
- READER_FIX_BINDING_V1.json SHA256 74df97acf3da6eb2603c29ad06e70f7181f4b6dc22fd244f92fed10381bdc61f: all 30 bound entries independently matched file bytes/hash.
- native_postanalysis_v3/NATIVE_AUDIT_RESULT.json SHA256 3d97ac0ce90fb84f7d4e437207b5e2d79f4bbc17846facad271ab4d3ccc67060: UNKNOWN_INCOMPLETE_EVIDENCE; missing/unknown only full_horizon (last ACK650 versus target4200); qualified/native_safety_proven/formal_effect_proven all false. Both the current query-floor denial and runtime STOP remain observed alarms. Unreached windows and urban evaluation remain untested/unknown.

All three paths above are under data/processed/issue16_natural_gap_scope_20261015_v1/reader_fix_v1/. Current owning hashes are recorded in READER_STATIC_REVIEW_BINDING_V1.json.

## Verification and limits

Only source/document reads and Python stdlib JSON/hash/byte checks were performed for this final independent review. No tests, audit entry point, native command, simulation or raw reanalysis was run. The data agent reports four targeted test methods passing in 0.567s and 17 rejection variants; those results were inspected, not independently rerun. A display-only check initially assumed card['sources'] and raised KeyError; the actual existing key is sources_sha256. The corrected read-only check succeeded. No project file was changed by that failed display.

The T1 recommendation remains MINIMAL_SCOPE_CHANGE_PROPOSED, awaiting scientific review and explicit user contract approval. Documentation impact: root owns required STATE/WORKLOG/Issue updates; this reviewer changes only this new engineering receipt and its binding.

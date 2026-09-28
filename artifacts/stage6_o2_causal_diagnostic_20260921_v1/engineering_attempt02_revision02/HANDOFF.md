# Attempt02 handoff — no new SUMO start yet

Card SHA `c5b86295f41a9dedbd59cfd10427b34a9d50d522fd941b1df83fc89fd0d261f2`.

Read `diagnostics/ROOT_CAUSE_AND_FIX.md`, `code_changes.diff`, `startup_probe.py`, `DIAGNOSTIC_CONTRACT.md` and `authorization_provenance.json` before review. Underlying SUMO startup cause remains Unknown; the8s observable timeout is not itself a proven lower-level cause. The only technical changes are a60s owned-listener wait, one pre-step ps/startup sample, fresh attempt paths and honest cumulative accounting. Scientific inputs and450-step observer are unchanged.

Verified: Python TCP/lsof control PASS;14 inherited fake-process/observer tests+6 new readiness tests PASS;58 static checks;3 local XSD validations;27 installed getter checks. No new simulator/network build was started.193 card bindings passed dry-run. Prior attempt01 remains immutable; its1 start/8.43560208400595s/13288B are retained, and no budget is silently reset.

This new card authorizes only one attempt02 after exact static/scientific PASS and parent-bound release under the user's existing continuing troubleshooting instruction. No automatic retry. If it fails, preserve evidence, state known/unknown root cause and formulate a new reviewed technical fix for this same condition. Successful runtime must then pass independent C-prefix neutrality and data gates before any U35 explanation.

The parent creates `O2_RELEASE_APPROVAL.json` from the template, binds a top-level `stage=exact_o2_diagnostic_package` PASS_STATIC_FINAL receipt and this card SHA. Do not use the old consumed card or sidecar.

Command after review/release only:

```sh
env -u PYTHONPATH SUMO_HOME=/Library/Frameworks/EclipseSUMO.framework/Versions/1.26.0/EclipseSUMO/share/sumo PATH=/usr/bin:/bin LANG=C LC_ALL=C \
 /Library/Frameworks/Python.framework/Versions/3.13/bin/python3.13 -B /Users/yuhongzhang/Desktop/Masterarbeit-Ramp-Metering/artifacts/stage6_o2_causal_diagnostic_20260921_v1/engineering_attempt02_revision02/runtime_executor.py \
 --card /Users/yuhongzhang/Desktop/Masterarbeit-Ramp-Metering/artifacts/stage6_o2_causal_diagnostic_20260921_v1/engineering_attempt02_revision02/O2_DIAGNOSTIC_CARD.json \
 --approval /Users/yuhongzhang/Desktop/Masterarbeit-Ramp-Metering/artifacts/stage6_o2_causal_diagnostic_20260921_v1/engineering_attempt02_revision02/O2_RELEASE_APPROVAL.json --execute
```

Use supported elevated execution for the authorized SUMO/socket/OS observation; no sandbox or signature workaround. Fresh output root: `data/raw/stage6_o2_causal_diagnostic_20260921_v1/O2_C_S17_450_attempt2/`. Per-attempt180s/200MB and cumulative188.43560208400595s/200013288B are observed stop-lines with50ms polling, not hard quotas. The same group contains observer and its sole SUMO child. The startup sample is bounded to1s sampling with5s subprocess timeout and occurs before connection/traffic stepping.

Primary owns state/worklog updates. No governance, protocol, old cards or raw files were modified by this preparation.

## Path repair revision02

Prior attempt02 package was rejected before launch because card/input_manifest roots still identified attempt1. All old packages remain unchanged. This version fixes that generator constant and adds validate_path_isolation.py: card, input_manifest,20 XML writers and18 roles must all identify the same new attempt2 root. The known-bad old card is a mandatory negative regression. path_isolation_receipt.json verifies attempt1 all11 files/13288B unchanged and target attempt2 absent. Runtime executor/observer/startup_probe are byte-identical to the preceding technical revision; readiness60s and one startup sample remain. isolation_repair_report.json confirms demand byte identity and all config/additional science semantics equal attempt1 except new paths.

Full offline commands used, all with `.venv/bin/python -B` from project root: `tests/test_offline.py` (14/14), `tests/test_startup_probe.py` (6/6), `static_validate.py` (58 checks/3XSD/27APIs), `finalize_package.py`, `validate_path_isolation.py`, then the explicit zero-process dry-run above. Each relative script is under this package directory. No release sidecar has been created; a fresh exact review is required.

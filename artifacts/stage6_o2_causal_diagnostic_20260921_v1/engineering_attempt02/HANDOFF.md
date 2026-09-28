# Attempt02 handoff — no new SUMO start yet

Card SHA `fce5fc6f4580557528d2d1f182ed0fc933fec3e2e8b9b77c1fa9e93dde8cfbbc`.

Read `diagnostics/ROOT_CAUSE_AND_FIX.md`, `code_changes.diff`, `startup_probe.py`, `DIAGNOSTIC_CONTRACT.md` and `authorization_provenance.json` before review. Underlying SUMO startup cause remains Unknown; the8s observable timeout is not itself a proven lower-level cause. The only technical changes are a60s owned-listener wait, one pre-step ps/startup sample, fresh attempt paths and honest cumulative accounting. Scientific inputs and450-step observer are unchanged.

Verified: Python TCP/lsof control PASS;14 inherited fake-process/observer tests+6 new readiness tests PASS;58 static checks;3 local XSD validations;27 installed getter checks. No new simulator/network build was started.194 card bindings passed dry-run. Prior attempt01 remains immutable; its1 start/8.43560208400595s/13288B are retained, and no budget is silently reset.

This new card authorizes only one attempt02 after exact static/scientific PASS and parent-bound release under the user's existing continuing troubleshooting instruction. No automatic retry. If it fails, preserve evidence, state known/unknown root cause and formulate a new reviewed technical fix for this same condition. Successful runtime must then pass independent C-prefix neutrality and data gates before any U35 explanation.

The parent creates `O2_RELEASE_APPROVAL.json` from the template, binds a top-level `stage=exact_o2_diagnostic_package` PASS_STATIC_FINAL receipt and this card SHA. Do not use the old consumed card or sidecar.

Command after review/release only:

```sh
env -u PYTHONPATH SUMO_HOME=/Library/Frameworks/EclipseSUMO.framework/Versions/1.26.0/EclipseSUMO/share/sumo PATH=/usr/bin:/bin LANG=C LC_ALL=C \
 /Library/Frameworks/Python.framework/Versions/3.13/bin/python3.13 -B /Users/yuhongzhang/Desktop/Masterarbeit-Ramp-Metering/artifacts/stage6_o2_causal_diagnostic_20260921_v1/engineering_attempt02/runtime_executor.py \
 --card /Users/yuhongzhang/Desktop/Masterarbeit-Ramp-Metering/artifacts/stage6_o2_causal_diagnostic_20260921_v1/engineering_attempt02/O2_DIAGNOSTIC_CARD.json \
 --approval /Users/yuhongzhang/Desktop/Masterarbeit-Ramp-Metering/artifacts/stage6_o2_causal_diagnostic_20260921_v1/engineering_attempt02/O2_RELEASE_APPROVAL.json --execute
```

Use supported elevated execution for the authorized SUMO/socket/OS observation; no sandbox or signature workaround. Fresh output root: `data/raw/stage6_o2_causal_diagnostic_20260921_v1/O2_C_S17_450_attempt2/`. Per-attempt180s/200MB and cumulative188.43560208400595s/200013288B are observed stop-lines with50ms polling, not hard quotas. The same group contains observer and its sole SUMO child. The startup sample is bounded to1s sampling with5s subprocess timeout and occurs before connection/traffic stepping.

Primary owns state/worklog updates. No governance, protocol, old cards or raw files were modified by this preparation.

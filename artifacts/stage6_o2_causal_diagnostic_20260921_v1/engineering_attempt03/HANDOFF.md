# Attempt03: accepted-connection ownership repair

Card SHA `fa90dd0757acbe7f63b86cd95b27baabedf6977f56c9f9885f9f5593a6ea255c`. No SUMO start yet; no release sidecar.

Read `diagnostics/ATTEMPT02_ROOT_CAUSE_AND_ATTEMPT03_FIX.md`, `technical_changes.diff`, `technical_delta_proof.json` and `science_invariants_receipt.json`. Only postconnect ownership logic changes: preserve preconnect child LISTEN gate, then verify the same child's ESTABLISHED descriptor and exact reversed client endpoint tuple. Official hash-bound sources prove SUMO closes the one-client listener after accept; the Python-only live fixture reproduces the old false failure and validates the new check. Startup readiness60s and one pre-step sample are unchanged. No setters, model or scientific settings changed.

Offline validation:14 inherited tests+6 readiness tests+7 new accepted-ownership tests PASS;58 static checks/3XSD/27getter checks PASS;232 exact card bindings pass dry-run. Cross-card path isolation verifies20 XML writers/18 roles share fresh absent attempt3 root and all43 prior raw files remain unchanged. Data measurement gate is byte-identical to attempt02. The two parent's preflight invocation errors are non-SUMO notes, not starts.

Accounting: old2 starts/28.542396625998663s/118166B plus one new card-bounded attempt03 at180s/200MB. Cumulative observed stop-lines208.54239662599866s/200118166B. No automatic retry. Current user authority permits future evidence-based technical attempts of this exact condition only after separate immutable cards/reviews, never a search or scientific grid.

After exact independent static/data/scientific review, the parent may bind a new `O2_RELEASE_APPROVAL.json` using existing authorization. Do not reuse old approval. The review must contain top-level stage=exact_o2_diagnostic_package and status=PASS_STATIC_FINAL for the new card SHA.

Launch command only after review/release:

```sh
env -u PYTHONPATH SUMO_HOME=/Library/Frameworks/EclipseSUMO.framework/Versions/1.26.0/EclipseSUMO/share/sumo PATH=/usr/bin:/bin LANG=C LC_ALL=C \
 /Library/Frameworks/Python.framework/Versions/3.13/bin/python3.13 -B /Users/yuhongzhang/Desktop/Masterarbeit-Ramp-Metering/artifacts/stage6_o2_causal_diagnostic_20260921_v1/engineering_attempt03/runtime_executor.py \
 --card /Users/yuhongzhang/Desktop/Masterarbeit-Ramp-Metering/artifacts/stage6_o2_causal_diagnostic_20260921_v1/engineering_attempt03/O2_DIAGNOSTIC_CARD.json \
 --approval /Users/yuhongzhang/Desktop/Masterarbeit-Ramp-Metering/artifacts/stage6_o2_causal_diagnostic_20260921_v1/engineering_attempt03/O2_RELEASE_APPROVAL.json --execute
```

Fresh root `data/raw/stage6_o2_causal_diagnostic_20260921_v1/O2_C_S17_450_attempt3/`. Use supported elevated execution; do not bypass policies. If it succeeds, stop and hand off for prefix neutrality/clock alignment before interpreting new leader evidence. Current package does not decide U35 cause or resolve O2. Parent owns governance/worklog updates.

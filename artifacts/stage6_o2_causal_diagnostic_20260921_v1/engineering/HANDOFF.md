# O2 C/seed17 450-second diagnostic: static handoff

**Not launched.** The new card is independent of the exhausted TV5/5 card. Exact card SHA-256:
`087852e8bd826c7f6a5c754e4222a0a01ea2631ea830dd41e29a81039d21d353`.

Scope: one headless C/seed17 reproduction0–450, native leader output plus read-only TraCI snapshot0/1/2 and385–430, no behavior setters, no retry. Original compiled network, demand, detectors, C WAUT and urban TLS remain unchanged. Inputs are under `inputs/`; no run root exists yet. End450 is a deliberate horizon change and future demand after450 remains censored.

Files to review:

- `DIAGNOSTIC_CONTRACT.md`: scope, API meanings, time/space uncertainty, resource semantics.
- `O2_DIAGNOSTIC_CARD.json`:172 unique exact file bindings, precise binary/Python/network/argv/env, one-start cap.
- `authorization_provenance.json`: original conditional user instruction and why missing leader evidence meets the condition; no assertion user personally saw this SHA.
- `O2_RELEASE_APPROVAL.template.json`: never executable approval. Parent may create `O2_RELEASE_APPROVAL.json` under existing user authorization only after exact final review.
- `runtime_executor.py`: fail-closed supervisor derived from prior audited wrapper; process group, atomic reservation, hash checks, no retry,50ms observed stop-lines.
- `observer.py`: one SUMO Popen; explicit450 steps; owned listener checks; getters only plus clock/session operations; physical-event immediate stop.
- `static_validation_receipt.json`:58 checks PASS,3 local XSD checks PASS,27 getter dispatch/signature checks PASS,18 recursive schemas bound.
- `offline_test_receipt_revision02.json`:14/14 offline tests PASS, four Python fake processes, zero SUMO/TraCI. Earlier13/14 receipt and fixtures are retained; its failure was argparse AST false positive. A first whitespace-sensitive static comparison failure is also retained in `preparation_history.json` and source history.
- `diagnostic_gate_contract.json`:12 required post-run checks. Technical process success alone does not resolve O2.

Dry-run command (no SUMO start or TraCI connection):

```sh
/Library/Frameworks/Python.framework/Versions/3.13/bin/python3.13 -B \
  /Users/yuhongzhang/Desktop/Masterarbeit-Ramp-Metering/artifacts/stage6_o2_causal_diagnostic_20260921_v1/engineering/runtime_executor.py \
  --card /Users/yuhongzhang/Desktop/Masterarbeit-Ramp-Metering/artifacts/stage6_o2_causal_diagnostic_20260921_v1/engineering/O2_DIAGNOSTIC_CARD.json
```

**After exact independent static review and parent release only**, precise launch command:

```sh
env SUMO_HOME=/Library/Frameworks/EclipseSUMO.framework/Versions/1.26.0/EclipseSUMO/share/sumo \
  /Library/Frameworks/Python.framework/Versions/3.13/bin/python3.13 -B \
  /Users/yuhongzhang/Desktop/Masterarbeit-Ramp-Metering/artifacts/stage6_o2_causal_diagnostic_20260921_v1/engineering/runtime_executor.py \
  --card /Users/yuhongzhang/Desktop/Masterarbeit-Ramp-Metering/artifacts/stage6_o2_causal_diagnostic_20260921_v1/engineering/O2_DIAGNOSTIC_CARD.json \
  --approval /Users/yuhongzhang/Desktop/Masterarbeit-Ramp-Metering/artifacts/stage6_o2_causal_diagnostic_20260921_v1/engineering/O2_RELEASE_APPROVAL.json \
  --execute
```

Use supported elevated execution if sandbox blocks required process/socket behavior; do not work around sandbox limits. Do not call SUMO directly or `traci.start`. `PYTHON*`, `LD_*`, and `DYLD_*` environment injection is rejected. The sole spawned SUMO argv is recorded in the card; it adds only `--remote-port 8819 --num-clients 1` to the bound config.

Run root:
`data/raw/stage6_o2_causal_diagnostic_20260921_v1/O2_C_S17_450_attempt1/`

A claimed root is consumed even on failure; preserve it. No next attempt is authorized.180s/200MB are observed stop-lines, not hard OS quotas, and include the observer and SUMO files. Existing TV task's5 starts/7.03850783398957s/170383856B remain separate, with no transferred credit.

Remaining unknowns: runtime TraCI/backend support has not been live-tested in this package; native/TraCI timestamp correspondence and behavioral neutrality require raw prefix equality; selected leader/foes/link state may still not identify the ultimate braking cause. Cross-branch tail extent uses actual queried lengths and route geometry, not a fabricated blocker ID. No change to registered O2 storage-cross criteria is made. The primary owns state/worklog updates and final reviewer disposition.

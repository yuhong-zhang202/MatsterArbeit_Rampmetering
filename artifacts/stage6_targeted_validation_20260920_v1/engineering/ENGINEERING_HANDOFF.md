# Targeted validation Phase1 engineering handoff

Engineering status: **static package delivered, real SUMO not released**. Confidence High for file/compiled invariants and zero-SUMO scope; runtime program selection, logger neutrality and physical mechanisms remain untested. Formal protocol remains empty. Only parent may complete the exact review/authorization gate.

## Delivered and verified

- Re-read AGENTS, PROJECT_STATE, DECISIONS, EXPERIMENT_PROTOCOL and relevant WORKLOG; prior RV4 is closed/exhausted, specific_obstacle unresolved. New user attachment supplies independent bounded task. No existing inputs/raw/governance/protocol/decision file edited.
- New common CandidateB network adds only ramp_mid traffic-light control and programs A/B/C. `TV_BUILD01` completed once, return0,11.653046334002283s, stderr empty, stdout Success. Network12814bytes, SHA `887c232483f0c68dc024334ff5997250d7d36299ab2744bdcf49d5a314c700ca`. Final build directory15210bytes; PID/process group absent. Network output preserved unchanged.
- 65 compiled checks PASS. All edge/lane geometry, speed, permissions, storage, urban_tls and nonmeter connections unchanged. Meter connection now has tl=ramp_mid/linkIndex0/stateO. This compiled state attribute is not observed red/green behavior.
- 15 runtime XSD checks PASS;52 static input/scope/default checks PASS. All primary scientific inputs differ only selected WAUT startProg after output path labels. Technical OFF fixture only disables native LC output.
- 26 fake-executor tests PASS,18 corrected measurement fixtures PASS. First mixed-chain fixture initially placed U on the internal connector instead of shared lane; initial failure retained. Corrected34-member chain fixture passed with unchanged helper. An initial config-semantic comparison mistakenly retained formatting tails; corrected comparison ignores only formatting, with no input change.
- 118 unique card/source/schema/binary/input bindings verified. Unapproved template fails preflight; no new raw runtime directory exists. New task calls:netconvert1,SUMO0,TraCI0,GUI0.

## Exact entry points

All paths below are within `artifacts/stage6_targeted_validation_20260920_v1/engineering/`.

- `RUNTIME_CARD.json`: SHA `8e54ab7ac73e3192a1db5ea249efbe610e1114d79980166baea83934a6601f4c`.
- `input_manifest.json`: five exact attempts, all inputs/hashes/argv/output paths.
- `RUNTIME_CONTRACT.md` and `gate_contract.json`: fixed14 technical gates, role18ON/17OFF, phase/time/population/native-event and queue rules, physical stop behavior.
- `compiled_audit.json`, `static_receipt.json`, `closeout_verification.json`: static acceptance and exact post-writer accounting.
- `runtime_executor.py`, `executor_test_receipt.json`, `measurement_helpers.py`, `measurement_test_receipt_revision02.json`: executable checks/stop rules and tests.
- `RUNTIME_approval_TEMPLATE.json`: explicitly NOT_APPROVED; actual approval/review receipts absent.
- `resource_budget.json`, `environment_and_sources.json`, `references/source_provenance.json`: resource assumptions, binary/XSD/source version provenance and passenger5m default rationale.

Command shape after reviewer/parent release only:

```sh
SUMO_HOME=/Library/Frameworks/EclipseSUMO.framework/Versions/1.26.0/EclipseSUMO/share/sumo \
.venv/bin/python artifacts/stage6_targeted_validation_20260920_v1/engineering/runtime_executor.py \
  --card /Users/yuhongzhang/Desktop/Masterarbeit-Ramp-Metering/artifacts/stage6_targeted_validation_20260920_v1/engineering/RUNTIME_CARD.json \
  --approval /Users/yuhongzhang/Desktop/Masterarbeit-Ramp-Metering/artifacts/stage6_targeted_validation_20260920_v1/engineering/RUNTIME_user_approval.json \
  --attempt TV_SMOKE_B_LC_ON_S17_attempt1 --execute
```

The child argv is exact SUMO1.26 binary `-c` the attempt's scenario.sumocfg; cwd project root; sanitized env SUMO_HOME, PATH=/usr/bin:/bin, LANG=C, LC_ALL=C and inherited HOME. Supported elevated execution may be needed, as with prior framework binary execution; never bypass sandbox.

Only two B technical fixtures then A/B/Cseed17 are executable, five starts maximum under this card. Each180s/1.5GB and cumulative900s/7.5GB are monitored operational stop-lines, not hard disk guarantees. All old RV4 costs are reported separately, not transferred/reset. Further technical repair or conditional scientific family requires new immutable package/review, preserving all prior attempts. No seed23 or fallback family is silently executable here.

## Reviewer attention and limitations

1. The helper's U candidate means an actually stopped U on shared lane with a stopped R ahead connected through the observed bumper chain. It retains R-U-R mixed ordering and does not require U to be behind every R further upstream. Parent/data/scientific review should resolve any intended stricter interpretation of “upstream of queue tail” before analysis release; no causal claim is made by this primitive.
2. Passenger5m is the version-tag SUMO software default supported by archived source and input audit; it is not empirical or runtime TraCI measured. Downloaded source provenance does not prove reproducible derivation of the installed binary.
3. Full streamed event/episode/identity analysis and O1/O2 gates belong to the separate data/scientific workflow. The helper fixtures alone do not constitute a completed production analysis adapter or scientific acceptance.
4. Actual WAUT phase selection, two-TLS output, stopline movement and native logger neutrality need the reviewed technical fixtures. Additional logging is expected traffic-neutral but not claimed proven before paired output equality.
5. First real collision/teleport/invalid movement is a stop with preserved evidence. No final mechanism interpretation, obstacle closure or formal readiness is issued here.

Safest next step: independent exact-package data/scientific review; then bind separate authorization/review receipts and start only the first technical fixture. Phase1 stops here.

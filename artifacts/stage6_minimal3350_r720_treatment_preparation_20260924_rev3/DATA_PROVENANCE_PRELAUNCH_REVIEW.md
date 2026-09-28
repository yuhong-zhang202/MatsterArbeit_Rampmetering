# Independent data/provenance prelaunch review — MINIMAL3350_R720_DELAYED_S17 REV3

**Disposition:** `BLOCKED_CARD_CONDITION_BINDING` — findings 1/0/0 (Blocker/Major/required Minor). This is not an execution authorization.

## Verified data binding

- Exact card SHA-256: `f151ea300bd236aa30ef0baec9980a2c28b01e1e80bfaa4aa2f080a26934783c`.
- M input: 1,396/1,396 IDs and XML order match REV8 control and the common M manifest. Desired depart, route, type/vType, speedFactor, lane, position and speed mismatches: 0.
- Only added vehicle identities: 192 R (`R_flow.0`–`R_flow.191`) at 540000 through 1495000 ms, every 5000 ms. U and X are explicitly zero.
- qMain 3350.4, seed 17, A_OPEN, `[540,1500)` R window, 1 s step, 2700 s horizon. Treatment network byte hash matches REV8 control. All card/input/source hashes, including locked method, D-008 plan, parent contract, adapter, R source and control review evidence, match.
- SUMO 1.26.0 executable, additional schema and Python executable hashes match the bound runtime. Runner hashes agree across card, manifest, runtime and actual package runner. START request receipt binds the persisted 7,164-byte request and exact SHA-256.
- All 18 unique output roles reconcile exactly to sumocfg outputs plus the additional XML detector/TLS destinations. Every role is below the bound v11 output directory and absent.
- Resource contract agrees across card, runtime and request: 90 s / 75,000,000 bytes, 100 ms polling, overshoot accepted.
- In-memory preview of deterministic runner staging predicts sumocfg 2,759 bytes / SHA-256 `8cab2c806e6584515db0048809bd336cdc3cd723629349abbe863c592759a1d0` and additional XML 3,832 bytes / SHA-256 `195ae5ccc094044905802e98b60c31c46a6644e61eb2ff4c4bdd33cf5fdafadb`. No staged/output files were written during this review; static preflight remains non-launchable while review binding is pending.

## Blocker: release condition not fail-closed

D-008 requires an acceptable 3350.4/R=0 control, specifically `LOW_R_BACKGROUND_ACCEPTABLE`. REV8 does have that disposition and its review hash is referenced in REV3. However, REV3 sets `LOW_R_BACKGROUND_ACCEPTABLE_required_for_release=false`; the dedicated runner enforces that field but does not validate the matched control scientific review hash/disposition in its minimal3350 treatment branch. Thus the adopted entry condition is not explicitly enforced by the exact card/runner pair. The ambiguity is substantive for release provenance, not a raw-input mismatch.

A new exact card/runner revision should separately name the legacy strict normal/high-mobility screen as not required and bind+validate the exploratory control category/hash as required. REV3 should remain blocked and must not be released.

## Limits

This is a prelaunch input/provenance review only; no treatment raw was inspected and no process started. The per-M speedFactor vector is copied from the prior full-network seed17 run and materialized for matching; it is not an independent U=X=0 RNG realization. The witness contract D-005 was originally adopted for the 3199 pair; D-008 adopts the conditional minimal3350 sequence and unchanged witness rules, so scientific review must confirm its scope for this exact arm.

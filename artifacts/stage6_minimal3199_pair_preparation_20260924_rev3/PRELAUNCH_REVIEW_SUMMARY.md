# MINIMAL3199 U=X=0 pair — control prelaunch summary

**Disposition:** `MINIMAL3199_CTRL_PRELAUNCH_READY_AWAITING_AUTHORIZATION`  
**Scope:** Preparation and prelaunch review only. No SUMO, TraCI or netconvert start.

## Current exact-card drafts

- Control: `scripts/stage6/minimal3199/prepared_rev3/MINIMAL3199_CTRL_S17_CARD_DRAFT_NOT_AUTHORIZED_REV3.json` — SHA-256 `e64e88c8fa40cb22da3f8c02a8e9fca1b9f284d9df4452564fa6dda135ea116f`.
- Treatment draft, unreleased: `scripts/stage6/minimal3199/prepared_rev3/MINIMAL3199_R720_DELAYED_S17_CARD_DRAFT_NOT_AUTHORIZED_REV3.json` — SHA-256 `f717a9e8cac24de991c57dab3dfe234ee369dab195f8c61529a7bf5a7ac0b9e8`.
- Input manifest SHA-256: `6c4ea95baf16fa339e9fcc0fe1060daae9cb06f5e0d52de8ca779ff146471d40`.
- Package receipt SHA-256: `28addb6e2c26ee2de3810f88fb8896134393793e820874da61ebdbef316b1f44`.

## Static pair and binding

The fail-closed checker confirms exact M match **1333/1333** across ID, desired depart in integer milliseconds, full route, vType, speedFactor and all bound depart attributes. Both route files are globally sorted by `(depart_ms,id)`. Control has no R records and manifest explicitly records R/U/X as `PASS_ZERO`. Treatment adds only `R_flow.0–191`, scheduled at 5 s intervals from 540 through 1495 s. U and X are explicitly `PASS_ZERO` in each arm; missing entries fail closed.

Runtime, input, network, plan, runner, validation adapter/test source, output-role and card hashes are cross-bound. Both R02 calls returned `PREFLIGHT_PASS_NO_PROCESS_STARTED`; a launch check rejected the draft cards with `CARD_NOT_EXACTLY_AUTHORIZED`. Each arm has a distinct absent output path. Resource proposals are control 90 s / 60,000,000 bytes and treatment 90 s / 75,000,000 bytes, with 100 ms polling and possible slight overshoot; neither proposal authorizes use.

## Independent reviews

| Review | Disposition | Findings | Scope note |
|---|---|---:|---|
| Engineering (`simulation_engineer`) | PASS | No blocker or required issue reported | Static binding passes. Strict XML rejection branches are implemented and code-reviewed, but have no dedicated adversarial XML regression fixture in this 20-test suite. |
| Data/provenance (`data_analyst`) | PASS | Blocker/Major/required Minor 0/0/0 | 20/20 tests pass; 14/14 receipt hashes and current source/runner/card/runtime/input bindings independently recomputed. |
| Scientific (`scientific_reviewer`) | `PASS_BOUNDED_CONTROL_INPUT_ALIGNMENT` | Blocker/Major/required Minor 0/0/0 | High confidence for static input/design alignment. A control alone cannot establish a witness or release treatment. |

Engineering and data reviewers found static M/R/U/X and provenance gates satisfied. The scientific review is limited to this control's alignment with the approved modular existence-test plan. It does not claim that the future run will be evaluable, does not make a clean-normal-baseline claim, and does not authorize a start. The treatment remains a draft and is not released.

## Execution boundary

Control is prepared for a **separate one-time user authorization**. No exact FINAL card exists. The treatment, second qMain, other seeds and B/C remain outside this preparation's release. Geometry, scientific demand values, vehicle behavior, classifier, thresholds, formal protocol and previously reviewed raw are unchanged.

SUMO starts = 0; TraCI starts = 0; netconvert starts = 0.

# Exploratory validation closeout report

Date: 2026-09-13  
Stages covered: Stage 1–5, with Stage 2–4 already closed  
Classification: exploratory technical and scientific assessment; not a formal experiment  
Current gate: T53 complete; T54 user acceptance pending

```text
assessment_work: complete
assessment_completion: pending_user_acceptance_T54
design_readiness: specific_obstacle
preliminary_ready: false
formal_experiment_status: not_started
new_simulation_in_stage5: 0
```

## 1. Decision-facing conclusion

The prescribed exploratory assessment work is complete. The current synthetic scenario can measure the declared mainline, ramp and urban flow and stock quantities, and it shows stopped R/U exposure on the shared urban approach. It does not yet support the intended formal study of the trade-off between freeway protection and urban-side spillback.

The reason is specific. Under the fixed Stage 4 scaffold, qRamp=720, qUrban=360 and qX=180 veh/h, both seeds at qMain=3500 show non-zero ramp first-downstream passage in A=[0,1500), while both seeds at qMain=3650 show zero A-window ramp passage. The preregistered local mainline impairment signature, EJMI, is not identified at either point. Within the registered points, the scenario therefore loses demand-window ramp passage before it presents the registered protectable mainline-side state. This supports `specific_obstacle`; it does not establish why the pattern occurs. [EV-S4-MATRIX; EV-S4-EJMI; EV-S4-DECISION; EV-S4-ORACLE; EV-S4-SCI]

The recommended Stage 5 closeout is consequently:

```text
assessment_completion: completed, after explicit T54 user acceptance
design_readiness: specific_obstacle
preliminary_ready: false
```

Confidence in completion of the prescribed assessment: **High**. Confidence in the bounded `specific_obstacle` classification: **High**. Suitability of any redesigned scenario and the structural cause of the obstacle: **Unknown**.

## 2. What the exploration established

### Q1 — observability: `supported` within scope

The registered observation domain has complete metadata and accounting for the required M/R/U flow, stock and stopped-state quantities: Stage 3 retained 128/128 required outputs, 64/64 endpoints, 21,600/21,600 FCD labels and 4,320/4,320 E1 intervals; Stage 4 retained 64/64 class-endpoint units and the complete registered observation contract. [EV-S3-Q/Q1; EV-S3-IV; EV-S4-SNAPSHOT]

The support is local to the declared synthetic topology. Mainline vehicles actually enter approximately 0.1–287 m from the merge, so the data do not describe a realistic long upstream freeway feeder. The old upstream E1 is affected by insertion, ordinary E1 lacks vehicle identities, and a validated continuous outside-waiting curve is unavailable. [EV-S3-REPORT §4; EV-S3-Q/Q1]

### Q2 — freeway-side impairment: `not_identified`

Stage 2/3 internal M-only A-window speeds remain approximately 30.02–31.71 m/s while measured flow tracks requested mainline input. All four Stage 4 qMain=3500/3650 candidates fail the registered EJMI sufficient signature. [EV-S2-G2; EV-S3-Q/Q2; EV-S4-EJMI]

This does not show that freeway impairment is absent. There is no approved Breakdown or Capacity Drop definition, and the local detector, near-merge insertion and untested downstream/lane-changing mechanisms do not establish the state of a realistic upstream freeway. [EV-S4-SCI; EV-S4-REPORT §4]

### Q3 — urban-side exposure: `supported` within scope

All eight Stage 3 runs show stopped R and U vehicles on the shared approach at common 1 Hz labels, totalling 7,120 independently reconstructed sampled seconds. R propagation order is observed in 8/8 runs, and R/U endpoint accounting is complete. [EV-S3-Q/Q3; EV-S3-IV]

This is evidence of spatial and temporal exposure. It does not identify the additional U loss caused by R spillback because signal red phases, downstream supply and ordinary urban queuing remain alternative explanations. [EV-S3-REPORT §6; EV-S4-SCI]

### Q4 — same-scenario trade-off basis: `not_identified`

The registered q3500-to-q3650 result identifies passage-to-exclusion for R before EJMI is identified. Q3 is observable, but Q2 is not identified; the two sides therefore cannot yet be connected into the intended controllable trade-off in this scenario. [EV-S4-MATRIX; EV-S4-DECISION; EV-S4-ORACLE]

The result is not a contradiction of all possible scenario designs. It covers the current structure, the registered demand points and two seeds only. [EV-S4-SCI]

## 3. Required outputs and completion gates

T50 verified the available O1–O6 inventory and T52 handover; this T53 report completes the narrative part of O6. O1, O2, O3 and O5 are complete; O4 is complete with the `specific_obstacle` result; O6 now contains the complete 22-item machine-readable handover and this report. The inventory is `data/processed/exploratory_validation_closeout_20260913_v1/artifact_inventory.csv`. [EV-S5-T50]

G01–G08 each have a recorded result and pass their stated completion test. Passing G04 and G07 means that diagnosis and intended-use assessment were completed; it does not turn `not_identified` findings into support. Passing G08 means the handover is complete; it does not make the scenario `preliminary_ready`. The gate register is `data/processed/exploratory_validation_closeout_20260913_v1/gate_inventory.csv`. [EV-S5-T50]

Key denominators are:

| Check | Result |
| --- | --- |
| Required outputs | 6/6 |
| Completion gates with result | 8/8 |
| Stage 3 run-question evidence units | 40/40 |
| Stage 3 input contrasts / seed units / sensitivity values / time series | 6/6; 8/8; 96/96; 48/48 |
| Stage 4 logical terminal runs / used evidence manifests | 10/10; 8/8 |
| Stage 4 archived files / endpoint units / adjacent comparisons | 116/116; 64/64; 6/6 |
| Stage 5 handover classes | 22/22 |
| Open analysis Blocker / Major / required Minor | 0 / 0 / 0 |

[EV-S3-REPORT §§3,5; EV-S4-SNAPSHOT; EV-S4-SCI; EV-S5-T50; EV-S5-T51]

## 4. Method and parameter handover

The 22-item register is `data/processed/exploratory_validation_closeout_20260913_v1/method_handover_draft.csv`. Every item has a current value or explicit unknown, evidence ID, domain, qualification, reason, owner and next action. No formal value has been selected. [EV-S5-T52]

| Qualification | Count | Meaning for Stage 6 |
| --- | ---: | --- |
| `reuse_with_scope` | 1 | Carry forward the E1/E2/FCD mapping method only within unchanged topology; remap and revalidate after topology changes. |
| `candidate_requires_validation` | 8 | Reproducible exploratory choices may be proposed, but require validation before protocol freeze. |
| `requires_scientific_decision` | 11 | The research objective, estimand or acceptance rule must determine the value. |
| `not_available_or_ineligible` | 2 | Current evidence cannot supply the value. |

The formal experiment still lacks selected freeway, ramp, urban and system estimands; an approved Breakdown/Capacity Drop definition; an effective and acceptable ramp-storage boundary; demand range and duration; warm-up/window/clearance rules; seed precision; a causal U-loss comparison; controller settings; and a sweet-spot or robustness decision rule. [EV-S5-T52; EV-PROTOCOL-EMPTY]

## 5. What must not be claimed

The exploration did not establish:

- a validated formal scenario or a frozen protocol;
- absence or presence of freeway Breakdown, Capacity Drop or capacity threshold;
- the structural cause of ramp exclusion;
- causal additional U loss from ramp spillback;
- controller benefit, a sweet spot or statistical robustness;
- suitability of the two exploratory seeds as a formal repetition plan.

[EV-S4-SCI; EV-S5-T51]

No smoke, exploratory or targeted-validation output is eligible as thesis evidence. The formal protocol remains empty and unfrozen, and no formal experiment has started. [EV-PROTOCOL-EMPTY; EV-PROJECT-STATE]

## 6. Stage 6 boundary

After T54 acceptance, Stage 6 may draft a constrained formal-design proposal and a Robert review package. It may develop bounded alternatives for addressing the identified obstacle, including extending the freeway feeder/entry design or proposing a narrower scientific use for user and Robert review. No alternative is selected by this Stage 5 closeout. The draft must carry all 22 handover qualifications forward and label every numeric value as evidence-supported, candidate or research choice. [EV-S5-T52; EV-PLAN §10]

Stage 6 may design the study; it does not authorize controller implementation, a pilot, a formal simulation, protocol freeze or communication with Robert. Sending material remains a separate user decision. [EV-PLAN §§10,12]

## 7. Evidence index

| ID | Source |
| --- | --- |
| EV-PLAN | `docs/EXPLORATORY_VALIDATION_COMPLETION_PLAN.md` |
| EV-PROJECT-STATE | `docs/PROJECT_STATE.md` |
| EV-PROTOCOL-EMPTY | `docs/EXPERIMENT_PROTOCOL.md` |
| EV-S2-G2 | `docs/STAGE2_COMPLETION_REPORT.md` |
| EV-S3-Q | `data/processed/stage3_baseline_diagnostic_20260912_v2/analysis_review/revision_06/claim_evidence.csv`, SHA-256 `e28ffdbb0411a5579fd4cbfcee405057f4610683b1be3d79ef37a39553ac7c2a` |
| EV-S3-IV | `data/processed/stage3_baseline_diagnostic_20260912_v2/verification/T33_T34_independent_v3.json` |
| EV-S3-REPORT | `docs/STAGE3_BASELINE_DIAGNOSTIC_REPORT.md` |
| EV-S4-SNAPSHOT | `data/processed/stage4_qmain_sequential_20260912_v1/final_evidence_ledger_snapshot.json`, SHA-256 `f589c905067887536037fe6fe045438e8a1588cbf3246dcc50b573facecb4516` |
| EV-S4-MATRIX | `results/tables/stage4_qmain_sequential_20260912_v1/final/revision_03/final_run_matrix.csv` |
| EV-S4-EJMI | `results/tables/stage4_qmain_sequential_20260912_v1/final/revision_03/final_ejmi_envelope_checks.csv` |
| EV-S4-DECISION | `data/processed/stage4_qmain_sequential_20260912_v1/analysis/final/revision_04/registered_final_decision.json`, SHA-256 `c87884325f7f1a0e5dfdd18a01dd6c244b00fb85a2b41818fc65e6c4ba4d0080` |
| EV-S4-ORACLE | `data/processed/stage4_qmain_sequential_20260912_v1/analysis/final/revision_04/snapshot_bound_independent_oracle.json`, SHA-256 `74beffc5ea5efde27649cb6204f275429309d4a6eeb2bd3b55532bdb29571ace` |
| EV-S4-SCI | `data/processed/stage4_qmain_sequential_20260912_v1/verification/T43_final_scientific_review_record_20260913.json`, SHA-256 `b73513dca5a0b535a8910ff4c779f410a13f0b165391b503b6e70c0475469726` |
| EV-S4-REPORT | `docs/STAGE4_TARGETED_VALIDATION_REPORT.md` |
| EV-S5-T50 | `data/processed/exploratory_validation_closeout_20260913_v1/artifact_inventory.csv`; `gate_inventory.csv`; `inventory_verification_revision_02.json` |
| EV-S5-T51 | `data/processed/exploratory_validation_closeout_20260913_v1/T51_scientific_review_record_revision_02.json`, SHA-256 `c5aafabf28afaf5fbf9c919226cd9852a2730667236907ec3750539c36ae7f42` |
| EV-S5-T52 | `data/processed/exploratory_validation_closeout_20260913_v1/method_handover_draft.csv` |

## 8. Specialist review

- Data review: T50/T52 passed with 15/15 path-hash checks after adding T51/T53, 3/3 byte-identical table mirrors, 22/22 classified handover items and zero open data findings.
- Scientific review: Q1/Q3 supported within scope; Q2/Q4 not identified; core question-level unknowns=2; open Blocker/Major/required Minor=0; `specific_obstacle` is the supported readiness classification.
- Simulation engineering: Stage 4 final evidence snapshot and operational closure passed; Stage 5 added no SUMO, netconvert, TraCI or GUI activity.

T54 user acceptance is the only remaining Stage 5 gate.

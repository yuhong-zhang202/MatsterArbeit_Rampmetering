# Data / lifecycle post-run review — MINIMAL3350_CTRL_S17 REV8

**Disposition:** `PASS_DATA_LIFECYCLE`  
**Data-side branch evidence:** `LOW_R_BACKGROUND_ACCEPTABLE`; independent scientific post-run review remains required.

## Binding and lifecycle

- FINAL card SHA-256: `15544478e8e7ced98b12673bec65cfe646b1f73e9e471ed501ddee052306bbfd`
- Output manifest SHA-256: `48456bb607b4e4679dd13274696c60ab7f5ae020aa6ecbf2462110e1fdcd752f`
- All 25 inventory files match bound SHA-256 and byte size.
- 1,396 planned M identities reconcile exactly to 1,396 vehroute and tripinfo identities. Route, type and speedFactor mismatches: 0.
- SUMO summary: loaded/inserted/ended/arrived = 1,396; running/waiting/vaporized/discarded = 0; collisions/teleports = 0. No unfinished M. Actual departures span 0–1499 s; arrival 65–1570 s; departDelay 0–1 s (median 0.5 s). Desired departures remain bound to the integer SUMOTime schedule in the common M manifest (1074 ms offset).
- R/U/X are explicit planned zeros and their vehicle classes are absent from outputs, as expected.

## Exposure and classifier

FCD covers every one-second label from 0 through 2699, with 1,396 unique M IDs, 102,444 M samples and no duplicate time/ID keys. All M samples use the bound mainline/through internal-lane whitelist. During [720,1440), 677 unique M vehicles and 7,096 samples appear in the merge core. All 1,396 M vehicles are observed at E1 stations upstream (1300), downstream-near (20) and downstream-far (200). All required E1 files have 90 30-second intervals.

The locked P/S/L results are all `NO_QUALIFYING_EVENT`. Candidate A has no adjacent-cell S confirmation. Candidate C has 28 single-bin early-warning flags, retained in the machine report; they do not qualify as State 1 and none form same-cell persistence satisfying L. The flags occur across cells and times, including several adjacent-cell clusters near the merge. These remain warnings and do not establish clean high-mobility operation.

## Artifact and measurement checks

No mainline direct-red TLS records are present. Ramp-storage and shared-boundary E2 outputs contain 90 complete intervals each and remain empty, consistent with R=U=X=0. The queue-export file has 2,700 labels but only an empty `<lanes>` element per label, so queue morphology is unavailable from that export. The three M E1 passage stations each account for all 1,396 vehicles, and the locked compiled lane map is consistent with observed FCD lanes. No insertion loss, unfinished traffic, unexplained lane mapping, or P/S/L measurement gap was found.

## Provenance limitations

Per-M speedFactors were copied from the archived qMain=3350.4, seed17 full-network vehroute where U/X were nonzero. They are explicitly materialized and reconcile 100% here; this supports common M identity/attribute matching without claiming a separately generated U=X=0 RNG realization. This is one fixed seed/vector. The old strict normal/high-mobility screen remains FAIL and is unchanged. No raw files were modified.

## Reproducible outputs

- `data/processed/stage6_minimal3350_ctrl_postrun_20260924_v2/analyze_minimal3350_control.py`
- `data/processed/stage6_minimal3350_ctrl_postrun_20260924_v2/data_lifecycle_classifier_report.json`
- `data/processed/stage6_minimal3350_ctrl_postrun_20260924_v2/cell_bin_metrics.csv`

This review evaluates data completeness and the approved exploratory low-R control contract. The independent scientific reviewer retains final disposition authority.

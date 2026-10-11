# Initial read-only scientific findings — retained V1

Review of the frozen engineering/data source and partial tracked-tree export found two Minor reporting defects; no material schedule/guard/auth issue was identified at this checkpoint. Final disposition remains pending controlled correction.

1. `independent_selfloop_review.py` verifies 29 bound files with an assertion, but reuses `count` in the vehicle-group loop. The final X group has150 vehicles, so `engineering_files` incorrectly reports150 in both originalV1 and exportV1 outputs. Actual file verification is29. PreserveV1 source/results/receipts/bindings; introduceV2 with separate binding/vehicle counts. One corrected public-checker execution is sufficient; no native/test-suite/full-export rerun required.
2. `OFFICIAL_SOURCE_RECEIPT_R1.json` contains5 excerpts (2 MSTrafficLightLogic +2 MSSimpleTrafficLightLogic +1 NLJunctionControlBuilder), and the machine result correctly says5. The V1 data/main report sayssix. Correct current text using versioned evidence and retain old drafts. All3official source files and relevant init/successor/call-site evidence are present.

The scientific reviewer is read-only. Parent/data owner perform controlled corrections; reviewer will independently read back V2. No SUMO or safety/service qualification is authorized by this finding.

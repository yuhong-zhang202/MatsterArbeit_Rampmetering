# Independent scientific prelaunch review — MINIMAL3350 control REV2

**Disposition:** `BLOCKED` — Blocker / Major / required Minor = 1 / 0 / 0; confidence High.

The card binds and monitors `<repo>/data/raw/stage6_minimal3350_ux0_20260924_v2/MINIMAL3350_CTRL_S17/outputs`. The actual `scenario.sumocfg` and `scenario.add.xml` configure `<repo>/data/raw/data/raw/stage6_minimal3350_ux0_20260924_v2/MINIMAL3350_CTRL_S17/outputs`. SUMO would therefore write outputs outside the bound and monitored directory. The absent-path and 90 s / 60,000,000-byte guards would not cover the configured outputs. Hashes match their manifests, but do not cure the path mismatch. **Do not launch this card.**

The minimal fix is a new immutable exact-card revision with one unique output path shared exactly by the config, additional file, card, runner and output-role manifest. Verify every resolved output path, then repeat engineering, data/provenance and scientific reviews.

Apart from this blocker, the scientific reviewer accepted the explicitly materialized M vector for this single conditional exploratory contrast, provided the future treatment reuses the exact common-M manifest. The vector is sourced from prior qMain3350.4 seed17 full-network raw with U/X present; it is not evidence of a representative or independent U=X=0 RNG realization.

No process was started and no traffic raw was produced. Full hash and review provenance are in `SCIENTIFIC_PRELAUNCH_REVIEW_BLOCKED_REV1.json`.

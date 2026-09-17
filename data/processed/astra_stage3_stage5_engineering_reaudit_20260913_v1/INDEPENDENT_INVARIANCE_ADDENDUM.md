# Independent fixed-archive invariance closure

Date: 2026-09-13. This supplements, without changing, `ENGINEERING_REAUDIT_REPORT.md` SHA-256 `c832319364033e39cad624219700fa099bd8ebd9b8c93a32c930e7e474bd37d4`.

The data analyst completed the pending repaired-code comparison: **8/8 accepted archives and 96/96 output files passed**. The primary agent reports that the scientific reviewer also independently checked those 96 files. These are externally performed checks; they are not additional engineering test executions.

Source: `data/processed/astra_stage3_stage5_reaudit_20260913_v1/repaired_invariance.json`, supplied SHA-256 `17588ed3f6c790442b11f2986122dbad470d8883f162ccc2bb5bf7e50d2550cc`. The engineer read its passing status and binding fields: repaired production `6558f971bc713397e26a41fd4b2b4a71255a38ff7b6122d77df6056b88b6b8f6`; audit-only ledger `22bc5506f0b9df2976b2dc7100fde7ab9729e469836cf7d8d8a0bd5ef2316b38`; original measurement contract `e9c8a6c026b22faedb51902d79cc3952333a3e86ea963b0c06083f0889b81fd7`.

The recorded manifest difference is limited to output paths, with other manifest metadata matching historical revision_02 and no historical file rewritten. New SUMO and netconvert starts remain zero. The four engineering repairs therefore do not require historical numerical result replacement or new simulation. Confidence: High within these fixed archives. Broader future-input exhaustiveness and scientific design suitability are not implied.

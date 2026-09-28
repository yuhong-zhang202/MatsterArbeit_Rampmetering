# Review artifact status — `MINIMAL3199_CTRL_S17_TECH_RETRY1`

The current exact-card launch gate is the R02 receipt set listed below, bound by `FINAL_PRELAUNCH_REVIEW_BINDING.json` to card SHA-256 `027d7dc7b74561648ec6c0799abd64a99b7fb746273d1ecb78905c00c082c672`:

- `FINAL_ENGINEERING_PRELAUNCH_REVIEW.json`
- `FINAL_DATA_PROVENANCE_PRELAUNCH_REVIEW.json`
- `FINAL_SCIENTIFIC_PRELAUNCH_REVIEW.json`
- `FINAL_PRELAUNCH_REVIEW_BINDING.json`

The earlier `PROVENANCE_RECEIPT.json`, `FINAL_PRELAUNCH_REVIEW.md`, and `FINAL_PRELAUNCH_REVIEW_RECEIPT.json` are preserved historical snapshots for the DRAFT card (`5f9c8f17476296cab5b30c59b9dd60bda1f4b066b956a897bbd53be43a50be22`). They describe the state before the one-start authorization and before staged files were materialized. They are superseded for this FINAL launch gate and must not be used to represent the current card or staged-output status.

`FINAL_ENGINEERING_PRELAUNCH_REVIEW_REV0_HOLD.json` preserves the earlier hold record and its findings. The active engineering receipt is the current `FINAL_ENGINEERING_PRELAUNCH_REVIEW.json`, which binds the current FINAL card and current manifest after resolution.

The rev3 source prelaunch receipt is retained unchanged as historical input/design provenance. Its embedded runner hash belongs to that earlier review and is not the current execution runner binding; the current runner is independently bound by the FINAL card, execution manifest, FINAL runtime sidecar, and current engineering review.

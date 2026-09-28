# Engineering post-run review — MINIMAL3199 R720 treatment REV2

- **Disposition:** `PASS_ENGINEERING_POSTRUN`; Blocker/Major/required Minor = `0/0/0`.
- **Exact card:** `f3d7d03e0b521d330a6ccc07d807bd88149ce4eb424e3f3895f917e083234b5e`.
- **Durable execution evidence:** one consumed reservation; Guardian PID `9492`, simulator PID/PGID `9493/9493`; status `PROCESS_EXITED`, exit `0`, runtime `3.165857` s; stop reason `None`; retry disabled. SUMO log records end at 2700.00 s.
- **Resource check:** payload `21151489` bytes against 75,000,000; whole output directory `21158799` bytes. Wall time 3.165857 s against 90 s. Neither trigger fired.
- **Output inventory:** `18/18` bound output roles and `7` support files; all listed sizes/SHA-256 values independently match. On disk `27` files including output manifest and execution receipt; no unexplained file. All 18 XML roles parse and have the expected root element.
- **Staging provenance:** deterministic source-to-run output rewrite reproduces the stored config and additional XML byte-for-byte, including 8 output-root substitutions and 1 additional-file path substitution in sumocfg and 12 output-root substitutions in additional XML.
- **START request provenance:** persisted request hash, sidecar card hash, and FINAL REV2 card hash match. The immutable sidecar records `PERSISTED_UNSENT` at persistence time; the later single dispatch is independently evidenced by reservation/execution receipts.
- **Integrity:** output manifest hash and execution receipt hash agree with reservation. Input/runtime/runner/staging hashes remain bound to the final card. Raw files were not modified.
- **Scope boundary:** This is engineering integrity only. No lifecycle or traffic analysis, classifier result, or scientific interpretation was performed. No process was started for this review.

Full hash inventory and check booleans are in `ENGINEERING_POSTRUN_REVIEW_REV1.json`.

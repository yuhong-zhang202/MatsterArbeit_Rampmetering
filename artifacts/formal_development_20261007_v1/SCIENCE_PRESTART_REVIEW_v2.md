# Pre-start scientific review — FIX01 / v2

Date: 2026-10-07. Reviewer: project scientific_reviewer, read-only. Status: PASS_FOR_DEVELOPMENT_EXECUTION for the first OPEN only, after the primary release.

Exact run: `DEV_M3600_R900_S17_OPEN_A02`. Card SHA-256: `43cac63df671c4c69b4de278b5ac50f2b3f834906a8a412a915a52a9d0b40cfb`. Parameter SHA-256: `31f439c1a83f724259d7a74a382b3d03b6cb82378ec145b85431739655ca07f3`.

The v1 startup interface blocker is closed. The card and resource contract both bind60s, and `validate_worker_card` checks the required fields before TraCI import or Popen. Ten offline tests include a real worker invocation with missing startup field and mocked Popen, proving no process start for that defect. The current source hashes and new card match; initial A01 cards and source provenance remain archived. Traffic parameters and behavior definitions did not change.

The same-parameter design-level review remains applicable to the S17 controls, but their actual release waits for OPEN equivalence and independent data checks. This review does not prove successful traffic execution, measurement completeness or policy effectiveness, and does not authorize formal simulations. No simulation was run by the reviewer.

The primary agent adopts the registered180s/300MB per-attempt,4GB new-raw and5GB free-reserve envelope under D-019. The parameter file is copied byte-exact into `PINNED_PARAMETER_CONTRACT.json` before any new traffic result. The one-run release is `RELEASE_OPEN_S17_R900_A02.json`.

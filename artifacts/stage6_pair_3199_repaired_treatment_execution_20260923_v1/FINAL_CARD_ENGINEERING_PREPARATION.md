# FINAL-card engineering preparation — repaired v5 treatment

**Status: exact one-start user authorization is present; do not launch until the fresh exact-card engineering, data/provenance, and scientific reviews pass and the R02 review-binding sidecar is verified.** This task did not launch, reserve, or consume the attempt.

- Scenario: `PAIR_3199_R720_DELAYED_S17`; run/attempt ID: `PAIR3199_R720_DELAYED_S17_REPAIRED_V5_ATTEMPT1`; execution UUID: `b095cce4-baba-4c40-aa79-08b5e58b9ce1`.
- Exact FINAL card SHA-256: `0801dc1e15ade92babe33640d521ba831174210a200b9e5a66aaeb3bd472e0ef`. Runtime sidecar SHA-256: `4978450c6dd83f37377d1f1a454ba35d5944e4d7a0ed353ed5d43906793b4053`. R02 runner SHA-256: `0961912a46464eb9757ab245c26577e8f1de0985534f34db04a41a4dac45f9c8`.
- Card records the current user authorization for exactly one repaired treatment start at 90 s / 75,000,000 bytes, 100 ms polling with accepted slight overshoot; retries=0. The prior D-006 card/output/reservation remain preserved and consumed, with no shared path.
- V5 demand is byte-identical to the reviewed treatment demand. Static invariant checker passes all 1,558/1,558 common M/U/X full records and 192 treatment-only R IDs. This is input binding only, not future trajectory equivalence.
- Fresh output path `data/raw/stage6_bounded_pair_repaired_20260923_v2/PAIR3199_R720_DELAYED_S17_REPAIRED_V5_ATTEMPT1/outputs` and per-attempt consumption directory are distinct; neither output nor reservation exists.
- R02 exact binding recognizes the unique attempt ID and routes launcher, Guardian, output, and reservation to its exact paths. Read-only preflight status `PREFLIGHT_PASS_NO_PROCESS_STARTED` with `launch_authorized=True` and `launchable_now=False`. It consumed no slot. The review gate reports `WAITING_FOR_REQUIRED_REVIEWS`.
- Runner launch is fail-closed until three exact-card JSON review receipts exist at the paths in the card, each with `status=PASS_PRELAUNCH`, `card_sha256` equal to this FINAL card hash, and findings `blocker/major/required_minor=0/0/0`; then `FINAL_PRELAUNCH_REVIEW_BINDING.json` must bind those three receipt hashes and the exact card hash. The immutable card remains unchanged after reviews.
- R02 tests: 24/24 PASS; includes authorized unique-attempt preflight, refusal of stale draft runner hash, exact-card review-gate/sidecar matching, legacy mapping regression, and no reservation/output creation. Python compilation and `git diff --check` pass.
- When the parent confirms reviews and requests the already-authorized execution step, the exact invocation is:

```sh
.venv/bin/python artifacts/stage6_ramp_induced_validation_20260922_v1/r02_single_start/runner.py launch --repo "$PWD" \
  --card artifacts/stage6_pair_3199_repaired_treatment_execution_20260923_v1/PAIR3199_R720_DELAYED_S17_REPAIRED_V5_ATTEMPT1_CARD_FINAL.json \
  --approved-card-sha256 0801dc1e15ade92babe33640d521ba831174210a200b9e5a66aaeb3bd472e0ef
```

No SUMO, TraCI, or netconvert was run in this preparation.

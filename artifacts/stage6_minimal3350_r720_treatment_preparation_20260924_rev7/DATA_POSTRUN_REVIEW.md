# Data/lifecycle post-run review — MINIMAL3350 R720 REV7

**Data-side disposition: `NO_WITNESS`**, pending the independent scientific post-run disposition. Treatment/control card SHA-256: `d610c5c47c440014a3b8254b36de8d93a48c5d32be928746b93f50003ebcb125` / `15544478e8e7ced98b12673bec65cfe646b1f73e9e471ed501ddee052306bbfd`. Both raw manifests pass (25 treatment and 25 control entries); raw is unchanged.

## Ordered gates

1. **Lifecycle:** M=1,396/1,396 in both arms; treatment R=192/192; U=X=0 explicitly; no unfinished vehicles. FCD covers 2,700 frames (0–2699 s) and E1 has 90 intervals per role.
2. **Pre-R M match:** PASS over `[0,540)`: 34,491 vehicle-second records per arm, zero missing keys and zero tuple differences.
3. **Actual R exposure:** first actual departure 540 s; first through-lane entry 582 s; unique entries in bins 570–600 / 600–630 / 630–660 are 4 / 5 / 6. T3 confirms at 660 s, within the 720 s bound.
4. **Outcome:** first M tuple divergence occurs at 584 s, after R through-lane entry. Locked P/S qualifying events=0 in both arms; Candidate A=0. Candidate C warnings (28 control, 65 treatment overall) and isolated low bins are retained; treatment has 28 core-cell C bins in `[720,1440)` versus 0 control, but these do not qualify as sustained State1. Result: `NO_WITNESS`.

## Alternatives and limits

All vehicles arrived; downstream E1 passage is present; ramp-mid TLS stayed green; no direct mainline red record. `queues.xml` has 2,700 frames but empty lane arrays, so queue morphology is unavailable. Upstream two-lane E1 totals 1,397 in both arms versus 1,396 planned M; E1 has no identity attribution, so the +1 remains unresolved. Historical strict high-mobility screen remains FAIL; Candidate C warnings remain. The paired M speedFactor vector originates in a prior full-network run, so this confirms within-pair matching, not independent U=X=0 randomization. Single seed/vector only. This exploratory negative does not show that ramp-induced breakdown is impossible. Detailed hashes and counts are in `DATA_POSTRUN_REVIEW.json`.

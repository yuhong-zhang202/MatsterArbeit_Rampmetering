# Independent scientific prelaunch review — E1 R900 technical retry 2

- **Disposition:** PASS for this exact attempt
- **Findings:** Blocker / Major / required Minor = 0 / 0 / 0
- **Confidence:** High for condition continuity; Moderate for cross-rate exposure interpretation
- **Run:** `MINIMAL3350_E1_R900_DELAYED_S17_TECH_RETRY2`
- **Card SHA-256:** `cea374f60db487ce9b4bd0c5f45ed28996b298a710af2da33aca6ae9f3bae380`

The independent reviewer confirmed the approved E1 condition is preserved: qMain 3350.4, seed 17, U=X=0, A_OPEN, delayed R900 over `[540,1500)`, 240 planned R vehicles, and the same 1,396-vehicle M vector. Demand, network, common-M manifest, R vector and witness-contract bindings are unchanged. Updated staging/output references are technical-only, with nested closure and revision-local output paths supported by engineering and data review.

REV18 failed before Guardian/SUMO spawn and produced no traffic raw; it has a separate consumed reservation. REV19 uses a new attempt identity and absent v19 output path. The single-start resource contract is 120 s / 100,000,000 bytes / 100 ms polling, with no automatic retry.

**Retained caveat:** The 192 shared R identities have 0/192 speedFactor matches to the R720 vector. This does not invalidate the R900-versus-R0 comparison but limits attributing any later R900-versus-R720 exposure difference solely to nominal qRamp.

This review applies only to this exact attempt. No outcome or post-run result was inspected.

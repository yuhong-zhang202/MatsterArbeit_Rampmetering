# Independent scientific post-run review — PAIR_3199_R720_DELAYED_S17

**Contract outcome: `NOT_EVALUABLE`**  
**Scientific review disposition:** `NOT_EVALUABLE` — Blocker/Major/required Minor = **0/1/0**  
**Confidence:** High for the contract-based disposition; Moderate for the underlying traffic interpretation.

## Exact scope and provenance

The review concerns the single user-authorized run `PAIR_3199_R720_DELAYED_S17`, FINAL_REV1 card SHA-256 `08160a2ad225ee9fcc2abcc11d509a88ecf554252f1fb17e35dc69b9404351d4`, under the adopted Stage 6 exploratory witness contract SHA-256 `958890a7dd017110787a85d77ebfa3e6dac2b7d862f0fd91f6bafb7cf1738d9a`. The treatment execution capture is SHA-256 `00e061736a21c3031b476b2e9c0c1bcee2b669179e48bb375778c070d5f56374`; execution receipt `7d77da828ca962178432150bccf26ea7922d59428b31eda564ad4c3c64628d5a`; raw output manifest `92dbe5627f8afbfe26f50bc8d62207ca9a9ed579c6f707481079d8ad795228dd`. The independently reviewed data report is SHA-256 `54e7830620f9d945749b5c8bb215182b05f2e34575b93484be6d38dfc6032509`; its receipt is `7074ebce98e42b1bc730f832b73032945188dad6f568f64b5ff2e7ac20b68338`.

## Findings

The one authorized SUMO start completed normally, returned code 0 at 2700 s, and stayed below both accepted stop triggers. Engineering review passes execution binding and raw inventory integrity (18/18 required roles and 25/25 manifest files), with no retry. Those execution checks do not establish valid matched treatment conditions.

The defining treatment/control match fails. The treatment schedule contains M/R/U/X = 1333/192/150/75, but the raw route, tripinfo and FCD identity sets contain only M/R = 1333/192. SUMO logged that it ignored `U_flow` and `X_flow`; 225 planned U/X IDs are absent. The matched R=0 control realized U/X. Therefore the arms differ by more than R, so a treatment-control contrast cannot identify the contract’s R-associated increment. Separately, M departures and serialized delays match by ID, but only 2/1333 M speedFactors match and material pre-R trajectory differences were already present. These matching failures make both a witness claim and an evaluable negative invalid.

The R exposure sequence itself passes the contract’s T3 rule: activation and first scheduled/actual departure at 540 s; first near-merge sample at 578 s; T2 entry interval `(577,578]`; native through-lane entry at 583 s; certain-entry counts 5/6/5 in `[600,630)`, `[630,660)`, `[660,690)`, confirming at 690 s before the 720 s deadline. All 192 R identities have route-bracketed auxiliary entries and corresponding native through-lane changes.

The locked classifier reports P/S/L=`NO_QUALIFYING_EVENT`, Candidate C=`EARLY_WARNING_PRESENT_NOT_STATE1` (17 warnings), and Candidate A=`NO_SPATIAL_CANDIDATE`. The only P short candidates in cells 14/15 start at 1440 s, outside the fixed `[720,1440)` onset window, and last one bin rather than the required persistence. An independent per-vehicle FCD/route/speedFactor/network recalculation confirms their late one-bin deterioration against the same-time control; it does not make them qualifying events. No P/S State1 event is established.

Accepted geometry/lane mapping checks passed; no direct mainline TLS restriction was identified. Downstream E1 taps show continued passage, but their bounded coverage does not exclude every downstream alternative. Control history remains `LOW_R_BACKGROUND_ACCEPTABLE=NOT_EVALUABLE`, fixed-screen failures, and low-speed/C warnings; it is not treated as a clean normal baseline.

## Measurement checks and limitations

- Measurement target, cohort and fixed windows: specified.
- Actual treatment coverage/lifecycle: fails for U/X; M/R are complete.
- Omission/duplication: 225 scheduled U/X identities are absent; FCD records otherwise have no duplicate time-ID samples.
- Independent raw reconciliation: complete for the R-entry intervals and the only short P candidate bins; there are no qualifying P/S bins to adjudicate.
- Regression-test coverage for this post-run analysis: not verified by this scientific review.

## Conclusion and stop

The contract outcome is **`NOT_EVALUABLE`**, not `RAMP_INDUCED_WITNESS_ESTABLISHED` and not `NO_WITNESS`. R exposure occurred, but treatment realization and M matching fail the prospective pair contract. This review supports no causal or general traffic claim and requires no additional run to classify this authorized pair. The one-start authorization is consumed. Do not retry, scan demand, or prepare/execute B/C. No SUMO, TraCI, or netconvert was started during review; no file changes were made by the reviewer.

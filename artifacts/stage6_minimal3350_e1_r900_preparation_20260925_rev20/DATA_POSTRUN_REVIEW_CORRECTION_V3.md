# RETRY3 reporting correction v3

The reporting regression is fixed in a retry3-specific derived adapter. The locked method requires `ONSET_REFERENCE_UNRESOLVED` when a duration-qualified low-state run lacks the exact eligible preceding reference. The P event at core cell 15 starts at 1260 s and lasts four bins; preceding ratios are 0.839884, 0.780261 and 0.762122, all below 0.85. No State1-positive event is established. The earlier data-side `NO_WITNESS` recommendation is withdrawn.

The corrected primary-window profile states are P=`ONSET_REFERENCE_UNRESOLVED`, S=`NO_QUALIFYING_EVENT`, L=`ONSET_REFERENCE_UNRESOLVED`, with seven duration-qualified core unresolved events. Candidate A remains zero. Existing lifecycle, same-time/cell comparison and alternative-cause evidence was retained and hash-bound; no raw files or scientific criteria changed.

Regression suite: **3 passed, 0 failed**, including the exact P episode fixture, an eligible-reference control, and a below-duration control.

Receipt SHA-256: `c700e2d0c4d3c66cd8115e46cb8058e902a6cb79dd20e45bfddc308a610dc653`.

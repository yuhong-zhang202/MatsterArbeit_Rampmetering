# Data/lifecycle review correction v2 — MINIMAL3350 E1 R900 RETRY3

**Correction status:** the previous data-side `NO_WITNESS` recommendation is withdrawn. The raw data and locked numerical thresholds are unchanged. This correction addresses output precedence/reporting only.

## What was wrong

The earlier summary mapped “no numerically qualifying episode” directly to `NO_QUALIFYING_EVENT`. That omitted a duration-qualified low-state candidate whose exact three-bin onset reference is ineligible. The locked methodology explicitly says such a candidate is `ONSET_REFERENCE_UNRESOLVED`, not absent and not confirmed (sections 16–17; run-output precedence section 17).

## Independently reproduced candidate

R900 treatment, core cell 15, P profile: low-state run begins at bin 42 (`[1260,1290)`), continues for four bins through `[1350,1380)`, and exceeds P's three-bin duration. The immediate reference bins are 39–41 with model-reference mean ratios 0.840, 0.780, 0.762; all are below the required 0.85 reference gate. Therefore no reference density may be used and no P event is eligible as State1. The correct status is **`ONSET_REFERENCE_UNRESOLVED`**. This is not a positive State1 result.

The same omission affects duration-qualified core L low-state candidates with ineligible references in the primary window; these are listed in `locked_classifier_correction_v2.json`. The corrected core primary-window profile states are P=`ONSET_REFERENCE_UNRESOLVED`, S=`NO_QUALIFYING_EVENT`, L=`ONSET_REFERENCE_UNRESOLVED`. Candidate A remains 0.

## Corrected data-side conclusion

Withdraw the prior data-side `NO_WITNESS` recommendation. Report the treatment as **`ONSET_REFERENCE_UNRESOLVED` under the locked classifier output precedence**, with no State1-positive episode established. The existing independent scientific disposition must not be replaced by this data-side correction; final pair disposition remains pending/for scientific adjudication.

## Provenance

- Exact run card SHA-256: `c5e94245dc44cc190dbcb2e402c28213c7e7e3ea90edf35e708a8d332209f31a`.
- Previous data receipt (preserved, historical) SHA-256: `c3d387a12d27470e03aea766b725906cc2894d72f83d422f9a350b1ee7a41f96`.
- Source classifier summary SHA-256: `5add43a46fc874d7425c05908ba079fc7f220016d3f64898a552101b68c50124`.
- Cell/bin source SHA-256: `351c297fc5147e9b5e6e5f81a69146bc321d9216f3018e4d8e1e0f768bfb9c86`.
- Locked methodology SHA-256: `22fe22170c17ce74e261e717586a458a1b5173e9deabbee925bd4c1d606adfe7`.
- Corrected machine-readable classification: `locked_classifier_correction_v2.json`.
- No raw files, thresholds, classifier rules, or simulation inputs were modified.

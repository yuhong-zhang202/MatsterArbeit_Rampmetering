# Independent Scientific Prelaunch Review — A Package

**Disposition:** `PASS_WITH_EXPLICIT_LIMITATIONS` for package preparation only.  
**Confidence:** High for the reviewed static binding and comparison scope; Moderate for inference from one fixed materialized R realization.  
**Execution status:** Not authorized. The exact card remains `DRAFT_NOT_AUTHORIZED`.

## Findings

1. The R0 comparator remains historically `CONTROL_NOT_EVALUABLE`; the package does not recast it as a clean normal baseline. Its use is limited to a new exploratory relative comparison.
2. M/U/X identity sets, materialized schedules and key per-vehicle attributes are bound. Actual A-versus-R0 insertion and trajectory equivalence for `t<540` is unverified until A exists and must pass before any B/C arm.
3. `M_flow.502` (desired departure 539.148 s; R0 actual departure 540.00 s) is explicitly treated as an activation-boundary case, not as an actual pre-540 departure.
4. The 240 R speedFactors come from a previously reviewed qMain=3199.2, U=X=0, delayed-R900 raw. They are frozen identically across A/B/C but are not asserted to be the target context's native seed17 random draw. Conclusions must remain conditional on this fixed realization; robustness across R populations is not established.
5. The configured materialized-demand path, package additional XML, and all 18 unique output paths were independently checked against the recorded hashes; output paths resolve under the A-only output root.
6. Engineering preflight is static only: `PREFLIGHT_PASS_NO_PROCESS_STARTED`, `launch_authorized=false`, `launchable_now=false`. Three offline regression tests passed. These checks do not substitute for actual runtime coverage or the post-A empirical matching gate.

## Required limits

- Preserve the R-factor source context and conditional interpretation in any later analysis.
- Preserve all historical R0 dispositions and warnings.
- Do not start B/C unless A's actual pre-540 M/U/X insertion and trajectory gate passes and all remaining plan gates are reviewed.
- This review and package are not a SUMO execution authorization.

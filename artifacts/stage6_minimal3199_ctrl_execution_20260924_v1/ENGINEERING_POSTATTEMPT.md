# Engineering post-attempt review — MINIMAL3199_CTRL_S17

**Disposition:** Pre-spawn runner failure; authorization consumed.  
**Actual SUMO starts:** 0. **TraCI starts:** 0. **netconvert starts:** 0.

The one-use reservation was created, then R02 failed while constructing the Guardian START request with `KeyError:'additional_schema'`. The failure occurred before Guardian or SUMO spawn. The reservation records `status=FAILED`, `simulator_pid=null`, `retry_allowed=false`; under the exact authorization contract, the attempt is consumed. No retry or patch/relaunch was made.

The partial raw output directory was left intact. It contains only two staged configuration files: `scenario_control.add.xml` (3,796 bytes; SHA-256 matches the bound additional input) and `scenario_control.sumocfg` (2,694 bytes; SHA-256 `0a016bea72ef30815226bd8677dbdd86803796523c481e476a6e47f577457c49`). The staged sumocfg differs from its prepared source hash, consistent with an output-path rewrite, but no staged-config hash receipt exists; byte identity is not claimed. No simulation outputs or execution receipt exist. Resource triggers did not fire.

The final read-only preflight and 24 focused tests had passed before the one launch attempt. The failure is in the runner's Guardian request construction path, where `additional_schema` was looked up but not included in the specialized verifier's returned file bindings. That defect is documented, not repaired under the consumed authorization.

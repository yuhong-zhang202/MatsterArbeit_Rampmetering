# Data/provenance prelaunch review — PAIR_3199_S17

**Disposition: PASS for data/provenance binding; confidence High.** Read-only independent review by project `data_analyst`.

The reviewer verified hashes against all package and source bindings, including the plan, locked P/S/L method, accepted network, runner/analysis contracts, route/config sources, and project snapshots. Network SHA-256 is `887c232483f0c68dc024334ff5997250d7d36299ab2744bdcf49d5a314c700ca`. Both future raw directories are absent.

Parsed demand schedules: both arms M=1333 on [0,1500), U=150, X=75; control has no R source (explicit planned R=0), treatment adds R=192 on [540,1500). Exact rates are M=3199.2, R=720, U=360, X=180 veh/h. Seed17, A_OPEN, network, routes/type, 1s step and 2700s horizon match. Both arms bind 18 expected outputs (9 E1, 2 E2, FCD, queues, summary, tripinfo, vehroute, TLS and lanechanges), adequate for the specified future raw reconciliation and artifact checks, subject to postrun parser/application validation.

This pass does not clear engineering blockers: the existing R02 runner rejects these run IDs and runtime/resource bindings are absent. The user-directed waiver of 3350.4/R0 suitability as a prerequisite is recorded in `SCOPE_OVERRIDE.md`; it does not modify the reviewed plan.

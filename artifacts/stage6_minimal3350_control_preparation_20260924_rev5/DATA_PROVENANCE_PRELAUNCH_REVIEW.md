# Data/provenance prelaunch review — MINIMAL3350_CTRL_S17 REV5

**Disposition:** `PASS_DATA_PROVENANCE_PRELAUNCH`  
**Findings:** Blocker 0 / Major 0 / required Minor 0  
**Exact card SHA-256:** `8dc216dcd99f86c2a47eb612ebd61b5c5c81e8fe6ab3d27d7f1c10e59032f6e1`  
**Scope:** Fresh read-only review of immutable REV5 only. REV2's historical BLOCKED review remains intact. No raw files were edited, no process started, and no 3350 treatment outcome was inspected.

## Context

The project is in the Stage 6 minimal U=X=0 existence test. The 3199.2 matched pair has a reviewed `NO_WITNESS`; this review does not reanalyze it. The 3350.4 R=0 control is authorized first, with treatment conditional on the independently reviewed control result. D-008 adopted the second-tier stress plan for Stage 6 only; its escalation remains conditional on completing the 3350 pair. The formal protocol remains unchanged and unfrozen.

## Verified inputs and binding

- M demand contains 1,396 unique identities `M_flow.0`–`M_flow.1395`, each once. Desired departures follow SUMO 1.26.0 integer schedule `i × 1,074 ms`; last departure is 1,498.230 s. All M records use `M_route` and `technical_passenger`, with ID, desired time, route/type, depart position/lane/speed and speedFactor explicitly bound.
- Identity-keyed speedFactor values match the declared source for 1,396/1,396 M vehicles. The input schedule, common-M manifest, input manifest, runtime binding and exact card hashes agree.
- R=0, U=0 and X=0 are explicit `PASS_ZERO` class ledger entries. The demand file contains 1,396 M vehicles and no R/U/X demand.
- START request and receipt hash-bind to the exact card and each other. Request status is `PASS_PERSISTED_UNSENT`. Runner, runtime, SUMO 1.26.0, SUMO_HOME and additional schema bindings agree. Resource contract is 90 s and 60,000,000 bytes, polled every 100 ms with slight overshoot accepted.

## Output paths

I parsed the actual REV5 configuration, additional XML, and output-role manifest. The eight sumocfg target paths (six simulator outputs plus log and error log), all twelve detector/TLS additional XML destinations, and all eighteen required output-role paths resolve directly beneath the same bound control output directory. The eighteen role paths equal the union of six configured simulator outputs and twelve additional XML destinations. All target basenames are distinct. The output directory and its REV5 run parent are absent; the card points to a distinct REV5 raw path.

## SpeedFactor source scope

The values are copied by M identity from `data/raw/stage6_baseline_localization_20260921_v1/LOC_M3350_S17_attempt1/outputs/vehroute.xml` (SHA-256 `0183782a60172b5c038d7c0dcd0a9172478803a1c1673df6eadb29f2a6ea1702`). That source is a prior full-network qMain=3350.4, seed17 run with U/X nonzero. Hash and 1,396/1,396 identity coverage are verified. This closes the fixed M-vector provenance for a paired control/treatment comparison if treatment uses the exact same manifest; it does not establish an independent or representative U=X=0 RNG realization. The comparison is conditional on this explicit M vector.

## Review status and limits

Engineering's REV5 prelaunch review is PASS with 0/0/0 and six focused tests passing. Its static preflight says `launchable_now=false` pending the required fresh reviews. This data/provenance PASS does not classify low-R control suitability, authorize treatment, or establish any traffic result. Guardian/SUMO/TraCI/netconvert starts observed: 0/0/0/0.

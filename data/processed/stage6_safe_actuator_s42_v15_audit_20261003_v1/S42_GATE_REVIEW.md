# S42 V15 independent exploratory data gate

**Disposition: PASS for the prespecified S42 technical/data gates.** This is the third matched seed, not a formal experiment. No simulation was launched for this audit. Definitions and tolerances match the S17 and S23 gate reviews; no window was selected or excluded after inspection.

## Bound inputs and completeness

Run `M3600_R900_S42_ALINEA_TRACI_V15`; raw directory `data/raw/stage6_standard_metering_20261003_v1/M3600_R900_S42_ALINEA_TRACI_V15/outputs/`; card SHA-256 `16ccc167f1501d00f1d1ec84fb7f73087633a6a33e6ec3e4e2e1a295756c8f26`; receipt SHA-256 `9eb433d7b5054f17aea5a52dff83637726b3281fbb6509c66ef4b6d718cc1786`. Receipt is COMPLETED/return code 0, all 32/32 manifest sizes/hashes and card, demand, configuration, network and baseline receipt checks pass. FCD and controller have continuous 4200 seconds; pre-600 FCD labels equal OPEN S42 at 600/600 seconds with zero differences. All M3000/R600/U300/X150 are inserted and arrived by 4200, with no unfinished/undeparted vehicles, collisions, teleports, discards or warnings. Formal protocol remains empty and unfrozen.

There are 119 feedback decisions and 238/238 detector lane windows. E1 occupancy and `nVehContrib` match corresponding XML windows to within the original 0.0050001 percentage-point rounding tolerance. The 7140 event observation groups reconstruct all 238 feedback occupancies without error.

## Safety, service and command realization

Independent arithmetic using logged route/leader/secure-gap/front/follower inputs reproduces all 3600 guard decisions and reasons with zero mismatches. For all 600 actual greens, every remaining storage vehicle passes the separately recomputed immediate-red stopping bound: zero mismatches or aborts; minimum positive margin 2.721274 m. Independent one-second FCD checks find zero differences in pre/post storage sets and positions/speeds, frontmost IDs, internal lane and 600 unique R crossing brackets at the original 0.005001 FCD precision tolerance. Empty greens, red/multiple/wrong-front crossings are zero. Qualified-slot service is 600/600, meeting the ≥20 and ≥90% gate.

Per-second credit has zero mismatches: `Σr/3600 = 706.190524429` vehicles equals `600 greens + 105.190524429 dropped credit + final credit 1` (residual 7.7e−13). Dropped credit is controller bookkeeping, not a measured count of vehicles denied service.

## Fixed six-window rate gate

Each window has a storage queue and a valid rate command for all 300/300 seconds. `C=Σr(t)/3600`; `A=unique stopline crossing IDs`; receiver/safety denials remain in the denominator. All six prespecified `|A−C|/C ≤10%` screens pass.

| Window (s) | C (vehicles) | A | Relative error |
|---|---:|---:|---:|
| 1200–1500 | 42.301940 | 42 | 0.71% |
| 1500–1800 | 54.575540 | 54 | 1.05% |
| 1800–2100 | 44.944647 | 45 | 0.12% |
| 2100–2400 | 57.357319 | 55 | 4.11% |
| 2400–2700 | 52.886158 | 50 | 5.46% |
| 2700–3000 | 55.143767 | 53 | 3.89% |

## Traceability and limits

SHA-256: `controller_steps.csv` `d25288b82f4b4d036b0a9fdbbb4a6f7e5b8f22a91b61330bd38b67d2c1c4f65a`; `feedback_updates.csv` `eff922938b5222c552bdbe5fee10e09788f796949dd11c39173c6a4d6aed9122`; `detector_vehicle_events.csv` `787131b3298dd0dd2b1d511b1b2da6027b52986591a061d2e3a236e0a0eee329`; `fcd.xml.gz` `ba3c3a9bfd6cbd9636477e2d3251ff90476b9942c950a17b002ce5dd4d2fcee4`; `tripinfo.xml` `a52487f615669079e076b2165ef128426847d2270473f308086ee8a2092de156`. The receipt binds other raw files; this directory's `summary.json`, `city_evidence.json`, `operational_chain.json` and CSVs bind derived full-cohort analysis. Logged TraCI inputs and one-second FCD support these bounded checks, not every subsecond hazard or a controller-benefit claim. Three-seed paired interpretation is separate.

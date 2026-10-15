# S23 V15 independent exploratory data gate

**Disposition: PASS for the prespecified S23 technical/data gates.** This is the second seed, not an independent formal experiment or a multi-seed scientific conclusion. No simulation was launched for this review. Methods and thresholds are the same as the reviewed S17 `S17_GATE_REVIEW.md`, with no selected-window exclusion.

## Bound inputs and completeness

Run `M3600_R900_S23_ALINEA_TRACI_V15`; raw directory `data/raw/stage6_standard_metering_20261003_v1/M3600_R900_S23_ALINEA_TRACI_V15/outputs/`; card SHA-256 `4ea609521b8ef60bb04d733c8532e981203fe1cf4aecd7519891ff3bbe0bd796`, receipt SHA-256 `f44fddd17edb8a28fcdd313846a882b74fe85ac0d8b0410420eb7c2fd859ede2`. Receipt status COMPLETED/return code 0, all **32/32** manifest file sizes and hashes match, and card/demand/config/network/baseline receipt checks pass. Full 4200 FCD and controller seconds are continuous. The first 600 FCD labels equal OPEN S23 exactly (600/600, zero different). All requested M3000/R600/U300/X150 are inserted and arrived by 4200; unfinished and undeparted are zero, summary lifecycle reconciles, warnings zero. The formal protocol remains empty/unfrozen.

There are 119 feedback decisions and **238/238** detector lane windows. Logged E1 occupancy and `nVehContrib` agree with same-window XML within the original 0.0050001 percentage-point rounding tolerance; **7140** event observation groups reconstruct all 238 feedback occupancies with zero error. No legacy interval API value was substituted.

## Safety, service and command realization

From each second's recorded route, leader, `getSecureGap` result, front/follower state and the reviewed formulas, independent arithmetic reproduces all 3600 guard reason/allow decisions with **zero mismatches**. This check is conditional on logged TraCI sensor values; it does not make a second simulator call. All **600** actual greens have post-green immediate-red stopping inequalities independently recomputed for every remaining storage vehicle; zero mismatches/aborts, minimum positive margin **1.879212 m**. Independent one-second FCD reconstruction matches all pre/post storage vehicle sets and positions/speeds, frontmost IDs, internal lane and **600 unique R crossing brackets** with zero mismatches at the original FCD 0.005001 precision tolerance. Empty greens, red/multiple/wrong-front crossings and SUMO warnings are all zero. The original qualified-slot service gate passes at **600/600** (minimum 20 and at least 90%).

Credit recomputed every controlled second has zero log mismatches: integrated command `Σr/3600 = 702.706940190` vehicles equals **600 G + 101.706940190 dropped credit + final credit 1**, residual about 1.96e−12. Nominal due seconds are 1262. Dropped credit is bookkeeping, not a count of unserved requested vehicles.

## Fixed six-window rate gate

All six windows are eligible: storage queue ≥1 for **all 300/300 seconds** in each. `C=Σr(t)/3600`, `A=unique stopline crossing IDs`, and every prespecified `|A−C|/C ≤ 10%` screen passes; receiver/safety denials remain in the denominator.

| Window (s) | C (vehicles) | A | Relative error |
|---|---:|---:|---:|
| 1200–1500 | 49.939220 | 49 | 1.88% |
| 1500–1800 | 40.888618 | 41 | 0.27% |
| 1800–2100 | 52.231425 | 50 | 4.27% |
| 2100–2400 | 41.506000 | 42 | 1.19% |
| 2400–2700 | 51.499826 | 50 | 2.91% |
| 2700–3000 | 54.848791 | 55 | 0.28% |

## Traceability and interpretation boundary

SHA-256: `controller_steps.csv` `ff8650d07b2ba0782ceceb4f20a504ebfacb0af07cde0b4f2d8351f902d3ba96`; `feedback_updates.csv` `adc6f4369db47fe46faffc393b61eaa9c228ea219d0b62108f5d76422a86117e`; `detector_vehicle_events.csv` `05f8d4cb84a8ea7ed983ede48e00c9598ff604fc99849e2b0897084a41daa39c`; `fcd.xml.gz` `b917ddb4ccb0959ea8bbe1dce2a6a0360dbd1a33ed9123f34ee88d9e68ef0f52`; `tripinfo.xml` `49c30c12672840f03e5974d8d00e5b8ca61f442be14c951c8e9d9c762f43f07d`. Original receipt binds all other raw files; derived `summary.json` and CSVs in this directory bind full-cohort/classifier analysis. One-second brackets and warning checks support this bounded technical gate, not a claim about every subsecond hazard or controller benefit. Scientific review of the paired S17/S23/S42 effects remains separate.

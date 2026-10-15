# S17 V15 independent exploratory data gate

**Disposition: PASS for the prespecified S17 technical/data gates.** This is one seed and does not itself authorize a scientific interpretation or prove multi-seed robustness. No new simulation was launched for this review.

## Bound inputs and coverage

Run `M3600_R900_S17_ALINEA_TRACI_V15`; raw directory `data/raw/stage6_standard_metering_20261003_v1/M3600_R900_S17_ALINEA_TRACI_V15/outputs/`; card `artifacts/stage6_standard_metering_execution_20261003_v1/inputs/M3600_R900_S17_ALINEA_TRACI_V15/card.json` (SHA-256 `f7b7c373f67e913521d6cc9bdfb84a343d90f6edab6a47e9a55b4f8639d98066`). Receipt SHA-256 `0e34703653f9ccdbfd0353438906f291f8096763eaca304c109f43e210dbf63d`, status COMPLETED, return code 0; all **32/32** manifest file sizes and hashes match, and demand/config/network/baseline receipt checks pass. The requested cohort is M3000/R600/U300/X150. The 4200 controller and FCD seconds are continuous, all 4050 requested IDs were inserted and arrived, with 0 unfinished and 0 undeparted; `sumo_summary.xml` reconciles. Warning count 0. The first 600 FCD time labels exactly match the existing S17 OPEN baseline (600/600, 0 differing records). The formal protocol remains empty/unfrozen; these are exploratory results.

## Feedback, safety and service

There are 119 feedback decisions and **238/238** E1 lane windows. Each logged occupancy and `nVehContrib` matches its XML interval within the original ±0.0050001 percentage-point XML rounding tolerance; the 7140 detector event observation groups reconstruct all 238 logged lane occupancies exactly (maximum residual 0). The feedback source is `getVehicleData` event residence, not the known nonequivalent legacy TraCI interval API.

The 3600 controlled one-second logs independently reproduce all guard reason/allowed decisions from recorded route, leader, secure-gap result, front/follower states and stated formulas with **0 mismatches**. This reproduces decision arithmetic conditional on recorded TraCI sensor values; it does not independently rerun `getSecureGap`. For every green, recomputing the post-green immediate-red stopping inequality from the recorded *post-step* state gives 0 mismatches and a minimum positive margin of **2.166845 m** over all remaining vehicles. Independent FCD reconstruction finds 600 unique R stopline crossings, matching all 600 green slots and all logged brackets; before/after storage population, frontmost ID and pre/post state match at original FCD 0.005001 m/s or m precision tolerance with 0 mismatches. There are 0 empty greens, red crossings, multiple crossings, wrong-front crossings, interlock aborts and warning messages. The original ≥20 qualified-slot and ≥90% crossing gate passes at **600/600**.

Credit independently recomputed second by second has 0 row mismatches: integrated command `Σr/3600 = 718.184333702` vehicles equals **600 greens + 117.184333702 dropped credit + final credit 1** (rounding residual about 1.8e−12). Nominal due seconds 1307. Dropped credit is an actuator accounting quantity, not a count of unserved requested vehicles.

## Predeclared six-window rate gate

Eligibility requires storage queue ≥1 at **every** decision second within each fixed `[1200,3000)` 300 s window. `C=Σr(t)/3600` and `A=unique observed R crossings`; receiver obstruction and safety denials remain in the denominator. Every window is eligible and passes the prospective `|A−C|/C ≤ 0.10` threshold:

| Window (s) | C (vehicles) | A | Relative error |
|---|---:|---:|---:|
| 1200–1500 | 50.690136 | 51 | 0.61% |
| 1500–1800 | 43.403992 | 43 | 0.93% |
| 1800–2100 | 45.398464 | 45 | 0.88% |
| 2100–2400 | 54.489261 | 53 | 2.73% |
| 2400–2700 | 47.791262 | 47 | 1.66% |
| 2700–3000 | 58.095454 | 55 | 5.33% |

## Source mapping and limits

Independent source hashes: `controller_steps.csv` `ee6e28f272723f4f7d13294d111bc21eacc3d7d866fb17ab413d47119a0d9ff8`; `feedback_updates.csv` `ef5971b41d3b5ddc5f4d362ddf79bba6e43204c69f57fc5b25f919b64594ca34`; `detector_vehicle_events.csv` `94648e431b4a2fad55dc06cc89f96e3b9cf746e603c98b088189cc4876de9432`; `fcd.xml.gz` `7ef63742e146ea5467bbc21705ba4f5da50c1f908545181b6b146c9f0346f455`; `tripinfo.xml` `68ff5bcf0bb57c3cde82b6b90094b1aa1d9eaed06774bbfa9c1bffdfaff5aad3`. The original 32-file manifest binds all other outputs; `summary.json` and derived CSV files in this directory trace full-cohort/classifier processing. One-second FCD brackets cannot prove subsecond absence of every possible hazard; the safe interlock, zero SUMO warnings and complete crossing checks support the bounded technical gate. Scientific review remains separate.

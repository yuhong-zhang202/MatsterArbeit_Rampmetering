# Current OPEN city-side check — three stored runs

Date: 2026-10-03. Exploratory, bounded read-only audit. No simulation, scientific-input change or historical overwrite. Context Preflight: current Stage6 COMPLETE_WITH_LIMITATIONS/D-012; all new runs paused/unapproved; formal protocol empty. This check addresses whether current uncontrolled output already supplies the particular shared R/U obstruction previously observed under B22.

## Result

It does not in these three stored seed17 runs. `M3600_R1200_S17`, `M3000_R1200_S17`, `M3600_R900_S17` each have zero shared-approach R and U vehicle-seconds below1.389m/s and zero below0.1m/s, separately in whole[0,4200), active[600,3000), and evaluation[1200,3000). Corresponding slow R/U co-presence and slow U during urban green are consequently zero. The meter remains G at every recorded second. Previously audited storage/shared E2 records also have zero jam-positive bins out of140 for all three.

This is a lack of the specified shared-lane phenomenon in these observations, not a claim that city traffic is unaffected or that the network cannot exhibit it. The weaker speed<5m/s diagnostic does detect a few shared samples: evaluation U50/50/49 vehicle-seconds and R214/214/181, respectively. Do not confuse5m/s with the historical1.389m/s (about5km/h) threshold, or call those samples stopped spillback.

## Where current urban costs occur

For the two R1200 runs, complete-cohort U residence is111.07s and maximum external departDelay275s; R maximum departDelay274s. Evaluation U on the upstream `urban_in_0` has3321 vehicle-seconds below1.389m/s and725 stopped; R has11074 slow and2475 stopped. These observations are numerically identical for M3000 and M3600 in the bounded output. In contrast, shared-lane/storage slow and stopped counts under the historical threshold remain zero. The source waiting and upstream urban-in congestion must not be renamed ramp-storage spillback into the shared approach.

For M3600R900, R/U external departDelay is zero. U residence is66.293333s. Evaluation U urban-in slow/stopped counts217/140 are present while shared slow/stopped remain zero. The severe mainline state therefore does not by itself demonstrate the old B22 city-side queue mechanism at this OPEN operating point.

## Implication for the proposed extra OPEN run

The historical default V2 A was already the matched OPEN arm at the old B22 demand; its shared U slow count was0 while B22 had987. The present current-implementation OPEN observations include stronger mainline loading and R900 and likewise show no shared slow/stopped R/U event. Merely replaying old B22 demand with the meter OPEN would answer a limited implementation-comparison question; available data do not provide a positive reason to expect that it will reproduce the meter-induced storage/shared queue. An OPEN rerun should not be treated as a required replacement for qualified B22 capability evidence or as a guaranteed way to close the current shared-effect question. No run is proposed or authorized by this report.

This does not prove the absence of such an OPEN state at every demand or seed. It also does not prove that ALINEA will create, prevent or optimally balance the city effect. These are separate future experimental questions.

## Method and verification

First read existing processed summaries and sparse30s queue statistics; those already showed zero stopped shared samples but used5m/s for their other diagnostic. To answer the historical-threshold and physical co-presence question exactly, streamed only the three FCD files plus their TLS files. Each has4200 consecutive seconds and no duplicate vehicle within a step. All six raw files match their execution-receipt hashes. The meter is continuouslyG, and urban TLS has all4200 labels. No other new run was reprocessed.

Source hashes, window definitions, exact zero and nonzero counts, completed-cohort summary values and E2 reuse are in `current_open_city.json`. `recheck_current.py` reproduces the bounded extraction. Tables are in `results/tables/stage6_capability_closeout_20261002_v1/current_open_city/{lane_exposure.csv,shared_context.csv}`. FCD counters are vehicle-seconds, not unique vehicles; window endpoints are half-open. Cohort and E2 quantities reuse their independently checked current processed records and are labelled as such. External wait and physical in-network lane exposure are separate.

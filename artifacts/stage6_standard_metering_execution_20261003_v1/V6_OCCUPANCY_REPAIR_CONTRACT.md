# V6 occupancy measurement repair — review before one new NOOP start

Status: technical proposal and static implementation only. No V6 SUMO start has occurred. Existing V2, V3, and V5 cards and raw outputs remain immutable. Formal protocol is not frozen.

## Trigger and evidence

The completed V5 NOOP read at decision time 630 s (labeled [600, 630) s) returned TraCI `getLastIntervalOccupancy` 10.393498907794386% and 10.169271171366745% for `p1_main_down_20_l0/l1`. Its own same-window E1 XML gives 11.40% and 11.57%. TraCI last-interval vehicle counts and XML `nVehContrib` both give 16/20; XML `nVehEntered` also gives 16/20. Thus simple XML two-decimal rounding and a 30 s window shift do not account for the occupancy differences. The specific vehicle-level cause is unproved by V5 raw output.

SUMO v1_26_0 `MSInductLoop.cpp` computes E1 XML interval occupancy in `writeXMLOutput` from completed vehicle detector times plus vehicles still on the detector, then resets the interval. `getIntervalOccupancy(true)` uses a separate collection and clipping calculation. This establishes distinct calculation paths, not a diagnosed implementation defect for these particular vehicles. Source: <https://raw.githubusercontent.com/eclipse-sumo/sumo/v1_26_0/src/microsim/output/MSInductLoop.cpp>, lines 302–315 and 360–395. Official TraCI documentation defines E1 `getLastStepOccupancy` as a percentage for the last simulation step and `getLastIntervalOccupancy` as the previous interval: <https://sumo.dlr.de/docs/TraCI/Induction_Loop_Value_Retrieval.html>.

## Frozen V6 sampling contract

- After `simulationStep(t+1)`, for every integer t from 600 through 4169 inclusive, query both detectors' `getLastStepOccupancy`; log one row labeled `[t,t+1)` in `detector_step_occupancy.csv`. Querying is read-only.
- At decision times 630, 660, ..., 4170 s, require exactly 30 consecutive sample end times `decision_time−29, ..., decision_time`. Calculate each lane's arithmetic mean in percentage points and use their mean as the feedback occupancy. The observation window is exactly `[decision_time−30,decision_time)`; no feedback update moves to 631 s.
- Retain both `getLastIntervalOccupancy` values and `getLastIntervalVehicleNumber` values in `feedback_updates.csv` for diagnosis only. Log `occupancy_source=mean_last_step_30`, `sample_count=30`, both rolling values, and original 11% target and 70 veh/h per percentage point gain. Missing, duplicate, out-of-order, nonfinite, or outside-[0,100]% step samples fail the run; no imputation.
- V6 NOOP performs all 119 read-only feedback observations to test the full horizon and never calls `setRedYellowGreenState` or `Feedback.update`. ALINEA would apply its first update at 630 s if separately released. The existing initial rate, bounds, pulse and service gates, demand, seed, network, SUMO version, and 4200 s horizon are unchanged.

## Required release gate

Only one newly identified V6 S17 NOOP technical start is proposed. Its card must bind new runner hash and all existing inputs, and receive independent exact-card scientific release. After completion, verify 3570 consecutive sample rows, 119 complete 30-row windows, and every lane/window rolling mean against the corresponding XML E1 occupancy with XML two-decimal precision tolerance ±0.0050001 percentage points. Verify all original full-traffic neutral comparisons as well. A mismatch or incomplete sample window blocks all ALINEA cards; do not change tolerance, target, gain, or decision time after seeing the result. Record any failed start in the common budget.

At present the public start ledger is 21/40 global and 3/8 new control/technical. A V6 NOOP plus the three preplanned controlled seeds would make 25/40 and 7/8, leaving one technical start contingency. Per-start limits remain 120 s, 250 MB, and shared raw 8 GB.

Static verification before release: `.venv/bin/python -m unittest tests/test_stage6_standard_metering_s1.py -q` (16 tests, PASS); `.venv/bin/python -m py_compile scripts/stage6/standard_metering_20261003/control.py scripts/stage6/standard_metering_20261003/runner.py tests/test_stage6_standard_metering_s1.py` (PASS). These tests do not prove XML equality; the single V6 NOOP supplies that prospective measurement validation.

# REV19 retry2 engineering failure disposition

- Status: `FAILED_PRE_SPAWN_ENGINEERING`
- Run: `MINIMAL3350_E1_R900_DELAYED_S17_TECH_RETRY2`
- Exact card SHA-256: `cea374f60db487ce9b4bd0c5f45ed28996b298a710af2da33aca6ae9f3bae380`
- Consumed reservation SHA-256: `d27a977678871885d376272b56b945e9d1f28a7728b22fd63dedd05da3aaaa45`
- Guardian / SUMO / TraCI / netconvert starts: 0 / 0 / 0 / 0

The runner failed with `FileExistsError` during exclusive staging of `scenario_control.add.xml`, before the Guardian start handoff. The E1-specific branch had already written the staged additional and sumocfg files, then the generic staging block tried to write them a second time. The output directory contains only those two expected staged inputs (their byte lengths and SHA-256 values are recorded in the JSON receipt); no traffic output was produced.

The attempt reservation is irreversible (`FAILED`, `retry_allowed=false`, `simulator_pid=null`). This receipt and the output directory are preserved. The next attempt must use an independent run identity and output root.

Repair-cycle count: 2. Regression evidence for the fix is recorded separately after the focused engineering tests complete.

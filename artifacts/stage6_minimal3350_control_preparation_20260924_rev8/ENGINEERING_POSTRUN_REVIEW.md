# Engineering post-run review — MINIMAL3350_CTRL_S17 REV8

**Disposition: PASS_ENGINEERING_POSTRUN**, 0 blockers / 0 major / 0 required minor.

- Guardian/SUMO starts: 1/1; TraCI/netconvert: 0/0. One reservation; simulator exited 0 at 2,700 s.
- Runtime: 24.9565 s of 90 s; output payload 19,047,639 bytes of 60,000,000. No stop reason; retry disabled.
- Staged sumocfg and additional XML source hashes match the card; staged bytes and SHA-256 match the reservation.
- All 18 required output-role files and 7 support files match manifest byte counts and hashes. The manifest inventories 25 files; its hash and the execution-receipt hash match the reservation.
- `sumo.log` reports the final step at 2,700 s; SUMO and Guardian error logs are empty.
- Raw output remains immutable. This engineering review does not perform lifecycle/data or scientific evaluation and does not release treatment.

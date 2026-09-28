# REV20 data and provenance prelaunch review

- Disposition: `PASS_DATA_PROVENANCE_PRELAUNCH`
- Findings: Blocker / Major / required Minor = 0 / 0 / 0
- Confidence: High
- Run: `MINIMAL3350_E1_R900_DELAYED_S17_TECH_RETRY3`
- Exact card SHA-256: `c5e94245dc44cc190dbcb2e402c28213c7e7e3ea90edf35e708a8d332209f31a`

M 1,396/1,396 matches the common manifest and accepted control on identity, integer-ms departure, route, vType, speedFactor and departure attributes. The only added demand is R_flow.0–239 (240 vehicles, departures 540000–1496000 ms every 4000 ms); U/X are explicit zero. qMain, R rate/window, seed, geometry, behavior and witness bindings are unchanged. Demand, R vector and R source match earlier attempts byte-for-byte; XML changes are output-root references only.

The deterministic staged files match the card: sumocfg 2,888 bytes and additional XML 4,012 bytes. The sumocfg `additional-files` reference resolves exactly to staged v20 additional XML; all 20 output references are unique, canonical and confined to the new v20 output root. The persisted R02 request validates and is unsent. The new output directory and reservation are absent; `data/raw` is an existing writable ancestor.

REV18 and REV19 pre-spawn failures remain separate. REV19 contains only the two expected staged XML files with recorded hashes; REV17 raw integrity remains 15/15 files matching recorded sizes and hashes. No process started and no raw data was written during this review.

**Review-boundary note:** When the data analyst completed the audit, the engineering PASS receipt had not yet been written; I recorded the engineering disposition separately afterward. This data PASS does not itself release the attempt. Final preflight must validate all three exact-card receipts and their sidecar.

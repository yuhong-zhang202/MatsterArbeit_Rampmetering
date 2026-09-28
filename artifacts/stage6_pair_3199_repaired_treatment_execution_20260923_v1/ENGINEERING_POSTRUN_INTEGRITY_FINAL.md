# Engineering post-run integrity review

**Disposition: PASS — execution binding, resource contract, log completion, and raw-file integrity.** This is engineering integrity only; it does not analyze lifecycle, trajectory matching, R exposure, classifier output, or witness status.

- Attempt: `PAIR3199_R720_DELAYED_S17_REPAIRED_V5_ATTEMPT1`; scenario `PAIR_3199_R720_DELAYED_S17`; execution UUID `b095cce4-baba-4c40-aa79-08b5e58b9ce1`. FINAL card SHA-256 `0801dc1e15ade92babe33640d521ba831174210a200b9e5a66aaeb3bd472e0ef`.
- R02 reservation: `FINAL_STATUS_HANDED_OFF`; one start; return code 0; retry disabled; stop reason null. SUMO 1.26.0 log reports final step reached at 2700 s. The log summary says `Inserted: 1750`; no lifecycle inference is made here.
- Runtime `24.370309` s vs 90 s trigger; output payload `23,936,627` bytes vs 75,000,000-byte trigger. Neither trigger fired.
- Required output roles: 18/18 present and match manifest hash/size. Manifest inventory 25/25 files match; all inventoried XML files parse. `sumo_error.log` is empty.
- Execution receipt SHA-256 `eb8444594881f4d02716c7312890e72caa6db9d208e72f315cefe090bfc34e2a`; output manifest SHA-256 `f36f336473792c2af246abf75c3b7b2e9217abb537e7b42e15685e6af46b7173`; one-use reservation SHA-256 `863e11a6a444b06f6859f13cb26aa5cdcff4a0e52685965061ab46aee844e434`.

No retry or other simulation was started. This review does not adjudicate whether M/U/X trajectories were equivalent before R exposure; that is reserved for the independently reviewed post-run data/scientific workflow.

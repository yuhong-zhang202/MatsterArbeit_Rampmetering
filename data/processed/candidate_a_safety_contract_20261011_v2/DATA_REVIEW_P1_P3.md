# PR #7 P1/P3 data review (2026-10-11)

## Scope and preserved history

This is a versioned correction to the **offline evidence audit**, not to the A07 simulation, safety guard, or A1/A2 contract. The original ignored `data/raw/.../CA_FIXED_R300_S17_A07/` files, V1 audit result, V3 gate, and historical reviews remain unchanged. The formal protocol is empty/unfrozen. The output receipt is [`P1_CLEAN_AUDIT_RECEIPT.json`](P1_CLEAN_AUDIT_RECEIPT.json), SHA-256 `508845599a2c90d9239c0995a79869cef5cb7585a3ec3549211810087c53b463` at this review.

## P1: failure and correction

The prior `audit_a07.py` always opened ignored raw `guardian_receipt.json` and `phase_steps.csv`; a clean checkout therefore failed even though the public failure snapshot, guardian receipt, cycles and crossings were committed. The revised default reads only committed files. It checks the public guardian's hashes for its byte-identical snapshot/cycles/crossings, the V3 binding hashes for gate/window CSV/thin phase ledger, 42 matching guard witness identities (27 storage, 15 ingress), one unsafe `R_flow.1`, the recorded stopline-gap and guard algebra, 1206 contiguous **derived** thin-ledger rows, the single green crossing, an incomplete cycle, and six service windows. The source files and hashes are enumerated in the receipt. The public snapshot hash remains `0cb77aa1549d500628fa136742d5119d0cdbdd94c5e23f357090b44c6ccc984d`; V3 gate hash remains `d7cf23dce2f2639c0f972102938cca492bd7d6442c7b5d1c6eeac37b72c2a20f`.

The default public check **does not independently reconstruct `phase_steps.csv` from raw**. The committed `R300_A07_PHASE_LEDGER_THIN_V3.csv` is a V3-bound derivative. A separate `--verify-local-raw` mode additionally checks the ignored raw guardian and four raw hashes, verifies public/raw guardian, snapshot, cycles and crossings byte identity, and compares every thin-ledger field with all 1206 raw phase rows. This mode is local-only and must not be described as available in a clean Git checkout. Neither mode executes the rejected 1206–1207 red motion step or establishes native SUMO red safety.

## Clean archive and local verification

An archive of PR #7 head `f5959510a6f888dcb6bd6ae762fcf99f16d53d90` was extracted into `/private/tmp/pr7-clean-audit-BGqBS8`; the two revised script/test files were copied byte-for-byte into it. The ignored A07 raw guardian was confirmed **absent**. In that clean archive, `python3 -m unittest discover -s tests/candidate_a_safety_contract_20261011_v1 -v` returned **7 PASS, 0 FAIL, 0 ERROR**, and `python3 scripts/candidate_a_safety_contract_20261011_v1/audit_a07.py` returned PASS. In the original checkout, the same audit with `--verify-local-raw` returned PASS. All three commands exited 0; exact outputs are preserved in this V2 directory. Python was 3.13.0. This is a **precommit clean-archive check with exact revised file copies**, so a final delivered-commit archive rerun is still needed before claiming that the eventual new PR head itself was tested cleanly.

The new regression tests verify public audit independence from a nonexistent raw path, explicitly reject the optional local-raw mode when raw is missing, and retain distinct fixture behavior for a measured zero, a partially observed window, and wholly unobserved null/blank windows. The authoritative V3 windows are `[6,0,0,0,0,0]` observed seconds: the first has genuine values (`C=C_applied=0.5`, `E=0`, `N=1`) but is incomplete; five later windows have null measurements and blank CSV cells. All six lack full-window qualification.

The script SHA-256 is `5a9bbcf610acaefa95291e102c3a3b99020d921f306e878861057441a2456aaa`; test SHA-256 is `e1b121c973c7f9808d7c9793a4749d96611896c6b9321d1cc5c3cfc7fd962f87`. The receipt binds these and the public inputs. The clean archive log, public audit JSON and local-only audit JSON are adjacent to this report.

## P3 and scientific boundary

R300/A07 was started and aborted by the current prospective-red guard. The **four** unexecuted fixed rates are **450, 600, 750 and 900 veh/h**. This is a wording/accounting correction only; none has been tested or qualified. The new audit still supports the **recorded current-contract guard refusal** and the existing bounded STOP3/NOT_QUALIFIED classification, subject to independent scientific re-review. It provides no evidence that the refused red step would have been unsafe, that Candidate A is universally infeasible, or that 900 veh/h is physically impossible. No SUMO or TraCI start occurred in this correction.

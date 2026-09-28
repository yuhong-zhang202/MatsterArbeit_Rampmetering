# O2 C/S17/450 attempt02 technical failure record

## Outcome

Attempt02 is a technical troubleshooting failure, not a scientific diagnostic run. It consumed one SUMO start and 20.106794541992713 s. Two attempts together consumed 2 SUMO starts, 28.542396625998663 s and 118,166 final directory bytes (attempt01: 1 start, 8.43560208400595 s, 13,288 bytes; attempt02: 1 start, 20.106794541992713 s, 104,878 bytes). Attempt02 established one TraCI connection but executed zero `simulationStep` calls and collected no traffic, vehicle, detector, leader, or TLS observation.

## Root cause (High confidence)

The observer correctly identified the SUMO child PID 48669 as the sole TCP listener before connecting (first observed at elapsed 18.71878533299605 s). `traci.connect()` then returned successfully. The observer immediately required the same process still to own a socket in `LISTEN` state; that query returned empty and raised `server ownership changed before observation`. This check was invalid after connection: with `--num-clients 1`, SUMO accepts its sole client and closes the temporary listening socket while retaining the accepted client connection. The empty LISTEN result does not show process ownership actually changed.

The version-bound source corroborates this behavior: in SUMO v1_26_0, `TraCIServer` constructs a local `tcpip::Socket serverSocket`, accepts the client into `mySockets`, and completes the constructor after the expected client connects (`src/traci-server/TraCIServer.cpp`, lines 3117–3170). The listener's local lifetime ends while the accepted socket remains in the server's socket map.

## Exact technical fix for the next isolated attempt

Keep the pre-connect gate requiring exactly the expected SUMO PID to own the `LISTEN` socket on port 8819. After `traci.connect()`, verify the expected SUMO PID owns the accepted `ESTABLISHED` socket whose local/remote address tuple is the exact reverse of the observer client's `getsockname()` / `getpeername()` tuple. Do not require a post-connect `LISTEN` socket. Add an offline fixture with a one-client server that closes its listening socket immediately after accept, plus wrong-PID, wrong-tuple, and no-connection cases. This changes only connection ownership verification; traffic inputs, client calls, and simulation stepping remain unchanged.

## Preserved evidence

- `data/raw/stage6_o2_causal_diagnostic_20260921_v1/O2_C_S17_450_attempt2/execution_receipt.json`: SHA-256 `3fd40d233f8f54a0b4196b07a4f739ae237c3b569d27033ead89b8af0d8e27ed`.
- `observer_receipt.json`: SHA-256 `e53faf9e4eb0881c8fcd39ddb4650c7af5b7ebcaa1f1f07dd6a6ccd4cc818003`.
- `observer.jsonl`: SHA-256 `c2965e5de372ed1b2f0fc66bd92340c9c911606984d49ba2ff956a93433fe6b2`.
- `output_manifest.json`: SHA-256 `8100f85ca9c133e2bcb4963a699cd658c52d0fb641f3e1669a0dd14e488f69c0`; 30/30 listed output bindings matched.
- Attempt01 remains separately immutable with its original 11 files and 13,288 bytes.

No scientific conclusion is supported by attempt02.

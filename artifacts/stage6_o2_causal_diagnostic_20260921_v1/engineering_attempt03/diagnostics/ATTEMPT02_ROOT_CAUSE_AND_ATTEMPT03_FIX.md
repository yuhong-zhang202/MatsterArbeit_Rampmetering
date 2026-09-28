# Attempt02 root cause and attempt03 exact repair

## Observable failure and established technical cause

Attempt02 consumed one SUMO start,20.106794541992713s,104878bytes. Readiness saw SUMO PID48669 LISTEN at18.71878533299605s, traci.connect returned, and the immediately following LISTEN-only lsof query returned1/empty. The observer raised `server ownership changed before observation`, then terminated SUMO (ultimately−9). No getVersion or simulationStep occurred; this was one successful transport connection, not a completed TraCI protocol/version check or traffic run.

The postconnect predicate was wrong: absence of LISTEN after the sole client connects does not imply a changed owner. Confidence High.

Bound official SUMO v1_26_0 sources saved in this package:

- `diagnostics/TraCIServer.cpp`, SHAbe6a4ed81700bf917b9e7321ced8032d6e3752c84f7f4157875f8a37c35edd6b: local lines541 onward construct a block-local serverSocket; accept(true) moves each accepted socket to persistent mySockets; after numClients=1 is accepted, the block ends.
- `diagnostics/socket.cpp`, SHAfa210a9b49e984f786b58e5cb201ef78a0cbfeeb8a5f1f244aa3a211d4c9e04d: local lines286–295 move accepted socket_ into a new object; lines147–164 destroy the original listening server_socket_. The listening socket is intentionally gone while the accepted connection remains.

These are local plain-file line numbers for the exact hash-bound sources. Rendered GitHub line positions may differ and are not used as local evidence anchors. Tagged upstream source documents behavior but is not represented as a reproducible build provenance for the installed binary.

A real Python-only control reproduces this lifecycle: child49419 LISTEN verified, then accept and close listener; the old LISTEN query returns1/empty while the connection exchanges PING/PONG successfully. The new lsof check finds child49419 ESTABLISHED with exact127.0.0.1:8819→127.0.0.1:50950 counterpart. This fixture starts zero SUMO/TraCI processes. See accepted_socket_control_receipt.json.

## Startup delay is a separate observation

Attempt02 startup.sample.txt (SHA b31dc3ff753809bc7a9e9e535ea8972e2cefdc0514c8c89ab46ed50eca349f80) captured the first1s sample around2–3s after launch. All766 samples are within dyld preparation/dependency loading;607 sample frames include Loader::mapSegments→SyscallDelegate::fcntl→__fcntl. This directly documents loader activity before application startup at that interval. It does not prove that an OS security policy caused all18.7s, or reconstruct the unobserved lifetime of attempt01. Retain the60s readiness gate and180s whole-attempt watchdog, without changing signature, sandbox, dependencies, or scientific inputs.

## Attempt03 exact technical change

Keep the preconnect exact child-PID LISTEN gate. After traci.connect:

1. Read the connected Python socket's local and peer endpoint metadata using getsockname/getpeername (no TraCI command or behavior setter).
2. Query `/usr/sbin/lsof -nP -a -p CHILD_PID -iTCP:8819 -sTCP:ESTABLISHED -FpfntT`.
3. Require exactly one ESTABLISHED descriptor in that PID whose server-to-client endpoints exactly reverse the observer's connected socket. Require child still alive.
4. Preserve raw command/result/endpoints/matches. Allow at most2s for the accepted descriptor to become observable; wrong/missing identity fails closed. Only then query version and begin the unchanged450 single-second steps.

No relaxation to arbitrary port ownership, no reliance on PID alone, no direct SUMO invocation, no auto-retry. Same C/seed17/end450, no setters, no scientific parameters changed. Raw attempt03 root is new. Successful runtime still requires C-prefix neutrality/alignment and independent scientific interpretation.

Prior attempts01+02 are permanently retained:2 starts,28.542396625998663s,118166bytes. Attempt03 adds at most one start/180s/200MB under this card; cumulative observed stop-lines208.54239662599866s/200118166bytes. Subsequent troubleshooting, if required, needs a new evidence-based immutable reviewed card under existing user authorization.

The parent's two preflight invocation failures (relative paths, then sandbox-denied local bind) are recorded separately and consumed zero SUMO starts. Source note and parent immutable failure report are explicitly card-bound. Do not count those as science runs.

# Attempt01 startup diagnosis and attempt02 technical hypothesis

No new SUMO was started during this investigation. Original attempt01 raw files and frozen card remain unchanged.

## Confirmed facts — High confidence

- SUMO PID46760 was spawned with the exact registered binary/config and `--remote-port8819 --num-clients1` (separate argv tokens). Observer PID/PGID46758. The child remained alive while the observer's101 lsof polls returned1 with empty stdout/stderr. At8s the observer raised `no owned TraCI listener in 8 seconds` and terminated SUMO, producing native returncode−15. Supervisor returned terminal_nonzero after8.43560208400595s. It did not reach traci.connect or simulationStep. Native logs and all scientific XML were absent. This is an observer startup gate failure, not a native SUMO traffic error.
- Both PIDs and process group are absent.11 files/13288B are preserved. Prior receipt SHAceb91d360a1dea201b5d5151abe0cb0880c57b20768066d8a6923307e1e37114; manifest SHAa48263778cb80124224edb01c14419e4a3aa7068c698abf2b2877a78512c376f.
- Under the same sanitized execution environment and supported elevation, a Python-only child bound127.0.0.1:8819. The exact lsof query returned its unique PID47374 (rc0), and a PING/PONG loopback exchange succeeded. No SUMO or TraCI session was used in this control. Evidence: tcp_listener_control.py and tcp_listener_control_receipt.json.
- The narrow system log query covers2026-09-21 16:28:17..16:28:30 Europe/Berlin/CEST(+0200), including the recorded SUMO start16:28:19.082. Two exact-PID records show kernel notification of validation-category policy at16:28:19.173 and syspolicyd warning at16:28:19.178. The latter says the category violation will likely cause a block in the future. It does not report this particular process blocked. Original JSON is preserved with SHA c876d52647c67f831a63eda1488e8b7ecc499bfcb05889b697ba1e75f9921219.
- Read-only codesign metadata shows the bound1.26 ARM64 executable has a hardened-runtime signature and TeamIdentifierJCDTMS22B4; the diagnostic tool prints Authority=(unavailable). `xattr -l` printed no attributes. These outputs do not establish a valid/invalid gatekeeper assessment or a causal startup block. No signature, policy, quarantine, binary or environment installation was changed.

## What is NOT known

We cannot distinguish delayed loader/OS assessment, SUMO initialization before listening, or a SUMO-specific visibility/launch problem from the eight-second evidence alone. No startup stack/resource snapshot was retained by attempt01. A passing Python control makes an lsof syntax error or general loopback sandbox restriction unlikely, but cannot prove the SUMO process had no special restriction. No observed error identifies a bad network, detector, route, port flag or TraCI method. Config invariants and local XSD pass; they are not dynamic startup proof.

Do not state that OS validation caused the failure, that a60-second wait will solve it, or that a traffic artifact was observed.

## Exact next technical change — Proposed, pending exact review

Test the explicit hypothesis that the previous8s readiness gate was too short. New isolated attempt02 retains one SUMO process, the same original behavior input semantics, same seed17/0–450/step1, same port8819 and PID-ownership checks. Change startup readiness limit8→60s, while preserving180s per-attempt total watchdog/200MB observed output stop-lines.

If no owned listener is present after2s, capture `/bin/ps -p PID -o pid,ppid,pgid,state,wchan,etime,%cpu,command`, then `/usr/bin/sample PID 1 1 -file RUN/startup.sample.txt` once. Diagnostic subprocess deadlines are2s/5s. Retain stdout/stderr/failure status; do not retry sampling. These are pre-step OS observations. They cannot advance traffic; their wallclock cost counts against the same total watchdog. Successful listener detection still requires the exact child PID before connecting and before the first simulationStep. A foreign listener, dead child or60s timeout fails closed.

No automatic SUMO retry is introduced. Attempt02 has a new card/review/approval and immutable raw root. If it fails, preserve all evidence and form a new specific hypothesis before any separately reviewed further technical attempt under the user's continuing authorization. Only the same C/seed17/0–450 diagnostic condition is in scope.

## Tests already completed

- Python TCP/lsof loopback control PASS (real local socket, zero SUMO/TraCI).
-14/14 inherited offline supervisor/observer tests PASS using4 Python fake processes.
-6/6 new deterministic startup tests PASS: immediate listener; delayed listener after the old8s limit; foreign PID rejection; exited process rejection;60s deadline; sample timeout preserved without disabling PID checks.
-58 static checks,3 XML/XSD checks and27 installed getter checks PASS. Scientific input values unchanged. Dynamic observation neutrality and causal identification remain unverified.

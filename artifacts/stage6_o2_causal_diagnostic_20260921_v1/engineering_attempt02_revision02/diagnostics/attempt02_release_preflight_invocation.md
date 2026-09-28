# Attempt02 release preflight invocation correction

- Classification: local preflight invocation error; no SUMO process was started, no TraCI connection was made, and no simulation time advanced.
- Root cause: the parent called `preflight()` with relative card and approval paths. The executor's `no_symlink()` guard requires absolute paths and failed closed with `ValueError: absolute path required`.
- Exact fix: resolve both paths before calling `preflight()` (`Path(...).resolve()`); retain the same card, approval, scientific inputs, and port/PID checks.
- Scope impact: none. This is not a SUMO startup attempt and is not scientific evidence.
- Follow-up root cause: after correcting absolute paths, the local sandbox rejected the preflight's read-only bind to `127.0.0.1:8819` with `PermissionError: [Errno 1] Operation not permitted`. No listener, simulator, observer, or simulation step was created.
- Exact fix: run this same non-launching preflight in the authorized elevated execution context required for the eventual SUMO/TraCI socket test; do not alter the port or any scientific input.

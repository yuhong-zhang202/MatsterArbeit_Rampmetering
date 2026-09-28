# Engineering post-run integrity review — MINIMAL3199 control TECH_RETRY2

**Disposition:** `PASS_ENGINEERING_POSTRUN_INTEGRITY`  
**Scope:** exact-card execution provenance, launch/exit record, resource triggers, staged bytes, and output inventory/hash integrity. No lifecycle/data or scientific outcome analysis was performed.

## Execution and resource record

- Guardian starts: 1; SUMO starts: 1; simulator PID/PGID: `5313`; Guardian PID: `5312`.
- Reservation status: `FINAL_STATUS_HANDED_OFF`; process status: `PROCESS_EXITED`; return code: `0`; stop reason: `null`; retry allowed: `false`.
- Wall-clock: `24.507769 s` / `90 s` trigger. Output payload: `18,261,973 bytes` / `60,000,000 bytes` trigger. Neither trigger was reached.
- SUMO log records completion at 2700 s and 1,333 inserted vehicles. `sumo_error.log`, Guardian stderr, runner stdout/stderr are empty. This is execution-integrity evidence only.

## Provenance and inventory

- FINAL card SHA-256: `b387a750f9f41fe7439d79ead7133fc07ac817fe8da497a8e045433a4accee5a`.
- Execution manifest SHA-256: `551fdfbe78530662f2a437436d8a36813902d5728ac88b03a7a316382d7bca9a`.
- Runtime sidecar SHA-256: `95f3d7bdae0dfd5f629d28e1ebf2bcdb0e957c6eb790f61307442704a82c373d`; runner SHA-256: `4f31c3e1be5d4aba841ebb2ca00a6f7df90f2d6a434819ac83ed262d4401b529`.
- Reservation SHA-256: `0a22193f9dc0d400c3c9f07b1f79087d76daf40ebade3819b9d09dc30bed977c`; output manifest SHA-256: `07cd3cd1707e3717f9401f3e164a932cb6c10196af1461f267869f1d582e5e5e`; execution receipt SHA-256: `f9f783f19cc61d342de09ab7dc6172e56645b7e1604d7447ad6e0582a7bd2348`.
- All 18/18 bound traffic output roles are present; the output manifest independently matches every file size and SHA-256. It inventories 25 run files excluding manifest/receipt; the directory has 27 files including both. No unclassified files were found.
- Payload size recomputed from the file inventory matches the durable reservation. Total directory size including manifest and receipt is `18,269,264 bytes`.

## Staged input binding

- Staged `scenario_control.sumocfg`: 2,802 bytes, SHA-256 `f91c2fa87b12e83e39d27051e01d56f231d9a0a074e6ea445200d294adbf677b`; staged `scenario_control.add.xml`: 3,940 bytes, SHA-256 `354c1dcffc9f4b18d6e92f1dd4658098f0e24b3d2ab30671df4a1faefb6d62f3`.
- Reconstructed the ordered text transformations from the bound rev3 source bytes and confirmed byte-for-byte equality with both staged files: 8 sumocfg output-destination replacements, 1 sumocfg additional-file reference replacement, and 12 additional-XML output-destination replacements. No old attempt output root remains.

## Disposition

Engineering output integrity and provenance checks PASS. The raw is ready for the separate data/lifecycle review. No replay, retry, or additional process was initiated during this review. The raw directory was read-only.

Engineering review JSON SHA-256: `3c7d798178dbb2bdfbddf732f88356621025c25a092167cf6f86dad54e1b117c` (the file hash is reported by the package receipt/index after writing).

# Independent scientific failure review — E1 R900

**Disposition:** `NOT_EVALUABLE`  
**Confidence:** High

No traffic result, R exposure, locked classifier result, or `NO_WITNESS` can be inferred. Guardian and SUMO started once; SUMO exited with code 1 after loading the network and failing during additional-file loading because the configuration referenced REV14's additional XML, whose detector paths targeted the old v16 directory. The run lasted 23.522957 seconds. TraCI and netconvert starts were zero.

The output inventory lacks 12 detector/TLS roles. FCD, lane-change, queue, summary, tripinfo and vehroute XMLs contain no traffic records. Actual R departures, merge exposure, M deterioration, and P/S/L/Candidate A/C outcomes are therefore unavailable. The attempt cannot support a witness or negative witness result.

The adopted second-tier plan stops after a non-evaluable E1. The one-start authorization is consumed and retry is prohibited; no replacement or E2 escalation follows from this attempt.

Reviewed: exact card `f0387580053ad6b862ec2874a4eb55e5c9a468a3f23db561af40d6c9e6499908`; engineering failure receipt `b2268a7b336f3126eb5e6f2def7efa103a355dbe711782046a87009e8cf50574`; data/lifecycle failure receipt `27b39924e3755a1dd20b1b2307bfaa9c95ac343d9db07b9e7731bb94db1631b3`; consumption receipt `17f21d690985069be7c893e90da33ccabc4127382d5a8a88416a38bae74a8c16`; execution receipt `3d4b795ecebe38cc1dc01749b2f2c2c7fd25a9afdbdc7f732c149aeded27c62b`; output manifest `d7d70dc04722bdce1d510961393c79a7095a9e1d658fd3353e57e011d8cca707`.

The project state was corrected before finalizing this review. The reviewer changed no files and started no processes.

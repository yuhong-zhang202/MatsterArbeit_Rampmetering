# Engineering cumulative-discharge design review V1

2026-10-14. Parent transcription of simulation_engineer read-only design and document-readback responses. No implementation, tests, new card or SUMO execution.

Disposition: GO_FOR_BOUNDED_DESIGN_REVIEW_ONLY. Proposed complete-cycle scheduler retains original clipped ALINEA requested state and independently measured C/E/N. Use real D=C−N to choose candidate T minimizing abs(D+r*T/3600−2), with longer T on ties, only at complete boundaries after original admission/ACK/safety checks. T8/T10 is preferred over unobserved T9 as the smallest evidence-informed750 mechanism; existing separate-version observations do not qualify mixed operation. Actual N other than2 stops compensation for investigation, not automatic physical-debt recovery. No shortening yellow/red, extra quota or rate beyond900.

Constant750 and actual two-car packets yields10,10,8,10,10 /48s/10cars. This is conditional arithmetic, not native data. Candidate set supports only720–900 nominal mean; lower requested rates must be explicit UNSUPPORTED instead of clamped. Full300–900 integration remains unresolved.

Reuse generic Command, dynamic producer, real E1/Feedback and original previous-request state. New unified cycle object should bind green/yellow/red per selected T; adapter/bridge use it for deadline, nextSwitch, early quota close and remaining-red readback. Preserve old900 action/check compatibility and03 identity/yellow/body audit. Do not use fixed750 producer as closed-loop evidence or inherit an old numerical exception automatically.

Minimal proposed offline scope: rational constant-rate accounting; dynamic boundaries with unchanged ALINEA state; early-quota/deadline/T8 transitions; true zero, short/excess actual entry, UNKNOWN and partial negative controls. No expansion to a demand grid. Future one750 mixed-cycle native run requires separate exact implementation/card/reviews. Draft1296 endpoint is only a proposal, not a change to old1270.

Document readback found no substantive mistranscription. Engineering requested explicit first-start state: boundt0 initializesC=E=N0; there is no previous complete cycle, so do not invent priorN2. Parent added this before independent data binding. Reviewed draft SHA3888ff5dce3b6818cb296194cce419d7872a137ec9fe64ffeb6093bcb8fdf87f. Scientific design review still required.

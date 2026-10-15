# Measurement review clarification

2026-10-15. Root response to the data review of the proposed minimum plan. This addendum preserves the reviewed plan's exact bytes and data binder. Proposed acceptance clarification, not a new approved experimental rule or permission to execute.

Let D_k=C_k−N_k at a complete packet boundary, I_k the integral of actual original requests during that packet, r_k the request at selection, T_k its actual period and n_k its independently measured releases. Then:

`D_(k+1) = (D_k + r_k*T_k/3600 − 2) + (I_k − r_k*T_k/3600) + (2 − n_k)`.

Report these terms separately: the first is the frozen selector's forecast residual (including existing debt and finite-period choice), the second is the effect of requests changing inside an executing packet, the third is actual complete-packet service shortfall/excess. Application delays are additionally measured directly from original request and first-G binding. Do not relabel all residual as quantization, waiting or a safety event.

For the fixed four-request diagnostic, success requires measured complete-packet n_k=2, independently matching C/N and selections, and visible recovery from any positive accumulated deficit after the final lower300 request can actually be applied. Report the maximum positive deficit and subsequent complete-boundary and terminal deficits. An explained discrepancy without actual debt recovery is insufficient to call tracking successful. If no positive deficit exists at that stage, report that fact rather than invent one. No instantaneous zero, percentage tolerance or universal finite-horizon service guarantee is introduced; a remaining unexplained deficit, saturation/held request or inadequate observation makes tracking NOT_DEMONSTRATED and blocks ALINEA continuation.

At a partial packet, keep actual C/N and elapsed nominal integral, list phase observation support and censor/pending explicitly; do not substitute a full quota or require terminal C=N. The conditional coarse bounds in the separate arithmetic note remain consistency bounds, not allowed service deficits. The held-rate ideal-period quantization reference is likewise not a general empirical acceptance bound.

The future real ALINEA test, if separately released after dynamic success, must retain the same executor source/contract and report original cumulative requested volume and actual volume, including pending requests at cutoff. Formula/communication success alone cannot establish actual tracking or long-run qualification.

Reader compatibility means the exact frozen catalogue mapping: T8/Y2, T9/Y3, the T10/G5/Y3 exception, and T11…24/Y5. The plan's range shorthand “Y2…5” does not authorize arbitrary yellow durations or a T10/Y4 pairing. No unused Y4 configuration or extra simulation point is added.

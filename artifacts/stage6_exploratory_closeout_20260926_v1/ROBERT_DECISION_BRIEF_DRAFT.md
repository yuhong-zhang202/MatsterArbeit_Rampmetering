# Draft for Robert — Stage 6 exploratory mechanism decision

**Status:** draft only; not sent. Prepared from the current Stage 6 evidence, without attributing any position to Robert.

**Subject:** Ramp-metering thesis: exploratory SUMO mechanism gap before formal experiments

Dear Robert,

I have completed a bounded exploratory validation of the synthetic freeway–ramp–urban SUMO network. The old full-network A remains non-evaluable after a failed pre-ramp pairability gate; a later audit found mismatched requested input semantics that explain at least part of the divergence. A new prospective pair matched those requested inputs and passed the pre-ramp gate. A separate M-only sigma0 sensitivity showed ramp-associated local freeway deterioration with clean early spatial chronology, but the default-model A effect size remains difficult to attribute because M vehicles far upstream diverge almost immediately after R appears.

The missing link is moderate metering benefit. With the same default-model network, demand and seed, 22 s green reduced R merge entries by 1500 s from 226 to 170, but did not improve fixed freeway core speed or complete M travel time; R and U trips rose markedly. One prespecified milder 28 s green test admitted 222 R by 1500 s and also failed to improve the freeway, although its urban cost was smaller. A final, one-arm sigma0 sensitivity used the already tested 22 s program against the existing sigma0 A: it again reduced R entries to 170, but M core changes were mixed and complete M travel time was essentially unchanged. Stronger metering produces ramp/urban cost, yet the full freeway–ramp–urban trade-off is not established. These are single-seed synthetic findings, not proof that no controller or configuration can work.

Before I design formal multi-seed experiments, could we decide which scientific direction is appropriate?

1. Should the synthetic merge/scenario be revised to make the freeway response to ramp admission more physically identifiable, or should the current scenario be retained with a narrower claim?
2. Should the next bounded validation use a different control-response design (including an actual ALINEA implementation) rather than further tuning these fixed-time green durations?
3. What level of evidence would you require for a manageable-cost moderate-control leg and for handling the default-model stochastic coupling before freezing the formal protocol?

I can provide the exact run cards, raw outputs, fixed-window plots/tables, and independent scientific reviews. I have kept Stage 6 at `PARTIAL` and have not started the formal experiment grid.

Best regards,
Yuhong Zhang

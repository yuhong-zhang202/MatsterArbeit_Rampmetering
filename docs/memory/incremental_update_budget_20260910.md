# Tencent project-memory incremental update budget — 2026-09-10

Status: **approved update completed within budget**.

## Candidate identity and files

- Fixed MemoryCore volume: `tdai-ramp-metering-memory-v1`
- Fixed service/team/agent/user: `ramp-metering-formal-memory-v1` / `team-masterarbeit-ramp-metering` / `agent-project-memory` / `user-yuhong-zhang`
- Unique proposed update/session ID: `stage2-closeout-20260910-v1`
- Model fixed by the existing reviewed updater: `gpt-4.1-mini`
- Delta candidate: 8,670 bytes, SHA-256 `ea0d3aa4c6be63324bbdbbaecf6d43fd979874814c4b6908f972eeb4c0be89ad`
- Complete L3 candidate: 6,528 bytes, SHA-256 `94c495348fd2dc28bdc1bd22fc0afdd0f23385f8f83cf2ae62f3b090b1ac4bab`

## Approved cost calculation

Current official GPT-4.1 mini text rates checked on 2026-09-10 are USD 0.40 per million input tokens and USD 1.60 per million output tokens. The existing proxy limits each request to at most 20,000 bytes and requests at most 4,096 output tokens. The byte limit is conservatively charged as if every byte were one input token.

```text
per-attempt ceiling
= 20,000 × 0.40 / 1,000,000
  + 4,096 × 1.60 / 1,000,000
= USD 0.0145536

three-attempt hard ceiling
= 3 × USD 0.0145536
= USD 0.0436608
```

The previous formal import consumed 2 successful alias attempts plus 4 zero-token legacy failures, leaving 35 of the combined 41-attempt ceiling. A future three-attempt update would leave at least 32 attempts. Three is a containment ceiling: the prior native L1/L2 pipeline used two successful calls, while the third allows one bounded pipeline continuation. It is not a commitment to make three calls.

Actual usage was expected to be lower than the hard ceiling because UTF-8 bytes overstate input tokens and answers may stop before 4,096 output tokens. The hard ceiling remained the operative execution limit.

## Authorization chain

The initial manifest `incremental_update_approval_20260910_dry_run.json` remains `dry-run-authorized`. The runner accepts that status only with `--dry-run` and rejects it on the paid path. The later explicit approval is recorded separately in `incremental_update_approval_20260910.json` with status `user-approved`.

The paid run used the same displayed candidate hashes and limits. Future updates require a new unique session, new exact hashes and a fresh approval; this completed authorization cannot be replayed.

## Execution result

The user subsequently approved the exact hashes and limits. Update `stage2-closeout-20260910-v1` completed successfully with three model attempts, 13,052 prompt tokens and 908 completion tokens. The execution receipt records a conservative estimate of **USD 0.0066736**, which is 15.3% of the USD 0.0436608 ceiling. This is a ledger estimate at the approved standard input/output rates, not a claim about the provider's finalized invoice. Combined historical use is now 9/41 attempts, leaving 32.

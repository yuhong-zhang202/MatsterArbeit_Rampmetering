# Zero-Cost Layered-Memory Harness — 2026-09-09

## Scope

This is an engineering validation of the installed Tencent MemoryCore image with a local fake Chat Completions endpoint. It does not validate model quality and is not authorization to process real project history.

## Isolation and cost controls

- Tested image: `sha256:9798254a8cc06276b7c5b3c19df49f136fae25d579564e1f01f9c4b9b8cd2d11`.
- Container network mode: `none`.
- The OpenAI API key in macOS Keychain was not read or mounted.
- External model calls: `0`.
- All input was explicitly synthetic.

## Observed result

Status: **passed**.

- L0: two synthetic conversation messages accepted by the native v3 API.
- L1: one atomic memory materialized.
- L2: one scenario memory materialized through the native tool-call loop.
- L3: core memory materialized through the native tool-call loop.
- Native pipeline model steps before the cap exercise: five: one L1 response, two L2 responses, and two L3 responses.
- Native request-body sizes for those five steps were 5,837, 15,490, 16,197, 8,371 and 8,759 bytes. Each requested at most 4,096 output tokens. All fit beneath the proposed 20,000-byte conservative request ceiling.
- Isolation probe: the same queries under a different team/agent/user identity returned no L0, L1, L2, or L3 content.
- Ephemeral outbound-attempt gate: accepted exactly 41 local fake requests and rejected request 42 with HTTP 429.

A separate persistent proxy was then implemented in `scripts/memory/openai_budget_proxy.mjs`. Its fake-upstream regression test rejected a concurrent proxy process and four invalid request classes before budget claim, persisted 17 claims, restored them after a process restart, admitted the remaining 24 requests, and rejected request 42. The test made no external calls. The persisted ledger records a claim before forwarding, so a crash or uncertain upstream outcome consumes rather than refunds an attempt. A crash leaves a lock that requires explicit inspection instead of allowing an unaudited automatic restart.

The first start attempt never reached the gateway because the Colima VM could not bind-mount the macOS Desktop path. A disposable container copy was used instead. A second attempt timed out after ten seconds while the emulated image was still starting. The wait was increased to sixty seconds; the successful run completed in about eleven seconds. These attempts made no external model calls.

## Limitations and acceptance boundary

- Fake responses prove orchestration and storage flow only; they do not prove GPT extraction accuracy, useful recall, source fidelity, or conflict handling.
- The counter inside the original all-in-one harness is process-local. The separate proxy now has a restart-persistent attempt ledger, but it has not yet been connected to the native MemoryCore process or a real OpenAI endpoint.
- The 20,000-byte request ceiling is a conservative transport limit, not an exact tokenizer measurement. Actual token usage must be read from the upstream response and recorded by the persistent proxy.
- The installed image was exercised directly, but its byte-for-byte or source-build equivalence to audited public commit `2ee22397f6091b8cd3ea847bc1edb04d3bec0c94` remains unverified.
- The isolation result covers the tested v3 identity boundary in one local store. It is not a complete adversarial multi-tenant security audit.
- No real project conversation was imported, no automatic capture bridge was enabled, and no Codex provider or base URL was changed.

## Next gate

Before any paid model call, connect MemoryCore to the restart-tested persistent proxy and use a fresh ledger. Present the exact synthetic sample, model, maximum attempts, byte/output ceilings, and worst-case charge for explicit user authorization. Real-history import remains a separate later decision.

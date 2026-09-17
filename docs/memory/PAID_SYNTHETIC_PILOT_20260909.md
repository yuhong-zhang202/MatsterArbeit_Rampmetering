# First Paid Synthetic Layered-Memory Pilot — 2026-09-09

## Authorization and fixed scope

The user explicitly authorized the previously displayed first paid synthetic sample test. The authorized scope was two wholly fictional messages, model snapshot `gpt-4.1-mini-2025-04-14`, a persistent maximum of 41 outbound attempts, a 20,000-byte request-body ceiling and a 4,096-output-token ceiling. Real thesis history import and Codex provider changes were excluded.

## Result of the first attempt

Status: **stopped before model inference because the API credential was invalid**.

- Persistent attempts claimed: 1 of 41.
- Remaining attempts: 40.
- Request body: 5,835 bytes.
- Requested output ceiling: 4,096 tokens.
- OpenAI HTTP status: 401.
- Reported prompt/completion/total tokens: 0/0/0.
- Estimated token charge: USD 0.
- L1/L2/L3 result: not generated; the failure occurred on the first L1 request.
- The container stopped and was removed. The persistent ledger was retained under ignored generated data.

The gateway error reported an incorrect API key. A metadata-only Keychain diagnostic, which did not display the secret, found a 328-character value containing two `sk-` prefixes. The stored value therefore contains two concatenated keys rather than one usable project key. No attempt was made to guess which substring is valid.

## Result after the first credential replacement

The user reported replacing the Keychain value with one key. A metadata-only check found one `sk-` prefix, 128 characters, no whitespace, no non-ASCII characters, no quotes and no prompt label. A later controlled test established the actual cause: macOS `security add-generic-password ... -w` interactive input stored only 128 of 200 synthetic characters. The previously recommended command therefore truncated the user's correctly copied longer key. The temporary synthetic Keychain item was deleted.

The same authorized sample and existing ledger were resumed without changing policy. OpenAI again returned HTTP 401 on the first L1 request.

- Cumulative attempts claimed: 2 of 41.
- Remaining attempts: 39.
- Cumulative reported prompt/completion/total tokens: 0/0/0.
- Cumulative estimated token charge: USD 0.
- L1/L2/L3 result: not generated.

No further credential guesses or API calls are authorized. A newly created complete project key must be copied from the one-time creation view rather than from a later masked/truncated display.

The user then created a fresh key on the correct OpenAI API Keys page. Clipboard metadata showed one `sk-` prefix, 164 characters, ASCII only and no whitespace. Before the interrupted third run could be fully stopped, it submitted one request using the still-truncated 128-character Keychain value and received another HTTP 401. Cumulative state is therefore three claimed attempts, 38 remaining, zero reported tokens and USD 0 estimated token charge. The stopped container and local proxy left no listener. This third 401 does not test the 164-character clipboard secret.

An attempted secret-safe Swift helper did not compile because the local Command Line Tools SDK is incomplete; it did not access or modify the Keychain and was removed. The supported continuation is to paste the still-complete clipboard secret into the existing item through the macOS Keychain Access GUI, which avoids the CLI prompt limit.

## Safe continuation

The existing Keychain entry must be updated through Keychain Access with the complete 164-character clipboard value. The existing paid ledger must not be deleted or reset: a later corrected run resumes with 38 attempts remaining. The runner accepts only an existing ledger whose full policy matches the authorized model and caps.

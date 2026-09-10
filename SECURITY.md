# Security Policy

Natural Voice processes untrusted text (drafts, samples, profiles, LLM output)
as data. Please report vulnerabilities rather than exploiting them.

## Reporting

Open a GitHub issue titled `[SECURITY]` describing the issue class, affected
component, and reproduction steps with synthetic data only. Do not include real
credentials, private writing, or live secrets in reports.

## Scope of concern

- **Credential leakage:** API keys or tokens in code, config files, profiles,
  reports, logs, docs, or examples. (Design: env-only credentials; secret keys
  refused in config files; nothing secret is logged or persisted.)
- **Prompt injection:** draft/profile/model-output text escaping its DATA role
  into instructions (design: delimited prompt blocks; injection-as-data tests).
- **Unsafe deserialization:** malformed profile/config/LLM JSON causing crashes
  or bypassing validation (design: validated loads, typed checks, finite-number
  enforcement).
- **Malicious file handling:** path traversal, oversized inputs, binary payloads
  (design: UTF-8 reads with error handling, 50k-char draft cap, output only to
  explicit user paths, writes gated on validation success).
- **Dependency vulnerabilities:** core is stdlib-only; provider adapters here
  use stdlib HTTP. Report anything that contradicts this.

## Non-goals (will not be treated as vulnerabilities)

- Mock provider returning scripted text (by design, offline testing).
- Real providers requiring network + credentials (documented, user-configured).

## Secrets hygiene for contributors

Never commit `.env`, keys, tokens, private writing, profiles, or drafts.
A pre-commit search for `API_KEY|SECRET|PASSWORD|TOKEN` plus the Phase 8 audit
list is expected before pushing.

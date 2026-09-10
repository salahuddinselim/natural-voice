# Contributing to Natural Voice

## Architecture (read first)

`docs/architecture.md` is mandatory reading. The standing rule:

```text
Core ≠ Provider ≠ Agent
```

- Core (`analyzer/`, `profile/`, `comparison/`, `revision/`, `core/`,
  `natural_voice_config/`) stays platform-independent: no provider SDKs, no
  agent APIs, no credentials, no `if provider == ...` branches.
- Providers implement `llm.interface.LLMProvider` and live in `providers/`.
- Agent integrations are `SKILL.md` files in `adapters/` per
  `docs/adapter-contract.md`.

## Adding a provider

1. Subclass `LLMProvider` (`generate(prompt) -> str`), declare honest
   `capabilities()`, translate failures into `llm.errors`, stdlib-only unless
   an SDK is unavoidable (then it becomes an optional extra, never a core dep).
2. Register it in `providers/__init__.py`.
3. Extend `tests/test_providers.py` contract coverage (generate, normalization,
   errors, capabilities, no secret leakage) with stubbed transport — no network.
4. Document it in `docs/providers.md` with an honest state
   (implemented / experimental / planned).

## Adding an adapter

Follow `docs/adapter-contract.md` + `docs/adapters.md`, add contract tests in
`tests/test_adapters.py`. Never fork core methodology into an adapter.

## Testing

```bash
python -m unittest discover -s tests -v   # all offline; no keys, no network
```

New behavior needs tests with real assertions (values, not just "runs").
Security-relevant paths (injection-as-data, malformed inputs, secret handling)
need explicit tests.

## Security expectations

- Treat drafts, profiles, and LLM output as untrusted data (validate, never exec).
- Never log content (counts/statuses only), never persist samples, never commit
  secrets (see `SECURITY.md` for reporting).
- No detector-evasion features, wording, or "human-score" optimization — PRs
  introducing them will be rejected.

## Code style

Stdlib-first, small modules, documented heuristics labeled HEURISTIC,
deterministic outputs (sorted, no unseeded randomness), JSON-serializable
boundaries between components.

## Pull requests

Describe what changed, what was validated (tests + CLI runs), and what remains
planned. Update affected docs (`docs/`, package READMEs, adapter versions) in
the same PR.

# Natural Voice Architecture

## The core principle

```text
Core ≠ Provider ≠ Agent
```

- **Core** measures writing and enforces methodology. It never imports provider
  SDKs, agent APIs, or credentials, and it behaves identically everywhere.
- **Provider** generates text via the `LLMProvider` interface (`generate(prompt)
  -> str`, plus declared capabilities). Core code never names a provider.
- **Agent adapter** translates one environment's conventions (skill paths,
  invocation style) into core CLI/API calls. Adapters contain no methodology.

```text
Natural Voice Core
│
├── Local components (offline, deterministic, no credentials)
│     ├── analyzer/    measurements
│     ├── profile/     Author Voice Profile builder
│     ├── comparison/  draft-vs-profile consistency reports
│     └── revision/    prompt construction, parsing, validation
│         (revision calls the LLM, but only through LLMProvider)
│
├── Provider interface (llm/)
│     ├── interface.py      LLMProvider.generate
│     ├── models.py         LLMRequest / LLMResponse + normalization
│     ├── capabilities.py   declared abilities + negotiation
│     ├── errors.py         standardized hierarchy (auth, rate-limit,
│     │                       timeout, invalid-response, unsupported, config)
│     └── retry.py          transient-failure retries (conservative default)
│
├── Providers (providers/) — configured at runtime, never imported by core
│     ├── mock/               offline, no credentials (tests, dry runs)
│     ├── openai_compatible/  stdlib HTTPS, endpoint + key from environment
│     └── anthropic/          stdlib HTTPS, key from environment
│
├── Configuration (natural_voice_config/)
│     ├── models, env/file loader (arg > CLI > env > file > default),
│     │   secrets from environment only, secret-bearing files refused
│     ├── versions + profile compatibility gate
│     └── opt-in logging (counts and statuses only — never content)
│
├── Unified CLI (natural_voice_cli → `natural-voice`):
│     profile build · compare · revise · providers · validate · version
│
└── Agent adapters (adapters/opencode|claude|codex/SKILL.md)
      Same workflow (Profile → Analyze → Compare → Revise → Validate);
      only discovery paths and invocation style differ.
```

## Data flow (full chain)

```text
Samples → analyzer → profile builder → voice-profile.json (user-owned)
Draft + voice-profile.json → comparison → consistency report
Draft + profile + report + principles → revision engine → LLMProvider
  → validated revision (numbers/citations kept, drift-checked)
```

## Extension rules

- New provider: implement `LLMProvider` (+ capabilities), register in
  `providers/`, satisfy `tests/test_providers.py` contract tests. No core edits.
- New agent: add `adapters/<name>/SKILL.md` per `docs/adapter-contract.md`.
- New analyzer feature / revision mode / validation rule: core-side, with tests;
  never `if provider == ...` branches in core.
- Profiles, reports, and results stay provider-neutral (provider name appears
  only as result metadata); no credentials ever enter stored artifacts.

# Providers

Providers implement `LLMProvider.generate(prompt) -> str` plus declared
capabilities. The revision engine never imports a provider module; construction
happens via the `providers` registry or dependency injection.

## Status

| Provider | State | Credentials | Notes |
|---|---|---|---|
| `mock` | implemented | none (offline) | Deterministic scripted output; all unit tests |
| `openai-compatible` | implemented | `OPENAI_API_KEY` (or `api_key=`) | stdlib HTTPS to `/chat/completions`; `base_url` overridable; untested live here |
| `anthropic` | implemented | `ANTHROPIC_API_KEY` (or `api_key=`) | stdlib HTTPS to `/v1/messages`; untested live here |

"Implemented" means code-complete against the documented API with contract tests
over stubbed transport — not live-verified against vendor endpoints. Anything
else is **planned**, not present.

## Configuration

Non-secret settings via `natural_voice_config` (function arg > CLI flag >
`NATURAL_VOICE_*` env > JSON file > default): provider, model, temperature,
max_tokens, timeout, retries, base_url, mode, verbosity. Keys via environment
only; config files containing secret-like keys are refused outright.

## Capabilities and negotiation

Providers declare `structured_output / streaming / system_messages /
temperature / max_tokens`. The engine requests JSON in-prose and parses
robustly (JSON preferred, plain-text fallback), so both paths are safe; adapters
use `negotiate_structured_output` only to decide whether to also set native
format flags. Streaming is optional end-to-end: supported adapters may expose
chunks, but the engine always works on complete responses.

## Errors and retries

Standard hierarchy: `ProviderError` (base) → `AuthenticationError`,
`RateLimitError`, `TimeoutError`, `InvalidResponseError`,
`UnsupportedCapabilityError`, `ConfigurationError`. Only transient failures
(timeouts, rate limits, transport blips) are retried (default: 1 retry,
configurable); auth/config/parse/capability failures propagate immediately.
Provider-native payloads (strings, dicts, content blocks) are normalized to
`LLMResponse` before engine code sees them.

## Limitations

- No SDKs are used or required; behavior against real endpoints follows their
  documented HTTP APIs and may drift with vendor changes.
- Local-model support is architectural (any `LLMProvider` qualifies), not bundled.
- Every provider receives equivalent semantic instructions (profile, comparison,
  constraints, draft, request) — see cross-provider consistency tests.

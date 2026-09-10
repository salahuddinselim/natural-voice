# Natural Voice

Natural Voice is an open-source, cross-LLM writing framework. It helps transform
AI-assisted or rough-draft text into writing that is natural, clear, coherent, and
consistent with the author's genuine voice.

> Improve the writing without replacing the author's identity, ideas, reasoning, or genuine voice.

## Goal

Natural, clear, author-consistent writing — not artificial imperfections, not generic
"human-sounding" rewrites. The system asks *"What does THIS AUTHOR naturally sound
like?"* and edits inside those characteristics.

## Architecture

```text
                    Natural Voice
                         │
       ┌─────────────────┼─────────────────┐
       │                 │                 │
    Analyzer          Profile          Comparison
     (local)          (local)            (local)
                                           │
                                           ▼
                                      Revision (validated)
                                           │
                                           ▼
                                      LLM Layer
                                      (`llm/`: neutral interface,
                                       capabilities, errors, retry)
                                           │
                ┌──────────────────────────┼──────────────────┐
                ▼                          ▼                  ▼
             OpenCode                   Claude              Codex
             Adapter                    Adapter             Adapter
```

The core is platform-independent: identical methodology, tools, and validation
run under OpenCode, Claude Code, Codex, or the standalone `natural-voice` CLI.
The LLM is used only for generation/revision, guided and checked by local
components. Local phases (analyzer, profiler, comparison) never transmit text
anywhere; the revision step sends the draft to the configured provider — see
`analysis/revision-spec.md` §7. Details: `docs/architecture.md`.

- `core/` — methodology: principles, rewriting pipeline, voice model, research.
- `analysis/` — profile, comparison, and revision specifications.
- `analyzer/`, `profile/`, `comparison/`, `revision/` — pipeline code (stdlib-only).
- `llm/` — provider-neutral interface, request/response models, capabilities,
  error hierarchy, retry helper, offline mock.
- `providers/` — registry + mock / OpenAI-compatible / Anthropic adapters.
- `natural_voice_config/` — configuration (arg > CLI > env > file > default),
  versions + profile compatibility, opt-in logging.
- `natural_voice_cli/` — unified `natural-voice` command.
- `adapters/opencode|claude|codex/` — thin platform skills (same workflow).
- `docs/` — architecture, adapter contract, installation, providers, adapters.
- `examples/` — synthetic demonstrations only (never private writing).

## Current Status

```text
v0.8 — Portable core: providers + cross-platform adapters + unified CLI
```

Install: `pip install .` → `natural-voice version` (see `docs/installation.md`).
Configure providers via environment (`docs/providers.md`). Contribute via
`CONTRIBUTING.md`; report vulnerabilities per `SECURITY.md`.

Licensed under the [MIT License](LICENSE).

## Supported Platforms

- **OpenCode** — `adapters/opencode/SKILL.md`, live at `.opencode/skills/natural-voice/SKILL.md`
- **Claude Code** — `adapters/claude/SKILL.md`, live at `.claude/skills/natural-voice/SKILL.md`
- **Codex** — `adapters/codex/SKILL.md`, live at `.codex/skills/natural-voice/SKILL.md` (also referenced from `AGENTS.md`)
- **ChatGPT** — `adapters/chatgpt/SKILL.md`; no local skill discovery exists on
  this platform, so install by pasting `adapters/chatgpt/custom-gpt-instructions.md`
  into a Custom GPT or Project's instructions field

See `docs/adapters.md` for the full conformance table and `docs/installation.md`
for per-platform install steps.

## Research Foundation

Informed by **Nguyen, Hatua, Sung — "How to Detect AI-Generated Texts?"** (see
`core/research.md` and `references/research-foundation.md`). The paper's features are
used as future writing-analysis signals, never as an authorship detector. Reported
results (e.g. RF/XGB F1 ≈ 0.9993) are cited strictly with their experimental context
(the paper's Wikipedia setup) and are not generalized.

Step 4 of the rewriting pipeline (`core/rewriting.md`, "identify unnecessary/generic
wording") also draws on the concrete phrasing catalog in
`references/ai-phrasing-patterns.md`, adapted from
[Wikipedia:Signs of AI writing](https://en.wikipedia.org/wiki/Wikipedia:Signs_of_AI_writing)
(WikiProject AI Cleanup). Same rule as the paper: the catalog is cited, its use here
is a Natural Voice engineering decision, and a match is evidence about phrasing
quality — never about authorship.

## Important Boundary

Natural Voice does not guarantee or advertise:

- AI detector bypass
- Turnitin bypass
- GPTZero bypass
- "100% human" scores
- undetectable AI output

It focuses on writing quality, authenticity, and voice consistency. External AI-text
detectors are probabilistic and domain-dependent.

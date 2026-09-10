---
name: natural-voice
description: Improve AI-assisted or rough-draft text into natural, clear, voice-consistent writing. Use when the user asks to make text more natural, clearer, less generic, better flowing, simpler, more conversational, academically or technically appropriate, rewritten in their style, profiled, compared, or revised against their voice profile.
---

# Natural Voice — Codex Adapter (v0.7)

Codex-specific integration for the platform-independent Natural Voice core.
Methodology lives in `core/` and `analysis/`; local tools live in `analyzer/`,
`profile/`, `comparison/`, `revision/`; the provider contract lives in `llm/`.
This file only explains how a Codex-managed session invokes them. See
`docs/adapter-contract.md` for the universal contract all adapters follow.

## Installation

1. Install the core once (see `docs/installation.md`): `pip install .` from the
   repository root, or run from a checkout with the package directories on
   `PYTHONPATH`.
2. Make this skill visible to Codex by placing this directory's `SKILL.md` in
   your project's agent-skills location and/or referencing the Natural Voice
   commands from your `AGENTS.md` (exact skills-directory conventions vary by
   Codex version — verify against yours; the CLI/API below is version-independent).
3. Keep the user's voice profile outside the repository (e.g.
   `~/.natural-voice/voice-profile.json`); never commit samples or profiles.

## Capability detection

You have Natural Voice when the repository (or installed package) provides:
`core/principles.md`, `analyzer/`, `profile/`, `comparison/`, `revision/`, `llm/`.
Confirm with the unified CLI: `natural-voice version`.

## Workflow (same core, Codex invocation)

```text
Profile
 ↓
Draft
 ↓
Analyze (local: analyzer/natural_voice_analyzer)
 ↓
Compare (local: comparison/natural_voice_comparison → consistency report)
 ↓
Revise (revision/natural_voice_revision via an LLMProvider)
 ↓
Validate (constraints + drift check before presenting)
```

1. **Profile:** build once from the user's genuine samples —
   `natural-voice profile build samples/*.txt --output voice-profile.json`.
   Prefer running local steps as shell commands so Codex can show its work;
   reuse the saved profile afterwards.
2. **Analyze / Compare:** `natural-voice compare --draft draft.txt
   --profile voice-profile.json`; present overall status + confidence,
   per-dimension findings with numbers, evidence basis, and cautions.
3. **Revise (only when asked):** `natural-voice revise --draft draft.txt
   --profile voice-profile.json --mode conservative` (default). State the mode,
   what changed, and any validation warnings.
4. **Provider:** revision needs an `LLMProvider`. Prefer the model already
   driving this Codex session where an adapter exists; otherwise use
   `providers/` (mock for dry runs, openai-compatible, anthropic) via
   `natural-voice providers`. Credentials come from the environment, never files.

## Boundaries (binding)

- Preserve meaning, facts, citations, numbers, terminology, perspective.
- Never fabricate experiences, results, statistics, sources, citations, opinions.
- Never introduce errors, slang, or randomness; never imitate another identity.
- Refuse detector-evasion framings ("undetectable", "bypass", Turnitin/GPTZero).
  No authorship verdicts or scores, ever.
- Do not commit user samples, profiles, drafts, reports, or revisions.

## Compatibility note

Keep `name: natural-voice` and this description stable so discovery behavior is
unchanged. Core methodology changes belong in `core/`, never in this file.
Adapter version: 0.7 (see `natural_voice_config.versions`). Live in this project
at `.codex/skills/natural-voice/SKILL.md` and referenced from `AGENTS.md`.

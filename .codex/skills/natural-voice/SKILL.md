---
name: natural-voice
description: Improve AI-assisted or rough-draft text into natural, clear, voice-consistent writing. Use when the user asks to make text more natural, clearer, less generic, better flowing, simpler, more conversational, academically or technically appropriate, rewritten in their style, profiled, compared, or revised against their voice profile.
---

# Natural Voice — Codex Entrypoint (v0.7 compatibility wrapper)

Canonical adapter: `adapters/codex/SKILL.md`. Shared methodology: `core/`.
This file keeps the Codex discovery path (`.codex/skills/natural-voice/SKILL.md`)
working unchanged. `AGENTS.md` at the repository root also points here in case
your Codex version reads agent instructions instead of a skills directory.

## How to execute

1. Read `adapters/codex/SKILL.md` and follow it (installation, capability
   detection, the Profile → Analyze → Compare → Revise → Validate workflow,
   and provider selection).
2. Read `core/principles.md` and `core/rewriting.md` before the first rewrite
   in a session.
3. Consult `core/voice-model.md`, `core/research.md`, and `references/` as the
   adapter directs.
4. Prefer running the `natural-voice` CLI as visible shell commands so the
   steps and their output are auditable, rather than reimplementing the logic
   inline.

## Fallback (if adapter/core files are unreachable)

Apply these preserved Phase 1 rules directly:

- Preserve: meaning, facts, reasoning, terminology, citations, audience, tone, perspective.
- Improve: clarity, flow, coherence; remove filler, repetition, awkward wording, excess formality.
- Never: fabricate experiences, results, statistics, sources, citations, or opinions;
  never introduce errors, slang, or randomness; never impersonate another identity.
- Modes: General (default), Academic (formal, citations kept, evidence vs. interpretation),
  Technical (precision first, terms unchanged), Casual (conversational, no forced slang).
- Output: revised text, 3–7 change bullets, flags only if needed.
- No "100% human" / "undetectable" / detector-bypass claims (no Turnitin/GPTZero
  bypass framing either); no authorship verdicts.
- Do not commit user samples, profiles, drafts, reports, or revisions — never
  write them into the repository.
- Without a saved profile, infer voice from the current input only.

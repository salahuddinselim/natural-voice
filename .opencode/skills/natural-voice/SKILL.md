---
name: natural-voice
description: Improve AI-assisted or rough-draft text into natural, clear, voice-consistent writing. Use when the user asks to make text more natural, clearer, less generic, better flowing, simpler, more conversational, academically or technically appropriate, rewritten in their style, or preserved in their voice.
---

# Natural Voice — OpenCode Entrypoint (v0.2 compatibility wrapper)

Canonical adapter: `adapters/opencode/SKILL.md`. Shared methodology: `core/`.
This file keeps the OpenCode discovery path (`.opencode/skills/natural-voice/SKILL.md`)
working unchanged.

## How to execute

1. Read `adapters/opencode/SKILL.md` and follow it.
2. Read `core/principles.md` and `core/rewriting.md` before the first rewrite in a session.
3. Consult `core/voice-model.md`, `core/research.md`, and `references/` as the adapter directs.

## Fallback (if adapter/core files are unreachable)

Apply these preserved Phase 1 rules directly:

- Preserve: meaning, facts, reasoning, terminology, citations, audience, tone, perspective.
- Improve: clarity, flow, coherence; remove filler, repetition, awkward wording, excess formality.
- Never: fabricate experiences, results, statistics, sources, citations, or opinions;
  never introduce errors, slang, or randomness; never impersonate another identity.
- Modes: General (default), Academic (formal, citations kept, evidence vs. interpretation),
  Technical (precision first, terms unchanged), Casual (conversational, no forced slang).
- Output: revised text, 3–7 change bullets, flags only if needed.
- No "100% human" / "undetectable" / detector-bypass claims; no authorship verdicts.
- v0.2 has no persistent profiles; infer voice from current input only.

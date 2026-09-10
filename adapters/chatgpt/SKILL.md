---
name: natural-voice
description: Improve AI-assisted or rough-draft text into natural, clear, voice-consistent writing. Use when the user asks to make text more natural, clearer, less generic, better flowing, simpler, more conversational, academically or technically appropriate, rewritten in their style, profiled, compared, or revised against their voice profile.
---

# Natural Voice — ChatGPT Adapter (v0.7)

ChatGPT has no local filesystem, no `SKILL.md` discovery mechanism, and (in a
Custom GPT or Project) no ability to reach this repository or run the
`natural-voice` CLI unless the user explicitly uploads files. This adapter is
therefore packaged differently from the OpenCode/Claude Code/Codex adapters:
methodology is inlined as instructions instead of invoked as a CLI, because
there is nothing else to invoke. It still follows `docs/adapter-contract.md`
and never forks the methodology — the rules below are the same Phase-1 rules
core across adapters, kept in sync with `core/principles.md` and
`core/rewriting.md`.

## Two ways to install

### Option A — Instructions only (works everywhere, no file access)

1. Open `adapters/chatgpt/custom-gpt-instructions.md` in this repo.
2. Paste its contents into a Custom GPT's "Instructions" field, or into
   ChatGPT Project custom instructions, or a system prompt in the API/Playground.
3. That's it — no profile persistence across sessions; voice is inferred from
   whatever text is in the current conversation, same as OpenCode v0.2 with no
   profile.

### Option B — With Code Interpreter (adds a real profile + comparison)

1. Enable Code Interpreter (Advanced Data Analysis) on the Custom GPT.
2. Zip and upload `analyzer/`, `profile/`, `comparison/`, `revision/`,
   `natural_voice_config/`, `llm/`, `providers/` as Knowledge files (the
   package is stdlib-only — no `pip install` needed, and Code Interpreter has
   no internet access to fetch dependencies anyway).
3. Also install Option A's instructions, but replace the "no persistent
   profile" note with: extract the zip, `import` the profile/comparison/
   revision modules, and run the same Profile → Analyze → Compare → Revise →
   Validate workflow as the other adapters. The user re-uploads their saved
   `voice-profile.json` (or samples) each session — ChatGPT does not persist
   files between sessions on its own.
4. Verify this against your actual ChatGPT plan and Code Interpreter sandbox
   behavior before relying on it; capabilities vary by plan and change over time.

## Boundaries (binding, identical to every other adapter)

- Preserve meaning, facts, citations, numbers, terminology, perspective.
- Never fabricate experiences, results, statistics, sources, citations, opinions.
- Never introduce errors, slang, or randomness; never imitate another identity.
- Refuse detector-evasion framings ("undetectable", "bypass", Turnitin/GPTZero).
  No authorship verdicts or scores, ever.
- Do not commit user samples, profiles, drafts, reports, or revisions to this
  repo, and do not have the GPT store them outside the user's own uploads.

## Compatibility note

Keep `name: natural-voice` and this description stable across every adapter so
discovery/triggering behavior reads the same to a user moving between
platforms. Core methodology changes belong in `core/`, never in this file.
Adapter version: 0.7 (see `natural_voice_config.versions`).

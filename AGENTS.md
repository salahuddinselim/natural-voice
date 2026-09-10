# Agent Instructions

This repository ships **Natural Voice**, a writing-quality skill (not an AI
detector, not a detector-bypass tool). If the user asks to make text more
natural, clearer, less generic, better-flowing, more conversational, or
rewritten to match their own voice, follow `.codex/skills/natural-voice/SKILL.md`
(or `adapters/codex/SKILL.md` directly).

Read `docs/adapter-contract.md` for the workflow and boundaries every agent
integration in this repo must follow (Profile → Analyze → Compare → Revise →
Validate; no fabrication; no detector-evasion framing; no authorship verdicts;
never commit user samples, profiles, drafts, reports, or revisions).

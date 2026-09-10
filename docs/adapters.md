# Agent Adapters

```text
Core
 ↓  (CLI: natural-voice … / Python APIs)
Adapter (platform conventions: skill file, invocation style)
 ↓
Agent (OpenCode / Claude Code / Codex / standalone use)
```

## Available adapters

| Adapter | Skill file | State |
|---|---|---|
| OpenCode | `adapters/opencode/SKILL.md` (live at `.opencode/skills/natural-voice/SKILL.md`) | implemented, live |
| Claude Code | `adapters/claude/SKILL.md` (live at `.claude/skills/natural-voice/SKILL.md`) | implemented, live (live-session verification pending) |
| Codex | `adapters/codex/SKILL.md` (live at `.codex/skills/natural-voice/SKILL.md`, referenced from `AGENTS.md`) | implemented, live (live-session verification pending) |
| ChatGPT | `adapters/chatgpt/SKILL.md` + `adapters/chatgpt/custom-gpt-instructions.md` | implemented as inlined instructions (no local CLI access — see adapter for why) |

All four expose the identical workflow and boundaries (no fabrication, no
artificial errors, detector-evasion refused, no authorship verdicts). Only
discovery paths and invocation idioms differ; methodology is never forked.
ChatGPT is the one exception to "invoke the CLI": it has no filesystem access
by default, so its adapter inlines the same Phase 1 rules as instructions
instead — see `adapters/chatgpt/SKILL.md` for the two install options.

## Creating a new adapter

1. Read `docs/adapter-contract.md` and copy the nearest existing `SKILL.md`.
2. Keep `name: natural-voice` and the trigger description stable.
3. Document: invocation, profile location, draft passing, result handling,
   provider configuration, installation path.
4. Add contract coverage in `tests/test_adapters.py` (frontmatter, core
   references, boundaries, privacy, version).
5. Do not modify core logic to fit the platform — extend the adapter instead.

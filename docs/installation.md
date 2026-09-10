# Installation

## 1. Install Natural Voice (once)

Requirements: Python 3.10+, no third-party runtime dependencies.

```bash
git clone <repo-url> && cd natural-voice
pip install .
```

This installs the analyzer, profile, comparison, revision, config, CLI,
provider, and adapter-registry packages, plus the `natural-voice` command.
Verify: `natural-voice version` (expect component versions incl. 0.8.0).

Without installing, run from a checkout by putting the package directories
(`analyzer/`, `profile/`, `comparison/`, `revision/`, `natural_voice_config/`,
`natural_voice_cli/`) and the repo root (for `llm`, `providers`, `adapters`)
on `PYTHONPATH`.

## 2. Build an author profile

```bash
natural-voice profile build "my-samples/*.txt" --output ~/.natural-voice/voice-profile.json
natural-voice validate ~/.natural-voice/voice-profile.json
```

Samples stay yours: they are measured locally and never stored or transmitted.

## 3. Select an LLM provider (only needed for `revise`)

```bash
natural-voice providers
```

- Offline/dry runs: `--provider mock` with `--mock-echo|--mock-text|--mock-file`.
- OpenAI-compatible endpoint: `--provider openai-compatible --model <name>`
  with `OPENAI_API_KEY` set (custom endpoint via config `base_url`).
- Anthropic: `--provider anthropic --model <name>` with `ANTHROPIC_API_KEY` set.

Credentials come from the environment only. `analyze`, `profile build`,
`compare`, and `validate` never need a provider or network access.

## 4. Select an agent integration

- **OpenCode:** the live skill entrypoint is
  `.opencode/skills/natural-voice/SKILL.md` (points at `adapters/opencode/`).
- **Claude Code:** the live skill entrypoint is
  `.claude/skills/natural-voice/SKILL.md` (points at `adapters/claude/`).
  Copy that file (and this repository) into any project where you want the
  skill discoverable; verify the exact skills-directory convention against
  your Claude Code version.
- **Codex:** the live skill entrypoint is
  `.codex/skills/natural-voice/SKILL.md` (points at `adapters/codex/`), and
  `AGENTS.md` at the repo root references it too, since Codex conventions vary
  by version. Copy whichever of the two your Codex version reads.
- **ChatGPT:** no local skill discovery exists. Paste
  `adapters/chatgpt/custom-gpt-instructions.md` into a Custom GPT's
  Instructions field (or Project custom instructions); see
  `adapters/chatgpt/SKILL.md` for an optional Code Interpreter setup that adds
  a real profile/comparison step.

Only integrations documented here exist; anything else is planned, not promised.

## 5. Use

```bash
natural-voice compare --draft draft.txt --profile voice-profile.json --pretty
natural-voice revise --draft draft.txt --profile voice-profile.json \
  --mode conservative --provider openai-compatible --output revised.txt
```

The same `voice-profile.json` works from OpenCode, Claude, Codex, or the
standalone CLI (subject to the compatibility check).

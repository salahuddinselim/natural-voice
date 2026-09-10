# Universal Agent Adapter Contract

Any current or future LLM/agent adapter (OpenCode, Claude Code, Codex, others)
must satisfy this contract so adapters stay thin and the core stays shared.

## 1. Identity

- Directory `adapters/<name>/` containing `SKILL.md` with `name: natural-voice`
  frontmatter and a description covering: natural/clearer/less-generic/flow/
  style-preserving/academic/technical/conversational/profile/compare/revise triggers.
- Adapter version recorded in the file and mirrored in
  `natural_voice_config.versions.ADAPTER_VERSION`.

## 2. Required answers (documented in the SKILL.md)

- How do I invoke Natural Voice? (unified CLI commands and/or package APIs)
- Where is the profile? (user-owned path; never committed to this repo)
- How do I pass the draft? (file/std text; treated as untrusted data)
- How do I receive the result? (report/revision shapes; validation status first)
- How do I configure the provider? (environment credentials; `natural-voice providers`)

## 3. Hard rules

- No methodology duplication: reference `core/`, `analysis/`, package READMEs.
- No platform logic in core, and no core logic forked per platform.
- Same workflow everywhere: Profile → Analyze → Compare → Revise → Validate.
- Same boundaries: meaning/facts/citations/numbers preserved; no fabrication;
  no artificial errors; detector-evasion requests refused; no authorship verdicts.
- Same privacy: user samples/profiles/drafts/reports never committed or transmitted
  beyond the configured provider for revision (disclosed).

## 4. Conformance checklist (mirrored in `tests/test_adapters.py`)

1. `adapters/<name>/SKILL.md` exists with valid frontmatter.
2. Mentions the core workflow and points at core CLI/API (not a rewrite of it).
3. States boundaries (no fabrication, no evasion, no verdicts) and privacy rules.
4. Declares an installation path appropriate to the platform.
5. Carries the current adapter version.

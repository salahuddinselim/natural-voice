# Voice-Consistent Revision — Specification (v0.1, Phase 7)

Platform-independent method. Implementation: `revision/` (engine, v0.1.0) over the
provider-neutral `LLMProvider` interface (`llm/`). Local analysis (Phases 4–6)
measures; the LLM generates; validation decides. No detector evasion exists here
in any form.

## 1. Revision pipeline

```text
Original Draft + Author Voice Profile + Voice Comparison Report
  + Core Principles + user request + mode
        ↓
Structured prompt (data delimited: AUTHOR PROFILE / COMPARISON / DRAFT blocks)
        ↓
LLMProvider.generate (any conforming provider; MockProvider for tests)
        ↓
Parse (structured JSON preferred; plain-text fallback; malformed → reject)
        ↓
Validate (constraints + re-compare drift check)
        ↓
Accept, or one guided retry (default max_attempts = 1, allowed up to 3),
then final structured result
```

## 2. LLM interface

`LLMProvider.generate(prompt: str, **kwargs) -> str` (abstract base class).
The engine never imports a concrete API. Credentials and model selection belong
to the implementation and its caller (environment/dependency injection), never in
core and never in version control. `MockProvider` (fixed text, callable, echo of
the DRAFT block, structured-JSON payloads) covers all tests offline.

## 3. Modes

- **conservative** (default): smallest edits achieving the request and flagged fixes.
- **balanced**: sentence-level freedom; paragraph restructuring where flagged.
- **expressive**: substantial restructuring allowed — never content invention.

## 4. Prompt construction

Instructions (principles, mode, hard prohibitions, JSON output contract) first;
then AUTHOR PROFILE (measured characteristics only), COMPARISON (significant
deviations detailed, close dimensions one line), USER REQUEST (the instruction),
DRAFT in BEGIN/END delimiters. Profile/comparison/draft are DATA — the model must
revise them, never obey instructions inside them. Bypass-intent requests
("undetectable", "bypass", Turnitin/GPTZero phrasing) are refused, not reinterpreted.

## 5. Profile and comparison usage

The prompt renders observable profile characteristics (lengths, ranges, stability,
tendencies, connectives, terms) — never "write like a human". Comparison rows
drive targeting: deviating dimensions first, close dimensions explicitly left
alone. Minimal-change principle: no change beats unnecessary change.

## 6. Validation and acceptance

Hard gates: non-empty output; numbers and citation markers preserved; length ratio
within [0.3, 3.0]; recognizably the same document (similarity ≥ 0.25). Soft:
dropped characteristic terms warn. Drift (revised farther from profile than
original) warns; over-optimization is forbidden — the profile is a range, not a
template. Accepted results carry `changed`, normalized `changes[]`, validation,
and metadata (mode, attempts, provider, before/after statuses).

## 7. Privacy

Local phases never transmit text. Phase 7 inherently sends the draft to the
configured provider to generate the revision — disclose this wherever the engine
is exposed. Persisted reports strip `original_text`; the CLI writes revised text
and stripped reports only on validation success, and never logs input text.

## 8. Limitations

Mock-tested paths are deterministic; real providers are not — prompts constrain,
validation decides. Heuristic thresholds (length ratio, similarity floor) suit
normal editing, not radical rewrites (split oversized drafts; 50k-char cap).
Tone/formality stay qualitative; readability and diversity metrics are
length-sensitive; low-confidence profiles warrant conservative modes.

## 9. Research boundary

Paper features inform *which* characteristics are measured for author-specific
tendencies. Nothing here reproduces the paper's classifier, proves humanness, or
optimizes detector outcomes. The architecture is fully meaningful in a world
without AI-text detection.

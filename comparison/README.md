# Natural Voice Comparison Engine (v0.1.0)

Compares a new draft against an Author Voice Profile and produces a
**style-consistency report**: which dimensions are close, moderately different,
or significantly different from the author's established characteristics.

This is not an AI detector. The report contains no authorship scores,
probabilities, verdicts, or detector-related outputs of any kind.

## Python API

```python
from natural_voice_comparison import compare_draft, compare_draft_file

report = compare_draft(draft_text, profile)
report = compare_draft(draft_text, profile, weights={"ngrams": 0.5},
                       draft_context="casual")
report = compare_draft_file("draft.txt", "profile.json")
```

`report` is JSON-serializable. Raises `TypeError` for non-string drafts and
`ValueError` for invalid profiles, bad weights, or unreadable files. Empty drafts
return an all-`unavailable` report instead of crashing.

## CLI

Run from this directory (`comparison/`):

```bash
python -m natural_voice_comparison --draft draft.txt --profile profile.json --pretty
python -m natural_voice_comparison --draft draft.txt --profile profile.json --output report.json --pretty
python -m natural_voice_comparison --draft draft.txt --profile profile.json --draft-context casual
python -m natural_voice_comparison --draft draft.txt --profile profile.json --weights '{"ngrams": 0.5}'
```

Exit 1 with a stderr message on failure, 2 on bad CLI usage. Draft text never
appears in output or logs.

## How comparison works

1. Draft analyzed once with the Phase 4 analyzer; profile loaded once and validated.
2. Numeric metrics: inside profile `typical_range` → close; else z-score bands
   (|z| ≤ 2 moderate, above significant); zero-spread profiles use the ±20%/±40%
   relative fallback. Missing values → `unavailable`, never invented.
3. Phrase overlap (N-grams, shared terms/connectives): presence-weighted overlap
   (≥0.5 close, ≥0.2 moderate, else significant), always with the caveat that
   topic/context differences explain low overlap.
4. Dimension status = mean of metric scores (0/1/2) with cutoffs 0.5/1.25.
   Overall = weight-averaged dimension scores, same cutoffs. Default weights:
   sentence/paragraph/vocabulary 1.0, punctuation/readability/cohesion 0.8,
   ngrams 0.7. All bands are project heuristics, documented in
   `analysis/comparison-spec.md`.
5. Overall confidence = weaker of profile evidence and draft length
   (<100 words low, <400 medium, else high).

## Report shape

`comparison_version`, `metadata` (versions, word counts, contexts, weights used),
`overall{status, confidence}`, per-dimension `{status, metrics[], explanations[],
notes[]}` (each metric carries profile mean/range, draft value, deviation, status —
ready for future visualization), `summary[]`, `limitations[]`.

## Limitations

- Heuristic bands, not validated science; thin profiles and short drafts cap confidence.
- N-gram overlap is topic-sensitive by design; low overlap is a caveat, not a verdict.
- No draft comparison across different profile contexts without an explicit label;
  mismatches warn rather than accuse.
- Descriptive only: never interpret output as quality or authorship judgment.

## Privacy

Fully local: no uploads, no APIs, no model downloads, no draft/profile storage or logging.
Inputs are validated as data and never executed.

# Draft vs Profile Comparison — Specification (v0.1, Phase 6)

Platform-independent method. Implementation: `comparison/` (v0.1.0). This spec is
the contract; code docstrings carry the same rules. Everything here is descriptive
style comparison — never authorship determination.

## 1. Comparison dimensions

Seven dimensions, each with its own metrics (see `comparison/natural_voice_comparison/report.py`
for the exact metric list):

- **sentence_structure** — average/median length, short/medium/long ratios, length-variation band
- **paragraph_structure** — average/median words, sentences per paragraph, size-variation band
- **vocabulary** — diversity (TTR), Guiraud's R, word lengths, shared characteristic terms
- **punctuation** — overall density + per-mark rates
- **readability** — the five implemented estimates, nulls skipped
- **cohesion** — pronoun ratio, transition rate, shared connectives
- **ngrams** — bigram/trigram overlap with recurring profile patterns

## 2. Numerical comparison

Draft value vs. profile aggregate `{mean, std, typical_range}`:

1. Inside `typical_range` (mean ± cross-sample std) → `close`.
2. Otherwise, usable std: z = (draft − mean)/std; |z| ≤ 2 → `moderately_different`,
   |z| > 2 → `significantly_different`.
3. Zero/missing std (e.g. single-sample profiles): relative-difference fallback —
   ≤20% → close, ≤40% → moderately_different, else significantly_different
   (the `feature-spec.md` fallback bands).
4. Missing profile mean or draft value → `unavailable` with a reason. Never invented.

Stable features (std ≈ 0) are handled by rule 3, so division by zero is impossible
by construction.

## 3. Categorical interpretation

`close` / `moderately_different` / `significantly_different` describe deviation from
the author's own observed range. They are project heuristics, not scientifically
validated authorship measurements, and must never be converted into human/AI
probabilities or detector scores. Explanations are factual
("draft 26.3 vs profile typical 12.4–16.1"), never "AI-like".

## 4. Confidence

Overall confidence = weaker of profile evidence (low/medium/high) and draft length
(<100 words low, <400 medium, else high). Low confidence reports keep all findings
but frame them cautiously; empty drafts yield an all-`unavailable` report.

## 5. Missing data

Any metric, dimension, or readability estimate may be `unavailable` (thin profile,
short draft, unsupported feature). Unavailable dimensions are excluded from the
overall aggregation (weights renormalized), and every report lists them as limitations.

## 6. Context

Profiles carry a context label; drafts may carry one (`draft_context`). Matching labels
pass silently; mismatches produce a warning ("differences may reflect context, not
inconsistency"), never an inconsistency verdict. No automatic context detection exists.

## 7. N-gram comparison

Reference set = profile patterns with sample_presence ≥ 0.5. Overlap and
presence-weighted overlap are reported with matched patterns listed; bands ≥0.5 /
≥0.2. Low overlap always carries the topic/context caveat. Short drafts and
header/boilerplate artifacts in samples are known overlap limitations.

## 8. Overall status

Metric scores (0/1/2) → dimension means (cutoffs 0.5/1.25) → weight-averaged overall
(same cutoffs; defaults sentence/paragraph/vocabulary 1.0, punctuation/readability/
cohesion 0.8, ngrams 0.7; configurable, deterministic). Unavailable dimensions are
skipped, not zero-filled. No similarity percentages are emitted — there is no
justified single-number interpretation, so none is offered.

## 9. Limitations

Heuristic bands; length-sensitive diversity metrics; topic-sensitive overlap;
single-domain profiles; English-calibrated readability. Reports must be read as
"where this draft differs from your normal writing", with the evidence basis
(samples, words) stated every time.

## 10. Research boundary

```
Research:      features → classification
Natural Voice: author samples → profile → style comparison
```

Paper features inform *which* characteristics are measured; the paper's classifiers,
PCA setup, and thresholds play no role. This engine would remain useful if AI-text
detection systems did not exist.

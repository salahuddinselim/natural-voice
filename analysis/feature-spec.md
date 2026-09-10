# Voice Consistency Analysis — Feature Specification (v0.1, Phase 3)

Platform-independent comparison method: an **Author Voice Profile** (see
`voice-profile-spec.md`) versus a **new draft**. This is style-consistency analysis,
not authorship prediction. No analyzer code is implemented in this phase.

## 1. Comparison procedure

1. Obtain or sketch the author's profile (or note `confidence: low` if samples are thin).
2. Measure the same dimensions on the draft using the same definitions.
3. Tabulate profile vs. draft side by side.
4. Classify each dimension's deviation (see §2).
5. Report only dimensions that matter: lead with the largest deviations, keep the list short.
6. Rewrite to pull the draft toward the profile **only where clarity is preserved or improved** —
   never force a match that would damage meaning, precision, or flow.

Example table shape:

```text
Metric                  Profile       Draft
------------------------------------------------
Avg sentence length     18.4          27.1
Vocabulary complexity   Medium        High
Formality               Moderate      High
Comma frequency         Medium        High
Paragraph length        4.2           8.7
```

## 2. Interpretation categories

Per-dimension deviation from the author's own profile:

```text
Close                 — within the author's normal range; leave alone.
Moderately different  — noticeable shift; suggest an edit only if it also helps clarity.
Significantly different — strong shift; flag and propose a voice-consistent revision.
```

These describe deviation from the author's habits. They must NEVER be converted into:

```text
Human probability / AI probability / Detector score / human_score
```

Forbidden outputs: any numeric authorship score, any claim about who or what wrote the text.

## 3. Dimension thresholds (initial heuristics, not validated science)

Apply judgment; numbers below are starting points for an LLM reader, not classifier cutoffs.
"Normal range" always means the author's observed range first, these fallbacks second.

- **Avg sentence length:** within ±20% → Close; ±20–40% → Moderately different; beyond → Significantly different.
- **Vocabulary complexity band:** same band → Close; one band apart → Moderately different; two+ bands → Significantly different.
- **Formality / directness:** same level → Close; adjacent level → Moderately different; opposite ends → Significantly different.
- **Punctuation frequency:** same level on the 4-point scale → Close; one step → Moderately different; two+ steps → Significantly different.
- **Paragraph length (sentences/paragraph):** within ±1.5 → Close; ±1.5–3 → Moderately different; beyond → Significantly different.
- **Transition frequency:** same band → Close; adjacent band → Moderately different; sparse-vs-rich jump → Significantly different.

Always state the comparison as: *"This draft differs from your normal writing style in these
areas"* — never as a judgment of quality or origin.

## 4. Missing style information

If no profile exists or confidence is `low`:

- Emit `Voice profile confidence: Low`.
- Do NOT fabricate profile values to fill the table.
- Fall back to conservative rewriting: preserve the draft's own voice, fix only clear
  clarity/flow issues per `core/rewriting.md`.
- Invite (don't require) 2–3 genuine samples to enable profile-aware editing next time.

## 5. Research connection (reuse, not classification)

Research features from `core/research.md` are reused here strictly as descriptive
writing characteristics:

| Research feature   | Voice-profile use         |
| ------------------ | ------------------------- |
| Word count         | Sample statistics         |
| Word density       | Vocabulary/style analysis |
| Punctuation        | Punctuation profile       |
| Readability        | Complexity profile        |
| POS counts         | Linguistic distribution   |
| N-grams            | Phrase-pattern analysis   |
| Character patterns | Future style analysis     |
| NER                | Optional linguistic context |

These features are being reused as descriptive characteristics. They are NOT used to
classify the author as human or AI. The paper's classifiers, PCA setup, and similarity
thresholds are research context only and have no role in this comparison.

## 6. No artificial humanization (hard requirement)

The consistency engine must never:

```text
Add mistakes / Add typos / Add weird punctuation
Randomize sentence lengths / Insert slang / Reduce grammar quality
```

Instead:

```text
Observe genuine author characteristics
        ↓
Preserve relevant characteristics
        ↓
Improve the draft without destroying the voice
```

A "Significantly different" flag never justifies degrading the draft. The fix is always a
clarity-preserving move toward the author's observed habits — or no change, with the flag
left for the author to decide.

## 7. Status (updated Phase 5)

Phase 4 analyzer features consumed by the profile builder (`profile/`, v0.1.0):

- **Consumed per sample:** basic counts, sentence/paragraph structure, vocabulary
  (diversity, word lengths, top words), punctuation rates, readability (nulls skipped),
  pronoun ratio, transition counts, word bigrams/trigrams.
- **Aggregated as:** weighted mean (sqrt-damped) + unweighted median/std/min/max/n +
  `typical_range`; terms/N-grams as count/frequency/sample_presence; stability labels;
  outlier notes. Full mapping in `voice-profile-spec.md` §9.
- **Not consumed (still `null`/absent):** open-class POS, NER, error metrics —
  per-feature `n` in `feature_coverage` records what each measurement rests on.

Method + categories + heuristics defined; measurements implemented as a local analyzer
(`analyzer/`, v0.1.0, stdlib-only) emitting structured JSON. No scoring model, no
persistence, no rewriting.

Implementation coverage:

- **Implemented:** word/character/sentence/paragraph counts and averages; sentence-length
  distribution + buckets + variation (std, CoV); paragraph structure; vocabulary diversity
  (TTR + Guiraud's R), word-length stats, top/repeated words; punctuation inventory +
  density; readability (FRE, FK grade, Gunning Fog, Coleman-Liau, ARI); pronoun +
  transition-connective distributions; word bigrams/trigrams; optional character n-grams.
- **Optional (implemented, off by default):** character n-grams
  (`include_character_ngrams=True`).
- **Planned, explicitly `null` (never estimated):** open-class POS
  (nouns/verbs/adjectives/adverbs), NER, grammar-error measurement. Dale-Chall, Spache,
  and Linsear Write readability variants omitted (need external word lists).

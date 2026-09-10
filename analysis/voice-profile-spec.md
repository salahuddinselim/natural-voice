# Author Voice Profile — Specification (v0.1, Phase 3)

Platform-independent data model. No adapter-specific instructions belong here.
No analyzer code, no storage, and no persistent-profile system are implemented in this phase.

## 1. Purpose

An Author Voice Profile describes **how** a particular author genuinely writes, as observed
in their own voluntarily provided samples. It answers:

> "What characteristics make this author's writing sound like this author?"

It never answers "what makes text look human", never carries an authorship score, and never
determines whether a text is human- or AI-written.

## 2. Schema (v0.1)

All fields are optional. Omit anything the samples do not support rather than guessing.
Numeric fields are descriptive measurements; categorical fields use the fixed vocabularies
given below so profiles stay comparable.

```yaml
voice_profile:
  version: "0.1"
  confidence: low | moderate | strong   # sample-size basis, see §4
  scope: global | academic | technical | casual   # see §5
  sample_stats:
    sample_count:
    total_words:
    domains: []              # e.g. [academic, email]; free-form labels

  vocabulary:
    complexity: simple | simple-to-medium | medium | medium-to-rich | rich
    diversity_note:          # free text, e.g. "repeats key terms deliberately"
    average_word_length:
    common_words: []         # author's own frequent content words
    technical_terms: []      # domain terms the author uses; must be preserved
    repeated_phrases: []     # characteristic multi-word habits, not verdicts

  sentence_structure:
    average_length:
    median_length:
    min_length:
    max_length:
    variation: low | medium | high
    short_ratio:             # share of sentences < ~12 words
    medium_ratio:            # share ~12–25 words
    long_ratio:              # share > ~25 words
    notes:

  paragraph_structure:
    average_sentences_per_paragraph:
    variation: low | medium | high
    notes:                   # e.g. "short-to-medium paragraphs; occasional single-sentence emphasis"

  punctuation:
    comma: rare | occasional | medium | frequent
    semicolon: rare | occasional | medium | frequent
    colon: rare | occasional | medium | frequent
    parentheses: rare | occasional | medium | frequent
    dash: rare | occasional | medium | frequent
    question: rare | occasional | medium | frequent
    exclamation: rare | occasional | medium | frequent
    notes:

  transitions:
    frequency: sparse | moderate | rich
    common_connectives: []   # author's own repertoire, e.g. [however, for example, so]

  tone:
    formality: low | moderate | high
    directness: indirect | balanced | direct

  readability:
    notes:                   # free text; optional numeric scores, see §3
    flesch_reading_ease:     # optional
    flesch_kincaid_grade:    # optional
    coleman_liau:            # optional
    # Any subset is acceptable; no metric is mandatory.

  ngrams:
    common_bigrams: []       # author's recurring word pairs
    common_trigrams: []      # author's recurring word triples
    notes:                   # stylistic habits only; never authorship evidence

  overall_style:             # 1–2 sentence human summary, e.g. "Explanatory and direct."
```

Design notes (deliberate deviations from a naive dump of every count):

- **Categorical bands over raw precision** for tone, punctuation, and transitions: the profile
  is read by an LLM applying judgment, not by a classifier needing floats.
- **Free-text `notes` alongside numbers**: captures what counts miss (e.g. deliberate repetition).
- **`scope` + `sample_stats` on every profile**: forces honesty about basis and domain.
- **No content fields**: beliefs, topics, and stances are excluded by construction (see §6).

## 3. Dimension guidance

**Vocabulary (§6 of spec: diversity, avg word length, common/technical/repeated terms).**
Record natural repetition as style; do not prescribe "increase diversity". Technical terms are
a preservation list for rewriting, not simplification targets.

**Sentence structure.** Report average, median, min, max, variation band, and short/medium/long
shares. Document explicitly: sentence length alone does not define style; it is one signal
among many.

**Paragraph structure.** Average sentences per paragraph plus variation and notes on very
short/long paragraphs. Uniform length is not inherently bad — describe the author, don't grade.

**Punctuation.** Tendencies per mark on the fixed 4-point scale. Identify habits; never impose
a "natural punctuation" template.

**Transitions.** Frequency band plus the author's own connective list. Open vocabulary: record
what the samples contain (however, therefore, because, although, also, then, for example,
in addition, …) rather than checking against a fixed universal list.

**Tone.** Formality (`low | moderate | high`) and directness (`indirect | balanced | direct`)
are writing-style descriptors, not psychological measurements. Say so when presenting them.

**Readability.** Descriptive measurements only, never quality judgments. Any subset of
Flesch-Kincaid, Flesch Reading Ease, Gunning Fog, Coleman-Liau, Dale-Chall, ARI, Linsear
Write, Spache is acceptable; none is mandatory. Profiles should be language/domain aware —
scores calibrated on English general prose do not transfer automatically.

**N-grams / phrase patterns.** Common bigrams/trigrams and recurring connective sequences as
stylistic characteristics. Repeated phrases are never "AI-like" or "human-like" evidence.

## 4. Sample-size guidance (engineering heuristics, not validated science)

No reliable research basis exists for a universal minimum; treat these as project heuristics:

| Basis | Heuristic | Profile confidence |
|---|---|---|
| 1 short sample (< ~300 words) | insufficient | `low` — describe tentatively, rewrite conservatively |
| 2–3 samples or ~500–1500 words | basic tendencies visible | `moderate` |
| 4+ samples across contexts, 1500+ words | stable habits visible | `strong` |

Rules:

- Below `moderate`, every inferred field is provisional; mark the profile `confidence: low`.
- With `low` confidence, prefer preserving the current draft over imposing inferred traits.
- Never fabricate a profile from insufficient samples — emit `Voice profile confidence: Low`
  and use conservative rewriting instead.

## 5. Cross-domain design (concept for later; single profile for now)

The same author writes differently across academic papers, emails, documentation, and chat.
Target model:

```text
Author
 ├── Global profile      # cross-context habits (directness, typical complexity)
 ├── Academic profile    # scope: academic
 ├── Technical profile   # scope: technical
 └── Casual profile      # scope: casual
```

Phase 3 implements only the schema's `scope` field and this concept. Do not build multiple
persistent profiles, selection logic, or storage yet. When scope-specific samples exist, create
a separate profile document with `scope` set; the `global` profile summarizes cross-context traits.

## 6. Style vs. content (hard boundary)

The profile describes HOW the author writes, never WHAT they believe. Do not infer or record:

- political beliefs, religion, ideology
- personality or psychological characteristics
- sensitive personal attributes (health, identity, protected characteristics)

If a sample's topic leaks into a field (e.g. topical words in `common_words`), prefer
function/structure words and domain terminology over topical nouns.

## 7. Privacy (binding)

- Samples are provided voluntarily in-conversation; never pulled from elsewhere.
- Never upload samples, send them to external services, or log them beyond the session.
- No API keys, no cloud storage, no database, no tracking.
- Never commit user samples to this repository. Repository `examples/` contain only
  synthetic or public-domain demonstrations, clearly labeled.
- Profiles are held by the user (conversation-local or a user-owned file), never in this repo.

## 8. Status (updated Phase 5)

Schema defined (Phase 3), analyzer implemented (Phase 4), builder implemented
(Phase 5: `profile/`, v0.1.0). No multi-profile logic, no comparison, no rewriting yet.

## 9. Implementation mapping (Phase 5 builder)

The builder implements this schema with two deliberate deviations (Phase 5 governs):

| Spec field (§2) | Builder output | Notes |
|---|---|---|
| `voice_profile.version` | `profile_version: "0.1.0"` | Phase 5 envelope |
| `confidence: low\|moderate\|strong` | `confidence.overall: low\|medium\|high` | **Deviation:** Phase 5 mandates low/medium/high; thresholds in `confidence.py` |
| `scope` | `metadata.context` | Values general/academic/technical/casual; no auto-classifier |
| `sample_stats` | `metadata.{sample_count,total_words,skipped_samples}` + analyzer version | Domains free-form; builder does not label domains |
| vocabulary.\* | `vocabulary.{diversity, guiraud_r, average_word_length, median_word_length, common_terms}` | `common_terms` carry count/frequency/sample_presence; no must-use word lists |
| sentence_structure.\* | `sentence_structure.{average_length, median_length, short/medium/long_ratio}` + `length_stability` | Aggregates `{mean,median,std,min,max,n,typical_range}`; same buckets |
| paragraph_structure.\* | `paragraph_structure.{average_words/sentences_per_paragraph, median_words}` + `size_stability` | As specified |
| punctuation.\* | `punctuation.{mark.per_100_words, density}` | Numeric rates instead of 4-point bands (bands remain an LLM-reading aid) |
| transitions.\* | `linguistic.{transitions_per_100_words, common_connectives}` | Author's own repertoire + presence rates |
| tone.\* | not measured | Formality/directness stay qualitative LLM judgments; no fake quantification |
| readability.\* | `readability.{flesch_reading_ease, flesch_kincaid_grade, gunning_fog, coleman_liau, automated_readability_index}` | Nulls skipped; any subset acceptable per §3 |
| ngrams.\* | `ngrams.{common_bigrams, common_trigrams}` + `patterns.repeated_phrases` | Presence + mean rate; never authorship evidence |
| `overall_style` | `patterns.{recurring_connectives, structural_notes}` | Template-generated from data, deterministic |

## 10. Consumption by the comparison engine (Phase 6)

`comparison/` reads a saved profile plus a draft analyzed with the same analyzer
version. Consumed: every numeric aggregate via its `typical_range` (closeness
check), stability labels (spread-band match), `common_terms`/`common_connectives`
and `common_bigrams/trigrams` with `sample_presence ≥ 0.5` (overlap reference
sets), `confidence.overall` and `metadata` (evidence framing + cautious wording),
`metadata.context` (mismatch warnings). Nothing is written back into the profile;
comparison is read-only. Contract: `analysis/comparison-spec.md`.

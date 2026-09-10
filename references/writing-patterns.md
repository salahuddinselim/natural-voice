# Writing Patterns — Practical Analysis Concepts

Translates research-adjacent signals into editing guidance. These are **analysis
concepts for improving quality and consistency, NOT evidence of authorship**.
No pattern below proves a text is human- or AI-written.

## 1. Sentence structure

- **Sentence length:** track mean and spread; compare against the author's own range.
  Flag uniform runs (e.g. ten 18–22-word sentences in a row) as monotonous, not as synthetic.
- **Sentence variation:** healthy prose mixes short/medium/long within the author's habits.
  Vary only inside the observed range unless asked for a major rewrite.
- **Structural variety:** note overuse of one open (e.g. always "It is…", always "There are…")
  or one clause shape; suggest alternatives the author already uses elsewhere.

## 2. Vocabulary

- **Vocabulary diversity:** type–token ratio over a sliding window; low diversity → repetition,
  not a verdict.
- **Repeated words/phrases:** list top repeated content words and filler phrases
  ("important to note", "in today's world", "delve", "tapestry" used emptily).
- **Word length:** average word length and distribution; sudden shifts may signal a pasted
  passage worth smoothing — or just a technical section. Ask, don't accuse.
- **Technical terminology:** inventory domain terms; they must survive rewriting unchanged.
  Never simplify a precise term into a vaguer one.

## 3. Punctuation

- **Frequency:** density of commas, periods, colons, semicolons, dashes, parentheses, quotes.
- **Variety:** range of marks the author actually uses.
- **Consistency:** one convention per document (Oxford comma, dash style, quote style).
  Fix inconsistency; don't impose an alien style.

## 4. Paragraph structure

- **Paragraph length:** sentence count and word count per paragraph; avoid machine-uniform blocks.
- **Sentence distribution:** where short punchy paragraphs vs. long developments fall.
- **Topic continuity:** one focus per paragraph; flag drift, missing topic sentences,
  or stacked ideas that should split.

## 5. Readability

- **Text complexity:** overall difficulty relative to audience (general vs. specialist).
- **Sentence complexity:** clause depth and nesting; split only when comprehension suffers.
- **Word complexity:** long/rare words where a plain equivalent exists *without precision loss*.
  Research readability scores (Flesch, Coleman-Liau, etc.) may inform future analysis;
  they are heuristics, not quality verdicts.

## 6. Linguistic distribution (POS-adjacent)

Rough distribution of nouns, verbs, adjectives, adverbs, pronouns:

- noun-heavy + adjective-stacked → possibly over-nominalized; prefer concrete verbs.
- adverb-stacked intensifiers ("very", "extremely", "deeply") → trim unless meaningful.
- pronoun drift (I/we/one switching) → unify per author intent and genre.

These describe style; they do not identify authorship.

## 7. N-grams (local patterns)

- **Common sequences:** recurring word bigrams/trigrams (e.g. "in order to", "due to the fact that").
  Replace wordy ones with tighter equivalents the author accepts.
- **Repeated local patterns:** identical openers/closers across paragraphs; vary using the
  author's own connective repertoire (see voice-model preferred connectives).

## 8. Transitions

Count and classify: additive, contrastive, causal, sequential, exemplifying.
Keep only transitions expressing a real logical relation; delete decorative ones.
Match the author's observed density — sparse stays sparse, rich stays rich.

## 9. Using this file

When editing: cite the pattern ("repeated opener ×4", "paragraph packs 3 topics"),
propose the smallest fix consistent with the author's voice, and move on.
Never present any of these as a human/AI judgment.

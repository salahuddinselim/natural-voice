# Natural Voice — Research Summary (Platform-Independent)

Primary source: **Nguyen, Hatua, Sung — "How to Detect AI-Generated Texts?"**

This file is a conciseOrientation summary. Detail lives in
`references/research-foundation.md`. Practical translation lives in
`references/writing-patterns.md`.

## Research findings (from the paper — not our claims)

The paper compares human-written text (HWT) with synthetically generated text (SGT,
ChatGPT-era) on two constructed datasets: a Wikipedia-based set (3974 HWT + 4557 SGT)
and a US Election 2024 news set (829 HWT + 664 SGT). Preprocessing used standard NLP
steps (NLTK, AutoCorrect, BeautifulSoup).

Feature groups studied (~50,783 features per text in the full construction):

- basic NLP: word count, word density (`#chars/#words`), punctuation, title/uppercase
  word counts, POS-related counts (noun, verb, adjective, adverb, pronoun)
- readability scores (8: Flesch-Kincaid, Flesch, Gunning Fog, Coleman-Liau, Dale-Chall,
  ARI, Linsear Write, Spache), grammar/text-error characteristics, NER counts
- TF-IDF and N-grams: count vectors, word bigrams/trigrams, character bi/trigrams
- topic modeling: Neural LDA (20 topics)
- reduction: PCA (1024 components in the similarity experiment)
- classifiers: Random Forest, SVM, XGBoost, evaluated with Precision, Recall, F1, Accuracy
- analysis tools: cosine similarity, feature importance (sklearn), SHAP explanations

Reported experimental findings (dataset-specific, not universal):

- On the paper's Wikipedia setup, RF and XGBoost reached F1 ≈ 0.9993; SVM was much
  lower (≈ 0.765). This describes that experiment, not general detection performance.
- Cosine-similarity analysis on the news set separated HWT/SGT pairs best with PCA
  features (99.97% of pairs in [-0.6, -0.2); authors noted -0.2 as a threshold *for that set*).
- Top distinguishing signals in that experiment included Coleman-Liau score, word density,
  text error length, title word count, punctuation count, and word count.

The paper itself situates the work among domain-specific efforts and notes that general,
cross-domain AI-text detection is imperfect.

## Natural Voice engineering decisions (ours — not the paper's)

- We reuse the paper's feature *vocabulary* (counts, density, variation, readability,
  N-grams, POS distribution, NER, error characteristics) as **writing-analysis signals**
  for quality and style consistency — never as an authorship verdict or detector.
- Author Voice Profiling, voice-consistent rewriting, conservative editing, the
  core→adapter architecture, mode system, and any future JSON analyzer are project
  design decisions. Do not attribute them to the paper.
- We report the paper's strong numbers only with their experimental context and an
  explicit non-generalization warning.

## Rule for all contributors and adapters

```text
Paper findings
      ≠
Natural Voice engineering decisions
```

When citing research-derived claims, name the paper and the experimental context.
When stating framework behavior, label it as a Natural Voice decision.

# Research Foundation — "How to Detect AI-Generated Texts?" (Nguyen, Hatua, Sung)

Detailed companion to `core/research.md`. Paper-faithful; engineering extensions are
labeled as such. Do not copy the full paper here.

## 1. Research problem

Can synthetically generated text (SGT, ChatGPT-era LLMs) be distinguished from
human-written text (HWT) using handcrafted features + classic ML, and can similarity-based
reverse-engineering classify without ground-truth collection? Motivation: academic
integrity, fake news/reviews, spam/phishing — areas where traditional plagiarism tools fail.

## 2. Datasets

- **Wikipedia-based (classification experiments):** 3974 HWT + 4557 SGT = 8530 texts.
  HWT = section text extracted from Wikipedia articles; SGT = ChatGPT prompted per section
  (e.g. "Describe Dog Taxonomy").
- **US Election 2024 news (similarity experiments):** 829 HWT + 664 SGT = 1493 texts.
  HWT = article text from 500+ collected URLs; SGT = up to 5–10 QA-style generations per
  article from extracted keywords.
- Both sets were balanced approximately between classes for their respective experiments.

## 3. Preprocessing

Standard NLP preprocessing with NLTK, AutoCorrect, and BeautifulSoup (tokenization,
cleaning, correction support). Feature extraction applied identically to both classes.

## 4. Feature groups (≈ 50,783 per text)

| Group | Contents | Size |
|---|---|---|
| Basic NLP | char count, word count, word density (`#chars/#words`), punctuation count, title word count, upper-case count, noun/verb/adj/adv/pronoun counts | 11 |
| Term frequencies & N-grams | Count vectors (35742), word bigrams TF-IDF (5000), word trigrams TF-IDF (5000), char bi/trigrams TF-IDF (5000) | 50742 |
| Topic modeling | Neural LDA, 20 topics | 20 |
| Other | 8 readability scores (Flesch-Kincaid, Flesch, Gunning Fog, Coleman-Liau, Dale-Chall, ARI, Linsear Write, Spache) + NER count + text error length | 10 |

## 5. Feature representation

Sparse count/TF-IDF vectors for N-grams; dense handcrafted scalars for NLP/readability/NER/
error/topic features. Similarity experiments compared three views: without TF/NG features
(15,041), all features (50,783), and PCA-reduced features.

## 6. PCA

Principal Component Analysis used for feature selection/reduction; similarity experiment
used `n_components=1024` retaining maximum information while removing sparsity/noise.

## 7. Classification models

Random Forest, SVM, XGBoost, tuned with grid search on the Wikipedia set:

- RF: `n_estimators=500, criterion=gini, min_samples_split=10, min_samples_leaf=10, max_features=sqrt`
- SVM: `C=4, kernel=rbf, degree=7, gamma=scale`
- XGBoost: `n_estimators=1000, learning_rate=0.01`

## 8. Evaluation metrics

Accuracy, Precision, Recall, F1 (scikit-learn).

## 9. Cosine similarity

Used on the news set to compare HWT vs. corresponding SGT in feature space (score in
[-1, 1]; 1 = identical). Binned into [-1,-0.6), [-0.6,-0.2), [-0.2,0.6), [0.6,1].

## 10. Feature importance & SHAP

- sklearn feature importance over the training set for RF/XGB.
- SHAP waterfall plots for individual predictions (top-10 features, log-odds units).

## 11. Experimental findings (with context — do not generalize)

- Wikipedia classification: RF F1 ≈ 0.9993, XGBoost F1 ≈ 0.9993, SVM F1 ≈ 0.765.
  → Result of that dataset/setup; not proof of universal detection.
- Similarity: PCA-feature view placed 99.97% of HWT/SGT pairs in [-0.6,-0.2); raw and
  no-TFNG views separated poorly. Authors noted -0.2 as a threshold *for that set*.
- Importance: top signals included Coleman-Liau score, word density, text error length,
  title word count, punctuation count, word count (4/5 overlap between RF and XGB top-5);
  SHAP single-sample plots largely agreed with global importance.

## 12. Limitations (paper + our reading)

- Results are tied to Wikipedia-style expository text and ChatGPT-era outputs; cross-domain,
  cross-model, and cross-time generalization is unproven (the paper surveys domain-specific
  detection for exactly this reason).
- Near-perfect scores on one constructed set suggest dataset artifacts as well as real
  stylistic differences; treat as an existence proof for *that* setup, not a universal law.
- Handcrafted features + classic ML trade interpretability for brittleness against
  paraphrase, editing, and newer generators.

## 13. What Natural Voice takes from this (engineering, not paper claims)

Only the feature *vocabulary* as future analysis signals (counts, density, variation,
readability, POS distribution, NER, error characteristics, N-grams, topics) for writing
quality and voice-consistency work. No detector, no authorship verdict, no bypass claims.

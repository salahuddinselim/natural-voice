# Natural Voice Analyzer (v0.1.0)

Local, dependency-free linguistic analyzer. It extracts **descriptive characteristics**
from text and returns them as structured JSON for the Natural Voice skill and future
voice-profile tooling.

This analyzer is **not** an AI detector. It produces no authorship scores, probabilities,
verdicts, or detector-related outputs of any kind.

## Installation

None required — standard library only (Python 3.10+). Clone the repository and run:

```bash
cd natural-voice
python -m unittest discover -s tests   # verify your checkout (from repo root)
```

`requirements.txt` is intentionally dependency-free and documents this.

## Python API

```python
from natural_voice_analyzer import analyze_text

result = analyze_text(text)                                  # defaults: top_k=20
result = analyze_text(text, top_k=10)                        # fewer frequency items
result = analyze_text(text, include_character_ngrams=True)   # opt-in char trigrams
```

`result` is JSON-serializable. Floats are rounded to 4 decimals; uncomputable values
(e.g. readability of empty text) are `null`, never invented.

## CLI

```bash
python -m natural_voice_analyzer input.txt
python -m natural_voice_analyzer input.txt --pretty
python -m natural_voice_analyzer input.txt --pretty --top-k 10
python -m natural_voice_analyzer input.txt --include-character-ngrams
```

Reads one UTF-8 file, prints JSON to stdout. Exit 2 on unreadable/missing file,
exit 1 on analysis failure. The input text itself is never logged.

## Output format

```json
{
  "metadata": {"analyzer_version": "0.1.0", "language": "en"},
  "basic": {"characters": 0, "characters_no_spaces": 0, "words": 0,
            "sentences": 0, "paragraphs": 0, "average_word_length": 0,
            "average_sentence_length": 0, "average_paragraph_length": 0,
            "median_sentence_length": 0, "min_sentence_length": 0,
            "max_sentence_length": 0},
  "sentence_structure": {"count": 0, "average_length": 0, "median_length": 0,
    "minimum_length": 0, "maximum_length": 0, "standard_deviation": 0,
    "coefficient_of_variation": 0, "short_ratio": 0, "medium_ratio": 0,
    "long_ratio": 0, "bucket_thresholds": {"short_max": 11, "medium_max": 25}},
  "paragraph_structure": {},
  "vocabulary": {"type_token_ratio": 0, "guiraud_r": 0, "top_words": [],
                 "repeated_words": []},
  "punctuation": {"counts": {}, "per_100_words": {}, "total": 0,
                  "punctuation_density": 0},
  "readability": {"flesch_reading_ease": 0, "flesch_kincaid_grade": 0,
                  "gunning_fog": 0, "coleman_liau": 0,
                  "automated_readability_index": 0},
  "linguistic": {"pronoun_count": 0, "transition_count": 0},
  "ngrams": {"top_k": 20, "bigrams": [], "trigrams": []}
}
```

Measurement rules (see module docstrings for full detail):

- **Words:** Unicode regex tokens; internal apostrophes kept (`don't` = 1 token); numbers kept.
- **Sentences:** split on `.`/`!`/`?`/`…` with an abbreviation guard list (English heuristic).
- **Paragraphs:** blank-line-separated blocks.
- **Buckets:** short <12, medium 12–25, long >25 words (engineering heuristics, descriptive only).
- **TTR** = unique/total (length-dependent — compare only similar-length texts; Guiraud's R
  is the stabler companion). **`punctuation_density`** = inventoried marks / words.
- **Readability:** standard FRE/FK/Fog/Coleman-Liau/ARI formulas with heuristic syllable
  counts; English-calibrated. Dale-Chall/Spache/Linsear omitted (need word lists).

## Supported features

Basic counts, sentence/paragraph structure + variation, vocabulary diversity (TTR + Guiraud's R),
word-length stats, punctuation inventory, 5 readability estimates, pronoun + transition-connective
distributions, word bigrams/trigrams, optional character n-grams.

## Optional / planned (not estimated, never faked)

Open-class POS (nouns/verbs/adjectives/adverbs) needs a tagger — fields exist as `null`.
NER, grammar-error measurement likewise planned. Character n-grams are implemented but
opt-in (`include_character_ngrams=False` by default).

## Research traceability

Research-informed (paper vocabulary, our implementation): counts, word density behavior,
punctuation, readability, N-gram inventories, pronoun/transition distributions.
Engineering decisions (ours): tokenizer, abbreviation list, buckets, normalization,
Guiraud's R, schema. The paper's classifiers/PCA/thresholds play no role here.

## Limitations

- Heuristic sentence splitting and syllable counting (English prose; degrades gracefully elsewhere).
- TTR is length-sensitive; readability is English-calibrated.
- No POS/NER/error analysis yet — those fields are explicitly `null`, not estimates.
- Descriptive statistics only: never interpret outputs as quality or authorship judgments.

## Privacy

Fully local: no uploads, no APIs, no model downloads, no sample storage, no text logging.

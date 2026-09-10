# Example Voice Profile — SYNTHETIC DEMONSTRATION ONLY

Derived from `voice-samples.md` (fictional author). Shows the schema from
`analysis/voice-profile-spec.md` and a consistency table from `analysis/feature-spec.md`.
Illustrative values, not measured claims about any real person.

## Sample writing → characteristics → profile

```text
Sample writing (voice-samples.md)
      ↓
Extracted characteristics (short sentences mixed with medium ones,
direct tone, short paragraphs, moderate transitions, exact terms)
      ↓
Example voice profile (below)
```

## Example profile

```yaml
voice_profile:
  version: "0.1"
  confidence: moderate
  scope: global
  sample_stats:
    sample_count: 3
    total_words: 172
    domains: [explanatory, technical, casual]

  vocabulary:
    complexity: simple-to-medium
    diversity_note: "repeats key terms deliberately; little decoration"
    average_word_length: 4.6
    common_words: [short, split, check, leave]
    technical_terms: [JSON, standard library, readability scores]
    repeated_phrases: ["I would", "for example"]

  sentence_structure:
    average_length: 14.8
    median_length: 14.0
    min_length: 5
    max_length: 24
    variation: medium
    short_ratio: 0.25
    medium_ratio: 0.60
    long_ratio: 0.15
    notes: "mostly medium-length with occasional short sentences"

  paragraph_structure:
    average_sentences_per_paragraph: 3.0
    variation: low
    notes: "short-to-medium paragraphs, one focus each"

  punctuation:
    comma: medium
    semicolon: rare
    colon: rare
    parentheses: rare
    dash: rare
    question: rare
    exclamation: rare
    notes: "plain punctuation; colons only before lists"

  transitions:
    frequency: moderate
    common_connectives: [however, for example, so, then]

  tone:
    formality: moderate
    directness: direct

  readability:
    notes: "plain explanatory prose; technical terms raise surface complexity"
    flesch_reading_ease: 62.0
    coleman_liau: 10.2

  ngrams:
    common_bigrams: ["for example", "I would"]
    common_trigrams: []
    notes: "few fixed phrases; connective-led openings recur"

  overall_style: "Explanatory and direct."
```

## Example consistency check (profile vs. a new draft)

A draft written in longer, more formal sentences than the samples:

```text
Metric                  Profile       Draft           Reading
--------------------------------------------------------------------
Avg sentence length     14.8          26.3            Significantly different
Vocabulary complexity   Simple-Med    Medium          Moderately different
Formality               Moderate      High            Moderately different
Comma frequency         Medium        Medium          Close
Paragraph length        3.0           3.4             Close
```

Suggested output (per `analysis/feature-spec.md`): *"This draft differs from your normal
writing style in these areas: sentences run ~75% longer than your usual range; wording is
a step more formal. Consider splitting the two longest sentences and swapping the three
flagged formal phrases for your usual plainer equivalents — meaning and terms unchanged."*

No authorship claim is made or implied.

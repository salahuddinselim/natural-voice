# Natural Voice Profile Builder (v0.1.0)

Builds an Author Voice Profile from multiple genuine writing samples using the
Phase 4 analyzer (`analyzer/`). Local-only, dependency-free (standard library +
sibling analyzer package). Derived statistics only — samples are never stored,
logged, uploaded, or transmitted.

The profile describes HOW the author tends to write. It never determines whether
a text is human- or AI-written and contains no such scores.

## Python API

```python
from natural_voice_profile import build_profile, build_profile_from_files

profile = build_profile(["sample one...", "sample two...", "sample three..."])
profile = build_profile(["..."], context="academic")
profile = build_profile_from_files(["s1.txt", "s2.txt"])
```

`build_profile` raises `ValueError` for empty input, all-empty samples, bad context,
or unreadable files (file variant), and `TypeError` for non-string samples.

## CLI

Run from this directory (`profile/`):

```bash
python -m natural_voice_profile build ../examples/voice_samples/*.txt --pretty
python -m natural_voice_profile build ../examples/voice_samples/*.txt --output profile.json
python -m natural_voice_profile build ../examples/voice_samples/*.txt --context academic --output profile.json
```

Glob patterns are expanded by the CLI itself (works where the shell does not glob).
Exit 1 with a stderr message on failure. Sample text never appears in output or logs.

## Profile schema (v0.1.0)

```json
{
  "profile_version": "0.1.0",
  "metadata": {"sample_count": 4, "total_words": 640, "language": "en",
               "context": "general", "analyzer_version": "0.1.0",
               "skipped_samples": 0},
  "confidence": {"overall": "medium", "sample_count": 4, "total_words": 640,
                 "skipped_samples": 0, "feature_coverage": {},
                 "note": "engineering heuristic ..."},
  "vocabulary": {}, "sentence_structure": {}, "paragraph_structure": {},
  "punctuation": {}, "readability": {}, "linguistic": {},
  "ngrams": {"common_bigrams": [], "common_trigrams": []},
  "patterns": {"repeated_phrases": [], "recurring_connectives": [],
               "structural_notes": []},
  "outlier_notes": []
}
```

Numeric features aggregate as `{mean, median, std, min, max, n, typical_range}`
(mean word-count-weighted with sqrt damping; spread unweighted to preserve
variation). N-grams/terms carry `{ngram, count, frequency, sample_presence}`.

Key methods (all engineering heuristics, documented in code):

- **Weighting:** weight = sqrt(sample words); a 100x longer sample gets 10x weight.
- **Confidence:** low below 500 words or <2 samples; high at 1500+ words over 4+
  samples; medium otherwise. Per-feature `n` recorded in `feature_coverage`.
- **Stability:** CoV bands (stable <0.15, moderate <0.35, variable above) on sentence
  length, diversity, paragraph size.
- **Outliers:** |z| > 2 flagged at n ≥ 4; preserved, never dropped; positions only.
- **Deviation from Phase 3 spec:** confidence uses low/medium/high (Phase 5 governs);
  envelope uses `profile_version`/`metadata` (mapping in
  `analysis/voice-profile-spec.md` §9).

## Persistence

```python
from natural_voice_profile import save_profile, load_profile, validate_profile
save_profile(profile, "profile.json")   # refuses invalid profiles
profile = load_profile("profile.json")  # validates on load
```

Deterministic JSON (sorted keys, UTF-8). Validation rejects missing keys, wrong
version, bad enums, non-finite numbers, and any raw-sample storage keys.

## Limitations

- Profiles describe the given samples, not the person; not an identifier or proof.
- Small/thin evidence → low confidence by design; single-domain samples → narrow profile.
- Analyzer limits inherit (English calibration, heuristic segmentation).
- No draft comparison or rewriting here — that is Phase 6+.

## Privacy

Fully local: no uploads, no APIs, no LLM calls, no database, no sample storage.

# Natural Voice — Author Voice Model (v0.3, builder implemented Phase 5)

Platform-independent definition. Profile construction is implemented
(`profile/`, v0.1.0); no sample storage, no database, no rewriting exist.

## Concept: Author Voice Profile

An Author Voice Profile is a compact, human-readable summary of how a particular
author genuinely writes, derived from their own authentic samples. It exists to answer:

> "What does THIS AUTHOR naturally sound like?"

— instead of forcing every user into one generic "good writing" style.

## Future profile dimensions

A future profile may contain:

```text
Vocabulary
Sentence length
Sentence-length variation
Word-length patterns
Paragraph structure
Punctuation habits
Transition frequency
Formality
Directness
Technical vocabulary
Repeated expressions
Preferred connectives
Readability characteristics
```

Example shape (illustrative, not a real person):

```text
Vocabulary: simple-to-medium
Sentence structure: mostly medium-length with occasional short sentences
Tone: direct and moderately formal
Paragraph structure: short-to-medium paragraphs
Technical terminology: frequently preserved
Transitions: moderate
Overall style: explanatory and direct
```

## Implemented flow (Phase 5)

```text
Samples
 ↓
Feature extraction (analyzer/, one pass per sample, never stored)
 ↓
Aggregation (sqrt-damped weighting; spread preserved as std/min/max)
 ↓
Stability (CoV bands) + outlier notes (flagged, never dropped)
 ↓
Confidence (evidence-quantity heuristic: low/medium/high)
 ↓
Author Voice Profile (JSON: profile/natural_voice_profile/builder.py)
```

- **Samples** are provided voluntarily by the user and consist of their own genuine writing.
- **Feature extraction** reuses the Phase 4 analyzer unchanged (no duplicated logic).
- **The profile** is held by the user (conversation-local or a user-owned file such as
  `profile.json`), never committed to this repository, never transmitted anywhere.
- **Draft comparison** is implemented (Phase 6: `comparison/`, v0.1.0):
  draft → analyzer → feature comparison against `typical_range` bands →
  voice consistency report (close/moderately/significantly different).
  Voice-consistent rewriting remains future work.

## Boundaries (binding on all adapters and future phases)

- Model only the current user's own writing, provided with consent.
- Do not imitate a specific real person's identity or style without authorization.
- Do not store user writing samples in the repository, in profiles, in logs, or anywhere else.
- Do not build a database, server, or tracking mechanism for profiles in the core framework.
- Without a profile (or at low confidence): infer voice from the current input text only
  and prefer minimal changes.

## Status (updated Phase 7)

Full chain implemented: model + schema + builder (`profile/` v0.1.0) +
comparison (`comparison/` v0.1.0) + revision (`revision/` v0.1.0 over `llm/`).
Details: `analysis/voice-profile-spec.md` (§9 mapping),
`analysis/comparison-spec.md`, `analysis/revision-spec.md`. Profiles, reports,
and revisions must still be read descriptively, never as authorship signals.

```text
Profile
   ↓
Draft
   ↓
Comparison
   ↓
Revision (LLM, provider-neutral)
   ↓
Validation
```

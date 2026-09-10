# AI-Phrasing Patterns — Concrete Catalog

Companion to `writing-patterns.md` (which covers statistical/structural signals:
sentence length, POS distribution, N-grams). This file catalogs concrete,
named phrasing defects: specific words, constructions, and formatting habits
that make prose read as generic or clichéd, regardless of who or what wrote it.

**Source:** adapted from [Wikipedia:Signs of AI writing](https://en.wikipedia.org/wiki/Wikipedia:Signs_of_AI_writing)
(WikiProject AI Cleanup) and this project's own `humanizer` skill packaging of
it. Per the same rule as `core/research.md` (`Paper findings ≠ Natural Voice
engineering decisions`): the *pattern catalog* is external and cited; how
Natural Voice applies it is a project decision, bound by `core/principles.md`.

## How this fits the pipeline

This is reference material for `core/rewriting.md` step 4, **Identify
unnecessary/generic wording**. Use it to name a specific defect ("that's a
vague attribution" / "that's an em dash doing three jobs") instead of a vague
"sounds AI-generated" impression — concrete findings are checkable; vibes
aren't. As with every other analysis file in this project, matching a pattern
below is **evidence about phrasing quality, never evidence about authorship**.
Do not cite this file to argue a text is or isn't AI-written.

## Boundary tighter than the source material

`core/principles.md` §7 forbids fabricating opinions, anecdotes, or qualifications
attributed to the author. The upstream `humanizer` skill's "add personality
when none exists" behavior (default opinions/reactions when no voice sample is
given) is **out of scope here** — it would fabricate a stance the author never
took. Natural Voice only varies rhythm, directness, or register *within what
the input or the Author Voice Profile already supports* (`core/voice-model.md`).
Never inject an opinion, reaction, or aside the author didn't express.

## Content-level patterns

| # | Pattern | Words/constructions to watch | Fix |
|---|---|---|---|
| 1 | Undue emphasis on significance | "stands as a testament to", "marking a pivotal moment", "underscores its importance", "evolving landscape" | State the plain fact; cut the inflation |
| 2 | Undue emphasis on notability | "independent coverage", "active social media presence" listed without specifics | Cite one concrete instance or cut |
| 3 | Superficial `-ing` analysis | "...symbolizing...", "...reflecting...", "...fostering..." tacked onto a sentence for fake depth | Cut the clause or replace with the actual claim, sourced |
| 4 | Promotional/advertisement language | "nestled", "breathtaking", "vibrant", "boasts a", "must-visit" | Neutral factual description |
| 5 | Vague attribution / weasel words | "experts argue", "observers have cited", "industry reports" with no named source | Name the source or cut the claim |
| 6 | Formulaic "Challenges/Future" section | "Despite its... faces several challenges", "Future Outlook" as a rote closer | Cut unless there's a specific, sourced challenge to state |

## Language and grammar patterns

| # | Pattern | Watch for | Fix |
|---|---|---|---|
| 7 | Overused "AI vocabulary" | delve, tapestry (abstract noun), landscape (abstract noun), pivotal, intricate, underscore (verb), garner, crucial, showcase | Plain equivalent, or cut if it adds nothing |
| 8 | Copula avoidance | "serves as", "stands as", "boasts" in place of "is"/"are"/"has" | Use the plain verb |
| 9 | Negative parallelism / tailing negation | "It's not just X, it's Y"; a clipped negation ("no guessing") tacked onto a sentence instead of a real clause | Write the direct claim once |
| 10 | Rule-of-three overuse | Ideas forced into triads to look comprehensive | Keep only the items that are actually distinct and load-bearing |
| 11 | Elegant variation (synonym cycling) | Referring to the same entity with a new synonym every sentence ("the protagonist" / "the main character" / "the hero") | Reuse the same term; readers don't need variety here |
| 12 | False ranges | "From X to Y" where X and Y aren't on a real scale | State the actual scope directly |
| 13 | Passive voice / subjectless fragments | "No configuration file needed.", "Results are preserved automatically." | Active voice with a named actor, when it improves clarity |

## Style / formatting patterns

| # | Pattern | Watch for | Fix |
|---|---|---|---|
| 14 | Em/en dash overuse | `—` or `–` doing the job of a comma, period, colon, or parentheses | Replace with the mark actually called for; this one is close to a hard rule — check the final draft for stray `—`/`–` |
| 15 | Boldface overuse | Mechanically bolding phrases mid-sentence | Bold only true emphasis or defined terms, sparingly |
| 16 | Inline-header vertical lists | `- **Label:** sentence that restates Label` repeated | Prose paragraph, or a real list without redundant restated headers |
| 17 | Title Case headings | "## Strategic Negotiations And Global Partnerships" | Sentence case headings |
| 18 | Decorative emojis | 🚀 / 💡 / ✅ on headings or bullets in non-casual content | Cut unless the register genuinely calls for them |
| 19 | Curly quotes where the document's convention is straight | Mixed `"..."` / `"..."` | Match the document's existing convention |

## Communication artifacts (only relevant if chatbot output was pasted in)

| # | Pattern | Watch for |
|---|---|---|
| 20 | Chat leftovers | "I hope this helps!", "Let me know if...", "Here is an overview of..." |
| 21 | Knowledge-cutoff / speculative gap-filling | "As of [date]...", "While specific details are limited...", inventing plausible-sounding biography to cover an actual gap | State what isn't known, or cut the sentence — never dress a guess as fact |
| 22 | Sycophantic tone | "Great question!", "You're absolutely right that..." |

## Filler and hedging

| # | Pattern | Before | After |
|---|---|---|---|
| 23 | Filler phrases | "In order to achieve this goal" | "To achieve this" |
| 24 | Excessive hedging | "It could potentially possibly be argued that..." | "It may be argued that..." |
| 25 | Generic positive conclusion | "The future looks bright... exciting times lie ahead" | State the actual next concrete fact, or cut |
| 26 | Hyphenated-pair overuse in predicate position | "the report is high-quality" | "the report is high quality" (keep the hyphen only when attributive: "a high-quality report") |
| 27 | Persuasive-authority tropes | "The real question is...", "at its core", "what really matters" | State the point plainly; usually the sentence after the trope was the whole point |
| 28 | Signposting/announcement | "Let's dive in", "here's what you need to know" | Just say the thing |

## What NOT to flag (avoid over-editing false positives)

Directly reinforces the conservative-editing rule in `core/rewriting.md`:
none of these, alone, justify a rewrite.

- Perfect grammar and polished style — professionals and edited prose look like this too.
- Mixed casual/formal register — common in technical writers, not a tell.
- "Bland" prose with none of the specific patterns above — that's just dry writing.
- Formal vocabulary used precisely — flatten only the *specific* overused words in
  pattern 7, never all sophisticated vocabulary.
- One `however`, one em dash, one curly quote in isolation — these are only
  meaningful clustered with several other patterns from this file.
- Unsourced claims in casual writing — most everyday text has no citations.

When several patterns cluster in the same passage, that's a real finding worth
raising. One isolated instance usually isn't — leave it, per the conservative-
editing rule.

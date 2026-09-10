# Natural Voice — Core Principles

Platform-independent methodology. No adapter-specific instructions, syntax,
or commands belong here. These principles apply identically on every platform adapter,
present or future.

## 1. Authenticity

The objective is natural, author-consistent writing — not artificial imperfections.

- Model the author's genuine characteristics; do not manufacture defects to appear human.
- Never introduce errors, slang, or randomness solely to change how the text might be perceived.
- Authenticity = clarity + coherence + voice consistency, not noise.

## 2. Meaning Preservation

- Do not change the author's intended meaning, claims, conclusions, or reasoning chain.
- Do not upgrade, downgrade, or hedge factual claims during rewriting.
- If a passage is ambiguous, preserve the ambiguity and flag it; do not silently resolve it.

## 3. Voice Preservation

Preserve the author's genuine:

- vocabulary level and word choices
- tone and formality
- perspective (first/third person, stance toward the subject)
- reasoning style (deductive, narrative, explanatory, argumentative)
- characteristic sentence rhythms and paragraph habits

Prefer minimal necessary changes over complete stylistic replacement, unless the user
explicitly requests a major rewrite.

## 4. Clarity

Improve writing that is unclear or unnecessarily complicated:

- concrete verbs over nominalizations where meaning is preserved
- one idea per sentence, one focus per paragraph
- remove filler and redundant qualification
- split or reorder only to aid comprehension, not to impose a foreign style

## 5. Natural Variation

Healthy writing varies naturally. Respect and preserve the author's existing variation in:

- sentence length and sentence structure
- paragraph length
- vocabulary range
- transitions and connectives
- rhythm and emphasis

Do not force uniform sentence lengths, uniform paragraph sizes, or a fixed
transition-per-paragraph quota. Do not impose artificial randomness either.

## 6. No Artificial Imperfections

Never deliberately introduce:

- grammar errors or spelling mistakes
- random punctuation or capitalization
- fake uncertainty, fake hesitation, or fake personal touches
- unnatural slang or unnatural vocabulary shifts
- forced sentence randomness

Do not deliberately damage writing quality for any reason, including any attempt
to influence an external detector.

## 7. Factual Integrity

Never fabricate:

- facts, statistics, or experimental results
- sources, citations, or reference entries
- personal experiences, anecdotes, qualifications, or opinions attributed to the author

If input contains unsupported claims, preserve the user's meaning and flag the gap
(e.g. `[citation needed]`, `[verify number]`) instead of inventing support.

Do not imitate a specific real person's identity or writing style without authorization.
Model only the current user's own writing.

## 8. Context Awareness

Writing decisions depend on:

- **audience** (general reader, reviewer, engineer, peer)
- **purpose** (explain, argue, document, narrate, persuade)
- **genre / register** (general, academic, technical, casual — see adapter modes)
- **domain** (terminology and conventions must survive rewriting)
- **author's actual style** (inferred from current input; in future, from an Author Voice Profile)

The same sentence may be rewritten differently for a journal, a code comment, or a chat
message. Infer context from the request; default to general clear writing when ambiguous.

## 9. Boundary (what Natural Voice is not)

Natural Voice does not:

- guarantee or advertise "100% human", "undetectable", or any detector-bypass outcome
- produce authorship verdicts or scores
- claim that linguistic signals prove who or what wrote a text

External AI-text detectors are probabilistic and domain-dependent. This project focuses
on writing quality, authenticity, and voice consistency.

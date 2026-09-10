# Natural Voice — Rewriting Methodology

Platform-independent editing pipeline. Adapters invoke it; they do not redefine it.

## Pipeline

```text
Input
 ↓
Understand meaning
 ↓
Identify audience
 ↓
Identify purpose
 ↓
Identify genre
 ↓
Identify tone
 ↓
Analyze existing voice
 ↓
Identify unnecessary/generic wording
 ↓
Improve clarity
 ↓
Improve sentence flow
 ↓
Improve paragraph coherence
 ↓
Preserve voice
 ↓
Verify meaning
 ↓
Final writing
```

## Step notes

1. **Understand meaning** — paraphrase the claim structure internally before changing any words.
2. **Audience / purpose / genre / tone** — fix the register first; it constrains every later edit.
   Defaults: general audience, explanatory purpose, general genre, author's current tone.
3. **Analyze existing voice** — note vocabulary level, typical sentence lengths, paragraph
   habits, transition density, formality, and technical-term density from the input itself,
   or compare against an Author Voice Profile when one exists (see `voice-model.md`;
   implemented: `profile/`, `comparison/`, `revision/`).
4. **Identify unnecessary/generic wording** — filler openers, empty intensifiers,
   redundant pairs, formulaic transitions that carry no logical relation.
5. **Improve clarity** — concrete verbs, resolved pronouns, trimmed qualification.
6. **Improve sentence flow** — vary length only within the author's existing range;
   fix awkward order; do not impose a foreign rhythm.
7. **Improve paragraph coherence** — one focus per paragraph; keep topic continuity;
   split or merge only when the idea structure demands it.
8. **Preserve voice** — re-check: same perspective, same terminology, same stance,
   same level of formality as the input.
9. **Verify meaning** — factual claims, numbers, citations, code identifiers, quoted
   material, and reasoning steps must be unchanged. Flag anything that cannot be verified.

## Conservative-editing rule

When the user already has a strong personal style, prefer **minimal necessary changes**
over complete stylistic replacement — unless the user explicitly asks for a major rewrite.

- Light touch (default): fix clarity and flow, remove filler, keep the author's sentences recognizable.
- Major rewrite (only on explicit request): restructure freely, but still preserve meaning,
  facts, citations, terminology, and perspective per `principles.md`.

## Output contract (recommended for all adapters)

1. **Revised text** — the complete rewrite (primary output).
2. **What changed (brief)** — 3–7 bullets maximum.
3. **Flags (only if needed)** — unsupported claims, missing citations, or ambiguities
   preserved rather than resolved.

Do not emit internal reasoning traces. Keep the change list short.

## Implemented revision architecture (Phase 7)

The pipeline above is executed by `revision/` (v0.1.0) over any `LLMProvider`
(`llm/`): structured prompt (principles + rendered profile + prioritized
comparison deviations + user request + delimited draft) → provider → parse
(JSON preferred, plain-text fallback) → validate (numbers/citations/length/
similarity gates + re-compare drift warning) → accept or one guided retry.
Modes: conservative (default), balanced, expressive — all bound by
`principles.md` (no fabrication, no artificial errors, no detector optimization).
Contract: `analysis/revision-spec.md`.

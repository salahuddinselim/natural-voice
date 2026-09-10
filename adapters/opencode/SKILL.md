---
name: natural-voice
description: Improve AI-assisted or rough-draft text into natural, clear, voice-consistent writing. Use when the user asks to make text more natural, clearer, less generic, better flowing, simpler, more conversational, academically or technically appropriate, rewritten in their style, or preserved in their voice.
---

# Natural Voice — OpenCode Adapter (v0.7)

This adapter translates the platform-independent Natural Voice core into OpenCode behavior.
The methodology lives in the core; this file only defines activation and execution.

## Core sources (read as needed)

Relative to the repository root:

- `core/principles.md` — what Natural Voice is; preserve/improve/forbidden lists
- `core/rewriting.md` — editing pipeline + output contract (follow in order)
- `core/voice-model.md` — Author Voice Profile concept and boundaries
- `analysis/voice-profile-spec.md` — profile schema (v0.1), confidence levels, scope, privacy
- `analysis/feature-spec.md` — profile-vs-draft comparison method + interpretation categories
- `core/research.md` — research summary + findings-vs-decisions rule
- `references/research-foundation.md` — detailed paper methodology
- `references/writing-patterns.md` — statistical/structural editing signals
- `references/ai-phrasing-patterns.md` — named, concrete phrasing defects
  (em-dash overuse, vague attributions, AI-vocabulary words, and more)

If a conflict arises between this adapter and the core, the core wins on methodology;
this adapter wins only on OpenCode mechanics (triggering, tool use, output delivery).

## When to activate

Activate when the user asks to:

- make this more natural / improve this writing / rewrite this
- make this sound like me / rewrite this in my style / preserve my writing style
- make this less generic / remove unnecessary generic wording
- improve the flow / simplify this writing / make this clearer
- improve academic writing / make academically appropriate
- improve technical writing / make technically precise
- make this more conversational / more direct / more readable
- analyze my writing style / analyze these writing samples
- build my voice profile / create a profile from these files
- show me my writing characteristics
- rewrite this using my voice profile / improve this while keeping my style
- make this clearer without changing my tone
- make this consistent with my academic voice
- use my voice profile to revise this
- rewrite this using my style / compare this draft with my style
- tell me where this draft differs from my normal writing

Do not activate for unrelated requests. Never proactively rewrite files the user did not ask about.

## How to execute (OpenCode)

1. Read `core/principles.md` and `core/rewriting.md` before the first rewrite in a session
   (re-read if the task spans modes).
2. Infer the mode from the request (default General):
   - **General:** natural, clear writing for a broad audience.
   - **Academic:** formal, evidence-based; keep citation markers; separate evidence from
     interpretation; no unsupported claims or exaggerated conclusions; keep the author's
     voice (no flattening into generic journal language).
   - **Technical:** precision first; concise; correct terminology; code/documentation
     consistency; never vaguer synonyms for precise terms.
   - **Casual:** conversational; simpler structures; contractions only if the author uses
     them; no added slang.
3. Follow the `core/rewriting.md` pipeline in order (meaning → audience → purpose → genre →
   tone → voice → generic-wording → clarity → flow → coherence → voice check → meaning check).
4. Apply the output contract from `core/rewriting.md`: revised text, 3–7 change bullets,
   flags only if needed. No reasoning traces.
5. Consult `references/writing-patterns.md` when diagnosing repetition, transitions, or
   paragraph issues, and `references/ai-phrasing-patterns.md` when diagnosing generic/
   clichéd phrasing (step 4 of the pipeline). Consult `references/research-foundation.md`
   only if the user asks about the research basis — never to render an authorship verdict.
6. Voice-profile requests (builder implemented in v0.4: `profile/`, local only):
   - "Analyze these samples" / "show my writing characteristics": run the builder
     (`build_profile` / `build_profile_from_files`, or the CLI:
     `python -m natural_voice_profile build <files> --pretty`) and summarize the
     resulting profile in the spec's qualitative terms (complexity bands, stability,
     typical ranges). Samples stay local; only the derived profile may be kept, in a
     user-owned file (e.g. `profile.json`), never in this repo.
   - "Build my voice profile": same as above, plus offer to save via `save_profile`.
     State the `confidence.overall` level plainly; if `low`, say
     `Voice profile confidence: Low` and edit conservatively.
   - "Compare this draft with my voice profile" / "where does this draft differ from
     my writing style" / "does this draft match my usual sentence structure" /
     "analyze the stylistic differences" / "show inconsistent parts": run the
     comparison engine (`compare_draft` / `compare_draft_file`, or the CLI:
     `python -m natural_voice_comparison --draft <file> --profile <file> --pretty`)
     and present its report: overall status + confidence, per-dimension
     Close/Moderately/Significantly different findings with draft-vs-typical-range
     numbers, the evidence basis (profile samples/words, draft words), and cautions
     (low confidence, context mismatch, N-gram topic caveat). Frame results as "this
     draft differs from your normal writing style in these areas" — never as an
     authorship score.
   - "Rewrite using my voice profile" / "improve while keeping my style" /
     "clearer without changing my tone" / "consistent with my academic voice":
     run the platform-independent revision engine (`revise` in `revision/`,
     prompt construction per `analysis/revision-spec.md`, validation before
     presenting). State the mode used (default conservative), what changed, and
     any validation warnings. Refuse detector-evasion framings outright; never
     duplicate the revision methodology here — invoke it, don't restate it.
   - See `examples/voice-profile-example.md` (illustrated) and
     `examples/example_voice_profile.json` (real builder output on synthetic samples).

## Boundaries (binding)

- Preserve meaning, facts, citations, terminology, perspective (per core).
- Never fabricate experiences, results, statistics, sources, citations, or opinions.
- Never introduce errors, slang, or randomness to affect perceived authorship.
- No "100% human" / "undetectable" / detector-bypass claims; no authorship verdicts or scores.
- v0.7 revises via the platform-independent engine (`revision/` over `llm/`)
  but has no persistent-profile system: profiles, reports, and revisions are built
  on demand, held by the user (conversation or user-owned files), never stored by
  the framework. Do not commit user samples, profiles, drafts, reports, or revisions
  to the repo. With `low` confidence or no samples, infer voice from the current
  input only. Never emit authorship verdicts, scores, or detector-related claims.

## Compatibility note

The live OpenCode skill entrypoint is `.opencode/skills/natural-voice/SKILL.md`,
which points to this adapter. Keep `name: natural-voice` and this description identical
in both files so discovery behavior is unchanged.

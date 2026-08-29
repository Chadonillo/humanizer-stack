---
name: no-ai-slop
description: >-
  Run the second surface-quality pass in the humanizer stack. Preserve the writer's
  voice while removing binary contrasts, throat-clearing, faux insights, colon
  reveals, dramatic fragments, fake-profound endings, formatting slop, and dash
  punctuation. Use after `humanizer` for both regular and deep humanization. In deep
  mode, run `structural-humanizer` after this skill.
---

# No AI slop

This is the surface quality gate adapted from
[petergyang/no-ai-slop](https://github.com/petergyang/no-ai-slop). It catches patterns
that overlap with `humanizer` and adds several useful checks the first pass does not
cover.

## Position in the stack

- **Regular humanization:** `humanizer` -> `no-ai-slop`
- **Deep humanization:** `humanizer` -> `no-ai-slop` -> `structural-humanizer`

Always run this pass. Deep mode adds the structural pass; it does not replace this one.

## Editing principles

- Preserve the writer's meaning, vocabulary, cadence, humor, uncertainty, useful
  digressions, and level of polish.
- Make the minimum effective edit. Leave strong human sentences alone.
- Do not invent facts, examples, statistics, quotations, feelings, or opinions.
- Lead with the point when the setup adds nothing, but keep personal setup that adds
  context or character.
- Prefer concrete details and direct verbs over abstractions and fake-strong verbs.
- Repeat the clear noun when it is still the right noun. Do not cycle synonyms merely
  to avoid repetition.
- Keep active voice when it identifies the real actor more clearly.
- Do not make every paragraph equally tidy. Consistency is not worth flattening a
  recognizable voice.

## Patterns to remove

1. **Binary contrasts and negative listing.** Cut “It is not X. It is Y,” “not just X
   but Y,” and “Not X. Not Y. Z.” State the real claim directly.
2. **Throat-clearing.** Cut “Here is the thing,” “Let me be clear,” and generic honesty
   announcements when the following sentence already carries the point.
3. **Faux-insight setups.** Remove “What nobody tells you,” “The part everyone misses,”
   and similar claims that flatter the writer as the lone expert.
4. **Colon reveals.** Do not use a noun phrase plus a colon for fake drama (“The best
   part: it learns”). Use a normal sentence. Keep colons for lists, labels, quotations,
   and grammar that genuinely needs them.
5. **Interpretive metadiscourse.** Cut “The key point is,” “As you can see,” “That last
   part matters,” and redundant “In other words” lines. Add evidence when the claim is
   not yet clear.
6. **Superficial analysis.** Remove trailing `-ing` clauses that only pretend to explain
   significance.
7. **Importance puffery and weasel attribution.** Replace vague importance claims with
   a fact. Name the source or remove the attribution.
8. **Dramatic fragmentation and robotic rhythm.** Fix stacked punchy fragments and
   repeated sentence shapes without sanding away intentional fragments or spoken
   cadence.
9. **Rhetorical setups.** Remove “What if I told you,” “Think about it,” “Plot twist,”
   and self-answered question-and-answer pairs when a direct sentence works.
10. **Fake-profound and recap endings.** Delete the mic-drop metaphor or summary that
    restates what the reader just read. End on the last concrete point or next action.
11. **Formatting slop.** Remove decorative emoji headings, unnecessary bold emphasis,
    tiny sections with oversized headings, and bullet lists that would read better as
    one or two sentences.

## Dash and hyphen policy

For outward-facing prose in this stack, remove sentence-level dash punctuation during
both regular and deep humanization:

- Do not use an em dash (`—` or `&mdash;`) as a rhythm shortcut.
- Do not substitute an en dash (`–` or `&ndash;`) for the same job.
- Do not replace either one with a spaced ASCII hyphen (`word - word`). That is the
  same construction in a different character.
- Rewrite the sentence with a comma, period, semicolon, or parentheses according to
  its grammar. A colon is not an automatic replacement.

Do **not** remove legitimate hyphens or range marks. Preserve:

- compounds such as `well-known`, `18th-century`, and `user-facing`;
- numeric ranges such as `10-12` or `2024–2026`;
- minus signs, identifiers, command flags, URLs, code, and Markdown list markers;
- exact quotations and official names unless the user asks to normalize them.

Run the surface scanner after editing. Any `copy-dash-break` finding must be fixed or
explicitly marked `copy-ignore` when the usage is intentional.

## Workflow

1. Read the full draft and identify its point and voice signals.
2. Apply the minimum edits needed for the rules above.
3. Run the checks in [eval.md](eval.md).
4. Run `copy_scan.py` on file-based output. Use `--html` for HTML.
5. Fix genuine findings and check that protected hyphens, ranges, code, links, and
   markup remain unchanged.
6. In deep mode, hand the revised text to `structural-humanizer`.

When this skill runs internally as part of writing or sending, return only the output
shape the user requested. Do not append an editing report unless it would help or the
user asks for one.

## Structural precedence

The upstream skill includes broad “show, do not tell” advice. This stack does not apply
that mechanically. In deep mode, `structural-humanizer` owns emotion mode and may
prefer a plain emotion label over an embodied or atmospheric performance.

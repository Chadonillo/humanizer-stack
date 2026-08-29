# The pipeline

Regular humanization uses two surface passes. Deep humanization runs the same two
surface passes and then adds the structural pass.

```
draft
  |
  v
[ pass 1: humanizer ]             words, phrasing, punctuation, common tells
  |
  v
[ pass 2: no-ai-slop ]            voice-preserving quality gate, dash policy
  |                                scanner: scripts/copy_scan.py
  +-----------------------------> regular output
  |
  v
[ pass 3: structural-humanizer ]  discourse shape, arc, emotion mode, reference
  |                                scanner: structural_scan.py, then copy_scan.py again
  v
[ voice layer (optional, yours) ] house style, register, personal rules
  |
  v
deep output / publish
```

## Mode definitions

- **Regular humanize:** `humanizer` -> `no-ai-slop`
- **Deep humanize:** `humanizer` -> `no-ai-slop` -> `structural-humanizer`

Both modes enforce the same dash-and-hyphen policy. Deep mode does not skip or weaken
the surface checks.

## Why this order

`humanizer` clears broad vocabulary and phrasing patterns. `no-ai-slop` then performs a
minimum-edit quality pass that protects the writer's voice while catching faux-insight
setups, colon reveals, dramatic fragments, formatting slop, and sentence-level dash
punctuation.

Structural work comes last because it moves and deletes whole sections. Run the surface
scanner again afterward because section-level rewriting can introduce fresh punctuation
or cadence tells.

The optional voice layer goes last because it is additive. The first three passes remove
signals that should not be there; a voice layer adds signal that should.

## What each layer owns

| Layer | Owns | Does not own |
|---|---|---|
| `humanizer` | Vocabulary, common phrasing, negative parallelism, rule of three, hype copy | Final surface QA, discourse structure |
| `no-ai-slop` | Voice preservation, minimum edit, faux insights, colon reveals, fragments, formatting, dash policy | Theme/arc audits |
| `structural-humanizer` | Stated lessons, tidiness, emotion mode, reference specificity, reader address, shape convergence | Final punctuation check, house style |
| voice layer | Register, rhythm, personal rules | Anything the first three passes handle |

Keeping these responsibilities separate matters. One giant prompt tends to fix every
piece the same way, which creates a new repetitive style.

## Dash and hyphen policy

Both regular and deep modes remove sentence-level:

- em dashes (`—`, `&mdash;`);
- en dashes used as prose breaks (`–`, `&ndash;`);
- spaced ASCII hyphens (`word - word`).

Rewrite with a comma, period, semicolon, or parentheses according to the grammar. A
colon is not an automatic replacement.

Preserve compound-word hyphens, numeric ranges, minus signs, identifiers, command
flags, URLs, code, Markdown list markers, exact quotations, and official names.

## Running the structural pass properly

The structural skill has one instruction people skip: audit the outline, not the prose.

1. Extract the skeleton: beats, repeated lessons, time structure, what resolves,
   tangents, emotion mode, and named versus vague references.
2. Run the six audits one at a time.
3. Choose one or two genre-appropriate interventions.
4. Rewrite structurally.
5. Run `structural_scan.py`.
6. Check the convergence trap: if the fix looks like yesterday's fix, vary it.
7. Run `copy_scan.py` again so structural edits cannot reintroduce surface tells.

## Hooking the scanners

Both scanners support `--strict`, which exits 1 when a configured threshold is met.
That makes them usable as pre-commit or pre-publish gates:

```bash
python3 scripts/copy_scan.py --strict content/**/*.md \
  && python3 skills/structural-humanizer/scripts/structural_scan.py --strict content/**/*.md
```

Use this only for outward-facing content. Applied indiscriminately to internal docs,
code, quotations, and changelogs, a strict prose scanner creates noise.

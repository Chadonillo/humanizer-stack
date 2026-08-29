# No AI slop evaluation

Run this after the second surface pass. Fix genuine failures before returning or
publishing the text.

## Meaning and voice

1. Did the edit preserve every supported claim, name, date, link, citation, recipient,
   attachment, code fragment, and piece of markup?
2. Did it preserve the writer's recognizable vocabulary, cadence, bluntness, humor,
   uncertainty, and useful digressions?
3. Did it leave strong human sentences alone instead of polishing everything to the
   same finish?
4. Were changes proportional to the actual problem?
5. Were no facts, examples, statistics, quotations, feelings, or opinions invented?

## Slop patterns

1. Are binary contrasts, negative listings, throat-clearing, faux-insight setups,
   rhetorical setups, and fake colon reveals gone?
2. Are importance puffery, vague attribution, interpretive metadiscourse, superficial
   `-ing` analysis, fake-strong verbs, and synonym cycling fixed?
3. Are dramatic fragments and repeated sentence shapes fixed without destroying an
   intentional spoken rhythm?
4. Is formatting driven by content rather than decorative emoji, bold, tiny sections,
   or needless bullet lists?
5. Does the ending stop on a concrete point or action instead of a recap or fake-deep
   mic drop?

## Dash and hyphen check

1. Are sentence-level em dashes gone?
2. Are sentence-level en dashes gone?
3. Are spaced ASCII hyphens used as sentence breaks gone?
4. Were legitimate compound-word hyphens preserved?
5. Were numeric ranges, minus signs, identifiers, flags, URLs, code, Markdown syntax,
   quotations, and official names preserved?
6. Does `copy_scan.py` return no unexplained `copy-dash-break` finding?

## Deep mode

For deep humanization, was this evaluation completed before the
`structural-humanizer` pass? After structural rewriting, run the surface scanner again
to make sure section-level edits did not reintroduce dash punctuation or other surface
tells.

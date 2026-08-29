#!/usr/bin/env python3
"""copy_scan.py - deterministic scan for surface copy tells in prose.

Ported from devibe_scan.py in jcarterjohnson/vibecoded-design-tells (MIT),
narrowed to the four mechanical copy rules and adapted for prose files
(markdown, plain text, HTML) rather than web source.

Catches the pattern-matchable slice of the surface layer:

  copy-dash-break   em dash, en dash, or spaced hyphen used as sentence punctuation
  copy-antithesis   "it's not just X, it's Y" / "not only X but Y" (2.8%)
  hype-copy         marketing cliche vocabulary
  copy-servile      sycophantic openers and signposted wrap-ups
  copy-faux-insight throat-clearing and "what nobody tells you" setups
  copy-colon-reveal noun-phrase + lowercase reveal used for fake drama
  copy-fragment     stock dramatic fragments and fake-profound kickers

The cadence tells (uniform sentence rhythm, formulaic shape, polished-but-empty)
are NOT catchable here. See references/copy-tells.md and run the structural pass.

Usage:
  python3 copy_scan.py FILE [FILE ...]
  python3 copy_scan.py --html page.html       # strip tags first
  cat draft.md | python3 copy_scan.py -
  python3 copy_scan.py --json draft.md        # machine-readable output
  python3 copy_scan.py --strict draft.md      # exit 1 on any hit (hook-friendly)

Mark a line with `copy-ignore` to suppress it (intentional usage).
"""

import argparse
import html as html_mod
import json
import re
import sys

RULES = [
    {
        "id": "copy-dash-break",
        "label": "Dash character used as sentence-level punctuation",
        "fix": (
            "Rewrite with a comma, period, semicolon, or parentheses. Preserve "
            "compound-word hyphens, ranges, minus signs, flags, identifiers, URLs, code, "
            "Markdown list markers, quotations, and official names."
        ),
        "pats": [
            r"[A-Za-z0-9][ \t]*(?:—|&mdash;)[ \t]*[A-Za-z0-9]",
            r"[A-Za-z][ \t]+(?:–|&ndash;)[ \t]+[A-Za-z]",
            r"[A-Za-z][ \t]+-[ \t]+[A-Za-z]",
        ],
        # Skip exact quotations, code comments, tables, and fenced-code markers. A
        # Markdown list marker is safe because each pattern requires a letter or digit
        # on both sides, so visible prose inside list items is still checked.
        "suppress": r"^\s*(//|/\*|<!--|>|\||```)",
    },
    {
        "id": "copy-antithesis",
        "label": 'The "it\'s not just X, it\'s Y" sentence (the AI accent)',
        "fix": "State the thing plainly. Lead with the real claim and drop the negation.",
        "pats": [
            r"(it'?s |it |that'?s )?\bnot just\b[^.,;!?]{1,40},?\s*(it'?s|but)\b",
            r"\bnot only\b[^.,;!?]{1,40},?\s*but\b",
        ],
    },
    {
        "id": "hype-copy",
        "label": "AI marketing-copy cliche",
        "fix": "Write what the thing literally does, in plain words, with a checkable claim.",
        "pats": [
            r"\bTransform your\b", r"\bSupercharge\b", r"\bUnleash\b",
            r"\bEffortlessly\b", r"\breimagined\b",
            r"take (your |it |things )?[^.]{0,30}to the next level",
            r"\bGame-?changer\b", r"\bunlock (your |the )?(full )?potential\b",
            r"\b(deep[- ]dive|dive in|let'?s dive)\b", r"\bdelve\b",
            r"\belevate your\b", r"\bin today'?s (fast-paced|digital) world\b",
            r"\bworld-class\b", r"\bcutting-edge\b", r"\brevolutionary\b",
            r"\bbest-in-class\b",
        ],
    },
    {
        "id": "copy-servile",
        "label": "Sycophantic opener / signposted wrap-up",
        "fix": "Start on the real point and end on the real point. Cut the framing.",
        "pats": [
            r"\bGreat question\b", r"\bI hope this helps\b",
            r"\bIn conclusion\b", r"\bIn summary\b",
        ],
    },
    {
        "id": "copy-faux-insight",
        "label": "Throat-clearing or faux-insight setup",
        "fix": "Delete the setup and state the supported claim directly.",
        "pats": [
            r"\bHere'?s the thing\b", r"\bLet me be clear\b",
            r"\bHere'?s what nobody tells you\b", r"\bWhat nobody tells you\b",
            r"\bThe part everyone misses\b", r"\bWhat most people get wrong\b",
            r"\bThe uncomfortable truth is\b", r"\bPlot twist\b",
            r"\bWhat if I told you\b", r"\bThink about it\s*:",
        ],
    },
    {
        "id": "copy-colon-reveal",
        "label": "Colon used for a lowercase dramatic reveal",
        "fix": "Rewrite as a normal sentence. Keep colons for real lists, labels, and quotations.",
        "pats": [
            r"\b(?:the\s+)?(?:best|hardest|wildest|important|key|real)\s+(?:part|thing|point|reason|detail)\s*:\s+[a-z]",
            r"\b(?:the\s+)?(?:secret|truth|reality|answer|result)\s*:\s+[a-z]",
        ],
    },
    {
        "id": "copy-fragment",
        "label": "Stock dramatic fragment or fake-profound kicker",
        "fix": "Use one complete direct sentence or delete the decorative kicker.",
        "pats": [
            r"\bThat'?s it\.\s+That'?s the whole thing\b",
            r"\bThe future isn'?t coming\.\s+It'?s already here\b",
            r"\bNot a\b[^.!?]{1,45}\.\s*\bNot a\b[^.!?]{1,45}\.\s*\bA\b",
        ],
    },
]

TAG_RE = re.compile(r"<[^>]+>")


def compile_rules():
    out = []
    for r in RULES:
        out.append({
            **r,
            "re": [re.compile(p, re.I) for p in r["pats"]],
            "suppress_re": re.compile(r["suppress"], re.I) if r.get("suppress") else None,
        })
    return out


def strip_html(text):
    text = re.sub(r"(?is)<(script|style)\b.*?</\1>", " ", text)
    return html_mod.unescape(TAG_RE.sub(" ", text))


def mask_inline_code(line):
    """Blank inline-code spans without shifting line offsets."""
    return re.sub(r"`[^`]*`", lambda m: " " * len(m.group(0)), line)


def scan(text, rules, path):
    hits = []
    in_fence = False
    for lineno, line in enumerate(text.splitlines(), 1):
        if line.lstrip().startswith("```"):
            in_fence = not in_fence
            continue
        if in_fence or "copy-ignore" in line:
            continue
        visible_line = mask_inline_code(line)
        for rule in rules:
            if rule["suppress_re"] and rule["suppress_re"].search(visible_line):
                continue
            for pat in rule["re"]:
                m = pat.search(visible_line)
                if m:
                    hits.append({
                        "file": path,
                        "line": lineno,
                        "id": rule["id"],
                        "label": rule["label"],
                        "fix": rule["fix"],
                        "match": line[m.start():m.end()].strip()[:80],
                        "text": line.strip()[:120],
                    })
                    break
    return hits


def main():
    ap = argparse.ArgumentParser(description="Scan prose for surface copy tells.")
    ap.add_argument("files", nargs="+", help="files to scan, or - for stdin")
    ap.add_argument("--html", action="store_true", help="strip HTML tags before scanning")
    ap.add_argument("--json", action="store_true", help="machine-readable output")
    ap.add_argument("--strict", action="store_true", help="exit 1 if any tell is found")
    args = ap.parse_args()

    rules = compile_rules()
    all_hits = []

    for path in args.files:
        if path == "-":
            text, label = sys.stdin.read(), "<stdin>"
        else:
            try:
                with open(path, encoding="utf-8") as fh:
                    text = fh.read()
            except OSError as exc:
                print(f"skip {path}: {exc}", file=sys.stderr)
                continue
            label = path
        if args.html or path.endswith((".html", ".htm")):
            text = strip_html(text)
        all_hits.extend(scan(text, rules, label))

    if args.json:
        print(json.dumps({"hits": all_hits, "count": len(all_hits)}, indent=2))
    elif not all_hits:
        print("clean: no mechanical copy tells found.")
        print("Cadence tells still need your eyes. See references/copy-tells.md.")
    else:
        by_rule = {}
        for h in all_hits:
            by_rule.setdefault(h["id"], []).append(h)
        for rid, hits in sorted(by_rule.items(), key=lambda kv: -len(kv[1])):
            print(f"\n{rid}  ({len(hits)} hit{'s' if len(hits) != 1 else ''})")
            print(f"  {hits[0]['label']}")
            print(f"  fix: {hits[0]['fix']}")
            for h in hits[:12]:
                print(f"    {h['file']}:{h['line']}  [{h['match']}]  {h['text']}")
            if len(hits) > 12:
                print(f"    ... and {len(hits) - 12} more")
        print(f"\ntotal: {len(all_hits)} hits across {len(by_rule)} categories")
        print("Cadence tells are not scannable. See references/copy-tells.md.")

    if args.strict and all_hits:
        sys.exit(1)


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""Regression tests for dash and no-ai-slop scanner rules."""

import importlib.util
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("copy_scan", ROOT / "scripts" / "copy_scan.py")
copy_scan = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(copy_scan)
RULES = copy_scan.compile_rules()


def ids(text):
    return {hit["id"] for hit in copy_scan.scan(text, RULES, "<test>")}


class CopyScanTests(unittest.TestCase):
    def assert_dash(self, text):
        self.assertIn("copy-dash-break", ids(text), text)

    def assert_no_dash(self, text):
        self.assertNotIn("copy-dash-break", ids(text), text)

    def test_sentence_dash_variants(self):
        self.assert_dash("The plan works—it is already deployed.")
        self.assert_dash("The plan works — it is already deployed.")
        self.assert_dash("The plan works &mdash; it is already deployed.")
        self.assert_dash("The plan works – it is already deployed.")
        self.assert_dash("The plan works &ndash; it is already deployed.")
        self.assert_dash("The plan works - it is already deployed.")

    def test_protected_hyphens_and_ranges(self):
        self.assert_no_dash("A well-known user-facing tool shipped in an 18th-century building.")
        self.assert_no_dash("Use versions 10-12 during 2024–2026.")
        self.assert_no_dash("The temperature was -5 and the delta was −3.")
        self.assert_no_dash("Run --strict against job-id-123 at https://example.com/a-b.")

    def test_markdown_and_code(self):
        self.assert_no_dash("- A normal Markdown list item")
        self.assert_dash("- The result works - it is deployed.")
        self.assert_no_dash("Use `word - word`, not the prose form.")
        self.assert_no_dash("```\nThe plan works - it is deployed.\n```")
        self.assert_no_dash("> Exact quote — preserve it.")

    def test_intentional_suppression(self):
        self.assert_no_dash("The house style allows this — here. copy-ignore")

    def test_added_no_ai_slop_patterns(self):
        self.assertIn("copy-faux-insight", ids("What nobody tells you is that distribution matters."))
        self.assertIn("copy-colon-reveal", ids("The best part: it learns."))
        self.assertIn("copy-fragment", ids("That's it. That's the whole thing."))
        self.assertIn("copy-fragment", ids("The future isn't coming. It's already here."))


if __name__ == "__main__":
    unittest.main()

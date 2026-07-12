"""Tests for content generation quality guards."""
from __future__ import annotations

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))

from content_quality import (  # noqa: E402
    assert_quality,
    is_deleted_guide,
    is_deleted_univ,
    quality_issues,
)


class ContentQualityTests(unittest.TestCase):
    def test_rejects_template_headings(self):
        body = """
## Who This Guide Is For
x
## How to Compare Your Options
| a | b |
| --- | --- |
| 1 | 2 |
## Recommended Decision Process
y
## Common Mistakes to Avoid
z
## Final Checklist
w
""" + ("more text " * 800)
        issues = quality_issues(body, kind="guide", require_tables=1)
        self.assertTrue(any("template headings" in i for i in issues))

    def test_accepts_unique_long_guide(self):
        table = "| A | B |\n| --- | --- |\n| 1 | 2 |\n\n| C | D |\n| --- | --- |\n| 3 | 4 |\n"
        body = "## Housing costs in Tokyo\n\n" + table + ("Practical detail. " * 400)
        assert_quality(body, kind="guide", require_tables=2)

    def test_diet_plan_deleted_lookups(self):
        self.assertTrue(is_deleted_guide("tokyo-school-near-yamanote"))
        self.assertTrue(is_deleted_univ("univ_osaka-university"))
        self.assertFalse(is_deleted_guide("housing"))


if __name__ == "__main__":
    unittest.main()

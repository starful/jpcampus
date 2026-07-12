"""Shared content-quality guards for generation scripts.

Prevents repeating the AdSense thin-content pattern:
- identical longtail template headings
- writing deleted slugs again
- saving bodies that are too short or lack substance
"""
from __future__ import annotations

import json
import re
from functools import lru_cache
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
ROOT = SCRIPT_DIR.parent
PLAN_PATH = ROOT / "data" / "content_diet" / "plan.json"

# Headings that marked the mass-produced longtail batch we deleted.
FORBIDDEN_HEADINGS = frozenset(
    {
        "who this guide is for",
        "how to compare your options",
        "recommended decision process",
        "common mistakes to avoid",
        "final checklist",
    }
)

MIN_GUIDE_CHARS = 5500
MIN_ENTITY_CHARS = 4500
MIN_TABLES = 1


@lru_cache(maxsize=1)
def load_diet_plan() -> dict:
    if not PLAN_PATH.exists():
        return {}
    try:
        return json.loads(PLAN_PATH.read_text(encoding="utf-8"))
    except Exception:
        return {}


def deleted_guide_slugs() -> set[str]:
    plan = load_diet_plan()
    return {str(s).strip() for s in plan.get("delete_guides", []) if str(s).strip()}


def deleted_univ_ids() -> set[str]:
    plan = load_diet_plan()
    return {str(s).strip() for s in plan.get("delete_univs", []) if str(s).strip()}


def is_deleted_guide(slug: str) -> bool:
    return slug.strip() in deleted_guide_slugs()


def is_deleted_univ(school_id: str) -> bool:
    sid = school_id.strip()
    if not sid.startswith("univ_"):
        sid = f"univ_{sid}"
    return sid in deleted_univ_ids()


def extract_h2_headings(body: str) -> list[str]:
    return [m.group(1).strip() for m in re.finditer(r"^##\s+(.+)$", body or "", re.M)]


def count_markdown_tables(body: str) -> int:
    # A table needs a header separator row with pipes.
    return len(re.findall(r"^\|[-: ]+\|", body or "", re.M))


def quality_issues(
    body: str,
    *,
    kind: str = "guide",
    min_chars: int | None = None,
    require_tables: int | None = None,
) -> list[str]:
    """Return human-readable problems; empty list means OK."""
    text = (body or "").strip()
    issues: list[str] = []
    floor = min_chars
    if floor is None:
        floor = MIN_GUIDE_CHARS if kind == "guide" else MIN_ENTITY_CHARS
    tables_needed = MIN_TABLES if require_tables is None else require_tables

    if len(text) < floor:
        issues.append(f"too short ({len(text)} < {floor} chars)")

    headings = [h.lower() for h in extract_h2_headings(text)]
    banned_hits = [h for h in headings if h in FORBIDDEN_HEADINGS]
    if len(banned_hits) >= 3:
        issues.append(f"template headings detected: {banned_hits[:5]}")

    if tables_needed > 0 and count_markdown_tables(text) < tables_needed:
        issues.append(f"need at least {tables_needed} markdown table(s)")

    # Obvious empty / placeholder bodies
    if text.lower() in {"", "no content available.", "n/a"}:
        issues.append("empty or placeholder body")

    return issues


def assert_quality(body: str, *, kind: str = "guide", **kwargs) -> None:
    issues = quality_issues(body, kind=kind, **kwargs)
    if issues:
        raise ValueError("; ".join(issues))


GUIDE_QUALITY_PROMPT_RULES = """
Quality rules (mandatory):
- Answer the search intent in the first section (no fluff-only intro).
- Do NOT use these template section titles: "Who This Guide Is For",
  "How to Compare Your Options", "Recommended Decision Process",
  "Common Mistakes to Avoid", "Final Checklist".
- Use unique ## headings tailored to THIS topic.
- Include at least two Markdown tables with concrete comparisons or checklists.
- Be specific (costs, steps, documents, city differences). Avoid generic filler.
- Generate ONLY Markdown body (no frontmatter, no surrounding JSON unless asked).
""".strip()

ENTITY_QUALITY_PROMPT_RULES = """
Quality rules (mandatory):
- Write specifically about THIS institution (city, programs, strengths). No interchangeable boilerplate.
- Do NOT copy a fixed five-section template used across many pages.
- Prefer concrete facts from provided data; if unknown, say so instead of inventing precise stats.
- Include at least one Markdown table when course/faculty/tuition data exists.
- Body length target: 5500–8000 characters.
""".strip()

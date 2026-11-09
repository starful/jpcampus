#!/usr/bin/env python3
"""
Auto-apply noindex to duplicate/low-quality guide pages flagged by GSC.

Takes a Search Console "Pages" (Index Coverage) export CSV -- URL + state
columns -- finds rows whose state marks the URL as a duplicate or stuck
"not indexed", and cross-checks each matching guide against the existing
thin-content rule (app/seo.py:is_thin_content) before adding it to
data/seo_overrides.json's noindex_slugs list. Only confirmed thin pages are
written; everything else is printed for manual review so a decent page
that simply hasn't been crawled yet is never noindexed by mistake.

Dry run by default. Pass --apply to write data/seo_overrides.json.

Usage:
    python scripts/noindex_from_gsc.py gsc_pages_export.csv
    python scripts/noindex_from_gsc.py gsc_pages_export.csv --apply
"""
from __future__ import annotations

import argparse
import csv
import json
import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from app.content_loader import ContentNotFoundError, load_guide_content
from app.seo import is_thin_content
from app.seo_overrides import noindex_slugs

SEO_OVERRIDES_PATH = ROOT_DIR / "data" / "seo_overrides.json"

# GSC "Coverage"/"Indexing" states that mean the URL is excluded as a
# duplicate or low-value page, not a server/crawl error we'd need to fix.
NOINDEX_CANDIDATE_STATES = {
    "duplicate without user-selected canonical",
    "duplicate, google chose different canonical than user",
    "crawled - currently not indexed",
    "discovered - currently not indexed",
}


def _slug_from_url(url: str) -> str | None:
    path = (url or "").split("?", 1)[0].rstrip("/")
    if "/guide/" not in path:
        return None
    return path.rsplit("/guide/", 1)[-1].strip() or None


def _find_column(fieldnames: list[str], *candidates: str) -> str | None:
    lowered = {name.lower().strip(): name for name in fieldnames}
    for candidate in candidates:
        if candidate in lowered:
            return lowered[candidate]
    return None


def candidate_slugs(rows: list[dict[str, str]]) -> dict[str, str]:
    """slug -> GSC state, for rows whose state matches NOINDEX_CANDIDATE_STATES."""
    if not rows:
        return {}
    url_col = _find_column(list(rows[0].keys()), "url", "page", "address")
    state_col = _find_column(
        list(rows[0].keys()), "coverage state", "index state", "indexing state", "coverage"
    )
    if not url_col or not state_col:
        raise ValueError(f"Could not find URL/state columns in CSV header: {list(rows[0].keys())}")

    found: dict[str, str] = {}
    for row in rows:
        state = (row.get(state_col) or "").strip().lower()
        if state not in NOINDEX_CANDIDATE_STATES:
            continue
        slug = _slug_from_url(row.get(url_col) or "")
        if slug:
            found[slug] = state
    return found


def confirm_low_quality(slug: str, lang: str = "en") -> bool:
    """Only noindex slugs that are also thin content by our own rule --
    avoids noindexing a decent page just because GSC hasn't indexed it yet."""
    try:
        _item, content_html = load_guide_content(slug, lang)
    except ContentNotFoundError:
        return False
    return is_thin_content(content_html)


def apply_noindex(to_add: list[str]) -> int:
    with open(SEO_OVERRIDES_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)
    merged = sorted(set(data.get("noindex_slugs", [])) | set(to_add))
    data["noindex_slugs"] = merged
    with open(SEO_OVERRIDES_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
        f.write("\n")
    return len(merged)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("csv_path", type=Path, help="GSC Pages (Index Coverage) export CSV")
    parser.add_argument(
        "--apply", action="store_true", help="Write data/seo_overrides.json (default: dry run)"
    )
    args = parser.parse_args()

    if not args.csv_path.exists():
        print(f"CSV not found: {args.csv_path}", file=sys.stderr)
        return 1

    with open(args.csv_path, newline="", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
    candidates = candidate_slugs(rows)

    already = noindex_slugs()
    to_add: list[str] = []
    skipped: list[str] = []
    for slug, state in sorted(candidates.items()):
        if slug in already:
            continue
        if confirm_low_quality(slug):
            to_add.append(slug)
        else:
            skipped.append(slug)

    print(f"GSC rows matching non-indexed/duplicate states: {len(candidates)}")
    print(f"Already noindexed: {len(candidates) - len(to_add) - len(skipped)}")
    print(f"Confirmed thin content -> noindex: {len(to_add)}")
    for slug in to_add:
        print(f"  + {slug} ({candidates[slug]})")
    print(f"Skipped (not thin content, needs manual review): {len(skipped)}")
    for slug in skipped:
        print(f"  ? {slug} ({candidates[slug]})")

    if not args.apply:
        print("\nDry run only -- rerun with --apply to write data/seo_overrides.json")
        return 0

    if not to_add:
        print("\nNothing to apply.")
        return 0

    total = apply_noindex(to_add)
    print(f"\nApplied: data/seo_overrides.json now has {total} noindex_slugs.")
    return 0


if __name__ == "__main__":
    sys.exit(main())

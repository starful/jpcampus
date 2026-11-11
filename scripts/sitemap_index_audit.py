#!/usr/bin/env python3
"""
Compare sitemap.xml against a GSC Index Status export to find submitted
pages that aren't indexed, and flag the duplicate/thin ones as noindex
candidates.

Takes a Search Console "Pages" (Index Coverage) export CSV -- URL + coverage/
index state columns, same shape as scripts/noindex_from_gsc.py and
scripts/check_broken_redirects.py expect -- and:

1. Fetches the live /sitemap.xml (via TestClient) and collects every
   submitted <loc> URL.
2. Cross-references each submitted URL against the GSC export to find which
   ones are missing from the report (never crawled) or sit in a
   "not indexed" state.
3. Among the not-indexed ones, flags duplicate/low-quality candidates for
   noindex using the same thin-content rule as noindex_from_gsc.py --
   printed for manual review only; nothing is written automatically.

Report only. Does not modify data/seo_overrides.json -- rerun confirmed
guide slugs through scripts/noindex_from_gsc.py --apply if you want that.

Usage:
    python scripts/sitemap_index_audit.py gsc_index_status_export.csv
"""
from __future__ import annotations

import argparse
import csv
import sys
import xml.etree.ElementTree as ET
from pathlib import Path
from urllib.parse import urlparse

ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from fastapi.testclient import TestClient

from app.content_loader import ContentNotFoundError, load_guide_content
from app.main import app
from app.seo import is_thin_content

SITEMAP_NS = {"sm": "http://www.sitemaps.org/schemas/sitemap/0.9"}

INDEXED_STATE = "submitted and indexed"

# GSC "Coverage"/"Indexing" states that mean the URL is excluded as a
# duplicate or low-value page, not a server/crawl error we'd need to fix.
NOINDEX_CANDIDATE_STATES = {
    "duplicate without user-selected canonical",
    "duplicate, google chose different canonical than user",
    "crawled - currently not indexed",
    "discovered - currently not indexed",
}


def _find_column(fieldnames: list[str], *candidates: str) -> str | None:
    lowered = {name.lower().strip(): name for name in fieldnames}
    for candidate in candidates:
        if candidate in lowered:
            return lowered[candidate]
    return None


def _path_from_url(url: str) -> str:
    path = urlparse(url).path.rstrip("/")
    return path or "/"


def _slug_from_path(path: str) -> str | None:
    if "/guide/" not in path:
        return None
    return path.rsplit("/guide/", 1)[-1].strip() or None


def fetch_sitemap_paths(client: TestClient) -> list[str]:
    """Submitted sitemap.xml URLs, as site-relative paths (dedup, order kept)."""
    res = client.get("/sitemap.xml")
    root = ET.fromstring(res.text)
    seen: dict[str, None] = {}
    for loc in root.findall("sm:url/sm:loc", SITEMAP_NS):
        path = _path_from_url(loc.text or "")
        seen.setdefault(path, None)
    return list(seen.keys())


def load_index_states(csv_path: Path) -> dict[str, str]:
    """path -> GSC coverage/index state, for every row in the export."""
    with open(csv_path, newline="", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
    if not rows:
        return {}
    url_col = _find_column(list(rows[0].keys()), "url", "page", "address")
    state_col = _find_column(
        list(rows[0].keys()), "coverage state", "index state", "indexing state", "coverage"
    )
    if not url_col or not state_col:
        raise ValueError(f"Could not find URL/state columns in CSV header: {list(rows[0].keys())}")

    states: dict[str, str] = {}
    for row in rows:
        path = _path_from_url(row.get(url_col) or "")
        state = (row.get(state_col) or "").strip().lower()
        if path:
            states[path] = state
    return states


def confirm_low_quality(path: str, lang: str = "en") -> bool:
    """Only flag paths that are also thin content by our own rule -- avoids
    flagging a decent page just because GSC hasn't indexed it yet."""
    slug = _slug_from_path(path)
    if not slug:
        return False
    try:
        _item, content_html = load_guide_content(slug, lang)
    except ContentNotFoundError:
        return False
    return is_thin_content(content_html)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("csv_path", type=Path, help="GSC Pages (Index Coverage) export CSV")
    args = parser.parse_args()

    if not args.csv_path.exists():
        print(f"CSV not found: {args.csv_path}", file=sys.stderr)
        return 1

    states = load_index_states(args.csv_path)
    client = TestClient(app)
    sitemap_paths = fetch_sitemap_paths(client)

    not_indexed: list[tuple[str, str]] = []
    for path in sitemap_paths:
        state = states.get(path)
        if state is None:
            not_indexed.append((path, "missing from GSC export"))
        elif state != INDEXED_STATE:
            not_indexed.append((path, state))

    noindex_candidates: list[str] = []
    needs_review: list[str] = []
    for path, state in not_indexed:
        if state in NOINDEX_CANDIDATE_STATES and confirm_low_quality(path):
            noindex_candidates.append(path)
        else:
            needs_review.append(f"{path} ({state})")

    print(f"Sitemap URLs checked: {len(sitemap_paths)}")
    print(f"Not indexed: {len(not_indexed)}")
    print(f"\nFlagged as noindex candidates (duplicate/thin content): {len(noindex_candidates)}")
    for path in noindex_candidates:
        print(f"  + {path}")
    print(f"\nNeeds manual review: {len(needs_review)}")
    for line in needs_review:
        print(f"  ? {line}")

    print(
        "\nReport only -- nothing written. To apply noindex to confirmed guide "
        "slugs, run scripts/noindex_from_gsc.py with the same export and --apply."
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())

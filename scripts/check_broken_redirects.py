#!/usr/bin/env python3
"""
Audit app/redirects.json for broken redirects and, optionally, cross-check
a Search Console "not indexed" pages export against the live route table.

Two checks:
1. Walk every rule in app/redirects.json through the real app (via
   TestClient) and flag any source that doesn't 301, any target that 404s,
   and any redirect chain (target itself redirects again).
2. If a GSC pages export CSV is given (URL + coverage/index state columns,
   same shape as scripts/noindex_from_gsc.py expects), find which of the
   "not indexed" URLs currently 404 -- or redirect to a 404 -- on the live
   site. Those are the ones Search Console gave up on because they
   genuinely don't resolve, not because of crawl budget, and are the
   highest-priority fixes.

Usage:
    python scripts/check_broken_redirects.py
    python scripts/check_broken_redirects.py gsc_not_indexed_export.csv
"""
from __future__ import annotations

import argparse
import csv
import sys
from pathlib import Path
from urllib.parse import urlparse

ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from fastapi.testclient import TestClient

from app.config import REDIRECT_MAP
from app.main import app

# GSC "Coverage"/"Indexing" states that mean the URL isn't in the index --
# either it's a dead end (404 / broken redirect) or Google deprioritized it.
NOT_INDEXED_STATES = {
    "duplicate without user-selected canonical",
    "duplicate, google chose different canonical than user",
    "crawled - currently not indexed",
    "discovered - currently not indexed",
    "not found (404)",
    "page with redirect",
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


def load_not_indexed_paths(csv_path: Path) -> dict[str, str]:
    """path -> GSC state, for rows whose state matches NOT_INDEXED_STATES."""
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

    found: dict[str, str] = {}
    for row in rows:
        state = (row.get(state_col) or "").strip().lower()
        if state not in NOT_INDEXED_STATES:
            continue
        path = _path_from_url(row.get(url_col) or "")
        found[path] = state
    return found


def check_redirect_map(client: TestClient) -> tuple[list[str], list[str]]:
    """Returns (broken, chained) messages for rules in app/redirects.json."""
    broken: list[str] = []
    chained: list[str] = []
    for source, target in sorted(REDIRECT_MAP.items()):
        if not target.startswith("/"):
            target = f"/{target}"
        if target == source:
            broken.append(f"{source}: redirects to itself")
            continue

        res = client.get(source, follow_redirects=False)
        if res.status_code != 301:
            broken.append(f"{source}: expected 301, got {res.status_code}")
            continue

        location = res.headers.get("location", "")
        final = client.get(location, follow_redirects=False)
        if final.status_code == 404:
            broken.append(f"{source} -> {location}: target returns 404")
        elif final.status_code == 301:
            chained.append(
                f"{source} -> {location} -> {final.headers.get('location')}: redirect chain"
            )
    return broken, chained


def check_not_indexed(client: TestClient, not_indexed: dict[str, str]) -> list[str]:
    """Flags not-indexed URLs that currently 404 (directly or after a
    redirect) on the live route table."""
    hits: list[str] = []
    for path, state in sorted(not_indexed.items()):
        res = client.get(path, follow_redirects=False)
        if res.status_code == 404:
            hits.append(f"{path}: 404, GSC state = {state}")
        elif res.status_code == 301:
            location = res.headers.get("location", "")
            final = client.get(location, follow_redirects=False)
            if final.status_code == 404:
                hits.append(f"{path} -> {location}: redirect target 404s, GSC state = {state}")
    return hits


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "csv_path",
        type=Path,
        nargs="?",
        help="GSC Pages (Index Coverage) export CSV, for the not-indexed cross-check",
    )
    args = parser.parse_args()

    client = TestClient(app)

    broken, chained = check_redirect_map(client)
    print("== app/redirects.json audit ==")
    print(f"{len(REDIRECT_MAP)} redirect rules checked")
    for line in broken:
        print(f"[BROKEN] {line}")
    for line in chained:
        print(f"[CHAIN]  {line}")
    if not broken and not chained:
        print("No broken redirects or chains found.")

    not_indexed_hits: list[str] = []
    if args.csv_path is not None:
        if not args.csv_path.exists():
            print(f"\nCSV not found: {args.csv_path}", file=sys.stderr)
            return 1
        not_indexed = load_not_indexed_paths(args.csv_path)
        print(f"\n== cross-check vs {len(not_indexed)} not-indexed URLs from {args.csv_path.name} ==")
        not_indexed_hits = check_not_indexed(client, not_indexed)
        for line in not_indexed_hits:
            print(f"[FIX ME] {line}")
        if not not_indexed_hits:
            print("None of the not-indexed URLs 404 on the live route table.")

    if broken or not_indexed_hits:
        print(f"\nFAILED: {len(broken)} broken redirect(s), {len(not_indexed_hits)} dead not-indexed URL(s).")
        return 1

    print("\nPASSED.")
    return 0


if __name__ == "__main__":
    sys.exit(main())

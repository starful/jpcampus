#!/usr/bin/env python3
"""
Regenerate a sitemap.xml snapshot from the live app route, so a cron/CI job
can produce (and validate) a fresh copy on a schedule instead of relying on
someone to fetch /sitemap.xml by hand.

/sitemap.xml itself is already generated fresh on every request (see
app/routes/pages.py); this script just fetches that same route through
TestClient, runs the same structural checks as scripts/seo_guard.py's
sitemap check, and optionally writes the result to disk.

Usage:
    python scripts/regenerate_sitemap.py                  # print XML to stdout
    python scripts/regenerate_sitemap.py --output out.xml  # write to a file
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from fastapi.testclient import TestClient

from app.main import app


def fetch_sitemap_xml(client: TestClient) -> str:
    res = client.get("/sitemap.xml")
    if res.status_code != 200:
        raise RuntimeError(f"/sitemap.xml returned {res.status_code}")
    return res.text


def validate_sitemap(xml: str) -> list[str]:
    """Same structural checks as scripts/seo_guard.py's sitemap check."""
    problems = []
    if "<urlset" not in xml or "<loc>" not in xml:
        problems.append("missing urlset/loc tags")
    if "<lastmod>" not in xml:
        problems.append("missing lastmod tags")
    if 'hreflang="en"' not in xml or 'hreflang="ko"' not in xml:
        problems.append("missing hreflang alternates")
    if "http://127.0.0.1" in xml or "localhost" in xml:
        problems.append("found localhost URL -- check the DOMAIN env var")
    if "?lang=en" in xml:
        problems.append("found a ?lang=en duplicate URL in the sitemap")
    return problems


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--output",
        type=Path,
        default=None,
        help="Write the regenerated sitemap here (default: print to stdout)",
    )
    args = parser.parse_args()

    client = TestClient(app)
    xml = fetch_sitemap_xml(client)

    problems = validate_sitemap(xml)
    if problems:
        for problem in problems:
            print(f"[FAIL] {problem}", file=sys.stderr)
        return 1

    if args.output:
        args.output.write_text(xml, encoding="utf-8")
        print(f"Wrote {args.output} ({len(xml)} bytes)")
    else:
        print(xml)

    return 0


if __name__ == "__main__":
    sys.exit(main())

#!/usr/bin/env python3
"""Fetch Oakhouse building name + address (+ lat/lng) from house_index.

Polite crawl of public listing metadata only.
Usage:
  python scripts/fetch_oakhouse_listings.py --limit 10
  python scripts/fetch_oakhouse_listings.py --resume
"""

from __future__ import annotations

import argparse
import json
import re
import sys
import time
from pathlib import Path
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup

SCRIPT_DIR = Path(__file__).resolve().parent
BASE_DIR = SCRIPT_DIR.parent
DEFAULT_OUT = BASE_DIR / "data" / "oakhouse_listings.json"

INDEX_URL = "https://www.oakhouse.jp/kr/house_index"
BASE = "https://www.oakhouse.jp"
UA = "jpcampus-research/1.0 (+https://jpcampus.net; lodging catalog research)"
DETAIL_RE = re.compile(r"^/kr/(house|apartment)/(\d+)/?$")
COORDS_RE = re.compile(
    r"var\s+lat\s*=\s*([-\d.]+)\s*;\s*var\s+lng\s*=\s*([-\d.]+)\s*;",
    re.IGNORECASE,
)
SKIP_NAMES = {
    "select language:",
    "상세 보기",
    "공실",
    "만실",
    "공실예정",
}


def make_session() -> requests.Session:
    s = requests.Session()
    s.headers.update(
        {
            "User-Agent": UA,
            "Accept": "text/html,application/xhtml+xml",
            "Accept-Language": "ko,en;q=0.8,ja;q=0.7",
        }
    )
    return s


def parse_index(html: str) -> list[dict]:
    """Prefer h4.p-index__name links — stable name/url pairing."""
    soup = BeautifulSoup(html, "lxml")
    items: list[dict] = []
    seen: set[str] = set()

    anchors = soup.select("h4.p-index__name a[href]")
    if not anchors:
        # Fallback: any numeric detail link with visible text
        anchors = [
            a
            for a in soup.select('a[href*="/kr/house/"], a[href*="/kr/apartment/"]')
            if a.get_text(strip=True)
        ]

    for a in anchors:
        href = (a.get("href") or "").strip().split("?")[0].split("#")[0]
        m = DETAIL_RE.match(href)
        if not m:
            continue
        url = urljoin(BASE, href)
        if url in seen:
            continue
        name = a.get_text(" ", strip=True)
        if not name or name.lower() in SKIP_NAMES:
            continue
        seen.add(url)
        items.append(
            {
                "id": f"oakhouse_{m.group(2)}",
                "oakhouse_id": m.group(2),
                "kind": m.group(1),
                "name": name,
                "url": url,
            }
        )
    return items


def clean_address(s: str) -> str:
    s = re.sub(r"\s+", " ", s).strip()
    s = re.sub(r"^(현\s*주소|現住所|Address)\s*", "", s, flags=re.IGNORECASE)
    return s.strip(" ：:·|-")


def extract_from_detail(html: str, fallback_name: str) -> dict:
    soup = BeautifulSoup(html, "lxml")
    out: dict = {
        "name": fallback_name,
        "address": None,
        "lat": None,
        "lng": None,
    }

    # Name: title first segment is reliable; h1 is often empty on KR pages
    if soup.title:
        title = soup.title.get_text(" ", strip=True)
        parts = [p.strip() for p in title.split("|")]
        if parts and parts[0] and parts[0].lower() not in SKIP_NAMES:
            out["name"] = parts[0]

    # Address: <li><strong>현 주소</strong> ...</li>
    for strong in soup.find_all("strong"):
        label = strong.get_text(" ", strip=True)
        if not re.search(r"(현\s*주소|現住所|Address)", label, re.IGNORECASE):
            continue
        parent = strong.parent
        if not parent:
            continue
        addr = clean_address(parent.get_text(" ", strip=True))
        if len(addr) >= 4:
            out["address"] = addr
            break

    if not out["address"] and soup.title:
        parts = [p.strip() for p in soup.title.get_text(" ", strip=True).split("|")]
        if len(parts) >= 2 and re.search(r"(都|道|府|県|구|시|市|区|부)", parts[1]):
            out["address"] = clean_address(parts[1])

    m = COORDS_RE.search(html)
    if m:
        out["lat"] = float(m.group(1))
        out["lng"] = float(m.group(2))

    return out


def fetch_listings(
    *,
    limit: int | None,
    sleep_sec: float,
    out_path: Path,
    resume: bool,
) -> list[dict]:
    session = make_session()
    print(f"Fetching index: {INDEX_URL}")
    resp = session.get(INDEX_URL, timeout=90)
    resp.raise_for_status()
    listings = parse_index(resp.text)
    print(f"Index listings: {len(listings)}")

    by_url: dict[str, dict] = {}
    if resume and out_path.exists():
        try:
            prev = json.loads(out_path.read_text(encoding="utf-8"))
            if isinstance(prev, list):
                for row in prev:
                    if row.get("url") and row.get("address"):
                        by_url[row["url"]] = row
                print(f"Resume: loaded {len(by_url)} rows with address")
        except Exception as exc:
            print(f"Resume load failed ({exc}); starting fresh")

    work = listings[:limit] if limit is not None else listings
    rows: list[dict] = []

    for i, row in enumerate(work, 1):
        url = row["url"]
        existing = by_url.get(url)
        if existing and existing.get("address"):
            print(f"[{i}/{len(work)}] skip {existing.get('name', '')[:40]}")
            rows.append(existing)
            continue

        print(f"[{i}/{len(work)}] {row['name'][:50]}")
        try:
            detail = session.get(url, timeout=90)
            detail.raise_for_status()
            extracted = extract_from_detail(detail.text, row["name"])
            item = {
                **row,
                **extracted,
                "fetched_ok": bool(extracted.get("address")),
            }
        except Exception as exc:
            print(f"  ! {exc}")
            item = {
                **row,
                "address": None,
                "lat": None,
                "lng": None,
                "fetched_ok": False,
                "error": str(exc),
            }

        rows.append(item)
        by_url[url] = item

        if i % 25 == 0 or i == len(work):
            out_path.parent.mkdir(parents=True, exist_ok=True)
            out_path.write_text(
                json.dumps(rows, ensure_ascii=False, indent=2),
                encoding="utf-8",
            )
            ok = sum(1 for r in rows if r.get("address"))
            print(f"  checkpoint {ok}/{len(rows)} → {out_path}")

        time.sleep(sleep_sec)

    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(rows, ensure_ascii=False, indent=2), encoding="utf-8")
    ok = sum(1 for r in rows if r.get("address"))
    with_coords = sum(1 for r in rows if r.get("lat") is not None)
    print(f"Wrote {out_path} (address {ok}/{len(rows)}, coords {with_coords}/{len(rows)})")
    return rows


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--limit", type=int, default=None, help="Max listings (dry run)")
    parser.add_argument("--sleep", type=float, default=1.0, help="Delay between detail requests")
    parser.add_argument("--out", type=Path, default=DEFAULT_OUT)
    parser.add_argument("--resume", action="store_true", help="Reuse existing addresses in --out")
    args = parser.parse_args()

    fetch_listings(
        limit=args.limit,
        sleep_sec=args.sleep,
        out_path=args.out,
        resume=args.resume,
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())

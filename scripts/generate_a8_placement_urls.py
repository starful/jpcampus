#!/usr/bin/env python3
"""Build A8 広告掲載URL CSV files for Oakhouse and Cross One Room programs."""

from __future__ import annotations

import csv
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
STAYS_JSON = ROOT / "app" / "static" / "json" / "stays_data.json"
OUT_DIR = ROOT / "data" / "a8"
BASE = "https://jpcampus.net"

HOUSING_GUIDE_SLUGS = (
    "housing",
    "housing-seed",
    "apartment-initial-costs",
    "finding-apts-online",
    "tokyo-student-housing-operators",
    "rent-guarantor",
    "utilities-setup",
    "nha-subsidy-housing",
    "thrift-stores-furniture",
)


def _hub_urls() -> list[str]:
    rows = [
        f"{BASE}/",
        f"{BASE}/?lang=en",
        f"{BASE}/?lang=kr",
        f"{BASE}/stays",
        f"{BASE}/stays?lang=en",
        f"{BASE}/stays?lang=kr",
    ]
    return rows


def _stay_urls(stays: list[dict], *, operator_filter: str | None = None) -> list[str]:
    rows: list[str] = []
    for stay in stays:
        op = (stay.get("basic_info") or {}).get("operator", "")
        if operator_filter == "oakhouse":
            if "oakhouse" not in op.lower() and not stay.get("id", "").startswith("oakhouse_"):
                continue
        sid = stay["id"]
        rows.extend(
            [
                f"{BASE}/stay/{sid}",
                f"{BASE}/stay/{sid}?lang=en",
                f"{BASE}/stay/{sid}?lang=kr",
            ]
        )
    return rows


def _housing_guide_urls() -> list[str]:
    rows: list[str] = []
    for slug in HOUSING_GUIDE_SLUGS:
        rows.extend(
            [
                f"{BASE}/guide/{slug}",
                f"{BASE}/guide/{slug}?lang=en",
                f"{BASE}/guide/{slug}?lang=kr",
            ]
        )
    return rows


def _write_csv(path: Path, urls: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    unique = sorted(dict.fromkeys(urls))
    with path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["掲載URL"])
        for url in unique:
            writer.writerow([url])


def main() -> None:
    stays = json.loads(STAYS_JSON.read_text(encoding="utf-8")).get("stays", [])

    oak_urls = _hub_urls() + _stay_urls(stays, operator_filter="oakhouse")
    cross_urls = _hub_urls() + _stay_urls(stays) + _housing_guide_urls()

    oak_path = OUT_DIR / "a8-oakhouse-placement-urls.csv"
    cross_path = OUT_DIR / "a8-cross-oneroom-placement-urls.csv"
    _write_csv(oak_path, oak_urls)
    _write_csv(cross_path, cross_urls)

    print(f"Wrote {oak_path} ({len(set(oak_urls))} URLs)")
    print(f"Wrote {cross_path} ({len(set(cross_urls))} URLs)")


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""Build A8 広告掲載URL CSV files (program ID + URL, no header).

A8 CSV format (UTF-8):
  Column A = プログラムID
  Column B = 広告掲載URL
"""

from __future__ import annotations

import csv
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
STAYS_JSON = ROOT / "app" / "static" / "json" / "stays_data.json"
OUT_DIR = ROOT / "data" / "a8"
BASE = "https://jpcampus.net"

# From A8 program detail pages / banner mid prefixes
OAKHOUSE_PROGRAM_ID = "s00000018828001"
CROSS_ONEROOM_PROGRAM_ID = "s00000020603002"

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
    return [
        f"{BASE}/",
        f"{BASE}/?lang=en",
        f"{BASE}/?lang=kr",
        f"{BASE}/stays",
        f"{BASE}/stays?lang=en",
        f"{BASE}/stays?lang=kr",
    ]


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


def _write_csv(path: Path, program_id: str, urls: list[str]) -> None:
    """A8 expects Column A = program ID, Column B = URL (no header row)."""
    path.parent.mkdir(parents=True, exist_ok=True)
    unique = sorted(dict.fromkeys(urls))
    with path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.writer(f, lineterminator="\n")
        for url in unique:
            writer.writerow([program_id, url])


def main() -> None:
    stays = json.loads(STAYS_JSON.read_text(encoding="utf-8")).get("stays", [])

    # Pages where each banner actually appears
    oak_urls = (
        _hub_urls()
        + _stay_urls(stays, operator_filter="oakhouse")
        + _housing_guide_urls()
    )
    cross_urls = _hub_urls() + _stay_urls(stays) + _housing_guide_urls()

    oak_path = OUT_DIR / "a8-oakhouse-placement-urls.csv"
    cross_path = OUT_DIR / "a8-cross-oneroom-placement-urls.csv"
    _write_csv(oak_path, OAKHOUSE_PROGRAM_ID, oak_urls)
    _write_csv(cross_path, CROSS_ONEROOM_PROGRAM_ID, cross_urls)

    print(f"Wrote {oak_path} ({len(set(oak_urls))} rows, program={OAKHOUSE_PROGRAM_ID})")
    print(f"Wrote {cross_path} ({len(set(cross_urls))} rows, program={CROSS_ONEROOM_PROGRAM_ID})")


if __name__ == "__main__":
    main()

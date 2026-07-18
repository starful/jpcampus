#!/usr/bin/env python3
"""Stay catalog helpers: region tagging, published detection, sample selection."""

from __future__ import annotations

import json
import re
from collections import defaultdict
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
CONTENT_DIR = BASE_DIR / "app" / "content"
LISTINGS_PATH = DATA_DIR / "stay_listings.json"

REGION_RULES: list[tuple[str, re.Pattern[str]]] = [
    ("tokyo", re.compile(r"도쿄|東京|Tokyo", re.I)),
    ("kanagawa", re.compile(r"가나가와|카나가와|神奈川|Kanagawa|Yokohama|요코하마|Kawasaki|가와사키", re.I)),
    ("osaka", re.compile(r"오사카|大阪|Osaka", re.I)),
    ("kyoto", re.compile(r"교토|京都|Kyoto", re.I)),
    ("hyogo", re.compile(r"효고|兵庫|Hyogo|Kobe|고베|Amagasaki|아마가사키", re.I)),
    ("saitama", re.compile(r"사이타마|埼玉|Saitama", re.I)),
    ("chiba", re.compile(r"치바|千葉|Chiba", re.I)),
    ("aichi", re.compile(r"아이치|愛知|Aichi|Nagoya|나고야", re.I)),
    ("fukuoka", re.compile(r"후쿠오카|福岡|Fukuoka", re.I)),
]

KIND_TO_STAY_TYPE = {
    "house": "share_house",
    "share_house": "share_house",
    "apartment": "monthly_mansion",
    "monthly_mansion": "monthly_mansion",
    "guesthouse": "guesthouse",
    "dormitory": "guesthouse",
}


def detect_region(row: dict) -> str:
    blob = " ".join(
        str(row.get(k) or "")
        for k in ("address_kr", "address_en", "address_ja", "name_en", "name_kr")
    )
    for region, pat in REGION_RULES:
        if pat.search(blob):
            return region
    return "other"


def published_stay_ids() -> set[str]:
    ids: set[str] = set()
    if not CONTENT_DIR.exists():
        return ids
    for path in CONTENT_DIR.glob("stay_*.md"):
        name = path.name
        if name.endswith("_kr.md"):
            continue
        stem = name[len("stay_") : -len(".md")]
        ids.add(stem)
    return ids


def load_listings(*, enrich_region: bool = True) -> list[dict]:
    rows = json.loads(LISTINGS_PATH.read_text(encoding="utf-8"))
    published = published_stay_ids()
    out = []
    for row in rows:
        item = dict(row)
        if enrich_region or not item.get("region"):
            item["region"] = detect_region(item)
        item["published"] = item["id"] in published
        item["stay_type"] = KIND_TO_STAY_TYPE.get(
            str(item.get("kind") or "").lower(), "share_house"
        )
        out.append(item)
    return out


def save_listings(rows: list[dict]) -> None:
    # Persist catalog fields without ephemeral published flag noise? Keep region.
    clean = []
    for row in rows:
        item = {k: v for k, v in row.items() if k != "published"}
        if "region" not in item:
            item["region"] = detect_region(item)
        clean.append(item)
    LISTINGS_PATH.write_text(
        json.dumps(clean, ensure_ascii=False, indent=2), encoding="utf-8"
    )


def region_counts(rows: list[dict]) -> dict[str, int]:
    counts: dict[str, int] = defaultdict(int)
    for row in rows:
        counts[row.get("region") or "other"] += 1
    return dict(sorted(counts.items(), key=lambda x: (-x[1], x[0])))


def select_samples(
    rows: list[dict],
    *,
    per_region: int = 8,
    regions: list[str] | None = None,
    unpublished_only: bool = True,
) -> list[dict]:
    """Pick up to per_region stays per region, mixing operators when possible."""
    filtered = rows
    if unpublished_only:
        filtered = [r for r in filtered if not r.get("published")]
    if regions:
        allow = set(regions)
        filtered = [r for r in filtered if r.get("region") in allow]

    by_region: dict[str, list[dict]] = defaultdict(list)
    for row in filtered:
        if row.get("lat") is None or row.get("lng") is None:
            continue
        by_region[row.get("region") or "other"].append(row)

    selected: list[dict] = []
    for region, items in sorted(by_region.items()):
        # Prefer operator diversity: round-robin Oakhouse / Sakura / others
        buckets: dict[str, list[dict]] = defaultdict(list)
        for item in items:
            buckets[item.get("operator") or "Other"].append(item)
        for bucket in buckets.values():
            bucket.sort(key=lambda r: (r.get("name_en") or r.get("id") or ""))

        picked: list[dict] = []
        ops = sorted(buckets.keys())
        idx = {op: 0 for op in ops}
        while len(picked) < per_region and any(idx[op] < len(buckets[op]) for op in ops):
            for op in ops:
                if len(picked) >= per_region:
                    break
                i = idx[op]
                if i < len(buckets[op]):
                    picked.append(buckets[op][i])
                    idx[op] = i + 1
        selected.extend(picked)
    return selected


def catalog_to_seed_row(row: dict) -> dict:
    """Map catalog row to generate_stay_content seed shape."""
    stay_id = row["id"]
    name_en = row.get("name_en") or row.get("name_kr") or stay_id
    name_kr = row.get("name_kr") or name_en
    address = row.get("address_en") or row.get("address_kr") or row.get("address_ja") or ""
    address_kr = row.get("address_kr") or address
    return {
        "id": stay_id,
        "name_en": name_en,
        "name_ja": name_kr,  # display fallback; JP Campus meta uses name_ja
        "name_kr": name_kr,
        "stay_type": row.get("stay_type") or KIND_TO_STAY_TYPE.get(row.get("kind", ""), "share_house"),
        "operator": row.get("operator") or "Unknown",
        "address": address,
        "address_kr": address_kr,
        "lat": row["lat"],
        "lng": row["lng"],
        "booking_url": row.get("url_en") or row.get("url_kr") or "",
        "url_en": row.get("url_en") or "",
        "url_kr": row.get("url_kr") or "",
        "region": row.get("region") or detect_region(row),
        "min_rent": row.get("min_rent"),
        "max_rent": row.get("max_rent"),
    }

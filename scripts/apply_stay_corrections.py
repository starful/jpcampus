#!/usr/bin/env python3
"""Apply stay_property_corrections + Google Geocoding to tokyo_stays_seed.py."""

from __future__ import annotations

import os
import re
import sys
import time
from pathlib import Path

import requests
from dotenv import load_dotenv

SCRIPT_DIR = Path(__file__).resolve().parent
ROOT = SCRIPT_DIR.parent
sys.path.insert(0, str(ROOT / "data"))

from stay_property_corrections import STAY_PROPERTY_CORRECTIONS  # noqa: E402
from tokyo_stays_seed import TOKYO_STAYS  # noqa: E402

load_dotenv(ROOT / ".env")
API_KEY = os.getenv("GOOGLE_MAPS_API_KEY")
SEED_PATH = ROOT / "data" / "tokyo_stays_seed.py"


def geocode_nominatim(address: str) -> tuple[float, float] | None:
    if not address:
        return None
    try:
        res = requests.get(
            "https://nominatim.openstreetmap.org/search",
            params={"q": address, "format": "json", "limit": 1, "countrycodes": "jp"},
            headers={"User-Agent": "jpcampus-stay-geocode/1.0 (contact: jpcampus)"},
            timeout=20,
        )
        res.raise_for_status()
        results = res.json() or []
        if not results:
            return None
        return round(float(results[0]["lat"]), 6), round(float(results[0]["lon"]), 6)
    except Exception as exc:
        print(f"  geocode error: {exc}")
        return None


def geocode_google(address: str) -> tuple[float, float] | None:
    if not API_KEY or not address:
        return None
    try:
        res = requests.get(
            "https://maps.googleapis.com/maps/api/geocode/json",
            params={"address": address, "key": API_KEY, "language": "en", "region": "jp"},
            timeout=15,
        )
        res.raise_for_status()
        data = res.json()
        if data.get("status") != "OK":
            return None
        results = data.get("results") or []
        if not results:
            return None
        loc = results[0].get("geometry", {}).get("location", {})
        lat, lng = loc.get("lat"), loc.get("lng")
        if lat is None or lng is None:
            return None
        return round(float(lat), 6), round(float(lng), 6)
    except Exception:
        return None


def geocode(address: str) -> tuple[float, float] | None:
    coords = geocode_google(address)
    if coords:
        return coords
    return geocode_nominatim(address)


def apply_corrections(*, geocode_coords: bool = True) -> list[dict]:
    updated: list[dict] = []
    for stay in TOKYO_STAYS:
        row = dict(stay)
        patch = STAY_PROPERTY_CORRECTIONS.get(row["id"], {})
        for key in ("name_en", "name_ja", "address", "booking_url"):
            if key in patch:
                row[key] = patch[key]
        if "lat" in patch and "lng" in patch:
            row["lat"], row["lng"] = patch["lat"], patch["lng"]
        elif geocode_coords:
            query = patch.get("geocode_address") or patch.get("address") or row.get("address")
            if query:
                coords = geocode(query)
                if coords:
                    row["lat"], row["lng"] = coords
                    print(f"  ✓ {row['id']}: {coords[0]}, {coords[1]} ← {query[:60]}")
                else:
                    print(f"  ⚠ {row['id']}: geocode failed ({query[:50]})")
                time.sleep(1.1)
        updated.append(row)
    return updated


def _format_stay(stay: dict) -> str:
    lines = [
        "    {",
        f'        "id": "{stay["id"]}",',
        f'        "name_en": "{stay["name_en"]}",',
        f'        "name_ja": "{stay["name_ja"]}",',
        f'        "stay_type": "{stay["stay_type"]}",',
        f'        "operator": "{stay["operator"]}",',
        f'        "address": "{stay["address"]}",',
        f'        "lat": {stay["lat"]},',
        f'        "lng": {stay["lng"]},',
        f'        "min_rent": {stay["min_rent"]},',
        f'        "max_rent": {stay["max_rent"]},',
        f'        "booking_url": "{stay["booking_url"]}",',
        "    }",
    ]
    return "\n".join(lines)


def write_seed(stays: list[dict]) -> None:
    body = ",\n".join(_format_stay(s) for s in stays)
    content = f'''"""Seed data: 30 Tokyo guesthouses / share houses / monthly mansions for MVP map."""

TOKYO_STAYS = [
{body}
]
'''
    SEED_PATH.write_text(content, encoding="utf-8")
    print(f"\n✅ Wrote {len(stays)} stays → {SEED_PATH}")


def main() -> None:
    import argparse

    parser = argparse.ArgumentParser(description="Apply stay URL/address/coordinate corrections")
    parser.add_argument("--no-geocode", action="store_true", help="Skip Google Geocoding API")
    args = parser.parse_args()

    if not API_KEY and not args.no_geocode:
        print("ℹ Google key unavailable for server geocode — using Nominatim (OSM)")

    print(f"Applying corrections to {len(TOKYO_STAYS)} stays…\n")
    stays = apply_corrections(geocode_coords=not args.no_geocode)
    write_seed(stays)


if __name__ == "__main__":
    main()

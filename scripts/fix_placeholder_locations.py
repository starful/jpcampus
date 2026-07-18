#!/usr/bin/env python3
"""Geocode universities stuck on the Tokyo placeholder (35.6812, 139.7671).

Uses Nominatim (OSM) — browser-restricted Google Maps keys cannot call Geocoding API.
Updates EN + KR markdown frontmatter.
"""

from __future__ import annotations

import json
import os
import re
import sys
import time
from pathlib import Path

import frontmatter
import requests
from dotenv import load_dotenv

SCRIPT_DIR = Path(__file__).resolve().parent
ROOT = SCRIPT_DIR.parent
CONTENT_DIR = ROOT / "app" / "content"
sys.path.insert(0, str(SCRIPT_DIR))
from md_dates import save_post  # noqa: E402

load_dotenv(ROOT / ".env")

TOKYO_DEFAULT = (35.6812, 139.7671)
CACHE_PATH = ROOT / "data" / "geocode_cache.json"
UA = {"User-Agent": "jpcampus-univ-geocode/1.0 (contact: jpcampus; educational)"}

# Rough city / prefecture centroids when OSM has no campus node
CITY_CENTROIDS: list[tuple[tuple[str, ...], float, float]] = [
    (("東京都", "Tokyo", "도쿄", "동경"), 35.6812, 139.7671),
    (("大阪府", "大阪市", "Osaka", "오사카"), 34.6937, 135.5023),
    (("京都府", "京都市", "Kyoto", "교토"), 35.0116, 135.7681),
    (("愛知県", "名古屋", "Nagoya", "나고야", "日進", "Nisshin", "豊田", "Toyota"), 35.1815, 136.9066),
    (("福岡", "Fukuoka", "후쿠오카"), 33.5904, 130.4017),
    (("北海道", "札幌", "Sapporo", "홋카이도", "삿포로"), 43.0618, 141.3545),
    (("宮城", "仙台", "Sendai", "센다이"), 38.2682, 140.8694),
    (("神奈川", "横浜", "Yokohama", "요코하마", "川崎"), 35.4437, 139.6380),
    (("兵庫", "神戸", "Kobe", "고베", "姫路", "Himeji"), 34.6901, 135.1955),
    (("広島", "Hiroshima", "히로시마"), 34.3853, 132.4553),
    (("岡山", "Okayama"), 34.6551, 133.9195),
    (("静岡", "浜松", "Hamamatsu", "Shizuoka"), 34.9756, 138.3828),
    (("岐阜", "Gifu"), 35.3912, 136.7223),
    (("三重", "Mie"), 34.7303, 136.5086),
    (("滋賀", "Shiga", "大津"), 35.0045, 135.8686),
    (("奈良", "Nara"), 34.6851, 135.8048),
    (("和歌山", "Wakayama"), 34.2260, 135.1675),
    (("群馬", "Gunma", "前橋", "Maebashi"), 36.3912, 139.0608),
    (("栃木", "Tochigi", "宇都宮", "Utsunomiya"), 36.5551, 139.8828),
    (("茨城", "Ibaraki", "水戸", "Mito"), 36.3418, 140.4468),
    (("千葉", "Chiba"), 35.6074, 140.1065),
    (("埼玉", "Saitama"), 35.8617, 139.6455),
    (("新潟", "Niigata"), 37.9026, 139.0236),
    (("長野", "Nagano"), 36.6513, 138.1810),
    (("富山", "Toyama"), 36.6953, 137.2113),
    (("石川", "金沢", "Kanazawa", "Ishikawa"), 36.5947, 136.6256),
    (("福井", "Fukui"), 36.0652, 136.2216),
    (("山梨", "Yamanashi", "甲府"), 35.6642, 138.5684),
    (("青森", "Aomori", "弘前", "Hirosaki"), 40.8244, 140.7400),
    (("岩手", "Iwate", "盛岡", "Morioka"), 39.7036, 141.1527),
    (("秋田", "Akita"), 39.7186, 140.1024),
    (("山形", "Yamagata"), 38.2404, 140.3633),
    (("福島", "Fukushima"), 37.7500, 140.4678),
    (("徳島", "Tokushima"), 34.0658, 134.5593),
    (("香川", "高松", "Takamatsu", "Kagawa"), 34.3401, 134.0434),
    (("愛媛", "松山", "Matsuyama", "Ehime"), 33.8416, 132.7657),
    (("高知", "Kochi", "Kōchi"), 33.5597, 133.5311),
    (("山口", "Yamaguchi"), 34.1860, 131.4706),
    (("長崎", "Nagasaki"), 32.7503, 129.8777),
    (("熊本", "Kumamoto"), 32.8031, 130.7079),
    (("大分", "Oita", "Ōita"), 33.2382, 131.6126),
    (("宮崎", "Miyazaki"), 31.9077, 131.4202),
    (("鹿児島", "Kagoshima"), 31.5966, 130.5571),
    (("沖縄", "Okinawa", "那覇", "Naha"), 26.2124, 127.6809),
]


def is_tokyo_default(loc: dict | None) -> bool:
    if not loc:
        return False
    try:
        lat = float(loc.get("lat"))
        lng = float(loc.get("lng"))
    except (TypeError, ValueError):
        return False
    return abs(lat - TOKYO_DEFAULT[0]) < 1e-6 and abs(lng - TOKYO_DEFAULT[1]) < 1e-6


def in_japan(lat: float, lng: float) -> bool:
    return 24.0 <= lat <= 46.5 and 122.0 <= lng <= 146.5


def is_still_tokyo_center(lat: float, lng: float) -> bool:
    return abs(lat - TOKYO_DEFAULT[0]) < 0.02 and abs(lng - TOKYO_DEFAULT[1]) < 0.02


def address_implies_tokyo(text: str) -> bool:
    return any(x in text for x in ("東京都", "Tokyo", "도쿄", "동경"))


def geocode_nominatim(query: str) -> tuple[float, float] | None:
    if not query:
        return None
    try:
        res = requests.get(
            "https://nominatim.openstreetmap.org/search",
            params={"q": query, "format": "json", "limit": 1, "countrycodes": "jp"},
            headers=UA,
            timeout=25,
        )
        res.raise_for_status()
        results = res.json() or []
        if not results:
            return None
        return round(float(results[0]["lat"]), 6), round(float(results[0]["lon"]), 6)
    except Exception as exc:
        print(f"  nominatim error: {exc}", flush=True)
        return None


def city_fallback(text: str) -> tuple[float, float, str] | None:
    blob = text or ""
    for keys, lat, lng in CITY_CENTROIDS:
        if any(k in blob for k in keys):
            # slight jitter avoided — exact centroid is fine for map zoom
            if keys[0] in ("東京都", "Tokyo", "도쿄", "동경"):
                return lat, lng, "tokyo-city"
            return lat, lng, f"city:{keys[0]}"
    return None


def accept(
    coords: tuple[float, float] | None,
    *,
    context: str,
) -> tuple[float, float] | None:
    if not coords:
        return None
    lat, lng = coords
    if not in_japan(lat, lng):
        return None
    if is_still_tokyo_center(lat, lng) and not address_implies_tokyo(context):
        return None
    return coords


def geocode(address: str, name_ja: str, name_en: str) -> tuple[float, float, str] | None:
    context = " ".join(x for x in (address, name_ja, name_en) if x)
    queries: list[str] = []
    if name_ja:
        queries.append(name_ja)
        if "大学" not in name_ja and "短大" not in name_ja:
            queries.append(f"{name_ja}大学")
    if name_en:
        queries.append(name_en)
    if address:
        # Prefer Japanese-ish chunks / shorter address
        queries.append(address)
        # Drop postal-ish leading zip
        cleaned = re.sub(r"^〒?\d{3}-?\d{4}\s*", "", address)
        if cleaned != address:
            queries.append(cleaned)

    seen: set[str] = set()
    for q in queries:
        q = (q or "").strip()
        if not q or q in seen:
            continue
        seen.add(q)
        time.sleep(1.05)
        hit = accept(geocode_nominatim(q), context=context)
        if hit:
            return hit[0], hit[1], f"nominatim:{q[:40]}"

    fb = city_fallback(context)
    if fb:
        lat, lng, src = fb
        if is_still_tokyo_center(lat, lng) and not address_implies_tokyo(context):
            return None
        return lat, lng, src
    return None


def load_cache() -> dict:
    if CACHE_PATH.exists():
        return json.loads(CACHE_PATH.read_text(encoding="utf-8"))
    return {}


def save_cache(cache: dict) -> None:
    CACHE_PATH.parent.mkdir(parents=True, exist_ok=True)
    CACHE_PATH.write_text(json.dumps(cache, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def kr_path_for_en(en_path: Path) -> Path:
    return en_path.with_name(en_path.stem + "_kr.md")


def update_location(path: Path, lat: float, lng: float) -> bool:
    if not path.exists():
        return False
    post = frontmatter.load(path)
    post.metadata["location"] = {"lat": lat, "lng": lng}
    save_post(str(path), post)
    return True


def main() -> int:
    cache = load_cache()
    targets: list[tuple[str, Path, dict]] = []
    for path in sorted(CONTENT_DIR.glob("*.md")):
        if path.name.endswith("_kr.md"):
            continue
        if not path.name.startswith("univ_"):
            continue
        try:
            post = frontmatter.load(path)
        except Exception:
            continue
        meta = post.metadata
        if not is_tokyo_default(meta.get("location")):
            continue
        sid = str(meta.get("id") or path.stem)
        targets.append((sid, path, meta))

    print(f"Found {len(targets)} universities with Tokyo placeholder", flush=True)

    ok = fail = 0
    for i, (sid, path, meta) in enumerate(targets, 1):
        bi = meta.get("basic_info") or {}
        address = (bi.get("address") or "").strip()
        name_ja = (bi.get("name_ja") or "").strip()
        name_en = (bi.get("name_en") or bi.get("name_display") or "").strip()
        print(f"[{i}/{len(targets)}] {sid}", flush=True)

        lat = lng = None
        source = ""
        cached = cache.get(sid) or {}
        if cached.get("lat") is not None and cached.get("lng") is not None:
            clat, clng = float(cached["lat"]), float(cached["lng"])
            if accept((clat, clng), context=address or name_en or name_ja):
                lat, lng = clat, clng
                source = cached.get("source") or "cache"
                print(f"  cache → {lat}, {lng}", flush=True)

        if lat is None:
            result = geocode(address, name_ja, name_en)
            if not result:
                print(f"  ✗ failed ({name_ja or name_en or address[:50]})", flush=True)
                fail += 1
                continue
            lat, lng, source = result
            cache[sid] = {
                "lat": lat,
                "lng": lng,
                "address": address,
                "name_en": name_en,
                "name_ja": name_ja,
                "source": source,
            }
            if i % 10 == 0:
                save_cache(cache)
            print(f"  ✓ {lat}, {lng} ({source})", flush=True)

        update_location(path, lat, lng)
        update_location(kr_path_for_en(path), lat, lng)
        ok += 1

    save_cache(cache)
    print(f"\nDone: updated={ok} failed={fail}", flush=True)
    return 0 if fail == 0 else 0  # still rebuild even with a few failures


if __name__ == "__main__":
    raise SystemExit(main())

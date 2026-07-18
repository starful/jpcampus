#!/usr/bin/env python3
"""Build bilingual stay listings JSON (Oakhouse + Sakura House).

Schema per row:
  id, operator, kind, name_en, name_kr, address_en, address_kr,
  url_en, url_kr, lat, lng, source_id

Usage:
  python scripts/build_stay_listings.py --sakura-only
  python scripts/build_stay_listings.py --oakhouse-en --sleep 0.7
  python scripts/build_stay_listings.py   # sakura + migrate oakhouse (reuse EN cache)
"""

from __future__ import annotations

import argparse
import json
import re
import sys
import time
from pathlib import Path

import requests
from bs4 import BeautifulSoup

SCRIPT_DIR = Path(__file__).resolve().parent
BASE_DIR = SCRIPT_DIR.parent
DATA_DIR = BASE_DIR / "data"

OAKHOUSE_RAW = DATA_DIR / "oakhouse_listings.json"
SAKURA_RAW = DATA_DIR / "sakura_listings.json"
OUT_PATH = DATA_DIR / "stay_listings.json"
OAKHOUSE_EN_CACHE = DATA_DIR / "oakhouse_en_cache.json"

UA = "jpcampus-research/1.0 (+https://jpcampus.net; lodging catalog research)"
SAKURA_GQL = "https://sakurahouse-production.an.r.appspot.com/graphql"

# Japanese address fragments → Korean (common wards/prefs for stays)
JA_TO_KR = {
    "東京都": "도쿄도",
    "大阪府": "오사카부",
    "京都府": "교토부",
    "神奈川県": "가나가와현",
    "埼玉県": "사이타마현",
    "千葉県": "치바현",
    "兵庫県": "효고현",
    "愛知県": "아이치현",
    "福岡県": "후쿠오카현",
    "静岡県": "시즈오카현",
    "北海道": "홋카이도",
    "渋谷区": "시부야구",
    "新宿区": "신주쿠구",
    "豊島区": "도시마구",
    "港区": "미나토구",
    "目黒区": "메구로구",
    "世田谷区": "세타가야구",
    "中野区": "나카노구",
    "杉並区": "스기나미구",
    "練馬区": "네리마구",
    "板橋区": "이타바시구",
    "北区": "키타구",
    "台東区": "다이토구",
    "文京区": "분쿄구",
    "中央区": "주오구",
    "千代田区": "치요다구",
    "墨田区": "스미다구",
    "江東区": "고토구",
    "江戸川区": "에도가와구",
    "葛飾区": "가쓰시카구",
    "足立区": "아다치구",
    "荒川区": "아라카와구",
    "品川区": "시나가와구",
    "大田区": "오타구",
    "横浜市": "요코하마시",
    "川崎市": "가와사키시",
    "大阪市": "오사카시",
    "京都市": "교토시",
    "神戸市": "고베시",
    "名古屋市": "나고야시",
    "福岡市": "후쿠오카시",
}


def session() -> requests.Session:
    s = requests.Session()
    s.headers.update(
        {
            "User-Agent": UA,
            "Accept": "application/json,text/html",
            "Accept-Language": "en,ko;q=0.8,ja;q=0.7",
        }
    )
    return s


def ja_address_to_kr(address_ja: str) -> str:
    if not address_ja:
        return ""
    out = address_ja
    # Strip postal mark
    out = re.sub(r"〒\d{3}-?\d{4}\s*", "", out)
    # Longer keys first
    for ja, kr in sorted(JA_TO_KR.items(), key=lambda x: -len(x[0])):
        out = out.replace(ja, kr)
    out = re.sub(r"\s+", " ", out).strip()
    return out


def sakura_name_kr(display_name: str, name: str) -> str:
    base = display_name or name or ""
    base = re.sub(r"^SAKURA\s+HOUSE\s+", "", base, flags=re.I).strip()
    base = re.sub(r"^SAKURA\s+", "", base, flags=re.I).strip()
    return f"사쿠라 하우스 {base}" if base else "사쿠라 하우스"


def fetch_sakura(s: requests.Session) -> list[dict]:
    query = """
    query buildingGroups($groupType: BuildingGroupType!, $param: BuildingsSearchParam) {
      buildingGroups(groupType: $groupType, param: $param) {
        buildings {
          id
          name
          displayName
          address
          addressEN
          siteKey
          lat
          lng
          roomTypes
        }
      }
    }
    """
    r = s.post(
        SAKURA_GQL,
        json={"query": query, "variables": {"groupType": "Alphabet", "param": {}}},
        timeout=90,
    )
    r.raise_for_status()
    payload = r.json()
    if payload.get("errors"):
        raise RuntimeError(payload["errors"])

    by_id: dict[str, dict] = {}
    for group in payload["data"]["buildingGroups"]:
        for b in group["buildings"]:
            by_id[str(b["id"])] = b

    rows = []
    for b in by_id.values():
        site_key = b.get("siteKey") or str(b["id"])
        name_en = (b.get("displayName") or b.get("name") or "").strip()
        address_ja = (b.get("address") or "").strip()
        address_en = (b.get("addressEN") or "").strip()
        kind = "share_house"
        types = b.get("roomTypes") or []
        if isinstance(types, list) and types:
            t0 = str(types[0]).lower()
            if "apartment" in t0:
                kind = "apartment"
            elif "dorm" in t0:
                kind = "dormitory"
            elif "guest" in t0:
                kind = "guesthouse"

        rows.append(
            {
                "id": f"sakura_{site_key}".replace("-", "_"),
                "operator": "Sakura House",
                "kind": kind,
                "name_en": name_en,
                "name_kr": sakura_name_kr(name_en, b.get("name") or ""),
                "address_en": address_en,
                "address_kr": ja_address_to_kr(address_ja),
                "address_ja": address_ja,
                "url_en": f"https://www.sakura-house.com/building/{site_key}",
                "url_kr": f"https://www.sakura-house.com/kr/building/{site_key}",
                "lat": b.get("lat"),
                "lng": b.get("lng"),
                "source_id": str(b["id"]),
                "site_key": site_key,
            }
        )

    rows.sort(key=lambda x: x["name_en"].lower())
    SAKURA_RAW.write_text(json.dumps(rows, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Sakura: {len(rows)} buildings → {SAKURA_RAW}")
    return rows


def extract_oakhouse_en(html: str) -> tuple[str | None, str | None]:
    soup = BeautifulSoup(html, "lxml")
    name = None
    if soup.title:
        parts = [p.strip() for p in soup.title.get_text(" ", strip=True).split("|")]
        if parts and parts[0]:
            name = parts[0]

    address = None
    for strong in soup.find_all("strong"):
        label = strong.get_text(" ", strip=True)
        if re.search(r"^(Address|現住所)$", label, re.I):
            address = strong.parent.get_text(" ", strip=True) if strong.parent else None
            if address:
                address = re.sub(r"^(Address|現住所)\s*", "", address, flags=re.I)
                address = re.sub(r"\s*-\s*(to|ku|shi|ken|fu)\b", r" \1", address, flags=re.I)
                address = re.sub(r"\s+", " ", address).strip()
            break

    if not address and soup.title:
        parts = [p.strip() for p in soup.title.get_text(" ", strip=True).split("|")]
        if len(parts) >= 2 and re.search(r"(Tokyo|Osaka|Kyoto|Kanagawa|Pref)", parts[1], re.I):
            address = parts[1]
    return name, address


def kr_url_to_en(url: str) -> str:
    return url.replace("/kr/", "/eng/")


def load_en_cache() -> dict[str, dict]:
    if not OAKHOUSE_EN_CACHE.exists():
        return {}
    try:
        data = json.loads(OAKHOUSE_EN_CACHE.read_text(encoding="utf-8"))
        return {row["url_en"]: row for row in data if row.get("url_en")}
    except Exception:
        return {}


def save_en_cache(cache: dict[str, dict]) -> None:
    rows = list(cache.values())
    OAKHOUSE_EN_CACHE.write_text(
        json.dumps(rows, ensure_ascii=False, indent=2), encoding="utf-8"
    )


def migrate_oakhouse(
    s: requests.Session,
    *,
    fetch_en: bool,
    sleep_sec: float,
    limit: int | None,
) -> list[dict]:
    raw = json.loads(OAKHOUSE_RAW.read_text(encoding="utf-8"))
    if limit is not None:
        raw = raw[:limit]

    cache = load_en_cache()
    rows: list[dict] = []

    for i, item in enumerate(raw, 1):
        url_kr = item.get("url") or ""
        url_en = kr_url_to_en(url_kr)
        name_kr = item.get("name") or ""
        address_kr = item.get("address") or ""

        name_en = None
        address_en = None
        cached = cache.get(url_en)
        if cached:
            name_en = cached.get("name_en")
            address_en = cached.get("address_en")

        if fetch_en and (not name_en or not address_en):
            print(f"[oakhouse en {i}/{len(raw)}] {name_kr[:40]}")
            try:
                resp = s.get(url_en, timeout=90)
                if resp.status_code == 404:
                    print("  ! 404")
                else:
                    resp.raise_for_status()
                    name_en, address_en = extract_oakhouse_en(resp.text)
                    cache[url_en] = {
                        "url_en": url_en,
                        "name_en": name_en,
                        "address_en": address_en,
                    }
                    if i % 25 == 0:
                        save_en_cache(cache)
            except Exception as exc:
                print(f"  ! {exc}")
            time.sleep(sleep_sec)

        rows.append(
            {
                "id": item.get("id") or f"oakhouse_{item.get('oakhouse_id')}",
                "operator": "Oakhouse",
                "kind": item.get("kind") or "house",
                "name_en": name_en or name_kr,
                "name_kr": name_kr,
                "address_en": address_en or address_kr,
                "address_kr": address_kr,
                "url_en": url_en,
                "url_kr": url_kr,
                "lat": item.get("lat"),
                "lng": item.get("lng"),
                "source_id": str(item.get("oakhouse_id") or ""),
                "fetched_ok": bool(address_kr),
            }
        )

    if fetch_en:
        save_en_cache(cache)
    print(f"Oakhouse: {len(rows)} rows")
    return rows


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--sakura-only", action="store_true")
    parser.add_argument(
        "--oakhouse-en",
        action="store_true",
        help="Fetch Oakhouse English name/address (slow)",
    )
    parser.add_argument("--sleep", type=float, default=0.7)
    parser.add_argument("--limit", type=int, default=None, help="Limit oakhouse EN fetch")
    parser.add_argument("--out", type=Path, default=OUT_PATH)
    args = parser.parse_args()

    s = session()
    sakura = fetch_sakura(s)

    if args.sakura_only:
        args.out.write_text(json.dumps(sakura, ensure_ascii=False, indent=2), encoding="utf-8")
        print(f"Wrote {args.out}")
        return 0

    if not OAKHOUSE_RAW.exists():
        print(f"Missing {OAKHOUSE_RAW}", file=sys.stderr)
        return 1

    oakhouse = migrate_oakhouse(
        s,
        fetch_en=args.oakhouse_en,
        sleep_sec=args.sleep,
        limit=args.limit,
    )

    merged = oakhouse + sakura
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(merged, ensure_ascii=False, indent=2), encoding="utf-8")

    print(
        f"Wrote {args.out} "
        f"(oakhouse={len(oakhouse)}, sakura={len(sakura)}, total={len(merged)})"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())

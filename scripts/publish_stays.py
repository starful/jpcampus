#!/usr/bin/env python3
"""Selectively publish stay pages from data/stay_listings.json.

Examples:
  python scripts/publish_stays.py --sample --per-region 8 --build
  python scripts/publish_stays.py --ids oakhouse_384,sakura_asakusa_kuramae --build
  python scripts/publish_stays.py --region tokyo --limit 10 --build
  python scripts/publish_stays.py --list-regions
  python scripts/publish_stays.py --list-unpublished --region osaka
  python scripts/publish_stays.py --republish-published --force --build
"""

from __future__ import annotations

import argparse
import json
import math
import os
import re
import subprocess
import sys
from datetime import date
from functools import lru_cache
from pathlib import Path

import frontmatter

SCRIPT_DIR = Path(__file__).resolve().parent
BASE_DIR = SCRIPT_DIR.parent
sys.path.insert(0, str(SCRIPT_DIR))

from common import CONTENT_DIR  # noqa: E402
from stay_catalog import (  # noqa: E402
    LISTINGS_PATH,
    catalog_to_seed_row,
    load_listings,
    region_counts,
    save_listings,
    select_samples,
)

THUMB = "/static/images/stay_{id}.jpg"
SCHOOLS_JSON = BASE_DIR / "app" / "static" / "json" / "schools_data.json"

STAY_TYPE_LABEL = {
    "guesthouse": ("Guesthouse", "ゲストハウス"),
    "share_house": ("Share House", "シェアハウス"),
    "monthly_mansion": ("Monthly Mansion", "マンスリーマンション"),
}
STAY_TYPE_LABEL_KR = {
    "guesthouse": "게스트하우스",
    "share_house": "셰어하우스",
    "monthly_mansion": "먼슬리맨션",
}
REGION_LABEL_EN = {
    "tokyo": "Tokyo",
    "kanagawa": "Kanagawa",
    "osaka": "Osaka",
    "kyoto": "Kyoto",
    "hyogo": "Hyogo",
    "saitama": "Saitama",
    "chiba": "Chiba",
    "aichi": "Aichi",
    "fukuoka": "Fukuoka",
    "other": "Japan",
    "japan": "Japan",
}
REGION_LABEL_KR = {
    "tokyo": "도쿄",
    "kanagawa": "가나가와",
    "osaka": "오사카",
    "kyoto": "교토",
    "hyogo": "효고",
    "saitama": "사이타마",
    "chiba": "치바",
    "aichi": "아이치",
    "fukuoka": "후쿠오카",
    "other": "일본",
    "japan": "일본",
}


def _haversine_km(lat1: float, lng1: float, lat2: float, lng2: float) -> float:
    r = 6371.0
    p1, p2 = math.radians(lat1), math.radians(lat2)
    dlat = math.radians(lat2 - lat1)
    dlng = math.radians(lng2 - lng1)
    a = math.sin(dlat / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(dlng / 2) ** 2
    return 2 * r * math.asin(math.sqrt(a))


@lru_cache(maxsize=1)
def _load_schools() -> list[dict]:
    if not SCHOOLS_JSON.exists():
        return []
    data = json.loads(SCHOOLS_JSON.read_text(encoding="utf-8"))
    if isinstance(data, dict):
        return data.get("schools") or []
    return data if isinstance(data, list) else []


def nearby_schools(lat: float, lng: float, *, limit: int = 5, radius_km: float = 5.0) -> list[dict]:
    scored: list[tuple[float, dict]] = []
    for school in _load_schools():
        loc = school.get("location") or {}
        slat, slng = loc.get("lat"), loc.get("lng")
        if slat is None or slng is None:
            continue
        dist = _haversine_km(float(lat), float(lng), float(slat), float(slng))
        if dist > radius_km:
            continue
        basic = school.get("basic_info") or {}
        name = basic.get("name_en") or basic.get("name_ja") or school.get("id")
        scored.append(
            (
                dist,
                {
                    "id": school.get("id"),
                    "name": name,
                    "category": school.get("category") or "school",
                    "distance_km": round(dist, 1),
                    "link": f"/school/{school.get('id')}",
                },
            )
        )
    scored.sort(key=lambda x: x[0])
    if scored:
        return [s for _, s in scored[:limit]]

    # Nearest anywhere if nothing in radius
    scored = []
    for school in _load_schools():
        loc = school.get("location") or {}
        slat, slng = loc.get("lat"), loc.get("lng")
        if slat is None or slng is None:
            continue
        dist = _haversine_km(float(lat), float(lng), float(slat), float(slng))
        basic = school.get("basic_info") or {}
        name = basic.get("name_en") or basic.get("name_ja") or school.get("id")
        scored.append(
            (
                dist,
                {
                    "id": school.get("id"),
                    "name": name,
                    "category": school.get("category") or "school",
                    "distance_km": round(dist, 1),
                    "link": f"/school/{school.get('id')}",
                },
            )
        )
    scored.sort(key=lambda x: x[0])
    return [s for _, s in scored[:limit]]


def _area_from_address(address: str) -> str | None:
    if not address:
        return None
    # English: "Shinjuku-ku", "Shibuya City", "Osaka City"
    m = re.search(
        r"\b([A-Z][A-Za-z\-]+(?:\s+[A-Z][A-Za-z\-]+)?)\s*(?:-ku|Ku|Ward|City)\b",
        address,
    )
    if m:
        return m.group(1).replace("-", " ").strip()
    # Japanese wards / cities
    m = re.search(r"([^\s、,]+[市区町村])", address)
    if m:
        return m.group(1)
    # Korean: "신주쿠구", "시부야구"
    m = re.search(r"([가-힣]+[구시군])", address)
    if m:
        return m.group(1)
    return None


def _region_label(region: str, lang: str) -> str:
    key = (region or "japan").lower()
    if lang == "kr":
        return REGION_LABEL_KR.get(key, key)
    return REGION_LABEL_EN.get(key, key.replace("_", " ").title())


def _rent_line_en(stay: dict) -> str:
    lo, hi = stay.get("min_rent"), stay.get("max_rent")
    if lo and hi:
        return (
            f"Monthly rent typically ranges from **¥{lo:,}** to **¥{hi:,}** "
            "(utilities may be extra). Prices change by season and room type — "
            "confirm on the operator site before booking."
        )
    return (
        "Monthly rent depends on room type and season. "
        "Check current prices on the operator website before booking."
    )


def _rent_line_kr(stay: dict) -> str:
    lo, hi = stay.get("min_rent"), stay.get("max_rent")
    if lo and hi:
        return (
            f"월 **¥{lo:,} ~ ¥{hi:,}** 수준 (관리비 별도 가능). "
            "시즌·방 타입에 따라 변동하니 예약 전 반드시 확인하세요."
        )
    return "월세는 방 타입·시즌에 따라 다릅니다. 예약 전 운영사 사이트에서 최신 요금을 확인하세요."


def _nearby_section_en(schools: list[dict]) -> str:
    if not schools:
        return (
            "Use the map on [JP Campus](/?lang=en) to compare this stay with "
            "nearby language schools and universities."
        )
    lines = [
        "Schools and universities often searched near this property:",
        "",
    ]
    for s in schools:
        kind = "University" if s["category"] == "university" else "Language school"
        lines.append(
            f"- [{s['name']}]({s['link']}?lang=en) — about **{s['distance_km']} km** ({kind})"
        )
    lines.append("")
    lines.append(
        "Open the [JP Campus map](/?lang=en) to plot this stay against more schools."
    )
    return "\n".join(lines)


def _nearby_section_kr(schools: list[dict]) -> str:
    if not schools:
        return "[JP Campus 지도](/?lang=kr)에서 근처 어학원·대학과 함께 비교해 보세요."
    lines = [
        "이 숙소 근처에서 자주 찾는 학교:",
        "",
    ]
    for s in schools:
        kind = "대학교" if s["category"] == "university" else "어학원"
        lines.append(
            f"- [{s['name']}]({s['link']}?lang=kr) — 약 **{s['distance_km']} km** ({kind})"
        )
    lines.append("")
    lines.append("[JP Campus 지도](/?lang=kr)에서 더 많은 학교와 위치를 비교해 보세요.")
    return "\n".join(lines)


def _faq_en(stay: dict, schools: list[dict], area: str, type_en: str) -> list[dict]:
    name = stay["name_en"]
    addr = stay["address"]
    near = ""
    if schools:
        near = " Nearby options include " + ", ".join(
            f"{s['name']} (~{s['distance_km']} km)" for s in schools[:3]
        ) + "."
    return [
        {
            "q": f"Is {name} good for international students?",
            "a": (
                f"Yes — {name} is a foreigner-friendly {type_en.lower()} operated by "
                f"{stay['operator']}. Furnished rooms and flexible contracts make it "
                f"a common choice while studying in {area}."
            ),
        },
        {
            "q": f"Do I need a Japanese guarantor to stay at {name}?",
            "a": (
                f"Most {type_en.lower()} operators, including {stay['operator']}, "
                "do not require a Japanese guarantor. Always confirm the current "
                "contract rules on the operator website before you apply."
            ),
        },
        {
            "q": f"Where is {name} located?",
            "a": f"{name} is at {addr}.{near}",
        },
        {
            "q": f"How do I book {name}?",
            "a": (
                f"Check availability and apply on the {stay['operator']} website. "
                "JP Campus lists properties for research only and is not affiliated "
                f"with {stay['operator']}."
            ),
        },
    ]


def _faq_kr(stay: dict, schools: list[dict], area: str, type_kr: str) -> list[dict]:
    name = stay.get("name_kr") or stay["name_en"]
    addr = stay.get("address_kr") or stay["address"]
    near = ""
    if schools:
        near = " 근처 학교 예: " + ", ".join(
            f"{s['name']} (약 {s['distance_km']} km)" for s in schools[:3]
        ) + "."
    return [
        {
            "q": f"{name}은 유학생이 묵기 적합한가요?",
            "a": (
                f"네. {name}은 {stay['operator']}에서 운영하는 외국인 친화 {type_kr}입니다. "
                f"가구·유연한 계약으로 {area} 유학 중 임시 주거로 많이 찾습니다."
            ),
        },
        {
            "q": f"{name} 예약에 일본 보증인이 필요한가요?",
            "a": (
                f"{stay['operator']}를 포함한 대부분의 {type_kr}는 일본 보증인 없이 "
                "계약하는 경우가 많습니다. 최신 조건은 운영사 사이트에서 확인하세요."
            ),
        },
        {
            "q": f"{name}은 어디에 있나요?",
            "a": f"주소는 {addr}입니다.{near}",
        },
        {
            "q": f"{name}은 어떻게 예약하나요?",
            "a": (
                f"{stay['operator']} 사이트에서 공실을 확인하고 신청하세요. "
                f"JP Campus는 정보 제공 목적이며 {stay['operator']}와 제휴 관계가 없습니다."
            ),
        },
    ]


def _body_en(stay: dict, schools: list[dict], area: str) -> str:
    type_en, _ = STAY_TYPE_LABEL[stay["stay_type"]]
    # Benefits + booking CTA are rendered in detail.html (cards / buttons).
    return f"""## About this property

**{stay["name_en"]}** is a foreigner-friendly **{type_en.lower()}** in **{area}**, operated by **{stay["operator"]}**.
International students use it as furnished housing while studying Japanese or commuting to nearby campuses.

## Estimated rent

{_rent_line_en(stay)}

## Location & nearby schools

{stay["address"]}

{_nearby_section_en(schools)}
"""


def _body_kr(stay: dict, schools: list[dict], area: str) -> str:
    type_kr = STAY_TYPE_LABEL_KR[stay["stay_type"]]
    name_kr = stay.get("name_kr") or stay["name_en"]
    addr = stay.get("address_kr") or stay["address"]
    # 혜택 카드·예약 버튼은 detail.html에서 렌더합니다.
    return f"""## 시설 소개

**{name_kr}** ({stay["name_en"]})는 **{area}**의 **{type_kr}**로, **{stay["operator"]}**에서 운영합니다.
일본어 학교·대학 통학이 필요한 유학생이 가구 완비 숙소로 자주 찾는 유형입니다.

## 예상 월세

{_rent_line_kr(stay)}

## 위치·근처 학교

{addr}

{_nearby_section_kr(schools)}
"""


def _metadata(stay: dict, lang: str, schools: list[dict], area: str) -> dict:
    type_en, _ = STAY_TYPE_LABEL[stay["stay_type"]]
    type_kr = STAY_TYPE_LABEL_KR[stay["stay_type"]]
    region = stay.get("region") or "japan"
    region_en = _region_label(region, "en")
    region_kr = _region_label(region, "kr")
    name_en = stay["name_en"]
    name_kr = stay.get("name_kr") or name_en
    rent_lo, rent_hi = stay.get("min_rent"), stay.get("max_rent")

    if lang == "kr":
        title = f"{name_kr} — {area} 유학생 {type_kr}"
        if rent_lo and rent_hi:
            description = (
                f"{area} {type_kr} {name_kr}. 월세 약 ¥{rent_lo:,}–¥{rent_hi:,}. "
                f"근처 어학원·대학과 함께 JP Campus에서 비교하세요."
            )
        else:
            description = (
                f"{area} {type_kr} {name_kr}. 외국인 친화 숙소. "
                f"근처 어학원·대학과 함께 JP Campus에서 비교하세요."
            )
        seo_title = title
        seo_description = (
            f"{name_kr}({name_en}): {area} {type_kr}. "
            f"보증인·가구·예약 정보를 확인하고 근처 학교를 비교하세요."
        )
        faq = _faq_kr(stay, schools, area, type_kr)
        tags = ["숙소", region_kr, type_kr]
        if area and area != region_kr:
            tags.append(area)
    else:
        title = f"{name_en} — {area} Student {type_en}"
        if rent_lo and rent_hi:
            description = (
                f"{area} {type_en.lower()} for international students. "
                f"¥{rent_lo:,}–¥{rent_hi:,}/mo. Foreigner-friendly housing near schools."
            )
        else:
            description = (
                f"{area} {type_en.lower()} for international students. "
                f"Foreigner-friendly housing near schools. Confirm details on the operator site."
            )
        seo_title = title
        seo_description = (
            f"{name_en}: {area} {type_en.lower()} for students. "
            f"Compare location vs nearby schools on the JP Campus map."
        )
        faq = _faq_en(stay, schools, area, type_en)
        tags = ["Housing", region_en, type_en]
        if area and area != region_en:
            tags.append(area)

    today = date.today().isoformat()
    nearby_meta = [
        {
            "id": s["id"],
            "name": s["name"],
            "distance_km": s["distance_km"],
            "category": s["category"],
        }
        for s in schools
    ]
    return {
        "id": f"stay_{stay['id']}",
        "entity": "stay",
        "category": "stay",
        "stay_type": stay["stay_type"],
        "layout": "stay",
        "lang": "kr" if lang == "kr" else "en",
        "title": title,
        "description": description,
        "seo_title": seo_title,
        "seo_description": seo_description,
        "thumbnail": THUMB.format(id=stay["id"]),
        "date": today,
        "basic_info": {
            "name_en": name_en,
            "name_ja": name_kr,
            "name_display": name_kr if lang == "kr" else name_en,
            "address": stay.get("address_kr") if lang == "kr" else stay["address"],
            "operator": stay["operator"],
        },
        "location": {"lat": stay["lat"], "lng": stay["lng"]},
        "rent": {
            "min": stay.get("min_rent"),
            "max": stay.get("max_rent"),
        },
        "foreigner_ok": True,
        "furnished": True,
        "no_guarantor": True,
        "booking_url": stay["booking_url"],
        "tags": tags,
        "nearby_schools": nearby_meta,
        "faq": faq,
    }


def write_stay(stay: dict, *, force: bool = False) -> list[str]:
    written: list[str] = []
    schools = nearby_schools(float(stay["lat"]), float(stay["lng"]))
    area_en = _area_from_address(stay["address"]) or _region_label(stay.get("region") or "japan", "en")
    area_kr = (
        _area_from_address(stay.get("address_kr") or "")
        or _region_label(stay.get("region") or "japan", "kr")
    )

    for lang, suffix, body_fn, area in (
        ("en", "", _body_en, area_en),
        ("kr", "_kr", _body_kr, area_kr),
    ):
        filename = f"stay_{stay['id']}{suffix}.md"
        path = os.path.join(CONTENT_DIR, filename)
        if os.path.exists(path) and not force:
            continue
        post = frontmatter.Post(body_fn(stay, schools, area), **_metadata(stay, lang, schools, area))
        with open(path, "w", encoding="utf-8") as f:
            f.write(frontmatter.dumps(post))
        written.append(filename)
    return written


def resolve_targets(args: argparse.Namespace, rows: list[dict]) -> list[dict]:
    by_id = {r["id"]: r for r in rows}

    if args.republish_published:
        return [r for r in rows if r.get("published") and r.get("lat") is not None]

    if args.sample:
        return select_samples(
            rows,
            per_region=args.per_region,
            regions=args.region,
            unpublished_only=not args.include_published,
        )

    if args.ids:
        ids = [x.strip() for x in args.ids.split(",") if x.strip()]
        missing = [i for i in ids if i not in by_id]
        if missing:
            raise SystemExit(f"Unknown ids: {', '.join(missing)}")
        return [by_id[i] for i in ids]

    if args.region:
        allow = set(args.region)
        picked = [
            r
            for r in rows
            if r.get("region") in allow
            and (args.include_published or not r.get("published"))
            and r.get("lat") is not None
        ]
        picked.sort(key=lambda r: (r.get("operator") or "", r.get("name_en") or ""))
        if args.limit:
            # distribute roughly across regions
            per = max(1, args.limit // max(1, len(allow)))
            out: list[dict] = []
            for reg in sorted(allow):
                chunk = [r for r in picked if r.get("region") == reg][:per]
                out.extend(chunk)
            return out[: args.limit]
        return picked

    raise SystemExit("Specify --sample, --ids, --region, or --republish-published")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--sample", action="store_true", help="Publish N per region")
    parser.add_argument("--per-region", type=int, default=8)
    parser.add_argument("--ids", type=str, help="Comma-separated catalog ids")
    parser.add_argument(
        "--region",
        action="append",
        help="Region filter (repeatable). Ex: --region tokyo --region osaka",
    )
    parser.add_argument("--limit", type=int, default=None)
    parser.add_argument("--include-published", action="store_true")
    parser.add_argument(
        "--republish-published",
        action="store_true",
        help="Target all catalog stays that already have markdown pages",
    )
    parser.add_argument("--force", action="store_true", help="Overwrite existing md")
    parser.add_argument("--build", action="store_true", help="Run build_data.py after")
    parser.add_argument("--enrich-regions", action="store_true", help="Write region into stay_listings.json")
    parser.add_argument("--list-regions", action="store_true")
    parser.add_argument("--list-unpublished", action="store_true")
    args = parser.parse_args()

    rows = load_listings(enrich_region=True)

    if args.enrich_regions:
        save_listings(rows)
        print(f"Updated regions in {LISTINGS_PATH}")

    if args.list_regions:
        counts = region_counts(rows)
        published = sum(1 for r in rows if r.get("published"))
        print(f"catalog={len(rows)} published={published}")
        for reg, n in counts.items():
            pub = sum(1 for r in rows if r.get("region") == reg and r.get("published"))
            print(f"  {reg}: {n} (published {pub})")
        return 0

    if args.list_unpublished:
        items = [r for r in rows if not r.get("published")]
        if args.region:
            allow = set(args.region)
            items = [r for r in items if r.get("region") in allow]
        for r in items[:200]:
            print(f"{r['id']}\t{r.get('region')}\t{r.get('operator')}\t{r.get('name_en')}")
        print(f"total_unpublished_shown={min(len(items), 200)} / {len(items)}")
        return 0

    targets = resolve_targets(args, rows)
    if not targets:
        print("No stays to publish")
        return 0

    print(f"Publishing {len(targets)} stays…")
    written_files = 0
    for row in targets:
        seed = catalog_to_seed_row(row)
        files = write_stay(seed, force=args.force)
        written_files += len(files)
        for f in files:
            print(f"  wrote {f}")

    print(f"Done: {written_files} markdown file(s) for {len(targets)} stays")

    if args.build:
        print("Running build_data.py…")
        subprocess.check_call([sys.executable, str(SCRIPT_DIR / "build_data.py")])
        print("Running ensure_stay_images.py…")
        subprocess.check_call([sys.executable, str(SCRIPT_DIR / "ensure_stay_images.py")])

    return 0


if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env python3
"""Generate stay_*.md content files from data/tokyo_stays_seed.py."""

from __future__ import annotations

import os
import sys

import frontmatter

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, SCRIPT_DIR)
sys.path.insert(0, os.path.join(os.path.dirname(SCRIPT_DIR), "data"))

from common import BASE_DIR, CONTENT_DIR  # noqa: E402
from tokyo_stays_seed import TOKYO_STAYS  # noqa: E402

THUMB = "/static/images/stay_{id}.jpg"

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


def _body_en(stay: dict) -> str:
    type_en, _ = STAY_TYPE_LABEL[stay["stay_type"]]
    return f"""## About this property

**{stay["name_en"]}** is a foreigner-friendly **{type_en.lower()}** operated by **{stay["operator"]}** in Tokyo. It is a practical option for international students who need a furnished place before school dormitories open or while searching for a long-term apartment.

## Why students choose this type

- **No Japanese guarantor** required at most {type_en.lower()} operators
- **Furnished rooms** with Wi-Fi — move in with a suitcase
- **Flexible contracts** from a few weeks to several months
- **English support** available at booking (varies by operator)

## Estimated rent

Monthly rent typically ranges from **¥{stay["min_rent"]:,}** to **¥{stay["max_rent"]:,}** (utilities may be extra). Prices change by season and room type — confirm on the operator site before booking.

## Location

{stay["address"]}

Use the map on [JP Campus](/?lang=en) to compare this stay with nearby language schools and universities.

## Booking

Visit the operator website to check availability and apply:

**[{stay["operator"]}]({stay["booking_url"]})**

> JP Campus lists properties for research only. We are not affiliated with {stay["operator"]}. Always verify fees, house rules, and contract terms directly with the operator.
"""


def _body_kr(stay: dict) -> str:
    type_kr = STAY_TYPE_LABEL_KR[stay["stay_type"]]
    return f"""## 시설 소개

**{stay["name_en"]}** ({stay["name_ja"]})는 도쿄에 위치한 **{type_kr}** 시설로, **{stay["operator"]}**에서 운영합니다. 일본 유학 준비생이 기숙사 입소 전이나 월세 집을 구하는 동안 머물기 좋은 선택지입니다.

## 유학생에게 좋은 이유

- 대부분 **일본 보증인 없이** 계약 가능
- **가구·Wi-Fi 완비** — 가방만 들고 입주
- **단기~중기 계약** (수 주~수개월)
- 예약 시 **영어 지원** (업체별 상이)

## 예상 월세

월 **¥{stay["min_rent"]:,} ~ ¥{stay["max_rent"]:,}** 수준 (관리비 별도 가능). 시즌·방 타입에 따라 변동하니 예약 전 반드시 확인하세요.

## 위치

{stay["address"]}

[JP Campus 지도](/?lang=kr)에서 근처 어학원·대학과 함께 비교해 보세요.

## 예약

운영사 사이트에서 공실·요금을 확인하세요:

**[{stay["operator"]}]({stay["booking_url"]})**

> JP Campus는 정보 제공 목적입니다. {stay["operator"]}와 제휴 관계가 없습니다. 계약 조건은 반드시 운영사에서 직접 확인하세요.
"""


def _metadata(stay: dict, lang: str) -> dict:
    type_en, type_ja = STAY_TYPE_LABEL[stay["stay_type"]]
    title_en = f"{stay['name_en']} — Tokyo Student {type_en}"
    title_kr = f"{stay['name_en']} — 도쿄 유학생 {STAY_TYPE_LABEL_KR[stay['stay_type']]}"

    meta = {
        "id": f"stay_{stay['id']}",
        "entity": "stay",
        "category": "stay",
        "stay_type": stay["stay_type"],
        "layout": "stay",
        "lang": "kr" if lang == "kr" else "en",
        "title": title_kr if lang == "kr" else title_en,
        "description": (
            f"Tokyo {type_en.lower()} for international students. "
            f"¥{stay['min_rent']:,}–¥{stay['max_rent']:,}/mo. No guarantor. Furnished."
        ),
        "seo_title": title_kr if lang == "kr" else title_en,
        "seo_description": (
            f"{stay['name_en']}: foreigner-friendly Tokyo housing for students. "
            f"Compare on JP Campus map near schools."
        ),
        "thumbnail": THUMB.format(id=stay["id"]),
        "date": "2026-07-09",
        "basic_info": {
            "name_en": stay["name_en"],
            "name_ja": stay["name_ja"],
            "name_display": stay["name_en"],
            "address": stay["address"],
            "operator": stay["operator"],
        },
        "location": {"lat": stay["lat"], "lng": stay["lng"]},
        "rent": {"min": stay["min_rent"], "max": stay["max_rent"]},
        "foreigner_ok": True,
        "furnished": True,
        "no_guarantor": True,
        "booking_url": stay["booking_url"],
        "tags": ["Housing", "Tokyo", type_en],
    }
    return meta


def write_stay_files(force: bool = False) -> int:
    written = 0
    for stay in TOKYO_STAYS:
        for lang, suffix, body_fn in (
            ("en", "", _body_en),
            ("kr", "_kr", _body_kr),
        ):
            filename = f"stay_{stay['id']}{suffix}.md"
            path = os.path.join(CONTENT_DIR, filename)
            if os.path.exists(path) and not force:
                continue
            post = frontmatter.Post(body_fn(stay), **_metadata(stay, lang))
            with open(path, "w", encoding="utf-8") as f:
                f.write(frontmatter.dumps(post))
            written += 1
            print(f"  wrote {filename}")
    return written


def main():
    print(f"📍 Generating stay markdown in {CONTENT_DIR}")
    n = write_stay_files(force="--force" in sys.argv)
    print(f"✅ {n} file(s) written ({len(TOKYO_STAYS)} stays × 2 langs)")


if __name__ == "__main__":
    main()

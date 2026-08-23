"""A8.net housing affiliate banners (Oakhouse, Cross One Room)."""

from __future__ import annotations

import os
from typing import Any, Literal

A8PageKind = Literal["stays_list", "stay_detail", "housing_guide"]

# Default links from A8 link generator (jpcampus.com media). Override via env if rotated.
OAKHOUSE_A8 = {
    "id": "oakhouse",
    "click_url": os.getenv(
        "A8_OAKHOUSE_CLICK_URL",
        "https://px.a8.net/svt/ejp?a8mat=4BACLH+3OROOI+41A0+601S1",
    ),
    "image_url": os.getenv(
        "A8_OAKHOUSE_BANNER_URL",
        "https://www23.a8.net/svt/bgt?aid=260823365223&wid=001&eno=01&mid=s00000018828001008000&mc=1",
    ),
    "pixel_url": os.getenv(
        "A8_OAKHOUSE_PIXEL_URL",
        "https://www18.a8.net/0.gif?a8mat=4BACLH+3OROOI+41A0+601S1",
    ),
    "label_en": "Oakhouse — share houses",
    "label_kr": "오크하우스 — 셰어하우스",
    "desc_en": "Japan’s largest share-house network · no deposit / key money",
    "desc_kr": "일본 최대급 셰어하우스 · 보증금·예키금 부담 적음",
    "alt_en": "Oakhouse share house — affiliate",
    "alt_kr": "오크하우스 셰어하우스 — 제휴",
}

CROSS_ONEROOM_A8 = {
    "id": "cross_oneroom",
    "click_url": os.getenv(
        "A8_CROSS_ONEROOM_CLICK_URL",
        "https://px.a8.net/svt/ejp?a8mat=4BACLH+3L731U+4EZ2+BY641",
    ),
    "image_url": os.getenv(
        "A8_CROSS_ONEROOM_BANNER_URL",
        "https://www27.a8.net/svt/bgt?aid=260823365217&wid=001&eno=01&mid=s00000020603002007000&mc=1",
    ),
    "pixel_url": os.getenv(
        "A8_CROSS_ONEROOM_PIXEL_URL",
        "https://www11.a8.net/0.gif?a8mat=4BACLH+3L731U+4EZ2+BY641",
    ),
    "label_en": "Cross One Room — furnished apartments",
    "label_kr": "크로스 원룸 — 가구·가전 포함",
    "desc_en": "Tokyo from ¥38,000/mo · furniture & appliances included",
    "desc_kr": "도쿄 월 3.8만엔부터 · 가구·가전 포함 원룸",
    "alt_en": "Cross One Room furnished apartments in Tokyo — affiliate",
    "alt_kr": "크로스 원룸 도쿄 가구·가전 포함 원룸 — 제휴",
}

HOUSING_A8_GUIDE_SLUGS: frozenset[str] = frozenset(
    {
        "housing",
        "housing-seed",
        "apartment-initial-costs",
        "finding-apts-online",
        "tokyo-student-housing-operators",
        "rent-guarantor",
        "utilities-setup",
        "nha-subsidy-housing",
        "thrift-stores-furniture",
    }
)


def _is_oakhouse_stay(stay_id: str = "", operator: str = "") -> bool:
    sid = (stay_id or "").lower()
    op = (operator or "").lower()
    return sid.startswith("oakhouse_") or "oakhouse" in op


def _banner_copy(banner: dict[str, str], *, lang: str) -> dict[str, str]:
    is_kr = (lang or "en").lower() in ("kr", "ko")
    return {
        "id": banner["id"],
        "click_url": banner["click_url"],
        "image_url": banner["image_url"],
        "pixel_url": banner["pixel_url"],
        "alt": banner["alt_kr"] if is_kr else banner["alt_en"],
        "label": banner["label_kr"] if is_kr else banner["label_en"],
        "desc": banner["desc_kr"] if is_kr else banner["desc_en"],
    }


def a8_housing_context(
    *,
    page_kind: A8PageKind,
    lang: str = "en",
    stay_id: str = "",
    stay_operator: str = "",
    guide_slug: str = "",
) -> dict[str, Any]:
    """Template context for A8 housing banners on stays / housing guides."""
    if not os.getenv("A8_HOUSING_ENABLED", "1").strip().lower() in ("1", "true", "yes", "on"):
        return {"show_a8_housing": False, "a8_housing_banners": [], "a8_housing_note": ""}

    is_kr = (lang or "en").lower() in ("kr", "ko")
    guide_key = (guide_slug or "").removesuffix("_kr").removeprefix("guide_")
    show_oakhouse = False
    show_cross = False

    if page_kind == "stays_list":
        show_oakhouse = True
        show_cross = True
    elif page_kind == "stay_detail":
        if _is_oakhouse_stay(stay_id, stay_operator):
            show_oakhouse = True
        show_cross = True
    elif page_kind == "housing_guide" and guide_key in HOUSING_A8_GUIDE_SLUGS:
        show_oakhouse = True
        show_cross = True

    banners: list[dict[str, str]] = []
    if show_oakhouse:
        banners.append(_banner_copy(OAKHOUSE_A8, lang=lang))
    if show_cross:
        banners.append(_banner_copy(CROSS_ONEROOM_A8, lang=lang))

    if not banners:
        return {"show_a8_housing": False, "a8_housing_banners": [], "a8_housing_note": ""}

    note = (
        "제휴 광고 · 새 탭 · JP Campus는 운영사와 제휴 관계가 없을 수 있습니다."
        if is_kr
        else "Affiliate ads · open in new tab · JP Campus may earn a commission."
    )
    title = (
        "유학생 숙소 제휴"
        if is_kr
        else "Student housing partners"
    )
    return {
        "show_a8_housing": True,
        "a8_housing_banners": banners,
        "a8_housing_note": note,
        "a8_housing_title": title,
        "oakhouse_a8_click_url": OAKHOUSE_A8["click_url"],
    }


def oakhouse_booking_url(
    *,
    operator: str,
    booking_url: str,
) -> str:
    """Use A8 click URL for Oakhouse operator booking CTAs when configured."""
    if _is_oakhouse_stay(operator=operator) and OAKHOUSE_A8["click_url"]:
        return OAKHOUSE_A8["click_url"]
    return booking_url

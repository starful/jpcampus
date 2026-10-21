"""A8.net housing + travel affiliate banners for JP Campus.

Oakhouse (A8) + Agoda Partners. Cross One Room / TORA / Shin-Okubo removed.
"""

from __future__ import annotations

import os
from typing import Any, Literal

try:
    from agoda_partners import url_for_location
except ImportError:
    from .agoda_partners import url_for_location


def _agoda_partners_url(lang: str | None = "en") -> str:
    return url_for_location(lang=lang, country="jp", default_city=5085)


A8PageKind = Literal["stays_list", "stay_detail", "housing_guide", "travel_guide"]

GUIDE_A8_TRAVEL: frozenset[str] = frozenset(
    {
        "transport-ic",
        "transport-seed",
        "shinkansen-deals",
        "student-travel-willerexpress",
        "train-pass",
        "capsule-hotels-etiquette",
        "golden-week",
        "onsen-etiquette",
    }
)

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
        "humidity-mold-prevention",
        "winter-room-heating",
    }
)

# Housing guides: Oakhouse A8 is primary CTA (not Rakuten Ichiba bedding).
A8_PRIORITY_GUIDE_SLUGS: frozenset[str] = HOUSING_A8_GUIDE_SLUGS

OAKHOUSE_A8 = {
    "id": "oakhouse",
    "click_url": os.getenv(
        "A8_OAKHOUSE_CLICK_URL",
        "https://px.a8.net/svt/ejp?a8mat=4BACLH+3OROOI+41A0+60H7L",
    ),
    "image_url": os.getenv(
        "A8_OAKHOUSE_BANNER_URL",
        "https://www22.a8.net/svt/bgt?aid=260823365223&wid=001&eno=01&mid=s00000018828001010000&mc=1",
    ),
    "pixel_url": os.getenv(
        "A8_OAKHOUSE_PIXEL_URL",
        "https://www17.a8.net/0.gif?a8mat=4BACLH+3OROOI+41A0+60H7L",
    ),
    "label_en": "Oakhouse",
    "label_kr": "오크하우스",
    "desc_en": "Share houses · no deposit / key money",
    "desc_kr": "셰어하우스 · 보증금·예키금 부담 적음",
    "alt_en": "Oakhouse share house — affiliate",
    "alt_kr": "오크하우스 셰어하우스 — 제휴",
}

AGODA_A8 = {
    "id": "agoda",
    "click_url": "",
    "image_url": "",
    "pixel_url": "",
    "label_en": "Agoda",
    "label_kr": "Agoda",
    "desc_en": "Hotels and stays near campus",
    "desc_kr": "캠퍼스 주변 숙소·호텔",
    "alt_en": "Agoda — hotels",
    "alt_kr": "Agoda — 숙소",
}


def _enabled() -> bool:
    return os.getenv("A8_HOUSING_ENABLED", "1").strip().lower() in (
        "1",
        "true",
        "yes",
        "on",
    )


def _is_oakhouse_stay(stay_id: str = "", operator: str = "") -> bool:
    sid = (stay_id or "").lower()
    op = (operator or "").lower()
    return sid.startswith("oakhouse_") or "oakhouse" in op


def _banner_copy(banner: dict[str, str], *, lang: str) -> dict[str, str]:
    is_kr = (lang or "en").lower() in ("kr", "ko")
    click = banner["click_url"]
    image = banner["image_url"]
    pixel = banner["pixel_url"]
    if banner.get("id") == "agoda":
        click = _agoda_partners_url(lang)
        image = ""
        pixel = ""
    return {
        "id": banner["id"],
        "click_url": click,
        "image_url": image,
        "pixel_url": pixel,
        "alt": banner["alt_kr"] if is_kr else banner["alt_en"],
        "label": banner["label_kr"] if is_kr else banner["label_en"],
        "desc": banner["desc_kr"] if is_kr else banner["desc_en"],
    }


def _empty() -> dict[str, Any]:
    return {
        "show_a8_housing": False,
        "a8_housing_banners": [],
        "a8_housing_note": "",
        "show_a8_banners": False,
        "a8_banners": [],
        "a8_banners_note": "",
        "agoda_cta": None,
        "show_agoda_cta": False,
    }


def _attach_agoda_cta(ctx: dict[str, Any]) -> dict[str, Any]:
    banners = ctx.get("a8_housing_banners") or ctx.get("a8_banners") or []
    agoda = next((b for b in banners if b.get("id") == "agoda"), None)
    ctx["agoda_cta"] = agoda
    ctx["show_agoda_cta"] = agoda is not None
    return ctx


def a8_housing_context(
    *,
    page_kind: A8PageKind,
    lang: str = "en",
    stay_id: str = "",
    stay_operator: str = "",
    guide_slug: str = "",
) -> dict[str, Any]:
    """Oakhouse on stays and housing guides; Agoda on stay detail (EN)."""
    if not _enabled():
        return _empty()

    is_kr = (lang or "en").lower() in ("kr", "ko")
    guide_key = (guide_slug or "").removesuffix("_kr").removeprefix("guide_")
    show_oakhouse = False

    if page_kind == "stays_list":
        show_oakhouse = True
    elif page_kind == "stay_detail":
        if _is_oakhouse_stay(stay_id, stay_operator):
            show_oakhouse = True
    elif page_kind == "housing_guide" and guide_key in HOUSING_A8_GUIDE_SLUGS:
        show_oakhouse = True

    banners: list[dict[str, str]] = []
    if show_oakhouse:
        banners.append(_banner_copy(OAKHOUSE_A8, lang=lang))
    if page_kind == "stay_detail":
        banners.append(_banner_copy(AGODA_A8, lang=lang))

    if not banners:
        return _empty()

    note = (
        "제휴 광고 · 새 탭에서 열림"
        if is_kr
        else "Affiliate ads · opens in a new tab"
    )
    if page_kind == "stay_detail":
        title = ""
    elif page_kind == "housing_guide":
        title = (
            "셰어하우스 먼저 확인"
            if is_kr
            else "Check share houses first"
        )
    else:
        title = "유학생 숙소 제휴" if is_kr else "Student housing partners"
    return _attach_agoda_cta(
        {
            "show_a8_housing": True,
            "a8_housing_banners": banners,
            "a8_housing_note": note,
            "a8_housing_title": title,
            "oakhouse_a8_click_url": OAKHOUSE_A8["click_url"],
            "show_a8_banners": False,
            "a8_banners": [],
            "a8_banners_note": "",
        }
    )


def a8_travel_context(
    *,
    page_kind: A8PageKind,
    lang: str = "en",
    guide_slug: str = "",
    item_type: str = "guide",
) -> dict[str, Any]:
    """Agoda Partners on travel prep guides (EN + KR).

    Empty responses omit agoda_cta keys so a prior a8_housing_context
    (e.g. stay detail) is not overwritten when contexts are merged.
    """
    empty = {"show_a8_banners": False, "a8_banners": [], "a8_banners_note": ""}
    if not _enabled():
        return empty

    is_kr = (lang or "en").lower() in ("kr", "ko")
    guide_key = (guide_slug or "").removesuffix("_kr").removeprefix("guide_")
    kind = (item_type or "guide").strip().lower()

    if kind == "stay" or page_kind == "stay_detail":
        return empty

    if guide_key not in GUIDE_A8_TRAVEL:
        return empty

    banners = [_banner_copy(AGODA_A8, lang=lang)]
    return _attach_agoda_cta(
        {
            "show_a8_banners": True,
            "a8_banners": banners,
            "a8_banners_title": (
                "여행·숙소 제휴" if is_kr else "Travel partners"
            ),
            "a8_banners_note": (
                "제휴 광고 · 새 탭에서 열림"
                if is_kr
                else "Affiliate ads · opens in new tab"
            ),
        }
    )


def oakhouse_booking_url(*, operator: str, booking_url: str) -> str:
    if _is_oakhouse_stay(operator=operator) and OAKHOUSE_A8["click_url"]:
        return OAKHOUSE_A8["click_url"]
    return booking_url

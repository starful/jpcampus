"""A8.net housing + travel affiliate banners for JP Campus."""

from __future__ import annotations

import os
from typing import Any, Literal

A8PageKind = Literal["stays_list", "stay_detail", "housing_guide", "travel_guide"]

GUIDE_A8_ESIM: frozenset[str] = frozenset(
    {
        "sim-card-guide",
        "cheap-phone-accessories",
        "internet-setup",
        "soft-bank-air-vs-fiber",
    }
)
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
    }
)

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

CROSS_ONEROOM_A8 = {
    "id": "cross_oneroom",
    "click_url": os.getenv(
        "A8_CROSS_ONEROOM_CLICK_URL",
        "https://px.a8.net/svt/ejp?a8mat=4BACLH+3L731U+4EZ2+BYDTT",
    ),
    "image_url": os.getenv(
        "A8_CROSS_ONEROOM_BANNER_URL",
        "https://www21.a8.net/svt/bgt?aid=260823365217&wid=001&eno=01&mid=s00000020603002008000&mc=1",
    ),
    "pixel_url": os.getenv(
        "A8_CROSS_ONEROOM_PIXEL_URL",
        "https://www16.a8.net/0.gif?a8mat=4BACLH+3L731U+4EZ2+BYDTT",
    ),
    "label_en": "Cross One Room",
    "label_kr": "크로스 원룸",
    "desc_en": "Furnished Tokyo apartments from ¥38,000/mo",
    "desc_kr": "도쿄 월 3.8만엔부터 · 가구·가전 포함",
    "alt_en": "Cross One Room furnished apartments in Tokyo — affiliate",
    "alt_kr": "크로스 원룸 도쿄 가구·가전 포함 원룸 — 제휴",
}

AGODA_A8 = {
    "id": "agoda",
    "click_url": os.getenv(
        "A8_AGODA_CLICK_URL",
        "https://px.a8.net/svt/ejp?a8mat=4BAH9J+13AMPE+4X1W+5ZMCH",
    ),
    "image_url": os.getenv(
        "A8_AGODA_BANNER_URL",
        "https://www28.a8.net/svt/bgt?aid=260829415066&wid=001&eno=01&mid=s00000022946001006000&mc=1",
    ),
    "pixel_url": os.getenv(
        "A8_AGODA_PIXEL_URL",
        "https://www17.a8.net/0.gif?a8mat=4BAH9J+13AMPE+4X1W+5ZMCH",
    ),
    "label_en": "Agoda",
    "label_kr": "Agoda",
    "desc_en": "Hotels and stays near campus",
    "desc_kr": "캠퍼스 주변 숙소·호텔",
    "alt_en": "Agoda — affiliate",
    "alt_kr": "Agoda — 제휴",
}

TORA_ESIM_A8 = {
    "id": "tora_esim",
    "click_url": os.getenv(
        "A8_TORA_ESIM_CLICK_URL",
        "https://px.a8.net/svt/ejp?a8mat=4BAH9I+GEM0VM+5NG6+5ZEMP",
    ),
    "image_url": os.getenv(
        "A8_TORA_ESIM_BANNER_URL",
        "https://www23.a8.net/svt/bgt?aid=260829414992&wid=001&eno=01&mid=s00000026367001005000&mc=1",
    ),
    "pixel_url": os.getenv(
        "A8_TORA_ESIM_PIXEL_URL",
        "https://www10.a8.net/0.gif?a8mat=4BAH9I+GEM0VM+5NG6+5ZEMP",
    ),
    "label_en": "TORA eSIM",
    "label_kr": "TORA eSIM",
    "desc_en": "Travel eSIM for arrival in Japan",
    "desc_kr": "일본 도착용 여행 eSIM",
    "alt_en": "TORA eSIM — affiliate",
    "alt_kr": "TORA eSIM — 제휴",
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
    return {
        "id": banner["id"],
        "click_url": banner["click_url"],
        "image_url": banner["image_url"],
        "pixel_url": banner["pixel_url"],
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
    }


def a8_housing_context(
    *,
    page_kind: A8PageKind,
    lang: str = "en",
    stay_id: str = "",
    stay_operator: str = "",
    guide_slug: str = "",
) -> dict[str, Any]:
    """Oakhouse / Cross One Room on stays and housing guides."""
    if not _enabled():
        return _empty()

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
    # Stay detail EN: Agoda in the same one-row (not a second block)
    if page_kind == "stay_detail" and not is_kr:
        banners.append(_banner_copy(AGODA_A8, lang=lang))

    if not banners:
        return _empty()

    note = (
        "제휴 광고 · 새 탭에서 열림"
        if is_kr
        else "Affiliate ads · opens in a new tab"
    )
    if page_kind == "stay_detail":
        # Panel already has Ready to book? — skip duplicate section title
        title = ""
    else:
        title = "유학생 숙소 제휴" if is_kr else "Student housing partners"
    return {
        "show_a8_housing": True,
        "a8_housing_banners": banners,
        "a8_housing_note": note,
        "a8_housing_title": title,
        "oakhouse_a8_click_url": OAKHOUSE_A8["click_url"],
        "show_a8_banners": False,
        "a8_banners": [],
        "a8_banners_note": "",
    }


def a8_travel_context(
    *,
    page_kind: A8PageKind,
    lang: str = "en",
    guide_slug: str = "",
    item_type: str = "guide",
) -> dict[str, Any]:
    """Agoda / TORA eSIM on travel prep guides and EN stay pages."""
    if not _enabled():
        return {"show_a8_banners": False, "a8_banners": [], "a8_banners_note": ""}

    is_kr = (lang or "en").lower() in ("kr", "ko")
    if is_kr:
        return {"show_a8_banners": False, "a8_banners": [], "a8_banners_note": ""}

    guide_key = (guide_slug or "").removesuffix("_kr").removeprefix("guide_")
    kind = (item_type or "guide").strip().lower()
    banners: list[dict[str, str]] = []

    # Stay detail Agoda lives in a8_housing_context (one row with housing)
    if kind == "stay" or page_kind == "stay_detail":
        return {"show_a8_banners": False, "a8_banners": [], "a8_banners_note": ""}
    if guide_key in GUIDE_A8_ESIM:
        banners.append(_banner_copy(TORA_ESIM_A8, lang=lang))
    elif guide_key in GUIDE_A8_TRAVEL:
        banners.append(_banner_copy(AGODA_A8, lang=lang))
    elif kind in ("school", "university"):
        banners.append(_banner_copy(TORA_ESIM_A8, lang=lang))

    if not banners:
        return {"show_a8_banners": False, "a8_banners": [], "a8_banners_note": ""}

    return {
        "show_a8_banners": True,
        "a8_banners": banners,
        "a8_banners_title": "Travel partners",
        "a8_banners_note": "Affiliate ads · opens in new tab",
    }


def oakhouse_booking_url(*, operator: str, booking_url: str) -> str:
    if _is_oakhouse_stay(operator=operator) and OAKHOUSE_A8["click_url"]:
        return OAKHOUSE_A8["click_url"]
    return booking_url

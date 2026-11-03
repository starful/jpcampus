"""Amazon JP Associates CTA for JP Campus (secondary to Oakhouse A8 / Rakuten)."""

from __future__ import annotations

import os
from typing import Any
from urllib.parse import quote

from app.i18n import is_kr_lang

AMAZON_TAG = os.getenv("AMAZON_JP_TAG", "starful06-22")

AMAZON_KEYWORDS: dict[str, str] = {
    "housing": "一人暮らし 寝具",
    "travel": "日本旅行 グッズ",
    "school": "留学 準備",
    "default": "日本 生活 便利グッズ",
}


def amazon_search_url(keyword: str) -> str:
    return f"https://www.amazon.co.jp/s?k={quote(keyword)}&tag={AMAZON_TAG}"


def amazon_category(slug: str = "", item_type: str = "guide") -> str:
    kind = (item_type or "guide").strip().lower()
    if kind in ("school", "university"):
        return "school"
    from app.a8_affiliate import GUIDE_A8_TRAVEL, HOUSING_A8_GUIDE_SLUGS
    from app.affiliate import normalize_guide_slug

    key = normalize_guide_slug(slug)
    if key in HOUSING_A8_GUIDE_SLUGS:
        return "housing"
    if key in GUIDE_A8_TRAVEL:
        return "travel"
    return "default"


def _hidden() -> dict[str, Any]:
    return {"show_amazon": False, "amazon_cta": None}


def amazon_context(
    slug: str = "",
    *,
    lang: str = "en",
    item_type: str = "guide",
    oakhouse_primary: bool = False,
    rakuten_shown: bool = False,
) -> dict[str, Any]:
    """Amazon CTA for guides/schools. Always secondary: placed below the article,
    never replacing Oakhouse (``oakhouse_primary``) or an already-shown Rakuten box.
    """
    raw = os.getenv("AFFILIATE_JPCAMPUS_AMAZON_ENABLED", "1")
    if raw.strip().lower() not in ("1", "true", "yes", "on"):
        return _hidden()
    kind = (item_type or "guide").strip().lower()
    if kind not in ("guide", "school", "university"):
        return _hidden()
    # Guides already carrying a Rakuten shop box: don't stack another shop CTA.
    if kind == "guide" and rakuten_shown:
        return _hidden()

    cat = amazon_category(slug, kind)
    keyword = AMAZON_KEYWORDS[cat]
    is_kr = is_kr_lang(lang)
    return {
        "show_amazon": True,
        "amazon_cta": {
            "id": "amazon",
            "category": cat,
            "keyword": keyword,
            "click_url": amazon_search_url(keyword),
            "secondary": True,
            "after_oakhouse": bool(oakhouse_primary),
            "title": "관련 용품 — Amazon" if is_kr else "Related gear — Amazon",
            "button_label": (
                f"Amazon에서 「{keyword}」 검색 ↗"
                if is_kr
                else f"Search 「{keyword}」 on Amazon ↗"
            ),
            "note": (
                "제휴 링크 · 새 탭에서 열림"
                if is_kr
                else "Affiliate links · opens in new tab"
            ),
        },
    }

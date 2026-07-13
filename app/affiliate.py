"""Amazon Associates + Rakuten Ichiba search CTAs for JP Campus guides."""

from __future__ import annotations

import os
from typing import Any
from urllib.parse import quote, quote_plus

AMAZON_TAG = os.getenv("AMAZON_ASSOCIATE_TAG", "starful06-22")
RAKUTEN_HGC = os.getenv(
    "RAKUTEN_ICHIBA_HGC", "43cde6d2.98a376f7.43cde6d3.c7b92630"
)
_RAKUTEN_UT = "eyJwYWdlIjoidXJsIiwidHlwZSI6InRleHQiLCJjb2wiOjF9"

# guide slug (without _kr) → search keyword + kind
# kind: "shop" | "book"
GUIDE_AFFILIATE_MAP: dict[str, tuple[str, str]] = {
    # Shopping / lifestyle
    "sim-card-guide": ("格安SIM", "shop"),
    "drugstore-skincare-guide": ("スキンケア", "shop"),
    "cheap-phone-accessories": ("スマホアクセサリー", "shop"),
    "costco-japan-membership": ("コストコ", "shop"),
    "thrift-stores-furniture": ("家具", "shop"),
    "glasses-jins-zoff": ("メガネ", "shop"),
    "100-yen-stores": ("100円ショップ", "shop"),
    "humidity-mold-prevention": ("除湿機", "shop"),
    "winter-room-heating": ("ヒーター", "shop"),
    "bicycle-rules": ("自転車", "shop"),
    "bicycle-parking": ("自転車", "shop"),
    "bicycle-insurance-law": ("自転車 保険", "shop"),
    # Books / study
    "jlpt-levels": ("JLPT 本", "book"),
    "jlpt-seed": ("JLPT 本", "book"),
    "eju-subjects": ("EJU 本", "book"),
    "eju-jlpt": ("JLPT EJU 本", "book"),
    "job-hunting": ("就活 本", "book"),
    "resume-jp": ("履歴書 本", "book"),
}


def normalize_guide_slug(slug: str) -> str:
    s = (slug or "").strip().lower()
    if s.endswith("_kr"):
        s = s[: -len("_kr")]
    if s.startswith("guide_"):
        s = s[len("guide_") :]
    return s


def amazon_search_url(keyword: str) -> str:
    return (
        "https://www.amazon.co.jp/s?k="
        + quote_plus(keyword)
        + "&tag="
        + quote_plus(AMAZON_TAG)
    )


def rakuten_search_url(keyword: str) -> str:
    """Wrap Ichiba search URL the same way the Affiliate tool does."""
    dest = f"https://search.rakuten.co.jp/search/mall/{quote(keyword, safe='')}/"
    pc = quote(dest, safe="")
    return (
        f"https://hb.afl.rakuten.co.jp/hgc/{RAKUTEN_HGC}/"
        f"?pc={pc}&link_type=text&ut={_RAKUTEN_UT}"
    )


def affiliate_context(slug: str, *, lang: str = "en") -> dict[str, Any]:
    """Return template vars for guide affiliate box, or empty show_affiliate=False."""
    key = normalize_guide_slug(slug)
    mapped = GUIDE_AFFILIATE_MAP.get(key)
    if not mapped:
        return {"show_affiliate": False}

    keyword, kind = mapped
    is_kr = (lang or "en").lower() in ("kr", "ko")

    if is_kr:
        if kind == "book":
            title = f"관련 책은 Amazon / 라쿠텐에서 검색하세요"
            desc = (
                "이 페이지는 가이드입니다. 버튼을 누르면 새 탭에서 "
                f"「{keyword}」 검색 결과가 열리며, 특정 상품 페이지가 아닐 수 있습니다."
            )
            amazon_label = f"Amazon에서 {keyword} 검색 ↗"
            rakuten_label = f"라쿠텐에서 {keyword} 검색 ↗"
        else:
            title = f"관련 쇼핑은 Amazon / 라쿠텐에서 검색하세요"
            desc = (
                "이 페이지는 가이드입니다. 버튼을 누르면 새 탭에서 "
                f"「{keyword}」 검색 결과가 열리며, 특정 상품 페이지가 아닐 수 있습니다."
            )
            amazon_label = f"Amazon에서 {keyword} 검색 ↗"
            rakuten_label = f"라쿠텐에서 {keyword} 검색 ↗"
        note = "제휴 링크 · 새 탭에서 열림"
    else:
        if kind == "book":
            title = f"Find related books on Amazon / Rakuten"
            desc = (
                "This page is a guide. Buttons open a new-tab search for "
                f"「{keyword}」 — not always a specific product page."
            )
            amazon_label = f"Search {keyword} on Amazon ↗"
            rakuten_label = f"Search {keyword} on Rakuten ↗"
        else:
            title = f"Shop related items on Amazon / Rakuten"
            desc = (
                "This page is a guide. Buttons open a new-tab search for "
                f"「{keyword}」 — not always a specific product page."
            )
            amazon_label = f"Search {keyword} on Amazon ↗"
            rakuten_label = f"Search {keyword} on Rakuten ↗"
        note = "Affiliate links · opens in new tab"

    return {
        "show_affiliate": True,
        "affiliate_kind": kind,
        "affiliate_keyword": keyword,
        "affiliate_title": title,
        "affiliate_desc": desc,
        "affiliate_note": note,
        "amazon_search_url": amazon_search_url(keyword),
        "rakuten_search_url": rakuten_search_url(keyword),
        "amazon_button_label": amazon_label,
        "rakuten_button_label": rakuten_label,
    }

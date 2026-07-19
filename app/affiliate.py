"""Amazon Associates + Rakuten Ichiba + Klook CTAs for JP Campus guides."""

from __future__ import annotations

import os
from typing import Any
from urllib.parse import quote, quote_plus

AMAZON_TAG = os.getenv("AMAZON_ASSOCIATE_TAG", "starful06-22")
RAKUTEN_HGC = os.getenv(
    "RAKUTEN_ICHIBA_HGC", "43cde6d2.98a376f7.43cde6d3.c7b92630"
)
_RAKUTEN_UT = "eyJwYWdlIjoidXJsIiwidHlwZSI6InRleHQiLCJjb2wiOjF9"

# Travelpayouts jpcampus project — do not reuse krcampus / okonsen short links.
KLOOK_URL = os.getenv("KLOOK_URL", "https://klook.tpo.mx/s8kswiYD")

# eSIM / transport → Klook
GUIDE_KLOOK_SLUGS: frozenset[str] = frozenset(
    {
        "sim-card-guide",
        "transport-ic",
        "transport-seed",
        "cheap-phone-accessories",
    }
)

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
    """Amazon/Rakuten (mapped) + Klook (sim/transport). No Coupang on jpcampus."""
    key = normalize_guide_slug(slug)
    is_kr = (lang or "en").lower() in ("kr", "ko")

    mapped = GUIDE_AFFILIATE_MAP.get(key)
    show_amazon = bool(mapped)
    keyword, kind = mapped if mapped else ("", "shop")
    show_klook = key in GUIDE_KLOOK_SLUGS

    if not show_amazon and not show_klook:
        return {
            "show_affiliate": False,
            "show_amazon": False,
            "show_klook": False,
        }

    partners: list[str] = []
    if show_amazon:
        partners.extend(["Amazon", "라쿠텐" if is_kr else "Rakuten"])
    if show_klook:
        partners.append("Klook")

    if is_kr:
        title = "관련 링크 — " + " / ".join(partners)
        bits = []
        if show_amazon:
            bits.append(
                f"「{keyword}」을 Amazon·라쿠텐에서 검색"
                if keyword
                else "Amazon·라쿠텐에서 검색"
            )
        if show_klook:
            bits.append("eSIM·교통은 Klook")
        desc = ". ".join(bits) + "."
        amazon_label = f"Amazon에서 {keyword} 검색 ↗" if keyword else ""
        rakuten_label = f"라쿠텐에서 {keyword} 검색 ↗" if keyword else ""
        klook_label = "Klook에서 eSIM·교통 보기 ↗"
        note = "제휴 링크 · 새 탭에서 열림"
    else:
        title = "Related links — " + " / ".join(partners)
        bits = []
        if show_amazon:
            bits.append(
                f"Search 「{keyword}」 on Amazon / Rakuten" if keyword else "Amazon / Rakuten"
            )
        if show_klook:
            bits.append("Klook for eSIM & transport")
        desc = ". ".join(bits) + "."
        amazon_label = f"Search {keyword} on Amazon ↗" if keyword else ""
        rakuten_label = f"Search {keyword} on Rakuten ↗" if keyword else ""
        klook_label = "eSIM & transport on Klook ↗"
        note = "Affiliate links · opens in new tab"

    return {
        "show_affiliate": True,
        "show_amazon": show_amazon,
        "show_klook": show_klook,
        "affiliate_kind": kind,
        "affiliate_keyword": keyword,
        "affiliate_title": title,
        "affiliate_desc": desc,
        "affiliate_note": note,
        "amazon_search_url": amazon_search_url(keyword) if keyword else "",
        "rakuten_search_url": rakuten_search_url(keyword) if keyword else "",
        "amazon_button_label": amazon_label,
        "rakuten_button_label": rakuten_label,
        "klook_url": KLOOK_URL if show_klook else "",
        "klook_button_label": klook_label if show_klook else "",
    }

"""Amazon Associates + Rakuten Ichiba + Klook CTAs for JP Campus.

Guides: slug maps. Schools/universities: default book + Klook. Stay: none.
No Coupang on jpcampus.
"""

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

SCHOOL_BOOK_KEYWORD = "JLPT 本"
UNIVERSITY_BOOK_KEYWORD = "EJU 本"

# Arrival / eSIM / transport / domestic travel → Klook
GUIDE_KLOOK_SLUGS: frozenset[str] = frozenset(
    {
        "sim-card-guide",
        "transport-ic",
        "transport-seed",
        "cheap-phone-accessories",
        "internet-setup",
        "soft-bank-air-vs-fiber",
        "shinkansen-deals",
        "student-travel-willerexpress",
        "capsule-hotels-etiquette",
        "train-pass",
        "golden-week",
        "onsen-etiquette",
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
    "amazon-prime-student": ("Amazonプライム 学生", "shop"),
    "hanko-guide": ("印鑑", "shop"),
    "over-the-counter-meds": ("常備薬", "shop"),
    "earthquake-prep": ("防災グッズ", "shop"),
    "typhoon-prep": ("防災グッズ", "shop"),
    "gift-giving-culture": ("お土産", "shop"),
    "internet-setup": ("ポケットWiFi", "shop"),
    "soft-bank-air-vs-fiber": ("ポケットWiFi", "shop"),
    # Housing prep (product search only — no stay operator affiliate)
    "housing": ("寝具セット", "shop"),
    "housing-seed": ("寝具セット", "shop"),
    "apartment-initial-costs": ("収納ボックス", "shop"),
    "finding-apts-online": ("収納ボックス", "shop"),
    "utilities-setup": ("延長コード", "shop"),
    "tokyo-student-housing-operators": ("寝具セット", "shop"),
    # Books / study / career
    "jlpt-levels": ("JLPT 本", "book"),
    "jlpt-seed": ("JLPT 本", "book"),
    "eju-subjects": ("EJU 本", "book"),
    "eju-jlpt": ("JLPT EJU 本", "book"),
    "job-hunting": ("就活 本", "book"),
    "resume-jp": ("履歴書 本", "book"),
    "interview-etiquette": ("面接 本", "book"),
    "internship-types-japan": ("インターンシップ 本", "book"),
    "vocational-school-deepdive": ("専門学校 進学", "book"),
}


def normalize_guide_slug(slug: str) -> str:
    s = (slug or "").strip().lower()
    if s.endswith("_kr"):
        s = s[: -len("_kr")]
    if s.startswith("guide_"):
        s = s[len("guide_") :]
    if s.startswith("school_"):
        s = s[len("school_") :]
    if s.startswith("univ_"):
        s = s[len("univ_") :]
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


def _hidden() -> dict[str, Any]:
    return {
        "show_affiliate": False,
        "show_amazon": False,
        "show_klook": False,
    }


def _build_copy(
    *,
    is_kr: bool,
    show_amazon: bool,
    show_klook: bool,
    keyword: str,
    item_type: str,
) -> dict[str, str]:
    partners: list[str] = []
    if show_amazon:
        partners.extend(["Amazon", "라쿠텐" if is_kr else "Rakuten"])
    if show_klook:
        partners.append("Klook")

    if item_type == "school":
        if is_kr:
            return {
                "title": "유학 준비 — " + " / ".join(partners),
                "desc": "JLPT 교재는 Amazon·라쿠텐, 도착용 eSIM·교통은 Klook.",
                "amazon_label": f"Amazon에서 {keyword} 검색 ↗",
                "rakuten_label": f"라쿠텐에서 {keyword} 검색 ↗",
                "klook_label": "Klook에서 eSIM·교통 보기 ↗",
                "note": "제휴 링크 · 새 탭에서 열림",
            }
        return {
            "title": "Prep links — " + " / ".join(partners),
            "desc": "JLPT books on Amazon / Rakuten. Klook for eSIM & transport.",
            "amazon_label": f"Search {keyword} on Amazon ↗",
            "rakuten_label": f"Search {keyword} on Rakuten ↗",
            "klook_label": "eSIM & transport on Klook ↗",
            "note": "Affiliate links · opens in new tab",
        }

    if item_type == "university":
        if is_kr:
            return {
                "title": "유학 준비 — " + " / ".join(partners),
                "desc": "EJU 교재는 Amazon·라쿠텐, 도착용 eSIM·교통은 Klook.",
                "amazon_label": f"Amazon에서 {keyword} 검색 ↗",
                "rakuten_label": f"라쿠텐에서 {keyword} 검색 ↗",
                "klook_label": "Klook에서 eSIM·교통 보기 ↗",
                "note": "제휴 링크 · 새 탭에서 열림",
            }
        return {
            "title": "Prep links — " + " / ".join(partners),
            "desc": "EJU books on Amazon / Rakuten. Klook for eSIM & transport.",
            "amazon_label": f"Search {keyword} on Amazon ↗",
            "rakuten_label": f"Search {keyword} on Rakuten ↗",
            "klook_label": "eSIM & transport on Klook ↗",
            "note": "Affiliate links · opens in new tab",
        }

    # guide
    if is_kr:
        bits = []
        if show_amazon:
            bits.append(
                f"「{keyword}」을 Amazon·라쿠텐에서 검색"
                if keyword
                else "Amazon·라쿠텐에서 검색"
            )
        if show_klook:
            bits.append("eSIM·교통·여행은 Klook")
        return {
            "title": "관련 링크 — " + " / ".join(partners),
            "desc": ". ".join(bits) + ".",
            "amazon_label": f"Amazon에서 {keyword} 검색 ↗" if keyword else "",
            "rakuten_label": f"라쿠텐에서 {keyword} 검색 ↗" if keyword else "",
            "klook_label": "Klook에서 eSIM·교통·여행 보기 ↗",
            "note": "제휴 링크 · 새 탭에서 열림",
        }

    bits = []
    if show_amazon:
        bits.append(
            f"Search 「{keyword}」 on Amazon / Rakuten" if keyword else "Amazon / Rakuten"
        )
    if show_klook:
        bits.append("Klook for eSIM, transport & trips")
    return {
        "title": "Related links — " + " / ".join(partners),
        "desc": ". ".join(bits) + ".",
        "amazon_label": f"Search {keyword} on Amazon ↗" if keyword else "",
        "rakuten_label": f"Search {keyword} on Rakuten ↗" if keyword else "",
        "klook_label": "eSIM, transport & trips on Klook ↗",
        "note": "Affiliate links · opens in new tab",
    }


def affiliate_context(
    slug: str = "",
    *,
    lang: str = "en",
    item_type: str = "guide",
) -> dict[str, Any]:
    """Amazon/Rakuten (mapped or school/univ default) + Klook. Stay → hidden."""
    kind_raw = (item_type or "guide").strip().lower()
    if kind_raw == "stay":
        return _hidden()

    is_kr = (lang or "en").lower() in ("kr", "ko")
    key = normalize_guide_slug(slug)

    if kind_raw in ("school", "university"):
        show_amazon = True
        show_klook = True
        keyword = (
            SCHOOL_BOOK_KEYWORD if kind_raw == "school" else UNIVERSITY_BOOK_KEYWORD
        )
        kind = "book"
    else:
        mapped = GUIDE_AFFILIATE_MAP.get(key)
        show_amazon = bool(mapped)
        keyword, kind = mapped if mapped else ("", "shop")
        show_klook = key in GUIDE_KLOOK_SLUGS

    if not show_amazon and not show_klook:
        return _hidden()

    copy = _build_copy(
        is_kr=is_kr,
        show_amazon=show_amazon,
        show_klook=show_klook,
        keyword=keyword,
        item_type=kind_raw if kind_raw in ("school", "university") else "guide",
    )

    return {
        "show_affiliate": True,
        "show_amazon": show_amazon,
        "show_klook": show_klook,
        "affiliate_kind": kind,
        "affiliate_keyword": keyword,
        "affiliate_title": copy["title"],
        "affiliate_desc": copy["desc"],
        "affiliate_note": copy["note"],
        "amazon_search_url": amazon_search_url(keyword) if keyword else "",
        "rakuten_search_url": rakuten_search_url(keyword) if keyword else "",
        "amazon_button_label": copy["amazon_label"] if show_amazon else "",
        "rakuten_button_label": copy["rakuten_label"] if show_amazon else "",
        "klook_url": KLOOK_URL if show_klook else "",
        "klook_button_label": copy["klook_label"] if show_klook else "",
    }

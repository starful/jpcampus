"""Amazon Associates + Rakuten Ichiba + Klook + KO Coupang / JP eSIM for JP Campus.

Guides: slug maps. Schools/universities: default book + Klook (EN) or JP eSIM (KO).
KO UI: no Klook — Coupang + Rakuten JP eSIM instead.
"""

from __future__ import annotations

import os
from typing import Any, Literal
from urllib.parse import quote, quote_plus

AMAZON_TAG = os.getenv("AMAZON_ASSOCIATE_TAG", "starful06-22")
RAKUTEN_HGC = os.getenv(
    "RAKUTEN_ICHIBA_HGC", "43cde6d2.98a376f7.43cde6d3.c7b92630"
)
_RAKUTEN_UT = "eyJwYWdlIjoidXJsIiwidHlwZSI6InRleHQiLCJjb2wiOjF9"

COUPANG_DISCLOSURE_KO = (
    "이 포스팅은 쿠팡 파트너스 활동의 일환으로, "
    "이에 따른 일정액의 수수료를 제공받습니다."
)
_COUPANG = {
    "travel": "https://link.coupang.com/a/f289Oxl1hI",
    "shop": "https://link.coupang.com/a/f29dMP4AEe",
}

# Rakuten JP eSIM short link (KO UI only — replaces Klook on Korean).
JP_ESIM_URL = "https://a.r10.to/hPsyyI"

KlookIntent = Literal["esim", "transport", "fallback"]

# Travelpayouts jpcampus project — do not reuse krcampus / okonsen short links.
KLOOK_URLS: dict[str, str] = {
    "esim_en": "https://klook.tpo.mx/G3Ubatko",
    "esim_ko": "https://klook.tpo.mx/v1ZEX82k",
    "transport_en": "https://klook.tpo.mx/ZFlCQaio",
    "transport_ko": "https://klook.tpo.mx/UkhBXMaj",
    "fallback_en": "https://klook.tpo.mx/YUPTrdhU",
    # No dedicated KO fallback issued — reuse transport_ko.
    "fallback_ko": "https://klook.tpo.mx/UkhBXMaj",
}

# Back-compat: default / generic landing.
KLOOK_URL = os.getenv("KLOOK_URL", KLOOK_URLS["fallback_en"])

SCHOOL_BOOK_KEYWORD = "JLPT N2 問題集"
UNIVERSITY_BOOK_KEYWORD = "EJU 問題集"

GUIDE_KLOOK_ESIM: frozenset[str] = frozenset(
    {
        "sim-card-guide",
        "cheap-phone-accessories",
        "internet-setup",
        "soft-bank-air-vs-fiber",
    }
)
GUIDE_KLOOK_TRANSPORT: frozenset[str] = frozenset(
    {
        "transport-ic",
        "transport-seed",
        "shinkansen-deals",
        "student-travel-willerexpress",
        "train-pass",
    }
)
GUIDE_KLOOK_FALLBACK: frozenset[str] = frozenset(
    {
        "capsule-hotels-etiquette",
        "golden-week",
        "onsen-etiquette",
    }
)

# Arrival / eSIM / transport / domestic travel → Klook
GUIDE_KLOOK_SLUGS: frozenset[str] = (
    GUIDE_KLOOK_ESIM | GUIDE_KLOOK_TRANSPORT | GUIDE_KLOOK_FALLBACK
)

# guide slug (without _kr) → search keyword + kind
# kind: "shop" | "book"
GUIDE_AFFILIATE_MAP: dict[str, tuple[str, str]] = {
    # Shopping / lifestyle — buyable JP keywords
    "sim-card-guide": ("ポケットWiFi レンタル", "shop"),
    "drugstore-skincare-guide": ("スキンケア 化粧水", "shop"),
    "cheap-phone-accessories": ("モバイルバッテリー", "shop"),
    "costco-japan-membership": ("クーラーボックス", "shop"),
    "thrift-stores-furniture": ("収納ボックス", "shop"),
    "glasses-jins-zoff": ("ブルーライトカット メガネ", "shop"),
    "100-yen-stores": ("キッチン用品 セット", "shop"),
    "humidity-mold-prevention": ("除湿機", "shop"),
    "winter-room-heating": ("セラミックヒーター", "shop"),
    "bicycle-rules": ("自転車 ヘルメット", "shop"),
    "bicycle-parking": ("自転車 鍵", "shop"),
    "bicycle-insurance-law": ("自転車 保険", "shop"),
    "amazon-prime-student": ("Amazonプライム", "shop"),
    "hanko-guide": ("認印", "shop"),
    "over-the-counter-meds": ("常備薬 セット", "shop"),
    "earthquake-prep": ("防災セット", "shop"),
    "typhoon-prep": ("防災セット", "shop"),
    "gift-giving-culture": ("手土産 お菓子", "shop"),
    "internet-setup": ("ポケットWiFi", "shop"),
    "soft-bank-air-vs-fiber": ("ポケットWiFi", "shop"),
    # Housing prep (product search only — no stay operator affiliate)
    "housing": ("寝具セット シングル", "shop"),
    "housing-seed": ("寝具セット シングル", "shop"),
    "apartment-initial-costs": ("掃除用具 セット", "shop"),
    "finding-apts-online": ("収納ボックス", "shop"),
    "utilities-setup": ("延長コード 電源タップ", "shop"),
    "tokyo-student-housing-operators": ("寝具セット シングル", "shop"),
    # Books / study / career
    "jlpt-levels": ("JLPT N2 問題集", "book"),
    "jlpt-seed": ("JLPT N2 問題集", "book"),
    "eju-subjects": ("EJU 問題集", "book"),
    "eju-jlpt": ("JLPT EJU 問題集", "book"),
    "job-hunting": ("就活 自己分析 本", "book"),
    "resume-jp": ("履歴書 書き方", "book"),
    "interview-etiquette": ("面接 対策 本", "book"),
    "internship-types-japan": ("インターンシップ 本", "book"),
    "vocational-school-deepdive": ("専門学校 進路 本", "book"),
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


def resolve_klook_intent(
    slug: str = "",
    *,
    item_type: str = "guide",
) -> KlookIntent:
    kind = (item_type or "guide").strip().lower()
    if kind in ("school", "university"):
        return "esim"
    if kind == "stay":
        return "transport"
    key = normalize_guide_slug(slug)
    if key in GUIDE_KLOOK_ESIM:
        return "esim"
    if key in GUIDE_KLOOK_TRANSPORT:
        return "transport"
    return "fallback"


def klook_url_for(
    slug: str = "",
    *,
    lang: str = "en",
    item_type: str = "guide",
) -> str:
    intent = resolve_klook_intent(slug, item_type=item_type)
    is_kr = (lang or "en").lower() in ("kr", "ko")
    suffix = "ko" if is_kr else "en"
    return KLOOK_URLS[f"{intent}_{suffix}"]


def resolve_coupang_intent(*, affiliate_kind: str, show_amazon: bool) -> str:
    """shop/book Amazon CTAs → shop prep; travel / Klook-only → travel."""
    if affiliate_kind in ("shop", "book") or show_amazon:
        return "shop"
    return "travel"


def coupang_url_for(*, affiliate_kind: str, show_amazon: bool) -> str:
    return _COUPANG[
        resolve_coupang_intent(affiliate_kind=affiliate_kind, show_amazon=show_amazon)
    ]


def _hidden() -> dict[str, Any]:
    return {
        "show_affiliate": False,
        "show_amazon": False,
        "show_klook": False,
        "show_coupang": False,
        "show_jp_esim": False,
        "coupang_url": "",
        "coupang_button_label": "",
        "coupang_disclosure": "",
        "jp_esim_url": "",
        "jp_esim_button_label": "",
    }


def _build_copy(
    *,
    is_kr: bool,
    show_amazon: bool,
    show_klook: bool,
    show_coupang: bool,
    show_jp_esim: bool,
    keyword: str,
    item_type: str,
) -> dict[str, str]:
    partners: list[str] = []
    if show_amazon:
        partners.extend(["Amazon", "라쿠텐" if is_kr else "Rakuten"])
    if show_coupang:
        partners.append("쿠팡" if is_kr else "Coupang")
    if show_jp_esim:
        partners.append("일본 eSIM" if is_kr else "JP eSIM")
    if show_klook:
        partners.append("Klook")

    if item_type == "school":
        if is_kr:
            bits = ["JLPT 교재는 Amazon·라쿠텐", "준비물은 쿠팡"]
            if show_jp_esim:
                bits.append("도착용 eSIM은 라쿠텐")
            return {
                "title": "유학 준비 — " + " / ".join(partners),
                "desc": ", ".join(bits) + ".",
                "amazon_label": f"Amazon에서 {keyword} 검색 ↗",
                "rakuten_label": f"라쿠텐에서 {keyword} 검색 ↗",
                "coupang_label": "쿠팡에서 유학 준비물 보기 ↗",
                "jp_esim_label": "라쿠텐에서 일본 eSIM 보기 ↗",
                "klook_label": "",
                "note": "제휴 링크 · 새 탭에서 열림",
            }
        return {
            "title": "Prep links — " + " / ".join(partners),
            "desc": "JLPT books on Amazon / Rakuten. Klook for eSIM & transport.",
            "amazon_label": f"Search {keyword} on Amazon ↗",
            "rakuten_label": f"Search {keyword} on Rakuten ↗",
            "coupang_label": "",
            "jp_esim_label": "",
            "klook_label": "eSIM & transport on Klook ↗",
            "note": "Affiliate links · opens in new tab",
        }

    if item_type == "university":
        if is_kr:
            bits = ["EJU 교재는 Amazon·라쿠텐", "준비물은 쿠팡"]
            if show_jp_esim:
                bits.append("도착용 eSIM은 라쿠텐")
            return {
                "title": "유학 준비 — " + " / ".join(partners),
                "desc": ", ".join(bits) + ".",
                "amazon_label": f"Amazon에서 {keyword} 검색 ↗",
                "rakuten_label": f"라쿠텐에서 {keyword} 검색 ↗",
                "coupang_label": "쿠팡에서 유학 준비물 보기 ↗",
                "jp_esim_label": "라쿠텐에서 일본 eSIM 보기 ↗",
                "klook_label": "",
                "note": "제휴 링크 · 새 탭에서 열림",
            }
        return {
            "title": "Prep links — " + " / ".join(partners),
            "desc": "EJU books on Amazon / Rakuten. Klook for eSIM & transport.",
            "amazon_label": f"Search {keyword} on Amazon ↗",
            "rakuten_label": f"Search {keyword} on Rakuten ↗",
            "coupang_label": "",
            "jp_esim_label": "",
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
        if show_coupang:
            bits.append("여행·준비물은 쿠팡")
        if show_jp_esim:
            bits.append("일본 eSIM은 라쿠텐")
        return {
            "title": "관련 링크 — " + " / ".join(partners),
            "desc": ". ".join(bits) + ".",
            "amazon_label": f"Amazon에서 {keyword} 검색 ↗" if keyword else "",
            "rakuten_label": f"라쿠텐에서 {keyword} 검색 ↗" if keyword else "",
            "coupang_label": (
                "쿠팡에서 준비물 보기 ↗"
                if show_amazon
                else "쿠팡트래블에서 여행 보기 ↗"
            ),
            "jp_esim_label": "라쿠텐에서 일본 eSIM 보기 ↗",
            "klook_label": "",
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
        "coupang_label": "",
        "jp_esim_label": "",
        "klook_label": "eSIM, transport & trips on Klook ↗",
        "note": "Affiliate links · opens in new tab",
    }


def affiliate_context(
    slug: str = "",
    *,
    lang: str = "en",
    item_type: str = "guide",
) -> dict[str, Any]:
    """Amazon/Rakuten + Klook (EN) or Coupang + JP eSIM (KO)."""
    kind_raw = (item_type or "guide").strip().lower()
    is_kr = (lang or "en").lower() in ("kr", "ko")
    key = normalize_guide_slug(slug)
    klook = klook_url_for(slug, lang=lang, item_type=kind_raw)

    if kind_raw == "stay":
        if is_kr:
            return {
                "show_affiliate": True,
                "show_amazon": False,
                "show_klook": False,
                "show_coupang": True,
                "show_jp_esim": True,
                "affiliate_kind": "travel",
                "affiliate_keyword": "",
                "affiliate_title": "유학 준비 — 쿠팡 / 일본 eSIM",
                "affiliate_desc": "여행·숙소는 쿠팡트래블, 도착용 eSIM은 라쿠텐.",
                "affiliate_note": "제휴 링크 · 새 탭에서 열림",
                "amazon_search_url": "",
                "rakuten_search_url": "",
                "amazon_button_label": "",
                "rakuten_button_label": "",
                "coupang_url": _COUPANG["travel"],
                "coupang_button_label": "쿠팡트래블에서 여행 보기 ↗",
                "coupang_disclosure": COUPANG_DISCLOSURE_KO,
                "jp_esim_url": JP_ESIM_URL,
                "jp_esim_button_label": "라쿠텐에서 일본 eSIM 보기 ↗",
                "klook_url": "",
                "klook_button_label": "",
            }
        return {
            "show_affiliate": True,
            "show_amazon": False,
            "show_klook": True,
            "show_coupang": False,
            "show_jp_esim": False,
            "affiliate_kind": "travel",
            "affiliate_keyword": "",
            "affiliate_title": "Prep links — Klook",
            "affiliate_desc": "Klook for eSIM, transport, and arrival essentials.",
            "affiliate_note": "Affiliate links · opens in new tab",
            "amazon_search_url": "",
            "rakuten_search_url": "",
            "amazon_button_label": "",
            "rakuten_button_label": "",
            "coupang_url": "",
            "coupang_button_label": "",
            "coupang_disclosure": "",
            "jp_esim_url": "",
            "jp_esim_button_label": "",
            "klook_url": klook,
            "klook_button_label": "eSIM & transport on Klook ↗",
        }

    mapped_klook = False
    if kind_raw in ("school", "university"):
        show_amazon = True
        mapped_klook = True
        keyword = (
            SCHOOL_BOOK_KEYWORD if kind_raw == "school" else UNIVERSITY_BOOK_KEYWORD
        )
        kind = "book"
    else:
        mapped = GUIDE_AFFILIATE_MAP.get(key)
        show_amazon = bool(mapped)
        if mapped:
            keyword, kind = mapped
        else:
            keyword, kind = "", "travel"
        mapped_klook = key in GUIDE_KLOOK_SLUGS

    show_klook = mapped_klook and not is_kr
    # KO eSIM only when Amazon shop/book CTAs are absent (avoid 4 buttons).
    show_jp_esim = is_kr and not show_amazon and mapped_klook
    show_coupang = is_kr and (show_amazon or mapped_klook)

    if not show_amazon and not show_klook and not show_jp_esim and not show_coupang:
        return _hidden()

    copy = _build_copy(
        is_kr=is_kr,
        show_amazon=show_amazon,
        show_klook=show_klook,
        show_coupang=show_coupang,
        show_jp_esim=show_jp_esim,
        keyword=keyword,
        item_type=kind_raw if kind_raw in ("school", "university") else "guide",
    )
    coupang_url = (
        coupang_url_for(affiliate_kind=kind, show_amazon=show_amazon)
        if show_coupang
        else ""
    )

    return {
        "show_affiliate": True,
        "show_amazon": show_amazon,
        "show_klook": show_klook,
        "show_coupang": show_coupang,
        "show_jp_esim": show_jp_esim,
        "affiliate_kind": kind,
        "affiliate_keyword": keyword,
        "affiliate_title": copy["title"],
        "affiliate_desc": copy["desc"],
        "affiliate_note": copy["note"],
        "amazon_search_url": amazon_search_url(keyword) if keyword else "",
        "rakuten_search_url": rakuten_search_url(keyword) if keyword else "",
        "amazon_button_label": copy["amazon_label"] if show_amazon else "",
        "rakuten_button_label": copy["rakuten_label"] if show_amazon else "",
        "coupang_url": coupang_url,
        "coupang_button_label": copy["coupang_label"] if show_coupang else "",
        "coupang_disclosure": COUPANG_DISCLOSURE_KO if show_coupang else "",
        "jp_esim_url": JP_ESIM_URL if show_jp_esim else "",
        "jp_esim_button_label": copy["jp_esim_label"] if show_jp_esim else "",
        "klook_url": klook if show_klook else "",
        "klook_button_label": copy["klook_label"] if show_klook else "",
    }

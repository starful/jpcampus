"""Rakuten Ichiba + JP eSIM affiliate CTAs for JP Campus."""

from __future__ import annotations

import os
from typing import Any
from urllib.parse import quote

RAKUTEN_HGC = os.getenv(
    "RAKUTEN_ICHIBA_HGC", "43cde6d2.98a376f7.43cde6d3.c7b92630"
)
_RAKUTEN_UT = "eyJwYWdlIjoidXJsIiwidHlwZSI6InRleHQiLCJjb2wiOjF9"

JP_ESIM_URL = "https://a.r10.to/hPsyyI"

SCHOOL_BOOK_KEYWORD = "JLPT N2 問題集"
UNIVERSITY_BOOK_KEYWORD = "EJU 問題集"

GUIDE_PREP_ESIM: frozenset[str] = frozenset(
    {
        "sim-card-guide",
        "cheap-phone-accessories",
        "internet-setup",
        "soft-bank-air-vs-fiber",
    }
)

GUIDE_AFFILIATE_MAP: dict[str, tuple[str, str]] = {
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
    "hanko-guide": ("認印", "shop"),
    "over-the-counter-meds": ("常備薬 セット", "shop"),
    "earthquake-prep": ("防災セット", "shop"),
    "typhoon-prep": ("防災セット", "shop"),
    "gift-giving-culture": ("手土産 お菓子", "shop"),
    "internet-setup": ("ポケットWiFi", "shop"),
    "soft-bank-air-vs-fiber": ("ポケットWiFi", "shop"),
    "housing": ("寝具セット シングル", "shop"),
    "housing-seed": ("寝具セット シングル", "shop"),
    "apartment-initial-costs": ("掃除用具 セット", "shop"),
    "finding-apts-online": ("収納ボックス", "shop"),
    "utilities-setup": ("延長コード 電源タップ", "shop"),
    "tokyo-student-housing-operators": ("寝具セット シングル", "shop"),
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


def rakuten_search_url(keyword: str) -> str:
    dest = f"https://search.rakuten.co.jp/search/mall/{quote(keyword, safe='')}/"
    pc = quote(dest, safe="")
    return (
        f"https://hb.afl.rakuten.co.jp/hgc/{RAKUTEN_HGC}/"
        f"?pc={pc}&link_type=text&ut={_RAKUTEN_UT}"
    )


def _hidden() -> dict[str, Any]:
    return {
        "show_affiliate": False,
        "show_rakuten": False,
        "show_jp_esim": False,
        "jp_esim_url": "",
        "jp_esim_button_label": "",
    }


def affiliate_context(
    slug: str = "",
    *,
    lang: str = "en",
    item_type: str = "guide",
) -> dict[str, Any]:
    """Rakuten Ichiba (shop/book) + JP eSIM for KO prep guides."""
    kind_raw = (item_type or "guide").strip().lower()
    is_kr = (lang or "en").lower() in ("kr", "ko")
    key = normalize_guide_slug(slug)

    if kind_raw == "stay":
        if is_kr:
            return {
                "show_affiliate": True,
                "show_rakuten": False,
                "show_jp_esim": True,
                "affiliate_kind": "travel",
                "affiliate_keyword": "",
                "affiliate_title": "유학 준비 — 일본 eSIM",
                "affiliate_desc": "도착용 eSIM은 라쿠텐.",
                "affiliate_note": "제휴 링크 · 새 탭에서 열림",
                "rakuten_search_url": "",
                "rakuten_button_label": "",
                "jp_esim_url": JP_ESIM_URL,
                "jp_esim_button_label": "라쿠텐에서 일본 eSIM 보기 ↗",
            }
        return _hidden()

    if kind_raw in ("school", "university"):
        keyword = (
            SCHOOL_BOOK_KEYWORD if kind_raw == "school" else UNIVERSITY_BOOK_KEYWORD
        )
        show_jp_esim = is_kr
        if is_kr:
            return {
                "show_affiliate": True,
                "show_rakuten": True,
                "show_jp_esim": show_jp_esim,
                "affiliate_kind": "book",
                "affiliate_keyword": keyword,
                "affiliate_title": "유학 준비 — 라쿠텐",
                "affiliate_desc": f"교재는 라쿠텐, eSIM은 라쿠텐.",
                "affiliate_note": "제휴 링크 · 새 탭에서 열림",
                "rakuten_search_url": rakuten_search_url(keyword),
                "rakuten_button_label": f"라쿠텐에서 {keyword} 검색 ↗",
                "jp_esim_url": JP_ESIM_URL if show_jp_esim else "",
                "jp_esim_button_label": (
                    "라쿠텐에서 일본 eSIM 보기 ↗" if show_jp_esim else ""
                ),
            }
        return {
            "show_affiliate": True,
            "show_rakuten": True,
            "show_jp_esim": False,
            "affiliate_kind": "book",
            "affiliate_keyword": keyword,
            "affiliate_title": f"Prep links — Rakuten",
            "affiliate_desc": f"Search {keyword} on Rakuten Ichiba.",
            "affiliate_note": "Affiliate links · opens in new tab",
            "rakuten_search_url": rakuten_search_url(keyword),
            "rakuten_button_label": f"Search {keyword} on Rakuten ↗",
            "jp_esim_url": "",
            "jp_esim_button_label": "",
        }

    mapped = GUIDE_AFFILIATE_MAP.get(key)
    show_rakuten = bool(mapped)
    show_jp_esim = is_kr and key in GUIDE_PREP_ESIM and not show_rakuten

    if not show_rakuten and not show_jp_esim:
        return _hidden()

    keyword, kind = mapped if mapped else ("", "travel")
    if is_kr:
        bits = []
        if show_rakuten:
            bits.append(
                f"「{keyword}」을 라쿠텐에서 검색" if keyword else "라쿠텐에서 검색"
            )
        if show_jp_esim:
            bits.append("일본 eSIM은 라쿠텐")
        return {
            "show_affiliate": True,
            "show_rakuten": show_rakuten,
            "show_jp_esim": show_jp_esim,
            "affiliate_kind": kind,
            "affiliate_keyword": keyword,
            "affiliate_title": "관련 링크 — 라쿠텐",
            "affiliate_desc": ". ".join(bits) + "." if bits else "",
            "affiliate_note": "제휴 링크 · 새 탭에서 열림",
            "rakuten_search_url": rakuten_search_url(keyword) if show_rakuten else "",
            "rakuten_button_label": (
                f"라쿠텐에서 {keyword} 검색 ↗" if show_rakuten else ""
            ),
            "jp_esim_url": JP_ESIM_URL if show_jp_esim else "",
            "jp_esim_button_label": (
                "라쿠텐에서 일본 eSIM 보기 ↗" if show_jp_esim else ""
            ),
        }

    return {
        "show_affiliate": True,
        "show_rakuten": show_rakuten,
        "show_jp_esim": False,
        "affiliate_kind": kind,
        "affiliate_keyword": keyword,
        "affiliate_title": "Related links — Rakuten",
        "affiliate_desc": (
            f"Search 「{keyword}」 on Rakuten." if keyword else "Rakuten Ichiba."
        ),
        "affiliate_note": "Affiliate links · opens in new tab",
        "rakuten_search_url": rakuten_search_url(keyword) if show_rakuten else "",
        "rakuten_button_label": f"Search {keyword} on Rakuten ↗" if keyword else "",
        "jp_esim_url": "",
        "jp_esim_button_label": "",
    }

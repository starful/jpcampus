"""Affiliate slug → keyword / Klook / KO Coupang for JP Campus."""

from app.affiliate import (
    GUIDE_KLOOK_SLUGS,
    KLOOK_URL,
    KLOOK_URLS,
    SCHOOL_BOOK_KEYWORD,
    UNIVERSITY_BOOK_KEYWORD,
    affiliate_context,
    amazon_search_url,
    klook_url_for,
    normalize_guide_slug,
    rakuten_search_url,
    resolve_klook_intent,
)


def test_normalize_strips_kr_and_guide_prefix():
    assert normalize_guide_slug("sim-card-guide_kr") == "sim-card-guide"
    assert normalize_guide_slug("guide_jlpt-levels") == "jlpt-levels"
    assert normalize_guide_slug("school_foo") == "foo"
    assert normalize_guide_slug("univ_bar") == "bar"


def test_shopping_guide_context():
    ctx = affiliate_context("sim-card-guide", lang="en")
    assert ctx["show_affiliate"] is True
    assert ctx["affiliate_kind"] == "shop"
    assert "ポケットWiFi" in ctx["affiliate_keyword"]
    assert "amazon.co.jp/s?k=" in ctx["amazon_search_url"]
    assert "starful06-22" in ctx["amazon_search_url"]
    assert "hb.afl.rakuten.co.jp/hgc/" in ctx["rakuten_search_url"]
    assert "search.rakuten.co.jp" in ctx["rakuten_search_url"]
    assert ctx["show_klook"] is True
    assert ctx["klook_url"] == KLOOK_URLS["esim_en"]
    assert ctx["show_coupang"] is False


def test_book_guide_korean_copy():
    ctx = affiliate_context("jlpt-levels_kr", lang="kr")
    assert ctx["show_affiliate"] is True
    assert ctx["affiliate_kind"] == "book"
    assert "JLPT" in ctx["amazon_button_label"]
    assert "Amazon" in ctx["affiliate_desc"]
    assert "라쿠텐" in ctx["affiliate_desc"]
    assert ctx["show_klook"] is False
    assert ctx["show_coupang"] is True
    assert "f29dMP4AEe" in ctx["coupang_url"]
    assert "쿠팡 파트너스" in ctx["coupang_disclosure"]


def test_housing_guide_shows_coupang_shop_on_ko():
    ctx = affiliate_context("housing", lang="kr", item_type="guide")
    assert ctx["show_affiliate"] is True
    assert ctx["show_amazon"] is True
    assert "寝具" in ctx["affiliate_keyword"]
    assert ctx["show_coupang"] is True
    assert "f29dMP4AEe" in ctx["coupang_url"]
    ctx_en = affiliate_context("housing", lang="en", item_type="guide")
    assert ctx_en["show_coupang"] is False


def test_stay_page_shows_klook_only():
    ctx = affiliate_context("oakhouse_1164", lang="en", item_type="stay")
    assert ctx["show_affiliate"] is True
    assert ctx["show_klook"] is True
    assert ctx["show_amazon"] is False
    assert ctx["klook_url"] == KLOOK_URLS["transport_en"]
    assert ctx["show_coupang"] is False


def test_stay_page_ko_shows_coupang_travel():
    ctx = affiliate_context("oakhouse_1164", lang="kr", item_type="stay")
    assert ctx["show_coupang"] is True
    assert ctx["show_klook"] is False
    assert ctx["show_jp_esim"] is True
    assert "f289Oxl1hI" in ctx["coupang_url"]
    assert "hPsyyI" in ctx["jp_esim_url"]
    assert "쿠팡 파트너스" in ctx["coupang_disclosure"]


def test_transport_shows_klook_only_partners():
    ctx = affiliate_context("transport-seed", lang="en")
    assert ctx["show_affiliate"] is True
    assert ctx["show_klook"] is True
    assert ctx["show_amazon"] is False
    assert ctx["klook_url"] == KLOOK_URLS["transport_en"]


def test_travel_guide_ko_uses_coupang_travel():
    ctx = affiliate_context("shinkansen-deals", lang="kr")
    assert ctx["show_klook"] is False
    assert ctx["show_amazon"] is False
    assert ctx["affiliate_kind"] == "travel"
    assert ctx["show_coupang"] is True
    assert ctx["show_jp_esim"] is True
    assert "f289Oxl1hI" in ctx["coupang_url"]
    assert "hPsyyI" in ctx["jp_esim_url"]


def test_travel_guide_shows_klook():
    ctx = affiliate_context("shinkansen-deals", lang="en")
    assert ctx["show_klook"] is True
    assert ctx["show_amazon"] is False
    assert ctx["klook_url"] == KLOOK_URLS["transport_en"]


def test_prime_guide_shows_amazon():
    ctx = affiliate_context("amazon-prime-student", lang="en")
    assert ctx["show_amazon"] is True
    assert ctx["show_klook"] is False


def test_school_default_jlpt_and_klook():
    ctx = affiliate_context("school_abc", lang="en", item_type="school")
    assert ctx["show_affiliate"] is True
    assert ctx["affiliate_kind"] == "book"
    assert ctx["affiliate_keyword"] == SCHOOL_BOOK_KEYWORD
    assert ctx["show_klook"] is True
    assert ctx["klook_url"] == KLOOK_URLS["esim_en"]


def test_university_default_eju_and_klook():
    ctx = affiliate_context("univ_xyz", lang="kr", item_type="university")
    assert ctx["show_affiliate"] is True
    assert ctx["affiliate_keyword"] == UNIVERSITY_BOOK_KEYWORD
    assert ctx["show_klook"] is False
    assert ctx["show_jp_esim"] is True
    assert "hPsyyI" in ctx["jp_esim_url"]
    assert ctx["show_coupang"] is True
    assert "f29dMP4AEe" in ctx["coupang_url"]


def test_unmapped_guide_hides_box():
    ctx = affiliate_context("visa-seed", lang="en")
    assert ctx["show_affiliate"] is False


def test_url_builders():
    assert "tag=starful06-22" in amazon_search_url("JLPT 本")
    assert "%2520" in rakuten_search_url("JLPT 本") or "%20" in rakuten_search_url(
        "JLPT 本"
    )


def test_klook_intents_are_jpcampus_only():
    assert "ED7IfKaq" not in KLOOK_URL
    assert "YUPTrdhU" in KLOOK_URL
    for slug in GUIDE_KLOOK_SLUGS:
        ctx = affiliate_context(slug, lang="en")
        assert "klook.tpo.mx" in ctx["klook_url"]
        assert ctx["klook_url"] in KLOOK_URLS.values()
    assert resolve_klook_intent("sim-card-guide") == "esim"
    assert resolve_klook_intent("transport-ic") == "transport"
    assert klook_url_for("onsen-etiquette", lang="en") == KLOOK_URLS["fallback_en"]
    assert klook_url_for("sim-card-guide", lang="kr") == KLOOK_URLS["esim_ko"]

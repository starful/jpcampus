"""Affiliate slug → keyword / Klook for JP Campus (no Coupang; stay skipped)."""

from app.affiliate import (
    GUIDE_KLOOK_SLUGS,
    KLOOK_URL,
    SCHOOL_BOOK_KEYWORD,
    UNIVERSITY_BOOK_KEYWORD,
    affiliate_context,
    amazon_search_url,
    normalize_guide_slug,
    rakuten_search_url,
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
    assert ctx["affiliate_keyword"] == "格安SIM"
    assert "amazon.co.jp/s?k=" in ctx["amazon_search_url"]
    assert "starful06-22" in ctx["amazon_search_url"]
    assert "hb.afl.rakuten.co.jp/hgc/" in ctx["rakuten_search_url"]
    assert "search.rakuten.co.jp" in ctx["rakuten_search_url"]
    assert ctx["show_klook"] is True
    assert ctx["klook_url"] == KLOOK_URL
    assert "s8kswiYD" in ctx["klook_url"]


def test_book_guide_korean_copy():
    ctx = affiliate_context("jlpt-levels_kr", lang="kr")
    assert ctx["show_affiliate"] is True
    assert ctx["affiliate_kind"] == "book"
    assert "JLPT 本" in ctx["amazon_button_label"]
    assert "Amazon" in ctx["affiliate_desc"]
    assert "라쿠텐" in ctx["affiliate_desc"]
    assert ctx["show_klook"] is False


def test_housing_guide_shows_amazon_not_coupang():
    ctx = affiliate_context("housing", lang="kr", item_type="guide")
    assert ctx["show_affiliate"] is True
    assert ctx["show_amazon"] is True
    assert "寝具" in ctx["affiliate_keyword"]
    assert "coupang" not in ctx["amazon_search_url"].lower()


def test_stay_page_hides_affiliate():
    ctx = affiliate_context("oakhouse_1164", lang="en", item_type="stay")
    assert ctx["show_affiliate"] is False


def test_transport_shows_klook_only_partners():
    ctx = affiliate_context("transport-seed", lang="en")
    assert ctx["show_affiliate"] is True
    assert ctx["show_klook"] is True
    assert ctx["show_amazon"] is False
    assert "s8kswiYD" in ctx["klook_url"]


def test_travel_guide_shows_klook():
    ctx = affiliate_context("shinkansen-deals", lang="en")
    assert ctx["show_klook"] is True
    assert ctx["show_amazon"] is False


def test_prime_guide_shows_amazon():
    ctx = affiliate_context("amazon-prime-student", lang="en")
    assert ctx["show_affiliate"] is True
    assert ctx["show_amazon"] is True
    assert "プライム" in ctx["affiliate_keyword"]


def test_school_default_jlpt_and_klook():
    ctx = affiliate_context("school_kokusai-nihongo-gakuin", lang="en", item_type="school")
    assert ctx["show_affiliate"] is True
    assert ctx["show_amazon"] is True
    assert ctx["show_klook"] is True
    assert ctx["affiliate_keyword"] == SCHOOL_BOOK_KEYWORD
    assert "s8kswiYD" in ctx["klook_url"]


def test_university_default_eju_and_klook():
    ctx = affiliate_context("univ_waseda", lang="kr", item_type="university")
    assert ctx["show_affiliate"] is True
    assert ctx["affiliate_keyword"] == UNIVERSITY_BOOK_KEYWORD
    assert "EJU" in ctx["affiliate_desc"]
    assert ctx["show_klook"] is True


def test_unmapped_guide_hides_box():
    ctx = affiliate_context("visa-seed", lang="en")
    assert ctx["show_affiliate"] is False


def test_url_builders():
    assert "tag=starful06-22" in amazon_search_url("JLPT 本")
    assert "%2520" in rakuten_search_url("JLPT 本") or "%20" in rakuten_search_url("JLPT 本")


def test_klook_url_is_jpcampus_only():
    assert "ED7IfKaq" not in KLOOK_URL
    assert "s8kswiYD" in KLOOK_URL
    for slug in GUIDE_KLOOK_SLUGS:
        ctx = affiliate_context(slug, lang="en")
        assert ctx["klook_url"] == KLOOK_URL

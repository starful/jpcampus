"""Affiliate slug → keyword / Klook for JP Campus guides (no Coupang)."""

from app.affiliate import (
    GUIDE_KLOOK_SLUGS,
    KLOOK_URL,
    affiliate_context,
    amazon_search_url,
    normalize_guide_slug,
    rakuten_search_url,
)


def test_normalize_strips_kr_and_guide_prefix():
    assert normalize_guide_slug("sim-card-guide_kr") == "sim-card-guide"
    assert normalize_guide_slug("guide_jlpt-levels") == "jlpt-levels"


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


def test_housing_no_coupang():
    ctx = affiliate_context("housing", lang="kr")
    assert ctx["show_affiliate"] is False


def test_transport_shows_klook_only_partners():
    ctx = affiliate_context("transport-seed", lang="en")
    assert ctx["show_affiliate"] is True
    assert ctx["show_klook"] is True
    assert ctx["show_amazon"] is False
    assert "s8kswiYD" in ctx["klook_url"]


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

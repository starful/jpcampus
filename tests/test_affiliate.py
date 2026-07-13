"""Affiliate slug → keyword mapping for JP Campus guides."""

from app.affiliate import (
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


def test_book_guide_korean_copy():
    ctx = affiliate_context("jlpt-levels_kr", lang="kr")
    assert ctx["show_affiliate"] is True
    assert ctx["affiliate_kind"] == "book"
    assert "JLPT 本" in ctx["amazon_button_label"]
    assert "새 탭" in ctx["affiliate_desc"]


def test_unmapped_guide_hides_box():
    ctx = affiliate_context("visa-seed", lang="en")
    assert ctx["show_affiliate"] is False


def test_url_builders():
    assert "tag=starful06-22" in amazon_search_url("JLPT 本")
    assert "%2520" in rakuten_search_url("JLPT 本") or "%20" in rakuten_search_url("JLPT 本")

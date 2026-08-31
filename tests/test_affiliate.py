"""JP Campus affiliate: Rakuten + JP eSIM (Klook removed)."""

from app.affiliate import (
    GUIDE_PREP_ESIM,
    SCHOOL_BOOK_KEYWORD,
    UNIVERSITY_BOOK_KEYWORD,
    affiliate_context,
    normalize_guide_slug,
    rakuten_search_url,
)
from app.a8_affiliate import a8_housing_context, a8_travel_context, SHINOKUBO_KOREAN_A8


def test_rakuten_search_url_encoded():
    url = rakuten_search_url("JLPT N2 問題集")
    assert "hb.afl.rakuten.co.jp/hgc/" in url
    assert "search.rakuten.co.jp" in url


def test_english_sim_guide_shows_rakuten_shop():
    ctx = affiliate_context("sim-card-guide", lang="en")
    assert ctx["show_affiliate"] is True
    assert ctx["show_rakuten"] is True
    assert "ポケットWiFi" in ctx["affiliate_keyword"]


def test_korean_sim_guide_shows_rakuten_shop():
    ctx = affiliate_context("sim-card-guide_kr", lang="kr")
    assert ctx["show_affiliate"] is True
    assert ctx["show_rakuten"] is True
    assert ctx["show_jp_esim"] is False
    assert "ポケットWiFi" in ctx["affiliate_keyword"]


def test_korean_jlpt_guide_no_klook():
    ctx = affiliate_context("jlpt-levels_kr", lang="kr")
    assert ctx["show_affiliate"] is True
    assert ctx["affiliate_kind"] == "book"
    assert "라쿠텐" in ctx["affiliate_desc"]


def test_amazon_prime_guide_hides_affiliate():
    ctx = affiliate_context("amazon-prime-student", lang="en")
    assert ctx["show_affiliate"] is False


def test_school_default_jlpt_rakuten():
    ctx = affiliate_context("school_abc", lang="en", item_type="school")
    assert ctx["show_affiliate"] is True
    assert ctx["affiliate_kind"] == "book"
    assert ctx["affiliate_keyword"] == SCHOOL_BOOK_KEYWORD
    assert ctx["show_rakuten"] is True


def test_university_eju_rakuten():
    ctx = affiliate_context("univ_xyz", lang="kr", item_type="university")
    assert ctx["show_affiliate"] is True
    assert ctx["affiliate_keyword"] == UNIVERSITY_BOOK_KEYWORD
    assert ctx["show_jp_esim"] is True


def test_stay_en_uses_a8_not_klook():
    aff = affiliate_context("oakhouse_1164", lang="en", item_type="stay")
    assert aff["show_affiliate"] is False
    # Agoda is in the housing one-row, not a separate travel block
    travel = a8_travel_context(
        page_kind="stay_detail",
        lang="en",
        guide_slug="oakhouse_1164",
        item_type="stay",
    )
    assert travel["show_a8_banners"] is False
    housing = a8_housing_context(
        page_kind="stay_detail",
        lang="en",
        stay_id="oakhouse_1164",
        stay_operator="Oakhouse",
    )
    assert housing["show_a8_housing"] is True
    assert [b["id"] for b in housing["a8_housing_banners"]] == [
        "oakhouse",
        "cross_oneroom",
        "agoda",
    ]


def test_transport_guide_a8_agoda():
    ctx = a8_travel_context(
        page_kind="travel_guide",
        lang="en",
        guide_slug="shinkansen-deals",
        item_type="guide",
    )
    assert ctx["show_a8_banners"] is True
    assert ctx["a8_banners"][0]["id"] == "agoda"


def test_esim_guide_a8_tora():
    ctx = a8_travel_context(
        page_kind="travel_guide",
        lang="en",
        guide_slug="sim-card-guide",
        item_type="guide",
    )
    assert ctx["show_a8_banners"] is True
    assert ctx["a8_banners"][0]["id"] == "tora_esim"


def test_urban_tokyo_guide_korean_banner(monkeypatch):
    monkeypatch.setitem(
        SHINOKUBO_KOREAN_A8,
        "click_url",
        "https://px.a8.net/svt/ejp?a8mat=TEST",
    )
    monkeypatch.setitem(
        SHINOKUBO_KOREAN_A8,
        "image_url",
        "https://www22.a8.net/svt/bgt?aid=test",
    )
    monkeypatch.setitem(
        SHINOKUBO_KOREAN_A8,
        "pixel_url",
        "https://www17.a8.net/0.gif?a8mat=TEST",
    )
    ctx = a8_travel_context(
        page_kind="travel_guide",
        lang="en",
        guide_slug="urban-lifestyle-tokyo-schools",
        item_type="guide",
    )
    assert ctx["show_a8_banners"] is True
    assert ctx["a8_banners"][0]["id"] == "shin_okubo_korean"
    assert ctx["a8_banners_title"] == "Learn Korean in Tokyo"


def test_normalize_guide_slug():
    assert normalize_guide_slug("guide_housing_kr") == "housing"
    assert "sim-card-guide" in GUIDE_PREP_ESIM

"""A8 housing affiliate banners."""

from app.a8_affiliate import (
    HOUSING_A8_GUIDE_SLUGS,
    OAKHOUSE_A8,
    a8_housing_context,
    oakhouse_booking_url,
)


def test_stays_list_shows_both_banners():
    ctx = a8_housing_context(page_kind="stays_list", lang="en")
    assert ctx["show_a8_housing"] is True
    ids = [b["id"] for b in ctx["a8_housing_banners"]]
    assert ids == ["oakhouse", "cross_oneroom"]


def test_oakhouse_stay_detail():
    ctx = a8_housing_context(
        page_kind="stay_detail",
        lang="en",
        stay_id="oakhouse_994",
        stay_operator="Oakhouse",
    )
    assert ctx["show_a8_housing"] is True
    ids = [b["id"] for b in ctx["a8_housing_banners"]]
    assert "oakhouse" in ids
    assert "cross_oneroom" in ids


def test_sakura_stay_shows_cross_only():
    ctx = a8_housing_context(
        page_kind="stay_detail",
        lang="en",
        stay_id="sakura_sunshine_city",
        stay_operator="Sakura House",
    )
    ids = [b["id"] for b in ctx["a8_housing_banners"]]
    assert ids == ["cross_oneroom"]


def test_housing_guide_shows_banners():
    ctx = a8_housing_context(page_kind="housing_guide", lang="kr", guide_slug="housing")
    assert ctx["show_a8_housing"] is True
    assert len(ctx["a8_housing_banners"]) == 2
    assert ctx["a8_housing_banners"][0]["alt"] == OAKHOUSE_A8["alt_kr"]
    assert ctx["a8_housing_banners"][0]["label"] == OAKHOUSE_A8["label_kr"]
    assert ctx["a8_housing_banners"][1]["label"] == "크로스 원룸 — 가구·가전 포함"


def test_non_housing_guide_hidden():
    ctx = a8_housing_context(page_kind="housing_guide", lang="en", guide_slug="jlpt-levels")
    assert ctx["show_a8_housing"] is False


def test_oakhouse_booking_url_override():
    url = oakhouse_booking_url(
        operator="Oakhouse",
        booking_url="https://www.oakhouse.jp/eng/apartment/994",
    )
    assert url == OAKHOUSE_A8["click_url"]


def test_non_oakhouse_booking_url_unchanged():
    direct = "https://www.sakura-house.com/building/foo"
    assert oakhouse_booking_url(operator="Sakura House", booking_url=direct) == direct


def test_housing_guide_slug_set_nonempty():
    assert "housing" in HOUSING_A8_GUIDE_SLUGS
    assert "tokyo-student-housing-operators" in HOUSING_A8_GUIDE_SLUGS

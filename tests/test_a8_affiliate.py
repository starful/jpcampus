"""A8 housing affiliate banners."""

from app.a8_affiliate import (
    HOUSING_A8_GUIDE_SLUGS,
    OAKHOUSE_A8,
    a8_housing_context,
    oakhouse_booking_url,
)


def test_stays_list_shows_oakhouse_only():
    ctx = a8_housing_context(page_kind="stays_list", lang="en")
    assert ctx["show_a8_housing"] is True
    ids = [b["id"] for b in ctx["a8_housing_banners"]]
    assert ids == ["oakhouse"]


def test_oakhouse_stay_detail():
    ctx = a8_housing_context(
        page_kind="stay_detail",
        lang="en",
        stay_id="oakhouse_994",
        stay_operator="Oakhouse",
    )
    assert ctx["show_a8_housing"] is True
    ids = [b["id"] for b in ctx["a8_housing_banners"]]
    assert ids == ["oakhouse", "agoda"]


def test_sakura_stay_shows_agoda_only():
    ctx = a8_housing_context(
        page_kind="stay_detail",
        lang="en",
        stay_id="sakura_sunshine_city",
        stay_operator="Sakura House",
    )
    ids = [b["id"] for b in ctx["a8_housing_banners"]]
    assert ids == ["agoda"]


def test_sakura_stay_kr_no_banners():
    ctx = a8_housing_context(
        page_kind="stay_detail",
        lang="kr",
        stay_id="sakura_sunshine_city",
        stay_operator="Sakura House",
    )
    assert ctx["show_a8_housing"] is False


def test_housing_guide_shows_oakhouse():
    ctx = a8_housing_context(page_kind="housing_guide", lang="kr", guide_slug="housing")
    assert ctx["show_a8_housing"] is True
    assert len(ctx["a8_housing_banners"]) == 1
    assert ctx["a8_housing_banners"][0]["alt"] == OAKHOUSE_A8["alt_kr"]
    assert ctx["a8_housing_banners"][0]["label"] == OAKHOUSE_A8["label_kr"]


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


def test_rendered_a8_uses_text_buttons_not_images():
    from fastapi.testclient import TestClient

    from app.main import app

    client = TestClient(app)
    travel = client.get("/guide/transport-ic")
    assert travel.status_code == 200
    assert "a8-banners__img" not in travel.text
    assert "Travel partners" in travel.text
    assert "Agoda" in travel.text
    assert "agoda.com/partners" in travel.text
    assert "TORA" not in travel.text

    housing = client.get("/guide/housing")
    assert housing.status_code == 200
    assert "Oakhouse" in housing.text
    assert "Cross One Room" not in housing.text
    assert "oakhouse-repeat" in housing.text
    assert "Check share houses" in housing.text

    stay = client.get("/stay/oakhouse_994")
    if stay.status_code == 200:
        assert "a8-banners__img" not in stay.text
        assert "a8-banners__label" in stay.text
        assert "Agoda" in stay.text

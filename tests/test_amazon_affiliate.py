"""Amazon JP CTA — always secondary to Oakhouse / Rakuten."""

from app.affiliate import affiliate_context
from app.amazon_affiliate import amazon_category, amazon_context


def test_categories():
    assert amazon_category("housing") == "housing"
    assert amazon_category("transport-ic") == "travel"
    assert amazon_category("abc", "school") == "school"
    assert amazon_category("jlpt-levels") == "default"


def test_keywords():
    assert "tag=starful06-22" in amazon_context("housing", oakhouse_primary=True)["amazon_cta"]["click_url"]
    assert amazon_context("housing", oakhouse_primary=True)["amazon_cta"]["keyword"] == "一人暮らし 寝具"
    assert amazon_context("transport-ic")["amazon_cta"]["keyword"] == "日本旅行 グッズ"
    assert amazon_context("x", item_type="school")["amazon_cta"]["keyword"] == "留学 準備"
    assert amazon_context("glasses-x")["amazon_cta"]["keyword"] == "日本 生活 便利グッズ"


def test_housing_guide_marked_secondary_after_oakhouse():
    cta = amazon_context("housing", oakhouse_primary=True)["amazon_cta"]
    assert cta["secondary"] is True and cta["after_oakhouse"] is True


def test_hidden_for_stay_and_when_rakuten_on_guide():
    assert amazon_context("oakhouse_994", item_type="stay")["show_amazon"] is False
    assert amazon_context("housing", rakuten_shown=True)["show_amazon"] is False


def test_rendered_housing_oakhouse_primary_amazon_secondary():
    from fastapi.testclient import TestClient

    from app.main import app

    client = TestClient(app)
    html = client.get("/guide/housing").text
    assert "oakhouse-repeat" in html
    assert "Check share houses" in html
    assert html.count("px.a8.net") >= 1
    assert "amazon.co.jp/s?k=" in html
    assert html.index("oakhouse-repeat") < html.index("amazon.co.jp/s?k=")
    # Rakuten bedding stays hidden when Oakhouse is primary
    assert affiliate_context("housing", lang="en")["show_affiliate"] is False
    assert "hb.afl.rakuten.co.jp" not in html

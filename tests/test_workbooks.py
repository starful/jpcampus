"""Free workbook PDFs on matching guide and stay pages."""

from app.workbooks import GUIDE_WORKBOOKS, WORKBOOK_FILES, workbook_context, workbook_href


def test_pdf_files_are_served():
    from fastapi.testclient import TestClient

    from app.main import app

    client = TestClient(app)
    for filename in WORKBOOK_FILES.values():
        response = client.get(f"/static/workbooks/{filename}")
        assert response.status_code == 200
        assert "pdf" in response.headers.get("content-type", "").lower()
        assert response.content[:4] == b"%PDF"


def test_visa_seed_shows_coe_workbook():
    from fastapi.testclient import TestClient

    from app.main import app

    client = TestClient(app)
    response = client.get("/guide/visa-seed")
    assert response.status_code == 200
    assert "workbook-box" in response.text
    assert workbook_href("coe") in response.text
    assert "workbook_download" in response.text


def test_housing_guide_shows_housing_workbook():
    from fastapi.testclient import TestClient

    from app.main import app

    client = TestClient(app)
    response = client.get("/guide/housing")
    assert response.status_code == 200
    assert workbook_href("housing") in response.text


def test_unrelated_guide_has_no_workbook_box():
    from fastapi.testclient import TestClient

    from app.main import app

    client = TestClient(app)
    response = client.get("/guide/jlpt-seed")
    assert response.status_code == 200
    assert "workbook-box" not in response.text


def test_workbook_context_maps_guides():
    assert GUIDE_WORKBOOKS["visa-seed"] == ("coe",)
    ctx = workbook_context("en", guide_slug="guide_visa-seed")
    assert len(ctx["workbooks"]) == 1
    assert ctx["workbooks"][0]["id"] == "coe"

    stays = workbook_context("kr", page_kind="stays_list")
    assert stays["workbooks"][0]["id"] == "housing"
    assert "숙소" in stays["workbooks"][0]["title"]

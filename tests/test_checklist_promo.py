"""Guide-list checklist preview CTA + free workbook download tracking hooks."""

from pathlib import Path

from fastapi.testclient import TestClient

from app.main import app
from app.workbooks import WORKBOOK_FILES, workbook_href

STATIC = Path(__file__).resolve().parents[1] / "app" / "static"
PREVIEW = STATIC / "checklist-preview"


def test_guide_list_has_cta_checklist_and_workbook_download_tracking():
    client = TestClient(app)
    for lang, label_preview, label_wb in (
        ("en", "guide_list_preview_en", "arrival_guide_list_en"),
        ("kr", "guide_list_preview_kr", "arrival_guide_list_kr"),
    ):
        path = "/guide" if lang == "en" else "/guide?lang=kr"
        response = client.get(path)
        assert response.status_code == 200
        html = response.text
        assert 'data-track="cta_checklist"' in html
        assert f'data-track-label="{label_preview}"' in html
        assert 'data-track="workbook_download"' in html
        assert f'data-track-label="{label_wb}"' in html
        assert f'data-track-lang="{lang}"' in html
        assert f"/static/checklist-preview/{lang}/00-flow.html" in html
        assert workbook_href("arrival") in html
        assert "data-preview-popup" not in html


def test_home_no_longer_has_checklist_promo():
    client = TestClient(app)
    html = client.get("/?lang=kr").text
    assert 'data-track-label="home_preview_kr"' not in html
    assert 'data-preview-popup="1"' not in html
    # Home may still have other CTAs; checklist section title track should be gone.
    assert "checklist-promo" not in html


def test_schools_list_has_no_checklist_promo():
    client = TestClient(app)
    html = client.get("/schools").text
    assert "checklist-promo" not in html
    assert 'data-track="cta_checklist"' not in html


def test_preview_html_files_exist_kr_en():
    for lang in ("kr", "en"):
        for name in ("00-flow.html", "02-day-01.html", "20-later-money.html"):
            path = PREVIEW / lang / name
            assert path.is_file(), path
            text = path.read_text(encoding="utf-8")
            assert "track.js" in text
            assert "langbar.js" in text
            assert "waitlist.js" in text
            assert "data-waitlist" in text
            assert "data-preview-page" in text
            if name == "00-flow.html":
                assert "preview-locked__badge" in text
                assert "02-day-01.html" in text
                assert "20-later-money.html" in text


def test_preview_and_workbook_static_routes():
    client = TestClient(app)
    assert client.get("/static/checklist-preview/kr/00-flow.html").status_code == 200
    assert client.get("/static/checklist-preview/en/00-flow.html").status_code == 200
    assert client.get("/static/checklist-preview/track.js").status_code == 200
    arrival = WORKBOOK_FILES["arrival"]
    assert client.get(f"/static/workbooks/{arrival}").status_code == 200


def test_base_tracking_uses_beacon():
    client = TestClient(app)
    html = client.get("/").text
    assert "transport_type" in html
    assert 'addEventListener("click"' in html or "addEventListener('click'" in html

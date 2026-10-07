"""Home checklist preview CTA + free workbook download tracking hooks."""

from pathlib import Path

from fastapi.testclient import TestClient

from app.main import app
from app.workbooks import WORKBOOK_FILES, workbook_href

STATIC = Path(__file__).resolve().parents[1] / "app" / "static"
PREVIEW = STATIC / "checklist-preview"


def test_home_has_cta_checklist_and_workbook_download_tracking():
    client = TestClient(app)
    for lang, label_preview, label_wb in (
        ("en", "home_preview_en", "arrival_home_en"),
        ("kr", "home_preview_kr", "arrival_home_kr"),
    ):
        path = "/" if lang == "en" else "/?lang=kr"
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
        assert "quick-action-btn" not in html


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

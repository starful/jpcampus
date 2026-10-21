"""Checklist waitlist API (Firestore collection shared with reactions)."""

from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_waitlist_rejects_invalid_email():
    response = client.post(
        "/api/checklist-waitlist",
        json={"email": "not-an-email", "lang": "kr", "source": "test"},
    )
    assert response.status_code in (400, 503)
    if response.status_code == 400:
        assert "Invalid" in response.json().get("detail", "")


def test_waitlist_honeypot_ignored():
    response = client.post(
        "/api/checklist-waitlist",
        json={
            "email": "bot@example.com",
            "lang": "en",
            "source": "test",
            "website": "http://spam.example",
        },
    )
    assert response.status_code == 200
    assert response.json().get("action") == "ignored"


def test_guide_list_has_checklist_cta_without_popup():
    html = client.get("/guide?lang=kr").text
    assert 'data-track="cta_checklist"' in html
    assert "data-preview-popup" not in html


def test_preview_pages_have_waitlist_mount():
    for lang in ("kr", "en"):
        path = f"/static/checklist-preview/{lang}/00-flow.html"
        html = client.get(path).text
        assert "data-waitlist" in html
        assert "waitlist.js" in html
        assert "script.google.com" not in html

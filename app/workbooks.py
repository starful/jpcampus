"""Free printable workbooks (English PDFs). Paid editions will be separate later."""

from __future__ import annotations

from typing import Any

from app.affiliate import normalize_guide_slug
from app.i18n import get_ui_text

WORKBOOK_FILES: dict[str, str] = {
    "coe": "jpcampus-coe-financial-documents-workbook-en.pdf",
    "arrival": "jpcampus-first-14-days-workbook-en.pdf",
    "housing": "jpcampus-housing-guarantor-workbook-en.pdf",
}

GUIDE_WORKBOOKS: dict[str, tuple[str, ...]] = {
    "visa-seed": ("coe",),
    "ward-office": ("arrival",),
    "residence-card": ("arrival",),
    "bank-seed": ("arrival",),
    "sim-card-guide": ("arrival",),
    "my-number-card": ("arrival",),
    "healthcare-seed": ("arrival",),
    "housing": ("housing",),
    "housing-seed": ("housing",),
    "rent-guarantor": ("housing",),
    "tokyo-student-housing-operators": ("housing",),
    "apartment-initial-costs": ("housing",),
    "finding-apts-online": ("housing",),
}


def workbook_href(workbook_id: str) -> str:
    filename = WORKBOOK_FILES[workbook_id]
    return f"/static/workbooks/{filename}"


def workbook_context(
    lang: str,
    *,
    guide_slug: str | None = None,
    page_kind: str | None = None,
) -> dict[str, Any]:
    ids: tuple[str, ...] = ()
    if page_kind in {"stays_list", "stay_detail"}:
        ids = ("housing",)
    elif guide_slug:
        ids = GUIDE_WORKBOOKS.get(normalize_guide_slug(guide_slug), ())

    if not ids:
        return {"workbooks": []}

    ui = get_ui_text(lang)
    items = []
    for workbook_id in ids:
        filename = WORKBOOK_FILES[workbook_id]
        items.append(
            {
                "id": workbook_id,
                "href": workbook_href(workbook_id),
                "filename": filename,
                "title": ui[f"workbook_{workbook_id}_title"],
                "desc": ui[f"workbook_{workbook_id}_desc"],
            }
        )
    return {"workbooks": items}

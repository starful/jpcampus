"""Social card/image routes and favicon assets."""
from __future__ import annotations

import os

from fastapi import APIRouter, Query, Request
from fastapi.responses import FileResponse, HTMLResponse, Response

from app.config import DOMAIN
from app.deps import templates
from app.seo import apply_guide_serp_overrides, build_meta_description, build_meta_title
from app.social_share import (
    card_page_path,
    detail_page_path,
    fetch_social_jpeg,
    load_guide_item,
    load_school_item,
    resolve_thumbnail_url,
    share_context,
)
from app.utils import STATIC_DIR

router = APIRouter()


def _static_social_path(image_key: str) -> str | None:
    path = os.path.join(STATIC_DIR, "social", f"{image_key}.jpg")
    return path if os.path.isfile(path) else None


def _social_image_headers() -> dict[str, str]:
    return {"Cache-Control": "public, max-age=604800"}


def _render_social_image(kind: str, identifier: str, lang: str) -> Response:
    if kind == "school":
        item, item_type = load_school_item(identifier, lang)
        source = resolve_thumbnail_url(DOMAIN, item, item_type)
    else:
        item = load_guide_item(identifier, lang)
        source = resolve_thumbnail_url(DOMAIN, item, "guide", guide_slug=identifier)
    data = fetch_social_jpeg(source)
    return Response(content=data, media_type="image/jpeg", headers=_social_image_headers())


@router.api_route("/social/{image_key}.jpg", methods=["GET", "HEAD"])
async def social_image(image_key: str, lang: str = Query("en")):
    static_path = _static_social_path(image_key)
    if static_path:
        return FileResponse(static_path, media_type="image/jpeg", headers=_social_image_headers())
    if image_key.startswith("guide-"):
        return _render_social_image("guide", image_key[6:], lang)
    return _render_social_image("school", image_key, lang)


@router.api_route("/card/school/{school_id}", methods=["GET", "HEAD"], response_class=HTMLResponse)
async def school_social_card(request: Request, school_id: str, lang: str = Query("en")):
    item, item_type = load_school_item(school_id, lang)
    title = (
        item.get("title")
        or item.get("basic_info", {}).get("name_en")
        or item.get("basic_info", {}).get("name_ja")
        or "JP Campus"
    )
    ctx = share_context(DOMAIN, "school", school_id, title, lang)
    page = f"{DOMAIN}{detail_page_path('school', school_id, lang)}"
    card = f"{DOMAIN}{card_page_path('school', school_id, lang)}"
    return templates.TemplateResponse(request, "social_card.html", {
        "lang": lang,
        "title": title,
        "seo_title": build_meta_title(title, lang),
        "seo_desc": build_meta_description(
            item.get("description", ""),
            "Compare school details, tuition clues, and student-ready preparation tips.",
        ),
        "page_url": page,
        "card_url": card,
        **ctx,
    })


@router.api_route("/card/guide/{slug}", methods=["GET", "HEAD"], response_class=HTMLResponse)
async def guide_social_card(request: Request, slug: str, lang: str = Query("en")):
    item = load_guide_item(slug, lang)
    title_raw, desc_raw = apply_guide_serp_overrides(slug, lang, item)
    title = title_raw or item.get("title", "Study in Japan Guide")
    ctx = share_context(DOMAIN, "guide", slug, title, lang)
    page = f"{DOMAIN}{detail_page_path('guide', slug, lang)}"
    card = f"{DOMAIN}{card_page_path('guide', slug, lang)}"
    return templates.TemplateResponse(request, "social_card.html", {
        "lang": lang,
        "title": title,
        "seo_title": build_meta_title(title, lang),
        "seo_desc": build_meta_description(
            desc_raw,
            "Actionable study-in-Japan guide with practical decisions and student checklists.",
        ),
        "page_url": page,
        "card_url": card,
        **ctx,
    })


_STATIC_ROOT_FILES: dict[str, tuple[str, str | None]] = {
    "/favicon.ico": ("img/favicon.ico", None),
    "/favicon-32x32.png": ("img/favicon-32x32.png", "image/png"),
    "/favicon-48x48.png": ("img/favicon-48x48.png", "image/png"),
    "/apple-touch-icon.png": ("img/apple-touch-icon.png", "image/png"),
    "/android-chrome-192x192.png": ("img/android-chrome-192x192.png", "image/png"),
    "/android-chrome-512x512.png": ("img/android-chrome-512x512.png", "image/png"),
    "/site.webmanifest": ("site.webmanifest", "application/manifest+json"),
}


def _make_static_handler(rel_path: str, media_type: str | None):
    async def handler():
        path = os.path.join(STATIC_DIR, rel_path)
        if media_type:
            return FileResponse(path, media_type=media_type)
        return FileResponse(path)

    return handler


for _route_path, (_rel_path, _media_type) in _STATIC_ROOT_FILES.items():
    router.add_api_route(
        _route_path,
        _make_static_handler(_rel_path, _media_type),
        methods=["GET", "HEAD"],
        include_in_schema=False,
    )

"""FastAPI application entrypoint."""
from __future__ import annotations

import os
from urllib.parse import urlencode

from dotenv import load_dotenv
from fastapi import FastAPI, Request
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles

from app.config import DOMAIN, redirect_target
from app.deps import configure_template_globals
from app.reactions import router as reactions_router
from app.routes.pages import router as pages_router
from app.routes.social import router as social_router
from app.utils import CONTENT_DIR, STATIC_DIR

load_dotenv()

app = FastAPI()

configure_template_globals()

if not os.path.exists(CONTENT_DIR):
    os.makedirs(CONTENT_DIR)

app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")


def _seo_cleanup_redirect(request: Request) -> RedirectResponse | None:
    """Collapse crawlable junk query URLs onto canonical destinations."""
    if request.method not in {"GET", "HEAD"}:
        return None
    path = request.url.path
    if path.startswith("/api") or path.startswith("/static"):
        return None

    params = request.query_params
    add_compare = (params.get("add_compare") or "").strip()
    if add_compare:
        target = f"/school/{add_compare}"
        if params.get("lang") == "kr":
            target = f"{target}?lang=kr"
        return RedirectResponse(url=target, status_code=301)

    # English canonicals are bare paths; drop explicit ?lang=en.
    if params.get("lang") == "en":
        kept = [(k, v) for k, v in params.multi_items() if k != "lang"]
        query = urlencode(kept)
        target = f"{path}?{query}" if query else path
        return RedirectResponse(url=target, status_code=301)

    return None


@app.middleware("http")
async def legacy_redirect_middleware(request: Request, call_next):
    cleanup = _seo_cleanup_redirect(request)
    if cleanup is not None:
        return cleanup

    response = await call_next(request)
    if response.status_code != 404:
        return response
    if request.url.path.startswith("/api") or request.url.path.startswith("/static"):
        return response

    target = redirect_target(request.url.path)
    if not target:
        return response

    # Keep Korean locale only; drop crawl junk like add_compare / lang=en.
    if request.query_params.get("lang") == "kr" and "?" not in target:
        redirect_url = f"{target}?lang=kr"
    else:
        redirect_url = target
    return RedirectResponse(url=redirect_url, status_code=301)


app.include_router(reactions_router, prefix="/api")
app.include_router(pages_router)
app.include_router(social_router)

__all__ = ["app", "DOMAIN"]

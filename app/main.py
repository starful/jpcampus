"""FastAPI application entrypoint."""
from __future__ import annotations

import os

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


@app.middleware("http")
async def legacy_redirect_middleware(request: Request, call_next):
    response = await call_next(request)
    if response.status_code != 404:
        return response
    if request.url.path.startswith("/api") or request.url.path.startswith("/static"):
        return response

    target = redirect_target(request.url.path)
    if not target:
        return response

    query = request.url.query
    redirect_url = f"{target}?{query}" if query and "?" not in target else target
    return RedirectResponse(url=redirect_url, status_code=301)


app.include_router(reactions_router, prefix="/api")
app.include_router(pages_router)
app.include_router(social_router)

__all__ = ["app", "DOMAIN"]

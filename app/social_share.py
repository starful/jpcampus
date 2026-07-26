"""SNS share bar + X/OG card helpers (same-domain social images)."""
from __future__ import annotations

import io
import os
import re
import urllib.error
import urllib.request
from functools import lru_cache
from urllib.parse import quote, urlparse

from app.content_loader import ContentNotFoundError, load_guide_content, load_school_content
from app.utils import STATIC_DIR, assign_thumbnails, resolve_guide_thumbnail

SOCIAL_CARD_VERSION = "2"
_FETCH_UA = "JPCampus/1.0 (+https://jpcampus.net)"
# Request-path remote fetch was hanging Cloud Run (Unsplash timeouts starve uvicorn).
# Default off — serve static/prebuilt or a local placeholder. Build scripts can enable.
SOCIAL_REMOTE_FETCH = os.getenv("JPCAMPUS_SOCIAL_REMOTE_FETCH", "0").strip().lower() in (
    "1",
    "true",
    "yes",
)
SOCIAL_FETCH_TIMEOUT = float(os.getenv("JPCAMPUS_SOCIAL_FETCH_TIMEOUT", "2.5"))


def social_image_path(kind: str, identifier: str) -> str:
    if kind == "guide":
        safe = "guide-" + re.sub(r"[^a-z0-9_-]", "", identifier.lower())
    else:
        safe = re.sub(r"[^a-z0-9_-]", "", identifier.lower())
    return f"/social/{safe}.jpg"


def social_image_url(domain: str, kind: str, identifier: str) -> str:
    return f"{domain.rstrip('/')}{social_image_path(kind, identifier)}"


def detail_page_path(kind: str, identifier: str, lang: str) -> str:
    segment = "school" if kind == "school" else "guide"
    path = f"/{segment}/{identifier}"
    return f"{path}?lang=kr" if lang == "kr" else path


def card_page_path(kind: str, identifier: str, lang: str) -> str:
    params = {"sc": SOCIAL_CARD_VERSION}
    if lang == "kr":
        params["lang"] = "kr"
    query = "&".join(f"{key}={value}" for key, value in params.items())
    return f"/card/{kind}/{identifier}?{query}"


def share_context(domain: str, kind: str, identifier: str, title: str, lang: str) -> dict:
    page = detail_page_path(kind, identifier, lang)
    share_url = f"{domain.rstrip('/')}{page}"
    if lang == "kr":
        share_tweet = f"{title} — JP Campus"
    else:
        share_tweet = f"{title} — Study in Japan on JP Campus"
    return {
        "share_id": identifier,
        "share_url": share_url,
        "share_url_x": f"{domain.rstrip('/')}{card_page_path(kind, identifier, lang)}",
        "share_tweet": share_tweet,
        "share_lang": lang,
        "og_page_url": share_url,
        "og_image_abs": social_image_url(domain, kind, identifier),
        "og_image_width": 1200,
        "og_image_height": 630,
        "linkedin_inspector_url": (
            f"https://www.linkedin.com/post-inspector/inspect/{quote(share_url, safe='')}"
        ),
    }


def _guide_thumbnail(item: dict, guide_slug: str) -> str:
    guide_id = str(item.get("id") or guide_slug).replace("_kr", "")
    return resolve_guide_thumbnail(item, guide_id)


def resolve_thumbnail_url(domain: str, item: dict, item_type: str, *, guide_slug: str | None = None) -> str:
    thumb = (item.get("thumbnail") or "").strip()
    if thumb.startswith("http"):
        return thumb
    if thumb.startswith("/"):
        return f"{domain.rstrip('/')}{thumb}"
    if item_type == "guide":
        return _guide_thumbnail(item, guide_slug or "")
    category = "university" if item_type == "university" else "school"
    row = {"id": item.get("id") or "default_id"}
    assign_thumbnails([row], category)
    return row["thumbnail"]


def load_school_item(school_id: str, lang: str) -> tuple[dict, str]:
    try:
        item, item_type, _content_html = load_school_content(school_id, lang)
    except ContentNotFoundError as exc:
        raise FileNotFoundError(school_id) from exc
    item["id"] = school_id
    assign_thumbnails([item], item_type)
    return item, item_type


def load_guide_item(slug: str, lang: str) -> dict:
    try:
        item, _content_html = load_guide_content(slug, lang)
    except ContentNotFoundError as exc:
        raise FileNotFoundError(slug) from exc
    return item


def jpeg_bytes(img) -> bytes:
    buf = io.BytesIO()
    img.save(buf, format="JPEG", quality=88, optimize=True)
    return buf.getvalue()


def _is_self_hosted_url(url: str) -> bool:
    host = (urlparse(url).hostname or "").lower()
    return host in {"jpcampus.net", "www.jpcampus.net"} or host.endswith(".a.run.app")


@lru_cache(maxsize=1)
def placeholder_social_jpeg() -> bytes:
    """Local 1200x630 JPEG — never touches the network."""
    from PIL import Image, ImageOps

    og_path = os.path.join(STATIC_DIR, "img", "og_image.png")
    if os.path.isfile(og_path):
        img = Image.open(og_path).convert("RGB")
        return jpeg_bytes(ImageOps.fit(img, (1200, 630), Image.Resampling.LANCZOS))
    img = Image.new("RGB", (1200, 630), (15, 23, 42))
    return jpeg_bytes(img)


def fetch_social_jpeg(source_url: str, *, timeout: float | None = None) -> bytes:
    """Fetch + fit a remote image. Raises on failure (callers may fall back)."""
    timeout = SOCIAL_FETCH_TIMEOUT if timeout is None else timeout
    if not source_url or _is_self_hosted_url(source_url):
        raise ValueError("refusing self-hosted or empty social source")
    req = urllib.request.Request(source_url, headers={"User-Agent": _FETCH_UA})
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        raw = resp.read()
        if not raw:
            raise ValueError("empty image")
    try:
        from PIL import Image, ImageOps

        img = Image.open(io.BytesIO(raw)).convert("RGB")
        return jpeg_bytes(ImageOps.fit(img, (1200, 630), Image.Resampling.LANCZOS))
    except Exception:
        return raw


def resolve_social_jpeg(source_url: str, *, allow_remote: bool | None = None) -> bytes:
    """Safe bytes for the request path: optional short remote fetch, else placeholder."""
    use_remote = SOCIAL_REMOTE_FETCH if allow_remote is None else allow_remote
    if use_remote and source_url:
        try:
            return fetch_social_jpeg(source_url)
        except (urllib.error.URLError, TimeoutError, ValueError, OSError):
            pass
        except Exception:
            pass
    return placeholder_social_jpeg()


def static_social_image_key(kind: str, identifier: str) -> str:
    if kind == "guide":
        return "guide-" + re.sub(r"[^a-z0-9_-]", "", identifier.lower())
    return re.sub(r"[^a-z0-9_-]", "", identifier.lower())

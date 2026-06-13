"""SNS share bar + X/OG card helpers (same-domain social images)."""
from __future__ import annotations

import hashlib
import io
import os
import re
import urllib.request
from urllib.parse import quote

import frontmatter

from app.utils import CONTENT_DIR, GUIDE_THUMBNAILS, assign_thumbnails


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
    path = f"/card/{kind}/{identifier}"
    return f"{path}?lang=kr" if lang == "kr" else path


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
    thumb = (item.get("thumbnail") or "").strip()
    if item.get("is_featured") and thumb:
        return thumb
    guide_id = str(item.get("id") or guide_slug).replace("_kr", "")
    hash_val = int(hashlib.md5(guide_id.encode("utf-8")).hexdigest(), 16)
    return GUIDE_THUMBNAILS[hash_val % len(GUIDE_THUMBNAILS)]


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
    filename = f"{school_id}_kr.md" if lang == "kr" else f"{school_id}.md"
    md_path = os.path.join(CONTENT_DIR, filename)
    if not os.path.exists(md_path) and lang == "kr":
        md_path = os.path.join(CONTENT_DIR, f"{school_id}.md")
    if not os.path.exists(md_path):
        raise FileNotFoundError(school_id)
    post = frontmatter.load(md_path)
    item = dict(post.metadata)
    item["id"] = school_id
    item_type = "university" if item.get("category") == "university" else "school"
    assign_thumbnails([item], item_type)
    return item, item_type


def load_guide_item(slug: str, lang: str) -> dict:
    filename = f"guide_{slug}_kr.md" if lang == "kr" else f"guide_{slug}.md"
    md_path = os.path.join(CONTENT_DIR, filename)
    if not os.path.exists(md_path) and lang == "kr":
        md_path = os.path.join(CONTENT_DIR, f"guide_{slug}.md")
    if not os.path.exists(md_path):
        raise FileNotFoundError(slug)
    post = frontmatter.load(md_path)
    item = dict(post.metadata)
    item.setdefault("id", slug)
    return item


def jpeg_bytes(img) -> bytes:
    buf = io.BytesIO()
    img.save(buf, format="JPEG", quality=78, optimize=True, progressive=True)
    return buf.getvalue()


def fetch_social_jpeg(source_url: str) -> bytes:
    with urllib.request.urlopen(source_url, timeout=15) as resp:
        raw = resp.read()
        if not raw:
            raise ValueError("empty image")
    try:
        from PIL import Image, ImageOps

        img = Image.open(io.BytesIO(raw)).convert("RGB")
        return jpeg_bytes(ImageOps.fit(img, (1200, 630), Image.Resampling.LANCZOS))
    except Exception:
        return raw

"""SEO helpers: canonical URLs, meta tags, SERP overrides, FAQ JSON-LD."""
from __future__ import annotations

import json
import os
from datetime import datetime, timezone

from app.config import DOMAIN
from app.seo_overrides import faq_rows, high_ctr_slugs, serp_override
from app.utils import CONTENT_DIR, load_school_data


def build_canonical_url(path: str, lang: str | None = None) -> str:
    canonical = f"{DOMAIN}{path}"
    if lang == "kr":
        return f"{canonical}?lang=kr"
    return canonical


def build_hreflang_urls(path: str) -> dict[str, str]:
    return {
        "en": build_canonical_url(path),
        "ko": build_canonical_url(path, "kr"),
        "x-default": build_canonical_url(path),
    }


def default_updated_at() -> str:
    _, updated_at = load_school_data("en")
    return updated_at or datetime.now(timezone.utc).strftime("%Y-%m-%d")


def site_stats(lang: str = "en") -> dict[str, int | str]:
    schools, updated_at = load_school_data(lang)
    return {
        "total_schools": len(schools),
        "updated_at": updated_at or default_updated_at(),
    }


def content_lastmod(*filenames: str) -> str:
    timestamps: list[float] = []
    for filename in filenames:
        filepath = os.path.join(CONTENT_DIR, filename)
        if os.path.exists(filepath):
            timestamps.append(os.path.getmtime(filepath))
    if not timestamps:
        return datetime.now(timezone.utc).strftime("%Y-%m-%d")
    return datetime.fromtimestamp(max(timestamps), timezone.utc).strftime("%Y-%m-%d")


def build_meta_title(raw_title: str, lang: str = "en", suffix: str = "JP Campus") -> str:
    year = datetime.now(timezone.utc).strftime("%Y")
    base = f"[{year}] {raw_title}"
    title = f"{base} | {suffix}"
    return title[:68]


def build_meta_description(raw_description: str, fallback: str) -> str:
    text = (raw_description or "").strip() or fallback
    if len(text) <= 155:
        return text
    return f"{text[:152].rstrip()}..."


def _guide_lang_key(lang: str) -> str:
    return "kr" if lang == "kr" else "en"


def apply_guide_serp_overrides(slug: str, lang: str, item: dict) -> tuple[str, str]:
    if slug in high_ctr_slugs():
        title = item.get("title", "Study in Japan Guide")
        desc = item.get("description", "")
        return title, desc
    lk = _guide_lang_key(lang)
    ov = serp_override(slug, lk)
    if not ov:
        return item.get("title", "Study in Japan Guide"), item.get("description", "")
    return ov.get("title", item.get("title", "")), ov.get("description", item.get("description", ""))


def guide_faq_json_ld(slug: str, lang: str) -> str | None:
    if slug in high_ctr_slugs():
        return None
    rows = faq_rows(slug, _guide_lang_key(lang))
    if not rows:
        return None
    entities = []
    for q, a in rows:
        entities.append(
            {
                "@type": "Question",
                "name": q,
                "acceptedAnswer": {"@type": "Answer", "text": a},
            }
        )
    payload = {"@context": "https://schema.org", "@type": "FAQPage", "mainEntity": entities}
    return json.dumps(payload, ensure_ascii=False)


def stay_faq_json_ld(item: dict) -> str | None:
    """Build FAQPage JSON-LD from stay frontmatter `faq` list [{q,a}, ...]."""
    rows = item.get("faq") or []
    entities = []
    for row in rows:
        if not isinstance(row, dict):
            continue
        q = (row.get("q") or row.get("question") or "").strip()
        a = (row.get("a") or row.get("answer") or "").strip()
        if not q or not a:
            continue
        entities.append(
            {
                "@type": "Question",
                "name": q,
                "acceptedAnswer": {"@type": "Answer", "text": a},
            }
        )
    if not entities:
        return None
    payload = {"@context": "https://schema.org", "@type": "FAQPage", "mainEntity": entities}
    return json.dumps(payload, ensure_ascii=False)

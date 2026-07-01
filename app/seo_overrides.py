"""Load guide SERP overrides and FAQ entries from data/seo_overrides.json."""
from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path

_DATA_PATH = Path(__file__).resolve().parent.parent / "data" / "seo_overrides.json"


@lru_cache(maxsize=1)
def _load() -> dict:
    with open(_DATA_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def high_ctr_slugs() -> frozenset[str]:
    return frozenset(_load().get("high_ctr_slugs", []))


def serp_override(slug: str, lang_key: str) -> dict[str, str] | None:
    entry = _load().get("serp_overrides", {}).get(slug, {}).get(lang_key)
    if not entry:
        return None
    return entry


def faq_rows(slug: str, lang_key: str) -> list[tuple[str, str]] | None:
    entries = _load().get("faq", {}).get(slug, {}).get(lang_key)
    if not entries:
        return None
    return [(row["q"], row["a"]) for row in entries]

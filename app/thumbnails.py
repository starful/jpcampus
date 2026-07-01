"""Thumbnail URL pools loaded from app/data/thumbnails.json."""
from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path

_DATA_PATH = Path(__file__).resolve().parent / "data" / "thumbnails.json"


@lru_cache(maxsize=1)
def _load() -> dict:
    with open(_DATA_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def univ_thumbnails() -> list[str]:
    return _load()["university"]


def school_thumbnails() -> list[str]:
    return _load()["school"]


def guide_thumbnails() -> list[str]:
    return _load()["guide"]


def broken_thumbnail_redirects() -> dict[str, str]:
    return _load().get("broken_redirects", {})

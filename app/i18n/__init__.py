"""UI string translations loaded from app/i18n/*.json."""
from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path

_I18N_DIR = Path(__file__).resolve().parent


@lru_cache(maxsize=8)
def _load_lang_cached(lang_key: str, mtime_ns: int) -> dict[str, str]:
    path = _I18N_DIR / f"{lang_key}.json"
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def get_ui_text(lang: str = "en") -> dict[str, str]:
    lang_key = "kr" if lang == "kr" else "en"
    path = _I18N_DIR / f"{lang_key}.json"
    mtime_ns = path.stat().st_mtime_ns if path.exists() else 0
    return _load_lang_cached(lang_key, mtime_ns)

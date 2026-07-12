"""Site configuration and legacy redirect map."""
from __future__ import annotations

import json
import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

FAMILY_SITE_ID = "jpcampus"
BASE_DIR = Path(__file__).resolve().parent
REDIRECT_MAP_PATH = BASE_DIR / "redirects.json"

DOMAIN = os.getenv("SITE_DOMAIN", "https://jpcampus.net").rstrip("/")
GOOGLE_MAPS_API_KEY = os.getenv("GOOGLE_MAPS_API_KEY")
ADS_TXT_CONTENT = os.getenv(
    "ADS_TXT_CONTENT",
    "google.com, pub-8780435268193938, DIRECT, f08c47fec0942fa0",
)
GA_MEASUREMENT_ID = os.getenv("GA_MEASUREMENT_ID", "G-EDJL0618LL")
ADSENSE_CLIENT_ID = os.getenv("ADSENSE_CLIENT_ID", "ca-pub-8780435268193938")

# Stay map/cards/nearby UI (seed + /stay/{id} kept; set true to re-enable)
SHOW_STAYS_UI = os.getenv("SHOW_STAYS_UI", "0").strip().lower() in {"1", "true", "yes", "on"}


def load_redirect_map() -> dict[str, str]:
    if not REDIRECT_MAP_PATH.exists():
        return {}
    try:
        with open(REDIRECT_MAP_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)
            if isinstance(data, dict):
                return {str(k): str(v) for k, v in data.items()}
    except Exception:
        pass
    return {}


REDIRECT_MAP = load_redirect_map()


def redirect_target(path: str) -> str | None:
    normalized = path.rstrip("/") or "/"
    target = REDIRECT_MAP.get(normalized) or REDIRECT_MAP.get(f"{normalized}/")
    if not target:
        return None
    if not target.startswith("/"):
        return f"/{target}"
    if target == normalized:
        return None
    return target

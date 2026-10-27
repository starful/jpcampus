"""Heuristics for the Direct-traffic anomaly investigation.

Generic scripts/scrapers show up in GA as "Direct" sessions because they
carry no referrer and never fire real pageviews with UTM context. This
module only flags such requests -- it never blocks them, since legitimate
search/social crawlers (Googlebot, Twitterbot, ...) must still reach every
page for SEO and social card previews.
"""
from __future__ import annotations

import re

from fastapi import Request

# Search engine / social preview crawlers we always want to serve normally.
_ALLOWED_BOT_RE = re.compile(
    r"googlebot|bingbot|yandexbot|duckduckbot|baiduspider|slurp|"
    r"applebot|facebookexternalhit|twitterbot|slackbot|discordbot|"
    r"telegrambot|linkedinbot|whatsapp",
    re.IGNORECASE,
)

# Generic scripts/scrapers that inflate "Direct" sessions because they
# don't run analytics JS and never carry a referrer or UTM params.
_SUSPECT_BOT_RE = re.compile(
    r"python-requests|python-urllib|go-http-client|okhttp|libwww-perl|"
    r"java/|curl/|wget/|scrapy|headlesschrome|phantomjs|ahrefsbot|"
    r"semrushbot|mj12bot|dotbot|petalbot|bytespider|"
    r"\bbot\b|crawler|spider",
    re.IGNORECASE,
)


def is_suspected_bot(user_agent: str) -> bool:
    """True when the UA looks like a non-essential bot/script, not a known search/social crawler."""
    ua = user_agent or ""
    if not ua.strip():
        return True  # blank UA is almost always a script, not a browser
    if _ALLOWED_BOT_RE.search(ua):
        return False
    return bool(_SUSPECT_BOT_RE.search(ua))


def has_utm_params(request: Request) -> bool:
    return any(key.startswith("utm_") for key in request.query_params.keys())


def describe_traffic(request: Request) -> dict:
    """Snapshot logged for the Direct-traffic anomaly investigation."""
    ua = request.headers.get("User-Agent", "")
    referer = request.headers.get("Referer", "")
    has_utm = has_utm_params(request)
    return {
        "path": request.url.path,
        "user_agent": ua,
        "is_suspected_bot": is_suspected_bot(ua),
        "has_referer": bool(referer),
        "has_utm": has_utm,
        # Referer present but no UTM: GA will likely bucket this as
        # "Direct" even though it came from somewhere -- the anomaly
        # we're chasing separately from bot traffic.
        "referer_without_utm": bool(referer) and not has_utm,
    }

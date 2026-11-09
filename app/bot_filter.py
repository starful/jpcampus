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


# Known utm_source/utm_medium values for the acquisition channels we tag
# ourselves (app webview, email campaigns, SNS shares -- see
# app/social_share.py:append_utm_params) plus common provider names, so we
# can separate real app/email/SNS entries from the catch-all "Direct" bucket.
_APP_UTM_SOURCES = {"app", "ios_app", "android_app", "webview", "inapp"}
_EMAIL_UTM_SOURCES = {"email", "newsletter", "mailchimp", "sendgrid"}
_SNS_UTM_SOURCES = {
    "share_bar", "x", "twitter", "instagram", "facebook", "kakao", "kakaotalk",
    "line", "threads", "tiktok", "naver_blog",
}


def classify_utm_channel(request: Request) -> str:
    """Bucket an inbound request into app/email/sns/other/none by its UTM params."""
    source = (request.query_params.get("utm_source") or "").strip().lower()
    medium = (request.query_params.get("utm_medium") or "").strip().lower()
    if not source and not medium:
        return "none"
    if source in _APP_UTM_SOURCES or medium == "app":
        return "app"
    if source in _EMAIL_UTM_SOURCES or medium == "email":
        return "email"
    if source in _SNS_UTM_SOURCES or medium in {"social", "sns"}:
        return "sns"
    return "other"


def describe_traffic(request: Request) -> dict:
    """Snapshot logged for the Direct-traffic anomaly investigation."""
    ua = request.headers.get("User-Agent", "")
    referer = request.headers.get("Referer", "")
    has_utm = has_utm_params(request)
    is_bot = is_suspected_bot(ua)
    # No referer and no UTM is exactly what GA buckets as "Direct". Pairing
    # this with is_suspected_bot lets us split the 86% Direct spike into
    # bot-inflated vs genuinely direct sessions from the logs alone.
    is_direct_session = not referer and not has_utm
    return {
        "path": request.url.path,
        "user_agent": ua,
        "is_suspected_bot": is_bot,
        "has_referer": bool(referer),
        "has_utm": has_utm,
        # Referer present but no UTM: GA will likely bucket this as
        # "Direct" even though it came from somewhere -- the anomaly
        # we're chasing separately from bot traffic.
        "referer_without_utm": bool(referer) and not has_utm,
        "is_direct_session": is_direct_session,
        "direct_session_is_bot": is_direct_session and is_bot,
        # App/email/SNS entries carry their own utm_source -- logging these
        # separately shows how much of the 86% "Direct" figure is really
        # attributable traffic that GA just can't see the tag for.
        "utm_channel": classify_utm_channel(request),
        "utm_source": request.query_params.get("utm_source", ""),
        "utm_medium": request.query_params.get("utm_medium", ""),
        "utm_campaign": request.query_params.get("utm_campaign", ""),
    }

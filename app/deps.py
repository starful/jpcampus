"""Shared FastAPI dependencies (Jinja2 templates)."""
from __future__ import annotations

from fastapi.templating import Jinja2Templates

from app.config import ADSENSE_CLIENT_ID, DOMAIN, FAMILY_SITE_ID, GA_MEASUREMENT_ID
from app.family_sites import inject_family_context
from app.seo import site_stats
from app.utils import TEMPLATES_DIR

templates = Jinja2Templates(directory=TEMPLATES_DIR)


def configure_template_globals() -> None:
    templates.env.globals["inject_family_context"] = inject_family_context
    templates.env.globals["FAMILY_SITE_ID"] = FAMILY_SITE_ID
    templates.env.globals["ga_measurement_id"] = GA_MEASUREMENT_ID
    templates.env.globals["adsense_client_id"] = ADSENSE_CLIENT_ID
    templates.env.globals["site_url"] = DOMAIN
    templates.env.globals["site_stats"] = site_stats

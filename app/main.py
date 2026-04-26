# app/main.py
from fastapi import FastAPI, Request, HTTPException, Query
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, PlainTextResponse, Response, FileResponse, RedirectResponse
import json
import os
import frontmatter
import markdown
from dotenv import load_dotenv
from datetime import datetime, timezone
from pathlib import Path
from xml.sax.saxutils import escape as xml_escape

# 분리된 유틸 및 API 라우터 임포트
from app.utils import (
    calculate_tag_counts, assign_thumbnails, get_ui_text, 
    load_school_data, load_guides, STATIC_DIR, CONTENT_DIR, TEMPLATES_DIR
)
from app.reactions import router as reactions_router

load_dotenv()
app = FastAPI()

if not os.path.exists(CONTENT_DIR): os.makedirs(CONTENT_DIR)

app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")
templates = Jinja2Templates(directory=TEMPLATES_DIR)

GOOGLE_MAPS_API_KEY = os.getenv("GOOGLE_MAPS_API_KEY")
DOMAIN = os.getenv("SITE_DOMAIN", "https://jpcampus.net").rstrip("/")
ADS_TXT_CONTENT = os.getenv(
    "ADS_TXT_CONTENT",
    "google.com, pub-8780435268193938, DIRECT, f08c47fec0942fa0"
)
GA_MEASUREMENT_ID = os.getenv("GA_MEASUREMENT_ID", "G-EDJL0618LL")
ADSENSE_CLIENT_ID = os.getenv("ADSENSE_CLIENT_ID", "ca-pub-8780435268193938")
REDIRECT_MAP_PATH = Path(BASE_DIR := os.path.dirname(os.path.abspath(__file__))) / "redirects.json"


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
templates.env.globals["ga_measurement_id"] = GA_MEASUREMENT_ID
templates.env.globals["adsense_client_id"] = ADSENSE_CLIENT_ID


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


def content_lastmod(*filenames: str) -> str:
    timestamps: list[float] = []
    for filename in filenames:
        filepath = os.path.join(CONTENT_DIR, filename)
        if os.path.exists(filepath):
            timestamps.append(os.path.getmtime(filepath))
    if not timestamps:
        return datetime.now(timezone.utc).strftime("%Y-%m-%d")
    return datetime.fromtimestamp(max(timestamps), timezone.utc).strftime("%Y-%m-%d")


def _redirect_target(path: str) -> str | None:
    normalized = path.rstrip("/") or "/"
    target = REDIRECT_MAP.get(normalized) or REDIRECT_MAP.get(f"{normalized}/")
    if not target:
        return None
    if not target.startswith("/"):
        return f"/{target}"
    if target == normalized:
        return None
    return target


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


def pick_related_guides(item: dict, item_type: str, lang: str, limit: int = 4) -> list[dict]:
    guides = load_guides(lang)
    source_text = ""
    if item_type == "guide":
        source_text = f"{item.get('title', '')} {item.get('description', '')}".lower()
    else:
        basic = item.get("basic_info", {}) or {}
        source_text = f"{basic.get('name_en', '')} {basic.get('address', '')}".lower()

    city_keywords = ["tokyo", "osaka", "kyoto", "nagoya", "fukuoka", "hokkaido", "japan"]
    matched = [kw for kw in city_keywords if kw in source_text]
    related = []
    for guide in guides:
        guide_text = f"{guide.get('title', '')} {guide.get('description', '')}".lower()
        if any(kw in guide_text for kw in matched):
            related.append(guide)
    if len(related) < limit:
        existing_links = {g.get("link") for g in related}
        for guide in guides:
            if guide.get("link") not in existing_links:
                related.append(guide)
            if len(related) >= limit:
                break
    return related[:limit]


def pick_related_schools(item: dict, lang: str, limit: int = 4) -> list[dict]:
    schools, _ = load_school_data(lang)
    source_text = f"{item.get('title', '')} {item.get('description', '')}".lower()
    wants_university = "university" in source_text or "eju" in source_text
    wants_school = "language school" in source_text or "jlpt" in source_text
    city_keywords = ["東京", "大阪", "京都", "名古屋", "福岡", "tokyo", "osaka", "kyoto", "nagoya", "fukuoka"]

    related = []
    for school in schools:
        basic = school.get("basic_info", {}) or {}
        address = basic.get("address", "")
        address_lower = address.lower()
        category = school.get("category")

        if wants_university and category != "university":
            continue
        if wants_school and category == "university":
            continue
        if any(kw in source_text for kw in ["tokyo", "東京"]) and not ("tokyo" in address_lower or "東京都" in address):
            continue
        if any(kw in source_text for kw in ["osaka", "大阪"]) and not ("osaka" in address_lower or "大阪府" in address):
            continue

        if any(kw in source_text for kw in city_keywords):
            related.append(school)
        if len(related) >= limit:
            break

    if len(related) < limit:
        for school in schools:
            if school not in related:
                related.append(school)
            if len(related) >= limit:
                break

    return assign_thumbnails(related[:limit], "university" if wants_university else "school")


@app.middleware("http")
async def legacy_redirect_middleware(request: Request, call_next):
    response = await call_next(request)
    if response.status_code != 404:
        return response
    if request.url.path.startswith("/api") or request.url.path.startswith("/static"):
        return response

    target = _redirect_target(request.url.path)
    if not target:
        return response

    query = request.url.query
    redirect_url = f"{target}?{query}" if query and "?" not in target else target
    return RedirectResponse(url=redirect_url, status_code=301)

# 좋아요/싫어요 API 연결
app.include_router(reactions_router, prefix="/api")

# ==========================================
# 기본 웹 페이지 라우터 (HTML 렌더링)
# ==========================================
@app.get("/ads.txt", response_class=PlainTextResponse)
async def ads_txt(): return ADS_TXT_CONTENT

@app.get("/sitemap.xml", response_class=PlainTextResponse)
async def sitemap():
    entries: list[dict[str, str]] = []

    def add_entry(path: str, lastmod: str, changefreq: str, priority: str):
        alternates = build_hreflang_urls(path)
        entries.append({
            "loc": alternates["en"],
            "lastmod": lastmod,
            "changefreq": changefreq,
            "priority": priority,
            "alt_en": alternates["en"],
            "alt_ko": alternates["ko"],
            "alt_default": alternates["x-default"],
        })
        entries.append({
            "loc": alternates["ko"],
            "lastmod": lastmod,
            "changefreq": changefreq,
            "priority": priority,
            "alt_en": alternates["en"],
            "alt_ko": alternates["ko"],
            "alt_default": alternates["x-default"],
        })

    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    add_entry("/", today, "daily", "1.0")
    for page in ["/about", "/guide", "/schools", "/universities", "/contact", "/policy"]:
        add_entry(page, today, "weekly", "0.8")

    schools_en, _ = load_school_data("en")
    for school in schools_en:
        school_id = school.get("id")
        if not school_id:
            continue
        add_entry(
            f"/school/{school_id}",
            content_lastmod(f"{school_id}.md", f"{school_id}_kr.md"),
            "weekly",
            "0.8",
        )

    guides_en = load_guides("en")
    for guide in guides_en:
        slug = guide["link"].split("/")[-1].split("?")[0]
        add_entry(
            f"/guide/{slug}",
            content_lastmod(f"guide_{slug}.md", f"guide_{slug}_kr.md"),
            "weekly",
            "0.7",
        )

    unique_entries = {(e["loc"], e["lastmod"], e["changefreq"], e["priority"]): e for e in entries}
    xml_items = []
    for entry in sorted(unique_entries.values(), key=lambda x: x["loc"]):
        xml_items.append(
            f"""
        <url>
            <loc>{xml_escape(entry["loc"])}</loc>
            <lastmod>{entry["lastmod"]}</lastmod>
            <changefreq>{entry["changefreq"]}</changefreq>
            <priority>{entry["priority"]}</priority>
            <xhtml:link rel="alternate" hreflang="en" href="{xml_escape(entry["alt_en"])}" />
            <xhtml:link rel="alternate" hreflang="ko" href="{xml_escape(entry["alt_ko"])}" />
            <xhtml:link rel="alternate" hreflang="x-default" href="{xml_escape(entry["alt_default"])}" />
        </url>"""
        )

    xml_content = f"""<?xml version="1.0" encoding="UTF-8"?>
    <urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9"
            xmlns:xhtml="http://www.w3.org/1999/xhtml">
        {''.join(xml_items)}
    </urlset>"""
    return Response(content=xml_content, media_type="application/xml")

@app.get("/robots.txt", response_class=PlainTextResponse)
async def robots():
    return f"User-agent: *\nAllow: /\nSitemap: {DOMAIN}/sitemap.xml"

@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request, lang: str = Query("en")):
    schools_data, updated_at = load_school_data(lang)
    all_guides = load_guides(lang)
    ui = get_ui_text(lang)

    featured_guides =[g for g in all_guides if g.get('is_featured')]
    if not featured_guides: featured_guides = all_guides[:6]
    else: featured_guides = featured_guides[:6]

    latest_schools = assign_thumbnails([s for s in schools_data if s.get('category') != 'university'][:6], "school")
    latest_universities = assign_thumbnails([s for s in schools_data if s.get('category') == 'university'][:6], "university")
    tags_with_counts = calculate_tag_counts(schools_data)
    
    # [방어 로직] basic_info가 없는 불량 데이터를 완벽하게 커버
    university_list =[]
    for s in schools_data:
        if s.get('category') == 'university':
            b_info = s.get('basic_info') or {}
            university_list.append({
                "name_ja": b_info.get('name_ja', ''),
                "name_en": b_info.get('name_display') or b_info.get('name_en') or ''
            })

    # [수정] 최신 문법: request 객체를 첫 번째 인자로 전달
    return templates.TemplateResponse(request, "index.html", {
        "schools_json": json.dumps({"schools": schools_data}, ensure_ascii=False),
        "maps_api_key": GOOGLE_MAPS_API_KEY, 
        "updated_at": updated_at,
        "total_schools": len(schools_data),
        "featured_guides": featured_guides, 
        "latest_schools": latest_schools, 
        "latest_universities": latest_universities, 
        "latest_guides":[g for g in all_guides if g not in featured_guides][:6],
        "tags_with_counts": tags_with_counts, 
        "university_list_json": university_list,
        "current_lang": lang,
        "ui": ui,
        "canonical_url": build_canonical_url("/", lang),
        "hreflang_urls": build_hreflang_urls("/"),
        "meta_title": build_meta_title("Study in Japan: Schools, Universities, Essential Guides", lang),
        "meta_description": build_meta_description(
            "Find Japanese language schools and universities with practical student guides.",
            "Find Japanese language schools and universities with practical student guides."
        ),
    })

@app.get("/school/{school_id}", response_class=HTMLResponse)
async def read_school_detail(request: Request, school_id: str, lang: str = Query("en")):
    filename = f"{school_id}_kr.md" if lang == "kr" else f"{school_id}.md"
    md_path = os.path.join(CONTENT_DIR, filename)
    if not os.path.exists(md_path) and lang == "kr":
        md_path = os.path.join(CONTENT_DIR, f"{school_id}.md")
    
    if not os.path.exists(md_path):
        raise HTTPException(status_code=404, detail="School content file not found")
    
    post = frontmatter.load(md_path)
    content_html = markdown.markdown(post.content, extensions=['tables', 'fenced_code', 'nl2br'])
    item = post.metadata
    item_type = 'university' if item.get('category') == 'university' else 'school'

    # [수정] 최신 문법 적용
    return templates.TemplateResponse(request, "detail.html", { 
        "item": item, "item_type": item_type, 
        "content_body": content_html, "current_lang": lang, "ui": get_ui_text(lang),
        "canonical_url": build_canonical_url(f"/school/{school_id}", lang),
        "hreflang_urls": build_hreflang_urls(f"/school/{school_id}"),
        "updated_at": default_updated_at(),
        "related_guides": pick_related_guides(item, item_type, lang),
        "meta_title": build_meta_title(
            item.get("basic_info", {}).get("name_en") or item.get("basic_info", {}).get("name_ja") or "School Guide",
            lang
        ),
        "meta_description": build_meta_description(
            item.get("basic_info", {}).get("address", ""),
            "Compare school details, tuition clues, and student-ready preparation tips."
        ),
    })

@app.get("/guide/{slug}", response_class=HTMLResponse)
async def guide_detail(request: Request, slug: str, lang: str = Query("en")):
    filename = f"guide_{slug}_kr.md" if lang == "kr" else f"guide_{slug}.md"
    md_path = os.path.join(CONTENT_DIR, filename)
    if not os.path.exists(md_path) and lang == "kr":
        md_path = os.path.join(CONTENT_DIR, f"guide_{slug}.md")

    if not os.path.exists(md_path):
        raise HTTPException(status_code=404, detail="Guide content file not found")

    post = frontmatter.load(md_path)
    content_html = markdown.markdown(post.content, extensions=['tables', 'fenced_code', 'nl2br'])
    item = post.metadata

    # [수정] 최신 문법 적용
    return templates.TemplateResponse(request, "detail.html", { 
        "item": item, "item_type": "guide", 
        "content_body": content_html, "current_lang": lang, "ui": get_ui_text(lang),
        "canonical_url": build_canonical_url(f"/guide/{slug}", lang),
        "hreflang_urls": build_hreflang_urls(f"/guide/{slug}"),
        "updated_at": default_updated_at(),
        "related_schools": pick_related_schools(item, lang),
        "related_guides": pick_related_guides(item, "guide", lang),
        "meta_title": build_meta_title(item.get("title", "Study in Japan Guide"), lang),
        "meta_description": build_meta_description(
            item.get("description", ""),
            "Actionable study-in-Japan guide with practical decisions and student checklists."
        ),
    })

@app.get("/schools", response_class=HTMLResponse)
async def school_list(request: Request, lang: str = Query("en")):
    schools_data, _ = load_school_data(lang)
    schools = assign_thumbnails([s for s in schools_data if s.get('category') != 'university'], "school")
    
    # [수정] 최신 문법 적용
    return templates.TemplateResponse(request, "list.html", {
        "items": schools, "item_type": "school", 
        "title": "All Language Schools" if lang == 'en' else "일본어학교 목록",
        "description": "Browse all language schools across Japan." if lang == "en" else "일본 전역의 일본어학교를 확인하세요.",
        "current_lang": lang, "ui": get_ui_text(lang),
        "canonical_url": build_canonical_url("/schools", lang),
        "hreflang_urls": build_hreflang_urls("/schools"),
        "updated_at": default_updated_at(),
        "meta_title": build_meta_title("All Language Schools in Japan", lang),
        "meta_description": build_meta_description(
            "Compare language schools by city, tuition, and student lifestyle fit.",
            "Compare language schools by city, tuition, and student lifestyle fit."
        ),
    })

@app.get("/universities", response_class=HTMLResponse)
async def university_list(request: Request, lang: str = Query("en")):
    schools_data, _ = load_school_data(lang)
    universities = assign_thumbnails([s for s in schools_data if s.get('category') == 'university'], "university")
    
    # [수정] 최신 문법 적용
    return templates.TemplateResponse(request, "list.html", {
        "items": universities, "item_type": "university", 
        "title": "All Universities" if lang == 'en' else "일본 대학 목록",
        "description": "Explore universities in Japan for international students." if lang == "en" else "유학생을 위한 일본 대학교 정보를 확인하세요.",
        "current_lang": lang, "ui": get_ui_text(lang),
        "canonical_url": build_canonical_url("/universities", lang),
        "hreflang_urls": build_hreflang_urls("/universities"),
        "updated_at": default_updated_at(),
        "meta_title": build_meta_title("Universities in Japan for International Students", lang),
        "meta_description": build_meta_description(
            "Find university options in Japan with practical comparisons and prep guidance.",
            "Find university options in Japan with practical comparisons and prep guidance."
        ),
    })

@app.get("/guide", response_class=HTMLResponse)
async def guide_list_page(request: Request, lang: str = Query("en")):
    guides = load_guides(lang)
    
    # [수정] 최신 문법 적용
    return templates.TemplateResponse(request, "list.html", {
        "items": guides, "item_type": "guide", 
        "title": "Essential Guides" if lang == 'en' else "유학 가이드",
        "description": "Read practical study-abroad guides for life in Japan." if lang == "en" else "일본 유학 생활 실전 가이드를 확인하세요.",
        "current_lang": lang, "ui": get_ui_text(lang),
        "canonical_url": build_canonical_url("/guide", lang),
        "hreflang_urls": build_hreflang_urls("/guide"),
        "updated_at": default_updated_at(),
        "meta_title": build_meta_title("Essential Japan Study Guides", lang),
        "meta_description": build_meta_description(
            "Read practical guides on costs, housing, visas, and student life in Japan.",
            "Read practical guides on costs, housing, visas, and student life in Japan."
        ),
    })

@app.get("/compare", response_class=HTMLResponse)
async def compare_page(request: Request, ids: str = Query(""), lang: str = Query("en")):
    schools_data, _ = load_school_data(lang)
    id_list = [v.strip() for v in ids.split(",") if v.strip()]
    selected = [item for item in schools_data if item.get("id") in id_list]

    if len(selected) < 3:
        fallback = [item for item in schools_data if item.get("id") not in {s.get("id") for s in selected}]
        selected.extend(fallback[: max(0, 3 - len(selected))])

    selected = assign_thumbnails(selected, "school")
    return templates.TemplateResponse(request, "compare.html", {
        "items": selected[:3],
        "current_lang": lang,
        "ui": get_ui_text(lang),
        "title": "School Comparison" if lang == "en" else "학교 비교",
        "description": "Compare tuition, location, and fit in one view." if lang == "en" else "학비, 위치, 특성을 한 화면에서 비교하세요.",
        "canonical_url": build_canonical_url("/compare", lang),
        "hreflang_urls": build_hreflang_urls("/compare"),
        "updated_at": default_updated_at(),
        "meta_title": build_meta_title("Compare Schools in Japan", lang),
        "meta_description": build_meta_description(
            "Compare selected schools and universities side by side.",
            "Compare selected schools and universities side by side."
        ),
    })

@app.get("/about", response_class=HTMLResponse)
async def about(request: Request, lang: str = Query("en")):
    return templates.TemplateResponse(request, "about.html", {
        "canonical_url": build_canonical_url("/about", lang),
        "current_lang": lang,
        "hreflang_urls": build_hreflang_urls("/about"),
        "updated_at": default_updated_at(),
        "meta_title": build_meta_title("About JP Campus", lang),
        "meta_description": build_meta_description(
            "Learn how JP Campus helps international students choose schools in Japan.",
            "Learn how JP Campus helps international students choose schools in Japan."
        ),
    })

@app.get("/contact", response_class=HTMLResponse)
async def contact(request: Request, lang: str = Query("en")):
    return templates.TemplateResponse(request, "contact.html", {
        "canonical_url": build_canonical_url("/contact", lang),
        "current_lang": lang,
        "hreflang_urls": build_hreflang_urls("/contact"),
        "updated_at": default_updated_at(),
        "meta_title": build_meta_title("Contact JP Campus", lang),
        "meta_description": build_meta_description(
            "Contact JP Campus for corrections, feedback, or collaboration.",
            "Contact JP Campus for corrections, feedback, or collaboration."
        ),
    })

@app.get("/policy", response_class=HTMLResponse)
async def policy(request: Request, lang: str = Query("en")):
    return templates.TemplateResponse(request, "policy.html", {
        "canonical_url": build_canonical_url("/policy", lang),
        "current_lang": lang,
        "hreflang_urls": build_hreflang_urls("/policy"),
        "updated_at": default_updated_at(),
        "meta_title": build_meta_title("Privacy Policy", lang),
        "meta_description": build_meta_description(
            "Read how JP Campus handles privacy, cookies, and data usage.",
            "Read how JP Campus handles privacy, cookies, and data usage."
        ),
    })

@app.get("/favicon.ico", include_in_schema=False)
async def favicon(): return FileResponse(os.path.join(STATIC_DIR, "img", "logo.png"))
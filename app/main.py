# app/main.py
from fastapi import FastAPI, Request, HTTPException, Query
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, PlainTextResponse, Response, FileResponse
import json
import os
import frontmatter
import markdown
from dotenv import load_dotenv
from datetime import datetime

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
DOMAIN = "https://jpcampus.net"
ADS_TXT_CONTENT = "google.com, pub-8780435268193938, DIRECT, f08c47fec0942fa0"


def build_canonical_url(path: str, lang: str | None = None) -> str:
    canonical = f"{DOMAIN}{path}"
    if lang == "kr":
        return f"{canonical}?lang=kr"
    return canonical

# 좋아요/싫어요 API 연결
app.include_router(reactions_router, prefix="/api")

# ==========================================
# 기본 웹 페이지 라우터 (HTML 렌더링)
# ==========================================
@app.get("/ads.txt", response_class=PlainTextResponse)
async def ads_txt(): return ADS_TXT_CONTENT

@app.get("/sitemap.xml", response_class=PlainTextResponse)
async def sitemap():
    urls = []
    base_paths =["", "about", "guide", "schools", "universities", "contact", "policy"]
    for path in base_paths:
        urls.append(f"{DOMAIN}/{path}") 
        urls.append(f"{DOMAIN}/{path}?lang=kr") 

    schools_en, _ = load_school_data("en")
    for s in schools_en:
        if s.get('id'):
            urls.append(f"{DOMAIN}/school/{s['id']}")
            urls.append(f"{DOMAIN}/school/{s['id']}?lang=kr")

    guides_en = load_guides("en")
    for g in guides_en:
        slug = g['link'].split('/')[-1].split('?')[0]
        urls.append(f"{DOMAIN}/guide/{slug}")
        urls.append(f"{DOMAIN}/guide/{slug}?lang=kr")

    urls = list(set(urls))
    xml_urls = "".join([f'<url><loc>{url}</loc><changefreq>weekly</changefreq><priority>0.8</priority></url>' for url in urls])
    
    xml_content = f"""<?xml version="1.0" encoding="UTF-8"?>
    <urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
        {xml_urls}
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
        "university_list_json": json.dumps(university_list, ensure_ascii=False),
        "current_lang": lang,
        "ui": ui,
        "canonical_url": build_canonical_url("/", lang)
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
        "canonical_url": build_canonical_url(f"/school/{school_id}", lang)
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
        "canonical_url": build_canonical_url(f"/guide/{slug}", lang)
    })

@app.get("/schools", response_class=HTMLResponse)
async def school_list(request: Request, lang: str = Query("en")):
    schools_data, _ = load_school_data(lang)
    schools = assign_thumbnails([s for s in schools_data if s.get('category') != 'university'], "school")
    
    # [수정] 최신 문법 적용
    return templates.TemplateResponse(request, "list.html", {
        "items": schools, "item_type": "school", 
        "title": "All Language Schools" if lang == 'en' else "일본어학교 목록",
        "current_lang": lang, "ui": get_ui_text(lang),
        "canonical_url": build_canonical_url("/schools", lang)
    })

@app.get("/universities", response_class=HTMLResponse)
async def university_list(request: Request, lang: str = Query("en")):
    schools_data, _ = load_school_data(lang)
    universities = assign_thumbnails([s for s in schools_data if s.get('category') == 'university'], "university")
    
    # [수정] 최신 문법 적용
    return templates.TemplateResponse(request, "list.html", {
        "items": universities, "item_type": "university", 
        "title": "All Universities" if lang == 'en' else "일본 대학 목록",
        "current_lang": lang, "ui": get_ui_text(lang),
        "canonical_url": build_canonical_url("/universities", lang)
    })

@app.get("/guide", response_class=HTMLResponse)
async def guide_list_page(request: Request, lang: str = Query("en")):
    guides = load_guides(lang)
    
    # [수정] 최신 문법 적용
    return templates.TemplateResponse(request, "list.html", {
        "items": guides, "item_type": "guide", 
        "title": "Essential Guides" if lang == 'en' else "유학 가이드",
        "current_lang": lang, "ui": get_ui_text(lang),
        "canonical_url": build_canonical_url("/guide", lang)
    })

@app.get("/about", response_class=HTMLResponse)
async def about(request: Request, lang: str = Query("en")):
    return templates.TemplateResponse(request, "about.html", {
        "canonical_url": build_canonical_url("/about", lang),
        "current_lang": lang,
    })

@app.get("/contact", response_class=HTMLResponse)
async def contact(request: Request, lang: str = Query("en")):
    return templates.TemplateResponse(request, "contact.html", {
        "canonical_url": build_canonical_url("/contact", lang),
        "current_lang": lang,
    })

@app.get("/policy", response_class=HTMLResponse)
async def policy(request: Request, lang: str = Query("en")):
    return templates.TemplateResponse(request, "policy.html", {
        "canonical_url": build_canonical_url("/policy", lang),
        "current_lang": lang,
        "updated_at": datetime.utcnow().strftime("%Y-%m-%d"),
    })

@app.get("/favicon.ico", include_in_schema=False)
async def favicon(): return FileResponse(os.path.join(STATIC_DIR, "img", "logo.png"))
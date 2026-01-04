# app/main.py

from fastapi import FastAPI, Request, HTTPException
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, PlainTextResponse, Response
import json
import os
import frontmatter
import markdown
from dotenv import load_dotenv
import glob
from app.utils import calculate_tag_counts

# --- 초기 설정 ---
load_dotenv()

app = FastAPI()

# 파일 경로를 절대 경로 기준으로 설정
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
STATIC_DIR = os.path.join(BASE_DIR, "static")
CONTENT_DIR = os.path.join(BASE_DIR, "content")
TEMPLATES_DIR = os.path.join(BASE_DIR, "templates")

app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")
templates = Jinja2Templates(directory=TEMPLATES_DIR)

# 환경 변수 및 상수
GOOGLE_MAPS_API_KEY = os.getenv("GOOGLE_MAPS_API_KEY")
DOMAIN = "https://jpcampus.net"
DATA_FILE = os.path.join(STATIC_DIR, "json", "schools_data.json")
ADS_TXT_CONTENT = "google.com, pub-8780435268193938, DIRECT, f08c47fec0942fa0"

# --- 안정적인 데이터 로딩 함수 ---
def load_school_data():
    if not os.path.exists(DATA_FILE):
        return [], ""
    try:
        with open(DATA_FILE, 'r', encoding='utf-8') as f:
            data = json.load(f)
            schools = data.get('schools', [])
            updated_at = data.get('last_updated', '')
            if not isinstance(schools, list):
                return [], updated_at
            return schools, updated_at
    except Exception as e:
        print(f"Error loading data: {e}")
        return [], ""

# --- 라우팅 (Routing) ---

@app.get("/ads.txt", response_class=PlainTextResponse)
async def ads_txt():
    return ADS_TXT_CONTENT

# --- [복구됨] 사이트맵 생성 라우트 ---
@app.get("/sitemap.xml", response_class=PlainTextResponse)
async def sitemap():
    urls = [f"{DOMAIN}/{path}" for path in ["", "about", "guide", "schools", "universities", "contact", "policy"]]
    
    # 학교 및 대학 URL 추가
    schools_data, _ = load_school_data()
    for s in schools_data:
        if s.get('id'):
            urls.append(f"{DOMAIN}/school/{s['id']}")
            
    # 가이드 URL 추가
    guide_files = glob.glob(os.path.join(CONTENT_DIR, "guide_*.md"))
    for filepath in guide_files:
        try:
            post = frontmatter.load(filepath)
            if slug := post.metadata.get('id'):
                urls.append(f"{DOMAIN}/guide/{slug}")
        except Exception:
            pass
            
    xml_urls = "".join([f'<url><loc>{url}</loc><changefreq>weekly</changefreq></url>' for url in urls])
    return Response(content=f'<?xml version="1.0" encoding="UTF-8"?><urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">{xml_urls}</urlset>', media_type="application/xml")

@app.get("/robots.txt", response_class=PlainTextResponse)
async def robots():
    return f"User-agent: *\nAllow: /\nSitemap: {DOMAIN}/sitemap.xml"


@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    schools_data, updated_at = load_school_data()

    # 메인 화면 표시 건수 6개로 적용
    latest_schools = [s for s in schools_data if s.get('category') != 'university'][:6]
    latest_universities = [s for s in schools_data if s.get('category') == 'university'][:6]
    
    tags_with_counts = calculate_tag_counts(schools_data)
    university_list = [
        {"name_ja": s.get('basic_info', {}).get('name_ja'), "name_en": s.get('basic_info', {}).get('name_en')}
        for s in schools_data if s.get('category') == 'university' and s.get('basic_info', {}).get('name_en')
    ]
    guides = []
    guide_files = glob.glob(os.path.join(CONTENT_DIR, "guide_*.md"))
    guide_files.sort(key=os.path.getmtime, reverse=True)
    for filepath in guide_files[:6]: # 가이드도 6개 표시
        try:
            post = frontmatter.load(filepath)
            meta = post.metadata
            guides.append({
                "title": meta.get('title', 'Untitled'), "description": meta.get('description', ''),
                "category": meta.get('category', 'Guide'), "link": f"/guide/{meta.get('id')}",
                "thumbnail": meta.get('thumbnail', '')
            })
        except Exception: pass

    return templates.TemplateResponse("index.html", {
        "request": request, "schools_json": json.dumps({"schools": schools_data}, ensure_ascii=False),
        "maps_api_key": GOOGLE_MAPS_API_KEY, "meta_url": f"{DOMAIN}/", "updated_at": updated_at,
        "latest_schools": latest_schools, "latest_universities": latest_universities, "latest_guides": guides,
        "tags_with_counts": tags_with_counts, "university_list_json": json.dumps(university_list, ensure_ascii=False)
    })

# (이하 상세 페이지 및 리스트 페이지 라우트는 이전 답변과 동일)
@app.get("/school/{school_id}", response_class=HTMLResponse)
async def read_school_detail(request: Request, school_id: str):
    md_path = os.path.join(CONTENT_DIR, f"{school_id}.md")
    if not os.path.exists(md_path):
        raise HTTPException(status_code=404, detail="School content file not found")
    
    post = frontmatter.load(md_path)
    content_html = markdown.markdown(post.content, extensions=['tables', 'fenced_code', 'nl2br'])
    item = post.metadata
    item_type = 'university' if item.get('category') == 'university' else 'school'

    return templates.TemplateResponse("detail.html", { "request": request, "item": item, "item_type": item_type, "content_body": content_html })

@app.get("/guide/{slug}", response_class=HTMLResponse)
async def guide_detail(request: Request, slug: str):
    md_path = os.path.join(CONTENT_DIR, f"guide_{slug}.md")
    if not os.path.exists(md_path):
        raise HTTPException(status_code=404, detail="Guide content file not found")

    post = frontmatter.load(md_path)
    content_html = markdown.markdown(post.content, extensions=['tables', 'fenced_code', 'nl2br'])
    item = post.metadata

    return templates.TemplateResponse("detail.html", { "request": request, "item": item, "item_type": "guide", "content_body": content_html })

@app.get("/schools", response_class=HTMLResponse)
async def school_list(request: Request):
    schools_data, _ = load_school_data()
    schools = [s for s in schools_data if s.get('category') != 'university']
    
    school_placeholders = ['https://images.unsplash.com/photo-1544531586-fde5298cdd40?w=500', 'https://images.unsplash.com/photo-1523240795612-9a054b0db644?w=500', 'https://images.unsplash.com/photo-1509062522246-3755977927d7?w=500']
    for i, item in enumerate(schools): item['thumbnail'] = school_placeholders[i % len(school_placeholders)]
    return templates.TemplateResponse("list.html", {"request": request, "items": schools, "item_type": "school", "title": "All Language Schools"})

@app.get("/universities", response_class=HTMLResponse)
async def university_list(request: Request):
    schools_data, _ = load_school_data()
    universities = [s for s in schools_data if s.get('category') == 'university']
    univ_placeholders = ['https://images.unsplash.com/photo-1562774053-701939374585?w=500', 'https://images.unsplash.com/photo-1541339907198-e08756dedf3f?w=500', 'https://images.unsplash.com/photo-1498243691581-b145c3f54a5a?w=500']
    for i, item in enumerate(universities): item['thumbnail'] = univ_placeholders[i % len(univ_placeholders)]
    return templates.TemplateResponse("list.html", {"request": request, "items": universities, "item_type": "university", "title": "All Universities"})

@app.get("/guide", response_class=HTMLResponse)
async def guide_list_page(request: Request):
    guides = []
    guide_files = glob.glob(os.path.join(CONTENT_DIR, "guide_*.md"))
    guide_files.sort(key=os.path.getmtime, reverse=True)
    for filepath in guide_files:
        try:
            post = frontmatter.load(filepath)
            meta = post.metadata
            guides.append({ "title": meta.get('title'), "description": meta.get('description'), "category": meta.get('category'), "link": f"/guide/{meta.get('id')}", "thumbnail": meta.get('thumbnail'), "item_type": "guide" })
        except Exception: pass
    return templates.TemplateResponse("list.html", {"request": request, "items": guides, "item_type": "guide", "title": "Essential Guides"})

@app.get("/about", response_class=HTMLResponse)
async def about(request: Request): return templates.TemplateResponse("about.html", {"request": request})
@app.get("/contact", response_class=HTMLResponse)
async def contact(request: Request): return templates.TemplateResponse("contact.html", {"request": request})
@app.get("/policy", response_class=HTMLResponse)
async def policy(request: Request): return templates.TemplateResponse("policy.html", {"request": request})
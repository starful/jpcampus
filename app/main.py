from fastapi import FastAPI, Request, HTTPException, Response
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, PlainTextResponse
import json
import os
import re
import frontmatter
import markdown
from dotenv import load_dotenv
import glob

load_dotenv()

app = FastAPI()

# 정적 파일 마운트
app.mount("/static", StaticFiles(directory="app/static"), name="static")
templates = Jinja2Templates(directory="app/templates")

# 환경 변수
GOOGLE_MAPS_API_KEY = os.getenv("GOOGLE_MAPS_API_KEY")
DOMAIN = "https://jpcampus.net"
DATA_FILE = "app/static/json/schools_data.json"

# Ads.txt (애드센스용)
ADS_TXT_CONTENT = """google.com, pub-8780435268193938, DIRECT, f08c47fec0942fa0"""

@app.get("/ads.txt", response_class=PlainTextResponse)
async def ads_txt():
    return ADS_TXT_CONTENT

@app.get("/sitemap.xml", response_class=PlainTextResponse)
async def sitemap():
    # 1. 고정 페이지 URL
    urls = [
        f"{DOMAIN}/",
        f"{DOMAIN}/about",
        f"{DOMAIN}/guide",
        f"{DOMAIN}/schools",
        f"{DOMAIN}/universities",
        f"{DOMAIN}/contact",
        f"{DOMAIN}/policy"
    ]
    
    # 2. 학교 및 대학 상세 페이지 URL
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, 'r', encoding='utf-8') as f:
            data = json.load(f)
            for s in data.get('schools', []):
                urls.append(f"{DOMAIN}/school/{s['id']}")
    
    # 3. 가이드 상세 페이지 URL
    guide_dir = "app/content"
    guide_files = glob.glob(os.path.join(guide_dir, "guide_*.md"))
    
    for filepath in guide_files:
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                post = frontmatter.load(f)
                slug = post.metadata.get('id')
                if slug:
                    urls.append(f"{DOMAIN}/guide/{slug}")
        except Exception:
            pass
    
    # XML 생성
    xml = '<?xml version="1.0" encoding="UTF-8"?>\n'
    xml += '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
    for url in urls:
        xml += f'  <url><loc>{url}</loc><changefreq>weekly</changefreq></url>\n'
    xml += '</urlset>'
    
    return Response(content=xml, media_type="application/xml")

@app.get("/robots.txt", response_class=PlainTextResponse)
async def robots():
    return f"User-agent: *\nAllow: /\nSitemap: {DOMAIN}/sitemap.xml"
    
# ---------------------------------------------------------
# 1. 메인 페이지
# ---------------------------------------------------------
@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    schools_data = []
    updated_at = ""
    
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, 'r', encoding='utf-8') as f:
            data = json.load(f)
            schools_data = data.get('schools', [])
            updated_at = data.get('last_updated', '')

    school_count = len(schools_data)
    meta_desc = f"Compare {school_count} Japanese language schools & universities. Tuition, location, and nationality ratio."

    # 학교/대학 데이터 분리
    latest_schools = [s for s in schools_data if s.get('category') != 'university'][:4]
    latest_universities = [s for s in schools_data if s.get('category') == 'university'][:4]

    # 가이드 목록 가져오기 (최신 4개)
    guides = []
    guide_dir = "app/content"
    guide_files = glob.glob(os.path.join(guide_dir, "guide_*.md"))
    guide_files.sort(reverse=True) 
    
    for filepath in guide_files[:4]:
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                post = frontmatter.load(f)
                meta = post.metadata
                guides.append({
                    "title": meta.get('title'),
                    "description": meta.get('description'),
                    "category": meta.get('tags', ['Guide'])[0],
                    "link": f"/guide/{meta.get('id')}",
                    "thumbnail": meta.get('thumbnail')
                })
        except Exception as e:
            print(f"Error loading guide for home: {e}")

    return templates.TemplateResponse("index.html", {
        "request": request,
        "schools_json": json.dumps(schools_data, ensure_ascii=False),
        "maps_api_key": GOOGLE_MAPS_API_KEY,
        "meta_url": f"{DOMAIN}/",
        "meta_title": "JP Campus - Japanese Language School Map",
        "meta_desc": meta_desc,
        "updated_at": updated_at,
        "latest_schools": latest_schools,
        "latest_universities": latest_universities,
        "latest_guides": guides
    })

# ---------------------------------------------------------
# 2. 상세 페이지 (학교/대학)
# ---------------------------------------------------------
@app.get("/school/{school_id}", response_class=HTMLResponse)
async def read_school_detail(request: Request, school_id: str):
    md_path = f"app/content/{school_id}.md"
    
    if not os.path.exists(md_path):
        raise HTTPException(status_code=404, detail="School not found")

    with open(md_path, 'r', encoding='utf-8') as f:
        post = frontmatter.load(f)
    
    raw_content = post.content
    # 마크다운 전처리 및 변환
    raw_content = re.sub(r'\|([^\n]+)\|\s*\|(:?-+:?)\|', r'|\1|\n|\2|', raw_content)
    raw_content = re.sub(r'\.\s*\*', '.\n\n*', raw_content)
    content_html = markdown.markdown(raw_content, extensions=['tables', 'fenced_code', 'nl2br', 'sane_lists'])
    
    school = post.metadata
    
    # [SEO 최적화] Title & Description 생성
    name_ja = school.get('basic_info', {}).get('name_ja', 'Unknown')
    name_en = school.get('basic_info', {}).get('name_en', '')
    
    # Title
    if name_en:
        page_title = f"{name_en} ({name_ja}) - Tuition & Admission Info | JP Campus"
    else:
        page_title = f"{name_ja} - Japanese Language School Info | JP Campus"

    # Description
    tuition = school.get('tuition', {}).get('yearly_tuition', 'N/A')
    if isinstance(tuition, int):
        tuition_str = f"¥{tuition:,}"
    else:
        tuition_str = "Contact for details"
        
    location = school.get('basic_info', {}).get('address', 'Japan')
    page_desc = f"Comprehensive guide for {name_ja}. Yearly tuition: {tuition_str}. Located in {location}. Find admission requirements, dormitory info, and scholarships."

    # OG Image 설정
    thumbnail_path = school.get('thumbnail', '/static/img/og-image.png')
    if thumbnail_path.startswith('/'):
        og_image_url = f"{DOMAIN}{thumbnail_path}"
    else:
        og_image_url = thumbnail_path

    return templates.TemplateResponse("detail.html", {
        "request": request,
        "school": school,
        "content_body": content_html,
        "meta_url": f"{DOMAIN}/school/{school_id}",
        "meta_title": page_title,
        "meta_desc": page_desc,
        "og_image": og_image_url,
        "maps_api_key": GOOGLE_MAPS_API_KEY
    })

# ---------------------------------------------------------
# 3. 가이드 및 리스트 페이지
# ---------------------------------------------------------

@app.get("/guide", response_class=HTMLResponse)
async def guide_list_page(request: Request):
    """가이드 목록 페이지"""
    guides = []
    guide_files = glob.glob(os.path.join("app/content", "guide_*.md"))
    guide_files.sort(reverse=True)
    
    for filepath in guide_files:
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                post = frontmatter.load(f)
                meta = post.metadata
                guides.append({
                    "title": meta.get('title'),
                    "description": meta.get('description'),
                    "category": meta.get('tags', ['Guide'])[0],
                    "link": f"/guide/{meta.get('id')}",
                    "thumbnail": meta.get('thumbnail')
                })
        except Exception as e:
            print(f"Error loading guide: {e}")
            
    return templates.TemplateResponse("guide_list.html", {
        "request": request,
        "guides": guides,
        "meta_title": "Essential Guides for Japan - JP Campus",
        "meta_desc": "Everything you need to know before studying in Japan."
    })

@app.get("/guide/{slug}", response_class=HTMLResponse)
async def guide_detail(request: Request, slug: str):
    """가이드 상세 페이지"""
    filename = f"guide_{slug}.md"
    md_path = os.path.join("app/content", filename)
    
    if not os.path.exists(md_path):
        raise HTTPException(status_code=404, detail="Guide not found")

    with open(md_path, 'r', encoding='utf-8') as f:
        post = frontmatter.load(f)
    
    content_html = markdown.markdown(post.content, extensions=['tables', 'fenced_code', 'nl2br', 'sane_lists'])
    
    meta = post.metadata
    og_image_url = meta.get('thumbnail', f"{DOMAIN}/static/img/og-image.png")

    return templates.TemplateResponse("guide_detail.html", {
        "request": request,
        "guide": meta,
        "content_body": content_html,
        "meta_title": f"{meta['title']} - JP Campus Guide",
        "meta_desc": meta.get('description', ''),
        "meta_url": f"{DOMAIN}/guide/{slug}",
        "og_image": og_image_url
    })

@app.get("/schools", response_class=HTMLResponse)
async def school_list(request: Request):
    """어학원 전체 목록 페이지"""
    with open(DATA_FILE, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    schools = [s for s in data['schools'] if s.get('category') != 'university']
    
    return templates.TemplateResponse("school_list.html", {
        "request": request,
        "items": schools,
        "title": "Japanese Language Schools",
        "description": "Browse all Japanese language schools across Japan."
    })

@app.get("/universities", response_class=HTMLResponse)
async def university_list(request: Request):
    """대학 전체 목록 페이지"""
    with open(DATA_FILE, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    universities = [s for s in data['schools'] if s.get('category') == 'university']
    
    return templates.TemplateResponse("school_list.html", {
        "request": request,
        "items": universities,
        "title": "Universities in Japan",
        "description": "Explore top universities in Japan for international students."
    })

@app.get("/about", response_class=HTMLResponse)
async def about(request: Request):
    return templates.TemplateResponse("about.html", {"request": request})

@app.get("/contact", response_class=HTMLResponse)
async def contact(request: Request):
    return templates.TemplateResponse("contact.html", {"request": request})

@app.get("/policy", response_class=HTMLResponse)
async def policy(request: Request):
    return templates.TemplateResponse("policy.html", {"request": request})
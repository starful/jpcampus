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

# content 폴더가 없으면 생성 (에러 방지)
if not os.path.exists(CONTENT_DIR):
    os.makedirs(CONTENT_DIR)

app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")
templates = Jinja2Templates(directory=TEMPLATES_DIR)

# 환경 변수 및 상수
GOOGLE_MAPS_API_KEY = os.getenv("GOOGLE_MAPS_API_KEY")
DOMAIN = "https://jpcampus.net"
DATA_FILE = os.path.join(STATIC_DIR, "json", "schools_data.json")
ADS_TXT_CONTENT = "google.com, pub-8780435268193938, DIRECT, f08c47fec0942fa0"

# --- 데이터 로딩 헬퍼 함수들 ---

def load_school_data():
    """학교 데이터 JSON 로드"""
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

def load_guides():
    """가이드 마크다운 파일 로드 및 최신순 정렬"""
    guides = []
    # guide_ 로 시작하는 파일만 로드
    guide_files = glob.glob(os.path.join(CONTENT_DIR, "guide_*.md"))
    # 수정 시간 역순 정렬 (최신순)
    guide_files.sort(key=os.path.getmtime, reverse=True)
    
    for filepath in guide_files:
        try:
            post = frontmatter.load(filepath)
            meta = post.metadata
            guides.append({
                "title": meta.get('title', 'Untitled'), 
                "description": meta.get('description', ''),
                "category": meta.get('category', 'Guide'), 
                "link": f"/guide/{meta.get('id')}",
                "thumbnail": meta.get('thumbnail', ''), 
                "item_type": "guide",
                "is_featured": meta.get('is_featured', False) # Featured 여부 확인
            })
        except Exception:
            pass
    return guides

def load_guide_meta(link):
    """링크를 통해 가이드의 메타데이터만 빠르게 확인"""
    try:
        slug = link.split('/')[-1]
        filepath = os.path.join(CONTENT_DIR, f"guide_{slug}.md")
        if os.path.exists(filepath):
            return frontmatter.load(filepath).metadata
    except:
        pass
    return {}

# --- 라우팅 (Routing) ---

@app.get("/ads.txt", response_class=PlainTextResponse)
async def ads_txt():
    return ADS_TXT_CONTENT

@app.get("/sitemap.xml", response_class=PlainTextResponse)
async def sitemap():
    urls = [f"{DOMAIN}/{path}" for path in ["", "about", "guide", "schools", "universities", "contact", "policy"]]
    
    schools_data, _ = load_school_data()
    for s in schools_data:
        if s.get('id'):
            urls.append(f"{DOMAIN}/school/{s['id']}")
            
    guides = load_guides()
    for g in guides:
        if g.get('link'):
            urls.append(f"{DOMAIN}{g['link']}")
            
    xml_urls = "".join([f'<url><loc>{url}</loc><changefreq>weekly</changefreq></url>' for url in urls])
    return Response(content=f'<?xml version="1.0" encoding="UTF-8"?><urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">{xml_urls}</urlset>', media_type="application/xml")

@app.get("/robots.txt", response_class=PlainTextResponse)
async def robots():
    return f"User-agent: *\nAllow: /\nSitemap: {DOMAIN}/sitemap.xml"

@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    schools_data, updated_at = load_school_data()
    all_guides = load_guides() # 여기서 위에서 정의한 함수를 호출

    # [Featured 가이드 필터링]
    # is_featured가 True인 가이드만 추출
    featured_guides = [g for g in all_guides if g.get('is_featured')]
    
    # 만약 featured 가이드가 없으면(아직 생성 안 됨), 최신 가이드 3개를 대체로 사용
    if not featured_guides:
        featured_guides = all_guides[:3]
    else:
        featured_guides = featured_guides[:3] # 최대 3개만 표시

    # 메인 리스트 (학교/대학) - 6개씩
    latest_schools = [s for s in schools_data if s.get('category') != 'university'][:6]
    latest_universities = [s for s in schools_data if s.get('category') == 'university'][:6]
    
    tags_with_counts = calculate_tag_counts(schools_data)
    
    # 검색용 대학 리스트
    university_list = [
        {"name_ja": s.get('basic_info', {}).get('name_ja'), "name_en": s.get('basic_info', {}).get('name_en')}
        for s in schools_data if s.get('category') == 'university' and s.get('basic_info', {}).get('name_en')
    ]

    return templates.TemplateResponse("index.html", {
        "request": request, 
        "schools_json": json.dumps({"schools": schools_data}, ensure_ascii=False),
        "maps_api_key": GOOGLE_MAPS_API_KEY, 
        "updated_at": updated_at,
        "featured_guides": featured_guides, 
        "latest_schools": latest_schools, 
        "latest_universities": latest_universities, 
        # Featured나 상단에 쓴거 제외하고 나머지 보여주기 (중복 방지용 로직 단순화: 그냥 전체 중 일부 노출)
        "latest_guides": [g for g in all_guides if g not in featured_guides][:6],
        "tags_with_counts": tags_with_counts, 
        "university_list_json": json.dumps(university_list, ensure_ascii=False)
    })

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
    
    # 썸네일이 없는 경우 기본 이미지 할당
    school_placeholders = ['https://images.unsplash.com/photo-1544531586-fde5298cdd40?w=500', 'https://images.unsplash.com/photo-1523240795612-9a054b0db644?w=500', 'https://images.unsplash.com/photo-1509062522246-3755977927d7?w=500']
    for i, item in enumerate(schools): 
        if not item.get('thumbnail'):
            item['thumbnail'] = school_placeholders[i % len(school_placeholders)]
            
    return templates.TemplateResponse("list.html", {"request": request, "items": schools, "item_type": "school", "title": "All Language Schools"})

@app.get("/universities", response_class=HTMLResponse)
async def university_list(request: Request):
    schools_data, _ = load_school_data()
    universities = [s for s in schools_data if s.get('category') == 'university']
    
    univ_placeholders = ['https://images.unsplash.com/photo-1562774053-701939374585?w=500', 'https://images.unsplash.com/photo-1541339907198-e08756dedf3f?w=500', 'https://images.unsplash.com/photo-1498243691581-b145c3f54a5a?w=500']
    for i, item in enumerate(universities): 
        if not item.get('thumbnail'):
            item['thumbnail'] = univ_placeholders[i % len(univ_placeholders)]
            
    return templates.TemplateResponse("list.html", {"request": request, "items": universities, "item_type": "university", "title": "All Universities"})

@app.get("/guide", response_class=HTMLResponse)
async def guide_list_page(request: Request):
    guides = load_guides()
    return templates.TemplateResponse("list.html", {"request": request, "items": guides, "item_type": "guide", "title": "Essential Guides"})

@app.get("/about", response_class=HTMLResponse)
async def about(request: Request): return templates.TemplateResponse("about.html", {"request": request})
@app.get("/contact", response_class=HTMLResponse)
async def contact(request: Request): return templates.TemplateResponse("contact.html", {"request": request})
@app.get("/policy", response_class=HTMLResponse)
async def policy(request: Request): return templates.TemplateResponse("policy.html", {"request": request})
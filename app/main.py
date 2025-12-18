from fastapi import FastAPI, Request, HTTPException
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
    # 모든 학교 ID 가져오기
    urls = [f"{DOMAIN}/"]
    
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, 'r', encoding='utf-8') as f:
            data = json.load(f)
            for s in data.get('schools', []):
                urls.append(f"{DOMAIN}/school/{s['id']}")
    
    # 가이드 페이지 등 추가
    urls.append(f"{DOMAIN}/guide")
    
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
# 1. 메인 페이지 (지도)
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

    # 1. 학교/대학 데이터 분리
    latest_schools = [s for s in schools_data if s.get('category') != 'university'][:4]
    latest_universities = [s for s in schools_data if s.get('category') == 'university'][:4]

    # 2. [추가] 가이드 목록 가져오기 (최신 4개)
    guides = []
    guide_dir = "app/content"
    # guide_*.md 파일 검색
    guide_files = glob.glob(os.path.join(guide_dir, "guide_*.md"))
    
    # 최신순 정렬 (파일명 역순 또는 날짜순 등)
    guide_files.sort(reverse=True) 
    
    for filepath in guide_files[:4]: # 상위 4개만
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
        "latest_guides": guides  # [추가] 템플릿으로 전달
    })

# ---------------------------------------------------------
# 2. 상세 페이지 (Markdown 파싱)
# ---------------------------------------------------------
@app.get("/school/{school_id}", response_class=HTMLResponse)
async def read_school_detail(request: Request, school_id: str):
    md_path = f"app/content/{school_id}.md"
    
    if not os.path.exists(md_path):
        raise HTTPException(status_code=404, detail="School not found")

    with open(md_path, 'r', encoding='utf-8') as f:
        post = frontmatter.load(f)
    
    raw_content = post.content
    
    # 1. 테이블 전처리 (줄바꿈 강제 삽입)
    # 헤더와 구분선 사이, 그리고 표 앞뒤에 엔터를 넣어 파싱 확률을 높임
    raw_content = re.sub(r'\|([^\n]+)\|\s*\|(:?-+:?)\|', r'|\1|\n|\2|', raw_content)
    
    # 2. 리스트 전처리 (글머리 기호 * 앞에 엔터가 없으면 리스트로 인식 안될 수 있음)
    # 문장 끝(.) 뒤에 바로 *가 오면 줄바꿈 추가
    raw_content = re.sub(r'\.\s*\*', '.\n\n*', raw_content)

    # 3. 마크다운 변환 (확장 기능 추가)
    content_html = markdown.markdown(
        raw_content,
        extensions=[
            'tables',       # 표 지원
            'fenced_code',  # 코드 블록
            'nl2br',        # 줄바꿈을 <br>로 변환 (중요!)
            'sane_lists'    # 리스트 파싱 강화
        ]
    )
    
    school = post.metadata
    name = school.get('basic_info', {}).get('name_ja', 'Unknown')
    
    return templates.TemplateResponse("detail.html", {
        "request": request,
        "school": school,
        "content_body": content_html,
        "meta_url": f"{DOMAIN}/school/{school_id}",
        "meta_title": f"{name} - Detail | JP Campus",
        "meta_desc": f"Details about {name}",
        "maps_api_key": GOOGLE_MAPS_API_KEY
    })

# ---------------------------------------------------------
# 가이드 리스트 및 상세 페이지 (동적 처리)
# ---------------------------------------------------------

def get_all_guides():
    """가이드 폴더의 모든 MD 파일을 읽어 메타데이터 리스트 반환"""
    guide_dir = "app/content/guides"
    guides = []
    
    if not os.path.exists(guide_dir):
        return []

    # 모든 .md 파일 검색
    files = glob.glob(os.path.join(guide_dir, "*.md"))
    
    for filepath in files:
        with open(filepath, 'r', encoding='utf-8') as f:
            post = frontmatter.load(f)
            meta = post.metadata
            meta['link'] = f"/guide/{meta['id']}"
            guides.append(meta)
    
    # 카테고리 순서나 날짜 순으로 정렬하고 싶다면 여기서 sort
    return guides

# ---------------------------------------------------------
# 3. 가이드 섹션 (동적 MD 로딩)
# ---------------------------------------------------------

@app.get("/guide", response_class=HTMLResponse)
async def guide_list(request: Request):
    """가이드 목록 페이지: app/content/guide_*.md 파일들을 스캔하여 목록 생성"""
    guides = []
    content_dir = "app/content"
    
    # guide_ 로 시작하는 모든 MD 파일 검색
    files = glob.glob(os.path.join(content_dir, "guide_*.md"))
    
    for filepath in files:
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                post = frontmatter.load(f)
                meta = post.metadata
                # 리스트에 필요한 정보만 추출
                guides.append({
                    "title": meta.get('title'),
                    "description": meta.get('description'),
                    "category": meta.get('tags', ['Guide'])[0], # 첫 번째 태그를 카테고리로 사용
                    "link": f"/guide/{meta.get('id')}", # id는 slug (예: cost)
                    "thumbnail": meta.get('thumbnail')
                })
        except Exception as e:
            print(f"Error loading guide {filepath}: {e}")
            
    return templates.TemplateResponse("guide_list.html", {
        "request": request,
        "guides": guides,
        "meta_title": "Essential Guides for Japan - JP Campus",
        "meta_desc": "Everything you need to know before studying in Japan."
    })

@app.get("/guide/{slug}", response_class=HTMLResponse)
async def guide_detail(request: Request, slug: str):
    """가이드 상세 페이지: guide_{slug}.md 로딩"""
    # [중요] 파일명 매핑: URL slug -> guide_slug.md
    filename = f"guide_{slug}.md"
    md_path = os.path.join("app/content", filename)
    
    if not os.path.exists(md_path):
        raise HTTPException(status_code=404, detail="Guide not found")

    with open(md_path, 'r', encoding='utf-8') as f:
        post = frontmatter.load(f)
    
    # 마크다운 변환
    content_html = markdown.markdown(
        post.content,
        extensions=['tables', 'fenced_code', 'nl2br', 'sane_lists']
    )
    
    return templates.TemplateResponse("guide_detail.html", {
        "request": request,
        "guide": post.metadata,
        "content_body": content_html,
        "meta_title": f"{post.metadata['title']} - JP Campus",
        "meta_desc": post.metadata.get('description', ''),
        "meta_url": f"{DOMAIN}/guide/{slug}"
    })

@app.get("/schools", response_class=HTMLResponse)
async def school_list(request: Request):
    """어학원 전체 목록 페이지"""
    with open(DATA_FILE, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # 대학(university)이 아닌 것만 필터링
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
    
    # 대학(university)인 것만 필터링
    universities = [s for s in data['schools'] if s.get('category') == 'university']
    
    return templates.TemplateResponse("school_list.html", {
        "request": request,
        "items": universities,
        "title": "Universities in Japan",
        "description": "Explore top universities in Japan for international students."
    })
    
# ---------------------------------------------------------
# 3. 기타 라우트 (가이드 등)
# ---------------------------------------------------------
@app.get("/guide", response_class=HTMLResponse)
async def guide_list(request: Request):
    return templates.TemplateResponse("guide_list.html", {"request": request})

@app.get("/guide/{guide_name}", response_class=HTMLResponse)
async def guide_detail(request: Request, guide_name: str):
    return templates.TemplateResponse(f"guides/{guide_name}.html", {"request": request})

@app.get("/about", response_class=HTMLResponse)
async def about(request: Request):
    return templates.TemplateResponse("about.html", {"request": request})

@app.get("/contact", response_class=HTMLResponse)
async def contact(request: Request):
    return templates.TemplateResponse("contact.html", {"request": request})

@app.get("/policy", response_class=HTMLResponse)
async def policy(request: Request):
    return templates.TemplateResponse("policy.html", {"request": request})
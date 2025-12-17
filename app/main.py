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
    meta_desc = f"일본 전역 {school_count}개 학교 완전 정복. 위치, 학비, 국적 비율 비교."

    # [추가] 최신 등록 학교/대학 추출 (각각 앞에서 4개씩)
    # 데이터가 최신순으로 정렬되어 있다고 가정하거나, 단순 리스트 상위 4개를 가져옵니다.
    latest_schools = [s for s in schools_data if s.get('category') != 'university'][:4]
    latest_universities = [s for s in schools_data if s.get('category') == 'university'][:4]

    return templates.TemplateResponse("index.html", {
        "request": request,
        "schools_json": json.dumps(schools_data, ensure_ascii=False),
        "maps_api_key": GOOGLE_MAPS_API_KEY,
        "meta_url": f"{DOMAIN}/",
        "meta_title": "JP Campus - 일본 유학 지도 검색",
        "meta_desc": meta_desc,
        "updated_at": updated_at,
        "latest_schools": latest_schools,       # 템플릿으로 전달
        "latest_universities": latest_universities # 템플릿으로 전달
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
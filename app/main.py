from fastapi import FastAPI, Request, HTTPException
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, PlainTextResponse
import json
import os
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
ADS_TXT_CONTENT = """google.com, pub-XXXXXXXXXXXXXXXX, DIRECT, f08c47fec0942fa0"""

@app.get("/ads.txt", response_class=PlainTextResponse)
async def ads_txt():
    return ADS_TXT_CONTENT

# ---------------------------------------------------------
# 1. 메인 페이지 (지도)
# ---------------------------------------------------------
@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    # 빌드된 JSON 파일 로드 (지도 표시용)
    schools_data = []
    updated_at = ""
    
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, 'r', encoding='utf-8') as f:
            data = json.load(f)
            schools_data = data.get('schools', [])
            updated_at = data.get('last_updated', '')

    school_count = len(schools_data)
    meta_desc = f"일본 전역 {school_count}개 학교 완전 정복. 위치, 학비, 국적 비율 비교."

    return templates.TemplateResponse("index.html", {
        "request": request,
        "schools_json": json.dumps(schools_data, ensure_ascii=False), # JS로 전달
        "maps_api_key": GOOGLE_MAPS_API_KEY,
        "meta_url": f"{DOMAIN}/",
        "meta_title": "JP Campus - 일본 유학 지도 검색",
        "meta_desc": meta_desc,
        "updated_at": updated_at
    })

# ---------------------------------------------------------
# 2. 상세 페이지 (Markdown 파싱)
# ---------------------------------------------------------
@app.get("/school/{school_id}", response_class=HTMLResponse)
async def read_school_detail(request: Request, school_id: str):
    md_path = f"app/content/{school_id}.md"
    
    if not os.path.exists(md_path):
        raise HTTPException(status_code=404, detail="School not found")

    # Frontmatter + Markdown 파싱
    with open(md_path, 'r', encoding='utf-8') as f:
        post = frontmatter.load(f)
    
    # 본문을 HTML로 변환
    content_html = markdown.markdown(post.content)
    
    # 메타 데이터 (Frontmatter)
    school = post.metadata
    
    name = school.get('basic_info', {}).get('name_ja', 'Unknown')
    
    return templates.TemplateResponse("detail.html", {
        "request": request,
        "school": school,          # Frontmatter 데이터 (기존 템플릿 변수와 호환)
        "content_body": content_html, # [중요] 변환된 본문 HTML
        "meta_url": f"{DOMAIN}/school/{school_id}",
        "meta_title": f"{name} - 상세 정보 | JP Campus",
        "meta_desc": f"{name}의 학비, 위치, 특징 상세 분석",
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
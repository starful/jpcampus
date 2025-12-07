
# app/main.py
from fastapi import FastAPI, Request, HTTPException
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, Response, PlainTextResponse
from contextlib import asynccontextmanager
import json
import os
from dotenv import load_dotenv

from .utils import load_data

load_dotenv()
GOOGLE_MAPS_API_KEY = os.getenv("GOOGLE_MAPS_API_KEY")
DOMAIN = "https://jpcampus.net"
CACHED_DATA = []
LAST_UPDATED = ""

@asynccontextmanager
async def lifespan(app: FastAPI):
    global CACHED_DATA, LAST_UPDATED
    # [수정] 데이터와 날짜 로드
    CACHED_DATA, LAST_UPDATED = load_data()
    yield

app = FastAPI(lifespan=lifespan)

app.mount("/static", StaticFiles(directory="app/static"), name="static")
templates = Jinja2Templates(directory="app/templates")


@app.get("/policy", response_class=HTMLResponse)
async def policy(request: Request):
    return templates.TemplateResponse("policy.html", {"request": request})

@app.get("/about", response_class=HTMLResponse)
async def about(request: Request):
    return templates.TemplateResponse("about.html", {"request": request})

@app.get("/contact", response_class=HTMLResponse)
async def contact(request: Request):
    return templates.TemplateResponse("contact.html", {"request": request})

@app.get("/guide", response_class=HTMLResponse)
async def guide_list(request: Request):
    return templates.TemplateResponse("guide_list.html", {"request": request})

@app.get("/guide/{article_name}", response_class=HTMLResponse)
async def guide_detail(request: Request, article_name: str):
    # guides 폴더 내의 해당 html 파일을 찾아 보여줌
    return templates.TemplateResponse(f"guides/{article_name}.html", {"request": request})
    
# ---------------------------------------------------------
# 1. 메인 페이지
# ---------------------------------------------------------
@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    school_count = len(CACHED_DATA)
    meta_desc = f"도쿄, 오사카, 후쿠오카 등 일본 전역 {school_count}개 일본어학교 완전 정복. 위치, 학비, 국적 비율을 지도에서 비교하고 나에게 맞는 학교를 찾아보세요."

    return templates.TemplateResponse("index.html", {
        "request": request,
        "schools_json": json.dumps(CACHED_DATA, ensure_ascii=False),
        "maps_api_key": GOOGLE_MAPS_API_KEY,
        "meta_url": f"{DOMAIN}/",
        "meta_title": "JP Campus - 일본 전국 일본어학교 지도 검색 & 비교",
        "meta_desc": meta_desc,
        "updated_at": LAST_UPDATED  # [추가] 갱신일 전달
    })

# ---------------------------------------------------------
# 2. 상세 페이지
# ---------------------------------------------------------
@app.get("/school/{school_id}", response_class=HTMLResponse)
async def read_school_detail(request: Request, school_id: str):
    school = next((s for s in CACHED_DATA if s.get("id") == school_id), None)
    
    if not school:
        raise HTTPException(status_code=404, detail="School not found")

    name = school['basic_info']['name_ja']
    address = school['basic_info']['address']
    
    # 최저 학비 계산
    min_fee = "-"
    if school.get('courses'):
        fees = [c['total_fees'] for c in school['courses'] if isinstance(c['total_fees'], (int, float))]
        if fees:
            min_fee = f"{min(fees):,}엔"

    title = f"{name} - 학비 및 정보 | JP Campus"
    desc = f"{name} 상세 분석. 주소: {address}. 최저 학비: {min_fee}. 학생 국적 비율 및 진학 실적 확인."

    return templates.TemplateResponse("detail.html", {
        "request": request,
        "school": school,
        "meta_url": f"{DOMAIN}/school/{school_id}",
        "meta_title": title,
        "meta_desc": desc,
        "maps_api_key": GOOGLE_MAPS_API_KEY
    })

# ---------------------------------------------------------
# 3. Sitemap & Robots
# ---------------------------------------------------------
@app.get("/sitemap.xml", response_class=Response)
async def sitemap():
    xml = '<?xml version="1.0" encoding="UTF-8"?>\n'
    xml += '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
    xml += f'  <url><loc>{DOMAIN}/</loc><changefreq>daily</changefreq><priority>1.0</priority></url>\n'
    for s in CACHED_DATA:
        if "id" in s:
            xml += f'  <url><loc>{DOMAIN}/school/{s["id"]}</loc><changefreq>weekly</changefreq><priority>0.8</priority></url>\n'
    xml += '</urlset>'
    return Response(content=xml, media_type="application/xml")

@app.get("/robots.txt", response_class=PlainTextResponse)
async def robots():
    content = f"""User-agent: *
Allow: /
Sitemap: {DOMAIN}/sitemap.xml
"""
    return content
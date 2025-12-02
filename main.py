from fastapi import FastAPI, Request, HTTPException
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, Response, PlainTextResponse
from contextlib import asynccontextmanager
from google.cloud import storage
import json
import os
from dotenv import load_dotenv

# 환경변수 로드
load_dotenv()

BUCKET_NAME = os.getenv("GCS_BUCKET_NAME", "jpcampus")
GCS_FILE = "schools_complete_db.json"
LOCAL_FILE = "file/schools_complete_db.json"
GOOGLE_MAPS_API_KEY = os.getenv("GOOGLE_MAPS_API_KEY")

# 도메인 설정
DOMAIN = "https://jpcampus.net"

CACHED_DATA = []

def load_data():
    """GCS 또는 로컬에서 데이터 로드"""
    data = []
    # 1. GCS 시도
    try:
        storage_client = storage.Client()
        bucket = storage_client.bucket(BUCKET_NAME)
        blob = bucket.blob(GCS_FILE)
        if blob.exists():
            data_str = blob.download_as_text()
            data = json.loads(data_str)
            return data
    except Exception:
        pass

    # 2. 로컬 시도
    if os.path.exists(LOCAL_FILE):
        try:
            with open(LOCAL_FILE, 'r', encoding='utf-8') as f:
                data = json.load(f)
            return data
        except Exception:
            pass
    return []

@asynccontextmanager
async def lifespan(app: FastAPI):
    global CACHED_DATA
    CACHED_DATA = load_data()
    yield

app = FastAPI(lifespan=lifespan)
templates = Jinja2Templates(directory="templates")

# ---------------------------------------------------------
# [SEO 1] 메인 페이지
# ---------------------------------------------------------
@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    return templates.TemplateResponse("index.html", {
        "request": request,
        "schools_json": json.dumps(CACHED_DATA, ensure_ascii=False),
        "maps_api_key": GOOGLE_MAPS_API_KEY,
        "meta_url": f"{DOMAIN}/",
        "meta_title": "도쿄 & 치바 일본어학교 지도 | JP Campus",
        "meta_desc": "도쿄와 치바 지역의 일본어학교 위치, 학비, 국적 비율을 지도에서 한눈에 비교하세요. 성공적인 유학의 시작."
    })

# ---------------------------------------------------------
# [SEO 2] 상세 페이지
# ---------------------------------------------------------
@app.get("/school/{school_id}", response_class=HTMLResponse)
async def read_school_detail(request: Request, school_id: str):
    school = next((s for s in CACHED_DATA if s.get("id") == school_id), None)
    
    if not school:
        raise HTTPException(status_code=404, detail="School not found")

    name = school['basic_info']['name_ja']
    address = school['basic_info']['address']
    
    title = f"{name} - 정보 및 학비 | JP Campus"
    desc = f"{name} 상세 정보. 위치: {address}, 학비, 학생 국적 비율, 진학 실적 등 최신 데이터를 확인하세요."

    return templates.TemplateResponse("detail.html", {
        "request": request,
        "school": school,
        "meta_url": f"{DOMAIN}/school/{school_id}",
        "meta_title": title,
        "meta_desc": desc,
        "maps_api_key": GOOGLE_MAPS_API_KEY
    })

# ---------------------------------------------------------
# [SEO 3] Sitemap.xml
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

# ---------------------------------------------------------
# [SEO 4] Robots.txt
# ---------------------------------------------------------
@app.get("/robots.txt", response_class=PlainTextResponse)
async def robots():
    content = f"""User-agent: *
Allow: /
Sitemap: {DOMAIN}/sitemap.xml
"""
    return content

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080)
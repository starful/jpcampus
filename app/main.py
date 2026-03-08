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
import glob
from app.utils import calculate_tag_counts

# ==========================================
#[수정] 파이어베이스 연동을 위한 모듈 (명시적 분리)
# ==========================================
import firebase_admin
from firebase_admin import credentials, firestore
from starlette.concurrency import run_in_threadpool

load_dotenv()
app = FastAPI()

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
STATIC_DIR = os.path.join(BASE_DIR, "static")
CONTENT_DIR = os.path.join(BASE_DIR, "content") 
TEMPLATES_DIR = os.path.join(BASE_DIR, "templates")

if not os.path.exists(CONTENT_DIR): os.makedirs(CONTENT_DIR)

app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")
templates = Jinja2Templates(directory=TEMPLATES_DIR)

GOOGLE_MAPS_API_KEY = os.getenv("GOOGLE_MAPS_API_KEY")
DOMAIN = "https://jpcampus.net"
ADS_TXT_CONTENT = "google.com, pub-8780435268193938, DIRECT, f08c47fec0942fa0"
COLLECTION_NAME = "jpcampus"

# ==========================================
# Firebase 초기화 세팅
# ==========================================
try:
    if not firebase_admin._apps:
        cred_path = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
        if cred_path and os.path.exists(cred_path):
            cred = credentials.Certificate(cred_path)
            firebase_admin.initialize_app(cred)
        else:
            firebase_admin.initialize_app()
    db = firestore.client()
except Exception as e:
    print(f"🔥 Firebase initialization error: {e}")
    db = None

def get_client_ip(request: Request):
    try:
        x_forwarded_for = request.headers.get("X-Forwarded-For")
        if x_forwarded_for:
            return x_forwarded_for.split(",")[0].strip()
        if request.client and request.client.host:
            return request.client.host
    except Exception:
        pass
    return "unknown_ip"

# --- UI 텍스트 번역 사전 ---
def get_ui_text(lang):
    if lang == "kr":
        return {
            "featured_title": "추천 컬렉션",
            "best_selection": "추천",
            "view_ranking": "랭킹 보기 →",
            "language_schools": "일본어 어학원",
            "top_universities": "주요 대학교",
            "view_all": "전체 보기 →",
            "essential_guides": "유학 가이드",
            "school_badge": "어학원",
            "univ_badge": "대학교",
            "contact_fee": "학비 문의",
            "yearly": "연간",
            "search_placeholder": "대학교 검색...",
            "all_schools": "모든 학교",
            "back_to_map": "지도로 돌아가기",
            "back_to_list": "목록으로 돌아가기",
            "global_programs": "글로벌 프로그램",
            "national_private": "공식 국공립/사립 기관",
            "view_all_schools": "모든 학교 보기 →",
            "view_all_univs": "모든 대학교 보기 →"
        }
    return {
        "featured_title": "Featured Collections",
        "best_selection": "Best Selection",
        "view_ranking": "View Ranking →",
        "language_schools": "Language Schools",
        "top_universities": "Top Universities",
        "view_all": "View all →",
        "essential_guides": "Essential Guides",
        "school_badge": "School",
        "univ_badge": "University",
        "contact_fee": "Contact for Fee",
        "yearly": "Yearly",
        "search_placeholder": "Search universities...",
        "all_schools": "All Schools",
        "back_to_map": "Back to Map",
        "back_to_list": "Back to List",
        "global_programs": "Global Programs",
        "national_private": "Official National/Private Institute",
        "view_all_schools": "View all schools →",
        "view_all_univs": "View all universities →"
    }

# --- Helper Functions ---

def load_school_data(lang="en"):
    """언어에 맞는 학교 데이터 JSON 로드"""
    filename = "schools_data_kr.json" if lang == "kr" else "schools_data.json"
    file_path = os.path.join(STATIC_DIR, "json", filename)
    
    if not os.path.exists(file_path):
        file_path = os.path.join(STATIC_DIR, "json", "schools_data.json")
        
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            return data.get('schools',[]), data.get('last_updated', '')
    except Exception as e:
        print(f"Error loading data: {e}")
        return[], ""

def load_guides(lang="en"):
    """언어에 맞는 가이드 로드"""
    guides =[]
    if lang == "kr":
        pattern = os.path.join(CONTENT_DIR, "guide_*_kr.md")
    else:
        pattern = os.path.join(CONTENT_DIR, "guide_*.md")

    guide_files = glob.glob(pattern)
    if lang != "kr":
        guide_files =[f for f in guide_files if not f.endswith("_kr.md")]
        
    guide_files.sort(key=os.path.getmtime, reverse=True)
    
    for filepath in guide_files:
        try:
            post = frontmatter.load(filepath)
            meta = post.metadata
            guide_id = meta.get('id', '').replace('_kr', '')
            guides.append({
                "title": meta.get('title', 'Untitled'), 
                "description": meta.get('description', ''),
                "category": meta.get('category', 'Guide'), 
                "link": f"/guide/{guide_id}?lang={lang}",
                "thumbnail": meta.get('thumbnail', ''), 
                "item_type": "guide",
                "is_featured": meta.get('is_featured', False)
            })
        except Exception:
            pass
    return guides

# ==========================================
# [수정] 좋아요/싫어요 API 엔드포인트
# ==========================================
@app.get("/api/reactions/{slug}")
async def get_reactions(slug: str):
    if db is None:
        return {"likes": 0, "dislikes": 0, "error": "Database not connected"}
        
    doc_ref = db.collection(COLLECTION_NAME).document(slug)
    doc = await run_in_threadpool(doc_ref.get)

    if doc.exists:
        data = doc.to_dict()
        return {"likes": data.get("likes_count", 0), "dislikes": data.get("dislikes_count", 0)}
    return {"likes": 0, "dislikes": 0}


def sync_process_reaction(db_client, collection_name, slug, safe_ip, new_type):
    post_ref = db_client.collection(collection_name).document(slug)
    reaction_ref = post_ref.collection('reactions').document(safe_ip)

    # 1. 현재 접속자(IP)의 이전 클릭 기록 읽기 (트랜잭션 없이 일반 GET 사용)
    reaction_doc = reaction_ref.get()

    likes_inc = 0
    dislikes_inc = 0
    
    # 2. Batch (일괄 쓰기) 객체 생성 - 쓰레드 충돌을 원천 차단함
    batch = db_client.batch()

    if not reaction_doc.exists:
        # 처음 클릭하는 경우
        if new_type == "like": likes_inc = 1
        else: dislikes_inc = 1
        batch.set(reaction_ref, {"type": new_type})
        current_type = None
    else:
        # 이미 누른 기록이 있는 경우
        current_type = reaction_doc.to_dict().get("type")
        if current_type == new_type:
            # 같은 버튼을 또 누름 -> 취소 (숫자 차감)
            if new_type == "like": likes_inc = -1
            else: dislikes_inc = -1
            batch.delete(reaction_ref)
        else:
            # 다른 버튼으로 환승 (예: 좋아요 -> 싫어요)
            if new_type == "like":
                likes_inc = 1
                dislikes_inc = -1
            else:
                likes_inc = -1
                dislikes_inc = 1
            batch.update(reaction_ref, {"type": new_type})

    # 3. 문서 카운트 증감 업데이트
    # Increment를 사용하므로 수천 명이 동시에 눌러도 숫자가 꼬이지 않음
    batch.set(post_ref, {
        "likes_count": firestore.Increment(likes_inc),
        "dislikes_count": firestore.Increment(dislikes_inc)
    }, merge=True)
    
    # 4. 일괄 쓰기 실행
    batch.commit()
    
    action_result = "added" if (not reaction_doc.exists) or current_type != new_type else "removed"
    
    # 최신 결과 반환
    updated_doc = post_ref.get()
    return action_result, updated_doc.to_dict() or {}


async def process_reaction(request: Request, slug: str, reaction_type: str):
    if db is None:
         raise HTTPException(status_code=500, detail="Database connection failed")

    safe_ip = get_client_ip(request).replace(".", "_").replace(":", "_")

    try:
        # 동기 함수를 비동기 풀에서 안전하게 실행
        result, data = await run_in_threadpool(
            sync_process_reaction, db, COLLECTION_NAME, slug, safe_ip, reaction_type
        )
    except Exception as e:
        print(f"🔥 Reaction Error: {e}")
        raise HTTPException(status_code=500, detail="Reaction processing failed")

    return {
        "status": "success", 
        "action": result,
        "likes": data.get("likes_count", 0), 
        "dislikes": data.get("dislikes_count", 0),
        "current_type": reaction_type if result == "added" else None
    }

@app.post("/api/like/{slug}")
async def like_post(request: Request, slug: str):
    return await process_reaction(request, slug, "like")

@app.post("/api/dislike/{slug}")
async def dislike_post(request: Request, slug: str):
    return await process_reaction(request, slug, "dislike")

# ==========================================
# 기본 화면 라우터
# ==========================================

@app.get("/ads.txt", response_class=PlainTextResponse)
async def ads_txt():
    return ADS_TXT_CONTENT

@app.get("/sitemap.xml", response_class=PlainTextResponse)
async def sitemap():
    urls =[]
    # 1. 기본 메뉴 페이지들 (EN/KR)
    base_paths = ["", "about", "guide", "schools", "universities", "contact", "policy"]
    for path in base_paths:
        urls.append(f"{DOMAIN}/{path}") # 기본(영어)
        urls.append(f"{DOMAIN}/{path}?lang=kr") # 한국어

    # 2. 학교 & 대학교 상세 페이지 (EN/KR)
    schools_en, _ = load_school_data("en")
    for s in schools_en:
        if s.get('id'):
            urls.append(f"{DOMAIN}/school/{s['id']}")
            urls.append(f"{DOMAIN}/school/{s['id']}?lang=kr")

    # 3. 가이드 상세 페이지 (EN/KR)
    guides_en = load_guides("en")
    for g in guides_en:
        slug = g['link'].split('/')[-1].split('?')[0]
        urls.append(f"{DOMAIN}/guide/{slug}")
        urls.append(f"{DOMAIN}/guide/{slug}?lang=kr")

    urls = list(set(urls))

    xml_urls = "".join([
        f'<url><loc>{url}</loc><changefreq>weekly</changefreq><priority>0.8</priority></url>' 
        for url in urls
    ])
    
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
    if not featured_guides: featured_guides = all_guides[:3]
    else: featured_guides = featured_guides[:3]

    latest_schools =[s for s in schools_data if s.get('category') != 'university'][:6]
    latest_universities =[s for s in schools_data if s.get('category') == 'university'][:6]
    
    tags_with_counts = calculate_tag_counts(schools_data)
    
    university_list =[
        {"name_ja": s['basic_info'].get('name_ja'), "name_en": s['basic_info'].get('name_display', s['basic_info'].get('name_en'))}
        for s in schools_data if s.get('category') == 'university'
    ]

    return templates.TemplateResponse("index.html", {
        "request": request, 
        "schools_json": json.dumps({"schools": schools_data}, ensure_ascii=False),
        "maps_api_key": GOOGLE_MAPS_API_KEY, 
        "updated_at": updated_at,
        "featured_guides": featured_guides, 
        "latest_schools": latest_schools, 
        "latest_universities": latest_universities, 
        "latest_guides":[g for g in all_guides if g not in featured_guides][:6],
        "tags_with_counts": tags_with_counts, 
        "university_list_json": json.dumps(university_list, ensure_ascii=False),
        "current_lang": lang,
        "ui": ui 
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

    return templates.TemplateResponse("detail.html", { 
        "request": request, "item": item, "item_type": item_type, 
        "content_body": content_html, "current_lang": lang,
        "ui": get_ui_text(lang) 
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

    return templates.TemplateResponse("detail.html", { 
        "request": request, "item": item, "item_type": "guide", 
        "content_body": content_html, "current_lang": lang,
        "ui": get_ui_text(lang) 
    })

@app.get("/schools", response_class=HTMLResponse)
async def school_list(request: Request, lang: str = Query("en")):
    schools_data, _ = load_school_data(lang)
    schools =[s for s in schools_data if s.get('category') != 'university']
    
    school_placeholders =['https://images.unsplash.com/photo-1544531586-fde5298cdd40?w=500', 'https://images.unsplash.com/photo-1580582932707-520aed937b7b?w=500']
    for i, item in enumerate(schools): 
        if not item.get('thumbnail'): item['thumbnail'] = school_placeholders[i % 2]
            
    return templates.TemplateResponse("list.html", {
        "request": request, "items": schools, "item_type": "school", 
        "title": "All Language Schools" if lang == 'en' else "일본어학교 목록",
        "current_lang": lang,
        "ui": get_ui_text(lang) 
    })

@app.get("/universities", response_class=HTMLResponse)
async def university_list(request: Request, lang: str = Query("en")):
    schools_data, _ = load_school_data(lang)
    universities =[s for s in schools_data if s.get('category') == 'university']
    
    univ_placeholders =['https://images.unsplash.com/photo-1562774053-701939374585?w=500', 'https://images.unsplash.com/photo-1498243691581-b145c3f54a5a?w=500']
    for i, item in enumerate(universities): 
        if not item.get('thumbnail'): item['thumbnail'] = univ_placeholders[i % 2]
            
    return templates.TemplateResponse("list.html", {
        "request": request, "items": universities, "item_type": "university", 
        "title": "All Universities" if lang == 'en' else "일본 대학 목록",
        "current_lang": lang,
        "ui": get_ui_text(lang) 
    })

@app.get("/guide", response_class=HTMLResponse)
async def guide_list_page(request: Request, lang: str = Query("en")):
    guides = load_guides(lang)
    return templates.TemplateResponse("list.html", {
        "request": request, "items": guides, "item_type": "guide", 
        "title": "Essential Guides" if lang == 'en' else "유학 가이드",
        "current_lang": lang,
        "ui": get_ui_text(lang) 
    })

@app.get("/about", response_class=HTMLResponse)
async def about(request: Request): return templates.TemplateResponse("about.html", {"request": request})
@app.get("/contact", response_class=HTMLResponse)
async def contact(request: Request): return templates.TemplateResponse("contact.html", {"request": request})
@app.get("/policy", response_class=HTMLResponse)
async def policy(request: Request): return templates.TemplateResponse("policy.html", {"request": request})
@app.get("/favicon.ico", include_in_schema=False)
async def favicon():
    return FileResponse(os.path.join(STATIC_DIR, "img", "logo.png"))
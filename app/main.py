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
import hashlib
from app.utils import calculate_tag_counts

import hashlib

# ==========================================
# 1. [대학교] 썸네일 (캠퍼스, 도서관, 대학생, 학업, 노트북) - 30개
# ==========================================
UNIV_THUMBNAILS =[
    "https://images.unsplash.com/photo-1541339907198-e08756dedf3f?w=500", # 클래식 대학 건물
    "https://images.unsplash.com/photo-1498243691581-b145c3f54a5a?w=500", # 잔디밭과 캠퍼스 외관
    "https://images.unsplash.com/photo-1592280771190-3e2e4d571952?w=500", # 현대적인 대학 건물
    "https://images.unsplash.com/photo-1562774053-701939374585?w=500", # 웅장한 도서관 건축물
    "https://images.unsplash.com/photo-1606092195730-5d7b9af1efc5?w=500", # 유럽풍 대학 건축물
    "https://images.unsplash.com/photo-1521587760476-6c12a4b040da?w=500", # 역사적인 대학 외관
    "https://images.unsplash.com/photo-1541336318489-083c7d277b8e?w=500", # 모던한 기하학적 캠퍼스
    "https://images.unsplash.com/photo-1584697964190-7383cbee8277?w=500", # 대학의 대형 기둥
    "https://images.unsplash.com/photo-1511629091441-ee46146481b6?w=500", # 빈 캠퍼스 산책로
    "https://images.unsplash.com/photo-1573894998033-c0cef4ed722b?w=500", # 클래식한 아치형 복도
    "https://images.unsplash.com/photo-1542621334-a254cf47733d?w=500", # 웅장한 건축 양식
    "https://images.unsplash.com/photo-1497634763913-2ea08bf9de5d?w=500", # 담쟁이 덩굴이 있는 시계탑
    "https://images.unsplash.com/photo-1500088139251-37350df3c1ad?w=500" # 클래식 캠퍼스 정원
]

# ==========================================
# 2. [어학원] 썸네일 (교실, 일본어 노트, 칠판, 일본 문화) - 30개
# ==========================================
SCHOOL_THUMBNAILS =[
    "https://images.unsplash.com/photo-1503676260728-1c00da094a0b?w=500",
    "https://images.unsplash.com/photo-1509062522246-3755977927d7?w=500",
    "https://images.unsplash.com/photo-1456513080510-7bf3a84b82f8?w=500",
    "https://images.unsplash.com/photo-1580582932707-520aed937b7b?w=500",
    "https://images.unsplash.com/photo-1544531586-fde5298cdd40?w=500",
    "https://images.unsplash.com/photo-1493976040374-85c8e12f0c0e?w=500",
    "https://images.unsplash.com/photo-1528164344705-47542687000d?w=500",
    "https://images.unsplash.com/photo-1577985051167-0d49eec21977?w=500",
    "https://images.unsplash.com/photo-1608813607488-0f932c5b71ef?w=500",
    "https://images.unsplash.com/photo-1581276879432-15e50529f34b?w=500",
    "https://images.unsplash.com/photo-1584697964190-7383cbee8277?w=500",
    "https://images.unsplash.com/photo-1577825294026-50dc375b9119?w=500",
    "https://images.unsplash.com/photo-1453694595360-51e193e121fc?w=500",
    "https://images.unsplash.com/photo-1573416033034-e42e14b545d2?w=500",
    "https://images.unsplash.com/photo-1586877644127-e5ee9b4231c3?w=500",
    "https://images.unsplash.com/photo-1550303435-1703d8811aaa?w=500",
    "https://images.unsplash.com/photo-1505738313577-5357ff512f16?w=500",
    "https://images.unsplash.com/photo-1561535893-bb7a98c7ee45?w=500",
    "https://images.unsplash.com/photo-1523905330026-b8bd1f5f320e?w=500",
    "https://images.unsplash.com/photo-1613376023733-0a73315d9b06?w=500",
    "https://images.unsplash.com/photo-1493934558415-9d19f0b2b4d2?w=500",
    "https://images.unsplash.com/photo-1541336318489-083c7d277b8e?w=500",
    "https://images.unsplash.com/photo-1622589476300-b72799ca4ade?w=500",
    "https://images.unsplash.com/photo-1639621108959-15f9c4257508?w=500",
    "https://images.unsplash.com/photo-1503387762-592deb58ef4e?w=500",
    "https://images.unsplash.com/photo-1586023492125-27b2c045efd7?w=500",
    "https://images.unsplash.com/photo-1526916025899-1a28d20f2a5f?w=500",
    "https://images.unsplash.com/photo-1559077138-3e27e1cdb95a?w=500",
    "https://images.unsplash.com/photo-1598368195835-91e67f80c9d7?w=500"
]

# ==========================================
# 3. [가이드] 썸네일 (일본 거리, 주거, 비자, 지하철, 예산 등) - 30개
# ==========================================
GUIDE_THUMBNAILS =[
    "https://images.unsplash.com/photo-1491841550275-ad7854e35ca6?w=500",
    "https://images.unsplash.com/photo-1610312278520-bcc893a3ff1d?w=500",
    "https://images.unsplash.com/photo-1590559899731-a382839e5549?w=500",
    "https://images.unsplash.com/photo-1436491865332-7a61a109cc05?w=500",
    "https://images.unsplash.com/photo-1561414927-6d86591d0c4f?w=500",
    "https://images.unsplash.com/photo-1522708323590-d24dbb6b0267?w=500",
    "https://images.unsplash.com/photo-1556740758-90de374c12ad?w=500",
    "https://images.unsplash.com/photo-1563986768609-322da13575f3?w=500",
    "https://images.unsplash.com/photo-1505751172876-fa1923c5c528?w=500",
    "https://images.unsplash.com/photo-1542051841857-5f90071e7989?w=500",
    "https://images.unsplash.com/photo-1580167227251-be70f01b0c51?w=500",
    "https://images.unsplash.com/photo-1684526688489-b08cbd8e1848?w=500",
    "https://images.unsplash.com/photo-1603491543570-f7df3c9a12c1?w=500",
    "https://images.unsplash.com/photo-1563089145-599997674d42?w=500",
    "https://images.unsplash.com/photo-1580477667995-2b94f01c9516?w=500",
    "https://images.unsplash.com/photo-1560972550-aba3456b5564?w=500",
    "https://images.unsplash.com/photo-1580477371971-91fc2a9a4899?w=500",
    "https://images.unsplash.com/photo-1548630435-998a2cbbff67?w=500",
    "https://images.unsplash.com/photo-1473496169904-658ba7c44d8a?w=500",
    "https://images.unsplash.com/photo-1558471250-385a4b04941e?w=500",
    "https://images.unsplash.com/photo-1526127230111-0197afe94d72?w=500",
    "https://images.unsplash.com/photo-1557409518-691ebcd96038?w=500",
    "https://images.unsplash.com/photo-1516205651411-aef33a44f7c2?w=500",
    "https://images.unsplash.com/photo-1551322120-c697cf88fbdc?w=500",
    "https://images.unsplash.com/photo-1573655349936-de6bed86f839?w=500",
    "https://images.unsplash.com/photo-1540569014015-19a7be504e3a?w=500",
    "https://images.unsplash.com/photo-1492571350019-22de08371fd3?w=500",
    "https://images.unsplash.com/photo-1524413840847-05c04c1f964b?w=500",
    "https://images.unsplash.com/photo-1522199755839-a2bacb67c546?w=500"
]

# 아이템 카테고리에 맞춰 올바른 리스트를 선택하도록 매핑
def assign_thumbnails(items, item_category="school"):
    """각 학교/대학의 고유 ID를 기반으로 카테고리에 맞는 썸네일 고정 배정"""
    if item_category == "university":
        thumb_pool = UNIV_THUMBNAILS
    else:
        thumb_pool = SCHOOL_THUMBNAILS

    for item in items:
        if not item.get('thumbnail'):
            item_id = item.get('id', 'default_id')
            hash_val = int(hashlib.md5(item_id.encode('utf-8')).hexdigest(), 16)
            item['thumbnail'] = thumb_pool[hash_val % len(thumb_pool)]
    return items

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
        guide_files = [f for f in guide_files if not f.endswith("_kr.md")]
        
    guide_files.sort(key=os.path.getmtime, reverse=True)
    
    for filepath in guide_files:
        try:
            post = frontmatter.load(filepath)
            meta = post.metadata
            guide_id = meta.get('id', '').replace('_kr', '')
            
            # [핵심 추가] 추천 컬렉션(Featured)이 아닌 일반 가이드면 
            # 마크다운 파일 안의 깨진 이미지를 무시하고 안전한 새 이미지 풀에서 고정 할당
            if meta.get('is_featured'):
                safe_thumbnail = meta.get('thumbnail', '')
            else:
                hash_val = int(hashlib.md5(guide_id.encode('utf-8')).hexdigest(), 16)
                safe_thumbnail = GUIDE_THUMBNAILS[hash_val % len(GUIDE_THUMBNAILS)]

            guides.append({
                "title": meta.get('title', 'Untitled'), 
                "description": meta.get('description', ''),
                "category": meta.get('category', 'Guide'), 
                "link": f"/guide/{guide_id}?lang={lang}",
                "thumbnail": safe_thumbnail,  # <--- 안전한 이미지로 강제 적용
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
    if not featured_guides: 
        featured_guides = all_guides[:6]
    else: 
        featured_guides = featured_guides[:6]

    # [수정] 카테고리를 명시하여 알맞은 이미지 풀이 배정되도록 함
    latest_schools = assign_thumbnails([s for s in schools_data if s.get('category') != 'university'][:6], "school")
    latest_universities = assign_thumbnails([s for s in schools_data if s.get('category') == 'university'][:6], "university")
    
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
        "total_schools": len(schools_data), # <--- [신규] 이 줄을 추가해 주세요!
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
    # [수정] "school" 명시
    schools = assign_thumbnails([s for s in schools_data if s.get('category') != 'university'], "school")
            
    return templates.TemplateResponse("list.html", {
        "request": request, "items": schools, "item_type": "school", 
        "title": "All Language Schools" if lang == 'en' else "일본어학교 목록",
        "current_lang": lang,
        "ui": get_ui_text(lang) 
    })

@app.get("/universities", response_class=HTMLResponse)
async def university_list(request: Request, lang: str = Query("en")):
    schools_data, _ = load_school_data(lang)
    # [수정] "university" 명시
    universities = assign_thumbnails([s for s in schools_data if s.get('category') == 'university'], "university")
            
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
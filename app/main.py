# app/main.py

from fastapi import FastAPI, Request, HTTPException, Query
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

# --- [추가] UI 텍스트 번역 사전 ---
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
            return data.get('schools', []), data.get('last_updated', '')
    except Exception as e:
        print(f"Error loading data: {e}")
        return [], ""

def load_guides(lang="en"):
    """언어에 맞는 가이드 로드"""
    guides = []
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

# --- Routes ---

@app.get("/ads.txt", response_class=PlainTextResponse)
async def ads_txt():
    return ADS_TXT_CONTENT

@app.get("/sitemap.xml", response_class=PlainTextResponse)
async def sitemap():
    urls = []
    # 1. 기본 메뉴 페이지들 (EN/KR)
    base_paths = ["", "about", "guide", "schools", "universities", "contact", "policy"]
    for path in base_paths:
        urls.append(f"{DOMAIN}/{path}") # 기본(영어)
        urls.append(f"{DOMAIN}/{path}?lang=kr") # 한국어

    # 2. 학교 & 대학교 상세 페이지 (EN/KR)
    # 영어 데이터를 기준으로 ID 목록을 가져와서 두 언어 URL 생성
    schools_en, _ = load_school_data("en")
    for s in schools_en:
        if s.get('id'):
            urls.append(f"{DOMAIN}/school/{s['id']}")
            urls.append(f"{DOMAIN}/school/{s['id']}?lang=kr")

    # 3. 가이드 상세 페이지 (EN/KR)
    # 가이드는 파일명이 다르므로 별도로 체크하여 추가
    guides_en = load_guides("en")
    for g in guides_en:
        # g['link'] 에 이미 /guide/slug?lang=en 형태가 들어있을 수 있으므로 슬러그만 추출
        slug = g['link'].split('/')[-1].split('?')[0]
        urls.append(f"{DOMAIN}/guide/{slug}")
        urls.append(f"{DOMAIN}/guide/{slug}?lang=kr")

    # 중복 제거
    urls = list(set(urls))

    # XML 생성
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
    ui = get_ui_text(lang) # UI 번역 가져오기

    featured_guides = [g for g in all_guides if g.get('is_featured')]
    if not featured_guides: featured_guides = all_guides[:3]
    else: featured_guides = featured_guides[:3]

    latest_schools = [s for s in schools_data if s.get('category') != 'university'][:6]
    latest_universities = [s for s in schools_data if s.get('category') == 'university'][:6]
    
    tags_with_counts = calculate_tag_counts(schools_data)
    
    university_list = [
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
        "latest_guides": [g for g in all_guides if g not in featured_guides][:6],
        "tags_with_counts": tags_with_counts, 
        "university_list_json": json.dumps(university_list, ensure_ascii=False),
        "current_lang": lang,
        "ui": ui # 템플릿에 UI 번역 전달
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
        "ui": get_ui_text(lang) # UI 번역 전달
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
        "ui": get_ui_text(lang) # UI 번역 전달
    })

@app.get("/schools", response_class=HTMLResponse)
async def school_list(request: Request, lang: str = Query("en")):
    schools_data, _ = load_school_data(lang)
    schools = [s for s in schools_data if s.get('category') != 'university']
    
    school_placeholders = ['https://images.unsplash.com/photo-1544531586-fde5298cdd40?w=500', 'https://images.unsplash.com/photo-1523240795612-9a054b0db644?w=500']
    for i, item in enumerate(schools): 
        if not item.get('thumbnail'): item['thumbnail'] = school_placeholders[i % 2]
            
    return templates.TemplateResponse("list.html", {
        "request": request, "items": schools, "item_type": "school", 
        "title": "All Language Schools" if lang == 'en' else "일본어학교 목록",
        "current_lang": lang,
        "ui": get_ui_text(lang) # UI 번역 전달
    })

@app.get("/universities", response_class=HTMLResponse)
async def university_list(request: Request, lang: str = Query("en")):
    schools_data, _ = load_school_data(lang)
    universities = [s for s in schools_data if s.get('category') == 'university']
    
    univ_placeholders = ['https://images.unsplash.com/photo-1562774053-701939374585?w=500', 'https://images.unsplash.com/photo-1522202176988-66273c2fd55f?w=500']
    for i, item in enumerate(universities): 
        if not item.get('thumbnail'): item['thumbnail'] = univ_placeholders[i % 2]
            
    return templates.TemplateResponse("list.html", {
        "request": request, "items": universities, "item_type": "university", 
        "title": "All Universities" if lang == 'en' else "일본 대학 목록",
        "current_lang": lang,
        "ui": get_ui_text(lang) # UI 번역 전달
    })

@app.get("/guide", response_class=HTMLResponse)
async def guide_list_page(request: Request, lang: str = Query("en")):
    guides = load_guides(lang)
    return templates.TemplateResponse("list.html", {
        "request": request, "items": guides, "item_type": "guide", 
        "title": "Essential Guides" if lang == 'en' else "유학 가이드",
        "current_lang": lang,
        "ui": get_ui_text(lang) # UI 번역 전달
    })

@app.get("/about", response_class=HTMLResponse)
async def about(request: Request): return templates.TemplateResponse("about.html", {"request": request})
@app.get("/contact", response_class=HTMLResponse)
async def contact(request: Request): return templates.TemplateResponse("contact.html", {"request": request})
@app.get("/policy", response_class=HTMLResponse)
async def policy(request: Request): return templates.TemplateResponse("policy.html", {"request": request})
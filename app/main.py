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

app.mount("/static", StaticFiles(directory="app/static"), name="static")
templates = Jinja2Templates(directory="app/templates")

GOOGLE_MAPS_API_KEY = os.getenv("GOOGLE_MAPS_API_KEY")
DOMAIN = "https://jpcampus.net"
DATA_FILE = "app/static/json/schools_data.json"
ADS_TXT_CONTENT = """google.com, pub-8780435268193938, DIRECT, f08c47fec0942fa0"""

# [수정됨] 태그 툴팁 설명(description) 구체화
TAG_DEFINITIONS = {
    'academic': {
        'name': '🎓 Academic Focus', 
        'description': 'Filters for schools with EJU prep courses or a strong focus on university admissions.', 
        'keywords': ["eju", "university", "academic", "進学", "大学"]
    },
    'business': {
        'name': '💼 Business & Job', 
        'description': 'Filters for schools offering specialized courses for business Japanese or job hunting support.', 
        'keywords': ["business", "job", "취업", "ビジネス"]
    },
    'culture': {
        'name': '🗣️ Conversation', 
        'description': 'Filters for schools that emphasize conversational skills and cultural activities, ideal for short-term stays.', 
        'keywords': ["conversation", "culture", "short-term", "회화", "短期", "문화"]
    },
    'affordable': {
        'name': '💰 Affordable', 
        'description': 'Filters for schools with a yearly tuition of less than ¥800,000.', 
        'keywords': []
    },
    'international': {
        'name': '🌏 International', 
        'description': 'Filters for schools where the largest single nationality group is 60% or less of the total students.', 
        'keywords': []
    }
}

def calculate_tag_counts(schools):
    counts = {key: 0 for key in TAG_DEFINITIONS}
    for school in schools:
        if school.get('category') == 'university': continue
        features_str = " ".join(school.get('features', [])).lower()
        for key, definition in TAG_DEFINITIONS.items():
            if any(kw in features_str for kw in definition['keywords']): counts[key] += 1
        cost = school.get('tuition', {}).get('yearly_tuition') or school.get('tuition')
        if isinstance(cost, int) and cost < 800000: counts['affordable'] += 1
        demo = school.get('stats', {}).get('student_demographics', {})
        if demo:
            total_students = sum(filter(None, demo.values()))
            if total_students > 0:
                top_nationality_ratio = max(demo.values() or [0]) / total_students
                if top_nationality_ratio <= 0.6: counts['international'] += 1
    return [{'key': key, 'name': definition['name'], 'description': definition['description'], 'count': counts[key]} for key, definition in TAG_DEFINITIONS.items()]

@app.get("/ads.txt", response_class=PlainTextResponse)
async def ads_txt(): return ADS_TXT_CONTENT

@app.get("/sitemap.xml", response_class=PlainTextResponse)
async def sitemap():
    urls = [f"{DOMAIN}/{path}" for path in ["", "about", "guide", "schools", "universities", "contact", "policy"]]
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, 'r', encoding='utf-8') as f:
            data = json.load(f)
            for s in data.get('schools', []): urls.append(f"{DOMAIN}/school/{s['id']}")
    guide_files = glob.glob(os.path.join("app/content", "guide_*.md"))
    for filepath in guide_files:
        try:
            post = frontmatter.load(filepath)
            if slug := post.metadata.get('id'): urls.append(f"{DOMAIN}/guide/{slug}")
        except Exception: pass
    xml_urls = "".join([f'  <url><loc>{url}</loc><changefreq>weekly</changefreq></url>\n' for url in urls])
    return Response(content=f'<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n{xml_urls}</urlset>', media_type="application/xml")

@app.get("/robots.txt", response_class=PlainTextResponse)
async def robots(): return f"User-agent: *\nAllow: /\nSitemap: {DOMAIN}/sitemap.xml"
    
@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    schools_data = []
    updated_at = ""
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, 'r', encoding='utf-8') as f:
            data = json.load(f)
            schools_data = data.get('schools', [])
            updated_at = data.get('last_updated', '')

    school_count = len([s for s in schools_data if s.get('category') != 'university'])
    meta_desc = f"Compare {school_count} Japanese language schools & universities."

    latest_schools = [s for s in schools_data if s.get('category') != 'university'][:4]
    latest_universities = [s for s in schools_data if s.get('category') == 'university'][:4]
    
    tags_with_counts = calculate_tag_counts(schools_data)

    university_list = [
        {"name_ja": s.get('basic_info', {}).get('name_ja'), "name_en": s.get('basic_info', {}).get('name_en')}
        for s in schools_data if s.get('category') == 'university' and s.get('basic_info', {}).get('name_ja')
    ]

    guides = []
    guide_files = glob.glob(os.path.join("app/content", "guide_*.md"))
    guide_files.sort(reverse=True) 
    for filepath in guide_files[:4]:
        try:
            post = frontmatter.load(filepath)
            meta = post.metadata
            guides.append({"title": meta.get('title'), "description": meta.get('description'), "category": meta.get('tags', ['Guide'])[0], "link": f"/guide/{meta.get('id')}", "thumbnail": meta.get('thumbnail')})
        except Exception: pass

    return templates.TemplateResponse("index.html", {
        "request": request, "schools_json": json.dumps({"schools": schools_data}, ensure_ascii=False),
        "maps_api_key": GOOGLE_MAPS_API_KEY, "meta_url": f"{DOMAIN}/", "meta_title": "JP Campus - Japanese Language School Map", "meta_desc": meta_desc,
        "updated_at": updated_at, "school_count": school_count, "latest_schools": latest_schools, "latest_universities": latest_universities, "latest_guides": guides,
        "tags_with_counts": tags_with_counts, "university_list_json": json.dumps(university_list, ensure_ascii=False)
    })

@app.get("/school/{school_id}", response_class=HTMLResponse)
async def read_school_detail(request: Request, school_id: str):
    md_path = f"app/content/{school_id}.md"
    if not os.path.exists(md_path): raise HTTPException(status_code=404, detail="School not found")
    with open(md_path, 'r', encoding='utf-8') as f: post = frontmatter.load(f)
    raw_content = re.sub(r'\n\s*\*\*\s*\n', '\n\n', re.sub(r'-\s*\n\s*\*\*', '- **', re.sub(r'\.\s*\*', '.\n\n*', re.sub(r'\|([^\n]+)\|\s*\|(:?-+:?)\|', r'|\1|\n|\2|', post.content))))
    content_html = markdown.markdown(raw_content, extensions=['tables', 'fenced_code', 'nl2br', 'sane_lists'])
    school = post.metadata
    name_ja = school.get('basic_info', {}).get('name_ja', 'Unknown')
    name_en = school.get('basic_info', {}).get('name_en', '')
    page_title = f"{name_en} ({name_ja}) - Tuition & Info | JP Campus" if name_en else f"{name_ja} - Japanese Language School Info | JP Campus"
    tuition = school.get('tuition', {}).get('yearly_tuition')
    tuition_str = f"¥{tuition:,}" if isinstance(tuition, int) else "Contact for details"
    location = school.get('basic_info', {}).get('address', 'Japan')
    page_desc = f"Comprehensive guide for {name_ja}. Yearly tuition: {tuition_str}. Located in {location}."
    thumbnail_path = school.get('thumbnail', '/static/img/og-image.png')
    og_image_url = f"{DOMAIN}{thumbnail_path}" if thumbnail_path.startswith('/') else thumbnail_path
    return templates.TemplateResponse("detail.html", {"request": request, "school": school, "content_body": content_html, "meta_url": f"{DOMAIN}/school/{school_id}", "meta_title": page_title, "meta_desc": page_desc, "og_image": og_image_url, "maps_api_key": GOOGLE_MAPS_API_KEY})
@app.get("/guide", response_class=HTMLResponse)
async def guide_list_page(request: Request):
    guides = []
    guide_files = glob.glob(os.path.join("app/content", "guide_*.md"))
    guide_files.sort(reverse=True)
    for filepath in guide_files:
        try:
            post = frontmatter.load(filepath)
            meta = post.metadata
            guides.append({"title": meta.get('title'), "description": meta.get('description'), "category": meta.get('tags', ['Guide'])[0], "link": f"/guide/{meta.get('id')}", "thumbnail": meta.get('thumbnail')})
        except Exception as e: print(f"Error loading guide: {e}")
    return templates.TemplateResponse("guide_list.html", {"request": request, "guides": guides, "meta_title": "Essential Guides for Japan - JP Campus", "meta_desc": "Everything you need to know before studying in Japan."})
@app.get("/guide/{slug}", response_class=HTMLResponse)
async def guide_detail(request: Request, slug: str):
    md_path = os.path.join("app/content", f"guide_{slug}.md")
    if not os.path.exists(md_path): raise HTTPException(status_code=404, detail="Guide not found")
    with open(md_path, 'r', encoding='utf-8') as f: post = frontmatter.load(f)
    content_html = markdown.markdown(post.content, extensions=['tables', 'fenced_code', 'nl2br', 'sane_lists'])
    meta = post.metadata
    og_image_url = meta.get('thumbnail', f"{DOMAIN}/static/img/og-image.png")
    return templates.TemplateResponse("guide_detail.html", {"request": request, "guide": meta, "content_body": content_html, "meta_title": f"{meta['title']} - JP Campus Guide", "meta_desc": meta.get('description', ''), "meta_url": f"{DOMAIN}/guide/{slug}", "og_image": og_image_url})
@app.get("/schools", response_class=HTMLResponse)
async def school_list(request: Request):
    with open(DATA_FILE, 'r', encoding='utf-8') as f: data = json.load(f)
    schools = [s for s in data['schools'] if s.get('category') != 'university']
    return templates.TemplateResponse("school_list.html", {"request": request, "items": schools, "title": "Japanese Language Schools", "description": "Browse all Japanese language schools across Japan."})
@app.get("/universities", response_class=HTMLResponse)
async def university_list(request: Request):
    with open(DATA_FILE, 'r', encoding='utf-8') as f: data = json.load(f)
    universities = [s for s in data['schools'] if s.get('category') == 'university']
    return templates.TemplateResponse("school_list.html", {"request": request, "items": universities, "title": "Universities in Japan", "description": "Explore top universities in Japan for international students."})
@app.get("/about", response_class=HTMLResponse)
async def about(request: Request): return templates.TemplateResponse("about.html", {"request": request})
@app.get("/contact", response_class=HTMLResponse)
async def contact(request: Request): return templates.TemplateResponse("contact.html", {"request": request})
@app.get("/policy", response_class=HTMLResponse)
async def policy(request: Request): return templates.TemplateResponse("policy.html", {"request": request})
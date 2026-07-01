# app/utils.py
import json
import os
import glob
import hashlib

import frontmatter
from fastapi import Request

from app.content_badges import enrich_item
from app.i18n import get_ui_text
from app.thumbnails import (
    broken_thumbnail_redirects,
    guide_thumbnails,
    school_thumbnails,
    univ_thumbnails,
)

# --- 디렉토리 경로 설정 ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
STATIC_DIR = os.path.join(BASE_DIR, "static")
CONTENT_DIR = os.path.join(BASE_DIR, "content") 
TEMPLATES_DIR = os.path.join(BASE_DIR, "templates")

# --- 기존 필터 정의 ---
TAG_DEFINITIONS = {
    'academic': {'name': 'Academic', 'icon': '🎓', 'description': 'Schools with a strong focus on university admissions (EJU prep).', 'keywords':["eju", "university", "academic", "進学", "大学"]},
    'business': {'name': 'Business', 'icon': '💼', 'description': 'Schools with business Japanese courses or job hunting support.', 'keywords':["business", "job", "취업", "ビジネス"]},
    'culture': {'name': 'Conversation', 'icon': '🗣️', 'description': 'Schools emphasizing conversational skills and cultural activities.', 'keywords':["conversation", "culture", "short-term", "회화", "短期", "문화"]},
    'tokyo': {'name': 'Tokyo', 'icon': '🏙️', 'description': 'Schools located in the Tokyo area.'},
    'osaka': {'name': 'Osaka', 'icon': '🏯', 'description': 'Schools located in the Osaka area.'},
    'nagoya': {'name': 'Nagoya', 'icon': '🚃', 'description': 'Schools in the Nagoya / Aichi area.'},
    'kyoto': {'name': 'Kyoto', 'icon': '⛩️', 'description': 'Schools in the Kyoto area.'},
    'major_city': {'name': 'Cities', 'icon': '🌇', 'description': 'Schools in other major cities (e.g., Fukuoka, Sapporo).'},
    'size_small': {'name': 'Small', 'icon': '🧑‍🏫', 'description': 'Small-sized schools (Capacity: ~150 students).'},
    'size_medium': {'name': 'Medium', 'icon': '👨‍👩‍👧‍👦', 'description': 'Medium-sized schools (Capacity: 151-500 students).'},
    'dormitory': {'name': 'Dormitory', 'icon': '🏠', 'description': 'Schools that offer dormitory options.'},
}

def calculate_tag_counts(schools):
    counts = {key: 0 for key in TAG_DEFINITIONS}
    MAJOR_CITIES =['福岡', '名古屋', '京都', '神戸', '札幌', '横浜', '仙台']
    DORM_KEYWORDS =['dormitory', '기숙사', '寮']

    for school in schools:
        if school.get('category') == 'university': continue

        # [방어 로직] features가 null이거나 문자가 섞여 있어도 절대 에러 나지 않음
        features = school.get('features')
        if not features: features = []
        elif isinstance(features, str): features = [features]
        
        safe_features = [str(f) for f in features if f is not None]
        full_text = " ".join(safe_features).lower()
        
        if any(kw in full_text for kw in TAG_DEFINITIONS['academic']['keywords']): counts['academic'] += 1
        if any(kw in full_text for kw in TAG_DEFINITIONS['business']['keywords']): counts['business'] += 1
        if any(kw in full_text for kw in TAG_DEFINITIONS['culture']['keywords']): counts['culture'] += 1

        b_info = school.get('basic_info') or {}
        address = b_info.get('address') or ''
        if '東京都' in address:
            counts['tokyo'] += 1
        elif '大阪府' in address:
            counts['osaka'] += 1
        elif ('名古屋' in address or '愛知' in address):
            counts['nagoya'] += 1
        elif '京都' in address:
            counts['kyoto'] += 1
        elif any(city in address for city in MAJOR_CITIES): counts['major_city'] += 1
        
        capacity = b_info.get('capacity')
        if isinstance(capacity, int):
            if capacity <= 150: counts['size_small'] += 1
            elif capacity <= 500: counts['size_medium'] += 1
        
        if any(kw in full_text for kw in DORM_KEYWORDS): counts['dormitory'] += 1

    results = [
        {'key': key, 'name': d['name'], 'icon': d['icon'], 'description': d['description'], 'count': counts[key]}
        for key, d in TAG_DEFINITIONS.items()
    ]
    return [tag for tag in results if tag['count'] >= 5]

def get_type_filters(lang="en"):
    ui = get_ui_text(lang)
    return [
        {"key": "all", "icon": "📍", "label": ui["filter_all"]},
        {"key": "dormitory", "icon": "🏠", "label": ui["filter_dormitory"]},
        {"key": "academic", "icon": "🎓", "label": ui["filter_academic"]},
        {"key": "university", "icon": "🏛️", "label": ui["filter_universities"]},
        {"key": "size_medium", "icon": "📊", "label": ui["filter_medium"]},
    ]


def get_region_filters(lang="en"):
    ui = get_ui_text(lang)
    return [
        {"key": "all", "icon": "🌏", "label": ui["filter_all_regions"]},
        {"key": "tokyo", "icon": "🏙️", "label": ui["filter_tokyo"]},
        {"key": "osaka", "icon": "🏯", "label": ui["filter_osaka"]},
        {"key": "nagoya", "icon": "🚃", "label": ui["filter_nagoya"]},
        {"key": "kyoto", "icon": "⛩️", "label": ui["filter_kyoto"]},
        {"key": "major_city", "icon": "🌇", "label": ui["filter_other_cities"]},
    ]


def get_client_ip(request: Request):
    try:
        x_forwarded_for = request.headers.get("X-Forwarded-For")
        if x_forwarded_for: return x_forwarded_for.split(",")[0].strip()
        if request.client and request.client.host: return request.client.host
    except Exception: pass
    return "unknown_ip"

def resolve_guide_thumbnail(meta: dict, guide_id: str) -> str:
    """Use frontmatter thumbnail when set; otherwise stable pool by guide id."""
    thumb = (meta.get("thumbnail") or "").strip()
    thumb = broken_thumbnail_redirects().get(thumb, thumb)
    if thumb.startswith(("http://", "https://", "/")):
        return thumb
    key = (guide_id or "guide").replace("_kr", "")
    pool = guide_thumbnails()
    hash_val = int(hashlib.md5(key.encode("utf-8")).hexdigest(), 16)
    return pool[hash_val % len(pool)]


def assign_thumbnails(items, item_category="school"):
    thumb_pool = univ_thumbnails() if item_category == "university" else school_thumbnails()

    for item in items:
        if not item.get('thumbnail'):
            item_id = str(item.get('id', 'default_id'))
            hash_val = int(hashlib.md5(item_id.encode('utf-8')).hexdigest(), 16)
            item['thumbnail'] = thumb_pool[hash_val % len(thumb_pool)]
    return items


def compare_city(item: dict) -> str:
    address = item.get("basic_info", {}).get("address", "")
    if not address:
        return "—"
    return address.split(",")[0].strip()

def compare_fee_value(item: dict) -> int | None:
    tuition = item.get("tuition") or {}
    value = tuition.get("yearly_tuition")
    return value if isinstance(value, (int, float)) else None

def compare_fee_label(item: dict, lang: str) -> str | None:
    value = compare_fee_value(item)
    if value is None:
        return None
    suffix = " <small>(yearly)</small>" if item.get("category") == "university" else " <small>(yearly tuition)</small>"
    return f"¥{int(value):,}{suffix}"

def prepare_compare_items(items: list[dict], lang: str) -> list[dict]:
    prepared = []
    for item in items:
        row = dict(item)
        row["compare_city"] = compare_city(item)
        row["compare_fee_value"] = compare_fee_value(item)
        row["compare_fee_label"] = compare_fee_label(item, lang)
        fee_value = compare_fee_value(item)
        row["compare_fee_plain"] = f"¥{int(fee_value):,}" if fee_value is not None else None
        prepared.append(row)
    return prepared

def build_compare_export(selected: list[dict], lang: str, site_name: str) -> dict:
    items = []
    for item in selected:
        bi = item.get("basic_info", {}) or {}
        name = bi.get("name_display") or bi.get("name_en") or bi.get("name_ja") or bi.get("name_ko") or item.get("id", "")
        fee = item.get("compare_fee_plain") or item.get("compare_fee_label", "")
        if fee and "<" in str(fee):
            fee = str(fee).split("<")[0].strip()
        features = item.get("features") or []
        items.append({
            "name": name,
            "city": item.get("compare_city", "—"),
            "fee": fee or "—",
            "features": features[:3],
        })
    return {"siteName": site_name, "lang": lang, "items": items}

def load_school_data(lang="en"):
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
        return [], ""

def load_guides(lang="en"):
    guides =[]
    pattern = os.path.join(CONTENT_DIR, "guide_*_kr.md") if lang == "kr" else os.path.join(CONTENT_DIR, "guide_*.md")
    guide_files = glob.glob(pattern)
    if lang != "kr":
        guide_files =[f for f in guide_files if not f.endswith("_kr.md")]
        
    guide_files.sort(key=os.path.getmtime, reverse=True)
    
    for filepath in guide_files:
        try:
            post = frontmatter.load(filepath)
            meta = post.metadata
            guide_id = str(meta.get('id', '')).replace('_kr', '')
            safe_thumbnail = resolve_guide_thumbnail(meta, guide_id)

            guides.append(enrich_item({
                "title": meta.get('title', 'Untitled'), 
                "description": meta.get('description', ''),
                "category": meta.get('category', 'Guide'), 
                "link": f"/guide/{guide_id}?lang={lang}",
                "thumbnail": safe_thumbnail,
                "item_type": "guide",
                "is_featured": meta.get('is_featured', False),
                "published": str(meta.get('date', '')),
            }))
        except Exception:
            pass
    return guides
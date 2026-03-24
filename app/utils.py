# app/utils.py
import json
import os
import glob
import hashlib
import frontmatter
from fastapi import Request

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
    'major_city': {'name': 'Cities', 'icon': '🌇', 'description': 'Schools in other major cities (e.g., Fukuoka, Nagoya).'},
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
        if '東京都' in address: counts['tokyo'] += 1
        elif '大阪府' in address: counts['osaka'] += 1
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

def get_client_ip(request: Request):
    try:
        x_forwarded_for = request.headers.get("X-Forwarded-For")
        if x_forwarded_for: return x_forwarded_for.split(",")[0].strip()
        if request.client and request.client.host: return request.client.host
    except Exception: pass
    return "unknown_ip"

# =========================================================================
# 🚨 여기에 대표님이 가지고 계신 90개의 썸네일 리스트를 그대로 붙여넣으세요! 🚨
# --- 썸네일 풀 (3종류 - 총 90개) ---
UNIV_THUMBNAILS =[
    "https://images.unsplash.com/photo-1541339907198-e08756dedf3f?w=500", "https://images.unsplash.com/photo-1498243691581-b145c3f54a5a?w=500",
    "https://images.unsplash.com/photo-1592280771190-3e2e4d571952?w=500", "https://images.unsplash.com/photo-1562774053-701939374585?w=500",
    "https://images.unsplash.com/photo-1606092195730-5d7b9af1efc5?w=500", "https://images.unsplash.com/photo-1521587760476-6c12a4b040da?w=500",
    "https://images.unsplash.com/photo-1541336318489-083c7d277b8e?w=500",
    "https://images.unsplash.com/photo-1584697964190-7383cbee8277?w=500", "https://images.unsplash.com/photo-1511629091441-ee46146481b6?w=500",
    "https://images.unsplash.com/photo-1573894998033-c0cef4ed722b?w=500", "https://images.unsplash.com/photo-1485893086445-ed75865251e0?w=500",
    "https://images.unsplash.com/photo-1568038479111-87bf80659645?w=500", "https://images.unsplash.com/photo-1542621334-a254cf47733d?w=500",
    "https://images.unsplash.com/photo-1497634763913-2ea08bf9de5d?w=500", "https://images.unsplash.com/photo-1500088139251-37350df3c1ad?w=500",
    "https://images.unsplash.com/photo-1547699326-3d895d9acd30?w=500", "https://images.unsplash.com/photo-1530785602389-07594beb8b73?w=500",
    "https://images.unsplash.com/photo-1612310480588-061aad90bb64?w=500",
    "https://images.unsplash.com/photo-1596207891316-24e52f534cb3?w=500",
    "https://images.unsplash.com/photo-1558223602-0e2ff17571db?w=500",
    "https://images.unsplash.com/photo-1566374971846-5b4819c962b1?w=500",
    "https://images.unsplash.com/photo-1590895315572-c51323ca7369?w=500"
]

SCHOOL_THUMBNAILS =[
    "https://images.unsplash.com/photo-1503676260728-1c00da094a0b?w=500", "https://images.unsplash.com/photo-1509062522246-3755977927d7?w=500",
    "https://images.unsplash.com/photo-1456513080510-7bf3a84b82f8?w=500", "https://images.unsplash.com/photo-1580582932707-520aed937b7b?w=500",
    "https://images.unsplash.com/photo-1544531586-fde5298cdd40?w=500", "https://images.unsplash.com/photo-1493976040374-85c8e12f0c0e?w=500",
    "https://images.unsplash.com/photo-1528164344705-47542687000d?w=500", "https://images.unsplash.com/photo-1577985051167-0d49eec21977?w=500",
    "https://images.unsplash.com/photo-1581092334978-16972703644f?w=500", "https://images.unsplash.com/photo-1608813607488-0f932c5b71ef?w=500",
    "https://images.unsplash.com/photo-1581276879432-15e50529f34b?w=500", "https://images.unsplash.com/photo-1584697964190-7383cbee8277?w=500",
    "https://images.unsplash.com/photo-1577825294026-50dc375b9119?w=500", "https://images.unsplash.com/photo-1453694595360-51e193e121fc?w=500",
    "https://images.unsplash.com/photo-1573416033034-e42e14b545d2?w=500", "https://images.unsplash.com/photo-1586877644127-e5ee9b4231c3?w=500",
    "https://images.unsplash.com/photo-1550303435-1703d8811aaa?w=500", "https://images.unsplash.com/photo-1505738313577-5357ff512f16?w=500",
    "https://images.unsplash.com/photo-1561535893-bb7a98c7ee45?w=500", "https://images.unsplash.com/photo-1523905330026-b8bd1f5f320e?w=500",
    "https://images.unsplash.com/photo-1613376023733-0a73315d9b06?w=500", "https://images.unsplash.com/photo-1493934558415-9d19f0b2b4d2?w=500",
    "https://images.unsplash.com/photo-1541336318489-083c7d277b8e?w=500", "https://images.unsplash.com/photo-1622589476300-b72799ca4ade?w=500",
    "https://images.unsplash.com/photo-1639621108959-15f9c4257508?w=500", "https://images.unsplash.com/photo-1503387762-592deb58ef4e?w=500",
    "https://images.unsplash.com/photo-1586023492125-27b2c045efd7?w=500", "https://images.unsplash.com/photo-1526916025899-1a28d20f2a5f?w=500",
    "https://images.unsplash.com/photo-1559077138-3e27e1cdb95a?w=500", "https://images.unsplash.com/photo-1598368195835-91e67f80c9d7?w=500"
]

GUIDE_THUMBNAILS =[
    "https://images.unsplash.com/photo-1491841550275-ad7854e35ca6?w=500", "https://images.unsplash.com/photo-1610312278520-bcc893a3ff1d?w=500",
    "https://images.unsplash.com/photo-1590559899731-a382839e5549?w=500", "https://images.unsplash.com/photo-1436491865332-7a61a109cc05?w=500",
    "https://images.unsplash.com/photo-1561414927-6d86591d0c4f?w=500", "https://images.unsplash.com/photo-1522708323590-d24dbb6b0267?w=500",
    "https://images.unsplash.com/photo-1556740758-90de374c12ad?w=500", "https://images.unsplash.com/photo-1563986768609-322da13575f3?w=500",
    "https://images.unsplash.com/photo-1505751172876-fa1923c5c528?w=500", "https://images.unsplash.com/photo-1542051841857-5f90071e7989?w=500",
    "https://images.unsplash.com/photo-1580167227251-be70f01b0c51?w=500", "https://images.unsplash.com/photo-1684526688489-b08cbd8e1848?w=500",
    "https://images.unsplash.com/photo-1603491543570-f7df3c9a12c1?w=500", "https://images.unsplash.com/photo-1563089145-599997674d42?w=500",
    "https://images.unsplash.com/photo-1580477667995-2b94f01c9516?w=500", "https://images.unsplash.com/photo-1560972550-aba3456b5564?w=500",
    "https://images.unsplash.com/photo-1580477371971-91fc2a9a4899?w=500", "https://images.unsplash.com/photo-1548630435-998a2cbbff67?w=500",
    "https://images.unsplash.com/photo-1473496169904-658ba7c44d8a?w=500", "https://images.unsplash.com/photo-1558471250-385a4b04941e?w=500",
    "https://images.unsplash.com/photo-1526127230111-0197afe94d72?w=500", "https://images.unsplash.com/photo-1557409518-691ebcd96038?w=500",
    "https://images.unsplash.com/photo-1516205651411-aef33a44f7c2?w=500", "https://images.unsplash.com/photo-1551322120-c697cf88fbdc?w=500",
    "https://images.unsplash.com/photo-1573655349936-de6bed86f839?w=500", "https://images.unsplash.com/photo-1540569014015-19a7be504e3a?w=500",
    "https://images.unsplash.com/photo-1503899036084-c55cdd94dd10?w=500", "https://images.unsplash.com/photo-1492571350019-22de08371fd3?w=500",
    "https://images.unsplash.com/photo-1524413840847-05c04c1f964b?w=500", "https://images.unsplash.com/photo-1522199755839-a2bacb67c546?w=500"
]
# =========================================================================

def assign_thumbnails(items, item_category="school"):
    if item_category == "university": thumb_pool = UNIV_THUMBNAILS
    else: thumb_pool = SCHOOL_THUMBNAILS

    for item in items:
        if not item.get('thumbnail'):
            item_id = str(item.get('id', 'default_id')) 
            hash_val = int(hashlib.md5(item_id.encode('utf-8')).hexdigest(), 16)
            item['thumbnail'] = thumb_pool[hash_val % len(thumb_pool)]
    return items

def get_ui_text(lang):
    if lang == "kr":
        return {
            "featured_title": "추천 컬렉션", "best_selection": "추천", "view_ranking": "랭킹 보기 →",
            "language_schools": "일본어 어학원", "top_universities": "주요 대학교", "view_all": "전체 보기 →",
            "essential_guides": "유학 가이드", "school_badge": "어학원", "univ_badge": "대학교",
            "contact_fee": "학비 문의", "yearly": "연간", "search_placeholder": "대학교 검색...",
            "all_schools": "모든 학교", "back_to_map": "지도로 돌아가기", "back_to_list": "목록으로 돌아가기",
            "global_programs": "글로벌 프로그램", "national_private": "공식 국공립/사립 기관",
            "view_all_schools": "모든 학교 보기 →", "view_all_univs": "모든 대학교 보기 →"
        }
    return {
        "featured_title": "Featured Collections", "best_selection": "Best Selection", "view_ranking": "View Ranking →",
        "language_schools": "Language Schools", "top_universities": "Top Universities", "view_all": "View all →",
        "essential_guides": "Essential Guides", "school_badge": "School", "univ_badge": "University",
        "contact_fee": "Contact for Fee", "yearly": "Yearly", "search_placeholder": "Search universities...",
        "all_schools": "All Schools", "back_to_map": "Back to Map", "back_to_list": "Back to List",
        "global_programs": "Global Programs", "national_private": "Official National/Private Institute",
        "view_all_schools": "View all schools →", "view_all_univs": "View all universities →"
    }

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
                "thumbnail": safe_thumbnail,
                "item_type": "guide",
                "is_featured": meta.get('is_featured', False)
            })
        except Exception:
            pass
    return guides
# app/utils.py
import json
import os
import glob
import hashlib

try:
    from .content_new import enrich_item
except ImportError:
    from content_new import enrich_item
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


def get_quick_filters(lang="en"):
    return get_type_filters(lang) + get_region_filters(lang)[1:]

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
    "https://images.unsplash.com/photo-1584697964190-7383cbee8277?w=500", "https://images.unsplash.com/photo-1511629091441-ee46146481b6?w=500",
    "https://images.unsplash.com/photo-1573894998033-c0cef4ed722b?w=500", "https://images.unsplash.com/photo-1485893086445-ed75865251e0?w=500",
    "https://images.unsplash.com/photo-1568038479111-87bf80659645?w=500", "https://images.unsplash.com/photo-1542621334-a254cf47733d?w=500",
    "https://images.unsplash.com/photo-1500088139251-37350df3c1ad?w=500",
    "https://images.unsplash.com/photo-1547699326-3d895d9acd30?w=500", 
    "https://images.unsplash.com/photo-1612310480588-061aad90bb64?w=500",
    "https://images.unsplash.com/photo-1592280771190-3e2e4d571952?w=600", "https://images.unsplash.com/photo-1562774053-701939374585?w=600",
    "https://images.unsplash.com/photo-1606092195730-5d7b9af1efc5?w=600", "https://images.unsplash.com/photo-1521587760476-6c12a4b040da?w=600",
    "https://images.unsplash.com/photo-1541336318489-083c7d277b8e?w=600", 
    "https://images.unsplash.com/photo-1511629091441-ee46146481b6?w=600",
    "https://images.unsplash.com/photo-1464938050520-ef2270bb8ce8?w=600", "https://images.unsplash.com/photo-1519452635265-7b1fbfd1e4e0?w=600",
    "https://images.unsplash.com/photo-1517486808906-6ca8b3f04846?w=600",
    "https://images.unsplash.com/photo-1568605117036-5fe5e7bab0b7?w=600",
    "https://images.unsplash.com/photo-1527891751199-7225231a68dd?w=600"

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
    "https://images.unsplash.com/photo-1548630435-998a2cbbff67?w=500",
    "https://images.unsplash.com/photo-1473496169904-658ba7c44d8a?w=500", "https://images.unsplash.com/photo-1558471250-385a4b04941e?w=500",
    "https://images.unsplash.com/photo-1526127230111-0197afe94d72?w=500", "https://images.unsplash.com/photo-1557409518-691ebcd96038?w=500",
    "https://images.unsplash.com/photo-1516205651411-aef33a44f7c2?w=500", "https://images.unsplash.com/photo-1551322120-c697cf88fbdc?w=500",
    "https://images.unsplash.com/photo-1573655349936-de6bed86f839?w=500", "https://images.unsplash.com/photo-1540569014015-19a7be504e3a?w=500",
    "https://images.unsplash.com/photo-1492571350019-22de08371fd3?w=500",
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
            "view_all_schools": "모든 학교 보기 →", "view_all_univs": "모든 대학교 보기 →",
            "find_schools": "학교 찾기", "find_universities": "대학 찾기", "read_guides": "가이드 보기",
            "filter_all": "전체", "filter_tokyo": "도쿄", "filter_osaka": "오사카", "filter_nagoya": "나고야", "filter_kyoto": "교토",
            "filter_dormitory": "기숙사",
            "filter_academic": "진학", "filter_universities": "대학", "filter_other_cities": "기타 도시",
            "filter_medium": "중형", "filter_all_regions": "전 지역",
            "filter_row_type": "유형", "filter_row_region": "지역",
            "schools_listed": "개 학교 등록됨", "last_updated": "최근 업데이트:", "updating_weekly": "매주 업데이트 중",
            "reaction_title": "이 페이지가 도움이 되었나요?",
            "reaction_subtitle": "피드백은 콘텐츠 개선에 활용합니다",
            "share_label": "이 페이지 공유하기",
            "share_copy": "링크 복사",
            "share_copied": "복사됨!",
            "share_hint": "X 공유는 미리보기 전용 /card/ URL을 사용합니다. 이미지가 안 보이면 ",
            "share_hint_link": "카드 페이지",
            "share_hint_tail": "를 새 탭에서 연 뒤 X 버튼으로 공유하세요.",
            "category": "구분", "capacity": "정원", "yearly_tuition": "연간 학비", "view_details": "상세 보기",
            "students": "유학생 수", "language_school": "어학원", "university": "대학교", "guide_badge": "가이드",
            "compare_header": "비교",
            "compare_add": "+ 비교",
            "compare_added": "✓ 비교 중",
            "compare_selected": "개 선택",
            "compare_clear": "초기화",
            "compare_now": "비교하기",
            "compare_title": "학교 비교",
            "compare_desc": "최대 3개 학교를 선택해 학비·지역·특징을 나란히 비교하세요.",
            "compare_table_title": "나란히 비교",
            "compare_schools_compared": "개 학교 비교 중",
            "compare_need_more": "한 곳 더 추가하세요",
            "compare_pick_schools": "목록에서 2~3개 학교를 선택하세요",
            "compare_empty_html": "비교하려면 목록에서 <strong>2개 이상</strong>의 학교를 선택하세요.",
            "compare_remove": "제거",
            "compare_row_type": "구분",
            "compare_row_city": "도시",
            "compare_row_fees": "학비",
            "compare_row_features": "특징",
            "compare_toast_added": "비교 목록에 추가했습니다 ✓",
            "compare_toast_removed": "비교 목록에서 제거했습니다",
            "compare_toast_max": "최대 3개 — 하나를 제거하세요",
            "compare_toast_cleared": "비교 목록을 초기화했습니다",
            "meta_compare_title": "학교 비교 | JP Campus",
            "meta_compare_desc": "일본어 어학원·대학을 최대 3개까지 나란히 비교하세요. 학비·정원·유학생 수·특징을 한눈에 확인합니다.",
            "compare_copy_url": "비교 링크 복사",
            "compare_copy_text": "비교 텍스트 복사",
            "compare_copied": "복사됨!",
            "compare_related_guides": "관련 가이드",
        }
    return {
        "featured_title": "Featured Collections", "best_selection": "Best Selection", "view_ranking": "View Ranking →",
        "language_schools": "Language Schools", "top_universities": "Top Universities", "view_all": "View all →",
        "essential_guides": "Essential Guides", "school_badge": "School", "univ_badge": "University",
        "contact_fee": "Contact for Fee", "yearly": "Yearly", "search_placeholder": "Search universities...",
        "all_schools": "All Schools", "back_to_map": "Back to Map", "back_to_list": "Back to List",
        "global_programs": "Global Programs", "national_private": "Official National/Private Institute",
        "view_all_schools": "View all schools →", "view_all_univs": "View all universities →",
        "find_schools": "Find Schools", "find_universities": "Find Universities", "read_guides": "Read Guides",
        "filter_all": "All", "filter_tokyo": "Tokyo", "filter_osaka": "Osaka", "filter_nagoya": "Nagoya", "filter_kyoto": "Kyoto",
        "filter_dormitory": "Dorm",
        "filter_academic": "Prep", "filter_universities": "Univ", "filter_other_cities": "Other Cities",
        "filter_medium": "Mid", "filter_all_regions": "All areas",
        "filter_row_type": "Type", "filter_row_region": "Region",
        "schools_listed": "Schools Listed", "last_updated": "Last Updated:", "updating_weekly": "Updating Weekly",
        "reaction_title": "Was this page helpful?",
        "reaction_subtitle": "Your feedback helps us improve our guides",
        "share_label": "Share this page",
        "share_copy": "Copy link",
        "share_copied": "Copied!",
        "share_hint": "X shares use the /card/ preview URL. If the image is missing, ",
        "share_hint_link": "open the card page",
        "share_hint_tail": ", then share again via the X button.",
        "category": "Category", "capacity": "Capacity", "yearly_tuition": "Yearly Tuition", "view_details": "View Details",
        "students": "Students", "language_school": "Language School", "university": "University", "guide_badge": "Guide",
        "compare_header": "Compare",
        "compare_add": "+ Compare",
        "compare_added": "✓ Comparing",
        "compare_selected": "selected",
        "compare_clear": "Clear",
        "compare_now": "Compare now",
        "compare_title": "School Compare",
        "compare_desc": "Select up to 3 schools or universities to compare fees, location, and features side by side.",
        "compare_table_title": "Side-by-side comparison",
        "compare_schools_compared": "schools compared",
        "compare_need_more": "add one more",
        "compare_pick_schools": "Pick 2–3 schools from the list for a meaningful comparison",
        "compare_empty_html": "Select at least <strong>2 schools</strong> from the list to see a comparison.",
        "compare_remove": "Remove",
        "compare_row_type": "Type",
        "compare_row_city": "City",
        "compare_row_fees": "Tuition / fees",
        "compare_row_features": "Features",
        "compare_toast_added": "Added to compare ✓",
        "compare_toast_removed": "Removed from compare",
        "compare_toast_max": "Max 3 schools — remove one first",
        "compare_toast_cleared": "Compare list cleared",
        "meta_compare_title": "Compare Schools | JP Campus",
        "meta_compare_desc": "Compare up to 3 Japanese language schools or universities side by side — fees, capacity, international students, and features.",
        "compare_copy_url": "Copy comparison link",
        "compare_copy_text": "Copy as text",
        "compare_copied": "Copied!",
        "compare_related_guides": "Related guides",
    }

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
            
            if meta.get('is_featured'):
                safe_thumbnail = meta.get('thumbnail', '')
            else:
                hash_val = int(hashlib.md5(guide_id.encode('utf-8')).hexdigest(), 16)
                safe_thumbnail = GUIDE_THUMBNAILS[hash_val % len(GUIDE_THUMBNAILS)]

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
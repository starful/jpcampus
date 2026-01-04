# app/utils.py

import json

# [수정] 새로운 필터 정의 (아이콘, 설명 포함)
TAG_DEFINITIONS = {
    # 기존 필터 (유지)
    'academic': {
        'name': 'Academic', 'icon': '🎓',
        'description': 'Schools with a strong focus on university admissions (EJU prep).',
        'keywords': ["eju", "university", "academic", "進学", "大学"]
    },
    'business': {
        'name': 'Business', 'icon': '💼',
        'description': 'Schools with business Japanese courses or job hunting support.',
        'keywords': ["business", "job", "취업", "ビジネス"]
    },
    'culture': {
        'name': 'Conversation', 'icon': '🗣️',
        'description': 'Schools emphasizing conversational skills and cultural activities.',
        'keywords': ["conversation", "culture", "short-term", "회화", "短期", "문화"]
    },
    # [신규] 지역별 필터
    'tokyo': {'name': 'Tokyo', 'icon': '🏙️', 'description': 'Schools located in the Tokyo area.'},
    'osaka': {'name': 'Osaka', 'icon': '🏯', 'description': 'Schools located in the Osaka area.'},
    'major_city': {'name': 'Cities', 'icon': '🌇', 'description': 'Schools in other major cities (e.g., Fukuoka, Nagoya).'},
    # [신규] 학교 규모별 필터
    'size_small': {'name': 'Small', 'icon': '🧑‍🏫', 'description': 'Small-sized schools (Capacity: ~150 students).'},
    'size_medium': {'name': 'Medium', 'icon': '👨‍👩‍👧‍👦', 'description': 'Medium-sized schools (Capacity: 151-500 students).'},
    # [신규] 기숙사 유무 필터
    'dormitory': {'name': 'Dormitory', 'icon': '🏠', 'description': 'Schools that offer dormitory options.'},
}

def calculate_tag_counts(schools):
    """학교 목록을 받아 새 기준에 따라 태그별 카운트를 계산하고, 결과가 적은 태그는 제외하여 반환"""
    counts = {key: 0 for key in TAG_DEFINITIONS}
    
    # 주요 도시 키워드
    MAJOR_CITIES = ['福岡', '名古屋', '京都', '神戸', '札幌', '横浜', '仙台']
    DORM_KEYWORDS = ['dormitory', '기숙사', '寮']

    for school in schools:
        if school.get('category') == 'university':
            continue

        # --- 키워드 기반 필터 (기존 로직 활용) ---
        full_text = " ".join(school.get('features', [])).lower()
        if any(kw in full_text for kw in TAG_DEFINITIONS['academic']['keywords']):
            counts['academic'] += 1
        if any(kw in full_text for kw in TAG_DEFINITIONS['business']['keywords']):
            counts['business'] += 1
        if any(kw in full_text for kw in TAG_DEFINITIONS['culture']['keywords']):
            counts['culture'] += 1

        # --- [신규] 지역별 필터링 ---
        address = school.get('basic_info', {}).get('address', '')
        if '東京都' in address:
            counts['tokyo'] += 1
        elif '大阪府' in address:
            counts['osaka'] += 1
        elif any(city in address for city in MAJOR_CITIES):
            counts['major_city'] += 1
        
        # --- [신규] 학교 규모별 필터링 ---
        capacity = school.get('basic_info', {}).get('capacity')
        if isinstance(capacity, int):
            if capacity <= 150:
                counts['size_small'] += 1
            elif capacity <= 500:
                counts['size_medium'] += 1
        
        # --- [신규] 기숙사 유무 필터링 ---
        if any(kw in full_text for kw in DORM_KEYWORDS):
            counts['dormitory'] += 1

    # 최종 결과 리스트 생성
    results = [
        {'key': key, 'name': definition['name'], 'icon': definition['icon'], 
         'description': definition['description'], 'count': counts[key]}
        for key, definition in TAG_DEFINITIONS.items()
    ]
    
    # [핵심] 카운트가 5 미만인 태그는 최종 목록에서 제외
    return [tag for tag in results if tag['count'] >= 5]
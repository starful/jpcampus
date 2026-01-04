import json

# 태그 정의 및 설명
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
    """학교 목록을 받아 태그별 카운트를 계산하여 반환"""
    counts = {key: 0 for key in TAG_DEFINITIONS}
    
    for school in schools:
        if school.get('category') == 'university':
            continue

        features_str = " ".join(school.get('features', [])).lower()
        career_path_str = json.dumps(school.get('stats', {}).get('career_path', {}), ensure_ascii=False).lower()
        full_search_str = features_str + " " + career_path_str
        
        # 키워드 기반
        for key, definition in TAG_DEFINITIONS.items():
            if any(kw in full_search_str for kw in definition['keywords']):
                counts[key] += 1
        
        # 학비 기반 (Affordable)
        cost = school.get('tuition', {}).get('yearly_tuition') or school.get('tuition')
        if isinstance(cost, int) and cost < 800000:
            counts['affordable'] += 1
            
        # 국적 비율 기반 (International)
        demo = school.get('stats', {}).get('student_demographics', {})
        if demo:
            total_students = sum(filter(None, demo.values()))
            if total_students > 0:
                top_nationality_ratio = max(demo.values() or [0]) / total_students
                if top_nationality_ratio <= 0.6:
                    counts['international'] += 1
                
    return [
        {'key': key, 'name': definition['name'], 'description': definition['description'], 'count': counts[key]}
        for key, definition in TAG_DEFINITIONS.items()
    ]
import json
import os
import time
import re
import frontmatter
from datetime import datetime
from common import setup_logging, setup_gemini, clean_json_response, DATA_DIR, CONTENT_DIR, LOG_DIR

# --- 설정 ---
setup_logging("auto_featured.log")
model = setup_gemini()

# 학교 데이터 경로
SCHOOLS_JSON = os.path.join(os.path.dirname(DATA_DIR), "app", "static", "json", "schools_data.json")

# [자동 생성할 주제 목록]
# 원하는 주제를 여기에 계속 추가하면 AI가 알아서 글을 씁니다.
# [새로운 TOPICS 목록]
TOPICS = [
    # 1. [취업/비즈니스] 도쿄에서 취업하기 가장 좋은 학교
    {
        "slug": "best-business-schools-tokyo",
        "title": "Top 5 Schools in Tokyo for Finding a Job in Japan",
        "criteria": {
            "category": "school", 
            "tag": "business",  # 비즈니스/취업 태그
            "region": "東京都"   # 도쿄 지역
        },
        "count": 5,
        "thumbnail": "https://images.unsplash.com/photo-1486406146926-c627a92ad1ab?w=500" # 오피스 빌딩 이미지
    },

    # 2. [지역/문화] 교토: 일본의 전통 속에서 공부하기
    {
        "slug": "study-in-kyoto-top-picks",
        "title": "Study in Kyoto: Top 3 Schools in Japan's Cultural Capital",
        "criteria": {
            "category": "school", 
            "region": "京都" # 교토 지역 (주소에 '京都' 포함)
        },
        "count": 3,
        "thumbnail": "https://images.unsplash.com/photo-1493976040374-85c8e12f0c0e?w=500" # 교토 거리 이미지
    },

    # 3. [전공/특기] 애니메이션 & 디자인 유학 추천 (학교/대학 혼합 검색)
    {
        "slug": "best-schools-for-design-arts",
        "title": "Best 4 Schools for Animation, Manga, and Design",
        "criteria": {
            "category": "school", # 혹은 university로 변경 가능
            "tag": "Design"       # 특징에 Design, Art, Manga 등이 포함된 학교
        },
        "count": 4,
        "thumbnail": "https://images.unsplash.com/photo-1613376023733-0a73315d9b06?w=500" # 만화/애니메이션 관련 이미지
    }
]

def load_data_and_build_index():
    """학교 데이터를 로드하고, 링크 생성을 위한 인덱스를 구축함"""
    if not os.path.exists(SCHOOLS_JSON):
        print("❌ schools_data.json not found. Run build_data.py first.")
        return [], []

    with open(SCHOOLS_JSON, 'r', encoding='utf-8') as f:
        data = json.load(f)
        schools = data.get('schools', [])

    # 링크 인덱스 구축 (이름 -> ID/Link)
    link_index = []
    for s in schools:
        name_en = s['basic_info'].get('name_en')
        if name_en and len(name_en) > 3:
            # 괄호 제거 등 정제
            clean_name = re.sub(r'\s*\(.*?\)', '', name_en).strip()
            link_index.append({
                "name": clean_name,
                "link": s['link'], # /school/id
                "id": s['id']
            })
    
    # 긴 이름부터 처리하기 위해 정렬 (부분 일치 방지)
    link_index.sort(key=lambda x: len(x['name']), reverse=True)
    
    return schools, link_index

def filter_schools(schools, criteria, limit):
    """조건에 맞는 학교 필터링"""
    candidates = []
    for s in schools:
        if s.get('category') != criteria['category']: continue
        
        full_text = str(s).lower()
        match = True
        
        if 'region' in criteria and criteria['region'] not in s['basic_info']['address']:
            match = False
        if 'tag' in criteria and criteria['tag'].lower() not in full_text:
            match = False
            
        if match:
            candidates.append(s)
            
    return candidates[:limit]

def generate_article_content(topic, selected_schools):
    """AI를 사용하여 영어 기사 본문 생성"""
    print(f"🤖 AI Writing: {topic['title']}...")
    
    schools_context = ""
    for s in selected_schools:
        name = s['basic_info']['name_en'] or s['basic_info']['name_ja']
        features = ", ".join(s.get('features', []))
        schools_context += f"- {name} (Features: {features})\n"

    prompt = f"""
    You are an expert editor for a 'Study in Japan' portal.
    Write a "Curated Ranking" article titled: "{topic['title']}".
    
    **Instructions:**
    1. Write a compelling introduction about this specific topic (approx 100 words).
    2. Create a numbered list (Ranking) for the selected schools below.
    3. For each school, write a dedicated section explaining WHY it is recommended. Focus on their unique strengths.
    4. **Language:** English Only.
    5. **Tone:** Professional, helpful, and encouraging.
    6. **Format:** Standard Markdown (Use ## for School Names).
    7. Do NOT include links manually. Just write the school names naturally.

    ---
    **Selected Schools:**
    {schools_context}
    ---
    
    Generate ONLY the Markdown body content.
    """
    
    try:
        response = model.generate_content(prompt)
        return clean_json_response(response.text)
    except Exception as e:
        print(f"❌ Error generating {topic['slug']}: {e}")
        return None

def apply_auto_links(content, link_index):
    """생성된 본문에 학교 링크 자동 적용"""
    updated_content = content
    
    for item in link_index:
        name = item['name']
        link = item['link']
        
        # 정규식: 이미 링크된 텍스트([]) 제외하고 순수 텍스트만 타겟팅
        pattern = re.compile(r'(?<!\[)\b' + re.escape(name) + r'\b(?!\])')
        
        if pattern.search(updated_content):
            # 문서당 '첫 번째' 등장만 링크로 변경
            replacement = f"[{name}]({link})"
            updated_content = pattern.sub(replacement, updated_content, count=1)
            
    return updated_content

def main():
    # 1. 데이터 로드 및 인덱스 구축
    schools, link_index = load_data_and_build_index()
    if not schools: return

    print(f"📚 Loaded {len(schools)} schools & built link index.")

    # 2. 주제별 처리 루프
    for topic in TOPICS:
        # 학교 필터링
        selected_schools = filter_schools(schools, topic['criteria'], topic['count'])
        
        if not selected_schools:
            print(f"⚠️ Skipping {topic['title']} (No schools match criteria)")
            continue
            
        # AI 기사 생성
        raw_content = generate_article_content(topic, selected_schools)
        
        if raw_content:
            # [통합] 생성된 글에 바로 링크 적용
            linked_content = apply_auto_links(raw_content, link_index)
            
            # 파일 저장
            filename = f"guide_{topic['slug']}.md"
            filepath = os.path.join(CONTENT_DIR, filename)
            
            frontmatter_data = {
                "layout": "guide",
                "id": topic['slug'],
                "title": topic['title'],
                "category": "Curated List",
                "is_featured": True, # 메인 상단 노출
                "tags": ["Ranking", "Recommendation", topic['criteria'].get('tag', 'General')],
                "description": f"Our curated selection for {topic['title']}.",
                "thumbnail": topic['thumbnail'],
                "date": datetime.now().strftime("%Y-%m-%d")
            }
            
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write("---\n")
                f.write(json.dumps(frontmatter_data, ensure_ascii=False, indent=2))
                f.write("\n---\n\n")
                f.write(linked_content) # 링크가 적용된 본문 저장
                
            print(f"✅ Created & Linked: {filename}")
            
            # API 쿨타임 (안정성)
            time.sleep(2)

if __name__ == "__main__":
    main()
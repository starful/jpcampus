import os
import json
import time
import frontmatter
import google.generativeai as genai
from dotenv import load_dotenv
import re

# ==========================================
# [설정]
# ==========================================
load_dotenv()
CONTENT_DIR = "app/content"
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
model = genai.GenerativeModel('gemini-2.0-flash')

# 🎯 한 번에 처리할 파일 개수
LIMIT = 3

def clean_json(text):
    """
    AI 응답에서 순수 JSON 추출 및 제어 문자 제거 (강력한 버전)
    """
    # 1. 마크다운 코드 블록 제거
    text = text.replace("```json", "").replace("```", "").strip()
    
    # 2. JSON 시작({)과 끝(}) 찾기
    start = text.find("{")
    end = text.rfind("}") + 1
    if start != -1 and end != -1:
        text = text[start:end]
    
    # 3. 제어 문자 제거 (이게 핵심!)
    # 줄바꿈(\n), 탭(\t) 등은 JSON 문자열 안에서 이스케이프 처리되어야 하는데,
    # AI가 실수로 쌩으로 넣는 경우가 있어서 이를 방지합니다.
    # strict=False 옵션을 json.loads에 줘서 해결할 수도 있지만,
    # 여기서는 파이썬 정규식으로 제어 문자를 날려버리는 게 안전합니다.
    
    # (선택 1) 단순하게 제어 문자 제거 (줄바꿈은 살려야 할 수도 있음)
    # text = re.sub(r'[\x00-\x1f\x7f]', '', text) 
    
    # (선택 2 - 추천) json.loads 시 strict=False 사용을 위해 원본 유지하되,
    # 정말 이상한 문자만 제거
    return text

def get_ai_enhancement(school_name, current_data):
    """AI에게 상세 학교 분석 요청"""
    print(f"✍️ [어학원 분석 중...] {school_name}")
    
    prompt = f"""
    당신은 일본 유학 전문 에디터입니다. '{school_name}'에 대해 
    블로그 포스팅 1개 분량(약 3000~3800자)의 매우 상세하고 매력적인 분석글을 작성하세요.
    
    [기초 데이터]
    {json.dumps(current_data, ensure_ascii=False)}

    [작성 규칙 & 스타일]
    1. **가독성 최우선**: 긴 줄글보다는 **Markdown 표(Table)**, 글머리 기호(Bulleted List)를 적극 활용하세요.
    2. **표 필수 포함**: '커리큘럼 구성', '학비 상세 내역', '하루 일과 예시' 등은 반드시 표로 작성하세요.
    3. **톤앤매너**: 전문적이면서도 친절하게 상담하는 듯한 어조.

    [필수 포함 목차 (Markdown 형식)]
    1. **🏫 학교 개요 및 특징**: 설립 배경, 교육 철학, 전반적인 분위기.
    2. **📍 위치 및 주변 환경**: 역세권 여부, 주변 편의시설. (표 활용: '주요 역까지 소요 시간')
    3. **🎓 커리큘럼 및 수업**: 레벨별 수업 구성. (표 활용: '레벨별 도달 목표 및 기간')
    4. **📈 진학 및 취업 지원**: 명문대 진학 실적, 취업 서포트 디테일.
    5. **🏠 기숙사 및 시설**: 기숙사 타입별 월세 비교. (표 활용: '기숙사 타입별 비용 및 시설')
    6. **💰 학비 및 장학금**: (표 활용: '초기 6개월 학비 내역 상세')
    7. **💡 총평 및 추천 대상**: 요약 정리.

    [출력 포맷 - JSON]
    {{
        "english_slug": "school-name-in-english-lowercase",
        "features": ["태그1", "태그2", "태그3", "태그4", "태그5"],
        "description_ko": "## 🏫 학교 개요\\n\\n(여기에 표와 리스트가 포함된 3800자 분량의 상세 본문 작성)...",
        "stats": {{ "international_students": 0, "capacity": 0 }} (모르면 0)
    }}
    """
    
    try:
        response = model.generate_content(prompt)
        cleaned_text = clean_json(response.text)
        
        # [중요] strict=False 옵션 추가!
        # 이렇게 하면 문자열 내부에 줄바꿈 같은 제어 문자가 있어도 너그럽게 파싱합니다.
        return json.loads(cleaned_text, strict=False) 
        
    except Exception as e:
        print(f"❌ AI 오류 ({school_name}): {e}")
        # 오류 발생 시 원본 텍스트를 살짝 출력해보면 디버깅에 도움됨
        # print(f"--- Raw Text ---\n{response.text[:100]}...")
        return None

def main():
    if not os.path.exists(CONTENT_DIR):
        print(f"❌ {CONTENT_DIR} 폴더가 없습니다.")
        return

    # [핵심 로직]
    # 파일명이 '숫자' 또는 '대문자'로 시작하는 파일만 처리 대상
    # 예: 5025.md (O), REDO_jet.md (O), school_jet.md (X - 이미 완료된 것)
    target_files = [f for f in os.listdir(CONTENT_DIR) if re.match(r'^[A-Z0-9].*\.md$', f)]
    
    print(f"📂 수정 대상 파일: 총 {len(target_files)}개 / 이번 실행: {LIMIT}개")

    count = 0
    for filename in target_files:
        if count >= LIMIT:
            print(f"🛑 목표 수량({LIMIT}개) 달성! 종료합니다.")
            break

        filepath = os.path.join(CONTENT_DIR, filename)
        
        try:
            post = frontmatter.load(filepath)
            metadata = post.metadata
            school_name = metadata.get('basic_info', {}).get('name_ja', metadata.get('title'))
            
            # AI 생성 요청
            ai_result = get_ai_enhancement(school_name, metadata)
            
            if not ai_result:
                continue

            # 1. 데이터 병합 (Slug 생성)
            raw_slug = ai_result.get('english_slug', str(metadata['id'])).lower()
            
            # [중요] 'school_' 접두어 강제 추가
            if not raw_slug.startswith("school_"):
                new_slug = f"school_{raw_slug}"
            else:
                new_slug = raw_slug
            
            new_desc = ai_result.get('description_ko', post.content)
            
            # 2. 메타데이터 업데이트
            metadata['id'] = new_slug
            metadata['category'] = 'school' # 확실하게 지정
            metadata['features'] = ai_result.get('features', [])
            metadata['tags'] = metadata['features']
            metadata['thumbnail'] = "/static/img/pin-school.png" # 핀 이미지 지정
            
            if not metadata.get('stats'):
                metadata['stats'] = ai_result.get('stats', {})

            # 3. 새 파일 저장
            new_filename = f"{new_slug}.md"
            new_filepath = os.path.join(CONTENT_DIR, new_filename)
            
            with open(new_filepath, 'w', encoding='utf-8') as f:
                f.write("---\n")
                f.write(json.dumps(metadata, ensure_ascii=False, indent=2))
                f.write("\n---\n\n")
                f.write(new_desc)
            
            print(f"   ✅ 변환 완료: {filename} -> {new_filename}")

            # 4. 기존 파일 삭제 (파일명이 바뀌었을 경우만)
            if filename != new_filename:
                os.remove(filepath)
                # print(f"   🗑️ 원본 삭제: {filename}")
            
            count += 1
            time.sleep(5) # AI 휴식

        except Exception as e:
            print(f"⚠️ 에러 발생 ({filename}): {e}")

if __name__ == "__main__":
    main()
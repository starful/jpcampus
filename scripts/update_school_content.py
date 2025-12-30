import os
import json
import time
import frontmatter
import google.generativeai as genai
from dotenv import load_dotenv
import re
import logging

# ==========================================
# [설정]
# ==========================================
load_dotenv()
CONTENT_DIR = "app/content"
LOG_DIR = "logs"
LIMIT = 10  # 한 번에 처리할 파일 수

# 로깅 설정
if not os.path.exists(LOG_DIR):
    os.makedirs(LOG_DIR)

logging.basicConfig(
    filename=os.path.join(LOG_DIR, "school_update.log"),
    level=logging.INFO,
    format='%(asctime)s - %(message)s',
    encoding='utf-8'
)

genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
model = genai.GenerativeModel('gemini-2.5-pro')

def clean_json(text):
    """
    AI 응답에서 순수 JSON 추출 및 오류 유발 문자 제거
    """
    # 1. 마크다운 코드 블록 제거
    text = text.replace("```json", "").replace("```", "").strip()
    
    # 2. JSON 시작({)과 끝(}) 찾기
    start = text.find("{")
    end = text.rfind("}") + 1
    if start != -1 and end != -1:
        text = text[start:end]
    
    # 3. [추가] JSON 파싱을 방해하는 제어 문자 제거 (줄바꿈 제외)
    # 탭, 백스페이스 등은 제거하되, 줄바꿈(\n)은 마크다운 내용에 필요하므로 유지
    text = re.sub(r'[\x00-\x09\x0b-\x1f\x7f]', '', text)
    
    return text

def get_ai_enhancement(school_name, current_data):
    """AI에게 상세 학교 분석 요청 (영문 버전)"""
    print(f"✍️ Analyzing: {school_name}")
    
    prompt = f"""
    You are an expert editor specializing in Japanese language education.
    Write a detailed review about '{school_name}' in **ENGLISH**.
    
    [Input Data]
    {json.dumps(current_data, ensure_ascii=False)}

    [Output Requirements]
    1. **Strict JSON Format**: Do not include any text outside the JSON object.
    2. **Markdown Content**: Use standard Markdown tables for lists.
    3. **English Slug**: Use kebab-case (e.g., 'tokyo-language-school').
    
    [JSON Structure]
    {{
        "english_slug": "school-name-slug",
        "features": ["Feature1", "Feature2"],
        "description_ko": "## 🏫 School Overview\\n\\n(Content)...",
        "stats": {{ "international_students": 0, "capacity": 0 }}
    }}
    """
    
    try:
        response = model.generate_content(prompt)
        cleaned_text = clean_json(response.text)
        
        # [수정] strict=False 옵션 사용
        return json.loads(cleaned_text, strict=False) 
        
    except json.JSONDecodeError as e:
        print(f"❌ JSON Parse Error ({school_name}): {e}")
        logging.error(f"JSON Parse Error ({school_name}): {e}\nRaw Text: {response.text[:200]}...") # 앞부분만 로그에 남김
        return None
    except Exception as e:
        print(f"❌ AI/Network Error ({school_name}): {e}")
        logging.error(f"AI/Network Error ({school_name}): {e}")
        return None

def main():
    if not os.path.exists(CONTENT_DIR):
        print(f"❌ {CONTENT_DIR} folder not found.")
        return

    # 처리 대상: 숫자나 대문자로 시작하는 파일 (아직 변환 안 된 파일)
    target_files = [f for f in os.listdir(CONTENT_DIR) if re.match(r'^[A-Z0-9].*\.md$', f)]
    
    print(f"📂 Pending files: {len(target_files)}. Limit: {LIMIT}")
    logging.info(f"Start processing. Pending: {len(target_files)}")

    count = 0
    for filename in target_files:
        if count >= LIMIT:
            print(f"🛑 Limit reached ({LIMIT}). Stopping.")
            break

        filepath = os.path.join(CONTENT_DIR, filename)
        
        try:
            post = frontmatter.load(filepath)
            metadata = post.metadata
            school_name = metadata.get('basic_info', {}).get('name_ja', metadata.get('title'))
            
            # AI 생성 요청
            ai_result = get_ai_enhancement(school_name, metadata)
            
            if not ai_result:
                # [추가] 실패 시 잠시 대기 후 계속 진행 (중단되지 않도록)
                time.sleep(2)
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
            metadata['category'] = 'school' 
            metadata['features'] = ai_result.get('features', [])
            metadata['tags'] = metadata['features']
            metadata['thumbnail'] = "/static/img/pin-school.png" 
            
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
            
            print(f"   ✅ Converted: {filename} -> {new_filename}")
            logging.info(f"Success: {filename} -> {new_filename}")

            # 4. 기존 파일 삭제 
            if filename != new_filename:
                os.remove(filepath)
            
            count += 1
            time.sleep(5) # AI 휴식

        except Exception as e:
            print(f"⚠️ Unexpected Error ({filename}): {e}")
            logging.error(f"Unexpected Error {filename}: {e}")

if __name__ == "__main__":
    main()
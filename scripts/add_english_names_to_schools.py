import os
import json
import time
import frontmatter
import google.generativeai as genai
from dotenv import load_dotenv
import re
import logging

# --- 설정 ---
load_dotenv()
CONTENT_DIR = "app/content"
LOG_DIR = "logs"
LIMIT = 100  # 한 번에 처리할 파일 수 (API 호출 속도 조절)

# --- 로깅 설정 ---
if not os.path.exists(LOG_DIR):
    os.makedirs(LOG_DIR)
logging.basicConfig(
    filename=os.path.join(LOG_DIR, "add_en_name.log"),
    level=logging.INFO,
    format='%(asctime)s - %(message)s',
    encoding='utf-8'
)

# --- AI 모델 설정 ---
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
model = genai.GenerativeModel('gemini-2.0-flash')


def get_english_name_from_ai(school_name_ja, website_url=None):
    """
    AI를 통해 학교의 공식 영어 이름을 찾아오는 함수
    """
    print(f"🔎 Finding English name for: {school_name_ja}")
    
    prompt = f"""
    What is the official English name for the Japanese language school "{school_name_ja}"?
    If an official English name exists (often found on their website), please provide it.
    If not, provide a proper and natural-sounding English translation of the name.
    
    The website URL is: {website_url if website_url else "Not provided."}

    Respond in JSON format with a single key "name_en".
    Example: {{"name_en": "Shinjuku Gyoen Gakuin Japanese Language School"}}
    """
    
    try:
        response = model.generate_content(prompt)
        # 응답에서 JSON 부분만 추출
        json_text = response.text.replace("```json", "").replace("```", "").strip()
        result = json.loads(json_text)
        return result.get("name_en")
    except Exception as e:
        print(f"❌ AI Error ({school_name_ja}): {e}")
        logging.error(f"AI Error ({school_name_ja}): {e}")
        return None

def main():
    if not os.path.exists(CONTENT_DIR):
        print(f"❌ Directory not found: {CONTENT_DIR}")
        return

    # 'school_'로 시작하는 파일만 대상으로 함
    target_files = [f for f in os.listdir(CONTENT_DIR) if f.startswith('school_') and f.endswith('.md')]
    
    print(f"📂 Found {len(target_files)} school files to process. Batch limit: {LIMIT}")
    logging.info(f"Start adding English names. Total files: {len(target_files)}")

    count = 0
    for filename in target_files:
        if count >= LIMIT:
            print(f"🛑 Batch limit of {LIMIT} reached. Stopping for now.")
            break

        filepath = os.path.join(CONTENT_DIR, filename)
        
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                post = frontmatter.load(f)
            
            metadata = post.metadata
            basic_info = metadata.get("basic_info", {})

            # 이미 'name_en' 필드가 있고 비어있지 않으면 건너뛰기
            if basic_info.get("name_en"):
                print(f"⏭️ Skipping (already has name_en): {filename}")
                continue
            
            school_name_ja = basic_info.get("name_ja")
            if not school_name_ja:
                print(f"⚠️ Skipping (no name_ja): {filename}")
                continue

            website_url = metadata.get("source_url") # 웹사이트 URL 정보 활용
            
            # AI에게 영어 이름 요청
            english_name = get_english_name_from_ai(school_name_ja, website_url)
            
            if not english_name:
                time.sleep(2)
                continue

            # 메타데이터에 'name_en' 추가 또는 업데이트
            basic_info["name_en"] = english_name
            metadata["basic_info"] = basic_info
            
            # 파일 덮어쓰기
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(frontmatter.dumps(post))
            
            print(f"   ✅ Added English name to: {filename}")
            logging.info(f"Success (Added name_en): {filename}")
            
            count += 1
            time.sleep(2) # API 속도 제한 방지

        except Exception as e:
            print(f"⚠️ Unexpected Error on file {filename}: {e}")
            logging.error(f"Unexpected Error on {filename}: {e}")

if __name__ == "__main__":
    main()
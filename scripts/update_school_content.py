import os
import json
import time
import frontmatter
import google.generativeai as genai
from dotenv import load_dotenv
import re
import logging

load_dotenv()
CONTENT_DIR = "app/content"
LOG_DIR = "logs"
LIMIT = 10

if not os.path.exists(LOG_DIR): os.makedirs(LOG_DIR)
logging.basicConfig(filename=os.path.join(LOG_DIR, "school_update.log"), level=logging.INFO, format='%(asctime)s - %(message)s', encoding='utf-8')

genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
model = genai.GenerativeModel('gemini-2.0-flash')

def clean_json(text):
    text = text.replace("```json", "").replace("```", "").strip()
    start = text.find("{")
    end = text.rfind("}") + 1
    if start != -1 and end != -1: text = text[start:end]
    text = re.sub(r'[\x00-\x09\x0b-\x1f\x7f]', '', text)
    return text

def get_ai_enhancement(school_name, current_data):
    print(f"✍️ Analyzing (Deep): {school_name}")
    
    # [수정됨] 프롬프트에 'name_en' 요구사항 추가
    prompt = f"""
    You are an expert consultant for international students studying in Japan.
    Analyze the Japanese language school '{school_name}' based on the provided data and write an in-depth, comprehensive guide in ENGLISH.
    The output must be in a single JSON format.

    **The markdown content for 'description_ko' must be between 7000 and 8000 characters.**

    ---
    ### REQUIRED JSON STRUCTURE ###
    {{
        "english_slug": "A URL-friendly slug based on the English name.",
        "name_en": "The official English name of the school. If none exists, provide a proper English translation.",
        "features": ["An array of key features as strings."],
        "description_ko": "## 🏫 School Overview & Philosophy\\n- Write 3-4 detailed paragraphs...\\n\\n## 📚 Courses, Curriculum & Teaching Style\\n- Create a Markdown table...\\n\\n## 🌍 Student Body & Campus Life\\n- Analyze nationality mix...\\n\\n## 🎓 University & Career Pathways\\n- Detail support systems...\\n\\n## 🏡 Accommodation & Living Support\\n- Describe dormitory options...\\n\\n## 💰 Tuition, Fees & Scholarships\\n- Create a detailed cost table...",
        "stats": {{ "international_students": 123, "capacity": 456 }}
    }}

    ---
    [Input Data to Analyze]
    {json.dumps(current_data, ensure_ascii=False)}
    """
    
    try:
        response = model.generate_content(prompt)
        cleaned_text = clean_json(response.text)
        return json.loads(cleaned_text, strict=False) 
    except Exception as e:
        print(f"❌ AI/Network Error ({school_name}): {e}")
        logging.error(f"AI/Network Error ({school_name}): {e}")
        return None

def main():
    if not os.path.exists(CONTENT_DIR):
        print(f"❌ {CONTENT_DIR} folder not found.")
        return

    # ID 형식 파일(B275.md 등)을 대상으로 함
    target_files = [f for f in os.listdir(CONTENT_DIR) if re.match(r'^[A-Z0-9].*\.md$', f)]
    
    print(f"📂 Pending files for conversion: {len(target_files)}. Batch limit: {LIMIT}")
    logging.info(f"Start processing new files. Pending: {len(target_files)}")

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
            
            ai_result = get_ai_enhancement(school_name, metadata)
            if not ai_result:
                time.sleep(2)
                continue

            raw_slug = ai_result.get('english_slug', str(metadata['id'])).lower()
            new_slug = f"school_{raw_slug}" if not raw_slug.startswith("school_") else raw_slug
            new_desc = ai_result.get('description_ko', post.content)
            
            # 메타데이터 업데이트
            metadata['id'] = new_slug
            metadata['category'] = 'school' 
            metadata['features'] = ai_result.get('features', [])
            metadata['tags'] = metadata['features']
            metadata['thumbnail'] = "/static/img/pin-school.png" 
            
            # [수정] basic_info에 name_en 추가
            if 'basic_info' not in metadata:
                metadata['basic_info'] = {}
            metadata['basic_info']['name_en'] = ai_result.get('name_en')
            
            if not metadata.get('stats'):
                metadata['stats'] = ai_result.get('stats', {})

            # 새 파일 저장
            new_filename = f"{new_slug}.md"
            new_filepath = os.path.join(CONTENT_DIR, new_filename)
            
            with open(new_filepath, 'w', encoding='utf-8') as f:
                f.write("---\n")
                f.write(json.dumps(metadata, ensure_ascii=False, indent=2))
                f.write("\n---\n\n")
                f.write(new_desc)
            
            print(f"   ✅ Converted: {filename} -> {new_filename}")
            logging.info(f"Success: {filename} -> {new_filename}")

            if filename != new_filename:
                os.remove(filepath)
            
            count += 1
            time.sleep(5)

        except Exception as e:
            print(f"⚠️ Unexpected Error ({filename}): {e}")
            logging.error(f"Unexpected Error {filename}: {e}")

if __name__ == "__main__":
    main()
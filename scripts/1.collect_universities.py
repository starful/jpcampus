import csv
import json
import os
import time
import requests
from tqdm import tqdm
from concurrent.futures import ThreadPoolExecutor, as_completed
from google.generativeai.types import GenerationConfig
from common import setup_logging, setup_gemini, clean_json_response, DATA_DIR, CONTENT_DIR, LOG_DIR

# --- 설정 ---
setup_logging("univ_gen.log")
model = setup_gemini()

LIMIT = 20
MAX_WORKERS = 5  # 동시에 처리할 개수 (Gemini 유료 계정은 10~20, 무료는 2~5 권장)
INPUT_CSV = os.path.join(DATA_DIR, "univ_list_100.csv")
OUTPUT_DIR = CONTENT_DIR
HISTORY_FILE = os.path.join(LOG_DIR, "univ_processed_history.txt")
GOOGLE_MAPS_API_KEY = os.getenv("GOOGLE_MAPS_API_KEY")

if not os.path.exists(OUTPUT_DIR): os.makedirs(OUTPUT_DIR)

def load_history():
    if not os.path.exists(HISTORY_FILE): return set()
    with open(HISTORY_FILE, "r", encoding="utf-8") as f:
        return set(line.strip() for line in f)

def append_history(name):
    with open(HISTORY_FILE, "a", encoding="utf-8") as f:
        f.write(f"{name}\n")

def get_google_coordinates(address):
    if not address: return {"lat": 35.6812, "lng": 139.7671}
    base_url = "https://maps.googleapis.com/maps/api/geocode/json"
    params = {"address": address, "key": GOOGLE_MAPS_API_KEY, "language": "en"}
    try:
        res = requests.get(base_url, params=params, timeout=5) # 타임아웃 설정
        data = res.json()
        if data['status'] == 'OK':
            loc = data['results'][0]['geometry']['location']
            return {"lat": loc['lat'], "lng": loc['lng']}
    except: pass
    return {"lat": 35.6812, "lng": 139.7671}

def get_university_info(name_ja, name_en):
    # 멀티스레딩 시 출력이 섞이지 않도록 간단하게 출력
    prompt = f"""
    You are an expert consultant for international students planning to study in Japan.
    Analyze the university "{name_ja}" ({name_en}) and write an in-depth, comprehensive guide in **ENGLISH**.
    
    The output must be in Markdown format, follow the structure below precisely, and be **between 7000 and 8000 characters**.
    
    Required JSON Structure:
    {{
        "english_slug": "url-friendly-slug-in-english",
        "basic_info": {{
            "name_ja": "{name_ja}",
            "name_en": "{name_en}",
            "address": "Official address in English",
            "capacity": null
        }},
        "stats": {{
            "international_students": 123,
            "acceptance_rate": "Estimated % string"
        }},
        "tuition": {{
            "admission_fee": 123456,
            "yearly_tuition": 123456
        }},
        "faculties": ["List", "of", "faculties"],
        "features": ["Key Feature 1", "Key Feature 2"],
        "description": "## 🏫 University Overview\\n...long text..."
    }}
    """
    for i in range(3):
        try:
            res = model.generate_content(
                prompt, generation_config=GenerationConfig(response_mime_type="application/json")
            )
            return json.loads(clean_json_response(res.text))
        except Exception as e:
            # 429 Error (Rate Limit) 발생 시 대기 후 재시도
            if "429" in str(e):
                time.sleep(10 * (i + 1))
            else:
                time.sleep(2)
    return None

def process_university(univ):
    """한 대학교를 처리하는 독립적인 작업 단위"""
    name_ja = univ['name_ja']
    name_en = univ['name_en']
    
    data = get_university_info(name_ja, name_en)
    if not data:
        return f"❌ Failed: {name_ja}"

    addr = data['basic_info'].get('address')
    coords = get_google_coordinates(addr)
    
    raw_slug = data.get('english_slug', name_en.replace(" ", "-").lower())
    slug = f"univ_{raw_slug}" if not raw_slug.startswith("univ_") else raw_slug
    
    frontmatter_data = {
        "layout": "school", 
        "id": slug, 
        "title": data['basic_info']['name_en'],
        "category": "university",
        "tags": data.get('features', []), 
        "thumbnail": "/static/img/pin-univ.png", 
        "location": coords,
        "basic_info": data['basic_info'], 
        "stats": data['stats'], 
        "tuition": data['tuition'],
        "faculties": data.get('faculties', []), 
        "features": data.get('features', [])
    }

    filepath = os.path.join(OUTPUT_DIR, f"{slug}.md")
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write("---\n")
        f.write(json.dumps(frontmatter_data, ensure_ascii=False, indent=2))
        f.write("\n---\n\n")
        f.write(data.get('description', 'No content available.'))
    
    append_history(name_ja)
    return f"✅ Saved: {slug}.md"

def main():
    if not os.path.exists(INPUT_CSV):
        print(f"❌ {INPUT_CSV} file not found.")
        return

    processed_list = load_history()
    univ_list = []
    with open(INPUT_CSV, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row['name_ja'] not in processed_list:
                univ_list.append(row)
            
    univ_list = univ_list[:LIMIT] # 처리할 개수 제한
    print(f"🚀 Total Universities to process: {len(univ_list)} | Workers: {MAX_WORKERS}")

    # --- 멀티스레딩 처리 부분 ---
    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        # 작업 등록
        future_to_univ = {executor.submit(process_university, univ): univ for univ in univ_list}
        
        # tqdm으로 진행률 표시
        for future in tqdm(as_completed(future_to_univ), total=len(univ_list)):
            univ = future_to_univ[future]
            try:
                result = future.result()
                # print(result) # 필요시 결과 출력
            except Exception as e:
                print(f"⚠️ {univ['name_ja']} generated an exception: {e}")

if __name__ == "__main__":
    main()
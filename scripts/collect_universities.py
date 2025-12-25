import csv
import json
import os
import time
import requests
from tqdm import tqdm
from dotenv import load_dotenv
import google.generativeai as genai

# ==========================================
# [설정]
# ==========================================
load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
GOOGLE_MAPS_API_KEY = os.getenv("GOOGLE_MAPS_API_KEY")

# 🎯 생성할 대학 개수 설정 (0이면 제한 없음)
LIMIT = 10

# 경로 설정
INPUT_CSV = "scripts/file/univ_list_100.csv"
OUTPUT_DIR = "app/content"
LOG_DIR = "logs"
HISTORY_FILE = os.path.join(LOG_DIR, "univ_processed_history.txt")

if not os.path.exists(OUTPUT_DIR):
    os.makedirs(OUTPUT_DIR)
if not os.path.exists(LOG_DIR):
    os.makedirs(LOG_DIR)

genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel('gemini-2.0-flash')

# ==========================================
# [함수 정의]
# ==========================================

def load_history():
    """처리된 학교 목록 로드"""
    if not os.path.exists(HISTORY_FILE):
        return set()
    with open(HISTORY_FILE, "r", encoding="utf-8") as f:
        return set(line.strip() for line in f)

def append_history(name):
    """처리된 학교 기록 추가"""
    with open(HISTORY_FILE, "a", encoding="utf-8") as f:
        f.write(f"{name}\n")

def get_google_coordinates(address):
    """구글 맵스 API로 좌표 추출"""
    if not address: return {"lat": 35.6812, "lng": 139.7671} # 기본값 (도쿄역)
    
    base_url = "https://maps.googleapis.com/maps/api/geocode/json"
    params = {"address": address, "key": GOOGLE_MAPS_API_KEY, "language": "ja"}
    try:
        res = requests.get(base_url, params=params)
        data = res.json()
        if data['status'] == 'OK':
            loc = data['results'][0]['geometry']['location']
            return {"lat": loc['lat'], "lng": loc['lng']}
    except: pass
    return {"lat": 35.6812, "lng": 139.7671}

def clean_json(text):
    """AI 응답에서 순수 JSON 추출"""
    text = text.replace("```json", "").replace("```", "").strip()
    start = text.find("{")
    end = text.rfind("}") + 1
    if start != -1 and end != -1:
        return text[start:end]
    return text

def get_university_info(name_ja, name_en):
    """AI에게 대학 상세 정보 요청 (영문 버전)"""
    print(f"🏫 AI Analysis - English: {name_ja}")
    
    prompt = f"""
    You are an expert in Japanese higher education.
    Analyze the university "{name_ja}" ({name_en}) and provide data for a Markdown file in **ENGLISH**.

    [Formatting Rules - IMPORTANT]
    1. **Strict Markdown Tables**: 
       - Ensure a blank line before and after the table.
       - Use `| Header | Header |` format.
       - Separator line MUST be `|---|---|`.
       - Do NOT merge cells or use complex structures.

    [Requirements]
    1. **english_slug**: URL-friendly English name (lowercase, kebab-case). e.g., "waseda-university"
    2. **description_ko**: Write a detailed introduction in **ENGLISH** (Markdown format, 2000+ characters).
       - **MUST use Markdown Tables**: Use tables for 'Faculties list', 'Tuition breakdown', 'Admission stats', etc.
       - Structure:
         - 🏫 University Overview (History, Reputation)
         - 🎓 Faculties & Departments (Use Table)
         - 💰 Tuition & Fees (Use Table: Admission fee, Yearly tuition in JPY)
         - 🌍 International Student Support (Dormitory, English programs, Career support)
         - 📍 Campus Location & Access (Use Table for access)
    3. **tuition**: Integer values only (JPY).
    
    [Output Format - JSON Only]
    {{
        "english_slug": "university-name-slug",
        "basic_info": {{
            "name_ja": "{name_ja}",
            "name_en": "{name_en}",
            "address": "Official Japanese Address",
            "website": "Official URL"
        }},
        "stats": {{
            "international_students": "Number (integer)",
            "acceptance_rate": "Rate (string)" 
        }},
        "tuition": {{
            "admission_fee": 200000,
            "yearly_tuition": 1000000
        }},
        "faculties": ["School of Political Science", "School of Law", ...],
        "features": ["SGU", "EJU Required", "English Program", "Dormitory", "Scholarship"],
        "description_ko": "## 🏫 University Overview\\n\\n(Detailed ENGLISH content with Tables)..."
    }}
    """

    for i in range(3):
        try:
            res = model.generate_content(prompt)
            return json.loads(clean_json(res.text))
        except Exception as e:
            print(f"   ⚠️ Retry ({i+1}/3)... {e}")
            time.sleep(5)
    return None

def save_to_md(data):
    """MD 파일로 저장"""
    # 1. 좌표 구하기
    addr = data['basic_info'].get('address')
    coords = get_google_coordinates(addr)
    
    # 2. 파일명 결정 (univ_ 접두어 강제)
    raw_slug = data.get('english_slug', data['basic_info']['name_en'].replace(" ", "-").lower())
    if not raw_slug.startswith("univ_"):
        slug = f"univ_{raw_slug}"
    else:
        slug = raw_slug
        
    filename = f"{slug}.md"
    filepath = os.path.join(OUTPUT_DIR, filename)

    # 3. Frontmatter 데이터 구성
    frontmatter = {
        "layout": "school",
        "id": slug,
        "title": data['basic_info']['name_ja'],
        "category": "university", # [중요] 대학 구분자
        "tags": data.get('features', []),
        "thumbnail": "/static/img/pin-univ.png",
        "location": coords,
        "basic_info": data['basic_info'],
        "stats": data['stats'],
        "tuition": data['tuition'],
        "faculties": data.get('faculties', []),
        "features": data.get('features', [])
    }

    # 4. 본문 분리
    description = data.get('description_ko', 'No content available.')

    # 5. 파일 쓰기
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write("---\n")
        f.write(json.dumps(frontmatter, ensure_ascii=False, indent=2))
        f.write("\n---\n\n")
        f.write(description)
    
    return filename

# ==========================================
# [메인 실행]
# ==========================================
def main():
    if not os.path.exists(INPUT_CSV):
        print(f"❌ {INPUT_CSV} file not found.")
        return

    # 처리된 목록 로드
    processed_list = load_history()
    
    # CSV 읽기 및 필터링
    univ_list = []
    with open(INPUT_CSV, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row['name_ja'] not in processed_list:
                univ_list.append(row)
            
    print(f"🚀 Total Universities: {len(univ_list)} (Already processed: {len(processed_list)})")
    print(f"🎯 Target for this run: {LIMIT}")

    count = 0
    for univ in tqdm(univ_list):
        if LIMIT > 0 and count >= LIMIT:
            print(f"🛑 Limit reached ({LIMIT}). Stopping.")
            break
            
        data = get_university_info(univ['name_ja'], univ['name_en'])
        
        if data:
            filename = save_to_md(data)
            append_history(univ['name_ja']) # 성공 시 기록
            print(f"   ✅ Saved: {filename}")
            count += 1
            time.sleep(3) # API 제한 방지
        else:
            print(f"   ❌ Failed: {univ['name_ja']}")

if __name__ == "__main__":
    main()
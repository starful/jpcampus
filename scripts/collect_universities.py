import csv
import json
import os
import time
import requests
from tqdm import tqdm
from dotenv import load_dotenv
import google.generativeai as genai
from google.api_core.exceptions import ResourceExhausted

# ==========================================
# [설정]
# ==========================================
load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
GOOGLE_MAPS_API_KEY = os.getenv("GOOGLE_MAPS_API_KEY")

if not GEMINI_API_KEY or not GOOGLE_MAPS_API_KEY:
    print("❌ 오류: .env 파일에 API 키가 없습니다.")
    exit()

genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel('gemini-2.0-flash')

INPUT_CSV = "file/univ_list_100.csv"
OUTPUT_JSON = "file/universities.json"

# ==========================================
# [함수 정의]
# ==========================================

def get_google_coordinates(address):
    if not address: return None
    base_url = "https://maps.googleapis.com/maps/api/geocode/json"
    params = {"address": address, "key": GOOGLE_MAPS_API_KEY, "language": "ja"}
    try:
        res = requests.get(base_url, params=params)
        data = res.json()
        if data['status'] == 'OK':
            loc = data['results'][0]['geometry']['location']
            return {"lat": loc['lat'], "lng": loc['lng']}
    except: pass
    return None

def clean_json(text):
    text = text.replace("```json", "").replace("```", "").strip()
    if "{" in text:
        text = text[text.find("{"):text.rfind("}")+1]
    return text

def get_university_info(name_ja, name_en):
    prompt = f"""
    You are an expert in Japanese higher education.
    Extract detailed information about the university "{name_ja}" ({name_en}) for international students.
    
    Output Format: ONLY valid JSON string. No markdown.

    [JSON Structure]
    {{
        "id": "Unique ID based on English name (e.g., U_WASEDA)",
        "category": "university",
        "basic_info": {{
            "name_ja": "{name_ja}",
            "name_en": "{name_en}",
            "address": "Main Campus Address in Japanese",
            "website": "Official Website URL"
        }},
        "stats": {{
            "international_students": "Approx number of intl students (integer, e.g., 5000)",
            "acceptance_rate": "Approx acceptance rate for intl students (string, e.g., '30%')" 
        }},
        "faculties": ["Faculty A", "Faculty B", "Faculty C" (List up to 7 major faculties)],
        "tuition": {{
            "admission_fee": "Entrance fee in JPY (integer)",
            "yearly_tuition": "First year tuition in JPY (integer)"
        }},
        "features": ["Feature1", "Feature2", "Feature3" (e.g., 'SGU', 'EJU Required', 'English Course', 'Dormitory')],
        "description_ko": "Write a 3-sentence summary in Korean explaining why this university is good for international students. Mention its reputation, location, or unique strengths."
    }}
    """

    for i in range(3):
        try:
            res = model.generate_content(prompt)
            if not res.text: return None
            return json.loads(clean_json(res.text))
        except ResourceExhausted:
            print("   ⏳ API 한도 초과! 대기 중...")
            time.sleep(10)
        except Exception as e:
            print(f"   ⚠️ AI 파싱 에러 ({name_ja}): {e}")
            return None
    return None

def load_existing_data():
    if os.path.exists(OUTPUT_JSON):
        try:
            with open(OUTPUT_JSON, 'r', encoding='utf-8') as f:
                return json.load(f)
        except: return []
    return []

# ==========================================
# [메인 실행]
# ==========================================
def main():
    if not os.path.exists(INPUT_CSV):
        print(f"❌ {INPUT_CSV} 파일이 없습니다. 1단계 스크립트를 먼저 실행하세요.")
        return

    # 1. 기존 데이터 로드 (이어하기용)
    collected_data = load_existing_data()
    existing_names = {u['basic_info']['name_ja'] for u in collected_data}
    print(f"📂 기존 데이터: {len(collected_data)}개 로드됨")

    # 2. CSV 읽기
    univ_list = []
    with open(INPUT_CSV, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row['name_ja'] not in existing_names:
                univ_list.append(row)
            
    print(f"🚀 남은 {len(univ_list)}개 중 10개만 우선 수집합니다...")

    # 3. 수집 시작 (10개 제한)
    count = 0
    limit = 10  # [수정] 10개만 하고 멈춤

    for univ in tqdm(univ_list):
        if count >= limit:
            print("\n🛑 테스트용 10개 수집 완료! 종료합니다.")
            break

        data = get_university_info(univ['name_ja'], univ['name_en'])
        
        if data:
            # 좌표 변환
            addr = data['basic_info'].get('address')
            if addr:
                coords = get_google_coordinates(addr)
                if coords:
                    data['location'] = coords
                else:
                    data['location'] = {"lat": 35.6812, "lng": 139.7671} # 도쿄역 기본값
            
            collected_data.append(data)
            
            # [중요] 하나 할 때마다 저장 (중간에 꺼도 안전)
            with open(OUTPUT_JSON, 'w', encoding='utf-8') as f:
                json.dump(collected_data, f, ensure_ascii=False, indent=2)
            
            count += 1
            time.sleep(2)
        else:
            print(f"   ❌ 실패: {univ['name_ja']}")

    print(f"\n🎉 현재까지 총 {len(collected_data)}개 대학 정보가 저장되었습니다.")

if __name__ == "__main__":
    main()
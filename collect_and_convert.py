import requests
from bs4 import BeautifulSoup
import json
import time
import random
import re
import os
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

MODEL_NAME = 'models/gemini-2.0-flash'
try:
    model = genai.GenerativeModel(MODEL_NAME)
    print(f"🤖 사용 모델: {MODEL_NAME}")
except:
    print("⚠️ 모델 설정 실패, 기본 모델 시도")
    model = genai.GenerativeModel('gemini-pro')

OUTPUT_JSON = "file/schools_complete_db.json"

# [수정됨] 도쿄 + 치바 URL 리스트
TARGET_AREAS = [
    # 도쿄
    "https://www.nisshinkyo.org/search/area.php?lng=1&area=%E6%9D%B1%E4%BA%AC%E9%83%BD",
    # 치바
    "https://www.nisshinkyo.org/search/area.php?lng=1&area=%E5%8D%83%E8%91%89"
]

HEADERS = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}

# ==========================================
# [1] Google Geocoding (좌표 변환)
# ==========================================
def get_google_coordinates(address):
    base_url = "https://maps.googleapis.com/maps/api/geocode/json"
    
    # 우편번호 및 공백 제거, 건물명 분리
    clean_address = re.sub(r'〒?\s*\d{3}-\d{4}', '', address).strip()
    if ' ' in clean_address:
        clean_address = clean_address.split(' ')[0]
    
    # [중요] 여기에 '東京都' 강제 추가 로직 없음 (치바현 주소 대응)
    
    params = {"address": clean_address, "key": GOOGLE_MAPS_API_KEY, "language": "ja"}
    
    try:
        res = requests.get(base_url, params=params)
        data = res.json()
        if data['status'] == 'OK':
            loc = data['results'][0]['geometry']['location']
            return {"lat": loc['lat'], "lng": loc['lng']}
    except:
        pass
    # 실패 시 기본값 (도쿄 시청)
    return {"lat": 35.6895, "lng": 139.6917}

# ==========================================
# [2] 크롤링 & AI 변환
# ==========================================
def clean_json(text):
    text = re.sub(r'```json\s*', '', text)
    text = re.sub(r'```\s*', '', text)
    return text.strip()

def extract_info_ai(school_name, text):
    prompt = f"""
    Extract data to JSON.
    [Rules]
    1. Numbers: Remove commas, convert to Integer.
    2. Missing: Use 0 or null.
    3. Output: ONLY valid JSON string.

    [Schema]
    {{
        "id": "unique_id_english_or_number",
        "basic_info": {{ "name_ja": "School Name", "address": "Address", "capacity": "Capacity(int)" }},
        "student_demographics": {{ "total": "Total(int)", "korea": "Korea(int)", "china": "China(int)", "vietnam": "Vietnam(int)", "nepal": "Nepal(int)", "usa": "USA(int)" }},
        "courses": [ {{ "course_name": "Name", "admission_month": "Month", "total_fees": "1st Year Fee(int)" }} ],
        "career_path": {{ "grad_school": "Grad(int)", "university": "Univ(int)", "vocational": "Vocational(int)" }},
        "features": ["Feature1", "Feature2"]
    }}
    [Text] {school_name} \n {text[:15000]}
    """
    
    max_retries = 3
    for i in range(max_retries):
        try:
            res = model.generate_content(prompt)
            return json.loads(clean_json(res.text))
        except ResourceExhausted:
            wait_time = (i + 1) * 10
            print(f"   ⏳ API 한도 초과! {wait_time}초 대기...")
            time.sleep(wait_time)
        except Exception as e:
            print(f"   ⚠️ 변환 에러: {e}")
            return None
    return None

def get_school_links(target_url):
    try:
        res = requests.get(target_url, headers=HEADERS)
        res.encoding = 'utf-8'
        soup = BeautifulSoup(res.text, 'html.parser')
        links = soup.select('a[href*="college.php"]')
        return [{"name": l.get_text(strip=True), "url": f"https://www.nisshinkyo.org/search/{l['href']}"} for l in links]
    except Exception as e:
        print(f"링크 수집 실패 ({target_url}): {e}")
        return []

def get_page_text(url):
    try:
        time.sleep(random.uniform(0.5, 1.0))
        res = requests.get(url, headers=HEADERS)
        res.encoding = res.apparent_encoding
        if res.status_code != 200: return None
        soup = BeautifulSoup(res.text, 'html.parser')
        for s in soup(["script", "style"]): s.extract()
        return soup.get_text("\n", strip=True)
    except:
        return None

# ==========================================
# [3] 메인 실행
# ==========================================
def main():
    if not os.path.exists("file"): os.makedirs("file")
    
    all_schools_meta = []
    
    print("🔍 각 지역별 학교 리스트 수집 중...")
    for area_url in TARGET_AREAS:
        links = get_school_links(area_url)
        print(f"   ㄴ 발견: {len(links)}개 학교")
        all_schools_meta.extend(links)
    
    # 중복 제거 (URL 기준)
    seen_urls = set()
    unique_schools = []
    for s in all_schools_meta:
        if s['url'] not in seen_urls:
            unique_schools.append(s)
            seen_urls.add(s['url'])

    final_data = []
    print(f"🚀 총 {len(unique_schools)}개 학교 상세 정보 처리 시작...")

    for school in tqdm(unique_schools):
        raw_text = get_page_text(school['url'])
        if not raw_text: continue

        data = extract_info_ai(school['name'], raw_text)
        if data:
            data['source_url'] = school['url']
            addr = data['basic_info'].get('address', '')
            if addr:
                data['location'] = get_google_coordinates(addr)
            final_data.append(data)
            time.sleep(2) # API 속도 조절

    with open(OUTPUT_JSON, 'w', encoding='utf-8') as f:
        json.dump(final_data, f, ensure_ascii=False, indent=2)
    
    print(f"\n🎉 완료! {len(final_data)}개 저장됨: {OUTPUT_JSON}")

if __name__ == "__main__":
    main()
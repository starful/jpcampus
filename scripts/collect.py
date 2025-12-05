import requests
from bs4 import BeautifulSoup
import json
import time
import random
import re
import os
import datetime
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

MODEL_NAME = 'gemini-2.0-flash'
try:
    model = genai.GenerativeModel(MODEL_NAME)
    print(f"🤖 사용 모델: {MODEL_NAME}")
except:
    print("⚠️ 모델 설정 실패, 기본 모델 시도")
    model = genai.GenerativeModel('gemini-pro')

OUTPUT_JSON = "file/schools_complete_db.json"

TARGET_AREAS = [
    "https://www.nisshinkyo.org/search/area.php?lng=1&area=%E5%9F%BC%E7%8E%89",         # 사이타마
    "https://www.nisshinkyo.org/search/area.php?lng=1&area=%E5%8D%83%E8%91%89",         # 치바
    "https://www.nisshinkyo.org/search/area.php?lng=1&area=%E6%9D%B1%E4%BA%AC%E9%83%BD", # 도쿄
    "https://www.nisshinkyo.org/search/area.php?lng=1&area=%E7%A5%9E%E5%A5%88%E5%B7%9D", # 가나가와
    "https://www.nisshinkyo.org/search/area.php?lng=1&area=%E4%BA%AC%E9%83%BD",         # 교토
    "https://www.nisshinkyo.org/search/area.php?lng=1&area=%E5%A4%A7%E9%98%AA",         # 오사카
    "https://www.nisshinkyo.org/search/area.php?lng=1&area=%E5%85%B5%E5%BA%AB",         # 효고
    "https://www.nisshinkyo.org/search/area.php?lng=1&area=%E7%A6%8F%E5%B2%A1",         # 후쿠오카
    "https://www.nisshinkyo.org/search/area.php?lng=1&area=%E5%8C%97%E6%B5%B7%E9%81%93", # 홋카이도
    "https://www.nisshinkyo.org/search/area.php?lng=1&area=%E6%84%9B%E7%9F%A5"          # 아이치
]

HEADERS = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}

# ==========================================
# [1] Google Geocoding (fix_coords 기능 통합)
# ==========================================
def clean_address_string(address):
    """주소 전처리: 우편번호 제거, 공백 뒤 건물명 제거"""
    if not address: return ""
    # 우편번호 제거 (〒123-4567, 123-4567 등)
    address = re.sub(r'〒?\s*\d{3}-\d{4}', '', address)
    # 앞뒤 공백 제거
    address = address.strip()
    # 공백이 있다면 앞부분(번지수)만 가져오기 (건물명 제거)
    if ' ' in address:
        address = address.split(' ')[0]
    return address

def get_google_coordinates(address):
    base_url = "https://maps.googleapis.com/maps/api/geocode/json"
    clean_address = clean_address_string(address)
    
    if not clean_address:
        return None

    params = {"address": clean_address, "key": GOOGLE_MAPS_API_KEY, "language": "ja"}
    
    try:
        res = requests.get(base_url, params=params)
        data = res.json()
        if data['status'] == 'OK':
            loc = data['results'][0]['geometry']['location']
            return {"lat": loc['lat'], "lng": loc['lng']}
        else:
            print(f"   ⚠️ 좌표 변환 실패 [{data['status']}]: {clean_address}")
    except Exception as e:
        print(f"   ⚠️ API 요청 에러: {e}")
    
    return None

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

def load_existing_db():
    """기존 DB 파일 로드"""
    if os.path.exists(OUTPUT_JSON):
        try:
            with open(OUTPUT_JSON, 'r', encoding='utf-8') as f:
                data = json.load(f)
                # 신규 포맷(dict) vs 구버전 포맷(list) 처리
                if isinstance(data, dict) and "schools" in data:
                    return data["schools"]
                elif isinstance(data, list):
                    return data
        except Exception as e:
            print(f"⚠️ 기존 DB 로드 실패: {e}")
    return []

# ==========================================
# [3] 메인 실행
# ==========================================
def main():
    if not os.path.exists("file"): os.makedirs("file")
    
    # 1. 기존 데이터 로드
    existing_data = load_existing_db()
    existing_urls = {s.get('source_url') for s in existing_data if s.get('source_url')}
    print(f"📂 기존 데이터: {len(existing_data)}개 로드됨")

    # 2. 크롤링 할 URL 수집
    all_links = []
    print("🔍 각 지역별 학교 리스트 수집 중...")
    for area_url in TARGET_AREAS:
        links = get_school_links(area_url)
        all_links.extend(links)
    
    # 3. 신규 학교 필터링 (중복 제거 및 기존 DB에 없는 것만)
    seen_urls_in_crawl = set()
    new_targets = []
    
    for s in all_links:
        url = s['url']
        if url not in seen_urls_in_crawl and url not in existing_urls:
            new_targets.append(s)
            seen_urls_in_crawl.add(url)
    
    print(f"📊 검색된 전체 학교: {len(seen_urls_in_crawl)}개")
    print(f"🆕 추가할 신규 학교: {len(new_targets)}개")
    
    if len(new_targets) == 0:
        print("✨ 새로운 데이터가 없습니다. 날짜만 갱신합니다.")
    else:
        print("🚀 신규 학교 데이터 처리 시작 (AI 분석 + 좌표 변환)...")

    # 4. 신규 데이터 처리 Loop
    new_data_list = []
    for school in tqdm(new_targets):
        raw_text = get_page_text(school['url'])
        if not raw_text: continue

        # AI 데이터 추출
        data = extract_info_ai(school['name'], raw_text)
        if data:
            data['source_url'] = school['url']
            
            # [통합] 좌표 변환 즉시 실행
            addr = data['basic_info'].get('address', '')
            if addr:
                coords = get_google_coordinates(addr)
                if coords:
                    data['location'] = coords
            
            new_data_list.append(data)
            time.sleep(1.5) # API 속도 조절

    # 5. 기존 데이터 + 신규 데이터 병합
    final_list = existing_data + new_data_list
    
    # 6. 저장
    today_str = datetime.date.today().strftime("%Y-%m-%d")
    final_structure = {
        "last_updated": today_str,
        "schools": final_list
    }

    with open(OUTPUT_JSON, 'w', encoding='utf-8') as f:
        json.dump(final_structure, f, ensure_ascii=False, indent=2)
    
    print(f"\n🎉 완료! 총 {len(final_list)}개 저장됨 (신규 추가: {len(new_data_list)}개)")
    print(f"📁 파일 위치: {OUTPUT_JSON}")

if __name__ == "__main__":
    main()
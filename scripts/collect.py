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
from google.api_core.exceptions import ResourceExhausted, InvalidArgument

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
except Exception as e:
    print(f"⚠️ 모델 설정 실패: {e}")
    model = genai.GenerativeModel('gemini-pro')

OUTPUT_JSON = "file/schools_complete_db.json"

# 일본 전국 47개 도도부현 리스트
PREFECTURES = [
    "北海道", "青森", "岩手", "宮城", "秋田", "山形", "福島",
    "茨城", "栃木", "群馬", "埼玉", "千葉", "東京都", "神奈川",
    "新潟", "富山", "石川", "福井", "山梨", "長野", "岐阜", "静岡", "愛知",
    "三重", "滋賀", "京都", "大阪", "兵庫", "奈良", "和歌山",
    "鳥取", "島根", "岡山", "広島", "山口",
    "徳島", "香川", "愛媛", "高知",
    "福岡", "佐賀", "長崎", "熊本", "大分", "宮崎", "鹿児島", "沖縄"
]

HEADERS = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}

# ==========================================
# [함수 정의]
# ==========================================
def clean_address_string(address):
    if not address: return ""
    address = re.sub(r'〒?\s*\d{3}-\d{4}', '', address)
    address = address.strip()
    if ' ' in address:
        address = address.split(' ')[0]
    return address

def get_google_coordinates(address):
    base_url = "https://maps.googleapis.com/maps/api/geocode/json"
    clean_address = clean_address_string(address)
    if not clean_address: return None
    params = {"address": clean_address, "key": GOOGLE_MAPS_API_KEY, "language": "ja"}
    try:
        res = requests.get(base_url, params=params)
        data = res.json()
        if data['status'] == 'OK':
            loc = data['results'][0]['geometry']['location']
            return {"lat": loc['lat'], "lng": loc['lng']}
    except: pass
    return None

def clean_json(text):
    text = re.sub(r'```json\s*', '', text)
    text = re.sub(r'```\s*', '', text)
    return text.strip()

# [수정] 오타 수정됨 (ddef -> def)
def extract_info_ai(school_name, text):
    prompt = f"""
    You are a data extractor. Extract info from the text into a strict JSON format.
    [Rules]
    1. Numbers: Remove commas, convert to Integer. If missing, use 0.
    2. 'features': Extract keywords based on the text. Mandatory: '기숙사', '1인실', '장학금', 'EJU', '이과', '진학', '회화', '비즈니스', '미술', '디자인', '단기'.
    3. 'major_universities': Extract specific names of universities/grad schools. 
       **IMPORTANT**: Extract names in **Japanese Kanji** (e.g., 早稲田大学, 東京大学). Limit to 10 names.
    4. 'description_ko': Summarize the school's characteristics in Korean (2-3 sentences). 
       Focus on location, unique courses, or atmosphere. (e.g., "도쿄 신주쿠에 위치하며 진학 지도에 강점이 있는 학교입니다...")
    5. Output: ONLY valid JSON string.

    [Schema]
    {{
        "id": "unique_id_english_or_number",
        "basic_info": {{ "name_ja": "School Name", "address": "Address", "capacity": "Capacity(int)" }},
        "student_demographics": {{ "total": "Total(int)", "korea": "Korea(int)", "china": "China(int)", "vietnam": "Vietnam(int)", "nepal": "Nepal(int)", "usa": "USA(int)" }},
        "courses": [ {{ "course_name": "Name", "admission_month": "Month", "total_fees": "1st Year Fee(int)" }} ],
        "career_path": {{ "grad_school": "Grad(int)", "university": "Univ(int)", "vocational": "Vocational(int)", "major_universities": ["早稲田大学", "明治大学"] }},
        "features": ["Feature1", "Feature2", "기숙사", ...],
        "description_ko": "학교 소개글..."
    }}
    [Text] {school_name} \n {text[:15000]}
    """
    
    for i in range(3):
        try:
            res = model.generate_content(prompt)
            if not res.text: return None
            return json.loads(clean_json(res.text))
        except ResourceExhausted:
            time.sleep((i + 1) * 10)
        except Exception as e:
            print(f"   ❌ AI 오류 ({school_name}): {e}")
            return None
    return None

def get_school_links(area_name):
    target_url = f"https://www.nisshinkyo.org/search/area.php?lng=1&area={area_name}"
    try:
        res = requests.get(target_url, headers=HEADERS)
        res.encoding = 'utf-8'
        soup = BeautifulSoup(res.text, 'html.parser')
        links = soup.select('a[href*="college.php"]')
        return [{"name": l.get_text(strip=True), "url": f"https://www.nisshinkyo.org/search/{l['href']}"} for l in links]
    except: return []

def get_page_text(url):
    try:
        time.sleep(random.uniform(0.5, 1.0))
        res = requests.get(url, headers=HEADERS)
        res.encoding = res.apparent_encoding
        if res.status_code != 200: return None
        soup = BeautifulSoup(res.text, 'html.parser')
        for s in soup(["script", "style"]): s.extract()
        return soup.get_text("\n", strip=True)
    except: return None

# 실시간 저장 함수
def save_db(data_list):
    structure = {
        "last_updated": datetime.date.today().strftime("%Y-%m-%d"),
        "schools": data_list
    }
    with open(OUTPUT_JSON, 'w', encoding='utf-8') as f:
        json.dump(structure, f, ensure_ascii=False, indent=2)

def load_existing_db():
    if os.path.exists(OUTPUT_JSON):
        try:
            with open(OUTPUT_JSON, 'r', encoding='utf-8') as f:
                content = f.read()
                if not content: return []
                data = json.loads(content)
                if isinstance(data, dict) and "schools" in data: return data["schools"]
                elif isinstance(data, list): return data
        except: pass
    return []

# ==========================================
# [메인 실행]
# ==========================================
def main():
    if not os.path.exists("file"): os.makedirs("file")
    
    # 1. 기존 데이터 로드 (이어하기)
    existing_data = load_existing_db()
    existing_urls = {s.get('source_url') for s in existing_data if s.get('source_url')}
    print(f"📂 기존 데이터: {len(existing_data)}개 로드됨 (여기부터 이어서 진행)")
    
    # 2. 전체 링크 수집
    all_links = []
    print(f"🔍 일본 전국 {len(PREFECTURES)}개 도도부현 검색 중...")
    for pref in tqdm(PREFECTURES, desc="지역 리스트 수집"):
        links = get_school_links(pref)
        all_links.extend(links)
        time.sleep(0.1)
    
    # 3. 아직 안 한 학교만 골라내기
    new_targets = [s for s in all_links if s['url'] not in existing_urls]
    
    if not new_targets:
        print("✨ 모든 학교가 이미 저장되어 있습니다!")
        return

    print(f"🚀 남은 {len(new_targets)}개 학교 처리를 시작합니다...")

    # 4. 하나씩 처리하고 즉시 저장
    count = 0
    for school in tqdm(new_targets, desc="AI 처리 및 자동저장"):
        raw_text = get_page_text(school['url'])
        if not raw_text: continue
        
        data = extract_info_ai(school['name'], raw_text)
        
        if data:
            data['source_url'] = school['url']
            addr = data['basic_info'].get('address', '')
            if addr:
                coords = get_google_coordinates(addr)
                if coords: data['location'] = coords
            
            # [핵심] 기존 리스트에 추가하고 바로 파일 저장
            existing_data.append(data)
            save_db(existing_data)
            
            count += 1
            time.sleep(4.5) # 무료 티어 안전 딜레이

    print(f"\n🎉 최종 완료! 총 {len(existing_data)}개 저장됨 (이번에 {count}개 추가)")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n🛑 사용자에 의해 중단되었습니다. 데이터는 안전하게 저장되었습니다.")
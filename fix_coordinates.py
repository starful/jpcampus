import json
import requests
import time
import os
import re
from dotenv import load_dotenv
from tqdm import tqdm

load_dotenv()
GOOGLE_MAPS_API_KEY = os.getenv("GOOGLE_MAPS_API_KEY")
JSON_FILE = "file/schools_complete_db.json"

if not GOOGLE_MAPS_API_KEY:
    print("❌ API 키 없음! .env 확인하세요.")
    exit()

def clean_address_string(address):
    """주소에서 우편번호, 기호 등을 제거하여 검색 정확도 높임"""
    # 1. 우편번호 제거 (〒123-4567, 123-4567 등)
    address = re.sub(r'〒?\s*\d{3}-\d{4}', '', address)
    # 2. 앞뒤 공백 제거
    address = address.strip()
    # 3. 공백이 있다면 앞부분만 가져오기 (빌딩 이름 등이 뒤에 붙는 경우 제거)
    if ' ' in address:
        address = address.split(' ')[0]
    
    return address

def get_coords(address):
    base_url = "https://maps.googleapis.com/maps/api/geocode/json"
    
    # 주소 전처리
    search_address = clean_address_string(address)
    
    # [수정] "東京都" 강제 추가 로직 삭제됨 (치바현 등 타 지역 대응)

    params = {
        "address": search_address,
        "key": GOOGLE_MAPS_API_KEY,
        "language": "ja"
    }
    
    try:
        res = requests.get(base_url, params=params)
        data = res.json()
        
        if data['status'] == 'OK':
            loc = data['results'][0]['geometry']['location']
            return {"lat": loc['lat'], "lng": loc['lng']}
        else:
            print(f"\n⚠️ API 실패: {search_address}")
            print(f"   ㄴ Status: {data.get('status')}")
            return None
            
    except Exception as e:
        print(f"\n❌ 요청 에러: {e}")
        return None

def main():
    if not os.path.exists(JSON_FILE):
        print(f"파일이 없습니다: {JSON_FILE}")
        return

    with open(JSON_FILE, 'r', encoding='utf-8') as f:
        schools = json.load(f)
    
    print(f"🚀 {len(schools)}개 학교 좌표 점검 및 수정 시작...")
    
    updated_count = 0
    DEFAULT_LAT = 35.6895 # 도쿄 시청 좌표(실패 시 기본값이었던 것)
    
    for school in tqdm(schools):
        current_lat = school.get('location', {}).get('lat')
        
        # 좌표가 없거나, 기본값이면 다시 시도
        if current_lat == DEFAULT_LAT or current_lat is None:
            raw_addr = school['basic_info'].get('address', '')
            if not raw_addr:
                continue

            new_loc = get_coords(raw_addr)
            
            if new_loc:
                school['location'] = new_loc
                updated_count += 1
            else:
                pass
            
            time.sleep(0.1) # API 제한 고려

    with open(JSON_FILE, 'w', encoding='utf-8') as f:
        json.dump(schools, f, ensure_ascii=False, indent=2)
    
    print(f"\n🎉 완료! {updated_count}개 좌표 업데이트됨.")

if __name__ == "__main__":
    main()
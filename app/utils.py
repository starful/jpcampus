# app/utils.py
import json
import os
from google.cloud import storage

BUCKET_NAME = os.getenv("GCS_BUCKET_NAME", "jpcampus")
SCHOOL_FILE = "file/schools_complete_db.json"
UNIV_FILE = "file/universities.json"

# [수정] 로컬 파일 로드 함수 (공통 사용)
def load_json_file(filepath):
    if os.path.exists(filepath):
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"⚠️ Load Error ({filepath}): {e}")
    return None

def load_data():
    """학교 데이터와 대학 데이터를 모두 로드하여 합침"""
    schools_data = []
    univ_data = []
    last_updated = ""

    # 1. 학교 데이터 로드
    s_data = load_json_file(SCHOOL_FILE)
    if s_data:
        if isinstance(s_data, dict) and "schools" in s_data:
            schools_data = s_data["schools"]
            last_updated = s_data.get("last_updated", "")
        elif isinstance(s_data, list):
            schools_data = s_data

    # 2. 대학 데이터 로드 [신규]
    u_data = load_json_file(UNIV_FILE)
    if u_data and isinstance(u_data, list):
        univ_data = u_data

    # 3. 데이터 합치기
    # 대학 데이터에는 category: "university"가 이미 들어있으므로 그대로 합침
    # 학교 데이터에는 category가 없으므로 "school"을 추가해주면 좋음 (JS에서 처리 중이긴 함)
    for s in schools_data:
        s['category'] = 'school'
        
    combined_data = schools_data + univ_data
    
    print(f"✅ Data Loaded: Schools({len(schools_data)}) + Univs({len(univ_data)}) = Total {len(combined_data)}")
    
    return combined_data, last_updated
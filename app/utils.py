
# app/utils.py
import json
import os
from google.cloud import storage

BUCKET_NAME = os.getenv("GCS_BUCKET_NAME", "jpcampus")
GCS_FILE = "schools_complete_db.json"
LOCAL_FILE = "file/schools_complete_db.json"

def load_data():
    """GCS 또는 로컬에서 JSON 데이터 로드 (schools, last_updated 반환)"""
    data = None

    # 1. GCS 시도
    try:
        storage_client = storage.Client()
        bucket = storage_client.bucket(BUCKET_NAME)
        blob = bucket.blob(GCS_FILE)
        if blob.exists():
            data_str = blob.download_as_text()
            data = json.loads(data_str)
            print("✅ Data loaded from GCS")
    except Exception as e:
        print(f"⚠️ GCS Load Error: {e}")

    # 2. 로컬 시도 (GCS 실패 시)
    if data is None and os.path.exists(LOCAL_FILE):
        try:
            with open(LOCAL_FILE, 'r', encoding='utf-8') as f:
                data = json.load(f)
                print("✅ Data loaded from Local File")
        except Exception:
            pass
    
    # [수정] 데이터 구조 분해 반환
    if data:
        # 신규 포맷: {"last_updated": "...", "schools": [...]}
        if isinstance(data, dict) and "schools" in data:
            return data["schools"], data.get("last_updated", "")
        # 구버전 포맷: [...]
        elif isinstance(data, list):
            return data, ""
    
    return [], ""
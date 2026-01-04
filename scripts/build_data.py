# scripts/build_data.py

import os
import json
import frontmatter
from datetime import datetime
import re

# [수정] 스크립트 파일 위치를 기준으로 프로젝트 루트 경로 계산
# scripts/build_data.py -> 상위(scripts) -> 상위(root)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# 절대 경로 설정
CONTENT_DIR = os.path.join(BASE_DIR, 'app', 'content')
OUTPUT_DIR = os.path.join(BASE_DIR, 'app', 'static', 'json')
OUTPUT_FILE = os.path.join(OUTPUT_DIR, 'schools_data.json')

def main():
    print(f"🔨 학교 데이터 빌드 시작... (Root: {BASE_DIR})")
    
    schools_list = []
    
    # 출력 폴더가 없으면 생성
    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)

    if not os.path.exists(CONTENT_DIR):
        print(f"❌ '{CONTENT_DIR}' 폴더가 없습니다.")
        return

    for filename in os.listdir(CONTENT_DIR):
        if not (filename.startswith('univ_') or filename.startswith('school_')):
            continue
            
        filepath = os.path.join(CONTENT_DIR, filename)
        
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                post = frontmatter.load(f)
                meta = post.metadata
                
                school_data = {
                    "id": meta.get('id'),
                    "category": meta.get('category', 'school'),
                    "basic_info": {
                        "name_ja": meta.get('basic_info', {}).get('name_ja'),
                        "name_en": meta.get('basic_info', {}).get('name_en'),
                        "address": meta.get('basic_info', {}).get('address'),
                        "capacity": meta.get('basic_info', {}).get('capacity')
                    },
                    "location": meta.get('location'),
                    "features": meta.get('features', []),
                    "tuition": meta.get('tuition'),
                    "stats": meta.get('stats'),
                    "link": f"/school/{meta.get('id')}"
                }
                schools_list.append(school_data)

        except Exception as e:
            print(f"⚠️ 에러 발생 ({filename}): {e}")

    final_data = {
        "last_updated": datetime.now().strftime("%Y-%m-%d"),
        "schools": schools_list
    }

    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        json.dump(final_data, f, ensure_ascii=False)
    
    print(f"🎉 빌드 완료! 총 {len(schools_list)}개 정제된 데이터 생성됨.")
    print(f"📁 저장 경로: {OUTPUT_FILE}")

if __name__ == "__main__":
    main()